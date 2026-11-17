"""Baut aus den Meshy-Rohmodellen (Vorlage_Raw/Helden_Roh/<id>_comic_v1) die fertigen Spiel-GLBs für
Pip, Nova (humanoides Meshy-Rig mit Mixamo-Namen), Fünkchen und Rollo (ohne Rig: Skelett entsteht hier) und die
sieben Menschen aus H3 (Iska, Brocken, Volta, Kalle, Margot, Lynx, Fritzi) mit eigener Waffe an der rechten Hand.
Aufruf: python3 build_hero_v2.py <id> <eingabe.glb> <ausgabe.glb>   (benötigt: pip install bpy)

Gemeinsam mit Dusty Jo (build_dusty_jo.py):
- Figur auf 2,0 Einheiten, Füße auf dem Boden, Blick nach -Y (Blender) = -Z im Spiel nach dem Drehen
- Animationen Idle, Shoot (beginnt in der Zielhaltung, Rückstoß und zurück, 0,4 s), Victory
- Knoten „Muzzle“ an der Stelle, aus der der Schuss kommt (Greifer, Faust, Maul, Kanonenrohr)
- Texturen auf 1024 × 1024
"""
import bpy, sys, math
from mathutils import Vector, Matrix, Quaternion

hero, src, out = sys.argv[-3], sys.argv[-2], sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
scene = bpy.context.scene
for o in list(scene.objects):
    if o.name.startswith("Icosphere"):
        bpy.data.objects.remove(o, do_unlink=True)
for a in list(bpy.data.actions):   # Meshy-Clips (Walking, Running) braucht das Spiel nicht
    bpy.data.actions.remove(a)
body = [o for o in scene.objects if o.type == 'MESH'][0]
body.name = hero.capitalize()
FPS = 30
scene.render.fps = FPS


def update():
    bpy.context.view_layer.update()


def world_verts():
    return [body.matrix_world @ v.co for v in body.data.vertices]


# --- Texturen 1024 -------------------------------------------------------------------------
for img in bpy.data.images:
    if img.size[0] > 1024:
        img.scale(1024, 1024)
        img.pack()


# --- Oberfläche matt: Meshys Metall-/Rauheitskarte spiegelt im hellen Kampflicht zu stark (Rollo wirkte gelb)
for m in body.data.materials:
    for n in m.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            for key, val in (("Metallic", 0.0), ("Roughness", 0.7)):
                for l in list(n.inputs[key].links):
                    m.node_tree.links.remove(l)
                n.inputs[key].default_value = val


# --- Textur ausbessern (Stellen, die Meshy anders als die Vorlage gemalt hat) -------------------
def base_image():
    for m in body.data.materials:
        for n in m.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED' and n.inputs["Base Color"].links:
                return n.inputs["Base Color"].links[0].from_node.image
    return None


def paint(select, recolor):
    """select(p, n) -> True für Flächen (Mitte p, Normale n in Welt); recolor(pos3d, rgba) -> rgba oder None
    je Bildpunkt der Fläche (pos3d aus den Eckpunkten interpoliert)."""
    import numpy as np
    img = base_image()
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    uv = body.data.uv_layers.active.data
    mw = body.matrix_world
    nm = mw.to_3x3().inverted().transposed()
    changed = 0
    for poly in body.data.polygons:
        c = mw @ poly.center
        n = (nm @ poly.normal).normalized()
        if not select(c, n):
            continue
        idx = list(poly.loop_indices)
        for k in range(1, len(idx) - 1):
            tri = [idx[0], idx[k], idx[k + 1]]
            P = [mw @ body.data.vertices[body.data.loops[i].vertex_index].co for i in tri]
            U = [Vector((uv[i].uv.x * w, uv[i].uv.y * h)) for i in tri]
            x0, x1 = int(min(u.x for u in U)), int(max(u.x for u in U)) + 1
            y0, y1 = int(min(u.y for u in U)), int(max(u.y for u in U)) + 1
            d = (U[1].y - U[2].y) * (U[0].x - U[2].x) + (U[2].x - U[1].x) * (U[0].y - U[2].y)
            if abs(d) < 1e-9:
                continue
            for yy in range(max(0, y0), min(h, y1 + 1)):
                for xx in range(max(0, x0), min(w, x1 + 1)):
                    a = ((U[1].y - U[2].y) * (xx + 0.5 - U[2].x) + (U[2].x - U[1].x) * (yy + 0.5 - U[2].y)) / d
                    b = ((U[2].y - U[0].y) * (xx + 0.5 - U[2].x) + (U[0].x - U[2].x) * (yy + 0.5 - U[2].y)) / d
                    g = 1 - a - b
                    if min(a, b, g) < -0.08:
                        continue
                    col = recolor(P[0] * a + P[1] * b + P[2] * g, px[yy, xx])
                    if col is not None:
                        px[yy, xx] = col
                        changed += 1
    img.pixels[:] = px.ravel()
    img.pack()
    print("TEXTUR", changed, "Bildpunkte geändert")


def region_color(select, keep):
    """Mittlere Farbe der Bildpunkte auf den gewählten Flächen, die keep(rgba) erfüllen."""
    acc = []
    paint(select, lambda p, c: (acc.append(tuple(c)), None)[1] if keep(c) else None)
    acc.sort(key=lambda c: c[0] + c[1] + c[2])
    return acc[len(acc) // 2] if acc else (0.5, 0.5, 0.5, 1.0)


# --- Hilfen für Posen ------------------------------------------------------------------------
def reset_pose(arm):
    for pb in arm.pose.bones:
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Quaternion()
        pb.location = (0, 0, 0)
    update()


def rot_world(arm, name, axis, deg):
    """Knochen um eine Weltachse drehen (in Knochenkoordinaten umgerechnet, wirkt in jeder Pose gleich)."""
    b = arm.data.bones[name]
    aw = arm.matrix_world.to_3x3().normalized().inverted()
    local = (b.matrix_local.to_3x3().inverted() @ (aw @ Vector(axis))).normalized()
    pb = arm.pose.bones[name]
    pb.rotation_quaternion = Quaternion(local, math.radians(deg)) @ pb.rotation_quaternion


def move_world(arm, name, vec):
    b = arm.data.bones[name]
    aw = arm.matrix_world.to_3x3().normalized().inverted()
    arm.pose.bones[name].location = b.matrix_local.to_3x3().inverted() @ (aw @ Vector(vec))


def point_bones(arm, dirs, order):
    """Knochen nacheinander in Weltrichtungen drehen (wie bei Dusty Jo)."""
    for name in order:
        if name not in dirs:
            continue
        pb = arm.pose.bones[name]
        cur = pb.matrix.copy()
        y = cur.to_3x3().col[1].normalized()
        q = y.rotation_difference(dirs[name].normalized())
        pb.matrix = Matrix.Translation(cur.translation) @ q.to_matrix().to_4x4() @ Matrix.Translation(-cur.translation) @ cur
        update()


def make_actions(arm, clips):
    arm.animation_data_create()
    for name, frames in clips:
        act = bpy.data.actions.new(name)
        act.use_fake_user = True
        arm.animation_data.action = act
        for f, fn in frames:
            fn()
            update()
            for pb in arm.pose.bones:
                pb.keyframe_insert("rotation_quaternion", frame=f)
                pb.keyframe_insert("location", frame=f)
    arm.animation_data.action = None
    reset_pose(arm)


def scale_rigged(arm):
    h = max((body.matrix_world @ v.co).z for v in body.data.vertices)
    arm.scale = arm.scale * (2.0 / h)
    update()
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True)
    body.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


def add_muzzle(arm, bone, world_pos):
    """Muzzle starr an einen Knochen hängen, an einer Stelle in der Ruhehaltung."""
    m = bpy.data.objects.new("Muzzle", None)
    scene.collection.objects.link(m)
    m.parent = arm
    m.parent_type = 'BONE'
    m.parent_bone = bone
    pb = arm.pose.bones[bone]
    tail = arm.matrix_world @ pb.matrix @ Matrix.Translation((0, pb.bone.length, 0))
    m.matrix_parent_inverse = Matrix.Identity(4)
    # wie bei Dusty Jo: Blender +Y des Knotens zeigt nach vorn (Welt -Y), im glTF wird das -Z
    fwd = Vector((0, -1, 0))
    up = Vector((0, 0, 1))
    rot = Matrix((fwd.cross(up), fwd, up)).transposed()
    m.matrix_basis = tail.inverted() @ (Matrix.Translation(world_pos) @ rot.to_4x4())
    update()
    return m


# --- Humanoide: Pip und Nova -------------------------------------------------------------------
ARM_ORDER = ["mixamorig:RightArm", "mixamorig:RightForeArm", "mixamorig:RightHand",
             "mixamorig:LeftArm", "mixamorig:LeftForeArm", "mixamorig:LeftHand"]


def fix_pip_back():
    """Orange Rückenplatte wie in der Vorlage: gleiche Breite und Höhe wie die Brustplatte vorn."""
    import numpy as np
    orange = lambda c: c[0] > 0.6 and 0.25 < c[1] < 0.6 and c[2] < 0.25
    front = []
    # nur der Oberkörper (die Antennenkugel oben ist auch orange)
    paint(lambda p, n: n.y < -0.5 and p.z < 1.25, lambda p, c: (front.append((p.x, p.z, tuple(c))), None)[1] if orange(c) else None)
    xs = sorted(f[0] for f in front); zs = sorted(f[1] for f in front)
    q = lambda v, t: v[int(t * (len(v) - 1))]
    x0, x1, z0, z1 = q(xs, 0.02), q(xs, 0.98), q(zs, 0.02), q(zs, 0.98)
    col = sorted((f[2] for f in front), key=lambda c: c[0] + c[1] + c[2])[len(front) // 2]
    print("BRUSTPLATTE x", round(x0, 3), round(x1, 3), "z", round(z0, 3), round(z1, 3), "Farbe", tuple(round(v, 2) for v in col))
    r = 0.025   # abgerundete Ecken
    def inside(p):
        dx = max(x0 + r - p.x, 0, p.x - (x1 - r)); dz = max(z0 + r - p.z, 0, p.z - (z1 - r))
        return dx * dx + dz * dz <= r * r
    def rec(p, c):
        if not inside(p):
            return None
        # leichte Kante: am Rand etwas dunkler
        edge = min(p.x - x0, x1 - p.x, p.z - z0, z1 - p.z)
        k = 0.82 if edge < 0.012 else 1.0
        return (col[0] * k, col[1] * k, col[2] * k, 1.0)
    paint(lambda p, n: n.y > 0.35 and x0 - 0.05 < p.x < x1 + 0.05 and z0 - 0.05 < p.z < z1 + 0.05, rec)


def build_humanoid():
    arm = [o for o in scene.objects if o.type == 'ARMATURE'][0]
    arm.name = "Armature"
    scale_rigged(arm)
    if hero == "pip":
        fix_pip_back()

    def pose(dirs, spine=0.0, hips_up=0.0):
        reset_pose(arm)
        rot_world(arm, "mixamorig:Spine2", (1, 0, 0), spine)
        move_world(arm, "mixamorig:Hips", (0, 0, hips_up))
        update()
        point_bones(arm, dirs, ARM_ORDER)

    # Zielhaltung: rechter Arm waagerecht nach vorn (leicht zur Mitte), linker Arm locker unten
    def aim(r=0.0):
        return {"mixamorig:RightArm": Vector((-0.12, -1.0, -0.05 + 0.1 * r)),
                "mixamorig:RightForeArm": Vector((0.0, -1.0, 0.02 + 0.3 * r)),
                "mixamorig:RightHand": Vector((0.0, -1.0, 0.05 + 0.35 * r)),
                "mixamorig:LeftArm": Vector((0.35, -0.1, -1.0)),
                "mixamorig:LeftForeArm": Vector((0.2, -0.35, -1.0))}

    def idle(t):
        w = math.sin(t * 2 * math.pi)
        return {"mixamorig:RightArm": Vector((-0.35, 0.02 * w, -1.0)),
                "mixamorig:RightForeArm": Vector((-0.2, -0.25 - 0.05 * w, -1.0)),
                "mixamorig:LeftArm": Vector((0.35, -0.02 * w, -1.0)),
                "mixamorig:LeftForeArm": Vector((0.2, -0.25 + 0.05 * w, -1.0))}

    def victory(t):
        w = math.sin(t * 2 * math.pi)
        return {"mixamorig:RightArm": Vector((-0.5, -0.1, 0.9)),
                "mixamorig:RightForeArm": Vector((-0.35, -0.2 + 0.15 * w, 1.0)),
                "mixamorig:LeftArm": Vector((0.5, -0.1, 0.9 + 0.1 * w)),
                "mixamorig:LeftForeArm": Vector((0.35, -0.1, 1.0))}

    # Nova (Raketenfäuste): Schuss als kurzer Fauststoß nach vorn; Pip: Rückstoß wie ein Werfer
    if hero == "nova":
        shoot = [(0, lambda: pose(aim(0.0))), (2, lambda: pose(aim(0.6), -4)),
                 (5, lambda: pose(aim(-0.15), 3)), (12, lambda: pose(aim(0.0)))]
    else:
        shoot = [(0, lambda: pose(aim(0.0))), (2, lambda: pose(aim(1.0), -4)),
                 (6, lambda: pose(aim(0.35), -1)), (12, lambda: pose(aim(0.0)))]
    make_actions(arm, [
        ("Idle", [(i * 15, (lambda t=i / 4.0: pose(idle(t), 2 * math.sin(t * 2 * math.pi), 0.01 * math.sin(t * 4 * math.pi)))) for i in range(5)]),
        ("Shoot", shoot),
        ("Victory", [(i * 12, (lambda t=i / 4.0: pose(victory(t), -3, 0.06 * abs(math.sin(t * 2 * math.pi))))) for i in range(5)]),
    ])
    # Mündung vor der rechten Hand (Greifer bzw. Faust) in der Zielhaltung
    pose(aim(0.0))
    pb = arm.pose.bones["mixamorig:RightHand"]
    tip = arm.matrix_world @ pb.matrix @ Vector((0, pb.bone.length, 0))
    m = add_muzzle(arm, "mixamorig:RightHand", tip + Vector((0, -0.05, 0)))
    reset_pose(arm)
    print("MUENDUNG", tuple(round(c, 3) for c in m.matrix_world.translation))
    return arm



# --- Menschen mit Waffe (H3): Iska, Brocken, Volta, Kalle, Margot, Lynx, Fritzi ---------------------
# Meshys zweite Rig-Vorlage heißt Hips/Spine02/Spine01/Spine/LeftArm …, Brockens Intelligentes Rig nur
# Bone_###. Alles wird auf die Mixamo-Namen gebracht, die das Spiel und dieses Skript erwarten.
STD = ["Hips", "Neck", "Head", "LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand", "RightShoulder",
       "RightArm", "RightForeArm", "RightHand", "LeftUpLeg", "LeftLeg", "LeftFoot", "RightUpLeg", "RightLeg", "RightFoot"]
MESHY2 = {"Spine02": "mixamorig:Spine", "Spine01": "mixamorig:Spine1", "Spine": "mixamorig:Spine2", "neck": "mixamorig:Neck"}
# Brocken: Seiten aus der Lage bestimmt (Figur schaut nach -Y, rechts = -X)
BROCKEN = {"Bone_001": "mixamorig:Hips", "Bone_014": "mixamorig:Spine2", "Bone_017": "mixamorig:Head",
           "Bone_020": "mixamorig:RightArm", "Bone_019": "mixamorig:RightForeArm", "Bone_018": "mixamorig:RightHand",
           "Bone_023": "mixamorig:LeftArm", "Bone_022": "mixamorig:LeftForeArm", "Bone_021": "mixamorig:LeftHand",
           "Bone_009": "mixamorig:RightFoot", "Bone_004": "mixamorig:LeftFoot"}


def normalize_bones(arm):
    names = [b.name for b in arm.data.bones]
    if "mixamorig:Hips" in names:
        return
    ren = dict(BROCKEN) if "Bone_001" in names and "Hips" not in names else dict(MESHY2)
    for n in names:
        if n in STD and n not in ren:
            ren[n] = "mixamorig:" + n
    for old, new in ren.items():
        if old in names:
            arm.data.bones[old].name = new   # Gruppen der Hautgewichte werden mit umbenannt


def mat(name, col, metal=0.0, rough=0.6, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1.0)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*col, 1.0)
        b.inputs["Emission Strength"].default_value = emit
    return m


R90 = 0.5 * math.pi
# Waffen im Waffenraum: +Y = Lauf nach vorn, +Z = oben, Ursprung = Griff in der rechten Hand.
# Teile: (Form, Maße, Lage, Drehung, Farbe). cyl: (Radius, Länge) entlang Y; box: (Breite, Länge, Höhe).
# hold: rifle (zweihändig vor der Brust), shoulder (auf der Schulter), pistol (einhändig ausgestreckt)
DARK, METAL, WOOD = (0.16, 0.17, 0.2), (0.45, 0.47, 0.52), (0.42, 0.24, 0.11)
WEAPONS = {
    "iska": {"hold": "rifle", "fore": 0.30, "tip": 0.62, "parts": [
        ("box", (0.07, 0.5, 0.11), (0, 0.12, 0.04), DARK), ("cyl", (0.024, 0.3), (0, 0.5, 0.06), METAL),
        ("box", (0.08, 0.2, 0.085), (0, 0.3, 0.05), (0.15, 0.75, 0.8)), ("box", (0.05, 0.08, 0.17), (0, 0.13, -0.09), DARK, (-0.35, 0, 0)),
        ("box", (0.06, 0.26, 0.1), (0, -0.2, 0.01), (0.3, 0.32, 0.38)), ("box", (0.045, 0.06, 0.12), (0, 0.0, -0.06), DARK, (-0.3, 0, 0))]},
    "brocken": {"hold": "shoulder", "fore": 0.32, "tip": 0.66, "parts": [
        ("cyl", (0.095, 0.95), (0, 0.18, 0.13), (0.85, 0.16, 0.12)), ("cyl", (0.11, 0.07), (0, 0.63, 0.13), DARK),
        ("cyl", (0.11, 0.07), (0, -0.27, 0.13), DARK), ("box", (0.05, 0.07, 0.14), (0, 0.0, 0.0), DARK),
        ("box", (0.05, 0.07, 0.12), (0, 0.32, 0.02), DARK), ("box", (0.04, 0.14, 0.06), (0, 0.12, 0.25), (0.95, 0.75, 0.15))]},
    "volta": {"hold": "pistol", "tip": 0.33, "parts": [
        ("box", (0.065, 0.22, 0.09), (0, 0.08, 0.05), (0.92, 0.93, 0.95)), ("cyl", (0.038, 0.16), (0, 0.22, 0.07), (0.2, 0.85, 0.9)),
        ("cyl", (0.05, 0.025), (0, 0.17, 0.07), METAL), ("cyl", (0.05, 0.025), (0, 0.25, 0.07), METAL),
        ("cyl", (0.02, 0.05), (0, 0.31, 0.07), (0.6, 1.0, 1.0)), ("box", (0.045, 0.06, 0.13), (0, -0.01, -0.04), DARK, (-0.35, 0, 0))]},
    "kalle": {"hold": "pistol", "tip": 0.37, "parts": [
        ("box", (0.075, 0.25, 0.1), (0, 0.09, 0.05), (0.55, 0.82, 0.95)), ("cyl", (0.04, 0.16), (0, 0.28, 0.06), (0.92, 0.96, 1.0)),
        ("cyl", (0.03, 0.03), (0, 0.36, 0.06), (0.3, 0.9, 1.0)), ("cyl", (0.035, 0.12), (0, 0.03, 0.14), (0.3, 0.9, 1.0), (0, 0, 0)),
        ("box", (0.05, 0.065, 0.13), (0, -0.01, -0.04), DARK, (-0.35, 0, 0))]},
    "margot": {"hold": "rifle", "fore": 0.28, "tip": 0.66, "parts": [
        ("cyl", (0.028, 0.6), (0.03, 0.36, 0.07), METAL), ("cyl", (0.028, 0.6), (-0.03, 0.36, 0.07), METAL),
        ("box", (0.09, 0.22, 0.07), (0, 0.27, 0.03), WOOD), ("box", (0.065, 0.36, 0.11), (0, -0.12, 0.0), WOOD),
        ("cyl", (0.045, 0.03), (0, 0.12, 0.07), (0.85, 0.65, 0.25)), ("box", (0.045, 0.06, 0.12), (0, 0.0, -0.06), WOOD, (-0.3, 0, 0))]},
    "lynx": {"hold": "rifle", "fore": 0.32, "tip": 0.84, "parts": [
        ("cyl", (0.022, 0.55), (0, 0.55, 0.06), DARK), ("box", (0.06, 0.42, 0.1), (0, 0.06, 0.04), (0.33, 0.4, 0.22)),
        ("cyl", (0.036, 0.3), (0, 0.08, 0.15), DARK), ("cyl", (0.042, 0.03), (0, 0.24, 0.15), (0.25, 0.75, 0.9)),
        ("box", (0.06, 0.28, 0.11), (0, -0.26, 0.01), WOOD), ("box", (0.045, 0.06, 0.12), (0, 0.0, -0.06), DARK, (-0.3, 0, 0))]},
    "fritzi": {"hold": "rifle", "fore": 0.28, "tip": 0.6, "parts": [
        ("box", (0.08, 0.4, 0.11), (0, 0.1, 0.05), (0.38, 0.27, 0.16)), ("cyl", (0.04, 0.24), (0, 0.42, 0.07), METAL),
        ("cyl", (0.055, 0.04), (0, 0.55, 0.07), (1.0, 0.45, 0.1)), ("cyl", (0.06, 0.24), (0, 0.16, -0.07), (0.9, 0.25, 0.12)),
        ("box", (0.06, 0.2, 0.1), (0, -0.18, 0.02), (0.38, 0.27, 0.16)), ("box", (0.045, 0.06, 0.12), (0, 0.0, -0.06), DARK, (-0.3, 0, 0))]},
}


def build_weapon(spec):
    objs = []
    for part in spec["parts"]:
        kind, size, loc, col = part[:4]
        rot = part[4] if len(part) > 4 else None
        if kind == "cyl":
            bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=size[0], depth=size[1], location=loc,
                                                rotation=rot if rot is not None else (R90, 0, 0))
        else:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot or (0, 0, 0))
            bpy.context.object.scale = size
        o = bpy.context.object
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)   # Maße fest, bevor zusammengefügt wird
        o.data.materials.append(mat("W_%d" % len(objs), col, 0.3 if col == METAL else 0.0))
        objs.append(o)
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    w = bpy.context.object
    w.name = "Weapon"
    w.scale = (wscale(spec),) * 3   # im Spielmaßstab von hinten gut erkennbar (wie Dustys Revolver)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return w


def wscale(spec):
    return {"rifle": 1.4, "shoulder": 1.15, "pistol": 1.6}[spec["hold"]]


def bone_head(arm, name):
    return arm.matrix_world @ arm.pose.bones[name].head


def bone_tail(arm, name):
    return arm.matrix_world @ arm.pose.bones[name].tail


def ik(arm, upper, lower, target, pole):
    """Zwei Knochen so drehen, dass das Ende des unteren den Zielpunkt erreicht (Ellbogen Richtung pole)."""
    S = bone_head(arm, upper)
    a, b = arm.data.bones[upper].length, arm.data.bones[lower].length
    d = target - S
    dist = max(0.05, min(d.length, (a + b) * 0.995))
    n = d.normalized()
    cos_a = max(-1.0, min(1.0, (a * a + dist * dist - b * b) / (2 * a * dist)))
    p = Vector(pole) - n * Vector(pole).dot(n)
    p.normalize()
    elbow = S + n * a * cos_a + p * a * math.sqrt(1 - cos_a * cos_a)
    point_bones(arm, {upper: elbow - S}, [upper])
    point_bones(arm, {lower: target - bone_head(arm, lower)}, [lower])


def fix_volta_pocket():
    """Türkise Seitentasche hinten rechts am Kittel (fehlt im Meshy-Export, steht in der Vorlage)."""
    x0, x1, z0, z1 = -0.27, -0.17, 0.58, 0.72
    col = (0.12, 0.72, 0.76, 1.0)
    def rec(p, c):
        if not (x0 < p.x < x1 and z0 < p.z < z1):
            return None
        edge = min(p.x - x0, x1 - p.x, p.z - z0, z1 - p.z)
        k = 0.78 if edge < 0.01 else 1.0
        return (col[0] * k, col[1] * k, col[2] * k, 1.0)
    paint(lambda p, n: n.y > 0.3 and x0 - 0.05 < p.x < x1 + 0.05 and z0 - 0.05 < p.z < z1 + 0.05, rec)


def build_armed():
    arm = [o for o in scene.objects if o.type == 'ARMATURE'][0]
    arm.name = "Armature"
    normalize_bones(arm)
    scale_rigged(arm)
    if hero == "volta":
        fix_volta_pocket()
    spec = WEAPONS[hero]
    hold = spec["hold"]
    reset_pose(arm)
    sh_r = bone_head(arm, "mixamorig:RightArm")
    sh_l = bone_head(arm, "mixamorig:LeftArm")
    reach = arm.data.bones["mixamorig:RightArm"].length + arm.data.bones["mixamorig:RightForeArm"].length
    fwd = Vector((0, -1, 0))
    if hold == "pistol":
        grip = sh_r + Vector((0.1, -0.85 * reach, -0.06))
    elif hold == "shoulder":
        grip = sh_r + Vector((0.12, -0.45 * reach, -0.05))
    else:
        grip = sh_r + Vector((0.14, -0.6 * reach, -0.14))
    print("GRIFF", tuple(round(c, 3) for c in grip), "Reichweite", round(reach, 3))
    POLE_R, POLE_L = (-0.6, 0.3, -1.0), (0.6, 0.3, -1.0)

    def arms(g, left, hand_dir=fwd):
        ik(arm, "mixamorig:RightArm", "mixamorig:RightForeArm", g, POLE_R)
        point_bones(arm, {"mixamorig:RightHand": hand_dir}, ["mixamorig:RightHand"])
        if left is None:
            point_bones(arm, {"mixamorig:LeftArm": Vector((0.35, -0.1, -1.0)), "mixamorig:LeftForeArm": Vector((0.2, -0.35, -1.0))},
                        ["mixamorig:LeftArm", "mixamorig:LeftForeArm"])
        else:
            ik(arm, "mixamorig:LeftArm", "mixamorig:LeftForeArm", left, POLE_L)
            point_bones(arm, {"mixamorig:LeftHand": fwd}, ["mixamorig:LeftHand"])

    def body(spine=0.0, hips_up=0.0):
        reset_pose(arm)
        if "mixamorig:Spine2" in arm.pose.bones:
            rot_world(arm, "mixamorig:Spine2", (1, 0, 0), spine)
        move_world(arm, "mixamorig:Hips", (0, 0, hips_up))
        update()

    def fore(g):
        return None if hold == "pistol" else g + Vector((-0.02, -spec["fore"] * wscale(spec), 0.0))

    def aim(r=0.0, spine=0.0):
        body(spine)
        g = grip + Vector((0, 0.06 * r, 0.025 * r))
        arms(g, fore(g), Vector((0, -1, 0.3 * r)))

    def idle(t):
        w = math.sin(t * 2 * math.pi)
        body(1.5 * w, 0.008 * math.sin(t * 4 * math.pi))
        g = grip + Vector((0.02, 0.1, -0.18 + 0.01 * w))
        arms(g, fore(g) + Vector((0, 0.05, -0.04)) if hold != "pistol" else None, Vector((0, -1, -0.55)))

    def victory(t):
        w = math.sin(t * 2 * math.pi)
        body(-3, 0.06 * abs(w))
        g = sh_r + Vector((-0.1, -0.1, 0.55 + 0.04 * w))
        ik(arm, "mixamorig:RightArm", "mixamorig:RightForeArm", g, (-1.0, 0.2, 0.0))
        point_bones(arm, {"mixamorig:RightHand": Vector((0, -0.3, 1.0))}, ["mixamorig:RightHand"])
        point_bones(arm, {"mixamorig:LeftArm": Vector((0.5, -0.1, 0.9 + 0.1 * w)), "mixamorig:LeftForeArm": Vector((0.35, -0.1, 1.0))},
                    ["mixamorig:LeftArm", "mixamorig:LeftForeArm"])

    make_actions(arm, [
        ("Idle", [(i * 15, (lambda t=i / 4.0: idle(t))) for i in range(5)]),
        ("Shoot", [(0, lambda: aim(0.0)), (2, lambda: aim(1.0, -4)), (6, lambda: aim(0.35, -1)), (12, lambda: aim(0.0))]),
        ("Victory", [(i * 12, (lambda t=i / 4.0: victory(t))) for i in range(5)]),
    ])

    # Waffe: starr an der rechten Hand, in der Zielhaltung so gelegt, dass der Griff in der Hand sitzt
    weapon = build_weapon(spec)
    socket = bpy.data.objects.new("WeaponSocket", None)
    scene.collection.objects.link(socket)
    socket.parent = arm
    socket.parent_type = 'BONE'
    socket.parent_bone = "mixamorig:RightHand"
    socket.matrix_parent_inverse = Matrix.Identity(4)
    weapon.parent = socket
    weapon.matrix_parent_inverse = Matrix.Identity(4)
    weapon.location = (0, 0, 0)
    muzzle = bpy.data.objects.new("Muzzle", None)
    scene.collection.objects.link(muzzle)
    muzzle.parent = weapon
    muzzle.location = Vector((0, spec["tip"], 0.07 if hold != "shoulder" else 0.13)) * wscale(spec)
    aim(0.0)
    hand = (bone_head(arm, "mixamorig:RightHand") + bone_tail(arm, "mixamorig:RightHand")) * 0.5
    up = Vector((0, 0, 1))
    rot = Matrix((fwd.cross(up), fwd, up)).transposed()
    want = Matrix.Translation(hand) @ rot.to_4x4()
    pb = arm.pose.bones["mixamorig:RightHand"]
    tail = arm.matrix_world @ pb.matrix @ Matrix.Translation((0, pb.bone.length, 0))
    socket.matrix_basis = tail.inverted() @ want
    update()
    lh = bone_tail(arm, "mixamorig:LeftHand")
    print("HAND", tuple(round(c, 3) for c in hand), "LINKS", tuple(round(c, 3) for c in lh),
          "MUENDUNG", tuple(round(c, 3) for c in muzzle.matrix_world.translation))
    reset_pose(arm)
    return arm


# --- Eigenes Skelett: Fünkchen und Rollo ----------------------------------------------------------
def ground_static(turn=0.0):
    """Statische Figur: Füße auf z = 0, Mitte auf x = y = 0, Höhe 2,0. turn: Drehung um die Hochachse,
    damit die Figur nach -Y schaut (Rollo liefert Meshy mit dem Rohr nach -X)."""
    if turn:
        body.matrix_world = Matrix.Rotation(math.radians(turn), 4, 'Z') @ body.matrix_world
        update()
    vs = world_verts()
    lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
    hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
    s = 2.0 / (hi.z - lo.z)
    c = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    body.matrix_world = Matrix.Scale(s, 4) @ Matrix.Translation(-c) @ body.matrix_world
    update()
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def new_armature(bones):
    """bones: [(name, head, tail, parent)] in Weltkoordinaten."""
    data = bpy.data.armatures.new("Armature")
    arm = bpy.data.objects.new("Armature", data)
    scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    eb = {}
    for name, h, t, parent in bones:
        b = data.edit_bones.new(name)
        b.head, b.tail = Vector(h), Vector(t)
        if parent:
            b.parent = eb[parent]
        eb[name] = b
    bpy.ops.object.mode_set(mode='OBJECT')
    return arm


def bind(arm, weights):
    """weights(v) -> {knochen: gewicht} je Weltpunkt; normalisiert, Rest an Root."""
    body.parent = arm
    mod = body.modifiers.new("Armature", 'ARMATURE')
    mod.object = arm
    groups = {b.name: body.vertex_groups.new(name=b.name) for b in arm.data.bones}
    for v in body.data.vertices:
        w = weights(body.matrix_world @ v.co)
        tot = sum(w.values())
        if tot < 1.0:
            w["Root"] = w.get("Root", 0.0) + (1.0 - tot)
            tot = 1.0
        for name, x in w.items():
            if x > 0.001:
                groups[name].add([v.index], x / tot, 'REPLACE')


def ramp(x, a, b):
    """0 bei a, 1 bei b (weicher Übergang)."""
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def build_dragon():
    ground_static()
    vs = world_verts()
    # Maul: vorderster Punkt im oberen Drittel; Flügelansatz und Schweif aus der Form
    top = [v for v in vs if v.z > 1.2]
    snout = min(top, key=lambda v: v.y)
    print("MAUL", tuple(round(c, 3) for c in snout))
    arm = new_armature([
        ("Root", (0, 0, 0.0), (0, 0, 0.6), None),
        ("Body", (0, 0.05, 0.6), (0, -0.1, 1.05), "Root"),
        ("Head", (0, -0.15, 1.05), (0, -0.25, 1.75), "Body"),
        ("Wing.L", (0.22, 0.1, 1.05), (0.75, 0.15, 1.35), "Body"),
        ("Wing.R", (-0.22, 0.1, 1.05), (-0.75, 0.15, 1.35), "Body"),
        ("Tail", (0, 0.35, 0.35), (0, 0.95, 0.15), "Root"),
    ])

    def weights(p):
        wing = ramp(abs(p.x), 0.3, 0.45) * ramp(p.z, 0.75, 0.95) * (1.0 - ramp(p.y, 0.45, 0.6) * 0)
        head = ramp(p.z, 1.0, 1.2) * (1.0 - ramp(abs(p.x), 0.35, 0.45)) * (1.0 - ramp(p.y, 0.15, 0.3))
        tail = ramp(p.y, 0.3, 0.5) * (1.0 - ramp(p.z, 0.55, 0.75))
        bodyw = ramp(p.z, 0.45, 0.65)
        w = {"Wing.L" if p.x > 0 else "Wing.R": wing, "Head": head * (1 - wing), "Tail": tail * (1 - wing)}
        rest = max(0.0, 1.0 - sum(w.values()))
        w["Body"] = rest * bodyw
        return w

    bind(arm, weights)

    def pose(flap=0.0, head_pitch=0.0, head_fwd=0.0, tail=0.0, hop=0.0, breathe=0.0):
        reset_pose(arm)
        rot_world(arm, "Wing.L", (0, 1, 0), -flap)
        rot_world(arm, "Wing.R", (0, 1, 0), flap)
        rot_world(arm, "Head", (1, 0, 0), head_pitch)
        move_world(arm, "Head", (0, -head_fwd, 0))
        rot_world(arm, "Tail", (0, 0, 1), tail)
        rot_world(arm, "Body", (1, 0, 0), breathe)
        move_world(arm, "Root", (0, 0, hop))

    make_actions(arm, [
        ("Idle", [(i * 15, (lambda t=i / 4.0: pose(12 * math.sin(t * 2 * math.pi), 2 * math.sin(t * 2 * math.pi),
                                                  0, 10 * math.sin(t * 2 * math.pi), 0, 1.5 * math.sin(t * 2 * math.pi)))) for i in range(5)]),
        # Atemzug: Kopf vor und leicht nach unten, Flügel öffnen sich, zurück
        ("Shoot", [(0, lambda: pose(0, 0, 0)), (3, lambda: pose(-15, -10, 0.08)),
                   (7, lambda: pose(-8, -5, 0.04)), (12, lambda: pose(0, 0, 0))]),
        ("Victory", [(i * 6, (lambda t=i / 8.0: pose(35 * math.sin(t * 4 * math.pi), 8, 0, 15 * math.sin(t * 2 * math.pi),
                                                    0.12 * abs(math.sin(t * 2 * math.pi))))) for i in range(9)]),
    ])
    m = add_muzzle(arm, "Head", snout + Vector((0, -0.04, 0)))
    print("MUENDUNG", tuple(round(c, 3) for c in m.matrix_world.translation))
    return arm


def fix_rollo_back():
    """Rückseite wie in der Vorlage: kein Stern auf der Wanne, kein Muster am Turm (glattes Blau)."""
    blueish = lambda c: c[2] > c[0] + 0.08 and c[2] > c[1] + 0.02 and c[0] + c[1] + c[2] < 1.4
    back = lambda p, n: n.y > 0.45 and abs(p.x) < 0.5
    hull = lambda p, n: back(p, n) and 0.45 < p.z < 1.05
    tur = lambda p, n: back(p, n) and 1.05 <= p.z < 1.55
    for sel, name in ((hull, "Wanne"), (tur, "Turm")):
        col = region_color(sel, blueish)
        print(name, "Blau", tuple(round(v, 2) for v in col))
        def rec(p, c, col=col):
            light = c[0] + c[1] + c[2]
            cyan = c[1] > 0.55 and c[2] > 0.55 and c[0] < 0.45
            if cyan or (c[0] > 0.6 and c[1] > 0.3 and c[2] < 0.35):   # Leuchten und Orange bleiben
                return None
            if light > 1.75 and name == "Wanne" and p.z < 0.53:      # helle Platte unten bleibt (bis z 0,52)
                return None
            return (col[0], col[1], col[2], 1.0)
        paint(sel, rec)


def build_tank():
    ground_static(90.0)
    fix_rollo_back()
    vs = world_verts()
    # Turm: oberer Teil; Rohr: vorderster Punkt in Turmhöhe
    zt = 1.0
    barrel = [v for v in vs if v.z > zt and v.y < -0.6]
    tip_y = min(v.y for v in barrel)
    tip = [v for v in barrel if v.y < tip_y + 0.03]
    muzzle = sum(tip, Vector()) / len(tip)
    print("ROHR", tuple(round(c, 3) for c in muzzle), "Punkte", len(barrel))
    arm = new_armature([
        ("Root", (0, 0, 0.0), (0, 0, 0.5), None),
        ("Hull", (0, 0, 0.5), (0, 0, 0.95), "Root"),
        ("Turret", (0, 0, 0.95), (0, 0, 1.6), "Hull"),
    ])

    def weights(p):
        tur = ramp(p.z, zt - 0.08, zt + 0.04)
        return {"Turret": tur, "Hull": 1.0 - tur}

    bind(arm, weights)

    def pose(bob=0.0, recoil=0.0, pitch=0.0, yaw=0.0, hop=0.0, tilt=0.0):
        reset_pose(arm)
        move_world(arm, "Hull", (0, 0, bob))
        move_world(arm, "Turret", (0, recoil, 0))
        rot_world(arm, "Turret", (1, 0, 0), pitch)
        rot_world(arm, "Turret", (0, 0, 1), yaw)
        rot_world(arm, "Hull", (1, 0, 0), tilt)
        move_world(arm, "Root", (0, 0, hop))

    make_actions(arm, [
        ("Idle", [(i * 15, (lambda t=i / 4.0: pose(0.012 * math.sin(t * 4 * math.pi), 0, 0, 3 * math.sin(t * 2 * math.pi)))) for i in range(5)]),
        # Wumms: Turm stößt zurück und kippt hoch, die Wanne wippt nach
        ("Shoot", [(0, lambda: pose()), (2, lambda: pose(-0.02, 0.1, 8, 0, 0, -3)),
                   (6, lambda: pose(0.01, 0.04, 3, 0, 0, 1)), (12, lambda: pose())]),
        ("Victory", [(i * 6, (lambda t=i / 8.0: pose(0, 0, 6, 25 * math.sin(t * 2 * math.pi), 0.1 * abs(math.sin(t * 4 * math.pi))))) for i in range(9)]),
    ])
    m = add_muzzle(arm, "Turret", muzzle + Vector((0, -0.03, 0)))
    print("MUENDUNG", tuple(round(c, 3) for c in m.matrix_world.translation))
    return arm


arm = {"pip": build_humanoid, "nova": build_humanoid, "fuenkchen": build_dragon, "rollo": build_tank}.get(hero, build_armed)()
tris = sum(len(p.vertices) - 2 for o in scene.objects if o.type == 'MESH' for p in o.data.polygons)
print("DREIECKE", tris, "TEXTUREN", [tuple(i.size) for i in bpy.data.images], "AKTIONEN", [a.name for a in bpy.data.actions])
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS',
                          export_yup=True, export_apply=False, export_force_sampling=True)
print("FERTIG", out)
