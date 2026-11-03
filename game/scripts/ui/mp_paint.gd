class_name MpPaint
## Zeichenhilfen für die Multiplayer-Bildschirme (Mockups „Multiplayer · …“, „Rangliste · Liga“):
## runde Heldenbilder mit Ring, Totenkopf (besiegte Gegner), Pokal, Uhr. Alle Maße in Bildpunkten.

## Hintergrund des Rundbilds je Held (Verlauf wie im Mockup: hell oben links, dunkel unten rechts)
const HERO_BG := {
	"dusty": [Color("#ffd34d"), Color("#e8960f")], "iska": [Color("#6fb4ff"), Color("#3a64d8")],
	"margot": [Color("#ff9fc3"), Color("#c2508f")], "lynx": [Color("#7a4bff"), Color("#3a1f9a")],
	"volta": [Color("#6fe8d0"), Color("#1f8f9a")], "brocken": [Color("#ff8a7a"), Color("#c0303a")],
	"kalle": [Color("#ffb070"), Color("#c8661a")], "fritzi": [Color("#9dff7a"), Color("#3f9f3a")],
	"fuenkchen": [Color("#c8a0ff"), Color("#6a3fd8")], "pip": [Color("#8fe8e8"), Color("#1f8f9a")],
	"rollo": [Color("#ffc070"), Color("#d8661a")], "nova": [Color("#d0a8ff"), Color("#5a2a9a")],
}

static var _tex := {}


static func avatar_tex(id: String) -> Texture2D:
	if not _tex.has(id):
		var path := "res://ui/avatars/%s.png" % id
		_tex[id] = load(path) if ResourceLoader.exists(path) else null
	return _tex[id]


## Rundbild: Mittelpunkt c, Durchmesser d, Ring in ring (Breite rw); dim = ausgegraut (ausgeschieden)
static func avatar(ci: CanvasItem, c: Vector2, d: float, id: String, ring := Color.WHITE, rw := 2.0, dim := false) -> void:
	var r := d * 0.5
	var bg: Array = HERO_BG.get(id, [Color("#a98cff"), Color("#5a3fd8")])
	var c1: Color = bg[0]
	var c2: Color = bg[1]
	if dim:
		c1 = _gray(c1)
		c2 = _gray(c2)
	ci.draw_circle(c + Vector2(0, d * 0.06), r, Color(0, 0, 0, 0.35))
	# Verlauf in Ringen (radial-gradient at 35% 30%)
	var steps := 10
	for i in steps:
		var f := 1.0 - float(i) / steps
		ci.draw_circle(c + Vector2(-0.15, -0.2) * d * (1.0 - f), r * f, c2.lerp(c1, float(i) / (steps - 1)))
	var tex := avatar_tex(id)
	if tex:
		var pts := PackedVector2Array()
		var uvs := PackedVector2Array()
		var inner := r - rw * 0.5
		for i in 40:
			var a := TAU * i / 40.0
			var p := Vector2(cos(a), sin(a))
			pts.append(c + p * inner)
			uvs.append(Vector2(0.5, 0.5) + p * 0.5 * inner / r)
		var mod := Color(0.62, 0.62, 0.66, 1.0) if dim else Color.WHITE
		ci.draw_polygon(pts, PackedColorArray([mod]), uvs, tex)
	ci.draw_arc(c, r - rw * 0.5, 0.0, TAU, 48, _gray(ring) if dim else ring, rw, true)


static func _gray(c: Color) -> Color:
	var l := c.get_luminance()
	return c.lerp(Color(l, l, l, c.a), 0.8)


## Totenkopf (besiegte Gegner) in einem Quadrat r
static func skull(ci: CanvasItem, r: Rect2) -> void:
	var k := r.size.x / 24.0
	var o := r.position
	var pts := PackedVector2Array()
	for i in 24:
		var a := PI + PI * i / 23.0
		pts.append(o + (Vector2(12, 10.4) + Vector2(cos(a) * 8.0, sin(a) * 7.4)) * k)
	for p in [Vector2(20, 10.4), Vector2(19.6, 13.4), Vector2(17.2, 15.5), Vector2(17.2, 19), Vector2(6.8, 19), Vector2(6.8, 15.5), Vector2(4.4, 13.4), Vector2(4, 10.4)]:
		pts.append(o + p * k)
	ci.draw_colored_polygon(pts, Color("#e8e2ff"))
	pts.append(pts[0])
	ci.draw_polyline(pts, Color("#3a2a70"), maxf(1.0, 1.2 * k), true)
	ci.draw_circle(o + Vector2(9, 10.5) * k, 2.0 * k, Color("#3a2a70"))
	ci.draw_circle(o + Vector2(15, 10.5) * k, 2.0 * k, Color("#3a2a70"))
	for x in [9.6, 12.0, 14.4]:
		ci.draw_line(o + Vector2(x, 17) * k, o + Vector2(x, 19) * k, Color("#3a2a70"), maxf(1.0, 1.0 * k))


## Pokal in einem Quadrat r
static func trophy(ci: CanvasItem, r: Rect2) -> void:
	var k := r.size.x / 24.0
	var o := r.position
	var gold := Color("#ffd34d")
	var dark := Color("#a86a00")
	var cup := PackedVector2Array()
	for i in 13:
		var a := PI * i / 12.0
		cup.append(o + (Vector2(12, 7) + Vector2(cos(a) * 5.0, sin(a) * 5.0)) * k)
	cup.append(o + Vector2(7, 3) * k)
	cup.append(o + Vector2(17, 3) * k)
	# Reihenfolge: rechts oben → Bogen unten → links oben
	var ring := PackedVector2Array([o + Vector2(17, 3) * k])
	for p in cup.slice(0, 13):
		ring.append(p)
	ring.append(o + Vector2(7, 3) * k)
	ci.draw_colored_polygon(ring, gold)
	ring.append(ring[0])
	ci.draw_polyline(ring, dark, maxf(1.0, 1.2 * k), true)
	ci.draw_arc(o + Vector2(6, 6.5) * k, 2.6 * k, PI * 0.5, PI * 1.5, 8, dark, maxf(1.0, 1.4 * k), true)
	ci.draw_arc(o + Vector2(18, 6.5) * k, 2.6 * k, -PI * 0.5, PI * 0.5, 8, dark, maxf(1.0, 1.4 * k), true)
	ci.draw_rect(Rect2(o + Vector2(10, 12) * k, Vector2(4, 3) * k), Color("#e8960f"))
	var base := PackedVector2Array([o + Vector2(7, 21) * k, o + Vector2(17, 21) * k, o + Vector2(16, 17) * k, o + Vector2(8, 17) * k])
	ci.draw_colored_polygon(base, gold)
	base.append(base[0])
	ci.draw_polyline(base, dark, maxf(1.0, 1.2 * k), true)
	ci.draw_line(o + Vector2(9, 4) * k, o + Vector2(9, 7) * k, Color("#fff8c8"), maxf(1.0, 1.2 * k), true)


## Uhr in einem Quadrat r
static func clock(ci: CanvasItem, r: Rect2) -> void:
	var k := r.size.x / 24.0
	var c := r.position + Vector2(12, 12) * k
	ci.draw_circle(c, 9.0 * k, Color("#fff4e0"))
	ci.draw_arc(c, 9.0 * k, 0.0, TAU, 32, Color("#6fe0ff"), 2.0 * k, true)
	ci.draw_polyline(PackedVector2Array([c + Vector2(0, -5) * k, c, c + Vector2(3.5, 2) * k]), Color("#2a3a70"), 2.2 * k, true)
