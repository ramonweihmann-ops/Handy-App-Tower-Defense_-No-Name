"""Baut aus dem Meshy-Rohmodell des Zombies die Spiel-GLB (Vorlage_Raw/Monster_Roh/Modelltests_v1).
Aufruf: python3 build_zombie.py <zombie_rig_roh.glb> <ausgabe.glb> [dreiecke]   (benötigt: pip install bpy)

- Hilfsobjekt „Icosphere“ entfernen
- auf etwa 5.000 Dreiecke verkleinern (mittlerer Gegner, docs/MONSTER_EINBAU.md), Gewichte bleiben erhalten
- Textur auf 1024 × 1024
- Bewegungen umbenennen: Walking → Walk, Running → Run, Attack bleibt, Dead → Death.
  Hit_Reaction fällt weg (wandert 60 cm zur Seite; Treffer zeigt das Spiel durch Aufblitzen).
- Blick +Z (glTF), Füße auf dem Boden; die Größe im Kampf stellt das Spiel ein (models.gd „height“)
"""
import bpy, sys

args = [a for a in sys.argv if not a.startswith('-')]
src, out = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else args[-2], args[-1]
target = 5000
if len(args) >= 3 and args[-1].isdigit():
    target = int(args[-1]); src, out = args[-3], args[-2]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
scene = bpy.context.scene
for o in list(scene.objects):
    if o.name.startswith("Icosphere"):
        bpy.data.objects.remove(o, do_unlink=True)
arm = [o for o in scene.objects if o.type == 'ARMATURE'][0]
body = [o for o in scene.objects if o.type == 'MESH'][0]
arm.name = "Armature"
body.name = "Zombie"

# --- Dreiecke verkleinern (Decimate vor dem Armature-Modifier anwenden) -----------------------
tris = sum(len(p.vertices) - 2 for p in body.data.polygons)
bpy.context.view_layer.objects.active = body
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
dec = body.modifiers.new("Verkleinern", 'DECIMATE')
dec.ratio = min(1.0, target / tris)
dec.use_collapse_triangulate = True
bpy.ops.object.modifier_move_to_index(modifier=dec.name, index=0)
bpy.ops.object.modifier_apply(modifier=dec.name)
print("DREIECKE", tris, "->", sum(len(p.vertices) - 2 for p in body.data.polygons))

# --- Textur 1024 ------------------------------------------------------------------------------
for img in bpy.data.images:
    if img.size[0] > 1024:
        img.scale(1024, 1024)
        img.pack()

# --- Bewegungen --------------------------------------------------------------------------------
RENAME = {"Walking": "Walk", "Running": "Run", "Attack": "Attack", "Dead": "Death"}
for a in list(bpy.data.actions):
    if a.name in RENAME:
        a.name = RENAME[a.name]
        a.use_fake_user = True
    else:
        bpy.data.actions.remove(a)
if arm.animation_data:
    arm.animation_data.action = None
print("BEWEGUNGEN", sorted(a.name for a in bpy.data.actions))

bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS',
                          export_yup=True, export_apply=False, export_force_sampling=True)
print("FERTIG", out)
