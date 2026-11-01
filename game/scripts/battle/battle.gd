class_name Battle
extends Node3D
## Das Schlachtfeld in 3D: Stationsdeck, Energiezaun, Wurmloch, Helden, Gegner und Wellen.

signal enemy_killed(enemy: Enemy, xp: int)
signal wave_started(wave: int, total: int)
signal fence_changed(hp: float, max_hp: float)
signal damage_dealt(pos: Vector3, amount: float, crit: bool)
signal level_won
signal level_lost

const FENCE_Z := 0.0
const SPAWN_Z := -27.0
const HERO_Z := 3.3
const MAX_HEROES := 4
const DECK_HALF_W := 4.7

var level := 1
var ammo: AmmoStore
## Energiekern entladen: so viele Sekunden feuern alle Helden doppelt so schnell
var overdrive_left := 0.0
## Karte „+2 Schuss“: zusätzliche Schüsse im Magazin für alle Helden
var team_mag := 0
var camera: Camera3D
var enemies: Array[Enemy] = []
var heroes: Array[Hero] = []
var fence_hp := 1000.0
var fence_max := 1000.0
var running := false
var wave := 0
var total_waves := 0
var kills := 0
var elapsed := 0.0
## Boni aus Spielstand und Schwierigkeit (setzt main.gd beim Levelstart)
var hp_scale := 1.0
var bonus_crit := 0.0
var bonus_reload := 0.0
var hero_damage := {}
## Schadensbonus für alle Helden durch dazugerufene Verstärkungs-Helden.
var team_aura := 0.0
## Für Auswertungen: Heldensekunden ohne Munition und Heldensekunden insgesamt.
var hero_wait_time := 0.0
var hero_time := 0.0
## Für Auswertungen: mittlere Füllung des Munitionsspeichers und Zeit mit vollem Speicher
var fill_sum := 0.0
var full_time := 0.0

var _spawn_queue: Array[String] = []
## Alle Wellen des Levels, im Voraus gewürfelt (für die Vorschau).
var _plan: Array = []
var _spawn_timer := 0.0
var _wave_timer := 0.0
var _shake := 0.0
var _cam_base := Transform3D.IDENTITY
var _fence_mat: ShaderMaterial
var _fence_flash := 0.0
var _wormhole_mat: ShaderMaterial
var _pulse := 0.0
var _wormhole_ring: Node3D
var _asteroids: Array[Node3D] = []
var _target_cache: Enemy
var _flame_tick := 0
var _env: Environment
var _rim: OmniLight3D
var _sun: DirectionalLight3D
var _target_frame := -1


func _ready() -> void:
	_build_world()
	apply_quality()


## Farben des Wurmlochs und Licht passend zur Welt.
func _apply_world() -> void:
	var w: Dictionary = GameData.WORLDS[GameData.world_of(level)]
	if _wormhole_mat:
		_wormhole_mat.set_shader_parameter("c1", w["c1"])
		_wormhole_mat.set_shader_parameter("c2", w["c2"])
	if _rim:
		_rim.light_color = w["rim"]


## Grafikstufe aus den Einstellungen: Hoch = Leuchten und Schatten, Sparsam = ohne.
func apply_quality() -> void:
	var high: bool = Save.data.get("quality", "hoch") == "hoch"
	if _env:
		_env.glow_enabled = high
	if _sun:
		_sun.shadow_enabled = high


# --- Ablauf ----------------------------------------------------------------

func setup(level_: int, ammo_: AmmoStore) -> void:
	clear()
	level = level_
	ammo = ammo_
	fence_max = GameData.fence_base(level)
	fence_hp = fence_max
	total_waves = GameData.waves_in_level(level)
	_apply_world()
	_plan.clear()
	for w in range(1, total_waves + 1):
		_plan.append(GameData.wave_spawns(level, w))
	wave = 0
	kills = 0
	overdrive_left = 0.0
	team_mag = 0
	elapsed = 0.0
	hero_wait_time = 0.0
	hero_time = 0.0
	fill_sum = 0.0
	full_time = 0.0
	running = false
	fence_changed.emit(fence_hp, fence_max)


func clear() -> void:
	running = false
	for e in enemies:
		if is_instance_valid(e):
			e.queue_free()
	enemies.clear()
	for h in heroes:
		if is_instance_valid(h):
			h.queue_free()
	heroes.clear()
	for c in get_children():
		if c is Projectile or c is CPUParticles3D:
			c.queue_free()
	_spawn_queue.clear()


func start() -> void:
	running = true
	_next_wave()


## joined: per Karte im Kampf dazugerufen (nicht der erste Held).
func add_hero(id: String, joined := false) -> Hero:
	var h := Hero.new()
	add_child(h)
	h.position = Vector3(0, 0, HERO_Z)
	h.reinforced = joined and GameData.HERO_TYPE.get(id, "start") == "verstaerkung"
	if h.reinforced:
		team_aura += GameData.TEAM_AURA
	h.setup(id, self)
	heroes.append(h)
	_layout_heroes(true)
	Fx.flash(self, h.global_position + Vector3(0, 0.8, 0), Color(0.3, 0.9, 1.0), 1.4, 0.35)
	Fx.burst(self, h.global_position + Vector3(0, 0.6, 0), Color(0.4, 0.95, 1.0), 20, 4.0, 0.08)
	return h


func has_hero(id: String) -> bool:
	for h in heroes:
		if h.id == id:
			return true
	return false


func _layout_heroes(snap_new: bool) -> void:
	var n := heroes.size()
	var spacing := 3.4
	for i in n:
		var x := (i - (n - 1) * 0.5) * spacing
		heroes[i].slide_to(x)
		if snap_new and i == n - 1:
			heroes[i].position.x = x


func _process(delta: float) -> void:
	_animate_world(delta)
	if not running:
		return
	elapsed += delta
	shield_guard = maxf(0.0, shield_guard - delta)
	overdrive_left = maxf(0.0, overdrive_left - delta)
	if ammo:
		var ratio := float(ammo.total()) / maxf(1.0, ammo.cap)
		fill_sum += ratio * delta
		if ratio >= 0.95:
			full_time += delta
	for h in heroes:
		hero_time += delta
		if h.waiting_for_ammo:
			hero_wait_time += delta
	_update_spawning(delta)


func _update_spawning(delta: float) -> void:
	if not _spawn_queue.is_empty():
		_spawn_timer -= delta
		if _spawn_timer <= 0.0:
			var kind: String = _spawn_queue.pop_front()
			spawn_enemy(kind)
			var tier: String = GameData.ENEMIES[kind]["tier"]
			_spawn_timer = randf_range(0.45, 0.95) * (1.8 if tier == "stark" else 1.0)
		return
	_wave_timer += delta
	if wave < total_waves:
		if enemies.size() <= 2 or _wave_timer > 10.0:
			_next_wave()
	elif enemies.is_empty():
		running = false
		level_won.emit()


func _next_wave() -> void:
	wave += 1
	_spawn_queue.assign(_plan[wave - 1])
	_spawn_timer = 0.6
	_wave_timer = 0.0
	wave_started.emit(wave, total_waves)
	_pulse = 1.0


## Text für die Vorschau: welche Gegner in der nächsten Welle kommen.
func next_wave_text() -> String:
	if wave >= total_waves:
		return "Letzte Welle – halte durch!"
	var counts := {}
	var order: Array[String] = []
	for kind in _plan[wave]:
		if not counts.has(kind):
			order.append(kind)
		counts[kind] = int(counts.get(kind, 0)) + 1
	var parts: Array[String] = []
	var kinds: Array = GameData.WORLDS[GameData.world_of(level)]["kinds"].duplicate()
	kinds.reverse()
	for kind in kinds:
		if counts.has(kind):
			var n: int = counts[kind]
			parts.append("%d %s" % [n, GameData.enemy_name(kind, level, n != 1)])
	var prefix := "Erste Welle: " if wave == 0 else "Als Nächstes: "
	return prefix + " · ".join(PackedStringArray(parts))


func spawn_enemy(kind: String, pos := Vector3.INF) -> Enemy:
	var e := Enemy.new()
	add_child(e)
	if pos == Vector3.INF:
		pos = Vector3(randf_range(-3.6, 3.6), 0, SPAWN_Z + randf_range(-1.0, 1.0))
	e.position = pos
	e.tint = GameData.world_tint(level)
	e.dps_scale = GameData.dps_mult(level)
	var hp := GameData.hp_mult(level, maxi(wave, 1)) * hp_scale
	if GameData.ENEMIES[kind]["tier"] == "boss":
		hp *= GameData.boss_hp(level)
	e.setup(kind, self, hp)
	enemies.append(e)
	if pos.z < SPAWN_Z + 3.0:
		# Auftauchen aus dem Wurmloch
		Fx.flash(self, pos + Vector3(0, 0.8, 0), Color(0.75, 0.35, 1.0), 1.6, 0.4)
	if GameData.ENEMIES[kind]["tier"] == "boss":
		Fx.flash(self, pos + Vector3(0, 1.5, 0), Color(1.0, 0.3, 0.9), 5.0, 0.6)
		add_shake(0.5)
	return e


func on_enemy_died(e: Enemy) -> void:
	enemies.erase(e)
	kills += 1
	var col := Color(0.4, 1.0, 0.5)
	match e.kind:
		"tentakler":
			col = Color(0.75, 0.35, 1.0)
		"panzerkaefer":
			col = Color(0.3, 0.95, 0.9)
		"schleimmutter":
			col = Color(1.0, 0.35, 0.85)
		"krabbler", "zombie":
			col = Color(0.55, 0.75, 0.35)
		"brecher":
			col = Color(0.6, 0.6, 0.55)
		"koloss":
			col = Color(0.7, 1.0, 0.3)
	Fx.burst(self, e.aim_point(), col, 10 + int(e.size * 10), 4.0 + e.size * 2.0, 0.08 + e.size * 0.05)
	if e.is_boss():
		Fx.flash(self, e.aim_point(), col, 6.0, 0.5)
		add_shake(0.8)
	enemy_killed.emit(e, e.xp)


func damage_fence(amount: float) -> void:
	if not running or shield_guard > 0.0:
		return
	fence_hp -= amount
	_fence_flash = minf(1.0, _fence_flash + amount * 0.02)
	if fence_hp <= 0.0:
		fence_hp = 0.0
		running = false
		fence_changed.emit(fence_hp, fence_max)
		level_lost.emit()
		return
	fence_changed.emit(fence_hp, fence_max)


## Booster: Bomben auf fünf Stellen der Bahn
func booster_air_strike(power: float) -> void:
	var spots: Array[Vector3] = []
	# Zuerst dort, wo Gegner stehen
	for e in enemies:
		if spots.size() >= 5:
			break
		if e.ready_as_target():
			spots.append(e.global_position)
	while spots.size() < 5:
		spots.append(Vector3(randf_range(-3.5, 3.5), 0, randf_range(-20.0, -4.0)))
	for i in spots.size():
		var p := spots[i]
		get_tree().create_timer(0.15 * i).timeout.connect(func() -> void:
			explode(p, 2.3, 140.0 * power * GameData.hp_mult(level, maxi(wave, 1)), false, "fire"))


## Booster: alle Gegner verlangsamen
func booster_slow(power: float) -> void:
	for e in enemies:
		e.apply_slow(clampf(0.6 * power, 0.0, 0.85), 5.0)
	Fx.flash(self, Vector3(0, 1, -12), Color(0.5, 0.85, 1.0), 12.0, 0.5)


## Booster: Schild kurz unverwundbar
var shield_guard := 0.0


func booster_dome(power: float) -> void:
	shield_guard = 4.0 * power
	_fence_flash = 1.0


func repair_fence(fraction: float, raise_max: float) -> void:
	fence_max *= 1.0 + raise_max
	fence_hp = minf(fence_max, fence_hp + fence_max * fraction)
	fence_changed.emit(fence_hp, fence_max)
	_fence_flash = 0.6


## Anteil der Zeit, in der Helden auf Munition warten mussten.
## Energiekern entladen: alle Helden feuern einige Sekunden doppelt so schnell und laden sofort nach
func overdrive(seconds: float) -> void:
	overdrive_left = seconds
	for h in heroes:
		h.reload_left = 0.0


func ammo_wait_ratio() -> float:
	return hero_wait_time / maxf(0.001, hero_time)


func add_shake(amount: float) -> void:
	_shake = minf(1.0, _shake + amount)


# --- Zielwahl und Treffer --------------------------------------------------

## Vorderster Gegner, also der, der dem Zaun am nächsten ist.
func pick_target() -> Enemy:
	var frame := Engine.get_process_frames()
	if frame == _target_frame and is_instance_valid(_target_cache) and _target_cache.alive:
		return _target_cache
	var best: Enemy = null
	var best_z := -INF
	for e in enemies:
		if e.ready_as_target() and e.position.z > best_z:
			best = e
			best_z = e.position.z
	_target_cache = best
	_target_frame = frame
	return best


## Weitere Ziele für Streuschüsse, möglichst nicht das Hauptziel.
func spread_targets(n: int, main: Enemy) -> Array[Enemy]:
	var pool: Array[Enemy] = []
	for e in enemies:
		if e.ready_as_target() and e != main:
			pool.append(e)
	pool.sort_custom(func(a: Enemy, b: Enemy) -> bool: return a.position.z > b.position.z)
	var out: Array[Enemy] = []
	for i in n:
		if pool.is_empty():
			if is_instance_valid(main) and main.alive:
				out.append(main)
		else:
			out.append(pool[i % pool.size()])
	return out


func fire_bullet(from: Vector3, target: Enemy, dmg: float, crit: bool, ammo_type: String,
		pierce: int, speed: float, size: float) -> void:
	var p := Projectile.new()
	add_child(p)
	p.pierce = pierce
	p.launch(self, "bullet", from, target, dmg, crit, ammo_type, speed, size)


func fire_rocket(from: Vector3, target: Enemy, dmg: float, crit: bool, ammo_type: String, radius: float) -> void:
	var p := Projectile.new()
	add_child(p)
	p.splash = radius
	p.launch(self, "rocket", from, target, dmg, crit, ammo_type, 11.0, 1.0)


func fire_chain(from: Vector3, target: Enemy, dmg: float, crit: bool, ammo_type: String, jumps: int, color := Color(0, 0, 0, 0)) -> void:
	var hit: Array[Enemy] = [target]
	var points: Array[Vector3] = [from, target.aim_point()]
	var current := target
	apply_hit(target, dmg, crit, ammo_type)
	var d := dmg
	for i in jumps:
		d *= 0.8
		var nxt := _nearest_enemy(current.global_position, 4.5, hit)
		if nxt == null:
			break
		hit.append(nxt)
		points.append(nxt.aim_point())
		apply_hit(nxt, d, false, ammo_type)
		current = nxt
	var col := Color(0.8, 0.5, 1.0)
	if ammo_type == "fire":
		col = Color(1.0, 0.5, 0.2)
	elif ammo_type == "ice":
		col = Color(0.5, 0.9, 1.0)
	if color.a > 0.0:
		col = color
	Fx.lightning(self, points, col)


## Flammenwerfer: trifft alle Gegner im Umkreis des Ziels und setzt sie in Brand.
func flame(from: Vector3, target: Enemy, dmg: float, crit: bool, ammo_type: String, radius: float) -> void:
	var center := target.global_position
	for e in enemies.duplicate():
		if not is_instance_valid(e) or not e.alive:
			continue
		if Vector2(e.position.x - center.x, e.position.z - center.z).length() <= radius + e.radius():
			apply_hit(e, dmg, crit, ammo_type)
			e.apply_burn(dmg * 0.6, 2.5)
	_flame_tick += 1
	if _flame_tick % 3 == 0:
		var mid := from.lerp(target.aim_point(), 0.7)
		Fx.flash(self, mid, Color(1.0, 0.55, 0.15), 0.9, 0.2)
		Fx.flash(self, target.aim_point(), Color(1.0, 0.35, 0.1), radius * 0.8, 0.25)


func _nearest_enemy(pos: Vector3, max_dist: float, exclude: Array[Enemy]) -> Enemy:
	var best: Enemy = null
	var best_d := max_dist
	for e in enemies:
		if not e.ready_as_target() or exclude.has(e):
			continue
		var d := e.global_position.distance_to(pos)
		if d < best_d:
			best = e
			best_d = d
	return best


func apply_hit(e: Enemy, dmg: float, crit: bool, ammo_type: String) -> void:
	if not is_instance_valid(e) or not e.alive:
		return
	var at := e.aim_point()
	var dealt := e.take_damage(dmg)
	if ammo_type == "fire":
		e.apply_burn(dmg * 0.35, 3.0)
	elif ammo_type == "ice":
		e.apply_slow(0.45, 2.0)
	damage_dealt.emit(at, dealt, crit)
	if crit:
		Fx.burst(self, at, Projectile.AMMO_COLORS.get(ammo_type, Color.WHITE), 5, 2.5, 0.06, 0.3)


func pierce_behind(main: Enemy, count: int, dmg: float, ammo_type: String) -> void:
	var behind: Array[Enemy] = []
	for e in enemies:
		if e != main and e.ready_as_target() and absf(e.position.x - main.position.x) < 0.8 and e.position.z < main.position.z:
			behind.append(e)
	behind.sort_custom(func(a: Enemy, b: Enemy) -> bool: return a.position.z > b.position.z)
	for i in mini(count, behind.size()):
		apply_hit(behind[i], dmg, false, ammo_type)


func explode(pos: Vector3, radius: float, dmg: float, crit: bool, ammo_type: String) -> void:
	for e in enemies.duplicate():
		if not is_instance_valid(e) or not e.alive:
			continue
		var d := Vector2(e.position.x - pos.x, e.position.z - pos.z).length()
		if d <= radius + e.radius():
			var falloff := 1.0 if d < radius * 0.5 else 0.7
			apply_hit(e, dmg * falloff, crit, ammo_type)
	var col: Color = Projectile.AMMO_COLORS.get(ammo_type, Color.WHITE)
	if ammo_type == "normal":
		col = Color(1.0, 0.6, 0.2)
	Sfx.play("boom", 0.12, -3.0)
	Fx.flash(self, pos, col, radius, 0.28)
	Fx.burst(self, pos, col, 14, 6.0, 0.12, 0.5)
	add_shake(0.22)


# --- Welt ------------------------------------------------------------------

func _animate_world(delta: float) -> void:
	if camera:
		_shake = maxf(0.0, _shake - delta * 2.5)
		var s := _shake * _shake * 0.35
		var offset := Vector3(randf_range(-s, s), randf_range(-s, s), 0)
		camera.transform = _cam_base.translated_local(offset)
	_fence_flash = maxf(0.0, _fence_flash - delta * 3.0)
	if shield_guard > 0.0:
		_fence_flash = maxf(_fence_flash, 0.6 + 0.3 * sin(Time.get_ticks_msec() * 0.01))
	if _fence_mat:
		_fence_mat.set_shader_parameter("hit", _fence_flash)
		_fence_mat.set_shader_parameter("health", fence_hp / maxf(1.0, fence_max))
	_pulse = maxf(0.0, _pulse - delta * 1.5)
	if _wormhole_mat:
		_wormhole_mat.set_shader_parameter("pulse", _pulse)
	if _wormhole_ring:
		_wormhole_ring.rotation.z += delta * 0.4
	for i in _asteroids.size():
		_asteroids[i].rotate_y(delta * (0.1 + 0.05 * i))
		_asteroids[i].rotate_x(delta * 0.07)


func _build_world() -> void:
	# Umgebung: Weltraum mit Sternen, Licht, leichtes Leuchten
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_SKY
	var sky := Sky.new()
	var sky_mat := ShaderMaterial.new()
	sky_mat.shader = preload("res://shaders/nebula_sky.gdshader")
	sky.sky_material = sky_mat
	e.sky = sky
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.55, 0.6, 0.85)
	e.ambient_light_energy = 0.75
	e.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	e.glow_enabled = true
	e.glow_intensity = 0.7
	e.glow_bloom = 0.05
	e.glow_hdr_threshold = 0.9
	env.environment = e
	add_child(env)
	_env = e

	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-58, -35, 0)
	sun.light_energy = 1.15
	sun.light_color = Color(1.0, 0.95, 0.9)
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 40.0
	_sun = sun
	add_child(sun)

	var rim := OmniLight3D.new()
	rim.position = Vector3(0, 4, -27)
	rim.light_color = Color(0.7, 0.35, 1.0)
	rim.light_energy = 2.5
	rim.omni_range = 22.0
	add_child(rim)
	_rim = rim

	camera = Camera3D.new()
	camera.keep_aspect = Camera3D.KEEP_WIDTH
	camera.fov = 34.0
	camera.position = Vector3(0, 15.5, 13.5)
	add_child(camera)
	camera.look_at(Vector3(0, 0, -8.5), Vector3.UP)
	_cam_base = camera.transform
	camera.current = true

	# Stationsdeck
	var deck_mesh := PlaneMesh.new()
	deck_mesh.size = Vector2(DECK_HALF_W * 2.0, 46.0)
	var deck_mat := ShaderMaterial.new()
	deck_mat.shader = preload("res://shaders/deck_mock.gdshader")
	# Zaun liegt bei z = 0; das Deck reicht von z = +9 bis z = -37.
	deck_mat.set_shader_parameter("fence_v", (FENCE_Z - (-37.0)) / 46.0)
	var deck := Fx.inst(deck_mesh, deck_mat)
	deck.position = Vector3(0, 0, -14.0)
	add_child(deck)
	var under := Fx.box(Vector3(DECK_HALF_W * 2.0 + 0.4, 0.8, 46.0), Fx.mat(Color(0.1, 0.11, 0.16), 0.0, 0.6, 0.4))
	under.position = Vector3(0, -0.42, -14.0)
	add_child(under)

	# Geländer mit Leuchtstreifen
	for side in [-1.0, 1.0]:
		var rail := Fx.box(Vector3(0.3, 0.45, 46.0), Fx.mat(Color(0.22, 0.24, 0.3), 0.0, 0.7, 0.3))
		rail.position = Vector3(side * (DECK_HALF_W + 0.1), 0.22, -14.0)
		add_child(rail)
		var strip := Fx.box(Vector3(0.08, 0.06, 46.0), Fx.mat(Color(0.2, 0.85, 1.0), 2.2))
		strip.position = Vector3(side * (DECK_HALF_W + 0.1), 0.47, -14.0)
		add_child(strip)
		for k in 9:
			var post := Fx.box(Vector3(0.32, 0.9, 0.32), Fx.mat(Color(0.18, 0.2, 0.26), 0.0, 0.7, 0.3))
			post.position = Vector3(side * (DECK_HALF_W + 0.1), 0.45, 6.0 - k * 5.0)
			add_child(post)
			var light := Fx.sphere(0.1, Fx.mat(Color(1.0, 0.65, 0.2), 3.0), 8, 4)
			light.position = Vector3(side * (DECK_HALF_W + 0.1), 0.95, 6.0 - k * 5.0)
			add_child(light)

	# Energiezaun
	for k in 8:
		var x := -DECK_HALF_W + 0.25 + k * (DECK_HALF_W * 2.0 - 0.5) / 7.0
		var post := Fx.box(Vector3(0.22, 1.3, 0.22), Fx.mat(Color(0.28, 0.3, 0.36), 0.0, 0.8, 0.3))
		post.position = Vector3(x, 0.65, FENCE_Z)
		post.visible = false   # die Mauer zeichnet die Kampfanzeige (Mockup)
		add_child(post)
		var cap := Fx.sphere(0.13, Fx.mat(Color(0.2, 0.85, 1.0), 3.0), 8, 4)
		cap.position = Vector3(x, 1.36, FENCE_Z)
		cap.visible = false
		add_child(cap)
	var field := QuadMesh.new()
	field.size = Vector2(DECK_HALF_W * 2.0 - 0.4, 1.25)
	_fence_mat = ShaderMaterial.new()
	_fence_mat.shader = preload("res://shaders/energy_fence.gdshader")
	var field_inst := Fx.inst(field, _fence_mat)
	field_inst.position = Vector3(0, 0.66, FENCE_Z)
	add_child(field_inst)

	# Wurmloch am Ende des Decks
	var hole := QuadMesh.new()
	hole.size = Vector2(13, 13)
	_wormhole_mat = ShaderMaterial.new()
	_wormhole_mat.shader = preload("res://shaders/wormhole.gdshader")
	var hole_inst := Fx.inst(hole, _wormhole_mat)
	hole_inst.position = Vector3(0, 3.6, -34.0)
	add_child(hole_inst)
	_wormhole_ring = Node3D.new()
	_wormhole_ring.position = Vector3(0, 3.6, -33.6)
	_wormhole_ring.visible = false   # im Mockup nur der Wirbel, ohne Rahmen
	add_child(_wormhole_ring)
	var ring := Fx.torus(5.0, 5.5, Fx.mat(Color(0.35, 0.3, 0.45), 0.0, 0.8, 0.3))
	ring.rotation.x = PI * 0.5
	_wormhole_ring.add_child(ring)
	for k in 6:
		var a := k * TAU / 6.0
		var node := Fx.box(Vector3(0.7, 0.7, 0.7), Fx.mat(Color(0.75, 0.4, 1.0), 2.5))
		node.position = Vector3(cos(a) * 5.25, sin(a) * 5.25, 0)
		_wormhole_ring.add_child(node)

	# Stationsaufbauten neben dem Deck, nahe bei den Helden
	var props := [
		[Vector3(-6.2, 0.6, 3.0), Vector3(1.4, 1.2, 1.4), Color(0.85, 0.55, 0.15)],
		[Vector3(-6.0, 1.6, 3.2), Vector3(1.0, 0.8, 1.0), Color(0.75, 0.75, 0.8)],
		[Vector3(6.3, 0.9, 2.0), Vector3(1.2, 1.8, 2.4), Color(0.3, 0.35, 0.45)],
		[Vector3(6.1, 0.5, -3.5), Vector3(1.0, 1.0, 1.0), Color(0.85, 0.55, 0.15)],
	]
	for p in props:
		var crate := Fx.box(p[1], Fx.mat(p[2], 0.0, 0.4, 0.5))
		crate.position = p[0]
		crate.visible = false   # im Mockup stehen keine Kisten neben der Brücke
		add_child(crate)
	var mast := Fx.cylinder(0.08, 0.12, 4.0, Fx.mat(Color(0.5, 0.52, 0.58), 0.0, 0.8, 0.3))
	mast.position = Vector3(6.3, 3.6, 2.0)
	mast.visible = false
	add_child(mast)
	var beacon := Fx.sphere(0.2, Fx.mat(Color(1.0, 0.2, 0.2), 4.0), 8, 4)
	beacon.position = Vector3(6.3, 5.7, 2.0)
	beacon.visible = false
	add_child(beacon)

	# Asteroiden und ein Planet im Hintergrund
	var rock_mat := Fx.mat(Color(0.42, 0.36, 0.34), 0.0, 0.1, 0.9)
	var rng := RandomNumberGenerator.new()
	rng.seed = 7
	for k in 12:
		var side := -1.0 if k % 2 == 0 else 1.0
		var rock := Fx.sphere(rng.randf_range(0.5, 1.6), rock_mat, 7, 4)
		rock.position = Vector3(side * rng.randf_range(8.0, 15.0), rng.randf_range(-5.0, 3.0), rng.randf_range(-36.0, 4.0))
		rock.scale = Vector3(1.0, rng.randf_range(0.6, 0.9), rng.randf_range(0.8, 1.2))
		add_child(rock)
		_asteroids.append(rock)
	# Planeten wie im Mockup: großer Lava-Planet links, Eisplanet mit Ring rechts oben
	var lava := _noise_tex(3, 0.012, PackedColorArray([Color(0.35, 0.08, 0.06), Color(0.85, 0.35, 0.15), Color(1.0, 0.75, 0.45), Color(0.6, 0.2, 0.12)]), PackedFloat32Array([0.0, 0.4, 0.6, 1.0]))
	_planet(Vector3(-27.0, -6.0, -40.0), 17.0, lava, Color(1.0, 0.55, 0.35))
	var ice := _noise_tex(9, 0.018, PackedColorArray([Color(0.1, 0.25, 0.6), Color(0.3, 0.6, 0.95), Color(0.85, 0.95, 1.0), Color(0.2, 0.45, 0.85)]), PackedFloat32Array([0.0, 0.45, 0.62, 1.0]))
	var p2 := _planet(Vector3(19.0, 16.0, -62.0), 5.0, ice, Color(0.5, 0.8, 1.0))
	var pring := MeshInstance3D.new()
	var q := PlaneMesh.new()
	q.size = Vector2(22, 22)
	pring.mesh = q
	var rm := ShaderMaterial.new()
	rm.shader = preload("res://shaders/planet_ring.gdshader")
	pring.material_override = rm
	pring.rotation_degrees = Vector3(14, 0, -18)
	p2.add_child(pring)


## Rauschtextur für Planetenoberflächen
func _noise_tex(seed: int, freq: float, cols: PackedColorArray, offs: PackedFloat32Array) -> NoiseTexture2D:
	var n := FastNoiseLite.new()
	n.seed = seed
	n.frequency = freq
	n.fractal_octaves = 5
	n.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	var t := NoiseTexture2D.new()
	t.width = 512
	t.height = 256
	t.seamless = true
	t.noise = n
	var g := Gradient.new()
	g.offsets = offs
	g.colors = cols
	t.color_ramp = g
	return t


## Planet mit Oberfläche und leuchtender Atmosphäre
func _planet(pos: Vector3, r: float, tex: Texture2D, atmo: Color) -> Node3D:
	var root := Node3D.new()
	root.position = pos
	add_child(root)
	var mi := MeshInstance3D.new()
	var sm := SphereMesh.new()
	sm.radius = r
	sm.height = r * 2.0
	sm.radial_segments = 48
	sm.rings = 24
	mi.mesh = sm
	var m := StandardMaterial3D.new()
	m.albedo_texture = tex
	m.roughness = 0.85
	mi.material_override = m
	root.add_child(mi)
	var at := MeshInstance3D.new()
	var s2 := SphereMesh.new()
	s2.radius = r * 1.06
	s2.height = r * 2.12
	s2.radial_segments = 48
	s2.rings = 24
	at.mesh = s2
	var am := ShaderMaterial.new()
	am.shader = preload("res://shaders/atmosphere.gdshader")
	am.set_shader_parameter("col", atmo)
	at.material_override = am
	root.add_child(at)
	return root
