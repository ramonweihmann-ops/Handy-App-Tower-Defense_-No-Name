#!/usr/bin/env python3
"""Brockens Rakete als 3D-Modell (game/models/fx/brocken_rakete.glb), gebaut nach dem freigegebenen Entwurf
(Vorlage_Raw/Schusseffekte_brocken_v2/, ChatGPT) und passend zum Meshy-Werfer (Vorlage_Raw/Waffen_Roh/brocken_waffe_v1/).

Form aus dem Entwurf (Bild 1 des Geschoss-Blatts, 256 px Kachel, Maße hier in Pixeln des 768er-Ausschnitts):
glänzend rotes, rundes Gehäuse, runde Spitze, zwei dunkle Metallringe, türkiser Leuchtstreifen mit kleinem orangem
Punkt, abgerundete rote Flossen hinten. Flamme und Rauch baut das Spiel selbst (Fx3D.build_rocket), damit sie flackern.

Achsen: Blender +Y = Flugrichtung (im Spiel −Z, wie look_at), +Z = oben. Länge 0,91, Durchmesser 0,22 (Weltmaß vor
Fx3D.ROCKET_SCALE). Aufruf: python3 tools/effekte/build_rakete.py [ausgabe.glb]
"""
import math, os, sys
import bpy, bmesh

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'game', 'models', 'fx', 'brocken_rakete.glb')

PX = 0.002          # Meter je Entwurfspixel (Durchmesser 110 px = 0,22 m)
CX = 482.0          # Mitte der Rakete im Entwurf (Heck 255, Spitze 710)
SEG = 24            # Unterteilung rundherum (viele Raketen gleichzeitig auf dem Handy)


def ax(x):
    return (x - CX) * PX


def mat(name, rgb, rough, metal=0.0, emit=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1.0)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1.0)
        b.inputs['Emission Strength'].default_value = strength
    return m


def lathe(name, profile, mats_by_x):
    """Drehkörper aus Profilpunkten (x im Entwurf, Radius in px); Material je Abschnitt nach der x-Mitte."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rings = []
    for x, r in profile:
        ring = []
        for i in range(SEG):
            a = 2 * math.pi * i / SEG
            ring.append(bm.verts.new((math.cos(a) * r * PX, ax(x), math.sin(a) * r * PX)))
        rings.append(ring)
    for k in range(len(rings) - 1):
        xm = (profile[k][0] + profile[k + 1][0]) * 0.5
        mi = 0
        for idx, (x0, x1) in enumerate(mats_by_x):
            if x0 <= xm <= x1:
                mi = idx + 1
        for i in range(SEG):
            j = (i + 1) % SEG
            f = bm.faces.new((rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i]))
            f.material_index = mi
            f.smooth = True
    # Deckel hinten (Düse sitzt davor) und Spitze schließen
    for ring, rev in ((rings[0], True), (rings[-1], False)):
        if ring[0].co.x ** 2 + ring[0].co.z ** 2 > 1e-8:
            f = bm.faces.new(list(reversed(ring)) if rev else ring)
            f.smooth = True
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def rounded_fin(name, m):
    """Flosse im Entwurf: an der Wurzel x 255–345, nach außen 45 px, nach hinten gepfeilt, Ecken rund."""
    pts = [(345, 52), (318, 82), (282, 100), (262, 102), (246, 94), (250, 70), (258, 52)]
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    vs = [bm.verts.new((0.0, ax(x), r * PX)) for x, r in pts]
    bm.faces.new(vs)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(m)
    sol = ob.modifiers.new('dicke', 'SOLIDIFY')
    sol.thickness = 0.042
    sol.offset = 0.0
    bev = ob.modifiers.new('rund', 'BEVEL')
    bev.width = 0.016
    bev.segments = 3
    bev.limit_method = 'NONE'
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def capsule_strip(name, m, x0, x1, h, angle):
    """Leuchtstreifen (abgerundeter Stab) auf der Gehäuseoberfläche, angle = Lage rundherum."""
    length = (x1 - x0) * PX
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=h * PX * 0.5, depth=length)
    ob = bpy.context.active_object
    ob.name = name
    ob.rotation_euler = (math.pi / 2, 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    bev = ob.modifiers.new('rund', 'BEVEL')
    bev.width = h * PX * 0.45
    bev.segments = 3
    rr = 55 * PX + 0.002
    ob.location = (math.cos(angle) * rr, ax((x0 + x1) * 0.5), math.sin(angle) * rr)
    ob.data.materials.append(m)
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # Farben linear (glTF): kräftiges Rot wie im Entwurf, helle Metallringe wie am Werfer, türkiser Streifen
    red = mat('Gehaeuse', (0.62, 0.012, 0.01), 0.3)
    band = mat('Ring', (0.30, 0.30, 0.34), 0.35, 0.55)
    glow = mat('Leuchtstreifen', (0.0, 0.75, 0.8), 0.3, 0.0, (0.0, 0.85, 0.9), 1.2)
    dot = mat('Lampe', (1.0, 0.35, 0.02), 0.3, 0.0, (1.0, 0.35, 0.02), 1.2)
    dark = mat('Duese', (0.12, 0.12, 0.14), 0.5, 0.4)

    # Profil aus dem Entwurf: rundes Heck, zwei leicht abstehende Ringe, elliptische Spitze
    prof = [(255, 30), (258, 38), (264, 45), (274, 50), (290, 54), (310, 55),
            (333, 55), (335, 58), (385, 58), (387, 55),
            (578, 55), (580, 58), (625, 58), (627, 55)]
    for k in range(1, 10):
        th = math.pi / 2 * k / 10.0
        prof.append((627 + 83 * math.sin(th), 55 * math.cos(th)))
    prof.append((710, 0.0))
    body = lathe('Rakete', prof, [(334, 386), (579, 626)])
    for m in (red, band):
        body.data.materials.append(m)
    # Materialindex 0 = rot, 1 und 2 = Ringe → Ringe auf Index 1 legen
    for p in body.data.polygons:
        if p.material_index == 2:
            p.material_index = 1

    # Düse am Heck
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=22 * PX, depth=12 * PX)
    noz = bpy.context.active_object
    noz.name = 'Duese'
    noz.rotation_euler = (math.pi / 2, 0, 0)
    noz.location = (0, ax(252), 0)
    noz.data.materials.append(dark)

    # vier Flossen über Kreuz (45°), wie beim bisherigen Modell
    for k in range(4):
        f = rounded_fin('Flosse%d' % k, red)
        f.rotation_euler = (0, math.pi / 4 + k * math.pi / 2, 0)

    # Leuchtstreifen links und rechts, kleiner oranger Punkt davor (Entwurf: x 410–555, 14 px hoch, Punkt bei 570)
    for k, a in enumerate((0.0, math.pi)):
        capsule_strip('Streifen%d' % k, glow, 410, 555, 14, a)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=6, radius=4.5 * PX)
        d = bpy.context.active_object
        d.name = 'Punkt%d' % k
        rr = 55 * PX + 0.003
        d.location = (math.cos(a) * rr, ax(570), math.sin(a) * rr)
        d.data.materials.append(dot)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_apply=True, export_yup=True)
    tris = 0
    dg = bpy.context.evaluated_depsgraph_get()
    for ob in bpy.context.scene.objects:
        if ob.type == 'MESH':
            e = ob.evaluated_get(dg).to_mesh()
            tris += sum(len(p.vertices) - 2 for p in e.polygons)
    print('Rakete gebaut: %s (%d Dreiecke)' % (OUT, tris))


if __name__ == '__main__':
    main()
