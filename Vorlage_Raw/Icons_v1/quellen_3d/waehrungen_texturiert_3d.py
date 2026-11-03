import bpy,json,math
from pathlib import Path
from mathutils import Vector
W=Path(__file__).resolve().parent
OUT=(W.parent/'modelle') if W.name=='quellen_3d' else (W.parent/'icons_v1'/'modelle')
OUT.mkdir(parents=True,exist_ok=True)
(W/'drehung_roh').mkdir(exist_ok=True)
reports=[]
for spec in json.loads((W/'waehrung_geometrie.json').read_text(encoding='utf-8')):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    kind=spec['motiv'];points=spec['kontur'];n=len(points)
    depth={'gold':.22,'gems':.45,'energy':.22,'stars':.20}[kind]
    verts=[(x,y,z) for y in [-depth/2,depth/2] for x,z in points]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    front_count=2
    if kind=='gems':
        # Zwei gefaltete Kristallflächen statt eines rechteckigen Seitenprofils.
        verts=[(x,y,z) for y in [-.025,.025] for x,z in points]+[(0,-.40,.04),(0,.40,.04)]
        faces=[(i,(i+1)%n,2*n) for i in range(n)]+[(n+(i+1)%n,n+i,2*n+1) for i in range(n)]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        front_count=2*n
    mesh=bpy.data.meshes.new('Motivkoerper');mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new('IconRoot',mesh);bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj;obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')
    front=bpy.data.materials.new('Freigegebenes_Motiv');front.use_nodes=True
    nodes=front.node_tree.nodes;nodes.clear();out=nodes.new('ShaderNodeOutputMaterial');em=nodes.new('ShaderNodeEmission');tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(W/('waehrung_'+kind+'.png')));tex.image.pack()
    front.node_tree.links.new(tex.outputs['Color'],em.inputs['Color']);front.node_tree.links.new(em.outputs[0],out.inputs['Surface'])
    side=bpy.data.materials.new('Koerperkante');side.use_nodes=True
    color={'gold':(1,.48,.012,1),'gems':(.65,.055,.36,1),'energy':(.07,.55,.035,1),'stars':(1,.48,.012,1)}[kind]
    p=side.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=color;p.inputs['Roughness'].default_value=.3;p.inputs['Metallic'].default_value=.05
    p.inputs['Emission Color'].default_value=color;p.inputs['Emission Strength'].default_value=.75
    mesh.materials.append(front);mesh.materials.append(side)
    uv=mesh.uv_layers.new(name='Motiv_UV')
    for poly in mesh.polygons:
        poly.material_index=0 if poly.index<front_count else 1;poly.use_smooth=False
        for li in poly.loop_indices:
            v=mesh.vertices[mesh.loops[li].vertex_index].co
            uv.data[li].uv=((v.x+1)/2,(v.z+1)/2)
    obj.rotation_euler=(0,0,0);obj.keyframe_insert(data_path='rotation_euler',frame=0)
    obj.rotation_euler.z=2*math.pi;obj.keyframe_insert(data_path='rotation_euler',frame=36)
    a=obj.animation_data.action;a.name='Spin'
    for layer in a.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for kp in fc.keyframe_points:kp.interpolation='LINEAR'
    sc=bpy.context.scene;sc.render.fps=30;sc.frame_start=0;sc.frame_end=36;sc.frame_set(0)
    bpy.ops.export_scene.gltf(filepath=str(OUT/('icon_'+kind+'.glb')),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_yup=True)
    bpy.ops.object.camera_add(location=(0,-6,0));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2;sc.camera=cam
    for loc,energy,size in [((-3,-4,5),400,4),((3,1,2),200,4)]:
        bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=energy;o.data.size=size;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
    sc.world=bpy.data.worlds.new('Umgebung');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[1].default_value=.4
    sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.render.image_settings.color_depth='8';sc.render.resolution_x=512;sc.render.resolution_y=512;sc.render.resolution_percentage=100
    sc.view_settings.view_transform='Standard';sc.view_settings.look='None'
    for i in range(12):
        sc.frame_set(i*3);sc.render.filepath=str(W/'drehung_roh'/(kind+'_'+str(i).zfill(2)+'.png'));bpy.ops.render.render(write_still=True)
    tris=sum(len(p.vertices)-2 for p in mesh.polygons);assert tris<=2000
    reports.append({'motiv':kind,'dreiecke':tris,'texturen':1,'texturmass':[512,512],'animation':'Spin','dauer_sekunden':1.2,'drehachse_glb':'Y','vorderseite_glb':'+Z','bilder':12,'winkelabstand_grad':30,'modellart':'Einfacher Symbolkörper mit eingebetteter Motivtextur; Kristall mit gefalteten Flächen, übrige Symbole als Extrusionen'})
    (W/'DREHUNG_3D_PRUEFUNG.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
    print('MOTIV_FERTIG',kind,tris,flush=True)
