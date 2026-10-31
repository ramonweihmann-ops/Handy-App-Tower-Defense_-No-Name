class_name Icon
extends Control
## Selbst gezeichnete Symbole (keine fremden Grafiken): Währungen, Menüreiter, Knöpfe.

var kind := ""
var tint := Color(1, 1, 1)
var badge := false
var _t := 0.0


static func make(kind_: String, size_px := 40.0, tint_ := Color(1, 1, 1)) -> Icon:
	var i := Icon.new()
	i.kind = kind_
	i.tint = tint_
	i.custom_minimum_size = Vector2(size_px, size_px)
	i.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return i


func _process(delta: float) -> void:
	if badge or kind == "wheel":
		_t += delta
		queue_redraw()


func _draw() -> void:
	var s := minf(size.x, size.y)
	var c := size * 0.5
	var r := s * 0.5
	match kind:
		"gold":
			draw_circle(c, r * 0.9, Color(0.85, 0.6, 0.1))
			draw_circle(c, r * 0.75, Color(1.0, 0.82, 0.25))
			draw_circle(c + Vector2(-r * 0.25, -r * 0.25), r * 0.2, Color(1, 1, 0.85, 0.8))
		"gem":
			var pts := PackedVector2Array([c + Vector2(-r * 0.85, -r * 0.2), c + Vector2(-r * 0.45, -r * 0.7),
				c + Vector2(r * 0.45, -r * 0.7), c + Vector2(r * 0.85, -r * 0.2), c + Vector2(0, r * 0.85)])
			draw_colored_polygon(pts, Color(0.95, 0.35, 0.95))
			draw_colored_polygon(PackedVector2Array([c + Vector2(-r * 0.45, -r * 0.7), c + Vector2(r * 0.45, -r * 0.7), c + Vector2(0, -r * 0.2)]), Color(1, 0.75, 1))
		"energy":
			var pts := PackedVector2Array([c + Vector2(r * 0.15, -r * 0.9), c + Vector2(-r * 0.55, r * 0.1), c + Vector2(-r * 0.05, r * 0.1),
				c + Vector2(-r * 0.2, r * 0.9), c + Vector2(r * 0.55, -r * 0.15), c + Vector2(r * 0.05, -r * 0.15)])
			draw_colored_polygon(pts, Color(0.45, 1.0, 0.4))
		"star":
			_star(c, r * 0.9, Color(1.0, 0.82, 0.25))
		"cards":
			draw_rect(Rect2(c + Vector2(-r * 0.75, -r * 0.6), Vector2(r * 1.0, r * 1.4)), Color(0.55, 0.65, 0.95))
			draw_rect(Rect2(c + Vector2(-r * 0.25, -r * 0.85), Vector2(r * 1.0, r * 1.4)), Color(0.85, 0.9, 1.0))
			draw_circle(c + Vector2(r * 0.25, -r * 0.3), r * 0.22, Color(0.45, 0.55, 0.85))
			draw_rect(Rect2(c + Vector2(r * 0.0, r * 0.0), Vector2(r * 0.5, r * 0.3)), Color(0.45, 0.55, 0.85))
		"shop":
			draw_rect(Rect2(c + Vector2(-r * 0.8, -r * 0.15), Vector2(r * 1.6, r * 0.95)), Color(0.85, 0.88, 0.95))
			for k in 4:
				var col := Color(0.95, 0.3, 0.35) if k % 2 == 0 else Color(1, 1, 1)
				draw_rect(Rect2(c + Vector2(-r * 0.9 + k * r * 0.45, -r * 0.75), Vector2(r * 0.45, r * 0.6)), col)
			draw_rect(Rect2(c + Vector2(-r * 0.25, r * 0.2), Vector2(r * 0.5, r * 0.6)), Color(0.35, 0.3, 0.5))
		"swords":
			for sgn in [-1.0, 1.0]:
				var a := c + Vector2(-r * 0.75 * sgn, -r * 0.75)
				var b := c + Vector2(r * 0.6 * sgn, r * 0.6)
				draw_line(a, b, Color(0.85, 0.9, 1.0), r * 0.22)
				draw_line(b + Vector2(-r * 0.3 * sgn, r * 0.1), b + Vector2(r * 0.1 * sgn, -r * 0.3), Color(0.95, 0.7, 0.2), r * 0.2)
		"up":
			draw_colored_polygon(PackedVector2Array([c + Vector2(0, -r * 0.9), c + Vector2(-r * 0.8, r * 0.05), c + Vector2(-r * 0.3, r * 0.05),
				c + Vector2(-r * 0.3, r * 0.85), c + Vector2(r * 0.3, r * 0.85), c + Vector2(r * 0.3, r * 0.05), c + Vector2(r * 0.8, r * 0.05)]), Color(1.0, 0.85, 0.2))
		"camp":
			draw_colored_polygon(PackedVector2Array([c + Vector2(0, -r * 0.85), c + Vector2(-r * 0.9, r * 0.75), c + Vector2(r * 0.9, r * 0.75)]), Color(0.95, 0.6, 0.2))
			draw_colored_polygon(PackedVector2Array([c + Vector2(0, -r * 0.1), c + Vector2(-r * 0.3, r * 0.75), c + Vector2(r * 0.3, r * 0.75)]), Color(0.35, 0.2, 0.15))
			draw_line(c + Vector2(0, -r * 0.85), c + Vector2(0, -r), Color(0.4, 1.0, 0.5), 3.0)
		"gear":
			draw_circle(c, r * 0.6, Color(0.75, 0.8, 0.9))
			for k in 8:
				var a := k * TAU / 8.0
				draw_line(c + Vector2(cos(a), sin(a)) * r * 0.5, c + Vector2(cos(a), sin(a)) * r * 0.92, Color(0.75, 0.8, 0.9), r * 0.28)
			draw_circle(c, r * 0.28, Color(0.15, 0.17, 0.27))
		"gift":
			draw_rect(Rect2(c + Vector2(-r * 0.75, -r * 0.2), Vector2(r * 1.5, r * 1.0)), Color(0.95, 0.35, 0.4))
			draw_rect(Rect2(c + Vector2(-r * 0.85, -r * 0.5), Vector2(r * 1.7, r * 0.35)), Color(1.0, 0.45, 0.5))
			draw_rect(Rect2(c + Vector2(-r * 0.13, -r * 0.5), Vector2(r * 0.26, r * 1.3)), Color(1.0, 0.85, 0.25))
			draw_circle(c + Vector2(-r * 0.25, -r * 0.65), r * 0.18, Color(1.0, 0.85, 0.25))
			draw_circle(c + Vector2(r * 0.25, -r * 0.65), r * 0.18, Color(1.0, 0.85, 0.25))
		"wheel":
			for k in 8:
				var a0 := k * TAU / 8.0 + _t
				var pts := PackedVector2Array([c])
				for j in 5:
					var a := a0 + j * TAU / 32.0
					pts.append(c + Vector2(cos(a), sin(a)) * r * 0.9)
				draw_colored_polygon(pts, Color(0.6, 0.35, 1.0) if k % 2 == 0 else Color(0.95, 0.85, 1.0))
			draw_circle(c, r * 0.18, Color(1.0, 0.82, 0.25))
		"trophy":
			draw_colored_polygon(PackedVector2Array([c + Vector2(-r * 0.6, -r * 0.8), c + Vector2(r * 0.6, -r * 0.8), c + Vector2(r * 0.4, r * 0.0), c + Vector2(-r * 0.4, r * 0.0)]), Color(1.0, 0.8, 0.25))
			draw_rect(Rect2(c + Vector2(-r * 0.12, 0), Vector2(r * 0.24, r * 0.5)), Color(1.0, 0.8, 0.25))
			draw_rect(Rect2(c + Vector2(-r * 0.45, r * 0.5), Vector2(r * 0.9, r * 0.3)), Color(0.85, 0.6, 0.15))
		"noads":
			draw_circle(c, r * 0.85, Color(0.95, 0.3, 0.3))
			draw_circle(c, r * 0.65, Color(1, 1, 1))
			draw_line(c + Vector2(-r * 0.5, r * 0.5), c + Vector2(r * 0.5, -r * 0.5), Color(0.95, 0.3, 0.3), r * 0.2)
		"pass":
			draw_colored_polygon(PackedVector2Array([c + Vector2(-r * 0.8, -r * 0.55), c + Vector2(r * 0.8, -r * 0.55), c + Vector2(r * 0.8, r * 0.55), c + Vector2(-r * 0.8, r * 0.55)]), Color(1.0, 0.75, 0.2))
			_star(c, r * 0.4, Color(1, 1, 1))
		"lock":
			draw_rect(Rect2(c + Vector2(-r * 0.55, -r * 0.1), Vector2(r * 1.1, r * 0.9)), Color(0.65, 0.7, 0.8))
			draw_arc(c + Vector2(0, -r * 0.15), r * 0.38, PI, TAU, 16, Color(0.65, 0.7, 0.8), r * 0.18)
		"check":
			draw_polyline(PackedVector2Array([c + Vector2(-r * 0.6, 0), c + Vector2(-r * 0.15, r * 0.5), c + Vector2(r * 0.65, -r * 0.5)]), Color(0.4, 1.0, 0.5), r * 0.28)
		"skull":
			draw_circle(c + Vector2(0, -r * 0.1), r * 0.7, Color(0.9, 0.9, 0.95))
			draw_rect(Rect2(c + Vector2(-r * 0.35, r * 0.4), Vector2(r * 0.7, r * 0.4)), Color(0.9, 0.9, 0.95))
			draw_circle(c + Vector2(-r * 0.28, -r * 0.1), r * 0.18, Color(0.2, 0.15, 0.3))
			draw_circle(c + Vector2(r * 0.28, -r * 0.1), r * 0.18, Color(0.2, 0.15, 0.3))
		"plane":
			draw_colored_polygon(PackedVector2Array([c + Vector2(0, -r * 0.9), c + Vector2(r * 0.15, -r * 0.2), c + Vector2(r * 0.9, r * 0.15),
				c + Vector2(r * 0.9, r * 0.35), c + Vector2(r * 0.15, r * 0.2), c + Vector2(r * 0.12, r * 0.6), c + Vector2(r * 0.4, r * 0.85),
				c + Vector2(-r * 0.4, r * 0.85), c + Vector2(-r * 0.12, r * 0.6), c + Vector2(-r * 0.15, r * 0.2), c + Vector2(-r * 0.9, r * 0.35),
				c + Vector2(-r * 0.9, r * 0.15), c + Vector2(-r * 0.15, -r * 0.2)]), Color(0.75, 0.85, 1.0))
		"medic":
			draw_rect(Rect2(c + Vector2(-r * 0.75, -r * 0.55), Vector2(r * 1.5, r * 1.2)), Color(0.95, 0.95, 1.0))
			draw_rect(Rect2(c + Vector2(-r * 0.15, -r * 0.4), Vector2(r * 0.3, r * 0.9)), Color(0.95, 0.25, 0.3))
			draw_rect(Rect2(c + Vector2(-r * 0.45, -r * 0.1), Vector2(r * 0.9, r * 0.3)), Color(0.95, 0.25, 0.3))
		"clock":
			draw_circle(c, r * 0.85, Color(0.55, 0.85, 1.0))
			draw_circle(c, r * 0.68, Color(0.12, 0.2, 0.35))
			draw_line(c, c + Vector2(0, -r * 0.5), Color(1, 1, 1), r * 0.12)
			draw_line(c, c + Vector2(r * 0.38, 0), Color(1, 1, 1), r * 0.12)
		"dome":
			draw_arc(c + Vector2(0, r * 0.4), r * 0.85, PI, TAU, 24, Color(0.4, 0.9, 1.0), r * 0.2)
			draw_rect(Rect2(c + Vector2(-r * 0.9, r * 0.35), Vector2(r * 1.8, r * 0.18)), Color(0.75, 0.8, 0.9))
		"crate":
			draw_rect(Rect2(c + Vector2(-r * 0.75, -r * 0.6), Vector2(r * 1.5, r * 1.3)), Color(0.75, 0.5, 0.25))
			draw_rect(Rect2(c + Vector2(-r * 0.75, -r * 0.6), Vector2(r * 1.5, r * 1.3)), Color(0.45, 0.28, 0.12), false, r * 0.12)
			for k in 3:
				draw_circle(c + Vector2(-r * 0.35 + k * r * 0.35, -r * 0.05), r * 0.14, Color(1.0, 0.82, 0.28))
	if badge:
		var bc := Vector2(size.x - 6.0, 6.0)
		draw_circle(bc, 10.0 + sin(_t * 5.0), Color(0.95, 0.2, 0.25))
		draw_string(ThemeDB.fallback_font, bc + Vector2(-10, 6), "!", HORIZONTAL_ALIGNMENT_CENTER, 20, 16, Color(1, 1, 1))


func _star(c: Vector2, r: float, col: Color) -> void:
	var pts := PackedVector2Array()
	for k in 10:
		var rr := r if k % 2 == 0 else r * 0.45
		var a := -PI * 0.5 + k * PI / 5.0
		pts.append(c + Vector2(cos(a), sin(a)) * rr)
	draw_colored_polygon(pts, col)
