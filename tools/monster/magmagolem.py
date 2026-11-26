# Magma-Golem neu (Entwurf „Kraterherz“ von ChatGPT, vom Nutzer freigegeben am 26.11.2026):
# Vorlage_Raw/Magmagolem_Neuentwurf_v1 (01_turnaround.png maßgeblich, 02_kopf_und_angriff.png, LIESMICH_CLAUDE.md).
# Gedrungener Gorilla-Golem aus zusammenhängenden, gerundeten Basaltformen (dunkles Anthrazitbraun, matt), mit breiten
# glühenden Lavarissen über Schultern, Arme, Beine, Rücken und Kopf, wenigen großen Schlackenporen, einer tiefen
# unregelmäßigen Kratermulde in der Brust mit glühendem Lavakern, schweren Gesteinsbrauen, orangegelben Augen mit
# dunklen Pupillen und einem breiten, offenen Grinsen (Glut innen, zwei stumpfe Basalthauer).
# Maße aus dem Turnaround (Maßstab 0,0037 m je Bildpunkt, Vorlage zeigt die Gehhaltung).
# Skelett und Bewegungen des Koloss; Beine etwas weiter auseinander, Schultergelenke breiter und höher, Arme hängen
# fast senkrecht wie in der Vorlage.
# Haut aus Metaballs (Rumpf, Kopf, Brauen/Lippen, Arme, Beine, Füße je eine Familie: weich in sich, mit Falte
# zueinander), Krater, Maul und Poren ausgeschnitten. Die Lavarisse werden 1:1 aus dem Turnaround übernommen:
# jede Hautstelle nimmt in der Gehhaltung die Ansicht (vorn, Seite, hinten), aus der sie am besten zu sehen ist.
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

M_HEAD = MV(318, 160, 1285)
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
            "zahn": look("Basaltzahn", (0.34, 0.25, 0.22), rough=0.7),
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

def widen_shoulders(arm, dx, dz):
    """Arme samt Händen nach außen und oben setzen (Vorlage: Schultergelenk in der großen Schulterkugel)"""
    sets = {s: descendants(arm, "mixamorig:%sArm" % s) for s in ("Left", "Right")}
    def fn(name, h, t):
        for s, sg in (("Left", 1), ("Right", -1)):
            v = Vector((dx * sg, 0, dz))
            if name in sets[s]:
                return h + v, t + v
            if name == "mixamorig:%sShoulder" % s:
                return h, t + v
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

ARM_PORES = []                  # (Mitte, Richtung, Radius): wenige große Poren auf Schultern, Bizeps und Unterarmen
MOUTH3 = [(258, 190), (268, 184.5), (292, 182.5), (318, 182), (344, 182.5), (368, 184.5), (378, 190),
          (371, 196), (348, 200), (318, 201), (288, 200), (265, 196)]      # breites, offenes Grinsen (px der Vorderansicht)

def smooth_loop(pts, k=4):
    """Geschlossenen Umriss weich machen (Catmull-Rom, k Punkte je Abschnitt)"""
    n = len(pts); out = []
    for i in range(n):
        p0, p1, p2, p3 = (Vector(pts[(i + j) % n]) for j in (-1, 0, 1, 2))
        for t in [j / k for j in range(k)]:
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    return out

def loop_cutter(name, P2, front_y, depth, shrink=0.6, extra=0.3, straight=0.06):
    """Schneidekörper aus einem weichen Umriss (Punkte in Ruhehaltung, y wird gesetzt), nach hinten zur Schüssel
    (bis straight hinter front_y gerade Wand, danach verjüngt)"""
    c = sum(P2, Vector()) / len(P2)
    bm = bmesh.new(); rings = []
    for k in range(16):
        t = k / 15
        y = front_y - extra + (extra + depth) * t
        dd = max(0.0, (y - front_y - straight) / max(depth - straight, 1e-3))
        sc = 1.0 - (1 - shrink) * min(1.0, dd) ** 1.6
        rings.append([bm.verts.new((c.x + (p.x - c.x) * sc, y, c.z + (p.z - c.z) * sc)) for p in P2])
    n = len(P2)
    for a, b in zip(rings, rings[1:]):
        for k in range(n):
            bm.faces.new([a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]])
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finish(name, bm)

def mouth_loop():
    return smooth_loop([MV(px, py) for px, py in MOUTH3], 3)

CRATER_K = 0.86                 # Öffnung etwas kleiner als der Umriss der Vorlage, außen herum der wulstige Rand

def crater_loop(k=CRATER_K):
    P = smooth_loop([MV(px, py) for px, py in CRATER], 4)
    c = sum(P, Vector()) / len(P)
    return [c + (p - c) * k for p in P]

def seg_dist(X, Z, poly):
    """Abstand der Punkte (X, Z) zum geschlossenen Umriss poly [(x, z)]"""
    A = np.asarray(poly, np.float32); B_ = np.roll(A, -1, 0)
    d = np.full(X.shape, 9.0, np.float32)
    for (ax, az), (bx, bz) in zip(A, B_):
        vx, vz = bx - ax, bz - az
        t = np.clip(((X - ax) * vx + (Z - az) * vz) / (vx * vx + vz * vz + 1e-12), 0, 1)
        d = np.minimum(d, np.hypot(X - ax - t * vx, Z - az - t * vz))
    return d

def crater_rim(body, cy):
    """Wulstiger, runder Steinrand um die Kratermulde: Haut am Umriss etwas nach außen wölben"""
    me = body.data
    co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    nr = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get("normal", nr); nr = nr.reshape(-1, 3)
    d = seg_dist(co[:, 0], co[:, 2], [(p.x, p.z) for p in crater_loop(0.95)])
    w = 0.04 * np.exp(-(d / 0.045) ** 2) * (co[:, 1] < cy + 0.14) * np.clip(-nr[:, 1] * 2, 0, 1)
    co += nr * w[:, None]
    me.vertices.foreach_set("co", co.ravel()); me.update()

def magma_body(arm):
    """Ein Guss aus weichen, runden Basaltmassen (Comicform): Rumpf und Kopf verschmelzen weich, Arme und Beine je
    eine Form mit weichen Mulden zwischen Schulterkugel, Bizeps und Unterarm; die Gliederung zeigen die Glutrisse"""
    T = mb_family("Rumpf")
    mb_ell(T, MV(318, 285, 1392), (0.46, 0.4, 0.28))               # mächtige Brust
    for s in (1, -1):
        mb_ell(T, MV(318 + 95 * s, 292, 1322), (0.24, 0.2, 0.17))   # Brustmuskeln
        mb_ell(T, MV(318 + 105 * s, 218, 1410), (0.2, 0.24, 0.14))   # Kapuzenmuskel vom Kopf zur Schulter
    mb_ell(T, MV(318, 250, 1440), (0.42, 0.25, 0.25))              # Nacken- und Rückenbuckel
    for s in (1, -1):
        mb_ell(T, MV(318 + 86 * s, 186, 1420), (0.2, 0.24, 0.13))    # Kapuzenmuskel steigt bis an die Kopfseiten
    mb_ell(T, MV(318, 175, 1450), (0.28, 0.22, 0.14))              # Buckel hinter dem Kopf
    mb_ell(T, MV(318, 395, 1372), (0.33, 0.32, 0.19))              # schmalere Taille / Bauch
    mb_ell(T, MV(318, 458, 1385), (0.3, 0.27, 0.13))               # Becken
    # Kopf: eine eigene breite, kompakte Masse (Falte zum Rumpf), Gesicht weich darin verschmolzen
    K = mb_family("Kopf")
    def at(px, py, y):
        c = MV(px, py); c.y = y
        return tuple(c)
    mb_ell(K, at(318, 136, -0.1), (0.255, 0.24, 0.16))             # runder Schädel (Augenpartie zurück)
    mb_ell(K, at(318, 180, -0.19), (0.3, 0.22, 0.12))              # Wangen breit bis zum Kiefer
    mb_ell(K, at(318, 92, -0.17), (0.075, 0.075, 0.07))            # Scheitelhöcker (kleiner Krater obenauf)
    mb_ell(K, at(318, 80, -0.17), (0.035, 0.035, 0.035), neg=True)
    for s in (1, -1):
        mb_ell(K, at(318 + 47 * s, 102, -0.14), (0.07, 0.075, 0.06))    # Höcker seitlich
        mb_ell(K, at(318 + 62 * s, 118, 0.06), (0.055, 0.065, 0.05))    # Höcker hinten außen
        mb_ell(K, at(318 + 32 * s, 158, -0.37), (0.078, 0.065, 0.068), neg=True)   # Augenhöhle
    mb_ell(K, at(318, 168, -0.41), (0.058, 0.05, 0.046))           # breite Nase
    Bw = mb_family("Brauen")              # eigene Familie: Brauen und Lippen setzen sich mit einer Falte vom Gesicht ab
    lip = [(-0.25, -0.25, 186), (-0.175, -0.35, 179), (-0.085, -0.395, 177), (0.0, -0.405, 177), (0.085, -0.395, 177),
           (0.175, -0.35, 179), (0.25, -0.25, 186)]
    for (x0, y0, p0), (x1, y1, p1) in zip(lip, lip[1:]):
        mb_caps(Bw, Vector((x0, y0, MV(318, p0).z)), Vector((x1, y1, MV(318, p1).z)), 0.05)   # dicke Oberlippe
    mb_ell(K, at(318, 219, -0.24), (0.31, 0.2, 0.095))             # wuchtiger, breiter Unterkiefer
    low = [(-0.215, -0.29, 196), (-0.13, -0.385, 206), (0.0, -0.41, 209), (0.13, -0.385, 206), (0.215, -0.29, 196)]
    for (x0, y0, p0), (x1, y1, p1) in zip(low, low[1:]):
        mb_caps(Bw, Vector((x0, y0, MV(318, p0).z)), Vector((x1, y1, MV(318, p1).z)), 0.045)   # Unterlippe als Wulst
    for s in (1, -1):                                              # schwere, runde Brauenwülste im V
        mb_ell(Bw, at(318 + 35 * s, 132, -0.37), (0.135, 0.09, 0.054), Quaternion((0, 1, 0), math.radians(-22 * s)))
    parts = [K, Bw]
    for side, s in (("Left", 1), ("Right", -1)):
        sh, el, wr = B(arm, side + "Arm"), B(arm, side + "ForeArm"), B(arm, side + "Hand")
        A_ = mb_family("Arm" + side)
        sc = sh + Vector((0.07 * s, 0.01, 0.03))
        mb_ell(A_, tuple(sc), (0.235, 0.23, 0.225))                # große runde Schulterkugel
        mb_caps(A_, sh.lerp(el, 0.3), el, 0.125)
        c, semi, q = along(sh, el, 0.165, 0.2, 0.62); mb_ell(A_, c, semi, q)          # Bizeps
        mb_caps(A_, el, wr, 0.13)
        c, semi, q = along(el, wr, 0.205, 0.235, 0.45); mb_ell(A_, c, semi, q)        # mächtiger Unterarm, oben dick
        mb_ell(A_, tuple(wr), (0.125, 0.125, 0.125))
        parts.append(A_)
        ARM_PORES.extend([(sc, Vector((s, -0.55, 0.45)).normalized(), 0.075),
                          (el.lerp(wr, 0.45), Vector((s, -0.2, 0.25)).normalized(), 0.065)])
        up, kn, an = B(arm, side + "UpLeg"), B(arm, side + "Leg"), B(arm, side + "Foot")
        L_ = mb_family("Bein" + side)
        top = Vector((kn.x * 0.9, kn.y + 0.02, 0.58))
        mb_caps(L_, top, kn, 0.225)                                # gerade Säule (kein X-Bein)
        mb_ell(L_, tuple(top.lerp(kn, 0.4)), (0.26, 0.25, 0.2))
        mb_caps(L_, kn, an, 0.205)
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
    remesh(body, 0.011)
    bvh0 = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())
    cy = front_hit(tbvh, MV(325, 315).x, MV(325, 315).z)[0].y
    my = front_hit(bvh0, 0, MV(318, 191).z)[0].y
    crater_rim(body, cy)
    cutters = [loop_cutter("Krater", crater_loop(), cy, 0.16, shrink=0.42, straight=-0.03),      # flache Schüssel
               loop_cutter("Maul", mouth_loop(), my, 0.12, shrink=0.85)]
    for kind, px, py, r in PORES:
        if r < 0.045:
            continue
        if kind == "v":
            p = MV(px, py); h = bvh0.ray_cast(Vector((p.x, -3, p.z)), Vector((0, 1, 0)), 6)
        elif kind == "h":
            p = MB(px, py); h = bvh0.ray_cast(Vector((p.x, 3, p.z)), Vector((0, -1, 0)), 6)
        else:
            continue
        if h[0] is None:
            continue
        n = h[1] if h[1].dot(h[0] - Vector((0, 0.1, h[0].z))) > 0 else -h[1]
        cutters.append(sphere("Pore", tuple(h[0] + n * r * 0.4), r, (1, 1, 1), segs=(24, 14)))
    for c, d, r in ARM_PORES:
        h = bvh0.ray_cast(c + d * 1.5, -d, 3.0)
        if h[0] is None:
            continue
        n = h[1] if h[1].dot(d) > 0 else -h[1]
        cutters.append(sphere("Pore", tuple(h[0] + n * r * 0.4), r, (1, 1, 1), segs=(24, 14)))
    for ct in cutters:
        md = body.modifiers.new("Schnitt", 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = ct; md.solver = 'EXACT'
        apply_mod(body, md)
        bpy.data.objects.remove(ct, do_unlink=True)
    remesh(body, 0.011)
    md = body.modifiers.new("Glatt", 'SMOOTH'); md.factor = 0.55; md.iterations = 7; apply_mod(body, md)
    md = body.modifiers.new("Weniger", 'DECIMATE'); md.ratio = 0.3; apply_mod(body, md)
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
        p, _ = front_hit(bvh, MV(318 + 32 * s, 158).x, MV(318, 158).z)    # in der Augenhöhle, unter dem Brauenwulst
        p = p + Vector((0, -0.016, 0))                                      # groß und vorgewölbt
        nn = Vector((0.25 * s, -1, 0.05)).normalized()
        inner = Vector((-s, 0, 0)); inner = (inner - nn * inner.dot(nn)).normalized()
        up = nn.cross(inner).normalized()
        if up.z < 0:
            up = -up
        a, dd, b = 0.073, 0.036, 0.066
        e = sphere("Auge%d" % s, (0, 0, 0), 1.0, (1, 1, 1), segs=(32, 16))
        Fm = Matrix((inner * a, nn * dd, up * b)).transposed().to_4x4(); Fm.translation = p
        e.data.transform(Fm)
        me = e.data; me.uv_layers.new(name="UVMap"); uvl = me.uv_layers.active.data
        for poly in me.polygons:
            for li in poly.loop_indices:
                q = me.vertices[me.loops[li].vertex_index].co - p
                uvl[li].uv = (0.5 + 0.5 * q.dot(inner) / a, 0.5 + 0.5 * q.dot(up) / b)
        out.append(give(e, M["eye"]))
    return out

def mouth_fill(bvh, M, my):
    """Glut hinter dem breiten Maulspalt und zwei stumpfe Basalt-Hauer an seiner Unterkante"""
    P2 = mouth_loop()
    c = sum(P2, Vector()) / len(P2)
    bm = bmesh.new()
    ring = [bm.verts.new((c.x + (p.x - c.x) * 0.97, my + 0.075, c.z + (p.z - c.z) * 0.97)) for p in P2]
    cen = bm.verts.new((c.x, my + 0.085, c.z))
    for k in range(len(ring)):
        bm.faces.new([cen, ring[(k + 1) % len(ring)], ring[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    glow = finish("Maulglut", bm, smooth=True)
    me = glow.data; me.uv_layers.new(name="UVMap"); uvl = me.uv_layers.active.data
    for poly in me.polygons:
        for li in poly.loop_indices:
            q = me.vertices[me.loops[li].vertex_index].co - c
            uvl[li].uv = (0.5 + q.x / 0.5, 0.5 + q.z / 0.16)
    give(glow, M["lava"])
    parts = [glow]
    for s in (1, -1):
        x = 0.107 * s
        z0 = MV(318, 212).z
        p, _ = front_hit(bvh, x, z0)
        base = Vector((x, p.y + 0.03, z0))
        o = tube("Hauer%d" % s, [base + Vector((0, -0.004 * t, h)) for t, h in ((0, 0), (1, 0.025), (2, 0.05), (3, 0.07), (3, 0.082), (3, 0.088))],
                 [0.05, 0.043, 0.033, 0.022, 0.012, 0.0], segs=16)              # breit, stumpf zulaufend
        smooth_obj(o, 70)
        parts.append(give(o, M["zahn"]))
    return parts

def crater_pool(M, cy):
    """Unregelmäßiger, knotiger Lavakern in der Kratermulde, dicht hinter dem wulstigen Rand (kleiner Hohlraum);
    reicht seitlich bis in die Wand, damit keine Fuge zu sehen ist"""
    P2 = crater_loop()
    c = sum(P2, Vector()) / len(P2)
    bm = bmesh.new(); rings = []
    rng = random.Random(9)
    for j in range(1, 7):
        t = j / 6
        rings.append([bm.verts.new((c.x + (p.x - c.x) * 1.04 * t, cy + 0.065 - 0.03 * (1 - t) ** 2 + 0.03 * t ** 3 + rng.uniform(-0.008, 0.008),
                                    c.z + (p.z - c.z) * 1.04 * t)) for p in P2])
    cen = bm.verts.new((c.x, cy + 0.04, c.z))
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

REF_TA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Vorlage_Raw", "Magmagolem_Neuentwurf_v1",
                      "01_turnaround.png")
VIEWS = (("vorn", 318, 638, (0, -1, 0)), ("seite", 1395, 639, None), ("hinten", BACK_X, 639, (0, 1, 0)))

def in_poly(X, Y, poly):
    inside = np.zeros(X.shape, bool)
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        inside ^= ((y1 > Y) != (y2 > Y)) & (X < (x2 - x1) * (Y - y1) / (y2 - y1 + 1e-9) + x1)
    return inside

def ref_lava():
    """Turnaround als Feld: Farbe (sRGB) und Glutstärke je Bildpunkt (gelber Kern und oranger Strom 1, dunkelroter
    Rand ~0,5, warmer Schein auf dem Gestein wenig); Augen, Maul und Krater gehören nicht zu den Rissen"""
    img = bpy.data.images.load(os.path.abspath(REF_TA))
    w, h = img.size
    a = np.array(img.pixels[:], np.float32).reshape(h, w, 4)[::-1, :, :3].copy()     # Zeile 0 = oben
    bpy.data.images.remove(img)
    L = np.clip((a[..., 0] - a[..., 2] - 0.18) / 0.5, 0, 1)
    Y, X = np.mgrid[0:h, 0:w].astype(np.float32)
    def ell(cx, cy, rx, ry):
        return ((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2 < 1
    cx = sum(p[0] for p in CRATER) / len(CRATER); cyy = sum(p[1] for p in CRATER) / len(CRATER)
    crater = [(cx + (px - cx) * 1.14, cyy + (py - cyy) * 1.14) for px, py in CRATER]
    cut = ell(287, 156, 25, 21) | ell(349, 156, 25, 21) | ell(318, 191, 72, 17) | in_poly(X, Y, crater)
    cut |= ell(1300, 152, 24, 21) | ((X > 1245) & (X < 1335) & (Y > 172) & (Y < 204))    # Seite: Auge, Maul
    cut |= (X > 1235) & (X < 1300) & (Y > 232) & (Y < 385)                                # Seite: Kraterrand
    L[cut] = 0
    return a, L

def texel_multi(T, vals):
    """Mehrere Werte je Punkt (n, k) auf die Texel übertragen (h, w, k)"""
    me = T["body"].data
    h, w = T["P"].shape[:2]; k = vals.shape[1]
    out = np.zeros((h, w, k), np.float32)
    uvl = me.uv_layers.active.data
    for tri in me.loop_triangles:
        U = np.array([(uvl[i].uv.x * w, uvl[i].uv.y * h) for i in tri.loops])
        x0, y0 = np.floor(U.min(0)).astype(int) - 1; x1, y1 = np.ceil(U.max(0)).astype(int) + 1
        x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, w - 1), min(y1, h - 1)
        if x1 < x0 or y1 < y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        Q = np.stack([gx.ravel(), gy.ravel()], 1)
        v0 = U[1] - U[0]; v1 = U[2] - U[0]; d00 = v0 @ v0; d01 = v0 @ v1; d11 = v1 @ v1
        den = d00 * d11 - d01 * d01
        if abs(den) < 1e-12:
            continue
        v2 = Q - U[0]; d20 = v2 @ v0; d21 = v2 @ v1
        b1 = (d11 * d20 - d01 * d21) / den; b2 = (d00 * d21 - d01 * d20) / den; b0 = 1 - b1 - b2
        eps = -1.0 / max(1.0, math.sqrt(max(d00, d11)))
        ins = (b0 >= eps) & (b1 >= eps) & (b2 >= eps)
        if not ins.any():
            continue
        bb = np.clip(np.stack([b0[ins], b1[ins], b2[ins]], 1), 0, None); bb /= bb.sum(1, keepdims=True)
        ix = (Q[ins] - 0.5).astype(int)
        out[ix[:, 1], ix[:, 0]] = bb @ vals[list(tri.vertices)]
    return out

def sample(img, X, Y):
    """Bilinear aus dem Turnaround lesen (X, Y in Bildpunkten)"""
    h, w = img.shape[:2]
    X = np.clip(X, 0, w - 1.001); Y = np.clip(Y, 0, h - 1.001)
    x0 = X.astype(int); y0 = Y.astype(int); fx = X - x0; fy = Y - y0
    if img.ndim == 3:
        fx = fx[..., None]; fy = fy[..., None]
    return ((img[y0, x0] * (1 - fx) + img[y0, x0 + 1] * fx) * (1 - fy) +
            (img[y0 + 1, x0] * (1 - fx) + img[y0 + 1, x0 + 1] * fx) * fy)

def ref_project(T, arm):
    """Rissbild der Vorlage auf die Haut legen: jede Stelle nimmt die Ansicht (vorn, Seite, hinten), aus der sie in
    der Gehhaltung der Vorlage am besten zu sehen ist (verdeckte Stellen nehmen eine andere Ansicht).
    Liefert Glutstärke L (h, w) und Farbe der Vorlage C (h, w, 3)"""
    body = T["body"]
    sc = bpy.context.scene; ad = arm.animation_data
    saved = (ad.action, sc.frame_current, arm.data.pose_position)
    arm.data.pose_position = 'POSE'
    ad.action = next(a for a in bpy.data.actions if a.name.startswith("Walk"))
    sc.frame_set(0)
    dg = bpy.context.evaluated_depsgraph_get()
    me = body.evaluated_get(dg).data
    assert len(me.vertices) == len(body.data.vertices)
    mw = body.matrix_world; m3 = mw.to_3x3()
    co = [mw @ v.co for v in me.vertices]
    nr = [(m3 @ v.normal).normalized() for v in me.vertices]
    bvh = BVHTree.FromPolygons([tuple(c) for c in co], [tuple(p.vertices) for p in me.polygons])
    ad.action, _, arm.data.pose_position = saved[0], None, saved[2]
    sc.frame_set(saved[1])
    n = len(co)
    vals = np.zeros((n, 9), np.float32)
    for i, (c, nn) in enumerate(zip(co, nr)):
        side = Vector((1 if nn.x >= 0 else -1, 0, 0))
        for j, (name, cx, fy, d) in enumerate(VIEWS):
            d = side if d is None else Vector(d)
            f = max(0.0, nn.dot(d)) + 0.04
            vis = bvh.ray_cast(c + nn * 0.012 + d * 0.004, d, 4.0)[0] is None
            vals[i, 3 * j + 2] = (f ** 3) * (1.0 if vis else 0.02)
            if name == "vorn":
                vals[i, 3 * j] = cx + c.x / SCM
            elif name == "hinten":
                vals[i, 3 * j] = cx - c.x / SCM
            else:
                vals[i, 3 * j] = cx + (c.y - 0.1) / SCM
            vals[i, 3 * j + 1] = fy - c.z / SCM
    TV = texel_multi(T, vals)
    img, Lr = ref_lava()
    Wsum = TV[..., 2] + TV[..., 5] + TV[..., 8] + 1e-6
    L = np.zeros(TV.shape[:2], np.float32); C = np.zeros(TV.shape[:2] + (3,), np.float32)
    for j, (name, cx, fy, d) in enumerate(VIEWS):
        X = TV[..., 3 * j]; Y = TV[..., 3 * j + 1]
        if name == "vorn":
            X = np.clip(X, 0, 640)
        elif name == "seite":
            X = np.clip(X, 1235, 1530)
        else:
            X = np.clip(X, 1560, 2171)
        wv = TV[..., 3 * j + 2] / Wsum
        L += wv * sample(Lr, X, Y)
        C += wv[..., None] * sample(img, X, Y)
    return L, C

def paint_magma(body, cy, arm):
    """Comicartige Tonoberfläche: warmes Anthrazitbraun ohne Körnung, sanftes Licht von oben, weiche Schatten in
    Mulden; die Glutrisse samt Farbe und Schein 1:1 aus dem Turnaround; Kraterwand glüht von innen"""
    ao = vertex_ao(body)
    T = texels(body)
    P, N, cov = T["P"], T["N"], T["cov"]
    AO = texel_values(T, ao)
    v1 = fbm3(P, 2.2, 41, 3)
    light = smoothstep(-0.45, 0.95, N[..., 2] * 0.75 - N[..., 1] * 0.35)
    col = gradient((0.17, 0.125, 0.115), (0.4, 0.31, 0.28), light) * (0.96 + 0.08 * v1[..., None])
    occ = np.clip(AO * 1.5, 0, 1)
    col = col * (1 - 0.5 * occ[..., None]) + np.asarray((0.08, 0.055, 0.05), np.float32) * (0.5 * occ[..., None])
    em = np.zeros(P.shape, np.float32)
    L, C = ref_project(T, arm)                                     # Risse 1:1 aus dem Turnaround
    lav = smoothstep(0.1, 0.55, L)
    col = col * (1 - lav[..., None]) + C * lav[..., None]
    em += C * (smoothstep(0.35, 0.9, L) * 0.95)[..., None]
    warm = np.asarray((0.62, 0.2, 0.06), np.float32)
    # Kratermulde: Innenwand glüht von unten, Rand bekommt warmen Schein
    poly = [(q.x, q.z) for q in crater_loop()]
    X, Z = P[..., 0], P[..., 2]
    inside = np.zeros(X.shape, bool)
    for (x1, z1), (x2, z2) in zip(poly, poly[1:] + poly[:1]):
        cross = ((z1 > Z) != (z2 > Z)) & (X < (x2 - x1) * (Z - z1) / (z2 - z1 + 1e-9) + x1)
        inside ^= cross
    front = P[..., 1] < cy + 0.3
    deep = np.clip((P[..., 1] - (cy - 0.035)) / 0.075, 0, 1) * inside * front      # Wand glüht zur Lava hin
    col = col * (1 - deep[..., None] * 0.7) + np.asarray((0.75, 0.2, 0.04), np.float32) * (deep[..., None] * 0.7)
    em += np.asarray((0.9, 0.24, 0.03), np.float32) * (0.75 * deep ** 2.2)[..., None]       # Wand dunkler als der Kern
    cxz = np.asarray(sum((Vector((x, 0, z)) for x, z in poly), Vector()) / len(poly))
    rd = np.sqrt(((X - cxz[0]) / 0.36) ** 2 + ((Z - cxz[2]) / 0.3) ** 2)
    rim = np.clip(1 - np.abs(rd - 1.0) / 0.35, 0, 1) * (P[..., 1] < cy + 0.05) * front * (~inside)
    col = col * (1 - 0.25 * rim[..., None]) + warm * (0.25 * rim[..., None])
    T["out"][..., :3] = np.where(cov[..., None], np.clip(col, 0, 1), T["out"][..., :3])
    T["em"][..., :3] = np.where(cov[..., None], np.clip(em, 0, 1), 0)
    commit(T, strength=2.4)

# ---------------------------------------------------------------- Variante

@variante("magma_golem", "koloss")
def magmagolem_neu(arm, body):
    remove_body(body)
    widen_legs(arm, float(os.environ.get("LEG_OUT", "0.1")))
    widen_shoulders(arm, 0.09, 0.07)
    spread_arms(arm, float(os.environ.get("ARM_SPREAD", "8")), acts=("Walk", "Run"))
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
        paint_magma(body, cy, arm)
    bvh = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())
    head = magma_eyes(bvh, M) + mouth_fill(bvh, M, my)
    pool = crater_pool(M, cy)
    attach(pool, arm, "mixamorig:Spine2")
    for o in head:
        attach(o, arm, "mixamorig:Head")
    print("MAGMAGOLEM", sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH'), "Flächen")

if __name__ == "__main__":
    run(VAR, OUT)
