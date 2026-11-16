class_name Fx3D
extends RefCounted
## Räumliche Schusseffekte (Konzept docs/HELDEN_UND_SCHUESSE.md): Was fliegt, ist ein kleines 3D-Objekt,
## was leuchtet, raucht oder brennt, sind Partikel. Ersetzt die flachen Bildfolgen bei Brocken (Rakete),
## Volta (Blitz) und Fritzi (Flammen), die von schräg oben wie Striche wirkten.

## Champions mit neuen 3D-Schüssen (Effekt-Stil laut Hero.FX_STYLE)
const STYLES := ["brocken", "volta", "fritzi"]
## Größe der Rakete (aus der Spielkamera muss sie deutlich als Rakete erkennbar sein)
const ROCKET_SCALE := 2.8


static func has(style: String) -> bool:
	return style in STYLES


# --- Brocken: massive Rakete mit Feuerstrahl und Rauchfahne -------------------------------------------

## Baut die Rakete an das Geschoss (zeigt mit -Z nach vorn, wie look_at es dreht). Gibt den Rauch zurück,
## damit das Geschoss ihn beim Einschlag stehen lassen kann.
static func build_rocket(p: Node3D) -> CPUParticles3D:
	var body_mat := Fx.mat(Color(0.86, 0.2, 0.16), 0.15, 0.2, 0.45)
	var band_mat := Fx.mat(Color(0.95, 0.93, 0.88), 0.1, 0.0, 0.5)
	var metal := Fx.mat(Color(0.62, 0.65, 0.7), 0.05, 0.7, 0.35)
	var dark := Fx.mat(Color(0.25, 0.26, 0.3), 0.0, 0.4, 0.5)
	var rocket := Node3D.new()
	rocket.name = "Rakete"
	rocket.scale = Vector3.ONE * ROCKET_SCALE
	p.add_child(rocket)
	var body := Fx.cylinder(0.11, 0.11, 0.56, body_mat, 12)
	body.rotation.x = PI * 0.5
	rocket.add_child(body)
	var band := Fx.cylinder(0.115, 0.115, 0.08, band_mat, 12)
	band.rotation.x = PI * 0.5
	band.position.z = -0.12
	rocket.add_child(band)
	var nose := Fx.cylinder(0.0, 0.11, 0.24, metal, 12)
	nose.rotation.x = -PI * 0.5
	nose.position.z = -0.4
	rocket.add_child(nose)
	var nozzle := Fx.cylinder(0.08, 0.06, 0.1, dark, 10)
	nozzle.rotation.x = PI * 0.5
	nozzle.position.z = 0.33
	rocket.add_child(nozzle)
	for k in 4:
		var fin := Fx.box(Vector3(0.025, 0.2, 0.18), dark)
		var a := TAU * k / 4.0 + PI * 0.25
		fin.position = Vector3(cos(a) * 0.15, sin(a) * 0.15, 0.2)
		fin.rotation.z = a - PI * 0.5
		rocket.add_child(fin)
	# Feuerstrahl am Heck: zwei Leuchtkegel (außen orange, innen gelb), flackern über rocket_tick
	var outer := Fx.cylinder(0.0, 0.11, 0.5, Fx.shared_glow(Color(1.0, 0.45, 0.1), 0.85), 10)
	outer.rotation.x = PI * 0.5
	outer.position.z = 0.62
	outer.name = "Flamme"
	rocket.add_child(outer)
	var inner := Fx.cylinder(0.0, 0.06, 0.3, Fx.shared_glow(Color(1.0, 0.95, 0.6)), 8)
	inner.rotation.x = PI * 0.5
	inner.position.z = 0.5
	inner.name = "Kern"
	rocket.add_child(inner)
	# Rauchfahne in Weltkoordinaten: bleibt in der Luft stehen, während die Rakete weiterfliegt
	var smoke := CPUParticles3D.new()
	smoke.local_coords = false
	smoke.amount = 48
	smoke.lifetime = 0.9
	smoke.mesh = _puff_mesh(0.12)
	smoke.direction = Vector3(0, 1, 0)
	smoke.spread = 30.0
	smoke.initial_velocity_min = 0.2
	smoke.initial_velocity_max = 0.6
	smoke.gravity = Vector3(0, 0.6, 0)
	smoke.scale_amount_min = 0.7
	smoke.scale_amount_max = 1.2
	smoke.scale_amount_curve = _curve([Vector2(0, 0.5), Vector2(0.4, 1.0), Vector2(1, 1.6)])
	smoke.color_ramp = _ramp([Color(1.0, 0.8, 0.5, 0.9), Color(0.75, 0.74, 0.76, 0.75), Color(0.55, 0.55, 0.6, 0.0)], [0.0, 0.25, 1.0])
	smoke.position.z = 0.55
	rocket.add_child(smoke)
	smoke.emitting = true
	return smoke


## Pro Bild: Rakete dreht sich um die Längsachse, der Feuerstrahl flackert
static func rocket_tick(p: Node3D, t: float) -> void:
	var r := p.get_node_or_null("Rakete") as Node3D
	if r == null:
		return
	r.rotation.z = t * 9.0
	var f := r.get_node_or_null("Flamme") as Node3D
	if f:
		f.scale = Vector3(1.0, 0.8 + 0.4 * absf(sin(t * 47.0)), 1.0)


## Rauch beim Einschlag aus der Rakete lösen und ausklingen lassen
static func release_smoke(smoke: CPUParticles3D, battle: Node) -> void:
	if smoke == null or not is_instance_valid(smoke):
		return
	var gp := smoke.global_transform
	smoke.get_parent().remove_child(smoke)
	battle.add_child(smoke)
	smoke.global_transform = gp
	smoke.emitting = false
	battle.get_tree().create_timer(smoke.lifetime + 0.2, false).timeout.connect(smoke.queue_free)


## Rückstoß-Rauch an der Mündung (nach hinten)
static func rocket_launch(battle: Node, from: Vector3, dir: Vector3) -> void:
	var back := -dir.normalized()
	var p := _one_shot(battle, from, 14, 0.55)
	p.mesh = _puff_mesh(0.3)
	p.direction = back
	p.spread = 35.0
	p.initial_velocity_min = 1.5
	p.initial_velocity_max = 3.2
	p.damping_min = 3.0
	p.damping_max = 5.0
	p.scale_amount_curve = _curve([Vector2(0, 0.6), Vector2(1, 1.8)])
	p.color_ramp = _ramp([Color(1.0, 0.85, 0.5, 0.9), Color(0.8, 0.8, 0.82, 0.6), Color(0.6, 0.6, 0.65, 0.0)], [0.0, 0.2, 1.0])
	p.emitting = true
	Fx.flash(battle, from + dir.normalized() * 0.2, Color(1.0, 0.75, 0.3), 0.45, 0.12)


# --- Volta: gezackter, flackernder Blitz ---------------------------------------------------------------

## Blitz zwischen den Punkten (erster Punkt = Gerät). Drei Lagen (Schein, Farbe, weißer Kern), Abzweigungen,
## flackert dreimal mit neuer Form und verblasst; an jedem Treffer ein Funkenregen.
static func lightning(battle: Node, points: Array[Vector3], col: Color) -> void:
	if points.size() < 2:
		return
	var root := Node3D.new()
	battle.add_child(root)
	var halo := Fx.glow_mat(col.lerp(Color(0.3, 0.25, 1.0), 0.5), 0.5)
	var mid := Fx.glow_mat(col.lerp(Color(1, 1, 1), 0.35), 1.0)
	var core := Fx.glow_mat(Color(1, 1, 1), 1.0)
	for m in [halo, mid, core]:
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	var draw := func() -> void:
		for c in root.get_children():
			c.queue_free()
		for i in points.size() - 1:
			var n := clampi(int(points[i].distance_to(points[i + 1]) / 0.6), 6, 22)
			var path := _zigzag(points[i], points[i + 1], n, 0.45)
			_polyline(root, path, 0.42, halo)
			_polyline(root, path, 0.15, mid)
			_polyline(root, path, 0.06, core)
			# eine kurze Abzweigung je Strecke
			var k := Fx.vis_rng.randi_range(2, path.size() - 2)
			var tip: Vector3 = path[k] + Vector3(Fx.vis_rng.randf_range(-0.7, 0.7), Fx.vis_rng.randf_range(-0.1, 0.5), Fx.vis_rng.randf_range(-0.7, 0.7))
			var br := _zigzag(path[k], tip, 3, 0.15)
			_polyline(root, br, 0.3, halo)
			_polyline(root, br, 0.1, mid)
	draw.call()
	for i in range(1, points.size()):
		Fx.burst(battle, points[i], col.lerp(Color(1, 1, 1), 0.4), 16, 6.0, 0.09, 0.4)
		Fx.flash(battle, points[i], col.lerp(Color(1, 1, 1), 0.5), 1.1, 0.22)
	Fx.flash(battle, points[0], col.lerp(Color(1, 1, 1), 0.5), 0.6, 0.15)
	var tw := root.create_tween()
	tw.tween_interval(0.08)
	tw.tween_callback(draw)
	tw.tween_interval(0.08)
	tw.tween_callback(draw)
	tw.tween_interval(0.08)
	tw.set_parallel(true)
	tw.tween_property(halo, "albedo_color:a", 0.0, 0.14)
	tw.tween_property(mid, "albedo_color:a", 0.0, 0.14)
	tw.tween_property(core, "albedo_color:a", 0.0, 0.14)
	tw.chain().tween_callback(root.queue_free)


static func _zigzag(a: Vector3, b: Vector3, steps: int, jitter: float) -> Array[Vector3]:
	var out: Array[Vector3] = [a]
	var side := (b - a).cross(Vector3.UP).normalized()
	var sign := 1.0 if Fx.vis_rng.randf() < 0.5 else -1.0
	for s in range(1, steps):
		var t := float(s) / steps
		var j := jitter * (0.35 + 0.65 * sin(t * PI))
		sign = -sign
		out.append(a.lerp(b, t) + side * sign * Fx.vis_rng.randf_range(j * 0.3, j) + Vector3(0, Fx.vis_rng.randf_range(-j, j) * 0.4, 0))
	out.append(b)
	return out


static func _polyline(root: Node3D, path: Array[Vector3], thickness: float, m: Material) -> void:
	for i in path.size() - 1:
		Fx._segment(root, path[i], path[i + 1], thickness, m)


# --- Fritzi: echte Flammen im Kegel --------------------------------------------------------------------

## Flammenstoß von der Waffe zum Ziel: Feuerteilchen wachsen, werden von Gelb über Orange zu dunklem Rot und
## verglühen; am Ziel züngeln Flammen hoch. Reine Optik, der Schaden ist schon verrechnet.
static func flame_burst(battle: Node, from: Vector3, to: Vector3, radius: float) -> void:
	var d := to - from
	var dist := d.length()
	var p := _one_shot(battle, from, 70, 0.45)
	p.explosiveness = 0.35
	p.mesh = _puff_mesh(0.22)
	p.direction = d.normalized()
	p.spread = clampf(rad_to_deg(atan2(radius * 0.8, maxf(dist, 0.5))), 6.0, 22.0)
	p.initial_velocity_min = dist / 0.42 * 0.85
	p.initial_velocity_max = dist / 0.42 * 1.1
	p.gravity = Vector3(0, 2.0, 0)
	p.scale_amount_min = 0.8
	p.scale_amount_max = 1.4
	p.scale_amount_curve = _curve([Vector2(0, 0.4), Vector2(0.5, 2.0), Vector2(1, 3.0)])
	p.color_ramp = _ramp([Color(1.0, 0.97, 0.7, 1.0), Color(1.0, 0.65, 0.15, 0.95), Color(0.95, 0.25, 0.05, 0.7), Color(0.35, 0.1, 0.05, 0.0)], [0.0, 0.25, 0.65, 1.0])
	p.emitting = true
	# Flammen am Ziel
	battle.get_tree().create_timer(0.3, false).timeout.connect(func() -> void:
		if not is_instance_valid(battle):
			return
		var q := _one_shot(battle, to + Vector3(0, -0.2, 0), 26, 0.55)
		q.explosiveness = 0.4
		q.mesh = _puff_mesh(0.2)
		q.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
		q.emission_sphere_radius = radius * 0.45
		q.direction = Vector3.UP
		q.spread = 20.0
		q.initial_velocity_min = 1.2
		q.initial_velocity_max = 2.6
		q.gravity = Vector3(0, 1.5, 0)
		q.scale_amount_curve = _curve([Vector2(0, 0.8), Vector2(1, 0.1)])
		q.color_ramp = _ramp([Color(1.0, 0.9, 0.5, 1.0), Color(1.0, 0.45, 0.1, 0.9), Color(0.6, 0.15, 0.05, 0.0)], [0.0, 0.4, 1.0])
		q.emitting = true)


# --- Hilfen ---------------------------------------------------------------------------------------------

static func _one_shot(parent: Node, pos: Vector3, amount: int, life: float) -> CPUParticles3D:
	var p := CPUParticles3D.new()
	p.one_shot = true
	p.explosiveness = 0.9
	p.amount = amount
	p.lifetime = life
	p.local_coords = false
	parent.add_child(p)
	p.global_position = pos
	parent.get_tree().create_timer(life + 0.4, false).timeout.connect(p.queue_free)
	return p


## Weiche Kugel für Rauch und Feuer: unbeleuchtet, Farbe und Deckkraft aus der Farbrampe der Teilchen
static func _puff_mesh(r: float) -> Mesh:
	return Fx.shared_mesh("fx3d_puff:%.2f" % r, func() -> Mesh:
		var m := SphereMesh.new()
		m.radius = r
		m.height = r * 2.0
		m.radial_segments = 8
		m.rings = 4
		var pm := StandardMaterial3D.new()
		pm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		pm.vertex_color_use_as_albedo = true
		pm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		m.material = pm
		return m)


static func _curve(pts: Array) -> Curve:
	var c := Curve.new()
	c.max_value = 4.0
	for v in pts:
		c.add_point(v)
	return c


static func _ramp(cols: Array, offs: Array) -> Gradient:
	var g := Gradient.new()
	g.offsets = PackedFloat32Array(offs)
	g.colors = PackedColorArray(cols)
	return g
