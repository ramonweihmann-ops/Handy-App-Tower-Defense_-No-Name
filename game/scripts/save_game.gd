extends Node
## Spielstand (als Autoload „Save“ überall erreichbar): Währungen, Energie, Helden, Tech-Baum,
## Talente, Basislager, Missionen und Battle Pass. Wird in user://spielstand.cfg gespeichert.
##
## Im automatischen Test (test_mode) ist alles freigeschaltet, es gibt keine Boni und es
## wird nichts gespeichert, damit die Balance-Tests vergleichbar bleiben.

signal changed

const PATH := "user://spielstand.cfg"

var test_mode := false
## Balance-Labor: Im Test wird ein Spielerprofil (Stufen, Upgrades, Helden) nachgestellt.
## Dann gelten die Werte aus data statt der neutralen Testwerte; gespeichert wird trotzdem nichts.
var sim := false
## Testkonto für die Testphase: "normal" (ohne Käufe) oder "voll" (alles freigeschaltet).
## Beide haben einen eigenen Spielstand in derselben Datei.
var account := "normal"
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
		"daily_streak": 0,
		"wheel_date": "",
		"shop_free_date": "",
		"tutorial_seen": false,
		"unlocked": [],
		"squad": [],
		"ammo_up": {},
		"quality": "hoch",
		"sound": true,
		"music": true,
		"boosters": {},
		"booster_slots": ["luftangriff", "medipack"],
		"prime": false,
		"pass_premium": false,
		"trophies": 0,
		"mp": {"games": 0, "wins": 0, "history": [], "season": -1, "season_games": 0},
	}


func load_game() -> void:
	data = default_data()
	var cfg := ConfigFile.new()
	if cfg.load(PATH) == OK:
		account = String(cfg.get_value("meta", "account", "normal"))
		var stored = cfg.get_value(_section(), "data", {})
		if stored is Dictionary and not stored.is_empty():
			for k in stored.keys():
				data[k] = stored[k]
		elif account == "voll":
			data = full_data()
	_ensure_heroes()


func _section() -> String:
	return "spiel" if account == "normal" else "spiel_" + account


## Zwischen den Testkonten wechseln; der Stand des bisherigen Kontos bleibt erhalten.
func switch_account(kind: String) -> void:
	if kind == account:
		return
	save_game()
	account = kind
	var cfg := ConfigFile.new()
	cfg.load(PATH)
	cfg.set_value("meta", "account", account)
	cfg.save(PATH)
	load_game()
	save_game()


## Konto „Alles freigeschaltet“: so, als hätte jemand alles gekauft und lange gespielt.
func full_data() -> Dictionary:
	var d := default_data()
	d["gold"] = 250000
	d["gems"] = 25000
	d["stars"] = 40
	d["energy"] = MetaData.ENERGY_MAX
	d["max_level"] = GameData.LEVEL_COUNT
	d["hard_unlocked"] = true
	d["prime"] = true
	d["pass_premium"] = true
	d["unlocked"] = GameData.HERO_IDS.duplicate()
	for id in GameData.HERO_IDS:
		d["heroes"][id] = {"level": 15, "cards": 40}
	d["tech"] = MetaData.TECH.size()
	var ups := {}
	for u in MetaData.AMMO_UPGRADES:
		ups[u["id"]] = int(u["max"])
	d["ammo_up"] = ups
	var tal := {}
	for id in MetaData.TALENTS.keys():
		tal[id] = MetaData.TALENT_MAX
	d["talents"] = tal
	var bl := {}
	for id in MetaData.BOOSTERS.keys():
		bl[id] = MetaData.BOOSTER_MAX
	d["boosters"] = bl
	var won := []
	for n in range(1, GameData.LEVEL_COUNT):
		won.append("N" + str(n))
	d["won_levels"] = won
	return d


func has_prime() -> bool:
	return bool(data.get("prime", false))


## Neutrale Testwerte (alles frei, keine Boni) – nur im Test ohne Spielerprofil.
func _neutral() -> bool:
	return test_mode and not sim


func save_game() -> void:
	if test_mode:
		return
	var cfg := ConfigFile.new()
	cfg.load(PATH)  # das andere Testkonto nicht überschreiben
	cfg.set_value("meta", "account", account)
	cfg.set_value(_section(), "data", data)
	cfg.save(PATH)
	changed.emit()


func reset() -> void:
	data = full_data() if account == "voll" else default_data()
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
	if level >= GameData.LEVELS_PER_WORLD:
		data["hard_unlocked"] = true
	save_game()
	return first


func hard_unlocked() -> bool:
	return test_mode or bool(data["hard_unlocked"])


# --- Helden ------------------------------------------------------------------

func hero_unlocked(id: String) -> bool:
	if _neutral():
		return true
	var need: int = MetaData.HERO_UNLOCK.get(id, 0)
	if need == 0 or data["unlocked"].has(id):
		return true
	return data["won_levels"].has("N" + str(need)) or data["won_levels"].has("S" + str(need))


func unlocked_heroes() -> Array[String]:
	var out: Array[String] = []
	for id in GameData.HERO_IDS:
		if hero_unlocked(id):
			out.append(id)
	return out


func unlock_with_gems(id: String) -> bool:
	if hero_unlocked(id) or not spend("gems", MetaData.HERO_UNLOCK_GEMS):
		return false
	data["unlocked"].append(id)
	save_game()
	return true


## Helden in der Aufstellung (nur freigeschaltete). Leer gespeichert heißt: alle freigeschalteten.
func squad() -> Array[String]:
	var out: Array[String] = []
	var chosen: Array = data["squad"]
	for id in unlocked_heroes():
		if _neutral() or chosen.is_empty() or chosen.has(id):
			out.append(id)
	return out


func in_squad(id: String) -> bool:
	return squad().has(id)


## Nimmt einen Helden in die Aufstellung auf oder heraus. Mindestens 1 bleibt drin.
func toggle_squad(id: String) -> String:
	var current := squad()
	if current.has(id):
		if current.size() <= 1:
			return "Mindestens ein Held muss in der Aufstellung bleiben."
		current.erase(id)
	else:
		if current.size() >= MetaData.SQUAD_MAX:
			return "Die Aufstellung ist voll (höchstens %d Helden)." % MetaData.SQUAD_MAX
		current.append(id)
	data["squad"] = current
	save_game()
	return ""


func hero_level(id: String) -> int:
	if _neutral():
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
	return 0 if _neutral() else int(data["tech"])


func has_tech(id: String) -> bool:
	for i in tech_count():
		if MetaData.TECH[i]["id"] == id:
			return true
	return false


# --- Booster ---------------------------------------------------------------------

func booster_unlocked(id: String) -> bool:
	var need: int = MetaData.BOOSTERS[id]["unlock"]
	if _neutral() or need == 0:
		return true
	return data["won_levels"].has("N" + str(need)) or data["won_levels"].has("S" + str(need))


func booster_level(id: String) -> int:
	return int(data["boosters"].get(id, 1))


func booster_slots() -> Array[String]:
	var out: Array[String] = []
	for id in data["booster_slots"]:
		if MetaData.BOOSTERS.has(id) and booster_unlocked(id):
			out.append(id)
	return out


## Rüstet einen Booster aus oder ab (höchstens 2).
func toggle_booster(id: String) -> String:
	var slots: Array = data["booster_slots"]
	if slots.has(id):
		slots.erase(id)
	else:
		if slots.size() >= MetaData.BOOSTER_SLOTS:
			return "Es passen nur %d Booster in einen Kampf. Nimm zuerst einen heraus." % MetaData.BOOSTER_SLOTS
		slots.append(id)
	save_game()
	return ""


func upgrade_booster(id: String) -> bool:
	var lvl := booster_level(id)
	if lvl >= MetaData.BOOSTER_MAX or not spend("gold", MetaData.booster_cost(lvl)):
		return false
	data["boosters"][id] = lvl + 1
	save_game()
	return true


# --- Munition ----------------------------------------------------------------

func ammo_level(id: String) -> int:
	if _neutral():
		return 0
	return int(data["ammo_up"].get(id, 0))


func buy_ammo_upgrade(id: String) -> bool:
	for u in MetaData.AMMO_UPGRADES:
		if u["id"] == id:
			var lvl := ammo_level(id)
			if lvl >= int(u["max"]) or not spend("gold", MetaData.ammo_cost(u, lvl)):
				return false
			data["ammo_up"][id] = lvl + 1
			save_game()
			return true
	return false


# --- Hinweise fürs Menü: Wo kann gerade etwas aufgewertet oder abgeholt werden? ---

func can_buy_tech() -> bool:
	var i := tech_count()
	return i < MetaData.TECH.size() and gold() >= int(MetaData.TECH[i]["cost"])


func can_buy_ammo(id: String) -> bool:
	for u in MetaData.AMMO_UPGRADES:
		if u["id"] == id:
			var lvl := ammo_level(id)
			return lvl < int(u["max"]) and gold() >= MetaData.ammo_cost(u, lvl)
	return false


func any_ammo_upgrade() -> bool:
	for u in MetaData.AMMO_UPGRADES:
		if can_buy_ammo(String(u["id"])):
			return true
	return false


func can_draw_talent() -> bool:
	if stars() <= 0:
		return false
	for id in MetaData.TALENTS.keys():
		if talent_level(id) < MetaData.TALENT_MAX:
			return true
	return false


func can_upgrade_booster(id: String) -> bool:
	var lvl := booster_level(id)
	return booster_unlocked(id) and lvl < MetaData.BOOSTER_MAX and gold() >= MetaData.booster_cost(lvl)


func any_booster_upgrade() -> bool:
	for id in MetaData.BOOSTERS.keys():
		if can_upgrade_booster(id):
			return true
	return false


func any_hero_ready() -> bool:
	for id in unlocked_heroes():
		if can_level_hero(id):
			return true
	return false


func any_building_ready() -> bool:
	for id in unlocked_heroes():
		if float(building(id)["stock"]) >= 1.0:
			return true
	return false


## Mehrere Talente auf einmal ziehen (z. B. 5 Sterne). Gibt die gezogenen IDs zurück.
func draw_talents(n: int) -> Array[String]:
	var out: Array[String] = []
	for i in n:
		var id := draw_talent()
		if id == "":
			break
		out.append(id)
	return out


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
	if _neutral():
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
	if bool(data.get("pass_premium", false)):
		var pr := MetaData.pass_reward(level, true)
		add(pr["type"], int(pr["amount"]))
	return r


# --- Täglich -------------------------------------------------------------------

# --- Tägliche Belohnung (7-Tage-Kalender und Treue-Serie) ------------------------------

static func _yesterday() -> String:
	return Time.get_date_string_from_unix_time(_now() - 86400)


## Heute schon abgeholt?
func daily_claimed_today() -> bool:
	return str(data.get("daily_date", "")) == today()


## Aktuelle Serie: abgeholte Tage am Stück (bricht ab, wenn ein Tag fehlt)
func daily_streak() -> int:
	var last := str(data.get("daily_date", ""))
	if last == today() or last == _yesterday():
		return int(data.get("daily_streak", 0))
	return 0


## Tag im 7-Tage-Kalender, der heute dran ist (oder heute schon abgeholt wurde), 1..7
func daily_day() -> int:
	var st := daily_streak()
	if daily_claimed_today():
		return (st - 1) % 7 + 1
	return st % 7 + 1


## Tagesbelohnung abholen; gibt die Gewinne für die Erfolgsmeldungen zurück
func claim_daily() -> Array:
	if daily_claimed_today():
		return []
	var day := daily_day()
	var streak := daily_streak() + 1
	data["daily_streak"] = streak
	data["daily_date"] = today()
	var got: Array = []
	for r in MetaData.DAILY_REWARDS[day - 1]:
		got.append(grant(r))
	if streak % 7 == 0:
		for r in MetaData.LOYALTY_CHEST:
			var g := grant(r)
			g["source"] = "Treue-Truhe · %d Tage" % streak
			got.append(g)
	save_game()
	return got


## Einen Gewinn gutschreiben: {type, amount, hero}
func grant(r: Dictionary) -> Dictionary:
	var t := str(r["type"])
	var n := int(r.get("amount", 1))
	match t:
		"hero":
			add_hero_cards(str(r["hero"]), n)
		"pass":
			add_pass_points(n)
		_:
			add(t, n)
	return r.duplicate()


func daily_ready(key: String) -> bool:
	return data.get(key, "") != today()


func mark_daily(key: String) -> void:
	data[key] = today()
	save_game()


# --- Multiplayer: Pokale, Liga, letzte Kämpfe, Saison -----------------------------

func trophies() -> int:
	return int(data.get("trophies", 0))


func mp() -> Dictionary:
	if not data.has("mp") or not data["mp"] is Dictionary:
		data["mp"] = {"games": 0, "wins": 0, "history": [], "season": -1, "season_games": 0}
	return data["mp"]


## Ergebnis eines Kampfes speichern: Pokale, Verlauf (die letzten 10). Gibt die Pokal-Änderung zurück.
func mp_record(place: int, standings: Array) -> int:
	var m := mp()
	var before := trophies()
	var d := MpData.trophy_delta(before, place)
	if not test_mode:
		data["trophies"] = before + d
		m["games"] = int(m["games"]) + 1
		m["season_games"] = int(m.get("season_games", 0)) + 1
		if place == 1:
			m["wins"] = int(m["wins"]) + 1
		var rows: Array = []
		for e in standings:
			rows.append({"name": e["name"], "hero": e["hero"], "kills": e["kills"], "secs": int(e["secs"]),
				"points": e["points"], "me": e.get("me", false)})
		var hist: Array = m["history"]
		hist.push_front({"date": today(), "place": place, "delta": d, "rows": rows})
		while hist.size() > 10:
			hist.pop_back()
		save_game()
	return d


## Liga-Rangliste der laufenden Saison: 30 Kommandanten derselben Liga (inkl. Spieler), absteigend.
## Die anderen sind im Pilot Computergegner; ihre Pokale wachsen über die Saison langsam an.
func leaderboard(now := -1) -> Array:
	if now < 0:
		now = _now()
	var season := MpData.season(now)
	var mine := trophies()
	var league := MpData.league_index(mine)
	var lo: int = MpData.LEAGUES[league]["from"]
	var hi: int = MpData.LEAGUES[league + 1]["from"] if league + 1 < MpData.LEAGUES.size() else lo + 2000
	var rng := RandomNumberGenerator.new()
	rng.seed = season * 101 + league * 7 + 3
	var names: Array = MpData.NAMES.duplicate()
	var progress := 1.0 - float(MpData.season_left(now)) / float(MpData.SEASON_DAYS * 86400)
	var rows: Array = []
	for i in 29:
		var n: String = names.pop_at(rng.randi_range(0, names.size() - 1)) if not names.is_empty() else "Kommandant_%d" % i
		var base := rng.randf_range(lo, lo + (hi - lo) * 0.85)
		var gain := rng.randf_range(0.0, (hi - lo) * 0.25)
		rows.append({"name": n, "hero": GameData.HERO_IDS[rng.randi_range(0, GameData.HERO_IDS.size() - 1)],
			"trophies": int(base + gain * progress), "me": false})
	var me_hero: String = squad()[0] if not squad().is_empty() else "dusty"
	rows.append({"name": "DU", "hero": me_hero, "trophies": mine, "me": true})
	rows.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		if a["trophies"] != b["trophies"]:
			return a["trophies"] > b["trophies"]
		return bool(a["me"]))
	for i in rows.size():
		rows[i]["rank"] = i + 1
	return rows


func leaderboard_rank() -> int:
	for r in leaderboard():
		if r["me"]:
			return int(r["rank"])
	return 30


## Saisonwechsel: Wer in der letzten Saison gespielt hat, bekommt eine Truhe nach seinem Platz
## (goldene Truhe für die ersten Plätze, sonst silberne). Gibt die Gewinne zurück (leer = nichts).
func mp_season_check() -> Array:
	var m := mp()
	var now := _now()
	var cur := MpData.season(now)
	var last := int(m.get("season", -1))
	if last == cur:
		return []
	var got: Array = []
	if last >= 0 and int(m.get("season_games", 0)) > 0:
		# Platz zum Ende der letzten Saison (die Rangliste dieses Zeitpunkts nachbilden)
		var end_time := (last + 1) * MpData.SEASON_DAYS * 86400 - 1
		var rank := 30
		for r in leaderboard(end_time):
			if r["me"]:
				rank = int(r["rank"])
		var chest: Array = MetaData.MP_CHEST_GOLD if rank <= MpData.GOLD_CHEST_RANKS else MetaData.MP_CHEST_SILVER
		for r in chest:
			var g := grant(r)
			g["source"] = "Saison-Truhe · Platz %d" % rank
			got.append(g)
	m["season"] = cur
	m["season_games"] = 0
	save_game()
	return got


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
	var crit := 0.02 * talent_level("scharfschuetze")
	if has_tech("crit"):
		crit += 0.05
	if has_tech("crit2"):
		crit += 0.05
	var gates: Array[String] = []
	if ammo_level("gate") >= 1:
		gates.append("plus3")
	if ammo_level("gate") >= 2:
		gates.append("x2")
	return {
		"shield": shield,
		"start_ammo": 5 * ammo_level("start"),
		"lever": 1.5 * ammo_level("lever"),
		"lever_balls": 2 * ammo_level("lever"),
		"count": ammo_level("count"),
		"rate": 0.06 * ammo_level("rate"),
		"crit": crit,
		"cap": 8 * ammo_level("cap") + 6 * talent_level("munitionslager"),
		"xp": (0.1 if has_tech("xp") else 0.0) + (0.1 if has_tech("xp2") else 0.0) + 0.05 * talent_level("lernfreude"),
		"gates": gates,
		"reload": 0.04 * talent_level("schnelllader"),
		"heal": 0.02 * talent_level("sanitaet") + (0.01 if has_tech("heal") else 0.0),
		"gold": 0.08 * talent_level("kopfgeld") + (0.1 if has_tech("gold") else 0.0),
		"damage": 0.03 * talent_level("feuerkraft") + (0.05 if has_tech("damage") else 0.0),
		"lucky": 0.04 * talent_level("glueckspilz"),
	}
