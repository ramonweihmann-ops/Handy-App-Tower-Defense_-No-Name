#!/usr/bin/env python3
"""Heldenbilder in kleinen Boxen (Karten, runde Avatare) auf den Kopf ausrichten: Gesicht mittig und
groß genug, Hut darf oben über den Rand, wird aber von der Box abgeschnitten (Box hat overflow: hidden).
Eingabe: Ergebnis von portraits.js (welche <img> in welcher Box stecken, ermittelt im Browser).
Aufruf: helden_koepfe.py <mockup-ordner> <portraits.json>"""
import json, os, re, sys

D, PJ = sys.argv[1], sys.argv[2]
P = os.path.join(D, 'project')
# Augenmitte (Anteil an Breite/Höhe des Bildes) und Gesichtsbreite (Anteil an der Bildbreite),
# gemessen an game/ui/heroes2d/*.png
FACE = {'dusty': (0.506, 0.283, 0.375), 'iska': (0.55, 0.256, 0.45), 'brocken': (0.755, 0.233, 0.40),
        'volta': (0.61, 0.245, 0.41), 'kalle': (0.55, 0.242, 0.46), 'margot': (0.55, 0.286, 0.35),
        'lynx': (0.475, 0.228, 0.40), 'fritzi': (0.41, 0.222, 0.33)}
SIZE = {'dusty': (286, 418), 'iska': (273, 400), 'brocken': (326, 413), 'volta': (298, 395),
        'kalle': (283, 409), 'margot': (297, 428), 'lynx': (347, 400), 'fritzi': (338, 420)}

NEW_IDS = {'dusty': '49c2c7a7', 'iska': '79813789', 'brocken': '4ad155d8', 'volta': '4bb4b32b',
           'kalle': 'aa343cd8', 'margot': 'ae9b5eb6', 'lynx': '947d90c3', 'fritzi': '183ff7e7'}
data = json.load(open(PJ))
for board, info in data.items():
    if not info['res']:
        continue
    f = os.path.join(P, board)
    s = open(f).read()
    tags = list(re.finditer(r'<img\b[^>]*>', s))
    repl = {}
    for r in info['res']:
        ex, ey, fw = FACE[r['hero']]
        w0, h0 = SIZE[r['hero']]
        bx, by, bw, bh = r['box']
        iw, ih = bw + 2 * bx, bh + 2 * by   # Innenmaß (bx, by sind minus Randbreite)
        if r['round']:
            face_w, eye_y = min(0.66 * iw, 0.66 * ih), 0.47 * ih
        else:
            face_w, eye_y = min(0.62 * iw, 0.56 * ih), 0.40 * ih
        W = face_w / fw
        H = W * h0 / w0
        L = iw / 2 - ex * W
        T = eye_y - ey * H
        tag = tags[r['i']].group(0) if r['i'] < len(tags) else ''
        # Sicherheitsprüfung: an dieser Stelle muss ein Bild desselben Helden stehen
        if NEW_IDS.get(r['hero']) not in tag:
            print('passt nicht, übersprungen:', board, r['i'], r['hero'])
            continue
        st = re.search(r'style="([^"]*)"', tag).group(1)
        keep = '; '.join(x.strip() for x in st.split(';') if x.strip().split(':')[0].strip() in ('filter', 'animation', 'z-index', 'will-change'))
        new_st = 'position: absolute; left: %.1fpx; top: %.1fpx; width: %.1fpx; height: %.1fpx; max-width: none; transform: none' % (L, T, W, H)
        if keep:
            new_st += '; ' + keep
        repl[r['i']] = re.sub(r'style="[^"]*"', 'style="%s"' % new_st, tag, count=1)
    out = []
    last = 0
    for k, m in enumerate(tags):
        out.append(s[last:m.start()])
        out.append(repl.get(k, m.group(0)))
        last = m.end()
    out.append(s[last:])
    open(f, 'w').write(''.join(out))
    print(board, len(repl))
