# Lava-Asteroid, Detailstufe 2 (zweite Fassung nach Kommentar „zu knuffig“): wie die Brücke gebaut – große Steinplatten
# mit abgeschrägten Ecken in dunklen Metallrahmen, glühende Fugen dazwischen, Risse mit Glut, dicke Neonröhren in
# Metallrinnen, Pfeiler als Metallhalter mit waagerechtem Glutbalken (wie an der Brücke), scharfe statt runde Kanten
import bmesh as _bm
stone = rich("Stein", (0.2, 0.17, 0.165), metal=0.0, rough=0.8, dirt=(0.02, 0.012, 0.01), var=0.45, grad=0.25, bump=1.0,
             cracks=(0.9, 0.18, 0.01), crack_emit=1.8, crack_width=0.008, crack_mask=0.58)
metal = rich("Metall", (0.13, 0.12, 0.12), metal=0.85, rough=0.42, dirt=(0.02, 0.015, 0.015), scratches=0.25, bump=0.15)
metal2 = rich("Metall2", (0.2, 0.18, 0.17), metal=0.85, rough=0.38, dirt=(0.03, 0.02, 0.02), scratches=0.3, bump=0.1)
lava = glowm("Glut", (1.0, 0.26, 0.01), 2.5)
neon = glowm("Neon", (1.0, 0.36, 0.04), 6.0)

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
box("Glutrinne", (0, FR - 0.125, 0.12), (HALF * 2, 0.02, 0.04), lava, bevel=0.0)

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
    cyl("Neon%d" % i, (cx, FR - 0.11, 1.075), 0.03, w - 0.04, neon, rot=(0, 90, 0), verts=12)
    # Deckplatten oben
    octo_top("Deck%d" % i, cx, -0.12, w - 0.05, 0.75, 0.08, 1.12, 1.15, stone)
    box("DeckRahmen%d" % i, (cx, -0.12, 1.1), (w, 0.86, 0.04), metal2, bevel=0.006)
    plight((cx, FR - 0.35, 1.0), (1.0, 0.35, 0.05), 5.0)

for i, x in enumerate(MODS):
    # Metallhalter wie an der Brücke
    box("Halter%d" % i, (x, -0.13, 0.85), (0.8, 0.96, 1.1), metal, bevel=0.015)
    box("HFront%d" % i, (x, FR - 0.05, 0.85), (0.72, 0.06, 1.0), metal2, bevel=0.01)
    octo("HStein%d" % i, x, 0.6, 0.56, 0.36, 0.07, FR - 0.09, FR - 0.05, stone)
    octo("HStein2_%d" % i, x, 1.12, 0.56, 0.36, 0.07, FR - 0.09, FR - 0.05, stone)
    # waagerechter Glutbalken in Fassung
    box("BFassung%d" % i, (x, FR - 0.1, 0.86), (0.6, 0.06, 0.13), metal, bevel=0.01)
    box("Balken%d" % i, (x, FR - 0.13, 0.86), (0.46, 0.02, 0.055), neon, bevel=0.0)
    for sx in (-1, 1):
        cyl("Bolzen", (x + sx * 0.27, FR - 0.135, 0.86), 0.02, 0.02, metal2, rot=(90, 0, 0), verts=8)
        cyl("SNeon%d_%d" % (i, sx), (x + sx * 0.37, FR - 0.07, 0.85), 0.022, 1.0, neon, verts=10)
    plight((x, FR - 0.4, 0.86), (1.0, 0.38, 0.05), 6.0)
    box("Kappe%d" % i, (x, -0.13, 1.44), (0.88, 1.02, 0.08), metal2, bevel=0.012)
    octo_top("KStein%d" % i, x, -0.13, 0.64, 0.8, 0.08, 1.48, 1.51, stone)

world.node_tree.nodes["Background"].inputs[0].default_value = (0.07, 0.06, 0.08, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.5
light('SUN', "Sonne", (0, -5, 8), (55, 0, -40), 2.3, (0.9, 0.88, 0.95))
light('AREA', "Rand", (0, 3.0, 3.5), (-60, 0, 0), 220, (1.0, 0.38, 0.08), size=12)
glare(threshold=1.0, size=7)
