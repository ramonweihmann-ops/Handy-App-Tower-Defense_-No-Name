"""Baut aus dem Meshy-Rohmodell von Dusty Jo die fertige Spiel-GLB (Vorlage_Raw/Helden_Roh/dusty_jo_comic_v1).
Aufruf: python3 build_dusty_jo.py <smart_rig_roh.glb> <ausgabe.glb>   (benötigt: pip install bpy)

- Hilfsobjekt „Icosphere“ entfernen, Figur samt Skelett auf 2,0 Einheiten, Füße auf dem Boden
- Pflichtknochen nach Mixamo benennen (Seiten aus der Textur bestimmt: türkises Abzeichen = linker Arm = +X)
- Revolver als eigenes starres Teil: rechte Hand → WeaponSocket → Weapon → Muzzle
- Texturen auf 1024 × 1024
- Animationen Idle, Shoot (Anschlag → Rückstoß → Anschlag, 0,4 s), Victory
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
body.name = "DustyJo"

# --- Größe: 2,0 Einheiten -------------------------------------------------------
h = max((body.matrix_world @ v.co).z for v in body.data.vertices)
s = 2.0 / h
arm.scale = arm.scale * s
bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
body.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# --- Knochennamen -------------------------------------------------------------------
RENAME = {"Bone_000": "mixamorig:Hips", "Bone_016": "mixamorig:Head",
          "Bone_023": "mixamorig:RightHand", "Bone_018": "mixamorig:LeftHand",
          "Bone_012": "mixamorig:RightFoot", "Bone_008": "mixamorig:LeftFoot",
          "Bone_025": "mixamorig:RightArm", "Bone_024": "mixamorig:RightForeArm",
          "Bone_020": "mixamorig:LeftArm", "Bone_019": "mixamorig:LeftForeArm",
          "Bone_005": "mixamorig:Spine2", "Bone_026": "mixamorig:RightShoulder", "Bone_021": "mixamorig:LeftShoulder"}
for old, new in RENAME.items():
    arm.data.bones[old].name = new   # Gruppen der Hautgewichte werden mit umbenannt

# --- Texturen 1024 --------------------------------------------------------------------
for img in bpy.data.images:
    if img.size[0] > 1024:
        img.scale(1024, 1024)
        img.pack()

# --- Revolver -------------------------------------------------------------------------------
def mat(name, col, metal=0.2, rough=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1.0)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    return m

steel = mat("Revolver_Metall", (0.42, 0.44, 0.48), 0.6, 0.35)
wood = mat("Revolver_Griff", (0.36, 0.2, 0.09), 0.0, 0.6)

def part(kind, size, loc, rot=(0, 0, 0), m=steel, verts=12):
    if kind == "cyl":
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=size[0], depth=size[1], location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
        bpy.context.object.scale = size
    o = bpy.context.object
    o.data.materials.append(m)
    return o

# im Waffenraum: Lauf entlang +Y (Richtung der Handknochen), Griff nach -Z
R = 0.5 * math.pi
parts = [
    part("cyl", (0.028, 0.30), (0, 0.17, 0.02), (R, 0, 0)),          # Lauf
    part("cyl", (0.055, 0.10), (0, 0.0, 0.02), (R, 0, 0), verts=8),  # Trommel
    part("cube", (0.05, 0.12, 0.07), (0, -0.04, 0.03)),              # Rahmen
    part("cube", (0.045, 0.07, 0.16), (0, -0.09, -0.07), (-0.35, 0, 0), wood),  # Griff
    part("cube", (0.015, 0.03, 0.03), (0, 0.3, 0.06)),               # Korn
]
bpy.ops.object.select_all(action='DESELECT')
for p in parts:
    p.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
weapon = bpy.context.object
weapon.name = "Weapon"
weapon.scale = (1.45, 1.45, 1.45)   # im Spielmaßstab gut erkennbar
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

socket = bpy.data.objects.new("WeaponSocket", None)
scene.collection.objects.link(socket)
socket.parent = arm
socket.parent_type = 'BONE'
socket.parent_bone = "mixamorig:RightHand"
# Griff in der Faust: etwas vor dem Handgelenk (Knochen-Y), kein Versatz quer
socket.matrix_parent_inverse = Matrix.Identity(4)
socket.location = (0.0, -0.06, 0.0)      # Bone-Parent: Ursprung an der Knochenspitze; zurück in die Faust
socket.rotation_euler = (0.0, 0.0, 0.0)
weapon.parent = socket
weapon.matrix_parent_inverse = Matrix.Identity(4)
weapon.location = (0, 0, 0)
muzzle = bpy.data.objects.new("Muzzle", None)
scene.collection.objects.link(muzzle)
muzzle.parent = weapon
muzzle.location = (0, 0.33 * 1.45, 0.02 * 1.45)
# glTF -Z = Blender +Y: Muzzle zeigt ohne Drehung schon entlang des Laufs

# --- Posen ----------------------------------------------------------------------------------
pose = arm.pose
bones = arm.data.bones
FWD = Vector((0, -1, 0))   # Figur schaut nach -Y (Blender), rechts = -X

def aim_dirs(recoil=0.0):
    return {
        "mixamorig:RightArm": Vector((-0.2, -1.0, -0.12)),
        "mixamorig:RightForeArm": Vector((-0.02, -1.0, 0.02 + 0.28 * recoil)),
        "mixamorig:RightHand": Vector((0.0, -1.0, 0.05 + 0.4 * recoil)),
        "mixamorig:LeftArm": Vector((0.3, -0.05, -1.0)),
        "mixamorig:LeftForeArm": Vector((0.18, -0.35, -1.0)),
    }

def idle_dirs(t):
    w = math.sin(t * 2 * math.pi)
    return {
        "mixamorig:RightArm": Vector((-0.32, 0.02 * w, -1.0)),
        "mixamorig:RightForeArm": Vector((-0.18, -0.3 - 0.05 * w, -1.0)),
        "mixamorig:RightHand": Vector((-0.1, -0.6, -1.0)),
        "mixamorig:LeftArm": Vector((0.32, -0.02 * w, -1.0)),
        "mixamorig:LeftForeArm": Vector((0.18, -0.3 + 0.05 * w, -1.0)),
    }

def victory_dirs(t):
    w = math.sin(t * 2 * math.pi)
    return {
        "mixamorig:RightArm": Vector((-0.55, -0.1, 0.85)),
        "mixamorig:RightForeArm": Vector((-0.45, -0.25 + 0.15 * w, 1.0)),
        "mixamorig:RightHand": Vector((0.0, -0.4, 1.0)),
        "mixamorig:LeftArm": Vector((0.55, -0.1, 0.85 + 0.1 * w)),
        "mixamorig:LeftForeArm": Vector((0.5, -0.1, 1.0)),
    }

ORDER = ["mixamorig:RightArm", "mixamorig:RightForeArm", "mixamorig:RightHand",
         "mixamorig:LeftArm", "mixamorig:LeftForeArm"]

def apply_dirs(dirs, spine_tilt=0.0, hips_up=0.0):
    for pb in pose.bones:
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Quaternion()
        pb.location = (0, 0, 0)
    bpy.context.view_layer.update()
    sp = pose.bones["mixamorig:Spine2"]
    sp.rotation_quaternion = Quaternion((1, 0, 0), spine_tilt)
    hp = pose.bones["mixamorig:Hips"]
    # Hüfte anheben (Weltachse Z) in Knochenkoordinaten umrechnen
    rest = bones["mixamorig:Hips"].matrix_local.to_3x3()
    hp.location = rest.inverted() @ Vector((0, 0, hips_up))
    bpy.context.view_layer.update()
    for name in ORDER:
        pb = pose.bones[name]
        cur = pb.matrix.copy()
        y = cur.to_3x3().col[1].normalized()
        d = dirs[name].normalized()
        q = y.rotation_difference(d)
        m = Matrix.Translation(cur.translation) @ q.to_matrix().to_4x4() @ Matrix.Translation(-cur.translation) @ cur
        pb.matrix = m
        bpy.context.view_layer.update()

def keyall(frame):
    for pb in pose.bones:
        pb.keyframe_insert("rotation_quaternion", frame=frame)
        pb.keyframe_insert("location", frame=frame)

FPS = 30
scene.render.fps = FPS
arm.animation_data_create()

def make(name, frames):
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    arm.animation_data.action = act
    for f, fn in frames:
        fn()
        keyall(f)
    return act

make("Idle", [(int(i * 15), (lambda t=i / 4.0: apply_dirs(idle_dirs(t), 0.03 * math.sin(t * 2 * math.pi), 0.01 * math.sin(t * 4 * math.pi)))) for i in range(5)])
make("Shoot", [(0, lambda: apply_dirs(aim_dirs(0.0))), (2, lambda: apply_dirs(aim_dirs(1.0), -0.06)),
               (6, lambda: apply_dirs(aim_dirs(0.35), -0.02)), (12, lambda: apply_dirs(aim_dirs(0.0)))])
make("Victory", [(int(i * 12), (lambda t=i / 4.0: apply_dirs(victory_dirs(t), -0.05, 0.06 * abs(math.sin(t * 2 * math.pi))))) for i in range(5)])
arm.animation_data.action = None
for pb in pose.bones:
    pb.rotation_quaternion = Quaternion()
    pb.location = (0, 0, 0)

tris = sum(len(p.vertices) - 2 for o in scene.objects if o.type == 'MESH' for p in o.data.polygons)
print("DREIECKE", tris, "TEXTUREN", [tuple(i.size) for i in bpy.data.images])
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS',
                          export_yup=True, export_apply=False, export_force_sampling=True)
print("FERTIG", out)
