class_name MainMenu
extends Control
## Hauptmenü: Kopfleiste (Profil, Energie, Gold, Edelsteine, Einstellungen), Update-Hinweis,
## fünf Reiter (Shop · Sammlung · Kampf · Upgrades · Basislager), Battle Pass und Dialoge.

signal play_requested(level: int, hard: bool)
signal quality_changed

const MAX_ASPECT := 0.62
const TABS := [
	["shop", "Shop", "shop"],
	["sammlung", "Sammlung", "cards"],
	["kampf", "Kampf", "swords"],
	["upgrades", "Upgrades", "up"],
	["basis", "Basislager", "camp"],
]

var updater: Updater
var current_tab := "kampf"
var selected_level := 1
var hard := false
var sub_tab := {"sammlung": "helden", "upgrades": "tech"}

var _frame: VBoxContainer
var _content: Control
var _energy_label: Label
var _gold_label: Label
var _gems_label: Label
var _banner: PanelContainer
var _banner_label: Label
var _banner_button: Button
var _nav: Dictionary = {}
var _modal: Control
var _toast: Label
var _toast_t := 0.0
var _tick := 0.0
var _bg_mat: ShaderMaterial


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	var bg := ColorRect.new()
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var mat := ShaderMaterial.new()
	mat.shader = preload("res://shaders/menu_bg.gdshader")
	bg.material = mat
	_bg_mat = mat
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)
	var shade := ColorRect.new()
	shade.color = Color(0.03, 0.02, 0.09, 0.15)
	shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(shade)

	_frame = VBoxContainer.new()
	_frame.add_theme_constant_override("separation", 0)
	add_child(_frame)
	_frame.add_child(_build_top_bar())
	_frame.add_child(_build_banner())
	_content = Control.new()
	_content.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_content.clip_contents = true
	_frame.add_child(_content)
	_frame.add_child(_build_nav())

	_toast = UiKit.label("", 24, UiKit.C_TEXT)
	_toast.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	_toast.offset_top = -230
	_toast.offset_bottom = -190
	_toast.offset_left = -330
	_toast.offset_right = 330
	_toast.add_theme_constant_override("outline_size", 10)
	_toast.modulate.a = 0.0
	add_child(_toast)

	get_viewport().size_changed.connect(_fit)
	_fit()
	Save.changed.connect(_refresh_top)
	if updater:
		updater.update_available.connect(_on_update_available)
		updater.download_progress.connect(_on_download_progress)
		updater.download_failed.connect(_on_download_failed)
		updater.download_done.connect(func() -> void: _banner_label.text = "Installation wird geöffnet …")
	selected_level = Save.max_level()
	show_tab("kampf")


func _fit() -> void:
	var vp := get_viewport().get_visible_rect().size
	var w := minf(vp.x, vp.y * MAX_ASPECT)
	_frame.anchor_left = 0.5
	_frame.anchor_right = 0.5
	_frame.anchor_top = 0.0
	_frame.anchor_bottom = 1.0
	_frame.offset_left = -w * 0.5
	_frame.offset_right = w * 0.5
	_frame.offset_top = 0.0
	_frame.offset_bottom = 0.0


func refresh() -> void:
	selected_level = clampi(selected_level, 1, Save.max_level())
	_refresh_top()
	show_tab(current_tab)
	if updater:
		updater.check()


func _process(delta: float) -> void:
	_tick += delta
	if _tick >= 1.0:
		_tick = 0.0
		_refresh_top()
	if _bg_mat and size.y > 0.0:
		_bg_mat.set_shader_parameter("aspect", Vector2(size.x / size.y, 1.0))
	if _toast_t > 0.0:
		_toast_t -= delta
		_toast.modulate.a = clampf(_toast_t * 2.0, 0.0, 1.0)


# --- Kopfleiste ---------------------------------------------------------------

func _build_top_bar() -> Control:
	var panel := PanelContainer.new()
	var sb := UiKit.box(Color(0.12, 0.07, 0.3, 0.85), 0)
	sb.border_width_bottom = 2
	sb.border_color = Color(1.0, 0.75, 0.4, 0.5)
	sb.corner_radius_bottom_left = 28
	sb.corner_radius_bottom_right = 28
	sb.shadow_size = 12
	sb.shadow_color = Color(0, 0, 0, 0.35)
	sb.content_margin_top = 14
	sb.content_margin_bottom = 12
	sb.content_margin_left = 10
	sb.content_margin_right = 10
	panel.add_theme_stylebox_override("panel", sb)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 5)
	panel.add_child(row)
	var avatar := Button.new()
	avatar.custom_minimum_size = Vector2(58, 58)
	avatar.text = String(Save.data["name"]).left(1)
	for st in ["normal", "hover", "pressed"]:
		avatar.add_theme_stylebox_override(st, UiKit.candy(Color(0.3, 0.55, 1.0), 26, "button"))
	UiKit.add_pop(avatar)
	avatar.add_theme_color_override("font_color", Color(1, 1, 1))
	avatar.pressed.connect(_open_settings)
	row.add_child(avatar)
	_energy_label = _pill(row, "energy", _open_energy)
	_gold_label = _pill(row, "gold", func() -> void: show_tab("shop"))
	_gems_label = _pill(row, "gem", func() -> void: show_tab("shop"))
	var gear := Button.new()
	gear.custom_minimum_size = Vector2(44, 64)
	gear.flat = true
	var gi := Icon.make("gear", 38)
	gi.set_anchors_preset(Control.PRESET_CENTER)
	gi.offset_left = -19
	gi.offset_right = 19
	gi.offset_top = -19
	gi.offset_bottom = 19
	gear.add_child(gi)
	gear.pressed.connect(_open_settings)
	row.add_child(gear)
	return panel


func _pill(row: HBoxContainer, icon: String, on_plus: Callable) -> Label:
	var pill := PanelContainer.new()
	var sb := UiKit.box(Color(0.05, 0.02, 0.14, 0.75), 20, 2, Color(1, 1, 1, 0.12))
	sb.content_margin_left = 4
	sb.content_margin_right = 3
	sb.content_margin_top = 5
	sb.content_margin_bottom = 5
	pill.add_theme_stylebox_override("panel", sb)
	pill.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(pill)
	var h := HBoxContainer.new()
	h.add_theme_constant_override("separation", 4)
	pill.add_child(h)
	h.add_child(Icon.make(icon, 28))
	var l := UiKit.label("0", 21, UiKit.C_TEXT, HORIZONTAL_ALIGNMENT_LEFT)
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	l.clip_text = true
	l.custom_minimum_size = Vector2(40, 0)
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	h.add_child(l)
	var plus := Button.new()
	plus.text = "+"
	plus.custom_minimum_size = Vector2(30, 34)
	plus.add_theme_font_size_override("font_size", 24)
	for st in ["normal", "hover", "pressed"]:
		plus.add_theme_stylebox_override(st, UiKit.candy(Color(0.35, 0.85, 0.3), 12, "bar"))
	plus.add_theme_color_override("font_outline_color", Color(0, 0.2, 0, 0.8))
	plus.add_theme_constant_override("outline_size", 4)
	UiKit.add_pop(plus)
	plus.add_theme_color_override("font_color", Color(1, 1, 1))
	plus.pressed.connect(on_plus)
	h.add_child(plus)
	return l


func _refresh_top() -> void:
	if _energy_label == null:
		return
	_energy_label.text = "%d/%d" % [Save.energy(), MetaData.ENERGY_MAX]
	_gold_label.text = _short(Save.gold())
	_gems_label.text = _short(Save.gems())


static func _short(n: int) -> String:
	if n >= 100000:
		return "%dK" % (n / 1000)
	return str(n)


# --- Update-Hinweis -------------------------------------------------------------

func _build_banner() -> Control:
	_banner = PanelContainer.new()
	var sb := UiKit.candy(Color(1.0, 0.62, 0.2), 20, "panel")
	_banner.add_theme_stylebox_override("panel", sb)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	_banner.add_child(row)
	_banner_label = UiKit.label("Neue Version verfügbar", 21, Color(0.12, 0.06, 0.0), HORIZONTAL_ALIGNMENT_LEFT)
	_banner_label.add_theme_constant_override("outline_size", 0)
	_banner_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_banner_label.custom_minimum_size = Vector2(360, 0)
	_banner_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	row.add_child(_banner_label)
	_banner_button = UiKit.secondary(UiKit.button("Jetzt aktualisieren", _on_update_pressed, 220))
	_banner_button.custom_minimum_size = Vector2(230, 56)
	_banner_button.add_theme_font_size_override("font_size", 21)
	row.add_child(_banner_button)
	_banner.visible = false
	return _banner


func _on_update_available(info: Dictionary) -> void:
	_banner.visible = true
	_banner_button.disabled = false
	var notes := str(info.get("notes", ""))
	_banner_label.text = "Neue Version verfügbar (Stand %s)%s" % [str(info.get("stamp", "")), ("\n" + notes) if notes != "" else ""]


func _on_update_pressed() -> void:
	if updater == null:
		return
	_banner_button.disabled = true
	_banner_label.text = "Update wird geladen …"
	updater.start_download()


func _on_download_progress(ratio: float) -> void:
	_banner_label.text = "Update wird geladen … %d %%" % int(ratio * 100.0)


func _on_download_failed(message: String) -> void:
	_banner_label.text = message
	_banner_button.disabled = false
	_banner_button.text = "Nochmal versuchen"


# --- Reiter unten ----------------------------------------------------------------

func _build_nav() -> Control:
	var panel := PanelContainer.new()
	var sb := UiKit.box(Color(0.14, 0.08, 0.34, 0.95), 0)
	sb.corner_radius_top_left = 30
	sb.corner_radius_top_right = 30
	sb.content_margin_left = 8
	sb.content_margin_right = 8
	sb.content_margin_top = 8
	sb.content_margin_bottom = 10
	sb.border_width_top = 2
	sb.border_color = Color(1.0, 0.75, 0.4, 0.45)
	sb.shadow_size = 14
	sb.shadow_color = Color(0, 0, 0, 0.4)
	panel.add_theme_stylebox_override("panel", sb)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 2)
	panel.add_child(row)
	for t in TABS:
		var id: String = t[0]
		var b := Button.new()
		b.custom_minimum_size = Vector2(0, 118)
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		b.pressed.connect(func() -> void: show_tab(id))
		UiKit.add_pop(b)
		var v := VBoxContainer.new()
		v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		v.alignment = BoxContainer.ALIGNMENT_CENTER
		v.mouse_filter = Control.MOUSE_FILTER_IGNORE
		b.add_child(v)
		var ic := Icon.make(t[2], 56)
		ic.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
		v.add_child(ic)
		var l := UiKit.label(t[1], 18)
		v.add_child(l)
		row.add_child(b)
		_nav[id] = b
	return panel


func show_tab(id: String) -> void:
	current_tab = id
	for k in _nav.keys():
		var b: Button = _nav[k]
		var active: bool = k == id
		for state in ["normal", "hover", "pressed"]:
			if active:
				b.add_theme_stylebox_override(state, UiKit.candy(Color(1.0, 0.62, 0.25), 24, "button"))
			else:
				b.add_theme_stylebox_override(state, StyleBoxEmpty.new())
	for c in _content.get_children():
		c.queue_free()
	var page: Control
	match id:
		"shop":
			page = _tab_shop()
		"sammlung":
			page = _tab_sammlung()
		"upgrades":
			page = _tab_upgrades()
		"basis":
			page = _tab_basis()
		_:
			page = _tab_kampf()
	page.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_content.add_child(page)
	# Weich einblenden: nur Ränder oben/unten verschieben, nie die Breite anfassen
	page.modulate.a = 0.0
	page.offset_top = 18.0
	page.offset_bottom = 18.0
	var tw := page.create_tween()
	tw.set_parallel(true)
	tw.tween_property(page, "modulate:a", 1.0, 0.18)
	tw.tween_property(page, "offset_top", 0.0, 0.22).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_property(page, "offset_bottom", 0.0, 0.22).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	_refresh_top()


# --- Bausteine -------------------------------------------------------------------

func _panel(color := Color(0.1, 0.12, 0.25, 0.92), border := Color(0.3, 0.4, 0.7)) -> PanelContainer:
	var p := PanelContainer.new()
	# Kühle Grundfarben werden zu warmem Violett aufgehellt, damit alles freundlicher wirkt
	var warm := Color(color.r * 0.8 + 0.12, color.g * 0.7 + 0.05, color.b * 0.8 + 0.18, maxf(0.9, color.a))
	p.add_theme_stylebox_override("panel", UiKit.candy(warm, 24, "panel"))
	return p


func _scroll_page(separation := 14) -> Array:
	var scroll := ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var margin := MarginContainer.new()
	margin.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	for side in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, 16)
	scroll.add_child(margin)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", separation)
	margin.add_child(v)
	return [scroll, v]


func _small_button(text: String, cb: Callable, width := 190.0, primary := true) -> Button:
	var b := UiKit.button(text, cb, width)
	b.custom_minimum_size = Vector2(width, 60)
	b.add_theme_font_size_override("font_size", 21)
	if not primary:
		UiKit.secondary(b)
	return b


func _toggle(options: Array, current: String, cb: Callable) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 8)
	for o in options:
		var key: String = o[0]
		var b := _small_button(o[1], func() -> void: cb.call(key), 200, key == current)
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(b)
	return row


func _wrap_left(text: String, font_size := 20, color := UiKit.C_TEXT) -> Label:
	var l := UiKit.wrap_label(text, font_size, color)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	return l


func toast(text: String) -> void:
	_toast.text = text
	_toast_t = 2.2


# --- Reiter: Kampf ------------------------------------------------------------------

func _tab_kampf() -> Control:
	var root := MarginContainer.new()
	for side in ["left", "right"]:
		root.add_theme_constant_override("margin_" + side, 12)
	root.add_theme_constant_override("margin_top", 12)
	root.add_theme_constant_override("margin_bottom", 12)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 12)
	root.add_child(v)

	# Battle Pass
	var pass_btn := Button.new()
	pass_btn.custom_minimum_size = Vector2(0, 100)
	var gold_box := UiKit.candy(Color(1.0, 0.7, 0.2), 26, "button")
	pass_btn.add_theme_stylebox_override("normal", gold_box)
	pass_btn.add_theme_stylebox_override("hover", gold_box)
	pass_btn.add_theme_stylebox_override("pressed", gold_box)
	pass_btn.pressed.connect(open_battle_pass)
	UiKit.add_pop(pass_btn)
	var ph := HBoxContainer.new()
	ph.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	ph.offset_left = 14
	ph.offset_right = -14
	ph.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ph.add_theme_constant_override("separation", 12)
	pass_btn.add_child(ph)
	var pi := Icon.make("pass", 64)
	pi.badge = not Save.pass_claimable().is_empty() or _mission_ready()
	ph.add_child(pi)
	var pv := VBoxContainer.new()
	pv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	pv.alignment = BoxContainer.ALIGNMENT_CENTER
	pv.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ph.add_child(pv)
	var pt := UiKit.label("BATTLE PASS", 28, Color(0.45, 0.15, 0.05), HORIZONTAL_ALIGNMENT_LEFT)
	pt.add_theme_constant_override("outline_size", 0)
	pv.add_child(pt)
	var bar := ProgressBar.new()
	bar.show_percentage = false
	bar.custom_minimum_size = Vector2(0, 24)
	bar.max_value = MetaData.PASS_POINTS_PER_LEVEL
	bar.value = Save.pass_progress()
	bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bar.add_theme_stylebox_override("fill", UiKit.box(Color(0.25, 0.6, 1.0), 8))
	pv.add_child(bar)
	var bl := UiKit.label("%d/%d" % [Save.pass_progress(), MetaData.PASS_POINTS_PER_LEVEL], 17)
	bl.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	bar.add_child(bl)
	var lvl := UiKit.label("Stufe\n%d" % Save.pass_level(), 22, Color(1, 1, 1))
	ph.add_child(lvl)
	v.add_child(pass_btn)

	# Mitte: linke Spalte, Level-Auswahl, rechte Spalte
	var mid := HBoxContainer.new()
	mid.size_flags_vertical = Control.SIZE_EXPAND_FILL
	mid.add_theme_constant_override("separation", 10)
	v.add_child(mid)
	var left := VBoxContainer.new()
	left.add_theme_constant_override("separation", 10)
	mid.add_child(left)
	left.add_child(_side_button("shop", "Angebote", false, func() -> void: show_tab("shop")))
	left.add_child(_side_button("check", "Missionen", _mission_ready(), open_battle_pass))
	left.add_child(_side_button("skull", "Gegner", false, _open_bestiary))

	var center := VBoxContainer.new()
	center.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	center.add_theme_constant_override("separation", 10)
	mid.add_child(center)
	center.add_child(_toggle([["normal", "Normal"], ["schwer", "Schwer"]], "schwer" if hard else "normal", _set_difficulty))
	var card := StageScene.new()
	card.level = selected_level
	card.hard = hard
	card.size_flags_vertical = Control.SIZE_EXPAND_FILL
	card.custom_minimum_size = Vector2(0, 300)
	center.add_child(card)
	var sel := HBoxContainer.new()
	sel.add_theme_constant_override("separation", 8)
	center.add_child(sel)
	var prev := _small_button("‹", func() -> void: _change_level(-1), 70, false)
	sel.add_child(prev)
	var name_l := UiKit.label("Level %d" % selected_level + (" · Boss" if GameData.is_boss_level(selected_level) else ""), 26, UiKit.C_GOLD)
	name_l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sel.add_child(name_l)
	var next := _small_button("›", func() -> void: _change_level(1), 70, false)
	sel.add_child(next)
	prev.disabled = selected_level <= 1
	next.disabled = selected_level >= Save.max_level()
	center.add_child(_segments())

	var right := VBoxContainer.new()
	right.add_theme_constant_override("separation", 10)
	mid.add_child(right)
	right.add_child(_side_button("gift", "Täglich", Save.daily_ready("daily_date"), _open_daily))
	right.add_child(_side_button("wheel", "Glücksrad", Save.daily_ready("wheel_date"), _open_wheel))
	right.add_child(_side_button("trophy", "Ranglisten", false, func() -> void:
		_info("Ranglisten", "Ranglisten kommen, sobald es einen Spielserver gibt. Dann misst du dich mit anderen Kommandanten.")
	))
	right.add_child(_side_button("noads", "Keine\nWerbung", false, func() -> void:
		_info("Keine Werbung", "In der Testphase gibt es keine Werbung. Später soll Werbung nur freiwillig sein – gegen eine Belohnung, nie erzwungen.")
	))

	# Unten: Kampf
	var bottom := HBoxContainer.new()
	bottom.add_theme_constant_override("separation", 12)
	bottom.alignment = BoxContainer.ALIGNMENT_CENTER
	v.add_child(bottom)
	var fight := VBoxContainer.new()
	fight.add_theme_constant_override("separation", 2)
	bottom.add_child(fight)
	var cost := HBoxContainer.new()
	cost.alignment = BoxContainer.ALIGNMENT_CENTER
	cost.add_child(Icon.make("energy", 30))
	cost.add_child(UiKit.label(str(MetaData.ENERGY_COST), 24))
	fight.add_child(cost)
	var fight_btn := UiKit.button("KAMPF", _on_fight, 330)
	fight_btn.custom_minimum_size = Vector2(330, 92)
	fight_btn.add_theme_font_size_override("font_size", 40)
	fight.add_child(fight_btn)
	var mode := _small_button("Spielmodus", func() -> void:
		_info("Spielmodus", "Weitere Modi folgen:\n\n• Boss-Ansturm: ein Boss nach dem anderen\n• Überleben: endlose Wellen – wie lange hältst du durch?")
	, 170, false)
	mode.custom_minimum_size = Vector2(170, 92)
	bottom.add_child(mode)
	return root


func _side_button(icon: String, text: String, badge: bool, cb: Callable) -> Button:
	var b := Button.new()
	b.custom_minimum_size = Vector2(112, 118)
	for st in ["normal", "hover", "pressed"]:
		b.add_theme_stylebox_override(st, UiKit.candy(Color(0.36, 0.22, 0.7), 24, "button"))
	b.pressed.connect(cb)
	UiKit.add_pop(b)
	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.alignment = BoxContainer.ALIGNMENT_CENTER
	v.mouse_filter = Control.MOUSE_FILTER_IGNORE
	b.add_child(v)
	var ic := Icon.make(icon, 54)
	ic.badge = badge
	ic.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	v.add_child(ic)
	var l := UiKit.label(text, 16)
	v.add_child(l)
	return b


func _segments() -> Control:
	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", 6)
	var first := GameData.world_of(selected_level) * GameData.LEVELS_PER_WORLD + 1
	for n in range(first, first + GameData.LEVELS_PER_WORLD):
		var won: bool = Save.data["won_levels"].has(("S" if hard else "N") + str(n))
		var col := Color(1.0, 0.8, 0.25) if won else (Color(0.35, 0.9, 0.35) if n == selected_level else Color(0.3, 0.32, 0.42))
		if GameData.is_boss_level(n):
			var ic := Icon.make("skull", 34)
			row.add_child(ic)
		else:
			var r := Panel.new()
			r.add_theme_stylebox_override("panel", UiKit.candy(col, 11, "bar"))
			r.custom_minimum_size = Vector2(48, 24)
			row.add_child(r)
	return row


func _change_level(d: int) -> void:
	selected_level = clampi(selected_level + d, 1, Save.max_level())
	show_tab("kampf")


func _set_difficulty(key: String) -> void:
	if key == "schwer" and not Save.hard_unlocked():
		_info("Schwer", "Schwer wird freigeschaltet, wenn du die Schleimmutter in Level %d besiegt hast. Dann gibt es mehr Gegnerleben und 50 %% mehr Belohnung." % GameData.LEVELS_PER_WORLD)
		return
	hard = key == "schwer"
	show_tab("kampf")


func _on_fight() -> void:
	if Save.energy() < MetaData.ENERGY_COST:
		_open_energy()
		return
	play_requested.emit(selected_level, hard)


func _mission_ready() -> bool:
	var m := Save.missions()
	for id in m["ids"]:
		var d := Save.mission_def(id)
		if not m["claimed"].has(id) and int(m["progress"].get(id, 0)) >= int(d["goal"]):
			return true
	return false


# --- Reiter: Sammlung ----------------------------------------------------------------

func _tab_sammlung() -> Control:
	var page := _scroll_page()
	var v: VBoxContainer = page[1]
	var current: String = sub_tab["sammlung"]
	v.add_child(_toggle([["helden", "Helden"], ["booster", "Booster"]], current, func(k: String) -> void:
		sub_tab["sammlung"] = k
		show_tab("sammlung")
	))
	if current == "booster":
		_booster_list(v)
		return page[0]
	var head := HBoxContainer.new()
	var hl := UiKit.label("Aufstellung %d/%d" % [Save.squad().size(), MetaData.SQUAD_MAX], 24, UiKit.C_GOLD, HORIZONTAL_ALIGNMENT_LEFT)
	hl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head.add_child(hl)
	v.add_child(head)
	v.add_child(_wrap_left("Helden in der Aufstellung erscheinen im Kampf als Start- und Team-Karten (zufällig). Tippe auf einen Helden für Details.", 18, UiKit.C_MUTED))
	var grid := GridContainer.new()
	grid.columns = 3
	grid.add_theme_constant_override("h_separation", 10)
	grid.add_theme_constant_override("v_separation", 12)
	v.add_child(grid)
	for id in GameData.HERO_IDS:
		grid.add_child(_hero_card(id))
	return page[0]


func _booster_list(v: VBoxContainer) -> void:
	var slots := Save.booster_slots()
	v.add_child(UiKit.label("Ausgerüstet %d/%d" % [slots.size(), MetaData.BOOSTER_SLOTS], 24, UiKit.C_GOLD, HORIZONTAL_ALIGNMENT_LEFT))
	v.add_child(_wrap_left("Booster löst du im Kampf mit den runden Knöpfen aus. Danach brauchen sie eine Weile zum Aufladen.", 18, UiKit.C_MUTED))
	for id in MetaData.BOOSTERS.keys():
		var d: Dictionary = MetaData.BOOSTERS[id]
		var unlocked := Save.booster_unlocked(id)
		var equipped := slots.has(id)
		var lvl := Save.booster_level(id)
		var p := _panel(Color(0.3, 0.2, 0.55, 0.95) if equipped else Color(0.14, 0.12, 0.28, 0.92))
		var h := HBoxContainer.new()
		h.add_theme_constant_override("separation", 12)
		p.add_child(h)
		var ic := Icon.make(String(d["icon"]), 60)
		if not unlocked:
			ic.modulate = Color(0.4, 0.4, 0.5)
		h.add_child(ic)
		var tv := VBoxContainer.new()
		tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var title := "%s · Stufe %d" % [d["title"], lvl] if unlocked else String(d["title"])
		tv.add_child(UiKit.label(title, 22, UiKit.C_GOLD if equipped else UiKit.C_TEXT, HORIZONTAL_ALIGNMENT_LEFT))
		tv.add_child(_wrap_left(String(d["desc"]).replace("%%", "%"), 17, UiKit.C_MUTED))
		if unlocked:
			tv.add_child(_wrap_left("Aufladen: %d s · Wirkung %d %%" % [int(MetaData.booster_cd(id, lvl)), int(MetaData.booster_power(lvl) * 100)], 16, UiKit.C_MUTED))
		else:
			tv.add_child(_wrap_left("Freischaltung: Level %d gewinnen" % int(d["unlock"]), 16, UiKit.C_MUTED))
		h.add_child(tv)
		if unlocked:
			var btns := VBoxContainer.new()
			btns.add_theme_constant_override("separation", 6)
			h.add_child(btns)
			var booster_id: String = id
			var eq := _small_button("Abnehmen" if equipped else "Ausrüsten", func() -> void:
				var msg := Save.toggle_booster(booster_id)
				if msg != "":
					toast(msg)
				show_tab("sammlung")
			, 150, not equipped)
			btns.add_child(eq)
			var up := _small_button("Max." if lvl >= MetaData.BOOSTER_MAX else "%d Gold" % MetaData.booster_cost(lvl), func() -> void:
				if Save.upgrade_booster(booster_id):
					toast("%s: Stufe %d" % [d["title"], Save.booster_level(booster_id)])
				show_tab("sammlung")
			, 150, false)
			up.disabled = lvl >= MetaData.BOOSTER_MAX or Save.gold() < MetaData.booster_cost(lvl)
			btns.add_child(up)
		v.add_child(p)


## Heldenkarte im Raster: Name, 3D-Porträt, Stufe oder Freischaltbedingung.
func _hero_card(id: String) -> Control:
	var d: Dictionary = GameData.HEROES[id]
	var col: Color = d["color"]
	var unlocked := Save.hero_unlocked(id)
	var b := Button.new()
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	b.custom_minimum_size = Vector2(0, 300)
	var border := col if unlocked else Color(0.3, 0.32, 0.42)
	var sb := UiKit.candy(Color(0.32, 0.2, 0.62) if unlocked else Color(0.2, 0.17, 0.3), 22, "panel")
	UiKit.add_pop(b)
	b.add_theme_stylebox_override("normal", sb)
	b.add_theme_stylebox_override("hover", sb)
	b.add_theme_stylebox_override("pressed", sb)
	b.pressed.connect(func() -> void: _open_hero(id))
	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.offset_left = 6
	v.offset_right = -6
	v.offset_top = 6
	v.offset_bottom = -6
	v.add_theme_constant_override("separation", 4)
	v.mouse_filter = Control.MOUSE_FILTER_IGNORE
	b.add_child(v)
	var banner := PanelContainer.new()
	banner.add_theme_stylebox_override("panel", UiKit.box(col.darkened(0.25) if unlocked else Color(0.25, 0.27, 0.36), 8))
	banner.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var nl := UiKit.label(String(d["name"]).to_upper(), 17, Color(1, 1, 1))
	nl.clip_text = true
	banner.add_child(nl)
	v.add_child(banner)
	var portrait := HeroPortrait.make(id, 150, not unlocked)
	portrait.size_flags_vertical = Control.SIZE_EXPAND_FILL
	portrait.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	v.add_child(portrait)
	var foot := PanelContainer.new()
	foot.mouse_filter = Control.MOUSE_FILTER_IGNORE
	foot.add_theme_stylebox_override("panel", UiKit.box(Color(0.32, 0.25, 0.75) if unlocked else Color(0.2, 0.2, 0.3), 8))
	var fl: Label
	if unlocked:
		var lvl := Save.hero_level(id)
		var txt := "Stufe %d" % lvl
		if Save.can_level_hero(id):
			txt += " · bereit!"
		fl = UiKit.label(txt, 18, UiKit.C_GOLD if Save.can_level_hero(id) else Color(1, 1, 1))
	else:
		fl = UiKit.label("Level %d gewinnen" % int(MetaData.HERO_UNLOCK[id]), 15, UiKit.C_MUTED)
	foot.add_child(fl)
	v.add_child(foot)
	if unlocked:
		var in_team := UiKit.label("Im Team" if Save.in_squad(id) else "Reserve", 15, Color(0.45, 1.0, 0.55) if Save.in_squad(id) else UiKit.C_MUTED)
		v.add_child(in_team)
	return b


## Detailansicht eines Helden: Werte, Aufwerten, Aufstellung, Freischalten.
func _open_hero(id: String) -> void:
	var d: Dictionary = GameData.HEROES[id]
	var v := _modal_box(String(d["name"]))
	var unlocked := Save.hero_unlocked(id)
	v.add_child(UiKit.label("%s · %s" % [d["role"], d["weapon"]], 21, UiKit.C_MUTED))
	var portrait := HeroPortrait.make(id, 260, not unlocked)
	portrait.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	v.add_child(portrait)
	v.add_child(UiKit.wrap_label(String(d["blurb"]), 21))
	if not unlocked:
		v.add_child(UiKit.wrap_label("Freischaltung: Gewinne Level %d – oder sofort für %d Edelsteine." % [int(MetaData.HERO_UNLOCK[id]), MetaData.HERO_UNLOCK_GEMS], 20, UiKit.C_MUTED))
		var buy := UiKit.button("Freischalten · %d Edelsteine" % MetaData.HERO_UNLOCK_GEMS, func() -> void:
			if Save.unlock_with_gems(id):
				toast("%s ist jetzt im Team!" % d["name"])
			_close_modal()
			show_tab("sammlung")
		, 460)
		buy.disabled = Save.gems() < MetaData.HERO_UNLOCK_GEMS
		v.add_child(buy)
		v.add_child(UiKit.secondary(UiKit.button("Schließen", _close_modal, 460)))
		return
	var lvl := Save.hero_level(id)
	var need := MetaData.hero_cards_needed(lvl)
	var dmg_now := int(round(float(d["damage"]) * MetaData.hero_damage_mult(lvl)))
	var dmg_next := int(round(float(d["damage"]) * MetaData.hero_damage_mult(lvl + 1)))
	var stats := GridContainer.new()
	stats.columns = 2
	stats.add_theme_constant_override("h_separation", 30)
	for row in [["Stufe", str(lvl)], ["Schaden", "%d → %d" % [dmg_now, dmg_next] if lvl < MetaData.HERO_MAX_LEVEL else str(dmg_now)],
			["Nachladezeit", "%s s" % String.num(float(d["reload"]), 1).replace(".", ",")], ["Magazin", str(int(d["mag"]))],
			["Karten", "%d/%d" % [Save.hero_cards(id), need]]]:
		stats.add_child(UiKit.label(row[0], 21, UiKit.C_MUTED, HORIZONTAL_ALIGNMENT_LEFT))
		stats.add_child(UiKit.label(row[1], 21, UiKit.C_TEXT, HORIZONTAL_ALIGNMENT_LEFT))
	var sc := CenterContainer.new()
	sc.add_child(stats)
	v.add_child(sc)
	var up_text := "Höchste Stufe erreicht" if lvl >= MetaData.HERO_MAX_LEVEL else "Aufwerten · %d Gold · %d Karten" % [MetaData.hero_gold_needed(lvl), need]
	var up := UiKit.button(up_text, func() -> void:
		if Save.level_hero(id):
			toast("%s ist jetzt Stufe %d!" % [d["name"], Save.hero_level(id)])
		_open_hero(id)
		show_tab_keep_modal("sammlung")
	, 460)
	up.disabled = not Save.can_level_hero(id)
	v.add_child(up)
	var team := UiKit.secondary(UiKit.button("Aus der Aufstellung nehmen" if Save.in_squad(id) else "In die Aufstellung", func() -> void:
		var msg := Save.toggle_squad(id)
		if msg != "":
			toast(msg)
		_open_hero(id)
		show_tab_keep_modal("sammlung")
	, 460))
	v.add_child(team)
	v.add_child(UiKit.secondary(UiKit.button("Schließen", func() -> void:
		_close_modal()
		show_tab("sammlung")
	, 460)))


## Baut einen Reiter neu, ohne den offenen Dialog zu schließen.
func show_tab_keep_modal(id: String) -> void:
	var keep := _modal
	_modal = null
	show_tab(id)
	_modal = keep
	if _modal:
		move_child(_modal, get_child_count() - 1)


func _hero_row(id: String) -> Control:
	var d: Dictionary = GameData.HEROES[id]
	var col: Color = d["color"]
	var unlocked := Save.hero_unlocked(id)
	var p := _panel(Color(0.1, 0.12, 0.25, 0.92) if unlocked else Color(0.08, 0.08, 0.14, 0.9), col if unlocked else Color(0.25, 0.27, 0.35))
	var h := HBoxContainer.new()
	h.add_theme_constant_override("separation", 12)
	p.add_child(h)
	var em := HeroBadge.new()
	em.color = col if unlocked else Color(0.3, 0.3, 0.35)
	em.text = String(d["name"]).left(1)
	em.custom_minimum_size = Vector2(96, 96)
	h.add_child(em)
	var info := VBoxContainer.new()
	info.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	info.add_theme_constant_override("separation", 4)
	h.add_child(info)
	info.add_child(UiKit.label("%s · %s" % [d["name"], d["weapon"]], 24, UiKit.C_GOLD if unlocked else UiKit.C_MUTED, HORIZONTAL_ALIGNMENT_LEFT))
	if not unlocked:
		info.add_child(_wrap_left("Freischaltung: Gewinne Level %d." % int(MetaData.HERO_UNLOCK[id]), 19, UiKit.C_MUTED))
		h.add_child(Icon.make("lock", 48))
		return p
	var lvl := Save.hero_level(id)
	var need := MetaData.hero_cards_needed(lvl)
	info.add_child(UiKit.label("Stufe %d  ·  %s" % [lvl, d["role"]], 19, UiKit.C_TEXT, HORIZONTAL_ALIGNMENT_LEFT))
	var bar := ProgressBar.new()
	bar.show_percentage = false
	bar.custom_minimum_size = Vector2(0, 22)
	bar.max_value = need
	bar.value = mini(Save.hero_cards(id), need)
	bar.add_theme_stylebox_override("fill", UiKit.box(Color(0.35, 0.9, 0.45), 8))
	info.add_child(bar)
	var bl := UiKit.label("%d/%d Karten" % [Save.hero_cards(id), need], 16)
	bl.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	bar.add_child(bl)
	var dmg := float(d["damage"]) * MetaData.hero_damage_mult(lvl)
	var stats := "Schaden %d → %d · Nachladen %s s · Magazin %d" % [int(round(dmg)), int(round(float(d["damage"]) * MetaData.hero_damage_mult(lvl + 1))),
		String.num(float(d["reload"]), 1).replace(".", ","), int(d["mag"])]
	info.add_child(_wrap_left(stats, 16, UiKit.C_MUTED))
	var btn_text := "Max." if lvl >= MetaData.HERO_MAX_LEVEL else "Aufwerten\n%d Gold" % MetaData.hero_gold_needed(lvl)
	var b := _small_button(btn_text, func() -> void:
		if Save.level_hero(id):
			toast("%s ist jetzt Stufe %d!" % [d["name"], Save.hero_level(id)])
		show_tab("sammlung")
	, 150)
	b.custom_minimum_size = Vector2(150, 84)
	b.disabled = not Save.can_level_hero(id)
	h.add_child(b)
	return p


# --- Reiter: Upgrades ----------------------------------------------------------------

func _tab_upgrades() -> Control:
	var page := _scroll_page(10)
	var v: VBoxContainer = page[1]
	var current: String = sub_tab["upgrades"]
	v.add_child(_toggle([["tech", "Tech-Baum"], ["munition", "Munition"], ["talente", "Talente"]], current, func(k: String) -> void:
		sub_tab["upgrades"] = k
		show_tab("upgrades")
	))
	if current == "talente":
		_talents(v)
		return page[0]
	if current == "munition":
		_ammo_upgrades(v)
		return page[0]
	v.add_child(_wrap_left("Verbesserungen für die Station. Sie gelten in jedem Kampf.", 20, UiKit.C_MUTED))
	var done := Save.tech_count()
	for i in MetaData.TECH.size():
		var t: Dictionary = MetaData.TECH[i]
		var state := "done" if i < done else ("next" if i == done else "locked")
		var p := _panel(Color(0.1, 0.18, 0.12, 0.92) if state == "done" else (Color(0.12, 0.12, 0.28, 0.95) if state == "next" else Color(0.08, 0.08, 0.14, 0.9)),
			Color(0.35, 0.9, 0.45) if state == "done" else (UiKit.C_GOLD if state == "next" else Color(0.25, 0.27, 0.35)))
		var h := HBoxContainer.new()
		h.add_theme_constant_override("separation", 12)
		p.add_child(h)
		h.add_child(Icon.make("check" if state == "done" else ("up" if state == "next" else "lock"), 48))
		var tv := VBoxContainer.new()
		tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		tv.add_child(UiKit.label(t["title"], 23, UiKit.C_TEXT if state != "locked" else UiKit.C_MUTED, HORIZONTAL_ALIGNMENT_LEFT))
		tv.add_child(_wrap_left(t["desc"], 18, UiKit.C_MUTED))
		h.add_child(tv)
		if state == "next":
			var b := _small_button("%d Gold" % int(t["cost"]), func() -> void:
				if Save.buy_next_tech():
					toast("%s gebaut!" % t["title"])
				else:
					toast("Nicht genug Gold.")
				show_tab("upgrades")
			, 150)
			b.disabled = Save.gold() < int(t["cost"])
			h.add_child(b)
		v.add_child(p)
	return page[0]


func _ammo_upgrades(v: VBoxContainer) -> void:
	v.add_child(_wrap_left("Dauerhafte Verbesserungen der Kugelbahn. Sie gelten in jedem Kampf.", 20, UiKit.C_MUTED))
	for u in MetaData.AMMO_UPGRADES:
		var id: String = u["id"]
		var lvl := Save.ammo_level(id)
		var mx := int(u["max"])
		var p := _panel()
		var h := HBoxContainer.new()
		h.add_theme_constant_override("separation", 12)
		p.add_child(h)
		h.add_child(Icon.make("energy" if id == "rate" else ("gold" if id == "cap" else "up"), 48))
		var tv := VBoxContainer.new()
		tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		tv.add_child(UiKit.label("%s · Stufe %d/%d" % [u["title"], lvl, mx], 22, UiKit.C_TEXT, HORIZONTAL_ALIGNMENT_LEFT))
		tv.add_child(_wrap_left(String(u["desc"]).replace("%%", "%"), 17, UiKit.C_MUTED))
		var bar := ProgressBar.new()
		bar.show_percentage = false
		bar.custom_minimum_size = Vector2(0, 12)
		bar.max_value = mx
		bar.value = lvl
		bar.add_theme_stylebox_override("fill", UiKit.box(UiKit.C_GOLD, 6))
		tv.add_child(bar)
		h.add_child(tv)
		if lvl >= mx:
			h.add_child(Icon.make("check", 44))
		else:
			var cost := MetaData.ammo_cost(u, lvl)
			var b := _small_button("%d Gold" % cost, func() -> void:
				if Save.buy_ammo_upgrade(id):
					toast("%s: Stufe %d" % [u["title"], Save.ammo_level(id)])
				show_tab("upgrades")
			, 150)
			b.disabled = Save.gold() < cost
			h.add_child(b)
		v.add_child(p)


func _talents(v: VBoxContainer) -> void:
	var head := HBoxContainer.new()
	head.add_theme_constant_override("separation", 8)
	head.add_child(Icon.make("star", 40))
	var sl := UiKit.label("%d Sterne" % Save.stars(), 26, UiKit.C_GOLD, HORIZONTAL_ALIGNMENT_LEFT)
	sl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head.add_child(sl)
	var draw := _small_button("Talent ziehen\n1 Stern", func() -> void:
		var id := Save.draw_talent()
		if id == "":
			toast("Keine Sterne. Sterne gibt es für gewonnene Level.")
		else:
			var t: Dictionary = MetaData.TALENTS[id]
			_info("Talent erhalten", "%s – Stufe %d\n\n%s" % [t["title"], Save.talent_level(id), t["desc"]])
		show_tab("upgrades")
	, 210)
	draw.custom_minimum_size = Vector2(210, 80)
	draw.disabled = Save.stars() <= 0
	head.add_child(draw)
	v.add_child(head)
	v.add_child(_wrap_left("Talente sind dauerhafte Boni. Zieht man ein Talent erneut, steigt es eine Stufe (bis 5).", 19, UiKit.C_MUTED))
	var grid := GridContainer.new()
	grid.columns = 3
	grid.add_theme_constant_override("h_separation", 10)
	grid.add_theme_constant_override("v_separation", 10)
	v.add_child(grid)
	var ids: Array = MetaData.TALENTS.keys()
	for i in MetaData.TALENT_SLOTS:
		var p: PanelContainer
		var box := VBoxContainer.new()
		box.alignment = BoxContainer.ALIGNMENT_CENTER
		if i < ids.size() and Save.talent_level(ids[i]) > 0:
			var t: Dictionary = MetaData.TALENTS[ids[i]]
			p = _panel(Color(0.12, 0.3, 0.18, 0.95), t["color"])
			box.add_child(_wrap_left(t["title"], 19, UiKit.C_TEXT))
			box.add_child(UiKit.label("Stufe %d/%d" % [Save.talent_level(ids[i]), MetaData.TALENT_MAX], 17, UiKit.C_GOLD))
		else:
			p = _panel(Color(0.18, 0.15, 0.4, 0.85), Color(0.35, 0.3, 0.6))
			box.add_child(UiKit.label("?", 44, Color(0.5, 0.45, 0.8)))
		p.custom_minimum_size = Vector2(0, 120)
		p.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		p.add_child(box)
		grid.add_child(p)


# --- Reiter: Shop ------------------------------------------------------------------

func _tab_shop() -> Control:
	var page := _scroll_page()
	var v: VBoxContainer = page[1]
	v.add_child(_shop_item("gift", "Angebot des Tages", "Gratis: 100 Gold", "Abholen" if Save.daily_ready("shop_free_date") else "Morgen wieder",
		Save.daily_ready("shop_free_date"), func() -> void:
			Save.add("gold", 100)
			Save.mark_daily("shop_free_date")
			toast("+100 Gold")
			show_tab("shop")))
	v.add_child(_shop_item("cards", "Heldentruhe", "8 zufällige Heldenkarten", "%d Edelsteine" % MetaData.SHOP_CHEST_COST,
		Save.gems() >= MetaData.SHOP_CHEST_COST, func() -> void:
			if Save.spend("gems", MetaData.SHOP_CHEST_COST):
				Save.add("cards", 8)
				_info("Heldentruhe", "8 Heldenkarten erhalten. Schau in der Sammlung nach, wer aufsteigen kann!")
			show_tab("shop")))
	v.add_child(_shop_item("energy", "Energie auffüllen", "Energie sofort auf %d" % MetaData.ENERGY_MAX, "%d Edelsteine" % MetaData.SHOP_ENERGY_COST,
		Save.gems() >= MetaData.SHOP_ENERGY_COST, _buy_energy))
	v.add_child(UiKit.label("Edelsteine", 28, UiKit.C_GOLD, HORIZONTAL_ALIGNMENT_LEFT))
	for pack in MetaData.GEM_PACKS:
		v.add_child(_shop_item("gem", "%d Edelsteine" % int(pack["gems"]), "Kauf über Google Play – kommt nach der Testphase", pack["price"], true, func() -> void:
			_info("Noch nicht verfügbar", "Echte Käufe kommen, wenn die App im Play Store ist. In der Testphase gibt es Edelsteine über den Battle Pass, das Glücksrad und die tägliche Belohnung.")))
	return page[0]


func _shop_item(icon: String, title: String, desc: String, button: String, enabled: bool, cb: Callable) -> Control:
	var p := _panel()
	var h := HBoxContainer.new()
	h.add_theme_constant_override("separation", 12)
	p.add_child(h)
	h.add_child(Icon.make(icon, 64))
	var tv := VBoxContainer.new()
	tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	tv.add_child(UiKit.label(title, 24, UiKit.C_TEXT, HORIZONTAL_ALIGNMENT_LEFT))
	tv.add_child(_wrap_left(desc, 18, UiKit.C_MUTED))
	h.add_child(tv)
	var b := _small_button(button, cb, 180)
	b.custom_minimum_size = Vector2(180, 70)
	b.disabled = not enabled
	h.add_child(b)
	return p


func _buy_energy() -> void:
	if Save.spend("gems", MetaData.SHOP_ENERGY_COST):
		Save.data["energy"] = MetaData.ENERGY_MAX
		Save.save_game()
		toast("Energie aufgefüllt!")
	show_tab(current_tab)


# --- Reiter: Basislager ------------------------------------------------------------

func _tab_basis() -> Control:
	var page := _scroll_page()
	var v: VBoxContainer = page[1]
	v.add_child(UiKit.label("Basislager", 32, UiKit.C_GOLD, HORIZONTAL_ALIGNMENT_LEFT))
	v.add_child(_wrap_left("Jedes Crewmitglied hat ein Quartier, das Heldenkarten herstellt – auch wenn du nicht spielst.", 20, UiKit.C_MUTED))
	for id in GameData.HERO_IDS:
		v.add_child(_building_row(id))
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	for t in ["Überfall", "Rache"]:
		var b := _small_button(t + " – bald", func() -> void:
			_info(t, "Überfälle auf andere Stationen brauchen einen Spielserver und kommen später.")
		, 200, false)
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(b)
	v.add_child(row)
	return page[0]


func _building_row(id: String) -> Control:
	var d: Dictionary = GameData.HEROES[id]
	var unlocked := Save.hero_unlocked(id)
	var p := _panel(Color(0.1, 0.12, 0.25, 0.92) if unlocked else Color(0.08, 0.08, 0.14, 0.9), d["color"] if unlocked else Color(0.25, 0.27, 0.35))
	var h := HBoxContainer.new()
	h.add_theme_constant_override("separation", 12)
	p.add_child(h)
	var em := HeroBadge.new()
	em.color = d["color"] if unlocked else Color(0.3, 0.3, 0.35)
	em.text = String(d["name"]).left(1)
	em.custom_minimum_size = Vector2(80, 80)
	h.add_child(em)
	var tv := VBoxContainer.new()
	tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	h.add_child(tv)
	tv.add_child(UiKit.label(MetaData.BUILDINGS[id], 22, UiKit.C_TEXT if unlocked else UiKit.C_MUTED, HORIZONTAL_ALIGNMENT_LEFT))
	if not unlocked:
		tv.add_child(_wrap_left("Kommt mit %s (Level %d gewinnen)." % [d["name"], int(MetaData.HERO_UNLOCK[id])], 18, UiKit.C_MUTED))
		h.add_child(Icon.make("lock", 44))
		return p
	var b := Save.building(id)
	var lvl := int(b["level"])
	var cap := MetaData.building_cap(lvl)
	var stock := int(floor(float(b["stock"])))
	tv.add_child(UiKit.label("Stufe %d · %d Karten pro Stunde" % [lvl, int(MetaData.building_rate(lvl))], 18, UiKit.C_MUTED, HORIZONTAL_ALIGNMENT_LEFT))
	var bar := ProgressBar.new()
	bar.show_percentage = false
	bar.custom_minimum_size = Vector2(0, 20)
	bar.max_value = cap
	bar.value = float(b["stock"])
	bar.add_theme_stylebox_override("fill", UiKit.box(d["color"], 8))
	tv.add_child(bar)
	var bl := UiKit.label("%d/%d bereit" % [stock, cap], 15)
	bl.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	bar.add_child(bl)
	var btns := VBoxContainer.new()
	btns.add_theme_constant_override("separation", 6)
	h.add_child(btns)
	var collect := _small_button("Sammeln", func() -> void:
		var n := Save.collect_building(id)
		toast("+%d %s-Karten" % [n, d["name"]] if n > 0 else "Noch nichts bereit.")
		show_tab("basis")
	, 150)
	collect.disabled = stock <= 0
	btns.add_child(collect)
	var up_text := "Max." if lvl >= MetaData.BUILDING_MAX_LEVEL else "Ausbauen\n%d Gold" % MetaData.building_cost(lvl)
	var up := _small_button(up_text, func() -> void:
		if Save.upgrade_building(id):
			toast("Ausgebaut auf Stufe %d!" % (lvl + 1))
		show_tab("basis")
	, 150, false)
	up.custom_minimum_size = Vector2(150, 70)
	up.disabled = lvl >= MetaData.BUILDING_MAX_LEVEL or Save.gold() < MetaData.building_cost(lvl)
	btns.add_child(up)
	return p


# --- Dialoge ---------------------------------------------------------------------

func _close_modal() -> void:
	if _modal:
		_modal.queue_free()
		_modal = null


func _modal_box(title: String) -> VBoxContainer:
	_close_modal()
	_modal = Control.new()
	_modal.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_modal.add_child(UiKit.dim(0.7))
	add_child(_modal)
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_modal.add_child(center)
	var p := _panel(Color(0.1, 0.11, 0.24, 0.98), Color(0.45, 0.55, 1.0))
	p.custom_minimum_size = Vector2(560, 0)
	center.add_child(p)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 16)
	p.add_child(v)
	v.add_child(UiKit.label(title, 34, UiKit.C_GOLD))
	return v


func _info(title: String, text: String) -> void:
	var v := _modal_box(title)
	var t := UiKit.wrap_label(text, 22)
	t.custom_minimum_size = Vector2(520, 0)
	v.add_child(t)
	v.add_child(UiKit.button("OK", _close_modal, 240))


func _reward_text(r: Dictionary) -> String:
	return "+%d %s" % [int(r["amount"]), MetaData.REWARD_NAMES.get(r["type"], r["type"])]


func _open_daily() -> void:
	var v := _modal_box("Tägliche Belohnung")
	if Save.daily_ready("daily_date"):
		v.add_child(_wrap_left("Schön, dass du da bist, Kommandant! Deine Belohnung für heute:\n\n+150 Gold  ·  +10 Edelsteine", 22))
		v.add_child(UiKit.button("Abholen", func() -> void:
			Save.add("gold", 150)
			Save.add("gems", 10)
			Save.mark_daily("daily_date")
			_close_modal()
			toast("+150 Gold · +10 Edelsteine")
			show_tab(current_tab)
		, 260))
	else:
		v.add_child(_wrap_left("Heute schon abgeholt. Morgen gibt es die nächste Belohnung.", 22))
		v.add_child(UiKit.button("OK", _close_modal, 240))


func _open_wheel() -> void:
	var v := _modal_box("Glücksrad")
	var wheel := Wheel.new()
	wheel.custom_minimum_size = Vector2(420, 420)
	wheel.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	v.add_child(wheel)
	if not Save.daily_ready("wheel_date"):
		v.add_child(_wrap_left("Heute schon gedreht. Morgen wieder!", 22))
		v.add_child(UiKit.button("OK", _close_modal, 240))
		return
	var spin := UiKit.button("Drehen!", func() -> void: pass, 260)
	spin.pressed.connect(func() -> void:
		spin.disabled = true
		var idx := randi() % MetaData.WHEEL.size()
		Save.mark_daily("wheel_date")
		wheel.spin_to(idx, func() -> void:
			var r: Dictionary = MetaData.WHEEL[idx]
			Save.add(r["type"], int(r["amount"]))
			_close_modal()
			_info("Glückwunsch!", _reward_text(r))
			show_tab(current_tab)
		)
	)
	v.add_child(spin)


func _open_energy() -> void:
	var v := _modal_box("Energie")
	var next := Save.energy_next()
	var txt := "Jeder Kampf kostet %d Energie. Alle %d Minuten kommt 1 Energie zurück." % [MetaData.ENERGY_COST, MetaData.ENERGY_REGEN / 60]
	if next > 0:
		txt += "\n\nNächste Energie in %d:%02d." % [next / 60, next % 60]
	v.add_child(_wrap_left(txt, 22))
	var buy := UiKit.button("Auffüllen · %d Edelsteine" % MetaData.SHOP_ENERGY_COST, func() -> void:
		_close_modal()
		_buy_energy()
	, 400)
	buy.disabled = Save.gems() < MetaData.SHOP_ENERGY_COST
	v.add_child(buy)
	v.add_child(UiKit.secondary(UiKit.button("Testphase: kostenlos auffüllen", func() -> void:
		Save.data["energy"] = MetaData.ENERGY_MAX
		Save.save_game()
		_close_modal()
		toast("Energie aufgefüllt (Testphase)")
		show_tab(current_tab)
	, 400)))
	v.add_child(UiKit.secondary(UiKit.button("Schließen", _close_modal, 400)))


func _open_bestiary() -> void:
	var lines := []
	for w in GameData.WORLDS:
		lines.append(String(w["name"]) + ":")
		for kind in w["kinds"]:
			var d: Dictionary = GameData.ENEMIES[kind]
			lines.append("   • %s (%s)" % [d["name"], d["tier"]])
	_info("Gegner hinter dem Wurmloch", "\n".join(PackedStringArray(lines)) + "\n\nAlle 5 Level wechselt die Welt hinter dem Wurmloch.")


func _open_settings() -> void:
	var v := _modal_box("Einstellungen")
	var ver := "Version %s" % (updater.current_name if updater else "?")
	if updater and updater.current_stamp != "":
		ver += " · Stand %s" % updater.current_stamp
	v.add_child(UiKit.label(ver, 20, UiKit.C_MUTED))
	var high: bool = Save.data.get("quality", "hoch") == "hoch"
	v.add_child(UiKit.secondary(UiKit.button("Grafik: %s" % ("Hoch (Leuchten, Schatten)" if high else "Sparsam"), func() -> void:
		Save.data["quality"] = "sparsam" if high else "hoch"
		Save.save_game()
		quality_changed.emit()
		_open_settings()
	, 420)))
	var snd: bool = Save.data.get("sound", true)
	var mus: bool = Save.data.get("music", true)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_child(UiKit.secondary(UiKit.button("Töne: %s" % ("an" if snd else "aus"), func() -> void:
		Sfx.set_sound(not snd)
		_open_settings()
	, 204)))
	row.add_child(UiKit.secondary(UiKit.button("Musik: %s" % ("an" if mus else "aus"), func() -> void:
		Sfx.set_music(not mus)
		_open_settings()
	, 204)))
	v.add_child(row)
	v.add_child(UiKit.button("Nach Updates suchen", func() -> void:
		_close_modal()
		if updater:
			updater.check(true)
		toast("Suche nach Updates …")
	, 420))
	v.add_child(UiKit.secondary(UiKit.button("Spielstand zurücksetzen", func() -> void:
		var c := _modal_box("Wirklich zurücksetzen?")
		c.add_child(_wrap_left("Gold, Edelsteine, Helden, Talente und Fortschritt gehen verloren.", 22))
		c.add_child(UiKit.button("Ja, zurücksetzen", func() -> void:
			Save.reset()
			selected_level = 1
			_close_modal()
			show_tab("kampf")
			toast("Spielstand zurückgesetzt")
		, 360))
		c.add_child(UiKit.secondary(UiKit.button("Abbrechen", _close_modal, 360)))
	, 420)))
	v.add_child(UiKit.secondary(UiKit.button("Schließen", _close_modal, 420)))


## Ergebnis eines Kampfs mit Belohnungen anzeigen (von main.gd aufgerufen).
func show_rewards(title: String, text: String, rewards: Array) -> void:
	var v := _modal_box(title)
	var t := _wrap_left(text, 22)
	t.custom_minimum_size = Vector2(520, 0)
	v.add_child(t)
	var grid := GridContainer.new()
	grid.columns = 2
	grid.add_theme_constant_override("h_separation", 20)
	grid.add_theme_constant_override("v_separation", 8)
	for r in rewards:
		var row := HBoxContainer.new()
		var icon_kind: String = {"gold": "gold", "gems": "gem", "stars": "star", "pass": "pass"}.get(r["type"], "cards")
		row.add_child(Icon.make(icon_kind, 36))
		row.add_child(UiKit.label(str(r["text"]), 21, UiKit.C_TEXT, HORIZONTAL_ALIGNMENT_LEFT))
		grid.add_child(row)
	v.add_child(grid)
	v.add_child(UiKit.button("Weiter", _close_modal, 260))


# --- Battle Pass ---------------------------------------------------------------------

func open_battle_pass() -> void:
	_close_modal()
	_modal = Control.new()
	_modal.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_modal)
	var bg := ColorRect.new()
	bg.color = Color(0.04, 0.05, 0.12, 0.98)
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_modal.add_child(bg)
	var frame := VBoxContainer.new()
	frame.anchor_left = 0.5
	frame.anchor_right = 0.5
	frame.anchor_bottom = 1.0
	frame.offset_left = _frame.offset_left
	frame.offset_right = _frame.offset_right
	frame.add_theme_constant_override("separation", 10)
	_modal.add_child(frame)

	var head := _panel(Color(0.4, 0.2, 0.75, 0.98), Color(0.8, 0.6, 1.0))
	var hv := VBoxContainer.new()
	head.add_child(hv)
	hv.add_child(UiKit.label("BATTLE PASS", 36, UiKit.C_GOLD))
	hv.add_child(UiKit.label(MetaData.PASS_SEASON, 22))
	var left_s := maxi(0, MetaData.PASS_END - int(Time.get_unix_time_from_system()))
	hv.add_child(UiKit.label("Endet in %d T · %d Std" % [left_s / 86400, (left_s % 86400) / 3600], 20, UiKit.C_MUTED))
	var bar := ProgressBar.new()
	bar.show_percentage = false
	bar.custom_minimum_size = Vector2(0, 28)
	bar.max_value = MetaData.PASS_POINTS_PER_LEVEL
	bar.value = Save.pass_progress()
	bar.add_theme_stylebox_override("fill", UiKit.box(Color(1.0, 0.75, 0.2), 8))
	hv.add_child(bar)
	var bl := UiKit.label("Stufe %d · %d/%d" % [Save.pass_level(), Save.pass_progress(), MetaData.PASS_POINTS_PER_LEVEL], 18)
	bl.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	bar.add_child(bl)
	frame.add_child(head)

	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	frame.add_child(scroll)
	var margin := MarginContainer.new()
	margin.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	for side in ["left", "right"]:
		margin.add_theme_constant_override("margin_" + side, 12)
	scroll.add_child(margin)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 8)
	margin.add_child(v)

	# Missionen
	v.add_child(UiKit.label("Tägliche Missionen", 26, UiKit.C_GOLD, HORIZONTAL_ALIGNMENT_LEFT))
	var m := Save.missions()
	for id in m["ids"]:
		var d := Save.mission_def(id)
		var prog := mini(int(m["progress"].get(id, 0)), int(d["goal"]))
		var done: bool = m["claimed"].has(id)
		var p := _panel()
		var h := HBoxContainer.new()
		h.add_theme_constant_override("separation", 10)
		p.add_child(h)
		h.add_child(Icon.make("check" if done else "pass", 40))
		var tv := VBoxContainer.new()
		tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		tv.add_child(UiKit.label(String(d["text"]) % int(d["goal"]), 20, UiKit.C_TEXT, HORIZONTAL_ALIGNMENT_LEFT))
		tv.add_child(UiKit.label("%d/%d · +%d Pass-Punkte" % [prog, int(d["goal"]), int(d["points"])], 17, UiKit.C_MUTED, HORIZONTAL_ALIGNMENT_LEFT))
		h.add_child(tv)
		var mission_id: String = id
		var b := _small_button("Erledigt" if done else "Abholen", func() -> void:
			if Save.claim_mission(mission_id):
				toast("+%d Pass-Punkte" % int(d["points"]))
			open_battle_pass()
		, 140)
		b.disabled = done or prog < int(d["goal"])
		h.add_child(b)
		v.add_child(p)

	# Belohnungsstufen
	var cols := HBoxContainer.new()
	var fl := UiKit.label("Kostenlos", 22, UiKit.C_TEXT)
	fl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	cols.add_child(fl)
	var pl := UiKit.label("Premium", 22, UiKit.C_GOLD)
	pl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	cols.add_child(pl)
	v.add_child(cols)
	for lvl in range(1, MetaData.PASS_LEVELS + 1):
		v.add_child(_pass_row(lvl))

	var bottom := HBoxContainer.new()
	bottom.add_theme_constant_override("separation", 10)
	frame.add_child(bottom)
	var all_btn := _small_button("Alles beanspruchen", func() -> void:
		var got := []
		for l in Save.pass_claimable():
			var r := Save.claim_pass(l)
			if not r.is_empty():
				got.append(_reward_text(r))
		toast(", ".join(PackedStringArray(got)) if not got.is_empty() else "Noch nichts abzuholen.")
		open_battle_pass()
	, 260)
	all_btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	all_btn.disabled = Save.pass_claimable().is_empty()
	bottom.add_child(all_btn)
	var up := _small_button("Premium", func() -> void:
		_info("Premium-Pass", "Der Premium-Pass verdoppelt die Belohnungen und kommt mit dem Play Store. In der Testphase gibt es nur die kostenlose Spur.")
	, 200, false)
	bottom.add_child(up)
	var back := _small_button("Zurück", func() -> void:
		_close_modal()
		show_tab(current_tab)
	, 160, false)
	bottom.add_child(back)


func _pass_row(lvl: int) -> Control:
	var reached := lvl <= Save.pass_level()
	var claimed: bool = Save.data["pass_claimed"].has(lvl)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 8)
	var free := MetaData.pass_reward(lvl, false)
	var prem := MetaData.pass_reward(lvl, true)
	var fp := _reward_cell(free, Color(0.15, 0.35, 0.8, 0.95) if reached else Color(0.1, 0.14, 0.3, 0.9), "check" if claimed else ("" if reached else "lock"))
	row.add_child(fp)
	var badge := UiKit.label(str(lvl), 26, UiKit.C_GOLD if reached else UiKit.C_MUTED)
	badge.custom_minimum_size = Vector2(56, 0)
	row.add_child(badge)
	var pp := _reward_cell(prem, Color(0.45, 0.35, 0.1, 0.9), "lock")
	row.add_child(pp)
	if reached and not claimed:
		var btn := _small_button("Holen", func() -> void:
			var r := Save.claim_pass(lvl)
			if not r.is_empty():
				toast(_reward_text(r))
			open_battle_pass()
		, 100)
		btn.custom_minimum_size = Vector2(100, 56)
		fp.get_child(0).add_child(btn)
	return row


func _reward_cell(r: Dictionary, color: Color, mark: String) -> PanelContainer:
	var p := _panel(color, Color(0.4, 0.5, 0.8))
	p.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	p.custom_minimum_size = Vector2(0, 76)
	var h := HBoxContainer.new()
	h.add_theme_constant_override("separation", 6)
	p.add_child(h)
	var kind: String = {"gold": "gold", "gems": "gem", "stars": "star"}.get(r["type"], "cards")
	h.add_child(Icon.make(kind, 40))
	var l := UiKit.label(str(int(r["amount"])), 22, UiKit.C_TEXT, HORIZONTAL_ALIGNMENT_LEFT)
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	h.add_child(l)
	if mark != "":
		h.add_child(Icon.make(mark, 30))
	return p


# --- Kleine gezeichnete Bausteine ----------------------------------------------------

## Rundes Heldenabzeichen mit Anfangsbuchstabe.
class HeroBadge extends Control:
	var color := Color.WHITE
	var text := ""

	func _draw() -> void:
		var c := size * 0.5
		var r := minf(size.x, size.y) * 0.45
		draw_circle(c, r + 4.0, Color(color.r, color.g, color.b, 0.3))
		draw_circle(c, r, color)
		draw_circle(c, r, Color(1, 1, 1, 0.35), false, 3.0)
		var font := ThemeDB.fallback_font
		var fs := int(r * 1.1)
		draw_string_outline(font, Vector2(0, c.y + fs * 0.36), text, HORIZONTAL_ALIGNMENT_CENTER, size.x, fs, 6, Color(0, 0, 0, 0.6))
		draw_string(font, Vector2(0, c.y + fs * 0.36), text, HORIZONTAL_ALIGNMENT_CENTER, size.x, fs, Color(1, 1, 1))


## Glücksrad mit 8 Feldern.
class Wheel extends Control:
	var angle := 0.0

	func spin_to(idx: int, done: Callable) -> void:
		var seg := TAU / MetaData.WHEEL.size()
		# Zeiger oben: Feld idx soll nach oben zeigen
		# Mitte von Feld idx liegt bei angle + (idx + 0.5) * seg - PI/2; oben ist -PI/2
		var want := fposmod(-(idx + 0.5) * seg, TAU)
		var target := angle + TAU * 5.0 + fposmod(want - angle, TAU)
		var tw := create_tween()
		tw.tween_property(self, "angle", target, 3.0).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
		tw.tween_callback(done)

	func _process(_d: float) -> void:
		queue_redraw()

	func _draw() -> void:
		var c := size * 0.5
		var r := minf(size.x, size.y) * 0.46
		var n := MetaData.WHEEL.size()
		var seg := TAU / n
		var font := ThemeDB.fallback_font
		for i in n:
			var a0 := angle + i * seg - PI * 0.5
			var pts := PackedVector2Array([c])
			for j in 9:
				var a := a0 + seg * j / 8.0
				pts.append(c + Vector2(cos(a), sin(a)) * r)
			draw_colored_polygon(pts, Color(0.55, 0.3, 0.95) if i % 2 == 0 else Color(0.25, 0.5, 0.95))
			var mid := a0 + seg * 0.5
			var w: Dictionary = MetaData.WHEEL[i]
			var txt := "%d %s" % [int(w["amount"]), String(MetaData.REWARD_NAMES[w["type"]]).left(4)]
			draw_string(font, c + Vector2(cos(mid), sin(mid)) * r * 0.62 - Vector2(40, -6), txt, HORIZONTAL_ALIGNMENT_CENTER, 80, 16, Color(1, 1, 1))
		draw_circle(c, r * 0.14, Color(1.0, 0.82, 0.25))
		draw_arc(c, r, 0, TAU, 64, Color(1, 1, 1, 0.8), 4.0)
		draw_colored_polygon(PackedVector2Array([c + Vector2(-16, -r - 18), c + Vector2(16, -r - 18), c + Vector2(0, -r + 10)]), Color(1.0, 0.3, 0.3))
