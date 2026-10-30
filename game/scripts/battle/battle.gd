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
const HERO_Z := 1.7
const MAX_HEROES := 4
const DECK_HALF_W := 4.7

var level := 1
var ammo: AmmoStore
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
## Für Auswertungen: Heldensekunden ohne Munition und Heldensekunden insgesamt.
var hero_wait_time := 0.0
var hero_time := 0.0

var _spawn_queue: Array[String] = []
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
var _target_frame := -1


func _ready() -> void:
	_build_world()


# --- Ablauf ----------------------------------------------------------------

func setup(level_: int, ammo_: AmmoStore) -> void:
	clear()
	level = level_
	ammo = ammo_
	fence_max = 1000.0 + 300.0 * (level - 1)
	fence_hp = fence_max
	total_waves = GameData.waves_in_level(level)
	wave = 0
	kills = 0
	elapsed = 0.0
	hero_wait_time = 0.0
	hero_time = 0.0
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


func add_hero(id: String) -> Hero:
	var h := Hero.new()
	add_child(h)
	h.position = Vector3(0, 0, HERO_Z)
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
	var spacing := 2.3
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
			_spawn_timer = randf_range(0.45, 0.95) * (1.8 if kind == "panzerkaefer" else 1.0)
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
	_spawn_queue = GameData.wave_spawns(level, wave)
	_spawn_timer = 0.6
	_wave_timer = 0.0
	wave_started.emit(wave, total_waves)
	_pulse = 1.0


func spawn_enemy(kind: String, pos := Vector3.INF) -> Enemy:
	var e := Enemy.new()
	add_child(e)
	if pos == Vector3.INF:
		pos = Vector3(randf_range(-3.6, 3.6), 0, SPAWN_Z + randf_range(-1.0, 1.0))
	e.position = pos
	e.setup(kind, self, GameData.hp_mult(level, maxi(wave, 1)))
	enemies.append(e)
	if kind == "schleimmutter":
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
	Fx.burst(self, e.aim_point(), col, 10 + int(e.size * 10), 4.0 + e.size * 2.0, 0.08 + e.size * 0.05)
	if e.is_boss():
		Fx.flash(self, e.aim_point(), col, 6.0, 0.5)
		add_shake(0.8)
	enemy_killed.emit(e, e.xp)


func damage_fence(amount: float) -> void:
	if not running:
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


func repair_fence(fraction: float, raise_max: float) -> void:
	fence_max *= 1.0 + raise_max
	fence_hp = minf(fence_max, fence_hp + fence_max * fraction)
	fence_changed.emit(fence_hp, fence_max)
	_fence_flash = 0.6


## Anteil der Zeit, in der Helden auf Munition warten mussten.
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
	p.launch(self, "rocket", from, target, dmg, crit, ammo_type, 16.0, 1.0)


func fire_chain(from: Vector3, target: Enemy, dmg: float, crit: bool, ammo_type: String, jumps: int) -> void:
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
	Fx.lightning(self, points, col)


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
	Fx.burst(self, at, Projectile.AMMO_COLORS.get(ammo_type, Color.WHITE), 4, 2.5, 0.05, 0.3)


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
	Fx.flash(self, pos, col, radius, 0.28)
	Fx.burst(self, pos, col, 22, 6.0, 0.12, 0.6)
	Fx.burst(self, pos, Color(0.35, 0.35, 0.4), 10, 2.0, 0.2, 0.9)
	add_shake(0.22)


# --- Welt ------------------------------------------------------------------

func _animate_world(delta: float) -> void:
	if camera:
		_shake = maxf(0.0, _shake - delta * 2.5)
		var s := _shake * _shake * 0.35
		var offset := Vector3(randf_range(-s, s), randf_range(-s, s), 0)
		camera.transform = _cam_base.translated_local(offset)
	_fence_flash = maxf(0.0, _fence_flash - delta * 3.0)
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
	sky_mat.shader = preload("res://shaders/space_sky.gdshader")
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

	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-58, -35, 0)
	sun.light_energy = 1.15
	sun.light_color = Color(1.0, 0.95, 0.9)
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 45.0
	add_child(sun)

	var rim := OmniLight3D.new()
	rim.position = Vector3(0, 4, -27)
	rim.light_color = Color(0.7, 0.35, 1.0)
	rim.light_energy = 2.5
	rim.omni_range = 22.0
	add_child(rim)

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
	deck_mat.shader = preload("res://shaders/deck.gdshader")
	deck_mat.set_shader_parameter("tiles", Vector2(4.0, 19.6))
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
		add_child(post)
		var cap := Fx.sphere(0.13, Fx.mat(Color(0.2, 0.85, 1.0), 3.0), 8, 4)
		cap.position = Vector3(x, 1.36, FENCE_Z)
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
		add_child(crate)
	var mast := Fx.cylinder(0.08, 0.12, 4.0, Fx.mat(Color(0.5, 0.52, 0.58), 0.0, 0.8, 0.3))
	mast.position = Vector3(6.3, 3.6, 2.0)
	add_child(mast)
	var beacon := Fx.sphere(0.2, Fx.mat(Color(1.0, 0.2, 0.2), 4.0), 8, 4)
	beacon.position = Vector3(6.3, 5.7, 2.0)
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
	var planet := Fx.sphere(9.0, Fx.mat(Color(0.25, 0.45, 0.75), 0.25, 0.0, 0.8), 32, 16)
	planet.position = Vector3(-26.0, 6.0, -62.0)
	add_child(planet)
	var planet_ring := Fx.torus(11.0, 13.5, Fx.mat(Color(0.75, 0.6, 0.45), 0.2, 0.0, 0.8))
	planet_ring.position = planet.position
	planet_ring.rotation = Vector3(0.4, 0.0, 0.3)
	add_child(planet_ring)
