# Wolkenstadt, Detailstufe 2: Marmor-Balustrade wie das Geländer der Brücke: Postamente mit Gesimsen, Goldbändern,
# Goldkugeln und blauen Edelsteinen; dazwischen gedrechselte Baluster zwischen Sockel- und Handlauf mit Goldeinlage
marble = rich("Marmor", (0.86, 0.84, 0.8), metal=0.0, rough=0.22, dirt=(0.42, 0.44, 0.52), ao_strength=0.75, var=0.08,
              grad=0.18, veins=(0.74, 0.72, 0.7), bump=0.03)
gold = rich("Gold", (1.0, 0.72, 0.3), metal=1.0, rough=0.22, dirt=(0.35, 0.2, 0.04), var=0.1, grad=0.12, bump=0.02)
slate = rich("Schiefer", (0.28, 0.34, 0.44), metal=0.3, rough=0.5, dirt=(0.05, 0.06, 0.09))
gem = glowm("Edelstein", (0.3, 0.68, 1.0), 3.5)

prism("Sockel", -HALF, HALF, [(FR - 0.1, 0.0), (0.35, 0.0), (0.35, 0.22), (FR - 0.1, 0.22)], slate, bevel=0.02)
prism("Stufe", -HALF, HALF, [(FR - 0.04, 0.22), (0.3, 0.22), (0.3, 0.33), (FR, 0.33), (FR - 0.04, 0.29)], marble, bevel=0.015)
box("GoldStufe", (0, FR - 0.045, 0.255), (HALF * 2, 0.012, 0.025), gold, bevel=0.0)

for i, (x0, x1) in enumerate(segments()):
    w = x1 - x0
    cx = (x0 + x1) / 2
    box("Rueckwand%d" % i, (cx, 0.0, 0.72), (w, 0.3, 0.7), marble, bevel=0.02)
    box("Fussleiste%d" % i, (cx, -0.25, 0.39), (w, 0.6, 0.12), marble, bevel=0.025)
    box("Handlauf%d" % i, (cx, -0.25, 1.02), (w, 0.62, 0.1), marble, bevel=0.025)
    cyl("Rundung%d" % i, (cx, -0.25, 1.08), 0.07, w, marble, rot=(0, 90, 0), verts=20)
    box("GoldLinie%d" % i, (cx, FR + 0.04, 1.0), (w - 0.02, 0.012, 0.022), gold, bevel=0.0)
    n = max(3, int(w / 0.19))
    for k in range(n):
        bx = x0 + (k + 0.5) * w / n
        by = -0.3
        box("BFuss", (bx, by, 0.48), (0.11, 0.11, 0.06), marble, bevel=0.012)
        b = sphere("Bauch", (bx, by, 0.62), 0.07, marble)
        b.scale = (1, 1, 1.55)
        cyl("Hals", (bx, by, 0.76), 0.03, 0.1, marble, verts=14)
        cyl("Ring", (bx, by, 0.8), 0.05, 0.035, marble, verts=14, bevel=0.008)
        cyl("Oben", (bx, by, 0.88), 0.04, 0.12, marble, verts=14)
        box("BKopf", (bx, by, 0.95), (0.1, 0.1, 0.04), marble, bevel=0.01)

for i, x in enumerate(MODS):
    cham("Basis%d" % i, (x, -0.15, 0.4), (0.92, 1.0, 0.14), marble, ch=0.035)
    cham("Postament%d" % i, (x, -0.15, 0.84), (0.7, 0.86, 0.74), marble, ch=0.03)
    # vertieftes Feld mit Goldrahmen und Edelstein
    box("Nische%d" % i, (x, FR - 0.005, 0.84), (0.34, 0.03, 0.5), slate, bevel=0.01)
    for sx in (-1, 1):
        box("GR%d_%d" % (i, sx), (x + sx * 0.18, FR - 0.025, 0.84), (0.025, 0.02, 0.54), gold, bevel=0.004)
    for sz in (-1, 1):
        box("GRQ%d_%d" % (i, sz), (x, FR - 0.025, 0.84 + sz * 0.26), (0.385, 0.02, 0.025), gold, bevel=0.004)
    e = sphere("Stein%d" % i, (x, FR - 0.04, 0.84), 0.06, gem)
    e.scale = (1, 0.6, 2.6)
    plight((x, FR - 0.35, 0.84), (0.35, 0.7, 1.0), 6.0)
    # Gesims mit Goldband
    cham("Gesims1_%d" % i, (x, -0.15, 1.25), (0.82, 0.96, 0.08), marble, ch=0.02)
    box("Goldband%d" % i, (x, -0.15, 1.31), (0.84, 0.98, 0.035), gold, bevel=0.006)
    cham("Gesims2_%d" % i, (x, -0.15, 1.37), (0.76, 0.9, 0.08), marble, ch=0.02)
    cyl("KSockel%d" % i, (x, -0.15, 1.45), 0.1, 0.07, gold, verts=20, bevel=0.01)
    sphere("Kugel%d" % i, (x, -0.15, 1.6), 0.13, gold)

world.node_tree.nodes["Background"].inputs[0].default_value = (0.45, 0.6, 0.85, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.1
light("SUN", "Sonne", (0, -5, 8), (52, 0, -35), 3.0, (1.0, 0.95, 0.86))
light('AREA', "Rand", (0, 3.0, 3.5), (-60, 0, 0), 150, (0.6, 0.8, 1.0), size=12)
glare(threshold=1.0, size=6)
