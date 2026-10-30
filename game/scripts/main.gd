extends Node
## Spielablauf des Piloten: Menü → Held wählen → Kampf mit Kartenauswahl → Ergebnis.
##
## Automatischer Test (ohne Fenster):
##   godot --headless --fixed-fps 60 --path game -- --autotest --level=1 [--seed=1] [--pull]

const SAVE_PATH := "user://pilot.cfg"
const START_AMMO := 30
const START_CAP := 60
## Grundtempo des Spiels (1.0 wäre die Rechengeschwindigkeit); x2 per Knopf.
## Später (etwa ab Level 100) soll x3 dazukommen.
const BASE_SPEED := 0.6
## Breiteste erlaubte Spalte im Verhältnis zur Höhe (Querformat am PC wird zur Hochformat-Spalte).
const MAX_ASPECT := 0.62

var battle: Battle
var ball_run: BallRun
var hud: Hud
var ammo := AmmoStore.new()

var level := 1
var max_unlocked := 1
var xp := 0
var xp_needed := 8
var levelups := 0
var pending_levelups := 0
var card_levels := {}
var cards_taken: Array[String] = []
var state := "menu"
var tempo := 1

var _overlay: Control
var _column: VBoxContainer
var _screen: Control
var _autotest := false
var _auto_pull := false
var _auto_pull_t := 0.0


func _ready() -> void:
	# Hängt das Handy kurz, lieber kurz langsamer werden als viele Schritte nachholen
	Engine.max_physics_steps_per_frame = 3
	_parse_args()
	_load_progress()
	_build_layout()
	if _autotest:
		start_level(level)
	else:
		show_menu()


## Setzt das Spieltempo (x1 oder x2). Die Physik bleibt bei 60 Schritten pro Spielsekunde,
## weniger Schritte lassen schnelle Kugeln durch die Wände der Kugelbahn rutschen.
func _apply_speed(t: int) -> void:
	Engine.time_scale = BASE_SPEED * float(t)


func _parse_args() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg == "--autotest":
			_autotest = true
		elif arg == "--pull":
			_auto_pull = true
		elif arg.begins_with("--level="):
			level = clampi(int(arg.get_slice("=", 1)), 1, GameData.LEVEL_COUNT)
		elif arg.begins_with("--seed="):
			seed(int(arg.get_slice("=", 1)))


func _build_layout() -> void:
	var theme := UiKit.make_theme()
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.theme = theme
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)
	var side_bg := ColorRect.new()
	side_bg.color = Color(0.02, 0.02, 0.05)
	side_bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	side_bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(side_bg)
	var column := VBoxContainer.new()
	_column = column
	column.add_theme_constant_override("separation", 0)
	column.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(column)

	var world_holder := Control.new()
	world_holder.size_flags_vertical = Control.SIZE_EXPAND_FILL
	world_holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	column.add_child(world_holder)
	var container := SubViewportContainer.new()
	container.stretch = true
	container.set_anchors_preset(Control.PRESET_FULL_RECT)
	container.mouse_filter = Control.MOUSE_FILTER_IGNORE
	world_holder.add_child(container)
	var viewport := SubViewport.new()
	viewport.own_world_3d = true
	container.add_child(viewport)
	battle = Battle.new()
	viewport.add_child(battle)
	hud = Hud.new()
	hud.set_anchors_preset(Control.PRESET_FULL_RECT)
	hud.battle = battle
	world_holder.add_child(hud)

	ball_run = BallRun.new()
	ball_run.custom_minimum_size = Vector2(0, BallRun.PANEL_H)
	ball_run.ammo = ammo
	column.add_child(ball_run)

	var layer := CanvasLayer.new()
	layer.layer = 10
	layer.process_mode = Node.PROCESS_MODE_ALWAYS
	add_child(layer)
	_overlay = Control.new()
	_overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	_overlay.theme = theme
	_overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(_overlay)

	get_viewport().size_changed.connect(_fit_column)
	_fit_column()

	battle.enemy_killed.connect(_on_enemy_killed)
	battle.wave_started.connect(func(w: int, total: int) -> void:
		hud.set_wave(level, w, total)
		hud.set_next_wave(battle.next_wave_text())
	)
	battle.fence_changed.connect(hud.set_fence)
	battle.damage_dealt.connect(hud.add_floater)
	battle.level_won.connect(_on_level_won)
	battle.level_lost.connect(_on_level_lost)
	hud.pause_pressed.connect(_on_pause)
	hud.tempo_pressed.connect(_toggle_tempo)


## Hält das Spiel als Hochformat-Spalte in der Mitte, auch im breiten Fenster.
func _fit_column() -> void:
	var vp := get_viewport().get_visible_rect().size
	var w := minf(vp.x, vp.y * MAX_ASPECT)
	_column.anchor_left = 0.5
	_column.anchor_right = 0.5
	_column.anchor_top = 0.0
	_column.anchor_bottom = 1.0
	_column.offset_left = -w * 0.5
	_column.offset_right = w * 0.5
	_column.offset_top = 0.0
	_column.offset_bottom = 0.0


var _perf_t := 0.0


func _process(delta: float) -> void:
	# Leistungsmessung für Tests im Browser (erscheint in der Browser-Konsole)
	_perf_t += delta / maxf(0.01, Engine.time_scale)
	if _perf_t >= 2.0 and state == "battle":
		_perf_t = 0.0
		print("PERF fps=%d tempo=%d gegner=%d kugeln=%d knoten=%d physik_ms=%.1f bild_ms=%.1f" % [
			Engine.get_frames_per_second(), tempo, battle.enemies.size(), ball_run.ball_count(),
			Performance.get_monitor(Performance.OBJECT_NODE_COUNT),
			Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS) * 1000.0,
			Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0])
	if _autotest and state == "battle":
		if battle.elapsed > 900.0:
			_finish_autotest("timeout")
		if _auto_pull:
			_auto_pull_t -= delta
			if _auto_pull_t <= 0.0:
				_auto_pull_t = 1.0
				ball_run.try_manual_pull()


# --- Bildschirme ----------------------------------------------------------

func _set_screen(screen: Control) -> void:
	if _screen:
		_screen.queue_free()
	_screen = screen
	if screen:
		_overlay.add_child(screen)


func _full_screen() -> Control:
	var c := Control.new()
	c.set_anchors_preset(Control.PRESET_FULL_RECT)
	return c


func _centered(parent: Control, separation := 18) -> VBoxContainer:
	var center := CenterContainer.new()
	center.set_anchors_preset(Control.PRESET_FULL_RECT)
	parent.add_child(center)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", separation)
	v.alignment = BoxContainer.ALIGNMENT_CENTER
	center.add_child(v)
	return v


func show_menu() -> void:
	state = "menu"
	get_tree().paused = false
	_apply_speed(1)
	battle.clear()
	ball_run.reset()
	hud.visible = false
	var s := _full_screen()
	s.add_child(UiKit.dim(0.55))
	var v := _centered(s, 16)
	v.custom_minimum_size = Vector2(620, 0)
	var title := UiKit.label("Station am Wurmloch", 52, UiKit.C_GOLD)
	title.add_theme_constant_override("outline_size", 10)
	v.add_child(title)
	v.add_child(UiKit.label("Pilot · Arbeitstitel", 24, UiKit.C_MUTED))
	var how := UiKit.wrap_label(
		"Aus dem Wurmloch kommen Schleimwesen. Deine Crew hinter dem Energiezaun schießt von selbst.\n\n"
		+ "Die Munition kommt aus der Kugelbahn unten: Jede Kugel im Sammler ist Munition. "
		+ "Tore verdoppeln Kugeln oder machen Feuer- und Eismunition. Zieh den Hebel rechts für eine Extra-Ladung.\n\n"
		+ "Bei jedem Aufstieg wählst du eine von drei Karten.", 22, UiKit.C_TEXT)
	how.custom_minimum_size = Vector2(600, 0)
	v.add_child(how)
	var spacer := Control.new()
	spacer.custom_minimum_size = Vector2(0, 8)
	v.add_child(spacer)
	var grid := GridContainer.new()
	grid.columns = 2
	grid.add_theme_constant_override("h_separation", 16)
	grid.add_theme_constant_override("v_separation", 14)
	v.add_child(grid)
	for n in range(1, GameData.LEVEL_COUNT + 1):
		var lvl := n
		var text := "Level %d" % n
		if n == GameData.LEVEL_COUNT:
			text += " · Boss"
		var b := UiKit.button(text, func() -> void: start_level(lvl), 290)
		if n > max_unlocked:
			b.disabled = true
			b.text = "Level %d · gesperrt" % n
		grid.add_child(b)
	v.add_child(UiKit.label("Grafik: Platzhalter aus einfachen Formen", 18, UiKit.C_MUTED))
	_set_screen(s)


func start_level(n: int) -> void:
	level = n
	state = "hero_select"
	get_tree().paused = false
	tempo = 1
	_apply_speed(1)
	ammo.reset(START_CAP, START_AMMO)
	xp = 0
	levelups = 0
	xp_needed = GameData.xp_needed(0)
	pending_levelups = 0
	card_levels.clear()
	cards_taken.clear()
	battle.setup(n, ammo)
	ball_run.reset()
	hud.visible = true
	hud.reset(level, GameData.waves_in_level(level))
	hud.set_next_wave(battle.next_wave_text())
	hud.set_xp(0, xp_needed)
	hud.set_fence(battle.fence_hp, battle.fence_max)
	var options: Array = GameData.HERO_IDS.duplicate()
	options.shuffle()
	options.resize(3)
	if _autotest:
		_set_screen(null)
		_on_hero_picked(options[0])
		return
	_show_hero_picker(options)


func _show_hero_picker(options: Array) -> void:
	var s := _full_screen()
	s.add_child(UiKit.dim(0.6))
	var v := _centered(s, 22)
	v.add_child(UiKit.label("Wer verteidigt die Station?", 40, UiKit.C_GOLD))
	v.add_child(UiKit.label("Wähle deinen ersten Helden", 24, UiKit.C_MUTED))
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)
	v.add_child(row)
	for id in options:
		var d: Dictionary = GameData.HEROES[id]
		var card := {
			"kind": "hero_pick", "target": d["weapon"], "color": d["color"], "title": d["name"],
			"desc": "%s\n\n%s" % [d["role"], d["blurb"]], "stars": 0, "max": 0, "emblem": String(d["name"]).left(1),
		}
		var hero_id: String = id
		row.add_child(_card_button(card, func(_c: Dictionary) -> void: _on_hero_picked(hero_id)))
	_set_screen(s)


func _on_hero_picked(id: String) -> void:
	_set_screen(null)
	battle.add_hero(id)
	cards_taken.append("start:" + id)
	state = "battle"
	if _autotest:
		_apply_speed(1)
	battle.start()
	ball_run.active = true


# --- Erfahrung und Karten ---------------------------------------------------

func _on_enemy_killed(_e: Enemy, gained: int) -> void:
	xp += gained
	while xp >= xp_needed:
		xp -= xp_needed
		levelups += 1
		pending_levelups += 1
		xp_needed = GameData.xp_needed(levelups)
	hud.set_xp(xp, xp_needed)
	if pending_levelups > 0 and state == "battle":
		_open_card_pick.call_deferred()


func _open_card_pick() -> void:
	if state != "battle" or pending_levelups <= 0 or not battle.running:
		return
	var cards := _roll_cards(3)
	if cards.is_empty():
		pending_levelups = 0
		return
	state = "cards"
	get_tree().paused = true
	if _autotest:
		_on_card_picked(_auto_choose(cards))
		return
	var s := _full_screen()
	s.add_child(UiKit.dim(0.6))
	var v := _centered(s, 22)
	v.add_child(UiKit.label("Fähigkeit wählen", 44, UiKit.C_GOLD))
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)
	v.add_child(row)
	for c in cards:
		row.add_child(_card_button(c, _on_card_picked))
	_set_screen(s)


## Kartenwahl im automatischen Test: grob wie ein vernünftiger Spieler.
func _auto_choose(cards: Array) -> Dictionary:
	var best: Dictionary = cards[0]
	var best_score := -1.0
	var starving := battle.ammo_wait_ratio() > 0.25
	for c in cards:
		var score := 3.0
		var key: String = c["key"]
		if c["kind"] == "add_hero":
			score = 10.0 if battle.heroes.size() < 3 else 6.0
		elif c["kind"] == "machine":
			score = 7.0 if starving else 3.5
		elif c["kind"] == "station":
			score = 9.0 if battle.fence_hp < battle.fence_max * 0.5 else 1.0
		elif key.ends_with(":damage") or key.ends_with(":special"):
			score = 5.0
		elif key.ends_with(":rate"):
			score = 4.0
		score += randf()
		if score > best_score:
			best_score = score
			best = c
	return best


func _on_card_picked(card: Dictionary) -> void:
	_set_screen(null)
	var apply: Callable = card["apply"]
	apply.call()
	card_levels[card["key"]] = int(card_levels.get(card["key"], 0)) + 1
	cards_taken.append(card["key"])
	pending_levelups -= 1
	get_tree().paused = false
	state = "battle"
	if pending_levelups > 0:
		_open_card_pick.call_deferred()


func _roll_cards(n: int) -> Array:
	var pool: Array = []
	if battle.heroes.size() < Battle.MAX_HEROES:
		for id in GameData.HERO_IDS:
			if not battle.has_hero(id):
				pool.append(_card_add_hero(id))
	for h in battle.heroes:
		pool.append_array(_hero_cards(h))
	pool.append_array(_machine_cards())
	pool.append(_card_repair())
	pool = pool.filter(func(c: Dictionary) -> bool: return int(c["stars"]) < int(c["max"]) and bool(c.get("available", true)))
	var picked: Array = []
	var has_add := false
	while picked.size() < n and not pool.is_empty():
		var total := 0.0
		for c in pool:
			total += float(c["weight"])
		var r := randf() * total
		var chosen: Dictionary = pool[pool.size() - 1]
		for c in pool:
			r -= float(c["weight"])
			if r <= 0.0:
				chosen = c
				break
		pool.erase(chosen)
		if chosen["kind"] == "add_hero":
			if has_add:
				continue
			has_add = true
		picked.append(chosen)
	return picked


func _card_add_hero(id: String) -> Dictionary:
	var d: Dictionary = GameData.HEROES[id]
	return {
		"key": "add:" + id, "kind": "add_hero", "target": "Neu im Team", "color": d["color"],
		"title": d["name"], "desc": "%s mit %s.\n%s\n+10 Munition" % [d["role"], d["weapon"], d["blurb"]],
		"stars": 0, "max": 1, "emblem": String(d["name"]).left(1),
		"weight": 4.0 if battle.heroes.size() < 2 else 2.2,
		"apply": _apply_add_hero.bind(id),
	}


func _apply_add_hero(id: String) -> void:
	battle.add_hero(id)
	ammo.add("normal", 10)


func _hero_cards(h: Hero) -> Array:
	var d := h.data
	var list: Array = []
	var stats := [
		["damage", "Mehr Schaden", "Schaden +20 %", 5],
		["rate", "Schneller feuern", "Feuerrate +15 %", 5],
		["reload", "Schneller nachladen", "Nachladen 25 % schneller", 3],
		["mag", "Größeres Magazin", "Magazin +50 %\n(braucht mehr Munition)", 3],
		["crit", "Kritische Treffer", "+10 % Chance auf doppelten Schaden", 4],
	]
	var special := {
		"revolver": ["Fächerfeuer", "Der letzte Schuss im Magazin feuert 2 Kugeln mehr", 3],
		"mg": ["Durchschlag", "Kugeln treffen 1 Gegner mehr", 2],
		"rocket": ["Größere Explosion", "Explosionsradius +25 %", 3],
		"tesla": ["Kettenblitz", "Der Blitz springt 1 Gegner weiter", 3],
	}
	var sp: Array = special[h.family()]
	stats.append(["special", sp[0], sp[1], sp[2]])
	for s in stats:
		var mod: String = s[0]
		list.append({
			"key": "%s:%s" % [h.id, mod], "kind": "hero", "target": d["name"], "color": d["color"],
			"title": s[1], "desc": s[2], "stars": int(h.mods[mod]), "max": s[3],
			"emblem": String(d["name"]).left(1), "weight": 1.2 if mod == "special" else 1.0,
			"apply": _apply_hero_mod.bind(h, mod),
		})
	return list


func _apply_hero_mod(h: Hero, mod: String) -> void:
	h.mods[mod] = int(h.mods[mod]) + 1


func _machine_cards() -> Array:
	var free := ball_run.free_slots() > 0
	var gates := [
		["x2", "×2-Tor", "Neues Tor in der Kugelbahn: verdoppelt jede Kugel, die hindurchrollt.", 3],
		["plus3", "+3-Tor", "Neues Tor: Jede Kugel bringt 3 weitere mit.", 2],
		["fire", "Feuer-Tor", "Kugeln werden zu Brandmunition: Getroffene Gegner brennen.", 1],
		["ice", "Eis-Tor", "Kugeln werden zu Frostmunition: Getroffene Gegner werden langsamer.", 1],
	]
	var list: Array = []
	for g in gates:
		var type: String = g[0]
		var count := 0
		for i in BallRun.GATE_SLOTS.size():
			if ball_run._gate_types[i] == type:
				count += 1
		list.append({
			"key": "gate:" + type, "kind": "machine", "target": "Kugelbahn", "color": UiKit.C_MACHINE,
			"title": g[1], "desc": g[2], "stars": count, "max": g[3], "available": free,
			"emblem": BallRun.GATE_INFO[type]["label"], "weight": 1.3,
			"apply": func() -> void: ball_run.add_gate(type),
		})
	list.append({
		"key": "machine:rate", "kind": "machine", "target": "Kugelbahn", "color": UiKit.C_MACHINE,
		"title": "Schneller abschießen", "desc": "Der Hebel schießt 25 % öfter von selbst.",
		"stars": ball_run.rate_level, "max": 4, "emblem": "»", "weight": 1.2,
		"apply": func() -> void: ball_run.upgrade_rate(),
	})
	list.append({
		"key": "machine:count", "kind": "machine", "target": "Kugelbahn", "color": UiKit.C_MACHINE,
		"title": "Mehr Kugeln", "desc": "+1 Kugel pro Abschuss.",
		"stars": ball_run.balls_per_launch - BallRun.BASE_COUNT, "max": 3, "emblem": "+1", "weight": 1.2,
		"apply": func() -> void: ball_run.upgrade_count(),
	})
	list.append({
		"key": "machine:tank", "kind": "machine", "target": "Kugelbahn", "color": UiKit.C_MACHINE,
		"title": "Größerer Speicher", "desc": "Speicher +30, dazu sofort 15 Kugeln.",
		"stars": int(card_levels.get("machine:tank", 0)), "max": 3, "emblem": "+30", "weight": 0.8,
		"apply": _apply_tank,
	})
	return list


func _apply_tank() -> void:
	ammo.raise_cap(30)
	ammo.add("normal", 15)


func _card_repair() -> Dictionary:
	var low := battle.fence_hp / maxf(1.0, battle.fence_max) < 0.6
	return {
		"key": "station:repair", "kind": "station", "target": "Station", "color": UiKit.C_STATION,
		"title": "Schild flicken", "desc": "Schild +35 % und Maximum +10 %.",
		"stars": int(card_levels.get("station:repair", 0)), "max": 3, "emblem": "+",
		"weight": 2.5 if low else 0.5,
		"apply": func() -> void: battle.repair_fence(0.35, 0.1),
	}


func _card_button(card: Dictionary, on_pick: Callable) -> Button:
	var col: Color = card["color"]
	var b := Button.new()
	b.custom_minimum_size = Vector2(214, 380)
	var normal := UiKit.box(Color(0.1, 0.12, 0.22), 18, 3, col)
	var hover := normal.duplicate() as StyleBoxFlat
	hover.bg_color = Color(0.14, 0.17, 0.3)
	b.add_theme_stylebox_override("normal", normal)
	b.add_theme_stylebox_override("hover", hover)
	b.add_theme_stylebox_override("pressed", hover)
	b.pressed.connect(func() -> void: on_pick.call(card))
	var v := VBoxContainer.new()
	v.set_anchors_preset(Control.PRESET_FULL_RECT)
	v.offset_left = 10
	v.offset_right = -10
	v.offset_top = 10
	v.offset_bottom = -12
	v.add_theme_constant_override("separation", 8)
	v.mouse_filter = Control.MOUSE_FILTER_IGNORE
	b.add_child(v)
	var head := PanelContainer.new()
	head.add_theme_stylebox_override("panel", UiKit.box(col, 10))
	head.mouse_filter = Control.MOUSE_FILTER_IGNORE
	head.add_child(UiKit.label(card["target"], 18, Color(0.08, 0.08, 0.12)))
	(head.get_child(0) as Label).add_theme_constant_override("outline_size", 0)
	v.add_child(head)
	var emblem := Emblem.new(col, String(card.get("emblem", "")))
	v.add_child(emblem)
	var title := UiKit.wrap_label(card["title"], 26, UiKit.C_GOLD)
	v.add_child(title)
	var desc := UiKit.wrap_label(card["desc"], 19, UiKit.C_TEXT)
	desc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(desc)
	if int(card["max"]) > 1:
		v.add_child(UiKit.StarRow.new(int(card["stars"]), int(card["max"])))
	return b


## Rundes Abzeichen oben auf einer Karte.
class Emblem extends Control:
	var color: Color
	var text: String

	func _init(color_: Color, text_: String) -> void:
		color = color_
		text = text_
		custom_minimum_size = Vector2(0, 86)
		mouse_filter = Control.MOUSE_FILTER_IGNORE

	func _draw() -> void:
		var c := Vector2(size.x * 0.5, size.y * 0.5)
		draw_circle(c, 40.0, Color(color.r, color.g, color.b, 0.25))
		draw_circle(c, 33.0, color)
		draw_circle(c, 33.0, Color(1, 1, 1, 0.35), false, 3.0)
		var font := ThemeDB.fallback_font
		var fs := 34 if text.length() <= 2 else 20
		draw_string_outline(font, Vector2(c.x - 60, c.y + fs * 0.36), text, HORIZONTAL_ALIGNMENT_CENTER, 120, fs, 6, Color(0, 0, 0, 0.6))
		draw_string(font, Vector2(c.x - 60, c.y + fs * 0.36), text, HORIZONTAL_ALIGNMENT_CENTER, 120, fs, Color(1, 1, 1))


# --- Pause, Tempo, Ende ---------------------------------------------------

func _toggle_tempo() -> void:
	tempo = 2 if tempo == 1 else 1
	_apply_speed(tempo)
	hud.set_tempo(tempo)


func _on_pause() -> void:
	if state != "battle":
		return
	state = "paused"
	get_tree().paused = true
	var s := _full_screen()
	s.add_child(UiKit.dim(0.6))
	var v := _centered(s, 18)
	v.add_child(UiKit.label("Pause", 48, UiKit.C_GOLD))
	v.add_child(UiKit.button("Weiter", _resume))
	v.add_child(UiKit.secondary(UiKit.button("Level neu starten", func() -> void: start_level(level))))
	v.add_child(UiKit.secondary(UiKit.button("Zum Menü", show_menu)))
	_set_screen(s)


func _resume() -> void:
	_set_screen(null)
	state = "battle"
	get_tree().paused = false


func _on_level_won() -> void:
	ball_run.active = false
	if level >= max_unlocked and level < GameData.LEVEL_COUNT:
		max_unlocked = level + 1
		_save_progress()
	if _autotest:
		_finish_autotest("win")
		return
	state = "result"
	_apply_speed(1)
	var title := "Geschafft!"
	var text := "Die Station hält. Level %d ist geschafft." % level
	if level == GameData.LEVEL_COUNT:
		title = "Die Schleimmutter ist besiegt!"
		text = "Alle Level des Piloten sind geschafft. Danke fürs Testen!"
	_show_result(title, text, true)


func _on_level_lost() -> void:
	ball_run.active = false
	if _autotest:
		_finish_autotest("lost")
		return
	state = "result"
	_apply_speed(1)
	_show_result("Der Schild ist gefallen", "Versuch eine andere Kartenwahl. Oft hilft mehr Munition aus der Kugelbahn.", false)


func _show_result(title: String, text: String, won: bool) -> void:
	var s := _full_screen()
	s.add_child(UiKit.dim(0.65))
	var v := _centered(s, 18)
	v.custom_minimum_size = Vector2(600, 0)
	v.add_child(UiKit.label(title, 44, UiKit.C_GOLD if won else Color(1.0, 0.5, 0.45)))
	var t := UiKit.wrap_label(text, 24)
	t.custom_minimum_size = Vector2(580, 0)
	v.add_child(t)
	var secs := int(battle.elapsed)
	v.add_child(UiKit.label("Besiegt: %d  ·  Zeit: %d:%02d  ·  Welle %d/%d" % [battle.kills, secs / 60, secs % 60, battle.wave, battle.total_waves], 22, UiKit.C_MUTED))
	if won and level < GameData.LEVEL_COUNT:
		v.add_child(UiKit.button("Weiter zu Level %d" % (level + 1), func() -> void: start_level(level + 1), 400))
	v.add_child(UiKit.secondary(UiKit.button("Nochmal", func() -> void: start_level(level), 400)))
	v.add_child(UiKit.secondary(UiKit.button("Zum Menü", show_menu, 400)))
	_set_screen(s)


func _finish_autotest(result: String) -> void:
	var names: Array[String] = []
	for h in battle.heroes:
		names.append(h.id)
	print("AUTOTEST level=%d result=%s time=%.0f wave=%d/%d kills=%d fence=%d/%d wait=%.2f collected=%d heroes=%s balls=%d ammo=%d cards=%s" % [
		level, result, battle.elapsed, battle.wave, battle.total_waves, battle.kills,
		int(battle.fence_hp), int(battle.fence_max), battle.ammo_wait_ratio(), ball_run.collected_total,
		",".join(PackedStringArray(names)), ball_run.ball_count(), ammo.total(),
		",".join(PackedStringArray(cards_taken))])
	print("   kugelbahn: ", ball_run.stats)
	get_tree().quit()


# --- Speichern ------------------------------------------------------------

func _load_progress() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(SAVE_PATH) == OK:
		max_unlocked = clampi(int(cfg.get_value("progress", "max_level", 1)), 1, GameData.LEVEL_COUNT)


func _save_progress() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value("progress", "max_level", max_unlocked)
	cfg.save(SAVE_PATH)


func _exit_tree() -> void:
	# Gemeinsame Formen vor dem Herunterfahren der Grafik freigeben
	if Engine.has_meta("fx_cache"):
		Engine.remove_meta("fx_cache")
