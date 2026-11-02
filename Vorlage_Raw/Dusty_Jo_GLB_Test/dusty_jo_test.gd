extends Node3D

const CLIPS = ["Idle", "Run", "Shoot", "Hit", "Death", "Victory"]
const BESCHRIFTUNG = {"Idle": "Anschlag", "Run": "Laufen", "Shoot": "Schießen", "Hit": "Treffer", "Death": "Tod", "Victory": "Siegerpose"}
var held: Node3D
var spieler: AnimationPlayer
var status: Label
var drehen := false

func _ready() -> void:
	held = load("res://dusty_jo.glb").instantiate()
	add_child(held)
	spieler = held.find_child("AnimationPlayer", true, false) as AnimationPlayer
	for clip in CLIPS:
		var animation := spieler.get_animation(clip)
		animation.loop_mode = Animation.LOOP_LINEAR if clip in ["Idle", "Run", "Hit", "Victory"] else Animation.LOOP_NONE
	spieler.animation_finished.connect(_animation_beendet)
	var camera := Camera3D.new()
	add_child(camera)
	camera.position = Vector3(-3.0, 2.4, 5.5)
	camera.look_at(Vector3(0, 1.0, 0))
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 2.9
	var licht := DirectionalLight3D.new()
	add_child(licht)
	licht.rotation_degrees = Vector3(-35, -35, 0)
	licht.light_energy = 1.5
	var fuelllicht := DirectionalLight3D.new()
	add_child(fuelllicht)
	fuelllicht.rotation_degrees = Vector3(-20, 140, 0)
	fuelllicht.light_energy = 0.65
	var umgebung := WorldEnvironment.new()
	add_child(umgebung)
	umgebung.environment = Environment.new()
	umgebung.environment.background_mode = Environment.BG_COLOR
	umgebung.environment.background_color = Color(0.055, 0.065, 0.10)
	umgebung.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	umgebung.environment.ambient_light_color = Color(0.6, 0.65, 0.8)
	umgebung.environment.ambient_light_energy = 0.55
	var boden := MeshInstance3D.new()
	boden.mesh = CylinderMesh.new()
	boden.mesh.top_radius = 1.2
	boden.mesh.bottom_radius = 1.2
	boden.mesh.height = 0.035
	boden.position.y = -0.025
	var material := StandardMaterial3D.new()
	material.albedo_color = Color(0.12, 0.15, 0.22)
	boden.material_override = material
	add_child(boden)
	var ebene := CanvasLayer.new()
	add_child(ebene)
	var menue := VBoxContainer.new()
	ebene.add_child(menue)
	menue.position = Vector2(24, 20)
	var titel := Label.new()
	titel.text = "Dusty Jo · Godot-Modellprüfung"
	titel.add_theme_font_size_override("font_size", 25)
	menue.add_child(titel)
	var zeile := HBoxContainer.new()
	menue.add_child(zeile)
	for clip in CLIPS:
		var taste := Button.new()
		taste.text = BESCHRIFTUNG[clip]
		zeile.add_child(taste)
		taste.pressed.connect(_abspielen.bind(clip))
	var drehtaste := CheckButton.new()
	drehtaste.text = "Modell drehen"
	menue.add_child(drehtaste)
	drehtaste.toggled.connect(func(wert: bool): drehen = wert)
	status = Label.new()
	menue.add_child(status)
	_abspielen("Idle")
	if "--aufnahme" in OS.get_cmdline_user_args():
		await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("res://godot_vorschau.png")
		get_tree().quit()

func _abspielen(clip: String) -> void:
	spieler.stop()
	spieler.play(clip)
	spieler.advance(0)
	status.text = "Aktuell: " + BESCHRIFTUNG[clip]

func _animation_beendet(clip: StringName) -> void:
	if clip == &"Shoot":
		spieler.play("Idle", 0.06)
	# Death bleibt absichtlich in der letzten, liegenden Pose.

func _process(delta: float) -> void:
	if drehen:
		held.rotate_y(delta * 0.45)
