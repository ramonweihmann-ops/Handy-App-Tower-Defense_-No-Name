"""Baut aus dem Meshy-Rohmodell des Tentaklers die Spiel-GLB (Vorlage_Raw/Monster_Roh/Modelltests_v1).
Aufruf: python3 build_tentakler.py <tentakler_rig_roh.glb> <ausgabe.glb>   (benötigt: pip install bpy)

Smart Rig ohne Bewegungen. Knochen (Blender, Figur schaut nach −Y, linke Seite auf −X):
Bone_000 Wurzel, Bone_001 Körper, Bone_009…006 / 013…010 Hörner (bleiben starr),
Bone_017…014 / 021…018 Scherenarme, Bone_026…022 / 031…027 Flügel.

- Hilfsobjekt „Icosphere“ entfernen, auf etwa 5.000 Dreiecke verkleinern, Textur 1024
- Fly (0,8 s, Schleife): Flügelschlag mit verzögerten äußeren Gliedern, Körper wippt, Scheren pendeln
- Attack (0,9 s, Schleife): Scheren holen seitlich nach oben außen aus (Zangen auf) und schnappen nach vorn unten zu,
  Körper stößt leicht nach vorn, Flügel schlagen schneller
"""
import bpy, sys, math
from mathutils import Vector, Matrix, Quaternion

src, out = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
scene = bpy.context.scene
for o in list(scene.objects):
    if o.name.startswith("Icosphere"):
        bpy.data.objects.remove(o, do_unlink=True)
arm = [o for o in scene.objects if o.type == 'ARMATURE'][0]
body = [o for o in scene.objects if o.type == 'MESH'][0]
arm.name = "Armature"
body.name = "Tentakler"

tris = sum(len(p.vertices) - 2 for p in body.data.polygons)
bpy.context.view_layer.objects.active = body
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
dec = body.modifiers.new("Verkleinern", 'DECIMATE')
dec.ratio = min(1.0, 5000 / tris)
dec.use_collapse_triangulate = True
bpy.ops.object.modifier_move_to_index(modifier=dec.name, index=0)
bpy.ops.object.modifier_apply(modifier=dec.name)
print("DREIECKE", tris, "->", sum(len(p.vertices) - 2 for p in body.data.polygons))
for img in bpy.data.images:
    if img.size[0] > 1024:
        img.scale(1024, 1024)
        img.pack()

pose = arm.pose
WING_L = ["Bone_026", "Bone_025", "Bone_024", "Bone_023", "Bone_022"]
WING_R = ["Bone_031", "Bone_030", "Bone_029", "Bone_028", "Bone_027"]
ARM_L = ["Bone_017", "Bone_016", "Bone_015", "Bone_014"]
ARM_R = ["Bone_021", "Bone_020", "Bone_019", "Bone_018"]

def reset():
    for pb in pose.bones:
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Quaternion()
        pb.location = (0, 0, 0)
    bpy.context.view_layer.update()

def rot(name, axis, deg):
    """Knochen um eine Weltachse durch seinen Kopf drehen (Kinder drehen mit)."""
    pb = pose.bones[name]
    cur = arm.matrix_world @ pb.matrix
    q = Quaternion(Vector(axis).normalized(), math.radians(deg))
    m = Matrix.Translation(cur.translation) @ q.to_matrix().to_4x4() @ Matrix.Translation(-cur.translation) @ cur
    pb.matrix = arm.matrix_world.inverted() @ m
    bpy.context.view_layer.update()

def move(name, offset):
    pb = pose.bones[name]
    cur = arm.matrix_world @ pb.matrix
    pb.matrix = arm.matrix_world.inverted() @ (Matrix.Translation(Vector(offset)) @ cur)
    bpy.context.view_layer.update()

def wings(phase, amp=32.0, sweep=0.0):
    # linker Flügel (−X) hebt sich bei +Drehung um Y, rechter bei −Drehung; äußere Glieder schwingen nach
    for i, (l, r) in enumerate(zip(WING_L[:3], WING_R[:3])):
        # Aufschlag weit, Abschlag knapp (Flügel sollen nicht vor die Scheren klappen)
        a = amp * (0.7 * math.sin(phase - i * 0.55) + 0.3) * (1.0 if i == 0 else 0.45)
        rot(l, (0, 1, 0), a)
        rot(r, (0, 1, 0), -a)
    if sweep:
        rot(WING_L[0], (0, 0, 1), -sweep)
        rot(WING_R[0], (0, 0, 1), sweep)

def claws(up_deg, fwd_deg, pinch_deg):
    # up: Scheren seitlich nach oben außen (linke Seite +Drehung um Y, rechte −);
    # fwd: nach vorn stoßen (negative Drehung um X); pinch: Zange schließen (+) bzw. öffnen (−)
    for chain, sy, sx in ((ARM_L, 1.0, -1.0), (ARM_R, -1.0, 1.0)):
        rot(chain[0], (0, 1, 0), up_deg * sy)
        rot(chain[0], (1, 0, 0), -fwd_deg)
        rot(chain[1], (1, 0, 0), -fwd_deg * 0.4)
        rot(chain[2], (0, 0, 1), pinch_deg * sx)

def keyall(frame):
    for pb in pose.bones:
        pb.keyframe_insert("rotation_quaternion", frame=frame)
        pb.keyframe_insert("location", frame=frame)

scene.render.fps = 30
arm.animation_data_create()

def make(name, frames):
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    arm.animation_data.action = act
    for f, fn in frames:
        reset()
        fn()
        keyall(f)

# Fliegen: 24 Bilder = 0,8 s
def fly(t):
    def f():
        ph = t * 2 * math.pi
        move("Bone_000", (0, 0, 0.05 * math.sin(ph - 0.9)))
        rot("Bone_001", (1, 0, 0), 3.0 * math.sin(ph))
        wings(ph)
        claws(5.0 * math.sin(ph + 1.2), 3.0 * math.sin(ph + 0.4), 4.0 * math.sin(ph))
    return f
make("Fly", [(int(round(i * 3)), fly(i / 8.0)) for i in range(9)])

# Angriff: 27 Bilder = 0,9 s; Flügel schlagen doppelt so schnell
def attack(t):
    def f():
        ph = t * 4 * math.pi
        # 0 → 0,4: ausholen (Scheren hoch, offen), 0,55: zuschnappen nach vorn unten, 1: zurück
        if t < 0.4:      # ausholen: Scheren hoch nach außen, Zangen auf
            k = t / 0.4; up, fwd, pinch, lunge, tilt = 42 * k, -8 * k, -22 * k, 0.0, -6 * k
        elif t < 0.55:   # zuschnappen nach vorn unten
            k = (t - 0.4) / 0.15; up, fwd, pinch, lunge, tilt = 42 - 54 * k, -8 + 30 * k, -22 + 40 * k, -0.18 * k, -6 + 20 * k
        else:            # zurück in die Flughaltung
            k = (t - 0.55) / 0.45; up, fwd, pinch, lunge, tilt = -12 * (1 - k), 22 * (1 - k), 18 * (1 - k), -0.18 * (1 - k), 14 * (1 - k)
        move("Bone_000", (0, lunge, 0.04 * math.sin(ph)))
        rot("Bone_001", (1, 0, 0), tilt)
        wings(ph, 26.0)
        claws(up, fwd, pinch)
    return f
make("Attack", [(int(round(i * 2.7)), attack(i / 10.0)) for i in range(11)])

arm.animation_data.action = None
reset()
print("BEWEGUNGEN", sorted(a.name for a in bpy.data.actions))
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS',
                          export_yup=True, export_apply=False, export_force_sampling=True)
print("FERTIG", out)
