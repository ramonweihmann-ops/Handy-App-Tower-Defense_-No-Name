extends SceneTree
## Rendert die Rundbilder der Helden (ui/avatars) aus den 3D-Modellen:
##   xvfb-run godot --rendering-driver opengl3 --path game --script tests/render_avatars.gd
var views := []
func _initialize() -> void:
	var root_c := Control.new()
	root.add_child(root_c)
	var k := 0
	# Helden mit freigegebenem Entwurf (ui/heroes2d) haben ihr Rundbild schon daraus; nur die übrigen rendern
	for id in GameData.HERO_IDS.filter(func(h: String) -> bool: return not ResourceLoader.exists("res://ui/heroes2d/%s.png" % h)):
		var v = load("res://scripts/ui/hero_view_3d.gd").new()
		v.hero_id = id
		v.portrait = true
		v.px = 256
		v.aspect = 1.0
		v.fig = 2.05
		v.feet = 2.1
		v.size = Vector2(128, 128)
		v.position = Vector2((k % 4) * 130, (k / 4) * 130)
		root_c.add_child(v)
		views.append([id, v])
		k += 1
	for i in 40:
		await process_frame
	for p in views:
		var img: Image = p[1].texture.get_image()
		img.save_png("res://ui/avatars/%s.png" % p[0])
		print("AVATAR ", p[0], " ", img.get_size())
	quit()
