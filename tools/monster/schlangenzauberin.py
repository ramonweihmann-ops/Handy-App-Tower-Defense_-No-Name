# Schlangenzauberin (Vorlage_Raw/Schlangenzauberin_Vorlage_v1, Wunsch 26.11.2026: „als Zweites dann“).
# Das Originalbild des Nutzers ist maßgeblich (00_originalreferenz.png), 01/02 sind abgeleitete Ansichten.
# Oberkörper einer Zauberin mit genau zwei Armen (je vier Finger und ein Daumen), keine Beine: Der Unterkörper ist ein
# einziger dicker Schlangenschwanz, am Boden in einer breiten Windung eingerollt, vorn steigt er mit hellen
# Bauchplatten zur Hüfte auf. Großer Comic-Kopf mit schrägen Leuchtaugen, sechs dicken Haarschlangen (je ein Kopf),
# Goldkrone mit violettem Stein, goldener Schulterkragen, je zwei Armreifen, Hüftschmuck mit Rautenstein.
# Magiekugeln, schwebende Steine, Nebel und Bodenrune des Originals sind nicht am Modell (wären Spieleffekte).
# Skelett der Schleimmutter plus eigene Knochen (Schwanz, Becken, Brust, Kopf, Arme) mit eigenen Bewegungen.
# Spielname und Welt sind noch offen: Look „schlangen_zauberin“ ist keiner Welt zugeordnet.
# Aufruf: blender -b -P tools/monster/schlangenzauberin.py -- schlangen_zauberin <ziel.glb>
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kristallriese import *          # Metaballs, Bemalen (texels, vertex_ao, texel_values, smoothstep), image_material, smart_uv
from mathutils import Euler, Matrix
import boss_aufsatz
boss_aufsatz.EXPORT_IMAGE_FORMAT = "JPEG"
from schlangenkoenigin import smooth3, mb_ball, remesh_tilted, rhombus_plate, key_rot

RING_C, RING_R, RING_Z, TUBE = (0.0, 0.13), 0.33, 0.235, 0.24
HIP = Vector((0.0, -0.25, 0.64))                 # hier geht der Schwanz in die Taille über
HEAD = Vector((0.0, -0.21, 1.2))
ARM = {s: (Vector((0.185 * s, -0.2, 0.975)), Vector((0.335 * s, -0.2, 0.81)), Vector((0.475 * s, -0.225, 0.655))) for s in (1, -1)}   # Schulter, Ellbogen, Handgelenk
SKIN = (0.26, 0.13, 0.48)

def centerline(n=360):
    pts = []
    for k, deg in enumerate(range(-50, 271, 20)):
        a = math.radians(deg)
        r = RING_R - 0.1 * max(0.0, 1 - k / 4.0)
        pts.append((r * math.cos(a), RING_C[1] + r * math.sin(a), RING_Z - 0.09 * max(0.0, 1 - k / 4.0)))
    pts += [(0.13, -0.22, 0.26), (0.08, -0.3, 0.33), (0.02, -0.33, 0.44), (0.0, -0.3, 0.55), tuple(HIP)]
    P, L = smooth3(pts, n)
    arc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    lift = int(np.argmax((P[:, 2] > RING_Z + 0.03) & (np.arange(n) > n // 4)))
    return P, L, float(arc[lift] / arc[-1])

CL, CL_LEN, U_LIFT = centerline()

def frames():
    n = len(CL); out = []
    arc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(CL, axis=0), axis=1))]; u = arc / arc[-1]
    for i in range(n):
        t = Vector(CL[min(i + 1, n - 1)] - CL[max(i - 1, 0)]).normalized()
        k = smooth01((u[i] - (U_LIFT - 0.08)) / 0.14)
        neck = Vector((0.0, -t.z, t.y))
        if neck.length < 1e-3:
            neck = Vector((0, 0, -1))
        d = Vector((0, 0, -1)).lerp(neck.normalized(), k)
        d = (d - t * d.dot(t)).normalized()
        side = t.cross(d).normalized()
        base = 0.03 + (TUBE - 0.03) * smooth01(u[i] / 0.14)
        f = (u[i] - U_LIFT) / (1 - U_LIFT)
        r = base if f < 0 else TUBE * (1 - 0.42 * smooth01((f - 0.72) / 0.28))       # erst an der Hüfte schmaler
        out.append((t, d, side, r * 1.03, r * 0.95, float(u[i])))
    return out

FR = frames()

def body_tube():
    segs = 28; bm = bmesh.new(); rings = []
    for i in range(0, len(CL), 2):
        t, d, side, a, b, u = FR[i]
        c = Vector(CL[i])
        rings.append([bm.verts.new(c + side * (a * math.cos(q)) + d * (b * math.sin(q) * (0.88 if math.sin(q) > 0 else 1.0)))
                      for q in [k * 2 * math.pi / segs for k in range(segs)]])
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(segs):
            bm.faces.new([r0[k], r0[(k + 1) % segs], r1[(k + 1) % segs], r1[k]])
    tip = bm.verts.new(Vector(CL[0]) - FR[0][0] * 0.04)
    for k in range(segs):
        bm.faces.new([tip, rings[0][(k + 1) % segs], rings[0][k]])
    bm.faces.new(rings[-1])
    return finish("Zauberin", bm)

def torso_shape():
    """Taille, Brustkorb, Schultern, Hals, großer Kopf und Arme als eine weiche Form"""
    R = mb_family("Oberkoerper")
    mb_ell(R, HIP + Vector((0, 0.0, 0.02)), (0.165, 0.14, 0.1))               # Hüfte
    mb_ell(R, (0, -0.235, 0.76), (0.095, 0.08, 0.1))                         # Taille
    mb_ell(R, (0, -0.22, 0.89), (0.14, 0.1, 0.105))                          # Brustkorb
    for s in (1, -1):
        mb_ball(R, (0.06 * s, -0.285, 0.9), 0.058)                           # Brust
        mb_caps(R, (0, -0.2, 0.975), ARM[s][0], 0.05)                        # Schulter
        mb_caps(R, ARM[s][0], ARM[s][1], 0.043)                              # Oberarm
        mb_caps(R, ARM[s][1], ARM[s][2], 0.037)                              # Unterarm
    mb_caps(R, (0, -0.205, 0.98), (0, -0.205, 1.07), 0.04)                   # Hals
    mb_ell(R, HEAD, (0.185, 0.18, 0.185))                                    # Kopf
    mb_ell(R, HEAD + Vector((0, -0.05, -0.11)), (0.115, 0.11, 0.08))         # Kinn (herzförmiges Gesicht)
    mb_ell(R, HEAD + Vector((0, 0.08, 0.04)), (0.21, 0.16, 0.2))             # Haarmasse hinten
    mb_ball(R, HEAD + Vector((0, -0.188, -0.05)), 0.02)                      # kleine Nase
    for s in (1, -1):
        mb_ell(R, HEAD + Vector((0.185 * s, -0.01, -0.01)), (0.032, 0.022, 0.055))  # Ohr
    return mb_to_mesh(R)

def vertex_coords(g):
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

def paint_body(g, us, bel):
    """Dunkelviolette Haut, helle Bauchplatten am Schwanz, wenige Leuchtrisse (Schwanz und Brust), Gesicht ruhig"""
    ao = vertex_ao(g, rays=14, dist=0.22)
    T = texels(g); P, N, cov = T["P"], T["N"], T["cov"]
    AO = texel_values(T, ao); U = texel_values(T, us); B = texel_values(T, bel)
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    col = gradient((0.22, 0.1, 0.42), (0.31, 0.16, 0.56), np.clip(N[..., 2] * 0.5 + 0.5, 0, 1))
    em = np.zeros(P.shape, np.float32)
    tail = smoothstep(HIP.z + 0.04, HIP.z - 0.03, z)
    belly = smoothstep(0.6, 0.72, B) * tail
    edge, cid = worley3(P, 1.9, 61)
    chest = smoothstep(0.75, 0.8, z) * smoothstep(0.99, 0.94, z) * (np.abs(x) < 0.13) * (y < -0.22)
    where = np.maximum(tail * (1 - belly), chest * 0.9)
    edge2, _ = worley3(P, 6.5, 12)
    e_ = np.where(chest > 0.5, edge2 * 3.2, edge)
    line = np.clip(1.6 * (1 - e_ / np.where(chest > 0.5, 0.03, 0.02)), 0, 1) * where
    halo = np.clip(1 - e_ / 0.06, 0, 1) ** 2 * where
    col = col * (1 - 0.25 * halo[..., None]) + np.asarray((0.5, 0.2, 0.85), np.float32) * 0.25 * halo[..., None]
    col = col * (1 - line[..., None]) + np.asarray((0.78, 0.36, 1.0), np.float32) * line[..., None]
    em += np.asarray((0.62, 0.2, 1.0), np.float32) * (line + 0.15 * halo)[..., None]
    bcol = gradient((0.6, 0.48, 0.88), (0.74, 0.64, 0.97), smoothstep(0.65, 0.98, B))
    band = np.abs(((U * CL_LEN / 0.1) % 1.0) - 0.5) * 2
    bline = smoothstep(0.8, 0.95, band)
    bcol = bcol * (1 - 0.32 * bline[..., None]) + np.asarray((0.42, 0.3, 0.72), np.float32) * 0.32 * bline[..., None]
    col = col * (1 - belly[..., None]) + bcol * belly[..., None]
    occ = np.clip(AO * 1.8, 0, 1)
    col = col * (1 - 0.3 * occ[..., None]) + np.asarray((0.16, 0.08, 0.34), np.float32) * 0.3 * occ[..., None]
    face = (y < HEAD.y - 0.06) & (z > HEAD.z - 0.17) & (z < HEAD.z + 0.12) & (np.abs(x) < 0.15)
    fcol = np.asarray((0.3, 0.17, 0.52), np.float32)                 # Gesicht eine Spur heller, damit es lesbar bleibt
    col = np.where(face[..., None], col * 0.4 + fcol * 0.6, col)
    for s in (1, -1):
        d = np.linalg.norm(P - np.asarray(HEAD + Vector((0.075 * s, -0.175, 0.0)), np.float32), axis=-1)
        gl = np.clip(1 - d / 0.1, 0, 1) ** 2
        em += np.asarray((0.7, 0.45, 1.0), np.float32) * gl[..., None] * 0.5
    T["out"][..., :3] = np.where(cov[..., None], np.clip(col, 0, 1), T["out"][..., :3])
    T["em"][..., :3] = np.where(cov[..., None], np.clip(em, 0, 1), 0)
    commit(T, strength=1.6)

# ---------------------------------------------------------------- Aufsätze

def band_ring(name, pts, outs, half_h, thick, mat, up=None):
    """Geschlossener Reif entlang der Punkte: hoch (half_h), dünn (thick), mit weichen Kanten"""
    n = len(pts); bm = bmesh.new(); rings = []
    prof = [(thick * math.copysign(abs(math.cos(q)) ** 0.5, math.cos(q)), half_h * math.copysign(abs(math.sin(q)) ** 0.5, math.sin(q))) for q in [k * 2 * math.pi / 10 for k in range(10)]]
    for i in range(n):
        t = (pts[(i + 1) % n] - pts[(i - 1) % n]).normalized()
        o = outs[i].normalized(); u_ = up if up is not None else t.cross(o).normalized()
        if up is None and u_.z < 0 and abs(u_.z) > 0.3:
            u_ = -u_
        rings.append([bm.verts.new(pts[i] + o * a + u_ * b) for a, b in prof])
    for i in range(n):
        a, b = rings[i], rings[(i + 1) % n]
        for k in range(10):
            bm.faces.new([a[k], a[(k + 1) % 10], b[(k + 1) % 10], b[k]])
    return give(finish(name, bm), mat)

def ring_around(bvh, c, rx, ry, zfun, n=72, lift=0.006, reach=0.3):
    """Punkte rund um die Achse durch c auf der Haut (Strahl von außen nach innen)"""
    pts, outs = [], []
    for k in range(n):
        phi = k * 2 * math.pi / n
        d = Vector((math.sin(phi), -math.cos(phi), 0))
        o = Vector((c.x, c.y, zfun(phi)))
        hit = bvh.ray_cast(o + d * reach, -d, reach)[0]              # nur bis zur Reichweite suchen (nicht an Armen und Händen hängen bleiben)
        r = (hit - o).length if hit is not None else rx
        pts.append((o, d, r)); outs.append(d)
    rad = np.asarray([p[2] for p in pts])
    for _ in range(5):
        rad = 0.25 * np.roll(rad, 1) + 0.5 * rad + 0.25 * np.roll(rad, -1)
    return [o + d * (r + lift) for (o, d, _), r in zip(pts, rad)], outs

def snake_hair(name, pts, M, r0=0.074):
    """Dicke Haarschlange: fester Ansatz im Kopf, genau ein Schlangenkopf am Ende"""
    P, _ = smooth3(pts, 14, passes=6)
    P = [Vector(p) for p in P]
    radii = [r0 * (1.0 - 0.18 * k / (len(P) - 1)) for k in range(len(P))]
    parts = [give(tube(name, [tuple(p) for p in P], radii, segs=12), M["hair"])]
    t = (P[-1] - P[-2]).normalized()
    hc = P[-1] + t * 0.055
    q = t.to_track_quat('-Y', 'Z')
    def loc(x, y, z):
        return hc + q @ Vector((x, y, z))
    h = sphere(name + "Kopf", (0, 0, 0), 1.0, (0.085, 0.115, 0.066), segs=(18, 12)); h.rotation_euler = q.to_euler(); h.location = hc
    parts.append(give(h, M["hair"]))
    j = sphere(name + "Kiefer", (0, 0, 0), 1.0, (0.068, 0.088, 0.026), segs=(14, 8)); j.rotation_euler = q.to_euler(); j.location = loc(0, -0.03, -0.054)
    parts.append(give(j, M["hair"]))
    for s in (1, -1):
        e = sphere(name + "Auge%d" % s, (0, 0, 0), 1.0, (0.017, 0.03, 0.017), segs=(10, 8)); e.rotation_euler = q.to_euler(); e.location = loc(0.062 * s, -0.048, 0.026)
        parts.append(give(e, M["eye"]))
        b = loc(0.04 * s, -0.095, -0.028)
        parts.append(give(tube(name + "Zahn%d" % s, [tuple(b), tuple(b + (q @ Vector((0, 0.005, -0.048))))], [0.012, 0.0], segs=6), M["fang"]))
    return parts

def hand(name, s, M):
    """Offene Hand: vier Finger und ein Daumen, klar getrennt"""
    S_, E_, W_ = ARM[s]
    d = (W_ - E_).normalized()
    side = Vector((0, -1, 0)); side = (side - d * side.dot(d)).normalized()     # Handfläche zeigt nach vorn
    acr = d.cross(side).normalized()                                             # quer über die Handfläche
    parts = []
    palm = sphere(name + "Flaeche", (0, 0, 0), 1.0, (0.044, 0.024, 0.052), segs=(14, 10))
    m = Matrix((acr, side, d)).transposed().to_4x4(); m.translation = W_ + d * 0.04
    palm.matrix_world = m
    parts.append(give(palm, M["hair"]))
    for k, off in enumerate((-0.033, -0.011, 0.011, 0.033)):
        b = W_ + d * 0.08 + acr * off
        spread = acr * (off * 1.3)
        L = 0.09 - 0.014 * abs(k - 1.5)
        pts = [b - d * 0.01, b + d * (L * 0.5) + spread * 0.5 + side * 0.006, b + d * L + spread + side * 0.016]
        parts.append(give(tube(name + "Finger%d" % k, [tuple(p) for p in pts] + [tuple(pts[-1] + d * 0.008)], [0.0155, 0.015, 0.013, 0.0], segs=8), M["hair"]))
    tb = W_ + d * 0.035 + acr * (0.042 * -s)
    tp = [tb, tb + acr * (0.035 * -s) + d * 0.025 + side * 0.012, tb + acr * (0.058 * -s) + d * 0.055 + side * 0.024]
    parts.append(give(tube(name + "Daumen", [tuple(p) for p in tp] + [tuple(tp[-1] + d * 0.008)], [0.0175, 0.016, 0.0135, 0.0], segs=8), M["hair"]))
    return parts

def bracers(name, s, M):
    """Zwei einzelne breite Goldreifen am Unterarm, mit Abstand"""
    S_, E_, W_ = ARM[s]; d = (W_ - E_).normalized()
    a = d.orthogonal().normalized(); b = d.cross(a)
    out = []
    for k, t in enumerate((0.36, 0.74)):
        c = E_.lerp(W_, t); r = 0.037 + 0.012
        pts = [c + (a * math.cos(q) + b * math.sin(q)) * r for q in [i * 2 * math.pi / 28 for i in range(28)]]
        outs = [(p - c) for p in pts]
        out.append(band_ring("%s%d" % (name, k), pts, outs, 0.026, 0.01, M["gold"], up=d))
    return out

def tiara(bvh, M):
    """Goldkrone: geschlossenes Band um den Kopf, vorn ein Rautenrahmen mit violettem Stein"""
    zf = lambda phi: HEAD.z + 0.095 + 0.02 * (1 - math.cos(phi))
    pts, outs = ring_around(bvh, Vector((0, HEAD.y + 0.02, 0)), 0.2, 0.2, zf, n=72, lift=0.008, reach=0.45)
    parts = [band_ring("Kronenband", pts, outs, 0.026, 0.011, M["gold"], up=Vector((0, 0, 1)))]
    front = pts[0]
    up = Vector((0, 0.18, 1)).normalized(); right = Vector((1, 0, 0)); fwd = Vector((0, -1, 0.18)).normalized()
    c = front + up * 0.055 + fwd * 0.006
    parts.append(rhombus_plate("Kronenraute", c, right, up, fwd, 0.09, 0.14, 0.022, M["gold"]))
    parts.append(rhombus_plate("Kronenstein", c, right, up, fwd, 0.056, 0.095, 0.04, M["gem"], inset=1.0))
    for s in (1, -1):                                               # kleine Zacken links und rechts der Raute
        parts.append(rhombus_plate("Kronenzacke%d" % s, pts[(s * 7) % 72] + Vector((0, 0, 0.03)), Vector((math.cos(0.6 * s), math.sin(0.6 * s) * 1.0, 0)).normalized(), Vector((0, 0, 1)), Vector((-math.sin(0.6 * s) * -1.0, -math.cos(0.6 * s), 0)).normalized() * 1.0, 0.035, 0.05, 0.014, M["gold"]))
    return parts

def collar(bvh, M):
    """Goldener Schulterkragen: Reif um den Halsansatz, Schulterstücke, vorn eine Spitze mit kleinem Stein"""
    parts = []
    c = Vector((0, -0.205, 0)); n = 60; pts, outs = [], []
    for k in range(n):
        phi = k * 2 * math.pi / n
        d = Vector((math.sin(phi), -math.cos(phi), 0))
        p = Vector((c.x + d.x * 0.12, c.y + d.y * 0.09, 2.0))
        hit = bvh.ray_cast(p, Vector((0, 0, -1)), 3.0)[0]
        pts.append(Vector((p.x, p.y, (hit.z if hit is not None and hit.z < 1.03 else 0.98) + 0.012))); outs.append(d)
    zs = np.asarray([p.z for p in pts])
    for _ in range(5):
        zs = 0.25 * np.roll(zs, 1) + 0.5 * zs + 0.25 * np.roll(zs, -1)
    for p, z in zip(pts, zs):
        p.z = z
    parts.append(band_ring("Kragen", pts, [Vector((o.x, o.y, -0.7)) for o in outs], 0.016, 0.05, M["gold"], up=Vector((0, 0, 1))))
    for s in (1, -1):
        cap = sphere("Schulterstueck%d" % s, (0, 0, 0), 1.0, (0.092, 0.08, 0.05), segs=(18, 10))
        cap.rotation_euler = (0, math.radians(-28 * s), 0); cap.location = ARM[s][0] + Vector((-0.005 * s, 0, 0.03))
        parts.append(give(cap, M["gold"]))
    hit = bvh.ray_cast(Vector((0, -2.0, 0.945)), Vector((0, 1, 0)), 4.0)[0]
    up = Vector((0, 0.25, 1)).normalized(); fwd = Vector((0, -1, 0.25)).normalized()
    parts.append(rhombus_plate("Kragenspitze", hit + fwd * 0.012, Vector((1, 0, 0)), up, fwd, 0.085, 0.07, 0.016, M["gold"]))
    parts.append(rhombus_plate("Kragenstein", hit + fwd * 0.014, Vector((1, 0, 0)), up, fwd, 0.026, 0.034, 0.024, M["gem"], inset=1.0))
    return parts

def belt(bvh, M):
    """Goldener Hüftschmuck: Reif um die Hüfte, vorn ein großer Rautenrahmen mit violettem Stein"""
    zf = lambda phi: HIP.z + 0.045 - 0.02 * math.cos(phi)
    pts, outs = ring_around(bvh, Vector((0, HIP.y + 0.005, 0)), 0.15, 0.13, zf, n=72, lift=0.006, reach=0.3)
    parts = [band_ring("Hueftreif", pts, outs, 0.038, 0.012, M["gold"], up=Vector((0, 0, 1)))]
    front = pts[0]
    up = Vector((0, -0.08, 1)).normalized(); fwd = Vector((0, -1, -0.08)).normalized()
    c = front + up * -0.03 + fwd * 0.008
    parts.append(rhombus_plate("Hueftraute", c, Vector((1, 0, 0)), up, fwd, 0.1, 0.135, 0.022, M["gold"]))
    parts.append(rhombus_plate("Hueftstein", c, Vector((1, 0, 0)), up, fwd, 0.06, 0.09, 0.04, M["gem"], inset=1.0))
    return parts

def face(bvh, M):
    parts = []
    for s in (1, -1):
        tx, tz = 0.075 * s, HEAD.z + 0.002
        hit, nrm, _, _ = bvh.ray_cast(Vector((tx, -3.0, tz)), Vector((0, 1, 0)), 6.0)
        e = sphere("Auge%d" % s, (0, 0, 0), 1.0, (0.06, 0.02, 0.034), segs=(22, 12))
        e.rotation_euler = Euler((0, math.radians(-24 * s), math.radians(math.degrees(math.atan2(nrm.x, -nrm.y)) * 0.8)), 'XYZ')
        e.location = hit + Vector((0, 0.008, 0))
        parts.append(give(e, M["eye"]))
        brow = []
        for bx, bz in ((0.022, 0.04), (0.078, 0.06), (0.13, 0.068)):
            h = bvh.ray_cast(Vector((bx * s, -3.0, HEAD.z + bz)), Vector((0, 1, 0)), 6.0)[0]
            brow.append(h + Vector((0, -0.004, 0)))
        ends = [brow[0] + (brow[0] - brow[1]).normalized() * 0.01] + brow + [brow[-1] + (brow[-1] - brow[-2]).normalized() * 0.01]
        parts.append(give(tube("Braue%d" % s, [tuple(p) for p in ends], [0.0, 0.011, 0.012, 0.008, 0.0], segs=8), M["brow"]))
    m = [bvh.ray_cast(Vector((mx, -3.0, HEAD.z - 0.108 + 0.3 * mx * mx)), Vector((0, 1, 0)), 6.0)[0] + Vector((0, -0.002, 0)) for mx in (-0.028, 0.0, 0.028)]
    parts.append(give(tube("Mund", [tuple(m[0] + Vector((-0.006, 0, 0)))] + [tuple(p) for p in m] + [tuple(m[2] + Vector((0.006, 0, 0)))], [0.0, 0.005, 0.006, 0.005, 0.0], segs=6), M["brow"]))
    return parts

def hair(M):
    parts = []
    for s in (1, -1):
        parts += snake_hair("HaarOben%d" % s, [(0.08 * s, -0.13, 1.33), (0.15 * s, -0.09, 1.46), (0.23 * s, -0.09, 1.57), (0.24 * s, -0.16, 1.66), (0.19 * s, -0.24, 1.67)], M)
        parts += snake_hair("HaarMitte%d" % s, [(0.16 * s, -0.11, 1.28), (0.29 * s, -0.06, 1.35), (0.39 * s, -0.08, 1.4), (0.44 * s, -0.16, 1.39), (0.43 * s, -0.24, 1.36)], M)
        parts += snake_hair("HaarUnten%d" % s, [(0.17 * s, -0.08, 1.16), (0.3 * s, -0.03, 1.15), (0.38 * s, -0.07, 1.1), (0.4 * s, -0.15, 1.06), (0.39 * s, -0.23, 1.05)], M)
        loop = [(0.11 * s, -0.02, 1.27), (0.21 * s, 0.03, 1.15), (0.2 * s, 0.02, 1.03), (0.12 * s, -0.03, 0.97), (0.07 * s, -0.05, 0.99)]   # Schleife hinten, ohne Kopf
        Pl, _ = smooth3(loop, 12, passes=6)
        parts.append(give(tube("HaarSchleife%d" % s, [tuple(p) for p in Pl], [0.068] * 10 + [0.05, 0.0], segs=12), M["hair"]))
    return parts

# ---------------------------------------------------------------- Skelett und Bewegung

def cl_at(u):
    arc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(CL, axis=0), axis=1))]; arc /= arc[-1]
    return Vector([float(np.interp(u, arc, CL[:, k])) for k in range(3)])

U_TAIL = U_LIFT + (1 - U_LIFT) * 0.12             # Beginn des Knochens „Schwanz“ (aufsteigender Teil)

def make_bones(arm):
    bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones
    def bone(name, head, tail, parent):
        b = eb.new(name); b.head = head; b.tail = tail; b.parent = eb[parent]
    bone("Schwanz", cl_at(U_TAIL), HIP, "Root")
    bone("Becken", HIP, Vector((0, -0.225, 0.82)), "Schwanz")
    bone("Brust", Vector((0, -0.225, 0.82)), Vector((0, -0.205, 1.02)), "Becken")
    bone("Kopf", Vector((0, -0.205, 1.02)), HEAD + Vector((0, 0, 0.12)), "Brust")
    for s, side in ((1, "L"), (-1, "R")):
        bone("Oberarm" + side, ARM[s][0], ARM[s][1], "Brust")
        bone("Unterarm" + side, ARM[s][1], ARM[s][2] + (ARM[s][2] - ARM[s][1]).normalized() * 0.12, "Oberarm" + side)
    bpy.ops.object.mode_set(mode='OBJECT')

def seg_param(p, a, b):
    ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
    return t, (p - (a + ab * t)).length

def weights_fn():
    kd = KDTree(len(CL))
    for i, p in enumerate(CL):
        kd.insert(Vector(p), i)
    kd.balance()
    def w(c):
        c = Vector(c)
        for s, side in ((1, "L"), (-1, "R")):                       # Arme
            if c.x * s > 0.17:
                t1, d1 = seg_param(c, ARM[s][0], ARM[s][1]); t2, d2 = seg_param(c, ARM[s][1], ARM[s][2])
                if min(d1, d2) < 0.085 and c.z < 1.03:
                    if d2 <= d1 or t1 >= 1.0:
                        k = smooth01((t2 + 0.12) / 0.24)
                        return {"Oberarm" + side: 1 - k, "Unterarm" + side: k} if t2 < 0.12 else {"Unterarm" + side: 1.0}
                    k = smooth01(t1 / 0.3)
                    k2 = smooth01((t1 - 0.88) / 0.24)
                    if k2 > 0:
                        return {"Oberarm" + side: 1 - k2, "Unterarm" + side: k2}
                    return {"Brust": 1 - k, "Oberarm" + side: k}
        if c.z > 1.09:
            return {"Kopf": 1.0}
        if c.z > 0.99:
            k = smooth01((c.z - 0.99) / 0.1)
            return {"Brust": 1 - k, "Kopf": k}
        if c.z > HIP.z + 0.02 and (c - Vector((0, -0.23, c.z))).length < 0.3:
            k = smooth01((c.z - (HIP.z + 0.04)) / 0.2)
            return {"Becken": 1 - k, "Brust": k}
        u = FR[kd.find(c)[1]][5]
        k = smooth01((u - (U_TAIL - 0.04)) / 0.08)
        k2 = smooth01((u - 0.9) / 0.1)
        if k2 > 0:
            return {"Schwanz": 1 - k2, "Becken": k2}
        return {"Body": 1 - k, "Schwanz": k}
    return w

def motion(arm):
    """Gleiten: Oberkörper und Kopf wiegen sich, die Arme schweben leicht. Angriff: beide Hände heben und den Zauber
    nach vorn stoßen."""
    for act in bpy.data.actions:
        for fc in list(act.fcurves):
            if fc.data_path == 'pose.bones["Root"].location' and fc.array_index == 1:
                for kp in fc.keyframe_points:
                    kp.co[1] *= 0.0; kp.handle_left[1] *= 0.0; kp.handle_right[1] *= 0.0
                fc.update()
        f1 = int(math.ceil(act.frame_range[1]))
        if act.name.startswith("Walk"):
            w = lambda f, ph=0.0: math.sin(2 * math.pi * f / f1 + ph)
            fr = range(0, f1 + 1, 2)
            key_rot(act, arm, "Schwanz", [(f, (0, 3.0 * w(f), 0)) for f in fr])
            key_rot(act, arm, "Becken", [(f, (0, -2.0 * w(f, 0.5), 2.0 * w(f, 0.5))) for f in fr])
            key_rot(act, arm, "Brust", [(f, (1.5 * w(f * 2), 3.0 * w(f, 1.0), -2.0 * w(f, 1.0))) for f in fr])
            key_rot(act, arm, "Kopf", [(f, (0, -3.5 * w(f, 1.6), 0)) for f in fr])
            for s, side in ((1, "L"), (-1, "R")):
                key_rot(act, arm, "Oberarm" + side, [(f, (-4 - 4 * w(f * 2, 0.5 * s), -5.0 * s * w(f * 2), 0)) for f in fr])
                key_rot(act, arm, "Unterarm" + side, [(f, (-6 - 5 * w(f * 2, 0.9), 0, 0)) for f in fr])
        elif act.name.startswith("Attack"):
            key_rot(act, arm, "Schwanz", [(0, (0, 0, 0)), (9, (-4, 0, 0)), (14, (6, 0, 0)), (f1, (0, 0, 0))])
            key_rot(act, arm, "Brust", [(0, (0, 0, 0)), (9, (-9, 0, 0)), (11, (-9, 0, 0)), (14, (11, 0, 0)), (17, (9, 0, 0)), (f1, (0, 0, 0))])
            key_rot(act, arm, "Kopf", [(0, (0, 0, 0)), (9, (-6, 0, 0)), (14, (5, 0, 0)), (f1, (0, 0, 0))])
            for s, side in ((1, "L"), (-1, "R")):
                key_rot(act, arm, "Oberarm" + side, [(0, (0, 0, 0)), (9, (-35, -28 * s, 0)), (11, (-35, -28 * s, 0)), (14, (-80, 8 * s, -18 * s)), (17, (-76, 8 * s, -18 * s)), (f1, (0, 0, 0))])
                key_rot(act, arm, "Unterarm" + side, [(0, (0, 0, 0)), (9, (-45, 0, 0)), (11, (-45, 0, 0)), (14, (-8, 0, 0)), (17, (-10, 0, 0)), (f1, (0, 0, 0))])

# ---------------------------------------------------------------- Aufbau

@variante("schlangen_zauberin", "schleimmutter")
def schlangenzauberin(arm, body):
    remove_body(body)
    M = {
        "skin": image_material("Zauberinhaut", 2048, color=SKIN, rough=0.45),
        "hair": look("Schlangenhaar", (0.25, 0.12, 0.47), rough=0.45),
        "gold": look("Gold", (1.0, 0.76, 0.26), rough=0.3, metal=0.85),
        "gem": look("Zauberstein", (0.5, 0.18, 0.95), rough=0.08, emit=(0.5, 0.15, 1.0), strength=1.2),
        "eye": look("Leuchtauge", (0.88, 0.78, 1.0), rough=0.2, emit=(0.8, 0.62, 1.0), strength=3.0),
        "fang": look("Zahn", (0.97, 0.96, 1.0), rough=0.15),
        "brow": look("Braue", (0.12, 0.05, 0.24), rough=0.5),
    }
    g = join_parts([body_tube(), torso_shape()], "Zauberin")
    remesh_tilted(g, 0.011)
    md = g.modifiers.new("Glatt", 'SMOOTH'); md.factor = 0.5; md.iterations = 4; apply_mod(g, md)
    for v in g.data.vertices:
        v.co.z = max(v.co.z, 0.0)
    md = g.modifiers.new("Weniger", 'DECIMATE'); md.ratio = 0.24; apply_mod(g, md)
    g.data.validate(clean_customdata=True); g.data.update()
    for p in g.data.polygons:
        p.use_smooth = True
    g.data.materials.clear(); g.data.materials.append(M["skin"])
    smart_uv(g)
    us_v, bel_v = vertex_coords(g)
    paint_body(g, us_v, bel_v)
    bvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    head = join_parts(face(bvh, M) + hair(M) + tiara(bvh, M), "ZauberinKopf")
    chest = join_parts(collar(bvh, M), "ZauberinKragen")
    hip = join_parts(belt(bvh, M), "ZauberinHuefte")
    hands = {s: join_parts(hand("Hand%d" % s, s, M) + bracers("Armreif%d" % s, s, M), "ZauberinHand" + side) for s, side in ((1, "L"), (-1, "R"))}
    make_bones(arm)
    skin_to(g, arm, weights_fn())
    attach(head, arm, "Kopf"); attach(chest, arm, "Brust"); attach(hip, arm, "Becken")
    attach(hands[1], arm, "UnterarmL"); attach(hands[-1], arm, "UnterarmR")
    dampen_scale(arm, ("Body", "Top"), 0.1)
    motion(arm)
    print("ZAUBERIN", len(g.data.polygons), "Flächen Körper,", sum(len(o.data.polygons) for o in (head, chest, hip, hands[1], hands[-1])), "Aufsätze")

if __name__ == "__main__":
    run(VAR, OUT)
