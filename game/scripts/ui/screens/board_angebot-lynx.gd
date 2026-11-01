extends OfferBoard
## Champion-Angebot Lynx (Mockup „Angebot-Lynx“): Angebot läuft bis Mitternacht.


func _init(m: MainMenu) -> void:
	super("angebot_lynx", m)
	timer_text = "22 Std. 04 Min."
