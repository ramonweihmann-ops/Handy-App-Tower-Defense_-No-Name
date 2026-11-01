class_name AmmoStore
extends RefCounted
## Gemeinsamer Plasmavorrat: Der Plasma-Erzeuger füllt ihn, die Helden laden daraus nach.

signal changed

## Reihenfolge beim Entnehmen: Spezialmunition zuerst, damit sie nicht liegen bleibt.
const TAKE_ORDER := ["fire", "ice", "normal"]

var cap := 60
var counts := {"normal": 0, "fire": 0, "ice": 0}


func reset(new_cap: int, start: int) -> void:
	cap = new_cap
	counts = {"normal": start, "fire": 0, "ice": 0}
	changed.emit()


func total() -> int:
	return int(counts["normal"]) + int(counts["fire"]) + int(counts["ice"])


## Legt Kugeln ab. Gibt zurück, wie viele Platz hatten.
func add(type: String, n: int = 1) -> int:
	var space := cap - total()
	var added := mini(space, n)
	if added <= 0:
		return 0
	counts[type] = int(counts[type]) + added
	changed.emit()
	return added


## Entnimmt genau n Kugeln. Reicht der Vorrat nicht, wird nichts entnommen.
func take(n: int) -> Array[String]:
	var out: Array[String] = []
	if n <= 0 or total() < n:
		return out
	for type in TAKE_ORDER:
		while out.size() < n and int(counts[type]) > 0:
			counts[type] = int(counts[type]) - 1
			out.append(type)
	changed.emit()
	return out


func raise_cap(amount: int) -> void:
	cap += amount
	changed.emit()
