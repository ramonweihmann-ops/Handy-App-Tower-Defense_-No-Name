class_name OfferBoard
extends MockScreen
## Gemeinsame Grundlage der Angebots-Fenster (Champion-Angebote, Starterpaket, Kartentruhe), die
## vom Hauptbildschirm über die Angebots-Knöpfe links geöffnet werden. Alles wie im Mockup; echte
## Käufe gibt es im Pilot noch nicht, der Preis-Knopf erklärt das. Roter X-Knopf schließt.

## Ursprünglicher Text der Restzeit im Mockup ("" = keine Restzeit)
var timer_text := ""
## Vorsatz vor der Restzeit (z. B. „Nur heute · “)
var timer_prefix := ""
## Länge eines Angebotszeitraums in Stunden (ab Mitternacht gezählt); 24 = endet um Mitternacht
var period_hours := 24


func _init(screen_name: String, m: MainMenu) -> void:
	super(screen_name, m)


func bind() -> void:
	if timer_text != "":
		set_text(timer_text, timer_prefix + time_left())


func refresh_top() -> void:
	super()
	# Restzeit läuft jede Sekunde mit (MockScreen ruft das sekündlich auf)
	if timer_text != "" and data.size() > 0:
		set_text(timer_text, timer_prefix + time_left())


## Restzeit bis zum Ende des aktuellen Angebotszeitraums, z. B. „22 Std. 04 Min.“
func time_left() -> String:
	var t := Time.get_time_dict_from_system()
	var since := int(t["hour"]) * 3600 + int(t["minute"]) * 60 + int(t["second"])
	var span := period_hours * 3600
	var left := span - since % span
	return "%d Std. %02d Min." % [left / 3600, (left % 3600) / 60]


func handle(b: Dictionary) -> bool:
	if str(b.get("label", "")) == "Schließen":
		menu.close_board(self)
		return true
	if str(b.get("href", "")) == "Main.dc.html":
		# Preis-Knopf
		menu.info("Noch nicht verfügbar", "Echte Käufe kommen, wenn die App im Play Store ist. In der Testphase gibt es Edelsteine über den Battle Pass, das Glücksrad und die tägliche Belohnung.")
		return true
	return false
