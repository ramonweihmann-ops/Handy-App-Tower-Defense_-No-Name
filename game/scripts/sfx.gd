extends Node
## Töne und Musik (Autoload „Sfx“). Alle Klänge sind selbst erzeugt (scripts/make_sounds.py).
## Ein kleiner Pool von Spielern; gleiche Töne werden gedrosselt, damit Salven bei x2/x3
## nicht zu einem Rauschen werden und das Handy nicht überlastet.

const SOUNDS := ["shot", "shot_light", "shot_heavy", "launch", "boom", "zap", "frost", "flame",
	"pop", "clack", "ding", "spring", "click", "whoosh", "levelup", "win", "lose"]
## Mindestabstand in Sekunden zwischen zwei gleichen Tönen.
const GAP := {"shot": 0.07, "shot_light": 0.06, "shot_heavy": 0.12, "launch": 0.15, "boom": 0.09,
	"zap": 0.1, "frost": 0.12, "flame": 0.18, "pop": 0.05, "clack": 0.04, "ding": 0.06,
	"spring": 0.2, "click": 0.03, "whoosh": 0.1}
## Lautstärke je Ton in dB.
const VOLUME := {"shot": -14.0, "shot_light": -15.0, "shot_heavy": -11.0, "launch": -10.0,
	"boom": -9.0, "zap": -13.0, "frost": -13.0, "flame": -15.0, "pop": -12.0, "clack": -20.0,
	"ding": -14.0, "spring": -9.0, "click": -10.0, "whoosh": -9.0, "levelup": -6.0, "win": -5.0,
	"lose": -5.0}
const POOL := 10

var _streams := {}
var _last := {}
var _players: Array[AudioStreamPlayer] = []
var _next := 0
var _music: AudioStreamPlayer
var _time := 0.0
## Während des automatischen Tests stumm, damit nichts Zeit kostet.
var muted := false


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for n in SOUNDS:
		var path := "res://audio/%s.wav" % n
		if ResourceLoader.exists(path):
			_streams[n] = load(path)
	for i in POOL:
		var p := AudioStreamPlayer.new()
		add_child(p)
		_players.append(p)
	_music = AudioStreamPlayer.new()
	_music.volume_db = -16.0
	add_child(_music)
	if ResourceLoader.exists("res://audio/music.wav"):
		_music.stream = load("res://audio/music.wav")
	_music.finished.connect(func() -> void:
		if music_on():
			_music.play())
	# Jeder Knopf im Spiel klickt beim Antippen, ohne dass jede Stelle daran denken muss
	get_tree().node_added.connect(func(n: Node) -> void:
		if n is BaseButton:
			(n as BaseButton).pressed.connect(func() -> void: play("click", 0.06)))


## Beim Beenden alles anhalten und freigeben, sonst hält der Audioserver die Klänge fest.
func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST or what == NOTIFICATION_EXIT_TREE:
		for p in _players:
			p.stop()
			p.stream = null
		if _music:
			_music.stop()
			_music.stream = null
		_streams.clear()


func _process(delta: float) -> void:
	_time += delta


## Ohne Fenster (automatische Tests) gibt es nichts zu hören.
func _silent() -> bool:
	return muted or DisplayServer.get_name() == "headless"


func sound_on() -> bool:
	return not _silent() and bool(Save.data.get("sound", true))


func music_on() -> bool:
	return not _silent() and bool(Save.data.get("music", true))


## Spielt einen kurzen Ton; pitch_var streut die Tonhöhe leicht, damit es lebendig klingt.
func play(name: String, pitch_var: float = 0.08, volume: float = 0.0) -> void:
	if not sound_on() or not _streams.has(name):
		return
	var gap: float = GAP.get(name, 0.0)
	if _time - float(_last.get(name, -10.0)) < gap:
		return
	_last[name] = _time
	var p := _players[_next]
	_next = (_next + 1) % POOL
	p.stream = _streams[name]
	p.volume_db = float(VOLUME.get(name, -10.0)) + volume
	p.pitch_scale = 1.0 + randf_range(-pitch_var, pitch_var)
	p.play()


func start_music() -> void:
	if music_on() and _music.stream and not _music.playing:
		_music.play()


func stop_music() -> void:
	_music.stop()


func set_sound(on: bool) -> void:
	Save.data["sound"] = on
	Save.save_game()


func set_music(on: bool) -> void:
	Save.data["music"] = on
	Save.save_game()
	if on:
		start_music()
	else:
		stop_music()
