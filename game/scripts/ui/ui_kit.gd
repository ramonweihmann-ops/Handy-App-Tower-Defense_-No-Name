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


## Weiche „Bonbon“-Fläche: abgerundet, Farbverlauf, Glanzkante oben, dunkler Rand, weicher
## Schatten. Wird einmal als kleines Bild erzeugt und dann als 9-Slice gestreckt.
## style: "button" (mit 3D-Kante unten), "panel" (ruhiger) oder "bar" (für Balken).
static var _candy_cache := {}


static func candy(color: Color, radius := 22, style := "button") -> StyleBoxTexture:
	var key := "%s|%d|%s" % [color.to_html(), radius, style]
	if _candy_cache.has(key):
		return _candy_cache[key]
	var pad := 10 if style != "bar" else 2
	var inner := radius * 2 + 12
	var size := inner + pad * 2
	var img := Image.create(size, size, false, Image.FORMAT_RGBA8)
	var r := float(radius)
	var top := color.lightened(0.22)
	var bottom := color.darkened(0.14)
	var bevel := color.darkened(0.38)
	var edge := color.darkened(0.5)
	var bevel_h := 7.0 if style == "button" else 0.0
	var gloss := 0.32 if style == "button" else (0.16 if style == "panel" else 0.4)
	var c0 := Vector2(size * 0.5, size * 0.5)
	var half := inner * 0.5
	for y in size:
		for x in size:
			var p := Vector2(x + 0.5, y + 0.5)
			var d := _rr_sdf(p - c0, half, r)
			var col := Color(0, 0, 0, 0)
			# weicher Schatten unter der Fläche
			if style != "bar":
				var ds := _rr_sdf(p - c0 - Vector2(0, 5), half, r)
				var sa := clampf(1.0 - (ds + 1.0) / 9.0, 0.0, 1.0)
				col = Color(0.02, 0.0, 0.08, 0.42 * sa * sa)
			var a := clampf(0.5 - d, 0.0, 1.0)
			if a > 0.0:
				var t := clampf((p.y - (c0.y - half)) / inner, 0.0, 1.0)
				var c := top.lerp(bottom, t)
				if bevel_h > 0.0 and p.y > c0.y + half - bevel_h:
					c = bevel
				# Glanz in der oberen Hälfte
				var inner_d := _rr_sdf(p - c0 - Vector2(0, 1), half - 4.0, maxf(2.0, r - 4.0))
				if inner_d < 0.0 and t < 0.48:
					c = c.lerp(Color(1, 1, 1), gloss * (1.0 - t / 0.48))
				# dunkler Rand und helle Innenkante
				if d > -2.2:
					c = c.lerp(edge, 0.85)
				elif d > -4.0 and t < 0.6:
					c = c.lerp(Color(1, 1, 1), 0.28)
				c.a = color.a
				col = col.blend(Color(c.r, c.g, c.b, c.a * a)) if col.a > 0.0 else Color(c.r, c.g, c.b, c.a * a)
			img.set_pixel(x, y, col)
	var sb := StyleBoxTexture.new()
	sb.texture = ImageTexture.create_from_image(img)
	var m := float(radius + pad + 4)
	sb.texture_margin_left = m
	sb.texture_margin_right = m
	sb.texture_margin_top = m
	sb.texture_margin_bottom = m
	sb.expand_margin_left = pad
	sb.expand_margin_right = pad
	sb.expand_margin_top = pad
	sb.expand_margin_bottom = pad
	sb.content_margin_left = 16
	sb.content_margin_right = 16
	sb.content_margin_top = 10
	sb.content_margin_bottom = 10 + bevel_h * 0.6
	_candy_cache[key] = sb
	return sb


## Abstand eines Punkts zu einem abgerundeten Quadrat (negativ = innen).
static func _rr_sdf(p: Vector2, half: float, r: float) -> float:
	var q := Vector2(absf(p.x), absf(p.y)) - Vector2(half - r, half - r)
	return Vector2(maxf(q.x, 0.0), maxf(q.y, 0.0)).length() + minf(maxf(q.x, q.y), 0.0) - r


## Knöpfe federn beim Drücken leicht nach.
static func add_pop(b: Control) -> void:
	b.resized.connect(func() -> void: b.pivot_offset = b.size * 0.5)
	b.gui_input.connect(func(e: InputEvent) -> void:
		if e is InputEventMouseButton and e.button_index == MOUSE_BUTTON_LEFT:
			var tw := b.create_tween()
			if e.pressed:
				tw.tween_property(b, "scale", Vector2(0.93, 0.93), 0.06)
			else:
				tw.tween_property(b, "scale", Vector2(1.04, 1.04), 0.08)
				tw.tween_property(b, "scale", Vector2.ONE, 0.1)
	)


## Kräftigere Schrift für das ganze Spiel (auch für selbst gezeichnete Texte).
static func use_bold_font() -> void:
	if ThemeDB.fallback_font is FontVariation:
		return
	var fv := FontVariation.new()
	fv.base_font = ThemeDB.fallback_font
	fv.variation_embolden = 0.6
	ThemeDB.fallback_font = fv


static func make_theme() -> Theme:
	use_bold_font()
	var t := Theme.new()
	t.default_font = ThemeDB.fallback_font
	t.default_font_size = 26
	t.set_color("font_color", "Label", C_TEXT)
	t.set_color("font_outline_color", "Label", Color(0, 0, 0, 0.8))
	t.set_constant("outline_size", "Label", 6)

	var normal := candy(C_GOLD, 22, "button")
	var hover := candy(C_GOLD.lightened(0.08), 22, "button")
	var pressed := candy(C_GOLD.darkened(0.06), 22, "button")
	var disabled := candy(Color(0.42, 0.44, 0.55), 22, "button")
	t.set_stylebox("normal", "Button", normal)
	t.set_stylebox("hover", "Button", hover)
	t.set_stylebox("pressed", "Button", pressed)
	t.set_stylebox("disabled", "Button", disabled)
	t.set_stylebox("focus", "Button", StyleBoxEmpty.new())
	for state in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color"]:
		t.set_color(state, "Button", Color(0.16, 0.1, 0.03))
	t.set_color("font_disabled_color", "Button", Color(0.75, 0.78, 0.85))
	t.set_font_size("font_size", "Button", 28)

	t.set_stylebox("background", "ProgressBar", box(Color(0.02, 0.0, 0.08, 0.6), 12))
	t.set_stylebox("fill", "ProgressBar", candy(C_ACCENT, 10, "bar"))
	t.set_stylebox("panel", "PanelContainer", candy(Color(0.2, 0.16, 0.42), 24, "panel"))
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
	add_pop(b)
	return b


## Blauer Nebenknopf (z. B. „Menü“).
static func secondary(b: Button) -> Button:
	var base := Color(0.3, 0.42, 0.95)
	b.add_theme_stylebox_override("normal", candy(base, 22, "button"))
	b.add_theme_stylebox_override("hover", candy(base.lightened(0.08), 22, "button"))
	b.add_theme_stylebox_override("pressed", candy(base.darkened(0.06), 22, "button"))
	b.add_theme_stylebox_override("disabled", candy(Color(0.35, 0.37, 0.5), 22, "button"))
	for state in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color"]:
		b.add_theme_color_override(state, C_TEXT)
	b.add_theme_color_override("font_outline_color", Color(0.05, 0.05, 0.2, 0.8))
	b.add_theme_constant_override("outline_size", 5)
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
