extends Node
## Löst die Superfähigkeiten aller Helden einmal aus (im laufenden Kampf).
## Aufruf: godot --headless --fixed-fps 60 --path game -- --autotest --level=3 --ultcheck

var main: Node
var _t := 0.0
var _done := false


func _process(delta: float) -> void:
	if main.state != "battle" or main.battle.enemies.is_empty():
		return
	_t += delta
	if _t > 1.0 and not _done:
		_done = true
		for id in GameData.HERO_IDS:
			var h: Hero = main.battle.heroes[0] if main.battle.has_hero(id) else main.battle.add_hero(id)
			for x in main.battle.heroes:
				if x.id == id:
					h = x
			h.mods["ult"] = 1
			print("ULTCHECK ", id, " ", Hero.ULTS[h.family()][0], " ausgelöst: ", h.activate_ult())
	if _done and _t > 12.0:
		print("ULTCHECK fertig, Gegner übrig ", main.battle.enemies.size())
		get_tree().quit()
