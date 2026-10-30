class_name Updater
extends Node
## Selbst-Update für die Testphase (später übernimmt das Google Play).
##
## Ablauf:
## 1. Beim Start lädt die App version.json von GitHub Pages und vergleicht die Versionsnummer
##    mit der eigenen (res://build_info.json, wird beim Bauen geschrieben).
## 2. Ist eine neuere da, meldet sie update_available; das Menü zeigt oben „Jetzt aktualisieren“.
## 3. Auf Wunsch lädt die App die APK in ihren eigenen Speicher und öffnet die Android-
##    Installation. Beim nächsten Start wird die Datei gelöscht, damit nichts liegen bleibt.

signal update_available(info: Dictionary)
signal download_progress(ratio: float)
signal download_failed(message: String)
signal download_done

const BASE_URL := "https://ramonweihmann-ops.github.io/Handy-App-Tower-Defense_-No-Name/pilot/"
const APK_FILE := "update.apk"

var current_code := 0
var current_name := "?"
var current_stamp := ""
var latest: Dictionary = {}
var downloading := false

var _check_req: HTTPRequest
var _dl_req: HTTPRequest
var _last_check := -1000.0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	var f := FileAccess.open("res://build_info.json", FileAccess.READ)
	if f:
		var info = JSON.parse_string(f.get_as_text())
		if info is Dictionary:
			current_code = int(info.get("code", 0))
			current_name = str(info.get("name", "?"))
			current_stamp = str(info.get("stamp", ""))
	# Alte Update-Datei aufräumen (die neue Version läuft ja schon)
	var old := apk_path()
	if FileAccess.file_exists(old):
		DirAccess.remove_absolute(old)
	_check_req = HTTPRequest.new()
	_check_req.timeout = 15.0
	add_child(_check_req)
	_check_req.request_completed.connect(_on_check_done)
	_dl_req = HTTPRequest.new()
	_dl_req.timeout = 600.0
	_dl_req.use_threads = true
	add_child(_dl_req)
	_dl_req.request_completed.connect(_on_download_done)


func apk_path() -> String:
	return OS.get_user_data_dir().path_join(APK_FILE)


## Fragt nach einer neuen Version (höchstens alle 60 Sekunden, außer force).
func check(force := false) -> void:
	if current_code == 0 and not force:
		return
	var now := Time.get_ticks_msec() / 1000.0
	if not force and now - _last_check < 60.0:
		if has_update():
			update_available.emit(latest)
		return
	_last_check = now
	_check_req.cancel_request()
	var url := BASE_URL + "version.json?t=%d" % int(Time.get_unix_time_from_system())
	_check_req.request(url, ["Cache-Control: no-cache"])


func has_update() -> bool:
	return not latest.is_empty() and int(latest.get("code", 0)) > current_code


func _on_check_done(result: int, code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	if result != HTTPRequest.RESULT_SUCCESS or code != 200:
		return
	var info = JSON.parse_string(body.get_string_from_utf8())
	if not (info is Dictionary):
		return
	latest = info
	if has_update():
		update_available.emit(latest)


func start_download() -> void:
	if downloading or not has_update():
		return
	downloading = true
	var path := apk_path()
	if FileAccess.file_exists(path):
		DirAccess.remove_absolute(path)
	_dl_req.download_file = path
	var err := _dl_req.request(BASE_URL + str(latest.get("apk", "")))
	if err != OK:
		downloading = false
		download_failed.emit("Download konnte nicht starten.")


func _process(_delta: float) -> void:
	if downloading:
		var total := _dl_req.get_body_size()
		if total > 0:
			download_progress.emit(float(_dl_req.get_downloaded_bytes()) / total)


func _on_download_done(result: int, code: int, _headers: PackedStringArray, _body: PackedByteArray) -> void:
	downloading = false
	if result != HTTPRequest.RESULT_SUCCESS or code != 200:
		download_failed.emit("Download fehlgeschlagen. Bitte später noch einmal versuchen.")
		return
	download_done.emit()
	install()


## Öffnet die Android-Installation für die geladene APK. Klappt das nicht, öffnet sich die
## Download-Seite im Browser als Ausweg.
func install() -> void:
	var path := apk_path()
	if OS.get_name() == "Android" and FileAccess.file_exists(path):
		var err := OS.shell_open(path)
		if err == OK:
			return
	OS.shell_open(BASE_URL)
