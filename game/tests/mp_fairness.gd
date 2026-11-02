extends SceneTree
## Prüft die Multiplayer-Wertung und die Computergegner (docs/MULTIPLAYER.md):
##   godot --headless --path game --script tests/mp_fairness.gd
##
## 1. Regel: Wer zuerst fällt und am wenigsten besiegt hat, ist immer Letzter. Allgemein: Wer früher
##    fällt und weniger besiegt hat, steht nie vor dem anderen. Geprüft an 50.000 zufälligen Kämpfen.
## 2. Fairness: Echte Testläufe des Spiels (tests/mp_runs.json aus scripts/mp-lab.py) spielen je
##    300-mal gegen neu gewürfelte Computergegner. Ein typischer Spieler (Profil „durchschnitt“) soll
##    im Mittel etwa Platz 2,5 erreichen, ein stärkerer (zahlend) besser, ein schwächerer schlechter.
## 3. Die Computergegner sollen so viele Gegner besiegen und so oft durchhalten wie echte Läufe.
## Ausgabe „MPCHECK ok“ oder „MPCHECK FEHLER …“; bei Fehlern Rückgabewert 1.

var failed := false


func _initialize() -> void:
	_rule_check()
	_fairness_check()
	print("MPCHECK ", "FEHLER" if failed else "ok")
	quit(1 if failed else 0)


func _fail(msg: String) -> void:
	failed = true
	print("MPCHECK FEHLER: ", msg)


func _rule_check() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 42
	var bad_last := 0
	var bad_pair := 0
	var cases := 0
	for n in 50000:
		var es: Array = []
		for i in 4:
			var out := rng.randf() < 0.6
			var secs := float(rng.randi_range(30, 299)) if out else MpData.MATCH_TIME
			var kills := rng.randi_range(0, 400)
			var bosses := 1 if kills > 0 and rng.randf() < 0.4 else 0
			es.append({"name": str(i), "kills": kills, "bosses": bosses, "secs": secs})
		var ranked := MpData.rank(es)
		# Paare: früher gefallen und weniger besiegt → nie davor
		for a in ranked:
			for b in ranked:
				if float(a["secs"]) < float(b["secs"]) and int(a["kills"]) < int(b["kills"]) and int(a["place"]) < int(b["place"]):
					bad_pair += 1
		# Erster, der fällt, mit den wenigsten besiegten Gegnern → Letzter
		var first: Dictionary = {}
		for e in ranked:
			if float(e["secs"]) < MpData.MATCH_TIME and (first.is_empty() or float(e["secs"]) < float(first["secs"])):
				first = e
		if first.is_empty():
			continue
		var unique := true
		var fewest := true
		for e in ranked:
			if e == first:
				continue
			if float(e["secs"]) <= float(first["secs"]):
				unique = false
			if int(e["kills"]) <= int(first["kills"]):
				fewest = false
		if unique and fewest:
			cases += 1
			if int(first["place"]) != 4:
				bad_last += 1
	print("MPCHECK Regel: %d Kämpfe mit „zuerst gefallen und am wenigsten besiegt“, davon nicht Letzter: %d; verletzte Paare: %d" % [cases, bad_last, bad_pair])
	if bad_last > 0 or bad_pair > 0:
		_fail("Rangregel verletzt")


func _fairness_check() -> void:
	var path := "res://tests/mp_runs.json"
	if not FileAccess.file_exists(path):
		print("MPCHECK Fairness: keine Testläufe (scripts/mp-lab.py), übersprungen")
		return
	var runs: Array = JSON.parse_string(FileAccess.get_file_as_string(path))
	var by_profile := {}
	var bot_kills := 0.0
	var bot_full := 0.0
	var bot_n := 0
	for r in runs:
		var prof := str(r["profile"])
		if not by_profile.has(prof):
			by_profile[prof] = {"places": [0, 0, 0, 0], "n": 0, "kills": 0.0, "full": 0.0, "runs": 0}
		var bp: Dictionary = by_profile[prof]
		bp["kills"] = float(bp["kills"]) + float(r["kills"])
		bp["full"] = float(bp["full"]) + (0.0 if r["out"] else 1.0)
		bp["runs"] = int(bp["runs"]) + 1
		for k in 300:
			var m := MpMatch.new(int(r["level"]), 0, k * 7919 + int(r["seed"]) * 31 + int(r["level"]))
			var player := {"name": "DU", "hero": "dusty", "kills": int(r["kills"]), "bosses": int(r["bosses"]),
				"secs": float(r["secs"]), "out": bool(r["out"]), "me": true}
			for e in m.finish(player):
				if e.get("me", false):
					bp["places"][int(e["place"]) - 1] += 1
				elif prof == "durchschnitt":
					bot_kills += float(e["kills"])
					bot_full += 0.0 if e["out"] else 1.0
					bot_n += 1
			bp["n"] = int(bp["n"]) + 1
	var avg := {}
	for prof in by_profile:
		var bp: Dictionary = by_profile[prof]
		var n := float(bp["n"])
		var pl: Array = bp["places"]
		var mean := (pl[0] * 1.0 + pl[1] * 2.0 + pl[2] * 3.0 + pl[3] * 4.0) / n
		avg[prof] = mean
		print("MPCHECK Fairness %-12s %d Läufe: Platz 1 %.0f %%, 2 %.0f %%, 3 %.0f %%, 4 %.0f %%, Mittel %.2f · echt: %.0f besiegt, hält durch %.0f %%" % [
			prof, int(bp["runs"]), 100.0 * pl[0] / n, 100.0 * pl[1] / n, 100.0 * pl[2] / n, 100.0 * pl[3] / n, mean,
			float(bp["kills"]) / int(bp["runs"]), 100.0 * float(bp["full"]) / int(bp["runs"])])
	if bot_n > 0:
		print("MPCHECK Computergegner (Bronze-Liga): %.0f besiegt, halten durch %.0f %%" % [bot_kills / bot_n, 100.0 * bot_full / bot_n])
	if avg.has("durchschnitt") and (float(avg["durchschnitt"]) < 2.2 or float(avg["durchschnitt"]) > 2.8):
		_fail("typischer Spieler im Mittel auf Platz %.2f (Ziel 2,2–2,8)" % float(avg["durchschnitt"]))
	if avg.has("zahlend") and avg.has("durchschnitt") and float(avg["zahlend"]) >= float(avg["durchschnitt"]):
		_fail("stärkerer Spieler schneidet nicht besser ab")
	if avg.has("anfaenger") and avg.has("durchschnitt") and float(avg["anfaenger"]) <= float(avg["durchschnitt"]):
		_fail("schwächerer Spieler schneidet nicht schlechter ab")
