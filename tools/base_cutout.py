"""Stellt die 30 Gebäude der Raumbasis frei: Unterschied zwischen dem Bild mit Gebäuden und dem Bild
mit leeren Bauplätzen (Vorlage_Raw/Raumbasis_Wege_v1). Ausgabe: game/ui/base/geb_<id>.png (mit Durchsicht,
gleiche Lage wie im Gesamtbild) und layout.json mit den Rechtecken. Aufruf: python3 tools/base_cutout.py"""
import json, os
import numpy as np
from PIL import Image, ImageFilter
from collections import deque
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = os.path.join(ROOT, "Vorlage_Raw", "Raumbasis_Wege_v1")
OUT = os.path.join(ROOT, "game", "ui", "base")
full = np.asarray(Image.open(os.path.join(V, "raumbasis_mit_wegen_vorschau.png")).convert("RGB")).astype(int)
empty = Image.open(os.path.join(V, "raumbasis_leere_bauplaetze.png")).convert("RGB")
idx = json.load(open(os.path.join(V, "GEBAEUDE_INDEX_ORIGINAL.json")))["gebaeude"]
diff = np.abs(full - np.asarray(empty).astype(int)).sum(axis=2)
H, W = diff.shape
layout = {}

def largest(mask):
    h, w = mask.shape
    lab = np.zeros((h, w), int); best = 0; bestn = 0; n = 0
    for y in range(h):
        for x in range(w):
            if mask[y, x] and not lab[y, x]:
                n += 1; q = deque([(y, x)]); lab[y, x] = n; cnt = 0
                while q:
                    cy, cx = q.popleft(); cnt += 1
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        yy, xx = cy + dy, cx + dx
                        if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not lab[yy, xx]:
                            lab[yy, xx] = n; q.append((yy, xx))
                if cnt > bestn:
                    best, bestn = n, cnt
    return lab == best

def fill_holes(mask):
    h, w = mask.shape
    out = np.zeros((h, w), bool); q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if not mask[y, x]: out[y, x] = True; q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if not mask[y, x] and not out[y, x]: out[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < h and 0 <= xx < w and not mask[yy, xx] and not out[yy, xx]:
                out[yy, xx] = True; q.append((yy, xx))
    return ~out

for g in idx:
    a = g["auswahl_px"]; foot = g["fusspunkt_ca_px"]
    x0 = max(0, a["x"] - 4); x1 = min(W, a["x"] + a["breite"] + 4)
    y0 = max(0, a["y"] - 6); y1 = min(H, foot["y"] + 40)
    sub = diff[y0:y1, x0:x1]
    m = sub > 70
    # Nummernschilder (dunkle Plaketten mit weißer Zahl, nur im Bild mit Gebäuden) herausnehmen
    fsub = full[y0:y1, x0:x1].sum(axis=2)
    esub = np.asarray(empty).astype(int)[y0:y1, x0:x1].sum(axis=2)
    plaque = np.zeros_like(m)
    dark = (fsub < 270) & (esub > 330)
    lab_seen = np.zeros_like(dark)
    hh, ww = dark.shape
    for yy in range(hh):
        for xx in range(ww):
            if dark[yy, xx] and not lab_seen[yy, xx]:
                q = deque([(yy, xx)]); lab_seen[yy, xx] = True; pts = []
                while q:
                    cy, cx = q.popleft(); pts.append((cy, cx))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < hh and 0 <= nx < ww and dark[ny, nx] and not lab_seen[ny, nx]:
                            lab_seen[ny, nx] = True; q.append((ny, nx))
                ys = [p[0] for p in pts]; xs = [p[1] for p in pts]
                bw = max(xs) - min(xs) + 1; bh = max(ys) - min(ys) + 1
                if 26 <= bw <= 90 and 8 <= bh <= 36 and bw > bh * 1.4 and len(pts) > bw * bh * 0.35:
                    plaque[max(0, min(ys) - 4):max(ys) + 5, max(0, min(xs) - 4):max(xs) + 5] = True
    m &= ~plaque
    # Stücke schließen, größtes Teil nehmen, Löcher füllen, wieder auf Form bringen
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(9))) > 0
    m = largest(m)
    m = fill_holes(m)
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(5))) > 0
    m &= ~plaque
    alpha = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    rgb = Image.fromarray(full[y0:y1, x0:x1].astype(np.uint8)).convert("RGBA")
    rgb.putalpha(alpha)
    bb = rgb.getbbox()
    rgb = rgb.crop(bb)
    rx, ry = x0 + bb[0], y0 + bb[1]
    rgb.save(os.path.join(OUT, "geb_%s.png" % g["id"]))
    # Bild für das Gebäudefenster: Ausschnitt mit Boden, ohne Schild
    card = Image.fromarray(full[a["y"]:foot["y"] - 16, a["x"]:a["x"] + a["breite"]].astype(np.uint8))
    card.save(os.path.join(OUT, "bild_%s.webp" % g["id"]), quality=90)
    layout[g["id"]] = {"rect": [rx, ry, rgb.width, rgb.height], "foot": [foot["x"], foot["y"]], "name": g["name"]}
    print(g["id"], g["name"], layout[g["id"]]["rect"])
empty.save(os.path.join(OUT, "basis_leer.webp"), quality=92)
json.dump({"size": [W, H], "buildings": layout}, open(os.path.join(OUT, "layout.json"), "w"), ensure_ascii=False, indent=1)
