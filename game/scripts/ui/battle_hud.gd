class_name BattleHud
extends MockView
## Kampfanzeige nach dem Mockup „Kampf · 2 Helden“: Kopfleiste (Pause, Welt/Level, Wellen-Balken,
## Tempo, Gold), Schild-Balken an der Mauer, unten Plasma-Vorrat mit Verbrauch je Held,
## Nachladen, zwei Booster und der Energiekern. An jedem Helden: Stufe, Magazin, „TIPPEN!“,
## wenn die Superfähigkeit bereit ist. Dazu Lebensbalken der Gegner und Schadenszahlen.
## Panels und Knöpfe kommen als Bilder aus dem Mockup (ui_mock/kampf_hud), Balken, Ringe
## und Zahlen zeichnet das Spiel live.

signal pause_pressed
signal tempo_pressed
signal booster_pressed(index: int)

const MAX_FLOATERS := 40
## Farben der Helden für Magazin, Ring und Verbrauchs-Punkt (wie im Mockup: Dusty cyan, Iska lila)
const HERO_COLORS := [Color(0.44, 0.88, 1.0), Color(0.75, 0.54, 1.0), Color(1.0, 0.71, 0.24), Color(0.49, 1.0, 0.54)]
const TEMPO_RECT := Rect2(338, 12, 42, 36)

var battle: Battle
var plasma: PlasmaCore
var _level := 1
var _wave := 0
var _total := 1
var _tempo := 1
var _boosters: Array[String] = []
var _booster_ready: Array[float] = [0.0, 0.0]
var _floaters: Array = []
var _banner := ""
var _banner_t := 0.0
var _t := 0.0
var _layer: HudLayer
## Wo das 3D-Kampfbild in dieser Anzeige liegt (main.gd, gemaltes Schlachtfeld = Mockup-Rahmen)
var world_frame := Rect2()
## Multiplayer: Rangliste der vier Kommandanten, Restzeit, Hinweis auf den Boss (Mockup „Multiplayer · Kampf“)
var _mp := false
var _mp_rows: Array = []
var _mp_left := 0.0
var _mp_tag := ""


func _init() -> void:
	super("kampf_hud")


func _ready() -> void:
	super()
	mouse_filter = Control.MOUSE_FILTER_IGNORE   # Antippen geht ans Kampfbild (Superfähigkeiten)
	_layer = HudLayer.new()
	_layer.hud = self
	place_at(_layer, Rect2(0, 0, W, H))
	button_pressed.connect(_on_button)
	for b in buttons():
		b.mouse_filter = Control.MOUSE_FILTER_STOP
	# Tempo-Feld oben rechts ist im Mockup kein Knopf: unsichtbare Fläche darüber
	var tempo := Control.new()
	tempo.mouse_filter = Control.MOUSE_FILTER_STOP
	tempo.gui_input.connect(func(e: InputEvent) -> void:
		if e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT:
			tempo_pressed.emit())
	place_at(tempo, TEMPO_RECT, true)
	# Booster-Symbole über den Knöpfen (die Knopfbilder zeigen Luftangriff und Medipack)
	_icons = BoosterIcons.new()
	_icons.hud = self
	place_at(_icons, Rect2(0, 0, W, H), true)
	for key in ["−3/s", "−2/s", "80%"]:
		hide_text(key)


func _on_button(b: Dictionary) -> void:
	var label := str(b.get("label", ""))
	if label == "Pause":
		pause_pressed.emit()
	elif label.begins_with("Energiekern"):
		if plasma:
			plasma.try_manual_pull()
	elif label.begins_with("Luftschlag"):
		booster_pressed.emit(0)
	elif label.begins_with("Reparatur"):
		booster_pressed.emit(1)


# --- Schnittstelle für main.gd (wie die alte Anzeige) -------------------------------------

func reset(level: int, total_waves: int) -> void:
	_floaters.clear()
	_level = level
	_wave = 0
	_total = total_waves
	_update_title()
	set_tempo(1)


func set_wave(level: int, wave: int, total: int) -> void:
	_level = level
	_wave = wave
	_total = total
	_update_title()
	show_banner("Letzte Welle!" if wave == total else "Welle %d" % wave)


func set_mp(on: bool) -> void:
	_mp = on
	_mp_rows = []
	_mp_left = MpData.MATCH_TIME
	_mp_tag = "Boss in Welle %d" % MpData.BOSS_WAVE
	_update_title()


func set_mp_state(rows: Array, left: float, wave: int) -> void:
	_mp_rows = rows
	_mp_left = left
	if wave < MpData.BOSS_WAVE:
		_mp_tag = "Boss in Welle %d" % MpData.BOSS_WAVE
	elif battle and battle.bosses > 0:
		_mp_tag = "Boss besiegt!"
	else:
		_mp_tag = "Der Boss ist da!"


func _update_title() -> void:
	if _mp:
		set_text("Schleim-Welt · Level 7", "%s · Station %d" % [GameData.world_name(_level), _level])
	else:
		set_text("Schleim-Welt · Level 7", "%s · Level %d" % [GameData.world_name(_level), _level])
	set_text("Welle 3/7", "Welle %d/%d" % [_wave, _total])


func set_xp(_xp: int, _needed: int) -> void:
	pass


func set_fence(hp: float, max_hp: float) -> void:
	set_text("Schild 1.462 / 1.700", "Schild %s / %s" % [MockScreen.num(mini(int(ceil(hp)), int(round(max_hp)))), MockScreen.num(int(round(max_hp)))])


func set_boosters(ids: Array[String]) -> void:
	_boosters = ids
	if _icons:
		_icons.queue_redraw()
	var left := button("Luftschlag bereit")
	var right := button("Reparatur bereit")
	if left:
		left.visible = ids.size() > 0
	if right:
		right.visible = ids.size() > 1


var _booster_tex := {}
var _icons: Control


## Symbol eines Boosters (Vorlage_Raw/Icons_v1, ui/boosters)
func booster_icon(id: String) -> Texture2D:
	if not _booster_tex.has(id):
		var f := "res://ui/boosters/%s.webp" % id
		_booster_tex[id] = load(f) if ResourceLoader.exists(f) else null
	return _booster_tex[id]


func set_booster_ready(i: int, ratio: float) -> void:
	if i < _booster_ready.size():
		_booster_ready[i] = ratio


func set_tempo(tempo: int) -> void:
	_tempo = tempo
	set_text("x1", "x%d" % tempo)


func set_next_wave(_text: String) -> void:
	pass


func show_banner(text: String) -> void:
	_banner = text
	_banner_t = 1.6


func add_floater(pos: Vector3, amount: float, crit: bool) -> void:
	if amount < 1.0:
		return
	if _floaters.size() >= MAX_FLOATERS:
		_floaters.pop_front()
	_floaters.append({"pos": pos + Vector3(randf_range(-0.3, 0.3), 0.2, 0),
		"text": ("KRIT %d!" if crit else "%d") % int(round(amount)), "crit": crit, "t": 0.0})


func _process(delta: float) -> void:
	_t += delta
	for f in _floaters:
		f["t"] = float(f["t"]) + delta
	_floaters = _floaters.filter(func(f: Dictionary) -> bool: return float(f["t"]) < 0.8)
	_banner_t = maxf(0.0, _banner_t - delta)
	if plasma and battle and battle.ammo:
		set_text("52", str(battle.ammo.total()))
		set_text("/ 80", "/ %d" % battle.ammo.cap)
		set_text("+4", _dec(plasma.rate_per_sec()))
		var use := 0.0
		for h in battle.heroes:
			use += _hero_use(h)
		set_text("−5/s", "−%s/s" % _dec(use))
	set_text("480", MockScreen.num(Save.gold()))
	_layer.queue_redraw()


## Plasma pro Sekunde, das ein Held beim Dauerfeuern verbraucht
static func _hero_use(h: Hero) -> float:
	var per_shot := float(h.ammo_cost()) / maxf(1.0, float(h.mag_size()))
	var cycle := h.interval() * h.mag_size() + h.reload_time()
	return per_shot * h.mag_size() / maxf(0.1, cycle)


static func _gray(c: Color, a: float) -> Color:
	var l := c.get_luminance()
	var g := c.lerp(Color(l, l, l), 0.8)
	g.a = c.a * a
	return g


static func _dec(v: float) -> String:
	var r := roundf(v * 10.0) / 10.0
	if absf(r - roundf(r)) < 0.05:
		return str(int(roundf(r)))
	return ("%.1f" % r).replace(".", ",")


## Zeichnet alles, was sich bewegt oder Werte zeigt
class HudLayer:
	extends Control
	var hud: BattleHud

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE
		for id in ["badge", "tippen"]:
			_tex(id)
		await get_tree().process_frame
		queue_redraw()

	var _cache := {}

	func _tex(id: String) -> Texture2D:
		if not _cache.has(id):
			var l: Dictionary = hud._live_info.get(id, {})
			_cache[id] = load("res://ui_mock/kampf_hud/" + str(l["img"])) if str(l.get("img", "")) != "" else null
		return _cache[id]

	func _s(v: float) -> float:
		return v * hud.s

	func _p(v: Vector2) -> Vector2:
		return v * hud.s

	## Abgerundeter Balken mit Verlauf (Spur bleibt im Hintergrundbild, hier nur die Füllung)
	func _bar(id: String, ratio: float, c1: Color, c2: Color, radius := 0.0) -> void:
		var r := hud.live_rect(id)
		if r.size == Vector2.ZERO:
			return
		var full := _orig_width(id)
		var w := full * clampf(ratio, 0.0, 1.0)
		if w < 0.5:
			return
		var rr := Rect2(_p(r.position), Vector2(_s(w), _s(r.size.y)))
		var cols := PackedColorArray([c1, c1.lerp(c2, ratio), c1.lerp(c2, ratio), c1])
		var pts := PackedVector2Array([rr.position, Vector2(rr.end.x, rr.position.y), rr.end, Vector2(rr.position.x, rr.end.y)])
		draw_polygon(pts, cols)
		if radius > 0.0:
			pass

	## Volle Breite eines Balkens (im Mockup ist er nur teilweise gefüllt)
	func _orig_width(id: String) -> float:
		match id:
			"wave_fill":
				return 272.0
			"shield_fill":
				return 132.0
			"plasma_fill":
				return 100.0
		return hud.live_rect(id).size.x

	func _draw() -> void:
		var b := hud.battle
		if b == null:
			return
		# Wellen-Fortschritt, Schild, Plasma
		_bar("wave_fill", float(hud._wave) / maxf(1.0, hud._total), Color("ff9f1c"), Color("ffe27a"))
		var fr := b.fence_hp / maxf(1.0, b.fence_max)
		var low := fr <= 0.35
		_bar("shield_fill", fr, Color("ff5a5a") if low else Color("7dff8a"), Color(1.0, 0.35, 0.35, 0.8) if low else Color(0.49, 1.0, 0.54, 0.8))
		if b.ammo:
			var pr := float(b.ammo.total()) / maxf(1.0, b.ammo.cap)
			var pf := hud.live_rect("plasma_fill")
			var w := _s(100.0 * pr)
			if w > 0.5:
				var sb := StyleBoxFlat.new()
				sb.bg_color = Color("7dff8a")
				sb.set_corner_radius_all(roundi(_s(3)))
				draw_style_box(sb, Rect2(_p(pf.position), Vector2(w, _s(6))))
		_draw_usage(b)
		_draw_core()
		_draw_boosters()
		_draw_enemies(b)
		_draw_heroes(b)
		_draw_floaters(b)
		if hud._mp:
			_draw_mp()
		_draw_banner()

	## Multiplayer-Rangliste links oben, Restzeit und Boss-Hinweis rechts (Maße aus dem Mockup)
	func _draw_mp() -> void:
		var s := hud.s
		var y := 132.0
		for e in hud._mp_rows:
			var me: bool = e.get("me", false)
			var out: bool = e.get("out", false)
			var r := Rect2(8, y, 118, 26)
			var top := Color("#4fb8ff") if me else Color(1.0, 0.416, 0.478, 0.92)
			var bot := Color("#2a6ad8") if me else Color(0.85, 0.188, 0.29, 0.92)
			var sh := Color("#14408a") if me else Color("#7a1020")
			var a := 0.55 if out else 1.0
			if out:
				top = BattleHud._gray(top, a)
				bot = BattleHud._gray(bot, a)
				sh = BattleHud._gray(sh, a)
			MockPaint.rrect(self, Rect2((r.position + Vector2(0, 3)) * s, r.size * s), 7 * s, sh)
			MockPaint.rrect(self, Rect2(r.position * s, r.size * s), 7 * s, top, bot)
			var tc := "rgba(255, 247, 234, %.2f)" % a
			MockPaint.text(hud, self, str(e["place"]), Rect2(11, y + 6, 10, 14), "Fredoka", 700, 10, tc, "0px 1px 0px #1a0f3a")
			MpPaint.avatar(self, Vector2(32, y + 13) * s, 22 * s, str(e["hero"]), Color(1, 1, 1, a), 2 * s, out)
			var kills := str(int(e["kills"]))
			var kw := MockPaint.text_width(kills, "Fredoka", 700, 12)
			var kx := 126.0 - 5.0 - kw
			MockPaint.text(hud, self, kills, Rect2(kx, y + 5, kw, 16), "Fredoka", 700, 12, tc)
			MpPaint.skull(self, Rect2((kx - 14) * s, (y + 7) * s, 12 * s, 12 * s))
			var name_w := kx - 16.0 - 47.0
			var name := _fit_text(str(e["name"]), name_w, 9)
			if out:
				var ly := y + 3.0
				_left_text(name, Vector2(47, ly), name_w, 9, tc)
				_left_text("RAUS · %s" % MpData.time_text(float(e["secs"])), Vector2(47, ly + 11), name_w, 7, "rgba(255, 208, 214, %.2f)" % a, "Nunito", 800)
			else:
				_left_text(name, Vector2(47, y + 8), name_w, 9, tc)
			y += 29.0
		# Restzeit
		var t := MpData.time_text(hud._mp_left)
		var tw := MockPaint.text_width(t, "Fredoka", 700, 15)
		var pill := Rect2(380.0 - (6 + 16 + 5 + tw + 10), 136, 6 + 16 + 5 + tw + 10, 27)
		var pr := Rect2(pill.position * s, pill.size * s)
		MockPaint.rrect(self, pr, 12 * s, Color(10 / 255.0, 6 / 255.0, 30 / 255.0, 0.7))
		MockPaint.border(self, pr, 12 * s, Color(111 / 255.0, 224 / 255.0, 1.0, 0.45), 1.5 * s)
		MpPaint.clock(self, Rect2((pill.position + Vector2(6, 5.5)) * s, Vector2(16, 16) * s))
		MockPaint.text(hud, self, t, Rect2(pill.position.x + 27, 139, tw, 20), "Fredoka", 700, 15, "rgb(255, 247, 234)")
		# Boss-Hinweis
		var tag := hud._mp_tag
		var gw := MockPaint.text_width(tag, "Nunito", 800, 10)
		var tr := Rect2(380.0 - (gw + 16), 168, gw + 16, 18)
		MockPaint.rrect(self, Rect2(tr.position * s, tr.size * s), 8 * s, Color(1.0, 0.416, 0.478, 0.85))
		MockPaint.text(hud, self, tag, Rect2(tr.position.x + 8, 170, gw, 14), "Nunito", 800, 10, "rgb(255, 247, 234)")

	## Text linksbündig ab p (Mockup-Punkte), höchstens w breit
	func _left_text(txt: String, p: Vector2, w: float, size: float, color: String, family := "Fredoka", weight := 700) -> void:
		var tw := MockPaint.text_width(txt, family, weight, size)
		MockPaint.text(hud, self, txt, Rect2(p.x, p.y, minf(tw, w), size * 1.2), family, weight, size, color)

	## Kürzt einen Namen mit „…“, bis er passt (text-overflow: ellipsis)
	func _fit_text(txt: String, w: float, size: float) -> String:
		if MockPaint.text_width(txt, "Fredoka", 700, size) <= w:
			return txt
		var t := txt
		while t.length() > 1 and MockPaint.text_width(t + "…", "Fredoka", 700, size) > w:
			t = t.left(t.length() - 1)
		return t + "…"

	## Verbrauch je Held: farbiger Punkt und „−x/s“
	func _draw_usage(b: Battle) -> void:
		var d0 := hud.live_rect("use_dot")
		if d0.size == Vector2.ZERO:
			return
		var font := MockFonts.font("Fredoka", 700)
		var fs := roundi(_s(13))
		var n := mini(b.heroes.size(), 3)
		var step := 17.0
		var top := d0.get_center().y - (n - 1) * step * 0.5 + (step * 0.5 if n == 1 else 0.0)
		if n == 3:
			top = d0.get_center().y - 8.0
			step = 12.0
			fs = roundi(_s(11))
		for i in n:
			var h: Hero = b.heroes[i]
			var c := Vector2(d0.get_center().x, top + i * step)
			draw_circle(_p(c), _s(4.5), Color.WHITE)
			draw_circle(_p(c), _s(3.5), HERO_COLORS[i % HERO_COLORS.size()])
			var txt := "−%s/s" % BattleHud._dec(BattleHud._hero_use(h))
			draw_string(font, _p(c + Vector2(9.0, 4.5)), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color("ffb53d"))

	## Energiekern: Ladering, Prozent, Leuchten wenn voll
	func _draw_core() -> void:
		var pl := hud.plasma
		if pl == null:
			return
		var r := hud.live_rect("core_ring")
		var c := _p(r.get_center())
		var ratio := pl.core_ratio()
		var rad := _s(r.size.x * 0.5 - 2.5)
		if pl.core_ready():
			var a := 0.35 + 0.25 * sin(hud._t * 6.0)
			draw_circle(c, rad + _s(10), Color(0.44, 0.88, 1.0, a * 0.5))
		draw_arc(c, rad, -PI * 0.5, -PI * 0.5 + TAU * ratio, 48, Color("6fe0ff"), _s(5), true)
		var font := MockFonts.font("Fredoka", 700)
		var fs := roundi(_s(10.3))
		var txt := "%d%%" % roundi(ratio * 100.0)
		var tw := font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		draw_string(font, c + Vector2(-tw * 0.5, _s(18)), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color.WHITE)
		if pl.core_ready():
			var t2 := "TIPPEN!"
			var f2 := roundi(_s(11))
			var w2 := font.get_string_size(t2, HORIZONTAL_ALIGNMENT_LEFT, -1, f2).x
			var pill := Rect2(c + Vector2(-w2 * 0.5 - _s(8), -rad - _s(26)), Vector2(w2 + _s(16), _s(17)))
			var sb := StyleBoxFlat.new()
			sb.bg_color = Color("ffd34d")
			sb.set_corner_radius_all(roundi(_s(8)))
			draw_style_box(sb, pill)
			draw_string(font, pill.position + Vector2(_s(8), _s(13)), t2, HORIZONTAL_ALIGNMENT_LEFT, -1, f2, Color("5a2400"))

	## Booster: dunkler Kreisausschnitt, solange sie laden
	func _draw_boosters() -> void:
		for i in 2:
			var btn := hud.button("Luftschlag bereit" if i == 0 else "Reparatur bereit")
			if btn == null or not btn.visible:
				continue
			var ratio: float = hud._booster_ready[i]
			if ratio >= 1.0:
				continue
			var r: Array = btn.info["rect"]
			var c := _p(Vector2(r[0] + r[2] * 0.5, r[1] + r[3] * 0.5))
			var rad := _s(r[2] * 0.5)
			var pts := PackedVector2Array([c])
			var steps := 32
			for k in steps + 1:
				var a := -PI * 0.5 + TAU * ratio + TAU * (1.0 - ratio) * k / steps
				pts.append(c + Vector2.from_angle(a) * rad)
			if pts.size() > 3:
				draw_colored_polygon(pts, Color(0.02, 0.02, 0.1, 0.62))
			draw_arc(c, rad - _s(1.5), -PI * 0.5, -PI * 0.5 + TAU * ratio, 40, Color("ffd34d"), _s(3), true)

	func _draw_enemies(b: Battle) -> void:
		var cam := b.camera
		if cam == null:
			return
		for e in b.enemies:
			if not is_instance_valid(e) or not e.alive:
				continue
			if e.hp >= e.max_hp and not e.is_boss():
				continue
			var p3 := e.global_position + Vector3(0, e.top_height(), 0)
			if cam.is_position_behind(p3):
				continue
			var p := _screen(cam, p3)
			var w := _s(160.0) if e.is_boss() else _s(24.0)
			var h := _s(6.0) if e.is_boss() else _s(4.0)
			var r := Rect2(p.x - w * 0.5, p.y - h - _s(4), w, h)
			var sb := StyleBoxFlat.new()
			sb.bg_color = Color(0, 0, 0, 0.55)
			sb.set_corner_radius_all(roundi(h * 0.5))
			draw_style_box(sb, r)
			var ratio := clampf(e.hp / e.max_hp, 0.0, 1.0)
			var col := Color("ff6fd2") if e.is_boss() else (Color("7dff8a") if ratio > 0.5 else Color("ffd34d"))
			var sf := StyleBoxFlat.new()
			sf.bg_color = col
			sf.set_corner_radius_all(roundi(h * 0.5))
			draw_style_box(sf, Rect2(r.position, Vector2(w * ratio, h)))

	## Kampfbild-Punkt -> Punkt in dieser Ebene (beide decken dieselbe Fläche ab)
	func _screen(cam: Camera3D, p3: Vector3) -> Vector2:
		var vp := cam.get_viewport()
		var vs := Vector2(vp.get_visible_rect().size)
		var fr := hud.world_frame if hud.world_frame.size != Vector2.ZERO else Rect2(Vector2.ZERO, hud.size)
		return cam.unproject_position(p3) / vs * fr.size + fr.position - hud.off

	## Ring, Stufe, Magazin und „TIPPEN!“ an jedem Helden
	func _draw_heroes(b: Battle) -> void:
		var cam := b.camera
		if cam == null:
			return
		var font := MockFonts.font("Fredoka", 700)
		for i in b.heroes.size():
			var h: Hero = b.heroes[i]
			if not is_instance_valid(h):
				continue
			var col: Color = HERO_COLORS[i % HERO_COLORS.size()]
			var feet := _screen(cam, h.global_position)
			# Ring unter den Füßen
			draw_set_transform(feet + Vector2(0, -_s(2)), 0.0, Vector2(1.0, 0.32))
			draw_arc(Vector2.ZERO, _s(28), 0.0, TAU, 40, Color(col, 0.85), _s(3) / 0.32 * 0.5, true)
			draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
			# Stufe (Abzeichen aus dem Mockup) links unten am Helden
			var badge := _tex("badge")
			var bc := feet + _p(Vector2(-22, 10))
			if badge:
				var ir: Array = hud._live_info["badge"]["img_rect"]
				var bs := _p(Vector2(ir[2], ir[3]))
				draw_texture_rect(badge, Rect2(bc - bs * 0.5, bs), false)
			var lvl := str(Save.hero_level(h.id))
			var fs := roundi(_s(11))
			var tw := font.get_string_size(lvl, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
			draw_string(font, bc + Vector2(-tw * 0.5, _s(4)), lvl, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color.WHITE)
			# Magazin
			var pill := Rect2(feet + _p(Vector2(-43, 20)), _p(Vector2(86, 18)))
			var sb := StyleBoxFlat.new()
			sb.bg_color = Color(0.04, 0.03, 0.12, 0.85)
			sb.set_corner_radius_all(roundi(_s(8)))
			sb.set_border_width_all(maxi(1, roundi(_s(1))))
			sb.border_color = Color(col, 0.9)
			draw_style_box(sb, pill)
			var n := h.mag_size()
			var have := h.magazine.size()
			var ratio := float(have) / maxf(1.0, n)
			if h.reloading:
				ratio = 1.0 - h.reload_left / maxf(0.01, h.reload_total)
			var inner := pill.grow(-_s(1))
			if ratio > 0.0:
				var sf := StyleBoxFlat.new()
				sf.bg_color = Color(col, 0.95 if not h.reloading else 0.5)
				sf.set_corner_radius_all(roundi(_s(7)))
				draw_style_box(sf, Rect2(inner.position, Vector2(maxf(_s(10), inner.size.x * ratio), inner.size.y)))
			var mt := "%d / %d" % [have, n]
			if h.waiting_for_ammo:
				mt = "Kein Plasma"
			var mfs := roundi(_s(10))
			var mw := font.get_string_size(mt, HORIZONTAL_ALIGNMENT_LEFT, -1, mfs).x
			draw_string(font, pill.get_center() + Vector2(-mw * 0.5, _s(3.5)), mt, HORIZONTAL_ALIGNMENT_LEFT, -1, mfs, Color.WHITE)
			# Superfähigkeit bereit
			if h.ult_ready():
				var head := _screen(cam, h.global_position + Vector3(0, h.top_height() + 0.2, 0))
				var tp := _tex("tippen")
				var bob := sin(hud._t * 5.0) * _s(2)
				if tp:
					var ir2: Array = hud._live_info["tippen"]["img_rect"]
					var ts := _p(Vector2(ir2[2], ir2[3]))
					draw_texture_rect(tp, Rect2(head - Vector2(ts.x * 0.5, ts.y) + Vector2(0, bob), ts), false)
				var t3 := "TIPPEN!"
				var f3 := roundi(_s(12))
				var w3 := font.get_string_size(t3, HORIZONTAL_ALIGNMENT_LEFT, -1, f3).x
				draw_string(font, head + Vector2(-w3 * 0.5, -_s(7) + bob), t3, HORIZONTAL_ALIGNMENT_LEFT, -1, f3, Color("5a2400"))

	## Schadenszahlen: weiß mit dunklem Rand, Krit groß in Gold
	func _draw_floaters(b: Battle) -> void:
		var cam := b.camera
		var font := MockFonts.font("Fredoka", 700)
		for f in hud._floaters:
			var t: float = f["t"]
			var p3: Vector3 = f["pos"] + Vector3(0, t * 1.6, 0)
			if cam.is_position_behind(p3):
				continue
			var p := _screen(cam, p3)
			var crit: bool = f["crit"]
			var fs := roundi(_s(19.0 if crit else 13.0))
			var a := clampf(1.7 - t * 2.0, 0.0, 1.0)
			var txt: String = f["text"]
			var tw := font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
			var pos := p + Vector2(-tw * 0.5, 0)
			draw_string_outline(font, pos, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, roundi(_s(4)), Color(0.35, 0.1, 0.0, a) if crit else Color(0.05, 0.03, 0.15, a))
			draw_string(font, pos, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(1.0, 0.78, 0.25, a) if crit else Color(1, 1, 1, a))

	## Hinweis oben (Welle, Energiekern …) als Schild wie „Achtung: Gegner am Schild!“
	func _draw_banner() -> void:
		if hud._banner_t <= 0.0:
			return
		var a := clampf(hud._banner_t * 2.0, 0.0, 1.0)
		var font := MockFonts.font("Fredoka", 700)
		var fs := roundi(_s(14))
		var tw := font.get_string_size(hud._banner, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var r := Rect2(_p(Vector2(195, 96)) - Vector2(tw * 0.5 + _s(16), 0), Vector2(tw + _s(32), _s(30)))
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color(0.55, 0.08, 0.14, 0.9 * a)
		sb.set_corner_radius_all(roundi(_s(10)))
		sb.set_border_width_all(maxi(1, roundi(_s(2))))
		sb.border_color = Color(1.0, 0.6, 0.6, a)
		draw_style_box(sb, r)
		draw_string(font, r.position + Vector2(_s(16), _s(20)), hud._banner, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(1, 1, 1, a))


## Symbol des mitgenommenen Boosters auf dem Knopf, wenn es nicht Luftangriff (links) bzw. Medipack (rechts) ist
class BoosterIcons:
	extends Control
	var hud: BattleHud

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE

	func _process(_delta: float) -> void:
		# nur neu zeichnen, wenn ein anderer Booster als die beiden im Knopfbild mitgenommen ist (Ladekreis läuft)
		if hud._boosters.size() > 0 and (hud._boosters[0] != "luftangriff" or (hud._boosters.size() > 1 and hud._boosters[1] != "medipack")):
			queue_redraw()

	func _draw() -> void:
		for i in mini(2, hud._boosters.size()):
			var btn := hud.button("Luftschlag bereit" if i == 0 else "Reparatur bereit")
			if btn == null or not btn.visible or hud._boosters[i] == ["luftangriff", "medipack"][i]:
				continue
			var tex := hud.booster_icon(hud._boosters[i])
			if tex == null:
				continue
			var r: Array = btn.info["rect"]
			var c := Vector2(r[0] + r[2] * 0.5, r[1] + r[3] * 0.5) * hud.s
			var inner: float = r[2] * 0.5 * 0.83 * hud.s
			draw_circle(c, inner, Color8(62, 58, 128))
			draw_circle(c + Vector2(0, -inner * 0.35), inner * 0.62, Color(1, 1, 1, 0.12))
			var isz: float = r[2] * 0.72 * hud.s
			draw_texture_rect(tex, Rect2(c - Vector2(isz, isz) * 0.5, Vector2(isz, isz)), false)
			# Ladekreis wie in HudLayer._draw_boosters, hier über dem Symbol
			var ratio: float = hud._booster_ready[i]
			if ratio >= 1.0:
				continue
			var rad: float = r[2] * 0.5 * hud.s
			var pts := PackedVector2Array([c])
			for k in 33:
				pts.append(c + Vector2.from_angle(-PI * 0.5 + TAU * ratio + TAU * (1.0 - ratio) * k / 32.0) * rad)
			draw_colored_polygon(pts, Color(0.02, 0.02, 0.1, 0.62))
			draw_arc(c, rad - 1.5 * hud.s, -PI * 0.5, -PI * 0.5 + TAU * ratio, 40, Color("ffd34d"), 3.0 * hud.s, true)
