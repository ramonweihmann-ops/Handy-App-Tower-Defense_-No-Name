# Sturmwolke neu (Kommentar 25.11.2026 im Mockup „Alle Bosse“: Maul sitzt komisch, billige runde Formen, die nicht
# ineinander übergehen, Blitze nicht ordentlich dran – Detailtiefe wie bei Schrottkoloss und Fabrikmutter).
# Eine zusammenhängende Gewitterwolke statt einzelner Kugeln: Metaball-Körper mit vielen Quellwolken (Blumenkohl),
# oben hell, unten dunkel, in den Mulden schattiert, innen zuckende Blitzadern. Gesicht in die Wolke geformt: tiefe
# Augenhöhlen mit glühenden Augen und schrägen Wolkenlidern, dicke Wolkenbrauen, ins Gesicht geschnittenes Maul mit
# Wolkenlippen, kantigen Hagelzähnen, glühendem Schlund und einer Blitzzunge. Blitze wachsen aus der Unterseite
# (verzweigt, scharfkantig, leuchtend). Skelett der Schleimmutter, ein zusammenhängendes Netz mit Gewichten nach Höhe.
# Aufruf: blender -b -P tools/monster/sturmwolke.py -- sturm_wolke <ziel.glb>
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kristallriese import *          # Metaballs, Bemalen (texels, vertex_ao, texel_values, smoothstep), image_material, smart_uv
import boss_aufsatz
boss_aufsatz.EXPORT_IMAGE_FORMAT = "JPEG"

FACE_Y = -0.5
EYE_Z, EYE_X = 0.665, 0.155
M_Z, M_A, M_BU, M_BL = 0.47, 0.25, 0.065, 0.105

def mb_ball(o, c, r):
    return mb_ell(o, c, (r, r, r))

def cloud_shape():
    """Wolke aus Metaballs: flacher dunkler Boden, darüber Quellwolken; vorn eine ruhigere Gesichtsfläche"""
    R = mb_family("Wolke")
    mb_ell(R, (0, 0.02, 0.52), (0.62, 0.44, 0.3))                  # Kern
    mb_ell(R, (0, 0.02, 0.33), (0.68, 0.47, 0.13))                 # flache Unterseite
    mb_ell(R, (0, -0.28, 0.56), (0.4, 0.2, 0.27))                  # Gesichtsfläche
    rnd = random.Random(1717)
    # große Quellwolken oben und an den Seiten, dazu viele kleine Wölbungen: deutlich plastischer Blumenkohl
    for count, rr, off, ph0 in ((26, (0.15, 0.25), 0.55, 0.05), (60, (0.06, 0.11), 0.75, -0.25)):
        placed = 0
        while placed < count:
            th = rnd.uniform(0, 2 * math.pi); ph = rnd.uniform(ph0, 1.4)
            n = Vector((math.cos(th) * math.cos(ph), math.sin(th) * math.cos(ph) * 0.75, math.sin(ph)))
            p = Vector((n.x * 0.6, 0.02 + n.y * 0.6, 0.52 + n.z * 0.3))
            if p.y < -0.22 and abs(p.x) < 0.42 and 0.33 < p.z < 0.88:
                continue                                             # Gesicht frei halten
            r = rnd.uniform(*rr) * (1.0 + 0.3 * max(0.0, n.z))
            mb_ball(R, p + n * r * off, r)
            placed += 1
    for k in range(14):                                              # unruhige Unterkante
        a = k * 2 * math.pi / 14 + rnd.uniform(-0.1, 0.1)
        mb_ball(R, (math.cos(a) * 0.62, 0.02 + math.sin(a) * 0.42, 0.3 + rnd.uniform(-0.02, 0.03)), rnd.uniform(0.07, 0.11))
    for s in (1, -1):
        mb_caps(R, (0.05 * s, FACE_Y + 0.03, 0.735), (0.29 * s, FACE_Y + 0.1, 0.81), 0.055)   # dicke Wolkenbraue (böser Blick)
        mb_ball(R, (0.3 * s, FACE_Y + 0.08, 0.84), 0.075)
        mb_ell(R, (0.27 * s, FACE_Y + 0.09, 0.5), (0.1, 0.09, 0.09))   # Backen
        mb_ell(R, (EYE_X * s, FACE_Y + 0.02, EYE_Z), (0.088, 0.065, 0.058), neg=True)      # Augenhöhle
    for k in range(36):                                              # Wolkenlippen rund ums Maul
        th = k * 2 * math.pi / 36; c, s_ = math.cos(th), math.sin(th)
        x = (M_A + 0.015) * math.copysign(abs(c) ** (2 / 2.4), c)
        z = ((M_BU if s_ > 0 else M_BL) + 0.018) * math.copysign(abs(s_) ** (2 / 2.4), s_)
        mb_ball(R, (x, FACE_Y + 0.02 + 0.12 * (x / M_A) ** 2, M_Z + z), 0.032 - 0.012 * (x / M_A) ** 2)
    return mb_to_mesh(R)

def mouth_section_c(y):
    t = np.clip((y - (FACE_Y + 0.04)) / 0.3, 0, 1)
    k = np.sqrt(np.clip(1 - t ** 2.2, 0, 1)) * 0.75 + 0.25 * (1 - t)
    return M_A * k, M_BU * (0.9 * k + 0.1), M_BL * k, M_Z

def mouth_in(P):
    a, bu, bl, zc = mouth_section_c(P[..., 1])
    dz = P[..., 2] - zc; b = np.where(dz > 0, bu, bl); e = 2.4
    return ((np.abs(P[..., 0]) / (a + 1e-6)) ** e + (np.abs(dz) / (b + 1e-6)) ** e) ** (1 / e)

def mouth_cut():
    bm = bmesh.new(); S = 48; rings = []
    for y in np.linspace(FACE_Y - 0.25, FACE_Y + 0.34, 14):
        a, bu, bl, zc = [float(v) for v in mouth_section_c(np.float32(y))]
        ring = []
        for k in range(S):
            th = k * 2 * math.pi / S; c, s = math.cos(th), math.sin(th)
            ring.append(bm.verts.new((a * math.copysign(abs(c) ** (2 / 2.4), c), y, zc + (bu if s > 0 else bl) * math.copysign(abs(s) ** (2 / 2.4), s))))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(S):
            bm.faces.new([r0[k], r0[(k + 1) % S], r1[(k + 1) % S], r1[k]])
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
    return finish("Maulschnitt", bm)

# ---------------------------------------------------------------- Blitze, Zähne, Zunge

def bolt_ribbon(name, top, down, length, width, rnd, mat, branch=True, thick=0.022):
    """Scharfkantiger Blitz als dickes Zickzack-Band (Stamm, optional ein Ast), oben in der Wolke verankert"""
    down = Vector(down).normalized(); side = down.cross(Vector((0, 0, 1)))
    if side.length < 1e-3:
        side = Vector((1, 0, 0))
    side.normalize(); nrm = side.cross(down).normalized()
    pts = [Vector(top)]; n = 6
    for i in range(1, n + 1):
        t = i / n
        off = side * length * 0.16 * (1 if i % 2 else -1) * rnd.uniform(0.6, 1.0) if i < n else Vector()
        pts.append(Vector(top) + down * length * t + off)
    def ribbon(pts, w0, w1):
        bm = bmesh.new(); L = len(pts); rows = []
        for i, p in enumerate(pts):
            t = i / (L - 1); w = w0 + (w1 - w0) * t
            d = (pts[min(i + 1, L - 1)] - pts[max(i - 1, 0)]).normalized(); sd = d.cross(nrm).normalized()
            rows.append([bm.verts.new(p + sd * w + nrm * thick), bm.verts.new(p - sd * w + nrm * thick),
                         bm.verts.new(p - sd * w - nrm * thick), bm.verts.new(p + sd * w - nrm * thick)])
        for r0, r1 in zip(rows, rows[1:]):
            for k in range(4):
                bm.faces.new([r0[k], r0[(k + 1) % 4], r1[(k + 1) % 4], r1[k]])
        bm.faces.new(list(reversed(rows[0]))); bm.faces.new(rows[-1])
        o = finish(name, bm, smooth=False)
        return give(o, mat)
    parts = [ribbon(pts, width, width * 0.12)]
    if branch:
        k = 3; a = pts[k]
        bd = (down * 0.7 + side * 0.7 * rnd.choice((-1, 1))).normalized()
        bpts = [a] + [a + bd * length * 0.42 * (i / 3) + side * length * 0.06 * (1 if i % 2 else -1) for i in range(1, 4)]
        parts.append(ribbon(bpts, width * 0.55, width * 0.08))
    return parts

def hail_tooth(name, base, d, L, r, mat, rnd):
    """Kantiger Hagelzahn: facettierte Spitze, etwas schief"""
    o = crystal(name, (0, 0, 0), L * 0.55, r)
    q = Vector((0, 0, 1)).rotation_difference(Vector(d).normalized()) @ Quaternion((0, 0, 1), rnd.uniform(0, 1))
    o.rotation_euler = (0, 0, 0)
    o.data.transform(q.to_matrix().to_4x4()); o.data.transform(Matrix.Translation(Vector(base)))
    return give(o, mat)

# ---------------------------------------------------------------- Variante

@variante("sturm_wolke", "schleimmutter")
def sturmwolke_neu(arm, body):
    remove_body(body)
    M = {
        "cloud": image_material("Gewitterwolke", 2048, rough=0.8),
        "eye": image_mat_glow("Blitzauge", (1.0, 0.92, 0.45), 4.0),
        "bolt": look("Blitz", (1.0, 0.76, 0.12), rough=0.3, emit=(1.0, 0.7, 0.1), strength=1.8),
        "core": image_mat_glow("Gewitterschlund", (1.0, 0.7, 0.25), 3.0),
        "hail": look("Hagel", (0.9, 0.95, 1.0), rough=0.15),
    }
    g = cloud_shape()
    remesh(g, 0.012)
    cut = mouth_cut()
    md = g.modifiers.new("Maul", 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = cut; md.solver = 'EXACT'
    apply_mod(g, md); bpy.data.objects.remove(cut, do_unlink=True)
    remesh(g, 0.011)
    md = g.modifiers.new("Glatt", 'SMOOTH'); md.factor = 0.5; md.iterations = 1; apply_mod(g, md)
    md = g.modifiers.new("Weniger", 'DECIMATE'); md.ratio = 0.3; apply_mod(g, md)
    for p in g.data.polygons:
        p.use_smooth = True
    bvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    # Augen in den Höhlen, darüber schräg geschnittene Wolkenlider
    eyes, lids = [], []
    for s in (1, -1):
        hit, n, _, _ = bvh.ray_cast(Vector((EYE_X * s, -2.0, EYE_Z)), Vector((0, 1, 0)), 4.0)
        f = (n * 0.4 + Vector((0, -1, 0)) * 0.6).normalized()
        lng = Vector((s * math.cos(math.radians(22)), 0, math.sin(math.radians(22)))); lng = (lng - f * lng.dot(f)).normalized()
        up = f.cross(lng) * s
        if up.z < 0:
            up = -up
        frame = (hit + f * (-0.012), f, lng, up, s)
        e = eye_shell("Auge%d" % s, frame, 0.072, 0.045, 0.035, uv=True); give(e, M["eye"]); eyes.append(e)
        lid = eye_shell("Lid%d" % s, frame, 0.072 * 1.15, 0.045 * 1.3, 0.035 * 1.5, keep=lambda lx, ly, lz: lz >= 0.12 + 0.42 * lx and ly > -0.6)
        md = lid.modifiers.new("Dicke", 'SOLIDIFY'); md.thickness = 0.01; md.offset = 1.0; apply_mod(lid, md)
        give(lid, M["cloud"]); lids.append(lid)
    # Wolke samt Lidern abwickeln und bemalen
    g.data.materials.clear(); g.data.materials.append(M["cloud"])
    bpy.ops.object.select_all(action='DESELECT')
    for o in lids:
        o.select_set(True)
    g.select_set(True); bpy.context.view_layer.objects.active = g; bpy.ops.object.join()
    smart_uv(g)
    paint_cloud(g)
    # Maul: Schlund, Hagelzähne, Blitzzunge
    rnd = random.Random(1718)
    parts = [g] + eyes
    core = sphere("Schlund", (0, FACE_Y + 0.26, M_Z), 1.0, (0.18, 0.04, 0.07)); give(core, M["core"]); parts.append(core)
    for top in (True, False):
        xs = (-0.19, -0.13, -0.065, 0.0, 0.065, 0.13, 0.19) if top else (-0.17, -0.1, -0.035, 0.035, 0.1, 0.17)
        for i, x in enumerate(xs):
            q = max(0.0, 1 - abs(x / M_A) ** 2.4) ** (1 / 2.4)
            z = M_Z + (M_BU if top else -M_BL) * q * 0.92
            y = FACE_Y + 0.05 + 0.12 * (x / M_A) ** 2
            L = (0.075 if abs(abs(x) - 0.13) < 0.01 else 0.05) * rnd.uniform(0.85, 1.1)
            parts.append(hail_tooth("Hagelzahn%s%d" % ("O" if top else "U", i), (x, y, z), (0.1 * x, -0.25, -1 if top else 1), L, 0.024, M["hail"], rnd))
    tongue = bolt_ribbon("Blitzzunge", Vector((0.02, FACE_Y + 0.12, M_Z - 0.02)), (0.15, -0.75, -0.55), 0.26, 0.045, rnd, M["bolt"], branch=False, thick=0.014)
    parts += tongue
    # Blitze aus der Unterseite: oben in der Wolke verankert
    for k, (x, y, L, d) in enumerate(((-0.34, -0.08, 0.5, (0.15, -0.05, -1)), (0.06, -0.18, 0.62, (-0.1, -0.1, -1)),
                                      (0.36, 0.04, 0.46, (-0.2, 0.0, -1)), (-0.08, 0.24, 0.42, (0.1, 0.1, -1)))):
        hit = bvh.ray_cast(Vector((x, y, -1.0)), Vector((0, 0, 1)), 4.0)[0]
        top_pt = (hit if hit is not None else Vector((x, y, 0.25))) + Vector((0, 0, 0.05))
        parts += bolt_ribbon("Blitz%d" % k, top_pt, d, L, 0.065, rnd, M["bolt"], thick=0.026)
    g = join_parts(parts, "Sturmwolke")
    skin_to(g, arm, lambda c: {"Top": smooth01((c.z - 0.3) / 0.3), "Body": 1 - smooth01((c.z - 0.3) / 0.3)})
    dampen_scale(arm, ("Body", "Top"), 0.5)
    print("STURMWOLKE", len(g.data.polygons), "Flächen")

def image_mat_glow(name, col, strength):
    return look(name, col, rough=0.3, emit=col, strength=strength)

def paint_cloud(g):
    """Oben hell, unten Gewittergrau, Mulden schattiert, innen zuckende Blitzadern, Maulraum dunkel"""
    ao = vertex_ao(g, rays=14, dist=0.25)
    T = texels(g); P, N, cov = T["P"], T["N"], T["cov"]
    AO = texel_values(T, ao)
    h = smoothstep(0.25, 0.95, P[..., 2])
    col = gradient((0.3, 0.35, 0.5), (0.97, 0.97, 1.0), h ** 0.8)
    col = col * (0.9 + 0.1 * fbm3(P, 7.0, 3, 3)[..., None])
    occ = np.clip(AO * 2.3, 0, 1)
    col = col * (1 - 0.62 * occ[..., None]) + np.asarray((0.2, 0.22, 0.4), np.float32) * (0.62 * occ[..., None])
    rim = np.clip(N[..., 2], 0, 1) * h
    col = col * (1 - 0.15 * rim[..., None]) + np.asarray((1.0, 1.0, 1.0), np.float32) * 0.15 * rim[..., None]
    em = np.zeros(P.shape, np.float32)
    veins = ridges(P, 4.0, 11, 0.028) ** 1.6 * np.clip((fbm3(P, 3.0, 12, 2) - 0.56) / 0.06, 0, 1) * (1 - smoothstep(0.5, 0.7, P[..., 2]))
    face = (P[..., 1] < -0.3) & (np.abs(P[..., 0]) < 0.4) & (P[..., 2] > 0.36) & (P[..., 2] < 0.86)
    veins = veins * (~face)
    col = col * (1 - veins[..., None]) + np.asarray((1.0, 0.95, 0.6), np.float32) * veins[..., None]
    em += np.asarray((1.0, 0.85, 0.3), np.float32) * veins[..., None]
    for s in (1, -1):                                               # Augenschein auf den Höhlenrändern
        d = np.linalg.norm(P - np.asarray((EYE_X * s, FACE_Y + 0.02, EYE_Z), np.float32), axis=-1)
        gl = np.clip(1 - d / 0.13, 0, 1) ** 2
        em += np.asarray((1.0, 0.85, 0.35), np.float32) * gl[..., None] * 0.35
    mi = mouth_in(P)
    inside = (mi < 1.04) & (P[..., 1] > FACE_Y - 0.03)
    depth = smoothstep(FACE_Y + 0.02, FACE_Y + 0.3, P[..., 1])
    mcol = gradient((0.3, 0.32, 0.5), (0.05, 0.05, 0.12), depth)
    col = np.where(inside[..., None], mcol, col)
    em = np.where(inside[..., None], np.asarray((0.5, 0.3, 0.08), np.float32) * smoothstep(0.5, 1.0, depth)[..., None], em)
    lip = np.clip(1 - np.abs(mi - 1.15) / 0.2, 0, 1) * (P[..., 1] < FACE_Y + 0.1) * (~inside)
    col = col * (1 - 0.3 * lip[..., None])
    T["out"][..., :3] = np.where(cov[..., None], np.clip(col, 0, 1), T["out"][..., :3])
    T["em"][..., :3] = np.where(cov[..., None], np.clip(em, 0, 1), 0)
    commit(T, strength=1.5)

if __name__ == "__main__":
    run(VAR, OUT)
