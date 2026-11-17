extends MockScreen
## Spielmodi (Mockup „Spielmodi · Auswahl“), geöffnet über die Kachel „Modi“ im Hauptbildschirm:
## Multiplayer (4 Kommandanten), Universumsode (kommt bald), Weltraumschlacht (kommt bald).
## Dazu der Knopf „Testkarte“ (Werkzeug zum Testen, nicht im Mockup; solange der Nutzer der einzige Tester
## ist, immer sichtbar).

var _test_btn: Button


func _init(m: MainMenu) -> void:
	super("spielmodi", m, {"energy": "25/30", "gold": "4.674"})


func bind() -> void:
	set_text("1.228", MockScreen.num(Save.trophies()))
	if _test_btn == null:
		_test_btn = Button.new()
		_test_btn.text = "TESTKARTE"
		_test_btn.focus_mode = Control.FOCUS_NONE
		_test_btn.add_theme_font_size_override("font_size", 30)
		_test_btn.add_theme_color_override("font_color", Color(1, 1, 1))
		_test_btn.add_theme_stylebox_override("normal", UiKit.box(Color(0.75, 0.2, 0.25, 0.95), 12, 3, Color(1, 1, 1, 0.85)))
		_test_btn.add_theme_stylebox_override("hover", UiKit.box(Color(0.85, 0.28, 0.3, 0.95), 12, 3, Color(1, 1, 1, 0.85)))
		_test_btn.add_theme_stylebox_override("pressed", UiKit.box(Color(0.6, 0.15, 0.2, 0.95), 12, 3, Color(1, 1, 1, 0.85)))
		_test_btn.pressed.connect(menu.open_test_map)
		place_at(_test_btn, Rect2(16, 774, 136, 40), true)


func handle(b: Dictionary) -> bool:
	var href := str(b.get("href", ""))
	if str(b.get("label", "")) == "Schließen":
		menu.close_board(self)
		return true
	if href == "MP-Gegnersuche.dc.html":
		if Save.energy() < MetaData.ENERGY_COST:
			menu.open_energy()
			return true
		menu.close_board(self)
		menu.open_mp_search()
		return true
	if href == "Main.dc.html" or href == "Universumsode-Preis.dc.html":
		menu.toast("Die Universumsode kommt mit einem der nächsten Updates.")
		return true
	return false
