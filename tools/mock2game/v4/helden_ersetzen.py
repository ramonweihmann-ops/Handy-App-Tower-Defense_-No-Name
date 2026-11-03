#!/usr/bin/env python3
"""Neue Heldenbilder (game/ui/heroes2d, ins Artefakt hochgeladen) in den Mockups einsetzen.
Ersetzt die alten Heldenbilder in allen Menü-Boards: erkannt am Namen (alt) oder, bei Bildern ohne
Namen, am Bild selbst. Kampf-Boards (Rückansicht) und die „bisher“-Boards bleiben. Die neuen Figuren
sind breiter: Breite auf 0,62 × Höhe begrenzt, Figur unten mittig (object-fit), Mitte bleibt.
Aufruf: helden_ersetzen.py <mockup-ordner>   (Ordner mit project/*.dc.html und <id>.webp)"""
import json, os, re, sys
from PIL import Image

D = sys.argv[1]
P = os.path.join(D, 'project')
NEW = {'dusty': '49c2c7a7d1fc59eebfae97c1d288d979', 'iska': '7981378994b2f2ccca2588721a350c70',
       'brocken': '4ad155d8c481666dfa9e641b39621cdd', 'volta': '4bb4b32b2e55374f73585bcbae4a9684',
       'kalle': 'aa343cd8be20c8d242ac0e21cc7814dd', 'margot': 'ae9b5eb64db8b5ab5e944aa05630a200',
       'lynx': '947d90c35067f7a7407bad4b65a0bbf6', 'fritzi': '183ff7e75881cc85745b466c116e08bd'}
# schon neue Bilder (Main-v4, Helden-Meldung)
KEEP_BLOBS = set(NEW.values()) | {'9f460bc7bfd2c147ed0a87fe1b39f28e', '66666d77ba3d3b9a7d3e7d8806df61fb'}
NAMES = {'dusty jo': 'dusty', 'iska': 'iska', 'brocken': 'brocken', 'volta': 'volta', 'kalle': 'kalle',
         "käpt'n margot": 'margot', 'lynx': 'lynx', 'fritzi': 'fritzi'}
SKIP = re.compile(r'^(Main\.dc|Feld-|Kampf-|Alt-Nachladen-|MP-Kampf|Bruecke|Buehne|Ladebildschirm)')
RATIO = 0.62
IMG = re.compile(r'<img src="/_blob/([0-9a-f]+)" alt="([^"]*)"((?: aria-hidden="true")?) style="([^"]*)"')

# Bild -> Held, aus allen Stellen mit Namen
BY_BLOB = {}
for f in os.listdir(P):
    if f.endswith('.dc.html'):
        for m in IMG.finditer(open(os.path.join(P, f)).read()):
            if m.group(2).lower() in NAMES:
                BY_BLOB[m.group(1)] = NAMES[m.group(2).lower()]


def blob_size(bid):
    for f in os.listdir(D):
        if f.startswith(bid):
            return Image.open(os.path.join(D, f)).size
    return None


def fix(m):
    bid, alt, aria, st = m.group(1), m.group(2), m.group(3), m.group(4)
    hero = NAMES.get(alt.lower()) or (BY_BLOB.get(bid) if alt == '' else None)
    if hero is None or bid in KEEP_BLOBS:
        return m.group(0)
    hm = re.search(r'(?<![-\w])height:\s*([\d.]+)px', st)
    if hm and 'object-fit' not in st:
        h = float(hm.group(1))
        sz = blob_size(bid)
        old_w = h * sz[0] / sz[1] if sz else h * 0.4
        w = round(h * RATIO, 1)
        if 'translateX(-50%)' not in st:
            for side in ('left', 'right'):
                sm = re.search(r'(?<![-\w])%s:\s*([-\d.]+)px' % side, st)
                if sm:
                    st = st[:sm.start(1)] + str(round(float(sm.group(1)) + (old_w - w) / 2, 1)) + st[sm.end(1):]
        st = st.rstrip('; ') + '; width: %spx; object-fit: contain; object-position: 50%% 100%%' % w
    return '<img src="/_blob/%s" alt="%s"%s style="%s"' % (NEW[hero], alt, aria, st)


canvas = json.load(open(os.path.join(P, 'canvas.json')))
changed = {}
for board in canvas['order']:
    if SKIP.match(board):
        continue
    f = os.path.join(P, board)
    s = open(f).read()
    count = [0]

    def rep(m):
        out = fix(m)
        if out != m.group(0):
            count[0] += 1
        return out
    n = IMG.sub(rep, s)
    if n != s:
        open(f, 'w').write(n)
        changed[board] = count[0]
print(json.dumps(changed))
