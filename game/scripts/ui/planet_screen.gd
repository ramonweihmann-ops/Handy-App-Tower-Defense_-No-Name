class_name PlanetScreen
extends MockView
## „Neuer Planet entdeckt“ (Mockup „Neuer Planet entdeckt · Dschungelmond“, ui_mock/neuer_planet):
## erscheint einmal vor dem ersten Level eines neuen Planeten. Hintergrund, Farben, Symbol, Texte
## und die Reihe aller Planeten setzt das Spiel je Planet; Banner und Leuchten sind im Export weiß
## bzw. grau und werden hier in der Farbe des Planeten eingefärbt.

signal go_pressed

const BLUR := """
shader_type canvas_item;
uniform float radius = 8.0;
void fragment() {
	vec2 px = TEXTURE_PIXEL_SIZE * radius * 0.5;
	vec4 c = vec4(0.0);
	for (int x = -2; x <= 2; x++) {
		for (int y = -2; y <= 2; y++) {
			c += texture(TEXTURE, UV + vec2(float(x), float(y)) * px);
		}
	}
	COLOR = c / 25.0;
}
"""
## radial-gradient(80% 40% at 50% 30%, Leuchtfarbe, durchsichtig 70%)
const GLOW := """
shader_type canvas_item;
uniform vec4 glow : source_color;
void fragment() {
	vec2 d = (UV - vec2(0.5, 0.3)) / vec2(0.8, 0.4);
	float a = 1.0 - clamp(length(d) / 0.7, 0.0, 1.0);
	COLOR = vec4(glow.rgb, glow.a * a);
}
"""

var level := 51
var _id := ""
var _accent := Color.WHITE
var _dark := Color.BLACK
var _rays: TextureRect
var _planet: TextureRect
var _layer: Control
var _t := 0.0


func _init(level_: int) -> void:
	level = level_
	_id = Battlefields.for_level(level)
	super("neuer_planet")


func _ready() -> void:
	super()
	_fill.visible = false
	var d: Dictionary = Battlefields.FIELDS[_id]
	_accent = d.get("accent", Color.WHITE)
	_dark = d.get("dark", Color(0.2, 0.2, 0.4))
	# Hintergrund: unscharfes Schlachtfeld des neuen Planeten, abgedunkelt, mit Leuchten
	var field := TextureRect.new()
	field.texture = Battlefields.texture(_id)
	field.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	field.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	field.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	field.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var blur := ShaderMaterial.new()
	blur.shader = Shader.new()
	blur.shader.code = BLUR
	field.material = blur
	var dim := ColorRect.new()
	dim.color = Color(8 / 255.0, 6 / 255.0, 24 / 255.0, 0.74)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var glow := ColorRect.new()
	glow.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	glow.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var gm := ShaderMaterial.new()
	gm.shader = Shader.new()
	gm.shader.code = GLOW
	gm.set_shader_parameter("glow", Color(_accent, 0.45))
	glow.material = gm
	for k in [glow, dim, field]:
		add_child(k)
		move_child(k, 0)
	_rays = live_image("rays")
	if _rays:
		_live_layer.move_child(_rays, 0)
	var banner := live_image("banner")
	if banner:
		banner.modulate = _accent
	var halo := live_image("halo")
	if halo:
		halo.modulate = Color(_accent, 0.9)
	_planet = TextureRect.new()
	_planet.texture = Battlefields.icon(_id)
	_planet.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_planet.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_planet.mouse_filter = Control.MOUSE_FILTER_IGNORE
	place("planet", _planet)
	_layer = Layer.new()
	_layer.view = self
	place_at(_layer, Rect2(0, 0, W, H))
	_build_row()
	_fill_texts()
	button_pressed.connect(func(_b: Dictionary) -> void: go_pressed.emit())
	# Auftritt wie im Mockup: alles wächst kurz auf
	pivot_offset = size * 0.5
	scale = Vector2(0.94, 0.94)
	modulate.a = 0.0
	var tw := create_tween().set_parallel(true).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_property(self, "scale", Vector2.ONE, 0.35)
	tw.tween_property(self, "modulate:a", 1.0, 0.2)


func _process(delta: float) -> void:
	_t += delta
	if _rays:
		_rays.rotation += delta * TAU / 40.0
	if _planet and _live.has("planet"):
		var r: Rect2 = _live["planet"]
		_planet.position = to_screen(r.position + Vector2(0, -2.5 + 2.5 * cos(_t * TAU / 3.0)))


func _fill_texts() -> void:
	var n := Battlefields.planet_number(level)
	var total := Battlefields.ADVENTURE.size()
	var last := n == total
	var d: Dictionary = Battlefields.FIELDS[_id]
	var first := (n - 1) * 10 + 1
	set_text("PLANET 6 VON 15", "PLANET %d VON %d%s" % [n, total, " · FINALE" if last else ""])
	set_text("Dschungelmond", str(d["name"]))
	set_text("Level 51–60", "Level %d–%d%s" % [first, first + 9, " · Finale" if last else ""])
	set_text_color("Level 51–60", _accent)
	set_text("Urwald auf schwebenden Felsen. Hier lauern Gegner mit Ranken und Blüten.", _wrap(str(d.get("desc", "")), 318.0))
	var w0 := GameData.world_of(first)
	set_text("Rankendickicht", str(GameData.WORLDS[w0]["name"]))
	set_text("51–55", "%d–%d" % [first, first + 4])
	set_text("Blütenwipfel", str(GameData.WORLDS[mini(w0 + 1, GameData.WORLDS.size() - 1)]["name"]))
	set_text("56–60", "%d–%d" % [first + 5, first + 9])
	set_text("+50", "+%d" % MetaData.PLANET_GIFT_GEMS)
	set_text("LOS GEHT'S · LEVEL 51", "LOS GEHT'S · LEVEL %d" % level)
	for t in texts_of_button(0):
		if str(t["text"]) == "5":
			set_text(int(t["i"]), str(MetaData.ENERGY_COST))


## Schilder „WELT n“ in der dunklen Farbe des Planeten und die Reihe aller Planeten
func _draw_layer(ci: CanvasItem) -> void:
	var first := (Battlefields.planet_number(level) - 1) * 10 + 1
	var w0 := GameData.world_of(first)
	for k in 2:
		var id := "welt" if k == 0 else "welt_1"
		if not _live.has(id):
			continue
		var r: Rect2 = _live[id]
		MockPaint.rrect(ci, Rect2(r.position * s, r.size * s), 8 * s, _dark)
		MockPaint.text(self, ci, "WELT %d" % (w0 + k + 1), r, "Nunito", 800, 10, "rgb(255, 255, 255)")
	if not _live.has("row"):
		return
	var c := _row_center()
	ci.draw_circle(c * s, 21.0 * s, Color(_accent, 0.22))
	ci.draw_circle(c * s, 15.0 * s, Color(10 / 255.0, 6 / 255.0, 30 / 255.0, 0.5))
	ci.draw_arc(c * s, 16.0 * s, 0, TAU, 40, _accent, 2.0 * s, true)


const ROW_SMALL := 19.0
const ROW_BIG := 30.0
const ROW_GAP := 3.0


## Mitte des neuen Planeten in der Reihe (Mockup-Punkte)
func _row_center() -> Vector2:
	var row: Rect2 = _live["row"]
	var count := Battlefields.ADVENTURE.size()
	var width := (count - 1) * (ROW_SMALL + ROW_GAP) + ROW_BIG
	var n := Battlefields.planet_number(level)
	return Vector2(row.get_center().x - width * 0.5 + (n - 1) * (ROW_SMALL + ROW_GAP) + ROW_BIG * 0.5, row.get_center().y)


## Reihe aller Planeten: entdeckte farbig, der neue groß mit Ring, die übrigen als dunkle Schatten
func _build_row() -> void:
	if not _live.has("row"):
		return
	var row: Rect2 = _live["row"]
	var count := Battlefields.ADVENTURE.size()
	var n := Battlefields.planet_number(level)
	var x := row.get_center().x - ((count - 1) * (ROW_SMALL + ROW_GAP) + ROW_BIG) * 0.5
	for i in count:
		var k := i + 1
		var isz := 28.0 if k == n else ROW_SMALL
		var slot := ROW_BIG if k == n else ROW_SMALL
		var tr := TextureRect.new()
		tr.texture = Battlefields.icon(str(Battlefields.ADVENTURE[i]))
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
		if k > n:
			tr.modulate = Color(0, 0, 0, 0.45)
		place_at(tr, Rect2(x + (slot - isz) * 0.5, row.get_center().y - isz * 0.5, isz, isz))
		x += slot + ROW_GAP


## Text in höchstens zwei Zeilen umbrechen (Nunito 700, 13 Punkte wie im Mockup)
func _wrap(txt: String, width: float) -> String:
	if MockPaint.text_width(txt, "Nunito", 700, 13) <= width:
		return txt
	var words := txt.split(" ")
	var best := txt
	for k in range(1, words.size()):
		var a := " ".join(words.slice(0, k))
		var b := " ".join(words.slice(k))
		var wa := MockPaint.text_width(a, "Nunito", 700, 13)
		var wb := MockPaint.text_width(b, "Nunito", 700, 13)
		# wie der Browser: die erste Zeile so voll wie möglich
		if wa <= width and wb <= width:
			best = a + "\n" + b
	return best


class Layer:
	extends Control
	var view: PlanetScreen

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE

	func _draw() -> void:
		view._draw_layer(self)
