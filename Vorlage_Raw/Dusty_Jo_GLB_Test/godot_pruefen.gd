extends SceneTree

func _initialize() -> void:
	call_deferred("_pruefen")

func _pruefen() -> void:
	var szene := load("res://dusty_jo.glb") as PackedScene
	assert(szene != null, "GLB konnte nicht geladen werden")
	var held := szene.instantiate()
	root.add_child(held)
	var skeleton := held.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var spieler := held.find_child("AnimationPlayer", true, false) as AnimationPlayer
	assert(skeleton != null and spieler != null)
	for name in ["mixamorig:Hips", "mixamorig:Head", "mixamorig:RightHand", "mixamorig:LeftHand", "mixamorig:RightFoot", "mixamorig:LeftFoot"]:
		assert(skeleton.find_bone(name.replace(":", "_")) >= 0, "Pflichtknochen fehlt nach Godot-Namensumsetzung: " + name)
	var socket := held.find_child("WeaponSocket", true, false) as Node3D
	var weapon := held.find_child("Weapon", true, false) as MeshInstance3D
	var muzzle := held.find_child("Muzzle", true, false) as Node3D
	assert(socket != null and weapon != null and muzzle != null)
	assert(weapon.get_parent() == socket and muzzle.get_parent() == weapon)
	var attachment := socket.get_parent() as BoneAttachment3D
	assert(attachment != null and attachment.bone_name == "mixamorig_RightHand")
	assert(weapon.skin == null, "Waffe muss starr bleiben")
	var protokoll := {"status": "Godot-Import und sechs Animationen erfolgreich geprüft", "godot_version": Engine.get_version_info().string, "knochen": skeleton.get_bone_count(), "waffenanker": str(socket.get_path()), "handknochen": attachment.bone_name, "animationen": {}}
	for clip in ["Idle", "Run", "Shoot", "Hit", "Death", "Victory"]:
		assert(spieler.has_animation(clip), "Animation fehlt: " + clip)
		var animation := spieler.get_animation(clip)
		assert(animation.get_track_count() > 0)
		spieler.play(clip)
		spieler.seek(animation.length * 0.5, true)
		spieler.advance(0)
		skeleton.force_update_all_bone_transforms()
		attachment.on_skeleton_update()
		assert(muzzle.global_position.is_finite())
		protokoll.animationen[clip] = {"dauer_sekunden": animation.length, "spuren": animation.get_track_count()}
	spieler.play("Idle")
	spieler.seek(0, true)
	spieler.advance(0)
	skeleton.force_update_all_bone_transforms()
	attachment.on_skeleton_update()
	var schussrichtung := -muzzle.global_basis.z.normalized()
	protokoll.muendungsrichtung_im_anschlag = [schussrichtung.x, schussrichtung.y, schussrichtung.z]
	assert(schussrichtung.dot(Vector3(0, 0, 1)) > 0.98, "Mündung zeigt im Anschlag nicht nach +Z")
	FileAccess.open("res://GODOT_PRUEFBERICHT.json", FileAccess.WRITE).store_string(JSON.stringify(protokoll, "\t"))
	print("ERFOLG: Import, sechs Animationen, rechte Hand, starre Waffe und Mündungsrichtung geprüft.")
	quit(0)
