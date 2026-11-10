extends SceneTree
## Nahaufnahmen eines Gegnermodells in Bewegung (Prüfbilder): je Bewegung vier Bilder schräg von vorn.
## Aufruf (mit Fenster): godot --path game --resolution 360x360 -s tests/model_frames.gd -- <modell.glb> <ordner> <name>

var _model: Node3D
var _anim: AnimationPlayer
var _names: Array = []
var _ai := 0
var _k := 0
var _wait := 0
var _out := ""
var _name := ""


func _initialize() -> void:
	var a := OS.get_cmdline_user_args()
	_out = a[1]
	_name = a[2]
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color("2a1f63")
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color(0.75, 0.75, 0.85)
	root.add_child(env)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-45, -30, 0)
	root.add_child(sun)
	_model = (load(a[0]) as PackedScene).instantiate()
	root.add_child(_model)
	_anim = _model.find_child("AnimationPlayer", true, false)
	_names = Array(_anim.get_animation_list())
	var aabb := AABB()
	for m in _model.find_children("*", "MeshInstance3D", true, false):
		aabb = aabb.merge((m as MeshInstance3D).get_aabb()) if aabb.size != Vector3.ZERO else (m as MeshInstance3D).get_aabb()
	var cam := Camera3D.new()
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	var size := maxf(aabb.size.x, maxf(aabb.size.y, aabb.size.z))
	cam.size = size * 1.7
	root.add_child(cam)
	var c := aabb.get_center()
	cam.look_at_from_position(c + Vector3(0.9, 0.7, 2.2) * size, c, Vector3.UP)


var _pending := false


func _process(_delta: float) -> bool:
	if _ai >= _names.size():
		return true
	if _wait > 0:
		_wait -= 1
		return false
	var an: String = _names[_ai]
	if _pending:
		# Bild der eingestellten Haltung ist jetzt gezeichnet
		root.get_texture().get_image().save_png("%s/%s_%s_%d.png" % [_out, _name, an, _k])
		_pending = false
		_k += 1
		if _k >= 4:
			_k = 0
			_ai += 1
		return false
	_anim.play(an)
	_anim.seek(_anim.get_animation(an).length * _k / 4.0, true)
	_anim.pause()
	_pending = true
	_wait = 2
	return false
