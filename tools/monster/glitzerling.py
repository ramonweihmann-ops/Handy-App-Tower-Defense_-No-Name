# Glitzerling neu (Kommentar 26.11.2026 im Mockup „Monster je Welt 3“: komplett überarbeiten, passt nicht zu den
# Comicfiguren, eckig-kantig; das Gesicht – Augen und Mund – gefällt; mehr Details, glatter und runder).
# Statt des geschliffenen Steins ein weicher, runder Tropfen aus Rosenquarz: glänzende Haut mit Verlauf und hellen
# Schlieren, eingerollte Locke obenauf mit Goldring und kleinem Rubin, runde Wangen, zwei kleine Füße (nichts schwebt),
# zwei runde goldene Flügelchen, Perlenkette mit Rubinanhänger. Das Gesicht bleibt: große dunkle Augen mit Glanzpunkt,
# schräge Brauen, schiefes Grinsen. Skelett des Schleimlings (hüpft wie er).
# Aufruf: blender -b -P tools/monster/glitzerling.py -- rosen_schleimling <ziel.glb>
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kristallriese import *          # Metaballs, Bemalen (texels, vertex_ao, texel_values, smoothstep), image_material, smart_uv
from mathutils import Euler
import boss_aufsatz
boss_aufsatz.EXPORT_IMAGE_FORMAT = "JPEG"

C = Vector((0.0, 0.0, 0.3))          # Mitte des Körpers
CURL = [((0.0, 0.0, 0.5), 0.1), ((0.0, 0.015, 0.585), 0.074), ((0.0, 0.05, 0.645), 0.055), ((0.0, 0.1, 0.672), 0.042), ((0.0, 0.147, 0.662), 0.034), ((0.0, 0.172, 0.63), 0.03)]

def mb_ball(o, c, r):
    return mb_ell(o, c, (r, r, r))

def drop_shape():
    R = mb_family("Glitzerling")
    mb_ell(R, C, (0.275, 0.255, 0.25))
    for c, r in CURL:                                               # Locke: nach hinten eingerollt
        mb_ball(R, c, r)
    for s in (1, -1):
        mb_ell(R, (0.11 * s, -0.09, 0.055), (0.075, 0.095, 0.05))   # Füße
        mb_ell(R, (0.165 * s, -0.16, 0.265), (0.055, 0.04, 0.045))  # runde Wangen
    return mb_to_mesh(R)

def remesh_tilted(o, voxel):
    """Neu vernetzen mit schräg gelegtem Raster (sonst Treppenstufen auf fast senkrechten Flächen)"""
    rot = Euler((0.31, 0.42, 0.23)).to_matrix().to_4x4()
    o.data.transform(rot); o.data.update()
    remesh(o, voxel)
    o.data.transform(rot.inverted()); o.data.update()

def star(P, c, size):
    """kleiner Glitzerstern (vier Strahlen) um den Punkt c auf der Haut, gemessen in der Bildebene x/z"""
    dx = np.abs(P[..., 0] - c[0]) / size; dz = np.abs(P[..., 2] - c[2]) / size
    near = (np.abs(P[..., 1] - c[1]) < size * 2.5)
    ray = np.clip(1 - (np.minimum(dx, dz) * 9 + np.maximum(dx, dz)), 0, 1)
    core = np.clip(1 - np.hypot(dx, dz) * 3.2, 0, 1)
    return np.maximum(ray, core) * near

def paint_drop(g):
    """Rosenquarz als Comic: oben hell, unten tiefes Rosa, helle Schlieren, Wangenrot, Glanzfleck und Glitzersterne"""
    ao = vertex_ao(g, rays=14, dist=0.2)
    T = texels(g); P, N, cov = T["P"], T["N"], T["cov"]
    AO = texel_values(T, ao)
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    h = smoothstep(0.02, 0.62, z + (fbm3(P, 3.0, 9, 2) - 0.5) * 0.12)
    col = gradient((0.86, 0.3, 0.55), (0.98, 0.56, 0.76), h)
    col = col * (1 - smoothstep(0.55, 1.0, h)[..., None] * 0.5) + np.asarray((1.0, 0.8, 0.9), np.float32) * smoothstep(0.55, 1.0, h)[..., None] * 0.5
    # helle Schlieren wie im Stein, weich und breit
    flow = fbm3(P * np.asarray((1.0, 1.0, 0.45), np.float32) + (fbm3(P, 2.5, 3, 2)[..., None] - 0.5) * 0.6, 5.0, 17, 3)
    vein = np.clip(1 - np.abs(flow - 0.5) / 0.09, 0, 1) ** 2
    col = col * (1 - 0.22 * vein[..., None]) + np.asarray((1.0, 0.82, 0.92), np.float32) * 0.22 * vein[..., None]
    deep = np.clip((0.4 - flow) / 0.15, 0, 1)
    col = col * (1 - 0.22 * deep[..., None]) + np.asarray((0.78, 0.22, 0.52), np.float32) * 0.22 * deep[..., None]
    front = np.clip(-N[..., 1], 0, 1)
    for s in (1, -1):                                               # Wangenrot
        d = np.hypot((x - 0.17 * s) / 0.075, (z - 0.25) / 0.05)
        k = np.clip(1 - d, 0, 1) ** 1.3 * front
        col = col * (1 - 0.6 * k[..., None]) + np.asarray((0.98, 0.32, 0.5), np.float32) * 0.6 * k[..., None]
    occ = np.clip(AO * 1.8, 0, 1)
    col = col * (1 - 0.35 * occ[..., None]) + np.asarray((0.66, 0.16, 0.42), np.float32) * 0.35 * occ[..., None]
    # Comic-Glanz: weicher heller Fleck oben links und drei Glitzersterne
    d = np.hypot((x + 0.12) / 0.085, (z - 0.44) / 0.045) + np.clip(y + 0.1, 0, 1) * 6
    gl = np.clip(1 - d, 0, 1) ** 0.8
    col = col * (1 - 0.75 * gl[..., None]) + 0.75 * gl[..., None]
    em = np.zeros(P.shape, np.float32)
    for c, size in (((0.19, -0.14, 0.42), 0.045), ((-0.21, -0.11, 0.2), 0.035), ((0.06, -0.2, 0.13), 0.028)):
        st = star(P, c, size) * (y < 0.0)
        col = col * (1 - st[..., None]) + st[..., None]
        em += st[..., None] * np.asarray((1.0, 0.9, 0.95), np.float32)
    T["out"][..., :3] = np.where(cov[..., None], np.clip(col, 0, 1), T["out"][..., :3])
    T["em"][..., :3] = np.where(cov[..., None], np.clip(em, 0, 1), 0)
    commit(T, strength=1.2)

def wing(name, s, mat):
    """rundes Flügelchen aus drei weichen Federlappen"""
    parts = []
    base = Vector((0.235 * s, 0.07, 0.33))
    for k, (ang, L, w) in enumerate(((38, 0.19, 0.075), (8, 0.17, 0.068), (-22, 0.14, 0.062))):
        a = math.radians(ang)
        d = Vector((s * math.cos(a) * 0.85, 0.45, math.sin(a))).normalized()
        o = sphere("%s%d" % (name, k), (0, 0, 0), 1.0, (L * 0.5, 0.022, w * 0.5), segs=(20, 12))
        o.rotation_euler = d.to_track_quat('X', 'Z').to_euler(); o.location = base + d * (L * 0.42)
        parts.append(give(o, mat))
    parts.append(give(sphere(name + "Ansatz", tuple(base), 0.04, (1, 0.7, 1)), mat))
    return parts

@variante("rosen_schleimling", "schleimling")
def glitzerling_neu(arm, body):
    remove_body(body)
    M = {
        "skin": image_material("Glitzerhaut", 1024, color=(0.94, 0.45, 0.68), rough=0.22),
        "gold": look("Gold", (1.0, 0.78, 0.32), rough=0.25, metal=0.9),
        "ruby": look("Rubin", (0.9, 0.08, 0.24), rough=0.08, emit=(0.8, 0.04, 0.16), strength=0.5),
        "pearl": look("Perle", (0.98, 0.94, 0.97), rough=0.2),
        "eye": look("Glitzeraugen", (0.08, 0.03, 0.08), rough=0.2),
        "shine": look("Glanzpunkt", (1, 1, 1), rough=0.2, emit=(1, 1, 1), strength=2.0),
    }
    g = drop_shape()
    remesh_tilted(g, 0.009)
    md = g.modifiers.new("Glatt", 'SMOOTH'); md.factor = 0.5; md.iterations = 6; apply_mod(g, md)
    for v in g.data.vertices:
        v.co.z = max(v.co.z, 0.0)
    md = g.modifiers.new("Weniger", 'DECIMATE'); md.ratio = 0.25; apply_mod(g, md)
    for p in g.data.polygons:
        p.use_smooth = True
    g.data.materials.clear(); g.data.materials.append(M["skin"])
    smart_uv(g)
    paint_drop(g)
    bvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    def on(x, z, lift=0.0):
        hit, n, _, _ = bvh.ray_cast(Vector((x, -2.0, z)), Vector((0, 1, 0)), 4.0)
        return hit + n * lift, n
    parts = []
    # Gesicht wie bisher: große dunkle Augen mit Glanzpunkt, schräge Brauen, schiefes Grinsen
    for s in (-1, 1):
        p, n = on(s * 0.068, 0.345)
        e = sphere("Auge%d" % s, (0, 0, 0), 0.038, (0.85, 0.34, 1.18), segs=(24, 14)); e.location = p + n * 0.004
        e.rotation_euler = (-n).to_track_quat('Y', 'Z').to_euler()
        parts.append(give(e, M["eye"]))
        parts.append(give(sphere("Glanz%d" % s, tuple(p + n * 0.014 + Vector((0.012, 0, 0.018))), 0.012), M["shine"]))
        parts.append(give(sphere("Glanzklein%d" % s, tuple(p + n * 0.014 + Vector((-0.01, 0, -0.016))), 0.006), M["shine"]))
        brow = [on(s * 0.118, 0.418, 0.006)[0], on(s * 0.07, 0.408, 0.008)[0], on(s * 0.026, 0.388, 0.006)[0]]
        ends = [brow[0] + (brow[0] - brow[1]).normalized() * 0.012] + brow + [brow[-1] + (brow[-1] - brow[-2]).normalized() * 0.01]
        parts.append(give(tube("Braue%d" % s, [tuple(q) for q in ends], [0.0, 0.011, 0.013, 0.01, 0.0], segs=10), M["eye"]))
    mouth = [on(-0.045, 0.262, 0.004)[0], on(-0.015, 0.25, 0.005)[0], on(0.02, 0.252, 0.005)[0], on(0.05, 0.272, 0.004)[0]]
    ends = [mouth[0] + (mouth[0] - mouth[1]).normalized() * 0.008] + mouth + [mouth[-1] + (mouth[-1] - mouth[-2]).normalized() * 0.008]
    parts.append(give(tube("Mund", [tuple(q) for q in ends], [0.0, 0.007, 0.009, 0.009, 0.007, 0.0], segs=10), M["eye"]))
    # Goldring um die Locke, vorn ein kleiner runder Rubin
    rc = Vector((0.0, 0.01, 0.545)); ring = []
    for k in range(40):                                             # Ring liegt rundum auf der Locke auf
        q = k * 2 * math.pi / 40
        d = Vector((math.cos(q), math.sin(q), 0))
        c0 = rc + Vector((0, 0, 0.012 * math.sin(q)))
        hit = bvh.ray_cast(c0 + d * 1.0, -d, 2.0)[0]
        ring.append(hit + d * 0.004)
    rr = (ring[30] - rc).length
    bm = bmesh.new(); loops = []
    for i, p in enumerate(ring):
        out = (p - rc); out.z = 0; out.normalize()
        loops.append([bm.verts.new(p + out * (0.012 * math.cos(q)) + Vector((0, 0, 0.02 * math.sin(q)))) for q in [k * 2 * math.pi / 10 for k in range(10)]])
    for i in range(40):
        a, b = loops[i], loops[(i + 1) % 40]
        for k in range(10):
            bm.faces.new([a[k], a[(k + 1) % 10], b[(k + 1) % 10], b[k]])
    parts.append(give(finish("Lockenring", bm), M["gold"]))
    parts.append(give(sphere("Lockenrubin", tuple(rc + Vector((0, -rr - 0.006, 0.0))), 0.026, (1, 0.6, 1), segs=(20, 12)), M["ruby"]))
    parts.append(give(sphere("Lockenfassung", tuple(rc + Vector((0, -rr - 0.001, 0.0))), 0.033, (1, 0.35, 1), segs=(20, 12)), M["gold"]))
    # Perlenkette mit Rubinanhänger: Perlen liegen auf der Haut
    for k in range(-15, 16):                                        # einmal rundum, hinten etwas höher
        if k == 0:
            continue
        a = k * math.pi / 15.5
        d = Vector((math.sin(a), -math.cos(a), 0))
        z = 0.16 + 0.07 * (1 - math.cos(a)) / 2
        hit, n, _, _ = bvh.ray_cast(Vector((0, 0, z)) + d * 2.0, -d, 4.0)
        parts.append(give(sphere("Perle%d" % k, tuple(hit + n * 0.008), 0.017, segs=(14, 10)), M["pearl"]))
    p, n = on(0.0, 0.152)
    parts.append(give(sphere("Anhaengerfassung", tuple(p + n * 0.002), 0.034, (1, 0.4, 1.15), segs=(20, 12)), M["gold"]))
    parts.append(give(sphere("Anhaenger", tuple(p + n * 0.008), 0.026, (1, 0.6, 1.15), segs=(20, 12)), M["ruby"]))
    for s in (1, -1):
        parts += wing("Fluegel%d_" % s, s, M["gold"])
    g = join_parts([g] + parts, "Glitzerling")
    skin_to(g, arm, lambda c: {"Top": smooth01((c.z - 0.02) / 0.13), "Body": 1 - smooth01((c.z - 0.02) / 0.13)})
    dampen_scale(arm, ("Body", "Top"), 0.55)
    print("GLITZERLING", len(g.data.polygons), "Flächen")

if __name__ == "__main__":
    run(VAR, OUT)
