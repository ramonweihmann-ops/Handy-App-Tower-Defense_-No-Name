extends Node
## Prüfbilder der Kampfeffekte (Bildfolgen) im echten Kampf. Aufruf (mit Fenster):
## godot --path game -- --autotest --level=10 --fx-neu --fx-show=galerie:<ordner>   alle Effekte auf der Brücke, je 12 pro Bild
## godot --path game -- --autotest --level=10 --fx-neu --fx-show=kampf:<ordner>     laufender Kampf, alle 1,2 s ein Bild
##   (kampf:<ordner>:60 = erst ab 60 s Spielzeit)
## godot --path game -- --autotest --level=10 --fx-partikel --fx-show=galerie:<ordner>  Partikel-Effekte, 4 Bilder

var main: Node
var mode := "galerie"
var out_dir := ""
var _t := 0.0
var _page := -1
var _names: Array[String] = []
var _shots := 0
var _placed: Array[Node] = []
## Kampf-Modus: erst ab dieser Spielzeit (Sekunden) Bilder machen, damit mehr Helden stehen
var start := 0.0
var _game_t := 0.0


func _process(delta: float) -> void:
	if main.state != "battle":
		return
	_t += delta / maxf(0.01, Engine.time_scale)
	if mode == "kampf":
		_game_t += delta
		if _game_t < start:
			_t = 0.0
			return
		if _t > 1.2:
			_t = 0.0
			get_viewport().get_texture().get_image().save_png("%s/kampf_%02d.png" % [out_dir, _shots])
			_shots += 1
			if _shots >= 14:
				get_tree().quit()
		return
	var b: Battle = main.battle
	if FxP.enabled and mode == "galerie":
		_particle_gallery(b, delta)
		return
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


var _pg_t := 0.6
var _pg_shots := 0


## Partikel-Galerie: jeder Effekt an seinem Platz, alle 0,6 s neu ausgelöst; Bilder nach 0,05 / 0,12 / 0,25 / 0,45 s
func _particle_gallery(b: Battle, delta: float) -> void:
	for e in b.enemies.duplicate():
		e.queue_free()
	b.enemies.clear()
	_pg_t += delta
	if _pg_t < 0.6:
		var at: float = [0.05, 0.12, 0.25, 0.45][_pg_shots % 4]
		if _pg_t > at and _pg_t - delta <= at:
			get_viewport().get_texture().get_image().save_png("%s/partikel_%02d.png" % [out_dir, _pg_shots])
			_pg_shots += 1
			if _pg_shots >= 4:
				get_tree().quit()
		return
	_pg_t = 0.0
	var z0 := b.spawn_z()
	var spots := []
	for r in 4:
		for c in 3:
			spots.append(Vector3(-2.9 + c * 2.9, 0.6, z0 * (0.1 + r * 0.13)))
	var up := Vector3(0, 0, -1)
	FxP.explosion(b, spots[0], 1.7)
	FxP.death(b, spots[1], Color(0.4, 1.0, 0.5), 1.0, false)
	FxP.death(b, spots[2], Color(1.0, 0.35, 0.85), 2.0, true)
	FxP.crit(b, spots[3])
	FxP.vortex(b, spots[4], 1.2)
	FxP.heal(b, spots[5])
	FxP.flame(b, spots[6] + Vector3(0, 0, 3), spots[6])
	FxP.beam(b, "volta", spots[7] + Vector3(-1, 0, 2), spots[7] + Vector3(1, 0, -2))
	FxP.fence_hit(b, spots[8])
	for k in 3:
		FxP.muzzle(b, ["iska", "brocken", "margot"][k], spots[9 + k], up)
		FxP.impact(b, ["kalle", "lynx", "nova"][k], spots[9 + k] + Vector3(0, 0.4, -1.2))
