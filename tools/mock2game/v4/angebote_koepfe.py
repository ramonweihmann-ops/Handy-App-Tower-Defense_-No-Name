#!/usr/bin/env python3
"""Hauptbildschirm (Main-v4): Die Angebots-Knöpfe links haben im Hintergrundbild noch die alten
Heldenköpfe. Legt in jeden Knopf ein Feld mit der Kachelfarbe und dem neuen Heldenbild, Kopf mittig
(gleiche Regel wie helden_koepfe.py), Hut am Kachelrand abgeschnitten, dazu das weiße Plus.
Aufruf: angebote_koepfe.py <mockup-ordner>"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
D = sys.argv[1]
P = os.path.join(D, 'project', 'Main-v4.dc.html')
FACE = {'dusty': (0.506, 0.283, 0.375), 'brocken': (0.755, 0.233, 0.40), 'volta': (0.61, 0.245, 0.41), 'lynx': (0.475, 0.228, 0.40)}
SIZE = {'dusty': (286, 418), 'brocken': (326, 413), 'volta': (298, 395), 'lynx': (347, 400)}
NEW = {'dusty': '49c2c7a7d1fc59eebfae97c1d288d979', 'brocken': '4ad155d8c481666dfa9e641b39621cdd',
       'volta': '4bb4b32b2e55374f73585bcbae4a9684', 'lynx': '947d90c35067f7a7407bad4b65a0bbf6'}
# Knopf -> Held und Kachelfarben (oben, unten), aus dem Hintergrundbild gemessen
TILES = {'Angebot-Lynx.dc.html': ('lynx', '#f59d79', '#c95f8a'), 'Angebot-Volta.dc.html': ('volta', '#6bb8fe', '#2a4fd0'),
         'Starterpaket.dc.html': ('brocken', '#62df63', '#1f9a42'), 'Kartenpaket.dc.html': ('dusty', '#ffbf43', '#e8960f')}
PLUS = ('<svg width="12" height="12" viewBox="0 0 24 24" aria-hidden="true" style="position:absolute;right:4px;top:4px">'
        '<path d="M12 3v18M3 12h18" stroke="#fff" stroke-width="4" stroke-linecap="round"></path></svg>')

s = open(P).read()
for href, (hero, c1, c2) in TILES.items():
    m = re.search(r'(<a href="%s"[^>]*style="[^"]*width: ([\d.]+)px; height: ([\d.]+)px[^"]*">)(.*?)(</a>)' % re.escape(href), s, re.S)
    if not m:
        print('nicht gefunden', href)
        continue
    bw, bh = float(m.group(2)) - 4, float(m.group(3)) - 4
    ex, ey, fw = FACE[hero]
    w0, h0 = SIZE[hero]
    face_w = min(0.66 * bw, 0.66 * bh)
    W = face_w / fw
    H = W * h0 / w0
    L = bw / 2 - ex * W
    T = 0.47 * bh - ey * H
    inner = ('<span data-angebot-kopf="%s" aria-hidden="true" style="position:absolute;left:2px;top:2px;width:%.1fpx;height:%.1fpx;'
             'border-radius:9px;overflow:hidden;background:linear-gradient(180deg,%s,%s);box-shadow:inset 0 2px 0 rgba(255,255,255,0.35)">'
             '<img src="/_blob/%s" alt="" style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;max-width:none">%s</span>'
             % (hero, bw, bh, c1, c2, NEW[hero], L, T, W, H, PLUS))
    s = s[:m.start(4)] + inner + s[m.end(4):]
open(P, 'w').write(s)
print('ok')
