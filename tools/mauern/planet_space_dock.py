# Raumstation im Comic-Stil: wuchtige, abgerundete Barrikade (blauer Stahl, weiße Panzerplatten mit leuchtendem
# Pfeil), runde Schildtürme mit Goldring und Leuchtkugel, Energiestrahl und Wabenschild dazwischen.
CYAN = (0.15, 0.7, 1.0)
steel = toon("Stahl", (0.2, 0.33, 0.62), shade=0.5, rim=CYAN, rim_amount=0.45)
armor = toon("Panzer", (0.74, 0.81, 0.92), shade=0.6, light=1.12, rim=CYAN, rim_amount=0.35)
dark = toon("Dunkel", (0.07, 0.09, 0.16), gloss=0.3, rim=CYAN, rim_amount=0.3)
gold = toon("Gold", (1.0, 0.72, 0.18), shade=0.6, gloss=0.7)
glow = glowmat("Licht", CYAN, 4.0)
lamp = glowmat("Lampe", (1.0, 0.5, 0.08), 5.0)
beam = glowmat("Strahl", (0.45, 0.85, 1.0), 6.0)
shield = shield_mat("Schild", (0.2, 0.7, 1.0), strength=3.5, alpha=0.9)

def flat_stripes(name, c1, c2, scale=9.0):
    m = stripes(name, c1, c2, scale)
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    em = nt.nodes.new("ShaderNodeEmission")
    cr = [n for n in nt.nodes if n.type == 'VALTORGB'][0]
    nt.links.new(cr.outputs[0], em.inputs[0])
    nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs[0])
    return m
warn = flat_stripes("Warn", (1.0, 0.76, 0.1), (0.06, 0.06, 0.09))

HALF = 6.4
PY = [-5.25, -3.5, -1.75, 0.0, 1.75, 3.5, 5.25]
FR = -0.62

# Sockel, rund gefast, vorn ein Warnband
box("Sockel", (0, -0.15, 0.17), (HALF * 2, 0.98, 0.34), steel, bevel=0.1, segs=4)
box("Warnband", (0, FR - 0.035, 0.17), (HALF * 2, 0.02, 0.15), warn, bevel=0.0)
no_outline(box("Bodenlicht", (0, FR - 0.05, 0.02), (HALF * 2, 0.04, 0.035), glow, bevel=0.0))

edges = [-HALF] + PY + [HALF]
for i in range(len(edges) - 1):
    x0 = edges[i] + (0.42 if i > 0 else 0.0)
    x1 = edges[i + 1] - (0.42 if i < len(edges) - 2 else 0.0)
    w = x1 - x0
    cx = (x0 + x1) / 2
    box("Koerper%d" % i, (cx, -0.12, 0.72), (w + 0.1, 0.82, 0.8), steel, bevel=0.14, segs=5)
    box("Platte%d" % i, (cx, FR + 0.02, 0.7), (w - 0.16, 0.12, 0.6), armor, bevel=0.07, segs=4)
    # leuchtender Pfeil auf der Platte (nach oben)
    for sx in (-1, 1):
        o = no_outline(box("Pfeil%d_%d" % (i, sx), (cx + sx * 0.11, FR - 0.045, 0.68), (0.3, 0.02, 0.07), glow, bevel=0.0))
        o.rotation_euler = (0, sx * math.radians(-32), 0)
    box("Kappe%d" % i, (cx, -0.12, 1.16), (w + 0.16, 0.9, 0.18), armor, bevel=0.08, segs=4)
    no_outline(box("Kappenlicht%d" % i, (cx, FR + 0.04, 1.1), (w * 0.8, 0.02, 0.04), glow, bevel=0.0))
    for sx in (-1, 1):
        sphere("Niete%d_%d" % (i, sx), (cx + sx * (w / 2 - 0.2), FR - 0.04, 0.9), 0.045, gold)
        sphere("NieteU%d_%d" % (i, sx), (cx + sx * (w / 2 - 0.2), FR - 0.04, 0.5), 0.045, gold)

for i, x in enumerate(PY):
    cyl("Turm%d" % i, (x, -0.15, 1.0), 0.42, 2.0, steel, verts=20, bevel=0.1)
    cyl("Mantel%d" % i, (x, -0.15, 0.62), 0.47, 0.8, armor, verts=20, bevel=0.08)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.45, minor_radius=0.07, location=(x, -0.15, 1.3))
    t = bpy.context.active_object
    t.data.materials.append(gold)
    bpy.ops.object.shade_smooth()
    no_outline(cyl("Glimm%d" % i, (x, -0.15, 1.62), 0.43, 0.06, glow, verts=20))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.36, location=(x, -0.15, 2.0))
    dome = bpy.context.active_object
    dome.scale = (1, 1, 0.55)
    dome.data.materials.append(dark)
    bpy.ops.object.shade_smooth()
    no_outline(sphere("Kern%d" % i, (x, -0.15, 2.2), 0.15, glow))
    sphere("Warn%d" % i, (x, -0.66, 1.0), 0.06, lamp)

for a, b in zip(PY[:-1], PY[1:]):
    no_outline(cyl("Strahl%d" % int(a * 10), ((a + b) / 2, -0.15, 2.2), 0.04, (b - a) - 0.25, beam, rot=(0, 90, 0), verts=10))
for xe in (-HALF, HALF):
    a, b = (xe, PY[0]) if xe < 0 else (PY[-1], xe)
    no_outline(cyl("StrahlRand%d" % int(xe), ((a + b) / 2, -0.15, 2.2), 0.04, abs(b - a), beam, rot=(0, 90, 0), verts=10))

bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -0.08, 1.7))
sh = bpy.context.active_object
sh.scale = (HALF * 2, 1.0, 1)
sh.rotation_euler = (math.radians(90), 0, 0)
sh.data.materials.append(shield)
no_outline(sh)

light("SUN", "Sonne", (0, -5, 8), (52, 0, 22), 1.4, (1.0, 0.97, 0.94))
