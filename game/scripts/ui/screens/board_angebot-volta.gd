extends OfferBoard
## Champion-Angebot Volta (Mockup „Angebot-Volta“): Angebot wechselt alle sechs Stunden.


func _init(m: MainMenu) -> void:
	super("angebot_volta", m)
	timer_text = "5 Std. 12 Min."
	period_hours = 6
