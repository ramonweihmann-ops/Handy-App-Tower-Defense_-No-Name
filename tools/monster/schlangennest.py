# Monster der Welt „Schlangennest“ (Planet Schlangenhöhle, Boss Schlangenkönigin), Vorlage_Raw/Schlangennest_Monster_v1,
# vom Nutzer freigegeben 27.11.2026. Maßgeblich sind die Einzelblätter 02–04 und LIESMICH_CLAUDE.md.
#   nest_schleimling   Schlüpfling: Jungschlange in halber Eierschale (keine Gliedmaßen), Skelett Schleimling
#   nest_tentakler     Haubenflatterer: Schlange mit zwei großen Flügeln (keine Arme, keine Beine), Skelett Tentakler
#   nest_panzerkaefer  Schuppenpanzer: flache Echse mit drei Rückenplatten und genau vier Beinen, Skelett Panzerkäfer
# Gemeinsam: dunkelviolette Oberseite, heller Lavendelbauch, wenige breite magentafarbene Leuchtrisse (aufgemalt, keine
# Löcher), hellviolette Leuchtaugen, nichts schwebt. Gold nur am Schuppenpanzer.
# Aufruf: blender -b -P tools/monster/schlangennest.py -- <variante> <ziel.glb>
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kristallriese import *          # Metaballs, Bemalen (texels, vertex_ao, texel_values, smoothstep), image_material, smart_uv
from schlangenkoenigin import smooth3, mb_ball, remesh_tilted, key_rot
from mathutils import Euler, Matrix
import boss_aufsatz
boss_aufsatz.EXPORT_IMAGE_FORMAT = "JPEG"

SKIN_LO, SKIN_HI = (0.22, 0.1, 0.44), (0.36, 0.18, 0.64)       # Haut: Schattenseite, Lichtseite
BELLY_LO, BELLY_HI = (0.6, 0.5, 0.88), (0.78, 0.7, 0.98)        # Bauch
CRACK = (1.0, 0.36, 0.9)                                         # Leuchtriss
CRACK_EM = (0.95, 0.2, 0.8)

def f3(c):
    return np.asarray(c, np.float32)

def mix(col, other, m):
    return col * (1 - m[..., None]) + f3(other) * m[..., None]

def seg_dist(P, pts):
    """Abstand jedes Punktes zur Linie durch pts (Welt-Einheiten)"""
    best = np.full(P.shape[:-1], 9.0, np.float32)
    for a, b in zip(pts, pts[1:]):
        a = f3(a); b = f3(b); ab = b - a
        t = np.clip(((P - a) @ ab) / max(float(ab @ ab), 1e-9), 0, 1)
        best = np.minimum(best, np.linalg.norm(P - (a + t[..., None] * ab), axis=-1))
    return best

def crack_mask(P, lines, width):
    """Breite Zickzack-Risse: lines = [(Punkte, Breite am Anfang, Breite am Ende)], weich auslaufend"""
    m = np.zeros(P.shape[:-1], np.float32)
    for pts, w0, w1 in lines:
        n = len(pts) - 1
        for k, (a, b) in enumerate(zip(pts, pts[1:])):
            w = width * (w0 + (w1 - w0) * (k + 0.5) / n)
            m = np.maximum(m, np.clip(1.6 * (1 - seg_dist(P, [a, b]) / w), 0, 1))
    return m

def cast_pts(bvh, center, dirs, lift=0.0):
    """Punkte auf der Oberfläche: von außen entlang -dir auf center zu"""
    out = []
    for d in dirs:
        d = Vector(d).normalized()
        hit = bvh.ray_cast(Vector(center) + d * 3.0, -d, 6.0)[0]
        if hit is not None:
            out.append(tuple(hit + d * lift))
    return out

def groove(g, depth_fn):
    """Rille in die Haut drücken: depth_fn(Punkt, Flächenrichtung) -> Tiefe (0 = nichts)"""
    for v in g.data.vertices:
        d = depth_fn(v.co, v.normal)
        if d > 0:
            v.co -= v.normal * d
    g.data.update()

def snake_face(M, bvh, H, k, eye=(0.105, 0.0), eye_size=(0.075, 0.046), slant=24.0, fangs=(0.075, -0.07, 0.05), tongue=0.07, lid=(0.0, 0.8)):
    """Gesicht einer Schlange an der Kopfmitte H (Größe k): schräge Leuchtaugen mit hellem Kern, zwei Zähne,
    kurze gegabelte Zunge, Nasenlöcher. Alles liegt auf der Haut oder steckt im Maul."""
    parts = []
    def on(x, z, lift=0.0):
        hit, n, _, _ = bvh.ray_cast(Vector((H.x + x * k, H.y - 3.0, H.z + z * k)), Vector((0, 1, 0)), 6.0)
        return hit + n * lift, n
    for s in (1, -1):
        p, n = on(eye[0] * s, eye[1])
        yaw = math.atan2(n.x, -n.y); pitch = math.asin(max(-1.0, min(1.0, n.z)))
        rot = Euler((pitch * 0.7, math.radians(-slant * s), yaw * 0.9), 'XYZ')
        e = sphere("Auge%d" % s, (0, 0, 0), 1.0, (eye_size[0] * k, 0.028 * k, eye_size[1] * k), segs=(24, 14))
        for v in e.data.vertices:                                   # oben schräg abgeschnitten: innen tief, außen hoch (böser Blick)
            u = (v.co.x * s) / (eye_size[0] * k) * 0.5 + 0.5
            v.co.z = min(v.co.z, eye_size[1] * k * (lid[0] + (lid[1] - lid[0]) * u))
        e.rotation_euler = rot; e.location = p + Vector((0, 0.014 * k, 0))
        parts.append(give(e, M["eye"]))
        c = sphere("Augenkern%d" % s, (0, 0, 0), 1.0, (eye_size[0] * 0.4 * k, 0.026 * k, eye_size[1] * 0.4 * k), segs=(20, 12))
        c.rotation_euler = rot; c.location = p + Vector((-0.004 * s * k, 0.007 * k, -0.2 * eye_size[1] * k))
        parts.append(give(c, M["eyecore"]))
        if fangs:
            b, bn = on(fangs[0] * s, fangs[1])
            b = b + Vector((0, 0.004 * k, 0.012 * k))
            parts.append(give(tube("Zahn%d" % s, [tuple(b + Vector((0, 0.006 * k, 0.012 * k))), tuple(b), tuple(b + Vector((0, 0.002 * k, -fangs[2] * 0.5 * k))), tuple(b + Vector((0, 0.01 * k, -fangs[2] * k)))],
                                   [0.026 * k, 0.026 * k, 0.018 * k, 0.0], segs=12), M["fang"]))
        q, qn = on(0.03 * s, eye[1] - 0.045, 0.0)
        parts.append(give(sphere("Nase%d" % s, tuple(on(0.032 * s, -0.035)[0]), 0.009 * k, (1, 0.6, 1)), M["dark"]))
    if tongue:
        t0, tn = on(0.0, (fangs[1] if fangs else -0.07) - 0.012)
        t0 = t0 + Vector((0, 0.02 * k, 0))
        c0 = t0 + Vector((0, -0.036, -tongue * 0.42)) * k
        st = sphere("Zunge", (0, 0, 0), 1.0, (0.017 * k, 0.012 * k, tongue * 0.6 * k), segs=(16, 12))
        st.rotation_euler = Euler((math.radians(-24), 0, 0), 'XYZ'); st.location = c0
        parts.append(give(st, M["tongue"]))
        for s in (1, -1):                                           # zwei kurze Spitzen
            pr = sphere("Zungenspitze%d" % s, (0, 0, 0), 1.0, (0.009 * k, 0.009 * k, tongue * 0.42 * k), segs=(12, 10))
            pr.rotation_euler = Euler((math.radians(-24), math.radians(-32 * s), 0), 'XYZ')
            pr.location = c0 + Vector((0.018 * s, -0.018, -tongue * 0.72)) * k
            parts.append(give(pr, M["tongue"]))
    return parts

def snake_mats(size=1024):
    return {
        "skin": image_material("Schlangenhaut", size, color=(0.27, 0.13, 0.5), rough=0.38),
        "eye": look("Leuchtauge", (0.7, 0.56, 1.0), rough=0.2, emit=(0.66, 0.46, 1.0), strength=0.75),
        "eyecore": look("Augenkern", (0.97, 0.94, 1.0), rough=0.2, emit=(0.95, 0.9, 1.0), strength=1.5),
        "fang": look("Zahn", (0.97, 0.96, 1.0), rough=0.15),
        "tongue": look("Zunge", (0.98, 0.42, 0.85), rough=0.3, emit=(0.8, 0.2, 0.65), strength=0.35),
        "dark": look("Nasenloch", (0.08, 0.03, 0.14), rough=0.5),
        "lid": look("Lid", (0.29, 0.14, 0.55), rough=0.38),
        "gold": look("Gold", (1.0, 0.76, 0.26), rough=0.3, metal=0.85),
    }

def finish_skin(g, voxel, ratio, smooth_it=5):
    remesh_tilted(g, voxel)
    md = g.modifiers.new("Glatt", 'SMOOTH'); md.factor = 0.5; md.iterations = smooth_it; apply_mod(g, md)
    for v in g.data.vertices:
        v.co.z = max(v.co.z, 0.0)
    return g

def reduce(g, ratio):
    md = g.modifiers.new("Weniger", 'DECIMATE'); md.ratio = ratio; apply_mod(g, md)
    g.data.validate(clean_customdata=True); g.data.update()
    for p in g.data.polygons:
        p.use_smooth = True
    return g

def head_light(P, N, H, k):
    """Heller Glanzfleck oben auf dem Kopf (wie in der Vorlage)"""
    d = np.linalg.norm((P - f3(H + Vector((0, -0.03, 0.0)) * k)) / (f3((0.075, 0.05, 1.0)) * k), axis=-1)
    return np.clip(1 - d, 0, 1) ** 1.5 * (N[..., 2] > 0.75) * (P[..., 2] > H.z)

# ================================================================ Schlüpfling (leicht, Schleimling)

SC = Vector((0.0, 0.0, 0.265))                  # Mitte der Eierschale
SRX, SRZ, STH = 0.32, 0.27, 0.03               # Halbachsen und Wandstärke
SH = Vector((0.0, -0.03, 0.8))                 # Kopfmitte des Jungtiers
SK = 0.95                                       # Kopfgröße

def rim_z(phi):
    """Höhe der Bruchkante rundum (phi = 0 vorn): vorn tiefer, hinten höher, leicht unregelmäßig"""
    return 0.4 - 0.035 * math.cos(phi) + 0.012 * math.cos(3 * phi + 0.6) + 0.006 * math.sin(5 * phi)

def egg_shell():
    """Halbe Eierschale als ein zusammenhängender offener Körper mit Wandstärke und runder Bruchkante"""
    segs, n_out, n_in, n_rim = 44, 10, 4, 4
    bm = bmesh.new(); cols = []
    for k in range(segs):
        phi = k * 2 * math.pi / segs
        dx, dy = math.sin(phi), -math.cos(phi)
        th_r = math.acos(max(-1.0, min(1.0, (SC.z - rim_z(phi)) / SRZ)))
        col = []
        for i in range(1, n_out + 1):                               # außen von unten zur Kante
            th = th_r * i / n_out
            col.append(Vector((SRX * math.sin(th) * dx, SRX * math.sin(th) * dy, SC.z - SRZ * math.cos(th))))
        o = col[-1]
        inn = Vector(((SRX - STH) * math.sin(th_r) * dx, (SRX - STH) * math.sin(th_r) * dy, SC.z - (SRZ - STH) * math.cos(th_r)))
        mid = (o + inn) / 2; half = (o - inn) / 2; up = Vector((0, 0, 1))
        for i in range(1, n_rim):                                   # runde Kante
            a = math.pi * i / n_rim
            col.append(mid + half * math.cos(a) + up * (half.length * math.sin(a)))
        for i in range(n_in + 1):                                   # innen ein Stück hinunter (darunter liegt das Jungtier)
            th = th_r * (1 - 0.5 * i / n_in)
            col.append(Vector(((SRX - STH) * math.sin(th) * dx, (SRX - STH) * math.sin(th) * dy, SC.z - (SRZ - STH) * math.cos(th))))
        cols.append([bm.verts.new(p) for p in col])
    bottom = bm.verts.new((0, 0, SC.z - SRZ))
    for k in range(segs):
        a, b = cols[k], cols[(k + 1) % segs]
        bm.faces.new([bottom, b[0], a[0]])
        for i in range(len(a) - 1):
            bm.faces.new([a[i], b[i], b[i + 1], a[i + 1]])
    bm.faces.new([c[-1] for c in cols])
    o = finish("Eierschale", bm)
    for v in o.data.vertices:
        v.co.z = max(v.co.z, 0.0)
    return o

HATCH_NECK = [(0.0, 0.04, 0.26), (0.0, -0.03, 0.38), (0.0, -0.045, 0.5), (0.0, -0.01, 0.6), (0.0, 0.02, 0.69)]

def hatchling_shape():
    """Jungtier: eingerollter Körper füllt die Schale, kurzer gebogener Hals, großer runder Kopf"""
    R = mb_family("Jungtier")
    mb_ell(R, (0, 0, 0.2), (0.27, 0.27, 0.11))                                     # füllt die Schale unter der Windung
    for q in range(0, 360, 24):                                                    # Windung des Schwanzes
        a = math.radians(q)
        mb_ball(R, (0.16 * math.cos(a), 0.01 + 0.16 * math.sin(a), 0.27 + 0.01 * math.sin(a * 2)), 0.095)
    mb_caps(R, (0.0, 0.2, 0.31), (-0.13, 0.14, 0.325), 0.05)                       # Schwanzende liegt hinten obenauf
    P, _ = smooth3(HATCH_NECK, 14, passes=4)
    rr = np.interp(np.linspace(0, 1, 14), [0, 0.3, 0.75, 1], [0.175, 0.15, 0.13, 0.135])        # breiter, flacher Hals
    for p, r in zip(P, rr):
        mb_ell(R, tuple(p), (r, r * 0.66, r))
    k = SK; H = SH
    mb_ell(R, H, (0.25 * k, 0.24 * k, 0.205 * k))
    mb_ell(R, H + Vector((0, -0.15, -0.045)) * k, (0.165 * k, 0.115 * k, 0.08 * k))  # runde Schnauze
    mb_ell(R, H + Vector((0, -0.09, -0.12)) * k, (0.16 * k, 0.14 * k, 0.05 * k))     # Unterkiefer
    for s in (1, -1):
        mb_caps(R, H + Vector((0.035 * s, -0.19, 0.062)) * k, H + Vector((0.15 * s, -0.125, 0.11)) * k, 0.026 * k)   # Brauenwulst
        mb_ell(R, H + Vector((0.15 * s, -0.04, -0.05)) * k, (0.09 * k, 0.12 * k, 0.09 * k))                            # Wange
    return mb_to_mesh(R)

def hatch_mouth_z(x):
    """Maullinie: breites Grinsen, zu den Wangen hin ansteigend"""
    return SH.z + (-0.098 + 1.5 * (x / SK) ** 2) * SK

def hatch_neck_at(z):
    P = np.asarray(HATCH_NECK)
    return float(np.interp(z, P[:, 2], P[:, 1]))

def paint_hatchling(g):
    bvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    ao = vertex_ao(g, rays=14, dist=0.2)
    T = texels(g); P, N, cov = T["P"], T["N"], T["cov"]
    AO = texel_values(T, ao)
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    k = SK; H = SH
    # --- Bereiche
    e_out = np.linalg.norm((P - f3(SC)) / f3((SRX, SRX, SRZ)), axis=-1)
    e_in = np.linalg.norm((P - f3(SC)) / f3((SRX - STH, SRX - STH, SRZ - STH)), axis=-1)
    phi = np.arctan2(x, -y)
    rz = 0.4 - 0.035 * np.cos(phi) + 0.012 * np.cos(3 * phi + 0.6) + 0.006 * np.sin(5 * phi)
    shell = (e_in > 0.965) & (z < rz + 0.012)
    shell_inner = shell & (e_out < 0.955)
    head = (np.linalg.norm((P - f3(H)) / (f3((0.3, 0.3, 0.24)) * k), axis=-1) < 1.0) & ~shell
    # --- Haut
    col = gradient(SKIN_LO, SKIN_HI, np.clip(N[..., 2] * 0.5 + 0.55, 0, 1))
    em = np.zeros(P.shape, np.float32)
    # Bauch: Vorderseite des Halses und Unterkiefer
    cy = np.interp(z, np.asarray(HATCH_NECK)[:, 2], np.asarray(HATCH_NECK)[:, 1])
    front = -(y - cy) / np.maximum(np.sqrt((y - cy) ** 2 + x * x), 1e-4)
    neck = (z > 0.29) & (z < H.z - 0.06 * k) & ~shell
    belly = smoothstep(0.34, 0.5, front) * neck
    zm = H.z + (-0.098 + 1.5 * (x / k) ** 2) * k
    hd = np.linalg.norm((P - f3(H)) / (f3((0.3, 0.3, 0.24)) * k), axis=-1)
    jaw = smoothstep(1.0, 0.9, hd) * (~shell) * smoothstep(0.004, -0.012, z - zm) * smoothstep(H.y + 0.12 * k, H.y + 0.03 * k, y)
    jaw = jaw * smoothstep(0.25 * k, 0.19 * k, np.abs(x))
    bel = np.clip(np.maximum(belly, jaw), 0, 1)
    bcol = gradient(BELLY_LO, BELLY_HI, np.clip(0.5 - N[..., 1] * 0.6, 0, 1))
    band = np.abs((((z + 1.2 * x * x) / 0.052) % 1.0) - 0.5) * 2                  # Querbänder am Hals
    bline = smoothstep(0.72, 0.92, band) * belly * (1 - jaw)
    bcol = mix(bcol, (0.45, 0.33, 0.76), 0.75 * bline)
    col = mix(col, (0, 0, 0), np.zeros_like(bel)); col = col * (1 - bel[..., None]) + bcol * bel[..., None]
    # Maul: dunkle Linie in der Rille
    mouth = np.clip(1.4 * (1 - np.abs(z - zm) / (0.01 * k)), 0, 1) * head * (y < H.y - 0.03 * k) * smoothstep(0.19 * k, 0.16 * k, np.abs(x))
    col = mix(col, (0.1, 0.03, 0.18), mouth)
    # dunkler Rand um die Augen, damit sie sich abheben
    for s in (1, -1):
        d = np.linalg.norm((P - f3(H + Vector((0.112 * s, -0.2, 0.005)) * k)) / (f3((0.15, 0.14, 0.105)) * k), axis=-1)
        rim = np.clip(1.6 * (1 - d), 0, 1) * head * (1 - jaw)
        col = mix(col, (0.17, 0.07, 0.36), rim)
    col = mix(col, (0.6, 0.42, 0.95), 0.35 * head_light(P, N, H, k) * head)
    # --- Schale
    scol = gradient((0.3, 0.17, 0.55), (0.46, 0.3, 0.74), np.clip(N[..., 2] * 0.5 + 0.6 + 0.25 * (z - 0.1) / 0.3, 0, 1))
    scol = np.where(shell_inner[..., None], f3((0.24, 0.12, 0.45)), scol)
    col = np.where(shell[..., None], scol, col)
    # --- Leuchtrisse: auf der Schale (von der Kante abwärts) und hinten über Kopf und Hals
    def sp(deg, zz):                                                # Punkt auf der Schale: Winkel (0 = vorn), Höhe
        a = math.radians(deg); r = SRX * math.sqrt(max(0.0, 1 - ((zz - SC.z) / SRZ) ** 2))
        return (r * math.sin(a), -r * math.cos(a), zz)
    lines = [([sp(-38, 0.400), sp(-30, 0.335), sp(-46, 0.300), sp(-36, 0.235), sp(-50, 0.195), sp(-44, 0.135)], 1.0, 0.55),
             ([sp(-46, 0.300), sp(-64, 0.315), sp(-76, 0.280)], 0.8, 0.4),
             ([sp(34, 0.405), sp(42, 0.340), sp(27, 0.305), sp(38, 0.250), sp(24, 0.200)], 1.0, 0.5),
             ([sp(42, 0.340), sp(60, 0.335), sp(70, 0.365)], 0.8, 0.4),
             ([sp(118, 0.425), sp(126, 0.355), sp(110, 0.315), sp(124, 0.255), sp(112, 0.195)], 1.0, 0.5),
             ([sp(-150, 0.435), sp(-142, 0.365), sp(-158, 0.325), sp(-148, 0.265), sp(-160, 0.185)], 1.0, 0.5)]
    crack = crack_mask(P, lines, 0.019) * shell * (~shell_inner)
    back = []
    for bx, bz in ((0.03, H.z + 0.17 * k), (-0.035, H.z + 0.08 * k), (0.05, H.z - 0.02 * k), (-0.03, H.z - 0.11 * k), (0.04, 0.6), (-0.03, 0.52), (0.02, 0.44)):
        hit = bvh.ray_cast(Vector((bx, 3.0, bz)), Vector((0, -1, 0)), 6.0)[0]      # von hinten auf die Haut
        if hit is not None:
            back.append(tuple(hit))
    crack = np.maximum(crack, crack_mask(P, [(back, 1.0, 0.55)], 0.03) * (~shell) * (y > cy + 0.02) * (z > 0.42))
    col = mix(col, CRACK, crack)
    em += f3(CRACK_EM) * crack[..., None]
    occ = np.clip(AO * 1.7, 0, 1)
    col = mix(col, (0.14, 0.06, 0.3), 0.32 * occ * (1 - crack) * (1 - 0.7 * bel))
    T["out"][..., :3] = np.where(cov[..., None], np.clip(col, 0, 1), T["out"][..., :3])
    T["em"][..., :3] = np.where(cov[..., None], np.clip(em, 0, 1), 0)
    commit(T, strength=1.3)

@variante("nest_schleimling", "schleimling")
def schluepfling(arm, body):
    remove_body(body)
    M = snake_mats(1024)
    g = hatchling_shape()
    finish_skin(g, 0.009, 0.3)
    k = SK; H = SH
    def mouth_depth(co, n):
        if n.y > 0.2 or abs(co.x) > 0.2 * k or co.y > H.y - 0.03 * k or abs(co.z - H.z) > 0.2 * k:
            return 0.0
        d = abs(co.z - hatch_mouth_z(co.x)) / (0.016 * k)
        return 0.014 * k * (1 - d * d) * smooth01((0.2 * k - abs(co.x)) / (0.04 * k)) if d < 1 else 0.0
    groove(g, mouth_depth)
    reduce(g, 0.13)
    shell = egg_shell()
    g = join_parts([g, shell], "Schluepfling")
    for p in g.data.polygons:
        p.use_smooth = True
    g.data.materials.clear(); g.data.materials.append(M["skin"])
    smart_uv(g)
    paint_hatchling(g)
    bvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    parts = snake_face(M, bvh, H, k, eye=(0.115, 0.008), eye_size=(0.105, 0.074), slant=10.0, fangs=(0.075, -0.088, 0.055), tongue=0.06)
    g = join_parts([g] + parts, "Schluepfling")
    def weights(c):
        t = smooth01((c.z - 0.44) / 0.2)                            # Schale und Windung folgen dem Körper, Hals und Kopf dem Oberteil
        return {"Top": t, "Body": 1 - t}
    skin_to(g, arm, weights)
    dampen_scale(arm, ("Body", "Top"), 0.4)                         # die Schale ist hart: weniger quetschen
    print("SCHLUEPFLING", len(g.data.polygons), "Flächen")

# ================================================================ Haubenflatterer (mittel, Tentakler)

FH = Vector((0.0, -0.1, 1.27))                  # Kopfmitte
FK = 1.08                                       # Kopfgröße
# Mittellinie vom Kopfansatz zum eingerollten Schwanzende (x, y, z) und Dicke
FL_PTS = [(0.0, 0.0, 1.14), (0.0, 0.06, 0.98), (0.0, 0.05, 0.8), (0.0, -0.03, 0.62), (0.03, -0.09, 0.45), (0.1, -0.09, 0.29),
          (0.22, -0.05, 0.17), (0.36, 0.0, 0.17), (0.44, 0.03, 0.29), (0.4, 0.04, 0.42), (0.29, 0.04, 0.44), (0.24, 0.03, 0.35), (0.3, 0.02, 0.3)]
FL_R = [0.155, 0.165, 0.185, 0.195, 0.185, 0.165, 0.14, 0.115, 0.092, 0.072, 0.056, 0.044, 0.032]
FL_CL, FL_LEN = smooth3(FL_PTS, 120, passes=6)
FL_RAD = np.interp(np.linspace(0, 1, 120), np.linspace(0, 1, len(FL_R)), FL_R)
# Flügelrand von vorn gesehen (x, z), rechter Flügel: innen oben am Hals → Bogen → äußerste Stelle → untere Spitze → zurück zum Körper
WING_RIM = [(0.1, 1.08), (0.2, 1.36), (0.38, 1.58), (0.6, 1.66), (0.82, 1.58), (0.96, 1.36), (0.97, 1.1), (0.86, 0.86), (0.66, 0.68),
            (0.47, 0.56), (0.36, 0.62), (0.25, 0.7), (0.13, 0.78)]
WING_TIP = 9                                    # Index der unteren Spitze
WING_ROOT = (0.13, 0.95)                        # hier sitzt der Flügel am Körper
WING_Y = 0.13                                   # Flügel liegen hinter dem Körper

def wing_rim_path(side, n=90):
    P, _ = smooth3([(x * side, WING_Y, z) for x, z in WING_RIM], n, passes=3)
    t = np.linspace(0, 1, n)
    tip = WING_TIP / (len(WING_RIM) - 1)
    P[:, 1] += -0.05 * np.sin(np.pi * np.clip(t / tip, 0, 1)) + 0.03 * np.clip((t - tip) / (1 - tip), 0, 1)   # Rand wölbt sich nach vorn
    rad = np.interp(t, [0, 0.08, 0.3, tip * 0.92, tip, 1], [0.05, 0.062, 0.066, 0.05, 0.036, 0.03])
    return P, rad

def wing_rim(side):
    P, rad = wing_rim_path(side)
    pts = [tuple(P[0] + (P[0] - P[1]) * 0.5)] + [tuple(p) for p in P] + [tuple(P[-1] + (P[-1] - P[-2]) * 0.5)]
    return tube("Fluegelrand%d" % side, pts, [0.0] + list(rad) + [0.0], segs=14)

def wing_membrane(side, mem, rib):
    """Membran als gewölbte Fläche vom Körper zum Rand, mit Wandstärke; drei große Rippen liegen vorn auf"""
    P, _ = wing_rim_path(side, n=44)
    n = len(P); m = 8
    root = Vector((WING_ROOT[0] * side, WING_Y + 0.02, WING_ROOT[1]))
    def at(i, t):
        p = root.lerp(Vector(P[i]), t)
        p.y += 0.13 * math.sin(math.pi * min(1.0, t * 1.05)) ** 1.3 * (0.4 + 0.6 * math.sin(math.pi * i / (n - 1)))   # in der Mitte nach hinten gewölbt
        return p
    bm = bmesh.new()
    grid = [[bm.verts.new(at(i, j / m)) for j in range(1, m + 1)] for i in range(n)]
    c = bm.verts.new(root)
    for i in range(n - 1):
        a, b = grid[i], grid[i + 1]
        bm.faces.new([c, a[0], b[0]] if side > 0 else [c, b[0], a[0]])
        for j in range(m - 1):
            bm.faces.new([a[j], a[j + 1], b[j + 1], b[j]] if side > 0 else [a[j], b[j], b[j + 1], a[j + 1]])
    o = finish("Membran%d" % side, bm)
    md = o.modifiers.new("Dicke", 'SOLIDIFY'); md.thickness = 0.03; md.offset = 0.0; apply_mod(o, md)
    for p in o.data.polygons:
        p.use_smooth = True
    parts = [give(o, mem)]
    for t in (0.38, 0.58, 0.78):
        i0, i1 = int(n * 0.1), int(n * 0.78)
        pts = [at(i, t) + Vector((0, -0.016, 0)) for i in range(i0, i1, 2)]
        parts.append(give(tube("Rippe%d_%d" % (side, int(t * 100)), [tuple(q) for q in pts], [0.0] + [0.012] * (len(pts) - 2) + [0.0], segs=8), rib))
    return parts

def ring_tube(name, CL, RAD, segs=22, depth=1.0):
    """Schlauch mit genauer Dicke entlang einer Mittellinie (beide Enden rund geschlossen); depth staucht quer zur Breite"""
    bm = bmesh.new(); rings = []; n = len(CL)
    ref = Vector((1, 0, 0))
    for i in range(n):
        t = Vector(CL[min(i + 1, n - 1)] - CL[max(i - 1, 0)]).normalized()
        side = (ref - t * ref.dot(t))
        side = side.normalized() if side.length > 1e-3 else Vector((0, 1, 0))
        ref = side
        fwd = t.cross(side).normalized()
        c = Vector(CL[i]); r = float(RAD[i])
        rings.append([bm.verts.new(c + side * (r * math.cos(q)) + fwd * (r * depth * math.sin(q))) for q in [k * 2 * math.pi / segs for k in range(segs)]])
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(segs):
            bm.faces.new([r0[k], r0[(k + 1) % segs], r1[(k + 1) % segs], r1[k]])
    t0 = Vector(CL[0] - CL[1]).normalized(); t1 = Vector(CL[-1] - CL[-2]).normalized()
    a = bm.verts.new(Vector(CL[0]) + t0 * float(RAD[0]) * 0.8); b = bm.verts.new(Vector(CL[-1]) + t1 * float(RAD[-1]) * 0.9)
    for k in range(segs):
        bm.faces.new([a, rings[0][(k + 1) % segs], rings[0][k]])
        bm.faces.new([b, rings[-1][k], rings[-1][(k + 1) % segs]])
    o = finish(name, bm)
    bm2 = bmesh.new(); bm2.from_mesh(o.data); bmesh.ops.recalc_face_normals(bm2, faces=bm2.faces); bm2.to_mesh(o.data); bm2.free()
    return o

def flutter_shape():
    R = mb_family("Flatterer")
    k = FK; H = FH
    mb_ell(R, H, (0.25 * k, 0.24 * k, 0.2 * k))
    mb_ell(R, H + Vector((0, -0.15, -0.045)) * k, (0.165 * k, 0.115 * k, 0.08 * k))
    mb_ell(R, H + Vector((0, -0.09, -0.12)) * k, (0.16 * k, 0.14 * k, 0.05 * k))
    for s in (1, -1):
        mb_caps(R, H + Vector((0.035 * s, -0.19, 0.062)) * k, H + Vector((0.15 * s, -0.125, 0.11)) * k, 0.026 * k)
        mb_ell(R, H + Vector((0.15 * s, -0.04, -0.05)) * k, (0.09 * k, 0.12 * k, 0.09 * k))
        mb_ell(R, (0.15 * s, WING_Y - 0.02, 0.96), (0.1, 0.085, 0.16))            # kräftige Flügelwurzel
    return mb_to_mesh(R)

def tube_coords(P, CL, RAD, front=(0, -1, 0)):
    """Je Punkt: Lage entlang der Mittellinie (0..1), Abstand zur Mittellinie in Körperdicken und wie sehr er zur
    Bauchseite zeigt (-1..1; Bauch = front, quer zur Laufrichtung)"""
    Pf = P.reshape(-1, 3); n = len(CL)
    T = np.gradient(CL, axis=0); T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-9)
    F = np.asarray(front, np.float32)[None] - T * (T @ np.asarray(front, np.float32))[:, None]
    F /= np.maximum(np.linalg.norm(F, axis=1, keepdims=True), 1e-9)
    idx = np.zeros(len(Pf), np.int32)
    for a in range(0, len(Pf), 100000):
        d = np.linalg.norm(Pf[a:a + 100000, None, :] - CL[None].astype(np.float32), axis=-1) / RAD[None]
        idx[a:a + 100000] = np.argmin(d, axis=1)
    off = Pf - CL[idx].astype(np.float32)
    off -= T[idx] * np.sum(off * T[idx], axis=1, keepdims=True)
    dist = np.linalg.norm(off, axis=1)
    bel = np.sum(off * F[idx], axis=1) / np.maximum(dist, 1e-5)
    sh = P.shape[:-1]
    return (idx / (n - 1.0)).reshape(sh).astype(np.float32), (dist / RAD[idx]).reshape(sh).astype(np.float32), bel.reshape(sh).astype(np.float32)

def jaw_mask(P, H, k, shellfree=None):
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    zm = H.z + (-0.098 + 1.5 * ((x - H.x) / k) ** 2) * k
    hd = np.linalg.norm((P - f3(H)) / (f3((0.3, 0.3, 0.24)) * k), axis=-1)
    jaw = smoothstep(1.0, 0.9, hd) * smoothstep(0.004, -0.012, z - zm) * smoothstep(H.y + 0.12 * k, H.y + 0.03 * k, y)
    jaw = jaw * smoothstep(0.25 * k, 0.19 * k, np.abs(x - H.x))
    mouth = np.clip(1.4 * (1 - np.abs(z - zm) / (0.01 * k)), 0, 1) * (hd < 1.0) * (y < H.y - 0.03 * k) * smoothstep(0.19 * k, 0.16 * k, np.abs(x - H.x))
    return jaw, mouth, hd

def eye_rims(P, col, H, k, eye, size, keep):
    for s in (1, -1):
        d = np.linalg.norm((P - f3(H + Vector((eye[0] * s, -0.2, eye[1])) * k)) / (f3((size[0] * 1.45, 0.14, size[1] * 1.45)) * k), axis=-1)
        col = mix(col, (0.17, 0.07, 0.36), np.clip(1.6 * (1 - d), 0, 1) * keep)
    return col

def paint_flutter(g):
    bvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    ao = vertex_ao(g, rays=14, dist=0.25)
    T = texels(g); P, N, cov = T["P"], T["N"], T["cov"]
    AO = texel_values(T, ao)
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    k = FK; H = FH
    U, D, B = tube_coords(P, FL_CL, FL_RAD)
    jaw, mouth, hd = jaw_mask(P, H, k)
    head = hd < 1.0
    body = (D < 1.25) & ~head                                      # Schlangenkörper (nicht Flügelrand)
    col = gradient(SKIN_LO, SKIN_HI, np.clip(N[..., 2] * 0.5 + 0.55, 0, 1))
    em = np.zeros(P.shape, np.float32)
    belly = smoothstep(0.46, 0.6, B) * body * smoothstep(0.93, 0.8, U)            # Bauch bis kurz vor das Schwanzende
    bel = np.clip(np.maximum(belly, jaw), 0, 1)
    bcol = gradient(BELLY_LO, BELLY_HI, np.clip(0.5 - N[..., 1] * 0.6, 0, 1))
    band = np.abs(((U * FL_LEN / 0.075) % 1.0) - 0.5) * 2
    bline = smoothstep(0.74, 0.92, band) * belly * (1 - jaw)
    bcol = mix(bcol, (0.45, 0.33, 0.76), 0.75 * bline)
    col = col * (1 - bel[..., None]) + bcol * bel[..., None]
    col = mix(col, (0.1, 0.03, 0.18), mouth)
    col = eye_rims(P, col, H, k, (0.115, 0.008), (0.105, 0.074), head * (1 - jaw))
    col = mix(col, (0.6, 0.42, 0.95), 0.35 * head_light(P, N, H, k) * head)
    # Leuchtmarken: schräge Streifen auf dem Flügelrand, zwei Bänder am Schwanz, Zickzack den Rücken hinunter
    crack = np.zeros(P.shape[:-1], np.float32)
    rimzone = ~body & ~head
    for s in (1, -1):
        R, rr = wing_rim_path(s)
        Pf = P.reshape(-1, 3); ti = np.zeros(len(Pf), np.int32); td = np.zeros(len(Pf), np.float32)
        for a0 in range(0, len(Pf), 100000):
            dd = np.linalg.norm(Pf[a0:a0 + 100000, None, :] - R[None].astype(np.float32), axis=-1)
            ti[a0:a0 + 100000] = np.argmin(dd, axis=1); td[a0:a0 + 100000] = dd.min(axis=1)
        ti = ti.reshape(P.shape[:-1]); td = td.reshape(P.shape[:-1])
        onrim = (td < 0.085) & rimzone
        cross = z - R[ti][..., 2].astype(np.float32)                 # schräg über den Rand laufende Streifen
        for i0, hw in ((17, 2.3), (62, 2.0)):
            crack = np.maximum(crack, np.clip(1.6 * (1 - np.abs(ti - i0 - 30 * cross) / hw), 0, 1) * onrim)
    for u0 in (0.66, 0.84):                                        # Bänder am Schwanz
        crack = np.maximum(crack, np.clip(1.5 * (1 - np.abs(U - u0 - 0.03 * B) / 0.022), 0, 1) * body * (1 - belly))
    back = []
    for bx, bz in ((0.03, H.z + 0.15 * k), (-0.04, H.z + 0.04 * k), (0.04, H.z - 0.08 * k), (-0.03, 1.02), (0.04, 0.9), (-0.035, 0.78), (0.03, 0.66), (-0.02, 0.55)):
        hit = bvh.ray_cast(Vector((bx, 3.0, bz)), Vector((0, -1, 0)), 6.0)[0]
        if hit is not None:
            back.append(tuple(hit))
    crack = np.maximum(crack, crack_mask(P, [(back, 1.0, 0.6)], 0.032) * (N[..., 1] > 0.1) * (np.abs(x) < 0.14))
    col = mix(col, CRACK, crack)
    em += f3(CRACK_EM) * crack[..., None]
    occ = np.clip(AO * 1.7, 0, 1)
    col = mix(col, (0.14, 0.06, 0.3), 0.3 * occ * (1 - crack) * (1 - 0.7 * bel))
    T["out"][..., :3] = np.where(cov[..., None], np.clip(col, 0, 1), T["out"][..., :3])
    T["em"][..., :3] = np.where(cov[..., None], np.clip(em, 0, 1), 0)
    commit(T, strength=1.3)

WING_BONES = {-1: ("Bone_026", "Bone_025", "Bone_024", "Bone_023"), 1: ("Bone_031", "Bone_030", "Bone_029", "Bone_028")}

def flutter_weights(c):
    a = abs(c.x)
    if a < 0.2 or c.z < 0.5:                                        # Körper und Schwanz
        return {"Bone_001": 1.0}
    b = WING_BONES[1 if c.x > 0 else -1]
    t0 = smooth01((a - 0.22) / 0.3); t1 = smooth01((a - 0.58) / 0.2); t2 = smooth01((a - 0.86) / 0.2)
    w = {"Bone_001": 1 - t0, b[0]: t0 * (1 - t1), b[1]: t0 * t1 * (1 - t2), b[2]: t0 * t1 * t2}
    return {n: v for n, v in w.items() if v > 1e-4}

@variante("nest_tentakler", "tentakler")
def haubenflatterer(arm, body):
    remove_body(body)
    M = snake_mats(1024)
    M["membrane"] = look("Membran", (0.66, 0.56, 0.93), rough=0.45)
    M["rib"] = look("Rippe", (0.58, 0.47, 0.88), rough=0.45)
    g = join_parts([flutter_shape(), ring_tube("Koerper", FL_CL, FL_RAD, depth=0.9), wing_rim(1), wing_rim(-1)], "Haubenflatterer")
    finish_skin(g, 0.011, 0.3)
    k = FK; H = FH
    def mouth_depth(co, n):
        if n.y > 0.2 or abs(co.x) > 0.2 * k or co.y > H.y - 0.03 * k or abs(co.z - H.z) > 0.2 * k:
            return 0.0
        d = abs(co.z - (H.z + (-0.098 + 1.5 * (co.x / k) ** 2) * k)) / (0.016 * k)
        return 0.014 * k * (1 - d * d) * smooth01((0.2 * k - abs(co.x)) / (0.04 * k)) if d < 1 else 0.0
    groove(g, mouth_depth)
    reduce(g, 0.13)
    g.data.materials.clear(); g.data.materials.append(M["skin"])
    smart_uv(g)
    paint_flutter(g)
    bvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    parts = snake_face(M, bvh, H, k, eye=(0.115, 0.008), eye_size=(0.105, 0.074), slant=10.0, fangs=(0.075, -0.088, 0.06), tongue=0.065)
    for s in (1, -1):
        parts += wing_membrane(s, M["membrane"], M["rib"])
    g = join_parts([g] + parts, "Haubenflatterer")
    skin_to(g, arm, flutter_weights)
    print("HAUBENFLATTERER", len(g.data.polygons), "Flächen")

# ================================================================ Schuppenpanzer (stark, Panzerkäfer)

PH = Vector((0.0, -0.46, 0.34))                 # Kopfmitte
PK = 0.98                                       # Kopfgröße
PMZ = -0.098                                   # Höhe der Maullinie (in Kopfgrößen)
# Rückenplatten von vorn nach hinten: Mitte, Halbachsen, Neigung (Grad, vorn angehoben), Schnitthöhe (Anteil der Höhe)
PLATES = [((0.0, -0.03, 0.32), (0.365, 0.31, 0.38), -14.0, 0.0),
          ((0.0, 0.27, 0.29), (0.325, 0.23, 0.3), -16.0, 0.05),
          ((0.0, 0.47, 0.25), (0.25, 0.17, 0.22), -18.0, 0.1)]
# Beine an den vier Laufketten des Panzerkäfers (die mittleren Beine bleiben leer): Schulter, Knie, Fuß
LEGS = {"FL": ((-0.21, -0.16, 0.25), (-0.26, -0.19, 0.13), (-0.29, -0.21, 0.03)),
        "FR": ((0.21, -0.16, 0.25), (0.26, -0.19, 0.13), (0.29, -0.21, 0.03)),
        "BL": ((-0.22, 0.2, 0.24), (-0.27, 0.24, 0.13), (-0.3, 0.27, 0.03)),
        "BR": ((0.22, 0.2, 0.24), (0.27, 0.24, 0.13), (0.3, 0.27, 0.03))}

def plate_frame(i):
    c, rad, tilt, cut = PLATES[i]
    return Vector(c), Vector(rad), Matrix.Rotation(math.radians(tilt), 3, 'X'), cut

def plate_point(i, dx, dy):
    """Punkt außen auf Platte i: dx, dy in -1..1 (seitlich, nach hinten) über die Wölbung"""
    c, rad, rot, cut = plate_frame(i)
    dz = math.sqrt(max(0.0, 1 - dx * dx - dy * dy))
    return tuple(c + rot @ Vector((dx * rad.x, dy * rad.y, dz * rad.z)))

def plate(i):
    """Rückenplatte: gewölbte Schale mit Wandstärke, unten offen"""
    c, rad, rot, cut = plate_frame(i)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=16, radius=1.0)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < cut - 1e-4], context='VERTS')
    for v in bm.verts:
        v.co = c + rot @ Vector((v.co.x * rad.x, v.co.y * rad.y, v.co.z * rad.z))
    o = finish("Platte%d" % i, bm)
    md = o.modifiers.new("Dicke", 'SOLIDIFY'); md.thickness = 0.035; md.offset = -1.0; apply_mod(o, md)
    md = o.modifiers.new("Kante", 'BEVEL'); md.width = 0.012; md.segments = 2; md.limit_method = 'ANGLE'; md.angle_limit = math.radians(50); apply_mod(o, md)
    for p in o.data.polygons:
        p.use_smooth = True
    return o

def tag(o, value):
    """Teilnummer je Punkt merken (0 Körper, 1–3 Platten): bleibt beim Verbinden erhalten"""
    a = o.data.attributes.new("teil", 'FLOAT', 'POINT')
    a.data.foreach_set("value", [float(value)] * len(o.data.vertices))
    return o

def toe_points(c):
    fx = c[0]; fy = c[1] - 0.02
    return [(fx + dx, fy - 0.105 + 0.018 * abs(dx) / 0.062, 0.042) for dx in (-0.062, 0.0, 0.062)]

def armor_shape():
    R = mb_family("Echse")
    mb_ell(R, (0, 0.12, 0.275), (0.29, 0.39, 0.14))                                 # flacher, breiter Rumpf
    mb_caps(R, (0, -0.2, 0.28), (0, -0.32, 0.3), 0.14)                              # kurzer Hals
    k = PK; H = PH
    mb_ell(R, H, (0.26 * k, 0.25 * k, 0.175 * k))                                    # breiter, flacher Schlangenkopf
    mb_ell(R, H + Vector((0, -0.16, -0.04)) * k, (0.18 * k, 0.12 * k, 0.08 * k))     # Schnauze
    mb_ell(R, H + Vector((0, -0.1, -0.12)) * k, (0.175 * k, 0.15 * k, 0.055 * k))    # Unterkiefer
    for s in (1, -1):
        mb_caps(R, H + Vector((0.035 * s, -0.2, 0.05)) * k, H + Vector((0.15 * s, -0.135, 0.09)) * k, 0.024 * k)
        mb_ell(R, H + Vector((0.16 * s, -0.04, -0.05)) * k, (0.09 * k, 0.12 * k, 0.09 * k))
    for name, (a, b, c) in LEGS.items():                                              # vier kurze, kräftige Beine
        mb_caps(R, a, b, 0.1); mb_caps(R, b, (c[0], c[1], 0.08), 0.096)
        fx = c[0]; fy = c[1] - 0.02
        mb_ell(R, (fx, fy, 0.05), (0.1, 0.115, 0.055))                                # Fuß
        for q in toe_points(c):                                                       # drei stumpfe Zehen
            mb_ball(R, q, 0.044)
    for (a, b, r) in (((0, 0.44, 0.25), (0, 0.58, 0.2), 0.09), ((0, 0.58, 0.2), (0, 0.68, 0.18), 0.064), ((0, 0.68, 0.18), (0.02, 0.75, 0.23), 0.04)):
        mb_caps(R, a, b, r)                                                          # kurzer, dicker Schwanz, Spitze leicht angehoben
    return mb_to_mesh(R)

def leg_coords(P):
    """Je Punkt: gehört er zu einem Bein (0..1), Lage entlang des Beins (0 Schulter … 1 Fuß)"""
    m = np.zeros(P.shape[:-1], np.float32); tt = np.zeros(P.shape[:-1], np.float32)
    for name, (a, b, c) in LEGS.items():
        a = f3(a); c = f3((c[0], c[1], 0.0)); ac = c - a
        t = np.clip(((P - a) @ ac) / float(ac @ ac), 0, 1.2)
        d = np.linalg.norm(P - (a + t[..., None] * ac), axis=-1)
        w = smoothstep(0.17, 0.12, d) * (P[..., 2] < 0.27) * (np.sign(P[..., 0]) == np.sign(a[0]))
        tt = np.where(w > m, t, tt); m = np.maximum(m, w)
    return m, tt

def paint_armor(g):
    ao = vertex_ao(g, rays=14, dist=0.2)
    part_v = np.zeros(len(g.data.vertices), np.float32)
    g.data.attributes["teil"].data.foreach_get("value", part_v)
    T = texels(g); P, N, cov = T["P"], T["N"], T["cov"]
    AO = texel_values(T, ao); part = np.rint(texel_values(T, part_v)).astype(np.int32)
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    k = PK; H = PH
    is_plate = part > 0
    zm = H.z + (PMZ + 1.5 * (x / k) ** 2) * k
    hd = np.linalg.norm((P - f3(H)) / (f3((0.3, 0.3, 0.22)) * k), axis=-1)
    head = (hd < 1.0) & ~is_plate
    jaw = smoothstep(1.0, 0.9, hd) * smoothstep(0.004, -0.012, z - zm) * smoothstep(H.y + 0.14 * k, H.y + 0.05 * k, y) * smoothstep(0.26 * k, 0.2 * k, np.abs(x)) * (~is_plate)
    mouth = np.clip(1.4 * (1 - np.abs(z - zm) / (0.01 * k)), 0, 1) * head * (y < H.y - 0.03 * k) * smoothstep(0.2 * k, 0.17 * k, np.abs(x))
    leg, lt = leg_coords(P)
    leg = leg * (~is_plate)
    col = gradient(SKIN_LO, SKIN_HI, np.clip(N[..., 2] * 0.5 + 0.55, 0, 1))
    em = np.zeros(P.shape, np.float32)
    # heller Bauch: Unterseite des Rumpfes und ein Streifen an den Flanken, dazu Unterkiefer und Zehen
    under = smoothstep(0.31, 0.27, z + 0.1 * np.clip(N[..., 2], -1, 0)) * (y > -0.3) * (1 - leg) * (~is_plate) * (y < 0.56)
    toes = np.zeros(P.shape[:-1], np.float32)
    for name, (a, b, c) in LEGS.items():
        for q in toe_points(c):
            toes = np.maximum(toes, smoothstep(0.066, 0.052, np.linalg.norm(P - f3(q), axis=-1)))
    bel = np.clip(np.maximum(np.maximum(under, jaw), toes), 0, 1)
    bcol = gradient(BELLY_LO, BELLY_HI, np.clip(0.55 + N[..., 2] * 0.3 - N[..., 1] * 0.3, 0, 1))
    band = np.abs(((y / 0.07) % 1.0) - 0.5) * 2
    bcol = mix(bcol, (0.45, 0.33, 0.76), 0.6 * smoothstep(0.78, 0.94, band) * under * (1 - jaw))
    col = col * (1 - bel[..., None]) + bcol * bel[..., None]
    col = mix(col, (0.1, 0.03, 0.18), mouth)
    col = eye_rims(P, col, H, k, (0.115, 0.02), (0.1, 0.07), head * (1 - jaw))
    col = mix(col, (0.6, 0.42, 0.95), 0.35 * head_light(P, N, H, k) * head)
    # Platten: glänzendes Violett, oben heller, dunkle Unterkante
    pcol = gradient((0.25, 0.11, 0.5), (0.42, 0.22, 0.72), np.clip(N[..., 2] * 0.6 + 0.45, 0, 1))
    inner = np.zeros(P.shape[:-1], bool)
    for i in range(3):
        c, rad, rot, cut = plate_frame(i)
        L = (P - f3(c)) @ np.asarray(rot, np.float32)               # in die Lage der Platte gedreht
        e = np.linalg.norm(L / f3(rad), axis=-1)
        inner |= (part == i + 1) & (e < 0.93)
    pcol = np.where(inner[..., None], f3((0.16, 0.07, 0.34)), pcol)
    col = np.where(is_plate[..., None], pcol, col)
    # Leuchtrisse: je Platte ein breiter Zickzack, Bänder an den Beinen, Zeichen auf der hinteren Platte
    crack = np.zeros(P.shape[:-1], np.float32)
    zig = [[(-0.96, -0.25), (-0.6, 0.1), (-0.34, -0.16), (0.02, 0.18), (0.3, -0.08), (0.62, 0.26), (0.95, 0.05)],
           [(-0.95, 0.1), (-0.52, -0.16), (-0.22, 0.14), (0.15, -0.14), (0.48, 0.16), (0.94, -0.08)],
           [(-0.6, 0.5), (-0.35, 0.72), (0.0, 0.6), (0.35, 0.72), (0.6, 0.5)]]
    for i, pts in enumerate(zig):
        line = [plate_point(i, dx, dy) for dx, dy in pts]
        crack = np.maximum(crack, crack_mask(P, [(line, 1.0, 0.8)], 0.03 if i < 2 else 0.024) * (part == i + 1) * (~inner))
    crack = np.maximum(crack, np.clip(1.5 * (1 - np.abs(lt - 0.4) / 0.11), 0, 1) * (leg > 0.6) * (1 - toes))
    col = mix(col, CRACK, crack)
    em += f3(CRACK_EM) * crack[..., None]
    occ = np.clip(AO * 1.7, 0, 1)
    col = mix(col, (0.14, 0.06, 0.3), 0.3 * occ * (1 - crack) * (1 - 0.7 * bel))
    T["out"][..., :3] = np.where(cov[..., None], np.clip(col, 0, 1), T["out"][..., :3])
    T["em"][..., :3] = np.where(cov[..., None], np.clip(em, 0, 1), 0)
    commit(T, strength=1.3)

def armor_weights(arm):
    bones = {n: [Vector(arm.data.bones["Leg%s_%s" % (n, part)].head_local) for part in ("Up", "Lo")] for n in LEGS}
    def w(c):
        if c.z > 0.29 or abs(c.x) < 0.1 or c.y < -0.33:
            hw = smooth01((-0.25 - c.y) / 0.08) if c.z < 0.44 and abs(c.x) < 0.27 and c.y < -0.2 else 0.0   # Kopf folgt dem Kopfknochen
            if c.y > -0.36 and c.z > 0.4:
                hw = 0.0                                             # die vordere Platte bleibt am Rumpf
            return {"Head": hw, "Body": 1 - hw} if hw > 0 else {"Body": 1.0}
        best = None
        for n, (a, b, f) in LEGS.items():
            if (c.x > 0) != (a[0] > 0):
                continue
            a = Vector(a); f = Vector((f[0], f[1], 0.0)); af = f - a
            t = max(0.0, min(1.2, (Vector(c) - a).dot(af) / af.length_squared))
            d = (Vector(c) - (a + af * t)).length
            if best is None or d < best[0]:
                best = (d, n, t)
        d, n, t = best
        if d > 0.18 or c.z > 0.29:
            return {"Body": 1.0}
        up = smooth01((t - 0.02) / 0.3); lo = smooth01((t - 0.42) / 0.25)
        out = {"Body": 1 - up, "Leg%s_Up" % n: up * (1 - lo), "Leg%s_Lo" % n: up * lo}
        return {q: v for q, v in out.items() if v > 1e-4}
    return w

@variante("nest_panzerkaefer", "panzerkaefer")
def schuppenpanzer(arm, body):
    remove_body(body)
    M = snake_mats(1024)
    g = armor_shape()
    finish_skin(g, 0.009, 0.3)
    k = PK; H = PH
    def mouth_depth(co, n):
        if n.y > 0.2 or abs(co.x) > 0.21 * k or co.y > H.y - 0.03 * k or abs(co.z - H.z) > 0.2 * k:
            return 0.0
        d = abs(co.z - (H.z + (PMZ + 1.5 * (co.x / k) ** 2) * k)) / (0.016 * k)
        return 0.013 * k * (1 - d * d) * smooth01((0.21 * k - abs(co.x)) / (0.04 * k)) if d < 1 else 0.0
    groove(g, mouth_depth)
    reduce(g, 0.13)
    tag(g, 0)
    g = join_parts([g] + [tag(plate(i), i + 1) for i in range(3)], "Schuppenpanzer")
    for p in g.data.polygons:
        p.use_smooth = True
    g.data.materials.clear(); g.data.materials.append(M["skin"])
    smart_uv(g)
    paint_armor(g)
    bvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    parts = snake_face(M, bvh, H, k, eye=(0.115, 0.02), eye_size=(0.1, 0.07), slant=8.0, fangs=(0.085, PMZ + 0.01, 0.055), tongue=0)
    for i, (dx, dy) in ((0, (0.985, 0.42)), (1, (0.985, 0.3))):     # goldene Befestigungen fest auf den Platten
        for s in (1, -1):
            c, rad, rot, cut = plate_frame(i)
            pt = c + rot @ Vector((dx * s * rad.x * 0.93, dy * rad.y, (cut + 0.14) * rad.z))
            out = Vector((s, 0, 0.15)).normalized()
            parts.append(give(sphere("Niet%d_%d" % (i, s), tuple(pt + out * 0.012), 0.05, (0.55, 1, 1)), M["gold"]))
            parts.append(give(sphere("Nietkopf%d_%d" % (i, s), tuple(pt + out * 0.04), 0.026), M["gold"]))
    g = join_parts([g] + parts, "Schuppenpanzer")
    skin_to(g, arm, armor_weights(arm))
    print("SCHUPPENPANZER", len(g.data.polygons), "Flächen")

if __name__ == "__main__":
    run(VAR, OUT)
