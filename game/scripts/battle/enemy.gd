class_name Enemy
extends Node3D
## Ein Gegner: läuft auf den Energiezaun zu und greift ihn an, sobald er ihn erreicht.

## Alle Gegner werden in dieser Größe dargestellt.
const VIS_SCALE := 1.45

var kind := ""
var data: Dictionary
var battle: Battle
var hp := 1.0
var max_hp := 1.0
var speed := 1.0
var armor := 0.0
var dps := 1.0
var xp := 1
var size := 1.0
var alive := true
var attacking := false

var _t := 0.0
var _phase := 0.0
var _base_x := 0.0
var _burn_dps := 0.0
var _burn_t := 0.0
var _burn_tick := 0.0
var _slow := 0.0
var _slow_t := 0.0
var _flash := 0.0
var _appear := 0.0
var _spawn_cd := 5.0
var _visual: Node3D
var _mats: Array[StandardMaterial3D] = []
var _wiggle: Array[Node3D] = []
var _ice_tint := 0.0
var _last_tint_key := 0.0
## Fertiges 3D-Modell (wenn vorhanden) mit Animationen und Aufblitz-Überlagerung.
var _model: Node3D
var _anim: AnimationPlayer
var _overlay: StandardMaterial3D
var _overlay_on := false
var _anim_name := ""
## Färbung der Welt (Weiß = Originalfarben), vor setup() setzen.
var tint := Color(1, 1, 1)


func setup(kind_: String, battle_: Battle, hp_mult: float) -> void:
	kind = kind_
	battle = battle_
	data = GameData.ENEMIES[kind]
	max_hp = float(data["hp"]) * hp_mult
	hp = max_hp
	speed = float(data["speed"]) * randf_range(0.92, 1.08)
	armor = float(data["armor"])
	dps = float(data["dps"])
	xp = int(data["xp"])
	size = float(data["size"])
	_phase = randf() * TAU
	_base_x = position.x
	scale = Vector3.ONE * VIS_SCALE
	_build_visual()
	_visual.scale = Vector3.ONE * 0.01


func is_boss() -> bool:
	return data["tier"] == "boss"


func aim_point() -> Vector3:
	return global_position + Vector3(0, size * 0.55 * VIS_SCALE, 0)


## Höhe über dem Boden für den Lebensbalken.
func top_height() -> float:
	return (size * 1.25 + 0.3) * VIS_SCALE


## Halbe Breite am Boden (für Treffer durch Explosionen).
func radius() -> float:
	return size * 0.5 * VIS_SCALE


func ready_as_target() -> bool:
	return alive and _appear > 0.35


func take_damage(amount: float) -> float:
	if not alive:
		return 0.0
	var dealt := amount * (1.0 - armor)
	hp -= dealt
	_flash = 1.0
	if hp <= 0.0:
		_die()
	return dealt


func apply_burn(burn_dps: float, duration: float) -> void:
	_burn_dps = maxf(_burn_dps, burn_dps)
	_burn_t = maxf(_burn_t, duration)


func apply_slow(amount: float, duration: float) -> void:
	_slow = maxf(_slow, amount)
	_slow_t = maxf(_slow_t, duration)


func _process(delta: float) -> void:
	if not alive:
		return
	_t += delta
	_appear = minf(1.0, _appear + delta * 2.2)
	var s := _appear
	_visual.scale = Vector3.ONE * (s * (1.0 + 0.25 * sin(s * PI)))
	if not battle.running:
		_animate(delta, false)
		return
	_update_effects(delta)
	if not alive:
		return
	var spd := speed * (1.0 - _slow)
	if not attacking:
		position.z += spd * delta
		if data["tier"] == "leicht" or data["tier"] == "mittel":
			position.x = clampf(_base_x + sin(_t * 1.4 + _phase) * 0.25, -3.9, 3.9)
		if position.z >= Battle.FENCE_Z - (0.3 + radius()):
			attacking = true
	else:
		battle.damage_fence(dps * delta)
	if is_boss():
		_spawn_cd -= delta
		if _spawn_cd <= 0.0:
			_spawn_cd = 6.5
			for i in 3:
				var p := position + Vector3(randf_range(-1.6, 1.6), 0, randf_range(0.6, 1.4))
				p.x = clampf(p.x, -3.8, 3.8)
				battle.spawn_enemy(String(data.get("minion", "schleimling")), p)
			Fx.burst(battle, aim_point(), Color(0.95, 0.3, 0.85), 18, 5.0, 0.14)
	_animate(delta, true)


func _update_effects(delta: float) -> void:
	if _burn_t > 0.0:
		_burn_t -= delta
		var dmg := _burn_dps * delta
		hp -= dmg * (1.0 - armor)
		_burn_tick -= delta
		if _burn_tick <= 0.0:
			_burn_tick = 0.6
			Fx.burst(battle, aim_point(), Color(1.0, 0.5, 0.1), 4, 1.8, 0.07, 0.35)
		if hp <= 0.0:
			_die()
			return
	if _slow_t > 0.0:
		_slow_t -= delta
		if _slow_t <= 0.0:
			_slow = 0.0
	_ice_tint = move_toward(_ice_tint, 1.0 if _slow_t > 0.0 else 0.0, delta * 4.0)
	_flash = maxf(0.0, _flash - delta * 7.0)
	# Materialien nur anfassen, wenn sich Aufblitzen oder Eis-Färbung geändert haben
	var key := snappedf(_flash, 0.1) + snappedf(_ice_tint, 0.1) * 10.0
	if key == _last_tint_key:
		return
	_last_tint_key = key
	if _overlay:
		var c := Color(1, 1, 1) * (_flash * 0.75) + Color(0.15, 0.4, 0.75) * (_ice_tint * 0.6)
		_overlay.albedo_color = Color(c.r, c.g, c.b, 1.0)
		var on := key > 0.0
		if on != _overlay_on:
			_overlay_on = on
			Models.set_overlay(_model, _overlay if on else null)
	for m in _mats:
		var base: Color = m.get_meta("base_emission")
		var c := base.lerp(Color(1, 1, 1), _flash * 0.85)
		c = c.lerp(Color(0.3, 0.7, 1.2), _ice_tint * 0.5)
		m.emission = c


func _animate(_delta: float, moving: bool) -> void:
	if _model:
		var d: Dictionary = Models.ENEMIES[kind]
		_play(String(d["attack"]) if attacking else String(d["walk"]))
		if _anim:
			_anim.speed_scale = (1.0 - _slow) * (1.0 if moving else 0.6)
		return
	var t := _t
	match kind:
		"schleimling":
			var hop := absf(sin(t * 7.0 + _phase))
			_visual.position.y = hop * 0.35 if moving else 0.0
			_visual.scale *= Vector3(1.0 + (1.0 - hop) * 0.15, 0.85 + hop * 0.25, 1.0 + (1.0 - hop) * 0.15)
		"tentakler":
			_visual.position.y = sin(t * 3.0 + _phase) * 0.08
			for i in _wiggle.size():
				_wiggle[i].rotation.x = sin(t * 6.0 + i * 1.7) * 0.35
		"panzerkaefer":
			_visual.rotation.z = sin(t * 8.0) * 0.04
			for i in _wiggle.size():
				_wiggle[i].rotation.x = sin(t * 12.0 + i * PI) * 0.5
		"schleimmutter":
			var breathe := sin(t * 2.0)
			_visual.scale *= Vector3(1.0 + breathe * 0.04, 1.0 - breathe * 0.05, 1.0 + breathe * 0.04)
			for i in _wiggle.size():
				_wiggle[i].rotation.z = sin(t * 3.0 + i) * 0.15
		"krabbler", "zombie", "brecher", "koloss":
			# Schlurfen: Beine und Arme schwingen gegenläufig
			var spd := 9.0 if kind == "krabbler" else (5.0 if kind != "koloss" else 3.0)
			_visual.rotation.z = sin(t * spd * 0.5 + _phase) * 0.06
			for i in _wiggle.size():
				var sgn := 1.0 if i % 2 == 0 else -1.0
				_wiggle[i].rotation.x = sin(t * spd + _phase) * 0.5 * sgn if moving else 0.0
	if attacking:
		_visual.position.z = absf(sin(t * 6.0)) * 0.18


func _die() -> void:
	if not alive:
		return
	alive = false
	Sfx.play("boom" if is_boss() else "pop", 0.15)
	battle.on_enemy_died(self)
	var tw := create_tween()
	tw.tween_property(_visual, "scale", _visual.scale * 1.35, 0.06)
	tw.tween_property(_visual, "scale", Vector3.ONE * 0.01, 0.12)
	tw.tween_callback(queue_free)


# --- Aussehen -------------------------------------------------------------

func _m(color: Color, emission := 0.0, metallic := 0.0, roughness := 0.5) -> StandardMaterial3D:
	var m := Fx.mat(color, emission, metallic, roughness)
	_mats.append(m)
	return m


func _eye(parent: Node3D, pos: Vector3, r: float, pupil_color := Color(0.05, 0.05, 0.08)) -> void:
	var white := Fx.sphere(r, _m(Color(0.97, 0.97, 1.0), 0.05), 10, 6)
	white.position = pos
	parent.add_child(white)
	var pupil := Fx.sphere(r * 0.5, _m(pupil_color), 8, 4)
	pupil.position = pos + Vector3(0, 0, r * 0.7)
	parent.add_child(pupil)


## Zombie aus einfachen Formen: hängende Haltung, Arme nach vorn, gelbe Augen.
func _zombie(s: float, skin: Color, shirt: Color, armored: bool, crawl: bool) -> void:
	var body := Node3D.new()
	_visual.add_child(body)
	body.scale = Vector3.ONE * s
	if crawl:
		body.rotation.x = 0.7
		body.position.y = -0.25 * s
	for sx in [-0.13, 0.13]:
		var pivot := Node3D.new()
		pivot.position = Vector3(sx, 0.48, 0)
		body.add_child(pivot)
		var leg := Fx.capsule(0.1, 0.5, _m(Color(0.25, 0.25, 0.3)))
		leg.position.y = -0.24
		pivot.add_child(leg)
		_wiggle.append(pivot)
	var torso := Fx.capsule(0.26, 0.72, _m(shirt))
	torso.position.y = 0.82
	torso.rotation.x = 0.25
	body.add_child(torso)
	var head := Fx.sphere(0.22, _m(skin, 0.05), 12, 6)
	head.position = Vector3(0.03, 1.3, 0.12)
	body.add_child(head)
	for ex in [-0.08, 0.08]:
		var eye := Fx.sphere(0.045, _m(Color(1.0, 0.9, 0.2), 3.0), 6, 3)
		eye.position = Vector3(ex + 0.03, 1.33, 0.31)
		body.add_child(eye)
	for sx in [-0.28, 0.28]:
		var pivot := Node3D.new()
		pivot.position = Vector3(sx, 1.05, 0.05)
		body.add_child(pivot)
		var arm := Fx.capsule(0.07, 0.5, _m(skin))
		arm.rotation.x = 1.35
		arm.position = Vector3(0, -0.05, 0.25)
		pivot.add_child(arm)
		_wiggle.append(pivot)
	if armored:
		var plate := Fx.box(Vector3(0.6, 0.45, 0.15), _m(Color(0.5, 0.52, 0.55), 0.0, 0.8, 0.35))
		plate.position = Vector3(0, 0.9, 0.24)
		plate.rotation.x = 0.25
		body.add_child(plate)
		var helmet := Fx.sphere(0.24, _m(Color(0.45, 0.47, 0.5), 0.0, 0.8, 0.35), 12, 6)
		helmet.scale = Vector3(1.0, 0.6, 1.0)
		helmet.position = Vector3(0.03, 1.42, 0.12)
		body.add_child(helmet)


func _build_visual() -> void:
	_visual = Node3D.new()
	add_child(_visual)
	if Models.has_enemy(kind):
		_build_model()
		return
	match kind:
		"schleimling":
			var body := Fx.sphere(0.5, _m(Color(0.32, 0.92, 0.42), 0.25, 0.0, 0.2), 14, 8)
			body.scale = Vector3(1.0, 0.82, 1.0)
			body.position.y = 0.42
			_visual.add_child(body)
			_eye(_visual, Vector3(-0.16, 0.62, 0.34), 0.12)
			_eye(_visual, Vector3(0.16, 0.62, 0.34), 0.12)
			var drop := Fx.sphere(0.12, _m(Color(0.4, 1.0, 0.5), 0.3, 0.0, 0.2), 8, 4)
			drop.position = Vector3(0.3, 0.85, -0.1)
			_visual.add_child(drop)
		"tentakler":
			var body := Fx.capsule(0.38, 1.15, _m(Color(0.62, 0.25, 0.85), 0.15, 0.0, 0.35))
			body.position.y = 0.95
			_visual.add_child(body)
			_eye(_visual, Vector3(0, 1.2, 0.3), 0.2, Color(0.9, 0.2, 0.2))
			for i in 4:
				var pivot := Node3D.new()
				var ang := i * TAU / 4.0 + PI / 4.0
				pivot.position = Vector3(cos(ang) * 0.25, 0.55, sin(ang) * 0.25)
				pivot.rotation.y = -ang
				_visual.add_child(pivot)
				var tent := Fx.cylinder(0.05, 0.12, 0.65, _m(Color(0.5, 0.18, 0.75), 0.1))
				tent.position = Vector3(0.12, -0.3, 0)
				tent.rotation.z = 0.5
				pivot.add_child(tent)
				_wiggle.append(pivot)
		"panzerkaefer":
			var shell := Fx.sphere(0.75, _m(Color(0.12, 0.42, 0.48), 0.05, 0.6, 0.3), 16, 8)
			shell.scale = Vector3(1.0, 0.58, 1.25)
			shell.position.y = 0.55
			_visual.add_child(shell)
			var stripe := Fx.box(Vector3(0.08, 0.05, 1.7), _m(Color(0.3, 0.95, 0.9), 1.2))
			stripe.position = Vector3(0, 0.98, 0)
			_visual.add_child(stripe)
			var head := Fx.sphere(0.34, _m(Color(0.1, 0.3, 0.34), 0.0, 0.5, 0.4), 12, 6)
			head.position = Vector3(0, 0.45, 0.92)
			_visual.add_child(head)
			for sx in [-0.14, 0.14]:
				var e := Fx.sphere(0.07, _m(Color(1.0, 0.2, 0.15), 2.5), 6, 4)
				e.position = Vector3(sx, 0.55, 1.2)
				_visual.add_child(e)
			var horn := Fx.cylinder(0.0, 0.1, 0.45, _m(Color(0.85, 0.85, 0.75)))
			horn.position = Vector3(0, 0.62, 1.22)
			horn.rotation.x = deg_to_rad(70)
			_visual.add_child(horn)
			for side in [-1.0, 1.0]:
				for k in 3:
					var pivot := Node3D.new()
					pivot.position = Vector3(0.62 * side, 0.35, -0.5 + k * 0.5)
					_visual.add_child(pivot)
					var leg := Fx.cylinder(0.04, 0.05, 0.55, _m(Color(0.08, 0.2, 0.22)))
					leg.position = Vector3(0.15 * side, -0.18, 0)
					leg.rotation.z = 0.9 * side
					pivot.add_child(leg)
					_wiggle.append(pivot)
		"schleimmutter":
			var body := Fx.sphere(1.0, _m(Color(0.9, 0.22, 0.72), 0.3, 0.0, 0.25), 20, 10)
			body.scale = Vector3(1.25, 1.0, 1.15)
			body.position.y = 1.0
			_visual.add_child(body)
			var eye_pos := [Vector3(-0.45, 1.35, 0.85), Vector3(0.45, 1.35, 0.85), Vector3(0, 1.6, 0.8), Vector3(-0.25, 1.0, 1.05), Vector3(0.25, 1.0, 1.05)]
			for p in eye_pos:
				_eye(_visual, p, 0.17, Color(0.6, 0.0, 0.4))
			for i in 7:
				var pivot := Node3D.new()
				var ang := -PI * 0.5 + (i - 3) * 0.38
				pivot.position = Vector3(sin(ang) * 0.9, 1.0 + cos(ang) * 0.85, -0.1)
				pivot.rotation.z = -ang
				_visual.add_child(pivot)
				var spike := Fx.cylinder(0.0, 0.16, 0.6, _m(Color(1.0, 0.75, 0.95), 0.8))
				spike.position.y = 0.25
				pivot.add_child(spike)
				_wiggle.append(pivot)
			var aura := Fx.torus(1.5, 1.65, Fx.glow_mat(Color(1.0, 0.3, 0.9), 0.5))
			aura.position.y = 0.05
			_visual.add_child(aura)
		"krabbler":
			_zombie(0.62, Color(0.55, 0.7, 0.45), Color(0.45, 0.35, 0.3), false, true)
		"zombie":
			_zombie(0.95, Color(0.5, 0.65, 0.4), Color(0.3, 0.4, 0.6), false, false)
		"brecher":
			_zombie(1.25, Color(0.45, 0.58, 0.35), Color(0.35, 0.3, 0.28), true, false)
		"koloss":
			_zombie(2.1, Color(0.55, 0.75, 0.3), Color(0.4, 0.2, 0.3), true, false)
			var tank := Fx.cylinder(0.45, 0.45, 1.3, _m(Color(0.6, 1.0, 0.3), 1.5, 0.3, 0.3), 12)
			tank.position = Vector3(0, 2.6, -0.7)
			_visual.add_child(tank)
	_visual.scale = Vector3.ONE
	if kind == "schleimmutter":
		_visual.scale = Vector3.ONE


## Fertiges Modell statt einfacher Formen. Zombies bekommen grünliche Haut.
func _build_model() -> void:
	var d: Dictionary = Models.ENEMIES[kind]
	_model = Models.make(String(d["file"]), float(d["height"]), false)
	_model.position.y = float(d.get("lift", 0.0))
	_visual.add_child(_model)
	if kind == "krabbler" or kind == "zombie":
		Models.recolor(_model, "Skin", Color(0.52, 0.66, 0.42))
	if tint != Color(1, 1, 1):
		Models.tint_all(_model, tint)
	_anim = Models.player(_model)
	_overlay = Models.add_overlay(_model)
	_play(String(d["walk"]))
	if _anim:
		_anim.seek(randf() * 0.8, true)


func _play(anim_name: String) -> void:
	if _anim == null or anim_name == _anim_name or not _anim.has_animation(anim_name):
		return
	_anim_name = anim_name
	_anim.play(anim_name, 0.15)
