# Schlangenkönigin (Vorlage_Raw/Schlangenkoenigin_Vorlage_v1, Wunsch 26.11.2026: „baue sie nach“).
# Das Originalbild des Nutzers ist maßgeblich (00_originalreferenz.png), 01/02 sind abgeleitete Ansichten.
# Ein durchgehender Schlangenkörper entlang einer Mittellinie: breite Windung am Boden, aufgerichteter Vorderkörper
# in S-Kurve mit Haube, breiter Kopf mit schweren Brauen, zwei schrägen Leuchtaugen, zwei Giftzähnen, gegabelter
# Zunge und goldener Krone mit violettem Stein. Dunkelviolette Haut mit wenigen breiten Leuchtrissen, helle
# Bauchplatten entlang des ganzen Verlaufs. Nichts schwebt (Steine, Nebel und Aura des Originals wären Effekte).
# Skelett der Schleimmutter plus Knochenkette Hals1–Hals3 und Kopf mit eigenen Bewegungen (wiegen, zustoßen).
# Spielname und Welt sind noch offen: Look „schlangen_koenigin“ ist keiner Welt zugeordnet.
# Aufruf: blender -b -P tools/monster/schlangenkoenigin.py -- schlangen_koenigin <ziel.glb>
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kristallriese import *          # Metaballs, Bemalen (texels, vertex_ao, texel_values, smoothstep), image_material, smart_uv
from mathutils import Euler, Matrix
import boss_aufsatz
boss_aufsatz.EXPORT_IMAGE_FORMAT = "JPEG"

RING_C, RING_R, RING_Z = (0.0, 0.0), 0.3, 0.24
H = Vector((0.0, -0.15, 1.2))                   # Mitte des Kopfes
HS = 1.3                                        # Größe des Kopfes

def hp(x, y, z):
    return H + Vector((x, y, z)) * HS

def mb_ball(o, c, r):
    return mb_ell(o, c, (r, r, r))

def smooth3(pts, n, passes=40):
    P = np.asarray(pts, float); out = []
    for i in range(len(P) - 1):
        p0 = P[max(i - 1, 0)]; p1 = P[i]; p2 = P[i + 1]; p3 = P[min(i + 2, len(P) - 1)]
        for t in np.linspace(0, 1, 10, endpoint=False):
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-1]); out = np.asarray(out)
    for _ in range(passes):
        out[1:-1] = 0.25 * out[:-2] + 0.5 * out[1:-1] + 0.25 * out[2:]
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(out, axis=0), axis=1))]
    s = np.linspace(0, d[-1], n)
    return np.stack([np.interp(s, d, out[:, k]) for k in range(3)], 1), d[-1]

def centerline(n=420):
    """Mittellinie vom Schwanz zum Kopfansatz: Windung am Boden, dann vorn aufsteigen und als S nach oben"""
    pts = []
    for k, deg in enumerate(range(-50, 271, 20)):
        a = math.radians(deg)
        r = RING_R - 0.1 * max(0.0, 1 - k / 4.0)            # Schwanz liegt innen
        pts.append((r * math.cos(a), RING_C[1] + r * math.sin(a), RING_Z - 0.09 * max(0.0, 1 - k / 4.0)))
    ring_n = len(pts)
    pts += [(0.12, -0.2, 0.31), (0.06, -0.27, 0.42), (0.01, -0.27, 0.55), (0.0, -0.18, 0.69), (0.0, -0.04, 0.81),
            (0.0, 0.1, 0.94), (0.0, 0.19, 1.07), (0.0, 0.18, 1.2), (0.0, 0.09, 1.29), (0.0, -0.02, 1.31)]
    P, L = smooth3(pts, n)
    arc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    lift = int(np.argmax((P[:, 2] > RING_Z + 0.03) & (np.arange(n) > n // 4)))     # hier verlässt der Körper den Boden
    return P, L, float(arc[lift] / arc[-1])

CL, CL_LEN, U_LIFT = centerline()

def frames():
    """Je Punkt der Mittellinie: Richtung, Bauchrichtung, Seite, halbe Breite, halbe Tiefe"""
    n = len(CL); out = []
    arc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(CL, axis=0), axis=1))]; u = arc / arc[-1]
    for i in range(n):
        t = Vector(CL[min(i + 1, n - 1)] - CL[max(i - 1, 0)]).normalized()
        k = smooth01((u[i] - (U_LIFT - 0.06)) / 0.14)        # am Boden zeigt der Bauch nach unten, am Hals nach vorn
        neck = Vector((0.0, -t.z, t.y))
        if neck.length < 1e-3:
            neck = Vector((0, 0, -1))
        d = Vector((0, 0, -1)).lerp(neck.normalized(), k)
        d = (d - t * d.dot(t)).normalized()
        side = t.cross(d).normalized()
        z = CL[i][2]
        base = 0.03 + 0.22 * smooth01(u[i] / 0.14)            # Schwanz wird schnell dick
        r = base if u[i] < U_LIFT else 0.25 - 0.04 * smooth01((u[i] - U_LIFT) / 0.1)
        f = (u[i] - U_LIFT) / (1 - U_LIFT)                    # Anteil am aufgerichteten Vorderkörper
        hood = math.exp(-((f - 0.72) / 0.27) ** 2) if f > 0.15 else 0.0  # Haube hinter dem Kopf
        a = r * (1 + 0.78 * hood) * (1 - 0.18 * smooth01((f - 0.93) / 0.07))
        b = r * (1 - 0.12 * hood) * (1 - 0.25 * smooth01((f - 0.93) / 0.07))
        out.append((t, d, side, a, b, float(u[i])))
    return out

FR = frames()

def body_tube():
    """Körper als Schlauch mit ovalem Querschnitt (Bauch etwas flacher)"""
    segs = 28; bm = bmesh.new(); rings = []
    for i in range(0, len(CL), 2):
        t, d, side, a, b, u = FR[i]
        c = Vector(CL[i])
        rings.append([bm.verts.new(c + side * (a * math.cos(q)) + d * (b * math.sin(q) * (0.86 if math.sin(q) > 0 else 1.0)))
                      for q in [k * 2 * math.pi / segs for k in range(segs)]])
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(segs):
            bm.faces.new([r0[k], r0[(k + 1) % segs], r1[(k + 1) % segs], r1[k]])
    tip = bm.verts.new(Vector(CL[0]) - FR[0][0] * 0.04)
    for k in range(segs):
        bm.faces.new([tip, rings[0][(k + 1) % segs], rings[0][k]])
    bm.faces.new(rings[-1])
    return finish("Schlange", bm)

def head_shape():
    """Breiter Kopf mit flacher Schnauze, schweren Brauen und kräftigem Unterkiefer"""
    R = mb_family("Schlangenkopf")
    k = HS
    mb_ell(R, H, (0.21 * k, 0.18 * k, 0.135 * k))
    mb_ell(R, hp(0, -0.15, -0.035), (0.15 * k, 0.105 * k, 0.07 * k))              # flache, breite Schnauze
    mb_ell(R, hp(0, -0.09, -0.1), (0.15 * k, 0.14 * k, 0.045 * k))                # Unterkiefer
    for s in (1, -1):
        mb_caps(R, hp(0.03 * s, -0.175, 0.05), hp(0.175 * s, -0.06, 0.095), 0.036 * k)   # Brauenwulst: innen tief, außen hoch
        mb_ell(R, hp(0.14 * s, -0.03, -0.04), (0.09 * k, 0.12 * k, 0.09 * k))     # Wange
    return mb_to_mesh(R)

def remesh_tilted(o, voxel):
    rot = Euler((0.31, 0.42, 0.23)).to_matrix().to_4x4()
    o.data.transform(rot); o.data.update()
    remesh(o, voxel)
    o.data.transform(rot.inverted()); o.data.update()

def vertex_coords(g):
    """Je Punkt: Lage entlang des Körpers (0 Schwanz … 1 Kopf) und wie sehr er zur Bauchseite gehört (-1 … 1).
    Wo sich Windung und Hals berühren, zählt der Abschnitt, in dessen Querschnitt der Punkt wirklich liegt; danach
    über das Netz geglättet, damit die Bauchkante ruhig verläuft."""
    kd = KDTree(len(CL))
    for i, p in enumerate(CL):
        kd.insert(Vector(p), i)
    kd.balance()
    n = len(g.data.vertices)
    us = np.zeros(n, np.float32); bel = np.zeros(n, np.float32)
    for v in g.data.vertices:
        best = None
        for _, i, dist in kd.find_n(v.co, 24):
            t, d, side, a, b, u = FR[i]
            off = v.co - Vector(CL[i]); along = off.dot(t); perp = off - t * along
            score = abs(along) + 0.5 * abs(perp.length - 0.5 * (a + b))
            if best is None or score < best[0]:
                best = (score, u, perp.normalized().dot(d) if perp.length > 1e-5 else 0.0)
        us[v.index] = best[1]; bel[v.index] = best[2]
    e = np.asarray([tuple(ed.vertices) for ed in g.data.edges])
    cnt = np.bincount(e.ravel(), minlength=n).astype(np.float32)
    for _ in range(6):
        acc = np.zeros(n, np.float32)
        np.add.at(acc, e[:, 0], bel[e[:, 1]]); np.add.at(acc, e[:, 1], bel[e[:, 0]])
        bel = 0.5 * bel + 0.5 * acc / np.maximum(cnt, 1)
    return us, bel

def in_head(P):
    return np.linalg.norm((P - np.asarray(H, np.float32)) / (np.asarray((0.27, 0.29, 0.2), np.float32) * HS), axis=-1) < 1.0

def paint_snake(g, us, bel):
    """Dunkelviolette Haut, breite Leuchtrisse, helle Bauchplatten mit Querbändern, dunkles Maul, Leuchten um die Augen"""
    ao = vertex_ao(g, rays=14, dist=0.25)
    T = texels(g); P, N, cov = T["P"], T["N"], T["cov"]
    AO = texel_values(T, ao); U = texel_values(T, us); B = texel_values(T, bel)
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    head = in_head(P)
    col = gradient((0.24, 0.11, 0.46), (0.33, 0.17, 0.6), np.clip(N[..., 2] * 0.5 + 0.5, 0, 1))
    em = np.zeros(P.shape, np.float32)
    core = np.linalg.norm((P - np.asarray(H, np.float32)) / (np.asarray((0.24, 0.23, 0.17), np.float32) * HS), axis=-1) < 1.0
    belly = smoothstep(0.38, 0.5, B) * (~head)
    # Leuchtrisse: wenige, breit, nur auf der dunklen Haut (nicht im Gesicht)
    edge, cid = worley3(P, 1.9, 61)
    calm = np.where(head & (y < H.y + 0.05), 0.0, 1.0)
    line = np.clip(1.6 * (1 - edge / 0.02), 0, 1) * (1 - belly) * calm
    halo = np.clip(1 - edge / 0.06, 0, 1) ** 2 * (1 - belly) * calm
    col = col * (1 - 0.25 * halo[..., None]) + np.asarray((0.5, 0.2, 0.85), np.float32) * 0.25 * halo[..., None]
    col = col * (1 - line[..., None]) + np.asarray((0.78, 0.36, 1.0), np.float32) * line[..., None]
    em += np.asarray((0.62, 0.2, 1.0), np.float32) * (line + 0.15 * halo)[..., None]
    # Bauchplatten: helles Lavendel, Querbänder entlang des Körpers
    bcol = gradient((0.62, 0.5, 0.9), (0.76, 0.66, 0.98), smoothstep(0.5, 0.95, B))
    band = np.abs(((U * CL_LEN / 0.105) % 1.0) - 0.5) * 2
    bline = smoothstep(0.82, 0.95, band)
    bcol = bcol * (1 - 0.3 * bline[..., None]) + np.asarray((0.45, 0.32, 0.75), np.float32) * 0.3 * bline[..., None]
    col = col * (1 - belly[..., None]) + bcol * belly[..., None]
    occ = np.clip(AO * 1.8, 0, 1)
    col = col * (1 - 0.3 * occ[..., None]) + np.asarray((0.2, 0.1, 0.4), np.float32) * 0.3 * occ[..., None]
    # Maul innen dunkel
    # Maulspalt: dunkle Linie in der Falte zwischen Schnauze und Unterkiefer
    zm = H.z - 0.07 * HS + 0.1 * (y - (H.y - 0.2 * HS)) + 0.8 * x * x / HS
    mouth = np.clip(1.5 * (1 - np.abs(z - zm) / (0.02 * HS)), 0, 1) * head * (y < H.y - 0.02 * HS) * (np.abs(x) < 0.2 * HS)
    col = col * (1 - mouth[..., None]) + np.asarray((0.08, 0.03, 0.16), np.float32) * mouth[..., None]
    for s in (1, -1):                                               # Schein um die Leuchtaugen
        d = np.linalg.norm(P - np.asarray(hp(0.105 * s, -0.19, -0.012), np.float32), axis=-1)
        gl = np.clip(1 - d / 0.17, 0, 1) ** 2
        em += np.asarray((0.7, 0.45, 1.0), np.float32) * gl[..., None] * 0.6
        col = col * (1 - 0.3 * gl[..., None]) + np.asarray((0.6, 0.35, 0.95), np.float32) * 0.3 * gl[..., None]
    T["out"][..., :3] = np.where(cov[..., None], np.clip(col, 0, 1), T["out"][..., :3])
    T["em"][..., :3] = np.where(cov[..., None], np.clip(em, 0, 1), 0)
    commit(T, strength=1.6)

def rhombus_plate(name, c, right, up, fwd, w, h, depth, mat, inset=0.0):
    """Raute als Platte (oder mit inset als geschliffener Stein: vorn und hinten spitz zulaufend)"""
    bm = bmesh.new()
    def ring(scale, off):
        return [bm.verts.new(c + right * (w * scale * dx) + up * (h * scale * dz) + fwd * off) for dx, dz in ((0, 1), (1, 0), (0, -1), (-1, 0))]
    if inset:
        a = ring(1.0, 0.0); f = bm.verts.new(c + fwd * depth); b = bm.verts.new(c - fwd * depth)
        for k in range(4):
            bm.faces.new([a[k], a[(k + 1) % 4], f]); bm.faces.new([a[(k + 1) % 4], a[k], b])
    else:
        f0 = ring(0.86, depth); f1 = ring(1.0, depth * 0.55); b1 = ring(1.0, -depth * 0.55); b0 = ring(0.86, -depth)
        for r0, r1 in ((f0, f1), (f1, b1), (b1, b0)):
            for k in range(4):
                bm.faces.new([r0[k], r0[(k + 1) % 4], r1[(k + 1) % 4], r1[k]])
        bm.faces.new(f0[::-1]); bm.faces.new(b0)
    return give(finish(name, bm, smooth=False), mat)

def crown(bvh, gold, gem):
    """Goldener Reif fest auf dem Kopf, rundum geschlossen: vorn große Raute mit violettem Stein, seitlich und hinten
    niedrigere Zacken"""
    cy = H.y + 0.0 * HS; n = 96
    zf = bvh.ray_cast(Vector((0, cy - 0.12 * HS, 2.0)), Vector((0, 0, -1)), 3.0)[0].z
    zb = bvh.ray_cast(Vector((0, cy + 0.12 * HS, 2.0)), Vector((0, 0, -1)), 3.0)[0].z
    peaks = ((55, 0.06, 26), (-55, 0.06, 26), (125, 0.03, 28), (-125, 0.03, 28), (180, 0.03, 30))
    bm = bmesh.new(); rings = []
    for k in range(n):
        phi = k * 2 * math.pi / n
        out = Vector((math.sin(phi), -math.cos(phi), 0))
        p = Vector((0.155 * HS * out.x, cy + 0.12 * HS * out.y, 2.0))
        hit = bvh.ray_cast(p, Vector((0, 0, -1)), 3.0)[0]
        plane = (zf + zb) / 2 - (zb - zf) / 2 * math.cos(phi)       # Reif liegt in einer Ebene: vorn tiefer, hinten höher
        z0 = min(plane, hit.z if hit is not None else plane) - 0.03
        deg = math.degrees(phi); h = 0.075
        for c, amp, wdt in peaks:
            dd = abs((deg - c + 180) % 360 - 180)
            h += amp * max(0.0, 1 - dd / wdt) ** 0.8
        base = Vector((p.x, p.y, z0))
        rings.append([bm.verts.new(base + out * 0.022), bm.verts.new(base + out * 0.03 + Vector((0, 0, h))),
                      bm.verts.new(base - out * 0.006 + Vector((0, 0, h))), bm.verts.new(base - out * 0.014)])
    zs = np.asarray([r[0].co.z for r in rings])
    for _ in range(6):                                              # Unterkante ruhig halten
        zs = 0.25 * np.roll(zs, 1) + 0.5 * zs + 0.25 * np.roll(zs, -1)
    for r, z in zip(rings, zs):
        dz = z - r[0].co.z
        for v in r:
            v.co.z += dz
    for i in range(n):
        a, b = rings[i], rings[(i + 1) % n]
        for k in range(4):
            bm.faces.new([a[k], a[(k + 1) % 4], b[(k + 1) % 4], b[k]])
    front = rings[0][0].co.copy()
    band = give(finish("Kronenreif", bm), gold)
    up = Vector((0, 0.2, 1)).normalized(); right = Vector((1, 0, 0)); fwd = up.cross(right).normalized()
    if fwd.y > 0:
        fwd = -fwd
    c = front + up * 0.115 + fwd * 0.004
    frame = rhombus_plate("Kronenraute", c, right, up, fwd, 0.135, 0.21, 0.03, gold)
    stone = rhombus_plate("Kronenstein", c, right, up, fwd, 0.088, 0.145, 0.062, gem, inset=1.0)
    return [band, frame, stone]

def face_parts(M, bvh):
    parts = []
    for s in (1, -1):
        tgt = hp(0.105 * s, 0, -0.012)                                # Auge liegt auf der Haut unter der Braue
        hit, nrm, _, _ = bvh.ray_cast(Vector((tgt.x, -3.0, tgt.z)), Vector((0, 1, 0)), 6.0)
        e = sphere("Auge%d" % s, (0, 0, 0), 1.0, (0.09 * HS, 0.03 * HS, 0.05 * HS), segs=(24, 14))
        yaw = math.degrees(math.atan2(nrm.x, -nrm.y)) * 0.8           # der Wölbung folgen, schräg: außen hoch
        e.rotation_euler = Euler((0, math.radians(-26 * s), math.radians(yaw)), 'XYZ')
        e.location = hit + Vector((0, 0.014 * HS, 0))
        parts.append(give(e, M["eye"]))
        b = hp(0.095 * s, -0.228, -0.066)                  # Giftzahn: breit am Kiefer, spitz, leicht nach hinten gebogen
        parts.append(give(tube("Giftzahn%d" % s, [tuple(b + Vector((0, 0.01, 0.02))), tuple(b), tuple(b + Vector((0, 0.004, -0.06))), tuple(b + Vector((0, 0.018, -0.14)))],
                               [0.036, 0.036, 0.025, 0.0], segs=12), M["fang"]))
        parts.append(give(sphere("Nase%d" % s, tuple(hp(0.038 * s, -0.25, 0.02)), 0.012, (1, 0.6, 1)), M["dark"]))
    t0 = hp(0, -0.17, -0.085)
    stem = [t0, t0 + Vector((0, -0.09, -0.02)), t0 + Vector((0, -0.14, -0.09)), t0 + Vector((0, -0.16, -0.17))]
    parts.append(give(tube("Zunge", [tuple(p) for p in stem], [0.02, 0.02, 0.018, 0.015], segs=10), M["tongue"]))
    for s in (1, -1):
        tip = [stem[-1] + Vector((0, 0.004, 0.01)), stem[-1] + Vector((0.02 * s, -0.012, -0.035)), stem[-1] + Vector((0.05 * s, -0.035, -0.06)), stem[-1] + Vector((0.065 * s, -0.06, -0.05))]
        parts.append(give(tube("Zungenspitze%d" % s, [tuple(p) for p in tip], [0.015, 0.012, 0.008, 0.0], segs=8), M["tongue"]))
    return parts

# ---------------------------------------------------------------- Skelett und Bewegung

JOINTS = tuple(U_LIFT + (1 - U_LIFT) * f for f in (0.06, 0.36, 0.64, 0.9))     # Beginn von Hals1, Hals2, Hals3, Kopf

def cl_at(u):
    arc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(CL, axis=0), axis=1))]; arc /= arc[-1]
    return Vector([float(np.interp(u, arc, CL[:, k])) for k in range(3)])

def neck_bones(arm):
    bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones; parent = eb["Root"]
    us = JOINTS
    names = ("Hals1", "Hals2", "Hals3", "Kopf")
    for k, name in enumerate(names):
        b = eb.new(name); b.head = cl_at(us[k]); b.tail = cl_at(us[k + 1]) if k < 3 else hp(0, -0.25, 0)
        b.parent = parent; parent = b
    bpy.ops.object.mode_set(mode='OBJECT')
    return us

def bone_weights(us):
    """Gewichte entlang des Körpers: Windung am Boden (Body), dann Hals1–Hals3 und Kopf, weich überblendet"""
    cuts = list(us)
    def w(u):
        names = ["Body", "Hals1", "Hals2", "Hals3", "Kopf"]
        out = {}
        idx = sum(1 for c in cuts if u >= c)                       # 0 = Body … 4 = Kopf
        out[names[idx]] = 1.0
        for k, c in enumerate(cuts):                               # um jedes Gelenk weich mischen
            wdt = 0.035
            if abs(u - c) < wdt:
                t = smooth01((u - c + wdt) / (2 * wdt))
                out = {names[k]: 1 - t, names[k + 1]: t}
        return out
    return w

def key_rot(act, arm, bone, keys):
    """Drehungen um Achsen der Welt als Schlüsselbilder eines Knochens: keys = [(Bild, (x°, y°, z°)), …]"""
    M = arm.data.bones[bone].matrix_local.to_3x3()
    curves = [act.fcurves.new('pose.bones["%s"].rotation_quaternion' % bone, index=i, action_group=bone) for i in range(4)]
    for f, (rx, ry, rz) in keys:
        R = Euler((math.radians(rx), math.radians(ry), math.radians(rz)), 'XYZ').to_matrix()
        q = (M.inverted() @ R @ M).to_quaternion()
        for i in range(4):
            curves[i].keyframe_points.insert(f, q[i])

def snake_motion(arm):
    """Kriechen: Hals und Kopf wiegen sich hin und her. Angriff: zurücknehmen, dann blitzschnell nach vorn zustoßen."""
    for act in bpy.data.actions:
        for fc in list(act.fcurves):
            if fc.data_path == 'pose.bones["Root"].location' and fc.array_index == 1:
                for kp in fc.keyframe_points:                      # kein Hüpfen
                    kp.co[1] *= 0.0; kp.handle_left[1] *= 0.0; kp.handle_right[1] *= 0.0
                fc.update()
        f1 = int(math.ceil(act.frame_range[1]))
        if act.name.startswith("Walk"):
            for bone, amp, ph in (("Hals1", 5.0, 0.0), ("Hals2", -6.0, 0.6), ("Hals3", 5.0, 1.2), ("Kopf", -4.0, 1.8)):
                key_rot(act, arm, bone, [(f, (1.5 * math.sin(2 * math.pi * f / f1 * 2 + ph), amp * math.sin(2 * math.pi * f / f1 + ph), -0.6 * amp * math.sin(2 * math.pi * f / f1 + ph)))
                                         for f in range(0, f1 + 1, 2)])
        elif act.name.startswith("Attack"):
            for bone, back, fwd in (("Hals1", -10, 20), ("Hals2", -12, 18), ("Hals3", -8, 10), ("Kopf", 14, -26)):
                key_rot(act, arm, bone, [(0, (0, 0, 0)), (9, (back, 0, 0)), (11, (back, 0, 0)), (14, (fwd, 0, 0)), (17, (fwd * 0.8, 0, 0)), (f1, (0, 0, 0))])

# ---------------------------------------------------------------- Aufbau

@variante("schlangen_koenigin", "schleimmutter")
def schlangenkoenigin(arm, body):
    remove_body(body)
    M = {
        "skin": image_material("Schlangenhaut", 2048, color=(0.27, 0.13, 0.5), rough=0.45),
        "gold": look("Gold", (1.0, 0.76, 0.26), rough=0.3, metal=0.85),
        "gem": look("Kronenstein", (0.5, 0.18, 0.95), rough=0.08, emit=(0.5, 0.15, 1.0), strength=1.2),
        "eye": look("Leuchtauge", (0.88, 0.78, 1.0), rough=0.2, emit=(0.8, 0.62, 1.0), strength=3.0),
        "fang": look("Giftzahn", (0.97, 0.96, 1.0), rough=0.15),
        "tongue": look("Zunge", (0.78, 0.3, 0.95), rough=0.3, emit=(0.6, 0.15, 0.8), strength=0.4),
        "dark": look("Nasenloch", (0.08, 0.03, 0.14), rough=0.5),
    }
    g = join_parts([body_tube(), head_shape()], "Schlange")
    remesh_tilted(g, 0.012)
    md = g.modifiers.new("Glatt", 'SMOOTH'); md.factor = 0.5; md.iterations = 5; apply_mod(g, md)
    for v in g.data.vertices:
        v.co.z = max(v.co.z, 0.0)
    md = g.modifiers.new("Weniger", 'DECIMATE'); md.ratio = 0.22; apply_mod(g, md)
    g.data.validate(clean_customdata=True); g.data.update()     # entartete Flächen entfernen, sonst verwirft der Export den Körper
    for p in g.data.polygons:
        p.use_smooth = True
    g.data.materials.clear(); g.data.materials.append(M["skin"])
    smart_uv(g)
    us_v, bel_v = vertex_coords(g)
    paint_snake(g, us_v, bel_v)
    bvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    head = join_parts(face_parts(M, bvh) + crown(bvh, M["gold"], M["gem"]), "Schlangenkopf")
    cuts = neck_bones(arm)
    w = bone_weights(cuts)
    kd = KDTree(len(CL))
    for i, p in enumerate(CL):
        kd.insert(Vector(p), i)
    kd.balance()
    def weights(c):
        if (Vector(c) - H).length < 0.3 * HS and c.z > H.z - 0.2 * HS and c.y < H.y + 0.2 * HS:
            return {"Kopf": 1.0}
        return w(FR[kd.find(c)[1]][5])
    skin_to(g, arm, weights)
    attach(head, arm, "Kopf")
    dampen_scale(arm, ("Body", "Top"), 0.12)
    snake_motion(arm)
    print("SCHLANGE", len(g.data.polygons), "Flächen Körper,", len(head.data.polygons), "Kopf")

if __name__ == "__main__":
    run(VAR, OUT)
