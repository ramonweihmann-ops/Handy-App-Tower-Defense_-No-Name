class_name SuccessScreen
extends MockView
## Erfolgsmeldung nach jedem Gewinn von Karten oder Rohstoffen (Mockups „Erfolgsmeldung · …“).
## Banner „ABGEHOLT!“, Strahlen, Texte und Knopf kommen aus dem Mockup (ui_mock/erfolg); in der
## Mitte zeichnet das Spiel den Gewinn selbst: Diamant, Münze und Blitz drehen sich in 3D (jedes
## Bild neu berechnet, daher ohne Ruckeln), bei Heldenkarten steht der ganze Held auf einer Plattform.
##
## item: {type: gems|gold|energy|cards|stars|pass|hero, amount, hero (bei hero), label (optional)}

signal done

const CENTER := Rect2(110, 262, 170, 170)
const GLOW := {
	"gems": [Color(1.0, 0.44, 0.82, 0.45), Color(0.55, 0.24, 0.78, 0.25)],
	"gold": [Color(1.0, 0.84, 0.27, 0.5), Color(0.78, 0.51, 0.08, 0.25)],
	"energy": [Color(0.49, 1.0, 0.54, 0.45), Color(0.16, 0.63, 0.31, 0.25)],
	"hero": [Color(0.44, 0.71, 1.0, 0.55), Color(0.23, 0.39, 0.85, 0.25)],
	"pass": [Color(0.75, 0.55, 1.0, 0.5), Color(0.4, 0.2, 0.85, 0.25)],
	"other": [Color(0.75, 0.55, 1.0, 0.45), Color(0.4, 0.25, 0.8, 0.25)],
}
const LABEL_COLOR := {"gems": "rgb(255, 184, 234)", "gold": "rgb(255, 226, 122)", "energy": "rgb(157, 255, 122)",
	"hero": "rgb(143, 208, 255)", "cards": "rgb(143, 208, 255)", "stars": "rgb(255, 226, 122)", "pass": "rgb(200, 170, 255)"}
const NAMES := {"gems": "Edelsteine", "gold": "Gold", "energy": "Energie", "cards": "Heldenkarten", "stars": "Sterne",
	"pass": "Pass-Punkte"}

var item := {}
var source := ""
## Zusatzzeile unten (z. B. „Serie: 10 Tage · noch 4 bis zur Treue-Truhe“), leer = keine
var chip_text := ""
var _layer: CenterLayer
var _rays: TextureRect
var _hero_view: HeroView3D
var _icon: Icon
var _t := 0.0


func _init(item_: Dictionary, source_ := "", chip := "") -> void:
	item = item_
	source = source_
	chip_text = chip
	super("erfolg")


func _ready() -> void:
	super()
	_fill.visible = false
	var dim := ColorRect.new()
	dim.color = Color(8 / 255.0, 6 / 255.0, 24 / 255.0, 0.88)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(dim)
	move_child(dim, 0)
	_rays = live_image("rays")
	if _rays:
		_live_layer.move_child(_rays, 0)
	var kind := _kind()
	set_text("Tag 3 · Tägliche Belohnung", source)
	set_text("×20", "×" + MockScreen.num(int(item.get("amount", 1))))
	var label: String = item.get("label", "")
	if label == "":
		label = NAMES.get(kind, "")
		if kind == "hero":
			label = "Heldenkarten · " + String(GameData.HEROES[item["hero"]]["name"])
	set_text("Edelsteine", label)
	_set_text_color("Edelsteine", LABEL_COLOR.get(kind, "rgb(255, 247, 234)"))
	if kind == "hero":
		# Held komplett statt Symbol, die Anzahl rückt etwas tiefer
		_move_text("×20", 8.0)
		_move_text("Edelsteine", 8.0)
	_layer = CenterLayer.new()
	_layer.view = self
	place_at(_layer, Rect2(0, 0, W, H))
	if kind == "hero":
		_hero_view = HeroView3D.make(str(item["hero"]))
		_hero_view.aspect = 200.0 / 210.0
		_hero_view.fig = 0.9
		_hero_view.feet = 0.97
		_hero_view.mouse_filter = Control.MOUSE_FILTER_IGNORE
		place_at(_hero_view, Rect2(95, 226, 200, 210))
	elif not kind in ["gems", "gold", "energy", "pass"]:
		_icon = Icon.make({"cards": "cards", "stars": "star", "pass": "pass"}.get(kind, "star"), 84)
		_icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
		place_at(_icon, Rect2(CENTER.get_center() - Vector2(42, 42), Vector2(84, 84)))
	button_pressed.connect(func(_b: Dictionary) -> void:
		Sfx.play("click")
		done.emit())
	# Auftritt
	pivot_offset = size * 0.5
	scale = Vector2(0.9, 0.9)
	modulate.a = 0.0
	var tw := create_tween().set_parallel(true).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_property(self, "scale", Vector2.ONE, 0.35)
	tw.tween_property(self, "modulate:a", 1.0, 0.2)
	Sfx.play("win", 0.0)


func _kind() -> String:
	var t := str(item.get("type", ""))
	if t == "hero" or item.has("hero"):
		return "hero"
	return t


func _set_text_color(key: String, css: String) -> void:
	for t in data.get("texts", []):
		if str(t["text"]) == key:
			t["color"] = css
	_redraw_texts()


func _move_text(key: String, dy: float) -> void:
	for t in data.get("texts", []):
		if str(t["text"]) == key:
			for l in t["lines"]:
				var r: Array = l["rect"]
				r[1] = float(r[1]) + dy
	_redraw_texts()


func _process(delta: float) -> void:
	_t += delta
	if _rays:
		_rays.rotation += delta * TAU / 40.0
	if _hero_view:
		_hero_view.position.y = to_screen(Vector2(0, 226)).y + sin(_t * 2.8) * 3.0 * s
	if _icon:
		# Umdrehen um die senkrechte Achse (gleichmäßig) und leichtes Wippen
		_icon.pivot_offset = _icon.size * 0.5
		_icon.scale.x = maxf(0.08, absf(cos(_t * PI / 1.6)))
		_icon.position.y = to_screen(Vector2(0, CENTER.get_center().y - 42.0 + sin(_t * 3.9) * 3.0)).y
	if _layer:
		_layer.queue_redraw()


class CenterLayer:
	extends Control
	var view: SuccessScreen

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE

	func _draw() -> void:
		var s := view.s
		var kind := view._kind()
		var g: Array = SuccessScreen.GLOW.get(kind, SuccessScreen.GLOW["other"])
		if kind == "hero":
			_draw_platform(s, g)
		else:
			_glow(SuccessScreen.CENTER.get_center() * s, 85.0 * s, g[0], g[1])
		var bob := sin(view._t * 3.9) * 3.0
		# Symbol: 100 Punkte groß, Mittelpunkt wie im Mockup
		var k := 100.0 / 24.0 * s
		var o := (SuccessScreen.CENTER.get_center() + Vector2(0, bob)) * s - Vector2(12, 12) * k
		match kind:
			"gems":
				Gem3D.draw_gem(self, o, k, view._t)
			"gold":
				Gem3D.draw_coin(self, o, k, view._t)
			"energy":
				Gem3D.draw_bolt(self, o, k, view._t)
			"pass":
				Gem3D.draw_ticket(self, o, k, view._t)
		if view.chip_text != "":
			_chip(s)
		if kind == "hero":
			_hero_bar(s)

	func _glow(c: Vector2, r: float, inner: Color, mid: Color) -> void:
		for i in 12:
			var f := 1.0 - i / 12.0
			var col := mid.lerp(inner, f)
			col.a = lerpf(0.0, inner.a, f) * 0.5
			draw_circle(c, r * (0.3 + 0.7 * (1.0 - f) + 0.05) , col)

	func _draw_platform(s: float, g: Array) -> void:
		var c := Vector2(195, 430) * s
		_glow(Vector2(195, 330) * s, 110.0 * s, g[0], g[1])
		Gem3D.ellipse(self, c, Vector2(75, 15) * s, Color(0.55, 0.82, 1.0, 0.55))
		Gem3D.ellipse(self, c, Vector2(60, 11) * s, Color(0.75, 0.9, 1.0, 0.35))
		var p := fmod(view._t / 1.8, 1.0)
		Gem3D.ellipse_line(self, c, Vector2(lerpf(40, 80, p), lerpf(7, 13, p)) * s, Color(0.75, 0.96, 1.0, 0.9 * (1.0 - p)), 2.0 * s)

	func _chip(s: float) -> void:
		var w := MockPaint.text_width(view.chip_text, "Nunito", 800, 13) + 28.0
		var r := Rect2(195 - w * 0.5, 530, w, 34)
		MockPaint.rrect(self, Rect2(r.position * s, r.size * s), 12 * s, Color(10 / 255.0, 6 / 255.0, 30 / 255.0, 0.6))
		MockPaint.border(self, Rect2(r.position * s, r.size * s), 12 * s, Color(1, 1, 1, 0.18), 1 * s)
		MockPaint.text(view, self, view.chip_text, r, "Nunito", 800, 13, "rgb(255, 247, 234)")

	func _hero_bar(s: float) -> void:
		var id := str(view.item["hero"])
		var lvl := Save.hero_level(id)
		var have := Save.hero_cards(id)
		var need := MetaData.hero_cards_needed(lvl)
		var y := 576.0 if view.chip_text != "" else 536.0
		var hero_name := String(GameData.HEROES[id]["name"])
		MockPaint.text(view, self, hero_name, Rect2(75, y, 50, 16), "Nunito", 800, 12, "rgb(207, 234, 255)")
		var bar := Rect2(128, y, 187, 16)
		MockPaint.rrect(self, Rect2(bar.position * s, bar.size * s), 8 * s, Color(10 / 255.0, 6 / 255.0, 30 / 255.0, 0.75))
		var ratio := 1.0 if lvl >= MetaData.HERO_MAX_LEVEL else clampf(float(have) / float(maxi(1, need)), 0.0, 1.0)
		if ratio * bar.size.x > 1.0:
			var ready := ratio >= 1.0
			MockPaint.rrect_h(self, Rect2(bar.position * s, Vector2(bar.size.x * ratio, bar.size.y) * s), 8 * s,
				Color("#7dff8a") if ready else Color("#6fe0ff"), Color("#3fbf3a") if ready else Color("#3a8cff"))
		MockPaint.border(self, Rect2(bar.position * s, bar.size * s), 8 * s, Color(1, 1, 1, 0.2), 1 * s)
		var txt := "Höchste Stufe" if lvl >= MetaData.HERO_MAX_LEVEL else ("%d/%d · Aufwertbar!" % [have, need] if have >= need else "%d/%d Karten" % [have, need])
		MockPaint.text(view, self, txt, bar, "Nunito", 800, 10, "rgb(255, 255, 255)")
