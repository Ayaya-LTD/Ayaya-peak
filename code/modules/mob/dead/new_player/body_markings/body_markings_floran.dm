// Floran carni growths, worn as markings in the Markings tab. The art lives in
// floran_male.dmi and floran_female.dmi, one sheet per body build, where every
// piece is drawn one state per zone in an "_m"/"_f" pair against the bulky and
// slim body builds, the way every other gendered marking is drawn. The reference
// fullbodies (m_carni/f_carni) in those sheets are previews of the finished
// pattern, like the ent's entM/entF.
/datum/body_marking/carni
	icon = 'icons/mob/species/floran_male.dmi'
	icon_f = 'icons/mob/species/floran_female.dmi'
	// The pieces carry their own baked colours, so white leaves them as drawn.
	default_color = "FFF"

/datum/body_marking/carni/full
	name = "Carni"
	icon_state = "carni"
	affected_bodyparts = HEAD|CHEST|ARM_LEFT|ARM_RIGHT|HAND_LEFT|HAND_RIGHT|LEG_LEFT|LEG_RIGHT

/datum/body_marking/carni/belly
	name = "Carni Belly"
	icon_state = "carni_belly"
	affected_bodyparts = CHEST

/datum/body_marking/carni/overgrowth
	name = "Carni Overgrowth"
	icon_state = "carni_over"
	affected_bodyparts = HAND_LEFT|HAND_RIGHT|LEG_LEFT|LEG_RIGHT

/datum/body_marking/carni/above
	name = "Carni Thighs"
	icon_state = "carni_above"
	affected_bodyparts = LEG_LEFT|LEG_RIGHT

// The petals piece holds both hands in one cell, so it hangs off a single hand
// zone and paints both when that zone draws it.
/datum/body_marking/carni/petals
	name = "Carni Petals"
	icon_state = "carni_petals"
	affected_bodyparts = HAND_RIGHT
