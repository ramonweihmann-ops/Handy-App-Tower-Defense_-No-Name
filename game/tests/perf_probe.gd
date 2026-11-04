extends Node
## Leistungsprobe: misst Bildzeiten beim Öffnen der Reiter, beim Ziehen und Zoomen der Basiskarte,
## beim Öffnen eines Gebäudes und im Kampf. Aufruf (mit Fenster, sonst wird nicht gezeichnet):
## godot --path game -- --perf
## Ausgabe: PERF <Abschnitt> bilder=… mittel=… ms max=… ms ruckler(>33 ms)=…

var main: Node
var _phase := 0
var _frame := 0
var _last := 0
var _times: Array[float] = []
var _label := ""
var _spike_call := 0.0
var _proc: Array[float] = []
var _cpu: Array[float] = []
var _gpu: Array[float] = []
var _calls: Array[float] = []
var _prims: Array[float] = []


var _first: Node
var _proc_t0 := 0


## Läuft vor allen anderen _process: Beginn der Skriptzeit im Bild
class First:
	extends Node
	var probe: Node
	func _process(_d: float) -> void:
		probe.set("_proc_t0", Time.get_ticks_usec())


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	process_priority = 100000
	_first = First.new()
	_first.probe = self
	_first.process_priority = -100000
	_first.process_mode = Node.PROCESS_MODE_ALWAYS
	add_child.call_deferred(_first)
	RenderingServer.viewport_set_measure_render_time(get_viewport().get_viewport_rid(), true)


func _begin(label: String) -> void:
	_label = label
	_times.clear()
	_proc.clear()
	_cpu.clear()
	_gpu.clear()
	_calls.clear()
	_prims.clear()
	_frame = 0


func _end() -> void:
	if _times.is_empty():
		return
	var sum := 0.0
	var mx := 0.0
	var spikes := 0
	for t in _times:
		sum += t
		mx = maxf(mx, t)
		if t > 33.0:
			spikes += 1
	print("PERF %-20s n=%3d bild=%5.1f max=%6.1f ruckler=%3d | skript=%4.1f max=%5.1f | zeichnen cpu=%4.1f gpu=%5.1f | aufrufe=%4.0f prim=%6.0f%s" % [_label, _times.size(), sum / _times.size(), mx, spikes,
		_avg(_proc), _max(_proc), _avg(_cpu), _avg(_gpu), _avg(_calls), _avg(_prims),
		("  aufruf=%.0f ms" % _spike_call) if _spike_call > 0.0 else ""])
	print("PERF   speicher: vorgehalten %.0f MB, texturen %.0f MB, video %.0f MB, knoten %d" % [TexCache.held_mb(), Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED) / 1048576.0,
		Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED) / 1048576.0, Performance.get_monitor(Performance.OBJECT_NODE_COUNT)])
	_spike_call = 0.0


func _avg(a: Array[float]) -> float:
	var t := 0.0
	for v in a:
		t += v
	return t / maxf(1.0, a.size())


func _max(a: Array[float]) -> float:
	var t := 0.0
	for v in a:
		t = maxf(t, v)
	return t


func _timed(f: Callable) -> void:
	var t0 := Time.get_ticks_usec()
	f.call()
	_spike_call = (Time.get_ticks_usec() - t0) / 1000.0


func _process(_d: float) -> void:
	var now := Time.get_ticks_usec()
	if _last > 0 and _label != "":
		_times.append((now - _last) / 1000.0)
		_proc.append((now - _proc_t0) / 1000.0 if _proc_t0 > 0 else 0.0)
		var vp := get_viewport().get_viewport_rid()
		_cpu.append(RenderingServer.viewport_get_measured_render_time_cpu(vp) + RenderingServer.get_frame_setup_time_cpu())
		_gpu.append(RenderingServer.viewport_get_measured_render_time_gpu(vp))
		_calls.append(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
		_prims.append(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME))
	_last = now
	_frame += 1
	if "--autotest" in OS.get_cmdline_user_args():
		# Kampf vom Autotest spielen lassen, nur messen (je 5 s ein Abschnitt)
		if main.state == "battle":
			for arg in OS.get_cmdline_user_args():
				if arg.begins_with("--stufe=") and int(Save.data.get("perf_level", 0)) != int(arg.get_slice("=", 1)):
					Save.data["perf_level"] = int(arg.get_slice("=", 1))
					main.battle.apply_quality()
				if arg.begins_with("--quality=") and Save.data.get("quality") != arg.get_slice("=", 1):
					Save.data["quality"] = arg.get_slice("=", 1)
					main.battle.apply_quality()
			if "--noglow" in OS.get_cmdline_user_args() and main.battle._env:
				main.battle._env.glow_enabled = false
			if "--noshadow" in OS.get_cmdline_user_args() and main.battle._sun:
				main.battle._sun.shadow_enabled = false
			if _label == "":
				_begin("kampf 0 s")
			elif _times.size() >= 300:
				var sec := _frame / 60
				_end()
				_census(main.battle)
				_begin("kampf %d s (%d gegner)" % [sec, main.battle.enemies.size() if "enemies" in main.battle else -1])
		return
	if main.state != "menu" and _phase < 20:
		return
	var m: MainMenu = main.menu
	match _phase:
		0:
			if _frame > 240:
				Save.reset()
				Save.data["gold"] = 50000
				Save.data["max_level"] = 20
				_phase = 1
				_begin("menü ruhig")
		1:
			if _frame == 60:
				_dump(get_tree().root, "")
			if _frame == 110:
				_textures()
			if _frame > 120:
				_end()
				_phase = 2
		2:
			_next_tab(m, ["shop", "sammlung", "upgrades", "basis", "kampf", "basis"])
		3:
			# Basiskarte ziehen
			var map := _map(m)
			if map:
				var ev := InputEventMouseMotion.new()
				ev.button_mask = MOUSE_BUTTON_MASK_LEFT
				ev.relative = Vector2(0, 14.0 * (1 if (_frame / 60) % 2 == 0 else -1))
				ev.position = map.size * 0.5
				map._gui_input(ev)
			if _frame == 100 and map:
				var t0 := Time.get_ticks_usec()
				for k in 10:
					map._refresh_cache()
				print("PERF   basis zwischenspeicher: %.2f ms" % ((Time.get_ticks_usec() - t0) / 10000.0))
			if _frame > 180:
				_end()
				_phase = 4
				_begin("basis zoomen")
		4:
			var map := _map(m)
			if map:
				var ev := InputEventMouseButton.new()
				ev.pressed = true
				ev.button_index = MOUSE_BUTTON_WHEEL_UP if (_frame / 40) % 2 == 0 else MOUSE_BUTTON_WHEEL_DOWN
				ev.position = map.size * 0.5
				map._gui_input(ev)
			if _frame > 160:
				_end()
				_phase = 5
		5:
			_begin("gebäude öffnen")
			_timed(func() -> void: m.open_building("01"))
			_phase = 6
		6:
			if _frame > 90:
				_end()
				_phase = 7
				_begin("basis ruhig")
				m._close_modal() if m.has_method("_close_modal") else null
		7:
			if _frame > 120:
				_end()
				_phase = 8
		8:
			_begin("kampf starten")
			_timed(func() -> void: main.start_level(5))
			_phase = 20
		20:
			if main.state == "hero_select":
				main._on_hero_picked("dusty")
			if main.state == "battle":
				_end()
				_begin("kampf")
				_phase = 21
		21:
			if _frame % 300 == 0:
				_end()
				_begin("kampf ab %d s" % (_frame / 60))
			if _frame > 2400 or main.state != "battle":
				_end()
				print("PERF fertig")
				get_tree().quit()


var _tab_i := 0
var _tab_wait := 0


func _next_tab(m: MainMenu, tabs: Array) -> void:
	if _tab_wait > 0:
		_tab_wait -= 1
		if _tab_wait == 0:
			_end()
		return
	if _tab_i >= tabs.size():
		_phase = 3
		_begin("basis ziehen")
		return
	var t: String = tabs[_tab_i]
	_tab_i += 1
	_begin("reiter " + t)
	var t0 := Time.get_ticks_usec()
	var probe: Control = m._mock_for(t)
	var t1 := Time.get_ticks_usec()
	if probe:
		m.add_child(probe)
	var t2 := Time.get_ticks_usec()
	if probe:
		probe.free()
	print("PERF   %s: bauen %.0f ms, einhängen %.0f ms" % [t, (t1 - t0) / 1000.0, (t2 - t1) / 1000.0])
	_timed(func() -> void: m.show_tab(t))
	var first := _spike_call
	_timed(func() -> void: m.show_tab(t))
	print("PERF   %s: erster aufruf %.0f ms, sofort nochmal %.0f ms" % [t, first, _spike_call])
	_tab_wait = 60


func _map(m: MainMenu) -> BaseMap:
	if m._mock is BaseTab:
		return (m._mock as BaseTab).map
	return null


## Große sichtbare Flächen auflisten (Überzeichnen finden)
func _dump(n: Node, ind: String) -> void:
	var scr := get_viewport().get_visible_rect().size
	if n is CanvasItem and not (n as CanvasItem).is_visible_in_tree():
		return
	if n is Control:
		var c := n as Control
		var r := c.get_global_rect()
		var frac := r.intersection(Rect2(Vector2.ZERO, scr)).get_area() / (scr.x * scr.y)
		var draws := c is TextureRect and (c as TextureRect).texture != null or c is ColorRect or c is Panel or c is PanelContainer or c.get_script() != null
		if frac > 0.4 and draws:
			print("PERF   gross %.2f %s %s %s" % [frac, c.get_class(), str(c.get_script().resource_path.get_file()) if c.get_script() else "", c.get_path()])
	for ch in n.get_children():
		_dump(ch, ind + " ")


## Welche Bilder gerade geladen sind (alle Bilddateien des Spiels durchgehen)
func _textures() -> void:
	var found: Array = []
	_scan("res://", found)
	found.sort_custom(func(a: Array, b: Array) -> bool: return a[0] > b[0])
	var tot := 0.0
	for f in found:
		tot += f[0]
	print("PERF   geladene bilder: %d, zusammen %.0f MB" % [found.size(), tot])
	for i in mini(25, found.size()):
		print("PERF     %5.1f MB %s" % [found[i][0], found[i][1]])


func _scan(dir: String, out: Array) -> void:
	for f in ResourceLoader.list_directory(dir):
		if f.ends_with("/"):
			if not f.begins_with("."):
				_scan(dir + f, out)
		elif (f.ends_with(".webp") or f.ends_with(".png") or f.ends_with(".jpg")) and ResourceLoader.has_cached(dir + f):
			var t: Texture2D = load(dir + f)
			out.append([t.get_width() * t.get_height() * 4 / 1048576.0, dir + f])


## Was im Kampf an Knoten herumliegt (nach Art), um Ansammlungen zu finden
func _census(root: Node) -> void:
	var counts := {}
	var stack: Array[Node] = [root]
	var vis := 0
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		var key := n.get_class()
		if n.get_script():
			key += ":" + str(n.get_script().resource_path.get_file())
		counts[key] = int(counts.get(key, 0)) + 1
		if n is VisualInstance3D and (n as Node3D).is_visible_in_tree():
			vis += 1
		stack.append_array(n.get_children())
	var keys := counts.keys()
	keys.sort_custom(func(a, b) -> bool: return counts[a] > counts[b])
	var parts := []
	for k in keys.slice(0, 10):
		parts.append("%s=%d" % [k, counts[k]])
	print("PERF   knoten im kampf (sichtbar 3D %d): %s" % [vis, ", ".join(parts)])
