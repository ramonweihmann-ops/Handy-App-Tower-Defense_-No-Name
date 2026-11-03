"""Baut aus dem Meshy-Rohmodell des Zombies die Spiel-GLB (Vorlage_Raw/Monster_Roh/Modelltests_v1).
Aufruf: python3 build_zombie.py <zombie_rig_roh.glb> <ausgabe.glb> [dreiecke]   (benötigt: pip install bpy)

- Hilfsobjekt „Icosphere“ entfernen
- auf etwa 5.000 Dreiecke verkleinern (mittlerer Gegner, docs/MONSTER_EINBAU.md), Gewichte bleiben erhalten
- Textur auf 1024 × 1024
- Bewegungen umbenennen: Walking → Walk, Running → Run, Dead → Death.
  Hit_Reaction fällt weg (wandert 60 cm zur Seite; Treffer zeigt das Spiel durch Aufblitzen).
- Angriff neu berechnet (der mitgelieferte kreuzt die Arme und führt sie durch den Körper):
  Lauern (Arme nach vorn) → Ausholen (Arme schräg nach außen oben, am Kopf vorbei) → Schlag (beide Klauen
  nach vorn unten, Oberkörper beugt mit) → Lauern; 1,1 s, Schleife.
- Faust beim Schlag: Die Finger hängen im Rohmodell kaum an ihren Knochen. Darum je Hand ein neuer Knochen
  „LeftFingers“/„RightFingers“ ab den Knöcheln, die Punkte dahinter gehen weich auf ihn über; beim Schlag
  krümmt er die Finger zur Handfläche (Faust), beim Ausholen leicht (Klaue).
- Blick +Z (glTF), Füße auf dem Boden; die Größe im Kampf stellt das Spiel ein (models.gd „height“)
"""
import bpy, sys, math

args = [a for a in sys.argv if not a.startswith('-')]
src, out = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else args[-2], args[-1]
target = 5000
if len(args) >= 3 and args[-1].isdigit():
    target = int(args[-1]); src, out = args[-3], args[-2]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
scene = bpy.context.scene
for o in list(scene.objects):
    if o.name.startswith("Icosphere"):
        bpy.data.objects.remove(o, do_unlink=True)
arm = [o for o in scene.objects if o.type == 'ARMATURE'][0]
body = [o for o in scene.objects if o.type == 'MESH'][0]
arm.name = "Armature"
body.name = "Zombie"

# --- Dreiecke verkleinern (Decimate vor dem Armature-Modifier anwenden) -----------------------
tris = sum(len(p.vertices) - 2 for p in body.data.polygons)
bpy.context.view_layer.objects.active = body
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
dec = body.modifiers.new("Verkleinern", 'DECIMATE')
dec.ratio = min(1.0, target / tris)
dec.use_collapse_triangulate = True
bpy.ops.object.modifier_move_to_index(modifier=dec.name, index=0)
bpy.ops.object.modifier_apply(modifier=dec.name)
print("DREIECKE", tris, "->", sum(len(p.vertices) - 2 for p in body.data.polygons))

# --- Fingerknochen für die Faust ------------------------------------------------------------------
from mathutils import Vector
def finger_bone(side, palm):
    hand = "mixamorig:%sHand" % side
    groups = {g.index for g in body.vertex_groups if g.name == hand or g.name.startswith("mixamorig:%sHand" % side)}
    hb = arm.data.bones[hand]
    h0 = arm.matrix_world @ hb.head_local
    h1 = arm.matrix_world @ hb.tail_local
    axis = (h1 - h0).normalized()
    pts = []
    for v in body.data.vertices:
        w = sum(g.weight for g in v.groups if g.group in groups)
        if w > 0.5:
            pts.append((v, (body.matrix_world @ v.co - h0).dot(axis)))
    tmax = max(t for _, t in pts)
    knuckle = 0.45 * tmax
    # neuer Knochen an den Knöcheln
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones.new("%sFingers" % side)
    inv = arm.matrix_world.inverted()
    eb.head = inv @ (h0 + axis * knuckle)
    eb.tail = inv @ (h0 + axis * tmax)
    eb.parent = arm.data.edit_bones[hand]
    bpy.ops.object.mode_set(mode='OBJECT')
    # Gewichte: Fingergruppen in die Hand, dann weich ab den Knöcheln auf den Fingerknochen
    vg_hand = body.vertex_groups[hand]
    vg_f = body.vertex_groups.new(name="%sFingers" % side)
    for v, t in pts:
        w = sum(g.weight for g in v.groups if g.group in groups)
        for g in list(v.groups):
            if g.group in groups and g.group != vg_hand.index:
                body.vertex_groups[g.group].remove([v.index])
        x = min(1.0, max(0.0, (t - (knuckle - 0.012)) / 0.03))
        s = x * x * (3 - 2 * x)
        vg_hand.add([v.index], w * (1 - s), 'REPLACE')
        if s > 0:
            vg_f.add([v.index], w * s, 'REPLACE')
    # Krümmachse in Knochenkoordinaten: Finger drehen zur Handfläche
    bend = axis.cross(Vector(palm)).normalized()
    return "%sFingers" % side, bend

FINGERS = [finger_bone("Left", (-1, 0, 0)), finger_bone("Right", (1, 0, 0))]

# --- Textur 1024 ------------------------------------------------------------------------------
for img in bpy.data.images:
    if img.size[0] > 1024:
        img.scale(1024, 1024)
        img.pack()

# --- Bewegungen --------------------------------------------------------------------------------
RENAME = {"Walking": "Walk", "Running": "Run", "Dead": "Death"}
for a in list(bpy.data.actions):
    if a.name in RENAME:
        a.name = RENAME[a.name]
        a.use_fake_user = True
    else:
        bpy.data.actions.remove(a)
if arm.animation_data:
    arm.animation_data.action = None

# --- eigener Angriff aus Armrichtungen (Figur schaut nach −Y, linker Arm auf +X) ------------------
from mathutils import Vector, Matrix, Quaternion
pose = arm.pose

def dirs(lr_arm, lr_fore, spine):
    out = {"mixamorig:Spine1": Vector(spine)}
    for side, sx in (("Left", 1.0), ("Right", -1.0)):
        a = Vector((lr_arm[0] * sx, lr_arm[1], lr_arm[2]))
        f = Vector((lr_fore[0] * sx, lr_fore[1], lr_fore[2]))
        out["mixamorig:%sArm" % side] = a
        out["mixamorig:%sForeArm" % side] = f
        out["mixamorig:%sHand" % side] = f
    return out

ORDER = ["mixamorig:Spine1", "mixamorig:LeftArm", "mixamorig:LeftForeArm", "mixamorig:LeftHand",
         "mixamorig:RightArm", "mixamorig:RightForeArm", "mixamorig:RightHand"]

def curl(deg):
    aw = arm.matrix_world.to_3x3().normalized().inverted()
    for name, bend in FINGERS:
        local = (arm.data.bones[name].matrix_local.to_3x3().inverted() @ (aw @ bend)).normalized()
        pose.bones[name].rotation_quaternion = Quaternion(local, math.radians(deg))
    bpy.context.view_layer.update()

def apply_dirs(d, fist=0.0):
    for pb in pose.bones:
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Quaternion()
        pb.location = (0, 0, 0)
    bpy.context.view_layer.update()
    for name in ORDER:
        pb = pose.bones[name]
        cur = (arm.matrix_world @ pb.matrix)
        y = cur.to_3x3().col[1].normalized()
        q = y.rotation_difference(d[name].normalized())
        m = Matrix.Translation(cur.translation) @ q.to_matrix().to_4x4() @ Matrix.Translation(-cur.translation) @ cur
        pb.matrix = arm.matrix_world.inverted() @ m
        bpy.context.view_layer.update()
    curl(fist)

LAUERN = dirs((0.22, -1.0, 0.05), (0.12, -1.0, 0.12), (0.0, -0.08, 1.0))
AUSHOLEN = dirs((0.75, 0.05, 0.7), (0.55, -0.1, 0.85), (0.0, 0.14, 1.0))
SCHLAG = dirs((0.28, -0.9, -0.35), (0.12, -0.8, -0.6), (0.0, -0.4, 1.0))
arm.animation_data_create()
act = bpy.data.actions.new("Attack")
act.use_fake_user = True
arm.animation_data.action = act
for frame, d, fist in [(0, LAUERN, 0), (8, AUSHOLEN, 30), (12, SCHLAG, 100), (18, SCHLAG, 100), (26, LAUERN, 0)]:
    apply_dirs(d, fist)
    for pb in pose.bones:
        pb.keyframe_insert("rotation_quaternion", frame=frame)
        pb.keyframe_insert("location", frame=frame)
arm.animation_data.action = None
for pb in pose.bones:
    pb.rotation_quaternion = Quaternion()
    pb.location = (0, 0, 0)
print("BEWEGUNGEN", sorted(a.name for a in bpy.data.actions))

bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS',
                          export_yup=True, export_apply=False, export_force_sampling=True)
print("FERTIG", out)
