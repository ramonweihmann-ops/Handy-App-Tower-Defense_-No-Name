# Fabrikmutter neu (Entwurf „Ofenbrutstätte“ von ChatGPT, vom Nutzer freigegeben am 25.11.2026):
# Vorlage_Raw/Fabrikmutter_Neuentwurf_v2 (01_turnaround.png, 02_maul_und_federbot.png, LIESMICH_CLAUDE.md).
# Knuffiger, breiter Ofenkörper auf zwei kurzen Ketten: dunkler blaugrauer Stahl mit runden Kanten, zwei Schornsteine mit
# gelben Manschetten, gelbe Rohre über die Schultern, böses Gesicht aus schweren Brauenplatten, rot glühenden Augen,
# Blockzähnen und glühendem Ofenmaul hinter einem Gitter, seitliche Kolben, darunter eine eigene Bot-Ausgabe mit Rampe.
# Seiten: Manometer, Lüftungsgitter, Warnstreifen; hinten Doppeltür und Lüftungen. Skelett und Bewegungen der
# Schleimmutter (Body/Top); Quetschen und Kippen stark gedämpft, damit das Metall nicht wie Gummi wirkt.
# Aufruf: blender -b -P tools/monster/fabrikmutter.py -- fabrik_mutter <ziel.glb>
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monster_aufsatz import *
from mathutils import Quaternion
from mathutils.bvhtree import BVHTree
import boss_aufsatz
boss_aufsatz.EXPORT_IMAGE_FORMAT = "JPEG"

K_SCALE = 0.5        # gebaut in Entwurfsmaßen (Höhe 1,3), danach auf die Größe des Schleimmutter-Skeletts gebracht

# ---------------------------------------------------------------- Grundformen

def smooth_obj(o, angle=40):
    for p in o.data.polygons:
        p.use_smooth = True
    o.data.use_auto_smooth = True
    o.data.auto_smooth_angle = math.radians(angle)
    return o

def rbox(name, c, half, r, mat, rot=None, segs=3):
    """Quader mit runden Kanten (Mitte c, halbe Maße half, Kantenradius r, Drehung rot als Quaternion)"""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * half[0], v.co.y * half[1], v.co.z * half[2]))
    o = finish(name, bm, smooth=True)
    md = o.modifiers.new("Rund", 'BEVEL'); md.width = min(r, min(half) * 0.95); md.segments = segs; md.limit_method = 'NONE'
    apply_mod(o, md)
    if rot is not None:
        o.data.transform(rot.to_matrix().to_4x4())
    o.data.transform(Matrix.Translation(Vector(c)))
    smooth_obj(o)
    return give(o, mat)

def apply_mod(o, mod):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier=mod.name)

def cyl(name, p0, p1, r, mat, segs=32, r1=None):
    """Zylinder (oder Kegelstumpf) von p0 nach p1, beide Enden geschlossen"""
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=r, radius2=r if r1 is None else r1, depth=d.length)
    o = finish(name, bm, smooth=True)
    q = Vector((0, 0, 1)).rotation_difference(d.normalized())
    o.data.transform(q.to_matrix().to_4x4())
    o.data.transform(Matrix.Translation((p0 + p1) / 2))
    smooth_obj(o, 50)
    return give(o, mat)

def ring(name, c, axis, R, r, mat, segs=40):
    t = torus(name, (0, 0, 0), R, r, rot=(0, 0, 0), segs=segs)
    q = Vector((0, 0, 1)).rotation_difference(Vector(axis).normalized())
    t.data.transform(q.to_matrix().to_4x4()); t.data.transform(Matrix.Translation(Vector(c)))
    return give(t, mat)

def ball(name, c, r, mat, squash=(1, 1, 1)):
    return give(sphere(name, tuple(c), r, squash, segs=(24, 14)), mat)

def frame_at(p, n, up_hint=(0, 0, 1)):
    """Rahmen auf der Oberfläche: Normale n, „oben“ möglichst nach up_hint, „rechts“ quer dazu"""
    n = Vector(n).normalized(); up = Vector(up_hint); up = (up - n * up.dot(n)).normalized(); rt = n.cross(up)
    return Matrix((rt, n, up)).transposed().to_quaternion()            # lokales x = rechts, y = Normale (nach außen), z = oben

def planar_uv(o, c, ax_u, ax_v, su, sv):
    """Flache Abwicklung: uv = 0.5 + (p - c)·ax / (2 s)"""
    me = o.data
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uvl = me.uv_layers.active.data
    for poly in me.polygons:
        for li in poly.loop_indices:
            p = me.vertices[me.loops[li].vertex_index].co
            q = p - Vector(c)
            uvl[li].uv = (0.5 + q.dot(Vector(ax_u)) / (2 * su), 0.5 + q.dot(Vector(ax_v)) / (2 * sv))
    return o

def image_mat(name, arr, rough=0.4, metal=0.0, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = new_image(name + "_Bild", arr)
    nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough; p.inputs["Metallic"].default_value = metal
    if emit > 0:
        nt.links.new(tex.outputs["Color"], p.inputs["Emission Color"]); p.inputs["Emission Strength"].default_value = emit
    return m

# ---------------------------------------------------------------- Bilder

def radial_image(cols, n=256, center=(0.5, 0.5)):
    """Kreisverlauf: cols = [(r, (r,g,b)), …] von innen nach außen"""
    y, x = np.mgrid[0:n, 0:n]
    r = np.sqrt(((x + 0.5) / n - center[0]) ** 2 + ((y + 0.5) / n - center[1]) ** 2) * 2
    rs = [c[0] for c in cols]; out = np.ones((n, n, 4), np.float32)
    for ch in range(3):
        out[..., ch] = np.interp(r, rs, [c[1][ch] for c in cols])
    return out

def hazard_image(n=256, m=64, stripes=6.0, yellow=(0.98, 0.72, 0.1), dark=(0.06, 0.06, 0.07)):
    y, x = np.mgrid[0:m, 0:n]
    k = (((x + 0.5) / n * stripes + (y + 0.5) / m * (stripes * m / n)) % 1.0) < 0.5
    out = np.ones((m, n, 4), np.float32)
    out[..., :3] = np.where(k[..., None], np.asarray(yellow, np.float32), np.asarray(dark, np.float32))
    return out

def ramp_image(n=256):
    """Rampe: dunkle Riffelbleche, am unteren Ende gelb-schwarze Warnstreifen"""
    y, x = np.mgrid[0:n, 0:n]
    u, v = (x + 0.5) / n, (y + 0.5) / n
    rib = (np.sin(v * 2 * np.pi * 7) > 0.55)
    col = np.where(rib[..., None], np.asarray((0.36, 0.37, 0.41), np.float32), np.asarray((0.2, 0.21, 0.24), np.float32))
    haz = (((u * 5 + v * 5) % 1.0) < 0.5)
    hz = np.where(haz[..., None], np.asarray((0.98, 0.72, 0.1), np.float32), np.asarray((0.06, 0.06, 0.07), np.float32))
    col = np.where((v < 0.3)[..., None], hz, col)
    out = np.ones((n, n, 4), np.float32); out[..., :3] = col
    return out

def gauge_image(n=256):
    y, x = np.mgrid[0:n, 0:n]
    u, v = (x + 0.5) / n * 2 - 1, (y + 0.5) / n * 2 - 1
    r = np.sqrt(u * u + v * v); a = np.arctan2(v, u)
    col = np.zeros((n, n, 3), np.float32) + np.asarray((0.95, 0.93, 0.84), np.float32)
    ticks = (r > 0.68) & (r < 0.86) & ((np.degrees(a) % 30) < 4) & (v > -0.45)
    col[ticks] = (0.12, 0.12, 0.14)
    nd = np.asarray((math.cos(math.radians(35)), math.sin(math.radians(35))))          # Zeiger nach rechts oben
    t = u * nd[0] + v * nd[1]; d = np.abs(-u * nd[1] + v * nd[0])
    needle = (t > -0.08) & (t < 0.75) & (d < 0.045 * (1 - np.clip(t, 0, 1) * 0.7))
    col[needle] = (0.85, 0.12, 0.08)
    col[r < 0.1] = (0.15, 0.15, 0.17)
    col[r > 0.95] = (0.2, 0.2, 0.22)
    out = np.ones((n, n, 4), np.float32); out[..., :3] = col
    return out

# ---------------------------------------------------------------- Ofenkörper

Z0, Z1, ZT = 0.2, 1.1, 0.95
E_SHELL = 3.2

def shell_dims(z):
    t = (z - Z0) / (Z1 - Z0)
    hw = 0.56 - 0.22 * t; df = 0.48 - 0.22 * t; db = 0.43 - 0.08 * t
    if z > ZT:                                                       # runde Oberkante
        k = math.sqrt(max(0.0, 1 - ((z - ZT) / (Z1 - ZT)) ** 2))
        f = 0.3 + 0.7 * k ** 0.8
        hw, df, db = hw * f, df * f, db * f
    if z < Z0 + 0.04:                                                # leicht eingezogene Unterkante
        f = 0.94 + 0.06 * (z - Z0) / 0.04
        hw, df, db = hw * f, df * f, db * f
    return hw, df, db

def shell_pt(z, th):
    hw, df, db = shell_dims(z)
    c, s = math.cos(th), math.sin(th)
    return Vector((hw * math.copysign(abs(c) ** (2 / E_SHELL), c), (db if s > 0 else df) * math.copysign(abs(s) ** (2 / E_SHELL), s), z))

def shell_normal(z, th):
    a = shell_pt(z, th + 0.01) - shell_pt(z, th - 0.01)
    b = shell_pt(min(z + 0.01, Z1 - 0.001), th) - shell_pt(max(z - 0.01, Z0), th)
    n = a.cross(b).normalized()
    p = shell_pt(z, th)
    if n.dot(Vector((p.x, p.y, 0))) < 0:
        n = -n
    return n

def shell(mat):
    S = 72
    zs = [Z0 + (Z1 - Z0) * t for t in np.concatenate([np.linspace(0, 0.8, 28), 0.8 + 0.2 * np.sin(np.linspace(0, 1, 14)[1:] * np.pi / 2)])]
    bm = bmesh.new(); rings = []
    for z in zs:
        rings.append([bm.verts.new(shell_pt(z, -math.pi / 2 + k * 2 * math.pi / S)) for k in range(S)])
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(S):
            bm.faces.new([r0[k], r0[(k + 1) % S], r1[(k + 1) % S], r1[k]])
    top = bm.verts.new((0, sum(v.co.y for v in rings[-1]) / S, Z1 + 0.004))
    for k in range(S):
        bm.faces.new([rings[-1][k], rings[-1][(k + 1) % S], top])
    bm.faces.new(list(reversed(rings[0])))
    o = finish("Ofenkoerper", bm)
    smooth_obj(o, 35)
    return give(o, mat)

def front_y(z, x=0.0):
    """y der Vorderseite bei Höhe z und seitlichem Versatz x (Superellipse)"""
    hw, df, db = shell_dims(z)
    q = max(0.0, 1 - abs(x / hw) ** E_SHELL)
    return -df * q ** (1 / E_SHELL)

def cut(body, cutter):
    md = body.modifiers.new("Schnitt", 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = cutter; md.solver = 'EXACT'
    apply_mod(body, md)
    bpy.data.objects.remove(cutter, do_unlink=True)

def strip(name, z0, z1, th0, th1, off, thick, mat, n=24, uv_scale=1.0):
    """Blechstreifen um den unteren Körper (Kotflügel, Warnstreifen) mit Abwicklung entlang des Umfangs"""
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
    ths = np.linspace(th0, th1, n); rows = []
    for z in (z0, z1):
        outer = []; inner = []
        for th in ths:
            p = shell_pt(z, th); nn = shell_normal(z, th); nn = Vector((nn.x, nn.y, 0)).normalized()
            outer.append(bm.verts.new(p + nn * (off + thick))); inner.append(bm.verts.new(p + nn * (off - 0.01)))
        rows.append((outer, inner))
    L = 0.0; us = [0.0]
    for a_, b_ in zip(ths, ths[1:]):
        L += (shell_pt(z0, b_) - shell_pt(z0, a_)).length; us.append(L)
    us = [u_ / (z1 - z0) * uv_scale for u_ in us]

    def quad(vs, uvs):
        f = bm.faces.new(vs)
        for lp, uv in zip(f.loops, uvs):
            lp[uvl].uv = uv
    (o0, i0), (o1, i1) = rows
    for k in range(n - 1):
        quad([o0[k], o0[k + 1], o1[k + 1], o1[k]], [(us[k] / 4, 0), (us[k + 1] / 4, 0), (us[k + 1] / 4, 1), (us[k] / 4, 1)])
        quad([i0[k + 1], i0[k], i1[k], i1[k + 1]], [(0, 0)] * 4)
        quad([o1[k], o1[k + 1], i1[k + 1], i1[k]], [(0.01, 0.99)] * 4)
        quad([i0[k], i0[k + 1], o0[k + 1], o0[k]], [(0.01, 0.01)] * 4)
    quad([o0[0], o1[0], i1[0], i0[0]], [(0.01, 0.5)] * 4)
    quad([o0[-1], i0[-1], i1[-1], o1[-1]], [(0.01, 0.5)] * 4)
    o = finish(name, bm)
    o.data.uv_layers[0].name = "UVMap"
    md = o.modifiers.new("Rund", 'BEVEL'); md.width = 0.008; md.segments = 2; md.limit_method = 'ANGLE'
    apply_mod(o, md)
    smooth_obj(o, 35)
    return give(o, mat)

# ---------------------------------------------------------------- Bauteile

def track(name, s, M):
    """Kurze Kette: Gummiband mit Stollen um zwei große Räder, Radkappen außen"""
    parts = []
    cx, L, R = 0.45 * s, 0.56, 0.11
    outline = []
    for k in range(64):
        t = k / 64
        per = 2 * L + 2 * math.pi * R; d = t * per
        if d < L:
            y, z = -L / 2 + d, 0.0
        elif d < L + math.pi * R:
            a = (d - L) / R; y, z = L / 2 + R * math.sin(a), R - R * math.cos(a)
        elif d < 2 * L + math.pi * R:
            y, z = L / 2 - (d - L - math.pi * R), 2 * R
        else:
            a = (d - 2 * L - math.pi * R) / R; y, z = -L / 2 - R * math.sin(a), R + R * math.cos(a)
        outline.append((y, z))
    w = 0.1
    bm = bmesh.new()
    vo = [bm.verts.new((cx - w, y, z)) for y, z in outline]; vi = [bm.verts.new((cx + w, y, z)) for y, z in outline]
    n = len(outline)
    for k in range(n):
        bm.faces.new([vo[k], vo[(k + 1) % n], vi[(k + 1) % n], vi[k]])
    bm.faces.new(list(reversed(vo))); bm.faces.new(vi)
    band = finish(name + "Band", bm); smooth_obj(band, 30); give(band, M["rubber"])
    md = band.modifiers.new("Rund", 'BEVEL'); md.width = 0.015; md.segments = 2; md.limit_method = 'ANGLE'; apply_mod(band, md)
    parts.append(band)
    for k in range(0, 64, 3):                                        # Stollen
        y, z = outline[k]; y2, z2 = outline[(k + 1) % 64]
        nrm = Vector((0, -(z2 - z), (y2 - y))).normalized()
        if nrm.dot(Vector((0, y, z - R))) < 0:
            nrm = -nrm
        c = Vector((cx, y, z)) + nrm * 0.008
        # Drehung nur um die Querachse: rotation_difference ist für die Unterseite (genau entgegengesetzt) mehrdeutig
        # und drehte die unteren Stollen um 90 Grad, sie ragten vorn als Stab heraus (Kommentar 26.11.)
        q = Quaternion((1, 0, 0), math.atan2(-nrm.y, nrm.z))
        parts.append(rbox(name + "Stollen%d" % k, c, (w * 1.02, 0.012, 0.012), 0.005, M["rubber"], q, segs=1))
    for y in (-L / 2, L / 2):
        parts.append(cyl(name + "Rad%d" % int(y * 100), (cx + s * (w - 0.01), y, R), (cx + s * (w + 0.014), y, R), 0.088, M["steel"]))
        parts.append(cyl(name + "Kappe%d" % int(y * 100), (cx + s * (w + 0.01), y, R), (cx + s * (w + 0.026), y, R), 0.06, M["steel_l"]))
        parts.append(ball(name + "Nabe%d" % int(y * 100), (cx + s * (w + 0.024), y, R), 0.022, M["steel"], (0.5, 1, 1)))
    return parts

def vent(name, c, rot, w, h, M, slots=3):
    """Lüftungsgitter: heller Rahmen, dunkle Schlitze"""
    parts = [rbox(name + "Rahmen", c, (w, 0.022, h), 0.02, M["steel_l"], rot)]
    for i in range(slots):
        zz = h * 0.62 * (1 - 2 * i / max(slots - 1, 1))
        off = rot @ Vector((0, 0.018, zz))
        parts.append(rbox(name + "Schlitz%d" % i, Vector(c) + off, (w * 0.8, 0.012, h * 0.2), 0.008, M["black"], rot, segs=2))
    return parts

def rivet(name, p, n, M, r=0.016):
    return ball(name, Vector(p) + Vector(n).normalized() * r * 0.3, r, M["steel_l"])

def fabrik_mats():
    return {
        "steel": look("Ofenstahl", (0.25, 0.27, 0.32), rough=0.3, metal=0.55),
        "steel_l": look("Hellstahl", (0.5, 0.52, 0.56), rough=0.28, metal=0.6),
        "yellow": look("Industriegelb", (0.98, 0.7, 0.1), rough=0.3, metal=0.1),
        "black": look("Schwarz", (0.03, 0.03, 0.035), rough=0.7),
        "rubber": look("Gummi", (0.1, 0.1, 0.11), rough=0.75),
        "soot": look("Russ", (0.07, 0.07, 0.08), rough=0.85),
        "white": look("Zifferblatt", (0.95, 0.93, 0.84), rough=0.3),
        "eye": image_mat("Ofenauge", radial_image([(0.0, (1.0, 0.95, 0.55)), (0.35, (1.0, 0.55, 0.12)), (0.7, (0.95, 0.12, 0.05)),
                                                   (1.0, (0.55, 0.03, 0.02))], center=(0.45, 0.42)), rough=0.2, emit=3.0),
        "fire": image_mat("Ofenglut", radial_image([(0.0, (1.0, 0.92, 0.45)), (0.4, (1.0, 0.62, 0.12)), (0.8, (0.95, 0.28, 0.05)),
                                                    (1.0, (0.6, 0.08, 0.02))]), rough=0.5, emit=3.2),
        "hazard": image_mat("Warnstreifen", hazard_image(), rough=0.35),
        "ramp": image_mat("Rampe", ramp_image(), rough=0.4, metal=0.3),
        "gauge": image_mat("Manometer", gauge_image(), rough=0.25),
    }

# ---------------------------------------------------------------- Zusammenbau

def build_fabrikmutter():
    M = fabrik_mats()
    body = shell(M["steel"])
    zm, zb = 0.575, 0.3
    # Vertiefungen: Ofenmaul, Bot-Ausgabe, Augenhöhlen
    cut(body, rbox("SchnittMaul", (0, front_y(zm) + 0.02, zm), (0.21, 0.15, 0.105), 0.07, M["black"]))
    cut(body, rbox("SchnittBucht", (0, front_y(zb) + 0.03, zb), (0.165, 0.2, 0.083), 0.03, M["black"]))
    for s in (1, -1):
        cut(body, ball("SchnittAuge", (0.14 * s, front_y(0.77, 0.14) + 0.035, 0.77), 0.098, M["black"]))
    parts = [body]
    # Ofenglut hinter dem Gitter
    yf = front_y(zm)
    glow = ball("Ofenglut", (0, yf + 0.13, zm), 1.0, M["fire"], (0.21, 0.05, 0.11))
    planar_uv(glow, (0, 0, zm), (1, 0, 0), (0, 0, 1), 0.21, 0.11); give(glow, M["fire"])
    parts.append(glow)
    for i, x in enumerate((-0.14, -0.047, 0.047, 0.14)):
        parts.append(give(tube("Gitterstab%d" % i, [(x, yf + 0.05, zm + 0.11), (x * 1.04, yf - 0.012, zm + 0.04), (x * 1.04, yf - 0.012, zm - 0.04),
                                                     (x, yf + 0.05, zm - 0.11)], [0.014] * 4, segs=12), M["steel"]))
    parts.append(cyl("Gitterquer", (-0.205, yf + 0.0, zm), (0.205, yf + 0.0, zm), 0.015, M["steel"]))
    for i, x in enumerate((-0.17, -0.085, 0.0, 0.085, 0.17)):        # Blockzähne oben und unten
        tilt = Quaternion((0, 1, 0), math.radians(6 if i % 2 else -5)) @ Quaternion((1, 0, 0), math.radians(-13))
        parts.append(rbox("ZahnOben%d" % i, (x, front_y(zm + 0.1, x) - 0.01, zm + 0.1), (0.039, 0.034, 0.033), 0.013, M["steel_l"], tilt))
        tilt = Quaternion((0, 1, 0), math.radians(-5 if i % 2 else 6)) @ Quaternion((1, 0, 0), math.radians(-13))
        parts.append(rbox("ZahnUnten%d" % i, (x, front_y(zm - 0.1, x) - 0.01, zm - 0.1), (0.036, 0.032, 0.028), 0.012, M["steel_l"], tilt))
    # Augen und schwere Brauenplatten (innen tiefer: böser Blick)
    for s in (1, -1):
        c = Vector((0.14 * s, front_y(0.77, 0.14) + 0.02, 0.77))
        parts.append(ball("Auge%d" % s, c, 0.082, M["eye"], (1.0, 0.75, 0.95)))
        planar_uv(parts[-1], c, (1, 0, 0), (0, 0, 1), 0.082, 0.078)
        q = Quaternion((0, 0, 1), math.radians(-12 * s)) @ Quaternion((0, 1, 0), math.radians(-24 * s)) @ Quaternion((1, 0, 0), math.radians(-14))
        bc = Vector((0.15 * s, front_y(0.88, 0.15) - 0.03, 0.88))
        parts.append(rbox("Braue%d" % s, bc, (0.155, 0.06, 0.058), 0.024, M["steel_l"], q))
        for k, dx in enumerate((-0.07, 0.07)):
            rp = bc + q @ Vector((dx, -0.05, 0.0))
            parts.append(rivet("BrauenNiete%d%d" % (s, k), rp, q @ Vector((0, -1, 0)), M, 0.017))
    # seitliche Kolben am Maul
    for s in (1, -1):
        x = 0.3 * s
        P = lambda z: Vector((x, front_y(z, x) - 0.045, z))
        parts.append(ball("KolbenKugelOben%d" % s, P(0.74), 0.042, M["steel"]))
        parts.append(cyl("KolbenStange%d" % s, P(0.74), P(0.63), 0.017, M["steel_l"]))
        parts.append(cyl("Kolben%d" % s, P(0.64), P(0.49), 0.052, M["yellow"]))
        for zz in (0.632, 0.498):
            parts.append(cyl("KolbenRing%d%d" % (s, int(zz * 1000)), P(zz + 0.008), P(zz - 0.008), 0.055, M["steel"]))
        parts.append(cyl("KolbenStangeU%d" % s, P(0.49), P(0.41), 0.017, M["steel_l"]))
        parts.append(ball("KolbenKugelUnten%d" % s, P(0.4), 0.045, M["steel"]))
    # Bot-Ausgabe mit Rahmen und Rampe
    yb = front_y(zb)
    parts.append(rbox("BuchtRueckwand", (0, yb + 0.17, zb), (0.17, 0.012, 0.09), 0.01, M["black"]))
    fr = Quaternion((1, 0, 0), math.radians(-13))
    for name, c, h in (("RahmenOben", (0, yb - 0.008, zb + 0.1), (0.205, 0.03, 0.022)), ("RahmenUnten", (0, yb - 0.004, zb - 0.095), (0.205, 0.03, 0.02)),
                       ("RahmenL", (0.19, yb - 0.006, zb), (0.022, 0.03, 0.1)), ("RahmenR", (-0.19, yb - 0.006, zb), (0.022, 0.03, 0.1))):
        parts.append(rbox("Bucht" + name, c, h, 0.012, M["steel_l"], fr))
    for sx in (1, -1):
        for sz in (1, -1):
            parts.append(rivet("BuchtNiete%d%d" % (sx, sz), (0.19 * sx, yb - 0.04, zb + 0.105 * sz), (0, -1, 0.2), M, 0.014))
    r0 = Vector((0, yb - 0.02, zb - 0.095)); r1 = Vector((0, yb - 0.3, 0.014))
    d = (r1 - r0); q = Vector((0, -1, 0)).rotation_difference(d.normalized())
    ramp = rbox("Rampe", (r0 + r1) / 2, (0.15, d.length / 2, 0.014), 0.008, M["ramp"], q)
    planar_uv(ramp, (r0 + r1) / 2, (1, 0, 0), -d.normalized(), 0.15, d.length / 2)
    parts.append(ramp)
    for sx in (1, -1):
        rail = rbox("RampenRand%d" % sx, (r0 + r1) / 2 + Vector((0.155 * sx, 0, 0.012)), (0.014, d.length / 2, 0.022), 0.008, M["hazard"], q)
        planar_uv(rail, (r0 + r1) / 2, (0, 1, 0), (0, 0, 1), 0.1, 0.1)
        parts.append(rail)
    # Schornsteine mit gelben Manschetten und Ruß oben
    for s in (1, -1):
        b = Vector((0.15 * s, 0.03, 0.98))
        parts.append(cyl("Schornstein%d" % s, b, b + Vector((0, 0, 0.27)), 0.085, M["steel"]))
        parts.append(cyl("SchornsteinKopf%d" % s, b + Vector((0, 0, 0.24)), b + Vector((0, 0, 0.31)), 0.103, M["soot"]))
        parts.append(cyl("SchornsteinLoch%d" % s, b + Vector((0, 0, 0.29)), b + Vector((0, 0, 0.312)), 0.078, M["black"]))
        parts.append(cyl("Manschette%d" % s, b + Vector((0, 0, 0.06)), b + Vector((0, 0, 0.13)), 0.104, M["yellow"]))
    # gelbe Rohre über die Schultern, mit Schellen, fest am Körper
    for s in (1, -1):
        pts = []
        for th_deg, z in ((14, 1.085), (16, 1.05), (22, 0.98), (28, 0.88), (33, 0.76), (36, 0.64)):
            th = math.radians(th_deg) if s > 0 else math.pi - math.radians(th_deg)
            pts.append(shell_pt(z, th) + shell_normal(z, th) * 0.06)
        pts[0] = pts[0] + Vector((0, 0, -0.02))
        pipe = give(tube("Rohr%d" % s, [tuple(p_) for p_ in pts], [0.055] * len(pts), segs=20), M["yellow"])
        sub = pipe.modifiers.new("Glatt", 'SUBSURF'); sub.levels = 2; apply_mod(pipe, sub); smooth_obj(pipe, 60)
        parts.append(pipe)
        for t_ in (2, 4):
            a_, b_ = pts[t_], pts[t_ + 1]
            parts.append(ring("Schelle%d%d" % (s, t_), a_.lerp(b_, 0.3), b_ - a_, 0.058, 0.014, M["steel"]))
        parts.append(cyl("RohrSockel%d" % s, pts[-1] + (pts[-1] - pts[-2]).normalized() * -0.01, pts[-1] + (pts[-1] - pts[-2]).normalized() * 0.05,
                         0.068, M["steel"]))
    # Kotflügel (gelb) an den Ecken, Warnstreifen an den Seiten, Nieten
    for (a, b) in ((-160, -112), (-68, -20), (20, 66), (114, 160)):
        parts.append(strip("Kotfluegel%d" % a, 0.2, 0.37, math.radians(a), math.radians(b), 0.008, 0.035, M["yellow"], n=16))
        for k, tt in enumerate((0.3, 0.7)):
            th = math.radians(a + (b - a) * tt)
            p = shell_pt(0.3, th); nn = shell_normal(0.3, th)
            parts.append(rivet("KotNiete%d%d" % (a, k), p + nn * 0.045, nn, M, 0.016))
    for (a, b) in ((-21, 21), (159, 201)):
        parts.append(strip("Warnband%d" % a, 0.215, 0.345, math.radians(a), math.radians(b), 0.008, 0.024, M["hazard"], n=20, uv_scale=1.0))
    # Seiten: Manometer, Lüftung
    for s in (1, -1):
        th = 0.0 if s > 0 else math.pi
        p = shell_pt(0.64, th); nn = shell_normal(0.64, th)
        q = Vector((0, 0, 1)).rotation_difference(nn)
        parts.append(cyl("Manometer%d" % s, p - nn * 0.01, p + nn * 0.03, 0.09, M["gauge"]))
        planar_uv(parts[-1], p, (q @ Vector((1, 0, 0))), (q @ Vector((0, 1, 0))), 0.09, 0.09)
        parts.append(ring("ManometerRing%d" % s, p + nn * 0.03, nn, 0.093, 0.019, M["yellow"]))
        for k in range(4):
            a = k * math.pi / 2 + math.pi / 4
            rp = p + nn * 0.036 + (q @ Vector((math.cos(a), math.sin(a), 0))) * 0.093
            parts.append(rivet("ManoNiete%d%d" % (s, k), rp, nn, M, 0.011))
        p = shell_pt(0.43, th); nn = shell_normal(0.43, th)
        parts += vent("Seitenlueftung%d" % s, p + nn * 0.005, frame_at(p, nn), 0.15, 0.075, M)
    # hinten: Doppeltür und zwei Lüftungen
    bvh = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())
    for s in (1, -1):                                                # große Doppeltür mit erhabenem Rahmen
        hit = bvh.ray_cast(Vector((0.135 * s, 2.0, 0.53)), Vector((0, -1, 0)), 4.0)
        p, nn = hit[0], Vector((0, 1, 0)).lerp(hit[1], 0.5).normalized()
        q = frame_at(p, nn)
        parts.append(rbox("TuerRahmen%d" % s, p + nn * 0.004, (0.132, 0.016, 0.205), 0.02, M["steel_l"], q))
        parts.append(rbox("Tuer%d" % s, p + nn * 0.012, (0.118, 0.016, 0.19), 0.018, M["steel"], q))
        for zz in (-0.12, 0.12):
            parts.append(rbox("Scharnier%d%d" % (s, int(zz * 10)), p + nn * 0.03 + q @ Vector((0.135 * s, 0, zz)), (0.026, 0.017, 0.03), 0.007, M["steel_l"], q))
        parts.append(rbox("Griff%d" % s, p + nn * 0.035 + q @ Vector((-0.085 * s, 0, 0.0)), (0.014, 0.017, 0.04), 0.006, M["steel_l"], q))
    for zz, w in ((0.86, 0.2), (0.27, 0.21)):
        p = shell_pt(zz, math.pi / 2); nn = shell_normal(zz, math.pi / 2)
        parts += vent("RueckLueftung%d" % int(zz * 100), p + nn * 0.004, frame_at(p, nn), w, 0.055, M)
    for s in (1, -1):
        parts += track("Kette%d" % s, s, M)
    g = join_parts(parts, "Fabrikmutter")
    g.data.transform(Matrix.Scale(K_SCALE, 4))
    return g

def dampen_rot(arm, bone, factor):
    """Kippen eines Knochens abschwächen (Drehschlüssel näher an die Ruhelage)"""
    for act in bpy.data.actions:
        fcs = [fc for fc in act.fcurves if fc.data_path == 'pose.bones["%s"].rotation_quaternion' % bone]
        if len(fcs) != 4:
            continue
        fcs.sort(key=lambda fc: fc.array_index)
        for k in range(len(fcs[0].keyframe_points)):
            q = Quaternion([fc.keyframe_points[k].co[1] for fc in fcs])
            q2 = Quaternion().slerp(q, factor)
            for i, fc in enumerate(fcs):
                kp = fc.keyframe_points[k]
                kp.co = (kp.co[0], q2[i]); kp.handle_left = (kp.handle_left[0], q2[i]); kp.handle_right = (kp.handle_right[0], q2[i])
        for fc in fcs:
            fc.update()

@variante("fabrik_mutter", "schleimmutter")
def fabrikmutter_neu(arm, body):
    remove_body(body)
    g = build_fabrikmutter()
    # unten (Ketten, Rampe) am Körperknochen, ab der Bucht weich zum oberen Knochen: der Ofen schwankt als Ganzes
    skin_to(g, arm, lambda c: {"Top": smooth01((c.z - 0.12) / 0.28), "Body": 1 - smooth01((c.z - 0.12) / 0.28)})
    dampen_scale(arm, ("Body", "Top"), 0.2)
    dampen_rot(arm, "Top", 0.45)
    print("FABRIKMUTTER", len(g.data.polygons), "Flächen")

if __name__ == "__main__":
    run(VAR, OUT)
