# Monster der Welt „Thron der Zauberin“ (Planet Schlangenhöhle, Boss Schlangenzauberin),
# Vorlage_Raw/Thron_der_Zauberin_Monster_v1 (vier Bilder vom Nutzer, 27.11.2026). Alle drei haben zwei Arme und zwei Beine.
#   thron_krabbler   Haubenwicht: kleiner Wicht mit einfachem Schlangenkopf (ohne Haube, Wunsch 27.11.), Skelett Krabbler
#   thron_zombie     Zirkelzischer: schlanker Schlangenpriester mit langem Hals, Weste und Goldreif, Skelett Zombie
#   thron_brecher    Thronwächter: breiter Beschützer mit Kristall-Schulterplatten und Goldrand, Skelett Brecher
# Farben und Gesicht wie bei den Schlangennest-Monstern (tools/monster/schlangennest.py): dunkelviolett mit klarem
# Hell-Dunkel-Verlauf, heller Bauch, magentafarbene Leuchtstreifen als weiche Sicheln, flieder leuchtende Augen ohne Pupille (wie in der Vorlage).
# Aufruf: blender -b -P tools/monster/zauberthron.py -- <variante> <ziel.glb>
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schlangennest import *

def violet(N):
    """Haut mit klarem Verlauf: oben hell, zur Seite sattes Purpur, unten dunkel"""
    tz = np.clip(N[..., 2] * 0.5 + 0.5, 0, 1)
    return np.where((tz < 0.5)[..., None], gradient(SKIN_D, SKIN_M, tz * 2), gradient(SKIN_M, SKIN_L, smoothstep(0.5, 1.0, tz)))

def belly_col(N):
    return gradient(BELLY_D, BELLY_L, smoothstep(0.1, 0.9, np.clip(0.55 + N[..., 2] * 0.35 - N[..., 1] * 0.35, 0, 1)))

def shade(col, AO, keep):
    """gemalte Schatten in Falten und unter Überhängen"""
    occ = np.clip(AO * 2.2, 0, 1) ** 0.85
    return mix(col, SHADOW, 0.58 * occ * keep)

def surf(bvh, outer, target, lift=0.0):
    """Punkt auf der Haut: von outer in Richtung target"""
    o = Vector(outer); d = (Vector(target) - o).normalized()
    hit, n, _, _ = bvh.ray_cast(o, d, 6.0)
    return tuple(hit + n * lift) if hit is not None else tuple(target)

def bind_biped(body, arm, rigid, core=None):
    """Bone Heat nur mit den Hauptknochen; rigid(Punkt) -> Knochen für starre Bereiche (Kopf mit Haube und Gesicht);
    core(Punkt) -> 0…1 für die Rumpfmitte: dort ziehen Arm- und Schulterknochen entsprechend weniger (1 = gar nicht),
    mit weichem Übergang, damit Bauchschild und Flanken in der Bewegung glatt bleiben"""
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
    if core:
        armg = [g for g in body.vertex_groups if any(k in g.name for k in ("Arm", "Shoulder", "Hand"))]
        names = {g.index: g for g in body.vertex_groups}
        for v in body.data.vertices:
            f = float(core(v.co))
            if f <= 0.0:
                continue
            ws = [(names[e.group], e.weight * ((1 - f) if names[e.group] in armg else 1.0)) for e in v.groups]
            tot = sum(w for _, w in ws)
            if tot < 1e-4:
                continue
            for g, w in ws:
                if w / tot < 1e-4:
                    g.remove([v.index])
                else:
                    g.add([v.index], w / tot, 'REPLACE')

def uv_ball(name, center, radii, segs=(20, 14)):
    return sphere(name, tuple(center), 1.0, tuple(radii), segs=segs)

def rigid_parts(parts, bone):
    for o in parts:
        group_all(o, "mixamorig:" + bone)
    return parts

def limb(R, pts, radii):
    for (a, b), r in zip(zip(pts, pts[1:]), radii):
        mb_caps(R, tuple(a), tuple(b), r)

def snake_head(R, H, k):
    mb_ell(R, H, (0.25 * k, 0.24 * k, 0.2 * k))
    mb_ell(R, H + Vector((0, -0.15, -0.045)) * k, (0.165 * k, 0.115 * k, 0.08 * k))
    mb_ell(R, H + Vector((0, -0.1, -0.13)) * k, (0.17 * k, 0.15 * k, 0.07 * k))
    for s in (1, -1):
        mb_ell(R, H + Vector((0.15 * s, -0.04, -0.05)) * k, (0.09 * k, 0.12 * k, 0.09 * k))

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

# ---------------------------------------------------------------- Runde 3 (Kritik 27.11.): Farben, Hände, Pfoten, Glühen, Augen

SKIN_D, SKIN_M, SKIN_L = (0.2, 0.07, 0.38), (0.4, 0.18, 0.66), (0.58, 0.36, 0.86)     # Purpur wie in der Vorlage
SHADOW = (0.13, 0.04, 0.27)
BELLY_D, BELLY_L, BELLY_LINE = (0.62, 0.5, 0.84), (0.85, 0.76, 0.97), (0.5, 0.36, 0.76)
GLOW, GLOW_CORE, GLOW_HALO = (0.95, 0.32, 0.95), (1.0, 0.76, 1.0), (0.66, 0.2, 0.8)

def throne_mats(size=1024):
    M = snake_mats(size)
    M["eyetex"] = eye_material()
    M["mouth"] = look("Maul", (0.16, 0.05, 0.26), rough=0.6)
    M["gold"] = look("Gold", (0.95, 0.66, 0.2), rough=0.32, metal=0.85)
    return M

def bone_frame(arm, bone):
    """Lage und Richtung eines Knochens in der Ruhehaltung (ohne Maßstab)"""
    loc, rot, _ = (arm.matrix_world @ arm.data.bones["mixamorig:" + bone].matrix_local).decompose()
    return Matrix.Translation(loc) @ rot.to_matrix().to_4x4()

def round_tube(name, pts, radii, n=10, segs=12):
    """Weich gebogener Finger mit runder Kuppe"""
    Q, _ = smooth3([tuple(p) for p in pts], n, passes=1)
    R = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(radii)), radii)
    Q = [Vector(q) for q in Q]; R = [float(r) for r in R]
    Q = [Q[0] - (Q[1] - Q[0]).normalized() * (0.3 * R[0])] + Q + [Q[-1] + (Q[-1] - Q[-2]).normalized() * (0.3 * R[-1])]   # beide Enden geschlossen
    return [tube(name, [tuple(q) for q in Q], [0.0] + R + [0.0], segs=segs), sphere(name + "Kuppe", tuple(Q[-2]), R[-1], segs=(12, 8))]

def comic_hand(name, arm, side, k=1.0, n=3, curl=0.3, slim=1.0, reach=1.0, roll=0.0):
    """Schlichte, glatte Comic-Hand (wie die Hände der Monster im Spiel und der Vorlage): Handfläche, n dicke Finger
    und ein Daumen, weich zu einer Haut verschmolzen, ohne Knöchel oder Knubbel. Im Rahmen des Handknochens gebaut
    (Finger entlang +Y, Daumen auf der +X-Seite, Handfläche nach -Z), daher gerade am Arm. curl 0 = offen … 1 = Faust."""
    fist = curl > 0.6
    if fist:                                                        # Faust wie in der Vorlage: ein runder, glatter Körper, das Handgelenk läuft ohne Absatz hinein
        parts = [sphere(name + "Faust", (0.0, 0.1, -0.012), 0.1, (1.06, 1.2, 0.9), segs=(28, 18))]
        parts += round_tube(name + "Gelenk", [(0, -0.04, 0), (0, 0.0, 0), (0, 0.05, -0.004), (0, 0.09, -0.008)], [0.078, 0.082, 0.092, 0.098])
    else:
        parts = [sphere(name + "Ballen", (0.0, 0.09, 0.0), 0.1, (1.0, 1.0, 0.56), segs=(24, 14)),
                 sphere(name + "Gelenk", (0.0, 0.025, 0.0), 0.076, (1.0, 1.0, 0.78), segs=(20, 12))]
    xs, r, splay = (((-0.062, 0.0, 0.062), 0.036, (-12, 0, 12)) if n == 3 else ((-0.078, -0.026, 0.026, 0.078), 0.03 + 0.008 * curl, (-13, -4, 4, 13)))
    L = 0.115 * reach
    for i, (x, sp) in enumerate(zip(xs, splay)):
        sx = math.sin(math.radians(sp)) * (1 - 0.7 * curl)
        a1, a2 = math.radians(18 + 55 * curl), math.radians(38 + 110 * curl)
        p0 = Vector((x, 0.13, 0.0))
        p1 = p0 + Vector((sx, math.cos(a1), -math.sin(a1))) * (0.55 * L)
        p2 = p1 + Vector((sx, math.cos(a2), -math.sin(a2))) * (0.5 * L)
        parts += round_tube("%sFinger%d" % (name, i), [p0 - Vector((0, 0.03, 0)), p0, p1, p2], [r, r, r * 0.97, r * 0.9])
    if fist:                                                        # kurzer, dicker Daumen liegt vorn an
        t0 = Vector((0.07, 0.07, -0.03)); t1 = Vector((0.104, 0.12, -0.062)); t2 = Vector((0.07, 0.17, -0.092))
        parts += round_tube(name + "Daumen", [t0 - (t1 - t0) * 0.5, t0, t1, t2], [0.042, 0.044, 0.042, 0.038])
    else:
        t0 = Vector((0.07, 0.05, -0.005)); t1 = Vector((0.124, 0.09, -0.02 - 0.03 * curl)); t2 = Vector((0.148 - 0.07 * curl, 0.14, -0.045 - 0.06 * curl))
        parts += round_tube(name + "Daumen", [t0 - (t1 - t0) * 0.5, t0, t1, t2], [0.038, 0.038, 0.036, 0.032])
    o = join_parts(parts, name)
    o.data.transform(Matrix.Rotation(roll, 4, 'Y') @ Matrix.Diagonal((k * slim, k, k, 1.0)))
    if side == "Right":                                             # Spiegelbild (bei diesen Skeletten zeigt X rechts andersherum)
        o.data.transform(Matrix.Diagonal((-1.0, 1.0, 1.0, 1.0))); o.data.flip_normals()
    remesh(o, 0.0055 * k * min(1.0, slim + 0.2))
    md = o.modifiers.new("Glatt", 'SMOOTH'); md.factor = 0.5; md.iterations = 8 if fist else 3; apply_mod(o, md)
    md = o.modifiers.new("Weniger", 'DECIMATE'); md.ratio = 0.15; apply_mod(o, md)
    for pl in o.data.polygons:
        pl.use_smooth = True
    if arm is not None:
        o.data.transform(bone_frame(arm, side + "Hand"))
        group_all(o, "mixamorig:%sHand" % side)
    return o

def paw(name, cx, cy, size, toes=3):
    """Fuß als runde Pfote: gewölbter Ballen, vorn einzeln modellierte runde Zehen mit echten Furchen dazwischen
    (eigene Körper, damit sie beim Verschmelzen nicht zulaufen). cy = Ferse/Knöchel, die Zehen zeigen nach -Y."""
    parts = [uv_ball(name, (cx, cy - 0.28 * size, 0.36 * size), (0.72 * size, 0.88 * size, 0.5 * size), segs=(28, 18))]
    for k in range(toes):
        u = k - (toes - 1) / 2
        parts.append(uv_ball("%sZehe%d" % (name, k), (cx + u * 0.47 * size, cy - (1.1 - 0.12 * abs(u)) * size, 0.26 * size),
                             (0.255 * size, 0.36 * size, 0.27 * size), segs=(20, 14)))
    return parts

def paw_paint(P, N, col, feet):
    """Pfoten: weiche Schatten in den Furchen, Licht auf jeder Zehe, dunkle Sohlenkante (keine harten Striche);
    feet = [(x, y, Größe, Zehenzahl)] wie bei paw"""
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    for fx, fy, size, toes in feet:
        near = (np.abs(x - fx) < 0.9 * size) & (z < 0.8 * size) & (y < fy + 0.75 * size)
        front = smoothstep(fy - 0.5 * size, fy - 0.85 * size, y) * near
        for k in range(toes - 1):
            gx = fx + (k - (toes - 2) / 2) * 0.47 * size
            g = np.exp(-((x - gx) / (0.05 * size)) ** 2) * front * smoothstep(0.6 * size, 0.3 * size, z)
            col = mix(col, SHADOW, 0.5 * g)
        for k in range(toes):
            u = k - (toes - 1) / 2
            c = f3((fx + u * 0.47 * size, fy - (1.1 - 0.12 * abs(u)) * size, 0.34 * size))
            d = np.linalg.norm((P - c) / (0.26 * size), axis=-1)
            col = mix(col, SKIN_L, 0.42 * np.clip(1 - d, 0, 1) * (N[..., 2] > 0.15) * near)
        col = mix(col, SHADOW, 0.5 * smoothstep(0.09 * size, 0.01 * size, z) * near)
    return col

def glow_stripes(P, lines, width, bvh=None):
    """Leuchtstreifen als weiche Sicheln: in der Mitte breit, an beiden Enden spitz, mit hellem Kern und einem
    Lichthof, der in die Haut ausläuft. lines = Punktlisten auf der Haut; liefert (Band, Kern, Lichthof)."""
    shape = P.shape[:-1]; F = P.reshape(-1, 3)
    band = np.zeros(len(F), np.float32); core = np.zeros(len(F), np.float32); halo = np.zeros(len(F), np.float32)
    width0 = width
    for pts in lines:
        width = width0
        if len(pts) == 2 and isinstance(pts[1], float):             # (Punkte, eigene Breite)
            pts, width = pts
        Q, _ = smooth3([tuple(p) for p in pts], 26, passes=2)
        if bvh is not None:
            Q = np.asarray([tuple(bvh.find_nearest(Vector(q))[0]) for q in Q])
        n = len(Q)
        W = np.maximum(width * np.sin(np.pi * np.linspace(0.02, 0.98, n)) ** 0.8, 1e-4)
        lo = Q.min(0) - 4 * width; hi = Q.max(0) + 4 * width
        idx = np.nonzero(np.all((F > lo) & (F < hi), axis=1))[0]
        if not len(idx):
            continue
        S = F[idx]
        b_ = np.zeros(len(S), np.float32); c_ = np.zeros(len(S), np.float32); h_ = np.zeros(len(S), np.float32)
        for i in range(n - 1):
            a = Q[i].astype(np.float32); ab = (Q[i + 1] - Q[i]).astype(np.float32)
            t = np.clip(((S - a) @ ab) / max(float(ab @ ab), 1e-9), 0, 1)
            d = np.linalg.norm(S - (a + t[:, None] * ab), axis=-1)
            w = W[i] + t * (W[i + 1] - W[i])
            u = d / w
            b_ = np.maximum(b_, smoothstep(1.0, 0.5, u))
            c_ = np.maximum(c_, smoothstep(0.62, 0.0, u) * np.clip(w / (0.6 * width), 0, 1))
            h_ = np.maximum(h_, np.exp(-(np.maximum(d - 0.45 * w, 0) / (0.5 * width + 0.006)) ** 2) * np.clip(w / (0.45 * width), 0, 1))
        band[idx] = np.maximum(band[idx], b_); core[idx] = np.maximum(core[idx], c_); halo[idx] = np.maximum(halo[idx], h_)
    return band.reshape(shape), core.reshape(shape), halo.reshape(shape)

def paint_glow(col, em, fields, keep=None):
    """Glühen in die Haut einarbeiten: Lichthof färbt die Umgebung, das Band leuchtet, der Kern ist am hellsten"""
    band, core, halo = fields
    if keep is not None:
        band = band * keep; core = core * keep; halo = halo * keep
    col = mix(col, GLOW_HALO, 0.5 * halo)
    col = mix(col, GLOW, band)
    col = mix(col, GLOW_CORE, 0.6 * core)
    em += f3((0.5, 0.1, 0.58)) * (0.55 * halo)[..., None] + f3((0.92, 0.2, 0.88)) * band[..., None] + f3((0.55, 0.5, 0.55)) * (0.6 * core)[..., None]
    return col, em

def part_tags(g):
    v = np.zeros(len(g.data.vertices), np.float32)
    g.data.attributes["teil"].data.foreach_get("value", v)
    return v

EYE_SHAPE = [(-1.0, -0.2), (-0.5, 0.2), (0.0, 0.55), (0.45, 0.82), (0.85, 0.85), (1.08, 0.62), (0.98, 0.1), (0.62, -0.55), (0.1, -0.9),
             (-0.45, -0.88), (-0.88, -0.58)]   # leicht langgezogenes Auge: innen tief, oben schräg, außen eine kleine Spitze
EYE_C = (0.06, -0.08)                           # Mitte der Wölbung (in Augenmaßen)

def eye_material(n=160):
    """Auge als ein Bild mit weichen Verläufen (keine aufeinandergelegten Farbflächen): flieder leuchtende Iris, zur
    Mitte heller, weiche Schlitzpupille, oben der Schatten der Braue, dunkler Rand, kleines Glanzlicht.
    Bildmitte = Augenmitte, Bildrand = Umriss des Auges; x nach außen, y nach oben."""
    ax = np.linspace(-1, 1, n, dtype=np.float32); x, y = np.meshgrid(ax, ax)
    t = np.hypot(x, y)
    col = np.zeros((n, n, 3), np.float32) + f3((0.58, 0.38, 0.95))
    col = mix(col, (0.9, 0.82, 1.0), 0.8 * np.exp(-((x + 0.05) ** 2 + (y + 0.22) ** 2) / 0.3))
    col = mix(col, (0.36, 0.17, 0.72), 0.6 * smoothstep(0.05, 0.95, 0.8 * y - 0.45 * x + 0.1))
    col = mix(col, (0.32, 0.12, 0.62), 0.62 * np.exp(-(x / 0.2) ** 2 - (y / 0.68) ** 2))
    rim = smoothstep(0.8, 1.0, t)
    col = mix(col, (0.19, 0.07, 0.36), 0.8 * rim)
    col = mix(col, (1.0, 0.97, 1.0), 0.7 * np.exp(-((x - 0.34) ** 2 + (y - 0.36) ** 2) / 0.022))
    arr = np.ones((n, n, 4), np.float32); arr[..., :3] = np.clip(col, 0, 1)
    em = arr.copy(); em[..., :3] *= (0.55 * (1 - rim))[..., None]
    m = bpy.data.materials.new("Leuchtauge"); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value = 0.3
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = new_image("Auge_Farbe", arr)
    nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
    te = nt.nodes.new("ShaderNodeTexImage"); te.image = new_image("Auge_Leuchten", em)
    nt.links.new(te.outputs["Color"], p.inputs["Emission Color"])
    p.inputs["Emission Strength"].default_value = 1.0
    return m

def caster(bvh, H, k):
    """Punkt auf dem Gesicht von vorn (x, z in k um die Kopfmitte H), mit Abstand lift über der Haut"""
    def on(x, z, lift=0.0):
        o = Vector((H.x + x * k, H.y - 2.0, H.z + z * k))
        hit, n, _, _ = bvh.ray_cast(o, Vector((0, 1, 0)), 6.0)
        if hit is None or hit.y > H.y + 0.05 * k:
            hit, n, _, _ = bvh.ray_cast(o, (H + Vector((0, 0.05 * k, z * k * 0.8)) - o).normalized(), 6.0)
        return hit + (hit - back).normalized() * (lift * k)
    back = H + Vector((0, 0.3 * k, 0))
    return on

def glow_eyes(M, bvh, H, k, eye, size, outline=EYE_SHAPE):
    """Leuchtaugen: eine flach gewölbte Fläche je Auge mit dem Verlaufsbild aus eye_material (Iris, Pupille, Rand
    und Glanz gehen weich ineinander über)."""
    on = caster(bvh, H, k)
    a, b = size
    O = closed_curve(outline, 44); n = len(O)
    cu, cw = EYE_C
    dome = lambda t: 0.006 + 0.014 * (1 - t * t) ** 0.7
    parts = []
    for s in (1, -1):
        def at(du, dw, lift):
            return on((eye[0] + du * a) * s, eye[1] + dw * b, lift)
        bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap"); uv = {}
        c = bm.verts.new(at(cu, cw, dome(0.0))); uv[c] = (0.5, 0.5)
        rings = []
        for t in (0.25, 0.5, 0.72, 0.88, 1.0):
            ring = []
            for u, w in O:
                v = bm.verts.new(at(cu + t * (u - cu), cw + t * (w - cw), dome(t)))
                ang = math.atan2(w - cw, u - cu)
                uv[v] = (0.5 + 0.49 * t * math.cos(ang), 0.5 + 0.49 * t * math.sin(ang))
                ring.append(v)
            rings.append(ring)
        for i in range(n):
            bm.faces.new([c, rings[0][i], rings[0][(i + 1) % n]] if s > 0 else [c, rings[0][(i + 1) % n], rings[0][i]])
        for r0, r1 in zip(rings, rings[1:]):
            for i in range(n):
                q = [r0[i], r1[i], r1[(i + 1) % n], r0[(i + 1) % n]]
                bm.faces.new(q if s > 0 else q[::-1])
        for f in bm.faces:
            for l in f.loops:
                l[uvl].uv = uv[l.vert]
        parts.append(give(finish("Auge%d" % s, bm), M["eyetex"]))
    return parts

def eye_brows(bvh, H, k, eye, size, brow):
    """Brauenwülste entlang der schrägen Oberkante der Augen. Sie werden mit der Haut verbunden und mit ihr bemalt
    (Verlauf und Schatten wie die Haut, keine eigene Farbfläche). Liefert (Teile, Linien für die Bemalung)."""
    on = caster(bvh, H, k); a, b = size; parts = []; lines = []
    top = [(-1.14, -0.44), (-0.55, 0.04), (0.0, 0.42), (0.5, 0.74), (1.06, 0.86)]
    for s in (1, -1):
        pts = [tuple(on((eye[0] + (u - 0.04) * a) * s, eye[1] + (w + 0.22) * b, 0.004 + brow * 0.35)) for u, w in top]
        parts.append(tube("Braue%d" % s, pts, [brow * k * v for v in (0.0, 0.9, 1.0, 0.85, 0.0)], segs=12))
        lines.append(pts)
    return parts, lines

def brow_shade(P, col, lines, r):
    """Brauen und die Haut direkt darunter etwas dunkler (weicher Schatten über dem Auge)"""
    m = np.zeros(P.shape[:-1], np.float32)
    for pts in lines:
        m = np.maximum(m, smoothstep(2.2 * r, 0.6 * r, seg_dist(P, pts)))
    return mix(col, SKIN_D, 0.5 * m)

def tooth(name, base, r, length, lean=0.0):
    """Reißzahn als ein glatter Körper: runder Ansatz oben, nach unten spitz zulaufend, leicht zur Mitte gebogen"""
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=10, radius=1.0)
    for v in bm.verts:
        x, y, z = v.co
        if z >= 0:
            v.co = Vector((x * r, y * r * 0.85, z * r * 0.7))
        else:
            t = -z; h = max(math.sqrt(max(1 - t * t, 0.0)), 1e-6); w = (1 - t) ** 0.85 * (1 + 0.25 * t)
            v.co = Vector((x / h * w * r + lean * t * t, y / h * w * r * 0.85, -t * length))
        v.co += Vector(base)
    return finish(name, bm)

def fangs(M, bvh, H, k, mouth, x, length, r=0.02):
    """Zwei saubere Reißzähne an der Oberlippe"""
    on = caster(bvh, H, k); parts = []
    zu = float(lip_curves(np.asarray([x]), mouth)[0][0])
    for s in (1, -1):
        base = on(x * s, zu + 0.003, 0.012)
        parts.append(give(tooth("Zahn%d" % s, base, r * k, length * k, lean=-0.006 * s * k), M["fang"]))
    return parts

# ================================================================ Haubenwicht (leicht, Krabbler)

WH = Vector((0.0, -0.06, 1.28))                 # Kopfmitte
WK = 1.42                                       # Kopfgröße: groß gegenüber dem kleinen Körper
WMOUTH = (-0.1, -0.142, 0.118)
W_EYE, W_EYE_SIZE = (0.105, 0.03), (0.072, 0.07)
W_FOOT = (0.31, 0.03, 0.27)                     # Pfote: x, y (Knöchel), Größe
HAND_ROLL = {"krabbler": -115, "zombie": -110, "brecher": -97}   # Grad um die Armachse: Handfläche zeigt in Schlagrichtung
# (gemessen an der Angriffsbewegung der Skelette; in der Laufhaltung zeigt sie damit zum Körper, der Daumen nach vorn)

def wicht_shape(arm):
    """Einfach gehalten (Wunsch 27.11.): ein ganz normaler Schlangenkopf auf kurzem Hals, keine Haube dahinter"""
    R = mb_family("Wicht")
    mb_caps(R, (0, 0.01, 0.8), (0, -0.02, 1.14), 0.125)                             # kurzer, kräftiger Schlangenhals
    mb_ell(R, (0, 0.0, 0.79), (0.2, 0.15, 0.12))                                    # schmale Schultern
    mb_ell(R, (0, -0.01, 0.65), (0.2, 0.17, 0.17))                                  # Bauch
    mb_ell(R, (0, 0.01, 0.5), (0.2, 0.15, 0.13))                                    # schmale Hüfte: die Arme schwingen frei daneben
    snake_head(R, WH, WK)
    for s, side in ((1, "Left"), (-1, "Right")):
        el, wr = B(arm, side + "ForeArm"), B(arm, side + "Hand")
        limb(R, [(0.16 * s, 0.0, 0.83), el, wr + (wr - el).normalized() * 0.02], [0.062, 0.07])
        hip, kn, an = Vector((0.12 * s, 0.02, 0.44)), Vector((0.2 * s, 0.01, 0.3)), Vector((0.29 * s, 0.01, 0.17))
        limb(R, [hip, kn, an], [0.095, 0.155])                                        # Beine stehen weit und werden nach unten breiter
    parts = [mb_to_mesh(R)]
    for s in (1, -1):
        parts += paw("Pfote%d" % s, W_FOOT[0] * s, W_FOOT[1], W_FOOT[2])
    return parts

def paint_wicht(g, arm, brow_lines):
    bvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    ao = vertex_ao(g, rays=18, dist=0.3)
    T = texels(g); P, N, cov = T["P"], T["N"], T["cov"]
    AO = texel_values(T, ao)
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    k = WK; H = WH
    jaw, mouth, hd = face_masks(P, H, k, WMOUTH)
    head = z > 0.985
    face = head & (hd < 1.0)
    col = violet(N)
    em = np.zeros(P.shape, np.float32)
    # heller Bauch: Schild am Rumpf, Vorderseite des Halses bis zum Unterkiefer
    sh = (np.abs(x) / 0.165) ** 2.6 + (np.abs(z - 0.7) / 0.235) ** 2.6
    plate = smoothstep(1.06, 0.94, sh) * smoothstep(-0.05, -0.32, N[..., 1]) * (~head)
    throat = smoothstep(0.014, -0.014, np.abs(x) - 0.09) * smoothstep(-0.15, -0.5, N[..., 1]) * (z > 0.93) * (z < H.z - 0.17 * k)
    bel = np.clip(np.maximum(np.maximum(plate, throat), jaw * face), 0, 1)
    bcol = belly_col(N)
    lines = np.zeros(P.shape[:-1], np.float32)
    for zl in (0.585, 0.695, 0.805, 0.985, 1.04):
        lines = np.maximum(lines, np.clip(1.4 * (1 - np.abs(z - 0.9 * x * x - zl) / 0.009), 0, 1))
    bcol = mix(bcol, BELLY_LINE, 0.7 * lines * np.maximum(plate, throat * (1 - jaw)))
    bcol = mix(bcol, BELLY_LINE, 0.5 * smoothstep(0.8, 1.02, sh) * plate)        # Rand des Schilds etwas dunkler
    col = col * (1 - bel[..., None]) + bcol * bel[..., None]
    col = mix(col, (0.16, 0.05, 0.26), mouth * face)
    col = brow_shade(P, col, brow_lines, 0.02 * k)
    col = paw_paint(P, N, col, [(W_FOOT[0] * s, W_FOOT[1], W_FOOT[2], 3) for s in (1, -1)])
    # Leuchtstreifen: zwei kurze Sicheln auf der Stirn, zwei längere über den Hinterkopf, eine schräg über jeden Oberschenkel
    lt, lh = [], []
    for s in (1, -1):
        lt.append([surf(bvh, (s * dx, -1.5, dz), (s * dx, 1.0, dz)) for dx, dz in ((0.17, 0.56), (0.235, 0.5), (0.29, 0.42), (0.3, 0.33))])
        lh.append([surf(bvh, (s * dx * k, -2.0, H.z + dz * k), (s * dx * k, 1.0, H.z + dz * k)) for dx, dz in ((0.035, 0.128), (0.08, 0.148), (0.13, 0.158), (0.175, 0.148))])
        lh.append([surf(bvh, (s * dx * k, 2.0, H.z + dz * k), (s * dx * k, -1.0, H.z + dz * k)) for dx, dz in ((0.05, 0.16), (0.11, 0.1), (0.14, 0.02), (0.12, -0.07))])
    fields = [np.zeros(P.shape[:-1], np.float32) for _ in range(3)]
    for lines3, keep, width in ((lt, (1 - bel) * (z < 0.75), 0.046), (lh, head * (1 - bel), 0.026)):
        for i, f in enumerate(glow_stripes(P, lines3, width, bvh)):
            fields[i] = np.maximum(fields[i], f * keep)
    col = shade(col, AO, (1 - fields[0]) * (1 - 0.5 * bel))
    col, em = paint_glow(col, em, fields)
    finish_paint(T, col, em)

@variante("thron_krabbler", "krabbler")
def haubenwicht(arm, body):
    remove_body(body)
    M = throne_mats(1024)
    hands = [comic_hand("Hand" + side, arm, side, k=1.05, n=3, curl=0.35, roll=math.radians(HAND_ROLL["krabbler"])) for side in ("Left", "Right")]
    g = join_parts(wicht_shape(arm), "Haubenwicht")
    finish_skin(g, 0.011, 0.3, smooth_it=6)
    reduce(g, 0.2)
    tag(g, 0)
    bind_biped(g, arm, lambda c: "Head" if c.z > 0.985 else None, core=lambda c: smooth01((0.25 - abs(c.x)) / 0.08) * smooth01((0.86 - c.z) / 0.08) * smooth01((c.z - 0.34) / 0.08))
    fbvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    brows, brow_lines = eye_brows(fbvh, WH, WK, W_EYE, W_EYE_SIZE, 0.02)
    rigid_parts(brows, "Head")
    g = join_parts([g] + hands + brows, "Haubenwicht")
    for p in g.data.polygons:
        p.use_smooth = True
    g.data.materials.clear(); g.data.materials.append(M["skin"])
    smart_uv(g)
    paint_wicht(g, arm, brow_lines)
    parts = snake_face(M, fbvh, WH, WK, mouth=WMOUTH, tongue=False, teeth=True, brows=False, eyes=False, fangs=False)
    parts += fangs(M, fbvh, WH, WK, WMOUTH, 0.088, 0.04, r=0.017)
    parts += glow_eyes(M, fbvh, WH, WK, W_EYE, W_EYE_SIZE)
    rigid_parts(parts, "Head")
    parts += rigid_parts([give(gold_ring("Halsreif", (0, -0.01, 0.945), 0.185, 0.04, tilt=-6.0, squash=0.92), M["gold"])], "Neck")
    g = join_parts([g] + parts, "Haubenwicht")
    print("HAUBENWICHT", len(g.data.polygons), "Flächen")

# ================================================================ Zirkelzischer (mittel, Zombie)

ZH = Vector((0.0, -0.1, 1.58))                  # Kopfmitte auf dem langen Hals
ZK = 0.72
ZMOUTH = (-0.108, -0.13, 0.165)                 # Maul fast geschlossen, zwei Zähne an der Oberlippe
Z_EYE, Z_EYE_SIZE = (0.123, 0.004), (0.08, 0.062)
Z_NECK = [(0.0, 0.0, 1.16), (0.0, 0.03, 1.28), (0.0, 0.04, 1.4), (0.0, 0.0, 1.5), (0.0, -0.05, 1.56)]
Z_FOOT = (0.19, 0.04, 0.195)                    # Pfote: x, y (Knöchel), Größe
# Jacke: Höhe -> halbe Breite, halbe Tiefe (liegt mit Abstand über dem Körper, unten ausgestellt)
VEST = [(1.175, 0.09, 0.085), (1.15, 0.105, 0.098), (1.12, 0.122, 0.11), (1.07, 0.138, 0.126), (1.0, 0.142, 0.132), (0.93, 0.132, 0.128), (0.87, 0.126, 0.122),
        (0.8, 0.126, 0.12), (0.74, 0.13, 0.122), (0.7, 0.136, 0.128), (0.66, 0.144, 0.134)]
# (so schmal wie der Rumpf des Grundmodells: die Arme schwingen in allen Bewegungen außen an der Jacke vorbei)
VEST_TOP, VEST_V = 1.175, 0.83                   # Kragen; hier endet der Ausschnitt vorn
VEST_HOLE = 0.098                               # Armausschnitt: weit genug, dass der Arm in jeder Bewegung frei bleibt

def vest_at(z):
    zs = [v[0] for v in VEST][::-1]
    return float(np.interp(z, zs, [v[1] for v in VEST][::-1])), float(np.interp(z, zs, [v[2] for v in VEST][::-1]))

def vest_open(z):
    return 0.068 * max(0.0, (z - VEST_V) / (VEST_TOP - VEST_V)) ** 0.9

def vest_hem(phi):
    return 0.685 - 0.04 * math.exp(-(math.degrees(min(phi, 2 * math.pi - phi)) / 28) ** 2)          # Spitze vorn in der Mitte

def loop_tube(name, pts, r, segs=10):
    """Geschlossener Wulst entlang einer Linie (Anfang und Ende überlappen)"""
    q = [tuple(p) for p in pts]
    q = [q[-1]] + q + q[:2]
    return tube(name, q, [0.0] + [r] * (len(q) - 2) + [0.0], segs=segs)

def frame_of(axis):
    z = Vector(axis).normalized()
    x = z.cross(Vector((0, 1, 0)))
    x = x.normalized() if x.length > 1e-3 else Vector((1, 0, 0))
    return x, z.cross(x).normalized(), z

def spine_weights(o, arm, bones=("Hips", "Spine", "Spine1", "Spine2"), only=None):
    """Kleidung am Rumpf: Gewichte weich nach der Höhe zwischen den Wirbelknochen verteilt (keine Arm- oder Beinknochen).
    So bleiben Stoff und Kanten in der Bewegung glatt, statt dass jede Stelle an einem anderen Knochen zieht.
    only(Punkt): nur diese Punkte (für die Haut unter der Kleidung, damit sie genau wie der Stoff läuft)."""
    heads = [B(arm, b).z for b in bones]
    mids = [(a + b) / 2 for a, b in zip(heads, heads[1:])] + [heads[-1] + 0.06]
    groups = [o.vertex_groups.get("mixamorig:" + b) or o.vertex_groups.new(name="mixamorig:" + b) for b in bones]
    for v in o.data.vertices:
        if only:
            if not only(v.co):
                continue
            for g in o.vertex_groups:
                g.remove([v.index])
        z = v.co.z
        if z <= mids[0]:
            w = [1.0] + [0.0] * (len(bones) - 1)
        elif z >= mids[-1]:
            w = [0.0] * (len(bones) - 1) + [1.0]
        else:
            w = [0.0] * len(bones)
            for i in range(len(bones) - 1):
                if mids[i] <= z <= mids[i + 1]:
                    t = smooth01((z - mids[i]) / (mids[i + 1] - mids[i])); w[i] = 1 - t; w[i + 1] = t
        for g, wi in zip(groups, w):
            if wi > 1e-4:
                g.add([v.index], wi, 'REPLACE')

def vest_parts(arm):
    """Ärmellose Jacke als eigenes Kleidungsstück mit sauberen Kanten: liegt über Schultern und Rumpf, vorn ein
    Ausschnitt bis zur Brustmitte (darunter geschlossen, ohne Naht), runde Armlöcher, unten ein ausgestellter Schoß
    mit Spitze vorn; an Ausschnitt, Armlöchern und Saum eine helle Borte, die genau auf der Kante liegt.
    Liefert (Stoffteile, Borten); beide werden mit der Haut verbunden und mit Verläufen bemalt."""
    nz, ncol = 30, 72
    bm = bmesh.new(); grid = []
    for j in range(ncol + 1):
        row = []
        for i in range(nz + 1):
            t = i / nz; f = j / ncol
            z_mid = VEST_TOP + (vest_hem(math.pi) - VEST_TOP) * t
            phi0 = math.asin(min(0.95, vest_open(z_mid) / max(vest_at(z_mid)[0], 1e-3)))
            phi = phi0 + (2 * math.pi - 2 * phi0) * f
            zz = VEST_TOP + (vest_hem(phi) - VEST_TOP) * t
            rx, ry = vest_at(zz)
            row.append(bm.verts.new((rx * math.sin(phi), -ry * math.cos(phi), zz)))
        grid.append(row)
    for a, b in zip(grid, grid[1:]):
        for i in range(nz):
            bm.faces.new([a[i], a[i + 1], b[i + 1], b[i]])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0015)       # unter dem Ausschnitt schließt sich die Front
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = finish("Jacke", bm)
    md = o.modifiers.new("Dicke", 'SOLIDIFY'); md.thickness = 0.02; md.offset = 1.0; apply_mod(o, md)
    bvh = BVHTree.FromObject(o, bpy.context.evaluated_depsgraph_get())
    parts = []; holes = []; cloth = []
    for s, side in ((1, "Left"), (-1, "Right")):                   # Armlöcher: mit einem Zylinder sauber ausgeschnitten
        sh, el = B(arm, side + "Arm"), B(arm, side + "ForeArm")
        d = (el - sh).normalized(); x, y, _ = frame_of(d); Rh = VEST_HOLE
        cyl = tube("Armloch", [tuple(sh - d * 0.1), tuple(sh - d * 0.09), tuple(sh + d * 0.3), tuple(sh + d * 0.31)], [0.0, Rh, Rh, 0.0], segs=40)
        md = o.modifiers.new("Loch", 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = cyl; md.solver = 'EXACT'
        apply_mod(o, md)
        bpy.data.objects.remove(cyl, do_unlink=True)
        ring = []
        for q in [i * 2 * math.pi / 36 for i in range(36)]:        # Kante des Lochs auf der Außenseite der Jacke
            p0 = sh + (x * math.cos(q) + y * math.sin(q)) * Rh + d * 0.35
            hit = bvh.ray_cast(p0, -d, 0.6)[0]
            ring.append(hit)
        holes.append(ring)
    md = o.modifiers.new("Kanten", 'EDGE_SPLIT'); md.split_angle = math.radians(50); apply_mod(o, md)
    for pl in o.data.polygons:
        pl.use_smooth = True
    cloth.append(o)
    edge = []
    for sgn in (1, -1):                                             # Borte am Ausschnitt: vom Kragen zur Spitze und zurück
        zs = np.linspace(VEST_TOP - 0.006, VEST_V - 0.004, 18) if sgn > 0 else np.linspace(VEST_V - 0.004, VEST_TOP - 0.006, 18)
        for zz in zs:
            rx, ry = vest_at(zz)
            xx = vest_open(max(zz, VEST_V)) * sgn
            edge.append((xx, -(ry + 0.01) * math.sqrt(max(0.0, 1 - (xx / rx) ** 2)), float(zz)))
    parts.append(tube("Jackenrand", [edge[0]] + edge + [edge[-1]], [0.0] + [0.014] * len(edge) + [0.0], segs=10))
    hem_pts = []
    for j in range(64):
        phi = j * 2 * math.pi / 64
        zz = vest_hem(phi); rx, ry = vest_at(zz)
        hem_pts.append(((rx + 0.01) * math.sin(phi), -(ry + 0.01) * math.cos(phi), zz))
    parts.append(loop_tube("Jackensaum", hem_pts, 0.016, segs=12))
    for k, ring in enumerate(holes):
        hit = [h for h in ring if h is not None]
        if len(hit) >= len(ring) - 3:
            parts.append(loop_tube("Armlochborte%d" % k, hit, 0.013, segs=10))
        elif len(hit) >= 6:                                         # das Loch schneidet die Schulterkante: Borte als Bogen
            i0 = next(i for i in range(len(ring)) if ring[i] is None and ring[(i + 1) % len(ring)] is not None)
            run = []
            for j in range(1, len(ring) + 1):
                h = ring[(i0 + j) % len(ring)]
                if h is None:
                    break
                run.append(tuple(h))
            parts.append(tube("Armlochborte%d" % k, run, [0.0] + [0.013] * (len(run) - 2) + [0.0], segs=10))
    vz = VEST_V - 0.004                                              # kleiner Knoten an der Spitze des Ausschnitts
    parts.append(sphere("Jackenknoten", (0.0, -(vest_at(vz)[1] + 0.012), vz - 0.004), 0.018, (1.0, 0.8, 1.15)))
    for q in cloth + parts:
        spine_weights(q, arm)
    return [tag(q, 3) for q in cloth], [tag(q, 4) for q in parts]

def zischer_shape(arm):
    R = mb_family("Zischer")
    mb_ell(R, (0, 0.0, 1.0), (0.122, 0.112, 0.17))                                 # schmale Brust
    mb_ell(R, (0, 0.0, 0.82), (0.106, 0.1, 0.16))                                  # Taille
    mb_ell(R, (0, 0.0, 0.68), (0.118, 0.104, 0.1))                                 # Becken
    for s, side in ((1, "Left"), (-1, "Right")):
        sh, el, wr = B(arm, side + "Arm"), B(arm, side + "ForeArm"), B(arm, side + "Hand")
        mb_ball(R, (sh.x, sh.y, sh.z), 0.06)                                        # Schulter
        limb(R, [sh, el, wr + (wr - el).normalized() * 0.015], [0.046, 0.043])
        hip, kn, an = B(arm, side + "UpLeg"), B(arm, side + "Leg"), B(arm, side + "Foot")
        fx = Z_FOOT[0] * s
        limb(R, [hip, kn, (fx * 0.95, an.y, 0.24), (fx, an.y, 0.13)], [0.085, 0.072, 0.1])   # Unterschenkel wird zum Fuß hin breiter
    g = mb_to_mesh(R)
    P, _ = smooth3(Z_NECK, 24, passes=3)
    rad = np.interp(np.linspace(0, 1, 24), [0, 0.25, 0.7, 1], [0.115, 0.1, 0.1, 0.11])
    H = mb_family("Zischerkopf")
    snake_head(H, ZH, ZK)
    parts = [g, ring_tube("Hals", P, rad, depth=0.74), mb_to_mesh(H)]
    for s in (1, -1):
        parts += paw("Pfote%d" % s, Z_FOOT[0] * s, Z_FOOT[1], Z_FOOT[2])
    return parts

def paint_zischer(g, arm, brow_lines):
    bvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    ao = vertex_ao(g, rays=18, dist=0.3)
    T = texels(g); P, N, cov = T["P"], T["N"], T["cov"]
    AO = texel_values(T, ao)
    tags = texel_values(T, part_tags(g))
    skin = tags < 1.5; cloth = (tags > 2.5) & (tags < 3.5); trim = tags > 3.5
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    k = ZK; H = ZH
    jaw, mouth, hd = face_masks(P, H, k, ZMOUTH)
    head = (hd < 1.0) & skin
    col = violet(N)
    em = np.zeros(P.shape, np.float32)
    torso = (np.abs(x) < 0.2) & (z > 0.64) & (z < 1.19) & ~head
    # heller Bauch: Brust im Ausschnitt der Jacke, Vorderseite des Halses, Unterkiefer
    chest = smoothstep(0.012, -0.012, np.abs(x) - 0.08) * smoothstep(-0.05, -0.3, N[..., 1]) * (z > 0.78) * (z < 1.2) * torso * skin
    cy = np.interp(z, np.asarray(Z_NECK)[:, 2], np.asarray(Z_NECK)[:, 1])
    nfront = -(y - cy) / np.maximum(np.sqrt((y - cy) ** 2 + x * x), 1e-4)
    neck = (z > 1.2) * smoothstep(H.z - 0.1 * k, H.z - 0.19 * k, z) * (np.abs(x) < 0.13)
    nbel = smoothstep(0.35, 0.52, nfront) * neck * skin
    bel = np.clip(np.maximum(np.maximum(chest, nbel), jaw * head), 0, 1)
    bcol = belly_col(N)
    band = np.abs((((z + 1.0 * x * x) / 0.06) % 1.0) - 0.5) * 2
    bcol = mix(bcol, BELLY_LINE, 0.65 * smoothstep(0.78, 0.94, band) * np.maximum(chest, nbel) * (1 - jaw))
    col = col * (1 - bel[..., None]) + bcol * bel[..., None]
    col = mix(col, (0.16, 0.05, 0.26), mouth * head)
    col = brow_shade(P, col, brow_lines, 0.022 * k)
    col = paw_paint(P, N, col, [(Z_FOOT[0] * s, Z_FOOT[1], Z_FOOT[2], 3) for s in (1, -1)])
    # Jacke und Borte: Verlauf von hell (oben, zum Licht) nach dunkel, keine Einheitsfarbe
    tl = np.clip(0.5 + 0.38 * N[..., 2] - 0.22 * N[..., 1] + (z - 0.9) * 0.55, 0, 1)
    col = np.where(cloth[..., None], gradient((0.16, 0.06, 0.32), (0.37, 0.18, 0.62), tl), col)
    col = np.where(trim[..., None], gradient((0.42, 0.25, 0.7), (0.74, 0.57, 0.96), tl), col)
    # Leuchtstreifen: ein Bogen quer über die Stirn, je eine Sichel seitlich am Kopf, an Unterarm, Ober- und Unterschenkel
    lines = [([surf(bvh, (dx * k, -2.0, H.z + dz * k), (dx * k, 1.0, H.z + dz * k)) for dx, dz in ((-0.165, 0.175), (-0.095, 0.146), (0.0, 0.13), (0.095, 0.146), (0.165, 0.175))], 0.021)]
    for s, side in ((1, "Left"), (-1, "Right")):
        lines.append(([surf(bvh, (s * 1.0, H.y + dy * k, H.z + dz * k), (0.0, H.y + dy * k, H.z + dz * k)) for dy, dz in ((0.02, 0.1), (0.1, 0.085), (0.18, 0.04), (0.23, -0.03))], 0.02))
        el, wr = B(arm, side + "ForeArm"), B(arm, side + "Hand")
        mid = el.lerp(wr, 0.5); ax = (wr - el).normalized()
        lines.append([surf(bvh, mid + ax * t + Vector((s * 0.4, dy, 0.1)), mid + ax * t) for t, dy in ((-0.075, -0.07), (-0.025, -0.03), (0.025, 0.02), (0.075, 0.06))])
        hip, kn, an = B(arm, side + "UpLeg"), B(arm, side + "Leg"), B(arm, side + "Foot")
        for c, q in ((hip.lerp(kn, 0.62), 1), (kn.lerp(Vector((Z_FOOT[0] * s, an.y, 0.13)), 0.48), -1)):   # Oberschenkel schräg nach außen, Unterschenkel zurück
            lines.append([surf(bvh, (c.x + s * q * dx, -1.0, c.z + dz), (c.x + s * q * dx, 1.0, c.z + dz)) for dx, dz in ((-0.055, 0.085), (-0.024, 0.04), (0.018, -0.025), (0.046, -0.085))])
    fields = glow_stripes(P, lines, 0.03, bvh)
    keep = (1 - bel) * (1 - torso) * skin
    col = shade(col, AO, (1 - fields[0] * keep) * (1 - 0.5 * bel))
    col, em = paint_glow(col, em, fields, keep)
    finish_paint(T, col, em)

@variante("thron_zombie", "zombie")
def zirkelzischer(arm, body):
    remove_body(body)
    M = throne_mats(2048)
    g = join_parts(zischer_shape(arm), "Zirkelzischer")
    finish_skin(g, 0.009, 0.3)
    reduce(g, 0.16)
    tag(g, 0)
    bind_biped(g, arm, lambda c: "Head" if c.z > 1.3 else None)
    axes = [(B(arm, side + "Arm"), (B(arm, side + "ForeArm") - B(arm, side + "Arm")).normalized()) for side in ("Left", "Right")]
    def under_vest(c):                                              # Haut, die unter der Jacke liegt (nicht die Schultern in den Armausschnitten)
        if not (0.69 < c.z < 1.165):
            return False
        rx, ry = vest_at(c.z)
        if (c.x / (rx - 0.004)) ** 2 + (c.y / (ry - 0.004)) ** 2 > 1:
            return False
        return all(((c - a) - d * max(-0.03, (c - a).dot(d))).length > VEST_HOLE - 0.012 for a, d in axes)
    spine_weights(g, arm, only=under_vest)
    fbvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    brows, brow_lines = eye_brows(fbvh, ZH, ZK, Z_EYE, Z_EYE_SIZE, 0.022)
    rigid_parts(brows, "Head")
    hands = [comic_hand("Hand" + side, arm, side, k=0.76, n=4, curl=0.25, slim=0.82, reach=1.25, roll=math.radians(HAND_ROLL["zombie"])) for side in ("Left", "Right")]
    cloth, trim = vest_parts(arm)
    g = join_parts([g] + hands + brows + cloth + trim, "Zirkelzischer")
    for p in g.data.polygons:
        p.use_smooth = True
    g.data.materials.clear(); g.data.materials.append(M["skin"])
    smart_uv(g)
    paint_zischer(g, arm, brow_lines)
    parts = snake_face(M, fbvh, ZH, ZK, mouth=ZMOUTH, tongue=False, brows=False, eyes=False, fangs=False)
    parts += fangs(M, fbvh, ZH, ZK, ZMOUTH, 0.085, 0.062, r=0.019)
    parts += glow_eyes(M, fbvh, ZH, ZK, Z_EYE, Z_EYE_SIZE)
    rigid_parts(parts, "Head")
    parts += rigid_parts([give(gold_ring("Halsreif", (0, 0.01, 1.2), 0.125, 0.034, tilt=-8.0, squash=0.9), M["gold"])], "Spine2")
    g = join_parts([g] + parts, "Zirkelzischer")
    print("ZIRKELZISCHER", len(g.data.polygons), "Flächen")

# ================================================================ Thronwächter (stark, Brecher)

TH = Vector((0.0, -0.2, 1.38))                  # Kopfmitte: sitzt oben vorn auf dem Rumpf zwischen den Schulterplatten
TK = 1.12
TMOUTH = (-0.1, -0.122, 0.2)                    # breites, fast geschlossenes Maul
T_EYE, T_EYE_SIZE = (0.125, 0.0), (0.08, 0.056)
T_FOOT = (0.33, 0.06, 0.31)                     # Pfote: x, y (Knöchel), Größe

def gem_cap(name, center, axis, ra, rb, h, n=6, phase=0.0):
    """Geschliffener Kristall als Kappe mit sechseckigem Grundriss: zwei Kränze schräger Facetten und eine Tafel oben.
    Der Rand liegt genau im Goldrahmen, der Boden ist offen (er steckt im Körper)."""
    x, y, z = frame_of(axis)
    bm = bmesh.new()
    def ring(scale, height, shift):
        return [bm.verts.new(Vector(center) + x * (ra * scale * math.cos(phase + (i + shift) * 2 * math.pi / n)) + y * (rb * scale * math.sin(phase + (i + shift) * 2 * math.pi / n)) + z * height) for i in range(n)]
    r0 = ring(1.0, -0.03, 0.0); r1 = ring(1.0, 0.1 * h, 0.0); r2 = ring(0.84, 0.52 * h, 0.5); r3 = ring(0.5, 0.88 * h, 0.0)
    top = bm.verts.new(Vector(center) + z * h)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([r0[i], r0[j], r1[j], r1[i]])
        bm.faces.new([r1[i], r1[j], r2[i]]); bm.faces.new([r2[i], r1[j], r2[j]])
        bm.faces.new([r2[i], r2[j], r3[j]]); bm.faces.new([r2[i], r3[j], r3[i]])
        bm.faces.new([r3[i], r3[j], top])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finish(name, bm, smooth=False)

def gold_band(name, center, axis, ra, rb, w, h, n=6, phase=0.0):
    """Kantiger Goldreif um einen Kristall oder um den Arm: Vieleck mit abgeschrägtem Querschnitt"""
    x, y, z = frame_of(axis)
    prof = ((-0.4 * w, -0.5 * h), (0.7 * w, -0.5 * h), (1.0 * w, -0.18 * h), (1.0 * w, 0.18 * h), (0.7 * w, 0.5 * h), (-0.4 * w, 0.5 * h))
    bm = bmesh.new(); rings = []
    for i in range(n):
        a = phase + i * 2 * math.pi / n
        out = x * math.cos(a) + y * math.sin(a)
        base = Vector(center) + x * (ra * math.cos(a)) + y * (rb * math.sin(a))
        rings.append([bm.verts.new(base + out * dw + z * dh) for dw, dh in prof])
    m = len(prof)
    for i in range(n):
        a, b = rings[i], rings[(i + 1) % n]
        for j in range(m):
            bm.faces.new([a[j], b[j], b[(j + 1) % m], a[(j + 1) % m]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finish(name, bm, smooth=False)

def gem_sleeve(name, a, b, r0, r1, bulge, n=8):
    """Kristall-Armschiene: geschliffene Hülse rund um den Unterarm (liegt überall auf), in der Mitte bauchig"""
    a, b = Vector(a), Vector(b); x, y, z = frame_of(b - a); L = (b - a).length
    bm = bmesh.new(); rings = []
    for k, (t, r, shift) in enumerate(((0.0, r0, 0.0), (0.3, r0 + bulge, 0.5), (0.7, r1 + bulge, 0.0), (1.0, r1, 0.5))):
        rings.append([bm.verts.new(a + z * (L * t) + (x * math.cos((i + shift) * 2 * math.pi / n) + y * math.sin((i + shift) * 2 * math.pi / n)) * r) for i in range(n)])
    for (ra_, rb_), flip in zip(zip(rings, rings[1:]), (0, 1, 0)):
        for i in range(n):
            j = (i + 1) % n
            if flip:
                bm.faces.new([ra_[i], ra_[j], rb_[j]]); bm.faces.new([ra_[i], rb_[j], rb_[i]])
            else:
                bm.faces.new([ra_[i], ra_[j], rb_[i]]); bm.faces.new([rb_[i], ra_[j], rb_[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finish(name, bm, smooth=False)

def guard_shape(arm):
    R = mb_family("Waechter")
    mb_ell(R, (0, 0.04, 1.12), (0.44, 0.33, 0.28))                                 # breite, gewölbte Brust
    mb_ell(R, (0, 0.03, 0.84), (0.29, 0.31, 0.26))                                 # Bauch: schmal genug, dass Unterarme und Armschienen außen vorbeigehen
    mb_ell(R, (0, 0.03, 0.64), (0.26, 0.26, 0.16))                                 # Becken
    mb_ell(R, (0, 0.08, 1.32), (0.28, 0.27, 0.2))                                  # Nacken: der Kopf wächst oben aus dem Rumpf
    mb_caps(R, (0, 0.02, 1.3), (0, -0.14, 1.37), 0.2)                              # dicker Hals trägt den Kopf nach vorn
    for s in (1, -1):
        mb_ell(R, (0.2 * s, -0.2, 1.1), (0.2, 0.12, 0.16))                          # angedeutete Brustmuskeln
    snake_head(R, TH, TK)
    for s, side in ((1, "Left"), (-1, "Right")):
        sh, el, wr = B(arm, side + "Arm"), B(arm, side + "ForeArm"), B(arm, side + "Hand")
        mb_ball(R, (sh.x, sh.y, sh.z), 0.23)                                        # runde Schulter (darauf sitzt die Kristallkappe)
        limb(R, [sh, el, wr + (wr - el).normalized() * 0.03], [0.165, 0.15])
        limb(R, [(0.16 * s, 0.0, 0.58), (0.24 * s, 0.0, 0.4), (0.31 * s, 0.03, 0.22)], [0.165, 0.2])     # Hüfte schmal, die Fäuste schwingen frei daneben
    parts = [mb_to_mesh(R)]
    for s in (1, -1):
        parts += paw("Pfote%d" % s, T_FOOT[0] * s, T_FOOT[1], T_FOOT[2])
    return parts

def facet(o, tagv):
    """Geschliffenes Teil: harte Kanten bleiben beim Verbinden erhalten"""
    md = o.modifiers.new("Kanten", 'EDGE_SPLIT'); md.split_angle = math.radians(18); apply_mod(o, md)
    return tag(o, tagv)

def guard_armor(arm, M):
    """Rüstung: Auf jeder Schulter liegt eine Kristallkappe in einem runden Goldrand, wie ein Schulterstück, das am
    Rumpf sitzt (nicht am Arm) und Abstand zum Kopf hält. Am Unterarm eine Kristallhülse zwischen zwei Goldreifen.
    Liefert (Kristallteile für die Bemalung, Goldteile); die Gewichte sind gesetzt."""
    crystal, gold = [], []
    for s, side in ((1, "Left"), (-1, "Right")):
        sh, el, wr = B(arm, side + "Arm"), B(arm, side + "ForeArm"), B(arm, side + "Hand")
        axis = Vector((s * 0.7, -0.05, 0.71)).normalized()         # nach außen oben: liegt auf der Schulterkuppe
        c = sh + axis * 0.1
        ra = rb = 0.24
        cap = facet(gem_cap("Schulterkristall%d" % s, c, axis, ra, rb, 0.2, n=8, phase=math.pi / 8), 5)
        band = give(gold_band("Schulterrand%d" % s, c, axis, ra, rb, 0.042, 0.075, n=28), M["gold"])
        for pl in band.data.polygons:
            pl.use_smooth = True
        rigid_parts([cap, band], side + "Shoulder")
        crystal.append(cap); gold.append(band)
        ax = (wr - el).normalized(); L = (wr - el).length
        a, b = el + ax * (0.32 * L), el + ax * (0.88 * L)
        sleeve = facet(gem_sleeve("Armkristall%d" % s, a, b, 0.168, 0.168, 0.03), 5)
        bands = [give(gold_band("Armreif%d%d" % (s, i), q, ax, 0.168, 0.168, 0.034, 0.06, n=28), M["gold"]) for i, q in enumerate((a, b))]
        for o in bands:
            for pl in o.data.polygons:
                pl.use_smooth = True
        rigid_parts([sleeve] + bands, side + "ForeArm")
        crystal.append(sleeve); gold += bands
    return crystal, gold

def paint_guard(g, arm, brow_lines):
    bvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    ao = vertex_ao(g, rays=18, dist=0.35)
    T = texels(g); P, N, cov = T["P"], T["N"], T["cov"]
    AO = texel_values(T, ao)
    gem = texel_values(T, part_tags(g)) > 4.5                       # Kristalle, sonst Haut
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    k = TK; H = TH
    jaw, mouth, hd = face_masks(P, H, k, TMOUTH)
    head = (hd < 1.0) & ~gem
    col = violet(N)
    em = np.zeros(P.shape, np.float32)
    # Bauchschild: oben breit unter dem Kiefer, nach unten spitz, mit geschwungenen Querlinien
    tz = np.clip((z - 0.6) / 0.62, 0, 1)
    wz = 0.26 * tz ** 0.6
    edge = np.abs(x) - wz
    plate = smoothstep(0.014, -0.014, edge) * (z > 0.6) * (z < 1.22) * smoothstep(-0.05, -0.32, N[..., 1]) * (~head) * (np.abs(x) < 0.29) * (~gem)
    bel = np.clip(np.maximum(plate, jaw * head), 0, 1)
    bcol = belly_col(N)
    lines = np.zeros(P.shape[:-1], np.float32)
    for zl in (0.74, 0.86, 0.98, 1.1):
        lines = np.maximum(lines, np.clip(1.4 * (1 - np.abs(z - 0.35 * x * x - zl) / 0.012), 0, 1))
    bcol = mix(bcol, BELLY_LINE, 0.7 * lines * plate)
    bcol = mix(bcol, BELLY_LINE, 0.45 * smoothstep(-0.05, -0.005, edge) * plate)
    col = col * (1 - bel[..., None]) + bcol * bel[..., None]
    col = mix(col, (0.16, 0.05, 0.26), mouth * head)
    col = brow_shade(P, col, brow_lines, 0.024 * k)
    col = paw_paint(P, N, col, [(T_FOOT[0] * s, T_FOOT[1], T_FOOT[2], 3) for s in (1, -1)])
    # Kristalle: jede Schlifffläche mit eigenem Ton, von oben hell nach unten tief violett, dazu ein inneres Leuchten
    tg = np.clip(0.5 + 0.42 * N[..., 2] - 0.18 * N[..., 1] + 1.3 * (z - np.where(z > 1.08, 1.34, 0.9)), 0, 1)
    gcol = np.where((tg < 0.5)[..., None], gradient((0.17, 0.05, 0.42), (0.4, 0.17, 0.78), tg * 2), gradient((0.4, 0.17, 0.78), (0.68, 0.47, 0.97), tg * 2 - 1))
    col = np.where(gem[..., None], gcol, col)
    em = em + np.where(gem[..., None], gcol * 0.35, 0).astype(np.float32)
    # Leuchtstreifen: zwei kurze Bögen auf der Stirn, Sicheln an den Flanken neben dem Schild, schräg über die
    # Oberschenkel, zwei auf dem Rücken
    lines3 = []
    for s in (1, -1):
        lines3.append(([surf(bvh, (s * dx * k, -2.0, H.z + dz * k), (s * dx * k, 1.0, H.z + dz * k)) for dx, dz in ((0.04, 0.112), (0.09, 0.132), (0.14, 0.143), (0.185, 0.135))], 0.022))
        lines3.append([surf(bvh, (s * dx, -1.5, dz), (s * dx, 1.0, dz)) for dx, dz in ((0.25, 1.0), (0.245, 0.9), (0.225, 0.8), (0.19, 0.72))])   # auf der Flanke, nicht in der Achselfalte
        lines3.append([surf(bvh, (s * (0.23 + dx), -1.5, 0.43 + dz), (s * (0.23 + dx), 1.0, 0.43 + dz)) for dx, dz in ((-0.13, 0.13), (-0.055, 0.08), (0.03, 0.0), (0.1, -0.1))])
        lines3.append([surf(bvh, (s * dx, 1.5, dz), (s * dx, -1.0, dz)) for dx, dz in ((0.2, 1.0), (0.26, 0.9), (0.26, 0.78), (0.2, 0.68))])
    fields = glow_stripes(P, lines3, 0.04, bvh)
    keep = (1 - bel) * (1 - (head & (z < H.z + 0.08 * k))) * (~gem)
    col = shade(col, AO, (1 - fields[0] * keep) * (1 - 0.5 * bel) * (1 - 0.6 * gem))
    col, em = paint_glow(col, em, fields, keep)
    finish_paint(T, col, em)

@variante("thron_brecher", "brecher")
def thronwaechter(arm, body):
    remove_body(body)
    M = throne_mats(2048)
    g = join_parts(guard_shape(arm), "Thronwaechter")
    finish_skin(g, 0.014, 0.3)
    reduce(g, 0.16)
    tag(g, 0)
    def rigid(c):
        q = Vector(((c.x - TH.x) / (0.3 * TK), (c.y - TH.y) / (0.38 * TK), (c.z - TH.z) / (0.28 * TK)))
        return "Head" if q.length < 1.0 and c.y < TH.y + 0.16 else None
    bind_biped(g, arm, rigid, core=lambda c: smooth01((0.38 - abs(c.x)) / 0.14) * smooth01((1.22 - c.z) / 0.1) * smooth01((c.z - 0.52) / 0.08))
    fbvh = BVHTree.FromObject(g, bpy.context.evaluated_depsgraph_get())
    brows, brow_lines = eye_brows(fbvh, TH, TK, T_EYE, T_EYE_SIZE, 0.024)
    rigid_parts(brows, "Head")
    hands = [comic_hand("Hand" + side, arm, side, k=1.6, n=4, curl=0.9, roll=math.radians(HAND_ROLL["brecher"])) for side in ("Left", "Right")]
    crystal, gold = guard_armor(arm, M)
    g = join_parts([g] + hands + brows + crystal, "Thronwaechter")
    for p in g.data.polygons:
        p.use_smooth = True
    g.data.materials.clear(); g.data.materials.append(M["skin"])
    smart_uv(g)
    paint_guard(g, arm, brow_lines)
    parts = snake_face(M, fbvh, TH, TK, mouth=TMOUTH, tongue=False, brows=False, eyes=False, fangs=False)
    parts += fangs(M, fbvh, TH, TK, TMOUTH, 0.112, 0.062, r=0.02)
    parts += glow_eyes(M, fbvh, TH, TK, T_EYE, T_EYE_SIZE)
    rigid_parts(parts, "Head")
    g = join_parts([g] + parts + gold, "Thronwaechter")
    print("THRONWAECHTER", len(g.data.polygons), "Flächen")

if __name__ == "__main__":
    run(VAR, OUT)
