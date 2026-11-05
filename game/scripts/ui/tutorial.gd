class_name Tutorial
extends CanvasLayer
## Geführter Einstieg nach dem freigegebenen Mockup „Tutorial 1–6“ (Plan: Vorlage_Raw/Tutorial_v1/
## TUTORIAL_ABLAUF.md): Kein langes Tutorial am Anfang, sondern über die ersten drei Kämpfe wird der
## Spieler zu genau einem neuen Bereich geführt und führt den Schritt einmal selbst aus
## (Helden aufleveln, Tech-Werft ausbauen, Gebäude ausbauen).
##
## Aussehen: Abdunklung mit Lichtkegel auf das Ziel, pulsierende Zeigerhand, Hinweisblase mit Pip
## als Erzähler und „Schritt N von 5“. Bei Pflichtschritten geht nur das Ziel (und „Ohne Hilfe
## spielen“), alles andere ist gesperrt.
##
## Fehlt für einen Schritt Material (Energie, Karten, Gold, Sterne), schenkt das Spiel genau den
## Fehlbetrag, damit der Knopf sicher klappt (freigegeben am 05.11.2026).
## Fortschritt in Save.data["tut"]; „Spielstand zurücksetzen“ startet die Führung neu.

const W := 390.0
const H := 844.0
const PAD := 8.0
const BUBBLE_W := 354.0
const GOLD := Color("ffd56a")
const CREAM := Color("fff4d8")
const LILAC := Color("d9d2f0")
const DIM_A := 0.62
## Plasma-Anzeige unten links in der Kampfanzeige (Mockup-Punkte)
const PLASMA_RECT := Rect2(8, 718, 118, 58)
const PLASMA_SECS := 4.0

## Aus in Prüfbildern und automatischen Tests (dort darf nichts den Bildschirm verdecken)
static var enabled := true
## Prüfbild eines Schritts (--tutshot=pfad.png,abschnitt): Spielstand nachstellen, Bild speichern
static var shot_path := ""
static var shot_stage := ""
const SHOT_KEY := {"start": "play1", "wahl": "pick", "plasma": "plasma", "kern": "core", "karte": "card",
	"sieg": "result", "reiter": "nav#helden", "heldkarte": "herocard", "aufleveln": "levelup",
	"kampf2": "play4", "tech": "tech", "basis": "base01", "bau": "build01", "fertig": "done"}

var main: Node   # main.gd
var _root: Control
var _shade: Shade
var _hand: TextureRect
var _bubble: Bubble
var _step := {}
var _key := ""
var _t := 0.0
var _fade := 0.0
var _prev_state := ""
var _plasma_t := 0.0
var _paused := false   # Kampf für einen Hinweis angehalten
var _focused := false  # Basislager einmal auf die Kommandozentrale gezoomt
var _note := ""        # Geschenk zum aktuellen Schritt („Geschenk: +8 Karten“)
var _gift_key := ""
var _tex := {}


func _ready() -> void:
	layer = 20
	process_mode = Node.PROCESS_MODE_ALWAYS
	_root = Control.new()
	_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_root)
	_shade = Shade.new()
	_shade.tut = self
	_shade.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.add_child(_shade)
	_hand = TextureRect.new()
	_hand.texture = _img("zeigerhand")
	_hand.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_hand.stretch_mode = TextureRect.STRETCH_SCALE
	_hand.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.add_child(_hand)
	_bubble = Bubble.new()
	_bubble.tut = self
	_root.add_child(_bubble)
	_root.visible = false


func _img(id: String) -> Texture2D:
	if not _tex.has(id):
		_tex[id] = load("res://ui/tutorial/%s.webp" % id)
	return _tex[id]


# --- Spielstand ---------------------------------------------------------------------------

## Läuft die Führung gerade? (nicht im Test, nicht nach „Ohne Hilfe spielen“ oder dem Abschluss)
static func active() -> bool:
	if not enabled or Save.test_mode:
		return false
	var t = Save.data.get("tut", {})
	return t is Dictionary and not bool(t.get("done", false))


func _tut() -> Dictionary:
	if not Save.data.get("tut") is Dictionary:
		Save.data["tut"] = {}
	return Save.data["tut"]


func _flag(k: String) -> void:
	if bool(_tut().get(k, false)):
		return
	_tut()[k] = true
	Save.save_game()


## Held aus der ersten Heldenauswahl merken (an ihm wird später das Aufleveln gezeigt)
static func note_hero(id: String) -> void:
	if not active():
		return
	var t: Dictionary = Save.data["tut"]
	if str(t.get("hero", "")) == "":
		t["hero"] = id
		Save.save_game()


## Hilfe beenden (Abschluss oder „Ohne Hilfe spielen“)
func finish() -> void:
	_tut()["done"] = true
	Save.save_game()
	_unpause()
	_show({})


static func _wins() -> int:
	return (Save.data.get("won_levels", []) as Array).size()


static func _held_done() -> bool:
	for id in GameData.HERO_IDS:
		if Save.hero_level(id) > 1:
			return true
	return false


static func _base_done() -> bool:
	var b := Save.base()
	for id in b.keys():
		if int((b[id] as Dictionary).get("level", 1)) > 1:
			return true
	return false


# --- Ablauf ---------------------------------------------------------------------------------

func _process(delta: float) -> void:
	if main == null or not active():
		if _root.visible:
			_unpause()
			_show({})
		return
	_t += delta
	var st: String = main.state
	if _prev_state == "hero_select" and st == "battle":
		_flag("picked")
	if _prev_state == "cards" and st != "cards":
		_flag("card")
	_prev_state = st
	_show(_resolve(delta))
	if shot_path != "":
		_shot(delta)
	if _root.visible:
		_fade = minf(1.0, _fade + delta / 0.2)
		_root.modulate.a = _fade
		_animate()


func _resolve(delta: float) -> Dictionary:
	var t := _tut()
	var wins := _wins()
	if bool(main.get("mp")) or bool(main.get("hard")):
		return {}
	match str(main.state):
		"hero_select":
			if wins == 0 and not bool(t.get("picked", false)):
				return {"key": "pick", "n": 2, "pose": "winken", "y": 636.0, "mode": "none",
					"title": "Wähle deinen ersten Helden.", "body": "Jeder Held kann die Station schützen."}
		"battle":
			if wins == 0:
				return _battle_step(t, delta)
		"cards":
			if wins == 0 and not bool(t.get("card", false)):
				return {"key": "card", "n": 2, "pose": "zeigen", "y": 600.0, "mode": "none",
					"title": "Wähle eine Karte für dein Team.", "body": "Nimm einen Helden oder eine Verbesserung."}
		"result":
			return _result_step(wins)
		"menu":
			return _menu_step(wins)
	return {}


func _battle_step(t: Dictionary, delta: float) -> Dictionary:
	var pl: PlasmaCore = main.plasma
	var hud: BattleHud = main.hud
	if not bool(t.get("core", false)) and pl.core_ready() and main.battle.running:
		var b := _hud_core(hud)
		if b:
			return {"key": "core", "n": 2, "pose": "zeigen", "target": b.get_global_rect(), "circle": true,
				"mode": "catch", "pause": true, "action": _core_tap,
				"title": "Der Energiekern ist bereit!", "body": "Tippe darauf und hol dir Plasma."}
	if not bool(t.get("plasma", false)) and main.battle.running and main.battle.elapsed > 1.5:
		_plasma_t += delta
		if _plasma_t > PLASMA_SECS:
			_flag("plasma")
			return {}
		return {"key": "plasma", "n": 2, "pose": "zeigen", "target": _view_rect(hud, PLASMA_RECT), "mode": "none",
			"dim": false, "hand": false,
			"title": "Dein Plasma füllt sich wieder auf.", "body": "Damit schießen deine Helden."}
	return {}


func _hud_core(hud: BattleHud) -> MockView.MockButton:
	for b in hud.buttons():
		if str(b.info.get("label", "")).begins_with("Energiekern"):
			return b
	return null


func _core_tap() -> void:
	_unpause()
	main.plasma.try_manual_pull()
	_flag("core")


## Nach dem Sieg: zurück ins Menü, dort geht es mit dem nächsten Bereich weiter
func _result_step(wins: int) -> Dictionary:
	var r = main.get("_screen")
	if not r is ResultScreen or not (r as ResultScreen).won or wins < 1:
		return {}
	var b := (r as ResultScreen).button("Main.dc.html")
	if b == null:
		return {}
	var n := 3 if wins == 1 else (4 if wins == 2 else 5)
	return {"key": "result%d" % wins, "n": n, "pose": "freuen", "target": b.get_global_rect(), "mode": "pass",
		"title": "Geschafft! Das ist deine Beute.", "body": "Tippe auf Zum Menü."}


func _menu_step(wins: int) -> Dictionary:
	var menu: MainMenu = main.menu
	if not menu.visible or is_instance_valid(menu._modal) or is_instance_valid(menu._success):
		return {}
	var top: Control = null
	for b in menu._boards:
		if is_instance_valid(b) and not b.is_queued_for_deletion():
			top = b
	if wins == 0:
		return _play_step(menu, top, 1, "Bereit für deinen ersten Einsatz?", "Tippe auf Spielen.", "winken")
	if not _held_done():
		return _hero_step(menu, top)
	if wins == 1:
		return _play_step(menu, top, 4, "Teste deinen stärkeren Helden.", "Tippe auf Spielen.", "zeigen")
	if Save.tech_count() == 0:
		return _tech_step(menu, top)
	if wins == 2:
		return _play_step(menu, top, 5, "Die Station ist stärker geworden.", "Starte den nächsten Kampf.", "zeigen")
	if not _base_done():
		return _base_step(menu, top)
	if top != null:
		return {}
	return {"key": "done", "n": 5, "pose": "freuen", "mode": "close", "done": true, "y": 150.0, "h": 128.0,
		"title": "Du bist bereit für die Station!", "body": "Viel Spaß bei deinem nächsten Einsatz."}


## Knopf in einem Mockup-Bildschirm über sein Ziel, eingeschränkt auf einen Bereich (Mockup-Punkte)
func _find(view: MockView, href: String, y_min := 0.0, y_max := H) -> MockView.MockButton:
	if view == null:
		return null
	for b in view.buttons():
		var r: Array = b.info.get("rect", [0, 0, 0, 0])
		if str(b.info.get("href", "")) == href and float(r[1]) >= y_min and float(r[1]) <= y_max:
			return b
	return null


func _nav_step(menu: MainMenu, href: String, n: int, title: String, body: String) -> Dictionary:
	var b := _find(menu._mock, href, 740.0)
	if b == null:
		return {}
	return {"key": "nav" + href, "n": n, "pose": "winken", "target": b.get_global_rect(), "mode": "pass",
		"title": title, "body": body}


func _play_step(menu: MainMenu, top: Control, n: int, title: String, body: String, pose: String) -> Dictionary:
	if top != null:
		return {}
	if not menu._mock is HomeScreen:
		return _nav_step(menu, "#kampf", n, "Weiter geht's!", "Öffne den Reiter Kampf.")
	var b := _find(menu._mock, "#kampf", 600.0, 740.0)
	if b == null:
		return {}
	return {"key": "play%d" % n, "n": n, "pose": pose, "target": b.get_global_rect(), "mode": "pass",
		"title": title, "body": body, "gift": _gift_energy, "regift": true}


func _hero_step(menu: MainMenu, top: Control) -> Dictionary:
	if top is HeroBoard:
		var hb := top as HeroBoard
		var up := hb._btn("levelUp")
		if up == null or Save.hero_level(hb.hero) >= MetaData.HERO_MAX_LEVEL:
			return {}
		return {"key": "levelup:" + hb.hero, "n": 3, "pose": "zeigen", "target": up.get_global_rect(), "mode": "pass",
			"title": "Tippe auf Aufleveln.", "body": "So wird dein Held dauerhaft stärker.",
			"gift": _gift_hero.bind(hb)}
	if top != null:
		return {}
	var m: MockScreen = menu._mock
	if menu.current_tab == "sammlung" and m != null and m.get("_cards") is Dictionary:
		var cards: Dictionary = m.get("_cards")
		var open: Array = m.get("_open")
		var hero := str(_tut().get("hero", ""))
		if not open.has(hero):
			hero = str(open[0]) if not open.is_empty() else ""
		if not cards.has(hero):
			return {}
		var r: Rect2 = cards[hero]
		r.position.y -= float(m.get("_scroll"))
		return {"key": "herocard", "n": 3, "pose": "zeigen", "target": _view_rect(m, r), "mode": "pass",
			"title": "Tippe auf deinen ersten Helden.", "body": "Wir schauen uns seinen Ausbau an."}
	return _nav_step(menu, "#helden", 3, "Dein Held kann stärker werden.", "Öffne den Reiter Helden.")


func _tech_step(menu: MainMenu, top: Control) -> Dictionary:
	if top != null:
		return {}
	if menu.current_tab == "upgrades" and menu._mock is UpgradesTab:
		var u := menu._mock as UpgradesTab
		if u.talents or is_instance_valid(u._ammo):
			return {}
		if Save.tech_state(u.selected) != "open":
			# ein ausbaubares Modul vorauswählen (das günstigste offene)
			for a in MetaData.TECH_AREAS:
				for t in MetaData.tech_in_area(a):
					if Save.tech_state(str(t["id"])) == "open" and Save.tech_state(u.selected) != "open":
						u.set_area(a)
						u.select(str(t["id"]))
			if Save.tech_state(u.selected) != "open":
				return {}
		return {"key": "tech:" + u.selected, "n": 4, "pose": "zeigen", "y": 330.0, "target": _view_rect(u, UpgradesTab.BUILD),
			"mode": "pass", "title": "Tippe auf Ausbauen.", "body": "Diese Verbesserung bleibt dir erhalten.",
			"gift": _gift_tech.bind(u)}
	return _nav_step(menu, "#upgrades", 4, "Jetzt stärken wir die Station.", "Öffne Upgrades.")


func _base_step(menu: MainMenu, top: Control) -> Dictionary:
	if top is BuildingWindow:
		var w := top as BuildingWindow
		var b := w._big_button()
		if w.id != "01" or b == null:
			return {}
		return {"key": "build01", "n": 5, "pose": "zeigen", "target": b.get_global_rect(), "mode": "pass",
			"title": "Baue das Gebäude oder baue es aus.", "body": "Es sammelt mit der Zeit Nachschub.",
			"gift": _gift_base.bind(w)}
	if top != null:
		return {}
	if menu.current_tab == "basis" and menu._mock is BaseTab:
		var map := (menu._mock as BaseTab).map
		if map == null or not map._layout.has("01"):
			return {}
		var area := map.get_global_rect()
		var lr: Array = map._layout["01"]["rect"]
		var r := Rect2(area.position + map._to_screen(Vector2(float(lr[0]), float(lr[1]))), Vector2(float(lr[2]), float(lr[3])) * map._zoom)
		if not _focused:
			_focused = true
			map.focus("01")
		return {"key": "base01", "n": 5, "pose": "zeigen", "target": r, "mode": "pass",
			"title": "Tippe auf die Kommandozentrale.", "body": "Hier versorgst du deine Station."}
	return _nav_step(menu, "#basis", 5, "Zeit für dein Basislager.", "Öffne den Reiter Basis.")


## Rechteck in Mockup-Punkten einer Ansicht -> Bildschirm
func _view_rect(v: MockView, r: Rect2) -> Rect2:
	var p := v.get_global_rect().position
	return Rect2(p + v.to_screen(r.position), r.size * v.s)


# --- Prüfbilder ------------------------------------------------------------------------------

## Spielstand für einen Abschnitt nachstellen (nur für Prüfbilder, wird nicht gespeichert)
static func setup_stage(stage: String) -> void:
	Save.test_mode = false
	Save.data = Save.default_data()
	var wins := 0
	match stage:
		"reiter", "heldkarte", "aufleveln", "kampf2":
			wins = 1
		"tech":
			wins = 2
		"basis", "bau", "fertig":
			wins = 3
	for n in range(1, wins + 1):
		Save.data["won_levels"].append("N%d" % n)
	Save.data["max_level"] = wins + 1
	var hero: String = Save.squad()[0]
	var t := {"hero": hero}
	if stage not in ["start", "wahl"]:
		t.merge({"picked": true})
	if stage in ["kern", "karte", "sieg"] or wins > 0:
		t.merge({"plasma": true})
	if stage in ["karte", "sieg"] or wins > 0:
		t.merge({"core": true})
	if stage == "sieg" or wins > 0:
		t.merge({"card": true})
	Save.data["tut"] = t
	if stage == "kampf2" or wins >= 2:
		Save.data["heroes"][hero]["level"] = 2
	if wins >= 3:
		Save.data["tech"] = ["shield1"]
	if stage == "fertig":
		Save.base()["01"] = {"level": 2, "stock": 0.0, "time": int(Time.get_unix_time_from_system())}


var _shot_t := 0.0


func _shot(delta: float) -> void:
	_shot_t += delta
	var st := str(main.state)
	if st == "hero_select" and shot_stage != "wahl" and main.get("_screen") != null:
		main._on_hero_picked(Save.squad()[0])
	elif st == "battle" and main.battle.elapsed > 2.0:
		match shot_stage:
			"kern":
				main.plasma._manual_cd = 0.0
			"karte":
				main.pending_levelups = 1
				main._open_card_pick()
			"sieg":
				main._on_level_won()
	var want: String = SHOT_KEY.get(shot_stage, "?")
	if (_key.begins_with(want) and _t > 0.6) or _shot_t > 60.0:
		get_viewport().get_texture().get_image().save_png(shot_path)
		print("BILD gespeichert: ", shot_path, "" if _key.begins_with(want) else " (Schritt %s nicht erreicht, jetzt: %s)" % [want, _key])
		shot_path = ""
		get_tree().quit()


# --- Geschenke: genau der Fehlbetrag ---------------------------------------------------------

func _gift_energy() -> Array:
	var need := MetaData.ENERGY_COST - Save.energy()
	if need <= 0:
		return []
	Save.add("energy", need)
	main.menu._refresh_top()
	return ["+%d Energie" % need]


func _gift_hero(hb: HeroBoard) -> Array:
	var id := hb.hero
	var lvl := Save.hero_level(id)
	var parts := []
	var cards := MetaData.hero_cards_needed(lvl) - Save.hero_cards(id)
	if cards > 0:
		Save.add_hero_cards(id, cards)
		parts.append("+%d Karten" % cards)
	var gold := MetaData.hero_gold_needed(lvl) - Save.gold()
	if gold > 0:
		Save.add("gold", gold)
		parts.append("+%d Gold" % gold)
	if not parts.is_empty():
		hb.refresh()
	return parts


func _gift_tech(u: UpgradesTab) -> Array:
	var gold := int(MetaData.tech(u.selected).get("cost", 0)) - Save.gold()
	if gold <= 0:
		return []
	Save.add("gold", gold)
	u.refresh()
	return ["+%d Gold" % gold]


func _gift_base(w: BuildingWindow) -> Array:
	var c := BaseData.upgrade_cost(w.id, Save.base_level(w.id))
	var parts := []
	var gold := int(c[0]) - Save.gold()
	if gold > 0:
		Save.add("gold", gold)
		parts.append("+%d Gold" % gold)
	var stars := int(c[1]) - Save.stars()
	if stars > 0:
		Save.add("stars", stars)
		parts.append("+%d Sterne" % stars)
	if not parts.is_empty() and w.has_method("refresh"):
		w.refresh()
	return parts


# --- Anzeige ----------------------------------------------------------------------------------

func _unpause() -> void:
	if _paused:
		_paused = false
		if main and str(main.state) == "battle":
			get_tree().paused = false


func _show(step: Dictionary) -> void:
	var key := str(step.get("key", ""))
	if key != _key:
		if shot_path != "":
			print("TUT schritt: ", key, " zustand ", main.state)
		_key = key
		_fade = 0.0
		_t = 0.0
		if not bool(step.get("pause", false)):
			_unpause()
		_note = ""
	# Geschenk beim Erscheinen des Schritts; Energie auch später noch (sie kann inzwischen fehlen)
	if step.has("gift") and (key != _gift_key or bool(step.get("regift", false))):
		_gift_key = key
		var parts: Array = (step["gift"] as Callable).call()
		if not parts.is_empty():
			_note = "Geschenk: " + ", ".join(parts)
	if bool(step.get("pause", false)) and not _paused:
		_paused = true
		get_tree().paused = true
	step["note"] = _note
	_step = step
	_root.visible = key != ""
	if key == "":
		_shade.mode = "none"
		return
	var vs := _root.size
	var s := minf(vs.x / W, vs.y / H)
	var off := (vs - Vector2(W, H) * s) * 0.5
	var target: Rect2 = step.get("target", Rect2())
	var has_target := target.size != Vector2.ZERO
	var circle := bool(step.get("circle", false))
	var hole := Rect2()
	if has_target:
		if circle:
			var rr := target.size.x * 0.5 + PAD * s
			hole = Rect2(target.get_center() - Vector2(rr, rr), Vector2(rr, rr) * 2.0)
		else:
			hole = target.grow(PAD * s)
	_shade.mode = str(step.get("mode", "pass"))
	_shade.hole = hole
	_shade.set_box(hole, (hole.size.x * 0.5) if circle else 24.0 * s,
		DIM_A * (0.75 if _shade.mode == "close" else 1.0) if bool(step.get("dim", true)) else 0.0, has_target, 2.0 * s)
	# Hinweisblase: über dem Ziel, wenn es in der unteren Hälfte liegt, sonst darunter
	var d := Rect2((target.position - off) / s, target.size / s)
	_bubble.setup(step, s)
	var bh := maxf(float(step.get("h", 112.0)), _bubble.needed_h())
	var flip := has_target and d.end.y > 770.0
	var by := 150.0
	if step.has("y"):
		by = float(step["y"])
	elif has_target:
		if d.get_center().y > 422.0:
			by = d.position.y - PAD - 12.0 - bh - (40.0 if flip else 0.0)
		else:
			by = d.end.y + PAD + 20.0
	_bubble.position = off + Vector2(18.0, by) * s
	_bubble.size = Vector2(BUBBLE_W, bh) * s
	_bubble.bh = bh
	# Zeigerhand: Fingerspitze rechts im Ziel; am unteren Rand von oben (gespiegelt)
	_hand.visible = has_target and bool(step.get("hand", true))
	if _hand.visible:
		var hs := 50.0 * s
		var tip: Vector2
		if flip:
			tip = target.position + Vector2(target.size.x * 0.5 + target.size.x * 0.3, target.size.y * 0.2)
			_hand.flip_v = true
			_hand.pivot_offset = Vector2(0.14, 0.9) * hs
		else:
			tip = Vector2(target.end.x - minf(59.0 * s, target.size.x * 0.25), target.position.y + target.size.y * 0.63)
			_hand.flip_v = false
			_hand.pivot_offset = Vector2(0.14, 0.1) * hs
		_hand.size = Vector2(hs, hs)
		_hand.position = tip - _hand.pivot_offset


func _animate() -> void:
	# Zeigerhand pulsiert sanft (1,1 s), Goldring atmet (1,6 s)
	var k := 0.5 - 0.5 * cos(_t * TAU / 1.1)
	_hand.scale = Vector2.ONE * (1.0 + 0.06 * k)
	_shade.ring_a = 0.7 + 0.3 * (0.5 - 0.5 * cos(_t * TAU / 1.6))
	_shade.update_ring()
	_bubble.anim_t = _t
	_bubble._front.queue_redraw()


## Abdunklung mit Lichtkegel (Shader: abgerundetes Loch und Goldring). Fängt alle Eingaben ab,
## außer im Loch (mode "pass"); "catch": Antippen im Loch ruft die Aktion des Schritts auf;
## "close": Antippen irgendwo schließt (Abschluss); "none": sperrt nichts.
class Shade:
	extends ColorRect

	const CODE := """
shader_type canvas_item;
uniform vec2 px_size = vec2(1.0);
uniform vec2 box_pos;
uniform vec2 box_size;
uniform float radius = 0.0;
uniform float dim_a = 0.62;
uniform float ring_a = 1.0;
uniform float ring_w = 2.0;
uniform float has_box = 0.0;
float sd(vec2 p, vec2 b, float r) {
	vec2 q = abs(p) - b + r;
	return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - r;
}
void fragment() {
	vec2 p = UV * px_size;
	float d = sd(p - (box_pos + box_size * 0.5), box_size * 0.5, radius);
	float outside = mix(1.0, smoothstep(-0.75, 0.75, d), has_box);
	float ring = has_box * smoothstep(-ring_w - 0.75, -ring_w + 0.75, d) * (1.0 - smoothstep(-0.75, 0.75, d));
	vec4 dimc = vec4(0.043, 0.027, 0.11, dim_a * outside);
	vec4 gold = vec4(1.0, 0.835, 0.416, ring_a);
	COLOR = mix(dimc, gold, ring);
}
"""

	var tut: Tutorial
	var mode := "none"
	var hole := Rect2()
	var ring_a := 1.0
	var _mat: ShaderMaterial

	func _ready() -> void:
		color = Color.WHITE
		var sh := Shader.new()
		sh.code = CODE
		_mat = ShaderMaterial.new()
		_mat.shader = sh
		material = _mat
		mouse_filter = Control.MOUSE_FILTER_STOP

	func set_box(r: Rect2, radius: float, dim_a: float, has_box: bool, ring_w: float) -> void:
		var p := r.position - global_position
		_mat.set_shader_parameter("px_size", size)
		_mat.set_shader_parameter("box_pos", p)
		_mat.set_shader_parameter("box_size", r.size)
		_mat.set_shader_parameter("radius", minf(radius, minf(r.size.x, r.size.y) * 0.5))
		_mat.set_shader_parameter("dim_a", dim_a)
		_mat.set_shader_parameter("has_box", 1.0 if has_box else 0.0)
		_mat.set_shader_parameter("ring_w", ring_w)
		mouse_filter = Control.MOUSE_FILTER_IGNORE if mode == "none" else Control.MOUSE_FILTER_STOP

	func update_ring() -> void:
		_mat.set_shader_parameter("ring_a", ring_a)

	func _has_point(p: Vector2) -> bool:
		if mode == "none":
			return false
		if mode == "pass":
			return not hole.has_point(p + global_position)
		return true

	func _gui_input(e: InputEvent) -> void:
		if not (e is InputEventMouseButton and (e as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT):
			return
		accept_event()
		if not e.pressed:
			return
		if mode == "catch" and hole.has_point(get_global_mouse_position()):
			var a = tut._step.get("action")
			if a is Callable:
				(a as Callable).call()
		elif mode == "close":
			tut.finish()


## Hinweisblase: dunkelviolett mit Goldrand, Pip links, Überschrift (Fredoka) und Text (Nunito),
## oben rechts „Schritt N von 5“, unten „Ohne Hilfe spielen“.
class Bubble:
	extends Control

	const BODY := """
shader_type canvas_item;
uniform vec2 px_size = vec2(1.0);
uniform vec2 box_pos;
uniform vec2 box_size;
uniform float radius = 18.0;
uniform float border = 2.0;
uniform float sh_off = 10.0;
uniform float sh_blur = 24.0;
float sd(vec2 p, vec2 b, float r) {
	vec2 q = abs(p) - b + r;
	return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - r;
}
void fragment() {
	vec2 p = UV * px_size;
	vec2 c = box_pos + box_size * 0.5;
	float d = sd(p - c, box_size * 0.5, radius);
	float ds = sd(p - c - vec2(0.0, sh_off), box_size * 0.5, radius);
	float sh = 0.55 * (1.0 - smoothstep(-sh_blur * 0.3, sh_blur, ds));
	float t = clamp((p.y - box_pos.y) / box_size.y, 0.0, 1.0);
	vec3 c1 = vec3(0.267, 0.188, 0.435);
	vec3 c2 = vec3(0.173, 0.122, 0.345);
	vec3 c3 = vec3(0.137, 0.090, 0.278);
	vec3 g = t < 0.4 ? mix(c1, c2, t / 0.4) : mix(c2, c3, (t - 0.4) / 0.6);
	// feine helle Kante oben innen
	float hi = (1.0 - smoothstep(border, border + 2.5, p.y - box_pos.y)) * 0.12;
	g = mix(g, vec3(1.0), hi);
	float inside = 1.0 - smoothstep(-0.75, 0.75, d);
	float edge = smoothstep(-border - 0.75, -border + 0.75, d);
	vec3 col = mix(g, vec3(1.0, 0.835, 0.416), edge);
	COLOR = mix(vec4(0.0, 0.0, 0.0, sh), vec4(col, 1.0), inside);
}
"""
	const MARGIN := 34.0   # Platz für den Schatten (Mockup-Punkte)

	var tut: Tutorial
	var bh := 112.0
	var anim_t := 0.0
	var _s := 1.0
	var _step := {}
	var _body: ColorRect
	var _mat: ShaderMaterial
	var _pip: TextureRect
	var _title: Label
	var _text: Label
	var _front: Control
	var _link := Rect2()

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_STOP
		_body = ColorRect.new()
		_body.color = Color.WHITE
		_body.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var sh := Shader.new()
		sh.code = BODY
		_mat = ShaderMaterial.new()
		_mat.shader = sh
		_body.material = _mat
		add_child(_body)
		_pip = TextureRect.new()
		_pip.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		_pip.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		_pip.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(_pip)
		_title = _label()
		_text = _label()
		_front = Control.new()
		_front.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_front.set_anchors_preset(Control.PRESET_FULL_RECT)
		_front.draw.connect(_draw_front)
		add_child(_front)

	func _label() -> Label:
		var l := Label.new()
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.mouse_filter = Control.MOUSE_FILTER_IGNORE
		l.label_settings = LabelSettings.new()
		add_child(l)
		return l

	func setup(step: Dictionary, s: float) -> void:
		var changed: bool = step.get("key") != _step.get("key") or not is_equal_approx(s, _s)
		_step = step
		_s = s
		if not changed:
			return
		_pip.texture = tut._img("pip_" + str(step.get("pose", "zeigen")))
		var title := str(step.get("title", ""))
		var ts := _title.label_settings
		ts.font = MockFonts.font("Fredoka", 700)
		ts.font_size = roundi((18.0 if title.length() < 30 else 16.0) * s)
		ts.font_color = Tutorial.CREAM
		ts.line_spacing = -2.0 * s
		ts.shadow_color = Color(10 / 255.0, 6 / 255.0, 30 / 255.0, 0.6)
		ts.shadow_offset = Vector2(0, 2) * s
		ts.shadow_size = 0
		_title.text = title
		var bs := _text.label_settings
		bs.font = MockFonts.font("Nunito", 700)
		bs.font_size = roundi(14.0 * s)
		bs.font_color = Tutorial.CREAM
		_text.text = str(step.get("body", ""))
		_fit()

	func _notification(what: int) -> void:
		if what == NOTIFICATION_RESIZED:
			_fit()

	## Höhe eines Textes bei Breite w (Pixel)
	func _text_h(l: Label, w: float) -> float:
		var ls := l.label_settings
		var sz := ls.font.get_multiline_string_size(l.text, HORIZONTAL_ALIGNMENT_LEFT, w, ls.font_size)
		var lines := maxi(1, roundi(sz.y / maxf(1.0, ls.font.get_height(ls.font_size))))
		return sz.y + ls.line_spacing * (lines - 1)

	func _text_w() -> float:
		return (Tutorial.BUBBLE_W - 96.0 - 14.0) * _s

	## Nötige Höhe der Blase (Mockup-Punkte): Text plus Rand oben und die Zeile unten
	func needed_h() -> float:
		var w := _text_w()
		return (_text_h(_title, w) + 4.0 * _s + _text_h(_text, w)) / _s + 26.0 + 24.0

	func _fit() -> void:
		if _body == null:
			return
		var s := _s
		var m := MARGIN * s
		_body.position = Vector2(-m, -m)
		_body.size = size + Vector2(m, m) * 2.0
		_mat.set_shader_parameter("px_size", _body.size)
		_mat.set_shader_parameter("box_pos", Vector2(m, m))
		_mat.set_shader_parameter("box_size", size)
		_mat.set_shader_parameter("radius", 18.0 * s)
		_mat.set_shader_parameter("border", 2.0 * s)
		_mat.set_shader_parameter("sh_off", 10.0 * s)
		_mat.set_shader_parameter("sh_blur", 24.0 * s)
		var pip := 92.0 * s
		_pip.position = Vector2(2.0 * s, size.y - 6.0 * s - pip)
		_pip.size = Vector2(pip, pip)
		# Text mittig zwischen oben und der Zeile „Ohne Hilfe spielen“
		var x := 96.0 * s
		var w := _text_w()
		var th := _text_h(_title, w)
		var bh2 := _text_h(_text, w)
		_title.size = Vector2(w, th)
		_text.size = Vector2(w, bh2)
		var gap := 4.0 * s
		var top := (size.y - 26.0 * s - (th + gap + bh2)) * 0.5
		_title.position = Vector2(x, top)
		_text.position = Vector2(x, top + th + gap)
		_front.queue_redraw()

	func _draw_front() -> void:
		var s := _s
		var ci := _front
		# „Schritt N von 5“
		var done := bool(_step.get("done", false))
		var chip := "Schritt %d von 5%s" % [int(_step.get("n", 1)), " ✓" if done else ""]
		var f := MockFonts.font("Nunito", 800)
		var fs := roundi(11.5 * s)
		var tw := f.get_string_size(chip, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var cr := Rect2(size.x - 16.0 * s - tw - 20.0 * s, -11.0 * s, tw + 20.0 * s, 20.0 * s)
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color("2c1f58")
		sb.border_color = Tutorial.GOLD
		sb.set_border_width_all(maxi(1, roundi(1.5 * s)))
		sb.set_corner_radius_all(roundi(9.0 * s))
		ci.draw_style_box(sb, cr)
		ci.draw_string(f, Vector2(cr.position.x + 10.0 * s, cr.get_center().y + fs * 0.36), chip, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Tutorial.GOLD)
		# Geschenk zum Schritt: grünes Schild links oben
		var note := str(_step.get("note", ""))
		if note != "":
			var nw := f.get_string_size(note, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
			var nr := Rect2(16.0 * s, -11.0 * s, nw + 20.0 * s, 20.0 * s)
			var nb := StyleBoxFlat.new()
			nb.bg_color = Color("2f8a3a")
			nb.border_color = Tutorial.GOLD
			nb.set_border_width_all(maxi(1, roundi(1.5 * s)))
			nb.set_corner_radius_all(roundi(9.0 * s))
			ci.draw_style_box(nb, nr)
			ci.draw_string(f, Vector2(nr.position.x + 10.0 * s, nr.get_center().y + fs * 0.36), note, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color.WHITE)
		# „Ohne Hilfe spielen“ (beim Abschluss: „Tippen zum Weiterspielen“)
		var lf := MockFonts.font("Nunito", 700)
		var ls := roundi(12.0 * s)
		var link := "Tippen zum Weiterspielen" if done else "Ohne Hilfe spielen"
		var lw := lf.get_string_size(link, HORIZONTAL_ALIGNMENT_LEFT, -1, ls).x
		var base := Vector2(96.0 * s, size.y - 8.0 * s - 3.0 * s)
		ci.draw_string(lf, base, link, HORIZONTAL_ALIGNMENT_LEFT, -1, ls, Tutorial.LILAC)
		if not done:
			ci.draw_line(base + Vector2(0, 2.0 * s), base + Vector2(lw, 2.0 * s), Tutorial.LILAC, maxf(1.0, 1.0 * s))
		_link = Rect2(base.x - 6.0 * s, base.y - ls - 6.0 * s, lw + 12.0 * s, ls + 14.0 * s)
		# Abschluss: grünes Häkchen
		if done:
			var k := clampf(anim_t / 0.5, 0.0, 1.0)
			var pop := (0.4 + 0.7 * k / 0.7) if k < 0.7 else (1.1 - 0.1 * (k - 0.7) / 0.3)
			var c := Vector2(size.x - 38.0 * s, size.y - 36.0 * s)
			var r := 20.0 * s * pop
			ci.draw_circle(c, r + 5.0 * s, Color(0.47, 0.9, 0.36, 0.25))
			ci.draw_circle(c, r, Color("78e65b"))
			var q := r / 20.0
			var pts := PackedVector2Array([c + Vector2(-7, 0.5) * q, c + Vector2(-2.5, 5) * q, c + Vector2(7, -4.5) * q])
			ci.draw_polyline(pts, Color("14320e"), 3.4 * q, true)

	func _gui_input(e: InputEvent) -> void:
		if not (e is InputEventMouseButton and (e as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT):
			return
		accept_event()
		if e.pressed:
			return
		if bool(_step.get("done", false)) or _link.has_point(get_local_mouse_position()):
			tut.finish()
