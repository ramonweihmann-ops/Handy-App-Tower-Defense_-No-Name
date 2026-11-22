# Wüstenaußenposten, Zusatz (Kommentar 22.11.: zu wenig Details und Tiefe): abgesetzte Innenfelder mit
# Nieten auf allen Platten und Deckeln, Nietreihen, senkrechte Bernsteinlampen in Fassungen wie an der Brücke,
# Sandverwehungen auf den Deckeln, Schmutzflecken und Staub (planet_desert_outpost_form.py).
sand = plate("Sand", (0.92, 0.75, 0.5), rough=0.95, bump=0.9, var=0.5)
amber = pm("Bernstein", (1.0, 0.7, 0.28), emit=(1.0, 0.6, 0.16), strength=4.5)
amber_light = glowm("BernsteinLicht", L_((1.0, 0.6, 0.2)), 10.0)
random.seed(23)

def rivet(loc, r=0.014):
    return sphere("Niete", loc, r, metal2)

for i, (x0, x1) in enumerate(segments()):
    w = x1 - x0
    cx = (x0 + x1) / 2
    pw = (w - 0.06) / 2
    for k in (-1, 1):
        px = cx + k * (pw / 2 + 0.012)
        # abgesetztes Innenfeld (Stufe gibt Kante und Schatten), Nieten in den Ecken
        octo("Innenfeld%d_%d" % (i, k), px, 0.67, pw - 0.13, 0.42, 0.06, FR - 0.068, FR - 0.035, stone)
        for sx in (-1, 1):
            rivet((px + sx * (pw / 2 - 0.05), FR - 0.045, 0.67 - 0.25))
            rivet((px + sx * (pw / 2 - 0.05), FR - 0.045, 0.67 + 0.25))
    # Nietreihe auf dem unteren Rahmen
    x = x0 + 0.08
    while x < x1 - 0.05:
        rivet((x, FR - 0.092, 0.32), 0.012)
        x += 0.16
    # Deckplatte: abgesetztes Innenfeld, Eck-Nieten, Sandverwehung hinten
    octo_top("DeckInnen%d" % i, cx, -0.1, w - 0.24, 0.44, 0.06, 1.18, 1.196, stone_top)
    for sx in (-1, 1):
        for sy in (-1, 1):
            rivet((cx + sx * (w / 2 - 0.07), -0.1 + sy * 0.26, 1.183), 0.015)
    d_ = sphere("SandDeck%d" % i, (cx + random.uniform(-0.2, 0.2), 0.1, 1.17), 0.16, sand)
    d_.scale = (1.8, 0.7, 0.16)

for j, x in enumerate(MODS):
    # Erhöhung: Innenfeld oben, Nieten an der Kappe
    octo_top("KInnen%d" % j, x, -0.13, 0.46, 0.6, 0.06, 1.51, 1.526, stone_top)
    for sx in (-1, 1):
        for sy in (-1, 1):
            rivet((x + sx * 0.39, -0.13 + sy * 0.46, 1.485), 0.016)
    s_ = sphere("SandKappe%d" % j, (x + random.uniform(-0.12, 0.12), 0.08, 1.51), 0.12, sand)
    s_.scale = (1.5, 0.8, 0.18)
    # Pfeilerfront: Nieten in den Ecken, senkrechte Bernsteinlampen neben dem oberen Stein
    for sx in (-1, 1):
        for z in (0.4, 1.3):
            rivet((x + sx * 0.32, FR - 0.085, z), 0.016)
        lx = x + sx * 0.305
        box("LGehaeuse%d_%d" % (j, sx), (lx, FR - 0.1, 1.14), (0.085, 0.06, 0.3), metal, bevel=0.012)
        see_through(box("LGlas%d_%d" % (j, sx), (lx, FR - 0.13, 1.14), (0.045, 0.02, 0.22), amber, bevel=0.004))
        for dz in (-0.15, 0.15):
            box("LKlammer%d_%d" % (j, sx), (lx, FR - 0.115, 1.14 + dz), (0.11, 0.07, 0.035), metal2, bevel=0.006)
        light_only(sphere("LLicht%d_%d" % (j, sx), (lx, FR - 0.3, 1.14), 0.03, amber_light), amber_light)
