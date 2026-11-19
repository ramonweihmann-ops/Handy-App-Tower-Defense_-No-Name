#!/usr/bin/env python3
"""App-Symbol aus der freigegebenen Lieferung (Vorlage_Raw/App_Logo_v2, Variante B) ins Spiel übernehmen.

  game/icon.png                    512 px, Symbol des Projekts (Fenster, Web)
  game/icons/app_192.png           klassisches Android-Symbol
  game/icons/app_vordergrund_432   Android-Vordergrund mit dem vorderen Portalbogen (weicher Übergang, Wunsch ChatGPT)
  game/icons/app_hintergrund_432   Android-Hintergrund (Portal)
  game/icons/app_einfarbig_432     Android 13+ „Designsymbole“: weiße Umrisse von Schleimmutter und Dusty Jo, sonst
                                   zeigt Android dort das Godot-Logo. Dunkle Stellen (Augen, Mund, Hutband) bleiben
                                   frei, ein schmaler Spalt trennt den Helden vom Monster.

Aufruf: python3 tools/app_symbol.py
"""
import os
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC = os.path.join(ROOT, 'Vorlage_Raw', 'App_Logo_v2')
GAME = os.path.join(ROOT, 'game')


def monochrome(fg):
    sil = np.array(fg.split()[3]) > 200
    sil = ndimage.median_filter(sil, 5)
    hue = np.array(fg.convert('RGB').convert('HSV'))[:, :, 0]
    # Held: Hut, Gesicht, Jacke und Halstuch im Orange-/Braunbereich; das Monster ist pink und lila
    hero = ndimage.binary_opening((hue >= 3) & (hue <= 40) & sil, iterations=2)
    lab, n = ndimage.label(hero)
    hero = lab == (np.argmax(ndimage.sum(hero, lab, range(1, n + 1))) + 1)
    hero = ndimage.binary_fill_holes(ndimage.binary_closing(hero, iterations=4))
    ring = ndimage.binary_dilation(hero, iterations=4) & ~hero
    dark = ndimage.median_filter(np.array(ImageOps.grayscale(fg.convert('RGB'))) < 50, 3)
    m = ndimage.binary_opening(sil & ~dark & ~ring, iterations=1)
    mask = Image.fromarray((m * 255).astype('uint8'))
    crop = mask.crop(mask.getbbox())
    # Designsymbole zeigen nur die innere Fläche (66 von 108 dp): Figur 250 px breit, mittig
    f = 250 / crop.width
    crop = crop.resize((round(crop.width * f), round(crop.height * f)), Image.LANCZOS)
    out = Image.new('RGBA', (432, 432), (255, 255, 255, 0))
    out.paste(Image.new('RGBA', crop.size, (255, 255, 255, 255)),
              ((432 - crop.width) // 2, (432 - crop.height) // 2 + 6), crop)
    return out


def main():
    os.makedirs(os.path.join(GAME, 'icons'), exist_ok=True)
    Image.open(os.path.join(SRC, 'B_1024.png')).convert('RGBA').resize((512, 512), Image.LANCZOS) \
        .save(os.path.join(GAME, 'icon.png'))
    Image.open(os.path.join(SRC, 'B_192.png')).convert('RGBA').save(os.path.join(GAME, 'icons', 'app_192.png'))
    fg = Image.open(os.path.join(SRC, 'B_vordergrund_432.png')).convert('RGBA')
    fg.save(os.path.join(GAME, 'icons', 'app_vordergrund_432.png'))
    Image.open(os.path.join(SRC, 'B_hintergrund_432.png')).convert('RGBA') \
        .save(os.path.join(GAME, 'icons', 'app_hintergrund_432.png'))
    monochrome(fg).save(os.path.join(GAME, 'icons', 'app_einfarbig_432.png'))
    print('App-Symbol übernommen: game/icon.png, game/icons/app_*.png')


if __name__ == '__main__':
    main()
