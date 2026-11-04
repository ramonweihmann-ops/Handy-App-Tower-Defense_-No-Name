class_name FxP
extends RefCounted
## Kampfeffekte als Partikel (Versuch neben „Bisher“ und den Bildfolgen von ChatGPT, FxSprite). Nicht übernommen
## (04.11.2026: Bildfolgen abgeschwächt sind Standard), nur noch mit dem Testschalter --fx-partikel erreichbar.
## Alles aus weichen, runden Leuchtpunkten und Rauchflocken, ohne Bilddateien. Ein eigener kleiner Rechner (Runner)
## bewegt die Teilchen mit eigenem Zufall (Godots Partikel würfeln mit dem Zufall des Kampfes und würden den
## Spielverlauf verändern) und zeichnet alle in zwei Sammel-Zeichnungen (MultiMesh: Leuchten addiert, Rauch gemischt).
## Farben je Held, Größen dezent, damit die Gegner sichtbar bleiben.

## Farben je Held (Präfix wie bei den Bildfolgen): Kern, Rand
const COLORS := {
	"dusty_jo": [Color(1.0, 0.92, 0.55), Color(1.0, 0.6, 0.15)],
	"iska": [Color(1.0, 0.95, 0.6), Color(1.0, 0.7, 0.2)],
	"brocken": [Color(1.0, 0.85, 0.45), Color(1.0, 0.4, 0.1)],
	"volta": [Color(0.85, 0.95, 1.0), Color(0.35, 0.65, 1.0)],
	"kalle": [Color(0.9, 1.0, 1.0), Color(0.45, 0.9, 1.0)],
	"margot": [Color(1.0, 0.9, 0.55), Color(1.0, 0.55, 0.15)],
	"lynx": [Color(1.0, 1.0, 0.85), Color(1.0, 0.8, 0.3)],
	"fritzi": [Color(1.0, 0.85, 0.35), Color(1.0, 0.3, 0.05)],
	"fuenkchen": [Color(1.0, 0.9, 1.0), Color(0.75, 0.45, 1.0)],
	"pip": [Color(0.85, 1.0, 1.0), Color(0.3, 0.9, 0.95)],
	"rollo": [Color(1.0, 0.9, 0.6), Color(1.0, 0.55, 0.2)],
	"nova": [Color(0.95, 0.85, 1.0), Color(0.6, 0.3, 1.0)],
}

static var enabled := false
## Höchstzahl gleichzeitiger Teilchen je Art (Leuchten, Rauch)
const CAP := 700
## Alle Teilchen so viel größer als in den Effekten angegeben (Figuren stehen im Kampf vergrößert)
const SIZE := 2.4
static var _runner: Runner
static var _mats := {}
static var _curves := {}


static func _tex() -> Texture2D:
	if not _mats.has("_tex"):
		var g := Gradient.new()
		# fester Kern, kurzer weicher Rand: liest sich als Funke/Flocke statt als verwaschener Fleck
		g.offsets = PackedFloat32Array([0.0, 0.3, 0.62, 1.0])
		g.colors = PackedColorArray([Color(1, 1, 1, 1), Color(1, 1, 1, 0.95), Color(1, 1, 1, 0.35), Color(1, 1, 1, 0)])
		var t := GradientTexture2D.new()
		t.gradient = g
		t.fill = GradientTexture2D.FILL_RADIAL
		t.fill_from = Vector2(0.5, 0.5)
		t.fill_to = Vector2(1.0, 0.5)
		t.width = 64
		t.height = 64
		_mats["_tex"] = t
	return _mats["_tex"]


## „glow“ = leuchtend (addiert), „smoke“ = Rauch (deckend gemischt)
static func _mat(kind: String) -> StandardMaterial3D:
	if not _mats.has(kind):
		var m := StandardMaterial3D.new()
		m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		m.vertex_color_use_as_albedo = true
		m.albedo_texture = _tex()
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		# auch das Leuchten gemischt statt addiert: auf der hellen Brücke würde Addieren nur ausbleichen
		m.blend_mode = BaseMaterial3D.BLEND_MODE_MIX
		m.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
		m.billboard_keep_scale = true
		m.no_depth_test = true
		m.disable_receive_shadows = true
		_mats[kind] = m
	return _mats[kind]


## Größe über die Lebenszeit (0..1 → Faktor): „out“ schrumpft, „grow“ wächst, „pop“ wächst schnell und schrumpft
static func size_at(curve: int, t: float) -> float:
	match curve:
		1:
			return 0.35 + 0.65 * t
		2:
			return 0.3 + 0.7 * (t / 0.25) if t < 0.25 else 1.0 - 0.85 * (t - 0.25) / 0.75
		_:
			return 1.0 - t


static func colors(style: String) -> Array:
	return COLORS.get(style, [Color(1.0, 0.95, 0.7), Color(1.0, 0.6, 0.2)])


## Der Rechner hängt am Kampf (eine Instanz je Kampf), zeichnet alle Teilchen in zwei MultiMeshes
static func _r(parent: Node) -> Runner:
	if not enabled:
		return null
	if is_instance_valid(_runner) and _runner.is_inside_tree():
		return _runner
	var b: Node = parent
	while b and not b is Battle:
		b = b.get_parent()
	if b == null:
		return null
	_runner = Runner.new()
	b.add_child(_runner)
	return _runner


## Teilchen ausstoßen. o: amount, life, speed [min,max], dir, spread (Grad), gravity, size [min,max], curve
## („out“/„grow“/„pop“), a, b (Farben), end_alpha, kind („glow“/„smoke“), damping, box (Ausdehnung, mit look
## ausgerichtet), ring (Radius), sphere (Radius), radial, tangential, explosive (<1: über die Lebenszeit verteilt)
static func emit(parent: Node, pos: Vector3, o: Dictionary) -> void:
	var r := _r(parent)
	if r:
		r.spawn(pos, o)


## Dauer-Ausstoß an einem Knoten (Spur hinter Geschossen, Triebwerk); endet mit dem Knoten. rate = Teilchen/s
static func stream(node: Node3D, rate: float, o: Dictionary) -> void:
	var r := _r(node)
	if r:
		r.streams.append({"node": node, "rate": rate, "acc": 0.0, "o": o})


class Runner:
	extends Node3D
	var rng := RandomNumberGenerator.new()
	var mm := {}          # Art -> MultiMesh
	var parts := {}       # Art -> Array von Teilchen (Dictionary)
	var streams: Array = []

	func _ready() -> void:
		rng.seed = 4242
		for kind in ["smoke", "glow"]:
			var m := MultiMesh.new()
			m.transform_format = MultiMesh.TRANSFORM_3D
			m.use_colors = true
			var q := QuadMesh.new()
			q.size = Vector2.ONE
			m.mesh = q
			m.instance_count = CAP
			m.visible_instance_count = 0
			var mi := MultiMeshInstance3D.new()
			mi.multimesh = m
			mi.material_override = FxP._mat(kind)
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			mi.custom_aabb = AABB(Vector3(-60, -20, -80), Vector3(120, 60, 160))
			add_child(mi)
			mm[kind] = m
			parts[kind] = []

	func _rand_dir(dir: Vector3, spread_deg: float) -> Vector3:
		var d := dir.normalized() if dir.length() > 0.0001 else Vector3.UP
		if spread_deg >= 179.0:
			var v := Vector3(rng.randf_range(-1, 1), rng.randf_range(-1, 1), rng.randf_range(-1, 1))
			return v.normalized() if v.length() > 0.001 else Vector3.UP
		var ang := deg_to_rad(spread_deg) * sqrt(rng.randf())
		var perp := d.cross(Vector3.UP if absf(d.y) < 0.95 else Vector3.RIGHT).normalized()
		perp = perp.rotated(d, rng.randf() * TAU)
		return (d * cos(ang) + perp * sin(ang)).normalized()

	func spawn(pos: Vector3, o: Dictionary) -> void:
		var kind := str(o.get("kind", "glow"))
		var list: Array = parts[kind]
		var n := int(o.get("amount", 8))
		if list.size() + n > CAP:
			n = CAP - list.size()
		if n <= 0:
			return
		var life := float(o.get("life", 0.4))
		var sp: Array = o.get("speed", [1.0, 3.0])
		var sz: Array = o.get("size", [0.2, 0.35])
		var curve: int = {"out": 0, "grow": 1, "pop": 2}.get(str(o.get("curve", "out")), 0)
		var explosive := float(o.get("explosive", 0.95))
		var basis := Basis.IDENTITY
		if o.has("look"):
			var to: Vector3 = o["look"]
			if to.distance_to(pos) > 0.01:
				basis = Basis.looking_at(to - pos, Vector3.UP if absf((to - pos).normalized().y) < 0.95 else Vector3.RIGHT)
		for k in n:
			var p := pos
			if o.has("box"):
				var e: Vector3 = o["box"]
				p += basis * Vector3(rng.randf_range(-e.x, e.x), rng.randf_range(-e.y, e.y), rng.randf_range(-e.z, e.z))
			elif o.has("ring"):
				var a := rng.randf() * TAU
				p += Vector3(cos(a), 0, sin(a)) * float(o["ring"]) * rng.randf_range(0.8, 1.0)
			elif o.has("sphere"):
				p += _rand_dir(Vector3.UP, 180.0) * float(o["sphere"]) * rng.randf()
			var v := _rand_dir(o.get("dir", Vector3.UP), float(o.get("spread", 180.0))) * rng.randf_range(float(sp[0]), float(sp[1]))
			list.append({"p": p, "v": v, "c": pos, "age": -rng.randf() * life * (1.0 - explosive), "life": life,
				"s": rng.randf_range(float(sz[0]), float(sz[1])) * SIZE, "cv": curve, "a": o.get("a", Color.WHITE),
				"b": o.get("b", Color(1, 0.6, 0.2)), "ea": float(o.get("end_alpha", 0.0)), "g": o.get("gravity", Vector3.ZERO),
				"dmp": float(o.get("damping", 0.0)), "rad": float(o.get("radial", 0.0)), "tan": float(o.get("tangential", 0.0))})

	func _process(delta: float) -> void:
		# Dauer-Ausstöße
		for i in range(streams.size() - 1, -1, -1):
			var st: Dictionary = streams[i]
			var obj: Variant = st["node"]
			if not is_instance_valid(obj) or not (obj as Node3D).is_inside_tree():
				streams.remove_at(i)
				continue
			var node := obj as Node3D
			st["acc"] = float(st["acc"]) + delta * float(st["rate"])
			var o: Dictionary = st["o"].duplicate()
			var n := int(st["acc"])
			if n > 0:
				st["acc"] = float(st["acc"]) - n
				o["amount"] = n
				o["explosive"] = 1.0
				spawn(node.global_position, o)
		# Teilchen bewegen und in die MultiMeshes schreiben
		for kind in parts.keys():
			var list: Array = parts[kind]
			var m: MultiMesh = mm[kind]
			var w := 0
			var keep: Array = []
			for q in list:
				q["age"] = float(q["age"]) + delta
				var age: float = q["age"]
				if age >= float(q["life"]):
					continue
				keep.append(q)
				if age < 0.0:
					continue
				var v: Vector3 = q["v"]
				var p: Vector3 = q["p"]
				if float(q["rad"]) != 0.0 or float(q["tan"]) != 0.0:
					var out: Vector3 = p - (q["c"] as Vector3)
					out.y = 0.0
					if out.length() > 0.001:
						var on := out.normalized()
						v += on * float(q["rad"]) * delta + Vector3(-on.z, 0, on.x) * float(q["tan"]) * delta
				v += (q["g"] as Vector3) * delta
				if float(q["dmp"]) > 0.0:
					v = v.move_toward(Vector3.ZERO, float(q["dmp"]) * delta)
				p += v * delta
				q["v"] = v
				q["p"] = p
				var t := age / float(q["life"])
				var col: Color
				var a: Color = q["a"]
				var b: Color = q["b"]
				if t < 0.45:
					col = a.lerp(b, t / 0.45)
				else:
					col = b.lerp(Color(b.r, b.g, b.b, float(q["ea"])), (t - 0.45) / 0.55)
				var sc := float(q["s"]) * FxP.size_at(int(q["cv"]), t)
				m.set_instance_transform(w, Transform3D(Basis.IDENTITY.scaled(Vector3.ONE * maxf(0.001, sc)), p))
				m.set_instance_color(w, col)
				w += 1
			parts[kind] = keep
			m.visible_instance_count = w


# --- Effekte -------------------------------------------------------------------------------------

## Mündungsfeuer: kurzer Funkenstoß in Schussrichtung (Brocken: Rauchstoß nach hinten)
static func muzzle(parent: Node, style: String, pos: Vector3, dir: Vector3) -> void:
	var c := colors(style)
	var d := dir.normalized()
	if style == "brocken":
		emit(parent, pos, {"amount": 6, "life": 0.35, "speed": [1.0, 2.2], "dir": -d, "spread": 25.0, "size": [0.3, 0.5],
			"curve": "grow", "a": Color(0.85, 0.8, 0.9, 0.6), "b": Color(0.4, 0.38, 0.5, 0.35), "kind": "smoke", "damping": 3.0})
		d = -d
	var big := style in ["margot", "rollo", "brocken"]
	emit(parent, pos + d * 0.15, {"amount": 1, "life": 0.07, "speed": [0.0, 0.0], "size": [0.3, 0.3] if not big else [0.45, 0.45],
		"curve": "pop", "a": c[0], "b": c[1]})
	emit(parent, pos, {"amount": 6 if big else 4, "life": 0.1, "speed": [2.0, 5.0], "dir": d, "spread": 18.0 if not big else 32.0,
		"size": [0.18, 0.32] if not big else [0.25, 0.45], "a": c[0], "b": c[1]})


## Leuchtspur an einem Geschoss (fliegt mit, bleibt hinter ihm zurück)
static func trail(node: Node3D, style: String, rocket := false) -> void:
	var c := colors(style)
	if rocket:
		stream(node, 32.0, {"life": 0.45, "speed": [0.1, 0.4], "spread": 180.0, "size": [0.18, 0.3], "curve": "grow",
			"a": Color(0.8, 0.78, 0.9, 0.5), "b": Color(0.35, 0.33, 0.45, 0.3), "kind": "smoke"})
	stream(node, 60.0 if not rocket else 70.0, {"life": 0.14, "speed": [0.0, 0.2], "spread": 180.0,
		"size": [0.14, 0.22] if not rocket else [0.22, 0.32], "a": c[0], "b": c[1]})


## Einschlag: kleine Funken in der Farbe des Helden
static func impact(parent: Node, style: String, pos: Vector3) -> void:
	var c := colors(style)
	emit(parent, pos, {"amount": 7, "life": 0.28, "speed": [1.5, 3.5], "spread": 180.0, "gravity": Vector3(0, -6, 0),
		"size": [0.08, 0.16], "a": c[0], "b": c[1]})
	emit(parent, pos, {"amount": 1, "life": 0.12, "speed": [0.0, 0.0], "size": [0.5, 0.5], "curve": "pop", "a": c[0], "b": c[1]})


## Strahl zwischen a und b: eine Kette von Leuchtpunkten (Volta, Kalle, Fünkchen)
static func beam(parent: Node, style: String, a: Vector3, b: Vector3) -> void:
	var c := colors(style)
	var len := a.distance_to(b)
	if len < 0.1:
		return
	emit(parent, a.lerp(b, 0.5), {"amount": clampi(int(len * 5.0), 6, 40), "life": 0.2, "speed": [0.0, 0.3], "spread": 180.0,
		"box": Vector3(0.04, 0.04, len * 0.5), "look": b, "size": [0.13, 0.22], "a": c[0], "b": c[1], "explosive": 1.0})


## Flammenstoß (Fritzi): schmaler Kegel vom Helden zum Ziel, dezent
static func flame(parent: Node, from: Vector3, to: Vector3) -> void:
	var len := from.distance_to(to)
	var d := (to - from).normalized()
	if len < 0.1:
		return
	emit(parent, from.lerp(to, 0.5), {"amount": clampi(int(len * 3.5), 10, 28), "life": 0.3, "speed": [0.6, 1.4], "dir": d,
		"spread": 12.0, "box": Vector3(0.08, 0.05, len * 0.45), "look": to, "size": [0.13, 0.28], "curve": "grow",
		"a": Color(1.0, 0.85, 0.35, 0.75), "b": Color(1.0, 0.32, 0.05, 0.5), "explosive": 0.6})
	emit(parent, to, {"amount": 5, "life": 0.4, "speed": [0.4, 1.2], "dir": Vector3.UP, "spread": 30.0, "size": [0.2, 0.35],
		"curve": "pop", "a": Color(1.0, 0.75, 0.3, 0.8), "b": Color(0.9, 0.2, 0.05, 0.5)})


## Schwerkraftfeld (Nova): lila Ring, der sich zur Mitte zieht und dreht
static func vortex(parent: Node, center: Vector3, radius: float) -> void:
	emit(parent, center + Vector3(0, 0.2, 0), {"amount": 22, "life": 0.55, "speed": [0.0, 0.3], "spread": 180.0, "ring": radius,
		"radial": -radius * 7.0, "tangential": radius * 6.0, "size": [0.14, 0.24], "a": Color(0.95, 0.85, 1.0), "b": Color(0.6, 0.3, 1.0),
		"explosive": 0.9})


## Kritischer Treffer: heller Funkenstern
static func crit(parent: Node, pos: Vector3) -> void:
	emit(parent, pos, {"amount": 14, "life": 0.28, "speed": [3.0, 5.5], "spread": 180.0, "size": [0.09, 0.15], "damping": 6.0,
		"a": Color(1.0, 1.0, 0.85), "b": Color(1.0, 0.75, 0.2)})
	emit(parent, pos, {"amount": 1, "life": 0.16, "speed": [0.0, 0.0], "size": [0.7, 0.7], "curve": "pop",
		"a": Color(1.0, 0.95, 0.7), "b": Color(1.0, 0.7, 0.2)})


## Explosion: heller Kern, Feuerball, dunkler Rauch, Funken und Druckring am Boden
static func explosion(parent: Node, pos: Vector3, radius: float) -> void:
	var r := maxf(1.0, radius)
	emit(parent, pos + Vector3(0, 0.4, 0), {"amount": 1, "life": 0.14, "speed": [0.0, 0.0], "size": [r * 0.75, r * 0.75], "curve": "pop",
		"a": Color(1.0, 0.98, 0.9), "b": Color(1.0, 0.7, 0.3)})
	emit(parent, pos + Vector3(0, 0.4, 0), {"amount": 24, "life": 0.5, "speed": [r * 1.2, r * 2.6], "spread": 180.0, "sphere": r * 0.2,
		"gravity": Vector3(0, 1.5, 0), "damping": r * 4.0, "size": [r * 0.16, r * 0.3], "curve": "pop",
		"a": Color(1.0, 0.85, 0.4), "b": Color(0.92, 0.25, 0.05, 0.75), "explosive": 0.9})
	emit(parent, pos + Vector3(0, 0.5, 0), {"amount": 10, "life": 0.95, "speed": [0.4, 1.2], "dir": Vector3.UP, "spread": 60.0,
		"sphere": r * 0.35, "gravity": Vector3(0, 0.8, 0), "damping": 0.8, "size": [r * 0.4, r * 0.7], "curve": "grow",
		"a": Color(0.35, 0.28, 0.32, 0.75), "b": Color(0.18, 0.15, 0.2, 0.45), "kind": "smoke", "explosive": 0.8})
	emit(parent, pos + Vector3(0, 0.3, 0), {"amount": 14, "life": 0.55, "speed": [r * 2.5, r * 4.5], "spread": 75.0, "dir": Vector3.UP,
		"gravity": Vector3(0, -12, 0), "size": [0.08, 0.14], "a": Color(1.0, 0.95, 0.7), "b": Color(1.0, 0.5, 0.1)})
	emit(parent, pos + Vector3(0, 0.08, 0), {"amount": 18, "life": 0.35, "speed": [0.0, 0.0], "ring": r * 0.3, "radial": r * 22.0,
		"size": [0.16, 0.24], "a": Color(1.0, 0.85, 0.5, 0.8), "b": Color(1.0, 0.45, 0.15, 0.4), "explosive": 1.0})


## Gegner besiegt: Glibber-Tropfen in seiner Farbe, Boss größer mit Lichtring
static func death(parent: Node, pos: Vector3, color: Color, size: float, boss: bool) -> void:
	var k := clampf(size, 0.8, 2.2) * (1.15 if boss else 1.0)
	emit(parent, pos, {"amount": 14 if not boss else 24, "life": 0.6, "speed": [1.5 * k, 3.5 * k], "spread": 180.0,
		"gravity": Vector3(0, -9, 0), "size": [0.1 * k, 0.2 * k], "a": color.lerp(Color.WHITE, 0.35), "b": color, "end_alpha": 0.0,
		"kind": "smoke"})
	emit(parent, pos, {"amount": 1, "life": 0.16, "speed": [0.0, 0.0], "size": [0.4 * k, 0.4 * k], "curve": "pop",
		"a": color.lerp(Color.WHITE, 0.6), "b": color})
	if boss:
		emit(parent, pos, {"amount": 26, "life": 0.6, "speed": [0.0, 0.0], "ring": 0.6, "radial": 18.0, "size": [0.25, 0.4],
			"a": Color(1.0, 0.95, 0.8), "b": color, "explosive": 1.0})


## Zauntreffer: blaue Funken am Energiezaun
static func fence_hit(parent: Node, pos: Vector3) -> void:
	emit(parent, pos, {"amount": 7, "life": 0.3, "speed": [1.5, 3.0], "dir": Vector3(0, 0.6, 1), "spread": 70.0,
		"gravity": Vector3(0, -5, 0), "size": [0.08, 0.15], "a": Color(0.85, 1.0, 1.0), "b": Color(0.3, 0.8, 1.0)})
	emit(parent, pos, {"amount": 1, "life": 0.12, "speed": [0.0, 0.0], "size": [0.45, 0.45], "curve": "pop",
		"a": Color(0.85, 1.0, 1.0, 0.9), "b": Color(0.3, 0.75, 1.0, 0.6)})


## Heilung am Zaun: grüne Lichter steigen auf (Medipack, Pip)
static func heal(parent: Node, pos: Vector3, strong := true) -> void:
	emit(parent, pos, {"amount": 22 if strong else 8, "life": 0.9, "speed": [0.8, 1.8], "dir": Vector3.UP, "spread": 20.0,
		"box": Vector3(1.0 if strong else 0.4, 0.05, 0.25), "size": [0.13, 0.24], "curve": "pop",
		"a": Color(0.9, 1.0, 0.85), "b": Color(0.25, 0.95, 0.4), "explosive": 0.55})
	if strong:
		emit(parent, pos + Vector3(0, 0.05, 0), {"amount": 20, "life": 0.45, "speed": [0.0, 0.0], "ring": 0.3, "radial": 9.0,
			"size": [0.12, 0.18], "a": Color(0.85, 1.0, 0.8, 0.9), "b": Color(0.3, 0.95, 0.45, 0.5), "explosive": 1.0})


## Raumjäger für den Luftangriff: flacher Pfeilflügler (lila/weiß/gelb) mit zwei Triebwerksspuren
static func jet(parent: Node) -> Node3D:
	var j := Node3D.new()
	parent.add_child(j)
	j.add_child(_wedge(Vector3(1.7, 1.3, 0.06), Color(0.58, 0.42, 0.98), Vector3(0, 0, 0.1)))
	j.add_child(_wedge(Vector3(0.42, 1.75, 0.2), Color(0.93, 0.9, 1.0), Vector3(0, 0.05, -0.05)))
	var cockpit := Fx.inst(Fx.unit_sphere(), Fx.shared_glow(Color(1.0, 0.85, 0.3)))
	cockpit.scale = Vector3(0.14, 0.1, 0.3)
	cockpit.position = Vector3(0, 0.14, -0.15)
	j.add_child(cockpit)
	for x in [-0.3, 0.3]:
		var tail := Node3D.new()
		tail.position = Vector3(x, 0, 0.72)
		j.add_child(tail)
		stream(tail, 40.0, {"life": 0.22, "speed": [0.2, 0.6], "dir": Vector3(0, 0, 1), "spread": 10.0,
			"size": [0.14, 0.24], "a": Color(0.9, 0.97, 1.0), "b": Color(0.45, 0.55, 1.0)})
	return j


## Keil (Dreiecksprisma), flach gelegt, Spitze nach vorn (−Z); size = Spannweite, Länge, Dicke
static func _wedge(size: Vector3, color: Color, pos: Vector3) -> MeshInstance3D:
	var key := "wedge:%s" % str(size)
	var mesh: Mesh = Fx.shared_mesh(key, func() -> Mesh:
		var pm := PrismMesh.new()
		pm.size = size
		return pm)
	var mi := Fx.inst(mesh, Fx.shared_glow(color))
	mi.rotation = Vector3(-PI / 2.0, 0, 0)
	mi.position = pos
	return mi
