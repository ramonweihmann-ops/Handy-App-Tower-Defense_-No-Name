"""Baut aus dem statischen Meshy-Krabbenpanzer (Vorlage_Raw/Monster_Roh/Modelltests_v6) die Spiel-GLB.
Aufruf: python3 build_krabbe.py <krabbenpanzer_statisch_roh.glb> <ausgabe.glb>   (benötigt: pip install bpy scipy)

Blender-Achsen nach dem Import: Gesicht vorn (−Y), Panzer oben (+Z), die zwei Scheren hoch erhoben über der
hinteren Hälfte (+Y), Spitzen nach außen unten. Das Rohmodell hat acht Laufbeine (vier je Seite, die Prüfung
zählte sechs); die Vorlage verlangt sechs. Das Paar unter den Scheren (fast verdeckt) wird in den Körper
zurückgezogen, damit sechs Beine und zwei Scheren bleiben.

- Gliedmaßen finden: Punkte außerhalb des Panzers (Abstand zur Hochachse > R) und über Kanten verbunden
  bilden je ein Teil; kleine Teile (Gelenkringe) gehören zum Bein in derselben Richtung
- auf etwa 6.500 Dreiecke verkleinern (Gegner „stark“ ≤ 7.000), Textur 1024, Ursprung mittig am Boden
- Skelett: Root → Body; je Bein Oberteil (bis zur Mitte) und Unterteil (bis zum Fuß); je Schere Arm
  (bis zum höchsten Punkt) und Zange (bis zur Spitze); Gewichte selbst berechnet und geglättet
- Walk (0,8 s, Schleife): Dreifuß-Gang wie beim Panzerkäfer, Scheren wiegen leicht, Körper wippt
- Attack (0,9 s, Schleife): Scheren holen nach hinten oben aus und schlagen nach vorn unten zu, Körper geht mit
"""
import bpy, sys, math
import numpy as np
from mathutils import Vector, Matrix, Quaternion
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

src, out = sys.argv[-2], sys.argv[-1]
R = 0.29   # Panzerrand (Abstand zur Hochachse)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
scene = bpy.context.scene
body = [o for o in scene.objects if o.type == 'MESH'][0]
body.name = "Krabbenpanzer"
bpy.context.view_layer.objects.active = body
body.select_set(True)
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in list(scene.objects):
    if o != body:
        bpy.data.objects.remove(o, do_unlink=True)
me = body.data


def parts():
    """Gliedmaßen: (Punkt → Teilnummer oder −1), Liste der Teile mit Art, Winkel, Punkten"""
    V = np.array([v.co[:] for v in me.vertices])
    key = np.round(V / 0.0005).astype(np.int64)
    _, inv = np.unique(key, axis=0, return_inverse=True)
    inv = inv.ravel()
    E = np.array([e.vertices[:] for e in me.edges])
    E = inv[E]
    n = inv.max() + 1
    P = np.zeros((n, 3))
    P[inv] = V
    outside = np.hypot(P[:, 0], P[:, 1]) > R
    m = outside[E[:, 0]] & outside[E[:, 1]]
    A = coo_matrix((np.ones(m.sum()), (E[m, 0], E[m, 1])), shape=(n, n))
    _, lab = connected_components(A, directed=False)
    lab = np.where(outside, lab, -1)
    info = []
    big = {}
    for c in np.unique(lab[lab >= 0]):
        idx = np.nonzero(lab == c)[0]
        Q = P[idx]
        ang = math.degrees(math.atan2(Q[:, 1].mean(), Q[:, 0].mean()))
        if len(idx) >= 80:
            kind = "claw" if Q[:, 2].max() - P[:, 2].min() > 0.33 else "leg"   # Scheren reichen hoch über den Panzer
            big[c] = (kind, ang)
        info.append((c, len(idx), ang))
    # kleine Teile zum Bein in derselben Richtung
    for c, cnt, ang in info:
        if c in big:
            continue
        best = min((abs((ang - a + 180) % 360 - 180), b) for b, (k, a) in big.items() if k == "leg")
        lab[lab == c] = best[1]
    return P, inv, lab[inv], big


# --- Beinpaar unter den Scheren in den Körper zurückziehen --------------------------------------
P, inv, vlab, big = parts()
legs = {c: a for c, (k, a) in big.items() if k == "leg"}
hidden = []
for c, a in legs.items():
    tipy = np.array([me.vertices[i].co.y for i in np.nonzero(vlab == c)[0]])
    if abs(math.cos(math.radians(a))) > 0.85 and tipy.mean() > 0.0:
        hidden.append(c)
print("BEINE", len(legs), "zurückgezogen", len(hidden), "Scheren", sum(1 for k, a in big.values() if k == "claw"))
V = np.array([v.co[:] for v in me.vertices])
inner = np.nonzero(np.hypot(V[:, 0], V[:, 1]) < R - 0.03)[0]
tree = cKDTree(V[inner])
for c in hidden:
    for i in np.nonzero(vlab == c)[0]:
        _, j = tree.query(V[i])
        me.vertices[int(i)].co = Vector(V[inner[j]].tolist())
# auch die Ansätze dieser Beine am Panzerrand (zwischen R − 0,03 und R) in den Körper
near = np.nonzero((np.hypot(V[:, 0], V[:, 1]) >= R - 0.03) & (vlab < 0))[0]
for i in near:
    a = math.degrees(math.atan2(V[i, 1], V[i, 0]))
    for c in hidden:
        if abs((a - legs[c] + 180) % 360 - 180) < 12 and V[i, 2] < -0.05:
            _, j = tree.query(V[i])
            me.vertices[int(i)].co = Vector(V[inner[j]].tolist())
me.update()

# --- Verkleinern, Textur, Boden --------------------------------------------------------------------
tris = sum(len(p.vertices) - 2 for p in me.polygons)
dec = body.modifiers.new("Verkleinern", 'DECIMATE')
dec.ratio = min(1.0, 6500 / tris)
dec.use_collapse_triangulate = True
bpy.ops.object.modifier_apply(modifier=dec.name)
me = body.data
print("DREIECKE", tris, "->", sum(len(p.vertices) - 2 for p in me.polygons))
for img in bpy.data.images:
    if img.size[0] > 1024:
        img.scale(1024, 1024)
        img.pack()
zmin = min(v.co.z for v in me.vertices)
for v in me.vertices:
    v.co.z -= zmin
me.update()

# --- Teile neu bestimmen (nach dem Verkleinern) -----------------------------------------------------
P, inv, vlab, big = parts()
V = np.array([v.co[:] for v in me.vertices])
rr = np.hypot(V[:, 0], V[:, 1])
limbs = {}
for c, (kind, a) in big.items():
    idx = np.nonzero(vlab == c)[0]
    if len(idx) < 30:
        continue   # zurückgezogenes Bein
    Q = V[idx]
    r = np.hypot(Q[:, 0], Q[:, 1])
    root = Q[r < r.min() + 0.02].mean(0)
    tip = Q[r > r.max() - 0.02].mean(0)
    if kind == "claw":
        mid = Q[Q[:, 2] > Q[:, 2].max() - 0.02].mean(0)   # Ellbogen: höchster Punkt
        tip = Q[np.argmax(r)]
    else:
        tip[2] = max(0.01, Q[r > r.max() - 0.02][:, 2].min())
        mid = Q[np.abs(r - (r.min() + r.max()) * 0.5) < 0.02].mean(0)
        mid[2] = Q[np.abs(r - (r.min() + r.max()) * 0.5) < 0.02][:, 2].max() - 0.01
    side = "L" if math.cos(math.radians(a)) < 0 else "R"
    limbs[c] = {"kind": kind, "ang": a, "side": side, "root": root, "mid": mid, "tip": tip}
# Namen: Beine je Seite von vorn (−Y) nach hinten 1..3, Scheren ClawL / ClawR
names = {}
for side in "LR":
    ls = sorted([c for c, g in limbs.items() if g["side"] == side and g["kind"] == "leg"], key=lambda c: limbs[c]["tip"][1])
    for k, c in enumerate(ls):
        names[c] = "%s%d" % (side, k + 1)
    for c, g in limbs.items():
        if g["side"] == side and g["kind"] == "claw":
            names[c] = "Claw" + side
for c, g in limbs.items():
    print("TEIL", names[c], g["kind"], "Ansatz", g["root"].round(3), "Mitte", g["mid"].round(3), "Spitze", g["tip"].round(3))

# --- Skelett ---------------------------------------------------------------------------------------
bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
arm = bpy.context.object
arm.name = "Armature"
eb = arm.data.edit_bones
eb[0].name = "Root"
eb["Root"].head = (0, 0, 0)
eb["Root"].tail = (0, 0, 0.08)
hz = float(np.percentile(V[rr < R][:, 2], 50))
bb = eb.new("Body")
bb.head = (0, 0.15, hz)
bb.tail = (0, -0.15, hz)
bb.parent = eb["Root"]
for c, g in limbs.items():
    n = names[c]
    up = eb.new(n + "_Up")
    up.head = Vector(g["root"].tolist())
    up.tail = Vector(g["mid"].tolist())
    up.parent = bb
    lo = eb.new(n + "_Lo")
    lo.head = Vector(g["mid"].tolist())
    lo.tail = Vector(g["tip"].tolist())
    lo.parent = up
    lo.use_connect = True
bpy.ops.object.mode_set(mode='OBJECT')


def smooth(a, b, x):
    k = min(1.0, max(0.0, (x - a) / (b - a)))
    return k * k * (3 - 2 * k)


groups = {"Body": body.vertex_groups.new(name="Body")}
for c in limbs:
    for p in ("_Up", "_Lo"):
        groups[names[c] + p] = body.vertex_groups.new(name=names[c] + p)
names_l = list(groups.keys())
nv = len(me.vertices)
Wt = np.zeros((nv, len(names_l)))
col = {n: i for i, n in enumerate(names_l)}
# Punkte am Panzerrand: Teil des nächsten Glieds, Übergang über den Rand
lab_pts = np.nonzero(np.isin(vlab, list(limbs.keys())))[0]
ltree = cKDTree(V[lab_pts])
for i in range(nv):
    c = vlab[i]
    if c not in limbs:
        d, j = ltree.query(V[i])
        if d < 0.04 and rr[i] > R - 0.05:
            c = vlab[lab_pts[j]]
    if c not in limbs:
        Wt[i, col["Body"]] = 1.0
        continue
    g = limbs[c]
    on = smooth(R - 0.04, R + 0.02, rr[i])
    a, m, t = g["root"], g["mid"], g["tip"]
    seg = t - a
    tt = float(np.dot(V[i] - a, seg) / np.dot(seg, seg))
    mt = float(np.dot(m - a, seg) / np.dot(seg, seg))
    lo = smooth(mt - 0.08, mt + 0.08, tt)
    Wt[i, col[names[c] + "_Up"]] = on * (1 - lo)
    Wt[i, col[names[c] + "_Lo"]] = on * lo
    Wt[i, col["Body"]] = 1 - on
# glätten wie beim Panzerkäfer, Nahtpunkte gleich
E = np.array([e.vertices[:] for e in me.edges])
deg = np.bincount(E.ravel(), minlength=nv).astype(float)[:, None]
_, inv0 = np.unique(np.round(V / 0.0005).astype(np.int64), axis=0, return_inverse=True)
inv0 = inv0.ravel()
for _ in range(6):
    acc0 = np.zeros((inv0.max() + 1, Wt.shape[1]))
    np.add.at(acc0, inv0, Wt)
    Wt = (acc0 / np.bincount(inv0)[:, None])[inv0]
    nb = np.zeros_like(Wt)
    np.add.at(nb, E[:, 0], Wt[E[:, 1]])
    np.add.at(nb, E[:, 1], Wt[E[:, 0]])
    Wt = 0.5 * Wt + 0.5 * nb / np.maximum(deg, 1.0)
acc = np.zeros((inv0.max() + 1, Wt.shape[1]))
np.add.at(acc, inv0, Wt)
Wt = (acc / np.bincount(inv0)[:, None])[inv0]
Wt /= np.maximum(Wt.sum(1, keepdims=True), 1e-6)
for gi, name in enumerate(names_l):
    for vi in np.nonzero(Wt[:, gi] > 0.001)[0]:
        groups[name].add([int(vi)], float(Wt[vi, gi]), 'REPLACE')
mod = body.modifiers.new("Armature", 'ARMATURE')
mod.object = arm
body.parent = arm

# --- Bewegungen ------------------------------------------------------------------------------------
pose = arm.pose
geo = {names[c]: g for c, g in limbs.items()}


def reset():
    for pb in pose.bones:
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Quaternion()
        pb.location = (0, 0, 0)
    bpy.context.view_layer.update()


def rot(name, axis_, deg):
    """Knochen um eine Weltachse durch seinen Kopf drehen (Kinder drehen mit)."""
    pb = pose.bones[name]
    cur = arm.matrix_world @ pb.matrix
    q = Quaternion(Vector(axis_).normalized(), math.radians(deg))
    m = Matrix.Translation(cur.translation) @ q.to_matrix().to_4x4() @ Matrix.Translation(-cur.translation) @ cur
    pb.matrix = arm.matrix_world.inverted() @ m
    bpy.context.view_layer.update()


def move(name, offset):
    pb = pose.bones[name]
    cur = arm.matrix_world @ pb.matrix
    pb.matrix = arm.matrix_world.inverted() @ (Matrix.Translation(Vector(offset)) @ cur)
    bpy.context.view_layer.update()


def outward(n):
    g = geo[n]
    d = Vector((float(g["tip"][0] - g["root"][0]), float(g["tip"][1] - g["root"][1]), 0.0)).normalized()
    return d, d.cross(Vector((0, 0, 1)))


def leg(n, swing, lift):
    """swing: Grad nach vorn (+) um die Hochachse; lift: Grad Fuß nach oben"""
    d, ax = outward(n)
    left = n.startswith("L")
    rot(n + "_Up", (0, 0, 1), -swing if left else swing)
    rot(n + "_Up", ax, lift)
    rot(n + "_Lo", ax, -lift * 0.45)


def claw(n, raise_, swing, pinch):
    """raise_: Arm nach hinten oben (+) / vorn unten (−) in Grad; swing: zur Mitte (+); pinch: Zange einklappen"""
    d, ax = outward(n)
    left = n.endswith("L")
    rot(n + "_Up", (1, 0, 0), -raise_)
    rot(n + "_Up", (0, 0, 1), -swing if left else swing)
    rot(n + "_Lo", ax, pinch)


def keyall(frame):
    for pb in pose.bones:
        pb.keyframe_insert("rotation_quaternion", frame=frame)
        pb.keyframe_insert("location", frame=frame)


scene.render.fps = 30
arm.animation_data_create()


def make(name, frames):
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    arm.animation_data.action = act
    for f, fn in frames:
        reset()
        fn()
        keyall(f)


TRIPOD_A = ["L1", "R2", "L3"]


def walk(t):
    def f():
        for n in ("L1", "L2", "L3", "R1", "R2", "R3"):
            if n not in geo:
                continue
            p = (t + (0.0 if n in TRIPOD_A else 0.5)) % 1.0
            s = math.sin(2 * math.pi * p)
            leg(n, -14.0 * math.cos(2 * math.pi * p), 24.0 * s * s if s > 0 else 0.0)
        move("Body", (0, 0, 0.004 * (1 + math.cos(4 * math.pi * t)) * 0.5))
        for n in ("ClawL", "ClawR"):
            if n in geo:
                ph = 0.0 if n == "ClawL" else 0.5
                claw(n, 5 * math.sin(2 * math.pi * (t + ph)), 0.0, 6 * math.sin(4 * math.pi * t))
    return f


make("Walk", [(i, walk(i / 24.0)) for i in range(25)])


def attack(t):
    def f():
        # 0 → 0,4 ausholen (Scheren nach hinten oben, Zangen auf), 0,4 → 0,55 nach vorn unten zuschlagen, zurück
        if t < 0.4:
            k = t / 0.4
            k = k * k * (3 - 2 * k)
            up, pinch, pitch, lunge = 22 * k, -14 * k, -6 * k, 0.0
        elif t < 0.55:
            k = (t - 0.4) / 0.15
            up, pinch, pitch, lunge = 22 - 70 * k, -14 + 34 * k, -6 + 16 * k, -0.08 * k
        else:
            k = (t - 0.55) / 0.45
            k = k * k * (3 - 2 * k)
            up, pinch, pitch, lunge = -48 * (1 - k), 20 * (1 - k), 10 * (1 - k), -0.08 * (1 - k)
        move("Root", (0, lunge, 0))
        rot("Body", (1, 0, 0), pitch)
        for n in ("ClawL", "ClawR"):
            if n in geo:
                claw(n, up, 8 * max(0.0, -up) / 48.0, pinch)
        for n in ("L1", "L2", "L3", "R1", "R2", "R3"):
            if n in geo:
                leg(n, 0.0, -pitch * 0.3 if n.endswith("1") else 0.0)
    return f


make("Attack", [(int(round(i * 2.7)), attack(i / 10.0)) for i in range(11)])

arm.animation_data.action = None
reset()
print("BEWEGUNGEN", sorted(a.name for a in bpy.data.actions))
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS',
                          export_yup=True, export_apply=False, export_force_sampling=True)
print("FERTIG", out)
