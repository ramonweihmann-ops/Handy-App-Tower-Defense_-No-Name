class_name FxSprite
extends MeshInstance3D
## Kampfeffekte als Bildfolgen (game/fx/<name>.webp + .json, aus Vorlage_Raw/Effekte_ChatGPT_v1 und v2, übernommen
## mit tools/effekte/import_chatgpt.py). Ein Effekt ist ein Viereck, das zur Kamera zeigt (shaders/fx_sprite.gdshader);
## gerichtete Effekte drehen sich in Schussrichtung, Strahlen strecken sich zwischen zwei Punkten.
## Größe in Weltmaß (1 Einheit ≈ 1 m, die Brücke ist gut 9 breit), Vorgabe aus der JSON („groesse_m“).
##
## FxSprite.play(battle, "brocken_explosion", pos)                       – einmal abspielen, dann weg
## FxSprite.play(battle, "lynx_muendung", pos, {"dir": d, "speed": 2.5})  – gerichtet, schneller
## FxSprite.beam(battle, "volta_geschoss", a, b, 0.35)                   – Strahl von a nach b für 0,35 s
## FxSprite.attach(node, "iska_geschoss", {"dir": d})                     – läuft als Schleife mit dem Knoten mit

const DIR := "res://fx/"
## Höchstzahl gleichzeitiger Effekte: was darüber hinausgeht, wird nicht mehr gezeigt (Dauerfeuer)
const MAX_LIVE := 90
## Alle Effekte so viel größer als „groesse_m“ (Figuren stehen im Kampf vergrößert: Helden ×2, Gegner ×1,45);
## bewusst etwas kleiner als die Figuren es verlangen würden, damit die Gegner sichtbar bleiben
const SCALE := 1.2
## Effekte abgeschwächt: leicht durchsichtig (außer festen Dingen wie den Raumjägern, Option „solid“)
const ALPHA := 0.8

static var enabled := true
static var _info := {}
static var _mats := {}
static var _mesh: QuadMesh
static var _live := 0

var fx_name := ""
var frames := 16
var fps := 24.0
var loop := false
var speed := 1.0
var life := -1.0          # Sekunden; −1 = einmal durch alle Bilder
var fade := 0.12          # Ausblenden am Ende (Sekunden)
var base_alpha := 1.0
var _t := 0.0
var _counted := false


static func has(name: String) -> bool:
	return enabled and not info(name).is_empty()


static func info(name: String) -> Dictionary:
	if not _info.has(name):
		var path := DIR + name + ".json"
		var d = JSON.parse_string(FileAccess.get_file_as_string(path)) if FileAccess.file_exists(path) else null
		_info[name] = d if d is Dictionary and ResourceLoader.exists(DIR + name + ".webp") else {}
	return _info[name]


static func _material(name: String) -> ShaderMaterial:
	if not _mats.has(name):
		var d := info(name)
		var m := ShaderMaterial.new()
		m.shader = preload("res://shaders/fx_sprite.gdshader")
		m.set_shader_parameter("tex", load(DIR + name + ".webp"))
		m.set_shader_parameter("grid", Vector2(float(d.get("cols", 1)), float(d.get("rows", 1))))
		var a: Array = d.get("anker", [0.5, 0.5])
		m.set_shader_parameter("anchor", Vector2(float(a[0]), float(a[1])))
		m.set_shader_parameter("inset", 0.5 / maxf(1.0, float(d.get("frame_px", 128))))
		_mats[name] = m
	return _mats[name]


## Alle Bildfolgen vorab laden (beim Kampfstart), damit der erste Schuss nicht hakt
static func preload_all() -> void:
	if not enabled:
		return
	for f in ResourceLoader.list_directory(DIR):
		if f.ends_with(".json"):
			var n := f.trim_suffix(".json")
			if not info(n).is_empty():
				_material(n)


static func _make(name: String, opts: Dictionary) -> FxSprite:
	if not has(name) or _live >= MAX_LIVE:
		return null
	if _mesh == null:
		_mesh = QuadMesh.new()
		_mesh.size = Vector2.ONE
	var d := info(name)
	var s := FxSprite.new()
	s.fx_name = name
	s.mesh = _mesh
	s.material_override = _material(name)
	s.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	s.frames = int(d.get("frames", 1))
	s.fps = float(d.get("fps", 24))
	s.loop = bool(opts.get("loop", d.get("loop", false)))
	s.speed = float(opts.get("speed", 1.0))
	s.life = float(opts.get("life", -1.0))
	s.fade = float(opts.get("fade", 0.12))
	var w := float(opts.get("width", float(d.get("groesse_m", 1.0)) * float(opts.get("scale", 1.0)))) * SCALE
	var l := float(opts.get("length", w))
	s.set_instance_shader_parameter("size", Vector2(w, l))
	s.set_instance_shader_parameter("dir", opts.get("dir", Vector3.ZERO))
	s.set_instance_shader_parameter("frame", 0.0)
	s.base_alpha = float(opts.get("alpha", 1.0)) * (1.0 if opts.get("solid", false) else ALPHA)
	s.set_instance_shader_parameter("alpha", s.base_alpha)
	s.set_instance_shader_parameter("stretch", 1.0 if opts.has("length") else 0.0)
	s.sorting_offset = float(opts.get("sort", 0.0))
	_live += 1
	s._counted = true
	return s


## Einmal abspielen an pos (Weltkoordinaten)
static func play(parent: Node, name: String, pos: Vector3, opts := {}) -> FxSprite:
	var s := _make(name, opts)
	if s == null:
		return null
	parent.add_child(s)
	s.global_position = pos
	return s


## Strahl von a nach b (gestreckt), steht life Sekunden
static func beam(parent: Node, name: String, a: Vector3, b: Vector3, life_s: float, width := -1.0, alpha := 0.8) -> FxSprite:
	var d := info(name)
	if d.is_empty():
		return null
	var anchor: Array = d.get("anker", [0.5, 0.5])
	var len := a.distance_to(b)
	var w := (width if width > 0.0 else float(d.get("groesse_m", 1.0)) * 0.35) / SCALE
	# Anker unten (0,75): Ursprung bei a; Anker in der Mitte: Ursprung in der Mitte zwischen a und b
	var at := a if float(anchor[1]) > 0.6 else a.lerp(b, 0.5)
	var l := len / maxf(0.25, float(anchor[1])) if float(anchor[1]) > 0.6 else len
	return play(parent, name, at, {"dir": b - a, "width": w, "length": l, "loop": true, "life": life_s, "fade": minf(0.1, life_s * 0.4), "alpha": alpha})


## Als Schleife an einen Knoten hängen (Geschoss); verschwindet mit ihm
static func attach(node: Node3D, name: String, opts := {}) -> FxSprite:
	var o := opts.duplicate()
	o["loop"] = true
	var s := _make(name, o)
	if s == null:
		return null
	node.add_child(s)
	return s


func set_dir(d: Vector3) -> void:
	set_instance_shader_parameter("dir", d)


func _exit_tree() -> void:
	if _counted:
		_counted = false
		_live -= 1


func _process(delta: float) -> void:
	_t += delta * speed
	var f := _t * fps
	var total := float(frames) / fps
	if loop:
		f = fmod(f, float(frames))
	else:
		f = minf(f, float(frames - 1))
	set_instance_shader_parameter("frame", floorf(f))
	var end := (life * speed) if life > 0.0 else total
	if not loop or life > 0.0:
		var left := end - _t
		if left <= fade * speed:
			set_instance_shader_parameter("alpha", base_alpha * clampf(left / maxf(0.001, fade * speed), 0.0, 1.0))
		if _t >= end:
			queue_free()
