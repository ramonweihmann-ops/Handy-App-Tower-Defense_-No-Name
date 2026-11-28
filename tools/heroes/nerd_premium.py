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
         clav=(0.07, 0, 1.25), shoulder=(0.26, 0, 1.235), elbow=(0.415, 0, 0.975), wrist=(0.555, 0, 0.745), palm=(0.615, 0, 0.64),
         hip=(0.125, 0, 0.64), knee=(0.15, -0.01, 0.385), ankle=(0.16, 0, 0.15), toe=(0.17, -0.24, 0.04))
HAND_K = 1.12
V = lambda p: Vector(p)
mir = lambda p: Vector((-p[0], p[1], p[2]))

T_SKIN, T_CLOTH, T_HAIR, T_SHOE, T_PACK, T_PHONE, T_GLASS, T_BROW, T_TEAL, T_STRAP, T_POCKET, T_LACE, T_TAB, T_MOUTH, T_CUSH = range(13 + 2)
G_BODY, G_HEAD, G_HANDL, G_HANDR, G_LAPTOP, G_PHONE, G_PACK = range(7)

# ---------------------------------------------------------------- Körper im Hoodie, Hose

def body_shape():
    parts = [("e", (0, 0, 1.1), (0.27, 0.2, 0.2)), ("e", (0, -0.01, 0.9), (0.275, 0.215, 0.17)),         # Brust, Bauch
             ("e", (0, -0.005, 0.775), (0.285, 0.225, 0.06)),                                            # Saum des Hoodies
             ("e", (0, 0, 0.665), (0.235, 0.185, 0.12)),                                                 # Becken
             ("e", (0, 0.17, 1.25), (0.2, 0.105, 0.14))]                                                 # Kapuze im Nacken
    for k in range(12):                                                                                  # Kragenwulst der Kapuze
        a = k * 2 * math.pi / 12
        parts.append(("e", (0.165 * math.sin(a), 0.025 - 0.15 * math.cos(a), 1.325 - 0.035 * math.cos(a)), (0.078, 0.078, 0.07)))
    for s in (1, -1):
        sh, el, wr = [V((p[0] * s, p[1], p[2])) for p in (J["shoulder"], J["elbow"], J["wrist"])]
        d = (wr - el).normalized()
        parts += [("e", sh + V((0, 0, -0.01)), (0.115, 0.115, 0.115)), ("c", sh, el, 0.098), ("c", el, wr - d * 0.05, 0.092),
                  ("e", wr - d * 0.05, (0.084, 0.084, 0.084))]                                           # Ärmel mit Bündchen
        hp, kn, an = [V((p[0] * s, p[1], p[2])) for p in (J["hip"], J["knee"], J["ankle"])]
        parts += [("c", hp + V((0, 0, -0.02)), kn, 0.132), ("c", kn, an + V((0, 0, 0.1)), 0.125),
                  ("e", an + V((0, 0, 0.1)), (0.145, 0.15, 0.075))]                                     # weite Hose, unten gerafft
    return blob("Koerper", parts, voxel=0.013, smooth=7)

def head_shape():
    parts = [("e", HC, (0.29, 0.275, 0.28)), ("e", HC + V((0, -0.02, -0.12)), (0.245, 0.235, 0.17)),     # Schädel, Kinnpartie
             ("e", HC + V((0, -0.285, -0.07)), (0.036, 0.04, 0.034)),                                    # Nase
             ("c", (0, 0.01, 1.27), (0, 0.01, 1.45), 0.088)]                                             # Hals
    for s in (1, -1):
        parts.append(("e", HC + V((0.285 * s, 0.02, -0.04)), (0.05, 0.05, 0.078)))                      # Ohren
    return blob("Kopf", parts, voxel=0.011, smooth=6)

def hair_shape():
    """Frisur aus wenigen großen runden Strähnen: eine Kappe über dem Schädel, darauf die Tolle, die nach links oben
    schwingt, Büschel an den Schläfen und wilde Spitzen am Hinterkopf. Liefert die Teile (nicht verschmolzen: zwischen
    den Strähnen bleiben klare Furchen)."""
    cap = blob("Haarkappe", [("e", HC + V((0, 0.04, 0.08)), (0.312, 0.305, 0.265)), ("e", HC + V((0, 0.14, -0.04)), (0.295, 0.215, 0.27))], voxel=0.014, smooth=4)
    L = [  # Ansatz, Stützpunkt, Spitze (ab Kopfmitte), Dicke
        ((-0.2, -0.2, 0.2), (0.0, -0.36, 0.36), (0.3, -0.2, 0.33), 0.125),      # große Tolle: von rechts vorn nach links oben
        ((-0.24, -0.1, 0.24), (-0.02, -0.2, 0.46), (0.27, -0.06, 0.4), 0.12),   # zweite Welle darüber
        ((-0.16, 0.04, 0.28), (0.02, 0.0, 0.5), (0.24, 0.1, 0.42), 0.115),      # Scheitel
        ((-0.14, -0.24, 0.17), (-0.3, -0.26, 0.2), (-0.34, -0.14, 0.02), 0.085),  # Büschel an der rechten Schläfe
        ((-0.24, -0.1, 0.16), (-0.37, -0.05, 0.14), (-0.36, 0.03, -0.06), 0.09),
        ((0.2, -0.2, 0.2), (0.33, -0.18, 0.2), (0.35, -0.08, 0.0), 0.085),      # linke Schläfe
        ((0.25, -0.06, 0.2), (0.38, 0.0, 0.2), (0.37, 0.08, -0.04), 0.09),
        ((-0.2, 0.12, 0.24), (-0.36, 0.2, 0.3), (-0.4, 0.26, 0.14), 0.095),     # wilde Spitzen hinten rechts
        ((0.2, 0.14, 0.24), (0.34, 0.24, 0.32), (0.4, 0.3, 0.16), 0.095),       # hinten links
        ((0.0, 0.16, 0.27), (0.02, 0.36, 0.36), (0.04, 0.42, 0.2), 0.105),      # Wirbel am Hinterkopf
        ((-0.2, 0.22, 0.08), (-0.3, 0.33, 0.02), (-0.27, 0.34, -0.14), 0.09),   # Nacken
        ((0.2, 0.22, 0.08), (0.3, 0.33, 0.02), (0.27, 0.34, -0.14), 0.09),
        ((0.0, 0.27, 0.06), (0.0, 0.38, -0.02), (0.0, 0.35, -0.2), 0.1),
        ((-0.07, -0.25, 0.22), (-0.12, -0.33, 0.2), (-0.17, -0.3, 0.1), 0.06)]  # kleine Strähne in der Stirn
    L += [((0.1, -0.16, 0.27), (0.26, -0.2, 0.36), (0.36, -0.1, 0.24), 0.1),      # füllt die Tolle links auf
          ((-0.05, 0.1, 0.3), (-0.2, 0.16, 0.42), (-0.32, 0.12, 0.3), 0.1),       # oben rechts
          ((0.1, 0.2, 0.22), (0.2, 0.34, 0.24), (0.22, 0.38, 0.06), 0.095), ((-0.1, 0.2, 0.22), (-0.2, 0.34, 0.24), (-0.22, 0.38, 0.06), 0.095)]
    locks = [lock("Straehne%d" % i, HC + V(a_), HC + V(b_), HC + V(c_), r * 1.22, flat=1.0) for i, (a_, b_, c_, r) in enumerate(L)]
    return [cap] + locks

def shoe(s):
    x = J["ankle"][0]
    parts = [("e", (x, -0.1, 0.11), (0.138, 0.235, 0.108)), ("e", (x, -0.245, 0.1), (0.132, 0.135, 0.098)),         # Schuh, Kappe
             ("e", (x, 0.07, 0.125), (0.125, 0.11, 0.125)), ("e", (x, 0.0, 0.225), (0.118, 0.125, 0.07)),          # Ferse, Schaft
             ("e", (x, -0.095, 0.035), (0.15, 0.265, 0.046))]                                                     # kräftige Sohle
    g = blob("Schuh", parts, voxel=0.011, smooth=5, ground=True)
    g.data.transform(Matrix.Translation((x, 0, 0)) @ Matrix.Rotation(math.radians(-8), 4, 'Z') @ Matrix.Translation((-x, 0, 0)))
    laces = [rounded_box("Band", (x, -0.15 + 0.072 * i, 0.2 + 0.02 * i), (0.085, 0.023, 0.014), 0.009,
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
            u = 0.092 * abs(math.cos(a)) ** 0.5 * (1 if math.cos(a) >= 0 else -1); w = 0.072 * abs(math.sin(a)) ** 0.5 * (1 if math.sin(a) >= 0 else -1)
            x = (0.118 + u) * s; z = HC.z - 0.012 + w
            hit = bvh.ray_cast(V((x, -2.0, z)), V((0, 1, 0)), 6.0)[0]
            pts.append(V((x, min(hit.y if hit is not None else -0.2, -0.2) - 0.034, z)))
        ys = sum(q.y for q in pts) / len(pts)
        pts = [V((q.x, 0.6 * ys + 0.4 * q.y, q.z)) for q in pts]                                         # fast ebener Rahmen
        parts.append(loop_tube("Rahmen%d" % s, [tuple(q) for q in pts], 0.021, segs=8))
        a = V((0.212 * s, ys + 0.004, HC.z + 0.02)); b = V((0.292 * s, 0.0, HC.z + 0.03))
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
        c = V((0.2 * s, -0.135, 1.285)); ax = V((0.78 * s, -0.6, 0.18)).normalized()
        e1 = ax.cross(V((0, 0, 1))).normalized(); e2 = ax.cross(e1)
        o = sphere("Muschel%d" % s, (0, 0, 0), 1.0, segs=(18, 10))
        for v in o.data.vertices:
            q = v.co.copy()
            v.co = c + e1 * (q.x * 0.112) + e2 * (q.y * 0.112) + ax * (q.z * 0.05 * (1.0 if q.z > 0 else 0.6))
        shells.append(o)
        cush.append(torus("Polster%d" % s, c - ax * 0.028, ax, 0.08, 0.034, n=18, m=8))
        teal.append(torus("Leuchtring%d" % s, c + ax * 0.03, ax, 0.066, 0.014, n=18, m=6))
    pts = [V((0.235 * math.sin(a_), 0.02 + 0.235 * math.cos(a_), 1.285 + 0.03 * math.cos(a_))) for a_ in np.linspace(-2.05, 2.05, 15)]
    shells.append(sweep("Buegel", pts, [0.034] * 15, segs=8, flat=0.6, flat_axis=(0, 0, 1)))
    return shells, cush, teal

def backpack(bvh):
    """kompakter Rucksack mit Vortasche, Seitentaschen, Griff und zwei breiten anliegenden Gurten"""
    main = [rounded_box("Rucksack", (0, 0.37, 1.0), (0.245, 0.15, 0.3), 0.1), rounded_box("Vortasche", (0, 0.515, 0.89), (0.17, 0.045, 0.15), 0.04),
            rounded_box("Seitentasche", (-0.265, 0.38, 0.89), (0.045, 0.095, 0.125), 0.035), rounded_box("SeitentascheL", (0.265, 0.38, 0.89), (0.045, 0.095, 0.125), 0.035),
            torus("Griff", (0, 0.35, 1.305), (0, 1, 0), 0.055, 0.018, n=12, m=6, squash=0.7)]
    teal = [rounded_box("Clip", (-0.318, 0.38, 0.93), (0.014, 0.034, 0.055), 0.011), rounded_box("ClipL", (0.318, 0.38, 0.93), (0.014, 0.034, 0.055), 0.011)]
    straps = []
    for s in (1, -1):
        mid = V((0.15 * s, 0.03, 1.1)); pts, nrm = [], []
        for ang in np.linspace(math.radians(158), math.radians(-48), 18):                # über die Schulter: hinten -> oben -> vorn
            d = V((0.12 * s * max(0.0, -math.cos(ang)), -math.cos(ang), math.sin(ang))).normalized()   # vorn leicht nach außen zur Achsel
            hit = bvh.ray_cast(mid + d * 0.9, -d, 2.0)[0]
            pts.append(hit + d * 0.008); nrm.append(d)
        straps.append(ribbon("Gurt%d" % s, pts, nrm, 0.04, 0.014))
    return main, teal, straps

def cargo(s):
    hp, kn = V(J["hip"]), V(J["knee"])
    ax = (kn - hp).normalized(); c = hp.lerp(kn, 0.55) + V((0.125, -0.005, 0))
    rot = V((0, 0, -1)).rotation_difference(ax).to_euler()
    out = [rounded_box("Tasche", c, (0.035, 0.085, 0.085), 0.025, rot), rounded_box("Klappe", c + V((0.008, 0, 0.062)), (0.036, 0.092, 0.036), 0.02, rot)]
    return [mirror_x(o) for o in out] if s < 0 else out

LAP_W, LAP_D = 0.2, 0.14

def laptop():
    """Laptop im eigenen Maß: Basis liegt auf z = 0, Scharnier hinten bei y = -Tiefe, der Deckel steht aufgeklappt.
    Eigene kleine Textur: außen das türkise Energiezeichen, innen der Bildschirm, auf der Basis Tasten und Bedienfläche."""
    W, D, Tk = LAP_W, LAP_D, LAP_TK
    base = tag(rounded_box("Basis", (0, 0, Tk), (W, D, Tk), 0.008), 0)
    lid = tag(rounded_box("Deckel", (0, 0, 0), (W, D, Tk * 0.85), 0.008), 1)
    open_m = Matrix.Translation((0, -D, 2 * Tk)) @ Matrix.Rotation(math.radians(108), 4, 'X') @ Matrix.Translation((0, D, 0))
    lid.data.transform(open_m)
    hinge = tag(sweep("Scharnier", [V((-W * 0.7, -D, 2 * Tk)), V((0, -D, 2 * Tk)), V((W * 0.7, -D, 2 * Tk))], [0.011] * 3, segs=8), 2)
    g = join_parts([base, lid, hinge], "LaptopTeil")
    g.data.materials.clear(); g.data.materials.append(image_material("Laptop", 512, color=(0.5, 0.47, 0.62), rough=0.35))
    smart_uv(g, margin=0.01)
    T = texels(g); P, N, cov = T["P"], T["N"], T["cov"]
    TG = np.rint(texel_values(T, part_tags(g))).astype(int)
    inv = np.array(open_m.inverted(), np.float32)
    Q = P @ inv[:3, :3].T + inv[:3, 3]; NQ = N @ inv[:3, :3].T                    # Deckel zurück in die flache Lage
    col = gradient((0.4, 0.37, 0.54), (0.62, 0.6, 0.76), np.clip(N[..., 2] * 0.5 + 0.5, 0, 1)); em = np.zeros(P.shape, np.float32)
    teal = f3((0.2, 0.9, 0.88))
    # Deckel außen: Sechseck mit Blitz
    lidm = (TG == 1)
    lc = gradient((0.5, 0.47, 0.64), (0.64, 0.62, 0.78), smoothstep(-D, D, Q[..., 1]))
    hexd = np.maximum(np.abs(Q[..., 0]), np.abs(Q[..., 0]) * 0.5 + np.abs(Q[..., 1]) * 0.866)
    sign = smoothstep(0.012, 0.006, np.abs(hexd - 0.062))
    bolt = np.full(P.shape[:-1], 9.0, np.float32)
    for (x0, y0), (x1, y1) in (((0.014, 0.04), (-0.016, -0.004)), ((-0.016, -0.004), (0.014, 0.004)), ((0.014, 0.004), (-0.012, -0.042))):
        a_ = f3((x0, y0)); ab = f3((x1, y1)) - a_
        t = np.clip(((Q[..., :2] - a_) @ ab) / float(ab @ ab), 0, 1)
        bolt = np.minimum(bolt, np.linalg.norm(Q[..., :2] - (a_ + t[..., None] * ab), axis=-1))
    sign = np.maximum(sign, smoothstep(0.0105, 0.006, bolt)) * (NQ[..., 2] > 0.6)
    lc = lc * (1 - sign[..., None]) + teal * sign[..., None]
    # Deckel innen: dunkler Bildschirm mit türkisen Zeilen
    scr = (NQ[..., 2] < -0.6) * smoothstep(W - 0.012, W - 0.02, np.abs(Q[..., 0])) * smoothstep(D - 0.012, D - 0.02, np.abs(Q[..., 1]))
    row = np.floor((Q[..., 1] + D) / 0.022); frac = ((Q[..., 1] + D) / 0.022) % 1.0
    length = 0.06 + 0.24 * ((np.sin(row * 12.9898) * 43758.5453) % 1.0)
    line = (frac > 0.3) * (frac < 0.62) * (Q[..., 0] > -W + 0.03) * (Q[..., 0] < -W + 0.03 + length) * (np.abs(Q[..., 1]) < D - 0.03)
    sc = gradient((0.07, 0.06, 0.16), (0.13, 0.12, 0.3), smoothstep(-D, D, Q[..., 1]))
    sc = sc * (1 - line[..., None] * 0.9) + teal * (line[..., None] * 0.9)
    lc = lc * (1 - scr[..., None]) + sc * scr[..., None]
    col = np.where(lidm[..., None], lc, col)
    em += np.where(lidm[..., None], teal * (0.9 * sign + 0.0)[..., None] + sc * (0.75 * scr)[..., None], 0)
    # Basis oben: Tastenfeld und die leuchtende Bedienfläche, auf die der Finger tippt
    top = (TG == 0) * (N[..., 2] > 0.7)
    keys = top * (P[..., 1] < 0.0) * (np.abs(P[..., 0]) < W - 0.025) * (P[..., 1] > -D + 0.03)
    kx = (P[..., 0] / 0.03) % 1.0; ky = (P[..., 1] / 0.03) % 1.0
    key = keys * (kx > 0.14) * (kx < 0.86) * (ky > 0.14) * (ky < 0.86)
    col = mix(col, (0.3, 0.28, 0.44), 0.9 * keys); col = mix(col, (0.44, 0.42, 0.6), 0.9 * key)
    pad = top * smoothstep(0.055, 0.047, np.abs(P[..., 0] + 0.075)) * smoothstep(0.045, 0.037, np.abs(P[..., 1] - 0.06))
    col = mix(col, (0.2, 0.9, 0.88), pad); em += teal * (0.8 * pad)[..., None]
    finish_paint(T, col, em, strength=1.0)
    return g

# ---------------------------------------------------------------- Haltung mit Laptop, Bewegungen

LAP_C = V((0.2, -0.47, 0.985))                    # Laptop: Mitte der Unterseite in der Haltung der Vorlage
LAP_V = V((-0.36, 1.0, 0.0)).normalized()       # von hinten (Scharnier) nach vorn zur Figur
LAP_U = LAP_V.cross(V((0, 0, 1))).normalized()          # Breite, nach links der Figur
LAP_TK = 0.011

def lap_pt(u, v, w, c=None):
    return (c if c is not None else LAP_C) + LAP_U * u + LAP_V * v + V((0, 0, 1)) * w

def hold_pose(arm, tap=0.0, push=0.0, breathe=0.0, nod=0.0, lean=0.0, hop=0.0, right=None):
    """Haltung der Vorlage: linke Hand stützt den Laptop von unten, rechter Zeigefinger tippt auf die Bedienfläche.
    tap: Finger hebt sich um so viel (0 = berührt); push: Laptop geht so weit nach vorn; right: andere Lage der rechten
    Hand als (Handgelenk, Finger, Handrücken). Liefert die Lage des Laptops (auch für die Ruhelage)."""
    reset_pose(arm)
    k = HAND_K
    move_world(arm, "Root", (0, 0, hop))
    rot_world(arm, "Spine", (1, 0, 0), 2 + lean); rot_world(arm, "Chest", (1, 0, 0), 3 + breathe + lean)     # leicht vorgebeugt
    rot_world(arm, "Neck", (1, 0, 0), 3 + nod); rot_world(arm, "Head", (1, 0, 0), 4 + nod); rot_world(arm, "Head", (0, 0, 1), 12)   # Blick zum Laptop
    for sfx, sg in ((".L", 1), (".R", -1)):
        rot_world(arm, "UpLeg" + sfx, (0, 1, 0), -7 * sg); rot_world(arm, "Leg" + sfx, (0, 1, 0), 2 * sg); rot_world(arm, "Foot" + sfx, (0, 1, 0), 5 * sg)
    update()
    C = LAP_C + V((0, -push, 0.4 * push))
    # linke Hand: flach unter der Basis, Finger zeigen schräg nach vorn rechts, Daumen außen
    fin = (LAP_U * 0.92 - LAP_V * 0.38).normalized(); back = V((0, 0, -1))      # Finger zeigen zur linken Kante und greifen um sie
    palm = lap_pt(LAP_W + 0.014 - 0.048 * k, 0.0, -0.004, C)                    # Fingeransatz knapp außerhalb der Kante
    X = fin.cross(back).normalized(); F = Matrix((X, fin, back)).transposed()
    wl = palm - F @ V((0, 0.06 * k, -0.037 * k))
    reach(arm, ".L", wl, (0.8, 0.3, -0.5)); F1 = turn_hand(arm, ".L", fin, back)
    wl_now = bone_head(arm, "Hand.L")
    # rechte Hand: Zeigefinger auf der Bedienfläche
    if right is None:
        tip = lap_pt(-0.075, 0.045, 2 * LAP_TK + 0.004 + tap, C)
        fin_r = V((0.34, -0.52, -0.78)).normalized(); back_r = V((0.1, -0.5, 0.86))
        Zr = (back_r - fin_r * back_r.dot(fin_r)).normalized(); Xr = fin_r.cross(Zr)
        wr = tip - Matrix((Xr, fin_r, Zr)).transposed() @ V((-0.048 * k, 0.2 * k, -0.03 * k))
    else:
        wr, fin_r, back_r = right
    reach(arm, ".R", wr, (-0.75, 0.2, -0.45)); turn_hand(arm, ".R", fin_r, back_r)
    M = Matrix((LAP_U, LAP_V, V((0, 0, 1)))).transposed().to_4x4(); M.translation = C
    wl_rest = V(arm.data.bones["Hand.L"].head_local)
    rest = Matrix.Translation(wl_rest) @ (HAND_FRAMES[".L"] @ F1.transposed()).to_4x4() @ Matrix.Translation(-wl_now) @ M
    return {"rest": rest, "world": M}

def animate(arm):
    S = lambda t, ph=0.0: math.sin((t - ph) * 2 * math.pi)
    tapf = lambda t: 0.03 * max(0.0, math.sin(t * 2 * math.pi * 4)) ** 2            # vier kurze Tipper je Durchlauf
    idle = [(i * 4, (lambda t=i / 16.0: hold_pose(arm, tap=tapf(t), breathe=1.2 * S(t), nod=1.0 * S(t, 0.1)))) for i in range(17)]
    pose = [(i * 6, (lambda t=i / 8.0: hold_pose(arm, tap=0.012 + 0.012 * S(t * 2), breathe=1.0 * S(t), nod=1.2 * S(t, 0.1)))) for i in range(9)]
    # Schuss: beginnt in der Haltung, der Finger schlägt auf die Taste, der Laptop stößt kurz nach vorn, zurück
    shoot = [(0, lambda: hold_pose(arm, tap=0.02)), (2, lambda: hold_pose(arm, tap=0.0, push=0.045, lean=3.0)),
             (5, lambda: hold_pose(arm, tap=0.03, push=0.02, lean=1.0)), (9, lambda: hold_pose(arm, tap=0.024, push=0.0)),
             (12, lambda: hold_pose(arm, tap=0.02))]
    def cheer(t):
        up = 0.5 + 0.5 * S(t * 2)
        wr = V((-0.36, -0.08, 1.5 + 0.1 * up))
        hold_pose(arm, hop=0.1 * abs(S(t)), nod=-10, lean=-3, right=(wr, V((-0.15, 0.0, 1.0)), V((-1, 0.2, 0))))
    win = [(i * 6, (lambda t=i / 8.0: cheer(t))) for i in range(9)]
    make_actions(arm, [("Idle", idle), ("Pose", pose), ("Shoot", shoot), ("Victory", win)])

# ---------------------------------------------------------------- Bemalung

HEM = 0.74                                      # Unterkante des Hoodies
HOOD_L, HOOD_M, HOOD_D = (0.86, 0.81, 0.98), (0.74, 0.67, 0.93), (0.52, 0.44, 0.78)
DARK_L, DARK_M, DARK_D = (0.42, 0.3, 0.68), (0.3, 0.2, 0.53), (0.17, 0.1, 0.34)
HAIR_L, HAIR_M, HAIR_D = (0.72, 0.46, 0.27), (0.55, 0.32, 0.18), (0.34, 0.18, 0.1)
SKIN_L, SKIN_M, SKIN_D = (1.0, 0.84, 0.7), (0.99, 0.76, 0.6), (0.88, 0.6, 0.46)

def paint(g):
    ao = vertex_ao(g, rays=16, dist=0.26)
    T = texels(g); P, N, cov = T["P"], T["N"], T["cov"]
    AO = texel_values(T, ao)
    TG = np.rint(texel_values(T, part_tags(g))).astype(int)
    x, y, z = P[..., 0], P[..., 1], P[..., 2]; ax = np.abs(x)
    lit = smoothstep(0.05, 0.95, np.clip(N[..., 2] * 0.42 + 0.5 - 0.12 * N[..., 1], 0, 1))      # Licht von oben vorn
    occ = np.clip(AO * 2.2, 0, 1) ** 0.85
    sel = lambda t: ((TG == t) & cov).astype(np.float32)
    col = np.zeros(P.shape, np.float32); em = np.zeros(P.shape, np.float32)
    def lay(mask, c):
        nonlocal col
        col = col * (1 - mask[..., None]) + c * mask[..., None]
    # ---- Hoodie und Hose (eine Haut): Bereiche nach der Lage
    cl = sel(T_CLOTH)
    wr = V(J["wrist"]); el = V(J["elbow"]); d_arm = (wr - el).normalized(); cuff_c = wr - d_arm * 0.045
    Pa = np.stack([ax, y, z], -1)
    rel = Pa - f3(cuff_c); along = rel @ f3(d_arm)
    cuff = smoothstep(0.0, 0.012, along + 0.035) * (np.linalg.norm(rel, axis=-1) < 0.16) * cl
    tro = smoothstep(HEM + 0.003, HEM - 0.003, z) * (ax < 0.4) * (1 - cuff) * cl
    hood = cl * (1 - tro) * (1 - cuff)
    hc = three(HOOD_D, HOOD_M, HOOD_L, lit)
    fold = fbm3(P * f3((1.0, 1.0, 2.6)), 5.0, 3, 3)
    hc = mix(hc, HOOD_D, 0.22 * smoothstep(0.52, 0.72, fold))                                  # weiche breite Falten
    band = smoothstep(HEM + 0.07, HEM + 0.062, z) * (ax < 0.34)                                 # Saumbund: Rippen
    rib = 0.5 + 0.5 * np.sin(np.arctan2(y, x) * 46)
    hc = mix(hc, HOOD_D, band * (0.2 + 0.25 * smoothstep(0.55, 0.9, rib)))
    hc = mix(hc, HOOD_D, 0.55 * smoothstep(0.006, 0.002, np.abs(z - (HEM + 0.068))) * (ax < 0.34))
    front = smoothstep(-0.2, -0.5, N[..., 1])
    pk = np.full(P.shape[:-1], 9.0, np.float32)                                                 # Bauchtasche: Naht und Eingriffe
    for (x0, z0), (x1, z1) in (((0.175, 0.815), (0.115, 0.985)), ((0.115, 0.985), (-0.115, 0.985)), ((-0.115, 0.985), (-0.175, 0.815))):
        a_ = f3((x0, z0)); ab = f3((x1, z1)) - a_; XZ = np.stack([x, z], -1)
        t = np.clip(((XZ - a_) @ ab) / float(ab @ ab), 0, 1)
        pk = np.minimum(pk, np.linalg.norm(XZ - (a_ + t[..., None] * ab), axis=-1))
    hc = mix(hc, HOOD_D, 0.65 * smoothstep(0.007, 0.003, pk) * front * (z > HEM + 0.07))
    hc = mix(hc, (0.44, 0.36, 0.7), 0.5 * smoothstep(0.03, 0.008, pk) * front * (z < 0.93) * (z > HEM + 0.07) * (ax > 0.1))
    hc = mix(hc, (0.4, 0.3, 0.66), 0.5 * occ)
    lay(hood, hc)
    cc = three(DARK_D, DARK_M, DARK_L, lit)
    perp = rel - along[..., None] * f3(d_arm)
    cc = mix(cc, DARK_D, 0.4 * smoothstep(0.5, 0.9, 0.5 + 0.5 * np.sin(np.arctan2(perp[..., 1], perp[..., 2]) * 22)))
    lay(cuff, mix(cc, (0.1, 0.06, 0.22), 0.4 * occ))
    tc = three(DARK_D, DARK_M, DARK_L, lit)
    tc = mix(tc, DARK_D, 0.3 * smoothstep(0.5, 0.72, fbm3(P * f3((1.0, 1.0, 2.2)), 5.5, 9, 3)))
    tc = mix(tc, DARK_D, 0.5 * smoothstep(0.006, 0.002, ax) * front * (z > 0.56))               # Naht vorn
    tc = mix(tc, DARK_D, 0.45 * smoothstep(0.3, 0.2, z) * smoothstep(0.5, 0.9, 0.5 + 0.5 * np.sin(np.arctan2(y, ax - J["ankle"][0]) * 14)))   # gerafft
    lay(tro, mix(tc, (0.09, 0.05, 0.2), 0.45 * occ))
    # ---- Haut
    sk = sel(T_SKIN)
    sc = three(SKIN_D, SKIN_M, SKIN_L, lit)
    for s in (1, -1):
        sc = mix(sc, (1.0, 0.62, 0.58), 0.42 * np.exp(-(((x - 0.17 * s) / 0.055) ** 2 + ((z - (HC.z - 0.105)) / 0.04) ** 2)) * (y < -0.1))   # Wangen
        sc = mix(sc, SKIN_D, 0.6 * np.exp(-(((ax - 0.3) / 0.02) ** 2 + ((z - (HC.z - 0.04)) / 0.04) ** 2 + ((y - 0.005) / 0.03) ** 2)))     # Ohrmuschel
    lay(sk, mix(sc, (0.72, 0.42, 0.34), 0.38 * occ))
    # ---- Haare
    hr = sel(T_HAIR)
    hcol = three(HAIR_D, HAIR_M, HAIR_L, smoothstep(0.1, 0.95, 0.75 * lit + 0.25 * (1 - occ)))
    lay(hr, mix(hcol, (0.22, 0.1, 0.06), 0.55 * occ))
    # ---- Schuhe
    shm = sel(T_SHOE)
    scol = three(DARK_D, (0.36, 0.25, 0.62), (0.5, 0.38, 0.78), lit)
    light = three((0.62, 0.56, 0.84), (0.84, 0.8, 0.96), (0.96, 0.94, 1.0), lit)
    white = np.clip(smoothstep(0.062, 0.054, z) + smoothstep(-0.262, -0.275, y) * (z > 0.05) + smoothstep(0.125, 0.14, y) * (z < 0.2), 0, 1)
    scol = scol * (1 - white[..., None]) + light * white[..., None]
    scol = mix(scol, (0.24, 0.16, 0.44), 0.8 * smoothstep(0.006, 0.002, np.abs(z - 0.064)))     # Linie über der Sohle
    lay(shm, mix(scol, (0.12, 0.07, 0.26), 0.45 * occ))
    # ---- Rucksack, Gurte, Taschen
    for t_, base in ((T_PACK, ((0.2, 0.12, 0.4), (0.34, 0.23, 0.6), (0.48, 0.36, 0.76))), (T_STRAP, ((0.14, 0.08, 0.3), (0.24, 0.16, 0.45), (0.36, 0.26, 0.6))),
                     (T_POCKET, ((0.2, 0.12, 0.4), (0.33, 0.23, 0.58), (0.46, 0.34, 0.72)))):
        lay(sel(t_), mix(three(*base, lit), (0.08, 0.04, 0.2), 0.5 * occ))
    # ---- Kopfhörer, Brille, Brauen, Mund, helle Teile
    lay(sel(T_PHONE), mix(three((0.56, 0.5, 0.8), (0.8, 0.76, 0.95), (0.95, 0.93, 1.0), lit), (0.3, 0.24, 0.55), 0.4 * occ))
    lay(sel(T_CUSH), three((0.1, 0.06, 0.22), (0.2, 0.13, 0.38), (0.32, 0.23, 0.54), lit))
    lay(sel(T_GLASS), three((0.11, 0.07, 0.24), (0.2, 0.14, 0.4), (0.38, 0.3, 0.62), lit))
    lay(sel(T_BROW), three((0.2, 0.1, 0.05), (0.32, 0.17, 0.09), (0.46, 0.27, 0.15), lit))
    lay(sel(T_MOUTH), np.zeros(P.shape, np.float32) + f3((0.5, 0.17, 0.17)))
    lay(sel(T_LACE), mix(three((0.7, 0.66, 0.9), (0.9, 0.88, 0.99), (1.0, 1.0, 1.0), lit), (0.4, 0.34, 0.66), 0.35 * occ))
    lay(sel(T_TAB), three((0.5, 0.42, 0.76), (0.68, 0.61, 0.9), (0.84, 0.79, 0.97), lit))
    tl = sel(T_TEAL)
    tcol = three((0.08, 0.6, 0.66), (0.18, 0.86, 0.86), (0.6, 1.0, 0.97), lit)
    lay(tl, tcol); em += tcol * (0.55 * tl)[..., None]
    finish_paint(T, col, em, strength=1.0)

# ---------------------------------------------------------------- Ablauf

FLAT = {T_SKIN: (0.95, 0.72, 0.55), T_CLOTH: (0.76, 0.7, 0.93), T_HAIR: (0.56, 0.33, 0.2), T_SHOE: (0.36, 0.25, 0.6), T_PACK: (0.3, 0.2, 0.52),
        T_PHONE: (0.74, 0.68, 0.9), T_GLASS: (0.2, 0.14, 0.38), T_BROW: (0.3, 0.17, 0.1), T_TEAL: (0.2, 0.84, 0.84), T_STRAP: (0.26, 0.18, 0.46),
        T_POCKET: (0.3, 0.2, 0.52), T_LACE: (0.92, 0.9, 1.0), T_TAB: (0.82, 0.77, 0.96), T_MOUTH: (0.5, 0.2, 0.2), T_CUSH: (0.25, 0.17, 0.44)}

def build(out):
    body = to_tris(body_shape(), 6500); head = to_tris(head_shape(), 2600); hair = hair_shape(); to_tris(hair[0], 900)
    dg = bpy.context.evaluated_depsgraph_get()
    bvh_b = BVHTree.FromObject(body, dg); bvh_h = BVHTree.FromObject(head, dg)
    arm = biped(J)
    mark(body, T_CLOTH, G_BODY)
    auto_bind(body, arm, {"Hips", "Spine", "Chest", "Neck"} | {b + s for b in ("Shoulder", "UpperArm", "ForeArm", "UpLeg", "Leg", "Foot") for s in (".L", ".R")})
    parts = [body, mark(head, T_SKIN, G_HEAD, "Head")] + [mark(o, T_HAIR, G_HEAD, "Head") for o in hair]
    # Hände: rechts zeigt der Zeigefinger (tippt), links stützt die offene Hand den Laptop
    for s, sfx, curls, th in ((-1, ".R", (0.12, 0.85, 0.9, 0.92), 0.7), (1, ".L", (0.62, 0.62, 0.64, 0.66), 0.0)):
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
    for sx in (1, -1):                                                              # zwei flache Bänder der Kapuze
        hit = bvh_b.ray_cast(V((0.05 * sx, -2.0, 1.17)), V((0, 1, 0)), 6.0)[0]
        parts.append(mark(rounded_box("Band%d" % sx, hit + V((0, -0.006, -0.02)), (0.016, 0.009, 0.055), 0.007), T_TAB, G_BODY, "Chest"))
    g = join_parts(parts, "Nerd")
    for p in g.data.polygons:
        p.use_smooth = True
    g.data.materials.clear(); g.data.materials.append(image_material("Nerd", int(os.environ.get("TEXTUR", "2048")), color=(0.74, 0.67, 0.93), rough=0.55))
    smart_uv(g, margin=0.004)
    paint(g)
    g = join_parts([g] + [mark(o, 20, G_HEAD, "Head") for o in eyes], "Nerd")
    bpy.context.scene.render.fps = FPS
    reset_pose(arm)
    # Laptop: in der Haltung der Vorlage bauen und in die Ruhelage der linken Hand zurückrechnen (hängt starr an ihr)
    P = hold_pose(arm)
    lap = laptop()
    lap.data.transform(P["rest"]); lap.data.update()
    lap.data.attributes.remove(lap.data.attributes["teil"])
    mark(lap, 21, G_LAPTOP, "Hand.L")
    reset_pose(arm)
    g = join_parts([g, lap], "Nerd")
    g.parent = arm; md = g.modifiers.new("Armature", 'ARMATURE'); md.object = arm
    animate(arm)
    co = np.array([tuple(v.co) for v in g.data.vertices])
    print("MASSE x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (co[:, 0].min(), co[:, 0].max(), co[:, 1].min(), co[:, 1].max(), co[:, 2].min(), co[:, 2].max()))
    print("DREIECKE", sum(len(p.vertices) - 2 for p in g.data.polygons), "AKTIONEN", [(a_.name, int(a_.frame_range[1])) for a_ in bpy.data.actions])
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS',
                              export_yup=True, export_apply=False, export_force_sampling=True,
                              export_image_format='JPEG', export_jpeg_quality=90)

if __name__ == "__main__":
    bpy.ops.wm.read_factory_settings(use_empty=True)
    build(OUT)
    print("FERTIG", OUT)
