# Gemeinsame Bausteine für die Premium-Helden mit zwei Armen und zwei Beinen (Nerd, Biker; Wunsch 28.11.2026):
# Hände mit vier Fingern und Daumen, runde Kästen, Ringe, Skelett, Gewichte, Armhaltung über Zielpunkte.
# Gebaut wie der neue Fünkchen (tools/heroes/fuenkchen_premium.py): weiche Formen aus Metaballs, neu vernetzt und
# geglättet, im Raum bemalt. Figur 2,0 hoch, Füße auf z = 0, Blick nach -Y; links der Figur ist +x.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fuenkchen_premium import *
from mathutils.kdtree import KDTree

# ---------------------------------------------------------------- Formen

def blob(name, parts, voxel=0.012, smooth=6, ground=False):
    """Weiche Form aus Kugeln und Kapseln: parts = [("e", Mitte, Halbachsen[, Drehung]) | ("c", von, bis, Radius)].
    ground: unten bei z = 0 flach abschneiden (Sohlen); sonst bleibt die Form rundum rund."""
    R = mb_family(name); up = Vector((0, 0, 0.0 if ground else 20.0))
    for p in parts:
        if p[0] == "e":
            mb_ell(R, tuple(Vector(p[1]) + up), tuple(p[2]), p[3] if len(p) > 3 else None)
        else:
            mb_caps(R, tuple(Vector(p[1]) + up), tuple(Vector(p[2]) + up), p[3])
    g = mb_to_mesh(R)
    finish_skin(g, voxel, 1.0, smooth_it=smooth)
    g.data.transform(Matrix.Translation(-up)); g.data.update()
    return g

def lock(name, p0, p1, p2, r, flat=0.75, n=9, segs=10, axis=None):
    """Haarsträhne: dick am Ansatz, läuft in eine runde Spitze aus"""
    pts = [qbez(Vector(p0), Vector(p1), Vector(p2), t) for t in np.linspace(0, 1, n)]
    rad = [r * (0.75 + 0.5 * math.sin(math.pi * min(t * 1.6, 1.0) * 0.5) - 0.25) * (1 - t ** 2.2) + 0.012 * r for t in np.linspace(0, 1, n)]
    return sweep(name, pts, rad, segs=segs, flat=flat, flat_axis=axis)

def place(o, origin, X, Y, Z):
    """Teil aus seinem eigenen Maß (x, y, z) in die Welt setzen: Achsen X, Y, Z ab origin"""
    M = Matrix((Vector(X), Vector(Y), Vector(Z))).transposed().to_4x4()
    M.translation = Vector(origin)
    o.data.transform(M); o.data.update()
    return o

def mirror_x(o):
    """an der Mitte spiegeln (für die rechte Körperseite), Flächen wieder nach außen drehen"""
    o.data.transform(Matrix.Scale(-1, 4, (1, 0, 0)))
    bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.reverse_faces(bm, faces=bm.faces); bm.to_mesh(o.data); bm.free()
    o.data.update()
    return o

def rounded_box(name, c, half, r, rot=None, segs=3):
    """Kasten mit runden Kanten (Rucksack, Taschen, Laptop)"""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=2.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * half[0], v.co.y * half[1], v.co.z * half[2]))
    o = finish(name, bm, smooth=True)
    md = o.modifiers.new("Rund", 'BEVEL'); md.width = r; md.segments = segs; md.limit_method = 'NONE'; apply_mod(o, md)
    M = (rot.to_matrix().to_4x4() if rot is not None else Matrix())
    M.translation = Vector(c)
    o.data.transform(M); o.data.update()
    for p in o.data.polygons:
        p.use_smooth = True
    return o

def torus(name, c, axis, R, r, n=18, m=8, squash=1.0, flat=1.0):
    """Ring um die Achse axis; squash staucht ihn in einer Querrichtung, flat macht den Querschnitt flacher"""
    axis = Vector(axis).normalized()
    e1 = axis.cross(Vector((0, 0, 1)) if abs(axis.z) < 0.9 else Vector((1, 0, 0))).normalized(); e2 = axis.cross(e1)
    bm = bmesh.new(); rings = []
    for i in range(n):
        a = i * 2 * math.pi / n; out = e1 * math.cos(a) + e2 * (math.sin(a) * squash)
        rings.append([bm.verts.new(Vector(c) + out * (R + r * flat * math.cos(q)) + axis * (r * math.sin(q))) for q in [j * 2 * math.pi / m for j in range(m)]])
    for i in range(n):
        r0, r1 = rings[i], rings[(i + 1) % n]
        for j in range(m):
            bm.faces.new([r0[j], r1[j], r1[(j + 1) % m], r0[(j + 1) % m]])
    return finish(name, bm)

def hand_mesh(name, k=1.0, curls=(0.3, 0.3, 0.3, 0.3), thumb=0.3, spread=0.0, thumb_in=0.0):
    """Linke Hand im eigenen Maß: Finger nach +y, Handrücken nach +z, Daumen nach -x … (zum Körper hin, wenn die
    Hand herabhängt). curls: Beugung je Finger (Zeige-, Mittel-, Ring-, kleiner Finger; 0 gestreckt, 1 Faust).
    Alles ist eine glatte Form: Handfläche, Finger und Daumen gehen weich ineinander über."""
    parts = [("e", (0, 0.055 * k, 0), (0.07 * k, 0.07 * k, 0.034 * k)), ("e", (0, 0.0, 0), (0.05 * k, 0.045 * k, 0.036 * k))]
    xs = (-0.048, -0.016, 0.016, 0.046); Ls = (0.1, 0.108, 0.1, 0.085); rs = (0.0225, 0.023, 0.022, 0.02)
    for x, L, r, c in zip(xs, Ls, rs, curls):
        p = Vector((x * k, 0.108 * k, 0.0)); ang = 0.0; yaw = spread * (x / 0.048) * 0.25
        for frac, bend in ((0.42, 62), (0.33, 78), (0.25, 55)):
            ang += math.radians(bend) * c
            d = Vector((math.sin(yaw) * math.cos(ang), math.cos(yaw) * math.cos(ang), -math.sin(ang)))
            q = p + d * (L * k * frac)
            parts.append(("c", p, q, r * k)); p = q
    # Daumen: setzt seitlich unten an der Handfläche an
    p = Vector((-0.058 * k, 0.03 * k, -0.008 * k)); a0 = math.radians(48 - 30 * thumb_in)
    d = Vector((-math.sin(a0), math.cos(a0), -0.25 - 0.5 * thumb)).normalized()
    q = p + d * (0.055 * k); parts.append(("c", p, q, 0.026 * k))
    d2 = (d + Vector((0.45 * thumb + 0.35 * thumb_in, 0.3, -0.55 * thumb))).normalized()
    parts.append(("c", q, q + d2 * (0.048 * k), 0.024 * k))
    g = blob(name, parts, voxel=0.0075, smooth=5)
    return g

# ---------------------------------------------------------------- Skelett, Gewichte, Haltung

def biped(J, extra=()):
    """Skelett aus Gelenkpunkten J (linke Seite, die rechte wird gespiegelt). Namen ohne Vorsatz: Hips, Spine, Chest,
    Neck, Head, Shoulder.L, UpperArm.L, ForeArm.L, Hand.L, UpLeg.L, Leg.L, Foot.L (und .R)."""
    mir = lambda p: (-p[0], p[1], p[2])
    bones = [("Root", (0, 0, 0), (0, 0, 0.3), None), ("Hips", J["hips"], J["spine"], "Root"), ("Spine", J["spine"], J["chest"], "Hips"),
             ("Chest", J["chest"], J["neck"], "Spine"), ("Neck", J["neck"], J["head"], "Chest"), ("Head", J["head"], J["top"], "Neck")]
    for sfx, f in ((".L", lambda p: p), (".R", mir)):
        bones += [("Shoulder" + sfx, f(J["clav"]), f(J["shoulder"]), "Chest"), ("UpperArm" + sfx, f(J["shoulder"]), f(J["elbow"]), "Shoulder" + sfx),
                  ("ForeArm" + sfx, f(J["elbow"]), f(J["wrist"]), "UpperArm" + sfx), ("Hand" + sfx, f(J["wrist"]), f(J["palm"]), "ForeArm" + sfx),
                  ("UpLeg" + sfx, f(J["hip"]), f(J["knee"]), "Hips"), ("Leg" + sfx, f(J["knee"]), f(J["ankle"]), "UpLeg" + sfx),
                  ("Foot" + sfx, f(J["ankle"]), f(J["toe"]), "Leg" + sfx)]
    return new_armature(bones + list(extra))

def auto_bind(body, arm, deform):
    """Gewichte der Haut nach der Nähe zu den Knochen (Bone Heat), nur mit den genannten Knochen"""
    saved = {b.name: b.use_deform for b in arm.data.bones}
    for b in arm.data.bones:
        b.use_deform = b.name in deform
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    for b in arm.data.bones:
        b.use_deform = saved[b.name]
    for md in list(body.modifiers):                 # der Bezug zum Skelett kommt am Ende einmal für die ganze Figur
        if md.type == 'ARMATURE':
            body.modifiers.remove(md)
    body.parent = None

def copy_weights(o, src, bvh=None):
    """Gewichte vom nächstgelegenen Punkt einer schon gewichteten Haut übernehmen (Gurte, Taschen: bewegen sich mit ihr)"""
    kd = KDTree(len(src.data.vertices))
    for v in src.data.vertices:
        kd.insert(v.co, v.index)
    kd.balance()
    names = {g.index: g.name for g in src.vertex_groups}
    for v in o.data.vertices:
        _, idx, _ = kd.find(v.co)
        for e in src.data.vertices[idx].groups:
            if e.weight > 0.002:
                (o.vertex_groups.get(names[e.group]) or o.vertex_groups.new(name=names[e.group])).add([v.index], e.weight, 'REPLACE')

def bone_head(arm, name):
    return arm.matrix_world @ arm.pose.bones[name].head

def point_bone(arm, name, direction):
    """Knochen in eine Weltrichtung drehen"""
    pb = arm.pose.bones[name]; cur = pb.matrix.copy()
    q = cur.to_3x3().col[1].normalized().rotation_difference(Vector(direction).normalized())
    pb.matrix = Matrix.Translation(cur.translation) @ q.to_matrix().to_4x4() @ Matrix.Translation(-cur.translation) @ cur
    update()

def reach(arm, sfx, target, pole):
    """Arm so beugen, dass das Handgelenk den Zielpunkt erreicht; der Ellbogen zeigt Richtung pole"""
    up, lo = "UpperArm" + sfx, "ForeArm" + sfx
    S = bone_head(arm, up); a, b = arm.data.bones[up].length, arm.data.bones[lo].length
    d = Vector(target) - S; dist = max(0.05, min(d.length, (a + b) * 0.995)); n = d.normalized()
    cos_a = max(-1.0, min(1.0, (a * a + dist * dist - b * b) / (2 * a * dist)))
    p = Vector(pole) - n * Vector(pole).dot(n); p.normalize()
    elbow = S + n * (a * cos_a) + p * (a * math.sqrt(max(0.0, 1 - cos_a * cos_a)))
    point_bone(arm, up, elbow - S)
    point_bone(arm, lo, Vector(target) - bone_head(arm, lo))

def orient(arm, name, y_dir, z_dir):
    """Knochen ausrichten: seine Länge zeigt nach y_dir, seine z-Achse möglichst nach z_dir (Hand: Finger, Handrücken)"""
    pb = arm.pose.bones[name]; cur = pb.matrix.copy()
    Y = Vector(y_dir).normalized(); Z = Vector(z_dir); Z = (Z - Y * Z.dot(Y)).normalized(); X = Y.cross(Z)
    M = Matrix((X, Y, Z)).transposed().to_4x4(); M.translation = cur.translation
    pb.matrix = M
    update()

HAND_FRAMES = {}                                # Ruhelage der Hände: Achsen (Daumenseite, Finger, Handrücken) je Seite

def turn_hand(arm, sfx, fingers, back):
    """Hand drehen: Finger zeigen nach fingers, der Handrücken nach back (Weltrichtungen)"""
    F0 = HAND_FRAMES[sfx]
    Y = Vector(fingers).normalized(); Z = Vector(back); Z = (Z - Y * Z.dot(Y)).normalized(); X = Y.cross(Z)
    F1 = Matrix((X, Y, Z)).transposed()
    pb = arm.pose.bones["Hand" + sfx]
    M = ((F1 @ F0.transposed()) @ arm.data.bones["Hand" + sfx].matrix_local.to_3x3()).to_4x4()
    M.translation = pb.matrix.translation
    pb.matrix = M
    update()
    return F1
