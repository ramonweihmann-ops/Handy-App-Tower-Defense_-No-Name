class_name TexCache
extends RefCounted
## Hält die Bilder (und Programmteile) der Hauptreiter geladen, damit ein Reiterwechsel sie nicht jedes Mal neu entpacken
## muss (WebP entpacken kostet auf dem Handy pro Bildschirm leicht 100–300 ms). Godot gibt ein Bild
## frei, sobald es niemand mehr benutzt; solange es hier gehalten wird, liefert load() es sofort.
## Die Bilder werden nach dem Start im Hintergrund vorgeladen (eigene Threads), ohne das Menü zu bremsen.
## Obergrenze für den Grafikspeicher: älteste Bilder fallen heraus, wenn sie überschritten wird.

const BUDGET := 128 * 1024 * 1024

## Reiter, die man ständig wechselt: zuerst geladen (Bildschirm -> Zustand beim Öffnen)
const MAIN_SCREENS := {"home": "main", "helden_neu": "main", "upgrades_tech_neu": "main", "upgrades_talente_neu": "main",
	"basis": "main", "shop": "angebote", "bauplatz": "main", "gebaeude": "lager", "kampf_hud": "main"}
const EXTRA_DIRS := ["res://ui/helden_v2/", "res://ui/upgrades_v2/", "res://ui/icons/"]
const EXTRA_FILES := ["res://ui/base/basis_voll.webp", "res://ui/base/basis_voll_unscharf.webp"]
## Programmteile der Reiter und Fenster: würden sonst bei jedem Öffnen neu übersetzt
const SCRIPT_DIR := "res://scripts/ui/screens/"

static var _held := {}          # Pfad -> Bild oder Skript
static var _order: Array[String] = []
static var _bytes := 0
static var _pending: Array[String] = []
static var _queue: Array[String] = []
const PARALLEL := 2
static var _started := false


## Einmal nach dem Start: alle Bilder der Hauptreiter im Hintergrund laden
static func prefetch_main() -> void:
	if _started:
		return
	_started = true
	var paths: Array[String] = []
	for f in ResourceLoader.list_directory(SCRIPT_DIR):
		if f.ends_with(".gd"):
			paths.append(SCRIPT_DIR + f)
	for sc in MAIN_SCREENS:
		paths.append_array(screen_paths(sc, MAIN_SCREENS[sc]))
	for d in EXTRA_DIRS:
		paths.append_array(_dir_images(d))
	paths.append_array(EXTRA_FILES)
	_queue.append_array(paths)


## Bilder des Grundzustands eines Mockup-Bildschirms (Hintergrund, Knöpfe, Live-Bilder)
static func screen_paths(screen: String, state := "main") -> Array[String]:
	var out: Array[String] = []
	var st: Dictionary = MockView.layout_of(screen).get("states", {}).get(state, {})
	var dir := "res://ui_mock/%s/" % screen
	if str(st.get("bg", "")) != "":
		out.append(dir + str(st["bg"]))
	for b in st.get("buttons", []):
		if str(b.get("img", "")) != "":
			out.append(dir + str(b["img"]))
	for l in st.get("live", []):
		if str(l.get("img", "")) != "":
			out.append(dir + str(l["img"]))
	return out


static func _dir_images(dir: String) -> Array[String]:
	var out: Array[String] = []
	for f in ResourceLoader.list_directory(dir):
		if f.ends_with(".webp") or f.ends_with(".png") or f.ends_with(".svg"):
			out.append(dir + f)
	return out


static func request(path: String) -> void:
	if _held.has(path) or _pending.has(path) or not ResourceLoader.exists(path):
		return
	if ResourceLoader.has_cached(path):
		hold(path, load(path))
		return
	if ResourceLoader.load_threaded_request(path) == OK:
		_pending.append(path)


## Jedes Bild einmal pro Bild abfragen (aus dem Menü); fertige übernehmen
static func poll() -> void:
	while _pending.size() < PARALLEL and not _queue.is_empty():
		request(_queue.pop_front())
	if _pending.is_empty():
		return
	for i in range(_pending.size() - 1, -1, -1):
		var p := _pending[i]
		var st := ResourceLoader.load_threaded_get_status(p)
		if st == ResourceLoader.THREAD_LOAD_LOADED:
			_pending.remove_at(i)
			hold(p, ResourceLoader.load_threaded_get(p))
		elif st != ResourceLoader.THREAD_LOAD_IN_PROGRESS:
			_pending.remove_at(i)


## Ein Bild oder Skript festhalten (oder als zuletzt benutzt markieren)
static func hold(path: String, tex: Resource) -> void:
	if tex == null:
		return
	if _held.has(path):
		_order.erase(path)
		_order.append(path)
		return
	_held[path] = tex
	if _size_of(tex) == 0:
		return   # Skripte und Kleinkram bleiben immer
	_order.append(path)
	_bytes += _size_of(tex)
	while _bytes > BUDGET and _order.size() > 1:
		var old: String = _order.pop_front()
		_bytes -= _size_of(_held[old])
		_held.erase(old)


static func _size_of(r: Resource) -> int:
	if r is Texture2D:
		return (r as Texture2D).get_width() * (r as Texture2D).get_height() * 4
	return 0


static func held_mb() -> float:
	return _bytes / 1048576.0
