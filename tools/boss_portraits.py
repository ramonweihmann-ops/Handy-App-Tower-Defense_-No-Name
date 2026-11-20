#!/usr/bin/env python3
"""Boss-Porträts fürs Portal im Abenteuer-Pfad (game/ui/bosse/welt_NN.webp), freigegeben 20.11.2026.

Je Welt (GameData.WORLDS) der Boss (letzte Gegnerart der Welt) von vorn, in der Färbung der Welt (eigene Gegner wie
Urwaldriese und Tiefseekrake ungefärbt), gerendert mit game/tests/boss_portrait.gd, dann rund mit violettem Grund wie
im Mockup „Boss je Welt“: 171 × 171 Pixel (57 Punkte × 3).

Aufruf: GODOT=/pfad/zu/godot python3 tools/boss_portraits.py     (braucht xvfb-run)
"""
import os, re, subprocess, tempfile
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
GAME = os.path.join(ROOT, 'game')
OUT = os.path.join(GAME, 'ui', 'bosse')
# Ausschnitt je Modell: Anteil der Figurhöhe von oben, Anteil der Breite (wie bei der Freigabe)
FRAME = {'schleimmutter': (1.0, 0.62), 'koloss': (0.5, 0.5), 'urwaldriese': (0.5, 0.5), 'tiefseekrake': (0.8, 0.62)}
OWN_LOOK = {'urwaldriese', 'tiefseekrake'}
D = 171


def worlds():
    t = open(os.path.join(GAME, 'scripts', 'game_data.gd'), encoding='utf-8').read()
    s = t.index('const WORLDS := ['); e = t.index('\n]', s)
    for m in re.finditer(r'\{"name": "([^"]+)", "kinds": \[([^\]]*)\](.*?)(?=\n\t\{"name"|\Z)', t[s:e], re.S):
        boss = [k.strip().strip('"') for k in m.group(2).split(',')][-1]
        tint = re.search(r'"tint": Color\(([^)]*)\)', m.group(3))
        yield boss, (tint.group(1).replace(' ', '') if tint and boss not in OWN_LOOK else '1,1,1')


def circle(src, dst):
    p = Image.open(src).convert('RGBA')
    bg = Image.new('RGBA', (D, D), (0, 0, 0, 0)); g = ImageDraw.Draw(bg)
    for r in range(D // 2, 0, -1):
        t = r / (D / 2)
        g.ellipse((D // 2 - r, D // 2 - r, D // 2 + r, D // 2 + r), fill=(int(70 + 60 * (1 - t)), int(40 + 30 * (1 - t)), int(140 + 60 * (1 - t)), 255))
    q = p.resize((int(D * 1.08), int(D * 1.08)), Image.LANCZOS)
    tmp = Image.new('RGBA', (D, D), (0, 0, 0, 0)); tmp.paste(q, ((D - q.width) // 2, (D - q.height) // 2 + 6), q)
    bg.alpha_composite(tmp)
    m = Image.new('L', (D * 4, D * 4), 0); ImageDraw.Draw(m).ellipse((0, 0, D * 4 - 1, D * 4 - 1), fill=255)
    bg.putalpha(Image.composite(bg.split()[3], Image.new('L', (D, D), 0), m.resize((D, D), Image.LANCZOS)))
    bg.save(dst, 'WEBP', quality=90, method=6)


def main():
    godot = os.environ.get('GODOT', 'godot')
    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp()
    for i, (boss, tint) in enumerate(worlds(), 1):
        frac, wfrac = FRAME[boss]
        png = os.path.join(tmp, 'w%02d.png' % i)
        subprocess.run(['xvfb-run', '-a', '-s', '-screen 0 1280x1800x24', godot, '--path', GAME, '--resolution', '512x512',
                        '-s', 'tests/boss_portrait.gd', '--', 'res://models/enemies_v2/%s.glb' % boss, png, tint, str(frac), str(wfrac)],
                       check=False, capture_output=True, timeout=120)
        circle(png, os.path.join(OUT, 'welt_%02d.webp' % i))
        print('Welt %2d  %-14s %s' % (i, boss, tint))


if __name__ == '__main__':
    main()
