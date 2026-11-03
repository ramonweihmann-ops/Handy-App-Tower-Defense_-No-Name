import bpy, json, math
from pathlib import Path
from mathutils import Vector

p = Path(__file__).parent
berichte = []
for name in ['zombie', 'tentakler', 'panzerkaefer']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(p/(name+'_rig_roh.glb')))
    arm = next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
    netze = [o for o in bpy.context.scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers)]
    for o in list(bpy.context.scene.objects):
        if o.type=='MESH' and o not in netze: bpy.data.objects.remove(o,do_unlink=True)
    def grenzen():
        deps = bpy.context.evaluated_depsgraph_get()
        punkte = [o.matrix_world @ v.co for orig in netze for o in [orig.evaluated_get(deps)] for v in o.data.vertices]
        assert all(math.isfinite(c) for v in punkte for c in v)
        return [[min(v[i] for v in punkte),max(v[i] for v in punkte)] for i in range(3)]
    aktionen = list(bpy.data.actions)
    proben = []
    for a in aktionen:
        arm.animation_data_create(); arm.animation_data.action = a
        if a.slots: arm.animation_data.action_slot=a.slots[0]
        start,ende=a.frame_range
        for t in [0,.25,.5,.75,1]:
            f=start+(ende-start)*t
            bpy.context.scene.frame_set(int(f),subframe=f-int(f))
            bpy.context.view_layer.update()
            proben.append({'aktion':a.name,'anteil':t,'grenzen_blender':grenzen()})
    if name=='zombie':
        a=next(a for a in aktionen if a.name=='Walking')
        arm.animation_data.action=a
        if a.slots: arm.animation_data.action_slot=a.slots[0]
        bpy.context.scene.frame_set(8)
    else:
        arm.data.pose_position='REST'
    bpy.context.view_layer.update()
    b=grenzen(); mitte=Vector([(a+z)/2 for a,z in b]); groesse=max(z-a for a,z in b)
    scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE_NEXT'
    scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
    scene.world=bpy.data.worlds.new('Vorschauraum');scene.world.color=(.05,.06,.1)
    scene.view_settings.view_transform='Standard'
    def aim(o):o.rotation_euler=(mitte-o.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add(location=mitte+Vector((.8,-2,1.05))*groesse)
    cam=bpy.context.object;aim(cam);cam.data.type='ORTHO';cam.data.ortho_scale=groesse*1.35;scene.camera=cam
    for versatz,leistung in [((2,-3,4),700),((-3,-2,2),450),((0,3,3),550)]:
        bpy.ops.object.light_add(type='AREA',location=mitte+Vector(versatz)*groesse)
        licht=bpy.context.object;licht.data.energy=leistung*groesse**2;licht.data.shape='DISK';licht.data.size=groesse*3;aim(licht)
    scene.render.filepath=str(p/(name+'_modellvorschau.png'));bpy.ops.render.render(write_still=True)
    if name=='panzerkaefer':
        cam.location=mitte+Vector((0,0,5))*groesse;aim(cam)
        scene.render.filepath=str(p/'panzerkaefer_draufsicht_pruefung.png');bpy.ops.render.render(write_still=True)
    gewichte = {b.name:sum(1 for o in netze for v in o.data.vertices for g in v.groups if o.vertex_groups[g.group].name==b.name and g.weight>.001) for b in arm.data.bones}
    berichte.append({'datei':name+'_rig_roh.glb','beispiele':proben,'gewichtete_punkte_je_knochen':gewichte,'hinweis':'Bewegung nur beim Zombie vorhanden. Fünf Stichproben je Clip, keine Godot- oder Handy-Freigabe. Die beiden anderen Vorschauen zeigen die Ruhepose.'})
(p/'BEWEGUNGSPRUEFUNG.json').write_text(json.dumps(berichte,ensure_ascii=False,indent=2),encoding='utf-8')
