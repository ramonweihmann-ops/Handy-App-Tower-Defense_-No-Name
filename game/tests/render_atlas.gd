extends Node
## Rendert jeden Gegner jeder Welt in Weltfarbe als PNG mit transparentem Hintergrund.
## Aufruf (mit Fenster, z. B. xvfb-run): godot --path game res://tests/render_atlas.tscn -- --out=/pfad/ordner

var out := "user://atlas"


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.substr(6)
	DirAccess.make_dir_recursive_absolute(out)
	_run()


func _run() -> void:
	var vp := SubViewport.new()
	vp.size = Vector2i(360, 360)
	vp.transparent_bg = true
	vp.own_world_3d = true
	vp.msaa_3d = Viewport.MSAA_4X
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
	rim.light_energy = 1.0
	vp.add_child(rim)
	var cam := Camera3D.new()
	cam.fov = 30.0
	vp.add_child(cam)
	for wi in GameData.WORLDS.size():
		var w: Dictionary = GameData.WORLDS[wi]
		for kind in w["kinds"]:
			var en := Enemy.new()
			en.process_mode = Node.PROCESS_MODE_DISABLED
			en.tint = w.get("tint", Color(1, 1, 1))
			vp.add_child(en)
			en.setup(String(kind), null, 1.0)
			en._visual.scale = Vector3.ONE
			en.rotation.y = 0.35
			if en._anim:
				en._anim.process_mode = Node.PROCESS_MODE_ALWAYS
			var h := en.top_height()
			if kind == "tentakler":
				h *= 1.7  # schwebt über dem Boden
			cam.position = Vector3(0, h * 0.55, h * 2.6 + 1.5)
			cam.look_at(Vector3(0, h * 0.42, 0))
			for i in 12:
				await get_tree().process_frame
			var img := vp.get_texture().get_image()
			img.save_png("%s/w%02d_%s.png" % [out, wi + 1, kind])
			en.queue_free()
			await get_tree().process_frame
	print("ATLASBILDER fertig: ", out)
	get_tree().quit()
