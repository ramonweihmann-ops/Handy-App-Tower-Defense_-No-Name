# Raumstation, Zusatz (Kommentar 22.11.: erstes Level muss fesseln – mehr Raumstation und Leuchten, Enden der
# Leuchtröhren detaillierter): Endfassungen an allen Röhren, Schein um die Röhren, Bildschirme, Schildsender mit
# Energiekern, orange Warnlampen wie an der Brücke, Lüftungsgitter mit Leuchten dahinter.
core_white = pm("RöhrenKern", (0.85, 0.97, 1.0), emit=(0.8, 0.96, 1.0), strength=6.0)
cap_dark = plate("Fassung", (0.08, 0.1, 0.16), metal=0.85, rough=0.35, bump=0.1, scratches=0.2)
orange = pm("Warnlampe", (1.0, 0.55, 0.15), emit=(1.0, 0.5, 0.1), strength=5.0)
orange_light = glowm("WarnLicht", L_((1.0, 0.5, 0.12)), 25.0)

def halo(name, color, strength, alpha):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (*L_(color), 1); em.inputs[1].default_value = strength
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

glow_halo = halo("Schein", (0.25, 0.7, 1.0), 2.2, 1.0)

def end_cap(name, x, y, z, side):
    """Endfassung einer waagerechten Röhre: Metallhülse mit zwei Ringen, Schrauben und hell leuchtendem Abschluss"""
    cyl(name + "Huelse", (x, y, z), 0.088, 0.12, cap_dark, rot=(0, 90, 0), verts=24, bevel=0.01)
    for k, dx in enumerate((-0.045, 0.045)):
        cyl(name + "Ring%d" % k, (x + dx, y, z), 0.096, 0.018, metal2, rot=(0, 90, 0), verts=24, bevel=0.004)
    see_through(cyl(name + "Licht", (x - side * 0.07, y, z), 0.05, 0.02, core_white, rot=(0, 90, 0), verts=20))
    for a in (0.0, 2.1, 4.2):
        sphere(name + "Schraube", (x, y + 0.088 * math.sin(a), z + 0.088 * math.cos(a)), 0.012, metal2)

for i, (x0, x1) in enumerate(segments()):
    # helle Kerne und Schein in den oberen Röhren
    w = x1 - x0
    cx = (x0 + x1) / 2
    see_through(cyl("Kern%d" % i, (cx, FR - 0.125, 1.06), 0.03, w - 0.3, core_white, rot=(0, 90, 0), verts=10))
    see_through(cyl("Schein%d" % i, (cx, FR - 0.1, 1.06), 0.14, w - 0.2, glow_halo, rot=(0, 90, 0), verts=20))
    end_cap("CapL%d" % i, x0 + 0.07, FR - 0.1, 1.06, -1)
    end_cap("CapR%d" % i, x1 - 0.07, FR - 0.1, 1.06, 1)
    # Lüftungsgitter in der Fuge zwischen den Platten mit Leuchten dahinter
    for k in range(4):
        box("Lamelle%d_%d" % (i, k), (cx, FR - 0.05, 0.5 + k * 0.1), (0.05, 0.03, 0.035), cap_dark, bevel=0.004)
see_through(cyl("SockelSchein", (0, FR - 0.2, 0.13), 0.13, HALF * 2, glow_halo, rot=(0, 90, 0), verts=20))

for i, x in enumerate(MODS):
    # Endfassungen am Leuchtbalken
    for sx in (-1, 1):
        cyl("BCap%d_%d" % (i, sx), (x + sx * 0.255, FR - 0.17, 0.86), 0.07, 0.07, cap_dark, rot=(0, 90, 0), verts=20, bevel=0.008)
        cyl("BRing%d_%d" % (i, sx), (x + sx * 0.225, FR - 0.17, 0.86), 0.076, 0.016, metal2, rot=(0, 90, 0), verts=20)
    see_through(cyl("BKern%d" % i, (x, FR - 0.17, 0.86), 0.02, 0.4, core_white, rot=(0, 90, 0), verts=10))
    see_through(cyl("BSchein%d" % i, (x, FR - 0.17, 0.86), 0.12, 0.44, glow_halo, rot=(0, 90, 0), verts=20))
    # Bildschirm über dem oberen Steinfeld
    scr = flow("Bildschirm%d" % i, "z", GLOW, facing=False, strength=1.1, scale=22.0)
    box("BRahmen%d" % i, (x, FR - 0.11, 1.15), (0.44, 0.03, 0.24), cap_dark, bevel=0.01)
    see_through(box("BSchirm%d" % i, (x, FR - 0.125, 1.15), (0.36, 0.01, 0.17), scr, bevel=0.0))
    # orange Warnlampen seitlich (wie an der Brücke)
    for sx in (-1, 1):
        box("WGehaeuse%d_%d" % (i, sx), (x + sx * 0.33, FR - 0.1, 0.48), (0.09, 0.08, 0.16), cap_dark, bevel=0.01)
        see_through(box("WLampe%d_%d" % (i, sx), (x + sx * 0.33, FR - 0.145, 0.48), (0.055, 0.01, 0.11), orange, bevel=0.0))
        light_only(sphere("WLicht%d_%d" % (i, sx), (x + sx * 0.33, FR - 0.3, 0.48), 0.03, orange_light), orange_light)
    # Schildsender mit Energiekern auf dem Pfeiler
    cyl("SSockel%d" % i, (x, -0.13, TOP_Z + 0.05), 0.2, 0.1, cap_dark, verts=24, bevel=0.012)
    cyl("SRing%d" % i, (x, -0.13, TOP_Z + 0.12), 0.17, 0.035, metal2, verts=24, bevel=0.006)
    for a in range(4):
        ang = a * math.pi / 2 + math.pi / 4
        f_ = box("SFinne%d_%d" % (i, a), (x + 0.15 * math.cos(ang), -0.13 + 0.15 * math.sin(ang), TOP_Z + 0.2), (0.04, 0.04, 0.2), metal2, bevel=0.008)
        f_.rotation_euler = (0, 0, ang)
    see_through(sphere("SKern%d" % i, (x, -0.13, TOP_Z + 0.24), 0.085, core_white))
    see_through(sphere("SSchein%d" % i, (x, -0.13, TOP_Z + 0.24), 0.16, glow_halo))
    light_only(sphere("SLicht%d" % i, (x, -0.35, TOP_Z + 0.3), 0.05, lamp_glow), lamp_glow)
