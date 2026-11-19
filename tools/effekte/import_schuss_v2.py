#!/usr/bin/env python3
"""Schusseffekte von ChatGPT (Vorlage_Raw/Schusseffekte_<held>_v<n>/, die neueste) ins Spiel übernehmen: game/fx/<spielname>_<teil>.webp + .json.

Geliefert wird je Champion: <held>_muendung, <held>_geschoss, <held>_einschlag (Sheet + JSON, Schussrichtung im Bild
nach rechts). Das Spiel dreht Effekte so, dass die Bild-Oberkante in Schussrichtung zeigt (shaders/fx_sprite.gdshader),
darum wird jedes Einzelbild um 90° gegen den Uhrzeigersinn gedreht; Anker (x, y) → (y, 1 − x).

Die Größen in der Lieferung passen zu ChatGPTs eigener Vorschau, nicht zur Kamera im Spiel. Die Werte unten sind im Spiel
abgestimmt (Weltmaß, 1 Einheit ≈ 1 m, die Brücke ist gut 9 breit):
  muendung  groesse_m       Kantenlänge des Blitzes (im Spiel × FxSprite.SCALE = 1,2)
  geschoss  groesse_m       Länge der Kachel entlang der Flugrichtung (leuchtspur/bolzen), genau so im Spiel
            feste_hoehe_m   Breite der Kachel quer zur Flugrichtung, genau so im Spiel
  einschlag groesse_m       Kantenlänge des Treffers (im Spiel × 1,2)
Weitere Schlüssel für das Spiel: v2, tempo (Abspieltempo), gerichtet (Treffer dreht sich in Schussrichtung),
darstellung (leuchtspur, bolzen: Streifen fliegt mit; durchschuss: Linie von der Mündung bis zum Ziel),
schleife_bilder (fliegende Geschosse wiederholen nur die ersten n Bilder, der Rest ist das Ausblenden),
laenge_faktor (Linie: Quadlänge = Abstand × 256 / 216, weil Start und Spitze 20 px vom Rand liegen),
deckkraft (Linie: Faktor auf die Deckkraft, Vorgabe 1). Alles mit v2 wird voll deckend gezeichnet (FxSprite).

Aufruf: import_schuss_v2.py <ziel> <held> [<held> …]     z. B. import_schuss_v2.py game/fx dusty iska lynx
"""
import glob, json, os, re, sys
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')

# Lieferordner-Name → Name im Spiel (Helden-Stil in hero.gd)
GAME_ID = {'dusty': 'dusty_jo'}

# Im Spiel abgestimmte Werte je Champion und Teil (überschreiben die Lieferung)
TUNING = {
    'dusty': {
        'muendung': {'groesse_m': 1.15, 'tempo': 1.3},
        'geschoss': {'groesse_m': 3.0, 'feste_hoehe_m': 2.6, 'schleife_bilder': 4},
        'einschlag': {'groesse_m': 1.5, 'tempo': 1.0},
    },
    'iska': {
        'muendung': {'groesse_m': 1.1, 'tempo': 1.3},
        'geschoss': {'groesse_m': 2.0, 'feste_hoehe_m': 2.4, 'schleife_bilder': 4},   # kürzer (Wunsch 18.11.)
        'einschlag': {'groesse_m': 1.4, 'tempo': 1.0},
    },
    'kalle': {
        'muendung': {'groesse_m': 1.15, 'tempo': 1.3},
        'geschoss': {'feste_hoehe_m': 2.8},   # Froststrahl, gespannt wie Voltas Blitzbogen (battle.fire_chain)
        'einschlag': {'groesse_m': 1.3, 'tempo': 1.0},
    },
    'margot': {
        'muendung': {'groesse_m': 1.2, 'tempo': 1.3},
        'geschoss': {'groesse_m': 3.2, 'feste_hoehe_m': 3.0, 'schleife_bilder': 4},   # Bündel aus drei Schrotkugeln
        'einschlag': {'groesse_m': 1.2, 'tempo': 1.0},
    },
    'pip': {
        'muendung': {'groesse_m': 1.0, 'tempo': 1.3},
        'geschoss': {'groesse_m': 2.4, 'feste_hoehe_m': 2.2, 'schleife_bilder': 4},
        'einschlag': {'groesse_m': 1.2, 'tempo': 1.0},
    },
    'fuenkchen': {   # v3: Drachenatem bis zur Vorderkante des Gegners, Flammenbögen um ihn herum
        'muendung': {'groesse_m': 1.1, 'tempo': 1.3},
        'geschoss': {'feste_hoehe_m': 2.4},
        # freie_mitte: Anteil der Kachel zwischen den Flammenbögen (gemessen 55 von 256 px); das Spiel rechnet die
        # Größe je Gegner so, dass die Flammen um ihn herumgehen und ihn nicht verdecken (projectile.gd)
        # laenge_anteil: Kachel in Schussrichtung nur halb so lang wie breit, die Bögen liegen dann eng am Gegner
        'einschlag': {'freie_mitte': 0.21, 'laenge_anteil': 0.5, 'tempo': 1.0},
    },
    'rollo': {
        'muendung': {'groesse_m': 1.2, 'tempo': 1.3},
        'geschoss': {'groesse_m': 2.4, 'feste_hoehe_m': 2.4, 'schleife_bilder': 4},   # Kanonenkugel
        'einschlag': {'groesse_m': 1.4, 'tempo': 1.0},
    },
    'nova': {
        'muendung': {'groesse_m': 1.2, 'tempo': 1.3},
        'geschoss': {'groesse_m': 2.4, 'feste_hoehe_m': 2.4, 'schleife_bilder': 4},   # Schwerkraftkugel
        'einschlag': {'tempo': 0.7},   # Wirbel; Größe kommt vom Schwerkraftfeld (battle.gravity_well)
    },
    'brocken': {   # v2: gemalte Rakete; Körper 155 von 256 px, sichtbar etwa 1,35 m → Kachel 2,23 m (Lieferhinweis)
        'muendung': {'groesse_m': 1.1, 'tempo': 1.3},
        'geschoss': {'groesse_m': 2.23, 'feste_hoehe_m': 2.23, 'schleife_bilder': 4},
    },
    'fritzi': {   # v4: Flammenstrahl bis an den Körperrand, kleiner Treffer am zugewandten Körperrand (battle.flame)
        'muendung': {'groesse_m': 1.0, 'tempo': 1.3},
        'geschoss': {'feste_hoehe_m': 2.2},
        # kontakt: Kachelgröße als Vielfaches des Gegnerdurchmessers (ChatGPTs Vorschau: Kachel 58 px bei Gegnern
        # von gut 45 px); weitere Gegner im Trefferkreis bekommen kontakt_neben davon
        # laenge_anteil: Kachel in Schussrichtung flacher, damit die Flammen unten am Körper bleiben (Gesicht frei)
        'einschlag': {'gerichtet': True, 'kontakt': 1.7, 'kontakt_neben': 0.8, 'laenge_anteil': 0.5, 'tempo': 1.0},
    },
    'lynx': {
        'muendung': {'groesse_m': 1.2, 'tempo': 1.3},
        'geschoss': {'feste_hoehe_m': 2.4},
        'einschlag': {'groesse_m': 1.6, 'tempo': 1.0},
    },
}

KEEP = ('frames', 'cols', 'rows', 'fps', 'loop', 'groesse_m', 'feste_hoehe_m', 'darstellung')


def rotate_sheet(im, cols, rows):
    fw, fh = im.width // cols, im.height // rows
    out = Image.new('RGBA', (fh * cols, fw * rows))
    for r in range(rows):
        for c in range(cols):
            f = im.crop((c * fw, r * fh, (c + 1) * fw, (r + 1) * fh)).rotate(90, expand=True)
            out.paste(f, (c * fh, r * fw))
    return out, fh


def convert(held, dst):
    # neueste Lieferung (Schusseffekte_<held>_v1, _v2, …)
    found = glob.glob(os.path.join(ROOT, 'Vorlage_Raw', 'Schusseffekte_%s_v*' % held))
    src = max(found, key=lambda p: int(re.sub(r'\D', '', p.rsplit('_v', 1)[1]) or 0))
    gid = GAME_ID.get(held, held)
    for teil in ('muendung', 'geschoss', 'einschlag'):
        d = os.path.join(src, '%s_%s' % (held, teil))
        if not os.path.isdir(d):
            # z. B. Brocken: nur Mündung und Rakete, die freigegebene Explosion (brocken_explosion) bleibt
            print('%-22s fehlt in der Lieferung, bleibt wie im Spiel' % ('%s_%s' % (gid, teil)))
            continue
        meta = json.load(open(os.path.join(d, '%s_%s.json' % (held, teil))))
        im = Image.open(os.path.join(d, '%s_%s_sheet.png' % (held, teil))).convert('RGBA')
        cols, rows = int(meta['cols']), int(meta['rows'])
        tune = dict(TUNING.get(held, {}).get(teil, {}))
        # ungedreht: Bild schon so gezeichnet, wie es vor der Kamera stehen soll (Fritzis flacher Bodenkranz)
        straight = tune.pop('ungedreht', False)
        if straight:
            out, px = im, im.width // cols
        else:
            out, px = rotate_sheet(im, cols, rows)
        ax, ay = meta.get('anker', [0.5, 0.5])
        info = {k: meta[k] for k in KEEP if k in meta}
        info['anker'] = [round(ax, 6), round(ay, 6)] if straight else [round(ay, 6), round(1.0 - ax, 6)]
        info['frame_px'] = px
        info['v2'] = True
        if teil == 'geschoss':
            if info.get('darstellung') in ('durchschuss', 'bogen'):
                info['anker'] = [0.5, 0.5]
            else:
                # Spitze vorn: Ursprung an der Spitze (ziel_anker), damit der Streifen hinter dem Geschoss herzieht
                tx, ty = meta.get('ziel_anker', [0.921875, 0.5])
                info['anker'] = [round(ty, 6), round(1.0 - tx, 6)]
            info['laenge_faktor'] = 256.0 / 216.0
        if teil == 'einschlag':
            info['gerichtet'] = True
        info.update(tune)
        name = '%s_%s' % (gid, teil)
        out.save(os.path.join(dst, name + '.webp'), 'WEBP', quality=90, method=6)
        json.dump(info, open(os.path.join(dst, name + '.json'), 'w'))
        print('%-22s %dx%d  %s' % (name, out.width, out.height, {k: info[k] for k in info if k not in ('cols', 'rows', 'fps', 'loop', 'frame_px', 'v2')}))


if __name__ == '__main__':
    os.makedirs(sys.argv[1], exist_ok=True)
    for h in sys.argv[2:]:
        convert(h, sys.argv[1])
