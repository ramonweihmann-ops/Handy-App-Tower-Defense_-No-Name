class_name BaseData
## Basislager mit 30 Gebäuden (docs/BASISLAGER.md, Vorlage Vorlage_Raw/Raumbasis_Wege_v1).
## Gebäude 01–12 kommen mit dem 1. bis 12. freigeschalteten Champion (01–05 gibt es von Anfang an),
## 13–30 baut man der Reihe nach ab einem Abenteuer-Level mit Gold, damit die Wege lückenlos wachsen.
##
## kind „prod“: stellt mit der Zeit etwas her (Lager läuft voll); value = Menge pro Stunde.
## kind „boost“: wirkt dauerhaft im Kampf; value = Wert des Bonus.
## Werte von Stufe 1 bis Stufe 10 steigen gleichmäßig von v1 auf v10.

const MAX_LEVEL := 10
## Lager der Erzeuger: so viele Stunden Ertrag passen hinein
const STORE_HOURS := 8.0
const START_COUNT := 5

const BUILDINGS := [
	{"id": "01", "name": "Kommandozentrale", "kind": "prod", "item": "gold", "v1": 40.0, "v10": 400.0,
		"text": "Gold pro Stunde. Ihre Stufe begrenzt die Stufe aller anderen Gebäude."},
	{"id": "02", "name": "Sanitätsstation", "kind": "boost", "bonus": "heal", "v1": 0.02, "v10": 0.06,
		"text": "Schild heilt nach jeder Welle"},
	{"id": "03", "name": "Werkstatt", "kind": "prod", "item": "cards", "v1": 0.5, "v10": 5.0,
		"text": "Heldenkarten pro Stunde für deine Helden"},
	{"id": "04", "name": "Hologrammakademie", "kind": "boost", "bonus": "xp", "v1": 0.03, "v10": 0.15,
		"text": "Mehr Erfahrung im Kampf"},
	{"id": "05", "name": "Reaktorturm", "kind": "prod", "item": "energy", "v1": 1.0 / 3.0, "v10": 1.0,
		"text": "Energie pro Stunde"},
	{"id": "06", "name": "Kommunikationsstation", "kind": "boost", "bonus": "pass_bonus", "v1": 2.0, "v10": 10.0,
		"text": "Pass-Punkte je Sieg zusätzlich"},
	{"id": "07", "name": "Gewächshaus", "kind": "prod", "item": "gold", "v1": 60.0, "v10": 600.0,
		"text": "Gold pro Stunde"},
	{"id": "08", "name": "Roboterlabor", "kind": "boost", "bonus": "rate", "v1": 0.02, "v10": 0.10,
		"text": "Plasma lädt schneller"},
	{"id": "09", "name": "Sternwarte", "kind": "boost", "bonus": "crit", "v1": 0.01, "v10": 0.05,
		"text": "Kritische Treffer häufiger"},
	{"id": "10", "name": "Schiffswerft", "kind": "boost", "bonus": "booster_cd", "v1": 0.03, "v10": 0.15,
		"text": "Booster laden schneller"},
	{"id": "11", "name": "Schildgenerator", "kind": "boost", "bonus": "shield", "v1": 0.02, "v10": 0.10,
		"text": "Stärkerer Schild"},
	{"id": "12", "name": "Trainingshalle", "kind": "boost", "bonus": "damage", "v1": 0.01, "v10": 0.06,
		"text": "Mehr Schaden aller Helden"},
	{"id": "13", "name": "Kristallforschung", "kind": "prod", "item": "gems", "v1": 2.0 / 24.0, "v10": 10.0 / 24.0,
		"level": 13, "gold": 2600, "text": "Edelsteine pro Stunde"},
	{"id": "14", "name": "Panzerwerkstatt", "kind": "boost", "bonus": "heavy_dmg", "v1": 0.02, "v10": 0.10,
		"level": 15, "gold": 3000, "text": "Mehr Schaden gegen starke Gegner und Bosse"},
	{"id": "15", "name": "Drohnenhangar", "kind": "boost", "bonus": "start_ammo", "v1": 2.0, "v10": 10.0,
		"level": 17, "gold": 3400, "text": "Plasma zu Beginn des Kampfes"},
	{"id": "16", "name": "Alchemielabor", "kind": "prod", "item": "stars", "v1": 1.0 / 24.0, "v10": 1.0 / 8.0,
		"level": 19, "gold": 3800, "text": "Talent-Sterne pro Stunde"},
	{"id": "17", "name": "Energiespeicher", "kind": "boost", "bonus": "energy_max", "v1": 2.0, "v10": 10.0,
		"level": 21, "gold": 4200, "text": "Mehr Energie-Maximum"},
	{"id": "18", "name": "Navigationszentrale", "kind": "boost", "bonus": "gold", "v1": 0.03, "v10": 0.15,
		"level": 23, "gold": 4600, "text": "Mehr Gold aus Kämpfen"},
	{"id": "19", "name": "Eisforschung", "kind": "boost", "bonus": "frost", "v1": 0.05, "v10": 0.25,
		"level": 25, "gold": 5000, "text": "Frost verlangsamt stärker"},
	{"id": "20", "name": "Feuerforschung", "kind": "boost", "bonus": "burn", "v1": 0.05, "v10": 0.25,
		"level": 27, "gold": 5400, "text": "Brand macht mehr Schaden"},
	{"id": "21", "name": "Waffenwerkstatt", "kind": "boost", "bonus": "damage", "v1": 0.01, "v10": 0.06,
		"level": 29, "gold": 5800, "text": "Mehr Schaden aller Helden"},
	{"id": "22", "name": "Bibliotheksarchiv", "kind": "boost", "bonus": "cards_bonus", "v1": 0.05, "v10": 0.25,
		"level": 31, "gold": 6200, "text": "Mehr Heldenkarten aus Kämpfen"},
	{"id": "23", "name": "Biolabor", "kind": "boost", "bonus": "medipack", "v1": 0.05, "v10": 0.25,
		"level": 33, "gold": 6600, "text": "Medipack heilt mehr"},
	{"id": "24", "name": "Teleportstation", "kind": "boost", "bonus": "cap", "v1": 3.0, "v10": 15.0,
		"level": 35, "gold": 7000, "text": "Größerer Plasma-Speicher"},
	{"id": "25", "name": "Versorgungsdepot", "kind": "prod", "item": "gold", "v1": 100.0, "v10": 1000.0,
		"level": 37, "gold": 7400, "text": "Gold pro Stunde"},
	{"id": "26", "name": "Veredelungsanlage", "kind": "prod", "item": "cards", "v1": 1.0, "v10": 8.0,
		"level": 39, "gold": 7800, "text": "Heldenkarten pro Stunde für deine Helden"},
	# 27–29 in der Reihenfolge der Grafik (Hangar mit Kran, Palast mit Bannern, Satellitenschüsseln)
	{"id": "27", "name": "Reparaturdock", "kind": "boost", "bonus": "repair_card", "v1": 0.05, "v10": 0.25,
		"level": 41, "gold": 8200, "text": "Schild-Reparatur (Karte) stärker"},
	{"id": "28", "name": "Kommandantenresidenz", "kind": "boost", "bonus": "store_bonus", "v1": 0.1, "v10": 0.5,
		"level": 43, "gold": 8600, "text": "Größeres Lager aller Erzeuger"},
	{"id": "29", "name": "Satellitenkontrolle", "kind": "boost", "bonus": "airstrike", "v1": 0.05, "v10": 0.25,
		"level": 45, "gold": 9000, "text": "Luftschlag stärker"},
	{"id": "30", "name": "Heldenmonument", "kind": "boost", "bonus": "damage", "v1": 0.02, "v10": 0.10,
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
	var f := clampf(float(level - 1) / float(MAX_LEVEL - 1), 0.0, 1.0)
	return lerpf(float(d["v1"]), float(d["v10"]), f)


## Ausbau von Stufe level auf level+1: [Gold, Sterne]
static func upgrade_cost(id: String, level: int) -> Array:
	var i := index_of(id)
	var gold := int(round(150.0 * level * (1.0 + i * 0.1) / 10.0) * 10)
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
