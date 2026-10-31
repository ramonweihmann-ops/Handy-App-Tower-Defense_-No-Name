extends Node3D
## Nur zum Ansehen am PC: stellt Helden und Gegner nebeneinander und speichert ein Bild.
## Aufruf: godot --path game res://tests/render_models.tscn -- --out=/pfad/bild.png [--mode=heroes|enemies|aim]

var out := "user://render.png"
var mode := "heroes"
var frames := 0


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.substr(6)
		elif a.begins_with("--mode="):
			mode = a.substr(7)
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color(0.25, 0.22, 0.35)
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.7, 0.7, 0.85)
	e.ambient_light_energy = 0.7
	env.environment = e
	add_child(env)
	var key := DirectionalLight3D.new()
	key.rotation_degrees = Vector3(-40, 30, 0)
	add_child(key)
	var cam := Camera3D.new()
	add_child(cam)
	cam.fov = 40
	var ids: Array = GameData.HERO_IDS
	if mode == "enemies":
		ids = GameData.ENEMIES.keys()
	if mode == "times":
		ids = ["dusty", "dusty", "dusty", "dusty", "dusty", "dusty", "dusty", "dusty"]
	var x := -float(ids.size() - 1) * 1.1
	for id in ids:
		var n: Node3D
		if mode == "enemies":
			var en := Enemy.new()
			en.process_mode = Node.PROCESS_MODE_DISABLED
			add_child(en)
			en.setup(String(id), null, 1.0)
			en._visual.scale = Vector3.ONE
			if en._anim:
				en._anim.process_mode = Node.PROCESS_MODE_ALWAYS
			n = en
		else:
			var h := Hero.new()
			add_child(h)
			h.setup(String(id), null)
			h.hide_pipe()
			if mode == "times" and h._anim:
				h._anim.play("Shoot_OneHanded")
				h._anim.seek(float(get_child_count() - 4) * 0.12, true)
				h._anim.pause()
			if mode != "front" and mode != "heroes":
				h.rotation.y = -PI * 0.5
			n = h
		n.position = Vector3(x, 0, 0)
		if n is Hero:
			(n as Hero)._target_x = x
		x += 2.2 if mode != "enemies" else 3.0
	var span := float(ids.size()) * (2.2 if mode != "enemies" else 3.0)
	cam.position = Vector3(0, 2.5, span * 0.75)
	cam.look_at(Vector3(0, 1.2, 0))
	if mode == "front":
		cam.position = Vector3(0, 2.5, -span * 0.75)
		cam.look_at(Vector3(0, 1.2, 0))


func _process(_d: float) -> void:
	frames += 1
	if frames == 20:
		get_viewport().get_texture().get_image().save_png(out)
		get_tree().quit()
