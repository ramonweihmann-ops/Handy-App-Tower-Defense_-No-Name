class_name MetaData
extends RefCounted
## Feste Daten für alles außerhalb des Kampfs: Helden-Freischaltung und -Stufen, Tech-Baum,
## Talente, Basislager, Missionen, Battle Pass, Glücksrad, Shop.

const ENERGY_MAX := 30
const ENERGY_COST := 5
## Sekunden pro Energiepunkt
const ENERGY_REGEN := 240
const HERO_MAX_LEVEL := 10

## Welches Level gewonnen sein muss, damit ein Held freigeschaltet ist (0 = von Anfang an).
const HERO_UNLOCK := {"dusty": 0, "iska": 0, "brocken": 1, "volta": 2}

const STAGE_NAME := "Schleim-Welt"


## Karten, die ein Held für die nächste Stufe braucht.
static func hero_cards_needed(level: int) -> int:
	return 4 + level * 4


static func hero_gold_needed(level: int) -> int:
	return 60 * level


## Schadensbonus durch die Heldenstufe.
static func hero_damage_mult(level: int) -> float:
	return 1.0 + 0.08 * (level - 1)


# --- Tech-Baum: Knoten werden nacheinander gekauft ---------------------------

const TECH := [
	{"id": "shield1", "title": "Schildgenerator I", "desc": "Schild +10 %", "cost": 100},
	{"id": "start_ammo", "title": "Munitionsvorrat", "desc": "+10 Kugeln zu Beginn", "cost": 200},
	{"id": "lever", "title": "Federhebel", "desc": "Hebel ist 1 s schneller bereit", "cost": 300},
	{"id": "shield2", "title": "Schildgenerator II", "desc": "Schild +10 %", "cost": 450},
	{"id": "count", "title": "Zweiter Lauf", "desc": "+1 Kugel pro Abschuss", "cost": 650},
	{"id": "crit", "title": "Zielhilfe", "desc": "Kritische Treffer +5 %", "cost": 900},
	{"id": "tank", "title": "Großer Speicher", "desc": "+20 Kugeln Platz", "cost": 1200},
	{"id": "shield3", "title": "Schildgenerator III", "desc": "Schild +15 %", "cost": 1600},
	{"id": "xp", "title": "Kampferfahrung", "desc": "Erfahrung +10 %", "cost": 2100},
	{"id": "gate", "title": "Startausrüstung", "desc": "Kugelbahn startet mit +3-Tor", "cost": 2800},
]

# --- Talente: mit Sternen ziehen, gleiche Talente steigen auf ----------------

const TALENT_MAX := 5
const TALENTS := {
	"schnelllader": {"title": "Schnelllader", "desc": "Nachladen +4 % je Stufe", "color": Color(0.3, 0.8, 1.0)},
	"sanitaet": {"title": "Sanitätskoffer", "desc": "Schild heilt 2 % je Stufe nach jeder Welle", "color": Color(1.0, 0.4, 0.45)},
	"kopfgeld": {"title": "Kopfgeld", "desc": "Gold nach dem Kampf +8 % je Stufe", "color": Color(1.0, 0.8, 0.25)},
	"scharfschuetze": {"title": "Scharfschütze", "desc": "Kritische Treffer +2 % je Stufe", "color": Color(1.0, 0.55, 0.2)},
	"munitionslager": {"title": "Munitionslager", "desc": "Speicher +6 Kugeln je Stufe", "color": Color(0.95, 0.9, 0.4)},
	"feuerkraft": {"title": "Feuerkraft", "desc": "Schaden +3 % je Stufe", "color": Color(1.0, 0.35, 0.25)},
	"glueckspilz": {"title": "Glückspilz", "desc": "4 % je Stufe: Kugel im Sammler zählt doppelt", "color": Color(0.4, 1.0, 0.55)},
	"lernfreude": {"title": "Lernfreude", "desc": "Erfahrung +5 % je Stufe", "color": Color(0.7, 0.5, 1.0)},
}
const TALENT_SLOTS := 12

# --- Basislager: jeder Held hat ein Gebäude, das Heldenkarten herstellt -------

const BUILDINGS := {
	"dusty": "Dustys Frachtcontainer",
	"iska": "Iskas Wachturm",
	"brocken": "Brockens Bohrturm",
	"volta": "Voltas Labor",
}
const BUILDING_MAX_LEVEL := 10


## Karten pro Stunde (in der Testphase bewusst schnell)
static func building_rate(level: int) -> float:
	return 2.0 * level


static func building_cap(level: int) -> int:
	return 6 + level * 4


static func building_cost(level: int) -> int:
	return 150 * level


# --- Missionen und Battle Pass -------------------------------------------------

const MISSIONS := [
	{"id": "kills", "text": "Besiege %d Gegner", "goal": 120, "points": 50},
	{"id": "wins", "text": "Gewinne %d Level", "goal": 2, "points": 60},
	{"id": "pulls", "text": "Ziehe %d-mal den Hebel", "goal": 10, "points": 40},
	{"id": "cards", "text": "Wähle %d Fähigkeitskarten", "goal": 12, "points": 40},
	{"id": "waves", "text": "Überstehe %d Wellen", "goal": 25, "points": 50},
	{"id": "boss", "text": "Besiege %d Boss", "goal": 1, "points": 80},
]
const MISSIONS_PER_DAY := 3

const PASS_SEASON := "Saison 1 · Schleim-Welt"
## Saisonende (Unix-Zeit, 28.11.2026 00:00 UTC)
const PASS_END := 1795824000
const PASS_LEVELS := 30
const PASS_POINTS_PER_LEVEL := 100
## Punkte für einen gewonnenen Kampf
const PASS_WIN_POINTS := 20


## Belohnung auf einer Stufe des Battle Pass: {"type", "amount"}
static func pass_reward(level: int, premium: bool) -> Dictionary:
	var cycle := ["gold", "gems", "cards", "stars", "gold", "gems"]
	var type: String = cycle[(level - 1) % cycle.size()]
	var base := {"gold": 150, "gems": 10, "cards": 4, "stars": 1}
	var amount: int = int(base[type]) * (1 + level / 10)
	if premium:
		amount *= 2
	return {"type": type, "amount": amount}


# --- Glücksrad -------------------------------------------------------------

const WHEEL := [
	{"type": "gold", "amount": 100},
	{"type": "gems", "amount": 5},
	{"type": "gold", "amount": 250},
	{"type": "cards", "amount": 3},
	{"type": "energy", "amount": 10},
	{"type": "gems", "amount": 20},
	{"type": "stars", "amount": 1},
	{"type": "gold", "amount": 500},
]

# --- Shop ------------------------------------------------------------------

const SHOP_CHEST_COST := 100
const SHOP_ENERGY_COST := 20
const GEM_PACKS := [
	{"gems": 80, "price": "1,99 €"},
	{"gems": 500, "price": "9,99 €"},
	{"gems": 1200, "price": "19,99 €"},
]

const REWARD_NAMES := {
	"gold": "Gold", "gems": "Edelsteine", "cards": "Heldenkarten", "stars": "Sterne", "energy": "Energie",
}
