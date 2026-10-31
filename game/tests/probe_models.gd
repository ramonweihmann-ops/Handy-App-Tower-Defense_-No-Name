extends SceneTree

func _aabb(n: Node, xf: Transform3D, acc: Array) -> void:
	var t := xf
	if n is Node3D:
		t = xf * (n as Node3D).transform
	if n is MeshInstance3D:
		var a: AABB = t * (n as MeshInstance3D).get_aabb()
		acc[0] = a if acc[0] == null else acc[0].merge(a)
	for c in n.get_children():
		_aabb(c, t, acc)

func _initialize() -> void:
	for dir in ["heroes", "enemies", "guns"]:
		for f in DirAccess.get_files_at("res://models/" + dir):
			if not f.ends_with(".gltf"):
				continue
			var s: Node = load("res://models/%s/%s" % [dir, f]).instantiate()
			var acc := [null]
			_aabb(s, Transform3D.IDENTITY, acc)
			var info := "%s/%s aabb=%s" % [dir, f, acc[0]]
			var sk := s.find_children("*", "Skeleton3D", true, false)
			if sk.size() > 0 and dir == "heroes" and f.begins_with("Cowboy"):
				var names := []
				for i in sk[0].get_bone_count():
					names.append(sk[0].get_bone_name(i))
				info += " bones=" + str(names)
			print(info)
			s.free()
	quit()
