#!/usr/bin/env python3
"""Board „Helden (neu, freigegeben)“ nach dem Baukasten Vorlage_Raw/Helden_Baukasten_v1 (Entwurf 934 × 1684).
Gebaut aus den gelieferten Einzelteilen (Hintergrund, sieben freigestellte Figuren, UI-Bauteile) und den
Navigationssymbolen aus Icons_v1. Namen, Stufen, Kartenstände, Zeiten und Knopftexte sind Textelemente.
Lagen aus der Layoutdatei (Faktor 390/934), in der Höhe etwas gestreckt auf 844 Punkte.
Aufruf: helden_board.py <mockup-ordner>"""
import os, sys

D = sys.argv[1]
P = os.path.join(D, 'project')
SRC = open(os.path.join(P, 'Battle-Pass.dc.html')).read()
TAIL = SRC[SRC.index('</x-dc>'):]
K = 390 / 934
YK = K * 1.16   # Höhe: etwas mehr Abstand, damit das Bild die Handyhöhe füllt

U = {
    'fig_brocken': 'c96f575c352a6dd1cca047e25c9172d6', 'fig_dusty': '6afb7612384c068c71121b674140a5a5',
    'fig_iska': 'f882d5f2db11731146f7e72f44367ce8', 'fig_lynx': 'c0ccefbcb590fb3c4404fac689504cb8',
    'fig_margot': '209e147a62f8ef77853c405925daca1e', 'fig_schleimmutter': 'dbbd7d711a12f14bfc0f6c7613362bff',
    'fig_volta': '3f056da691d957dae47c6ee7748b0f14',
    'banner_gruen': '35d6ad6986f94da87d6b074f65dd5730', 'banner_rot': '3f253230d72c237cee4ef8ce463598e6',
    'f_cyan': 'd2f5c2e211fcc933f0d9162b6aef8a89', 'f_gold': '49dfc1b6a41536220c31b95f2b48adda',
    'f_gruen': '78005d928e325adf54c835a8a3a16d95', 'f_schiene': '8c86b016bc74218814c05f91e1252017',
    'hintergrund': 'dbbe885556c78b1b56e86958dbb4b2d7', 'hinweis': 'ff7108342bf3cb95c16d634fa995ec71',
    'kartenkoerper': '17b2b7cf1cd80e1aa65a2ff8d427296c', 'plus': 'f2ef996b254f7a84aaf51d50db1495c3',
    'p_cyan': 'c351b80fd7d5f52c98706505982e2289', 'p_gold': 'c1a916068dfc6b0bf44b0e30a099c4f2',
    'p_rosa': '6b6b3f79eddc6e648473ea4fd1525ccb', 'p_violett': '670d3d00b477865f6395c6f448d90202',
    'rahmen': '70920a0303dcbca30d73a5969f1cfb83', 'stufe': '329cd1213b2dc92a2de08760e734b5d3',
    'zaehler': 'f41a9e4d955b4bb9b76ca6e19bd51405', 'zeit': 'd50febd455e2b2c5a509068184c353ad',
    'kampf_knopf': '42a730b23478d8f5d29bcdca4a4a8a67', 'knopf_gesperrt': '15760d3ad0e7b1fa01bf09c1d2a842dd',
    'knopf_gruen': '9eec6e317ce90c62c6ec1aa2fa281394', 'nav_aktiv': '6858f747f41a4e530567bd68d20e9156',
    'nav_hintergrund': 'a365c3eae4d9d0c6b18ecbe25dfea3a8',
    'icon_clock': '6fc4e6a92dba79eb70d4cc012895d7bc', 'nav_base': 'ddf3200a8de9ae897c5ce73c2b84f6bc',
    'nav_battle': 'fb9c6ac51a4e714e85dd643f94f2b256', 'nav_heroes': 'bba9c40260a4ba0dcb7396b68ea8746c',
    'nav_shop': '384538de9e78872298ca6773ce57a8e6', 'nav_upgrades': '260b46a3b52192d6858b1ee0dc229989',
}


def img(key, x, y, w, h, extra='', up=None):
    tag = ' data-up="%s"' % up if up else ''
    return ('<img src="/_blob/%s" alt="" aria-hidden="true"%s style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;'
            'height:%.1fpx;%s">' % (U[key], tag, x, y, w, h, extra))


def text(t, x, y, w, font, color, align='center', shadow='', extra=''):
    sh = ';text-shadow:%s' % shadow if shadow else ''
    return ('<div style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;text-align:%s;font:%s;color:%s;white-space:nowrap%s;%s">%s</div>'
            % (x, y, w, align, font, color, sh, extra, t))


def portrait(x, y, w, h, bg, fig, grey=False):
    """Bildfeld: Farbfläche, Figur (oberer Körper groß, unten abgeschnitten), Goldrahmen darüber"""
    f = 'filter:grayscale(1) brightness(0.85);' if grey else ''
    fw = w * 1.12
    return ('<div data-up="portrait" style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;border-radius:%.1fpx;overflow:hidden">'
            % (x, y, w, h, w * 0.12)
            + img(bg, 0, 0, w, h) + img(fig, (w - fw) / 2, h * 0.02, fw, fw, f) + '</div>'
            + img('rahmen', x - 1, y - 1, w + 2, h + 2))


def bar(x, y, w, h, frac, fill):
    out = img('f_schiene', x, y, w, h)
    if frac > 0:
        out += ('<div style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;overflow:hidden">' % (x, y, w * frac, h)
                + img(fill, 0, 0, w, h) + '</div>')
    return out


def nav():
    out = [img('nav_hintergrund', 0, 770, 390, 76, up='nav')]
    items = [('#shop', 'nav_shop', 'Shop', 48.6), ('#helden', 'nav_heroes', 'Helden', 122.8), ('#kampf', None, 'Kampf', 195.0),
             ('#upgrades', 'nav_upgrades', 'Upgrades', 271.2), ('#basis', 'nav_base', 'Basis', 346.0)]
    for href, icon, label, cx in items:
        if icon is None:
            out.append('<a href="%s" aria-label="Kampf" style="position:absolute;left:%.1fpx;top:750px;width:70px;height:90px;text-decoration:none">'
                       % (href, cx - 35) + img('kampf_knopf', 0, 0, 70, 70) + img('nav_battle', 13, 9, 44, 44)
                       + text(label, 0, 72, 70, '700 12px Fredoka, sans-serif', '#ffd34d', shadow='0 1px 0 #1a0f3a') + '</a>')
            continue
        active = href == '#helden'
        inner = (img('nav_aktiv', 0, -6, 68, 62) if active else '') + img(icon, 15, 0, 38, 38) + \
            text(label, 0, 39, 68, '800 11px Nunito, sans-serif', '#ffd34d' if active else '#fff7ea')
        out.append('<a href="%s" style="position:absolute;left:%.1fpx;top:786px;width:68px;height:58px;text-decoration:none">%s</a>' % (href, cx - 34, inner))
    return '\n'.join(out)


def board():
    b = ['<div style="width: 390px; height: 844px; position: relative; overflow: hidden; font-family: Nunito, \'Trebuchet MS\', sans-serif; '
         'color: #fff7ea; background: #1a1450">' + img('hintergrund', -39, 0, 468, 844, 'object-fit:cover')]
    # Bereich „Freigeschaltet“
    bx, by, bw, bh = 88 * K, 67 * YK, 758 * K, 120 * K
    b.append(img('banner_gruen', bx, by, bw, bh, up='banner'))
    b.append(text('FREIGESCHALTET', bx, by + bh / 2 - 13, bw - 70, '700 21px Fredoka, sans-serif', '#fff', shadow='0 2px 0 #1d6b2a'))
    b.append(img('zaehler', bx + bw - 78, by + bh / 2 - 12, 48, 24) + text('4/7', bx + bw - 78, by + bh / 2 - 10, 48, '700 15px Fredoka, sans-serif', '#fff'))
    OPEN = [('lynx', 'LYNX', 'p_violett', 3, 40, 40, 'f_gruen', True), ('dusty', 'DUSTY JO', 'p_gold', 6, 15, 25, 'f_gold', False),
            ('iska', 'ISKA', 'p_cyan', 5, 7, 20, 'f_cyan', False), ('margot', 'MARGOT', 'p_rosa', 4, 18, 20, 'f_gold', False)]
    pw, ph = 210 * K, 230 * K
    py = 220 * YK
    for i, (hid, name, bg, lvl, have, need, fill, ready) in enumerate(OPEN):
        x = (26 + 224 * i) * K
        b.append('<a href="Artboard-seqx-c6i2.dc.html" aria-label="%s" style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx"></a>'
                 % (name, x, py, pw, ph + 60))
        b.append(portrait(x, py, pw, ph, bg, 'fig_' + hid))
        b.append(img('stufe', x + pw / 2 - 31, py + ph - 14, 62, 23))
        b.append(text('Stufe %d' % lvl, x + pw / 2 - 31, py + ph - 10, 62, '700 11.5px Fredoka, sans-serif', '#4a2000'))
        if ready:
            b.append(img('hinweis', x + pw - 13, py - 5, 18, 18))
        b.append(text(name, x - 6, py + ph + 13, pw + 12, '700 14px Fredoka, sans-serif', '#fff', shadow='0 2px 0 #1a0f3a'))
        b.append(bar(x + 2, py + ph + 33, pw - 4, 11, have / need, fill))
        b.append(text('%d/%d · bereit' % (have, need) if ready else '%d/%d Karten' % (have, need), x - 6, py + ph + 47, pw + 12,
                      '800 10.5px Nunito, sans-serif', '#7dff8a' if ready else '#e8e2ff'))
    # Bereich „Noch nicht freigeschaltet“
    rx, ry, rw, rh = 42 * K, 621 * YK, 850 * K, 104 * K
    b.append(img('banner_rot', rx, ry, rw, rh, up='banner'))
    b.append(text('NOCH NICHT FREIGESCHALTET', rx, ry + rh / 2 - 11, rw - 60, '700 17px Fredoka, sans-serif', '#fff', shadow='0 2px 0 #7a1020'))
    b.append(img('zaehler', rx + rw - 64, ry + rh / 2 - 11, 40, 22) + text('3', rx + rw - 64, ry + rh / 2 - 9, 40, '700 14px Fredoka, sans-serif', '#fff'))
    LOCKED = [('volta', 'VOLTA', 'p_cyan', 2, 10, None, '5 Std.', 'KAUFEN', False),
              ('brocken', 'BROCKEN', 'p_cyan', 0, 10, 'Starterpaket · 3 Tage', None, 'ANSEHEN', True),
              ('schleimmutter', 'SCHLEIMMUTTER', 'p_rosa', 0, 10, 'Boss Welt 1 besiegen', None, 'GESPERRT', False)]
    cw, ch = 286 * K, 530 * K
    cy = 760 * YK
    for i, (hid, name, bg, have, need, cond, zeit, action, grey) in enumerate(LOCKED):
        x = (19 + 305 * i) * K
        b.append(img('kartenkoerper', x, cy, cw, ch, up='card_locked'))
        ix, iy, iw, ih = x + 6, cy + 6, cw - 12, 100
        b.append(portrait(ix, iy, iw, ih, bg, 'fig_' + hid, grey))
        if zeit:
            b.append(img('zeit', ix + 3, iy + 4, 54, 17) + img('icon_clock', ix + 7, iy + 6, 12, 12)
                     + text(zeit, ix + 21, iy + 6, 34, '800 9.5px Nunito, sans-serif', '#fff', 'left'))
        if hid != 'brocken':
            b.append(img('plus', ix + iw - 19, iy + 3, 16, 16))
        b.append(text(name, x, cy + 114, cw, '700 %s Fredoka, sans-serif' % ('12px' if len(name) > 10 else '15px'), '#ffe27a', shadow='0 2px 0 #3a1a80'))
        if cond:
            b.append('<div style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;text-align:center;font:800 10.5px/1.25 Nunito, sans-serif;color:#ffd34d">%s</div>'
                     % (x + 8, cy + 134, cw - 16, cond.replace(' · 3', ' ·&nbsp;3')))
        if have > 0:
            b.append(bar(x + 10, cy + 160, cw - 20, 14, have / need, 'f_cyan'))
            b.append(text('%d/%d Karten' % (have, need), x + 10, cy + 160, cw - 20, '800 10px Nunito, sans-serif', '#fff'))
        else:
            label = '0/%d · Level 5 nötig' % need if hid == 'schleimmutter' else '0/%d Karten' % need
            b.append(img('zaehler', x + 10, cy + 160, cw - 20, 16) + text(label, x + 10, cy + 161, cw - 20, '800 10px Nunito, sans-serif', '#fff'))
        key = 'knopf_gesperrt' if action == 'GESPERRT' else 'knopf_gruen'
        col = '#d8d4f0' if action == 'GESPERRT' else '#0f3d12'
        b.append('<a href="#%s" data-on="hero_%s" style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;height:30px;text-decoration:none">'
                 % (action.lower(), hid, x + 8, cy + 182, cw - 16) + img(key, 0, 0, cw - 16, 30)
                 + text(action, 0, 6, cw - 16, '700 15px Fredoka, sans-serif', col) + '</a>')
    b.append(nav())
    b.append('</div>')
    head = SRC[:SRC.index('</helmet>')].replace('<title>Battle Pass</title>', '<title>Helden</title>') + '</helmet>\n'
    return head + '\n'.join(b) + '\n' + TAIL


open(os.path.join(P, 'Helden-Neu.dc.html'), 'w').write(board())
print('ok')
