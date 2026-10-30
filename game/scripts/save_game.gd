extends Node
## Spielstand (als Autoload „Save“ überall erreichbar): Währungen, Energie, Helden, Tech-Baum,
## Talente, Basislager, Missionen und Battle Pass. Wird in user://spielstand.cfg gespeichert.
##
## Im automatischen Test (test_mode) ist alles freigeschaltet, es gibt keine Boni und es
## wird nichts gespeichert, damit die Balance-Tests vergleichbar bleiben.

signal changed

const PATH := "user://spielstand.cfg"

var test_mode := false
var data := {}


func _ready() -> void:
	load_game()


func default_data() -> Dictionary:
	var heroes := {}
	for id in GameData.HERO_IDS:
		heroes[id] = {"level": 1, "cards": 0}
	var buildings := {}
	for id in GameData.HERO_IDS:
		buildings[id] = {"level": 1, "stock": 0.0, "time": _now()}
	return {
		"name": "Kommandant",
		"gold": 300,
		"gems": 100,
		"stars": 1,
		"energy": MetaData.ENERGY_MAX,
		"energy_time": _now(),
		"max_level": 1,
		"won_levels": [],
		"hard_unlocked": false,
		"heroes": heroes,
		"tech": 0,
		"talents": {},
		"buildings": buildings,
		"missions": {"date": "", "ids": [], "progress": {}, "claimed": {}},
		"pass_points": 0,
		"pass_claimed": [],
		"daily_date": "",
		"wheel_date": "",
		"shop_free_date": "",
		"tutorial_seen": false,
	}


func load_game() -> void:
	data = default_data()
	var cfg := ConfigFile.new()
	if cfg.load(PATH) == OK:
		var stored = cfg.get_value("spiel", "data", {})
		if stored is Dictionary:
			for k in stored.keys():
				data[k] = stored[k]
	_ensure_heroes()


func save_game() -> void:
	if test_mode:
		return
	var cfg := ConfigFile.new()
	cfg.set_value("spiel", "data", data)
	cfg.save(PATH)
	changed.emit()


func reset() -> void:
	data = default_data()
	save_game()


func _ensure_heroes() -> void:
	for id in GameData.HERO_IDS:
		if not data["heroes"].has(id):
			data["heroes"][id] = {"level": 1, "cards": 0}
		if not data["buildings"].has(id):
			data["buildings"][id] = {"level": 1, "stock": 0.0, "time": _now()}


static func _now() -> int:
	return int(Time.get_unix_time_from_system())


static func today() -> String:
	return Time.get_date_string_from_system()


# --- Währungen --------------------------------------------------------------

func gold() -> int:
	return int(data["gold"])


func gems() -> int:
	return int(data["gems"])


func stars() -> int:
	return int(data["stars"])


func add(type: String, amount: int) -> void:
	match type:
		"gold", "gems", "stars":
			data[type] = int(data[type]) + amount
		"energy":
			_update_energy()
			data["energy"] = int(data["energy"]) + amount
		"cards":
			# Karten für zufällige freigeschaltete Helden
			var ids := unlocked_heroes()
			for i in amount:
				var id: String = ids[randi() % ids.size()]
				data["heroes"][id]["cards"] = int(data["heroes"][id]["cards"]) + 1
	save_game()


func spend(type: String, amount: int) -> bool:
	if int(data[type]) < amount:
		return false
	data[type] = int(data[type]) - amount
	save_game()
	return true


# --- Energie ----------------------------------------------------------------

func _update_energy() -> void:
	var now := _now()
	var e := int(data["energy"])
	var t := int(data["energy_time"])
	if e >= MetaData.ENERGY_MAX:
		data["energy_time"] = now
		return
	var gained := (now - t) / MetaData.ENERGY_REGEN
	if gained > 0:
		e = mini(MetaData.ENERGY_MAX, e + gained)
		t += gained * MetaData.ENERGY_REGEN
		data["energy"] = e
		data["energy_time"] = now if e >= MetaData.ENERGY_MAX else t


func energy() -> int:
	_update_energy()
	return int(data["energy"])


## Sekunden bis zum nächsten Energiepunkt (0, wenn voll).
func energy_next() -> int:
	_update_energy()
	if int(data["energy"]) >= MetaData.ENERGY_MAX:
		return 0
	return MetaData.ENERGY_REGEN - (_now() - int(data["energy_time"]))


func use_energy(amount: int) -> bool:
	if test_mode:
		return true
	_update_energy()
	if int(data["energy"]) < amount:
		return false
	if int(data["energy"]) >= MetaData.ENERGY_MAX:
		data["energy_time"] = _now()
	data["energy"] = int(data["energy"]) - amount
	save_game()
	return true


# --- Level -------------------------------------------------------------------

func max_level() -> int:
	if test_mode:
		return GameData.LEVEL_COUNT
	return int(data["max_level"])


func level_won(level: int, hard: bool) -> bool:
	var key := ("S" if hard else "N") + str(level)
	var first: bool = not data["won_levels"].has(key)
	if first:
		data["won_levels"].append(key)
	if level >= int(data["max_level"]) and level < GameData.LEVEL_COUNT:
		data["max_level"] = level + 1
	if level == GameData.LEVEL_COUNT:
		data["hard_unlocked"] = true
	save_game()
	return first


func hard_unlocked() -> bool:
	return test_mode or bool(data["hard_unlocked"])


# --- Helden ------------------------------------------------------------------

func hero_unlocked(id: String) -> bool:
	if test_mode:
		return true
	var need: int = MetaData.HERO_UNLOCK.get(id, 0)
	if need == 0:
		return true
	return data["won_levels"].has("N" + str(need)) or data["won_levels"].has("S" + str(need))


func unlocked_heroes() -> Array[String]:
	var out: Array[String] = []
	for id in GameData.HERO_IDS:
		if hero_unlocked(id):
			out.append(id)
	return out


func hero_level(id: String) -> int:
	if test_mode:
		return 1
	return int(data["heroes"][id]["level"])


func hero_cards(id: String) -> int:
	return int(data["heroes"][id]["cards"])


func can_level_hero(id: String) -> bool:
	var lvl := hero_level(id)
	return lvl < MetaData.HERO_MAX_LEVEL and hero_cards(id) >= MetaData.hero_cards_needed(lvl) and gold() >= MetaData.hero_gold_needed(lvl)


func level_hero(id: String) -> bool:
	if not can_level_hero(id):
		return false
	var lvl := hero_level(id)
	data["heroes"][id]["cards"] = hero_cards(id) - MetaData.hero_cards_needed(lvl)
	data["gold"] = gold() - MetaData.hero_gold_needed(lvl)
	data["heroes"][id]["level"] = lvl + 1
	save_game()
	return true


func add_hero_cards(id: String, n: int) -> void:
	data["heroes"][id]["cards"] = hero_cards(id) + n


# --- Tech-Baum ---------------------------------------------------------------

func tech_count() -> int:
	return 0 if test_mode else int(data["tech"])


func has_tech(id: String) -> bool:
	for i in tech_count():
		if MetaData.TECH[i]["id"] == id:
			return true
	return false


func buy_next_tech() -> bool:
	var i := tech_count()
	if i >= MetaData.TECH.size():
		return false
	if not spend("gold", int(MetaData.TECH[i]["cost"])):
		return false
	data["tech"] = i + 1
	save_game()
	return true


# --- Talente -------------------------------------------------------------------

func talent_level(id: String) -> int:
	if test_mode:
		return 0
	return int(data["talents"].get(id, 0))


## Zieht ein zufälliges Talent für einen Stern. Gibt die ID zurück oder "".
func draw_talent() -> String:
	var pool: Array[String] = []
	for id in MetaData.TALENTS.keys():
		if talent_level(id) < MetaData.TALENT_MAX:
			pool.append(id)
	if pool.is_empty() or not spend("stars", 1):
		return ""
	var id: String = pool[randi() % pool.size()]
	data["talents"][id] = talent_level(id) + 1
	save_game()
	return id


# --- Basislager --------------------------------------------------------------

func building(id: String) -> Dictionary:
	var b: Dictionary = data["buildings"][id]
	var now := _now()
	var lvl := int(b["level"])
	var hours := (now - int(b["time"])) / 3600.0
	b["stock"] = minf(float(MetaData.building_cap(lvl)), float(b["stock"]) + hours * MetaData.building_rate(lvl))
	b["time"] = now
	return b


func collect_building(id: String) -> int:
	var b := building(id)
	var n := int(floor(float(b["stock"])))
	if n <= 0:
		return 0
	b["stock"] = float(b["stock"]) - n
	add_hero_cards(id, n)
	save_game()
	return n


func upgrade_building(id: String) -> bool:
	var b := building(id)
	var lvl := int(b["level"])
	if lvl >= MetaData.BUILDING_MAX_LEVEL or not spend("gold", MetaData.building_cost(lvl)):
		return false
	b["level"] = lvl + 1
	save_game()
	return true


# --- Missionen und Battle Pass -------------------------------------------------

func missions() -> Dictionary:
	var m: Dictionary = data["missions"]
	if m["date"] != today():
		# Jeden Tag drei andere Missionen, abhängig vom Datum
		var rng := RandomNumberGenerator.new()
		rng.seed = hash(today())
		var idx: Array = range(MetaData.MISSIONS.size())
		for i in range(idx.size() - 1, 0, -1):
			var j := rng.randi_range(0, i)
			var tmp = idx[i]
			idx[i] = idx[j]
			idx[j] = tmp
		var ids: Array = []
		for i in MetaData.MISSIONS_PER_DAY:
			ids.append(MetaData.MISSIONS[idx[i]]["id"])
		data["missions"] = {"date": today(), "ids": ids, "progress": {}, "claimed": {}}
		m = data["missions"]
	return m


func mission_def(id: String) -> Dictionary:
	for d in MetaData.MISSIONS:
		if d["id"] == id:
			return d
	return {}


func track(id: String, amount: int = 1) -> void:
	if test_mode:
		return
	var m := missions()
	if not m["ids"].has(id):
		return
	m["progress"][id] = int(m["progress"].get(id, 0)) + amount


func claim_mission(id: String) -> bool:
	var m := missions()
	var d := mission_def(id)
	if m["claimed"].has(id) or int(m["progress"].get(id, 0)) < int(d["goal"]):
		return false
	m["claimed"][id] = true
	add_pass_points(int(d["points"]))
	return true


func add_pass_points(n: int) -> void:
	if test_mode:
		return
	data["pass_points"] = int(data["pass_points"]) + n
	save_game()


func pass_level() -> int:
	return mini(MetaData.PASS_LEVELS, int(data["pass_points"]) / MetaData.PASS_POINTS_PER_LEVEL)


func pass_progress() -> int:
	if pass_level() >= MetaData.PASS_LEVELS:
		return MetaData.PASS_POINTS_PER_LEVEL
	return int(data["pass_points"]) % MetaData.PASS_POINTS_PER_LEVEL


func pass_claimable() -> Array[int]:
	var out: Array[int] = []
	for l in range(1, pass_level() + 1):
		if not data["pass_claimed"].has(l):
			out.append(l)
	return out


func claim_pass(level: int) -> Dictionary:
	if level > pass_level() or data["pass_claimed"].has(level):
		return {}
	var r := MetaData.pass_reward(level, false)
	data["pass_claimed"].append(level)
	add(r["type"], int(r["amount"]))
	return r


# --- Täglich -------------------------------------------------------------------

func daily_ready(key: String) -> bool:
	return data.get(key, "") != today()


func mark_daily(key: String) -> void:
	data[key] = today()
	save_game()


# --- Boni für den Kampf (Tech-Baum, Talente) -----------------------------------

## Alle Boni gesammelt, damit main.gd sie beim Levelstart anwenden kann.
func battle_bonus() -> Dictionary:
	var shield := 0.0
	if has_tech("shield1"):
		shield += 0.1
	if has_tech("shield2"):
		shield += 0.1
	if has_tech("shield3"):
		shield += 0.15
	return {
		"shield": shield,
		"start_ammo": 10 if has_tech("start_ammo") else 0,
		"lever": 1.0 if has_tech("lever") else 0.0,
		"count": 1 if has_tech("count") else 0,
		"crit": (0.05 if has_tech("crit") else 0.0) + 0.02 * talent_level("scharfschuetze"),
		"cap": (20 if has_tech("tank") else 0) + 6 * talent_level("munitionslager"),
		"xp": (0.1 if has_tech("xp") else 0.0) + 0.05 * talent_level("lernfreude"),
		"gate": "plus3" if has_tech("gate") else "",
		"reload": 0.04 * talent_level("schnelllader"),
		"heal": 0.02 * talent_level("sanitaet"),
		"gold": 0.08 * talent_level("kopfgeld"),
		"damage": 0.03 * talent_level("feuerkraft"),
		"lucky": 0.04 * talent_level("glueckspilz"),
	}
