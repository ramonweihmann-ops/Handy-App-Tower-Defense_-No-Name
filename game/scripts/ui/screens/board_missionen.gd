extends MockScreen
## Tägliche Missionen (Mockup „Missionen“), geöffnet vom Hauptbildschirm über „Missionen“.
## Die Missionen kommen aus dem Spielstand (Save.missions()): Text, Fortschrittsbalken und Knopf
## („Holen“, wenn geschafft, sonst „Los“ = zum Kampf) zeichnet das Spiel selbst mit den Bildern
## aus dem Mockup. Missionen bringen Punkte für den Battle Pass; die Truhen-Leiste oben zeigt
## deshalb die Punkte bis zur nächsten Battle-Pass-Stufe (100 Punkte je Stufe), die Truhe bei
## 100 ist die Belohnung dieser Stufe. Eigene Missionstruhen kennt das Spiel (noch) nicht.

## Punkte der Truhen in der Leiste
const CHEST_PTS := [20, 40, 60, 80, 100]
## Spitze des Truhen-Popups je Truhe (Mockup: 36 + arrowLeft)
const ARROW_X := [118.0, 172.0, 226.0, 280.0, 332.0]
## Ende des Balkens bei 0, 20, 40, 60, 80, 100 Punkten (Mockup: 40 Punkte reichen knapp über die Truhe)
const BAR_X := [76.0, 130.0, 186.8, 243.0, 292.0, 334.0]
## Missionszeilen: erste Karte, Abstand, Textbreite
const ROW_TOP := 301.0
const ROW_GAP := 8.0
const TEXT_X := 102.0
const TEXT_W := 162.0
## Lage in einer Zeile relativ zur Oberkante der Karte: kurz (eine Textzeile) und hoch (zwei)
const ROW_SHORT := {"h": 68.0, "text": 14.0, "track": 38.0, "pts": 42.5, "btn": 14.0, "card": "card"}
const ROW_TALL := {"h": 75.0, "text": 8.0, "track": 51.0, "pts": 46.0, "btn": 17.5, "card": "card_1"}
const POPUP := Rect2(36, 256, 318, 137)
const ITEM_NAMES := {"gold": "Gold", "gems": "Edelsteine", "cards": "Heldenkarten", "stars": "Talentstern"}
## Popup-Bilder: Symbol je Belohnung (Popup im Export, Live-Kennung)
const ICONS := {"gems": ["chest", "icon"], "cards": ["chest", "icon_1"], "stars": ["chest", "icon_2"], "gold": ["chest_gold", "icon"]}

const C_TEXT := "rgb(74, 58, 122)"
const C_RED := "rgb(208, 42, 42)"
const C_LIGHT := "rgb(255, 247, 234)"

var rows: Array = []   # je Mission: {id, text, goal, prog, claimed, points, y, kind}
var sel := -1          # geöffnete Truhe (Popup) oder -1
var pressed := -1      # gedrückter Zeilen-Knopf
var _layer: Control
var _popup: Control
var _tex := {}
var _row_btn: Array[Dictionary] = []   # Knopf-Daten aus dem Export: [grün „Holen“, blau „Los“]


func _init(m: MainMenu) -> void:
	super("missionen", m)


func _ready() -> void:
	super()
	for b in buttons():
		var r: Array = b.info["rect"]
		if str(b.info.get("href", "")) == "Main.dc.html" and str(b.info.get("label", "")) == "" and r[1] > 290 and r[1] < 700:
			# Zeilen-Knöpfe zeichnet die Zeile selbst (Anzahl und Lage hängen von den Missionen ab)
			b.visible = false
			_row_btn.append(b.info)
		elif str(b.info.get("on", "")).begins_with("pick"):
			for t in b.texts():
				hide_text(int(t["i"]))
	_row_btn.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return a["rect"][1] < b["rect"][1])
	_layer = Layer.new()
	_layer.board = self
	place_at(_layer, Rect2(0, 0, W, H))
	_popup = ChestPopup.new()
	_popup.board = self
	place_at(_popup, POPUP, true)
	_popup.visible = false
	# Bilder vorab laden; frisch geladene Bilder sind im ersten Bild noch nicht bereit
	for id in ["card", "card_1", "fill", "fill_2", "pts_fill", "pts_dial", "chest", "chest_2", "chest_4"]:
		tex(id)
	for k in ICONS:
		tex(ICONS[k][1], ICONS[k][0])
	tex("arrow", "chest")
	for bi in _row_btn:
		load("res://ui_mock/missionen/" + str(bi["img"]))
	var ov: Dictionary = layout_of("missionen").get("overlays", {}).get("chest", {})
	_tex["chest/_bg"] = load("res://ui_mock/missionen/" + str(ov["bg"])) if str(ov.get("bg", "")) != "" else null
	bind()
	await get_tree().process_frame
	_layer.queue_redraw()


func bind() -> void:
	refresh_top()
	rows.clear()
	var m := Save.missions()
	var y := ROW_TOP
	for id in m["ids"]:
		if rows.size() >= 4:
			break
		var d := Save.mission_def(id)
		if d.is_empty():
			continue
		var goal := int(d["goal"])
		var text := str(d["text"])
		var kind: Dictionary = ROW_TALL if _wrap(text, goal).size() > 1 else ROW_SHORT
		rows.append({"id": id, "text": text, "goal": goal, "prog": mini(int(m["progress"].get(id, 0)), goal),
			"claimed": m["claimed"].has(id), "points": int(d["points"]), "y": y, "kind": kind})
		y += float(kind["h"]) + ROW_GAP
	if _layer:
		_layer.queue_redraw()
	if _popup:
		_popup.queue_redraw()


func refresh_top() -> void:
	super()
	if data.size() > 0:
		var t := Time.get_time_dict_from_system()
		var left := 86400 - (int(t["hour"]) * 3600 + int(t["minute"]) * 60 + int(t["second"]))
		set_text("Neue Missionen in 9 Std. 12 Min.", "Neue Missionen in %d Std. %02d Min." % [left / 3600, (left % 3600) / 60])


func handle(b: Dictionary) -> bool:
	var on := str(b.get("on", ""))
	if on.begins_with("pick"):
		var k := CHEST_PTS.find(int(on.trim_prefix("pick")))
		_select(-1 if k == sel else k)
		return true
	if str(b.get("label", "")) == "Schließen":
		menu.close_board(self)
		return true
	if str(b.get("href", "")) == "Main.dc.html" and float(b["rect"][1]) > 700.0:
		menu.open_daily()
		return true
	return false


func _select(k: int) -> void:
	sel = k
	_popup.visible = k >= 0
	_popup.queue_redraw()


## Zeilen-Knopf: „Holen“ (geschafft) oder „Los“ (zum Kampf)
func row_pressed(i: int) -> void:
	var r: Dictionary = rows[i]
	if bool(r["claimed"]):
		return
	Sfx.play("click")
	if int(r["prog"]) >= int(r["goal"]):
		if Save.claim_mission(str(r["id"])):
			menu.celebrate("star", "+%d Pass-Punkte" % int(r["points"]))
		refresh()
	else:
		menu.close_board(self)
		menu.play_selected()


# --- Werte für die Truhen-Leiste -------------------------------------------------------------

func points() -> int:
	return Save.pass_progress()


func claimable() -> bool:
	return not Save.pass_claimable().is_empty()


## Battle-Pass-Stufe, deren Belohnung die Truhen zeigen
func reward_level() -> int:
	if claimable():
		return Save.pass_claimable()[0]
	return mini(Save.pass_level() + 1, MetaData.PASS_LEVELS)


func bar_end(p: int) -> float:
	var f := clampf(p / 20.0, 0.0, 5.0)
	var k := mini(int(f), 4)
	return lerpf(BAR_X[k], BAR_X[k + 1], f - k)


# --- Zeichnen -----------------------------------------------------------------------------

## Bild eines Live-Elements (ov = Name des Popups im Export oder "")
func tex(id: String, ov := "") -> Texture2D:
	var key := ov + "/" + id
	if not _tex.has(key):
		var f := str(info(id, ov).get("img", ""))
		_tex[key] = load("res://ui_mock/missionen/" + f) if f != "" else null
	return _tex[key]


func info(id: String, ov := "") -> Dictionary:
	if ov == "":
		return _live_info.get(id, {})
	for l in layout_of("missionen").get("overlays", {}).get(ov, {}).get("live", []):
		if str(l["id"]) == id:
			return l
	return {}


static func _rect(a: Array) -> Rect2:
	return Rect2(a[0], a[1], a[2], a[3])


## Bild aus dem Export so zeichnen, dass sein Element (rect) bei target liegt. Mit cap ≥ 0 wird es
## nur in der Mitte gestreckt (Balken mit runden Enden), sonst als Ganzes skaliert.
func draw_piece(ci: CanvasItem, t: Texture2D, inf: Dictionary, target: Rect2, cap := -1.0, mod := Color.WHITE) -> void:
	if t == null or inf.is_empty():
		return
	var el := _rect(inf["rect"])
	var ir := _rect(inf["img_rect"])
	var pad := el.position - ir.position
	if cap < 0.0:
		var k := target.size / el.size
		ci.draw_texture_rect(t, Rect2((target.position - pad * k) * s, ir.size * k * s), false, mod)
		return
	var px := t.get_width() / ir.size.x
	var lw := pad.x + cap
	var rw := ir.end.x - el.end.x + cap
	var mid_dst := maxf(0.0, target.size.x - 2.0 * cap)
	var mid_src := ir.size.x - lw - rw
	var x0 := target.position.x - pad.x
	var y0 := target.position.y - pad.y
	var th := float(t.get_height())
	var parts := [[x0, lw, 0.0, lw], [x0 + lw, mid_dst, lw, mid_src], [x0 + lw + mid_dst, rw, ir.size.x - rw, rw]]
	for p in parts:
		if p[1] <= 0.0:
			continue
		ci.draw_texture_rect_region(t, Rect2(Vector2(p[0], y0) * s, Vector2(p[1], ir.size.y) * s),
			Rect2(p[2] * px, 0.0, p[3] * px, th), mod)


## Text in Mockup-Schrift: r in Mockup-Punkten, align = left/center/right
func label(ci: CanvasItem, txt: String, r: Rect2, family: String, weight: int, size: float, color: String, align := "center", shadow := "none") -> float:
	var tw := text_w(txt, family, weight, size)
	var x := r.position.x
	if align == "center":
		x = r.position.x + (r.size.x - tw) * 0.5
	elif align == "right":
		x = r.end.x - tw
	var t := {"i": -1000, "lines": [{"rect": [x, r.position.y, tw, r.size.y], "text": txt}], "family": family,
		"weight": weight, "size": size, "color": color, "ls": 0.0, "shadow": shadow, "align": "center",
		"rot": 0.0, "opacity": 1.0, "button": -1}
	draw_text(ci, t, Vector2.ZERO)
	return x + tw


func text_w(txt: String, family: String, weight: int, size: float) -> float:
	var fs := maxi(1, roundi(size * s))
	return MockFonts.font(family, weight).get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x / s


## Missionstext in Zeilen umbrechen; jedes Wort ist eine Liste aus [Text, rot?]
func _wrap(text: String, goal: int) -> Array:
	var parts := text.split("%d")
	var marked := parts[0] + "\u0001" + str(goal) + "\u0002" + (parts[1] if parts.size() > 1 else "")
	var lines: Array = [[]]
	var line_w := 0.0
	var space := text_w(" ", "Nunito", 800, 14)
	var red := false
	for word in marked.split(" ", false):
		var pieces := []
		var cur := ""
		for ch in word:
			if ch == "\u0001" or ch == "\u0002":
				if cur != "":
					pieces.append([cur, red])
				cur = ""
				red = ch == "\u0001"
			else:
				cur += ch
		if cur != "":
			pieces.append([cur, red])
		var w := 0.0
		for p in pieces:
			w += text_w(p[0], "Nunito", 800, 14)
		var line: Array = lines[-1]
		if not line.is_empty() and line_w + space + w > TEXT_W:
			lines.append([])
			line_w = 0.0
		elif not line.is_empty():
			line_w += space
		lines[-1].append(pieces)
		line_w += w
	return lines


func draw_rows(ci: CanvasItem) -> void:
	for i in rows.size():
		var r: Dictionary = rows[i]
		var k: Dictionary = r["kind"]
		var y: float = r["y"]
		var card_id := str(k["card"])
		draw_piece(ci, tex(card_id), info(card_id), Rect2(32, y, 326, float(k["h"])))
		# Belohnung (Battle-Pass-Punkte) auf dem Symbol
		label(ci, "+%d" % int(r["points"]), Rect2(42, y + float(k["pts"]), 48, 14), "Fredoka", 800, 14, "rgb(255, 226, 122)",
			"center", "rgb(90, 42, 0) 0px 1px 0px, rgba(255, 200, 80, 0.3) 0px 0px 7px")
		# Text mit roter Zahl
		var ly := y + float(k["text"])
		for line in _wrap(str(r["text"]), int(r["goal"])):
			var x := TEXT_X
			for word in line:
				for p in word:
					x = label(ci, p[0], Rect2(x, ly, 0, 19), "Nunito", 800, 14, C_RED if p[1] else C_TEXT, "left")
				x += text_w(" ", "Nunito", 800, 14)
			ly += 19.0
		# Fortschrittsbalken
		var track := Rect2(TEXT_X, y + float(k["track"]), TEXT_W, 16)
		var done := int(r["prog"]) >= int(r["goal"])
		if done:
			draw_piece(ci, tex("fill"), info("fill"), track, 5.0)
		elif int(r["prog"]) > 0:
			var w := maxf(10.0, TEXT_W * float(r["prog"]) / float(r["goal"]))
			draw_piece(ci, tex("fill_2"), info("fill_2"), Rect2(track.position, Vector2(w, 16)), 5.0)
		label(ci, "%d/%d" % [int(r["prog"]), int(r["goal"])], track, "Nunito", 800, 11, "rgb(255, 255, 255)")
		# Knopf
		if _row_btn.size() < 2:
			continue
		var bi: Dictionary = _row_btn[0] if done else _row_btn[1]
		var br := button_rect(i)
		if pressed == i:
			br = br.grow(-br.size.y * 0.04)
		var mod := Color(1, 1, 1, 0.5) if bool(r["claimed"]) else Color.WHITE
		draw_piece(ci, load("res://ui_mock/missionen/" + str(bi["img"])), bi, br, -1.0, mod)
		var cap := "Erledigt" if bool(r["claimed"]) else ("Holen" if done else "LOS")
		label(ci, cap, Rect2(br.position.x, br.position.y + 10.5, br.size.x, 19), "Fredoka", 700, 15,
			"rgb(15, 61, 18)" if done else "rgb(255, 255, 255)")


func button_rect(i: int) -> Rect2:
	var r: Dictionary = rows[i]
	return Rect2(274, float(r["y"]) + float(r["kind"]["btn"]), 74, 40)


func draw_chests(ci: CanvasItem) -> void:
	var p := points()
	# Balken und Punktezahl
	if p > 0:
		var pi := info("pts_fill")
		draw_piece(ci, tex("pts_fill"), pi, Rect2(76, 220, bar_end(p) - 76.0, 8), 4.0)
	draw_piece(ci, tex("pts_dial"), info("pts_dial"), _rect(info("pts_dial")["rect"]))
	label(ci, str(p), Rect2(40, 213.5, 46, 19), "Fredoka", 700, 16, "rgb(255, 255, 255)")
	var ids := ["chest", "chest_1", "chest_2", "chest_3", "chest_4"]
	for k in 5:
		var r := _rect(info(ids[k])["rect"])
		var cx := r.get_center().x
		if k == 4:
			draw_piece(ci, tex("chest_4"), info("chest_4"), r)
			if claimable():
				label(ci, "Öffnen!", Rect2(cx - 30, 244, 60, 15), "Nunito", 800, 11, "rgb(29, 122, 58)")
			else:
				label(ci, "100", Rect2(cx - 30, 244, 60, 15), "Nunito", 800, 11, C_LIGHT)
			continue
		var reached := p >= int(CHEST_PTS[k])
		var tid := "chest" if reached else "chest_2"
		draw_piece(ci, tex(tid), info(tid), r)
		var num := str(CHEST_PTS[k])
		if reached:
			# Zahl mit Haken (die Schrift hat kein Hakenzeichen)
			var tw := text_w(num, "Nunito", 800, 11)
			var x0 := cx - (tw + 12.0) * 0.5
			label(ci, num, Rect2(x0, 242, tw, 15), "Nunito", 800, 11, C_LIGHT, "left")
			var c := Vector2(x0 + tw + 3.0, 249.5)
			ci.draw_polyline(PackedVector2Array([c * s, (c + Vector2(3, 3)) * s, (c + Vector2(9, -3)) * s]),
				MockFonts.color(C_LIGHT), 1.6 * s, true)
		else:
			label(ci, num, Rect2(cx - 20, 242, 40, 15), "Nunito", 800, 11, C_LIGHT)


func draw_popup(ci: CanvasItem) -> void:
	if sel < 0:
		return
	var ov: Dictionary = layout_of("missionen").get("overlays", {}).get("chest", {})
	if not _tex.has("chest/_bg"):
		_tex["chest/_bg"] = load("res://ui_mock/missionen/" + str(ov.get("bg", ""))) if str(ov.get("bg", "")) != "" else null
	var bg_tex: Texture2D = _tex["chest/_bg"]
	if bg_tex:
		var br := _rect(ov["rect"])
		ci.draw_texture_rect(bg_tex, Rect2(br.position * s, br.size * s), false)
	var ai := info("arrow", "chest")
	if not ai.is_empty():
		var ar := _rect(ai["rect"])
		ar.position.x = float(ARROW_X[sel]) - ar.size.x * 0.5
		draw_piece(ci, tex("arrow", "chest"), ai, ar)
	var lvl := reward_level()
	label(ci, "Battle Pass · Stufe %d" % lvl, Rect2(48, 276, 0, 20), "Fredoka", 700, 16, C_LIGHT, "left")
	var status := "Noch %d Punkte" % maxi(0, MetaData.PASS_POINTS_PER_LEVEL - points())
	var col := "rgb(255, 226, 122)"
	if claimable():
		status = "Jetzt abholen!"
		col = "rgb(157, 255, 122)"
	elif Save.pass_level() >= MetaData.PASS_LEVELS:
		status = "Alles geschafft"
		col = "rgb(157, 255, 122)"
	label(ci, status, Rect2(48, 278, 294, 16), "Nunito", 800, 12, col, "right")
	var items := [MetaData.pass_reward(lvl, false)]
	var n := items.size()
	var w := (294.0 - 8.0 * (n - 1)) / n
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(1, 1, 1, 0.08)
	sb.set_corner_radius_all(roundi(10 * s))
	for k in n:
		var it: Dictionary = items[k]
		var r := Rect2(48 + k * (w + 8.0), 304, w, 77)
		ci.draw_style_box(sb, Rect2(r.position * s, r.size * s))
		var type := str(it["type"])
		if ICONS.has(type):
			var ic: Array = ICONS[type]
			draw_piece(ci, tex(ic[1], ic[0]), info(ic[1], ic[0]), Rect2(r.get_center().x - 14.0, 310, 28, 28))
		label(ci, "×" + num(int(it["amount"])), Rect2(r.position.x, 340, w, 18), "Fredoka", 700, 15, C_LIGHT)
		var name: String = ITEM_NAMES.get(type, MetaData.REWARD_NAMES.get(type, type))
		if type == "stars" and int(it["amount"]) > 1:
			name = "Talentsterne"
		label(ci, name, Rect2(r.position.x, 360, w, 14), "Nunito", 700, 10, "rgb(207, 200, 240)")


## Missionszeilen und Truhen-Leiste; Antippen der Zeilen-Knöpfe
class Layer:
	extends Control
	var board: Node

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_STOP

	func _draw() -> void:
		board.draw_chests(self)
		board.draw_rows(self)

	func _hit(p: Vector2) -> int:
		for i in board.rows.size():
			if board.button_rect(i).grow(4.0).has_point(p):
				return i
		return -1

	func _gui_input(e: InputEvent) -> void:
		if not (e is InputEventMouseButton and (e as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT):
			return
		var p: Vector2 = get_local_mouse_position() / float(board.s)
		if e.pressed:
			if board.sel >= 0:
				board._select(-1)
			board.pressed = _hit(p)
			queue_redraw()
		else:
			var i: int = board.pressed
			board.pressed = -1
			queue_redraw()
			if i >= 0 and _hit(p) == i:
				board.row_pressed(i)
		accept_event()


## Popup einer Truhe: Belohnung der nächsten Battle-Pass-Stufe
class ChestPopup:
	extends Control
	var board: Node

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_STOP

	func _draw() -> void:
		draw_set_transform(-POPUP.position * board.s)
		board.draw_popup(self)

	func _gui_input(e: InputEvent) -> void:
		if e is InputEventMouseButton and e.pressed and (e as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT:
			accept_event()
			var open: bool = board.claimable()
			board._select(-1)
			if open:
				board.menu.open_battle_pass()
