# Baukasten für Mauern im Stil der gemalten Brücken. Erwartet CFG (dict) mit den Farben und Zierteilen des Planeten.
def lin(c):
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)

def surface(name, color, metal=0.7, rough=0.32, var=0.12, cracks=None, crack_emit=0.0, crack_scale=4.0, brushed=True):
    """Metall oder Stein mit Gebrauchsspuren; cracks = Farbe feiner Risse (Eis weiß, Lava glühend)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Metallic"].default_value = metal
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (2.0, 40.0, 40.0) if brushed else (6.0, 6.0, 6.0)
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 6.0
    nz.inputs["Detail"].default_value = 8.0
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
    rr = nt.nodes.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = rough - 0.08
    rr.inputs["To Max"].default_value = rough + 0.12
    nt.links.new(nz.outputs["Fac"], rr.inputs["Value"])
    nt.links.new(rr.outputs["Result"], p.inputs["Roughness"])
    nz2 = nt.nodes.new("ShaderNodeTexNoise")
    nz2.inputs["Scale"].default_value = 3.0
    nz2.inputs["Detail"].default_value = 4.0
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = 'RGBA'
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.45
    mr.inputs["From Max"].default_value = 0.7
    mr.inputs["To Max"].default_value = var
    nt.links.new(nz2.outputs["Fac"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], mx.inputs["Factor"])
    mx.inputs[6].default_value = (*color, 1)
    mx.inputs[7].default_value = (color[0] * 0.45, color[1] * 0.45, color[2] * 0.5, 1)
    col = mx.outputs[2]
    if cracks:
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        vor = nt.nodes.new("ShaderNodeTexVoronoi")
        vor.feature = 'DISTANCE_TO_EDGE'
        vor.inputs["Scale"].default_value = crack_scale
        msk = nt.nodes.new("ShaderNodeTexNoise")
        msk.inputs["Scale"].default_value = 1.6
        mskr = nt.nodes.new("ShaderNodeMapRange")
        mskr.inputs["From Min"].default_value = CFG.get("crack_mask", 0.0)
        mskr.inputs["From Max"].default_value = CFG.get("crack_mask", 0.0) + 0.05
        nt.links.new(msk.outputs["Fac"], mskr.inputs["Value"])
        warp = nt.nodes.new("ShaderNodeTexNoise")
        warp.inputs["Scale"].default_value = 2.5
        add = nt.nodes.new("ShaderNodeVectorMath")
        add.operation = 'ADD'
        sc = nt.nodes.new("ShaderNodeVectorMath")
        sc.operation = 'SCALE'
        sc.inputs["Scale"].default_value = 0.25
        nt.links.new(warp.outputs["Color"], sc.inputs[0])
        nt.links.new(geo.outputs["Position"], add.inputs[0])
        nt.links.new(sc.outputs[0], add.inputs[1])
        nt.links.new(add.outputs[0], vor.inputs["Vector"])
        th = nt.nodes.new("ShaderNodeMapRange")
        th.inputs["From Min"].default_value = 0.0
        th.inputs["From Max"].default_value = CFG.get("crack_width", 0.035)
        th.inputs["To Min"].default_value = 1.0
        th.inputs["To Max"].default_value = 0.0
        nt.links.new(vor.outputs["Distance"], th.inputs["Value"])
        mm = nt.nodes.new("ShaderNodeMath")
        mm.operation = 'MULTIPLY'
        nt.links.new(th.outputs["Result"], mm.inputs[0])
        nt.links.new(mskr.outputs["Result"], mm.inputs[1])
        th = mm
        mx2 = nt.nodes.new("ShaderNodeMix")
        mx2.data_type = 'RGBA'
        nt.links.new(th.outputs[0], mx2.inputs["Factor"])
        nt.links.new(col, mx2.inputs[6])
        mx2.inputs[7].default_value = (*cracks, 1)
        col = mx2.outputs[2]
        if crack_emit > 0:
            p.inputs["Emission Color"].default_value = (*cracks, 1)
            mul = nt.nodes.new("ShaderNodeMath")
            mul.operation = 'MULTIPLY'
            mul.inputs[1].default_value = crack_emit
            nt.links.new(th.outputs[0], mul.inputs[0])
            nt.links.new(mul.outputs[0], p.inputs["Emission Strength"])
    nt.links.new(col, p.inputs["Base Color"])
    return m

C = CFG
light_steel = surface("Block", C["block"], metal=C.get("metal", 0.7), rough=C.get("rough", 0.32),
                      cracks=C.get("block_cracks"), crack_emit=C.get("crack_emit", 0.0), brushed=C.get("brushed", True))
deck = surface("Deck", C["deck"], metal=C.get("metal", 0.65), rough=C.get("rough", 0.36) + 0.04,
               cracks=C.get("deck_cracks"), crack_emit=C.get("crack_emit", 0.0), brushed=C.get("brushed", True))
dark = mat("Schwarz", C.get("recess", (0.015, 0.02, 0.04)), metal=0.4, rough=0.6)
screw = mat("Schraube", C.get("screw", (0.4, 0.45, 0.6)), metal=0.9, rough=0.25)
neon = mat("Neon", C["neon"], emit=C["neon"], strength=C.get("neon_strength", 4.0))
lampm = mat("Lampe", C.get("lamp", (1.0, 0.55, 0.15)), emit=C.get("lamp", (1.0, 0.55, 0.15)), strength=C.get("lamp_strength", 6.0))

HALF = 6.4
FR = -0.6
MODS = [-5.4, -3.6, -1.8, 0.0, 1.8, 3.6, 5.4]

box("Sockel", (0, -0.15, 0.14), (HALF * 2, 0.95, 0.28), deck, bevel=0.025)
for x in [-6.3 + k * 0.9 for k in range(15)]:
    box("SockelFuge%.1f" % x, (x, FR - 0.03, 0.14), (0.02, 0.02, 0.24), dark, bevel=0.0)

def screw4(cx, y, cz, w, h, top=False):
    for sx in (-1, 1):
        for sz in (-1, 1):
            if top:
                cyl("S", (cx + sx * w, y + sz * h, cz), 0.03, 0.015, screw, verts=12)
            else:
                cyl("S", (cx + sx * w, y, cz + sz * h), 0.035, 0.02, screw, rot=(90, 0, 0), verts=12, bevel=0.005)

edges = [-HALF] + MODS + [HALF]
for i in range(len(edges) - 1):
    x0 = edges[i] + (0.38 if i > 0 else 0.0)
    x1 = edges[i + 1] - (0.38 if i < len(edges) - 2 else 0.0)
    w = x1 - x0
    cx = (x0 + x1) / 2
    box("Wand%d" % i, (cx, -0.12, 0.62), (w, 0.8, 0.7), deck, bevel=0.03)
    box("Fuge%d" % i, (cx, FR + 0.075, 0.62), (0.025, 0.02, 0.6), dark, bevel=0.0)
    box("FugeQ%d" % i, (cx, FR + 0.075, 0.62), (w - 0.1, 0.02, 0.02), dark, bevel=0.0)
    if C.get("screws", True):
        screw4(cx, FR + 0.07, 0.62, w / 2 - 0.12, 0.25)
    box("Fassung%d" % i, (cx, -0.12, 1.05), (w + 0.02, 0.86, 0.16), light_steel, bevel=0.03)
    box("Rinne%d" % i, (cx, FR + 0.05, 1.05), (w - 0.06, 0.06, 0.08), dark, bevel=0.01)
    cyl("Neon%d" % i, (cx, FR + 0.04, 1.05), 0.032, w - 0.1, neon, rot=(0, 90, 0), verts=12)
    box("OberPlatte%d" % i, (cx, -0.1, 1.135), (w - 0.14, 0.6, 0.02), deck, bevel=0.008)
    box("OberNeon%d" % i, (cx, -0.1, 1.15), (w * 0.35, 0.05, 0.015), neon, bevel=0.0)
    if C.get("screws", True):
        screw4(cx, -0.1, 1.15, w / 2 - 0.16, 0.22, top=True)

for i, x in enumerate(MODS):
    box("Block%d" % i, (x, -0.13, 0.72), (0.76, 0.92, 1.24), light_steel, bevel=0.05)
    box("BlockKappe%d" % i, (x, -0.13, 1.37), (0.82, 0.98, 0.08), deck, bevel=0.03)
    box("KappeInnen%d" % i, (x, -0.13, 1.415), (0.6, 0.76, 0.02), light_steel, bevel=0.008)
    box("KappeSchlitz%d" % i, (x, -0.13, 1.43), (0.36, 0.06, 0.01), dark, bevel=0.0)
    if C.get("screws", True):
        screw4(x, -0.13, 1.43, 0.24, 0.3, top=True)
    if C.get("vents", True):
        box("Gitter%d" % i, (x, FR - 0.06, 0.95), (0.44, 0.03, 0.34), dark, bevel=0.01)
        for k in range(5):
            box("Lamelle%d_%d" % (i, k), (x, FR - 0.075, 0.82 + k * 0.065), (0.4, 0.02, 0.022), light_steel, bevel=0.004)
    box("LampeFassung%d" % i, (x, FR - 0.06, 0.45), (0.2, 0.03, 0.3), dark, bevel=0.01)
    box("Lampe%d" % i, (x, FR - 0.075, 0.45), (0.11, 0.02, 0.22), lampm, bevel=0.0)
    box("Schlitz%d" % i, (x, FR - 0.065, 1.2), (0.3, 0.02, 0.04), dark, bevel=0.0)
    if C.get("edge_neon", True):
        for sx in (-1, 1):
            cyl("KantenNeon%d_%d" % (i, sx), (x + sx * 0.36, FR - 0.04, 0.72), 0.022, 1.0, neon, verts=10)

# Zierteile: Kristalle auf den Blöcken (Eis, Nebel)
if C.get("crystals"):
    cm = mat("Kristall", C["crystals"], metal=0.0, rough=0.35, emit=C["crystals"], strength=C.get("crystal_glow", 1.2))
    cm.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.2
    random.seed(3)
    for i, x in enumerate(MODS):
        for k in range(3):
            h = random.uniform(0.28, 0.5) * (1.25 if k == 0 else 1.0)
            dx = [0.0, -0.17, 0.16][k]
            dy = [0.0, 0.12, -0.08][k]
            tilt = [0, -18, 20][k]
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.07 if k else 0.09, depth=h, location=(x + dx, -0.13 + dy, 1.42 + h / 2))
            body = bpy.context.active_object
            bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.07 if k else 0.09, radius2=0.0, depth=0.14, location=(x + dx, -0.13 + dy, 1.42 + h + 0.07))
            tip = bpy.context.active_object
            for o in (body, tip):
                o.data.materials.append(cm)
                o.rotation_euler = (0, math.radians(tilt), 0)
            tip.location.x += math.sin(math.radians(tilt)) * (h / 2 + 0.07)
            tip.location.z -= (1 - math.cos(math.radians(tilt))) * (h / 2 + 0.07)


# --- weitere Zierteile je Planet ---
P = C.get("props", [])
def pmat(name, color, metal=0.0, rough=0.5, emit=None, strength=0.0):
    return mat(name, color, metal=metal, rough=rough, emit=emit, strength=strength)

def curve_tube(name, pts, radius, material):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius
    cu.bevel_resolution = 3
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu)
    scene.collection.objects.link(o)
    o.data.materials.append(material)
    return o

random.seed(11)
if "vines" in P:
    vine = pmat("Ranke", (0.12, 0.3, 0.08), rough=0.6)
    leaf = pmat("Blatt", (0.2, 0.55, 0.12), rough=0.5)
    for i in range(len(edges) - 1):
        x0 = edges[i] + 0.3
        x1 = edges[i + 1] - 0.3
        pts = [(x0, FR + 0.02, 1.12), ((x0 + x1) / 2, FR - 0.04, 0.82 + random.uniform(-0.08, 0.06)), (x1, FR + 0.02, 1.12)]
        curve_tube("Ranke%d" % i, pts, 0.035, vine)
        for k in range(5):
            t = (k + 0.5) / 5
            x = x0 + (x1 - x0) * t
            z = 1.12 - 0.3 * math.sin(t * math.pi) + random.uniform(-0.05, 0.05)
            l = sphere("Blatt%d_%d" % (i, k), (x, FR - 0.06, z), 0.07, leaf)
            l.scale = (1.4, 0.35, 0.8)
            l.rotation_euler = (0, random.uniform(-0.8, 0.8), 0)
    for i, x in enumerate(MODS):
        pts = [(x - 0.4, FR - 0.02, 0.2), (x - 0.38, FR - 0.08, 0.7), (x + 0.1, FR - 0.08, 1.1), (x + 0.4, FR - 0.02, 1.35)]
        curve_tube("BlockRanke%d" % i, pts, 0.03, vine)
if "portholes" in P:
    brass = pmat("Messing", (0.85, 0.6, 0.25), metal=0.9, rough=0.25)
    glass = pmat("Bullauge", (1.0, 0.75, 0.35), emit=(1.0, 0.68, 0.28), strength=2.0)
    for i, x in enumerate(MODS):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.17, minor_radius=0.045, location=(x, FR - 0.08, 0.92), rotation=(math.radians(90), 0, 0))
        t = bpy.context.active_object
        t.data.materials.append(brass)
        bpy.ops.object.shade_smooth()
        cyl("Glas%d" % i, (x, FR - 0.07, 0.92), 0.14, 0.03, glass, rot=(90, 0, 0), verts=24)
if "rope" in P:
    rope = pmat("Tau", (0.72, 0.6, 0.42), rough=0.8)
    for i in range(len(edges) - 1):
        x0 = edges[i] + 0.36
        x1 = edges[i + 1] - 0.36
        curve_tube("Tau%d" % i, [(x0, FR - 0.05, 1.3), ((x0 + x1) / 2, FR - 0.1, 1.16), (x1, FR - 0.05, 1.3)], 0.045, rope)
if "hazard" in P:
    warn = stripes("Warn", (0.95, 0.7, 0.1), (0.05, 0.05, 0.06), scale=10.0)
    for i in range(len(edges) - 1):
        x0 = edges[i] + (0.38 if i > 0 else 0.0)
        x1 = edges[i + 1] - (0.38 if i < len(edges) - 2 else 0.0)
        box("Warn%d" % i, ((x0 + x1) / 2, FR + 0.04, 0.32), (x1 - x0 - 0.1, 0.02, 0.1), warn, bevel=0.0)
if "rods" in P:
    rodm = pmat("Stab", (0.5, 0.52, 0.58), metal=0.9, rough=0.3)
    tipm = pmat("Funke", (1.0, 0.9, 0.5), emit=(1.0, 0.85, 0.4), strength=8.0)
    for i, x in enumerate(MODS):
        cyl("Stab%d" % i, (x + 0.22, -0.13, 1.7), 0.022, 0.6, rodm, verts=8)
        sphere("Spitze%d" % i, (x + 0.22, -0.13, 2.02), 0.045, tipm)
if "pipe" in P:
    copper = pmat("Kupfer", (0.72, 0.38, 0.2), metal=0.9, rough=0.35)
    cyl("Rohr", (0, FR - 0.1, 0.36), 0.08, HALF * 2, copper, rot=(0, 90, 0), verts=16)
    for x in [-5.85, -4.5, -2.7, -0.9, 0.9, 2.7, 4.5, 5.85]:
        cyl("Flansch%.1f" % x, (x, FR - 0.1, 0.36), 0.11, 0.07, copper, rot=(0, 90, 0), verts=16, bevel=0.01)
if "gold_balls" in P:
    goldm = pmat("Gold", (1.0, 0.75, 0.3), metal=1.0, rough=0.2)
    for i, x in enumerate(MODS):
        cyl("Sockelchen%d" % i, (x, -0.13, 1.48), 0.1, 0.08, goldm, verts=16)
        sphere("Kugel%d" % i, (x, -0.13, 1.62), 0.13, goldm)
if "mushrooms" in P:
    stem = pmat("Stiel", (0.85, 0.8, 0.65), rough=0.6)
    caps = [pmat("HutOrange", (1.0, 0.42, 0.08), emit=(1.0, 0.38, 0.06), strength=1.3),
            pmat("HutTuerkis", (0.1, 0.8, 0.8), emit=(0.08, 0.75, 0.78), strength=1.3)]
    for i, x in enumerate(MODS):
        for k in range(3):
            dx = [0.0, -0.22, 0.2][k]
            h = [0.34, 0.22, 0.26][k]
            cyl("Stiel%d_%d" % (i, k), (x + dx, -0.2 + 0.1 * k, 1.42 + h / 2), 0.035, h, stem, verts=10)
            c = sphere("Hut%d_%d" % (i, k), (x + dx, -0.2 + 0.1 * k, 1.42 + h), [0.14, 0.1, 0.11][k], caps[(i + k) % 2])
            c.scale = (1, 1, 0.5)
if "lanterns" in P:
    frame = pmat("Laterne", (0.12, 0.13, 0.14), metal=0.8, rough=0.4)
    ghost = pmat("Geistlicht", (0.2, 1.0, 0.75), emit=(0.15, 1.0, 0.7), strength=1.8)
    for i, x in enumerate(MODS):
        box("LatRahmen%d" % i, (x, FR - 0.14, 0.95), (0.2, 0.16, 0.28), frame, bevel=0.02)
        box("LatLicht%d" % i, (x, FR - 0.15, 0.95), (0.14, 0.17, 0.2), ghost, bevel=0.0)
        cyl("LatDach%d" % i, (x, FR - 0.14, 1.12), 0.13, 0.06, frame, verts=4, bevel=0.01)
if "bowls" in P:
    goldm = pmat("Schale", (0.9, 0.65, 0.25), metal=1.0, rough=0.3)
    fire = pmat("Feuer", (1.0, 0.45, 0.08), emit=(1.0, 0.4, 0.05), strength=1.6)
    for i, x in enumerate(MODS):
        bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.08, radius2=0.2, depth=0.14, location=(x, -0.13, 1.5))
        b = bpy.context.active_object
        b.data.materials.append(goldm)
        bpy.ops.object.shade_smooth()
        bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.15, radius2=0.0, depth=0.32, location=(x, -0.13, 1.72))
        fl = bpy.context.active_object
        fl.data.materials.append(fire)

world.node_tree.nodes["Background"].inputs[0].default_value = (*C.get("ambient", (0.04, 0.09, 0.25)), 1)
world.node_tree.nodes["Background"].inputs[1].default_value = C.get("ambient_strength", 1.2)
light('SUN', "Sonne", (0, -5, 8), (55, 0, -40), C.get("sun", 2.6), C.get("sun_color", (0.9, 0.93, 1.0)))
light('AREA', "Rand", (0, 3.0, 3.5), (-60, 0, 0), 300, C["neon"], size=12)
glare(threshold=1.0, size=7)
