# Farben der gemalten Brücke messen (sRGB 0..1): Fahrbahn, Seitenteile, Leuchtfarbe
import json, sys, numpy as np, colorsys
from PIL import Image
F = ["space_dock","ice_world","desert_outpost","lava_asteroid","nebula_portal","jungle_moon","ocean_world","crystal_planet",
     "storm_giant","scrap_world","cloud_city","spore_world","ghost_moon","temple_planet","black_hole","universums_arena","multiplayer_arena"]
out = {}
for n in F:
    a = np.asarray(Image.open('/home/user/Handy-App-Tower-Defense_-No-Name/game/fields/%s.webp' % n).convert('RGB')).astype(float) / 255
    deck = a[930:1140, 300:480].reshape(-1, 3)
    side = np.concatenate([a[880:1140, 90:200].reshape(-1, 3), a[880:1140, 580:690].reshape(-1, 3)])
    edge = np.concatenate([a[600:1160, 20:300].reshape(-1, 3), a[600:1160, 480:760].reshape(-1, 3)])
    lum = edge.max(1); sat = (edge.max(1) - edge.min(1)) / np.maximum(edge.max(1), 1e-3)
    sel = edge[(lum > 0.75) & (sat > 0.35)]
    glow = sel.mean(0) if len(sel) > 50 else edge[lum > np.percentile(lum, 99)].mean(0)
    hot = edge[lum > np.percentile(lum, 99.7)].mean(0)
    out[n] = {"deck": np.median(deck, 0).round(3).tolist(), "deck_dark": np.percentile(deck, 15, 0).round(3).tolist(),
              "side": np.median(side, 0).round(3).tolist(), "side_light": np.percentile(side, 80, 0).round(3).tolist(),
              "glow": glow.round(3).tolist(), "hot": hot.round(3).tolist(), "glow_n": int(len(sel))}
json.dump(out, open(sys.argv[1], 'w'), indent=1)
for n, v in out.items():
    print(f"{n:18s} deck {v['deck']} side {v['side']} sideL {v['side_light']} glow {v['glow']} ({v['glow_n']}) hot {v['hot']}")
