# Lava-Asteroid, Detailstufe 2 (zweite Fassung nach Kommentar „zu knuffig“): wie die Brücke gebaut – große Steinplatten
# mit abgeschrägten Ecken in dunklen Metallrahmen, glühende Fugen dazwischen, Risse mit Glut, dicke Neonröhren in
# Metallrinnen, Pfeiler als Metallhalter mit waagerechtem Glutbalken (wie an der Brücke), scharfe statt runde Kanten
import bmesh as _bm
stone = rich("Stein", (0.06, 0.035, 0.065), metal=0.0, rough=0.82, dirt=(0.015, 0.006, 0.012), var=0.45, grad=0.25, bump=1.0,
             cracks=(1.0, 0.14, 0.03), crack_emit=0.8, crack_width=0.008, crack_mask=0.56)
metal = rich("Metall", (0.05, 0.028, 0.035), metal=0.85, rough=0.42, dirt=(0.02, 0.015, 0.015), scratches=0.25, bump=0.15)
metal2 = rich("Metall2", (0.12, 0.05, 0.045), metal=0.85, rough=0.38, dirt=(0.03, 0.02, 0.02), scratches=0.3, bump=0.1)
# Farben gemessen an der Brücke (21.11.2026): Röhrenkern blassgelb (254,253,199), dann gelb, orange (247,117,42),
# breiter orangeroter Schein; Fugen und Risse orangerot (209,83,39)
lava = glowm("Glut", (1.0, 0.14, 0.03), 0.8)
def tube_mat(name, core, mid, edge, strength):
    """Röhre wie gemalt: Kern gelb, nach außen orange und rot (nach Blickwinkel)"""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.45
    cr = nt.nodes.new("ShaderNodeValToRGB")
    e = cr.color_ramp.elements
    e[0].position = 0.0; e[0].color = (*core, 1)
    e[1].position = 0.75; e[1].color = (*edge, 1)
    e2 = e.new(0.4); e2.color = (*mid, 1)
    nt.links.new(lw.outputs["Facing"], cr.inputs[0])
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs[1].default_value = strength
    nt.links.new(cr.outputs[0], em.inputs[0]); nt.links.new(em.outputs[0], out.inputs[0])
    return m
neon = tube_mat("Neon", (1.0, 0.9, 0.15), (1.0, 0.32, 0.03), (0.6, 0.03, 0.0), 1.3)

def halo_mat(name, color, strength, alpha):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (*color, 1); em.inputs[1].default_value = strength
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.5
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
    nt.links.new(lw.outputs["Facing"], inv.inputs[1])
    pw = nt.nodes.new("ShaderNodeMath"); pw.operation = 'POWER'; pw.inputs[1].default_value = 2.0
    nt.links.new(inv.outputs[0], pw.inputs[0])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = alpha
    nt.links.new(pw.outputs[0], mul.inputs[0])
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(mul.outputs[0], mix.inputs[0]); nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    m.blend_method = 'BLEND'
    return m
glow_halo = halo_mat("Schein", (0.9, 0.08, 0.005), 1.0, 0.95)

def octo(name, cx, cz, w, h, ch, y0, y1, material):
    """Platte mit abgeschrägten Ecken, Vorderseite bei y0 (Kamera), Rückseite bei y1"""
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
    bv = o.modifiers.new("Bevel", 'BEVEL'); bv.width = 0.012; bv.segments = 1; bv.limit_method = 'ANGLE'
    return o

def octo_top(name, cx, cy, w, d, ch, z0, z1, material):
    """liegende Platte mit abgeschrägten Ecken (Draufsicht), von z0 bis z1"""
    o = octo(name, 0, 0, w, d, ch, 0, z1 - z0, material)
    o.rotation_euler = (math.radians(-90), 0, 0)
    o.location = (cx, cy, z1)
    return o

# Sockel: Metall mit Glutrinne
prism("Sockel", -HALF, HALF, [(FR - 0.12, 0.0), (0.35, 0.0), (0.35, 0.28), (FR - 0.06, 0.28), (FR - 0.12, 0.22)], metal, bevel=0.012)
box("Glutrinne", (0, FR - 0.125, 0.12), (HALF * 2, 0.02, 0.04), neon, bevel=0.0)
cyl("RSchein", (0, FR - 0.13, 0.12), 0.06, HALF * 2, glow_halo, rot=(0, 90, 0), verts=16)

for i, (x0, x1) in enumerate(segments()):
    w = x1 - x0
    cx = (x0 + x1) / 2
    box("Kern%d" % i, (cx, -0.05, 0.66), (w, 0.6, 0.76), metal, bevel=0.01)
    box("GlutGrund%d" % i, (cx, FR + 0.03, 0.66), (w - 0.06, 0.02, 0.7), lava, bevel=0.0)
    # Metallrahmen
    box("RahmenO%d" % i, (cx, FR - 0.02, 1.0), (w, 0.1, 0.07), metal2, bevel=0.008)
    box("RahmenU%d" % i, (cx, FR - 0.02, 0.33), (w, 0.1, 0.06), metal2, bevel=0.008)
    # zwei Steinplatten mit abgeschrägten Ecken, Glutfuge dazwischen
    pw = (w - 0.06) / 2
    for k in (-1, 1):
        octo("Platte%d_%d" % (i, k), cx + k * (pw / 2 + 0.01), 0.665, pw - 0.015, 0.6, 0.08, FR - 0.03, FR + 0.02, stone)
    # Neonröhre in Metallrinne oben (wie am Brückenrand)
    box("Rinne%d" % i, (cx, FR - 0.08, 1.07), (w, 0.1, 0.07), metal, bevel=0.008)
    cyl("Neon%d" % i, (cx, FR - 0.12, 1.075), 0.05, w - 0.04, neon, rot=(0, 90, 0), verts=12)
    cyl("Schein%d" % i, (cx, FR - 0.12, 1.075), 0.15, w - 0.02, glow_halo, rot=(0, 90, 0), verts=16)
    # Deckplatten oben
    octo_top("Deck%d" % i, cx, -0.12, w - 0.05, 0.75, 0.08, 1.12, 1.15, stone)
    box("DeckRahmen%d" % i, (cx, -0.12, 1.1), (w, 0.86, 0.04), metal2, bevel=0.006)
    plight((cx, FR - 0.35, 1.0), (1.0, 0.22, 0.04), 7.0)

for i, x in enumerate(MODS):
    # Metallhalter wie an der Brücke
    box("Halter%d" % i, (x, -0.13, 0.85), (0.8, 0.96, 1.1), metal, bevel=0.015)
    box("HFront%d" % i, (x, FR - 0.05, 0.85), (0.72, 0.06, 1.0), metal2, bevel=0.01)
    octo("HStein%d" % i, x, 0.6, 0.56, 0.36, 0.07, FR - 0.09, FR - 0.05, stone)
    octo("HStein2_%d" % i, x, 1.12, 0.56, 0.36, 0.07, FR - 0.09, FR - 0.05, stone)
    # waagerechter Glutbalken in Fassung
    box("BFassung%d" % i, (x, FR - 0.1, 0.86), (0.6, 0.06, 0.13), metal, bevel=0.01)
    box("Balken%d" % i, (x, FR - 0.13, 0.86), (0.46, 0.02, 0.055), neon, bevel=0.0)
    box("BSchein%d" % i, (x, FR - 0.14, 0.86), (0.54, 0.01, 0.13), glow_halo, bevel=0.0)
    for sx in (-1, 1):
        cyl("Bolzen", (x + sx * 0.27, FR - 0.135, 0.86), 0.02, 0.02, metal2, rot=(90, 0, 0), verts=8)
        cyl("SNeon%d_%d" % (i, sx), (x + sx * 0.37, FR - 0.08, 0.85), 0.035, 1.0, neon, verts=10)
        cyl("SSchein%d_%d" % (i, sx), (x + sx * 0.37, FR - 0.08, 0.85), 0.11, 1.02, glow_halo, verts=16)
    plight((x, FR - 0.4, 0.86), (1.0, 0.25, 0.05), 7.0)
    box("Kappe%d" % i, (x, -0.13, 1.44), (0.88, 1.02, 0.08), metal2, bevel=0.012)
    octo_top("KStein%d" % i, x, -0.13, 0.64, 0.8, 0.08, 1.48, 1.51, stone)

world.node_tree.nodes["Background"].inputs[0].default_value = (0.08, 0.04, 0.08, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.5
light('SUN', "Sonne", (0, -5, 8), (55, 0, -40), 2.3, (0.9, 0.88, 0.95))
light('AREA', "Rand", (0, 3.0, 3.5), (-60, 0, 0), 260, (1.0, 0.22, 0.05), size=12)
shadow_catcher()
glow_comp(tint=(1.0, 0.16, 0.02), threshold=0.6, size=8, alpha_gain=0.95, mix_strength=2.6)
