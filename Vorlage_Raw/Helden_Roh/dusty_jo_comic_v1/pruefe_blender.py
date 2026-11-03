import bpy, json
from pathlib import Path
from mathutils import Vector

p = Path(__file__).parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(p/'dusty_jo_smart_rig_roh.glb'))
netze = [o for o in bpy.context.scene.objects if o.type == 'MESH']
armaturen = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
punkte = [o.matrix_world @ Vector(e) for o in netze for e in o.bound_box]
hautnetze = [o for o in netze if any(m.type == 'ARMATURE' for m in o.modifiers)]
hautpunkte = [o.matrix_world @ Vector(e) for o in hautnetze for e in o.bound_box]
bericht = {
    'import_erfolgreich': True,
    'hinweis': 'Nur Importprüfung, keine Änderungen oder Exporte. Blender verwendet intern Z als Hochachse.',
    'ausdehnung_blender': {a: [min(v[i] for v in punkte), max(v[i] for v in punkte)] for i,a in enumerate('XYZ')},
    'ausdehnung_nur_figur_blender': {a: [min(v[i] for v in hautpunkte), max(v[i] for v in hautpunkte)] for i,a in enumerate('XYZ')},
    'netze': [{'name': o.name, 'punkte': len(o.data.vertices), 'punkte_ohne_gewicht': sum(not any(g.weight > 0 for g in v.groups) for v in o.data.vertices), 'armatur_modifikatoren': [m.object.name if m.object else None for m in o.modifiers if m.type == 'ARMATURE']} for o in netze],
    'skelette': [{'name': a.name, 'knochenzahl': len(a.data.bones), 'knochen': [{'name': b.name, 'eltern': b.parent.name if b.parent else None, 'kopf_blender_welt': list(a.matrix_world @ b.head_local), 'ende_blender_welt': list(a.matrix_world @ b.tail_local)} for b in a.data.bones]} for a in armaturen],
    'aktionen': [a.name for a in bpy.data.actions],
}
(p/'BLENDER_IMPORTPRUEFUNG.json').write_text(json.dumps(bericht, ensure_ascii=False, indent=2), encoding='utf-8')
print('IMPORTPRUEFUNG:', json.dumps({k:v for k,v in bericht.items() if k != 'skelette'}, ensure_ascii=False))
