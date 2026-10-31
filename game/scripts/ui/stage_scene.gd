class_name StageScene
extends Control
## Bild des gewählten Levels im Kampf-Reiter: ein runder, glänzender Rahmen, dahinter das
## Wurmloch in den Farben der Welt und davor die echten 3D-Gegner dieser Welt, die auf der
## Stelle tänzeln. Beim Boss-Level steht der Boss in der Mitte.

const FRAME := 7.0

var level := 1
var hard := false

var _bg: ColorRect
var _mat: ShaderMaterial
var _view: SubViewportContainer
var _enemies: Array[Enemy] = []
var _t := 0.0
var _title: Label


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var w: Dictionary = GameData.WORLDS[GameData.world_of(level)]
	_bg = ColorRect.new()
	_bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_mat = ShaderMaterial.new()
	_mat.shader = preload("res://shaders/stage_bg.gdshader")
	_mat.set_shader_parameter("c1", w["c1"])
	_mat.set_shader_parameter("c2", w["c2"])
	if GameData.world_of(level) == 1:
		_mat.set_shader_parameter("sky_top", Color(0.05, 0.1, 0.08))
		_mat.set_shader_parameter("sky_bottom", Color(0.18, 0.26, 0.14))
		_mat.set_shader_parameter("ground", Color(0.3, 0.36, 0.2))
	if hard:
		_mat.set_shader_parameter("sky_top", Color(0.18, 0.03, 0.06))
		_mat.set_shader_parameter("sky_bottom", Color(0.4, 0.08, 0.12))
		_mat.set_shader_parameter("ground", Color(0.5, 0.15, 0.15))
	_bg.material = _mat
	add_child(_bg)
	_build_view()
	_title = UiKit.label("%s%s" % [GameData.world_name(level), " · Schwer" if hard else ""], 28, UiKit.C_GOLD)
	_title.add_theme_constant_override("outline_size", 10)
	_title.add_theme_color_override("font_outline_color", Color(0.15, 0.03, 0.2, 0.9))
	add_child(_title)
	resized.connect(_layout)
	_layout()


func _layout() -> void:
	var inner := Rect2(Vector2(FRAME, FRAME), size - Vector2(FRAME, FRAME) * 2.0)
	_bg.position = inner.position
	_bg.size = inner.size
	_mat.set_shader_parameter("px_size", inner.size)
	_mat.set_shader_parameter("radius", 22.0)
	_view.position = inner.position
	_view.size = inner.size
	_title.position = Vector2(0, size.y - 62)
	_title.size = Vector2(size.x, 40)


func _build_view() -> void:
	_view = SubViewportContainer.new()
	_view.stretch = true
	_view.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_view)
	var vp := SubViewport.new()
	vp.own_world_3d = true
	vp.transparent_bg = true
	vp.msaa_3d = Viewport.MSAA_2X
	vp.render_target_update_mode = SubViewport.UPDATE_WHEN_VISIBLE
	_view.add_child(vp)
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_CLEAR_COLOR
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.75, 0.7, 0.95)
	e.ambient_light_energy = 0.7
	e.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.environment = e
	vp.add_child(env)
	var key := DirectionalLight3D.new()
	key.rotation_degrees = Vector3(-40, 20, 0)
	key.light_energy = 1.2
	key.light_color = Color(1.0, 0.92, 0.85)
	vp.add_child(key)
	var rim := DirectionalLight3D.new()
	rim.rotation_degrees = Vector3(-15, 180, 0)
	rim.light_energy = 1.4
	rim.light_color = GameData.WORLDS[GameData.world_of(level)]["rim"]
	vp.add_child(rim)
	var cam := Camera3D.new()
	# Breite festhalten: die Karte ist hochkant, alle Figuren sollen nebeneinander passen
	cam.keep_aspect = Camera3D.KEEP_WIDTH
	cam.fov = 44.0
	cam.position = Vector3(0, 2.6, 9.0)
	vp.add_child(cam)
	# Blick über die Figuren hinweg, damit sie unten auf dem Boden stehen
	cam.look_at(Vector3(0, 3.6, 0), Vector3.UP)
	# Aufstellung: leichte Gegner vorne, stärkere dahinter, der Boss in der Mitte
	var kinds: Array = GameData.WORLDS[GameData.world_of(level)]["kinds"]
	var in_world := (level - 1) % GameData.LEVELS_PER_WORLD
	var spots := [[kinds[0], Vector3(-1.9, 0, 1.2)], [kinds[0], Vector3(1.9, 0, 1.2)]]
	if in_world >= 1:
		spots.append([kinds[1], Vector3(-0.9, 0, 0.3)])
	if in_world >= 2:
		spots.append([kinds[2], Vector3(1.0, 0, -0.2)])
	if GameData.is_boss_level(level):
		spots = [[kinds[0], Vector3(-2.1, 0, 1.3)], [kinds[1], Vector3(2.1, 0, 1.1)], [kinds[3], Vector3(0, 0, -0.6)]]
	elif in_world == 0:
		spots.append([kinds[0], Vector3(0, 0, 0.0)])
	for s in spots:
		var en := Enemy.new()
		en.process_mode = Node.PROCESS_MODE_DISABLED
		en.position = s[1]
		vp.add_child(en)
		en.setup(String(s[0]), null, 1.0)
		en.rotation.y = randf_range(-0.25, 0.25)
		_enemies.append(en)


func _process(delta: float) -> void:
	_t += delta
	for en in _enemies:
		en._t += delta
		en._visual.scale = Vector3.ONE
		en._animate(delta, true)


func _draw() -> void:
	# Rahmen: weicher Schatten, warmes Gold-Lila, darauf Glanz
	var r := Rect2(Vector2.ZERO, size)
	var frame := Color(0.95, 0.6, 0.35) if not hard else Color(1.0, 0.4, 0.35)
	draw_style_box(UiKit.candy(frame, 30, "panel"), r)
