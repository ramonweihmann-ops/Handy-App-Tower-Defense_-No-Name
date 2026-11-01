class_name LoadingScreen
extends Control
## Ladebildschirm beim Start der App, nach dem Mockup „Ladebildschirm · animiert“:
## Weltraum mit Wurmloch-Wirbel, Gasplanet, ein schwebender Drache und drei Helden als echte
## 3D-Figuren, die auf ihn feuern (Mündungsblitz genau an der Waffe), dazu Titel, Sternschnuppen
## und ein Ladebalken mit Blitz-Knopf. Während er zu sehen ist, bereitet main.gd Figuren und
## Effekte vor (siehe main.gd, _warm_up), damit es später nicht ruckelt.
##
## Alle Maße stammen aus dem Mockup (390 × 844) und werden auf den Bildschirm skaliert.

const W := 390.0
const H := 844.0
const PLANET := Vector2(195, 375)
const PLANET_R := 88.0
const VIEW_PX := 512

## Die drei Helden: Modell, Waffe, Animation und Zeitfenster (läuft hin und zurück), Takt in
## Sekunden, Schussmoment (Animationszeit; liegt er am Anfang, feuert der Held bei jedem
## Umkehrpunkt), Fenster im Mockup (Rechteck, Drehpunkt, Drehung), Ziel am Drachen, Farbe.
const CREW := [
	{"id": "iska", "file": "heroes/BlueSoldier_Female", "gun": "guns/AK", "anim": "Shoot_OneHanded",
		"t0": 0.35, "t1": 0.75, "period": 1.4, "fire": 0.35, "yaw": -35.0,
		"rect": Rect2(-138.1, 318.3, 464.8, 464.8), "pivot": Vector2(201.2, 373.7), "rot": -8.0,
		"target": Vector2(150, 360), "color": Color(0.44, 0.88, 1.0)},
	{"id": "margot", "file": "heroes/Pirate_Female", "gun": "guns/Shotgun", "anim": "Victory",
		"t0": 0.45, "t1": 1.0, "period": 2.2, "fire": 0.85, "yaw": -20.0,
		"rect": Rect2(101.0, 315.4, 473.2, 473.2), "pivot": Vector2(219.4, 378.6), "rot": 8.0,
		"target": Vector2(245, 345), "color": Color(1.0, 0.6, 0.24)},
	{"id": "dusty", "file": "heroes/Cowboy_Male", "gun": "guns/Revolver", "anim": "Victory",
		"t0": 0.3, "t1": 0.75, "period": 1.9, "fire": 0.4, "yaw": 25.0,
		"rect": Rect2(-83.1, 337.4, 514.9, 514.9), "pivot": Vector2(277.9, 412.6), "rot": 0.0,
		"target": Vector2(198, 320), "color": Color(1.0, 0.83, 0.3)},
]
const DRAGON_RECT := Rect2(45, 168, 300, 300)
## Funkelnde Sterne (Kreuze) und Lichtpunkte im Mockup
const SPARKLES := [[Vector2(40, 340), 10.0, 1.7], [Vector2(350, 411), 11.0, 2.1], [Vector2(190, 188), 8.0, 1.4],
	[Vector2(300, 567), 7.0, 1.9], [Vector2(60, 47), 7.0, 2.5], [Vector2(310, 129), 9.0, 3.0]]
const GLOWS := [[Vector2(70, 250), 14.0, 2.6], [Vector2(330, 300), 18.0, 3.2], [Vector2(320, 470), 12.0, 2.2],
	[Vector2(55, 440), 16.0, 2.9], [Vector2(260, 215), 10.0, 1.9], [Vector2(120, 205), 9.0, 2.4]]
const CRACK := [Vector2(20, 750), Vector2(70, 740), Vector2(100, 758), Vector2(150, 748), Vector2(190, 766),
	Vector2(240, 752), Vector2(300, 770), Vector2(370, 756)]

var progress := 0.0
var _shown := 0.0
var _status_text := "Die Station fährt hoch …"
var _t := 0.0
var _font: Font
var _s := 1.0
var _off := Vector2.ZERO

var _bg: ColorRect
var _bg_mat: ShaderMaterial
var _back: Control
var _planet: ColorRect
var _ground: Control
var _front: Control
var _title: Control
var _title_top: Label
var _title_main: Label
var _dragon: Dictionary = {}
var _crew: Array[Dictionary] = []
var _shots: Array[Dictionary] = []  # Mündungsblitze und Leuchtspuren, die gerade zu sehen sind


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	_font = ThemeDB.fallback_font
	_bg = ColorRect.new()
	_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_bg_mat = ShaderMaterial.new()
	_bg_mat.shader = preload("res://shaders/loading_bg.gdshader")
	_bg.material = _bg_mat
	add_child(_bg)
	_back = _layer(_draw_back)
	_planet = ColorRect.new()
	_planet.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var pm := ShaderMaterial.new()
	pm.shader = preload("res://shaders/loading_planet.gdshader")
	_planet.material = pm
	add_child(_planet)
	_ground = _layer(_draw_ground)
	_front = _layer(_draw_front)

	_title = Control.new()
	_title.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_title)
	_title_top = UiKit.label("STATION AM", 22, Color(0.56, 0.91, 1.0))
	_title_top.add_theme_color_override("font_shadow_color", Color(0.04, 0.1, 0.35))
	_title_top.add_theme_color_override("font_outline_color", Color(0.04, 0.1, 0.35))
	_title.add_child(_title_top)
	_title_main = UiKit.label("WURMLOCH", 58, Color(1.0, 0.83, 0.3))
	_title_main.add_theme_color_override("font_outline_color", Color(0.72, 0.39, 0.05))
	_title_main.add_theme_color_override("font_shadow_color", Color(0.35, 0.16, 0.0))
	_title.add_child(_title_main)
	resized.connect(_layout)
	_layout()
	# Die 3D-Figuren erst nach dem ersten Bild laden, damit der Bildschirm sofort erscheint
	_build_3d.call_deferred()


func _layer(fn: Callable) -> Control:
	var c := Control.new()
	c.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	c.draw.connect(fn.bind(c))
	add_child(c)
	return c


func set_progress(value: float, status: String) -> void:
	progress = clampf(value, 0.0, 1.0)
	_status_text = status


## Mockup-Koordinaten in Bildschirm-Koordinaten
func _p(v: Vector2) -> Vector2:
	return _off + v * _s


func _layout() -> void:
	if size.x <= 0.0 or size.y <= 0.0:
		return
	_s = minf(size.x / W, size.y / H)
	_off = Vector2((size.x - W * _s) * 0.5, (size.y - H * _s) * 0.5)
	_bg_mat.set_shader_parameter("size_px", size)
	_bg_mat.set_shader_parameter("center_px", _p(PLANET))
	_bg_mat.set_shader_parameter("radius_px", PLANET_R * _s)
	var pr := PLANET_R / 0.74
	_planet.position = _p(PLANET - Vector2(pr, pr))
	_planet.size = Vector2(pr, pr) * 2.0 * _s
	_title_top.add_theme_font_size_override("font_size", int(22 * _s))
	_title_top.add_theme_constant_override("shadow_offset_y", int(2 * _s))
	_title_top.add_theme_constant_override("outline_size", int(4 * _s))
	_title_main.add_theme_font_size_override("font_size", int(58 * _s))
	_title_main.add_theme_constant_override("outline_size", int(10 * _s))
	_title_main.add_theme_constant_override("shadow_offset_y", int(6 * _s))
	_title.position = _p(Vector2(0, 92))
	_title.size = Vector2(W, 100) * _s
	_title.pivot_offset = _title.size * 0.5
	_title_top.position = Vector2.ZERO
	_title_top.size = Vector2(W * _s, 30 * _s)
	_title_main.position = Vector2(0, 26 * _s)
	_title_main.size = Vector2(W * _s, 70 * _s)
	for c in _crew:
		_place_view(c["view"], c["rect"], c["pivot"], c["rot"])
	if not _dragon.is_empty():
		_place_view(_dragon["view"], DRAGON_RECT, DRAGON_RECT.size * 0.5, 0.0)


func _place_view(view: TextureRect, r: Rect2, pivot: Vector2, rot: float) -> void:
	view.position = _p(r.position)
	view.size = r.size * _s
	view.pivot_offset = pivot * _s
	view.rotation_degrees = rot


# --- 3D-Figuren ---------------------------------------------------------------------------

## Ein kleines 3D-Fenster mit eigener Welt, Licht und Kamera; das Bild zeigt ein TextureRect.
func _make_view(cam_pos: Vector3, look: Vector3) -> Dictionary:
	var vp := SubViewport.new()
	vp.size = Vector2i(VIEW_PX, VIEW_PX)
	vp.transparent_bg = true
	vp.own_world_3d = true
	vp.msaa_3d = Viewport.MSAA_2X
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(vp)
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_CLEAR_COLOR
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.8, 0.78, 0.9)
	e.ambient_light_energy = 0.75
	e.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.environment = e
	vp.add_child(env)
	var key := DirectionalLight3D.new()
	key.rotation_degrees = Vector3(-35, 25, 0)
	key.light_energy = 1.2
	vp.add_child(key)
	var rim := DirectionalLight3D.new()
	rim.rotation_degrees = Vector3(-20, 200, 0)
	vp.add_child(rim)
	var cam := Camera3D.new()
	cam.fov = 30.0
	vp.add_child(cam)
	cam.position = cam_pos
	cam.look_at(look)
	var view := TextureRect.new()
	view.texture = vp.get_texture()
	view.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	view.stretch_mode = TextureRect.STRETCH_SCALE
	view.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return {"vp": vp, "cam": cam, "view": view}


## Modell auf 2,0 Höhe bringen, Füße auf den Boden, mittig.
func _place_model(file: String, vp: SubViewport, yaw: float) -> Node3D:
	var scene := Models._scene(file)
	if scene == null:
		return null
	var n: Node3D = scene.instantiate()
	var acc := [null]
	Models._measure(n, Transform3D.IDENTITY, acc)
	var box: AABB = acc[0]
	var holder := Node3D.new()
	vp.add_child(holder)
	holder.add_child(n)
	var sc := 2.0 / box.size.y
	n.scale = Vector3.ONE * sc
	n.position = -Vector3(box.get_center().x, box.position.y, box.get_center().z) * sc
	holder.rotation_degrees.y = yaw
	return n


func _build_3d() -> void:
	# Drache hinter den Helden, Helden in der Reihenfolge des Mockups (Dusty vorn)
	var d := _make_view(Vector3(0, 0.6, 7.0), Vector3(0, 1.05, 0))
	var dn := _place_model("enemies/Dragon_Evolved", d["vp"], -8.0)
	if dn:
		var ap := Models.player(dn)
		if ap and ap.has_animation("Flying_Idle"):
			ap.get_animation("Flying_Idle").loop_mode = Animation.LOOP_LINEAR
			ap.play("Flying_Idle")
		_dragon = d
		add_child(d["view"])
		move_child(d["view"], _ground.get_index())
	for data in CREW:
		var v := _make_view(Vector3(0, 1.3, 8.0), Vector3(0, 1.25, 0))
		var n := _place_model(data["file"], v["vp"], data["yaw"])
		if n == null:
			continue
		var hero: Dictionary = GameData.HEROES.get(data["id"], {})
		Models.recolor(n, "Skin", hero.get("skin", Color(0.93, 0.75, 0.6)))
		Models.recolor(n, "Face", Color(0.1, 0.07, 0.12))
		var ap := Models.player(n)
		if ap == null or not ap.has_animation(data["anim"]):
			continue
		ap.play(data["anim"])
		ap.seek(data["t0"], true)
		ap.pause()
		var c: Dictionary = data.duplicate()
		c.merge(v)
		c["ap"] = ap
		c["prev_t"] = float(data["t0"])
		c["phase_prev"] = 0.0
		var sk: Skeleton3D = Models.skeleton(n)
		var gun := Models.make_gun(data["gun"])
		if sk and gun:
			var att := BoneAttachment3D.new()
			att.bone_name = "Fist.R"
			sk.add_child(att)
			att.add_child(gun)
			c["att"] = att
			c["gun"] = gun
		add_child(v["view"])
		move_child(v["view"], _front.get_index())
		_crew.append(c)
	_layout()
	# Waffe erst ausrichten, wenn die Knochen einmal berechnet sind
	await get_tree().process_frame
	for c in _crew:
		if c.has("gun"):
			var att: BoneAttachment3D = c["att"]
			var g: Node3D = c["gun"]
			var sc := att.global_transform.basis.get_scale().x
			g.scale = Vector3.ONE * (2.0 / 1.55) / maxf(0.001, sc)
			g.rotation_degrees = Vector3(90, 0, 0)


## Bildschirmpunkt der Mündung: der Waffenpunkt, der am weitesten von der Hand entfernt ist.
func _muzzle(c: Dictionary) -> Vector2:
	var g: Node3D = c["gun"]
	var hand: Vector3 = (c["att"] as Node3D).global_position
	var best := hand
	var bd := -1.0
	for mi in g.find_children("*", "MeshInstance3D", true, false):
		var m := mi as MeshInstance3D
		var ab := m.get_aabb()
		for k in 8:
			var w: Vector3 = m.global_transform * ab.get_endpoint(k)
			var dd := w.distance_to(hand)
			if dd > bd:
				bd = dd
				best = w
	var px: Vector2 = (c["cam"] as Camera3D).unproject_position(best)
	var r: Rect2 = c["rect"]
	var local: Vector2 = px / float(VIEW_PX) * r.size
	var piv: Vector2 = c["pivot"]
	return r.position + piv + (local - piv).rotated(deg_to_rad(c["rot"]))


func _process(delta: float) -> void:
	_t += delta
	_shown = move_toward(_shown, progress, delta * 1.5)
	for c in _crew:
		var period: float = c["period"]
		var ph := fmod(_t, period) / period
		var u := 1.0 - absf(ph * 2.0 - 1.0)
		var t: float = lerpf(c["t0"], c["t1"], u)
		(c["ap"] as AnimationPlayer).seek(t, true)
		var fire_t: float = c["fire"]
		var shot := false
		if fire_t <= float(c["t0"]) + 0.001:
			shot = ph < float(c["phase_prev"])  # neuer Durchlauf: Umkehrpunkt beim Rückstoß
		else:
			shot = float(c["prev_t"]) < fire_t and t >= fire_t
		if shot and c.has("gun"):
			_shots.append({"from": _muzzle(c), "hero": c, "to": c["target"], "age": 0.0, "color": c["color"]})
		c["prev_t"] = t
		c["phase_prev"] = ph
	for s in _shots:
		s["age"] += delta
		if (s["hero"] as Dictionary).has("gun"):
			s["from"] = _muzzle(s["hero"])  # Blitz wandert mit der Waffe
	_shots.assign(_shots.filter(func(s: Dictionary) -> bool: return float(s["age"]) < 0.2))
	if not _dragon.is_empty():
		var v: TextureRect = _dragon["view"]
		v.position = _p(DRAGON_RECT.position + Vector2(0, sin(_t * TAU / 3.4) * -5.0 - 5.0))
		v.rotation_degrees = sin(_t * TAU / 3.4) * 1.5
	var pulse := 0.5 + 0.5 * sin(_t * TAU / 2.8)
	_title.scale = Vector2.ONE * (1.0 + 0.03 * pulse)
	_title.modulate = Color(1, 1, 1) * (1.0 + 0.15 * pulse)
	_back.queue_redraw()
	_ground.queue_redraw()
	_front.queue_redraw()


# --- Gezeichnete Ebenen -------------------------------------------------------------------

func _cross(c: Control, at: Vector2, r: float, col: Color, w := 1.8) -> void:
	c.draw_line(_p(at + Vector2(0, -r)), _p(at + Vector2(0, r)), col, w * _s)
	c.draw_line(_p(at + Vector2(-r, 0)), _p(at + Vector2(r, 0)), col, w * _s)


func _glow(c: Control, at: Vector2, r: float, col: Color, a: float) -> void:
	for i in 5:
		var k := 1.0 - i / 5.0
		c.draw_circle(at, r * k, Color(col, a * 0.22))


## Hinter dem Planeten: Sternschnuppen, Lichtpunkte, funkelnde Sterne, drehender Punkte-Ring
func _draw_back(c: Control) -> void:
	for i in 3:
		var dur: float = [4.2, 5.1, 6.0][i]
		var start := Vector2([360.0, 300.0, 390.0][i], [40.0, 150.0, 260.0][i])
		var delay: float = [0.0, 1.6, 3.1][i]
		var ph := fmod(_t + delay, dur) / dur
		if ph < 0.3:
			var k := ph / 0.3
			var head := start + Vector2(-260, 180) * k
			var dir := Vector2(-260, 180).normalized()
			var a := minf(1.0, k * 6.0) * (1.0 - k)
			for seg in 6:
				var f0 := seg / 6.0
				c.draw_line(_p(head - dir * 90.0 * f0), _p(head - dir * 90.0 * (f0 + 1.0 / 6.0)),
					Color(0.85, 0.92, 1.0, a * (1.0 - f0)), 2.0 * _s)
	for g in GLOWS:
		var a := 0.2 + 0.8 * (0.5 + 0.5 * sin(_t * TAU / float(g[2])))
		_glow(c, _p(g[0]), float(g[1]) * _s, Color(0.75, 0.89, 1.0), a)
	for sp in SPARKLES:
		var a := 0.1 + 0.9 * (0.5 + 0.5 * sin(_t * TAU / float(sp[2]) + float(sp[1])))
		_cross(c, sp[0], sp[1], Color(1, 0.97, 0.9, a))
	# Punkte-Ring, dreht sich in 30 Sekunden einmal
	var n := 150
	for i in n:
		var ang := TAU * i / n + _t * TAU / 30.0
		c.draw_circle(_p(PLANET + Vector2.from_angle(ang) * 172.0), 0.9 * _s, Color(0.82, 0.66, 1.0, 0.5))


## Boden: violetter Planetenrand mit glühender Kante, Kratern und Lava-Rissen
func _draw_ground(c: Control) -> void:
	var left := -_off.x / _s - 40.0
	var right := (size.x - _off.x) / _s + 40.0
	var top := 640.0
	var cx := 195.0
	var rx := maxf(235.0, (right - left) * 0.5)
	var pts := PackedVector2Array()
	for i in 41:
		var a := PI + PI * i / 40.0
		pts.append(_p(Vector2(cx + cos(a) * rx, top + 110.0 + sin(a) * 110.0)))
	pts.append(_p(Vector2(right, H + 40)))
	pts.append(_p(Vector2(left, H + 40)))
	c.draw_colored_polygon(pts, Color(0.23, 0.13, 0.5))
	# heller Kern oben in der Mitte (wie ein Lichtschein auf der Oberfläche)
	for layer in [[260.0, 120.0, Color(0.54, 0.27, 0.72)], [150.0, 60.0, Color(0.88, 0.44, 0.6)], [70.0, 22.0, Color(1.0, 0.77, 0.54)]]:
		var hp := PackedVector2Array()
		for i in 25:
			var a := PI * i / 24.0
			var v := Vector2(cx + cos(a) * float(layer[0]), top + 6.0 + sin(a) * float(layer[1]))
			hp.append(_p(v))
		c.draw_colored_polygon(hp, Color(layer[2], 0.55))
	# glühende Kante
	var edge := PackedVector2Array()
	for i in 41:
		var a := PI + PI * i / 40.0
		edge.append(_p(Vector2(cx + cos(a) * rx, top + 110.0 + sin(a) * 110.0)))
	c.draw_polyline(edge, Color(1.0, 0.6, 0.35, 0.35), 10.0 * _s, true)
	c.draw_polyline(edge, Color(1.0, 0.86, 0.66, 0.8), 2.0 * _s, true)
	# Krater
	for cr in [[Vector2(60, 710), 34.0, 9.0], [Vector2(335, 726), 30.0, 8.0], [Vector2(290, 800), 42.0, 11.0], [Vector2(90, 790), 46.0, 12.0]]:
		_ellipse(c, cr[0], cr[1], cr[2], Color(0.1, 0.05, 0.25), Color(1.0, 0.7, 0.48))
	# Lava-Risse, pulsieren
	var crack := PackedVector2Array()
	for v in CRACK:
		crack.append(_p(v))
	var la := 0.55 + 0.45 * (0.5 + 0.5 * sin(_t * TAU / 1.6))
	c.draw_polyline(crack, Color(1.0, 0.48, 0.16, la), 4.0 * _s, true)
	c.draw_polyline(crack, Color(1.0, 0.89, 0.48), 1.6 * _s, true)
	for br in [[Vector2(190, 766), Vector2(200, 800), Vector2(184, 830)], [Vector2(100, 758), Vector2(112, 790), Vector2(100, 816)]]:
		var bp := PackedVector2Array()
		for v in br:
			bp.append(_p(v))
		c.draw_polyline(bp, Color(1.0, 0.6, 0.23, 1.0 - la * 0.5), 3.0 * _s, true)
	# Funken steigen auf
	for sp in [[200.0, 700.0, 2.4, Color(1, 0.96, 0.75)], [120.0, 730.0, 1.9, Color(1, 0.83, 0.3)], [270.0, 736.0, 2.1, Color(1, 0.6, 0.23)]]:
		var k := 0.5 + 0.5 * sin(_t * TAU / float(sp[2]))
		c.draw_circle(_p(Vector2(sp[0], float(sp[1]) - 30.0 * k)), 2.5 * _s, sp[3])


func _ellipse(c: Control, at: Vector2, rx: float, ry: float, fill: Color, line: Color) -> void:
	var pts := PackedVector2Array()
	for i in 24:
		var a := TAU * i / 24.0
		pts.append(_p(at + Vector2(cos(a) * rx, sin(a) * ry)))
	c.draw_colored_polygon(pts, fill)
	pts.append(pts[0])
	c.draw_polyline(pts, line, 2.0 * _s, true)


## Vorn: Leuchtspuren, Mündungsblitze, Treffer am Drachen und der Ladebalken
func _draw_front(c: Control) -> void:
	for s in _shots:
		var k: float = 1.0 - float(s["age"]) / 0.2
		var col: Color = s["color"]
		var from := _p(s["from"])
		var to := _p(s["to"])
		c.draw_line(from, to, Color(col, 0.45 * k), 6.0 * _s, true)
		c.draw_line(from, to, Color(1, 1, 1, 0.9 * k), 1.6 * _s, true)
		_glow(c, from, 13.0 * _s, Color(1.0, 0.89, 0.48), k * 1.6)
		var star := PackedVector2Array()
		for i in 8:
			var r := 12.0 if i % 2 == 0 else 3.0
			star.append(from + Vector2.from_angle(i * TAU / 8.0) * r * _s)
		c.draw_colored_polygon(star, Color(1, 0.96, 0.75, k))
		c.draw_circle(from, 3.2 * _s, Color(1, 1, 1, k))
		_glow(c, to, 10.0 * _s, Color(1.0, 0.89, 0.48), k * 1.4)
		for a in [0.0, PI * 0.25, PI * 0.5, PI * 0.75]:
			var d := Vector2.from_angle(a) * 9.0 * _s
			c.draw_line(to - d, to + d, Color(col, k), 1.6 * _s)
	# Ladebalken
	var bar := Rect2(_p(Vector2(50, 768)), Vector2(290, 18) * _s)
	var bg := StyleBoxFlat.new()
	bg.bg_color = Color(0.04, 0.03, 0.16, 0.7)
	bg.set_corner_radius_all(int(9 * _s))
	bg.set_border_width_all(maxi(1, int(2 * _s)))
	bg.border_color = Color(0.63, 0.75, 1.0, 0.5)
	c.draw_style_box(bg, bar)
	var inner := bar.grow(-2.0 * _s)
	var fw := maxf(inner.size.y, inner.size.x * _shown)
	var fill := Rect2(inner.position, Vector2(fw, inner.size.y))
	var rr := fill.size.y * 0.5
	var cols := PackedColorArray([Color(0.44, 0.82, 1.0), Color(1.0, 0.83, 0.3).lerp(Color(0.44, 0.82, 1.0), 1.0 - _shown),
		Color(1.0, 0.83, 0.3).lerp(Color(0.44, 0.82, 1.0), 1.0 - _shown), Color(0.44, 0.82, 1.0)])
	if fill.size.x - rr * 2.0 > 1.0:
		c.draw_polygon(PackedVector2Array([fill.position + Vector2(rr, 0), fill.end - Vector2(rr, fill.size.y),
			fill.end - Vector2(rr, 0), fill.position + Vector2(rr, fill.size.y)]), cols)
	c.draw_circle(fill.position + Vector2(rr, rr), rr, cols[0])
	c.draw_circle(fill.end - Vector2(rr, rr), rr, cols[1])
	# Blitz-Knopf am Ende des Balkens, pulsiert
	var knob := Vector2(inner.position.x + inner.size.x * _shown, bar.get_center().y)
	var pulse := 0.5 + 0.5 * sin(_t * TAU)
	_glow(c, knob, (22.0 + 6.0 * pulse) * _s, Color(1.0, 0.84, 0.35), 0.9)
	c.draw_circle(knob, 17.0 * _s, Color(1, 1, 1))
	c.draw_circle(knob, 15.0 * _s, Color(0.91, 0.59, 0.06))
	c.draw_circle(knob + Vector2(-2, -2) * _s, 12.0 * _s, Color(1.0, 0.83, 0.3))
	c.draw_circle(knob + Vector2(-4, -4) * _s, 5.0 * _s, Color(1.0, 0.97, 0.84))
	var bolt := PackedVector2Array()
	for v in [Vector2(1, -10), Vector2(-6, 2), Vector2(-1, 2), Vector2(-2, 10), Vector2(6, -2), Vector2(1, -2)]:
		bolt.append(knob + v * 0.8 * _s)
	c.draw_colored_polygon(bolt, Color(0.35, 0.16, 0.0))
	var text := "%s %d %%" % [_status_text, int(round(_shown * 100.0))]
	var fs := int(16 * _s)
	var ty := _p(Vector2(0, 810)).y
	c.draw_string(_font, Vector2(0, ty + 2.0 * _s), text, HORIZONTAL_ALIGNMENT_CENTER, size.x, fs, Color(0, 0, 0, 0.6))
	c.draw_string(_font, Vector2(0, ty), text, HORIZONTAL_ALIGNMENT_CENTER, size.x, fs, Color(1.0, 0.97, 0.92))
