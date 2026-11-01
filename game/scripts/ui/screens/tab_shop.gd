extends MockScreen
## Shop (Mockup „Shop“, Main-c4lv): Prime-Karte, Champion-Angebot, Sonderangebote,
## Talentstern-Angebot und die Reiter Angebote · Truhen · Aufladen · Event.
## Das Mockup zeigt nur „Angebote“; die anderen Reiter sind beim Export aus denselben Bausteinen
## gebaut (tools/mock2game/cfg/shop.js) und hier mit der echten Spiellogik verbunden:
## Heldentruhe für Edelsteine, Gratis-Gold einmal am Tag, Energie auffüllen.
## Echtgeld-Angebote zeigen einen Hinweis, bis die App im Play Store ist.

const PAGES := ["angebote", "truhen", "aufladen", "event"]
const GIFT_GOLD := 100
const PLAY_STORE := "Echte Käufe kommen, wenn die App im Play Store ist. In der Testphase gibt es Edelsteine über den Battle Pass, das Glücksrad und die tägliche Belohnung."

var page := "angebote"
var _chest: TextureRect
var _t := 0.0


func _init(m: MainMenu) -> void:
	super("shop", m, {"level": "12", "energy": "25/30", "gold": "4.573", "gems": "350"})
	state = page


func _ready() -> void:
	super()
	_place_chest()


func _process(delta: float) -> void:
	super(delta)
	_t += delta
	# Die Truhe wippt leicht, als wollte sie gleich aufspringen
	if is_instance_valid(_chest):
		_chest.rotation = sin(_t * 1.7) * 0.05
		_chest.scale = Vector2.ONE * (1.0 + 0.035 * sin(_t * 3.1))


## Einen der vier Reiter zeigen
func show_page(name: String) -> void:
	if not name in PAGES:
		return
	page = name
	# Texte haben je Zustand eigene Nummern: Ersetzungen gelten nur für den bisherigen Zustand
	_overrides.clear()
	_hidden.clear()
	show_state(name)
	_place_chest()
	refresh()


func _place_chest() -> void:
	if is_instance_valid(_chest):
		# aus der Liste der platzierten Elemente nehmen, sonst stolpert _layout() darüber
		for id in _placed.keys():
			if _placed[id] == _chest:
				_placed.erase(id)
		_chest.queue_free()
	_chest = live_image("chest", true)


func bind() -> void:
	var gift := Save.daily_ready("shop_free_date")
	var tab := _tab_button("TRUHEN")
	if tab:
		tab.badge = gift
	match page:
		"angebote":
			set_text("23 Std. 59 Min.", until_tomorrow())
			# Im Mockup vom Preisband verdeckt (Texte zeichnet das Spiel sonst obenauf)
			hide_text("×50")
			hide_text("×5")
		"truhen":
			set_text("×25", "×%d" % MetaData.chest_cards(Save.max_level()))
			set_text("100", str(MetaData.SHOP_CHEST_COST))
			_dim("#truhe", Save.gems() < MetaData.SHOP_CHEST_COST)
			set_text("×100", "×%d" % GIFT_GOLD)
			set_text("ABHOLEN", "ABHOLEN" if gift else "MORGEN")
			_dim("#geschenk", not gift)
		"aufladen":
			set_text("Sofort wieder voll: 30/30", "Sofort wieder voll: %d/%d" % [MetaData.ENERGY_MAX, MetaData.ENERGY_MAX])
			set_text("20", str(MetaData.SHOP_ENERGY_COST))
			# „25/30“ steht zweimal da: oben in der Kopfleiste und auf der Energie-Karte
			var card := _nth_text("25/30", 1)
			if card >= 0:
				set_text(card, "%d/%d" % [Save.energy(), MetaData.ENERGY_MAX])
			_dim("#energie", Save.gems() < MetaData.SHOP_ENERGY_COST or Save.energy() >= MetaData.ENERGY_MAX)
			var shown := [["×80", "1,99 €"], ["×500", "9,99 €"], ["×1.200", "19,99 €"]]
			for k in mini(shown.size(), MetaData.GEM_PACKS.size()):
				var pack: Dictionary = MetaData.GEM_PACKS[k]
				set_text(shown[k][0], "×" + num(int(pack["gems"])))
				set_text(shown[k][1], str(pack["price"]))


func refresh_top() -> void:
	super()
	if page == "aufladen":
		var card := _nth_text("25/30", 1)
		if card >= 0:
			set_text(card, "%d/%d" % [Save.energy(), MetaData.ENERGY_MAX])


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
		"#geschenk":
			_claim_gift()
			return true
		"#energie":
			_buy_energy()
			return true
		"#prime", "#paket0", "#paket1", "#paket2":
			_real_money()
			return true
		"Angebot-Lynx.dc.html", "Kartenpaket.dc.html":
			# Eigenes Fenster zum Angebot, sobald es gebaut ist; sonst nur der Hinweis
			if not ResourceLoader.exists("res://scripts/ui/screens/board_%s.gd" % href.trim_suffix(".dc.html").to_lower()):
				_real_money()
				return true
			return false
	if on in ["sonder", "talent"]:
		_real_money()
		return true
	match label:
		"Gold kaufen":
			show_page("truhen")
			return true
		"Edelsteine kaufen":
			show_page("aufladen")
			return true
	return false


# --- Käufe ---------------------------------------------------------------------------------

func _buy_chest() -> void:
	var cost := MetaData.SHOP_CHEST_COST
	var cards := MetaData.chest_cards(Save.max_level())
	if not Save.spend("gems", cost):
		menu.toast("Dir fehlen noch %d Edelsteine" % (cost - Save.gems()))
		return
	Save.add("cards", cards)
	Sfx.play("win")
	menu.celebrate("cards", "+%d Heldenkarten" % cards)
	menu.info("Heldentruhe", "%d Heldenkarten erhalten. Schau in der Sammlung nach, wer aufsteigen kann!" % cards)
	refresh()


func _claim_gift() -> void:
	if not Save.daily_ready("shop_free_date"):
		menu.toast("Heute schon abgeholt. Morgen gibt es wieder Gold!")
		return
	Save.add("gold", GIFT_GOLD)
	Save.mark_daily("shop_free_date")
	menu.celebrate("gold", "+%d Gold" % GIFT_GOLD)
	refresh()


func _buy_energy() -> void:
	if Save.energy() >= MetaData.ENERGY_MAX:
		menu.toast("Deine Energie ist schon voll")
		return
	if not Save.spend("gems", MetaData.SHOP_ENERGY_COST):
		menu.toast("Dir fehlen noch %d Edelsteine" % (MetaData.SHOP_ENERGY_COST - Save.gems()))
		return
	Save.data["energy"] = MetaData.ENERGY_MAX
	Save.save_game()
	menu.celebrate("energy", "Energie aufgefüllt!", Color(0.5, 1.0, 0.5))
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


## Knopf blasser zeigen, wenn er gerade nichts bewirkt
func _dim(key: String, off: bool) -> void:
	var b := button(key)
	if b:
		b.modulate.a = 0.55 if off else 1.0


## Nummer des n-ten Texts mit diesem Wortlaut (0 = erster)
func _nth_text(original: String, n: int) -> int:
	var k := 0
	for t in data.get("texts", []):
		if str(t["text"]) == original:
			if k == n:
				return int(t["i"])
			k += 1
	return -1


## Zeit bis Mitternacht, wie im Mockup („23 Std. 59 Min.“)
static func until_tomorrow() -> String:
	var t := Time.get_time_dict_from_system()
	var left := 86400 - (int(t["hour"]) * 3600 + int(t["minute"]) * 60 + int(t["second"]))
	return "%d Std. %d Min." % [left / 3600, (left % 3600) / 60]
