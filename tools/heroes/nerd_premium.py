# Nerd (Wunsch 28.11.2026): bezahlter Held in der Detailtiefe des neuen Fünkchen, nachgebaut nach
# Vorlage_Raw/Nerd_Biker_Premium_v1 (nerd_variante_B_comicaugen.png: einfache dunkelviolette Augen wie bei den
# bisherigen Helden; LIESMICH_CLAUDE.md). Aufruf: blender -b -P tools/heroes/nerd_premium.py -- nerd <ziel.glb>
# Hoodie und Hose sind eine durchgehende Haut (nichts kann durch die Kleidung stoßen); Kopf mit Haaren, Brille und
# Gesicht ist starr; Rucksack, Kopfhörer, Taschen, Schuhe und Laptop sind eigene glatte Teile.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from premium_figur import *

HC = Vector((0.0, 0.0, 1.62))                   # Kopfmitte
J = dict(hips=(0, 0, 0.66), spine=(0, 0, 0.82), chest=(0, 0, 1.02), neck=(0, 0.01, 1.3), head=(0, 0.01, 1.42), top=(0, 0.01, 1.95),
         clav=(0.07, 0, 1.25), shoulder=(0.26, 0, 1.235), elbow=(0.405, 0, 0.995), wrist=(0.525, 0, 0.79), palm=(0.585, 0, 0.685),
         hip=(0.125, 0, 0.64), knee=(0.15, -0.01, 0.385), ankle=(0.16, 0, 0.15), toe=(0.17, -0.24, 0.04))
HAND_K = 1.12
V = lambda p: Vector(p)
mir = lambda p: Vector((-p[0], p[1], p[2]))

T_SKIN, T_CLOTH, T_HAIR, T_SHOE, T_PACK, T_PHONE, T_GLASS, T_BROW, T_TEAL, T_STRAP, T_POCKET, T_LACE, T_TAB, T_MOUTH, T_CUSH = range(13 + 2)
G_BODY, G_HEAD, G_HANDL, G_HANDR, G_LAPTOP, G_PHONE, G_PACK = range(7)

# ---------------------------------------------------------------- Körper im Hoodie, Hose

def body_shape():
    parts = [("e", (0, 0, 1.1), (0.245, 0.185, 0.2)), ("e", (0, -0.005, 0.9), (0.24, 0.19, 0.17)),       # Brust, Bauch
             ("e", (0, 0, 0.775), (0.25, 0.2, 0.055)),                                                   # Saum des Hoodies
             ("e", (0, 0, 0.665), (0.215, 0.17, 0.12)),                                                  # Becken
             ("e", (0, 0.17, 1.25), (0.2, 0.105, 0.14))]                                                 # Kapuze im Nacken
    for k in range(12):                                                                                  # Kragenwulst der Kapuze
        a = k * 2 * math.pi / 12
        parts.append(("e", (0.165 * math.sin(a), 0.025 - 0.15 * math.cos(a), 1.325 - 0.035 * math.cos(a)), (0.078, 0.078, 0.07)))
    for s in (1, -1):
        sh, el, wr = [V((p[0] * s, p[1], p[2])) for p in (J["shoulder"], J["elbow"], J["wrist"])]
        d = (wr - el).normalized()
        parts += [("e", sh + V((0, 0, -0.01)), (0.115, 0.115, 0.115)), ("c", sh, el, 0.098), ("c", el, wr - d * 0.05, 0.092),
                  ("e", wr - d * 0.045, (0.09, 0.09, 0.09))]                                             # Ärmel mit Bündchen
        hp, kn, an = [V((p[0] * s, p[1], p[2])) for p in (J["hip"], J["knee"], J["ankle"])]
        parts += [("c", hp + V((0, 0, -0.02)), kn, 0.12), ("c", kn, an + V((0, 0, 0.06)), 0.11),
                  ("e", an + V((0, 0, 0.045)), (0.128, 0.13, 0.07))]                                     # weite Hose, unten gerafft
    return blob("Koerper", parts, voxel=0.013, smooth=7)

def head_shape():
    parts = [("e", HC, (0.29, 0.275, 0.28)), ("e", HC + V((0, -0.02, -0.12)), (0.245, 0.235, 0.17)),     # Schädel, Kinnpartie
             ("e", HC + V((0, -0.285, -0.07)), (0.036, 0.04, 0.034)),                                    # Nase
             ("c", (0, 0.01, 1.27), (0, 0.01, 1.45), 0.088)]                                             # Hals
    for s in (1, -1):
        parts.append(("e", HC + V((0.285 * s, 0.02, -0.04)), (0.05, 0.05, 0.078)))                      # Ohren
    return blob("Kopf", parts, voxel=0.011, smooth=6)

def hair_shape():
    """Frisur aus wenigen großen runden Strähnen: Tolle nach links oben, Büschel an den Seiten und am Hinterkopf"""
    E = Euler
    lobes = [((0, 0.03, 0.1), (0.305, 0.3, 0.24), None),                                                 # Kappe über dem Schädel
             ((0, 0.12, -0.02), (0.29, 0.22, 0.26), None),                                               # Hinterkopf
             ((-0.1, -0.2, 0.2), (0.17, 0.12, 0.1), E((0.3, 0.2, -0.3))),                                # Ansatz der Tolle rechts
             ((0.04, -0.23, 0.27), (0.2, 0.12, 0.1), E((0.35, -0.2, 0.15))),                             # Tolle, schwingt nach links
             ((0.2, -0.2, 0.31), (0.14, 0.1, 0.085), E((0.3, -0.75, 0.35))),                             # Spitze der Tolle
             ((0.27, -0.16, 0.36), (0.07, 0.07, 0.06), None),
             ((-0.2, -0.13, 0.18), (0.13, 0.12, 0.1), E((0.1, 0.5, -0.2))),                              # Büschel vorn rechts
             ((-0.28, 0.0, 0.1), (0.09, 0.14, 0.13), E((0, 0.25, 0))),                                   # über dem rechten Ohr
             ((0.28, 0.02, 0.1), (0.09, 0.15, 0.14), E((0, -0.25, 0))),                                  # über dem linken Ohr
             ((-0.17, 0.08, 0.3), (0.13, 0.13, 0.1), E((0, 0.5, 0))),                                    # Wirbel oben rechts
             ((0.1, 0.12, 0.33), (0.15, 0.14, 0.1), E((-0.2, -0.3, 0))),                                 # oben hinten
             ((-0.22, 0.2, 0.16), (0.1, 0.1, 0.1), None), ((0.22, 0.22, 0.14), (0.1, 0.1, 0.11), None),  # Büschel hinten
             ((0, 0.27, 0.12), (0.14, 0.09, 0.13), None), ((0, 0.24, -0.12), (0.2, 0.1, 0.12), None),    # Nacken
             ((-0.3, 0.06, -0.06), (0.05, 0.1, 0.1), None), ((0.3, 0.08, -0.06), (0.05, 0.1, 0.1), None)]   # Koteletten
    parts = [("e", HC + V(c), semi, (r.to_quaternion() if r is not None else None)) for c, semi, r in lobes]
    return blob("Haare", parts, voxel=0.012, smooth=5)

def shoe(s):
    x = J["ankle"][0]
    parts = [("e", (x, -0.085, 0.095), (0.118, 0.2, 0.092)), ("e", (x, -0.205, 0.085), (0.112, 0.115, 0.085)),      # Schuh, Kappe
             ("e", (x, 0.065, 0.105), (0.105, 0.095, 0.105)), ("e", (x, 0.005, 0.19), (0.1, 0.105, 0.06)),         # Ferse, Schaft
             ("e", (x, -0.08, 0.03), (0.128, 0.225, 0.04))]                                                       # kräftige Sohle
    g = blob("Schuh", parts, voxel=0.011, smooth=5)
    g.data.transform(Matrix.Translation((x, 0, 0)) @ Matrix.Rotation(math.radians(-8), 4, 'Z') @ Matrix.Translation((-x, 0, 0)))
    laces = [rounded_box("Band", (x, -0.115 + 0.062 * i, 0.172 + 0.016 * i), (0.07, 0.019, 0.012), 0.008,
                         Euler((math.radians(-14), 0, 0))) for i in range(3)]
    for o in laces:
        o.data.transform(Matrix.Translation((x, 0, 0)) @ Matrix.Rotation(math.radians(-8), 4, 'Z') @ Matrix.Translation((-x, 0, 0)))
    out = [g] + laces
    if s < 0:
        out = [mirror_x(o) for o in out]
    return out[0], out[1:]

# ---------------------------------------------------------------- Zubehör

def glasses(bvh):
    """kräftiger, eckig-runder Rahmen ohne Gläser, Steg und Bügel bis zu den Ohren"""
    parts = []
    for s in (1, -1):
        pts = []
        for k in range(28):
            a = k * 2 * math.pi / 28
            u = 0.098 * abs(math.cos(a)) ** 0.5 * (1 if math.cos(a) >= 0 else -1); w = 0.078 * abs(math.sin(a)) ** 0.5 * (1 if math.sin(a) >= 0 else -1)
            x = (0.122 + u) * s; z = HC.z - 0.015 + w
            hit = bvh.ray_cast(V((x, -2.0, z)), V((0, 1, 0)), 6.0)[0]
            pts.append(V((x, min(hit.y if hit is not None else -0.2, -0.2) - 0.034, z)))
        ys = sum(q.y for q in pts) / len(pts)
        pts = [V((q.x, 0.6 * ys + 0.4 * q.y, q.z)) for q in pts]                                         # fast ebener Rahmen
        parts.append(loop_tube("Rahmen%d" % s, [tuple(q) for q in pts], 0.017, segs=8))
        a = V((0.222 * s, ys + 0.004, HC.z + 0.02)); b = V((0.292 * s, 0.0, HC.z + 0.03))
        parts.append(sweep("Buegel%d" % s, [a, a.lerp(b, 0.5) + V((0.012 * s, 0, 0)), b], [0.014, 0.013, 0.012], segs=6))
    parts.append(sweep("Steg", [V((-0.03, ys - 0.004, HC.z + 0.012)), V((0, ys - 0.012, HC.z + 0.02)), V((0.03, ys - 0.004, HC.z + 0.012))], [0.014] * 3, segs=6))
    return parts

def face_parts(bvh, eye_m):
    """Augen (Variante B: schmale dunkelviolette Ovale mit Glanzpunkt), kräftige Brauen, Lächeln"""
    eyes, brows, mouth = [], [], []
    def on(x, z, lift):
        hit, n, _, _ = bvh.ray_cast(V((x, -2.0, z)), V((0, 1, 0)), 6.0)
        return hit + n * lift
    for s in (1, -1):
        cx, cz, a, b = 0.118 * s, HC.z - 0.02, 0.036, 0.062
        bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap"); uv = {}
        c = bm.verts.new(on(cx, cz, 0.006)); uv[c] = (0.5, 0.5); rings = []; n = 20
        for t in (0.4, 0.75, 1.0):
            ring = []
            for k in range(n):
                ph = k * 2 * math.pi / n
                v = bm.verts.new(on(cx + a * t * math.cos(ph), cz + b * t * math.sin(ph), 0.006 - 0.003 * t))
                uv[v] = (0.5 + 0.5 * t * math.cos(ph) * s, 0.5 + 0.5 * t * math.sin(ph)); ring.append(v)
            rings.append(ring)
        for k in range(n):
            bm.faces.new([c, rings[0][k], rings[0][(k + 1) % n]] if s > 0 else [c, rings[0][(k + 1) % n], rings[0][k]])
        for r0, r1 in zip(rings, rings[1:]):
            for k in range(n):
                q = [r0[k], r1[k], r1[(k + 1) % n], r0[(k + 1) % n]]
                bm.faces.new(q if s > 0 else q[::-1])
        for f in bm.faces:
            for l in f.loops:
                l[uvl].uv = uv[l.vert]
        eyes.append(give(finish("Auge%d" % s, bm), eye_m))
        pts = [on((0.045 + 0.155 * t) * s, HC.z + 0.105 + 0.05 * math.sin(t * 2.2) - 0.022 * (1 - t), 0.012) for t in np.linspace(0, 1, 6)]
        brows.append(sweep("Braue%d" % s, pts, [0.016, 0.022, 0.023, 0.021, 0.017, 0.011], segs=8, flat=0.55))
    pts = [on(x, HC.z - 0.165 - 0.018 * math.cos(x / 0.075 * math.pi / 2) + 0.01 * (x > 0) * (x / 0.075), 0.003) for x in np.linspace(-0.07, 0.085, 8)]
    mouth.append(sweep("Mund", pts, [0.004, 0.007, 0.008, 0.008, 0.008, 0.008, 0.007, 0.004], segs=6))
    return eyes, brows, mouth

def eye_material_b():
    """Auge wie bei den bisherigen Helden: dunkelviolettes Oval, oben eine Spur heller, kleiner Glanzpunkt"""
    n = 64
    ax = np.linspace(-1, 1, n, dtype=np.float32); x, y = np.meshgrid(ax, ax)
    col = np.zeros((n, n, 3), np.float32) + f3((0.157, 0.125, 0.267))
    col = mix(col, (0.3, 0.25, 0.5), 0.5 * smoothstep(-0.2, 1.0, y))
    col = mix(col, (0.07, 0.05, 0.14), 0.6 * smoothstep(0.2, -1.0, y))
    col = mix(col, (1.0, 1.0, 1.0), smoothstep(0.34, 0.2, np.hypot((x + 0.25) / 1.5, y - 0.45)))
    arr = np.ones((n, n, 4), np.float32); arr[..., :3] = col
    m = bpy.data.materials.new("Auge"); m.use_nodes = True
    nt = m.node_tree; pr = nt.nodes["Principled BSDF"]; pr.inputs["Roughness"].default_value = 0.2
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = new_image("Auge_Farbe", arr)
    nt.links.new(tex.outputs["Color"], pr.inputs["Base Color"])
    return m

def headphones():
    """Kopfhörer um den Hals: zwei runde Muscheln vorn seitlich, Bügel hinten herum"""
    shells, cush, teal = [], [], []
    for s in (1, -1):
        c = V((0.175 * s, -0.125, 1.275)); ax = V((0.72 * s, -0.66, 0.2)).normalized()
        o = sphere("Muschel%d" % s, (0, 0, 0), 1.0, segs=(18, 10))
        e1 = ax.cross(V((0, 0, 1))).normalized(); e2 = ax.cross(e1)
        for v in o.data.vertices:
            q = v.co.copy(); r = math.hypot(q.x, q.y); k = 1.0 if r < 1e-6 else min(1.0, (0.55 + 0.45 * abs(q.z) ** 0.3 * 0 + 0.45) )
            v.co = c + e1 * (q.x * 0.1) + e2 * (q.y * 0.1) + ax * (q.z * 0.05)
        shells.append(o)
        cush.append(torus("Polster%d" % s, c - ax * 0.03, ax, 0.076, 0.028, n=18, m=8))
        teal.append(torus("Leuchtring%d" % s, c + ax * 0.036, ax, 0.055, 0.012, n=18, m=6))
    pts = [V((0.215 * math.sin(a), 0.03 + 0.215 * math.cos(a) * 0.95, 1.275 + 0.03 * math.cos(a))) for a in np.linspace(-1.9, 1.9, 13)]
    shells.append(sweep("Buegel", pts, [0.03] * 13, segs=8, flat=0.6, flat_axis=(0, 0, 1)))
    return shells, cush, teal

def backpack(bvh):
    """kompakter Rucksack mit Vortasche, Seitentasche, Griff und zwei breiten anliegenden Gurten"""
    main = [rounded_box("Rucksack", (0, 0.315, 1.0), (0.215, 0.125, 0.27), 0.085), rounded_box("Vortasche", (0, 0.44, 0.9), (0.15, 0.04, 0.13), 0.035),
            rounded_box("Seitentasche", (-0.235, 0.33, 0.9), (0.04, 0.085, 0.115), 0.03), rounded_box("SeitentascheL", (0.235, 0.33, 0.9), (0.04, 0.085, 0.115), 0.03),
            torus("Griff", (0, 0.3, 1.275), (0, 1, 0), 0.05, 0.016, n=12, m=6, squash=0.7)]
    teal = [rounded_box("Clip", (-0.283, 0.33, 0.93), (0.012, 0.03, 0.05), 0.01), rounded_box("ClipL", (0.283, 0.33, 0.93), (0.012, 0.03, 0.05), 0.01)]
    straps = []
    for s in (1, -1):
        pts = []
        for ang in np.linspace(math.radians(118), math.radians(-62), 12):                # über die Schulter: hinten oben -> vorn unten
            d = V((0, -math.cos(ang) * -1, math.sin(ang)))
            o = V((0.15 * s, 0.0, 1.12)) + V((0, math.cos(ang), math.sin(ang))) * 0.9
            hit = bvh.ray_cast(o, (V((0.15 * s, 0, 1.12)) - o).normalized(), 2.0)[0]
            pts.append(hit + (hit - V((0.15 * s, 0, 1.12))).normalized() * 0.012)
        pts.append(V((0.17 * s, 0.2, 0.86)))
        straps.append(sweep("Gurt%d" % s, pts, [0.036] * len(pts), segs=8, flat=0.38, flat_axis=(1, 0, 0)))
    return main, teal, straps

def cargo(s):
    hp, kn = V(J["hip"]), V(J["knee"])
    ax = (kn - hp).normalized(); c = hp.lerp(kn, 0.55) + V((0.125, -0.005, 0))
    rot = V((0, 0, -1)).rotation_difference(ax).to_euler()
    out = [rounded_box("Tasche", c, (0.035, 0.085, 0.085), 0.025, rot), rounded_box("Klappe", c + V((0.008, 0, 0.062)), (0.036, 0.092, 0.036), 0.02, rot)]
    return [mirror_x(o) for o in out] if s < 0 else out

def laptop(mat):
    """Laptop im eigenen Maß: Basis liegt in der Ebene z = 0, Scharnier bei y = -Tiefe/2, Deckel steht aufgeklappt"""
    W, D, Tk = 0.2, 0.14, 0.011
    base = rounded_box("Basis", (0, 0, Tk), (W, D, Tk), 0.008)
    lid = rounded_box("Deckel", (0, 0, 0), (W, D, Tk * 0.85), 0.008)
    lid.data.transform(Matrix.Translation((0, -D, 2 * Tk)) @ Matrix.Rotation(math.radians(-108), 4, 'X') @ Matrix.Translation((0, -D, 0)))
    hinge = sweep("Scharnier", [V((-W * 0.7, -D, 2 * Tk)), V((0, -D, 2 * Tk)), V((W * 0.7, -D, 2 * Tk))], [0.011] * 3, segs=8)
    return [give(o, mat) for o in (base, lid, hinge)]

# ---------------------------------------------------------------- Ablauf

FLAT = {T_SKIN: (0.95, 0.72, 0.55), T_CLOTH: (0.76, 0.7, 0.93), T_HAIR: (0.56, 0.33, 0.2), T_SHOE: (0.36, 0.25, 0.6), T_PACK: (0.3, 0.2, 0.52),
        T_PHONE: (0.74, 0.68, 0.9), T_GLASS: (0.2, 0.14, 0.38), T_BROW: (0.3, 0.17, 0.1), T_TEAL: (0.2, 0.84, 0.84), T_STRAP: (0.26, 0.18, 0.46),
        T_POCKET: (0.3, 0.2, 0.52), T_LACE: (0.92, 0.9, 1.0), T_TAB: (0.82, 0.77, 0.96), T_MOUTH: (0.5, 0.2, 0.2), T_CUSH: (0.25, 0.17, 0.44)}

def build(out):
    body = to_tris(body_shape(), 6500); head = to_tris(head_shape(), 2600); hair = to_tris(hair_shape(), 2600)
    dg = bpy.context.evaluated_depsgraph_get()
    bvh_b = BVHTree.FromObject(body, dg); bvh_h = BVHTree.FromObject(head, dg)
    arm = biped(J, extra=[("Laptop", J["palm"], (J["palm"][0], J["palm"][1] - 0.2, J["palm"][2]), "Hand.L")])
    mark(body, T_CLOTH, G_BODY)
    auto_bind(body, arm, {"Hips", "Spine", "Chest", "Neck"} | {b + s for b in ("Shoulder", "UpperArm", "ForeArm", "UpLeg", "Leg", "Foot") for s in (".L", ".R")})
    parts = [body, mark(head, T_SKIN, G_HEAD, "Head"), mark(hair, T_HAIR, G_HEAD, "Head")]
    # Hände: rechts zeigt der Zeigefinger (tippt), links stützt die offene Hand den Laptop
    for s, sfx, curls, th in ((-1, ".R", (0.12, 0.85, 0.9, 0.92), 0.7), (1, ".L", (0.42, 0.45, 0.48, 0.5), 0.15)):
        h = to_tris(hand_mesh("Hand" + sfx, HAND_K, curls, thumb=th), 1100)
        wr, el = V((J["wrist"][0] * s, 0, J["wrist"][2])), V((J["elbow"][0] * s, 0, J["elbow"][2]))
        Y = (wr - el).normalized()
        if s > 0:
            mirror_x(h); X = V((0, -1, 0))
        else:
            X = V((0, 1, 0))
        Z = X.cross(Y).normalized(); X = Y.cross(Z)
        place(h, wr - Y * 0.01, X, Y, Z)
        HAND_FRAMES[sfx] = Matrix((X, Y, Z)).transposed()
        parts.append(mark(h, T_SKIN, G_HANDL if s > 0 else G_HANDR, "Hand" + sfx))
    for s, sfx in ((1, ".L"), (-1, ".R")):
        sh, laces = shoe(s)
        parts.append(mark(to_tris(sh, 900), T_SHOE, G_BODY, "Foot" + sfx)); parts += [mark(o, T_LACE, G_BODY, "Foot" + sfx) for o in laces]
        parts += [mark(o, T_POCKET, G_BODY, "UpLeg" + sfx) for o in cargo(s)]
    parts += [mark(o, T_GLASS, G_HEAD, "Head") for o in glasses(bvh_h)]
    eye_m = eye_material_b()
    eyes, brows, mouth = face_parts(bvh_h, eye_m)
    parts += [mark(o, T_BROW, G_HEAD, "Head") for o in brows] + [mark(o, T_MOUTH, G_HEAD, "Head") for o in mouth]
    shells, cush, teal = headphones()
    parts += [mark(o, T_PHONE, G_PHONE, "Chest") for o in shells] + [mark(o, T_CUSH, G_PHONE, "Chest") for o in cush] + [mark(o, T_TEAL, G_PHONE, "Chest") for o in teal]
    main, teal, straps = backpack(bvh_b)
    parts += [mark(o, T_PACK, G_PACK, "Chest") for o in main] + [mark(o, T_TEAL, G_PACK, "Chest") for o in teal] + [mark(o, T_STRAP, G_PACK, "Chest") for o in straps]
    mats = {t: look("F%d" % t, c, rough=0.55) for t, c in FLAT.items()}
    for o in parts:
        give(o, mats[int(round(o.data.attributes["teil"].data[0].value))])
    g = join_parts(parts, "Nerd")
    for p in g.data.polygons:
        p.use_smooth = True
    lap_m = look("Laptop", (0.5, 0.47, 0.6), rough=0.4)
    lap = join_parts(laptop(lap_m), "LaptopTeil")
    g = join_parts([g] + [mark(o, 20, G_HEAD, "Head") for o in eyes], "Nerd")
    bpy.context.scene.render.fps = FPS
    g.parent = arm; md = g.modifiers.new("Armature", 'ARMATURE'); md.object = arm
    reset_pose(arm)
    co = np.array([tuple(v.co) for v in g.data.vertices])
    print("MASSE x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (co[:, 0].min(), co[:, 0].max(), co[:, 1].min(), co[:, 1].max(), co[:, 2].min(), co[:, 2].max()))
    print("DREIECKE", sum(len(p.vertices) - 2 for p in g.data.polygons))
    bpy.data.objects.remove(lap, do_unlink=True)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS',
                              export_yup=True, export_apply=False, export_force_sampling=True)

if __name__ == "__main__":
    bpy.ops.wm.read_factory_settings(use_empty=True)
    build(OUT)
    print("FERTIG", OUT)
