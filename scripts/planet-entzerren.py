#!/usr/bin/env python3
"""Brücke eines Planetenbilds auf die Soll-Fahrbahn bringen: innen Perspektive, Seiten je Zeile gestreckt,
Boden ab Brückenende unverändert (nur senkrecht angepasst). Aufruf: entzerren.py quelle ziel tlx tly trx try blx bly brx bry"""
import sys, cv2, numpy as np
src = cv2.imread(sys.argv[1]); out_path = sys.argv[2]
tl, tr, bl, br = [tuple(map(float, sys.argv[i:i + 2])) for i in (3, 5, 7, 9)]
S = np.float32([tl, tr, br, bl]); T = np.float32([[280, 294], [500, 294], [716, 1158], [64, 1158]])
Hi = cv2.getPerspectiveTransform(T, S)
W, H = 780, 1688
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
def inv(x, y):
    d = Hi[2, 0] * x + Hi[2, 1] * y + Hi[2, 2]
    return (Hi[0, 0] * x + Hi[0, 1] * y + Hi[0, 2]) / d, (Hi[1, 0] * x + Hi[1, 1] * y + Hi[1, 2]) / d
mx, my = inv(xs, ys)
xl_t = 280 - (ys - 294) / 4; xr_t = 500 + (ys - 294) / 4
xl_s, yl_s = inv(xl_t, ys); xr_s, yr_s = inv(xr_t, ys)
left = xs < xl_t; right = xs > xr_t
mx = np.where(left, xs / np.maximum(xl_t, 1) * np.clip(xl_s, 0, W - 1), mx); my = np.where(left, yl_s, my)
xr_c = np.clip(xr_s, 0, W - 1)
mx = np.where(right, xr_c + (xs - xr_t) / np.maximum(W - 1 - xr_t, 1) * (W - 1 - xr_c), mx); my = np.where(right, yr_s, my)
# Himmel über der Brücke: je Spalte senkrecht gestreckt (keine Streifen am oberen Rand)
top = 294
mx[:top] = mx[top]; my[:top] = ys[:top] / top * my[top]
up = cv2.remap(src, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
ybot = int(round((bl[1] + br[1]) / 2))
up[1158:] = cv2.resize(src[ybot:H], (W, H - 1158), interpolation=cv2.INTER_AREA)
cv2.imwrite(out_path, up)
