class_name LoadingScreen
extends Control
## Start- und Ladebildschirm (Mockup „Ladebildschirm · Startintro (Comic)“, Vorlage
## Vorlage_Raw/Ladebildschirm_Comic_v2): das Comic-Startbild mit Titel, fünf Helden und dem
## Wurmloch-Koloss, darunter ein echter Ladebalken und die Statuszeile.
## Das Bild wird gleichmäßig skaliert und nie beschnitten (Titel, Gesichter und Stiefel bleiben
## sichtbar); bei anderem Seitenverhältnis füllt eine abgedunkelte, unscharfe Kopie die Ränder.

const W := 390.0
const H := 844.0
const IMAGE := "res://ui/start/ladebildschirm_comic.webp"
## Ladebalken und Statuszeile (Mockup-Punkte, ca. 94 % und 97 % der Bildhöhe)
const BAR := Rect2(40, 790, 310, 16)
const STATUS_Y := 812.0

var progress := 0.0
var _shown := 0.0
var _status_text := "Die Station fährt hoch …"
var _t := 0.0
var _s := 1.0
var _off := Vector2.ZERO
var _fill: TextureRect
var _image: TextureRect
var _front: Control


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	var bg := ColorRect.new()
	bg.color = Color(0.1, 0.07, 0.25)
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)
	var tex: Texture2D = load(IMAGE)
	_fill = TextureRect.new()
	_fill.texture = tex
	_fill.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_fill.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	_fill.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_fill.modulate = Color(0.4, 0.38, 0.55)
	_fill.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_fill)
	_image = TextureRect.new()
	_image.texture = tex
	_image.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_image.stretch_mode = TextureRect.STRETCH_SCALE
	_image.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_image)
	_front = Control.new()
	_front.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_front.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_front.draw.connect(_draw_front)
	add_child(_front)
	resized.connect(_layout)
	_layout()


func set_progress(value: float, status: String) -> void:
	progress = clampf(value, 0.0, 1.0)
	_status_text = status


func _p(v: Vector2) -> Vector2:
	return _off + v * _s


func _layout() -> void:
	if size.x <= 0.0 or size.y <= 0.0:
		return
	_s = minf(size.x / W, size.y / H)
	_off = Vector2((size.x - W * _s) * 0.5, (size.y - H * _s) * 0.5)
	_image.position = _off
	_image.size = Vector2(W, H) * _s
	_front.queue_redraw()


func _process(delta: float) -> void:
	_t += delta
	# Balken läuft weich hinterher, springt nie zurück
	_shown = minf(progress, _shown + delta * 0.9) if _shown < progress else _shown
	_front.queue_redraw()


func _draw_front() -> void:
	var ci := _front
	# leichter Verlauf unten, damit Balken und Text lesbar sind
	var top := _p(Vector2(0, H - 90))
	var bottom := _p(Vector2(W, H))
	ci.draw_polygon(PackedVector2Array([top, Vector2(bottom.x, top.y), bottom, Vector2(top.x, bottom.y)]),
		PackedColorArray([Color(0.055, 0.04, 0.16, 0.0), Color(0.055, 0.04, 0.16, 0.0), Color(0.055, 0.04, 0.16, 0.75), Color(0.055, 0.04, 0.16, 0.75)]))
	var r := Rect2(_p(BAR.position), BAR.size * _s)
	MockPaint.rrect(ci, r.grow(2 * _s), 10 * _s, Color(1.0, 0.75, 0.25, 0.25))
	MockPaint.rrect(ci, r, 8 * _s, Color(10 / 255.0, 6 / 255.0, 30 / 255.0, 0.85))
	var w := r.size.x * clampf(_shown, 0.04, 1.0)
	var fr := Rect2(r.position + Vector2(2, 2) * _s, Vector2(w - 4 * _s, r.size.y - 4 * _s))
	if fr.size.x > 2:
		MockPaint.rrect(ci, fr, 6 * _s, Color("#ffe27a"), Color("#ff9f1c"))
		# wandernder Glanz
		var gx := fmod(_t * 160.0 * _s, fr.size.x + 40 * _s) - 20 * _s
		var g0 := fr.position + Vector2(maxf(0.0, gx), 0)
		var g1 := fr.position + Vector2(minf(fr.size.x, gx + 18 * _s), 0)
		if g1.x > g0.x:
			ci.draw_rect(Rect2(g0, Vector2(g1.x - g0.x, fr.size.y)), Color(1, 1, 1, 0.45))
		ci.draw_rect(Rect2(fr.position + Vector2(4 * _s, 1 * _s), Vector2(maxf(0.0, fr.size.x - 8 * _s), 2 * _s)), Color(1, 1, 1, 0.45))
	MockPaint.border(ci, r, 8 * _s, Color(1.0, 0.89, 0.48, 0.85), 2 * _s)
	var txt := "%s  %d %%" % [_status_text, roundi(_shown * 100.0)]
	var font := MockFonts.font("Nunito", 800)
	var fs := maxi(1, roundi(12 * _s))
	var tw := font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var pos := Vector2(_off.x + (W * _s - tw) * 0.5, _p(Vector2(0, STATUS_Y + 12)).y)
	ci.draw_string(font, pos + Vector2(0, 1.5 * _s), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(0, 0, 0, 0.7))
	ci.draw_string(font, pos, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color("#e8e2ff"))
