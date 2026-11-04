extends MockScreen
## Spielmodi (Mockup „Spielmodi · Auswahl“), geöffnet über die Kachel „Modi“ im Hauptbildschirm:
## Multiplayer (4 Kommandanten), Universumsode (kommt bald), Weltraumschlacht (kommt bald).


func _init(m: MainMenu) -> void:
	super("spielmodi", m, {"energy": "25/30", "gold": "4.674"})


func bind() -> void:
	set_text("1.228", MockScreen.num(Save.trophies()))


func handle(b: Dictionary) -> bool:
	var href := str(b.get("href", ""))
	if str(b.get("label", "")) == "Schließen":
		menu.close_board(self)
		return true
	if href == "MP-Gegnersuche.dc.html":
		if Save.energy() < MetaData.ENERGY_COST:
			menu.open_energy()
			return true
		menu.close_board(self)
		menu.open_mp_search()
		return true
	if href == "Main.dc.html" or href == "Universumsode-Preis.dc.html":
		menu.toast("Die Universumsode kommt mit einem der nächsten Updates.")
		return true
	return false
