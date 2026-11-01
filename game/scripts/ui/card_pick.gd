class_name CardPick
extends MockView
## Kartenwahl nach jeder Welle (Mockup „Karte nach der Welle“): „Welle N geschafft! Wähle eine
## Karte“, drei Karten mit Rahmen aus dem Mockup (gold = Plasma, cyan = Held mit Porträt-Chip,
## lila = Schild und Sonstiges), Antippen wählt aus, NEHMEN übernimmt.

signal picked(card: Dictionary)

## Rahmen aus dem Mockup: 0 = gold (Magazin), 1 = cyan mit Helden-Chip (Nachladen), 2 = lila (Kern)
const FRAME_LABELS := ["Karte MAGAZIN: +2 Schuss für alle Helden", "Karte NACHLADEN für Dusty Jo: −20 % schneller nachladen", "Karte KERN: +30 % lädt schneller auf"]
const ACCENT := [Color("ffd34d"), Color("6fe0ff"), Color("c08aff")]
const HERO_MODS := {
	"damage": ["SCHADEN", "+20 %", "mehr Schaden"],
	"rate": ["FEUERRATE", "+15 %", "schneller feuern"],
	"reload": ["NACHLADEN", "−20 %", "schneller nachladen"],
	"mag": ["MAGAZIN", "+50 %", "größeres Magazin"],
	"crit": ["KRITISCH", "+10 %", "doppelter Schaden"],
}

var cards: Array = []
var wave := 1
var hero_levels := {}   # Held -> Kartenstufe (für „Lv. 6 → Lv. 7“)
var _sel := 0
var _layer: CardLayer
var _portraits: Array[Control] = []


func _init(cards_: Array, wave_: int) -> void:
	super("karten")
	cards = cards_
	wave = wave_


func _ready() -> void:
	super()
	_fill.visible = false
	var dim := ColorRect.new()
	dim.color = Color(0.03, 0.02, 0.1, 0.55)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(dim)
	move_child(dim, 0)
	set_text("WELLE 3 GESCHAFFT!", "WELLE %d GESCHAFFT!" % wave)
	set_text("Ersetzt die Tore der Kugelmaschine: Die Karten gelten bis zum Ende des Levels.", "Die Karten gelten bis zum Ende des Levels.")
	# Kartenknöpfe aus dem Mockup nur als Rahmen-Vorlage, gezeichnet wird in der eigenen Ebene
	for b in buttons():
		if str(b.info.get("label", "")).begins_with("Karte"):
			b.visible = false
	for t in data.get("texts", []):
		if int(t["button"]) in [0, 1, 2]:
			hide_text(int(t["i"]))
	_layer = CardLayer.new()
	_layer.pick = self
	place_at(_layer, Rect2(0, 0, W, H))
	button_pressed.connect(func(b: Dictionary) -> void:
		if str(b.get("label", "")) == "" and _sel < cards.size():
			picked.emit(cards[_sel]))
	_sel = 1 if cards.size() >= 3 else 0
	_place_portraits()


func select(i: int) -> void:
	_sel = i
	_place_portraits()
	_layer.queue_redraw()


func slot_rect(i: int) -> Rect2:
	var n := cards.size()
	var w := 106.0 if n <= 3 else 84.0
	var gap := (W - 22.0 * 2.0 - w * n) / maxf(1.0, n - 1)
	var r := Rect2(22.0 + i * (w + gap), 300.0, w, 168.0)
	if i == _sel:
		r = r.grow_individual(3, 18, 3, 9)
	return r


## Was auf der Karte steht: Rahmen, Überschrift, großer Wert, kleiner Text, Held
func face(c: Dictionary) -> Dictionary:
	var kind: String = c.get("kind", "")
	var key: String = c.get("key", "")
	if kind == "hero":
		var mod := key.get_slice(":", 1)
		var hid := key.get_slice(":", 0)
		var m: Array = HERO_MODS.get(mod, [String(c["title"]).to_upper(), "+1", String(c["desc"]).split("\n")[0]])
		if mod == "ult":
			m = ["SUPER", "★", String(c["title"])]
		elif mod == "special":
			m = [String(c["title"]).to_upper(), "+1", "Spezialfähigkeit"]
		return {"frame": 1, "label": m[0], "value": m[1], "sub": m[2], "hero": hid,
			"lv": int(c.get("stars", 0))}
	if kind == "add_hero":
		return {"frame": 1, "label": "NEU IM TEAM", "value": "+1", "sub": String(GameData.HEROES[c["hero_id"]]["weapon"]),
			"hero": c["hero_id"], "lv": -1}
	if kind == "station":
		return {"frame": 2, "label": "SCHILD", "value": "+35 %", "sub": "Schild flicken", "hero": ""}
	var target := String(c.get("target", "")).to_upper()
	if key in ["plasma:mag", "plasma:reload", "plasma:core"]:
		return {"frame": {"plasma:mag": 0, "plasma:reload": 2, "plasma:core": 2}[key], "label": target, "value": String(c["title"]).split(" ")[0],
			"sub": String(c["desc"]).trim_suffix("."), "hero": "", "icon": c.get("emblem", "")}
	return {"frame": 0, "label": target, "value": String(c.get("emblem", "")), "sub": String(c["title"]), "hero": ""}


func _place_portraits() -> void:
	for p in _portraits:
		p.queue_free()
	_portraits.clear()
	for i in cards.size():
		var f := face(cards[i])
		if str(f["hero"]) == "":
			continue
		var r := slot_rect(i)
		var por := HeroPortrait.make(str(f["hero"]), 64)
		por.spin = false
		place_at(por, Rect2(r.get_center().x - 22.0, r.position.y - 33.0, 44.0, 44.0), true)
		_portraits.append(por)


class CardLayer:
	extends Control
	var pick: CardPick
	var _tex: Array[Texture2D] = []
	var _img_rects: Array[Rect2] = []
	var _btn_rects: Array[Rect2] = []

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_STOP
		for lab in CardPick.FRAME_LABELS:
			var b := pick.button(lab)
			_tex.append(b.texture if b else null)
			var ir: Array = b.info.get("img_rect", [0, 0, 1, 1]) if b else [0, 0, 1, 1]
			var br: Array = b.info.get("rect", [0, 0, 1, 1]) if b else [0, 0, 1, 1]
			_img_rects.append(Rect2(ir[0], ir[1], ir[2], ir[3]))
			_btn_rects.append(Rect2(br[0], br[1], br[2], br[3]))
		await get_tree().process_frame
		queue_redraw()

	func _draw() -> void:
		var s := pick.s
		for i in pick.cards.size():
			var c: Dictionary = pick.cards[i]
			var f := pick.face(c)
			var fr: int = f["frame"]
			var slot := pick.slot_rect(i)
			# Rahmenbild so strecken, dass der Kartenkörper genau im Platz liegt
			var br := _btn_rects[fr]
			var ir := _img_rects[fr]
			var k := slot.size / br.size
			var img := Rect2(slot.position + (ir.position - br.position) * k, ir.size * k)
			if _tex[fr]:
				draw_texture_rect(_tex[fr], Rect2(img.position * s, img.size * s), false, Color.WHITE if i == pick._sel else Color(0.85, 0.85, 0.9))
			var cx := slot.get_center().x * s
			var font := MockFonts.font("Fredoka", 700)
			var small := MockFonts.font("Nunito", 700)
			# Höhen wie im Mockup; der cyane Rahmen hat oben noch das Stufen-Schild
			var hero_frame := fr == 1
			var y_label := 46.0 if hero_frame else 26.0
			var y_icon := 78.0 if hero_frame else 60.0
			var y_value := 130.0 if hero_frame else 116.0
			var y_sub := 140.0 if hero_frame else 132.0
			var kk := slot.size.y / (195.0 if hero_frame and i == pick._sel else 168.0)
			y_label *= kk
			y_icon *= kk
			y_value *= kk
			y_sub *= kk
			_center(font, f["label"], Vector2(cx, (slot.position.y + y_label) * s), roundi(11 * s), CardPick.ACCENT[fr])
			# Symbol: leuchtender Kreis mit Zeichen
			var ic := Vector2(cx, (slot.position.y + y_icon) * s)
			draw_circle(ic, 22.0 * s, Color(CardPick.ACCENT[fr], 0.18))
			draw_circle(ic, 17.0 * s, Color(CardPick.ACCENT[fr], 0.35))
			var emb := str(f.get("icon", f["value"] if str(f["value"]).length() <= 3 else "★"))
			_center(font, emb, ic + Vector2(0, 7.0 * s), roundi(18 * s), Color.WHITE)
			_center(font, str(f["value"]), Vector2(cx, (slot.position.y + y_value) * s), roundi((24 if str(f["value"]).length() <= 6 else 16) * s), Color("fff7ea"))
			_wrap(small, str(f["sub"]), Vector2(cx, (slot.position.y + y_sub) * s), (slot.size.x - 12.0) * s, roundi(11 * s), Color("cfc8f0"))
			if str(f["hero"]) != "":
				var name := String(GameData.HEROES[f["hero"]]["name"]).to_upper()
				_center(font, name, Vector2(cx, (slot.position.y - 3.0) * s), roundi(9 * s), Color("4a2000"))
				var lv: int = f.get("lv", -1)
				if lv >= 0:
					_center(font, "Lv. %d → Lv. %d" % [lv, lv + 1], Vector2(cx, (slot.position.y + 28.0 * kk) * s), roundi(10 * s), Color("ffd34d"))

	func _center(font: Font, txt: String, at: Vector2, fs: int, col: Color) -> void:
		var w := font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		draw_string(font, at + Vector2(-w * 0.5, 0), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)

	func _wrap(font: Font, txt: String, top: Vector2, width: float, fs: int, col: Color) -> void:
		var words := txt.split(" ")
		var line := ""
		var y := top.y + fs
		for w in words:
			var test := w if line == "" else line + " " + w
			if font.get_string_size(test, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > width and line != "":
				_center(font, line, Vector2(top.x, y), fs, col)
				y += fs * 1.2
				line = w
			else:
				line = test
		if line != "":
			_center(font, line, Vector2(top.x, y), fs, col)

	func _gui_input(e: InputEvent) -> void:
		if e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT:
			var p := get_local_mouse_position() / pick.s
			for i in pick.cards.size():
				if pick.slot_rect(i).has_point(p):
					if i == pick._sel:
						pick.picked.emit(pick.cards[i])
					else:
						pick.select(i)
					accept_event()
					return
