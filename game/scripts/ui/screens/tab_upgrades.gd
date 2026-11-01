class_name UpgradesTab
extends MockScreen
## Reiter „Upgrades“ nach den Mockups „Upgrades“ (Tech-Baum) und „Upgrades · Talente“.
## Oben zwei Unterreiter TECH-BAUM / TALENTE; jeder ist ein eigener Mockup-Bildschirm
## (ui_mock/upgrades_tech, ui_mock/upgrades_talent), gewählt über menu.sub_tab["upgrades"].
##
## Tech-Baum: Knoten von unten nach oben (MetaData.TECH), gebaut / als nächstes kaufbar / gesperrt,
## mit Rahmen und Symbolen aus dem Mockup. Der Baum scrollt, wenn er höher als der Bildschirm ist.
## Antippen öffnet das Fenster aus dem Mockup (Beschreibung, Preis, AUFWERTEN).
## Munition (dauerhafte Stufen der Kugelbahn) steht nicht im Mockup und öffnet sich über einen
## Knopf links unten im Baum in einem Fenster im selben Stil.
##
## Talente: Raster mit entdeckten Talenten (Karte, Symbol, Stufe) und „?“-Feldern, unten
## „Neues Talent erhalten“ mit Ziehen für einen Stern und „5 Sterne auf einmal ziehen“.

const TECH_TOP := {"level": "12", "energy": "25/30", "gold": "4.573", "gems": "350"}
const TALENT_TOP := {"level": "12", "stars": "3", "gold": "4.573", "gems": "350"}

## Baum: Abstand der Knoten, Mitte, sichtbarer Bereich (Mockup-Punkte)
const STEP := 150.0
const TREE_X := 195.0
const TREE_RECT := Rect2(0, 64, 390, 646)
const CUR_Y := 332.0        # Mitte des aktuellen Knotens im Mockup
const FIRST_Y := 632.0      # Mitte des untersten Knotens im Mockup
const TOP_Y := 160.0        # höchste Lage des obersten Knotens
const AMMO_BUTTON := Rect2(16, 660, 112, 40)

## Talente: Raster (Mockup: 4 Spalten, Karten 112 hoch, 8 Punkte Abstand)
const GRID_RECT := Rect2(12, 72, 366, 470)
const GRID_COLS := 4
const GRID_CELLS := 16
const CELL := Vector2(85.5, 112)
const GAP := 8.0

var talents := false
var _tex := {}
var _tree: TreeLayer
var _grid: TalentGrid
var _pop: MockView          # Fenster zu einem Knoten
var _pop_index := -1
var _bought: MockView       # Meldung „… gebaut!“
var _ammo: AmmoPanel
var _talent_pop: TalentPop
var _ammo_btn: AmmoButton


static func _is_talents(m: MainMenu) -> bool:
	return str(m.sub_tab.get("upgrades", "tech")) == "talente"


func _init(m: MainMenu) -> void:
	super("upgrades_talent" if _is_talents(m) else "upgrades_tech", m, TALENT_TOP if _is_talents(m) else TECH_TOP)
	talents = _is_talents(m)


func _ready() -> void:
	super()
	_copy_nav_badges()
	if talents:
		_grid = TalentGrid.new()
		_grid.tab = self
		place_at(_grid, GRID_RECT)
	else:
		_tree = TreeLayer.new()
		_tree.tab = self
		place_at(_tree, TREE_RECT)
		_ammo_btn = AmmoButton.new()
		_ammo_btn.tab = self
		place_at(_ammo_btn, AMMO_BUTTON, true)
		if str(menu.sub_tab.get("upgrades", "")) == "munition":
			open_ammo()
	bind()


# --- gemeinsame Werte ------------------------------------------------------------------

func bind() -> void:
	var tech := button("showTech")
	var tal := button("showTalent")
	if tech and tal:
		tech.badge = talents and Save.can_buy_tech()
		tal.badge = not talents and Save.can_draw_talent()
	if talents:
		var one := button("#stern")
		if one:
			one.modulate.a = 1.0 if Save.can_draw_talent() else 0.6
		var five := button("#fuenf")
		if five:
			five.modulate.a = 1.0 if Save.stars() >= 5 and Save.can_draw_talent() else 0.6
		if _grid:
			_grid.queue_redraw()
	elif _tree:
		_tree.queue_redraw()
	if _ammo_btn:
		_ammo_btn.queue_redraw()
	if is_instance_valid(_ammo):
		_ammo.queue_redraw()


## Die Reiterleiste dieser Mockups hat keine roten Punkte: Lage wie im Hauptbildschirm übernehmen
func _copy_nav_badges() -> void:
	var home: Dictionary = MockView.layout_of("home").get("states", {}).get("main", {})
	var home_btns := {}
	for hb in home.get("buttons", []):
		home_btns[int(hb["i"])] = hb
	for l in home.get("live", []):
		if not bool(l.get("badge", false)) or not home_btns.has(int(l.get("button", -1))):
			continue
		var hb: Dictionary = home_btns[int(l["button"])]
		var href := str(hb.get("href", ""))
		var mine := button(href) if href != "" else null
		if mine == null:
			continue
		var hr: Array = hb["rect"]
		var mr: Array = mine.info["rect"]
		var r: Array = l["rect"]
		mine.badge_rect = Rect2(float(r[0]) - float(hr[0]) + float(mr[0]), float(r[1]) - float(hr[1]) + float(mr[1]), r[2], r[3])


func handle(b: Dictionary) -> bool:
	var on := str(b.get("on", ""))
	var href := str(b.get("href", ""))
	var label := str(b.get("label", ""))
	match on:
		"showTech", "showTalent":
			var want := on == "showTalent"
			if want != talents:
				menu.sub_tab["upgrades"] = "talente" if want else "tech"
				menu.show_tab("upgrades")
			return true
		"closePop":
			close_pop()
			return true
		"buy":
			_buy_tech()
			return true
	match href:
		"#stern":
			_draw_talents(1)
			return true
		"#fuenf":
			_draw_talents(5)
			return true
		"#werbung":
			menu.info("Talent für Werbung", "In der Testphase gibt es keine Werbung. Talente gibt es hier für Sterne – Sterne bekommst du für gewonnene Level.")
			return true
	if label == "Talentsterne kaufen":
		menu.toast("Sterne gibt es für gewonnene Level.")
		return true
	return false


# --- Bilder und Texte ------------------------------------------------------------------

## Bild eines Live-Elements (aus diesem Bildschirm oder einem Popup darüber)
func tex_in(v: MockView, id: String) -> Texture2D:
	var key := v.overlay + "/" + id
	if not _tex.has(key):
		var l: Dictionary = v._live_info.get(id, {})
		_tex[key] = load("res://ui_mock/%s/%s" % [v.screen, l["img"]]) if str(l.get("img", "")) != "" else null
	return _tex[key]


## Wo das Bild eines Live-Elements liegt, wenn seine Mitte bei c ist (Mockup-Punkte, Maßstab k)
func part_in(v: MockView, id: String, c: Vector2, k := 1.0) -> Rect2:
	var lr := v.live_rect(id)
	var ir: Array = v._live_info.get(id, {}).get("img_rect", [0, 0, 0, 0])
	return Rect2(c + (Vector2(ir[0], ir[1]) - lr.get_center()) * k, Vector2(ir[2], ir[3]) * k)


## Bild eines Live-Elements zeichnen; origin = Mockup-Punkt, der im CanvasItem bei (0,0) liegt
func draw_part(ci: CanvasItem, v: MockView, id: String, c: Vector2, origin: Vector2, k := 1.0, mod := Color.WHITE) -> void:
	var t := tex_in(v, id)
	if t == null:
		return
	var r := part_in(v, id, c, k)
	ci.draw_texture_rect(t, Rect2((r.position - origin) * s, r.size * s), false, mod)


## Text in Mockup-Schrift; p = Ankerpunkt in Bildschirmpunkten (x je nach align, y = Mitte)
func label_at(ci: CanvasItem, txt: String, p: Vector2, family: String, weight: int, size_pt: float, col: Color, align := 0, shadow := Color(0, 0, 0, 0), shadow_off := Vector2.ZERO) -> float:
	var fs := maxi(1, roundi(size_pt * s))
	var font := MockFonts.font(family, weight)
	var tw := font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var x := p.x - tw * 0.5
	if align < 0:
		x = p.x
	elif align > 0:
		x = p.x - tw
	var base := Vector2(x, p.y + (font.get_ascent(fs) - font.get_descent(fs)) * 0.5)
	if shadow.a > 0.0:
		ci.draw_string(font, base + shadow_off * s, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, shadow)
	ci.draw_string(font, base, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
	return tw


func text_width(txt: String, family: String, weight: int, size_pt: float) -> float:
	var fs := maxi(1, roundi(size_pt * s))
	return MockFonts.font(family, weight).get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x / s


## Zeilen umbrechen (Breite in Mockup-Punkten)
func wrap(txt: String, family: String, weight: int, size_pt: float, width: float) -> PackedStringArray:
	var out := PackedStringArray()
	var line := ""
	for w in txt.split(" ", false):
		var test := w if line == "" else line + " " + w
		if line != "" and text_width(test, family, weight, size_pt) > width:
			out.append(line)
			line = w
		else:
			line = test
	if line != "":
		out.append(line)
	return out


## Knopfbild aus dem Mockup in anderer Größe zeichnen: Ecken bleiben, die Mitte dehnt sich.
## info = Knopf aus der layout.json (rect, img_rect), hit = neue Lage des Knopfs (Mockup-Punkte),
## radius = Eckenradius im Mockup.
func draw_button_image(ci: CanvasItem, info: Dictionary, t: Texture2D, hit: Rect2, origin: Vector2, radius: float, mod := Color.WHITE) -> void:
	if t == null:
		return
	var hr: Array = info["rect"]
	var ir: Array = info["img_rect"]
	var tl := Vector2(float(hr[0]) - float(ir[0]), float(hr[1]) - float(ir[1]))
	var br := Vector2(float(ir[0]) + float(ir[2]) - float(hr[0]) - float(hr[2]), float(ir[1]) + float(ir[3]) - float(hr[1]) - float(hr[3]))
	var dest := Rect2((hit.position - tl - origin) * s, (hit.size + tl + br) * s)
	var ppt := t.get_size().x / float(ir[2])   # Bildpunkte je Mockup-Punkt
	var m := [tl.x + radius, tl.y + radius, br.x + radius, br.y + radius]
	var ts := t.get_size()
	var sx := [0.0, m[0] * ppt, ts.x - m[2] * ppt, ts.x]
	var sy := [0.0, m[1] * ppt, ts.y - m[3] * ppt, ts.y]
	var dx := [dest.position.x, dest.position.x + m[0] * s, dest.end.x - m[2] * s, dest.end.x]
	var dy := [dest.position.y, dest.position.y + m[1] * s, dest.end.y - m[3] * s, dest.end.y]
	for i in 3:
		for j in 3:
			var src := Rect2(sx[i], sy[j], sx[i + 1] - sx[i], sy[j + 1] - sy[j])
			var dst := Rect2(dx[i], dy[j], dx[i + 1] - dx[i], dy[j + 1] - dy[j])
			if src.size.x > 0.0 and src.size.y > 0.0 and dst.size.x > 0.0 and dst.size.y > 0.0:
				ci.draw_texture_rect_region(t, dst, src, mod)


# --- Tech-Baum ---------------------------------------------------------------------------

func tech_state(i: int) -> String:
	var done := Save.tech_count()
	if i < done:
		return "done"
	return "cur" if i == done else "lock"


func open_pop(i: int) -> void:
	close_pop()
	var st := tech_state(i)
	_pop = open_overlay({"done": "pop_done", "cur": "pop_cur", "lock": "pop_lock"}[st])
	_pop_index = i
	_pop.gui_input.connect(_on_pop_input)
	if st == "lock":
		_pop.hide_text("Erst Schildgenerator II bauen")
	var buy := _pop.button("buy")
	if buy:
		buy.modulate.a = 1.0 if Save.gold() >= int(MetaData.TECH[i]["cost"]) else 0.6
	var layer := PopLayer.new()
	layer.tab = self
	layer.view = _pop
	layer.index = i
	_pop.place_at(layer, Rect2(0, 0, W, H))


func close_pop() -> void:
	if is_instance_valid(_pop):
		close_overlay(_pop)
	_pop = null
	_pop_index = -1


func _on_pop_input(e: InputEvent) -> void:
	if e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT and is_instance_valid(_pop):
		var r: Array = _pop.data.get("rect", [0, 0, W, H])
		var p := (_pop.get_local_mouse_position() - off) / s
		if not Rect2(r[0], r[1], r[2], r[3]).grow(-20.0).has_point(p):
			close_pop()


func _buy_tech() -> void:
	var i := _pop_index
	if i < 0 or i != Save.tech_count():
		close_pop()
		return
	var t: Dictionary = MetaData.TECH[i]
	if not Save.buy_next_tech():
		menu.toast("Nicht genug Gold.")
		return
	close_pop()
	Sfx.play("levelup")
	refresh()
	if _tree:
		_tree.scroll_to(Save.tech_count())
	if is_instance_valid(_bought):
		_bought.queue_free()
	_bought = open_overlay("bought")
	_bought.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_bought.set_text("Schildgenerator II gebaut!", "%s gebaut!" % t["title"])
	_bought.set_text("Schild +10 %", str(t["desc"]))
	var b := _bought
	var tw := b.create_tween()
	tw.tween_interval(1.8)
	tw.tween_property(b, "modulate:a", 0.0, 0.25)
	tw.tween_callback(b.queue_free)


func open_ammo() -> void:
	if is_instance_valid(_ammo):
		return
	_ammo = AmmoPanel.new()
	_ammo.tab = self
	place_at(_ammo, Rect2(0, 0, W, H), true)


func close_ammo() -> void:
	if is_instance_valid(_ammo):
		_ammo.queue_free()
	_ammo = null
	if str(menu.sub_tab.get("upgrades", "")) == "munition":
		menu.sub_tab["upgrades"] = "tech"


# --- Talente -------------------------------------------------------------------------------

## Entdeckte Talente zuerst (Reihenfolge wie in MetaData.TALENTS), danach „?“
func grid_ids() -> Array[String]:
	var out: Array[String] = []
	for id in MetaData.TALENTS.keys():
		if Save.talent_level(id) > 0:
			out.append(id)
	return out


func cell_rect(k: int) -> Rect2:
	var col := k % GRID_COLS
	var row := k / GRID_COLS
	return Rect2(GRID_RECT.position + Vector2(col * (CELL.x + GAP), row * (CELL.y + GAP)), CELL)


## Talentkarte zeichnen: r = Lage der Karte (Mockup-Punkte), origin wie bei draw_part
func draw_card(ci: CanvasItem, id: String, level: int, r: Rect2, origin: Vector2) -> void:
	var k := r.size.x / CELL.x
	var c := r.get_center()
	draw_part(ci, self, "card", c, origin, k)
	var idx := MetaData.TALENTS.keys().find(id)
	var icon_id := "tic" if idx == 0 else "tic_%d" % idx
	draw_part(ci, self, icon_id, r.position + Vector2(CELL.x * 0.5, 56.0) * k, origin, k)
	var t: Dictionary = MetaData.TALENTS[id]
	var title := str(t["title"])
	var size_pt := 11.0 * k
	while text_width(title, "Fredoka", 700, size_pt) > (CELL.x - 2.0) * k and size_pt > 7.0:
		size_pt -= 0.5
	label_at(ci, title, (r.position + Vector2(CELL.x * 0.5, 10.0) * k - origin) * s, "Fredoka", 700, size_pt, Color("#fff7ea"))
	label_at(ci, "Stufe %d" % level, (r.position + Vector2(CELL.x * 0.5, 99.5) * k - origin) * s, "Nunito", 800, 11.0 * k, Color("#0f3d12"))


func draw_unknown(ci: CanvasItem, r: Rect2, origin: Vector2) -> void:
	draw_part(ci, self, "unk", r.get_center(), origin)
	label_at(ci, "?", (r.get_center() - origin) * s, "Fredoka", 700, 44.0, Color(1, 1, 1, 0.35), 0, Color(20 / 255.0, 10 / 255.0, 80 / 255.0, 0.6), Vector2(0, 2))


func _draw_talents(n: int) -> void:
	if not Save.can_draw_talent():
		if Save.stars() <= 0:
			menu.toast("Keine Sterne. Sterne gibt es für gewonnene Level.")
		else:
			menu.toast("Alle Talente sind schon auf Stufe %d." % MetaData.TALENT_MAX)
		return
	if n > 1 and Save.stars() < n:
		menu.toast("Dafür brauchst du %d Sterne." % n)
		return
	var before := {}
	for id in MetaData.TALENTS.keys():
		before[id] = Save.talent_level(id)
	var got: Array[String] = Save.draw_talents(n)
	if got.is_empty():
		return
	var shown: Array = []
	for id in got:
		before[id] = int(before[id]) + 1
		shown.append([id, int(before[id])])
	Sfx.play("levelup")
	refresh()
	if is_instance_valid(_talent_pop):
		_talent_pop.queue_free()
	_talent_pop = TalentPop.new()
	_talent_pop.tab = self
	_talent_pop.cards = shown
	place_at(_talent_pop, Rect2(0, 0, W, H), true)


func open_talent_info(id: String) -> void:
	var t: Dictionary = MetaData.TALENTS[id]
	menu.info(str(t["title"]), "Stufe %d von %d\n\n%s" % [Save.talent_level(id), MetaData.TALENT_MAX, t["desc"]])


# ===========================================================================================

## Der Baum: Linien, Knoten, Leuchten, Nummer am aktuellen Knoten; scrollt mit dem Finger
class TreeLayer:
	extends Control
	var tab: UpgradesTab
	var node0_y := FIRST_Y      # Mitte des untersten Knotens (Mockup-Punkte, ganzer Bildschirm)
	var _press := Vector2.ZERO
	var _pressed := false
	var _dragged := false
	var _t := 0.0

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_STOP
		clip_contents = true
		node0_y = _target_for(Save.tech_count())
		for id in ["node_done", "node_cur", "node_lock", "cur_glow", "lvl_badge"]:
			tab.tex_in(tab, id)
		for k in MetaData.TECH.size():
			tab.tex_in(tab, _icon(k, false))
			tab.tex_in(tab, _icon(k, true))
		await get_tree().process_frame
		queue_redraw()

	func _process(delta: float) -> void:
		_t += delta
		if Save.tech_count() < MetaData.TECH.size():
			queue_redraw()   # Leuchten am aktuellen Knoten pulsiert

	static func _icon(k: int, gray: bool) -> String:
		var base := "gicon" if gray else "icon"
		return base if k == 0 else "%s_%d" % [base, k]

	func _max_y() -> float:
		return maxf(FIRST_Y, TOP_Y + STEP * (MetaData.TECH.size() - 1))

	func _target_for(cur: int) -> float:
		return clampf(CUR_Y + STEP * mini(cur, MetaData.TECH.size() - 1), FIRST_Y, _max_y())

	func scroll_to(cur: int) -> void:
		var tw := create_tween()
		tw.tween_property(self, "node0_y", _target_for(cur), 0.45).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
		tw.parallel().tween_method(func(_v: float) -> void: queue_redraw(), 0.0, 1.0, 0.45)

	func center_of(i: int) -> Vector2:
		return Vector2(TREE_X, node0_y - STEP * i)

	func _draw() -> void:
		var o := TREE_RECT.position
		var s := tab.s
		var n := MetaData.TECH.size()
		var done := Save.tech_count()
		var top := center_of(n - 1)
		var bottom := center_of(0)
		# graue Linie durch alle Knoten, darüber der Weg bis zum aktuellen Knoten (gold → grün)
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color(1, 1, 1, 0.35)
		sb.set_corner_radius_all(maxi(1, roundi(5 * s)))
		draw_style_box(sb, Rect2((Vector2(190, top.y) - o) * s, Vector2(10, bottom.y - top.y) * s))
		if done > 0:
			var hi := center_of(mini(done, n - 1))
			_gradient_line(hi.y, bottom.y, Color("#ffd34d"), Color("#3fd05a"))
		var cur := done if done < n else -1
		for i in n:
			var c := center_of(i)
			if c.y < o.y - 120.0 or c.y > o.y + TREE_RECT.size.y + 120.0:
				continue
			var st := tab.tech_state(i)
			tab.draw_part(self, tab, "node_" + st, c, o)
			tab.draw_part(self, tab, _icon(i, st == "lock"), c, o)
			if i == cur:
				var pulse := 0.9 + 0.1 * sin(_t * TAU / 1.8)
				tab.draw_part(self, tab, "cur_glow", c, o, pulse)
				var bc := c + Vector2(82, 0)
				tab.draw_part(self, tab, "lvl_badge", bc, o)
				tab.label_at(self, str(i + 1), (bc - o) * s, "Fredoka", 700, 15.0, Color("#5a2400"))

	func _gradient_line(y0: float, y1: float, c0: Color, c1: Color) -> void:
		var o := TREE_RECT.position
		var s := tab.s
		var r := 5.0
		var pts := PackedVector2Array()
		var cols := PackedColorArray()
		# Rechteck mit Verlauf, oben und unten halbrund
		for j in 9:
			var a := PI + PI * j / 8.0
			pts.append((Vector2(195, y0) + Vector2(cos(a), sin(a)) * r - o) * s)
			cols.append(c0)
		for j in 9:
			var a := PI * j / 8.0
			pts.append((Vector2(195, y1) + Vector2(cos(a), sin(a)) * r - o) * s)
			cols.append(c1)
		# Reihenfolge: oben links → oben rechts, unten rechts → unten links
		var ordered := PackedVector2Array()
		var ocols := PackedColorArray()
		for j in 9:
			ordered.append(pts[j])
			ocols.append(cols[j])
		for j in 9:
			ordered.append(pts[9 + j])
			ocols.append(cols[9 + j])
		draw_polygon(ordered, ocols)

	func _gui_input(e: InputEvent) -> void:
		if e is InputEventMouseButton and e.button_index == MOUSE_BUTTON_LEFT:
			if e.pressed:
				_pressed = true
				_dragged = false
				_press = e.position
			elif _pressed:
				_pressed = false
				if not _dragged:
					_tap(e.position)
			accept_event()
		elif e is InputEventMouseMotion and _pressed:
			if (e.position - _press).length() > 8.0:
				_dragged = true
			if _dragged:
				node0_y = clampf(node0_y + e.relative.y / tab.s, FIRST_Y, _max_y())
				queue_redraw()
			accept_event()

	func _tap(p_local: Vector2) -> void:
		var p := p_local / tab.s + TREE_RECT.position
		for i in MetaData.TECH.size():
			var c := center_of(i)
			if Rect2(c - Vector2(52, 52), Vector2(104, 104)).has_point(p):
				Sfx.play("click")
				tab.open_pop(i)
				return


## Inhalt des Knoten-Fensters, der sich ändert: Symbol, Name, Beschreibung, Preis, Hinweis
class PopLayer:
	extends Control
	var tab: UpgradesTab
	var view: MockView
	var index := 0

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE
		tab.tex_in(view, "coin")
		tab.tex_in(view, "need_lock")
		await get_tree().process_frame
		queue_redraw()

	func _draw() -> void:
		var s := tab.s
		var t: Dictionary = MetaData.TECH[index]
		var st := tab.tech_state(index)
		var ic := view.live_rect("pop_icon")
		var icon_id := TreeLayer._icon(index, false)   # im Fenster immer farbig (wie im Mockup)
		tab.draw_part(self, tab, icon_id, ic.get_center(), Vector2.ZERO, ic.size.x / 54.0)
		# Name und Beschreibung, gemeinsam mittig neben dem Symbol
		var tr := view.live_rect("pop_text")
		var lines := tab.wrap(str(t["desc"]), "Nunito", 700, 13.0, tr.size.x)
		var h := 24.0 + 18.0 * lines.size()
		var y := ic.get_center().y - h * 0.5
		tab.label_at(self, str(t["title"]), Vector2(tr.position.x, y + 12.0) * s, "Fredoka", 700, 20.0, Color("#fff7ea"), -1)
		for k in lines.size():
			tab.label_at(self, lines[k], Vector2(tr.position.x, y + 24.0 + 9.0 + 18.0 * k) * s, "Nunito", 700, 13.0, Color("#d6d0f5"), -1)
		# Preis rechtsbündig, Münze davor
		var pr := view.live_rect("price")
		var price := "%s Gold" % MockScreen.num(int(t["cost"]))
		var tw := tab.text_width(price, "Fredoka", 700, 16.0)
		var right := pr.end.x
		tab.label_at(self, price, Vector2(right, pr.get_center().y) * s, "Fredoka", 700, 16.0, Color("#ffe27a"), 1)
		tab.draw_part(self, view, "coin", Vector2(right - tw - 5.0 - 9.0, pr.get_center().y), Vector2.ZERO)
		# gesperrt: „Erst … bauen“ mit Schloss, mittig im Kasten
		if st == "lock" and index > 0:
			var need := "Erst %s bauen" % MetaData.TECH[index - 1]["title"]
			var nw := tab.text_width(need, "Fredoka", 700, 15.0)
			var lk := view.live_rect("need_lock")
			var x0 := TREE_X - (16.0 + 8.0 + nw) * 0.5
			tab.draw_part(self, view, "need_lock", Vector2(x0 + 8.0, lk.get_center().y), Vector2.ZERO)
			tab.label_at(self, need, Vector2(x0 + 24.0, lk.get_center().y - 0.5) * s, "Fredoka", 700, 15.0, Color("#d6d0f5"), -1)


## Knopf „MUNITION“ links unten im Baum (nicht im Mockup, im Stil der Unterreiter)
class AmmoButton:
	extends Control
	var tab: UpgradesTab
	var _tex: Texture2D

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_STOP
		pivot_offset = size * 0.5
		var b := tab.button("showTech")
		if b:
			_tex = b.texture
		await get_tree().process_frame
		queue_redraw()

	func _process(_d: float) -> void:
		pivot_offset = size * 0.5

	func _draw() -> void:
		var s := tab.s
		var b := tab.button("showTech")
		if b and _tex:
			# Bild des aktiven Unterreiters, auf die Größe dieses Knopfs gebracht
			tab.draw_button_image(self, b.info, _tex, AMMO_BUTTON, AMMO_BUTTON.position, 10.0)
		tab.label_at(self, "MUNITION", size * 0.5, "Fredoka", 700, 15.0, Color.WHITE)
		if Save.any_ammo_upgrade():
			var p := Vector2(size.x - 4.0 * s, 2.0 * s)
			draw_circle(p, 6.0 * s, Color.WHITE)
			draw_circle(p, 4.0 * s, Color(1.0, 0.23, 0.19))

	func _gui_input(e: InputEvent) -> void:
		if e is InputEventMouseButton and e.button_index == MOUSE_BUTTON_LEFT:
			if e.pressed:
				scale = Vector2.ONE * 0.93
			else:
				scale = Vector2.ONE
				if Rect2(Vector2.ZERO, size).has_point(e.position):
					Sfx.play("click")
					tab.open_ammo()
			accept_event()


## Fenster „Munition“: dauerhafte Stufen der Kugelbahn (Logik wie im alten Upgrade-Reiter)
class AmmoPanel:
	extends Control
	const PANEL := Rect2(16, 112, 358, 574)
	const ROW_Y := 162.0
	const ROW_H := 84.0
	var tab: UpgradesTab
	var _btn: Texture2D
	var _btn_info: Dictionary

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_STOP
		var lay: Dictionary = MockView.layout_of("upgrades_tech").get("overlays", {}).get("pop_cur", {})
		for b in lay.get("buttons", []):
			if str(b.get("on", "")) == "buy":
				_btn_info = b
				_btn = load("res://ui_mock/upgrades_tech/" + str(b["img"]))
		modulate.a = 0.0
		create_tween().tween_property(self, "modulate:a", 1.0, 0.15)
		await get_tree().process_frame
		queue_redraw()

	func _row_button(k: int) -> Rect2:
		return Rect2(262, ROW_Y + ROW_H * k + 16.0, 98, 44)

	func _draw() -> void:
		var s := tab.s
		var o := Vector2.ZERO   # Ursprung = Mockup-Punkt (0,0)
		draw_rect(Rect2(-tab.off, tab.size), Color(0.04, 0.02, 0.12, 0.55))
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color(20 / 255.0, 12 / 255.0, 48 / 255.0, 0.96)
		sb.border_color = Color(1, 1, 1, 0.15)
		sb.set_border_width_all(maxi(1, roundi(2 * s)))
		sb.set_corner_radius_all(roundi(16 * s))
		sb.shadow_color = Color(0, 0, 0, 0.35)
		sb.shadow_size = roundi(20 * s)
		draw_style_box(sb, Rect2(o + PANEL.position * s, PANEL.size * s))
		# Reiter-Kopf wie „Neues Talent erhalten“
		var hb := StyleBoxFlat.new()
		hb.bg_color = Color("#24203a")
		hb.corner_radius_top_left = roundi(8 * s)
		hb.corner_radius_top_right = roundi(8 * s)
		var head := Rect2(100, PANEL.position.y - 14.0, 190, 31)
		draw_style_box(hb, Rect2(o + head.position * s, head.size * s))
		tab.label_at(self, "Munition", o + head.get_center() * s, "Fredoka", 700, 15.0, Color("#fff7ea"))
		# Schließen-Kreuz
		var cr := Rect2(326, PANEL.position.y + 12.0, 34, 34)
		var cb := StyleBoxFlat.new()
		cb.bg_color = Color(1, 1, 1, 0.12)
		cb.set_corner_radius_all(roundi(10 * s))
		draw_style_box(cb, Rect2(o + cr.position * s, cr.size * s))
		var cc := o + cr.get_center() * s
		var d := 5.0 * s
		draw_line(cc + Vector2(-d, -d), cc + Vector2(d, d), Color.WHITE, 2.3 * s, true)
		draw_line(cc + Vector2(d, -d), cc + Vector2(-d, d), Color.WHITE, 2.3 * s, true)
		tab.label_at(self, "Gilt in jedem Kampf.", o + Vector2(32, PANEL.position.y + 29.0) * s, "Nunito", 700, 13.0, Color("#d6d0f5"), -1)
		for k in MetaData.AMMO_UPGRADES.size():
			_row(k)

	func _row(k: int) -> void:
		var s := tab.s
		var o := Vector2.ZERO
		var u: Dictionary = MetaData.AMMO_UPGRADES[k]
		var id := str(u["id"])
		var lvl := Save.ammo_level(id)
		var mx := int(u["max"])
		var y := ROW_Y + ROW_H * k
		var rb := StyleBoxFlat.new()
		rb.bg_color = Color(0, 0, 0, 0.25)
		rb.set_corner_radius_all(roundi(10 * s))
		draw_style_box(rb, Rect2(o + Vector2(28, y) * s, Vector2(334, 76) * s))
		var tw := tab.label_at(self, str(u["title"]), o + Vector2(40, y + 15.0) * s, "Fredoka", 700, 16.0, Color("#fff7ea"), -1)
		tab.label_at(self, "Stufe %d/%d" % [lvl, mx], o + Vector2(40, y + 15.0) * s + Vector2(tw + 8.0 * s, 1.0 * s), "Nunito", 800, 12.0, Color("#ffe27a"), -1)
		var lines := tab.wrap(String(u["desc"]).replace("%%", "%"), "Nunito", 700, 12.0, 212.0)
		for j in mini(lines.size(), 2):
			tab.label_at(self, lines[j], o + Vector2(40, y + 35.0 + 15.0 * j) * s, "Nunito", 700, 12.0, Color("#d6d0f5"), -1)
		# Fortschritt
		var bar := Rect2(40, y + 64.0, 212, 5)
		var bb := StyleBoxFlat.new()
		bb.bg_color = Color(1, 1, 1, 0.15)
		bb.set_corner_radius_all(maxi(1, roundi(2.5 * s)))
		draw_style_box(bb, Rect2(o + bar.position * s, bar.size * s))
		if lvl > 0:
			bb.bg_color = Color("#ffd34d")
			draw_style_box(bb, Rect2(o + bar.position * s, Vector2(bar.size.x * lvl / float(mx), bar.size.y) * s))
		var br := _row_button(k)
		if lvl >= mx:
			var mb := StyleBoxFlat.new()
			mb.bg_color = Color(63 / 255.0, 208 / 255.0, 90 / 255.0, 0.18)
			mb.border_color = Color("#3fd05a")
			mb.set_border_width_all(maxi(1, roundi(2 * s)))
			mb.set_corner_radius_all(roundi(14 * s))
			draw_style_box(mb, Rect2(o + br.position * s, br.size * s))
			tab.label_at(self, "MAX", o + br.get_center() * s, "Fredoka", 700, 17.0, Color("#9dff7a"))
			return
		var cost := MetaData.ammo_cost(u, lvl)
		var can := Save.gold() >= cost
		if _btn:
			# grüner Knopf aus dem Mockup-Fenster (AUFWERTEN)
			tab.draw_button_image(self, _btn_info, _btn, br, Vector2.ZERO, 14.0, Color(1, 1, 1, 1.0 if can else 0.55))
		var price := MockScreen.num(cost)
		var pw := tab.text_width(price, "Fredoka", 700, 16.0)
		var x0 := br.get_center().x - (18.0 + 5.0 + pw) * 0.5
		_coin(o + Vector2(x0 + 9.0, br.get_center().y) * s, 9.0 * s, can)
		tab.label_at(self, price, o + Vector2(x0 + 23.0, br.get_center().y) * s, "Fredoka", 700, 16.0, Color(15 / 255.0, 61 / 255.0, 18 / 255.0, 1.0 if can else 0.6), -1)

	## Goldmünze wie im Mockup (Kreis mit Rand und hellem Innenring)
	func _coin(c: Vector2, r: float, bright: bool) -> void:
		var a := 1.0 if bright else 0.6
		draw_circle(c, r * 0.75 + r * 0.0625, Color(168 / 255.0, 106 / 255.0, 0, a))
		draw_circle(c, r * 0.75 - r * 0.0625, Color(1.0, 210 / 255.0, 58 / 255.0, a))
		draw_arc(c, r * 0.458, 0, TAU, 24, Color(1.0, 243 / 255.0, 176 / 255.0, a), r * 0.125, true)

	func _gui_input(e: InputEvent) -> void:
		if not (e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT):
			return
		accept_event()
		var p: Vector2 = e.position / tab.s
		if Rect2(326, PANEL.position.y + 12.0, 34, 34).grow(6.0).has_point(p) or not PANEL.has_point(p):
			Sfx.play("click")
			tab.close_ammo()
			return
		for k in MetaData.AMMO_UPGRADES.size():
			if _row_button(k).grow(4.0).has_point(p):
				var u: Dictionary = MetaData.AMMO_UPGRADES[k]
				var id := str(u["id"])
				if Save.ammo_level(id) >= int(u["max"]):
					return
				if Save.buy_ammo_upgrade(id):
					Sfx.play("levelup")
					tab.menu.toast("%s: Stufe %d" % [u["title"], Save.ammo_level(id)])
					tab.refresh()
				else:
					Sfx.play("click")
					tab.menu.toast("Nicht genug Gold.")
				return


## Das Raster der Talente: Karten (entdeckt) und „?“-Felder
class TalentGrid:
	extends Control
	var tab: UpgradesTab

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_STOP
		clip_contents = true
		tab.tex_in(tab, "card")
		tab.tex_in(tab, "unk")
		for k in MetaData.TALENTS.size():
			tab.tex_in(tab, "tic" if k == 0 else "tic_%d" % k)
		await get_tree().process_frame
		queue_redraw()

	func _draw() -> void:
		var ids := tab.grid_ids()
		for k in GRID_CELLS:
			var r := tab.cell_rect(k)
			if k < ids.size():
				tab.draw_card(self, ids[k], Save.talent_level(ids[k]), r, GRID_RECT.position)
			else:
				tab.draw_unknown(self, r, GRID_RECT.position)

	func _gui_input(e: InputEvent) -> void:
		if e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT:
			accept_event()
			var p: Vector2 = e.position / tab.s + GRID_RECT.position
			var ids := tab.grid_ids()
			for k in GRID_CELLS:
				if tab.cell_rect(k).has_point(p):
					Sfx.play("click")
					if k < ids.size():
						tab.open_talent_info(ids[k])
					else:
						tab.menu.toast("Noch nicht entdeckt. Öffne ein Talent für einen Stern.")
					return


## Popup „Neues Talent erhalten“: gezogene Karten groß, darunter die grüne Meldung aus dem
## Mockup (Stil der Meldung „… gebaut!“). Antippen schließt.
class TalentPop:
	extends Control
	var tab: UpgradesTab
	var cards: Array = []     # [id, Stufe]
	var _t := 0.0

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_STOP
		modulate.a = 0.0
		create_tween().tween_property(self, "modulate:a", 1.0, 0.18)
		await get_tree().process_frame
		queue_redraw()

	func _process(delta: float) -> void:
		if _t < 0.5:
			_t += delta
			queue_redraw()

	func _draw() -> void:
		var s := tab.s
		var o := Vector2.ZERO   # Ursprung = Mockup-Punkt (0,0)
		draw_rect(Rect2(-tab.off, tab.size), Color(0.04, 0.02, 0.12, 0.6))
		var n := cards.size()
		var k0 := 1.6 if n == 1 else minf(1.0, (358.0 - 6.0 * (n - 1)) / (CELL.x * n))
		var k := k0 * (0.85 + 0.15 * ease(clampf(_t / 0.35, 0.0, 1.0), 0.4))
		var cw := CELL.x * k
		var total := cw * n + 6.0 * (n - 1)
		var y := 300.0 - CELL.y * k * 0.5
		for j in n:
			var r := Rect2(195.0 - total * 0.5 + j * (cw + 6.0), y, cw, CELL.y * k)
			tab.draw_card(self, str(cards[j][0]), int(cards[j][1]), r, o)
		# Meldung
		var head := "Neues Talent erhalten!" if n == 1 else "%d neue Talente erhalten!" % n
		var sub: PackedStringArray
		if n == 1:
			var t: Dictionary = MetaData.TALENTS[cards[0][0]]
			sub = tab.wrap("%s · Stufe %d: %s" % [t["title"], cards[0][1], t["desc"]], "Nunito", 800, 13.0, 240.0)
		else:
			sub = tab.wrap("Sie gelten ab dem nächsten Kampf.", "Nunito", 800, 13.0, 240.0)
		var box_h := 12.0 * 2.0 + 3.0 * 2.0 + 22.0 + 18.0 * sub.size()
		var box := Rect2(60, 300.0 + CELL.y * k0 * 0.5 + 24.0, 270, box_h)
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color(20 / 255.0, 60 / 255.0, 30 / 255.0, 0.92)
		sb.border_color = Color("#9dff7a")
		sb.set_border_width_all(maxi(1, roundi(3 * s)))
		sb.set_corner_radius_all(roundi(16 * s))
		sb.shadow_color = Color(120 / 255.0, 1.0, 120 / 255.0, 0.6)
		sb.shadow_size = roundi(24 * s * 0.5)
		draw_style_box(sb, Rect2(o + box.position * s, box.size * s))
		var cy := box.position.y + 15.0 + 11.0
		tab.label_at(self, head, o + Vector2(195, cy) * s, "Fredoka", 700, 18.0, Color("#e8ffd8"))
		for j in sub.size():
			tab.label_at(self, sub[j], o + Vector2(195, cy + 20.0 + 18.0 * j) * s, "Nunito", 800, 13.0, Color("#e8ffd8"))

	func _gui_input(e: InputEvent) -> void:
		if e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT:
			accept_event()
			queue_free()
