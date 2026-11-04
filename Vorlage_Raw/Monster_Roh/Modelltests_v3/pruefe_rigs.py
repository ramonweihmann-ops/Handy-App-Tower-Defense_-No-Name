import bpy,json,math
from pathlib import Path
root=Path(__file__).resolve().parent
reports=[]
for name in ['krabbler','brecher','koloss']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(root/(name+'_rig_roh.glb')))
    arms=[o for o in bpy.context.scene.objects if o.type=='ARMATURE'];assert len(arms)==1
    arm=arms[0];meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers)]
    assert meshes
    actions=list(bpy.data.actions);assert {'Walking','Running','Attack'}<={a.name for a in actions}
    samples=[]
    for a in actions:
        arm.animation_data_create();arm.animation_data.action=a
        if a.slots:arm.animation_data.action_slot=a.slots[0]
        start,end=a.frame_range
        for t in [0,.25,.5,.75,1]:
            frame=start+(end-start)*t;bpy.context.scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update()
            deps=bpy.context.evaluated_depsgraph_get();pts=[o.matrix_world@v.co for src in meshes for o in [src.evaluated_get(deps)] for v in o.data.vertices]
            assert pts and all(math.isfinite(c) for p in pts for c in p)
            samples.append({'aktion':a.name,'anteil':t,'grenzen_blender':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]})
    reports.append({'id':name,'import_erfolgreich':True,'knochenzahl':len(arm.data.bones),'animationen':[a.name for a in actions],'punkte_ohne_gewicht':sum(1 for o in meshes for v in o.data.vertices if not any(g.weight>.00001 for g in v.groups)),'stichproben':samples,'hinweis':'Import und endliche Koordinaten bestätigt; keine fertige Animations- oder Godot-Freigabe. Gewichte und Schulter-/Fingerverformung nacharbeiten.'})
(root/'RIG_IMPORT_UND_BEWEGUNGSPRUEFUNG.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
print('Drei Rigs mit Walking, Running und Attack importiert und stichprobenartig geprüft.')
