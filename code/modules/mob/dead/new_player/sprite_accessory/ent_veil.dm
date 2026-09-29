// The ent Veil: a hollow worn on the face, offered as a Snout section the way Aasimar offers
// its own (see /datum/customizer/organ/snout/wings and its "Winged Veil"). The sprites are the
// marking states of the same name and paint themselves with the wood picked under Heartwood
// unless the player colours them.

/datum/sprite_accessory/snout/ent_veil
	abstract_type = /datum/sprite_accessory/snout/ent_veil
	icon = 'icons/mob/species/ENTS.dmi'
	// The sheet carries the finished state, so this draws it as-is instead of asking for
	// per-layer "_ADJ" copies the way the snout sheet does.
	relevant_layers = null
	// Above the limb and any markings, below hair and the other BODY_LAYER features.
	layer = BODY_ADJ_LAYER
	color_key_name = "Growth"
	color_key_defaults = list(KEY_SKIN_COLOR)
	gendered_variants = FALSE

/datum/sprite_accessory/snout/ent_veil/hollow/birch
	name = "Birch Hollow"
	icon_state = "birch_hollow_head"

/datum/sprite_accessory/snout/ent_veil/hollow/oak
	name = "Oak Hollow"
	icon_state = "oak_hollow_head"

/datum/sprite_accessory/snout/ent_veil/hollow/swamp
	name = "Swamp Hollow"
	icon_state = "swamp_hollow_head"

/datum/sprite_accessory/snout/ent_veil/shrike
	name = "Shrike"
	icon_state = "shrike_ent_head"
	// The shrike is painted, not bark: a white default leaves the bird its own
	// colours (it was the one growth that did not paint with the Heartwood).
	default_colors = list("#FFFFFF")
