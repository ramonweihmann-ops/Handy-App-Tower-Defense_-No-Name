# Lava-Asteroid, Detailstufe 2, vierte Fassung (Kommentar 22.11.: Leuchtstäbe wirken aufgeklebt): Glut wie an der Brücke –
# Röhren in gestuften Metallrinnen mit Klammern, fließende Glut (heiße und kühlere Stellen, Kern gelb, außen rot),
# unsichtbare Lichtquellen in Röhren und Fugen, die Rinnenwände, Klammern und Steinkanten orange anstrahlen;
# tiefe Fugen zwischen den Steinplatten. Farben gemessen am Bild (21.11.2026).
import bmesh as _bm
stone = rich("Stein", (0.06, 0.035, 0.065), metal=0.0, rough=0.78, dirt=(0.01, 0.005, 0.01), var=0.45, grad=0.2, bump=1.0,
             cracks=(1.0, 0.14, 0.03), crack_emit=0.8, crack_width=0.008, crack_mask=0.56)
metal = rich("Metall", (0.05, 0.028, 0.035), metal=0.85, rough=0.38, dirt=(0.01, 0.006, 0.008), scratches=0.25, bump=0.15)
metal2 = rich("Metall2", (0.14, 0.06, 0.05), metal=0.9, rough=0.3, dirt=(0.02, 0.01, 0.01), scratches=0.3, bump=0.1)
deep = rich("Tief", (0.015, 0.008, 0.01), metal=0.3, rough=0.6, ao_strength=0.2, var=0.05, grad=0.05, bump=0.05)

def molten(name, axis, facing=True, strength=1.3, scale=3.0):
    """Fließende Glut: Rauschen entlang der Achse (heiße und kühlere Stellen), bei Röhren Kern heller als der Rand"""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    L = nt.links.new
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    mp = nt.nodes.new("ShaderNodeMapping")
    sc = {"x": (scale, 14.0, 14.0), "y": (14.0, scale, 14.0), "z": (14.0, 14.0, scale)}[axis]
    mp.inputs["Scale"].default_value = sc
    L(geo.outputs["Position"], mp.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.0; nz.inputs["Detail"].default_value = 5.0
    nz.inputs["Distortion"].default_value = 0.6
    L(mp.outputs["Vector"], nz.inputs["Vector"])
    heat = nz.outputs["Fac"]
    if facing:
        lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.45
        inv = nt.nodes.new("ShaderNodeMath"); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
        L(lw.outputs["Facing"], inv.inputs[1])
        mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'
        L(heat, mul.inputs[0]); L(inv.outputs[0], mul.inputs[1])
        add = nt.nodes.new("ShaderNodeMath"); add.operation = 'MULTIPLY_ADD'; add.inputs[1].default_value = 0.55; add.inputs[2].default_value = 0.35
        L(mul.outputs[0], add.inputs[0])
        heat = add.outputs[0]
    cr = nt.nodes.new("ShaderNodeValToRGB")
    e = cr.color_ramp.elements
    e[0].position = 0.25; e[0].color = (0.45, 0.015, 0.0, 1)
    e[1].position = 0.85; e[1].color = (1.0, 0.92, 0.25, 1)
    x = e.new(0.48); x.color = (1.0, 0.18, 0.01, 1)
    y = e.new(0.66); y.color = (1.0, 0.45, 0.04, 1)
    L(heat, cr.inputs[0])
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs[1].default_value = strength
    L(cr.outputs[0], em.inputs[0]); L(em.outputs[0], out.inputs[0])
    return m

def see_through(o):
    """sichtbare Glutröhre: lässt das Licht der Lichtquelle darin durch (wirft keinen Schatten)"""
    o.visible_shadow = False
    o.visible_diffuse = False
    return o

def light_only(o, strength_mat):
    """unsichtbar für die Kamera, beleuchtet aber die Umgebung"""
    o.visible_camera = False
    o.visible_shadow = False
    o.data.materials.clear()
    o.data.materials.append(strength_mat)
    return o


def lava_stone(name, base=(0.06, 0.035, 0.065), crack_density=2.2, crack_width=0.016, crack_mask=0.42, heat_bottom=0.6):
    """Lavastein: dunkler narbiger Stein mit glühenden Rissen (Kern gelb, Rand rot), dunkelrot glimmenden Fugen und Ecken
    und Wärme von unten"""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    L = nt.links.new
    p = nt.nodes["Principled BSDF"]
    p.inputs["Metallic"].default_value = 0.0
    p.inputs["Roughness"].default_value = 0.78
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    # Grundfarbe mit Flecken
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0; nz.inputs["Detail"].default_value = 8.0
    L(geo.outputs["Position"], nz.inputs["Vector"])
    cb = nt.nodes.new("ShaderNodeValToRGB")
    cb.color_ramp.elements[0].color = (base[0] * 0.5, base[1] * 0.5, base[2] * 0.55, 1)
    cb.color_ramp.elements[1].color = (base[0] * 1.6, base[1] * 1.5, base[2] * 1.5, 1)
    L(nz.outputs["Fac"], cb.inputs[0])
    L(cb.outputs[0], p.inputs["Base Color"])
    # Narben
    bn = nt.nodes.new("ShaderNodeTexNoise"); bn.inputs["Scale"].default_value = 30.0; bn.inputs["Detail"].default_value = 10.0
    L(geo.outputs["Position"], bn.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.9; bp.inputs["Distance"].default_value = 0.02
    L(bn.outputs["Fac"], bp.inputs["Height"]); L(bp.outputs["Normal"], p.inputs["Normal"])
    # Risse: Abstand zur Zellkante, leicht verzerrt
    warp = nt.nodes.new("ShaderNodeTexNoise"); warp.inputs["Scale"].default_value = 3.5; warp.inputs["Detail"].default_value = 6.0
    L(geo.outputs["Position"], warp.inputs["Vector"])
    sc = nt.nodes.new("ShaderNodeVectorMath"); sc.operation = 'SCALE'; sc.inputs["Scale"].default_value = 0.5
    L(warp.outputs["Color"], sc.inputs[0])
    ad = nt.nodes.new("ShaderNodeVectorMath"); ad.operation = 'ADD'
    L(geo.outputs["Position"], ad.inputs[0]); L(sc.outputs[0], ad.inputs[1])
    vor = nt.nodes.new("ShaderNodeTexVoronoi"); vor.feature = 'DISTANCE_TO_EDGE'; vor.inputs["Scale"].default_value = crack_density
    L(ad.outputs[0], vor.inputs["Vector"])
    hc = nt.nodes.new("ShaderNodeMapRange"); hc.inputs["From Min"].default_value = 0.0; hc.inputs["From Max"].default_value = crack_width
    hc.inputs["To Min"].default_value = 1.0; hc.inputs["To Max"].default_value = 0.0
    L(vor.outputs["Distance"], hc.inputs["Value"])
    mk = nt.nodes.new("ShaderNodeTexNoise"); mk.inputs["Scale"].default_value = 1.2
    L(geo.outputs["Position"], mk.inputs["Vector"])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = crack_mask; mr.inputs["From Max"].default_value = crack_mask + 0.1
    L(mk.outputs["Fac"], mr.inputs["Value"])
    crack0 = nt.nodes.new("ShaderNodeMath"); crack0.operation = 'MULTIPLY'
    L(hc.outputs["Result"], crack0.inputs[0]); L(mr.outputs["Result"], crack0.inputs[1])
    hot = nt.nodes.new("ShaderNodeTexNoise"); hot.inputs["Scale"].default_value = 4.0; hot.inputs["Detail"].default_value = 3.0
    L(geo.outputs["Position"], hot.inputs["Vector"])
    hr = nt.nodes.new("ShaderNodeMapRange"); hr.inputs["From Min"].default_value = 0.35; hr.inputs["From Max"].default_value = 0.7
    hr.inputs["To Min"].default_value = 0.55; hr.inputs["To Max"].default_value = 1.0
    L(hot.outputs["Fac"], hr.inputs["Value"])
    crack = nt.nodes.new("ShaderNodeMath"); crack.operation = 'MULTIPLY'
    L(crack0.outputs[0], crack.inputs[0]); L(hr.outputs["Result"], crack.inputs[1])
    # Glimmen in Fugen und Ecken (Umgebungsverdeckung)
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = 0.12; ao.samples = 16
    ar = nt.nodes.new("ShaderNodeMapRange"); ar.inputs["From Min"].default_value = 0.3; ar.inputs["From Max"].default_value = 0.85
    ar.inputs["To Min"].default_value = 0.55; ar.inputs["To Max"].default_value = 0.0
    L(ao.outputs["AO"], ar.inputs["Value"])
    # Wärme von unten (Höhe in der Mauer)
    sz = nt.nodes.new("ShaderNodeSeparateXYZ"); L(geo.outputs["Position"], sz.inputs[0])
    hb = nt.nodes.new("ShaderNodeMapRange"); hb.inputs["From Min"].default_value = 0.3; hb.inputs["From Max"].default_value = 0.75
    hb.inputs["To Min"].default_value = heat_bottom; hb.inputs["To Max"].default_value = 0.0
    L(sz.outputs[2], hb.inputs["Value"])
    glow = nt.nodes.new("ShaderNodeMath"); glow.operation = 'MAXIMUM'
    L(ar.outputs["Result"], glow.inputs[0]); L(hb.outputs["Result"], glow.inputs[1])
    gsc = nt.nodes.new("ShaderNodeMath"); gsc.operation = 'MULTIPLY'; gsc.inputs[1].default_value = 0.42
    L(glow.outputs[0], gsc.inputs[0])
    heat = nt.nodes.new("ShaderNodeMath"); heat.operation = 'MAXIMUM'
    L(crack.outputs[0], heat.inputs[0]); L(gsc.outputs[0], heat.inputs[1])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    e = ramp.color_ramp.elements
    e[0].position = 0.0; e[0].color = (0, 0, 0, 1)
    e[1].position = 0.92; e[1].color = (1.0, 0.85, 0.22, 1)
    x = e.new(0.15); x.color = (0.25, 0.008, 0.0, 1)
    y = e.new(0.42); y.color = (0.9, 0.07, 0.005, 1)
    z = e.new(0.68); z.color = (1.0, 0.32, 0.02, 1)
    L(heat.outputs[0], ramp.inputs[0])
    L(ramp.outputs[0], p.inputs["Emission Color"])
    p.inputs["Emission Strength"].default_value = 1.6
    return m

lamp_glow = glowm("GlutLicht", (1.0, 0.24, 0.03), 120.0)
seam_glow = glowm("FugenLicht", (1.0, 0.22, 0.03), 30.0)

def hot_metal(name, base, glow_corner=0.5, crack_mask=0.62):
    """heißes Metall: glimmt in Ecken und Rillen, dazu vereinzelte Glutrisse (wie die Deckplatten)"""
    m = lava_stone(name, base=base, crack_density=2.4, crack_width=0.012, crack_mask=crack_mask, heat_bottom=0.35)
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Metallic"].default_value = 0.8
    p.inputs["Roughness"].default_value = 0.4
    for n in m.node_tree.nodes:
        if n.type == 'MAP_RANGE' and abs(n.inputs["To Min"].default_value - 0.55) < 1e-6 and abs(n.inputs["From Min"].default_value - 0.3) < 1e-6:
            n.inputs["To Min"].default_value = glow_corner
    return m

stone = lava_stone("LavaStein")
stone_top = lava_stone("LavaSteinOben", crack_density=1.8, crack_width=0.013, crack_mask=0.38, heat_bottom=0.0)
metal = hot_metal("HeissesMetall", (0.05, 0.028, 0.035), glow_corner=0.7)
metal2 = hot_metal("HeissesMetall2", (0.14, 0.06, 0.05), glow_corner=0.55, crack_mask=0.7)
# Rillengrund: glühende Lava mit dunkler Kruste
deep = lava_stone("LavaKruste", base=(0.03, 0.015, 0.02), crack_density=7.0, crack_width=0.06, crack_mask=0.0, heat_bottom=0.0)
tube_x = molten("RöhreX", "x")
tube_z = molten("RöhreZ", "z")
lava_plane = molten("LavaFuge", "x", facing=False, strength=1.2, scale=5.0)

def octo(name, cx, cz, w, h, ch, y0, y1, material):
    pts = [(-w / 2 + ch, -h / 2), (w / 2 - ch, -h / 2), (w / 2, -h / 2 + ch), (w / 2, h / 2 - ch),
           (w / 2 - ch, h / 2), (-w / 2 + ch, h / 2), (-w / 2, h / 2 - ch), (-w / 2, -h / 2 + ch)]
    me = bpy.data.meshes.new(name)
    bm = _bm.new()
    a = [bm.verts.new((cx + x, y0, cz + z)) for x, z in pts]
    b = [bm.verts.new((cx + x, y1, cz + z)) for x, z in pts]
    bm.faces.new(a); bm.faces.new(list(reversed(b)))
    for i in range(8):
        j = (i + 1) % 8
        bm.faces.new([a[j], a[i], b[i], b[j]])
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

def rail_x(name, x0, x1, y, z):
    """waagerechte Glutröhre in gestufter Metallrinne mit Klammern und eigenem Licht"""
    w = x1 - x0
    cx = (x0 + x1) / 2
    box(name + "Grund", (cx, y + 0.07, z), (w, 0.04, 0.2), deep, bevel=0.005)
    for s in (-1, 1):
        box(name + "Lippe%d" % s, (cx, y - 0.01, z + s * 0.11), (w, 0.15, 0.04), metal2, bevel=0.012)
        box(name + "Stufe%d" % s, (cx, y + 0.03, z + s * 0.14), (w, 0.1, 0.035), metal, bevel=0.01)
    see_through(cyl(name + "Roehre", (cx, y, z), 0.065, w - 0.02, tube_x, rot=(0, 90, 0), verts=20))
    light_only(cyl(name + "Licht", (cx, y - 0.01, z), 0.04, w - 0.04, lamp_glow, rot=(0, 90, 0), verts=8), lamp_glow)
    k = 0
    x = x0 + 0.3
    while x < x1 - 0.15:
        box(name + "Klammer%d" % k, (x, y - 0.03, z), (0.06, 0.15, 0.22), metal2, bevel=0.012)
        k += 1
        x += 0.9

def rail_z(name, x, y, z0, z1):
    h = z1 - z0
    cz = (z0 + z1) / 2
    box(name + "Grund", (x, y + 0.05, cz), (0.15, 0.04, h), deep, bevel=0.005)
    for s in (-1, 1):
        box(name + "Lippe%d" % s, (x + s * 0.08, y - 0.01, cz), (0.035, 0.12, h), metal2, bevel=0.01)
    cyl(name + "Roehre", (x, y, cz), 0.04, h - 0.02, tube_z, verts=16)
    light_only(cyl(name + "Licht", (x, y - 0.005, cz), 0.028, h - 0.04, lamp_glow, verts=8), lamp_glow)
    for zz in (z0 + 0.15, z1 - 0.15):
        box(name + "Klammer", (x, y - 0.02, zz), (0.16, 0.11, 0.045), metal2, bevel=0.01)

# Sockel mit Glutrinne
prism("Sockel", -HALF, HALF, [(FR - 0.14, 0.0), (0.35, 0.0), (0.35, 0.3), (FR - 0.06, 0.3), (FR - 0.14, 0.24)], metal, bevel=0.015)
rail_x("Sockelrinne", -HALF, HALF, FR - 0.2, 0.13)

for i, (x0, x1) in enumerate(segments()):
    w = x1 - x0
    cx = (x0 + x1) / 2
    box("Kern%d" % i, (cx, -0.02, 0.67), (w, 0.55, 0.78), metal, bevel=0.01)
    # tiefe Fuge: Lava weit hinten, davor Licht, das die Plattenkanten anstrahlt
    see_through(box("Lava%d" % i, (cx, FR + 0.12, 0.66), (w - 0.04, 0.02, 0.66), lava_plane, bevel=0.0))
    light_only(box("FugenLicht%d" % i, (cx, FR + 0.085, 0.66), (w - 0.08, 0.01, 0.6), seam_glow, bevel=0.0), seam_glow)
    box("RahmenU%d" % i, (cx, FR - 0.03, 0.32), (w, 0.12, 0.05), metal2, bevel=0.01)
    pw = (w - 0.06) / 2
    for k in (-1, 1):
        octo("Platte%d_%d" % (i, k), cx + k * (pw / 2 + 0.012), 0.66, pw - 0.03, 0.6, 0.08, FR - 0.04, FR + 0.06, stone)
    rail_x("Oben%d" % i, x0, x1, FR - 0.1, 1.06)
    octo_top("Deck%d" % i, cx, -0.1, w - 0.06, 0.62, 0.08, 1.14, 1.18, stone_top)
    box("DeckRahmen%d" % i, (cx, -0.1, 1.13), (w, 0.74, 0.03), metal, bevel=0.006)

for i, x in enumerate(MODS):
    box("Halter%d" % i, (x, -0.13, 0.85), (0.8, 0.96, 1.1), metal, bevel=0.015)
    box("HFront%d" % i, (x, FR - 0.05, 0.85), (0.72, 0.06, 1.0), metal2, bevel=0.012)
    octo("HStein%d" % i, x, 0.58, 0.5, 0.32, 0.07, FR - 0.1, FR - 0.04, stone)
    octo("HStein2_%d" % i, x, 1.14, 0.5, 0.32, 0.07, FR - 0.1, FR - 0.04, stone)
    # Glutbalken in tiefer Fassung (wie an der Brücke)
    box("BFassung%d" % i, (x, FR - 0.12, 0.86), (0.62, 0.12, 0.22), metal2, bevel=0.018)
    box("BGrund%d" % i, (x, FR - 0.13, 0.86), (0.5, 0.13, 0.13), deep, bevel=0.005)
    see_through(cyl("Balken%d" % i, (x, FR - 0.17, 0.86), 0.05, 0.46, tube_x, rot=(0, 90, 0), verts=16))
    light_only(cyl("BLicht%d" % i, (x, FR - 0.18, 0.86), 0.03, 0.42, lamp_glow, rot=(0, 90, 0), verts=8), lamp_glow)
    for sx in (-1, 1):
        cyl("Bolzen", (x + sx * 0.27, FR - 0.185, 0.86), 0.025, 0.02, metal, rot=(90, 0, 0), verts=8)
    box("Kappe%d" % i, (x, -0.13, 1.44), (0.88, 1.02, 0.08), metal2, bevel=0.012)
    octo_top("KStein%d" % i, x, -0.13, 0.64, 0.8, 0.08, 1.48, 1.51, stone_top)

world.node_tree.nodes["Background"].inputs[0].default_value = (0.08, 0.04, 0.08, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.45
light('SUN', "Sonne", (0, -5, 8), (55, 0, -40), 1.8, (0.9, 0.88, 0.95))
light('AREA', "Rand", (0, 3.0, 3.5), (-60, 0, 0), 160, (1.0, 0.22, 0.05), size=12)
shadow_catcher()
glow_comp(tint=(1.0, 0.15, 0.02), threshold=0.7, size=9, alpha_gain=0.9, mix_strength=2.6)
