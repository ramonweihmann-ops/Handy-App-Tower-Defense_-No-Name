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
import os
DEBUG_TWIST = bool(os.environ.get("DREHUNG"))
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


# Dusty Jo (Intelligentes Rig, Seiten aus der Textur bestimmt, wie in build_dusty_jo.py)
DUSTY = {"Bone_000": "mixamorig:Hips", "Bone_016": "mixamorig:Head", "Bone_023": "mixamorig:RightHand",
         "Bone_018": "mixamorig:LeftHand", "Bone_012": "mixamorig:RightFoot", "Bone_008": "mixamorig:LeftFoot",
         "Bone_025": "mixamorig:RightArm", "Bone_024": "mixamorig:RightForeArm", "Bone_020": "mixamorig:LeftArm",
         "Bone_019": "mixamorig:LeftForeArm", "Bone_005": "mixamorig:Spine2", "Bone_026": "mixamorig:RightShoulder",
         "Bone_021": "mixamorig:LeftShoulder"}


def normalize_bones(arm):
    names = [b.name for b in arm.data.bones]
    if "mixamorig:Hips" in names:
        return
    if hero == "dusty":
        ren = dict(DUSTY)
    else:
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


# Meshy-Waffen (Vorlage_Raw/Waffen_Roh/<id>_waffe_v1/<id>_waffe_reduziert.glb, Auftrag W2). Im Modell zeigt die
# Mündung nach -X, oben ist +Z. Punkte (x, z) am Seitenraster abgelesen: grip = Griff der rechten Hand,
# fore = Stelle für die linke Hand, muzzle = Mündung. len = Länge an der 2,0 hohen Figur (LIESMICH, Anteil der
# Körperhöhe). hold: rifle (Anschlag an der rechten Schulter, zweihändig), shoulder (Werfer auf der Schulter),
# pistol (einhändig, Arm gestreckt)
WEAPONS = {
    "dusty": {"hold": "pistol", "len": 0.6, "grip": (0.69, -0.30), "muzzle": (-0.935, 0.41)},
    "iska": {"hold": "rifle", "len": 0.94, "grip": (0.74, -0.36), "fore": (-0.22, -0.27), "muzzle": (-0.88, 0.22)},
    "brocken": {"hold": "shoulder", "len": 0.98, "grip": (0.55, -0.44), "fore": (-0.44, -0.5), "muzzle": (-0.935, 0.275)},
    "volta": {"hold": "pistol", "len": 0.70, "grip": (0.715, -0.275), "muzzle": (-0.935, 0.25)},
    "kalle": {"hold": "pistol", "len": 0.62, "grip": (0.52, -0.50), "muzzle": (-0.935, 0.14)},
    "margot": {"hold": "rifle", "len": 1.04, "grip": (0.74, -0.165), "fore": (-0.05, 0.0), "muzzle": (-0.935, 0.24)},
    "lynx": {"hold": "rifle", "len": 1.34, "grip": (0.52, -0.22), "fore": (-0.22, -0.055), "muzzle": (-0.935, 0.0)},
    "fritzi": {"hold": "rifle", "len": 1.30, "grip": (0.495, -0.165), "fore": (-0.3, 0.0), "muzzle": (-0.935, 0.18)},
}
WEAPON_DIR = sys.argv[-2].split("Vorlage_Raw")[0] + "Vorlage_Raw/Waffen_Roh"
# Menü-Pose wie auf dem Heldenbild (game/ui/heroes2d): raised = Arm seitlich gestreckt, Waffe zielt nach außen
# (Waffe neben dem Kopf nach oben ragt bei den großen Comic-Köpfen immer ins Gesicht), across = Waffe
# quer vor dem Körper, shoulder = Werfer auf der Schulter. left: hip (Faust in der Hüfte), tablet, low (locker)
POSES = {"dusty": ("raised", "hip"), "volta": ("raised", "tablet"), "kalle": ("raised", "low"),
         "iska": ("across", None), "margot": ("across", None), "lynx": ("across", None), "fritzi": ("across", None),
         "brocken": ("shoulder", "hip")}


def load_weapon(spec):
    """Meshy-Waffe laden und in den Waffenraum legen: +Y = Lauf nach vorn, +Z = oben, Ursprung = Griff.
    Gibt die Punkte fore und muzzle im Waffenraum zurück."""
    before = set(scene.objects)
    bpy.ops.import_scene.gltf(filepath="%s/%s_waffe_v1/%s_waffe_reduziert.glb" % (WEAPON_DIR, hero, hero))
    new = [o for o in scene.objects if o not in before]
    w = [o for o in new if o.type == 'MESH'][0]
    for o in new:
        if o != w:
            bpy.data.objects.remove(o, do_unlink=True)
    w.parent = None
    bpy.ops.object.select_all(action='DESELECT')
    w.select_set(True)
    bpy.context.view_layer.objects.active = w
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    vs = [v.co for v in w.data.vertices]
    length = max(v.x for v in vs) - min(v.x for v in vs)
    sc = spec["len"] / length
    g = Vector((spec["grip"][0], 0.0, spec["grip"][1]))
    # Modell (x, y, z) -> Waffenraum (y, -x, z): Mündung -X wird +Y
    rot = Matrix(((0, 1, 0), (-1, 0, 0), (0, 0, 1))).to_4x4()
    m = Matrix.Scale(sc, 4) @ rot @ Matrix.Translation(-g)
    w.data.transform(m)
    w.name = "Weapon"
    for mt in w.data.materials:   # matt wie die Figuren
        for n in mt.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                for key, val in (("Metallic", 0.0), ("Roughness", 0.65)):
                    for l in list(n.inputs[key].links):
                        mt.node_tree.links.remove(l)
                    n.inputs[key].default_value = val
    for img in bpy.data.images:
        if img.size[0] > 1024:
            img.scale(1024, 1024)
            img.pack()
    pt = lambda xz: (m @ Vector((xz[0], 0.0, xz[1])))
    fore = pt(spec["fore"]) if "fore" in spec else None
    # Waffe am Griff und am Vorderschaft vermessen: halbe Griffbreite (rechte Seite), Unterkante unter dem Vorderschaft
    vs = [v.co for v in w.data.vertices]
    near = [v for v in vs if abs(v.y) < 0.04 and abs(v.z) < 0.05]
    spec["_grip_hw"] = max((v.x for v in near), default=0.03)
    if fore is not None:
        # halbe Breite des Vorderschafts zur linken Seite (dort liegt die linke Hand an)
        side = [v for v in vs if abs(v.y - fore.y) < 0.04 and abs(v.z - fore.z) < 0.05]
        spec["_fore_hw"] = max((-v.x for v in side), default=0.03)
    print("WAFFE Griffbreite", round(2 * spec["_grip_hw"], 3), "Vorderschaft", round(2 * spec.get("_fore_hw", 0), 3))
    return w, fore, pt(spec["muzzle"])


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


def add_tablet(arm, pose_fn):
    """Voltas Tablet (wie auf dem Heldenbild) starr an der linken Hand: dunkler Rahmen, türkiser Bildschirm."""
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    frame_o = bpy.context.object
    frame_o.scale = (0.24, 0.028, 0.32)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bev = frame_o.modifiers.new("Rund", 'BEVEL')
    bev.width, bev.segments = 0.02, 3
    bpy.ops.object.modifier_apply(modifier="Rund")
    frame_o.data.materials.append(mat("Tablet_Rahmen", (0.12, 0.16, 0.3)))
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.016, 0))
    screen = bpy.context.object
    screen.scale = (0.2, 0.008, 0.27)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    screen.data.materials.append(mat("Tablet_Bild", (0.3, 0.85, 0.95), emit=0.6))
    bpy.ops.object.select_all(action='DESELECT')
    frame_o.select_set(True)
    screen.select_set(True)
    bpy.context.view_layer.objects.active = frame_o
    bpy.ops.object.join()
    tab = bpy.context.object
    tab.name = "Tablet"
    tab.parent = arm
    tab.parent_type = 'BONE'
    tab.parent_bone = "mixamorig:LeftHand"
    tab.matrix_parent_inverse = Matrix.Identity(4)
    # in der Menü-Pose: Tablet aufrecht vor der linken Hand, Bildschirm nach vorn (-Y) und leicht nach oben gekippt
    pose_fn(0.0)
    pb = arm.pose.bones["mixamorig:LeftHand"]
    tail = arm.matrix_world @ pb.matrix @ Matrix.Translation((0, pb.bone.length, 0))
    want = Matrix.Translation(tail.translation + Vector((0.02, -0.03, 0.08))) @ Matrix.Rotation(math.radians(-20), 4, "X")
    tab.matrix_basis = tail.inverted() @ want
    update()
    reset_pose(arm)


def hand_data(arm, side):
    """Echte Hand aus dem Netz vermessen (in Knochenkoordinaten der Ruhehaltung): Mitte der Faust, Richtung der
    Finger (längste Achse) und der Handfläche (flachste Achse, zeigt zum Körper hin)."""
    import numpy as np
    bone = arm.data.bones["mixamorig:%sHand" % side]
    names = {bone.name} | {c.name for c in bone.children_recursive}
    idx = {body.vertex_groups[n].index for n in names if n in body.vertex_groups}
    Mb = arm.matrix_world @ bone.matrix_local
    inv = Mb.inverted()
    pts = []
    for v in body.data.vertices:
        if sum(g.weight for g in v.groups if g.group in idx) >= 0.6:
            pts.append(inv @ (body.matrix_world @ v.co))
    P = np.array([tuple(p) for p in pts])
    c = P.mean(axis=0)
    ev, evec = np.linalg.eigh(np.cov((P - c).T))
    fing = Vector(evec[:, 2])
    if fing.dot(Vector((0, 1, 0))) < 0:
        fing = -fing
    palm = Vector(evec[:, 0])
    toward = 1.0 if side == "Right" else -1.0      # Handfläche zeigt in der A-Haltung zur Körpermitte
    if (Mb.to_3x3() @ palm).x * toward < 0:
        palm = -palm
    size = np.sqrt(ev) * 2
    print("HANDMASS", side, len(pts), "Punkte, Mitte", tuple(round(x, 3) for x in c), "Größe", tuple(round(float(x), 3) for x in size))
    return {"c": Vector(c), "f": fing.normalized(), "p": palm.normalized(), "thick": float(size[0])}


# Daumen in Skeletten ohne sprechende Namen (Seiten wie in DUSTY/BROCKEN bestimmt)
THUMBS = {"dusty": {"Bone_036", "Bone_037", "Bone_038"}, "brocken": {"Bone_034", "Bone_035", "Bone_039", "Bone_040"}}


def finger_curl(arm, side, hd, amount=1.0):
    """Finger zur Faust krümmen, wo das Skelett Fingerknochen hat: jeder Fingerknochen dreht um die Querachse der
    Hand (Finger x Handfläche), so dass die Fingerspitzen zur Handfläche gehen. Daumen schwächer."""
    hand = arm.data.bones["mixamorig:%sHand" % side]
    axis_rest = hand.matrix_local.to_3x3() @ hd["f"].cross(hd["p"]).normalized()
    for b in hand.children_recursive:
        n = b.name
        if n.endswith("_End") or n.endswith("4") or b.length < 0.004:
            continue
        depth = 0
        q = b
        while q.parent and q.parent != hand:
            depth += 1
            q = q.parent
        thumb = "Thumb" in n or n in THUMBS.get(hero, set())
        deg = ([30, 35, 30] if thumb else [70, 85, 65])[min(depth, 2)] * amount
        local = (b.matrix_local.to_3x3().inverted() @ axis_rest).normalized()
        pb = arm.pose.bones[n]
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Quaternion(local, math.radians(deg))
    update()


def build_armed():
    arm = [o for o in scene.objects if o.type == 'ARMATURE'][0]
    arm.name = "Armature"
    normalize_bones(arm)
    scale_rigged(arm)
    if hero == "volta":
        fix_volta_pocket()
    spec = WEAPONS[hero]
    hold = spec["hold"]
    weapon, fore_w, muzzle_w = load_weapon(spec)
    reset_pose(arm)
    HR, HL = hand_data(arm, "Right"), hand_data(arm, "Left")
    sh_r = bone_head(arm, "mixamorig:RightArm")
    sh_l = bone_head(arm, "mixamorig:LeftArm")
    FWD, UP = Vector((0, -1, 0)), Vector((0, 0, 1))
    kind, left = POSES[hero]

    def frame(barrel, up=UP):
        b = barrel.normalized()
        u = (up - b * up.dot(b)).normalized()
        return b, u, b.cross(u)

    roll = {"Right": 0.0, "Left": 0.0}
    last_twist = [0.0]

    def orient(hd, f, d, side="Right"):
        """Drehung der Hand: Finger nach f, Handfläche nach d (beides Weltrichtungen), dazu die je Champion gesuchte
        Drehung um die Fingerachse (roll), die das Handgelenk am wenigsten verdreht."""
        if roll[side]:
            d = Matrix.Rotation(math.radians(roll[side]), 3, f.normalized()) @ d
        fl = hd["f"]
        pl = (hd["p"] - fl * hd["p"].dot(fl)).normalized()
        L = Matrix((fl, pl, fl.cross(pl))).transposed()
        f = f.normalized()
        d = (d - f * d.dot(f)).normalized()
        W = Matrix((f, d, f.cross(d))).transposed()
        return W @ L.transposed()

    def place(side, hd, center, f, d, pole):
        """Handmitte (Faust) genau an center, Hand gedreht nach f/d, Arm per IK. Der Ellbogen darf um die Achse
        Schulter-Ziel ausweichen: genommen wird die Richtung mit der kleinsten Verdrehung am Handgelenk."""
        M = orient(hd, f, d, side)
        up, lo = "mixamorig:%sArm" % side, "mixamorig:%sForeArm" % side
        pb = arm.pose.bones["mixamorig:%sHand" % side]
        fpb = arm.pose.bones[lo]
        saved = {n: (arm.pose.bones[n].rotation_quaternion.copy(), arm.pose.bones[n].location.copy()) for n in (up, lo, pb.name)}

        def solve(pl):
            for n, (r, l) in saved.items():
                arm.pose.bones[n].rotation_quaternion = r
                arm.pose.bones[n].location = l
            update()
            for _ in range(2):   # Handgelenk so legen, dass die Faustmitte am Ziel sitzt
                ik(arm, up, lo, center - M @ hd["c"], pl)
            pb.matrix = Matrix.Translation(pb.matrix.translation) @ M.to_4x4()
            update()
            qh = pb.matrix_basis.to_quaternion()   # Drehung gegenüber der Ruhestellung: die zählt für die Haut
            a = 2.0 * math.atan2(qh.y, qh.w)
            return (a + math.pi) % (2 * math.pi) - math.pi

        axis = (center - bone_head(arm, up)).normalized()
        best = None
        for deg in (-75, -50, -25, 0, 25, 50, 75):
            pl = Matrix.Rotation(math.radians(deg), 3, axis) @ Vector(pole)
            a = solve(pl)
            cost = abs(a) + 0.004 * abs(deg)   # bei gleicher Verdrehung lieber nah an der gewünschten Richtung
            if best is None or cost < best[0]:
                best = (cost, pl)
        ang = solve(best[1])
        last_twist[0] = ang
        if DEBUG_TWIST and side == "Right":
            print("DREHUNG", round(math.degrees(ang), 1))
        # Rest der Verdrehung zur Hälfte auf den Unterarm, sonst verdreht sich die Haut wie ein Bonbonpapier
        Mf = fpb.matrix.to_3x3().normalized()
        fpb.matrix = Matrix.Translation(fpb.matrix.translation) @ (Mf @ Matrix.Rotation(ang * 0.5, 3, 'Y')).to_4x4()
        update()
        pb.matrix = Matrix.Translation(pb.matrix.translation) @ M.to_4x4()
        update()
        head = pb.matrix.translation.copy()
        finger_curl(arm, side, hd, 0.5 if side == "Right" else 0.3)   # stärker zerknittern Meshys verschmolzene Finger
        return (head + M @ hd["c"] - center).length   # wie weit die Faust das Ziel verfehlt (Arm zu kurz)

    def grip(center, barrel, up=UP, two=True, pole_r=(-0.7, 0.6, -0.5), far=False):
        """Rechte Faust um den Griff (Griff läuft senkrecht durch die Faust, Waffe sitzt darüber); bei Gewehren
        die linke Hand flach unter den Vorderschaft, Finger quer, Handfläche nach oben."""
        b, u, x = frame(barrel, up)
        # center = Griffmitte; die Faust liegt rechts außen am Griff an, Handfläche flach zum Griff
        side = spec["_grip_hw"] + 0.45 * HR["thick"]
        # far: Faust auf der Rückseite des Griffs (erhobene Waffe: Griff und Finger zum Betrachter, Handrücken weg)
        if far:
            place("Right", HR, center - x * side, b, x, pole_r)
        else:
            place("Right", HR, center + x * side, b, -x, pole_r)
        if two and fore_w is not None:
            fp = center + x * fore_w.x + b * fore_w.y + u * fore_w.z
            # linke Hand flach von links an den Vorderschaft, Finger nach vorn, Handfläche zur Waffe
            miss = place("Left", HL, fp - x * (spec["_fore_hw"] + 0.45 * HL["thick"]), b - u * 0.25, x, (0.6, 0.3, -1.0))
            if miss > 0.03:   # Vorderschaft außer Reichweite: lieber locker hängen lassen als in der Luft greifen
                left_free("low", 0.0)
        return b, u, x

    def left_free(how, w):
        if how == "hip":
            point_bones(arm, {"mixamorig:LeftArm": Vector((0.6, 0.1, -1.0)), "mixamorig:LeftForeArm": Vector((-0.75, -0.3, -0.35 + 0.03 * w))},
                        ["mixamorig:LeftArm", "mixamorig:LeftForeArm"])
        elif how == "tablet":
            point_bones(arm, {"mixamorig:LeftArm": Vector((0.3, -0.45, -0.85)), "mixamorig:LeftForeArm": Vector((-0.15, -1.0, 0.35 + 0.03 * w)),
                              "mixamorig:LeftHand": Vector((-0.1, -1.0, 0.5))},
                        ["mixamorig:LeftArm", "mixamorig:LeftForeArm", "mixamorig:LeftHand"])
        else:
            point_bones(arm, {"mixamorig:LeftArm": Vector((0.3, -0.05, -1.0)), "mixamorig:LeftForeArm": Vector((0.15, -0.35, -1.0))},
                        ["mixamorig:LeftArm", "mixamorig:LeftForeArm"])

    def body(spine=0.0, hips_up=0.0):
        reset_pose(arm)
        if "mixamorig:Spine2" in arm.pose.bones:
            rot_world(arm, "mixamorig:Spine2", (1, 0, 0), spine)
        move_world(arm, "mixamorig:Hips", (0, 0, hips_up))
        update()

    # Kampf (von hinten oben gesehen): die Waffe rechts außen neben dem Körper, sonst verdeckt sie der Kopf
    AIM = {"rifle": Vector((-0.2, -0.2, -0.3)), "shoulder": Vector((-0.03, -0.16, -0.3)),
           "pistol": Vector((-0.22, -0.32, -0.02))}[hold]

    def aim(r=0.0, spine=0.0):
        body(spine)
        c = sh_r + AIM + Vector((0, 0.05 * r, 0.02 * r))
        grip(c, FWD + UP * (0.06 + 0.25 * r), two=hold != "pistol")
        if hold == "pistol":
            left_free("low", 0.0)

    def idle(t):
        w = math.sin(t * 2 * math.pi)
        body(1.5 * w, 0.008 * math.sin(t * 4 * math.pi))
        c = sh_r + Vector((-0.16, -0.14, -0.4 + 0.01 * w))
        grip(c, Vector((0.1, -1.0, -0.75)), two=hold != "pistol")
        if hold == "pistol":
            left_free("low", w)

    def victory(t):
        w = math.sin(t * 2 * math.pi)
        body(-3, 0.06 * abs(w))
        c = sh_r + Vector((-0.24, -0.06, 0.34 + 0.03 * w))
        grip(c, Vector((-0.1, -0.2, 1.0)), Vector((-1.0, 0.0, 0.0)), two=False, pole_r=(-0.8, 0.2, -1.0))
        point_bones(arm, {"mixamorig:LeftArm": Vector((0.5, -0.1, 0.9 + 0.1 * w)), "mixamorig:LeftForeArm": Vector((0.35, -0.1, 1.0))},
                    ["mixamorig:LeftArm", "mixamorig:LeftForeArm"])

    def menu_pose(t):
        """Heldenpose wie auf dem Heldenbild, mit leichtem Atmen (t 0..1)."""
        w = math.sin(t * 2 * math.pi)
        body(1.0 * w, 0.006 * w)
        if kind == "raised":
            # Revolverhelden-Pose: breiter Stand, Oberkörper und Blick zum Ziel, Arm zur Seite gestreckt, Waffe im
            # Profil, Faust hinter dem Griff; linke Faust vorn an der Hüfte (von vorn sichtbar)
            for leg, sgn in (("mixamorig:RightUpLeg", -1), ("mixamorig:LeftUpLeg", 1)):
                if leg in arm.pose.bones:
                    rot_world(arm, leg, (0, 1, 0), 9 * sgn)
            if "mixamorig:Spine2" in arm.pose.bones:
                rot_world(arm, "mixamorig:Spine2", (0, 0, 1), 10)
            if "mixamorig:Head" in arm.pose.bones:
                rot_world(arm, "mixamorig:Head", (0, 0, 1), 14)
                rot_world(arm, "mixamorig:Head", (1, 0, 0), -4)
            update()
            c = sh_r + Vector((-0.4, -0.24, 0.02 + 0.008 * w))
            grip(c, Vector((-0.85, -0.5, 0.12)), two=False, pole_r=(-0.2, 0.6, -1.0))
            if left == "tablet":
                left_free(left, w)
            else:
                hip = bone_head(arm, "mixamorig:LeftArm") + Vector((0.1, -0.12, -0.46 + 0.006 * w))
                place("Left", HL, hip, Vector((-0.2, -0.3, -1.0)), Vector((-1.0, 0.2, 0.0)), (1.0, 0.6, 0.2))
        elif kind == "shoulder":
            c = sh_r + Vector((-0.03, -0.1, -0.3 + 0.006 * w))
            grip(c, Vector((-0.12, -0.9, 0.42)), two=False)
            left_free(left, w)
        else:
            b = Vector((0.85, -0.42, -0.05 if hero == "lynx" else 0.15))
            c = sh_r + Vector((0.04, -0.26, -0.32 + 0.008 * w))
            grip(c, b, pole_r=(-0.6, 0.5, -0.7))

    # Handdrehung um den Griff je Champion suchen: kleinste Verdrehung am rechten Handgelenk in Schuss und Heldenpose
    best_roll = None
    for r in range(-90, 91, 15):
        roll["Right"] = float(r)
        aim(0.0)
        t1 = abs(last_twist[0])
        menu_pose(0.0)
        t2 = abs(last_twist[0]) if kind != "across" else abs(last_twist[0])
        cost = t1 + t2 + 0.002 * abs(r)
        if best_roll is None or cost < best_roll[0]:
            best_roll = (cost, r, t1, t2)
    roll["Right"] = float(best_roll[1])
    print("HANDDREHUNG", best_roll[1], "Grad, Rest-Verdrehung Schuss", round(math.degrees(best_roll[2])), "Pose", round(math.degrees(best_roll[3])))
    reset_pose(arm)

    make_actions(arm, [
        ("Idle", [(i * 15, (lambda t=i / 4.0: idle(t))) for i in range(5)]),
        ("Shoot", [(0, lambda: aim(0.0)), (2, lambda: aim(1.0, -4)), (6, lambda: aim(0.35, -1)), (12, lambda: aim(0.0))]),
        ("Victory", [(i * 12, (lambda t=i / 4.0: victory(t))) for i in range(5)]),
        ("Pose", [(i * 15, (lambda t=i / 4.0: menu_pose(t))) for i in range(5)]),
    ])
    if left == "tablet":
        add_tablet(arm, menu_pose)

    # Waffe starr an der rechten Hand: Griffmitte in der Faustmitte. Die Hand steht zur Waffe in jeder Pose gleich
    # (grip/place), deshalb reicht die Lage aus der Zielhaltung.
    socket = bpy.data.objects.new("WeaponSocket", None)
    scene.collection.objects.link(socket)
    socket.parent = arm
    socket.parent_type = 'BONE'
    socket.parent_bone = "mixamorig:RightHand"
    socket.matrix_parent_inverse = Matrix.Identity(4)
    weapon.parent = socket
    weapon.matrix_parent_inverse = Matrix.Identity(4)
    weapon.matrix_basis = Matrix.Identity(4)
    muzzle = bpy.data.objects.new("Muzzle", None)
    scene.collection.objects.link(muzzle)
    muzzle.parent = weapon
    muzzle.location = muzzle_w
    aim(0.0)
    b, u, x = frame(FWD + UP * 0.06)
    pb = arm.pose.bones["mixamorig:RightHand"]
    center = pb.matrix.translation + pb.matrix.to_3x3() @ HR["c"]
    center = center - x * (spec["_grip_hw"] + 0.45 * HR["thick"])   # zurück zur Griffmitte
    want = Matrix.Translation(center) @ Matrix((x, b, u)).transposed().to_4x4()
    tail = arm.matrix_world @ pb.matrix @ Matrix.Translation((0, pb.bone.length, 0))
    socket.matrix_basis = tail.inverted() @ want
    update()
    print("FAUST", tuple(round(c, 3) for c in center), "MUENDUNG", tuple(round(c, 3) for c in muzzle.matrix_world.translation))
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
