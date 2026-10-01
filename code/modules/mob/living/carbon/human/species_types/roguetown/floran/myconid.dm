/mob/living/carbon/human/species/floran/myconid
	race = /datum/species/floran/myconid

/datum/species/floran/myconid
	name = "Myconid"
	id = "myconid"
	is_subrace = TRUE
	inherent_traits = list(TRAIT_PERMAMUTE)
	desc_title = "Myconid"
	desc = "Myconids are the mushroom-folk of the Floran, quick to spread and \
	quicker to take root wherever they happen to be planted. They trade in soft, \
	drifting spores that settle into the minds of anyone who cares to listen, and \
	they remember every rot they have ever fed upon."

/datum/species/floran/myconid/check_roundstart_eligible()
	return TRUE

/datum/species/floran/myconid/on_species_gain(mob/living/carbon/C, datum/species/old_species, datum/preferences/pref_load)
	. = ..()
	if(!C.HasSpell(/obj/effect/proc_holder/spell/targeted/myconid_telepathy))
		C.AddSpell(new /obj/effect/proc_holder/spell/targeted/myconid_telepathy)

/datum/species/floran/myconid/on_species_loss(mob/living/carbon/human/C, datum/species/new_species, pref_load)
	C.RemoveSpell(/obj/effect/proc_holder/spell/targeted/myconid_telepathy)
	. = ..()
