# Detail-Baukasten: reiche Oberflächen (Schmutz in Fugen, Verläufe, Kratzer, Maserung, feine Unebenheit) und Bauteile
import random
def rich(name, color, metal=0.6, rough=0.35, dirt=(0.04, 0.045, 0.06), ao_dist=0.18, ao_strength=0.85, var=0.18,
         grad=0.35, scratches=0.0, veins=None, bump=0.12, cracks=None, crack_emit=0.0, crack_width=0.018, crack_mask=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    L = nt.links.new
    p = nt.nodes["Principled BSDF"]
    p.inputs["Metallic"].default_value = metal
    p.inputs["Roughness"].default_value = rough
    tc = nt.nodes.new("ShaderNodeTexCoord")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    # Grundfarbe mit großflächiger Schwankung
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.2; nz.inputs["Detail"].default_value = 6.0
    L(geo.outputs["Position"], nz.inputs["Vector"])
    mv = nt.nodes.new("ShaderNodeMix"); mv.data_type = 'RGBA'
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.35; mr.inputs["From Max"].default_value = 0.7
    mr.inputs["To Max"].default_value = var
    L(nz.outputs["Fac"], mr.inputs["Value"]); L(mr.outputs["Result"], mv.inputs["Factor"])
    mv.inputs[6].default_value = (*color, 1)
    mv.inputs[7].default_value = (color[0] * 0.55, color[1] * 0.55, color[2] * 0.62, 1)
    col = mv.outputs[2]
    # Maserung (Marmor) oder Kratzer
    if veins:
        wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 1.6; wv.inputs["Distortion"].default_value = 14.0
        wv.inputs["Detail"].default_value = 6.0
        L(geo.outputs["Position"], wv.inputs["Vector"])
        vr = nt.nodes.new("ShaderNodeMapRange"); vr.inputs["From Min"].default_value = 0.0; vr.inputs["From Max"].default_value = 0.08
        vr.inputs["To Min"].default_value = 0.55; vr.inputs["To Max"].default_value = 0.0
        L(wv.outputs["Fac"], vr.inputs["Value"])
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
        L(vr.outputs["Result"], mx.inputs["Factor"]); L(col, mx.inputs[6]); mx.inputs[7].default_value = (*veins, 1)
        col = mx.outputs[2]
    if scratches > 0:
        mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.5, 60.0, 9.0)
        mp.inputs["Rotation"].default_value = (0, 0, 0.3)
        L(geo.outputs["Position"], mp.inputs["Vector"])
        sn = nt.nodes.new("ShaderNodeTexNoise"); sn.inputs["Scale"].default_value = 4.0; sn.inputs["Detail"].default_value = 2.0
        L(mp.outputs["Vector"], sn.inputs["Vector"])
        sr = nt.nodes.new("ShaderNodeMapRange"); sr.inputs["From Min"].default_value = 0.66; sr.inputs["From Max"].default_value = 0.7
        sr.inputs["To Max"].default_value = scratches
        L(sn.outputs["Fac"], sr.inputs["Value"])
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
        L(sr.outputs["Result"], mx.inputs["Factor"]); L(col, mx.inputs[6])
        mx.inputs[7].default_value = (min(1, color[0] * 1.8 + 0.1), min(1, color[1] * 1.8 + 0.1), min(1, color[2] * 1.8 + 0.1), 1)
        col = mx.outputs[2]
    # Schmutz und Schatten in Fugen und Ecken (Umgebungsverdeckung)
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = ao_dist; ao.samples = 16
    ar = nt.nodes.new("ShaderNodeMapRange"); ar.inputs["From Min"].default_value = 0.35; ar.inputs["From Max"].default_value = 1.0
    ar.inputs["To Min"].default_value = ao_strength; ar.inputs["To Max"].default_value = 0.0
    L(ao.outputs["AO"], ar.inputs["Value"])
    md = nt.nodes.new("ShaderNodeMix"); md.data_type = 'RGBA'
    L(ar.outputs["Result"], md.inputs["Factor"]); L(col, md.inputs[6]); md.inputs[7].default_value = (*dirt, 1)
    col = md.outputs[2]
    # Verlauf: unten dunkler (wie gemalt)
    sz = nt.nodes.new("ShaderNodeSeparateXYZ"); L(geo.outputs["Position"], sz.inputs[0])
    gr = nt.nodes.new("ShaderNodeMapRange"); gr.inputs["From Min"].default_value = 0.0; gr.inputs["From Max"].default_value = 1.6
    gr.inputs["To Min"].default_value = 1.0 - grad; gr.inputs["To Max"].default_value = 1.05
    L(sz.outputs[2], gr.inputs["Value"])
    mg = nt.nodes.new("ShaderNodeMix"); mg.data_type = 'RGBA'; mg.blend_type = 'MULTIPLY'; mg.inputs["Factor"].default_value = 1.0
    L(col, mg.inputs[6])
    cg = nt.nodes.new("ShaderNodeCombineColor")
    for k in range(3):
        L(gr.outputs["Result"], cg.inputs[k])
    L(cg.outputs[0], mg.inputs[7])
    col = mg.outputs[2]
    if cracks:
        vor = nt.nodes.new("ShaderNodeTexVoronoi"); vor.feature = 'DISTANCE_TO_EDGE'; vor.inputs["Scale"].default_value = 3.0
        L(geo.outputs["Position"], vor.inputs["Vector"])
        th = nt.nodes.new("ShaderNodeMapRange"); th.inputs["From Max"].default_value = crack_width
        th.inputs["To Min"].default_value = 1.0; th.inputs["To Max"].default_value = 0.0
        L(vor.outputs["Distance"], th.inputs["Value"])
        msk = nt.nodes.new("ShaderNodeTexNoise"); msk.inputs["Scale"].default_value = 1.3
        L(geo.outputs["Position"], msk.inputs["Vector"])
        mk = nt.nodes.new("ShaderNodeMapRange"); mk.inputs["From Min"].default_value = crack_mask; mk.inputs["From Max"].default_value = crack_mask + 0.05
        L(msk.outputs["Fac"], mk.inputs["Value"])
        mm = nt.nodes.new("ShaderNodeMath"); mm.operation = 'MULTIPLY'
        L(th.outputs["Result"], mm.inputs[0]); L(mk.outputs["Result"], mm.inputs[1])
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
        L(mm.outputs[0], mx.inputs["Factor"]); L(col, mx.inputs[6]); mx.inputs[7].default_value = (*cracks, 1)
        col = mx.outputs[2]
        if crack_emit > 0:
            p.inputs["Emission Color"].default_value = (*cracks, 1)
            me = nt.nodes.new("ShaderNodeMath"); me.operation = 'MULTIPLY'; me.inputs[1].default_value = crack_emit
            L(mm.outputs[0], me.inputs[0]); L(me.outputs[0], p.inputs["Emission Strength"])
    L(col, p.inputs["Base Color"])
    # feine Unebenheit
    if bump > 0:
        bn = nt.nodes.new("ShaderNodeTexNoise"); bn.inputs["Scale"].default_value = 28.0; bn.inputs["Detail"].default_value = 8.0
        L(geo.outputs["Position"], bn.inputs["Vector"])
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump; bp.inputs["Distance"].default_value = 0.02
        L(bn.outputs["Fac"], bp.inputs["Height"]); L(bp.outputs["Normal"], p.inputs["Normal"])
    return m

def glowm(name, color, strength):
    return mat(name, color, emit=color, strength=strength)

def plight(loc, color, energy, radius=0.08):
    ld = bpy.data.lights.new("P", 'POINT'); ld.energy = energy; ld.color = color; ld.shadow_soft_size = radius
    o = bpy.data.objects.new("P", ld); scene.collection.objects.link(o); o.location = loc
    return o

def cham(name, center, size, material, ch=0.06, segs=1):
    """Kasten mit gefasten (abgeschrägten) Kanten"""
    return box(name, center, size, material, bevel=ch, segs=segs)

HALF = 6.4
FR = -0.6
MODS = [-5.4, -3.6, -1.8, 0.0, 1.8, 3.6, 5.4]
def segments():
    e = [-HALF] + MODS + [HALF]
    out = []
    for i in range(len(e) - 1):
        x0 = e[i] + (0.42 if i > 0 else 0.0)
        x1 = e[i + 1] - (0.42 if i < len(e) - 2 else 0.0)
        out.append((x0, x1))
    return out

def shadow_catcher():
    """Boden als Schattenfänger: weicher Schatten und Kontaktschatten der Mauer fallen auf Brücke und Plattform"""
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -1.0, 0.0))
    g = bpy.context.active_object
    g.scale = (16, 8, 1)
    g.is_shadow_catcher = True
    return g

def glow_comp(tint=(1.0, 0.3, 0.08), threshold=0.85, size=8, alpha_gain=0.9, mix_strength=1.0):
    """Leuchten wie gemalt: Schein der hellen Teile, eingefärbt, auch über den Rand der Mauer hinaus (Deckkraft)"""
    scene.use_nodes = True
    nt = scene.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    L = nt.links.new
    rl = nt.nodes.new("CompositorNodeRLayers")
    gl = nt.nodes.new("CompositorNodeGlare"); gl.glare_type = 'FOG_GLOW'; gl.quality = 'HIGH'
    gl.threshold = threshold; gl.size = size; gl.mix = 1.0
    L(rl.outputs["Image"], gl.inputs["Image"])
    tn = nt.nodes.new("CompositorNodeMixRGB"); tn.blend_type = 'MULTIPLY'; tn.inputs[0].default_value = 1.0
    tn.inputs[2].default_value = (*tint, 1)
    L(gl.outputs["Image"], tn.inputs[1])
    st = nt.nodes.new("CompositorNodeMixRGB"); st.blend_type = 'MULTIPLY'; st.inputs[0].default_value = 1.0
    st.inputs[2].default_value = (mix_strength, mix_strength, mix_strength, 1)
    L(tn.outputs["Image"], st.inputs[1])
    add = nt.nodes.new("CompositorNodeMixRGB"); add.blend_type = 'ADD'; add.inputs[0].default_value = 1.0
    L(rl.outputs["Image"], add.inputs[1]); L(st.outputs["Image"], add.inputs[2])
    bw = nt.nodes.new("CompositorNodeRGBToBW"); L(st.outputs["Image"], bw.inputs[0])
    gain = nt.nodes.new("CompositorNodeMath"); gain.operation = 'MULTIPLY'; gain.inputs[1].default_value = alpha_gain
    L(bw.outputs[0], gain.inputs[0])
    mx = nt.nodes.new("CompositorNodeMath"); mx.operation = 'MAXIMUM'; mx.use_clamp = True
    L(rl.outputs["Alpha"], mx.inputs[0]); L(gain.outputs[0], mx.inputs[1])
    sa = nt.nodes.new("CompositorNodeSetAlpha"); sa.mode = 'REPLACE_ALPHA'
    L(add.outputs["Image"], sa.inputs["Image"]); L(mx.outputs[0], sa.inputs["Alpha"])
    comp = nt.nodes.new("CompositorNodeComposite")
    L(sa.outputs["Image"], comp.inputs["Image"])
