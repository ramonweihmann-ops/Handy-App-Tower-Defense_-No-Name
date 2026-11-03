"""Baut aus dem Meshy-Rohmodell des Panzerkäfers die Spiel-GLB (Vorlage_Raw/Monster_Roh/Modelltests_v2).
Aufruf: python3 build_panzerkaefer.py <panzerkaefer_statisch_roh.glb> <ausgabe.glb>   (benötigt: pip install bpy)

Das Rohmodell ist statisch (kein Skelett). Blender-Achsen nach dem Import: Käfer schaut nach −Y,
Panzer oben (+Z), linke Seite −X. Sechs Beine, getrennt über den Winkel um die Körpermitte:
vorn links/rechts, Mitte links/rechts, hinten links/rechts. Vorn in der Mitte ragt das Gesicht vor.

- Spitzer Netzfortsatz unter dem linken Mittelbein (Erzeugungsfehler): über die Draufsicht erkannt und
  auf das Bein zurückgesetzt; auf etwa 6.500 Dreiecke verkleinern (Gegner „stark“ ≤ 7.000), Textur 1024
- Ursprung zwischen den Füßen auf den Boden
- Skelett: Root → Body → Head, je Bein Hüfte (bis zum Knie) und Unterschenkel (bis zum Fuß),
  Gewichte selbst berechnet (Körper, Kopf, Beine mit weichem Übergang an Knie und Panzerrand)
- Walk (0,8 s, Schleife): Dreifuß-Gang, abwechselnd vorn links/Mitte rechts/hinten links und die anderen
  drei; Bein hebt sich, schwingt nach vorn, setzt auf, schiebt nach hinten; Körper wippt leicht
- Attack (0,9 s, Schleife): bäumt sich vorn auf (Kopf hoch, Vorderbeine zur Seite, damit das Gesicht frei
  bleibt), schnappt nach vorn unten zu
"""
import bpy, bmesh, sys, math
import numpy as np
from mathutils import Vector, Matrix, Quaternion

src, out = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
scene = bpy.context.scene
body = [o for o in scene.objects if o.type == 'MESH'][0]
body.name = "Panzerkaefer"
me = body.data

# --- Beine finden ---------------------------------------------------------------------------
A, B = 0.27, 0.33   # Panzerrand (Ellipse in xy)
LEGS = {  # Name: Winkelbereich (Grad, x rechts, y hinten); vorn = −Y
    "FL": (-165, -125), "ML": (165, 195), "BL": (125, 165),
    "FR": (-60, -25), "MR": (-25, 15), "BR": (15, 50),
}


ZOFF = 0.0   # nach dem Absenken auf den Boden: um so viel liegen die Punkte höher als im Rohmodell


def leg_of(co):
    e = math.hypot(co.x / A, co.y / B)
    if e <= 0.92 or co.z - ZOFF > 0.02:
        return None, e
    a = math.degrees(math.atan2(co.y, co.x))
    for n, (lo, hi) in LEGS.items():
        aa = a + 360 if (hi > 180 and a < 0) else a
        if lo <= aa < hi:
            return n, e
    return None, e


def leg_points():
    pts = {n: [] for n in LEGS}
    for v in me.vertices:
        n, e = leg_of(v.co)
        if n and e > 1.0:
            pts[n].append(v.index)
    return pts


# Achse je Bein (Hauptrichtung der Beinpunkte)
def axis(idx):
    P = np.array([me.vertices[i].co[:] for i in idx])
    c = P.mean(0)
    u, s, vt = np.linalg.svd(P - c, full_matrices=False)
    d = vt[0]
    if np.dot(d, np.array([c[0], c[1], 0.0])) < 0:
        d = -d
    return P, c, d


# Fortsatz: dünner Dorn unter dem linken Mittelbein. In der Draufsicht des Netzes (selbst gezeichnet)
# verschwindet er beim Öffnen der Silhouette; seine Spitzenpunkte liegen außerhalb der geöffneten Form und
# werden auf den nächsten Punkt innerhalb gesetzt.
import cv2
V = np.array([v.co[:] for v in me.vertices])
NPX = 1024
SC = NPX / 1.1
PX = np.stack([((V[:, 0] + 0.55) * SC).astype(int), ((0.55 - V[:, 1]) * SC).astype(int)], 1)
mask = np.zeros((NPX, NPX), np.uint8)
for poly in me.polygons:
    cv2.fillPoly(mask, [PX[list(poly.vertices)].astype(np.int32)], 255)
opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))
thin = cv2.morphologyEx(cv2.subtract(mask, opened), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
n_cc, lab, st, _ = cv2.connectedComponentsWithStats(thin)
spike_px = np.zeros_like(thin)
for i in range(1, n_cc):
    if st[i, cv2.CC_STAT_AREA] > 40 and max(st[i, 2], st[i, 3]) > 25:
        spike_px[lab == i] = 255
spike_px = cv2.dilate(spike_px, np.ones((11, 11), np.uint8))
inside = opened > 0
spike = [j for j, (x, y) in enumerate(PX) if spike_px[y, x] and not inside[y, x]]
good = np.array([j for j, (x, y) in enumerate(PX) if inside[y, x]])
for j in spike:
    k = good[np.argmin(np.linalg.norm(V[good] - V[j], axis=1))]
    me.vertices[j].co = me.vertices[int(k)].co.copy()
me.update()
print("FORTSATZ Punkte zurückgesetzt:", len(spike))

# Verkleinern, Textur 1024
tris = sum(len(p.vertices) - 2 for p in me.polygons)
bpy.context.view_layer.objects.active = body
body.select_set(True)
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

# Ursprung auf den Boden zwischen den Füßen
zmin = min(v.co.z for v in me.vertices)
for v in me.vertices:
    v.co.z -= zmin
me.update()
ZOFF = -zmin

# --- Skelett ---------------------------------------------------------------------------------
pts = leg_points()
geo = {}
for n, idx in pts.items():
    P, c, d = axis(idx)
    t = (P - c) @ d
    t0, t1 = t.min(), t.max()
    root = c + t0 * d
    tip_pts = P[t > t1 - 0.03]
    tip = tip_pts.mean(0)
    tip[2] = max(0.01, tip_pts[:, 2].min())
    mid = P[np.abs(t - (t0 + 0.5 * (t1 - t0))) < 0.03]
    knee = mid.mean(0)
    knee[2] = np.percentile(mid[:, 2], 70)
    geo[n] = {"root": root, "knee": knee, "tip": tip, "c": c, "d": d, "t0": t0, "t1": t1}
    print("BEIN", n, "Hüfte", root.round(3), "Knie", knee.round(3), "Fuß", tip.round(3))

bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
arm = bpy.context.object
arm.name = "Armature"
eb = arm.data.edit_bones
eb[0].name = "Root"
eb["Root"].head = (0, 0, 0)
eb["Root"].tail = (0, 0, 0.08)
hz = 0.2
bb = eb.new("Body")
bb.head = (0, 0.12, hz)
bb.tail = (0, -0.12, hz)
bb.parent = eb["Root"]
hb = eb.new("Head")
hb.head = (0, -0.24, 0.11)
hb.tail = (0, -0.36, 0.09)
hb.parent = bb
for n, g in geo.items():
    up = eb.new("Leg%s_Up" % n)
    up.head = Vector(g["root"].tolist())
    up.tail = Vector(g["knee"].tolist())
    up.parent = bb
    lo = eb.new("Leg%s_Lo" % n)
    lo.head = Vector(g["knee"].tolist())
    lo.tail = Vector(g["tip"].tolist())
    lo.parent = up
    lo.use_connect = True
bpy.ops.object.mode_set(mode='OBJECT')

# --- Gewichte --------------------------------------------------------------------------------
groups = {}
for name in ["Body", "Head"] + ["Leg%s_%s" % (n, p) for n in LEGS for p in ("Up", "Lo")]:
    groups[name] = body.vertex_groups.new(name=name)


def smooth(a, b, x):
    k = min(1.0, max(0.0, (x - a) / (b - a)))
    return k * k * (3 - 2 * k)


for v in me.vertices:
    co = v.co
    n, e = leg_of(co)
    w = {}
    if n:
        g = geo[n]
        p = np.array([co.x, co.y, co.z])
        knee_t = float(np.dot(g["knee"] - g["root"], g["tip"] - g["root"]) / np.dot(g["tip"] - g["root"], g["tip"] - g["root"]))
        tt = float(np.dot(p - g["root"], g["tip"] - g["root"]) / np.dot(g["tip"] - g["root"], g["tip"] - g["root"]))
        on_leg = smooth(0.92, 1.06, e)
        lo = smooth(knee_t - 0.1, knee_t + 0.1, tt)
        w["Leg%s_Up" % n] = on_leg * (1 - lo)
        w["Leg%s_Lo" % n] = on_leg * lo
        w["Body"] = 1 - on_leg
    else:
        # Gesicht: vorn unter dem Panzer
        head = smooth(-0.2, -0.28, co.y) * (1 - smooth(0.16, 0.24, co.z))
        w["Head"] = head
        w["Body"] = 1 - head
    for k, val in w.items():
        if val > 0.001:
            groups[k].add([v.index], val, 'REPLACE')

mod = body.modifiers.new("Armature", 'ARMATURE')
mod.object = arm
body.parent = arm

# --- Bewegungen ------------------------------------------------------------------------------
pose = arm.pose


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


def leg(n, swing, lift, bend=None):
    """swing: Grad nach vorn (+) / hinten (−) um die Hochachse; lift: Grad Fuß nach oben;
    bend: Unterschenkel zusätzlich (Standard: hält den Fuß beim Heben etwas unter dem Knie)"""
    g = geo[n]
    left = g["d"][0] < 0
    rot("Leg%s_Up" % n, (0, 0, 1), swing if left else -swing)
    d = Vector((float(g["d"][0]), float(g["d"][1]), 0.0)).normalized()
    ax = d.cross(Vector((0, 0, 1)))
    rot("Leg%s_Up" % n, ax, lift)
    rot("Leg%s_Lo" % n, ax, -lift * 0.45 if bend is None else bend)


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


TRIPOD_A = ["FL", "MR", "BL"]
SWING = 14.0
LIFT = 22.0


def gait(p):
    """Bein im Dreifuß-Gang zum Zeitpunkt p (0..1): (swing, lift)"""
    if p < 0.5:   # Schwungphase: hoch und nach vorn
        k = p / 0.5
        s = k * k * (3 - 2 * k)
        return -SWING + 2 * SWING * s, LIFT * math.sin(math.pi * k)
    k = (p - 0.5) / 0.5   # Standphase: Fuß am Boden, schiebt nach hinten
    return SWING - 2 * SWING * k, 0.0


def walk(t):
    def f():
        for n in LEGS:
            p = (t + (0.0 if n in TRIPOD_A else 0.5)) % 1.0
            sw, li = gait(p)
            leg(n, sw, li)
        move("Body", (0, 0, 0.012 * math.cos(4 * math.pi * t)))
        rot("Body", (0, 1, 0), 2.0 * math.sin(2 * math.pi * t))
        rot("Head", (1, 0, 0), 3.0 * math.sin(4 * math.pi * t))
    return f


make("Walk", [(int(round(i * 2)), walk(i / 12.0)) for i in range(13)])


def attack(t):
    def f():
        # 0 → 0,4 aufbäumen (Kopf hoch, Vorderbeine zur Seite), 0,4 → 0,55 nach vorn unten zuschnappen, zurück
        if t < 0.4:
            k = t / 0.4
            k = k * k * (3 - 2 * k)
            pitch, head, front, lunge = -16 * k, -16 * k, 1.0 * k, 0.0
        elif t < 0.55:
            k = (t - 0.4) / 0.15
            pitch, head, front, lunge = -16 + 26 * k, -16 + 40 * k, 1.0 - 1.3 * k, -0.11 * k
        else:
            k = (t - 0.55) / 0.45
            k = k * k * (3 - 2 * k)
            pitch, head, front, lunge = 10 * (1 - k), 24 * (1 - k), -0.3 * (1 - k), -0.11 * (1 - k)
        move("Root", (0, lunge, 0))
        rot("Body", (1, 0, 0), pitch)
        rot("Head", (1, 0, 0), head)
        for n in ("FL", "FR"):
            # zur Seite und leicht nach hinten, angehoben: das Gesicht bleibt frei
            leg(n, -18 * front, 16 * max(0.0, front))
        for n in ("ML", "MR", "BL", "BR"):
            leg(n, 0.0, 0.0, -pitch * 0.3)
    return f


make("Attack", [(int(round(i * 2.7)), attack(i / 10.0)) for i in range(11)])

arm.animation_data.action = None
reset()
print("BEWEGUNGEN", sorted(a.name for a in bpy.data.actions))
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS',
                          export_yup=True, export_apply=False, export_force_sampling=True)
print("FERTIG", out)
