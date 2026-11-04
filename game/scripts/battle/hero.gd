class_name Hero
extends Node3D
## Ein Held hinter dem Energiezaun: zielt selbst, schießt sein Magazin leer und lädt aus dem
## gemeinsamen Munitionsspeicher nach. Gibt der Speicher nichts her, wartet er.

var id := ""
var data: Dictionary
var battle: Battle
## Stufen der Verbesserungen aus der Kartenauswahl.
## Als Verstärkung dazugerufen (Bonus-Schaden, siehe GameData.HERO_TYPE).
var reinforced := false
var mods := {"damage": 0, "rate": 0, "reload": 0, "mag": 0, "crit": 0, "special": 0, "ult": 0}

var magazine: Array[String] = []
var reloading := false
var reload_left := 0.0
var reload_total := 1.0
var waiting_for_ammo := false

var _shot_cd := 0.3
var _t := 0.0
var _recoil := 0.0
var _body: Node3D
var _weapon: Node3D
var _weapon_base := Vector3.ZERO
var _muzzle: Node3D
var _muzzle_flash: MeshInstance3D
var _flash_t := 0.0
var _pipe_mat: StandardMaterial3D
var _pipe: MeshInstance3D
var _pipe_glow := 0.0
var _target_x := 0.0

# --- Superfähigkeit ------------------------------------------------------------
## Je Waffenfamilie: Name, Beschreibung (für die Karte), Dauer in Sekunden (0 = sofort).
const ULTS := {
	"revolver": ["Kugelhagel", "Dreifach schnell, jeder Schuss fächert auf 2 weitere Gegner. Kein Nachladen.", 6.0],
	"mg": ["Dauerfeuer", "Dreifach schnelles Feuer mit hellen Kugeln, ohne Nachladen.", 7.0],
	"rocket": ["Raketensalve", "Feuert sofort einen Schwarm Raketen auf die Gegner.", 0.0],
	"tesla": ["Gewittersturm", "Ein Blitz trifft alle Gegner auf dem Feld.", 0.0],
	"cryo": ["Eiszeit", "Friert alle Gegner fast ganz ein und macht Frostschaden.", 0.0],
	"shotgun": ["Breitseite", "Drei mächtige Schrotsalven, die alle Gegner vorne treffen.", 0.0],
	"sniper": ["Kopfgeldjagd", "Durchschlagende Volltreffer auf die stärksten Gegner.", 0.0],
	"flamer": ["Feuerwalze", "Flammen erfassen alle Gegner in Reichweite und setzen sie in Brand.", 6.0],
	"beam": ["Sternenschweif", "Jeder Atemzug trifft drei Reihen auf einmal.", 6.0],
	"drone": ["Geschützturm", "Repariert die Mauer und stellt einen Turm auf, der mitschießt.", 8.0],
	"cannon": ["Dampfwalze", "Schleudert alle Gegner vor der Mauer weit zurück.", 0.0],
	"gravity": ["Schwarzes Loch", "Zieht alle Gegner zu einem Punkt und bremst sie stark.", 0.0],
}
const ULT_CD := 30.0
const ULT_MAX := 3

var _ult_cd := 0.0
var _ult_t := 0.0
var _ult_ring: MeshInstance3D
var _ult_mat: StandardMaterial3D


func ult_level() -> int:
	return int(mods["ult"])


func ult_ready() -> bool:
	return ult_level() > 0 and _ult_cd <= 0.0 and _ult_t <= 0.0


func ult_active() -> bool:
	return _ult_t > 0.0


## Superfähigkeit auslösen (Antippen des Helden). Gibt false zurück, wenn sie nicht bereit ist.
func activate_ult() -> bool:
	if not ult_ready() or battle == null or not battle.running:
		return false
	var lvl := ult_level()
	var power := 1.0 + 0.5 * (lvl - 1)
	_ult_cd = ULT_CD - 4.0 * (lvl - 1)
	var dur: float = ULTS[family()][2]
	if dur > 0.0:
		_ult_t = dur + 1.0 * (lvl - 1)
	var from := _muzzle.global_position
	var dmg := damage() * power
	match family():
		"rocket":
			var targets := battle.spread_targets(5 + 2 * lvl, battle.pick_target())
			for e in targets:
				battle.fire_rocket(from, e, dmg * 1.6, true, "fire", float(data["splash"]) * 1.2)
		"tesla":
			for e in battle.enemies.duplicate():
				if is_instance_valid(e) and e.alive:
					battle.fire_chain(from, e, dmg * 2.5, true, "normal", 0, Color(0.85, 0.6, 1.0))
		"cryo":
			for e in battle.enemies.duplicate():
				if is_instance_valid(e) and e.alive:
					e.apply_slow(0.9, 3.0 + lvl)
					battle.apply_hit(e, dmg * 1.5, false, "ice")
			Fx.flash(battle, Vector3(0, 1, -8), Color(0.6, 0.95, 1.0), 9.0, 0.6)
		"shotgun":
			for k in 3:
				get_tree().create_timer(0.35 * k, false).timeout.connect(func() -> void:
					if battle == null:
						return
					for e in battle.enemies.duplicate():
						if is_instance_valid(e) and e.alive and e.position.z > -12.0 * battle.z_scale:
							battle.fire_bullet(_muzzle.global_position, e, dmg * 1.4, false, "normal", 0, 34.0, 0.8))
		"drone":
			battle.repair_fence(0.1 + 0.05 * (lvl - 1), 0.0)
			_show_turret(true)
		"cannon":
			for e in battle.enemies.duplicate():
				if is_instance_valid(e) and e.alive and e.position.z > -14.0 * battle.z_scale:
					battle.apply_hit(e, dmg * 2.0, false, "normal")
					e.knockback((4.0 + lvl) * battle.z_scale)
			Fx.flash(battle, Vector3(0, 1, -4), Color(1.0, 0.7, 0.3), 8.0, 0.5)
		"gravity":
			var t := battle.pick_target()
			var c := t.global_position if t else Vector3(0, 0, -8.0 * battle.z_scale)
			battle.gravity_well(c, 5.0 + lvl, dmg * 2.0, true, "normal", 0.85, 0.7, 3.0 + lvl)
		"sniper":
			var strong: Array = battle.enemies.filter(func(e: Enemy) -> bool: return is_instance_valid(e) and e.alive)
			strong.sort_custom(func(a: Enemy, b: Enemy) -> bool: return a.hp > b.hp)
			for k in mini(4 + lvl, strong.size()):
				# Nur die Kennung merken: der Gegner kann bis zum Schuss schon besiegt sein
				var eid: int = (strong[k] as Enemy).get_instance_id()
				get_tree().create_timer(0.18 * k, false).timeout.connect(func() -> void:
					var e := instance_from_id(eid) as Enemy
					if battle and e and e.alive:
						battle.fire_bullet(_muzzle.global_position, e, dmg * 4.0, true, "normal", 3, 70.0, 1.6))
	battle.add_shake(0.35)
	Fx.flash(battle, global_position + Vector3(0, 1.4, 0), Color(1.0, 0.85, 0.3), 2.5, 0.35)
	var sfx := get_node_or_null("/root/Sfx")
	if sfx:
		sfx.play("whoosh", 0.0, 2.0)
	return true


## Pips Geschützturm (Superfähigkeit): steht neben ihm, solange sie läuft
var _turret: Node3D


func _show_turret(on: bool) -> void:
	if on and _turret == null:
		_turret = Node3D.new()
		var base := Fx.cylinder(0.3, 0.38, 0.35, Fx.mat(Color(0.85, 0.82, 0.75), 0.2, 0.5, 0.4), 10)
		base.position.y = 0.18
		_turret.add_child(base)
		var head := Fx.box(Vector3(0.4, 0.3, 0.45), Fx.mat(Color(0.2, 0.7, 0.75), 0.2, 0.4, 0.4))
		head.position.y = 0.5
		_turret.add_child(head)
		var gun := Fx.cylinder(0.06, 0.06, 0.5, Fx.mat(Color(0.3, 0.32, 0.36), 0.0, 0.8, 0.3), 8)
		gun.rotation.x = PI * 0.5
		gun.position = Vector3(0, 0.5, -0.4)
		_turret.add_child(gun)
		var eye := Fx.box(Vector3(0.24, 0.06, 0.02), Fx.mat(Color(0.3, 1.0, 1.0), 3.0))
		eye.position = Vector3(0, 0.55, -0.23)
		_turret.add_child(eye)
		battle.add_child(_turret)
		_turret.global_position = global_position + Vector3(1.4, 0, -0.6)
		Fx.flash(battle, _turret.global_position + Vector3(0, 0.5, 0), Color(0.3, 1.0, 1.0), 1.5, 0.35)
	elif not on and _turret:
		_turret.queue_free()
		_turret = null


func _exit_tree() -> void:
	if is_instance_valid(_turret):
		_turret.queue_free()


func _update_ult(delta: float) -> void:
	_ult_cd = maxf(0.0, _ult_cd - delta)
	_ult_t = maxf(0.0, _ult_t - delta)
	if _turret and _ult_t <= 0.0:
		_show_turret(false)
	if _ult_ring == null:
		return
	var ready := ult_ready()
	_ult_ring.visible = ready or ult_active()
	if _ult_ring.visible:
		var pulse := 1.0 + 0.12 * sin(_t * 6.0)
		_ult_ring.scale = Vector3(pulse, 1.0, pulse) * (1.25 if ult_active() else 1.0)
		_ult_mat.emission_energy_multiplier = 2.5 + (2.0 if ult_active() else sin(_t * 6.0))


func _build_ult_ring() -> void:
	_ult_mat = Fx.mat(Color(1.0, 0.8, 0.25), 3.0)
	_ult_ring = Fx.torus(0.78, 0.9, _ult_mat)
	_ult_ring.position.y = 0.26
	_ult_ring.visible = false
	add_child(_ult_ring)


## Darstellungsgröße der Helden.
const VIS_SCALE := 2.0
## Helden schräg zur Kamera drehen (aus: sie schauen beim Schießen zu den Gegnern)
const FACE_CAMERA := false


## Ton beim Schuss je Waffenfamilie.
const SHOT_SOUND := {"revolver": "shot", "mg": "shot_light", "rocket": "launch", "tesla": "zap",
	"cryo": "frost", "shotgun": "shot_heavy", "sniper": "shot_heavy", "flamer": "flame",
	"beam": "zap", "drone": "shot_light", "cannon": "shot_heavy", "gravity": "whoosh"}


func setup(id_: String, battle_: Battle) -> void:
	id = id_
	battle = battle_
	data = GameData.HEROES[id]
	scale = Vector3.ONE * VIS_SCALE * _field_scale()
	_build_visual()
	_build_ult_ring()
	magazine.clear()
	for i in mag_size():
		magazine.append("normal")


# --- Werte (Grundwert plus Karten) -----------------------------------------

func damage() -> float:
	var meta: float = battle.hero_damage.get(id, 1.0) if battle else 1.0
	var team: float = 1.0 + (battle.team_aura if battle else 0.0)
	var join := 1.0 + (GameData.REINFORCE_DAMAGE if reinforced else 0.0)
	return float(data["damage"]) * (1.0 + 0.2 * mods["damage"]) * meta * team * join


func interval() -> float:
	# Energiekern entladen: doppelt so schnell feuern
	var boost := 2.0 if battle and battle.overdrive_left > 0.0 else 1.0
	return float(data["interval"]) / (1.0 + 0.15 * mods["rate"]) / boost


func reload_time() -> float:
	var extra: float = battle.bonus_reload if battle else 0.0
	return float(data["reload"]) / (1.0 + 0.25 * mods["reload"] + extra)


func mag_size() -> int:
	var team: int = battle.team_mag if battle else 0
	return int(round(float(data["mag"]) * (1.0 + 0.5 * mods["mag"]))) + team


func ammo_cost() -> int:
	return int(ceil(float(data["cost"]) * (1.0 + 0.5 * mods["mag"])))


func crit_chance() -> float:
	var extra: float = battle.bonus_crit if battle else 0.0
	return 0.05 + 0.1 * mods["crit"] + extra


func family() -> String:
	return data["family"]


## Höhe über dem Boden für die Magazinanzeige.
func top_height() -> float:
	return 2.0 * VIS_SCALE * _field_scale()


func _field_scale() -> float:
	return Battle.BACKDROP_HERO_SCALE if battle and battle.field != "" else 1.0


## Für Porträts: Munitionsleitung ausblenden.
func hide_pipe() -> void:
	if _pipe:
		_pipe.visible = false


func slide_to(x: float) -> void:
	_target_x = x


# --- Ablauf ----------------------------------------------------------------

func _process(delta: float) -> void:
	_t += delta
	position.x = move_toward(position.x, _target_x, delta * 6.0)
	_animate(delta)
	if battle == null or not battle.running:
		return
	_update_ult(delta)
	if ult_active():
		_shot_cd -= delta
		var t2 := battle.pick_target()
		if t2:
			_aim_at(t2.global_position, delta)
			if _shot_cd <= 0.0:
				_fire(t2)
				_shot_cd = interval() / 3.0
		return
	if reloading:
		reload_left -= delta * (8.0 if battle.overdrive_left > 0.0 else 1.0)
		if reload_left <= 0.0:
			reloading = false
		return
	if magazine.is_empty():
		_try_reload()
		return
	_shot_cd -= delta
	var target := battle.pick_target()
	if target == null:
		return
	_aim_at(target.global_position, delta)
	if _shot_cd <= 0.0:
		_fire(target)
		_shot_cd = interval()


func _try_reload() -> void:
	var cost := ammo_cost()
	var balls := battle.ammo.take(cost)
	if balls.is_empty():
		waiting_for_ammo = true
		return
	waiting_for_ammo = false
	var shots := mag_size()
	magazine.clear()
	for i in shots:
		var idx := mini(int(floor(float(i) * balls.size() / shots)), balls.size() - 1)
		magazine.append(balls[idx])
	reloading = true
	reload_total = reload_time()
	reload_left = reload_total
	_pipe_glow = 1.0


func _fire(target: Enemy) -> void:
	# Während einer Daueraktion (Superfähigkeit) wird keine Munition verbraucht
	var ammo_type: String = "normal" if ult_active() or magazine.is_empty() else magazine.pop_front()
	var crit := randf() < crit_chance()
	var dmg := damage() * (2.0 if crit else 1.0)
	var from := _muzzle.global_position
	Sfx.play(SHOT_SOUND.get(family(), "shot"))
	var style := str(FX_STYLE.get(family(), ""))
	battle.shot_style = style
	_muzzle_fx(style, from, target)
	match family():
		"revolver":
			battle.fire_bullet(from, target, dmg, crit, ammo_type, 0, 30.0, 1.0)
			if magazine.is_empty() or ult_active():
				var extra := 2 + 2 * int(mods["special"])
				for other in battle.spread_targets(extra, target):
					battle.fire_bullet(from, other, dmg * 0.8, false, ammo_type, 0, 28.0, 0.9)
		"mg":
			if ult_active():
				battle.fire_bullet(from, target, dmg, crit, "normal", int(mods["special"]) + 1, 42.0, 1.1)
			else:
				battle.fire_bullet(from, target, dmg, crit, ammo_type, int(mods["special"]), 34.0, 0.75)
		"rocket":
			var radius: float = float(data["splash"]) * (1.0 + 0.25 * int(mods["special"]))
			battle.fire_rocket(from, target, dmg, crit, ammo_type, radius)
		"tesla":
			battle.fire_chain(from, target, dmg, crit, ammo_type, int(data["chain"]) + int(mods["special"]))
		"cryo":
			# Frost-Strahl: immer Eismunition, springt mit der Spezialkarte auf Nachbarn über
			battle.fire_chain(from, target, dmg, crit, "ice", int(mods["special"]), Color(0.55, 0.95, 1.0))
		"shotgun":
			var pellets := int(data["pellets"]) + int(mods["special"])
			battle.fire_bullet(from, target, dmg, crit, ammo_type, 0, 32.0, 0.7)
			for other in battle.spread_targets(pellets - 1, target):
				battle.fire_bullet(from, other, dmg, false, ammo_type, 0, 30.0, 0.7)
		"sniper":
			battle.fire_bullet(from, target, dmg, crit, ammo_type, int(data["pierce"]) + int(mods["special"]), 60.0, 1.3)
		"flamer":
			var cone: float = float(data["cone"]) * (1.0 + 0.2 * int(mods["special"])) * (2.2 if ult_active() else 1.0)
			battle.flame(from, target, dmg, crit, ammo_type, cone)
		"beam":
			# Sternenatem: durchschlägt die ganze Reihe; mit der Superfähigkeit drei Reihen
			var pierce := int(data["pierce"]) + int(mods["special"])
			var far := from + (target.aim_point() - from).normalized() * maxf(8.0, from.distance_to(target.aim_point()) + 4.0)
			if FxSprite.has("fuenkchen_geschoss"):
				FxSprite.beam(battle, "fuenkchen_geschoss", from, far, 0.25, 0.6, 0.7)
			elif FxP.enabled:
				FxP.beam(battle, "fuenkchen", from, far)
			battle.fire_bullet(from, target, dmg, crit, ammo_type, pierce, 60.0, 1.3)
			if ult_active():
				for other in battle.spread_targets(2, target):
					battle.fire_bullet(from, other, dmg, false, ammo_type, pierce, 60.0, 1.3)
		"drone":
			battle.fire_bullet(from, target, dmg, crit, ammo_type, 0, 34.0, 0.8)
			battle.repair_fence(float(data["repair"]) * (1.0 + 0.5 * int(mods["special"])), 0.0)
			_repair_n += 1
			if _repair_n % 4 == 0:
				battle.fence_heal_fx("pip_reparatur", [global_position.x])
			if ult_active() and _turret:
				for other in battle.spread_targets(2, target):
					battle.fire_bullet(_turret.global_position + Vector3(0, 0.6, 0), other, dmg * 1.2, false, "normal", 0, 34.0, 0.8)
		"cannon":
			# Wuchtgeschoss: stößt den getroffenen Gegner zurück (beim Auftreffen)
			battle.fire_bullet(from, target, dmg, crit, ammo_type, 0, 30.0, 1.4)
			var push: float = float(data["push"]) * (1.0 + 0.25 * int(mods["special"])) * battle.z_scale
			var eid := target.get_instance_id()
			var travel := from.distance_to(target.aim_point()) / 30.0
			get_tree().create_timer(travel, false).timeout.connect(func() -> void:
				var e := instance_from_id(eid) as Enemy
				if e and e.alive:
					e.knockback(push))
		"gravity":
			# Schwerkraftfeld am Ziel: zieht die Gegner dort zusammen und bremst sie
			var r: float = float(data["radius"]) * (1.0 + 0.2 * int(mods["special"]))
			battle.fire_bullet(from, target, 0.0, false, ammo_type, 0, 32.0, 1.0)
			var eid2 := target.get_instance_id()
			var travel2 := from.distance_to(target.aim_point()) / 32.0
			get_tree().create_timer(travel2, false).timeout.connect(func() -> void:
				var e := instance_from_id(eid2) as Enemy
				if battle and e and e.alive:
					battle.gravity_well(e.global_position, r, dmg, crit, ammo_type, 0.5, 0.35, 1.2))
	battle.shot_style = ""
	_recoil = 1.0
	_flash_t = 0.0 if FxSprite.has(style + "_muendung") or (FxP.enabled and style != "") else 0.06
	_shot_anim()


## Bildfolgen je Held (Präfix in game/fx): Mündung, Geschoss, Einschlag
const FX_STYLE := {"revolver": "dusty_jo", "mg": "iska", "rocket": "brocken", "tesla": "volta", "cryo": "kalle",
	"shotgun": "margot", "sniper": "lynx", "flamer": "fritzi", "beam": "fuenkchen", "drone": "pip", "cannon": "rollo",
	"gravity": "nova"}
var _repair_n := 0
var _muzzle_n := 0


## Mündungsfeuer als Bildfolge in Schussrichtung (Brocken: Rauchstoß nach hinten); Iska wechselt drei Varianten
func _muzzle_fx(style: String, from: Vector3, target: Enemy) -> void:
	if style == "":
		return
	if FxP.enabled:
		FxP.muzzle(battle, style, from, target.aim_point() - from)
		return
	var name := style + "_muendung"
	if style == "iska":
		_muzzle_n += 1
		var v := _muzzle_n % 3
		if v > 0 and FxSprite.has("iska_muendung_variante_%d" % (v + 1)):
			name = "iska_muendung_variante_%d" % (v + 1)
	if not FxSprite.has(name):
		return
	var d := target.aim_point() - from
	if style == "brocken":
		d = -d
	FxSprite.play(battle, name, from, {"dir": d, "speed": 2.4, "scale": 0.8})


func _aim_at(target_pos: Vector3, delta: float) -> void:
	var d := target_pos - global_position
	var yaw := atan2(-d.x, -d.z)
	# Wie im Mockup: Held schräg zur Kamera gedreht (Gesicht und Waffe sichtbar), zum Ziel hin geneigt
	if FACE_CAMERA:
		yaw += PI * 0.78 * (1.0 if d.x >= 0.0 else -1.0)
	rotation.y = lerp_angle(rotation.y, yaw, minf(1.0, delta * 12.0))


func _animate(delta: float) -> void:
	_settle_anim()
	if _glb_muzzle and is_instance_valid(_glb_muzzle):
		_muzzle.global_position = _glb_muzzle.global_position
	_body.position.y = 0.22 + sin(_t * 2.2) * 0.015
	_recoil = maxf(0.0, _recoil - delta * 9.0)
	var kick := 0.22 if family() == "rocket" else 0.12
	_weapon.position = _weapon_base + Vector3(0, 0, _recoil * kick)
	if reloading:
		var p := 1.0 - reload_left / reload_total
		_weapon.rotation.x = -sin(p * PI) * 0.9
	else:
		_weapon.rotation.x = move_toward(_weapon.rotation.x, 0.0, delta * 6.0)
	_flash_t -= delta
	_muzzle_flash.visible = _flash_t > 0.0
	if _muzzle_flash.visible:
		_muzzle_flash.scale = Vector3.ONE * Fx.vis_rng.randf_range(0.8, 1.3)
	if _pipe_glow > 0.0:
		_pipe_glow = maxf(0.0, _pipe_glow - delta * 1.5)
		_pipe_mat.emission = Color(0.2, 0.8, 1.0) * (0.4 + _pipe_glow * 3.0)


# --- Aussehen --------------------------------------------------------------

func _build_visual() -> void:
	var col: Color = data["color"]
	var skin: Color = data["skin"]
	var dark := Color(0.16, 0.17, 0.22)
	# Geschützsockel der Station
	# (Sockel entfällt: im Mockup stehen die Helden frei vor der Mauer, den Ring zeichnet die Anzeige)
	var base := Fx.cylinder(0.72, 0.82, 0.22, Fx.mat(Color(0.25, 0.27, 0.33), 0.0, 0.7, 0.35), 6)
	base.position.y = 0.11
	base.visible = false
	add_child(base)
	var rim := Fx.cylinder(0.74, 0.74, 0.04, Fx.mat(Color(0.2, 0.85, 1.0), 2.0), 6)
	rim.position.y = 0.23
	rim.visible = false
	add_child(rim)
	# Munitionsleitung zur Kugelbahn
	_pipe_mat = Fx.mat(Color(0.2, 0.8, 1.0), 0.4, 0.3, 0.3)
	var pipe := Fx.cylinder(0.08, 0.08, 6.0, _pipe_mat, 8)
	_pipe = pipe
	pipe.visible = false
	pipe.rotation.x = PI * 0.5
	pipe.position = Vector3(0, 0.08, 3.2)
	add_child(pipe)

	_body = Node3D.new()
	add_child(_body)
	var big := 1.12 if family() == "rocket" else 1.0
	_body.scale = Vector3.ONE * big
	if Models.has_hero(id):
		_build_model()
	else:
		_build_simple_body(col, skin, dark)

	# Waffe
	_weapon = Node3D.new()
	_body.add_child(_weapon)
	_muzzle = Node3D.new()
	_weapon.add_child(_muzzle)
	var metal := Fx.mat(Color(0.3, 0.32, 0.36), 0.0, 0.85, 0.3)
	match family():
		"revolver":
			_weapon_base = Vector3(0.24, 0.92, -0.42)
			var grip := Fx.box(Vector3(0.07, 0.16, 0.08), Fx.mat(Color(0.45, 0.25, 0.1)))
			grip.position = Vector3(0, -0.08, 0.06)
			grip.rotation.x = 0.3
			_weapon.add_child(grip)
			var drum := Fx.cylinder(0.065, 0.065, 0.11, metal, 8)
			drum.rotation.x = PI * 0.5
			_weapon.add_child(drum)
			var barrel := Fx.cylinder(0.03, 0.035, 0.32, metal, 8)
			barrel.rotation.x = PI * 0.5
			barrel.position.z = -0.2
			_weapon.add_child(barrel)
			_muzzle.position = Vector3(0, 0, -0.38)
		"mg":
			_weapon_base = Vector3(0.1, 0.86, -0.4)
			var body := Fx.box(Vector3(0.14, 0.16, 0.62), metal)
			_weapon.add_child(body)
			var mag := Fx.box(Vector3(0.1, 0.18, 0.14), Fx.mat(Color(0.95, 0.75, 0.2)))
			mag.position = Vector3(0, -0.14, -0.05)
			_weapon.add_child(mag)
			var barrel := Fx.cylinder(0.035, 0.04, 0.5, metal, 8)
			barrel.rotation.x = PI * 0.5
			barrel.position.z = -0.52
			_weapon.add_child(barrel)
			_muzzle.position = Vector3(0, 0, -0.8)
		"rocket":
			_weapon_base = Vector3(0.3, 1.15, -0.15)
			var tube := Fx.cylinder(0.13, 0.13, 1.1, Fx.mat(Color(0.3, 0.42, 0.25), 0.0, 0.3, 0.5), 12)
			tube.rotation.x = PI * 0.5
			_weapon.add_child(tube)
			for z in [-0.42, 0.42]:
				var band := Fx.cylinder(0.145, 0.145, 0.08, Fx.mat(Color(0.9, 0.25, 0.15)), 12)
				band.rotation.x = PI * 0.5
				band.position.z = z
				_weapon.add_child(band)
			var sight := Fx.box(Vector3(0.05, 0.1, 0.12), metal)
			sight.position = Vector3(-0.12, 0.08, -0.2)
			_weapon.add_child(sight)
			_muzzle.position = Vector3(0, 0, -0.6)
		"tesla":
			_weapon_base = Vector3(0.18, 0.9, -0.4)
			var body := Fx.box(Vector3(0.12, 0.14, 0.4), metal)
			_weapon.add_child(body)
			var orb := Fx.sphere(0.1, Fx.mat(Color(0.8, 0.5, 1.0), 4.0), 10, 6)
			orb.position.z = -0.28
			_weapon.add_child(orb)
			for k in 2:
				var ring := Fx.torus(0.06, 0.1, Fx.mat(Color(0.75, 0.4, 1.0), 2.0))
				ring.rotation.x = PI * 0.5
				ring.position.z = -0.05 - k * 0.1
				_weapon.add_child(ring)
			_muzzle.position = Vector3(0, 0, -0.36)
	match family():
		"cryo":
			_weapon_base = Vector3(0.18, 0.9, -0.4)
			var body := Fx.cylinder(0.08, 0.1, 0.45, Fx.mat(Color(0.75, 0.85, 0.95), 0.0, 0.6, 0.3), 10)
			body.rotation.x = PI * 0.5
			_weapon.add_child(body)
			var crystal := Fx.sphere(0.1, Fx.mat(Color(0.6, 0.95, 1.0), 3.0), 6, 3)
			crystal.position.z = -0.3
			_weapon.add_child(crystal)
			_muzzle.position = Vector3(0, 0, -0.38)
		"shotgun":
			_weapon_base = Vector3(0.16, 0.88, -0.4)
			for sx in [-0.035, 0.035]:
				var barrel := Fx.cylinder(0.035, 0.035, 0.62, metal, 8)
				barrel.rotation.x = PI * 0.5
				barrel.position = Vector3(sx, 0, -0.2)
				_weapon.add_child(barrel)
			var stock := Fx.box(Vector3(0.1, 0.12, 0.3), Fx.mat(Color(0.45, 0.25, 0.1)))
			stock.position.z = 0.15
			_weapon.add_child(stock)
			_muzzle.position = Vector3(0, 0, -0.52)
		"sniper":
			_weapon_base = Vector3(0.14, 0.92, -0.45)
			var barrel := Fx.cylinder(0.03, 0.035, 1.0, metal, 8)
			barrel.rotation.x = PI * 0.5
			barrel.position.z = -0.35
			_weapon.add_child(barrel)
			var stock := Fx.box(Vector3(0.09, 0.13, 0.4), Fx.mat(Color(0.3, 0.35, 0.25)))
			stock.position.z = 0.12
			_weapon.add_child(stock)
			var scope := Fx.cylinder(0.045, 0.045, 0.3, metal, 8)
			scope.rotation.x = PI * 0.5
			scope.position = Vector3(0, 0.09, -0.05)
			_weapon.add_child(scope)
			_muzzle.position = Vector3(0, 0, -0.86)
		"flamer":
			_weapon_base = Vector3(0.16, 0.86, -0.4)
			var nozzle := Fx.cylinder(0.06, 0.08, 0.55, metal, 10)
			nozzle.rotation.x = PI * 0.5
			nozzle.position.z = -0.12
			_weapon.add_child(nozzle)
			var pilot := Fx.sphere(0.05, Fx.mat(Color(0.4, 0.7, 1.0), 4.0), 6, 3)
			pilot.position = Vector3(0, -0.06, -0.4)
			_weapon.add_child(pilot)
			_muzzle.position = Vector3(0, 0, -0.42)
	match family():
		"beam":
			# Drache: kein Werkzeug, der Atem kommt aus dem Maul
			_weapon_base = Vector3(0, 1.22, -0.3)
			_muzzle.position = Vector3(0, 0, -0.12)
		"drone":
			_weapon_base = Vector3(0.2, 0.9, -0.38)
			var wrench := Fx.box(Vector3(0.06, 0.06, 0.42), metal)
			_weapon.add_child(wrench)
			var jaw := Fx.torus(0.05, 0.1, metal)
			jaw.rotation.x = PI * 0.5
			jaw.position.z = -0.24
			_weapon.add_child(jaw)
			_muzzle.position = Vector3(0, 0, -0.32)
		"cannon":
			_weapon_base = Vector3(0, 1.0, -0.35)
			var barrel := Fx.cylinder(0.1, 0.11, 0.7, metal, 12)
			barrel.rotation.x = PI * 0.5
			barrel.position.z = -0.2
			_weapon.add_child(barrel)
			var ring := Fx.torus(0.09, 0.14, Fx.mat(Color(0.95, 0.55, 0.15)))
			ring.rotation.x = PI * 0.5
			ring.position.z = -0.52
			_weapon.add_child(ring)
			_muzzle.position = Vector3(0, 0, -0.58)
		"gravity":
			_weapon_base = Vector3(0.22, 0.9, -0.36)
			var fist := Fx.box(Vector3(0.2, 0.2, 0.24), Fx.mat(Color(0.5, 0.3, 0.85), 0.2, 0.4, 0.4))
			_weapon.add_child(fist)
			var core := Fx.sphere(0.07, Fx.mat(Color(0.3, 1.0, 1.0), 3.5), 8, 4)
			core.position.z = -0.13
			_weapon.add_child(core)
			_muzzle.position = Vector3(0, 0, -0.18)
	if _model:
		_fit_weapon_to_model()
	_weapon.position = _weapon_base
	_muzzle_flash = Fx.sphere(0.11, Fx.glow_mat(Color(1.0, 0.9, 0.5)), 8, 4)
	_muzzle.add_child(_muzzle_flash)
	_muzzle_flash.visible = false


## Einfache Figur aus Grundformen (wenn kein fertiges Modell da ist).
func _build_simple_body(col: Color, skin: Color, dark: Color) -> void:
	for sx in [-0.12, 0.12]:
		var leg := Fx.capsule(0.1, 0.46, Fx.mat(dark))
		leg.position = Vector3(sx, 0.23, 0)
		_body.add_child(leg)
	var torso := Fx.capsule(0.25, 0.72, Fx.mat(col, 0.05, 0.1, 0.55))
	torso.position.y = 0.74
	_body.add_child(torso)
	var belt := Fx.cylinder(0.255, 0.255, 0.07, Fx.mat(Color(0.12, 0.1, 0.08)))
	belt.position.y = 0.55
	_body.add_child(belt)
	var pack := Fx.box(Vector3(0.34, 0.38, 0.16), Fx.mat(Color(0.3, 0.32, 0.38), 0.0, 0.5, 0.4))
	pack.position = Vector3(0, 0.82, 0.24)
	_body.add_child(pack)
	var lamp := Fx.box(Vector3(0.2, 0.05, 0.02), Fx.mat(Color(0.2, 0.9, 1.0), 2.5))
	lamp.position = Vector3(0, 0.92, 0.33)
	_body.add_child(lamp)
	var head := Fx.sphere(0.21, Fx.mat(skin), 14, 8)
	head.position.y = 1.24
	_body.add_child(head)
	for sx in [-1.0, 1.0]:
		var arm := Fx.capsule(0.075, 0.42, Fx.mat(col.darkened(0.15)))
		arm.position = Vector3(0.24 * sx, 0.92, -0.12)
		arm.rotation.x = -1.1
		arm.rotation.z = -0.25 * sx
		_body.add_child(arm)

	match family():
		"revolver":
			var brim := Fx.cylinder(0.4, 0.4, 0.035, Fx.mat(Color(0.45, 0.27, 0.12)), 16)
			brim.position.y = 1.36
			_body.add_child(brim)
			var crown := Fx.cylinder(0.19, 0.22, 0.2, Fx.mat(Color(0.5, 0.3, 0.14)), 12)
			crown.position.y = 1.47
			_body.add_child(crown)
			var scarf := Fx.cylinder(0.2, 0.24, 0.08, Fx.mat(Color(0.85, 0.2, 0.2)))
			scarf.position.y = 1.08
			_body.add_child(scarf)
		"mg":
			var helmet := Fx.sphere(0.235, Fx.mat(Color(0.12, 0.22, 0.45), 0.0, 0.6, 0.3), 14, 8)
			helmet.scale = Vector3(1.0, 0.8, 1.0)
			helmet.position.y = 1.31
			_body.add_child(helmet)
			var visor := Fx.box(Vector3(0.34, 0.07, 0.1), Fx.mat(Color(0.2, 0.9, 1.0), 2.5))
			visor.position = Vector3(0, 1.25, -0.17)
			_body.add_child(visor)
			for sx in [-1.0, 1.0]:
				var pad := Fx.sphere(0.13, Fx.mat(Color(0.12, 0.22, 0.45), 0.0, 0.6, 0.3), 10, 5)
				pad.position = Vector3(0.27 * sx, 1.05, 0)
				_body.add_child(pad)
		"rocket":
			var helmet := Fx.sphere(0.24, Fx.mat(Color(1.0, 0.78, 0.1), 0.05, 0.2, 0.4), 14, 8)
			helmet.scale = Vector3(1.05, 0.75, 1.1)
			helmet.position.y = 1.32
			_body.add_child(helmet)
			var head_lamp := Fx.cylinder(0.06, 0.06, 0.06, Fx.mat(Color(1.0, 1.0, 0.7), 4.0))
			head_lamp.rotation.x = PI * 0.5
			head_lamp.position = Vector3(0, 1.36, -0.24)
			_body.add_child(head_lamp)
			var beard := Fx.sphere(0.14, Fx.mat(Color(0.35, 0.2, 0.1)), 10, 5)
			beard.position = Vector3(0, 1.12, -0.1)
			_body.add_child(beard)
		"tesla":
			var hair := Fx.sphere(0.22, Fx.mat(Color(0.95, 0.95, 1.0), 0.1), 10, 6)
			hair.scale = Vector3(1.2, 0.8, 1.2)
			hair.position.y = 1.36
			_body.add_child(hair)
			for sx in [-0.09, 0.09]:
				var goggle := Fx.cylinder(0.06, 0.06, 0.05, Fx.mat(Color(0.75, 0.4, 1.0), 3.0))
				goggle.rotation.x = PI * 0.5
				goggle.position = Vector3(sx, 1.29, -0.2)
				_body.add_child(goggle)
			var coil := Fx.cylinder(0.05, 0.05, 0.55, Fx.mat(Color(0.5, 0.5, 0.55), 0.0, 0.8, 0.3))
			coil.position = Vector3(0, 1.15, 0.28)
			_body.add_child(coil)
			for k in 3:
				var ring := Fx.torus(0.07, 0.12, Fx.mat(Color(0.75, 0.4, 1.0), 2.5))
				ring.position = Vector3(0, 1.0 + k * 0.13, 0.28)
				_body.add_child(ring)

	match family():
		"cryo":
			var beanie := Fx.sphere(0.23, Fx.mat(Color(0.2, 0.55, 0.85)), 12, 6)
			beanie.scale = Vector3(1.0, 0.7, 1.0)
			beanie.position.y = 1.33
			_body.add_child(beanie)
			var pom := Fx.sphere(0.07, Fx.mat(Color(1, 1, 1)), 8, 4)
			pom.position.y = 1.5
			_body.add_child(pom)
			var tank := Fx.cylinder(0.11, 0.11, 0.4, Fx.mat(Color(0.6, 0.85, 1.0), 1.5), 10)
			tank.position = Vector3(0, 0.85, 0.3)
			_body.add_child(tank)
		"shotgun":
			var cap := Fx.cylinder(0.2, 0.22, 0.14, Fx.mat(Color(0.12, 0.15, 0.3)), 14)
			cap.position.y = 1.4
			_body.add_child(cap)
			var peak := Fx.box(Vector3(0.3, 0.03, 0.16), Fx.mat(Color(0.08, 0.08, 0.1)))
			peak.position = Vector3(0, 1.34, -0.2)
			_body.add_child(peak)
			var badge := Fx.sphere(0.04, Fx.mat(Color(1.0, 0.85, 0.3), 2.0), 6, 3)
			badge.position = Vector3(0, 1.42, -0.2)
			_body.add_child(badge)
			var hair := Fx.sphere(0.2, Fx.mat(Color(0.92, 0.92, 0.95)), 10, 5)
			hair.scale = Vector3(1.1, 0.6, 1.0)
			hair.position = Vector3(0, 1.2, 0.06)
			_body.add_child(hair)
		"sniper":
			var hood := Fx.sphere(0.25, Fx.mat(Color(0.25, 0.35, 0.2)), 12, 6)
			hood.scale = Vector3(1.0, 0.9, 1.05)
			hood.position = Vector3(0, 1.28, 0.03)
			_body.add_child(hood)
			var scope_eye := Fx.cylinder(0.04, 0.04, 0.08, Fx.mat(Color(1.0, 0.25, 0.2), 3.0))
			scope_eye.rotation.x = PI * 0.5
			scope_eye.position = Vector3(0.08, 1.27, -0.22)
			_body.add_child(scope_eye)
		"beam":
			# Drache: Hörner, Flügel, Schwanz an der einfachen Figur
			for sx in [-1.0, 1.0]:
				var horn := Fx.cylinder(0.0, 0.05, 0.2, Fx.mat(Color(0.95, 0.88, 0.7)), 6)
				horn.position = Vector3(0.12 * sx, 1.46, 0.02)
				horn.rotation.z = -0.4 * sx
				_body.add_child(horn)
				var wing := Fx.box(Vector3(0.42, 0.03, 0.3), Fx.mat(Color(0.3, 0.85, 0.85), 0.0, 0.4, 0.4))
				wing.position = Vector3(0.38 * sx, 1.0, 0.22)
				wing.rotation.z = 0.5 * sx
				_body.add_child(wing)
			var tail := Fx.capsule(0.07, 0.55, Fx.mat(Color(0.55, 0.35, 0.85)))
			tail.position = Vector3(0, 0.35, 0.38)
			tail.rotation.x = 1.1
			_body.add_child(tail)
			var star := Fx.sphere(0.06, Fx.mat(Color(1.0, 0.85, 0.3), 2.5), 6, 3)
			star.position = Vector3(0, 1.04, -0.24)
			_body.add_child(star)
		"drone":
			var box_head := Fx.box(Vector3(0.44, 0.36, 0.4), Fx.mat(Color(0.95, 0.9, 0.8)))
			box_head.position.y = 1.26
			_body.add_child(box_head)
			var visor := Fx.box(Vector3(0.36, 0.2, 0.05), Fx.mat(Color(0.08, 0.1, 0.15)))
			visor.position = Vector3(0, 1.26, -0.2)
			_body.add_child(visor)
			for sx in [-0.08, 0.08]:
				var eye := Fx.box(Vector3(0.05, 0.1, 0.02), Fx.mat(Color(0.3, 1.0, 1.0), 3.0))
				eye.position = Vector3(sx, 1.26, -0.23)
				_body.add_child(eye)
			var antenna := Fx.cylinder(0.015, 0.015, 0.2, Fx.mat(Color(0.3, 0.32, 0.36)), 6)
			antenna.position.y = 1.53
			_body.add_child(antenna)
			var tip := Fx.sphere(0.05, Fx.mat(Color(1.0, 0.6, 0.15), 2.0), 6, 3)
			tip.position.y = 1.64
			_body.add_child(tip)
		"cannon":
			# Mini-Panzer: Ketten statt Beine, runde Kuppel als Kopf
			for sx in [-1.0, 1.0]:
				var track := Fx.box(Vector3(0.2, 0.3, 0.8), Fx.mat(Color(0.95, 0.55, 0.15), 0.0, 0.6, 0.4))
				track.position = Vector3(0.28 * sx, 0.15, 0)
				_body.add_child(track)
			var dome := Fx.sphere(0.26, Fx.mat(Color(0.25, 0.3, 0.55)), 14, 8)
			dome.scale = Vector3(1.1, 0.8, 1.1)
			dome.position.y = 1.18
			_body.add_child(dome)
			for sx in [-0.09, 0.09]:
				var eye := Fx.box(Vector3(0.06, 0.1, 0.02), Fx.mat(Color(0.3, 1.0, 1.0), 3.0))
				eye.position = Vector3(sx, 1.2, -0.25)
				_body.add_child(eye)
		"gravity":
			var hair := Fx.sphere(0.28, Fx.mat(Color(0.3, 0.18, 0.12)), 12, 6)
			hair.scale = Vector3(1.15, 0.95, 1.1)
			hair.position = Vector3(0, 1.32, 0.05)
			_body.add_child(hair)
			var band := Fx.torus(0.2, 0.23, Fx.mat(Color(0.2, 0.75, 0.78)))
			band.position.y = 1.4
			_body.add_child(band)
			for sx in [-1.0, 1.0]:
				var pad := Fx.sphere(0.14, Fx.mat(Color(0.5, 0.3, 0.85)), 10, 5)
				pad.position = Vector3(0.27 * sx, 1.05, 0)
				_body.add_child(pad)
		"flamer":
			var helmet := Fx.sphere(0.25, Fx.mat(Color(0.9, 0.15, 0.1), 0.1, 0.3, 0.4), 14, 8)
			helmet.scale = Vector3(1.05, 0.75, 1.15)
			helmet.position.y = 1.33
			_body.add_child(helmet)
			var brim := Fx.cylinder(0.32, 0.32, 0.03, Fx.mat(Color(0.8, 0.12, 0.08)), 14)
			brim.position.y = 1.27
			_body.add_child(brim)
			for sx in [-0.1, 0.1]:
				var tank := Fx.cylinder(0.09, 0.09, 0.5, Fx.mat(Color(0.85, 0.85, 0.2), 0.0, 0.6, 0.3), 10)
				tank.position = Vector3(sx, 0.85, 0.3)
				_body.add_child(tank)


# --- Fertiges 3D-Modell ------------------------------------------------------

## Höhe der Figur in Körper-Einheiten (die einfache Figur ist ebenso groß).
const MODEL_HEIGHT := 1.55
## Zeitpunkt in der Schuss-Animation, an dem der Arm nach vorn zeigt (Zielhaltung).
const AIM_TIME := 0.6

var _model: Node3D
var _anim: AnimationPlayer


func _build_model() -> void:
	_model = Models.make(String(Models.HEROES[id]["file"]), MODEL_HEIGHT)
	_body.add_child(_model)
	_model.position.y = 0.0
	Models.recolor(_model, "Skin", data["skin"])
	Models.recolor(_model, "Face", Color(0.1, 0.07, 0.12))
	_anim = Models.player(_model)
	if Models.is_v2(id):
		_glb_muzzle = _model.find_child("Muzzle", true, false)
	_pose_aim()


## Zielhaltung: Schuss-Animation an der Stelle mit ausgestrecktem Arm anhalten.
## Kleine Schussbewegung: ein Stück der Schuss-Animation abspielen, dann zurück in die Zielhaltung.
func _shot_anim() -> void:
	if _anim == null:
		return
	if _glb_muzzle:
		# Comic-Modell: „Shoot“ beginnt im Anschlag, Rückstoß und zurück (0,4 s)
		_anim.play("Shoot")
		_anim.seek(0.0, true)
		_anim.speed_scale = 1.6
		return
	_anim.play("Shoot_OneHanded")
	_anim.seek(AIM_TIME - 0.12, true)
	_anim.speed_scale = 2.5


func _settle_anim() -> void:
	if _glb_muzzle:
		if _anim and _anim.is_playing() and _anim.current_animation_position >= 0.38:
			_anim.seek(0.0, true)
			_anim.pause()
			_anim.speed_scale = 1.0
		return
	if _anim and _anim.is_playing() and _anim.current_animation_position >= AIM_TIME + 0.12:
		_anim.seek(AIM_TIME, true)
		_anim.pause()
		_anim.speed_scale = 1.0


func _pose_aim() -> void:
	if _anim == null:
		return
	if _glb_muzzle:
		_anim.play("Shoot")
		_anim.seek(0.0, true)
		_anim.pause()
		return
	_anim.play("Shoot_OneHanded")
	_anim.seek(AIM_TIME, true)
	_anim.pause()


## Waffe an die Figur anpassen: fertiges Waffenmodell statt der einfachen Form, wo vorhanden.
## Mündung des Comic-Modells (GLB-Knoten „Muzzle“); die einfache Waffe bleibt dann unsichtbar
var _glb_muzzle: Node3D


func _fit_weapon_to_model() -> void:
	if _glb_muzzle:
		for c in _weapon.get_children():
			if c != _muzzle and c is Node3D:
				(c as Node3D).visible = false
		return
	var gun_file: String = Models.HEROES[id]["gun"]
	if gun_file != "":
		var gun := Models.make_gun(gun_file)
		if gun:
			for c in _weapon.get_children():
				if c != _muzzle:
					c.queue_free()
			_weapon.add_child(gun)
			_muzzle.position = Vector3(0, 0.03, -float(gun.get_meta("front")))
