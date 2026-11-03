import bpy,json,math
from pathlib import Path
from mathutils import Vector

p=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(p/'panzerkaefer_statisch_roh.glb'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert meshes
pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
assert all(math.isfinite(x) for v in pts for x in v)
bounds=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
center=Vector([(a+b)/2 for a,b in bounds]);size=max(b-a for a,b in bounds)
assert 0<size<100
report={'datei':'panzerkaefer_statisch_roh.glb','import_erfolgreich':True,'netze':len(meshes),'dreiecke':sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in meshes),'skelette':len([o for o in bpy.context.scene.objects if o.type=='ARMATURE']),'animationen':[a.name for a in bpy.data.actions],'grenzen_blender_xyz':bounds,'hinweis':'Beinzahl wird in den gerenderten Ansichten visuell geprueft; noch keine automatische oder Godot-Freigabe.'}
(p/'BLENDER_IMPORTPRUEFUNG.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
s=bpy.context.scene;s.render.engine='BLENDER_EEVEE_NEXT';s.render.resolution_x=1024;s.render.resolution_y=1024;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.film_transparent=True;s.view_settings.view_transform='Standard'
s.world=bpy.data.worlds.new('Pruefumgebung');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.15,.17,.22,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
def aim(o):o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=center+Vector((.8,-2,1.3))*size);cam=bpy.context.object;aim(cam);cam.data.type='ORTHO';cam.data.ortho_scale=size*1.2;s.camera=cam
for offset,power in [((-2,-3,4),550),((3,-2,3),350),((0,3,4),400)]:
    bpy.ops.object.light_add(type='AREA',location=center+Vector(offset)*size);l=bpy.context.object;l.data.energy=power*size**2;l.data.size=size*3;aim(l)
for name,offset in [('panzerkaefer_modellvorschau.png',(.8,-2,1.3)),('panzerkaefer_draufsicht_pruefung.png',(0,0,5)),('panzerkaefer_unterseite_pruefung.png',(0,0,-5))]:
    cam.location=center+Vector(offset)*size;aim(cam);s.render.filepath=str(p/name);bpy.ops.render.render(write_still=True)
print(json.dumps(report,ensure_ascii=False))
