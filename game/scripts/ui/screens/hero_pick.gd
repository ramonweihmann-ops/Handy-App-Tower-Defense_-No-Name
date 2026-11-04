class_name HeroPickBoard
extends MockView
## Heldenauswahl beim Kampfstart nach dem freigegebenen Mockup „Kampf · Heldenauswahl beim Start“
## (Entwurf Vorlage_Raw/Heldenauswahl_Start_v1). Die Box mit Überschrift, Untertitel und Hinweis kommt aus
## dem Export ui_mock/heldenwahl; die Karten zeichnet das Spiel selbst, weil die angebotenen Helden wechseln:
## Rahmen und Kopf in der Waffenfarbe, Waffensymbol, Figur (ui/heroes2d) auf dem Podest, Name, Beruf,
## Beschreibung, grüner Knopf „Auswählen“. Die ganze Karte ist antippbar. Dahinter bleibt der Kampf sichtbar.

signal picked(id: String)

## Karten im Mockup (Punkte): Box links 12, oben 222; Karten 112 × 274, 5 Abstand, oben 325
const CARD_W := 112.0
const CARD_H := 274.0
const CARD_GAP := 5.0
const CARD_TOP := 325.0
## Waffenfarben wie im Mockup; Helden ohne Eintrag nehmen ihre Heldenfarbe
const WEAPON_COL := {"brocken": "#e8642c", "kalle": "#4fd2f2", "iska": "#3f7df0"}
## Lange Waffennamen zweizeilig wie „Maschinen-/gewehr“ im Mockup
const WRAP := {"Maschinengewehr": "Maschinen-\ngewehr", "Präzisionsgewehr": "Präzisions-\ngewehr",
	"Schraubenwerfer": "Schrauben-\nwerfer", "Raketenfäuste": "Raketen-\nfäuste", "Funkenpistole": "Funken-\npistole"}

var options: Array = []
var _hint_text := ""


func _init(ids: Array) -> void:
	super("heldenwahl")
	options = ids


func _ready() -> void:
	super()
	_fill.visible = false
	# Hinweis unter den Karten: passt sich an Anzahl und Art der angebotenen Helden an
	var starts := options.filter(func(id: String) -> bool: return GameData.HERO_TYPE.get(id, "start") == "start").size()
	if starts == options.size():
		_hint_text = ["Ein starker Start-Held", "Beide sind starke Start-Helden", "Alle drei sind starke Start-Helden"][clampi(options.size(), 1, 3) - 1]
	else:
		_hint_text = "Verstärkungen im Kampf dazurufen"
	set_text("Alle drei sind starke Start-Helden", _hint_text)
	var n := options.size()
	var total := n * CARD_W + (n - 1) * CARD_GAP
	for i in n:
		var card := Card.new()
		card.board = self
		card.hero_id = str(options[i])
		place_at(card, Rect2(195.0 - total * 0.5 + i * (CARD_W + CARD_GAP), CARD_TOP, CARD_W, CARD_H), true)


## Eine Heldenkarte; zeichnet sich in Mockup-Punkten (k = Bildschirmpunkte je Mockup-Punkt)
class Card:
	extends Control
	var board: HeroPickBoard
	var hero_id := ""
	var _tex: Texture2D
	var _icon: Texture2D
	var _pressed := false

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_STOP
		mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
		var path := "res://ui/heroes2d/%s.png" % hero_id
		_tex = load(path) if ResourceLoader.exists(path) else null
		_icon = WeaponIcons.texture(str(GameData.HEROES[hero_id].get("family", "")), 64)

	func _gui_input(e: InputEvent) -> void:
		var down := (e is InputEventMouseButton and (e as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT) or e is InputEventScreenTouch
		if not down:
			return
		if e.is_pressed():
			_pressed = true
			scale = Vector2.ONE * 0.97
			pivot_offset = size * 0.5
		elif _pressed:
			_pressed = false
			scale = Vector2.ONE
			if Rect2(Vector2.ZERO, size).has_point(e.position):
				Sfx.play("click")
				board.picked.emit(hero_id)
		accept_event()

	func _col() -> Color:
		var d: Dictionary = GameData.HEROES[hero_id]
		return Color(WEAPON_COL[hero_id]) if WEAPON_COL.has(hero_id) else (d["color"] as Color).lightened(0.12)

	func _box(r: Rect2, fill: Color, radius: float, border := Color(0, 0, 0, 0), bw := 0.0, shadow := Color(0, 0, 0, 0), sh_off := Vector2.ZERO, sh_size := 0.0) -> void:
		var k := size.x / CARD_W
		var sb := StyleBoxFlat.new()
		sb.bg_color = fill
		sb.set_corner_radius_all(roundi(radius * k))
		if bw > 0.0:
			sb.border_color = border
			sb.set_border_width_all(maxi(1, roundi(bw * k)))
		if shadow.a > 0.0:
			sb.shadow_color = shadow
			sb.shadow_offset = sh_off * k
			sb.shadow_size = roundi(sh_size * k)
		sb.anti_aliasing = true
		draw_style_box(sb, Rect2(r.position * k, r.size * k))

	func _text(t: String, cx: float, top: float, fam: String, weight: int, px: float, col: Color, shadow := Color(0, 0, 0, 0), sh_y := 0.0) -> void:
		var k := size.x / CARD_W
		var f := MockFonts.font(fam, weight)
		var fs := maxi(1, roundi(px * k))
		var w := f.get_string_size(t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var base := top * k + f.get_ascent(fs)
		if shadow.a > 0.0:
			draw_string(f, Vector2(cx * k - w * 0.5, base + sh_y * k), t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, shadow)
		draw_string(f, Vector2(cx * k - w * 0.5, base), t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)

	func _tw(t: String, fam: String, weight: int, px: float) -> float:
		var k := size.x / CARD_W
		return MockFonts.font(fam, weight).get_string_size(t, HORIZONTAL_ALIGNMENT_LEFT, -1, maxi(1, roundi(px * k))).x / k

	func _draw() -> void:
		var k := size.x / CARD_W
		var d: Dictionary = GameData.HEROES[hero_id]
		var col := _col()
		# Karte: dunkler Grund, Rahmen in der Waffenfarbe, leichter farbiger Schein innen
		_box(Rect2(0, 0, CARD_W, CARD_H), Color("#1d1748"), 14, col, 2.0, Color(0, 0, 0, 0.35), Vector2(0, 4), 6)
		_box(Rect2(2, 2, CARD_W - 4, CARD_H - 4), Color(col.r, col.g, col.b, 0.07), 12)
		# Kopf: Waffenname in der Waffenfarbe, oben etwas heller
		var head := Rect2(4, 4, CARD_W - 8, 34)
		_box(head, col.darkened(0.18), 10)
		_box(Rect2(head.position, Vector2(head.size.x, head.size.y * 0.62)), col, 10)
		draw_line(Vector2(14, 5.2) * k, Vector2(CARD_W - 14, 5.2) * k, Color(1, 1, 1, 0.35), maxf(1.0, k))
		var dark := col.get_luminance() > 0.62
		var tcol := Color("#0b2f4a") if dark else Color.WHITE
		var tsh := Color(1, 1, 1, 0.45) if dark else col.darkened(0.55)
		var weapon := str(d["weapon"])
		var lines: PackedStringArray = [weapon]
		var px := 11.5
		var icon_w := 22.0 if _icon else 0.0
		if _tw(weapon, "Fredoka", 700, px) + icon_w > head.size.x - 4:
			if WRAP.has(weapon):
				lines = WRAP[weapon].split("\n")
			while px > 9.0 and _tw(lines[0], "Fredoka", 700, px) + icon_w > head.size.x - 4:
				px -= 0.5
		var tw := 0.0
		for l in lines:
			tw = maxf(tw, _tw(l, "Fredoka", 700, px))
		var x0 := head.get_center().x - (tw + icon_w) * 0.5
		if _icon:
			draw_texture_rect(_icon, Rect2(Vector2(x0, head.get_center().y - 8) * k, Vector2(19, 16) * k), false)
		var lh := px * 1.05
		var ty := head.get_center().y - lh * lines.size() * 0.5 - px * 0.08
		for i in lines.size():
			_text(lines[i], x0 + icon_w + tw * 0.5, ty + i * lh, "Fredoka", 700, px, tcol, tsh, 1.0)
		# Podest: leuchtende Ellipse unter der Figur
		draw_set_transform(Vector2(56, 145) * k, 0.0, Vector2(1.0, 18.0 / 86.0))
		draw_circle(Vector2.ZERO, 43 * k, Color(0.24, 0.47, 0.86, 0.32))
		draw_circle(Vector2.ZERO, 30 * k, Color(0.44, 0.88, 1.0, 0.28))
		draw_arc(Vector2.ZERO, 43 * k, 0, TAU, 48, Color(0.44, 0.88, 1.0, 0.6), 1.5 * k, true)
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
		# Figur: 112 hoch, Füße auf dem Podest
		if _tex:
			var th := 112.0
			var tw2 := th * _tex.get_width() / float(_tex.get_height())
			if tw2 > CARD_W - 6:
				tw2 = CARD_W - 6
				th = tw2 * _tex.get_height() / float(_tex.get_width())
			draw_texture_rect(_tex, Rect2(Vector2(56 - tw2 * 0.5, 152 - th) * k, Vector2(tw2, th) * k), false)
		# Name, Beruf, Beschreibung
		_text(str(d["name"]), 56, 158.5, "Fredoka", 700, 21, Color("#ffd34d"), Color("#7a4a00"), 2.0)
		var role := str(d["role"])
		var rpx := 11.0
		while rpx > 9.0 and _tw(role, "Nunito", 700, rpx) > CARD_W - 6:
			rpx -= 0.5
		_text(role, 56, 185.5, "Nunito", 700, rpx, Color("#cfc8f0"))
		_desc(str(d["blurb"]))
		# Knopf „Auswählen“
		var btn := Rect2(7, CARD_H - 8 - 30, CARD_W - 14, 30)
		_box(btn, Color("#3fbf3a"), 10, Color(0, 0, 0, 0), 0, Color("#23802a"), Vector2(0, 3), 0.1)
		_box(Rect2(btn.position, Vector2(btn.size.x, btn.size.y * 0.6)), Color("#7ce85a"), 10)
		draw_line((btn.position + Vector2(10, 1.6)) * k, (btn.position + Vector2(btn.size.x - 10, 1.6)) * k, Color(1, 1, 1, 0.55), maxf(1.0, 1.6 * k))
		_text("Auswählen", 56, btn.position.y + 5, "Fredoka", 700, 15, Color("#0f3d12"))

	## Beschreibung in höchstens zwei Zeilen (10 px wie im freigegebenen Mockup, sonst etwas kleiner)
	func _desc(t: String) -> void:
		var avail := CARD_W - 4
		var px := 10.0
		var lines := _wrap(t, px, avail)
		while lines.size() > 2 and px > 8.5:
			px -= 0.5
			lines = _wrap(t, px, avail)
		var lh := px * 1.38
		for i in mini(lines.size(), 2):
			_text(lines[i], 56, 205 + i * lh, "Nunito", 800, px, Color.WHITE)

	func _wrap(t: String, px: float, avail: float) -> PackedStringArray:
		var words := t.split(" ")
		if _tw(t, "Nunito", 800, px) > avail:
			# zwei Zeilen, so gleich lang wie möglich
			var best: PackedStringArray = []
			var best_w := INF
			for i in range(1, words.size()):
				var a := " ".join(words.slice(0, i))
				var b := " ".join(words.slice(i))
				var w := maxf(_tw(a, "Nunito", 800, px), _tw(b, "Nunito", 800, px))
				if w <= avail and w < best_w:
					best_w = w
					best = [a, b]
			if not best.is_empty():
				return best
		var out: PackedStringArray = []
		var cur := ""
		for w in t.split(" "):
			var test := w if cur == "" else cur + " " + w
			if cur != "" and _tw(test, "Nunito", 800, px) > avail:
				out.append(cur)
				cur = w
			else:
				cur = test
		if cur != "":
			out.append(cur)
		return out
