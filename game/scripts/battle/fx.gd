class_name Fx
extends RefCounted
## Hilfsfunktionen für Formen, Materialien und Effekte.
## Der Pilot baut alle Figuren aus einfachen Formen; echte Modelle folgen später.


static func mat(color: Color, emission := 0.0, metallic := 0.0, roughness := 0.6) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.metallic = metallic
	m.roughness = roughness
	m.emission_enabled = true
	m.emission = color * emission
	m.set_meta("base_emission", m.emission)
	return m


## Gemeinsame Formen und Materialien, die sich nie ändern. Neue Formen pro Schuss
## anzulegen kostet im Browser am Handy spürbar Zeit.
static func _cache() -> Dictionary:
	if not Engine.has_meta("fx_cache"):
		Engine.set_meta("fx_cache", {})
	return Engine.get_meta("fx_cache")


static func shared_mesh(key: String, make: Callable) -> Mesh:
	var c := _cache()
	if not c.has(key):
		c[key] = make.call()
	return c[key]


static func shared_glow(color: Color) -> StandardMaterial3D:
	var c := _cache()
	var key := "glow:" + color.to_html()
	if not c.has(key):
		c[key] = glow_mat(color)
	return c[key]


static func unit_sphere() -> Mesh:
	return shared_mesh("sphere1", func() -> Mesh:
		var m := SphereMesh.new()
		m.radius = 1.0
		m.height = 2.0
		m.radial_segments = 12
		m.rings = 6
		return m)


static func unit_box() -> Mesh:
	return shared_mesh("box1", func() -> Mesh: return BoxMesh.new())


static func glow_mat(color: Color, alpha := 1.0) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.albedo_color = Color(color.r, color.g, color.b, alpha)
	if alpha < 1.0:
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	return m


static func inst(mesh: Mesh, material: Material) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = material
	return mi


static func sphere(r: float, material: Material, segments := 16, rings := 8) -> MeshInstance3D:
	var m := SphereMesh.new()
	m.radius = r
	m.height = r * 2.0
	m.radial_segments = segments
	m.rings = rings
	return inst(m, material)


static func box(size: Vector3, material: Material) -> MeshInstance3D:
	var m := BoxMesh.new()
	m.size = size
	return inst(m, material)


static func capsule(r: float, h: float, material: Material) -> MeshInstance3D:
	var m := CapsuleMesh.new()
	m.radius = r
	m.height = maxf(h, r * 2.0)
	m.radial_segments = 12
	m.rings = 4
	return inst(m, material)


static func cylinder(top: float, bottom: float, h: float, material: Material, segments := 12) -> MeshInstance3D:
	var m := CylinderMesh.new()
	m.top_radius = top
	m.bottom_radius = bottom
	m.height = h
	m.radial_segments = segments
	m.rings = 1
	return inst(m, material)


static func torus(inner: float, outer: float, material: Material) -> MeshInstance3D:
	var m := TorusMesh.new()
	m.inner_radius = inner
	m.outer_radius = outer
	m.rings = 24
	m.ring_segments = 8
	return inst(m, material)


## Funken- oder Splitterwolke, die sich selbst aufräumt.
static func burst(parent: Node, pos: Vector3, color: Color, amount := 12, speed := 4.0, size := 0.1, life := 0.5) -> void:
	var p := CPUParticles3D.new()
	p.one_shot = true
	p.explosiveness = 0.95
	p.amount = amount
	p.lifetime = life
	var m := SphereMesh.new()
	m.radius = size
	m.height = size * 2.0
	m.radial_segments = 6
	m.rings = 3
	var pm := StandardMaterial3D.new()
	pm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	pm.vertex_color_use_as_albedo = true
	m.material = pm
	p.mesh = m
	p.direction = Vector3.UP
	p.spread = 180.0
	p.initial_velocity_min = speed * 0.4
	p.initial_velocity_max = speed
	p.gravity = Vector3(0, -9.0, 0)
	p.scale_amount_min = 0.6
	p.scale_amount_max = 1.3
	var curve := Curve.new()
	curve.add_point(Vector2(0, 1))
	curve.add_point(Vector2(1, 0))
	p.scale_amount_curve = curve
	p.color = color
	parent.add_child(p)
	p.global_position = pos
	p.emitting = true
	parent.get_tree().create_timer(life + 0.3).timeout.connect(p.queue_free)


## Aufblähende, verblassende Kugel (Explosion, Mündungsblitz, Auftauchen).
static func flash(parent: Node, pos: Vector3, color: Color, radius: float, duration := 0.25) -> void:
	var m := glow_mat(color, 0.9)
	var s := inst(unit_sphere(), m)
	parent.add_child(s)
	s.global_position = pos
	s.scale = Vector3.ONE * radius * 0.2
	var tw := s.create_tween()
	tw.set_parallel(true)
	tw.tween_property(s, "scale", Vector3.ONE * radius, duration).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	tw.tween_property(m, "albedo_color:a", 0.0, duration)
	tw.chain().tween_callback(s.queue_free)


## Zackiger Blitz zwischen mehreren Punkten.
static func lightning(parent: Node, points: Array[Vector3], color: Color) -> void:
	if points.size() < 2:
		return
	var root := Node3D.new()
	parent.add_child(root)
	var m := glow_mat(color, 1.0)
	var core := glow_mat(Color(1, 1, 1), 1.0)
	for i in points.size() - 1:
		var a: Vector3 = points[i]
		var b: Vector3 = points[i + 1]
		var steps := 4
		var prev := a
		for s in steps:
			var t := float(s + 1) / steps
			var nxt := a.lerp(b, t)
			if s < steps - 1:
				nxt += Vector3(randf_range(-0.25, 0.25), randf_range(-0.2, 0.2), randf_range(-0.25, 0.25))
			_segment(root, prev, nxt, 0.07, m)
			_segment(root, prev, nxt, 0.025, core)
			prev = nxt
	var tw := root.create_tween()
	tw.tween_property(m, "albedo_color:a", 0.0, 0.18)
	tw.tween_callback(root.queue_free)
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA


static func _segment(parent: Node3D, a: Vector3, b: Vector3, thickness: float, material: Material) -> void:
	var length := a.distance_to(b)
	if length < 0.001:
		return
	var seg := inst(unit_box(), material)
	parent.add_child(seg)
	seg.global_position = (a + b) * 0.5
	seg.look_at(b, Vector3.UP if absf((b - a).normalized().y) < 0.95 else Vector3.RIGHT)
	seg.scale = Vector3(thickness, thickness, length)
