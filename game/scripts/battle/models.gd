class_name Models
## Fertige 3D-Figuren (CC0 von Quaternius, Quellen in models/QUELLEN.md): welcher Held und
## welcher Gegner welches Modell bekommt, Größe, Animationen. Fehlt ein Modell, bauen Held und
## Gegner ihre einfache Form wie bisher.

const HEROES := {
	# v2: Comic-Modelle (GLB) mit eigener Waffe (WeaponSocket → Weapon → Muzzle) bzw. Mündung am Körper und den
	# Animationen Idle, Shoot (beginnt im Anschlag), Victory; Dusty gebaut mit tools/heroes/build_dusty_jo.py,
	# alle anderen (Meshy H2 und H3) mit tools/heroes/build_hero_v2.py
	"dusty": {"file": "heroes_v2/dusty_jo", "gun": "", "v2": true},   # seit 0.10.14 ebenfalls build_hero_v2.py (Meshy-Revolver)
	"iska": {"file": "heroes_v2/iska", "gun": "", "v2": true},
	"brocken": {"file": "heroes_v2/brocken", "gun": "", "v2": true},
	"volta": {"file": "heroes_v2/volta", "gun": "", "v2": true},
	"kalle": {"file": "heroes_v2/kalle", "gun": "", "v2": true},
	"margot": {"file": "heroes_v2/margot", "gun": "", "v2": true},
	"lynx": {"file": "heroes_v2/lynx", "gun": "", "v2": true},
	"fritzi": {"file": "heroes_v2/fritzi", "gun": "", "v2": true},
	"pip": {"file": "heroes_v2/pip", "gun": "", "v2": true},
	"nova": {"file": "heroes_v2/nova", "gun": "", "v2": true},
	# size: Höhe im Verhältnis zu den Menschen (Rollo ist breit und gedrungen)
	"fuenkchen": {"file": "heroes_v2/fuenkchen", "gun": "", "v2": true, "size": 0.95},
	"rollo": {"file": "heroes_v2/rollo", "gun": "", "v2": true, "size": 0.72},
}


## Modell-Eintrag eines Helden
static func hero_info(id: String) -> Dictionary:
	return HEROES.get(id, {})


## Länge der Waffe in Körper-Einheiten (der Held ist etwa 1,5 hoch).
const GUN_LENGTH := {"guns/Revolver": 0.42, "guns/AK": 0.78, "guns/RocketLauncher": 0.95,
	"guns/Shotgun": 0.8, "guns/Sniper": 1.05}

## height: Höhe in Gegner-Einheiten (vor VIS_SCALE); walk/attack: Namen der Animationen.
## stride: Tempo, bei dem die Laufbewegung ohne Rutschen passt, in Körperhöhen pro Sekunde (nur neue
## Modelle, gemessen in Blender). Dann läuft die Bewegung so schnell wie der Gegner wirklich ist.
const ENEMIES := {
	# Comic-Schleimling (tools/monsters/build_schleim.py), freigegeben 04.11.2026; breiter als hoch,
	# daher Höhe so, dass er so breit ist wie die bisherige Figur
	"schleimling": {"file": "enemies_v2/schleimling", "height": 0.85, "walk": "Walk", "attack": "Attack", "v2": true, "stride": 0.62},
	# Comic-Tentakler (tools/monsters/build_tentakler.py), freigegeben 03.11.2026
	"tentakler": {"file": "enemies_v2/tentakler", "height": 1.2, "walk": "Fly", "attack": "Attack", "lift": 0.45, "v2": true},
	# Comic-Panzerkäfer (tools/monsters/build_panzerkaefer.py), freigegeben 03.11.2026; flach und breit,
	# daher geringere Höhe; Schrittlänge 0,075 je 0,8 s bei 0,416 hohem Rohmodell
	"panzerkaefer": {"file": "enemies_v2/panzerkaefer", "height": 0.85, "walk": "Walk", "attack": "Attack", "v2": true, "stride": 0.23},
	# Comic-Schleimmutter (Boss, tools/monsters/build_schleim.py), freigegeben 04.11.2026; Höhe nach Breite wie oben
	"schleimmutter": {"file": "enemies_v2/schleimmutter", "height": 1.45, "walk": "Walk", "attack": "Attack", "v2": true, "stride": 0.6},
	# Comic-Krabbler (tools/monsters/build_zweibeiner.py), freigegeben 04.11.2026
	"krabbler": {"file": "enemies_v2/krabbler", "height": 1.45, "walk": "Walk", "attack": "Attack", "v2": true, "stride": 0.39},
	# Comic-Zombie (tools/monsters/build_zombie.py), freigegeben 03.11.2026
	"zombie": {"file": "enemies_v2/zombie", "height": 1.6, "walk": "Walk", "attack": "Attack", "v2": true, "stride": 0.68},
	# Comic-Brecher (tools/monsters/build_zweibeiner.py), freigegeben 04.11.2026
	"brecher": {"file": "enemies_v2/brecher", "height": 2.0, "walk": "Walk", "attack": "Attack", "v2": true, "stride": 0.59},
	# Comic-Zombie-Koloss (Boss, tools/monsters/build_zweibeiner.py), freigegeben 04.11.2026
	"koloss": {"file": "enemies_v2/koloss", "height": 3.0, "walk": "Walk", "attack": "Attack", "v2": true, "stride": 0.58},
	# Dschungelmond (Level 51–60), Rohmodelle Vorlage_Raw/Monster_Roh/Modelltests_v4, freigegeben 10.11.2026
	# Rankling: tools/monsters/build_schleim.py (Hüpfen wie der Schleimling)
	"rankling": {"file": "enemies_v2/rankling", "height": 0.85, "walk": "Walk", "attack": "Attack", "v2": true, "stride": 0.62},
	# Blütenschnapper: tools/monsters/build_flieger.py (Flügelschlag, Biss), schwebt wie der Tentakler
	"bluetenschnapper": {"file": "enemies_v2/bluetenschnapper", "height": 0.95, "walk": "Fly", "attack": "Attack", "lift": 0.45, "v2": true},
	# Urwaldriese (Boss): tools/monsters/build_zweibeiner.py mit Meshys Skelett, wie der Zombie-Koloss
	"urwaldriese": {"file": "enemies_v2/urwaldriese", "height": 3.0, "walk": "Walk", "attack": "Attack", "v2": true, "stride": 0.58},
	# Ozeanwelt (Level 61–70), Rohmodelle Vorlage_Raw/Monster_Roh/Modelltests_v6, freigegeben 11.11.2026
	# Blubberfisch: tools/monsters/build_flieger.py (Seitenflossen schlagen), schwebt wie der Blütenschnapper
	"blubberfisch": {"file": "enemies_v2/blubberfisch", "height": 0.85, "walk": "Fly", "attack": "Attack", "lift": 0.4, "v2": true},
	# Krabbenpanzer: tools/monsters/build_krabbe.py (sechs Beine, zwei Scheren), flach und breit wie der Panzerkäfer
	"krabbenpanzer": {"file": "enemies_v2/krabbenpanzer", "height": 1.15, "walk": "Walk", "attack": "Attack", "v2": true, "stride": 0.2},
	# Tiefseekrake (Boss): tools/monsters/build_krake.py (acht Fangarme wogen), schwebt
	"tiefseekrake": {"file": "enemies_v2/tiefseekrake", "height": 2.6, "walk": "Fly", "attack": "Attack", "lift": 0.35, "v2": true},
}

## Neue Comic-Gegner zur Prüfung, gebaut, aber noch nicht freigegeben. Aktiv nur mit dem Test-Schalter
## --neue-monster (Prüfbilder: tests/monster_show.gd); nach der Freigabe wandern die Einträge nach ENEMIES.
const ENEMIES_NEU := {}
static var test_new := false


## Daten eines Gegnermodells (mit dem Test-Schalter die neuen, noch nicht freigegebenen). look: Boss je Welt
## (tools/bosse/boss_aufsatz.py, Datei enemies_v2/bosse/<look>.glb): gleiche Animationen, eigene Aufsätze.
static func enemy(kind: String, look := "") -> Dictionary:
	if test_new and ENEMIES_NEU.has(kind):
		return ENEMIES_NEU[kind]
	var d: Dictionary = ENEMIES.get(kind, {})
	if not d.is_empty() and has_look(look):
		d = d.duplicate()
		d["file"] = look_file(look)
		d.merge(LOOK_DATA.get(look, {}), true)
	return d


## Abweichende Maße der Bosse und Monster mit eigenem Körper (Höhe, Schweben, Schrittlänge des Grundmodells).
## Monster: Höhe so, dass der Körper so groß bleibt wie beim Grundmodell (Höhe Grundart × Modellhöhe neu / alt).
const LOOK_DATA := {
	"schleimmutter_krone": {"height": 1.6},
	"frost_yeti": {"height": 2.7, "stride": 0.58},
	"gift_kroete": {"height": 1.75},
	"magma_golem": {"height": 3.3},
	"kristall_kaefer": {"height": 2.4, "stride": 0.23},
	"nebel_geist": {"height": 2.1, "lift": 0.3},
	"schatten_wesen": {"height": 3.2},
	"kristall_riese": {"height": 3.5},
	"frost_schleimling": {"height": 1.0},
	"frost_tentakler": {"height": 1.21},
	"frost_panzerkaefer": {"height": 1.16},
	"lava_krabbler": {"height": 1.51},
	"lava_zombie": {"height": 1.68},
	"lava_brecher": {"height": 2.04},
	"gift_schleimling": {"height": 0.55},
	"gift_zombie": {"height": 1.54},
	"gift_panzerkaefer": {"height": 1.39},
	"kristall_krabbler": {"height": 1.69},
	"kristall_tentakler": {"height": 1.25},
	"kristall_brecher": {"height": 2.18},
	"sand_krabbler": {"height": 1.45},
	"sand_zombie": {"height": 1.6},
	"sand_panzerkaefer": {"height": 1.16},
	"nebel_schleimling": {"height": 0.94, "lift": 0.2},
	"nebel_tentakler": {"height": 1.2},
	"nebel_brecher": {"height": 2.23},
	"schatten_krabbler": {"height": 1.59},
	"schatten_zombie": {"height": 1.73},
	"schatten_brecher": {"height": 2.0},
	"wurm_tentakler": {"height": 1.26},
	"wurm_zombie": {"height": 1.8},
	"wurm_panzerkaefer": {"height": 0.85},
	"ozean_tentakler": {"height": 1.2},
	"ozean_brecher": {"height": 2.16},
	"rosen_schleimling": {"height": 0.6, "lift": 0.15},
	"rosen_zombie": {"height": 1.75},
	"rosen_panzerkaefer": {"height": 0.91},
	"glitzer_krabbler": {"height": 1.6},
	"glitzer_tentakler": {"height": 1.2},
	"glitzer_brecher": {"height": 2.26},
	"sturm_schleimling": {"height": 1.03},
	"sturm_tentakler": {"height": 1.23},
	"sturm_brecher": {"height": 2.25},
	"blitz_krabbler": {"height": 1.68},
	"blitz_zombie": {"height": 1.77},
	"blitz_panzerkaefer": {"height": 1.39},
	"juwelen_schnecke": {"height": 2.17},
	"edelstein_golem": {"height": 3.3},
	"sturm_wolke": {"height": 2.3, "lift": 0.35},
	"donner_riese": {"height": 3.4},
	"schrott_krabbler": {"height": 1.45},
	"schrott_zombie": {"height": 1.6},
	"schrott_brecher": {"height": 2.0},
	"schrott_koloss": {"height": 3.5},
	"robo_schleimling": {"height": 0.76},
	"robo_tentakler": {"height": 1.2},
	"robo_panzerkaefer": {"height": 1.11},
	"fabrik_mutter": {"height": 2.6},
	"himmel_krabbler": {"height": 1.55},
	"himmel_tentakler": {"height": 1.2},
	"himmel_brecher": {"height": 2.24},
	"greifen_waechter": {"height": 3.6},
	"turm_schleimling": {"height": 1.0, "lift": 0.12},
	"turm_zombie": {"height": 1.77},
	"turm_panzerkaefer": {"height": 1.54},
	"wolken_eule": {"height": 2.4},
	"pilz_schleimling": {"height": 1.0},
	"pilz_tentakler": {"height": 1.2},
	"pilz_panzerkaefer": {"height": 1.36},
	"pilz_koenigin": {"height": 3.0},
	"sporen_krabbler": {"height": 1.58},
	"sporen_zombie": {"height": 1.7},
	"sporen_brecher": {"height": 2.16},
	"pilz_riese": {"height": 3.6},
}


## Gibt es für diesen Boss oder dieses Monster ein eigenes Modell? Dann trägt es seine eigenen Farben (keine Weltfärbung).
static func has_look(look: String) -> bool:
	return look_file(look) != ""


## Datei des eigenen Modells (Bosse: enemies_v2/bosse/, Monster je Welt: enemies_v2/monster/), leer = keins
static func look_file(look: String) -> String:
	if look == "":
		return ""
	for dir in ["bosse", "monster"]:
		if ResourceLoader.exists("res://models/enemies_v2/%s/%s.glb" % [dir, look]):
			return "enemies_v2/%s/%s" % [dir, look]
	return ""


static var _scenes := {}
static var _heights := {}
static var _widths := {}   # Breite (größere von x/z) je Höhe 1, gemessen wie die Höhe


static func _scene(file: String) -> PackedScene:
	if not _scenes.has(file):
		var path := "res://models/%s.gltf" % file
		if not ResourceLoader.exists(path):
			path = "res://models/%s.glb" % file
		_scenes[file] = load(path) if ResourceLoader.exists(path) else null
	return _scenes[file]


## Neues Comic-Modell (eigene Waffe, Animationen Idle/Shoot/Victory)
static func is_v2(id: String) -> bool:
	return bool(hero_info(id).get("v2", false)) and has_hero(id)


static func has_hero(id: String) -> bool:
	return not hero_info(id).is_empty() and _scene(hero_info(id)["file"]) != null


static func has_enemy(kind: String) -> bool:
	return not enemy(kind).is_empty() and _scene(enemy(kind)["file"]) != null


## Modell anlegen und auf die gewünschte Höhe bringen. Blickrichtung: -Z (wie das Spiel).
static func make(file: String, height: float, face_minus_z := true) -> Node3D:
	var s := _scene(file)
	if s == null:
		return null
	var n: Node3D = s.instantiate()
	if not _heights.has(file):
		var acc := [null]
		_measure(n, Transform3D.IDENTITY, acc)
		_heights[file] = (acc[0] as AABB).size.y if acc[0] != null else 1.0
		var box: AABB = acc[0] if acc[0] != null else AABB(Vector3.ZERO, Vector3.ONE)
		_widths[file] = maxf(box.size.x, box.size.z) / maxf(0.01, box.size.y)
	var holder := Node3D.new()
	holder.add_child(n)
	n.scale = Vector3.ONE * (height / maxf(0.01, float(_heights[file])))
	if face_minus_z:
		n.rotation.y = PI
	holder.set_meta("model_scale", n.scale.x)
	_loop_all(n)
	return holder


## Halbe Breite eines Gegnermodells in Gegner-Einheiten (vor VIS_SCALE), nach make() bekannt
static func half_width(file: String, height: float) -> float:
	return 0.5 * height * float(_widths.get(file, 1.0))


## Länge der Waffe entlang X messen und Waffe so drehen, dass der Lauf nach -Z zeigt.
static func make_gun(file: String) -> Node3D:
	var s := _scene(file)
	if s == null:
		return null
	var n: Node3D = s.instantiate()
	var acc := [null]
	_measure(n, Transform3D.IDENTITY, acc)
	var a: AABB = acc[0]
	var holder := Node3D.new()
	holder.add_child(n)
	n.scale = Vector3.ONE * (float(GUN_LENGTH.get(file, 0.6)) / maxf(0.01, a.size.x))
	# Lauf liegt bei -X: um Y drehen, damit -X zu -Z wird
	n.rotation.y = -PI * 0.5
	holder.set_meta("front", float(GUN_LENGTH.get(file, 0.6)) * (-a.position.x / a.size.x))
	return holder


## Eine Materialfarbe des Modells ersetzen (z. B. „Skin“, das bei den Figuren nur ein
## dunkler Platzhalter ist). Nur dieses Modell ändert sich, die Vorlage bleibt.
static func recolor(model: Node, material_name: String, color: Color) -> void:
	for mi in model.find_children("*", "MeshInstance3D", true, false):
		var mesh: Mesh = (mi as MeshInstance3D).mesh
		for i in mesh.get_surface_count():
			var mat := mesh.surface_get_material(i)
			if mat and mat.resource_name == material_name and mat is StandardMaterial3D:
				var m: StandardMaterial3D = mat.duplicate()
				m.albedo_color = color
				(mi as MeshInstance3D).set_surface_override_material(i, m)


## Alle Farben eines Modells mit einer Weltfarbe multiplizieren (z. B. Frost = bläulich).
## Eingefärbte Materialien werden geteilt, damit nicht jeder Gegner eigene braucht.
static var _tinted := {}


static func tint_all(model: Node, tint: Color) -> void:
	for mi in model.find_children("*", "MeshInstance3D", true, false):
		var m3 := mi as MeshInstance3D
		for i in m3.mesh.get_surface_count():
			var base := m3.get_surface_override_material(i)
			if base == null:
				base = m3.mesh.surface_get_material(i)
			if not (base is StandardMaterial3D):
				continue
			# Schlüssel aus Aussehen statt Objekt: umgefärbte Haut (Zombies) teilt sich so ein Material
			var sm := base as StandardMaterial3D
			var tex_id := sm.albedo_texture.get_instance_id() if sm.albedo_texture else 0
			var key := "%s|%s|%d|%s" % [sm.resource_name, sm.albedo_color.to_html(), tex_id, tint.to_html()]
			if not _tinted.has(key):
				var m: StandardMaterial3D = base.duplicate()
				m.albedo_color = (base as StandardMaterial3D).albedo_color * tint
				_tinted[key] = m
			m3.set_surface_override_material(i, _tinted[key])


static func player(model: Node) -> AnimationPlayer:
	var list := model.find_children("*", "AnimationPlayer", true, false)
	return list[0] if not list.is_empty() else null


static func skeleton(model: Node) -> Skeleton3D:
	var list := model.find_children("*", "Skeleton3D", true, false)
	return list[0] if not list.is_empty() else null


## Weiße/eisblaue Überlagerung für Treffer und Frost auf alle Teile des Modells legen.
static func add_overlay(model: Node) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.albedo_color = Color(0, 0, 0, 0)
	return m


## Überlagerung ein- oder ausschalten (aus = kein zusätzlicher Zeichendurchgang).
static func set_overlay(model: Node, m: Material) -> void:
	# Ohne Fenster (automatische Tests) gibt es nichts zu sehen; der Ersatz-Renderer meldet dort
	# beim Abschalten der Überlagerung sonst Fehler.
	if DisplayServer.get_name() == "headless":
		return
	for mi in model.find_children("*", "MeshInstance3D", true, false):
		(mi as MeshInstance3D).material_overlay = m


static func _loop_all(model: Node) -> void:
	var ap := player(model)
	if ap == null:
		return
	for lib_name in ap.get_animation_library_list():
		var lib := ap.get_animation_library(lib_name)
		for a in lib.get_animation_list():
			var anim := lib.get_animation(a)
			if a in ["Death", "Jump", "PickUp", "SitDown", "StandUp", "Roll", "Jump_Land"]:
				anim.loop_mode = Animation.LOOP_NONE
			else:
				anim.loop_mode = Animation.LOOP_LINEAR


static func _measure(n: Node, xf: Transform3D, acc: Array) -> void:
	var t := xf
	if n is Node3D:
		t = xf * (n as Node3D).transform
	if n is MeshInstance3D:
		var a: AABB = t * (n as MeshInstance3D).get_aabb()
		acc[0] = a if acc[0] == null else (acc[0] as AABB).merge(a)
	for c in n.get_children():
		_measure(c, t, acc)
