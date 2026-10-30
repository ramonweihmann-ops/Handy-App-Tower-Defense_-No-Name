extends SceneTree
## Verfolgt einzelne Kugeln in der Kugelbahn und gibt ihren Weg aus.
## Aufruf: godot --headless --fixed-fps 60 --path game --script res://tests/ball_trace.gd

var run: BallRun
var frame := 0
var tracked: AmmoBall


func _initialize() -> void:
	var root_ctrl := Control.new()
	root_ctrl.size = Vector2(720, 470)
	root.add_child(root_ctrl)
	run = BallRun.new()
	run.size = Vector2(720, 470)
	run.ammo = AmmoStore.new()
	run.ammo.reset(999, 0)
	root_ctrl.add_child(run)


func _process(_delta: float) -> bool:
	frame += 1
	if frame == 5:
		run._spawn_ball("normal", BallRun.LAUNCH_POS, Vector2(0, -1200), {})
		tracked = run._balls.get_child(run._balls.get_child_count() - 1)
	if tracked and is_instance_valid(tracked) and frame % 3 == 0 and frame < 200:
		print("f=%d pos=(%d,%d) vel=(%d,%d)" % [frame, tracked.position.x, tracked.position.y, tracked.linear_velocity.x, tracked.linear_velocity.y])
	return frame > 200
