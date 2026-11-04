extends Node
## Spielablauf des Piloten: Menü → Held wählen → Kampf mit Kartenauswahl → Ergebnis.
##
## Automatischer Test (ohne Fenster):
##   godot --headless --fixed-fps 60 --path game -- --autotest --level=1 [--seed=1] [--pull]
## Multiplayer im automatischen Test (Messung für die Computergegner, scripts/mp-lab.py):
##   godot --headless --fixed-fps 60 --path game -- --autotest --mp --level=12 --profile=durchschnitt

const SAVE_PATH := "user://pilot.cfg"
const START_AMMO := 20
const START_CAP := 50
## Grundtempo des Spiels (1.0 wäre die Rechengeschwindigkeit); x2 per Knopf.
## Später (etwa ab Level 100) soll x3 dazukommen.
const BASE_SPEED := 0.6
## Tatsächliches Tempo je Stufe: x1 etwas flotter als das Grundtempo (Wunsch aus dem Test),
## x2 und x3 bleiben beim Doppelten und Dreifachen des Grundtempos, damit der Abstand klar bleibt.
const TEMPO_SCALE := {1: 0.68, 2: 1.2, 3: 1.8}
## Breiteste erlaubte Spalte im Verhältnis zur Höhe (Querformat am PC wird zur Hochformat-Spalte).
const MAX_ASPECT := 0.62
## Energiekern entladen: so lange feuern alle Helden doppelt so schnell
const OVERDRIVE_TIME := 6.0
## Tempo im Multiplayer: x1 etwas flotter als im Abenteuer. In der Testphase per Knopf x1/x2/x3;
## später ein festes Tempo für alle (etwa das 2- bis 2,3-Fache des Abenteuer-x1), im Balance-Labor bestimmt.
const MP_SPEED := 1.0
const MP_TEMPO_SCALE := {1: MP_SPEED, 2: MP_SPEED * 2.0, 3: MP_SPEED * 3.0}

var battle: Battle
var plasma: PlasmaCore
var hud: BattleHud
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

var hard := false
## Multiplayer-Kampf läuft (MpMatch hält die Computergegner)
var mp := false
var mp_match: MpMatch
var _mp_seed := 0
var _mp_curve: Array[int] = []
var _mp_hud_t := 0.0
var bonus := {}
var updater: Updater
var menu: MainMenu
var _xp_carry := 0.0
var _card_wave := 1
var _boosters: Array[String] = []
var _booster_cd: Array[float] = []

var _overlay: Control
var _column: VBoxContainer
var _screen: Control
var _autotest := false
var _auto_pull := false
var _auto_pull_t := 0.0
## Balance-Labor: Spielerprofil für den automatischen Test (tests/balance_profiles.gd).
var _profile := ""
## Nur für Tests mit Fenster: nach 8 Sekunden Kampf ein Bild speichern und beenden (--shot=pfad.png).
var _shot_path := ""
## Nur für Tests mit Fenster: Menübild speichern (--menushot=pfad.png[,reiter[,lager-voll|held:<id>|bau:<id>[:leer]|unterreiter]]) und beenden.
var _menu_shot := ""
var _squad := ""
var _pick_shot := ""
var _world_holder: Control
var _world_container: SubViewportContainer
## Gemaltes Schlachtfeld hinter dem Kampf; _field_fill füllt Ränder bei anderem Seitenverhältnis
var _field_bg: TextureRect
var _field_fill: TextureRect
var _menu_shot_t := 0
var _side_bg: ColorRect   # Rand neben dem Spielfeld; im Menü verdeckt


func _ready() -> void:
	# Hängt das Handy kurz, lieber kurz langsamer werden als viele Schritte nachholen
	Engine.max_physics_steps_per_frame = 3
	_parse_args()
	Save.test_mode = _autotest
	Sfx.muted = _autotest
	if _autotest:
		Save.data = Save.default_data()
		if _profile != "":
			Save.sim = true
			load("res://tests/balance_profiles.gd").apply(Save, _profile, level)
			if _squad != "":
				Save.data["squad"] = Array(_squad.split(","))
	_build_layout()
	if _autotest and mp:
		start_mp(level)
	elif _autotest:
		start_level(level)
	elif _menu_shot != "":
		show_menu()
	else:
		_warm_up()


## Setzt das Spieltempo (x1 oder x2). Die Physik bleibt bei 60 Schritten pro Spielsekunde,
## weniger Schritte lassen schnelle Kugeln durch die Wände der Kugelbahn rutschen.
func _apply_speed(t: int) -> void:
	if mp and state in ["battle", "cards", "paused"]:
		Engine.time_scale = float(MP_TEMPO_SCALE.get(t, MP_SPEED))
	else:
		Engine.time_scale = float(TEMPO_SCALE.get(t, BASE_SPEED * float(t)))


## Ladebildschirm: Jede Figur und jeder Effekt wird einmal unsichtbar dahinter gezeigt,
## damit das Handy die Grafik vorbereitet, bevor gespielt wird (verhindert Ruckler beim
## ersten Schuss, der ersten Explosion usw.).
func _warm_up() -> void:
	state = "loading"
	hud.visible = false
	Sfx.muted = true  # die Probeschüsse hinter dem Ladebildschirm bleiben still
	var screen := LoadingScreen.new()
	_set_screen(screen)
	var steps := [
		[0.1, "Wurmloch wird geöffnet …"],
		[0.35, "Crew bezieht Stellung …"],
		[0.55, "Schleimwesen werden gezählt …"],
		[0.75, "Energiezaun lädt …"],
		[0.9, "Energiekern lädt …"],
	]
	screen.set_progress(steps[0][0], steps[0][1])
	await _frames(20)
	battle.setup(1, ammo)
	screen.set_progress(steps[1][0], steps[1][1])
	for id in GameData.HERO_IDS:
		battle.add_hero(id)
		await _frames(4)
	screen.set_progress(steps[2][0], steps[2][1])
	var targets: Array[Enemy] = []
	var x := -3.5
	for kind in GameData.ENEMIES.keys():
		targets.append(battle.spawn_enemy(kind, Vector3(x, 0, -8.0)))
		x += 1.0
		await _frames(4)
	await _frames(15)
	screen.set_progress(steps[3][0], steps[3][1])
	var from := Vector3(0, 1.5, 1.5)
	for type in ["normal", "fire", "ice"]:
		battle.fire_bullet(from, targets[0], 0.0, true, type, 0, 30.0, 1.0)
		battle.fire_bullet(from, targets[1], 0.0, false, type, 0, 34.0, 0.75)
		battle.fire_rocket(from, targets[2], 0.0, false, type, 2.0)
		battle.fire_chain(from, targets[1], 0.0, false, type, 2)
		await _frames(6)
	Fx.flash(battle, Vector3(0, 1, -6), Color(1.0, 0.3, 0.9), 3.0, 0.4)
	Fx.burst(battle, Vector3(0, 1, -6), Color(0.4, 1.0, 0.5), 12, 4.0, 0.1)
	await _frames(40)
	screen.set_progress(steps[4][0], steps[4][1])
	plasma.active = true
	await _frames(40)
	screen.set_progress(1.0, "Bereit!")
	await _frames(25)
	plasma.reset()
	Sfx.muted = false
	Sfx.start_music()
	show_menu()
	print("LADEN_FERTIG")


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _parse_args() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg == "--autotest":
			_autotest = true
		elif arg == "--smoke":
			var smoke: Node = load("res://tests/menu_smoke.gd").new()
			smoke.set("main", self)
			add_child.call_deferred(smoke)
		elif arg == "--perf":
			var pp: Node = load("res://tests/perf_probe.gd").new()
			pp.set("main", self)
			add_child.call_deferred(pp)
		elif arg == "--ultcheck":
			var uc: Node = load("res://tests/ult_check.gd").new()
			uc.set("main", self)
			add_child.call_deferred(uc)
		elif arg.begins_with("--monster-show="):
			var ms: Node = load("res://tests/monster_show.gd").new()
			var spec := arg.get_slice("=", 1)
			ms.set("main", self)
			ms.set("kinds", spec.get_slice(":", 0).split(","))
			ms.set("out_dir", spec.get_slice(":", 1))
			add_child.call_deferred(ms)
		elif arg.begins_with("--fx-show="):
			var fs: Node = load("res://tests/fx_show.gd").new()
			var spec := arg.get_slice("=", 1)
			fs.set("main", self)
			fs.set("mode", spec.get_slice(":", 0))
			fs.set("out_dir", spec.get_slice(":", 1))
			if spec.get_slice_count(":") > 2:
				fs.set("start", float(spec.get_slice(":", 2)))
			add_child.call_deferred(fs)
		elif arg == "--fx-neu":
			Battle.fx_test = "bilder"
		elif arg == "--fx-bisher":
			Battle.fx_test = "bisher"
		elif arg == "--neue-monster":
			Models.test_new = true   # noch nicht freigegebene Gegnermodelle zeigen (Prüfbilder)
		elif arg == "--mp":
			mp = true
		elif arg == "--pull":
			_auto_pull = true
		elif arg.begins_with("--level="):
			level = clampi(int(arg.get_slice("=", 1)), 1, GameData.LEVEL_COUNT)
		elif arg.begins_with("--seed="):
			seed(int(arg.get_slice("=", 1)))
		elif arg.begins_with("--hpg="):
			GameData.HP_GROWTH = float(arg.get_slice("=", 1))
		elif arg.begins_with("--dpsg="):
			GameData.DPS_GROWTH = float(arg.get_slice("=", 1))
		elif arg.begins_with("--herog="):
			MetaData.HERO_GROWTH = float(arg.get_slice("=", 1))
		elif arg.begins_with("--hpstep="):
			GameData.HP_STEP = float(arg.get_slice("=", 1))
		elif arg.begins_with("--hplate="):
			GameData.HP_GROWTH_LATE = float(arg.get_slice("=", 1))
		elif arg.begins_with("--dpsstep="):
			GameData.DPS_STEP = float(arg.get_slice("=", 1))
		elif arg.begins_with("--dpslate="):
			GameData.DPS_GROWTH_LATE = float(arg.get_slice("=", 1))
		elif arg.begins_with("--bosshp="):
			GameData.HARD_BOSS_HP = float(arg.get_slice("=", 1))
		elif arg.begins_with("--mphp="):
			MpData.HP_WAVE = float(arg.get_slice("=", 1))
		elif arg.begins_with("--mptune="):
			MpData.HP_TUNE_FIXED = float(arg.get_slice("=", 1))
		elif arg.begins_with("--mpboss="):
			MpData.BOSS_TUNE_FIXED = float(arg.get_slice("=", 1))
		elif arg.begins_with("--profile="):
			_profile = arg.get_slice("=", 1)
		elif arg.begins_with("--pickshot="):
			_pick_shot = arg.get_slice("=", 1)
		elif arg.begins_with("--squad="):
			# nur mit --profile: feste Heldenauswahl für Prüfbilder, z. B. --squad=iska,fritzi
			_squad = arg.get_slice("=", 1)
		elif arg.begins_with("--menushot="):
			_menu_shot = arg.get_slice("=", 1)
		elif arg.begins_with("--shot="):
			_shot_path = arg.get_slice("=", 1)


func _build_layout() -> void:
	var theme := UiKit.make_theme()
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.theme = theme
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)
	var side_bg := ColorRect.new()
	_side_bg = side_bg
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
	_world_holder = world_holder
	world_holder.size_flags_vertical = Control.SIZE_EXPAND_FILL
	world_holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	column.add_child(world_holder)
	_field_fill = TextureRect.new()
	_field_fill.set_anchors_preset(Control.PRESET_FULL_RECT)
	_field_fill.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_field_fill.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	_field_fill.modulate = Color(0.45, 0.42, 0.6)
	_field_fill.mouse_filter = Control.MOUSE_FILTER_IGNORE
	world_holder.add_child(_field_fill)
	_field_bg = TextureRect.new()
	_field_bg.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_field_bg.stretch_mode = TextureRect.STRETCH_SCALE
	_field_bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	world_holder.add_child(_field_bg)
	var container := SubViewportContainer.new()
	_world_container = container
	container.stretch = true
	container.set_anchors_preset(Control.PRESET_FULL_RECT)
	container.mouse_filter = Control.MOUSE_FILTER_IGNORE
	world_holder.add_child(container)
	world_holder.resized.connect(_fit_world)
	var viewport := SubViewport.new()
	viewport.transparent_bg = true
	viewport.own_world_3d = true
	container.add_child(viewport)
	battle = Battle.new()
	viewport.add_child(battle)
	hud = BattleHud.new()
	hud.set_anchors_preset(Control.PRESET_FULL_RECT)
	hud.battle = battle
	world_holder.add_child(hud)

	# Plasma-Erzeuger und Energiekern (ersetzen die Kugelbahn): laufen ohne eigene Ansicht,
	# angezeigt werden sie in der Kampfanzeige (BattleHud)
	plasma = PlasmaCore.new()
	plasma.ammo = ammo
	add_child(plasma)
	hud.plasma = plasma

	var layer := CanvasLayer.new()
	layer.layer = 10
	layer.process_mode = Node.PROCESS_MODE_ALWAYS
	add_child(layer)
	_overlay = Control.new()
	_overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	_overlay.theme = theme
	_overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(_overlay)

	updater = Updater.new()
	add_child(updater)
	menu = MainMenu.new()
	menu.updater = updater
	menu.visible = false
	_overlay.add_child(menu)
	menu.play_requested.connect(start_level)
	menu.mp_requested.connect(func(m: MpMatch) -> void: start_mp(0, m))
	menu.quality_changed.connect(battle.apply_quality)

	get_viewport().size_changed.connect(_fit_column)
	_fit_column()

	battle.enemy_killed.connect(_on_enemy_killed)
	battle.wave_started.connect(func(w: int, total: int) -> void:
		hud.set_wave(level, w, total)
		hud.set_next_wave(battle.next_wave_text())
		if w > 1:
			Save.track("waves")
			# Nach jeder geschafften Welle eine Karte wählen (Mockup „Karte nach der Welle“)
			pending_levelups += 1
			_card_wave = w - 1
			_open_card_pick.call_deferred()
			var heal := float(bonus.get("heal", 0.0))
			if heal > 0.0:
				battle.repair_fence(heal, 0.0)
	)
	plasma.manual_pulled.connect(func() -> void:
		Save.track("pulls")
		battle.overdrive(OVERDRIVE_TIME)
		hud.show_banner("Energiekern!")
		Sfx.play("whoosh", 0.05))
	battle.fence_changed.connect(hud.set_fence)
	battle.damage_dealt.connect(hud.add_floater)
	battle.level_won.connect(_on_level_won)
	battle.level_lost.connect(_on_level_lost)
	hud.pause_pressed.connect(_on_pause)
	hud.booster_pressed.connect(_use_booster)
	hud.tempo_pressed.connect(_toggle_tempo)


## Hält das Spiel als Hochformat-Spalte in der Mitte, auch im breiten Fenster.
## Kampfbild auf den Rahmen der Anzeige legen (390 × 844, wie die Mockups): Bei gemaltem Schlachtfeld
## deckt das 3D-Bild genau das gemalte Bild ab, damit die Gegner auf der gemalten Brücke laufen.
func _fit_world() -> void:
	if _world_container == null or _world_holder == null:
		return
	var hs := _world_holder.size
	var on := battle != null and battle.field != ""
	var sc := minf(hs.x / MockView.W, hs.y / MockView.H)
	var frame := Rect2((hs - Vector2(MockView.W, MockView.H) * sc) * 0.5, Vector2(MockView.W, MockView.H) * sc)
	if not on:
		frame = Rect2(Vector2.ZERO, hs)
	_world_container.set_anchors_preset(Control.PRESET_TOP_LEFT)
	_world_container.position = frame.position
	_world_container.size = frame.size
	_field_bg.position = frame.position
	_field_bg.size = frame.size
	_field_bg.visible = on
	_field_fill.visible = on
	if hud:
		hud.world_frame = frame


func _set_field(id: String) -> void:
	battle.set_field(id)
	var tex := Battlefields.texture(id) if id != "" else null
	if id != "" and tex == null:
		battle.set_field("")
	_field_bg.texture = tex
	_field_fill.texture = tex
	_fit_world()


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


func _update_boosters(delta: float) -> void:
	for i in _boosters.size():
		var id := _boosters[i]
		var full := MetaData.booster_cd(id, Save.booster_level(id))
		_booster_cd[i] = maxf(0.0, _booster_cd[i] - delta)
		hud.set_booster_ready(i, 1.0 - _booster_cd[i] / full)


func _use_booster(i: int) -> void:
	if state != "battle" or i >= _boosters.size() or _booster_cd[i] > 0.0 or not battle.running:
		return
	var id := _boosters[i]
	var lvl := Save.booster_level(id)
	var power := MetaData.booster_power(lvl)
	match id:
		"luftangriff":
			battle.booster_air_strike(power * (1.0 + float(bonus.get("airstrike", 0.0))))
		"medipack":
			battle.repair_fence(0.25 * power * (1.0 + float(bonus.get("medipack", 0.0))), 0.0)
			battle.fence_heal_fx("medipack_heilung", [-2.8, 0.0, 2.8])
		"zeitlupe":
			battle.booster_slow(power)
		"kuppel":
			battle.booster_dome(power)
		"munition":
			ammo.add("normal", int(25 * power))
	_booster_cd[i] = MetaData.booster_cd(id, lvl) * (1.0 - float(bonus.get("booster_cd", 0.0)))
	Sfx.play("whoosh", 0.05)
	hud.show_banner(String(MetaData.BOOSTERS[id]["title"]) + "!")


## Antippen im Kampfbild: nächster Held mit bereiter Superfähigkeit löst sie aus.
func _unhandled_input(event: InputEvent) -> void:
	if state != "battle" or not (event is InputEventMouseButton):
		return
	var mb := event as InputEventMouseButton
	if not mb.pressed or mb.button_index != MOUSE_BUTTON_LEFT:
		return
	var local := mb.position - _world_container.global_position
	if not Rect2(Vector2.ZERO, _world_container.size).has_point(local):
		return
	var best: Hero = null
	var best_d := 110.0
	for h in battle.heroes:
		if not h.ult_ready():
			continue
		var p := battle.camera.unproject_position(h.global_position + Vector3(0, 1.2, 0))
		var dist := p.distance_to(local)
		if dist < best_d:
			best = h
			best_d = dist
	if best and best.activate_ult():
		hud.show_banner(Hero.ULTS[best.family()][0] + "!")
		get_viewport().set_input_as_handled()


## Automatische Grafikstufe: Kommt das Gerät im Kampf nicht mit (Median der Bildzeit über 2 s
## über 22 ms, also unter etwa 45 Bildern pro Sekunde), eine Stufe herunter (battle.apply_quality).
## Die ersten Sekunden nach dem Start zählen nicht (Laden, erste Effekte).
const PERF_LIMIT_MS := 22.0
const PERF_MAX_LEVEL := 3
var _perf_frames: PackedFloat32Array = []
var _perf_last := 0
var _perf_skip := 0.0


func _watch_performance(delta: float) -> void:
	var now := Time.get_ticks_usec()
	var ms := (now - _perf_last) / 1000.0
	_perf_last = now
	if state != "battle" or _autotest or get_tree().paused:
		_perf_frames.clear()
		_perf_skip = 3.0
		return
	if _perf_skip > 0.0:
		_perf_skip -= delta / maxf(0.01, Engine.time_scale)
		return
	_perf_frames.append(ms)
	if _perf_frames.size() < 120:
		return
	var sorted := _perf_frames.duplicate()
	sorted.sort()
	var median: float = sorted[sorted.size() / 2]
	_perf_frames.clear()
	var lvl := int(Save.data.get("perf_level", 0))
	if median > PERF_LIMIT_MS and lvl < PERF_MAX_LEVEL and Save.data.get("quality", "hoch") == "hoch":
		Save.data["perf_level"] = lvl + 1
		Save.save_game()
		battle.apply_quality()
		_perf_skip = 1.0   # Umstellen selbst kostet kurz


func _process(delta: float) -> void:
	# Das Menü liegt bildschirmfüllend darüber: den Rand darunter nicht zeichnen
	_side_bg.visible = not menu.visible
	_watch_performance(delta)
	if state == "battle":
		_update_boosters(delta)
		if mp and mp_match:
			_update_mp(delta)
	# Leistungsmessung für Tests im Browser (erscheint in der Browser-Konsole)
	_perf_t += delta / maxf(0.01, Engine.time_scale)
	if _perf_t >= 2.0 and state == "battle":
		_perf_t = 0.0
		print("PERF fps=%d tempo=%d gegner=%d kugeln=%d knoten=%d physik_ms=%.1f bild_ms=%.1f" % [
			Engine.get_frames_per_second(), tempo, battle.enemies.size(), plasma.ball_count(),
			Performance.get_monitor(Performance.OBJECT_NODE_COUNT),
			Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS) * 1000.0,
			Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0])
	if _menu_shot != "" and state == "menu":
		_menu_shot_t += 1
		var parts := _menu_shot.split(",")
		if _menu_shot_t == 5 and parts.size() > 1:
			if parts[1] == "feier":
				menu.celebrate("gold", "+150 Gold")
			else:
				if parts.size() > 2 and parts[2] == "lager-voll":
					# Testzustand fürs Bild: alle Champions, Gebäude 1–15 gebaut, Lager voll
					Save.data["unlocked"] = GameData.HERO_IDS.duplicate()
					Save.data["max_level"] = 20
					for i in range(1, 16):
						var bid := "%02d" % i
						if not BaseData.by_champion(bid):
							Save.base()[bid] = {"level": 2, "stock": 999.0, "time": Time.get_unix_time_from_system()}
					menu.show_tab(parts[1])
				elif parts.size() > 2 and parts[2].begins_with("bau:"):
					# Gebäudefenster fürs Bild: bau:<id>, gebaut mit halbvollem Lager (bau:<id>:leer = noch nicht gebaut)
					Save.data["max_level"] = 20
					var bid2 := parts[2].get_slice(":", 1)
					if parts[2].get_slice_count(":") < 3:
						Save.base()[bid2] = {"level": 2, "stock": 3.0, "time": Time.get_unix_time_from_system()}
					menu.show_tab(parts[1])
					menu.open_building(bid2)
				elif parts.size() > 2 and parts[2].begins_with("held:"):
					menu.show_tab(parts[1])
					HeroLockBoard.hero = parts[2].get_slice(":", 1)
					menu.open_board("Helden-Meldung.dc.html")
				else:
					if parts.size() > 2:
						menu.sub_tab[parts[1]] = parts[2]
					menu.show_tab(parts[1])
		if _menu_shot_t == (25 if parts.size() > 1 and parts[1] == "feier" else 90):
			get_viewport().get_texture().get_image().save_png(parts[0])
			print("BILD gespeichert: ", parts[0])
			get_tree().quit()
	if _shot_path != "" and state == "battle" and battle.elapsed > 8.0:
		get_viewport().get_texture().get_image().save_png(_shot_path)
		print("BILD gespeichert: ", _shot_path)
		get_tree().quit()
	if _autotest and state == "battle":
		if battle.elapsed > 900.0:
			_finish_autotest("timeout")
		# Booster setzt der Test immer ein, sobald sie bereit sind; den Hebel nur mit --pull
		_auto_pull_t -= delta
		if _auto_pull_t <= 0.0:
			_auto_pull_t = 1.0
			if _auto_pull:
				plasma.try_manual_pull()
			for i in _boosters.size():
				_use_booster(i)
			for h in battle.heroes:
				h.activate_ult()


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
	mp = false
	get_tree().paused = false
	_apply_speed(1)
	battle.clear()
	plasma.reset()
	hud.visible = false
	_set_screen(null)
	_column.visible = false
	menu.visible = true
	# Zurück im Menü: der Abenteuer-Pfad zeigt immer das aktuelle (höchste freie) Level, nicht das zuletzt gewählte
	menu.selected_level = Save.max_level()
	menu.refresh()


## Alter Startbildschirm (nicht mehr verwendet).
func _old_menu() -> void:
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
		+ "Die Munition ist Plasma: Der Vorrat unten füllt sich von selbst, jeder Held lädt sein Magazin daraus nach. "
		+ "Ist der Energiekern in der Mitte voll, tippe ihn an: Dann gibt es einen Schwall Plasma und alle feuern doppelt so schnell.\n\n"
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
		if n > Save.max_level():
			b.disabled = true
			b.text = "Level %d · gesperrt" % n
		grid.add_child(b)
	v.add_child(UiKit.label("Grafik: Platzhalter aus einfachen Formen", 18, UiKit.C_MUTED))
	_set_screen(s)


## Multiplayer starten: Station nach dem Fortschritt im Abenteuer, drei Kommandanten als Gegner.
## found: schon gefundene Gegner (Gegnersuche); leer = neue würfeln
func start_mp(station := 0, found: MpMatch = null) -> void:
	var lvl := station if station > 0 else (found.level if found else MpData.station_level(Save.max_level()))
	_start(lvl, false, true, found)


func start_level(n: int, hard_mode := false) -> void:
	_start(n, hard_mode, false)


func _start(n: int, hard_mode: bool, multi: bool, found: MpMatch = null) -> void:
	if not _autotest and not Save.use_energy(MetaData.ENERGY_COST):
		show_menu()
		return
	mp = multi
	mp_match = found
	level = n
	hard = hard_mode
	state = "hero_select"
	menu.visible = false
	_column.visible = true
	get_tree().paused = false
	tempo = 1
	_apply_speed(1)
	bonus = Save.battle_bonus()
	ammo.reset(START_CAP + int(bonus["cap"]), START_AMMO + int(bonus["start_ammo"]))
	_xp_carry = 0.0
	xp = 0
	levelups = 0
	xp_needed = GameData.xp_needed(0)
	pending_levelups = 0
	card_levels.clear()
	cards_taken.clear()
	if mp:
		_mp_seed = mp_match.match_seed if mp_match else randi()
		battle.setup_mp(n, ammo, _mp_seed)
	else:
		battle.setup(n, ammo)
	_set_field(Battlefields.for_mode("mp", n) if mp else Battlefields.for_level(n))
	battle.hp_scale = 1.5 if hard else 1.0
	battle.bonus_crit = float(bonus["crit"])
	battle.bonus_reload = float(bonus["reload"])
	battle.heavy_bonus = float(bonus.get("heavy_dmg", 0.0))
	battle.frost_bonus = float(bonus.get("frost", 0.0))
	battle.burn_bonus = float(bonus.get("burn", 0.0))
	battle.hero_damage = {}
	for id in GameData.HERO_IDS:
		battle.hero_damage[id] = MetaData.hero_damage_mult(Save.hero_level(id)) * (1.0 + float(bonus["damage"]))
	battle.fence_max *= 1.0 + float(bonus["shield"])
	battle.fence_hp = battle.fence_max
	plasma.reset()
	plasma.lucky = float(bonus["lucky"])
	plasma.manual_cd_bonus = float(bonus["lever"])
	plasma.manual_extra = int(bonus["lever_balls"])
	plasma.rate_bonus = float(bonus["rate"])
	plasma.update_interval()
	plasma.base_count_bonus = int(bonus["count"])
	plasma.balls_per_launch += int(bonus["count"])
	for g in bonus["gates"]:
		plasma.add_gate(g)
	hud.visible = true
	_boosters = Save.booster_slots()
	_booster_cd.clear()
	for id in _boosters:
		# Zu Beginn sind Booster halb geladen
		_booster_cd.append(MetaData.booster_cd(id, Save.booster_level(id)) * 0.5)
	hud.reset(level, battle.total_waves)
	hud.set_mp(mp)
	hud.show_banner("Multiplayer · Station %d" % level if mp else "%d · %s" % [level, GameData.level_name(level)])
	hud.set_boosters(_boosters)
	hud.set_next_wave(battle.next_wave_text())
	hud.set_xp(0, xp_needed)
	hud.set_fence(battle.fence_hp, battle.fence_max)
	var options: Array = Save.squad()
	options.shuffle()
	if options.size() > 3:
		options.resize(3)
	if _pick_shot != "":
		# Prüfbild der Heldenauswahl: --pickshot=pfad.png[,held1,held2,held3]
		var parts := _pick_shot.split(",")
		if parts.size() > 1:
			options = Array(parts.slice(1))
		_show_hero_picker(options)
		get_tree().create_timer(1.5).timeout.connect(func() -> void:
			get_viewport().get_texture().get_image().save_png(parts[0])
			print("BILD gespeichert: ", parts[0])
			get_tree().quit())
		return
	if _autotest:
		_set_screen(null)
		_on_hero_picked(options[0])
		return
	_show_hero_picker(options)


func _show_hero_picker(options: Array) -> void:
	# Heldenauswahl nach dem freigegebenen Mockup (screens/hero_pick.gd); der Kampf bleibt dahinter sichtbar
	var s := _full_screen()
	s.add_child(UiKit.dim(0.2))
	var board := HeroPickBoard.new(options)
	board.picked.connect(_on_hero_picked)
	s.add_child(board)
	_set_screen(s)


func _on_hero_picked(id: String) -> void:
	_set_screen(null)
	battle.add_hero(id)
	cards_taken.append("start:" + id)
	state = "battle"
	if mp:
		if mp_match == null:
			mp_match = MpMatch.new(level, Save.trophies(), _mp_seed, id)
		_mp_curve.clear()
		_apply_speed(1)
	if _autotest:
		_apply_speed(1)
	battle.start()
	plasma.active = true


# --- Erfahrung und Karten ---------------------------------------------------

func _on_enemy_killed(e: Enemy, gained: int) -> void:
	Save.track("kills")
	plasma.on_kill(e.is_boss())
	if e.is_boss():
		Save.track("boss")
	_xp_carry += gained * (1.0 + float(bonus.get("xp", 0.0)))
	var whole := int(floor(_xp_carry))
	_xp_carry -= whole
	xp += whole
	while xp >= xp_needed:
		xp -= xp_needed
		levelups += 1
		xp_needed = GameData.xp_needed(levelups)
	hud.set_xp(xp, xp_needed)


func _open_card_pick() -> void:
	if state != "battle" or pending_levelups <= 0 or not battle.running:
		return
	# Prime: 4 statt 3 Karten zur Auswahl
	var cards := _roll_cards(4 if Save.has_prime() else 3)
	if cards.is_empty():
		pending_levelups = 0
		return
	state = "cards"
	get_tree().paused = true
	if _autotest:
		_on_card_picked(_auto_choose(cards))
		return
	Sfx.play("levelup", 0.0)
	var pick := CardPick.new(cards, _card_wave)
	pick.picked.connect(_on_card_picked)
	_set_screen(pick)


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
		elif key.ends_with(":ult"):
			score = 6.5 if int(c["stars"]) == 0 else 4.0
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
	Save.track("cards")
	cards_taken.append(card["key"])
	pending_levelups -= 1
	get_tree().paused = false
	state = "battle"
	if pending_levelups > 0:
		_open_card_pick.call_deferred()


func _roll_cards(n: int) -> Array:
	var pool: Array = []
	if battle.heroes.size() < Battle.MAX_HEROES:
		for id in Save.squad():
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
		"title": d["name"], "desc": "%s mit %s.\n%s\n%s\n+10 Munition" % [d["role"], d["weapon"], d["blurb"], GameData.hero_type_text(id)],
		"stars": 0, "max": 1, "emblem": String(d["name"]).left(1), "hero_id": id,
		"weight": 4.0 if battle.heroes.size() < 2 else 2.2,
		"apply": _apply_add_hero.bind(id),
	}


func _apply_add_hero(id: String) -> void:
	# Höchstens drei Helden gleichzeitig auf dem Feld
	if battle.heroes.size() >= Battle.MAX_HEROES:
		return
	battle.add_hero(id, true)
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
		"cryo": ["Frostsplitter", "Der Frost-Strahl springt auf 1 Gegner mehr über", 3],
		"shotgun": ["Mehr Schrot", "+1 Kugel pro Schuss", 3],
		"sniper": ["Durchschlag", "Die Kugel durchschlägt 1 Gegner mehr", 3],
		"flamer": ["Breitere Flamme", "Flammenbereich +20 %", 3],
		"beam": ["Längerer Atem", "Der Atem durchschlägt 1 Gegner mehr", 3],
		"drone": ["Feinmechanik", "Repariert 50 % mehr Mauer je Schuss", 3],
		"cannon": ["Mehr Wucht", "Stößt 25 % weiter zurück", 3],
		"gravity": ["Größeres Feld", "Schwerkraftfeld +20 %", 3],
	}
	var sp: Array = special[h.family()]
	stats.append(["special", sp[0], sp[1], sp[2]])
	var ult: Array = Hero.ULTS[h.family()]
	var ult_desc := "SUPERFÄHIGKEIT: %s\nTippe danach auf %s, um sie auszulösen." % [ult[1], String(d["name"]).split(" ")[0]]
	if h.ult_level() > 0:
		ult_desc = "%s stärker, länger und schneller wieder bereit." % ult[0]
	stats.append(["ult", ult[0], ult_desc, Hero.ULT_MAX])
	for s in stats:
		var mod: String = s[0]
		list.append({
			"key": "%s:%s" % [h.id, mod], "kind": "hero", "target": d["name"], "color": d["color"],
			"title": s[1], "desc": s[2], "stars": int(h.mods[mod]), "max": s[3],
			"emblem": "★" if mod == "ult" else String(d["name"]).left(1),
			"weight": (1.5 if h.ult_level() == 0 else 0.9) if mod == "ult" else (1.2 if mod == "special" else 1.0),
			"apply": _apply_hero_mod.bind(h, mod),
		})
	return list


func _apply_hero_mod(h: Hero, mod: String) -> void:
	h.mods[mod] = int(h.mods[mod]) + 1
	if mod == "ult" and h.mods[mod] == 1:
		hud.show_banner("Tippe auf %s: %s!" % [String(h.data["name"]).split(" ")[0], Hero.ULTS[h.family()][0]])


func _machine_cards() -> Array:
	var free := plasma.free_slots() > 0
	var gates := [
		["x2", "Plasma-Verdichter", "Der Erzeuger liefert dauerhaft etwa 12 % mehr Plasma.", 3],
		["plus3", "Großer Verdichter", "Der Erzeuger liefert dauerhaft etwa 20 % mehr Plasma.", 2],
		["fire", "Feuer-Plasma", "Ein Teil des Plasmas wird zu Brandmunition: Getroffene Gegner brennen.", 1],
		["ice", "Eis-Plasma", "Ein Teil des Plasmas wird zu Frostmunition: Getroffene Gegner werden langsamer.", 1],
	]
	var list: Array = []
	for g in gates:
		var type: String = g[0]
		var count := 0
		for t in plasma._gate_types:
			if t == type:
				count += 1
		list.append({
			"key": "gate:" + type, "kind": "machine", "target": "Plasma", "color": UiKit.C_MACHINE,
			"title": g[1], "desc": g[2], "stars": count, "max": g[3], "available": free,
			"emblem": PlasmaCore.GATE_INFO[type]["label"], "weight": 1.3,
			"apply": func() -> void: plasma.add_gate(type),
		})
	list.append({
		"key": "machine:rate", "kind": "machine", "target": "Plasma", "color": UiKit.C_MACHINE,
		"title": "Schneller laden", "desc": "Der Plasma-Vorrat füllt sich 25 % schneller.",
		"stars": plasma.rate_level, "max": 4, "emblem": "»", "weight": 1.2,
		"apply": func() -> void: plasma.upgrade_rate(),
	})
	list.append({
		"key": "machine:count", "kind": "machine", "target": "Plasma", "color": UiKit.C_MACHINE,
		"title": "Mehr Plasma", "desc": "+1 Plasma pro Ladung.",
		"stars": plasma.balls_per_launch - PlasmaCore.BASE_COUNT - plasma.base_count_bonus, "max": 3, "emblem": "+1", "weight": 1.2,
		"apply": func() -> void: plasma.upgrade_count(),
	})
	list.append({
		"key": "machine:tank", "kind": "machine", "target": "Plasma", "color": UiKit.C_MACHINE,
		"title": "Größerer Tank", "desc": "Plasma-Vorrat +30, dazu sofort 15 Plasma.",
		"stars": int(card_levels.get("machine:tank", 0)), "max": 3, "emblem": "+30", "weight": 0.8,
		"apply": _apply_tank,
	})
	list.append({
		"key": "plasma:mag", "kind": "machine", "target": "Magazin", "color": UiKit.C_MACHINE,
		"title": "+2 Schuss", "desc": "+2 Schuss im Magazin für alle Helden.",
		"stars": int(card_levels.get("plasma:mag", 0)), "max": 3, "emblem": "+2", "weight": 1.1,
		"apply": func() -> void: battle.team_mag += 2,
	})
	list.append({
		"key": "plasma:reload", "kind": "machine", "target": "Nachladen", "color": UiKit.C_MACHINE,
		"title": "−20 %", "desc": "Alle Helden laden 20 % schneller nach.",
		"stars": int(card_levels.get("plasma:reload", 0)), "max": 3, "emblem": "↻", "weight": 1.1,
		"apply": func() -> void: battle.bonus_reload += 0.25,
	})
	list.append({
		"key": "plasma:core", "kind": "machine", "target": "Kern", "color": UiKit.C_MACHINE,
		"title": "+30 %", "desc": "Der Energiekern lädt 30 % schneller auf.",
		"stars": int(card_levels.get("plasma:core", 0)), "max": 3, "emblem": "⚡", "weight": 1.0,
		"apply": func() -> void: plasma.core_speed *= 1.3,
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
		"apply": func() -> void: battle.repair_fence(0.35 * (1.0 + float(bonus.get("repair_card", 0.0))), 0.1),
	}


func _card_button(card: Dictionary, on_pick: Callable) -> Control:
	var col: Color = card["color"]
	# Die Karte wächst mit ihrem Inhalt, damit Bild und Text immer im Rahmen bleiben
	var b := PanelContainer.new()
	b.custom_minimum_size = Vector2(214, 0)
	b.size_flags_vertical = Control.SIZE_FILL
	var normal := UiKit.box(Color(0.1, 0.12, 0.22), 18, 3, col)
	normal.content_margin_left = 10
	normal.content_margin_right = 10
	normal.content_margin_top = 10
	normal.content_margin_bottom = 14
	var hover := normal.duplicate() as StyleBoxFlat
	hover.bg_color = Color(0.14, 0.17, 0.3)
	b.add_theme_stylebox_override("panel", normal)
	b.mouse_filter = Control.MOUSE_FILTER_STOP
	b.mouse_entered.connect(func() -> void: b.add_theme_stylebox_override("panel", hover))
	b.mouse_exited.connect(func() -> void: b.add_theme_stylebox_override("panel", normal))
	b.gui_input.connect(func(e: InputEvent) -> void:
		if e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT:
			b.accept_event()
			on_pick.call(card))
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 6)
	v.mouse_filter = Control.MOUSE_FILTER_IGNORE
	b.add_child(v)
	var head := PanelContainer.new()
	head.add_theme_stylebox_override("panel", UiKit.box(col, 10))
	head.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var head_label := UiKit.label(card["target"], 18, Color(0.08, 0.08, 0.12))
	head_label.add_theme_constant_override("outline_size", 0)
	head.add_child(head_label)
	v.add_child(head)
	if card.has("hero_id"):
		var portrait := HeroPortrait.make(String(card["hero_id"]), 140)
		portrait.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
		v.add_child(portrait)
	else:
		v.add_child(Emblem.new(col, String(card.get("emblem", ""))))
	v.add_child(_card_text(card["title"], 26, UiKit.C_GOLD))
	if card.has("role"):
		v.add_child(_card_text(card["role"], 16, UiKit.C_MUTED))
	var desc := _card_text(card["desc"], 17, UiKit.C_TEXT)
	desc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(desc)
	if card.has("note"):
		v.add_child(_card_text(card["note"], 15, col.lightened(0.35)))
	if int(card["max"]) > 1:
		v.add_child(UiKit.StarRow.new(int(card["stars"]), int(card["max"])))
	return b


## Text auf einer Karte: bricht nur zwischen Wörtern um, nie mitten im Wort
func _card_text(text: String, font_size: int, color: Color) -> Label:
	var l := UiKit.wrap_label(text, font_size, color)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD
	l.custom_minimum_size.x = 190
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


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

## Multiplayer: Computergegner weiterrechnen, Rangliste und Restzeit in der Kampfanzeige
func _update_mp(delta: float) -> void:
	mp_match.step(battle.elapsed)
	while _mp_curve.size() < int(battle.elapsed / 10.0):
		_mp_curve.append(battle.kills)
	_mp_hud_t -= delta
	if _mp_hud_t <= 0.0:
		_mp_hud_t = 0.25
		hud.set_mp_state(mp_match.live(_mp_player(false)), MpData.MATCH_TIME - battle.elapsed, battle.wave)


func _mp_player(out: bool) -> Dictionary:
	var hero: String = battle.heroes[0].id if not battle.heroes.is_empty() else "dusty"
	return {"name": "DU", "hero": hero, "kills": battle.kills, "bosses": battle.bosses,
		"secs": minf(battle.elapsed, MpData.MATCH_TIME), "out": out, "me": true, "trophies": Save.trophies()}


func _toggle_tempo() -> void:
	# x3 und der Tempo-Knopf im Multiplayer nur für die Testphase
	tempo = tempo % 3 + 1
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
	if mp:
		# Im Multiplayer gibt es keinen Neustart: Aufgeben zählt wie das Fallen der Station
		v.add_child(UiKit.secondary(UiKit.button("Aufgeben", func() -> void:
			_set_screen(null)
			get_tree().paused = false
			state = "battle"
			battle.running = false
			plasma.active = false
			_finish_mp(true))))
	else:
		v.add_child(UiKit.secondary(UiKit.button("Level neu starten", func() -> void: start_level(level, hard))))
		v.add_child(UiKit.secondary(UiKit.button("Zum Menü", show_menu)))
	_set_screen(s)


func _resume() -> void:
	_set_screen(null)
	state = "battle"
	get_tree().paused = false


func _on_level_won() -> void:
	plasma.active = false
	if mp:
		_finish_mp(false)
		return
	if _autotest:
		_finish_autotest("win")
		return
	state = "result"
	_apply_speed(1)
	_show_result(true, _grant_rewards(true))


func _on_level_lost() -> void:
	plasma.active = false
	if mp:
		_finish_mp(true)
		return
	if _autotest:
		_finish_autotest("lost")
		return
	state = "result"
	_apply_speed(1)
	_show_result(false, _grant_rewards(false))


## Belohnungsfenster nach dem Kampf (Mockups „Belohnung nach dem Sieg / der Niederlage“)
func _show_result(won: bool, rewards: Dictionary) -> void:
	Sfx.play("win" if won else "lose", 0.0)
	var info := rewards.duplicate()
	info["level"] = level
	info["world"] = GameData.world_name(level)
	info["boss"] = GameData.is_boss_level(level)
	info["kills"] = battle.kills
	info["secs"] = int(battle.elapsed)
	info["shield"] = battle.fence_hp / maxf(1.0, battle.fence_max)
	info["wave"] = battle.wave
	info["waves"] = battle.total_waves
	info["last_level"] = level >= GameData.LEVEL_COUNT
	# Kampfanzeige ausblenden, das Fenster liegt über dem abgedunkelten Schlachtfeld
	hud.visible = false
	var r := ResultScreen.new(won, info)
	r.next_pressed.connect(func() -> void: start_level(level + 1, hard))
	r.retry_pressed.connect(func() -> void: start_level(level, hard))
	r.menu_pressed.connect(show_menu)
	r.heroes_pressed.connect(func() -> void:
		show_menu()
		menu.show_tab("sammlung"))
	_set_screen(r)


## Multiplayer zu Ende (out = Station ist gefallen): werten, Pokale und Belohnung, Ergebnis zeigen.
func _finish_mp(out: bool) -> void:
	_mp_curve.append(battle.kills)
	var standings := mp_match.finish(_mp_player(out))
	var place := 4
	for e in standings:
		if e.get("me", false):
			place = int(e["place"])
	if _autotest:
		var me: Dictionary = {}
		for e in standings:
			if e.get("me", false):
				me = e
		var others: Array[String] = []
		for e in standings:
			if not e.get("me", false):
				others.append("%d/%d/%d" % [int(e["kills"]), int(e["secs"]), int(e["points"])])
		print("MPTEST level=%d place=%d kills=%d bosses=%d secs=%.0f out=%s points=%d curve=%s heroes=%d bots=%s" % [
			level, place, battle.kills, battle.bosses, battle.elapsed, str(out), int(me.get("points", 0)),
			",".join(PackedStringArray(_mp_curve.map(func(k: int) -> String: return str(k)))), battle.heroes.size(),
			",".join(PackedStringArray(others))])
		get_tree().quit()
		return
	state = "result"
	var delta := Save.mp_record(place, standings)
	var rewards := _grant_mp_rewards(place)
	rewards["delta"] = delta
	rewards["place"] = place
	rewards["standings"] = standings
	rewards["trophies"] = Save.trophies()
	mp = false
	_apply_speed(1)
	Sfx.play("win" if place <= 2 else "lose", 0.0)
	hud.visible = false
	var r := MpResultScreen.new(rewards)
	r.again_pressed.connect(func() -> void: menu.open_mp_search())
	r.ranking_pressed.connect(func() -> void:
		show_menu()
		menu.open_board("Rangliste.dc.html"))
	r.menu_pressed.connect(show_menu)
	_set_screen(r)


## Belohnung nach Platz (MpData): Gold, Heldenkarten für die Helden im Kampf, Pass-Punkte
func _grant_mp_rewards(place: int) -> Dictionary:
	var i := clampi(place, 1, 4) - 1
	var mult := 1.0 + float(bonus.get("gold", 0.0))
	var gold := int(round(MetaData.win_gold(level) * float(MpData.GOLD_SHARE[i]) * mult))
	Save.data["gold"] = Save.gold() + gold
	var pass_pts := int(MpData.PASS_POINTS[i]) + int(round(float(bonus.get("pass_bonus", 0.0))))
	var out := {"gold": gold, "pass": pass_pts, "cards": []}
	for h in battle.heroes:
		var n := int(round(MetaData.win_cards(level) * float(MpData.CARD_SHARE[i]) * (1.0 + float(bonus.get("cards_bonus", 0.0)))))
		Save.add_hero_cards(h.id, n)
		out["cards"].append({"hero": h.id, "amount": n})
	Save.add_pass_points(pass_pts)
	if place == 1:
		Save.track("wins")
	Save.save_game()
	return out


func _finish_autotest(result: String) -> void:
	var names: Array[String] = []
	for h in battle.heroes:
		names.append(h.id)
	print("AUTOTEST level=%d result=%s time=%.0f wave=%d/%d kills=%d fence=%d/%d wait=%.2f fill=%.2f full=%.2f collected=%d heroes=%s balls=%d ammo=%d cards=%s" % [
		level, result, battle.elapsed, battle.wave, battle.total_waves, battle.kills,
		int(battle.fence_hp), int(battle.fence_max), battle.ammo_wait_ratio(), battle.fill_sum / maxf(1.0, battle.elapsed), battle.full_time / maxf(1.0, battle.elapsed), plasma.collected_total,
		",".join(PackedStringArray(names)), plasma.ball_count(), ammo.total(),
		",".join(PackedStringArray(cards_taken))])
	print("   plasma: ", plasma.stats)
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



# --- Belohnungen nach dem Kampf ------------------------------------------------

## Vergibt Belohnungen und gibt die Werte für das Belohnungsfenster zurück.
func _grant_rewards(won: bool) -> Dictionary:
	var mult := (1.5 if hard else 1.0) * (1.0 + float(bonus.get("gold", 0.0)))
	var out := {"gold": 0, "stars": 0, "pass": 0, "cards": []}
	# Abgestimmt mit scripts/economy-sim.py: ohne Käufe reicht das Gold für die Heldenstufen,
	# von denen die Schwierigkeitskurve ausgeht. Bei Niederlage gibt es einen Trostpreis.
	var gold := int(round((battle.kills * 2 + (MetaData.win_gold(level) if won else MetaData.LOSS_GOLD)) * mult))
	Save.data["gold"] = Save.gold() + gold
	out["gold"] = gold
	for h in battle.heroes:
		var n := int(round((MetaData.win_cards(level) if won else MetaData.win_cards(level) / 2) * (1.0 + float(bonus.get("cards_bonus", 0.0)))))
		Save.add_hero_cards(h.id, n)
		out["cards"].append({"hero": h.id, "amount": n})
	if won:
		var first := Save.level_won(level, hard)
		var stars := 3 if first else 1
		Save.data["stars"] = Save.stars() + stars
		out["stars"] = stars
		Save.track("wins")
		var pass_pts := MetaData.PASS_WIN_POINTS + int(round(float(bonus.get("pass_bonus", 0.0))))
		Save.add_pass_points(pass_pts)
		out["pass"] = pass_pts
	Save.save_game()
	return out
