extends Node
## Rundgang durchs Menü ohne Fenster: öffnet alle Reiter und Dialoge und spielt ein Level an.
## Aufruf: godot --headless --fixed-fps 60 --path game -- --smoke

var main: Node
var frame := 0
var step := 0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS


func _process(_delta: float) -> void:
	if _run():
		get_tree().quit()


func _run() -> bool:
	frame += 1
	if frame > 6000:
		print("SMOKE abgebrochen in Schritt ", step)
		return true
	if main.state != "menu" and step == 0:
		return false
	var save = Save
	var m: MainMenu = main.menu
	match step:
		0:
			save.reset()
			save.data["gold"] = 5000
			save.data["gems"] = 500
			save.data["stars"] = 3
			save.add_hero_cards("dusty", 20)
			print("SMOKE menü da, Reiter: ", m.current_tab)
		1:
			_report(m._content, 0)
			for t in ["shop", "sammlung", "upgrades", "basis", "kampf"]:
				m.show_tab(t)
			# Levelbilder: Boss der ersten Welt, Zombie-Welt, Boss der zweiten Welt
			for lvl in [5, 7, 10, 1]:
				m.selected_level = lvl
				m.show_tab("kampf")
			m.sub_tab["sammlung"] = "booster"
			m.show_tab("sammlung")
			m.sub_tab["upgrades"] = "talente"
			m.show_tab("upgrades")
			print("SMOKE alle Reiter gebaut")
		2:
			# Handybreite nachstellen (720 Pixel), damit nichts über den Rand ragt
			m._frame.offset_left = -360.0
			m._frame.offset_right = 360.0
			print("SMOKE held aufwerten: ", save.level_hero("dusty"), " stufe ", save.hero_level("dusty"))
			print("SMOKE tech kaufen: ", save.buy_next_tech(), " anzahl ", save.tech_count())
			print("SMOKE talent: ", save.draw_talent())
			save.data["buildings"]["dusty"]["time"] = int(Time.get_unix_time_from_system()) - 7200
			print("SMOKE gebäude sammeln: ", save.collect_building("dusty"), " ausbauen: ", save.upgrade_building("dusty"))
			save.add_pass_points(250)
			print("SMOKE pass stufe ", save.pass_level(), " holbar ", save.pass_claimable())
			print("SMOKE pass holen: ", save.claim_pass(1))
			print("SMOKE missionen: ", save.missions()["ids"])
			print("SMOKE munition kaufen: ", save.buy_ammo_upgrade("rate"), " stufe ", save.ammo_level("rate"))
			print("SMOKE kalle freischalten: ", save.unlock_with_gems("kalle"), " aufstellung ", save.squad())
			print("SMOKE aufstellung ändern: '", save.toggle_squad("iska"), "' jetzt ", save.squad())
			print("SMOKE boni: ", save.battle_bonus())
			print("SMOKE booster: ", save.booster_slots(), " aufwerten ", save.upgrade_booster("medipack"), " tauschen '", save.toggle_booster("zeitlupe"), "'")
		3:
			var page: Control = m._content.get_child(m._content.get_child_count() - 1)
			print("SMOKE reiter breite ", page.size.x, " inhalt ", m._content.size.x)
			var top: Control = m._frame.get_child(0)
			var parts := []
			for c in top.get_child(0).get_children():
				parts.append("%d-%d" % [c.position.x, c.position.x + c.size.x])
			print("SMOKE kopfleiste breite ", top.size.x, " rahmen ", m._frame.size.x, " teile ", parts)
			m._fit()
			m.open_battle_pass()
		4:
			m._open_daily()
		5:
			m._open_wheel()
		6:
			m._open_energy()
		7:
			m._open_settings()
			m._open_hero("kalle")
			m._open_hero("fritzi")
			m.sub_tab["upgrades"] = "munition"
			m.show_tab("upgrades")
		8:
			var u: Updater = main.updater
			u.current_code = 100
			var body := JSON.stringify({"code": 200, "name": "0.2.0", "stamp": "heute", "apk": "x.apk", "notes": "Test"}).to_utf8_buffer()
			u._on_check_done(HTTPRequest.RESULT_SUCCESS, 200, PackedStringArray(), body)
			print("SMOKE update erkannt: ", u.has_update(), " hinweis sichtbar: ", m._banner.visible)
			m._open_bestiary()
			m.show_rewards("Test", "Text", [{"type": "gold", "text": "+5 Gold"}])
		9:
			m._close_modal()
			main.start_level(1, false)
			print("SMOKE level gestartet, zustand ", main.state, " energie ", save.energy())
		10:
			main._on_hero_picked("dusty")
		200:
			main._booster_cd[0] = 0.0
			main._booster_cd[1] = 0.0
			main._use_booster(0)
			main._use_booster(1)
			print("SMOKE booster eingesetzt: ", main._boosters, " cd ", main._booster_cd)
		_:
			if step > 10 and step < 600:
				pass
			elif step == 600:
				main.battle.fence_hp = 1.0
				main.battle.damage_fence(5.0)
			elif step == 620:
				print("SMOKE ergebnis, zustand ", main.state, " gold ", save.gold(), " karten dusty ", save.hero_cards("dusty"))
				main.show_menu()
			elif step == 640:
				print("SMOKE zurück im menü: ", main.menu.visible, " ", main.state)
				print("SMOKE fertig")
				return true
	step += 1
	return false



## Meldet Elemente, die breiter als der Bildschirm sein wollen.
func _report(n: Node, depth: int) -> void:
	if n is Control:
		var c := n as Control
		var w := c.get_combined_minimum_size().x
		if w > 700.0 and depth < 12:
			print("SMOKE breit: ", "  ".repeat(depth), c.get_class(), " ", c.name, " min=", w)
	for ch in n.get_children():
		_report(ch, depth + 1)



func _sizes(n: Node, depth: int) -> void:
	if depth > 6:
		return
	if n is Control:
		var c := n as Control
		print("SMOKE größe: ", "  ".repeat(depth), c.get_class(), " pos=", c.position, " size=", c.size, " min=", c.get_combined_minimum_size())
	for ch in n.get_children():
		_sizes(ch, depth + 1)
