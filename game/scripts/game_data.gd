class_name GameData
extends RefCounted
## Feste Spieldaten des Piloten: Helden, Gegner, Wellen.
## Namen und Werte sind Arbeitsstände und werden beim Balancing angepasst.

const HERO_IDS := ["dusty", "iska", "brocken", "volta", "kalle", "margot", "lynx", "fritzi"]

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
	"kalle": {
		"name": "Kalle",
		"role": "Kühltechniker",
		"weapon": "Eiskanone",
		"blurb": "Friert ein, was zu schnell ist.",
		"family": "cryo",
		"color": Color(0.35, 0.8, 0.95),
		"skin": Color(0.92, 0.74, 0.6),
		"damage": 18.0, "interval": 0.6, "mag": 6, "reload": 1.5, "cost": 3,
	},
	"margot": {
		"name": "Käpt'n Margot",
		"role": "Pensionierte Kapitänin",
		"weapon": "Schrotflinte",
		"blurb": "Aus der Nähe trifft sie immer.",
		"family": "shotgun",
		"color": Color(0.2, 0.3, 0.55),
		"skin": Color(0.95, 0.8, 0.68),
		"damage": 13.0, "interval": 0.85, "mag": 2, "reload": 1.4, "cost": 3, "pellets": 4,
	},
	"lynx": {
		"name": "Lynx",
		"role": "Scharfschützin",
		"weapon": "Präzisionsgewehr",
		"blurb": "Ein Schuss, und drei Gegner wundern sich.",
		"family": "sniper",
		"color": Color(0.35, 0.55, 0.3),
		"skin": Color(0.75, 0.55, 0.42),
		"damage": 70.0, "interval": 1.3, "mag": 4, "reload": 1.8, "cost": 3, "pierce": 2,
	},
	"fritzi": {
		"name": "Fritzi",
		"role": "Feuerwehrfrau",
		"weapon": "Flammenwerfer",
		"blurb": "Heizt der ersten Reihe richtig ein.",
		"family": "flamer",
		"color": Color(0.95, 0.35, 0.15),
		"skin": Color(0.95, 0.78, 0.64),
		"damage": 8.0, "interval": 0.2, "mag": 20, "reload": 1.8, "cost": 5, "cone": 1.7,
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
		"minion": "schleimling",
	},
	# Welt 2: Zombie-Kolonie
	"krabbler": {
		"name": "Krabbler", "plural": "Krabbler", "tier": "leicht",
		"hp": 34.0, "speed": 2.6, "xp": 1, "dps": 10.0, "size": 0.6, "armor": 0.0,
	},
	"zombie": {
		"name": "Zombie", "plural": "Zombies", "tier": "mittel",
		"hp": 120.0, "speed": 1.2, "xp": 3, "dps": 22.0, "size": 0.85, "armor": 0.0,
	},
	"brecher": {
		"name": "Brecher", "plural": "Brecher", "tier": "stark",
		"hp": 420.0, "speed": 0.75, "xp": 9, "dps": 50.0, "size": 1.1, "armor": 0.35,
	},
	"koloss": {
		"name": "Zombie-Koloss", "plural": "Zombie-Kolosse", "tier": "boss",
		"hp": 3400.0, "speed": 0.4, "xp": 0, "dps": 120.0, "size": 2.2, "armor": 0.15,
		"minion": "krabbler",
	},
}

## Welten hinter dem Wurmloch: je 5 Level, Gegner nach Stärke (leicht, mittel, stark, Boss).
## Ab Welt 3 vorerst eingefärbte Varianten und neue Mischungen der vorhandenen Figuren, bis die
## Figuren aus dem Katalog ausgewählt sind. „prefix“ steht vor dem Gegnernamen, „tint“ färbt ein.
const WORLDS := [
	{"name": "Schleim-Welt", "kinds": ["schleimling", "tentakler", "panzerkaefer", "schleimmutter"],
		"c1": Color(0.62, 0.22, 1.0), "c2": Color(0.1, 0.9, 0.85), "rim": Color(0.7, 0.35, 1.0)},
	{"name": "Zombie-Kolonie", "kinds": ["krabbler", "zombie", "brecher", "koloss"],
		"c1": Color(0.35, 0.85, 0.2), "c2": Color(0.95, 0.85, 0.2), "rim": Color(0.5, 1.0, 0.3)},
	{"name": "Frostmond", "kinds": ["schleimling", "tentakler", "panzerkaefer", "schleimmutter"],
		"prefix": "Frost-", "tint": Color(0.6, 0.85, 1.25),
		"c1": Color(0.3, 0.6, 1.0), "c2": Color(0.85, 0.95, 1.0), "rim": Color(0.6, 0.85, 1.0)},
	{"name": "Lava-Kolonie", "kinds": ["krabbler", "zombie", "brecher", "koloss"],
		"prefix": "Lava-", "tint": Color(1.3, 0.65, 0.45),
		"c1": Color(1.0, 0.35, 0.1), "c2": Color(1.0, 0.8, 0.2), "rim": Color(1.0, 0.5, 0.2)},
	{"name": "Giftsumpf", "kinds": ["schleimling", "zombie", "panzerkaefer", "schleimmutter"],
		"prefix": "Gift-", "tint": Color(0.75, 1.25, 0.5),
		"c1": Color(0.4, 0.9, 0.2), "c2": Color(0.8, 0.3, 0.9), "rim": Color(0.6, 1.0, 0.3)},
	{"name": "Kristallhöhlen", "kinds": ["krabbler", "tentakler", "brecher", "koloss"],
		"prefix": "Kristall-", "tint": Color(1.05, 0.8, 1.35),
		"c1": Color(0.95, 0.4, 1.0), "c2": Color(0.4, 1.0, 1.0), "rim": Color(0.9, 0.6, 1.0)},
	{"name": "Sternenwüste", "kinds": ["krabbler", "zombie", "panzerkaefer", "koloss"],
		"prefix": "Sand-", "tint": Color(1.25, 1.05, 0.7),
		"c1": Color(1.0, 0.75, 0.3), "c2": Color(0.5, 0.8, 1.0), "rim": Color(1.0, 0.85, 0.5)},
	{"name": "Nebelfelder", "kinds": ["schleimling", "tentakler", "brecher", "schleimmutter"],
		"prefix": "Nebel-", "tint": Color(0.8, 0.85, 0.95),
		"c1": Color(0.6, 0.65, 0.8), "c2": Color(0.95, 0.95, 1.0), "rim": Color(0.75, 0.8, 1.0)},
	{"name": "Schattenreich", "kinds": ["krabbler", "zombie", "brecher", "koloss"],
		"prefix": "Schatten-", "tint": Color(0.7, 0.55, 1.1),
		"c1": Color(0.45, 0.2, 0.8), "c2": Color(0.9, 0.3, 0.6), "rim": Color(0.7, 0.4, 1.0)},
	{"name": "Herz des Wurmlochs", "kinds": ["tentakler", "zombie", "panzerkaefer", "koloss"],
		"prefix": "Wurmloch-", "tint": Color(1.25, 0.55, 1.2),
		"c1": Color(1.0, 0.2, 0.6), "c2": Color(0.3, 0.9, 1.0), "rim": Color(1.0, 0.4, 0.9)},
]
const LEVELS_PER_WORLD := 5
## Namen der Level, je Welt fünf (das fünfte ist der Boss).
const LEVEL_NAMES := [
	["Erster Kontakt", "Glibber im Gang", "Tentakel-Alarm", "Panzer im Schleim", "Die Schleimmutter"],
	["Stille Kolonie", "Schlurfende Schatten", "Krabbelnde Flut", "Die Brecher kommen", "Der Koloss erwacht"],
	["Eisiger Empfang", "Frostnebel", "Gefrorene Tentakel", "Kristallpanzer", "Die Frostmutter"],
	["Glühender Boden", "Ascheregen", "Feuerläufer", "Magmabrecher", "Der Lava-Koloss"],
	["Blubbernde Tümpel", "Sumpfgas", "Moorzombies", "Giftpanzer", "Die Sumpfmutter"],
	["Funkelnder Eingang", "Spiegelgänge", "Schwebende Tentakel", "Kristallbrecher", "Der Kristallkoloss"],
	["Sandsturm", "Dünenläufer", "Glühende Mittagssonne", "Panzer im Sand", "Der Wüstenkoloss"],
	["Dichter Nebel", "Stimmen im Dunst", "Nebeltentakel", "Unsichtbare Brecher", "Mutter des Nebels"],
	["Lichtloses Tor", "Schattenläufer", "Flüsternde Horde", "Brecher der Dunkelheit", "Der Schattenkoloss"],
	["Am Ereignishorizont", "Verzerrte Zeit", "Sturm der Tentakel", "Letzte Verteidigung", "Das Herz des Wurmlochs"],
]
## Anzahl der Level (Welten × 5). Wächst mit jeder neuen Welt.
const LEVEL_COUNT := 50

# --- Level-Baukasten -------------------------------------------------------------
# Jedes Level entsteht aus wenigen Werten: Lebenskurve (level_hp), Wellenzahl und Mischung
# nach Position in der Welt. Die Gegnerzahl wächst nur mäßig (Handy-Leistung), schwerer wird es
# vor allem über die Lebenspunkte. Level 1–10 behalten ihre abgestimmten Werte.

## Ab hier wächst das Gegnerleben je Level um diesen Faktor (vorher linear).
const HP_GROWTH := 1.06
## Ab Level 11 wächst der Schaden der Gegner mit dem Schild der Station mit, dazu dieser Druck je Level.
const DPS_GROWTH := 1.06
## Ab diesem Level brauchen Bosse ohne Käufe in der Regel einen Versuch mehr (Konzept, Abschnitt 9).
const HARD_BOSS_FROM := 21
const HARD_BOSS_HP := 1.3


static func world_of(level: int) -> int:
	return clampi((level - 1) / LEVELS_PER_WORLD, 0, WORLDS.size() - 1)


static func level_name(level: int) -> String:
	var w := world_of(level)
	if w >= LEVEL_NAMES.size():
		return ""
	return LEVEL_NAMES[w][(level - 1) % LEVELS_PER_WORLD]


static func world_name(level: int) -> String:
	return WORLDS[world_of(level)]["name"]


static func is_boss_level(level: int) -> bool:
	return level % LEVELS_PER_WORLD == 0


## Färbung der Gegner dieser Welt (Weiß = Originalfarben).
static func world_tint(level: int) -> Color:
	return WORLDS[world_of(level)].get("tint", Color(1, 1, 1))


## Name eines Gegners in der Welt dieses Levels (mit Vorsilbe der Welt).
static func enemy_name(kind: String, level: int, plural := false) -> String:
	var d: Dictionary = ENEMIES[kind]
	var n: String = d["plural"] if plural else d["name"]
	var prefix: String = WORLDS[world_of(level)].get("prefix", "")
	return prefix + n if prefix == "" else prefix + n.substr(0, 1).to_upper() + n.substr(1)


static func waves_in_level(level: int) -> int:
	return 5 + (level - 1) % LEVELS_PER_WORLD + 1 + mini(world_of(level), 3)


## Grundleben der Gegner in diesem Level (1 = Level 1).
static func level_hp(level: int) -> float:
	if level <= 10:
		return 1.0 + 0.2 * (level - 1)
	return 2.8 * pow(HP_GROWTH, level - 10)


## Schild der Station in diesem Level (vor Boni).
static func fence_base(level: int) -> float:
	return 1000.0 + 300.0 * (level - 1)


## Schadensfaktor der Gegner: bis Level 10 unverändert, danach wächst er mit dem Schild mit,
## damit Gegner den Schild auch in hohen Leveln gefährden.
static func dps_mult(level: int) -> float:
	if level <= 10:
		return 1.0
	return fence_base(level) / fence_base(10) * pow(DPS_GROWTH, level - 10)


static func hp_mult(level: int, wave: int) -> float:
	return level_hp(level) * (1.0 + 0.04 * (wave - 1))


## Zusätzlicher Lebensfaktor für den Boss dieses Levels.
static func boss_hp(level: int) -> float:
	return HARD_BOSS_HP if level >= HARD_BOSS_FROM else 1.0


## Stellt die Gegner einer Welle zusammen (Art nach Welt, Menge nach Level in der Welt).
static func wave_spawns(level: int, wave: int) -> Array[String]:
	var list: Array[String] = []
	var kinds: Array = WORLDS[world_of(level)]["kinds"]
	var lw := (level - 1) % LEVELS_PER_WORLD + 1
	var extra := mini(world_of(level), 2)
	var total := waves_in_level(level)
	var light := 2 + int(wave * 0.7) + lw + extra
	var mid := 0
	if wave >= 2:
		mid = int((wave - 1) * 0.55 + (lw - 1) * 0.6) + extra
	var heavy := 0
	if (lw >= 2 or extra > 0) and wave >= 3:
		heavy = int((wave - 2) / 3.0)
		if lw >= 4 and wave % 2 == 0:
			heavy += 1
	if wave == total and not is_boss_level(level):
		heavy += 1
	for i in light:
		list.append(kinds[0])
	for i in mid:
		list.append(kinds[1])
	for i in heavy:
		list.append(kinds[2])
	list.shuffle()
	if is_boss_level(level) and wave == total:
		list.append(kinds[3])
	return list


## Erfahrung, die für den nächsten Aufstieg nötig ist.
static func xp_needed(levelups_so_far: int) -> int:
	return 10 + levelups_so_far * 6
