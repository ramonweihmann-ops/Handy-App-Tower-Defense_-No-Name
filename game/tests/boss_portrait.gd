extends SceneTree
## Porträt eines Boss-Modells für das Boss-Portal im Abenteuer-Pfad: von vorn, oberer Teil der Figur,
## durchsichtiger Hintergrund, in der Färbung der Welt.
## Aufruf (mit Fenster): godot --path game --resolution 512x512 -s tests/boss_portrait.gd -- <modell.glb> <bild.png> <färbung r,g,b> <anteil>
## anteil: wie viel der Figurhöhe von oben ins Bild kommt (Schleim 1.0, Zweibeiner etwa 0.55)

var _frames := 0
var _out := ""


func _initialize() -> void:
	var a := OS.get_cmdline_user_args()
	_out = a[1]
	var t := a[2].split(",")
	var tint := Color(float(t[0]), float(t[1]), float(t[2]))
	var frac := float(a[3])
	var wfrac := float(a[4]) if a.size() > 4 else frac
	root.transparent_bg = true
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_CLEAR_COLOR
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color(0.8, 0.78, 0.9)
	root.add_child(env)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-35, -25, 0)
	root.add_child(sun)
	var model: Node3D = (load(a[0]) as PackedScene).instantiate()
	root.add_child(model)
	var anim: AnimationPlayer = model.find_child("AnimationPlayer", true, false)
	if anim:
		var names := anim.get_animation_list()
		var walk := "Walk" if names.has("Walk") else names[0]
		anim.play(walk)
		anim.seek(0.0, true)
		anim.pause()
	if tint != Color(1, 1, 1):
		Models.tint_all(model, tint)
	var aabb := AABB()
	for m in model.find_children("*", "MeshInstance3D", true, false):
		var b := (m as MeshInstance3D).get_aabb()
		aabb = b if aabb.size == Vector3.ZERO else aabb.merge(b)
	var h := aabb.size.y * frac
	var cam := Camera3D.new()
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	cam.size = maxf(h, aabb.size.x * wfrac) * 1.02
	root.add_child(cam)
	var c := Vector3(aabb.get_center().x, aabb.end.y - h * 0.5, aabb.get_center().z)
	cam.look_at_from_position(c + Vector3(0, 0.15 * h, 4.0 * aabb.size.y), c, Vector3.UP)


func _process(_delta: float) -> bool:
	_frames += 1
	if _frames == 4:
		root.get_texture().get_image().save_png(_out)
		return true
	return false
