class_name MpData
## Multiplayer „4 Kommandanten“ (Konzept: docs/MULTIPLAYER.md): Regeln, Wertung, Ligen und Belohnungen.
## Im Pilot sind die drei anderen Kommandanten Computergegner (MpMatch), später echte Spieler.

## Dauer eines Kampfes in Sekunden; wer bis dahin durchhält, bekommt die volle Zeit gewertet.
const MATCH_TIME := 300.0
const WAVES := 7
const WAVE_TIME := MATCH_TIME / WAVES
## In dieser Welle kommt der Boss (viel früher als im Abenteuer).
const BOSS_WAVE := 5
## Wertung: Punkte je besiegtem Gegner, je Boss und je Sekunde, die die Station hält.
const POINTS_KILL := 10
const POINTS_BOSS := 100
const POINTS_SEC := 2
## Gegner gleichzeitig auf der Bahn je Welle (wer schneller besiegt, bekommt schneller Nachschub).
const ALIVE_BASE := 8
const ALIVE_PER_WAVE := 2
## Sekunden zwischen zwei Gegnern, solange Platz auf der Bahn ist.
const SPAWN_GAP := 0.32
## Lebensfaktor des Bosses gegenüber dem Boss im Abenteuer (früh, aber schaffbar, nicht immer).
static var BOSS_HP := 0.55
## Gegnerleben wächst je Welle um diesen Faktor (viel schneller als im Abenteuer: kurz und heftig)
static var HP_WAVE := 1.22

## Ligen nach Pokalen. Aufstieg und Abstieg ergeben sich aus den Pokalen.
const LEAGUES := [
	{"name": "Bronze-Liga", "from": 0, "c1": Color("#e8964a"), "c2": Color("#a8561a")},
	{"name": "Silber-Liga", "from": 400, "c1": Color("#e6eaee"), "c2": Color("#8d949c")},
	{"name": "Gold-Liga", "from": 1000, "c1": Color("#ffe27a"), "c2": Color("#c8901a")},
	{"name": "Kristall-Liga", "from": 1800, "c1": Color("#b48cff"), "c2": Color("#5a3fd8")},
	{"name": "Sternen-Liga", "from": 2800, "c1": Color("#8fe8ff"), "c2": Color("#2a8ad8")},
	{"name": "Galaxie-Liga", "from": 4000, "c1": Color("#ff9fe0"), "c2": Color("#c2508f")},
]
## Pokale je Platz 1–4, je Liga (in den unteren Ligen geht es schneller aufwärts).
const TROPHIES := [[30, 15, 5, -5], [30, 12, 0, -10], [30, 10, -5, -15], [30, 8, -10, -20]]
## Stärke der Computergegner je Liga (1.0 = ein typischer Spieler auf demselben Stand).
const BOT_SKILL := [1.0, 1.04, 1.08, 1.12, 1.16, 1.2]
const BOT_SKILL_SPREAD := 0.1
## Belohnung je Platz: Anteil am Siegesgold eines Levels, Heldenkarten-Faktor, Pass-Punkte
const GOLD_SHARE := [1.0, 0.75, 0.55, 0.4]
const CARD_SHARE := [1.5, 1.25, 1.0, 0.8]
const PASS_POINTS := [30, 20, 15, 10]
## Eine Saison dauert zwei Wochen.
const SEASON_DAYS := 14
## Plätze in der Liga-Rangliste mit goldener Truhe (darüber steht im Mockup „Aufstiegszone“).
const GOLD_CHEST_RANKS := 5

## Namen der anderen Kommandanten (Pilot: Computergegner, wirken wie echte Spieler)
const NAMES := ["Nebula_Nia", "Kosmo_K", "Orion_X", "Sternfuchs", "Sternenwolf", "Luna_88", "Raketen-Rudi",
	"Komet", "Galaxa", "Astro_Ali", "Mondkind", "Quasar_Q", "Polaris", "Vega_V", "Nova77", "Pulsar",
	"Saturnine", "Meteor_Mo", "Andromeda", "Kassiopeia", "Zenit", "Lyra_L", "Plasma_Pia", "Ion_Ivo",
	"Sirius_S", "Comet_Cleo", "Asteroid_Axel", "Nebelparder", "Sonnenwind", "Gamma_Gil", "Titan_T",
	"Rigel", "Juno_J", "Kepler_K", "Halo_Hanna", "Photon_Phil", "Stella_S", "Draco_D", "Ceres_C", "Eris"]


static func points(kills: int, bosses: int, secs: float) -> int:
	return (kills - bosses) * POINTS_KILL + bosses * POINTS_BOSS + int(minf(secs, MATCH_TIME)) * POINTS_SEC


## Ordnet die Teilnehmer nach Punkten; bei Gleichstand zählt die längere Zeit, dann mehr besiegte Gegner.
## entries: [{name, kills, bosses, secs, ...}] → dieselben Einträge, sortiert, mit „points“ und „place“.
static func rank(entries: Array) -> Array:
	var out: Array = []
	for e in entries:
		var d: Dictionary = e.duplicate()
		d["points"] = points(int(d["kills"]), int(d.get("bosses", 0)), float(d["secs"]))
		out.append(d)
	out.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		if a["points"] != b["points"]:
			return a["points"] > b["points"]
		if float(a["secs"]) != float(b["secs"]):
			return float(a["secs"]) > float(b["secs"])
		return int(a["kills"]) > int(b["kills"]))
	# Feste Regel: Wer früher gefallen ist UND weniger Gegner besiegt hat, steht immer hinter dem
	# anderen, auch wenn ihn ein Boss nach Punkten nach vorn gebracht hätte. So bleibt, wer zuerst
	# fällt und am wenigsten besiegt hat, sicher Letzter.
	var moved := true
	while moved:
		moved = false
		for i in out.size():
			for j in range(i + 1, out.size()):
				if _beats(out[j], out[i]):
					var e: Dictionary = out[j]
					out.remove_at(j)
					out.insert(i, e)
					moved = true
					break
			if moved:
				break
	for i in out.size():
		out[i]["place"] = i + 1
	return out


## a hat länger durchgehalten und mehr Gegner besiegt als b
static func _beats(a: Dictionary, b: Dictionary) -> bool:
	return float(a["secs"]) > float(b["secs"]) and int(a["kills"]) > int(b["kills"])


static func league_index(trophies: int) -> int:
	var idx := 0
	for i in LEAGUES.size():
		if trophies >= int(LEAGUES[i]["from"]):
			idx = i
	return idx


static func league_name(trophies: int) -> String:
	return LEAGUES[league_index(trophies)]["name"]


static func trophy_delta(trophies: int, place: int) -> int:
	var row: Array = TROPHIES[mini(league_index(trophies), TROPHIES.size() - 1)]
	var d: int = row[clampi(place, 1, 4) - 1]
	# Nie unter null
	return maxi(d, -trophies)


## Gegnerstufe („Station“): richtet sich nach dem Fortschritt im Abenteuer.
static func station_level(max_level: int) -> int:
	return clampi(max_level, 1, GameData.LEVEL_COUNT)


static func wave_at(secs: float) -> int:
	return clampi(int(secs / WAVE_TIME) + 1, 1, WAVES)


static func alive_target(wave: int) -> int:
	return ALIVE_BASE + ALIVE_PER_WAVE * (wave - 1)


## Lebensfaktor der Gegner in Welle w
static func hp_mult(level: int, wave: int) -> float:
	# ohne die Sonderabstimmung der Boss-Level im Abenteuer (GameData.BOSS_TUNE)
	var base := GameData.level_hp(level) / float(GameData.BOSS_TUNE.get(level, 1.0))
	return base * hp_tune(level) * pow(HP_WAVE, wave - 1)


## Abstimmung je Levelbereich (gemessen mit scripts/mp-lab.py): Das Abenteuer ist je nach Bereich
## unterschiedlich streng, der Multiplayer soll überall gleich spannend sein. Zwischen den Stützstellen
## wird gleitend übergeblendet.
static var HP_TUNE := {5: 0.85, 15: 1.15, 25: 0.29, 35: 0.31, 45: 0.37}
## Nur für das Labor: fester Faktor statt HP_TUNE (0 = aus)
static var HP_TUNE_FIXED := 0.0


## Leben des Bosses je Levelbereich (zusätzlich zu BOSS_HP), gleitend wie HP_TUNE
static var BOSS_TUNE := {5: 1.0, 15: 1.2, 25: 3.0, 35: 1.9, 45: 1.8}
static var BOSS_TUNE_FIXED := 0.0


static func boss_tune(level: int) -> float:
	if BOSS_TUNE_FIXED > 0.0:
		return BOSS_TUNE_FIXED
	return _interp(BOSS_TUNE, level)


static func hp_tune(level: int) -> float:
	if HP_TUNE_FIXED > 0.0:
		return HP_TUNE_FIXED
	return _interp(HP_TUNE, level)


static func _interp(table: Dictionary, level: int) -> float:
	var keys: Array = table.keys()
	keys.sort()
	if level <= int(keys[0]):
		return float(table[keys[0]])
	for i in range(1, keys.size()):
		var a: int = keys[i - 1]
		var b: int = keys[i]
		if level <= b:
			var f := float(level - a) / float(b - a)
			return exp(lerpf(log(float(table[a])), log(float(table[b])), f))
	return float(table[keys[keys.size() - 1]])


## Nächster Gegner: mit jeder Welle mehr mittlere und starke Gegner.
static func pick_kind(level: int, wave: int, roll: float) -> String:
	var kinds: Array = GameData.WORLDS[GameData.world_of(level)]["kinds"]
	var heavy := 0.0 if wave < 2 else 0.03 + 0.02 * wave
	var mid := 0.15 + 0.035 * wave
	if roll < heavy:
		return kinds[2]
	if roll < heavy + mid:
		return kinds[1]
	return kinds[0]


static func boss_kind(level: int) -> String:
	return GameData.WORLDS[GameData.world_of(level)]["kinds"][3]


## Nummer der laufenden Saison und Sekunden bis zu ihrem Ende
static func season(now: int) -> int:
	return int(now / (SEASON_DAYS * 86400))


static func season_left(now: int) -> int:
	return (season(now) + 1) * SEASON_DAYS * 86400 - now


static func season_left_text(now: int) -> String:
	var left := season_left(now)
	var days := left / 86400
	var hours := (left % 86400) / 3600
	if days > 0:
		return "Saison endet in %d %s %d Std." % [days, "Tag" if days == 1 else "Tagen", hours]
	return "Saison endet in %d Std." % maxi(1, hours)


static func time_text(secs: float) -> String:
	var s := maxi(0, int(ceil(secs)))
	return "%d:%02d" % [s / 60, s % 60]
