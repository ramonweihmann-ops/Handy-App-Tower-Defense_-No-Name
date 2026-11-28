# Fünkchen „Sternenschuppen“ (Wunsch 27.11.2026): der bezahlte Champion in Boss-Qualität, nachgebaut nach
# Vorlage_Raw/Fuenkchen_Premium_v1 (Ansichten, Detailblatt, BAUANLEITUNG_CLAUDE.md).
# Aufruf: blender -b -P tools/heroes/fuenkchen_premium.py -- fuenkchen <ziel.glb>
#   STUFE=form  nur die Form in Grau (Prüfschritt A der Anleitung), ohne Bemalung und Skelett
# Aufbau wie bei den Monstern der Schlangenhöhle (tools/monster/zauberthron.py): weiche Formen aus Metaballs, neu
# vernetzt und geglättet; Platten, Hörner, Krallen und Flügel als eigene glatte Teile; alles im Raum bemalt
# (Verläufe statt roher Farbflächen). Höhe 2,0, Füße auf z = 0, Blick nach -Y wie alle Comic-Helden.
# Kopf und Unterkiefer sind eigene, starre Teile (Knochen Head und Jaw): das Gesicht verzieht sich in keiner
# Bewegung, das Maul lässt sich weit öffnen, der Halsreif verdeckt den Übergang zum Rumpf.
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "monster"))
from zauberthron import *

STUFE = os.environ.get("STUFE", "voll")

# ---------------------------------------------------------------- Maße (Blender: x rechts/links, -y vorn, z oben)

H0 = Vector((0.0, -0.22, 1.40))                 # Kopfmitte
YH = H0.y - 0.05                                # hier endet der Unterkiefer nach hinten
HINGE = Vector((0.0, YH, H0.z - 0.04))          # Kiefergelenk (Drehachse quer), auf Höhe der Mundwinkel
LIP = H0.z - 0.14                               # Oberlippe: Höhe der Mundlinie in der Mitte
NECK = (Vector((0.0, -0.14, 0.82)), Vector((0.0, -0.2, 1.1)))
TAIL = [(0.0, 0.4, 0.56), (0.0, 0.62, 0.49), (0.0, 0.84, 0.41), (0.0, 1.04, 0.35), (0.0, 1.22, 0.31), (0.0, 1.38, 0.3)]
TAIL_R = [0.215, 0.185, 0.15, 0.115, 0.082, 0.055]
FRONT = (0.235, -0.3)                           # Vorderbein: x, y am Boden
HIND = (0.285, 0.3)                             # Hinterbein
WING_ROOT = Vector((0.15, 0.2, 0.86))           # Flügelansatz auf dem Rücken, hinter den Schultern
WING_A = Vector((0.8, 0.6, 0.0)).normalized()   # Spannrichtung: nach außen und hinten
WING_B = Vector((0.0, 0.0, 1.0))                # nach oben
WING_N = WING_A.cross(WING_B)                   # Flächennormale (zeigt nach vorn außen)
WRIST = (0.4, 0.33)                             # Handgelenk in Flügelmaßen (entlang A, entlang B)
FINGERS = [((0.78, 0.34), (1.03, -0.06)),       # je Finger: Stützpunkt, Spitze (Flügelmaße)
           ((0.64, 0.0), (0.7, -0.42)),
           ((0.4, -0.02), (0.34, -0.37))]

def wing_pt(a, b, n=0.0, side=1):
    p = WING_ROOT + WING_A * a + WING_B * b + WING_N * n
    return Vector((p.x * side, p.y, p.z))

def qbez(p0, p1, p2, t):
    return p0 * ((1 - t) ** 2) + p1 * (2 * t * (1 - t)) + p2 * (t * t)

# ---------------------------------------------------------------- Bausteine

def sweep(name, pts, radii, segs=14, flat=1.0, flat_axis=None):
    """Runde Röhre entlang einer Linie; der Querschnitt wird mitgeführt (verdreht sich nicht), beide Enden laufen
    rund aus. flat < 1 drückt den Querschnitt entlang flat_axis zusammen."""
    P = [Vector(p) for p in pts]; n = len(P)
    T = [(P[min(i + 1, n - 1)] - P[max(i - 1, 0)]).normalized() for i in range(n)]
    ref = Vector((0, 0, 1)) if abs(T[0].z) < 0.85 else Vector((0, 1, 0))
    if flat_axis is not None:
        ref = Vector(flat_axis)
    n1 = (ref - T[0] * ref.dot(T[0])).normalized()
    bm = bmesh.new(); rings = []
    first = bm.verts.new(P[0] - T[0] * radii[0] * 0.7)
    for i in range(n):
        if i:
            n1 = T[i - 1].rotation_difference(T[i]) @ n1
            n1 = (n1 - T[i] * n1.dot(T[i])).normalized()
        n2 = T[i].cross(n1)
        rings.append([bm.verts.new(P[i] + (n1 * math.cos(a) * flat + n2 * math.sin(a)) * radii[i])
                      for a in [k * 2 * math.pi / segs for k in range(segs)]])
    last = bm.verts.new(P[-1] + T[-1] * radii[-1] * 0.7)
    for k in range(segs):
        bm.faces.new([first, rings[0][(k + 1) % segs], rings[0][k]])
        bm.faces.new([last, rings[-1][k], rings[-1][(k + 1) % segs]])
    for a, b in zip(rings, rings[1:]):
        for k in range(segs):
            bm.faces.new([a[k], a[(k + 1) % segs], b[(k + 1) % segs], b[k]])
    return finish(name, bm)

def leaf(name, base, up, along, height, length, thick, lean=0.0, sink=0.35, segs=(10, 6), petal=False):
    """Weiche Platte (Rückenkamm, Kragenblatt): unten breit, oben eine runde Spitze; lean kippt die Spitze entlang
    'along'. Der untere Teil steckt im Körper. petal: Blattform, am breitesten ein Drittel über dem Ansatz."""
    up = Vector(up).normalized(); along = Vector(along); along = (along - up * along.dot(up)).normalized()
    side = up.cross(along)
    o = sphere(name, (0, 0, 0), 1.0, segs=segs)
    for v in o.data.vertices:
        sx, sy, sz = v.co
        t = max(sz, 0.0)
        k = (1 - t) ** 0.3 if sz > 0 else 1.0
        if petal and sz > 0:
            k = math.sin(math.pi * (0.27 + 0.73 * t)) ** 0.85 / max(math.sqrt(1 - t * t), 0.12) if t < 0.995 else 0.0
        w = sz * height if sz > 0 else sz * height * sink
        u = sx * length * 0.5 * k + lean * height * t ** 1.6
        v.co = Vector(base) + along * u + side * (sy * thick * 0.5 * k) + up * w
    return o

def claw(name, base, d, r, L, drop=0.35):
    """stumpfe, leicht nach unten gebogene Kralle"""
    d = Vector(d).normalized(); base = Vector(base)
    pts = [base + d * (L * t) + Vector((0, 0, -drop * L * t * t)) for t in (0.0, 0.3, 0.6, 0.85, 1.0)]
    return sweep(name, pts, [r, r * 0.92, r * 0.72, r * 0.48, r * 0.26], segs=8)

# ---------------------------------------------------------------- Rumpf mit Hals, Beinen und Schwanz

def paw_shape(R, x, y, s):
    mb_ell(R, (x * s, y - 0.045, 0.082), (0.135, 0.17, 0.082))
    for dx in (-0.078, 0.0, 0.078):
        mb_ell(R, ((x + dx * 1.0) * s, y - 0.175 + 0.02 * abs(dx) / 0.078, 0.06), (0.05, 0.062, 0.058))

def body_shape():
    R = mb_family("Rumpf")
    mb_ell(R, (0, -0.13, 0.655), (0.29, 0.275, 0.295))               # Brust
    mb_ell(R, (0, 0.2, 0.6), (0.3, 0.31, 0.28))                      # Bauch und Becken
    mb_caps(R, tuple(NECK[0]), tuple(NECK[1]), 0.215)                # kurzer, kräftiger Hals
    n = 16
    for i in range(n):                                               # Schwanz: dick am Becken, läuft schlank aus
        t = i / (n - 1) * (len(TAIL) - 1); j = min(int(t), len(TAIL) - 2); f = t - j
        c = Vector(TAIL[j]).lerp(Vector(TAIL[j + 1]), f); r = TAIL_R[j] * (1 - f) + TAIL_R[j + 1] * f
        mb_ell(R, tuple(c), (r * 0.86, r * 0.86, r * 0.86))
    for s in (1, -1):
        x, y = FRONT                                                 # Vorderbeine: stämmige Säulen
        limb(R, [(0.21 * s, y + 0.02, 0.56), (x * s, y, 0.3), (x * s, y + 0.01, 0.13)], [0.135, 0.118])
        paw_shape(R, x, y + 0.02, s)
        x, y = HIND                                                  # Hinterbeine: runder Oberschenkel, kurzer Lauf
        mb_ell(R, (0.27 * s, y - 0.02, 0.47), (0.165, 0.215, 0.235))
        limb(R, [(x * s, y + 0.045, 0.33), (x * s, y + 0.02, 0.13)], [0.118])
        paw_shape(R, x, y + 0.02, s)
    g = mb_to_mesh(R)
    finish_skin(g, 0.014, 1.0, smooth_it=7)
    return g

# ---------------------------------------------------------------- Kopf und Unterkiefer

MOUTH_W = 0.25                                  # halbe Breite der Maulöffnung: breites Grinsen bis in die Wangen

def lip_up(x, y):
    """Mundlinie (Unterkante der Oberlippe): in der Mitte flach, zu den Mundwinkeln hin ansteigend = Lächeln"""
    return LIP + 0.1 * np.clip(np.abs(x) / 0.36, 0, 1.3) ** 2.3

def lip_gap(x, y):
    """Öffnung zwischen den Lippen: vorn in der Mitte weit, zu den Mundwinkeln und nach hinten geschlossen"""
    g = 0.128 * np.clip(1 - (x / MOUTH_W) ** 2, 0, 1) ** 0.5 * smoothstep(-0.28, -0.5, y)
    return np.where(g < 0.022, 0.0, g)                                              # endet rund statt als schmaler Schlitz

def palate(x, y):
    """Gaumen: hinter der Oberlippe wölbt sich das Maul nach oben"""
    return lip_up(x, y) + 0.045 * np.clip(1 - (x / (MOUTH_W - 0.02)) ** 2, 0, 1) * smoothstep(-0.69, -0.56, y) * smoothstep(-0.3, -0.42, y)

def lip_low(x, y):
    return lip_up(x, y) - lip_gap(x, y)

def mouth_solid():
    """Schnittkörper für das Maul: der Raum zwischen Unterlippe/Mundboden und Oberlippe/Gaumen. An den Mundwinkeln
    und hinten läuft er auf null aus, dort bleibt die Haut geschlossen."""
    xs = np.linspace(-MOUTH_W, MOUTH_W, 53); ys = np.linspace(-1.0, -0.28, 49)
    X, Y = np.meshgrid(xs, ys); T = palate(X, Y); Bt = lip_low(X, Y)
    bm = bmesh.new(); ny, nx = len(ys), len(xs)
    top = [[bm.verts.new((X[j, i], Y[j, i], T[j, i])) for i in range(nx)] for j in range(ny)]
    bot = [[bm.verts.new((X[j, i], Y[j, i], min(Bt[j, i], T[j, i]))) for i in range(nx)] for j in range(ny)]
    for j in range(ny - 1):
        for i in range(nx - 1):
            bm.faces.new([top[j][i], top[j][i + 1], top[j + 1][i + 1], top[j + 1][i]])
            bm.faces.new([bot[j][i], bot[j + 1][i], bot[j + 1][i + 1], bot[j][i + 1]])
    for i in range(nx - 1):
        bm.faces.new([top[0][i], bot[0][i], bot[0][i + 1], top[0][i + 1]])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    return finish("Maulschnitt", bm, smooth=False)

def cut(o, cutter, op):
    md = o.modifiers.new("Schnitt", 'BOOLEAN'); md.operation = op; md.object = cutter; md.solver = 'EXACT'
    apply_mod(o, md)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return o

NOSTRIL = (0.085, 0.055)                         # Nasenloch: x und Höhe über der Kopfmitte

def head_shape():
    """Kopf als eine runde Form: Schädel, Wangen, breites Untergesicht mit Kinn, darauf die kleine Schnauze.
    Das Maul wird danach als lächelnde Höhle herausgeschnitten; an den Mundwinkeln bleibt die Haut geschlossen."""
    R = mb_family("Kopf")
    mb_ell(R, H0, (0.395, 0.33, 0.33))                                              # Schädel
    mb_ell(R, H0 + Vector((0, -0.18, -0.19)), (0.3, 0.3, 0.175))                    # Untergesicht und kräftiges Kinn
    mb_ell(R, H0 + Vector((0, -0.37, -0.02)), (0.225, 0.2, 0.138))                  # breite, runde Schnauze: ihr unterer Rand ist die Oberlippe
    mb_ell(R, H0 + Vector((0, -0.455, 0.02)), (0.165, 0.115, 0.085))                # Nasenrücken: eine einzige runde Wölbung
    mb_ell(R, H0 + Vector((0, -0.33, -0.215)), (0.2, 0.19, 0.105))                  # Unterkiefer gehört zur Schnauze, etwas kürzer
    for s in (1, -1):
        mb_ell(R, H0 + Vector((0.21 * s, -0.14, -0.13)), (0.2, 0.2, 0.17))          # Wangen
    g = mb_to_mesh(R)
    finish_skin(g, 0.012, 1.0, smooth_it=6)
    cut(g, mouth_solid(), 'DIFFERENCE')
    finish_skin(g, 0.011, 1.0, smooth_it=5)                                         # Lippen rund, Maulhöhle sauber vernetzt
    bvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    for s in (1, -1):                                                               # Nasenlöcher: kleine Mulden in der runden Schnauze
        hit, n, _, _ = bvh.ray_cast(Vector((NOSTRIL[0] * s, H0.y - 2.0, H0.z + NOSTRIL[1])), Vector((0, 1, 0)), 6.0)
        for v in g.data.vertices:
            d = (v.co - hit).length / 0.024
            if d < 1:
                v.co -= n * (0.012 * (1 - d * d) ** 2)
    g.data.update()
    return g

def head_weights(o):
    """Der Kopf ist eine Haut; alles unter der Mundlinie folgt weich dem Kiefer, nach hinten zum Gelenk hin immer weniger"""
    gh = o.vertex_groups.new(name="Head"); gj = o.vertex_groups.new(name="Jaw")
    for v in o.data.vertices:
        x, y, z = v.co
        xa, ya = np.float32(x), np.float32(y)
        up = float(lip_up(xa, ya)); gap = float(lip_gap(xa, ya)); roof = float(palate(xa, ya))
        low = ramp(up - z, 0.0, 0.07)
        inside = 1.0 if z < 0.5 * (up - gap + roof) else 0.0
        k = ramp(gap, 0.0, 0.03)
        w = (low * (1 - k) + inside * k) * ramp(YH - y, -0.02, 0.14)
        if w > 0.002:
            gj.add([v.index], w, 'REPLACE')
        if w < 0.998:
            gh.add([v.index], 1 - w, 'REPLACE')

HORN_N = 16

def horn_pts(side):
    p0 = H0 + Vector((0.235 * side, 0.05, 0.225)); p1 = H0 + Vector((0.53 * side, 0.07, 0.43)); p2 = H0 + Vector((0.26 * side, 0.21, 0.61))
    return [qbez(p0, p1, p2, i / (HORN_N - 1)) for i in range(HORN_N)]

def horn(side):
    Q = horn_pts(side)
    n = HORN_N; pts = []; rad = []
    for i in range(n):
        t = i / (n - 1)
        pts.append(Q[i])
        r = 0.128 * (1 - t) ** 0.8 + 0.022
        rad.append(r * (1 + 0.045 * math.cos(t * 2 * math.pi * 4.2 + 0.6) * (1 - t)))     # sanfte Ringe
    return sweep("Horn%d" % side, pts, rad, segs=12)

def head_plates():
    """Kamm auf dem Kopf (drei Blätter zwischen den Hörnern), Platten den Hinterkopf hinab, Kragenblätter seitlich"""
    parts = []
    # Mittelreihe: Winkel um die Querachse des Kopfes (0 = oben, positiv = nach hinten)
    for i, (deg, hgt, ln, th) in enumerate(((-24, 0.075, 0.12, 0.08), (0, 0.115, 0.16, 0.1), (27, 0.15, 0.2, 0.125),
                                            (58, 0.13, 0.22, 0.14), (90, 0.115, 0.21, 0.14), (120, 0.09, 0.17, 0.12))):
        a = math.radians(deg)
        d = Vector((0, math.sin(a), math.cos(a)))
        base = H0 + Vector((0, d.y * 0.325, d.z * 0.325))
        parts.append(leaf("Kamm%d" % i, base, d, Vector((0, math.cos(a), -math.sin(a))), hgt, ln, th, lean=0.35))
    # Kragen: vier Blätter je Seite, strahlen hinter den Wangen nach außen und leicht nach hinten
    for s in (1, -1):
        for i, (deg, hgt, ln) in enumerate(((64, 0.2, 0.17), (36, 0.26, 0.2), (7, 0.3, 0.22), (-22, 0.28, 0.21), (-50, 0.22, 0.18))):
            a = math.radians(deg)
            rad = Vector((math.cos(a) * s, 0, math.sin(a)))
            base = H0 + Vector((rad.x * 0.36, 0.1, rad.z * 0.27 - 0.02))
            up = (rad + Vector((0, 0.42, 0))).normalized()
            parts.append(leaf("Kragen%d_%d" % (s, i), base, up, rad.cross(Vector((0, 1, 0))), hgt, ln, 0.085, lean=0.0, sink=0.5, petal=True))
    return parts

# ---------------------------------------------------------------- Rücken, Schwanz, Krallen

def spine_plates(bvh):
    """Kamm den Rücken und den Schwanz hinab: sitzt auf der Haut, wird nach hinten kleiner"""
    parts = []
    spots = [(0.0, 0.14, 0.2, 0.13), (0.19, 0.14, 0.2, 0.13), (0.38, 0.125, 0.185, 0.12), (0.56, 0.11, 0.165, 0.105),
             (0.72, 0.095, 0.145, 0.09), (0.86, 0.082, 0.13, 0.078), (0.99, 0.07, 0.112, 0.066), (1.105, 0.058, 0.096, 0.055),
             (1.205, 0.048, 0.08, 0.045), (1.29, 0.038, 0.064, 0.036)]
    for i, (y, hgt, ln, th) in enumerate(spots):
        hit, n, _, _ = bvh.ray_cast(Vector((0, y, 3.0)), Vector((0, 0, -1)), 6.0)
        hit2, _, _, _ = bvh.ray_cast(Vector((0, y + 0.04, 3.0)), Vector((0, 0, -1)), 6.0)
        along = (hit2 - hit).normalized()
        up = Vector((0, -along.z, along.y))
        if up.z < 0:
            up = -up
        parts.append(leaf("Ruecken%d" % i, hit, up, along, hgt, ln, th, lean=0.45))
    return parts

def claws():
    parts = []
    for s in (1, -1):
        for nm, (x, y) in (("V", FRONT), ("H", HIND)):
            for j, dx in enumerate((-0.078, 0.0, 0.078)):
                base = Vector(((x + dx) * s, y + 0.02 - 0.2 + 0.02 * abs(dx) / 0.078, 0.062))
                parts.append(claw("Kralle%s%d_%d" % (nm, s, j), base, (dx * 0.6 * s, -1, 0.05), 0.036, 0.085))
    return parts

# ---------------------------------------------------------------- Flügel

def finger_curve(i, t):
    w = Vector((WRIST[0], WRIST[1], 0)); c, e = FINGERS[i]
    return qbez(w, Vector((c[0], c[1], 0)), Vector((e[0], e[1], 0)), t)

def arm_curve(t):
    """vom Ansatz zum Handgelenk, leicht nach oben gewölbt"""
    return qbez(Vector((0, 0, 0)), Vector((0.17, 0.22, 0)), Vector((WRIST[0], WRIST[1], 0)), t)

def wing(side):
    """Ein Flügel: Arm vom Rücken zum Handgelenk, drei Finger, dazwischen die dünne Haut mit geschwungenem Rand.
    Liefert (Arme und Finger, Flughaut)."""
    W = lambda q, n=0.0: wing_pt(q.x, q.y, n, side)
    bones = [sweep("FluegelArm%d" % side, [W(arm_curve(t)) for t in np.linspace(0, 1, 9)], list(np.linspace(0.062, 0.046, 9)), segs=10)]
    for i, (r0, r1) in enumerate(((0.044, 0.014), (0.032, 0.011), (0.03, 0.011))):
        bones.append(sweep("Finger%d_%d" % (side, i), [W(finger_curve(i, t)) for t in np.linspace(0, 1, 9)], list(np.linspace(r0, r1, 9)), segs=8))
    bones.append(sphere("Handgelenk%d" % side, tuple(W(Vector((WRIST[0], WRIST[1], 0)))), 0.056, segs=(10, 7)))
    bones.append(sphere("Schulter%d" % side, tuple(W(Vector((-0.01, -0.03, 0)))), 0.074, segs=(12, 8)))
    # Flughaut: Felder zwischen den Fingern und zwischen innerem Finger und Arm
    curves = [lambda t, i=i: finger_curve(i, t) for i in range(3)] + [lambda t: arm_curve(1 - t)]
    bm = bmesh.new(); ns, nt = 6, 7; cache = {}
    def vert(panel, si, ti):
        key = (panel, si, ti) if 0 < si < ns else ((panel if si == 0 else panel + 1), 0, ti)
        if ti == 0:
            key = ("w",)
        if key not in cache:
            s = si / ns; t = ti / nt
            edge = 1 - (0.2 if panel < 2 else 0.3) * math.sin(math.pi * s) ** 0.9       # geschwungener Außenrand
            q = curves[panel](t * edge).lerp(curves[panel + 1](t * edge), s) if 0 < si < ns else curves[panel if si == 0 else panel + 1](t)
            bulge = 0.035 * math.sin(math.pi * s) * t
            cache[key] = bm.verts.new(W(q, -bulge))
        return cache[key]
    for panel in range(3):
        for si in range(ns):
            for ti in range(nt):
                q = [vert(panel, si, ti), vert(panel, si + 1, ti), vert(panel, si + 1, ti + 1), vert(panel, si, ti + 1)]
                q = [v for k, v in enumerate(q) if v not in q[:k]]
                if len(q) >= 3:
                    bm.faces.new(q if side > 0 else q[::-1])
    skin = finish("Flughaut%d" % side, bm)
    md = skin.modifiers.new("Dicke", 'SOLIDIFY'); md.thickness = 0.016; md.offset = 0.0; apply_mod(skin, md)
    for p in skin.data.polygons:
        p.use_smooth = True
    return bones, skin

# ---------------------------------------------------------------- Teile kennzeichnen

T_BODY, T_PLATE, T_HORN, T_MEM, T_BROW, T_TONGUE, T_TOOTH, T_GEM, T_GOLD, T_JAW, T_HEAD, T_WARM, T_CLAW = range(13)
G_BODY, G_HEAD, G_JAW, G_WL, G_WR, G_NECK, G_TAIL = range(7)       # Gruppen für die Prüfung auf Durchdringungen

def mark(o, teil, grp, bone=None):
    """Teilnummer (für die Bemalung) und Gruppe (für die Prüfung) je Punkt merken; bone: starr an diesem Knochen"""
    tag(o, teil)
    a = o.data.attributes.new("gruppe", 'FLOAT', 'POINT'); a.data.foreach_set("value", [float(grp)] * len(o.data.vertices))
    if bone:
        group_all(o, bone)
    return o

def to_tris(o, target):
    """auf etwa target Dreiecke verringern"""
    n = sum(len(p.vertices) - 2 for p in o.data.polygons)
    if n > target:
        reduce(o, target / n)
    return o

def ramp(x, a, b):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)

def line_param(P, pts):
    """Abstand zur Linie durch pts und Lage entlang der Linie (Bogenlänge) für jeden Punkt in P"""
    best = np.full(P.shape[:-1], 9.0, np.float32); par = np.zeros(P.shape[:-1], np.float32); cum = 0.0
    for a, b in zip(pts, pts[1:]):
        a = f3(a); b = f3(b); ab = b - a; L = float(np.linalg.norm(ab))
        t = np.clip(((P - a) @ ab) / max(L * L, 1e-9), 0, 1)
        d = np.linalg.norm(P - (a + t[..., None] * ab), axis=-1)
        closer = d < best
        par = np.where(closer, cum + t * L, par); best = np.where(closer, d, best); cum += L
    return best, par

# ---------------------------------------------------------------- Bauchschilde

SEG = 0.118                                     # Länge eines Bauchschilds entlang des Bauchs
BELLY_W = ([0.0, 0.15, 0.32, 0.46, 0.62, 0.8, 0.96, 1.1, 1.3, 1.5, 1.95, 2.3],          # Lage entlang der Bauchlinie
           [0.12, 0.16, 0.15, 0.108, 0.084, 0.086, 0.13, 0.11, 0.084, 0.086, 0.05, 0.024])  # halbe Breite: schmal zwischen den Beinen

def belly_line(bvh):
    """Mittellinie der hellen Unterseite: Kehle, Brust, Bauch, Schwanzunterseite (auf der Haut)"""
    pts = []
    for zz in (1.0, 0.9, 0.8, 0.7, 0.6, 0.5):
        pts.append(bvh.ray_cast(Vector((0, -2.0, zz)), Vector((0, 1, 0)), 6.0)[0])
    for yy in (-0.27, -0.15, 0.0, 0.15, 0.3, 0.43, 0.56, 0.7, 0.85, 1.0, 1.15, 1.28):
        pts.append(bvh.ray_cast(Vector((0, yy, -1.0)), Vector((0, 0, 1)), 6.0)[0])
    return [tuple(p) for p in pts]

def belly_fields(P, N, line):
    """Maske der Unterseite (0..1) und Lage im Schild (0 = oberer Rand, 1 = unterer Rand)"""
    d, par = line_param(P, line)
    x = P[..., 0]
    w = np.interp(par, BELLY_W[0], BELLY_W[1]).astype(np.float32)
    ax_ = np.abs(x); y = P[..., 1]; z = P[..., 2]
    legf = np.hypot(ax_ - FRONT[0], y - FRONT[1]) / 0.158                                    # Vorderbein: Kreis um die Beinachse
    legh = np.hypot((ax_ - 0.275) / 0.185, (y - HIND[1] + 0.02) / 0.235)                    # Oberschenkel: Ellipse
    m = smoothstep(w + 0.003, w - 0.003, ax_) * smoothstep(0.36, 0.31, d) * smoothstep(0.4, 0.1, N[..., 2])
    frac = ((par + 1.5 * x * x) / SEG) % 1.0
    return m, frac, np.abs(x) / np.maximum(w, 1e-3)

def belly_bulge(body, line):
    """Schilde leicht aufwölben, an den Fugen bleibt die Haut auf ihrer Höhe"""
    me = body.data; n = len(me.vertices)
    P = np.zeros(n * 3, np.float32); me.vertices.foreach_get("co", P); P = P.reshape(n, 3)
    N = np.array([tuple(v.normal) for v in me.vertices], np.float32)
    m, frac, _ = belly_fields(P, N, line)
    P += N * (0.016 * m * np.sin(np.pi * np.clip(frac, 0, 1)) ** 0.6)[:, None]
    me.vertices.foreach_set("co", P.ravel()); me.update()

# ---------------------------------------------------------------- Gesicht

EYE = (0.222, 0.108)                               # Augenmitte: x, z ab Kopfmitte
EYE_R = (0.118, 0.08, 0.142)                    # halbe Breite, Tiefe, halbe Höhe des Augapfels
EYES = []                                       # je Auge: Mitte, Achse rechts, Achse oben, Blickachse

def eye_material():
    """Großes Kulleraugen-Bild mit weichen Verläufen: Augenweiß mit Lidschatten, Iris oben türkis und unten golden,
    große Pupille, zwei Glanzlichter, dunkler Lidrand. Bildmitte = Augenmitte."""
    n = 256
    ax = np.linspace(-1, 1, n, dtype=np.float32); x, y = np.meshgrid(ax, ax)
    r = np.hypot(x, y)
    col = np.zeros((n, n, 3), np.float32) + f3((0.98, 0.98, 1.0))
    col = mix(col, (0.66, 0.62, 0.9), 0.6 * smoothstep(0.1, 0.95, y) + 0.25 * smoothstep(0.55, 0.95, r))
    ix, iy = x / 0.76, (y - 0.07) / 0.62                 # große Iris, oben vom Lid angeschnitten: freundlicher Blick
    ir = np.hypot(ix, iy)
    iris = gradient((0.99, 0.84, 0.28), (0.2, 0.84, 0.84), smoothstep(-0.75, -0.05, iy))
    iris = mix(iris, (0.08, 0.5, 0.74), 0.85 * smoothstep(0.1, 0.9, iy))
    iris = mix(iris, (1.0, 0.97, 0.6), 0.5 * np.exp(-((ix) ** 2 + (iy + 0.72) ** 2) / 0.12))        # Schimmer unten
    iris = mix(iris, (0.04, 0.2, 0.4), 0.9 * smoothstep(0.8, 1.0, ir))                               # dunkler Irisrand
    iris = mix(iris, (0.03, 0.02, 0.08), smoothstep(0.6, 0.52, ir))                                  # Pupille
    col = mix(col, iris, smoothstep(1.0, 0.95, ir))
    col = mix(col, (1.0, 1.0, 1.0), smoothstep(0.26, 0.2, np.hypot(ix + 0.3, iy - 0.36)))            # großes Glanzlicht
    col = mix(col, (1.0, 1.0, 1.0), 0.9 * smoothstep(0.11, 0.07, np.hypot(ix - 0.3, iy + 0.34)))     # kleines Glanzlicht
    lid = smoothstep(0.78 - 0.1 * smoothstep(0.0, 0.8, y), 0.93, r)
    col = mix(col, (0.13, 0.05, 0.25), 0.95 * lid)
    arr = np.ones((n, n, 4), np.float32); arr[..., :3] = np.clip(col, 0, 1)
    em = arr.copy(); em[..., :3] *= 0.22
    m = bpy.data.materials.new("Auge"); m.use_nodes = True
    nt = m.node_tree; pr = nt.nodes["Principled BSDF"]
    pr.inputs["Roughness"].default_value = 0.14
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = new_image("Auge_Farbe", arr)
    nt.links.new(tex.outputs["Color"], pr.inputs["Base Color"])
    te = nt.nodes.new("ShaderNodeTexImage"); te.image = new_image("Auge_Leuchten", em)
    nt.links.new(te.outputs["Color"], pr.inputs["Emission Color"])
    pr.inputs["Emission Strength"].default_value = 1.0
    return m

def eyes(bvh, mat):
    """Augäpfel: je eine glatte Kuppel, die im Kopf sitzt; die Haut bildet das Lid"""
    parts = []; a, dep, b = EYE_R
    for s in (1, -1):
        hit, n, _, _ = bvh.ray_cast(Vector((EYE[0] * s, H0.y - 2.0, H0.z + EYE[1])), Vector((0, 1, 0)), 6.0)
        d = (n * 0.5 + Vector((0, -1, 0)) * 0.5).normalized()
        e1 = Vector((0, 0, 1)).cross(d).normalized(); e2 = d.cross(e1)
        c = hit - d * (dep - 0.03)
        EYES.append((c, e1, e2, d))
        bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap"); uv = {}
        top = bm.verts.new(c + d * dep); uv[top] = (0.5, 0.5)
        rings = []; nphi = 28
        for th in (10, 22, 35, 48, 61, 74, 87, 100):
            t = math.radians(th); ring = []
            for k in range(nphi):
                ph = k * 2 * math.pi / nphi
                v = bm.verts.new(c + e1 * (a * math.sin(t) * math.cos(ph)) + e2 * (b * math.sin(t) * math.sin(ph)) + d * (dep * math.cos(t)))
                q = min(math.sin(t), 1.0) if th <= 90 else 1.0
                uv[v] = (0.5 + 0.5 * q * math.cos(ph), 0.5 + 0.5 * q * math.sin(ph))
                ring.append(v)
            rings.append(ring)
        for k in range(nphi):
            bm.faces.new([top, rings[0][k], rings[0][(k + 1) % nphi]])
        for r0, r1 in zip(rings, rings[1:]):
            for k in range(nphi):
                bm.faces.new([r0[k], r1[k], r1[(k + 1) % nphi], r0[(k + 1) % nphi]])
        for f in bm.faces:
            for l in f.loops:
                l[uvl].uv = uv[l.vert]
        parts.append(give(finish("Auge%d" % s, bm), mat))
    return parts

def brows(bvh):
    """kurze, kräftige Brauen über den Augen, liegen auf der Stirn"""
    parts = []; a, dep, b = EYE_R
    for (c, e1, e2, d), s in zip(EYES, (1, -1)):
        pts = []
        for u, w in ((-0.55, 1.04), (-0.2, 1.15), (0.2, 1.17), (0.6, 1.1), (0.92, 0.92)):
            o = c + e1 * (u * a * s) + e2 * (w * b) + d * 0.5
            hit, n, _, _ = bvh.ray_cast(o, -d, 2.0)
            pts.append(hit + n * 0.006)
        Q, _ = smooth3([tuple(q) for q in pts], 9, passes=2)
        parts.append(sweep("Braue%d" % s, [Vector(q) for q in Q], [0.016, 0.026, 0.031, 0.032, 0.031, 0.028, 0.023, 0.017, 0.01], segs=8, flat=0.6))
    return parts

def teeth_tongue(bvh):
    """Zwei kleine Fangzähne an der Oberlippe, zwei runde Zähnchen unten nahe den Mundwinkeln, große Zunge.
    Liefert (oben, unten, Zunge)."""
    up, low = [], []
    for s in (1, -1):
        x = 0.118 * s
        yl = bvh.ray_cast(Vector((x, -2.0, LIP + 0.02)), Vector((0, 1, 0)), 6.0)[0].y
        hit = bvh.ray_cast(Vector((x, yl + 0.036, LIP - 0.04)), Vector((0, 0, 1)), 1.0)[0]
        up.append(sweep("Fang%d" % s, [hit + Vector((0, 0, 0.012)), hit + Vector((0, 0, -0.022)), hit + Vector((0, 0.003, -0.05))], [0.025, 0.02, 0.006], segs=8))
        x = 0.16 * s
        zl = float(lip_low(np.float32(x), np.float32(-0.6)))
        yl = bvh.ray_cast(Vector((x, -2.0, zl - 0.02)), Vector((0, 1, 0)), 6.0)[0].y
        hit = bvh.ray_cast(Vector((x, yl + 0.038, LIP - 0.012)), Vector((0, 0, -1)), 1.0)[0]
        low.append(sweep("Zahn%d" % s, [hit + Vector((0, 0, -0.012)), hit + Vector((0, 0, 0.01)), hit + Vector((0, 0, 0.026))], [0.02, 0.017, 0.007], segs=8))
    a = bvh.ray_cast(Vector((0, -0.64, LIP - 0.006)), Vector((0, 0, -1)), 1.0)[0]; b = bvh.ray_cast(Vector((0, -0.44, LIP + 0.01)), Vector((0, 0, -1)), 1.0)[0]
    along = (a - b).normalized(); upv = Vector((1, 0, 0)).cross(along)
    if upv.z < 0:
        upv = -upv
    c = a.lerp(b, 0.62)
    tongue = sphere("Zunge", (0, 0, 0), 1.0, segs=(16, 10))
    for v in tongue.data.vertices:
        sx, sy, sz = v.co
        wide = 0.14 * (1 - 0.3 * max(sy, 0) ** 2)                                   # vorn rund, hinten breit
        v.co = c + Vector((1, 0, 0)) * (sx * wide) + along * (sy * 0.15) + upv * (sz * 0.05 + 0.03 - 0.03 * sx * sx * (sz > 0))
    return up, low, [tongue]

# ---------------------------------------------------------------- Schmuck

COLLAR_C = Vector((0.0, -0.165, 0.9))           # Mitte des Halsreifs
COLLAR_TILT = 12.0                              # Grad: vorn tiefer als hinten
STAR = {}                                       # Mitte und Achsen des Sterns (für die Bemalung)

def collar_frame():
    t = math.radians(COLLAR_TILT)
    return Vector((0, -math.cos(t), -math.sin(t))), Vector((1, 0, 0)), Vector((0, -math.sin(t), math.cos(t)))    # vorn, quer, Achse

def collar(bvh):
    """Goldener Halsreif: breites Band mit zwei runden Wülsten; folgt in jeder Höhe der Haut, liegt also rundum auf.
    Liefert (Teil, Punkt vorn außen auf dem Band)."""
    fwd, ex, axis = collar_frame(); n = 36
    prof = [(-0.012, -0.04), (0.012, -0.048), (0.03, -0.042), (0.034, -0.028), (0.026, -0.018), (0.026, 0.018), (0.034, 0.028),
            (0.03, 0.042), (0.012, 0.048), (-0.012, 0.04)]
    hs = (-0.045, 0.0, 0.045); rad = np.zeros((len(hs), n))
    for k in range(n):
        ph = k * 2 * math.pi / n
        r = fwd * math.cos(ph) + ex * math.sin(ph)
        for i, h in enumerate(hs):
            hit = bvh.ray_cast(COLLAR_C + axis * h + r * 1.2, -r, 2.0)[0]
            rad[i, k] = (hit - COLLAR_C - axis * h).dot(r) if hit is not None else 0.2
    for _ in range(2):
        rad = 0.25 * np.roll(rad, 1, 1) + 0.5 * rad + 0.25 * np.roll(rad, -1, 1)
    bm = bmesh.new(); rings = []
    for k in range(n):
        ph = k * 2 * math.pi / n
        r = fwd * math.cos(ph) + ex * math.sin(ph)
        rings.append([bm.verts.new(COLLAR_C + r * (float(np.interp(h, hs, rad[:, k])) + 0.005 + pr) + axis * h) for pr, h in prof])
    m = len(prof)
    for k in range(n):
        a, b = rings[k], rings[(k + 1) % n]
        for j in range(m):
            bm.faces.new([a[j], a[(j + 1) % m], b[(j + 1) % m], b[j]])
    return finish("Halsreif", bm), COLLAR_C + fwd * (float(rad[1, 0]) + 0.036)

def star_solid(name, center, normal, up, R, r, depth, apex, inset=0.86, back=0.0):
    """Fünfzackiger Stern mit geschliffener Vorderseite (Spitze in der Mitte)"""
    normal = Vector(normal).normalized(); up = Vector(up); up = (up - normal * up.dot(normal)).normalized(); side = up.cross(normal)
    bm = bmesh.new()
    def ring(scale, off):
        vs = []
        for k in range(10):
            a = k * math.pi / 5; rr = (R if k % 2 == 0 else r) * scale
            vs.append(bm.verts.new(Vector(center) + (up * math.cos(a) + side * math.sin(a)) * rr + normal * off))
        return vs
    b = ring(1.0, back); f = ring(inset, depth); top = bm.verts.new(Vector(center) + normal * (depth + apex))
    for k in range(10):
        bm.faces.new([b[k], b[(k + 1) % 10], f[(k + 1) % 10], f[k]])
        bm.faces.new([top, f[k], f[(k + 1) % 10]])
    bm.faces.new(b[::-1])
    o = finish(name, bm, smooth=False)
    return o

def pendant(front, bvh):
    """Sternanhänger: hängt an einer kleinen Öse unten am Halsreif und schwebt frei vor der Brust (liegt nicht auf).
    Liefert (Fassung, Stein, Öse)."""
    fwd, ex, axis = collar_frame()
    eye = front - axis * 0.058 + Vector((0, -0.004, 0))                             # Öse: unter der Unterkante des Bands
    R = 0.122
    low = min((bvh.ray_cast(Vector((0, -2.0, eye.z - dz)), Vector((0, 1, 0)), 6.0)[0] for dz in (0.1, 0.16, 0.22, 0.28)), key=lambda q: q.y)
    low = Vector((0, low.y - 0.05, eye.z - 0.26))                                   # tiefster Punkt: gut vor der Brust
    top = eye + Vector((0, -0.006, -0.016))
    up = (top - low).normalized(); n = Vector((1, 0, 0)).cross(up).normalized()
    if n.y > 0:
        n = -n
    c = top - up * (R + 0.004)
    STAR.update(c=c + n * 0.028, n=n)
    frame = star_solid("Sternfassung", c, n, up, R, R * 0.52, 0.028, 0.006, inset=0.88)
    gem = star_solid("Sternstein", c + n * 0.028, n, up, R * 0.69, R * 0.33, 0.006, 0.028, inset=0.95)
    bm = bmesh.new(); rings = []
    for i in range(14):
        a_ = i * 2 * math.pi / 14; out = Vector((math.cos(a_), 0, math.sin(a_)))
        rings.append([bm.verts.new(eye + out * (0.021 + 0.0075 * math.cos(q)) + Vector((0, 0.0075 * math.sin(q), 0))) for q in [j * 2 * math.pi / 6 for j in range(6)]])
    for i in range(14):
        r0, r1 = rings[i], rings[(i + 1) % 14]
        for j in range(6):
            bm.faces.new([r0[j], r1[j], r1[(j + 1) % 6], r0[(j + 1) % 6]])
    return frame, gem, finish("Sternoese", bm)

TAILGEM = {}                                    # Fußpunkt und Achse des Schwanzsteins (für die Bemalung)

def tail_gem():
    """Schwanzspitze: geschliffener türkiser Kristall (Sockel, Gürtel, Krone, Spitze) in einer goldenen Fassung aus
    sechs Blättern, darunter ein Goldring. Liefert (Stein, Goldteile)."""
    e = Vector(TAIL[-1]); t = (Vector(TAIL[-1]) - Vector(TAIL[-2])).normalized()
    ex = Vector((1, 0, 0)); ez = t.cross(ex).normalized()
    TAILGEM.update(e=e, t=t)
    def ring(bm, along, rx, n, phase=0.0, rz=0.8):
        return [bm.verts.new(e + t * along + ex * (rx * math.cos(phase + k * 2 * math.pi / n)) + ez * (rx * rz * math.sin(phase + k * 2 * math.pi / n))) for k in range(n)]
    def strip(bm, r0, r1):
        """zwei gegeneinander verdrehte Ringe mit Dreiecken verbinden (geschliffene Facetten)"""
        n = len(r0)
        for k in range(n):
            bm.faces.new([r0[k], r0[(k + 1) % n], r1[k]]); bm.faces.new([r0[(k + 1) % n], r1[(k + 1) % n], r1[k]])
    bm = bmesh.new(); n = 6; h = math.pi / n
    base = bm.verts.new(e - t * 0.015); tip = bm.verts.new(e + t * 0.33)
    r1 = ring(bm, 0.055, 0.058, n); r2 = ring(bm, 0.125, 0.09, n, h); r3 = ring(bm, 0.215, 0.052, n, 2 * h)
    for k in range(n):
        bm.faces.new([base, r1[(k + 1) % n], r1[k]]); bm.faces.new([tip, r3[k], r3[(k + 1) % n]])
    strip(bm, r1, r2); strip(bm, r2, r3)
    gem = finish("Schwanzstein", bm, smooth=False)
    # Fassung: Kelch mit sechs spitzen Blättern, die den Stein halten
    bm = bmesh.new(); m = 12
    c0 = ring(bm, -0.035, 0.044, m); c1 = ring(bm, 0.012, 0.064, m)
    c2 = [bm.verts.new(e + t * (0.108 if k % 2 == 0 else 0.05) + (ex * math.cos(k * 2 * math.pi / m) + ez * (0.8 * math.sin(k * 2 * math.pi / m))) * (0.092 if k % 2 == 0 else 0.07))
          for k in range(m)]
    for ra, rb in ((c0, c1), (c1, c2)):
        for k in range(m):
            bm.faces.new([ra[k], ra[(k + 1) % m], rb[(k + 1) % m], rb[k]])
    cup = finish("Schwanzfassung", bm)
    gold = [cup]
    for along, R, r in ((-0.03, 0.05, 0.016), (0.014, 0.068, 0.009)):               # Goldring am Ansatz, schmaler Wulst darüber
        c = e + t * along; bm = bmesh.new(); rings = []
        for i in range(14):
            a_ = i * 2 * math.pi / 14; out = ex * math.cos(a_) + ez * (0.8 * math.sin(a_))
            rings.append([bm.verts.new(c + out * (R + r * math.cos(q)) + t * (r * 1.2 * math.sin(q))) for q in [j * 2 * math.pi / 6 for j in range(6)]])
        for i in range(14):
            r0, r1_ = rings[i], rings[(i + 1) % 14]
            for j in range(6):
                bm.faces.new([r0[j], r1_[j], r1_[(j + 1) % 6], r0[(j + 1) % 6]])
        gold.append(finish("Schwanzring", bm))
    return gem, gold

# ---------------------------------------------------------------- Bemalung

SK_D, SK_M, SK_L = (0.3, 0.11, 0.55), (0.46, 0.2, 0.76), (0.61, 0.34, 0.89)
SK_SHADOW = (0.2, 0.07, 0.4)
PL_D, PL_M, PL_L = (0.4, 0.1, 0.62), (0.62, 0.22, 0.86), (0.84, 0.52, 0.98)
BEL_D, BEL_M, BEL_L = (0.27, 0.62, 0.66), (0.5, 0.84, 0.82), (0.72, 0.96, 0.92)
HORN_D, HORN_M, HORN_L = (0.84, 0.68, 0.44), (0.98, 0.88, 0.66), (1.0, 0.96, 0.84)
MEM_T, MEM_M, MEM_B = (0.43, 0.38, 0.84), (0.3, 0.76, 0.86), (0.5, 0.93, 0.93)
GOLD_D, GOLD_M, GOLD_L = (0.7, 0.42, 0.09), (0.93, 0.69, 0.2), (1.0, 0.9, 0.5)
GEM_D, GEM_M, GEM_L = (0.08, 0.5, 0.64), (0.3, 0.84, 0.84), (0.66, 0.98, 0.94)

def three(a, b, c, t):
    """Verlauf über drei Farben, t = 0..1"""
    return np.where((t < 0.5)[..., None], gradient(a, b, t * 2), gradient(b, c, t * 2 - 1))

def scale_rows(a, b, size):
    """Schuppen in Reihen (a quer, b in Richtung der freien Schuppenränder): jede Reihe ist um eine halbe Schuppe
    versetzt und liegt über der folgenden. Liefert eine weiche Helligkeit (etwa -0.2 … 0.25), keine Umrisslinien."""
    U = a / size; V = b / size; ROW = 0.62; R = 0.74
    j0 = np.floor(V / ROW)
    found = np.zeros(U.shape, bool); dv = np.zeros(U.shape, np.float32); dd = np.ones(U.shape, np.float32)
    for dj in (-2, -1, 0, 1):                                    # obere Reihen zuerst: sie liegen oben
        j = j0 + dj
        off = 0.5 * (np.mod(j, 2))
        i0 = np.round(U - off)
        for di in (0, -1, 1):
            cu = i0 + di + off; cv = j * ROW
            d = np.hypot(U - cu, V - cv) / R
            hit = (d < 1.0) & ~found
            dv = np.where(hit, (V - cv) / R, dv); dd = np.where(hit, d, dd); found |= hit
    shade = 0.26 * smoothstep(-0.45, 0.85, dv) - 0.12
    shade += 0.14 * smoothstep(0.72, 0.93, dd) * smoothstep(0.0, 0.5, dv)        # heller Saum am freien Rand
    shade -= 0.16 * smoothstep(0.93, 1.0, dd)                                     # weicher Schatten in der Fuge
    return np.where(found, shade, -0.1).astype(np.float32)

def scales(P, N, size):
    """Schuppen auf beliebig gekrümmter Haut: aus drei Richtungen aufgetragen und nach der Flächenrichtung gemischt"""
    w = np.abs(N) ** 4; w /= np.maximum(w.sum(-1, keepdims=True), 1e-6)
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    return w[..., 0] * scale_rows(y, -z + 0.3 * y, size) + w[..., 1] * scale_rows(x, -z, size) + w[..., 2] * scale_rows(x, y, size)

def sparkle(P, c, n, size):
    """kleiner Stern mit vier Strahlen auf der Haut um den Punkt c (Flächenrichtung n)"""
    n = Vector(n); t1 = Vector((0, 0, 1)).cross(n)
    t1 = t1.normalized() if t1.length > 0.2 else Vector((1, 0, 0)); t2 = n.cross(t1)
    L = P - f3(c)
    d1 = np.abs(L @ f3(t1)) / size; d2 = np.abs(L @ f3(t2)) / size; d3 = np.abs(L @ f3(n))
    near = d3 < size * 2.0
    ray = np.clip(1 - (np.minimum(d1, d2) * 8 + np.maximum(d1, d2)), 0, 1)
    core = np.clip(1 - np.hypot(d1, d2) * 3.0, 0, 1)
    return np.maximum(ray, core) * near

def wing_stars(a, b):
    """Sternpunkte auf der Flughaut (in Flügelmaßen): kleine weiche Lichter, einzelne mit Strahlen"""
    import monster_aufsatz as ma
    cs = 0.085; out = np.zeros(a.shape, np.float32); big = np.zeros(a.shape, np.float32)
    i0 = np.floor(a / cs).astype(np.int64); j0 = np.floor(b / cs).astype(np.int64); zero = np.zeros_like(i0)
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            i = i0 + di; j = j0 + dj
            h = [ma._hash(i, j, zero, 31 + k) for k in range(4)]
            ca = (i + 0.15 + 0.7 * h[0]) * cs; cb = (j + 0.15 + 0.7 * h[1]) * cs
            r = 0.0035 + 0.0095 * h[3] ** 2
            da = np.abs(a - ca); db = np.abs(b - cb)
            dot = np.exp(-(da * da + db * db) / (r * r)) * (h[2] < 0.52)
            ray = np.clip(1 - (np.minimum(da, db) * 9 + np.maximum(da, db)) / (r * 3.6), 0, 1) * (h[2] < 0.5) * (h[3] > 0.72)
            out = np.maximum(out, np.maximum(dot, ray)); big = np.maximum(big, ray)
    return out, big

def paint(g, line, sparks):
    ao = vertex_ao(g, rays=16, dist=0.28)
    T = texels(g); P, N, cov = T["P"], T["N"], T["cov"]
    AO = texel_values(T, ao)
    TG = np.rint(texel_values(T, part_tags(g))).astype(int)
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    tz = np.clip(N[..., 2] * 0.5 + 0.5, 0, 1)
    occ = np.clip(AO * 2.2, 0, 1) ** 0.85
    sel = lambda t: ((TG == t) & cov).astype(np.float32)
    col = np.zeros(P.shape, np.float32); em = np.zeros(P.shape, np.float32)
    # ---- Haut: Verlauf, Schuppen, Schatten
    hd, jw, bd, wa = sel(T_HEAD), sel(T_JAW), sel(T_BODY), sel(T_WARM)
    skin = three(SK_D, SK_M, SK_L, smoothstep(0.08, 0.95, tz))
    front = smoothstep(-0.08, -0.3, y - H0.y)                                              # Gesicht und Kinn: glatt
    k_sc = bd * smoothstep(0.05, 0.16, z) + hd * (1 - 0.88 * front) + 0.0 * jw
    sc = np.where(hd > 0, scales(P, N, 0.052), scales(P, N, 0.074)) * k_sc
    skin = np.clip(skin * (1 + 0.95 * sc)[..., None] + f3((0.07, 0.05, 0.04)) * np.clip(sc, 0, 1)[..., None], 0, 1)
    skin = mix(skin, SK_L, 0.22 * hd * front * smoothstep(-0.2, 0.25, N[..., 2]))        # Schnauze und Wangen etwas heller
    skin = mix(skin, (0.56, 0.24, 0.8), 0.5 * wa)                                          # Flügelarme: eine Spur röter
    corner = hd * front * smoothstep(0.1, 0.03, np.abs(z - lip_up(x, y))) * smoothstep(MOUTH_W - 0.07, MOUTH_W - 0.02, np.abs(x))
    skin = mix(skin, SK_SHADOW, 0.55 * occ * (1 - 0.85 * corner))                 # an den Mundwinkeln kein dunkler Strich
    m_skin = np.clip(hd + jw + bd + wa, 0, 1)
    col = col * (1 - m_skin[..., None]) + skin * m_skin[..., None]
    # ---- helle Unterseite mit Schilden
    bel, frac, edge = belly_fields(P, N, line)
    bel = bel * bd
    bcol = three(BEL_L, BEL_M, (0.3, 0.66, 0.7), frac ** 1.1)
    bcol = mix(bcol, (0.1, 0.38, 0.5), np.clip(smoothstep(0.82, 0.93, frac) * smoothstep(1.0, 0.985, frac), 0, 1))               # Fuge
    bcol = mix(bcol, (0.16, 0.46, 0.56), 0.7 * smoothstep(0.86, 0.95, edge))          # schmale dunklere Kante statt eines breiten Verlaufs
    bcol = bcol * (0.86 + 0.14 * tz)[..., None]
    bcol = mix(bcol, (0.16, 0.36, 0.5), 0.45 * occ * smoothstep(0.62, 0.5, z))       # auf der Brust kein Schatten vom Anhänger
    col = col * (1 - bel[..., None]) + bcol * bel[..., None]
    # ---- Maul: Gaumen und Mundboden, Nasenlöcher, Lidrand
    inm = (y < YH + 0.03) * smoothstep(0.52, 0.74, occ)                             # nur verdeckte Flächen: die Lippen bleiben violett
    cav = hd * inm * (z < palate(x, y) + 0.03) * (z > lip_low(x, y) - 0.03) * smoothstep(0.004, 0.02, lip_gap(x, y))
    deep = smoothstep(-0.68, -0.4, y)                                               # nach hinten dunkler
    up_side = smoothstep(0.2, -0.3, N[..., 2])                                      # Gaumen dunkler als der Mundboden
    mcol = gradient((0.66, 0.18, 0.34), (0.5, 0.11, 0.27), up_side)
    mcol = mcol * (1 - deep[..., None]) + gradient((0.4, 0.08, 0.22), (0.3, 0.05, 0.18), up_side) * deep[..., None]
    col = col * (1 - cav[..., None]) + mcol * cav[..., None]
    em += mcol * (0.3 * cav)[..., None]                                             # Maulinneres bleibt auch im Schatten warm
    for c, n in sparks["nose"]:
        col = mix(col, (0.2, 0.07, 0.36), hd * 0.88 * np.exp(-(np.linalg.norm(P - f3(c), axis=-1) / 0.015) ** 2))
    a, dep, b = EYE_R
    for c, e1, e2, d in EYES:
        L = P - f3(c)
        q = (L @ f3(e1) / a) ** 2 + (L @ f3(e2) / b) ** 2 + (L @ f3(d) / dep) ** 2
        rim = smoothstep(1.55, 1.02, q) * hd * (0.55 + 0.45 * smoothstep(-0.3, 0.6, L @ f3(e2) / b))
        col = mix(col, (0.17, 0.06, 0.34), 0.85 * rim)
    # ---- Kamm, Rückenplatten, Kragen: kräftiges Purpur, zur Spitze heller
    pl = sel(T_PLATE)
    pc = three(PL_D, PL_M, PL_L, smoothstep(0.1, 0.95, 0.6 * tz + 0.4 * (1 - occ)))
    pc = mix(pc, PL_D, 0.55 * occ)
    col = col * (1 - pl[..., None]) + pc * pl[..., None]
    # ---- Hörner und Krallen: Elfenbein mit Verlauf, Hörner mit Ringen
    hm = (TG == T_HORN) & cov
    if hm.any():
        Ph = P[hm]; Q = np.array([tuple(q) for q in horn_pts(1)], np.float32)
        Pa = np.stack([np.abs(Ph[:, 0]), Ph[:, 1], Ph[:, 2]], 1)
        d2 = ((Pa[:, None, :] - Q[None, :, :]) ** 2).sum(-1)
        i = np.argmin(d2, 1); j = np.clip(i + np.where(np.take_along_axis(d2, np.clip(i + 1, 0, HORN_N - 1)[:, None], 1)[:, 0] <
                                                         np.take_along_axis(d2, np.clip(i - 1, 0, HORN_N - 1)[:, None], 1)[:, 0], 1, -1), 0, HORN_N - 1)
        qa, qb = Q[i], Q[j]; ab = qb - qa
        f = np.clip(((Pa - qa) * ab).sum(1) / np.maximum((ab * ab).sum(1), 1e-9), 0, 1)
        t = (i + f * (j - i)) / (HORN_N - 1)
        hc = three(HORN_D, HORN_M, HORN_L, np.clip(0.12 + 0.95 * t, 0, 1))
        hc = hc * (0.8 + 0.2 * tz[hm])[:, None]
        ring = np.cos(t * 2 * np.pi * 4.2 + 0.6)
        hc = mix(hc, (0.66, 0.44, 0.22), 0.5 * smoothstep(-0.55, -1.0, ring) * (1 - t))
        hc = mix(hc, (0.5, 0.3, 0.2), 0.5 * occ[hm])
        col[hm] = hc
    cl = sel(T_CLAW)
    cc = three(HORN_D, HORN_M, HORN_L, smoothstep(0.1, 0.9, tz))
    col = col * (1 - cl[..., None]) + mix(cc, (0.5, 0.3, 0.2), 0.4 * occ) * cl[..., None]
    # ---- Flughaut: oben blauviolett, unten helles Türkis, Sternennebel und Sternpunkte
    mm = (TG == T_MEM) & cov
    if mm.any():
        Pm = P[mm]
        A = np.array([WING_A.x, WING_A.y], np.float32)
        wa_ = (np.abs(Pm[:, 0]) - WING_ROOT.x) * A[0] + (Pm[:, 1] - WING_ROOT.y) * A[1]; wb = Pm[:, 2] - WING_ROOT.z
        mc = three(MEM_B, MEM_M, MEM_T, smoothstep(-0.42, 0.36, wb + 0.12 * wa_))
        Pabs = np.stack([np.abs(Pm[:, 0]), Pm[:, 1], Pm[:, 2]], 1)
        neb = fbm3(Pabs, 4.5, 5, 4); neb2 = fbm3(Pabs + 7.3, 3.2, 23, 3)
        mc = mix(mc, (0.8, 0.5, 0.95), 0.5 * smoothstep(0.5, 0.72, neb))
        mc = mix(mc, (0.24, 0.3, 0.78), 0.4 * smoothstep(0.52, 0.75, neb2))
        dbone = np.full(len(Pm), 9.0, np.float32)
        for i in range(3):
            dbone = np.minimum(dbone, seg_dist(Pabs, [tuple(wing_pt(q.x, q.y)) for q in [finger_curve(i, t) for t in np.linspace(0, 1, 9)]]))
        dbone = np.minimum(dbone, seg_dist(Pabs, [tuple(wing_pt(q.x, q.y)) for q in [arm_curve(t) for t in np.linspace(0, 1, 7)]]))
        mc = mix(mc, (0.5, 0.3, 0.82), 0.6 * smoothstep(0.075, 0.02, dbone))
        st, big = wing_stars(wa_, wb)
        st = st * smoothstep(0.02, 0.05, dbone)
        mc = mix(mc, (0.95, 1.0, 1.0), st)
        col[mm] = mc
        em[mm] = f3((0.75, 0.95, 1.0)) * (0.9 * st)[:, None] + mc * 0.12
    # ---- Brauen, Zunge, Zähne
    br = sel(T_BROW)
    col = col * (1 - br[..., None]) + gradient((0.11, 0.05, 0.2), (0.27, 0.15, 0.42), tz) * br[..., None]
    tg = sel(T_TONGUE)
    tc = gradient((0.78, 0.25, 0.4), (1.0, 0.5, 0.58), smoothstep(0.0, 0.8, N[..., 2]))
    tc = mix(tc, (0.8, 0.27, 0.42), 0.45 * np.exp(-(x / 0.009) ** 2) * (y > -0.66))
    tc = mix(tc, (0.5, 0.11, 0.28), 0.5 * smoothstep(-0.52, -0.36, y))
    col = col * (1 - tg[..., None]) + tc * tg[..., None]
    em += tc * (0.3 * tg)[..., None]
    th = sel(T_TOOTH)
    col = col * (1 - th[..., None]) + mix(np.zeros(P.shape, np.float32) + f3((1.0, 0.98, 0.92)), (0.86, 0.74, 0.6), 0.6 * occ) * th[..., None]
    # ---- Gold: Verlauf, Gravur im Band des Halsreifs
    go = sel(T_GOLD)
    gc = three(GOLD_D, GOLD_M, GOLD_L, smoothstep(0.05, 0.95, 0.75 * tz + 0.25 * np.clip(-N[..., 1], 0, 1)))
    fwd, ex, axis = collar_frame()
    L = P - f3(COLLAR_C); hh = L @ f3(axis); ph = np.arctan2(L @ f3(ex), L @ f3(fwd))
    rad = L - hh[..., None] * f3(axis); rad /= np.maximum(np.linalg.norm(rad, axis=-1, keepdims=True), 1e-6)
    band = smoothstep(0.02, 0.014, np.abs(hh)) * smoothstep(0.5, 0.8, (N * rad).sum(-1)) * (np.abs(hh) < 0.03)
    wave = smoothstep(0.0052, 0.0028, np.abs(hh - 0.0085 * np.sin(ph * 16))) + smoothstep(0.004, 0.002, np.abs(np.abs(hh) - 0.0145))
    gc = mix(gc, (0.56, 0.31, 0.06), 0.8 * np.clip(wave, 0, 1) * band)
    gc = mix(gc, (0.45, 0.24, 0.08), 0.45 * occ)
    col = col * (1 - go[..., None]) + gc * go[..., None]
    # ---- Steine: geschliffenes Türkis, Stern mit goldenem Herz
    ge = sel(T_GEM)
    lgt = np.clip(N @ f3(Vector((-0.35, -0.55, 0.76)).normalized()), -1, 1) * 0.5 + 0.5
    cg = three(GEM_D, GEM_M, GEM_L, smoothstep(0.2, 1.0, lgt))
    ds = np.linalg.norm(P - f3(STAR["c"]), axis=-1)
    cg = mix(cg, (1.0, 0.93, 0.42), 0.85 * smoothstep(0.07, 0.01, ds))
    col = col * (1 - ge[..., None]) + cg * ge[..., None]
    ta = np.clip((P - f3(TAILGEM["e"])) @ f3(TAILGEM["t"]) / 0.33, 0, 1)            # Schwanzstein: innen tief, zur Spitze hin hell
    tg_ = ge * (ds > 0.4)
    cg = mix(cg, (0.04, 0.36, 0.6), 0.45 * tg_ * (1 - ta))
    cg = mix(cg, (0.85, 1.0, 0.98), 0.6 * tg_ * ta ** 1.6)
    col = col * (1 - tg_[..., None]) + cg * tg_[..., None]
    em += cg * (0.22 * ge + 0.3 * tg_)[..., None]
    # ---- Glitzersterne auf der Haut
    for c, n, size in sparks["skin"]:
        s_ = sparkle(P, c, n, size) * m_skin * (1 - bel)
        col = mix(col, (0.86, 1.0, 1.0), s_)
        em += f3((0.6, 0.95, 1.0)) * (0.9 * s_)[..., None]
    finish_paint(T, col, em, strength=1.0)

# ---------------------------------------------------------------- Gewichte

TAIL_BONES = ("Tail", "Tail2", "Tail3", "Tail4", "Tail5")

def tail_bone(y):
    """Knochen des Schwanzes an der Stelle y (für starre Teile)"""
    return TAIL_BONES[sum(1 for j in range(1, 5) if y > TAIL[j][1])]

def body_weights(o):
    gr = {n: o.vertex_groups.new(name=n) for n in ("Root", "Body") + TAIL_BONES}
    for v in o.data.vertices:
        p = v.co
        tl = ramp(p.y, 0.42, 0.64) * (1 - (1 - ramp(p.y, 0.5, 0.6)) * ramp(abs(p.x), 0.15, 0.24))
        r = [1.0] + [ramp(p.y, TAIL[j][1] - 0.075, TAIL[j][1] + 0.075) for j in range(1, 5)] + [0.0]
        leg = 1 - ramp(p.z, 0.1, 0.42)
        w = {"Root": (1 - tl) * leg, "Body": (1 - tl) * (1 - leg)}
        for i, n in enumerate(TAIL_BONES):
            w[n] = tl * (r[i] - r[i + 1])
        for n, x in w.items():
            if x > 0.002:
                gr[n].add([v.index], x, 'REPLACE')

def wing_weights(o, side):
    """Arm und innere Flughaut am Flügelknochen, Finger und äußere Haut weich an der Flügelspitze"""
    nm = ".L" if side > 0 else ".R"
    gw = o.vertex_groups.new(name="Wing" + nm); gt = o.vertex_groups.new(name="WingTip" + nm)
    ang_f3 = math.degrees(math.atan2(FINGERS[2][1][1] - WRIST[1], FINGERS[2][1][0] - WRIST[0]))        # innerer Finger
    ang_arm = math.degrees(math.atan2(-WRIST[1], -WRIST[0]))
    for v in o.data.vertices:
        p = Vector((v.co.x * side, v.co.y, v.co.z)) - WING_ROOT
        a = p.dot(WING_A) - WRIST[0]; b = p.dot(WING_B) - WRIST[1]
        d = math.hypot(a, b); ang = math.degrees(math.atan2(b, a))
        tip = ramp(d, 0.03, 0.2) * (1 - ramp(-ang, -ang_f3 + 6, -ang_arm - 4)) if ang < 30 else 0.0
        if tip > 0.002:
            gt.add([v.index], tip, 'REPLACE')
        if tip < 0.998:
            gw.add([v.index], 1 - tip, 'REPLACE')

# ---------------------------------------------------------------- Skelett und Bewegungen

FPS = 30

def update():
    bpy.context.view_layer.update()

def new_armature(bones):
    """bones: [(name, head, tail, parent)] in Weltkoordinaten"""
    data = bpy.data.armatures.new("Armature"); arm = bpy.data.objects.new("Armature", data)
    bpy.context.scene.collection.objects.link(arm); bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT'); eb = {}
    for name, h, t, parent in bones:
        bn = data.edit_bones.new(name); bn.head, bn.tail = Vector(h), Vector(t)
        if parent:
            bn.parent = eb[parent]
        eb[name] = bn
    bpy.ops.object.mode_set(mode='OBJECT')
    return arm

def reset_pose(arm):
    for pb in arm.pose.bones:
        pb.rotation_mode = 'QUATERNION'; pb.rotation_quaternion = Quaternion(); pb.location = (0, 0, 0)
    update()

def rot_world(arm, name, axis, deg):
    """Knochen um eine Weltachse drehen (wirkt in jeder Haltung gleich)"""
    bn = arm.data.bones[name]
    local = (bn.matrix_local.to_3x3().inverted() @ Vector(axis)).normalized()
    pb = arm.pose.bones[name]
    pb.rotation_quaternion = Quaternion(local, math.radians(deg)) @ pb.rotation_quaternion

def move_world(arm, name, vec):
    arm.pose.bones[name].location = arm.data.bones[name].matrix_local.to_3x3().inverted() @ Vector(vec)

def make_actions(arm, clips):
    arm.animation_data_create()
    for name, frames in clips:
        act = bpy.data.actions.new(name); act.use_fake_user = True
        arm.animation_data.action = act
        for f, fn in frames:
            fn(); update()
            for pb in arm.pose.bones:
                pb.keyframe_insert("rotation_quaternion", frame=f); pb.keyframe_insert("location", frame=f)
    arm.animation_data.action = None
    reset_pose(arm)

def add_muzzle(arm, bone, world_pos):
    """Muzzle starr an einen Knochen hängen: Blender +Y des Knotens zeigt nach vorn (Welt -Y), im glTF wird das -Z"""
    m = bpy.data.objects.new("Muzzle", None); bpy.context.scene.collection.objects.link(m)
    m.parent = arm; m.parent_type = 'BONE'; m.parent_bone = bone
    pb = arm.pose.bones[bone]
    tail = arm.matrix_world @ pb.matrix @ Matrix.Translation((0, pb.bone.length, 0))
    m.matrix_parent_inverse = Matrix.Identity(4)
    fwd = Vector((0, -1, 0)); up = Vector((0, 0, 1))
    rot = Matrix((fwd.cross(up), fwd, up)).transposed()
    m.matrix_basis = tail.inverted() @ (Matrix.Translation(world_pos) @ rot.to_4x4())
    update()
    return m

MUZZLE = Vector((0.0, -0.76, LIP - 0.06))            # Sternenatem: zwischen den geöffneten Kiefern, vorn

def skeleton():
    wr = wing_pt(WRIST[0], WRIST[1]); tip = wing_pt(*FINGERS[0][1])
    mir = lambda p: Vector((-p.x, p.y, p.z))
    t5 = Vector(TAIL[5]) + (Vector(TAIL[5]) - Vector(TAIL[4])).normalized() * 0.2
    return new_armature([
        ("Root", (0, 0, 0), (0, 0, 0.4), None),
        ("Body", (0, 0.1, 0.55), (0, -0.12, 0.9), "Root"),
        ("Head", (0, -0.2, 1.04), (0, -0.22, 1.7), "Body"),
        ("Jaw", tuple(HINGE), (0, -0.68, 1.12), "Head"),
        ("Wing.L", tuple(WING_ROOT), tuple(wr), "Body"), ("WingTip.L", tuple(wr), tuple(tip), "Wing.L"),
        ("Wing.R", tuple(mir(WING_ROOT)), tuple(mir(wr)), "Body"), ("WingTip.R", tuple(mir(wr)), tuple(mir(tip)), "Wing.R"),
        ("Tail", TAIL[0], TAIL[1], "Root"), ("Tail2", TAIL[1], TAIL[2], "Tail"), ("Tail3", TAIL[2], TAIL[3], "Tail2"),
        ("Tail4", TAIL[3], TAIL[4], "Tail3"), ("Tail5", TAIL[4], tuple(t5), "Tail4"),
    ])

def animate(arm):
    nl = WING_N; nr = Vector((-WING_N.x, WING_N.y, WING_N.z)) * -1.0        # Flügel heben: Drehung um die Flächennormale

    def pose(flap=0.0, fold=0.0, sweep=0.0, pitch=0.0, fwd=0.0, jaw=0.0, yaw=(0, 0, 0, 0, 0), lift=(0, 0, 0, 0, 0), hop=0.0,
             bob=0.0, lean=0.0, turn=0.0, up=0.0):
        """yaw, lift: Drehung je Schwanzknochen (seitlich, nach oben), vom Ansatz zur Spitze"""
        reset_pose(arm)
        for nm, n, sg in ((".L", nl, 1), (".R", nr, -1)):
            rot_world(arm, "Wing" + nm, (0, 0, 1), sweep * sg)
            rot_world(arm, "Wing" + nm, n, flap)
            rot_world(arm, "WingTip" + nm, n, fold)
        rot_world(arm, "Head", (1, 0, 0), -pitch); rot_world(arm, "Head", (0, 0, 1), turn)
        move_world(arm, "Head", (0, -fwd, up))
        rot_world(arm, "Jaw", (1, 0, 0), jaw)
        for nm, a_, l_ in zip(TAIL_BONES, yaw, lift):
            rot_world(arm, nm, (0, 0, 1), a_); rot_world(arm, nm, (1, 0, 0), l_)
        rot_world(arm, "Body", (1, 0, 0), -lean)
        move_world(arm, "Body", (0, 0, bob)); move_world(arm, "Root", (0, 0, hop))

    S = lambda t, ph=0.0: math.sin((t - ph) * 2 * math.pi)
    wave = lambda t, amp, lag=0.07: tuple(amp * (0.7 + 0.12 * i) * S(t, lag * i) for i in range(5))
    add = lambda u, v: tuple(a_ + b_ for a_, b_ in zip(u, v))
    CURL = (17, 22, 24, 20, 14)                 # Zielhaltung: Schwanz nach oben eingerollt, der Stein steht hinter dem Rücken
    SIDE = (7, 9, 9, 7, 5)                      # und leicht zur Seite, damit er den Rücken nicht verdeckt
    idle = [(i * 8, (lambda t=i / 8.0: pose(flap=5 + 7 * S(t), fold=5 * S(t, 0.12), pitch=1.5 + 2.2 * S(t, 0.05), jaw=1.2 + 1.2 * S(t, 0.3),
                                            yaw=wave(t, 8), lift=add((5, 8, 10, 10, 8), wave(t, 2.5, 0.05)),
                                            bob=0.012 * S(t, 0.02), turn=1.5 * S(t * 0.5)))) for i in range(9)]
    aim = dict(flap=12, fold=10, sweep=-7, pitch=9, fwd=0.05, up=0.025, jaw=9, yaw=SIDE, lift=CURL, lean=1.5)
    # Schuss: der Schwanz peitscht mit (rollt sich enger ein und schlägt zur anderen Seite), dann zurück
    shoot = [(0, lambda: pose(**aim)),
             (3, lambda: pose(flap=24, fold=20, sweep=-2, pitch=11, fwd=0.11, up=0.035, jaw=16, lean=3.5, bob=-0.012,
                              yaw=(-5, -9, -13, -15, -15), lift=(22, 27, 29, 25, 19))),
             (7, lambda: pose(flap=8, fold=5, sweep=-8, pitch=9.5, fwd=0.035, up=0.022, jaw=7, lean=0.8,
                              yaw=(12, 16, 16, 12, 9), lift=(14, 19, 21, 17, 11))),
             (12, lambda: pose(**aim))]
    win = [(i * 6, (lambda t=i / 8.0: pose(flap=10 + 18 * S(t * 2), fold=6 + 12 * S(t * 2, 0.1), sweep=8, pitch=9 + 3 * S(t * 2), up=0.02, jaw=5 + 4 * S(t * 2),
                                           yaw=wave(t, 15, 0.08), lift=(14, 18, 20, 16, 12),
                                           hop=0.13 * abs(S(t)), lean=2 + 2 * S(t * 2), turn=4 * S(t)))) for i in range(9)]
    make_actions(arm, [("Idle", idle), ("Shoot", shoot), ("Victory", win)])

def clearance(arm, g):
    """Prüfschritt C: kleinster Abstand zwischen Teilen, die sich nicht berühren dürfen, über alle Bewegungen, und wie
    viele Punkte dabei im anderen Teil stecken (Strahl nach außen trifft dessen Oberfläche ungerade oft)."""
    grp = np.zeros(len(g.data.vertices), np.float32); g.data.attributes["gruppe"].data.foreach_get("value", grp)
    grp = np.rint(grp).astype(int)
    pairs = [("Flügel – Kopf", (G_WL, G_WR), (G_HEAD,)), ("Flügel – Flügel", (G_WL,), (G_WR,)),
             ("Kopf – Halsreif", (G_HEAD,), (G_NECK,)), ("Flügel – Schwanz", (G_WL, G_WR), (G_TAIL,))]
    polys = [tuple(p.vertices) for p in g.data.polygons]
    sets = []
    for name, A, Bg in pairs:
        tris = [p for p in polys if grp[p[0]] in Bg]
        idx = sorted({i for p in tris for i in p}); remap = {i: k for k, i in enumerate(idx)}
        sets.append((name, np.where(np.isin(grp, A))[0], idx, [tuple(remap[i] for i in p) for p in tris]))
    worst = {}; ray = Vector((0.31, 0.52, 0.8)).normalized()
    arm.animation_data_create()
    for act in bpy.data.actions:
        arm.animation_data.action = act
        f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
        for f in range(f0, f1 + 1, 2 if f1 - f0 > 20 else 1):
            bpy.context.scene.frame_set(f)
            dg = bpy.context.evaluated_depsgraph_get(); me = g.evaluated_get(dg).data
            co = [v.co.copy() for v in me.vertices]
            for name, A, idx, tris in sets:
                bvh = BVHTree.FromPolygons([co[i] for i in idx], tris)
                best = 9.0; inside = 0
                for i in A:
                    loc, nrm, _, dist = bvh.find_nearest(co[i], 0.25)
                    if loc is None:
                        continue
                    best = min(best, dist)
                    if dist < 0.12:
                        o = co[i]; hits = 0
                        while hits < 20:
                            h = bvh.ray_cast(o, ray, 5.0)[0]
                            if h is None:
                                break
                            hits += 1; o = h + ray * 1e-4
                        inside += hits % 2
                key = (name, act.name)
                if (inside, -best) > (worst.get(key, (0, -9.0, 0))[0], worst.get(key, (0, -9.0, 0))[1]):
                    worst[key] = (inside, -best, f)
    arm.animation_data.action = None; reset_pose(arm); bpy.context.scene.frame_set(0)
    for (name, an), (ins, d, f) in sorted(worst.items()):
        print("ABSTAND %-18s %-8s %6.3f, %d Punkte stecken drin (Bild %d)" % (name, an, -d, ins, f))

# ---------------------------------------------------------------- Ablauf

def grey(name, col):
    return look(name, col, rough=0.6)

def build(out, form=False):
    SIZE = int(os.environ.get("TEXTUR", "2048"))
    body = body_shape()
    line = belly_line(BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get()))
    belly_bulge(body, line)
    to_tris(body, 5000); head = to_tris(head_shape(), 4400)
    dg = bpy.context.evaluated_depsgraph_get()
    bvh_b = BVHTree.FromObject(body, dg); bvh_h = BVHTree.FromObject(head, dg)
    mark(body, T_BODY, G_BODY); body_weights(body)
    mark(head, T_HEAD, G_HEAD); head_weights(head)
    parts = [body, head]
    parts += [mark(o, T_PLATE, G_HEAD, "Head") for o in head_plates()] + [mark(horn(s), T_HORN, G_HEAD, "Head") for s in (1, -1)]
    for o in spine_plates(bvh_b):
        yy = sum(v.co.y for v in o.data.vertices) / len(o.data.vertices)
        bone = "Body" if yy < 0.5 else tail_bone(yy)
        parts.append(mark(o, T_PLATE, G_BODY if bone == "Body" else G_TAIL, bone))
    parts += [mark(o, T_CLAW, G_BODY, "Root") for o in claws()]
    for s in (1, -1):
        bones, skin = wing(s)
        for o in bones[:-1] + [skin]:
            mark(o, T_MEM if o is skin else T_WARM, G_WL if s > 0 else G_WR); wing_weights(o, s)
        parts += bones[:-1] + [skin, mark(bones[-1], T_WARM, G_BODY, "Body")]
    eye_m = eye_material()
    eye_parts = [mark(o, 20, G_HEAD, "Head") for o in eyes(bvh_h, eye_m)]
    parts += [mark(o, T_BROW, G_HEAD, "Head") for o in brows(bvh_h)]
    up, low, tongue = teeth_tongue(bvh_h)
    parts += [mark(o, T_TOOTH, G_HEAD, "Head") for o in up] + [mark(o, T_TOOTH, G_JAW, "Jaw") for o in low]
    parts += [mark(o, T_TONGUE, G_JAW, "Jaw") for o in tongue]
    ring, front = collar(bvh_b)
    frame, gem, bail = pendant(front, bvh_b)
    tgem, tgold = tail_gem()
    parts += [mark(ring, T_GOLD, G_NECK, "Body"), mark(bail, T_GOLD, G_NECK, "Body"), frame, gem, tgem]
    parts += [mark(o, T_GOLD, G_TAIL, "Tail5") for o in tgold]
    for o, t, grp, bone in ((frame, T_GOLD, G_NECK, "Body"), (gem, T_GEM, G_NECK, "Body"), (tgem, T_GEM, G_TAIL, "Tail5")):
        md = o.modifiers.new("Kanten", 'EDGE_SPLIT'); md.split_angle = math.radians(18); apply_mod(o, md)
        mark(o, t, grp, bone)
    # Glitzersterne und Nasenlöcher: Stellen auf der Haut
    sparks = {"skin": [], "nose": []}
    for s in (1, -1):
        hit, n, _, _ = bvh_h.ray_cast(Vector((NOSTRIL[0] * s, H0.y - 2.0, H0.z + NOSTRIL[1])), Vector((0, 1, 0)), 6.0)
        sparks["nose"].append((tuple(hit), tuple(n)))
        for bv, o, d, size in ((bvh_h, (0.9 * s, -0.42, 1.27), (-1 * s, 0.25, 0), 0.04), (bvh_h, (0.9 * s, -0.3, 1.2), (-1 * s, 0.1, 0), 0.024),
                               (bvh_b, (0.9 * s, 0.18, 0.56), (-1 * s, 0, 0), 0.045), (bvh_b, (0.9 * s, 0.34, 0.4), (-1 * s, 0, 0), 0.026),
                               (bvh_b, (0.9 * s, -0.2, 0.66), (-1 * s, 0, 0), 0.034), (bvh_b, (0.9 * s, -0.32, 0.36), (-1 * s, 0, 0), 0.024),
                               (bvh_b, (0.5 * s, 0.82, 0.9), (-0.8 * s, 0, -1), 0.026), (bvh_b, (0.16 * s, 0.02, 2.0), (0, 0, -1), 0.03)):
            hit, n, _, _ = bv.ray_cast(Vector(o), Vector(d).normalized(), 6.0)
            if hit is not None:
                sparks["skin"].append((tuple(hit), tuple(n), size))
    if form:
        M = {T_PLATE: grey("Platte", (0.4, 0.4, 0.46)), T_HORN: grey("Horn", (0.8, 0.78, 0.7)), T_MEM: grey("Flughaut", (0.62, 0.7, 0.72)),
             T_GOLD: grey("Gold", (0.75, 0.68, 0.45)), T_GEM: grey("Stein", (0.6, 0.8, 0.8)), T_BROW: grey("Braue", (0.2, 0.2, 0.25))}
        hautm = grey("Haut", (0.55, 0.55, 0.58))
        for o in parts:
            t = int(round(o.data.attributes["teil"].data[0].value)); give(o, M.get(T_HORN if t in (T_CLAW, T_TOOTH) else t, hautm))
    g = join_parts(parts, "Fuenkchen")
    for p in g.data.polygons:
        p.use_smooth = True
    if not form:
        g.data.materials.clear(); g.data.materials.append(image_material("Fuenkchen", SIZE, color=(0.5, 0.25, 0.79), rough=0.42))
        smart_uv(g, margin=0.004)
        paint(g, line, sparks)
        skin_m = g.data.materials[0]
        gold_m = skin_m.copy(); gold_m.name = "Gold"
        pr = gold_m.node_tree.nodes["Principled BSDF"]; pr.inputs["Metallic"].default_value = 0.85; pr.inputs["Roughness"].default_value = 0.3
        gem_m = skin_m.copy(); gem_m.name = "Kristall"; gem_m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.12
        g.data.materials.append(gold_m); g.data.materials.append(gem_m)
        tags = np.rint(part_tags(g)).astype(int)
        for p in g.data.polygons:
            t = tags[p.vertices[0]]
            p.material_index = 1 if t == T_GOLD else 2 if t == T_GEM else 0
    g = join_parts([g] + eye_parts, "Fuenkchen")
    # Skelett
    bpy.context.scene.render.fps = FPS
    arm = skeleton()
    g.parent = arm
    md = g.modifiers.new("Armature", 'ARMATURE'); md.object = arm
    reset_pose(arm)
    animate(arm)
    add_muzzle(arm, "Head", MUZZLE)
    clearance(arm, g)
    co = np.array([tuple(v.co) for v in g.data.vertices])
    tris = sum(len(p.vertices) - 2 for p in g.data.polygons)
    print("MASSE x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (co[:, 0].min(), co[:, 0].max(), co[:, 1].min(), co[:, 1].max(), co[:, 2].min(), co[:, 2].max()))
    print("DREIECKE", tris, "TEXTUREN", sorted({tuple(i.size) for i in bpy.data.images}), "MATERIALIEN", [m.name for m in g.data.materials],
          "KNOCHEN", len(arm.data.bones), "AKTIONEN", [(a.name, int(a.frame_range[1])) for a in bpy.data.actions])
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS',
                              export_yup=True, export_apply=False, export_force_sampling=True,
                              export_image_format='JPEG', export_jpeg_quality=90)

if __name__ == "__main__":
    bpy.ops.wm.read_factory_settings(use_empty=True)
    build(OUT, form=(STUFE == "form"))
    print("FERTIG", OUT)
