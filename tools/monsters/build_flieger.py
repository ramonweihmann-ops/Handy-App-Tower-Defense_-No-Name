"""Baut aus einem statischen Meshy-Flieger mit zwei seitlichen Flügeln (Blütenschnapper, Modelltests_v4) die
Spiel-GLB mit eigenem kleinem Skelett und zwei Bewegungen.
Aufruf: python3 build_flieger.py <id>_statisch_roh.glb <ausgabe.glb> [dreiecke] [flügelansatz]   (benötigt: pip install bpy)
flügelansatz: Anteil der halben Breite, ab dem die Punkte zum Flügel gehören (Standard 0.42)

- auf die Dreieckszahl verkleinern, Textur 1024, Ursprung mittig am Boden, Blick +Z (glTF)
- Knochen: Root (Boden) → Body (Körper mit Gesicht, bleibt starr) → WingL / WingR (seitlich, weich angesetzt)
- Fly (Schleife): Flügel schlagen auf und ab, Körper wippt leicht gegen den Flügelschlag
- Attack (Schleife): ausholen (zurück, Flügel hoch) – nach vorn schnappen (Körper kippt nach vorn unten) – zurück
"""
import bpy, sys, math
from mathutils import Vector, Quaternion

args = [a for a in sys.argv[1:] if not a.startswith('-')]
src, out = args[0], args[1]
target = int(args[2]) if len(args) > 2 else 5000
root_frac = float(args[3]) if len(args) > 3 else 0.42

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
scene = bpy.context.scene
meshes = [o for o in scene.objects if o.type == 'MESH']
body = meshes[0]
body.name = "Flieger"
bpy.context.view_layer.objects.active = body
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in list(scene.objects):
    if o != body:
        bpy.data.objects.remove(o, do_unlink=True)

tris = sum(len(p.vertices) - 2 for p in body.data.polygons)
dec = body.modifiers.new("Verkleinern", 'DECIMATE')
dec.ratio = min(1.0, target / tris)
dec.use_collapse_triangulate = True
bpy.ops.object.modifier_apply(modifier=dec.name)
print("DREIECKE", tris, "->", sum(len(p.vertices) - 2 for p in body.data.polygons))
for img in bpy.data.images:
    if img.size[0] > 1024:
        img.scale(1024, 1024)
        img.pack()

vs = body.data.vertices
xs = [v.co.x for v in vs]; ys = [v.co.y for v in vs]; zs = [v.co.z for v in vs]
off = Vector(((min(xs) + max(xs)) * 0.5, (min(ys) + max(ys)) * 0.5, min(zs)))
for v in vs:
    v.co -= off
H = max(zs) - min(zs)
HW = (max(xs) - min(xs)) * 0.5
print("GROESSE", round(2 * HW, 3), round(max(ys) - min(ys), 3), round(H, 3))

# Höhe der Flügel: Mittel der Punkte weit außen
outer = [v.co.z for v in vs if abs(v.co.x) > 0.7 * HW]
wz = sum(outer) / max(1, len(outer)) if outer else 0.5 * H

arm_data = bpy.data.armatures.new("Armature")
arm = bpy.data.objects.new("Armature", arm_data)
scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
eb = arm_data.edit_bones
root = eb.new("Root"); root.head = (0, 0, 0); root.tail = (0, 0, 0.15 * H)
b = eb.new("Body"); b.head = (0, 0, 0.05 * H); b.tail = (0, 0, H); b.parent = root
x0 = root_frac * HW
for name, sx in (("WingL", 1.0), ("WingR", -1.0)):
    w = eb.new(name)
    w.head = (sx * x0, 0, wz)
    w.tail = (sx * HW, 0, wz)
    w.parent = b
bpy.ops.object.mode_set(mode='OBJECT')

groups = {n: body.vertex_groups.new(name=n) for n in ("Body", "WingL", "WingR")}
for v in vs:
    u = min(1.0, max(0.0, (abs(v.co.x) / HW - root_frac) / 0.16))
    w = u * u * (3 - 2 * u)
    groups["Body"].add([v.index], 1.0 - w, 'REPLACE')
    if w > 0:
        groups["WingL" if v.co.x > 0 else "WingR"].add([v.index], w, 'REPLACE')
body.parent = arm
mod = body.modifiers.new("Armature", 'ARMATURE')
mod.object = arm

pose = arm.pose
scene.render.fps = 30
arm.animation_data_create()


def local_rot(bone_name, axis_world, deg):
    """Drehung um eine Weltachse in die lokale Drehung des Knochens umrechnen"""
    rq = arm.data.bones[bone_name].matrix_local.to_quaternion()
    qw = Quaternion(axis_world, math.radians(deg))
    return rq.inverted() @ qw @ rq


def set_pose(flap=0.0, lift=0.0, fwd=0.0, pitch=0.0, sweep=0.0):
    """flap: Flügel hoch (+) bzw. runter (−) in Grad; lift/fwd: in Körperhöhen; pitch: Körper nach vorn (+);
    sweep: Flügel nach hinten anlegen (+) in Grad"""
    for pb in pose.bones:
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Quaternion()
        pb.location = (0, 0, 0)
        pb.scale = (1, 1, 1)
    # Root zeigt nach +Z: lokale Y = Welt-Z (hoch), lokale Z = Welt −Y (vorn)
    pose.bones["Root"].location = (0, lift * H, fwd * H)
    pose.bones["Body"].rotation_quaternion = local_rot("Body", (1, 0, 0), -pitch)
    # Flügelschlag um die Blickachse (Welt Y); links hoch = Drehung um −Y, rechts hoch = um +Y
    for name, sx in (("WingL", 1.0), ("WingR", -1.0)):
        q = local_rot(name, (0, 1, 0), -sx * flap) @ local_rot(name, (0, 0, 1), sx * sweep)
        pose.bones[name].rotation_quaternion = q
    bpy.context.view_layer.update()


def make(name, length_frames, keys):
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    arm.animation_data.action = act
    for u, kw in keys:
        set_pose(**kw)
        f = round(u * length_frames)
        for pb in pose.bones:
            pb.keyframe_insert("rotation_quaternion", frame=f)
            pb.keyframe_insert("location", frame=f)
            pb.keyframe_insert("scale", frame=f)


make("Fly", 16, [
    (0.00, dict(flap=28, lift=-0.03)),
    (0.25, dict(flap=0, lift=0.0)),
    (0.50, dict(flap=-24, lift=0.04)),
    (0.75, dict(flap=0, lift=0.0)),
    (1.00, dict(flap=28, lift=-0.03)),
])
make("Attack", 27, [
    (0.00, dict(flap=6)),
    (0.30, dict(flap=34, fwd=-0.08, pitch=-14, sweep=10)),
    (0.45, dict(flap=36, fwd=-0.10, pitch=-18, sweep=12)),
    (0.56, dict(flap=-20, fwd=0.22, pitch=26, lift=-0.06)),
    (0.68, dict(flap=-14, fwd=0.18, pitch=20, lift=-0.04)),
    (0.85, dict(flap=10, fwd=0.04, pitch=-2)),
    (1.00, dict(flap=6)),
])
arm.animation_data.action = None
set_pose()
print("BEWEGUNGEN", sorted(a.name for a in bpy.data.actions))
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS',
                          export_yup=True, export_apply=False, export_force_sampling=True)
print("FERTIG", out)
