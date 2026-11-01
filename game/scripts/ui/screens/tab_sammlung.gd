extends MockScreen
## Reiter „Helden“ (Mockup „Helden-Übersicht“, Artboard-seqx): oben die freigeschalteten Helden
## mit Stufe und Kartenfortschritt, darunter die noch gesperrten mit Freischalt-Bedingung und
## Knopf zum Freischalten mit Edelsteinen. Antippen eines Helden öffnet „Held aufleveln“.
##
## Hintergrund, Bänder, roter Punkt und Glanz kommen als Bilder aus dem Mockup (ui_mock/helden);
## die Karten zeichnet das Spiel selbst, weil Anzahl und Werte sich ändern. Alle Maße in
## Mockup-Punkten (390 × 844), gemessen im Mockup.

const NAV := {"Shop": "shop", "Helden": "sammlung", "Kampf": "kampf", "Upgrades": "upgrades", "Basis": "basis"}
const BANNER_Y := 14.0
const OPEN_COL := 87.0     # Kartenbreite freigeschaltet (4 Spalten)
const OPEN_H := 143.0
const LOCK_COL := 118.0    # Kartenbreite gesperrt (3 Spalten)
const LOCK_H := 195.0
const GAP := 6.0
const LEFT := 12.0
## Farbverlauf des Bilderrahmens je Held (oben, unten); aus dem Mockup, fehlende passend ergänzt
const FRAME := {
	"lynx": ["#7a4bff", "#3a1f9a"], "dusty": ["#ffd34d", "#e8960f"], "iska": ["#6fb4ff", "#3a64d8"],
	"margot": ["#ff9fc3", "#c2508f"], "brocken": ["#ff8a7a", "#c0303a"], "kalle": ["#8fe8ff", "#2a9ad8"],
	"fritzi": ["#ffb070", "#e0602a"], "volta": ["#6fe8d0", "#1f8f9a"],
}
const LOCK_FRAME := ["#4a63e6", "#23267a"]
const TITLE_SHADOW_OK := "rgb(29, 107, 42) 0px 2px 0px, rgba(255, 214, 90, 0.5) 0px 0px 10px"
const TITLE_SHADOW_LOCK := "rgb(122, 16, 32) 0px 2px 0px, rgba(255, 214, 90, 0.35) 0px 0px 8px"

var _open: Array[String] = []
var _locked: Array[String] = []
var _cards := {}           # Held -> Rect2 der Karte (Mockup-Punkte)
var _lock_y := 0.0         # Lage des zweiten Bands
var _back: Layer
var _figs: Control
var _front: Layer
var _views := {}           # Held -> HeroView3D
var _tex := {}
var _armed := ""           # Held, dessen Freischalten einmal angetippt wurde
var _armed_t := 0.0


func _init(m: MainMenu) -> void:
	super("helden", m)


func _ready() -> void:
	super()
	_back = Layer.new()
	_back.tab = self
	place_at(_back, Rect2(0, 0, W, H))
	_figs = Control.new()
	_figs.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_figs.resized.connect(_place_views)
	place_at(_figs, Rect2(0, 0, W, H))
	_front = Layer.new()
	_front.tab = self
	_front.front = true
	_front.mouse_filter = Control.MOUSE_FILTER_PASS
	place_at(_front, Rect2(0, 0, W, H))
	# Bilder vorab laden; frisch geladene Bilder sind im ersten Bild noch nicht bereit
	for id in ["banner", "banner_1", "dot", "shine"]:
		_live_tex(id)
	bind()
	await get_tree().process_frame
	_front.queue_redraw()


func _process(delta: float) -> void:
	super(delta)
	if _armed_t > 0.0:
		_armed_t -= delta
		if _armed_t <= 0.0:
			_armed = ""


## Freigeschaltete Helden nach Stufe (höchste zuerst), gesperrte nach Freischalt-Level
func _sort() -> void:
	_open.clear()
	_locked.clear()
	for id in GameData.HERO_IDS:
		if Save.hero_unlocked(id):
			_open.append(id)
		else:
			_locked.append(id)
	var order := GameData.HERO_IDS
	_open.sort_custom(func(a: String, b: String) -> bool:
		if Save.hero_level(a) != Save.hero_level(b):
			return Save.hero_level(a) > Save.hero_level(b)
		return order.find(a) < order.find(b))
	_locked.sort_custom(func(a: String, b: String) -> bool:
		return int(MetaData.HERO_UNLOCK[a]) < int(MetaData.HERO_UNLOCK[b]))


func bind() -> void:
	if _front == null:
		return
	_sort()
	# Die Kauf-Knöpfe des Mockups sitzen fest; die Karten zeichnen ihre Knöpfe selbst
	for b in buttons():
		b.visible = int(b.info["rect"][1]) > 700
	_cards.clear()
	var y := BANNER_Y + 48.0 + 8.0
	for k in _open.size():
		_cards[_open[k]] = Rect2(LEFT + (k % 4) * (OPEN_COL + GAP), y + floorf(k / 4.0) * (OPEN_H + GAP), OPEN_COL, OPEN_H)
	var rows := ceili(_open.size() / 4.0)
	y += rows * OPEN_H + maxi(0, rows - 1) * GAP
	_lock_y = y + 8.0 + 20.0
	y = _lock_y + 48.0 + 8.0
	for k in _locked.size():
		_cards[_locked[k]] = Rect2(LEFT + (k % 3) * (LOCK_COL + GAP), y + floorf(k / 3.0) * (LOCK_H + GAP), LOCK_COL, LOCK_H)
	# 3D-Figuren: nur neu bauen, wenn sich etwas geändert hat
	for id in _views.keys():
		var v: HeroView3D = _views[id]
		if not _cards.has(id) or v.grayscale != _locked.has(id):
			v.queue_free()
			_views.erase(id)
	for id in _cards.keys():
		if not _views.has(id):
			var v := HeroView3D.make(id, true, _locked.has(id))
			var inner := _portrait(id).grow(-2.0)
			v.aspect = inner.size.x / inner.size.y
			v.fig = 1.07
			v.feet = 1.12
			_figs.add_child(v)
			_views[id] = v
	_place_views()
	_back.queue_redraw()
	_front.queue_redraw()


func _place_views() -> void:
	for id in _views.keys():
		var v: HeroView3D = _views[id]
		var inner := _portrait(id).grow(-2.0)
		v.position = inner.position * s
		v.size = inner.size * s


## Bilderrahmen einer Karte (mit 2 Punkten Rand)
func _portrait(id: String) -> Rect2:
	var c: Rect2 = _cards[id]
	return Rect2(c.position + Vector2(4, 4), Vector2(c.size.x - 8.0, 88.0))


func _live_tex(id: String) -> Texture2D:
	if not _tex.has(id):
		var l: Dictionary = _live_info.get(id, {})
		_tex[id] = load("res://ui_mock/helden/" + str(l.get("img", ""))) if str(l.get("img", "")) != "" else null
	return _tex[id]


## Bild eines Live-Elements an eine andere Stelle zeichnen: Versatz des Elements um d
func _draw_live(ci: CanvasItem, id: String, d: Vector2, mod := Color.WHITE) -> void:
	var tex := _live_tex(id)
	var ir: Array = _live_info.get(id, {}).get("img_rect", [])
	if tex == null or ir.is_empty():
		return
	ci.draw_texture_rect(tex, _px(Rect2(ir[0] + d.x, ir[1] + d.y, ir[2], ir[3])), false, mod)


func _px(r: Rect2) -> Rect2:
	return Rect2(r.position * s, r.size * s)


func _short_name(id: String) -> String:
	var n := String(GameData.HEROES[id]["name"]).to_upper()
	if MockPaint.text_width(n, "Fredoka", 700, 13) > OPEN_COL - 8.0:
		n = n.get_slice(" ", n.get_slice_count(" ") - 1)
	return n


# --- Zeichnen ------------------------------------------------------------------------------

func _draw_back(ci: CanvasItem) -> void:
	for id in _cards.keys():
		var c: Rect2 = _cards[id]
		MockPaint.rrect(ci, _px(c), 10 * s, Color(30 / 255.0, 20 / 255.0, 80 / 255.0, 0.55))
		var cols: Array = LOCK_FRAME if _locked.has(id) else FRAME.get(id, LOCK_FRAME)
		MockPaint.rrect(ci, _px(_portrait(id)), 8 * s, Color(cols[0]), Color(cols[1]))


func _draw_front(ci: CanvasItem) -> void:
	_draw_banner(ci, "banner", BANNER_Y, "FREIGESCHALTET", 181.3, 10.0, "%d/%d" % [_open.size(), GameData.HERO_IDS.size()],
		Color(15 / 255.0, 61 / 255.0, 18 / 255.0, 0.6), 700, 20.0, 1.0, TITLE_SHADOW_OK)
	if not _locked.is_empty():
		_draw_banner(ci, "banner_1", _lock_y, "NOCH NICHT FREIGESCHALTET", 239.9, 8.0, str(_locked.size()),
			Color(90 / 255.0, 10 / 255.0, 40 / 255.0, 0.6), 600, 16.0, 0.32, TITLE_SHADOW_LOCK)
	for id in _open:
		_draw_open_card(ci, id)
	for id in _locked:
		_draw_locked_card(ci, id)


## Band mit Titel und Zähler-Pille (Titelbreite aus dem Mockup)
func _draw_banner(ci: CanvasItem, id: String, y: float, title: String, title_w: float, gap: float, count: String,
		pill: Color, weight: int, size: float, ls: float, shadow: String) -> void:
	var src := live_rect(id)
	_draw_live(ci, id, Vector2(0, y - src.position.y))
	var pw := MockPaint.text_width(count, "Nunito", 800, 11) + 16.0
	var x0 := W * 0.5 - (title_w + gap + pw) * 0.5
	MockPaint.text(self, ci, title, Rect2(x0, y + 9.0, title_w, 24), "Fredoka", weight, size, "rgb(255, 226, 122)", shadow, ls)
	var pr := Rect2(x0 + title_w + gap, y + 11.5, pw, 19)
	MockPaint.rrect(ci, _px(pr), 10 * s, pill)
	MockPaint.text(self, ci, count, pr, "Nunito", 800, 11, "rgb(255, 255, 255)")


func _bar(ci: CanvasItem, r: Rect2, ratio: float, a: Color, b: Color) -> void:
	MockPaint.rrect(ci, _px(r), 4 * s, Color(0, 0, 0, 0.45))
	var w := r.size.x * clampf(ratio, 0.0, 1.0)
	if w > 0.5:
		MockPaint.rrect_h(ci, _px(Rect2(r.position, Vector2(w, r.size.y))), 4 * s, a, b)


func _draw_open_card(ci: CanvasItem, id: String) -> void:
	var c: Rect2 = _cards[id]
	var p := c.position
	var lvl := Save.hero_level(id)
	# Stufen-Band unten im Bild (unten rund wie der Rahmen)
	var rib := Rect2(p + Vector2(6, 76), Vector2(c.size.x - 12.0, 14))
	var top := Color("#ffe27a")
	var bottom := Color("#ffb53d")
	MockPaint.rrect(ci, _px(rib), 6 * s, top, bottom)
	MockPaint.rrect(ci, _px(Rect2(rib.position, Vector2(rib.size.x, 8))), 0.0, top, top.lerp(bottom, 8.0 / 14.0))
	MockPaint.text(self, ci, "Stufe %d" % lvl, rib, "Nunito", 800, 10, "rgb(90, 36, 0)")
	MockPaint.border(ci, _px(_portrait(id)), 8 * s, Color("#ffd34d"), 2 * s)
	if Save.can_level_hero(id):
		_draw_live(ci, "dot", p + Vector2(60, 9) - live_rect("dot").position)
	MockPaint.text(self, ci, _short_name(id), Rect2(p + Vector2(4, 95), Vector2(c.size.x - 8, 16)), "Fredoka", 700, 13, "rgb(255, 247, 234)")
	var bar := Rect2(p + Vector2(4, 114), Vector2(c.size.x - 8, 8))
	var label_r := Rect2(p + Vector2(4, 125), Vector2(c.size.x - 8, 14))
	if lvl >= MetaData.HERO_MAX_LEVEL:
		_bar(ci, bar, 1.0, Color("#b6ff8a"), Color("#3fbf3a"))
		MockPaint.text(self, ci, "Höchste Stufe", label_r, "Nunito", 800, 10, "rgb(182, 255, 138)")
		return
	var have := Save.hero_cards(id)
	var need := MetaData.hero_cards_needed(lvl)
	var ratio := float(have) / float(need)
	if have >= need:
		_bar(ci, bar, 1.0, Color("#b6ff8a"), Color("#3fbf3a"))
		MockPaint.text(self, ci, "%d/%d · bereit" % [have, need], label_r, "Nunito", 800, 10, "rgb(182, 255, 138)")
	elif ratio >= 0.5:
		_bar(ci, bar, ratio, Color("#ffe27a"), Color("#ffb53d"))
		MockPaint.text(self, ci, "%d/%d Karten" % [have, need], label_r, "Nunito", 800, 10, "rgb(255, 226, 122)")
	else:
		_bar(ci, bar, ratio, Color("#6fd0ff"), Color("#3a7dff"))
		MockPaint.text(self, ci, "%d/%d Karten" % [have, need], label_r, "Nunito", 800, 10, "rgb(207, 227, 255)")


func _draw_locked_card(ci: CanvasItem, id: String) -> void:
	var c: Rect2 = _cards[id]
	var p := c.position
	var w := c.size.x - 8.0
	_draw_live(ci, "shine", p + Vector2(6, 6) - live_rect("shine").position)
	MockPaint.border(ci, _px(_portrait(id)), 8 * s, Color(160 / 255.0, 190 / 255.0, 1.0, 0.5), 2 * s)
	MockPaint.text(self, ci, _short_name(id), Rect2(p + Vector2(4, 95), Vector2(w, 16)), "Fredoka", 700, 13, "rgb(255, 247, 234)")
	MockPaint.text(self, ci, "Level %d gewinnen" % int(MetaData.HERO_UNLOCK[id]), Rect2(p + Vector2(4, 114), Vector2(w, 14)),
		"Nunito", 800, 10, "rgb(255, 226, 122)")
	var have := Save.hero_cards(id)
	var need := MetaData.hero_cards_needed(1)
	_bar(ci, Rect2(p + Vector2(4, 131), Vector2(w, 8)), float(have) / float(need), Color("#6fd0ff"), Color("#3a7dff"))
	MockPaint.text(self, ci, "%d/%d Karten" % [have, need], Rect2(p + Vector2(4, 142), Vector2(w, 14)), "Nunito", 800, 10, "rgb(207, 227, 255)")
	# Freischalten mit Edelsteinen: grüner Knopf wie „Kaufen“ im Mockup, sonst dunkel wie „Gesperrt“
	var br := _buy_rect(id)
	var afford := Save.gems() >= MetaData.HERO_UNLOCK_GEMS
	var col := "rgb(15, 61, 18)"
	if afford:
		var btn := button("Angebot-Volta.dc.html")
		if btn and btn.texture:
			var hit: Array = btn.info["rect"]
			var ir: Array = btn.info["img_rect"]
			var d := br.position - Vector2(hit[0], hit[1])
			ci.draw_texture_rect(btn.texture, _px(Rect2(ir[0] + d.x, ir[1] + d.y, ir[2], ir[3])), false)
		else:
			MockPaint.rrect(ci, _px(br), 10 * s, Color("#b6ff8a"), Color("#3fbf3a"))
	else:
		MockPaint.rrect(ci, _px(br), 10 * s, Color(20 / 255.0, 12 / 255.0, 48 / 255.0, 0.7))
		MockPaint.border(ci, _px(br), 10 * s, Color(1, 1, 1, 0.25), 2 * s)
		col = "rgb(217, 208, 255)"
	var label := "SICHER?" if _armed == id else str(MetaData.HERO_UNLOCK_GEMS)
	var tw := MockPaint.text_width(label, "Fredoka", 700, 13)
	var gem := 13.0 if _armed != id else 0.0
	var x0 := br.get_center().x - (tw + gem + (4.0 if gem > 0.0 else 0.0)) * 0.5
	if gem > 0.0:
		_gem(ci, Rect2(x0, br.get_center().y - 6.5, 13, 13))
		x0 += gem + 4.0
	MockPaint.text(self, ci, label, Rect2(x0, br.position.y, tw, br.size.y), "Fredoka", 700, 13, col)


## Edelstein wie in der Kopfleiste der Mockups
func _gem(ci: CanvasItem, r: Rect2) -> void:
	var raw := [Vector2(6, 4), Vector2(18, 4), Vector2(22, 10), Vector2(12, 21), Vector2(2, 10)]
	var pts := PackedVector2Array()
	for q in raw:
		pts.append((r.position + q / 24.0 * r.size) * s)
	ci.draw_colored_polygon(pts, Color("#ff6fd2"))
	pts.append(pts[0])
	ci.draw_polyline(pts, Color("#8a1f6e"), 1.3 * r.size.x / 24.0 * s, true)
	ci.draw_line((r.position + Vector2(2, 10) / 24.0 * r.size) * s, (r.position + Vector2(22, 10) / 24.0 * r.size) * s, Color("#ffd0f2"), maxf(1.0, s * 0.6))


func _buy_rect(id: String) -> Rect2:
	var c: Rect2 = _cards[id]
	return Rect2(c.position + Vector2(4, 159), Vector2(c.size.x - 8.0, 32))


# --- Antippen ------------------------------------------------------------------------------

func _tap(p: Vector2) -> bool:
	for id in _cards.keys():
		var c: Rect2 = _cards[id]
		if not c.has_point(p):
			continue
		Sfx.play("click")
		if _open.has(id):
			HeroBoard.start_hero = id
			HeroBoard.hero_order = _open.duplicate()
			menu.open_board("Artboard-seqx-c6i2.dc.html")
		elif _buy_rect(id).grow(4.0).has_point(p):
			_buy(id)
		else:
			var d: Dictionary = GameData.HEROES[id]
			menu.info(String(d["name"]), "%s · %s\n\n%s\n\nGewinne Level %d, dann ist %s dabei – oder schalte %s sofort für %d Edelsteine frei." % [
				d["role"], d["weapon"], d["blurb"], int(MetaData.HERO_UNLOCK[id]), d["name"], d["name"], MetaData.HERO_UNLOCK_GEMS])
		return true
	return false


## Freischalten mit Edelsteinen: erst nachfragen (zweimal tippen), dann kaufen
func _buy(id: String) -> void:
	var name := String(GameData.HEROES[id]["name"])
	if Save.gems() < MetaData.HERO_UNLOCK_GEMS:
		menu.toast("Dafür fehlen noch %d Edelsteine" % (MetaData.HERO_UNLOCK_GEMS - Save.gems()))
		return
	if _armed != id:
		_armed = id
		_armed_t = 3.0
		menu.toast("Nochmal tippen: %s für %d Edelsteine freischalten" % [name, MetaData.HERO_UNLOCK_GEMS])
		_front.queue_redraw()
		return
	_armed = ""
	if Save.unlock_with_gems(id):
		menu.celebrate("up", "%s ist jetzt dabei!" % name, GameData.HEROES[id]["color"])
	refresh()


func handle(b: Dictionary) -> bool:
	for t in texts_of_button(int(b["i"])):
		if NAV.has(str(t["text"])):
			menu.show_tab(NAV[str(t["text"])])
			return true
	return false


## Zeichenfläche: hinten (Kartenflächen, Bildrahmen) oder vorn (alles über den Figuren)
class Layer:
	extends Control
	var tab: Node
	var front := false

	func _ready() -> void:
		if not front:
			mouse_filter = Control.MOUSE_FILTER_IGNORE

	func _draw() -> void:
		if front:
			tab._draw_front(self)
		else:
			tab._draw_back(self)

	func _gui_input(e: InputEvent) -> void:
		if front and e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT:
			if tab._tap((e as InputEventMouseButton).position / tab.s):
				accept_event()
