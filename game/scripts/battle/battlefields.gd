class_name Battlefields
## Gemalte Schlachtfelder (Vorlagen: Vorlage_Raw/Karten_v2, LAYOUT_FUER_CLAUDE.md): ein Bild je
## Planet mit Brücke und Plattform, 780 × 1688. Gegner, Helden, Mauer und Anzeige liegen darüber.
## Je 10 Level ein Planet, dazu eigene Felder für die Spielmodi.
##
## Brücke im Bild: oben (280..500, 294), unten (64..716, 1158), Mitte x 390. Die Kamera im Kampf
## (Battle.BACKDROP_CAM) ist so gestellt, dass die 3D-Bahn genau darauf liegt.

const FIELDS := {
	"space_dock": {"name": "Raumstation", "file": "res://fields/space_dock.webp", "rim": Color(0.45, 0.8, 1.0)},
	"ice_world": {"name": "Eiswelt", "file": "res://fields/ice_world.webp", "rim": Color(0.6, 0.85, 1.0)},
	"desert_outpost": {"name": "Wüstenaußenposten", "file": "res://fields/desert_outpost.webp", "rim": Color(1.0, 0.8, 0.5)},
	"lava_asteroid": {"name": "Lava-Asteroid", "file": "res://fields/lava_asteroid.webp", "rim": Color(1.0, 0.5, 0.25)},
	"nebula_portal": {"name": "Nebelportal", "file": "res://fields/nebula_portal.webp", "rim": Color(0.8, 0.5, 1.0)},
	"ringed_planet": {"name": "Ringplanet", "file": "res://fields/ringed_planet.webp", "rim": Color(0.55, 0.95, 0.8)},
}
## Planeten im Abenteuer, je 10 Level
const ADVENTURE := ["space_dock", "ice_world", "desert_outpost", "lava_asteroid", "nebula_portal"]
## Felder der Spielmodi
const MODES := {"mp": "ringed_planet"}


static func for_level(level: int) -> String:
	return ADVENTURE[clampi((level - 1) / 10, 0, ADVENTURE.size() - 1)]


static func for_mode(mode: String, level: int) -> String:
	return MODES.get(mode, for_level(level))


static func texture(id: String) -> Texture2D:
	var f: String = FIELDS.get(id, {}).get("file", "")
	return load(f) if f != "" and ResourceLoader.exists(f) else null
