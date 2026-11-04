#!/usr/bin/env python3
"""Effektpakete von ChatGPT (Vorlage_Raw/Effekte_ChatGPT_v1/<name>/) ins Spiel übernehmen: game/fx/<name>.webp + .json.
Die Einzelbilder werden auf die Größe gebracht, in der der Effekt auf dem Handy erscheint (etwa 110 Bildpunkte je
Meter, auf 64/128/256 gerundet), damit der Grafikspeicher im Kampf klein bleibt. Raster, Reihenfolge, Anker,
Bildrate und Schleife bleiben wie geliefert. Aufruf: import_chatgpt.py <quelle> <ziel>"""
import json, os, sys
from PIL import Image

PX_PER_M = 110.0


def frame_px(groesse_m, orig):
    want = groesse_m * PX_PER_M
    for p in (64, 128, 256):
        if want <= p * 1.15:
            return min(p, orig)
    return min(256, orig)


def main(src, dst):
    os.makedirs(dst, exist_ok=True)
    total = 0
    for name in sorted(os.listdir(src)):
        d = os.path.join(src, name)
        js = os.path.join(d, name + '.json')
        if not os.path.isfile(js):
            continue
        meta = json.load(open(js))
        sheet = os.path.join(d, name + '_sheet.png')
        if not os.path.isfile(sheet):
            sheet = os.path.join(d, name + '.png')
        im = Image.open(sheet).convert('RGBA')
        cols, rows = int(meta['cols']), int(meta['rows'])
        fw, fh = im.width // cols, im.height // rows
        px = frame_px(float(meta.get('groesse_m', 1.0)), fw)
        out = im.resize((px * cols, px * rows), Image.LANCZOS) if px != fw else im
        out.save(os.path.join(dst, name + '.webp'), 'WEBP', quality=90, method=6)
        info = {k: meta[k] for k in ('frames', 'cols', 'rows', 'fps', 'loop', 'anker', 'groesse_m') if k in meta}
        info['frame_px'] = px
        json.dump(info, open(os.path.join(dst, name + '.json'), 'w'))
        total += out.width * out.height * 4
        print('%-28s %4d -> %3d px  %dx%d' % (name, fw, px, out.width, out.height))
    print('Grafikspeicher aller Blätter: %.1f MB' % (total / 1048576))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
