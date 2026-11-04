extends Node
## Prüfbilder der Kampfeffekte (Bildfolgen) im echten Kampf. Aufruf (mit Fenster):
## godot --path game -- --autotest --level=10 --fx-neu --fx-show=galerie:<ordner>   alle Effekte auf der Brücke, je 12 pro Bild
## godot --path game -- --autotest --level=10 --fx-neu --fx-show=kampf:<ordner>     laufender Kampf, alle 1,2 s ein Bild

var main: Node
var mode := "galerie"
var out_dir := ""
var _t := 0.0
var _page := -1
var _names: Array[String] = []
var _shots := 0
var _placed: Array[Node] = []


func _process(delta: float) -> void:
	if main.state != "battle":
		return
	_t += delta / maxf(0.01, Engine.time_scale)
	if mode == "kampf":
		if _t > 1.2:
			_t = 0.0
			get_viewport().get_texture().get_image().save_png("%s/kampf_%02d.png" % [out_dir, _shots])
			_shots += 1
			if _shots >= 14:
				get_tree().quit()
		return
	var b: Battle = main.battle
	for e in b.enemies.duplicate():
		e.queue_free()
	b.enemies.clear()
	if _names.is_empty():
		for f in ResourceLoader.list_directory(FxSprite.DIR):
			if f.ends_with(".json"):
				_names.append(f.trim_suffix(".json"))
		_names.sort()
	if _page < 0 or _t > 1.0:
		if _page >= 0:
			get_viewport().get_texture().get_image().save_png("%s/galerie_%02d.png" % [out_dir, _page])
		_page += 1
		_t = 0.0
		for n in _placed:
			if is_instance_valid(n):
				n.queue_free()
		_placed.clear()
		if _page * 12 >= _names.size():
			_write_index()
			get_tree().quit()
			return
		for k in 12:
			var i := _page * 12 + k
			if i >= _names.size():
				break
			var col := k % 3
			var row := k / 3
			var pos := Vector3(-2.9 + col * 2.9, 0.6, b.spawn_z() * (0.2 + row * 0.2))
			var s := FxSprite.play(b, _names[i], pos, {"loop": true, "dir": Vector3(0, 0, -1)})
			if s:
				_placed.append(s)


func _write_index() -> void:
	var f := FileAccess.open(out_dir + "/galerie.txt", FileAccess.WRITE)
	for p in ceili(_names.size() / 12.0):
		f.store_line("%d: %s" % [p, ", ".join(_names.slice(p * 12, p * 12 + 12))])
