class_name BaseData
## Basislager mit 30 Gebäuden (docs/BASISLAGER.md, Vorlage Vorlage_Raw/Raumbasis_Wege_v1).
## Gebäude 01–12 kommen mit dem 1. bis 12. freigeschalteten Champion (01–05 gibt es von Anfang an),
## 13–30 baut man der Reihe nach ab einem Abenteuer-Level mit Gold, damit die Wege lückenlos wachsen.
##
## kind „prod“: stellt mit der Zeit etwas her (Lager läuft voll); value = Menge pro Stunde.
## kind „boost“: wirkt dauerhaft im Kampf; value = Wert des Bonus.
## Werte von Stufe 1 bis Stufe 10 steigen gleichmäßig von v1 auf v10.
## Die Kampfwerte sind bewusst klein (Balance-Labor 03.11.2026): Die Basis ist ein Bonus für alle,
## sie ersetzt weder das Aufwerten der Helden noch das Sammeln der Karten, und Käufe lohnen sich weiter
## (Schaden zusammen höchstens etwa +5,5 %; die volle Basis bringt etwa eine halbe Heldenstufe).

## Bis Stufe 10 wie bisher; Stufe 11–25 kam mit Level 51–150 dazu (Kommandozentrale 25 = Heldenstufe 60)
const MAX_LEVEL := 25
## Stufe, bis zu der die Werte von v1 auf v10 steigen; danach wächst es halb so schnell weiter
const VALUE_LEVEL := 10
## Lager der Erzeuger: so viele Stunden Ertrag passen hinein
const STORE_HOURS := 8.0
## Seltene Dinge erzeugen weniger als eins in acht Stunden: deren Lager fasst einen ganzen Tag,
## sonst ließe sich auf den ersten Stufen nie etwas abholen
const STORE_HOURS_BY_ITEM := {"gems": 24.0, "stars": 24.0}
const START_COUNT := 5

const BUILDINGS := [
	{"id": "01", "name": "Kommandozentrale", "kind": "prod", "item": "gold", "v1": 40.0, "v10": 400.0,
		"text": "Gold pro Stunde. Ihre Stufe begrenzt die Stufe aller anderen Gebäude."},
	{"id": "02", "name": "Sanitätsstation", "kind": "boost", "bonus": "heal", "v1": 0.005, "v10": 0.015,
		"text": "Schild heilt nach jeder Welle"},
	{"id": "03", "name": "Werkstatt", "kind": "prod", "item": "cards", "v1": 0.5, "v10": 5.0,
		"text": "Heldenkarten pro Stunde für deine Helden"},
	{"id": "04", "name": "Hologrammakademie", "kind": "boost", "bonus": "xp", "v1": 0.0075, "v10": 0.0375,
		"text": "Mehr Erfahrung im Kampf"},
	{"id": "05", "name": "Reaktorturm", "kind": "prod", "item": "energy", "v1": 1.0 / 3.0, "v10": 1.0,
		"text": "Energie pro Stunde"},
	{"id": "06", "name": "Kommunikationsstation", "kind": "boost", "bonus": "pass_bonus", "v1": 2.0, "v10": 10.0,
		"text": "Pass-Punkte je Sieg zusätzlich"},
	{"id": "07", "name": "Gewächshaus", "kind": "prod", "item": "gold", "v1": 60.0, "v10": 600.0,
		"text": "Gold pro Stunde"},
	{"id": "08", "name": "Roboterlabor", "kind": "boost", "bonus": "rate", "v1": 0.005, "v10": 0.025,
		"text": "Plasma lädt schneller"},
	{"id": "09", "name": "Sternwarte", "kind": "boost", "bonus": "crit", "v1": 0.0025, "v10": 0.0125,
		"text": "Kritische Treffer häufiger"},
	{"id": "10", "name": "Schiffswerft", "kind": "boost", "bonus": "booster_cd", "v1": 0.01, "v10": 0.04,
		"text": "Booster laden schneller"},
	{"id": "11", "name": "Schildgenerator", "kind": "boost", "bonus": "shield", "v1": 0.005, "v10": 0.025,
		"text": "Stärkerer Schild"},
	{"id": "12", "name": "Trainingshalle", "kind": "boost", "bonus": "damage", "v1": 0.0025, "v10": 0.015,
		"text": "Mehr Schaden aller Helden"},
	{"id": "13", "name": "Kristallforschung", "kind": "prod", "item": "gems", "v1": 2.0 / 24.0, "v10": 10.0 / 24.0,
		"level": 13, "gold": 2600, "text": "Edelsteine pro Stunde"},
	{"id": "14", "name": "Panzerwerkstatt", "kind": "boost", "bonus": "heavy_dmg", "v1": 0.005, "v10": 0.025,
		"level": 15, "gold": 3000, "text": "Mehr Schaden gegen starke Gegner und Bosse"},
	{"id": "15", "name": "Drohnenhangar", "kind": "boost", "bonus": "start_ammo", "v1": 0.5, "v10": 2.5,
		"level": 17, "gold": 3400, "text": "Plasma zu Beginn des Kampfes"},
	{"id": "16", "name": "Alchemielabor", "kind": "prod", "item": "stars", "v1": 1.0 / 24.0, "v10": 1.0 / 8.0,
		"level": 19, "gold": 3800, "text": "Talent-Sterne pro Stunde"},
	{"id": "17", "name": "Energiespeicher", "kind": "boost", "bonus": "energy_max", "v1": 2.0, "v10": 10.0,
		"level": 21, "gold": 4200, "text": "Mehr Energie-Maximum"},
	{"id": "18", "name": "Navigationszentrale", "kind": "boost", "bonus": "gold", "v1": 0.03, "v10": 0.15,
		"level": 23, "gold": 4600, "text": "Mehr Gold aus Kämpfen"},
	{"id": "19", "name": "Eisforschung", "kind": "boost", "bonus": "frost", "v1": 0.015, "v10": 0.06,
		"level": 25, "gold": 5000, "text": "Frost verlangsamt stärker"},
	{"id": "20", "name": "Feuerforschung", "kind": "boost", "bonus": "burn", "v1": 0.015, "v10": 0.06,
		"level": 27, "gold": 5400, "text": "Brand macht mehr Schaden"},
	{"id": "21", "name": "Waffenwerkstatt", "kind": "boost", "bonus": "damage", "v1": 0.0025, "v10": 0.015,
		"level": 29, "gold": 5800, "text": "Mehr Schaden aller Helden"},
	{"id": "22", "name": "Bibliotheksarchiv", "kind": "boost", "bonus": "cards_bonus", "v1": 0.05, "v10": 0.25,
		"level": 31, "gold": 6200, "text": "Mehr Heldenkarten aus Kämpfen"},
	{"id": "23", "name": "Biolabor", "kind": "boost", "bonus": "medipack", "v1": 0.015, "v10": 0.06,
		"level": 33, "gold": 6600, "text": "Medipack heilt mehr"},
	{"id": "24", "name": "Teleportstation", "kind": "boost", "bonus": "cap", "v1": 1.0, "v10": 4.0,
		"level": 35, "gold": 7000, "text": "Größerer Plasma-Speicher"},
	{"id": "25", "name": "Versorgungsdepot", "kind": "prod", "item": "gold", "v1": 100.0, "v10": 1000.0,
		"level": 37, "gold": 7400, "text": "Gold pro Stunde"},
	{"id": "26", "name": "Veredelungsanlage", "kind": "prod", "item": "cards", "v1": 1.0, "v10": 8.0,
		"level": 39, "gold": 7800, "text": "Heldenkarten pro Stunde für deine Helden"},
	# 27–29 in der Reihenfolge der Grafik (Hangar mit Kran, Palast mit Bannern, Satellitenschüsseln)
	{"id": "27", "name": "Reparaturdock", "kind": "boost", "bonus": "repair_card", "v1": 0.015, "v10": 0.06,
		"level": 41, "gold": 8200, "text": "Schild-Reparatur (Karte) stärker"},
	{"id": "28", "name": "Kommandantenresidenz", "kind": "boost", "bonus": "store_bonus", "v1": 0.1, "v10": 0.5,
		"level": 43, "gold": 8600, "text": "Größeres Lager aller Erzeuger"},
	{"id": "29", "name": "Satellitenkontrolle", "kind": "boost", "bonus": "airstrike", "v1": 0.015, "v10": 0.06,
		"level": 45, "gold": 9000, "text": "Luftschlag stärker"},
	{"id": "30", "name": "Heldenmonument", "kind": "boost", "bonus": "damage", "v1": 0.005, "v10": 0.025,
		"level": 47, "gold": 9400, "text": "Mehr Schaden aller Helden"},
]


static func index_of(id: String) -> int:
	return int(id) - 1


static func info(id: String) -> Dictionary:
	return BUILDINGS[index_of(id)]


static func by_champion(id: String) -> bool:
	return int(id) <= 12


## Wert eines Gebäudes auf einer Stufe
static func value(id: String, level: int) -> float:
	var d: Dictionary = info(id)
	var v1 := float(d["v1"])
	var v10 := float(d["v10"])
	if level <= VALUE_LEVEL:
		return lerpf(v1, v10, clampf(float(level - 1) / float(VALUE_LEVEL - 1), 0.0, 1.0))
	# ab Stufe 11: halbe Steigung, damit die Basis ein Bonus bleibt
	return v10 + (v10 - v1) / float(VALUE_LEVEL - 1) * 0.5 * float(mini(level, MAX_LEVEL) - VALUE_LEVEL)


## Ausbau von Stufe level auf level+1: [Gold, Sterne]
static func upgrade_cost(id: String, level: int) -> Array:
	var i := index_of(id)
	# ab Stufe 10 je Stufe +20 % dazu (Geldphase, abgestimmt mit scripts/progress-sim.py)
	var late := 1.0 + 0.2 * maxi(0, level - VALUE_LEVEL)
	var gold := int(round(150.0 * level * (1.0 + i * 0.1) * late / 10.0) * 10)
	var stars := maxi(0, level - 5)
	return [gold, stars]


## Wert lesbar: Prozent, ganze Zahl oder pro Stunde/Tag
static func value_text(id: String, level: int) -> String:
	var d: Dictionary = info(id)
	var v := value(id, level)
	if d["kind"] == "prod":
		match str(d["item"]):
			"gems":
				return "%s / Tag" % _num(v * 24.0)
			"stars":
				return "1 alle %s Std." % _num(1.0 / maxf(0.001, v))
			"energy":
				return "1 alle %s Std." % _num(1.0 / maxf(0.001, v)) if v < 1.0 else "%s / Std." % _num(v)
		return "%s / Std." % _num(v)
	if str(d["bonus"]) in ["pass_bonus", "start_ammo", "energy_max", "cap"]:
		return "+%d" % roundi(v)
	return "+%s %%" % _num(v * 100.0)


static func _num(v: float) -> String:
	var r := roundf(v * 10.0) / 10.0
	if absf(r - roundf(r)) < 0.05:
		return str(int(roundf(r)))
	return ("%.1f" % r).replace(".", ",")


# --- Texte für das Gebäudefenster (Mockup „Basislager · Gebäude“ / „Bauplatz“) ----------------

## Kurzer Name der Wirkung für die Wertezeile
const ROW_LABELS := {
	"gold": "Gold pro Stunde", "cards": "Heldenkarten pro Stunde", "energy": "Energie pro Tag",
	"gems": "Edelsteine pro Tag", "stars": "Talent-Sterne pro Tag",
	"heal": "Schild-Heilung je Welle", "xp": "Erfahrung im Kampf", "pass_bonus": "Pass-Punkte je Sieg",
	"rate": "Plasma lädt schneller", "crit": "Krit-Chance", "booster_cd": "Booster laden schneller",
	"shield": "Schildstärke", "damage": "Schaden aller Helden", "heavy_dmg": "Schaden gegen Bosse",
	"start_ammo": "Plasma zum Kampfbeginn", "energy_max": "Energie-Maximum", "frost": "Frost bremst stärker",
	"cards_bonus": "Karten aus Kämpfen", "medipack": "Medipack heilt mehr", "cap": "Plasma-Speicher",
	"repair_card": "Schild-Reparatur", "store_bonus": "Lager aller Erzeuger", "airstrike": "Luftschlag",
	"burn": "Brandschaden",
}
## Einheit im Lager der Erzeuger
const STORE_UNITS := {"gold": "Gold", "cards": "Karten", "energy": "Energie", "gems": "Edelsteine", "stars": "Sterne"}

## Beschreibung unter den Werten
const DESCRIPTIONS := {
	"01": "Das Herz deiner Station: Sie bringt Gold, und ihre Stufe gibt vor, wie weit alle anderen Gebäude wachsen können.",
	"02": "Die Sanitätsstation flickt den Schild nach jeder Welle ein Stück. Wirkt dauerhaft in jedem Kampf.",
	"03": "Die Werkstatt stellt Heldenkarten her, auch wenn du nicht spielst. Abholen, bevor das Lager voll ist.",
	"04": "Im Hologramm üben deine Helden weiter: Jeder Kampf bringt etwas mehr Erfahrung.",
	"05": "Der Reaktorturm lädt langsam Energie nach, auch wenn du nicht spielst. Abholen, bevor das Lager voll ist.",
	"06": "Die Kommunikationsstation meldet deine Siege weiter: Jeder Sieg bringt zusätzliche Pass-Punkte.",
	"07": "Im Gewächshaus wächst Gold nach, auch wenn du nicht spielst. Abholen, bevor das Lager voll ist.",
	"08": "Die Roboter im Labor helfen beim Nachladen: Plasma lädt in jedem Kampf etwas schneller.",
	"09": "Die Sternwarte späht Schwachstellen aus: Alle Helden treffen öfter kritisch. Wirkt dauerhaft in jedem Kampf.",
	"10": "Die Schiffswerft wartet deine Booster: Sie sind im Kampf schneller wieder bereit.",
	"11": "Der Schildgenerator verstärkt die Mauer vor deiner Station. Wirkt dauerhaft in jedem Kampf.",
	"12": "In der Trainingshalle üben alle Helden zusammen: Sie machen etwas mehr Schaden.",
	"13": "Die Kristallforschung züchtet Edelsteine, auch wenn du nicht spielst. Abholen, bevor das Lager voll ist.",
	"14": "Die Panzerwerkstatt baut schwere Munition: mehr Schaden gegen starke Gegner und Bosse.",
	"15": "Die Drohnen bringen Plasma schon vor dem ersten Schuss: Jeder Kampf beginnt mit etwas Vorrat.",
	"16": "Im Alchemielabor entstehen Talent-Sterne, auch wenn du nicht spielst. Abholen, bevor das Lager voll ist.",
	"17": "Der Energiespeicher fasst mehr: Dein Energie-Maximum steigt.",
	"18": "Die Navigationszentrale findet lohnende Wege: Kämpfe bringen mehr Gold.",
	"19": "Die Eisforschung macht den Frost kälter: Gegner werden stärker gebremst.",
	"20": "Die Feuerforschung macht den Brand heißer: Brennende Gegner verlieren mehr Leben.",
	"21": "Die Waffenwerkstatt schleift an allen Waffen: Alle Helden machen etwas mehr Schaden.",
	"22": "Im Archiv liegen alte Heldenberichte: Kämpfe bringen mehr Heldenkarten.",
	"23": "Das Biolabor verbessert die Medipacks: Sie heilen den Schild stärker.",
	"24": "Die Teleportstation schafft Platz: Der Plasma-Speicher im Kampf wird größer.",
	"25": "Das Versorgungsdepot sammelt Gold, auch wenn du nicht spielst. Abholen, bevor das Lager voll ist.",
	"26": "Die Veredelungsanlage stellt viele Heldenkarten her, auch wenn du nicht spielst. Abholen, bevor das Lager voll ist.",
	"27": "Im Reparaturdock lernen die Mechaniker dazu: Die Schild-Reparatur aus den Karten wirkt stärker.",
	"28": "Die Kommandantenresidenz lässt anbauen: Alle Erzeuger bekommen ein größeres Lager.",
	"29": "Die Satellitenkontrolle zielt genauer: Der Luftschlag macht mehr Schaden.",
	"30": "Das Heldenmonument erinnert an deine größten Siege: Alle Helden kämpfen etwas stärker.",
}


static func row_label(id: String) -> String:
	var d: Dictionary = info(id)
	return str(ROW_LABELS.get(str(d.get("item", d.get("bonus", ""))), d["text"]))


## Wert für die Wertezeile, ohne Einheit bei den Erzeugern („1,5“), Stufe 0 = noch nicht gebaut
static func row_value(id: String, level: int) -> String:
	var d: Dictionary = info(id)
	var v := value(id, level) if level > 0 else 0.0
	if d["kind"] == "prod":
		if str(d["item"]) in ["energy", "gems", "stars"]:
			v *= 24.0
		return _num(v)
	if str(d["bonus"]) in ["pass_bonus", "start_ammo", "energy_max", "cap"]:
		return "+%d" % roundi(v) if level > 0 else "0"
	return "+%s %%" % _num(v * 100.0) if level > 0 else "0 %"


static func store_hours(id: String) -> float:
	return float(STORE_HOURS_BY_ITEM.get(str(info(id).get("item", "")), STORE_HOURS))


static func store_unit(id: String) -> String:
	return str(STORE_UNITS.get(str(info(id).get("item", "gold")), ""))


static func description(id: String) -> String:
	return str(DESCRIPTIONS.get(id, info(id)["text"]))
