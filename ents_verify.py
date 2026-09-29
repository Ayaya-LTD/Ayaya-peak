import os
import re
import struct
import sys
import zlib
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
DM_FILES = []
for base in ("code", "modular"):
    for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, base)):
        for fn in filenames:
            if fn.endswith(".dm"):
                DM_FILES.append(os.path.join(dirpath, fn))

TYPE_RE = re.compile(r"^(/[\w/]+)\s*$", re.M)
NAME_RE = re.compile(r"^\s*name = \"(.*)\"\s*$", re.M)
ICONSTATE_RE = re.compile(r"^\s*icon_state = \"(.*)\"\s*$", re.M)
fail = []


def walk(path):
    out = {}
    for f in DM_FILES:
        text = open(f, encoding="utf-8", errors="replace").read()
        lines = text.split("\n")
        current = None
        for line in lines:
            m = re.match(r"^(/[A-Za-z0-9_/]+)\s*$", line)
            if m:
                current = m.group(1)
                out.setdefault(current, []).append((f, line))
            elif current is None:
                continue
    return out


print("scanning %d dm files" % len(DM_FILES))
all_types = set()
defined_names = defaultdict(set)  # datum root -> names
for f in DM_FILES:
    text = open(f, encoding="utf-8", errors="replace").read()
    for m in re.finditer(r"(?m)^(/[A-Za-z0-9_/]+)\s*$", text):
        all_types.add(m.group(1))

# names per family
fam_name_re = {
    "marking": re.compile(r"(?ms)^(/datum/body_marking[/\w]*)\n(.*?)(?=^/|^$)"),
}


def typepath_refs(pattern):
    refs = set()
    for f in DM_FILES:
        text = open(f, encoding="utf-8", errors="replace").read()
        for m in re.finditer(pattern, text):
            refs.add(m.group(0))
    return refs


# --- 1. resolve referenced typepaths for the ent feature ---
needles = [
    r"/datum/body_marking/ent[\w/]*",
    r"/datum/body_marking_set/ent[\w/]*",
    r"/datum/customizer/organ/snout/ent_veil[\w/]*",
    r"/datum/customizer_choice/organ/snout/ent_veil[\w/]*",
    r"/datum/sprite_accessory/snout/ent_veil[\w/]*",
    r"/obj/item/organ/snout/ent\b",
]
missing = []
seen = set()
for pat in needles:
    for ref in typepath_refs(pat):
        if ref in seen:
            continue
        seen.add(ref)
        if ref not in all_types:
            missing.append(ref)
if missing:
    fail.append("typepaths not defined: %s" % sorted(set(missing)))
else:
    print("typepath check OK (%d refs)" % len(seen))

# --- 2. DMI states ---
DMI = os.path.join(ROOT, "icons", "mob", "species", "ENTS.dmi")
data = open(DMI, "rb").read()
i = 8
desc = ""
while i < len(data):
    ln = struct.unpack(">I", data[i : i + 4])[0]
    typ = data[i + 4 : i + 8]
    chunk = data[i + 8 : i + 8 + ln]
    if typ == b"tEXt":
        k, _, v = chunk.partition(b"\x00")
        if k == b"Description":
            desc = v.decode("latin1")
    elif typ == b"zTXt":
        k, _, rest = chunk.partition(b"\x00")
        if k == b"Description":
            desc = zlib.decompress(rest[1:]).decode("latin1")
    elif typ == b"IEND":
        break
    i += 12 + ln
states = set(re.findall(r'(?m)^state = "(.*)"$', desc))
print("dmi states: %d" % len(states))

ZONE_BITS = {
    "HEAD": ["head"],
    "CHEST": ["chest"],
    "ARM_LEFT": ["l_arm"],
    "ARM_RIGHT": ["r_arm"],
    "LEG_LEFT": ["l_leg"],
    "LEG_RIGHT": ["r_leg"],
}

# parse ent markings: type -> (icon_state, affected bits, name)
marking_file = os.path.join(ROOT, "code", "modules", "mob", "dead", "new_player", "body_markings", "body_markings_ent.dm")
text = open(marking_file, encoding="utf-8").read()
inherit = {}
blocks = re.split(r"(?m)(?=^/datum/body_marking)", text)
markings = {}
for b in blocks:
    m = re.match(r"^(/datum/body_marking/[\w/]+)", b)
    if not m:
        continue
    tp = m.group(1)
    name = re.search(r'(?m)^\s*name = "(.*)"', b)
    ics = re.search(r'(?m)^\s*icon_state = "(.*)"', b)
    aff = re.search(r"(?m)^\s*affected_bodyparts = (.*)$", b)
    gen = re.search(r"(?m)^\s*gendered = (\w+)", b)
    markings[tp] = {
        "name": name.group(1) if name else None,
        "icon_state": ics.group(1) if ics else None,
        "affected": aff.group(1) if aff else None,
        "gendered": (gen.group(1) == "TRUE") if gen else None,
    }

# inherit affected_bodyparts and gendered from parents within the file
for tp, entry in markings.items():
    if entry["affected"]:
        continue
    cur = tp
    while "/" in cur:
        cur = cur.rsplit("/", 1)[0]
        if cur in markings and markings[cur]["affected"]:
            entry["affected"] = markings[cur]["affected"]
            break
    if not entry["affected"] and entry["name"]:
        fail.append("%s inherits no affected_bodyparts" % tp)
for tp, entry in markings.items():
    if entry["gendered"] is None:
        cur = tp
        while "/" in cur:
            cur = cur.rsplit("/", 1)[0]
            if cur in markings and markings[cur]["gendered"] is not None:
                entry["gendered"] = markings[cur]["gendered"]
                break
        if entry["gendered"] is None:
            entry["gendered"] = True  # /datum/body_marking default
    if entry["name"] and entry["gendered"]:
        # The sheet has no _m/_f variants, so the picker previews the plain
        # render state; a gendered marking would look for a "_m" state that
        # does not exist.
        fail.append("%s is gendered but the ent sheet carries no _m states" % tp)

named = [tp for tp, e in markings.items() if e["name"]]
print("ent markings: %d named" % len(named))
if len(named) != 12:
    fail.append("expected 12 named ent markings, found %d" % len(named))
# Hollows and the shrike live only in the Veil (sprite_accessory/snout/ent_veil),
# never as markings.
for banned in ("hollow", "shrike"):
    bad = [tp for tp in named if banned in tp]
    if bad:
        fail.append("%s growths must not be markings: %s" % (banned, bad))

for tp, e in sorted(markings.items()):
    if not e["name"]:
        continue
    if not e["icon_state"]:
        fail.append("%s has no icon_state" % tp)
        continue
    if not e["affected"]:
        fail.append("%s has no affected_bodyparts" % tp)
        continue
    zones = []
    for bit, zs in ZONE_BITS.items():
        if re.search(r"\b%s\b" % bit, e["affected"]):
            zones.extend(zs)
    if not zones:
        fail.append("%s: cannot map affected_bodyparts %r" % (tp, e["affected"]))
    for z in zones:
        render = "%s_%s" % (e["icon_state"], z)
        if render not in states:
            fail.append("DMI missing render state %s (from %s)" % (render, tp))
        # gendered = FALSE: the picker previews this same plain state
if not any("DMI missing" in f for f in fail):
    print("marking DMI states OK")

# --- 3. veil accessories ---
veil_file = os.path.join(ROOT, "code", "modules", "mob", "dead", "new_player", "sprite_accessory", "ent_veil.dm")
vtext = open(veil_file, encoding="utf-8").read()
accs = re.findall(r"(?ms)^(/datum/sprite_accessory/snout/ent_veil/[\w/]+)\n(.*?)(?=^/|\Z)", vtext)
veil_states = []
for tp, body in accs:
    nm = re.search(r'(?m)^\s*name = "(.*)"', body)
    ic = re.search(r'(?m)^\s*icon_state = "(.*)"', body)
    if not nm:
        continue  # abstract parent
    if not ic:
        fail.append("veil accessory %s has no icon_state" % tp)
        continue
    veil_states.append((tp, nm.group(1), ic.group(1)))
    if ic.group(1) not in states:
        fail.append("DMI missing veil state %s (%s)" % (ic.group(1), tp))
print("veil accessories: %d" % len(veil_states))
if len(veil_states) != 4:
    fail.append("expected 4 veil accessories, found %d" % len(veil_states))
if not any("veil state" in f for f in fail):
    print("veil DMI states OK")
want_veils = {
    "/datum/sprite_accessory/snout/ent_veil/hollow/birch",
    "/datum/sprite_accessory/snout/ent_veil/hollow/oak",
    "/datum/sprite_accessory/snout/ent_veil/hollow/swamp",
    "/datum/sprite_accessory/snout/ent_veil/shrike",
}
got_veils = {tp for tp, _, _ in veil_states}
if got_veils != want_veils:
    fail.append("veil must hold exactly the 3 hollows + shrike, got %s" % sorted(got_veils))
# Every veil accessory must be offered by the ent Veil customizer choice.
snout_file = os.path.join(ROOT, "code", "modules", "client", "customizer", "customizers", "organ", "snout.dm")
stext = open(snout_file, encoding="utf-8").read()
choice = re.search(r"(?ms)^/datum/customizer_choice/organ/snout/ent_veil\n(.*?)(?=^/|\Z)", stext)
if choice:
    offered = set(re.findall(r"/datum/sprite_accessory/snout/ent_veil/[\w/]+", choice.group(1)))
    if offered != want_veils:
        fail.append("snout.dm ent_veil choice lists %s" % sorted(offered))
else:
    fail.append("could not parse ent_veil customizer choice")

# --- 4. global name uniqueness for markings and sets ---
marking_names = defaultdict(list)
for f in DM_FILES:
    t = open(f, encoding="utf-8", errors="replace").read()
    for m in re.finditer(r"(?ms)^(/datum/body_marking(?:/[\w]+)*)\n(.*?)(?=^/|\Z)", t):
        tp, body = m.group(1), m.group(2)
        nm = re.search(r'(?m)^\s*name = "(.*)"', body)
        if nm:
            marking_names[nm.group(1)].append(tp)
dups = {k: v for k, v in marking_names.items() if len(v) > 1}
if dups:
    fail.append("duplicate marking names: %s" % dups)
else:
    print("marking names unique (%d total)" % len(marking_names))

set_names = defaultdict(list)
for f in DM_FILES:
    t = open(f, encoding="utf-8", errors="replace").read()
    for m in re.finditer(r"(?ms)^(/datum/body_marking_set(?:/[\w]+)*)\n(.*?)(?=^/|\Z)", t):
        tp, body = m.group(1), m.group(2)
        nm = re.search(r'(?m)^\s*name = "(.*)"', body)
        if nm:
            set_names[nm.group(1)].append(tp)
# "Belly & Socks" is a pre-existing duplicate in this codebase, so only ent sets are checked.
dups = {k: v for k, v in set_names.items() if len(v) > 1 and any("/ent_" in t for t in v)}
if dups:
    fail.append("duplicate ent marking set names: %s" % dups)
else:
    print("set names: %d total, ent sets unique" % len(set_names))

# --- 5. ent species lists ---
ent_file = os.path.join(ROOT, "code", "modules", "mob", "living", "carbon", "human", "species_types", "roguetown", "floran", "ent.dm")
etext = open(ent_file, encoding="utf-8").read()
ent_markings = re.findall(r"/datum/body_marking/ent/[\w/]+", etext)
ent_sets = re.findall(r"/datum/body_marking_set/ent_?\w+", etext)
print("ent species lists: %d markings, %d sets" % (len(ent_markings), len(ent_sets)))
if len(ent_markings) != 12:
    fail.append("ent species should list 12 ent markings, lists %d" % len(ent_markings))
if len(ent_sets) != 4:
    fail.append("ent species should list 4 ent sets, lists %d" % len(ent_sets))
if "/datum/body_marking_set/ent_shrike" in all_types:
    fail.append("ent_shrike preset still defined (its marking moved to the Veil)")
# Every ent preset wears the Sticks growth on the limbs by default.
sets_file = os.path.join(ROOT, "code", "modules", "mob", "dead", "new_player", "body_markings", "body_marking_sets.dm")
sfile_text = open(sets_file, encoding="utf-8").read()
ent_blocks = re.findall(r"(?ms)^(/datum/body_marking_set/ent_\w+)\n(.*?)(?=^/|\Z)", sfile_text)
print("ent presets in body_marking_sets.dm: %d" % len(ent_blocks))
if len(ent_blocks) != 4:
    fail.append("expected 4 ent presets, found %d" % len(ent_blocks))
for tp, body in ent_blocks:
    if "/datum/body_marking/ent/limbs/sticks" not in body:
        fail.append("ent preset %s is missing the default sticks growth" % tp)
# The selection lists may only carry ent content: species New() unions preset
# contents into body_markings, so both lists must stay ent-only.
sets_block = re.search(r"(?ms)^\tbody_marking_sets = list\((.*?)\n\t\)", etext)
if sets_block:
    set_paths = re.findall(r"/datum/body_marking_set/[\w/]+", sets_block.group(1))
    bad_sets = [p for p in set_paths if p != "/datum/body_marking_set/none" and not p.startswith("/datum/body_marking_set/ent_")]
    if bad_sets:
        fail.append("ent body_marking_sets offers non-ent sets: %s" % bad_sets)
else:
    fail.append("could not parse ent body_marking_sets list")
marks_block = re.search(r"(?ms)^\tbody_markings = list\((.*?)\n\t\)", etext)
if marks_block:
    mark_paths = re.findall(r"/datum/body_marking/[\w/]+", marks_block.group(1))
    non_ent = [p for p in mark_paths if not p.startswith("/datum/body_marking/ent/")]
    if non_ent:
        fail.append("ent body_markings lists non-ent markings: %s" % non_ent)
    if len(mark_paths) != 12:
        fail.append("ent body_markings should list 12 entries, lists %d" % len(mark_paths))
else:
    fail.append("could not parse ent body_markings list")
for tp in ent_markings + ent_sets:
    if tp not in all_types:
        fail.append("ent.dm references undefined %s" % tp)
customizers = re.search(r"(?ms)^\tcustomizers = list\((.*?)\n\t\)", etext)
if customizers:
    paths = re.findall(r"/datum/customizer/[\w/]+", customizers.group(1))
    if len(paths) != len(set(paths)):
        fail.append("ent customizers list has duplicates")
    if "/datum/customizer/organ/snout/ent_veil" not in paths:
        fail.append("ent customizers missing veil")
    for p in paths:
        if p not in all_types:
            fail.append("ent customizer undefined: %s" % p)
    for stale in ("/veil/head", "/veil/chest", "/veil/arms", "/veil/legs"):
        if any(p.endswith(stale) for p in paths):
            fail.append("stale customizer %s still listed" % stale)
    print("ent customizers: %d" % len(paths))
else:
    fail.append("could not parse ent customizers list")

# --- 6. DME include ---
dme = open(os.path.join(ROOT, "roguetown.dme"), encoding="utf-8", errors="replace").read()
for inc in (
    "code\\modules\\mob\\dead\\new_player\\body_markings\\body_markings_ent.dm",
    "code\\modules\\mob\\dead\\new_player\\sprite_accessory\\ent_veil.dm",
):
    if ('#include "%s"' % inc) not in dme:
        fail.append("DME missing include %s" % inc)
if '#include "code\\modules\\client\\customizer\\customizers\\bodypart_feature\\veil.dm"' in dme:
    fail.append("DME still includes the deleted bodypart_feature veil.dm")
if "body_markings_ent.dm" in dme:
    print("DME includes OK")

# --- 7. no stale veil-as-feature code ---
for f in DM_FILES:
    t = open(f, encoding="utf-8", errors="replace").read()
    for pat in ("/datum/customizer/bodypart_feature/veil/head", "/datum/customizer/bodypart_feature/veil/chest",
                "/datum/customizer/bodypart_feature/veil/arms", "/datum/customizer/bodypart_feature/veil/legs",
                "/datum/customizer/bodypart_feature/veil", "/datum/customizer_choice/bodypart_feature/veil",
                "/datum/bodypart_feature/veil", "#define BODYPART_FEATURE_VEIL"):
        if pat in t:
            fail.append("stale %s in %s" % (pat, os.path.relpath(f, ROOT)))

# --- 8. tabs only in touched files ---
touched = [marking_file, veil_file,
           os.path.join(ROOT, "code", "modules", "client", "customizer", "customizers", "organ", "snout.dm"),
           os.path.join(ROOT, "code", "modules", "surgery", "organs", "feature_organs", "snout.dm"),
           os.path.join(ROOT, "code", "modules", "surgery", "bodyparts", "bodypart_features", "features.dm"),
           os.path.join(ROOT, "code", "__DEFINES", "medical.dm"),
           ent_file,
           os.path.join(ROOT, "code", "modules", "mob", "dead", "new_player", "body_markings", "body_marking_sets.dm")]
for f in touched:
    for n, line in enumerate(open(f, encoding="utf-8").read().split("\n"), 1):
        if line.startswith("    ") or (line.startswith(" ") and line.strip()):
            fail.append("space indentation in %s:%d" % (os.path.relpath(f, ROOT), n))
            break

print()
if fail:
    print("FAILURES:")
    for f in fail:
        print(" -", f)
    sys.exit(1)
print("all checks passed")
