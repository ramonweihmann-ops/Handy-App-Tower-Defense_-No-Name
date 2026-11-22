# Mauerform der Lava-Mauer (freigegeben 22.11.2026) als Baukasten für alle Planeten.
# Erwartet CFG (Farben als sRGB 0..1, gemessen an der Brücke, messen.py) – siehe planet_<feld>_form.py.
import bmesh as _bm
C = CFG

def L_(c):
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)

def ramp_colors(cr, cols, positions=(0.15, 0.42, 0.68, 0.92)):
    e = cr.color_ramp.elements
    e[0].position = 0.0; e[0].color = (0, 0, 0, 1)
    e[1].position = positions[3]; e[1].color = (*L_(cols[3]), 1)
    for p, c in zip(positions[:3], cols[:3]):
        x = e.new(p); x.color = (*L_(c), 1)

def plate(name, base, metal=0.0, rough=0.75, bump=0.8, scratches=0.0, veins=None, var=1.0,
          cracks=None, corner=0.0, heat_bottom=0.0, glow=None, strength=1.6):
    """Oberfläche mit Flecken, Narben, Kratzern/Maserung, dunklen Ecken und Leuchten in Rissen, Ecken und von unten.
    cracks = (Dichte, Breite, Maske 0..1; Maske 1 = keine), glow = vier Leuchtfarben (dunkel → Kern)"""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    Ln = nt.links.new
    p = nt.nodes["Principled BSDF"]
    p.inputs["Metallic"].default_value = metal
    p.inputs["Roughness"].default_value = rough
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    b = L_(base)
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0; nz.inputs["Detail"].default_value = 8.0
    Ln(geo.outputs["Position"], nz.inputs["Vector"])
    cb = nt.nodes.new("ShaderNodeValToRGB")
    lo, hi = 1.0 - 0.45 * var, 1.0 + 0.35 * var
    cb.color_ramp.elements[0].color = (b[0] * lo, b[1] * lo, b[2] * lo * 1.05, 1)
    cb.color_ramp.elements[1].color = (min(1, b[0] * hi), min(1, b[1] * hi), min(1, b[2] * hi), 1)
    Ln(nz.outputs["Fac"], cb.inputs[0])
    col = cb.outputs[0]
    if veins:
        wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 1.4; wv.inputs["Distortion"].default_value = 14.0
        wv.inputs["Detail"].default_value = 6.0
        Ln(geo.outputs["Position"], wv.inputs["Vector"])
        vr = nt.nodes.new("ShaderNodeMapRange"); vr.inputs["From Max"].default_value = 0.08
        vr.inputs["To Min"].default_value = 0.6; vr.inputs["To Max"].default_value = 0.0
        Ln(wv.outputs["Fac"], vr.inputs["Value"])
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
        Ln(vr.outputs["Result"], mx.inputs["Factor"]); Ln(col, mx.inputs[6]); mx.inputs[7].default_value = (*L_(veins), 1)
        col = mx.outputs[2]
    if scratches > 0:
        mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.5, 60.0, 9.0)
        mp.inputs["Rotation"].default_value = (0, 0, 0.3)
        Ln(geo.outputs["Position"], mp.inputs["Vector"])
        sn = nt.nodes.new("ShaderNodeTexNoise"); sn.inputs["Scale"].default_value = 4.0; sn.inputs["Detail"].default_value = 2.0
        Ln(mp.outputs["Vector"], sn.inputs["Vector"])
        sr = nt.nodes.new("ShaderNodeMapRange"); sr.inputs["From Min"].default_value = 0.66; sr.inputs["From Max"].default_value = 0.7
        sr.inputs["To Max"].default_value = scratches
        Ln(sn.outputs["Fac"], sr.inputs["Value"])
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
        Ln(sr.outputs["Result"], mx.inputs["Factor"]); Ln(col, mx.inputs[6])
        mx.inputs[7].default_value = (min(1, b[0] * 2.2 + 0.08), min(1, b[1] * 2.2 + 0.08), min(1, b[2] * 2.2 + 0.08), 1)
        col = mx.outputs[2]
    # dunkle Ecken (Schmutz)
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = 0.14; ao.samples = 16
    ad = nt.nodes.new("ShaderNodeMapRange"); ad.inputs["From Min"].default_value = 0.35; ad.inputs["From Max"].default_value = 1.0
    ad.inputs["To Min"].default_value = 0.75; ad.inputs["To Max"].default_value = 0.0
    Ln(ao.outputs["AO"], ad.inputs["Value"])
    md = nt.nodes.new("ShaderNodeMix"); md.data_type = 'RGBA'
    Ln(ad.outputs["Result"], md.inputs["Factor"]); Ln(col, md.inputs[6]); md.inputs[7].default_value = (b[0] * 0.15, b[1] * 0.15, b[2] * 0.18, 1)
    Ln(md.outputs[2], p.inputs["Base Color"])
    bn = nt.nodes.new("ShaderNodeTexNoise"); bn.inputs["Scale"].default_value = 30.0; bn.inputs["Detail"].default_value = 10.0
    Ln(geo.outputs["Position"], bn.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump; bp.inputs["Distance"].default_value = 0.02
    Ln(bn.outputs["Fac"], bp.inputs["Height"]); Ln(bp.outputs["Normal"], p.inputs["Normal"])
    if glow is None or (corner <= 0 and heat_bottom <= 0 and (cracks is None or cracks[2] >= 1.0)):
        return m
    heat = None
    if cracks is not None and cracks[2] < 1.0:
        warp = nt.nodes.new("ShaderNodeTexNoise"); warp.inputs["Scale"].default_value = 3.5; warp.inputs["Detail"].default_value = 6.0
        Ln(geo.outputs["Position"], warp.inputs["Vector"])
        sc = nt.nodes.new("ShaderNodeVectorMath"); sc.operation = 'SCALE'; sc.inputs["Scale"].default_value = 0.5
        Ln(warp.outputs["Color"], sc.inputs[0])
        av = nt.nodes.new("ShaderNodeVectorMath"); av.operation = 'ADD'
        Ln(geo.outputs["Position"], av.inputs[0]); Ln(sc.outputs[0], av.inputs[1])
        vor = nt.nodes.new("ShaderNodeTexVoronoi"); vor.feature = 'DISTANCE_TO_EDGE'; vor.inputs["Scale"].default_value = cracks[0]
        Ln(av.outputs[0], vor.inputs["Vector"])
        hc = nt.nodes.new("ShaderNodeMapRange"); hc.inputs["From Max"].default_value = cracks[1]
        hc.inputs["To Min"].default_value = 1.0; hc.inputs["To Max"].default_value = 0.0
        Ln(vor.outputs["Distance"], hc.inputs["Value"])
        mk = nt.nodes.new("ShaderNodeTexNoise"); mk.inputs["Scale"].default_value = 1.2
        Ln(geo.outputs["Position"], mk.inputs["Vector"])
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = cracks[2]; mr.inputs["From Max"].default_value = cracks[2] + 0.1
        Ln(mk.outputs["Fac"], mr.inputs["Value"])
        c0 = nt.nodes.new("ShaderNodeMath"); c0.operation = 'MULTIPLY'
        Ln(hc.outputs["Result"], c0.inputs[0]); Ln(mr.outputs["Result"], c0.inputs[1])
        hot = nt.nodes.new("ShaderNodeTexNoise"); hot.inputs["Scale"].default_value = 4.0; hot.inputs["Detail"].default_value = 3.0
        Ln(geo.outputs["Position"], hot.inputs["Vector"])
        hr = nt.nodes.new("ShaderNodeMapRange"); hr.inputs["From Min"].default_value = 0.35; hr.inputs["From Max"].default_value = 0.7
        hr.inputs["To Min"].default_value = 0.55; hr.inputs["To Max"].default_value = 1.0
        Ln(hot.outputs["Fac"], hr.inputs["Value"])
        heat = nt.nodes.new("ShaderNodeMath"); heat.operation = 'MULTIPLY'
        Ln(c0.outputs[0], heat.inputs[0]); Ln(hr.outputs["Result"], heat.inputs[1])
        heat = heat.outputs[0]
    ar = nt.nodes.new("ShaderNodeMapRange"); ar.inputs["From Min"].default_value = 0.3; ar.inputs["From Max"].default_value = 0.85
    ar.inputs["To Min"].default_value = corner; ar.inputs["To Max"].default_value = 0.0
    Ln(ao.outputs["AO"], ar.inputs["Value"])
    sz = nt.nodes.new("ShaderNodeSeparateXYZ"); Ln(geo.outputs["Position"], sz.inputs[0])
    hb = nt.nodes.new("ShaderNodeMapRange"); hb.inputs["From Min"].default_value = 0.3; hb.inputs["From Max"].default_value = 0.75
    hb.inputs["To Min"].default_value = heat_bottom; hb.inputs["To Max"].default_value = 0.0
    Ln(sz.outputs[2], hb.inputs["Value"])
    g = nt.nodes.new("ShaderNodeMath"); g.operation = 'MAXIMUM'
    Ln(ar.outputs["Result"], g.inputs[0]); Ln(hb.outputs["Result"], g.inputs[1])
    gs = nt.nodes.new("ShaderNodeMath"); gs.operation = 'MULTIPLY'; gs.inputs[1].default_value = 0.42
    Ln(g.outputs[0], gs.inputs[0])
    tot = gs.outputs[0]
    if heat is not None:
        mxx = nt.nodes.new("ShaderNodeMath"); mxx.operation = 'MAXIMUM'
        Ln(heat, mxx.inputs[0]); Ln(gs.outputs[0], mxx.inputs[1])
        tot = mxx.outputs[0]
    rp = nt.nodes.new("ShaderNodeValToRGB"); ramp_colors(rp, glow)
    Ln(tot, rp.inputs[0])
    Ln(rp.outputs[0], p.inputs["Emission Color"])
    p.inputs["Emission Strength"].default_value = strength
    return m

def flow(name, axis, glow, facing=True, strength=1.3, scale=3.0):
    """Leuchtröhre: wandernde helle und dunklere Stellen, Kern heller als der Rand (Farben wie die Brücke)"""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    Ln = nt.links.new
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = {"x": (scale, 14.0, 14.0), "z": (14.0, 14.0, scale)}[axis]
    Ln(geo.outputs["Position"], mp.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.0; nz.inputs["Detail"].default_value = 5.0
    nz.inputs["Distortion"].default_value = 0.6
    Ln(mp.outputs["Vector"], nz.inputs["Vector"])
    heat = nz.outputs["Fac"]
    if facing:
        lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.45
        inv = nt.nodes.new("ShaderNodeMath"); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
        Ln(lw.outputs["Facing"], inv.inputs[1])
        mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'
        Ln(heat, mul.inputs[0]); Ln(inv.outputs[0], mul.inputs[1])
        ad = nt.nodes.new("ShaderNodeMath"); ad.operation = 'MULTIPLY_ADD'; ad.inputs[1].default_value = 0.55; ad.inputs[2].default_value = 0.35
        Ln(mul.outputs[0], ad.inputs[0])
        heat = ad.outputs[0]
    cr = nt.nodes.new("ShaderNodeValToRGB"); ramp_colors(cr, glow, positions=(0.25, 0.48, 0.66, 0.85))
    cr.color_ramp.elements[0].color = (*[v * 0.5 for v in L_(glow[0])], 1)
    Ln(heat, cr.inputs[0])
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs[1].default_value = strength
    Ln(cr.outputs[0], em.inputs[0]); Ln(em.outputs[0], out.inputs[0])
    return m

def see_through(o):
    o.visible_shadow = False
    o.visible_diffuse = False
    return o

def light_only(o, mat_):
    o.visible_camera = False
    o.visible_shadow = False
    o.data.materials.clear()
    o.data.materials.append(mat_)
    return o

def octo(name, cx, cz, w, h, ch, y0, y1, material):
    pts = [(-w / 2 + ch, -h / 2), (w / 2 - ch, -h / 2), (w / 2, -h / 2 + ch), (w / 2, h / 2 - ch),
           (w / 2 - ch, h / 2), (-w / 2 + ch, h / 2), (-w / 2, h / 2 - ch), (-w / 2, -h / 2 + ch)]
    me = bpy.data.meshes.new(name)
    bm = _bm.new()
    a = [bm.verts.new((cx + x, y0, cz + z)) for x, z in pts]
    bb = [bm.verts.new((cx + x, y1, cz + z)) for x, z in pts]
    bm.faces.new(a); bm.faces.new(list(reversed(bb)))
    for i in range(8):
        j = (i + 1) % 8
        bm.faces.new([a[j], a[i], bb[i], bb[j]])
    _bm.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); scene.collection.objects.link(o)
    o.data.materials.append(material)
    bv = o.modifiers.new("Bevel", 'BEVEL'); bv.width = 0.02; bv.segments = 2; bv.limit_method = 'ANGLE'
    return o

def octo_top(name, cx, cy, w, d, ch, z0, z1, material):
    o = octo(name, 0, 0, w, d, ch, 0, z1 - z0, material)
    o.rotation_euler = (math.radians(-90), 0, 0)
    o.location = (cx, cy, z1)
    return o

GLOW = C["glow"]                     # vier Leuchtfarben dunkel → Kern
LIGHT = L_(C["light"])               # Farbe des Lichtscheins
stone = plate("Platte", C["plate"], **C.get("plate_opts", {}), glow=GLOW)
stone_top = plate("Deckplatte", C.get("top", C["plate"]), **C.get("top_opts", C.get("plate_opts", {})), glow=GLOW)
metal = plate("Metall", C["metal"], **C.get("metal_opts", {"metal": 0.85, "rough": 0.4, "bump": 0.15, "scratches": 0.25}), glow=GLOW)
metal2 = plate("Metall2", C["metal2"], **C.get("metal2_opts", {"metal": 0.9, "rough": 0.3, "bump": 0.1, "scratches": 0.3}), glow=GLOW)
deep = plate("Rillengrund", C.get("deep", (0.05, 0.05, 0.06)), **C.get("deep_opts", {"cracks": (7.0, 0.06, 0.0), "rough": 0.6, "bump": 0.3}), glow=GLOW)
tube_x = flow("RöhreX", "x", GLOW, strength=C.get("tube_strength", 1.3))
seam = flow("Fuge", "x", GLOW, facing=False, strength=C.get("seam_strength", 1.2), scale=5.0)
lamp_glow = glowm("Licht", LIGHT, C.get("light_power", 120.0))
seam_glow = glowm("FugenLicht", LIGHT, C.get("seam_power", 30.0))

def rail_x(name, x0, x1, y, z):
    w = x1 - x0
    cx = (x0 + x1) / 2
    box(name + "Grund", (cx, y + 0.07, z), (w, 0.04, 0.2), deep, bevel=0.005)
    for s in (-1, 1):
        box(name + "Lippe%d" % s, (cx, y - 0.01, z + s * 0.11), (w, 0.15, 0.04), metal2, bevel=0.012)
        box(name + "Stufe%d" % s, (cx, y + 0.03, z + s * 0.14), (w, 0.1, 0.035), metal, bevel=0.01)
    see_through(cyl(name + "Roehre", (cx, y, z), 0.065, w - 0.02, tube_x, rot=(0, 90, 0), verts=20))
    light_only(cyl(name + "Licht", (cx, y - 0.01, z), 0.04, w - 0.04, lamp_glow, rot=(0, 90, 0), verts=8), lamp_glow)
    x = x0 + 0.3
    while x < x1 - 0.15:
        box(name + "Klammer", (x, y - 0.03, z), (0.06, 0.15, 0.22), metal2, bevel=0.012)
        x += 0.9

prism("Sockel", -HALF, HALF, [(FR - 0.14, 0.0), (0.35, 0.0), (0.35, 0.3), (FR - 0.06, 0.3), (FR - 0.14, 0.24)], metal, bevel=0.015)
rail_x("Sockelrinne", -HALF, HALF, FR - 0.2, 0.13)

for i, (x0, x1) in enumerate(segments()):
    w = x1 - x0
    cx = (x0 + x1) / 2
    box("Kern%d" % i, (cx, -0.02, 0.67), (w, 0.55, 0.78), metal, bevel=0.01)
    see_through(box("Fuge%d" % i, (cx, FR + 0.12, 0.66), (w - 0.04, 0.02, 0.66), seam, bevel=0.0))
    light_only(box("FugenLicht%d" % i, (cx, FR + 0.085, 0.66), (w - 0.08, 0.01, 0.6), seam_glow, bevel=0.0), seam_glow)
    box("RahmenU%d" % i, (cx, FR - 0.03, 0.32), (w, 0.12, 0.05), metal2, bevel=0.01)
    pw = (w - 0.06) / 2
    for k in (-1, 1):
        octo("Platte%d_%d" % (i, k), cx + k * (pw / 2 + 0.012), 0.66, pw - 0.03, 0.6, 0.08, FR - 0.04, FR + 0.06, stone)
    rail_x("Oben%d" % i, x0, x1, FR - 0.1, 1.06)
    octo_top("Deck%d" % i, cx, -0.1, w - 0.06, 0.62, 0.08, 1.14, 1.18, stone_top)
    box("DeckRahmen%d" % i, (cx, -0.1, 1.13), (w, 0.74, 0.03), metal, bevel=0.006)

P = C.get("props", [])
for i, x in enumerate(MODS):
    box("Halter%d" % i, (x, -0.13, 0.85), (0.8, 0.96, 1.1), metal, bevel=0.015)
    box("HFront%d" % i, (x, FR - 0.05, 0.85), (0.72, 0.06, 1.0), metal2, bevel=0.012)
    octo("HStein%d" % i, x, 0.58, 0.5, 0.32, 0.07, FR - 0.1, FR - 0.04, stone)
    if not ("portholes" in P or "lanterns" in P):
        octo("HStein2_%d" % i, x, 1.14, 0.5, 0.32, 0.07, FR - 0.1, FR - 0.04, stone)
    box("BFassung%d" % i, (x, FR - 0.12, 0.86), (0.62, 0.12, 0.22), metal2, bevel=0.018)
    box("BGrund%d" % i, (x, FR - 0.13, 0.86), (0.5, 0.13, 0.13), deep, bevel=0.005)
    see_through(cyl("Balken%d" % i, (x, FR - 0.17, 0.86), 0.05, 0.46, tube_x, rot=(0, 90, 0), verts=16))
    light_only(cyl("BLicht%d" % i, (x, FR - 0.18, 0.86), 0.03, 0.42, lamp_glow, rot=(0, 90, 0), verts=8), lamp_glow)
    for sx in (-1, 1):
        cyl("Bolzen", (x + sx * 0.27, FR - 0.185, 0.86), 0.025, 0.02, metal, rot=(90, 0, 0), verts=8)
    box("Kappe%d" % i, (x, -0.13, 1.44), (0.88, 1.02, 0.08), metal2, bevel=0.012)
    octo_top("KStein%d" % i, x, -0.13, 0.64, 0.8, 0.08, 1.48, 1.51, stone_top)

# --- Zierteile je Planet (auf die Form abgestimmt) ---
def pm(name, col, metal_=0.0, rough=0.5, emit=None, strength=0.0):
    return mat(name, L_(col), metal=metal_, rough=rough, emit=L_(emit) if emit else None, strength=strength)

def tube(name, pts, radius, material):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = radius; cu.bevel_resolution = 3
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp_, p_ in zip(sp.bezier_points, pts):
        bp_.co = p_; bp_.handle_left_type = bp_.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu); scene.collection.objects.link(o); o.data.materials.append(material)
    return o

random.seed(11)
TOP_Z = 1.51
edges = [-HALF] + MODS + [HALF]
if "crystals" in P:
    cc = C.get("crystal", C["light"])
    cm = pm("Kristall", cc, rough=0.25, emit=cc, strength=C.get("crystal_glow", 1.2))
    for i, x in enumerate(MODS):
        for k in range(3):
            h = random.uniform(0.26, 0.46) * (1.25 if k == 0 else 1.0)
            dx = [0.0, -0.16, 0.15][k]; dy = [0.0, 0.12, -0.08][k]; tilt = [0, -16, 18][k]
            r_ = 0.085 if k == 0 else 0.065
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=r_, depth=h, location=(x + dx, -0.13 + dy, TOP_Z + h / 2))
            body = bpy.context.active_object
            bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=r_, radius2=0.0, depth=0.13, location=(x + dx, -0.13 + dy, TOP_Z + h + 0.065))
            tip = bpy.context.active_object
            for o in (body, tip):
                o.data.materials.append(cm); o.rotation_euler = (0, math.radians(tilt), 0)
            tip.location.x += math.sin(math.radians(tilt)) * (h / 2 + 0.065)
            tip.location.z -= (1 - math.cos(math.radians(tilt))) * (h / 2 + 0.065)
        light_only(sphere("KLicht%d" % i, (x, -0.35, TOP_Z + 0.25), 0.06, lamp_glow), lamp_glow)
if "vines" in P:
    vine = pm("Ranke", (0.16, 0.3, 0.08), rough=0.6)
    leaf = pm("Blatt", (0.28, 0.52, 0.14), rough=0.5)
    for i in range(len(edges) - 1):
        x0 = edges[i] + 0.4; x1 = edges[i + 1] - 0.4
        tube("Ranke%d" % i, [(x0, FR - 0.22, 1.2), ((x0 + x1) / 2, FR - 0.26, 0.92 + random.uniform(-0.06, 0.04)), (x1, FR - 0.22, 1.2)], 0.03, vine)
        for k in range(6):
            t = (k + 0.5) / 6
            l_ = sphere("Blatt", (x0 + (x1 - x0) * t, FR - 0.28, 1.2 - 0.28 * math.sin(t * math.pi) + random.uniform(-0.04, 0.04)), 0.07, leaf)
            l_.scale = (1.4, 0.35, 0.8); l_.rotation_euler = (0, random.uniform(-0.8, 0.8), 0)
    for i, x in enumerate(MODS):
        tube("PRanke%d" % i, [(x - 0.42, FR - 0.08, 0.3), (x - 0.4, FR - 0.14, 0.8), (x + 0.1, FR - 0.14, 1.3), (x + 0.42, FR - 0.08, 1.5)], 0.028, vine)
if "portholes" in P:
    brass = pm("Messing", (0.85, 0.62, 0.3), metal_=0.9, rough=0.25)
    glass = pm("Bullauge", C.get("porthole", (1.0, 0.78, 0.45)), emit=C.get("porthole", (1.0, 0.78, 0.45)), strength=2.0)
    for i, x in enumerate(MODS):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.15, minor_radius=0.04, location=(x, FR - 0.1, 1.15), rotation=(math.radians(90), 0, 0))
        t_ = bpy.context.active_object; t_.data.materials.append(brass); bpy.ops.object.shade_smooth()
        see_through(cyl("Glas%d" % i, (x, FR - 0.09, 1.15), 0.125, 0.03, glass, rot=(90, 0, 0), verts=24))
        for k in range(6):
            a_ = k * math.pi / 3
            sphere("BNiete", (x + 0.15 * math.cos(a_), FR - 0.14, 1.15 + 0.15 * math.sin(a_)), 0.018, brass)
        light_only(sphere("BLichtP%d" % i, (x, FR - 0.3, 1.15), 0.05, lamp_glow), lamp_glow)
if "rope" in P:
    rope = pm("Tau", (0.72, 0.6, 0.42), rough=0.85)
    for i in range(len(edges) - 1):
        x0 = edges[i] + 0.4; x1 = edges[i + 1] - 0.4
        tube("Tau%d" % i, [(x0, FR - 0.24, 1.3), ((x0 + x1) / 2, FR - 0.3, 1.17), (x1, FR - 0.24, 1.3)], 0.04, rope)
if "hazard" in P:
    warn = stripes("Warn", (0.95, 0.7, 0.1), (0.05, 0.05, 0.06), scale=10.0)
    for i in range(len(edges) - 1):
        x0 = edges[i] + (0.4 if i > 0 else 0.0); x1 = edges[i + 1] - (0.4 if i < len(edges) - 2 else 0.0)
        box("Warn%d" % i, ((x0 + x1) / 2, FR - 0.095, 0.32), (x1 - x0 - 0.05, 0.02, 0.05), warn, bevel=0.0)
if "rods" in P:
    rodm = pm("Stab", (0.55, 0.57, 0.62), metal_=0.9, rough=0.3)
    tipm = pm("Funke", C["light"], emit=C["light"], strength=6.0)
    for i, x in enumerate(MODS):
        cyl("Stab%d" % i, (x + 0.22, -0.13, TOP_Z + 0.3), 0.022, 0.6, rodm, verts=8)
        sphere("Spitze%d" % i, (x + 0.22, -0.13, TOP_Z + 0.62), 0.045, tipm)
if "pipe" in P:
    copper = pm("Kupfer", (0.72, 0.4, 0.22), metal_=0.9, rough=0.35)
    cyl("Rohr", (0, FR - 0.32, 0.36), 0.075, HALF * 2, copper, rot=(0, 90, 0), verts=16)
    for x in [-5.85, -4.5, -2.7, -0.9, 0.9, 2.7, 4.5, 5.85]:
        cyl("Flansch", (x, FR - 0.32, 0.36), 0.1, 0.07, copper, rot=(0, 90, 0), verts=16, bevel=0.01)
if "gold_balls" in P:
    goldm = pm("Gold", (1.0, 0.76, 0.32), metal_=1.0, rough=0.2)
    for i, x in enumerate(MODS):
        cyl("Sockelchen%d" % i, (x, -0.13, TOP_Z + 0.05), 0.11, 0.1, goldm, verts=20, bevel=0.01)
        sphere("Kugel%d" % i, (x, -0.13, TOP_Z + 0.2), 0.13, goldm)
if "mushrooms" in P:
    stem = pm("Stiel", (0.88, 0.82, 0.68), rough=0.6)
    caps = [pm("HutOrange", (1.0, 0.45, 0.1), emit=(1.0, 0.4, 0.06), strength=1.4), pm("HutTuerkis", (0.12, 0.8, 0.8), emit=(0.1, 0.75, 0.78), strength=1.4)]
    for i, x in enumerate(MODS):
        for k in range(3):
            dx = [0.0, -0.22, 0.2][k]; h = [0.34, 0.22, 0.26][k]
            cyl("Stiel", (x + dx, -0.2 + 0.1 * k, TOP_Z + h / 2), 0.035, h, stem, verts=10)
            cp = sphere("Hut", (x + dx, -0.2 + 0.1 * k, TOP_Z + h), [0.14, 0.1, 0.11][k], caps[(i + k) % 2]); cp.scale = (1, 1, 0.5)
        light_only(sphere("PLicht%d" % i, (x, -0.4, TOP_Z + 0.35), 0.05, lamp_glow), lamp_glow)
if "lanterns" in P:
    frame = pm("Laterne", (0.12, 0.13, 0.14), metal_=0.8, rough=0.4)
    ghost = pm("Geistlicht", C["light"], emit=C["light"], strength=2.0)
    for i, x in enumerate(MODS):
        box("LatRahmen%d" % i, (x, FR - 0.16, 1.15), (0.22, 0.16, 0.3), frame, bevel=0.02)
        see_through(box("LatLicht%d" % i, (x, FR - 0.17, 1.15), (0.16, 0.17, 0.22), ghost, bevel=0.0))
        cyl("LatDach%d" % i, (x, FR - 0.16, 1.33), 0.14, 0.06, frame, verts=4, bevel=0.01)
        light_only(sphere("LLicht%d" % i, (x, FR - 0.35, 1.15), 0.05, lamp_glow), lamp_glow)
if "bowls" in P:
    goldm = pm("Schale", (0.92, 0.68, 0.28), metal_=1.0, rough=0.3)
    fire = flow("Feuer", "z", GLOW, facing=True, strength=1.6, scale=6.0)
    for i, x in enumerate(MODS):
        bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.08, radius2=0.2, depth=0.14, location=(x, -0.13, TOP_Z + 0.07))
        b_ = bpy.context.active_object; b_.data.materials.append(goldm); bpy.ops.object.shade_smooth()
        bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.15, radius2=0.0, depth=0.32, location=(x, -0.13, TOP_Z + 0.3))
        f_ = bpy.context.active_object; f_.data.materials.append(fire); see_through(f_)
        light_only(sphere("FLicht%d" % i, (x, -0.3, TOP_Z + 0.3), 0.05, lamp_glow), lamp_glow)

amb = L_(C.get("ambient", C["plate"]))
world.node_tree.nodes["Background"].inputs[0].default_value = (amb[0] * 0.6, amb[1] * 0.6, amb[2] * 0.6, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = C.get("ambient_strength", 0.6)
light('SUN', "Sonne", (0, -5, 8), (55, 0, -40), C.get("sun", 2.2), L_(C.get("sun_color", (0.95, 0.95, 1.0))))
light('AREA', "Rand", (0, 3.0, 3.5), (-60, 0, 0), C.get("rim", 160), LIGHT, size=12)
shadow_catcher()
tint = L_(C["light"])
glow_comp(tint=tint, threshold=C.get("glow_threshold", 0.7), size=9, alpha_gain=0.9, mix_strength=C.get("glow_mix", 2.0))
