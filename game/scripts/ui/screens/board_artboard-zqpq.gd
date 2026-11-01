extends MockScreen
## Glücksrad (Mockup „Glücksrad“, Artboard-zqpq): einmal am Tag kostenlos drehen.
## Zustände wie im Mockup: bereit (DREHEN) → dreht (Animation überspringen) → gewonnen (ABHOLEN).
## Rad, Nabe und Zeiger sind eigene Bilder aus dem Mockup; das Rad dreht das Spiel selbst.
##
## Felder auf dem Rad (k × 45° im Uhrzeigersinn ab oben) und echte Gewinne aus MetaData.WHEEL:
## Das Mockup zeigt 500 Gold · 10 Edelsteine · Held · 1.000 Gold · 5 Edelsteine · 3 Talentsterne ·
## 250 Gold · 20 Edelsteine. Beim Export (tools/mock2game/cfg/wheel.js) sind die Felder an die
## echten Gewinne angepasst: Feld 1 zeigt Energie statt Edelsteinen, „HELD“ wird „×3“ (Heldenkarten),
## „1.000“ wird „100“ und „×3“ Sterne wird „×1“. Die Zuordnung Feld -> Eintrag in MetaData.WHEEL:
const FIELD_TO_WHEEL := [7, 4, 3, 0, 1, 6, 2, 5]
const SPIN_TIME := 4.0
const ROUNDS := 5
## Kurzer Text im Gewinn-Feld (passt in die Breite aus dem Mockup)
## Breite des Gewinn-Felds im Mockup (Text „1.000 Gold“ + Innenabstand)
const WIN_BOX_W := 192.0
const SHORT := {"gold": "Gold", "gems": "Edelsteine", "energy": "Energie", "cards": "Karten", "stars": "Talentstern"}

var phase := "idle"
var angle := 0.0     # Drehung des Rads in Grad (im Uhrzeigersinn)
var prize: Dictionary = {}
var _target := 0.0
var _tween: Tween
var _wheel: WheelLayer
var _win: MockView
var _rays: TextureRect
var _last_tick := 0


func _init(m: MainMenu) -> void:
	super("wheel", m)
	state = phase


func _ready() -> void:
	super()
	_wheel = WheelLayer.new()
	_wheel.board = self
	add_child(_wheel)


func _process(delta: float) -> void:
	super(delta)
	if phase == "spinning":
		_wheel.queue_redraw()
		# Klacken, wenn ein Stift am Zeiger vorbeikommt
		var tick := floori((angle - 22.5) / 45.0)
		if tick != _last_tick:
			_last_tick = tick
			Sfx.play("clack", 0.15)
	if is_instance_valid(_rays):
		_rays.rotation += delta * TAU / 6.0


func bind() -> void:
	var ready := Save.daily_ready("wheel_date")
	match phase:
		"idle":
			set_text("Heute noch 1 kostenlose Drehung", "Heute noch 1 kostenlose Drehung" if ready else "Nächste kostenlose Drehung in " + until_tomorrow())
			var spin := button("spin")
			if spin:
				spin.modulate.a = 1.0 if ready else 0.5
		"done":
			set_text("Nächste kostenlose Drehung in 23 Std. 59 Min.", "Nächste kostenlose Drehung in " + until_tomorrow())


func handle(b: Dictionary) -> bool:
	var on := str(b.get("on", ""))
	var label := str(b.get("label", ""))
	if on == "spin":
		_spin()
		return true
	if on == "skip":
		_finish()
		return true
	if label == "Schließen" or str(b.get("href", "")) == "Main.dc.html":
		# Gewinn ist schon gutgeschrieben, auch wenn man während des Drehens schließt
		menu.close_board(self)
		return true
	return false


func _spin() -> void:
	if phase != "idle":
		return
	if not Save.daily_ready("wheel_date"):
		menu.toast("Heute schon gedreht. Morgen wieder!")
		return
	var idx := randi() % MetaData.WHEEL.size()
	prize = MetaData.WHEEL[idx]
	var field := FIELD_TO_WHEEL.find(idx)
	# Gleich gutschreiben: geht nichts verloren, wenn das Spiel während des Drehens endet
	Save.mark_daily("wheel_date")
	Save.add(str(prize["type"]), int(prize["amount"]))
	# Feld k steht oben unter dem Zeiger, wenn das Rad um -k × 45° gedreht ist
	_target = ROUNDS * 360.0 + fposmod(-field * 45.0, 360.0) + randf_range(-14.0, 14.0)
	_last_tick = floori((angle - 22.5) / 45.0)
	_set_phase("spinning")
	Sfx.play("whoosh")
	_tween = create_tween()
	_tween.tween_property(self, "angle", _target, SPIN_TIME).set_trans(Tween.TRANS_QUART).set_ease(Tween.EASE_OUT)
	_tween.tween_callback(_finish)


func _finish() -> void:
	if phase != "spinning":
		return
	if _tween:
		_tween.kill()
	angle = _target
	_set_phase("done")
	_show_win()
	Sfx.play("win")
	menu.celebrate(MainMenu.reward_icon(prize), "+%d %s" % [int(prize["amount"]), MetaData.REWARD_NAMES.get(prize["type"], "")])


func _set_phase(p: String) -> void:
	phase = p
	_overrides.clear()
	_hidden.clear()
	show_state(p)
	refresh()
	if _wheel:
		_wheel.queue_redraw()


## Feld „GEWONNEN!“ mit Strahlen über dem Rad, passendes Symbol zum Gewinn
func _show_win() -> void:
	_win = open_overlay("win")
	_win.mouse_filter = Control.MOUSE_FILTER_IGNORE   # ABHOLEN darunter bleibt antippbar
	var n := int(prize["amount"])
	var type := str(prize["type"])
	var word: String = SHORT.get(type, "")
	if type == "stars" and n != 1:
		word = "Talentsterne"
	var text := "%s %s" % [num(n), word]
	_win.set_text("1.000 Gold", text)
	_rays = _win.live_image("win_rays")
	# Das Feld wächst im Mockup mit dem Text: bei längeren Gewinnen breiter zeichnen
	var tw := MockFonts.font("Fredoka", 700).get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 30).x
	var extra := maxf(0.0, tw + 2.0 * 26.0 + 6.0 - WIN_BOX_W)
	if extra > 0.0:
		var panel := WidePanel.new()
		panel.texture = _win._bg.texture
		panel.extra = extra
		var r: Array = _win.data["rect"]
		_win.place_at(panel, Rect2(r[0] - extra * 0.5, r[1], r[2] + extra, r[3]))
		_win._bg.visible = false
	# Strahlen hinter das Feld legen
	_win.move_child(_win._live_layer, _win._bg.get_index())
	_win.live_image("icon_" + type, true)
	# Feld springt auf
	var c := _win.to_screen(_win.live_rect("win_rays").get_center())
	_win.pivot_offset = c
	_win.scale = Vector2.ONE * 0.6
	_win.create_tween().tween_property(_win, "scale", Vector2.ONE, 0.35).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


## Zeit bis Mitternacht, wie im Mockup („23 Std. 59 Min.“)
static func until_tomorrow() -> String:
	var t := Time.get_time_dict_from_system()
	var left := 86400 - (int(t["hour"]) * 3600 + int(t["minute"]) * 60 + int(t["second"]))
	return "%d Std. %d Min." % [left / 3600, (left % 3600) / 60]


## Gewinn-Feld in die Breite gezogen: Ränder und Ecken bleiben, nur die Mitte wird gestreckt
class WidePanel:
	extends Control
	var texture: Texture2D
	var extra := 0.0

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE

	func _draw() -> void:
		if texture == null:
			return
		var ts := texture.get_size()
		var k := size.y / ts.y
		var grow := size.x - ts.x * k
		var half := ts.x * 0.5
		var m := ts.x * 0.06
		var left := half - m
		draw_texture_rect_region(texture, Rect2(0, 0, left * k, size.y), Rect2(0, 0, left, ts.y))
		draw_texture_rect_region(texture, Rect2(left * k, 0, 2.0 * m * k + grow, size.y), Rect2(left, 0, 2.0 * m, ts.y))
		draw_texture_rect_region(texture, Rect2(left * k + 2.0 * m * k + grow, 0, left * k, size.y), Rect2(half + m, 0, left, ts.y))


## Rad, Nabe und Zeiger mit den Bildern aus dem Mockup (Grundzustand); das Rad dreht sich
## um seine Mitte, der Zeiger wippt, wenn ein Stift vorbeikommt.
class WheelLayer:
	extends Control
	var board: MockView
	var _tex := {}
	var _src := {}   # Kennung -> [Rechteck des Elements, Rechteck des Bilds] in Mockup-Punkten

	func _ready() -> void:
		set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		mouse_filter = Control.MOUSE_FILTER_IGNORE
		var idle: Dictionary = MockView.layout_of(board.screen).get("states", {}).get("idle", {})
		for l in idle.get("live", []):
			var id := str(l["id"])
			if id in ["wheel", "hub", "pointer"] and str(l.get("img", "")) != "":
				_tex[id] = load("res://ui_mock/%s/%s" % [board.screen, l["img"]])
				var r: Array = l["rect"]
				var ir: Array = l["img_rect"]
				_src[id] = [Rect2(r[0], r[1], r[2], r[3]), Rect2(ir[0], ir[1], ir[2], ir[3])]
		# Frisch geladene Bilder sind im ersten Bild noch nicht bereit
		await get_tree().process_frame
		queue_redraw()

	## Bild so zeichnen, dass es sich um pivot (Mockup-Punkte) um deg Grad dreht
	func _part(id: String, pivot: Vector2, deg: float) -> void:
		if not _tex.has(id):
			return
		var ir: Rect2 = _src[id][1]
		var s := board.s
		draw_set_transform(board.to_screen(pivot), deg_to_rad(deg), Vector2.ONE)
		draw_texture_rect(_tex[id], Rect2((ir.position - pivot) * s, ir.size * s), false)
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)

	func _draw() -> void:
		if _src.has("wheel"):
			var b: Variant = board
			var ang: float = b.angle
			_part("wheel", (_src["wheel"][0] as Rect2).get_center(), ang)
			_part("hub", (_src["hub"][0] as Rect2).get_center() if _src.has("hub") else Vector2.ZERO, 0.0)
			if _src.has("pointer"):
				var pr: Rect2 = _src["pointer"][0]
				var tilt := 0.0
				if str(b.phase) == "spinning":
					# Nach jedem Stift kippt der Zeiger kurz entgegen der Drehrichtung
					var d := fposmod(ang - 22.5, 45.0)
					tilt = -14.0 * maxf(0.0, 1.0 - d / 12.0)
				_part("pointer", Vector2(pr.get_center().x, pr.position.y + 22.0), tilt)
