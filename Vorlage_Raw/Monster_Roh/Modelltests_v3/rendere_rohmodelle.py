import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parent
ids=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['schleimling','schleimmutter','krabbler','brecher','koloss']
for name in ids:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(root/(name+'_statisch_roh.glb')))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
    assert pts and all(math.isfinite(c) for p in pts for c in p)
    bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
    center=Vector([(a+b)/2 for a,b in bounds]);size=max(b-a for a,b in bounds)
    scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE_NEXT'
    scene.render.resolution_x=1024;scene.render.resolution_y=1024;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=True
    scene.view_settings.view_transform='Standard'
    scene.world=bpy.data.worlds.new('Pruefumgebung');scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.18,.24,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.4
    def aim(o):o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=size*1.25;scene.camera=cam
    for offset,power in [((-2,-3,4),500),((3,-2,3),300),((0,3,4),350)]:
        bpy.ops.object.light_add(type='AREA',location=center+Vector(offset)*size)
        light=bpy.context.object;light.data.energy=power*size**2;light.data.size=size*3;aim(light)
    for view,offset in [('vorn',(0,-5,.0)),('seite',(5,0,0)),('oben',(0,0,5))]:
        cam.location=center+Vector(offset)*size;aim(cam)
        scene.render.filepath=str(root/(name+'_vorschau_'+view+'.png'));bpy.ops.render.render(write_still=True)
    report={'id':name,'import_erfolgreich':True,'netze':len(meshes),'dreiecke':sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in meshes),'grenzen_blender_xyz':bounds,'hinweis':'Ansichten aus unverändertem Rohmodell; Anatomie wird visuell geprüft. Kein Godot-Test.'}
    (root/(name+'_IMPORTPRUEFUNG.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
