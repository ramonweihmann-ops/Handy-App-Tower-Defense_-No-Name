class_name CardRules
## Neues Kartensystem im Kampf (Vorschlag vom 14.11.2026, noch im Balance-Labor): nur mit dem Schalter
## --karten-neu aktiv, einzelne Teile mit --karten-neu=held5,plaetze,meister,symbiose.
## - held5: Karten für neue Champions erst ab der Karte nach Welle 5
## - plaetze: höchstens 3 Waffenfähigkeiten je Champion (die Superfähigkeit zum Antippen zählt extra)
## - meister: Waffenfähigkeiten haben höchstens Stufe 3; auf Stufe 3 werden sie zur Meisterfähigkeit
## - symbiose: zwei Champions mit ihren Spezialfähigkeiten ergeben zusammen eine neue Wirkung

const PARTS := ["held5", "plaetze", "meister", "symbiose"]
## ab dieser Welle (Karte danach) können neue Champions kommen
const HERO_FROM_WAVE := 5
const WEAPON_MODS := ["damage", "rate", "reload", "mag", "crit", "special"]
const SLOTS := 3
const MEISTER_LEVEL := 3

static var on := {}


static func has(part: String) -> bool:
	return on.has(part)


static func enable(spec: String) -> void:
	on.clear()
	for p in (PARTS if spec == "" else Array(spec.split(","))):
		on[str(p)] = true


## Zusatz der Meisterfähigkeit je Waffenfähigkeit (Spezialfähigkeit: wirkt wie zwei Stufen mehr)
const MEISTER := {
	"damage": ["Wuchttreffer", "Jeder 4. Schuss macht dreifachen Schaden."],
	"rate": ["Doppelschuss", "Jeder 3. Schuss trifft zusätzlich einen zweiten Gegner."],
	"reload": ["Blitzladen", "30 % Chance, sofort fertig nachgeladen zu haben."],
	"mag": ["Sparmagazin", "25 % Chance, dass ein Schuss keine Munition verbraucht."],
	"crit": ["Volltreffer", "Kritische Treffer machen dreifachen statt doppelten Schaden."],
	"special": ["Meister", "Die Spezialfähigkeit wirkt, als hätte sie zwei Stufen mehr."],
}

## Symbiosen: zwei Waffenfamilien, beide Spezialfähigkeiten mindestens Stufe 1
const SYMBIOSES := {
	"kettenexplosion": {"a": "tesla", "b": "rocket", "title": "Explosiver Kettenblitz",
		"desc": "Voltas Kettenblitz lässt jeden getroffenen Gegner mit Brockens Sprengkraft explodieren."},
	"frostblitz": {"a": "tesla", "b": "cryo", "title": "Frostblitz",
		"desc": "Voltas Blitz trägt Kalles Frost: Getroffene Gegner werden langsamer."},
	"brandschrot": {"a": "shotgun", "b": "flamer", "title": "Brandschrot",
		"desc": "Margots Schrot brennt wie Fritzis Flammen: Getroffene Gegner brennen."},
	"schwerkraftbombe": {"a": "rocket", "b": "gravity", "title": "Schwerkraftbombe",
		"desc": "Brockens Raketen ziehen die Gegner am Einschlag zusammen wie Novas Schwerkraftfeld."},
	"durchschlagsalve": {"a": "mg", "b": "sniper", "title": "Durchschlag-Salve",
		"desc": "Iskas und Lynx' Kugeln durchschlagen je einen Gegner mehr."},
	"reparaturwucht": {"a": "drone", "b": "cannon", "title": "Reparaturwucht",
		"desc": "Jeder Wuchtschuss von Rollo flickt mit Pips Werkzeug das Schild ein wenig."},
	"sternenfeuer": {"a": "beam", "b": "flamer", "title": "Sternenfeuer",
		"desc": "Fünkchens Sternenatem setzt Gegner in Brand wie Fritzis Flammen."},
}
