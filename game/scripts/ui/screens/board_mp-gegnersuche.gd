extends MockScreen
## Gegnersuche (Mockup „Multiplayer · Gegnersuche“): Der Spieler oben, darunter drei Plätze, die sich
## nacheinander mit Kommandanten füllen. Im Pilot sind es Computergegner (MpMatch), die wie echte
## Spieler erscheinen. Sind alle drei da, beginnt der Kampf. „Abbrechen“ kostet nichts.

## Mittelpunkte der Rundbilder (aus dem Export)
const NAME_KEYS := [["Nebula_Nia", "1.310"], ["Kosmo_K", "1.195"], ["?", "wird gesucht …"]]

var game: MpMatch
var found := 0
var _t := 0.0
var _next := 0.0
var _layer: Control
var _station := 1


func _init(m: MainMenu) -> void:
	super("mp_suche", m)


func _ready() -> void:
	super()
	_station = MpData.station_level(Save.max_level())
	game = MpMatch.new(_station, Save.trophies(), randi())
	_layer = Layer.new()
	_layer.board = self
	place_at(_layer, Rect2(0, 0, W, H))
	_next = randf_range(0.7, 1.3)
	var t := Save.trophies()
	set_text("Bronze-Liga · Station 4", "%s · Station %d" % [MpData.league_name(t), _station])
	set_text("1.228 · Stufe 9", "%s · Stufe %d" % [MockScreen.num(t), Save.hero_level(_hero())])
	for i in 3:
		set_text(NAME_KEYS[i][0], "?")
		set_text(NAME_KEYS[i][1], "wird gesucht …")


func _hero() -> String:
	var sq := Save.squad()
	return sq[0] if not sq.is_empty() else "dusty"


func _process(delta: float) -> void:
	super(delta)
	_t += delta
	_layer.queue_redraw()
	if found >= 3:
		if _t >= _next:
			set_process(false)
			menu.close_board(self)
			menu.mp_requested.emit(game)
		return
	if _t >= _next:
		var b: Dictionary = game.bots[found]
		set_text(NAME_KEYS[found][0], str(b["name"]))
		set_text(NAME_KEYS[found][1], MockScreen.num(int(b["trophies"])))
		Sfx.play("click")
		found += 1
		_next = _t + (randf_range(0.6, 1.5) if found < 3 else 0.9)


func handle(b: Dictionary) -> bool:
	if str(b.get("href", "")) == "MP-Kampf.dc.html":
		menu.close_board(self)
		return true
	return false


class Layer:
	extends Control
	var board: MockScreen

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE

	func _draw() -> void:
		var bd: Variant = board
		var s := board.s
		var me := board.live_rect("av")
		MpPaint.avatar(self, me.get_center() * s, me.size.x * s, bd._hero(), Color.WHITE, 3 * s)
		for i in 3:
			var r := board.live_rect("av_%d" % (i + 1))
			var c := r.get_center() * s
			if i < int(bd.found):
				MpPaint.avatar(self, c, r.size.x * s, str(bd.game.bots[i]["hero"]), Color("#ffd0d6"), 3 * s)
			else:
				# Suche läuft: pulsierendes Fragezeichen
				var p := 0.5 + 0.5 * sin(float(bd._t) * 6.0 + i)
				draw_circle(c, r.size.x * 0.5 * s, Color("#1c1850"))
				draw_circle(c - Vector2(6, 6) * s, r.size.x * 0.3 * s, Color(0.35, 0.29, 0.69, 0.8))
				draw_arc(c, (r.size.x * 0.5 - 1.5) * s, 0.0, TAU, 40, Color("#ffd0d6"), 3 * s, true)
				var fs := 28.0 * (1.0 + 0.06 * p)
				MockPaint.text(board, self, "?", Rect2(r.position.x, r.position.y + 14, r.size.x, 34), "Fredoka", 700, fs, "rgba(255, 247, 234, %.2f)" % (0.55 + 0.45 * p))
