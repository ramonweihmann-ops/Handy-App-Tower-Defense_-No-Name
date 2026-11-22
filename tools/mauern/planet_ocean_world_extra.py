# Ozeanwelt, Zusatz: orange-weiße Rettungsringe an jedem zweiten Pfeiler, wie am Brückengeländer.
def ring_mat(name, c1, c2):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value = 0.45
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sx = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sx.inputs[0])
    at = nt.nodes.new("ShaderNodeMath"); at.operation = 'ARCTAN2'
    nt.links.new(sx.outputs["Y"], at.inputs[0]); nt.links.new(sx.outputs["X"], at.inputs[1])
    mu = nt.nodes.new("ShaderNodeMath"); mu.operation = 'MULTIPLY'; mu.inputs[1].default_value = 2.0
    nt.links.new(at.outputs[0], mu.inputs[0])
    sn = nt.nodes.new("ShaderNodeMath"); sn.operation = 'SINE'; nt.links.new(mu.outputs[0], sn.inputs[0])
    gt = nt.nodes.new("ShaderNodeMath"); gt.operation = 'GREATER_THAN'; gt.inputs[1].default_value = 0.0
    nt.links.new(sn.outputs[0], gt.inputs[0])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
    nt.links.new(gt.outputs[0], mx.inputs["Factor"])
    mx.inputs[6].default_value = (*L_(c1), 1); mx.inputs[7].default_value = (*L_(c2), 1)
    nt.links.new(mx.outputs[2], p.inputs["Base Color"])
    return m

lifering = ring_mat("Rettungsring", (1.0, 0.42, 0.12), (0.95, 0.93, 0.88))
for j, x in enumerate(MODS):
    if j % 2:
        continue
    bpy.ops.mesh.primitive_torus_add(major_radius=0.15, minor_radius=0.05, major_segments=32, minor_segments=12,
                                     location=(x, FR - 0.16, 0.58), rotation=(math.radians(90), 0, 0))
    t_ = bpy.context.active_object; t_.data.materials.append(lifering); bpy.ops.object.shade_smooth()
    # Haltetau oben
    cyl("RingTau%d" % j, (x, FR - 0.14, 0.75), 0.012, 0.06, rope, verts=8)
