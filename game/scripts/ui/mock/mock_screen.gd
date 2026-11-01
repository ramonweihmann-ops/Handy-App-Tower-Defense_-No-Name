class_name MockScreen
extends MockView
## Menü-Bildschirm aus einem Mockup mit allem, was alle gemeinsam haben: Kopfleiste (Profil,
## Energie, Gold, Edelsteine, Einstellungen), Reiterleiste unten mit roten Punkten und der
## Wechsel zu anderen Bildschirmen. Die einzelnen Bildschirme erben davon und kümmern sich nur
## um ihren eigenen Inhalt (handle()).

## Ziele der Reiterleiste im Mockup -> Reiter im Menü
const TAB_OF := {"#shop": "shop", "#helden": "sammlung", "#kampf": "kampf", "#upgrades": "upgrades", "#basis": "basis"}

var menu: MainMenu
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
	refresh()


func _process(delta: float) -> void:
	_tick += delta
	if _tick >= 1.0:
		_tick = 0.0
		refresh_top()


## Alles neu anzeigen (nach Kauf, Wechsel usw.)
func refresh() -> void:
	refresh_top()
	bind()


## Von den Bildschirmen überschrieben: eigene Werte eintragen
func bind() -> void:
	pass


## Von den Bildschirmen überschrieben: eigene Knöpfe; true = erledigt
func handle(_b: Dictionary) -> bool:
	return false


func refresh_top() -> void:
	if top_texts.has("energy"):
		set_text(top_texts["energy"], "%d/%d" % [Save.energy(), MetaData.ENERGY_MAX])
	if top_texts.has("gold"):
		set_text(top_texts["gold"], num(Save.gold()))
	if top_texts.has("gems"):
		set_text(top_texts["gems"], num(Save.gems()))
	if top_texts.has("stars"):
		set_text(top_texts["stars"], num(Save.stars()))
	if top_texts.has("level"):
		set_text(top_texts["level"], str(Save.max_level()))
	var want := {
		"#shop": Save.daily_ready("shop_free_date"),
		"#helden": Save.any_hero_ready() or Save.any_booster_upgrade(),
		"#upgrades": Save.can_buy_tech() or Save.any_ammo_upgrade() or Save.can_draw_talent(),
		"#basis": Save.any_building_ready(),
	}
	for b in buttons():
		var href := str(b.info.get("href", ""))
		if want.has(href) and b.badge_rect.size != Vector2.ZERO:
			b.badge = bool(want[href])


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
