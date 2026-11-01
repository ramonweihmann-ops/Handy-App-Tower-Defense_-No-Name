class_name Hud
extends Control
## Anzeige über dem Schlachtfeld: Welle, Erfahrung, Schild, Tempo, Magazine der Helden,
## Lebensbalken der Gegner und Schadenszahlen.

signal pause_pressed
signal tempo_pressed
signal booster_pressed(index: int)

const MAX_FLOATERS := 40

var battle: Battle
var plasma: PlasmaCore
var _wave_label: Label
var _xp_bar: ProgressBar
var _xp_label: Label
var _fence_bar: ProgressBar
var _fence_label: Label
var _tempo_btn: Button
var _next_label: Label
var _booster_buttons: Array[BoosterButton] = []
var _fence_shown := -1
var _fence_max_shown := -1
var _fence_low := false
var _fence_fill: StyleBoxFlat
var _floaters: Array = []
var _banner: Label
var _banner_t := 0.0
var _font: Font
var _t := 0.0


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_font = ThemeDB.fallback_font
	_build()


func _build() -> void:
	var top := HBoxContainer.new()
	top.set_anchors_preset(Control.PRESET_TOP_WIDE)
	top.offset_left = 14
	top.offset_right = -14
	top.offset_top = 14
	top.offset_bottom = 90
	top.add_theme_constant_override("separation", 12)
	top.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(top)

	var pause := UiKit.secondary(UiKit.button("II", func() -> void: pause_pressed.emit(), 72))
	pause.custom_minimum_size = Vector2(72, 72)
	top.add_child(pause)

	var mid := VBoxContainer.new()
	mid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	mid.add_theme_constant_override("separation", 4)
	mid.mouse_filter = Control.MOUSE_FILTER_IGNORE
	top.add_child(mid)
	_wave_label = UiKit.label("Level 1 · Welle 1/6", 26)
	mid.add_child(_wave_label)
	_xp_bar = ProgressBar.new()
	_xp_bar.show_percentage = false
	_xp_bar.custom_minimum_size = Vector2(0, 26)
	_xp_bar.add_theme_stylebox_override("fill", UiKit.box(Color(0.35, 1.0, 0.55), 8))
	_xp_bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	mid.add_child(_xp_bar)
	_xp_label = UiKit.label("0/8", 18)
	_xp_label.set_anchors_preset(Control.PRESET_FULL_RECT)
	_xp_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_xp_bar.add_child(_xp_label)
	_next_label = UiKit.wrap_label("", 18, Color(0.85, 0.75, 1.0))
	mid.add_child(_next_label)

	_tempo_btn = UiKit.button("x1", func() -> void: tempo_pressed.emit(), 72)
	_tempo_btn.custom_minimum_size = Vector2(72, 72)
	top.add_child(_tempo_btn)

	var bottom := HBoxContainer.new()
	bottom.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	bottom.offset_left = 18
	bottom.offset_right = -18
	bottom.offset_top = -46
	bottom.offset_bottom = -12
	bottom.add_theme_constant_override("separation", 10)
	bottom.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bottom)
	bottom.add_child(UiKit.label("Schild", 20, UiKit.C_ACCENT))
	_fence_bar = ProgressBar.new()
	_fence_bar.show_percentage = false
	_fence_bar.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_fence_bar.custom_minimum_size = Vector2(0, 24)
	_fence_bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bottom.add_child(_fence_bar)
	_fence_label = UiKit.label("1000/1000", 17)
	_fence_label.set_anchors_preset(Control.PRESET_FULL_RECT)
	_fence_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_fence_bar.add_child(_fence_label)

	# Booster-Knöpfe links und rechts über dem Schild
	for i in MetaData.BOOSTER_SLOTS:
		var b := BoosterButton.new()
		b.custom_minimum_size = Vector2(96, 96)
		b.size = Vector2(96, 96)
		b.anchor_top = 1.0
		b.anchor_bottom = 1.0
		b.anchor_left = 0.0 if i == 0 else 1.0
		b.anchor_right = b.anchor_left
		b.offset_left = 16.0 if i == 0 else -112.0
		b.offset_right = b.offset_left + 96.0
		b.offset_top = -160.0
		b.offset_bottom = -64.0
		var idx := i
		b.pressed.connect(func() -> void: booster_pressed.emit(idx))
		UiKit.add_pop(b)
		add_child(b)
		_booster_buttons.append(b)

	_banner = UiKit.label("", 56, UiKit.C_GOLD)
	_banner.set_anchors_preset(Control.PRESET_CENTER)
	_banner.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_banner.grow_vertical = Control.GROW_DIRECTION_BOTH
	_banner.add_theme_constant_override("outline_size", 12)
	_banner.modulate.a = 0.0
	add_child(_banner)


# --- Anzeigen setzen ------------------------------------------------------

func reset(level: int, total_waves: int) -> void:
	_floaters.clear()
	_wave_label.text = "Level %d · Welle 0/%d" % [level, total_waves]
	set_tempo(1)


func set_wave(level: int, wave: int, total: int) -> void:
	_wave_label.text = "Level %d · Welle %d/%d" % [level, wave, total]
	if wave == total:
		show_banner("Letzte Welle!")
	else:
		show_banner("Welle %d" % wave)


func set_xp(xp: int, needed: int) -> void:
	_xp_bar.max_value = needed
	_xp_bar.value = xp
	_xp_label.text = "%d/%d" % [xp, needed]


func set_fence(hp: float, max_hp: float) -> void:
	var shown := int(ceil(hp))
	if shown == _fence_shown and int(max_hp) == _fence_max_shown:
		return
	_fence_shown = shown
	_fence_max_shown = int(max_hp)
	_fence_bar.max_value = max_hp
	_fence_bar.value = hp
	_fence_label.text = "%d/%d" % [shown, int(max_hp)]
	var low := hp / maxf(1.0, max_hp) <= 0.35
	if low != _fence_low or _fence_fill == null:
		_fence_low = low
		_fence_fill = UiKit.box(Color(1.0, 0.35, 0.3) if low else UiKit.C_ACCENT, 8)
		_fence_bar.add_theme_stylebox_override("fill", _fence_fill)


## Zeigt die ausgerüsteten Booster (leer = Knopf ausblenden).
func set_boosters(ids: Array[String]) -> void:
	for i in _booster_buttons.size():
		var b := _booster_buttons[i]
		b.visible = i < ids.size()
		if b.visible:
			b.kind = String(MetaData.BOOSTERS[ids[i]]["icon"])
			b.title = String(MetaData.BOOSTERS[ids[i]]["title"])


func set_booster_ready(i: int, ratio: float) -> void:
	if i < _booster_buttons.size():
		_booster_buttons[i].ready_ratio = ratio


func set_tempo(tempo: int) -> void:
	_tempo_btn.text = "x%d" % tempo


func set_next_wave(text: String) -> void:
	_next_label.text = text


func show_banner(text: String) -> void:
	_banner.text = text
	_banner_t = 1.6


func add_floater(pos: Vector3, amount: float, crit: bool) -> void:
	if amount < 1.0:
		return
	if _floaters.size() >= MAX_FLOATERS:
		_floaters.pop_front()
	_floaters.append({
		"pos": pos + Vector3(randf_range(-0.3, 0.3), 0.2, 0),
		"text": str(int(round(amount))) + ("!" if crit else ""),
		"color": Color(1.0, 0.85, 0.25) if crit else Color(1, 1, 1),
		"size": 30 if crit else 22,
		"t": 0.0,
	})


# --- Zeichnen -------------------------------------------------------------

func _process(delta: float) -> void:
	_t += delta
	for f in _floaters:
		f["t"] = float(f["t"]) + delta
	_floaters = _floaters.filter(func(f: Dictionary) -> bool: return float(f["t"]) < 0.75)
	if _banner_t > 0.0:
		_banner_t -= delta
		_banner.modulate.a = clampf(_banner_t * 2.0, 0.0, 1.0)
		_banner.position = (size - _banner.size) * Vector2(0.5, 0.38)
	queue_redraw()


func _draw() -> void:
	if battle == null or battle.camera == null:
		return
	var cam := battle.camera
	for e in battle.enemies:
		if not is_instance_valid(e) or not e.alive:
			continue
		if e.hp >= e.max_hp and not e.is_boss():
			continue
		var p3 := e.global_position + Vector3(0, e.top_height(), 0)
		if cam.is_position_behind(p3):
			continue
		var p := cam.unproject_position(p3)
		var w := 170.0 if e.is_boss() else 44.0
		var h := 12.0 if e.is_boss() else 6.0
		var r := Rect2(p.x - w * 0.5, p.y - h * 0.5, w, h)
		draw_rect(r.grow(2.0), Color(0, 0, 0, 0.7))
		var ratio := clampf(e.hp / e.max_hp, 0.0, 1.0)
		var col := Color(1.0, 0.3, 0.85) if e.is_boss() else Color(1.0, 0.3, 0.25)
		draw_rect(Rect2(r.position, Vector2(w * ratio, h)), col)
		if e.is_boss():
			_text(Vector2(p.x, p.y - 14), e.data["name"], 22, Color(1, 0.8, 0.95))
	for hero in battle.heroes:
		if not is_instance_valid(hero):
			continue
		var p3 := hero.global_position + Vector3(0, hero.top_height(), 0)
		var p := cam.unproject_position(p3)
		var n := hero.mag_size()
		var have := hero.magazine.size()
		if n <= 8:
			var pw := 9.0
			var gap := 3.0
			var total_w := n * pw + (n - 1) * gap
			for i in n:
				var x := p.x - total_w * 0.5 + i * (pw + gap)
				var rr := Rect2(x, p.y - 8.0, pw, 16.0)
				draw_rect(rr.grow(1.5), Color(0, 0, 0, 0.6))
				if i < have:
					var type: String = hero.magazine[i]
					draw_rect(rr, AmmoBall.COLORS.get(type, UiKit.C_GOLD))
				else:
					draw_rect(rr, Color(0.25, 0.27, 0.33))
		else:
			var w := 70.0
			var r := Rect2(p.x - w * 0.5, p.y - 6.0, w, 12.0)
			draw_rect(r.grow(1.5), Color(0, 0, 0, 0.6))
			draw_rect(Rect2(r.position, Vector2(w * float(have) / n, 12.0)), UiKit.C_GOLD)
		if hero.reloading:
			var ratio := 1.0 - hero.reload_left / maxf(0.01, hero.reload_total)
			var rr := Rect2(p.x - 32.0, p.y + 12.0, 64.0, 6.0)
			draw_rect(rr.grow(1.0), Color(0, 0, 0, 0.6))
			draw_rect(Rect2(rr.position, Vector2(64.0 * ratio, 6.0)), UiKit.C_ACCENT)
		elif hero.waiting_for_ammo:
			var a := 0.55 + 0.45 * sin(_t * 9.0)
			_text(Vector2(p.x, p.y - 16.0), "Keine Munition!", 19, Color(1.0, 0.4, 0.35, a))
	for f in _floaters:
		var t: float = f["t"]
		var pos3: Vector3 = f["pos"] + Vector3(0, t * 1.6, 0)
		if cam.is_position_behind(pos3):
			continue
		var p := cam.unproject_position(pos3)
		var c: Color = f["color"]
		c.a = clampf(1.6 - t * 2.0, 0.0, 1.0)
		_text(p, f["text"], int(f["size"]), c)


func _text(center: Vector2, text: String, font_size: int, color: Color) -> void:
	var w := 240.0
	var pos := Vector2(center.x - w * 0.5, center.y)
	draw_string_outline(_font, pos, text, HORIZONTAL_ALIGNMENT_CENTER, w, font_size, 6, Color(0, 0, 0, color.a * 0.85))
	draw_string(_font, pos, text, HORIZONTAL_ALIGNMENT_CENTER, w, font_size, color)



## Runder Booster-Knopf mit Symbol und Abklingzeit als Kreisbogen.
class BoosterButton extends Button:
	var kind := "":
		set(v):
			kind = v
			if _icon:
				_icon.kind = v
	var title := ""
	var ready_ratio := 1.0
	var _t := 0.0
	var _icon: Icon

	func _init() -> void:
		flat = true
		focus_mode = Control.FOCUS_NONE
		_icon = Icon.make(kind, 52)
		_icon.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		_icon.offset_left = -26
		_icon.offset_right = 26
		_icon.offset_top = -26
		_icon.offset_bottom = 26
		add_child(_icon)

	func _process(delta: float) -> void:
		_t += delta
		_icon.modulate = Color(1, 1, 1) if ready_ratio >= 1.0 else Color(0.55, 0.55, 0.65)
		queue_redraw()

	func _draw() -> void:
		var c := size * 0.5
		var r := minf(size.x, size.y) * 0.46
		var ready := ready_ratio >= 1.0
		if ready:
			draw_circle(c, r + 5.0 + 3.0 * sin(_t * 4.0), Color(1.0, 0.75, 0.3, 0.28))
		draw_circle(c, r, Color(0.36, 0.2, 0.62) if ready else Color(0.17, 0.13, 0.28))
		draw_circle(c + Vector2(0, -r * 0.35), r * 0.62, Color(1, 1, 1, 0.1))
		if ready:
			draw_arc(c, r - 3.0, 0.0, TAU, 48, Color(1.0, 0.8, 0.3), 5.0)
		else:
			draw_arc(c, r - 3.0, -PI * 0.5, -PI * 0.5 + TAU * ready_ratio, 48, Color(0.4, 0.8, 1.0), 6.0)
		var font := ThemeDB.fallback_font
		draw_string_outline(font, Vector2(-20, size.y + 6), title, HORIZONTAL_ALIGNMENT_CENTER, size.x + 40, 16, 5, Color(0, 0, 0, 0.8))
		draw_string(font, Vector2(-20, size.y + 6), title, HORIZONTAL_ALIGNMENT_CENTER, size.x + 40, 16, Color(1, 1, 1))
