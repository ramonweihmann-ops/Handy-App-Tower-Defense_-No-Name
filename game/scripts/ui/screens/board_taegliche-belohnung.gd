extends MockScreen
## Tägliche Belohnung (Mockup „Tägliche Belohnung · ausgearbeitet“): 7-Tage-Kalender und
## Treue-Serie mit Truhen nach 7, 14, 21 und 28 Tagen am Stück.
##
## Rahmen, Kopf, Sternenfeld, Tag-7-Tafel, Knöpfe und Reiter kommen aus dem Mockup
## (ui_mock/taeglich). Die Tageskarten liegen in drei Zuständen als Bilder vor (erledigt, heute,
## gesperrt), die Symbole darauf einzeln, damit sie sich wie im Mockup bewegen und der Glanz
## nur über das Symbol läuft. Beschriftungen und Mengen zeichnet das Spiel.

const MILESTONES := [7, 14, 21, 28]
## Mitte der Truhen auf der Leiste und Anfang/Ende des Balkens (Mockup-Punkte)
const BAR_X0 := 94.0
const C_DONE := "rgb(182, 255, 138)"
const C_NEXT := "rgb(255, 226, 122)"
const C_LOCK := "rgb(255, 247, 234)"
const HEAD_SHADOW := {"done": "rgb(106, 98, 160) 0px 1px 0px", "today": "rgb(29, 107, 42) 0px 1px 0px", "locked": "rgb(138, 90, 42) 0px 1px 0px"}

var _layer: Layer
var _tex := {}
var _cards: Array[Rect2] = []   # 6 Tageskarten
var _icon_nodes: Array[TextureRect] = []
var _chest_nodes: Array[TextureRect] = []
var _shine: Shader


func _init(m: MainMenu) -> void:
	super("taeglich", m)


func _ready() -> void:
	super()
	_shine = load("res://shaders/glanz.gdshader")
	_layer = Layer.new()
	_layer.board = self
	place_at(_layer, Rect2(0, 0, W, H))
	bind()


func _lay(state_name: String) -> Dictionary:
	return layout_of("taeglich").get("states", {}).get(state_name, {})


## Bild eines Live-Elements aus einem Zustand ({img, img_rect}) oder {}
func _live_of(state_name: String, id: String) -> Dictionary:
	for l in _lay(state_name).get("live", []):
		if str(l["id"]) == id:
			return l
	return {}


func _image(state_name: String, id: String) -> Texture2D:
	var l := _live_of(state_name, id)
	var key := str(l.get("img", ""))
	if key == "":
		return null
	if not _tex.has(key):
		_tex[key] = load("res://ui_mock/taeglich/" + key)
	return _tex[key]


func _rect(l: Dictionary, k: String) -> Rect2:
	var r: Array = l.get(k, [0, 0, 0, 0])
	return Rect2(r[0], r[1], r[2], r[3])


func _day_state(i: int) -> String:
	var today := Save.daily_day()
	if i < today or (i == today and Save.daily_claimed_today()):
		return "done"
	return "today" if i == today else "locked"


func bind() -> void:
	if _layer == null:
		return
	var claimed := Save.daily_claimed_today()
	_overrides.clear()
	show_state("abgeholt" if claimed else "main")
	var streak := Save.daily_streak()
	set_text("10" if claimed else "9", str(streak))
	set_text("Nächste Belohnung in 23 Std. 58 Min.", _timer_text())
	# Truhen-Leiste: Tag 7/14/21/28 im aktuellen 28er-Block
	var block := _block(streak)
	var labels := ["Tag 7 ✓", "Tag 14", "Tag 21", "Tag 28"]
	for k in 4:
		var m: int = block + MILESTONES[k]
		var st := _chest_state(k, block, streak)
		set_text(labels[k], ("Tag %d ✓" % m) if st == "done" else "Tag %d" % m)
		for t in data.get("texts", []):
			if str(t["text"]) == labels[k]:
				t["color"] = C_DONE if st == "done" else (C_NEXT if st == "next" else C_LOCK)
	# Karten und Symbole neu aufbauen
	_cards.clear()
	for i in 6:
		_cards.append(_rect(_live_of("gesperrt", "day" if i == 0 else "day_%d" % i), "rect"))
	for n in _icon_nodes + _chest_nodes:
		n.queue_free()
	_icon_nodes.clear()
	_chest_nodes.clear()
	for i in 6:
		var st := _day_state(i + 1)
		if st == "done":
			continue
		var sname := "heute" if st == "today" else "gesperrt"
		var id := "dicon" if i == 0 else "dicon_%d" % i
		_add_icon(sname, id, i, DAILY_MOTION[i])
	if not (Save.daily_day() == 7 and claimed):
		for k in 5:
			_add_icon("main", "t7icon" if k == 0 else "t7icon_%d" % k, 10 + k, T7_MOTION[k])
	for k in 4:
		var st := _chest_state(k, block, streak)
		var img_id := "chest" if st == "done" else ("chest_1" if st == "next" else "chest_2")
		var l := _live_of("main", img_id)
		var target := _rect(_live_of("main", "chest" if k == 0 else "chest_%d" % k), "rect")
		var ir := _rect(l, "img_rect")
		var tr := _shiny(_image("main", img_id), k * 0.6 + 0.3)
		place_at(tr, Rect2(target.get_center() - ir.size * 0.5, ir.size))
		_chest_nodes.append(tr)
	_layer.queue_redraw()


## Bewegung je Tageskarte wie im Mockup: Münze dreht sich, sonst leichtes Wippen
const DAILY_MOTION := ["coin", "bob", "bob", "none", "coin", "bob"]
const T7_MOTION := ["bob", "coin", "none", "none", "none"]


func _add_icon(sname: String, id: String, n: int, motion: String) -> void:
	var l := _live_of(sname, id)
	if l.is_empty():
		return
	var tr := _shiny(_image(sname, id), n * 0.37)
	tr.set_meta("motion", motion)
	tr.set_meta("phase", n * 0.7)
	tr.set_meta("rect", _rect(l, "img_rect"))
	place_at(tr, _rect(l, "img_rect"))
	_icon_nodes.append(tr)


func _shiny(tex: Texture2D, delay: float) -> TextureRect:
	var tr := TextureRect.new()
	tr.texture = tex
	tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	tr.stretch_mode = TextureRect.STRETCH_SCALE
	tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var m := ShaderMaterial.new()
	m.shader = _shine
	m.set_shader_parameter("delay", delay)
	m.set_shader_parameter("dur", 2.2 + fmod(delay * 3.0, 0.8))
	tr.material = m
	return tr


## Truhe k (0..3) im aktuellen 28er-Block: erledigt, als nächste dran oder noch gesperrt
func _chest_state(k: int, block: int, streak: int) -> String:
	if streak >= block + MILESTONES[k]:
		return "done"
	if k == 0 or streak >= block + MILESTONES[k - 1]:
		return "next"
	return "locked"


func _block(streak: int) -> int:
	return int(maxi(0, streak - 1) / 28) * 28 if Save.daily_claimed_today() else int(streak / 28) * 28


func _timer_text() -> String:
	if not Save.daily_claimed_today():
		return "Deine Belohnung für heute wartet!"
	var t := Time.get_time_dict_from_system()
	var left := 86400 - (int(t["hour"]) * 3600 + int(t["minute"]) * 60 + int(t["second"]))
	return "Nächste Belohnung in %d Std. %d Min." % [left / 3600, (left % 3600) / 60]


func _process(delta: float) -> void:
	super(delta)
	var tm := Time.get_ticks_msec() * 0.001
	for tr in _icon_nodes:
		if not is_instance_valid(tr):
			continue
		var motion := str(tr.get_meta("motion", "none"))
		var ph := float(tr.get_meta("phase", 0.0))
		tr.pivot_offset = tr.size * 0.5
		if motion == "coin":
			# Münze dreht sich gleichmäßig wie im Mockup
			tr.scale.x = maxf(0.18, absf(cos((tm + ph) * PI / 2.8)))
		elif motion == "bob":
			# leichtes Wippen wie im Mockup
			var r: Rect2 = tr.get_meta("rect")
			tr.position = to_screen(r.position + Vector2(0, sin((tm + ph) * TAU / 2.0) * 1.5))
	if _tick == 0.0:
		set_text(_timer_key(), _timer_text())
	_layer.queue_redraw()


func _timer_key() -> String:
	return "Nächste Belohnung in 23 Std. 58 Min."


func handle(b: Dictionary) -> bool:
	var href := str(b.get("href", ""))
	if str(b.get("label", "")) == "Schließen":
		menu.close_board(self)
		return true
	if str(b.get("on", "")) == "claim":
		_claim()
		return true
	if href == "Missionen.dc.html":
		menu.close_board(self)
		menu.open_board("Missionen.dc.html")
		return true
	if href == "Taegliche-Belohnung.dc.html":
		return true
	var label := str(b.get("label", ""))
	if label.begins_with("Treue-Truhe"):
		menu.toast("Treue-Truhe: 20 Edelsteine und 8 Heldenkarten für jede volle Woche am Stück")
		return true
	return false


func _claim() -> void:
	if Save.daily_claimed_today():
		return
	var day := Save.daily_day()
	var items := Save.claim_daily()
	if items.is_empty():
		return
	bind()
	var streak := Save.daily_streak()
	var to_chest := 7 - streak % 7
	var chip := "Serie: %d %s · noch %d bis zur Treue-Truhe" % [streak, "Tag" if streak == 1 else "Tage", to_chest]
	menu.reward_success(items, "Tag %d · Tägliche Belohnung" % day, chip)


class Layer:
	extends Control
	var board

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_PASS

	func _draw() -> void:
		var b = board
		var s: float = b.s
		# Tageskarten: Bild je Zustand, darauf Kopf und Menge
		for i in 6:
			var st: String = b._day_state(i + 1)
			var r: Rect2 = b._cards[i]
			var tex: Texture2D
			var ir: Rect2
			if st == "done":
				tex = b._image("main", "day")
				ir = b._rect(b._live_of("main", "day"), "img_rect")
				ir.position += r.position - Vector2(34, 302)
			else:
				var sname := "heute" if st == "today" else "gesperrt"
				var id := "day" if i == 0 else "day_%d" % i
				tex = b._image(sname, id)
				ir = b._rect(b._live_of(sname, id), "img_rect")
			if tex:
				draw_texture_rect(tex, Rect2(ir.position * s, ir.size * s), false)
			var head := "HEUTE" if st == "today" else "TAG %d" % (i + 1)
			MockPaint.text(b, self, head, Rect2(r.position, Vector2(r.size.x, 22)), "Fredoka", 700, 13, "rgb(255, 255, 255)", b.HEAD_SHADOW[st])
			if st != "done":
				var amt := "×" + MockScreen.num(int(MetaData.DAILY_REWARDS[i][0]["amount"]))
				MockPaint.text(b, self, amt, Rect2(r.position.x, r.position.y + 77, r.size.x, 19), "Fredoka", 700, 14, "rgb(255, 255, 255)")
		# Tag 7: große Belohnung
		var st7: String = b._day_state(7)
		var t7l: Dictionary = b._live_of("heute" if st7 == "today" else "main", "t7")
		var t7tex: Texture2D = b._image("heute" if st7 == "today" else "main", "t7")
		var t7r: Rect2 = b._rect(t7l, "img_rect")
		if t7tex:
			draw_texture_rect(t7tex, Rect2(t7r.position * s, t7r.size * s), false, Color(0.75, 0.75, 0.8) if st7 == "done" else Color.WHITE)
		var head7 := ("HEUTE · GROSSE BELOHNUNG" if st7 == "today" else "TAG 7 · GROSSE BELOHNUNG")
		MockPaint.text(b, self, head7, Rect2(34, 532, 322, 24), "Fredoka", 700, 13, "rgb(255, 255, 255)",
			"rgb(29, 107, 42) 0px 1px 0px" if st7 == "today" else "rgb(58, 21, 128) 0px 1px 0px")
		var a7 := [Rect2(49.7, 611, 38.3, 19), Rect2(107.3, 611, 57.5, 19), Rect2(186.1, 611, 36, 19), Rect2(245.4, 611, 36, 19), Rect2(302.7, 611, 37.6, 19)]
		for k in 5:
			MockPaint.text(b, self, "×" + MockScreen.num(int(MetaData.DAILY_REWARDS[6][k]["amount"])), a7[k], "Fredoka", 700, 14, "rgb(255, 255, 255)")
		if st7 == "done":
			_check(Vector2(195, 586) * s, 22.0 * s)
		# Fortschritt der Treue-Serie bis zur nächsten Truhe
		var streak := Save.daily_streak()
		var block: int = b._block(streak)
		var x0: float = b.BAR_X0
		var xs := [x0, 134.0, 200.0, 265.0, 328.0]
		var in_block := clampi(streak - block, 0, 28)
		var seg := mini(in_block / 7, 3)
		var x: float = lerpf(xs[seg], xs[seg + 1], float(in_block - seg * 7) / 7.0) if in_block < 28 else float(xs[4])
		if x > x0 + 1.0:
			var fr := Rect2(x0, 184, x - x0, 8)
			MockPaint.rrect(self, Rect2(fr.position * s - Vector2(0, 2) * s, fr.size * s + Vector2(0, 4) * s), 6 * s, Color(0.55, 0.94, 0.42, 0.25))
			MockPaint.rrect_h(self, Rect2(fr.position * s, fr.size * s), 4 * s, Color("#8cf06a"), Color("#3fbf3a"))

	func _check(c: Vector2, r: float) -> void:
		draw_circle(c, r, Color("#3fbf3a"))
		draw_arc(c, r, 0, TAU, 32, Color.WHITE, r * 0.18, true)
		draw_polyline(PackedVector2Array([c + Vector2(-0.45, 0.05) * r, c + Vector2(-0.1, 0.4) * r, c + Vector2(0.5, -0.3) * r]), Color.WHITE, r * 0.25, true)

	func _gui_input(e: InputEvent) -> void:
		# Antippen der „Heute“-Karte holt die Belohnung ab (wie im Mockup)
		if e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT:
			var p: Vector2 = get_local_mouse_position() / board.s
			var today: int = Save.daily_day()
			if Save.daily_claimed_today():
				return
			var r: Rect2 = board._cards[today - 1] if today <= 6 else Rect2(34, 532, 322, 108)
			if r.has_point(p):
				accept_event()
				Sfx.play("click")
				board._claim()
