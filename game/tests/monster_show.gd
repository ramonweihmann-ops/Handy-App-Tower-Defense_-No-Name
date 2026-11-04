extends Node
## Prüfbilder neuer Gegner im echten Kampf: setzt die genannten Gegner auf die Brücke und speichert
## alle 1,5 s ein Bild. Aufruf (mit Fenster):
## godot --path game -- --autotest --level=10 --neue-monster --monster-show=krabbler,brecher,koloss:<ordner>

var main: Node
var kinds: PackedStringArray = []
var out_dir := ""
var _t := 0.0
var _spawned := false
var _shots := 0


func _process(delta: float) -> void:
	if main.state != "battle":
		return
	_t += delta / maxf(0.01, Engine.time_scale)
	if not _spawned and _t > 1.0:
		_spawned = true
		var b: Battle = main.battle
		for e in b.enemies.duplicate():
			e.queue_free()
		b.enemies.clear()
		for i in kinds.size():
			var x := -2.6 + 5.2 * i / maxf(1.0, kinds.size() - 1)
			var e := b.spawn_enemy(kinds[i], Vector3(x, 0, b.spawn_z() * (0.45 + 0.08 * i)))
			e.hp = 1e9
			e.max_hp = 1e9
		_t = 0.0
		return
	if _spawned and _t > 1.5:
		_t = 0.0
		get_viewport().get_texture().get_image().save_png("%s/bild_%02d.png" % [out_dir, _shots])
		_shots += 1
		if _shots >= 10:
			get_tree().quit()
