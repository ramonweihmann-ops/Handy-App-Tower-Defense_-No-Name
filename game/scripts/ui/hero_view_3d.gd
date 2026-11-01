class_name HeroView3D
extends TextureRect
## Ein Held als echte 3D-Figur für die Menü-Bildschirme (Heldenseite, Heldenübersicht).
## Eigenes kleines 3D-Fenster (SubViewport) mit Licht und Kamera; das Bild zeigt dieses
## TextureRect. Haut und Gesicht werden wie im Ladebildschirm umgefärbt, die Waffe sitzt an der
## rechten Faust.
##
## Zwei Arten:
## - Pose (Heldenseite): feste Pose je Held aus dem Mockup, die Animation läuft langsam zwischen
##   zwei Zeitpunkten hin und her. Die Füße bleiben dabei immer auf dem Boden (kein Hüpfen).
## - Porträt (Übersicht): Standbild von vorn ohne Waffe, wird nur einmal gezeichnet.
##
## Bildausschnitt: Die Figur (2,0 Einheiten hoch) steht mit den Füßen auf feet (Anteil der
## Fensterhöhe von oben) und ist fig (Anteil der Fensterhöhe) groß; die Breite folgt aus aspect.

## Pose je Held: Animation, Zeitfenster (hin und her), Drehung um die Hochachse in Grad.
## fig/dx/dy: Größe und Versatz (Anteile der Fensterhöhe), damit die Figur samt Waffe genau so
## groß ist und so steht wie das Heldenbild im Mockup (gemessen, siehe Mockup „Held aufleveln“).
const POSES := {
	"dusty": {"anim": "Shoot_OneHanded", "t0": 0.55, "t1": 0.65, "yaw": -35.0, "fig": 0.778, "dx": 0.078, "dy": 0.022},
	"iska": {"anim": "Run", "t0": 0.538, "t1": 0.562, "yaw": 30.0, "fig": 0.816, "dx": -0.053, "dy": 0.039},
	"brocken": {"anim": "Punch", "t0": 0.23, "t1": 0.27, "yaw": 25.0, "fig": 0.824, "dx": 0.05, "dy": 0.019},
	"kalle": {"anim": "Jump", "t0": 0.28, "t1": 0.32, "yaw": 30.0, "fig": 0.741, "dx": -0.085, "dy": 0.022},
	"fritzi": {"anim": "Victory", "t0": 0.75, "t1": 0.85, "yaw": -20.0, "fig": 0.764, "dx": 0.055, "dy": 0.017},
	"volta": {"anim": "Victory", "t0": 0.35, "t1": 0.45, "yaw": 25.0, "fig": 0.688, "dx": -0.044, "dy": 0.014},
	"margot": {"anim": "Shoot_OneHanded", "t0": 0.55, "t1": 0.65, "yaw": 35.0, "fig": 0.766, "dx": -0.118, "dy": 0.021},
	"lynx": {"anim": "Jump", "t0": 0.28, "t1": 0.32, "yaw": 30.0, "fig": 0.741, "dx": -0.176, "dy": 0.022},
}
## Waffen der Helden, die im Kampf eine eigene einfache Form haben, für das Menü eingefärbt
const MENU_GUNS := {"kalle": "guns/ShortCannon", "fritzi": "guns/GrenadeLauncher", "volta": "guns/Revolver"}
const GUN_TINT := {"kalle": Color("#a8e8ff"), "fritzi": Color("#ffb070"), "volta": Color("#9fe8ff")}
const FOOT_BONES := ["Foot.L", "Foot.R"]

var hero_id := ""
var portrait := false     # Standbild von vorn ohne Waffe
var grayscale := false    # gesperrt: grau und dunkler (wie im Mockup grayscale(1) brightness(0.55))
var px := 512             # Auflösung des 3D-Fensters (Höhe)
var aspect := 1.0         # Breite / Höhe des Fensters
var fig := 0.78           # Figurhöhe als Anteil der Fensterhöhe
var feet := 0.95          # Lage der Füße (Anteil von oben)
var period := 3.2         # Sekunden für einmal hin und zurück

var _vp: SubViewport
var _cam: Camera3D
var _holder: Node3D
var _model: Node3D
var _ap: AnimationPlayer
var _skel: Skeleton3D
var _pose: Dictionary = {}
var _foot_rest := 0.0
var _t := 0.0
var _frames_left := 0


static func make(id: String, as_portrait := false, locked := false) -> HeroView3D:
	var v := HeroView3D.new()
	v.hero_id = id
	v.portrait = as_portrait
	v.grayscale = locked
	if as_portrait:
		v.px = 256
	return v


func _ready() -> void:
	expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	stretch_mode = TextureRect.STRETCH_SCALE
	mouse_filter = Control.MOUSE_FILTER_IGNORE

	_vp = SubViewport.new()
	_vp.size = Vector2i(roundi(px * aspect), px)
	_vp.transparent_bg = true
	_vp.own_world_3d = true
	_vp.msaa_3d = Viewport.MSAA_2X
	add_child(_vp)
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_CLEAR_COLOR
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.8, 0.78, 0.9)
	e.ambient_light_energy = 0.75
	e.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.environment = e
	_vp.add_child(env)
	var key := DirectionalLight3D.new()
	key.rotation_degrees = Vector3(-35, 25, 0)
	key.light_energy = 1.2
	_vp.add_child(key)
	var rim := DirectionalLight3D.new()
	rim.rotation_degrees = Vector3(-20, 200, 0)
	_vp.add_child(rim)
	_cam = Camera3D.new()
	_cam.fov = 30.0
	_vp.add_child(_cam)
	_frame_camera()
	texture = _vp.get_texture()
	if grayscale and not _headless():
		var m := ShaderMaterial.new()
		m.shader = _gray_shader()
		material = m
	if hero_id != "":
		set_hero(hero_id)


## Kamera so stellen, dass eine 2,0 hohe Figur fig der Fensterhöhe einnimmt, Füße auf feet.
func _frame_camera() -> void:
	var span := 2.0 / fig                     # sichtbare Höhe in Einheiten
	var dist := span * 0.5 / tan(deg_to_rad(_cam.fov * 0.5))
	var center_y := (feet - 0.5) * span       # Bildmitte über dem Boden
	_cam.position = Vector3(0, center_y, dist)
	_cam.look_at(Vector3(0, center_y, 0))


## Anderen Helden zeigen
func set_hero(id: String) -> void:
	hero_id = id
	if _vp == null:
		return
	if is_instance_valid(_holder):
		_holder.queue_free()
	_holder = null
	_model = null
	_ap = null
	_skel = null
	var info: Dictionary = Models.HEROES.get(id, {})
	var scene := Models._scene(str(info.get("file", "")))
	if scene == null:
		return
	_model = scene.instantiate()
	var acc := [null]
	Models._measure(_model, Transform3D.IDENTITY, acc)
	var box: AABB = acc[0]
	_holder = Node3D.new()
	_vp.add_child(_holder)
	_holder.add_child(_model)
	var sc := 2.0 / box.size.y
	_model.scale = Vector3.ONE * sc
	_model.position = -Vector3(box.get_center().x, box.position.y, box.get_center().z) * sc
	var hero: Dictionary = GameData.HEROES.get(id, {})
	if not _headless():
		Models.recolor(_model, "Skin", hero.get("skin", Color(0.93, 0.75, 0.6)))
		Models.recolor(_model, "Face", Color(0.1, 0.07, 0.12))
	_ap = Models.player(_model)
	_skel = Models.skeleton(_model)
	_pose = {"anim": "Idle", "t0": 0.0, "t1": 0.0, "yaw": 0.0} if portrait else POSES.get(id, {"anim": "Idle", "t0": 0.0, "t1": 0.0, "yaw": 0.0})
	_holder.rotation_degrees.y = float(_pose["yaw"])
	if not portrait and _pose.has("fig"):
		fig = float(_pose["fig"])
		_frame_camera()
		var span := 2.0 / fig
		_holder.position = Vector3(float(_pose["dx"]) * span, float(_pose["dy"]) * span, 0.0)
	# Ruhelage der Füße (Idle am Anfang) merken: daran wird jede Pose auf den Boden gestellt
	_foot_rest = 0.0
	if _ap and _ap.has_animation("Idle"):
		_ap.play("Idle")
		_ap.seek(0.0, true)
		_ap.pause()
		_foot_rest = _foot_y()
	if _ap and _ap.has_animation(str(_pose["anim"])):
		_ap.play(str(_pose["anim"]))
		_ap.seek(float(_pose["t0"]), true)
		_ap.pause()
	_ground()
	if not portrait:
		_attach_gun(id)
	_vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	# Standbild: ein paar Bilder zeichnen (Knochen und Waffe sind dann gesetzt), danach ruhen
	_frames_left = 4 if portrait else -1


func _attach_gun(id: String) -> void:
	var file: String = str(Models.HEROES.get(id, {}).get("gun", ""))
	if file == "":
		file = MENU_GUNS.get(id, "")
	if file == "" or _skel == null:
		return
	var gun := Models.make_gun(file)
	if gun == null:
		return
	if GUN_TINT.has(id) and not _headless():
		Models.tint_all(gun, GUN_TINT[id])
	var att := BoneAttachment3D.new()
	att.bone_name = "Fist.R"
	_skel.add_child(att)
	att.add_child(gun)
	gun.visible = false
	# Waffe erst ausrichten, wenn die Knochen einmal berechnet sind
	await get_tree().process_frame
	if not is_instance_valid(att) or not is_instance_valid(gun):
		return
	var s := att.global_transform.basis.get_scale().x
	gun.scale = Vector3.ONE * (2.0 / 1.55) / maxf(0.001, s)
	gun.rotation_degrees = Vector3(90, 0, 0)
	gun.visible = true


## Tiefster Fußknochen in Weltkoordinaten
func _foot_y() -> float:
	if _skel == null:
		return 0.0
	var low := INF
	for b in FOOT_BONES:
		var i := _skel.find_bone(b)
		if i >= 0:
			var p: Vector3 = (_skel.global_transform * _skel.get_bone_global_pose(i)).origin
			low = minf(low, p.y)
	return 0.0 if low == INF else low


## Figur so verschieben, dass der tiefere Fuß wie in Ruhe auf dem Boden steht
func _ground() -> void:
	if _model == null or _skel == null:
		return
	var dy := _foot_y() - _foot_rest
	_model.position.y -= dy


func _process(delta: float) -> void:
	if _frames_left > 0:
		_frames_left -= 1
		if _frames_left == 0:
			_vp.render_target_update_mode = SubViewport.UPDATE_DISABLED
		return
	if portrait or _ap == null or _pose.is_empty() or not is_visible_in_tree():
		return
	_t += delta
	var ph := fmod(_t, period) / period
	var u := 0.5 - 0.5 * cos(ph * TAU)   # weich hin und zurück
	var t := lerpf(float(_pose["t0"]), float(_pose["t1"]), u)
	if _ap.has_animation(str(_pose["anim"])):
		_ap.seek(t, true)
		_ground()


## Ohne Grafik (Tests mit --headless): nicht umfärben, keine Shader. Der Ersatz-Renderer kennt
## die kopierten Materialien nicht und meldet sonst Fehler; zu sehen ist dort ohnehin nichts.
static func _headless() -> bool:
	return DisplayServer.get_name() == "headless"


static var _gray: Shader


static func _gray_shader() -> Shader:
	if _gray == null:
		_gray = Shader.new()
		_gray.code = "shader_type canvas_item;\nvoid fragment() {\n\tvec4 c = COLOR;\n\tfloat g = dot(c.rgb, vec3(0.299, 0.587, 0.114)) * 0.55;\n\tCOLOR = vec4(vec3(g), c.a);\n}\n"
	return _gray
