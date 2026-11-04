#!/usr/bin/env python3
"""Durchsichtige Mockup-Hintergründe (nur Kopf- und Reiterleiste o. Ä.) auf die Streifen mit Inhalt
verkleinern: die Streifen werden untereinander in ein kleineres Bild gelegt, ihre Lage steht in der
layout.json ("bg_rows": [oben, unten, Lage im Bild], Mockup-Punkte). Das Spiel zeichnet nur diese Streifen
statt eines bildschirmgroßen, größtenteils leeren Bildes (spart Speicher, Ladezeit und Zeichenarbeit).
Aufruf: bg_rows.py <bildschirm> [...]   (läuft auch in to_game.py für durchsichtige Bildschirme)"""
import json, os, sys
from PIL import Image

GAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'game')


def rows_of(path, scale, gap=6):
    im = Image.open(path).convert('RGBA')
    a = im.getchannel('A').point(lambda v: 255 if v > 3 else 0)
    w, h = im.size
    bands = []
    row = a.resize((1, h), Image.BOX)   # Zeile mit irgendeinem Inhalt -> Mittelwert > 0
    vals = row.tobytes()
    y = 0
    while y < h:
        if vals[y] > 0:
            y0 = y
            while y < h and vals[y] > 0:
                y += 1
            if bands and y0 - bands[-1][1] <= gap * scale:
                bands[-1][1] = y
            else:
                bands.append([y0, y])
        else:
            y += 1
    # in Mockup-Punkte, je einen Punkt Rand
    return [[max(0.0, b0 / scale - 1.0), min(h / scale, b1 / scale + 1.0)] for b0, b1 in bands]


def apply(name):
    p = os.path.join(GAME, 'ui_mock', name, 'layout.json')
    lay = json.load(open(p))
    if not lay.get('transparent'):
        return
    scale = float(lay.get('scale', 3))
    done = {}
    for st, d in lay['states'].items():
        if not d.get('bg'):
            continue
        if d['bg'] in done:          # mehrere Zustände mit demselben Bild
            d['bg_rows'] = done[d['bg']]
            continue
        if d.get('bg_rows') and len(d['bg_rows'][0]) == 3:
            done[d['bg']] = d['bg_rows']
            continue                  # schon verkleinert
        f = os.path.join(GAME, 'ui_mock', name, d['bg'])
        rows = rows_of(f, scale)
        im = Image.open(f).convert('RGBA')
        parts, out_rows, y = [], [], 0
        for y0, y1 in rows:
            a0, a1 = round(y0 * scale), round(y1 * scale)
            parts.append(im.crop((0, a0, im.width, a1)))
            out_rows.append([a0 / scale, a1 / scale, y / scale])
            y += a1 - a0
        atlas = Image.new('RGBA', (im.width, max(1, y)), (0, 0, 0, 0))
        y = 0
        for part in parts:
            atlas.paste(part, (0, y))
            y += part.height
        atlas.save(f, 'WEBP', lossless=True, quality=100, method=5)
        d['bg_rows'] = out_rows
        done[d['bg']] = out_rows
        print(name, st, im.size, '->', atlas.size)
    json.dump(lay, open(p, 'w'), ensure_ascii=False, separators=(',', ':'))


if __name__ == '__main__':
    for n in sys.argv[1:]:
        apply(n)
