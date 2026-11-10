class_name GameData
extends RefCounted
## Feste Spieldaten des Piloten: Helden, Gegner, Wellen.
## Namen und Werte sind Arbeitsstände und werden beim Balancing angepasst.

const HERO_IDS := ["dusty", "iska", "brocken", "volta", "kalle", "margot", "lynx", "fritzi",
	"fuenkchen", "pip", "rollo", "nova"]

## Heldentyp: Start-Helden tragen den Anfang eines Kampfes. Verstärkungs-Helden sind als erster
## Held schwächer, werden aber stark, wenn sie im Kampf per Karte dazugerufen werden:
## eigener Schaden +30 %, das ganze Team +6 % (je Verstärkung).
const HERO_TYPE := {"dusty": "start", "iska": "start", "brocken": "start", "kalle": "start", "fritzi": "start",
	"volta": "verstaerkung", "margot": "verstaerkung", "lynx": "verstaerkung",
	"fuenkchen": "start", "rollo": "start", "pip": "verstaerkung", "nova": "verstaerkung"}
const REINFORCE_DAMAGE := 0.3
const TEAM_AURA := 0.06


static func hero_type_text(id: String) -> String:
	if HERO_TYPE.get(id, "start") == "verstaerkung":
		return "Verstärkung: im Kampf dazugerufen +30 % Schaden, Team +6 %"
	return "Start-Held: stark von Anfang an"

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
		"weapon": "Funkenpistole",
		"blurb": "Trifft einen und schockt die Nachbarn mit.",
		"family": "tesla",
		"color": Color(0.62, 0.36, 0.95),
		"skin": Color(0.9, 0.72, 0.58),
		"damage": 16.0, "interval": 0.55, "mag": 8, "reload": 1.6, "cost": 4, "chain": 2,
	},
	"kalle": {
		"name": "Kalle",
		"role": "Kühltechniker",
		"weapon": "Frostpistole",
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
		"weapon": "Brandflinte",
		"blurb": "Heizt der ersten Reihe richtig ein.",
		"family": "flamer",
		"color": Color(0.95, 0.35, 0.15),
		"skin": Color(0.95, 0.78, 0.64),
		"damage": 8.0, "interval": 0.2, "mag": 20, "reload": 1.8, "cost": 5, "cone": 1.7,
	},
	# Ab hier die Champions aus dem zweiten Entwurf (03.11.2026); bis die GLB-Modelle da sind,
	# zeigen die Menüs das Entwurfsbild (ui/heroes2d) und der Kampf eine einfache Figur.
	"fuenkchen": {
		"name": "Fünkchen",
		"role": "Weltraumdrache",
		"weapon": "Sternenatem",
		"blurb": "Ein Atemzug, und die ganze Reihe glüht.",
		"family": "beam",
		"color": Color(0.6, 0.38, 0.92),
		"skin": Color(0.62, 0.42, 0.9),
		"damage": 30.0, "interval": 0.7, "mag": 5, "reload": 1.6, "cost": 4, "pierce": 4,
	},
	"pip": {
		"name": "Pip",
		"role": "Cyberbot",
		"weapon": "Schraubenwerfer",
		"blurb": "Repariert die Mauer, während er schraubt.",
		"family": "drone",
		"color": Color(0.2, 0.75, 0.78),
		"skin": Color(0.95, 0.9, 0.8),
		"damage": 12.0, "interval": 0.5, "mag": 8, "reload": 1.4, "cost": 3, "repair": 0.0015,
	},
	"rollo": {
		"name": "Rollo",
		"role": "Mini-Panzer",
		"weapon": "Wuchtkanone",
		"blurb": "Schiebt alles zurück, was zu nah kommt.",
		"family": "cannon",
		"color": Color(0.95, 0.55, 0.15),
		"skin": Color(0.25, 0.3, 0.55),
		"damage": 45.0, "interval": 0.8, "mag": 3, "reload": 1.8, "cost": 4, "push": 1.5,
	},
	"nova": {
		"name": "Nova",
		"role": "Exo-Pilotin",
		"weapon": "Raketenfäuste",
		"blurb": "Zieht die Gegner zusammen und bremst sie aus.",
		"family": "gravity",
		"color": Color(0.5, 0.3, 0.85),
		"skin": Color(0.66, 0.45, 0.32),
		"damage": 20.0, "interval": 0.6, "mag": 6, "reload": 1.6, "cost": 3, "radius": 1.6,
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
	# Dschungelmond (Level 51–60, freigegeben 10.11.2026): eigene Comic-Gegner mit eigenen Farben und Namen
	# (own_look: keine Färbung, keine Vorsilbe der Welt). Der starke Gegner (Borkenkäfer) folgt; bis dahin
	# eingefärbter Panzerkäfer bzw. Brecher. Werte wie die Gegner gleicher Stärke aus Welt 1, damit die Abstimmung gleich bleibt.
	"rankling": {
		"name": "Rankling", "plural": "Ranklinge", "tier": "leicht", "own_look": true,
		"hp": 28.0, "speed": 2.3, "xp": 1, "dps": 8.0, "size": 0.55, "armor": 0.0,
	},
	"bluetenschnapper": {
		"name": "Blütenschnapper", "plural": "Blütenschnapper", "tier": "mittel", "own_look": true,
		"hp": 95.0, "speed": 1.45, "xp": 3, "dps": 18.0, "size": 0.8, "armor": 0.0,
	},
	"urwaldriese": {
		"name": "Urwaldriese", "plural": "Urwaldriesen", "tier": "boss", "own_look": true,
		"hp": 2000.0, "speed": 0.45, "xp": 0, "dps": 90.0, "size": 2.0, "armor": 0.1,
		"minion": "rankling",
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
	# --- Level 51–150 (Schritt 2): je Planet zwei Welten, vorerst mit eingefärbten Gegnern ---
	# Planet Dschungelmond (Level 51–60)
	{"name": "Rankendickicht", "kinds": ["rankling", "bluetenschnapper", "panzerkaefer", "urwaldriese"],
		"prefix": "Ranken-", "tint": Color(0.70, 1.20, 0.60),
		"c1": Color(0.22, 0.93, 0.07), "c2": Color(0.62, 0.28, 0.92), "rim": Color(0.44, 0.96, 0.34)},
	{"name": "Blütenwipfel", "kinds": ["rankling", "bluetenschnapper", "brecher", "urwaldriese"],
		"prefix": "Blüten-", "tint": Color(1.25, 0.80, 1.00),
		"c1": Color(0.93, 0.07, 0.45), "c2": Color(0.28, 0.92, 0.44), "rim": Color(0.96, 0.34, 0.61)},
	# Planet Ozeanwelt (Level 61–70)
	{"name": "Korallenriff", "kinds": ["schleimling", "tentakler", "panzerkaefer", "schleimmutter"],
		"prefix": "Riff-", "tint": Color(0.60, 1.15, 1.25),
		"c1": Color(0.07, 0.79, 0.93), "c2": Color(0.92, 0.28, 0.37), "rim": Color(0.34, 0.87, 0.96)},
	{"name": "Tiefseegraben", "kinds": ["krabbler", "tentakler", "brecher", "koloss"],
		"prefix": "Tiefsee-", "tint": Color(0.50, 0.75, 1.30),
		"c1": Color(0.07, 0.34, 0.93), "c2": Color(0.92, 0.53, 0.28), "rim": Color(0.34, 0.53, 0.96)},
	# Planet Kristallplanet (Level 71–80)
	{"name": "Rosenkristalle", "kinds": ["schleimling", "zombie", "panzerkaefer", "schleimmutter"],
		"prefix": "Rosen-", "tint": Color(1.30, 0.75, 1.10),
		"c1": Color(0.93, 0.07, 0.62), "c2": Color(0.28, 0.92, 0.32), "rim": Color(0.96, 0.34, 0.74)},
	{"name": "Glitzerschlucht", "kinds": ["krabbler", "tentakler", "brecher", "koloss"],
		"prefix": "Glitzer-", "tint": Color(1.15, 1.00, 1.35),
		"c1": Color(0.44, 0.07, 0.93), "c2": Color(0.84, 0.92, 0.28), "rim": Color(0.60, 0.34, 0.96)},
	# Planet Sturmriese (Level 81–90)
	{"name": "Wolkenwirbel", "kinds": ["schleimling", "tentakler", "brecher", "schleimmutter"],
		"prefix": "Sturm-", "tint": Color(1.20, 1.15, 0.70),
		"c1": Color(0.93, 0.84, 0.07), "c2": Color(0.28, 0.54, 0.92), "rim": Color(0.96, 0.90, 0.34)},
	{"name": "Blitzfront", "kinds": ["krabbler", "zombie", "panzerkaefer", "koloss"],
		"prefix": "Blitz-", "tint": Color(0.85, 1.00, 1.35),
		"c1": Color(0.07, 0.33, 0.93), "c2": Color(0.92, 0.54, 0.28), "rim": Color(0.34, 0.52, 0.96)},
	# Planet Schrottwelt (Level 91–100)
	{"name": "Schrotthalden", "kinds": ["krabbler", "zombie", "brecher", "koloss"],
		"prefix": "Schrott-", "tint": Color(1.25, 0.85, 0.60),
		"c1": Color(0.93, 0.40, 0.07), "c2": Color(0.28, 0.87, 0.92), "rim": Color(0.96, 0.58, 0.34)},
	{"name": "Robo-Fabrik", "kinds": ["schleimling", "tentakler", "panzerkaefer", "schleimmutter"],
		"prefix": "Robo-", "tint": Color(0.85, 0.95, 1.10),
		"c1": Color(0.07, 0.41, 0.93), "c2": Color(0.92, 0.47, 0.28), "rim": Color(0.34, 0.59, 0.96)},
	# Planet Wolkenstadt (Level 101–110)
	{"name": "Himmelsbrücken", "kinds": ["krabbler", "tentakler", "brecher", "koloss"],
		"prefix": "Himmels-", "tint": Color(1.15, 1.15, 1.25),
		"c1": Color(0.07, 0.07, 0.93), "c2": Color(0.92, 0.73, 0.28), "rim": Color(0.34, 0.34, 0.96)},
	{"name": "Goldene Türme", "kinds": ["schleimling", "zombie", "panzerkaefer", "schleimmutter"],
		"prefix": "Gold-", "tint": Color(1.30, 1.10, 0.60),
		"c1": Color(0.93, 0.68, 0.07), "c2": Color(0.28, 0.65, 0.92), "rim": Color(0.96, 0.79, 0.34)},
	# Planet Sporenwelt (Level 111–120)
	{"name": "Pilzwald", "kinds": ["schleimling", "tentakler", "panzerkaefer", "schleimmutter"],
		"prefix": "Pilz-", "tint": Color(1.30, 0.80, 0.50),
		"c1": Color(0.93, 0.39, 0.07), "c2": Color(0.28, 0.87, 0.92), "rim": Color(0.96, 0.57, 0.34)},
	{"name": "Sporennebel", "kinds": ["krabbler", "zombie", "brecher", "koloss"],
		"prefix": "Sporen-", "tint": Color(0.60, 1.25, 1.15),
		"c1": Color(0.07, 0.93, 0.79), "c2": Color(0.92, 0.28, 0.57), "rim": Color(0.34, 0.96, 0.87)},
	# Planet Geistermond (Level 121–130)
	{"name": "Mondruinen", "kinds": ["krabbler", "tentakler", "brecher", "koloss"],
		"prefix": "Mond-", "tint": Color(0.75, 1.10, 1.10),
		"c1": Color(0.07, 0.92, 0.93), "c2": Color(0.92, 0.28, 0.47), "rim": Color(0.34, 0.96, 0.96)},
	{"name": "Geisterhallen", "kinds": ["schleimling", "zombie", "panzerkaefer", "schleimmutter"],
		"prefix": "Geister-", "tint": Color(0.70, 1.25, 1.00),
		"c1": Color(0.07, 0.93, 0.54), "c2": Color(0.92, 0.28, 0.76), "rim": Color(0.34, 0.96, 0.68)},
	# Planet Tempelplanet (Level 131–140)
	{"name": "Tempelschlucht", "kinds": ["krabbler", "zombie", "panzerkaefer", "koloss"],
		"prefix": "Tempel-", "tint": Color(1.20, 1.05, 0.75),
		"c1": Color(0.93, 0.64, 0.07), "c2": Color(0.28, 0.69, 0.92), "rim": Color(0.96, 0.76, 0.34)},
	{"name": "Goldenes Heiligtum", "kinds": ["schleimling", "tentakler", "brecher", "schleimmutter"],
		"prefix": "Hüter-", "tint": Color(1.30, 1.15, 0.55),
		"c1": Color(0.93, 0.75, 0.07), "c2": Color(0.28, 0.60, 0.92), "rim": Color(0.96, 0.84, 0.34)},
	# Planet Schwarzes Loch (Level 141–150)
	{"name": "Trümmerfeld", "kinds": ["krabbler", "zombie", "brecher", "koloss"],
		"prefix": "Trümmer-", "tint": Color(0.90, 0.85, 1.00),
		"c1": Color(0.36, 0.07, 0.93), "c2": Color(0.90, 0.92, 0.28), "rim": Color(0.55, 0.34, 0.96)},
	{"name": "Schlund des Schwarzen Lochs", "kinds": ["krabbler", "tentakler", "panzerkaefer", "koloss"],
		"prefix": "Schlund-", "tint": Color(1.10, 0.60, 1.35),
		"c1": Color(0.64, 0.07, 0.93), "c2": Color(0.69, 0.92, 0.28), "rim": Color(0.76, 0.34, 0.96)},
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
	["Grünes Dickicht", "Lianenpfad", "Schnappende Blüten", "Panzer im Laub", "Der Urwaldriese"],
	["Über den Wipfeln", "Duftende Falle", "Blütenschwarm", "Brecher im Geäst", "Der Riese erwacht"],
	["Brandung", "Korallengärten", "Tentakel im Riff", "Muschelpanzer", "Die Riffmutter"],
	["Abtauchen", "Leuchtende Tiefe", "Druckwelle", "Brecher der Tiefe", "Der Tiefseekoloss"],
	["Rosa Funkeln", "Kristallregen", "Gläserne Horde", "Facettenpanzer", "Die Kristallmutter"],
	["Schluchteingang", "Spiegelwände", "Glitzertentakel", "Splitterbrecher", "Der Glitzerkoloss"],
	["Aufwind", "Wirbelsturm", "Tentakel im Wind", "Donnerbrecher", "Die Sturmmutter"],
	["Erstes Grollen", "Elektrische Luft", "Blitzzombies", "Geladene Panzer", "Der Donnerkoloss"],
	["Rostige Hügel", "Klappernde Teile", "Schrottzombies", "Brecher aus Blech", "Der Schrottkoloss"],
	["Fließband", "Dampf und Funken", "Greifarme", "Stahlpanzer", "Die Maschinenmutter"],
	["Über den Wolken", "Windige Stege", "Tentakel im Himmel", "Wolkenbrecher", "Der Himmelskoloss"],
	["Glänzende Kuppeln", "Turmwache", "Goldener Ansturm", "Goldpanzer", "Die Goldmutter"],
	["Leuchtende Hüte", "Sporenpfad", "Pilztentakel", "Panzer unterm Hut", "Die Pilzmutter"],
	["Dichte Sporen", "Husten und Niesen", "Sporenzombies", "Moderbrecher", "Der Sporenkoloss"],
	["Stille Ruinen", "Mondlicht", "Tentakel im Gemäuer", "Ruinenbrecher", "Der Mondkoloss"],
	["Knarrende Tore", "Flackernde Lichter", "Geisterzug", "Spukpanzer", "Die Geistermutter"],
	["Uralte Stufen", "Säulengang", "Tempelwächter", "Steinpanzer", "Der Tempelkoloss"],
	["Verborgene Kammer", "Goldene Fallen", "Hüter der Tentakel", "Brecher des Heiligtums", "Die Hütermutter"],
	["Treibende Wracks", "Schwerelos", "Trümmerzombies", "Wrackbrecher", "Der Trümmerkoloss"],
	["Sog", "Gekrümmtes Licht", "Letzter Ansturm", "Panzer am Abgrund", "Der Schlundkoloss"],
]
## Anzahl der Level (Welten × 5). Wächst mit jeder neuen Welt.
const LEVEL_COUNT := 150

# --- Level-Baukasten -------------------------------------------------------------
# Jedes Level entsteht aus wenigen Werten: Lebenskurve (level_hp), Wellenzahl und Mischung
# nach Position in der Welt. Die Gegnerzahl wächst nur mäßig (Handy-Leistung), schwerer wird es
# vor allem über die Lebenspunkte. Level 1–10 behalten ihre abgestimmten Werte.

## Ab hier wächst das Gegnerleben je Level um diesen Faktor (vorher linear).
## (static var statt const, damit das Balance-Labor Werte per --hpg= / --dpsg= ausprobieren kann)
static var HP_GROWTH := 1.055
## Ab Level 11 wächst der Schaden der Gegner mit dem Schild der Station mit, dazu dieser Druck je Level.
static var DPS_GROWTH := 1.035
## Ab Level 21 (Spiel-Phase 2) ein spürbarer Sprung, danach wächst es im Gleichschritt mit
## einem Spieler, der regelmäßig aufwertet (abgestimmt mit dem Balance-Labor, docs/BALANCE.md).
const PHASE2_FROM := 21
static var HP_STEP := 6.0   # vorher 10; mit der doppelt langen Bahn treffen Flächenwaffen weniger (Labor 06.11.2026)
static var HP_GROWTH_LATE := 1.01
static var DPS_STEP := 1.6
static var DPS_GROWTH_LATE := 1.0
## Ab Level 51 (Geldphase, Schritt 2) wachsen fast nur noch die Heldenstufen (Profil „Durchschnitt“:
## 0,4 Stufen je Level, +7 % je Stufe); das Gegnerleben wächst hier im Gleichschritt (Balance-Labor).
const PHASE3_FROM := 51
static var HP_STEP3 := 1.28
static var HP_GROWTH_P3 := 1.0355
## Ab diesem Level brauchen Bosse ohne Käufe in der Regel einen Versuch mehr (Konzept, Abschnitt 9).
const HARD_BOSS_FROM := 21
static var HARD_BOSS_HP := 0.8
## Feinabstimmung der Boss-Level (Level -> Faktor auf das Leben aller Gegner dieses Levels).
## Boss-Level haben mehr und gemischtere Wellen; verloren wird meist mitten im Level, nicht am
## Boss. Die Welten sind unterschiedlich, ein gemeinsamer Wert trifft die Zielkurve nicht.
static var BOSS_TUNE := {24: 0.7, 25: 0.7, 30: 0.85, 35: 0.92, 40: 1.05, 44: 0.85, 45: 0.92, 48: 0.85, 50: 0.6,
	120: 0.85, 148: 0.85, 150: 0.65}


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
static func world_tint(level: int, kind := "") -> Color:
	if kind != "" and bool(ENEMIES.get(kind, {}).get("own_look", false)):
		return Color(1, 1, 1)
	return WORLDS[world_of(level)].get("tint", Color(1, 1, 1))


## Gegnerarten der Welt dieses Levels (leicht, mittel, stark, Boss). Mit dem Prüf-Schalter --neue-monster
## die neuen, noch nicht freigegebenen Gegner („kinds_neu“).
static func world_kinds(level: int) -> Array:
	var w: Dictionary = WORLDS[world_of(level)]
	if Models.test_new and w.has("kinds_neu"):
		return w["kinds_neu"]
	return w["kinds"]


## Name eines Gegners in der Welt dieses Levels (mit Vorsilbe der Welt).
static func enemy_name(kind: String, level: int, plural := false) -> String:
	var d: Dictionary = ENEMIES[kind]
	var n: String = d["plural"] if plural else d["name"]
	var prefix: String = "" if bool(d.get("own_look", false)) else WORLDS[world_of(level)].get("prefix", "")
	return prefix + n if prefix == "" else prefix + n.substr(0, 1).to_upper() + n.substr(1)


static func waves_in_level(level: int) -> int:
	return 5 + (level - 1) % LEVELS_PER_WORLD + 1 + mini(world_of(level), 3)


## Grundleben der Gegner in diesem Level (1 = Level 1).
static func level_hp(level: int) -> float:
	if level <= 10:
		return 1.0 + 0.2 * (level - 1)
	if level < PHASE2_FROM:
		return 2.8 * pow(HP_GROWTH, level - 10)
	var late := pow(HP_GROWTH_LATE, mini(level, PHASE3_FROM - 1) - PHASE2_FROM)
	if level >= PHASE3_FROM:
		late *= HP_STEP3 * pow(HP_GROWTH_P3, level - PHASE3_FROM + 1) * world_hp_norm(level)
		if is_boss_level(level):
			# Boss-Level haben mehr und gemischtere Wellen; je später, desto mehr Ausgleich (Labor)
			late *= clampf(0.78 - 0.0022 * (level - 60), 0.55, 0.78)
	return 2.8 * pow(HP_GROWTH, PHASE2_FROM - 11) * HP_STEP * late * float(BOSS_TUNE.get(level, 1.0))


## Ab Level 51: gleicht aus, dass manche Gegnerarten von Haus aus mehr Leben haben (z. B. Krabbler,
## Zombie, Brecher gegenüber Schleimling, Tentakler, Panzerkäfer), damit keine Welt aus der Reihe fällt.
static func world_hp_norm(level: int) -> float:
	var k: Array = world_kinds(level)
	var hp := 0.5 * float(ENEMIES[k[0]]["hp"]) + 0.35 * float(ENEMIES[k[1]]["hp"]) + 0.15 * float(ENEMIES[k[2]]["hp"])
	var ref := 0.5 * 28.0 + 0.35 * 95.0 + 0.15 * 320.0
	return ref / hp


## Schild der Station in diesem Level (vor Boni).
static func fence_base(level: int) -> float:
	return 1000.0 + 300.0 * (level - 1)


## Schadensfaktor der Gegner: bis Level 10 unverändert, danach wächst er mit dem Schild mit,
## damit Gegner den Schild auch in hohen Leveln gefährden.
static func dps_mult(level: int) -> float:
	if level <= 10:
		return 1.0
	var fence := fence_base(level) / fence_base(10)
	if level < PHASE2_FROM:
		return fence * pow(DPS_GROWTH, level - 10)
	return fence * pow(DPS_GROWTH, PHASE2_FROM - 11) * DPS_STEP * pow(DPS_GROWTH_LATE, level - PHASE2_FROM)


static func hp_mult(level: int, wave: int) -> float:
	return level_hp(level) * (1.0 + 0.04 * (wave - 1))


## Zusätzlicher Lebensfaktor für den Boss dieses Levels.
static func boss_hp(level: int) -> float:
	return HARD_BOSS_HP if level >= HARD_BOSS_FROM else 1.0


## Stellt die Gegner einer Welle zusammen (Art nach Welt, Menge nach Level in der Welt).
static func wave_spawns(level: int, wave: int) -> Array[String]:
	var list: Array[String] = []
	var kinds: Array = world_kinds(level)
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
