# Monster der Welt „Thron der Zauberin“ (Planet Schlangenhöhle, Boss Schlangenzauberin),
# Vorlage_Raw/Thron_der_Zauberin_Monster_v1 (vier Bilder vom Nutzer, 27.11.2026). Alle drei haben zwei Arme und zwei Beine.
#   thron_krabbler   Haubenwicht: kleiner Wicht mit großer Kobrahaube, Goldreif am Hals, Skelett Krabbler
#   thron_zombie     Zirkelzischer: schlanker Schlangenpriester mit langem Hals, Weste und Goldreif, Skelett Zombie
#   thron_brecher    Thronwächter: breiter Beschützer mit Kristall-Schulterplatten und Goldrand, Skelett Brecher
# Farben und Gesicht wie bei den Schlangennest-Monstern (tools/monster/schlangennest.py): dunkelviolett mit klarem
# Hell-Dunkel-Verlauf, heller Bauch, magentafarbene Leuchtstreifen, Leuchtaugen mit kleiner Pupille.
# Aufruf: blender -b -P tools/monster/zauberthron.py -- <variante> <ziel.glb>
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schlangennest import *

def violet(N):
    """Haut mit klarem Verlauf: oben hell, zur Seite satt violett, unten dunkel"""
    tz = np.clip(N[..., 2] * 0.5 + 0.5, 0, 1)
    return np.where((tz < 0.5)[..., None], gradient((0.1, 0.035, 0.27), (0.24, 0.095, 0.5), tz * 2),
                    gradient((0.24, 0.095, 0.5), (0.46, 0.26, 0.84), smoothstep(0.5, 1.0, tz)))

def belly_col(N):
    return gradient((0.48, 0.37, 0.8), (0.86, 0.8, 1.0), smoothstep(0.1, 0.9, np.clip(0.55 + N[..., 2] * 0.35 - N[..., 1] * 0.35, 0, 1)))

def shade(col, AO, keep):
    """gemalte Schatten in Falten und unter Überhängen"""
    occ = np.clip(AO * 2.2, 0, 1) ** 0.85
    return mix(col, (0.08, 0.03, 0.2), 0.58 * occ * keep)

def surf(bvh, outer, target, lift=0.0):
    """Punkt auf der Haut: von outer in Richtung target"""
    o = Vector(outer); d = (Vector(target) - o).normalized()
    hit, n, _, _ = bvh.ray_cast(o, d, 6.0)
    return tuple(hit + n * lift) if hit is not None else tuple(target)

def bind_biped(body, arm, rigid):
    """Bone Heat nur mit den Hauptknochen; rigid(Punkt) -> Knochen für starre Bereiche (Kopf mit Haube und Gesicht)"""
    keep = {"mixamorig:" + b for b in MAIN_BONES}
    saved = {b.name: b.use_deform for b in arm.data.bones}
    for b in arm.data.bones:
        b.use_deform = b.name in keep
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    for b in arm.data.bones:
        b.use_deform = saved[b.name]
    fixed = {}
    for v in body.data.vertices:
        r = rigid(v.co)
        if r:
            fixed.setdefault(r, []).append(v.index)
    for bone, idx in fixed.items():
        for g in body.vertex_groups:
            g.remove(idx)
        (body.vertex_groups.get("mixamorig:" + bone) or body.vertex_groups.new(name="mixamorig:" + bone)).add(idx, 1.0, 'REPLACE')

def rigid_parts(parts, bone):
    for o in parts:
        group_all(o, "mixamorig:" + bone)
    return parts

def limb(R, pts, radii):
    for (a, b), r in zip(zip(pts, pts[1:]), radii):
        mb_caps(R, tuple(a), tuple(b), r)

def hand_shape(R, wrist, elbow, s, size, fingers=3):
    """Hand mit dicken, leicht gekrümmten Fingern und Daumen (s = Seite ±1)"""
    d = (Vector(wrist) - Vector(elbow)).normalized()
    fw = Vector((0, -1, 0)); inw = Vector((-s, 0, 0))
    palm = Vector(wrist) + d * (0.7 * size)
    mb_ell(R, tuple(palm), (0.85 * size, 0.95 * size, 0.95 * size))
    for k in range(fingers):
        o = (k - (fingers - 1) / 2) * 0.62 * size
        a = palm + d * (0.6 * size) + fw * (-o)
        b = a + d * (0.75 * size) + inw * (0.25 * size)
        c = b + d * (0.4 * size) + inw * (0.5 * size)
        mb_caps(R, tuple(a), tuple(b), 0.36 * size); mb_caps(R, tuple(b), tuple(c), 0.3 * size)
    t0 = palm + fw * (0.7 * size) + d * (0.1 * size)
    mb_caps(R, tuple(t0), tuple(t0 + fw * (0.45 * size) + d * (0.6 * size) + inw * (0.2 * size)), 0.34 * size)

def foot_shape(R, ankle, size, toes=3):
    """breiter Fuß mit stumpfen Zehen, steht flach auf dem Boden"""
    ax, ay = ankle[0], ankle[1]
    mb_ell(R, (ax, ay - 0.5 * size, 0.42 * size), (0.78 * size, 1.1 * size, 0.46 * size))
    for k in range(toes):
        o = (k - (toes - 1) / 2) * 0.5 * size
        mb_ball(R, (ax + o, ay - 1.42 * size + 0.12 * size * abs(k - (toes - 1) / 2), 0.3 * size), 0.33 * size)

def snake_head(R, H, k):
    mb_ell(R, H, (0.25 * k, 0.24 * k, 0.2 * k))
    mb_ell(R, H + Vector((0, -0.15, -0.045)) * k, (0.165 * k, 0.115 * k, 0.08 * k))
    mb_ell(R, H + Vector((0, -0.1, -0.13)) * k, (0.17 * k, 0.15 * k, 0.07 * k))
    for s in (1, -1):
        mb_ell(R, H + Vector((0.15 * s, -0.04, -0.05)) * k, (0.09 * k, 0.12 * k, 0.09 * k))

def stripes(P, lines, width):
    """Leuchtstreifen: breite, an den Enden spitz zulaufende Bögen; lines = Listen von Punkten auf der Haut"""
    m = np.zeros(P.shape[:-1], np.float32); core = np.zeros(P.shape[:-1], np.float32)
    for pts in lines:
        n = len(pts) - 1
        for k, (a, b) in enumerate(zip(pts, pts[1:])):
            t = (k + 0.5) / n
            w = width * (0.35 + 0.65 * math.sin(math.pi * t) ** 0.6)
            d = seg_dist(P, [a, b])
            m = np.maximum(m, np.clip(1.6 * (1 - d / w), 0, 1)); core = np.maximum(core, np.clip(1.8 * (1 - d / (w * 0.45)), 0, 1))
    return m, core

def glow(col, em, m, core):
    col = mix(col, CRACK, m)
    col = mix(col, (1.0, 0.8, 1.0), 0.55 * core)
    em += f3(CRACK_EM) * m[..., None] + f3((1.0, 0.7, 1.0)) * (0.5 * core)[..., None]
    return col, em

def finish_paint(T, col, em, strength=1.5):
    cov = T["cov"]
    T["out"][..., :3] = np.where(cov[..., None], np.clip(col, 0, 1), T["out"][..., :3])
    T["em"][..., :3] = np.where(cov[..., None], np.clip(em, 0, 1), 0)
    commit(T, strength=strength)

def gold_ring(name, center, R, r, tilt=0.0, squash=1.0):
    """Goldreif: flacher, breiter Ring (wie ein Halsreif)"""
    bm = bmesh.new(); rings = []
    rot = Matrix.Rotation(math.radians(tilt), 3, 'X')
    for i in range(40):
        a = i * 2 * math.pi / 40
        out = Vector((math.cos(a), math.sin(a) * squash, 0))
        rings.append([bm.verts.new(Vector(center) + rot @ (out * (R + r * 0.75 * math.cos(q)) + Vector((0, 0, r * 1.25 * math.sin(q))))) for q in [j * 2 * math.pi / 10 for j in range(10)]])
    for i in range(40):
        a, b = rings[i], rings[(i + 1) % 40]
        for j in range(10):
            bm.faces.new([a[j], b[j], b[(j + 1) % 10], a[(j + 1) % 10]])
    return finish(name, bm)

# ================================================================ Haubenwicht (leicht, Krabbler)

WH = Vector((0.0, -0.1, 1.17))                  # Gesichtsmitte: der Kopf ist eine große Kugel, das Gesicht sitzt vorn unten
WK = 1.5
HOOD_C, HOOD_R = Vector((0.0, 0.05, 1.34)), Vector((0.56, 0.44, 0.4))

def hood_pt(deg, elev):
    a = math.radians(deg); e = math.radians(elev)
    return tuple(HOOD_C + Vector((HOOD_R.x * math.cos(e) * math.sin(a), -HOOD_R.y * math.cos(e) * math.cos(a), HOOD_R.z * math.sin(e))))

def hood_rim():
    """Dicker Rand der Haube: Bogen über der Stirn, seitlich am Gesicht hinunter bis zum Kiefer"""
    pts = []; radii = []
    for i in range(33):
        t = math.radians(-118 + 236 * i / 32)
        x = 0.47 * math.sin(t); z = 1.1 + 0.31 * math.cos(t)
        q = 1 - (x / HOOD_R.x) ** 2 - ((z - HOOD_C.z) / HOOD_R.z) ** 2
        pts.append((x, HOOD_C.y - HOOD_R.y * math.sqrt(max(0.03, q)) - 0.025, z))
        radii.append(0.052 * math.sin(math.pi * i / 32) ** 0.35 if 0 < i < 32 else 0.0)
    return tube("Haubenrand", pts, radii, segs=12)

def wicht_shape(arm):
    R = mb_family("Wicht")
    mb_ell(R, (0, 0.0, 0.66), (0.19, 0.16, 0.19))                                  # Rumpf
    mb_ell(R, (0, 0.01, 0.47), (0.25, 0.18, 0.14))                                  # breites Becken
    mb_caps(R, (0, 0.0, 0.8), (0, -0.02, 1.0), 0.11)                                # kurzer Hals
    snake_head(R, WH, WK)
    mb_ell(R, HOOD_C, HOOD_R)                                                       # große Kobrahaube über und hinter dem Gesicht
    for s, side in ((1, "Left"), (-1, "Right")):
        sh, el, wr = B(arm, side + "Arm"), B(arm, side + "ForeArm"), B(arm, side + "Hand")
        limb(R, [sh, el, wr], [0.074, 0.07])
        hand_shape(R, wr, el, s, 0.085)
        hip, kn, an = B(arm, side + "UpLeg"), B(arm, side + "Leg"), B(arm, side + "Foot")
        limb(R, [(hip.x + 0.02 * s, hip.y, hip.z), (kn.x + 0.03 * s, kn.y, kn.z), (an.x + 0.02 * s, an.y, 0.13)], [0.135, 0.125])
        foot_shape(R, (an.x + 0.03 * s, an.y + 0.02), 0.185)
    return mb_to_mesh(R)

def paint_wicht(g, arm):
    bvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    ao = vertex_ao(g, rays=18, dist=0.3)
    T = texels(g); P, N, cov = T["P"], T["N"], T["cov"]
    AO = texel_values(T, ao)
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    k = WK; H = WH
    jaw, mouth, hd = face_masks(P, H, k, MOUTH)
    e_h = np.linalg.norm((P - f3(HOOD_C)) / f3(HOOD_R), axis=-1)
    face = (hd < 1.0) & (y < H.y + 0.06)
    hood = (z > 0.96) & ~face
    col = violet(N)
    em = np.zeros(P.shape, np.float32)
    # Bauchplatte: helles Schild vorn am Rumpf mit drei Querlinien
    wz = 0.125 * np.sqrt(np.clip(1 - ((z - 0.62) / 0.2) ** 2, 0, 1))
    plate = smoothstep(0.012, -0.012, np.abs(x) - wz) * (z > 0.42) * (z < 0.83) * smoothstep(-0.1, -0.35, N[..., 1]) * (~hood) * (~face)
    bel = np.clip(np.maximum(plate, jaw * face), 0, 1)
    bcol = belly_col(N)
    lines = np.zeros(P.shape[:-1], np.float32)
    for zl in (0.52, 0.62, 0.72):
        lines = np.maximum(lines, np.clip(1.5 * (1 - np.abs(z + 0.9 * x * x - zl) / 0.008), 0, 1))
    bcol = mix(bcol, (0.42, 0.3, 0.72), 0.75 * lines * plate)
    col = col * (1 - bel[..., None]) + bcol * bel[..., None]
    col = mix(col, (0.1, 0.03, 0.18), mouth * face)
    # Leuchtstreifen: Bögen auf der Haube (vorn, seitlich, hinten) und auf den Oberschenkeln
    lines3 = []
    for s in (1, -1):
        lines3.append([hood_pt(s * d, e) for d, e in ((4, 50), (18, 42), (36, 34), (54, 28), (72, 22), (86, 18))])
        lines3.append([hood_pt(s * d, e) for d, e in ((84, 62), (100, 44), (110, 22), (112, 0), (106, -20))])
        lines3.append([hood_pt(s * d, e) for d, e in ((170, 66), (154, 48), (144, 26), (144, 4), (152, -18))])
    hm, hc = stripes(P, lines3, 0.05)
    tm = np.zeros(P.shape[:-1], np.float32); tc = np.zeros(P.shape[:-1], np.float32)
    for s, side in ((1, "Left"), (-1, "Right")):
        kn = B(arm, side + "Leg")
        pts = [surf(bvh, (kn.x + s * dx, -1.0, kn.z + dz), (kn.x + s * dx, 1.0, kn.z + dz)) for dx, dz in ((-0.07, 0.13), (-0.02, 0.09), (0.04, 0.04), (0.09, -0.03), (0.12, -0.1))]
        a_, b_ = stripes(P, [pts], 0.04); tm = np.maximum(tm, a_); tc = np.maximum(tc, b_)
    m = np.maximum(hm * hood * (e_h > 0.86), tm * (z < 0.45)); core = np.maximum(hc * hood * (e_h > 0.86), tc * (z < 0.45))
    col = shade(col, AO, (1 - m) * (1 - 0.5 * bel))
    col, em = glow(col, em, m, core)
    finish_paint(T, col, em)

@variante("thron_krabbler", "krabbler")
def haubenwicht(arm, body):
    remove_body(body)
    M = snake_mats(1024)
    g = join_parts([wicht_shape(arm), hood_rim()], "Haubenwicht")
    finish_skin(g, 0.011, 0.3)
    reduce(g, 0.16)
    g.data.materials.clear(); g.data.materials.append(M["skin"])
    smart_uv(g)
    paint_wicht(g, arm)
    bvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    bind_biped(g, arm, lambda c: "Head" if c.z > 0.97 else None)
    parts = rigid_parts(snake_face(M, bvh, WH, WK, tongue=False, teeth=True), "Head")
    parts += rigid_parts([give(gold_ring("Halsreif", (0, -0.005, 0.845), 0.205, 0.042, tilt=-10.0, squash=0.86), M["gold"])], "Spine2")
    g = join_parts([g] + parts, "Haubenwicht")
    print("HAUBENWICHT", len(g.data.polygons), "Flächen")

# ================================================================ Zirkelzischer (mittel, Zombie)

ZH = Vector((0.0, -0.1, 1.58))                  # Kopfmitte auf dem langen Hals
ZK = 0.72
Z_NECK = [(0.0, 0.0, 1.16), (0.0, 0.03, 1.28), (0.0, 0.04, 1.4), (0.0, 0.0, 1.5), (0.0, -0.05, 1.56)]

def zischer_shape(arm):
    R = mb_family("Zischer")
    mb_ell(R, (0, 0.0, 1.0), (0.165, 0.12, 0.17))                                  # schmale Brust
    mb_ell(R, (0, 0.0, 0.82), (0.14, 0.11, 0.16))                                  # Taille
    mb_ell(R, (0, 0.0, 0.68), (0.16, 0.115, 0.1))                                  # Becken
    for s, side in ((1, "Left"), (-1, "Right")):
        sh, el, wr = B(arm, side + "Arm"), B(arm, side + "ForeArm"), B(arm, side + "Hand")
        mb_ball(R, (sh.x, sh.y, sh.z), 0.075)                                       # Schulter
        limb(R, [sh, el, wr], [0.055, 0.05])
        hand_shape(R, wr, el, s, 0.07, fingers=3)
        hip, kn, an = B(arm, side + "UpLeg"), B(arm, side + "Leg"), B(arm, side + "Foot")
        limb(R, [hip, kn, (an.x, an.y, 0.2), (an.x, an.y, 0.1)], [0.082, 0.07, 0.085])
        foot_shape(R, (an.x, an.y + 0.02), 0.15)
    g = mb_to_mesh(R)
    P, _ = smooth3(Z_NECK, 24, passes=3)
    rad = np.interp(np.linspace(0, 1, 24), [0, 0.25, 0.7, 1], [0.115, 0.1, 0.1, 0.11])
    H = mb_family("Zischerkopf")
    snake_head(H, ZH, ZK)
    return [g, ring_tube("Hals", P, rad, depth=0.74), mb_to_mesh(H)]

def vest_hem(mat):
    """Saum der Weste: kurzer, leicht ausgestellter Rand über der Hüfte"""
    prof = [(0.72, 0.15), (0.69, 0.172), (0.655, 0.19), (0.645, 0.185), (0.66, 0.165), (0.7, 0.14)]
    o = lathe("Westensaum", prof, segs=36)
    for v in o.data.vertices:
        v.co.y *= 0.76
    return give(o, mat)

def paint_zischer(g, arm):
    bvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    ao = vertex_ao(g, rays=18, dist=0.3)
    T = texels(g); P, N, cov = T["P"], T["N"], T["cov"]
    AO = texel_values(T, ao)
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    k = ZK; H = ZH
    jaw, mouth, hd = face_masks(P, H, k, MOUTH)
    head = hd < 1.0
    col = violet(N)
    em = np.zeros(P.shape, np.float32)
    torso = (np.abs(x) < 0.2) & (z > 0.66) & (z < 1.19) & ~head
    # Weste: dunkler Stoff mit hellem Rand, vorn offen; darin der helle Bauch mit Querlinien
    open_w = 0.035 + 0.05 * smoothstep(0.78, 1.16, z)                           # Ausschnitt wird nach oben breiter
    front = smoothstep(-0.05, -0.3, N[..., 1])
    chest = smoothstep(0.008, -0.008, np.abs(x) - open_w) * front * (z > 0.74) * (z < 1.2) * torso
    trim = np.clip(1.4 * (1 - np.abs(np.abs(x) - open_w - 0.016) / 0.013), 0, 1) * front * (z > 0.74) * torso
    trim = np.maximum(trim, np.clip(1.4 * (1 - np.abs(z - 0.7) / 0.014), 0, 1) * torso)
    vest = torso * (1 - chest)
    col = mix(col, (0.15, 0.055, 0.34), 0.75 * vest)
    col = mix(col, (0.44, 0.27, 0.78), 0.9 * trim * (1 - chest))
    # heller Bauch: Brust im Ausschnitt, Vorderseite des Halses, Unterkiefer
    cy = np.interp(z, np.asarray(Z_NECK)[:, 2], np.asarray(Z_NECK)[:, 1])
    nfront = -(y - cy) / np.maximum(np.sqrt((y - cy) ** 2 + x * x), 1e-4)
    neck = (z > 1.2) * smoothstep(H.z - 0.1 * k, H.z - 0.19 * k, z) * (np.abs(x) < 0.13)
    nbel = smoothstep(0.35, 0.52, nfront) * neck
    bel = np.clip(np.maximum(np.maximum(chest, nbel), jaw * head), 0, 1)
    bcol = belly_col(N)
    band = np.abs((((z + 1.0 * x * x) / 0.06) % 1.0) - 0.5) * 2
    bcol = mix(bcol, (0.42, 0.3, 0.72), 0.7 * smoothstep(0.76, 0.93, band) * np.maximum(chest, nbel) * (1 - jaw))
    col = col * (1 - bel[..., None]) + bcol * bel[..., None]
    col = mix(col, (0.1, 0.03, 0.18), mouth * head)
    # Leuchtstreifen: zwei Bögen über dem Kopf, je einer an Unterarm, Oberschenkel und Unterschenkel
    lines = []
    for s, side in ((1, "Left"), (-1, "Right")):
        lines.append([surf(bvh, (s * dx, dy, 2.2), (s * dx * 0.9, dy, H.z)) for dx, dy in ((0.03, -0.16), (0.055, -0.1), (0.075, -0.03), (0.08, 0.04), (0.065, 0.1))])
        el, wr = B(arm, side + "ForeArm"), B(arm, side + "Hand")
        mid = el.lerp(wr, 0.5); ax = (wr - el).normalized()
        lines.append([surf(bvh, mid + ax * t + Vector((s * 0.4, dy, 0.1)), mid + ax * t) for t, dy in ((-0.07, -0.08), (-0.02, -0.03), (0.03, 0.02), (0.07, 0.07))])
        hip, kn, an = B(arm, side + "UpLeg"), B(arm, side + "Leg"), B(arm, side + "Foot")
        for c, (z0, z1) in ((hip.lerp(kn, 0.55), (0.09, -0.09)), (kn.lerp(an, 0.5), (0.1, -0.1))):
            lines.append([surf(bvh, (c.x + s * dx, -1.0, c.z + dz), (c.x + s * dx, 1.0, c.z + dz)) for dx, dz in ((-0.055, z0), (-0.02, z0 * 0.4), (0.02, z1 * 0.4), (0.055, z1))])
    m, core = stripes(P, lines, 0.03)
    m = m * (1 - bel) * (1 - 0.0 * vest); core = core * (1 - bel)
    m = m * (1 - torso); core = core * (1 - torso)
    col = shade(col, AO, (1 - m) * (1 - 0.5 * bel))
    col, em = glow(col, em, m, core)
    finish_paint(T, col, em)

@variante("thron_zombie", "zombie")
def zirkelzischer(arm, body):
    remove_body(body)
    M = snake_mats(1024)
    M["cloth"] = look("Westensaum", (0.17, 0.065, 0.38), rough=0.6)
    g = join_parts(zischer_shape(arm), "Zirkelzischer")
    finish_skin(g, 0.009, 0.3)
    reduce(g, 0.16)
    g.data.materials.clear(); g.data.materials.append(M["skin"])
    smart_uv(g)
    paint_zischer(g, arm)
    bvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    bind_biped(g, arm, lambda c: "Head" if c.z > 1.3 else None)
    parts = rigid_parts(snake_face(M, bvh, ZH, ZK, tongue=False), "Head")
    parts += rigid_parts([give(gold_ring("Halsreif", (0, 0.01, 1.2), 0.125, 0.034, tilt=-8.0, squash=0.9), M["gold"])], "Spine2")
    parts += rigid_parts([vest_hem(M["cloth"])], "Hips")
    g = join_parts([g] + parts, "Zirkelzischer")
    print("ZIRKELZISCHER", len(g.data.polygons), "Flächen")

# ================================================================ Thronwächter (stark, Brecher)

TH = Vector((0.0, -0.3, 1.27))                 # Kopfmitte: tief zwischen den Schultern, nach vorn geschoben
TK = 1.05

def frame_of(axis):
    z = Vector(axis).normalized()
    x = z.cross(Vector((0, 1, 0)))
    x = x.normalized() if x.length > 1e-3 else Vector((1, 0, 0))
    return x, z.cross(x).normalized(), z

def faceted_dome(name, center, radii, axis, cut=-0.15):
    """Geschliffener Kristall als Kuppel (kantige Flächen), unten geschlossen"""
    x, y, z = frame_of(axis)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < cut - 1e-4], context='VERTS')
    edges = [e for e in bm.edges if e.is_boundary]
    if edges:
        bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    for v in bm.verts:
        c = v.co
        v.co = Vector(center) + x * (c.x * radii[0]) + y * (c.y * radii[1]) + z * (c.z * radii[2])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finish(name, bm, smooth=False)

def ngon_ring(name, center, axis, ra, rb, w, h, n=8, phase=0.0):
    """Kantiger Goldrahmen: Vieleck-Ring mit rechteckigem Querschnitt (Breite w nach außen, Höhe h entlang der Achse)"""
    x, y, z = frame_of(axis)
    bm = bmesh.new(); rings = []
    for i in range(n):
        a = phase + i * 2 * math.pi / n
        out = x * (math.cos(a)) + y * (math.sin(a))
        base = Vector(center) + x * (ra * math.cos(a)) + y * (rb * math.sin(a))
        rings.append([bm.verts.new(base + out * dw + z * dh) for dw, dh in ((-w * 0.3, -h / 2), (w * 0.7, -h / 2), (w * 0.7, h / 2), (-w * 0.3, h / 2))])
    for i in range(n):
        a, b = rings[i], rings[(i + 1) % n]
        for j in range(4):
            bm.faces.new([a[j], b[j], b[(j + 1) % 4], a[(j + 1) % 4]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finish(name, bm, smooth=False)

def fist(R, wrist, elbow, s, size):
    """Große Faust: Ballen, vier Knöchel, Daumen quer davor"""
    d = (Vector(wrist) - Vector(elbow)).normalized()
    fw = Vector((0, -1, 0)); inw = Vector((-s, 0, 0))
    c = Vector(wrist) + d * (0.75 * size)
    mb_ell(R, tuple(c), (1.0 * size, 1.05 * size, 1.0 * size))
    for k in range(4):
        o = (k - 1.5) * 0.46 * size
        mb_ball(R, tuple(c + d * (0.62 * size) + fw * (-o) + inw * (0.25 * size)), 0.4 * size)
    mb_caps(R, tuple(c + fw * (0.8 * size)), tuple(c + fw * (0.9 * size) + d * (0.6 * size) + inw * (0.3 * size)), 0.36 * size)

def guard_shape(arm):
    R = mb_family("Waechter")
    mb_ell(R, (0, 0.03, 0.95), (0.46, 0.35, 0.36))                                 # mächtiger Rumpf
    mb_ell(R, (0, 0.06, 1.15), (0.56, 0.31, 0.24))                                 # Schultergürtel
    mb_ell(R, (0, 0.08, 1.32), (0.27, 0.25, 0.2))                                  # Nacken hinter dem Kopf
    mb_ell(R, (0, 0.03, 0.66), (0.33, 0.27, 0.17))                                 # Becken
    snake_head(R, TH, TK)
    for s, side in ((1, "Left"), (-1, "Right")):
        sh, el, wr = B(arm, side + "Arm"), B(arm, side + "ForeArm"), B(arm, side + "Hand")
        mb_ball(R, (sh.x, sh.y, sh.z), 0.22)
        limb(R, [sh, el, wr], [0.165, 0.18])
        fist(R, wr, el, s, 0.215)
        hip, kn, an = B(arm, side + "UpLeg"), B(arm, side + "Leg"), B(arm, side + "Foot")
        limb(R, [(hip.x + 0.06 * s, hip.y, hip.z), (kn.x + 0.08 * s, kn.y, kn.z), (an.x + 0.08 * s, an.y, 0.16)], [0.21, 0.2])
        foot_shape(R, (an.x + 0.09 * s, an.y + 0.02), 0.27)
    return mb_to_mesh(R)

def guard_armor(arm, M):
    """Schulterplatten und Armschienen aus geschliffenem Kristall mit kantigem Goldrand; je Seite Liste (Teile, Knochen)"""
    out = []
    for s, side in ((1, "Left"), (-1, "Right")):
        sh, el, wr = B(arm, side + "Arm"), B(arm, side + "ForeArm"), B(arm, side + "Hand")
        axis = Vector((s * 0.55, 0.0, 0.84))
        c = sh + Vector((s * 0.03, 0.0, 0.03))
        dome = give(faceted_dome("Schulterkristall%d" % s, c, (0.34, 0.31, 0.28), axis, cut=-0.1), M["crystal"])
        x, y, z = frame_of(axis)
        rim = give(ngon_ring("Schulterrand%d" % s, c - z * 0.028, axis, 0.34, 0.31, 0.055, 0.07, n=8, phase=math.pi / 8), M["gold"])
        out.append(([dome, rim], side + "Arm", side + "Shoulder"))
        ax = (wr - el).normalized(); mid = el.lerp(wr, 0.55)
        fx, fy, fz = frame_of(ax)
        bm = bmesh.new(); rings = []
        for t, r in ((-0.12, 0.215), (-0.04, 0.25), (0.04, 0.25), (0.12, 0.22)):
            rings.append([bm.verts.new(mid + fz * t + (fx * math.cos(q) + fy * math.sin(q)) * r) for q in [k * 2 * math.pi / 8 + math.pi / 8 for k in range(8)]])
        for r0, r1 in zip(rings, rings[1:]):
            for k in range(8):
                bm.faces.new([r0[k], r0[(k + 1) % 8], r1[(k + 1) % 8], r1[k]])
        bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        brace = give(finish("Armschiene%d" % s, bm, smooth=False), M["crystal"])
        r1 = give(ngon_ring("Schienenrand_a%d" % s, mid - fz * 0.125, ax, 0.22, 0.22, 0.05, 0.05, n=8, phase=math.pi / 8), M["gold"])
        r2 = give(ngon_ring("Schienenrand_b%d" % s, mid + fz * 0.125, ax, 0.225, 0.225, 0.05, 0.05, n=8, phase=math.pi / 8), M["gold"])
        out.append(([brace, r1, r2], side + "ForeArm", side + "ForeArm"))
    return out

def paint_guard(g, arm):
    bvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    ao = vertex_ao(g, rays=18, dist=0.35)
    T = texels(g); P, N, cov = T["P"], T["N"], T["cov"]
    AO = texel_values(T, ao)
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    k = TK; H = TH
    jaw, mouth, hd = face_masks(P, H, k, PMOUTH)
    head = hd < 1.0
    col = violet(N)
    em = np.zeros(P.shape, np.float32)
    # Bauchschild: oben breit und rund, unten spitz zulaufend, mit Querlinien
    tz = np.clip((z - 0.62) / 0.5, 0, 1)
    wz = 0.31 * tz ** 0.55 * smoothstep(1.2, 1.06, z)
    plate = smoothstep(0.014, -0.014, np.abs(x) - wz) * (z > 0.62) * (z < 1.2) * smoothstep(-0.05, -0.32, N[..., 1]) * (~head) * (np.abs(x) < 0.34)
    bel = np.clip(np.maximum(plate, jaw * head), 0, 1)
    bcol = belly_col(N)
    lines = np.zeros(P.shape[:-1], np.float32)
    for zl in (0.76, 0.87, 0.98, 1.08):
        lines = np.maximum(lines, np.clip(1.5 * (1 - np.abs(z + 0.45 * x * x - zl) / 0.011), 0, 1))
    bcol = mix(bcol, (0.42, 0.3, 0.72), 0.75 * lines * plate)
    col = col * (1 - bel[..., None]) + bcol * bel[..., None]
    col = mix(col, (0.1, 0.03, 0.18), mouth * head)
    # Leuchtstreifen: Bögen an den Flanken neben dem Schild, schräg über die Oberschenkel, zwei Bögen auf dem Rücken
    lines3 = []
    for s, side in ((1, "Left"), (-1, "Right")):
        lines3.append([surf(bvh, (s * dx, -1.5, dz), (s * dx, 1.0, dz)) for dx, dz in ((0.4, 0.95), (0.39, 0.85), (0.35, 0.75), (0.29, 0.67))])
        hip, kn = B(arm, side + "UpLeg"), B(arm, side + "Leg")
        c = hip.lerp(kn, 0.6)
        lines3.append([surf(bvh, (c.x + s * dx, -1.5, c.z + dz), (c.x + s * dx, 1.0, c.z + dz)) for dx, dz in ((-0.12, 0.13), (-0.05, 0.07), (0.03, 0.0), (0.1, -0.09))])
        lines3.append([surf(bvh, (s * dx, 1.5, dz), (s * dx, -1.0, dz)) for dx, dz in ((0.2, 1.0), (0.24, 0.88), (0.23, 0.76), (0.17, 0.66))])
    m, core = stripes(P, lines3, 0.042)
    m = m * (1 - bel) * (~head); core = core * (1 - bel) * (~head)
    col = shade(col, AO, (1 - m) * (1 - 0.5 * bel))
    col, em = glow(col, em, m, core)
    finish_paint(T, col, em)

@variante("thron_brecher", "brecher")
def thronwaechter(arm, body):
    remove_body(body)
    M = snake_mats(1024)
    M["crystal"] = look("Kristall", (0.33, 0.14, 0.7), rough=0.3, emit=(0.3, 0.1, 0.62), strength=0.35)
    g = guard_shape(arm)
    finish_skin(g, 0.014, 0.3)
    reduce(g, 0.16)
    g.data.materials.clear(); g.data.materials.append(M["skin"])
    smart_uv(g)
    paint_guard(g, arm)
    bvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    def rigid(c):
        q = Vector(((c.x - TH.x) / (0.3 * TK), (c.y - TH.y) / (0.38 * TK), (c.z - TH.z) / (0.28 * TK)))
        return "Head" if q.length < 1.0 and c.y < TH.y + 0.14 else None
    bind_biped(g, arm, rigid)
    parts = rigid_parts(snake_face(M, bvh, TH, TK, mouth=PMOUTH, fang_x=0.11, fang_len=0.065, tongue=False), "Head")
    for objs, b1, b2 in guard_armor(arm, M):
        for o in objs:
            if b1 == b2:
                group_all(o, "mixamorig:" + b1)
            else:
                group_all(o, "mixamorig:" + b1, 0.5); group_all(o, "mixamorig:" + b2, 0.5)
        parts += objs
    g = join_parts([g] + parts, "Thronwaechter")
    print("THRONWAECHTER", len(g.data.polygons), "Flächen")

if __name__ == "__main__":
    run(VAR, OUT)
