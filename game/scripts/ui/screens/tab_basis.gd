class_name BaseTab
extends MockScreen
## Reiter „Basis“ nach dem Mockup „Basislager · Übersicht“: Kopfleiste, Titel mit Zähler und
## Reiterleiste aus dem Mockup (Hintergrund durchsichtig), darunter die zoombare Karte (BaseMap).
## Antippen eines Gebäudes öffnet das Gebäudefenster des Menüs, Antippen seiner Lager-Blase sammelt direkt ein.
## Ab 10 Champions schwebt unten der Knopf „Alle Lager einsammeln“, sobald irgendwo etwas bereitliegt.

const TOP := {"energy": "25/30", "gold": "4.674", "gems": "350"}
const COUNT_TEXT := "6 von 30 Gebäuden · 3 baubar"
## Karte unter Kopfleiste und Titel; unten läuft sie wie im Mockup bis unter die Reiterleiste (Mockup-Punkte)
const MAP_TOP := 118.0
const MAP_BOTTOM := 0.0
## „Alle Lager einsammeln“: ab so vielen Champions, Lage über der Reiterleiste (Mockup-Punkte)
const COLLECT_ALL_FROM := 10
const COLLECT_ALL_RECT := Rect2(95, 696, 200, 46)
const ITEM_NAMES := {"gold": "Gold", "gems": "Edelsteine", "energy": "Energie", "cards": "Heldenkarten", "stars": "Sterne"}

var map: BaseMap
var _all: CollectAll


func _init(m: MainMenu) -> void:
	super("basis", m, TOP)


func _ready() -> void:
	super()
	_fill.visible = false
	map = BaseMap.new()
	map.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	map.building_pressed.connect(menu.open_building)
	map.collect_pressed.connect(_collect)
	add_child(map)
	move_child(map, 0)
	resized.connect(_fit_map)
	_fit_map()
	copy_nav_badges(self)
	_all = CollectAll.new()
	_all.tab = self
	place_at(_all, COLLECT_ALL_RECT.grow(8.0), true)
	bind()


func _fit_map() -> void:
	if map:
		map.pad_top = MAP_TOP * s + off.y
		map.pad_bottom = MAP_BOTTOM * s + off.y


func bind() -> void:
	var built := 0
	var ready := 0
	for d in BaseData.BUILDINGS:
		match Save.base_state(d["id"]):
			"built":
				built += 1
			"buildable":
				ready += 1
	set_text(COUNT_TEXT, "%d von 30 Gebäuden" % built + (" · %d baubar" % ready if ready > 0 else ""))


## Gebäude, deren Lager etwas bereit hat
func ready_buildings() -> Array[String]:
	var out: Array[String] = []
	for d in BaseData.BUILDINGS:
		if d["kind"] == "prod" and Save.base_state(d["id"]) == "built" and Save.base_stock(d["id"]) >= 1.0:
			out.append(str(d["id"]))
	return out


func collect_all_visible() -> bool:
	return Save.unlocked_heroes().size() >= COLLECT_ALL_FROM and not ready_buildings().is_empty()


## Lager-Blase angetippt: direkt einsammeln, „+120“ über dem Gebäude
func _collect(id: String) -> void:
	var r := Save.base_collect(id)
	if int(r["amount"]) <= 0:
		return
	map.popup(id, "+%s" % MockScreen.num(int(r["amount"])), str(r["type"]))
	refresh()
	menu._refresh_top()


## Alle Lager auf einmal: je Gebäude „+…“ auf der Karte, zusammen eine kurze Feier
func collect_all() -> void:
	var sums := {}
	for id in ready_buildings():
		var r := Save.base_collect(id)
		var n := int(r["amount"])
		if n <= 0:
			continue
		var item := str(r["type"])
		sums[item] = int(sums.get(item, 0)) + n
		map.popup(id, "+%s" % MockScreen.num(n), item)
	if sums.is_empty():
		menu.toast("Noch nichts bereit.")
		return
	var parts := []
	var main_item := ""
	var best := -1
	for item in sums.keys():
		parts.append("+%s %s" % [MockScreen.num(int(sums[item])), ITEM_NAMES.get(item, item)])
		if int(sums[item]) > best:
			best = int(sums[item])
			main_item = item
	menu.celebrate({"gems": "gem", "stars": "star"}.get(main_item, main_item), " · ".join(parts))
	refresh()
	menu._refresh_top()


## Rote Punkte der Reiterleiste an derselben Stelle wie auf dem Abenteuer-Pfad
static func copy_nav_badges(v: MockView) -> void:
	var home: Dictionary = MockView.layout_of("home").get("states", {}).get("main", {})
	var home_btns := {}
	for hb in home.get("buttons", []):
		home_btns[int(hb["i"])] = hb
	for l in home.get("live", []):
		if not bool(l.get("badge", false)) or not home_btns.has(int(l.get("button", -1))):
			continue
		var hb: Dictionary = home_btns[int(l["button"])]
		var href := str(hb.get("href", ""))
		var mine := v.button(href) if href != "" else null
		if mine == null:
			continue
		var hr: Array = hb["rect"]
		var mr: Array = mine.info["rect"]
		var r: Array = l["rect"]
		mine.badge_rect = Rect2(float(r[0]) - float(hr[0]) + float(mr[0]), float(r[1]) - float(hr[1]) + float(mr[1]), r[2], r[3])


## Schwebender Knopf „Alle Lager einsammeln“ (Gold wie „BAUEN“, Zähler mit der Zahl der vollen Lager)
class CollectAll:
	extends Control
	var tab: BaseTab
	var _t := 0.0
	var _press := false
	var _font: Font

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_STOP
		_font = MockFonts.font("Fredoka", 700)

	var _n := 0
	var _check := 0.0

	func _process(delta: float) -> void:
		# Lager nur zweimal pro Sekunde prüfen (30 Gebäude), gezeichnet wird bei jedem Bild (Wippen)
		_check -= delta
		if _check <= 0.0:
			_check = 0.5
			_n = tab.ready_buildings().size()
			visible = Save.unlocked_heroes().size() >= COLLECT_ALL_FROM and _n > 0
		if visible:
			_t += delta
			queue_redraw()

	func _draw() -> void:
		var s := tab.s
		var r := Rect2(Vector2(8, 8) * s, COLLECT_ALL_RECT.size * s)
		r.position.y += (sin(_t * TAU / 1.6) * 2.0 - (2.0 if _press else 0.0)) * s
		var rad := 23.0 * s
		MockPaint.rrect(self, Rect2(r.position + Vector2(0, 9 * s), r.size), rad, Color(0, 0, 0, 0.28))
		MockPaint.rrect(self, Rect2(r.position + Vector2(0, 5 * s), r.size), rad, Color("#a86a00"))
		MockPaint.rrect(self, r, rad, Color("#ffe27a"), Color("#f0a81f"))
		MockPaint.rrect(self, Rect2(r.position + Vector2(14, 2) * s, Vector2(r.size.x - 28 * s, 4 * s)), 2 * s, Color(1, 1, 1, 0.45))
		var fs := maxi(6, roundi(15 * s))
		var txt := "ALLE EINSAMMELN"
		var tw := _font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var base := r.get_center().y + (_font.get_ascent(fs) - _font.get_descent(fs)) * 0.5
		draw_string(_font, Vector2(r.get_center().x - tw * 0.5 - 10 * s, base), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color("#4a2000"))
		# Zähler: wie viele Lager etwas haben
		var n := _n
		var bc := Vector2(r.end.x - 22 * s, r.get_center().y)
		draw_circle(bc, 13 * s, Color("#ffffff"))
		draw_circle(bc, 11 * s, Color("#ff3b30"))
		var ns := str(n)
		var nfs := maxi(6, roundi(13 * s))
		var nw := _font.get_string_size(ns, HORIZONTAL_ALIGNMENT_LEFT, -1, nfs).x
		draw_string(_font, Vector2(bc.x - nw * 0.5, bc.y + (_font.get_ascent(nfs) - _font.get_descent(nfs)) * 0.5), ns, HORIZONTAL_ALIGNMENT_LEFT, -1, nfs, Color.WHITE)

	func _gui_input(e: InputEvent) -> void:
		if e is InputEventMouseButton and e.button_index == MOUSE_BUTTON_LEFT:
			if e.pressed:
				_press = true
			elif _press:
				_press = false
				if Rect2(Vector2.ZERO, size).has_point(e.position):
					Sfx.play("ding")
					tab.collect_all()
					_check = 0.0
			accept_event()
