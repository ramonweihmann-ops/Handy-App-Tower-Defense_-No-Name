class_name UpgradesTab
extends MockScreen
## Reiter „Upgrades“ nach den freigegebenen Entwürfen „Upgrades · Tech-Werft (neu)“ und
## „Upgrades · Talente (neu)“ (Vorlage_Raw/Tech_Werft_v1, Vorlage_Raw/Talente_v1).
## Hintergrund, Kopfleiste, Umschalter TECH-WERFT / TALENTE, Ziehknöpfe und Reiterleiste kommen aus
## dem Export (ui_mock/upgrades_tech_neu, ui_mock/upgrades_talente_neu); was sich ändert, zeichnet
## dieser Reiter aus den gelieferten Bauteilen (ui/upgrades_v2).
##
## Tech-Werft: drei Bereiche (Angriff, Schutz, Technik), je ein Grundmodul und zwei Äste, die
## parallel ausbaubar sind (MetaData.TECH). Antippen wählt ein Modul, die Detailbox zeigt es mit
## AUSBAUEN. Munition (dauerhafte Stufen für Plasma und Energiekern) öffnet sich über einen Knopf
## unter dem Umschalter.
##
## Talente: Raster mit entdeckten Talenten und „?“-Feldern, darunter „Neues Talent erhalten“.

const TECH_TOP := {"level": "12", "energy": "25/30", "gold": "4.573", "gems": "350"}
const TALENT_TOP := {"level": "12", "stars": "3", "gold": "4.573", "gems": "350"}
const PARTS := "res://ui/upgrades_v2/"
## Maßstab der Vorlage (978 breit) auf Mockup-Punkte
const K := 390.0 / 978.0

## Talente: Karten 198 × 204 (Vorlage), Spalten im Abstand 210, Zeilen 101 Punkte
const CARD := Vector2(198.0 * K, 204.0 * K)
const CELL := CARD
const GRID_X := 76.0 * K
const GRID_COL := 210.0 * K
const GRID_Y := 66.0
const GRID_ROW := 101.0
const GRID_COLS := 4
const GRID_CELLS := 16
const GRID_RECT := Rect2(0, 60, 390, 396)
## Symbole der Talente: aus dem Entwurf, sonst die bisherigen (mit eingezeichnetem Plus)
const TALENT_ICON := {"schnelllader": "icon_core", "sanitaet": "booster_medipack"}

## Tech-Werft (Mockup-Punkte)
const TECH_RECT := Rect2(0, 56, 390, 562)
const MOD := Vector2(102, 89)
const ROOT := Vector2(195, 410)
const BRANCH_POS := {"links": [Vector2(105, 322), Vector2(105, 226)], "rechts": [Vector2(285, 322), Vector2(285, 226)]}
const BRANCH_LABEL_X := {"links": 107.0, "rechts": 284.0}
const AREA_TABS := {"angriff": Rect2(22, 106, 96, 28), "schutz": Rect2(141, 106, 110, 28), "technik": Rect2(262, 106, 106, 28)}
const AREA_ICON := {"angriff": "ziel.svg", "schutz": "symbol_schild.webp", "technik": "zahnrad.svg"}
const TITLE := Rect2(90, 62, 210, 33)
const DETAIL := Rect2(26, 474, 338, 122)
const BUILD := Rect2(93, 546, 204, 42)
const TECH_ICON := {"crit": "tech_crit", "crit2": "tech_crit", "damage": "tech_damage", "xp": "tech_xp", "xp2": "tech_xp", "gold": "tech_gold"}
const AMMO_BUTTON := Rect2(57, 674, 134, 34)
const BOOSTER_BUTTON := Rect2(199, 674, 134, 34)

var talents := false
var area := "schutz"
var selected := ""
var _tex := {}
var _tech: TechLayer
var _grid: TalentGrid
var _ammo: AmmoPanel
var _talent_pop: TalentPop
var _ammo_btn: AmmoButton
var _booster_btn: AmmoButton
var _booster: BoosterPanel


static func _is_talents(m: MainMenu) -> bool:
	return str(m.sub_tab.get("upgrades", "tech")) == "talente"


func _init(m: MainMenu) -> void:
	super("upgrades_talente_neu" if _is_talents(m) else "upgrades_tech_neu", m, TALENT_TOP if _is_talents(m) else TECH_TOP)
	talents = _is_talents(m)


func _ready() -> void:
	super()
	BaseTab.copy_nav_badges(self)
	if talents:
		_grid = TalentGrid.new()
		_grid.tab = self
		place_at(_grid, GRID_RECT)
	else:
		area = str(menu.sub_tab.get("tech_area", ""))
		if not area in MetaData.TECH_AREAS:
			area = _default_area()
		selected = _default_selection(area)
		_tech = TechLayer.new()
		_tech.tab = self
		place_at(_tech, TECH_RECT)
		_ammo_btn = AmmoButton.new()
		_ammo_btn.tab = self
		place_at(_ammo_btn, AMMO_BUTTON, true)
		_booster_btn = AmmoButton.new()
		_booster_btn.tab = self
		_booster_btn.kind = "booster"
		place_at(_booster_btn, BOOSTER_BUTTON, true)
		if str(menu.sub_tab.get("upgrades", "")) == "munition":
			open_ammo()
		elif str(menu.sub_tab.get("upgrades", "")) == "booster":
			open_booster()
	bind()


# --- gemeinsame Werte ------------------------------------------------------------------

func bind() -> void:
	var tech := button("Upgrades-Tech-Neu.dc.html")
	var tal := button("Upgrades-Talente-Neu.dc.html")
	if tech and tal:
		tech.badge = talents and (Save.can_buy_tech() or Save.any_ammo_upgrade() or Save.any_booster_upgrade())
		tal.badge = not talents and Save.can_draw_talent()
	if talents:
		var one := button("draw_star")
		if one:
			one.modulate.a = 1.0 if Save.can_draw_talent() else 0.6
		var five := button("draw_five")
		if five:
			five.modulate.a = 1.0 if Save.stars() >= 5 and Save.can_draw_talent() else 0.6
		if _grid:
			_grid.queue_redraw()
	elif _tech:
		_tech.queue_redraw()
	if _ammo_btn:
		_ammo_btn.queue_redraw()
	if _booster_btn:
		_booster_btn.queue_redraw()
	if is_instance_valid(_ammo):
		_ammo.redraw()
	if is_instance_valid(_booster):
		_booster.redraw()


func handle(b: Dictionary) -> bool:
	var on := str(b.get("on", ""))
	var href := str(b.get("href", ""))
	var label := str(b.get("label", ""))
	if href in ["Upgrades-Tech-Neu.dc.html", "Upgrades-Talente-Neu.dc.html"]:
		var want := href == "Upgrades-Talente-Neu.dc.html"
		if want != talents:
			menu.sub_tab["upgrades"] = "talente" if want else "tech"
			menu.show_tab("upgrades")
		return true
	match on:
		"draw_star":
			_draw_talents(1)
			return true
		"draw_five":
			_draw_talents(5)
			return true
		"draw_ad":
			menu.info("Talent für Werbung", "In der Testphase gibt es keine Werbung. Talente gibt es hier für Sterne – Sterne bekommst du für gewonnene Level.")
			return true
	if label == "Sterne kaufen":
		menu.toast("Sterne gibt es für gewonnene Level.")
		return true
	return false


# --- Bauteile und Texte ----------------------------------------------------------------

func part(file: String) -> Texture2D:
	if not "." in file:
		file += ".webp"
	if not _tex.has(file):
		_tex[file] = load(file if file.begins_with("res://") else PARTS + file)
	return _tex[file]


## Bauteil gestreckt in r zeichnen (wie im Entwurf); origin = Mockup-Punkt bei (0,0) des CanvasItem
func pic(ci: CanvasItem, file: String, r: Rect2, origin: Vector2, mod := Color.WHITE) -> void:
	var t := part(file)
	if t:
		ci.draw_texture_rect(t, Rect2((r.position - origin) * s, r.size * s), false, mod)


## Bauteil mit Seitenverhältnis in ein Quadrat der Kantenlänge box um c
func pic_fit(ci: CanvasItem, file: String, c: Vector2, box: float, origin: Vector2, mod := Color.WHITE) -> void:
	var t := part(file)
	if t == null:
		return
	var ts := t.get_size()
	var k := box / maxf(ts.x, ts.y)
	var sz := ts * k
	ci.draw_texture_rect(t, Rect2((c - sz * 0.5 - origin) * s, sz * s), false, mod)


## Pillenförmiger Knopf: Enden behalten ihre Form, die Mitte dehnt sich
func pill(ci: CanvasItem, file: String, r: Rect2, origin: Vector2, mod := Color.WHITE) -> void:
	var t := part(file)
	if t == null:
		return
	var ts := t.get_size()
	var cap_src := minf(ts.y * 0.5, ts.x * 0.5)
	var dst := Rect2((r.position - origin) * s, r.size * s)
	var cap_dst := minf(dst.size.y * 0.5, dst.size.x * 0.5)
	ci.draw_texture_rect_region(t, Rect2(dst.position, Vector2(cap_dst, dst.size.y)), Rect2(0, 0, cap_src, ts.y), mod)
	ci.draw_texture_rect_region(t, Rect2(dst.position + Vector2(cap_dst, 0), Vector2(dst.size.x - 2.0 * cap_dst, dst.size.y)), Rect2(cap_src, 0, ts.x - 2.0 * cap_src, ts.y), mod)
	ci.draw_texture_rect_region(t, Rect2(dst.end.x - cap_dst, dst.position.y, cap_dst, dst.size.y), Rect2(ts.x - cap_src, 0, cap_src, ts.y), mod)


## Text wie ein HTML-Block im Entwurf: links oben bei (x, top), Breite w, align -1/0/1
func text_box(ci: CanvasItem, txt: String, x: float, top: float, w: float, origin: Vector2, family: String, weight: int, size_pt: float, col: Color, align := 0, shadow := Color(0, 0, 0, 0), shadow_off := Vector2.ZERO) -> void:
	var cy := top + size_pt * (0.605 if family == "Fredoka" else 0.682)
	var ax := x + w * 0.5
	if align < 0:
		ax = x
	elif align > 0:
		ax = x + w
	label_at(ci, txt, (Vector2(ax, cy) - origin) * s, family, weight, size_pt, col, align, shadow, shadow_off)


## Größte Schrift (höchstens size_pt), mit der txt in w passt
func fit_size(txt: String, family: String, weight: int, size_pt: float, w: float, min_pt := 7.0) -> float:
	while size_pt > min_pt and text_width(txt, family, weight, size_pt) > w:
		size_pt -= 0.5
	return size_pt


func draw_dot(ci: CanvasItem, p: Vector2) -> void:
	ci.draw_circle(p, 6.0 * s, Color.WHITE)
	ci.draw_circle(p, 4.5 * s, Color(1.0, 0.23, 0.19))


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


# --- Tech-Werft --------------------------------------------------------------------------

func _default_area() -> String:
	for a in MetaData.TECH_AREAS:
		for t in MetaData.tech_in_area(a):
			if Save.can_buy_tech_id(str(t["id"])):
				return a
	return "schutz"


## Erstes offenes Modul des Bereichs (günstigstes), sonst das zuletzt erforschte
func _default_selection(a: String) -> String:
	var mods := MetaData.tech_in_area(a)
	for t in mods:
		if Save.tech_state(str(t["id"])) == "open":
			return str(t["id"])
	var last := str(mods[0]["id"])
	for t in mods:
		if Save.has_tech(str(t["id"])):
			last = str(t["id"])
	return last


func set_area(a: String) -> void:
	if a == area:
		return
	area = a
	menu.sub_tab["tech_area"] = a
	selected = _default_selection(a)
	if _tech:
		_tech.queue_redraw()


func select(id: String) -> void:
	selected = id
	if _tech:
		_tech.queue_redraw()


## Mitte eines Moduls: Grundmodul unten, Äste von unten nach oben
func module_pos(id: String) -> Vector2:
	var t := MetaData.tech(id)
	var br := str(t.get("branch", ""))
	if br == "":
		return ROOT
	var k := 0
	for o in MetaData.tech_in_area(str(t["area"])):
		if str(o["id"]) == id:
			break
		if str(o["branch"]) == br:
			k += 1
	var list: Array = BRANCH_POS[br]
	return list[mini(k, list.size() - 1)]


func buy_selected() -> void:
	var t := MetaData.tech(selected)
	if t.is_empty():
		return
	match Save.tech_state(selected):
		"done":
			menu.toast("%s ist schon erforscht." % t["title"])
			return
		"lock":
			menu.toast("Erst %s erforschen." % MetaData.tech(str(t["needs"]))["title"])
			return
	if not Save.buy_tech(selected):
		menu.toast("Nicht genug Gold.")
		return
	Sfx.play("levelup")
	menu.celebrate("check", "%s erforscht!" % t["title"], Color(0.45, 1.0, 0.55))
	selected = _default_selection(area)
	refresh()


func open_ammo() -> void:
	if is_instance_valid(_ammo):
		return
	_ammo = AmmoPanel.new()
	_ammo.tab = self
	add_child(_ammo)


func open_booster() -> void:
	if is_instance_valid(_booster):
		return
	_booster = BoosterPanel.new()
	_booster.tab = self
	add_child(_booster)


func close_booster() -> void:
	if is_instance_valid(_booster):
		_booster.queue_free()
	_booster = null
	if str(menu.sub_tab.get("upgrades", "")) == "booster":
		menu.sub_tab["upgrades"] = "tech"


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
	return Rect2(GRID_X + col * GRID_COL, GRID_Y + row * GRID_ROW, CARD.x, CARD.y)


## Talentkarte zeichnen: r = Lage der Karte (Mockup-Punkte), origin wie bei pic
func draw_card(ci: CanvasItem, id: String, level: int, r: Rect2, origin: Vector2) -> void:
	var k := r.size.x / CARD.x
	var p := r.position
	pic(ci, "talent_freigeschaltet", r, origin)
	pic(ci, "talent_kopfbereich", Rect2(p + Vector2(2, 2) * k, Vector2(CARD.x - 4.0, 20.0) * k), origin)
	var title := str(MetaData.TALENTS[id]["title"])
	var fs := fit_size(title, "Fredoka", 700, 10.5 * k, (CARD.x - 6.0) * k)
	text_box(ci, title, p.x, p.y + 5.0 * k + (10.5 * k - fs) * 0.6, r.size.x, origin, "Fredoka", 700, fs, Color.WHITE, 0, Color("#1d6b2a"), Vector2(0, 1) * k)
	var icon := str(TALENT_ICON.get(id, "tal_" + id))
	pic_fit(ci, icon, p + Vector2(CARD.x * 0.5, 44.0) * k, 44.0 * k, origin)
	if TALENT_ICON.has(id):
		text_box(ci, "+", p.x + (CARD.x - 24.0) * k, p.y + 20.0 * k, 14.0 * k, origin, "Nunito", 800, 15.0 * k, Color.WHITE, 0, Color("#1d6b2a"), Vector2(0, 1) * k)
	text_box(ci, "Stufe %d" % level, p.x, p.y + (CARD.y - 17.0) * k, r.size.x, origin, "Fredoka", 700, 12.0 * k, Color("#163f12"))


func draw_unknown(ci: CanvasItem, r: Rect2, origin: Vector2) -> void:
	pic(ci, "talent_unbekannt", r, origin)
	text_box(ci, "?", r.position.x, r.position.y + CARD.y * 0.5 - 21.0, r.size.x, origin, "Fredoka", 700, 36.0, Color("#d6c8ff"), 0, Color("#3d2a8a"), Vector2(0, 3))


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

## Die Tech-Werft: Titel, Bereiche, Äste, Verbindungen, Module und Detailbox
class TechLayer:
	extends Control
	var tab: UpgradesTab

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_STOP
		# Bilder vorab laden: beim allerersten Zeichnen wären sie sonst kurz weiß
		for f in ["kopf_leiste", "bereich_angriff", "bereich_schutz", "bereich_technik", "ziel.svg", "zahnrad.svg", "symbol_schild",
				"symbol_regeneration", "symbol_schloss", "modul_normal", "modul_ausgewaehlt", "modul_gesperrt", "marke_gold", "haekchen",
				"detail_box", "knopf_gruen_normal", "knopf_gesperrt", "tech_crit", "tech_damage", "tech_xp", "tech_gold", "res://ui/icons/gold.webp"]:
			tab.part(f)
		await get_tree().process_frame
		queue_redraw()

	func _draw() -> void:
		var o := TECH_RECT.position
		var s := tab.s
		# Titel
		tab.pic(self, "kopf_leiste", TITLE, o)
		var title: String = MetaData.TECH_AREA_TITLES[tab.area]
		var tw := tab.text_width(title, "Fredoka", 700, 22.0)
		var x0 := 195.0 - (25.0 + 3.0 + tw) * 0.5
		tab.pic_fit(self, AREA_ICON[tab.area], Vector2(x0 + 12.5, 78.5), 26.0, o)
		tab.text_box(self, title, x0 + 28.0, 66.0, tw, o, "Fredoka", 700, 22.0, Color.WHITE, -1, Color("#3a1a80"), Vector2(0, 2))
		# Bereiche
		for a in MetaData.TECH_AREAS:
			var r: Rect2 = AREA_TABS[a]
			tab.pic(self, "bereich_" + a, r, o)
			if a == "schutz":
				tab.pic(self, "symbol_schild", Rect2(r.position + Vector2(10, 5), Vector2(16, 18)), o)
			else:
				tab.pic(self, AREA_ICON[a], Rect2(r.position + Vector2(10, 7), Vector2(15, 15)), o)
			tab.text_box(self, MetaData.TECH_AREA_TITLES[a], r.position.x + 30.0, r.position.y + 6.0, r.size.x - 34.0, o, "Fredoka", 700, 13.0, Color.WHITE, -1, Color(0, 0, 0, 0.3), Vector2(0, 1))
			if a != tab.area and _area_ready(a):
				tab.draw_dot(self, (r.position + Vector2(r.size.x - 6.0, 2.0) - o) * s)
		# Äste
		var names: Array = MetaData.TECH_BRANCHES[tab.area]
		for j in 2:
			var cx: float = BRANCH_LABEL_X["links" if j == 0 else "rechts"]
			var sb := StyleBoxFlat.new()
			sb.bg_color = Color(20 / 255.0, 30 / 255.0, 80 / 255.0, 0.75)
			sb.border_color = Color(120 / 255.0, 180 / 255.0, 1.0, 0.6)
			sb.set_border_width_all(maxi(1, roundi(1.5 * s)))
			sb.set_corner_radius_all(roundi(12 * s))
			draw_style_box(sb, Rect2((Vector2(cx - 56.0, 148.0) - o) * s, Vector2(112, 24) * s))
			tab.text_box(self, str(names[j]), cx - 56.0, 151.0, 112.0, o, "Fredoka", 700, 13.0, Color("#e8f2ff"))
		# Verbindungen hinter den Modulen
		var mods := MetaData.tech_in_area(tab.area)
		for t in mods:
			var need := str(t["needs"])
			if need == "":
				continue
			var a := tab.module_pos(need)
			var b := tab.module_pos(str(t["id"]))
			var pts := PackedVector2Array()
			if is_equal_approx(a.x, b.x):
				pts.append((a - o) * s)
				pts.append((b - o) * s)
			else:
				var c1 := Vector2(a.x + signf(b.x - a.x) * 60.0, a.y)
				var c2 := Vector2(b.x, b.y + 50.0)
				for k in 25:
					var u := k / 24.0
					var q := a.lerp(c1, u).lerp(c1.lerp(c2, u), u).lerp(c1.lerp(c2, u).lerp(c2.lerp(b, u), u), u)
					pts.append((q - o) * s)
			draw_polyline(pts, Color("#5a4aa8"), 8.0 * s, true)
			draw_polyline(pts, Color("#a8dcff"), 4.5 * s, true)
		# Module
		for t in mods:
			_module(t, o)
		_detail(o)

	func _area_ready(a: String) -> bool:
		for t in MetaData.tech_in_area(a):
			if Save.can_buy_tech_id(str(t["id"])):
				return true
		return false

	## Symbol eines Moduls in seinem Feld (Mitte c, Feldgröße box)
	func _symbol(t: Dictionary, c: Vector2, o: Vector2, box: float, alpha: float, numeral_pt: float) -> void:
		var id := str(t["id"])
		var col := Color(1, 1, 1, alpha)
		if id.begins_with("shield"):
			var sz := Vector2(44, 49) * (box / 44.0)
			tab.pic(self, "symbol_schild", Rect2(c - sz * 0.5, sz), o, col)
			tab.text_box(self, str(t["num"]), c.x - sz.x * 0.5, c.y - sz.y * 0.5 + 10.0 * box / 44.0, sz.x, o, "Fredoka", 700, numeral_pt, Color(1, 1, 1, alpha), 0, Color(42 / 255.0, 74 / 255.0, 154 / 255.0, alpha), Vector2(0, 1))
		elif id == "heal":
			tab.pic(self, "symbol_regeneration", Rect2(c - Vector2(25, 25) * box / 44.0, Vector2(50, 50) * box / 44.0), o, col)
		else:
			tab.pic_fit(self, TECH_ICON.get(id, "tech_crit"), c, box * 1.02, o, col)

	func _module(t: Dictionary, o: Vector2) -> void:
		var id := str(t["id"])
		var st := Save.tech_state(id)
		var c := tab.module_pos(id)
		var r := Rect2(c - MOD * 0.5, MOD)
		var key := "modul_ausgewaehlt" if id == tab.selected else ("modul_gesperrt" if st == "lock" else "modul_normal")
		tab.pic(self, key, r, o)
		_symbol(t, r.position + Vector2(MOD.x * 0.5, 34.5), o, 44.0, 0.6 if st == "lock" else 1.0, 19.0)
		if st == "lock":
			tab.pic(self, "symbol_schloss", Rect2(r.position + Vector2(MOD.x - 27.0, 24.0), Vector2(24, 24)), o)
		if id == tab.selected:
			var m := Rect2(r.position + Vector2(MOD.x - 22.0, -6.0), Vector2(24, 24))
			tab.pic(self, "marke_gold", m, o)
			var n := str(MetaData.TECH.find(t) + 1)
			tab.text_box(self, n, m.position.x, m.position.y + 3.0, 24.0, o, "Fredoka", 700, 13.0, Color("#4a2000"))
		if st == "done":
			tab.pic(self, "haekchen", Rect2(r.position + Vector2(MOD.x - 32.0, MOD.y - 38.0), Vector2(26, 26)), o)
		elif st == "open" and id != tab.selected and Save.can_buy_tech_id(id):
			tab.draw_dot(self, (r.position + Vector2(MOD.x - 10.0, 6.0) - o) * tab.s)

	func _detail(o: Vector2) -> void:
		var t := MetaData.tech(tab.selected)
		if t.is_empty():
			return
		var s := tab.s
		var d := DETAIL
		tab.pic(self, "detail_box", d, o)
		var st := Save.tech_state(tab.selected)
		_symbol(t, d.position + Vector2(41, 42), o, 50.0, 1.0, 20.0)
		var sep := StyleBoxFlat.new()
		sep.bg_color = Color(220 / 255.0, 210 / 255.0, 1.0, 0.5)
		sep.set_corner_radius_all(maxi(1, roundi(1 * s)))
		draw_style_box(sep, Rect2((d.position + Vector2(78, 14) - o) * s, Vector2(2, 52) * s))
		var title := str(t["title"])
		tab.text_box(self, title, d.position.x + 90.0, d.position.y + 12.0, 230.0, o, "Fredoka", 700, tab.fit_size(title, "Fredoka", 700, 17.0, 236.0), Color.WHITE, -1)
		var line2 := "Andere Forschungswege bleiben verfügbar"
		if st == "done":
			line2 = "Erforscht – gilt in jedem Kampf"
		elif st == "lock":
			line2 = "Erst %s erforschen" % MetaData.tech(str(t["needs"]))["title"]
		for j in 2:
			var line := str(t["desc"]) if j == 0 else line2
			tab.text_box(self, line, d.position.x + 90.0, d.position.y + 34.0 + 16.0 * j, 240.0, o, "Nunito", 700, tab.fit_size(line, "Nunito", 700, 11.5, 240.0), Color("#e8e2ff"), -1)
		# Knopf
		if st == "open":
			var cost := int(t["cost"])
			var can := Save.gold() >= cost
			tab.pill(self, "knopf_gruen_normal", BUILD, o, Color(1, 1, 1, 1.0 if can else 0.6))
			var price := MockScreen.num(cost)
			var w1 := tab.text_width("AUSBAUEN", "Fredoka", 700, 18.0)
			var w2 := tab.text_width(price, "Fredoka", 700, 16.0)
			var total := w1 + 10.0 + 18.0 + 4.0 + w2
			var x := BUILD.get_center().x - total * 0.5
			var cy := BUILD.get_center().y
			var ink := Color(15 / 255.0, 61 / 255.0, 18 / 255.0, 1.0 if can else 0.65)
			tab.label_at(self, "AUSBAUEN", (Vector2(x, cy) - o) * s, "Fredoka", 700, 18.0, ink, -1)
			var coin := tab.part("res://ui/icons/gold.webp")
			draw_texture_rect(coin, Rect2((Vector2(x + w1 + 10.0, cy - 9.0) - o) * s, Vector2(18, 18) * s), false, Color(1, 1, 1, 1.0 if can else 0.65))
			tab.label_at(self, price, (Vector2(x + w1 + 32.0, cy) - o) * s, "Fredoka", 700, 16.0, ink, -1)
		else:
			tab.pill(self, "knopf_gesperrt", BUILD, o)
			var label := "ERFORSCHT" if st == "done" else "GESPERRT"
			var lw := tab.text_width(label, "Fredoka", 700, 18.0)
			var icon_w := 22.0
			var x := BUILD.get_center().x - (icon_w + 6.0 + lw) * 0.5
			var cy := BUILD.get_center().y
			tab.pic(self, "haekchen" if st == "done" else "symbol_schloss", Rect2(Vector2(x, cy - icon_w * 0.5), Vector2(icon_w, icon_w)), o)
			tab.label_at(self, label, (Vector2(x + icon_w + 6.0, cy) - o) * s, "Fredoka", 700, 18.0, Color("#d6d0f5"), -1)

	func _gui_input(e: InputEvent) -> void:
		if not (e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT):
			return
		accept_event()
		var p: Vector2 = e.position / tab.s + TECH_RECT.position
		for a in MetaData.TECH_AREAS:
			if (AREA_TABS[a] as Rect2).grow(4.0).has_point(p):
				Sfx.play("click")
				tab.set_area(a)
				return
		for t in MetaData.tech_in_area(tab.area):
			var c := tab.module_pos(str(t["id"]))
			if Rect2(c - MOD * 0.5, MOD).has_point(p):
				Sfx.play("click")
				tab.select(str(t["id"]))
				return
		if BUILD.grow(4.0).has_point(p):
			Sfx.play("click")
			tab.buy_selected()


## Knopf „MUNITION“ unter dem Umschalter (im Stil des aktiven Umschalters)
class AmmoButton:
	extends Control
	var tab: UpgradesTab
	var kind := "munition"   # oder "booster"

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_STOP
		pivot_offset = size * 0.5
		tab.part("knopf_violett_normal")
		await get_tree().process_frame
		queue_redraw()

	func _process(_d: float) -> void:
		pivot_offset = size * 0.5

	func _draw() -> void:
		var s := tab.s
		var r := BOOSTER_BUTTON if kind == "booster" else AMMO_BUTTON
		tab.pill(self, "knopf_violett_normal", r, r.position)
		tab.label_at(self, "BOOSTER" if kind == "booster" else "MUNITION", size * 0.5, "Fredoka", 700, 15.0, Color.WHITE, 0, Color("#4a1a90"), Vector2(0, 1))
		if Save.any_booster_upgrade() if kind == "booster" else Save.any_ammo_upgrade():
			tab.draw_dot(self, Vector2(size.x - 4.0 * s, 2.0 * s))

	func _gui_input(e: InputEvent) -> void:
		if e is InputEventMouseButton and e.button_index == MOUSE_BUTTON_LEFT:
			if e.pressed:
				scale = Vector2.ONE * 0.93
			else:
				scale = Vector2.ONE
				if Rect2(Vector2.ZERO, size).has_point(e.position):
					Sfx.play("click")
					if kind == "booster":
						tab.open_booster()
					else:
						tab.open_ammo()
			accept_event()


## Fenster „Munition“ nach dem freigegebenen Mockup „Upgrades · Munition“ (Entwurf Vorlage_Raw/Munition_Fenster_v1):
## sechs unabhängige Module im 2×3-Raster. Rahmen, Symbole, Titel und Beschreibungen kommen aus dem Export
## ui_mock/munition (mit der weich auslaufenden Abdunklung dahinter); Stufe, Segmente und der Knopf je nach
## Spielstand zeichnet das Spiel: kaufbar (grün, Preis), zu teuer (grau, Preis rot), voll ausgebaut (MAX, gold).
class AmmoPanel:
	extends MockView
	const DIALOG := Rect2(13, 80, 364, 655)
	const CELL := Vector2(168, 185)
	var tab: UpgradesTab
	var _layer: Control
	var _coin: Texture2D

	func _init() -> void:
		super("munition")

	func _ready() -> void:
		super()
		_fill.visible = false
		_coin = load("res://ui/icons/gold.webp")
		_layer = Control.new()
		_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_layer.draw.connect(_draw_layer)
		place_at(_layer, Rect2(0, 0, W, H), true)
		button_pressed.connect(func(b: Dictionary) -> void:
			if str(b.get("label", "")) == "Schließen":
				Sfx.play("click")
				tab.close_ammo())
		modulate.a = 0.0
		create_tween().tween_property(self, "modulate:a", 1.0, 0.15)

	func redraw() -> void:
		if is_instance_valid(_layer):
			_layer.queue_redraw()

	static func cell(k: int) -> Rect2:
		return Rect2(Vector2(23 + (k % 2) * 176, 151 + (k / 2) * 191), CELL)

	static func button_rect(k: int) -> Rect2:
		var c := cell(k)
		return Rect2(c.position + Vector2(26, 149), Vector2(CELL.x - 52, 28))

	func _box(r: Rect2, fill: Color, radius: float, shadow := Color(0, 0, 0, 0), sh_y := 0.0) -> void:
		var sb := StyleBoxFlat.new()
		sb.bg_color = fill
		sb.set_corner_radius_all(roundi(radius * s))
		if shadow.a > 0.0:
			sb.shadow_color = shadow
			sb.shadow_offset = Vector2(0, sh_y * s)
			sb.shadow_size = 0
		sb.anti_aliasing = true
		_layer.draw_style_box(sb, Rect2(r.position * s, r.size * s))

	func _text(t: String, cx: float, mid_y: float, fam: String, weight: int, px: float, col: Color, align := 0.5) -> float:
		var f := MockFonts.font(fam, weight)
		var fs := maxi(1, roundi(px * s))
		var w := f.get_string_size(t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var base := mid_y * s + (f.get_ascent(fs) - f.get_descent(fs)) * 0.5
		_layer.draw_string(f, Vector2(cx * s - w * align, base), t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
		return w / s

	func _draw_layer() -> void:
		for k in MetaData.AMMO_UPGRADES.size():
			_module(k)

	func _module(k: int) -> void:
		var u: Dictionary = MetaData.AMMO_UPGRADES[k]
		var id := str(u["id"])
		var lvl := Save.ammo_level(id)
		var mx := int(u["max"])
		var c := cell(k)
		var cx := c.get_center().x
		var full := lvl >= mx
		_text("Stufe %d/%d" % [lvl, mx], cx, c.position.y + 124.0, "Fredoka", 700, 13.0, Color("#ffd56a"))
		# Segmente: so viele wie Stufen, gefüllt bis zur erreichten Stufe (gold, wenn voll)
		var seg := Vector2(11, 10)
		var gap := 3.0
		var x0 := cx - (mx * seg.x + (mx - 1) * gap) * 0.5
		for i in mx:
			var r := Rect2(Vector2(x0 + i * (seg.x + gap), c.position.y + 134.0), seg)
			if i < lvl:
				var col := Color("#f0b53a") if full else Color("#52e7ff")
				var hi := Color("#ffe58a") if full else Color("#9ef4ff")
				_box(r.grow(1.5), Color(col.r, col.g, col.b, 0.25), 4.5)
				_box(r, col, 3)
				_box(Rect2(r.position, Vector2(r.size.x, r.size.y * 0.5)), hi, 3)
			else:
				_box(r, Color("#514266"), 3)
		var b := button_rect(k)
		if full:
			_box(b, Color("#d99b31"), 14, Color("#8a5a10"), 3)
			_box(Rect2(b.position, Vector2(b.size.x, b.size.y * 0.55)), Color("#ffe58a"), 14)
			_text("MAX", cx, b.get_center().y + 0.5, "Fredoka", 700, 16.0, Color("#613a0a"))
			return
		var cost := MetaData.ammo_cost(u, lvl)
		var can := Save.gold() >= cost
		if can:
			_box(b, Color("#4bc62d"), 14, Color("#23802a"), 3)
			_box(Rect2(b.position, Vector2(b.size.x, b.size.y * 0.55)), Color("#8fe85c"), 14)
		else:
			_box(b, Color("#514d68"), 14, Color("#2e2b40"), 3)
			_box(Rect2(b.position, Vector2(b.size.x, b.size.y * 0.55)), Color("#6a6684"), 14)
		var price := MockScreen.num(cost)
		var pw := MockFonts.font("Fredoka", 700).get_string_size(price, HORIZONTAL_ALIGNMENT_LEFT, -1, maxi(1, roundi(16.0 * s))).x / s
		var left := cx - (18.0 + 6.0 + pw) * 0.5
		if _coin:
			_layer.draw_texture_rect(_coin, Rect2(Vector2(left, b.get_center().y - 9.0) * s, Vector2(18, 18) * s), false, Color(1, 1, 1, 1.0 if can else 0.8))
		_text(price, left + 24.0, b.get_center().y + 0.5, "Fredoka", 700, 16.0, Color("#14320e") if can else Color("#ff8a8a"), 0.0)

	func _gui_input(e: InputEvent) -> void:
		if not (e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT):
			return
		accept_event()
		var p: Vector2 = (e.position - off) / s
		if not DIALOG.has_point(p):
			Sfx.play("click")
			tab.close_ammo()
			return
		for k in MetaData.AMMO_UPGRADES.size():
			if button_rect(k).grow(6.0).has_point(p):
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
		for f in ["talent_freigeschaltet", "talent_kopfbereich", "talent_unbekannt", "icon_core", "booster_medipack"]:
			tab.part(f)
		for id in MetaData.TALENTS.keys():
			tab.part(str(TALENT_ICON.get(id, "tal_" + id)))
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


## Fenster „Booster“ nach dem freigegebenen Mockup „Upgrades · Booster“: alle fünf Booster mit Stufe,
## Verbessern (Gold + Booster-Teile) und Mitnehmen (zwei passen in einen Kampf), unten rechts der Vorrat
## an Booster-Teilen. Rahmen, Symbole und Texte kommen aus dem Export ui_mock/booster; Stufe, Segmente,
## Knöpfe, Haken und „IM KAMPF“ zeichnet das Spiel je nach Spielstand.
class BoosterPanel:
	extends MockView
	const DIALOG := Rect2(13, 80, 364, 655)
	const CELL := Vector2(168, 185)
	var tab: UpgradesTab
	var _layer: Control
	var _coin: Texture2D
	var _parts: Texture2D

	func _init() -> void:
		super("booster")

	func _ready() -> void:
		super()
		_fill.visible = false
		_coin = load("res://ui/icons/gold.webp")
		_parts = BoosterPanel.parts_icon(64)
		_layer = Control.new()
		_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_layer.draw.connect(_draw_layer)
		place_at(_layer, Rect2(0, 0, W, H), true)
		button_pressed.connect(func(b: Dictionary) -> void:
			if str(b.get("label", "")) == "Schließen":
				Sfx.play("click")
				tab.close_booster()
			elif str(b.get("href", "")) == "#zu-den-truhen":
				Sfx.play("click")
				tab.close_booster()
				tab.menu.sub_tab["shop"] = "truhen"
				tab.menu.show_tab("shop"))
		modulate.a = 0.0
		create_tween().tween_property(self, "modulate:a", 1.0, 0.15)
		redraw()

	## Symbol der Booster-Teile (Zahnrad mit Blitz, wie im Mockup)
	static func parts_icon(px: int) -> Texture2D:
		var svg := '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">' \
			+ '<path d="M32 6l5 7 8-2 2 8 8 3-3 8 5 6-6 6 2 8-8 2-3 8-8-2-5 6-5-6-8 2-2-8-8-3 3-8-5-6 6-6-2-8 8-2 3-8 8 2z" fill="#ff9a3d" stroke="#8a3a00" stroke-width="2.5" stroke-linejoin="round"/>' \
			+ '<circle cx="32" cy="32" r="14" fill="#ffd56a" stroke="#8a3a00" stroke-width="2.5"/><path d="M34 21l-9 13h7l-3 10 10-14h-7z" fill="#5a2ad0"/></svg>'
		var img := Image.new()
		if img.load_svg_from_string(svg, px / 64.0) != OK:
			return null
		return ImageTexture.create_from_image(img)

	func redraw() -> void:
		set_text("12", MockScreen.num(Save.booster_parts()))
		if is_instance_valid(_layer):
			_layer.queue_redraw()

	static func cell(k: int) -> Rect2:
		return Rect2(Vector2(23 + (k % 2) * 176, 151 + (k / 2) * 191), CELL)

	static func button_rect(k: int) -> Rect2:
		var c := cell(k)
		return Rect2(c.position + Vector2(10, 149), Vector2(CELL.x - 20, 28))

	static func toggle_rect(k: int) -> Rect2:
		var c := cell(k)
		return Rect2(c.position + Vector2(CELL.x - 34, 26), Vector2(28, 28))

	func _box(r: Rect2, fill: Color, radius: float, shadow := Color(0, 0, 0, 0), sh_y := 0.0, border := Color(0, 0, 0, 0), bw := 0.0) -> void:
		var sb := StyleBoxFlat.new()
		sb.bg_color = fill
		sb.set_corner_radius_all(roundi(radius * s))
		if shadow.a > 0.0:
			sb.shadow_color = shadow
			sb.shadow_offset = Vector2(0, sh_y * s)
			sb.shadow_size = 0
		if border.a > 0.0:
			sb.border_color = border
			sb.set_border_width_all(maxi(1, roundi(bw * s)))
		sb.anti_aliasing = true
		_layer.draw_style_box(sb, Rect2(r.position * s, r.size * s))

	func _text(t: String, cx: float, mid_y: float, fam: String, weight: int, px: float, col: Color, align := 0.5) -> float:
		var f := MockFonts.font(fam, weight)
		var fs := maxi(1, roundi(px * s))
		var w := f.get_string_size(t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var base := mid_y * s + (f.get_ascent(fs) - f.get_descent(fs)) * 0.5
		_layer.draw_string(f, Vector2(cx * s - w * align, base), t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
		return w / s

	func _text_w(t: String, px: float) -> float:
		return MockFonts.font("Fredoka", 700).get_string_size(t, HORIZONTAL_ALIGNMENT_LEFT, -1, maxi(1, roundi(px * s))).x / s

	func _draw_layer() -> void:
		var slots := Save.booster_slots()
		for k in MetaData.BOOSTER_ORDER.size():
			_booster(k, str(MetaData.BOOSTER_ORDER[k]), slots)

	func _booster(k: int, id: String, slots: Array[String]) -> void:
		var c := cell(k)
		var cx := c.get_center().x
		var open := Save.booster_unlocked(id)
		var eq := open and slots.has(id)
		var lvl := Save.booster_level(id)
		var mx := MetaData.BOOSTER_MAX
		var full := lvl >= mx
		if eq:
			# Goldrand und Schild „IM KAMPF“
			_box(Rect2(c.position, c.size), Color(0, 0, 0, 0), 14, Color(0, 0, 0, 0), 0, Color("#ffd56a"), 1.5)
			var chip := Rect2(c.position + Vector2(6, 30), Vector2(_text_w("IM KAMPF", 9.0) + 12, 14))
			_box(chip, Color("#2f8a3a"), 8, Color(0, 0, 0, 0), 0, Color("#b6ffcf"), 1.5)
			_text("IM KAMPF", chip.get_center().x, chip.get_center().y, "Nunito", 800, 9.0, Color.WHITE)
		if not open:
			# gesperrt: Symbol abgedunkelt, Knopf mit Schloss und „Ab Level N“
			_box(Rect2(c.position + Vector2(40, 22), Vector2(88, 66)), Color(0.17, 0.13, 0.31, 0.6), 12)
		_text("Stufe %d/%d" % [lvl, mx], cx, c.position.y + 124.0, "Fredoka", 700, 13.0, Color("#ffd56a"))
		var seg := Vector2(20, 10)
		var gap := 3.0
		var x0 := cx - (mx * seg.x + (mx - 1) * gap) * 0.5
		for i in mx:
			var r := Rect2(Vector2(x0 + i * (seg.x + gap), c.position.y + 134.0), seg)
			if i < lvl:
				var col := Color("#f0b53a") if full else Color("#52e7ff")
				var hi := Color("#ffe58a") if full else Color("#9ef4ff")
				_box(r.grow(1.5), Color(col.r, col.g, col.b, 0.25), 4.5)
				_box(r, col, 3)
				_box(Rect2(r.position, Vector2(r.size.x, r.size.y * 0.5)), hi, 3)
			else:
				_box(r, Color("#514266"), 3)
		var b := button_rect(k)
		if not open:
			_box(b, Color(0.08, 0.05, 0.19, 0.7), 14, Color(0, 0, 0, 0), 0, Color("#6c5298"), 1.5)
			_text("Ab Level %d" % (int(MetaData.BOOSTERS[id]["unlock"]) + 1), cx, b.get_center().y + 0.5, "Fredoka", 700, 14.0, Color("#ddd6f3"))
			return
		# Mitnehmen: grüner Haken (dabei) oder gestrichelter Kreis mit „+“
		var t := toggle_rect(k)
		if eq:
			_box(t, Color("#4bc62d"), 14, Color("#23802a"), 2, Color("#eaffd8"), 2)
			var cc := t.get_center() * s
			var q := s
			_layer.draw_polyline(PackedVector2Array([cc + Vector2(-5.5, 0.5) * q, cc + Vector2(-1.5, 4.5) * q, cc + Vector2(6, -4) * q]), Color("#14320e"), 3.0 * s, true)
		else:
			_box(t, Color(0.08, 0.05, 0.19, 0.7), 14, Color(0, 0, 0, 0), 0, Color("#9b86d0"), 2)
			_text("+", t.get_center().x, t.get_center().y, "Fredoka", 700, 18.0, Color("#d9d0ff"))
		if full:
			var mb := Rect2(c.position + Vector2(26, 149), Vector2(CELL.x - 52, 28))
			_box(mb, Color("#d99b31"), 14, Color("#8a5a10"), 3)
			_box(Rect2(mb.position, Vector2(mb.size.x, mb.size.y * 0.55)), Color("#ffe58a"), 14)
			_text("MAX", cx, mb.get_center().y + 0.5, "Fredoka", 700, 16.0, Color("#613a0a"))
			return
		var gold := MetaData.booster_cost(lvl)
		var parts := MetaData.booster_parts_cost(lvl)
		var ok_g := Save.gold() >= gold
		var ok_p := Save.booster_parts() >= parts
		var can := ok_g and ok_p
		if can:
			_box(b, Color("#4bc62d"), 14, Color("#23802a"), 3)
			_box(Rect2(b.position, Vector2(b.size.x, b.size.y * 0.55)), Color("#8fe85c"), 14)
		else:
			_box(b, Color("#514d68"), 14, Color("#2e2b40"), 3)
			_box(Rect2(b.position, Vector2(b.size.x, b.size.y * 0.55)), Color("#6a6684"), 14)
		var g_txt := MockScreen.num(gold)
		var p_txt := str(parts)
		var w := 17.0 + 3.0 + _text_w(g_txt, 15.0) + 8.0 + 17.0 + 3.0 + _text_w(p_txt, 15.0)
		var x := cx - w * 0.5
		var cy := b.get_center().y
		var dark := Color("#14320e")
		var grey := Color("#e8e4f4")
		var red := Color("#ff8a8a")
		if _coin:
			_layer.draw_texture_rect(_coin, Rect2(Vector2(x, cy - 8.5) * s, Vector2(17, 17) * s), false, Color(1, 1, 1, 1.0 if can else 0.8))
		x += 20.0
		x += _text(g_txt, x, cy + 0.5, "Fredoka", 700, 15.0, dark if can else (grey if ok_g else red), 0.0) + 8.0
		if _parts:
			_layer.draw_texture_rect(_parts, Rect2(Vector2(x, cy - 8.5) * s, Vector2(17, 17) * s), false, Color(1, 1, 1, 1.0 if can else 0.8))
		x += 20.0
		_text(p_txt, x, cy + 0.5, "Fredoka", 700, 15.0, dark if can else (grey if ok_p else red), 0.0)

	func _gui_input(e: InputEvent) -> void:
		if not (e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT):
			return
		accept_event()
		var p: Vector2 = (e.position - off) / s
		if not DIALOG.has_point(p):
			Sfx.play("click")
			tab.close_booster()
			return
		for k in MetaData.BOOSTER_ORDER.size():
			var id := str(MetaData.BOOSTER_ORDER[k])
			if not Save.booster_unlocked(id):
				if button_rect(k).grow(6.0).has_point(p):
					Sfx.play("click")
					tab.menu.toast("%s gibt es ab Level %d" % [MetaData.BOOSTERS[id]["title"], int(MetaData.BOOSTERS[id]["unlock"]) + 1])
				continue
			if toggle_rect(k).grow(8.0).has_point(p):
				Sfx.play("click")
				var msg := Save.toggle_booster(id)
				if msg != "":
					tab.menu.toast(msg)
				tab.refresh()
				return
			if button_rect(k).grow(6.0).has_point(p):
				var lvl := Save.booster_level(id)
				if lvl >= MetaData.BOOSTER_MAX:
					return
				if Save.upgrade_booster(id):
					Sfx.play("levelup")
					tab.menu.toast("%s: Stufe %d" % [MetaData.BOOSTERS[id]["title"], Save.booster_level(id)])
				else:
					Sfx.play("click")
					if Save.gold() < MetaData.booster_cost(lvl):
						tab.menu.toast("Nicht genug Gold.")
					else:
						tab.menu.toast("Dir fehlen %d Booster-Teile. Es gibt sie in den Booster-Truhen im Shop." % (MetaData.booster_parts_cost(lvl) - Save.booster_parts()))
				tab.refresh()
				return
