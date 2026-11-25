# Mund eines Champions in der Textur neu malen (Wunsch 25.11.2026 zu Fritzi: „Zähne stehen hervor, sieht aus wie ein
# Überbiss“). Die Zähne sind nur aufgemalt; das große weiße Band mit dem dunklen Strich in der Mitte wirkte wie
# Hasenzähne. Neu: schmalere obere Zahnreihe am Oberlippenrand mit feinen Zahnfugen, darunter dunkler Mundraum mit
# Zunge, unten ein schmaler Rand unterer Zähne. Umriss des Mundes bleibt. Nur die Farbtextur im GLB wird ersetzt,
# Netz, Skelett und Bewegungen bleiben unverändert.
# Aufruf: blender -b -P tools/heroes/mund_nachmalen.py -- <ein.glb> <aus.glb> <Netzname> <x0,x1,z0,z1>
import bpy, sys, json, struct, os, tempfile, math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform

argv = sys.argv[sys.argv.index("--") + 1:]
SRC, DST, MESH = argv[0], argv[1], argv[2]
X0, X1, Z0, Z1 = [float(v) for v in argv[3].split(",")]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
arm.data.pose_position = 'REST'; bpy.context.view_layer.update()
o = next(o for o in bpy.data.objects if o.name == MESH)
me = o.data
# 1) Mundbereich von vorn abtasten: Position (x, z) -> Texel; das Material nehmen, das der Mund wirklich trägt
bvh = BVHTree.FromObject(o, bpy.context.evaluated_depsgraph_get()); uvl = me.uv_layers.active.data
inv = o.matrix_world.inverted()
loc, nor, idx, d = bvh.ray_cast(inv @ Vector(((X0 + X1) / 2, -2.0, (Z0 + Z1) / 2)), (inv.to_3x3() @ Vector((0, 1, 0))).normalized())
MAT = me.materials[me.polygons[idx].material_index]
print("MATERIAL", MAT.name)
img = next(n for n in MAT.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image and 'normal' not in n.image.name.lower()).image
w, h = img.size
px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
S = []
step = 0.0005
for z in np.arange(Z0, Z1, step):
    for x in np.arange(X0, X1, step):
        loc, nor, idx, d = bvh.ray_cast(inv @ Vector((x, -2.0, z)), (inv.to_3x3() @ Vector((0, 1, 0))).normalized())
        if loc is None or me.materials[me.polygons[idx].material_index] != MAT:
            continue
        li = me.polygons[idx].loop_indices[:3]
        vs = [me.vertices[me.loops[k].vertex_index].co for k in li]
        uv = barycentric_transform(loc, *vs, *[uvl[k].uv.to_3d() for k in li])
        S.append((x, z, min(w - 1, int(uv.x * w)), min(h - 1, int(uv.y * h))))
S = np.array(S)
col = px[S[:, 3].astype(int), S[:, 2].astype(int), :3]
lum = col @ np.array([0.3, 0.6, 0.1]); sat = col.max(1) - col.min(1)
white = (lum > 0.7) & (sat < 0.15)
dark = (lum < 0.35) & (col[:, 2] >= col[:, 0])               # dunkler Umriss / Fuge (blaugrau)

# 2) Ober- und Unterkante des Mundes je Spalte (Zahnweiß), Lücken (dunkler Mittelstrich) aus den Nachbarn füllen
bins = np.round((S[:, 0] - X0) / 0.002).astype(int)
nb = bins.max() + 1
top = np.full(nb, np.nan); bot = np.full(nb, np.nan)
for b in range(nb):
    m = (bins == b) & white
    if m.sum() > 2:
        top[b] = S[m, 1].max(); bot[b] = S[m, 1].min()
ok = ~np.isnan(top)
idx = np.arange(nb)
top = np.interp(idx, idx[ok], top[ok]); bot = np.interp(idx, idx[ok], bot[ok])
xs_ok = idx[ok]
bmin, bmax = xs_ok.min(), xs_ok.max()
cx = X0 + (bmin + bmax) / 2 * 0.002; half = (bmax - bmin) / 2 * 0.002
print("MUND", round(cx, 4), round(half, 4), "Höhe", round(float(np.nanmax(top - bot)), 4))

# 3) neu malen, Dreieck für Dreieck: Die Textur ist in viele Stücke zerteilt; für jedes Texel eines Munddreiecks wird
#    seine Lage im Gesicht (x, z) berechnet und danach entschieden, ob es Zahn, Mundraum, Zunge oder Umriss ist
TOOTH = np.array((0.97, 0.96, 0.92), np.float32); FUGE = np.array((0.78, 0.77, 0.8), np.float32)
SHADE = np.array((0.86, 0.85, 0.84), np.float32)
INNER = np.array((0.34, 0.08, 0.12), np.float32); TONGUE = np.array((0.86, 0.4, 0.44), np.float32)
mw = o.matrix_world
OUTLINE = np.median(col[dark], axis=0).astype(np.float32) if dark.any() else np.array((0.13, 0.13, 0.25), np.float32)
base = px.copy()
PAINTED = np.zeros((h, w), dtype=bool)
n_paint = 0
zmin, zmax = float(bot.min()) - 0.004, float(top.max()) + 0.004
for poly in me.polygons:
    if me.materials[poly.material_index] != MAT:
        continue
    c3 = mw @ poly.center
    if not (cx - half - 0.006 < c3.x < cx + half + 0.006 and zmin < c3.z < zmax and c3.y < -0.15):
        continue
    li = list(poly.loop_indices)
    for t_ in range(1, len(li) - 1):
        tri = (li[0], li[t_], li[t_ + 1])
        UV = np.array([(uvl[k].uv.x * w, uvl[k].uv.y * h) for k in tri])
        P3 = np.array([tuple(mw @ me.vertices[me.loops[k].vertex_index].co) for k in tri])
        x0_, y0_ = np.floor(UV.min(0)).astype(int) - 1; x1_, y1_ = np.ceil(UV.max(0)).astype(int) + 1
        gx, gy = np.meshgrid(np.arange(max(x0_, 0), min(x1_, w - 1) + 1), np.arange(max(y0_, 0), min(y1_, h - 1) + 1))
        Q = np.stack([gx.ravel() + 0.5, gy.ravel() + 0.5], 1)
        v0 = UV[1] - UV[0]; v1 = UV[2] - UV[0]; d00 = v0 @ v0; d01 = v0 @ v1; d11 = v1 @ v1; den = d00 * d11 - d01 * d01
        if abs(den) < 1e-9:
            continue
        v2 = Q - UV[0]; d20 = v2 @ v0; d21 = v2 @ v1
        b1 = (d11 * d20 - d01 * d21) / den; b2 = (d00 * d21 - d01 * d20) / den; b0 = 1 - b1 - b2
        eps = -1.0 / max(1.0, math.sqrt(max(d00, d11)))
        ins = (b0 >= eps) & (b1 >= eps) & (b2 >= eps)
        for (qx, qy), bb0, bb1, bb2 in zip(Q[ins], b0[ins], b1[ins], b2[ins]):
            tx, ty = int(qx), int(qy)
            x, y, z = bb0 * P3[0] + bb1 * P3[1] + bb2 * P3[2]
            bi = int(round((x - X0) / 0.002))
            if bi < bmin or bi > bmax:
                continue
            tp, bt = top[bi], bot[bi]
            if not (bt - 0.0015 <= z <= tp + 0.0015) or abs(x - cx) > half + 0.001:
                continue
            t = min(1.0, max(0.0, (tp - z) / max(1e-4, tp - bt)))
            rx = (x - cx) / max(1e-4, half)
            if z > tp - 0.0012 or z < bt + 0.0012 or abs(x - cx) > half - 0.003:
                c = OUTLINE                                 # sauberer Umriss
            elif t < 0.42:                                  # obere Zahnreihe
                c = TOOTH if t < 0.34 else SHADE
                for k in range(-3, 3):                      # feine Zahnfugen, keine in der Mitte
                    fx = cx + (k + 0.5) * half * 0.3
                    if abs(x - fx) < 0.0012 and t > 0.06:
                        c = FUGE
            elif t > 0.86 and abs(rx) < 0.55:               # schmaler Rand unterer Zähne
                c = SHADE
            else:                                           # Mundraum mit Zunge
                c = INNER
                if ((rx / 0.5) ** 2 + ((t - 0.86) / 0.22) ** 2) < 1.0:
                    c = TONGUE
            PAINTED[ty, tx] = True
            base[ty, tx, :3] = c
            n_paint += 1
print("GEMALT", n_paint)
# Nahtränder: Texel außerhalb aller Dreiecke neben dem Mund mit den Mundfarben füllen (sonst dunkle Linie an Nähten)
from PIL import Image as _I, ImageDraw as _D
cov = _I.new("L", (w, h), 0); dr = _D.Draw(cov)
for poly in me.polygons:
    if me.materials[poly.material_index] == MAT:
        dr.polygon([(uvl[k].uv.x * w, uvl[k].uv.y * h) for k in poly.loop_indices], fill=255)
covered = np.array(cov) > 0
filled = PAINTED.copy()
for _ in range(3):
    acc = np.zeros((h, w, 3), np.float32); cnt = np.zeros((h, w), np.float32)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        f = np.roll(filled, (dy, dx), (0, 1)); acc += np.roll(base[..., :3], (dy, dx), (0, 1)) * f[..., None]; cnt += f
    new = (~filled) & (~covered) & (cnt > 0)
    base[new, :3] = acc[new] / cnt[new][:, None]; filled |= new
img.pixels.foreach_set(base.ravel())
tmp = os.path.join(tempfile.mkdtemp(), "farbe.png")
img.filepath_raw = tmp; img.file_format = 'PNG'; img.save()
new_png = open(tmp, "rb").read()

# 4) Bild im GLB ersetzen (Netz, Skelett und Bewegungen bleiben Byte für Byte gleich)
d = open(SRC, "rb").read()
jl = struct.unpack("<I", d[12:16])[0]; J = json.loads(d[20:20 + jl])
off = 20 + jl; bl = struct.unpack("<I", d[off:off + 4])[0]; BIN = bytearray(d[off + 8:off + 8 + bl])
mat = next(m for m in J["materials"] if m["name"] == MAT.name)
src_img = J["textures"][mat["pbrMetallicRoughness"]["baseColorTexture"]["index"]]["source"]
bv = J["bufferViews"][J["images"][src_img]["bufferView"]]
while len(BIN) % 4:
    BIN.append(0)
bv["byteOffset"] = len(BIN); bv["byteLength"] = len(new_png)
BIN += new_png
while len(BIN) % 4:
    BIN.append(0)
J["buffers"][0]["byteLength"] = len(BIN)
js = json.dumps(J, separators=(",", ":")).encode()
while len(js) % 4:
    js += b" "
out = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(BIN)) + struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(BIN), 0x004E4942) + bytes(BIN)
open(DST, "wb").write(out)
print("FERTIG", DST, len(out))
