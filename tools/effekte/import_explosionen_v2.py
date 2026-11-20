#!/usr/bin/env python3
"""Freigegebene Trefferanimationen (Vorlage_Raw/Explosionen_v2/, ChatGPT, Freigabe 20.11.2026) ins Spiel übernehmen.

  brocken/brocken_einschlag_sheet.png → game/fx/brocken_explosion.webp + .json   (battle.explode)
  rollo/rollo_einschlag_sheet.png     → game/fx/rollo_einschlag.webp + .json     (Projectile.play_impact)
  nova/nova_einschlag_sheet.png       → game/fx/nova_einschlag.webp + .json      (battle.gravity_well)

Blätter unverändert, verlustfrei als WebP mit geradem Alpha; einmal mit 24 fps, volle Deckkraft, ungedreht zur Kamera.
Die JSON der Lieferung wird übernommen und um die im Spiel abgestimmten Werte ergänzt:
  tempo            Abspieltempo (1.0 = die freigegebenen 24 fps; ersetzt die alten Aufrufwerte 1.15 / 1.5 / 0.7)
  ausblenden_s     zusätzliches Ausblenden am Ende (0: die Bildfolge blendet selbst aus)
  groesse_m        Kachelgröße für Einzeltreffer (Rollo), vor FxSprite.SCALE
  kachel_je_radius, kachel_min_m, kachel_max_m
                   Flächentreffer (Brocken, Nova): Kachel = Radius × kachel_je_radius in Metern, begrenzt, damit große
                   Radien (Superfähigkeit, Meister) die Gegner nicht zudecken. Schaden und Radius bleiben unverändert.
Maß aus der freigegebenen Vorschau (390 × 844): die Brücke ist auf Höhe der Gegner etwa 300 px = gut 9 m breit, also
etwa 32 px je Meter. Vorschau-Kacheln: Brocken 110 px (3,4 m bei Raketenradius 2,2), Rollo 88 px (2,75 m),
Nova 98 px (3,05 m bei Feldradius 1,6).

Aufruf: python3 tools/effekte/import_explosionen_v2.py
"""
import json, os
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
SRC = os.path.join(ROOT, 'Vorlage_Raw', 'Explosionen_v2')
DST = os.path.join(ROOT, 'game', 'fx')

TUNING = {
    'brocken': {'ziel': 'brocken_explosion', 'kachel_je_radius': 1.55, 'kachel_min_m': 1.4, 'kachel_max_m': 3.9},
    'rollo': {'ziel': 'rollo_einschlag', 'groesse_m': round(2.75 / 1.2, 3)},
    'nova': {'ziel': 'nova_einschlag', 'kachel_je_radius': 1.9, 'kachel_min_m': 1.6, 'kachel_max_m': 3.8},
}
KEEP = ('frames', 'cols', 'rows', 'fps', 'loop', 'anker', 'frame_px', 'deckend', 'groesse_m', 'gerichtet')

for held, tune in TUNING.items():
    meta = json.load(open(os.path.join(SRC, held, '%s_einschlag.json' % held)))
    im = Image.open(os.path.join(SRC, held, '%s_einschlag_sheet.png' % held)).convert('RGBA')
    assert im.size == (1024, 768), im.size
    name = tune['ziel']
    im.save(os.path.join(DST, name + '.webp'), 'WEBP', lossless=True, method=6, exact=True)
    info = {k: meta[k] for k in KEEP if k in meta}
    info.update({'deckend': True, 'gerichtet': False, 'loop': False, 'tempo': 1.0, 'ausblenden_s': 0.0,
                 'quelle': 'Vorlage_Raw/Explosionen_v2/%s' % held})
    info.update({k: v for k, v in tune.items() if k != 'ziel'})
    json.dump(info, open(os.path.join(DST, name + '.json'), 'w'), ensure_ascii=False)
    print('%-18s %s' % (name, {k: info[k] for k in info if k not in ('cols', 'rows', 'frame_px', 'quelle')}))
