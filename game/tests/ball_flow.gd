extends SceneTree
## Lässt die Kugelbahn eine Minute lang laufen und meldet, wie viele Kugeln ankommen.
## Aufruf: godot --headless --fixed-fps 60 --path game --script res://tests/ball_flow.gd

var run: BallRun
var frame := 0
var reported := 0


func _initialize() -> void:
	var root_ctrl := Control.new()
	root_ctrl.size = Vector2(720, 470)
	root.add_child(root_ctrl)
	run = BallRun.new()
	run.size = Vector2(720, 470)
	run.ammo = AmmoStore.new()
	run.ammo.reset(100000, 0)
	root_ctrl.add_child(run)


func _physics_process(_delta: float) -> bool:
	frame += 1
	if frame == 2:
		run.active = true
		var per_launch := int(OS.get_environment("PER_LAUNCH")) if OS.get_environment("PER_LAUNCH") != "" else BallRun.BASE_COUNT
		run.balls_per_launch = per_launch
	for node in run._balls.get_children():
		var b := node as AmmoBall
		if b == null or b.collected:
			continue
		var out := b.position.y > BallRun.PANEL_H + 40.0 or b.position.x > BallRun.DESIGN_W + 40.0 or b.position.x < -20.0 or b.position.y < -20.0
		if out and reported < 8:
			reported += 1
			print("raus: pos=(%d,%d) vel=(%d,%d) alter=%.2f" % [b.position.x, b.position.y, b.linear_velocity.x, b.linear_velocity.y, b.age])
	if frame % 600 == 0:
		print("t=%ds  %s  gesammelt=%d  auf_bahn=%d" % [frame / 60, run.stats, run.collected_total, run.ball_count()])
	return frame >= 3600
