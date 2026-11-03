#!/usr/bin/env python3
"""Boards „Upgrades · Talente (neu)“ und „Upgrades · Tech-Werft (neu)“ nach den freigegebenen Entwürfen
Vorlage_Raw/Talente_v1 und Vorlage_Raw/Tech_Werft_v1 (je 978 × 1608). Gebaut aus den gelieferten
Einzelteilen (ui_png, ins Artefakt hochgeladen) und den Symbolen aus Icons_v1; Texte, Zahlen,
Fragezeichen und Schild-Ziffern als eigene Textelemente, nichts eingebrannt. Lagen in x aus der
Vorlage (Faktor 390/978), in der Höhe auf 844 Punkte verteilt. Bauteile mit data-up für den Export.
Aufruf: upgrades_v2_boards.py <mockup-ordner>   (Kopf und Stile aus project/Battle-Pass.dc.html)"""
import os, sys

D = sys.argv[1]
P = os.path.join(D, 'project')
SRC = open(os.path.join(P, 'Battle-Pass.dc.html')).read()
TAIL = SRC[SRC.index('</x-dc>'):]
K = 390 / 978

U = {  # Bauteile (Artefakt-Bilder)
    'bereich_angriff': 'd08e1b86a27f4c76582b3d88dc607021', 'bereich_schutz': '3ebc730ef69e808eb131ed18c8eb6211',
    'bereich_technik': '4f55d7b0647d69ed3a6941c948e7edc0', 'detail_box': 'a375871402624047bc3f297fc76792a9',
    'haekchen': 'f828d656d66693e4e5a4f4d285839bf5', 'kampf_knopf': '42a730b23478d8f5d29bcdca4a4a8a67',
    'knopf_gesperrt': '15760d3ad0e7b1fa01bf09c1d2a842dd', 'knopf_gold_normal': 'da4cc806115ef51bf9b82f51702f5b8f',
    'knopf_gruen_normal': '9eec6e317ce90c62c6ec1aa2fa281394', 'knopf_violett_normal': '9149936c490276d84407a6d49ff61783',
    'kopf_leiste': '01bb1b04b85cdf380fe0d89471b49402', 'marke_gold': 'f953d7aebc06e6e40a8c8df54537d4c2',
    'modul_ausgewaehlt': '6638b44d2f0cdcf7bdfb878e1b8d85d2', 'modul_gesperrt': '9904678565e90e297ac290ab75eda406',
    'modul_normal': 'a4706bb085c62f781234f98c911b3f52', 'nav_aktiv': '6858f747f41a4e530567bd68d20e9156',
    'nav_hintergrund': 'a365c3eae4d9d0c6b18ecbe25dfea3a8', 'symbol_regeneration': 'df90a02576c591267a91c17eb64aae58',
    'symbol_schild': '99c603a8b4f4defa8e071525b2ed0a56', 'symbol_schloss': '862a20a3ff2efe03a146e59bedcb11c8',
    'hintergrund': 'cd7d4b2d49bd4f23c5196e587c210ac8', 'talent_freigeschaltet': '21fa57f9e0a5a6a640d6001f1b549220',
    'talent_kopfbereich': '1f738ce79b0ff383a049af892dc69222', 'talent_unbekannt': '29103f2147fc875e8a5b35fde9090665',
    'umschalter_aktiv': 'f9ac1544f18214ccaf349119e24d4875', 'umschalter_grund': 'c7bdb185594557318425439c4f2d2ccd',
    'verbinder_gebogen': '74bb3df583b76b001a52e560f0f0a573', 'verbinder_gerade': '5f795ae51be1e2048dd8e8ae33f0b626',
    'ziehbox': 'd9e4cef0eafc2ee2b08de4903b4fd294', 'ziehbox_titel': 'df9403291d7a2103539dee45d5fb5645',
}
S = {  # Symbole aus Icons_v1 (schon im Artefakt)
    'act_profile': 'c6520c126eaef250cf8c96aab08afb3d', 'act_settings': '611fa89140db6251fef2183951a9139e',
    'booster_medipack': 'dd7054fb54670662847dcdc16282bd60', 'icon_core': 'ef79e5170922359419113508f4fa4451',
    'icon_gems': '0e654f50e6bce23818b52fe089316e93', 'icon_gold': '09671ef380ce59e8e86d5efbf00d4b88',
    'icon_stars': 'f6b25886830b76047864fad5438cf901', 'icon_energy': '7d5fe1a2dacc479ab01f992e73ba4c53',
    'nav_base': 'ddf3200a8de9ae897c5ce73c2b84f6bc', 'nav_battle': 'fb9c6ac51a4e714e85dd643f94f2b256',
    'nav_heroes': 'bba9c40260a4ba0dcb7396b68ea8746c', 'nav_shop': '384538de9e78872298ca6773ce57a8e6',
    'nav_upgrades': '260b46a3b52192d6858b1ee0dc229989',
}


def img(key, x, y, w, h, extra='', up=None, sym=False):
    bid = (S if sym else U)[key]
    tag = ' data-up="%s"' % up if up else ''
    return ('<img src="/_blob/%s" alt="" aria-hidden="true"%s style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;'
            'height:%.1fpx;%s">' % (bid, tag, x, y, w, h, extra))


def shine(key, size):
    src = '/_blob/' + S[key]
    return ('<span aria-hidden="true" style="position:relative;display:inline-block;flex:none;width:%dpx;height:%dpx">'
            '<img src="%s" alt="" style="width:100%%;height:100%%;display:block">'
            '<span class="ic-shine" style="-webkit-mask:url(%s) center/contain no-repeat;mask:url(%s) center/contain no-repeat"></span></span>'
            % (size, size, src, src, src))


def text(t, x, y, w, font, color, align='center', shadow='', extra=''):
    sh = ';text-shadow:%s' % shadow if shadow else ''
    return ('<div style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;text-align:%s;font:%s;color:%s;white-space:nowrap%s;%s">%s</div>'
            % (x, y, w, align, font, color, sh, extra, t))


def head(title):
    return SRC[:SRC.index('</helmet>')].replace('<title>Battle Pass</title>', '<title>%s</title>' % title) + '</helmet>\n'


def page_start():
    return ('<div style="width: 390px; height: 844px; position: relative; overflow: hidden; font-family: Nunito, \'Trebuchet MS\', sans-serif; '
            'color: #fff7ea; background: #1a1450">' + img('hintergrund', -73, 0, 537, 844, 'object-fit:cover'))


def top_bar(res):
    """Kopfleiste wie im Entwurf: Profil mit Stufe, Vorräte mit Plus, Einstellungen"""
    out = ['<button aria-label="Profil" style="position:absolute;left:10px;top:9px;width:44px;height:44px;padding:0;border:none;background:transparent">',
           img('act_profile', 0, 0, 44, 44, sym=True),
           '<span style="position:absolute;right:-4px;bottom:-3px;width:20px;height:20px;border-radius:10px;background:linear-gradient(180deg,#ffe27a,#f0a81f);'
           'border:2px solid #fff;font:700 11px/16px Fredoka, sans-serif;color:#4a2000;text-align:center;box-sizing:border-box">12</span></button>']
    x = 62.0
    for icon, val, w in res:
        out.append('<div style="position:absolute;left:%.1fpx;top:15px;width:%dpx;height:30px;border-radius:15px;background:rgba(10,6,40,0.6);'
                   'border:1.5px solid rgba(169,140,255,0.35);box-sizing:border-box"></div>' % (x, w))
        out.append('<span style="position:absolute;left:%.1fpx;top:18px">%s</span>' % (x + 4, shine(icon, 24) if icon != 'icon_energy' and icon != 'icon_stars' else
                   '<img src="/_blob/%s" alt="" aria-hidden="true" style="display:block;width:24px;height:24px">' % S[icon]))
        out.append(text(val, x + 30, 21, w - 56, '700 14px Fredoka, sans-serif', '#fff7ea', 'left'))
        out.append('<button aria-label="%s kaufen" style="position:absolute;left:%.1fpx;top:18px;width:24px;height:24px;border-radius:12px;padding:0;'
                   'border:1.5px solid #d9ffc8;background:linear-gradient(180deg,#8cf06a,#3fbf3a);box-shadow:0 2px 0 #23802a;'
                   'font:700 18px/20px Fredoka, sans-serif;color:#fff">+</button>' % ({'icon_stars': 'Sterne', 'icon_gold': 'Gold', 'icon_gems': 'Edelsteine',
                                                                                    'icon_energy': 'Energie'}[icon], x + w - 27))
        x += w + 6
    out.append('<button aria-label="Einstellungen" style="position:absolute;left:354px;top:14px;width:32px;height:32px;padding:0;border:none;background:transparent">'
               + img('act_settings', 0, 0, 32, 32, sym=True) + '</button>')
    return '\n'.join(out)


def nav():
    """Untere Leiste aus den Bauteilen, Upgrades aktiv"""
    out = [img('nav_hintergrund', 0, 770, 390, 76, up='nav')]
    items = [('#shop', 'nav_shop', 'Shop', 48.6), ('#helden', 'nav_heroes', 'Helden', 122.8), ('#kampf', None, 'Kampf', 195.0),
             ('#upgrades', 'nav_upgrades', 'Upgrades', 271.2), ('#basis', 'nav_base', 'Basis', 346.0)]
    for href, icon, label, cx in items:
        if icon is None:
            out.append('<a href="%s" aria-label="Kampf" style="position:absolute;left:%.1fpx;top:750px;width:70px;height:90px;text-decoration:none">'
                       % (href, cx - 35) + img('kampf_knopf', 0, 0, 70, 70) + img('nav_battle', 13, 9, 44, 44, sym=True)
                       + text(label, 0, 72, 70, '700 12px Fredoka, sans-serif', '#ffd34d', shadow='0 1px 0 #1a0f3a') + '</a>')
            continue
        active = href == '#upgrades'
        inner = (img('nav_aktiv', 0, -6, 68, 62) if active else '') + img(icon, 15, 0, 38, 38, sym=True) + \
            text(label, 0, 39, 68, '800 11px Nunito, sans-serif', '#fff7ea' if active else '#d9d0ff')
        out.append('<a href="%s" style="position:absolute;left:%.1fpx;top:786px;width:68px;height:58px;text-decoration:none">%s</a>' % (href, cx - 34, inner))
    return '\n'.join(out)


def switch(active):
    """Umschalter TECH-WERFT / TALENTE"""
    x, y, w, h = 59.4, 0, 270.8, 36
    return y, w, h, x


def switcher(y, active):
    x, w, h = 59.4, 270.8, 36.0
    out = [img('umschalter_grund', x, y, w, h, up='switch')]
    ax = x + 4 if active == 'tech' else x + w / 2
    out.append(img('umschalter_aktiv', ax - 2, y + 1, w / 2, h - 2, up='switch_on'))
    out.append('<a href="Upgrades-Tech-Neu.dc.html" style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;text-decoration:none">%s</a>'
               % (x, y, w / 2, h, text('TECH-WERFT', 0, 9, w / 2, '700 14px Fredoka, sans-serif', '#fff' if active == 'tech' else '#e8e2ff')))
    out.append('<a href="Upgrades-Talente-Neu.dc.html" style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;text-decoration:none">%s</a>'
               % (x + w / 2, y, w / 2, h, text('TALENTE', 0, 9, w / 2, '700 14px Fredoka, sans-serif', '#fff' if active == 'talente' else '#e8e2ff')))
    return '\n'.join(out)


# --- Talente ----------------------------------------------------------------------------------
def talente():
    b = [page_start(), top_bar([('icon_stars', '3', 76), ('icon_gold', '4.573', 98), ('icon_gems', '350', 86)])]
    cw, ch = 198 * K, 204 * K
    gy0, gstep = 66.0, 101.0
    known = {0: ('Schnelllader', 'icon_core'), 1: ('Sanitätskoffer', 'booster_medipack')}
    for i in range(16):
        r, c = divmod(i, 4)
        x, y = (76 + 210 * c) * K, gy0 + r * gstep
        if i in known:
            name, icon = known[i]
            b.append('<a href="#talent" data-on="talent" aria-label="%s" style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;text-decoration:none">'
                     % (name, x, y, cw, ch)
                     + img('talent_freigeschaltet', 0, 0, cw, ch, up='card_on')
                     + img('talent_kopfbereich', 2, 2, cw - 4, 20, up='card_head')
                     + text(name, 0, 5, cw, '700 10.5px Fredoka, sans-serif', '#fff', shadow='0 1px 0 #1d6b2a')
                     + img(icon, cw / 2 - 22, 22, 44, 44, sym=True)
                     + text('+', cw - 24, 20, 14, '800 15px Nunito, sans-serif', '#fff', shadow='0 1px 0 #1d6b2a')
                     + text('Stufe 1', 0, ch - 17, cw, '700 12px Fredoka, sans-serif', '#163f12') + '</a>')
        else:
            b.append('<div data-up="card_unknown" style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx">' % (x, y, cw, ch)
                     + img('talent_unbekannt', 0, 0, cw, ch)
                     + text('?', 0, ch / 2 - 21, cw, '700 36px Fredoka, sans-serif', '#d6c8ff', shadow='0 3px 0 #3d2a8a') + '</div>')
    # Ziehbox
    bx, bw, bh = 89 * K, 800 * K, 274 * K
    by = 498.0
    b.append(img('ziehbox', bx, by, bw, bh, up='ziehbox'))
    b.append(img('ziehbox_titel', 195 - 75, by - 12, 150, 24, up='ziehbox_titel'))
    b.append(text('Neues Talent erhalten', 120, by - 8, 150, '700 12.5px Fredoka, sans-serif', '#fff7ea'))
    gw, gh = 361 * K, 105 * K
    b.append('<a href="#oeffnen_video" data-on="draw_ad" style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;text-decoration:none">'
             % (120 * K, by + 20, gw, gh) + img('knopf_gold_normal', 0, 0, gw, gh)
             + text('ÖFFNEN', 0, 7, gw, '700 15px Fredoka, sans-serif', '#5a2a00')
             + '<span style="position:absolute;left:%.1fpx;top:24px;width:16px;height:12px;border-radius:3px;background:#2fae4a;display:grid;place-items:center">'
               '<svg width="8" height="8" viewBox="0 0 10 10"><path d="M2 1l7 4-7 4z" fill="#fff"></path></svg></span>' % (gw / 2 - 22)
             + text('3/3', gw / 2 - 2, 22, 30, '700 13px Fredoka, sans-serif', '#5a2a00', 'left') + '</a>')
    b.append('<a href="#oeffnen_stern" data-on="draw_star" style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;text-decoration:none">'
             % (499 * K, by + 20, 360 * K, gh) + img('knopf_gruen_normal', 0, 0, 360 * K, gh)
             + text('ÖFFNEN', 0, 7, 360 * K, '700 15px Fredoka, sans-serif', '#0f3d12')
             + img('icon_stars', 360 * K / 2 - 16, 23, 15, 15, sym=True)
             + text('1', 360 * K / 2 + 3, 22, 20, '700 13px Fredoka, sans-serif', '#0f3d12', 'left') + '</a>')
    b.append('<a href="#fuenf" data-on="draw_five" style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;text-decoration:none">'
             % (120 * K, by + 67, 739 * K, 90 * K) + img('knopf_violett_normal', 0, 0, 739 * K, 90 * K)
             + text('5 STERNE AUF EINMAL ZIEHEN', 0, 9, 739 * K, '700 14px Fredoka, sans-serif', '#fff', shadow='0 1px 0 #4a1a90') + '</a>')
    b.append(switcher(640, 'talente'))
    b.append(nav())
    b.append('</div>')
    return head('Talente') + '\n'.join(b) + '\n' + TAIL


# --- Tech-Werft -------------------------------------------------------------------------------
def module(cx, cy, state, sym, label=None, mark=None, done=False, up=''):
    w, h = 102.0, 89.0
    key = {'ausgewaehlt': 'modul_ausgewaehlt', 'gesperrt': 'modul_gesperrt'}.get(state, 'modul_normal')
    x, y = cx - w / 2, cy - h / 2
    inner = img(key, 0, 0, w, h)
    if sym == 'schild':
        inner += img('symbol_schild', w / 2 - 22, 10, 44, 49, 'opacity:%s' % ('0.6' if state == 'gesperrt' else '1'))
        inner += text(label, 0, 20, w, '700 19px Fredoka, sans-serif', '#fff', shadow='0 1px 0 #2a4a9a')
    else:
        inner += img('symbol_regeneration', w / 2 - 25, 7, 50, 50, 'opacity:%s' % ('0.6' if state == 'gesperrt' else '1'))
    if state == 'gesperrt':
        inner += img('symbol_schloss', w - 27, 24, 24, 24)
    if mark:
        inner += img('marke_gold', w - 22, -6, 24, 24) + text(mark, w - 22, -3, 24, '700 13px Fredoka, sans-serif', '#4a2000')
    if done:
        inner += img('haekchen', w - 32, h - 38, 26, 26)
    return ('<a href="#modul" data-on="module" data-up="%s" style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;text-decoration:none">%s</a>'
            % (up, x, y, w, h, inner))


def tech():
    b = [page_start(), top_bar([('icon_energy', '25/30', 100), ('icon_gold', '4.573', 90), ('icon_gems', '350', 84)])]
    # Titel
    b.append(img('kopf_leiste', 195 - 105, 62, 210, 33, up='title'))
    b.append(img('symbol_schild', 112, 65, 25, 27))
    b.append(text('SCHUTZ', 140, 66, 140, '700 22px Fredoka, sans-serif', '#fff', 'left', '0 2px 0 #3a1a80'))
    # Bereiche
    for key, label, x, w, icon in (('bereich_angriff', 'ANGRIFF', 22, 96, 'ziel'), ('bereich_schutz', 'SCHUTZ', 141, 110, 'schild'),
                                   ('bereich_technik', 'TECHNIK', 262, 106, 'zahnrad')):
        ic = {'ziel': '<svg width="15" height="15" viewBox="0 0 24 24" style="position:absolute;left:10px;top:7px"><circle cx="12" cy="12" r="8" fill="none" stroke="#ffd34d" stroke-width="2.6"></circle><circle cx="12" cy="12" r="3" fill="#ffd34d"></circle><path d="M12 1v5M12 18v5M1 12h5M18 12h5" stroke="#ffd34d" stroke-width="2.4"></path></svg>',
              'schild': '<img src="/_blob/%s" alt="" style="position:absolute;left:10px;top:5px;width:16px;height:18px">' % U['symbol_schild'],
              'zahnrad': '<svg width="15" height="15" viewBox="0 0 24 24" style="position:absolute;left:10px;top:7px"><path d="M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8zm9 4-2.3-.8-.6-1.5 1.1-2.2-1.7-1.7-2.2 1.1-1.5-.6L13 3h-2l-.8 2.3-1.5.6-2.2-1.1-1.7 1.7 1.1 2.2-.6 1.5L3 11v2l2.3.8.6 1.5-1.1 2.2 1.7 1.7 2.2-1.1 1.5.6L11 21h2l.8-2.3 1.5-.6 2.2 1.1 1.7-1.7-1.1-2.2.6-1.5L21 13z" fill="#fff"></path></svg>'}[icon]
        b.append('<a href="#%s" data-on="area" style="position:absolute;left:%dpx;top:106px;width:%dpx;height:28px;text-decoration:none">' % (label.lower(), x, w)
                 + img(key, 0, 0, w, 28) + ic + text(label, 30, 6, w - 34, '700 13px Fredoka, sans-serif', '#fff', 'left', '0 1px 0 rgba(0,0,0,0.3)') + '</a>')
    # Äste
    for label, cx in (('Schildstärke', 107), ('Regeneration', 284)):
        b.append('<div data-up="branch" style="position:absolute;left:%.1fpx;top:148px;width:112px;height:24px;border-radius:12px;box-sizing:border-box;'
                 'background:rgba(20,30,80,0.75);border:1.5px solid rgba(120,180,255,0.6)"></div>' % (cx - 56))
        b.append(text(label, cx - 56, 151, 112, '700 13px Fredoka, sans-serif', '#e8f2ff'))
    # Verbindungen (hinter den Modulen)
    n3, n2, n1, r1, r2 = (105, 226), (105, 322), (195, 410), (285, 322), (285, 226)
    path = 'M%d %d L%d %d M%d %d L%d %d M%d %d C%d %d, %d %d, %d %d M%d %d C%d %d, %d %d, %d %d' % (
        n3[0], n3[1], n2[0], n2[1], r2[0], r2[1], r1[0], r1[1],
        n1[0], n1[1], n1[0] - 60, n1[1], n2[0], n2[1] + 50, n2[0], n2[1],
        n1[0], n1[1], n1[0] + 60, n1[1], r1[0], r1[1] + 50, r1[0], r1[1])
    b.append('<svg data-up="lines" width="390" height="844" viewBox="0 0 390 844" aria-hidden="true" style="position:absolute;left:0;top:0;pointer-events:none">'
             '<path d="%s" fill="none" stroke="#5a4aa8" stroke-width="8" stroke-linecap="round"></path>'
             '<path d="%s" fill="none" stroke="#a8dcff" stroke-width="4.5" stroke-linecap="round"></path></svg>' % (path, path))
    b.append(module(*n3, 'gesperrt', 'schild', 'III', up='schild_3'))
    b.append(module(*n2, 'ausgewaehlt', 'schild', 'II', mark='3', up='schild_2'))
    b.append(module(*n1, 'normal', 'schild', 'I', done=True, up='schild_1'))
    b.append(module(*r1, 'normal', 'regen', up='regen_1'))
    b.append(module(*r2, 'gesperrt', 'regen', up='regen_2'))
    # Detailbox
    dx, dy, dw, dh = 26.0, 474.0, 338.0, 122.0
    b.append(img('detail_box', dx, dy, dw, dh, up='detail'))
    b.append(img('symbol_schild', dx + 16, dy + 14, 50, 56))
    b.append(text('II', dx + 16, dy + 28, 50, '700 20px Fredoka, sans-serif', '#fff', shadow='0 1px 0 #2a4a9a'))
    b.append('<div style="position:absolute;left:%.1fpx;top:%.1fpx;width:2px;height:52px;background:rgba(220,210,255,0.5);border-radius:1px"></div>' % (dx + 78, dy + 14))
    b.append(text('Schild II', dx + 90, dy + 12, 230, '700 17px Fredoka, sans-serif', '#fff', 'left'))
    b.append(text('Mehr Schildstärke', dx + 90, dy + 34, 230, '700 11.5px Nunito, sans-serif', '#e8e2ff', 'left'))
    b.append(text('Andere Forschungswege bleiben verfügbar', dx + 90, dy + 50, 240, '700 11.5px Nunito, sans-serif', '#e8e2ff', 'left'))
    b.append('<a href="#ausbauen" data-on="upgrade" style="position:absolute;left:%.1fpx;top:%.1fpx;width:204px;height:42px;text-decoration:none">'
             % (195 - 102, dy + 72) + img('knopf_gruen_normal', 0, 0, 204, 42)
             + text('AUSBAUEN', 0, 9, 204, '700 19px Fredoka, sans-serif', '#0f3d12') + '</a>')
    b.append(switcher(624, 'tech'))
    b.append(nav())
    b.append('</div>')
    return head('Tech-Werft') + '\n'.join(b) + '\n' + TAIL


open(os.path.join(P, 'Upgrades-Talente-Neu.dc.html'), 'w').write(talente())
open(os.path.join(P, 'Upgrades-Tech-Neu.dc.html'), 'w').write(tech())
print('ok')
