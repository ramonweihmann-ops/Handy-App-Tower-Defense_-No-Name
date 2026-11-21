# Lava-Asteroid, Detailstufe 2: Mauerwerk aus Basaltquadern (zwei Reihen, unregelmäßig), glühende Lava in den Fugen,
# schwere Deckquader, Pfeiler mit rostigen Eisenbändern und Nieten, Glutschalen oben; Glutlicht auf dem Stein
random.seed(5)
basalt = rich("Basalt", (0.1, 0.085, 0.085), metal=0.0, rough=0.85, dirt=(0.01, 0.008, 0.008), var=0.3, grad=0.3, bump=0.5,
              cracks=(1.0, 0.28, 0.02), crack_emit=2.5, crack_width=0.01, crack_mask=0.62)
basalt2 = rich("Basalt2", (0.13, 0.11, 0.105), metal=0.0, rough=0.8, dirt=(0.03, 0.02, 0.02), var=0.3, grad=0.25, bump=0.45)
iron = rich("Eisen", (0.26, 0.22, 0.2), metal=0.8, rough=0.55, dirt=(0.25, 0.08, 0.02), scratches=0.15, bump=0.2)
lava = glowm("Lava", (1.0, 0.3, 0.02), 3.5)
ember = glowm("Glut", (1.0, 0.38, 0.04), 2.5)

prism("Sockel", -HALF, HALF, [(FR - 0.12, 0.0), (0.35, 0.0), (0.35, 0.28), (FR - 0.06, 0.28), (FR - 0.12, 0.2)], basalt2, bevel=0.03)
box("LavaRinne", (0, FR - 0.125, 0.1), (HALF * 2, 0.02, 0.05), lava, bevel=0.0)
for k in range(8):
    plight((-5.6 + k * 1.6, FR - 0.35, 0.15), (1.0, 0.35, 0.05), 3.0)

for i, (x0, x1) in enumerate(segments()):
    w = x1 - x0
    cx = (x0 + x1) / 2
    # glühende Fläche hinter den Quadern (scheint durch die Fugen)
    box("LavaGrund%d" % i, (cx, FR + 0.12, 0.66), (w, 0.02, 0.72), lava, bevel=0.0)
    box("Kern%d" % i, (cx, -0.05, 0.66), (w, 0.6, 0.72), basalt2, bevel=0.02)
    for row, (z0, h) in enumerate(((0.3, 0.34), (0.66, 0.34))):
        x = x0 + (0.0 if row == 0 else 0.15)
        while x < x1 - 0.05:
            sw = min(random.uniform(0.32, 0.55), x1 - x)
            st = cham("Quader", (x + sw / 2, FR + 0.05 + random.uniform(-0.02, 0.02), z0 + h / 2),
                      (sw - 0.035, 0.2, h - 0.035), basalt, ch=0.04, segs=2)
            st.rotation_euler = (random.uniform(-0.03, 0.03), random.uniform(-0.04, 0.04), random.uniform(-0.02, 0.02))
            x += sw
    # Deckquader
    cham("Deck%d" % i, (cx, -0.12, 1.08), (w + 0.06, 0.98, 0.14), basalt2, ch=0.05, segs=2)

for i, x in enumerate(MODS):
    cham("Pfeiler%d" % i, (x, -0.13, 0.86), (0.84, 0.96, 1.12), basalt, ch=0.07, segs=2)
    for z in (0.55, 1.15):
        box("Band%d_%.1f" % (i, z), (x, -0.13, z), (0.88, 1.0, 0.09), iron, bevel=0.015)
        for k in range(4):
            sphere("Niete", (x - 0.33 + k * 0.22, FR - 0.075, z), 0.025, iron)
    cham("Kopf%d" % i, (x, -0.13, 1.47), (0.92, 1.04, 0.12), basalt2, ch=0.04)
    # Glutschale
    bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.12, radius2=0.26, depth=0.16, location=(x, -0.13, 1.61))
    sch = bpy.context.active_object; sch.data.materials.append(iron); bpy.ops.object.shade_smooth()
    g = sphere("Glut%d" % i, (x, -0.13, 1.68), 0.2, ember); g.scale = (1, 1, 0.35)
    plight((x, -0.3, 1.95), (1.0, 0.42, 0.06), 12.0, radius=0.15)

world.node_tree.nodes["Background"].inputs[0].default_value = (0.07, 0.06, 0.08, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.5
light('SUN', "Sonne", (0, -5, 8), (55, 0, -40), 1.8, (0.88, 0.88, 0.98))
light('AREA', "Rand", (0, 3.0, 3.5), (-60, 0, 0), 90, (1.0, 0.4, 0.1), size=12)
glare(threshold=1.0, size=7)
