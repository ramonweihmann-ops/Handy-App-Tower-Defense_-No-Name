class_name HeroLockBoard
extends MockScreen
## Fenster „Champion noch gesperrt“ nach dem freigegebenen Mockup „Helden · Meldung: Champion noch gesperrt“
## (Export ui_mock/helden_meldung, durchsichtig). Öffnet sich beim Antippen eines gesperrten Champions auf der
## Heldenseite und füllt sich für jeden Helden selbst: Name, Bildfeld in der Farbe des Helden mit der Figur,
## Rolle, Waffe, Stärke, Bedingung („Kommt mit Level …“), Beschreibung und FREISCHALTEN für Edelsteine.
## Dahinter liegt die Heldenseite weichgezeichnet und abgedunkelt (shaders/hintergrund_weich.gdshader).

## Held, den das Fenster zeigt (vor menu.open_board("Helden-Meldung.dc.html") setzen)
static var hero := "fritzi"

## Stärke je Waffenart, kurz wie im Mockup („Feuerkegel · setzt in Brand“)
const STRENGTH := {
	"revolver": "Sechs Schuss · der letzte fächert auf",
	"mg": "Dauerfeuer",
	"rocket": "Flächenschaden",
	"tesla": "Kettenblitz · trifft die Nachbarn",
	"cryo": "Friert ein · bremst",
	"shotgun": "Stark aus der Nähe",
	"sniper": "Durchschlägt mehrere Gegner",
	"flamer": "Feuerkegel · setzt in Brand",
	"beam": "Strahl durch die ganze Reihe",
	"drone": "Repariert den Schild",
	"cannon": "Stößt Gegner zurück",
	"gravity": "Zieht zusammen · bremst",
}
## Werte rechtsbündig in den Zeilen (rechter Innenrand) und Zeilenmitten (Mockup-Punkte)
const VALUE_RIGHT := 338.0
const ROW_Y := {"role": 423.5, "weapon": 465.5, "strength": 507.5}
const HINT := Rect2(40, 538, 310, 40)
const DESC := Rect2(53, 592, 284, 60)

var _layer: Layer
var _view: HeroView3D
var _lock_tex: Texture2D
var _bg_name := "violett"


func _init(m: MainMenu) -> void:
	super("helden_meldung", m, {"energy": "25/30", "gold": "4.674", "gems": "350"})


func _ready() -> void:
	super()
	_fill.visible = false
	# weichgezeichnete, abgedunkelte Heldenseite dahinter
	var back := ColorRect.new()
	back.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	back.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var mat := ShaderMaterial.new()
	mat.shader = load("res://shaders/hintergrund_weich.gdshader")
	mat.set_shader_parameter("radius", 4.0 * s * 1.5)
	back.material = mat
	add_child(back)
	move_child(back, 0)
	var sammlung: Script = load("res://scripts/ui/screens/tab_sammlung.gd")
	_bg_name = str(sammlung.BG.get(hero, "violett"))
	var l: Dictionary = _live_info.get("schloss", {})
	_lock_tex = load("res://ui_mock/helden_meldung/" + str(l["img"])) if str(l.get("img", "")) != "" else null
	_layer = Layer.new()
	_layer.board = self
	place_at(_layer, Rect2(0, 0, W, H))
	# Figur im Bildfeld (wie auf der Heldenseite, hier in Farbe und ganz)
	var r := live_rect("bild").grow(-2.0)
	_view = HeroView3D.make(hero, true, false)
	_view.fig = 0.9
	_view.feet = 0.98
	place_at(_view, r)
	live_image("schloss", true)
	bind()
	await get_tree().process_frame
	if is_instance_valid(_layer):
		_layer.queue_redraw()


func _data() -> Dictionary:
	return GameData.HEROES.get(hero, {})


func bind() -> void:
	var d := _data()
	if d.is_empty():
		return
	set_text("Fritzi", str(d["name"]))
	for t in ["Feuerwehrfrau", "Brandflinte", "Feuerkegel · setzt in Brand", "🔒 Kommt mit Level 5 · du bist auf Level 4",
			"Heizt der ersten Reihe richtig ein. Gewinne Level 5, dann ist Fritzi dabei – oder schalte Fritzi gleich frei."]:
		hide_text(t)
	for b in buttons():
		if str(b.info.get("href", "")) == "Artboard-seqx.dc.html" and str(b.info.get("label", "")) == "":
			b.modulate.a = 1.0 if Save.gems() >= MetaData.HERO_UNLOCK_GEMS else 0.6
	set_text("150", str(MetaData.HERO_UNLOCK_GEMS))
	if is_instance_valid(_layer):
		_layer.queue_redraw()


func handle(b: Dictionary) -> bool:
	var href := str(b.get("href", ""))
	var label := str(b.get("label", ""))
	if href == "Artboard-seqx.dc.html":
		if label == "Schließen":
			menu.close_board(self)
		else:
			_unlock()
		return true
	if TAB_OF.has(href):
		menu.close_board(self)
		menu.show_tab(TAB_OF[href])
		return true
	return false


func _unlock() -> void:
	var d := _data()
	var name := str(d.get("name", hero))
	if Save.gems() < MetaData.HERO_UNLOCK_GEMS:
		menu.toast("Dafür fehlen noch %d Edelsteine" % (MetaData.HERO_UNLOCK_GEMS - Save.gems()))
		return
	if Save.unlock_with_gems(hero):
		menu.close_board(self)
		menu.reward_success([{"type": "hero", "hero": hero, "amount": 1, "label": "%s ist jetzt im Team!" % name}], "Neuer Held")


## Was sich je Held ändert: Bildfeld, Werte, Bedingung, Beschreibung
class Layer:
	extends Control
	var board: HeroLockBoard

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE

	func _draw() -> void:
		var b := board
		var s := b.s
		var d := b._data()
		if d.is_empty():
			return
		# Bildfeld: Hintergrund in der Farbe des Helden, heller Rand
		var box := b.live_rect("bild")
		var bg: Texture2D = load("res://ui/helden_v2/portrait_hintergrund_%s.webp" % b._bg_name)
		if bg:
			draw_texture_rect(bg, Rect2(box.position * s, box.size * s), false)
		var sb := StyleBoxFlat.new()
		sb.draw_center = false
		sb.border_color = Color(1, 1, 1, 0.35)
		sb.set_border_width_all(maxi(1, roundi(2 * s)))
		sb.set_corner_radius_all(roundi(18 * s))
		draw_style_box(sb, Rect2(box.position * s, box.size * s))
		# Rolle, Waffe, Stärke rechtsbündig
		var light: Color = (d.get("color", Color(1.0, 0.69, 0.44)) as Color).lerp(Color.WHITE, 0.35)
		_value(str(d["role"]), ROW_Y["role"], "Fredoka", 700, 15.0, Color("#fff7ea"))
		_value(str(d["weapon"]), ROW_Y["weapon"], "Fredoka", 700, 15.0, Color("#fff7ea"))
		_value(str(STRENGTH.get(str(d.get("family", "")), "")), ROW_Y["strength"], "Fredoka", 700, 12.0, light)
		# Bedingung mit Schloss
		var need := int(MetaData.HERO_UNLOCK.get(b.hero, 0))
		var hint := "Kommt mit Level %d · du bist auf Level %d" % [need, Save.max_level()]
		var fs := 12.0
		var tw := b.text_width(hint, "Nunito", 800, fs)
		var icon := 16.0
		var x0 := HINT.get_center().x - (icon + 6.0 + tw) * 0.5
		var cy := HINT.get_center().y
		if b._lock_tex:
			draw_texture_rect(b._lock_tex, Rect2(Vector2(x0, cy - icon * 0.5) * s, Vector2(icon, icon) * s), false)
		b.label(self, hint, Vector2(x0 + icon + 6.0, cy), "Nunito", 800, fs, Color("#ffe27a"), -1)
		# Beschreibung, umbrochen und mittig
		var text := "%s Gewinne Level %d, dann ist %s dabei – oder schalte %s gleich frei." % [d["blurb"], need, d["name"], d["name"]]
		# höchstens zwei Zeilen (sonst reicht der Text an den Knopf): bei langen Namen etwas kleiner
		var size_pt := 12.0
		var lines := b.wrap(text, "Nunito", 700, size_pt, DESC.size.x)
		while lines.size() > 2 and size_pt > 10.5:
			size_pt -= 0.5
			lines = b.wrap(text, "Nunito", 700, size_pt, DESC.size.x + 12.0)
		var lh := size_pt * 1.4 if lines.size() <= 2 else 14.0
		for k in lines.size():
			b.label(self, lines[k], Vector2(DESC.get_center().x, DESC.position.y + lh * 0.5 + lh * k), "Nunito", 700, size_pt, Color("#cfc8f0"), 0)

	func _value(txt: String, y: float, family: String, weight: int, size_pt: float, col: Color) -> void:
		var b := board
		var fs := size_pt
		while fs > 9.0 and b.text_width(txt, family, weight, fs) > 190.0:
			fs -= 0.5
		b.label(self, txt, Vector2(VALUE_RIGHT, y), family, weight, fs, col, 1)


# --- Text-Hilfen (Mockup-Punkte) -----------------------------------------------------------

func text_width(txt: String, family: String, weight: int, size_pt: float) -> float:
	var fs := maxi(1, roundi(size_pt * s))
	return MockFonts.font(family, weight).get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x / s


## Text mit Ankerpunkt p (Mockup-Punkte): align −1 links, 0 Mitte, 1 rechts; y = Mitte der Zeile
func label(ci: CanvasItem, txt: String, p: Vector2, family: String, weight: int, size_pt: float, col: Color, align := 0) -> void:
	var fs := maxi(1, roundi(size_pt * s))
	var font := MockFonts.font(family, weight)
	var tw := font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var x := p.x * s - (tw * 0.5 if align == 0 else (tw if align > 0 else 0.0))
	var base := p.y * s + (font.get_ascent(fs) - font.get_descent(fs)) * 0.5
	ci.draw_string(font, Vector2(x, base), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)


func wrap(txt: String, family: String, weight: int, size_pt: float, width: float) -> PackedStringArray:
	var out := PackedStringArray()
	var line := ""
	for w in txt.split(" ", false):
		var test := w if line == "" else line + " " + w
		if line != "" and text_width(test, family, weight, size_pt) > width:
			out.append(line)
			line = w
		else:
			line = test
	if line != "":
		out.append(line)
	return out
