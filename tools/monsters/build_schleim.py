"""Baut aus einem statischen Meshy-Schleim (Schleimling, Schleimmutter; Vorlage_Raw/Monster_Roh/Modelltests_v3)
die Spiel-GLB mit kleinem eigenem Skelett und zwei Bewegungen.
Aufruf: python3 build_schleim.py <id>_statisch_roh.glb <ausgabe.glb> [dreiecke] [schwere]   (benötigt: pip install bpy)
schwere 1 = flink (Schleimling), größer = träger und tiefer gestaucht (Schleimmutter, z. B. 1.6)

- auf die Dreieckszahl verkleinern, Textur 1024, Ursprung mittig am Boden, Blick +Z (glTF)
- Knochen: Root (Boden) → Body (unterer Körper, staucht und streckt) → Top (oberer Körper mit Gesicht)
  Gewichte nach Höhe, weich verlaufend; der Körper verformt sich wie Gummi, behält aber sein Volumen
- Walk (Hüpfen, Schleife): ducken – abspringen (strecken) – fliegen – landen (stauchen); Oberteil schwingt nach
- Attack (Zuschnappen, Schleife): zurücklehnen und ducken – nach vorn schnellen (Oberteil beißt nach vorn unten)
  – zurückfedern
"""
import bpy, sys, math
from mathutils import Vector, Quaternion

args = [a for a in sys.argv[1:] if not a.startswith('-')]
src, out = args[0], args[1]
target = int(args[2]) if len(args) > 2 else 3000
heavy = float(args[3]) if len(args) > 3 else 1.0

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
scene = bpy.context.scene
meshes = [o for o in scene.objects if o.type == 'MESH']
body = meshes[0]
body.name = "Schleim"
for o in scene.objects:
    if o not in meshes:
        o.select_set(False)
# Elternteile auflösen, Transformation übernehmen
bpy.context.view_layer.objects.active = body
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in list(scene.objects):
    if o != body:
        bpy.data.objects.remove(o, do_unlink=True)

tris = sum(len(p.vertices) - 2 for p in body.data.polygons)
dec = body.modifiers.new("Verkleinern", 'DECIMATE')
dec.ratio = min(1.0, target / tris)
dec.use_collapse_triangulate = True
bpy.ops.object.modifier_apply(modifier=dec.name)
print("DREIECKE", tris, "->", sum(len(p.vertices) - 2 for p in body.data.polygons))
for img in bpy.data.images:
    if img.size[0] > 1024:
        img.scale(1024, 1024)
        img.pack()

# Ursprung mittig am Boden
vs = body.data.vertices
xs = [v.co.x for v in vs]; ys = [v.co.y for v in vs]; zs = [v.co.z for v in vs]
off = Vector(((min(xs) + max(xs)) * 0.5, (min(ys) + max(ys)) * 0.5, min(zs)))
for v in vs:
    v.co -= off
H = max(zs) - min(zs)
print("GROESSE", round(max(xs) - min(xs), 3), round(max(ys) - min(ys), 3), round(H, 3))

# --- Skelett -------------------------------------------------------------------------------------
arm_data = bpy.data.armatures.new("Armature")
arm = bpy.data.objects.new("Armature", arm_data)
scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
eb = arm_data.edit_bones
root = eb.new("Root"); root.head = (0, 0, 0); root.tail = (0, 0, 0.15 * H)
b = eb.new("Body"); b.head = (0, 0, 0); b.tail = (0, 0, 0.5 * H); b.parent = root
t = eb.new("Top"); t.head = (0, 0, 0.42 * H); t.tail = (0, 0, H); t.parent = b
bpy.ops.object.mode_set(mode='OBJECT')

vg_b = body.vertex_groups.new(name="Body")
vg_t = body.vertex_groups.new(name="Top")
for v in vs:
    x = min(1.0, max(0.0, (v.co.z / H - 0.28) / 0.42))
    w = x * x * (3 - 2 * x)
    vg_b.add([v.index], 1.0 - w, 'REPLACE')
    if w > 0:
        vg_t.add([v.index], w, 'REPLACE')
body.parent = arm
mod = body.modifiers.new("Armature", 'ARMATURE')
mod.object = arm

pose = arm.pose
scene.render.fps = 30
arm.animation_data_create()


def set_pose(squash=1.0, lift=0.0, fwd=0.0, top_pitch=0.0, top_squash=1.0):
    """squash: Höhe des Körpers (1 = Ruhe), Breite gleicht aus (Volumen bleibt);
    lift: Anheben in Körperhöhen; fwd: nach vorn (−Y in Blender = Blickrichtung) in Körperhöhen;
    top_pitch: Oberteil nach vorn (+) bzw. hinten (−) neigen, Grad"""
    for pb in pose.bones:
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Quaternion()
        pb.location = (0, 0, 0)
        pb.scale = (1, 1, 1)
    # Root-Knochen zeigt nach +Z: lokale Y-Achse = Welt-Z, lokale Z-Achse = Welt-−Y
    pose.bones["Root"].location = (0, lift * H, fwd * H)
    side = 1.0 / math.sqrt(squash)
    pose.bones["Body"].scale = (side, squash, side)
    tside = 1.0 / math.sqrt(top_squash)
    pose.bones["Top"].scale = (tside, top_squash, tside)
    # Neigen um die Welt-X-Achse: nach vorn = Oberteil zur −Y-Seite
    pose.bones["Top"].rotation_quaternion = Quaternion((1, 0, 0), math.radians(top_pitch))
    bpy.context.view_layer.update()


def make(name, length_frames, keys):
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    arm.animation_data.action = act
    for u, kw in keys:
        set_pose(**kw)
        f = round(u * length_frames)
        for pb in pose.bones:
            pb.keyframe_insert("rotation_quaternion", frame=f)
            pb.keyframe_insert("location", frame=f)
            pb.keyframe_insert("scale", frame=f)


# Schwere: tiefer stauchen, niedriger springen, langsamer
dq = 0.18 * min(1.4, heavy)       # Stauchen
hop = 0.32 / heavy                 # Sprunghöhe
walk_len = round(24 * heavy ** 0.5)
make("Walk", walk_len, [
    (0.00, dict(squash=1 - dq, top_pitch=2)),
    (0.14, dict(squash=1 + dq * 0.65, lift=0.02, top_pitch=-4)),
    (0.30, dict(squash=1 + dq * 0.25, lift=hop * 0.8, top_pitch=-2)),
    (0.45, dict(squash=1.0, lift=hop, top_pitch=2)),
    (0.62, dict(squash=1 + dq * 0.2, lift=hop * 0.55, top_pitch=4)),
    (0.78, dict(squash=1.0, lift=0.0, top_pitch=3)),
    (0.88, dict(squash=1 - dq * 1.1, top_pitch=-3, top_squash=0.96)),
    (1.00, dict(squash=1 - dq, top_pitch=2)),
])
att_len = round(27 * heavy ** 0.5)
make("Attack", att_len, [
    (0.00, dict(squash=1.0)),
    (0.30, dict(squash=1 - dq * 0.8, fwd=-0.06, top_pitch=-20)),
    (0.42, dict(squash=1 - dq, fwd=-0.08, top_pitch=-24)),
    (0.52, dict(squash=1 + dq * 0.7, fwd=0.16, top_pitch=30, top_squash=1.05)),
    (0.62, dict(squash=1 + dq * 0.4, fwd=0.14, top_pitch=24)),
    (0.80, dict(squash=1 - dq * 0.35, fwd=0.03, top_pitch=-4)),
    (1.00, dict(squash=1.0)),
])
arm.animation_data.action = None
set_pose()
print("BEWEGUNGEN", sorted(a.name for a in bpy.data.actions), "Längen", walk_len, att_len)
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS',
                          export_yup=True, export_apply=False, export_force_sampling=True)
print("FERTIG", out)
