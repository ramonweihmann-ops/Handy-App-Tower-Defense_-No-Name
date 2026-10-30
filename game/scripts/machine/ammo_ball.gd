class_name AmmoBall
extends RigidBody2D
## Eine Energiekugel in der Kugelbahn. Landet sie im Sammler, wird sie zu Munition.

const R := 10.0
const COLORS := {
	"normal": Color(1.0, 0.82, 0.28),
	"fire": Color(1.0, 0.45, 0.15),
	"ice": Color(0.45, 0.9, 1.0),
}

var type := "normal"
## Tore, durch die diese Kugel schon gerollt ist (damit ein Tor nicht doppelt wirkt).
var passed := {}
var age := 0.0
var recycles := 0
var collected := false


func _init() -> void:
	var shape := CircleShape2D.new()
	shape.radius = R
	var cs := CollisionShape2D.new()
	cs.shape = shape
	add_child(cs)
	var pm := PhysicsMaterial.new()
	pm.bounce = 0.45
	pm.friction = 0.15
	physics_material_override = pm
	continuous_cd = RigidBody2D.CCD_MODE_CAST_SHAPE
	collision_layer = 2
	collision_mask = 1 | 2
	can_sleep = false


func set_type(t: String) -> void:
	type = t
	queue_redraw()


func _physics_process(delta: float) -> void:
	age += delta


func _draw() -> void:
	var c: Color = COLORS.get(type, COLORS["normal"])
	draw_circle(Vector2.ZERO, R + 5.0, Color(c.r, c.g, c.b, 0.22))
	draw_circle(Vector2.ZERO, R, c)
	draw_circle(Vector2.ZERO, R * 0.62, c.lightened(0.25))
	draw_circle(Vector2(-3.2, -3.2), R * 0.32, Color(1, 1, 1, 0.8))
