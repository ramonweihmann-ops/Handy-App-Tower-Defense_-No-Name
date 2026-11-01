class_name PlasmaCore
extends Node
## Plasma-Erzeuger (ersetzt die Kugelbahn, Mockup „Kampf“): füllt den Plasmavorrat (AmmoStore)
## gleichmäßig auf, im Schnitt so viel, wie die Kugelbahn geliefert hat. Aus dem Vorrat laden
## die Helden ihre Magazine nach.
##
## Energiekern (ersetzt die Überladung am Hebel): lädt sich mit der Zeit und durch besiegte
## Gegner auf. Voll angetippt gibt er einen Schwall Plasma und alle Helden feuern ein paar
## Sekunden doppelt so schnell (Battle.overdrive).
##
## Die Stellschrauben heißen wie bei der Kugelbahn, damit Upgrades, Karten und Spielstand
## unverändert weiterarbeiten: Takt (rate_level, rate_bonus), Menge pro Ladung
## (balls_per_launch), Tore (x2, plus3, fire, ice).

signal manual_pulled

const BASE_INTERVAL := 1.15
const BASE_COUNT := 2
## Ladezeit des Energiekerns in Spielsekunden (ohne Gegner), Plasma pro Kern-Entladung
const MANUAL_CD := 20.0
const OVERLOAD_BALLS := 8
## Jeder besiegte Gegner verkürzt die Ladezeit des Kerns um so viele Sekunden
const KILL_CHARGE := 0.35
## Mehrertrag je Tor (gemessen an der Kugelbahn: ×2-Tor etwa +12 %, +3-Tor etwa +20 %)
const GATE_GAIN := {"x2": 0.12, "plus3": 0.2}
## Anteil des Plasmas, den ein Feuer- oder Eis-Tor in Spezialplasma verwandelt
const SPECIAL_SHARE := 0.3
const GATE_INFO := {
	"x2": {"label": "×2"},
	"plus3": {"label": "+3"},
	"fire": {"label": "FEUER"},
	"ice": {"label": "EIS"},
}
const GATE_ORDER := [1, 3, 4, 0, 2]

var ammo: AmmoStore
var active := false
var launch_interval := BASE_INTERVAL
var balls_per_launch := BASE_COUNT
var rate_level := 0
## Boni aus dem Spielstand: Chance auf doppeltes Plasma, schnellerer Kern (Sekunden), Extra-Plasma
var lucky := 0.0
var manual_cd_bonus := 0.0
var manual_extra := 0
var base_count_bonus := 0
var rate_bonus := 0.0
## Zusätzlicher Faktor auf die Ladegeschwindigkeit des Kerns (Karte „Kern +30 %“)
var core_speed := 1.0
## Für Auswertungen
var collected_total := 0
var stats := {"produced": 0, "full": 0, "cores": 0}

var _gate_types: Array[String] = ["", "", "", "", ""]
var _acc := 0.0
var _manual_cd := 0.0


func reset() -> void:
	for i in _gate_types.size():
		_gate_types[i] = ""
	_gate_types[1] = "x2"
	launch_interval = BASE_INTERVAL
	balls_per_launch = BASE_COUNT
	rate_level = 0
	active = false
	_acc = 0.0
	_manual_cd = MANUAL_CD * 0.5
	collected_total = 0
	lucky = 0.0
	manual_cd_bonus = 0.0
	manual_extra = 0
	rate_bonus = 0.0
	base_count_bonus = 0
	core_speed = 1.0
	stats = {"produced": 0, "full": 0, "cores": 0}


func free_slots() -> int:
	return _gate_types.count("")


func has_gate(type: String) -> bool:
	return _gate_types.has(type)


func add_gate(type: String) -> bool:
	for idx in GATE_ORDER:
		if _gate_types[idx] == "":
			_gate_types[idx] = type
			return true
	return false


func upgrade_rate() -> void:
	rate_level += 1
	update_interval()


func update_interval() -> void:
	launch_interval = BASE_INTERVAL / ((1.0 + 0.25 * rate_level) * (1.0 + rate_bonus))


func upgrade_count() -> void:
	balls_per_launch += 1


## Plasma, das gerade unterwegs ist (bei der Kugelbahn: Kugeln auf der Bahn) – gibt es nicht mehr
func ball_count() -> int:
	return 0


## Plasma pro Spielsekunde
func rate_per_sec() -> float:
	var gain := 0.0
	for t in _gate_types:
		gain += float(GATE_GAIN.get(t, 0.0))
	return float(balls_per_launch) / launch_interval * (1.0 + gain) * (1.0 + lucky)


func _process(delta: float) -> void:
	if not active:
		return
	_acc += rate_per_sec() / (1.0 + lucky) * delta
	while _acc >= 1.0:
		_acc -= 1.0
		_produce()
	_manual_cd = maxf(0.0, _manual_cd - delta * core_speed)


func _produce() -> void:
	var type := "normal"
	for t in _gate_types:
		if (t == "fire" or t == "ice") and randf() < SPECIAL_SHARE:
			type = t
	collected_total += 1
	stats["produced"] += 1
	if ammo and ammo.add(type, 2 if randf() < lucky else 1) == 0:
		stats["full"] += 1


# --- Energiekern --------------------------------------------------------------------------

func core_total() -> float:
	return maxf(1.0, MANUAL_CD - manual_cd_bonus)


## Ladestand des Kerns 0..1
func core_ratio() -> float:
	return clampf(1.0 - _manual_cd / core_total(), 0.0, 1.0)


func core_ready() -> bool:
	return active and _manual_cd <= 0.0


## Ein besiegter Gegner lädt den Kern ein Stück (Bosse mehr)
func on_kill(boss := false) -> void:
	_manual_cd = maxf(0.0, _manual_cd - KILL_CHARGE * (6.0 if boss else 1.0) * core_speed)


## Kern entladen (Antippen oder automatischer Test)
func try_manual_pull() -> void:
	if not core_ready():
		return
	var n := OVERLOAD_BALLS + 4 + manual_extra
	for i in n:
		_produce()
	_manual_cd = core_total()
	stats["cores"] += 1
	manual_pulled.emit()
