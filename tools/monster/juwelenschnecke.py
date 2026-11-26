# Juwelenschnecke neu (Entwurf „Rosenquarz-Regentin“ von ChatGPT, vom Nutzer freigegeben am 26.11.2026):
# Vorlage_Raw/Juwelenschnecke_Neuentwurf_v1 (01_turnaround.png verbindlich, 02_kopf_und_angriff.png, LIESMICH_CLAUDE.md).
# Eine durchgehende weiche rosa Schnecke mit breitem, welligem Kriechfuß, hellem Bauch mit Falten, zwei Stielaugen mit
# schweren Brauen, zwei kurzen Tastfühlern, frechem Grinsen mit Kristallzähnen und Gold-Diadem mit Rubin. Darauf ein
# massives Haus aus Rosenquarz: ein geschlossener Körper, die Goldspirale liegt in einer flachen Rille der Seitenfläche
# (aus der Seitenansicht der Vorlage abgenommen), große Rubine sitzen bündig in Goldfassungen.
# Skelett der Schleimmutter (Body, Top) plus ein Knochen „Haus“: Das Haus bleibt starr und fährt nur mit dem Rücken mit.
# Spielname bleibt „Juwelenschnecke“ (Look juwelen_schnecke, ersetzt die alte Röhrenschnecke).
# Aufruf: blender -b -P tools/monster/juwelenschnecke.py -- juwelen_schnecke <ziel.glb>
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kristallriese import *
from mathutils import Euler          # Metaballs, Bemalen (texels, vertex_ao, texel_values, smoothstep), image_material, smart_uv
import boss_aufsatz
boss_aufsatz.EXPORT_IMAGE_FORMAT = "JPEG"

# ---------------------------------------------------------------- Maße aus der Seitenansicht der Vorlage

def side_px(X, Y):
    """Bildpunkt des Seitenausschnitts (1000 breit) -> (y, z) im Modell; die Schnecke schaut nach -y"""
    return ((X - 505) * 0.00175, (770 - Y) * 0.00175)

SC = side_px(620, 375)                       # Mitte des Hauses (y, z)
SA, SRY, SRZ, SN = 0.47, 0.569, 0.485, 2.4   # halbe Breite, Radien, Form (über 2 = breitere Lauffläche, gewölbte Seiten)
RHO_MAX = 0.86                               # so weit außen liegt die Goldkante höchstens (Schulter der Lauffläche)
RELIEF = 0.012                               # Windungen wölben sich so weit über die Rille der Goldkante
# Goldspirale von außen (unten vorn am Körper) nach innen, aus der Vorlage abgenommen
SPIRAL_PX = [(478, 590), (432, 500), (430, 420), (455, 340), (510, 265), (590, 215), (680, 195), (770, 205), (850, 250),
             (910, 320), (940, 410), (930, 500), (880, 580), (800, 630), (700, 650), (620, 625), (585, 560), (575, 500),
             (590, 440), (630, 395), (690, 370), (760, 375), (810, 410), (830, 460), (815, 510), (775, 535), (730, 525),
             (712, 495), (722, 468), (745, 462), (756, 476)]

def smooth_line(pts, n, passes=60):
    """Handabgenommene Punkte zu einer ruhigen, gleichmäßig unterteilten Linie"""
    P = np.asarray(pts, float); out = []
    for i in range(len(P) - 1):
        p0 = P[max(i - 1, 0)]; p1 = P[i]; p2 = P[i + 1]; p3 = P[min(i + 2, len(P) - 1)]
        for t in np.linspace(0, 1, 12, endpoint=False):
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-1]); out = np.asarray(out)
    for _ in range(passes):
        out[1:-1] = 0.25 * out[:-2] + 0.5 * out[1:-1] + 0.25 * out[2:]
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(out, axis=0), axis=1))]
    s = np.linspace(0, d[-1], n)
    return np.stack([np.interp(s, d, out[:, 0]), np.interp(s, d, out[:, 1])], 1)

def spiral_line(n=200):
    L = smooth_line([side_px(*p) for p in SPIRAL_PX], n)
    dy, dz = (L[:, 0] - SC[0]) / SRY, (L[:, 1] - SC[1]) / SRZ
    rho = np.maximum(np.hypot(dy, dz), 1e-6); a = 0.6
    t = np.clip((rho - a) / (1 - a), 0, 1)
    k = np.where(rho > a, a + (RHO_MAX - a) * (1 - (1 - t) ** 2), rho) / rho      # außen weich an die Schulter anlegen
    return np.stack([SC[0] + dy * k * SRY, SC[1] + dz * k * SRZ], 1)

SPIRAL = spiral_line()

def shell_rho(y, z):
    return np.hypot((np.asarray(y) - SC[0]) / SRY, (np.asarray(z) - SC[1]) / SRZ)

def spiral_dist(y, z):
    Q = np.stack([np.ravel(y), np.ravel(z)], 1)
    out = np.empty(len(Q))
    for a in range(0, len(Q), 4000):
        out[a:a + 4000] = np.sqrt(((Q[a:a + 4000, None, :] - SPIRAL[None]) ** 2).sum(-1)).min(1)
    return out.reshape(np.shape(y))

def shell_f(y, z):
    """Halbe Breite des Hauses über dem Punkt (y, z) der Seitenansicht, mit den gewölbten Windungen"""
    rho = np.clip(shell_rho(y, z), 0, 1)
    base = SA * np.clip(1 - rho ** SN, 0, 1) ** (1 / SN)
    return base + RELIEF * (1 - np.exp(-(spiral_dist(y, z) / 0.06) ** 2)) * smoothstep(1.0, 0.8, rho)

def shell_frames(L, side):
    """Punkte und Normalen auf der Seitenfläche des Hauses zu Punkten (y, z) der Seitenansicht"""
    y, z = L[:, 0], L[:, 1]; e = 2e-3
    f = shell_f(y, z)
    fy = (shell_f(y + e, z) - shell_f(y - e, z)) / (2 * e); fz = (shell_f(y, z + e) - shell_f(y, z - e)) / (2 * e)
    P = np.stack([side * f, y, z], 1)
    N = np.stack([np.full(len(y), float(side)), -fy, -fz], 1); N /= np.linalg.norm(N, axis=1, keepdims=True)
    return P, N

# ---------------------------------------------------------------- Haus

def shell_mesh(mat):
    """Geschlossenes Haus: Drehkörper mit breiter Lauffläche, die Seitenflächen tragen die Windungen. Liefert auch
    den Abstand jedes Punkts zur Goldkante (für die Schattierung der Rille)."""
    NT, NU = 128, 60
    us = np.linspace(-math.pi / 2, math.pi / 2, NU + 1)[1:-1]
    th = np.arange(NT) * 2 * math.pi / NT
    U, TH = np.meshgrid(us, th, indexing='ij')
    rho = np.abs(np.cos(U)) ** (2 / SN)
    Y = SC[0] + SRY * rho * np.cos(TH); Z = SC[1] + SRZ * rho * np.sin(TH)
    X = np.sign(np.sin(U)) * shell_f(Y, Z) * (np.abs(np.sin(U)) ** (2 / SN) / np.maximum((1 - rho ** SN) ** (1 / SN), 1e-6))
    D = spiral_dist(Y, Z)
    bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap")
    rings = [[bm.verts.new((X[i, k], Y[i, k], Z[i, k])) for k in range(NT)] for i in range(len(us))]
    pole_d = float(spiral_dist(np.asarray([SC[0]]), np.asarray([SC[1]]))[0])
    pole_x = float(shell_f(np.asarray([SC[0]]), np.asarray([SC[1]]))[0])
    lo = bm.verts.new((-pole_x, SC[0], SC[1])); hi = bm.verts.new((pole_x, SC[0], SC[1]))
    def face(vs, uvs):
        f = bm.faces.new(vs)
        for l, (a, b) in zip(f.loops, uvs):
            l[uv].uv = (a / NT, (b + 1) / (NU))
    for i in range(len(us) - 1):
        for k in range(NT):
            k1 = (k + 1) % NT
            face([rings[i][k], rings[i][k1], rings[i + 1][k1], rings[i + 1][k]], [(k, i), (k + 1, i), (k + 1, i + 1), (k, i + 1)])
    for k in range(NT):
        k1 = (k + 1) % NT
        face([lo, rings[0][k1], rings[0][k]], [(k + 0.5, -1), (k + 1, 0), (k, 0)])
        face([hi, rings[-1][k], rings[-1][k1]], [(k + 0.5, len(us)), (k, len(us) - 1), (k + 1, len(us) - 1)])
    dist = [float(D[i, k]) for i in range(len(us)) for k in range(NT)] + [pole_d, pole_d]
    o = finish("Haus", bm)
    give(o, mat)
    return o, np.asarray(dist, np.float32)

def paint_shell(o, dist):
    """Rosenquarz: große ruhige Flächen, oben heller, in der Rille neben der Goldkante etwas tiefer im Ton"""
    T = texels(o); P, N, cov = T["P"], T["N"], T["cov"]
    D = texel_values(T, dist)
    col = np.broadcast_to(np.asarray((0.92, 0.47, 0.6), np.float32), P.shape).copy()
    top = np.clip(N[..., 2], 0, 1) ** 1.5
    col = col * (1 - 0.25 * top[..., None]) + np.asarray((0.98, 0.62, 0.72), np.float32) * 0.25 * top[..., None]
    low = np.clip(-N[..., 2], 0, 1)
    col = col * (1 - 0.3 * low[..., None]) + np.asarray((0.8, 0.36, 0.52), np.float32) * 0.3 * low[..., None]
    col = col * (0.97 + 0.06 * fbm3(P, 2.2, 5, 2)[..., None])
    side = smoothstep(0.12, 0.3, np.abs(P[..., 0]))
    groove = np.exp(-(D / 0.05) ** 2) * side
    col = col * (1 - 0.3 * groove[..., None]) + np.asarray((0.74, 0.3, 0.47), np.float32) * 0.3 * groove[..., None]
    T["out"][..., :3] = np.where(cov[..., None], np.clip(col, 0, 1), T["out"][..., :3])
    commit(T)

def sweep(name, P, N, w, h, lift, segs=10, closed=False):
    """Band mit ovalem Querschnitt entlang der Punkte P (Fläche darunter mit Normalen N): w halbe Breite, h halbe
    Höhe, lift hebt die Mitte über die Fläche. Offene Enden laufen in eine Spitze aus."""
    n = len(P)
    P = [Vector(p) for p in P]; N = [Vector(q).normalized() for q in N]
    bm = bmesh.new(); rings = []
    for i in range(n):
        a = P[(i - 1) % n] if closed else P[max(i - 1, 0)]
        b = P[(i + 1) % n] if closed else P[min(i + 1, n - 1)]
        t = (b - a).normalized()
        side = N[i].cross(t).normalized(); up = t.cross(side).normalized()
        if up.dot(N[i]) < 0:
            up = -up
        c = P[i] + up * lift[i]
        rings.append([bm.verts.new(c + side * (w[i] * math.cos(q)) + up * (h[i] * math.sin(q))) for q in [k * 2 * math.pi / segs for k in range(segs)]])
    last = n if closed else n - 1
    for i in range(last):
        a, b = rings[i], rings[(i + 1) % n]
        for k in range(segs):
            bm.faces.new([a[k], a[(k + 1) % segs], b[(k + 1) % segs], b[k]])
    if not closed:
        for ring, rev in ((rings[0], True), (rings[-1], False)):
            bm.faces.new(ring[::-1] if rev else ring)
    return finish(name, bm)

def gold_spiral(side, mat):
    P, N = shell_frames(SPIRAL, side)
    s = np.linspace(0, 1, len(P))
    taper = np.minimum(1, np.sqrt(s / 0.05)) * np.minimum(1, np.sqrt((1 - s) / 0.03))
    w = np.maximum((0.042 - 0.02 * s) * taper, 0.002)
    return give(sweep("Goldkante%d" % side, P, N, w, w * 0.75, w * 0.75 * 0.5, segs=8), mat)

def bezel_gem(name, bvh, c, n, u, ru, rv, gold, ruby, segs=12, dome=0.42, rim=0.024):
    """Großer Edelstein, bündig in einer breiten Goldfassung, die der Wölbung der Fläche folgt"""
    c = Vector(c); n = Vector(n).normalized(); u = Vector(u); u = (u - n * u.dot(n)).normalized(); v = n.cross(u)
    def on(a, b):
        o = c + u * a + v * b
        hit, nn, _, _ = bvh.ray_cast(o + n * 0.35, -n, 0.9)
        return (hit, nn) if hit is not None else (o, n)
    ring = [on((ru + rim * 0.7) * math.cos(q), (rv + rim * 0.7) * math.sin(q)) for q in [k * 2 * math.pi / 48 for k in range(48)]]
    k48 = len(ring)
    bez = sweep(name + "Fassung", [p for p, _ in ring], [q for _, q in ring], [rim] * k48, [rim * 0.7] * k48, [rim * 0.25] * k48, segs=10, closed=True)
    give(bez, gold)
    H = min(ru, rv) * dome
    bm = bmesh.new()
    def loop(scale, lift, shift):
        return [bm.verts.new(on(ru * scale * math.cos(q), rv * scale * math.sin(q))[0] + n * lift) for q in [(k + shift) * 2 * math.pi / segs for k in range(segs)]]
    r0 = loop(1.0, -0.012, 0.0); r1 = loop(1.0, 0.012, 0.0); r2 = loop(0.74, 0.012 + H * 0.72, 0.5); r3 = loop(0.46, 0.012 + H, 0.0)
    top = bm.verts.new(on(0, 0)[0] + n * (0.012 + H))
    for k in range(segs):
        k1 = (k + 1) % segs
        bm.faces.new([r0[k], r0[k1], r1[k1], r1[k]])
        bm.faces.new([r1[k], r1[k1], r2[k]]); bm.faces.new([r1[k1], r2[k1], r2[k]])
        bm.faces.new([r2[k], r2[k1], r3[k1]]); bm.faces.new([r2[k], r3[k1], r3[k]])
        bm.faces.new([r3[k], r3[k1], top])
    g = finish(name + "Stein", bm, smooth=False)
    give(g, ruby)
    return [bez, g]

def shell_tread(theta, x):
    """Punkt und Normale auf der Lauffläche des Hauses (Winkel um die Achse, Abstand von der Mitte)"""
    rho = (1 - (abs(x) / SA) ** SN) ** (1 / SN)
    p = Vector((x, SC[0] + SRY * rho * math.cos(theta), SC[1] + SRZ * rho * math.sin(theta)))
    n = Vector((SN * abs(x) ** (SN - 1) / SA ** SN * (1 if x >= 0 else -1), SN * rho ** (SN - 1) * math.cos(theta) / SRY, SN * rho ** (SN - 1) * math.sin(theta) / SRZ))
    return p, n.normalized()

# ---------------------------------------------------------------- Körper

M_W = 0.2                                        # halbe Breite des Mauls
BELLY_Z = (0.398, 0.284, 0.196)                  # Höhe der Bauchfalten in der Mitte
STALK = {s: (Vector((0.17 * s, -0.595, 0.66)), Vector((0.2 * s, -0.585, 1.0)), Vector((0.2 * s, -0.58, 1.125))) for s in (1, -1)}
BULB_R = 0.156

def mouth_top(x):
    return 0.646 - 0.084 * np.clip(1 - (np.asarray(x) / M_W) ** 2, 0, 1)

def mouth_low(x):
    return 0.646 - 0.136 * np.clip(1 - (np.asarray(x) / M_W) ** 2, 0, 1) ** 0.75

def mb_ball(o, c, r):
    return mb_ell(o, c, (r, r, r))

def body_shape():
    """Eine zusammenhängende weiche Form: Kriechfuß mit welligem Saum, Rücken, Brust, Kopf, Tastfühler, Augenstiele"""
    R = mb_family("Schnecke")
    mb_ell(R, (0, 0.05, 0.07), (0.47, 0.57, 0.1))                   # Kriechfuß
    n = 72
    for k in range(n):                                             # welliger Saum: ein durchgehender Wulst, der sanft schwingt
        a = k * 2 * math.pi / n
        wave = math.cos(12 * a)
        k_ = 1.0 + 0.055 * wave
        mb_ball(R, (0.48 * k_ * math.sin(a), 0.05 - 0.595 * k_ * math.cos(a), 0.066 + 0.018 * wave), 0.08 + 0.012 * wave)
    mb_ell(R, (0, 0.13, 0.17), (0.42, 0.56, 0.17))                 # Rücken unter dem Haus
    mb_ell(R, (0, 0.52, 0.11), (0.27, 0.2, 0.09))                  # Schwanzende
    mb_ell(R, (0, -0.5, 0.34), (0.42, 0.31, 0.33))                 # Brust
    mb_ell(R, (0, -0.58, 0.585), (0.32, 0.25, 0.265))              # Kopf
    mb_ell(R, (0, -0.79, 0.5), (0.15, 0.065, 0.05))                # Kinn
    for s in (1, -1):
        mb_caps(R, (0.25 * s, -0.65, 0.585), (0.4 * s, -0.72, 0.598), 0.032)   # Tastfühler: kurz, dick, stumpf
        mb_ball(R, (0.425 * s, -0.73, 0.6), 0.052)
    parts = [mb_to_mesh(R)]
    for s in (1, -1):
        F = mb_family("Stiel%d" % s)
        mb_caps(F, STALK[s][0], STALK[s][1], 0.046)
        mb_ball(F, STALK[s][2], BULB_R)
        parts.append(mb_to_mesh(F))
    return join_parts(parts, "Schnecke")

def remesh_tilted(o, voxel):
    """Neu vernetzen mit schräg gelegtem Raster: sonst hinterlässt es auf fast senkrechten Flächen (Bauch) Treppenstufen"""
    rot = Euler((0.31, 0.42, 0.23)).to_matrix().to_4x4()
    o.data.transform(rot); o.data.update()
    remesh(o, voxel)
    o.data.transform(rot.inverted()); o.data.update()

def mouth_cut():
    """Grinsen als Sichel (Mundwinkel oben), ein Stück in den Kopf geschnitten"""
    xs = np.linspace(-M_W, M_W, 41)
    outline = [(x, float(mouth_top(x))) for x in xs] + [(x, float(mouth_low(x))) for x in xs[-2:0:-1]]
    bm = bmesh.new()
    front = [bm.verts.new((x, -1.2, z)) for x, z in outline]; back = [bm.verts.new((x, -0.72, z)) for x, z in outline]
    bm.faces.new(front); bm.faces.new(back[::-1])
    for k in range(len(outline)):
        k1 = (k + 1) % len(outline)
        bm.faces.new([front[k], back[k], back[k1], front[k1]])
    return finish("Maulschnitt", bm, smooth=False)

def belly_w(z):
    return np.clip(0.17 + 0.16 * (0.5 - z) / 0.3, 0.17, 0.36)

def belly_mask(x, z):
    return smoothstep(0.03, -0.01, np.abs(x) - belly_w(z)) * smoothstep(0.1, 0.16, z) * smoothstep(0.51, 0.47, z + 0.25 * x * x)

def belly_folds(g):
    """Wenige breite, sanfte Bauchfalten (geformt, nicht nur gemalt)"""
    for v in g.data.vertices:
        if v.normal.y > -0.15 or v.co.y > -0.3:
            continue
        m = float(belly_mask(v.co.x, v.co.z)) * min(1.0, -v.normal.y * 1.6)
        if m <= 0:
            continue
        d = 0.0
        for zk in BELLY_Z:
            d += -0.003 * math.exp(-((v.co.z - (zk + 0.75 * v.co.x ** 2)) / 0.02) ** 2)
        v.co += v.normal * (d + 0.0015) * m

def paint_body(g, front):
    """Rosa Haut, heller Bauch mit Falten, heller Saum, dunkles Maul"""
    ao = vertex_ao(g, rays=14, dist=0.22)
    T = texels(g); P, N, cov = T["P"], T["N"], T["cov"]
    AO = texel_values(T, ao)
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    col = gradient((0.85, 0.37, 0.48), (0.9, 0.45, 0.55), smoothstep(0.1, 0.9, z))
    top = np.clip(N[..., 2], 0, 1) ** 2
    col = col * (1 - 0.25 * top[..., None]) + np.asarray((0.94, 0.55, 0.64), np.float32) * 0.25 * top[..., None]
    bm_ = belly_mask(x, z) * smoothstep(-0.1, -0.35, N[..., 1]) * (y < -0.3)
    belly = gradient((0.94, 0.63, 0.66), (0.92, 0.58, 0.63), smoothstep(0.15, 0.5, z))
    col = col * (1 - bm_[..., None]) + belly * bm_[..., None]
    fold = np.zeros_like(z)
    for zk in BELLY_Z:
        fold = np.maximum(fold, np.exp(-((z - (zk + 0.75 * x * x)) / 0.008) ** 2))
    col = col * (1 - 0.3 * (fold * bm_)[..., None]) + np.asarray((0.8, 0.4, 0.49), np.float32) * 0.3 * (fold * bm_)[..., None]
    hem = smoothstep(0.16, 0.05, z)
    col = col * (1 - 0.55 * hem[..., None]) + np.asarray((0.93, 0.58, 0.66), np.float32) * 0.55 * hem[..., None]
    occ = np.clip(AO * 1.6, 0, 1)
    col = col * (1 - 0.3 * occ[..., None]) + np.asarray((0.72, 0.26, 0.4), np.float32) * 0.3 * occ[..., None]
    # Maul: alles, was hinter der alten Vorderfläche im Schnitt liegt
    inside = (np.abs(x) < M_W + 0.01) & (z < mouth_top(x) + 0.012) & (z > mouth_low(x) - 0.012) & (y > front(x, z) + 0.012) & (y < -0.62)
    depth = smoothstep(0.0, 0.1, y - front(x, z))
    mcol = gradient((0.72, 0.2, 0.32), (0.5, 0.09, 0.19), depth)
    col = np.where(inside[..., None], mcol, col)
    T["out"][..., :3] = np.where(cov[..., None], np.clip(col, 0, 1), T["out"][..., :3])
    commit(T)

def front_map(bvh):
    """Lage der Vorderfläche des Kopfes rund ums Maul, vor dem Schnitt (für Maulfarbe und Zähne)"""
    xs = np.linspace(-0.3, 0.3, 61); zs = np.linspace(0.4, 0.75, 36)
    G = np.zeros((len(zs), len(xs)), np.float32)
    for i, z in enumerate(zs):
        for k, x in enumerate(xs):
            hit = bvh.ray_cast(Vector((x, -2.0, z)), Vector((0, 1, 0)), 3.0)[0]
            G[i, k] = hit.y if hit is not None else -0.6
    def front(x, z):
        fx = np.clip((np.asarray(x) - xs[0]) / (xs[1] - xs[0]), 0, len(xs) - 1.001); fz = np.clip((np.asarray(z) - zs[0]) / (zs[1] - zs[0]), 0, len(zs) - 1.001)
        ix = fx.astype(int); iz = fz.astype(int); tx = fx - ix; tz = fz - iz
        return (G[iz, ix] * (1 - tx) + G[iz, ix + 1] * tx) * (1 - tz) + (G[iz + 1, ix] * (1 - tx) + G[iz + 1, ix + 1] * tx) * tz
    return front

def tooth(name, base, h, r, mat):
    """kleiner stumpfer Kristallzahn"""
    bm = bmesh.new(); b = Vector(base)
    eq = [bm.verts.new(b + Vector((r * math.cos(q), r * 0.8 * math.sin(q), h * 0.3))) for q in [math.pi / 4 + k * math.pi / 2 for k in range(4)]]
    tip = bm.verts.new(b + Vector((0, 0, h))); low = bm.verts.new(b + Vector((0, 0, -h * 0.5)))
    for k in range(4):
        bm.faces.new([eq[k], eq[(k + 1) % 4], tip]); bm.faces.new([eq[(k + 1) % 4], eq[k], low])
    return give(finish(name, bm, smooth=False), mat)

def diadem(bvh, gold, ruby):
    """Gold-Diadem: Reif fest um den Kopf (die Augenstiele stehen darin), vorn ein Schild mit Rubin"""
    cy = -0.58; n = 96; pts = []
    for k in range(n):
        phi = k * 2 * math.pi / n
        d = Vector((math.sin(phi), -math.cos(phi), 0))
        z = 0.775 - 0.025 * math.cos(phi)
        hit = bvh.ray_cast(Vector((0, cy, z)) + d * 1.2, -d, 1.5)[0]
        pts.append(((hit - Vector((0, cy, z))).length if hit is not None else 0.2, z, d))
    rad = np.asarray([p[0] for p in pts])
    for _ in range(6):
        rad = 0.25 * np.roll(rad, 1) + 0.5 * rad + 0.25 * np.roll(rad, -1)
    P = [Vector((0, cy, z)) + d * (r + 0.004) for r, (_, z, d) in zip(rad, pts)]
    N = [d for _, _, d in pts]
    # Reif: flaches Band (hoch, dünn)
    bm = bmesh.new(); rings = []
    prof = [(0.02 * math.copysign(abs(math.cos(q)) ** 0.5, math.cos(q)), 0.036 * math.copysign(abs(math.sin(q)) ** 0.5, math.sin(q))) for q in [k * 2 * math.pi / 12 for k in range(12)]]
    for i in range(n):
        t = (P[(i + 1) % n] - P[(i - 1) % n]).normalized()
        out = Vector((t.y, -t.x, 0)).normalized()
        if out.dot(N[i]) < 0:
            out = -out
        up = Vector((0, 0, 1))
        rings.append([bm.verts.new(P[i] + out * a + up * b) for a, b in prof])
    for i in range(n):
        a, b = rings[i], rings[(i + 1) % n]
        for k in range(12):
            bm.faces.new([a[k], a[(k + 1) % 12], b[(k + 1) % 12], b[k]])
    band = give(finish("Diademreif", bm), gold)
    # Schild vorn: liegt als ruhige, leicht gewölbte Platte auf dem Reif
    r0 = float(rad[0]) + 0.004; z0 = pts[0][1] + 0.008
    def plate(u, v, lift):
        a = u / r0
        return Vector(((r0 + lift) * math.sin(a), cy - (r0 + lift) * math.cos(a) + 0.12 * v, z0 + v))
    outline = [(0, 0.115), (0.052, 0.064), (0.104, 0.034), (0.104, -0.034), (0.052, -0.058), (0, -0.1), (-0.052, -0.058), (-0.104, -0.034), (-0.104, 0.034), (-0.052, 0.064)]
    bm = bmesh.new()
    def loop(scale, lift):
        return [bm.verts.new(plate(u * scale, v * scale, lift)) for u, v in outline]
    a0 = loop(1.0, -0.01); a1 = loop(1.0, 0.016); a2 = loop(0.86, 0.026); c = bm.verts.new(plate(0, 0, 0.026))
    m = len(outline)
    for k in range(m):
        k1 = (k + 1) % m
        bm.faces.new([a0[k], a0[k1], a1[k1], a1[k]]); bm.faces.new([a1[k], a1[k1], a2[k1], a2[k]]); bm.faces.new([a2[k], a2[k1], c])
    shield = give(finish("Diademschild", bm, smooth=False), gold)
    hexa = [(0, 0.07), (0.05, 0.034), (0.05, -0.034), (0, -0.07), (-0.05, -0.034), (-0.05, 0.034)]
    bm = bmesh.new()
    g0 = [bm.verts.new(plate(u, v, 0.02)) for u, v in hexa]; g1 = [bm.verts.new(plate(u, v, 0.03)) for u, v in hexa]
    g2 = [bm.verts.new(plate(u * 0.55, v * 0.62, 0.046)) for u, v in hexa]; gc = bm.verts.new(plate(0, 0, 0.046))
    for k in range(6):
        k1 = (k + 1) % 6
        bm.faces.new([g0[k], g0[k1], g1[k1], g1[k]]); bm.faces.new([g1[k], g1[k1], g2[k1], g2[k]]); bm.faces.new([g2[k], g2[k1], gc])
    stone = give(finish("Diademrubin", bm, smooth=False), ruby)
    return [band, shield, stone]

def eyes(M):
    """Genau zwei Augen, oben auf den Stielen: große helle Augenfläche im rosa Rand, dunkle Pupille, schwere Braue"""
    parts = []
    for s in (1, -1):
        bc = STALK[s][2]
        wc = bc + Vector((-0.013 * s, -0.042, -0.004)); wr = 0.135
        parts.append(give(sphere("Augenweiss%d" % s, tuple(wc), wr, segs=(32, 16)), M["white"]))
        d = Vector((-0.3 * s, -1.0, -0.14)).normalized()
        pup = sphere("Pupille%d" % s, (0, 0, 0), 0.062, (1, 1, 0.42), segs=(24, 12))
        pup.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); pup.location = wc + d * (wr - 0.014)
        parts.append(give(pup, M["black"]))
        hd = (d + Vector((-0.2, 0.0, 0.28))).normalized()
        parts.append(give(sphere("Glanz%d" % s, tuple(wc + hd * (wr + 0.004)), 0.014, segs=(12, 8)), M["white"]))
        def on_bulb(x, z):
            dx, dz = x - bc.x, z - bc.z; rr = BULB_R + 0.014
            return Vector((x, bc.y - math.sqrt(max(rr * rr - dx * dx - dz * dz, 0.0016)), z))
        line = [on_bulb(s * 0.355, 1.215), on_bulb(s * 0.265, 1.245), on_bulb(s * 0.145, 1.21), on_bulb(s * 0.045, 1.14)]
        pts = [line[0] + (line[0] - line[1]).normalized() * 0.022] + line + [line[-1] + (line[-1] - line[-2]).normalized() * 0.02]
        parts.append(give(tube("Braue%d" % s, [tuple(p) for p in pts], [0.0, 0.03, 0.043, 0.046, 0.032, 0.0], segs=14), M["brow"]))
    return parts

# ---------------------------------------------------------------- Skelett und Bewegung

def shell_bone(arm):
    """Knochen „Haus“: starr, fährt nur mit dem gestauchten Rücken mit (kein Mitquetschen des Rosenquarzes)"""
    bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones.new("Haus"); eb.head = (0, SC[0], 0.3); eb.tail = (0, SC[0], 0.6); eb.parent = arm.data.edit_bones["Root"]
    bpy.ops.object.mode_set(mode='OBJECT')

def scale_curve(act, path, index, factor, neg_factor=None):
    for fc in act.fcurves:
        if fc.data_path == path and fc.array_index == index:
            for kp in fc.keyframe_points:
                for attr in ("co", "handle_left", "handle_right"):
                    v = getattr(kp, attr)
                    setattr(kp, attr, (v[0], v[1] * (neg_factor if neg_factor is not None and v[1] < 0 else factor)))
            fc.update()

def snail_motion(arm):
    """Gleiten statt Hüpfen, das Haus folgt dem Rücken, beim Angriff bäumt sich der Vorderkörper nur leicht zurück"""
    inv = arm.data.bones["Haus"].matrix_local.to_3x3().inverted()
    for act in bpy.data.actions:
        scale_curve(act, 'pose.bones["Root"].location', 1, 0.25 if act.name.startswith("Walk") else 0.5)
        if act.name.startswith("Attack"):         # Kopfstoß nach vorn nur halb so tief (der Kopf sitzt weit vorn), Aufbäumen etwas sanfter
            scale_curve(act, 'pose.bones["Top"].rotation_quaternion', 1, 0.5, neg_factor=0.75)
        sc = {fc.array_index: fc for fc in act.fcurves if fc.data_path == 'pose.bones["Body"].scale'}
        if not sc:
            continue
        f0, f1 = int(act.frame_range[0]), int(math.ceil(act.frame_range[1]))
        curves = [act.fcurves.new('pose.bones["Haus"].location', index=i, action_group="Haus") for i in range(3)]
        for f in range(f0, f1 + 1):
            sv = sc[1].evaluate(f) if 1 in sc else 1.0; sh = sc[0].evaluate(f) if 0 in sc else 1.0
            loc = inv @ Vector((0, SC[0] * (sh - 1), 0.3 * (sv - 1)))
            for i in range(3):
                curves[i].keyframe_points.insert(f, loc[i])

# ---------------------------------------------------------------- Aufbau

@variante("juwelen_schnecke", "schleimmutter")
def juwelenschnecke_neu(arm, body):
    remove_body(body)
    M = {
        "skin": image_material("Schneckenhaut", 2048, color=(0.87, 0.4, 0.5), rough=0.5),
        "shell": image_material("Rosenquarz", 1024, color=(0.92, 0.47, 0.6), rough=0.3),
        "gold": look("Gold", (1.0, 0.76, 0.3), rough=0.28, metal=0.9),
        "ruby": look("Rubin", (0.9, 0.06, 0.2), rough=0.08, emit=(0.8, 0.03, 0.14), strength=0.5),
        "white": look("Augenweiss", (0.97, 0.95, 1.0), rough=0.2),
        "black": look("Pupille", (0.03, 0.02, 0.04), rough=0.15),
        "brow": look("Braue", (0.5, 0.12, 0.3), rough=0.45),
        "tooth": look("Kristallzahn", (0.97, 0.96, 1.0), rough=0.1, emit=(0.8, 0.8, 0.9), strength=0.15),
    }
    # Körper
    g = body_shape()
    remesh_tilted(g, 0.012)
    md = g.modifiers.new("Glatt", 'SMOOTH'); md.factor = 0.5; md.iterations = 4; apply_mod(g, md)
    for v in g.data.vertices:
        v.co.z = max(v.co.z, 0.0)
    g.data.update(); bpy.context.view_layer.update()
    belly_folds(g)
    front = front_map(BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get()))
    cut = mouth_cut()
    md = g.modifiers.new("Maul", 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = cut; md.solver = 'EXACT'
    apply_mod(g, md); bpy.data.objects.remove(cut, do_unlink=True)
    remesh_tilted(g, 0.0105)
    # kräftig glätten: auf der fast senkrechten Bauchfläche hinterlässt das Raster sonst Treppenstufen (graue Streifen)
    md = g.modifiers.new("Glatt", 'SMOOTH'); md.factor = 0.5; md.iterations = 5; apply_mod(g, md)
    md = g.modifiers.new("Weniger", 'DECIMATE'); md.ratio = 0.2; apply_mod(g, md)
    for p in g.data.polygons:
        p.use_smooth = True
    g.data.materials.clear(); g.data.materials.append(M["skin"])
    smart_uv(g)
    paint_body(g, front)
    bvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    # Kopf: Augen, Diadem, Zähne (fest am Kopf)
    head = eyes(M) + diadem(bvh, M["gold"], M["ruby"])
    for i, x in enumerate((-0.118, -0.042, 0.042, 0.118)):
        z = float(mouth_low(x))
        head.append(tooth("Zahn%d" % i, (x, float(front(x, z - 0.03)) + 0.042, z - 0.012), 0.036, 0.028, M["tooth"]))
    head = join_parts(head, "Schneckenkopf")
    # Haus: geschlossener Körper, Goldspirale in der Rille, Rubine in Fassungen
    shell, dist = shell_mesh(M["shell"])
    paint_shell(shell, dist)
    sbvh = BVHTree.FromObject(shell, bpy.context.evaluated_depsgraph_get())
    house = [shell]
    for side in (1, -1):
        house.append(gold_spiral(side, M["gold"]))
        gy, gz = side_px(383, 377)
        P, N = shell_frames(np.asarray([[gy, gz]]), side)
        house += bezel_gem("Seitenrubin%d" % side, sbvh, P[0], N[0], (0, 0, 1), 0.12, 0.092, M["gold"], M["ruby"])
    ty, tz = side_px(602, 127)
    p, n = shell_tread(math.acos((ty - SC[0]) / SRY), 0.0)
    house += bezel_gem("Dachrubin", sbvh, p, n, (0, 1, 0), 0.17, 0.125, M["gold"], M["ruby"], segs=14)
    house = join_parts(house, "Schneckenhaus")
    shell_bone(arm)
    skin_to(g, arm, lambda c: (lambda t: {"Top": t, "Body": 1 - t})(smooth01((c.z - 0.22) / 0.3) * smooth01((-0.28 - c.y) / 0.22)))
    attach(head, arm, "Top")
    attach(house, arm, "Haus")
    dampen_scale(arm, ("Body", "Top"), 0.25)       # Körper staucht sich nur leicht
    snail_motion(arm)
    print("JUWELENSCHNECKE", len(g.data.polygons), "Flächen Körper,", len(house.data.polygons), "Haus,", len(head.data.polygons), "Kopf")

if __name__ == "__main__":
    run(VAR, OUT)
