class_name MpMatch
extends RefCounted
## Ein Multiplayer-Kampf mit vier Kommandanten. Im Pilot sind die drei anderen Computergegner:
## Sie spielen dieselben Wellen nach einem Modell, das aus echten Testläufen des Spiels gemessen ist
## (docs/MULTIPLAYER.md, scripts/mp-lab.py): besiegte Gegner je Welle, Ausscheiden je Welle, Boss.
## Ihre Stärke streut um die eines typischen Spielers auf demselben Stand und steigt mit der Liga.
## Alles hängt nur vom Startwert ab, damit Läufe nachprüfbar sind.

## Besiegte Gegner je Sekunde eines typischen Spielers, je Welle (gemessen, mp-lab).
static var RATE := [0.55, 0.62, 0.66, 0.68, 0.66, 0.66, 0.64]
## Wahrscheinlichkeit je Sekunde auszuscheiden, je Welle (gemessen, mp-lab).
static var HAZARD := [0.0, 0.0, 0.0002, 0.0008, 0.0016, 0.0024, 0.003]
## Anteil der typischen Spieler, die den Boss besiegen, und wie lange sie dafür brauchen (s).
static var BOSS_CHANCE := 0.5
static var BOSS_DELAY := [12.0, 45.0]
## Wie stark die Stärke wirkt: Rate ~ Stärke^RATE_POW, Ausscheiden ~ Stärke^-HAZARD_POW, Boss ~ Stärke^BOSS_POW.
static var RATE_POW := 0.6
static var HAZARD_POW := 4.0
static var BOSS_POW := 2.5
## Schwankung je Welle (Kartenglück)
static var WAVE_NOISE := 0.12

const STEP := 0.5

var level := 1
var match_seed := 0
var bots: Array = []
var _t := 0.0


## trophies: Pokale des Spielers (Liga bestimmt die Stärke, Pokale der anderen liegen nahe dran)
func _init(level_: int, trophies: int, seed_: int, player_hero := "") -> void:
	level = level_
	match_seed = seed_
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_
	var names: Array = MpData.NAMES.duplicate()
	var heroes: Array = GameData.HERO_IDS.duplicate()
	heroes.erase(player_hero)
	var league := MpData.league_index(trophies)
	var mu: float = MpData.BOT_SKILL[league]
	for i in 3:
		var n: String = names.pop_at(rng.randi_range(0, names.size() - 1))
		var h: String = heroes.pop_at(rng.randi_range(0, heroes.size() - 1))
		var skill := clampf(mu + rng.randfn(0.0, MpData.BOT_SKILL_SPREAD), 0.7, 1.45)
		var b_rng := RandomNumberGenerator.new()
		b_rng.seed = rng.randi()
		var noise: Array[float] = []
		for w in MpData.WAVES:
			noise.append(clampf(1.0 + b_rng.randfn(0.0, WAVE_NOISE), 0.6, 1.4))
		var boss_at := -1.0
		if b_rng.randf() < clampf(BOSS_CHANCE * pow(skill, BOSS_POW), 0.0, 0.97):
			boss_at = (MpData.BOSS_WAVE - 1) * MpData.WAVE_TIME + b_rng.randf_range(BOSS_DELAY[0], BOSS_DELAY[1]) / skill
		bots.append({
			"name": n, "hero": h, "skill": skill, "me": false,
			"trophies": maxi(0, trophies + rng.randi_range(-90, 110)),
			"kills": 0, "bosses": 0, "secs": 0.0, "out": false,
			"_k": 0.0, "_noise": noise, "_boss_at": boss_at, "_rng": b_rng,
		})


## Rechnet die Computergegner bis zur Kampfzeit t weiter.
func step(t: float) -> void:
	t = minf(t, MpData.MATCH_TIME)
	while _t + STEP <= t + 0.0001:
		_t += STEP
		var w := MpData.wave_at(_t - 0.001) - 1
		for b in bots:
			if b["out"]:
				continue
			var s: float = b["skill"]
			b["_k"] = float(b["_k"]) + RATE[w] * pow(s, RATE_POW) * float(b["_noise"][w]) * STEP
			b["kills"] = int(b["_k"]) + int(b["bosses"])
			if float(b["_boss_at"]) > 0.0 and _t >= float(b["_boss_at"]) and int(b["bosses"]) == 0:
				b["bosses"] = 1
				b["kills"] = int(b["kills"]) + 1
			b["secs"] = _t
			var hz: float = HAZARD[w] * pow(s, -HAZARD_POW)
			if (b["_rng"] as RandomNumberGenerator).randf() < hz * STEP:
				b["out"] = true


## Rangliste für die Anzeige im Kampf (inkl. Spieler): sortiert nach bisherigen Punkten.
func live(player: Dictionary) -> Array:
	var all: Array = [player]
	for b in bots:
		all.append(b)
	return MpData.rank(all)


## Kampf zu Ende (Spieler hat durchgehalten oder ist ausgeschieden): Gegner zu Ende rechnen, werten.
func finish(player: Dictionary) -> Array:
	step(MpData.MATCH_TIME)
	return live(player)
