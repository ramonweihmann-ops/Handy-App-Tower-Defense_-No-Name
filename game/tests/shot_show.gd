extends Node
## Kurzer Film eines Champions beim Schießen (Abnahme der Schusseffekte, docs/HELDEN_UND_SCHUESSE.md).
## Aufruf (mit Fenster): godot --path game -- --autotest --level=12 --profile=zahlend --squad=<held>
##   --shot-show=<ordner>   → <ordner>/f_000.png … (etwa 3 s, 20 Bilder pro Sekunde)
## Drei zähe Gegner stehen mitten auf der Brücke, damit der Held durchgehend schießt.

var main: Node
var out_dir := ""
var _t := 0.0
var _spawned := false
var _frame := 0
var _acc := 0.0


func _process(delta: float) -> void:
	if main.state != "battle":
		return
	var b: Battle = main.battle
	_t += delta
	if not _spawned:
		if _t < 1.0:
			return
		_spawned = true
		for e in b.enemies.duplicate():
			e.queue_free()
		b.enemies.clear()
		b.set_process(true)
		for i in 3:
			var e := b.spawn_enemy(GameData.world_kinds(b.level)[i % 3], Vector3(-1.6 + 1.6 * i, 0, b.spawn_z() * (0.45 + 0.06 * i)))
			e.hp = 1e9
			e.max_hp = 1e9
		_t = 0.0
		return
	if _t < 0.8:
		return
	_acc += delta
	if _acc >= 0.05:
		_acc = 0.0
		get_viewport().get_texture().get_image().save_png("%s/f_%03d.png" % [out_dir, _frame])
		_frame += 1
		if _frame >= 60:
			get_tree().quit()
