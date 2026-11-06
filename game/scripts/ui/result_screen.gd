class_name ResultScreen
extends MockView
## Belohnung nach dem Kampf (Mockups „Belohnung nach dem Sieg“ / „… nach der Niederlage“).
## Banner, Sterne, Felder, Tafel und Knöpfe kommen als Bilder aus dem Mockup (ui_mock/belohnung_*),
## Werte als Texte; die Heldenkarten (Anzahl und Fortschritt ändern sich) und die Wellen-Leiste
## zeichnet das Spiel selbst. Alle Maße in Mockup-Punkten (390 × 844).

signal next_pressed
signal retry_pressed
signal menu_pressed
signal heroes_pressed
## „Belohnung verdoppeln“ angetippt (main.gd vergibt und ruft apply_double auf)
signal double_pressed

const DOUBLE_HREF := "Belohnung-Sieg-Verdoppelt.dc.html"

## Farbverlauf des Bilderrahmens je Held (wie in der Helden-Übersicht)
const FRAME := {
	"lynx": ["#7a4bff", "#3a1f9a"], "dusty": ["#ffd34d", "#e8960f"], "iska": ["#6fb4ff", "#3a64d8"],
	"margot": ["#ff9fc3", "#c2508f"], "brocken": ["#ff8a7a", "#c0303a"], "kalle": ["#8fe8ff", "#2a9ad8"],
	"fritzi": ["#ffb070", "#e0602a"], "volta": ["#6fe8d0", "#1f8f9a"],
}

var won := true
## Werte für die Anzeige: level, world, kills, secs, shield (0..1), wave, waves, gold, stars,
## pass, cards (Array von {hero, amount}), last_level (bool), doubled (bool)
var info := {}
var _double_t := -1.0   # Zeit seit dem Verdoppeln (für das kurze Aufploppen des Hinweises)
var _heroes: Array = []        # [{hero, amount, rect}]
var _layer: Layer
var _figs: Control
var _rays: TextureRect
var _tex_arrow: Texture2D
var _tex_card: Texture2D
var _front: FrontLayer


func _init(won_: bool, info_: Dictionary) -> void:
	won = won_
	info = info_
	super("belohnung_sieg" if won else "belohnung_niederlage")


func _ready() -> void:
	super()
	_fill.visible = false
	var dim := ColorRect.new()
	dim.color = Color(10 / 255.0, 6 / 255.0, 30 / 255.0, 0.74) if won else Color(14 / 255.0, 6 / 255.0, 22 / 255.0, 0.8)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(dim)
	move_child(dim, 0)
	if won:
		_rays = live_image("rays")
		if _rays:
			_rays.modulate = Color(1, 1, 1, 0.9)
			_live_layer.move_child(_rays, 0)
	_tex_arrow = load("res://ui_mock/belohnung_sieg/main_live_badge.webp")
	_tex_card = load("res://ui_mock/belohnung_sieg/main_live_badge_1.webp")
	_fill_texts()
	_layer = Layer.new()
	_layer.view = self
	_figs = Control.new()
	_figs.mouse_filter = Control.MOUSE_FILTER_IGNORE
	place_at(_layer, Rect2(0, 0, W, H))
	place_at(_figs, Rect2(0, 0, W, H))
	_front = FrontLayer.new()
	_front.view = self
	place_at(_front, Rect2(0, 0, W, H))
	_figs.resized.connect(_place_figs)
	_build_heroes()
	button_pressed.connect(_on_button)
	# Auftritt: alles wächst kurz auf
	pivot_offset = size * 0.5
	scale = Vector2(0.94, 0.94)
	modulate.a = 0.0
	var tw := create_tween().set_parallel(true).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_property(self, "scale", Vector2.ONE, 0.35)
	tw.tween_property(self, "modulate:a", 1.0, 0.2)
	await get_tree().process_frame
	_layer.queue_redraw()


func _process(delta: float) -> void:
	if _double_t >= 0.0:
		_double_t += delta
	if _rays:
		_rays.rotation += delta * TAU / 40.0


func _fill_texts() -> void:
	var lv := int(info.get("level", 1))
	set_text("Level 4 · Schleim-Welt", "Level %d · %s" % [lv, str(info.get("world", ""))])
	var cost := str(MetaData.ENERGY_COST)
	if won:
		if bool(info.get("boss", false)):
			set_text("GESCHAFFT!", "BOSS BESIEGT!")
		set_text("123 besiegt", "%d besiegt" % int(info.get("kills", 0)))
		var secs := int(info.get("secs", 0))
		set_text("1:41", "%d:%02d" % [secs / 60, secs % 60])
		set_text("86 % Schild", "%d %% Schild" % roundi(float(info.get("shield", 1.0)) * 100.0))
		set_text("×1.366", "×" + MockScreen.num(int(info.get("gold", 0))))
		set_text("×3", "×%d" % int(info.get("stars", 1)))
		set_text("×20", "×%d" % int(info.get("pass", 0)))
		if bool(info.get("last_level", false)):
			set_text("WEITER · LEVEL 5", "NOCHMAL")
		else:
			set_text("WEITER · LEVEL 5", "WEITER · LEVEL %d" % (lv + 1))
		for t in texts_of_button(1) + texts_of_button(2):
			if str(t["text"]) == "5":
				set_text(int(t["i"]), cost)
		_bind_double()
	else:
		var wave := int(info.get("wave", 1))
		var waves := int(info.get("waves", 1))
		set_text("Welle 6 von 9 erreicht", "Welle %d von %d erreicht" % [wave, waves])
		var r := float(wave) / maxf(1.0, float(waves))
		set_text("Fast geschafft!", "Fast geschafft!" if r >= 0.6 else ("Gut gekämpft!" if r >= 0.3 else "Kopf hoch!"))
		set_text("×540", "×" + MockScreen.num(int(info.get("gold", 0))))
		set_text("Dusty Jo kann aufsteigen (+12 % Schaden). Und nach jeder Welle lieber mal eine Plasma-Karte nehmen.", _tip())
		for t in texts_of_button(0):
			if str(t["text"]) == "5":
				set_text(int(t["i"]), cost)


## Knopf „Belohnung verdoppeln“: 5× am Tag, mit Prime ohne Video; aufgebraucht oder verdoppelt: weg
func _bind_double() -> void:
	var b := button(DOUBLE_HREF)
	if b == null:
		return
	var left := Save.videos_left()
	b.visible = won and not bool(info.get("doubled", false)) and left > 0
	set_text("Kurzes Video · noch 5× heute", "%s · noch %d× heute" % ["Kein Video nötig" if Save.has_prime() else "Kurzes Video", left])


## Nach dem Verdoppeln: neue Werte zeigen, Knopf wird zum grünen Hinweis
func apply_double(rewards: Dictionary) -> void:
	info["gold"] = rewards["gold"]
	info["cards"] = rewards["cards"]
	info["doubled"] = true
	set_text("×1.366", "×" + MockScreen.num(int(info["gold"])))
	for e in _heroes:
		for c in rewards["cards"]:
			if str(c["hero"]) == e["hero"]:
				e["amount"] = int(c["amount"])
	hide_text("HELDENKARTEN")
	_bind_double()
	_double_t = 0.0
	Sfx.play("levelup")


## Tipp nach der Niederlage: zuerst ein Held, der aufsteigen kann, sonst Plasma
func _tip() -> String:
	for c in info.get("cards", []):
		var id := str(c["hero"])
		if Save.can_level_hero(id):
			return " %s kann aufsteigen\n(mehr Schaden). Und nach jeder Welle\nlieber mal eine Plasma-Karte nehmen." % String(GameData.HEROES[id]["name"])
	return " Mehr Plasma hilft:\nnach jeder Welle eine Plasma-Karte\nnehmen oder bei Upgrades aufrüsten."


func _build_heroes() -> void:
	var slots: Array[Rect2] = []
	for id in ["hero", "hero_1", "hero_2"]:
		if _live.has(id):
			slots.append(_live[id])
	var cards: Array = info.get("cards", [])
	var n := mini(cards.size(), slots.size())
	if n == 0:
		return
	# Beim Sieg stehen weniger als drei Helden mittig, bei der Niederlage bleiben sie neben dem Gold
	var dx := slots[1].position.x - slots[0].position.x if slots.size() > 1 else 0.0
	for k in n:
		var c: Dictionary = cards[k]
		var r: Rect2 = slots[k]
		if won and n < slots.size():
			r.position.x = slots[1].position.x + (k - (n - 1) * 0.5) * dx
		var e := {"hero": str(c["hero"]), "amount": int(c["amount"]), "rect": r}
		var v := HeroView3D.make(e["hero"], true)
		v.head_crop = true   # Kopf mittig in der Karte, Hut am Rand abgeschnitten (Mockup)
		var inner := _frame(r).grow(-3.0)
		v.aspect = inner.size.x / inner.size.y
		v.fig = 1.0
		v.feet = 1.18
		_figs.add_child(v)
		e["view"] = v
		_heroes.append(e)
	_place_figs()


func _place_figs() -> void:
	for e in _heroes:
		var v: HeroView3D = e["view"]
		var inner := _frame(e["rect"]).grow(-3.0)
		v.position = inner.position * s
		v.size = inner.size * s


## Bilderrahmen einer Heldenkarte (Spalte aus dem Mockup: Rahmen, Leiste, Name)
func _frame(col: Rect2) -> Rect2:
	var fw := col.size.x - 6.0
	var fh := 100.0 if won else 80.0
	return Rect2(col.position.x + (col.size.x - fw) * 0.5, col.position.y, fw, fh)


func _px(r: Rect2) -> Rect2:
	return Rect2(r.position * s, r.size * s)


func _draw_heroes(ci: CanvasItem, front: bool) -> void:
	for e in _heroes:
		var id: String = e["hero"]
		var col: Rect2 = e["rect"]
		var fr := _frame(col)
		var lvl := Save.hero_level(id)
		var have := Save.hero_cards(id)
		var need := MetaData.hero_cards_needed(lvl)
		var maxed := lvl >= MetaData.HERO_MAX_LEVEL
		var ready := not maxed and Save.can_level_hero(id)
		if not front:
			var cols: Array = FRAME.get(id, ["#4a63e6", "#23267a"])
			MockPaint.rrect(ci, _px(fr), 12 * s, Color(cols[0]), Color(cols[1]))
			continue
		# unten im Bild: dunkler Verlauf mit „+N“
		var strip := Rect2(fr.position.x + 3, fr.end.y - 29, fr.size.x - 6, 26)
		MockPaint.rrect(ci, _px(strip), 8 * s, Color(20 / 255.0, 10 / 255.0, 60 / 255.0, 0.0), Color(20 / 255.0, 10 / 255.0, 60 / 255.0, 0.85))
		MockPaint.text(self, ci, "+%d" % int(e["amount"]), strip, "Fredoka", 700, 17, "rgb(255, 247, 234)", "rgb(26, 10, 64) 0px 2px 0px")
		MockPaint.border(ci, _px(fr), 12 * s, Color("#7dff8a") if ready else Color("#ffd34d"), 3 * s)
		# Leiste: Symbol, Balken, Zahlen
		var y := fr.end.y + 5.0
		var row_w := col.size.x - 2.0 if won else col.size.x
		var x0 := col.position.x + (col.size.x - row_w) * 0.5
		var icon := _tex_arrow if ready or maxed else _tex_card
		if icon:
			ci.draw_texture_rect(icon, _px(Rect2(x0 + 1, y - 1 + (sin(Time.get_ticks_msec() * 0.005) * 1.5 if ready else 0.0), 18, 18)), false)
		var bar := Rect2(x0 + 21, y + 2, row_w - 21, 12)
		MockPaint.rrect(ci, _px(bar), 6 * s, Color(10 / 255.0, 6 / 255.0, 30 / 255.0, 0.75))
		var ratio := 1.0 if maxed else clampf(float(have) / float(maxi(1, need)), 0.0, 1.0)
		if ratio * bar.size.x > 1.0:
			var a := Color("#7dff8a") if ready or maxed else Color("#6fe0ff")
			var b := Color("#3fbf3a") if ready or maxed else Color("#3a8cff")
			MockPaint.rrect_h(ci, _px(Rect2(bar.position, Vector2(bar.size.x * ratio, bar.size.y))), 6 * s, a, b)
		MockPaint.border(ci, _px(bar), 6 * s, Color(1, 1, 1, 0.18), 1 * s)
		MockPaint.text(self, ci, "MAX" if maxed else "%d/%d" % [have, need], bar, "Nunito", 800, 8.5, "rgb(255, 255, 255)")
		var label := "Aufwertbar!" if ready else String(GameData.HEROES[id]["name"])
		var lr := Rect2(col.position.x - 6, y + 21, col.size.x + 12, 14)
		var size := 10.0
		while size > 7.0 and MockPaint.text_width(label, "Nunito", 800, size) > lr.size.x:
			size -= 0.5
		MockPaint.text(self, ci, label, lr, "Nunito", 800, size, "rgb(125, 255, 138)" if ready else "rgb(207, 200, 240)")


## Zustand nach dem Video (Mockup „Sieg nach dem Video“): grüner Hinweis, ×2 an Gold und Heldenkarten
func _draw_doubled(ci: CanvasItem) -> void:
	if not bool(info.get("doubled", false)):
		return
	var k := clampf(_double_t / 0.25, 0.0, 1.0) if _double_t >= 0.0 else 1.0
	var r := Rect2(40, 602, 310, 52)
	var g := r.grow(-(1.0 - k) * 10.0)
	MockPaint.rrect(ci, _px(g), 16 * s, Color(20 / 255.0, 70 / 255.0, 30 / 255.0, 0.55 * k))
	MockPaint.border(ci, _px(g), 16 * s, Color(125 / 255.0, 1.0, 138 / 255.0, k), 2 * s)
	if k < 1.0:
		return
	var l1 := "VERDOPPELT!"
	var l2 := "Gold und Heldenkarten ×2 · noch %d× heute" % Save.videos_left()
	var w1 := MockPaint.text_width(l1, "Fredoka", 700, 19)
	var w2 := MockPaint.text_width(l2, "Nunito", 800, 11)
	var x0 := r.get_center().x - (36.0 + maxf(w1, w2)) * 0.5
	var c := Vector2(x0 + 13, r.get_center().y)
	ci.draw_circle(c * s, 12 * s, Color("#3fbf3a"))
	ci.draw_arc(c * s, 12 * s, 0, TAU, 32, Color("#d8ffd0"), 2 * s, true)
	var tick := PackedVector2Array([(c + Vector2(-5.5, 0.5)) * s, (c + Vector2(-1.5, 4.5)) * s, (c + Vector2(5.5, -3.5)) * s])
	ci.draw_polyline(tick, Color.WHITE, 3 * s, true)
	MockPaint.text(self, ci, l1, Rect2(x0 + 36, 611.5, w1, 21), "Fredoka", 700, 19, "rgb(182, 255, 138)")
	MockPaint.text(self, ci, l2, Rect2(x0 + 36, 632.5, w2, 12), "Nunito", 800, 11, "rgb(216, 255, 208)")
	# „×2“-Marke oben rechts an der Gold-Kachel
	var bw := MockPaint.text_width("×2", "Fredoka", 700, 11) + 13.0
	var badge := Rect2(128.0 - bw, 318.5, bw, 18)
	MockPaint.rrect(ci, _px(badge), 8 * s, Color("#7dff8a"))
	MockPaint.border(ci, _px(badge), 8 * s, Color("#145a2e"), 1.5 * s)
	MockPaint.text(self, ci, "×2", badge, "Fredoka", 700, 11, "rgb(15, 61, 18)")
	# Überschrift „HELDENKARTEN ×2“ (×2 in Grün)
	var wa := MockPaint.text_width("HELDENKARTEN ", "Nunito", 800, 11, 0.88)
	var wb := MockPaint.text_width("×2", "Nunito", 800, 11, 0.88)
	var hx := r.get_center().x - (wa + wb) * 0.5
	MockPaint.text(self, ci, "HELDENKARTEN ", Rect2(hx, 424, wa, 15), "Nunito", 800, 11, "rgb(207, 200, 240)", "", 0.88)
	MockPaint.text(self, ci, "×2", Rect2(hx + wa, 424, wb, 15), "Nunito", 800, 11, "rgb(125, 255, 138)", "", 0.88)


## Wellen-Leiste der Niederlage: erreichte Wellen orange, der Rest dunkel
func _draw_waves(ci: CanvasItem) -> void:
	if won or not _live.has("waves"):
		return
	var r: Rect2 = _live["waves"]
	r = Rect2(r.position.x, r.position.y + 2, r.size.x, 18)
	MockPaint.rrect(ci, _px(r), 8 * s, Color(10 / 255.0, 6 / 255.0, 30 / 255.0, 0.7))
	MockPaint.border(ci, _px(r), 8 * s, Color(1, 1, 1, 0.18), 1 * s)
	var n := maxi(1, int(info.get("waves", 1)))
	var done := clampi(int(info.get("wave", 1)), 0, n)
	var inner := r.grow(-3.0)
	var gap := 3.0
	var w := (inner.size.x - gap * (n - 1)) / n
	for i in n:
		var seg := Rect2(inner.position.x + i * (w + gap), inner.position.y, w, inner.size.y)
		if i < done:
			MockPaint.rrect(ci, _px(seg), 4 * s, Color("#ffb23a"), Color("#e8700f"))
		else:
			MockPaint.rrect(ci, _px(seg), 4 * s, Color(1, 1, 1, 0.12))


func _on_button(b: Dictionary) -> void:
	var href := str(b.get("href", ""))
	if href == DOUBLE_HREF:
		double_pressed.emit()
	elif href.begins_with("Main"):
		menu_pressed.emit()
	elif href.begins_with("Artboard-seqx"):
		heroes_pressed.emit()
	elif won and int(b.get("i", -1)) == 1 and not bool(info.get("last_level", false)):
		next_pressed.emit()
	else:
		retry_pressed.emit()


class Layer:
	extends Control
	var view: ResultScreen

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE

	func _process(_delta: float) -> void:
		queue_redraw()

	func _draw() -> void:
		view._draw_waves(self)
		view._draw_heroes(self, false)
		# Figuren liegen über dem Rahmen; Schrift und Leisten zeichnet die vordere Ebene
		if view._front:
			view._front.queue_redraw()


class FrontLayer:
	extends Control
	var view: ResultScreen

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE

	func _draw() -> void:
		view._draw_heroes(self, true)
		view._draw_doubled(self)
