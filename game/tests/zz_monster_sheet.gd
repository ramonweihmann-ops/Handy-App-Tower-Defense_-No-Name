extends SceneTree
## Prüfbild eines Gegnermodells: je Bewegung 6 Bilder (schräg von vorn), gerendert mit der Spiel-Engine.
## godot --path game --script tests/zz_monster_sheet.gd -- <modell.glb> <ausgabe-ordner> <Bewegung,…> [gierwinkel]

var vp: SubViewport
var holder: Node3D
var ap: AnimationPlayer
var jobs: Array = []
var out_dir := ""
var wait := 0
var cur: Array = []


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var glb: String = args[0]
	out_dir = args[1]
	var anims: PackedStringArray = args[2].split(",")
	var yaw := float(args[3]) if args.size() > 3 else 25.0
	var head := args.size() > 4 and args[4] == "kopf"
	var count := int(args[5]) if args.size() > 5 else 6
	vp = SubViewport.new()
	vp.size = Vector2i(360, 400)
	vp.transparent_bg = false
	vp.own_world_3d = true
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(vp)
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color(0.16, 0.12, 0.33)
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.6, 0.62, 0.8)
	e.ambient_light_energy = 0.8
	env.environment = e
	vp.add_child(env)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-50, -30, 0)
	sun.light_energy = 1.2
	vp.add_child(sun)
	var doc := GLTFDocument.new()
	var st := GLTFState.new()
	doc.append_from_file(glb, st)
	var scene: Node3D = doc.generate_scene(st)
	holder = Node3D.new()
	vp.add_child(holder)
	holder.add_child(scene)
	holder.rotation_degrees.y = yaw
	ap = scene.find_children("*", "AnimationPlayer", true, false)[0] if scene.find_children("*", "AnimationPlayer", true, false).size() > 0 else null
	# Größe: Kamera auf die Ruhehöhe
	var aabb := _aabb(scene)
	var h := aabb.size.y
	var cam := Camera3D.new()
	cam.fov = 30.0
	var c := aabb.get_center()
	var dist := maxf(h, aabb.size.x) * 2.2
	vp.add_child(cam)
	if head:
		var hy := aabb.position.y + h * 0.78
		cam.look_at_from_position(Vector3(0, hy, h * 1.0), Vector3(0, hy, 0))
	else:
		cam.look_at_from_position(Vector3(0, c.y + h * 0.15, dist), Vector3(0, c.y, 0))
	var floor_mesh := PlaneMesh.new()
	floor_mesh.size = Vector2(20, 20)
	var fl := MeshInstance3D.new()
	fl.mesh = floor_mesh
	var fm := StandardMaterial3D.new()
	fm.albedo_color = Color(0.25, 0.2, 0.45)
	fl.material_override = fm
	vp.add_child(fl)
	print("GROESSE ", aabb.size, " unten ", aabb.position.y)
	for a in anims:
		if a == "Ruhe":
			jobs.append(["Ruhe", 0.0, 0])
			continue
		if ap == null or not ap.has_animation(a):
			print("FEHLT ", a)
			continue
		var len := ap.get_animation(a).length
		for k in count:
			jobs.append([a, len * k / float(count), k])


func _aabb(n: Node) -> AABB:
	var box := AABB()
	var first := true
	for m in n.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		var b := mi.global_transform * mi.get_aabb()
		box = b if first else box.merge(b)
		first = false
	return box


func _process(_d: float) -> bool:
	if wait > 0:
		wait -= 1
		if wait == 0:
			var img := vp.get_texture().get_image()
			img.save_png("%s/%s_%d.png" % [out_dir, cur[0], cur[2]])
		return false
	if jobs.is_empty():
		return true
	cur = jobs.pop_front()
	if cur[0] != "Ruhe":
		ap.play(cur[0])
		ap.seek(cur[1], true)
		ap.pause()
	wait = 3
	return false
