class_name UiKit
extends RefCounted
## Farben, Theme und kleine Bausteine für die Oberfläche.

const C_BG := Color(0.05, 0.06, 0.12)
const C_PANEL := Color(0.1, 0.12, 0.22)
const C_ACCENT := Color(0.2, 0.85, 1.0)
const C_GOLD := Color(1.0, 0.8, 0.25)
const C_TEXT := Color(0.95, 0.96, 1.0)
const C_MUTED := Color(0.65, 0.72, 0.85)
const C_MACHINE := Color(0.25, 0.8, 0.75)
const C_STATION := Color(1.0, 0.55, 0.25)


static func box(color: Color, radius := 14, border := 0, border_color := Color.TRANSPARENT) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = color
	sb.set_corner_radius_all(radius)
	if border > 0:
		sb.set_border_width_all(border)
		sb.border_color = border_color
	sb.content_margin_left = 14
	sb.content_margin_right = 14
	sb.content_margin_top = 10
	sb.content_margin_bottom = 10
	return sb


static func make_theme() -> Theme:
	var t := Theme.new()
	t.default_font_size = 26
	t.set_color("font_color", "Label", C_TEXT)
	t.set_color("font_outline_color", "Label", Color(0, 0, 0, 0.8))
	t.set_constant("outline_size", "Label", 6)

	var normal := box(C_GOLD, 16)
	normal.border_width_bottom = 6
	normal.border_color = Color(0.72, 0.48, 0.08)
	var hover := normal.duplicate() as StyleBoxFlat
	hover.bg_color = C_GOLD.lightened(0.15)
	var pressed := normal.duplicate() as StyleBoxFlat
	pressed.bg_color = C_GOLD.darkened(0.1)
	pressed.border_width_bottom = 2
	var disabled := normal.duplicate() as StyleBoxFlat
	disabled.bg_color = Color(0.35, 0.37, 0.45)
	disabled.border_color = Color(0.25, 0.27, 0.33)
	t.set_stylebox("normal", "Button", normal)
	t.set_stylebox("hover", "Button", hover)
	t.set_stylebox("pressed", "Button", pressed)
	t.set_stylebox("disabled", "Button", disabled)
	t.set_stylebox("focus", "Button", StyleBoxEmpty.new())
	for state in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color"]:
		t.set_color(state, "Button", Color(0.16, 0.1, 0.03))
	t.set_color("font_disabled_color", "Button", Color(0.75, 0.78, 0.85))
	t.set_font_size("font_size", "Button", 28)

	t.set_stylebox("background", "ProgressBar", box(Color(0, 0, 0, 0.55), 8))
	t.set_stylebox("fill", "ProgressBar", box(C_ACCENT, 8))
	t.set_stylebox("panel", "PanelContainer", box(C_PANEL, 18, 2, Color(0.25, 0.4, 0.6)))
	return t


static func label(text: String, font_size := 26, color := C_TEXT, align := HORIZONTAL_ALIGNMENT_CENTER) -> Label:
	var l := Label.new()
	l.text = text
	l.horizontal_alignment = align
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_color", color)
	return l


static func wrap_label(text: String, font_size := 22, color := C_TEXT) -> Label:
	var l := label(text, font_size, color)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	return l


static func button(text: String, on_press: Callable, min_width := 280.0) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(min_width, 72)
	b.pressed.connect(on_press)
	return b


## Blauer Nebenknopf (z. B. „Menü“).
static func secondary(b: Button) -> Button:
	var normal := box(Color(0.2, 0.32, 0.55), 16)
	normal.border_width_bottom = 6
	normal.border_color = Color(0.1, 0.18, 0.35)
	var hover := normal.duplicate() as StyleBoxFlat
	hover.bg_color = normal.bg_color.lightened(0.12)
	var pressed := normal.duplicate() as StyleBoxFlat
	pressed.border_width_bottom = 2
	b.add_theme_stylebox_override("normal", normal)
	b.add_theme_stylebox_override("hover", hover)
	b.add_theme_stylebox_override("pressed", pressed)
	for state in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color"]:
		b.add_theme_color_override(state, C_TEXT)
	return b


## Abgedunkelter Hintergrund für Bildschirme über dem Spiel.
static func dim(alpha := 0.65) -> ColorRect:
	var r := ColorRect.new()
	r.color = Color(0.02, 0.02, 0.06, alpha)
	r.set_anchors_preset(Control.PRESET_FULL_RECT)
	r.mouse_filter = Control.MOUSE_FILTER_STOP
	return r


## Reihe aus Sternen für die Stufe einer Karte.
class StarRow extends Control:
	var filled := 0
	var total := 3
	var star_size := 13.0

	func _init(filled_: int, total_: int) -> void:
		filled = filled_
		total = total_
		custom_minimum_size = Vector2(total * star_size * 2.3, star_size * 2.2)
		mouse_filter = Control.MOUSE_FILTER_IGNORE

	func _draw() -> void:
		var step := star_size * 2.3
		var start := (size.x - step * total) * 0.5 + step * 0.5
		for i in total:
			var c := Vector2(start + i * step, size.y * 0.5)
			var pts := PackedVector2Array()
			for k in 10:
				var r := star_size if k % 2 == 0 else star_size * 0.45
				var a := -PI * 0.5 + k * PI / 5.0
				pts.append(c + Vector2(cos(a), sin(a)) * r)
			var col := UiKit.C_GOLD if i < filled else Color(0.3, 0.32, 0.4)
			draw_colored_polygon(pts, col)
