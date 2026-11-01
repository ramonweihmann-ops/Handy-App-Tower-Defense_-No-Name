class_name MockView
extends Control
## Baut einen Bildschirm genau wie im Mockup auf (Vorlage: Design-Entwurf „Menü-Entwürfe Wurmloch“).
## Das Werkzeug tools/mock2game zerlegt jedes Mockup in ein Hintergrundbild, Knöpfe als einzelne
## Bilder und alle Texte (Schrift, Größe, Farbe, Schatten, Lage). Hier wird das wieder
## zusammengesetzt: auf 390 × 844 Mockup-Punkte gerechnet und auf den Bildschirm skaliert.
## Texte bleiben echte Texte (Werte wie Gold lassen sich austauschen), Knöpfe echte Knöpfe.

signal button_pressed(btn: Dictionary)

const W := 390.0
const H := 844.0

var screen := ""
var state := ""
var overlay := ""      # gesetzt: diese Ansicht ist ein Popup über einem Bildschirm
var data: Dictionary = {}
var s := 1.0
var off := Vector2.ZERO

var _fill: TextureRect
var _bg: TextureRect
var _live_layer: Control
var _text_layer: Control
var _btn_layer: Control
var _buttons: Array[MockButton] = []
var _overrides := {}   # Text-Nummer -> neuer Text
var _hidden := {}      # Text-Nummer -> true
var _live := {}        # Live-Kennung -> Rect2 (Mockup-Punkte)
var _placed := {}      # Live-Kennung -> Control
var _live_info := {}   # Live-Kennung -> Daten aus dem Export (Bild, Drehung)

static var _layouts := {}


static func layout_of(screen_name: String) -> Dictionary:
	if not _layouts.has(screen_name):
		var path := "res://ui_mock/%s/layout.json" % screen_name
		var f := FileAccess.open(path, FileAccess.READ)
		_layouts[screen_name] = JSON.parse_string(f.get_as_text()) if f else {}
	return _layouts[screen_name]


func _init(screen_name := "", state_name := "main", overlay_name := "") -> void:
	screen = screen_name
	state = state_name
	overlay = overlay_name


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	_fill = TextureRect.new()
	_fill.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_fill.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_fill.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	_fill.modulate = Color(0.55, 0.55, 0.6)
	_fill.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fill.visible = overlay == ""
	add_child(_fill)
	_bg = TextureRect.new()
	_bg.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_bg.stretch_mode = TextureRect.STRETCH_SCALE
	_bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_bg)
	_live_layer = _plain()
	_text_layer = _plain()
	_text_layer.draw.connect(_draw_free_texts)
	_btn_layer = _plain()
	resized.connect(_layout)
	if screen != "":
		show_state(state)


func _plain() -> Control:
	var c := Control.new()
	c.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(c)
	return c


## Einen anderen Zustand des Bildschirms zeigen (z. B. „Rad dreht“), Ersetzungen bleiben.
func show_state(state_name: String) -> void:
	state = state_name
	var lay := layout_of(screen)
	if overlay != "":
		data = lay.get("overlays", {}).get(overlay, {})
	else:
		data = lay.get("states", {}).get(state_name, {})
	var dir := "res://ui_mock/%s/" % screen
	var tex: Texture2D = load(dir + str(data.get("bg", ""))) if str(data.get("bg", "")) != "" else null
	_bg.texture = tex
	if overlay == "":
		_fill.texture = tex
	for b in _buttons:
		b.queue_free()
	_buttons.clear()
	for b in data.get("buttons", []):
		var mb := MockButton.new()
		mb.view = self
		mb.info = b
		if str(b.get("img", "")) != "":
			mb.texture = load(dir + str(b["img"]))
		_btn_layer.add_child(mb)
		_buttons.append(mb)
	_live.clear()
	_live_info.clear()
	for l in data.get("live", []):
		var r: Array = l["rect"]
		_live[str(l["id"])] = Rect2(r[0], r[1], r[2], r[3])
		_live_info[str(l["id"])] = l
		if bool(l.get("badge", false)) and int(l.get("button", -1)) >= 0:
			for mb in _buttons:
				if int(mb.info["i"]) == int(l["button"]):
					mb.badge_rect = Rect2(r[0], r[1], r[2], r[3])
	_layout()


func _layout() -> void:
	if size.x <= 0.0 or size.y <= 0.0:
		return
	s = minf(size.x / W, size.y / H)
	off = Vector2((size.x - W * s) * 0.5, (size.y - H * s) * 0.5)
	if overlay != "" and data.has("rect"):
		var br: Array = data["rect"]
		_bg.position = to_screen(Vector2(br[0], br[1]))
		_bg.size = Vector2(br[2], br[3]) * s
	else:
		_bg.position = off
		_bg.size = Vector2(W, H) * s
	for b in _buttons:
		b.fit()
	for id in _placed.keys():
		var c: Control = _placed[id]
		if is_instance_valid(c) and _live.has(id):
			var r: Rect2 = _live[id]
			c.position = to_screen(r.position)
			c.size = r.size * s
			if c.has_meta("pivot_frac"):
				c.pivot_offset = c.size * (c.get_meta("pivot_frac") as Vector2)
	_text_layer.queue_redraw()


func to_screen(p: Vector2) -> Vector2:
	return off + p * s


# --- Texte ---------------------------------------------------------------------------------

## Texte über die Nummer oder den ursprünglichen Wortlaut finden
func _find_text(key: Variant) -> int:
	if key is int:
		return key
	for t in data.get("texts", []):
		if str(t["text"]) == str(key):
			return int(t["i"])
	return -1


func set_text(key: Variant, value: String) -> void:
	var i := _find_text(key)
	if i < 0:
		return
	_overrides[i] = value
	_redraw_texts()


func hide_text(key: Variant, hide := true) -> void:
	var i := _find_text(key)
	if i < 0:
		return
	if hide:
		_hidden[i] = true
	else:
		_hidden.erase(i)
	_redraw_texts()


func _redraw_texts() -> void:
	_text_layer.queue_redraw()
	for b in _buttons:
		b.queue_redraw()


func _draw_free_texts() -> void:
	for t in data.get("texts", []):
		if int(t["button"]) < 0:
			draw_text(_text_layer, t, Vector2.ZERO)


## Einen Mockup-Text zeichnen; origin = Bildschirmpunkt, der Mockup-Punkt (0,0) entspricht
func draw_text(ci: CanvasItem, t: Dictionary, origin: Vector2) -> void:
	var i := int(t["i"])
	if _hidden.has(i):
		return
	var lines: Array = t["lines"]
	if lines.is_empty():
		return
	if _overrides.has(i):
		var parts: PackedStringArray = str(_overrides[i]).split("\n")
		if parts.size() > 1 and parts.size() == lines.size():
			var nl := []
			for k in parts.size():
				nl.append({"rect": lines[k]["rect"], "text": parts[k]})
			lines = nl
		elif lines.size() > 1:
			# mehrere Zeilen im Mockup, eine im Spiel: mittig über alle Zeilen
			var r0: Array = lines[0]["rect"]
			var r1: Array = lines[lines.size() - 1]["rect"]
			var x0 := minf(r0[0], r1[0])
			var x1 := maxf(r0[0] + r0[2], r1[0] + r1[2])
			lines = [{"rect": [x0, (r0[1] + r1[1]) * 0.5, x1 - x0, r0[3]], "text": " ".join(parts)}]
		else:
			lines = [{"rect": lines[0]["rect"], "text": " ".join(parts)}]
	var fs := maxi(1, roundi(float(t["size"]) * s))
	var font := MockFonts.font(str(t["family"]), int(t["weight"]), roundi(float(t.get("ls", 0.0)) * s))
	var col := MockFonts.color(str(t["color"]))
	col.a *= float(t.get("opacity", 1.0))
	var align := str(t.get("align", "center"))
	var in_button := int(t["button"]) >= 0
	var rot := float(t.get("rot", 0.0))
	var sh := MockFonts.shadows(str(t.get("shadow", "")))
	if absf(rot) > 0.1:
		var r0: Array = lines[0]["rect"]
		var c0 := origin + Vector2(r0[0] + r0[2] * 0.5, r0[1] + r0[3] * 0.5) * s
		ci.draw_set_transform(c0, deg_to_rad(rot), Vector2.ONE)
		origin -= c0
	for ln in lines:
		var r: Array = ln["rect"]
		var txt := str(ln["text"])
		var rect := Rect2(origin + Vector2(r[0], r[1]) * s, Vector2(r[2], r[3]) * s)
		var asc := font.get_ascent(fs)
		var desc := font.get_descent(fs)
		var base_y := rect.position.y + (rect.size.y - (asc + desc)) * 0.5 + asc
		if _is_stars(txt):
			_draw_stars(ci, txt, rect, col, sh)
			continue
		var tw := font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var x := rect.position.x + (rect.size.x - tw) * 0.5
		if not in_button and _overrides.has(i):
			if align in ["start", "left"]:
				x = rect.position.x
			elif align in ["end", "right"]:
				x = rect.end.x - tw
		var p := Vector2(x, base_y)
		for d in sh:
			var sc: Color = d[0]
			sc.a *= col.a
			var blur: float = d[2]
			if blur > 1.0:
				ci.draw_string_outline(font, p + d[1] * s, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, maxi(1, roundi(blur * s * 0.7)), Color(sc, sc.a * 0.6))
			else:
				ci.draw_string(font, p + d[1] * s, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, sc)
		ci.draw_string(font, p, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
	if absf(rot) > 0.1:
		ci.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


func _is_stars(txt: String) -> bool:
	if txt.is_empty():
		return false
	for ch in txt:
		if ch != "★" and ch != "☆":
			return false
	return true


## Sterne selbst zeichnen (die Schriften haben kein Sternzeichen)
func _draw_stars(ci: CanvasItem, txt: String, rect: Rect2, col: Color, sh: Array) -> void:
	var n := txt.length()
	var r := rect.size.y * 0.42
	var step := rect.size.x / float(n)
	for k in n:
		var c := Vector2(rect.position.x + step * (k + 0.5), rect.position.y + rect.size.y * 0.52)
		var pts := PackedVector2Array()
		for j in 10:
			var rr := r if j % 2 == 0 else r * 0.45
			pts.append(c + Vector2.from_angle(-PI * 0.5 + j * PI / 5.0) * rr)
		for d in sh:
			if float(d[2]) <= 1.0:
				var moved := PackedVector2Array()
				for q in pts:
					moved.append(q + d[1] * s)
				ci.draw_colored_polygon(moved, d[0])
		ci.draw_colored_polygon(pts, col if txt[k] == "★" else Color(col, col.a * 0.35))


# --- Knöpfe --------------------------------------------------------------------------------

func buttons() -> Array[MockButton]:
	return _buttons


## Knopf über Ziel („#shop“, „Missionen.dc.html“), Handlungsnamen oder Beschriftung finden
func button(key: String) -> MockButton:
	for b in _buttons:
		var i: Dictionary = b.info
		if str(i.get("href", "")) == key or str(i.get("on", "")) == key or str(i.get("label", "")) == key:
			return b
	for b in _buttons:
		for t in b.texts():
			if str(t["text"]) == key:
				return b
	return null


func texts_of_button(i: int) -> Array:
	var out := []
	for t in data.get("texts", []):
		if int(t["button"]) == i:
			out.append(t)
	return out


# --- Live-Elemente (stellt das Spiel selbst dar) -------------------------------------------

func live_rect(id: String) -> Rect2:
	return _live.get(id, Rect2())


## Bild eines Live-Elements (falls beim Export mit aufgenommen) als TextureRect an seiner Stelle;
## der Drehpunkt liegt in der Mitte des Elements (z. B. für das Glücksrad).
func live_image(id: String, front := false) -> TextureRect:
	var l: Dictionary = _live_info.get(id, {})
	if str(l.get("img", "")) == "":
		return null
	var tr := TextureRect.new()
	tr.texture = load("res://ui_mock/%s/%s" % [screen, l["img"]])
	tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	tr.stretch_mode = TextureRect.STRETCH_SCALE
	tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var ir: Array = l["img_rect"]
	var r := Rect2(ir[0], ir[1], ir[2], ir[3])
	place_at(tr, r, front)
	var lr: Rect2 = _live[id]
	tr.set_meta("pivot_frac", (lr.get_center() - r.position) / r.size)
	tr.pivot_offset = tr.size * (tr.get_meta("pivot_frac") as Vector2)
	return tr


## Ein Popup über diesem Bildschirm öffnen; schließt sich über close_overlay()
func open_overlay(name: String) -> MockView:
	var v := MockView.new(screen, state, name)
	add_child(v)
	v.button_pressed.connect(func(b: Dictionary) -> void: button_pressed.emit(b))
	v.modulate.a = 0.0
	v.create_tween().tween_property(v, "modulate:a", 1.0, 0.15)
	return v


func close_overlay(v: MockView) -> void:
	if is_instance_valid(v):
		v.queue_free()


## Ein eigenes Element an die Stelle eines Live-Elements aus dem Mockup setzen
func place(id: String, c: Control, front := false) -> void:
	if not _live.has(id):
		return
	_placed[id] = c
	(_btn_layer if front else _live_layer).add_child(c)
	var r: Rect2 = _live[id]
	c.position = to_screen(r.position)
	c.size = r.size * s


## Etwas frei an Mockup-Koordinaten setzen (Rechteck in Mockup-Punkten)
func place_at(c: Control, r: Rect2, front := false) -> void:
	var id := "_frei_%d" % _placed.size()
	_live[id] = r
	_placed[id] = c
	(_btn_layer if front else _live_layer).add_child(c)
	c.position = to_screen(r.position)
	c.size = r.size * s


class MockButton:
	extends Control
	## Ein Knopf aus dem Mockup: sein Bild, seine Texte, drückt sich beim Antippen leicht ein.
	var view: MockView
	var info: Dictionary
	var texture: Texture2D
	var enabled := true
	var badge := false:
		set(v):
			badge = v
			queue_redraw()
	var badge_rect := Rect2()   # Lage des roten Punkts im Mockup (Mockup-Punkte)
	var _down := false

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_STOP

	func texts() -> Array:
		return view.texts_of_button(int(info["i"]))

	func fit() -> void:
		var hit: Array = info["rect"]
		position = view.to_screen(Vector2(hit[0], hit[1]))
		size = Vector2(hit[2], hit[3]) * view.s
		pivot_offset = size * 0.5
		queue_redraw()

	func _draw() -> void:
		var hit: Array = info["rect"]
		var origin := -Vector2(hit[0], hit[1]) * view.s
		if texture and info.has("img_rect"):
			var ir: Array = info["img_rect"]
			draw_texture_rect(texture, Rect2(origin + Vector2(ir[0], ir[1]) * view.s, Vector2(ir[2], ir[3]) * view.s), false)
		for t in texts():
			view.draw_text(self, t, origin)
		if badge:
			var br := badge_rect if badge_rect.size != Vector2.ZERO else Rect2(hit[0] + hit[2] - 10.0, hit[1] - 2.0, 12.0, 12.0)
			var p := origin + br.get_center() * view.s
			var r := br.size.x * 0.5 * view.s
			draw_circle(p, r, Color(1, 1, 1))
			draw_circle(p, r - 2.0 * view.s, Color(1.0, 0.23, 0.19))

	func _gui_input(e: InputEvent) -> void:
		var press := false
		var release := false
		if e is InputEventMouseButton and (e as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT:
			press = e.pressed
			release = not e.pressed
		if press and enabled:
			_down = true
			_squash(0.93)
			accept_event()
		elif release and _down:
			_down = false
			_squash(1.0)
			accept_event()
			if Rect2(Vector2.ZERO, size).has_point(get_local_mouse_position()):
				view.button_pressed.emit(info)

	func _squash(to: float) -> void:
		var tw := create_tween()
		tw.tween_property(self, "scale", Vector2.ONE * to, 0.08)
