class_name HeroPortrait
extends SubViewportContainer
## Kleines 3D-Porträt eines Helden für Menü und Heldenwahl. Der Held dreht sich langsam.
## Gesperrte Helden werden als dunkle Silhouette gezeigt.

var hero_id := ""
var locked := false
var spin := true
var _hero: Hero
var _t := 0.0


static func make(id: String, px: int, locked_ := false) -> HeroPortrait:
	var p := HeroPortrait.new()
	p.hero_id = id
	p.locked = locked_
	p.custom_minimum_size = Vector2(px, px)
	return p


func _ready() -> void:
	stretch = true
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var vp := SubViewport.new()
	vp.own_world_3d = true
	vp.transparent_bg = true
	vp.render_target_update_mode = SubViewport.UPDATE_WHEN_VISIBLE
	add_child(vp)
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_CLEAR_COLOR
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.6, 0.65, 0.9)
	e.ambient_light_energy = 0.8
	e.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.environment = e
	vp.add_child(env)
	var key := DirectionalLight3D.new()
	key.rotation_degrees = Vector3(-30, 150, 0)
	key.light_energy = 1.3
	vp.add_child(key)
	var rim := DirectionalLight3D.new()
	rim.rotation_degrees = Vector3(-20, -20, 0)
	rim.light_energy = 0.9
	rim.light_color = Color(0.6, 0.7, 1.0)
	vp.add_child(rim)
	var cam := Camera3D.new()
	cam.fov = 34.0
	cam.position = Vector3(0, 1.5, -5.0)
	vp.add_child(cam)
	cam.look_at(Vector3(0, 1.0, 0), Vector3.UP)
	_hero = Hero.new()
	vp.add_child(_hero)
	_hero.setup(hero_id, null)
	_hero.hide_pipe()
	_hero.rotation.y = 0.35
	if locked:
		modulate = Color(0.2, 0.2, 0.28)


func _process(delta: float) -> void:
	if spin and _hero:
		_t += delta
		_hero.rotation.y = 0.35 + sin(_t * 0.6) * 0.6
