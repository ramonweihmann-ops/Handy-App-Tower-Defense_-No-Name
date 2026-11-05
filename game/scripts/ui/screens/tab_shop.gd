extends MockScreen
## Shop nach den freigegebenen Mockups „Shop · Angebote / Truhen / Aufladen (neu)“ und „Shop“ (Main-c4lv).
## Der Rahmen (Kopfleiste, Reiter, Menü) kommt aus ui_mock/shop, der Inhalt jedes Reiters ist eine lange
## Seite (ui_mock/shop_<reiter>), die zwischen Kopfleiste und Reitern scrollt. Event bleibt eine Seite.
##
## Mit echter Spiellogik: Tagesangebote (Heldenkarten für drei eigene Helden, jeden Tag neu, das erste
## gratis), Gratis-Truhe und Heldentruhe, Energie, Gold-Shop (zwei Gratis-Pakete am Tag, dann Gold gegen
## Edelsteine). Echtgeld-Angebote (Prime, Werbefrei, 2× Tempo, Edelstein-Pakete …) zeigen einen Hinweis,
## bis die App im Play Store ist. „Gratis“ braucht in der Testphase kein Werbevideo.

const PAGES := ["angebote", "truhen", "aufladen", "event"]
const PLAY_STORE := "Echte Käufe kommen, wenn die App im Play Store ist. In der Testphase gibt es Edelsteine über den Battle Pass, das Glücksrad und die tägliche Belohnung."
const TEMPO_HINT := "2× Tempo ist in der Testphase für alle frei. Kaufen kannst du es, wenn die App im Play Store ist."
## Inhaltsbereich zwischen Kopfleiste und Reitern (Mockup-Punkte des Rahmens)
const AREA := Rect2(0, 64, 390, 668)
## Höhe unter dem Inhalt (Reiter und Menü) auf den langen Seiten
const BOTTOM := 112.0

var page := "angebote"
var _page_view: MockView
var _clip: Control
var _chest: TextureRect
var _cards: Array = []     # Tagesangebote: [Karte, Balken] je Angebot
var _t := 0.0
var _scroll := 0.0
var _vel := 0.0
var _press := Vector2.ZERO
var _press_scroll := 0.0
var _pressing := false
var _dragging := false
var _last_y := 0.0
## Prüfbilder: so weit nach unten gescrollt öffnen (--shop-scroll=N, Mockup-Punkte)
static var debug_scroll := 0.0


func _init(m: MainMenu) -> void:
	super("shop", m, {"level": "12", "energy": "25/30", "gold": "4.573", "gems": "350"})
	page = str(m.sub_tab.get("shop", "angebote"))
	if not page in PAGES:
		page = "angebote"
	state = page


func _ready() -> void:
	super()
	_clip = Control.new()
	_clip.clip_contents = true
	_clip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	place_at(_clip, AREA)
	_clip.resized.connect(_fit_page)
	_build_page()
	refresh()


func _process(delta: float) -> void:
	super(delta)
	_t += delta
	# Die Truhe wippt leicht, als wollte sie gleich aufspringen
	if is_instance_valid(_chest):
		_chest.rotation = sin(_t * 1.7) * 0.05
		_chest.scale = Vector2.ONE * (1.0 + 0.035 * sin(_t * 3.1))
	# Nachlaufen nach dem Wischen
	if not _pressing and absf(_vel) > 5.0:
		_set_scroll(_scroll + _vel * delta)
		_vel *= pow(0.04, delta)


## Einen der vier Reiter zeigen
func show_page(name: String) -> void:
	if not name in PAGES:
		return
	page = name
	# Texte haben je Zustand eigene Nummern: Ersetzungen gelten nur für den bisherigen Zustand
	_overrides.clear()
	_hidden.clear()
	show_state(name)
	_build_page()
	refresh()


# --- Lange Seite zum Scrollen ------------------------------------------------------------

func _build_page() -> void:
	if is_instance_valid(_page_view):
		_page_view.queue_free()
	_page_view = null
	_chest = null
	_cards.clear()
	_scroll = 0.0
	_vel = 0.0
	if _clip == null or page == "event":
		return
	var v := MockView.new("shop_" + page)
	_clip.add_child(v)
	# MockView füllt sonst seinen Platz aus; hier bestimmt die Seite selbst ihre Höhe
	v.set_anchors_preset(Control.PRESET_TOP_LEFT)
	v._fill.visible = false
	v.button_pressed.connect(_on_pressed)
	_page_view = v
	if page == "angebote":
		_chest = v.live_image("chest", true)
		for k in 3:
			var card := DailyCard.new()
			var bar := DailyBar.new()
			v.place("dcard" + ("" if k == 0 else "_%d" % k), card, true)
			v.place("dbar" + ("" if k == 0 else "_%d" % k), bar, true)
			_cards.append([card, bar])
	_scroll = clampf(debug_scroll, 0.0, _max_scroll())
	_fit_page()


func _fit_page() -> void:
	if not is_instance_valid(_page_view) or _clip == null:
		return
	var v := _page_view
	v.size = Vector2(W, v.page_h) * s
	v.position = Vector2(0, (-AREA.position.y - _scroll) * s)


func _max_scroll() -> float:
	if not is_instance_valid(_page_view):
		return 0.0
	return maxf(0.0, _page_view.page_h - AREA.position.y - BOTTOM - AREA.size.y)


func _set_scroll(v: float) -> void:
	_scroll = clampf(v, 0.0, _max_scroll())
	if _scroll <= 0.0 or _scroll >= _max_scroll():
		_vel = 0.0
	_fit_page()


## Wischen im Inhaltsbereich: Knöpfe bekommen das Antippen weiter, ab ein paar Punkten Bewegung wird
## daraus Scrollen (dann löst der Knopf nicht aus).
func _input(e: InputEvent) -> void:
	if not is_instance_valid(_page_view) or not is_visible_in_tree() or not _on_top():
		_pressing = false
		return
	var area := _clip.get_global_rect()
	if e is InputEventMouseButton:
		var mb := e as InputEventMouseButton
		if mb.button_index in [MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN] and mb.pressed and area.has_point(mb.position):
			_set_scroll(_scroll + (-48.0 if mb.button_index == MOUSE_BUTTON_WHEEL_UP else 48.0))
			return
		if mb.button_index != MOUSE_BUTTON_LEFT:
			return
		if mb.pressed and area.has_point(mb.position):
			_pressing = true
			_dragging = false
			_press = mb.position
			_press_scroll = _scroll
			_last_y = mb.position.y
			_vel = 0.0
		elif not mb.pressed:
			_pressing = false
			_dragging = false
	elif e is InputEventMouseMotion and _pressing:
		var mm := e as InputEventMouseMotion
		if not _dragging and absf(mm.position.y - _press.y) > 8.0 * maxf(1.0, s):
			_dragging = true
			for b in _page_view.buttons():
				if b._down:
					b._down = false
					b._squash(1.0)
		if _dragging:
			_set_scroll(_press_scroll - (mm.position.y - _press.y) / s)
			var dt := maxf(0.001, get_process_delta_time())
			_vel = lerpf(_vel, -(mm.position.y - _last_y) / s / dt, 0.4)
			_last_y = mm.position.y


## Liegt kein anderes Fenster über dem Shop?
func _on_top() -> bool:
	if is_instance_valid(menu._modal) or is_instance_valid(menu._success):
		return false
	for b in menu._boards:
		if is_instance_valid(b) and not b.is_queued_for_deletion():
			return false
	return true


# --- Werte eintragen ------------------------------------------------------------------

func bind() -> void:
	var daily := Save.shop_daily()
	var free_offer := not bool(daily["bought"][0])
	var chest := Save.daily_ready("shop_chest_date")
	var chests_free := chest or Save.daily_ready("shop_silver_date")
	var gold := Save.daily_ready("shop_free_date") or Save.daily_ready("shop_gold_date")
	for pair in [["ANGEBOTE", free_offer], ["TRUHEN", chests_free], ["AUFLADEN", gold]]:
		var tab := _tab_button(pair[0])
		if tab:
			tab.badge = bool(pair[1])
	var v := _page_view
	if not is_instance_valid(v):
		return
	match page:
		"angebote":
			v.set_text("23 Std. 59 Min.", until_tomorrow())
			v.set_text("Neu in 23 Std. 59 Min.", "Neu in " + until_tomorrow())
			# Im Mockup vom Preisband verdeckt (Texte zeichnet das Spiel sonst obenauf)
			v.hide_text("×50")
			v.hide_text("×5")
			var names := ["DUSTY JO", "ISKA", "KÄPT'N MARGOT"]
			var prices := ["GRATIS", "40", "120"]
			for k in 3:
				var id := str(daily["heroes"][k])
				var bought := bool(daily["bought"][k])
				var offer: Dictionary = MetaData.DAILY_OFFERS[k]
				v.set_text(names[k], String(GameData.HEROES[id]["name"]).to_upper())
				var price := "GRATIS" if int(offer["gems"]) == 0 else num(int(offer["gems"]))
				v.set_text(prices[k], "GEKAUFT" if bought else price)
				_pdim(v, "#tages%d" % k, bought or Save.gems() < int(offer["gems"]))
				if k < _cards.size():
					var card: DailyCard = _cards[k][0]
					card.setup(id, int(offer["cards"]), bought)
					(_cards[k][1] as DailyBar).setup(id)
			v.hide_text("1× AM TAG", bought_all(daily))
			_pdim(v, "#neu-mischen", bool(daily.get("mixed", false)))
		"truhen":
			v.set_text("Bis zu 10 Karten", "Bis zu %d Karten" % MetaData.free_chest_max(Save.max_level()))
			v.set_text("×25 Karten", "×%d Karten" % MetaData.chest_cards(Save.max_level()))
			v.set_text("100", num(MetaData.SHOP_CHEST_COST))
			v.set_text(_ptext(v, "GRATIS", 0), "GRATIS" if chest else "MORGEN")
			_pdim(v, "#gratis-truhe", not chest)
			_pdim(v, "#truhe", Save.gems() < MetaData.SHOP_CHEST_COST)
			var silver := Save.daily_ready("shop_silver_date")
			v.set_text(_ptext(v, "GRATIS", 1), "GRATIS" if silver else "MORGEN")
			_pdim(v, "#silbertruhe", not silver)
			v.set_text("150", num(MetaData.GOLD_CHEST_COST))
			_pdim(v, "#goldtruhe", Save.gems() < MetaData.GOLD_CHEST_COST)
			v.set_text("Bis zu 6 Booster-Teile", "Bis zu %d Booster-Teile" % MetaData.SILVER_CHEST_PARTS[1])
			v.set_text("Bis zu 30 Booster-Teile", "Bis zu %d Booster-Teile" % MetaData.GOLD_CHEST_PARTS[1])
		"aufladen":
			v.set_text("Sofort wieder voll: 30/30", "Sofort wieder voll: %d/%d" % [Save.energy_max(), Save.energy_max()])
			v.set_text("20", str(MetaData.SHOP_ENERGY_COST))
			_pdim(v, "#energie", Save.gems() < MetaData.SHOP_ENERGY_COST or Save.energy() >= Save.energy_max())
			var shown := [["100", "0,99 €"], ["320", "2,99 €"], ["550", "4,99 €"], ["1.200", "9,99 €"], ["2.600", "19,99 €"], ["5.500", "39,99 €"]]
			for k in mini(shown.size(), MetaData.GEM_PACKS.size()):
				var pack: Dictionary = MetaData.GEM_PACKS[k]
				v.set_text(shown[k][0], num(int(pack["gems"])))
				v.set_text(shown[k][1], str(pack["price"]))
			var gold_amount := ["200", "500", "1.000", "5.000", "15.000", "40.000"]
			var gold_price := ["", "", "60", "250", "650", "1.500"]
			var free_k := 0
			for k in MetaData.GOLD_PACKS.size():
				var gp: Dictionary = MetaData.GOLD_PACKS[k]
				v.set_text(gold_amount[k], num(int(gp["gold"])))
				if gp.has("daily"):
					var ready := Save.daily_ready(str(gp["daily"]))
					v.set_text(_ptext(v, "GRATIS", free_k), "GRATIS" if ready else "MORGEN")
					free_k += 1
					_pdim(v, "#gold%d" % k, not ready)
				else:
					v.set_text(gold_price[k], num(int(gp["gems"])))
					_pdim(v, "#gold%d" % k, Save.gems() < int(gp["gems"]))


static func bought_all(daily: Dictionary) -> bool:
	return bool(daily["bought"][0])


func handle(b: Dictionary) -> bool:
	var href := str(b.get("href", ""))
	var on := str(b.get("on", ""))
	var label := str(b.get("label", ""))
	var words := _words(b)
	# Reiter des Shops
	if words == "TRUHEN":
		show_page("truhen")
		return true
	match href:
		"#angebote", "#shop":
			show_page("angebote")
			return true
		"#aufladen":
			show_page("aufladen")
			return true
		"#event":
			show_page("event")
			return true
		"#truhe":
			_buy_chest()
			return true
		"#gratis-truhe":
			_free_chest()
			return true
		"#silbertruhe":
			_silver_chest()
			return true
		"#goldtruhe":
			_gold_chest()
			return true
		"#energie":
			_buy_energy()
			return true
		"#neu-mischen":
			_mix_daily()
			return true
		"#tages0", "#tages1", "#tages2":
			_buy_daily(int(href.right(1)))
			return true
		"#tempo0", "#tempo1", "#tempo2":
			menu.info("2× Tempo", TEMPO_HINT)
			return true
		"#prime", "#talentsterne", "#werbefrei", "#werbefrei-plus", \
		"#paket0", "#paket1", "#paket2", "#paket3", "#paket4", "#paket5":
			_real_money()
			return true
		"Angebot-Lynx.dc.html", "Kartenpaket.dc.html":
			# Eigenes Fenster zum Angebot, sobald es gebaut ist; sonst nur der Hinweis
			if not ResourceLoader.exists("res://scripts/ui/screens/board_%s.gd" % href.trim_suffix(".dc.html").to_lower()):
				_real_money()
				return true
			return false
	if href.begins_with("#gold"):
		_buy_gold(int(href.right(1)))
		return true
	if on in ["sonder", "talent"]:
		_real_money()
		return true
	match label:
		"Gold kaufen", "Edelsteine kaufen":
			show_page("aufladen")
			return true
	return false


# --- Käufe ---------------------------------------------------------------------------------

func _missing_gems(cost: int) -> void:
	menu.toast("Dir fehlen noch %d Edelsteine" % (cost - Save.gems()))


func _buy_chest() -> void:
	var cost := MetaData.SHOP_CHEST_COST
	var cards := MetaData.chest_cards(Save.max_level())
	if not Save.spend("gems", cost):
		_missing_gems(cost)
		return
	Save.add_squad_cards(cards)   # nur Helden der Aufstellung
	Sfx.play("win")
	menu.reward_success([{"type": "cards", "amount": cards}], "Heldentruhe")
	refresh()


func _silver_chest() -> void:
	if not Save.daily_ready("shop_silver_date"):
		menu.toast("Heute schon geöffnet. Morgen wartet die nächste Silbertruhe!")
		return
	Save.mark_daily("shop_silver_date")
	_got_parts(randi_range(MetaData.SILVER_CHEST_PARTS[0], MetaData.SILVER_CHEST_PARTS[1]))


func _gold_chest() -> void:
	if not Save.spend("gems", MetaData.GOLD_CHEST_COST):
		_missing_gems(MetaData.GOLD_CHEST_COST)
		return
	_got_parts(randi_range(MetaData.GOLD_CHEST_PARTS[0], MetaData.GOLD_CHEST_PARTS[1]))


func _got_parts(n: int) -> void:
	Save.add_booster_parts(n)
	Sfx.play("win")
	menu.celebrate("check", "+%d Booster-Teile" % n, Color(1.0, 0.65, 0.25))
	refresh()


func _free_chest() -> void:
	if not Save.daily_ready("shop_chest_date"):
		menu.toast("Heute schon geöffnet. Morgen wartet die nächste Truhe!")
		return
	var top := MetaData.free_chest_max(Save.max_level())
	var cards := randi_range(ceili(top * 0.5), top)
	Save.mark_daily("shop_chest_date")
	Save.add("cards", cards)
	Sfx.play("win")
	menu.reward_success([{"type": "cards", "amount": cards}], "Gratis-Truhe")
	refresh()


func _buy_gold(k: int) -> void:
	if k < 0 or k >= MetaData.GOLD_PACKS.size():
		return
	var gp: Dictionary = MetaData.GOLD_PACKS[k]
	var amount := int(gp["gold"])
	if gp.has("daily"):
		if not Save.daily_ready(str(gp["daily"])):
			menu.toast("Heute schon abgeholt. Morgen gibt es wieder Gold!")
			return
		Save.mark_daily(str(gp["daily"]))
	elif not Save.spend("gems", int(gp["gems"])):
		_missing_gems(int(gp["gems"]))
		return
	Save.add("gold", amount)
	Sfx.play("ding")
	menu.reward_success([{"type": "gold", "amount": amount}], "Gold-Shop")
	refresh()


func _buy_daily(k: int) -> void:
	var daily := Save.shop_daily()
	if bool(daily["bought"][k]):
		menu.toast("Schon geholt. Morgen gibt es neue Angebote!")
		return
	var cost := int(MetaData.DAILY_OFFERS[k]["gems"])
	if Save.gems() < cost:
		_missing_gems(cost)
		return
	var got := Save.shop_daily_buy(k)
	if got.is_empty():
		return
	Sfx.play("win")
	menu.reward_success([{"type": "hero", "hero": got["hero"], "amount": got["amount"]}], "Tägliches Angebot")
	refresh()


func _mix_daily() -> void:
	if not Save.shop_daily_mix():
		menu.toast("Heute schon neu gemischt. Morgen gibt es neue Angebote!")
		return
	Sfx.play("click")
	refresh()


func _buy_energy() -> void:
	if Save.energy() >= Save.energy_max():
		menu.toast("Deine Energie ist schon voll")
		return
	if not Save.spend("gems", MetaData.SHOP_ENERGY_COST):
		_missing_gems(MetaData.SHOP_ENERGY_COST)
		return
	var refill := Save.energy_max() - Save.energy()
	Save.data["energy"] = Save.energy_max()
	Save.save_game()
	menu.reward_success([{"type": "energy", "amount": refill}], "Energie aufgefüllt")
	refresh()


func _real_money() -> void:
	menu.info("Noch nicht verfügbar", PLAY_STORE)


# --- Hilfen --------------------------------------------------------------------------------

## Text eines Knopfs (alle Wörter, z. B. „TRUHEN“)
func _words(b: Dictionary) -> String:
	var out := PackedStringArray()
	for t in texts_of_button(int(b["i"])):
		out.append(str(t["text"]))
	return " ".join(out)


func _tab_button(word: String) -> MockButton:
	for b in buttons():
		if _words(b.info) == word:
			return b
	return null


## Knopf auf der Seite blasser zeigen, wenn er gerade nichts bewirkt
func _pdim(v: MockView, key: String, off: bool) -> void:
	var b := v.button(key)
	if b:
		b.modulate.a = 0.55 if off else 1.0


## Nummer des n-ten Texts mit diesem Wortlaut auf der Seite (0 = erster)
func _ptext(v: MockView, original: String, n: int) -> int:
	var k := 0
	for t in v.data.get("texts", []):
		if str(t["text"]) == original:
			if k == n:
				return int(t["i"])
			k += 1
	return -1


## Zeit bis Mitternacht („23 Std. 59 Min.“)
static func until_tomorrow() -> String:
	var t := Time.get_time_dict_from_system()
	var left := 86400 - (int(t["hour"]) * 3600 + int(t["minute"]) * 60 + int(t["second"]))
	return "%d Std. %d Min." % [left / 3600, (left % 3600) / 60]


## Heldenkarte im Tagesangebot (wie im Mockup): Bild des Helden, unten „×5“; gekauft: blasser mit Haken
class DailyCard:
	extends Control
	var hero := ""
	var amount := 0
	var bought := false
	var _tex: Texture2D

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE

	func setup(id: String, n: int, done: bool) -> void:
		if id != hero:
			var path := "res://ui/avatars/%s.png" % id
			_tex = load(path) if ResourceLoader.exists(path) else null
		hero = id
		amount = n
		bought = done
		queue_redraw()

	func _draw() -> void:
		var k := size.x / 62.0   # Rand des Live-Rechtecks: 2 Punkte je Seite um die 58 × 74 der Karte
		var r := Rect2(Vector2(2, 2) * k, Vector2(58, 74) * k)
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color("#3a64d8")
		sb.border_color = Color("#ffe27a")
		sb.set_border_width_all(maxi(1, roundi(2 * k)))
		sb.set_corner_radius_all(roundi(8 * k))
		sb.shadow_color = Color(0, 0, 0, 0.45)
		sb.shadow_size = roundi(4 * k)
		sb.shadow_offset = Vector2(0, 3) * k
		draw_style_box(sb, r)
		var inner := r.grow(-2 * k)
		if _tex:
			# Gesicht oben in der Karte, etwas größer als die Karte (wie im Mockup)
			var ts := _tex.get_size()
			var side := minf(ts.x, ts.y) * 0.78
			var src := Rect2((ts.x - side) * 0.5, 0, side, side * inner.size.y / inner.size.x)
			if src.end.y > ts.y:
				src.size.y = ts.y
			draw_texture_rect_region(_tex, inner, src, Color(1, 1, 1, 0.55 if bought else 1.0))
		var strip := Rect2(inner.position.x, inner.end.y - 18 * k, inner.size.x, 18 * k)
		draw_rect(strip, Color(20 / 255.0, 10 / 255.0, 60 / 255.0, 0.8))
		var f := MockFonts.font("Fredoka", 700)
		var fs := roundi(13 * k)
		var txt := "×%d" % amount
		var tw := f.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		draw_string(f, Vector2(strip.get_center().x - tw * 0.5, strip.get_center().y + fs * 0.36), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color.WHITE)
		if bought:
			var c := inner.get_center() - Vector2(0, 6 * k)
			draw_circle(c, 14 * k, Color("#78e65b"))
			draw_polyline(PackedVector2Array([c + Vector2(-6, 0) * k, c + Vector2(-2, 4.5) * k, c + Vector2(6.5, -4.5) * k]), Color("#14320e"), 3 * k, true)


## Fortschrittsbalken unter der Heldenkarte: Karten des Helden bis zur nächsten Stufe
class DailyBar:
	extends Control
	var have := 0
	var need := 1

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE

	func setup(id: String) -> void:
		have = Save.hero_cards(id)
		need = MetaData.hero_cards_needed(Save.hero_level(id))
		queue_redraw()

	func _draw() -> void:
		var k := size.x / 94.0
		var r := Rect2(Vector2(1, 1) * k, Vector2(92, 12) * k)
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color(10 / 255.0, 6 / 255.0, 40 / 255.0, 0.6)
		sb.border_color = Color(1, 1, 1, 0.35)
		sb.set_border_width_all(maxi(1, roundi(1.5 * k)))
		sb.set_corner_radius_all(roundi(6 * k))
		draw_style_box(sb, r)
		var frac := clampf(float(have) / float(maxi(1, need)), 0.0, 1.0)
		if frac > 0.0:
			var fill := StyleBoxFlat.new()
			fill.bg_color = Color("#5fd83f")
			fill.set_corner_radius_all(roundi(5 * k))
			draw_style_box(fill, Rect2(r.position + Vector2(1.5, 1.5) * k, Vector2((r.size.x - 3 * k) * frac, r.size.y - 3 * k)))
		var f := MockFonts.font("Nunito", 800)
		var fs := roundi(8.5 * k)
		var txt := "%d/%d" % [have, need]
		var tw := f.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		draw_string(f, Vector2(r.get_center().x - tw * 0.5, r.get_center().y + fs * 0.36), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color.WHITE)
