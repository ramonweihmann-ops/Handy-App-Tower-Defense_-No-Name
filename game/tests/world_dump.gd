extends SceneTree
## Gibt alle Welten mit Planet und Gegnern als JSON aus (für die Planeten-Übersicht).
## Aufruf: godot --headless --path game -s tests/world_dump.gd

func _init() -> void:
	var out: Array = []
	for i in GameData.WORLDS.size():
		var level := i * GameData.LEVELS_PER_WORLD + 1
		var w: Dictionary = GameData.WORLDS[i]
		var en: Array = []
		for k in w["kinds"]:
			var d: Dictionary = GameData.ENEMIES[k]
			en.append({"kind": k, "name": GameData.enemy_name(k, level), "tier": d["tier"],
				"own": bool(d.get("own_look", false)), "model": Models.ENEMIES.has(k)})
		var f: String = Battlefields.for_level(level)
		out.append({"world": w["name"], "levels": "%d–%d" % [level, level + 4], "field": f,
			"planet": Battlefields.FIELDS[f]["name"], "enemies": en})
	print("JSON:" + JSON.stringify(out))
	quit()
