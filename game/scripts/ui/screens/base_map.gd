class_name BaseMap
extends Control
## Basislager als Karte (Vorlage_Raw/Raumbasis_Wege_v1): leere Bauplätze mit Wegen als Hintergrund,
## gebaute Gebäude als freigestellte Bilder darüber (ui/base, tools/base_cutout.py). Gesperrte Plätze
## bleiben leer; das nächste Ausbauziel bekommt einen Knopf „Bauen“ bzw. ein Schloss mit Bedingung.
## Ziehen verschiebt, zwei Finger oder Mausrad zoomen (am Fingerpunkt), Antippen öffnet das Gebäude.
## Verschieben endet an der obersten aktiven Reihe, damit man nicht in leere Flächen scrollt.

signal building_pressed(id: String)

const IMG_W := 724.0
const IMG_H := 2172.0
const MAX_ZOOM := 2.6

var _bg: Texture2D
var _tex := {}
var _layout := {}
var _zoom := 1.0      # Bildpunkte je Vorlagen-Punkt
var _min_zoom := 0.5
var _pan := Vector2.ZERO   # Vorlagen-Punkt oben links im Bild
var _touches := {}
var _press_pos := Vector2.ZERO
var _moved := 0.0
var _t := 0.0
var _font: Font


func _ready() -> void:
	clip_contents = true
	mouse_filter = Control.MOUSE_FILTER_STOP
	_bg = load("res://ui/base/basis_leer.webp")
	_layout = JSON.parse_string(FileAccess.get_file_as_string("res://ui/base/layout.json"))["buildings"]
	_font = MockFonts.font("Fredoka", 700)
	resized.connect(_fit)
	_fit.call_deferred()


func _tex_of(id: String) -> Texture2D:
	if not _tex.has(id):
		var p := "res://ui/base/geb_%s.png" % id
		_tex[id] = load(p) if ResourceLoader.exists(p) else null
	return _tex[id]


## Oberste Kante des aktiven Bereichs (gebaute Gebäude und das nächste Ziel) in Vorlagen-Punkten
func _active_top() -> float:
	var top := IMG_H
	for d in BaseData.BUILDINGS:
		var id: String = d["id"]
		if Save.base_state(id) != "locked" or id == _next_locked():
			var r: Array = _layout[id]["rect"]
			top = minf(top, float(r[1]))
	return maxf(0.0, top - 90.0)


## Nächster gesperrter Platz (wird als Ausbauziel mit Schloss gezeigt)
func _next_locked() -> String:
	for d in BaseData.BUILDINGS:
		if Save.base_state(d["id"]) == "locked":
			return d["id"]
	return ""


func _fit() -> void:
	if size.x <= 0:
		return
	_zoom = size.x / IMG_W
	_min_zoom = minf(_zoom, size.y / maxf(1.0, IMG_H - _active_top()))
	_pan = Vector2(0, IMG_H - size.y / _zoom)
	_clamp()
	queue_redraw()


func _clamp() -> void:
	_zoom = clampf(_zoom, _min_zoom, MAX_ZOOM)
	var view := size / _zoom
	var top := _active_top()
	_pan.x = clampf(_pan.x, minf(0.0, IMG_W - view.x) if view.x > IMG_W else 0.0, maxf(0.0, IMG_W - view.x))
	if view.x > IMG_W:
		_pan.x = (IMG_W - view.x) * 0.5
	var lo := top
	var hi := IMG_H - view.y
	_pan.y = clampf(_pan.y, minf(lo, hi), maxf(lo, hi))


func _to_screen(p: Vector2) -> Vector2:
	return (p - _pan) * _zoom


func _to_img(p: Vector2) -> Vector2:
	return p / _zoom + _pan


func _zoom_at(screen_p: Vector2, factor: float) -> void:
	var before := _to_img(screen_p)
	_zoom = clampf(_zoom * factor, _min_zoom, MAX_ZOOM)
	_pan = before - screen_p / _zoom
	_clamp()
	queue_redraw()


func _gui_input(e: InputEvent) -> void:
	if e is InputEventMouseButton:
		var mb := e as InputEventMouseButton
		if mb.button_index == MOUSE_BUTTON_WHEEL_UP and mb.pressed:
			_zoom_at(mb.position, 1.1)
		elif mb.button_index == MOUSE_BUTTON_WHEEL_DOWN and mb.pressed:
			_zoom_at(mb.position, 1.0 / 1.1)
		elif mb.button_index == MOUSE_BUTTON_LEFT:
			if mb.pressed:
				_press_pos = mb.position
				_moved = 0.0
			elif _moved < 12.0 and _touches.size() <= 1:
				_tap(mb.position)
	elif e is InputEventMouseMotion and ((e as InputEventMouseMotion).button_mask & MOUSE_BUTTON_MASK_LEFT) and _touches.size() <= 1:
		var mm := e as InputEventMouseMotion
		_moved += mm.relative.length()
		_pan -= mm.relative / _zoom
		_clamp()
		queue_redraw()
	elif e is InputEventScreenTouch:
		var st := e as InputEventScreenTouch
		if st.pressed:
			_touches[st.index] = st.position
		else:
			_touches.erase(st.index)
	elif e is InputEventScreenDrag:
		var sd := e as InputEventScreenDrag
		if _touches.size() >= 2 and _touches.has(sd.index):
			# Zwei Finger: Abstand ändert den Maßstab, Mitte bleibt unter den Fingern
			var other: Vector2 = Vector2.ZERO
			for k in _touches.keys():
				if k != sd.index:
					other = _touches[k]
			var old_d := (_touches[sd.index] as Vector2).distance_to(other)
			var new_d := sd.position.distance_to(other)
			_touches[sd.index] = sd.position
			_moved += 100.0
			if old_d > 4.0:
				_zoom_at((sd.position + other) * 0.5, new_d / old_d)
		elif _touches.has(sd.index):
			_touches[sd.index] = sd.position


func _tap(p: Vector2) -> void:
	var ip := _to_img(p)
	for d in BaseData.BUILDINGS:
		var id: String = d["id"]
		var r: Array = _layout[id]["rect"]
		if Rect2(r[0], r[1], r[2], r[3]).has_point(ip):
			if Save.base_state(id) != "locked" or id == _next_locked():
				Sfx.play("click")
				building_pressed.emit(id)
			return


## Auf ein Gebäude zoomen (Gebäude-Fokus)
func focus(id: String) -> void:
	var r: Array = _layout[id]["rect"]
	var c := Vector2(float(r[0]) + float(r[2]) * 0.5, float(r[1]) + float(r[3]) * 0.5)
	_zoom = clampf(size.x / (float(r[2]) * 1.8), _min_zoom, MAX_ZOOM)
	_pan = c - size * 0.5 / _zoom
	_clamp()
	queue_redraw()


func overview() -> void:
	_fit()


func _process(delta: float) -> void:
	_t += delta
	queue_redraw()


func _draw() -> void:
	if _bg == null:
		return
	draw_texture_rect(_bg, Rect2(_to_screen(Vector2.ZERO), Vector2(IMG_W, IMG_H) * _zoom), false)
	var next := _next_locked()
	for d in BaseData.BUILDINGS:
		var id: String = d["id"]
		var r: Array = _layout[id]["rect"]
		var rect := Rect2(_to_screen(Vector2(r[0], r[1])), Vector2(r[2], r[3]) * _zoom)
		var foot: Array = _layout[id]["foot"]
		var fp := _to_screen(Vector2(foot[0], foot[1]))
		var st := Save.base_state(id)
		if st == "built":
			var tex := _tex_of(id)
			if tex:
				draw_texture_rect(tex, rect, false)
			_plaque(fp + Vector2(0, -6 * _zoom), "St. %d" % Save.base_level(id), Color("#6a5ad8"), Color("#43349e"))
			if d["kind"] == "prod" and Save.base_stock(id) >= 1.0:
				_bubble(rect, str(d["item"]))
		elif st == "buildable":
			var bob := sin(_t * 4.0) * 3.0
			var c := rect.get_center() + Vector2(0, bob)
			_button(c, "BAUEN", "%s Gold" % MockScreen.num(int(d["gold"])), Save.gold() >= int(d["gold"]))
		elif id == next:
			_lock(rect.get_center(), Save.base_lock_text(id))


func _plaque(c: Vector2, txt: String, c1: Color, c2: Color) -> void:
	var fs := maxi(8, roundi(11 * _zoom))
	var w := _font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + 14 * _zoom
	var r := Rect2(c - Vector2(w * 0.5, 9 * _zoom), Vector2(w, 18 * _zoom))
	MockPaint.rrect(self, Rect2(r.position + Vector2(0, 2 * _zoom), r.size), 9 * _zoom, Color(0.1, 0.05, 0.3, 0.8))
	MockPaint.rrect(self, r, 9 * _zoom, c1, c2)
	MockPaint.border(self, r, 9 * _zoom, Color.WHITE, maxf(1.0, 1.5 * _zoom))
	draw_string(_font, Vector2(r.position.x + 7 * _zoom, r.position.y + 13.5 * _zoom), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color.WHITE)


func _bubble(rect: Rect2, item: String) -> void:
	var bob := sin(_t * 3.5 + rect.position.x) * 3.0 * _zoom
	var c := Vector2(rect.position.x + rect.size.x * 0.72, rect.position.y + 18 * _zoom + bob)
	var r := 17.0 * _zoom
	draw_circle(c + Vector2(0, 2 * _zoom), r, Color(0.1, 0.05, 0.3, 0.6))
	draw_circle(c, r, Color(1, 1, 1, 0.95))
	draw_arc(c, r, 0, TAU, 32, Color("#7a5ad8"), 2.0 * _zoom, true)
	var k := r * 1.1 / 12.0
	var o := c - Vector2(12, 12) * k
	match item:
		"gold":
			Gem3D.draw_coin(self, o, k, _t)
		"gems":
			Gem3D.draw_gem(self, o, k, _t)
		"energy":
			Gem3D.draw_bolt(self, o, k, _t)
		"cards":
			for k2 in 2:
				var cr := Rect2(c + Vector2(-7 + k2 * 4, -9 + k2 * 2) * _zoom, Vector2(11, 15) * _zoom)
				MockPaint.rrect(self, cr, 2 * _zoom, Color("#8fd0ff") if k2 == 1 else Color("#6fb4ff"))
				MockPaint.border(self, cr, 2 * _zoom, Color("#1a3a80"), maxf(1.0, 1.2 * _zoom))
		_:
			MockPaint.star(self, Rect2(c - Vector2(r, r) * 0.6, Vector2(r, r) * 1.2), Color("#ffd34d"), Color("#a86a00"), 1.5 * _zoom)


func _button(c: Vector2, title: String, sub: String, ok: bool) -> void:
	var r := Rect2(c - Vector2(52, 20) * _zoom, Vector2(104, 40) * _zoom)
	MockPaint.rrect(self, Rect2(r.position + Vector2(0, 4 * _zoom), r.size), 14 * _zoom, Color("#a86a00"))
	MockPaint.rrect(self, r, 14 * _zoom, Color("#ffe27a") if ok else Color("#d0c8a0"), Color("#f0a81f") if ok else Color("#a89870"))
	var fs := maxi(8, roundi(15 * _zoom))
	var tw := _font.get_string_size(title, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	draw_string(_font, Vector2(c.x - tw * 0.5, r.position.y + 18 * _zoom), title, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color("#4a2000"))
	var f2 := MockFonts.font("Nunito", 800)
	var fs2 := maxi(7, roundi(10 * _zoom))
	var tw2 := f2.get_string_size(sub, HORIZONTAL_ALIGNMENT_LEFT, -1, fs2).x
	draw_string(f2, Vector2(c.x - tw2 * 0.5, r.position.y + 32 * _zoom), sub, HORIZONTAL_ALIGNMENT_LEFT, -1, fs2, Color("#4a2000"))


func _lock(c: Vector2, txt: String) -> void:
	var r := 18.0 * _zoom
	draw_circle(c, r + 3 * _zoom, Color(0.06, 0.04, 0.16, 0.75))
	var body := Rect2(c + Vector2(-9, -2) * _zoom, Vector2(18, 14) * _zoom)
	draw_arc(c + Vector2(0, -3) * _zoom, 6 * _zoom, PI, TAU, 16, Color("#e8e2ff"), 3 * _zoom, true)
	MockPaint.rrect(self, body, 3 * _zoom, Color("#ffe27a"), Color("#e8960f"))
	var f2 := MockFonts.font("Nunito", 800)
	var fs := maxi(7, roundi(11 * _zoom))
	var tw := f2.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var tr := Rect2(Vector2(c.x - tw * 0.5 - 8 * _zoom, c.y + r + 6 * _zoom), Vector2(tw + 16 * _zoom, 18 * _zoom))
	MockPaint.rrect(self, tr, 8 * _zoom, Color(0.06, 0.04, 0.16, 0.8))
	draw_string(f2, Vector2(tr.position.x + 8 * _zoom, tr.position.y + 13 * _zoom), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color("#e8e2ff"))
