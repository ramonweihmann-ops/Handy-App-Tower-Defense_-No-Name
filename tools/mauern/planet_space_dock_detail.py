# Raumstation, Detailstufe 2: gerahmte Panzerfelder mit Rippen, Gesims mit Neonrinne und Schellen, Kabelstrang am Sockel,
# Pfeiler mit Fuß und Kapitell, Lüftung, Lampengehäuse, Anzeige und Schildsender; farbiges Licht von Lampen und Neon
CY = (0.15, 0.65, 1.0)
steelL = rich("Hellstahl", (0.5, 0.55, 0.74), metal=0.75, rough=0.3, scratches=0.35, dirt=(0.03, 0.04, 0.08))
steelD = rich("Deckstahl", (0.14, 0.22, 0.44), metal=0.7, rough=0.38, scratches=0.2)
steelM = rich("Mittelstahl", (0.3, 0.36, 0.56), metal=0.75, rough=0.34, scratches=0.25)
dark = rich("Dunkel", (0.02, 0.025, 0.04), metal=0.5, rough=0.5, ao_strength=0.3, var=0.05, grad=0.1, bump=0.05)
neon = glowm("Neon", CY, 5.0)
lampm = glowm("Lampe", (1.0, 0.5, 0.12), 7.0)
screen = glowm("Anzeige", (0.2, 0.9, 1.0), 2.5)
warn = stripes("Warn", (0.95, 0.68, 0.1), (0.04, 0.04, 0.05), scale=12.0)

# Sockel mit Fase, Rinne und Kabelstrang
prism("Sockel", -HALF, HALF, [(FR - 0.1, 0.0), (0.35, 0.0), (0.35, 0.3), (FR + 0.02, 0.3), (FR - 0.1, 0.2)], steelD, bevel=0.02)
cyl("Kabel1", (0, FR - 0.17, 0.07), 0.04, HALF * 2, dark, rot=(0, 90, 0), verts=12)
cyl("Kabel2", (0, FR - 0.16, 0.15), 0.028, HALF * 2, steelM, rot=(0, 90, 0), verts=12)
for k in range(22):
    box("Schelle%d" % k, (-6.3 + k * 0.6, FR - 0.16, 0.11), (0.07, 0.12, 0.2), steelL, bevel=0.012)

for i, (x0, x1) in enumerate(segments()):
    w = x1 - x0
    cx = (x0 + x1) / 2
    box("Wand%d" % i, (cx, -0.13, 0.66), (w, 0.86, 0.76), steelD, bevel=0.03)
    # Rahmen
    box("RO%d" % i, (cx, FR - 0.03, 0.97), (w - 0.02, 0.08, 0.07), steelM, bevel=0.015)
    box("RU%d" % i, (cx, FR - 0.03, 0.37), (w - 0.02, 0.08, 0.07), steelM, bevel=0.015)
    for sx in (-1, 1):
        box("RS%d_%d" % (i, sx), (cx + sx * (w / 2 - 0.05), FR - 0.03, 0.67), (0.08, 0.08, 0.6), steelM, bevel=0.015)
    # vertieftes Feld mit zwei Rippen und Bolzen
    box("Feld%d" % i, (cx, FR + 0.01, 0.67), (w - 0.16, 0.04, 0.53), dark, bevel=0.005)
    for k in (-1, 1):
        rx = cx + k * w * 0.2
        box("Rippe%d_%d" % (i, k), (rx, FR - 0.02, 0.67), (0.1, 0.06, 0.5), steelL, bevel=0.015)
        for z in (0.47, 0.87):
            cyl("Bolzen", (rx, FR - 0.055, z), 0.022, 0.02, dark, rot=(90, 0, 0), verts=10)
    box("Warnschild%d" % i, (cx, FR - 0.005, 0.5), (0.26, 0.02, 0.08), warn, bevel=0.0)
    cyl("Status%d" % i, (cx, FR - 0.01, 0.82), 0.03, 0.02, screen, rot=(90, 0, 0), verts=12)
    # Gesims mit Neonrinne und Schellen
    box("Gesims1_%d" % i, (cx, -0.13, 1.08), (w + 0.04, 0.92, 0.1), steelM, bevel=0.02)
    box("Gesims2_%d" % i, (cx, -0.15, 1.16), (w + 0.1, 1.0, 0.07), steelL, bevel=0.02)
    box("Rinne%d" % i, (cx, FR - 0.07, 1.08), (w - 0.05, 0.04, 0.05), dark, bevel=0.005)
    cyl("Neon%d" % i, (cx, FR - 0.085, 1.08), 0.02, w - 0.1, neon, rot=(0, 90, 0), verts=10)
    for k in range(int(w / 0.35)):
        box("Klammer", (x0 + 0.2 + k * 0.35, FR - 0.09, 1.08), (0.03, 0.03, 0.07), steelL, bevel=0.005)
    plight((cx, FR - 0.35, 1.0), CY, 8.0)
    # Deck oben: Platten mit Fugen und Schrauben
    box("Deck%d" % i, (cx, -0.15, 1.2), (w - 0.1, 0.8, 0.015), steelD, bevel=0.004)
    box("DeckFuge%d" % i, (cx, -0.15, 1.21), (0.02, 0.8, 0.01), dark, bevel=0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl("S", (cx + sx * (w / 2 - 0.12), -0.15 + sy * 0.32, 1.21), 0.025, 0.012, steelL, verts=10)

for i, x in enumerate(MODS):
    cham("Fuss%d" % i, (x, -0.13, 0.39), (0.96, 1.02, 0.18), steelM, ch=0.04)
    cham("Schaft%d" % i, (x, -0.13, 0.92), (0.76, 0.92, 0.9), steelL, ch=0.07)
    cham("Kapitell%d" % i, (x, -0.13, 1.42), (0.9, 1.04, 0.12), steelM, ch=0.035)
    cham("Kappe%d" % i, (x, -0.13, 1.51), (0.7, 0.84, 0.06), steelD, ch=0.02)
    # Lüftung mit Rahmen
    box("LRahmen%d" % i, (x, FR - 0.07, 1.12), (0.46, 0.04, 0.26), steelM, bevel=0.01)
    box("LGrund%d" % i, (x, FR - 0.085, 1.12), (0.4, 0.02, 0.2), dark, bevel=0.0)
    for k in range(5):
        box("Lamelle", (x, FR - 0.1, 1.04 + k * 0.04), (0.38, 0.02, 0.018), steelL, bevel=0.003)
    # Lampengehäuse mit Licht
    box("Gehaeuse%d" % i, (x, FR - 0.12, 0.72), (0.22, 0.14, 0.3), steelD, bevel=0.02)
    box("Linse%d" % i, (x, FR - 0.19, 0.72), (0.12, 0.02, 0.2), lampm, bevel=0.0)
    plight((x, FR - 0.45, 0.72), (1.0, 0.5, 0.15), 6.0)
    box("Anzeige%d" % i, (x, FR - 0.07, 0.94), (0.18, 0.02, 0.06), screen, bevel=0.0)
    # Neonkanten in Rillen
    for sx in (-1, 1):
        box("Rille%d_%d" % (i, sx), (x + sx * 0.3, FR - 0.075, 0.92), (0.05, 0.02, 0.8), dark, bevel=0.0)
        cyl("KNeon%d_%d" % (i, sx), (x + sx * 0.3, FR - 0.09, 0.92), 0.015, 0.76, neon, verts=8)
    # Schildsender oben
    cyl("Sockelchen%d" % i, (x, -0.13, 1.6), 0.18, 0.12, dark, verts=20, bevel=0.01)
    cyl("Ring%d" % i, (x, -0.13, 1.68), 0.15, 0.04, steelL, verts=20, bevel=0.008)
    sphere("Kern%d" % i, (x, -0.13, 1.74), 0.1, neon)
    cyl("Antenne%d" % i, (x + 0.24, -0.05, 1.72), 0.012, 0.3, steelL, verts=8)
    plight((x, -0.4, 1.85), CY, 12.0)

world.node_tree.nodes["Background"].inputs[0].default_value = (0.04, 0.08, 0.22, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.8
light('SUN', "Sonne", (0, -5, 8), (55, 0, -40), 2.6, (0.92, 0.94, 1.0))
light('AREA', "Rand", (0, 3.0, 3.5), (-60, 0, 0), 320, CY, size=12)
glare(threshold=1.0, size=7)
