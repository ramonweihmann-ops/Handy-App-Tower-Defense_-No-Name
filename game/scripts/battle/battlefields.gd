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
	# Level 51–150 (Auftrag Vorlage_Raw/PLANETEN_FUER_CHATGPT.md): bis die Bilder da sind, zeigt
	# „fallback“ einen der bisherigen Planeten.
	"jungle_moon": {"name": "Dschungelmond", "file": "res://fields/jungle_moon.webp", "fallback": "space_dock", "rim": Color(0.45, 1.0, 0.55)},
	"ocean_world": {"name": "Ozeanwelt", "file": "res://fields/ocean_world.webp", "fallback": "ice_world", "rim": Color(0.35, 0.95, 1.0)},
	"crystal_planet": {"name": "Kristallplanet", "file": "res://fields/crystal_planet.webp", "fallback": "nebula_portal", "rim": Color(1.0, 0.5, 0.85)},
	"storm_giant": {"name": "Sturmriese", "file": "res://fields/storm_giant.webp", "fallback": "space_dock", "rim": Color(1.0, 0.9, 0.4)},
	"scrap_world": {"name": "Schrottwelt", "file": "res://fields/scrap_world.webp", "fallback": "desert_outpost", "rim": Color(1.0, 0.6, 0.3)},
	"cloud_city": {"name": "Wolkenstadt", "file": "res://fields/cloud_city.webp", "fallback": "ice_world", "rim": Color(0.75, 0.9, 1.0)},
	"spore_world": {"name": "Sporenwelt", "file": "res://fields/spore_world.webp", "fallback": "lava_asteroid", "rim": Color(1.0, 0.6, 0.3)},
	"ghost_moon": {"name": "Geistermond", "file": "res://fields/ghost_moon.webp", "fallback": "nebula_portal", "rim": Color(0.45, 1.0, 0.85)},
	"temple_planet": {"name": "Tempelplanet", "file": "res://fields/temple_planet.webp", "fallback": "desert_outpost", "rim": Color(1.0, 0.85, 0.4)},
	"black_hole": {"name": "Schwarzes Loch", "file": "res://fields/black_hole.webp", "fallback": "nebula_portal", "rim": Color(0.85, 0.5, 1.0)},
	# Arenen (Vorlage Arena_Karten_v1, 977 × 1610): auf 1688 hoch skaliert, links und rechts je 122 Punkte
	# Tribüne abgeschnitten; Brücke und Plattform liegen dann wie bei den Planeten.
	"universums_arena": {"name": "Universums-Arena", "file": "res://fields/universums_arena.webp", "rim": Color(0.85, 0.55, 1.0)},
	"multiplayer_arena": {"name": "Multiplayer-Arena", "file": "res://fields/multiplayer_arena.webp", "rim": Color(0.6, 0.8, 1.0)},
}
## Planeten im Abenteuer, je 10 Level
const ADVENTURE := ["space_dock", "ice_world", "desert_outpost", "lava_asteroid", "nebula_portal",
	"jungle_moon", "ocean_world", "crystal_planet", "storm_giant", "scrap_world",
	"cloud_city", "spore_world", "ghost_moon", "temple_planet", "black_hole"]
## Felder der Spielmodi („universe“: Universumsode, sobald es den Modus gibt)
const MODES := {"mp": "multiplayer_arena", "universe": "universums_arena"}


static func for_level(level: int) -> String:
	return ADVENTURE[clampi((level - 1) / 10, 0, ADVENTURE.size() - 1)]


static func for_mode(mode: String, level: int) -> String:
	return MODES.get(mode, for_level(level))


## Name des Planeten in diesem Level (je 10 Level ein Planet)
static func planet_name(level: int) -> String:
	return str(FIELDS[for_level(level)]["name"])


static func texture(id: String) -> Texture2D:
	var d: Dictionary = FIELDS.get(id, {})
	var f: String = d.get("file", "")
	if f != "" and ResourceLoader.exists(f):
		return load(f)
	if d.has("fallback"):
		return texture(str(d["fallback"]))
	return null
