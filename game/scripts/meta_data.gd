class_name MetaData
extends RefCounted
## Feste Daten für alles außerhalb des Kampfs: Helden-Freischaltung und -Stufen, Tech-Baum,
## Talente, Basislager, Missionen, Battle Pass, Glücksrad, Shop.

const ENERGY_MAX := 30
const ENERGY_COST := 5
## Sekunden pro Energiepunkt
const ENERGY_REGEN := 240
const HERO_MAX_LEVEL := 30

## Welches Level gewonnen sein muss, damit ein Held freigeschaltet ist (0 = von Anfang an).
const HERO_UNLOCK := {"dusty": 0, "iska": 0, "brocken": 1, "kalle": 2, "volta": 2, "margot": 3, "lynx": 4, "fritzi": 5}
## Alternativ sofort freischalten mit Edelsteinen
const HERO_UNLOCK_GEMS := 150
## Höchstzahl der Helden in der Aufstellung (aus ihnen werden die Karten im Kampf gezogen)
const SQUAD_MAX := 10

const STAGE_NAME := "Schleim-Welt"


## Karten, die ein Held für die nächste Stufe braucht.
static func hero_cards_needed(level: int) -> int:
	return 4 + level * 4


static func hero_gold_needed(level: int) -> int:
	return 60 * level


## Schadensbonus durch die Heldenstufe: +7 % je Stufe, prozentual (wie das Gegnerleben),
## damit Aufwerten auch in Level 200+ spürbar bleibt.
static var HERO_GROWTH := 1.07


static func hero_damage_mult(level: int) -> float:
	return pow(HERO_GROWTH, level - 1)


# --- Booster: Einsätze im Kampf, 2 davon gleichzeitig ausgerüstet --------------

const BOOSTER_SLOTS := 2
const BOOSTER_MAX := 5
const BOOSTERS := {
	"luftangriff": {"title": "Luftangriff", "desc": "Bomben treffen fünf Stellen der Bahn", "cd": 22.0, "unlock": 0, "icon": "plane"},
	"medipack": {"title": "Medipack", "desc": "Repariert 25 %% des Schilds", "cd": 30.0, "unlock": 0, "icon": "medic"},
	"zeitlupe": {"title": "Zeitlupe", "desc": "Alle Gegner 5 s lang 60 %% langsamer", "cd": 26.0, "unlock": 2, "icon": "clock"},
	"kuppel": {"title": "Schutzkuppel", "desc": "Der Schild nimmt 4 s lang keinen Schaden", "cd": 34.0, "unlock": 3, "icon": "dome"},
	"munition": {"title": "Munitionskiste", "desc": "Sofort 25 Plasma in den Vorrat", "cd": 24.0, "unlock": 1, "icon": "crate"},
}


## Wirkung eines Boosters je Stufe (+15 %) und Abklingzeit (−5 % je Stufe).
static func booster_power(level: int) -> float:
	return 1.0 + 0.15 * (level - 1)


static func booster_cd(id: String, level: int) -> float:
	return float(BOOSTERS[id]["cd"]) * (1.0 - 0.05 * (level - 1))


static func booster_cost(level: int) -> int:
	return 200 * level


# --- Tech-Baum: Knoten werden nacheinander gekauft ---------------------------

const TECH := [
	{"id": "shield1", "title": "Schildgenerator I", "desc": "Schild +10 % in jedem Kampf", "cost": 100},
	{"id": "crit", "title": "Zielhilfe", "desc": "Kritische Treffer +5 %", "cost": 200},
	{"id": "shield2", "title": "Schildgenerator II", "desc": "Schild +10 % in jedem Kampf", "cost": 350},
	{"id": "xp", "title": "Kampfsimulator", "desc": "Erfahrung +10 % nach jedem Kampf", "cost": 550},
	{"id": "gold", "title": "Bergungsteam", "desc": "Gold nach dem Kampf +10 %", "cost": 800},
	{"id": "heal", "title": "Reparaturdrohne", "desc": "Schild heilt 1 % nach jeder Welle", "cost": 1100},
	{"id": "shield3", "title": "Schildgenerator III", "desc": "Schild +15 % in jedem Kampf", "cost": 1500},
	{"id": "crit2", "title": "Zielcomputer", "desc": "Kritische Treffer +5 %", "cost": 2000},
	{"id": "damage", "title": "Waffenkammer", "desc": "Schaden aller Helden +5 %", "cost": 2600},
	{"id": "xp2", "title": "Gefechtsübung", "desc": "Erfahrung +10 % nach jedem Kampf", "cost": 3300},
]

# --- Munition: dauerhafte Stufen für Plasma-Erzeuger und Energiekern -----------------------------

const AMMO_UPGRADES := [
	{"id": "rate", "title": "Plasma-Takt", "desc": "Plasma kommt 6 %% schneller nach (je Stufe)", "max": 10, "cost": 80},
	{"id": "cap", "title": "Plasma-Tank", "desc": "+8 Plasma Platz (je Stufe)", "max": 10, "cost": 60},
	{"id": "start", "title": "Startvorrat", "desc": "+5 Plasma zu Beginn (je Stufe)", "max": 10, "cost": 50},
	{"id": "lever", "title": "Energiekern", "desc": "Energiekern 1,5 s schneller bereit und +2 Plasma (je Stufe)", "max": 5, "cost": 150},
	{"id": "count", "title": "Zweiter Erzeuger", "desc": "+1 Plasma pro Ladung (je Stufe)", "max": 3, "cost": 500},
	{"id": "gate", "title": "Start-Tore", "desc": "Stufe 1: +3-Tor, Stufe 2: zweites ×2-Tor von Anfang an", "max": 2, "cost": 1200},
]


## Goldpreis für die nächste Stufe einer Munitionsverbesserung.
static func ammo_cost(upgrade: Dictionary, level: int) -> int:
	return int(upgrade["cost"]) * (level + 1)

# --- Talente: mit Sternen ziehen, gleiche Talente steigen auf ----------------

const TALENT_MAX := 5
const TALENTS := {
	"schnelllader": {"title": "Schnelllader", "desc": "Nachladen +4 % je Stufe", "color": Color(0.3, 0.8, 1.0)},
	"sanitaet": {"title": "Sanitätskoffer", "desc": "Schild heilt 2 % je Stufe nach jeder Welle", "color": Color(1.0, 0.4, 0.45)},
	"kopfgeld": {"title": "Kopfgeld", "desc": "Gold nach dem Kampf +8 % je Stufe", "color": Color(1.0, 0.8, 0.25)},
	"scharfschuetze": {"title": "Scharfschütze", "desc": "Kritische Treffer +2 % je Stufe", "color": Color(1.0, 0.55, 0.2)},
	"munitionslager": {"title": "Munitionslager", "desc": "Plasma-Tank +6 je Stufe", "color": Color(0.95, 0.9, 0.4)},
	"feuerkraft": {"title": "Feuerkraft", "desc": "Schaden +3 % je Stufe", "color": Color(1.0, 0.35, 0.25)},
	"glueckspilz": {"title": "Glückspilz", "desc": "4 % je Stufe: Plasma zählt doppelt", "color": Color(0.4, 1.0, 0.55)},
	"lernfreude": {"title": "Lernfreude", "desc": "Erfahrung +5 % je Stufe", "color": Color(0.7, 0.5, 1.0)},
}
const TALENT_SLOTS := 12

# --- Basislager: jeder Held hat ein Gebäude, das Heldenkarten herstellt -------

const BUILDINGS := {
	"dusty": "Dustys Frachtcontainer",
	"iska": "Iskas Wachturm",
	"brocken": "Brockens Bohrturm",
	"volta": "Voltas Labor",
	"kalle": "Kalles Kühlhaus",
	"margot": "Margots Kapitänskajüte",
	"lynx": "Lynx' Ausguck",
	"fritzi": "Fritzis Feuerwache",
}
const BUILDING_MAX_LEVEL := 10


## Karten pro Stunde (in der Testphase bewusst schnell)
static func building_rate(level: int) -> float:
	return 0.5 * level


static func building_cap(level: int) -> int:
	return 4 + level * 3


static func building_cost(level: int) -> int:
	return 150 * level


# --- Missionen und Battle Pass -------------------------------------------------

const MISSIONS := [
	{"id": "kills", "text": "Besiege %d Gegner", "goal": 120, "points": 50},
	{"id": "wins", "text": "Gewinne %d Level", "goal": 2, "points": 60},
	{"id": "pulls", "text": "Entlade %d-mal den Energiekern", "goal": 4, "points": 40},
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


# --- Belohnungen pro Kampf (abgestimmt mit scripts/economy-sim.py) ----------------
const LOSS_GOLD := 400


static func win_gold(level: int) -> int:
	return 800 + 80 * level


## Karten je Held im Kampf bei einem Sieg (Niederlage: die Hälfte).
static func win_cards(level: int) -> int:
	return int(5 + 0.55 * level)


## Heldentruhe im Shop: wächst mit dem Fortschritt, damit ein Kauf immer gleich viel bringt.
static func chest_cards(max_level: int) -> int:
	return 10 + int(1.5 * max_level)
const SHOP_ENERGY_COST := 20
const GEM_PACKS := [
	{"gems": 80, "price": "1,99 €"},
	{"gems": 500, "price": "9,99 €"},
	{"gems": 1200, "price": "19,99 €"},
]

const REWARD_NAMES := {
	"gold": "Gold", "gems": "Edelsteine", "cards": "Heldenkarten", "stars": "Sterne", "energy": "Energie",
}
