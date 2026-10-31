class_name Celebration
extends Control
## Kurze Belohnungs-Feier über dem Menü: Lichtstrahlen, Funken, ein aufspringendes Symbol und
## der Text, was man bekommen hat. Optional fliegen Münzen/Edelsteine zur Kopfleiste.
## Blockiert keine Eingaben und räumt sich nach gut einer Sekunde selbst weg.

const LIFE := 1.5

var kind := "star"
var text := ""
var color := Color(1.0, 0.82, 0.3)
## Ziel in Bildschirmkoordinaten, zu dem kleine Symbole fliegen (leer = keine).
var fly_to := Vector2.INF
var fly_count := 0

var _t := 0.0
var _sparks: Array = []
var _icon: Icon
var _label: Label


static func make(kind_: String, text_: String, color_ := Color(1.0, 0.82, 0.3)) -> Celebration:
	var c := Celebration.new()
	c.kind = kind_
	c.text = text_
	c.color = color_
	return c


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var c := size * Vector2(0.5, 0.42)
	for i in 36:
		var a := randf() * TAU
		var sp := randf_range(260.0, 620.0)
		_sparks.append({"p": c, "v": Vector2(cos(a), sin(a)) * sp, "r": randf_range(3.0, 7.0),
			"c": color.lerp(Color(1, 1, 1), randf() * 0.6)})
	_icon = Icon.make(kind, 150)
	_icon.position = c - Vector2(75, 75)
	_icon.pivot_offset = Vector2(75, 75)
	_icon.scale = Vector2(0.1, 0.1)
	add_child(_icon)
	var tw := _icon.create_tween()
	tw.tween_property(_icon, "scale", Vector2(1.25, 1.25), 0.22).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_property(_icon, "scale", Vector2.ONE, 0.15)
	tw.tween_interval(0.7)
	tw.tween_property(_icon, "modulate:a", 0.0, 0.3)
	_label = UiKit.label(text, 40, color.lerp(Color(1, 1, 1), 0.3))
	_label.add_theme_constant_override("outline_size", 12)
	_label.add_theme_color_override("font_outline_color", Color(0.15, 0.05, 0.2, 0.95))
	_label.position = Vector2(0, c.y + 90)
	_label.size = Vector2(size.x, 60)
	_label.modulate.a = 0.0
	add_child(_label)
	var tl := _label.create_tween()
	tl.tween_property(_label, "modulate:a", 1.0, 0.15)
	tl.parallel().tween_property(_label, "position:y", c.y + 70, 0.4).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tl.tween_interval(0.7)
	tl.tween_property(_label, "modulate:a", 0.0, 0.3)
	if fly_to != Vector2.INF and fly_count > 0:
		for i in fly_count:
			var coin := Icon.make(kind, 44)
			coin.position = c + Vector2(randf_range(-60, 60), randf_range(-40, 40)) - Vector2(22, 22)
			add_child(coin)
			var tc := coin.create_tween()
			tc.tween_interval(0.35 + i * 0.05)
			tc.tween_property(coin, "position", fly_to - Vector2(22, 22), 0.5).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
			tc.parallel().tween_property(coin, "scale", Vector2(0.6, 0.6), 0.5)
			tc.tween_property(coin, "modulate:a", 0.0, 0.05)
	var sfx := get_node_or_null("/root/Sfx")
	if sfx:
		sfx.play("levelup", 0.04, -4.0)


func _process(delta: float) -> void:
	_t += delta
	for s in _sparks:
		s["v"] = (s["v"] as Vector2) * (1.0 - delta * 2.2) + Vector2(0, 260) * delta
		s["p"] = (s["p"] as Vector2) + (s["v"] as Vector2) * delta
	queue_redraw()
	if _t >= LIFE:
		queue_free()


func _draw() -> void:
	var c := size * Vector2(0.5, 0.42)
	var fade := clampf(1.0 - (_t - 0.9) / 0.6, 0.0, 1.0)
	var grow := minf(1.0, _t / 0.25)
	# weiches Leuchten
	for k in 4:
		draw_circle(c, (90.0 + k * 40.0) * grow, Color(color.r, color.g, color.b, 0.08 * fade))
	# sich drehende Lichtstrahlen
	var rays := 12
	for i in rays:
		var a := _t * 0.9 + i * TAU / rays
		var r := 230.0 * grow
		var p1 := c + Vector2(cos(a - 0.09), sin(a - 0.09)) * r
		var p2 := c + Vector2(cos(a + 0.09), sin(a + 0.09)) * r
		draw_colored_polygon(PackedVector2Array([c, p1, p2]), Color(1.0, 0.95, 0.7, 0.13 * fade))
	# Funken
	for s in _sparks:
		var col: Color = s["c"]
		col.a = fade
		draw_circle(s["p"], float(s["r"]) * (0.6 + 0.4 * fade), col)
