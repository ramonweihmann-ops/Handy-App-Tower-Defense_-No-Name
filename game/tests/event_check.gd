extends Node
## Prüft die Spiellogik des wöchentlichen Events (MetaData.EVENT_*, Save.event_*):
##   godot --headless --path game -- --eventcheck
## Wochenwechsel am Montag 0 Uhr UTC, Themen reihum, welche Gegner zählen, Punkte und Stufen, Abholen (einmal,
## nur erreichte Stufen), Truhen als Booster-Teile, neuer Stand in einer neuen Woche. Der echte Spielstand bleibt
## unberührt (eigene Daten, Speichern aus). Ausgabe „EVENTCHECK ok“ oder „EVENTCHECK FEHLER …“.

var main: Node
var failed := false


func _ready() -> void:
	var saved_data: Dictionary = Save.data
	var saved_mode: bool = Save.test_mode
	Save.data = Save.default_data()
	_run()
	Save.data = saved_data
	Save.test_mode = saved_mode
	print("EVENTCHECK ", "FEHLER" if failed else "ok")
	get_tree().quit(1 if failed else 0)


func _check(ok: bool, msg: String) -> void:
	if not ok:
		failed = true
		print("EVENTCHECK FEHLER: ", msg)


func _run() -> void:
	# Wochenwechsel: Montag, 23.11.2026, 0 Uhr UTC
	var monday := Time.get_unix_time_from_datetime_dict({"year": 2026, "month": 11, "day": 23, "hour": 0, "minute": 0, "second": 0})
	_check(MetaData.event_week(monday) == MetaData.event_week(monday - 1) + 1, "neue Woche beginnt nicht am Montag um 0 Uhr")
	_check(MetaData.event_week(monday + 6 * 86400 + 86399) == MetaData.event_week(monday), "Woche endet nicht am Sonntag")
	var ids := {}
	for w in MetaData.EVENT_THEMES.size():
		ids[MetaData.event_theme(MetaData.event_week(monday) + w)["id"]] = true
	_check(ids.size() == MetaData.EVENT_THEMES.size(), "Themen wechseln nicht reihum")
	# Welche Gegner zählen
	var t: Array = MetaData.EVENT_THEMES
	_check(MetaData.event_counts(t[0], "schleimling", "leicht", false) and not MetaData.event_counts(t[0], "zombie", "mittel", false), "Schleimflut zählt falsch")
	_check(MetaData.event_counts(t[1], "zombie", "mittel", true) and not MetaData.event_counts(t[1], "zombie", "mittel", false), "Frostwoche zählt falsch")
	_check(MetaData.event_counts(t[2], "koloss", "boss", false) and not MetaData.event_counts(t[2], "schleimling", "leicht", false), "Zombienacht zählt falsch")
	_check(MetaData.event_counts(t[3], "panzerkaefer", "stark", false) and not MetaData.event_counts(t[3], "zombie", "mittel", false), "Lavawoche zählt falsch")
	# Punkte und Stufen (Speichern aus: test_mode, nur für das Gutschreiben kurz ein)
	Save.test_mode = true
	Save.event_add(500)
	_check(Save.event_points() == 0, "im Test werden Punkte gutgeschrieben")
	Save.test_mode = false
	Save.event_add(840)
	Save.test_mode = true
	_check(Save.event_points() == 840 and Save.event_stage() == 3, "840 Punkte ergeben nicht Stufe 3")
	_check(Save.event_state(2) == "ready" and Save.event_state(3) == "lock", "Zustände der Stufen falsch")
	_check(Save.event_ready() == 3, "drei Stufen sollten bereitliegen")
	var gold := Save.gold()
	var r := Save.event_claim(0)
	_check(str(r.get("type", "")) == "gold" and Save.gold() == gold + 300, "Stufe 1 gibt nicht 300 Gold")
	_check(Save.event_state(0) == "done" and Save.event_claim(0).is_empty(), "Stufe 1 lässt sich zweimal holen")
	_check(Save.event_claim(3).is_empty(), "nicht erreichte Stufe lässt sich holen")
	_check(Save.event_ready() == 2, "nach dem Abholen sollten zwei Stufen bereitliegen")
	# Truhe auf Stufe 5: Booster-Teile wie die Silbertruhe im Shop
	Save.test_mode = false
	Save.event_add(410)
	Save.test_mode = true
	var c := Save.event_claim(4)
	_check(str(c.get("type", "")) == "parts" and int(c["amount"]) >= MetaData.SILVER_CHEST_PARTS[0] and int(c["amount"]) <= MetaData.SILVER_CHEST_PARTS[1], "Stufe 5 gibt keine Booster-Teile")
	# Abstimmung (20.11.2026): fünf Runden am Tag reichen nicht ganz für die Truhe, an manchen Tagen zehn schon
	var per_round := int(MetaData.EVENT_POINTS["win"]) + int(MetaData.EVENT_POINTS["foe_cap"]) / 2 + int(MetaData.EVENT_POINTS["boss"]) / 5
	var per_day := 3 * int(MetaData.EVENT_POINTS["mission"])
	var full := MetaData.EVENT_STEP * MetaData.EVENT_REWARDS.size()
	_check(7 * (5 * per_round + per_day) < full, "Truhe schon mit 5 Runden am Tag erreichbar")
	_check(5 * (5 * per_round + per_day) + 2 * (10 * per_round + per_day) >= full * 0.9, "Truhe auch mit 10 Runden an zwei Tagen kaum erreichbar")
	# Höchstens zehn Stufen
	Save.test_mode = false
	Save.event_add(5000)
	Save.test_mode = true
	_check(Save.event_stage() == MetaData.EVENT_REWARDS.size(), "mehr als zehn Stufen")
	# Neue Woche: alles von vorn
	Save.data["event"]["week"] = int(Save.data["event"]["week"]) - 1
	_check(Save.event_points() == 0 and Save.event_ready() == 0, "neue Woche beginnt nicht bei null")
