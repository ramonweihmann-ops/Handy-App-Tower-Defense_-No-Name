# Pilzriese neu (Entwurf v2 von ChatGPT, vom Nutzer freigegeben am 25.11.2026):
# Vorlage_Raw/Pilzriese_Neuentwurf_v2 (01_turnaround.png maßgeblich, 02_kopf_und_angriff.png, LIESMICH_CLAUDE.md).
# Schmaler, langbeiniger Zweibeiner aus weicher brauner Pilzhaut mit großem, schief sitzendem ockerfarbenem Hut
# (wenige breite Lamellen unten, Morchel und Bovist oben), großen angewachsenen Konsolenpilzen an Schultern, Rücken
# und Hüften, türkis leuchtenden Augen und wenigen türkisen Hautrissen, weit offenem Comicmaul (Zahnreihen mit
# Fangzähnen, Zahnfleisch, Zunge, dunkle Mundhöhle).
# Skelett und Bewegungen des Koloss; für die langen Beine der Vorlage werden die Unterschenkel verlängert und der
# Oberkörper verkleinert (Knochen behalten ihre Richtung, die Bewegungen bleiben dieselben, LIESMICH erlaubt
# angepasste Gelenkpositionen). Haut aus Metaballs (Bone Heat), Hut und Gesicht starr am Kopf.
# Aufruf: blender -b -P tools/monster/pilzriese.py -- pilz_riese <ziel.glb>
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edelsteingolem import *         # Metaballs, Ringe, Hilfen (frame3, sweep_loop, golem_hand, ...)
from fabrikmutter import cyl
import boss_aufsatz
boss_aufsatz.EXPORT_IMAGE_FORMAT = "JPEG"

STUFE = os.environ.get("STUFE", "voll")
LEG_PLUS = float(os.environ.get("LEG_PLUS", "0.5"))     # Unterschenkel länger (m, Ruhehaltung)
UPPER = float(os.environ.get("UPPER", "0.7"))           # Oberkörper (ab Hüfte) verkleinert
ARM_SPREAD = float(os.environ.get("ARM_SPREAD", "24"))  # Arme seitlich abgespreizt (Grad)
ATTACK_SPREAD = float(os.environ.get("ATTACK_SPREAD", "16"))
ATTACK_YAW = float(os.environ.get("ATTACK_YAW", "40"))
HEAD_BACK = float(os.environ.get("HEAD_BACK", "24"))     # Kopf mit Hut beim Ausholen in den Nacken (Grad)

# ---------------------------------------------------------------- Skelett anpassen

def toe_min(arm, act_name="Walk"):
    """Tiefster Punkt der Füße über den Gehzyklus (Ballen und Zehenspitzen)"""
    act = next(a for a in bpy.data.actions if a.name.startswith(act_name))
    ad = arm.animation_data; old = ad.action; ad.action = act
    arm.data.pose_position = 'POSE'
    lo = 9.0
    for f in range(int(act.frame_range[0]), int(act.frame_range[1]) + 1):
        bpy.context.scene.frame_set(f)
        for side in ("Left", "Right"):
            for b in ("Foot", "ToeBase"):
                pb = arm.pose.bones["mixamorig:%s%s" % (side, b)]
                lo = min(lo, (arm.matrix_world @ pb.tail).z)
    ad.action = old
    arm.data.pose_position = 'REST'
    bpy.context.scene.frame_set(0)
    return lo

def edit_bones(arm, fn):
    """fn(name, head, tail) -> (head, tail) für alle Knochen; Rollwinkel bleibt"""
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True); bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones
    old = {b.name: (b.head.copy(), b.tail.copy(), b.roll, b.use_connect) for b in eb}
    for b in eb:
        b.use_connect = False
    for b in eb:
        h, t, r, _ = old[b.name]
        h2, t2 = fn(b.name, h, t)
        b.head = h2; b.tail = t2; b.roll = r
    for b in eb:
        b.use_connect = old[b.name][3]
    bpy.ops.object.mode_set(mode='OBJECT')

def descendants(arm, root):
    out = set()
    def walk(b):
        out.add(b.name)
        for c in b.children:
            walk(c)
    walk(arm.data.bones[root])
    return out

def stretch_rig(arm, leg_plus, upper):
    """Unterschenkel entlang ihrer Richtung verlängern (Füße wandern mit), Oberkörper um die Hüfte verkleinern,
    dann alles anheben, bis die Füße im Gehzyklus wieder so tief reichen wie vorher"""
    base = toe_min(arm)
    feet = {s: descendants(arm, "mixamorig:%sFoot" % s) for s in ("Left", "Right")}
    up = descendants(arm, "mixamorig:Spine")
    P0 = arm.data.bones["mixamorig:Hips"].head_local.copy()
    legv, ank = {}, {}
    for s in ("Left", "Right"):
        lb = arm.data.bones["mixamorig:%sLeg" % s]
        L = (lb.tail_local - lb.head_local).length + leg_plus
        ank[s] = lb.head_local + Vector((0, 0, -L))           # Unterschenkel senkrecht (gerade, lange Beine)
        legv[s] = ank[s] - lb.tail_local
    def fn(name, h, t):
        for s in ("Left", "Right"):
            if name == "mixamorig:%sLeg" % s:
                return h, ank[s]
            if name in feet[s]:
                return h + legv[s], t + legv[s]
        if name in up:
            return P0 + (h - P0) * upper, P0 + (t - P0) * upper
        return h, t
    edit_bones(arm, fn)
    lift = base - toe_min(arm)
    edit_bones(arm, lambda n, h, t: (h + Vector((0, 0, lift)), t + Vector((0, 0, lift))))
    print("SKELETT Beine +%.2f, Oberkörper x%.2f, angehoben %.3f" % (leg_plus, upper, lift))
    return lift

def spread_arms(arm, deg, acts=("Walk", "Run", "Attack"), axis='Y', by_lift=False):
    """Oberarme in allen Bildern um deg Grad seitlich abspreizen (Vorlage: Arme hängen weit außen, Hände neben den
    Oberschenkeln); Unterarme und Hände folgen"""
    sc = bpy.context.scene; ad = arm.animation_data; saved = ad.action
    arm.data.pose_position = 'POSE'
    for act in [a for a in bpy.data.actions if a.name.startswith(acts)]:
        ad.action = act
        a0, a1 = int(act.frame_range[0]), int(act.frame_range[1])
        new = {"Left": [], "Right": []}
        lift = {}
        for f in range(a0, a1 + 1):
            sc.frame_set(f)
            sh = arm.pose.bones["mixamorig:LeftArm"].head.z
            lift[f] = max(0.0, max(arm.pose.bones["mixamorig:%sHand" % s_].head.z for s_ in ("Left", "Right")) - sh)
        top = max(lift.values()) or 1.0
        for f in range(a0, a1 + 1):
            sc.frame_set(f)
            w = smooth01(lift[f] / top) if by_lift else 1.0
            for side, sg in (("Left", 1), ("Right", -1)):
                ub = arm.pose.bones["mixamorig:%sArm" % side]
                ang = -deg * sg * w if axis == 'Y' else deg * sg * w
                R = Matrix.Rotation(math.radians(ang), 4, axis)
                head = ub.matrix.translation.copy()
                Mx = Matrix.Translation(head) @ R @ Matrix.Translation(-head) @ ub.matrix
                q = arm.convert_space(pose_bone=ub, matrix=Mx, from_space='POSE', to_space='LOCAL').to_quaternion()
                if new[side] and new[side][-1][1].dot(q) < 0:
                    q.negate()
                new[side].append((f, q))
        for side, keys in new.items():
            path = 'pose.bones["mixamorig:%sArm"].rotation_quaternion' % side
            for fc in [fc for fc in act.fcurves if fc.data_path == path]:
                act.fcurves.remove(fc)
            for i in range(4):
                fc = act.fcurves.new(path, index=i, action_group="mixamorig:%sArm" % side)
                fc.keyframe_points.add(len(keys))
                for kp, (f, q) in zip(fc.keyframe_points, keys):
                    kp.co = (f, q[i]); kp.interpolation = 'LINEAR'
                fc.update()
    ad.action = saved
    arm.data.pose_position = 'REST'
    bpy.context.view_layer.update()

# ---------------------------------------------------------------- Maße aus der Vorlage

SC = 0.0046                     # Meter je Bildpunkt der Vorlage (Schulterhöhe 355 px = 1,634 m in der Gehhaltung)
DZW = 0.113                     # Gehhaltung hebt den Oberkörper um so viel an

def V(px, py, sy=None):
    """Punkt aus der Vorderansicht (Bildpunkte) in die Ruhehaltung; sy = Bildpunkt in der Seitenansicht (Tiefe)"""
    y = 0.1 + (sy - 1297) * SC if sy is not None else 0.0
    return Vector(((px - 285) * SC, y, (665 - py) * SC - DZW))

HEAD_C2 = V(285, 212, 1242)
HEAD_S2 = (0.27, 0.235, 0.33)
MOUTH_Z = V(285, 212).z - 0.09        # Oberkante des Mauls wie in der Vorlage, das Maul hängt tief herab

def pilz_mats():
    def eye():
        n = 256; yy, xx = np.mgrid[0:n, 0:n]
        u = (xx + 0.5) / n * 2 - 1; v = (yy + 0.5) / n * 2 - 1
        r = np.sqrt(u * u + v * v); pu, pv = 0.22, 0.05
        rp = np.sqrt((u - pu) ** 2 + (v - pv) ** 2)
        col = np.zeros((n, n, 3), np.float32); col[:] = (0.25, 0.95, 0.95)
        g = smoothstep(0.8, 0.1, rp)[..., None]
        col = col * (1 - g) + np.asarray((0.75, 1.0, 1.0), np.float32) * g
        col = np.where((rp < 0.3)[..., None], np.asarray((0.02, 0.06, 0.08), np.float32), col)
        hl = np.sqrt((u - pu + 0.1) ** 2 + (v - pv - 0.1) ** 2) < 0.08
        col = np.where(hl[..., None], np.asarray((1.0, 1.0, 1.0), np.float32), col)
        col = np.where((r > 0.9)[..., None], np.asarray((0.03, 0.05, 0.05), np.float32), col)
        arr = np.ones((n, n, 4), np.float32); arr[..., :3] = col
        m = bpy.data.materials.new("Pilzauge"); m.use_nodes = True
        nt = m.node_tree; p = nt.nodes["Principled BSDF"]
        tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = new_image("Pilzauge_Bild", arr)
        nt.links.new(tex.outputs["Color"], p.inputs["Base Color"]); nt.links.new(tex.outputs["Color"], p.inputs["Emission Color"])
        p.inputs["Emission Strength"].default_value = 1.4; p.inputs["Roughness"].default_value = 0.15
        return m
    def morel():
        n = 256; rng = np.random.default_rng(4)
        pts = rng.random((60, 2))
        yy, xx = np.mgrid[0:n, 0:n] / n
        d1 = np.full((n, n), 9.0); d2 = np.full((n, n), 9.0)
        for px, py in pts:
            for ox in (-1, 0, 1):
                dx = np.abs(xx - px - ox); dy = np.abs(yy - py) * 1.6
                d = np.sqrt(dx * dx + dy * dy)
                d2 = np.minimum(d2, np.maximum(d1, d)); d1 = np.minimum(d1, d)
        edge = smoothstep(0.012, 0.035, d2 - d1)[..., None]
        col = np.asarray((0.62, 0.45, 0.3), np.float32) * (1 - edge) + np.asarray((0.17, 0.09, 0.05), np.float32) * edge
        arr = np.ones((n, n, 4), np.float32); arr[..., :3] = col
        m = bpy.data.materials.new("Morchel"); m.use_nodes = True
        nt = m.node_tree; p = nt.nodes["Principled BSDF"]
        tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = new_image("Morchel_Bild", arr)
        nt.links.new(tex.outputs["Color"], p.inputs["Base Color"]); p.inputs["Roughness"].default_value = 0.8
        return m
    return {
        "skin": look("Pilzhaut", (0.34, 0.22, 0.15), rough=0.72),
        "cap": look("Hutocker", (0.86, 0.47, 0.15), rough=0.5),
        "gill": look("Lamellen", (0.8, 0.62, 0.4), rough=0.75),
        "shelf": look("Konsolenpilz", (0.82, 0.5, 0.2), rough=0.5),
        "shelf2": look("Konsolenrand", (0.94, 0.8, 0.56), rough=0.6),
        "puff": look("Bovist", (0.95, 0.87, 0.72), rough=0.6),
        "stalk": look("Morchelstiel", (0.92, 0.86, 0.74), rough=0.7),
        "morel": morel(),
        "eye": eye(),
        "tooth": look("Pilzzahn", (0.96, 0.92, 0.8), rough=0.35),
        "gum": look("Zahnfleisch", (0.62, 0.3, 0.3), rough=0.55),
        "lip": look("Lippe", (0.27, 0.165, 0.125), rough=0.6),
        "tongue": look("Zunge", (0.93, 0.5, 0.52), rough=0.45),
        "throat": look("Mundhoehle", (0.12, 0.03, 0.04), rough=0.8),
        "crack": look("Hautriss", (0.25, 0.8, 0.75), rough=0.4, emit=(0.2, 0.85, 0.8), strength=0.8),
    }

# ---------------------------------------------------------------- Haut

def pilz_body(arm):
    T = mb_family("Rumpf")
    # Rumpf wie in der Vorlage (Rückmeldung 26.11.): breite Brust mit leichten Brustmuskeln, schlanker, flacher Bauch,
    # schmale Hüfte und schmales Gesäß – eine glatte Masse ohne Wülste
    mb_ell(T, V(282, 338, 1288), (0.31, 0.2, 0.17))                # Brust
    for s in (1, -1):
        pc = V(285 + 26 * s, 324); pc.y = -0.085
        mb_ell(T, tuple(pc), (0.125, 0.075, 0.09))                 # Brustmuskeln
    mb_ell(T, V(284, 388, 1282), (0.225, 0.17, 0.17))              # schlanker, flacher Bauch
    mb_ell(T, V(283, 424, 1296), (0.225, 0.16, 0.11))              # schmales Becken
    for side, s in (("Left", 1), ("Right", -1)):
        kn = B(arm, side + "Leg")
        mb_ell(T, (0.24 * s, kn.y + 0.01, kn.z + 0.03), (0.15, 0.15, 0.12))   # Hüfte läuft außen fließend in die Beine
    mb_ell(T, V(285, 298, 1280), (0.33, 0.2, 0.1))                 # Schultern
    mb_ell(T, V(285, 282, 1245), (0.21, 0.19, 0.12))               # kurzer Hals
    mb_ell(T, HEAD_C2, HEAD_S2)                                    # Kopf
    mb_ell(T, V(285, 256, 1222), (0.285, 0.22, 0.175))             # breiter, tiefer Kiefer (Maul hängt tief)
    for s in (1, -1):
        bc = V(285 + 25 * s, 178); bc.y = -0.35
        mb_ell(T, tuple(bc), (0.09, 0.06, 0.042), Quaternion((0, 1, 0), math.radians(-24 * s)))  # schwerer Brauenwulst, innen tief (V: böse, Kommentar 26.11.)
    fb = V(285, 184); fb.y = -0.36
    mb_ell(T, tuple(fb), (0.03, 0.04, 0.035))                      # Stirnfalte zwischen den Brauen
    nz = V(285, 204); nz.y = -0.39
    mb_ell(T, tuple(nz), (0.048, 0.042, 0.035))                    # kleine breite Nase
    parts = []
    for side, s in (("Left", 1), ("Right", -1)):
        A_ = mb_family("Arm" + side)
        sh, el, wr = B(arm, side + "Arm"), B(arm, side + "ForeArm"), B(arm, side + "Hand")
        mb_ell(A_, tuple(sh), (0.15, 0.15, 0.15))
        mb_caps(A_, sh, el, 0.125)
        mb_caps(A_, el, wr, 0.13)
        c, semi, q = along(el, wr, 0.145, 0.16, 0.55); mb_ell(A_, c, semi, q)
        parts.append(A_)
        # Bein und Fuß wie in der Vorlage (Rückmeldung 26.11.) in einem Guss: oben an der Hüfte schlank, ein kleines
        # Knie, nach unten dicker und fließend in den breiten Fuß; die Beine stehen leicht nach außen, zwischen Beinen
        # und Füßen bleibt ein Abstand (die Haut wuchs unten zusammen)
        L_ = mb_family("Bein" + side)
        up, kn, an = B(arm, side + "UpLeg"), B(arm, side + "Leg"), B(arm, side + "Foot")
        hip = Vector((0.25 * s, kn.y + 0.01, kn.z - 0.03))         # Maße aus der Vorderansicht: Innenkanten senkrecht,
        knee = Vector((0.27 * s, kn.y - 0.01, 0.57))               # außen wird das Bein nach unten breiter
        ank = Vector((0.31 * s, an.y - 0.01, 0.29))
        mb_caps(L_, hip, knee, 0.155)
        mb_ell(L_, tuple(knee + Vector((0.012 * s, -0.135, 0.03))), (0.06, 0.05, 0.06))     # kleines Knie
        mb_caps(L_, knee, ank, 0.178)
        mb_ell(L_, tuple(ank), (0.205, 0.215, 0.19))               # zum Fuß hin dicker
        fc = Vector((0.375 * s, an.y - 0.11, 0.1))
        mb_ell(L_, tuple(fc), (0.275, 0.3, 0.13))                  # breiter Fuß
        for k, x in enumerate((-0.18, -0.062, 0.062, 0.18)):
            mb_ell(L_, tuple(fc + Vector((x * 1.05, -0.27 + abs(x) * 0.4, -0.035))), (0.066, 0.085, 0.072))
        parts.append(L_)
    torso = mb_to_mesh(T)
    tbvh = BVHTree.FromObject(torso, bpy.context.evaluated_depsgraph_get())
    body = join_parts([torso] + [mb_to_mesh(o) for o in parts], "Pilzriese")
    remesh(body, 0.012)
    cut = mouth_cutter(tbvh)
    md = body.modifiers.new("Maul", 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = cut; md.solver = 'EXACT'
    apply_mod(body, md)
    bpy.data.objects.remove(cut, do_unlink=True)
    remesh(body, 0.01)
    md = body.modifiers.new("Glatt", 'SMOOTH'); md.factor = 0.5; md.iterations = 4; apply_mod(body, md)
    md = body.modifiers.new("Weniger", 'DECIMATE'); md.ratio = 0.25; apply_mod(body, md)
    for p in body.data.polygons:
        p.use_smooth = True
    return body, tbvh

MOUTH_A, MOUTH_BU, MOUTH_BL = 0.255, 0.085, 0.19

def mouth_sec(t):
    """Querschnitt des Maulraums: t=0 an der Öffnung, 1 ganz hinten (enger)"""
    k = math.sqrt(max(0.0, 1 - t ** 2.2)) * 0.75 + 0.25 * (1 - t)
    return MOUTH_A * k, MOUTH_BU * (0.95 * k + 0.05), MOUTH_BL * k

def mouth_front(tbvh):
    return front_hit(tbvh, 0, MOUTH_Z)[0].y

def mouth_cutter(tbvh):
    yf = mouth_front(tbvh)
    bm = bmesh.new(); S = 56; rings = []
    ys = [yf - 0.3] + [yf + 0.02 + 0.2 * k / 12 for k in range(13)]
    for i, y in enumerate(ys):
        t = 0.0 if i == 0 else (y - yf - 0.02) / 0.2
        a, bu, bl = mouth_sec(t)
        ring = []
        for k in range(S):
            th = 2 * math.pi * k / S; c, sn = math.cos(th), math.sin(th)
            x = a * math.copysign(abs(c) ** (2 / 2.6), c)
            z = (bu * math.copysign(abs(sn) ** (2 / 4.0), sn)) if sn > 0 else (bl * math.copysign(abs(sn) ** (2 / 1.9), sn))
            ring.append(bm.verts.new((x, y, MOUTH_Z + z)))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(S):
            bm.faces.new([r0[k], r0[(k + 1) % S], r1[(k + 1) % S], r1[k]])
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finish("Maulschnitt", bm)

def paint_throat(body, tbvh, M):
    """Flächen im Maulraum dunkel färben (Rachen)"""
    yf = mouth_front(tbvh)
    body.data.materials.append(M["throat"]); idx = len(body.data.materials) - 1
    for p in body.data.polygons:
        c = p.center
        if c.y < yf + 0.01 or c.y > yf + 0.25:
            continue
        a, bu, bl = mouth_sec(min(0.92, max(0.0, (c.y - yf) / 0.22)))
        dz = c.z - MOUTH_Z
        b = bu if dz > 0 else bl
        if (abs(c.x) / (a * 0.98)) ** 2.6 + (abs(dz) / (b * 0.98)) ** 2.6 < 1.0 and p.material_index == 0:
            p.material_index = idx

def bind_pilz(body, arm, tbvh):
    keep = {"mixamorig:" + b for b in MAIN_BONES}
    saved = {b.name: b.use_deform for b in arm.data.bones}
    for b in arm.data.bones:
        b.use_deform = b.name in keep
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    for b in arm.data.bones:
        b.use_deform = saved[b.name]
    # Rumpf gleichmäßig nach der Höhe auf Becken und Wirbel verteilen: Bone Heat allein faltete den Bauch beim Gehen
    # (Kommentar 26.11.: wirkte wie ein schwabbelnder Fettleib)
    torso_weights(body, tbvh, bones=[(b, B(arm, b).z) for b in ("Hips", "Spine", "Spine1", "Spine2")],
                  zmin=B(arm, "LeftLeg").z + 0.05, zmax=B(arm, "Neck").z + 0.02)   # Kopf und Kiefer bleiben am Kopfknochen
    # (ohne Obergrenze hing die Gesichtshaut am Rumpf und riss beim Ausholen vom Kopf ab, Kommentar 26.11.)
    head = body.vertex_groups.get("mixamorig:Head") or body.vertex_groups.new(name="mixamorig:Head")
    for v in body.data.vertices:
        q = v.co - HEAD_C2
        d = math.sqrt((q.x / 0.3) ** 2 + (q.y / 0.27) ** 2 + (q.z / 0.36) ** 2)
        h = smooth01((1.15 - d) / 0.25) * smooth01((v.co.z - (HEAD_C2.z - 0.36)) / 0.08)
        if h <= 0:
            continue
        for g in v.groups:
            g.weight *= (1 - h)
        head.add([v.index], h, 'ADD')

# ---------------------------------------------------------------- Hut

CAP_C = V(292, 158, 1355)       # Mitte des Huts (liegt hinter dem Kopf)
CAP_R = 0.86
CAP_N = Vector((0.2, float(os.environ.get("CAP_BACK", "0.38")), 0.9)).normalized()   # Hut vorn hochgeschwungen (Rückmeldung
# 26.11.: wie in der Vorlage, man sieht von vorn die Lamellen und von oben das Gesicht), kippt nach links hinten ...
CAP_DROOP = Vector((0.88, 0.47, 0)).normalized()   # ... und die weiche Krempe hängt dorthin herab, gegenüber hochgeschlagen

def cap_frame():
    n = CAP_N; u = Vector((1, 0, 0)); u = (u - n * u.dot(n)).normalized(); v = n.cross(u)
    return u, v, n

def cap_profile():
    """(r, z) einmal herum: Kuppel oben, runder dicker Rand, flache Unterseite"""
    pts = []
    for k in range(10):
        r = 0.78 * k / 9
        pts.append((r, 0.3 - 0.2 * (r / 0.78) ** 2))
    for k in range(1, 12):
        a = math.radians(90 - 180 * k / 11)
        pts.append((0.78 + 0.1 * math.cos(a), 0.0 + 0.1 * math.sin(a)))
    for k in range(1, 10):
        r = 0.78 - 0.76 * k / 9
        pts.append((r, -0.1 + 0.05 * (1 - r / 0.78)))
    return pts

def cap(M, head_top):
    """Großer schiefer Hut, sitzt fest auf dem Scheitel"""
    u, v, n = cap_frame()
    prof = cap_profile()
    S = 96
    def build(C):
        bm = bmesh.new(); rings = []
        for k in range(S):
            a = 2 * math.pi * k / S; d = u * math.cos(a) + v * math.sin(a)
            rings.append([bm.verts.new(C + d * r * CAP_R / 0.87 + n * z * 1.0) if r > 1e-4 else None for r, z in prof])
        top = bm.verts.new(C + n * prof[0][1]); bot = bm.verts.new(C + n * prof[-1][1])
        dd = (CAP_DROOP - n * CAP_DROOP.dot(n)).normalized()
        for ring in rings:
            for vv in ring:
                if vv is None:
                    continue
                q = vv.co - C; a_ = q.dot(u); b_ = q.dot(v)
                rr = math.sqrt(a_ * a_ + b_ * b_) / CAP_R
                cd = (a_ * u + b_ * v).normalized().dot(dd) if rr > 1e-4 else 0.0
                vv.co += n * (-0.2 * rr ** 2 * max(0.0, cd) ** 1.3 + 0.22 * rr ** 2 * max(0.0, -cd) ** 1.3)
        m = len(prof)
        under = [z < -0.02 and i > 12 for i, (r, z) in enumerate(prof)]
        for k in range(S):
            A_, B_ = rings[k], rings[(k + 1) % S]
            bm.faces.new([top, A_[1], B_[1]])
            for j in range(1, m - 1):
                f = bm.faces.new([A_[j], A_[j + 1], B_[j + 1], B_[j]])
                f.material_index = 1 if (under[j] and under[j + 1]) else 0
            f = bm.faces.new([A_[m - 1], bot, B_[m - 1]]); f.material_index = 1
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return bm
    C = CAP_C.copy()
    o = finish("Hut", build(C), smooth=True)
    hb = BVHTree.FromObject(o, bpy.context.evaluated_depsgraph_get())
    h = hb.ray_cast(head_top + Vector((0, 0, -1.0)), Vector((0, 0, 1)), 3.0)
    shift = (head_top.z - 0.09) - h[0].z if h[0] is not None else 0.0
    o.data.transform(Matrix.Translation((0, 0, shift)))
    smooth_obj(o, 60); give_idx(o, M["cap"], M["gill"])
    C = C + Vector((0, 0, shift))
    hb = BVHTree.FromObject(o, bpy.context.evaluated_depsgraph_get())
    parts = [o]
    # breite Lamellen: dicke runde Leisten unter dem Hut, strahlenförmig vom Scheitel zum Rand
    root = head_top + Vector((0, 0, 0.03))
    for k in range(16):
        a = 2 * math.pi * (k + 0.5) / 16
        d = u * math.cos(a) + v * math.sin(a)
        pts, rad = [], []
        for j in range(13):
            t = j / 12
            # Zielpunkt am Rand, Linie vom Scheitel dorthin, auf die Unterseite gelegt
            rim = C + d * CAP_R * 0.86
            q = root.lerp(rim, 0.42 + 0.56 * t)
            hit = hb.ray_cast(q + n * -0.6, n, 1.2)
            if hit[0] is None:
                continue
            pts.append(hit[0] - n * 0.02)
            rad.append(0.034 * math.sqrt(max(0.0, math.sin(math.pi * min(1.0, 0.02 + t * 0.96)))) + 0.004)
        if len(pts) > 3:
            rad[0] = rad[-1] = 0.0
            g = tube("Lamelle%d" % k, pts, rad, segs=10)
            smooth_obj(g, 70); parts.append(give(g, M["gill"]))
    # Morchel und Bovist oben auf dem Hut
    def on_top(px, sy):
        p = V(px, 100, sy); h = hb.ray_cast(Vector((p.x, p.y, 5.0)), Vector((0, 0, -1)), 9.0)
        return h[0], (h[1] if h[1].z > 0 else -h[1])
    mp, mn = on_top(322, 1330)
    stem = cyl("Morchelstiel", mp - mn * 0.03, mp + mn * 0.07, 0.055, M["stalk"], segs=16)
    parts.append(stem)
    prof = [(0.0, 0.0), (0.1, 0.0), (0.105, 0.05), (0.1, 0.12), (0.085, 0.19), (0.06, 0.25), (0.03, 0.29), (0.0, 0.305)]
    F = frame3(mn, (0, 1, 0))
    bm = bmesh.new(); rings = []
    base = mp + mn * 0.06
    for k in range(32):
        a = 2 * math.pi * k / 32
        rings.append([bm.verts.new(base + F @ Vector((math.cos(a) * r, 0, math.sin(a) * r)) + mn * z) for r, z in prof[1:-1]])
    top = bm.verts.new(base + mn * prof[-1][1]); bot = bm.verts.new(base)
    for k in range(32):
        A_, B_ = rings[k], rings[(k + 1) % 32]
        bm.faces.new([bot, B_[0], A_[0]])
        for j in range(len(A_) - 1):
            bm.faces.new([A_[j], B_[j], B_[j + 1], A_[j + 1]])
        bm.faces.new([A_[-1], B_[-1], top])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mo = finish("Morchel", bm, smooth=True)
    me = mo.data; me.uv_layers.new(name="UVMap"); uvl = me.uv_layers.active.data
    for poly in me.polygons:
        for li in poly.loop_indices:
            q = me.vertices[me.loops[li].vertex_index].co - base
            ang = math.atan2(q.dot(F @ Vector((0, 0, 1))), q.dot(F @ Vector((1, 0, 0))))
            uvl[li].uv = ((ang / (2 * math.pi)) % 1.0, q.dot(mn) / 0.31)
    parts.append(give(mo, M["morel"]))
    pp, pn = on_top(372, 1418)
    parts.append(give(sphere("Bovist", tuple(pp + pn * 0.095), 0.125, (1.0, 1.0, 0.92), segs=(28, 16)), M["puff"]))
    return parts

# ---------------------------------------------------------------- Gesicht

def pilz_eyes(bvh, M):
    out = []
    for s in (1, -1):
        p, n = front_hit(bvh, V(285 + 27 * s, 192).x, V(285, 192).z)
        nn = (n + Vector((0, -1, 0))).normalized()
        inner = Vector((-s, 0, 0)); inner = (inner - nn * inner.dot(nn)).normalized()
        up = nn.cross(inner).normalized()
        if up.z < 0:
            up = -up
        a, dd, b = 0.06, 0.026, 0.037
        e = sphere("Auge%d" % s, (0, 0, 0), 1.0, (1, 1, 1), segs=(32, 16))
        cen = p + nn * 0.0
        Fm = Matrix((inner * a, nn * dd, up * b)).transposed().to_4x4(); Fm.translation = cen
        e.data.transform(Fm)
        me = e.data; me.uv_layers.new(name="UVMap"); uvl = me.uv_layers.active.data
        for poly in me.polygons:
            for li in poly.loop_indices:
                q = me.vertices[me.loops[li].vertex_index].co - cen
                uvl[li].uv = (0.5 + 0.5 * q.dot(inner) / a, 0.5 + 0.5 * q.dot(up) / b)
        out.append(give(e, M["eye"]))
        # Lidwulst aus Haut über der oberen Augenhälfte, innen tiefer gezogen: böser Blick wie in der Vorlage
        lid = sphere("Lid%d" % s, (0, 0, 0), 1.0, (1, 1, 1), segs=(28, 14))
        lx = (inner - up * math.tan(math.radians(30))).normalized()   # innen tiefer, auf beiden Seiten gleich (vorher
        lz = (up + inner * math.tan(math.radians(30))).normalized()   # war eine Seite gespiegelt und wirkte müde)
        Fl = Matrix((lx * a * 1.25, nn * 0.03, lz * b * 0.85)).transposed().to_4x4()
        Fl.translation = cen + up * b * 0.95 + inner * a * 0.1 + nn * 0.008
        lid.data.transform(Fl)
        out.append(give(lid, M["skin"]))
    return out

def pilz_mouth(tbvh, M):
    """Weit offenes Comicmaul: oben Zahnfleisch mit vier breiten Schneidezähnen und zwei langen Fangzähnen,
    unten vier kleine Zähne und zwei Fangzähne nach oben, große rosa Zunge, dunkler Rachen"""
    yf = mouth_front(tbvh); zc = MOUTH_Z
    parts = []
    def edge_z(x, top):
        a = MOUTH_A; u = min(1.0, abs(x) / a)
        return zc + (MOUTH_BU * (1 - u ** 2.6) ** 0.35 if top else -MOUTH_BL * (1 - u ** 1.9) ** 0.53)
    # braune Lippe rund um die ganze Maulöffnung (Rückmeldung 26.11.: Lippe endete an den Fangzähnen und war zu rosa):
    # geschlossener Wulst auf der Haut, die Zähne sitzen dahinter im Maul
    loop = []
    for k in range(40):
        x = MOUTH_A * 0.97 * math.cos(math.pi * k / 40)
        loop.append((x, edge_z(x, True)))
    for k in range(40):
        x = -MOUTH_A * 0.97 * math.cos(math.pi * k / 40)
        loop.append((x, edge_z(x, False)))
    lp, ln = [], []
    for x, z in loop:
        h, n = front_hit(tbvh, x * 1.02, zc + (z - zc) * 1.03)
        lp.append(h); ln.append(n)
    # durchgängiger Wulst ohne Knicke und Lücken (Kommentar 26.11.): Schleife glätten, gleichmäßig verteilen, überall
    # gleich weit aus der Haut heben; der Querschnitt richtet sich nach der Hautnormalen (verdreht sich nicht)
    for _ in range(6):
        lp = [(lp[k - 1] + lp[k] * 2 + lp[(k + 1) % len(lp)]) / 4 for k in range(len(lp))]
        ln = [(ln[k - 1] + ln[k] * 2 + ln[(k + 1) % len(ln)]).normalized() for k in range(len(ln))]
    seg = [(lp[(k + 1) % len(lp)] - lp[k]).length for k in range(len(lp))]
    total = sum(seg); pts2, nrm2 = [], []
    for j in range(96):
        d = total * j / 96; k = 0
        while d > seg[k]:
            d -= seg[k]; k += 1
        t = d / seg[k]
        pts2.append(lp[k].lerp(lp[(k + 1) % len(lp)], t)); nrm2.append(ln[k].lerp(ln[(k + 1) % len(ln)], t).normalized())
    lip = loop_ring("Lippe", [q + n * 0.009 for q, n in zip(pts2, nrm2)], nrm2, 0.019, segs=12)
    smooth_obj(lip, 70); parts.append(give(lip, M["lip"]))
    TY = yf + 0.07                                   # Zahnreihen deutlich hinter der Lippe
    for nm, top in (("Oben", True), ("Unten", False)):
        pts = []
        for k in range(17):
            x = -0.2 + 0.4 * k / 16
            z = edge_z(x, top) + (-0.004 if top else 0.004)
            pts.append(Vector((x, TY + 0.012, z)))
        rr = [0.016 * math.sqrt(max(0.0, math.sin(math.pi * k / (len(pts) - 1)))) for k in range(len(pts))]
        g = tube("Zahnfleisch" + nm, pts, rr, segs=12)
        smooth_obj(g, 70); parts.append(give(g, M["gum"]))
    def tooth(name, x, top, length, w, fang):
        sg = -1 if top else 1
        if fang:                                     # Fangzahn wächst hinter der Lippe aus dem Zahnfleisch, ganz im Maul
            z0 = edge_z(x, top) + (-0.004 if top else 0.004)
            base = Vector((x, TY, z0))
            inward = -0.01 if x > 0 else 0.01
            pts = [base + Vector((0, 0.004, -sg * 0.014)), base, base + Vector((inward * 0.5, -0.004, sg * length * 0.55)), base + Vector((inward, -0.002, sg * length))]
            o = tube(name, pts, [w * 1.05, w, w * 0.7, 0.0], segs=14)
            smooth_obj(o, 60)
            return give(o, M["tooth"])
        z0 = edge_z(x, top) + (-0.022 if top else 0.022)
        base = Vector((x, TY, z0))
        o = rbox(name, base + Vector((0, 0, sg * length * 0.5)), (w, w * 0.6, length * 0.5), w * 0.75, M["tooth"])
        smooth_obj(o, 60)
        return give(o, M["tooth"])
    for k, x in enumerate((-0.09, -0.03, 0.03, 0.09)):
        parts.append(tooth("ZahnOben%d" % k, x, True, 0.05, 0.027, False))
    for s_ in (1, -1):
        parts.append(tooth("FangOben%d" % s_, 0.15 * s_, True, 0.1, 0.031, True))       # klar innerhalb der Maulecken
        parts.append(tooth("FangUnten%d" % s_, 0.128 * s_, False, 0.088, 0.03, True))
    for k, x in enumerate((-0.072, -0.024, 0.024, 0.072)):
        parts.append(tooth("ZahnUnten%d" % k, x, False, 0.04, 0.023, False))
    parts.append(give(sphere("Zunge", tuple(Vector((0, yf + 0.13, zc - 0.11))), 1.0, (0.16, 0.12, 0.06), segs=(28, 14)), M["tongue"]))
    return parts

def cracks(bvh, M):
    """Wenige feine türkise Hautrisse (Brust, Arme, Bein), gezackt auf der Haut"""
    out = []
    rng = random.Random(7)
    for nm, px, py, length, ang in (("Brust", 315, 318, 0.2, -70), ("ArmL", 120, 345, 0.16, -60), ("ArmR", 445, 345, 0.15, -110),
                                     ("Bein", 302, 505, 0.18, -80)):
        p0 = V(px, py)
        pts = []
        d = Vector((math.cos(math.radians(ang)), 0, math.sin(math.radians(ang))))
        for k in range(7):
            q = p0 + d * length * k / 6 + Vector((rng.uniform(-0.018, 0.018), 0, 0))
            p, n = front_hit(bvh, q.x, q.z)
            pts.append(p + n * 0.003)
        o = tube("Riss" + nm, pts, [0.0] + [0.006] * (len(pts) - 2) + [0.0], segs=6)
        out.append(give(o, M["crack"]))
    return out

# ---------------------------------------------------------------- Konsolenpilze

def shelf(name, base, out, up, w, d, t, M):
    """Großer angewachsener Konsolenpilz (Brötchenform): oben goldbraun, heller Rand und Unterseite,
    breiter Ansatz im Körper (base), ragt in Richtung out heraus"""
    out = Vector(out).normalized(); up = Vector(up); up = (up - out * up.dot(out)).normalized(); side = up.cross(out)
    c = base + out * d * 0.55
    bm = bmesh.new(); S, J = 40, 12
    rings = []
    for k in range(S):
        a = 2 * math.pi * k / S
        dirv = out * math.cos(a) * d + side * math.sin(a) * w
        ring = []
        for j in range(J + 1):
            th = math.pi * j / J                        # 0 oben ... pi unten
            r = math.sin(th); z = math.cos(th)
            zz = t * (z if z > 0 else z * 0.6)
            ring.append(bm.verts.new(c + dirv * r + up * zz))
        rings.append(ring)
    for k in range(S):
        A_, B_ = rings[k], rings[(k + 1) % S]
        for j in range(J):
            f = bm.faces.new([A_[j], A_[j + 1], B_[j + 1], B_[j]])
            f.material_index = 0 if j < J * 0.42 else 1
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = finish(name, bm, smooth=True)
    give_idx(o, M["shelf"], M["shelf2"])
    smooth_obj(o, 70)
    return o

def shelves(bvh, arm, M):
    """Schultern, oberer Rücken, Hüften vorn und hinten (wie im Turnaround)"""
    out = []
    def surf(p, d):
        h = bvh.ray_cast(p - Vector(d) * 1.5, Vector(d), 3.0)
        return h[0] if h[0] is not None else p
    for s, nm in ((1, "Links"), (-1, "Rechts")):
        sh = B(arm, ("Left" if s > 0 else "Right") + "Arm")
        top = surf(Vector((sh.x * 0.95, sh.y + 0.02, sh.z + 0.5)), (0, 0, -1))
        o = shelf("SchulterPilz" + nm, top + Vector((-0.08 * s, 0, -0.06)), (s, -0.05, 0.12), (0, 0, 1), 0.24, 0.32, 0.13, M)
        group_all(o, "mixamorig:%sShoulder" % ("Left" if s > 0 else "Right"), 0.6)
        group_all(o, "mixamorig:%sArm" % ("Left" if s > 0 else "Right"), 0.4)
        out.append(o)
    spots = (("Ruecken", V(285, 312), (0, 1, 0.35), 0.36, 0.34, 0.16, "Spine2"),
             ("HuefteVorn", V(325, 400), (0.5, -1, 0.45), 0.12, 0.16, 0.085, "Hips"),
             ("SchenkelVorn", V(218, 445), (-0.6, -1, 0.4), 0.125, 0.16, 0.085, "Hips"),
             ("HuefteHinten", V(1880 - 1790 + 285, 395), (0.6, 1, 0.4), 0.14, 0.17, 0.085, "Hips"),
             ("SchenkelHinten", V(285 - (1915 - 1880), 435), (-0.3, 1, 0.4), 0.11, 0.15, 0.08, "Hips"))
    for nm, p, d, w, dd, t, bone in spots:
        dv = Vector(d).normalized()
        flat = Vector((dv.x, dv.y, 0)).normalized()
        base = surf(Vector((p.x, 0.1, p.z)) + flat * 0.0, -flat) - flat * 0.04
        o = shelf("Konsole" + nm, base, dv, (0, 0, 1) if dv.z < 0.2 else (Vector((0, 0, 1)) - flat * 0.5), w, dd, t, M)
        group_all(o, "mixamorig:" + bone)
        out.append(o)
    return out

def head_back(arm, deg, act_name="Attack"):
    """Beim Hochreißen der Arme den Kopf (mit Hut) in den Nacken legen, je nach Höhe der Hände"""
    sc = bpy.context.scene; ad = arm.animation_data; saved = ad.action
    arm.data.pose_position = 'POSE'
    act = next(a for a in bpy.data.actions if a.name.startswith(act_name))
    ad.action = act
    a0, a1 = int(act.frame_range[0]), int(act.frame_range[1])
    lift = []
    for f in range(a0, a1 + 1):
        sc.frame_set(f)
        sh = arm.pose.bones["mixamorig:LeftArm"].head.z
        hz = max(arm.pose.bones["mixamorig:%sHand" % s].head.z for s in ("Left", "Right"))
        lift.append(max(0.0, hz - sh))
    top = max(lift) or 1.0
    keys = []
    for i, f in enumerate(range(a0, a1 + 1)):
        sc.frame_set(f)
        hb = arm.pose.bones["mixamorig:Head"]
        th = math.radians(-deg * smooth01(lift[i] / top))
        R = Matrix.Rotation(th, 4, 'X')
        head = hb.matrix.translation.copy()
        Mx = Matrix.Translation(head) @ R @ Matrix.Translation(-head) @ hb.matrix
        q = arm.convert_space(pose_bone=hb, matrix=Mx, from_space='POSE', to_space='LOCAL').to_quaternion()
        if keys and keys[-1][1].dot(q) < 0:
            q.negate()
        keys.append((f, q))
    path = 'pose.bones["mixamorig:Head"].rotation_quaternion'
    for fc in [fc for fc in act.fcurves if fc.data_path == path]:
        act.fcurves.remove(fc)
    for i in range(4):
        fc = act.fcurves.new(path, index=i, action_group="mixamorig:Head")
        fc.keyframe_points.add(len(keys))
        for kp, (f, q) in zip(fc.keyframe_points, keys):
            kp.co = (f, q[i]); kp.interpolation = 'LINEAR'
        fc.update()
    ad.action = saved
    arm.data.pose_position = 'REST'
    bpy.context.view_layer.update()

def hat_clearance(arm, hands, hat_objs, margin=0.04, acts=("Attack", "Walk", "Run")):
    """Hände dürfen den Hut nie treffen: je Bild Handpunkte in den Ruherahmen des Kopfes holen und gegen den Hut
    prüfen (Punkt unter der Hutunterseite + Abstand); sonst den Oberarm schrittweise absenken (um die Querachse)"""
    from mathutils.bvhtree import BVHTree as BT
    dg = bpy.context.evaluated_depsgraph_get()
    hb = BT.FromObject(hat_objs[0], dg)
    hbone = arm.data.bones["mixamorig:Head"]
    sc = bpy.context.scene; ad = arm.animation_data; saved = ad.action
    arm.data.pose_position = 'POSE'
    pts = {}
    for side, h in hands.items():
        vs = [v.co.copy() for v in h.data.vertices]
        pts[side] = vs[::4]
    def hits(side):
        hbn = arm.data.bones["mixamorig:%sHand" % side]
        pbn = arm.pose.bones["mixamorig:%sHand" % side]
        Mh = arm.matrix_world @ pbn.matrix @ hbn.matrix_local.inverted()
        ph = arm.pose.bones["mixamorig:Head"]
        to_rest = (arm.matrix_world @ hbone.matrix_local) @ (arm.matrix_world @ ph.matrix).inverted()
        worst = 0.0
        for p in pts[side]:
            q = to_rest @ (Mh @ p)
            e = q - HEAD_C2
            if (e.x / 0.33) ** 2 + (e.y / 0.3) ** 2 + (e.z / 0.38) ** 2 < 1.0:            # im Kopf: nach außen
                return -1.0
            up = hb.ray_cast(q, Vector((0, 0, 1)), 3.0)
            dn = hb.ray_cast(q, Vector((0, 0, -1)), 3.0)
            if up[0] is not None and up[1].z > 0:                 # im Hut
                worst = max(worst, 0.2)
            elif dn[0] is not None and dn[1].z > 0:               # über dem Hut (durchgestoßen)
                worst = max(worst, 0.3)
            elif up[0] is not None and (up[0] - q).length < margin:
                worst = max(worst, margin - (up[0] - q).length)
        return worst
    changed = 0
    for act in [a for a in bpy.data.actions if a.name.startswith(acts)]:
        ad.action = act
        a0, a1 = int(act.frame_range[0]), int(act.frame_range[1])
        new = {"Left": [], "Right": []}
        for f in range(a0, a1 + 1):
            sc.frame_set(f)
            for side in ("Left", "Right"):
                ub = arm.pose.bones["mixamorig:%sArm" % side]
                orig = ub.matrix.copy()
                k = 0
                sg = 1 if side == "Left" else -1
                while k < 24:
                    hcode = hits(side)
                    if hcode == 0:
                        break
                    if hcode < 0:                                   # Kopf: Oberarm zur Seite hin drehen
                        d = (ub.tail - ub.head).normalized()
                        ax = d.cross(Vector((sg, 0, 0)))
                        R = Matrix.Rotation(math.radians(4), 4, ax.normalized() if ax.length > 1e-3 else Vector((0, 1, 0)))
                    else:                                           # Hut: Oberarm absenken
                        d = (ub.tail - ub.head).normalized()
                        ax = d.cross(Vector((0, 0, 1)))
                        if ax.length < 1e-3:
                            ax = Vector((1, 0, 0))
                        R = Matrix.Rotation(math.radians(-4), 4, ax.normalized())
                    head = ub.matrix.translation.copy()
                    ub.matrix = Matrix.Translation(head) @ R @ Matrix.Translation(-head) @ ub.matrix
                    bpy.context.view_layer.update()
                    k += 1
                changed += k > 0
                q = arm.convert_space(pose_bone=ub, matrix=ub.matrix, from_space='POSE', to_space='LOCAL').to_quaternion()
                if new[side] and new[side][-1][1].dot(q) < 0:
                    q.negate()
                new[side].append((f, q))
                ub.matrix = orig
        for side, keys in new.items():
            path = 'pose.bones["mixamorig:%sArm"].rotation_quaternion' % side
            for fc in [fc for fc in act.fcurves if fc.data_path == path]:
                act.fcurves.remove(fc)
            for i in range(4):
                fc = act.fcurves.new(path, index=i, action_group="mixamorig:%sArm" % side)
                fc.keyframe_points.add(len(keys))
                for kp, (f, q) in zip(fc.keyframe_points, keys):
                    kp.co = (f, q[i]); kp.interpolation = 'LINEAR'
                fc.update()
    ad.action = saved
    arm.data.pose_position = 'REST'
    bpy.context.view_layer.update()
    print("HUTABSTAND angepasst in", changed, "Bildern")

# ---------------------------------------------------------------- Variante

@variante("pilz_riese", "koloss")
def pilzriese_neu(arm, body):
    remove_body(body)
    stretch_rig(arm, LEG_PLUS, UPPER)
    spread_arms(arm, ARM_SPREAD)
    spread_arms(arm, ATTACK_SPREAD, acts=("Attack",))      # beim Ausholen V-förmig neben den Hut (Angriffsbild)
    spread_arms(arm, ATTACK_YAW, acts=("Attack",), axis='Z', by_lift=True)   # Fäuste seitlich am Kopf vorbei
    head_back(arm, HEAD_BACK)
    fix_elbows(arm, inward=0.0)
    pose_hands(arm)
    M = pilz_mats()
    body, tbvh = pilz_body(arm)
    bind_pilz(body, arm, tbvh)
    bvh = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())
    ht = bvh.ray_cast(Vector((HEAD_C2.x, HEAD_C2.y, 5.0)), Vector((0, 0, -1)), 9.0)[0]
    head = cap(M, ht) + pilz_eyes(tbvh, M) + pilz_mouth(tbvh, M)
    skin_parts = cracks(bvh, M)
    for o in skin_parts:
        group_all(o, "insel_naechst")
    shelf_parts = shelves(bvh, arm, M)
    hands = list(shelf_parts) + skin_parts
    for side, s in (("Left", 1), ("Right", -1)):
        h = golem_hand("Hand" + side, side, 2.1, M["skin"])
        h.matrix_world = arm.matrix_world @ arm.data.bones["mixamorig:%sHand" % side].matrix_local @ h.matrix_world
        bake_transform(h); group_all(h, "mixamorig:%sHand" % side)
        hands.append(h)
    hat_clearance(arm, {"Left": hands[-2], "Right": hands[-1]}, head)
    bpy.ops.object.select_all(action='DESELECT')
    for o in hands:
        o.select_set(True)
    body.select_set(True); bpy.context.view_layer.objects.active = body
    body.data.materials.clear(); body.data.materials.append(M["skin"])
    bpy.ops.object.join()
    copy_nearest_weights(body, "insel_naechst")
    paint_throat(body, tbvh, M)
    for o in head:
        attach(o, arm, "mixamorig:Head")
    print("PILZRIESE", sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH'), "Flächen")

if __name__ == "__main__":
    run(VAR, OUT)
