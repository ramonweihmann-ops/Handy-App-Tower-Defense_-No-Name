import bpy, json
from pathlib import Path
from mathutils import Vector

p = Path(__file__).parent
berichte = []
for pfad in sorted(p.glob('*rig_roh.glb')):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(pfad))
    netze = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    armaturen = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
    hautnetze = [o for o in netze if any(m.type == 'ARMATURE' for m in o.modifiers)]
    punkte = [o.matrix_world @ Vector(e) for o in hautnetze for e in o.bound_box]
    bericht = {'datei': pfad.name, 'import_erfolgreich': True,
        'ausdehnung_nur_figur_blender': {a:[min(v[i] for v in punkte),max(v[i] for v in punkte)] for i,a in enumerate('XYZ')} if punkte else None,
        'netze': [{'name':o.name,'punkte':len(o.data.vertices),'punkte_ohne_gewicht':sum(not any(g.weight>0 for g in v.groups) for v in o.data.vertices),'gebunden':any(m.type=='ARMATURE' for m in o.modifiers)} for o in netze],
        'skelette': [{'name':a.name,'knochenzahl':len(a.data.bones),'knochen':[{'name':b.name,'eltern':b.parent.name if b.parent else None,'kopf_blender_welt':list(a.matrix_world@b.head_local),'ende_blender_welt':list(a.matrix_world@b.tail_local)} for b in a.data.bones]} for a in armaturen],
        'aktionen': [{'name':a.name,'bildbereich':list(a.frame_range)} for a in bpy.data.actions]}
    berichte.append(bericht)
    print('IMPORTPRUEFUNG:', json.dumps({k:v for k,v in bericht.items() if k!='skelette'},ensure_ascii=False))
(p/'BLENDER_IMPORTPRUEFUNG.json').write_text(json.dumps(berichte,ensure_ascii=False,indent=2),encoding='utf-8')
