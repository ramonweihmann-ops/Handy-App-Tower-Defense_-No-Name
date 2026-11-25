# Kristallriese neu (Entwurf „Sternenschlund“ von ChatGPT, vom Nutzer freigegeben am 25.11.2026):
# Vorlage_Raw/Kristallriese_Neuentwurf_v1 (01_turnaround.png, 02_kopf_und_angriff.png, LIESMICH_CLAUDE.md).
# Gedrungener Riese aus dunkelvioletter Sternenhaut mit magentafarbenen Leuchtrissen, großer tief sitzender Kopf mit
# weit offenem Maul (Gaumen, Zunge mit Mittelfurche, Zahnfleisch, einzelne Zähne), Sternenplatten (Galaxien) an
# Schultern, Unterarmen und Rücken. Skelett und Animationen bleiben die des Koloss (Gehen, Laufen, beidarmiger Schlag);
# der Körper ist neu: aus Metaballs geformt, auf das vorhandene Skelett gewichtet (Bone Heat), Haut im Raum bemalt.
# Spielname bleibt „Kristallriese“ (Look kristall_riese, ersetzt den alten rosa Kristallgolem).
# Aufruf: blender -b -P tools/monster/kristallriese.py -- kristall_riese <ziel.glb>
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monster_aufsatz import *
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

import boss_aufsatz
boss_aufsatz.EXPORT_IMAGE_FORMAT = "JPEG"     # Bilder als JPEG ins GLB (Haut 2048 als PNG wäre über 2 MB groß)
STUFE = os.environ.get("STUFE", "voll")      # "form": nur Form in Grau (zum Prüfen der Proportionen)
MB_K = 0.575        # Oberfläche eines Metaball-Elements (Steifigkeit 2, Schwelle 0.6) liegt bei 0.575 × Radius × Größe

# ---------------------------------------------------------------- Formen aus Metaballs

def mb_family(name):
    """Eigene Metaball-Familie (Teile verschiedener Familien verschmelzen nicht miteinander)"""
    mb = bpy.data.metaballs.new(name); mb.resolution = 0.011; mb.render_resolution = 0.011; mb.threshold = 0.6
    o = bpy.data.objects.new(name, mb); bpy.context.scene.collection.objects.link(o)
    return o

def mb_ell(o, c, semi, rot=None):
    e = o.data.elements.new(type='ELLIPSOID')
    e.co = c; e.radius = 1.0; e.stiffness = 2.0
    e.size_x, e.size_y, e.size_z = (s / MB_K for s in semi)
    if rot is not None:
        e.rotation = rot
    return e

def mb_caps(o, p0, p1, r):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0
    e = o.data.elements.new(type='CAPSULE'); e.co = (p0 + p1) / 2; e.radius = r / MB_K; e.stiffness = 2.0
    e.size_x = d.length / 2
    e.rotation = Vector((1, 0, 0)).rotation_difference(d.normalized())
    return e

def along(p0, p1, semi_r, semi_l, t, off=(0, 0, 0)):
    """Ellipsoid entlang einer Strecke: Mitte bei t, lange Achse entlang der Strecke"""
    p0, p1 = Vector(p0), Vector(p1); d = (p1 - p0)
    c = p0.lerp(p1, t) + Vector(off)
    q = Vector((0, 0, 1)).rotation_difference(d.normalized())
    return c, (semi_r, semi_r, semi_l), q

def mb_to_mesh(o):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    m = bpy.data.objects.new(o.name + "_Netz", me); bpy.context.scene.collection.objects.link(m)
    bpy.data.objects.remove(o, do_unlink=True)
    return m

def apply_mod(o, mod):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier=mod.name)

def remesh(o, voxel):
    md = o.modifiers.new("Voxel", 'REMESH'); md.mode = 'VOXEL'; md.voxel_size = voxel; md.use_smooth_shade = True
    apply_mod(o, md)

def B(arm, name, t=0.0):
    return bone_pt(arm, "mixamorig:" + name, t)

def mirror(p):
    return Vector((-p[0], p[1], p[2]))

# Maul: Öffnung vorn im Gesicht (Mitte, halbe Breite, halbe Höhe oben/unten) und Tiefe; der Hohlraum wird mit einem
# Schneidekörper aus dem Kopf geschnitten, Zahnfleisch, Zähne und Zunge sitzen darin.
MOUTH_Z, MOUTH_A, MOUTH_BU, MOUTH_BL = 1.245, 0.19, 0.105, 0.145
MOUTH_FRONT, MOUTH_BACK = -0.52, -0.06
LIP_Y = -0.345

def mouth_section(y):
    """Querschnitt des Maulraums bei Tiefe y: (halbe Breite, halbe Höhe oben, unten, Mitte z) – vorn so groß wie die
    Öffnung, nach hinten zum Schlund hin enger"""
    t = np.clip((y - (-0.3)) / (MOUTH_BACK - (-0.3)), 0, 1)       # 0 an der Öffnung, 1 ganz hinten
    k = np.sqrt(np.clip(1 - t ** 2.2, 0, 1)) * 0.75 + 0.25 * (1 - t)
    return MOUTH_A * k, MOUTH_BU * (0.95 * k + 0.05), MOUTH_BL * k, MOUTH_Z + 0.02 * t

def mouth_inside(P, grow=1.0):
    """Wie weit ein Punkt im Maulraum liegt (<1 innen), für Bemalung des Rachens"""
    a, bu, bl, zc = mouth_section(P[..., 1])
    dz = P[..., 2] - zc
    b = np.where(dz > 0, bu, bl)
    e = 2.6
    return ((np.abs(P[..., 0]) / (a * grow + 1e-6)) ** e + (np.abs(dz) / (b * grow + 1e-6)) ** e) ** (1 / e)

def mouth_cutter():
    bm = bmesh.new(); S = 56
    ys = list(np.linspace(MOUTH_FRONT, MOUTH_BACK, 16))
    rings = []
    for y in ys:
        a, bu, bl, zc = mouth_section(np.float32(y))
        a, bu, bl, zc = float(a), float(bu), float(bl), float(zc)
        ring = []
        for k in range(S):
            th = k * 2 * math.pi / S
            c, s = math.cos(th), math.sin(th)
            e = 2.6
            x = a * np.sign(c) * abs(c) ** (2 / e); z = (bu if s > 0 else bl) * np.sign(s) * abs(s) ** (2 / e)
            ring.append(bm.verts.new((x, y, zc + z)))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(S):
            bm.faces.new([r0[k], r0[(k + 1) % S], r1[(k + 1) % S], r1[k]])
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
    return finish("Maulschnitt", bm)

def body_shape(arm):
    """Körper aus Metaballs: Rumpf mit Kopf (ohne Hals, Kopf tief und vorn), Arme und Beine je eigene Familie"""
    R = mb_family("Rumpf")
    mb_ell(R, (0, 0.05, 1.0), (0.34, 0.27, 0.3))                  # Brust
    mb_ell(R, (0, 0.0, 0.77), (0.3, 0.28, 0.24))                  # Bauch
    mb_ell(R, (0, 0.08, 0.57), (0.27, 0.22, 0.15))                # Becken
    mb_ell(R, (0, 0.17, 1.15), (0.34, 0.24, 0.16))                # Nacken und Rücken (kein Hals)
    mb_ell(R, (0, -0.04, 1.41), (0.32, 0.3, 0.28))                # Schädel (groß, tief sitzend)
    mb_ell(R, (0, -0.12, 1.15), (0.28, 0.22, 0.15))               # Unterkiefer und Kinn
    mb_ell(R, (0, -0.355, 1.44), (0.045, 0.04, 0.05))             # Nasenrücken
    for s in (1, -1):
        mb_ell(R, (0.16 * s, -0.16, 1.03), (0.16, 0.09, 0.12))      # Brustmuskeln
        mb_ell(R, (0.4 * s, 0.08, 1.15), (0.16, 0.17, 0.15))        # Schulteransatz
        mb_ell(R, (0.21 * s, -0.2, 1.3), (0.12, 0.12, 0.12))        # Wangen
        mb_caps(R, (0.035 * s, -0.333, 1.505), (0.2 * s, -0.28, 1.55), 0.036)   # Brauenwulst (schräg: böser Blick)
        mb_ell(R, (0.028 * s, -0.385, 1.4), (0.028, 0.025, 0.022))  # Nasenflügel
    # Lippenwulst rund um die Öffnung (wird beim Schneiden halbiert und rundet den Rand)
    pts = []
    for k in range(28):
        th = k * 2 * math.pi / 28
        c, s_ = math.cos(th), math.sin(th)
        x = (MOUTH_A + 0.02) * np.sign(c) * abs(c) ** (2 / 2.6)
        z = ((MOUTH_BU if s_ > 0 else MOUTH_BL) + 0.02) * np.sign(s_) * abs(s_) ** (2 / 2.6)
        pts.append(Vector((x, LIP_Y + 0.06 * (x / MOUTH_A) ** 2, MOUTH_Z + z)))
    for p0, p1 in zip(pts, pts[1:] + pts[:1]):
        mb_caps(R, p0, p1, 0.03)
    parts = [R]
    for side, s in (("Left", 1), ("Right", -1)):
        A_ = mb_family("Arm" + side)
        sh, el, wr = B(arm, side + "Arm"), B(arm, side + "ForeArm"), B(arm, side + "Hand")
        mb_ell(A_, (0.5 * s, 0.05, 1.15), (0.18, 0.18, 0.19))       # Deltamuskel
        mb_caps(A_, sh, el, 0.13)
        c, semi, q = along(sh, el, 0.135, 0.15, 0.5, (0, -0.035, 0)); mb_ell(A_, c, semi, q)   # Bizeps
        mb_caps(A_, el, wr, 0.115)
        c, semi, q = along(el, wr, 0.15, 0.17, 0.35); mb_ell(A_, c, semi, q)                   # schwerer Unterarm
        mb_ell(A_, tuple(wr), (0.1, 0.1, 0.1))
        parts.append(A_)
        L_ = mb_family("Bein" + side)
        up, kn, an = B(arm, side + "UpLeg"), B(arm, side + "Leg"), B(arm, side + "Foot")
        an = Vector((0.248 * s, 0.126, 0.166))                    # Fußgelenk (rechts im Skelett verdreht: gespiegelt)
        kn = Vector((0.23 * s, 0.051, 0.399))
        mb_ell(L_, (0.15 * s, 0.07, 0.47), (0.16, 0.17, 0.16))       # Oberschenkel
        mb_caps(L_, kn, an, 0.13)
        mb_ell(L_, (0.24 * s, 0.13, 0.3), (0.125, 0.12, 0.14))      # Wade
        mb_ell(L_, (0.27 * s, -0.01, 0.07), (0.15, 0.2, 0.075))     # Fuß
        for i, dx in enumerate((-0.09, -0.03, 0.03, 0.09)):
            mb_ell(L_, ((0.27 + dx) * s, -0.17 - 0.012 * (1.5 - abs(i - 1.5)), 0.05), (0.042, 0.055, 0.042))   # Zehen
        parts.append(L_)
    meshes = [mb_to_mesh(o) for o in parts]
    body = join_parts(meshes, "Kristallriese")
    remesh(body, 0.012)                                           # Teile zu einer Hülle vereinen
    cut = mouth_cutter()
    md = body.modifiers.new("Maul", 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = cut; md.solver = 'EXACT'
    apply_mod(body, md)
    bpy.data.objects.remove(cut, do_unlink=True)
    remesh(body, 0.012)
    md = body.modifiers.new("Glatt", 'SMOOTH'); md.factor = 0.5; md.iterations = 3
    apply_mod(body, md)
    md = body.modifiers.new("Weniger", 'DECIMATE'); md.ratio = 0.24
    apply_mod(body, md)
    for pl in body.data.polygons:
        pl.use_smooth = True
    return body

# ---------------------------------------------------------------- Hände (im Rahmen des Handknochens, wie hand_model)

def star_hand(name, side, skin, nail, k=1.3, fist=0.7):
    """Große Hand mit vier dicken Fingern und Daumen (außen), Finger zur lockeren Faust eingerollt, helle Nägel"""
    zs = 1.0 if side == "Left" else -1.0

    def P(x, y, z):
        return (x * k, y * k, z * k * zs)
    parts = [give(sphere(name + "Gelenk", P(0.0, 0.01, -0.005), 0.085 * k, (1.0, 1.0, 0.8)), skin),
             give(sphere(name + "Ballen", P(0.0, 0.085, -0.004), 0.105 * k, (1.0, 0.92, 0.66)), skin),
             give(sphere(name + "Ruecken", P(-0.004, 0.11, 0.024), 0.09 * k, (1.0, 0.9, 0.55)), skin)]
    xs = (-0.066, -0.022, 0.021, 0.062)
    curl = 1.0 + fist * 1.6
    for i, x in enumerate(xs):
        rr = 0.043 if i in (1, 2) else 0.039
        pts = [P(x, 0.13, 0.0), P(x * 1.04, 0.19 - fist * 0.02, -0.014 * curl), P(x * 1.06, 0.235 - fist * 0.05, -0.048 * curl),
               P(x * 1.06, 0.25 - fist * 0.085, -0.08 * curl)]
        parts.append(give(tube("%sFinger%d" % (name, i), pts, [rr * k, rr * 0.98 * k, rr * 0.92 * k, rr * 0.82 * k]), skin))
        parts.append(give(sphere("%sKuppe%d" % (name, i), pts[-1], rr * 0.82 * k), skin))
        parts.append(give(sphere("%sKnoechel%d" % (name, i), P(x, 0.15, 0.02), rr * 1.02 * k, (1.0, 1.0, 0.85)), skin))
        tip = Vector(pts[-1]); d = (tip - Vector(pts[-2])).normalized()
        parts.append(give(sphere("%sNagel%d" % (name, i), tuple(tip + d * rr * 0.45 * k + Vector(P(0, 0, 0.012))), rr * 0.72 * k,
                                 (1.0, 0.75, 0.75)), nail))
    pts = [P(0.07, 0.05, -0.02), P(0.105, 0.1, -0.05 - fist * 0.02), P(0.1 - fist * 0.03, 0.15 - fist * 0.02, -0.08 - fist * 0.03)]
    parts.append(give(tube(name + "Daumen", pts, [0.047 * k, 0.042 * k, 0.036 * k]), skin))
    parts.append(give(sphere(name + "DaumenKuppe", pts[-1], 0.036 * k), skin))
    tip = Vector(pts[-1]); d = (tip - Vector(pts[-2])).normalized()
    parts.append(give(sphere(name + "DaumenNagel", tuple(tip + d * 0.016 * k), 0.03 * k, (0.9, 0.8, 0.8)), nail))
    return join_parts(parts, name)

def group_all(o, name, w=1.0):
    g = o.vertex_groups.new(name=name)
    g.add([v.index for v in o.data.vertices], w, 'REPLACE')

def bake_transform(o):
    o.data.transform(o.matrix_world); o.matrix_world = Matrix()

# ---------------------------------------------------------------- Gewichte

MAIN_BONES = ["Hips", "Spine", "Spine1", "Spine2", "Neck", "Head"] + \
    ["%s%s" % (s, b) for s in ("Left", "Right") for b in ("Shoulder", "Arm", "ForeArm", "Hand", "UpLeg", "Leg", "Foot", "ToeBase")]

def bind(body, arm):
    """Bone Heat nur mit den Hauptknochen (Finger, Zehenenden, Hilfsknochen bekommen nichts)"""
    keep = {"mixamorig:" + b for b in MAIN_BONES}
    saved = {b.name: b.use_deform for b in arm.data.bones}
    for b in arm.data.bones:
        b.use_deform = b.name in keep
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    for b in arm.data.bones:
        b.use_deform = saved[b.name]
    # Kopf: Gesicht, Maul und Schädel ganz am Kopfknochen (Zähne, Augen hängen starr daran)
    hc = Vector((0, -0.08, 1.34)); hs = Vector((0.37, 0.37, 0.34))
    head = body.vertex_groups.get("mixamorig:Head") or body.vertex_groups.new(name="mixamorig:Head")
    for v in body.data.vertices:
        q = v.co - hc
        d = math.sqrt((q.x / hs.x) ** 2 + (q.y / hs.y) ** 2 + (q.z / hs.z) ** 2)
        h = smooth01((1.12 - d) / 0.3)
        if h <= 0:
            continue
        for g in v.groups:
            g.weight *= (1 - h)
        head.add([v.index], h, 'ADD')

def copy_nearest_weights(body, group_name):
    """Teile mit der Gruppe group_name bekommen die Gewichte der nächsten Hautstelle (Nägel, Platten)"""
    gi = body.vertex_groups[group_name].index
    is_part = [any(g.group == gi for g in v.groups) for v in body.data.vertices]
    kd = KDTree(sum(1 for p in is_part if not p))
    idx = []
    for v, p in zip(body.data.vertices, is_part):
        if not p:
            kd.insert(v.co, len(idx)); idx.append(v.index)
    kd.balance()
    names = {g.index: g.name for g in body.vertex_groups}
    src = {}
    for v, p in zip(body.data.vertices, is_part):
        if p:
            _, j, _ = kd.find(v.co)
            src[v.index] = [(names[g.group], g.weight) for g in body.data.vertices[idx[j]].groups if names[g.group].startswith("mixamorig:")]
    for vi, ws in src.items():
        for gname, w in ws:
            body.vertex_groups[gname].add([vi], w, 'REPLACE')
    body.vertex_groups.remove(body.vertex_groups[group_name])

# ---------------------------------------------------------------- Bilder und Hilfen zum Bemalen

def image_material(name, size, color=(0.3, 0.2, 0.45), rough=0.5, emission=None, strength=1.0):
    """Material mit eigenem Bild (Grundfarbe) – damit lässt sich ein Teil mit texels() im Raum bemalen"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value = rough
    arr = np.zeros((size, size, 4), np.float32); arr[..., :3] = color; arr[..., 3] = 1
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = new_image(name + "_Farbe", arr)
    nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
    if emission is not None:
        em = nt.nodes.new("ShaderNodeTexImage"); em.name = "LeuchtTextur"; em.image = new_image(name + "_Leuchten", emission)
        nt.links.new(em.outputs["Color"], p.inputs["Emission Color"])
        p.inputs["Emission Strength"].default_value = strength
    return m

def smart_uv(o, margin=0.003):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=margin)
    bpy.ops.object.mode_set(mode='OBJECT')

def vertex_ao(o, rays=14, dist=0.3):
    """Umgebungsverdeckung je Punkt (wie viel der Halbkugel über der Haut vom eigenen Körper verdeckt ist)"""
    me = o.data
    bvh = BVHTree.FromObject(o, bpy.context.evaluated_depsgraph_get())
    rnd = random.Random(11)
    dirs = []
    while len(dirs) < rays:
        d = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)))
        if 0.2 < d.length <= 1:
            dirs.append(d.normalized())
    ao = np.zeros(len(me.vertices), np.float32)
    for v in me.vertices:
        n = v.normal; p = v.co + n * 0.004; hit = 0.0; tot = 0.0
        for d in dirs:
            if d.dot(n) < 0:
                d = -d
            w = d.dot(n)
            h = bvh.ray_cast(p, d, dist)
            tot += w
            if h[0] is not None:
                hit += w * (1 - h[3] / dist) ** 0.5
        ao[v.index] = hit / max(tot, 1e-6)
    return ao

def texel_values(T, vals):
    """Werte je Punkt (z. B. Verdeckung) auf die Texel übertragen (Schwerpunkt der Dreiecke wie in texels)"""
    body = T["body"]; me = body.data
    h, w = T["P"].shape[:2]
    out = np.zeros((h, w), np.float32)
    uvl = me.uv_layers.active.data
    for tri in me.loop_triangles:
        U = np.array([(uvl[k].uv.x * w, uvl[k].uv.y * h) for k in tri.loops])
        x0, y0 = np.floor(U.min(0)).astype(int) - 1; x1, y1 = np.ceil(U.max(0)).astype(int) + 1
        x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, w - 1), min(y1, h - 1)
        if x1 < x0 or y1 < y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        Q = np.stack([gx.ravel(), gy.ravel()], 1)
        v0 = U[1] - U[0]; v1 = U[2] - U[0]; d00 = v0 @ v0; d01 = v0 @ v1; d11 = v1 @ v1
        den = d00 * d11 - d01 * d01
        if abs(den) < 1e-12:
            continue
        v2 = Q - U[0]; d20 = v2 @ v0; d21 = v2 @ v1
        b1 = (d11 * d20 - d01 * d21) / den; b2 = (d00 * d21 - d01 * d20) / den; b0 = 1 - b1 - b2
        eps = -1.0 / max(1.0, math.sqrt(max(d00, d11)))
        ins = (b0 >= eps) & (b1 >= eps) & (b2 >= eps)
        if not ins.any():
            continue
        bb = np.clip(np.stack([b0[ins], b1[ins], b2[ins]], 1), 0, None); bb /= bb.sum(1, keepdims=True)
        ix = (Q[ins] - 0.5).astype(int)
        out[ix[:, 1], ix[:, 0]] = bb @ vals[list(tri.vertices)]
    return out

def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)

# ---------------------------------------------------------------- Augen

EYES = [(0.122, 1.468), (-0.122, 1.468)]

def eye_image(n=256):
    y, x = np.mgrid[0:n, 0:n]
    u = (x + 0.5) / n * 2 - 1; v = (y + 0.5) / n * 2 - 1
    r = np.sqrt(u ** 2 + v ** 2)
    col = gradient((1.0, 0.96, 1.0), (1.0, 0.55, 0.97), smoothstep(0.15, 0.85, r))
    ri = np.sqrt((u * 1.1) ** 2 + (v + 0.32) ** 2)                       # Iris unten, halb vom Lid verdeckt
    iris = (1 - smoothstep(0.34, 0.46, ri)) * 0.75
    col = col * (1 - iris[..., None]) + gradient((0.62, 0.55, 1.0), (0.42, 0.3, 0.95), ri / 0.46) * iris[..., None]
    hot = 1 - smoothstep(0.0, 0.16, np.sqrt(u ** 2 + (v + 0.25) ** 2))
    col = col * (1 - hot[..., None]) + np.asarray((1.0, 1.0, 1.0), np.float32) * hot[..., None]
    edge = smoothstep(0.82, 1.0, r)
    col = col * (1 - edge[..., None]) + np.asarray((0.7, 0.15, 0.7), np.float32) * edge[..., None]
    arr = np.ones((n, n, 4), np.float32); arr[..., :3] = col
    return arr

def star_eyes(body, arm):
    bvh = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())
    img = eye_image()
    m = bpy.data.materials.new("Sternenauge"); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = new_image("Sternenauge_Bild", img)
    nt.links.new(tex.outputs["Color"], p.inputs["Base Color"]); nt.links.new(tex.outputs["Color"], p.inputs["Emission Color"])
    p.inputs["Emission Strength"].default_value = 2.2; p.inputs["Roughness"].default_value = 0.15
    out = []
    for x, z in EYES:
        hit, n, _, _ = bvh.ray_cast(Vector((x, -1.0, z)), Vector((0, 1, 0)), 2.0)
        s = 1 if x > 0 else -1
        f = (n * 0.45 + Vector((0, -1, 0)) * 0.55).normalized()                 # Blickrichtung
        lng = Vector((s * math.cos(math.radians(17)), 0, math.sin(math.radians(17))))   # Augenachse, außen höher
        lng = (lng - f * lng.dot(f)).normalized(); up = f.cross(lng) * s
        if up.z < 0:
            up = -up
        a, b, d = 0.072, 0.033, 0.03
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=1.0)
        uv = bm.loops.layers.uv.new("UVMap")
        for v in bm.verts:
            lx, ly, lz = v.co.x, v.co.y, v.co.z
            v.co = hit + f * (-0.012) + lng * (lx * a) + up * (lz * b) + (-f) * (-ly * d)
        for fc in bm.faces:
            for lp in fc.loops:
                q = lp.vert.co - (hit + f * (-0.012))
                lp[uv].uv = (0.5 + 0.5 * q.dot(lng) / a, 0.5 + 0.5 * q.dot(up) / b)
        o = finish("Auge" + ("L" if s > 0 else "R"), bm)
        give(o, m)
        attach(o, arm, "mixamorig:Head")
        out.append(o)
    return out

# ---------------------------------------------------------------- Maul: Zahnfleisch, Zähne, Zunge

def lip_edge(x, top):
    """z der Maulöffnung bei x (Superellipse wie der Schneidekörper)"""
    e = 2.6
    q = max(0.0, 1 - abs(x / MOUTH_A) ** e) ** (1 / e)
    return MOUTH_Z + (MOUTH_BU if top else -MOUTH_BL) * q

def arch_pt(u, top, inset=0.0):
    """Zahnbogen: u -1…1 von Mundwinkel zu Mundwinkel, hinter der Lippe, an den Seiten nach hinten gebogen"""
    x = 0.9 * MOUTH_A * u
    y = LIP_Y + 0.045 + 0.05 * u * u + 0.05 * u ** 4 + inset
    z = lip_edge(x, top) + (-0.012 if top else 0.012) * (1 - 0.5 * u * u)
    return Vector((x, y, z))

def tooth(name, base, down, along_dir, L, w, t, kind, mats, curve=0.0):
    """Einzelner Zahn als Querschnittsfolge: kind "schneide" (flach, abgerundete Kante), "fang" (gebogene Spitze),
    "backen" (breit, kurz, Höcker). Wurzel steckt im Zahnfleisch (s < 0), Zahnhals gelblicher."""
    down = down.normalized(); sd = (along_dir - down * along_dir.dot(down)).normalized(); fd = sd.cross(down)
    if fd.y > 0:
        fd = -fd                                                    # nach vorn (aus dem Maul hinaus)
    S = 18; ss = [-0.3, -0.1, 0.05, 0.2, 0.38, 0.55, 0.7, 0.82, 0.9, 0.95, 0.985]
    bm = bmesh.new(); rings = []
    for s_ in ss:
        if kind == "fang":
            m = (1 - max(s_, 0)) ** 0.85 * (1.0 if s_ > 0.05 else 0.95)
            wx, wy, e = w * m, t * m, 2.0
        elif kind == "schneide":
            m = 0.8 + 0.2 * math.sin(math.pi * min(max(s_, 0), 1) * 0.8)
            tip = math.sqrt(max(0.0, 1 - ((max(s_, 0.78) - 0.78) / 0.22) ** 2))
            wx, wy, e = w * m * (0.35 + 0.65 * tip), t * (1 - 0.55 * max(s_, 0)) * tip, 2.6
        else:
            tip = math.sqrt(max(0.0, 1 - ((max(s_, 0.7) - 0.7) / 0.3) ** 2))
            wx, wy, e = w * (0.35 + 0.65 * tip), t * (0.35 + 0.65 * tip), 3.2
        c = base + down * (L * s_) + fd * (curve * L * max(s_, 0) ** 2)
        ring = []
        for k in range(S):
            th = k * 2 * math.pi / S
            cx, cy = math.cos(th), math.sin(th)
            px = wx * math.copysign(abs(cx) ** (2 / e), cx); py = wy * math.copysign(abs(cy) ** (2 / e), cy)
            ring.append(bm.verts.new(c + sd * px + fd * py))
        rings.append(ring)
    for i, (r0, r1) in enumerate(zip(rings, rings[1:])):
        for k in range(S):
            f = bm.faces.new([r0[k], r0[(k + 1) % S], r1[(k + 1) % S], r1[k]])
            f.material_index = 1 if ss[i] < 0.1 else 0
    tip = bm.verts.new(base + down * L + fd * (curve * L))
    for k in range(S):
        bm.faces.new([rings[-1][k], rings[-1][(k + 1) % S], tip])
    bm.faces.new(list(reversed(rings[0])))
    o = finish(name, bm)
    give(o, *mats)
    if kind == "backen":                                            # Höcker auf der Kaufläche
        cusps = []
        for i, (a_, b_) in enumerate(((-0.45, -0.4), (0.45, -0.4), (-0.45, 0.4), (0.45, 0.4))):
            cusps.append(give(sphere(name + "Hoecker%d" % i, tuple(base + down * (L * 0.93) + sd * (a_ * w) + fd * (b_ * t)), w * 0.26,
                                     (1.0, 1.0, 0.7)), mats[0]))
        o = join_parts([o] + cusps, name)
    return o

def tongue(arm):
    m = image_material("Zunge", 512, (0.8, 0.42, 0.58), rough=0.32)
    bm = bmesh.new(); bm.loops.layers.uv.new("UVMap")
    bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=20, radius=1.0, calc_uvs=True)
    c = Vector((0, -0.135, 1.15)); a, b, h = 0.13, 0.15, 0.055
    for v in bm.verts:
        x, y, z = v.co.x * a, v.co.y * b, v.co.z * h
        if z > 0:
            z -= 0.02 * math.exp(-(x / 0.028) ** 2) * (0.4 + 0.6 * max(0.0, -v.co.y + 0.3))    # Mittelfurche
            z += 0.018 * max(0.0, -v.co.y) ** 2                                            # Spitze vorn leicht erhoben
        v.co = c + Vector((x, y, z))
    o = finish("Zunge", bm)
    o.data.uv_layers[0].name = "UVMap"
    give(o, m)
    T = texels(o); P = T["P"]
    groove = np.exp(-(P[..., 0] / 0.014) ** 2) * (P[..., 2] > 1.16)
    pap = np.clip((noise3(P, 260, 5) - 0.55) / 0.2, 0, 1)
    back = smoothstep(-0.25, -0.06, P[..., 1])
    col = gradient((0.86, 0.45, 0.62), (0.45, 0.14, 0.28), back * 0.8 + groove * 0.5)
    col = col * (0.95 + 0.08 * pap[..., None])
    T["out"][..., :3] = np.where(T["cov"][..., None], col, T["out"][..., :3])
    commit(T, pad=False)
    attach(o, arm, "mixamorig:Head")
    return o

def star_mouth(arm, rnd):
    enamel = look("Zahnschmelz", (0.95, 0.91, 0.8), rough=0.22)
    neck = look("Zahnhals", (0.86, 0.78, 0.6), rough=0.3)
    gum = look("Zahnfleisch", (0.86, 0.45, 0.56), rough=0.35)
    parts = []
    for top in (True, False):
        pts = [arch_pt(-1.02 + 2.04 * k / 24, top) for k in range(25)]
        parts.append(give(tube("Zahnfleisch" + ("Oben" if top else "Unten"), [tuple(p_) for p_ in pts],
                               [0.012] + [0.026 if top else 0.02] * 23 + [0.012], segs=12), gum))
        if top:
            layout = [(0.09, "schneide", 0.058, 0.031), (0.27, "schneide", 0.055, 0.03), (0.45, "schneide", 0.05, 0.029),
                      (0.62, "fang", 0.12, 0.036), (0.77, "backen", 0.042, 0.034), (0.89, "backen", 0.034, 0.034), (0.98, "backen", 0.024, 0.03)]
        else:
            layout = [(0.08, "schneide", 0.052, 0.03), (0.24, "schneide", 0.052, 0.03), (0.4, "schneide", 0.048, 0.029),
                      (0.55, "fang", 0.088, 0.032), (0.7, "backen", 0.04, 0.033), (0.83, "backen", 0.034, 0.033), (0.94, "backen", 0.026, 0.03)]
        for i, (uu, kind, L, w) in enumerate(layout):
            for s in (1, -1):
                u = uu * s
                base = arch_pt(u, top) + Vector((0, 0, -0.012 if top else 0.012))
                tang = (arch_pt(u + 0.01, top) - arch_pt(u - 0.01, top)).normalized()
                down = Vector((0, 0.08 * abs(u), -1 if top else 1)) + Vector((-0.12 * u, 0, 0))
                Lr = L * rnd.uniform(0.94, 1.04)
                curve = 0.1 if kind == "fang" else 0.03
                t_ = w * (0.62 if kind == "schneide" else (0.9 if kind == "fang" else 1.05))
                parts.append(tooth("Zahn%s%d%s" % ("O" if top else "U", i, "L" if s > 0 else "R"), base, down, tang, Lr, w * 0.5, t_ * 0.5,
                                   kind, (enamel, neck), curve=-curve))
                parts.append(give(sphere("Zahnfleischbogen%s%d%d" % ("O" if top else "U", i, s), tuple(base - down.normalized() * 0.004),
                                         1.0, (w * 0.48, w * 0.42, 0.016), segs=(14, 8)), gum))
    out = []
    for o in parts:
        attach(o, arm, "mixamorig:Head")
        out.append(o)
    out.append(tongue(arm))
    return out

# ---------------------------------------------------------------- Sternenhaut

def paint_skin(body, arm):
    ao = vertex_ao(body)
    T = texels(body)
    P, N, cov = T["P"], T["N"], T["cov"]
    AO = texel_values(T, ao)
    # Grundton: dunkles Violett mit sanften Schwankungen, in Mulden zum Indigo
    v1 = fbm3(P, 3.0, 21, 4); v2 = fbm3(P, 11.0, 23, 3)
    col = gradient((0.19, 0.11, 0.38), (0.31, 0.19, 0.52), v1 * 1.3 - 0.15)
    col = col * (0.93 + 0.14 * v2[..., None])
    occ = np.clip(AO * 1.6, 0, 1)
    col = col * (1 - 0.55 * occ[..., None]) + np.asarray((0.08, 0.05, 0.2), np.float32) * (0.55 * occ[..., None])
    em = np.zeros(P.shape, np.float32)
    # Maulraum: hinten dunkel, vorn rosig-violett; Gaumen mit Querfalten; Lippen etwas dunkler
    mi = mouth_inside(P)
    inside = (mi < 1.04) & (P[..., 1] > LIP_Y - 0.02)
    depth = smoothstep(LIP_Y + 0.02, MOUTH_BACK - 0.02, P[..., 1])
    mouth_col = gradient((0.6, 0.27, 0.45), (0.1, 0.03, 0.08), depth ** 0.7)
    palate = (P[..., 2] > MOUTH_Z + 0.02) * (0.5 + 0.5 * np.sin(P[..., 1] * 140 + np.abs(P[..., 0]) * 40))
    mouth_col = mouth_col * (0.85 + 0.25 * palate[..., None] * (1 - depth[..., None]))
    lip = np.clip(1 - np.abs(mi - 1.1) / 0.12, 0, 1) * (P[..., 1] < LIP_Y + 0.06) * (~inside)
    col = col * (1 - 0.35 * lip[..., None])
    # Sternenstaub: feine Punkte, einzelne hellere Sterne
    dust = np.clip((noise3(P, 260, 31) - 0.9) / 0.05, 0, 1) * np.clip((noise3(P, 25, 32) - 0.35) / 0.3, 0, 1)
    big = np.clip((noise3(P, 70, 33) - 0.955) / 0.025, 0, 1)
    star = np.maximum(dust * 0.55, big * 0.9)
    col = col * (1 - star[..., None]) + np.asarray((0.75, 0.8, 1.0), np.float32) * star[..., None]
    em += star[..., None] * np.asarray((0.4, 0.45, 0.9), np.float32) * 0.7
    # Leuchtrisse: verzweigte Linien (Zellgrenzen im Raum, verwirbelt, nur stellenweise), nicht im Gesicht
    W = P + 0.05 * np.stack([fbm3(P, 5.0, 41, 3), fbm3(P, 5.0, 42, 3), fbm3(P, 5.0, 43, 3)], -1)
    edge, cid = worley3(W, 5.5, 44)
    keep = smoothstep(0.53, 0.6, fbm3(P, 2.3, 45, 3)) * smoothstep(0.42, 0.5, noise3(P, 9.0, 47))
    face = np.zeros(P.shape[:2], np.float32)
    for x, z in EYES:
        face = np.maximum(face, 1 - smoothstep(0.07, 0.1, np.linalg.norm(P - np.asarray((x, -0.3, z), np.float32), axis=-1)))
    face = np.maximum(face, (mi < 1.3) * 1.0)
    hands = ((np.abs(P[..., 0]) > 0.84) & (P[..., 2] < 0.8)) | (P[..., 2] < 0.12)            # keine Risse auf Händen und Zehen
    keep = keep * (1 - face) * (1 - hands)
    core = np.clip(1 - edge / 0.0026, 0, 1) * keep
    halo = np.clip(1 - edge / 0.013, 0, 1) ** 2 * keep
    node = np.clip((noise3(P, 18, 46) - 0.78) / 0.08, 0, 1) * np.clip(1 - edge / 0.02, 0, 1) ** 3 * keep
    glow_c = np.asarray((1.0, 0.3, 0.92), np.float32)
    col = col * (1 - halo[..., None] * 0.35) + glow_c * (halo[..., None] * 0.35)
    col = col * (1 - core[..., None]) + np.asarray((1.0, 0.75, 1.0), np.float32) * core[..., None]
    em += glow_c * (np.maximum(core, halo * 0.45) + node * 0.8)[..., None]
    # Augen: weicher magentafarbener Schein auf der Haut darum
    for x, z in EYES:
        d = np.linalg.norm((P - np.asarray((x, -0.31, z), np.float32)) * np.asarray((1, 1.5, 1.4), np.float32), axis=-1)
        g = np.clip(1 - d / 0.085, 0, 1) ** 2 * (P[..., 1] < -0.2)
        em += glow_c * g[..., None] * 0.35
    # Nasenlöcher
    for s in (1, -1):
        d = np.linalg.norm((P - np.asarray((0.03 * s, -0.395, 1.385), np.float32)) * np.asarray((1.0, 1.3, 1.8), np.float32), axis=-1)
        col = col * (1 - 0.8 * np.clip(1 - d / 0.016, 0, 1)[..., None])
    col = np.where(inside[..., None], mouth_col, col)
    em = np.where(inside[..., None], 0, em)
    T["out"][..., :3] = np.where(cov[..., None], np.clip(col, 0, 1), T["out"][..., :3])
    T["em"][..., :3] = np.where(cov[..., None], np.clip(em, 0, 1), 0)
    commit(T, strength=1.6)

# ---------------------------------------------------------------- Sternenplatten (Galaxien)

def galaxy_image(seed, spiral=True, n=1024, center=(0.0, 0.0), turn=0.0):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:n, 0:n]
    u = (x + 0.5) / n * 2 - 1; v = (y + 0.5) / n * 2 - 1
    r = np.sqrt(u ** 2 + v ** 2)
    P = np.stack([u * 1.6, v * 1.6, np.full_like(u, seed * 0.37)], -1).astype(np.float32)
    neb = fbm3(P, 1.7, seed, 5); neb2 = fbm3(P, 2.6, seed + 5, 4)
    col = np.zeros((n, n, 3), np.float32) + np.asarray((0.03, 0.02, 0.09), np.float32)
    col += np.clip(neb - 0.42, 0, 1)[..., None] * np.asarray((0.75, 0.2, 0.95), np.float32) * 1.6
    col += np.clip(neb2 - 0.52, 0, 1)[..., None] * np.asarray((0.2, 0.35, 1.0), np.float32) * 1.8
    if spiral:
        gu, gv = u - center[0], v - center[1]
        rr = np.sqrt(gu ** 2 + gv ** 2) / 0.62; th = np.arctan2(gv, gu) + turn
        phase = 2 * th - 3.4 * np.log(rr + 0.06)
        arms = (0.5 + 0.5 * np.cos(phase)) ** 2.5 * np.exp(-rr * 2.0) * (0.6 + 0.4 * fbm3(P, 6.0, seed + 9, 3))
        core = np.exp(-(rr / 0.12) ** 2)
        col += arms[..., None] * np.asarray((0.95, 0.5, 1.0), np.float32) * 1.4
        col += core[..., None] * np.asarray((1.0, 0.85, 1.0), np.float32) * 1.3
    img = np.zeros((n, n), np.float32); tint = np.zeros((n, n, 3), np.float32)
    for k in range(int(1400 * n / 1024)):
        cx, cy = rng.uniform(0, n, 2); b = rng.uniform(0.25, 1.0) ** 2.2; sg = rng.uniform(0.7, 1.5) if k > 40 else rng.uniform(1.8, 3.0)
        rad = int(sg * 4) + 1
        x0, x1 = int(max(cx - rad, 0)), int(min(cx + rad + 1, n)); y0, y1 = int(max(cy - rad, 0)), int(min(cy + rad + 1, n))
        if x1 <= x0 or y1 <= y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1) + 0.5 - cx, np.arange(y0, y1) + 0.5 - cy)
        g = np.exp(-(gx ** 2 + gy ** 2) / (2 * sg * sg)) * (b if k > 40 else 1.0)
        if k <= 40:                                                  # helle Sterne mit Strahlenkreuz
            g = g + 0.5 * np.exp(-np.abs(gx) / 0.8 - (gy / (sg * 2.5)) ** 2) + 0.5 * np.exp(-np.abs(gy) / 0.8 - (gx / (sg * 2.5)) ** 2)
        c = rng.choice([(1.0, 1.0, 1.0), (0.75, 0.85, 1.0), (1.0, 0.75, 1.0)])
        img[y0:y1, x0:x1] += g
        tint[y0:y1, x0:x1] += g[..., None] * np.asarray(c, np.float32)
    col += tint
    vign = smoothstep(0.82, 0.99, r)
    col = col * (1 - 0.85 * vign[..., None]) + np.asarray((0.05, 0.03, 0.12), np.float32) * vign[..., None]
    arr = np.ones((n, n, 4), np.float32); arr[..., :3] = np.clip(col, 0, 1)
    return arr

def outline_pts(kind, n=48):
    pts = []
    for k in range(n):
        th = k * 2 * math.pi / n
        c, s = math.cos(th), math.sin(th)
        if kind == "oval":
            e = 2.3
            pts.append((math.copysign(abs(c) ** (2 / e), c), math.copysign(abs(s) ** (2 / e), s)))
        elif kind == "tropfen":                                      # zum Handgelenk hin schmaler
            e = 2.2
            x = math.copysign(abs(c) ** (2 / e), c); y = math.copysign(abs(s) ** (2 / e), s)
            pts.append((x * (0.75 + 0.25 * (y + 1) / 2) ** 1.2, y))
        else:                                                        # Schild: oben breit, unten spitz
            e = 2.6
            x = math.copysign(abs(c) ** (2 / e), c); y = math.copysign(abs(s) ** (2 / e), s)
            if y < 0:
                x *= (1 + y) ** 0.9 * 0.85 + 0.15 * (1 + y)
                y *= 1.15
            else:
                y = y * 0.75 - 0.08 * x * x
            pts.append((x, y))
    return pts

def star_plate(name, bvh, origin, n, up, hw, hh, kind, gal_m, rim_m, uv_rot=0.0, uv_scale=0.95, dome=0.03):
    """Platte aus Sternenlicht, eingewachsen: gewölbte Oberfläche mit Galaxie, rundum eine glatte dunkle Fassung
    (wulstiger Rand), darunter eine Schürze in die Haut – nichts steht ab"""
    n = Vector(n).normalized(); up = Vector(up); up = (up - n * up.dot(n)).normalized(); rt = up.cross(n)
    outline = outline_pts(kind); R = 9; M = len(outline)
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")

    def place(x, y, lift):
        p0 = Vector(origin) + rt * (x * hw) + up * (y * hh) + n * 0.6
        hit = bvh.ray_cast(p0, -n, 2.0)
        return hit[0] + hit[1] * lift, hit[1]
    cv = bm.verts.new(place(0, 0, 0.008 + dome)[0])
    # (Maßstab des Umrisses, Abstand zur Haut, Material 0 Galaxie / 1 Fassung)
    prof = [(k / R, 0.008 + dome * (1 - (k / R) ** 2) ** 0.7, 0) for k in range(1, R + 1)] + \
           [(1.045, 0.017, 1), (1.09, 0.016, 1), (1.13, 0.006, 1), (1.15, -0.02, 1)]
    rings = []
    for sc_, lift, _ in prof:
        rings.append([bm.verts.new(place(x * sc_, y * sc_, lift)[0]) for (x, y) in outline])
    ca, sa = math.cos(uv_rot), math.sin(uv_rot)

    def uvc(x, y, sc_):
        X, Y = x * min(sc_, 1.0) * uv_scale, y * min(sc_, 1.0) * uv_scale
        return (0.5 + 0.5 * (X * ca - Y * sa), 0.5 + 0.5 * (X * sa + Y * ca))
    for j in range(M):
        f = bm.faces.new([cv, rings[0][j], rings[0][(j + 1) % M]])
        for lp, (x, y, sc_) in zip(f.loops, [(0, 0, 0), (*outline[j], prof[0][0]), (*outline[(j + 1) % M], prof[0][0])]):
            lp[uvl].uv = uvc(x, y, sc_)
    for k in range(len(prof) - 1):
        mi = prof[k + 1][2]
        for j in range(M):
            f = bm.faces.new([rings[k][j], rings[k + 1][j], rings[k + 1][(j + 1) % M], rings[k][(j + 1) % M]])
            f.material_index = mi
            for lp, (x, y, sc_) in zip(f.loops, [(*outline[j], prof[k][0]), (*outline[j], prof[k + 1][0]),
                                                 (*outline[(j + 1) % M], prof[k + 1][0]), (*outline[(j + 1) % M], prof[k][0])]):
                lp[uvl].uv = uvc(x, y, sc_) if mi == 0 else (0.02, 0.02)
    o = finish(name, bm)
    o.data.uv_layers[0].name = "UVMap"
    give(o, gal_m, rim_m)
    return o

def star_plates(body, arm):
    bvh = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())
    mats = []
    for i, g in enumerate((galaxy_image(3, True, 512, center=(0.08, -0.05)), galaxy_image(8, True, 512, center=(-0.1, 0.12), turn=1.3),
                           galaxy_image(13, False, 512))):
        m = bpy.data.materials.new("Galaxie%d" % (i + 1)); m.use_nodes = True
        nt = m.node_tree; pr = nt.nodes["Principled BSDF"]
        tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = new_image("Galaxie%d_Bild" % (i + 1), g)
        nt.links.new(tex.outputs["Color"], pr.inputs["Base Color"]); nt.links.new(tex.outputs["Color"], pr.inputs["Emission Color"])
        pr.inputs["Emission Strength"].default_value = 1.2; pr.inputs["Roughness"].default_value = 0.12
        mats.append(m)
    rim_m = look("Plattenfassung", (0.17, 0.11, 0.32), rough=0.3)
    plates = []
    for side, s in (("Left", 1), ("Right", -1)):
        sh, el, wr = B(arm, side + "Arm"), B(arm, side + "ForeArm"), B(arm, side + "Hand")
        arm_up = (sh - el).normalized()
        plates.append(star_plate("PlatteSchulter" + side, bvh, Vector((0.5 * s, 0.05, 1.14)), (0.92 * s, -0.18, 0.35), arm_up,
                                 0.15, 0.19, "oval", mats[0 if s > 0 else 1], rim_m, uv_rot=0.4 * s))
        fore = (wr - el).normalized()
        c = el.lerp(wr, 0.34)
        out = Vector((s, 0.15, 0.25)).normalized(); out = (out - fore * out.dot(fore)).normalized()
        plates.append(star_plate("PlatteArm" + side, bvh, c, out, -fore, 0.085, 0.12, "tropfen", mats[2], rim_m, uv_rot=1.0 * s, uv_scale=0.8))
    plates.append(star_plate("PlatteRuecken", bvh, Vector((0, 0.2, 1.12)), (0, 1, 0.18), (0, 0, 1), 0.29, 0.3, "schild", mats[1], rim_m,
                             uv_rot=0.2, dome=0.035))
    return plates

# ---------------------------------------------------------------- Variante

@variante("kristall_riese", "koloss")
def kristallriese(arm, body):
    remove_body(body)
    fix_elbows(arm)
    pose_hands(arm)
    skin = look("Sternenhaut", (0.32, 0.22, 0.5), rough=0.5)
    nail = look("Naegel", (0.8, 0.74, 0.82), rough=0.35)
    body = body_shape(arm)
    bind(body, arm)
    extra = []
    for side in ("Left", "Right"):
        h = star_hand("Hand" + side, side, skin, nail)
        h.matrix_world = arm.matrix_world @ arm.data.bones["mixamorig:%sHand" % side].matrix_local @ h.matrix_world
        bake_transform(h); group_all(h, "mixamorig:%sHand" % side)
        extra.append(h)
        s = 1 if side == "Left" else -1
        for i, dx in enumerate((-0.09, -0.03, 0.03, 0.09)):
            y = -0.17 - 0.012 * (1.5 - abs(i - 1.5))
            n_ = give(sphere("Zehennagel%s%d" % (side, i), ((0.27 + dx) * s, y - 0.038, 0.062), 0.034, (0.95, 0.8, 0.6)), nail)
            group_all(n_, "insel_naechst"); extra.append(n_)
    if body.data.materials:
        body.data.materials.clear()
    body.data.materials.append(skin); body.data.materials.append(nail)
    for o in extra:
        for pl in o.data.polygons:
            pl.material_index = 1 if o.data.materials and o.data.materials[pl.material_index] == nail else 0
        o.data.materials.clear(); o.data.materials.append(skin); o.data.materials.append(nail)
    bpy.ops.object.select_all(action='DESELECT')
    for o in extra:
        o.select_set(True)
    body.select_set(True); bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    copy_nearest_weights(body, "insel_naechst")
    print("KÖRPER", len(body.data.vertices), "Punkte", len(body.data.polygons), "Flächen")
    if STUFE == "form":
        return
    # Haut bemalen (eigene Abwicklung, Bild 2048), dann Platten, Augen und Maul
    smart_uv(body)
    skin_img = image_material("Sternenhaut", 2048, rough=0.5)
    body.data.materials[0] = skin_img
    paint_skin(body, arm)
    plates = star_plates(body, arm)
    for o in plates:
        group_all(o, "insel_naechst")
    bpy.ops.object.select_all(action='DESELECT')
    for o in plates:
        o.select_set(True)
    body.select_set(True); bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    copy_nearest_weights(body, "insel_naechst")
    star_eyes(body, arm)
    star_mouth(arm, random.Random(5))
    print("FERTIG GEBAUT", len(body.data.polygons), "Flächen Körper")

if __name__ == "__main__":
    run(VAR, OUT)
