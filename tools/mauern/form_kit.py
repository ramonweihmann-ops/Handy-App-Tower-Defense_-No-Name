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
          cracks=None, corner=0.0, heat_bottom=0.0, glow=None, strength=1.6, dust=None, edge_wear=0.0, streaks=0.0, blotches=0.0):
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
    if streaks > 0:
        # senkrechte Schmutzschlieren (wie die gemalten Flecken an der Brücke)
        sm = nt.nodes.new("ShaderNodeMapping"); sm.inputs["Scale"].default_value = (9.0, 9.0, 0.9)
        Ln(geo.outputs["Position"], sm.inputs["Vector"])
        st = nt.nodes.new("ShaderNodeTexNoise"); st.inputs["Scale"].default_value = 2.5; st.inputs["Detail"].default_value = 4.0
        Ln(sm.outputs["Vector"], st.inputs["Vector"])
        sr2 = nt.nodes.new("ShaderNodeMapRange"); sr2.inputs["From Min"].default_value = 0.52; sr2.inputs["From Max"].default_value = 0.72
        sr2.inputs["To Max"].default_value = streaks
        Ln(st.outputs["Fac"], sr2.inputs["Value"])
        smx = nt.nodes.new("ShaderNodeMix"); smx.data_type = 'RGBA'
        Ln(sr2.outputs["Result"], smx.inputs["Factor"]); Ln(col, smx.inputs[6])
        smx.inputs[7].default_value = (b[0] * 0.5, b[1] * 0.45, b[2] * 0.4, 1)
        col = smx.outputs[2]
    if blotches > 0:
        # größere dunkle Flecken (gemalter Schmutz wie an der Brücke)
        bl = nt.nodes.new("ShaderNodeTexNoise"); bl.inputs["Scale"].default_value = 1.6; bl.inputs["Detail"].default_value = 3.0
        bl.inputs["Roughness"].default_value = 0.6
        Ln(geo.outputs["Position"], bl.inputs["Vector"])
        br = nt.nodes.new("ShaderNodeMapRange"); br.inputs["From Min"].default_value = 0.5; br.inputs["From Max"].default_value = 0.66
        br.inputs["To Max"].default_value = blotches
        Ln(bl.outputs["Fac"], br.inputs["Value"])
        bmx = nt.nodes.new("ShaderNodeMix"); bmx.data_type = 'RGBA'
        Ln(br.outputs["Result"], bmx.inputs["Factor"]); Ln(col, bmx.inputs[6])
        bmx.inputs[7].default_value = (b[0] * 0.55, b[1] * 0.45, b[2] * 0.38, 1)
        col = bmx.outputs[2]
    # dunkle Ecken (Schmutz)
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = 0.14; ao.samples = 16
    ad = nt.nodes.new("ShaderNodeMapRange"); ad.inputs["From Min"].default_value = 0.35; ad.inputs["From Max"].default_value = 1.0
    ad.inputs["To Min"].default_value = 0.75; ad.inputs["To Max"].default_value = 0.0
    Ln(ao.outputs["AO"], ad.inputs["Value"])
    md = nt.nodes.new("ShaderNodeMix"); md.data_type = 'RGBA'
    Ln(ad.outputs["Result"], md.inputs["Factor"]); Ln(col, md.inputs[6]); md.inputs[7].default_value = (b[0] * 0.15, b[1] * 0.15, b[2] * 0.18, 1)
    col = md.outputs[2]
    if dust:
        # Staub/Sand sammelt sich in Ecken und Fugen (hell statt dunkel), fleckig
        dn = nt.nodes.new("ShaderNodeTexNoise"); dn.inputs["Scale"].default_value = 9.0; dn.inputs["Detail"].default_value = 6.0
        Ln(geo.outputs["Position"], dn.inputs["Vector"])
        da = nt.nodes.new("ShaderNodeMapRange"); da.inputs["From Min"].default_value = 0.45; da.inputs["From Max"].default_value = 0.95
        da.inputs["To Min"].default_value = 0.85; da.inputs["To Max"].default_value = 0.0
        Ln(ao.outputs["AO"], da.inputs["Value"])
        dm = nt.nodes.new("ShaderNodeMath"); dm.operation = 'MULTIPLY'
        Ln(da.outputs["Result"], dm.inputs[0]); Ln(dn.outputs["Fac"], dm.inputs[1])
        dmx = nt.nodes.new("ShaderNodeMix"); dmx.data_type = 'RGBA'
        Ln(dm.outputs[0], dmx.inputs["Factor"]); Ln(col, dmx.inputs[6]); dmx.inputs[7].default_value = (*L_(dust), 1)
        col = dmx.outputs[2]
    if edge_wear > 0:
        # abgeriebene, helle Kanten (nur Cycles: Spitzheit der Geometrie)
        pt = nt.nodes.new("ShaderNodeNewGeometry")
        pr = nt.nodes.new("ShaderNodeMapRange"); pr.inputs["From Min"].default_value = 0.52; pr.inputs["From Max"].default_value = 0.6
        pr.inputs["To Max"].default_value = edge_wear
        Ln(pt.outputs["Pointiness"], pr.inputs["Value"])
        emx = nt.nodes.new("ShaderNodeMix"); emx.data_type = 'RGBA'
        Ln(pr.outputs["Result"], emx.inputs["Factor"]); Ln(col, emx.inputs[6])
        emx.inputs[7].default_value = (min(1, b[0] * 1.9 + 0.05), min(1, b[1] * 1.9 + 0.05), min(1, b[2] * 1.9 + 0.05), 1)
        col = emx.outputs[2]
    Ln(col, p.inputs["Base Color"])
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
    # Kristalle wie an den Brücken: facettierte, glasige Körper mit leuchtendem Kern, in einer Metallfassung mit Krallen
    outer = bpy.data.materials.new("KristallHuelle"); outer.use_nodes = True
    po = outer.node_tree.nodes["Principled BSDF"]
    ccl = L_(cc)
    po.inputs["Base Color"].default_value = (*ccl, 1)
    po.inputs["Roughness"].default_value = 0.1
    po.inputs["Transmission Weight"].default_value = 0.35
    po.inputs["IOR"].default_value = 1.5
    po.inputs["Emission Color"].default_value = (*ccl, 1)
    po.inputs["Emission Strength"].default_value = C.get("crystal_glow", 1.2) * 0.22
    core_m = pm("KristallKern", cc, emit=tuple(min(1.0, v * 0.6 + 0.4) for v in cc), strength=C.get("crystal_glow", 1.2) * 3.0)
    socket_m = plate("Fassung", C.get("socket", C["metal2"]), metal=0.85, rough=0.3, bump=0.1, scratches=0.25, edge_wear=0.4)
    prong_m = metal2

    def crystal_mesh(name, h, r, tip):
        me = bpy.data.meshes.new(name)
        bm = _bm.new()
        lo = [bm.verts.new((r * 0.8 * math.cos(k * math.pi / 3), r * 0.8 * math.sin(k * math.pi / 3), 0.0)) for k in range(6)]
        hi = [bm.verts.new((r * math.cos(k * math.pi / 3 + 0.08), r * math.sin(k * math.pi / 3 + 0.08), h)) for k in range(6)]
        top = bm.verts.new((r * 0.12, -r * 0.08, h + tip))
        bm.faces.new(list(reversed(lo)))
        for k in range(6):
            j = (k + 1) % 6
            bm.faces.new([lo[k], lo[j], hi[j], hi[k]])
            bm.faces.new([hi[k], hi[j], top])
        _bm.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new(name, me); scene.collection.objects.link(o)
        bv = o.modifiers.new("Bevel", 'BEVEL'); bv.width = 0.006; bv.segments = 1; bv.limit_method = 'ANGLE'
        return o

    def crystal(name, loc, h, r, rx, ry, core=True):
        o = crystal_mesh(name, h, r, r * 1.7)
        o.data.materials.append(outer)
        o.location = loc; o.rotation_euler = (math.radians(rx), math.radians(ry), random.uniform(0, 1))
        if core:
            c = crystal_mesh(name + "Kern", h * 0.8, r * 0.45, r * 0.9)
            c.data.materials.append(core_m)
            c.location = loc; c.rotation_euler = o.rotation_euler
            see_through(c)
        return o

    for i, x in enumerate(MODS):
        y0 = -0.13
        z0 = TOP_Z
        # Fassung: Sockel, Ring mit Leuchtfuge, vier Krallen
        cyl("KSockel%d" % i, (x, y0, z0 + 0.04), 0.19, 0.08, socket_m, verts=8, bevel=0.012)
        cyl("KRing%d" % i, (x, y0, z0 + 0.1), 0.15, 0.04, prong_m, verts=16, bevel=0.006)
        see_through(cyl("KFuge%d" % i, (x, y0, z0 + 0.085), 0.155, 0.01, core_m, verts=24))
        for a in range(4):
            ang = a * math.pi / 2 + math.pi / 4
            pr = box("KKralle%d_%d" % (i, a), (x + 0.13 * math.cos(ang), y0 + 0.13 * math.sin(ang), z0 + 0.2), (0.035, 0.035, 0.22), prong_m, bevel=0.008)
            pr.rotation_euler = (math.sin(ang) * 0.3, -math.cos(ang) * 0.3, ang)
        # Gruppe: großer Kristall, vier kleinere, Splitter
        crystal("KHaupt%d" % i, (x, y0, z0 + 0.1), random.uniform(0.52, 0.6), 0.11, random.uniform(-6, 6), random.uniform(-6, 6))
        for k, (dx, dy, rx, ry, hh, rr) in enumerate([(-0.1, 0.05, -10, -22, 0.3, 0.06), (0.1, -0.04, 8, 24, 0.27, 0.055),
                                                     (0.03, 0.1, 26, 6, 0.22, 0.05), (-0.05, -0.09, -24, -8, 0.18, 0.045)]):
            crystal("KNeben%d_%d" % (i, k), (x + dx, y0 + dy, z0 + 0.1), hh * random.uniform(0.9, 1.15), rr, rx, ry, core=k < 2)
        for k in range(3):
            sx = random.choice((-1, 1))
            crystal("KSplitter%d_%d" % (i, k), (x + sx * random.uniform(0.22, 0.34), y0 + random.uniform(-0.25, 0.2), z0 + 0.0),
                    random.uniform(0.07, 0.12), 0.025, random.uniform(-30, 30), random.uniform(-30, 30), core=False)
        light_only(sphere("KLicht%d" % i, (x, -0.35, TOP_Z + 0.3), 0.06, lamp_glow), lamp_glow)
if "vines" in P:
    # Ranken wie an den Brückenpfeilern: zwei ineinander gedrehte Stränge und ein dünner, dazu spitze Blätter.
    # Eine durchgehende Ranke läuft oben über alle Deckel und Erhöhungen (Kommentar 22.11.), dazu Girlanden vorn.
    from mathutils import Vector, Matrix
    vine_a = plate("RankeA", C.get("vine_a", (0.2, 0.36, 0.1)), rough=0.6, bump=0.6, var=0.8)
    vine_b = plate("RankeB", C.get("vine_b", (0.34, 0.52, 0.15)), rough=0.55, bump=0.6, var=0.8)
    vine_c = plate("RankeC", C.get("vine_c", (0.5, 0.6, 0.22)), rough=0.5, bump=0.4, var=0.6)
    leaf_ms = [plate("Blatt%d" % k, c, rough=0.45, bump=0.3, var=0.7) for k, c in enumerate(C.get("leaves", [(0.3, 0.56, 0.12), (0.42, 0.66, 0.16), (0.22, 0.44, 0.1)]))]
    bud = pm("Knospe", C["light"], emit=C["light"], strength=4.0)
    bud_glow = glowm("KnospenLicht", LIGHT, C.get("bud_power", 25.0))

    def leaf_mesh():
        me = bpy.data.meshes.new("Blatt")
        bm = _bm.new()
        v = [bm.verts.new(p_) for p_ in [(0, 0, 0), (0.42, 0.34, -0.06), (0.45, 0, 0.05), (0.42, -0.34, -0.06), (1.0, 0, -0.04),
                                         (0.75, 0.2, -0.02), (0.75, -0.2, -0.02), (0.18, 0.2, -0.03), (0.18, -0.2, -0.03)]]
        for f in [(0, 7, 2), (7, 1, 2), (1, 5, 2), (5, 4, 2), (0, 2, 8), (8, 2, 3), (3, 2, 6), (6, 2, 4)]:
            bm.faces.new([v[i] for i in f])
        _bm.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me); bm.free()
        for pl in me.polygons:
            pl.use_smooth = True
        return me
    LEAF = leaf_mesh()

    def catmull(pts, step=0.02):
        pts = [Vector(p_) for p_ in pts]
        ext = [pts[0] * 2 - pts[1]] + pts + [pts[-1] * 2 - pts[-2]]
        out = []
        for i in range(1, len(ext) - 2):
            p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
            n = max(2, int((p2 - p1).length / step))
            for k in range(n):
                t = k / n
                out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
        out.append(pts[-1])
        return out

    def frames(path):
        res = []
        for i, p_ in enumerate(path):
            t = (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()
            up = Vector((0, 0, 1)) if abs(t.z) < 0.92 else Vector((0, -1, 0))
            n1 = t.cross(up).normalized()
            n2 = t.cross(n1).normalized()
            res.append((p_, t, n1, n2))
        return res

    def poly(name, pts, radius, material, wobble=0.15):
        cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = radius; cu.bevel_resolution = 3
        sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
        for k, (pt, p_) in enumerate(zip(sp.points, pts)):
            pt.co = (p_.x, p_.y, p_.z, 1)
            pt.radius = 1.0 + wobble * math.sin(k * 0.37) * math.sin(k * 0.11)
        sp.use_smooth = True
        o = bpy.data.objects.new(name, cu); scene.collection.objects.link(o); o.data.materials.append(material)
        return o

    def twisted(name, ctrl, r=0.032, helix=0.03, turn=0.34, leaf_every=0.085, leaf_size=(0.17, 0.08), thin=True, end_leaves=True):
        path = catmull(ctrl)
        fr = frames(path)
        dist = 0.0
        A, Bs, Cs = [], [], []
        for i, (p_, t, n1, n2) in enumerate(fr):
            if i:
                dist += (p_ - fr[i - 1][0]).length
            ph = dist / turn * 2 * math.pi
            A.append(p_ + (n1 * math.cos(ph) + n2 * math.sin(ph)) * helix)
            Bs.append(p_ - (n1 * math.cos(ph) + n2 * math.sin(ph)) * helix)
            ph2 = dist / (turn * 1.7) * 2 * math.pi + 1.0
            Cs.append(p_ + (n1 * math.cos(ph2) + n2 * math.sin(ph2)) * (helix + r * 1.1))
        poly(name + "A", A, r, vine_a)
        poly(name + "B", Bs, r * 0.92, vine_b)
        if thin:
            poly(name + "C", Cs, r * 0.42, vine_c, wobble=0.3)
        # Blätter abwechselnd nach vorn/oben und zur Seite, damit man sie von schräg oben sieht
        acc = 0.0
        side = 1
        for i in range(1, len(fr)):
            acc += (fr[i][0] - fr[i - 1][0]).length
            if acc < leaf_every * random.uniform(0.7, 1.3):
                continue
            acc = 0.0
            p_, t, n1, n2 = fr[i]
            a = random.uniform(-0.9, 1.5)
            d = (n1 * math.cos(a) - n2 * math.sin(a)) + t * (side * random.uniform(0.2, 0.7))
            d.normalize()
            side = -side
            upv = -n2 if abs(d.dot(-n2)) < 0.95 else n1
            yv = upv.cross(d).normalized()
            zv = d.cross(yv).normalized()
            s_ = leaf_size[0] * random.uniform(0.75, 1.25)
            ob = bpy.data.objects.new("Blatt", LEAF); scene.collection.objects.link(ob)
            m3 = Matrix((d, yv, zv)).transposed()
            rot = Matrix.Rotation(random.uniform(-0.5, 0.5), 3, 'X')
            wy = leaf_size[1] / 0.34 * s_ / leaf_size[0]
            ob.matrix_world = Matrix.Translation(p_ + d * (helix + r)) @ (m3 @ rot).to_4x4() @ Matrix.Diagonal((s_, wy, s_, 1))
            ob.material_slots[0].link = 'OBJECT'
            ob.material_slots[0].material = random.choice(leaf_ms)
        return fr

    if not LEAF.materials:
        LEAF.materials.append(leaf_ms[0])
    # oben: über alle Deckel – zwischen den Erhöhungen auf der Deckplatte, seitlich an der Erhöhung hinauf, quer über
    # ihre Oberseite und auf der anderen Seite wieder hinab
    ctrl = [(-HALF - 0.1, -0.42, 1.23)]
    for j, x in enumerate(MODS):
        xm = (x - 1.8 / 2) if j else (x - 0.75)
        ctrl += [(xm - 0.2, -0.44 + random.uniform(-0.04, 0.04), 1.235), (xm + 0.2, -0.4 + random.uniform(-0.04, 0.04), 1.23)]
        sw = random.choice((-1, 1))
        ctrl += [(x - 0.56, -0.38, 1.27), (x - 0.53, -0.3, 1.42), (x - 0.4, -0.22, 1.555),
                 (x - 0.14, -0.12 + sw * 0.08, 1.585), (x + 0.12, -0.18 - sw * 0.08, 1.585), (x + 0.4, -0.3, 1.555),
                 (x + 0.53, -0.36, 1.42), (x + 0.56, -0.42, 1.27)]
    ctrl += [(HALF - 0.45, -0.43, 1.23), (HALF + 0.1, -0.42, 1.23)]
    top_fr = twisted("RankeOben", ctrl, r=0.04, helix=0.036, turn=0.4, leaf_every=0.13, leaf_size=(0.22, 0.1))
    # Knospen mit grünem Leuchten oben auf den Erhöhungen (Licht wie an den Brückenpfeilern)
    last = -9.0
    for p_, t, n1, n2 in top_fr:
        if p_.z > 1.55 and (p_ - Vector((last, 0, 0))).x > 0.3:
            last = p_.x
            sphere("Knospe", p_ + n1 * random.choice((-1, 1)) * 0.075 - n2 * 0.03, 0.024, bud)
    for j, x in enumerate(MODS):
        light_only(sphere("KnLicht%d" % j, (x, -0.8, 1.75), 0.05, bud_glow), bud_glow)
    # vorn: Girlanden zwischen den Erhöhungen und je eine Ranke, die die Erhöhung hinaufklettert und oben einmündet
    for i in range(len(edges) - 1):
        x0 = edges[i] + 0.4; x1 = edges[i + 1] - 0.4
        mid = (x0 + x1) / 2
        twisted("Girlande%d" % i, [(x0, FR - 0.2, 1.22), (x0 + 0.2, FR - 0.25, 1.05), (mid, FR - 0.27, 0.95 + random.uniform(-0.04, 0.03)),
                                   (x1 - 0.2, FR - 0.25, 1.05), (x1, FR - 0.2, 1.22)], r=0.02, helix=0.02, turn=0.26, leaf_every=0.16,
                leaf_size=(0.15, 0.07), thin=False)
    for i, x in enumerate(MODS):
        twisted("PRanke%d" % i, [(x - 0.42, FR - 0.1, 0.3), (x - 0.4, FR - 0.16, 0.62), (x - 0.1, FR - 0.17, 1.0), (x + 0.3, FR - 0.15, 1.32),
                                 (x + 0.53, -0.46, 1.42)], r=0.022, helix=0.022, turn=0.28, leaf_every=0.14, leaf_size=(0.13, 0.06), thin=False)
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
    rope = pm("Tau", C.get("rope", (0.72, 0.6, 0.42)), rough=0.85)
    for i in range(len(edges) - 1):
        x0 = edges[i] + 0.4; x1 = edges[i + 1] - 0.4
        tube("Tau%d" % i, [(x0, FR - 0.24, 1.3), ((x0 + x1) / 2, FR - 0.3, 1.17), (x1, FR - 0.24, 1.3)], 0.04, rope)
if "hazard" in P:
    warn = stripes("Warn", (0.95, 0.7, 0.1), (0.05, 0.05, 0.06), scale=10.0)
    for i in range(len(edges) - 1):
        x0 = edges[i] + (0.4 if i > 0 else 0.0); x1 = edges[i + 1] - (0.4 if i < len(edges) - 2 else 0.0)
        box("Warn%d" % i, ((x0 + x1) / 2, FR - 0.095, 0.32), (x1 - x0 - 0.05, 0.02, 0.05), warn, bevel=0.0)
if "rods" in P:
    # Blitzableiter wie die Lampenmasten am Brückengeländer (Kommentar 22.11.: dicker, mehr Detail, nicht zu auffällig):
    # Sockel mit Warnring, Mast mit drei Isolatorscheiben, Lampengehäuse mit gelbem Licht, kurze Fangspitze
    rodm = plate("Mast", C.get("rod", (0.5, 0.53, 0.58)), metal=0.9, rough=0.3, bump=0.1, scratches=0.3, edge_wear=0.3)
    insul = pm("Isolator", (0.2, 0.22, 0.26), rough=0.18)
    warn_r = stripes("WarnRing", (0.95, 0.7, 0.1), (0.05, 0.05, 0.06), scale=10.0)
    lampm = pm("MastLampe", C["light"], emit=C["light"], strength=5.0)
    mast_glow = glowm("MastLicht", LIGHT, C.get("mast_power", 12.0))
    for i, x in enumerate(MODS):
        y0 = -0.13
        z0 = TOP_Z
        cyl("MSockel%d" % i, (x, y0, z0 + 0.03), 0.11, 0.06, metal, verts=8, bevel=0.01)
        cyl("MWarn%d" % i, (x, y0, z0 + 0.08), 0.085, 0.04, warn_r, verts=24)
        cyl("MFuss%d" % i, (x, y0, z0 + 0.12), 0.06, 0.04, metal2, verts=16, bevel=0.006)
        cyl("Mast%d" % i, (x, y0, z0 + 0.32), 0.038, 0.4, rodm, verts=12)
        for k, dz in enumerate((0.2, 0.25, 0.3)):
            cyl("MIso%d_%d" % (i, k), (x, y0, z0 + dz), 0.06 - k * 0.006, 0.022, insul, verts=20, bevel=0.006)
        cyl("MGehaeuse%d" % i, (x, y0, z0 + 0.53), 0.05, 0.03, metal2, verts=16, bevel=0.005)
        see_through(cyl("MGlas%d" % i, (x, y0, z0 + 0.575), 0.038, 0.06, lampm, verts=16))
        for a_ in range(4):
            ang = a_ * math.pi / 2
            box("MSteg%d" % i, (x + 0.042 * math.cos(ang), y0 + 0.042 * math.sin(ang), z0 + 0.575), (0.012, 0.012, 0.07), metal2, bevel=0.0)
        bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.055, radius2=0.012, depth=0.05, location=(x, y0, z0 + 0.63))
        c_ = bpy.context.active_object; c_.data.materials.append(metal2); bpy.ops.object.shade_smooth()
        cyl("MSpitze%d" % i, (x, y0, z0 + 0.71), 0.008, 0.12, rodm, verts=8)
        light_only(sphere("MLicht%d" % i, (x, -0.45, z0 + 0.6), 0.03, mast_glow), mast_glow)
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
tint = L_(C.get("glow_tint", C["light"]))  # Schein einfärben; neutral, wenn warme und kalte Lichter gemischt sind
glow_comp(tint=tint, threshold=C.get("glow_threshold", 0.7), size=9, alpha_gain=0.9, mix_strength=C.get("glow_mix", 2.0))
