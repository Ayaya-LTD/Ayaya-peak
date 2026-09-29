/mob/living/carbon/human/species/floran/myconid
	race = /datum/species/floran/myconid

/datum/species/floran/myconid
	name = "Myconid"
	id = "myconid"
	is_subrace = TRUE
	desc_title = "Myconid"
	desc = "Myconids are the mushroom-folk of the Floran, quick to spread and \
	quicker to take root wherever they happen to be planted. They trade in soft, \
	drifting spores that settle into the minds of anyone who cares to listen, and \
	they remember every rot they have ever fed upon."

/datum/species/floran/myconid/check_roundstart_eligible()
	return TRUE
