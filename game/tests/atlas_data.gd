extends SceneTree
## Schreibt die Daten für den Gegner-Atlas (Welten, Gegner, Level, Mob-Gruppen) als JSON.
## Aufruf: godot --headless --path game --script res://tests/atlas_data.gd -- --out=/pfad/atlas.json

func _initialize() -> void:
	seed(1)
	var out := "user://atlas.json"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.substr(6)
	var worlds := []
	for wi in GameData.WORLDS.size():
		var w: Dictionary = GameData.WORLDS[wi]
		var first := wi * GameData.LEVELS_PER_WORLD + 1
		var enemies := []
		for kind in w["kinds"]:
			var d: Dictionary = GameData.ENEMIES[kind]
			enemies.append({"kind": kind, "name": GameData.enemy_name(kind, first), "tier": d["tier"],
				"hp": d["hp"], "speed": d["speed"], "dps": d["dps"], "armor": d["armor"]})
		var levels := []
		for l in range(first, first + GameData.LEVELS_PER_WORLD):
			var counts := {}
			var waves := GameData.waves_in_level(l)
			for wave in range(1, waves + 1):
				for kind in GameData.wave_spawns(l, wave):
					counts[kind] = int(counts.get(kind, 0)) + 1
			var groups := []
			for kind in w["kinds"]:
				if counts.has(kind):
					groups.append({"kind": kind, "count": counts[kind], "name": GameData.enemy_name(kind, l, counts[kind] != 1)})
			levels.append({"level": l, "name": GameData.level_name(l), "boss": GameData.is_boss_level(l),
				"waves": waves, "hp": snappedf(GameData.level_hp(l) * (GameData.boss_hp(l) if GameData.is_boss_level(l) else 1.0), 0.1),
				"groups": groups})
		var tint: Color = w.get("tint", Color(1, 1, 1))
		worlds.append({"index": wi + 1, "name": w["name"], "first": first, "last": first + GameData.LEVELS_PER_WORLD - 1,
			"c1": (w["c1"] as Color).to_html(false), "c2": (w["c2"] as Color).to_html(false),
			"tint": [tint.r, tint.g, tint.b], "enemies": enemies, "levels": levels})
	var f := FileAccess.open(out, FileAccess.WRITE)
	f.store_string(JSON.stringify({"worlds": worlds}, "  "))
	f.close()
	print("ATLAS geschrieben: ", out)
	quit()
