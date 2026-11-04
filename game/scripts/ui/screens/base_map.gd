class_name BaseMap
extends Control
## Basislager als Karte nach dem abgenommenen Mockup „Basislager · Übersicht“: das ganze Bild der Basis mit
## allen 30 Gebäuden und Nummernschildern (Vorlage_Raw/Raumbasis_30, wie im Mockup) als Hintergrund. Noch nicht
## gebaute Plätze sind abgedunkelt und zeigen ein Schloss mit Bedingung („ab Level 19“, „mit 7. Champion“)
## oder, wenn baubar, den goldenen Knopf „BAUEN“. Gebaute Gebäude bekommen das Stufen-Schild („St. 2“) und,
## wenn ihr Lager etwas bereit hat, eine Blase mit dem Symbol. Lage und Größen wie im Mockup (Mockup-Punkte
## bei voller Breite = 390 Punkte für 724 Bildpunkte). Ziehen verschiebt, zwei Finger oder Mausrad zoomen,
## Antippen öffnet das Gebäudefenster (BuildingWindow).

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
var _lock_tex: Texture2D
var _hammer_tex: Texture2D
var _cache := {}        # Platz -> zwischengespeicherter Zustand (siehe _refresh_cache)
var _cache_t := 0.0
var _animated := false
var _vig: Texture2D
## Mockup-Punkte je Bildpunkt (Mockup zeigt das 724 Punkte breite Bild auf 390 Punkten)
const K := 390.0 / 724.0
## Bildschirmpunkte oben/unten, die Kopfleiste und Reiterleiste verdecken (Karte lässt sich darunter hervorziehen)
var pad_top := 0.0:
	set(v):
		pad_top = v
		if not _layout.is_empty():
			_clamp()
			queue_redraw()
var pad_bottom := 0.0:
	set(v):
		pad_bottom = v
		if not _layout.is_empty():
			_clamp()
			queue_redraw()


func _ready() -> void:
	clip_contents = true
	mouse_filter = Control.MOUSE_FILTER_STOP
	_bg = load("res://ui/base/basis_voll.webp")
	for item in ["gold", "cards", "energy", "gems", "stars"]:
		_icon(item)
	_lock_tex = _bauplatz_tex("lock")
	_hammer_tex = _bauplatz_tex("hammer")
	_layout = JSON.parse_string(FileAccess.get_file_as_string("res://ui/base/layout.json"))["buildings"]
	_font = MockFonts.font("Fredoka", 700)
	resized.connect(_fit)
	_fit.call_deferred()


func _icon(item: String) -> Texture2D:
	if not _tex.has(item):
		var p := "res://ui/icons/%s.webp" % item
		_tex[item] = load(p) if ResourceLoader.exists(p) else null
	return _tex[item]


func _bauplatz_tex(live_id: String) -> Texture2D:
	for l in MockView.layout_of("bauplatz").get("states", {}).get("main", {}).get("live", []):
		if str(l["id"]) == live_id:
			return load("res://ui_mock/bauplatz/" + str(l["img"]))
	return null


func _fit() -> void:
	if size.x <= 0:
		return
	_zoom = size.x / IMG_W
	_min_zoom = _zoom
	_pan = Vector2(0, IMG_H - (size.y - pad_bottom) / _zoom)
	_clamp()
	queue_redraw()


func _clamp() -> void:
	_zoom = clampf(_zoom, _min_zoom, MAX_ZOOM)
	var view := size / _zoom
	var top := 0.0
	_pan.x = clampf(_pan.x, minf(0.0, IMG_W - view.x) if view.x > IMG_W else 0.0, maxf(0.0, IMG_W - view.x))
	if view.x > IMG_W:
		_pan.x = (IMG_W - view.x) * 0.5
	var lo := top - pad_top / _zoom
	var hi := IMG_H - (size.y - pad_bottom) / _zoom
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
		if not _layout.is_empty():
			_clamp()
			queue_redraw()
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


## Lage des ganzen Basisbilds auf dem Bildschirm (für den unscharfen Hintergrund der Gebäudefenster)
func image_rect_global() -> Rect2:
	return Rect2(get_global_rect().position + _to_screen(Vector2.ZERO), Vector2(IMG_W, IMG_H) * _zoom)


func overview() -> void:
	_fit()


func _process(delta: float) -> void:
	_t += delta
	_cache_t -= delta
	if _cache_t <= 0.0:
		_refresh_cache()
	# Nur neu zeichnen, wenn sich etwas bewegt (Bauen-Knöpfe und Blasen wippen) oder die Karte bewegt wurde
	if _animated:
		queue_redraw()


## Spielstand je Platz zwischenspeichern (einmal pro Sekunde statt in jedem Bild für alle 30 Plätze)
func _refresh_cache() -> void:
	_cache_t = 1.0
	_cache.clear()
	_animated = false
	for d in BaseData.BUILDINGS:
		var id: String = d["id"]
		var st := Save.base_state(id)
		var e := {"st": st}
		if st == "built":
			e["plaque"] = "St. %d" % Save.base_level(id)
			e["ready"] = d["kind"] == "prod" and Save.base_stock(id) >= 1.0
			_animated = _animated or e["ready"]
		elif st == "buildable":
			_animated = true
		else:
			e["lock"] = _lock_text(id)
		_cache[id] = e
	queue_redraw()


## Abdunkelung eines Bauplatzes als vorberechnetes Bild (radialer Verlauf wie im Mockup)
func _vignette_tex() -> Texture2D:
	if _vig == null:
		var g := Gradient.new()
		var c := Color(14 / 255.0, 10 / 255.0, 40 / 255.0)
		g.offsets = PackedFloat32Array([0.0, 0.7, 1.0])
		g.colors = PackedColorArray([Color(c, 0.62), Color(c, 0.52), Color(c, 0.0)])
		var t := GradientTexture2D.new()
		t.gradient = g
		t.fill = GradientTexture2D.FILL_RADIAL
		t.fill_from = Vector2(0.5, 0.5)
		t.fill_to = Vector2(1.0, 0.5)
		t.width = 128
		t.height = 128
		_vig = t
	return _vig


func _draw() -> void:
	if _bg == null:
		return
	draw_texture_rect(_bg, Rect2(_to_screen(Vector2.ZERO), Vector2(IMG_W, IMG_H) * _zoom), false)
	if _cache.is_empty():
		_refresh_cache()
	var m := _zoom / K   # Bildschirmpunkte je Mockup-Punkt
	var view := Rect2(Vector2.ZERO, size).grow(120.0 * _zoom)
	for d in BaseData.BUILDINGS:
		var id: String = d["id"]
		var foot: Array = _layout[id]["foot"]
		var fp := _to_screen(Vector2(foot[0], foot[1]))
		if not view.has_point(fp + Vector2(0, -100) * _zoom):
			continue   # außerhalb des sichtbaren Ausschnitts
		var e: Dictionary = _cache[id]
		var st: String = e["st"]
		if st == "built":
			_plaque(fp + Vector2(-89, -23) * _zoom, str(e["plaque"]), m)
			if e["ready"]:
				_bubble(fp + Vector2(26, -207) * _zoom, str(d["item"]), m)
			continue
		var vc := fp + Vector2(0, -90) * _zoom
		_vignette(vc, Vector2(114, 80) * m)
		if st == "buildable":
			_build_button(vc + Vector2(0, 7.5 + sin(_t * TAU / 1.4) * 1.5) * m, m)
		else:
			_lock(vc + Vector2(0, 11.5) * m, str(e["lock"]), m)


## Bedingung wie im Mockup: „ab Level 19“, „mit 7. Champion“, „erst Nr. 13 bauen“
func _lock_text(id: String) -> String:
	if BaseData.by_champion(id):
		return "mit %d. Champion" % int(id)
	var lv := int(BaseData.info(id)["level"])
	if Save.max_level() < lv:
		return "ab Level %d" % lv
	return "erst Nr. %02d bauen" % (int(id) - 1)


## Abdunkeln eines Bauplatzes: radialer Verlauf (Mitte 62 %, bei 70 % noch 52 %, Rand durchsichtig)
func _vignette(c: Vector2, sz: Vector2) -> void:
	if sz.x < 2.0 or sz.y < 2.0:
		return
	draw_texture_rect(_vignette_tex(), Rect2(c - sz * 0.5, sz), false)


## Stufen-Schild „St. 2“ (oben links an p): Verlauf #6a5ad8 → #43349e, weißer Rand, Schatten 0 2px
func _plaque(p: Vector2, txt: String, m: float) -> void:
	var fs := maxi(6, roundi(11 * m))
	var w := _font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + 14 * m + 3 * m
	var h := 11 * 1.2 * m + 2 * m + 3 * m
	var r := Rect2(p, Vector2(w, h))
	MockPaint.rrect(self, Rect2(r.position + Vector2(0, 2 * m), r.size), 9 * m, Color("#241a66"))
	MockPaint.rrect(self, r, 9 * m, Color("#6a5ad8"), Color("#43349e"))
	MockPaint.border(self, r, 9 * m, Color.WHITE, maxf(1.0, 1.5 * m))
	var base := r.position.y + (h + _font.get_ascent(fs) - _font.get_descent(fs)) * 0.5
	draw_string(_font, Vector2(r.position.x + 8.5 * m, base), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color("#fff7ea"))


## Blase „Lager hat etwas“ (oben links an p), 30 Punkte, wippt wie im Mockup (bob 1,6 s)
func _bubble(p: Vector2, item: String, m: float) -> void:
	var c := p + Vector2(15, 15 - absf(sin(_t * PI / 1.6)) * 3.0) * m
	var r := 15.0 * m
	for k in 4:
		draw_circle(c, r + (6 - k * 1.5) * m, Color(1.0, 226 / 255.0, 122 / 255.0, 0.08 + k * 0.05))
	draw_circle(c + Vector2(0, 3 * m), r, Color(0, 0, 0, 0.3))
	draw_circle(c, r, Color("#7a5ad8"))
	draw_circle(c, r - 2 * m, Color("#f2efff"))
	draw_circle(c + Vector2(-3, -4) * m, r * 0.5, Color(1, 1, 1, 0.7))
	var tex := _icon(item)
	if tex:
		draw_texture_rect(tex, Rect2(c - Vector2(8, 8) * m, Vector2(16, 16) * m), false)


## Goldener Knopf „BAUEN“ mit Hammer (Mitte c), 84 × 30 Punkte
func _build_button(c: Vector2, m: float) -> void:
	var r := Rect2(c - Vector2(42, 15) * m, Vector2(84, 30) * m)
	MockPaint.rrect(self, Rect2(r.position + Vector2(0, 8 * m), r.size), 16 * m, Color(0, 0, 0, 0.25))
	MockPaint.rrect(self, Rect2(r.position + Vector2(0, 5 * m), r.size), 16 * m, Color("#a86a00"))
	MockPaint.rrect(self, r, 16 * m, Color("#ffe27a"), Color("#f0a81f"))
	MockPaint.rrect(self, Rect2(r.position + Vector2(10, 1.5) * m, Vector2(64, 3) * m), 1.5 * m, Color(1, 1, 1, 0.45))
	var fs := maxi(6, roundi(14 * m))
	var tw := _font.get_string_size("BAUEN", HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var total := 15 * m + 4 * m + tw
	var x := c.x - total * 0.5
	if _hammer_tex:
		draw_texture_rect(_hammer_tex, Rect2(Vector2(x - 3 * m, c.y - 10.5 * m), Vector2(21, 21) * m), false)
	var base := c.y + (_font.get_ascent(fs) - _font.get_descent(fs)) * 0.5
	draw_string(_font, Vector2(x + 19 * m, base), "BAUEN", HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color("#4a2000"))


## Schloss mit Bedingung darunter (Mitte des Blocks c), Schrift 10 Punkte mit Schatten
func _lock(c: Vector2, txt: String, m: float) -> void:
	var f2 := MockFonts.font("Nunito", 800)
	var fs := maxi(6, roundi(10 * m))
	var top := c.y - 18 * m
	if _lock_tex:
		draw_texture_rect(_lock_tex, Rect2(Vector2(c.x - 11 * m, top - 1 * m), Vector2(22, 22) * m), false)
	var tw := f2.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var base := top + 22 * m + 10 * m
	draw_string(f2, Vector2(c.x - tw * 0.5, base + 1 * m), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color.BLACK)
	draw_string(f2, Vector2(c.x - tw * 0.5, base), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color("#e8e2ff"))
