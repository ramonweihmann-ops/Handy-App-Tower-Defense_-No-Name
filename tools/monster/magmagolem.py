# Magma-Golem neu (Entwurf „Kraterherz“ von ChatGPT, vom Nutzer freigegeben am 26.11.2026):
# Vorlage_Raw/Magmagolem_Neuentwurf_v1 (01_turnaround.png maßgeblich, 02_kopf_und_angriff.png, LIESMICH_CLAUDE.md).
# Gedrungener Gorilla-Golem aus zusammenhängenden, gerundeten Basaltformen (dunkles Anthrazitbraun, matt), mit breiten
# glühenden Lavarissen über Schultern, Arme, Beine, Rücken und Kopf, wenigen großen Schlackenporen, einer tiefen
# unregelmäßigen Kratermulde in der Brust mit glühendem Lavakern, schweren Gesteinsbrauen, orangegelben Augen mit
# dunklen Pupillen und einem schmalen, halb geschlossenen Comicmaul (Glut innen, zwei Basaltzähne).
# Maße aus dem Turnaround (Maßstab 0,0037 m je Bildpunkt, Vorlage zeigt die Gehhaltung).
# Skelett und Bewegungen des Koloss; Beine etwas weiter auseinander, Arme seitlich abgespreizt wie in der Vorlage.
# Haut aus Metaballs (Bone Heat, Rumpf gleichmäßig nach der Höhe), Krater, Maul und Poren ausgeschnitten,
# Lavarisse auf die Haut gemalt (eigene Abwicklung, Farbe und Leuchten).
# Aufruf: blender -b -P tools/monster/magmagolem.py -- magma_golem <ziel.glb>
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pilzriese import *              # Skelett-Hilfen (edit_bones, descendants, spread_arms), Formen, Hände, Gewichte
import boss_aufsatz
boss_aufsatz.EXPORT_IMAGE_FORMAT = "JPEG"

STUFE = os.environ.get("STUFE", "voll")
SCM = 0.0037                    # Meter je Bildpunkt der Vorlage (Schulterhöhe 358 px = 1,327 m in der Gehhaltung)
BACK_X = 1862                   # Mitte der Rückansicht in der Vorlage

def MV(px, py, sy=None):
    """Punkt aus der Vorderansicht (Bildpunkte) in die Ruhehaltung; sy = Bildpunkt in der Seitenansicht (Tiefe)"""
    y = 0.1 + (sy - 1395) * SCM if sy is not None else 0.0
    return Vector(((px - 318) * SCM, y, (638 - py) * SCM - DZW))

def MB(px, py):
    """Punkt aus der Rückansicht (Bildpunkte, Bild rechts = Körper rechts = -x)"""
    return Vector((-(px - BACK_X) * SCM, 0.0, (638 - py) * SCM - DZW))

M_HEAD = MV(318, 172, 1272)
M_HEAD_S = (0.285, 0.25, 0.215)

def lava_mats():
    def lava_img(name, n=512, seed=3, core=0.55):
        yy, xx = np.mgrid[0:n, 0:n]
        u = (xx + 0.5) / n * 2 - 1; v = (yy + 0.5) / n * 2 - 1
        r = np.sqrt(u * u + v * v)
        P = np.stack([u * 2.2, v * 2.2, np.full_like(u, seed * 0.31)], -1).astype(np.float32)
        nz = fbm3(P, 1.6, seed, 4)
        t = np.clip(1 - r / 1.0 + (nz - 0.5) * 0.7, 0, 1)
        col = gradient((0.75, 0.12, 0.02), (1.0, 0.5, 0.05), smoothstep(0.0, 0.45, t))
        col = col * (1 - smoothstep(0.45, 0.85, t)[..., None]) + np.asarray((1.0, 0.86, 0.25), np.float32) * smoothstep(0.45, 0.85, t)[..., None]
        blob = np.clip((fbm3(P, 3.2, seed + 9, 3) - 0.62) / 0.12, 0, 1) * (t > 0.35)
        col = col * (1 - 0.35 * blob[..., None]) + np.asarray((1.0, 0.42, 0.05), np.float32) * (0.35 * blob[..., None])
        arr = np.ones((n, n, 4), np.float32); arr[..., :3] = np.clip(col, 0, 1)
        m = bpy.data.materials.new(name); m.use_nodes = True
        nt = m.node_tree; p = nt.nodes["Principled BSDF"]
        tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = new_image(name + "_Bild", arr)
        nt.links.new(tex.outputs["Color"], p.inputs["Base Color"]); nt.links.new(tex.outputs["Color"], p.inputs["Emission Color"])
        p.inputs["Emission Strength"].default_value = 1.8; p.inputs["Roughness"].default_value = 0.4
        return m
    def eye():
        n = 256; yy, xx = np.mgrid[0:n, 0:n]
        u = (xx + 0.5) / n * 2 - 1; v = (yy + 0.5) / n * 2 - 1
        r = np.sqrt(u * u + v * v); pu, pv = 0.12, 0.0
        rp = np.sqrt((u - pu) ** 2 + (v - pv) ** 2)
        col = gradient((1.0, 0.92, 0.25), (1.0, 0.55, 0.05), smoothstep(0.2, 0.95, r))
        col = np.where((rp < 0.4)[..., None], np.asarray((0.85, 0.25, 0.04), np.float32), col)
        col = np.where((rp < 0.27)[..., None], np.asarray((0.08, 0.02, 0.01), np.float32), col)
        hl = np.sqrt((u - pu + 0.12) ** 2 + (v - pv - 0.12) ** 2) < 0.07
        col = np.where(hl[..., None], np.asarray((1.0, 0.97, 0.85), np.float32), col)
        col = np.where((r > 0.93)[..., None], np.asarray((0.25, 0.06, 0.02), np.float32), col)
        arr = np.ones((n, n, 4), np.float32); arr[..., :3] = col
        m = bpy.data.materials.new("Magmaauge"); m.use_nodes = True
        nt = m.node_tree; p = nt.nodes["Principled BSDF"]
        tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = new_image("Magmaauge_Bild", arr)
        nt.links.new(tex.outputs["Color"], p.inputs["Base Color"]); nt.links.new(tex.outputs["Color"], p.inputs["Emission Color"])
        p.inputs["Emission Strength"].default_value = 1.5; p.inputs["Roughness"].default_value = 0.2
        return m
    return {"skin": look("Basalt", (0.19, 0.15, 0.14), rough=0.85), "lava": lava_img("Lavakern"),
            "glut": look("Maulglut", (1.0, 0.62, 0.1), rough=0.5, emit=(1.0, 0.55, 0.08), strength=1.6), "eye": eye()}

# ---------------------------------------------------------------- Skelett

def widen_legs(arm, dx):
    """Beine samt Füßen seitlich nach außen setzen (Vorlage: breiter Stand)"""
    sets = {s: descendants(arm, "mixamorig:%sUpLeg" % s) for s in ("Left", "Right")}
    def fn(name, h, t):
        for s, sg in (("Left", 1), ("Right", -1)):
            if name in sets[s]:
                v = Vector((dx * sg, 0, 0))
                if name == "mixamorig:%sUpLeg" % s:
                    return h, t + v
                return h + v, t + v
        return h, t
    edit_bones(arm, fn)

# ---------------------------------------------------------------- Körper

CRATER = [(244, 272), (268, 252), (296, 268), (322, 252), (350, 266), (380, 250), (408, 272), (402, 302), (387, 332),
          (365, 352), (340, 368), (318, 375), (296, 366), (272, 348), (256, 322), (246, 294)]   # Umriss der Kratermulde (px)
MOUTH = [(262, 177), (290, 181), (318, 182), (346, 181), (372, 176), (368, 188), (346, 197), (318, 200), (290, 197), (268, 188)]
PORES = [("v", 205, 262, 0.062), ("v", 224, 306, 0.05), ("v", 438, 283, 0.06), ("v", 455, 333, 0.05), ("v", 96, 246, 0.062),
         ("v", 232, 340, 0.042), ("v", 418, 255, 0.04), ("v", 428, 362, 0.042), ("v", 214, 232, 0.035), ("v", 446, 306, 0.032),
         ("v", 545, 248, 0.058), ("v", 66, 352, 0.05), ("v", 584, 372, 0.046), ("v", 318, 392, 0.03),
         ("h", 1702, 212, 0.05), ("h", 1946, 198, 0.08), ("s", 1392, 232, 0.085), ("s", 1388, 356, 0.075)]

def outline_cutter(name, pts, z_of, front_y, depth, shrink=0.45, extra=0.3):
    """Schneidekörper aus einem Umriss der Vorderansicht: vorn voll, nach hinten zur Schüssel verjüngt"""
    P2 = [MV(px, py) for px, py in pts]
    c = sum(P2, Vector()) / len(P2)
    bm = bmesh.new(); rings = []
    for k in range(10):
        t = k / 9
        y = front_y - extra + (extra + depth) * t
        dd = max(0.0, (y - front_y - 0.07) / max(depth - 0.07, 1e-3))
        sc = 1.0 - (1 - shrink) * min(1.0, dd) ** 1.6
        rings.append([bm.verts.new((c.x + (p.x - c.x) * sc, y, c.z + (p.z - c.z) * sc)) for p in P2])
    n = len(P2)
    for a, b in zip(rings, rings[1:]):
        for k in range(n):
            bm.faces.new([a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]])
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finish(name, bm)

def magma_body(arm):
    T = mb_family("Rumpf")
    mb_ell(T, MV(318, 300, 1385), (0.5, 0.44, 0.33))               # breite, tiefe Brust
    mb_ell(T, MV(318, 255, 1455), (0.42, 0.3, 0.24))               # Nacken- und Rückenbuckel
    mb_ell(T, MV(318, 405, 1370), (0.42, 0.37, 0.22))              # Bauch
    mb_ell(T, MV(318, 462, 1390), (0.36, 0.3, 0.13))               # Becken
    for s in (1, -1):
        mb_ell(T, MV(318 + 118 * s, 228, 1405), (0.25, 0.26, 0.15))  # Kapuzenmuskel vom Kopf zur Schulter
    mb_ell(T, tuple(M_HEAD), M_HEAD_S)                             # Kopf, tief zwischen den Schultern und vorn
    mb_ell(T, MV(318, 212, 1255), (0.28, 0.24, 0.12))              # schwerer Unterkiefer
    for px, py, r in ((318, 100, 0.075), (290, 106, 0.066), (348, 104, 0.066), (264, 120, 0.06), (374, 118, 0.06), (318, 114, 0.07)):
        mb_ell(T, tuple(MV(px, py, 1310)), (r, r * 1.1, r))          # Höcker auf dem Kopf
    for s in (1, -1):
        bc = MV(318 + 42 * s, 140, 1216)
        mb_ell(T, tuple(bc), (0.125, 0.09, 0.07), Quaternion((0, 1, 0), math.radians(22 * s)))  # schwere, vorstehende Gesteinsbraue
    mb_ell(T, MV(318, 166, 1222), (0.06, 0.05, 0.045))             # Nase
    parts = []
    for side, s in (("Left", 1), ("Right", -1)):
        A_ = mb_family("Arm" + side)
        sh, el, wr = B(arm, side + "Arm"), B(arm, side + "ForeArm"), B(arm, side + "Hand")
        mb_ell(A_, tuple(sh + Vector((0.1 * s, 0.03, 0.06))), (0.31, 0.31, 0.3))      # große runde Schulter
        mb_caps(A_, sh, el, 0.19)
        c, semi, q = along(sh, el, 0.215, 0.22, 0.55); mb_ell(A_, c, semi, q)
        mb_caps(A_, el, wr, 0.19)
        c, semi, q = along(el, wr, 0.235, 0.22, 0.6); mb_ell(A_, c, semi, q)          # mächtiger Unterarm
        mb_ell(A_, tuple(wr), (0.15, 0.15, 0.15))
        parts.append(A_)
        L_ = mb_family("Bein" + side)
        up, kn, an = B(arm, side + "UpLeg"), B(arm, side + "Leg"), B(arm, side + "Foot")
        mb_caps(L_, up, kn, 0.22)
        mb_caps(L_, kn, an, 0.21)
        parts.append(L_)
        F_ = mb_family("Fuss" + side)
        fc = Vector((an.x + 0.02 * s, an.y - 0.14, 0.1))
        mb_ell(F_, tuple(fc), (0.26, 0.32, 0.12))
        mb_ell(F_, tuple(an + Vector((0, 0, -0.02))), (0.21, 0.21, 0.13))
        for x in (-0.17, -0.06, 0.06, 0.17):
            mb_ell(F_, tuple(fc + Vector((x, -0.28 + abs(x) * 0.3, -0.03))), (0.065, 0.08, 0.07))
        parts.append(F_)
    torso = mb_to_mesh(T)
    tbvh = BVHTree.FromObject(torso, bpy.context.evaluated_depsgraph_get())
    body = join_parts([torso] + [mb_to_mesh(o) for o in parts], "Magmagolem")
    remesh(body, 0.012)
    bvh0 = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())
    # Kratermulde, Maulspalt und Schlackenporen ausschneiden, danach glätten (weiche, runde Ränder)
    cy = front_hit(tbvh, MV(325, 315).x, MV(325, 315).z)[0].y
    my = front_hit(tbvh, 0, MV(318, 190).z)[0].y
    cutters = [outline_cutter("Krater", CRATER, None, cy, 0.2, shrink=0.6), outline_cutter("Maul", MOUTH, None, my, 0.12, shrink=0.85)]
    for kind, px, py, r in PORES:
        if kind == "v":
            p = MV(px, py); h = bvh0.ray_cast(Vector((p.x, -3, p.z)), Vector((0, 1, 0)), 6)
        elif kind == "h":
            p = MB(px, py); h = bvh0.ray_cast(Vector((p.x, 3, p.z)), Vector((0, -1, 0)), 6)
        else:
            p = MV(318, py, px); h = bvh0.ray_cast(Vector((3, p.y, p.z)), Vector((-1, 0, 0)), 6)
        if h[0] is None:
            continue
        n = h[1] if h[1].dot(h[0] - Vector((0, 0.1, h[0].z))) > 0 else -h[1]
        cutters.append(sphere("Pore", tuple(h[0] + n * r * 0.35), r, (1, 1, 1), segs=(20, 12)))
    for ct in cutters:
        md = body.modifiers.new("Schnitt", 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = ct; md.solver = 'EXACT'
        apply_mod(body, md)
        bpy.data.objects.remove(ct, do_unlink=True)
    remesh(body, 0.011)
    md = body.modifiers.new("Glatt", 'SMOOTH'); md.factor = 0.5; md.iterations = 4; apply_mod(body, md)
    md = body.modifiers.new("Weniger", 'DECIMATE'); md.ratio = 0.25; apply_mod(body, md)
    for p in body.data.polygons:
        p.use_smooth = True
    return body, tbvh, cy, my

def bind_magma(body, arm, tbvh):
    keep = {"mixamorig:" + b for b in MAIN_BONES}
    saved = {b.name: b.use_deform for b in arm.data.bones}
    for b in arm.data.bones:
        b.use_deform = b.name in keep
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    for b in arm.data.bones:
        b.use_deform = saved[b.name]
    torso_weights(body, tbvh)
    head = body.vertex_groups.get("mixamorig:Head") or body.vertex_groups.new(name="mixamorig:Head")
    for v in body.data.vertices:
        q = v.co - M_HEAD
        d = math.sqrt((q.x / 0.3) ** 2 + (q.y / 0.29) ** 2 + (q.z / 0.3) ** 2)
        h = smooth01((1.15 - d) / 0.25) * smooth01((v.co.z - (M_HEAD.z - 0.22)) / 0.08)
        if h <= 0:
            continue
        for g in v.groups:
            g.weight *= (1 - h)
        head.add([v.index], h, 'ADD')

# ---------------------------------------------------------------- Gesicht und Lava

def magma_eyes(bvh, M):
    out = []
    for s in (1, -1):
        p, n = front_hit(bvh, MV(318 + 37 * s, 152).x, MV(318, 152).z)
        nn = (n + Vector((0, -1, 0))).normalized()
        inner = Vector((-s, 0, 0)); inner = (inner - nn * inner.dot(nn)).normalized()
        up = nn.cross(inner).normalized()
        if up.z < 0:
            up = -up
        a, dd, b = 0.062, 0.028, 0.052
        e = sphere("Auge%d" % s, (0, 0, 0), 1.0, (1, 1, 1), segs=(32, 16))
        Fm = Matrix((inner * a, nn * dd, up * b)).transposed().to_4x4(); Fm.translation = p
        e.data.transform(Fm)
        me = e.data; me.uv_layers.new(name="UVMap"); uvl = me.uv_layers.active.data
        for poly in me.polygons:
            for li in poly.loop_indices:
                q = me.vertices[me.loops[li].vertex_index].co - p
                uvl[li].uv = (0.5 + 0.5 * q.dot(inner) / a, 0.5 + 0.5 * q.dot(up) / b)
        out.append(give(e, M["eye"]))
        lid = sphere("Lid%d" % s, (0, 0, 0), 1.0, (1, 1, 1), segs=(28, 14))      # Gesteinslid, innen tief: böser Blick
        rot = Matrix.Rotation(math.radians(-34), 3, nn)
        lx, lz = rot @ inner, rot @ up
        Fl = Matrix((lx * a * 1.25, nn * 0.036, lz * b * 0.72)).transposed().to_4x4()
        Fl.translation = p + up * b * 0.98 + inner * a * 0.3 + nn * 0.008
        lid.data.transform(Fl)
        out.append(give(lid, M["skin"]))
    return out

def mouth_fill(bvh, M, my):
    """Glut im Maulspalt (dahinter) und zwei Basaltzähne unten"""
    P2 = [MV(px, py) for px, py in MOUTH]
    c = sum(P2, Vector()) / len(P2)
    bm = bmesh.new()
    ring = [bm.verts.new((c.x + (p.x - c.x) * 0.98, my + 0.07, c.z + (p.z - c.z) * 0.98)) for p in P2]
    cen = bm.verts.new((c.x, my + 0.08, c.z))
    for k in range(len(ring)):
        bm.faces.new([cen, ring[(k + 1) % len(ring)], ring[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    glow = finish("Maulglut", bm, smooth=True)
    me = glow.data; me.uv_layers.new(name="UVMap"); uvl = me.uv_layers.active.data
    for poly in me.polygons:
        for li in poly.loop_indices:
            q = me.vertices[me.loops[li].vertex_index].co - c
            uvl[li].uv = (0.5 + q.x / 0.5, 0.5 + q.z / 0.18)
    give(glow, M["lava"])
    parts = [glow]
    for s in (1, -1):
        p, n = front_hit(bvh, MV(318 + 27 * s, 200).x, MV(318, 200).z)
        base = p + Vector((0, 0.015, 0.0))
        o = tube("Zahn%d" % s, [base, base + Vector((0, -0.006, 0.03)), base + Vector((0, -0.005, 0.05)), base + Vector((0, -0.004, 0.058))],
                 [0.032, 0.027, 0.016, 0.0], segs=12)
        smooth_obj(o, 70)
        parts.append(give(o, M["skin"]))
    return parts

def crater_pool(M, cy):
    """Unregelmäßiger, knotiger Lavakern am Grund der Kratermulde"""
    P2 = [MV(px, py) for px, py in CRATER]
    c = sum(P2, Vector()) / len(P2)
    bm = bmesh.new(); rings = []
    rng = random.Random(9)
    for j in range(1, 7):
        t = j / 6
        rings.append([bm.verts.new((c.x + (p.x - c.x) * 0.86 * t, cy + 0.12 - 0.03 * (1 - t) ** 2 + 0.03 * t ** 3 + rng.uniform(-0.008, 0.008),
                                    c.z + (p.z - c.z) * 0.86 * t)) for p in P2])
    cen = bm.verts.new((c.x, cy + 0.095, c.z))
    n = len(P2)
    for k in range(n):
        bm.faces.new([cen, rings[0][(k + 1) % n], rings[0][k]])
    for a, b in zip(rings, rings[1:]):
        for k in range(n):
            bm.faces.new([a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = finish("Lavakern", bm, smooth=True)
    md = o.modifiers.new("Glatt", 'SUBSURF'); md.levels = 2; apply_mod(o, md)
    me = o.data; me.uv_layers.new(name="UVMap"); uvl = me.uv_layers.active.data
    for poly in me.polygons:
        for li in poly.loop_indices:
            q = me.vertices[me.loops[li].vertex_index].co - c
            uvl[li].uv = (0.5 + q.x / 0.7, 0.5 + q.z / 0.55)
    smooth_obj(o, 80)
    return give(o, M["lava"])

def crack_lines(bvh):
    """Breite Lavarisse wie im Turnaround (Linien in Bildpunkten der Vorder- und Rückansicht, auf die Haut gelegt)"""
    def onto(pts, view, w):
        line = []
        xs = np.interp(np.linspace(0, len(pts) - 1, 60), np.arange(len(pts)), [p[0] for p in pts])
        ys = np.interp(np.linspace(0, len(pts) - 1, 60), np.arange(len(pts)), [p[1] for p in pts])
        for px, py in zip(xs, ys):
            if view == "v":
                p = MV(px, py); h = bvh.ray_cast(Vector((p.x, -3, p.z)), Vector((0, 1, 0)), 6)
            elif view == "h":
                p = MB(px, py); h = bvh.ray_cast(Vector((p.x, 3, p.z)), Vector((0, -1, 0)), 6)
            else:
                p = MV(318, py); h = bvh.ray_cast(Vector((p.x, -3, 3.0)), Vector((0, 0.6, -1)).normalized(), 9)
            if h[0] is not None:
                line.append((h[0], w))
        return line
    front = [
        [(224, 182), (196, 204), (170, 228), (146, 252), (118, 280), (96, 298), (74, 314), (60, 338), (52, 370), (46, 400), (36, 430), (30, 446)],
        [(60, 338), (80, 360), (104, 378), (128, 392), (150, 396)],
        [(406, 178), (428, 190), (452, 212), (482, 234), (512, 252), (532, 282), (546, 312), (540, 344), (530, 372), (546, 398), (570, 420), (592, 440)],
        [(532, 372), (510, 388), (486, 398), (466, 400)],
        [(190, 446), (212, 456), (240, 470), (256, 490), (250, 512), (230, 526), (196, 536), (164, 546)],
        [(426, 450), (404, 460), (380, 482), (370, 506), (386, 522), (420, 536), (446, 546), (462, 556)],
        [(246, 128), (258, 108), (276, 96)], [(362, 96), (380, 108), (392, 128)],
    ]
    back = [
        [(1600, 300), (1630, 250), (1668, 210), (1716, 176), (1760, 160), (1800, 168), (1838, 182), (1872, 160), (1910, 138), (1950, 140),
         (1990, 160), (2020, 196), (2040, 240), (2052, 280)],
        [(1838, 182), (1850, 210), (1860, 232)],
        [(1600, 300), (1592, 336), (1580, 372), (1574, 404)],
        [(2052, 280), (2066, 322), (2080, 360), (2096, 392)],
        [(1716, 470), (1726, 500), (1748, 520), (1770, 532)],
        [(2002, 470), (1990, 500), (1968, 520), (1946, 532)],
        [(1840, 100), (1880, 92), (1920, 110), (1946, 138)],
    ]
    lines = [onto(l, "v", 1.0) for l in front] + [onto(l, "h", 1.0) for l in back]
    return [l for l in lines if len(l) > 2]

def paint_magma(body, cy):
    ao = vertex_ao(body)
    T = texels(body)
    P, N, cov = T["P"], T["N"], T["cov"]
    AO = texel_values(T, ao)
    v1 = fbm3(P, 3.0, 41, 4); v2 = fbm3(P, 14.0, 43, 3)
    col = gradient((0.13, 0.1, 0.095), (0.22, 0.17, 0.155), v1 * 1.2 - 0.1) * (0.92 + 0.14 * v2[..., None])
    occ = np.clip(AO * 1.7, 0, 1)
    col = col * (1 - 0.6 * occ[..., None]) + np.asarray((0.07, 0.05, 0.05), np.float32) * (0.6 * occ[..., None])
    em = np.zeros(P.shape, np.float32)
    D, Wd, K = line_field(T, [crack_lines(BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get()))], reach=0.09)
    on = (K == 0)
    core = np.clip(1 - D / 0.012, 0, 1) ** 0.8 * on
    mid = np.clip(1 - D / 0.03, 0, 1) ** 0.7 * on
    edge = np.clip(1 - D / 0.042, 0, 1) * on
    halo = np.exp(-D / 0.035) * on
    col = col * (1 - 0.55 * edge[..., None]) + np.asarray((0.45, 0.06, 0.02), np.float32) * (0.55 * edge[..., None])
    col = col * (1 - mid[..., None]) + np.asarray((1.0, 0.45, 0.05), np.float32) * mid[..., None]
    col = col * (1 - core[..., None]) + np.asarray((1.0, 0.85, 0.3), np.float32) * core[..., None]
    em += np.asarray((1.0, 0.38, 0.04), np.float32) * (mid * 0.95 + halo * 0.25)[..., None] + np.asarray((1.0, 0.82, 0.3), np.float32) * core[..., None]
    # Kratermulde: Innenwand glüht von unten nach oben dunkler werdend, Rand bleibt dunkel (Tiefe ohne Leuchten sichtbar)
    poly = [MV(px, py) for px, py in CRATER]
    c0 = sum(poly, Vector()) / len(poly)
    poly = [(c0.x + (q.x - c0.x) * 0.97, c0.z + (q.z - c0.z) * 0.97) for q in poly]
    X, Z = P[..., 0], P[..., 2]
    inside = np.zeros(X.shape, bool)
    for (x1, z1), (x2, z2) in zip(poly, poly[1:] + poly[:1]):          # gerade/ungerade Regel
        cross = ((z1 > Z) != (z2 > Z)) & (X < (x2 - x1) * (Z - z1) / (z2 - z1 + 1e-9) + x1)
        inside ^= cross
    deep = np.clip((P[..., 1] - (cy + 0.025)) / 0.1, 0, 1) * inside * (P[..., 1] < cy + 0.25)
    col = col * (1 - deep[..., None] * 0.8) + np.asarray((0.85, 0.28, 0.04), np.float32) * (deep[..., None] * 0.8)
    em += np.asarray((1.0, 0.35, 0.04), np.float32) * (deep ** 1.5)[..., None] * 0.9
    # Maulspalt innen: Glut
    T["out"][..., :3] = np.where(cov[..., None], np.clip(col, 0, 1), T["out"][..., :3])
    T["em"][..., :3] = np.where(cov[..., None], np.clip(em, 0, 1), 0)
    commit(T, strength=2.0)

# ---------------------------------------------------------------- Variante

@variante("magma_golem", "koloss")
def magmagolem_neu(arm, body):
    remove_body(body)
    widen_legs(arm, float(os.environ.get("LEG_OUT", "0.1")))
    spread_arms(arm, float(os.environ.get("ARM_SPREAD", "20")), acts=("Walk", "Run"))
    fix_elbows(arm, inward=10.0)
    pose_hands(arm)
    M = lava_mats()
    body, tbvh, cy, my = magma_body(arm)
    bind_magma(body, arm, tbvh)
    hands = []
    for side in ("Left", "Right"):
        h = golem_hand("Hand" + side, side, 2.2, M["skin"])
        h.matrix_world = arm.matrix_world @ arm.data.bones["mixamorig:%sHand" % side].matrix_local @ h.matrix_world
        bake_transform(h); group_all(h, "mixamorig:%sHand" % side)
        hands.append(h)
    body.data.materials.clear(); body.data.materials.append(M["skin"])
    bpy.ops.object.select_all(action='DESELECT')
    for o in hands:
        o.select_set(True)
    body.select_set(True); bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    if STUFE != "form":
        smart_uv(body)
        body.data.materials[0] = image_material("Basalthaut", 2048, rough=0.85)
        paint_magma(body, cy)
    bvh = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())
    head = magma_eyes(tbvh, M) + mouth_fill(tbvh, M, my)
    pool = crater_pool(M, cy)
    attach(pool, arm, "mixamorig:Spine2")
    for o in head:
        attach(o, arm, "mixamorig:Head")
    print("MAGMAGOLEM", sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH'), "Flächen")

if __name__ == "__main__":
    run(VAR, OUT)
