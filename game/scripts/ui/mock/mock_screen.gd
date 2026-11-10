class_name MockScreen
extends MockView
## Menü-Bildschirm aus einem Mockup mit allem, was alle gemeinsam haben: Kopfleiste (Profil,
## Energie, Gold, Edelsteine, Einstellungen), Reiterleiste unten mit roten Punkten und der
## Wechsel zu anderen Bildschirmen. Die einzelnen Bildschirme erben davon und kümmern sich nur
## um ihren eigenen Inhalt (handle()).

## Ziele der Reiterleiste im Mockup -> Reiter im Menü
const TAB_OF := {"#shop": "shop", "#helden": "sammlung", "#kampf": "kampf", "#upgrades": "upgrades", "#basis": "basis"}

## Einheitliche Reiterleiste (aus dem Kampf-Bildschirm, ui/nav_bar.webp): liegt auf jedem Bildschirm, der im
## Mockup eine eigene Reiterleiste hat, und ersetzt diese (Größe und Symbole überall gleich)
const NAV_TOP := 750.0
const NAV_HITS := {"#shop": Rect2(14, 778, 60, 66), "#helden": Rect2(87, 778, 60, 66), "#kampf": Rect2(163, 758, 64, 68),
	"#upgrades": Rect2(243, 778, 62, 66), "#basis": Rect2(320, 778, 60, 66)}
const NAV_BADGES := {"#shop": Vector2(61, 785), "#helden": Vector2(134, 785), "#upgrades": Vector2(289, 785), "#basis": Vector2(367, 785)}

var menu: MainMenu
var _nav_bar: NavBar
## Ursprüngliche Texte der Kopfleiste in diesem Mockup (zum Austauschen gegen echte Werte)
var top_texts := {}
var _tick := 0.0


func _init(screen_name: String, m: MainMenu, top := {}) -> void:
	super(screen_name)
	menu = m
	top_texts = top


func _ready() -> void:
	super()
	button_pressed.connect(_on_pressed)
	_use_shared_nav()
	refresh()


## Eigene Reiterleiste des Mockups ausblenden und die einheitliche darüberlegen (nicht im Kampf-Bildschirm,
## dort ist sie Teil des Hintergrunds)
func _use_shared_nav() -> void:
	if self is HomeScreen:
		return
	var own := false
	var top := 999.0
	for b in buttons():
		var href := str(b.info.get("href", ""))
		if TAB_OF.has(href) and float((b.info["rect"] as Array)[1]) > 700.0:
			b.visible = false
			own = true
			if href != "#kampf":
				top = minf(top, float((b.info["rect"] as Array)[1]))
	if not own or _nav_bar:
		return
	_nav_bar = NavBar.new()
	_nav_bar.screen = self
	# eigene Leiste beginnt höher als die einheitliche (Helden, Upgrades): Rand darüber verdecken
	_nav_bar.cover_from = 762.0 if top < 788.0 else 0.0
	place_at(_nav_bar, Rect2(0, NAV_TOP, W, H - NAV_TOP), true)


## Ein anderer Zustand legt die Knöpfe neu an: die eigene Reiterleiste wieder ausblenden
func show_state(state_name: String) -> void:
	super(state_name)
	if is_node_ready():
		_use_shared_nav()


func _process(delta: float) -> void:
	_tick += delta
	if _tick >= 1.0:
		_tick = 0.0
		refresh_top()


## Alles neu anzeigen (nach Kauf, Wechsel usw.)
func refresh() -> void:
	refresh_top()
	bind()
	# bind() darf die Knöpfe ein- und ausblenden; die alte Reiterleiste bleibt trotzdem verborgen
	if _nav_bar:
		_use_shared_nav()


## Von den Bildschirmen überschrieben: eigene Werte eintragen
func bind() -> void:
	pass


## Von den Bildschirmen überschrieben: eigene Knöpfe; true = erledigt
func handle(_b: Dictionary) -> bool:
	return false


func refresh_top() -> void:
	if top_texts.has("energy"):
		set_text(top_texts["energy"], "%d/%d" % [Save.energy(), Save.energy_max()])
	if top_texts.has("gold"):
		set_text(top_texts["gold"], num(Save.gold()))
	if top_texts.has("gems"):
		set_text(top_texts["gems"], num(Save.gems()))
	if top_texts.has("stars"):
		set_text(top_texts["stars"], num(Save.stars()))
	if top_texts.has("level"):
		set_text(top_texts["level"], str(Save.max_level()))
	var want := {
		"#shop": Save.shop_free_ready(),
		"#helden": Save.any_hero_ready(),
		"#upgrades": Save.can_buy_tech() or Save.any_ammo_upgrade() or Save.any_booster_upgrade() or Save.can_draw_talent(),
		"#basis": Save.any_building_ready(),
	}
	for b in buttons():
		var href := str(b.info.get("href", ""))
		if want.has(href) and b.badge_rect.size != Vector2.ZERO:
			b.badge = bool(want[href])
	if _nav_bar:
		_nav_bar.badges = want
		_nav_bar.queue_redraw()


## Zahl mit Tausenderpunkt wie im Mockup („4.573“)
static func num(n: int) -> String:
	var t := str(absi(n))
	var out := ""
	while t.length() > 3:
		out = "." + t.right(3) + out
		t = t.left(t.length() - 3)
	return ("-" if n < 0 else "") + t + out


func _on_pressed(b: Dictionary) -> void:
	Sfx.play("click")
	if handle(b):
		return
	var href := str(b.get("href", ""))
	var label := str(b.get("label", ""))
	if TAB_OF.has(href):
		menu.show_tab(TAB_OF[href])
	elif href == "#pass":
		menu.open_battle_pass()
	elif href.ends_with(".dc.html"):
		menu.open_board(href)
	elif label == "Energie kaufen":
		menu.open_energy()
	elif label in ["Gold kaufen", "Edelsteine kaufen"]:
		menu.show_tab("shop")
	elif label in ["Einstellungen", "Profil"]:
		menu.open_settings()
	elif label == "Schließen":
		menu.close_board(self)
	else:
		menu.toast("Kommt bald")



## Die einheitliche Reiterleiste: Bild aus dem Kampf-Bildschirm, rote Punkte, Antippen wechselt den Reiter,
## der aktive Reiter bekommt eine goldene Marke unter dem Namen
class NavBar:
	extends Control
	var screen: MockScreen
	var badges := {}
	var cover_from := 0.0
	var _tex: Texture2D = preload("res://ui/nav_bar.webp")

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_STOP

	func _p(v: Vector2) -> Vector2:
		return (v - Vector2(0, NAV_TOP)) * screen.s

	func _draw() -> void:
		var bg: Texture2D = screen._bg.texture if screen._bg else null
		if cover_from > 0.0 and bg:
			# Hintergrund knapp über der alten Leiste nach unten ziehen, damit deren Rand verschwindet
			var k := bg.get_width() / W
			var src := Rect2(0, (cover_from - 1.0) * k, bg.get_width(), 1.0)
			draw_texture_rect_region(bg, Rect2(_p(Vector2(0, cover_from)), Vector2(size.x, 16.0 * screen.s)), src)
		draw_texture_rect(_tex, Rect2(Vector2.ZERO, size), false)
		var cur := str(screen.menu.current_tab) if screen.menu else ""
		for href in NAV_HITS:
			if TAB_OF[href] == cur and href != "#kampf":
				var r: Rect2 = NAV_HITS[href]
				var c := _p(Vector2(r.get_center().x, 841.5))
				var w := 22.0 * screen.s
				draw_rect(Rect2(c - Vector2(w * 0.5, 1.5 * screen.s), Vector2(w, 3.0 * screen.s)), Color("ffd34d"))
		for href in NAV_BADGES:
			if bool(badges.get(href, false)):
				var p := _p(NAV_BADGES[href])
				draw_circle(p, 6.0 * screen.s, Color(1, 1, 1))
				draw_circle(p, 4.0 * screen.s, Color(1.0, 0.23, 0.19))

	func _gui_input(e: InputEvent) -> void:
		if e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT:
			var m: Vector2 = (e as InputEventMouseButton).position / screen.s + Vector2(0, NAV_TOP)
			for href in NAV_HITS:
				if (NAV_HITS[href] as Rect2).has_point(m):
					accept_event()
					Sfx.play("click")
					screen.menu.show_tab(TAB_OF[href])
					return
