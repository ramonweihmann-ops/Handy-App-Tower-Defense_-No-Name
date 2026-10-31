class_name LoadingScreen
extends Control
## Ladebildschirm beim Start der App: Weltraum mit Wurmloch, Titel und eine Energiekugel,
## die als Ladebalken über eine Bahn rollt. Während er zu sehen ist, bereitet main.gd
## Figuren und Effekte vor (siehe main.gd, _warm_up), damit es später nicht ruckelt.

const TIPS := [
	"Tipp: Tore in der Kugelbahn verdoppeln Kugeln – mehr Kugeln, mehr Munition.",
	"Tipp: Leuchtet der Hebel, zieh ihn für eine Überladung voller Kugeln.",
	"Tipp: Feuer-Tore machen Brandmunition, Eis-Tore bremsen Gegner.",
	"Tipp: Oben siehst du, welche Gegner als Nächstes kommen.",
]

var progress := 0.0
var _shown := 0.0
var _status: Label
var _bg_mat: ShaderMaterial
var _t := 0.0
var _font: Font


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	_font = ThemeDB.fallback_font
	var bg := ColorRect.new()
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_bg_mat = ShaderMaterial.new()
	_bg_mat.shader = preload("res://shaders/loading_bg.gdshader")
	bg.material = _bg_mat
	add_child(bg)
	# Bahn und Kugel werden über dem Hintergrund gezeichnet
	var overlay := Control.new()
	overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
	overlay.draw.connect(_draw_overlay.bind(overlay))
	add_child(overlay)
	set_meta("overlay", overlay)

	var title := UiKit.label("Station am Wurmloch", 54, UiKit.C_GOLD)
	title.add_theme_constant_override("outline_size", 12)
	title.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	title.offset_top = 70
	title.offset_bottom = 140
	add_child(title)
	var sub := UiKit.label("Pilot", 26, UiKit.C_MUTED)
	sub.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	sub.offset_top = 140
	sub.offset_bottom = 180
	add_child(sub)

	_status = UiKit.label("Wurmloch wird geöffnet …", 26)
	_status.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	_status.offset_top = -232
	_status.offset_bottom = -192
	add_child(_status)
	var tip := UiKit.wrap_label(TIPS[randi() % TIPS.size()], 20, UiKit.C_MUTED)
	tip.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	tip.offset_left = 40
	tip.offset_right = -40
	tip.offset_top = -120
	tip.offset_bottom = -40
	add_child(tip)


func set_progress(value: float, status: String) -> void:
	progress = clampf(value, 0.0, 1.0)
	_status.text = status


func _process(delta: float) -> void:
	_t += delta
	_shown = move_toward(_shown, progress, delta * 1.5)
	if size.y > 0.0:
		_bg_mat.set_shader_parameter("aspect", Vector2(size.x / size.y, 1.0))
	(get_meta("overlay") as Control).queue_redraw()


func _draw_overlay(c: Control) -> void:
	var w := minf(c.size.x - 80.0, 560.0)
	var y := c.size.y - 300.0
	var x0 := (c.size.x - w) * 0.5
	var track := Rect2(x0, y - 9.0, w, 18.0)
	c.draw_rect(track.grow(3.0), Color(0.25, 0.4, 0.6))
	c.draw_rect(track, Color(0.04, 0.05, 0.1))
	var fill_w := w * _shown
	c.draw_rect(Rect2(track.position, Vector2(fill_w, track.size.y)), Color(0.2, 0.85, 1.0, 0.85))
	# Stifte auf der Bahn, wie in der Kugelbahn
	var k := 0
	while k * 40.0 < w:
		c.draw_circle(Vector2(x0 + k * 40.0 + 20.0, y), 3.0, Color(0.8, 0.95, 1.0, 0.5))
		k += 1
	# Energiekugel rollt mit
	var ball := Vector2(x0 + fill_w, y)
	var glow := 0.5 + 0.5 * sin(_t * 6.0)
	c.draw_circle(ball, 26.0, Color(1.0, 0.82, 0.28, 0.18 + 0.1 * glow))
	c.draw_circle(ball, 17.0, Color(1.0, 0.82, 0.28))
	c.draw_circle(ball, 10.0, Color(1.0, 0.92, 0.6))
	c.draw_circle(ball + Vector2(-5, -5), 5.0, Color(1, 1, 1, 0.85))
	var pct := "%d %%" % int(round(_shown * 100.0))
	c.draw_string(_font, Vector2(0, y + 52.0), pct, HORIZONTAL_ALIGNMENT_CENTER, c.size.x, 22, Color(1, 0.9, 0.55))
