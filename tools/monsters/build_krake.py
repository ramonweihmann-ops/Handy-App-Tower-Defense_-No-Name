"""Baut aus der statischen Meshy-Tiefseekrake (Vorlage_Raw/Monster_Roh/Modelltests_v6) die Spiel-GLB.
Aufruf: python3 build_krake.py <tiefseekrake_statisch_roh.glb> <ausgabe.glb> [dreiecke]   (benötigt: pip install bpy scipy)

Blender-Achsen nach dem Import: Gesicht vorn (−Y), Kopf oben (+Z), acht Fangarme fächerförmig unter dem Kopf,
fast in einer Ebene (x/z), Spitzen nach außen unten.

- Fangarme finden: Punkte unter dem Kopf mit Abstand > R zur Mitte des Fächers (Ansicht von vorn), über Kanten
  verbunden, bilden je einen Arm; kleine Teile (Saugnäpfe) gehören zum nächsten Arm
- auf die Dreieckszahl verkleinern (Boss, Standard 7.000), Textur 1024, Ursprung mittig am Boden
- Skelett: Root → Body (Kopf) → je Arm drei Glieder vom Ansatz bis zur Spitze; Gewichte entlang des Arms
  weich verteilt und geglättet
- Fly (1,2 s, Schleife): schwebt auf und ab, die Arme wogen in einer Welle von innen nach außen
- Attack (1,0 s, Schleife): Arme holen nach hinten oben aus und peitschen nach vorn, der Kopf nickt mit
"""
import bpy, sys, math
import numpy as np
from mathutils import Vector, Matrix, Quaternion
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

args = [a for a in sys.argv[1:] if not a.startswith('-')]
src, out = args[0], args[1]
target = int(args[2]) if len(args) > 2 else 7000
R = 0.22    # Abstand zur Fächermitte (x/z), ab dem die Arme beginnen
ZC = -0.05  # Höhe der Fächermitte im Rohmodell

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
scene = bpy.context.scene
body = [o for o in scene.objects if o.type == 'MESH'][0]
body.name = "Tiefseekrake"
bpy.context.view_layer.objects.active = body
body.select_set(True)
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in list(scene.objects):
    if o != body:
        bpy.data.objects.remove(o, do_unlink=True)
me = body.data

tris = sum(len(p.vertices) - 2 for p in me.polygons)
dec = body.modifiers.new("Verkleinern", 'DECIMATE')
dec.ratio = min(1.0, target / tris)
dec.use_collapse_triangulate = True
bpy.ops.object.modifier_apply(modifier=dec.name)
me = body.data
print("DREIECKE", tris, "->", sum(len(p.vertices) - 2 for p in me.polygons))
for img in bpy.data.images:
    if img.size[0] > 1024:
        img.scale(1024, 1024)
        img.pack()

V = np.array([v.co[:] for v in me.vertices])
zmin = V[:, 2].min()
xmid = (V[:, 0].min() + V[:, 0].max()) * 0.5
ymid = (V[:, 1].min() + V[:, 1].max()) * 0.5
for v in me.vertices:
    v.co.x -= xmid
    v.co.y -= ymid
    v.co.z -= zmin
me.update()
V = np.array([v.co[:] for v in me.vertices])
HUB = np.array([0.0, 0.0, ZC - zmin])
H = V[:, 2].max()

# --- Arme finden ----------------------------------------------------------------------------------
_, inv = np.unique(np.round(V / 0.0005).astype(np.int64), axis=0, return_inverse=True)
inv = inv.ravel()
E = np.array([e.vertices[:] for e in me.edges])
Ei = inv[E]
n = inv.max() + 1
P = np.zeros((n, 3))
P[inv] = V
rp = np.hypot(P[:, 0] - HUB[0], P[:, 2] - HUB[2])
outside = (rp > R) & (P[:, 2] < HUB[2] + 0.12)
m = outside[Ei[:, 0]] & outside[Ei[:, 1]]
A = coo_matrix((np.ones(m.sum()), (Ei[m, 0], Ei[m, 1])), shape=(n, n))
_, lab = connected_components(A, directed=False)
lab = np.where(outside, lab, -1)
cnt = np.bincount(lab[lab >= 0])
bigc = [c for c in np.argsort(-cnt)[:8]]
big_pts = np.nonzero(np.isin(lab, bigc))[0]
btree = cKDTree(P[big_pts])
for c in np.unique(lab[lab >= 0]):
    if c in bigc:
        continue
    idx = np.nonzero(lab == c)[0]
    _, j = btree.query(P[idx].mean(0))
    lab[idx] = lab[big_pts[j]]
vlab = lab[inv]
rv = np.hypot(V[:, 0] - HUB[0], V[:, 2] - HUB[2])

arms = {}
for c in bigc:
    idx = np.nonzero(vlab == c)[0]
    Q = V[idx]
    rq = rv[idx]
    r0, r1 = rq.min(), rq.max()
    pts = []
    for k in range(4):
        u = r0 + (r1 - r0) * k / 3.0
        sel = Q[np.abs(rq - u) < 0.025]
        if len(sel) == 0:
            sel = Q[np.argsort(np.abs(rq - u))[:5]]
        pts.append(sel.mean(0))
    ang = math.degrees(math.atan2(Q[:, 2].mean() - HUB[2], Q[:, 0].mean()))
    arms[c] = {"ang": ang, "pts": pts, "r0": r0, "r1": r1}
# Namen: links (−X) A_L1 (oben) … A_L4 (unten), rechts ebenso
names = {}
for side, sgn in (("L", -1), ("R", 1)):
    cs = sorted([c for c in arms if np.sign(arms[c]["pts"][-1][0]) == sgn], key=lambda c: -arms[c]["pts"][-1][2])
    for k, c in enumerate(cs):
        names[c] = "Arm%s%d" % (side, k + 1)
for c, g in arms.items():
    print("ARM", names[c], "Winkel %.0f" % g["ang"], "Spitze", g["pts"][-1].round(2))

# --- Skelett ----------------------------------------------------------------------------------------
bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
arm = bpy.context.object
arm.name = "Armature"
eb = arm.data.edit_bones
eb[0].name = "Root"
eb["Root"].head = (0, 0, 0)
eb["Root"].tail = (0, 0, 0.1)
bb = eb.new("Body")
bb.head = (0, 0, HUB[2])
bb.tail = (0, 0, H)
bb.parent = eb["Root"]
for c, g in arms.items():
    prev = None
    for k in range(3):
        b = eb.new("%s_%d" % (names[c], k))
        b.head = Vector(g["pts"][k].tolist())
        b.tail = Vector(g["pts"][k + 1].tolist())
        b.parent = prev or bb
        if prev:
            b.use_connect = True
        prev = b
bpy.ops.object.mode_set(mode='OBJECT')


def smooth(a, b, x):
    k = min(1.0, max(0.0, (x - a) / (b - a)))
    return k * k * (3 - 2 * k)


gnames = ["Body"] + ["%s_%d" % (names[c], k) for c in arms for k in range(3)]
col = {nm: i for i, nm in enumerate(gnames)}
nv = len(V)
Wt = np.zeros((nv, len(gnames)))
arm_pts = np.nonzero(np.isin(vlab, list(arms.keys())))[0]
atree = cKDTree(V[arm_pts])
for i in range(nv):
    c = vlab[i]
    if c not in arms:
        d, j = atree.query(V[i])
        if d < 0.05 and V[i, 2] < HUB[2] + 0.12:
            c = vlab[arm_pts[j]]
    if c not in arms:
        Wt[i, col["Body"]] = 1.0
        continue
    g = arms[c]
    on = smooth(R - 0.06, R + 0.03, rv[i])
    u = min(1.0, max(0.0, (rv[i] - g["r0"]) / (g["r1"] - g["r0"]))) * 3.0
    w = [smooth(-0.5, 0.5, u) * (1 - smooth(0.5, 1.5, u)), smooth(0.5, 1.5, u) * (1 - smooth(1.5, 2.5, u)), smooth(1.5, 2.5, u)]
    w[0] = max(w[0], 1.0 - w[1] - w[2])
    s = sum(w)
    for k in range(3):
        Wt[i, col["%s_%d" % (names[c], k)]] = on * w[k] / s
    Wt[i, col["Body"]] = 1 - on
deg = np.bincount(E.ravel(), minlength=nv).astype(float)[:, None]
for _ in range(6):
    acc0 = np.zeros((inv.max() + 1, Wt.shape[1]))
    np.add.at(acc0, inv, Wt)
    Wt = (acc0 / np.bincount(inv)[:, None])[inv]
    nb = np.zeros_like(Wt)
    np.add.at(nb, E[:, 0], Wt[E[:, 1]])
    np.add.at(nb, E[:, 1], Wt[E[:, 0]])
    Wt = 0.5 * Wt + 0.5 * nb / np.maximum(deg, 1.0)
acc = np.zeros((inv.max() + 1, Wt.shape[1]))
np.add.at(acc, inv, Wt)
Wt = (acc / np.bincount(inv)[:, None])[inv]
Wt /= np.maximum(Wt.sum(1, keepdims=True), 1e-6)
groups = {nm: body.vertex_groups.new(name=nm) for nm in gnames}
for gi, nm in enumerate(gnames):
    for vi in np.nonzero(Wt[:, gi] > 0.001)[0]:
        groups[nm].add([int(vi)], float(Wt[vi, gi]), 'REPLACE')
mod = body.modifiers.new("Armature", 'ARMATURE')
mod.object = arm
body.parent = arm

# --- Bewegungen ------------------------------------------------------------------------------------
pose = arm.pose


def reset():
    for pb in pose.bones:
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Quaternion()
        pb.location = (0, 0, 0)
    bpy.context.view_layer.update()


def rot(name, axis_, deg):
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


def tentacle(c, curl, lash):
    """curl: Grad in der Fächerebene (+ = Spitze nach oben/außen); lash: Grad nach vorn (−Y, +) bzw. hinten (−)"""
    nm = names[c]
    sgn = 1.0 if nm[3] == "R" else -1.0
    g = arms[c]
    d = Vector((g["pts"][-1] - g["pts"][0]).tolist())
    d.y = 0.0
    d.normalize()
    side_ax = d.cross(Vector((0, -1, 0)))   # Drehung um diese Achse bewegt die Spitze nach vorn (−Y)
    for k in range(3):
        b = "%s_%d" % (nm, k)
        rot(b, (0, 1, 0), -sgn * curl * (0.6 + 0.2 * k))
        rot(b, side_ax, lash * (0.5 + 0.25 * k))


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


ORDER = {}
for c in arms:
    ORDER[c] = int(names[c][4]) - 1


def fly(t):
    def f():
        move("Root", (0, 0, 0.03 * H * math.sin(2 * math.pi * t)))
        rot("Body", (1, 0, 0), 2.5 * math.sin(2 * math.pi * t + 0.6))
        for c in arms:
            ph = 2 * math.pi * (t - 0.12 * ORDER[c]) + (0.0 if names[c][3] == "L" else 0.35)
            tentacle(c, 9 * math.sin(ph), 7 * math.sin(ph + 1.2))
    return f


make("Fly", [(i, fly(i / 36.0)) for i in range(37)])


def attack(t):
    def f():
        # 0 → 0,4 ausholen (Arme nach hinten oben, Kopf zurück), 0,4 → 0,55 nach vorn peitschen, zurück
        if t < 0.4:
            k = t / 0.4
            k = k * k * (3 - 2 * k)
            lash, curl, head = -26 * k, 10 * k, -8 * k
        elif t < 0.55:
            k = (t - 0.4) / 0.15
            lash, curl, head = -26 + 66 * k, 10 - 16 * k, -8 + 18 * k
        else:
            k = (t - 0.55) / 0.45
            k = k * k * (3 - 2 * k)
            lash, curl, head = 40 * (1 - k), -6 * (1 - k), 10 * (1 - k)
        rot("Body", (1, 0, 0), -head)
        for c in arms:
            tentacle(c, curl, lash * (1.0 if ORDER[c] >= 1 else 0.6))
    return f


make("Attack", [(int(round(i * 3.0)), attack(i / 10.0)) for i in range(11)])

arm.animation_data.action = None
reset()
print("BEWEGUNGEN", sorted(a.name for a in bpy.data.actions))
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS',
                          export_yup=True, export_apply=False, export_force_sampling=True)
print("FERTIG", out)
