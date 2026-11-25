# Schrottkoloss neu (Entwurf von ChatGPT, vom Nutzer freigegeben am 25.11.2026, vereinfachte Fassung v2:
# weniger Kleinteile, größere Panzerflächen, ruhigere Oberflächen). Roboter-Riese aus Schrott: rostorange lackierte
# Panzerplatten mit grauen abgeplatzten Stellen, dunkler Stahl an den Gelenken. Helm mit grauem Mittelstreifen,
# schwere Brauen, rot glühende Augen, Gorilla-Nase, Maulring mit gelben Zackenzähnen und Glut. Autotüren mit Fenster,
# Griff und Warnstreifen als Schulterpanzer, gelbe Federn an Schultern und Knöcheln, Brustpanzer über einem glühenden
# Ofenbauch mit Rohrring und Nabe, Kette um die Hüfte, gelbe Fässer an den Hüften, Radkappen an den Knien,
# Schienbeinpanzer mit Warnstreifen, große Stahlstiefel, Fäuste mit gelben Fingern. Teile starr an den Knochen des
# Koloss-Skeletts (Roboter: keine weiche Haut nötig), Gelenke von Federn und Kugeln verdeckt.
# Aufruf: blender -b -P tools/monster/schrottkoloss.py -- schrott_koloss <ziel.glb>
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fabrikmutter import *          # rbox, cyl, ring, ball, planar_uv, image_mat, radial_image, hazard_image, …
import boss_aufsatz
boss_aufsatz.EXPORT_IMAGE_FORMAT = "JPEG"

# ---------------------------------------------------------------- Oberflächen

def B(arm, name, t=0.0):
    return bone_pt(arm, "mixamorig:" + name, t)

def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)

def worn_image(base, dark, chip, n=1024, seed=3, chips=0.62, grime=0.35):
    """Lack mit Abplatzern: Grundfarbe, dunklere Flecken, graue Stellen mit dunklem Rand"""
    y, x = np.mgrid[0:n, 0:n]
    P = np.stack([(x + 0.5) / n * 3.4, (y + 0.5) / n * 3.4, np.full((n, n), seed * 0.7)], -1).astype(np.float32) * 1.8
    v = fbm3(P, 2.5, seed, 4); g = fbm3(P, 6.0, seed + 3, 3); c = fbm3(P, 3.2, seed + 7, 4) + 0.12 * fbm3(P, 14.0, seed + 9, 2)
    col = gradient(base, dark, np.clip((v - 0.45) * 2.2, 0, 1) * grime + np.clip((g - 0.6) * 3, 0, 1) * 0.25)
    chipm = smoothstep(chips, chips + 0.015, c); rim = smoothstep(chips - 0.03, chips, c) * (1 - chipm)
    col = col * (1 - rim[..., None] * 0.45)
    col = col * (1 - chipm[..., None]) + np.asarray(chip, np.float32) * (0.85 + 0.3 * g[..., None]) * chipm[..., None]
    out = np.ones((n, n, 4), np.float32); out[..., :3] = np.clip(col, 0, 1)
    return out

def box_uv(o, lo=-1.2, span=3.4):
    """Abwicklung je Fläche nach der stärksten Richtung der Normale (Würfelprojektion in Weltmaßen)"""
    me = o.data
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uvl = me.uv_layers.active.data
    mw = o.matrix_world
    for poly in me.polygons:
        n = poly.normal; ax = max(range(3), key=lambda i: abs(n[i]))
        a, b = [(1, 2), (0, 2), (0, 1)][ax]
        for li in poly.loop_indices:
            p = mw @ me.vertices[me.loops[li].vertex_index].co
            uvl[li].uv = ((p[a] - lo) / span, (p[b] - lo) / span)
    return o

def schrott_mats():
    M = {
        "rust": image_mat("Rostlack", worn_image((0.74, 0.36, 0.15), (0.42, 0.18, 0.08), (0.56, 0.55, 0.53), seed=3, chips=0.69), rough=0.55, metal=0.25),
        "yellow": image_mat("GelbAlt", worn_image((0.88, 0.66, 0.16), (0.55, 0.38, 0.1), (0.5, 0.48, 0.45), seed=11, chips=0.68, grime=0.3),
                            rough=0.5, metal=0.15),
        "steel": image_mat("Schrottstahl", worn_image((0.27, 0.24, 0.23), (0.16, 0.14, 0.13), (0.42, 0.4, 0.38), seed=21, chips=0.7, grime=0.5),
                           rough=0.45, metal=0.55),
        "steel_l": look("Altmetall", (0.45, 0.44, 0.43), rough=0.4, metal=0.6),
        "silver": look("Radkappe", (0.74, 0.74, 0.76), rough=0.22, metal=0.85),
        "glass": look("Autoscheibe", (0.33, 0.43, 0.48), rough=0.08, metal=0.3),
        "black": look("Schwarz", (0.03, 0.03, 0.035), rough=0.7),
        "chain": look("Kettenstahl", (0.4, 0.38, 0.36), rough=0.35, metal=0.75),
        "teeth": image_mat("Zackenzahn", worn_image((0.86, 0.67, 0.24), (0.62, 0.44, 0.14), (0.6, 0.57, 0.5), seed=31, chips=0.7, grime=0.4),
                           rough=0.45),
        "hazard": image_mat("WarnstreifenAlt", hazard_image(yellow=(0.88, 0.66, 0.16), dark=(0.09, 0.08, 0.08)), rough=0.45),
        "eye": image_mat("Gluehauge", radial_image([(0.0, (1.0, 0.92, 0.5)), (0.35, (1.0, 0.45, 0.1)), (0.75, (0.92, 0.1, 0.04)),
                                                     (1.0, (0.5, 0.03, 0.02))], center=(0.45, 0.45)), rough=0.2, emit=3.0),
        "fire": image_mat("Schrottglut", radial_image([(0.0, (1.0, 0.85, 0.35)), (0.4, (1.0, 0.5, 0.1)), (0.8, (0.9, 0.18, 0.04)),
                                                       (1.0, (0.45, 0.05, 0.02))]), rough=0.5, emit=3.0),
    }
    return M

def uv_all(objs, M):
    for o in objs:
        if o.data.materials and o.data.materials[0] in (M["rust"], M["yellow"], M["steel"], M["teeth"]):
            box_uv(o)
    return objs

# ---------------------------------------------------------------- Bausteine

def spring(name, c, axis, R, length, turns, r, mat):
    """Schraubenfeder (gelb) um eine Achse"""
    axis = Vector(axis).normalized(); a = axis.orthogonal().normalized(); b = axis.cross(a)
    pts = []
    N = int(turns * 16)
    for k in range(N + 1):
        t = k / N; ang = t * turns * 2 * math.pi
        pts.append(tuple(Vector(c) + axis * (length * (t - 0.5)) + (a * math.cos(ang) + b * math.sin(ang)) * R))
    o = give(tube(name, pts, [r] * len(pts), segs=10), mat)
    return smooth_obj(o, 60)

def along_box(name, p0, p1, half_r, mat, t0=0.0, t1=1.0, r=0.03, up=(0, -1, 0)):
    """Kasten entlang einer Strecke (Panzer um einen Knochen)"""
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0
    a = p0 + d * t0; b = p0 + d * t1
    z = d.normalized(); y = Vector(up); y = (y - z * y.dot(z)).normalized(); x = y.cross(z)
    q = Matrix((x, y, z)).transposed().to_quaternion()
    return rbox(name, (a + b) / 2, (half_r[0], half_r[1], (b - a).length / 2), r, mat, q)

def chain(name, pts, mat, link=0.05, r=0.012):
    """Kette durch die Punkte (Glieder abwechselnd gedreht)"""
    pts = [Vector(p) for p in pts]
    path = []
    for a, b in zip(pts, pts[1:]):
        n = max(1, int((b - a).length / (link * 0.8)))
        path += [a.lerp(b, k / n) for k in range(n)]
    path.append(pts[-1])
    out = []
    for i, (a, b) in enumerate(zip(path, path[1:])):
        d = (b - a); c = (a + b) / 2
        t = torus(name + "%d" % i, (0, 0, 0), link * 0.42, r, rot=(0, 0, 0), segs=16)
        t.data.transform(Matrix.Scale(1.45, 4, (1, 0, 0)))
        q = Vector((1, 0, 0)).rotation_difference(d.normalized())
        q = q @ Quaternion((1, 0, 0), math.pi / 2 if i % 2 else 0.0)
        t.data.transform(q.to_matrix().to_4x4()); t.data.transform(Matrix.Translation(c))
        out.append(give(t, mat))
    return out

def hubcap(name, c, axis, R, M):
    """Radkappe: silberne Scheibe mit Ring, Löchern und Mittelkappe"""
    axis = Vector(axis).normalized(); c = Vector(c)
    parts = [cyl(name + "Scheibe", c - axis * 0.012, c + axis * 0.02, R, M["silver"], 40),
             ring(name + "Ring", c + axis * 0.02, axis, R * 0.92, R * 0.09, M["silver"]),
             cyl(name + "Kappe", c + axis * 0.02, c + axis * 0.04, R * 0.3, M["steel_l"], 24)]
    a = axis.orthogonal().normalized(); b = axis.cross(a)
    q = Matrix((a, b, axis)).transposed().to_quaternion()
    for k in range(6):
        ang = k * math.pi / 3
        p = c + axis * 0.021 + (a * math.cos(ang) + b * math.sin(ang)) * R * 0.6
        qq = q @ Quaternion((0, 0, 1), ang)
        parts.append(rbox(name + "Loch%d" % k, p, (R * 0.17, R * 0.08, 0.006), 0.004, M["black"], qq, segs=1))
    return parts

def fang(name, base, d, L, r, mat):
    d = Vector(d).normalized(); base = Vector(base)
    return give(tube(name, [tuple(base - d * 0.01), tuple(base + d * L * 0.5), tuple(base + d * L)], [r, r * 0.62, 0.0], segs=7), mat)

def attach_all(objs, arm, bone):
    for o in objs:
        attach(o, arm, "mixamorig:" + bone)

# ---------------------------------------------------------------- Teile

def head_parts(M, rnd):
    H0 = Vector((0, 0.03, 1.47))
    P = []
    helm = ball("Helm", H0, 0.215, M["rust"], (1.08, 1.0, 0.88)); P.append(helm)
    # grauer Streifen über die Mitte des Helms
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=1.0)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if abs(v.co.x) > 0.17 or v.co.z < -0.1 or (v.co.y < -0.55 and v.co.z < 0.45)], context='VERTS')
    for v in bm.verts:
        v.co = H0 + Vector((v.co.x * 0.215 * 1.08, v.co.y * 0.215, v.co.z * 0.215 * 0.88)) * 1.012
    P.append(give(finish("HelmStreifen", bm), M["steel_l"]))
    P.append(ball("Gesicht", (0, -0.07, 1.34), 0.19, M["steel"], (1.0, 0.8, 0.82)))
    for s in (1, -1):
        q = Quaternion((0, 1, 0), math.radians(-20 * s)) @ Quaternion((1, 0, 0), math.radians(-10))
        bc = Vector((0.08 * s, -0.215, 1.47))
        P.append(rbox("Braue%d" % s, bc, (0.085, 0.04, 0.03), 0.015, M["steel"], q))
        P.append(rivet("BrauenNiete%d" % s, bc + q @ Vector((0.05 * s, -0.04, 0.0)), (0, -1, 0.2), M, 0.014))
        P.append(ball("Augenhoehle%d" % s, (0.078 * s, -0.2, 1.425), 0.056, M["black"], (1.05, 0.6, 0.72)))
        e = ball("Auge%d" % s, (0.078 * s, -0.215, 1.425), 0.05, M["eye"], (1.1, 0.55, 0.62)); P.append(e)
        planar_uv(e, (0.078 * s, -0.215, 1.425), (1, 0, 0), (0, 0, 1), 0.055, 0.031)
        P.append(cyl("Ohrbolzen%d" % s, (0.19 * s, -0.04, 1.37), (0.245 * s, -0.04, 1.37), 0.055, M["steel"], 24))
        P.append(ball("OhrNiete%d" % s, (0.247 * s, -0.04, 1.37), 0.017, M["steel_l"]))
        P.append(ball("Nasenloch%d" % s, (0.02 * s, -0.262, 1.372), 0.012, M["black"]))
    P.append(ball("Nase", (0, -0.25, 1.38), 0.04, M["steel"], (1.0, 0.7, 0.7)))
    # Maul: dunkler Ring wie ein Baggerschaufelrand, Glut dahinter, gelbe Zackenzähne
    jaw = torus("Maulring", (0, 0, 0), 0.155, 0.034, rot=(0, 0, 0), segs=40)
    jaw.data.transform(Matrix.Scale(0.72, 4, (0, 0, 1)) @ Matrix.Scale(1.0, 4, (1, 0, 0)))
    jaw.data.transform(Quaternion((1, 0, 0), math.radians(78)).to_matrix().to_4x4())
    jaw.data.transform(Matrix.Translation((0, -0.2, 1.285)))
    P.append(give(jaw, M["steel"]))
    P.append(rbox("Unterkiefer", (0, -0.13, 1.225), (0.17, 0.1, 0.05), 0.04, M["steel"]))
    glow = ball("Maulglut", (0, -0.15, 1.29), 1.0, M["fire"], (0.14, 0.07, 0.085))
    planar_uv(glow, (0, -0.15, 1.29), (1, 0, 0), (0, 0, 1), 0.14, 0.085); P.append(glow)
    for i, x in enumerate((-0.115, -0.08, -0.042, 0.0, 0.042, 0.08, 0.115)):
        L = 0.075 if abs(abs(x) - 0.08) < 0.01 else rnd.uniform(0.04, 0.055)
        z = 1.285 + 0.1 * math.sqrt(max(0.0, 1 - (x / 0.155) ** 2)) * 0.72
        P.append(fang("ZahnOben%d" % i, (x, -0.22 + 0.05 * (x / 0.155) ** 2, z - 0.02), (0.08 * x, -0.15, -1), L, 0.02 if L > 0.06 else 0.017, M["teeth"]))
    for i, x in enumerate((-0.1, -0.06, -0.02, 0.025, 0.065, 0.105)):
        L = 0.075 if abs(abs(x) - 0.06) < 0.01 or abs(abs(x) - 0.065) < 0.01 else rnd.uniform(0.035, 0.05)
        z = 1.285 - 0.1 * math.sqrt(max(0.0, 1 - (x / 0.155) ** 2)) * 0.72
        P.append(fang("ZahnUnten%d" % i, (x, -0.22 + 0.05 * (x / 0.155) ** 2, z + 0.02), (0.06 * x, -0.15, 1), L, 0.02 if L > 0.06 else 0.016, M["teeth"]))
    return P

def torso_parts(M):
    chest, belly, hips = [], [], []
    # Brust (Spine2): dunkler Kern, breiter Rostpanzer aus zwei Platten, Kragen, Rückenplatte mit Lüftung
    chest.append(rbox("Brustkern", (0, 0.06, 1.11), (0.34, 0.22, 0.17), 0.08, M["steel"]))
    for s in (1, -1):
        q = Quaternion((0, 0, 1), math.radians(14 * s)) @ Quaternion((1, 0, 0), math.radians(8))
        chest.append(rbox("Brustplatte%d" % s, (0.155 * s, -0.15, 1.1), (0.17, 0.07, 0.15), 0.04, M["rust"], q))
        for k, (dx, dz) in enumerate(((0.09, 0.08), (0.09, -0.08))):
            chest.append(rivet("BrustNiete%d%d" % (s, k), (0.155 * s + dx * s * 1.1, -0.225, 1.1 + dz), (0, -1, 0), M, 0.018))
    chest.append(rbox("Kragen", (0, 0.02, 1.245), (0.3, 0.2, 0.06), 0.045, M["rust"]))
    chest.append(rbox("Rueckenplatte", (0, 0.26, 1.08), (0.31, 0.06, 0.19), 0.045, M["rust"]))
    q = frame_at(Vector((0, 0.3, 1.04)), (0, 1, 0))
    chest += vent("RueckenLueftung", Vector((0, 0.315, 1.03)), q, 0.11, 0.085, {"steel_l": M["steel"], "black": M["black"]}, slots=4)
    # Bauch (Spine1): glühender Ofen hinter einem Rohrring, Nabe unten
    belly.append(rbox("Bauchkern", (0, 0.04, 0.88), (0.29, 0.2, 0.15), 0.08, M["steel"]))
    g = ball("Bauchglut", (0, -0.1, 0.9), 1.0, M["fire"], (0.15, 0.06, 0.1)); planar_uv(g, (0, -0.1, 0.9), (1, 0, 0), (0, 0, 1), 0.15, 0.1)
    belly.append(g)
    r = torus("Rohrring", (0, 0, 0), 0.15, 0.038, rot=(0, 0, 0), segs=36)
    r.data.transform(Matrix.Scale(0.72, 4, (0, 0, 1))); r.data.transform(Quaternion((1, 0, 0), math.radians(90)).to_matrix().to_4x4())
    r.data.transform(Matrix.Translation((0, -0.15, 0.9))); belly.append(give(r, M["steel"]))
    for i, x in enumerate((-0.06, 0.0, 0.06)):
        belly.append(cyl("Glutstab%d" % i, (x, -0.16, 0.99), (x, -0.16, 0.81), 0.012, M["steel"], 10))
    belly.append(cyl("Nabe", (0, -0.15, 0.82), (0, -0.225, 0.82), 0.07, M["steel"], 32))
    belly.append(ring("NabenRing", (0, -0.225, 0.82), (0, -1, 0), 0.06, 0.012, M["steel_l"]))
    belly.append(ball("NabenKappe", (0, -0.23, 0.82), 0.03, M["steel_l"], (1, 0.5, 1)))
    # Becken (Hips): Block, gelbe Fässer an den Seiten, Kette vorn und hinten
    hips.append(rbox("Becken", (0, 0.06, 0.65), (0.27, 0.2, 0.12), 0.06, M["steel"]))
    for s in (1, -1):
        hips.append(cyl("Fass%d" % s, (0.15 * s, -0.02, 0.62), (0.35 * s, -0.02, 0.62), 0.125, M["yellow"], 32))
        for xx in (0.17, 0.33):
            hips.append(ring("Fassring%d%d" % (s, int(xx * 100)), (xx * s, -0.02, 0.62), (1, 0, 0), 0.125, 0.016, M["steel"]))
    hips += chain("KetteVorn", [(-0.2, -0.17, 0.74), (-0.1, -0.215, 0.67), (0, -0.225, 0.645), (0.1, -0.215, 0.67), (0.2, -0.17, 0.74)], M["chain"])
    hips += chain("KetteHinten", [(-0.2, 0.25, 0.74), (-0.1, 0.27, 0.68), (0, 0.275, 0.655), (0.1, 0.27, 0.68), (0.2, 0.25, 0.74)], M["chain"])
    return chest, belly, hips

def arm_parts(arm, side, s, M):
    sh, el, wr = B(arm, side + "Arm"), B(arm, side + "ForeArm"), B(arm, side + "Hand")
    up, fore = [], []
    d = (el - sh).normalized()
    up.append(spring("Schulterfeder" + side, sh + d * 0.13, d, 0.11, 0.2, 4.0, 0.026, M["yellow"]))
    up.append(along_box("Oberarm" + side, sh, el, (0.1, 0.1), M["steel"], 0.15, 0.95, 0.045))
    door = []
    # Autotür als Schulterpanzer: senkrechte Platte außen, oben über die Schulter gewölbt; Fenster, Griff, Warnstreifen
    q = Quaternion((0, 0, 1), math.radians(-36 * s)) @ Quaternion((0, 1, 0), math.radians(14 * s))   # schräg nach vorn: Fenster sichtbar
    dc = Vector((0.6 * s, -0.05, 1.13))
    door.append(rbox("Tuer" + side, dc, (0.065, 0.21, 0.19), 0.04, M["rust"], q))
    door.append(rbox("Schulterkappe" + side, (0.48 * s, 0.05, 1.27), (0.15, 0.17, 0.08), 0.06, M["rust"], Quaternion((0, 1, 0), math.radians(-16 * s))))
    nrm = q @ Vector((s, 0, 0))
    door.append(rbox("TuerFenster" + side, dc + nrm * 0.06 + q @ Vector((0, 0.01, 0.075)), (0.012, 0.155, 0.075), 0.03, M["glass"], q))
    door.append(rbox("TuerFensterRahmen" + side, dc + nrm * 0.052 + q @ Vector((0, 0.01, 0.075)), (0.012, 0.17, 0.09), 0.035, M["steel"], q))
    door.append(rbox("TuerGriff" + side, dc + nrm * 0.075 + q @ Vector((0, -0.06, -0.035)), (0.014, 0.055, 0.014), 0.007, M["steel"], q))
    door.append(rbox("TuerGriffSockel" + side, dc + nrm * 0.065 + q @ Vector((0, -0.06, -0.035)), (0.01, 0.07, 0.022), 0.008, M["steel_l"], q))
    hz = rbox("TuerWarn" + side, dc + nrm * 0.004 + q @ Vector((0, 0, -0.15)), (0.069, 0.212, 0.04), 0.02, M["hazard"], q)
    planar_uv(hz, dc, q @ Vector((0, 1, 0)), (0, 0, 1), 0.09, 0.09); door.append(hz)
    fore.append(ball("Ellbogen" + side, el, 0.1, M["steel"]))
    fore.append(along_box("Unterarm" + side, el, wr, (0.155, 0.15), M["steel"], 0.08, 0.98, 0.055))
    fore.append(along_box("UnterarmPlatte" + side, el + Vector((0.075 * s, 0, 0)), wr + Vector((0.075 * s, 0, 0)), (0.11, 0.15), M["rust"], 0.2, 0.85, 0.045))
    for t in (0.18, 0.9):
        fore.append(ring("ArmBand%s%d" % (side, int(t * 10)), el.lerp(wr, t), wr - el, 0.155, 0.024, M["steel"]))
    return [o for o in up if o not in door], fore, door

def fist(name, side, M, k=1.0):
    """Faust im Rahmen des Handknochens (Finger entlang +Y, Daumen +X, Handfläche links nach -Z): rostiger Block,
    gelbe Fingerglieder vorn, Daumen"""
    zs = 1.0 if side == "Left" else -1.0

    def Pn(x, y, z):
        return Vector((x * k, y * k, z * k * zs))
    parts = [rbox(name + "Block", Pn(0, 0.11, 0.0), (0.12 * k, 0.11 * k, 0.1 * k), 0.035, M["rust"])]
    for i, x in enumerate((-0.078, -0.026, 0.026, 0.078)):
        parts.append(rbox(name + "Finger%d" % i, Pn(x, 0.2, -0.03), (0.024 * k, 0.045 * k, 0.07 * k), 0.012, M["yellow"]))
    parts.append(rbox(name + "Daumen", Pn(0.125, 0.09, -0.05), (0.035 * k, 0.06 * k, 0.04 * k), 0.015, M["rust"]))
    parts.append(rbox(name + "Knoechel", Pn(0, 0.175, 0.05), (0.11 * k, 0.03 * k, 0.04 * k), 0.015, M["steel"]))
    for o in parts:
        box_uv(o)
    return parts

def leg_parts(arm, side, s, M):
    hip, kn, an = B(arm, side + "UpLeg"), B(arm, side + "Leg"), B(arm, side + "Foot")
    kn = Vector((0.23 * s, 0.051, 0.399)); an = Vector((0.248 * s, 0.126, 0.166)); hip = Vector((0.075 * s, 0.084, 0.492))
    thigh, shin, foot = [], [], []
    thigh.append(cyl("Oberschenkel" + side, hip + Vector((0.03 * s, 0, 0.06)), kn, 0.14, M["steel"]))
    shin += hubcap("Knie" + side, kn + Vector((0, -0.12, 0.0)), (0, -1, 0.15), 0.095, M)
    shin.append(ball("Kniegelenk" + side, kn, 0.11, M["steel"]))
    shin.append(along_box("Schienbein" + side, kn, an, (0.16, 0.15), M["rust"], 0.25, 0.82, 0.055))
    hz = along_box("SchienWarn" + side, kn, an, (0.166, 0.156), M["hazard"], 0.34, 0.5, 0.03)
    planar_uv(hz, kn.lerp(an, 0.42), (1, 0, 0), (0, 0, 1), 0.08, 0.08); shin.append(hz)
    shin.append(spring("Knoechelfeder" + side, an + Vector((0, -0.01, 0.0)), (0, 0, 1), 0.11, 0.08, 3.0, 0.02, M["yellow"]))
    foot.append(rbox("Stiefel" + side, (0.27 * s, -0.04, 0.095), (0.19, 0.27, 0.095), 0.055, M["steel"]))
    foot.append(rbox("StiefelKappe" + side, (0.27 * s, -0.22, 0.075), (0.18, 0.09, 0.075), 0.05, M["steel"]))
    for i, dx in enumerate((-0.09, 0.0, 0.09)):
        foot.append(rbox("Zehe%s%d" % (side, i), ((0.27 + dx) * s, -0.29, 0.055), (0.04, 0.045, 0.055), 0.022, M["steel"]))
    foot.append(rbox("StiefelSchaft" + side, (0.255 * s, 0.1, 0.19), (0.14, 0.14, 0.06), 0.045, M["rust"]))
    return thigh, shin, foot

# ---------------------------------------------------------------- Variante

@variante("schrott_koloss", "koloss")
def schrottkoloss_neu(arm, body):
    remove_body(body)
    fix_elbows(arm)
    pose_hands(arm)
    M = schrott_mats(); rnd = random.Random(19)
    head = uv_all(head_parts(M, rnd), M)
    attach_all(head, arm, "Head")
    attach_all(uv_all([cyl("Hals", (0, 0.08, 1.2), (0, 0.04, 1.33), 0.11, M["steel"])], M), arm, "Neck")
    chest, belly, hips = torso_parts(M)
    attach_all(uv_all(chest, M), arm, "Spine2")
    attach_all(uv_all(belly, M), arm, "Spine1")
    attach_all(uv_all(hips, M), arm, "Hips")
    for side, s in (("Left", 1), ("Right", -1)):
        up, fore, door = arm_parts(arm, side, s, M)
        attach_all(uv_all(up, M), arm, side + "Arm")
        attach_all(uv_all(door, M), arm, side + "Shoulder")
        attach_all(uv_all(fore, M), arm, side + "ForeArm")
        for o in fist("Faust" + side, side, M, 1.35):
            place_in_bone(o, arm, "mixamorig:%sHand" % side)
        thigh, shin, foot = leg_parts(arm, side, s, M)
        attach_all(uv_all(thigh, M), arm, side + "UpLeg")
        attach_all(uv_all(shin, M), arm, side + "Leg")
        attach_all(uv_all(foot, M), arm, side + "Foot")
    print("SCHROTTKOLOSS", sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH'), "Flächen")

if __name__ == "__main__":
    run(VAR, OUT)
