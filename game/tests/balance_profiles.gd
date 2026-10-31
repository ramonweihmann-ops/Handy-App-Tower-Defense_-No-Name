extends RefCounted
## Spielerprofile für das Balance-Labor: So weit ist ein Spieler typischerweise, wenn er ein
## Level zum ersten Mal spielt. Die Zahlen sind Annahmen und werden mit echten Testdaten
## nachgeschärft (docs/BALANCE.md).
##
##   anfaenger    – spielt ohne Käufe, wertet wenig auf
##   durchschnitt – spielt ohne Käufe, wertet nach jedem Level auf, was das Gold hergibt
##   zahlend      – wie durchschnitt, dazu gekaufte Helden (alle frei), +2 Heldenstufen, Booster +1,
##                  Prime (4 statt 3 Karten bei der Kartenwahl)

const PROFILES := ["anfaenger", "durchschnitt", "zahlend"]


static func apply(save: Node, profile: String, level: int) -> void:
	var done := level - 1
	var d: Dictionary = save.data
	var won: Array = []
	for n in range(1, level):
		won.append("N" + str(n))
	d["won_levels"] = won
	d["max_level"] = level
	var hero_lvl := 1
	var tech := 0
	var ammo := {}
	var talents := 0
	var booster_lvl := 1
	match profile:
		"anfaenger":
			hero_lvl = 1 + done / 4
			tech = done / 2
			ammo = {"rate": done / 4, "cap": done / 4, "start": done / 5, "lever": done / 8}
		_:
			hero_lvl = 1 + int(done / 2.5)
			tech = int(done * 0.8)
			ammo = {"rate": done / 3, "cap": done / 3, "start": done / 4, "lever": done / 5,
				"count": done / 8, "gate": done / 10}
			talents = done / 3
			booster_lvl = 1 + done / 5
	if profile == "zahlend":
		hero_lvl += 2
		booster_lvl += 1
		d["unlocked"] = GameData.HERO_IDS.duplicate()
		d["prime"] = true
	for id in GameData.HERO_IDS:
		d["heroes"][id]["level"] = clampi(hero_lvl, 1, MetaData.HERO_MAX_LEVEL)
	d["tech"] = clampi(tech, 0, MetaData.TECH.size())
	var ups := {}
	for u in MetaData.AMMO_UPGRADES:
		ups[u["id"]] = clampi(int(ammo.get(u["id"], 0)), 0, int(u["max"]))
	d["ammo_up"] = ups
	# Talente reihum verteilen (fest statt zufällig, damit Läufe vergleichbar bleiben)
	var tal := {}
	var keys: Array = MetaData.TALENTS.keys()
	for i in talents:
		var k: String = keys[i % keys.size()]
		tal[k] = mini(int(tal.get(k, 0)) + 1, MetaData.TALENT_MAX)
	d["talents"] = tal
	var bl := {}
	for id in MetaData.BOOSTERS:
		bl[id] = clampi(booster_lvl, 1, MetaData.BOOSTER_MAX)
	d["boosters"] = bl
	d["squad"] = []
