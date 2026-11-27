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
HINGE = Vector((0.0, -0.2, 1.165))              # Kiefergelenk (Drehachse quer)
JAW_OPEN = 9.0                                 # Grad: so weit steht das Maul in der Ruhehaltung offen (Lächeln)
NECK = (Vector((0.0, -0.14, 0.82)), Vector((0.0, -0.2, 1.1)))
TAIL = [(0.0, 0.4, 0.56), (0.0, 0.62, 0.49), (0.0, 0.84, 0.41), (0.0, 1.04, 0.35), (0.0, 1.22, 0.31), (0.0, 1.38, 0.3)]
TAIL_R = [0.215, 0.185, 0.15, 0.115, 0.082, 0.055]
FRONT = (0.235, -0.3)                           # Vorderbein: x, y am Boden
HIND = (0.285, 0.3)                             # Hinterbein
WING_ROOT = Vector((0.15, 0.2, 0.86))           # Flügelansatz auf dem Rücken, hinter den Schultern
WING_A = Vector((0.74, 0.67, 0.0)).normalized() # Spannrichtung: nach außen und hinten
WING_B = Vector((0.0, 0.0, 1.0))                # nach oben
WING_N = WING_A.cross(WING_B)                   # Flächennormale (zeigt nach vorn außen)
WRIST = (0.3, 0.37)                             # Handgelenk in Flügelmaßen (entlang A, entlang B)
FINGERS = [((0.72, 0.36), (1.02, -0.06)),       # je Finger: Stützpunkt, Spitze (Flügelmaße)
           ((0.58, 0.02), (0.66, -0.42)),
           ((0.3, 0.0), (0.27, -0.36))]

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

def leaf(name, base, up, along, height, length, thick, lean=0.0, sink=0.35, segs=(12, 8), petal=False):
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
    return sweep(name, pts, [r, r * 0.92, r * 0.72, r * 0.48, r * 0.26], segs=10)

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

def head_shape():
    R = mb_family("Kopf")
    mb_ell(R, H0, (0.395, 0.33, 0.33))                                              # Schädel
    for s in (1, -1):
        mb_ell(R, H0 + Vector((0.2 * s, -0.13, -0.15)), (0.2, 0.2, 0.165))          # Wangen
        mb_ell(R, H0 + Vector((0.1 * s, -0.46, -0.035)), (0.078, 0.075, 0.052))     # Nasenhöcker
    mb_ell(R, H0 + Vector((0, -0.34, -0.118)), (0.25, 0.215, 0.125))                # Schnauze, sitzt im Schädel
    mb_ell(R, H0 + Vector((0, -0.37, -0.262)), (0.17, 0.17, 0.045), neg=True)       # Gaumen: flache Mulde
    g = mb_to_mesh(R)
    finish_skin(g, 0.012, 1.0, smooth_it=6)
    return g

def jaw_shape():
    """Unterkiefer, geschlossen gebaut und dann um das Gelenk aufgeklappt"""
    R = mb_family("Kiefer")
    mb_ell(R, (0, -0.4, 1.078), (0.2, 0.245, 0.092))                                # Kinn: sitzt unter der Schnauze, etwas kürzer
    mb_ell(R, (0, -0.26, 1.09), (0.22, 0.15, 0.095))                                # Kinnbacke hinten, steckt im Kopf
    mb_ell(R, (0, -0.42, 1.2), (0.13, 0.165, 0.045), neg=True)                      # Mundboden: Mulde für die Zunge
    g = mb_to_mesh(R)
    finish_skin(g, 0.011, 1.0, smooth_it=6)
    g.data.transform(Matrix.Translation(HINGE) @ Matrix.Rotation(math.radians(JAW_OPEN), 4, 'X') @ Matrix.Translation(-HINGE))
    g.data.update()
    return g

def horn(side):
    p0 = H0 + Vector((0.225 * side, 0.02, 0.22)); p1 = H0 + Vector((0.52 * side, 0.05, 0.43)); p2 = H0 + Vector((0.25 * side, 0.2, 0.61))
    n = 22; pts = []; rad = []
    for i in range(n):
        t = i / (n - 1)
        pts.append(qbez(p0, p1, p2, t))
        r = 0.128 * (1 - t) ** 0.8 + 0.022
        rad.append(r * (1 + 0.045 * math.cos(t * 2 * math.pi * 4.2 + 0.6) * (1 - t)))     # sanfte Ringe
    return sweep("Horn%d" % side, pts, rad, segs=16)

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
    return qbez(Vector((0, 0, 0)), Vector((0.06, 0.24, 0)), Vector((WRIST[0], WRIST[1], 0)), t)

def wing(side):
    """Ein Flügel: Arm vom Rücken zum Handgelenk, drei Finger, dazwischen die dünne Haut mit geschwungenem Rand.
    Liefert (Arme und Finger, Flughaut)."""
    W = lambda q, n=0.0: wing_pt(q.x, q.y, n, side)
    bones = [sweep("FluegelArm%d" % side, [W(arm_curve(t)) for t in np.linspace(0, 1, 9)], list(np.linspace(0.062, 0.046, 9)), segs=12)]
    for i, (r0, r1) in enumerate(((0.044, 0.014), (0.032, 0.011), (0.03, 0.011))):
        bones.append(sweep("Finger%d_%d" % (side, i), [W(finger_curve(i, t)) for t in np.linspace(0, 1, 12)], list(np.linspace(r0, r1, 12)), segs=10))
    bones.append(sphere("Handgelenk%d" % side, tuple(W(Vector((WRIST[0], WRIST[1], 0)))), 0.056, segs=(14, 10)))
    bones.append(sphere("Schulter%d" % side, tuple(W(Vector((0.0, -0.01, 0)))), 0.082, segs=(14, 10)))
    # Flughaut: Felder zwischen den Fingern und zwischen innerem Finger und Arm
    curves = [lambda t, i=i: finger_curve(i, t) for i in range(3)] + [lambda t: arm_curve(1 - t)]
    bm = bmesh.new(); ns, nt = 9, 10; cache = {}
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

# ---------------------------------------------------------------- Ablauf

def grey(name, col):
    return look(name, col, rough=0.6)

def build_form(out):
    """Prüfschritt A: nur die Formen, neutral eingefärbt nach Teilen"""
    M = {"haut": grey("Haut", (0.55, 0.55, 0.58)), "platte": grey("Platte", (0.4, 0.4, 0.46)), "horn": grey("Horn", (0.8, 0.78, 0.7)),
         "haut2": grey("Flughaut", (0.62, 0.7, 0.72))}
    body = give(body_shape(), M["haut"]); head = give(head_shape(), M["haut"]); jaw = give(jaw_shape(), M["haut"])
    bvh = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())
    parts = [body, head, jaw]
    parts += [give(o, M["platte"]) for o in head_plates() + spine_plates(bvh)]
    parts += [give(horn(s), M["horn"]) for s in (1, -1)] + [give(o, M["horn"]) for o in claws()]
    for s in (1, -1):
        bones, skin = wing(s)
        parts += [give(o, M["haut"]) for o in bones] + [give(skin, M["haut2"])]
    g = join_parts(parts, "Fuenkchen")
    for p in g.data.polygons:
        p.use_smooth = True
    zs = [v.co.z for v in g.data.vertices]; ys = [v.co.y for v in g.data.vertices]; xs = [v.co.x for v in g.data.vertices]
    print("MASSE x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f, Flächen %d" % (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs), len(g.data.polygons)))
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_yup=True, export_apply=True)

if __name__ == "__main__":
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if STUFE == "form":
        build_form(OUT)
    print("FERTIG", OUT)
