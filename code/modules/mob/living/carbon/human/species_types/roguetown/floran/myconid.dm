/mob/living/carbon/human/species/floran/myconid
	race = /datum/species/floran/myconid

/datum/species/floran/myconid
	name = "Myconid"
	id = "myconid"
	is_subrace = TRUE
	// Same brittle-form rules as a fragile bone golem: a cracked chest or skull
	// (or a shattered spine) kills outright, and with no blood in them the chest
	// crack has nothing to blunt it.
	inherent_traits = list(TRAIT_PERMAMUTE, TRAIT_CRITICAL_WEAKNESS, TRAIT_NOBREATH, TRAIT_ALCOHOL_INTOLERANCE)
	limbs_icon_m = 'icons/mob/species/myconids_male.dmi'
	limbs_icon_f = 'icons/mob/species/myconides_female.dmi'
	allowed_body_builds = null
	organs = list(
		ORGAN_SLOT_BRAIN = /obj/item/organ/brain/myconid,
		ORGAN_SLOT_HEART = /obj/item/organ/heart/myconid,
		ORGAN_SLOT_LUNGS = /obj/item/organ/lungs/myconid,
		ORGAN_SLOT_EYES = /obj/item/organ/eyes/myconid,
		ORGAN_SLOT_EARS = /obj/item/organ/ears,
		ORGAN_SLOT_TONGUE = /obj/item/organ/tongue/myconid,
		ORGAN_SLOT_LIVER = /obj/item/organ/liver/myconid,
		ORGAN_SLOT_STOMACH = /obj/item/organ/stomach/myconid,
		ORGAN_SLOT_APPENDIX = /obj/item/organ/appendix,
		ORGAN_SLOT_GUTS = /obj/item/organ/guts/myconid,
		)
	// The male is drawn at the dwarf's height - same head line, same hip line -
	// so he wears the dwarf's table, pulling head-slot gear, hair and held items
	// down onto the shorter body. The female is humen-tall, so she reads no
	// _F entries and stays where every humen-shaped sprite already lands.
	offset_features = list(
		OFFSET_ID = list(0,0), OFFSET_GLOVES = list(0,0), OFFSET_WRISTS = list(0,0),\
		OFFSET_CLOAK = list(0,0), OFFSET_FACEMASK = list(0,-4), OFFSET_HEAD = list(0,-4), \
		OFFSET_FACE = list(0,-4), OFFSET_BELT = list(0,-5), OFFSET_BACK = list(0,-4), \
		OFFSET_NECK = list(0,-4), OFFSET_MOUTH = list(0,-4), OFFSET_PANTS = list(0,0), \
		OFFSET_SHIRT = list(0,0), OFFSET_ARMOR = list(0,0), OFFSET_HANDS = list(0,-3), \
		OFFSET_UNDIES = list(0,-4), \
		)
	// No blood to spill: sap does not run, so wounds open without bleeding and
	// the chest-crack death above has the flag it needs to land.
	species_traits = list(EYECOLOR,LIPS,NOBLOOD)
	customizers = list(
		/datum/customizer/organ/eyes/humanoid,
		/datum/customizer/bodypart_feature/hair/head/myco_hat,
		/datum/customizer/bodypart_feature/accessory,
		/datum/customizer/bodypart_feature/face_detail,
		/datum/customizer/bodypart_feature/underwear,
		/datum/customizer/bodypart_feature/legwear,
		/datum/customizer/bodypart_feature/piercing,
		/datum/customizer/organ/testicles/anthro,
		/datum/customizer/organ/penis/anthro,
		/datum/customizer/organ/breasts/human,
		/datum/customizer/organ/vagina/human_anthro,
		/datum/customizer/bodypart_feature/pubes,
		/datum/customizer/bodypart_feature/pits,
		)
	desc_title = "Myconid"
	desc = "Myconids are the mushroom-folk of the Grovekin, quick to spread and \
	quicker to take root wherever they happen to be planted. They trade in soft, \
	drifting spores that settle into the minds of anyone who cares to listen, and \
	they remember every rot they have ever fed upon."
	mechanics_explanations = list("They never breathe and have no blood to spill: cuts and fractures open without bleeding, and neither thirst nor suffocation can touch them.",
		"<b>Brittle Form</b>: their fungal body cannot roll with a killing blow. A cracked chest, a broken skull or a snapped spine is the end of them, where any other race might walk away.",
		"<b>Crown</b>: the tough cap grown atop their skull refuses to be parted from them, and it alone shelters a myconid's head - coifs, hoods and helmets lend them no protection.",
		"<b>Alcohol Intolerance</b>: alcohol is poison to their fungal flesh. Every drop that passes their lips sickens them, and the stronger the drink, the worse the sickness.")

/datum/species/floran/myconid/check_roundstart_eligible()
	return TRUE

/datum/species/floran/myconid/get_skin_list()
	return list("Myconid" = "FFFFFF")

/datum/species/floran/myconid/on_species_gain(mob/living/carbon/C, datum/species/old_species, datum/preferences/pref_load)
	. = ..()
	if(!C.HasSpell(/obj/effect/proc_holder/spell/targeted/myconid_telepathy))
		C.AddSpell(new /obj/effect/proc_holder/spell/targeted/myconid_telepathy)
	if(ishuman(C))
		var/mob/living/carbon/human/H = C
		if(!H.get_item_by_slot(SLOT_HEAD))
			H.equip_to_slot_if_possible(new /obj/item/clothing/head/roguetown/helmet/leather/advanced/mycohelm, SLOT_HEAD, qdel_on_fail = TRUE, disable_warning = TRUE, bypass_equip_delay_self = TRUE)

/datum/species/floran/myconid/after_equip_job(datum/job/J, mob/living/carbon/human/H)
	. = ..()
	if(!H.get_item_by_slot(SLOT_HEAD))
		H.equip_to_slot_if_possible(new /obj/item/clothing/head/roguetown/helmet/leather/advanced/mycohelm, SLOT_HEAD, qdel_on_fail = TRUE, disable_warning = TRUE, bypass_equip_delay_self = TRUE)

/datum/species/floran/myconid/on_species_loss(mob/living/carbon/human/C, datum/species/new_species, pref_load)
	C.RemoveSpell(/obj/effect/proc_holder/spell/targeted/myconid_telepathy)
	var/obj/item/clothing/head/roguetown/helmet/leather/advanced/mycohelm/helm = C.get_item_by_slot(SLOT_HEAD)
	if(helm)
		REMOVE_TRAIT(helm, TRAIT_NODROP, CURSED_ITEM_TRAIT)
		C.dropItemToGround(helm)
	. = ..()
