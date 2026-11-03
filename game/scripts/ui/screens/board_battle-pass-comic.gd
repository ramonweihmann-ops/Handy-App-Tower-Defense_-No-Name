extends MockScreen
## Battle Pass nach dem freigegebenen Comic-Entwurf (Mockup „Battle Pass (neu, Comic v1)“, Vorlage
## Vorlage_Raw/Battle_Pass_Comic_v1). Kopf, Missionsfelder, Spaltenköpfe, Planeten und die drei Knöpfe
## unten kommen aus dem Export „battlepass“. Die Route mit allen Stufen zeichnet das Spiel aus den
## Bauteilen des Exports „battlepass_teile“ (Kapseln, Plattformen, Knoten, Schlösser, Haken, „Holen“):
## links kostenlos, rechts Premium, in der Mitte die leuchtende Route. Die Liste scrollt.
## Alle Maße in Mockup-Punkten, gemessen am Entwurf (tools/mock2game/v4/battlepass_board.py).

const SEASON_TEXT := "Saison 1 · Schleim-Welt"
const END_TEXT := "Endet in 24 T · 9 Std"
## Route: Knoten der Stufe k (ab 1) bei y = Y0 + (k − 1) · STEP, x = 195 + Schlängeln
const Y0 := 322.0
const STEP := 74.0
const ROUTE_TOP := 296.0
const ROUTE_BOTTOM := 654.0
const BAR_INNER := Rect2(57, 118, 280, 18)
const MISSION_Y := 166.0
const MISSION_GAP := 35.0
const CAP_FREE_X := 93.0     # Mitte der linken Kapsel
const CAP_PREM_X := 299.0    # Mitte der rechten Kapsel
const ICONS := ["gold", "gems", "cards", "stars"]

var _route: Route
var _head: Head
var _tex := {}
var _scroll := 0.0
var _mission_btn: Array[MockButton] = []


func _init(m: MainMenu) -> void:
	super("battlepass", m)


func _ready() -> void:
	super()
	for b in buttons():
		if str(b.info.get("on", "")) == "mission":
			_mission_btn.append(b)
			var lbl := BtnLabel.new()
			lbl.board = self
			lbl.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
			lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
			b.add_child(lbl)
	_mission_btn.sort_custom(func(a: MockButton, c: MockButton) -> bool: return a.info["rect"][1] < c.info["rect"][1])
	_head = Head.new()
	_head.board = self
	place_at(_head, Rect2(0, 0, W, H))
	_route = Route.new()
	_route.board = self
	_route.clip_contents = true
	place_at(_route, Rect2(0, ROUTE_TOP, W, ROUTE_BOTTOM - ROUTE_TOP))
	# Bauteile vorab laden; frisch geladene Bilder sind im ersten Bild noch nicht bereit
	for l in MockView.layout_of("battlepass_teile").get("states", {}).get("main", {}).get("live", []):
		part(str(l["id"]))
	for t in ICONS:
		icon(t)
	# Zur aktuellen Stufe scrollen
	_scroll = clampf(node_y(current_level()) - Y0 - STEP, 0.0, max_scroll())
	bind()
	await get_tree().process_frame
	queue_redraw_all()


func queue_redraw_all() -> void:
	if is_instance_valid(_route):
		_route.queue_redraw()
	if is_instance_valid(_head):
		_head.queue_redraw()
	_redraw_texts()
	for b in _mission_btn:
		for c in b.get_children():
			(c as Control).queue_redraw()


func bind() -> void:
	set_text(SEASON_TEXT, MetaData.PASS_SEASON)
	var left_s := maxi(0, MetaData.PASS_END - int(Time.get_unix_time_from_system()))
	set_text(END_TEXT, "Endet in %d T · %d Std" % [left_s / 86400, (left_s % 86400) / 3600])
	var m := Save.missions()
	var ids: Array = m["ids"]
	for k in _mission_btn.size():
		var b := _mission_btn[k]
		b.visible = k < ids.size()
		if k >= ids.size():
			continue
		var st := mission_state(str(ids[k]))
		b.enabled = st == "ready"
		b.texture = part("mbtn_ok") if st == "ready" else part("mbtn")
		var info: Dictionary = MockView.layout_of("battlepass_teile")["states"]["main"]
		for l in info["live"]:
			if str(l["id"]) == ("mbtn_ok" if st == "ready" else "mbtn"):
				var ir: Array = l["img_rect"]
				var dy: float = float(b.info["rect"][1]) - float(l["rect"][1])
				b.info["img_rect"] = [ir[0], float(ir[1]) + dy, ir[2], ir[3]]
		b.queue_redraw()
	queue_redraw_all()


## Zustand einer Mission: done (abgeholt), ready (geschafft), open
func mission_state(id: String) -> String:
	var m := Save.missions()
	var d := Save.mission_def(id)
	if m["claimed"].has(id):
		return "done"
	if int(m["progress"].get(id, 0)) >= int(d["goal"]):
		return "ready"
	return "open"


func handle(b: Dictionary) -> bool:
	var on := str(b.get("on", ""))
	if on == "mission":
		var k := -1
		for i in _mission_btn.size():
			if _mission_btn[i].info == b:
				k = i
		var ids: Array = Save.missions()["ids"]
		if k >= 0 and k < ids.size():
			var id := str(ids[k])
			var d := Save.mission_def(id)
			if Save.claim_mission(id):
				menu.reward_success([{"type": "pass", "amount": int(d["points"])}], "Tägliche Mission")
				bind()
		return true
	if on == "premium":
		menu.info("Premium-Pass", "Der Premium-Pass verdoppelt die Belohnungen und kommt mit dem Play Store. In der Testphase gibt es nur die kostenlose Spur.")
		return true
	if on == "claim_all":
		var got := []
		for l in Save.pass_claimable():
			var r := Save.claim_pass(l)
			if not r.is_empty():
				got.append(r)
		if got.is_empty():
			menu.toast("Noch nichts abzuholen.")
		else:
			menu.reward_success(got, "Battle Pass")
		bind()
		return true
	if str(b.get("href", "")) == "Main-v4.dc.html":
		menu.close_board(self)
		return true
	return false


func claim(level: int) -> void:
	var r := Save.claim_pass(level)
	if not r.is_empty():
		menu.reward_success([r], "Battle Pass · Stufe %d" % level)
	bind()


# --- Hilfen ------------------------------------------------------------------------------

## Stufe, an der gerade gesammelt wird (leuchtender Knoten)
func current_level() -> int:
	return mini(MetaData.PASS_LEVELS, Save.pass_level() + 1)


func node_y(level: int) -> float:
	return Y0 + (level - 1) * STEP


func node_x(level: int) -> float:
	if level <= 1:
		return 195.0
	return 189.0 if level % 2 == 0 else 201.0


func max_scroll() -> float:
	return maxf(0.0, node_y(MetaData.PASS_LEVELS) + 62.0 - ROUTE_BOTTOM)


func part(id: String) -> Texture2D:
	if not _tex.has(id):
		var t: Texture2D = null
		for l in MockView.layout_of("battlepass_teile").get("states", {}).get("main", {}).get("live", []):
			if str(l["id"]) == id:
				t = load("res://ui_mock/battlepass_teile/" + str(l["img"]))
		_tex[id] = t
	return _tex[id]


## Bildrechteck eines Bauteils (Mockup-Punkte) relativ zum Bezugspunkt im Export
func part_rect(id: String) -> Rect2:
	for l in MockView.layout_of("battlepass_teile")["states"]["main"]["live"]:
		if str(l["id"]) == id:
			var ir: Array = l["img_rect"]
			return Rect2(ir[0], ir[1], ir[2], ir[3])
	return Rect2()


func icon(t: String) -> Texture2D:
	var key := "icon_" + t
	if not _tex.has(key):
		var p := "res://ui/icons/%s.webp" % t
		_tex[key] = load(p) if ResourceLoader.exists(p) else null
	return _tex[key]


func text_at(ci: CanvasItem, txt: String, p: Vector2, fam: String, weight: int, px: float, col: Color, align := 0.5, shadow := Color(0, 0, 0, 0), sdy := 2.0) -> float:
	var f := MockFonts.font(fam, weight)
	var fs := maxi(1, roundi(px * s))
	var w := f.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var base := p.y * s + (f.get_ascent(fs) - f.get_descent(fs)) * 0.5
	var x := p.x * s - w * align
	if shadow.a > 0.0:
		ci.draw_string(f, Vector2(x, base + sdy * s), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, shadow)
	ci.draw_string(f, Vector2(x, base), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
	return w / s


class Head:
	extends Control
	## Fortschrittsbalken und die Texte der Missionen
	var board

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE

	func _draw() -> void:
		var bd = board
		var s: float = bd.s
		var r: Rect2 = BAR_INNER
		var prog := float(Save.pass_progress()) / float(MetaData.PASS_POINTS_PER_LEVEL)
		if prog > 0.0:
			var fr := Rect2(r.position, Vector2(maxf(r.size.y, r.size.x * prog), r.size.y))
			MockPaint.rrect(self, Rect2(fr.position * s, fr.size * s), 8 * s, Color("#ffe27a"), Color("#f0a81f"))
			MockPaint.rrect(self, Rect2((fr.position + Vector2(6, 1.5)) * s, Vector2(maxf(0.0, fr.size.x - 12), 2) * s), 1 * s, Color(1, 1, 1, 0.5))
		var txt := "Stufe %d · %d/%d" % [Save.pass_level(), Save.pass_progress(), MetaData.PASS_POINTS_PER_LEVEL]
		var cx: float = r.position.x + maxf(r.size.x * prog, 110.0) * 0.5
		bd.text_at(self, txt, Vector2(cx, r.get_center().y), "Fredoka", 700, 11.5, Color("#4a2000") if prog > 0.3 else Color.WHITE)
		var m := Save.missions()
		var ids: Array = m["ids"]
		for k in mini(3, ids.size()):
			var d := Save.mission_def(str(ids[k]))
			var y: float = MISSION_Y + k * MISSION_GAP
			var goal := int(d["goal"])
			var prog_m := mini(int(m["progress"].get(ids[k], 0)), goal)
			bd.text_at(self, String(d["text"]) % goal, Vector2(62, y + 11), "Fredoka", 600, 12.5, Color.WHITE, 0.0)
			bd.text_at(self, "%d/%d · +%d Pass-Punkte" % [prog_m, goal, int(d["points"])], Vector2(62, y + 23.5), "Nunito", 700, 9.5, Color("#b9b4e8"), 0.0)


class BtnLabel:
	extends Control
	## Beschriftung der Missions-Knöpfe: „Abholen“ (grün, wenn geschafft) bzw. „Erledigt“
	var board

	func _draw() -> void:
		var b := get_parent() as MockButton
		var bd = board
		var k: int = bd._mission_btn.find(b)
		var ids: Array = Save.missions()["ids"]
		if k < 0 or k >= ids.size():
			return
		var st: String = bd.mission_state(str(ids[k]))
		var txt := "Erledigt" if st == "done" else "Abholen"
		var col := Color("#0f3d12") if st == "ready" else Color("#d8d4f0")
		var s: float = bd.s
		var f := MockFonts.font("Fredoka", 600)
		var fs := maxi(1, roundi(11.5 * s))
		var w := f.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		draw_string(f, Vector2((size.x - w) * 0.5, size.y * 0.5 + (f.get_ascent(fs) - f.get_descent(fs)) * 0.5), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)


class Route:
	extends Control
	## Scrollbare Route mit allen Stufen; Antippen von „Holen“ holt die Belohnung
	var board
	var _t := 0.0
	var _press := Vector2.ZERO
	var _drag := 0.0
	var _down := false

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_STOP

	func _process(delta: float) -> void:
		_t += delta
		queue_redraw()

	## Mockup-Punkt auf dem Board -> Punkt in diesem Control (Bildpunkte)
	func _p(x: float, y: float) -> Vector2:
		return Vector2(x, y - ROUTE_TOP - board._scroll) * board.s

	func _draw_part(id: String, ref: Vector2, at: Vector2, size_override := Vector2(-1, -1), mod := Color.WHITE) -> void:
		var tex: Texture2D = board.part(id)
		if tex == null:
			return
		var r: Rect2 = board.part_rect(id)
		var pos := r.position - ref + at
		var sz := r.size if size_override.x < 0.0 else size_override
		draw_texture_rect(tex, Rect2(_p(pos.x, pos.y), sz * board.s), false, mod)

	func _draw() -> void:
		var bd = board
		var s: float = bd.s
		var n: int = MetaData.PASS_LEVELS
		var top: float = ROUTE_TOP + bd._scroll - STEP
		var bottom: float = ROUTE_BOTTOM + bd._scroll + STEP
		_draw_path(top, bottom)
		var reached: int = Save.pass_level()
		var premium := bool(Save.data.get("pass_premium", false))
		for lvl in range(1, n + 1):
			var y: float = bd.node_y(lvl)
			if y < top or y > bottom:
				continue
			var x: float = bd.node_x(lvl)
			var claimed: bool = Save.data["pass_claimed"].has(lvl)
			# Verbindungen Kapsel – Knoten
			_draw_part("conn_free", Vector2(149, 466), Vector2(149, y - 4), Vector2(x - 166.0, 4))
			_draw_part("conn_prem", Vector2(218, 466), Vector2(x + 17.0, y - 4), Vector2(238.0 - x - 16.0, 4))
			# Kapseln mit Plattform
			for prem in [false, true]:
				var side := "prem" if prem else "free"
				var cx: float = CAP_PREM_X if prem else CAP_FREE_X
				_draw_part("plat_" + side, Vector2(0, 470), Vector2(0, y))
				_draw_part("cap_" + side, Vector2(0, 470), Vector2(0, y))
				var rw := MetaData.pass_reward(lvl, prem)
				_draw_reward(cx, y - 2.0, str(rw["type"]), int(rw["amount"]))
				var open: bool = lvl <= reached and (premium or not prem)
				if not open:
					_draw_part("lock_" + side, Vector2(0, 470), Vector2(0, y))
				elif claimed:
					_draw_part("check", Vector2(0, 322), Vector2(0 if not prem else 206, y))
				elif not prem:
					var bob := sin(_t * 4.0) * 1.0
					_draw_part("holen", Vector2(0, 396), Vector2(0, y + bob))
					bd.text_at(self, "Holen", Vector2(92.0, y + 18.0 + bob - ROUTE_TOP - bd._scroll), "Fredoka", 700, 13, Color("#0f3d12"))
			# Knoten auf Plattform
			_draw_part("node_plat", Vector2(201, 470), Vector2(x, y))
			if lvl == bd.current_level():
				var pulse := 0.85 + 0.15 * sin(_t * TAU / 1.6)
				_draw_part("node_cur", Vector2(189, 396), Vector2(x, y), Vector2(-1, -1), Color(1, 1, 1, pulse))
			else:
				_draw_part("node", Vector2(201, 470), Vector2(x, y))
			bd.text_at(self, str(lvl), Vector2(x + 2.0, y - 3.0 - ROUTE_TOP - bd._scroll), "Fredoka", 700, 20 if lvl < 10 else 17, Color.WHITE, 0.5, Color("#0e6a2a"))

	func _draw_reward(cx: float, cy: float, type: String, amount: int) -> void:
		var bd = board
		var s: float = bd.s
		var txt := MockScreen.num(amount)
		var f := MockFonts.font("Fredoka", 700)
		var tw: float = f.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, maxi(1, roundi(18 * s))).x / s
		var total := 36.0 + 8.0 + tw
		var x0 := cx - total * 0.5
		var tex: Texture2D = bd.icon(type)
		var yy: float = cy - ROUTE_TOP - bd._scroll
		if tex:
			draw_texture_rect(tex, Rect2(Vector2(x0, yy - 18.0) * s, Vector2(36, 36) * s), false)
		bd.text_at(self, txt, Vector2(x0 + 44.0, yy), "Fredoka", 700, 18, Color.WHITE, 0.0, Color(20 / 255.0, 10 / 255.0, 60 / 255.0, 0.6))

	## Leuchtende Route wie im Entwurf: breiter violetter Schein, Kern, gestrichelte helle Mitte
	func _draw_path(top: float, bottom: float) -> void:
		var bd = board
		var pts := PackedVector2Array()
		var n: int = MetaData.PASS_LEVELS
		for lvl in range(1, n):
			var y0: float = bd.node_y(lvl)
			var y1: float = bd.node_y(lvl + 1)
			if y1 < top or y0 > bottom:
				continue
			var x0: float = bd.node_x(lvl)
			var x1: float = bd.node_x(lvl + 1)
			var off := 26.0 if (lvl - 1) % 2 == 0 else -26.0
			var mid := (y0 + y1) * 0.5
			var a := Vector2(x0, y0)
			var c1 := Vector2(x0 + off, mid - 6.0)
			var c2 := Vector2(x1 + off, mid + 6.0)
			var b := Vector2(x1, y1)
			for i in 17:
				var t := i / 16.0
				var u := 1.0 - t
				var q := a * u * u * u + c1 * 3.0 * u * u * t + c2 * 3.0 * u * t * t + b * t * t * t
				pts.append(_p(q.x, q.y))
		if pts.size() < 2:
			return
		var s: float = bd.s
		draw_polyline(pts, Color(150 / 255.0, 80 / 255.0, 1.0, 0.55), 14.0 * s, true)
		draw_polyline(pts, Color("#8a4cff"), 7.0 * s, true)
		# gestrichelt, läuft langsam mit
		var dash := 6.0 * s
		var acc := fmod(_t * 20.0 * s, dash * 2.0)
		for i in pts.size() - 1:
			var p0 := pts[i]
			var p1 := pts[i + 1]
			var seg := p0.distance_to(p1)
			var pos := 0.0
			while pos < seg:
				var phase := fmod(acc + pos, dash * 2.0)
				var step := minf(seg - pos, (dash - phase) if phase < dash else (dash * 2.0 - phase))
				if phase < dash:
					draw_line(p0.lerp(p1, pos / seg), p0.lerp(p1, (pos + step) / seg), Color("#bdf8ff"), 2.4 * s, true)
				pos += maxf(step, 0.01)
			acc = fmod(acc + seg, dash * 2.0)

	func _gui_input(e: InputEvent) -> void:
		var bd = board
		if e is InputEventMouseButton:
			var mb := e as InputEventMouseButton
			if mb.button_index == MOUSE_BUTTON_WHEEL_UP and mb.pressed:
				bd._scroll = clampf(bd._scroll - 40.0, 0.0, bd.max_scroll())
			elif mb.button_index == MOUSE_BUTTON_WHEEL_DOWN and mb.pressed:
				bd._scroll = clampf(bd._scroll + 40.0, 0.0, bd.max_scroll())
			elif mb.button_index == MOUSE_BUTTON_LEFT:
				if mb.pressed:
					_down = true
					_press = mb.position
					_drag = 0.0
				elif _down:
					_down = false
					if _drag < 10.0:
						_tap(mb.position)
			accept_event()
		elif e is InputEventMouseMotion and _down:
			var mm := e as InputEventMouseMotion
			_drag += mm.relative.length()
			bd._scroll = clampf(bd._scroll - mm.relative.y / bd.s, 0.0, bd.max_scroll())
			accept_event()

	func _tap(p: Vector2) -> void:
		var bd = board
		var my: float = p.y / bd.s + ROUTE_TOP + bd._scroll
		var mx: float = p.x / bd.s
		var reached: int = Save.pass_level()
		for lvl in range(1, reached + 1):
			if Save.data["pass_claimed"].has(lvl):
				continue
			var y: float = bd.node_y(lvl)
			# Kapsel links samt „Holen“
			if Rect2(34, y - 28, 118, 62).has_point(Vector2(mx, my)):
				Sfx.play("click")
				bd.claim(lvl)
				return
