class_name MockPaint
## Zeichenhilfen für Teile der Mockups, die das Spiel selbst zeichnet (weil sie sich ändern):
## abgerundete Flächen mit Farbverlauf, Rahmen, Sterne und Texte in den Mockup-Schriften.
## Alle Rechtecke in Bildschirmpixeln; die Aufrufer rechnen Mockup-Punkte mit view.s um.


## Umriss eines abgerundeten Rechtecks
static func rounded(r: Rect2, rad: float, seg := 6) -> PackedVector2Array:
	var pts := PackedVector2Array()
	rad = minf(rad, minf(r.size.x, r.size.y) * 0.5)
	if rad < 0.5:
		return PackedVector2Array([r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y)])
	var corners := [[r.position + Vector2(r.size.x - rad, rad), -PI * 0.5], [r.end - Vector2(rad, rad), 0.0],
		[Vector2(r.position.x + rad, r.end.y - rad), PI * 0.5], [r.position + Vector2(rad, rad), PI]]
	for c in corners:
		for k in seg + 1:
			var a: float = float(c[1]) + PI * 0.5 * float(k) / float(seg)
			var q := (c[0] as Vector2) + Vector2.from_angle(a) * rad
			# doppelte Punkte (Seite genau so lang wie zwei Rundungen) mag die Dreiecksteilung nicht
			if pts.is_empty() or pts[pts.size() - 1].distance_to(q) > 0.01:
				pts.append(q)
	if pts.size() > 1 and pts[0].distance_to(pts[pts.size() - 1]) <= 0.01:
		pts.remove_at(pts.size() - 1)
	return pts


## Fläche, senkrechter Verlauf von top nach bottom
static func rrect(ci: CanvasItem, r: Rect2, rad: float, top: Color, bottom := Color(0, 0, 0, -1)) -> void:
	if r.size.x <= 0.5 or r.size.y <= 0.5:
		return
	var pts := rounded(r, rad)
	if bottom.a < 0.0:
		ci.draw_colored_polygon(pts, top)
		return
	var cols := PackedColorArray()
	for p in pts:
		cols.append(top.lerp(bottom, (p.y - r.position.y) / r.size.y))
	ci.draw_polygon(pts, cols)


## Fläche, waagrechter Verlauf von left nach right
static func rrect_h(ci: CanvasItem, r: Rect2, rad: float, left: Color, right: Color) -> void:
	if r.size.x <= 0.5 or r.size.y <= 0.5:
		return
	var pts := rounded(r, rad)
	var cols := PackedColorArray()
	for p in pts:
		cols.append(left.lerp(right, (p.x - r.position.x) / r.size.x))
	ci.draw_polygon(pts, cols)


## Rahmen (Linie innen am Rand, wie CSS border)
static func border(ci: CanvasItem, r: Rect2, rad: float, col: Color, width: float) -> void:
	var inner := r.grow(-width * 0.5)
	var pts := rounded(inner, maxf(0.0, rad - width * 0.5))
	pts.append(pts[0])
	ci.draw_polyline(pts, col, width, true)


## Stern aus den Mockups (Pfad „m12 2 3 6.5 7 .8 …“ im 24er-Feld), r = Zielrechteck
static func star(ci: CanvasItem, r: Rect2, fill: Color, stroke := Color(0, 0, 0, 0), width := 0.0) -> void:
	var raw := [Vector2(12, 2), Vector2(15, 8.5), Vector2(22, 9.3), Vector2(16.8, 14.1), Vector2(18.2, 21.1),
		Vector2(12, 17.6), Vector2(5.8, 21), Vector2(7.2, 14), Vector2(2, 9.3), Vector2(9, 8.5)]
	var pts := PackedVector2Array()
	for p in raw:
		pts.append(r.position + p / 24.0 * r.size)
	ci.draw_colored_polygon(pts, fill)
	if width > 0.0 and stroke.a > 0.0:
		pts.append(pts[0])
		ci.draw_polyline(pts, stroke, width, true)


## Text mittig in ein Rechteck (Mockup-Punkte, bezogen auf origin = Bildschirmpunkt von (0,0))
static func text(view: MockView, ci: CanvasItem, txt: String, r: Rect2, family: String, weight: int, size: float,
		color: String, shadow := "", ls := 0.0, origin := Vector2.ZERO) -> void:
	var t := {"i": -1, "lines": [{"rect": [r.position.x, r.position.y, r.size.x, r.size.y], "text": txt}],
		"family": family, "weight": weight, "size": size, "color": color, "shadow": shadow, "ls": ls,
		"align": "center", "button": -1, "opacity": 1.0}
	view.draw_text(ci, t, origin)


## Breite eines Texts in Mockup-Punkten
static func text_width(txt: String, family: String, weight: int, size: float, ls := 0.0) -> float:
	var fs := 64
	var f := MockFonts.font(family, weight, roundi(ls * 64.0 / size))
	return f.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x * size / 64.0
