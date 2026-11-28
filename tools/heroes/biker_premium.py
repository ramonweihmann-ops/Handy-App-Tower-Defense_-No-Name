# Biker (Wunsch 28.11.2026): bezahlter Held in der Detailtiefe des neuen Fünkchen, nachgebaut nach
# Vorlage_Raw/Nerd_Biker_Premium_v1/biker.png (LIESMICH_CLAUDE.md). Aufruf:
#   blender -b -P tools/heroes/biker_premium.py -- biker <ziel.glb>
# Jacke, Hose, Unterarme und Hals sind eine durchgehende Haut; Helm mit geschlossenem Visier ist starr (kein Gesicht
# dahinter); Aufschläge, Gürtel, Knieschützer, Handschuh-Bänder, Stiefel und Beschläge sind eigene glatte Teile.
# Keine Waffe: Die Vorlage legt keine Kampfmechanik fest, „Shoot“ ist nur ein Platzhalter.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from premium_figur import *

HC = Vector((0.0, -0.01, 1.66))                 # Helmmitte
J = dict(hips=(0, 0, 0.76), spine=(0, 0, 0.9), chest=(0, 0, 1.06), neck=(0, 0.01, 1.29), head=(0, 0.01, 1.37), top=(0, 0.01, 2.0),
         clav=(0.08, 0, 1.26), shoulder=(0.315, 0, 1.24), elbow=(0.49, 0, 1.0), wrist=(0.6, -0.02, 0.785), palm=(0.645, -0.03, 0.685),
         hip=(0.165, 0, 0.74), knee=(0.24, -0.01, 0.5), ankle=(0.295, 0, 0.24), toe=(0.32, -0.3, 0.06))       # breiter Stand, lange Beine
HAND_K = 1.3
BELT_Z = 0.875
V = lambda p: Vector(p)

T_BODY, T_HELM, T_VISOR, T_GLOVE, T_BOOT, T_METAL, T_LEATHER, T_TEAL, T_RIM = range(9)
G_BODY, G_HEAD, G_HANDL, G_HANDR = range(4)

# ---------------------------------------------------------------- Formen

def body_shape():
    parts = [("e", (0, 0, 1.1), (0.31, 0.21, 0.19)), ("e", (0, 0, 0.97), (0.275, 0.2, 0.13)),            # Brust, Taille
             ("e", (0, 0, 0.905), (0.29, 0.212, 0.05)),                                                  # Saum der Jacke
             ("e", (0, 0, 0.78), (0.265, 0.195, 0.12)),                                                  # Becken
             ("c", (0, 0.01, 1.2), (0, 0.01, 1.37), 0.098)]                                              # Hals
    for k in range(12):                                                                                  # Jackenkragen
        a = k * 2 * math.pi / 12
        parts.append(("e", (0.17 * math.sin(a), 0.03 - 0.15 * math.cos(a), 1.275 - 0.02 * math.cos(a)), (0.06, 0.06, 0.05)))
    for s in (1, -1):
        sh, el, wr = [V((p[0] * s, p[1], p[2])) for p in (J["shoulder"], J["elbow"], J["wrist"])]
        d = (wr - el).normalized()
        parts += [("e", sh + V((0.01 * s, 0, 0)), (0.152, 0.14, 0.14)), ("c", sh, el + (sh - el).normalized() * 0.04, 0.128),
                  ("e", el + (sh - el).normalized() * 0.04, (0.15, 0.15, 0.09), V((0, 0, 1)).rotation_difference((el - sh).normalized())),      # aufgeschobener Ärmel
                  ("c", el, wr - d * 0.03, 0.092)]                                                       # nackter Unterarm
        hp, kn, an = [V((p[0] * s, p[1], p[2])) for p in (J["hip"], J["knee"], J["ankle"])]
        parts += [("c", hp, kn, 0.142), ("c", kn, an + V((0, 0, 0.14)), 0.128)]
    return blob("Koerper", parts, voxel=0.013, smooth=7)

def helmet_shape():
    """dicke runde Schale mit Kinnteil und zwei runden Seitenteilen"""
    parts = [("e", HC, (0.345, 0.365, 0.34)), ("e", HC + V((0, -0.1, -0.2)), (0.275, 0.26, 0.125)),       # Schale, Kinnteil
             ("e", HC + V((0, 0.04, -0.21)), (0.285, 0.285, 0.12))]                                       # unterer Rand
    for s in (1, -1):
        parts.append(("e", HC + V((0.33 * s, 0.04, -0.03)), (0.06, 0.12, 0.12)))                         # Seitenteil
    return blob("Helm", parts, voxel=0.012, smooth=6)

def visor(bvh):
    """geschlossenes dunkles Visier: liegt als eigene, leicht erhabene Fläche auf der Schale, mit kräftigem Rahmen.
    Liefert (Visier, Rahmen)."""
    nphi, nz = 26, 9; phis = np.linspace(math.radians(-84), math.radians(84), nphi); zs = np.linspace(-0.15, 0.15, nz)
    def at(ph, dz, lift):
        d = V((math.sin(ph), -math.cos(ph), 0))
        shrink = 1 - 0.5 * (abs(ph) / math.radians(84)) ** 3                                              # zu den Seiten schmaler
        z = HC.z + 0.005 + dz * shrink
        hit = bvh.ray_cast(V((0, HC.y, z)) + d * 1.2, -d, 3.0)[0]
        return hit + d * lift
    bm = bmesh.new(); grid = [[bm.verts.new(at(ph, dz, 0.012)) for ph in phis] for dz in zs]
    for j in range(nz - 1):
        for i in range(nphi - 1):
            bm.faces.new([grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]])
    vis = finish("Visier", bm)
    edge = [at(ph, zs[0], 0.014) for ph in phis] + [at(ph, zs[-1], 0.014) for ph in phis[::-1]]
    rim = loop_tube("Visierrahmen", [tuple(q) for q in edge], 0.034, segs=8)
    return vis, rim

def boot(s):
    x = J["ankle"][0]
    parts = [("e", (x, -0.11, 0.14), (0.165, 0.27, 0.132)), ("e", (x, -0.29, 0.135), (0.16, 0.16, 0.125)),         # Fuß, runde Kappe
             ("e", (x, 0.08, 0.16), (0.152, 0.13, 0.15)), ("c", (x, 0.0, 0.22), (x, 0.0, 0.43), 0.152),           # Ferse, Schaft
             ("e", (x, -0.11, 0.045), (0.182, 0.31, 0.058))]                                                     # dicke Sohle
    g = blob("Stiefel", parts, voxel=0.012, smooth=5, ground=True)
    R = Matrix.Translation((x, 0, 0)) @ Matrix.Rotation(math.radians(-14), 4, 'Z') @ Matrix.Translation((-x, 0, 0))
    g.data.transform(R)
    straps = [torus("Riemen%d" % i, (x, 0.0, zz), (0, 0, 1), 0.16, 0.04, n=20, m=8, flat=0.42) for i, zz in enumerate((0.28, 0.42))]
    buckles = [torus("Schnalle%d" % i, (x + 0.02, -0.176, zz), (0, 1, 0), 0.05, 0.014, n=4, m=6) for i, zz in enumerate((0.28, 0.42))]
    for o in buckles:                                                                                             # viereckiger Rahmen
        c = sum((v.co for v in o.data.vertices), V((0, 0, 0))) / len(o.data.vertices)
        o.data.transform(Matrix.Translation(c) @ Matrix.Rotation(math.radians(45), 4, 'Y') @ Matrix.Translation(-c))
    toe = [rounded_box("Kappe", (x, -0.33, 0.225), (0.08, 0.034, 0.013), 0.011, Euler((math.radians(-25), 0, 0)))]
    for o in straps + buckles + toe:
        o.data.transform(R)
    out = [g], straps, buckles + toe
    if s < 0:
        out = [[mirror_x(o) for o in grp] for grp in out]
    return out[0][0], out[1], out[2]

def jacket_parts(bvh):
    """Aufschläge, Reißverschlusskanten, Nieten, Schulterklappen, Gürtel mit Schnalle und Clip, Knieschützer.
    Liefert (Leder, Metall)."""
    leather, metal = [], []
    def on(x, z, lift=0.0, side=None):
        d = V((0, -1, 0)) if side is None else V(side).normalized()
        hit = bvh.ray_cast(V((x, 0, z)) + d * 1.5 if side is not None else V((x, -1.5, z)), -d if side is not None else V((0, 1, 0)), 4.0)[0]
        return hit + d * lift
    for s in (1, -1):
        # breiter Aufschlag: liegt als flaches Blatt auf der Brust, Spitze nach außen oben
        pts = [on(s * xx, zz, 0.012) for xx, zz in ((0.09, 0.98), (0.12, 1.06), (0.155, 1.15), (0.18, 1.22), (0.165, 1.275))]
        nrm = [V((0, -1, 0.15))] * len(pts)
        lap = ribbon("Aufschlag%d" % s, pts, nrm, 0.072, 0.018, segs=8)
        leather.append(lap)
        zipl = [on(s * xx, zz, 0.03) for xx, zz in ((0.055, 0.93), (0.074, 1.0), (0.104, 1.09), (0.132, 1.17), (0.144, 1.235))]
        metal.append(sweep("Zipper%d" % s, zipl, [0.009] * len(zipl), segs=6))
        for xx, zz in ((0.215, 1.235), (0.175, 1.02)):
            metal.append(sphere("Niete", tuple(on(s * xx, zz, 0.024)), 0.02, segs=(10, 6)))
        ep = V((0.27 * s, 0.0, 1.36)); leather.append(rounded_box("Klappe%d" % s, ep, (0.075, 0.045, 0.014), 0.012, Euler((0, math.radians(-16 * s), 0))))
        metal.append(sphere("Niete", tuple(ep + V((0.035 * s, 0, 0.012))), 0.018, segs=(10, 6)))
        kn = V((J["knee"][0] * s, 0, J["knee"][2] + 0.05)); kp = on(kn.x, kn.z, 0.0)
        leather.append(rounded_box("Knie%d" % s, kp + V((0, 0.012, 0)), (0.085, 0.03, 0.095), 0.03, Euler((math.radians(4), 0, 0))))
        wr, el = V((J["wrist"][0] * s, J["wrist"][1], J["wrist"][2])), V((J["elbow"][0] * s, J["elbow"][1], J["elbow"][2]))
        d = (wr - el).normalized()
        leather.append(torus("Band%d" % s, wr - d * 0.035, d, 0.092, 0.036, n=18, m=8, flat=0.42))
        for a in (0.9, 2.2):
            e1 = d.cross(V((0, 1, 0))).normalized(); e2 = d.cross(e1)
            metal.append(sphere("Niete", tuple(wr - d * 0.035 + (e1 * math.cos(a) * s + e2 * math.sin(a) * -1.0) * 0.108), 0.018, segs=(10, 6)))
    # Gürtel: folgt rundum der Hüfte
    n = 28; pts, nrm = [], []
    for k in range(n + 1):
        a = k * 2 * math.pi / n; d = V((math.sin(a), -math.cos(a), 0))
        hit = bvh.ray_cast(V((0, 0, BELT_Z)), d, 3.0)[0]                                 # von innen: trifft die Hüfte, nicht die Arme
        pts.append(hit + d * 0.006); nrm.append(d)
    leather.append(ribbon("Guertel", pts, nrm, 0.036, 0.016, segs=8))
    fr = on(0.0, BELT_Z, 0.02)
    metal.append(rounded_box("Schnalle", fr, (0.07, 0.014, 0.05), 0.014))
    cl = on(-0.14, BELT_Z - 0.03, 0.02)
    metal += [rounded_box("Clip", cl + V((0, 0, -0.03)), (0.022, 0.012, 0.055), 0.01), sphere("Clipknopf", tuple(cl + V((0, -0.012, -0.065))), 0.022, segs=(10, 6))]
    sl = on(0.065, 0.94, 0.034)
    metal.append(rounded_box("Schieber", sl, (0.017, 0.01, 0.036), 0.008))
    return leather, metal

# ---------------------------------------------------------------- Bemalung

LEA_L, LEA_M, LEA_D = (0.34, 0.31, 0.42), (0.17, 0.15, 0.23), (0.07, 0.06, 0.11)     # Anthrazit mit violettem Stich
SKIN_L, SKIN_M, SKIN_D = (1.0, 0.84, 0.7), (0.99, 0.76, 0.6), (0.86, 0.58, 0.45)
SIL_L, SIL_M, SIL_D = (0.98, 0.97, 1.0), (0.8, 0.78, 0.88), (0.5, 0.47, 0.6)

def paint(g):
    ao = vertex_ao(g, rays=16, dist=0.26)
    T = texels(g); P, N, cov = T["P"], T["N"], T["cov"]
    AO = texel_values(T, ao)
    TG = np.rint(texel_values(T, part_tags(g))).astype(int)
    x, y, z = P[..., 0], P[..., 1], P[..., 2]; ax = np.abs(x)
    lit = smoothstep(0.05, 0.95, np.clip(N[..., 2] * 0.42 + 0.5 - 0.12 * N[..., 1], 0, 1))
    occ = np.clip(AO * 2.2, 0, 1) ** 0.85
    sel = lambda t: ((TG == t) & cov).astype(np.float32)
    col = np.zeros(P.shape, np.float32); em = np.zeros(P.shape, np.float32)
    def lay(mask, c):
        nonlocal col
        col = col * (1 - mask[..., None]) + c * mask[..., None]
    leather = three(LEA_D, LEA_M, LEA_L, lit)
    leather = mix(leather, LEA_D, 0.25 * smoothstep(0.5, 0.72, fbm3(P * f3((1.0, 1.0, 2.4)), 5.0, 4, 3)))
    skin = three(SKIN_D, SKIN_M, SKIN_L, lit)
    # ---- Körper: Jacke, Hemd, Hals, Unterarme, Hose
    bd = sel(T_BODY)
    el, wr = V(J["elbow"]), V(J["wrist"]); d = (wr - el); L = d.length; d = d / L
    Pa = np.stack([ax, y, z], -1); rel = Pa - f3(el); t = (rel @ f3(d)) / L
    rad = np.linalg.norm(rel - (rel @ f3(d))[..., None] * f3(d), axis=-1)
    fore = smoothstep(0.1, 0.13, t) * (rad < 0.15) * (ax > 0.4) * bd                                      # nackter Unterarm
    neck = smoothstep(1.275, 1.285, z) * (np.hypot(x, y - 0.01) < 0.125) * bd
    front = smoothstep(-0.2, -0.5, N[..., 1])
    w = np.interp(z, [0.92, 1.0, 1.08, 1.17, 1.25, 1.3], [0.045, 0.066, 0.095, 0.125, 0.142, 0.15]).astype(np.float32)
    shirt = smoothstep(w + 0.003, w - 0.003, ax) * front * (z > 0.922) * (z < 1.285) * bd * (1 - neck)
    tro = smoothstep(BELT_Z + 0.02, BELT_Z + 0.014, z) * (ax < 0.42) * bd * (1 - fore)
    jc = mix(leather, (0.05, 0.03, 0.1), 0.45 * occ)
    tc = three((0.07, 0.06, 0.11), (0.15, 0.13, 0.21), (0.29, 0.26, 0.37), lit)
    tc = mix(tc, (0.09, 0.06, 0.15), 0.3 * smoothstep(0.5, 0.72, fbm3(P * f3((1.0, 1.0, 2.2)), 5.5, 9, 3)))
    tc = mix(tc, (0.07, 0.04, 0.12), 0.5 * smoothstep(0.006, 0.002, ax) * front * (z > 0.6))             # Naht vorn
    lay(bd, jc)
    lay(tro, mix(tc, (0.04, 0.02, 0.08), 0.45 * occ))
    sh = three((0.66, 0.6, 0.84), (0.84, 0.8, 0.96), (0.96, 0.94, 1.0), lit)
    sh = mix(sh, (0.6, 0.54, 0.8), 0.5 * smoothstep(0.008, 0.003, np.abs(z - 1.235 + 0.25 * ax)) * (ax < 0.12))    # Halsausschnitt
    lay(shirt, mix(sh, (0.44, 0.38, 0.66), 0.4 * occ))
    lay(np.clip(fore + neck, 0, 1), mix(skin, (0.72, 0.42, 0.34), 0.38 * occ))
    # ---- Helm: zwei helle Längsstreifen, Lüftungsschlitze am Kinn, Seitenteile
    hm = sel(T_HELM)
    hc = three((0.06, 0.05, 0.1), (0.15, 0.13, 0.22), (0.38, 0.34, 0.5), lit)
    stripe = smoothstep(0.04, 0.052, ax) * smoothstep(0.155, 0.143, ax) * (z > HC.z + 0.17) * smoothstep(-0.34, -0.3, y - HC.y) + \
             smoothstep(0.04, 0.052, ax) * smoothstep(0.155, 0.143, ax) * (y > HC.y) * (z > HC.z - 0.1)
    hc = hc * (1 - np.clip(stripe, 0, 1)[..., None]) + three((0.62, 0.58, 0.8), (0.86, 0.83, 0.96), (1.0, 1.0, 1.0), lit) * np.clip(stripe, 0, 1)[..., None]
    for k in (-1, 0, 1):                                                                                 # drei Schlitze am Kinnteil
        hc = mix(hc, (0.05, 0.03, 0.09), 0.85 * smoothstep(0.03, 0.022, np.abs(x - 0.085 * k)) * smoothstep(0.011, 0.006, np.abs(z - (HC.z - 0.265))) * (y < HC.y - 0.2))
    side = np.hypot(y - (HC.y + 0.04), z - (HC.z - 0.03))
    hc = mix(hc, (0.1, 0.07, 0.16), 0.5 * smoothstep(0.012, 0.004, np.abs(side - 0.085)) * (ax > 0.33))  # Ring im Seitenteil
    lay(hm, mix(hc, (0.04, 0.02, 0.08), 0.4 * occ))
    lay(sel(T_RIM), mix(three((0.06, 0.05, 0.1), (0.14, 0.12, 0.2), (0.32, 0.28, 0.42), lit), (0.03, 0.02, 0.06), 0.4 * occ))
    vs = sel(T_VISOR)
    vc = gradient((0.03, 0.02, 0.07), (0.13, 0.1, 0.22), smoothstep(HC.z - 0.14, HC.z + 0.16, z))          # unten tief, oben heller
    streak = smoothstep(0.035, 0.012, np.abs((x * 0.8 + (z - HC.z) * 0.9) - 0.06)) + 0.6 * smoothstep(0.018, 0.006, np.abs((x * 0.8 + (z - HC.z) * 0.9) - 0.14))
    vc = mix(vc, (0.42, 0.36, 0.6), 0.5 * np.clip(streak, 0, 1) * (y < HC.y - 0.1))                       # weiche schräge Spiegelung
    lay(vs, vc)
    # ---- Handschuhe: fingerlos, Fingerkuppen bleiben Haut
    gl = sel(T_GLOVE)
    gcol = mix(leather, (0.05, 0.03, 0.1), 0.4 * occ)
    for sfx, sg in ((".L", 1), (".R", -1)):
        F0 = np.array(HAND_FRAMES[sfx], np.float32); w0 = f3((J["wrist"][0] * sg, J["wrist"][1], J["wrist"][2]))
        loc = (P - w0) @ F0                                                                              # Lage im Maß der Hand
        tips = np.clip(smoothstep(0.118, 0.126, loc[..., 1] / HAND_K) + smoothstep(-0.03, -0.04, loc[..., 2] / HAND_K) * (loc[..., 1] / HAND_K > 0.045), 0, 1) * (x * sg > 0)
        gcol = np.where((x * sg > 0)[..., None], gcol * (1 - tips[..., None]) + mix(skin, (0.72, 0.42, 0.34), 0.4 * occ) * tips[..., None], gcol)
    lay(gl, gcol)
    # ---- Stiefel, Leder, Metall, Leuchte
    bt = sel(T_BOOT)
    bc = three((0.06, 0.05, 0.1), (0.14, 0.12, 0.2), (0.3, 0.27, 0.4), lit)
    bc = mix(bc, (0.04, 0.03, 0.08), 0.7 * smoothstep(0.085, 0.076, z))                                   # Profilsohle dunkler
    bc = mix(bc, (0.03, 0.02, 0.06), 0.7 * (z < 0.08) * smoothstep(0.6, 0.9, 0.5 + 0.5 * np.sin(y * 60)))
    lay(bt, mix(bc, (0.03, 0.02, 0.06), 0.45 * occ))
    lay(sel(T_LEATHER), mix(three((0.09, 0.08, 0.14), (0.21, 0.18, 0.28), (0.4, 0.36, 0.5), lit), (0.04, 0.03, 0.08), 0.45 * occ))
    lay(sel(T_METAL), mix(three(SIL_D, SIL_M, SIL_L, lit), (0.3, 0.27, 0.42), 0.4 * occ))
    tl = sel(T_TEAL); tcol = three((0.08, 0.6, 0.66), (0.2, 0.9, 0.9), (0.7, 1.0, 0.98), lit)
    lay(tl, tcol); em += tcol * (0.9 * tl)[..., None]
    finish_paint(T, col, em, strength=1.0)

# ---------------------------------------------------------------- Haltung und Bewegungen

def stand(arm, breathe=0.0, lean=0.0, hop=0.0, twist=0.0, right=None, left=None, nod=0.0):
    """Haltung der Vorlage: breiter Stand, Fäuste seitlich vor dem Körper, Oberkörper leicht gedreht"""
    reset_pose(arm)
    move_world(arm, "Root", (0, 0, hop))
    rot_world(arm, "Spine", (0, 0, 1), 5 + twist); rot_world(arm, "Chest", (0, 0, 1), 6 + twist)
    rot_world(arm, "Chest", (1, 0, 0), breathe + lean); rot_world(arm, "Head", (0, 0, 1), -9 - 2 * twist); rot_world(arm, "Head", (1, 0, 0), nod)
    for sfx, sg in ((".L", 1), (".R", -1)):
        pass                                                                    # der breite Stand steckt schon in der Ruhelage
    update()
    wr = right or (V((-0.5, -0.2, 0.93)), V((0.15, -0.75, -0.6)), V((-0.75, -0.5, 0.3)))
    wl = left or (V((0.56, -0.02, 0.86)), V((-0.1, -0.3, -0.95)), V((0.95, -0.2, 0.0)))
    reach(arm, ".R", wr[0], (-0.8, 0.5, 0.0)); turn_hand(arm, ".R", wr[1], wr[2])
    reach(arm, ".L", wl[0], (0.8, 0.5, 0.1)); turn_hand(arm, ".L", wl[1], wl[2])

def animate(arm):
    S = lambda t, ph=0.0: math.sin((t - ph) * 2 * math.pi)
    idle = [(i * 8, (lambda t=i / 8.0: stand(arm, breathe=1.5 * S(t), twist=1.0 * S(t, 0.1)))) for i in range(9)]
    pose = [(i * 6, (lambda t=i / 8.0: stand(arm, breathe=1.2 * S(t), twist=0.8 * S(t, 0.1)))) for i in range(9)]
    # Platzhalter, bis die Kampfmechanik feststeht: kurzer Ruck nach vorn und zurück
    shoot = [(0, lambda: stand(arm)), (3, lambda: stand(arm, lean=4, twist=-3)), (7, lambda: stand(arm, lean=1, twist=1)), (12, lambda: stand(arm))]
    def cheer(t):
        up = 0.5 + 0.5 * S(t * 2)
        stand(arm, hop=0.1 * abs(S(t)), lean=-3, nod=-6,
              right=(V((-0.4, -0.1, 1.5 + 0.1 * up)), V((-0.1, 0.0, 1.0)), V((-1, 0.2, 0))))
    win = [(i * 6, (lambda t=i / 8.0: cheer(t))) for i in range(9)]
    make_actions(arm, [("Idle", idle), ("Pose", pose), ("Shoot", shoot), ("Victory", win)])

# ---------------------------------------------------------------- Ablauf

def build(out):
    body = to_tris(body_shape(), 6500); helm = to_tris(helmet_shape(), 3200)
    dg = bpy.context.evaluated_depsgraph_get()
    bvh_b = BVHTree.FromObject(body, dg); bvh_h = BVHTree.FromObject(helm, dg)
    arm = biped(J)
    mark(body, T_BODY, G_BODY)
    auto_bind(body, arm, {"Hips", "Spine", "Chest", "Neck"} | {b + s for b in ("Shoulder", "UpperArm", "ForeArm", "UpLeg", "Leg", "Foot") for s in (".L", ".R")})
    parts = [body, mark(helm, T_HELM, G_HEAD, "Head")]
    vis, rim = visor(bvh_h)
    parts += [mark(vis, T_VISOR, G_HEAD, "Head"), mark(rim, T_RIM, G_HEAD, "Head")]
    parts.append(mark(sphere("Leuchte", tuple(HC + V((-0.305, -0.2, -0.13))), 0.028, segs=(12, 8)), T_TEAL, G_HEAD, "Head"))
    for s, sfx in ((-1, ".R"), (1, ".L")):                                                               # Fäuste
        h = to_tris(hand_mesh("Hand" + sfx, HAND_K, (0.95, 0.97, 0.98, 1.0), thumb=0.9, thumb_in=1.0), 1100)
        wr, el = V((J["wrist"][0] * s, J["wrist"][1], J["wrist"][2])), V((J["elbow"][0] * s, J["elbow"][1], J["elbow"][2]))
        Y = (wr - el).normalized()
        if s > 0:
            mirror_x(h); X = V((0, -1, 0))
        else:
            X = V((0, 1, 0))
        Z = X.cross(Y).normalized(); X = Y.cross(Z)
        place(h, wr - Y * 0.01, X, Y, Z)
        HAND_FRAMES[sfx] = Matrix((X, Y, Z)).transposed()
        parts.append(mark(h, T_GLOVE, G_HANDL if s > 0 else G_HANDR, "Hand" + sfx))
    for s, sfx in ((1, ".L"), (-1, ".R")):
        bt, straps, metal = boot(s)
        parts.append(mark(to_tris(bt, 1100), T_BOOT, G_BODY, "Foot" + sfx))
        parts += [mark(o, T_LEATHER, G_BODY, "Foot" + sfx) for o in straps] + [mark(o, T_METAL, G_BODY, "Foot" + sfx) for o in metal]
    leather, metal = jacket_parts(bvh_b)
    for o in leather + metal:
        c = sum((v.co for v in o.data.vertices), V((0, 0, 0))) / len(o.data.vertices)
        sfx = ".L" if c.x > 0 else ".R"
        if o.name.startswith("Guertel") or o.name.startswith("Schnalle") or o.name.startswith("Clip"):
            bone = "Hips"
        elif o.name.startswith("Knie"):
            bone = "UpLeg" + sfx
        elif o.name.startswith("Band") or (o.name.startswith("Niete") and abs(c.x) > 0.45):
            bone = "ForeArm" + sfx
        elif o.name.startswith("Klappe") or (o.name.startswith("Niete") and c.z > 1.3):
            bone = "Shoulder" + sfx
        else:
            bone = "Chest"
        parts.append(mark(o, T_LEATHER if o in leather else T_METAL, G_BODY, bone))
    g = join_parts(parts, "Biker")
    for p in g.data.polygons:
        p.use_smooth = True
    g.data.materials.clear(); g.data.materials.append(image_material("Biker", int(os.environ.get("TEXTUR", "2048")), color=(0.22, 0.17, 0.3), rough=0.5))
    smart_uv(g, margin=0.004)
    paint(g)
    base = g.data.materials[0]
    gloss = base.copy(); gloss.name = "Lack"; gloss.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.16
    metal_m = base.copy(); metal_m.name = "Metall"
    pr = metal_m.node_tree.nodes["Principled BSDF"]; pr.inputs["Metallic"].default_value = 0.85; pr.inputs["Roughness"].default_value = 0.28
    g.data.materials.append(gloss); g.data.materials.append(metal_m)
    tags = np.rint(part_tags(g)).astype(int)
    for p in g.data.polygons:
        t = tags[p.vertices[0]]
        p.material_index = 1 if t in (T_HELM, T_VISOR, T_RIM) else 2 if t == T_METAL else 0
    bpy.context.scene.render.fps = FPS
    g.parent = arm; md = g.modifiers.new("Armature", 'ARMATURE'); md.object = arm
    reset_pose(arm)
    animate(arm)
    add_muzzle(arm, "Chest", V((0, -0.45, 1.05)))
    co = np.array([tuple(v.co) for v in g.data.vertices])
    print("MASSE x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (co[:, 0].min(), co[:, 0].max(), co[:, 1].min(), co[:, 1].max(), co[:, 2].min(), co[:, 2].max()))
    print("DREIECKE", sum(len(p.vertices) - 2 for p in g.data.polygons), "AKTIONEN", [(a_.name, int(a_.frame_range[1])) for a_ in bpy.data.actions])
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS',
                              export_yup=True, export_apply=False, export_force_sampling=True,
                              export_image_format='JPEG', export_jpeg_quality=90)

if __name__ == "__main__":
    bpy.ops.wm.read_factory_settings(use_empty=True)
    build(OUT)
    print("FERTIG", OUT)
