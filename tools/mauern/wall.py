# Mauer für das Kampffeld in Blender bauen und aus der Spielkamera rendern.
# Aufruf: blender -b -P wall.py -- <planet> <ausgabe.png> [samples]
import bpy, bmesh, math, sys, random, os
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
PLANET = argv[0] if argv else "space_dock"
OUT = argv[1] if len(argv) > 1 else "/tmp/wall.png"
SAMPLES = int(argv[2]) if len(argv) > 2 else 64
random.seed(7)

# --- Szene leeren ---
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# Godot (x, y, z) -> Blender (x, -z, y)
def g2b(x, y, z):
    return Vector((x, -z, y))

# --- Kamera wie im Spiel (Battle.BACKDROP_CAM_*) ---
cam_data = bpy.data.cameras.new("Cam")
cam_data.sensor_fit = 'VERTICAL'
cam_data.angle = math.radians(52.0)
cam = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam)
cam.location = g2b(0, 15.96, 19.51)
look = g2b(0, 0, -8.87)
d = look - cam.location
cam.rotation_mode = 'QUATERNION'
cam.rotation_quaternion = d.to_track_quat('-Z', 'Y')
scene.camera = cam

r = scene.render
r.resolution_x, r.resolution_y = 780, 1688
r.resolution_percentage = 100
r.use_border = True
r.use_crop_to_border = True
r.border_min_x, r.border_max_x = 0.0, 1.0
r.border_min_y = (1688 - 1200) / 1688
r.border_max_y = (1688 - 940) / 1688
r.film_transparent = True
STYLE = os.environ.get("WALLSTYLE", "comic") if "os" in dir() else "comic"
r.engine = 'BLENDER_EEVEE'
scene.eevee.taa_render_samples = SAMPLES
scene.eevee.use_bloom = True
scene.eevee.bloom_threshold = 0.9
scene.eevee.bloom_intensity = 0.06
scene.eevee.bloom_radius = 4.0
scene.eevee.use_soft_shadows = True
scene.eevee.shadow_cube_size = '2048'
scene.eevee.shadow_cascade_size = '4096'
scene.eevee.use_gtao = True
scene.eevee.gtao_distance = 0.6
try:
    pass
except Exception:
    pass
r.image_settings.file_format = 'PNG'
r.image_settings.color_mode = 'RGBA'
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'

# Comic-Umriss wie bei den Figuren
import os
r.use_freestyle = os.environ.get("NOFS") is None
r.line_thickness_mode = 'ABSOLUTE'
r.line_thickness = 2.4
ls = scene.view_layers[0].freestyle_settings.linesets.new("Umriss")
ls.select_by_visibility = True
ls.select_by_edge_types = True
ls.select_by_collection = True
ls.collection_negation = "EXCLUSIVE"
ls.select_silhouette = True
ls.select_border = True
ls.select_crease = True
scene.view_layers[0].freestyle_settings.crease_angle = math.radians(120)
ls.linestyle = bpy.data.linestyles.new("Umriss")
ls.linestyle.color = (0.04, 0.05, 0.12)
ls.linestyle.thickness = 2.6
for other in scene.view_layers[0].freestyle_settings.linesets:
    if other.linestyle is None:
        other.linestyle = ls.linestyle
    if other != ls:
        other.show_render = False

# --- Welt und Licht ---
world = bpy.data.worlds.new("W")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.05, 0.08, 0.18, 1)
bg.inputs[1].default_value = 0.9

def light(kind, name, loc, rot, energy, color, size=1.0):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = color
    if kind == 'AREA':
        ld.size = size
    if kind == 'SUN':
        ld.angle = math.radians(8)
    o = bpy.data.objects.new(name, ld)
    scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    return o

# --- Materialien ---
def mat(name, color, metal=0.0, rough=0.5, emit=None, strength=0.0, noise=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metal
    p.inputs["Roughness"].default_value = rough
    if emit:
        p.inputs["Emission Color"].default_value = (*emit, 1)
        p.inputs["Emission Strength"].default_value = strength
    if noise > 0:
        tex = nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = 18.0
        tex.inputs["Detail"].default_value = 6.0
        ramp = nt.nodes.new("ShaderNodeMapRange")
        ramp.inputs["To Min"].default_value = rough - noise
        ramp.inputs["To Max"].default_value = rough + noise
        nt.links.new(tex.outputs["Fac"], ramp.inputs["Value"])
        nt.links.new(ramp.outputs["Result"], p.inputs["Roughness"])
        # leichte Farbschwankung (Gebrauchsspuren)
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = 'RGBA'
        mix.inputs["Factor"].default_value = 0.0
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["To Min"].default_value = 0.0
        mr.inputs["To Max"].default_value = 0.25
        nt.links.new(tex.outputs["Fac"], mr.inputs["Value"])
        nt.links.new(mr.outputs["Result"], mix.inputs["Factor"])
        mix.inputs[6].default_value = (*color, 1)
        mix.inputs[7].default_value = (color[0] * 0.6, color[1] * 0.6, color[2] * 0.6, 1)
        nt.links.new(mix.outputs[2], p.inputs["Base Color"])
    return m

# --- Bausteine ---
def box(name, center, size, material, bevel=0.03, segs=3):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    o = bpy.context.active_object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        b = o.modifiers.new("Bevel", 'BEVEL')
        b.width = bevel
        b.segments = segs
        b.limit_method = 'ANGLE'
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    o.data.use_auto_smooth = True if hasattr(o.data, "use_auto_smooth") else None
    return o

def cyl(name, center, radius, depth, material, rot=(0, 0, 0), verts=24, bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=center,
                                        rotation=[math.radians(a) for a in rot])
    o = bpy.context.active_object
    o.name = name
    if bevel > 0:
        b = o.modifiers.new("Bevel", 'BEVEL')
        b.width = bevel
        b.segments = 2
        b.limit_method = 'ANGLE'
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return o

def sphere(name, center, radius, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=radius, location=center)
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return o


def prism(name, x0, x1, profile, material, bevel=0.03, segs=3):
    """Profil (Liste von (y, z) gegen den Uhrzeigersinn) entlang x von x0 bis x1 ausziehen."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    a = [bm.verts.new((x0, y, z)) for (y, z) in profile]
    b = [bm.verts.new((x1, y, z)) for (y, z) in profile]
    n = len(profile)
    bm.faces.new(list(reversed(a)))
    bm.faces.new(b)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([a[i], a[j], b[j], b[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    o.data.materials.append(material)
    if bevel > 0:
        bv = o.modifiers.new("Bevel", 'BEVEL')
        bv.width = bevel
        bv.segments = segs
        bv.limit_method = 'ANGLE'
    for f in me.polygons:
        f.use_smooth = True
    return o

# Teile ohne Umriss (Energiefelder, Leuchten)
nolines = bpy.data.collections.new("OhneUmriss")
scene.collection.children.link(nolines)
def no_outline(o):
    for c in list(o.users_collection):
        c.objects.unlink(o)
    nolines.objects.link(o)
    return o

def shield_mat(name, color, strength=3.0, alpha=0.35):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*color, 1)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    # Verlauf von unten (kräftig) nach oben (aus), dazu feine Waben
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (alpha, alpha, alpha, 1)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (0, 0, 0, 1)
    nt.links.new(sep.outputs[1], ramp.inputs[0])
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.feature = 'DISTANCE_TO_EDGE'
    vor.inputs["Scale"].default_value = 3.2
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    nt.links.new(geo.outputs["Position"], vor.inputs["Vector"])
    edge = nt.nodes.new("ShaderNodeMapRange")
    edge.inputs["From Min"].default_value = 0.0
    edge.inputs["From Max"].default_value = 0.06
    edge.inputs["To Min"].default_value = 1.0
    edge.inputs["To Max"].default_value = 0.35
    nt.links.new(vor.outputs["Distance"], edge.inputs["Value"])
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = 'MULTIPLY'
    nt.links.new(ramp.outputs[0], mul.inputs[0])
    nt.links.new(edge.outputs["Result"], mul.inputs[1])
    nt.links.new(mul.outputs[0], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    em.inputs[1].default_value = strength
    nt.links.new(mix.outputs[0], out.inputs[0])
    m.blend_method = 'BLEND'
    return m


def stripes(name, c1, c2, scale=6.0, metal=0.3, rough=0.45):
    """Warnstreifen (schräge Bänder) in zwei Farben."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Metallic"].default_value = metal
    p.inputs["Roughness"].default_value = rough
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (0, math.radians(45), 0)
    wv = nt.nodes.new("ShaderNodeTexWave")
    wv.wave_type = 'BANDS'
    wv.bands_direction = 'X'
    wv.inputs["Scale"].default_value = scale
    wv.inputs["Distortion"].default_value = 0.0
    cr = nt.nodes.new("ShaderNodeValToRGB")
    cr.color_ramp.interpolation = 'CONSTANT'
    cr.color_ramp.elements[0].color = (*c1, 1)
    cr.color_ramp.elements[1].position = 0.5
    cr.color_ramp.elements[1].color = (*c2, 1)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], wv.inputs["Vector"])
    nt.links.new(wv.outputs["Fac"], cr.inputs[0])
    nt.links.new(cr.outputs[0], p.inputs["Base Color"])
    return m


def toon(name, color, shade=0.55, light=1.18, gloss=0.45, rim=None, rim_amount=0.35, emit=None, strength=0.0):
    """Comic-Material: Licht in drei harten Stufen, Glanzpunkt, Randlicht in der Planetenfarbe.
    Farben als sRGB (wie im Malprogramm), intern linear."""
    lin = lambda c: tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)
    color = lin(color)
    if rim:
        rim = lin(rim)
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
    dif.inputs[0].default_value = (1, 1, 1, 1)
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    nt.links.new(dif.outputs[0], s2r.inputs[0])
    bw = nt.nodes.new("ShaderNodeRGBToBW")
    nt.links.new(s2r.outputs[0], bw.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = 'CONSTANT'
    el = ramp.color_ramp.elements
    el[0].position = 0.0
    el[0].color = (color[0] * shade * 0.75, color[1] * shade * 0.75, color[2] * shade * 0.85, 1)
    el[1].position = 0.12
    el[1].color = (color[0] * shade, color[1] * shade, color[2] * shade, 1)
    e2 = el.new(0.32)
    e2.color = (*color, 1)
    e3 = el.new(0.7)
    e3.color = (min(1, color[0] * light), min(1, color[1] * light), min(1, color[2] * light), 1)
    nt.links.new(bw.outputs[0], ramp.inputs[0])
    col = ramp.outputs[0]
    # Glanzpunkt
    if gloss > 0:
        gl = nt.nodes.new("ShaderNodeBsdfGlossy")
        gl.inputs["Roughness"].default_value = 0.22
        s2 = nt.nodes.new("ShaderNodeShaderToRGB")
        nt.links.new(gl.outputs[0], s2.inputs[0])
        b2 = nt.nodes.new("ShaderNodeRGBToBW")
        nt.links.new(s2.outputs[0], b2.inputs[0])
        r2 = nt.nodes.new("ShaderNodeMapRange")
        r2.interpolation_type = 'STEPPED'
        r2.inputs["From Min"].default_value = 0.55
        r2.inputs["From Max"].default_value = 0.56
        r2.inputs["To Max"].default_value = gloss
        r2.clamp = True
        nt.links.new(b2.outputs[0], r2.inputs["Value"])
        add = nt.nodes.new("ShaderNodeMix")
        add.data_type = 'RGBA'
        add.blend_type = 'ADD'
        add.inputs["Factor"].default_value = 1.0
        nt.links.new(col, add.inputs[6])
        rgb = nt.nodes.new("ShaderNodeCombineColor")
        for k in range(3):
            nt.links.new(r2.outputs[0], rgb.inputs[k])
        nt.links.new(rgb.outputs[0], add.inputs[7])
        col = add.outputs[2]
    # Randlicht (Kante zur Kamera hin abgewandt)
    if rim:
        lw = nt.nodes.new("ShaderNodeLayerWeight")
        lw.inputs["Blend"].default_value = 0.35
        r3 = nt.nodes.new("ShaderNodeMapRange")
        r3.interpolation_type = 'STEPPED'
        r3.inputs["From Min"].default_value = 0.62
        r3.inputs["From Max"].default_value = 0.63
        r3.inputs["To Max"].default_value = rim_amount
        r3.clamp = True
        nt.links.new(lw.outputs["Facing"], r3.inputs["Value"])
        mx = nt.nodes.new("ShaderNodeMix")
        mx.data_type = 'RGBA'
        nt.links.new(r3.outputs[0], mx.inputs["Factor"])
        nt.links.new(col, mx.inputs[6])
        mx.inputs[7].default_value = (*rim, 1)
        col = mx.outputs[2]
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(col, em.inputs[0])
    em.inputs[1].default_value = 1.0
    if emit:
        e2n = nt.nodes.new("ShaderNodeEmission")
        e2n.inputs[0].default_value = (*emit, 1)
        e2n.inputs[1].default_value = strength
        ad = nt.nodes.new("ShaderNodeAddShader")
        nt.links.new(em.outputs[0], ad.inputs[0])
        nt.links.new(e2n.outputs[0], ad.inputs[1])
        nt.links.new(ad.outputs[0], out.inputs[0])
    else:
        nt.links.new(em.outputs[0], out.inputs[0])
    return m

def glowmat(name, color, strength=4.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*color, 1)
    em.inputs[1].default_value = strength
    nt.links.new(em.outputs[0], out.inputs[0])
    return m

def glare(threshold=1.0, size=7):
    scene.use_nodes = True
    nt = scene.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    rl = nt.nodes.new("CompositorNodeRLayers")
    gl = nt.nodes.new("CompositorNodeGlare")
    gl.glare_type = 'FOG_GLOW'
    gl.quality = 'HIGH'
    gl.threshold = threshold
    gl.size = size
    comp = nt.nodes.new("CompositorNodeComposite")
    nt.links.new(rl.outputs["Image"], gl.inputs["Image"])
    nt.links.new(gl.outputs["Image"], comp.inputs["Image"])

ls.collection = nolines
KIT_DIR = os.path.dirname(os.path.abspath(__file__))
if STYLE == "detail":
    r.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = SAMPLES
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.008
    scene.cycles.sample_clamp_indirect = 2.0
    scene.cycles.use_denoising = False
    r.use_freestyle = False
    exec(open(os.path.join(KIT_DIR, "detail_kit.py")).read())
    exec(open(os.path.join(KIT_DIR, "planet_%s_detail.py" % PLANET)).read())
elif STYLE == "streng":
    # wie die gemalten Schlachtfelder: Cycles, keine Umrisse, Leuchten über den Compositor
    r.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = False
    r.use_freestyle = False
    exec(open(os.path.join(KIT_DIR, "planet_%s_streng.py" % PLANET)).read())
else:
    exec(open(os.path.join(KIT_DIR, "planet_%s.py" % PLANET)).read())

bpy.context.view_layer.update()
r.filepath = OUT
bpy.ops.render.render(write_still=True)
print("GERENDERT", OUT)
