/mob/living/carbon/human/species/floran/plantkin
	race = /datum/species/floran/plantkin

/datum/species/floran/plantkin
	name = "Plantkin"
	id = "plantkin"
	is_subrace = TRUE
	desc_title = "Plantkin"
	desc = "Plantkin are the young of the Floran, hedge-born and hedge-raised, \
	sprouting up wherever a seed was scattered and then forgotten. Cheerful and \
	stubborn in equal measure, they root easily among Humens, and are usually the \
	first Floran a townsman will ever lay eyes on."

/datum/species/floran/plantkin/check_roundstart_eligible()
	return TRUE
