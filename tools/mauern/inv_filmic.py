# Bild so vorverzerren, dass es nach Godots Filmic-Tonemapping (weiß = 1) wieder wie gerendert aussieht
import sys, numpy as np
from PIL import Image
A, Bc, C, D, E, F = 0.22 * 4, 0.30 * 2, 0.10, 0.20, 0.01, 0.30
def f(x):
    return (x * (A * x + C * Bc) + D * E) / (x * (A * x + Bc) + D * F) - E / F
W = f(1.0)
xs = np.linspace(0, 1, 4096)
ys = f(xs) / W
def inv(y):
    return np.interp(y, ys, xs)
def to_lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def to_srgb(c):
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)
im = np.asarray(Image.open(sys.argv[1]).convert('RGBA')).astype(np.float64) / 255.0
rgb = to_srgb(inv(to_lin(im[..., :3])))
out = np.concatenate([rgb, im[..., 3:]], axis=2)
Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGBA').save(sys.argv[2])
print('ok', f(0.5) / W)
