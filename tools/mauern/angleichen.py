# Farben der Mauer an die Brücke angleichen (Farbübertragung im Lab-Raum, nur auf die Mauer selbst)
# Aufruf: python3 angleichen.py mauer.png feld.webp ausgabe.png [stärke 0..1]
import sys, numpy as np
from PIL import Image
def srgb2lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def lin2srgb(c): return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(np.clip(c, 0, None), 1 / 2.4) - 0.055)
M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
WP = np.array([0.95047, 1.0, 1.08883])
def f(t): return np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16 / 116)
def finv(t): return np.where(t > 0.2069, t ** 3, (t - 16 / 116) / 7.787)
def rgb2lab(rgb):
    xyz = srgb2lin(rgb) @ M.T / WP
    fx, fy, fz = f(xyz[..., 0]), f(xyz[..., 1]), f(xyz[..., 2])
    return np.stack([116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)], -1)
def lab2rgb(lab):
    fy = (lab[..., 0] + 16) / 116
    fx = fy + lab[..., 1] / 500
    fz = fy - lab[..., 2] / 200
    xyz = np.stack([finv(fx), finv(fy), finv(fz)], -1) * WP
    return np.clip(lin2srgb(xyz @ np.linalg.inv(M).T), 0, 1)
wall = np.asarray(Image.open(sys.argv[1]).convert('RGBA')).astype(float) / 255
field = np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(float) / 255
k = float(sys.argv[4]) if len(sys.argv) > 4 else 0.7
ref = rgb2lab(field[900:1160, 60:720].reshape(-1, 3))
a = wall[..., 3] > 0.5
lab = rgb2lab(wall[..., :3])
src = lab[a]
out = src.copy()
# kräftig farbige oder sehr helle Stellen (Neon, Lampen, Kristalle, Flammen) weniger angleichen, damit sie leuchten
chroma = np.sqrt(src[:, 1] ** 2 + src[:, 2] ** 2)
keep = np.clip((chroma - 35) / 40, 0, 0.7) + np.clip((src[:, 0] - 80) / 20, 0, 0.3)
w = k * (1 - np.clip(keep, 0, 0.85))
for c in range(3):
    mu_s, sd_s = src[:, c].mean(), src[:, c].std() + 1e-6
    mu_r, sd_r = ref[:, c].mean(), ref[:, c].std() + 1e-6
    t = (src[:, c] - mu_s) / sd_s * sd_r + mu_r
    out[:, c] = src[:, c] * (1 - w) + t * w
lab[a] = out
rgb = lab2rgb(lab)
# halbdurchsichtige Ränder ebenfalls umfärben
res = wall.copy()
res[..., :3] = np.where(wall[..., 3:4] > 0, rgb, wall[..., :3])
Image.fromarray((res * 255 + 0.5).astype(np.uint8), 'RGBA').save(sys.argv[3])
print('angeglichen', [round(float(x), 1) for x in src.mean(0)], '->', [round(float(x), 1) for x in out.mean(0)], 'Brücke', [round(float(x), 1) for x in ref.mean(0)])
