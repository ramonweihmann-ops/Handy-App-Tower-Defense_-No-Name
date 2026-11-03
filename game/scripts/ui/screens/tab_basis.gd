class_name BaseTab
extends MockScreen
## Reiter „Basis“ nach dem Mockup „Basislager · Übersicht“: Kopfleiste, Titel mit Zähler und
## Reiterleiste aus dem Mockup (Hintergrund durchsichtig), darunter die zoombare Karte (BaseMap).
## Antippen eines Gebäudes öffnet das Gebäudefenster des Menüs.

const TOP := {"energy": "25/30", "gold": "4.674", "gems": "350"}
const COUNT_TEXT := "6 von 30 Gebäuden · 3 baubar"
## Karte unter Kopfleiste und Titel; unten läuft sie wie im Mockup bis unter die Reiterleiste (Mockup-Punkte)
const MAP_TOP := 118.0
const MAP_BOTTOM := 0.0

var map: BaseMap


func _init(m: MainMenu) -> void:
	super("basis", m, TOP)


func _ready() -> void:
	super()
	_fill.visible = false
	map = BaseMap.new()
	map.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	map.building_pressed.connect(menu.open_building)
	add_child(map)
	move_child(map, 0)
	resized.connect(_fit_map)
	_fit_map()
	copy_nav_badges(self)
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
