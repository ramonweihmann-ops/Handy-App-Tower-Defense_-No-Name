"""Baut aus den Meshy-Rohmodellen (Vorlage_Raw/Helden_Roh/<id>_comic_v1) die fertigen Spiel-GLBs für
Pip, Nova (humanoides Meshy-Rig mit Mixamo-Namen), Fünkchen und Rollo (ohne Rig: Skelett entsteht hier).
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


arm = {"pip": build_humanoid, "nova": build_humanoid, "fuenkchen": build_dragon, "rollo": build_tank}[hero]()
tris = sum(len(p.vertices) - 2 for o in scene.objects if o.type == 'MESH' for p in o.data.polygons)
print("DREIECKE", tris, "TEXTUREN", [tuple(i.size) for i in bpy.data.images], "AKTIONEN", [a.name for a in bpy.data.actions])
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS',
                          export_yup=True, export_apply=False, export_force_sampling=True)
print("FERTIG", out)
