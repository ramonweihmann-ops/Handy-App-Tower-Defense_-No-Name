# Edelsteingolem neu (Entwurf „Smaragdhüter“ von ChatGPT, vom Nutzer freigegeben am 25.11.2026):
# Vorlage_Raw/Edelsteingolem_Neuentwurf_v1 (01_turnaround.png maßgeblich, 02_kopf_und_angriff.png, LIESMICH_CLAUDE.md).
# Vereinfachte Detailstufe wie in der Vorlage: großer, glatter dunkelgrüner Steinkörper mit runden Formen, breite
# warmgoldene Fassungen (Schulterpanzer, Kragen, achteckiger Brustrahmen, Gürtel mit Schurz, Armreifen, Beinreifen) und
# wenige große Smaragde im Smaragdschliff. Kopf mit niedriger, fester Krone (vorn große Zinne mit Smaragd, seitlich runde
# Zinnen mit Smaragden, hinten glatte Zinne), schweren Goldbrauen, grünen Augen mit dunklen Pupillen und schmalem,
# goldumrandetem Comicmaul mit zwei kleinen Smaragdzähnen. Große Hände mit vier Fingern und Daumen, runde Kuppelfüße.
# Jeder Goldreif ist ein eigenes, sauberes Teil (Nutzerhinweis 25.11.2026: Ringe einzeln, nicht verbunden).
# Maße aus dem Turnaround abgenommen (Maßstab 0,00338 m je Bildpunkt); die Vorlage zeigt die Gehhaltung, in der der
# Oberkörper um DZ höher steht als in der Ruhehaltung, in der hier gebaut wird.
# Skelett und Bewegungen des Koloss; Haut aus Metaballs (Bone Heat), Gold, Steine und Füße starr an ihren Knochen.
# Aufruf: blender -b -P tools/monster/edelsteingolem.py -- edelstein_golem <ziel.glb>
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kristallriese import *          # Metaballs, Hände (star_hand), Bone Heat, Hilfen
from fabrikmutter import rbox, smooth_obj
import boss_aufsatz
boss_aufsatz.EXPORT_IMAGE_FORMAT = "JPEG"

DZ = 0.113                          # Gehhaltung hebt den Oberkörper um so viel an

def R(z):
    """Höhe aus der Vorlage (Gehhaltung) in die Ruhehaltung umrechnen"""
    return z - DZ

HEAD_C = Vector((0, -0.075, R(1.515)))
HEAD_SEMI = (0.345, 0.33, 0.3)

# ---------------------------------------------------------------- Materialien

def eye_material():
    """Leuchtend hellgrünes Auge, dunkelgrüne Pupille mit schwarzem Kern zur Nase hin (böser Blick), Glanzpunkt"""
    n = 256; yy, xx = np.mgrid[0:n, 0:n]
    u = (xx + 0.5) / n * 2 - 1; v = (yy + 0.5) / n * 2 - 1           # u: zur Nase hin, v: nach oben
    r = np.sqrt(u * u + v * v)
    pu, pv = 0.3, 0.06
    rp = np.sqrt((u - pu) ** 2 + (v - pv) ** 2)
    col = np.zeros((n, n, 3), np.float32)
    col[:] = (0.62, 0.95, 0.12)
    glow = smoothstep(0.75, 0.2, rp)[..., None]
    col = col * (1 - glow) + np.asarray((0.88, 1.0, 0.45), np.float32) * glow
    edge = smoothstep(0.7, 0.98, r)[..., None]
    col = col * (1 - edge * 0.55) + np.asarray((0.1, 0.35, 0.05), np.float32) * edge * 0.55
    col = np.where((rp < 0.54)[..., None], np.asarray((0.06, 0.25, 0.06), np.float32), col)
    col = np.where((rp < 0.31)[..., None], np.asarray((0.01, 0.04, 0.015), np.float32), col)
    hl = np.sqrt((u - pu + 0.13) ** 2 + (v - pv - 0.13) ** 2) < 0.08
    col = np.where(hl[..., None], np.asarray((0.95, 1.0, 0.9), np.float32), col)
    col = np.where((r > 0.97)[..., None], np.asarray((0.03, 0.08, 0.04), np.float32), col)
    arr = np.ones((n, n, 4), np.float32); arr[..., :3] = col
    m = bpy.data.materials.new("Golemauge"); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = new_image("Golemauge_Bild", arr)
    nt.links.new(tex.outputs["Color"], p.inputs["Base Color"]); nt.links.new(tex.outputs["Color"], p.inputs["Emission Color"])
    p.inputs["Emission Strength"].default_value = 1.2; p.inputs["Roughness"].default_value = 0.12
    return m

def golem_mats():
    return {
        "skin": look("Smaragdstein", (0.15, 0.33, 0.2), rough=0.38),
        "gold": look("Warmgold", (0.93, 0.6, 0.16), rough=0.3, metal=0.5),
        "gem": look("Smaragd", (0.04, 0.62, 0.16), rough=0.06, emit=(0.0, 0.45, 0.08), strength=0.25),
        "dark": look("Maulschatten", (0.03, 0.08, 0.04), rough=0.7),
        "eye": eye_material(),
    }

# ---------------------------------------------------------------- allgemeine Formen

def frame3(n, up_hint=(0, 0, 1)):
    """Rechtshändiges Dreibein: x quer, y = n (nach außen), z möglichst nach up_hint"""
    n = Vector(n).normalized(); up = Vector(up_hint)
    up = (up - n * up.dot(n)).normalized()
    x = n.cross(up)
    return Matrix((x, n, up)).transposed()

def rrect(w, h, c, n=4):
    """Abgerundetes Rechteck (halbe Breite w, halbe Höhe h, Eckradius c) als geschlossene Punktfolge"""
    pts = []
    for cx, cz, a0 in ((w - c, h - c, 0), (-w + c, h - c, 90), (-w + c, -h + c, 180), (w - c, -h + c, 270)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + c * math.cos(a), cz + c * math.sin(a)))
    return pts

def sweep_loop(name, sections, closed=True):
    """Fläche aus Querschnitten (Liste gleich langer, geschlossener Punktringe)"""
    bm = bmesh.new()
    rings = [[bm.verts.new(p) for p in s] for s in sections]
    m = len(rings[0])
    pairs = list(zip(rings, rings[1:])) + ([(rings[-1], rings[0])] if closed else [])
    for a, b in pairs:
        for k in range(m):
            bm.faces.new([a[k], a[(k + 1) % m], b[(k + 1) % m], b[k]])
    if not closed:
        bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finish(name, bm, smooth=True)

def lathe_ring(name, center, axis, r_in, r_out, half, corner, mat, ell=(1.0, 1.0), ref=(1, 0, 0), segs=64):
    """Reif um eine Achse: Querschnitt abgerundetes Rechteck (radial r_in..r_out, axial ±half), elliptisch ell"""
    axis = Vector(axis).normalized(); u = Vector(ref); u = (u - axis * u.dot(axis)).normalized(); v = axis.cross(u)
    prof = rrect((r_out - r_in) / 2, half, corner)
    rm = (r_in + r_out) / 2
    secs = []
    for k in range(segs):
        a = 2 * math.pi * k / segs; d = u * math.cos(a) * ell[0] + v * math.sin(a) * ell[1]
        secs.append([Vector(center) + d * (rm + pr) + axis * pa for pr, pa in prof])
    o = sweep_loop(name, secs)
    smooth_obj(o, 60)
    return give(o, mat)

def hug_ring(name, bvh, origins, dirs, height, thick, mat, gap=0.0, corner=None, win=4):
    """Breites Band, das außen auf der Haut liegt: Strahlen von innen nach außen, Abstände geglättet"""
    hits = []
    for o, d in zip(origins, dirs):
        h = bvh.ray_cast(o, d, 3.0)
        hits.append((h[0] - o).length if h[0] is not None else None)
    good = [x for x in hits if x is not None]
    hits = [x if x is not None else sum(good) / len(good) for x in hits]
    N = len(hits)
    dist = [sum(hits[(i + k) % N] for k in range(-win, win + 1)) / (2 * win + 1) for i in range(N)]
    pts = [o + d * r for o, d, r in zip(origins, dirs, dist)]
    nrm = []
    for i in range(N):
        h = bvh.find_nearest(pts[i])
        nrm.append(h[1] if h[0] is not None else dirs[i])
    nrm = [sum((nrm[(i + k) % N] for k in range(-win, win + 1)), Vector()).normalized() for i in range(N)]
    prof = rrect(thick / 2, height / 2, corner if corner else min(thick, height) * 0.45)
    secs = []
    for i in range(N):
        t = (pts[(i + 1) % N] - pts[i - 1]).normalized(); n = nrm[i]
        if n.dot(dirs[i]) < 0:
            n = -n
        w = n.cross(t).normalized()
        if w.z < 0:
            w = -w
        n2 = t.cross(w).normalized()
        n = n2 if n2.dot(n) > 0 else -n2
        secs.append([pts[i] + n * (gap + thick / 2 + pr) + w * pz for pr, pz in prof])
    o = sweep_loop(name, secs)
    smooth_obj(o, 60)
    return give(o, mat)

def octa(hw, hh, ch):
    return [(hw - ch, -hh), (hw, -hh + ch), (hw, hh - ch), (hw - ch, hh), (-hw + ch, hh), (-hw, hh - ch), (-hw, -hh + ch), (-hw + ch, -hh)]

def emerald_cut(name, p, F, hw, hh, depth, mat, ch=0.3):
    """Smaragd im Smaragdschliff: achteckige Rundiste, zwei Stufen, flache Tafel; hinten flacher Unterteil"""
    c = min(hw, hh) * ch * 2
    o8 = octa(hw, hh, c)
    bm = bmesh.new(); rings = []
    for sc, dy in ((0.55, -depth * 0.5), (1.0, 0.0), (0.88, depth * 0.55), (0.66, depth)):
        rings.append([bm.verts.new(Vector(p) + F @ Vector((x * sc, dy, z * sc))) for x, z in o8])
    for a, b in zip(rings, rings[1:]):
        for k in range(8):
            bm.faces.new([a[k], a[(k + 1) % 8], b[(k + 1) % 8], b[k]])
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    g = finish(name, bm, smooth=False)
    return give(g, mat)

def octa_frame(name, p, F, outer, inner, front, back, mat, bevel=0.02):
    """Achteckiger Goldrahmen: outer/inner = (hw, hh, Fase), Vorderseite bei y=front, Rückseite bei y=back (lokal)"""
    O = octa(*outer); I = octa(*inner)
    bm = bmesh.new()
    vf = [bm.verts.new(Vector(p) + F @ Vector((x, front, z))) for x, z in O]
    vb = [bm.verts.new(Vector(p) + F @ Vector((x, back, z))) for x, z in O]
    wf = [bm.verts.new(Vector(p) + F @ Vector((x, front, z))) for x, z in I]
    wb = [bm.verts.new(Vector(p) + F @ Vector((x, back, z))) for x, z in I]
    for k in range(8):
        k1 = (k + 1) % 8
        bm.faces.new([vf[k], vf[k1], wf[k1], wf[k]])
        bm.faces.new([vb[k1], vb[k], wb[k], wb[k1]])
        bm.faces.new([vb[k], vb[k1], vf[k1], vf[k]])
        bm.faces.new([wf[k], wf[k1], wb[k1], wb[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = finish(name, bm, smooth=True)
    md = o.modifiers.new("Rund", 'BEVEL'); md.width = bevel; md.segments = 4; md.limit_method = 'ANGLE'
    md.angle_limit = math.radians(30); apply_mod(o, md)
    smooth_obj(o, 35)
    return give(o, mat)

def set_gem(name, p, n, hw, hh, depth, M, up=(0, 0, 1), rim=0.022):
    """Smaragd mit schmaler Goldfassung, Vorderseite in Richtung n"""
    F = frame3(n, up)
    ch = min(hw, hh) * 0.6
    fr = octa_frame(name + "Fassung", p, F, (hw + rim, hh + rim, ch + rim * 0.4), (hw * 0.97, hh * 0.97, ch * 0.97),
                    depth * 0.45, -depth * 0.9, M["gold"], bevel=min(rim * 0.45, 0.012))
    g = emerald_cut(name, p, F, hw, hh, depth, M["gem"])
    return [fr, g]

def front_hit(bvh, x, z, y0=-3.0):
    h = bvh.ray_cast(Vector((x, y0, z)), Vector((0, 1, 0)), 6.0)
    if h[0] is None:
        h = bvh.find_nearest(Vector((x, -0.3, z)))
    n = h[1]
    if n.y > 0:
        n = -n
    return h[0], n

# ---------------------------------------------------------------- Körper (Haut)

def golem_body(arm):
    """Haut aus Metaballs; gibt (Körper, BVH nur vom Rumpf mit Kopf) zurück"""
    T = mb_family("Rumpf")
    mb_ell(T, (0, 0.03, R(0.99)), (0.47, 0.45, 0.39))             # Rumpf: eine große runde Kugel
    mb_ell(T, (0, 0.08, 0.5), (0.27, 0.22, 0.13))                 # Becken
    mb_ell(T, tuple(HEAD_C), HEAD_SEMI)                           # großer runder Kopf ohne Hals
    mb_ell(T, (0, -0.09, R(1.42)), (0.36, 0.27, 0.17))            # breite Wangen unten am Kopf
    mb_ell(T, (0, -0.065, R(1.66)), (0.31, 0.25, 0.13))           # breite, flache Stirn unter der Krone
    mb_ell(T, (0, -0.06, R(1.76)), (0.27, 0.21, 0.05))            # Scheitel füllt die Krone bis unter den Rand
    mb_ell(T, (0, 0.0, R(1.31)), (0.3, 0.3, 0.12))                # Übergang Kopf – Schultern
    parts = []
    for side, s in (("Left", 1), ("Right", -1)):
        A_ = mb_family("Arm" + side)
        sh, el, wr = B(arm, side + "Arm"), B(arm, side + "ForeArm"), B(arm, side + "Hand")
        mb_ell(A_, (0.5 * s, 0.04, 1.17), (0.19, 0.19, 0.19))
        mb_caps(A_, sh, el, 0.175)
        c, semi, q = along(sh, el, 0.19, 0.21, 0.5); mb_ell(A_, c, semi, q)
        mb_caps(A_, el, wr, 0.13)
        mb_ell(A_, tuple(wr), (0.105, 0.105, 0.105))
        parts.append(A_)
        L_ = mb_family("Bein" + side)
        kn, an = B(arm, side + "Leg"), B(arm, side + "Foot")
        mb_caps(L_, (0.12 * s, 0.08, 0.5), kn, 0.19)
        mb_caps(L_, kn, an, 0.165)
        parts.append(L_)
    torso = mb_to_mesh(T)
    bvh = BVHTree.FromObject(torso, bpy.context.evaluated_depsgraph_get())
    body = join_parts([torso] + [mb_to_mesh(o) for o in parts], "Edelsteingolem")
    remesh(body, 0.012)
    md = body.modifiers.new("Glatt", 'SMOOTH'); md.factor = 0.5; md.iterations = 4; apply_mod(body, md)
    md = body.modifiers.new("Weniger", 'DECIMATE'); md.ratio = 0.2; apply_mod(body, md)
    for p in body.data.polygons:
        p.use_smooth = True
    return body, bvh

TORSO_BONES = (("Hips", 0.55), ("Spine", 0.72), ("Spine1", 0.9), ("Spine2", 1.1))

def torso_weights(body, tbvh, bones=None, zmin=0.42):
    """Rumpfhaut gleichmäßig nach der Höhe auf Becken und Wirbel verteilen (Bone Heat faltet den runden Bauch beim
    Gehen); Übergang zu Armen und Beinen über den Abstand zur reinen Rumpfform"""
    bones = bones or TORSO_BONES
    groups = {b: body.vertex_groups.get("mixamorig:" + b) or body.vertex_groups.new(name="mixamorig:" + b) for b, _ in bones}
    names = {g.index: g.name for g in body.vertex_groups}
    for v in body.data.vertices:
        h = tbvh.find_nearest(v.co)
        dist = (h[0] - v.co).length if h[0] is not None else 1.0
        t = smooth01((0.045 - dist) / 0.045) * smooth01((v.co.z - zmin) / 0.1)
        if t <= 0:
            continue
        grad = {}
        z = v.co.z
        if z <= bones[0][1]:
            grad[bones[0][0]] = 1.0
        elif z >= bones[-1][1]:
            grad[bones[-1][0]] = 1.0
        else:
            for (b0, z0), (b1, z1) in zip(bones, bones[1:]):
                if z0 <= z <= z1:
                    f = smooth01((z - z0) / (z1 - z0)); grad[b0] = 1 - f; grad[b1] = f
        old = {names[g.group]: g.weight for g in v.groups if names[g.group].startswith("mixamorig:")}
        tot = sum(old.values()) or 1.0
        new = {k: w / tot * (1 - t) for k, w in old.items()}
        for b, w in grad.items():
            new["mixamorig:" + b] = new.get("mixamorig:" + b, 0.0) + w * t
        for k, w in new.items():
            body.vertex_groups[k].add([v.index], w, 'REPLACE')

def bind_golem(body, arm, tbvh):
    """Bone Heat mit den Hauptknochen, Rumpf gleichmäßig nach der Höhe, der Kopf ganz am Kopfknochen"""
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
        q = v.co - HEAD_C
        d = math.sqrt((q.x / HEAD_SEMI[0]) ** 2 + (q.y / HEAD_SEMI[1]) ** 2 + (q.z / HEAD_SEMI[2]) ** 2)
        h = smooth01((1.2 - d) / 0.3) * smooth01((v.co.z - R(1.3)) / 0.1)
        if h <= 0:
            continue
        for g in v.groups:
            g.weight *= (1 - h)
        head.add([v.index], h, 'ADD')

# ---------------------------------------------------------------- Kopf: Krone, Brauen, Augen, Maul

def plateau(s, w, h, r, f=0.035):
    s = abs(s)
    if s <= w - r:
        return h
    if s <= w:
        return h - r + math.sqrt(max(0.0, r * r - (s - (w - r)) ** 2))
    if s <= w + f:
        return f - math.sqrt(max(0.0, f * f - (w + f - s) ** 2))
    return 0.0

def lobe(s, r, z0=0.03, f=0.03):
    """Runde Zinne: Kreis mit Mittelpunkt z0 über der Reifkante, Kehle f zum Reif"""
    s = abs(s)
    if s <= r:
        return z0 + math.sqrt(r * r - s * s)
    if s <= r + f:
        return f - math.sqrt(max(0.0, f * f - (r + f - s) ** 2))
    return 0.0

CROWN_TILT = math.radians(3)
LOBE_TH = math.radians(58)

def crown(M, bvh):
    """Niedrige, feste Krone: Reif mit großer Zinne vorn, runden Zinnen an den Seiten, glatter Zinne hinten;
    der Reif sitzt eng auf dem Kopf (Maße aus dem Kopfquerschnitt an der Reifkante)"""
    zb, hb, R0 = R(1.705), 0.105, 0.3
    c = Vector((0, HEAD_C.y + 0.01, zb))
    def reach(d):
        h = bvh.ray_cast(c, Vector(d), 2.0)
        return (h[0] - c).length
    fy, by = reach((0, -1, 0)), reach((0, 1, 0))
    c.y += (by - fy) / 2
    rbx = (reach((1, 0, 0)) + reach((-1, 0, 0))) / 2 - 0.006
    rby = (fy + by) / 2 - 0.006
    flare = 0.03
    N, J = 160, 4
    def top(th):
        def ds(t0):
            d = (th - t0 + math.pi) % (2 * math.pi) - math.pi
            return d * R0
        return hb + max(plateau(ds(0.0), 0.13, 0.25, 0.075), plateau(ds(math.pi), 0.1, 0.15, 0.09),
                        lobe(ds(LOBE_TH), 0.05, 0.0), lobe(ds(-LOBE_TH), 0.05, 0.0))
    Rx = Matrix.Rotation(CROWN_TILT, 3, 'X')
    bm = bmesh.new(); grid = []
    for k in range(N):
        th = 2 * math.pi * k / N; ht = top(th); col = []
        for j in range(J + 1):
            h = ht * j / J; f = h / 0.36
            p = Vector((math.sin(th) * (rbx + flare * f), -math.cos(th) * (rby + flare * f), h))
            col.append(bm.verts.new(c + Rx @ p))
        grid.append(col)
    for k in range(N):
        a, b = grid[k], grid[(k + 1) % N]
        for j in range(J):
            bm.faces.new([a[j], b[j], b[j + 1], a[j + 1]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = finish("Krone", bm, smooth=True)
    md = o.modifiers.new("Dicke", 'SOLIDIFY'); md.thickness = 0.052; md.offset = 0.0; md.use_even_offset = True; apply_mod(o, md)
    md = o.modifiers.new("Rund", 'BEVEL'); md.width = 0.02; md.segments = 4; md.limit_method = 'ANGLE'
    md.angle_limit = math.radians(35); apply_mod(o, md)
    smooth_obj(o, 40); give(o, M["gold"])
    parts = [o]
    cb = BVHTree.FromObject(o, bpy.context.evaluated_depsgraph_get())
    up = Rx @ Vector((0, 0, 1))
    d = Rx @ Vector((0, -1, 0)); tgt = c + Rx @ Vector((0, 0, hb + 0.13))
    h = cb.ray_cast(tgt + d * 2.0, -d, 3.0)
    n = h[1] if h[1].dot(d) > 0 else -h[1]
    parts += set_gem("KronSmaragdMitte", h[0] + n * 0.004, n, 0.078, 0.09, 0.032, M, up=up, rim=0.016)
    for nm, th in (("Links", LOBE_TH), ("Rechts", -LOBE_TH)):
        d = Rx @ Vector((math.sin(th), -math.cos(th), 0))
        tgt = c + Rx @ Vector((0, 0, hb + 0.03))
        h = cb.ray_cast(tgt + d * 2.0, -d, 3.0)
        n = (h[1] if h[1].dot(d) > 0 else -h[1]); n = (n + d).normalized()
        kc = h[0] + n * 0.0
        parts.append(lathe_ring("Kronknauf" + nm, kc, n, 0.012, 0.095, 0.038, 0.032, M["gold"], ref=up, segs=48))
        parts += set_gem("KronSmaragd" + nm, kc + n * 0.036, n, 0.044, 0.06, 0.03, M, up=up, rim=0.012)
    return parts

def brows(bvh, M):
    """Schwere Goldbrauen: dicke, runde Wülste schräg auf der Stirn (innen tief, außen hoch, böser Blick)"""
    out = []
    r0 = 0.038
    for s in (1, -1):
        a = Vector((0.04 * s, 0, R(1.608))); b = Vector((0.25 * s, 0, R(1.722)))
        L = (b - a).length; dv = (b - a) / L
        pts, rad = [], []
        for k in range(21):
            u = -r0 + (L + 2 * r0) * k / 20
            e = -u if u < 0 else (u - L if u > L else 0.0)
            q = a + dv * u
            p, n = front_hit(bvh, q.x, q.z)
            pts.append(p + Vector((0, -1, 0)) * (r0 * 0.7))
            rad.append(max(0.004, r0 * (0.88 + 0.2 * min(max(u / L, 0), 1)) * math.sqrt(max(0.0, 1 - (e / r0) ** 2))))
        o = tube("Braue%d" % s, pts, rad, segs=16)
        smooth_obj(o, 70)
        out.append(give(o, M["gold"]))
    return out

def eyes(bvh, M):
    out = []
    for s in (1, -1):
        p, n = front_hit(bvh, 0.13 * s, R(1.59))
        nn = (n + Vector((0, -1, 0))).normalized()
        inner = Vector((-s, 0, 0)); inner = (inner - nn * inner.dot(nn)).normalized()
        up = nn.cross(inner).normalized()
        if up.z < 0:
            up = -up
        a, dd, b = 0.074, 0.03, 0.068
        e = sphere("Auge%d" % s, (0, 0, 0), 1.0, (1, 1, 1), segs=(36, 18))
        cen = p + nn * 0.004
        F = Matrix((inner * a, nn * dd, up * b)).transposed().to_4x4()
        F.translation = cen
        e.data.transform(F)
        me = e.data; me.uv_layers.new(name="UVMap"); uvl = me.uv_layers.active.data
        for poly in me.polygons:
            for li in poly.loop_indices:
                q = me.vertices[me.loops[li].vertex_index].co - cen
                uvl[li].uv = (0.5 + 0.5 * q.dot(inner) / a, 0.5 + 0.5 * q.dot(up) / b)
        out.append(give(e, M["eye"]))
    return out

def closed_tube(name, pts, r, mat, segs=14):
    N = len(pts); secs = []
    for i in range(N):
        t = (pts[(i + 1) % N] - pts[i - 1]).normalized()
        a1 = t.orthogonal().normalized(); a2 = t.cross(a1)
        secs.append([pts[i] + (a1 * math.cos(2 * math.pi * k / segs) + a2 * math.sin(2 * math.pi * k / segs)) * r for k in range(segs)])
    o = sweep_loop(name, secs)
    smooth_obj(o, 60)
    return give(o, mat)

def rrect_dense(w, h, c, nc=6, nx=18, nz=3):
    """Abgerundetes Rechteck mit fester Punktzahl (Ecken und gerade Stücke unterteilt), beginnt rechts unten"""
    pts = []
    corners = ((w - c, h - c, 0), (-w + c, h - c, 90), (-w + c, -h + c, 180), (w - c, -h + c, 270))
    for i, (cx, cz, a0) in enumerate(corners):
        for k in range(nc + 1):
            a = math.radians(a0 + 90 * k / nc)
            pts.append((cx + c * math.cos(a), cz + c * math.sin(a)))
        nx_ = corners[(i + 1) % 4]
        p0 = pts[-1]
        a1 = math.radians(nx_[2])
        p1 = (nx_[0] + c * math.cos(a1), nx_[1] + c * math.sin(a1))
        m = nx if i in (0, 2) else nz
        for k in range(1, m):
            t = k / m
            pts.append((p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t))
    return pts

def mouth(bvh, M):
    """Schmales Comicmaul wie in der Vorlage: breiter, runder Goldrahmen (abgerundetes Rechteck), darin ein
    schmaler dunkler Schlitz, unten zwei kleine facettierte Smaragdzähne, die nach oben in den Schlitz ragen"""
    zc = R(1.448)
    outer = rrect_dense(0.222, 0.05, 0.047)
    inner = rrect_dense(0.168, 0.016, 0.015)
    secs = []
    for (xo, zo), (xi, zi) in zip(outer, inner):
        po, no = front_hit(bvh, xo, zc + zo); pi, ni = front_hit(bvh, xi, zc + zi)
        n = (no + ni).normalized(); mid = (po + pi) / 2; across = (po - pi); half = across.length / 2; across.normalize()
        secs.append([mid + across * x + n * (y + 0.01) for x, y in rrect(half, 0.025, min(half * 0.95, 0.023), n=4)])
    rim = sweep_loop("Maulrahmen", secs)
    smooth_obj(rim, 60); give(rim, M["gold"])
    parts = [rim]
    # Schlitz: Gitter innerhalb des Rahmens, knapp vor der Haut
    bm = bmesh.new(); G = []
    for j in range(7):
        row = []
        for i in range(31):
            x = -0.18 + 0.36 * i / 30; z = zc - 0.026 + 0.052 * j / 6
            p, n = front_hit(bvh, x, z)
            row.append(bm.verts.new(p + n * 0.004))
        G.append(row)
    for j in range(6):
        for i in range(30):
            bm.faces.new([G[j][i], G[j][i + 1], G[j + 1][i + 1], G[j + 1][i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    parts.append(give(finish("Maulschlitz", bm, smooth=True), M["dark"]))
    for s in (1, -1):
        p, n = front_hit(bvh, 0.096 * s, zc - 0.044)
        F = frame3(n, (0, 0, 1))
        base = p + n * 0.04
        bm = bmesh.new(); rings = []
        for rr, hz in ((0.037, -0.008), (0.037, 0.008), (0.025, 0.034)):
            rings.append([bm.verts.new(base + F @ Vector((math.cos(math.radians(22.5 + 45 * k)) * rr,
                                                          math.sin(math.radians(22.5 + 45 * k)) * rr * 0.75, hz))) for k in range(8)])
        tip = bm.verts.new(base + F @ Vector((0, 0.004, 0.056)))
        for a, b in zip(rings, rings[1:]):
            for k in range(8):
                bm.faces.new([a[k], a[(k + 1) % 8], b[(k + 1) % 8], b[k]])
        for k in range(8):
            bm.faces.new([rings[-1][k], rings[-1][(k + 1) % 8], tip])
        bm.faces.new(list(reversed(rings[0])))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        parts.append(give(finish("Zahn%d" % s, bm, smooth=False), M["gem"]))
    return parts

# ---------------------------------------------------------------- Gold am Rumpf

def collar(tbvh, M):
    """Breiter Kragen um den Halsansatz, vorn tief (unter dem Kinn), hinten höher über den Rücken"""
    zf, zbk = R(1.285), R(1.45)
    N = 96; org, dirs = [], []
    for k in range(N):
        th = 2 * math.pi * k / N
        z = zf + (zbk - zf) * (1 - math.cos(th)) / 2
        org.append(Vector((0, 0.03, z))); dirs.append(Vector((math.sin(th), -math.cos(th), 0)))
    return hug_ring("Kragen", tbvh, org, dirs, 0.13, 0.05, M["gold"], gap=-0.006)

def belt(tbvh, M):
    N = 96; z = R(0.745)
    org = [Vector((0, 0.05, z))] * N
    dirs = [Vector((math.sin(2 * math.pi * k / N), -math.cos(2 * math.pi * k / N), 0)) for k in range(N)]
    return hug_ring("Guertel", tbvh, org, dirs, 0.11, 0.05, M["gold"], gap=-0.004)

def brief(bvh, M):
    """Goldener Schurz unter dem Gürtel: oben breit, nach unten rund zulaufend"""
    zt, zb = R(0.76), R(0.5)
    J, I = 14, 14
    bm = bmesh.new(); G = []
    for j in range(J + 1):
        v = j / J
        w = 0.38 * (1 - 0.45 * v) * math.sqrt(max(0.0, 1 - max(0.0, (v - 0.55) / 0.45) ** 2)) + 0.004
        row = []
        for i in range(I + 1):
            x = w * (2 * i / I - 1); z = zt + (zb - zt) * v
            p, n = front_hit(bvh, x, z)
            row.append(bm.verts.new(p + n * 0.014))
        G.append(row)
    for j in range(J):
        for i in range(I):
            bm.faces.new([G[j][i], G[j][i + 1], G[j + 1][i + 1], G[j + 1][i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = finish("Schurz", bm, smooth=True)
    md = o.modifiers.new("Dicke", 'SOLIDIFY'); md.thickness = 0.05; md.offset = 1.0; apply_mod(o, md)
    md = o.modifiers.new("Rund", 'BEVEL'); md.width = 0.016; md.segments = 4; md.limit_method = 'ANGLE'
    md.angle_limit = math.radians(35); apply_mod(o, md)
    smooth_obj(o, 40)
    return give(o, M["gold"])

def chest(tbvh, M):
    """Achteckiger Goldrahmen mit großem Smaragd auf der Brust"""
    zc = R(1.06)
    p, n = front_hit(tbvh, 0, zc)
    F = frame3((0, -1, 0))
    c = Vector((0, p.y, zc))
    fr = octa_frame("Brustrahmen", c, F, (0.27, 0.21, 0.085), (0.193, 0.148, 0.058), 0.055, -0.13, M["gold"], bevel=0.022)
    g = emerald_cut("Brustsmaragd", c + Vector((0, -0.03, 0)), F, 0.19, 0.145, 0.045, M["gem"])
    return [fr, g]

def pauldron(s, M):
    """Schulterpanzer: abgerundeter Block, oben außen eine breite Schräge (40°), darauf ein großer Smaragd"""
    hx, hy, hz, cx, cz = 0.205, 0.3, 0.225, 0.26, 0.26
    prof = [(-hx, -hz), (hx, -hz), (hx, hz - cz), (hx - cx, hz), (-hx, hz)]
    bm = bmesh.new()
    fr = [bm.verts.new((x, -hy, z)) for x, z in prof]
    bk = [bm.verts.new((x, hy, z)) for x, z in prof]
    bm.faces.new(fr); bm.faces.new(list(reversed(bk)))
    for k in range(5):
        k1 = (k + 1) % 5
        bm.faces.new([fr[k1], fr[k], bk[k], bk[k1]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = finish("Schulter%d" % s, bm, smooth=True)
    md = o.modifiers.new("Rund", 'BEVEL'); md.width = 0.065; md.segments = 5; md.limit_method = 'ANGLE'
    md.angle_limit = math.radians(25); apply_mod(o, md)
    if s < 0:
        o.data.transform(Matrix.Scale(-1, 4, (1, 0, 0)))
        o.data.flip_normals()
    rot = Matrix.Rotation(math.radians(10 * s), 4, 'Y')
    c = Vector((0.595 * s, 0.075, R(1.27)))
    o.data.transform(Matrix.Translation(c) @ rot)
    smooth_obj(o, 30); give(o, M["gold"])
    nl = rot.to_3x3() @ Vector((cz * s, 0, cx)).normalized()
    gp = c + rot.to_3x3() @ Vector(((hx - cx / 2) * s, 0, hz - cz / 2))
    up = rot.to_3x3() @ Vector((-cx * s, 0, cz)).normalized()
    return [o] + set_gem("SchulterSmaragd%d" % s, gp + nl * 0.006, nl, 0.175, 0.115, 0.048, M, up=up, rim=0.02)

def cuff(arm, side, s, M):
    """Breiter Armreif am Unterarm, außen eine Platte mit großem Smaragd"""
    el, wr = B(arm, side + "ForeArm"), B(arm, side + "Hand")
    d = (wr - el); L = d.length; d = d.normalized()
    c = el + d * L * 0.5
    ring = lathe_ring("Armreif" + side, c, d, 0.125, 0.215, L * 0.4, 0.038, M["gold"])
    out = Vector((s, -0.35, 0)); out = (out - d * out.dot(d)).normalized()
    pc = el + d * L * 0.6 + out * 0.22
    F = frame3(out, -d)
    plate = rbox("ArmPlatte" + side, pc, (0.115, 0.035, 0.125), 0.032, M["gold"], F.to_quaternion())
    gem = emerald_cut("ArmSmaragd" + side, pc + out * 0.03, F, 0.078, 0.088, 0.036, M["gem"])
    return [ring, plate, gem]

def shin_band(arm, side, s, M):
    kn, an = B(arm, side + "Leg"), B(arm, side + "Foot")
    d = (an - kn).normalized()
    return lathe_ring("Beinreif" + side, an - d * 0.02, d, 0.15, 0.22, 0.095, 0.035, M["gold"], ell=(1.0, 1.12))

def foot(s, M):
    """Runder Kuppelfuß mit flacher Sohle"""
    prof = []
    for k in range(13):
        a = math.radians(90 - 90 * k / 12)
        ca, sa = math.cos(a), math.sin(a)
        prof.append((abs(ca) ** (2 / 2.5), 0.16 + 0.84 * abs(sa) ** (2 / 2.5)))
    for k in range(1, 6):
        a = math.radians(90 * k / 5)
        prof.append((0.86 + 0.14 * math.cos(a), 0.16 - 0.16 * math.sin(a)))
    prof.append((0.0, 0.0))
    c = Vector((0.285 * s, -0.04, 0.0)); sx, sy, sz = 0.245, 0.31, 0.22
    bm = bmesh.new(); top = bm.verts.new(c + Vector((0, 0, sz))); bot = bm.verts.new(c)
    S = 48; rings = []
    for k in range(S):
        a = 2 * math.pi * k / S
        rings.append([bm.verts.new(c + Vector((math.cos(a) * r * sx, math.sin(a) * r * sy, z * sz))) for r, z in prof[1:-1]])
    m = len(rings[0])
    for k in range(S):
        A_, B_ = rings[k], rings[(k + 1) % S]
        bm.faces.new([top, A_[0], B_[0]])
        for j in range(m - 1):
            bm.faces.new([A_[j], A_[j + 1], B_[j + 1], B_[j]])
        bm.faces.new([A_[-1], bot, B_[-1]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = finish("Fuss%d" % s, bm, smooth=True)
    smooth_obj(o, 70)
    return give(o, M["skin"])

def golem_hand(name, side, k, mat):
    """Glatte, dicke Faust wie in der Vorlage: Handballen, vier wurstige, eingerollte Finger mit Furchen, Daumen
    (im Rahmen des Handknochens: Finger +Y, Daumen +X, Handfläche -Z auf der linken Seite)"""
    zs = 1.0 if side == "Left" else -1.0
    def P(x, y, z):
        return Vector((x * k, y * k, z * k * zs))
    fams = []
    def fam(nm):
        f = mb_family(name + nm); f.data.resolution = 0.008; fams.append(f)
        return f
    o = fam("Ballen")
    mb_ell(o, P(0, 0.0, 0.0), (0.07 * k, 0.05 * k, 0.05 * k))
    mb_ell(o, P(0, 0.08, -0.01), (0.088 * k, 0.085 * k, 0.056 * k))
    for i, x in enumerate((-0.064, -0.0215, 0.0215, 0.064)):     # jeder Finger eigene Familie: Furchen dazwischen
        f = fam("Finger%d" % i)
        r = (0.025 if i in (0, 3) else 0.027) * k
        a, b_, c = P(x, 0.14, -0.002), P(x * 1.03, 0.212, -0.04), P(x * 1.03, 0.212, -0.1)
        mb_caps(f, a, b_, r); mb_caps(f, b_, c, r * 0.96)
    f = fam("Daumen")
    t0, t1, t2 = P(0.065, 0.05, -0.025), P(0.1, 0.11, -0.06), P(0.06, 0.15, -0.092)
    mb_caps(f, t0, t1, 0.03 * k); mb_caps(f, t1, t2, 0.028 * k)
    h = join_parts([mb_to_mesh(f) for f in fams], name)
    remesh(h, 0.007)
    md = h.modifiers.new("Glatt", 'SMOOTH'); md.factor = 0.5; md.iterations = 2; apply_mod(h, md)
    md = h.modifiers.new("Weniger", 'DECIMATE'); md.ratio = 0.3; apply_mod(h, md)
    for pl in h.data.polygons:
        pl.use_smooth = True
    h.name = name
    return give(h, mat)

# ---------------------------------------------------------------- Variante

@variante("edelstein_golem", "koloss")
def edelsteingolem_neu(arm, body):
    remove_body(body)
    fix_elbows(arm)
    pose_hands(arm)
    M = golem_mats()
    body, tbvh = golem_body(arm)
    bind_golem(body, arm, tbvh)
    bvh = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())
    head = crown(M, bvh) + brows(bvh, M) + eyes(bvh, M) + mouth(bvh, M)
    spine = [collar(tbvh, M)] + chest(tbvh, M)
    hips = [belt(tbvh, M), brief(bvh, M)]
    hands = []
    for side, s in (("Left", 1), ("Right", -1)):
        for o in pauldron(s, M):            # Schulterpanzer gehen beim Ausholen halb mit dem Oberarm mit (wie im Angriffsbild)
            group_all(o, "mixamorig:%sShoulder" % side, 0.5); group_all(o, "mixamorig:%sArm" % side, 0.5)
            hands.append(o)
        for o in cuff(arm, side, s, M):
            attach(o, arm, "mixamorig:%sForeArm" % side)
        attach(shin_band(arm, side, s, M), arm, "mixamorig:%sLeg" % side)
        attach(foot(s, M), arm, "mixamorig:%sFoot" % side)
        h = golem_hand("Hand" + side, side, 1.85, M["skin"])
        h.matrix_world = arm.matrix_world @ arm.data.bones["mixamorig:%sHand" % side].matrix_local @ h.matrix_world
        bake_transform(h); group_all(h, "mixamorig:%sHand" % side)
        hands.append(h)
    bpy.ops.object.select_all(action='DESELECT')
    for o in hands:
        o.select_set(True)
    body.select_set(True); bpy.context.view_layer.objects.active = body
    body.data.materials.clear(); body.data.materials.append(M["skin"])
    bpy.ops.object.join()
    for o in head:
        attach(o, arm, "mixamorig:Head")
    for o in spine:
        attach(o, arm, "mixamorig:Spine2")
    for o in hips:
        attach(o, arm, "mixamorig:Hips")
    print("EDELSTEINGOLEM", sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH'), "Flächen")

if __name__ == "__main__":
    run(VAR, OUT)
