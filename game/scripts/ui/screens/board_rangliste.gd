extends MockScreen
## Liga-Rangliste (Mockup „Rangliste · Liga“): Siegertreppchen für die Plätze 1–3, darunter die
## Plätze 4–7 (bis Platz 5 goldene Saison-Truhe, darüber die Aufstiegszone), unten der eigene Platz.
## Die Liga hat 30 Kommandanten (Save.leaderboard); im Pilot sind die anderen Computergegner.

var rows: Array = []
var _layer: Control


func _init(m: MainMenu) -> void:
	super("rangliste", m, {"energy": "25/30", "gold": "4.674"})


func _ready() -> void:
	super()
	_layer = Layer.new()
	_layer.board = self
	place_at(_layer, Rect2(0, 0, W, H))
	# Namen auf dem Treppchen stehen mittig auf ihrem Schild
	for t in data.get("texts", []):
		if str(t["text"]) in ["Nebula_Nia", "Orion_X", "Kosmo_K"]:
			t["align"] = "center"
	bind()


func bind() -> void:
	rows = Save.leaderboard()
	var t := Save.trophies()
	set_text("1.228", MockScreen.num(t))
	set_text("BRONZE-LIGA", MpData.league_name(t).to_upper())
	set_text("Saison endet in 3 Tagen 7 Std.", MpData.season_left_text(int(Time.get_unix_time_from_system())))
	if rows.size() >= 3:
		set_text("Orion_X", str(rows[0]["name"]))
		set_text("3.306", MockScreen.num(int(rows[0]["trophies"])))
		set_text("Nebula_Nia", str(rows[1]["name"]))
		set_text("3.183", MockScreen.num(int(rows[1]["trophies"])))
		set_text("Kosmo_K", str(rows[2]["name"]))
		set_text("2.196", MockScreen.num(int(rows[2]["trophies"])))
	if _layer:
		_layer.queue_redraw()


func me() -> Dictionary:
	for r in rows:
		if r["me"]:
			return r
	return {}


func handle(b: Dictionary) -> bool:
	var href := str(b.get("href", ""))
	var label := str(b.get("label", ""))
	if href == "MP-Gegnersuche.dc.html":
		if Save.energy() < MetaData.ENERGY_COST:
			menu.open_energy()
			return true
		menu.close_board(self)
		menu.open_mp_search()
		return true
	match label:
		"Zurück":
			menu.close_board(self)
			return true
		"So funktioniert die Liga":
			menu.info("Die Liga", "Im Multiplayer kämpfst du mit drei anderen Kommandanten um Pokale: Platz 1 und 2 bringen Pokale, auf den hinteren Plätzen können welche verloren gehen. Mit genug Pokalen steigst du in die nächste Liga auf. Am Ende jeder Saison (alle zwei Wochen) gibt es eine Truhe: eine goldene bis Platz %d, sonst eine silberne." % MpData.GOLD_CHEST_RANKS)
			return true
		"Letzte Kämpfe":
			menu.info("Letzte Kämpfe", _history_text())
			return true
	return false


func _history_text() -> String:
	var hist: Array = Save.mp()["history"]
	if hist.is_empty():
		return "Noch keine Kämpfe in dieser Saison. Auf geht's!"
	var lines: Array[String] = []
	for h in hist:
		var d := int(h["delta"])
		var me_row: Dictionary = {}
		for r in h["rows"]:
			if r.get("me", false):
				me_row = r
		lines.append("%d. Platz · %s Pokale · %d besiegt · %s" % [int(h["place"]), ("+%d" % d) if d >= 0 else "−%d" % absi(d),
			int(me_row.get("kills", 0)), MpData.time_text(float(me_row.get("secs", 0)))])
	return "\n".join(PackedStringArray(lines))


class Layer:
	extends Control
	var board: MockScreen

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE

	func _draw() -> void:
		var bd: Variant = board
		var s := board.s
		var rows: Array = bd.rows
		if rows.size() < 7:
			return
		# Treppchen: Rundbilder (Reihenfolge im Mockup: Platz 2, 1, 3)
		var pod := [[1, "av"], [0, "av_1"], [2, "av_2"]]
		for p in pod:
			var r := board.live_rect(p[1])
			MpPaint.avatar(self, r.get_center() * s, r.size.x * s, str(rows[p[0]]["hero"]), Color(1, 1, 1, 0.85), 3 * s)
		# Plätze 4–7
		for i in 4:
			var e: Dictionary = rows[3 + i]
			var slot := board.live_rect("row" if i == 0 else "row_%d" % i)
			var top := slot.position.y
			MockPaint.text(board, self, str(e["rank"]), Rect2(28, top + 10, 26, 22), "Fredoka", 700, 17, "rgb(255, 247, 234)")
			var av := board.live_rect("av_%d" % (3 + i))
			MpPaint.avatar(self, av.get_center() * s, av.size.x * s, str(e["hero"]), Color("#ffd34d"), 2 * s)
			var name := "DU" if e["me"] else str(e["name"])
			_left(name, Vector2(104, top + 12), 15, "rgb(255, 247, 234)")
			_trophies(int(e["trophies"]), 358.0, top + 12, 15, 16)
		# Eigener Platz
		var me: Dictionary = bd.me()
		var mr := board.live_rect("me")
		var mt := mr.position.y
		MockPaint.text(board, self, str(me.get("rank", 30)), Rect2(18, mt + 17, 30, 26), "Fredoka", 700, 20, "rgb(255, 247, 234)", "0px 2px 0px #14408a")
		var mav := board.live_rect("av_7")
		MpPaint.avatar(self, mav.get_center() * s, mav.size.x * s, str(me.get("hero", "dusty")), Color.WHITE, 2 * s)
		_left("DU", Vector2(104, mt + 18), 17, "rgb(255, 247, 234)", "0px 2px 0px #14408a")
		_trophies(int(me.get("trophies", 0)), 368.0, mt + 18, 17, 18, "0px 2px 0px #14408a")

	func _left(txt: String, p: Vector2, size: float, color: String, shadow := "") -> void:
		var w := MockPaint.text_width(txt, "Fredoka", 700, size)
		MockPaint.text(board, self, txt, Rect2(p.x, p.y, w, size * 1.25), "Fredoka", 700, size, color, shadow)

	## Pokal-Symbol und Zahl, rechtsbündig bis right
	func _trophies(n: int, right: float, y: float, size: float, icon: float, shadow := "") -> void:
		var t := MockScreen.num(n)
		var w := MockPaint.text_width(t, "Fredoka", 700, size)
		_left(t, Vector2(right - w, y), size, "rgb(255, 247, 234)", shadow)
		var s := board.s
		MpPaint.trophy(self, Rect2((right - w - icon - 3) * s, (y + (size * 1.25 - icon) * 0.5) * s, icon * s, icon * s))
