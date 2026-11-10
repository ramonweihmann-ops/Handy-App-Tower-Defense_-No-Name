class_name CardPick
extends Control
## Kartenwahl nach jeder Welle, Entwurf B aus dem Mockup („Karten-B-Plasma“ / „Karten-B-Mix“ im
## Schlachtfeld-Bereich, mit den Änderungen des Nutzers): kleine Kärtchen nebeneinander (Kategorie-Band,
## Motiv, Kurztitel, Stufenpunkte, bei Heldenkarten das Porträt), darunter das Detailfeld der gewählten
## Karte und NEHMEN. Alle Maße in Mockup-Punkten (390 × 844), auf den Bildschirm skaliert.
## Die Schriften haben keine Zeichen wie ⚡ ★ ♛ →, deshalb werden diese Symbole als Flächen gezeichnet.

signal picked(card: Dictionary)

const W := 390.0
const H := 844.0

## Kategorien: Name, Farbe, Symbol
const CATS := {
	"plasma": ["PLASMA", Color("ffd367"), "bolt"],
	"waffe": ["WAFFE", Color("42ddf4"), "spark"],
	"super": ["SUPER", Color("ffab52"), "star"],
	"champion": ["CHAMPION", Color("dfa0fc"), "crown"],
	"schild": ["SCHILD", Color("8ff04d"), "shield"],
}
const GOLD := Color("ffd367")
const GREEN := Color("8ff04d")
const TEXT := Color("fff4d7")
const TEXT_SIDE := Color("d6cfe8")
const INK := Color("1a1238")
const DOT_OFF := Color(1, 1, 1, 0.18)
const PORTRAIT_BG := Color("ffb070")

## Kärtchen und Detailfeld wie im Mockup
const ROW_Y := 214.0
const TILE_H := 132.0
const TILE_GAP := 9.0
const ROW_X := 24.0
const ROW_W := 342.0
const PANEL := Rect2(20, 361, 350, 196)
const OK_RECT := Rect2(95, 579, 200, 50)

## Motive je Karte: zuerst res://ui/karten/<Name>.webp (Heldenkarten: <Waffenfamilie>_<Art>, dann
## held_<Art>; Plasma/Schild: Schlüssel mit „_“ statt „:“), sonst diese Ersatzbilder, sonst ein Kreis mit
## Symbol (_fallback_icon). Neue Motive also nur mit dem passenden Namen ablegen.
const KARTEN_DIR := "res://ui/karten/"
const IMAGES := {
	"gate:plus3": "res://ui/karten/gate_x2.webp",
	"gate:fire": "res://ui/karten/flamer_ult.webp",
	"plasma:core": "res://ui/upgrades_v2/icon_core.webp",
	"station:repair": "res://ui/upgrades_v2/symbol_schild.webp",
	"damage": "res://ui/upgrades_v2/tech_damage.webp",
	"crit": "res://ui/upgrades_v2/tech_crit.webp",
}
## Kurztitel auf den Kärtchen (der volle Titel steht im Detailfeld)
const SHORT := {
	"gate:x2": "Verdichter", "gate:plus3": "Großverdichter", "machine:tank": "Tank",
	"machine:rate": "Schneller laden", "plasma:mag": "Magazin +2", "plasma:reload": "Nachladen",
	"plasma:core": "Energiekern", "damage": "Mehr Schaden", "rate": "Feuerrate", "reload": "Nachladen",
	"mag": "Magazin", "crit": "Kritisch",
}
## Titel im Detailfeld, wo der Kartentitel nur ein Wert ist
const LONG := {
	"plasma:mag": "+2 Schuss für alle", "plasma:reload": "Schneller nachladen",
	"plasma:core": "Energiekern lädt schneller",
}

var cards: Array = []
var wave := 1
var s := 1.0
var off := Vector2.ZERO
var _sel := 0
var _tex := {}


func _init(cards_: Array, wave_: int) -> void:
	cards = cards_
	wave = wave_


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	_sel = 1 if cards.size() >= 3 else 0
	resized.connect(_layout)
	_layout()


func _layout() -> void:
	s = minf(size.x / W, size.y / H) if size.x > 0.0 and size.y > 0.0 else 1.0
	off = Vector2((size.x - W * s) * 0.5, (size.y - H * s) * 0.5)
	queue_redraw()


func select(i: int) -> void:
	_sel = i
	queue_redraw()


## Platz eines Kärtchens (Mockup-Punkte); bei vier Karten (Prime) werden sie schmaler
func slot_rect(i: int) -> Rect2:
	var n := maxi(3, cards.size())
	var w := (ROW_W - TILE_GAP * (n - 1)) / n
	var x0 := ROW_X + (ROW_W - (w * cards.size() + TILE_GAP * (cards.size() - 1))) * 0.5
	return Rect2(x0 + i * (w + TILE_GAP), ROW_Y, w, TILE_H)


# --- Was auf einer Karte steht ----------------------------------------------------------------

## Alles, was die Karte zeigt: Kategorie, Titel, Kurztitel, Wirkung, Motiv, Held, Stufen
func face(c: Dictionary) -> Dictionary:
	var kind: String = c.get("kind", "")
	var key: String = c.get("key", "")
	var f := {"title": str(c.get("title", "")), "short": str(c.get("title", "")), "hero": "", "new": false,
		"stars": int(c.get("stars", 0)), "max": int(c.get("max", 1)), "emblem": str(c.get("emblem", "")),
		"text": " ".join(str(c.get("desc", "")).split("\n")),
		"image": _first([KARTEN_DIR + key.replace(":", "_") + ".webp", IMAGES.get(key, "")])}
	match kind:
		"add_hero":
			var id: String = c["hero_id"]
			var d: Dictionary = GameData.HEROES[id]
			f["cat"] = "champion"
			f["new"] = true
			f["image"] = "res://ui/heroes2d/%s.png" % id
			var extra := "Verstärkung: +30 % Schaden, Team +6 %. " if GameData.HERO_TYPE.get(id, "start") == "verstaerkung" else ""
			f["text"] = "%s mit %s: %s %s+10 Munition." % [d["role"], d["weapon"], d["blurb"], extra]
		"hero":
			var hid := key.get_slice(":", 0)
			var mod := key.get_slice(":", 1)
			var fam: String = GameData.HEROES[hid]["family"]
			var first := String(GameData.HEROES[hid]["name"]).split(" ")[0]
			f["hero"] = hid
			f["cat"] = "super" if mod == "ult" else "waffe"
			f["image"] = _first([KARTEN_DIR + "%s_%s.webp" % [fam, mod], KARTEN_DIR + "held_%s.webp" % mod, IMAGES.get(mod, "")])
			f["short"] = SHORT.get(mod, f["title"])
			if mod == "ult":
				var ult: Array = Hero.ULTS[fam]
				f["text"] = "%s Danach %s antippen." % [ult[1], first] if f["stars"] == 0 else "%s wird stärker, länger und schneller wieder bereit." % ult[0]
		"station":
			f["cat"] = "schild"
		_:
			f["cat"] = "plasma"
			f["short"] = SHORT.get(key, f["title"])
			f["title"] = LONG.get(key, f["title"])
	var tx := str(f["text"]).strip_edges()
	if tx != "" and not tx.right(1) in [".", "!", ")"]:
		tx += "."
	f["text"] = tx
	return f


# --- Zeichnen ----------------------------------------------------------------------------------

func _p(v: Vector2) -> Vector2:
	return off + v * s


func _r(r: Rect2) -> Rect2:
	return Rect2(_p(r.position), r.size * s)


func _font(fam: String, weight: int, size_pt: float, spacing_em := 0.0) -> Font:
	return MockFonts.font(fam, weight, roundi(spacing_em * size_pt * s))


func _fs(size_pt: float) -> int:
	return maxi(1, roundi(size_pt * s))


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Color(16 / 255.0, 13 / 255.0, 34 / 255.0, 0.62))
	# Überschrift
	var f1 := _font("Nunito", 800, 13, 0.06)
	_text_center(f1, "WELLE %d GESCHAFFT!" % wave, 195, 142, 13, GREEN)
	var f2 := _font("Fredoka", 700, 26)
	_text_center(f2, "Wähle eine Karte", 195, 162, 26, Color("5a3a00"))
	_text_center(f2, "Wähle eine Karte", 195, 160, 26, GOLD)
	for i in cards.size():
		_draw_tile(i)
	if _sel < cards.size():
		var r := slot_rect(_sel)
		var cx := r.get_center().x
		draw_colored_polygon(PackedVector2Array([_p(Vector2(cx, 350)), _p(Vector2(cx + 11, 362)), _p(Vector2(cx - 11, 362))]), GOLD)
		_draw_panel(cards[_sel])
	_draw_ok()


func _draw_tile(i: int) -> void:
	var f := face(cards[i])
	var cat: Array = CATS[f["cat"]]
	var col: Color = cat[1]
	var r := slot_rect(i)
	var sel := i == _sel
	var bw := 3.0 if sel else 2.0
	if sel:
		_shadow(r, 14, Color(1, 0.83, 0.4, 0.55), 8, Vector2.ZERO)
	else:
		_shadow(r, 14, Color(0, 0, 0, 0.45), 6, Vector2(0, 5))
	_fill_round(r, 14, _vgrad(Color("33275a"), Color("231a44")))
	# Kategorie-Band oben (innerhalb des Rahmens)
	var inner := r.grow(-bw)
	var band := _round_points(inner, 14 - bw)
	var clip := Geometry2D.intersect_polygons(band, _rect_points(Rect2(inner.position, Vector2(inner.size.x, 22))))
	for poly in clip:
		draw_colored_polygon(_screen_pts(poly), col)
	var k := r.size.x / 108.0
	_label_with_symbol(cat[0], cat[2], Vector2(inner.get_center().x, inner.position.y + 11), 10, 0.06, INK, false)
	_round_border(r, 14, bw, GOLD if sel else Color(col, 0.53))
	# Motiv
	var isz := 70.0 * minf(1.0, k)
	var irect := Rect2(inner.get_center().x - isz * 0.5, inner.position.y + 26, isz, isz)
	_image(f, irect, col)
	# Kurztitel und Stufen
	var ft := _font("Fredoka", 700, 13)
	var title := _ellipsis(ft, str(f["short"]), inner.size.x - 8)
	_text_center(ft, title, inner.get_center().x, inner.position.y + 97, 13, TEXT)
	if f["new"]:
		_text_center(_font("Nunito", 800, 9, 0.04), "NEU IM TEAM", inner.get_center().x, inner.position.y + 114, 9, GREEN)
	else:
		_dots(f, Vector2(inner.get_center().x, inner.position.y + 116 + 4.5), true)
	if f["hero"] != "":
		_portrait(f["hero"], Rect2(r.end.x - 35, r.position.y + 25, 30, 30), 2.5)


func _draw_panel(c: Dictionary) -> void:
	var f := face(c)
	var cat: Array = CATS[f["cat"]]
	var col: Color = cat[1]
	_shadow(PANEL, 18, Color(0, 0, 0, 0.5), 12, Vector2(0, 10))
	_fill_round(PANEL, 18, _vgrad(Color("3a2c68"), Color("241a46")))
	_round_border(PANEL, 18, 2.5, GOLD)
	var o := PANEL.position + Vector2(2.5, 2.5)
	var inner_w := PANEL.size.x - 5.0
	# Motiv im Kästchen mit Leuchten
	var box := Rect2(o + Vector2(12, 14), Vector2(104, 104))
	_fill_round(box, 16, _rgrad(Color(col, 0.33), Color(col, 0.063)))
	_image(f, Rect2(box.get_center() - Vector2(49, 49), Vector2(98, 98)), col)
	var hero_name := ""
	if f["hero"] != "":
		hero_name = String(GameData.HEROES[f["hero"]]["name"])
		_portrait(f["hero"], Rect2(box.end.x + 6 - 43, box.position.y - 6, 43, 43), 2.5)
	# Kategorie-Plakette, daneben der Held
	var x := o.x + 128
	var bf := _font("Nunito", 800, 11, 0.04)
	var bwid := _symbol_label_width(cat[0], bf, 11) + 14
	var pill := Rect2(x, o.y + 14, bwid, 17)
	_fill_round(pill, 8.5, null, col)
	_label_with_symbol(cat[0], cat[2], pill.get_center(), 11, 0.04, INK, false)
	if hero_name != "":
		_text_left(_font("Nunito", 800, 12), hero_name, pill.end.x + 6, o.y + 14 + 0.5, 12, TEXT)
	# Titel (bei Heldenkarten einzeilig, darunter Stufen und Champion-Zeile)
	var tw := inner_w - 128 - 10
	var tf := _font("Fredoka", 700, 21)
	var size_pt := 21.0
	if hero_name != "" or f["new"]:
		while size_pt > 15 and _font("Fredoka", 700, size_pt).get_string_size(str(f["title"]), HORIZONTAL_ALIGNMENT_LEFT, -1, _fs(size_pt)).x > tw * s:
			size_pt -= 0.5
		_text_left(_font("Fredoka", 700, size_pt), str(f["title"]), x, o.y + 36 + (21.0 - size_pt) * 0.5, size_pt, TEXT, 1.1)
	else:
		_wrap_left(tf, str(f["title"]), x, o.y + 36, tw, 21, 1.1, TEXT, 2)
	var row_y := o.y + (64.0 if hero_name != "" or f["new"] else 86.0)
	if f["new"]:
		var nf := _font("Nunito", 800, 10)
		var nw := nf.get_string_size("NEU IM TEAM", HORIZONTAL_ALIGNMENT_LEFT, -1, _fs(10)).x / s + 16
		var nr := Rect2(x, row_y, nw, 17)
		_round_border(nr, 8, 1.5, GREEN)
		_text_center(nf, "NEU IM TEAM", nr.get_center().x, row_y + 1.5, 10, GREEN)
	else:
		var dw := _dots(f, Vector2(x, row_y + 7.5), false)
		var sf := _font("Nunito", 800, 11)
		var sx := x + dw + 8
		var a := "Stufe %d" % f["stars"]
		var b := "%d von %d" % [int(f["stars"]) + 1, f["max"]]
		sx = _text_left(sf, a, sx, row_y, 11, TEXT_SIDE)
		_arrow(Vector2(sx + 3, row_y + 8.5), 9, TEXT_SIDE)
		_text_left(sf, b, sx + 15, row_y, 11, TEXT_SIDE)
	if hero_name != "":
		var cf := _font("Nunito", 800, 12, 0.04)
		var champ: Array = CATS["champion"]
		var w := _symbol_label_width(champ[0], cf, 12)
		_label_with_symbol(champ[0], champ[2], Vector2(x + w * 0.5, o.y + 88 + 8.5), 12, 0.04, champ[1], false)
		_text_left(_font("Nunito", 800, 12), hero_name, x + w + 6, o.y + 88, 12, TEXT)
	# Wirkung
	_effect_text(str(f["text"]), Rect2(o.x + 14, o.y + 128, inner_w - 28, 56))


func _draw_ok() -> void:
	var r := OK_RECT
	_fill_round(Rect2(r.position + Vector2(0, 5), r.size), 14, null, Color("23802a"))
	var g := Gradient.new()
	g.offsets = PackedFloat32Array([0.0, 0.6, 1.0])
	g.colors = PackedColorArray([Color("b6ff8a"), Color("5fd83f"), Color("3fbf3a")])
	_fill_round(r, 14, _grad_tex(g, false))
	draw_line(_p(r.position + Vector2(10, 1.5)), _p(Vector2(r.end.x - 10, r.position.y + 1.5)), Color(1, 1, 1, 0.6), 2.0 * s, true)
	_text_center(_font("Fredoka", 700, 21), "NEHMEN", r.get_center().x, r.position.y + 10.5, 21, Color("0f3d12"))


# --- Bausteine ---------------------------------------------------------------------------------

## Motiv „contain“ ins Rechteck, sonst ein leuchtender Kreis mit Symbol
func _image(f: Dictionary, r: Rect2, col: Color) -> void:
	var path: String = f["image"]
	var t := _load(path)
	if t == null:
		_fallback_icon(f, r, col)
		return
	var ts := t.get_size()
	var k := minf(r.size.x / ts.x, r.size.y / ts.y)
	var sz := ts * k
	draw_texture_rect(t, _r(Rect2(r.get_center() - sz * 0.5, sz)), false)


func _fallback_icon(f: Dictionary, r: Rect2, col: Color) -> void:
	var c := r.get_center()
	var rad := r.size.x * 0.42
	draw_circle(_p(c), rad * s, Color(col, 0.22), true, -1.0, true)
	draw_circle(_p(c), rad * 0.78 * s, Color(col, 0.4), true, -1.0, true)
	var em: String = f["emblem"]
	var font := _font("Fredoka", 700, 20)
	var ok := em != "" and em.length() <= 3
	for ch in em:
		ok = ok and font.has_char(ch.unicode_at(0))
	if ok and f["cat"] != "waffe" and f["cat"] != "super":
		var pt := rad * (0.9 if em.length() <= 2 else 0.7)
		_text_center(_font("Fredoka", 700, pt), em, c.x, c.y - pt * 0.62, pt, Color.WHITE)
	else:
		_symbol(CATS[f["cat"]][2], c, rad * 1.1, Color.WHITE)


## Rundes Porträt mit hellem Rand (rect = Außenmaß einschließlich Rand)
func _portrait(hero_id: String, r: Rect2, border: float) -> void:
	var c := r.get_center()
	var rad := r.size.x * 0.5
	draw_circle(_p(c + Vector2(0, 2)), (rad + 1.0) * s, Color(0, 0, 0, 0.3), true, -1.0, true)
	draw_circle(_p(c), rad * s, TEXT, true, -1.0, true)
	draw_circle(_p(c), (rad - border) * s, PORTRAIT_BG, true, -1.0, true)
	var t := _load("res://ui/avatars/%s.png" % hero_id)
	if t == null:
		return
	var pts := PackedVector2Array()
	var uvs := PackedVector2Array()
	var ir := rad - border
	for k in 40:
		var a := TAU * k / 40.0
		var d := Vector2(cos(a), sin(a))
		pts.append(_p(c + d * ir))
		uvs.append(Vector2(0.5, 0.5) + d * 0.5)
	draw_polygon(pts, PackedColorArray([Color.WHITE]), uvs, t)


## Stufenpunkte: gelb = schon genommen, grün = diese Karte, grau = noch offen. Gibt die Breite zurück.
func _dots(f: Dictionary, at: Vector2, centered: bool) -> float:
	var n: int = f["max"]
	var w := n * 12.0 if not centered else n * 9.0 + (n - 1) * 3.0
	var x := at.x - w * 0.5 if centered else at.x
	for i in n:
		var col := GOLD if i < int(f["stars"]) else (GREEN if i == int(f["stars"]) else DOT_OFF)
		var dx := x + (i * 12.0 if centered else 1.5 + i * 12.0)
		_fill_round(Rect2(dx, at.y - 4.5, 9, 9), 3, null, col)
	return w


func _effect_text(txt: String, box: Rect2) -> void:
	var size_pt := 13.5
	var lines: Array = []
	while true:
		lines = _lines(_font("Nunito", 700, size_pt), txt, box.size.x, size_pt)
		if lines.size() * size_pt * 1.35 <= box.size.y + 1.0 or size_pt <= 12.0:
			break
		size_pt -= 0.5
	var lh := size_pt * 1.35
	var y := box.position.y + (box.size.y - lines.size() * lh) * 0.5
	var font := _font("Nunito", 700, size_pt)
	for ln in lines:
		_text_left(font, ln, box.position.x, y, size_pt, TEXT, 1.35)
		y += lh


func _lines(font: Font, txt: String, width: float, size_pt: float) -> Array:
	var out: Array = []
	var line := ""
	for w in txt.split(" ", false):
		var test := w if line == "" else line + " " + w
		if line != "" and font.get_string_size(test, HORIZONTAL_ALIGNMENT_LEFT, -1, _fs(size_pt)).x > width * s:
			out.append(line)
			line = w
		else:
			line = test
	if line != "":
		out.append(line)
	return out


func _wrap_left(font: Font, txt: String, x: float, top: float, width: float, size_pt: float, lh: float, col: Color, max_lines: int) -> void:
	var lines := _lines(font, txt, width, size_pt)
	for i in mini(lines.size(), max_lines):
		_text_left(font, lines[i], x, top + i * size_pt * lh, size_pt, col, lh)


func _ellipsis(font: Font, txt: String, width: float) -> String:
	var fs := _fs(13)
	if font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x <= width * s:
		return txt
	var t := txt
	while t.length() > 1 and font.get_string_size(t + "…", HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > width * s:
		t = t.left(t.length() - 1)
	return t.strip_edges() + "…"


## Text, dessen Zeilenkasten (wie im Mockup, CSS „top“) bei top beginnt; gibt das rechte Ende zurück
func _text_left(font: Font, txt: String, x: float, top: float, size_pt: float, col: Color, lh := 0.0) -> float:
	var fs := _fs(size_pt)
	var asc := font.get_ascent(fs)
	var h := font.get_height(fs)
	var box := lh * size_pt * s if lh > 0.0 else h
	var base := _p(Vector2(x, top)).y + (box - h) * 0.5 + asc
	draw_string(font, Vector2(_p(Vector2(x, 0)).x, base), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
	return x + font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x / s


func _text_center(font: Font, txt: String, cx: float, top: float, size_pt: float, col: Color) -> void:
	var w := font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, _fs(size_pt)).x / s
	_text_left(font, txt, cx - w * 0.5, top, size_pt, col)


## Breite von Symbol + Leerraum + Wort (Mockup-Punkte)
func _symbol_label_width(label: String, font: Font, size_pt: float) -> float:
	return size_pt * 0.95 + size_pt * 0.3 + font.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, _fs(size_pt)).x / s


## Symbol und Wort, mittig um einen Punkt (senkrecht: Mitte der Schrift)
func _label_with_symbol(label: String, sym: String, center: Vector2, size_pt: float, spacing_em: float, col: Color, _left: bool) -> void:
	var font := _font("Nunito", 800, size_pt, spacing_em)
	var w := _symbol_label_width(label, font, size_pt)
	var x := center.x - w * 0.5
	_symbol(sym, Vector2(x + size_pt * 0.47, center.y), size_pt * 0.95, col)
	var fs := _fs(size_pt)
	_text_left(font, label, x + size_pt * 1.25, center.y - font.get_height(fs) / s * 0.5, size_pt, col)


## Symbole als Flächen: Blitz, Funkel-Stern, Stern, Krone, Schild
func _symbol(kind: String, c: Vector2, sz: float, col: Color) -> void:
	var pts: Array = []
	match kind:
		"bolt":
			pts = [[0.12, -0.5], [-0.3, 0.06], [-0.02, 0.06], [-0.12, 0.5], [0.3, -0.08], [0.02, -0.08]]
		"spark":
			for k in 8:
				var a := -PI * 0.5 + k * PI / 4.0
				var rr := 0.5 if k % 2 == 0 else 0.15
				pts.append([cos(a) * rr, sin(a) * rr])
		"star":
			for k in 10:
				var a := -PI * 0.5 + k * PI / 5.0
				var rr := 0.52 if k % 2 == 0 else 0.22
				pts.append([cos(a) * rr, sin(a) * rr + 0.04])
		"crown":
			pts = [[-0.46, 0.34], [-0.46, -0.28], [-0.22, 0.02], [0.0, -0.4], [0.22, 0.02], [0.46, -0.28], [0.46, 0.34]]
		"shield":
			pts = [[-0.4, -0.42], [0.4, -0.42], [0.4, 0.02], [0.0, 0.5], [-0.4, 0.02]]
	var poly := PackedVector2Array()
	for p in pts:
		poly.append(_p(c + Vector2(p[0], p[1]) * sz))
	draw_colored_polygon(poly, col)
	draw_polyline(poly + PackedVector2Array([poly[0]]), col, 0.6 * s, true)


func _arrow(at: Vector2, w: float, col: Color) -> void:
	draw_line(_p(at), _p(at + Vector2(w - 3.5, 0)), col, 1.6 * s, true)
	draw_colored_polygon(PackedVector2Array([_p(at + Vector2(w, 0)), _p(at + Vector2(w - 4.5, -3.2)), _p(at + Vector2(w - 4.5, 3.2))]), col)


func _round_points(r: Rect2, rad: float) -> PackedVector2Array:
	var pts := PackedVector2Array()
	rad = minf(rad, minf(r.size.x, r.size.y) * 0.5)
	var corners := [[r.end.x - rad, r.position.y + rad, -PI * 0.5], [r.end.x - rad, r.end.y - rad, 0.0],
		[r.position.x + rad, r.end.y - rad, PI * 0.5], [r.position.x + rad, r.position.y + rad, PI]]
	for cr in corners:
		for k in 7:
			var a: float = cr[2] + k * PI / 12.0
			pts.append(Vector2(cr[0], cr[1]) + Vector2(cos(a), sin(a)) * rad)
	return pts


func _rect_points(r: Rect2) -> PackedVector2Array:
	return PackedVector2Array([r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y)])


func _screen_pts(pts: PackedVector2Array) -> PackedVector2Array:
	var out := PackedVector2Array()
	for p in pts:
		out.append(_p(p))
	return out


## Abgerundete Fläche, mit Verlauf (Textur) oder einfarbig
func _fill_round(r: Rect2, rad: float, tex: Texture2D, col := Color.WHITE) -> void:
	var pts := _round_points(r, rad)
	if tex == null:
		draw_colored_polygon(_screen_pts(pts), col)
		draw_polyline(_screen_pts(pts + PackedVector2Array([pts[0]])), col, 0.8, true)
		return
	var uvs := PackedVector2Array()
	for p in pts:
		uvs.append((p - r.position) / r.size)
	draw_polygon(_screen_pts(pts), PackedColorArray([Color.WHITE]), uvs, tex)


func _round_border(r: Rect2, rad: float, w: float, col: Color) -> void:
	var pts := _round_points(r.grow(-w * 0.5), rad - w * 0.5)
	draw_polyline(_screen_pts(pts + PackedVector2Array([pts[0]])), col, w * s, true)


func _shadow(r: Rect2, rad: float, col: Color, blur: float, offset: Vector2) -> void:
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(col, 0.0)
	sb.draw_center = false
	sb.set_corner_radius_all(roundi(rad * s))
	sb.shadow_color = col
	sb.shadow_size = roundi(blur * s)
	sb.shadow_offset = offset * s
	sb.anti_aliasing = true
	draw_style_box(sb, _r(r))


func _vgrad(a: Color, b: Color) -> Texture2D:
	var g := Gradient.new()
	g.offsets = PackedFloat32Array([0.0, 1.0])
	g.colors = PackedColorArray([a, b])
	return _grad_tex(g, false)


func _rgrad(a: Color, b: Color) -> Texture2D:
	var g := Gradient.new()
	g.offsets = PackedFloat32Array([0.0, 0.7])
	g.colors = PackedColorArray([a, b])
	return _grad_tex(g, true)


func _grad_tex(g: Gradient, radial: bool) -> Texture2D:
	var key := "g:%s:%s" % [str(g.colors), radial]
	if not _tex.has(key):
		var t := GradientTexture2D.new()
		t.gradient = g
		t.width = 64
		t.height = 64
		if radial:
			t.fill = GradientTexture2D.FILL_RADIAL
			t.fill_from = Vector2(0.5, 0.5)
			t.fill_to = Vector2(1.0, 1.0)   # Radius bis zur Ecke wie CSS „circle“
		else:
			t.fill_from = Vector2(0.5, 0.0)
			t.fill_to = Vector2(0.5, 1.0)
		_tex[key] = t
	return _tex[key]


## Erstes Bild aus der Liste, das es gibt
static func _first(paths: Array) -> String:
	for p in paths:
		if str(p) != "" and ResourceLoader.exists(str(p)):
			return str(p)
	return ""


func _load(path: String) -> Texture2D:
	if path == "":
		return null
	if not _tex.has(path):
		_tex[path] = load(path) if ResourceLoader.exists(path) else null
	return _tex[path]


# --- Antippen ----------------------------------------------------------------------------------

func _gui_input(e: InputEvent) -> void:
	if not (e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT):
		return
	var p: Vector2 = (e.position - off) / s
	accept_event()
	if OK_RECT.grow(4).has_point(p) and _sel < cards.size():
		picked.emit(cards[_sel])
		return
	for i in cards.size():
		if slot_rect(i).grow(3).has_point(p):
			if i == _sel:
				picked.emit(cards[i])
			else:
				select(i)
			return
