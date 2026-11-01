class_name HeroBoard
extends MockScreen
## Fenster „Held aufleveln“ (Mockups „Held aufleveln · <Held>“, ui_mock/held): der Held als echte
## 3D-Figur auf dem Podest, Name, Typ und Superfähigkeit, Stufe mit Kartenbalken, Werte
## Schaden/Nachladen/Magazin mit Vorschau auf die nächste Stufe und der Aufleveln-Knopf mit
## echtem Goldpreis (Save.level_hero). Pfeile blättern durch die freigeschalteten Helden, das X
## schließt. Die drei Fähigkeiten-Karten (Superfähigkeit und zwei Kampfkarten) öffnen das
## Fähigkeiten-Fenster. Fähigkeiten-Stufen (Sterne) kennt das Spiel noch nicht: Sterne und
## Preise stehen wie im Mockup, „Verbessern“ gibt einen Hinweis.
##
## Je Held gibt es einen Zustand im Export (Symbole auf den Karten, Talent); gemeinsame Bilder
## liegen nur einmal vor. Zahlen und Balken zeichnet das Spiel selbst.

## Mit welchem Helden das Fenster aufgeht und in welcher Reihenfolge die Pfeile blättern
## (setzt die Heldenübersicht vor dem Öffnen).
static var start_hero := "dusty"
static var hero_order: Array[String] = []

const NAV := {"Shop": "shop", "Helden": "sammlung", "Kampf": "kampf", "Upgrades": "upgrades", "Basis": "basis"}
const SKILLS := ["supe", "kett", "luft"]
## Sterne und Preise der Fähigkeiten wie im Mockup (das Spiel kennt noch keine Fähigkeiten-Stufen)
const SKILL_STARS := {"supe": 2, "kett": 2, "luft": 1}
const SKILL_COST := {"supe": "250", "kett": "400", "luft": "250"}
## Superfähigkeit: Text vor, hervorgehoben, nach; Hinweis auf den 3. Stern (aus dem Mockup)
const ULT_TEXT := {
	"dusty": ["Dreifach schnelles Feuer, jeder Schuss fächert auf ", "2", " weitere Gegner. Kein Nachladen.", "Mit dem 3. Stern fächert jeder Schuss auf 3 Gegner"],
	"iska": ["Feuert ", "3x", " so schnell mit hellen Kugeln, ganz ohne Nachladen.", "Mit dem 3. Stern hält das Dauerfeuer 2 Sekunden länger"],
	"brocken": ["Feuert sofort einen Schwarm aus ", "8", " Raketen auf die Gegner.", "Mit dem 3. Stern fliegen 12 Raketen"],
	"kalle": ["Friert alle Gegner ", "4 Sekunden", " fast ganz ein und macht Frostschaden.", "Mit dem 3. Stern hält das Eis 6 Sekunden"],
	"fritzi": ["Flammen erfassen alle Gegner in Reichweite und brennen ", "6 Sekunden", " lang.", "Mit dem 3. Stern brennen die Flammen doppelt so heiß"],
	"volta": ["Ein gewaltiger Blitz trifft ", "alle", " Gegner auf dem Feld gleichzeitig.", "Mit dem 3. Stern schlägt der Blitz zweimal ein"],
	"margot": ["Drei mächtige Schrotsalven treffen ", "alle", " Gegner vorne auf der Bahn.", "Mit dem 3. Stern feuert Margot vier Salven"],
	"lynx": ["Durchschlagende Volltreffer auf die ", "3", " stärksten Gegner.", "Mit dem 3. Stern trifft Lynx 5 Ziele"],
}
## Zwei Kampfkarten je Held: Name, Text vor, hervorgehoben, nach (aus dem Mockup)
const CARDS := {
	"dusty": [["Fächerschuss", "Jeder ", "4.", " Schuss teilt sich in drei Kugeln."], ["Schnellzieher", "In den ersten 5 Sekunden jeder Welle feuert Dusty ", "2x", " so schnell."]],
	"iska": [["Leuchtspur", "Jede ", "10.", " Kugel explodiert und trifft Gegner daneben."], ["Doppelmagazin", "Nach dem Nachladen sind die ersten 8 Schüsse ", "+30 %", " stärker."]],
	"brocken": [["Splitterregen", "Nach jedem Raketentreffer fliegen ", "3", " Splitter in die Menge."], ["Schwerer Treffer", "Raketen werfen große Gegner ", "1 Feld", " zurück."]],
	"kalle": [["Frostmantel", "Getroffene Gegner sind ", "30 %", " langsamer."], ["Eissplitter", "Gefrorene Gegner zerspringen und treffen ", "2", " Nachbarn."]],
	"fritzi": [["Brandspur", "Brennende Gegner hinterlassen ", "3 Sekunden", " lang eine Feuerspur."], ["Hitzewelle", "Alle ", "10 Sekunden", " rollt eine Flammenwelle über die ganze Bahn."]],
	"volta": [["Kettenblitz", "Jeder Blitz springt auf ", "3", " weitere Gegner."], ["Überspannung", "Gegen Bosse ", "+40 %", " Blitzschaden."]],
	"margot": [["Enterhaken", "Zieht den vordersten Gegner ", "2 Felder", " zurück."], ["Schrotregen", "Die Breitseite trifft zusätzlich ", "alle", " Gegner am Rand."]],
	"lynx": [["Durchschuss", "Jeder Schuss durchschlägt bis zu ", "2", " Gegner."], ["Zielfernrohr", "Gegen Bosse ", "+25 %", " kritische Treffer."]],
}
const TEXT_SHADOW := "rgb(29, 107, 42) 0px 2px 0px"
## Fähigkeiten-Fenster und Symbolfeld darüber (Mockup-Punkte)
const DIALOG := Rect2(26, 262, 338, 330)
const DIALOG_ICON := Rect2(135, 214, 120, 120)
## Bildausschnitt der 3D-Figur: quadratisch, Füße kurz über der Unterkante des Mockup-Bilds
const VIEW_SIZE := 300.0

var hero := ""
var _info: InfoLayer
var _view3d: HeroView3D
var _skill_view: MockView
var _skill := ""
var _level_view: MockView
var _tex := {}


func _init(m: MainMenu) -> void:
	super("held", m, {"stars": "2", "gold": "4.974", "gems": "65"})
	hero = start_hero if MockView.layout_of("held").get("states", {}).has(start_hero) else "dusty"
	state = hero


func _ready() -> void:
	super()
	var hr := live_rect("hero")
	var feet := hr.end.y   # Unterkante des Heldenbilds im Mockup (Größe/Lage je Held: HeroView3D.POSES)
	_view3d = HeroView3D.make(hero)
	place_at(_view3d, Rect2(W * 0.5 - VIEW_SIZE * 0.5, feet - _view3d.feet * VIEW_SIZE, VIEW_SIZE, VIEW_SIZE))
	_info = InfoLayer.new()
	_info.board = self
	place_at(_info, Rect2(0, 0, W, H))
	_set_hero(hero)
	await get_tree().process_frame
	_info.queue_redraw()
	for b in buttons():
		b.queue_redraw()


func _order() -> Array[String]:
	var out: Array[String] = []
	for id in hero_order:
		if Save.hero_unlocked(id):
			out.append(id)
	if out.is_empty():
		out = Save.unlocked_heroes()
	if not out.has(hero):
		out.append(hero)
	return out


func _set_hero(id: String) -> void:
	hero = id
	_overrides.clear()
	_hidden.clear()
	show_state(id)
	if _view3d and _view3d.hero_id != id:
		_view3d.set_hero(id)
	_decorate()
	refresh()


## Text im aktuellen Zustand über eine Bedingung finden (Nummer, -1 wenn keiner passt)
func _text_where(d: Dictionary, f: Callable) -> int:
	for t in d.get("texts", []):
		if f.call(t):
			return int(t["i"])
	return -1


func _btn(on: String) -> MockButton:
	for b in buttons():
		if str(b.info.get("on", "")) == on:
			return b
	return null


func bind() -> void:
	if _info == null:
		return
	var d: Dictionary = GameData.HEROES[hero]
	var lvl := Save.hero_level(hero)
	set_text(_text_where(data, func(t: Dictionary) -> bool: return float(t["size"]) == 26.0), String(d["name"]).to_upper())
	var typ := "Verstärkung" if GameData.HERO_TYPE.get(hero, "start") == "verstaerkung" else "Start-Held"
	set_text(_text_where(data, func(t: Dictionary) -> bool: return str(t["text"]).contains("Superfähigkeit")),
		"%s · Superfähigkeit „%s“" % [typ, _ult_name(hero)])
	set_text(_text_where(data, func(t: Dictionary) -> bool: return str(t["text"]).begins_with("STUFE ")), "STUFE %d" % lvl)
	# Silberne Sterne (Währung für Fähigkeiten) gibt es im Spiel noch nicht
	set_text(_text_where(data, func(t: Dictionary) -> bool: return int(t["i"]) == 0), "0")
	var up := _btn("levelUp")
	if up:
		for t in up.texts():
			hide_text(int(t["i"]))
		up.modulate = Color.WHITE if Save.can_level_hero(hero) or lvl >= MetaData.HERO_MAX_LEVEL else Color(0.82, 0.82, 0.88)
	var order := _order()
	for on in ["prev", "next"]:
		var b := _btn(on)
		if b:
			b.modulate.a = 1.0 if order.size() > 1 else 0.35
	_info.queue_redraw()
	for b in buttons():
		b.queue_redraw()
		for c in b.get_children():
			(c as CanvasItem).queue_redraw()


func _ult_name(id: String) -> String:
	var fam := String(GameData.HEROES[id].get("family", ""))
	return String(Hero.ULTS.get(fam, ["Superfähigkeit"])[0])


## Zeichnungen auf Knöpfen (wandern beim Antippen mit): Symbole der Fähigkeiten, Aufleveln
func _decorate() -> void:
	for b in buttons():
		var on := str(b.info.get("on", ""))
		if on.begins_with("pick_") or on == "levelUp":
			var deco := ButtonDeco.new()
			deco.board = self
			deco.btn = b
			b.add_child(deco)


func _tex_of(file: String) -> Texture2D:
	if file == "":
		return null
	if not _tex.has(file):
		_tex[file] = load("res://ui_mock/held/" + file)
	return _tex[file]


## Symbol einer Fähigkeit (aus dem Fähigkeiten-Fenster des Mockups): [Bild, Rahmen, Symbolfläche]
func _skill_icon(id: String, kind: String) -> Array:
	var ov: Dictionary = MockView.layout_of("held").get("overlays", {}).get("ic_%s_%s" % [id, kind], {})
	for l in ov.get("live", []):
		if str(l["id"]) == "sk_icon" and str(l.get("img", "")) != "":
			var ir: Array = l["img_rect"]
			var r: Array = l["rect"]
			return [_tex_of(str(l["img"])), Rect2(ir[0], ir[1], ir[2], ir[3]), Rect2(r[0], r[1], r[2], r[3])]
	return []


## Live-Bild des aktuellen Zustands: [Bild, Rahmen, Fläche]
func _live_img(id: String) -> Array:
	var l: Dictionary = _live_info.get(id, {})
	if str(l.get("img", "")) == "":
		return []
	var ir: Array = l["img_rect"]
	var r: Array = l["rect"]
	return [_tex_of(str(l["img"])), Rect2(ir[0], ir[1], ir[2], ir[3]), Rect2(r[0], r[1], r[2], r[3])]


## Bild so zeichnen, dass seine Fläche (src) auf target liegt (Mockup-Punkte, origin = Bildpunkt von (0,0))
func draw_img_at(ci: CanvasItem, img: Array, target: Rect2, origin: Vector2) -> void:
	if img.is_empty() or img[0] == null:
		return
	var src: Rect2 = img[2]
	var ir: Rect2 = img[1]
	var k := target.size.x / src.size.x
	var p := target.position + (ir.position - src.position) * k
	ci.draw_texture_rect(img[0], Rect2(origin + p * s, ir.size * k * s), false)


func _skill_kind(b: MockButton) -> String:
	return str(b.info.get("on", "")).trim_prefix("pick_")


func draw_deco(ci: CanvasItem, b: MockButton) -> void:
	var hit: Array = b.info["rect"]
	var origin := -Vector2(hit[0], hit[1]) * s
	var on := str(b.info.get("on", ""))
	if on.begins_with("pick_"):
		var br := Rect2(hit[0], hit[1], hit[2], hit[3])
		for l in data.get("live", []):
			if str(l["id"]).begins_with("card_icon"):
				var r: Array = l["rect"]
				var ir := Rect2(r[0], r[1], r[2], r[3])
				if br.encloses(ir):
					draw_img_at(ci, _skill_icon(hero, _skill_kind(b)), ir, origin)
	elif on == "levelUp":
		_draw_level_button(ci, b, origin)


func _draw_level_button(ci: CanvasItem, b: MockButton, origin: Vector2) -> void:
	var hit: Array = b.info["rect"]
	var cy := 717.0
	var lvl := Save.hero_level(hero)
	if lvl >= MetaData.HERO_MAX_LEVEL:
		var t := "HÖCHSTE STUFE"
		MockPaint.text(self, ci, t, Rect2(hit[0], cy, hit[2], 24), "Fredoka", 700, 20, "rgb(255, 255, 255)", TEXT_SHADOW, 0.0, origin)
		return
	var cost := MockScreen.num(MetaData.hero_gold_needed(lvl))
	var w1 := MockPaint.text_width("AUFLEVELN", "Fredoka", 700, 20)
	var w2 := MockPaint.text_width(cost, "Fredoka", 700, 20)
	var total := w1 + 12.0 + 24.0 + 4.0 + w2
	var x := float(hit[0]) + float(hit[2]) * 0.5 - total * 0.5
	MockPaint.text(self, ci, "AUFLEVELN", Rect2(x, cy, w1, 24), "Fredoka", 700, 20, "rgb(255, 255, 255)", TEXT_SHADOW, 0.0, origin)
	x += w1 + 12.0
	var coin := _coin()
	if not coin.is_empty():
		draw_img_at(ci, coin, Rect2(x, cy, 24, 24), origin)
	x += 28.0
	MockPaint.text(self, ci, cost, Rect2(x, cy, w2, 24), "Fredoka", 700, 20, "rgb(255, 246, 192)", TEXT_SHADOW, 0.0, origin)


func _coin() -> Array:
	var d: Dictionary = MockView.layout_of("held")["states"]["dusty"]
	for l in d.get("live", []):
		if str(l["id"]) == "coin":
			var ir: Array = l["img_rect"]
			var r: Array = l["rect"]
			return [_tex_of(str(l["img"])), Rect2(ir[0], ir[1], ir[2], ir[3]), Rect2(r[0], r[1], r[2], r[3])]
	return []


# --- Werte -----------------------------------------------------------------------------------

func _values() -> Dictionary:
	var d: Dictionary = GameData.HEROES[hero]
	var lvl := Save.hero_level(hero)
	var nxt := mini(lvl + 1, MetaData.HERO_MAX_LEVEL)
	var reload := String.num(float(d["reload"]), 2).replace(".", ",")
	if not reload.contains(","):
		reload += ",00"
	elif reload.length() - reload.find(",") == 2:
		reload += "0"
	return {
		"dmg": [str(int(round(float(d["damage"]) * MetaData.hero_damage_mult(lvl)))), str(int(round(float(d["damage"]) * MetaData.hero_damage_mult(nxt))))],
		"rel": [reload, reload],
		"mag": [str(int(d["mag"])), str(int(d["mag"]))],
	}


func draw_info(ci: CanvasItem) -> void:
	var lvl := Save.hero_level(hero)
	# Kartenbalken
	var bar := live_rect("cardbar")
	MockPaint.rrect(ci, Rect2(bar.position * s, bar.size * s), 12 * s, Color("#141038"))
	var have := Save.hero_cards(hero)
	var need := MetaData.hero_cards_needed(lvl)
	var ratio := 1.0 if lvl >= MetaData.HERO_MAX_LEVEL else clampf(float(have) / float(need), 0.0, 1.0)
	if ratio > 0.0:
		var fill := Rect2(bar.position * s, Vector2(bar.size.x * ratio, bar.size.y) * s)
		# Füllung im runden Balken: links rund, rechts gerade (wie overflow: hidden)
		MockPaint.rrect_h(ci, fill, minf(12 * s, fill.size.x * 0.5), Color("#ff9f1c"), Color("#ffe27a"))
		if fill.size.x > 24 * s and ratio < 1.0:
			var tail := Rect2(fill.end.x - 12 * s, fill.position.y, 12 * s, fill.size.y)
			ci.draw_rect(tail, Color("#ff9f1c").lerp(Color("#ffe27a"), (tail.position.x - fill.position.x + 6 * s) / fill.size.x))
	var txt := "MAX" if lvl >= MetaData.HERO_MAX_LEVEL else "%d/%d" % [have, need]
	MockPaint.text(self, ci, txt, bar, "Fredoka", 700, 14, "rgb(255, 247, 234)", "rgba(0, 0, 0, 0.7) 0px 1px 2px")
	var icon := _live_img("cardicon")
	if not icon.is_empty():
		draw_img_at(ci, icon, icon[2], Vector2.ZERO)
	# Talent des Helden (Sechseck links neben den gesperrten Plätzen)
	var talent := _live_img("talent")
	if not talent.is_empty():
		draw_img_at(ci, talent, talent[2], Vector2.ZERO)
	# Werte mit Vorschau
	var v := _values()
	var ids := ["stat", "stat_1", "stat_2"]
	var keys := ["dmg", "rel", "mag"]
	for k in 3:
		var r := live_rect(ids[k])
		MockPaint.rrect(ci, Rect2(r.position * s, r.size * s), 8 * s, Color("#141038"))
		var a: String = v[keys[k]][0]
		var b: String = v[keys[k]][1]
		var wa := MockPaint.text_width(a, "Fredoka", 700, 16)
		var wb := MockPaint.text_width(b, "Fredoka", 700, 16)
		var total := wa + 6.0 + 8.0 + 6.0 + wb
		var x := r.get_center().x - total * 0.5
		MockPaint.text(self, ci, a, Rect2(x, r.position.y, wa, r.size.y), "Fredoka", 700, 16, "rgb(255, 247, 234)")
		x += wa + 6.0
		var cy := r.get_center().y
		ci.draw_colored_polygon(PackedVector2Array([Vector2(x, cy - 5) * s, Vector2(x + 8, cy) * s, Vector2(x, cy + 5) * s]), Color("#3a7dff"))
		x += 14.0
		MockPaint.text(self, ci, b, Rect2(x, r.position.y, wb, r.size.y), "Fredoka", 700, 16, "rgb(125, 255, 138)")


# --- Knöpfe ----------------------------------------------------------------------------------

func handle(b: Dictionary) -> bool:
	var on := str(b.get("on", ""))
	if on == "closeSkill":
		# Antippen im Fenster selbst schließt es nicht (nur daneben, das X oder „Verbessern“)
		var p := (get_local_mouse_position() - off) / s
		if float(b["rect"][3]) >= H - 1.0 and (DIALOG.has_point(p) or DIALOG_ICON.has_point(p)):
			return true
		if float(b["rect"][1]) > 500.0 and float(b["rect"][3]) < 200.0:
			menu.toast("Fähigkeiten verbessern kommt bald")
		_close_skill()
		return true
	if on.begins_with("pick_"):
		_open_skill(on.trim_prefix("pick_"))
		return true
	match on:
		"prev", "next":
			var order := _order()
			if order.size() > 1:
				var i := order.find(hero)
				_set_hero(order[(i + (1 if on == "next" else -1) + order.size()) % order.size()])
			return true
		"levelUp":
			_level_up()
			return true
	if str(b.get("label", "")) == "Schließen":
		menu.close_board(self)
		return true
	for t in texts_of_button(int(b["i"])):
		if NAV.has(str(t["text"])):
			menu.close_board(self)
			menu.show_tab(NAV[str(t["text"])])
			return true
	return false


func _level_up() -> void:
	var lvl := Save.hero_level(hero)
	if lvl >= MetaData.HERO_MAX_LEVEL:
		menu.toast("%s hat schon die höchste Stufe" % GameData.HEROES[hero]["name"])
		return
	var need := MetaData.hero_cards_needed(lvl)
	if Save.hero_cards(hero) < need:
		menu.toast("Noch %d Karten bis zur nächsten Stufe" % (need - Save.hero_cards(hero)))
		return
	if Save.gold() < MetaData.hero_gold_needed(lvl):
		menu.toast("Dafür fehlen noch %s Gold" % MockScreen.num(MetaData.hero_gold_needed(lvl) - Save.gold()))
		return
	if not Save.level_hero(hero):
		return
	Sfx.play("levelup")
	refresh()
	if is_instance_valid(_level_view):
		_level_view.queue_free()
	_level_view = open_overlay("leveled")
	_level_view.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_level_view.set_text(_text_where(_level_view.data, func(t: Dictionary) -> bool: return float(t["size"]) == 28.0),
		"Stufe %d" % Save.hero_level(hero))
	# wie im Mockup nach 1,6 Sekunden wieder weg (die Animation hängt am Fenster selbst)
	var tw := _level_view.create_tween()
	tw.tween_interval(1.4)
	tw.tween_property(_level_view, "modulate:a", 0.0, 0.2)
	tw.tween_callback(_level_view.queue_free)


func _open_skill(kind: String) -> void:
	_close_skill()
	_skill = kind
	_skill_view = open_overlay("skill")
	var ov := _skill_view
	# Abdunklung liegt im Mockup unter dem Fenster: als Fläche ganz unten statt als Knopf-Bild oben
	for b in ov.buttons():
		if float(b.info["rect"][3]) >= H - 1.0:
			b.texture = null
	var dim := ColorRect.new()
	dim.color = Color(8 / 255.0, 6 / 255.0, 24 / 255.0, 0.74)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	ov.add_child(dim)
	ov.move_child(dim, 0)
	var title := _ult_name(hero) if kind == "supe" else String(CARDS[hero][0 if kind == "kett" else 1][0])
	ov.set_text(_text_where(ov.data, func(t: Dictionary) -> bool: return float(t["size"]) == 20.0 and int(t["button"]) < 0),
		"SUPERFÄHIGKEIT" if kind == "supe" else "KAMPFKARTE")
	ov.set_text(_text_where(ov.data, func(t: Dictionary) -> bool: return float(t["size"]) == 24.0 and int(t["button"]) < 0), title.to_upper())
	ov.set_text(_text_where(ov.data, func(t: Dictionary) -> bool: return float(t["size"]) == 12.0),
		String(ULT_TEXT[hero][3]) if kind == "supe" else "Wird im Kampf als Karte gezogen")
	ov.set_text(_text_where(ov.data, func(t: Dictionary) -> bool: return int(t["button"]) >= 0 and str(t["text"]) != "VERBESSERN"), SKILL_COST[kind])
	var layer := SkillLayer.new()
	layer.board = self
	layer.view = ov
	ov.place_at(layer, Rect2(0, 0, W, H))


func _close_skill() -> void:
	if is_instance_valid(_skill_view):
		_skill_view.queue_free()
	_skill_view = null
	_skill = ""


## Fähigkeiten-Fenster: Symbol, Sterne und Beschreibung (mit hervorgehobenem Teil, umbrochen)
func draw_skill(ci: CanvasItem, ov: MockView) -> void:
	draw_img_at(ci, _skill_icon(hero, _skill), ov.live_rect("sk_icon"), Vector2.ZERO)
	var sr := ov.live_rect("sk_stars")
	var n: int = SKILL_STARS.get(_skill, 0)
	var x0 := sr.get_center().x - (3 * 40.0 + 2 * 8.0) * 0.5
	for k in 3:
		var on := k < n
		MockPaint.star(ci, Rect2(Vector2(x0 + k * 48.0, sr.position.y) * s, Vector2(40, 40) * s),
			Color("#ffd34d") if on else Color("#2e2a52"), Color("#a86a00") if on else Color("#24203f"), 1.4 * 40.0 / 24.0 * s)
	var parts: Array = ULT_TEXT[hero].slice(0, 3) if _skill == "supe" else CARDS[hero][0 if _skill == "kett" else 1].slice(1, 4)
	_draw_rich(ci, ov.live_rect("sk_text"), parts)


## Absatz mittig umbrechen; der mittlere Teil ist grün hervorgehoben
func _draw_rich(ci: CanvasItem, box: Rect2, parts: Array) -> void:
	var words := []   # [Wort, Farbe, Leerzeichen davor]
	var cols := ["rgb(255, 247, 234)", "rgb(125, 255, 138)", "rgb(255, 247, 234)"]
	var space := false
	for k in parts.size():
		var toks := String(parts[k]).split(" ")
		for j in toks.size():
			if j > 0:
				space = true
			if toks[j] == "":
				continue
			words.append([toks[j], cols[k], space])
			space = false
	var sp := MockPaint.text_width(" ", "Nunito", 800, 16)
	var lines := [[]]
	var lw := 0.0
	for w in words:
		var ww := MockPaint.text_width(w[0], "Nunito", 800, 16)
		var add := ww + (sp if bool(w[2]) and not lines[-1].is_empty() else 0.0)
		if lw + add > box.size.x and not lines[-1].is_empty():
			lines.append([])
			lw = 0.0
			add = ww
		lines[-1].append([w[0], w[1], add - ww, ww])
		lw += add
	var lh := 16.0 * 1.45
	for i in lines.size():
		var total := 0.0
		for w in lines[i]:
			total += float(w[2]) + float(w[3])
		var x := box.get_center().x - total * 0.5
		for w in lines[i]:
			x += float(w[2])
			MockPaint.text(self, ci, w[0], Rect2(x, box.position.y + i * lh, w[3], lh), "Nunito", 800, 16, w[1], "rgba(0, 0, 0, 0.5) 0px 1px 2px")
			x += float(w[3])


class InfoLayer:
	extends Control
	var board: HeroBoard

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE

	func _draw() -> void:
		board.draw_info(self)


class ButtonDeco:
	extends Control
	var board: HeroBoard
	var btn: MockView.MockButton

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE
		set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)

	func _draw() -> void:
		board.draw_deco(self, btn)


class SkillLayer:
	extends Control
	var board: HeroBoard
	var view: MockView

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE

	func _draw() -> void:
		board.draw_skill(self, view)
