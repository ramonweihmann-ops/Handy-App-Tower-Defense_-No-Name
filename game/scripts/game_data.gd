class_name GameData
extends RefCounted
## Feste Spieldaten des Piloten: Helden, Gegner, Wellen.
## Namen und Werte sind Arbeitsstände und werden beim Balancing angepasst.

const HERO_IDS := ["dusty", "iska", "brocken", "volta"]

const HEROES := {
	"dusty": {
		"name": "Dusty Jo",
		"role": "Raumfrachter-Cowboy",
		"weapon": "Revolver",
		"blurb": "Sechs Schuss – und der letzte fächert auf.",
		"family": "revolver",
		"color": Color(0.86, 0.52, 0.22),
		"skin": Color(0.95, 0.76, 0.6),
		"damage": 22.0, "interval": 0.32, "mag": 6, "reload": 1.1, "cost": 3,
	},
	"iska": {
		"name": "Iska",
		"role": "Sicherheitschefin",
		"weapon": "Maschinengewehr",
		"blurb": "Dauerfeuer, bis nichts mehr steht.",
		"family": "mg",
		"color": Color(0.22, 0.52, 0.95),
		"skin": Color(0.78, 0.56, 0.42),
		"damage": 6.5, "interval": 0.09, "mag": 30, "reload": 2.0, "cost": 6,
	},
	"brocken": {
		"name": "Brocken",
		"role": "Bergarbeiter",
		"weapon": "Raketenwerfer",
		"blurb": "Langsam, laut und mit viel Wumms.",
		"family": "rocket",
		"color": Color(0.88, 0.3, 0.22),
		"skin": Color(0.96, 0.8, 0.66),
		"damage": 70.0, "interval": 0.9, "mag": 2, "reload": 2.0, "cost": 4, "splash": 2.2,
	},
	"volta": {
		"name": "Volta",
		"role": "Tesla-Tüftlerin",
		"weapon": "Blitzwerfer",
		"blurb": "Trifft einen und schockt die Nachbarn mit.",
		"family": "tesla",
		"color": Color(0.62, 0.36, 0.95),
		"skin": Color(0.9, 0.72, 0.58),
		"damage": 16.0, "interval": 0.55, "mag": 8, "reload": 1.6, "cost": 4, "chain": 2,
	},
}

## Gegner des ersten Motivs „Schleim-Welt“: leicht, mittel, stark, Boss.
const ENEMIES := {
	"schleimling": {
		"name": "Schleimling", "plural": "Schleimlinge", "tier": "leicht",
		"hp": 28.0, "speed": 2.3, "xp": 1, "dps": 8.0, "size": 0.55, "armor": 0.0,
	},
	"tentakler": {
		"name": "Tentakler", "plural": "Tentakler", "tier": "mittel",
		"hp": 95.0, "speed": 1.45, "xp": 3, "dps": 18.0, "size": 0.8, "armor": 0.0,
	},
	"panzerkaefer": {
		"name": "Panzerkäfer", "plural": "Panzerkäfer", "tier": "stark",
		"hp": 320.0, "speed": 0.85, "xp": 8, "dps": 40.0, "size": 1.0, "armor": 0.35,
	},
	"schleimmutter": {
		"name": "Schleimmutter", "plural": "Schleimmütter", "tier": "boss",
		"hp": 2000.0, "speed": 0.45, "xp": 0, "dps": 90.0, "size": 2.0, "armor": 0.1,
	},
}

const LEVEL_COUNT := 5


static func waves_in_level(level: int) -> int:
	return 5 + level


static func hp_mult(level: int, wave: int) -> float:
	return 1.0 + 0.2 * (level - 1) + 0.04 * (wave - 1)


## Stellt die Gegner einer Welle zusammen.
static func wave_spawns(level: int, wave: int) -> Array[String]:
	var list: Array[String] = []
	var total := waves_in_level(level)
	var light := 2 + int(wave * 0.7) + level
	var mid := 0
	if wave >= 2:
		mid = int((wave - 1) * 0.55 + (level - 1) * 0.6)
	var heavy := 0
	if level >= 2 and wave >= 3:
		heavy = int((wave - 2) / 3.0)
		if level >= 4 and wave % 2 == 0:
			heavy += 1
	if wave == total and level < LEVEL_COUNT:
		heavy += 1
	for i in light:
		list.append("schleimling")
	for i in mid:
		list.append("tentakler")
	for i in heavy:
		list.append("panzerkaefer")
	list.shuffle()
	if level == LEVEL_COUNT and wave == total:
		list.append("schleimmutter")
	return list


## Erfahrung, die für den nächsten Aufstieg nötig ist.
static func xp_needed(levelups_so_far: int) -> int:
	return 10 + levelups_so_far * 6
