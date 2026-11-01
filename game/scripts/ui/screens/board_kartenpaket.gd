extends OfferBoard
## Kartentruhe (Mockup „Kartenpaket“): Angebot des Tages, läuft bis Mitternacht.


func _init(m: MainMenu) -> void:
	super("kartenpaket", m)
	timer_text = "Nur heute · 8 Std. 40 Min."
	timer_prefix = "Nur heute · "
