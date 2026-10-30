class_name BallRun
extends Control
## Die Kugelbahn unten am Bildschirm: Ein Federhebel schießt Energiekugeln in die Bahn,
## sie klackern durch Stifte und Tore und landen im Sammler. Jede gesammelte Kugel ist Munition.
## Der Hebel schießt von selbst; wer ihn zieht, bekommt eine Extra-Ladung (Abklingzeit).

signal ball_collected(type: String)

const PANEL_H := 470.0
const DESIGN_W := 720.0
const MAX_BALLS := 55
const LAUNCH_POS := Vector2(668, 436)
const PULL_RECT := Rect2(600, 300, 120, 170)
const COLLECT_RECT := Rect2(300, 424, 120, 34)
const GATE_SIZE := Vector2(100, 20)
const GATE_SLOTS := [Vector2(150, 200), Vector2(330, 200), Vector2(510, 200), Vector2(240, 296), Vector2(420, 296)]
## Reihenfolge, in der neue Tore eingebaut werden.
const GATE_ORDER := [1, 3, 4, 0, 2]
const MANUAL_CD := 6.0
const WALL_R := 5.0
## Abstand zwischen zwei Kugeln einer Ladung.
const LAUNCH_GAP := 0.16
const BASE_INTERVAL := 1.4
const BASE_COUNT := 3
const GATE_INFO := {
	"x2": {"label": "×2", "color": Color(0.35, 1.0, 0.55)},
	"plus3": {"label": "+3", "color": Color(1.0, 0.85, 0.25)},
	"fire": {"label": "FEUER", "color": Color(1.0, 0.45, 0.15)},
	"ice": {"label": "EIS", "color": Color(0.45, 0.9, 1.0)},
}

var ammo: AmmoStore
var active := false
var launch_interval := BASE_INTERVAL
var balls_per_launch := BASE_COUNT
var rate_level := 0
## Für Auswertungen: gesammelte Kugeln im aktuellen Level.
var collected_total := 0
var stats := {"launched": 0, "recycled": 0, "lost": 0, "aged": 0, "full": 0}

var _board: Node2D
var _balls: Node2D
var _gate_types: Array[String] = ["", "", "", "", ""]
var _gate_pulse: Array[float] = [0.0, 0.0, 0.0, 0.0, 0.0]
var _pegs: Array[Vector2] = []
var _lines: Array[PackedVector2Array] = []
var _launch_timer := 0.8
var _pending := 0
var _pending_t := 0.0
var _plunger := 0.0
var _pulling := false
var _pull := 0.0
var _pull_start := 0.0
var _manual_cd := 0.0
var _pops: Array = []
var _full_flash := 0.0
var _hint_t := 0.0
var _font: Font


func _ready() -> void:
	clip_contents = true
	mouse_filter = Control.MOUSE_FILTER_STOP
	_font = ThemeDB.fallback_font
	_board = Node2D.new()
	add_child(_board)
	_balls = Node2D.new()
	_board.add_child(_balls)
	_build_geometry()
	resized.connect(_layout)
	_layout()
	reset()


func _layout() -> void:
	_board.position = Vector2(floorf((size.x - DESIGN_W) * 0.5), floorf((size.y - PANEL_H) * 0.5))


# --- Steuerung von außen ---------------------------------------------------

func reset() -> void:
	for b in _balls.get_children():
		b.queue_free()
	for i in _gate_types.size():
		_gate_types[i] = ""
		_gate_pulse[i] = 0.0
	_gate_types[1] = "x2"
	launch_interval = BASE_INTERVAL
	balls_per_launch = BASE_COUNT
	rate_level = 0
	active = false
	_launch_timer = 0.6
	_pending = 0
	_manual_cd = 0.0
	_pull = 0.0
	_pulling = false
	_pops.clear()
	collected_total = 0
	stats = {"launched": 0, "recycled": 0, "lost": 0, "aged": 0, "full": 0}


func free_slots() -> int:
	return _gate_types.count("")


func has_gate(type: String) -> bool:
	return _gate_types.has(type)


func add_gate(type: String) -> bool:
	for idx in GATE_ORDER:
		if _gate_types[idx] == "":
			_gate_types[idx] = type
			_gate_pulse[idx] = 1.5
			return true
	return false


func upgrade_rate() -> void:
	rate_level += 1
	launch_interval = BASE_INTERVAL / (1.0 + 0.25 * rate_level)


func upgrade_count() -> void:
	balls_per_launch += 1


func ball_count() -> int:
	return _balls.get_child_count()


# --- Ablauf ----------------------------------------------------------------

func _process(delta: float) -> void:
	_hint_t += delta
	if active:
		_launch_timer -= delta
		if _launch_timer <= 0.0:
			_launch_timer = launch_interval
			_pending += balls_per_launch
		_manual_cd = maxf(0.0, _manual_cd - delta)
	_pending_t -= delta
	if _pending > 0 and _pending_t <= 0.0:
		_pending -= 1
		_pending_t = LAUNCH_GAP
		_launch_one()
	_plunger = maxf(0.0, _plunger - delta * 5.0)
	_full_flash = maxf(0.0, _full_flash - delta * 1.5)
	for i in _gate_pulse.size():
		_gate_pulse[i] = maxf(0.0, _gate_pulse[i] - delta * 4.0)
	for p in _pops:
		p["t"] = float(p["t"]) + delta
	_pops = _pops.filter(func(p: Dictionary) -> bool: return float(p["t"]) < 0.6)
	queue_redraw()


func _physics_process(_delta: float) -> void:
	for node in _balls.get_children():
		var ball := node as AmmoBall
		if ball == null or ball.collected:
			continue
		if ball.age > 14.0:
			stats["aged"] += 1
			_collect(ball)
		elif ball.position.y > PANEL_H + 40.0 or ball.position.x > DESIGN_W + 40.0:
			ball.collected = true
			stats["lost"] += 1
			ball.queue_free()
		elif ball.position.x > 640.0 and ball.position.y > 110.0 and ball.linear_velocity.y > 0.0 and ball.age > 0.3:
			# Kugel fällt in die Abschussbahn zurück: herausnehmen und neu einreihen,
			# damit sie nicht mit aufsteigenden Kugeln zusammenstößt
			stats["recycled"] += 1
			ball.collected = true
			ball.queue_free()
			_pending += 1


func _launch_velocity() -> Vector2:
	return Vector2(randf_range(-3.0, 3.0), -randf_range(1160.0, 1240.0))


func _launch_one() -> void:
	if _spawn_ball("normal", LAUNCH_POS + Vector2(randf_range(-1.0, 1.0), 0), _launch_velocity(), {}):
		stats["launched"] += 1
		_plunger = 1.0


func _spawn_ball(type: String, pos: Vector2, vel: Vector2, passed: Dictionary) -> bool:
	if _balls.get_child_count() >= MAX_BALLS:
		return false
	var b := AmmoBall.new()
	b.position = pos
	b.type = type
	b.passed = passed
	_balls.add_child(b)
	b.linear_velocity = vel
	return true


func _on_gate(body: Node, idx: int) -> void:
	var ball := body as AmmoBall
	if ball == null or ball.collected:
		return
	var type := _gate_types[idx]
	if type == "" or ball.passed.has(idx):
		return
	ball.passed[idx] = true
	_gate_pulse[idx] = 1.0
	match type:
		"x2":
			_clone(ball, 1)
		"plus3":
			_clone(ball, 3)
		"fire", "ice":
			ball.set_type(type)


func _clone(src: AmmoBall, n: int) -> void:
	# Kopien versetzt neben die Kugel setzen, damit sie sich nicht überlappen
	var offsets := [-22.0, 22.0, -44.0, 44.0]
	for i in n:
		var pos := src.position + Vector2(offsets[i % offsets.size()], -2.0)
		pos.x = clampf(pos.x, 36.0, 624.0)
		var vel := src.linear_velocity.rotated(randf_range(-0.4, 0.4)) * randf_range(0.7, 0.95)
		_spawn_ball.call_deferred(src.type, pos, vel, src.passed.duplicate())


func _on_collect(body: Node) -> void:
	var ball := body as AmmoBall
	if ball and not ball.collected:
		_collect(ball)


func _collect(ball: AmmoBall) -> void:
	ball.collected = true
	collected_total += 1
	var added := 0
	if ammo:
		added = ammo.add(ball.type, 1)
	if added == 0:
		stats["full"] += 1
		_full_flash = 1.0
	_pops.append({"pos": ball.position, "t": 0.0, "color": AmmoBall.COLORS.get(ball.type, Color.WHITE), "text": "+1" if added > 0 else "voll"})
	ball_collected.emit(ball.type)
	ball.queue_free.call_deferred()


# --- Hebel ziehen ----------------------------------------------------------

func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		var p: Vector2 = event.position - _board.position
		if event.pressed and PULL_RECT.has_point(p):
			_pulling = true
			_pull_start = p.y
			_pull = 0.0
			accept_event()
		elif not event.pressed and _pulling:
			_pulling = false
			_release_pull()
			accept_event()
	elif event is InputEventMouseMotion and _pulling:
		var p: Vector2 = event.position - _board.position
		_pull = clampf((p.y - _pull_start) / 110.0, 0.0, 1.0)
		accept_event()


func _release_pull() -> void:
	if active and _manual_cd <= 0.0:
		_pending += balls_per_launch + int(round(_pull * 4.0))
		_manual_cd = MANUAL_CD
	_pull = 0.0


## Für den automatischen Test: Hebel ziehen, wenn er bereit ist.
func try_manual_pull() -> void:
	if active and _manual_cd <= 0.0:
		_pull = 1.0
		_release_pull()


# --- Aufbau ----------------------------------------------------------------

func _build_geometry() -> void:
	_lines = [
		PackedVector2Array([Vector2(24, 330), Vector2(24, 14), Vector2(560, 14), Vector2(620, 17), Vector2(662, 29), Vector2(688, 50), Vector2(700, 80), Vector2(700, 458)]),
		PackedVector2Array([Vector2(636, 86), Vector2(636, 458), Vector2(700, 458)]),
		PackedVector2Array([Vector2(24, 330), Vector2(300, 420), Vector2(300, 458), Vector2(420, 458), Vector2(420, 420), Vector2(636, 330)]),
	]
	# Stifte: drei volle Reihen, dazu einzelne Stifte zwischen den Toren
	for row in 3:
		var y := 64.0 + row * 42.0
		var x := 62.0 + (row % 2) * 27.5
		while x <= 610.0:
			_pegs.append(Vector2(x, y))
			x += 55.0
	for x in [61.0, 240.0, 420.0, 599.0]:
		_pegs.append(Vector2(x, 200.0))
	var x2 := 89.5
	while x2 <= 610.0:
		_pegs.append(Vector2(x2, 248.0))
		x2 += 55.0
	for x in [70.0, 130.0, 330.0, 520.0, 585.0]:
		_pegs.append(Vector2(x, 296.0))

	var walls := StaticBody2D.new()
	walls.collision_layer = 1
	walls.collision_mask = 0
	var pm := PhysicsMaterial.new()
	pm.bounce = 0.4
	pm.friction = 0.1
	walls.physics_material_override = pm
	_board.add_child(walls)
	# Wände aus Kapseln: dick und an den Ecken überlappend, damit schnelle Kugeln nicht durchrutschen
	for line in _lines:
		for i in line.size() - 1:
			var a: Vector2 = line[i]
			var b: Vector2 = line[i + 1]
			var cap := CapsuleShape2D.new()
			cap.radius = WALL_R
			cap.height = a.distance_to(b) + WALL_R * 2.0
			var cs := CollisionShape2D.new()
			cs.shape = cap
			cs.position = (a + b) * 0.5
			cs.rotation = (b - a).angle() - PI * 0.5
			walls.add_child(cs)
	for p in _pegs:
		var c := CircleShape2D.new()
		c.radius = 6.0
		var cs := CollisionShape2D.new()
		cs.shape = c
		cs.position = p
		walls.add_child(cs)

	for i in GATE_SLOTS.size():
		var area := Area2D.new()
		area.collision_layer = 0
		area.collision_mask = 2
		var rect := RectangleShape2D.new()
		rect.size = GATE_SIZE
		var cs := CollisionShape2D.new()
		cs.shape = rect
		area.add_child(cs)
		area.position = GATE_SLOTS[i]
		area.body_entered.connect(_on_gate.bind(i))
		_board.add_child(area)

	var collector := Area2D.new()
	collector.collision_layer = 0
	collector.collision_mask = 2
	var crect := RectangleShape2D.new()
	crect.size = COLLECT_RECT.size
	var ccs := CollisionShape2D.new()
	ccs.shape = crect
	collector.add_child(ccs)
	collector.position = COLLECT_RECT.get_center()
	collector.body_entered.connect(_on_collect)
	_board.add_child(collector)


# --- Zeichnen --------------------------------------------------------------

func _draw() -> void:
	var o := _board.position
	draw_rect(Rect2(Vector2.ZERO, size), Color(0.045, 0.05, 0.1))
	draw_rect(Rect2(0, 0, size.x, 4), Color(0.2, 0.85, 1.0, 0.9))
	# Bahnfläche
	var area := PackedVector2Array()
	for p in [Vector2(24, 14), Vector2(560, 14), Vector2(620, 17), Vector2(662, 29), Vector2(688, 50), Vector2(700, 80),
			Vector2(700, 458), Vector2(636, 458), Vector2(636, 330), Vector2(420, 420), Vector2(420, 458),
			Vector2(300, 458), Vector2(300, 420), Vector2(24, 330)]:
		area.append(o + p)
	draw_colored_polygon(area, Color(0.085, 0.1, 0.18))
	for gx in range(60, 700, 40):
		draw_line(o + Vector2(gx, 16), o + Vector2(gx, 330), Color(1, 1, 1, 0.025), 1.0)
	# Sammler
	var cr := Rect2(o + COLLECT_RECT.position, COLLECT_RECT.size)
	draw_rect(cr, Color(0.2, 0.85, 1.0, 0.12 + 0.1 * sin(_hint_t * 3.0)))
	# Wände
	for line in _lines:
		var pts := PackedVector2Array()
		for p in line:
			pts.append(o + p)
		draw_polyline(pts, Color(0.32, 0.4, 0.55), 7.0, true)
		draw_polyline(pts, Color(0.55, 0.68, 0.85), 2.0, true)
	# Stifte
	for p in _pegs:
		draw_circle(o + p, 9.0, Color(0.2, 0.85, 1.0, 0.16))
		draw_circle(o + p, 5.5, Color(0.78, 0.95, 1.0))
	# Tore
	for i in GATE_SLOTS.size():
		var center: Vector2 = GATE_SLOTS[i]
		var r := Rect2(o + center - GATE_SIZE * 0.5, GATE_SIZE)
		var type := _gate_types[i]
		if type == "":
			draw_rect(r, Color(1, 1, 1, 0.04))
			draw_rect(r, Color(1, 1, 1, 0.14), false, 2.0)
			continue
		var info: Dictionary = GATE_INFO[type]
		var c: Color = info["color"]
		var pulse := _gate_pulse[i]
		draw_rect(r.grow(5.0 + pulse * 4.0), Color(c.r, c.g, c.b, 0.15 + pulse * 0.3))
		draw_rect(r, Color(c.r, c.g, c.b, 0.85))
		draw_string(_font, Vector2(r.position.x, r.position.y + 16.0), info["label"], HORIZONTAL_ALIGNMENT_CENTER, r.size.x, 17, Color(0.08, 0.08, 0.12))
	# Speicher-Anzeige
	_draw_storage(o)
	# Hebel
	_draw_plunger(o)
	# „+1“ am Sammler
	for p in _pops:
		var t: float = p["t"]
		var c: Color = p["color"]
		c.a = 1.0 - t / 0.6
		var pos: Vector2 = o + Vector2(clampf(p["pos"].x, 310.0, 410.0), 420.0 - t * 50.0)
		draw_string(_font, pos + Vector2(-30, 0), p["text"], HORIZONTAL_ALIGNMENT_CENTER, 60, 18, c)


func _draw_storage(o: Vector2) -> void:
	var total := 0
	var cap := 1
	var counts := {"normal": 0, "fire": 0, "ice": 0}
	if ammo:
		total = ammo.total()
		cap = maxi(1, ammo.cap)
		counts = ammo.counts
	var label_col := Color(1.0, 0.45, 0.4) if _full_flash > 0.0 else Color(0.85, 0.9, 1.0)
	draw_string(_font, o + Vector2(40, 404), "Munition" if _full_flash <= 0.0 else "Speicher voll!", HORIZONTAL_ALIGNMENT_LEFT, -1, 17, label_col)
	var bar := Rect2(o + Vector2(40, 414), Vector2(190, 20))
	draw_rect(bar, Color(0, 0, 0, 0.6))
	var x := bar.position.x + 2.0
	var w := bar.size.x - 4.0
	for type in ["fire", "ice", "normal"]:
		var n: int = counts[type]
		if n <= 0:
			continue
		var seg_w := w * float(n) / cap
		draw_rect(Rect2(x, bar.position.y + 2.0, seg_w, bar.size.y - 4.0), AmmoBall.COLORS[type])
		x += seg_w
	draw_rect(bar, Color(0.55, 0.68, 0.85), false, 2.0)
	draw_string(_font, o + Vector2(40, 456), "%d / %d" % [total, cap], HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color(1, 0.9, 0.55))


func _draw_plunger(o: Vector2) -> void:
	var knob_y := 452.0 + _pull * 12.0 - _plunger * 10.0
	# Feder
	var pts := PackedVector2Array()
	var top := knob_y + 4.0
	for k in 7:
		var yy := top + (464.0 - top) * k / 6.0
		pts.append(o + Vector2(668.0 + (8.0 if k % 2 == 0 else -8.0), yy))
	draw_polyline(pts, Color(0.7, 0.75, 0.85), 2.0)
	draw_rect(Rect2(o + Vector2(646, knob_y - 4.0), Vector2(44, 8)), Color(1.0, 0.8, 0.25))
	# Hinweis links neben der Bahn
	var ready := active and _manual_cd <= 0.0
	var text := ""
	var col := Color(0.85, 0.9, 1.0)
	if not active:
		text = ""
	elif ready:
		text = "Hebel ziehen: Extra!"
		col = Color(1.0, 0.85, 0.3, 0.6 + 0.4 * sin(_hint_t * 6.0))
	else:
		text = "Hebel lädt … %d s" % int(ceil(_manual_cd))
	if text != "":
		draw_string(_font, o + Vector2(440, 424), text, HORIZONTAL_ALIGNMENT_RIGHT, 190, 16, col)
	var auto_text := "Auto: %d Kugeln / %s s" % [balls_per_launch, String.num(launch_interval, 1).replace(".", ",")]
	draw_string(_font, o + Vector2(440, 450), auto_text, HORIZONTAL_ALIGNMENT_RIGHT, 190, 15, Color(0.6, 0.7, 0.85))
	if _pulling:
		draw_rect(Rect2(o + Vector2(640, 300), Vector2(56, 150)), Color(1.0, 0.85, 0.3, 0.12 + _pull * 0.2))
