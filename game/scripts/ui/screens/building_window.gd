class_name BuildingWindow
extends MockScreen
## Gebäudefenster des Basislagers nach den Mockups „Basislager · Gebäude“ (gebaut, Erzeuger mit Lager)
## und „Basislager · Bauplatz“ (noch nicht gebaut). Rahmen, Kopfleiste, Reiterleiste und die Knöpfe
## kommen als Bilder aus dem Export (Bildschirm „gebaeude“, Zustände „lager“ und „plain“; Schloss und
## Hammer aus „bauplatz“). Was je Gebäude wechselt, zeichnet das Fenster selbst an die Stellen des
## Mockups: Bild, Untertitel, Wertezeile (jetzt → nächste Stufe), Lager, Hinweis, Text und den Inhalt
## des großen Knopfs. Dahinter liegt die Basis verschwommen und abgedunkelt.

const TOP := {"energy": "25/30", "gold": "4.674", "gems": "350"}
const TITLE := "Werkstatt"
const LAGER_TEXT := "Lager: 7 von 13 Karten"
## Lage im Mockup (Punkte)
const CHIP_Y := 170.5
const PIC_INNER := Rect2(92, 204, 210, 170)
const BAR_INNER := Rect2(43.5, 461.5, 189, 17)
const BOX := Rect2(42.5, 442.5, 305, 40)
const DESC_LAGER_Y := 510.5
const DESC_BOX_Y := 502.5
const DESC_PLAIN_Y := 446.5
const DESC_X := 42.5
const DESC_W := 305.0
const HINT_Y := 632.0

const C_CHIP := "#cfc8f0"
const C_ROW := "#e8e2ff"
const C_NEXT := "#7dff8a"
const C_BTN := "#4a2000"
const C_SHORT := "#b3261e"

var id := ""
var _backdrop: Texture2D
var _layer: Layer
var _content: BigContent
var _lock: TextureRect
var _pic: TextureRect


func _init(m: MainMenu, building: String, backdrop: Texture2D = null) -> void:
	id = building
	_backdrop = backdrop
	var built := Save.base_state(building) == "built"
	super("gebaeude", m, TOP)
	state = "lager" if built and BaseData.info(building)["kind"] == "prod" else "plain"


func _ready() -> void:
	super()
	_fill.visible = false
	_add_backdrop()
	var st := Save.base_state(id)
	for l in ["pic", "row", "bar"]:
		live_image(l)
	_pic = TextureRect.new()
	_pic.texture = load("res://ui/base/bild_%s.webp" % id)
	_pic.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_pic.stretch_mode = TextureRect.STRETCH_SCALE
	_pic.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var mat := ShaderMaterial.new()
	mat.shader = load("res://shaders/gebaeude_bild.gdshader")
	var ts := _pic.texture.get_size() if _pic.texture else Vector2(240, 204)
	mat.set_shader_parameter("img", Vector2(220.0, 220.0 * ts.y / ts.x))
	mat.set_shader_parameter("grey", 0.0 if st == "built" else 1.0)
	mat.set_shader_parameter("alpha", 1.0 if st == "built" else 0.55)
	_pic.material = mat
	place_at(_pic, PIC_INNER)
	if st != "built":
		_lock = _bauplatz_image("lock")
	_layer = Layer.new()
	_layer.win = self
	place_at(_layer, Rect2(0, 0, W, H))
	var big := _big_button()
	if big:
		_content = BigContent.new()
		_content.win = self
		_content.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		_content.mouse_filter = Control.MOUSE_FILTER_IGNORE
		big.add_child(_content)
	BaseTab.copy_nav_badges(self)
	for item in ["gold", "cards", "energy", "gems", "stars"]:
		icon_tex(item)
	bind()
	# frisch geladene Bilder sind im ersten Bild noch nicht bereit
	await get_tree().process_frame
	if is_instance_valid(_layer):
		_layer.queue_redraw()
	if is_instance_valid(_content):
		_content.queue_redraw()


## Verschwommenes, abgedunkeltes Bild der Basis hinter dem Fenster (wie im Mockup: blur 4px, 70 % dunkel)
func _add_backdrop() -> void:
	if _backdrop == null and DisplayServer.get_name() != "headless":
		var vt := get_viewport().get_texture()
		var img := vt.get_image() if vt else null
		if img and img.get_width() > 16:
			img.resize(maxi(8, img.get_width() / 12), maxi(8, img.get_height() / 12), Image.INTERPOLATE_BILINEAR)
			_backdrop = ImageTexture.create_from_image(img)
	if _backdrop:
		var tr := TextureRect.new()
		tr.texture = _backdrop
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		tr.stretch_mode = TextureRect.STRETCH_SCALE
		tr.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tr.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		add_child(tr)
		move_child(tr, 0)
	var dim := ColorRect.new()
	dim.color = Color(10.0 / 255.0, 6.0 / 255.0, 30.0 / 255.0, 0.7 if _backdrop else 0.85)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	move_child(dim, 1 if _backdrop else 0)


## Schloss bzw. Hammer aus dem Export des Bauplatz-Mockups
func _bauplatz_image(live_id: String) -> TextureRect:
	var lay: Dictionary = MockView.layout_of("bauplatz").get("states", {}).get("main", {})
	for l in lay.get("live", []):
		if str(l["id"]) == live_id:
			var tr := TextureRect.new()
			tr.texture = load("res://ui_mock/bauplatz/" + str(l["img"]))
			tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
			tr.stretch_mode = TextureRect.STRETCH_SCALE
			tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
			var ir: Array = l["img_rect"]
			place_at(tr, Rect2(ir[0], ir[1], ir[2], ir[3]))
			return tr
	return null


func _big_button() -> MockButton:
	for b in buttons():
		if str(b.info.get("on", "")) == "main":
			return b
	return null


func _collect_button() -> MockButton:
	for b in buttons():
		if str(b.info.get("on", "")) == "collect":
			return b
	return null


func bind() -> void:
	refresh_top()
	if data.is_empty():
		return
	var d := BaseData.info(id)
	set_text(TITLE, str(d["name"]))
	var big := _big_button()
	if big:
		var a := action()
		big.enabled = bool(a["enabled"])
		big.modulate = Color(1, 1, 1) if a["enabled"] else Color(0.62, 0.6, 0.68)
	var col := _collect_button()
	if col:
		var ok := Save.base_stock(id) >= 1.0
		col.enabled = ok
		col.modulate = Color(1, 1, 1) if ok else Color(0.62, 0.66, 0.62)
	if _layer:
		_layer.queue_redraw()
	if _content:
		_content.refresh()


func refresh_top() -> void:
	super()
	if state == "lager" and data.size() > 0:
		set_text(LAGER_TEXT, "Lager: %d von %d %s" % [int(floor(Save.base_stock(id))), int(floor(Save.base_store_cap(id))), BaseData.store_unit(id)])
		var col := _collect_button()
		if col:
			var ok := Save.base_stock(id) >= 1.0
			col.enabled = ok
			col.modulate = Color(1, 1, 1) if ok else Color(0.62, 0.66, 0.62)
		if _layer:
			_layer.queue_redraw()


## Untertitel unter dem Namen
func subtitle() -> String:
	var kind := "Erzeuger" if BaseData.info(id)["kind"] == "prod" else "Verstärker"
	if Save.base_state(id) != "built":
		return kind + " · noch nicht gebaut"
	return kind + " · Stufe %d" % Save.base_level(id)


## Hinweis-Kasten der Bauplätze: [Text, baubar]
func requirement() -> Array:
	var st := Save.base_state(id)
	if st == "built":
		return []
	if BaseData.by_champion(id):
		return ["Kommt mit deinem %d. Champion" % int(id), false]
	var d := BaseData.info(id)
	var need := int(d["level"])
	var have := Save.max_level()
	if have < need:
		return ["Baubar ab Level %d · du bist auf Level %d" % [need, have], false]
	if st == "locked":
		return ["Erst %s bauen" % BaseData.info("%02d" % (int(id) - 1))["name"], false]
	return ["Baubar ab Level %d · du bist auf Level %d" % [need, have], true]


## Hinweis über dem großen Knopf, wenn ausbauen gerade nicht geht ("" = keiner)
func hint() -> String:
	var lvl := Save.base_level(id)
	if Save.base_state(id) == "built" and lvl < BaseData.MAX_LEVEL and id != "01" and lvl >= Save.base_level("01"):
		return "Erst die Kommandozentrale auf Stufe %d ausbauen" % (lvl + 1)
	return ""


## Was der große Knopf zeigt und tut: {text, hammer, gold, stars, enabled, kind}
func action() -> Dictionary:
	var st := Save.base_state(id)
	var d := BaseData.info(id)
	if st == "built":
		var lvl := Save.base_level(id)
		if lvl >= BaseData.MAX_LEVEL:
			return {"text": "HÖCHSTE STUFE", "hammer": false, "gold": -1, "stars": 0, "enabled": false, "kind": "none"}
		var c := BaseData.upgrade_cost(id, lvl)
		return {"text": "AUSBAUEN", "hammer": false, "gold": int(c[0]), "stars": int(c[1]), "enabled": hint() == "", "kind": "upgrade"}
	if BaseData.by_champion(id):
		return {"text": "ZU DEN HELDEN", "hammer": false, "gold": -1, "stars": 0, "enabled": true, "kind": "heroes"}
	return {"text": "BAUEN", "hammer": true, "gold": int(d["gold"]), "stars": 0, "enabled": st == "buildable", "kind": "build"}


func handle(b: Dictionary) -> bool:
	var on := str(b.get("on", ""))
	var href := str(b.get("href", ""))
	if str(b.get("label", "")) == "Schließen":
		menu.close_board(self)
		return true
	if TAB_OF.has(href):
		menu.close_board(self)
		menu.show_tab(TAB_OF[href])
		return true
	if on == "collect":
		var r := Save.base_collect(id)
		if int(r["amount"]) > 0:
			menu.reward_success([r], "Basislager · %s" % BaseData.info(id)["name"])
		else:
			menu.toast("Noch nichts bereit.")
		_changed()
		return true
	if on == "main":
		_main_action()
		return true
	return false


func _main_action() -> void:
	var a := action()
	var d := BaseData.info(id)
	match str(a["kind"]):
		"heroes":
			menu.close_board(self)
			menu.show_tab("sammlung")
		"build":
			if Save.gold() < int(a["gold"]):
				menu.toast("Nicht genug Gold.")
			elif Save.base_build(id):
				menu.celebrate("camp", "%s gebaut!" % d["name"])
				_changed(true)
		"upgrade":
			if Save.gold() < int(a["gold"]):
				menu.toast("Nicht genug Gold.")
			elif Save.stars() < int(a["stars"]):
				menu.toast("Nicht genug Talent-Sterne.")
			elif Save.base_upgrade(id):
				menu.celebrate("camp", "%s auf Stufe %d!" % [d["name"], Save.base_level(id)])
				_changed(true)


## Nach Bauen, Ausbauen, Abholen: Basis neu zeichnen, Fenster neu aufbauen (Zustand kann wechseln)
func _changed(rebuild := false) -> void:
	menu.show_tab("basis")
	if rebuild:
		menu.close_board(self)
		menu.open_building(id, _backdrop)
	else:
		bind()


# --- Selbst gezeichnete Teile --------------------------------------------------------------

func font(fam: String, weight: int) -> Font:
	return MockFonts.font(fam, weight)


func fpx(px: float) -> int:
	return maxi(1, roundi(px * s))


## Text in Mockup-Punkten zeichnen; align 0 links, 0.5 mittig, 1 rechts an x
func text_at(ci: CanvasItem, txt: String, x: float, mid_y: float, fam: String, weight: int, px: float, col: Color, align := 0.0) -> float:
	var f := font(fam, weight)
	var fs := fpx(px)
	var w := f.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var base := mid_y * s + (f.get_ascent(fs) - f.get_descent(fs)) * 0.5
	ci.draw_string(f, Vector2(x * s - w * align, base), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
	return w / s


func text_w(txt: String, fam: String, weight: int, px: float) -> float:
	return font(fam, weight).get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fpx(px)).x / s


func rounded(ci: CanvasItem, r: Rect2, fill: Color, radius: float, border := Color(0, 0, 0, 0), bw := 0.0) -> void:
	var sb := StyleBoxFlat.new()
	sb.bg_color = fill
	sb.set_corner_radius_all(roundi(radius * s))
	if bw > 0.0:
		sb.border_color = border
		sb.set_border_width_all(maxi(1, roundi(bw * s)))
	sb.anti_aliasing = true
	ci.draw_style_box(sb, Rect2(r.position * s, r.size * s))


## Zeichen, die die Schriften nicht sicher haben, als Linien: Haken, Pfeil, Funkeln
func draw_check(ci: CanvasItem, c: Vector2, size: float, col: Color) -> void:
	var p := PackedVector2Array([(c + Vector2(-0.45, 0.0) * size) * s, (c + Vector2(-0.12, 0.32) * size) * s, (c + Vector2(0.48, -0.36) * size) * s])
	ci.draw_polyline(p, col, maxf(1.5, 1.8 * s), true)


func draw_arrow(ci: CanvasItem, x: float, mid_y: float, w: float, col: Color) -> void:
	var a := Vector2(x, mid_y) * s
	var b := Vector2(x + w, mid_y) * s
	var t := maxf(1.2, 1.4 * s)
	ci.draw_line(a, b, col, t, true)
	ci.draw_line(b, b + Vector2(-3.2, -3.0) * s, col, t, true)
	ci.draw_line(b, b + Vector2(-3.2, 3.0) * s, col, t, true)


func draw_sparkle(ci: CanvasItem, c: Vector2, r: float, col: Color) -> void:
	var pts := PackedVector2Array()
	for k in 8:
		var ang := k * PI / 4.0 - PI / 2.0
		var rr := r if k % 2 == 0 else r * 0.32
		pts.append((c + Vector2(cos(ang), sin(ang)) * rr) * s)
	ci.draw_colored_polygon(pts, col)


var _icons := {}


func icon_tex(item: String) -> Texture2D:
	if not _icons.has(item):
		var path := "res://ui/icons/%s.webp" % item
		_icons[item] = load(path) if ResourceLoader.exists(path) else null
	return _icons[item]


class Layer:
	extends Control
	## Untertitel, Wertezeile, Lager-Füllung, Hinweis-Kasten und Beschreibung
	var win: BuildingWindow

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE

	func _draw() -> void:
		var w := win
		var id := w.id
		var d := BaseData.info(id)
		var st := Save.base_state(id)
		# Untertitel als Schild
		var sub := w.subtitle()
		var sw := w.text_w(sub, "Nunito", 800, 12)
		w.rounded(self, Rect2(195.0 - sw * 0.5 - 10.0, CHIP_Y, sw + 20.0, 20.4), Color(10 / 255.0, 6 / 255.0, 30 / 255.0, 0.55), 9)
		w.text_at(self, sub, 195.0, CHIP_Y + 10.2, "Nunito", 800, 12, Color(C_CHIP), 0.5)
		# Wertezeile: Symbol, Name, jetzt → nächste Stufe
		var row := w.live_rect("row")
		var mid := row.position.y + row.size.y * 0.5
		var x := row.position.x + 12.0
		var tex: Texture2D = w.icon_tex(str(d["item"])) if d["kind"] == "prod" else null
		if tex:
			draw_texture_rect(tex, Rect2(Vector2(x, mid - 9.0) * w.s, Vector2(18, 18) * w.s), false)
			x += 22.0
		else:
			w.draw_sparkle(self, Vector2(x + 6.0, mid), 6.0, Color(C_ROW))
			x += 16.0
		var lvl := Save.base_level(id)
		var right := row.end.x - 12.0
		var left_end := right
		if st == "built" and lvl >= BaseData.MAX_LEVEL:
			left_end -= w.text_at(self, BaseData.row_value(id, lvl), right, mid, "Fredoka", 700, 16, Color(C_NEXT), 1.0)
		else:
			var nxt := BaseData.row_value(id, lvl + 1)
			var nw := w.text_at(self, nxt, right, mid, "Fredoka", 700, 16, Color(C_NEXT), 1.0)
			var ax := right - nw - 8.0 - 12.0
			w.draw_arrow(self, ax, mid + 0.5, 11.0, Color(C_CHIP))
			left_end = ax - 8.0 - w.text_at(self, BaseData.row_value(id, lvl), ax - 8.0, mid, "Fredoka", 700, 16, Color(1, 0.97, 0.92), 1.0)
		# Name der Wirkung; zu lang für den Platz: etwas kleiner
		var label := BaseData.row_label(id)
		var px := 13.0
		while px > 10.0 and w.text_w(label, "Nunito", 800, px) > left_end - 10.0 - x:
			px -= 0.5
		w.text_at(self, label, x, mid, "Nunito", 800, px, Color(C_ROW))
		var desc_y := DESC_PLAIN_Y
		# Lager der Erzeuger
		if w.state == "lager":
			desc_y = DESC_LAGER_Y
			var f := clampf(Save.base_stock(id) / maxf(0.001, Save.base_store_cap(id)), 0.0, 1.0)
			if f > 0.0:
				var r := Rect2(BAR_INNER.position, Vector2(maxf(BAR_INNER.size.y, BAR_INNER.size.x * f), BAR_INNER.size.y))
				_gradient_bar(Rect2(r.position * w.s, r.size * w.s), BAR_INNER.size.x * w.s, Color("#6fe0ff"), Color("#3a8cff"))
		# Hinweis-Kasten der Bauplätze
		var req := w.requirement()
		if not req.is_empty():
			desc_y = DESC_BOX_Y
			var ok: bool = req[1]
			var fill := Color(125 / 255.0, 1.0, 138 / 255.0, 0.14) if ok else Color(1.0, 106 / 255.0, 90 / 255.0, 0.14)
			var border := Color(125 / 255.0, 1.0, 138 / 255.0, 0.5) if ok else Color(1.0, 106 / 255.0, 90 / 255.0, 0.55)
			var tc := Color("#b6ff8a") if ok else Color("#ffb0a8")
			w.rounded(self, BOX, fill, 12, border, 1.5)
			var txt: String = req[0]
			var tw := w.text_w(txt, "Nunito", 800, 13)
			var cx := 195.0 + 9.0
			var by := BOX.position.y + BOX.size.y * 0.5
			if ok:
				w.draw_check(self, Vector2(cx - tw * 0.5 - 10.0, by), 10.0, tc)
			elif w._lock and w._lock.texture:
				draw_texture_rect(w._lock.texture, Rect2(Vector2(cx - tw * 0.5 - 20.0, by - 8.0) * w.s, Vector2(15, 15) * w.s), false)
			w.text_at(self, txt, cx - tw * 0.5, by, "Nunito", 800, 13, tc)
		# Beschreibung, mittig umbrochen
		var f2 := w.font("Nunito", 700)
		var fs := w.fpx(12)
		var lines := _wrap(BaseData.description(id), f2, fs, DESC_W * w.s)
		var lh := 12.0 * 1.4
		for k in lines.size():
			w.text_at(self, lines[k], 195.0, desc_y + lh * (k + 0.5), "Nunito", 700, 12, Color(C_CHIP), 0.5)
		# Hinweis über dem großen Knopf
		var h := w.hint()
		if h != "":
			w.text_at(self, h, 195.0, HINT_Y, "Nunito", 800, 12, Color("#ffb0a8"), 0.5)

	## Abgerundeter Balken mit Farbverlauf von links nach rechts (über die volle Breite gerechnet)
	func _gradient_bar(r: Rect2, full_w: float, c0: Color, c1: Color) -> void:
		if r.size.y < 2.0 or r.size.x < r.size.y + 1.0:
			return
		var rad := r.size.y * 0.5
		var pts := PackedVector2Array()
		var cols := PackedColorArray()
		for k in 9:
			var ang := PI * 0.5 + PI * k / 8.0
			pts.append(Vector2(r.position.x + rad, r.position.y + rad) + Vector2(cos(ang), sin(ang)) * rad)
		for k in 9:
			var ang := -PI * 0.5 + PI * k / 8.0
			pts.append(Vector2(r.end.x - rad, r.position.y + rad) + Vector2(cos(ang), sin(ang)) * rad)
		for q in pts:
			cols.append(c0.lerp(c1, clampf((q.x - r.position.x) / maxf(1.0, full_w), 0.0, 1.0)))
		draw_polygon(pts, cols)

	func _wrap(txt: String, f: Font, fs: int, max_w: float) -> PackedStringArray:
		var out := PackedStringArray()
		var cur := ""
		for word in txt.split(" "):
			var t := word if cur == "" else cur + " " + word
			if cur != "" and f.get_string_size(t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > max_w:
				out.append(cur)
				cur = word
			else:
				cur = t
		if cur != "":
			out.append(cur)
		return out


class BigContent:
	extends Control
	## Inhalt des großen Knopfs: [Hammer] TEXT [Münze Preis] [Stern Anzahl], mittig wie im Mockup
	var win: BuildingWindow
	var _hammer: TextureRect
	var _coin: TextureRect
	var _star: TextureRect
	var _a := {}

	func _ready() -> void:
		_hammer = _img(null)
		_coin = _img(load("res://ui/icons/gold.webp"))
		var mat := ShaderMaterial.new()
		mat.shader = load("res://shaders/glanz.gdshader")
		_coin.material = mat
		_star = _img(load("res://ui/icons/stars.webp"))
		var lay: Dictionary = MockView.layout_of("bauplatz").get("states", {}).get("main", {})
		for l in lay.get("live", []):
			if str(l["id"]) == "hammer":
				_hammer.texture = load("res://ui_mock/bauplatz/" + str(l["img"]))
		resized.connect(refresh)
		refresh()

	func _img(t: Texture2D) -> TextureRect:
		var tr := TextureRect.new()
		tr.texture = t
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(tr)
		return tr

	func refresh() -> void:
		if win == null or _coin == null:
			return
		_a = win.action()
		queue_redraw()

	## Teile in Mockup-Punkten: [art, breite]
	func _parts() -> Array:
		var p := []
		if bool(_a.get("hammer", false)):
			p.append(["hammer", 22.0])
		p.append(["text", win.text_w(str(_a.get("text", "")), "Fredoka", 700, 22)])
		if int(_a.get("gold", -1)) >= 0:
			var w := 4.0 + 18.0 + 3.0 + win.text_w(MockScreen.num(int(_a["gold"])), "Fredoka", 700, 16) + 8.0
			if int(_a.get("stars", 0)) > 0:
				w += 6.0 + 18.0 + 3.0 + win.text_w(str(int(_a["stars"])), "Fredoka", 700, 16)
			p.append(["pill", w])
		return p

	func _draw() -> void:
		if win == null or _a.is_empty():
			return
		var s := win.s
		var parts := _parts()
		var total := 0.0
		for q in parts:
			total += float(q[1])
		total += 8.0 * (parts.size() - 1)
		var bw := size.x / s
		var mid := size.y / s * 0.5
		var x := (bw - total) * 0.5
		_hammer.visible = false
		_coin.visible = false
		_star.visible = false
		for q in parts:
			match str(q[0]):
				"hammer":
					_hammer.visible = true
					_hammer.position = Vector2(x, mid - 11.0) * s
					_hammer.size = Vector2(22, 22) * s
				"text":
					win.text_at(self, str(_a["text"]), x, mid, "Fredoka", 700, 22, Color(C_BTN))
				"pill":
					win.rounded(self, Rect2(x, mid - 12.0, float(q[1]), 24.0), Color(74 / 255.0, 32 / 255.0, 0, 0.2), 10)
					var px := x + 4.0
					_coin.visible = true
					_coin.position = Vector2(px, mid - 9.0) * s
					_coin.size = Vector2(18, 18) * s
					px += 21.0
					var short := Save.gold() < int(_a["gold"]) and bool(_a.get("enabled", false))
					px += win.text_at(self, MockScreen.num(int(_a["gold"])), px, mid, "Fredoka", 700, 16, Color(C_SHORT) if short else Color(C_BTN))
					if int(_a.get("stars", 0)) > 0:
						px += 6.0
						_star.visible = true
						_star.position = Vector2(px, mid - 9.0) * s
						_star.size = Vector2(18, 18) * s
						px += 21.0
						var short_s := Save.stars() < int(_a["stars"]) and bool(_a.get("enabled", false))
						win.text_at(self, str(int(_a["stars"])), px, mid, "Fredoka", 700, 16, Color(C_SHORT) if short_s else Color(C_BTN))
			x += float(q[1]) + 8.0
