class_name MpResultScreen
extends MockView
## Ergebnis eines Multiplayer-Kampfes (Mockup „Multiplayer · Ergebnis und Wertung“): Platz im Band,
## die vier Kommandanten nach Punkten (besiegte Gegner, Zeit, Punkte, Pokale), darunter die Regel
## und die Belohnung. Zeilen, Rundbilder und Werte zeichnet das Spiel mit den Bildern aus dem Mockup.
##
## info: {place, standings (MpData.rank), delta, gold, pass, trophies}

signal again_pressed
signal ranking_pressed
signal menu_pressed

const RANK_COLORS := ["rgb(255, 211, 77)", "rgb(217, 226, 255)", "rgb(255, 176, 112)", "rgb(207, 200, 240)"]

var info := {}
var _layer: Rows
var _rays: TextureRect
var _crown: TextureRect


func _init(info_: Dictionary) -> void:
	info = info_
	super("mp_ergebnis")


func _ready() -> void:
	super()
	_fill.visible = false
	var dim := ColorRect.new()
	dim.color = Color(10 / 255.0, 6 / 255.0, 30 / 255.0, 0.74)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(dim)
	move_child(dim, 0)
	_rays = live_image("rays")
	if _rays:
		_live_layer.move_child(_rays, 0)
	var place := int(info.get("place", 4))
	set_text("1. PLATZ!", "%d. PLATZ!" % place if place == 1 else "%d. PLATZ" % place)
	set_text("Bronze-Liga · Multiplayer", "%s · Multiplayer" % MpData.league_name(int(info.get("trophies", 0)) - int(info.get("delta", 0))))
	var d := int(info.get("delta", 0))
	set_text("+32", ("+%d" % d) if d >= 0 else "−%d" % absi(d))
	set_text("×850", "×" + MockScreen.num(int(info.get("gold", 0))))
	set_text("×30", "×%d" % int(info.get("pass", 0)))
	_layer = Rows.new()
	_layer.view = self
	place_at(_layer, Rect2(0, 0, W, H))
	_crown = live_image("crown", true)
	button_pressed.connect(func(b: Dictionary) -> void:
		Sfx.play("click")
		var href := str(b.get("href", ""))
		if href == "MP-Gegnersuche.dc.html":
			again_pressed.emit()
		elif href == "Rangliste.dc.html":
			ranking_pressed.emit()
		else:
			menu_pressed.emit())


func _process(delta: float) -> void:
	if _rays:
		_rays.pivot_offset = _rays.size * 0.5
		_rays.rotation += delta * TAU / 40.0


## Zeilen der vier Kommandanten
class Rows:
	extends Control
	var view: MpResultScreen
	var _tex := {}

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE

	func _img(id: String) -> Texture2D:
		if not _tex.has(id):
			var l: Dictionary = view._live_info.get(id, {})
			_tex[id] = load("res://ui_mock/mp_ergebnis/" + str(l["img"])) if str(l.get("img", "")) != "" else null
		return _tex[id]

	func _img_rect(id: String) -> Rect2:
		var ir: Array = view._live_info.get(id, {}).get("img_rect", [0, 0, 0, 0])
		return Rect2(ir[0], ir[1], ir[2], ir[3])

	func _draw() -> void:
		var s := view.s
		var rows: Array = view.info.get("standings", [])
		var base := view.live_rect("row")
		for i in mini(rows.size(), 4):
			var e: Dictionary = rows[i]
			var me: bool = e.get("me", false)
			var slot := view.live_rect("row" if i == 0 else "row_%d" % i)
			# Bild der Zeile: blau für den Spieler, rot für die anderen (beide aus dem Mockup)
			var src := "row" if me else "row_1"
			var tex := _img(src)
			if tex:
				var ir := _img_rect(src)
				var srect := view.live_rect(src)
				var off := ir.position - srect.position
				draw_texture_rect(tex, Rect2((slot.position + off) * s, ir.size * s), false)
			var top := slot.position.y
			MockPaint.text(view, self, str(e["place"]), Rect2(22, top + 14, 26, 36), "Fredoka", 700, 28, RANK_COLORS[i], "0px 2px 0px #1a0f3a")
			var av := view.live_rect("av" if i == 0 else "av_%d" % i)
			MpPaint.avatar(self, av.get_center() * s, av.size.x * s, str(e["hero"]), Color.WHITE, 2 * s)
			_left(str(e["name"]), Vector2(112, top + 9), 17, "Fredoka", 700, "rgb(255, 247, 234)", "0px 2px 0px #1a0f3a")
			# besiegte Gegner · Zeit
			var x := 112.0
			MpPaint.skull(self, Rect2(x * s, (top + 37.5) * s, 13 * s, 13 * s))
			x += 17.0
			x = _left(str(int(e["kills"])) + " ", Vector2(x, top + 36), 12, "Nunito", 800, "rgb(255, 247, 234)")
			x = _left("· ", Vector2(x, top + 36), 12, "Nunito", 800, "rgba(255, 247, 234, 0.6)")
			MpPaint.clock(self, Rect2(x * s, (top + 37.5) * s, 13 * s, 13 * s))
			_left(MpData.time_text(float(e["secs"])), Vector2(x + 17, top + 36), 12, "Nunito", 800, "rgb(255, 247, 234)")
			# Punkte rechtsbündig
			var right := 376.0 - 12.0
			var pk := " Pkt."
			var pw := MockPaint.text_width(pk, "Nunito", 800, 10)
			_left(pk, Vector2(right - pw, top + 15), 10, "Nunito", 800, "rgba(255, 247, 234, 0.8)")
			var pts := MockScreen.num(int(e["points"]))
			var tw := MockPaint.text_width(pts, "Fredoka", 700, 18)
			_left(pts, Vector2(right - pw - tw, top + 8), 18, "Fredoka", 700, "rgb(255, 247, 234)", "0px 2px 0px #1a0f3a")
			# Pokale
			var d := int(view.info.get("delta", 0)) if me else MpData.trophy_delta(int(e.get("trophies", 0)), int(e["place"]))
			var dt := ("+%d" % d) if d >= 0 else "−%d" % absi(d)
			var dw := MockPaint.text_width(dt, "Fredoka", 700, 13)
			_left(dt, Vector2(right - dw, top + 38), 13, "Fredoka", 700, "rgb(182, 255, 138)" if d >= 0 else "rgb(255, 176, 184)")
			MpPaint.trophy(self, Rect2((right - dw - 16) * s, (top + 39.5) * s, 13 * s, 13 * s))
		if view._crown:
			view._crown.visible = true

	## Text linksbündig ab p; gibt das rechte Ende zurück
	func _left(txt: String, p: Vector2, size: float, family: String, weight: int, color: String, shadow := "") -> float:
		var w := MockPaint.text_width(txt, family, weight, size)
		MockPaint.text(view, self, txt, Rect2(p.x, p.y, w, size * 1.25), family, weight, size, color, shadow)
		return p.x + w
