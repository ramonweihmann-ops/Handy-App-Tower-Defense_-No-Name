#!/usr/bin/env python3
"""Export (PNG + layout.json) in den Spielordner übernehmen: WebP, Import-Einstellungen (verlustbehaftet,
spart Platz), Bildpfade in der layout.json.  Aufruf: to_game.py <export-ordner> <bildschirm-name>"""
import hashlib, json, os, sys
from PIL import Image

GAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'game')
IMPORT = '''[remap]

importer="texture"
type="CompressedTexture2D"

[deps]

source_file="res://ui_mock/{name}/{file}"

[params]

compress/mode={mode}
compress/high_quality=false
compress/lossy_quality={q}
compress/uastc_level=0
compress/rdo_quality_loss=0.0
compress/hdr_compression=1
compress/normal_map=0
compress/channel_pack=0
mipmaps/generate=false
mipmaps/limit=-1
roughness/mode=0
roughness/src_normal=""
process/channel_remap/red=0
process/channel_remap/green=1
process/channel_remap/blue=2
process/channel_remap/alpha=3
process/fix_alpha_border=true
process/premult_alpha=false
process/normal_map_invert_y=false
process/hdr_as_srgb=false
process/hdr_clamp_exposure=false
process/size_limit=0
detect_3d/compress_to=1
'''


def convert(src, name):
    dst = os.path.join(GAME, 'ui_mock', name)
    os.makedirs(dst, exist_ok=True)
    lay = json.load(open(os.path.join(src, 'layout.json')))
    keep = set()
    seen = {}   # gleiche Bilder (z. B. Hintergrund mehrerer Zustände) nur einmal ablegen

    def add(f, q, opaque):
        src_f = os.path.join(src, f)
        if not os.path.exists(src_f):
            return ''
        im = Image.open(src_f)
        im = im.convert('RGB') if opaque else im.convert('RGBA')
        if not opaque and im.getbbox() is None:
            return ''
        digest = hashlib.sha1(im.tobytes() + str(im.size).encode() + im.mode.encode()).hexdigest()
        if digest in seen:
            return seen[digest]
        out = f.replace('.png', '.webp')
        if opaque:
            im.save(os.path.join(dst, out), 'WEBP', quality=int(q * 100), method=5)
        else:
            im.save(os.path.join(dst, out), 'WEBP', lossless=True, quality=100, method=5)
        keep.add(out)
        imp = os.path.join(dst, out + '.import')
        open(imp, 'w').write(IMPORT.format(name=name, file=out, q=q, mode=1 if opaque else 0))
        seen[digest] = out
        return out

    for st, d in lay['states'].items():
        d['bg'] = add(f'{st}_bg.png', 0.82, True)
        for b in d['buttons']:
            b['img'] = add(f'{st}_btn{b["i"]}.png', 0.9, False) if 'img_rect' in b else ''
        for l in d.get('live', []):
            l['img'] = add(f'{st}_live_{l["id"]}.png', 0.9, False) if l.get('img') else ''
    for ov, d in lay.get('overlays', {}).items():
        d['bg'] = add(f'ov_{ov}_bg.png', 0.88, False)
        for b in d['buttons']:
            b['img'] = add(f'ov_{ov}_btn{b["i"]}.png', 0.9, False) if 'img_rect' in b else ''
        for l in d.get('live', []):
            l['img'] = add(f'ov_{ov}_live_{l["id"]}.png', 0.9, False) if l.get('img') else ''
    # alte Bilder dieses Bildschirms entfernen
    for f in os.listdir(dst):
        base = f[:-7] if f.endswith('.import') else f
        if base.endswith('.webp') and base not in keep:
            os.remove(os.path.join(dst, f))
    json.dump(lay, open(os.path.join(dst, 'layout.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    total = sum(os.path.getsize(os.path.join(dst, f)) for f in os.listdir(dst))
    print(name, len(keep), 'Bilder', total // 1024, 'KB')


if __name__ == '__main__':
    convert(sys.argv[1], sys.argv[2])
