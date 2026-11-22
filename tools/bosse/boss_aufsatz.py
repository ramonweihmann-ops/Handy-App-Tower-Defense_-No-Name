# Bosse je Welt: Aufsätze und Oberfläche auf die zwei Boss-Modelle setzen (Wunsch 22.11.2026, ohne Meshy).
# Aufruf: blender -b -P tools/bosse/boss_aufsatz.py -- <variante> <ziel.glb>
#   variante: frost_schleimmutter, lava_koloss, … (siehe VARIANTEN unten)
# Ablauf: Grundmodell laden (game/models/enemies_v2/<basis>.glb), Aufsätze bauen und an Knochen hängen (bewegen sich
# mit Lauf- und Angriffsanimation), auf Wunsch die Textur des Grundmodells verändern (Reif, leuchtende Risse), als GLB
# mit allen Animationen ausgeben. Ohne Backen (Cycles-Backen liefert im Blender dieser Umgebung nur Schwarz): Aufsätze
# haben feste Farben und sind aus mehreren Teilen gebaut, Texturen werden mit numpy direkt im UV-Raum gezeichnet.
import bpy, bmesh, sys, os, math, random
import numpy as np
from mathutils import Vector

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

def sphere(name, loc, r, squash=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=r)
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
    et = m.node_tree.nodes.new("ShaderNodeTexImage"); et.image = new_image(body.name + "_Leuchten", em)
    p = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    m.node_tree.links.new(et.outputs["Color"], p.inputs["Emission Color"])
    p.inputs["Emission Strength"].default_value = strength

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

@variante("frost_schleimmutter", "schleimmutter")
def frost(arm, body):
    """Frostmond (Welt 3): Eiskrone hinter den Kugeln, Eiszapfen an der Schleimkappe, Eissplitter, Reif auf dem Schleim"""
    ice = look("Eis", (0.8, 0.94, 1.0), rough=0.08, emit=(0.55, 0.85, 1.0), strength=0.4)
    ice_deep = look("EisTief", (0.42, 0.7, 0.98), rough=0.1, emit=(0.35, 0.7, 1.0), strength=0.6)
    crown = [((0.0, 0.14, 0.4), 0.28, 0.065, (-8, 0, 0)), ((-0.14, 0.12, 0.38), 0.2, 0.05, (-6, -24, 0)),
             ((0.14, 0.12, 0.38), 0.21, 0.05, (-6, 24, 0)), ((-0.27, 0.06, 0.3), 0.14, 0.042, (0, -45, 0)),
             ((0.27, 0.06, 0.3), 0.14, 0.042, (0, 45, 0)), ((-0.07, 0.2, 0.36), 0.16, 0.04, (-30, -10, 0)),
             ((0.07, 0.2, 0.36), 0.15, 0.04, (-30, 12, 0))]
    for i, (loc, h, r, tilt) in enumerate(crown):
        attach(give(crystal("Krone%d" % i, loc, h, r, tilt), ice if i % 2 == 0 else ice_deep), arm, "Top")
    # Eiszapfen hängen unter der Schleimkappe (oberes Ende steckt in der Kappe), unterschiedlich lang
    rim = lambda x: (x, -0.33 + abs(x) * 0.3 + x * x * 0.6, 0.28 - abs(x) * 0.12)
    for i, x in enumerate((-0.34, -0.22, -0.1, 0.03, 0.15, 0.27)):
        _, y, z = rim(x)
        L = random.uniform(0.1, 0.18)
        attach(give(tube("Zapfen%d" % i, [(x, y + 0.03, z + 0.03), (x, y - 0.004, z - L * 0.35), (x, y - 0.01, z - L)],
                         [0.032, 0.019, 0.0]), ice), arm, "Top")
    for i, (loc, tilt) in enumerate((((-0.44, -0.05, 0.1), (0, -70, 10)), ((0.44, -0.02, 0.09), (0, 70, -10)),
                                     ((-0.36, 0.22, 0.14), (25, -55, 0)), ((0.34, 0.24, 0.13), (25, 55, 0)))):
        attach(give(crystal("Splitter%d" % i, loc, 0.1, 0.032, tilt), ice_deep), arm, "Body")
    frost_skin(body, ch="teal")

@variante("lava_koloss", "koloss")
def lava(arm, body):
    """Lava-Kolonie (Welt 4): Basalthörner mit Glutspitze, Magmabrocken auf den Schultern, Rückenstacheln, glühende Hautrisse"""
    basalt = look("Basalt", (0.27, 0.21, 0.2), rough=0.7)
    glut = look("Glut", (1.0, 0.4, 0.08), rough=0.5, emit=(1.0, 0.36, 0.05), strength=3.0)
    for s in (-1, 1):
        o = horn("Horn%d" % s, (s * 0.17, 0.12, 1.5), (s * 0.42, 0.12, 1.58), (s * 0.44, -0.06, 1.88), 0.09, glow_from=7)
        attach(give(o, basalt, glut), arm, "mixamorig:Head")
        side = "Left" if s > 0 else "Right"
        for k, (dx, dy, dz, sz) in enumerate(((0.0, 0.05, 0.14, 0.15), (0.13, 0.13, 0.06, 0.11), (-0.09, -0.07, 0.07, 0.1))):
            for o in magma_rock("Brocken%s%d" % (side, k), (s * (0.56 + dx), 0.06 + dy, 1.3 + dz), sz, basalt, glut, seed=k + (5 if s > 0 else 0)):
                attach(o, arm, "mixamorig:%sArm" % side)
    for k, (x, z, L) in enumerate(((0.0, 1.32, 0.32), (-0.17, 1.2, 0.24), (0.17, 1.2, 0.24), (0.0, 1.05, 0.22))):
        o = horn("Ruecken%d" % k, (x, 0.3, z), (x, 0.44, z + L * 0.45), (x * 1.3, 0.52, z + L), 0.075, n=8, glow_from=5)
        attach(give(o, basalt, glut), arm, "mixamorig:Spine2")
    skin_cracks(body, (1.0, 0.45, 0.08), 70, 0.0035, strength=2.2, ch=1)

# ---------------------------------------------------------------- Ablauf

basis, build = VARIANTEN[VAR]
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
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS',
                          export_yup=True, export_apply=False, export_force_sampling=True)
print("FERTIG", OUT)
