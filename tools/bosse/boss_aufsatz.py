# Bosse je Welt: Aufsätze und Oberfläche auf die zwei Boss-Modelle setzen (Wunsch 22.11.2026, ohne Meshy).
# Aufruf: blender -b -P tools/bosse/boss_aufsatz.py -- <variante> <ziel.glb>
#   variante: frost_schleimmutter, lava_koloss, … (siehe VARIANTEN unten)
# Ablauf: Grundmodell laden (game/models/enemies_v2/<basis>.glb), Aufsätze bauen und an Knochen hängen (bewegen sich
# mit Lauf- und Angriffsanimation), auf Wunsch die Textur des Grundmodells verändern (Reif, leuchtende Risse), als GLB
# mit allen Animationen ausgeben. Ohne Backen (Cycles-Backen liefert im Blender dieser Umgebung nur Schwarz): Aufsätze
# haben feste Farben und sind aus mehreren Teilen gebaut, Texturen werden mit numpy direkt im UV-Raum gezeichnet.
import bpy, bmesh, sys, os, math, random
import numpy as np
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
VAR, OUT = argv[0], argv[1]
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
random.seed(7)

def lin(c):
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)

# ---------------------------------------------------------------- Bausteine

def link(o):
    bpy.context.scene.collection.objects.link(o)
    return o

def finish(name, bm, smooth=True):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for pl in me.polygons:
        pl.use_smooth = smooth
    return link(bpy.data.objects.new(name, me))

def tube(name, pts, radii, segs=14, glow_from=None):
    """Röhre entlang Punkten mit wechselndem Radius (Horn, Zapfen, Stachel); Radius 0 am Ende = Spitze.
    glow_from: ab diesem Punkt bekommen die Flächen das zweite Material (z. B. glühende Spitze)."""
    bm = bmesh.new()
    rings = []
    for i, p in enumerate(pts):
        p = Vector(p)
        t = (Vector(pts[min(i + 1, len(pts) - 1)]) - Vector(pts[max(i - 1, 0)])).normalized()
        up = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((0, 1, 0))
        n1 = t.cross(up).normalized(); n2 = t.cross(n1).normalized()
        r = radii[i]
        if r <= 1e-4:
            rings.append([bm.verts.new(p)])
            continue
        rings.append([bm.verts.new(p + (n1 * math.cos(a) + n2 * math.sin(a)) * r)
                      for a in [k * 2 * math.pi / segs for k in range(segs)]])
    for i, (a, b) in enumerate(zip(rings, rings[1:])):
        mi = 1 if glow_from is not None and i >= glow_from else 0
        if len(b) == 1:
            fs = [bm.faces.new([a[k], a[(k + 1) % len(a)], b[0]]) for k in range(len(a))]
        elif len(a) == 1:
            fs = [bm.faces.new([a[0], b[(k + 1) % len(b)], b[k]]) for k in range(len(b))]
        else:
            fs = [bm.faces.new([a[k], a[(k + 1) % len(a)], b[(k + 1) % len(b)], b[k]]) for k in range(len(a))]
        for f in fs:
            f.material_index = mi
    if len(rings[0]) > 1:
        bm.faces.new(list(reversed(rings[0])))
    return finish(name, bm)

def bezier(p0, p1, p2, n=10):
    p0, p1, p2 = Vector(p0), Vector(p1), Vector(p2)
    return [(1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2 for t in [k / (n - 1) for k in range(n)]]

def horn(name, p0, p1, p2, r0, n=12, glow_from=None):
    pts = bezier(p0, p1, p2, n)
    radii = [r0 * (1 - k / (n - 1)) ** 0.8 for k in range(n)]
    radii[-1] = 0.0
    return tube(name, pts, radii, glow_from=glow_from)

def rock(name, loc, size, squash=(1, 1, 0.8), seed=0, subdiv=2):
    rnd = random.Random(seed)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=size)
    for v in bm.verts:
        v.co *= 1.0 + rnd.uniform(-0.2, 0.2)
        v.co.x *= squash[0]; v.co.y *= squash[1]; v.co.z *= squash[2]
        v.co += Vector(loc)
    return finish(name, bm)

def sphere(name, loc, r, squash=(1, 1, 1), segs=(20, 12)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs[0], v_segments=segs[1], radius=r)
    for v in bm.verts:
        v.co.x *= squash[0]; v.co.y *= squash[1]; v.co.z *= squash[2]
        v.co += Vector(loc)
    return finish(name, bm)

def crystal(name, loc, h, r, tilt=(0, 0, 0)):
    """Facettierter Kristall (sechskantig mit Spitze) wie an den Mauern; flach schattiert für klare Facetten"""
    tip = r * 1.8
    bm = bmesh.new()
    lo = [bm.verts.new((r * 0.75 * math.cos(k * math.pi / 3), r * 0.75 * math.sin(k * math.pi / 3), 0)) for k in range(6)]
    hi = [bm.verts.new((r * math.cos(k * math.pi / 3 + 0.1), r * math.sin(k * math.pi / 3 + 0.1), h)) for k in range(6)]
    top = bm.verts.new((r * 0.1, -r * 0.05, h + tip))
    bm.faces.new(list(reversed(lo)))
    for k in range(6):
        j = (k + 1) % 6
        bm.faces.new([lo[k], lo[j], hi[j], hi[k]]); bm.faces.new([hi[k], hi[j], top])
    o = finish(name, bm, smooth=False)
    o.location = loc; o.rotation_euler = tuple(math.radians(a) for a in tilt)
    return o

def look(name, base, rough=0.5, metal=0.0, emit=None, strength=0.0, alpha=1.0):
    """Material mit festen Werten (geht so ins GLB): Grundfarbe, Rauheit, Metall, Leuchten"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*lin(base), 1)
    p.inputs["Roughness"].default_value = rough; p.inputs["Metallic"].default_value = metal
    if emit:
        p.inputs["Emission Color"].default_value = (*lin(emit), 1)
        p.inputs["Emission Strength"].default_value = strength
    if alpha < 1.0:
        p.inputs["Alpha"].default_value = alpha
        m.blend_method = 'BLEND'
    return m

def give(o, *mats):
    o.data.materials.clear()
    for m in mats:
        o.data.materials.append(m)
    return o

def magma_rock(name, loc, size, rock_m, core_m, seed=0):
    """Magmabrocken: glühender Kern, darum dunkle Schollen mit Fugen, durch die die Glut scheint"""
    rnd = random.Random(seed)
    parts = [give(sphere(name + "Kern", loc, size * 0.8), core_m)]
    n = 12
    for k in range(n):
        # Schollen gleichmäßig auf der Kugel verteilt (Fibonacci), etwas zu klein, damit Fugen bleiben
        y = 1 - 2 * (k + 0.5) / n
        rad = math.sqrt(1 - y * y); th = k * 2.39996
        d = Vector((math.cos(th) * rad, y, math.sin(th) * rad))
        c = Vector(loc) + d * size * 0.6
        parts.append(give(rock(name + "Scholle%d" % k, c, size * rnd.uniform(0.5, 0.58), (1, 1, 0.8), seed=seed * 31 + k, subdiv=1), rock_m))
    return parts

# ---------------------------------------------------------------- Texturen im UV-Raum (numpy)

def value_noise(h, w, cells, seed):
    rng = np.random.default_rng(seed)
    g = rng.random((cells + 1, cells + 1))
    y = np.linspace(0, cells, h, endpoint=False); x = np.linspace(0, cells, w, endpoint=False)
    yi = y.astype(int); xi = x.astype(int); fy = (y - yi)[:, None]; fx = (x - xi)[None, :]
    fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
    a = g[yi][:, xi]; b = g[yi][:, xi + 1]; c = g[yi + 1][:, xi]; d = g[yi + 1][:, xi + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy

def fbm(h, w, cells, seed, octaves=4):
    out = np.zeros((h, w)); amp = 1.0; tot = 0.0
    for o in range(octaves):
        out += value_noise(h, w, cells * 2 ** o, seed + o) * amp; tot += amp; amp *= 0.5
    return out / tot

def voronoi_edges(h, w, n, seed, warp=0.015):
    """Abstand zur nächsten Zellgrenze (in UV-Einheiten), leicht verwackelt für natürliche Risse"""
    rng = np.random.default_rng(seed)
    pts = rng.random((n, 2)).astype(np.float32)
    pts = np.concatenate([pts + np.float32([dx, dy]) for dx in (-1, 0, 1) for dy in (-1, 0, 1)])  # nahtlos
    wy = (fbm(h, w, 6, seed + 11) - 0.5) * warp * 2; wx = (fbm(h, w, 6, seed + 23) - 0.5) * warp * 2
    out = np.zeros((h, w), dtype=np.float32)
    ys = ((np.arange(h) + 0.5) / h).astype(np.float32); xs = ((np.arange(w) + 0.5) / w).astype(np.float32)
    wy = wy.astype(np.float32); wx = wx.astype(np.float32)
    for r0 in range(0, h, 16):
        r1 = min(h, r0 + 16)
        py = ys[r0:r1, None] + wy[r0:r1]; px = xs[None, :] + wx[r0:r1]
        d = (py[..., None] - pts[:, 1]) ** 2 + (px[..., None] - pts[:, 0]) ** 2
        d = np.sqrt(np.partition(d, 1, axis=-1)[..., :2])
        out[r0:r1] = (d[..., 1] - d[..., 0]) * 0.5
    return out

def body_texture(body):
    m = body.data.materials[0]
    tex = next(n for n in m.node_tree.nodes if n.type == 'TEX_IMAGE')
    img = tex.image
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    return m, tex, img, px

def new_image(name, arr):
    h, w = arr.shape[:2]
    img = bpy.data.images.new(name, w, h, alpha=True)
    img.pixels.foreach_set(np.ascontiguousarray(arr, dtype=np.float32).ravel())
    img.pack()
    return img

def mask_color(px, ch, margin=0.05, soft=0.1):
    """Maske für Stellen, an denen Kanal ch (0 R, 1 G, 2 B) deutlich über den anderen liegt;
    ch = "teal": Grün und Blau beide deutlich über Rot (Schleim)"""
    if ch == "teal":
        d = np.minimum(px[..., 1], px[..., 2]) - px[..., 0]
    else:
        others = [c for c in (0, 1, 2) if c != ch]
        d = np.minimum(px[..., ch] - px[..., others[0]], px[..., ch] - px[..., others[1]])
    return np.clip((d - margin) / soft, 0, 1)

def skin_cracks(body, color, cells, width, strength=1.6, ch=1, seed=5):
    """Leuchtende Risse auf die Haut (Stellen, an denen Kanal ch vorherrscht), als Leuchttextur"""
    m, tex, img, px = body_texture(body)
    h, w = px.shape[:2]
    edge = voronoi_edges(h, w, cells, seed)
    line = np.clip(1 - edge / width, 0, 1) ** 1.5
    halo = np.clip(1 - edge / (width * 4), 0, 1) ** 2 * 0.35
    k = np.maximum(line, halo) * mask_color(px, ch) * (fbm(h, w, 4, seed + 3) > 0.35)
    c = np.array(color, dtype=np.float32)   # Texturwerte sind sRGB wie im Bild
    em = np.zeros((h, w, 4), dtype=np.float32); em[..., :3] = k[..., None] * c; em[..., 3] = 1
    # die Haut um die Risse dunkler (verkohlt)
    base = px.copy(); base[..., :3] *= (1 - 0.45 * np.clip(halo * 2.5, 0, 1))[..., None]
    tex.image = new_image(body.name + "_Farbe", base)
    set_emission(body, em, strength)

def set_emission(body, em, strength):
    """Leuchttextur des Grundmodells setzen oder mit der vorhandenen zusammenführen (hellerer Wert gewinnt)"""
    m = body.data.materials[0]; nt = m.node_tree
    p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    node = nt.nodes.get("LeuchtTextur")
    if node is None:
        node = nt.nodes.new("ShaderNodeTexImage"); node.name = "LeuchtTextur"
    elif node.image is not None:
        h, w = em.shape[:2]
        old = np.array(node.image.pixels[:], dtype=np.float32).reshape(h, w, 4)
        em[..., :3] = np.maximum(em[..., :3], old[..., :3])
    node.image = new_image(body.name + "_Leuchten", em)
    nt.links.new(node.outputs["Color"], p.inputs["Emission Color"])
    p.inputs["Emission Strength"].default_value = max(strength, p.inputs["Emission Strength"].default_value)

def mask_yellow(px):
    return np.clip((np.minimum(px[..., 0], px[..., 1]) - px[..., 2] - 0.25) / 0.15, 0, 1)

def recolor(body, mask, color, glow=0.0, strength=1.5):
    """Stellen der Maske umfärben (Helligkeit bleibt), auf Wunsch leuchtend"""
    m, tex, img, px = body_texture(body)
    k = mask(px)[..., None]
    lum = (0.3 * px[..., 0] + 0.6 * px[..., 1] + 0.1 * px[..., 2])[..., None]
    c = np.array(color, dtype=np.float32)
    new = np.clip(c * (0.35 + lum * 1.1), 0, 1)
    base = px.copy(); base[..., :3] = base[..., :3] * (1 - k) + new * k
    tex.image = new_image(body.name + "_Farbe", base)
    if glow > 0:
        em = np.zeros_like(px); em[..., :3] = k * c * glow; em[..., 3] = 1
        set_emission(body, em, strength)

def speckles(body, mask_ch, color, amount, cells, seed=3):
    """Flecken in einer Farbe auf die Stellen der Maske (Giftflecken, Sandkörner)"""
    m, tex, img, px = body_texture(body)
    h, w = px.shape[:2]
    n = fbm(h, w, cells, seed, octaves=3)
    k = (mask_color(px, mask_ch, 0.02, 0.15) * np.clip((n - (1 - amount)) * 6, 0, 1))[..., None]
    base = px.copy(); base[..., :3] = base[..., :3] * (1 - k * 0.7) + np.array(color, dtype=np.float32) * (k * 0.7)
    tex.image = new_image(body.name + "_Farbe", base)

def torus(name, loc, R, r, rot=(90, 0, 0), segs=40):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=segs, minor_segments=12,
                                     location=loc, rotation=tuple(math.radians(a) for a in rot))
    o = bpy.context.active_object; o.name = name
    bpy.ops.object.shade_smooth()
    return o

def frost_skin(body, ch=1, seed=9):
    """Reif auf dem Schleim: helle, fleckige Frostschicht auf den Stellen, an denen Kanal ch vorherrscht"""
    m, tex, img, px = body_texture(body)
    h, w = px.shape[:2]
    n = fbm(h, w, 5, seed)
    fine = fbm(h, w, 40, seed + 5, octaves=2)
    k = mask_color(px, ch, 0.02, 0.15) * np.clip((n - 0.42) * 2.2, 0, 1)
    sparkle = (fine > 0.8) * mask_color(px, ch, 0.02, 0.15)
    base = px.copy()
    frost = np.array((0.9, 0.97, 1.0), dtype=np.float32)
    base[..., :3] = base[..., :3] * (1 - k[..., None] * 0.42) + frost * (k[..., None] * 0.42)
    base[..., :3] = np.maximum(base[..., :3], sparkle[..., None] * 0.92)
    # gelbe Kugeln werden Eiskugeln (Helligkeit bleibt, Farbe eisblau)
    yel = np.clip((np.minimum(px[..., 0], px[..., 1]) - px[..., 2] - 0.25) / 0.15, 0, 1)
    lum = (0.3 * px[..., 0] + 0.6 * px[..., 1] + 0.1 * px[..., 2])[..., None]
    ice = np.clip(lum * np.array((0.82, 1.0, 1.12), dtype=np.float32) + 0.08, 0, 1)
    base[..., :3] = base[..., :3] * (1 - yel[..., None]) + ice * yel[..., None]
    tex.image = new_image(body.name + "_Farbe", base)

# ---------------------------------------------------------------- Varianten

bpy.ops.wm.read_factory_settings(use_empty=True)
VARIANTEN = {}

def variante(name, basis):
    def deco(f):
        VARIANTEN[name] = (basis, f)
        return f
    return deco

def attach(o, arm, bone):
    """Aufsatz an einen Knochen hängen, Lage aus der Ruhehaltung beibehalten"""
    bpy.context.view_layer.update()
    mw = o.matrix_world.copy()
    o.parent = arm; o.parent_type = 'BONE'; o.parent_bone = bone
    bpy.context.view_layer.update()
    o.matrix_world = mw
    return o

# ---------------------------------------------------------------- eigene Körper (Wunsch 23.11.2026: je Welt ein eigener Boss)

def lathe(name, profile, segs=48, hem=None):
    """Drehkörper aus einem Profil [(z, r), …] von oben nach unten; hem(a) verschiebt die unterste Reihe (Saum)"""
    bm = bmesh.new()
    rings = []
    for i, (z, r) in enumerate(profile):
        if r <= 1e-4:
            rings.append([bm.verts.new((0, 0, z))])
            continue
        ring = []
        for k in range(segs):
            a = k * 2 * math.pi / segs
            zz, rr = z, r
            if hem is not None and i == len(profile) - 1:
                dz, dr = hem(a)
                zz += dz; rr += dr
            ring.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), zz)))
        rings.append(ring)
    n = len(rings)
    uv = bm.loops.layers.uv.new("UVMap")
    for i, (a_, b_) in enumerate(zip(rings, rings[1:])):
        if len(a_) == 1:
            fs = [(bm.faces.new([a_[0], b_[k], b_[(k + 1) % len(b_)]]), [(0, k), (1, k), (1, k + 1)]) for k in range(len(b_))]
        elif len(b_) == 1:
            fs = [(bm.faces.new([a_[k], b_[0], a_[(k + 1) % len(a_)]]), [(0, k), (1, k), (0, k + 1)]) for k in range(len(a_))]
        else:
            fs = [(bm.faces.new([a_[k], b_[k], b_[(k + 1) % len(b_)], a_[(k + 1) % len(a_)]]), [(0, k), (1, k), (1, k + 1), (0, k + 1)])
                  for k in range(len(a_))]
        for f, coords in fs:
            for loop, (di, k) in zip(f.loops, coords):
                loop[uv].uv = (k / segs, 1 - (i + di) / (n - 1))
    return finish(name, bm)

def skin_to(o, arm, weights):
    """Eigenen Körper an das Skelett binden: weights(z) -> {Knochen: Gewicht}"""
    o.parent = arm
    o.matrix_parent_inverse = arm.matrix_world.inverted()
    md = o.modifiers.new("Skelett", 'ARMATURE'); md.object = arm
    groups = {}
    for v in o.data.vertices:
        for bone, w in weights(v.co).items():
            if bone not in groups:
                groups[bone] = o.vertex_groups.new(name=bone)
            if w > 0:
                groups[bone].add([v.index], w, 'REPLACE')
    return o

def remove_body(body):
    bpy.data.objects.remove(body, do_unlink=True)

def smooth01(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)

@variante("nebel_geist", "schleimmutter")
def nebelgeist(arm, body):
    """Nebelfelder (Welt 8): Nebelgeist – schwebendes Gespenst mit gewelltem Saum, kleinen Armen, glühenden Augen,
    offenem Maul, einer Nebellocke oben und Nebelkugeln auf einem Ring um den Kopf. Eigene Figur, kein Nachbau."""
    ghost = look("Geist", (0.93, 0.92, 1.0), rough=0.45, emit=(0.72, 0.68, 1.0), strength=0.45)   # undurchsichtig: keine sichtbaren Ebenen beim Springen (Kommentar 24.11.)
    ghost_shade = look("GeistSchatten", (0.7, 0.66, 0.92), rough=0.5, emit=(0.55, 0.5, 0.9), strength=0.3)
    dark = look("Maul", (0.08, 0.04, 0.16), rough=0.6, emit=(0.35, 0.1, 0.6), strength=0.6)
    eye = look("Auge", (0.75, 0.95, 1.0), rough=0.2, emit=(0.55, 0.9, 1.0), strength=4.0)
    pupil = look("Pupille", (0.1, 0.02, 0.2), rough=0.3)
    fog = look("Nebel", (0.88, 0.92, 1.0), rough=0.3, emit=(0.7, 0.8, 1.0), strength=0.9, alpha=0.6)
    prof = [(0.98, 0.0), (0.96, 0.09), (0.93, 0.16), (0.88, 0.22), (0.82, 0.28), (0.7, 0.335), (0.56, 0.35), (0.42, 0.345),
            (0.32, 0.35), (0.25, 0.365), (0.19, 0.385), (0.14, 0.405), (0.1, 0.42)]
    hem = lambda a: (-0.12 * (0.5 + 0.5 * math.cos(7 * a + 0.3)) ** 1.5, 0.025 * math.cos(7 * a + 0.3))
    g = lathe("Geistkoerper", prof, segs=64, hem=hem)
    # Boden des Saums: nach innen gewölbt, damit er von unten hohl wirkt
    inner = lathe("Saumboden", [(0.08, 0.41), (0.15, 0.3), (0.2, 0.0)], segs=64)
    # Textur: oben weiß, nach unten lavendel bis violett, mit hellen Nebelschlieren
    H_, W_ = 512, 512
    v = np.linspace(0, 1, H_)[:, None] * np.ones((1, W_))   # Bildzeile 0 ist unten (v = 0)
    wisp = fbm(H_, W_, 6, 77)
    grad = np.clip((v - 0.25) / 0.6, 0, 1)
    top = np.array((0.97, 0.96, 1.0)); bot = np.array((0.62, 0.52, 0.92))
    col = bot * (1 - grad[..., None]) + top * grad[..., None]
    col = np.clip(col + ((wisp - 0.5) * 0.25)[..., None] * np.array((0.6, 0.6, 0.8)), 0, 1)
    arr = np.ones((H_, W_, 4), dtype=np.float32); arr[..., :3] = col
    gimg = new_image("Geist_Farbe", arr)
    nt = ghost.node_tree
    ti = nt.nodes.new("ShaderNodeTexImage"); ti.image = gimg
    nt.links.new(ti.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    for o in (g, inner):
        give(o, ghost)
    for o in (g, inner):
        skin_to(o, arm, lambda c: {"Top": smooth01((c.z - 0.3) / 0.45), "Body": 1 - smooth01((c.z - 0.3) / 0.45)})
    # Gesicht (am Kopfknochen): schräge Augen, offenes Maul
    for s in (-1, 1):
        sock = sphere("Augenhoehle%d" % s, (0, 0, 0), 0.085, (1.0, 0.35, 1.25)); sock.location = (s * 0.13, -0.3, 0.64)
        sock.rotation_euler = (0, math.radians(s * 22), 0)
        attach(give(sock, dark), arm, "Top")
        e = sphere("Auge%d" % s, (0, 0, 0), 0.06, (1.0, 0.5, 1.2)); e.location = (s * 0.13, -0.325, 0.64)
        e.rotation_euler = (0, math.radians(s * 22), 0)
        attach(give(e, eye), arm, "Top")
        attach(give(sphere("Pupille%d" % s, (s * 0.12, -0.355, 0.62), 0.022), pupil), arm, "Top")
        brow = tube("Braue%d" % s, [(s * 0.22, -0.28, 0.76), (s * 0.13, -0.315, 0.73), (s * 0.05, -0.325, 0.69)], [0.02, 0.026, 0.018])
        attach(give(brow, ghost_shade), arm, "Top")
    mouth = sphere("Maul", (0, 0, 0), 0.1, (1.25, 0.35, 0.8)); mouth.location = (0, -0.33, 0.43)
    attach(give(mouth, dark), arm, "Top")
    for s in (-1, 1):
        attach(give(tube("Zahn%d" % s, [(s * 0.06, -0.355, 0.49), (s * 0.055, -0.36, 0.455), (s * 0.05, -0.36, 0.43)], [0.016, 0.01, 0.0]), ghost), arm, "Top")
    # Arme mit Fäustlingshänden
    for s in (-1, 1):
        armt = tube("Arm%d" % s, [(s * 0.3, -0.02, 0.44), (s * 0.44, -0.1, 0.5), (s * 0.53, -0.2, 0.62)], [0.07, 0.06, 0.055])
        attach(give(armt, ghost), arm, "Body")
        attach(give(sphere("Hand%d" % s, (s * 0.55, -0.23, 0.66), 0.075, (1, 1, 1.1)), ghost), arm, "Body")
        for k, (dx, dz) in enumerate(((0.05, 0.06), (0.0, 0.085), (-0.05, 0.06))):
            attach(give(sphere("Finger%d_%d" % (s, k), (s * 0.55 + dx * s, -0.26, 0.66 + dz), 0.026), ghost), arm, "Body")
    # Nebellocke oben, Nebelring mit Kugeln
    pts = []; radii = []
    for k in range(16):
        t = k / 15
        a = t * 2.3 * 2 * math.pi
        pts.append((0.13 * (1 - t) * math.cos(a), 0.13 * (1 - t) * math.sin(a), 0.93 + t * 0.3))
        radii.append(0.075 * (1 - t) + 0.004)
    radii[-1] = 0.0
    attach(give(tube("Locke", pts, radii), ghost), arm, "Top")
    # Nebelring über dem Kopf, vorn etwas höher (läuft nicht vor den Augen durch)
    tilt = math.radians(-14)
    t_ = torus("Nebelring", (0.0, 0.04, 0.95), 0.4, 0.016, rot=(-14, 0, 0))
    attach(give(t_, fog), arm, "Top")
    for i in range(6):
        a = i * math.pi / 3 + 0.4
        attach(give(sphere("Nebelkugel%d" % i, (0.4 * math.cos(a), 0.04 + 0.4 * math.sin(a) * math.cos(tilt),
                                               0.95 + 0.4 * math.sin(a) * math.sin(tilt)), 0.045 + 0.015 * (i % 2)), fog), arm, "Top")
    remove_body(body)

def mask_purple(px):
    return np.clip((np.minimum(px[..., 0], px[..., 2]) - px[..., 1] - 0.08) / 0.12, 0, 1)

def mask_white(px):
    return np.clip((np.min(px[..., :3], axis=-1) - 0.62) / 0.15, 0, 1)

def skin_lines(body, color, cells, width, ch=1, seed=41, strength=0.55):
    """feine dunkle Falten auf der Haut (z. B. Nashornhaut)"""
    m, tex, img, px = body_texture(body)
    h, w = px.shape[:2]
    edge = voronoi_edges(h, w, cells, seed, warp=0.03)
    k = (np.clip(1 - edge / width, 0, 1) * mask_color(px, ch, 0.0, 0.1))[..., None]
    base = px.copy(); base[..., :3] = base[..., :3] * (1 - k * strength) + np.array(color, dtype=np.float32) * (k * strength)
    tex.image = new_image(body.name + "_Farbe", base)

def reshape_arms(arm, body, upper=(1.15, 0.9), fore=(0.72, 0.8), hand=0.78):
    """Arme des Koloss umformen (Kommentare 23.11.: Unterarm nicht dicker als Oberarm, kürzere Arme).
    upper/fore = (Dicke, Länge) absolut, hand = Größe absolut. Nur Dicke und Länge ändern sich; die Ausrichtung der
    Knochen bleibt wie im Original, sonst biegt die Laufanimation den Unterarm nach hinten (Meldung 23.11.)."""
    saved = arm.animation_data.action if arm.animation_data else None
    if arm.animation_data:
        arm.animation_data.action = None
    arm.data.pose_position = 'POSE'
    for pb in arm.pose.bones:
        pb.location = (0, 0, 0); pb.rotation_quaternion = (1, 0, 0, 0); pb.rotation_euler = (0, 0, 0); pb.scale = (1, 1, 1)
    for side in ("Left", "Right"):
        ub = arm.pose.bones["mixamorig:%sArm" % side]
        fb = arm.pose.bones["mixamorig:%sForeArm" % side]
        hb = arm.pose.bones["mixamorig:%sHand" % side]
        ub.scale = (upper[0], upper[1], upper[0])
        fb.scale = (fore[0] / upper[0], fore[1] / upper[1], fore[0] / upper[0])   # Skalierung erbt vom Oberarm
        hb.scale = (hand / fore[0], hand / fore[1], hand / fore[0])
    bpy.context.view_layer.update()
    mod = next(m for m in body.modifiers if m.type == 'ARMATURE')
    bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); bpy.context.view_layer.objects.active = body
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='POSE'); bpy.ops.pose.armature_apply(selected=False); bpy.ops.object.mode_set(mode='OBJECT')
    md = body.modifiers.new("Armature", 'ARMATURE'); md.object = arm
    if saved:
        arm.animation_data.action = saved
    arm.data.pose_position = 'REST'
    bpy.context.view_layer.update()

def fix_elbows(arm, extra=12.0, lo=24.0, hi=85.0, inward=28.0):
    """Ellenbogen in allen Aktionen nur nach vorn (und etwas nach innen) beugen (Kommentar 23.11.: „überdehnt“).
    Die Koloss-Animationen strecken den Unterarm beim Angriff über die Gerade hinaus und knicken ihn beim Laufen
    seitlich nach außen; von der Spielkamera schräg oben wirkt das wie ein verkehrt herum gebogener Ellenbogen.
    Je Bild bleibt der Oberarm, wie er ist; der Unterarm wird in die Beugeebene gelegt: Scharnier quer zum Körper,
    um `inward` Grad nach innen gedreht (Hände vor den Bauch statt nach außen). Beugewinkel = bisheriger Winkel
    + `extra`, begrenzt auf lo…hi Grad; die Drehung des Unterarms um die eigene Achse bleibt erhalten."""
    from mathutils import Matrix
    sc = bpy.context.scene
    ad = arm.animation_data
    saved = ad.action
    arm.data.pose_position = 'POSE'
    bi = math.radians(inward)
    acts = [a for a in bpy.data.actions if any('mixamorig:LeftForeArm' in fc.data_path for fc in a.fcurves)]
    for act in acts:
        ad.action = act
        a, b = int(act.frame_range[0]), int(act.frame_range[1])
        new = {"Left": [], "Right": []}
        for f in range(a, b + 1):
            sc.frame_set(f)
            lat = arm.pose.bones["mixamorig:Spine2"].matrix.col[0].to_3d().normalized()   # zur linken Körperseite
            for side in ("Left", "Right"):
                ub = arm.pose.bones["mixamorig:%sArm" % side]
                fb = arm.pose.bones["mixamorig:%sForeArm" % side]
                u = (ub.tail - ub.head).normalized(); v = (fb.tail - fb.head).normalized()
                n = u.cross(lat).normalized()                                   # Beugen nach vorn
                inn = -lat if side == "Left" else lat
                m = (inn - u * inn.dot(u)).normalized()                         # nach innen, senkrecht zum Oberarm
                k = n * math.cos(bi) + m * math.sin(bi); k = (k - u * k.dot(u)).normalized()
                phi = math.radians(min(hi, max(lo, math.degrees(u.angle(v)) + extra)))
                t = (u * math.cos(phi) + k * math.sin(phi)).normalized()
                R = v.rotation_difference(t).to_matrix().to_4x4()
                head = fb.matrix.translation.copy()
                M = Matrix.Translation(head) @ R @ Matrix.Translation(-head) @ fb.matrix
                q = arm.convert_space(pose_bone=fb, matrix=M, from_space='POSE', to_space='LOCAL').to_quaternion()
                if new[side] and new[side][-1][1].dot(q) < 0:
                    q.negate()
                new[side].append((f, q))
        for side, keys in new.items():
            path = 'pose.bones["mixamorig:%sForeArm"].rotation_quaternion' % side
            for fc in [fc for fc in act.fcurves if fc.data_path == path]:
                act.fcurves.remove(fc)
            for i in range(4):
                fc = act.fcurves.new(path, index=i, action_group="mixamorig:%sForeArm" % side)
                fc.keyframe_points.add(len(keys))
                for kp, (f, q) in zip(fc.keyframe_points, keys):
                    kp.co = (f, q[i]); kp.interpolation = 'LINEAR'
                fc.update()
    ad.action = saved
    arm.data.pose_position = 'REST'
    bpy.context.view_layer.update()

def join_parts(objs, name):
    """Mehrere Teile zu einem Objekt verbinden (Materialien bleiben je Fläche erhalten)"""
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active; o.name = name
    return o

def place_in_bone(o, arm, bone):
    """Teil, das im Ruherahmen eines Knochens gebaut ist (Ursprung = Knochenkopf, Y entlang des Knochens), an seinen
    Platz setzen und an den Knochen hängen"""
    o.matrix_world = arm.matrix_world @ arm.data.bones[bone].matrix_local @ o.matrix_world
    return attach(o, arm, bone)

def cut_hands(body):
    """Hände des Koloss aus dem Körper schneiden (fünf Fingerknochen, verdrehte Fingerbewegungen; Kommentar 24.11.);
    Reste am Handgelenk folgen nur noch dem Unterarm"""
    gn = {g.index: g.name for g in body.vertex_groups}
    kill = []
    for side in ("Left", "Right"):
        fore = body.vertex_groups["mixamorig:%sForeArm" % side]
        for v in body.data.vertices:
            hw = sum(g.weight for g in v.groups if gn[g.group].startswith("mixamorig:%sHand" % side))
            if hw > 0.5:
                kill.append(v.index)
            elif hw > 0:
                fw = sum(g.weight for g in v.groups if gn[g.group] == "mixamorig:%sForeArm" % side)
                fore.add([v.index], fw + hw, 'REPLACE')
                for g in list(v.groups):
                    if gn[g.group].startswith("mixamorig:%sHand" % side):
                        body.vertex_groups[g.group].remove([v.index])
    bm = bmesh.new(); bm.from_mesh(body.data); bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.verts[i] for i in kill], context='VERTS')
    bm.to_mesh(body.data); bm.free(); body.data.update()

def hand_model(name, side, skin, nail, size=1.0, fingers=3, claws=False, fist=0.0):
    """Eigene Hand im Rahmen des Handknochens: Finger entlang +Y, Daumen auf der +X-Seite, Handfläche links nach -Z,
    rechts nach +Z (Spiegelbild). fingers 3 (Nashorn, Golem) oder 4; claws: spitze Krallen statt Hufnägeln;
    fist 0…1: Finger stärker zur Faust eingerollt."""
    k = size; zs = 1.0 if side == "Left" else -1.0

    def P(x, y, z):
        return (x * k, y * k, z * k * zs)
    parts = [give(sphere(name + "Ballen", P(0.0, 0.085, 0.0), 0.1 * k, (1.0, 0.95, 0.62)), skin),
             give(sphere(name + "Ruecken", P(-0.005, 0.1, 0.022), 0.085 * k, (1.0, 0.9, 0.55)), skin)]
    xs = (-0.058, -0.002, 0.05) if fingers == 3 else (-0.066, -0.023, 0.018, 0.057)
    rf = 1.0 if fingers == 3 else 0.82
    curl = 1.0 + fist * 1.6
    for i, x in enumerate(xs):
        pts = [P(x, 0.13, 0.0), P(x * 1.06, 0.195 - fist * 0.02, -0.012 * curl), P(x * 1.12, 0.245 - fist * 0.05, -0.045 * curl),
               P(x * 1.14, 0.262 - fist * 0.08, -0.075 * curl)]
        parts.append(give(tube("%sFinger%d" % (name, i), pts, [0.037 * k * rf, 0.035 * k * rf, 0.031 * k * rf, 0.026 * k * rf]), skin))
        parts.append(give(sphere("%sKuppe%d" % (name, i), pts[-1], 0.026 * k * rf), skin))
        if claws:
            tip = Vector(pts[-1]); d = (tip - Vector(pts[-2])).normalized()
            parts.append(give(tube("%sKralle%d" % (name, i), [tuple(tip - d * 0.005 * k), tuple(tip + d * 0.03 * k), tuple(tip + d * 0.055 * k + Vector(P(0, 0, -0.01)))],
                                   [0.02 * k * rf, 0.013 * k * rf, 0.0]), nail))
        else:
            parts.append(give(sphere("%sNagel%d" % (name, i), P(x * 1.14, 0.27 - fist * 0.08, -0.072 * curl), 0.028 * k * rf, (1.0, 0.8, 0.85)), nail))
    pts = [P(0.07, 0.055, -0.012), P(0.104, 0.11, -0.038 - fist * 0.02), P(0.112 - fist * 0.03, 0.155 - fist * 0.02, -0.065 - fist * 0.03)]
    parts.append(give(tube(name + "Daumen", pts, [0.04 * k, 0.035 * k, 0.029 * k]), skin))
    parts.append(give(sphere(name + "DaumenKuppe", pts[-1], 0.029 * k), skin))
    if claws:
        tip = Vector(pts[-1]); d = (tip - Vector(pts[-2])).normalized()
        parts.append(give(tube(name + "DaumenKralle", [tuple(tip - d * 0.005 * k), tuple(tip + d * 0.03 * k), tuple(tip + d * 0.05 * k)], [0.02 * k, 0.012 * k, 0.0]), nail))
    else:
        parts.append(give(sphere(name + "DaumenNagel", (pts[-1][0] + 0.004 * k, pts[-1][1] + 0.008 * k, pts[-1][2]), 0.03 * k, (0.9, 0.8, 0.85)), nail))
    return join_parts(parts, name)

def forearm_wrist(arm, body, side):
    """Mitte und Weite des Unterarms am Handgelenk (im Rahmen des Unterarmknochens), aus dem Körper gemessen"""
    fname = "mixamorig:%sForeArm" % side
    fb = arm.data.bones[fname]; L = fb.length
    Minv = (arm.matrix_world @ fb.matrix_local).inverted()
    fi = body.vertex_groups[fname].index
    pts = []
    for v in body.data.vertices:
        if any(g.group == fi and g.weight > 0.5 for g in v.groups):
            q = Minv @ (body.matrix_world @ v.co)
            if L - 0.12 < q.y < L + 0.02:
                pts.append(q)
    cx = sum(q.x for q in pts) / len(pts); cz = sum(q.z for q in pts) / len(pts)

    def ring_r(y0, y1):
        rr = sorted(math.hypot(q.x - cx, q.z - cz) for q in pts if y0 < q.y < y1)
        return rr[int(len(rr) * 0.95)] + 0.008
    r_top, r_bot = ring_r(L - 0.12, L - 0.06), ring_r(L - 0.05, L + 0.02)
    return L, cx, cz, max(r_top, max(r_bot, r_top * 0.9)), max(r_bot, r_top * 0.9)

def wrist_cuffs(arm, body, mat, rim=None, style="stulpe"):
    """Stulpe am Handgelenk (deckt den Schnitt zur neuen Hand ab): style "stulpe" (Leder mit Metallrand),
    "binde" (gewickelte Binde), "fell" (Fellkrause)"""
    for side in ("Left", "Right"):
        fname = "mixamorig:%sForeArm" % side
        L, cx, cz, rt, rb = forearm_wrist(arm, body, side)
        if style == "fell":
            parts = [give(tube("Krause" + side, [(cx, L - 0.09, cz), (cx, L - 0.04, cz), (cx, L + 0.015, cz)], [rt * 1.02, rb * 1.08, rb * 1.05]), mat)]
            for i in range(14):
                a = i * 2 * math.pi / 14 + (0.2 if i % 2 else 0)
                y = L - 0.02 - 0.05 * (i % 2)
                parts.append(give(sphere("Zotte%s%d" % (side, i), (cx + math.cos(a) * rb * 1.05, y, cz + math.sin(a) * rb * 1.05), 0.042,
                                         (1.0, 1.4, 1.0)), mat))
            o = join_parts(parts, "Krause" + side)
            place_in_bone(o, arm, fname)
            continue
        cuff = give(tube("Stulpe" + side, [(cx, L - 0.095, cz), (cx, L - 0.05, cz), (cx, L - 0.005, cz), (cx, L + 0.02, cz)],
                         [rt, (rt + rb) / 2 + 0.004, rb * 1.02, rb]), mat)
        place_in_bone(cuff, arm, fname)
        if style == "binde":
            for i, (y, tilt) in enumerate(((L - 0.085, 12), (L - 0.055, -10), (L - 0.025, 14), (L + 0.008, -8))):
                t = give(torus("Binde%s%d" % (side, i), (cx, y, cz), (rt + rb) / 2 + 0.006, 0.013, rot=(90 + tilt, 0, 0)), mat)
                place_in_bone(t, arm, fname)
        elif rim is not None:
            for i, (y, r) in enumerate(((L + 0.018, rb), (L - 0.093, rt))):
                t = give(torus("StulpenRand%s%d" % (side, i), (cx, y, cz), r, 0.014 - 0.002 * i, rot=(90, 0, 0)), rim)
                place_in_bone(t, arm, fname)

def pose_hands(arm, psi=30.0, flex=10.0):
    """Haltung der Hände in allen Aktionen setzen (Kommentar 24.11.): Hand in Verlängerung des Unterarms, `flex` Grad
    zur Handfläche gebeugt; Daumen zur Beugeseite des Unterarms, um `psi` Grad zum Körper gedreht. Hängende Arme:
    Handflächen zu den Oberschenkeln, Daumen vorn-innen. Passt zu hand_model (Daumen +X, Handfläche links -Z)."""
    from mathutils import Matrix
    sc = bpy.context.scene
    ad = arm.animation_data
    saved = ad.action
    arm.data.pose_position = 'POSE'
    PB = arm.pose.bones
    ps, fl = math.radians(psi), math.radians(flex)

    def perp(x, a):
        return (x - a * x.dot(a)).normalized()

    for act in [a for a in bpy.data.actions if any('mixamorig:LeftHand"' in fc.data_path for fc in a.fcurves)]:
        ad.action = act
        a, b = int(act.frame_range[0]), int(act.frame_range[1])
        keys = {"Left": [], "Right": []}
        for f in range(a, b + 1):
            sc.frame_set(f)
            lat = PB["mixamorig:Spine2"].matrix.col[0].to_3d().normalized()
            for side in ("Left", "Right"):
                inn = -lat if side == "Left" else lat
                u = (PB["mixamorig:%sArm" % side].tail - PB["mixamorig:%sArm" % side].head).normalized()
                fb = PB["mixamorig:%sForeArm" % side]; t = (fb.tail - fb.head).normalized()
                d = perp(u.cross(lat), t)                                   # Beugeseite des Unterarms
                m = perp(inn, t); m = perp(m - d * m.dot(d), t)             # zum Körper
                x = (d * math.cos(ps) + m * math.sin(ps)).normalized()      # Daumenseite
                palm = -x.cross(t) if side == "Left" else x.cross(t)
                y = (t * math.cos(fl) + palm * math.sin(fl)).normalized()
                x = perp(x, y); z = x.cross(y)
                hb = PB["mixamorig:%sHand" % side]
                M = Matrix((x, y, z)).transposed().to_4x4(); M.translation = hb.matrix.translation
                q = arm.convert_space(pose_bone=hb, matrix=M, from_space='POSE', to_space='LOCAL').to_quaternion()
                if keys[side] and keys[side][-1][1].dot(q) < 0:
                    q.negate()
                keys[side].append((f, q))
        for side, kk in keys.items():
            path = 'pose.bones["mixamorig:%sHand"].rotation_quaternion' % side
            for fc in [fc for fc in act.fcurves if fc.data_path == path]:
                act.fcurves.remove(fc)
            for i in range(4):
                fc = act.fcurves.new(path, index=i, action_group="mixamorig:%sHand" % side)
                fc.keyframe_points.add(len(kk))
                for kp, (f, q) in zip(fc.keyframe_points, kk):
                    kp.co = (f, q[i]); kp.interpolation = 'LINEAR'
                fc.update()
    ad.action = saved
    arm.data.pose_position = 'REST'
    bpy.context.view_layer.update()

def koloss_arms(arm, body, skin, nail, cuff, rim=None, cuff_style="stulpe", size=1.25, fingers=3, claws=False):
    """Arme und Hände aller Bosse auf dem Koloss-Skelett (freigegeben am Nashorn-Krieger, 24.11.): kürzere Arme,
    Unterarm schlanker als Oberarm, Ellenbogen nur nach vorn, eigene Hände mit Daumen innen, Stulpe am Handgelenk"""
    reshape_arms(arm, body)
    fix_elbows(arm)
    cut_hands(body)
    for side in ("Left", "Right"):
        place_in_bone(hand_model("Hand" + side, side, skin, nail, size, fingers, claws), arm, "mixamorig:%sHand" % side)
    wrist_cuffs(arm, body, cuff, rim, cuff_style)
    pose_hands(arm)

def bone_mid(arm, name, t=0.5):
    b = arm.data.bones[name]
    return arm.matrix_world @ (b.head_local.lerp(b.tail_local, t))

@variante("nashorn_krieger", "koloss")
def nashorn(arm, body):
    """Sternenwüste (Welt 7): Nashorn-Krieger – aufrecht gehendes Nashorn mit großem Horn, grauer Faltenhaut,
    Lederrüstung, Sandstein-Schulterpanzern mit Messing und Bronzekragen; kürzere Arme, Unterarm schlanker als Oberarm"""
    hide = look("Nashornhaut", (0.6, 0.58, 0.56), rough=0.75)
    hide_dark = look("NashornhautDunkel", (0.45, 0.43, 0.42), rough=0.8)
    ivory = look("Horn", (0.93, 0.86, 0.7), rough=0.35)
    dark = look("Nuester", (0.1, 0.08, 0.08), rough=0.6)
    eye_w = look("Augenweiss", (1.0, 0.95, 0.75), rough=0.3, emit=(1.0, 0.8, 0.3), strength=0.6)
    stone = look("Sandstein", (0.86, 0.68, 0.42), rough=0.85)
    stone2 = look("Sandstein2", (0.75, 0.56, 0.33), rough=0.85)
    brass = look("Messing", (0.9, 0.66, 0.3), rough=0.3, metal=0.9)
    hoof = look("Hufnagel", (0.3, 0.27, 0.25), rough=0.45)
    leather = look("Lederstulpe", (0.46, 0.3, 0.17), rough=0.8)
    koloss_arms(arm, body, hide, hoof, leather, brass)
    # Kopf: Schädel umschließt den Zombiekopf, Schnauze nach vorn, großes und kleines Horn, Ohren, Augen
    skull = sphere("Schaedel", (0, 0, 0), 0.34, (1.0, 1.12, 0.92)); skull.location = (0, 0.0, 1.47)
    attach(give(skull, hide), arm, "mixamorig:Head")
    snout = sphere("Schnauze", (0, 0, 0), 0.25, (0.88, 1.25, 0.78)); snout.location = (0, -0.36, 1.35)
    attach(give(snout, hide), arm, "mixamorig:Head")
    jaw = sphere("Unterkiefer", (0, 0, 0), 0.2, (0.85, 1.15, 0.5)); jaw.location = (0, -0.33, 1.24)
    attach(give(jaw, hide_dark), arm, "mixamorig:Head")
    for k, (y, r) in enumerate(((-0.2, 0.23), (-0.27, 0.215))):
        fold = torus("Falte%d" % k, (0, y, 1.35), r, 0.018, rot=(90, 0, 0)); fold.scale = (0.9, 1.0, 0.75)
        attach(give(fold, hide_dark), arm, "mixamorig:Head")
    attach(give(horn("GrossesHorn", (0.0, -0.5, 1.46), (0.0, -0.66, 1.62), (0.0, -0.6, 1.93), 0.11, n=14), ivory), arm, "mixamorig:Head")
    attach(give(horn("KleinesHorn", (0.0, -0.3, 1.62), (0.0, -0.38, 1.72), (0.0, -0.34, 1.82), 0.06, n=9), ivory), arm, "mixamorig:Head")
    for s in (-1, 1):
        ear = horn("Ohr%d" % s, (s * 0.2, 0.08, 1.72), (s * 0.3, 0.1, 1.82), (s * 0.34, 0.12, 1.92), 0.06, n=8)
        ear.scale = (1.0, 0.45, 1.0)
        attach(give(ear, hide_dark), arm, "mixamorig:Head")
        attach(give(sphere("Auge%d" % s, (s * 0.21, -0.27, 1.53), 0.045), eye_w), arm, "mixamorig:Head")
        attach(give(sphere("Pupille%d" % s, (s * 0.215, -0.305, 1.53), 0.022), dark), arm, "mixamorig:Head")
        brow = tube("Braue%d" % s, [(s * 0.3, -0.24, 1.6), (s * 0.2, -0.3, 1.58), (s * 0.12, -0.31, 1.55)], [0.035, 0.04, 0.03])
        attach(give(brow, hide_dark), arm, "mixamorig:Head")
        attach(give(sphere("Nuester%d" % s, (s * 0.08, -0.62, 1.33), 0.03, (1, 0.6, 0.7)), dark), arm, "mixamorig:Head")
        # Schulterpanzer wie beim Sand-Koloss
        side = "Left" if s > 0 else "Right"
        c = (s * 0.56, 0.06, 1.3)
        dome = sphere("Panzer%s" % side, (0, 0, 0), 0.24, (1.0, 1.08, 0.5)); dome.location = c; dome.rotation_euler = (0, math.radians(-s * 22), 0)
        attach(give(dome, stone), arm, "mixamorig:%sArm" % side)
        t = torus("Band%s" % side, (c[0], c[1], c[2] - 0.01), 0.225, 0.02, rot=(0, -s * 22, 0)); t.scale = (1.0, 1.08, 1.0)
        attach(give(t, brass), arm, "mixamorig:%sArm" % side)
        for a in range(8):
            ang = a * math.pi / 4
            attach(give(sphere("Niete%s%d" % (side, a), (c[0] + 0.215 * math.cos(ang), c[1] + 0.225 * math.sin(ang), c[2] + 0.04), 0.022), brass),
                   arm, "mixamorig:%sArm" % side)
        # Armschienen aus Messing
        fore = "mixamorig:%sForeArm" % side
        fm = bone_mid(arm, fore, 0.45)
        attach(give(torus("Schiene%s" % side, tuple(fm), 0.1, 0.022, rot=(0, 0, 0)), brass), arm, fore)
    # Haut grau mit Falten, Anzug wird Lederrüstung, Kragen und Gürtel Bronze (Falten zuerst, solange die Haut grün ist)
    skin_lines(body, (0.3, 0.28, 0.27), 55, 0.004, ch=1)
    recolor(body, lambda px: mask_color(px, 1, 0.03, 0.1), (0.62, 0.6, 0.58))
    recolor(body, mask_purple, (0.55, 0.36, 0.2))
    recolor(body, mask_white, (0.82, 0.6, 0.32))

# ---------------------------------------------------------------- Runde 2 (Wunsch 24.11.2026: alle Bosse mit neuen Armen und Händen)

def skin_color(body, ch=1):
    """mittlere Hautfarbe (Stellen, an denen Kanal ch vorherrscht) als sRGB, z. B. für die neuen Hände"""
    m, tex, img, px = body_texture(body)
    k = mask_color(px, ch) > 0.5
    return tuple(float(v) for v in px[k][:, :3].mean(0))

def surface(body, origin, toward):
    """Punkt und Normale auf der Körperoberfläche (Ruhehaltung): Strahl von origin in Richtung toward"""
    from mathutils.bvhtree import BVHTree
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    bvh = BVHTree.FromObject(body, dg)
    mw = body.matrix_world; inv = mw.inverted()
    loc, nor, idx, dist = bvh.ray_cast(inv @ Vector(origin), (inv.to_3x3() @ Vector(toward)).normalized())
    if loc is None:
        return None, None
    return mw @ loc, (mw.to_3x3() @ nor).normalized()

def on_surface(body, center, dirs, lift=0.006):
    """Punkte auf der Oberfläche um center in den Richtungen dirs (von außen nach innen gesucht)"""
    out = []
    for d in dirs:
        d = Vector(d).normalized()
        p, n = surface(body, Vector(center) + d * 1.5, -d)
        if p is not None:
            out.append((p + n * lift, n))
    return out

def stitched_scar(name, body, center, dirs, line_m, arm, bone, r=0.011, stitch=0.03, every=2):
    """genähte Narbe: Linie über die Oberfläche mit Querstichen"""
    hits = on_surface(body, center, dirs)
    pts = [tuple(p) for p, n in hits]
    attach(give(tube(name, pts, [r] * len(pts), segs=8), line_m), arm, bone)
    for i in range(0, len(hits), every):
        p, n = hits[i]
        t = (hits[min(i + 1, len(hits) - 1)][0] - hits[max(i - 1, 0)][0]).normalized()
        c = t.cross(n).normalized()
        attach(give(tube("%sStich%d" % (name, i), [tuple(p - c * stitch + n * 0.004), tuple(p + n * 0.01), tuple(p + c * stitch + n * 0.004)],
                         [r * 0.8] * 3, segs=6), line_m), arm, bone)

def patch_on(name, body, origin, toward, size, mat, stitch_m, arm, bone, spin=0.0, rivets=False):
    """aufgenähter Flicken (flache Platte mit Stichen am Rand) auf der Oberfläche; rivets: Blech mit Nieten"""
    p, n = surface(body, origin, toward)
    up = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((0, 1, 0))
    a = n.cross(up).normalized(); b = n.cross(a).normalized()
    ca, sa = math.cos(spin), math.sin(spin)
    a, b = a * ca + b * sa, b * ca - a * sa
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = p + n * 0.006 + a * v.co.x * size[0] + b * v.co.y * size[1] + n * v.co.z * 0.016
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.006, segments=2, affect='EDGES')
    o = give(finish(name, bm), mat)
    attach(o, arm, bone)
    if rivets:
        for k, (ex, ey) in enumerate(((0.38, 0.36), (-0.38, 0.36), (0.38, -0.36), (-0.38, -0.36))):
            attach(give(sphere("%sNiete%d" % (name, k), tuple(p + n * 0.02 + a * ex * size[0] + b * ey * size[1]), 0.014), stitch_m), arm, bone)
        return
    k = 0
    for ex, ey, ax in ((0.5, None, b), (-0.5, None, b), (None, 0.5, a), (None, -0.5, a)):
        for t in (-0.3, 0.0, 0.3):
            c = p + n * 0.016 + (a * ex * size[0] + b * t * size[1] if ex is not None else b * ey * size[1] + a * t * size[0])
            attach(give(tube("%sStich%d" % (name, k), [tuple(c - ax * 0.018), tuple(c + n * 0.004), tuple(c + ax * 0.018)], [0.006] * 3, segs=6), stitch_m), arm, bone)
            k += 1

@variante("zombie_koloss", "koloss")
def zombie_koloss(arm, body):
    """Zombie-Kolonie (Welt 2): Zombie-Koloss – der bekannte Koloss mit neuen Armen und Händen (Binden an den
    Handgelenken), genähten Narben am Kopf, Flicken am Bein, Leuchtpilzen auf der Schulter, giftgrün
    leuchtenden Augen und dunklen Flecken auf der Haut"""
    skin = look("ZombieHaut", skin_color(body), rough=0.7)
    nail = look("ZombieNagel", (0.25, 0.2, 0.18), rough=0.5)
    bandage = look("Binde", (0.86, 0.82, 0.68), rough=0.85)
    thread = look("Faden", (0.16, 0.08, 0.12), rough=0.7)
    patch = look("Flicken", (0.8, 0.7, 0.88), rough=0.8)
    patch2 = look("Flicken2", (0.5, 0.58, 0.36), rough=0.8)
    tin = look("Blech", (0.55, 0.52, 0.5), rough=0.4, metal=0.7)
    rust = look("Rost", (0.55, 0.32, 0.18), rough=0.6, metal=0.4)
    stalk = look("Pilzstiel", (0.9, 0.88, 0.76), rough=0.6)
    glowcap = look("Leuchtpilz", (0.55, 1.0, 0.3), rough=0.35, emit=(0.45, 1.0, 0.2), strength=1.6)
    koloss_arms(arm, body, skin, nail, bandage, cuff_style="binde")
    head = arm.data.bones["mixamorig:Head"]
    hc = arm.matrix_world @ (head.head_local + (head.tail_local - head.head_local) * 0.35)
    stitched_scar("NarbeKopf", body, hc, [(-0.75, -0.45, 0.45), (-0.55, -0.5, 0.65), (-0.3, -0.5, 0.82), (-0.05, -0.45, 0.9),
                                          (0.2, -0.35, 0.92), (0.42, -0.2, 0.88)], thread, arm, "mixamorig:Head", r=0.015, stitch=0.038)
    stitched_scar("NarbeWange", body, hc, [(0.75, -0.62, 0.05), (0.7, -0.66, -0.12), (0.62, -0.7, -0.28)], thread, arm, "mixamorig:Head", r=0.012, stitch=0.03, every=1)
    patch_on("BlechKopf", body, hc + Vector((-1.2, -0.3, 0.5)), (1.0, 0.25, -0.42), (0.13, 0.11), tin, rust, arm, "mixamorig:Head", spin=0.4, rivets=True)
    # Flicken auf der Brust entfernt (Kommentar 24.11.: silberne Plakette weg)
    hip = arm.matrix_world @ arm.data.bones["mixamorig:RightUpLeg"].head_local
    patch_on("FlickenBein", body, (hip.x - 0.02, hip.y - 1.5, hip.z - 0.22), (0, 1, 0), (0.12, 0.11), patch2, thread, arm, "mixamorig:RightUpLeg", spin=-0.35)
    sh = arm.matrix_world @ arm.data.bones["mixamorig:LeftArm"].head_local
    for i, (dx, dy, h, r) in enumerate(((0.02, 0.02, 0.17, 0.095), (0.12, 0.11, 0.12, 0.07), (-0.08, 0.12, 0.09, 0.055), (0.13, -0.07, 0.08, 0.045))):
        p, n = surface(body, (sh.x + dx, sh.y + dy, sh.z + 1.0), (0, 0, -1))
        if p is None:
            continue
        attach(give(tube("PilzStiel%d" % i, [tuple(p - n * 0.02), tuple(p + n * h * 0.5), tuple(p + n * h)], [r * 0.32, r * 0.28, r * 0.26]), stalk), arm, "mixamorig:LeftShoulder")
        cap_ = sphere("PilzHut%d" % i, (0, 0, 0), r, (1, 1, 0.6)); cap_.location = p + n * h
        attach(give(cap_, glowcap), arm, "mixamorig:LeftShoulder")
    speckles(body, 1, (0.22, 0.32, 0.1), 0.32, 14, seed=51)
    recolor(body, mask_yellow, (0.6, 1.0, 0.3), glow=1.1, strength=2.0)

def cut_head(body, bone="mixamorig:Head", keep="mixamorig:Neck"):
    """Kopf des Grundmodells entfernen (für einen ganz eigenen Kopf); liefert Mitte und halbe Ausdehnung des alten
    Kopfes (Welt), damit der neue Kopf ihn sicher abdeckt"""
    gi = body.vertex_groups[bone].index; ki = body.vertex_groups[keep]
    mw = body.matrix_world
    kill, pts = [], []
    for v in body.data.vertices:
        w = sum(g.weight for g in v.groups if g.group == gi)
        if w > 0.5:
            kill.append(v.index); pts.append(mw @ v.co)
        elif w > 0:
            ki.add([v.index], w + sum(g.weight for g in v.groups if g.group == ki.index), 'REPLACE')
            body.vertex_groups[bone].remove([v.index])
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    bm = bmesh.new(); bm.from_mesh(body.data); bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.verts[i] for i in kill], context='VERTS')
    bm.to_mesh(body.data); bm.free(); body.data.update()
    return (lo + hi) / 2, (hi - lo) / 2

def mask_colored(px, sat=0.12):
    """alle deutlich farbigen Stellen (nicht weiß, nicht grau)"""
    return np.clip((px[..., :3].max(-1) - px[..., :3].min(-1) - sat) / 0.08, 0, 1)

def fur_recolor(body, mask, color, seed=61, strength=0.16):
    """Stellen der Maske zu Fell umfärben: Grundfarbe mit feinen Strähnen (gestreckte Rauschzellen) und Tiefe"""
    m, tex, img, px = body_texture(body)
    h, w = px.shape[:2]
    k = mask(px)[..., None]
    fine = fbm(h, w, 90, seed, octaves=2)
    lum = (0.3 * px[..., 0] + 0.6 * px[..., 1] + 0.1 * px[..., 2])[..., None]
    c = np.array(color, dtype=np.float32)
    shade = 0.9 + (lum - 0.5) * 0.18 + (fine[..., None] - 0.5) * strength
    new = np.clip(c * shade, 0, 1)
    base = px.copy(); base[..., :3] = base[..., :3] * (1 - k) + new * k
    tex.image = new_image(body.name + "_Farbe", base)

def fur_tufts(name, pts, mat, arm, bone, r=0.06, length=0.12, seed=3):
    """Fellbüschel: spitze, leicht gebogene Strähnen an Punkten (Punkt, Normale), zu einem Objekt verbunden"""
    rnd = random.Random(seed)
    parts = []
    for i, (p, n) in enumerate(pts):
        side = n.cross(Vector((0, 0, 1)))
        if side.length < 0.1:
            side = n.cross(Vector((0, 1, 0)))
        side.normalize()
        down = Vector((0, 0, -0.35))
        L = length * rnd.uniform(0.75, 1.25)
        d = (n + down + side * rnd.uniform(-0.4, 0.4)).normalized()
        rr = r * rnd.uniform(0.85, 1.15)
        parts.append(give(tube("%s%d" % (name, i), [tuple(p - n * 0.02), tuple(p + d * L * 0.35), tuple(p + d * L * 0.7 + down * L * 0.2),
                                                   tuple(p + d * L + down * L * 0.45)], [rr, rr * 0.85, rr * 0.45, 0.0], segs=10), mat))
    o = join_parts(parts, name)
    return attach(o, arm, bone)

def ring_dirs(n, z, spread=1.0, phase=0.0):
    return [(math.cos(phase + i * 2 * math.pi / n) * spread, math.sin(phase + i * 2 * math.pi / n) * spread, z) for i in range(n)]

@variante("frost_yeti", "koloss")
def frost_yeti(arm, body):
    """Frostmond (Welt 3): Frost-Yeti – großer weißer Yeti mit dichtem Fell, blaugrauem Gesicht, eisblau leuchtenden
    Augen, eingerollten Eishörnern, Eiszapfen an den Schultern, Eiskristallen auf dem Rücken und Pranken mit Krallen.
    Eigene Figur auf dem Koloss-Skelett."""
    fur = look("Fell", (0.9, 0.94, 1.0), rough=0.9)
    fur2 = look("FellSchatten", (0.76, 0.84, 0.95), rough=0.9)
    face = look("YetiGesicht", (0.56, 0.64, 0.78), rough=0.6)
    face_dark = look("YetiDunkel", (0.12, 0.14, 0.22), rough=0.5)
    claw = look("Kralle", (0.16, 0.17, 0.25), rough=0.35)
    eye = look("EisAuge", (0.7, 0.95, 1.0), rough=0.2, emit=(0.45, 0.85, 1.0), strength=3.0)
    fang = look("Fangzahn", (0.97, 0.97, 0.94), rough=0.3)
    horn_m = look("Eishorn", (0.62, 0.72, 0.86), rough=0.25)
    ice = look("Eis", (0.8, 0.94, 1.0), rough=0.08, emit=(0.55, 0.85, 1.0), strength=0.45)
    ice_deep = look("EisTief", (0.42, 0.7, 0.98), rough=0.1, emit=(0.35, 0.7, 1.0), strength=0.7)
    koloss_arms(arm, body, face, claw, fur, cuff_style="fell", size=1.3, fingers=4, claws=True)
    # Fell überall, wo Anzug oder Haut war; Kragen wird Eis
    fur_recolor(body, mask_colored, (0.86, 0.91, 1.0))
    recolor(body, mask_white, (0.72, 0.88, 1.0), glow=0.25, strength=0.6)
    # Kopf ganz neu: alter Kopf wird entfernt; Fellkugel, Gesicht, Augen, Nase, Maul mit Fangzähnen, Hörner, Schopf
    c0, half = cut_head(body)
    H = "mixamorig:Head"
    R = max(half.x, half.z) * 1.02
    hc = c0 + Vector((0, 0.02, 0.02))
    skull = sphere("YetiKopf", (0, 0, 0), R, (1.08, 1.0, 1.0)); skull.location = hc
    attach(give(skull, fur), arm, H)
    fy = hc.y - R * 0.98                                         # Vorderseite des Kopfes
    F = lambda x, dy, z: tuple(Vector((hc.x + x, fy + dy, hc.z + z)))
    mask_ = sphere("Gesicht", (0, 0, 0), R * 0.7, (1.1, 0.42, 0.9)); mask_.location = F(0, 0.1, -0.04)
    attach(give(mask_, face), arm, H)
    muzzle = sphere("Schnauze", (0, 0, 0), R * 0.42, (1.3, 0.62, 0.72)); muzzle.location = F(0, -0.02, -0.14)
    attach(give(muzzle, face), arm, H)
    attach(give(sphere("Nase", F(0, -0.1, -0.08), 0.045, (1.3, 0.8, 0.8)), face_dark), arm, H)
    mouth = sphere("Maul", (0, 0, 0), 0.1, (1.4, 0.4, 0.45)); mouth.location = F(0, -0.07, -0.21)
    attach(give(mouth, face_dark), arm, H)
    for s in (-1, 1):
        attach(give(tube("Fang%d" % s, [F(s * 0.08, -0.1, -0.25), F(s * 0.085, -0.12, -0.19), F(s * 0.09, -0.12, -0.14)], [0.028, 0.018, 0.0]), fang), arm, H)
        attach(give(sphere("Augenhoehle%d" % s, F(s * 0.12, 0.0, 0.05), 0.065, (1.1, 0.6, 0.8)), face_dark), arm, H)
        attach(give(sphere("Auge%d" % s, F(s * 0.12, -0.025, 0.05), 0.046, (1.1, 0.6, 0.85)), eye), arm, H)
        attach(give(sphere("Pupille%d" % s, F(s * 0.115, -0.05, 0.045), 0.018), face_dark), arm, H)
        brow = tube("Braue%d" % s, [F(s * 0.22, 0.04, 0.14), F(s * 0.12, -0.03, 0.13), F(s * 0.03, -0.03, 0.1)], [0.045, 0.05, 0.035])
        attach(give(brow, fur), arm, H)
        # eingerolltes Horn: von der Schläfe nach außen, oben und zurück eingerollt
        pts = []; radii = []
        for i in range(14):
            t = i / 13
            a = t * 1.5 * math.pi
            Rh = 0.17 * (1 - 0.45 * t)
            pts.append(tuple(hc + Vector((s * (R * 0.82 + 0.09 * t), 0.02 + math.sin(a) * Rh, R * 0.45 + (1 - math.cos(a)) * Rh * 0.85 - 0.04))))
            radii.append(0.07 * (1 - t) + 0.008)
        radii[-1] = 0.0
        attach(give(tube("Horn%d" % s, pts, radii), horn_m), arm, H)
    top = [(p, n) for p, n in on_surface_sphere(hc, R, [(-0.2, -0.2, 1), (0.0, -0.1, 1), (0.2, -0.15, 1), (-0.1, 0.15, 1), (0.12, 0.2, 1)])]
    fur_tufts("Schopf", top, fur, arm, H, r=0.07, length=0.16, seed=5)
    # Fellbüschel an Schultern, Brust und Rücken
    sp = arm.matrix_world @ arm.data.bones["mixamorig:Spine2"].head_local
    for s, side in ((1, "Left"), (-1, "Right")):
        sh = arm.matrix_world @ arm.data.bones["mixamorig:%sArm" % side].head_local
        pts = on_surface(body, sh, [(s * 0.6, y, 1.0) for y in (-0.5, -0.2, 0.1, 0.4)] + [(s * 1.0, y, 0.2) for y in (-0.3, 0.1, 0.4)])
        fur_tufts("FellSchulter" + side, pts, fur2, arm, "mixamorig:%sArm" % side, r=0.09, length=0.13, seed=11 + s)
        ua = arm.data.bones["mixamorig:%sArm" % side]
        mid = arm.matrix_world @ (ua.head_local * 0.4 + ua.tail_local * 0.6)
        pts = on_surface(body, mid, [(s * 1.0, -0.3, 0), (s * 1.0, 0.3, 0), (s * 0.6, 0.8, 0)])
        fur_tufts("FellOberarm" + side, pts, fur, arm, "mixamorig:%sArm" % side, r=0.06, length=0.13, seed=21 + s)
        # Eiszapfen unter dem Schulterfell
        for i, (dx, dy) in enumerate(((0.05, -0.12), (0.12, 0.0), (0.06, 0.12))):
            p, n = surface(body, (sh.x + s * dx, sh.y + dy, sh.z + 1.0), (0, 0, -1))
            if p is None:
                continue
            L = 0.12 + 0.05 * (i % 2)
            attach(give(tube("Zapfen%s%d" % (side, i), [tuple(p + Vector((s * 0.12, 0, -0.06))), tuple(p + Vector((s * 0.13, 0, -0.06 - L * 0.4))),
                                                        tuple(p + Vector((s * 0.14, 0, -0.06 - L)))], [0.03, 0.018, 0.0]), ice), arm, "mixamorig:%sArm" % side)
    pts = on_surface(body, sp, [(x, -1.0, z) for x, z in ((-0.35, 0.55), (0.0, 0.6), (0.35, 0.55), (-0.2, 0.25), (0.2, 0.25))])
    fur_tufts("FellBrust", pts, fur, arm, "mixamorig:Spine2", r=0.07, length=0.14, seed=31)
    pts = on_surface(body, sp, [(x, 1.0, z) for x, z in ((-0.4, 0.5), (0.0, 0.6), (0.4, 0.5), (-0.3, 0.1), (0.3, 0.1), (0.0, 0.2))])
    fur_tufts("FellRuecken", pts, fur2, arm, "mixamorig:Spine2", r=0.08, length=0.16, seed=41)
    for k, (x, z, h, r, tx, ty) in enumerate(((0.0, 0.3, 0.36, 0.08, -35, 0), (-0.2, 0.18, 0.26, 0.065, -40, -25),
                                              (0.2, 0.18, 0.26, 0.065, -40, 25), (0.0, -0.02, 0.2, 0.05, -55, 0))):
        p, n = surface(body, (sp.x + x, sp.y + 1.5, sp.z + z), (0, -1, 0))
        if p is not None:
            attach(give(crystal("RueckenEis%d" % k, tuple(p - n * 0.03), h, r, (tx, ty, 0)), ice_deep if k % 2 == 0 else ice), arm, "mixamorig:Spine2")

def on_surface_sphere(center, r, dirs):
    out = []
    for d in dirs:
        d = Vector(d).normalized()
        out.append((Vector(center) + d * r, d))
    return out

def chunk_between(name, p0, p1, radius, mat, seed=0, flat=False, subdiv=2, depth=0.9, stretch=1.1):
    """Block (Stein, Kristall) entlang einer Strecke p0→p1, Längsachse in Richtung der Strecke"""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    o = rock(name, (0, 0, 0), 1.0, (radius, d.length / 2 * stretch, radius * depth), seed=seed, subdiv=subdiv)
    if flat:
        for pl in o.data.polygons:
            pl.use_smooth = False
    o.matrix_world = Matrix.Translation((p0 + p1) / 2) @ d.normalized().to_track_quat('Y', 'Z').to_matrix().to_4x4()
    return give(o, mat)

def block_at(name, c, semi, mat, seed=0, flat=False, subdiv=2):
    o = rock(name, tuple(c), 1.0, semi, seed=seed, subdiv=subdiv)
    if flat:
        for pl in o.data.polygons:
            pl.use_smooth = False
    return give(o, mat)

def carve(obj, cutter, mat):
    """Form aus einem Teil herausschneiden (Boolean); die neuen Innenflächen bekommen mat"""
    give(cutter, mat)
    if mat.name not in [m.name for m in obj.data.materials]:
        obj.data.materials.append(mat)
    mod = obj.modifiers.new("Schnitt", 'BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.object = cutter; mod.solver = 'EXACT'
    mod.material_mode = 'TRANSFER'
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True); bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)
    for pl in obj.data.polygons:
        pl.use_smooth = False

def golem_face(skull, jaw, hc, m, crystal_teeth=False):
    """Gesicht der Golems (Kommentare 24.11.: klare Augen und Maul, eingepasst statt einfacher Formen):
    Augenhöhlen und Maul sind aus Schädel und Kiefer herausgeschnitten; in den Höhlen liegen glühende, schräg
    gestellte Augen mit hellem Kern, darüber kantige Brauen; im Maul glüht das Innere, oben und unten sitzen Zähne;
    Leuchtrisse laufen von den Augen über die Wangen. m: Materialien socket, eye, core, mouth, tooth, brow, crack.
    Liefert die zusätzlichen Teile (Augen, Brauen, Zähne, Risse)."""
    parts = []
    eyes = {}
    for s_ in (-1, 1):
        p, n = surface(skull, (s_ * 0.095, -2.0, hc.z + 0.035), (0, 1, 0))
        eyes[s_] = (p, n)
        cut = sphere("Augenschnitt%d" % s_, (0, 0, 0), 0.062, (1.35, 1.0, 0.78), segs=(24, 14))
        cut.location = p - n * 0.012; cut.rotation_euler = (0, math.radians(-s_ * 18), 0)   # innen tiefer: böse (Kommentar 24.11.)
        carve(skull, cut, m["socket"]); bpy.data.objects.remove(cut)
    pm, nm = surface(jaw, (0.0, -2.0, hc.z - 0.135), (0, 1, 0))
    for o in (jaw, skull):
        cut = sphere("Maulschnitt", (0, 0, 0), 0.13, (1.15, 0.75, 0.42), segs=(28, 14))
        cut.location = pm - nm * 0.022
        carve(o, cut, m["mouth"]); bpy.data.objects.remove(cut)
    for s_, (p, n) in eyes.items():
        e = sphere("Auge%d" % s_, (0, 0, 0), 0.046, (1.3, 0.55, 0.66), segs=(32, 16)); e.location = p - n * 0.028; e.rotation_euler = (0, math.radians(-s_ * 18), 0)
        give(e, m["eye"])
        # böser Blick ohne verdeckende Braue (Kommentar 24.11.): Auge oben schräg abgeschnitten, innen tiefer
        bmc = bmesh.new(); bmesh.ops.create_cube(bmc, size=0.3)
        lid = finish("Lidschnitt%d" % s_, bmc, smooth=False)
        rot = Matrix.Rotation(math.radians(-s_ * 26), 4, 'Y')
        lid.matrix_world = Matrix.Translation(e.location) @ rot @ Matrix.Translation((0, 0, 0.15 + 0.006))
        carve(e, lid, m["eye"]); bpy.data.objects.remove(lid)
        parts.append(e)
        parts.append(give(sphere("Augenkern%d" % s_, tuple(p - n * 0.012 + Vector((-s_ * 0.012, 0, -0.008))), 0.017, (1.2, 0.6, 1.0)), m["core"]))
        # schmale Braue knapp über der Augenhöhle, innen tiefer (böse), verdeckt das Auge nicht (Kommentar 24.11.)
        brow = chunk_between("Braue%d" % s_, p + Vector((s_ * 0.1, -0.004, 0.082)), p + Vector((-s_ * 0.04, -0.01, 0.05)), 0.022, m["brow"], seed=60 + s_, flat=True, subdiv=1, depth=0.75)
        parts.append(brow)
        # Riss (Kommentar 24.11.: realistischer): gezackte, dünner werdende Linie mit kleinem Abzweig
        rnd = random.Random(80 + s_)
        crack = []
        for k in range(10):
            t = k / 9
            q, qn = surface(skull, (s_ * (0.1 + 0.055 * t) + rnd.uniform(-0.011, 0.011), -2.0, hc.z - 0.012 - 0.12 * t), (0, 1, 0))
            if q is not None:
                crack.append((q + qn * 0.0015, t))
        if len(crack) > 3:
            parts.append(give(tube("Riss%d" % s_, [tuple(c) for c, t in crack], [0.0065 * (1 - t) + 0.0022 for c, t in crack[:-1]] + [0.0], segs=6), m["crack"]))
            b0 = crack[4][0]
            br = []
            for k in range(4):
                q, qn = surface(skull, (b0.x + s_ * (0.012 + 0.014 * k), -2.0, b0.z - 0.01 * k + rnd.uniform(-0.004, 0.004)), (0, 1, 0))
                if q is not None:
                    br.append(tuple(q + qn * 0.0015))
            if len(br) > 2:
                parts.append(give(tube("RissAst%d" % s_, br, [0.0035] * (len(br) - 1) + [0.0], segs=6), m["crack"]))
    # Zähne genau am Rand der Maulöffnung (Kommentar 24.11.: sauber im Mundraum): Rand je Zahn ausmessen – Strahlen
    # von vorn, oberhalb/unterhalb der Maulmitte; wo der Strahl nicht mehr ins Maulinnere trifft, liegt der Rand
    from mathutils.bvhtree import BVHTree
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    trees = [(o, BVHTree.FromObject(o, dg)) for o in (skull, jaw)]

    def front_hit(x, z):
        best = None
        for o, bvh in trees:
            mw = o.matrix_world; inv = mw.inverted()
            loc, nor, idx, dist = bvh.ray_cast(inv @ Vector((x, -2.0, z)), (inv.to_3x3() @ Vector((0, 1, 0))).normalized())
            if loc is None:
                continue
            w = mw @ loc
            if best is None or w.y < best[0].y:
                best = (w, o.data.materials[o.data.polygons[idx].material_index].name == m["mouth"].name)
        return best

    def rim(x, sign):
        z = pm.z
        for _ in range(60):
            z += sign * 0.0025
            h = front_hit(x, z)
            if h is None or not h[1]:
                return Vector((x, h[0].y if h else pm.y, z - sign * 0.0025))
        return None
    for i, x in enumerate((-0.09, -0.03, 0.03, 0.09)):
        t, b_ = rim(x, 1), rim(x, -1)
        if t is None or b_ is None:
            continue
        gap = t.z - b_.z
        L = gap * (0.4 if i in (0, 3) else 0.33)
        parts.append(shard("Oberzahn%d" % i, t + Vector((0, 0.012, 0.006)), (x * 0.3, -0.22, -1), L, 0.022, m["tooth"]))
    for i, x in enumerate((-0.06, 0.0, 0.06)):
        t, b_ = rim(x, 1), rim(x, -1)
        if t is None or b_ is None:
            continue
        gap = t.z - b_.z
        parts.append(shard("Unterzahn%d" % i, b_ + Vector((0, 0.012, -0.006)), (x * 0.3, -0.22, 1), gap * 0.3, 0.019, m["tooth"]))
    if "throat" in m:
        parts.append(give(sphere("Rachen", tuple(pm + Vector((0, 0.06, 0.0))), 0.05, (1.6, 0.6, 0.7)), m["throat"]))
    return parts

def lengthen_legs(arm, factor):
    """Beine länger (Kommentar 24.11. zum Kristallriesen): Ober- und Unterschenkel um factor verlängert, das ganze
    Skelett so weit angehoben, dass die Füße wieder auf dem Boden stehen. Richtungen und Drehungen der Knochen bleiben,
    damit alle Bewegungen weiter passen. Nur für Bosse ohne Hautkörper (Golems)."""
    bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones
    up_ = eb["mixamorig:LeftUpLeg"]; lo_ = eb["mixamorig:LeftLeg"]
    dz = (factor - 1) * ((up_.head.z - up_.tail.z) + (lo_.head.z - lo_.tail.z))
    for b in eb:
        b.use_connect = False
    for b in eb:
        b.head.z += dz; b.tail.z += dz
    for side in ("Left", "Right"):
        up_, lo_ = eb["mixamorig:%sUpLeg" % side], eb["mixamorig:%sLeg" % side]
        old_ankle = lo_.tail.copy()
        up_.tail = up_.head + (up_.tail - up_.head) * factor
        d = lo_.tail - lo_.head
        lo_.head = up_.tail.copy(); lo_.tail = lo_.head + d * factor
        shift = lo_.tail - old_ankle
        for b in eb:
            if b.name.startswith("mixamorig:%s" % side) and any(k in b.name for k in ("Foot", "Toe")):
                b.head += shift; b.tail += shift
        for b in eb:                                          # Zusatzknochen am Fuß (Bone_005 u. a.) mitnehmen
            if b.parent is not None and b.parent.name == "mixamorig:%sFoot" % side and not b.name.startswith("mixamorig:"):
                b.head += shift; b.tail += shift
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.update()

def shard(name, base, direction, h, r, mat):
    """Kristallsplitter mit Fuß bei base, Spitze in Richtung direction"""
    o = crystal(name, (0, 0, 0), h, r)
    o.location = base
    o.rotation_euler = Vector(direction).normalized().to_track_quat('Z', 'Y').to_euler()
    return give(o, mat)

def shard_on(name, obj, guess, direction, h, r, mat, depth=0.035):
    """Splitter, dessen Fuß in der Oberfläche von obj steckt (Kommentar 24.11.: Kristalle liegen am Körper an):
    Strahl von außen entlang direction auf obj, Fuß depth unter der Oberfläche"""
    d = Vector(direction).normalized()
    p, n = surface(obj, Vector(guess) + d * 0.8, -d)
    base = (p - n * depth) if p is not None else Vector(guess)
    return shard(name, base, d, h, r, mat)

def obj_named(objs, prefix):
    return next(o for o in objs if o.name.startswith(prefix))

def crystal_joint(name, c, r, axis, glow_m, mats, seed=0, n=5):
    """Gelenk als facettierter Leuchtkristall mit Splittern ringsum, die schräg nach außen stehen (Kommentar 24.11.:
    keine runden Kugeln, Gelenke fließen in die Kristallform über)"""
    rnd = random.Random(seed)
    ax = Vector(axis).normalized()
    side = ax.cross(Vector((0, 0, 1)))
    if side.length < 0.1:
        side = ax.cross(Vector((1, 0, 0)))
    side.normalize(); up = ax.cross(side).normalized()
    out = [block_at(name, c, (r * 0.78, r * 0.78, r * 0.78), glow_m, seed, True, 1)]
    for k in range(n):
        a = k * 2 * math.pi / n + rnd.uniform(-0.3, 0.3)
        d = side * math.cos(a) + up * math.sin(a)
        out.append(shard("%sSplitter%d" % (name, k), c + d * r * 0.55, d + ax * rnd.uniform(-0.5, 0.5), r * rnd.uniform(0.9, 1.4), r * 0.3, mats[k % len(mats)]))
    return out

def golem_body(arm, body, rock_m, rock2_m, joint_m, flat=False, subdiv=2, fist_m=None, nail_m=None, legs=1.0, spiky=False):
    """Körper aus Blöcken am Koloss-Skelett (Magma-Golem, Kristallriese): Becken, Bauch, Brust, Schulterblöcke,
    Ober- und Unterarme (Unterarm schlanker), Fäuste, Beine, Füße, leuchtende Gelenke. Arme wie beim Nashorn-Krieger
    (kürzer, Ellenbogen nur nach vorn, Hände mit Daumen innen). Teile je Knochen zu einem Objekt verbunden.
    Liefert ein Wörterbuch mit Lagen (Brust, Kopf, Schultern) für die Aufsätze. legs > 1: längere Beine.
    spiky: Kristallgelenke statt Glutkugeln und Kristallsplitter an Armen, Beinen und Brust (Kristallriese)."""
    reshape_arms(arm, body)
    if legs != 1.0:
        lengthen_legs(arm, legs)
    fix_elbows(arm)
    W = lambda bone, t=0.0: arm.matrix_world @ (arm.data.bones[bone].head_local.lerp(arm.data.bones[bone].tail_local, t))
    B = lambda n: "mixamorig:" + n
    parts = {}
    add = lambda bone, o: parts.setdefault(B(bone), []).append(o)
    m2 = lambda i: rock_m if i % 2 == 0 else rock2_m
    hips, sp, sp1, sp2, neck, head = W(B("Hips")), W(B("Spine")), W(B("Spine1")), W(B("Spine2")), W(B("Neck")), W(B("Head"))
    add("Hips", block_at("Becken", hips + Vector((0, 0.03, 0.0)), (0.36, 0.26, 0.2), rock2_m, 1, flat, subdiv))
    add("Spine", block_at("Bauch", (sp + sp1) / 2 + Vector((0, -0.02, 0.0)), (0.36, 0.28, 0.2), rock_m, 2, flat, subdiv))
    chest = Vector((0, sp2.y + 0.02, sp2.z + 0.0))
    add("Spine2", block_at("BrustLinks", chest + Vector((0.2, -0.04, 0.0)), (0.3, 0.3, 0.24), rock_m, 3, flat, subdiv))
    add("Spine2", block_at("BrustRechts", chest + Vector((-0.2, -0.04, 0.0)), (0.3, 0.3, 0.24), rock2_m, 4, flat, subdiv))
    add("Spine2", block_at("Ruecken", chest + Vector((0, 0.18, 0.04)), (0.46, 0.22, 0.27), rock2_m, 5, flat, subdiv))
    add("Spine2", block_at("Nacken", Vector((0, neck.y + 0.08, neck.z - 0.02)), (0.26, 0.17, 0.1), rock_m, 6, flat, subdiv))
    if spiky:
        for k, (x, z, dx, dz, h) in enumerate(((0.34, 0.14, 0.7, 0.9, 0.16), (-0.34, 0.14, -0.7, 0.9, 0.16), (0.42, -0.06, 1.0, 0.3, 0.13),
                                               (-0.42, -0.06, -1.0, 0.3, 0.13), (0.22, -0.2, 0.5, -0.4, 0.11), (-0.22, -0.2, -0.5, -0.4, 0.11))):
            blk = obj_named(parts[B("Spine2")], "BrustLinks" if x > 0 else "BrustRechts")
            add("Spine2", shard_on("BrustSplitter%d" % k, blk, chest + Vector((x * 0.8, -0.05, z)), (dx, -0.35, dz), h, 0.035, rock_m if k % 2 else rock2_m))
    mats = [rock_m, rock2_m]

    def joint(bone, name, c, r, axis, squash=(1, 1, 1), seed=0):
        if spiky:
            for o in crystal_joint(name, c, r * max(squash), axis, joint_m, mats, seed=seed, n=6 if r > 0.2 else 5):
                add(bone, o)
        else:
            add(bone, give(sphere(name, tuple(c), r, squash), joint_m))
    joint("Spine", "GlutTaille", sp + Vector((0, 0.0, -0.02)), 0.24 if not spiky else 0.17, (0, 0, 1), (1.25, 1.0, 0.6) if not spiky else (1, 1, 1), 70)
    joint("Neck", "GlutHals", neck, 0.13, (0, 0, 1), seed=71)
    for s, side in ((1, "Left"), (-1, "Right")):
        a0, a1 = W(B(side + "Arm")), W(B(side + "Arm"), 1.0)
        f0, f1 = W(B(side + "ForeArm")), W(B(side + "ForeArm"), 1.0)
        add(side + "Arm", block_at("Schulter" + side, a0 + Vector((s * 0.06, 0.0, 0.08)), (0.24, 0.24, 0.2), rock_m, 10 + s, flat, subdiv))
        add(side + "Arm", chunk_between("Oberarm" + side, a0.lerp(a1, 0.12), a1, 0.16, rock2_m, 12 + s, flat, subdiv))
        joint(side + "Arm", "GlutSchulter" + side, a0, 0.14, a1 - a0, seed=72 + s)
        joint(side + "ForeArm", "GlutEllbogen" + side, f0, 0.11, f1 - f0, seed=74 + s)
        add(side + "ForeArm", chunk_between("Unterarm" + side, f0.lerp(f1, 0.18), f1.lerp(f0, 0.05), 0.12, rock_m, 14 + s, flat, subdiv))
        add(side + "ForeArm", chunk_between("Unterarm2" + side, f0.lerp(f1, 0.55), f1.lerp(f0, 0.0), 0.135, rock2_m, 16 + s, flat, subdiv, stretch=0.6))
        u0, u1 = W(B(side + "UpLeg")), W(B(side + "UpLeg"), 1.0)
        l1 = W(B(side + "Leg"), 1.0)
        ft0, ft1 = W(B(side + "Foot")), W(B(side + "Foot"), 1.0)
        joint(side + "UpLeg", "GlutHuefte" + side, u0, 0.13, u1 - u0, seed=76 + s)
        add(side + "UpLeg", chunk_between("Oberschenkel" + side, u0 + Vector((s * 0.02, 0, 0.04)), u1, 0.19, rock_m, 20 + s, flat, subdiv, stretch=1.35))
        joint(side + "Leg", "GlutKnie" + side, u1, 0.12, l1 - u1, seed=78 + s)
        add(side + "Leg", chunk_between("Schienbein" + side, u1.lerp(l1, 0.12), l1, 0.165, rock2_m, 22 + s, flat, subdiv, stretch=1.2))
        if spiky:
            # Kristallfuß (Kommentar 24.11.: soll einen Fuß abbilden): flache Sohle, Spann, Ferse, drei Kristallzehen
            ground = min(ft0.z, ft1.z) - 0.005
            fwd = Vector((ft1.x - ft0.x, ft1.y - ft0.y, 0)).normalized()
            lat = Vector((-fwd.y, fwd.x, 0)) * s
            for nm, c, semi, mat, sd in (("Spann" + side, ft0.lerp(ft1, 0.45) + Vector((0, 0, 0.02)), (0.13, 0.17, 0.085), rock_m, 24 + s),
                                         ("Ferse" + side, ft0 - fwd * 0.07 + Vector((0, 0, -0.06)), (0.1, 0.09, 0.07), rock2_m, 26 + s),
                                         ("Sohle" + side, ft0.lerp(ft1, 0.5) + Vector((0, 0, -0.02)), (0.15, 0.23, 0.06), rock2_m, 28 + s)):
                o = block_at(nm, c, semi, mat, sd, flat, subdiv)
                for v in o.data.vertices:
                    v.co.z = max(v.co.z, ground)
                add(side + "Foot", o)
            for k, dx in enumerate((-0.065, 0.0, 0.065)):
                base = ft0.lerp(ft1, 0.62) + lat * dx + Vector((0, 0, -0.03))
                add(side + "Foot", shard("Zeh%s%d" % (side, k), base, fwd + lat * dx * 2.5 + Vector((0, 0, -0.18)), 0.13 + 0.03 * (k == 1), 0.04, mats[k % 2]))
            add(side + "Foot", shard("Knoechelsplitter" + side, ft0 + lat * 0.1, lat + Vector((0, 0, 0.5)) - fwd * 0.3, 0.1, 0.03, mats[1]))
        else:
            add(side + "Foot", block_at("Fuss" + side, ft0.lerp(ft1, 0.55) + Vector((0, 0, 0.03)), (0.17, 0.25, 0.11), rock_m, 24 + s, flat, subdiv))
        joint(side + "Foot", "GlutKnoechel" + side, ft0, 0.09, ft1 - ft0, seed=80 + s)
        if spiky:
            # Kristallsplitter: Unterarm außen und hinten, Schienbein vorn, Oberschenkel außen (aggressiver, mehr Details)
            fa = obj_named(parts[B(side + "ForeArm")], "Unterarm" + side)
            for k, t in enumerate((0.3, 0.55, 0.8)):
                add(side + "ForeArm", shard_on("ArmSplitter%s%d" % (side, k), fa, f0.lerp(f1, t), (s * 0.8, 0.9, 0.35), 0.15 + 0.04 * (k == 1), 0.035, mats[k % 2]))
            sb = obj_named(parts[B(side + "Leg")], "Schienbein" + side)
            for k, t in enumerate((0.25, 0.6)):
                add(side + "Leg", shard_on("BeinSplitter%s%d" % (side, k), sb, u1.lerp(l1, t), (s * 0.2, -0.9, 0.5), 0.14, 0.035, mats[(k + 1) % 2]))
            th = obj_named(parts[B(side + "UpLeg")], "Oberschenkel" + side)
            add(side + "UpLeg", shard_on("SchenkelSplitter" + side, th, u0.lerp(u1, 0.6), (s * 1.0, 0.2, 0.4), 0.15, 0.04, mats[0]))
    for bone, objs in parts.items():
        attach(join_parts(objs, "Golem_" + bone.split(":")[1]), arm, bone)
    cut_hands(body)
    for side in ("Left", "Right"):
        hand = hand_model("Faust" + side, side, fist_m or rock_m, nail_m or rock2_m, size=1.5, fingers=3, fist=0.55)
        if flat:
            for pl in hand.data.polygons:
                pl.use_smooth = False
        place_in_bone(hand, arm, B(side + "Hand"))
    pose_hands(arm)
    remove_body(body)
    return {"chest": chest, "head": head, "neck": neck}

@variante("magma_golem_alt", "koloss")
def magma_golem(arm, body):
    """Lava-Kolonie (Welt 4): Magma-Golem – riesiger Golem aus dunklen Basaltblöcken, zwischen denen glühendes Magma
    leuchtet (Gelenke, Brustkern), Kopf mit Glutaugen und Glutmaul, Basaltstacheln mit Glutspitzen auf dem Rücken,
    Steinfäuste. Eigene Figur auf dem Koloss-Skelett."""
    basalt = look("Basalt", (0.24, 0.2, 0.19), rough=0.75)
    basalt2 = look("Basalt2", (0.33, 0.27, 0.24), rough=0.8)
    glut = look("Glut", (1.0, 0.42, 0.08), rough=0.5, emit=(1.0, 0.38, 0.05), strength=3.5)
    glut_hell = look("GlutHell", (1.0, 0.75, 0.25), rough=0.4, emit=(1.0, 0.65, 0.15), strength=5.0)
    g = golem_body(arm, body, basalt, basalt2, glut, flat=True, legs=1.6)   # längere Beine wie beim Kristallriesen (Wunsch 24.11.)
    H = "mixamorig:Head"
    hc = g["head"] + Vector((0, -0.08, 0.24))
    skull = block_at("Kopf", hc, (0.25, 0.23, 0.22), basalt, 31, True)
    jaw = block_at("Kiefer", hc + Vector((0, -0.07, -0.15)), (0.22, 0.17, 0.1), basalt2, 32, True)
    socket = look("Augenhoehle", (0.1, 0.05, 0.04), rough=0.6, emit=(0.6, 0.12, 0.02), strength=0.6)
    core = look("Glutkern", (1.0, 0.95, 0.7), rough=0.3, emit=(1.0, 0.92, 0.6), strength=9.0)
    mouth_in = look("Maulinneres", (0.45, 0.1, 0.03), rough=0.6, emit=(0.85, 0.22, 0.03), strength=1.3)
    tooth = look("Steinzahn", (0.62, 0.56, 0.5), rough=0.55)
    crack_m = look("Glutriss", (1.0, 0.5, 0.1), rough=0.5, emit=(1.0, 0.45, 0.06), strength=2.2)
    head_parts = [skull, jaw] + golem_face(skull, jaw, hc, {"socket": socket, "eye": glut_hell, "core": core, "mouth": mouth_in, "tooth": tooth,
                                                           "brow": basalt, "crack": crack_m, "throat": glut_hell})
    for s in (-1, 1):
        head_parts.append(give(horn("Kopfhorn%d" % s, tuple(hc + Vector((s * 0.15, -0.02, 0.12))), tuple(hc + Vector((s * 0.3, -0.04, 0.2))),
                                    tuple(hc + Vector((s * 0.32, -0.12, 0.36))), 0.07, n=9, glow_from=6), basalt, glut))
    attach(join_parts(head_parts, "Golem_Kopf"), arm, H)
    # Brustkern: Magma zwischen den Brustblöcken, darum Schollen
    core = g["chest"] + Vector((0, -0.2, 0.02))
    chest_parts = [give(sphere("Brustkern", tuple(core), 0.17), glut_hell)]
    for i, (dx, dz, sz) in enumerate(((-0.13, 0.12, 0.09), (0.14, 0.1, 0.08), (-0.12, -0.12, 0.085), (0.12, -0.13, 0.09), (0.0, 0.17, 0.07))):
        chest_parts.append(block_at("Scholle%d" % i, core + Vector((dx, -0.08, dz)), (sz, sz * 0.7, sz), basalt2, 40 + i, True))
    # Rückenstacheln mit Glutspitze
    for k, (x, z, L) in enumerate(((0.0, 0.14, 0.34), (-0.2, 0.06, 0.26), (0.2, 0.06, 0.26), (-0.1, -0.12, 0.2), (0.1, -0.12, 0.2))):
        b0 = g["chest"] + Vector((x, 0.36, z))
        chest_parts.append(give(horn("Stachel%d" % k, tuple(b0), tuple(b0 + Vector((x * 0.2, 0.14, L * 0.45))), tuple(b0 + Vector((x * 0.4, 0.22, L))), 0.08, n=9,
                                     glow_from=6), basalt, glut))
    attach(join_parts(chest_parts, "Golem_Brustkern"), arm, "mixamorig:Spine2")

@variante("kristall_riese_alt", "koloss")          # alter rosa Kristallgolem; neu: tools/monster/kristallriese.py
def kristall_riese(arm, body):
    """Herz des Wurmlochs (Welt 10): Kristallriese – in Koloss-Form, aber ganz aus facettierten violetten und rosa
    Kristallblöcken: kristalliner Kopf mit Kristallkrone und leuchtenden Augen, leuchtender Kern in der Brust,
    Kristallspitzen an Schultern und Rücken, Kristallfäuste, cyan leuchtende Gelenke. Eigene Figur."""
    cr = look("Riesenkristall", (0.5, 0.26, 0.9), rough=0.1, emit=(0.42, 0.18, 0.85), strength=0.35)
    cr2 = look("Riesenkristall2", (0.85, 0.3, 0.75), rough=0.1, emit=(0.75, 0.2, 0.65), strength=0.3)
    cr3 = look("Riesenkristall3", (0.34, 0.2, 0.7), rough=0.12, emit=(0.28, 0.12, 0.6), strength=0.35)
    energy = look("Kristallkern", (0.5, 0.95, 1.0), rough=0.2, emit=(0.3, 0.85, 1.0), strength=2.5)
    g = golem_body(arm, body, cr, cr3, energy, flat=True, subdiv=1, fist_m=cr3, nail_m=cr2, legs=1.6, spiky=True)
    H = "mixamorig:Head"
    hc = g["head"] + Vector((0, -0.08, 0.26))
    skull = block_at("Kopf", hc, (0.24, 0.22, 0.24), cr2, 51, True, 1)
    jaw = block_at("Kiefer", hc + Vector((0, -0.065, -0.16)), (0.21, 0.17, 0.1), cr3, 52, True, 1)
    socket = look("KristallHoehle", (0.14, 0.06, 0.3), rough=0.2, emit=(0.25, 0.06, 0.5), strength=0.6)
    core = look("Lichtkern", (0.95, 1.0, 1.0), rough=0.2, emit=(0.85, 1.0, 1.0), strength=8.0)
    tooth = look("Kristallzahn", (0.92, 0.85, 1.0), rough=0.1, emit=(0.6, 0.5, 0.9), strength=0.4)
    mouth_in = look("KristallMaul", (0.12, 0.3, 0.45), rough=0.3, emit=(0.15, 0.55, 0.8), strength=1.2)
    head_parts = [skull, jaw] + golem_face(skull, jaw, hc, {"socket": socket, "eye": energy, "core": core, "mouth": mouth_in, "tooth": tooth,
                                                           "brow": cr, "crack": energy, "throat": core}, crystal_teeth=True)
    # Krone (Kommentare 24.11.: aggressiver, mehr verziert, am Kopf verankert): lange, nach hinten gezogene Kristalle,
    # davor ein Diadem aus kleinen Splittern rund um die Stirn mit leuchtendem Stirnjuwel in einer Fassung;
    # Wangen- und Kinnsplitter
    for k, (x, y, h, r, d) in enumerate(((0.0, 0.0, 0.42, 0.075, (0, 0.55, 1)), (-0.11, 0.02, 0.32, 0.06, (-0.35, 0.6, 1)), (0.11, 0.02, 0.32, 0.06, (0.35, 0.6, 1)),
                                         (-0.2, 0.06, 0.24, 0.05, (-0.8, 0.5, 0.8)), (0.2, 0.06, 0.24, 0.05, (0.8, 0.5, 0.8)), (0.0, 0.14, 0.3, 0.055, (0, 1, 0.7)),
                                         (-0.07, 0.12, 0.2, 0.04, (-0.3, 1, 0.6)), (0.07, 0.12, 0.2, 0.04, (0.3, 1, 0.6)))):
        head_parts.append(shard_on("Krone%d" % k, skull, hc + Vector((x, y, 0.1)), d, h, r, cr if k % 2 == 0 else cr2, depth=0.05))
    for k in range(13):
        a = math.radians(-150 + k * 25)                       # Bogen über Stirn und Schläfen
        dvec = Vector((math.sin(a), -math.cos(a), 0.0))
        g_ = hc + dvec * 0.05 + Vector((0, 0, 0.13 - 0.02 * abs(math.sin(a))))
        h_ = 0.09 if k % 2 else 0.14
        if k == 6:
            h_ = 0.2
        head_parts.append(shard_on("Diadem%d" % k, skull, g_, dvec * 0.35 + Vector((0, 0, 1)), h_, 0.026 if k % 2 else 0.032, cr2 if k % 2 else cr, depth=0.03))
    gp, gn = surface(skull, (0, -2.0, hc.z + 0.13), (0, 1, 0))
    head_parts.append(give(torus("JuwelFassung", tuple(gp + gn * 0.004), 0.038, 0.01, rot=(90, 0, 0)), cr2))
    gem = block_at("Stirnjuwel", gp + gn * 0.01, (0.03, 0.024, 0.036), energy, 93, True, 1)
    head_parts.append(gem)
    for s_ in (-1, 1):
        head_parts.append(shard_on("Wange%d" % s_, skull, hc + Vector((s_ * 0.15, -0.08, -0.06)), (s_ * 1.0, -0.2, 0.25), 0.16, 0.035, cr))
        head_parts.append(shard_on("Wange2%d" % s_, skull, hc + Vector((s_ * 0.14, -0.02, -0.14)), (s_ * 1.0, 0.1, -0.1), 0.12, 0.03, cr2))
    head_parts.append(shard_on("Kinn", jaw, hc + Vector((0, -0.12, -0.2)), (0, -0.4, -1.0), 0.12, 0.035, cr))
    attach(join_parts(head_parts, "Riese_Kopf"), arm, H)
    core = g["chest"] + Vector((0, -0.22, 0.02))
    chest_parts = [block_at("Kern", core, (0.13, 0.1, 0.13), energy, 90, True, 1)]
    for i in range(7):
        a = i * 2 * math.pi / 7 + 0.3
        d = Vector((math.cos(a), -0.55, math.sin(a)))
        chest_parts.append(shard("KernSplitter%d" % i, core + Vector((math.cos(a) * 0.1, 0.04, math.sin(a) * 0.1)), d, 0.13 + 0.04 * (i % 2), 0.04, cr2 if i % 2 else cr))
    torso = next(o for o in bpy.data.objects if o.name.startswith("Golem_Spine2"))
    for k, (x, z, h, r, d) in enumerate(((0.0, 0.16, 0.48, 0.1, (0, 0.55, 0.85)), (-0.22, 0.08, 0.36, 0.08, (-0.35, 0.6, 0.75)), (0.22, 0.08, 0.36, 0.08, (0.35, 0.6, 0.75)),
                                         (-0.12, -0.1, 0.28, 0.065, (-0.2, 0.75, 0.6)), (0.12, -0.1, 0.28, 0.065, (0.2, 0.75, 0.6)))):
        chest_parts.append(shard_on("Ruecken%d" % k, torso, g["chest"] + Vector((x, 0.15, z)), d, h, r, cr if k % 2 == 0 else cr2, depth=0.05))
    attach(join_parts(chest_parts, "Riese_Brust"), arm, "mixamorig:Spine2")
    for s, side in ((1, "Left"), (-1, "Right")):
        a0 = arm.matrix_world @ arm.data.bones["mixamorig:%sArm" % side].head_local
        sp = []
        for k, (dx, dy, h, r, tx, ty) in enumerate(((0.04, 0.0, 0.44, 0.085, 0, 30), (0.14, 0.1, 0.32, 0.065, -15, 55), (-0.04, -0.1, 0.28, 0.06, 22, 16),
                                                    (0.12, -0.08, 0.24, 0.055, 28, 60), (0.0, 0.14, 0.26, 0.055, -32, 22), (0.18, 0.0, 0.2, 0.05, 0, 75))):
            up = Vector((0, 0, 1)); d = Matrix.Rotation(math.radians(tx), 3, 'X') @ Matrix.Rotation(math.radians(s * ty), 3, 'Y') @ up
            sh_obj = next(o for o in bpy.data.objects if o.name.startswith("Golem_%sArm" % side))
            sp.append(shard_on("Schulterkristall%s%d" % (side, k), sh_obj, Vector((a0.x + s * dx, a0.y + dy, a0.z + 0.1)), d, h, r, cr2 if k % 2 == 0 else cr, depth=0.05))
        attach(join_parts(sp, "Riese_Schulter" + side), arm, "mixamorig:%sArm" % side)
        # Kristallspitzen auf den Fingerknöcheln (Handrücken: links +Z, rechts -Z im Handrahmen)
        zs = 1.0 if side == "Left" else -1.0
        kn = []
        for k, (x, y, h, r) in enumerate(((-0.07, 0.17, 0.11, 0.035), (0.0, 0.19, 0.13, 0.04), (0.07, 0.16, 0.1, 0.033), (0.0, 0.07, 0.09, 0.03))):
            c = crystal("Knoechel%s%d" % (side, k), (x * 1.5, y * 1.5, 0.035 * zs), h, r, (0 if zs > 0 else 180, 0, 0))
            kn.append(give(c, cr))
        place_in_bone(join_parts(kn, "Riese_Knoechel" + side), arm, "mixamorig:%sHand" % side)

def googly_eyes(name, center, normal, r, white, black, spread=0.6):
    """zwei kleine Augen auf einer Kugeloberfläche (für Schleimkinder)"""
    n = Vector(normal).normalized()
    side = n.cross(Vector((0, 0, 1))).normalized() if abs(n.z) < 0.9 else Vector((1, 0, 0))
    parts = []
    for s in (-1, 1):
        c = Vector(center) + side * s * r * spread + Vector((0, 0, r * 0.25))
        parts.append(give(sphere("%sAuge%d" % (name, s), tuple(c + n * r * 0.8), r * 0.32), white))
        parts.append(give(sphere("%sPupille%d" % (name, s), tuple(c + n * r * 1.05), r * 0.16), black))
    return parts

def fix_flipped_faces(body):
    """Verkehrt herum eingesetzte Flächen des Grundmodells umdrehen (Kommentar 24.11.: schwarzes Dreieck auf dem Rücken
    der Schleimmutter) und die Schattierung neu berechnen lassen: Fläche, deren Richtung gegen alle Nachbarn zeigt,
    wird gewendet; die mitgelieferten Punktnormalen werden verworfen (glatte Schattierung aus der Form)."""
    bm = bmesh.new(); bm.from_mesh(body.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0002)
    bad = []
    for f in bm.faces:
        nb = [g for e in f.edges for g in e.link_faces if g is not f]
        if not nb:
            continue
        avg = Vector((0, 0, 0))
        for g in nb:
            avg += g.normal
        if avg.length > 0 and f.normal.dot(avg.normalized()) < -0.3:
            bad.append(f)
    if bad:
        bmesh.ops.reverse_faces(bm, faces=bad)
    bm.to_mesh(body.data); bm.free()
    me = body.data
    if me.has_custom_normals:
        bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); bpy.context.view_layer.objects.active = body
        bpy.ops.mesh.customdata_custom_splitnormals_clear()
    for pl in me.polygons:
        pl.use_smooth = True
    me.update()
    return len(bad)

def reproject_texture(body, size=2048, angle=70.0, margin=0.01):
    """Haut neu abwickeln (Kommentar 24.11.: Streifen auf der Schleimmutter bleiben): Die Textur des Grundmodells besteht
    aus Hunderten kleiner Stücke; an jeder Naht mischen sich beim Verkleinern und Komprimieren fremde Farben ein und
    erscheinen als Linien. Neue Abwicklung mit wenigen großen Stücken (Smart UV Project) und Abstand dazwischen; die
    Farben werden Dreieck für Dreieck aus der alten Textur übertragen (gleiches Dreieck, alte und neue UV), danach
    werden die Ränder der neuen Stücke aufgefüllt."""
    from PIL import Image as _Img, ImageDraw as _Draw
    m, tex, img, old = body_texture(body)
    oh, ow = old.shape[:2]
    me = body.data
    old_uv = me.uv_layers.active
    old_name = old_uv.name
    new_uv = me.uv_layers.new(name="NeuUV")
    me.uv_layers.active = new_uv
    bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); bpy.context.view_layer.objects.active = body
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.0002)        # an den alten Nähten getrennte Punkte wieder verbinden
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(angle), island_margin=margin)
    bpy.ops.object.mode_set(mode='OBJECT')
    ouv = me.uv_layers[old_name].data; nuv = me.uv_layers["NeuUV"].data
    out = np.zeros((size, size, 4), dtype=np.float32); out[..., 3] = 1
    filled = np.zeros((size, size), dtype=bool)

    def sample(u, v):                                    # bilinear, u/v in 0..1, Zeile 0 unten
        x = np.clip(u * ow - 0.5, 0, ow - 1.001); y = np.clip(v * oh - 0.5, 0, oh - 1.001)
        x0 = x.astype(int); y0 = y.astype(int); fx = (x - x0)[:, None]; fy = (y - y0)[:, None]
        a = old[y0, x0, :3]; b = old[y0, x0 + 1, :3]; c = old[y0 + 1, x0, :3]; d = old[y0 + 1, x0 + 1, :3]
        return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy
    for poly in me.polygons:
        li = list(poly.loop_indices)
        for t in range(1, len(li) - 1):                   # in Dreiecke zerlegen
            tri = (li[0], li[t], li[t + 1])
            N = np.array([(nuv[k].uv.x * size, nuv[k].uv.y * size) for k in tri])
            O = np.array([(ouv[k].uv.x, ouv[k].uv.y) for k in tri])
            x0, y0 = np.floor(N.min(0)).astype(int) - 1; x1, y1 = np.ceil(N.max(0)).astype(int) + 1
            x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, size - 1), min(y1, size - 1)
            if x1 < x0 or y1 < y0:
                continue
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            P = np.stack([gx.ravel(), gy.ravel()], 1)
            v0 = N[1] - N[0]; v1 = N[2] - N[0]; d00 = v0 @ v0; d01 = v0 @ v1; d11 = v1 @ v1
            den = d00 * d11 - d01 * d01
            if abs(den) < 1e-12:
                continue
            v2 = P - N[0]; d20 = v2 @ v0; d21 = v2 @ v1
            b1 = (d11 * d20 - d01 * d21) / den; b2 = (d00 * d21 - d01 * d20) / den; b0 = 1 - b1 - b2
            eps = -0.75 / max(1.0, math.sqrt(max(d00, d11)))   # ein halbes Texel über den Rand hinaus mitnehmen
            ins = (b0 >= eps) & (b1 >= eps) & (b2 >= eps)
            if not ins.any():
                continue
            bb = np.stack([b0[ins], b1[ins], b2[ins]], 1)
            bb = np.clip(bb, 0, None); bb /= bb.sum(1, keepdims=True)
            uvo = bb @ O
            col = sample(uvo[:, 0], uvo[:, 1])
            px_ = (P[ins] - 0.5).astype(int)
            out[px_[:, 1], px_[:, 0], :3] = col
            filled[px_[:, 1], px_[:, 0]] = True
    for _ in range(12):                                   # Ränder der neuen Stücke auffüllen
        acc = np.zeros((size, size, 3), dtype=np.float32); cnt = np.zeros((size, size), dtype=np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            f = np.roll(filled, (dy, dx), (0, 1)); acc += np.roll(out[..., :3], (dy, dx), (0, 1)) * f[..., None]; cnt += f
        new = (~filled) & (cnt > 0)
        out[new, :3] = acc[new] / cnt[new][:, None]; filled |= new
    me.uv_layers.remove(me.uv_layers[old_name])
    me.uv_layers.active = me.uv_layers["NeuUV"]
    me.uv_layers["NeuUV"].active_render = True
    tex.image = new_image(body.name + "_Farbe", out)

def fill_black_spots(body, keep=lambda c: False, dark=0.09):
    """Schwarze Fehlstellen in der Textur (z. B. kleines schwarzes Dreieck auf dem Rücken der Schleimmutter) mit der
    Farbe der Umgebung im selben Dreieck füllen; keep(Mitte) schützt Dreiecke mit echten dunklen Details (Augen, Mund)"""
    from PIL import Image as _Img, ImageDraw as _Draw
    m, tex, img, px = body_texture(body)
    h, w = px.shape[:2]
    base = px.copy()
    lumi = 0.3 * px[..., 0] + 0.6 * px[..., 1] + 0.1 * px[..., 2]
    uvl = body.data.uv_layers.active.data
    mw = body.matrix_world
    for poly in body.data.polygons:
        if keep(mw @ poly.center):
            continue
        uv = np.array([(uvl[li].uv.x * w, (1 - uvl[li].uv.y) * h) for li in poly.loop_indices])
        x0, y0 = np.floor(uv.min(0)).astype(int) - 8; x1, y1 = np.ceil(uv.max(0)).astype(int) + 8
        x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, w - 1), min(y1, h - 1)
        if x1 <= x0 or y1 <= y0:
            continue
        rows = (h - 1) - np.arange(y0, y1 + 1); cols_ = np.arange(x0, x1 + 1)
        blk_l = lumi[rows[:, None], cols_[None, :]]
        if not (blk_l < dark).any():
            continue
        mk = _Img.new("L", (x1 - x0 + 1, y1 - y0 + 1), 0)
        _Draw.Draw(mk).polygon([(u - x0, v - y0) for u, v in uv], fill=255)
        sel = np.array(mk) > 0
        blk = base[rows[:, None], cols_[None, :], :3]
        good = sel & (blk_l >= dark)
        if good.sum() < 3:                                # ganzes Dreieck schwarz: Farbe der Nachbarn im Umfeld nehmen
            good = blk_l >= dark
            if good.sum() < 3:
                continue
        med = np.median(blk[good], axis=0)
        bad = (blk_l < dark)
        blk[bad] = med
        base[rows[:, None], cols_[None, :], :3] = blk
    tex.image = new_image(body.name + "_Farbe", base)

def clean_seams(body, keep=lambda c: False, thresh=0.16):
    """Nahtlinien entfernen (Kommentar 24.11.: Streifen auf der Schleimmutter): Jedes Dreieck der Haut bekommt seine
    Texel aus der Textur; Texel, die deutlich von der mittleren Farbe des Dreiecks abweichen (fremde Farbe aus einem
    Nachbarstück oder schwarze Lücke an der Naht), werden durch diese ersetzt. keep(Mitte) schützt Dreiecke mit echten
    Details (Augen, Mund, Brauen)."""
    from PIL import Image as _Img, ImageDraw as _Draw
    m, tex, img, px = body_texture(body)
    h, w = px.shape[:2]
    base = px.copy()
    uvl = body.data.uv_layers.active.data
    mw = body.matrix_world
    for poly in body.data.polygons:
        if keep(mw @ poly.center):
            continue
        uv = np.array([(uvl[li].uv.x * w, (1 - uvl[li].uv.y) * h) for li in poly.loop_indices])
        x0, y0 = np.floor(uv.min(0)).astype(int) - 1; x1, y1 = np.ceil(uv.max(0)).astype(int) + 1
        x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, w - 1), min(y1, h - 1)
        if x1 <= x0 or y1 <= y0:
            continue
        mk = _Img.new("L", (x1 - x0 + 1, y1 - y0 + 1), 0)
        _Draw.Draw(mk).polygon([(u - x0, v - y0) for u, v in uv], fill=255)
        sel = np.array(mk) > 0
        if sel.sum() < 3:
            continue
        rows = (h - 1) - (np.arange(y0, y1 + 1))          # Bildzeile 0 ist unten (wie px)
        blk = px[rows[:, None], np.arange(x0, x1 + 1)[None, :], :3]
        cols = blk[sel]
        med = np.median(cols, axis=0)
        dist = np.abs(cols - med).sum(1)
        bad = dist > thresh
        if not bad.any():
            continue
        fixed = cols.copy(); fixed[bad] = med
        out = blk.copy(); out[sel] = fixed
        base[rows[:, None], np.arange(x0, x1 + 1)[None, :], :3] = out
    tex.image = new_image(body.name + "_Farbe", base)

def pad_texture(body, grow=12, shrink=1):
    """Ränder der Texturstücke auffüllen (Kommentar 24.11.: Streifen auf der Schleimmutter): Die Textur des Grundmodells
    besteht aus vielen kleinen Stücken mit schwarzen Lücken dazwischen. Beim Verkleinern (Mipmaps) mischt sich das
    Schwarz in die Stückränder, auf dem Modell erscheinen dünne Linien entlang der Nähte. Hier wird bestimmt, welche
    Pixel zu einem Stück gehören (UV-Dreiecke), die äußerste Randreihe verworfen und jedes Stück um grow Pixel mit
    seinen eigenen Randfarben nach außen verlängert."""
    from PIL import Image as _Img, ImageDraw as _Draw
    m, tex, img, px = body_texture(body)
    h, w = px.shape[:2]
    cov = _Img.new("L", (w, h), 0); d = _Draw.Draw(cov)
    uvl = body.data.uv_layers.active.data
    for poly in body.data.polygons:
        pts = [(uvl[li].uv.x * w, (1 - uvl[li].uv.y) * h) for li in poly.loop_indices]
        d.polygon(pts, fill=255)
    mask = np.array(cov)[::-1] > 0                       # Bildzeile 0 ist unten (wie px)
    for _ in range(shrink):                              # verunreinigte Randreihe verwerfen
        mask = mask & np.roll(mask, 1, 0) & np.roll(mask, -1, 0) & np.roll(mask, 1, 1) & np.roll(mask, -1, 1)
    col = px[..., :3].copy(); col[~mask] = 0
    filled = mask.copy()
    for _ in range(grow + shrink):
        acc = np.zeros_like(col); cnt = np.zeros(mask.shape, dtype=np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            f = np.roll(filled, (dy, dx), (0, 1)); c = np.roll(col, (dy, dx), (0, 1))
            acc += c * f[..., None]; cnt += f
        new = (~filled) & (cnt > 0)
        col[new] = acc[new] / cnt[new][:, None]
        filled |= new
    base = px.copy(); base[..., :3] = np.where(filled[..., None], col, px[..., :3])
    tex.image = new_image(body.name + "_Farbe", base)

def front_texels(body, x0, x1, z0, z1, n=320):
    """Texel der Körpertextur, die man von vorn im Bereich x0..x1 / z0..z1 sieht: Liste (x, z, tx, ty)"""
    from mathutils.bvhtree import BVHTree
    from mathutils.geometry import barycentric_transform
    bpy.context.view_layer.update()
    me = body.data
    m, tex, img, px = body_texture(body)
    w, h = img.size
    bvh = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())
    uvl = me.uv_layers.active.data
    inv = body.matrix_world.inverted()
    out = []
    for i in range(n):
        z = z0 + (z1 - z0) * i / (n - 1)
        for j in range(n):
            x = x0 + (x1 - x0) * j / (n - 1)
            loc, nor, idx, d = bvh.ray_cast(inv @ Vector((x, -2.0, z)), (inv.to_3x3() @ Vector((0, 1, 0))).normalized())
            if loc is None:
                continue
            poly = me.polygons[idx]
            li = poly.loop_indices[:3]
            vs = [me.vertices[me.loops[k].vertex_index].co for k in li]
            uv = barycentric_transform(loc, vs[0], vs[1], vs[2], uvl[li[0]].uv.to_3d(), uvl[li[1]].uv.to_3d(), uvl[li[2]].uv.to_3d())
            out.append((x, z, min(w - 1, max(0, int(uv.x * w))), min(h - 1, max(0, int(uv.y * h)))))
    return out

def fix_slime_eye(body):
    """Verrauschte Pupille im rechten Auge der Schleimmutter (Fehler in der Textur des Grundmodells, Kommentar 24.11.)
    sauber nachmalen: dunkle Pupille als Ellipse aus den dunklen Stellen, Glanzpunkt oben rechts wie im anderen Auge"""
    m, tex, img, px = body_texture(body)
    lum = lambda c: 0.3 * c[0] + 0.6 * c[1] + 0.1 * c[2]
    ref = front_texels(body, 0.05, 0.17, 0.13, 0.24, n=120)
    dark_ref = [px[ty, tx, :3] for x, z, tx, ty in ref if lum(px[ty, tx]) < 0.2]
    pupil_col = np.median(np.array(dark_ref), axis=0) if dark_ref else np.array((0.08, 0.05, 0.12), dtype=np.float32)
    pts = front_texels(body, -0.13, 0.0, 0.12, 0.25, n=520)
    sat = lambda c: max(c[0], c[1], c[2]) - min(c[0], c[1], c[2])
    white = np.array([(x, z) for x, z, tx, ty in pts if lum(px[ty, tx]) > 0.7 and sat(px[ty, tx]) < 0.15])
    lo, hi = white.min(0), white.max(0)                 # Augapfel (weiß) begrenzt die Suche, Braue (violett) fällt raus
    dark = np.array([(x, z) for x, z, tx, ty in pts if lum(px[ty, tx]) < 0.3 and sat(px[ty, tx]) < 0.18
                     and lo[0] <= x <= hi[0] and lo[1] <= z <= hi[1]])
    c = dark.mean(0); cov = np.cov((dark - c).T)
    ev, evec = np.linalg.eigh(cov); radii = 2.3 * np.sqrt(ev)
    white_col = np.median(np.array([px[ty, tx, :3] for x, z, tx, ty in pts if lum(px[ty, tx]) > 0.7 and sat(px[ty, tx]) < 0.15]), axis=0)
    hl = c + np.array((0.32, 0.38)) * radii.max()
    base = px.copy()
    h_, w_ = base.shape[:2]
    for x, z, tx, ty in pts:
        q = evec.T @ (np.array((x, z)) - c)
        r = math.sqrt((q[0] / radii[0]) ** 2 + (q[1] / radii[1]) ** 2)
        col = None
        if r < 1.0:
            k = 1.0 if r < 0.88 else (1.0 - r) / 0.12
            col = base[ty, tx, :3] * (1 - k) + pupil_col * k
            if math.hypot(x - hl[0], z - hl[1]) < radii.max() * 0.22:
                col = np.array((0.97, 0.97, 0.97), dtype=np.float32)
        elif lo[0] <= x <= hi[0] and lo[1] <= z <= hi[1] and sat(px[ty, tx]) < 0.15 and 0.25 < lum(px[ty, tx]) < 0.72:
            col = white_col                                   # graue Sprenkel im Augenweiß
        if col is not None:
            for dy in (-1, 0, 1):                             # Nachbartexel mit (gegen Ausfransen beim Verkleinern)
                for dx in (-1, 0, 1):
                    yy, xx = ty + dy, tx + dx
                    if 0 <= yy < h_ and 0 <= xx < w_ and (dx == 0 and dy == 0 or sat(px[yy, xx]) < 0.18):
                        base[yy, xx, :3] = col
    tex.image = new_image(body.name + "_Farbe", base)

@variante("schleimmutter_krone", "schleimmutter")
def schleimmutter_krone(arm, body):
    """Schleim-Welt (Welt 1): Schleimmutter mit mehr Details – goldenes Krönchen mit Edelsteinen um die drei Perlen,
    Bläschen im Schleim, zwei Schleimkinder auf ihr, glänzende Schleimpfütze"""
    slime = look("SchleimGlanz", (0.2, 0.9, 0.84), rough=0.06, emit=(0.08, 0.55, 0.5), strength=0.35, alpha=0.88)
    bubble = look("Blaeschen", (0.7, 1.0, 0.96), rough=0.03, emit=(0.35, 0.85, 0.8), strength=0.35)
    gold = look("Gold", (1.0, 0.78, 0.3), rough=0.25, metal=0.9)
    gem = look("Edelstein", (0.7, 0.3, 1.0), rough=0.1, emit=(0.6, 0.2, 1.0), strength=1.2)
    white = look("Weiss", (1.0, 1.0, 1.0), rough=0.3)
    black = look("Schwarz", (0.05, 0.05, 0.08), rough=0.3)
    baby = look("Schleimkind", (0.55, 0.3, 1.0), rough=0.1, emit=(0.4, 0.15, 0.8), strength=0.4)
    pad_texture(body)            # schwarze Lücken der alten Textur füllen, damit beim Übertragen nichts Schwarzes mitkommt
    fix_flipped_faces(body)      # verkehrt herum eingesetzte Flächen umdrehen (schwarzes Dreieck auf dem Rücken)
    reproject_texture(body)      # Haut neu abwickeln: wenige große Stücke statt Hunderter kleiner (keine Nahtlinien)
    fix_slime_eye(body)          # erst danach das rechte Auge nachmalen (auf der neuen Textur)
    fill_black_spots(body, keep=lambda c: c.y < -0.15 and -0.2 < c.x < 0.25 and 0.06 < c.z < 0.3)   # Gesicht vorn bleibt
    # Krönchen: Goldband über die Basis der drei Perlen, Fassungen, Edelsteine dazwischen
    band = []
    for x, y in ((-0.3, -0.1), (-0.19, -0.15), (-0.1, -0.18), (-0.02, -0.19), (0.07, -0.19), (0.155, -0.17), (0.27, -0.1)):
        p, n = surface(body, (x, y, 1.5), (0, 0, -1))
        band.append(tuple(p + n * 0.012))
    parts = [give(tube("Kronband", band, [0.02] * len(band), segs=10), gold)]
    for i, (c, rr) in enumerate((((-0.191, -0.158, 0.41), 0.075), ((-0.022, -0.188, 0.44), 0.09), ((0.155, -0.178, 0.41), 0.08))):
        parts.append(give(torus("Fassung%d" % i, c, rr, 0.016, rot=(0, 0, 0)), gold))
    for i, x in enumerate((-0.105, 0.065)):
        p, n = surface(body, (x, -0.19, 1.5), (0, 0, -1))
        parts.append(give(crystal("Stein%d" % i, tuple(p + n * 0.01), 0.05, 0.03, (0, 0, 0)), gem))
        parts.append(give(torus("SteinFassung%d" % i, tuple(p + n * 0.012), 0.032, 0.008, rot=(0, 0, 0)), gold))
    attach(join_parts(parts, "Kroenchen"), arm, "Top")
    # keine zusätzlichen Tropfen: frei hängend wirkten sie wie Stäbe und Striche (Kommentar 24.11.), die Kappe hat eigene Tropfenformen
    # Bläschen im Schleim der Kappe
    rnd = random.Random(17)
    bub = []
    for i in range(16):
        x, y = rnd.uniform(-0.36, 0.36), rnd.uniform(-0.05, 0.3)
        p, n = surface(body, (x, y, 1.5), (0, 0, -1))
        if p is None or p.z < 0.2:
            continue
        bub.append(give(sphere("Blase%d" % i, tuple(p + n * 0.005), rnd.uniform(0.018, 0.04)), bubble))
    attach(join_parts(bub, "Blaeschen"), arm, "Top")
    # zwei Schleimkinder: eins oben links auf der Kappe, eins seitlich rechts
    for i, (x, y, r, bone) in enumerate(((-0.3, 0.12, 0.075, "Top"), (0.36, 0.02, 0.065, "Body"))):
        p, n = surface(body, (x * 3, y, 0.3) if bone == "Body" else (x, y, 1.5), (-1, 0, 0) if bone == "Body" else (0, 0, -1))
        c = p + n * r * 0.6
        kid = [give(sphere("Kind%d" % i, tuple(c), r, (1, 1, 0.8)), baby)]
        kid += googly_eyes("Kind%d" % i, c, Vector((0.25 if i == 0 else 0.4, -1, 0.1)), r, white, black)
        attach(join_parts(kid, "Schleimkind%d" % i), arm, bone)
    # glänzende Pfütze am Boden
    hem = lambda a: (0.0, 0.05 * math.cos(5 * a + 0.4) + 0.03 * math.cos(9 * a))
    puddle = lathe("Pfuetze", [(0.022, 0.0), (0.02, 0.4), (0.012, 0.52), (0.0, 0.58)], segs=64, hem=hem)
    puddle.scale = (1.0, 0.85, 1.0)
    attach(give(puddle, look("Pfuetze", (0.16, 0.78, 0.74), rough=0.05, emit=(0.06, 0.45, 0.42), strength=0.3)), arm, "Body")
    # kein Fleckenmuster auf dem Schleim: die Textur besteht aus vielen kleinen Teilstücken, ein Muster darüber
    # bricht an jeder Kante ab und wirkt wie Striche (Kommentar 24.11.)

def dampen_scale(arm, bones, factor):
    """Quetschen und Strecken der Bewegungen abschwächen (Skalierungsschlüssel näher an 1): factor 0 = gar nicht, 1 = wie bisher"""
    for act in bpy.data.actions:
        for fc in act.fcurves:
            if any(fc.data_path == 'pose.bones["%s"].scale' % b for b in bones):
                for kp in fc.keyframe_points:
                    for attr in ("co", "handle_left", "handle_right"):
                        v = getattr(kp, attr)
                        setattr(kp, attr, (v[0], 1.0 + (v[1] - 1.0) * factor))
                fc.update()

@variante("gift_kroete", "schleimmutter")
def gift_kroete(arm, body):
    """Giftsumpf (Welt 5): Giftkröte – breite, gedrungene Kröte mit großen gelben Augen und Schlitzpupillen, breitem
    Maul mit Gifttropfen, olivgrüner Haut mit violetten Flecken und hellem Bauch, giftgrün leuchtenden Warzen, Giftpilzen
    auf dem Rücken, Vorderbeinen mit Schwimmfüßen und dicken Hinterbeinen. Eigene Figur auf dem Skelett der Schleimmutter."""
    skin = look("Kroetenhaut", (1.0, 1.0, 1.0), rough=0.55)
    skin_flat = look("Kroetenbein", (0.42, 0.55, 0.2), rough=0.6)
    belly = look("Bauch", (0.78, 0.82, 0.45), rough=0.6)
    wart = look("Giftwarze", (0.55, 1.0, 0.25), rough=0.25, emit=(0.45, 1.0, 0.15), strength=1.6)
    eye = look("Kroetenauge", (1.0, 0.8, 0.15), rough=0.15, emit=(0.9, 0.6, 0.05), strength=0.8)
    black = look("Pupille", (0.04, 0.03, 0.03), rough=0.3)
    mouth_m = look("Maulspalt", (0.18, 0.05, 0.12), rough=0.5)
    toxic = look("Gifttropfen", (0.6, 1.0, 0.3), rough=0.1, emit=(0.5, 1.0, 0.2), strength=1.8)
    stalk = look("Stiel", (0.9, 0.86, 0.75), rough=0.6)
    cap = look("Pilzhut", (0.7, 0.25, 0.85), rough=0.45, emit=(0.6, 0.15, 0.8), strength=0.5)
    hz = 1.3   # höher und schmaler als zuerst (Kommentar 24.11.: wirkte im Spiel breitgedrückt)
    prof = [(z * hz, r) for z, r in ((0.5, 0.0), (0.49, 0.1), (0.46, 0.2), (0.41, 0.29), (0.34, 0.37), (0.26, 0.42), (0.18, 0.445), (0.11, 0.44),
                                     (0.06, 0.41), (0.025, 0.34), (0.005, 0.22), (0.0, 0.0))]
    g = lathe("Kroete", prof, segs=64)
    for v in g.data.vertices:
        v.co.x *= 1.0; v.co.y *= 0.95
        if v.co.y < 0:                                   # Kopf vorn etwas flacher
            v.co.z *= 1.0 - 0.1 * min(1.0, -v.co.y / 0.4) * max(0.0, (v.co.z - 0.2 * hz) / (0.3 * hz))
    # Haut: oben oliv mit violetten Flecken, unten heller Bauch (Bildzeile 0 = unten)
    H_, W_ = 1024, 1024
    vv = np.linspace(0, 1, H_)[:, None] * np.ones((1, W_))
    spots = fbm(H_, W_, 9, 91)
    grad = np.clip((vv - 0.42) / 0.16, 0, 1)
    top = np.array((0.38, 0.52, 0.16)); bot = np.array((0.84, 0.86, 0.5))
    col = bot * (1 - grad[..., None]) + top * grad[..., None]
    k = (np.clip((spots - 0.58) * 45, 0, 1) * grad)[..., None]          # Flecken mit klarer Kante (Kommentar 24.11.)
    ring = (np.clip(1 - np.abs(spots - 0.575) * 70, 0, 1) * grad)[..., None]   # dunkle Umrandung
    col = np.clip(col + ((fbm(H_, W_, 40, 92, 2) - 0.5) * 0.12)[..., None], 0, 1)
    col = col * (1 - k) + np.array((0.5, 0.17, 0.6)) * k
    col = col * (1 - ring * 0.55) + np.array((0.16, 0.08, 0.18)) * (ring * 0.55)
    arr = np.ones((H_, W_, 4), dtype=np.float32); arr[..., :3] = col
    nt = skin.node_tree
    ti = nt.nodes.new("ShaderNodeTexImage"); ti.image = new_image("Kroete_Farbe", arr)
    nt.links.new(ti.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    give(g, skin)
    bpy.context.view_layer.update()
    # Warzen auf dem Rücken
    rnd = random.Random(23)
    warts = []
    for i in range(30):
        a = rnd.uniform(-2.6, 2.6) + math.pi / 2       # vor allem hinten und oben
        el = rnd.uniform(0.25, 1.2)
        d = Vector((math.cos(a) * math.cos(el), math.sin(a) * math.cos(el), math.sin(el)))
        p, n = surface(g, Vector((0, 0, 0.2 * hz)) + d * 2.0, -d)
        if p is None or p.z < 0.15 * hz:
            continue
        warts.append(give(sphere("Warze%d" % i, tuple(p), rnd.uniform(0.018, 0.04), (1, 1, 0.7)), wart))
    # Augen: Wülste, gelbe Augäpfel, waagerechte Schlitzpupillen
    face = []
    for s_ in (-1, 1):
        p, n = surface(g, (s_ * 0.17, -2.0, 0.42 * hz), (0, 1, 0))
        c = p + Vector((0, 0.03, 0.04))
        face.append(give(sphere("Augenwulst%d" % s_, tuple(c), 0.1, (1, 0.95, 0.9)), skin_flat))
        face.append(give(sphere("Augapfel%d" % s_, tuple(c + Vector((0, -0.045, 0.03))), 0.075), eye))
        face.append(give(sphere("Schlitz%d" % s_, tuple(c + Vector((0, -0.115, 0.035))), 0.03, (1.5, 0.35, 0.45)), black))
        face.append(give(tube("Lid%d" % s_, [tuple(c + Vector((-0.08, -0.05, 0.06))), tuple(c + Vector((0, -0.075, 0.085))), tuple(c + Vector((0.08, -0.05, 0.06)))],
                              [0.025, 0.03, 0.025]), skin_flat))
    # breites Maul vorn, mit Gifttropfen in den Mundwinkeln
    hits = on_surface(g, (0, 0, 0.25 * hz), [(math.sin(a), -math.cos(a), 0.12 * (abs(a) / 1.05) ** 2 - 0.05) for a in [math.radians(t) for t in range(-60, 65, 8)]], lift=0.004)
    face.append(give(tube("Maul", [tuple(p) for p, n in hits], [0.012] + [0.022] * (len(hits) - 2) + [0.012], segs=8), mouth_m))
    face.append(give(tube("Lippe", [tuple(p + n * 0.012 + Vector((0, 0, 0.022))) for p, n in hits[1:-1]], [0.016] * (len(hits) - 2), segs=8), skin_flat))
    for s_, (p, n) in ((-1, hits[0]), (1, hits[-1])):
        face.append(give(tube("Giftfaden%d" % s_, [tuple(p), tuple(p + Vector((0, -0.01, -0.06))), tuple(p + Vector((0, -0.012, -0.1)))], [0.016, 0.01, 0.012]), toxic))
        face.append(give(sphere("Gifttropfen%d" % s_, tuple(p + Vector((0, -0.012, -0.115))), 0.02, (1, 1, 1.2)), toxic))
    # Giftpilze auf dem Rücken
    for i, (x, y, h, r) in enumerate(((-0.12, 0.2, 0.12, 0.06), (0.14, 0.24, 0.1, 0.05), (0.02, 0.32, 0.08, 0.04))):
        p, n = surface(g, (x, y, 2.0), (0, 0, -1))
        face.append(give(tube("PilzStiel%d" % i, [tuple(p - n * 0.01), tuple(p + n * h * 0.5), tuple(p + n * h)], [r * 0.3, r * 0.26, r * 0.24]), stalk))
        cap_ = sphere("PilzHut%d" % i, (0, 0, 0), r, (1, 1, 0.55)); cap_.location = p + n * h
        face.append(give(cap_, cap))
    attach(join_parts(warts + face, "Kroete_Kopf"), arm, "Top")
    skin_to(g, arm, lambda c: {"Top": smooth01((c.z - 0.12 * hz) / (0.3 * hz)), "Body": 1 - smooth01((c.z - 0.12 * hz) / (0.3 * hz))})
    # Beine (Kommentare 24.11.: Füße sauber am Körper, Pfoten rundum plastisch, keine flache Scheibe unter den Zehen):
    # Vorderbeine aus dem Körper heraus, Ballen mit vier Zehen und Haftballen; Hinterbeine mit Schenkel, der im Körper
    # steckt, Unterschenkel und langem Fuß mit vier Zehen
    legs = []

    def toes(tag, s_, wrist, n, length, r, spread, fwd=0.0):
        out = []
        for k in range(n):
            a_ = math.radians(-spread / 2 + spread * k / (n - 1)) + fwd
            d = Vector((s_ * math.sin(a_ + 0.35), -math.cos(a_ + 0.35), 0.0)).normalized()
            p0 = wrist + d * 0.015 + Vector((0, 0, 0.012))
            p1 = wrist + d * length * 0.55 + Vector((0, 0, 0.03))
            p2 = wrist + d * length + Vector((0, 0, 0.016))
            out.append(give(tube("%sZeh%d" % (tag, k), [tuple(p0), tuple(p1), tuple(p2)], [r, r * 0.85, r * 0.75], segs=10), skin_flat))
            out.append(give(sphere("%sBallen%d" % (tag, k), tuple(p2 + d * 0.006), r * 1.15, (1, 1, 0.8)), belly))
        return out

    for s_ in (-1, 1):
        sh, shn = surface(g, (s_ * 1.5, -0.2, 0.24), (-s_, 0, 0))
        wrist = Vector((s_ * 0.42, -0.36, 0.04))
        elbow = Vector((s_ * 0.44, -0.27, 0.14))
        legs.append(give(tube("Vorderbein%d" % s_, [tuple(sh - shn * 0.05), tuple(elbow), tuple(wrist + Vector((0, 0, 0.02)))],
                              [0.075, 0.06, 0.05], segs=12), skin_flat))
        legs.append(give(sphere("Handballen%d" % s_, tuple(wrist), 0.055, (1.1, 1.15, 0.6)), skin_flat))
        legs += toes("Vorne%d" % s_, s_, wrist, 4, 0.11, 0.021, 80)
        hp, hn = surface(g, (s_ * 1.5, 0.12, 0.2), (-s_, 0, 0))
        thigh = sphere("Schenkel%d" % s_, (0, 0, 0), 1.0, (0.14, 0.22, 0.12))
        thigh.location = hp + Vector((s_ * 0.03, -0.02, -0.02)); thigh.rotation_euler = (math.radians(-12), 0, math.radians(s_ * 12))
        legs.append(give(thigh, skin_flat))
        knee = hp + Vector((s_ * 0.08, -0.17, -0.08))
        ankle = Vector((s_ * 0.5, -0.12, 0.035))
        legs.append(give(tube("Unterschenkel%d" % s_, [tuple(hp + Vector((s_ * 0.06, -0.08, -0.04))), tuple(knee), tuple(ankle + Vector((0, 0, 0.02)))],
                              [0.07, 0.055, 0.045], segs=12), skin_flat))
        legs.append(give(sphere("Ferse%d" % s_, tuple(ankle), 0.05, (1.0, 1.2, 0.6)), skin_flat))
        legs += toes("Hinten%d" % s_, s_, ankle, 4, 0.15, 0.022, 70, fwd=-0.15)
    attach(join_parts(legs, "Kroete_Beine"), arm, "Body")
    # die Schleim-Bewegung drückt den Körper bis auf 72 % Höhe zusammen: bei der Kröte nur leicht (Kommentar 24.11.: wirkt breitgezogen)
    dampen_scale(arm, ("Body", "Top"), 0.2)
    remove_body(body)

def tendril(name, start, direction, length, r0, curl=1.0, seed=0, n=12):
    """Schattenranke: von start in Richtung direction, dünner werdend und am Ende eingerollt"""
    rnd = random.Random(seed)
    d = Vector(direction).normalized()
    side = d.cross(Vector((0, 0, 1)))
    if side.length < 0.1:
        side = d.cross(Vector((1, 0, 0)))
    side.normalize(); up = side.cross(d).normalized()
    pts, radii = [], []
    p = Vector(start); h = d.copy()
    step = length / (n - 1)
    for i in range(n):
        t = i / (n - 1)
        pts.append(tuple(p)); radii.append(r0 * (1 - t) ** 0.9 + 0.004)
        ang = curl * (0.15 + 0.5 * t * t) + rnd.uniform(-0.05, 0.05)
        h = (h * math.cos(ang) + up * math.sin(ang)).normalized()
        up = side.cross(h).normalized()
        p = p + h * step
    radii[-1] = 0.0
    return tube(name, pts, radii, segs=10)

@variante("schatten_wesen", "koloss")
def schatten_wesen(arm, body):
    """Schattenreich (Welt 9): Schattenwesen – mächtige Gestalt aus glänzend schwarzem Schatten-Schleim mit violett
    glimmenden Adern, eigener Kopf mit drei leuchtenden Augen und gezacktem, violett glühendem Maul, Schattenranken aus
    Rücken, Kopf und Armen, violetten Kristalldornen auf Schultern und Rücken, Klauenhänden. Eigene Figur, kein Nachbau."""
    black = look("Schatten", (0.07, 0.06, 0.1), rough=0.18, metal=0.1)
    black2 = look("Schatten2", (0.12, 0.09, 0.18), rough=0.2, metal=0.1)
    glow = look("Schattenglut", (0.8, 0.4, 1.0), rough=0.3, emit=(0.72, 0.3, 1.0), strength=3.5)
    eye = look("Schattenauge", (0.95, 0.85, 1.0), rough=0.2, emit=(0.85, 0.65, 1.0), strength=5.0)
    thorn = look("Dorn", (0.55, 0.25, 0.85), rough=0.15, emit=(0.5, 0.2, 0.85), strength=1.4)
    fang = look("Schattenzahn", (0.92, 0.9, 1.0), rough=0.3)
    koloss_arms(arm, body, black, thorn, black2, cuff_style="binde", fingers=4, claws=True)
    # Körper: schwarz glänzend, violett glimmende Adern
    m, tex, img, px = body_texture(body)
    h, w = px.shape[:2]
    lum = (0.3 * px[..., 0] + 0.6 * px[..., 1] + 0.1 * px[..., 2])[..., None]
    sheen = fbm(h, w, 6, 71)[..., None]
    base = px.copy(); base[..., :3] = np.array((0.05, 0.04, 0.08)) + lum * 0.08 + sheen * np.array((0.07, 0.03, 0.12))
    tex.image = new_image(body.name + "_Farbe", base)
    edge = voronoi_edges(h, w, 40, 72, warp=0.03)
    k = np.clip(1 - edge / 0.003, 0, 1) ** 1.5 * (fbm(h, w, 5, 73) > 0.45)
    em = np.zeros((h, w, 4), dtype=np.float32); em[..., :3] = k[..., None] * np.array((0.7, 0.3, 1.0)); em[..., 3] = 1
    set_emission(body, em, 2.0)
    p_ = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'); p_.inputs["Roughness"].default_value = 0.22
    # eigener Kopf
    c0, half = cut_head(body)
    H = "mixamorig:Head"
    R = max(half.x, half.z) * 0.95
    hc = c0 + Vector((0, -0.02, -0.02))
    parts = [give(sphere("Kopf", tuple(hc), R, (1.0, 1.05, 0.95), segs=(48, 28)), black)]
    fy = hc.y - R * 1.02
    F = lambda x, dy, z: tuple(Vector((hc.x + x, fy + dy, hc.z + z)))
    for s_ in (-1, 1):
        e = sphere("Auge%d" % s_, (0, 0, 0), 0.075, (1.5, 0.45, 0.75)); e.location = F(s_ * 0.13, 0.05, 0.06); e.rotation_euler = (0, math.radians(s_ * -24), 0)
        parts.append(give(e, eye))
    parts.append(give(sphere("Stirnauge", F(0, 0.04, 0.2), 0.045, (1.0, 0.45, 1.3)), eye))
    # Maul (Kommentar 24.11.: sauber, ohne dass der Kopf in den Mundraum ragt): Fläche folgt der Kopfform knapp über der
    # Oberfläche, scharfer dunkler Rand, Zähne sitzen auf dem Rand
    ax = Vector((R, R * 1.05, R * 0.95))

    def on_head(d, lift=0.0):
        d = Vector(d).normalized()
        t = 1.0 / math.sqrt((d.x / ax.x) ** 2 + (d.y / ax.y) ** 2 + (d.z / ax.z) ** 2)
        n = Vector((d.x / ax.x ** 2, d.y / ax.y ** 2, d.z / ax.z ** 2)).normalized()
        return hc + d * t + n * lift
    P = on_head((0, -1, -0.28))
    N = (on_head((0, -1, -0.28), 0.01) - P).normalized()
    T1 = Vector((1, 0, 0)); T2 = N.cross(T1).normalized()
    if T2.z < 0:
        T2 = -T2
    ma, mb = 0.14, 0.065
    mpt = lambda u, v, lift: on_head(P + T1 * u + T2 * v - hc, lift)
    bm = bmesh.new()
    rings, segs_ = 6, 40
    centre = bm.verts.new(mpt(0, 0, 0.007))
    grid = [[bm.verts.new(mpt(ma * f * math.cos(a_), mb * f * math.sin(a_), 0.007)) for a_ in [k * 2 * math.pi / segs_ for k in range(segs_)]]
            for f in [(i + 1) / rings for i in range(rings)]]
    for k in range(segs_):
        bm.faces.new([centre, grid[0][k], grid[0][(k + 1) % segs_]])
    for i in range(rings - 1):
        for k in range(segs_):
            bm.faces.new([grid[i][k], grid[i + 1][k], grid[i + 1][(k + 1) % segs_], grid[i][(k + 1) % segs_]])
    parts.append(give(finish("Maul", bm), glow))
    rim = [tuple(mpt(ma * math.cos(a_), mb * math.sin(a_), 0.008)) for a_ in [k * 2 * math.pi / 48 for k in range(49)]]
    parts.append(give(tube("Maulrand", rim, [0.013] * len(rim), segs=8), black2))
    for i, u in enumerate((-0.085, 0.0, 0.085)):
        v0 = mb * math.sqrt(max(0.0, 1 - (u / ma) ** 2))
        parts.append(give(tube("Oberzahn%d" % i, [tuple(mpt(u, v0 + 0.004, 0.012)), tuple(mpt(u, v0 - 0.022, 0.014)), tuple(mpt(u * 0.96, v0 - 0.048, 0.012))],
                               [0.021, 0.013, 0.0]), fang))
    for i, u in enumerate((-0.05, 0.05)):
        v0 = -mb * math.sqrt(max(0.0, 1 - (u / ma) ** 2))
        parts.append(give(tube("Unterzahn%d" % i, [tuple(mpt(u, v0 - 0.004, 0.012)), tuple(mpt(u, v0 + 0.02, 0.014)), tuple(mpt(u * 0.96, v0 + 0.042, 0.012))],
                               [0.019, 0.012, 0.0]), fang))
    for i, (dx, dz, dy, L, cu) in enumerate(((-0.18, 0.25, 0.25, 0.42, 1.1), (0.0, 0.32, 0.28, 0.5, 1.2), (0.18, 0.25, 0.25, 0.42, 1.1))):
        parts.append(give(tendril("Kopfranke%d" % i, tuple(hc + Vector((dx, 0.05, dz))), (dx * 1.5, 1.0, 0.6), L, 0.06, cu, seed=i), black2))
    attach(join_parts(parts, "Schatten_Kopf"), arm, H)
    # Ranken und Dornen am Rücken
    sp = arm.matrix_world @ arm.data.bones["mixamorig:Spine2"].head_local
    back = []
    for i, (x, z, dx, dz, L) in enumerate(((-0.25, 0.25, -0.9, 0.5, 0.75), (0.25, 0.25, 0.9, 0.5, 0.75), (-0.18, 0.0, -0.8, -0.1, 0.6),
                                           (0.18, 0.0, 0.8, -0.1, 0.6))):
        p, n = surface(body, (sp.x + x, sp.y + 1.5, sp.z + z), (0, -1, 0))
        if p is not None:
            back.append(give(tendril("Rueckenranke%d" % i, tuple(p - n * 0.03), (dx, 1.0, dz), L, 0.075, 0.9, seed=10 + i), black2))
    for k, (x, z, h_, r, tx, ty) in enumerate(((0.0, 0.32, 0.3, 0.07, -35, 0), (-0.14, 0.18, 0.22, 0.055, -40, -20), (0.14, 0.18, 0.22, 0.055, -40, 20),
                                               (0.0, 0.05, 0.2, 0.05, -50, 0))):
        p, n = surface(body, (sp.x + x, sp.y + 1.5, sp.z + z), (0, -1, 0))
        if p is not None:
            back.append(give(crystal("Rueckendorn%d" % k, tuple(p - n * 0.03), h_, r, (tx, ty, 0)), thorn))
    attach(join_parts(back, "Schatten_Ruecken"), arm, "mixamorig:Spine2")
    for s_, side in ((1, "Left"), (-1, "Right")):
        a0 = arm.matrix_world @ arm.data.bones["mixamorig:%sArm" % side].head_local
        sh = []
        for k, (dx, dy, h_, r, tx, ty) in enumerate(((0.04, 0.0, 0.28, 0.065, 0, 30), (0.13, 0.1, 0.2, 0.05, -15, 55), (-0.03, -0.1, 0.18, 0.045, 25, 18))):
            sh.append(give(crystal("Schulterdorn%s%d" % (side, k), (a0.x + s_ * dx, a0.y + dy, a0.z + 0.13), h_, r, (tx, s_ * ty, 0)), thorn))
        attach(join_parts(sh, "Schatten_Schulter" + side), arm, "mixamorig:%sArm" % side)
        fb = arm.data.bones["mixamorig:%sForeArm" % side]
        f0 = arm.matrix_world @ fb.head_local.lerp(fb.tail_local, 0.35)
        o = tendril("Armranke" + side, tuple(f0 + Vector((s_ * 0.1, 0.05, 0.0))), (s_ * 1.0, 0.6, 0.3), 0.32, 0.04, 1.0, seed=30 + s_)
        attach(give(o, black2), arm, "mixamorig:%sForeArm" % side)

@variante("kristall_kaefer", "panzerkaefer")
def kristall_kaefer(arm, body):
    """Kristallhöhlen (Welt 6): Kristallkäfer – großer Käfer auf sechs Beinen, dessen Panzer aus Kristallgruppen wächst:
    dunkelvioletter Panzer mit pink leuchtenden Kristalladern, großes Kristallhorn auf dem Kopf, Kristallzangen,
    Kristallspitzen an den Beinen, dunkler Körper. Eigene Figur auf dem Skelett des Panzerkäfers."""
    cr = look("Kristall", (1.0, 0.6, 0.95), rough=0.1, emit=(0.95, 0.4, 0.9), strength=0.9)
    cr2 = look("Kristall2", (0.75, 0.5, 1.0), rough=0.1, emit=(0.6, 0.35, 1.0), strength=1.1)
    cr3 = look("Kristall3", (0.55, 0.95, 1.0), rough=0.1, emit=(0.35, 0.9, 1.0), strength=1.3)
    # Panzer (türkis) dunkelviolett mit leuchtenden Adern, Körper (rot) dunkel schiefer
    skin_cracks(body, (1.0, 0.45, 0.95), 30, 0.004, strength=2.2, ch="teal", seed=61)
    recolor(body, lambda px: mask_color(px, "teal"), (0.32, 0.16, 0.48))
    recolor(body, lambda px: mask_color(px, 0, 0.08), (0.3, 0.27, 0.38))
    # Kristallgruppen auf dem Panzer
    rnd = random.Random(5)
    shell = []
    spots = [(0.0, 0.02, 0.2, 0.06), (-0.12, 0.08, 0.15, 0.05), (0.12, 0.06, 0.16, 0.05), (-0.2, -0.04, 0.12, 0.04), (0.2, -0.06, 0.12, 0.04),
             (-0.06, -0.1, 0.13, 0.045), (0.07, -0.12, 0.11, 0.04), (0.0, 0.18, 0.12, 0.045), (-0.16, 0.2, 0.09, 0.035), (0.16, 0.2, 0.09, 0.035),
             (-0.26, 0.1, 0.08, 0.03), (0.27, 0.1, 0.08, 0.03)]
    for i, (x, y, h, r) in enumerate(spots):
        p, n = surface(body, (x, y, 2.0), (0, 0, -1))
        if p is None or p.z < 0.2:
            continue
        for j in range(3 if h > 0.1 else 2):
            tilt = (rnd.uniform(-25, 25) + math.degrees(-n.y) * 0.8, rnd.uniform(-25, 25) + math.degrees(n.x) * 0.8, rnd.uniform(0, 60))
            off = Vector((rnd.uniform(-0.025, 0.025), rnd.uniform(-0.025, 0.025), 0))
            shell.append(give(crystal("Panzerkristall%d_%d" % (i, j), tuple(p + off - n * 0.02), h * (1.0 if j == 0 else 0.65), r * (1.0 if j == 0 else 0.7), tilt),
                              (cr, cr2, cr3)[(i + j) % 3]))
    attach(join_parts(shell, "Kristallpanzer"), arm, "Body")
    # Kopf: großes Kristallhorn nach vorn oben, Kristallzangen
    hb = arm.data.bones["Head"]
    h0 = arm.matrix_world @ hb.head_local; h1 = arm.matrix_world @ hb.tail_local
    hp = []
    # Horn: Fuß steckt in der Stirn, zeigt nach vorn oben (Kommentar 24.11.: direkt am Kopf, ohne Abstand)
    p, n = surface(body, (0.0, -1.5, h0.z + 0.08), (0, 1, 0))
    hp.append(give(crystal("Horn", tuple(p - n * 0.035), 0.2, 0.05, (35, 0, 0)), cr))
    p2, n2 = surface(body, (0.06, -1.5, h0.z + 0.12), (0, 1, 0))
    hp.append(give(crystal("Horn2", tuple(p2 - n2 * 0.03), 0.11, 0.032, (25, 0, -25)), cr2))
    # Zangen: wachsen seitlich aus dem Maul, krümmen sich nach vorn innen
    for s_ in (-1, 1):
        q, m = surface(body, (s_ * 0.075, -1.5, h0.z - 0.04), (0, 1, 0))
        root = q - m * 0.02
        hp.append(give(horn("Zange%d" % s_, tuple(root), tuple(root + Vector((s_ * 0.05, -0.07, -0.005))),
                            tuple(root + Vector((-s_ * 0.03, -0.13, -0.015))), 0.03, n=9), cr3))
    attach(join_parts(hp, "Kristallkopf"), arm, "Head")
    # Kristallspitzen an den Beinenden
    for b in [b.name for b in arm.data.bones if b.name.endswith("_Lo")]:
        bb = arm.data.bones[b]
        t0 = arm.matrix_world @ bb.head_local; t1 = arm.matrix_world @ bb.tail_local
        d = (t1 - t0).normalized()
        o = tube("Spitze" + b, [tuple(t0.lerp(t1, 0.55)), tuple(t1), tuple(t1 + d * 0.04)], [0.028, 0.022, 0.0], segs=6)
        for pl in o.data.polygons:
            pl.use_smooth = False
        attach(give(o, cr2), arm, b)

# ---------------------------------------------------------------- Ablauf

EXPORT_IMAGE_FORMAT = "AUTO"        # Bildformat im GLB; einzelne Bauskripte können "JPEG" setzen (kleinere Dateien)

def run(var, out):
    """Grundmodell laden, Variante bauen, als GLB mit allen Animationen ausgeben (auch für tools/monster)"""
    basis, build = VARIANTEN[var]
    bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, "game/models/enemies_v2/%s.glb" % basis))
    arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    body = next(o for o in bpy.data.objects if o.type == 'MESH' and o.parent == arm)
    arm.data.pose_position = 'REST'
    bpy.context.view_layer.update()
    build(arm, body)
    arm.data.pose_position = 'POSE'
    # Animationen heißen im Spiel „Walk“, „Attack“ (und „Run“); beim Laden hängt Blender „_Armature“ an
    for a in bpy.data.actions:
        if a.name.endswith("_Armature"):
            a.name = a.name[:-len("_Armature")]
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS',
                              export_yup=True, export_apply=False, export_force_sampling=True,
                              export_image_format=EXPORT_IMAGE_FORMAT, export_jpeg_quality=90)
    print("FERTIG", out)

if __name__ == "__main__":
    run(VAR, OUT)
