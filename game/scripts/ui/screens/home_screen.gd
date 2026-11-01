class_name HomeScreen
extends MockScreen
## Hauptbildschirm „Abenteuer-Pfad“ (Mockup „1 · Abenteuer-Pfad“): Welt mit fünf Leveln als Pfad,
## Angebote links, Täglich/Glücksrad/Missionen/Shop rechts, großer Spielen-Knopf.
## Die Level-Knoten zeichnet das Spiel selbst (geschafft, ausgewählt, gesperrt) mit den Bildern
## aus dem Mockup.

const BOSS_RECT := Rect2(168, 236, 64, 64)

var _path: PathLayer


func _init(m: MainMenu) -> void:
	super("home", m, {"level": "12", "energy": "25/30", "gold": "4.573", "gems": "350"})


func _ready() -> void:
	super()
	_path = PathLayer.new()
	_path.home = self
	place_at(_path, Rect2(0, 0, W, H))
	_path.mouse_filter = Control.MOUSE_FILTER_PASS
	bind()


func world() -> int:
	return GameData.world_of(menu.selected_level)


func bind() -> void:
	set_text("Stufe 2", "Stufe %d" % Save.pass_level())
	set_text("Abholen!", "Abholen!" if not Save.pass_claimable().is_empty() else "Ansehen")
	var w := world()
	set_text("WELT 1", "WELT %d" % (w + 1))
	var name: String = GameData.WORLDS[w]["name"]
	var dash := name.find("-")
	set_text("Schleim-Welt", name.substr(0, dash + 1) + "\n" + name.substr(dash + 1) if dash > 0 else name)
	set_text("Level 4 · 5", "Level %d · %d" % [menu.selected_level, MetaData.ENERGY_COST])
	var badges := {"Tägliche Belohnung": Save.daily_ready("daily_date"), "Glücksrad": Save.daily_ready("wheel_date"),
		"Missionen": menu.mission_ready()}
	for b in buttons():
		var lab := str(b.info.get("label", ""))
		if badges.has(lab):
			b.badge = bool(badges[lab])
	var prev := button("Vorherige Welt")
	if prev:
		prev.modulate.a = 1.0 if w > 0 else 0.35
	var next := button("Nächste Welt")
	if next:
		next.modulate.a = 1.0 if (w + 1) * GameData.LEVELS_PER_WORLD < Save.max_level() else 0.35
	if _path:
		_path.queue_redraw()


func handle(b: Dictionary) -> bool:
	var label := str(b.get("label", ""))
	var href := str(b.get("href", ""))
	match label:
		"Vorherige Welt":
			_change_world(-1)
			return true
		"Nächste Welt":
			_change_world(1)
			return true
		"Tägliche Belohnung":
			menu.open_daily()
			return true
	if href == "#kampf" and b.get("rect", [0, 0, 0, 0])[1] > 600 and b.get("rect")[1] < 760:
		menu.play_selected()  # großer Spielen-Knopf
		return true
	return false


func _change_world(d: int) -> void:
	var w := clampi(world() + d, 0, GameData.WORLDS.size() - 1)
	var first := w * GameData.LEVELS_PER_WORLD + 1
	if first > Save.max_level():
		return
	var last := first + GameData.LEVELS_PER_WORLD - 1
	menu.selected_level = clampi(Save.max_level(), first, last)
	bind()


## Level-Knoten, Sterne, Held und Namensschild – mit den Bildern aus dem Mockup
class PathLayer:
	extends Control
	var home: HomeScreen
	var _cache := {}

	func _ready() -> void:
		# Bilder vorab laden; frisch geladene Bilder sind im ersten Bild noch nicht bereit
		for id in ["node_done", "node_cur", "cur_glow", "map_hero", "lvl_tag", "boss_lock"]:
			_tex(id)
		await get_tree().process_frame
		queue_redraw()

	func _slot_rects() -> Array[Rect2]:
		var out: Array[Rect2] = []
		for id in ["node_done", "node_done_1", "node_done_2", "node_cur"]:
			out.append(home.live_rect(id))
		out.append(BOSS_RECT)
		return out

	func _tex(id: String) -> Texture2D:
		if not _cache.has(id):
			var l: Dictionary = home._live_info.get(id, {})
			_cache[id] = load("res://ui_mock/home/" + str(l.get("img", ""))) if str(l.get("img", "")) != "" else null
		return _cache[id]

	func _img_rect(id: String) -> Rect2:
		var ir: Array = home._live_info.get(id, {}).get("img_rect", [0, 0, 0, 0])
		return Rect2(ir[0], ir[1], ir[2], ir[3])

	func _r(r: Rect2) -> Rect2:
		return Rect2(r.position * home.s, r.size * home.s)

	## Bild eines Live-Elements so zeichnen, dass seine Mitte bei center liegt
	func _draw_at(id: String, center: Vector2, scale_to := 1.0, mod := Color.WHITE) -> void:
		var tex := _tex(id)
		if tex == null:
			return
		var src := home.live_rect(id)
		var ir := _img_rect(id)
		var k := scale_to
		var off := (ir.position - src.get_center()) * k
		draw_texture_rect(tex, _r(Rect2(center + off, ir.size * k)), false, mod)

	func _draw() -> void:
		var w := home.world()
		var first := w * GameData.LEVELS_PER_WORLD + 1
		var sel := home.menu.selected_level
		var slots := _slot_rects()
		var cur_src := home.live_rect("node_cur")
		for k in 4:
			var lvl := first + k
			var c := slots[k].get_center()
			var won: bool = Save.data["won_levels"].has("N" + str(lvl))
			var open := lvl <= Save.max_level()
			if lvl == sel:
				_draw_at("cur_glow", c)
				_draw_at("node_cur", c)
				_num(c, lvl, 28, Color(0.35, 0.16, 0.0))
			else:
				var mod := Color.WHITE if open else Color(0.45, 0.45, 0.55)
				_draw_at("node_done", c, 1.0, mod)
				_num(c, lvl, 20, Color(1.0, 0.97, 0.92) if open else Color(0.8, 0.8, 0.85))
			if won:
				_stars(Vector2(c.x, slots[k].end.y + 9.0) if k < 3 or lvl != sel else Vector2(c.x, c.y + 41.0))
		var boss := first + GameData.LEVELS_PER_WORLD - 1
		if boss > Save.max_level():
			_draw_at("boss_lock", home.live_rect("boss_lock").get_center())
		if sel == boss:
			_draw_at("cur_glow", slots[4].get_center(), 1.05)
		# Held und Namensschild am ausgewählten Level
		var idx := clampi(sel - first, 0, 4)
		var sc := slots[idx].get_center()
		var hero_off := home.live_rect("map_hero").get_center() - cur_src.get_center()
		var tag_off := home.live_rect("lvl_tag").get_center() - cur_src.get_center()
		_draw_at("map_hero", sc + hero_off)
		_draw_at("lvl_tag", sc + tag_off)
		var tag_rect := home.live_rect("lvl_tag")
		var name := GameData.level_name(sel)
		var font := MockFonts.font("Nunito", 800)
		var fs := roundi(12 * home.s)
		var tw := font.get_string_size(name, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var tc := (sc + tag_off) * home.s
		if tw > tag_rect.size.x * home.s - 16.0 * home.s:
			# längerer Name: Schild breiter zeichnen
			var r := Rect2(tc - Vector2(tw * 0.5 + 10.0 * home.s, tag_rect.size.y * 0.5 * home.s), Vector2(tw + 20.0 * home.s, tag_rect.size.y * home.s))
			var sb := StyleBoxFlat.new()
			sb.bg_color = Color(0.08, 0.05, 0.19, 0.7)
			sb.set_corner_radius_all(roundi(10 * home.s))
			draw_style_box(sb, r)
		draw_string(font, Vector2(tc.x - tw * 0.5, tc.y + (font.get_ascent(fs) - font.get_descent(fs)) * 0.5), name, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(1.0, 0.97, 0.92))

	func _num(c: Vector2, n: int, size: int, col: Color) -> void:
		var font := MockFonts.font("Fredoka", 700)
		var fs := roundi(size * home.s)
		var t := str(n)
		var tw := font.get_string_size(t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var p := c * home.s + Vector2(-tw * 0.5, (font.get_ascent(fs) - font.get_descent(fs)) * 0.5)
		draw_string(font, p, t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)

	func _stars(c: Vector2) -> void:
		for j in 3:
			var p := (c + Vector2((j - 1) * 13.0, 0)) * home.s
			var pts := PackedVector2Array()
			for q in 10:
				var rr := 6.0 * home.s if q % 2 == 0 else 2.7 * home.s
				pts.append(p + Vector2.from_angle(-PI * 0.5 + q * PI / 5.0) * rr)
			draw_colored_polygon(pts, Color(1.0, 0.85, 0.29))

	func _gui_input(e: InputEvent) -> void:
		if e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT:
			var p := get_local_mouse_position() / home.s
			var first := home.world() * GameData.LEVELS_PER_WORLD + 1
			var slots := _slot_rects()
			for k in 5:
				if slots[k].grow(8.0).has_point(p):
					var lvl := first + k
					if lvl <= Save.max_level():
						home.menu.selected_level = lvl
						home.bind()
					else:
						home.menu.toast("Erst das Level davor schaffen")
					accept_event()
					return
