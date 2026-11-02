class_name Gem3D
## Gewinn-Symbole, die sich in 3D drehen (wie in den Mockups „Erfolgsmeldung“): Diamant
## (Doppelpyramide mit 6 Flächen), Goldmünze mit Rand und Energie-Blitz mit Tiefe. Jedes Bild
## wird aus dem Drehwinkel neu berechnet, dadurch läuft die Drehung gleichmäßig und ohne Sprung.
## Maße im 24er-Raster der Mockup-Symbole; o = linke obere Ecke, k = Pixel je Einheit.

const GEM_PERIOD := 1.4     # Sekunden für eine Fläche (60°)
const SPIN_PERIOD := 1.6    # Münze und Blitz: Sekunden für eine halbe Drehung


static func _mix(a: Color, b: Color, t: float) -> Color:
	return a.lerp(b, clampf(t, 0.0, 1.0))


static func draw_gem(ci: CanvasItem, o: Vector2, k: float, t: float) -> void:
	var n := 6
	var step := 360.0 / n
	var phi := step * fmod(t, GEM_PERIOD) / GEM_PERIOD
	var hi := Color8(255, 224, 246)
	var mid := Color8(255, 111, 210)
	var lo := Color8(120, 20, 100)
	ellipse(ci, o + Vector2(12, 23.4) * k, Vector2(6, 1.1) * k, Color(0, 0, 0, 0.3))
	for top in [false, true]:
		for j in n / 2 + 1:
			var base := -90.0 - step + step * j
			var a0 := base + phi
			var a1 := base + step + phi
			var apex := Vector2(12, 3) if top else Vector2(12, 21)
			var pts := PackedVector2Array([o + apex * k, o + _gir(a0) * k, o + _gir(a1) * k])
			var c := cos(deg_to_rad((a0 + a1) * 0.5 + 35.0))
			var kk := clampf(0.5 + 0.5 * c, 0.0, 1.0)
			var col := _mix(mid, hi, kk) if top else _mix(lo, mid, kk * 0.9)
			if absf(_gir(a0).x - _gir(a1).x) > 0.02:
				ci.draw_colored_polygon(pts, col)
				ci.draw_polyline(PackedVector2Array([pts[0], pts[1], pts[2], pts[0]]), Color(1, 1, 1, 0.55 if top else 0.4), maxf(1.0, 0.3 * k), true)
	ci.draw_line(o + Vector2(12, 3) * k, o + Vector2(7, 9.5) * k, Color(1, 1, 1, 0.7), maxf(1.0, 0.6 * k), true)
	_sparkle(ci, o, k, t)


static func _gir(a: float) -> Vector2:
	a = clampf(a, -90.0, 90.0)
	var r := deg_to_rad(a)
	return Vector2(12 + 9.0 * sin(r), 10.0 + 1.4 * cos(r))


static func draw_coin(ci: CanvasItem, o: Vector2, k: float, t: float) -> void:
	var th := PI * fmod(t, SPIN_PERIOD) / SPIN_PERIOD
	var c := absf(cos(th))
	var sn := sin(th)
	var r := 9.0
	var th_w := 1.8
	var xf := 12 - th_w / 2 * sn
	var xb := 12 + th_w / 2 * sn
	var rx := maxf(0.05, r * c)
	ellipse(ci, o + Vector2(12, 23.4) * k, Vector2(6, 1.1) * k, Color(0, 0, 0, 0.3))
	ellipse(ci, o + Vector2(xb, 12) * k, Vector2(rx, r) * k, Color8(138, 82, 0))
	ci.draw_rect(Rect2(o + Vector2(xf, 12 - r) * k, Vector2(xb - xf, 2 * r) * k), Color8(168, 106, 0))
	var face := _mix(Color8(150, 90, 0), Color8(255, 214, 70), 0.55 + 0.45 * c)
	ellipse(ci, o + Vector2(xf, 12) * k, Vector2(rx, r) * k, face)
	# heller Fleck oben links (Wölbung) und Rand
	ellipse(ci, o + Vector2(xf - rx * 0.25, 9.5) * k, Vector2(rx * 0.45, r * 0.4) * k, Color(1, 0.98, 0.8, 0.45 * c))
	ellipse_line(ci, o + Vector2(xf, 12) * k, Vector2(rx, r) * k, Color8(168, 106, 0), maxf(1.0, 0.6 * k))
	ellipse_line(ci, o + Vector2(xf, 12) * k, Vector2(maxf(0.03, r * 0.62 * c), r * 0.62) * k, Color8(255, 243, 176), maxf(1.0, 0.9 * k))
	_sparkle(ci, o, k, t)


static func draw_bolt(ci: CanvasItem, o: Vector2, k: float, t: float) -> void:
	var th := PI * fmod(t, SPIN_PERIOD) / SPIN_PERIOD
	var c := maxf(0.08, absf(cos(th)))
	var off := 1.6 * sin(th)
	var bolt := [Vector2(13, 2), Vector2(4, 14), Vector2(11, 14), Vector2(10, 22), Vector2(19, 10), Vector2(12, 10)]
	ellipse(ci, o + Vector2(12, 23.4) * k, Vector2(6, 1.1) * k, Color(0, 0, 0, 0.3))
	var back := PackedVector2Array()
	var front := PackedVector2Array()
	for p in bolt:
		var q := Vector2(12 + (p.x - 12) * c, p.y)
		back.append(o + (q + Vector2(off, 0)) * k)
		front.append(o + q * k)
	ci.draw_colored_polygon(back, Color8(20, 90, 36))
	ci.draw_colored_polygon(front, _mix(Color8(40, 150, 70), Color8(170, 255, 170), 0.35 + 0.65 * absf(cos(th))))
	var hl := PackedVector2Array()
	for p in [Vector2(13, 2), Vector2(4, 14), Vector2(11, 14), Vector2(13, 8)]:
		hl.append(o + Vector2(12 + (p.x - 12) * c, p.y) * k)
	ci.draw_colored_polygon(hl, Color(1, 1, 1, 0.3))
	front.append(front[0])
	ci.draw_polyline(front, Color8(29, 107, 42), maxf(1.0, 0.9 * k), true)
	_sparkle(ci, o, k, t)


## Pass-Ticket (lila mit goldenem Stern, wie das Pass-Symbol der Mockups), dreht sich wie die Münze
static func draw_ticket(ci: CanvasItem, o: Vector2, k: float, t: float) -> void:
	var th := PI * fmod(t, SPIN_PERIOD) / SPIN_PERIOD
	var c := maxf(0.08, absf(cos(th)))
	var off := 1.4 * sin(th)
	var shape := [Vector2(3, 6), Vector2(21, 6), Vector2(21, 10), Vector2(19.6, 10.6), Vector2(19, 12), Vector2(19.6, 13.4), Vector2(21, 14),
		Vector2(21, 18), Vector2(3, 18), Vector2(3, 14), Vector2(4.4, 13.4), Vector2(5, 12), Vector2(4.4, 10.6), Vector2(3, 10)]
	var fx := func(p: Vector2, dx := 0.0) -> Vector2: return o + Vector2(12 + (p.x - 12) * c + dx, p.y) * k
	ellipse(ci, o + Vector2(12, 23.4) * k, Vector2(6, 1.1) * k, Color(0, 0, 0, 0.3))
	var back := PackedVector2Array()
	var front := PackedVector2Array()
	for p in shape:
		back.append(fx.call(p, off))
		front.append(fx.call(p))
	ci.draw_colored_polygon(back, Color8(58, 21, 128))
	ci.draw_colored_polygon(front, _mix(Color8(90, 42, 200), Color8(160, 110, 255), 0.4 + 0.6 * absf(cos(th))))
	ci.draw_colored_polygon(PackedVector2Array([fx.call(Vector2(3, 6)), fx.call(Vector2(21, 6)), fx.call(Vector2(21, 9)), fx.call(Vector2(3, 9))]), Color(1, 1, 1, 0.22))
	front.append(front[0])
	ci.draw_polyline(front, Color8(58, 21, 128), maxf(1.0, 0.7 * k), true)
	var star := PackedVector2Array()
	for i in 10:
		var a := -PI / 2 + PI * i / 5.0
		var rr := 3.4 if i % 2 == 0 else 1.5
		star.append(fx.call(Vector2(12 + cos(a) * rr, 12.2 + sin(a) * rr)))
	ci.draw_colored_polygon(star, Color8(255, 226, 122))
	star.append(star[0])
	ci.draw_polyline(star, Color8(168, 106, 0), maxf(1.0, 0.4 * k), true)
	_sparkle(ci, o, k, t)


## Blinkendes Funkeln oben rechts (wie im Mockup)
static func _sparkle(ci: CanvasItem, o: Vector2, k: float, t: float) -> void:
	var a := 0.5 + 0.5 * cos(t * TAU / 1.3)
	var c := o + Vector2(21, 2.5) * k
	ci.draw_line(c - Vector2(0, 1.5) * k, c + Vector2(0, 1.5) * k, Color(1, 1, 1, a), maxf(1.0, 0.9 * k), true)
	ci.draw_line(c - Vector2(1.5, 0) * k, c + Vector2(1.5, 0) * k, Color(1, 1, 1, a), maxf(1.0, 0.9 * k), true)


static func ellipse(ci: CanvasItem, c: Vector2, r: Vector2, col: Color, seg := 40) -> void:
	if r.x < 0.01 or r.y < 0.01:
		return
	var pts := PackedVector2Array()
	for i in seg:
		var a := TAU * i / seg
		pts.append(c + Vector2(cos(a) * r.x, sin(a) * r.y))
	ci.draw_colored_polygon(pts, col)


static func ellipse_line(ci: CanvasItem, c: Vector2, r: Vector2, col: Color, w: float, seg := 40) -> void:
	var pts := PackedVector2Array()
	for i in seg + 1:
		var a := TAU * i / seg
		pts.append(c + Vector2(cos(a) * maxf(0.01, r.x), sin(a) * r.y))
	ci.draw_polyline(pts, col, w, true)
