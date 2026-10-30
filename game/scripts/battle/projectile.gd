class_name Projectile
extends Node3D
## Kugel oder Rakete. Fliegt dem Ziel nach; ist das Ziel schon besiegt, fliegt sie zu
## dessen letzter Position.

const AMMO_COLORS := {
	"normal": Color(1.0, 0.85, 0.3),
	"fire": Color(1.0, 0.45, 0.12),
	"ice": Color(0.45, 0.9, 1.0),
}

var battle: Battle
var target: Enemy
var dmg := 0.0
var crit := false
var ammo_type := "normal"
var kind := "bullet"
var pierce := 0
var splash := 0.0
var speed := 45.0

var _start := Vector3.ZERO
var _last_target := Vector3.ZERO
var _s := 0.0
var _length := 1.0
var _arc := 0.0
var _trail: CPUParticles3D


func launch(battle_: Battle, kind_: String, from: Vector3, target_: Enemy, dmg_: float, crit_: bool,
		ammo_type_: String, speed_: float, size: float) -> void:
	battle = battle_
	kind = kind_
	target = target_
	dmg = dmg_
	crit = crit_
	ammo_type = ammo_type_
	speed = speed_
	_start = from
	_last_target = target.aim_point()
	_length = maxf(0.5, from.distance_to(_last_target))
	global_position = from
	var col: Color = AMMO_COLORS.get(ammo_type, AMMO_COLORS["normal"])
	if kind == "rocket":
		_arc = clampf(_length * 0.12, 0.6, 2.5)
		var body := Fx.cylinder(0.08, 0.08, 0.42, Fx.mat(Color(0.85, 0.25, 0.2), 0.2))
		body.rotation.x = PI * 0.5
		add_child(body)
		var tip := Fx.cylinder(0.0, 0.08, 0.16, Fx.mat(Color(0.9, 0.9, 0.9)))
		tip.rotation.x = -PI * 0.5
		tip.position.z = -0.29
		add_child(tip)
		var glow := Fx.sphere(0.09, Fx.glow_mat(col), 8, 4)
		glow.position.z = 0.24
		add_child(glow)
		_trail = CPUParticles3D.new()
		_trail.amount = 24
		_trail.lifetime = 0.45
		_trail.local_coords = false
		var m := SphereMesh.new()
		m.radius = 0.09
		m.height = 0.18
		m.radial_segments = 6
		m.rings = 3
		var pm := StandardMaterial3D.new()
		pm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		pm.vertex_color_use_as_albedo = true
		pm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		m.material = pm
		_trail.mesh = m
		_trail.gravity = Vector3(0, 0.6, 0)
		_trail.initial_velocity_max = 0.3
		var grad := Gradient.new()
		grad.set_color(0, Color(1.0, 0.7, 0.3, 0.9))
		grad.set_color(1, Color(0.5, 0.5, 0.55, 0.0))
		_trail.color_ramp = grad
		var curve := Curve.new()
		curve.add_point(Vector2(0, 0.6))
		curve.add_point(Vector2(1, 1.6))
		_trail.scale_amount_curve = curve
		_trail.position.z = 0.25
		add_child(_trail)
	else:
		var b := Fx.capsule(0.045 * size, 0.34 * size, Fx.glow_mat(col))
		b.rotation.x = PI * 0.5
		add_child(b)


func _process(delta: float) -> void:
	if is_instance_valid(target) and target.alive:
		_last_target = target.aim_point()
	_s += speed * delta / _length
	var s := minf(_s, 1.0)
	var pos := _start.lerp(_last_target, s)
	pos.y += _arc * 4.0 * s * (1.0 - s)
	var dir := pos - global_position
	if dir.length() > 0.001:
		look_at(global_position + dir, Vector3.UP)
	global_position = pos
	if _s >= 1.0:
		_impact()


func _impact() -> void:
	if kind == "rocket":
		battle.explode(_last_target, splash, dmg, crit, ammo_type)
		if _trail:
			_trail.emitting = false
	elif is_instance_valid(target) and target.alive:
		battle.apply_hit(target, dmg, crit, ammo_type)
		if pierce > 0:
			battle.pierce_behind(target, pierce, dmg * 0.6, ammo_type)
	queue_free()
