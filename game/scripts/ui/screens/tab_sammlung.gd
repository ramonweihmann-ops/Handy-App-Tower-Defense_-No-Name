extends MockScreen
## Reiter „Helden“ nach dem freigegebenen Helden-Baukasten (Mockup „Helden (neu, freigegeben)“,
## Vorlage_Raw/Helden_Baukasten_v1): oben die freigeschalteten Helden mit Stufe und Kartenfortschritt,
## darunter die noch gesperrten mit Freischalt-Bedingung und Knopf zum Freischalten mit Edelsteinen.
## Antippen eines Helden öffnet „Held aufleveln“.
##
## Hintergrund und Reiterleiste kommen aus dem Mockup (ui_mock/helden_neu); Bänder, Karten, Bildrahmen,
## Plaketten, Balken und Knöpfe sind die Bauteile aus dem Baukasten (ui/helden_v2). Die Karten zeichnet
## das Spiel selbst, weil Anzahl und Werte sich ändern. Alle Maße in Mockup-Punkten (390 × 844).

const NAV := {"Shop": "shop", "Helden": "sammlung", "Kampf": "kampf", "Upgrades": "upgrades", "Basis": "basis"}
const PART := "res://ui/helden_v2/%s.webp"
## Bänder (Breite, Höhe) und Lage des ersten Bands
const BANNER_TOP := 32.0
const BANNER_OK := Vector2(316.5, 50.1)
const BANNER_LOCK := Vector2(355.0, 43.4)
## Freigeschaltet: 4 Spalten, Bildfeld 87,7 × 96, darunter Name, Balken, Kartenstand
const OPEN_X := 10.9
const OPEN_COL := 93.5
const PORTRAIT := Vector2(87.7, 96.0)
const OPEN_H := 156.0
const OPEN_GAP := 12.0
## Gesperrt: 3 Spalten, Karte 119,4 × 221
const LOCK_X := 7.9
const LOCK_COL := 127.4
const LOCK_CARD := Vector2(119.4, 221.0)
const LOCK_GAP := 12.0
const LEFT := 10.9
## Sichtbarer Bereich über der Reiterleiste; darin scrollt die Liste
const VIEW_H := 772.0
const BOTTOM_PAD := 24.0
## Farbe des Bildfelds je Held (Baukasten: violett, gold, cyan, rosa)
const BG := {
	"lynx": "violett", "dusty": "gold", "iska": "cyan", "margot": "rosa", "brocken": "cyan", "kalle": "cyan",
	"fritzi": "gold", "volta": "cyan", "nova": "violett", "pip": "cyan", "rollo": "gold", "fuenkchen": "rosa",
}

var _open: Array[String] = []
var _locked: Array[String] = []
var _cards := {}           # Held -> Rect2 der Karte (Mockup-Punkte)
var _lock_y := 0.0         # Lage des zweiten Bands
var _parts := {}
var _back: Layer
var _figs: Control
var _front: Layer
var _views := {}           # Held -> HeroView3D
var _tex := {}
var _armed := ""           # Held, dessen Freischalten einmal angetippt wurde
var _armed_t := 0.0
var _scroller: Control     # schneidet die Liste über der Reiterleiste ab
var _scroll := 0.0         # Mockup-Punkte
var _content_h := 0.0
var _press := Vector2.ZERO
var _dragged := 0.0
var _pressed := false


func _init(m: MainMenu) -> void:
	super("helden_neu", m)


func _ready() -> void:
	super()
	# Liste unter der Reiterleiste: Kopf, Karten und Figuren liegen in einem abgeschnittenen Bereich,
	# die Reiterleiste (Hintergrundbild und Knöpfe) bleibt immer davor sichtbar
	_scroller = Control.new()
	_scroller.clip_contents = true
	_scroller.mouse_filter = Control.MOUSE_FILTER_PASS
	place_at(_scroller, Rect2(0, 0, W, VIEW_H))
	_scroller.resized.connect(_fit_scroll)
	_back = Layer.new()
	_back.tab = self
	_scroller.add_child(_back)
	_figs = Control.new()
	_figs.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_figs.resized.connect(_place_views)
	_scroller.add_child(_figs)
	_front = Layer.new()
	_front.tab = self
	_front.front = true
	_front.mouse_filter = Control.MOUSE_FILTER_PASS
	_scroller.add_child(_front)
	# Bilder vorab laden; frisch geladene Bilder sind im ersten Bild noch nicht bereit
	for id in ["banner_gruen", "banner_rot", "zaehler_dunkel", "portrait_rahmen_gold", "stufe_plakette", "hinweispunkt",
			"fortschritt_schiene", "fortschritt_gruen", "fortschritt_gold", "fortschritt_cyan", "kartenkoerper",
			"knopf_gruen_normal", "knopf_gesperrt", "plus", "portrait_hintergrund_cyan", "portrait_hintergrund_gold",
			"portrait_hintergrund_rosa", "portrait_hintergrund_violett"]:
		part(id)
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
	var y := BANNER_TOP + BANNER_OK.y + 24.0
	for k in _open.size():
		_cards[_open[k]] = Rect2(OPEN_X + (k % 4) * OPEN_COL, y + floorf(k / 4.0) * (OPEN_H + OPEN_GAP), PORTRAIT.x, OPEN_H)
	var rows := ceili(_open.size() / 4.0)
	y += rows * OPEN_H + maxi(0, rows - 1) * OPEN_GAP
	_lock_y = y + 20.0
	y = _lock_y + BANNER_LOCK.y + 24.0
	for k in _locked.size():
		_cards[_locked[k]] = Rect2(LOCK_X + (k % 3) * LOCK_COL, y + floorf(k / 3.0) * (LOCK_CARD.y + LOCK_GAP), LOCK_CARD.x, LOCK_CARD.y)
	# 3D-Figuren: nur neu bauen, wenn sich etwas geändert hat
	for id in _views.keys():
		var v: HeroView3D = _views[id]
		if not _cards.has(id) or v.grayscale != _locked.has(id):
			v.queue_free()
			_views.erase(id)
	for id in _cards.keys():
		if not _views.has(id):
			var v := HeroView3D.make(id, true, _locked.has(id))
			v.head_crop = true
			v.crop_face = 0.34      # Brustbild wie im Baukasten: Kopf und Oberkörper
			v.crop_eye = 0.30
			_figs.add_child(v)
			_views[id] = v
	_content_h = (y + ceili(_locked.size() / 3.0) * (LOCK_CARD.y + LOCK_GAP) if not _locked.is_empty() else _lock_y - 20.0) + BOTTOM_PAD
	_fit_scroll()
	_place_views()
	_back.queue_redraw()
	_front.queue_redraw()


## Liste verschieben (Mockup-Punkte), begrenzt auf den Inhalt
func scroll_to(v: float) -> void:
	_scroll = clampf(v, 0.0, maxf(0.0, _content_h - VIEW_H))
	_fit_scroll()


func _fit_scroll() -> void:
	if _scroller == null:
		return
	_scroll = clampf(_scroll, 0.0, maxf(0.0, _content_h - VIEW_H))
	for c in [_back, _figs, _front]:
		c.position = Vector2(0, -_scroll * s)
		c.size = Vector2(W, maxf(VIEW_H, _content_h)) * s


func _place_views() -> void:
	for id in _views.keys():
		var v: HeroView3D = _views[id]
		var inner := _portrait(id).grow(-1.5)
		v.position = inner.position * s
		v.size = inner.size * s


## Bildfeld einer Karte
func _portrait(id: String) -> Rect2:
	var c: Rect2 = _cards[id]
	if _locked.has(id):
		return Rect2(c.position + Vector2(6, 6), Vector2(c.size.x - 12.0, 100.0))
	return Rect2(c.position, PORTRAIT)


## Bauteil aus dem Helden-Baukasten
func part(id: String) -> Texture2D:
	if not _parts.has(id):
		_parts[id] = load(PART % id)
	return _parts[id]


func _part(ci: CanvasItem, id: String, r: Rect2, mod := Color.WHITE) -> void:
	var t := part(id)
	if t:
		ci.draw_texture_rect(t, _px(r), false, mod)


func _text(ci: CanvasItem, txt: String, r: Rect2, family: String, weight: int, size: float, col: String, shadow := "") -> void:
	MockPaint.text(self, ci, txt, r, family, weight, size, col, shadow)


func _px(r: Rect2) -> Rect2:
	return Rect2(r.position * s, r.size * s)


func _short_name(id: String) -> String:
	var n := String(GameData.HEROES[id]["name"]).to_upper()
	if MockPaint.text_width(n, "Fredoka", 700, 14) > OPEN_COL - 4.0:
		n = n.get_slice(" ", n.get_slice_count(" ") - 1)
	return n


# --- Zeichnen ------------------------------------------------------------------------------

func _draw_back(ci: CanvasItem) -> void:
	for id in _cards.keys():
		if _locked.has(id):
			_part(ci, "kartenkoerper", _cards[id])
		_part(ci, "portrait_hintergrund_" + str(BG.get(id, "violett")), _portrait(id))


func _draw_front(ci: CanvasItem) -> void:
	_draw_banner(ci, "banner_gruen", Rect2(W * 0.5 - BANNER_OK.x * 0.5, BANNER_TOP, BANNER_OK.x, BANNER_OK.y), "FREIGESCHALTET", 21.0,
		"%d/%d" % [_open.size(), GameData.HERO_IDS.size()], "rgb(29, 107, 42) 0px 2px 0px")
	if not _locked.is_empty():
		_draw_banner(ci, "banner_rot", Rect2(W * 0.5 - BANNER_LOCK.x * 0.5, _lock_y, BANNER_LOCK.x, BANNER_LOCK.y), "NOCH NICHT FREIGESCHALTET", 17.0,
			str(_locked.size()), "rgb(122, 16, 32) 0px 2px 0px")
	for id in _open:
		_draw_open_card(ci, id)
	for id in _locked:
		_draw_locked_card(ci, id)


## Band aus dem Baukasten mit Titel und Zähler rechts
func _draw_banner(ci: CanvasItem, id: String, r: Rect2, title: String, size: float, count: String, shadow: String) -> void:
	_part(ci, id, r)
	var cw := 48.0 if count.length() > 1 else 40.0
	_text(ci, title, Rect2(r.position.x, r.position.y, r.size.x - cw - 8.0, r.size.y), "Fredoka", 700, size, "rgb(255, 255, 255)", shadow)
	var cr := Rect2(r.end.x - cw - 30.0, r.get_center().y - 12.0, cw, 24.0)
	_part(ci, "zaehler_dunkel", cr)
	_text(ci, count, cr, "Fredoka", 700, 15, "rgb(255, 255, 255)")


## Fortschritt: Schiene, darüber die Füllung (abgeschnitten auf den Anteil)
func _bar(ci: CanvasItem, r: Rect2, ratio: float, fill: String) -> void:
	_part(ci, "fortschritt_schiene", r)
	var f := clampf(ratio, 0.0, 1.0)
	var t := part(fill)
	if f > 0.01 and t:
		var src := Rect2(Vector2.ZERO, Vector2(t.get_width() * f, t.get_height()))
		ci.draw_texture_rect_region(t, _px(Rect2(r.position, Vector2(r.size.x * f, r.size.y))), src)


func _draw_open_card(ci: CanvasItem, id: String) -> void:
	var c: Rect2 = _cards[id]
	var p := c.position
	var pr := _portrait(id)
	_part(ci, "portrait_rahmen_gold", pr.grow(1.0))
	var lvl := Save.hero_level(id)
	var pl := Rect2(pr.get_center().x - 31.0, pr.end.y - 14.0, 62.0, 23.0)
	_part(ci, "stufe_plakette", pl)
	_text(ci, "Stufe %d" % lvl, pl, "Fredoka", 700, 11.5, "rgb(74, 32, 0)")
	if Save.can_level_hero(id):
		_part(ci, "hinweispunkt", Rect2(pr.end.x - 13.0, pr.position.y - 5.0, 18, 18))
	_text(ci, _short_name(id), Rect2(p.x - 6.0, pr.end.y + 12.0, c.size.x + 12.0, 18), "Fredoka", 700, 14, "rgb(255, 255, 255)", "rgb(26, 15, 58) 0px 2px 0px")
	var bar := Rect2(p.x + 2.0, pr.end.y + 33.0, c.size.x - 4.0, 11.0)
	var label_r := Rect2(p.x - 6.0, pr.end.y + 46.0, c.size.x + 12.0, 14)
	if lvl >= MetaData.HERO_MAX_LEVEL:
		_bar(ci, bar, 1.0, "fortschritt_gruen")
		_text(ci, "Höchste Stufe", label_r, "Nunito", 800, 10.5, "rgb(125, 255, 138)")
		return
	var have := Save.hero_cards(id)
	var need := MetaData.hero_cards_needed(lvl)
	var ratio := float(have) / float(need)
	if have >= need:
		_bar(ci, bar, 1.0, "fortschritt_gruen")
		_text(ci, "%d/%d · bereit" % [have, need], label_r, "Nunito", 800, 10.5, "rgb(125, 255, 138)")
	else:
		_bar(ci, bar, ratio, "fortschritt_gold" if ratio >= 0.5 else "fortschritt_cyan")
		_text(ci, "%d/%d Karten" % [have, need], label_r, "Nunito", 800, 10.5, "rgb(232, 226, 255)")


func _draw_locked_card(ci: CanvasItem, id: String) -> void:
	var c: Rect2 = _cards[id]
	var p := c.position
	var pr := _portrait(id)
	_part(ci, "portrait_rahmen_gold", pr.grow(1.0))
	_part(ci, "plus", Rect2(pr.end.x - 19.0, pr.position.y + 3.0, 16, 16))
	var name := _short_name(id)
	_text(ci, name, Rect2(p.x, p.y + 110.0, c.size.x, 20), "Fredoka", 700, 12.0 if name.length() > 10 else 15.0, "rgb(255, 226, 122)", "rgb(58, 26, 128) 0px 2px 0px")
	_text(ci, "Level %d gewinnen" % int(MetaData.HERO_UNLOCK[id]), Rect2(p.x + 6.0, p.y + 132.0, c.size.x - 12.0, 14), "Nunito", 800, 10.5, "rgb(255, 211, 77)")
	var have := Save.hero_cards(id)
	var need := MetaData.hero_cards_needed(1)
	var br := Rect2(p.x + 10.0, p.y + 156.0, c.size.x - 20.0, 15.0)
	if have > 0:
		_bar(ci, br, float(have) / float(need), "fortschritt_cyan")
	else:
		_part(ci, "zaehler_dunkel", br)
	_text(ci, "%d/%d Karten" % [have, need], br, "Nunito", 800, 10, "rgb(255, 255, 255)")
	# Freischalten mit Edelsteinen: grüner Knopf (genug Edelsteine) oder gesperrter Knopf
	var kr := _buy_rect(id)
	var afford := Save.gems() >= MetaData.HERO_UNLOCK_GEMS
	_part(ci, "knopf_gruen_normal" if afford else "knopf_gesperrt", kr)
	var col := "rgb(15, 61, 18)" if afford else "rgb(216, 212, 240)"
	var label := "SICHER?" if _armed == id else str(MetaData.HERO_UNLOCK_GEMS)
	var tw := MockPaint.text_width(label, "Fredoka", 700, 15)
	var gem := 14.0 if _armed != id else 0.0
	var x0 := kr.get_center().x - (tw + gem + (4.0 if gem > 0.0 else 0.0)) * 0.5
	if gem > 0.0:
		_gem(ci, Rect2(x0, kr.get_center().y - 7.0, 14, 14))
		x0 += gem + 4.0
	_text(ci, label, Rect2(x0, kr.position.y, tw, kr.size.y), "Fredoka", 700, 15, col)


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
	return Rect2(c.position + Vector2(8, 182), Vector2(c.size.x - 16.0, 30))


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
			# Fenster „Champion noch gesperrt“ (freigegebenes Mockup)
			HeroLockBoard.hero = id
			menu.open_board("Helden-Meldung.dc.html")
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
		menu.reward_success([{"type": "hero", "hero": id, "amount": 1, "label": "%s ist jetzt im Team!" % name}], "Neuer Held")
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

	# Ziehen scrollt die Liste, kurzes Antippen öffnet eine Karte
	func _gui_input(e: InputEvent) -> void:
		if not front:
			return
		if e is InputEventMouseButton:
			var mb := e as InputEventMouseButton
			if mb.button_index == MOUSE_BUTTON_WHEEL_UP and mb.pressed:
				tab.scroll_to(tab._scroll - 40.0)
				accept_event()
			elif mb.button_index == MOUSE_BUTTON_WHEEL_DOWN and mb.pressed:
				tab.scroll_to(tab._scroll + 40.0)
				accept_event()
			elif mb.button_index == MOUSE_BUTTON_LEFT:
				if mb.pressed:
					tab._pressed = true
					tab._press = mb.position
					tab._dragged = 0.0
				elif tab._pressed:
					tab._pressed = false
					if tab._dragged < 10.0 and tab._tap(mb.position / tab.s):
						accept_event()
		elif e is InputEventMouseMotion and tab._pressed:
			var mm := e as InputEventMouseMotion
			tab._dragged += mm.relative.length()
			if tab._dragged >= 10.0:
				tab.scroll_to(tab._scroll - mm.relative.y / tab.s)
			accept_event()
