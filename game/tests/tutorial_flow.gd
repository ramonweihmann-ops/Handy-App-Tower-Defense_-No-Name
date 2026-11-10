extends Node
## Spielt das Tutorial einmal ganz durch (ohne Fenster): nach dem Zurücksetzen von „Spielen“ über
## den ersten Kampf (Heldenwahl, Energiekern, Karte, Sieg), Helden aufleveln, Tech-Werft und
## Basislager bis zum Abschluss. Prüft jeden Schritt, die Sperre im Kampf und die Geschenke
## (genau der Fehlbetrag). Aufruf: godot --headless --fixed-fps 60 --path game -- --tutflow

var main: Node
var tut: Tutorial
var _step := 0
var _wait := 0
var _fails: Array[String] = []
var _board: Control


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS


func _process(_delta: float) -> void:
	if _wait > 0:
		_wait -= 1
		return
	if _step == 0 and main.state != "menu":
		return
	if tut == null:
		for c in main.get_children():
			if c is Tutorial:
				tut = c
	if _run():
		print("TUTFLOW fertig, fehler: ", _fails)
		get_tree().quit()
		return
	_step += 1
	_wait = 4


func _expect(key: String, what := "") -> void:
	var ok := tut._key.begins_with(key)
	print("TUTFLOW %-12s %s %s" % [key, "ok" if ok else "FEHLER (jetzt: %s, zustand %s)" % [tut._key, main.state], what])
	if not ok:
		_fails.append(key)


func _check(ok: bool, what: String) -> void:
	print("TUTFLOW %-12s %s" % [what, "ok" if ok else "FEHLER"])
	if not ok:
		_fails.append(what)


func _play_and_win() -> void:
	main.menu.play_selected()
	main._on_hero_picked(Save.squad()[0])
	main._on_level_won()


func _run() -> bool:
	var m: MainMenu = main.menu
	match _step:
		0:
			Save.reset()
			Save.data["energy"] = 0   # Geschenk prüfen: fehlende Energie für den ersten Kampf
			main.show_menu()
		1:
			_expect("play1")
			_check(Save.energy() >= MetaData.ENERGY_COST, "energie-geschenk")
			m.play_selected()
		2:
			_expect("pick")
			main._on_hero_picked(Save.squad()[0])
		3:
			_check(bool(Save.data["tut"].get("picked", false)), "held-gewählt")
			main.plasma._manual_cd = 0.0
		4:
			_expect("core")
			_check(get_tree().paused and tut._shade.mode == "catch", "kern-pause-sperre")
			tut._core_tap()
		5:
			_check(not get_tree().paused and bool(Save.data["tut"].get("core", false)), "kern-ausgelöst")
			main.pending_levelups = 1
			main._open_card_pick()
		6:
			_expect("card")
			# Kartenwahl (Entwurf B): jede mögliche Karte hat Kategorie, Titel, Wirkung; Antippen wählt aus
			var pick: CardPick = main._screen as CardPick
			_check(pick != null and pick.cards.size() >= 2, "kartenwahl-offen")
			if pick:
				var pool: Array = main._machine_cards() + [main._card_repair()]
				for h in main.battle.heroes:
					pool.append_array(main._hero_cards(h))
				for id in GameData.HERO_IDS:
					pool.append(main._card_add_hero(id))
				var bad: Array = []
				for c in pool:
					var f: Dictionary = pick.face(c)
					if not CardPick.CATS.has(f.get("cat", "")) or str(f["title"]) == "" or str(f["short"]) == "" or str(f["text"]) == "":
						bad.append(c["key"])
				_check(bad.is_empty(), "karten-gesichter %d %s" % [pool.size(), bad])
				var tap := InputEventMouseButton.new()
				tap.button_index = MOUSE_BUTTON_LEFT
				tap.pressed = true
				tap.position = pick.off + pick.slot_rect(0).get_center() * pick.s
				pick._gui_input(tap)
				_check(pick._sel == 0, "karte-antippen-waehlt")
			main._on_card_picked(main._roll_cards(3)[0])
		7:
			_check(bool(Save.data["tut"].get("card", false)), "karte-gewählt")
			main._on_level_won()
		8:
			_expect("result1")
			main.show_menu()
		9:
			_expect("nav#helden")
			m.show_tab("sammlung")
		10:
			_expect("herocard")
			HeroBoard.start_hero = str(Save.data["tut"].get("hero", Save.squad()[0]))
			m.open_board("Artboard-seqx-c6i2.dc.html")
		11:
			_expect("levelup")
			_board = m._boards[-1]
			var id: String = (_board as HeroBoard).hero
			_check(Save.can_level_hero(id), "helden-geschenk")
			(_board as HeroBoard)._level_up()
		12:
			_check(Tutorial._held_done(), "held-aufgelevelt")
			m.close_board(_board)
			m.show_tab("kampf")
		13:
			_expect("play4")
			_play_and_win()
		14:
			_expect("result2")
			main.show_menu()
		15:
			_expect("nav#upgrades")
			Save.data["gold"] = 0   # Geschenk prüfen: Gold fürs Ausbauen
			m.show_tab("upgrades")
		16:
			_expect("tech")
			var u := m._mock as UpgradesTab
			_check(Save.can_buy_tech_id(u.selected), "werft-geschenk")
			u.buy_selected()
		17:
			_check(Save.tech_count() == 1, "werft-ausgebaut")
			m.show_tab("kampf")
		18:
			_expect("play5")
			_play_and_win()
		19:
			_expect("result3")
			main.show_menu()
		20:
			_expect("nav#basis")
			Save.data["gold"] = 0
			m.show_tab("basis")
		21:
			_expect("base01")
			m.open_building("01")
		22:
			_expect("build01")
			_check(Save.base_can_upgrade("01"), "basis-geschenk")
			Save.base_upgrade("01")
			m.close_board(m._boards[-1])
		23:
			_expect("done")
			tut.finish()
		24:
			_check(not Tutorial.active(), "abgeschlossen")
			m.show_tab("kampf")
		25:
			# freiwilliger Tipp nach dem Tutorial: „Alles klar“ = nie wieder
			_expect("tip:taeglich")
			tut.tip_close()
		26:
			_check(int(Save.data["tut"]["tips"].get("taeglich", 0)) == -1 and tut._key == "", "tipp-alles-klar")
			m.show_tab("shop")
		27:
			m.show_tab("kampf")
		28:
			# nächster Tipp; ihm folgen (Glücksrad öffnen) = nie wieder
			_expect("tip:gluecksrad")
			_check(not tut._key.begins_with("tip:taeglich"), "tipp-kommt-nicht-wieder")
			m.open_board("Artboard-zqpq.dc.html")
		29:
			_check(int(Save.data["tut"]["tips"].get("gluecksrad", 0)) == -1, "tipp-befolgt")
			m.close_board(m._boards[-1])
		30:
			# „Spielstand zurücksetzen“ (Einstellungen) startet die Führung wieder von vorn
			m.open_settings()
		31:
			_check(tut._key == "", "einstellungen-frei")
			Save.reset()
			m.selected_level = 1
			m._close_modal()
			m.show_tab("kampf")
		32:
			_expect("play1", "(nach dem Zurücksetzen)")
			# „Ohne Hilfe spielen“ schaltet auch die Tipps ab
			tut.finish(true)
		33:
			_check(not Tutorial.active() and not Tutorial.tips_on() and tut._key == "", "ohne-hilfe-keine-tipps")
			return true
	return false
