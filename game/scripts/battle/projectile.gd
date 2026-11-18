class_name Projectile
extends Node3D
## Kugel oder Rakete. Fliegt dem Ziel nach; ist das Ziel schon besiegt, fliegt sie zu
## dessen letzter Position.

const AMMO_COLORS := {
	"normal": Color(1.0, 0.85, 0.3),
	"fire": Color(1.0, 0.45, 0.12),
	"ice": Color(0.45, 0.9, 1.0),
}

var battle: Battle
var target: Enemy
var dmg := 0.0
var crit := false
var ammo_type := "normal"
var kind := "bullet"
var pierce := 0
var splash := 0.0
var speed := 45.0
## Effekt-Stil des Helden (Bildfolgen <style>_geschoss / _einschlag); leer = einfache Kugel
var style := ""
## Diese Helden zeigen ihr Geschoss als Strahl (hero.gd/battle.gd), das Projektil selbst bleibt unsichtbar
const BEAM_STYLES := ["fuenkchen"]
## Diese Helden bekommen statt der (zu feinen) Bildfolge eine kräftige Leuchtspur, die mit dem Tempo länger wird
const TRACER_STYLES := ["iska"]
var _sprite: FxSprite
## Rauchfahne der 3D-Rakete (Fx3D), wird beim Einschlag stehen gelassen
var _smoke: CPUParticles3D
var _t := 0.0
var _tracer: Node3D
var _tracer_len := 1.0

var _start := Vector3.ZERO
var _last_target := Vector3.ZERO
var _s := 0.0
var _length := 1.0
var _arc := 0.0


func launch(battle_: Battle, kind_: String, from: Vector3, target_: Enemy, dmg_: float, crit_: bool,
		ammo_type_: String, speed_: float, size: float) -> void:
	battle = battle_
	kind = kind_
	target = target_
	dmg = dmg_
	crit = crit_
	ammo_type = ammo_type_
	speed = speed_
	_start = from
	_last_target = target.aim_point()
	_length = maxf(0.5, from.distance_to(_last_target))
	global_position = from
	var col: Color = AMMO_COLORS.get(ammo_type, AMMO_COLORS["normal"])
	# Gemalte Geschosse (Schusseffekte_<held>_v2): Darstellung steht in der JSON
	var gname := style + "_geschoss"
	# Strahl-Helden (Fünkchen) zeichnen ihren Schuss selbst (hero.gd), das Projektil bleibt dann unsichtbar
	var gi := FxSprite.info(gname) if style != "" and not style in BEAM_STYLES and FxSprite.has(gname) else {}
	match str(gi.get("darstellung", "")):
		"durchschuss", "bogen":
			# eine Linie (Lynx) oder ein Strahl (Kalle) von der Mündung bis zum Ziel, das Projektil selbst bleibt unsichtbar
			FxSprite.span(battle, gname, from, _last_target, {"width": float(gi.get("feste_hoehe_m", 1.0)) / FxSprite.SCALE,
				"alpha": float(gi.get("deckkraft", 1.0))})
			return
		"leuchtspur", "bolzen":
			# kurzer Streifen am Geschoss, Spitze vorn (Anker an der Spitze)
			_sprite = FxSprite.attach(self, gname, {"dir": _last_target - from, "stretch": false,
				"width": float(gi.get("feste_hoehe_m", 1.0)) / FxSprite.SCALE, "length": float(gi.get("groesse_m", 1.0)),
				"frames": int(gi.get("schleife_bilder", gi.get("frames", 1)))})
			return
	if style in TRACER_STYLES and FxSprite.enabled:
		_make_tracer(col)
		return
	if kind == "rocket" and FxSprite.enabled and Fx3D.has(style):
		_arc = clampf(_length * 0.12, 0.6, 2.5)
		_smoke = Fx3D.build_rocket(self)
		return
	if style != "" and FxSprite.has(style + "_geschoss"):
		if not style in BEAM_STYLES:
			_sprite = FxSprite.attach(self, style + "_geschoss", {"dir": _last_target - from, "scale": 0.6 * size if kind != "rocket" else 0.8, "alpha": 0.9})
		return
	if kind == "rocket":
		_arc = clampf(_length * 0.12, 0.6, 2.5)
		var body := Fx.inst(Fx.shared_mesh("rocket_body", func() -> Mesh:
			var m := CylinderMesh.new()
			m.top_radius = 0.08
			m.bottom_radius = 0.08
			m.height = 0.42
			m.radial_segments = 8
			return m), Fx.shared_glow(Color(0.85, 0.25, 0.2)))
		body.rotation.x = PI * 0.5
		add_child(body)
		var tip := Fx.inst(Fx.shared_mesh("rocket_tip", func() -> Mesh:
			var m := CylinderMesh.new()
			m.top_radius = 0.0
			m.bottom_radius = 0.08
			m.height = 0.16
			m.radial_segments = 8
			return m), Fx.shared_glow(Color(0.9, 0.9, 0.9)))
		tip.rotation.x = -PI * 0.5
		tip.position.z = -0.29
		add_child(tip)
		var glow := Fx.inst(Fx.unit_sphere(), Fx.shared_glow(col))
		glow.scale = Vector3.ONE * 0.12
		glow.position.z = 0.26
		add_child(glow)
	else:
		var key := "bullet:%.2f" % size
		var b := Fx.inst(Fx.shared_mesh(key, func() -> Mesh:
			var m := CapsuleMesh.new()
			m.radius = 0.045 * size
			m.height = 0.34 * size
			m.radial_segments = 6
			m.rings = 2
			return m), Fx.shared_glow(col))
		b.rotation.x = PI * 0.5
		add_child(b)


func _process(delta: float) -> void:
	_t += delta
	if _smoke:
		Fx3D.rocket_tick(self, _t)
	if is_instance_valid(target) and target.alive:
		_last_target = target.aim_point()
	_s += speed * delta / _length
	var s := minf(_s, 1.0)
	var pos := _start.lerp(_last_target, s)
	pos.y += _arc * 4.0 * s * (1.0 - s)
	var dir := pos - global_position
	if dir.length() > 0.001:
		look_at(global_position + dir, Vector3.UP)
		if _sprite:
			_sprite.set_dir(dir)
	global_position = pos
	if _tracer:
		# Spur wächst aus der Mündung heraus und bleibt dann gleich lang
		var l := minf(_tracer_len, _s * _length)
		_tracer.scale.z = maxf(0.05, l)
		_tracer.position.z = l * 0.5
	if _s >= 1.0:
		_impact()


## Leuchtspur: heller Kern und farbiger Schein, beide als lange flache Stäbe hinter der Kugel.
## Länge nach Tempo, damit sie auch bei hohem Spieltempo noch zu sehen ist.
func _make_tracer(col: Color) -> void:
	_tracer_len = clampf(speed * 0.03 * maxf(1.0, Engine.time_scale), 0.9, 2.2)
	_tracer = Node3D.new()
	add_child(_tracer)
	# flach liegend (von oben gesehen), außen weicher Schein in zwei Stufen, innen ein schmaler heller Kern
	# Schein kräftiger als die Kugelfarbe, damit er auch auf hellen Brücken (Eis, Wüste) absticht
	var glow := col.lerp(Color(1.0, 0.45, 0.05), 0.25) if ammo_type == "normal" else col
	var halo := Fx.inst(Fx.unit_box(), Fx.shared_glow(glow, 0.18))
	halo.scale = Vector3(0.26, 0.02, 1.06)
	_tracer.add_child(halo)
	var mid := Fx.inst(Fx.unit_box(), Fx.shared_glow(glow, 0.4))
	mid.scale = Vector3(0.13, 0.03, 1.0)
	_tracer.add_child(mid)
	var core := Fx.inst(Fx.unit_box(), Fx.shared_glow(col.lerp(Color(1, 1, 0.95), 0.75)))
	core.scale = Vector3(0.05, 0.04, 0.95)
	_tracer.add_child(core)
	var head := Fx.inst(Fx.unit_sphere(), Fx.shared_glow(Color(1, 1, 0.92)))
	head.scale = Vector3(0.07, 0.04, 0.1)
	add_child(head)


## Einschlag-Bildfolge des Helden am Trefferpunkt (gerichtet in Schussrichtung, wenn die JSON es sagt)
## target_ ohne Typ: das Ziel kann beim Einschlag schon besiegt und freigegeben sein
static func play_impact(battle_: Node, style_: String, at: Vector3, dir: Vector3, target_) -> void:
	var ei := FxSprite.info(style_ + "_einschlag")
	if not bool(ei.get("gerichtet", false)):
		FxSprite.play(battle_, style_ + "_einschlag", at, {"speed": 1.5})
		return
	var eo := {"dir": dir, "speed": float(ei.get("tempo", 1.0))}
	if ei.has("freie_mitte") and is_instance_valid(target_) and target_ is Enemy:
		# Flammen schmiegen sich um den Gegner (Fünkchens Drachenatem): die freie Mitte etwas breiter als der Gegner
		# und flacher als geliefert (laenge_anteil), damit die Bögen den Gegner eng umschließen statt hinter ihm hochzustehen
		var w := clampf(target_.radius() * 2.0 * 1.15 / float(ei["freie_mitte"]), 1.5, 8.0)
		eo.merge({"width": w / FxSprite.SCALE, "length": w * float(ei.get("laenge_anteil", 1.0)), "stretch": false}, true)
	FxSprite.play(battle_, style_ + "_einschlag", at, eo)


func _impact() -> void:
	if _smoke:
		Fx3D.release_smoke(_smoke, battle)
		_smoke = null
	# Strahl-Helden mit gespanntem Atem (Fünkchen) zeigen den Einschlag schon beim Aufprall des Atems (hero.gd)
	var beam_hit := style in BEAM_STYLES and str(FxSprite.info(style + "_geschoss").get("darstellung", "")) == "bogen"
	if kind != "rocket" and style != "" and style != "nova" and not beam_hit:
		play_impact(battle, style, _last_target, _last_target - _start, target)
	if kind == "rocket":
		battle.explode(_last_target, splash, dmg, crit, ammo_type)
	elif is_instance_valid(target) and target.alive:
		battle.apply_hit(target, dmg, crit, ammo_type)
		if pierce > 0:
			battle.pierce_behind(target, pierce, dmg * 0.6, ammo_type)
	queue_free()
