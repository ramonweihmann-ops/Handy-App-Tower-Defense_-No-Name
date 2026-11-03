#!/usr/bin/env python3
"""Board „Battle Pass (neu, Comic)“ nach der freigegebenen Vorlage
Vorlage_Raw/Battle_Pass_Comic_v1/battle_pass_entwurf_v1.png als echtes Mockup (Texte, Knöpfe,
Kapseln und Route als HTML, damit es sich wie die anderen Boards ins Spiel übernehmen lässt).
Hintergrund: Planeten und Horizont aus der Vorlage (weich ausgeblendet), Rest als Verlauf.
Aufruf: battlepass_board.py <mockup-ordner>   (Kopf und Stile kommen aus project/Battle-Pass.dc.html)"""
import os, sys

D = sys.argv[1]
P = os.path.join(D, 'project')
SRC = open(os.path.join(P, 'Battle-Pass.dc.html')).read()
HEAD = SRC[:SRC.index('</helmet>')].replace('<title>Battle Pass</title>', '<title>Battle Pass · Comic</title>')
HEAD = HEAD.replace('</style>', '''
@keyframes bpglow{0%,100%{box-shadow:0 0 0 3px rgba(111,240,255,.55),0 0 18px 6px rgba(111,240,255,.45)}50%{box-shadow:0 0 0 4px rgba(111,240,255,.8),0 0 26px 10px rgba(111,240,255,.6)}}
@keyframes bpdash{to{stroke-dashoffset:-24}}
</style>''')

B = {'gold': '09671ef380ce59e8e86d5efbf00d4b88', 'gems': '0e654f50e6bce23818b52fe089316e93',
     'cards': '4226ce88963d52c78a7e6a3bfd259f4f', 'stars': 'f6b25886830b76047864fad5438cf901',
     'planet_l': '766ceabaf97cd0f9c3d98e8b82db15f9', 'planet_r': '027800e83b474db4413e66dee163e3af',
     'horizon': 'deda103a05d7f48dc2d72f6e4dad9a73'}


def icon(kind, size):
    src = '/_blob/' + B[kind]
    if kind == 'gold':
        return ('<span aria-hidden="true" style="position:relative;display:inline-block;flex:none;width:%dpx;height:%dpx">'
                '<img src="%s" alt="" style="width:100%%;height:100%%;display:block;filter:drop-shadow(0 2px 2px rgba(0,0,0,.4))">'
                '<span class="ic-shine" style="-webkit-mask:url(%s) center/contain no-repeat;mask:url(%s) center/contain no-repeat"></span></span>'
                % (size, size, src, src, src))
    return ('<img src="%s" alt="" aria-hidden="true" style="display:inline-block;flex:none;width:%dpx;height:%dpx;object-fit:contain;'
            'filter:drop-shadow(0 2px 2px rgba(0,0,0,.4))">' % (src, size, size))


LOCK = ('<svg width="%d" height="%d" viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="10" width="14" height="11" rx="2.5" '
        'fill="%s" stroke="%s" stroke-width="1.5"></rect><path d="M8 10V7a4 4 0 0 1 8 0v3" fill="none" stroke="%s" '
        'stroke-width="2.4"></path><circle cx="12" cy="15.5" r="1.6" fill="%s"></circle></svg>')
CHECK = ('<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10.5" fill="#3fd06a" '
         'stroke="#fff" stroke-width="2"></circle><path d="m7 12.5 3.2 3.2L17 9" fill="none" stroke="#fff" stroke-width="2.6" '
         'stroke-linecap="round" stroke-linejoin="round"></path></svg>')

# Stufen wie in der Vorlage: [frei, premium], Zustand frei: done / ready / locked
STAGES = [
    (('gold', '150'), ('gold', '300'), 'done'),
    (('gems', '10'), ('gems', '20'), 'ready'),
    (('cards', '4'), ('cards', '8'), 'locked'),
    (('stars', '1'), ('stars', '2'), 'locked'),
    (('gold', '150'), ('gold', '300'), 'locked'),
]
Y0, STEP = 322, 74
NODE_X = [195, 195, 195, 195, 195]
WIGGLE = [0, -6, 6, -6, 6]


def capsule(x, y, kind, amount, premium, state):
    w, h = 116, 50
    if premium:
        bg = 'linear-gradient(180deg, rgba(255,186,80,0.34), rgba(160,80,20,0.30))'
        border = '1.5px solid rgba(255,196,84,0.85)'
        glow = '0 0 14px rgba(255,180,60,0.35)'
        lights = '#ffc94a'
    else:
        bg = 'linear-gradient(180deg, rgba(150,140,255,0.30), rgba(60,50,150,0.30))'
        border = '1.5px solid rgba(170,160,255,0.55)'
        glow = '0 0 12px rgba(120,110,255,0.25)'
        lights = '#6ff0ff'
    out = []
    # Plattform darunter
    out.append('<div aria-hidden="true" style="position:absolute;left:%dpx;top:%dpx;width:%dpx;height:14px;border-radius:50%%;'
               'background:radial-gradient(closest-side, rgba(90,70,190,0.95), rgba(40,30,110,0.95));border:1.5px solid rgba(190,170,255,0.6);'
               'box-shadow:0 3px 0 rgba(20,10,60,0.8)"><span style="position:absolute;left:18px;right:18px;top:5px;height:3px;border-radius:2px;'
               'background:repeating-linear-gradient(90deg, %s 0 14px, transparent 14px 34px);opacity:.9"></span></div>'
               % (x + 14, y + h - 10, w - 28, lights))
    out.append('<div style="position:absolute;left:%dpx;top:%dpx;width:%dpx;height:%dpx;border-radius:26px;background:%s;border:%s;'
               'box-shadow:%s, inset 0 2px 0 rgba(255,255,255,0.18);backdrop-filter:blur(2px);display:flex;align-items:center;'
               'justify-content:center;gap:8px;font:700 18px Fredoka, sans-serif;color:#fff;text-shadow:0 2px 0 rgba(20,10,60,0.6)">%s<span>%s</span></div>'
               % (x, y, w, h, bg, border, glow, icon(kind, 36), amount))
    if state == 'done':
        out.append('<span style="position:absolute;left:%dpx;top:%dpx">%s</span>' % (x + w - 16, y - 7, CHECK))
    elif state == 'locked':
        col = ('#ffe27a', '#7a4a00', '#fff3c4', '#7a4a00') if premium else ('#c9d0f0', '#3a4280', '#e8ecff', '#3a4280')
        out.append('<span style="position:absolute;left:%dpx;top:%dpx;filter:drop-shadow(0 2px 2px rgba(0,0,0,.5))">%s</span>'
                   % (x + w - 18, y - 9, LOCK % ((20, 20) + col)))
    if state == 'ready':
        out.append('<a href="#holen" data-on="claim" style="position:absolute;left:%dpx;top:%dpx;width:70px;height:22px;border-radius:11px;'
                   'text-decoration:none;color:#0f3d12;background:linear-gradient(180deg,#b6ff8a 0%%,#5fd83f 60%%,#3fbf3a 100%%);'
                   'box-shadow:0 3px 0 #23802a, inset 0 2px 0 rgba(255,255,255,0.6);display:flex;align-items:center;justify-content:center;'
                   'font:700 13px Fredoka, sans-serif">Holen</a>' % (x + w / 2 - 35, y + h - 16))
    return ''.join(out)


body = []
body.append('<div style="width: 390px; height: 844px; position: relative; overflow: hidden; font-family: Nunito, \'Trebuchet MS\', sans-serif; '
            'color: #fff7ea; background: radial-gradient(120% 60% at 20% 30%, rgba(140,60,200,0.35), rgba(0,0,0,0) 60%), '
            'radial-gradient(90% 50% at 90% 75%, rgba(120,50,190,0.35), rgba(0,0,0,0) 60%), linear-gradient(180deg, #1a1450 0%, #120f3c 45%, #160f46 100%)">')
# Sterne
import random
random.seed(7)
for _ in range(34):
    sx, sy, sr = random.uniform(4, 386), random.uniform(4, 840), random.choice([1, 1, 1.5, 2])
    body.append('<span aria-hidden="true" style="position:absolute;left:%.0fpx;top:%.0fpx;width:%spx;height:%spx;border-radius:50%%;'
                'background:#fff;opacity:%.2f"></span>' % (sx, sy, sr, sr, random.uniform(0.35, 0.9)))
body.append('<img src="/_blob/%s" alt="" aria-hidden="true" style="position:absolute;left:0;top:0;width:66px;height:66px">' % B['planet_l'])
body.append('<img src="/_blob/%s" alt="" aria-hidden="true" style="position:absolute;right:0;top:16px;width:66px;height:86px">' % B['planet_r'])
# Kopf: Wappen, Banner
body.append('<svg width="44" height="40" viewBox="0 0 44 40" aria-hidden="true" style="position:absolute;left:173px;top:4px;filter:drop-shadow(0 3px 2px rgba(0,0,0,.4))">'
            '<path d="M22 2 39 7v12c0 9-7 15-17 19C12 34 5 28 5 19V7z" fill="#e2357a" stroke="#ffd34d" stroke-width="3"></path>'
            '<path d="m22 9 3.2 6.5 7.1 1-5.2 5 1.2 7.1L22 25.3l-6.3 3.3 1.2-7.1-5.2-5 7.1-1z" fill="#ffe27a" stroke="#c88a10" stroke-width="1"></path></svg>')
for sx, sy in ((140, 12), (240, 12)):
    body.append('<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true" style="position:absolute;left:%dpx;top:%dpx">'
                '<path d="M12 1 14.5 9.5 23 12l-8.5 2.5L12 23l-2.5-8.5L1 12l8.5-2.5z" fill="#fff4c0"></path></svg>' % (sx, sy))
body.append('<div style="position:absolute;left:84px;top:34px;width:222px;height:38px;border-radius:19px;'
            'background:linear-gradient(180deg,#7b48e0,#4a22a8);border:3px solid #ffc93a;box-shadow:0 4px 0 #a86a00, 0 8px 18px rgba(0,0,0,.45), inset 0 2px 0 rgba(255,255,255,.3);'
            'display:flex;align-items:center;justify-content:center;font:700 24px Fredoka, sans-serif;letter-spacing:0.03em;color:#fff;'
            'text-shadow:0 2px 0 #2a1070">BATTLE PASS</div>')
for side in (68, 304):
    body.append('<span aria-hidden="true" style="position:absolute;left:%dpx;top:44px;width:18px;height:18px;border-radius:50%%;'
                'background:radial-gradient(circle at 40%% 35%%,#e8ecf8,#8a90b8);border:2px solid #4a3a90"><span style="position:absolute;left:3px;right:3px;top:6px;height:3px;'
                'border-radius:2px;background:#6ff0ff;box-shadow:0 0 6px #6ff0ff"></span></span>' % side)
body.append('<div style="position:absolute;left:0;right:0;top:78px;text-align:center;font:600 15px Fredoka, sans-serif;color:#fff;text-shadow:0 2px 0 #1a0f3a">Saison 1 · Schleim-Welt</div>')
body.append('<div style="position:absolute;left:0;right:0;top:98px;text-align:center;font:700 11px Nunito, sans-serif;color:#b9b4e8">Endet in 24 T · 9 Std</div>')
# Fortschritt
body.append('<div style="position:absolute;left:55px;top:116px;width:280px;height:18px;border-radius:10px;background:rgba(10,6,30,0.7);'
            'border:2px solid #7a5ad8;overflow:hidden"><div style="width:60%;height:100%;border-radius:8px;'
            'background:linear-gradient(180deg,#ffe27a,#f0a81f);box-shadow:inset 0 2px 0 rgba(255,255,255,.5)"></div></div>')
body.append('<div style="position:absolute;left:55px;top:116px;width:168px;height:22px;display:flex;align-items:center;justify-content:center;'
            'font:700 11.5px Fredoka, sans-serif;color:#4a2000">Stufe 2 · 60/100</div>')
# Tägliche Missionen
body.append('<div style="position:absolute;left:26px;top:144px;font:700 15px Fredoka, sans-serif;color:#ffc93a;text-shadow:0 2px 0 #1a0f3a">Tägliche Missionen</div>')
MISSIONS = [('Überstehe 25 Wellen', '1/25 · +50 Pass-Punkte'), ('Wähle 12 Fähigkeitskarten', '0/12 · +40 Pass-Punkte'),
            ('Besiege 1 Boss', '0/1 · +80 Pass-Punkte')]
for k, (t, sub) in enumerate(MISSIONS):
    y = 166 + k * 35
    body.append('<div style="position:absolute;left:22px;top:%dpx;width:346px;height:31px;border-radius:10px;'
                'background:linear-gradient(180deg,rgba(70,50,150,0.75),rgba(40,28,100,0.75));border:1.5px solid rgba(169,140,255,0.45)">'
                '<span aria-hidden="true" style="position:absolute;left:9px;top:8px;width:20px;height:14px;border-radius:3px;background:linear-gradient(180deg,#ffe27a,#f0a81f);'
                'box-shadow:0 1px 0 #a86a00"><svg width="10" height="10" viewBox="0 0 24 24" style="position:absolute;left:5px;top:2px"><path d="m12 2 3 6.3 6.9 1-5 4.8 1.2 6.9L12 17.8 5.9 21l1.2-6.9-5-4.8 6.9-1z" fill="#fff"></path></svg></span>'
                '<div style="position:absolute;left:40px;top:2px;font:600 12.5px Fredoka, sans-serif;color:#fff">%s</div>'
                '<div style="position:absolute;left:40px;top:17px;font:700 9.5px Nunito, sans-serif;color:#b9b4e8">%s</div>'
                '<a href="#abholen" data-on="mission" style="position:absolute;right:6px;top:4px;width:66px;height:21px;border-radius:9px;text-decoration:none;'
                'color:#d8d4f0;background:linear-gradient(180deg,#8a86a8,#6a6690);box-shadow:0 2px 0 #3e3a60;display:flex;align-items:center;justify-content:center;'
                'font:600 11.5px Fredoka, sans-serif">Abholen</a></div>' % (y, t, sub))
# Spaltenköpfe
body.append('<div style="position:absolute;left:44px;top:270px;width:104px;height:24px;border-radius:12px;background:rgba(10,30,60,0.75);'
            'border:2px solid #6ff0ff;box-shadow:0 0 10px rgba(111,240,255,.5);display:flex;align-items:center;justify-content:center;'
            'font:700 13px Fredoka, sans-serif;color:#bdf8ff">Kostenlos</div>')
body.append('<div style="position:absolute;left:242px;top:270px;width:104px;height:24px;border-radius:12px;background:rgba(60,30,10,0.75);'
            'border:2px solid #ffc93a;box-shadow:0 0 10px rgba(255,200,60,.5);display:flex;align-items:center;justify-content:center;'
            'font:700 13px Fredoka, sans-serif;color:#ffd96a">Premium</div>')
# Route
pts = [(NODE_X[k] + WIGGLE[k], Y0 + k * STEP) for k in range(len(STAGES))]
d = 'M %d %d' % pts[0]
for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
    mid = (y0 + y1) / 2
    off = 26 if (y0 // STEP) % 2 == 0 else -26
    d += ' C %d %d, %d %d, %d %d' % (x0 + off, mid - 6, x1 + off, mid + 6, x1, y1)
d += ' C %d %d, %d %d, %d %d' % (pts[-1][0] - 24, pts[-1][1] + 30, 196, pts[-1][1] + 50, 186, 670)
body.append('<svg width="390" height="844" viewBox="0 0 390 844" aria-hidden="true" style="position:absolute;left:0;top:0;pointer-events:none">'
            '<path d="%s" fill="none" stroke="rgba(150,80,255,0.55)" stroke-width="14" stroke-linecap="round"></path>'
            '<path d="%s" fill="none" stroke="#8a4cff" stroke-width="7" stroke-linecap="round"></path>'
            '<path d="%s" fill="none" stroke="#bdf8ff" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="6 6" style="animation:bpdash 1.2s linear infinite"></path></svg>'
            % (d, d, d))
for k, (free, prem, state) in enumerate(STAGES):
    x, y = pts[k]
    body.append(capsule(34, y - 28, free[0], free[1], False, state))
    body.append(capsule(240, y - 28, prem[0], prem[1], True, 'locked'))
    # Verbindung zum Knoten
    body.append('<span aria-hidden="true" style="position:absolute;left:150px;top:%dpx;width:%dpx;height:2px;background:linear-gradient(90deg,rgba(111,240,255,0),rgba(111,240,255,.7))"></span>'
                % (y - 3, x - 168))
    body.append('<span aria-hidden="true" style="position:absolute;left:%dpx;top:%dpx;width:%dpx;height:2px;background:linear-gradient(90deg,rgba(255,200,60,.7),rgba(255,200,60,0))"></span>'
                % (x + 18, y - 3, 238 - x - 18))
    # Knoten auf Plattform
    body.append('<div aria-hidden="true" style="position:absolute;left:%dpx;top:%dpx;width:52px;height:16px;border-radius:50%%;'
                'background:radial-gradient(closest-side,#6a54c8,#3a2a90);border:1.5px solid rgba(190,170,255,.7);box-shadow:0 3px 0 #1e1460">'
                '<span style="position:absolute;left:18px;top:6px;width:16px;height:3px;border-radius:2px;background:#6ff0ff;box-shadow:0 0 5px #6ff0ff"></span></div>'
                % (x - 26, y + 8))
    ring = 'animation:bpglow 1.6s ease-in-out infinite;' if state == 'ready' else ''
    body.append('<div style="position:absolute;left:%dpx;top:%dpx;width:36px;height:34px;border-radius:50%%;'
                'background:radial-gradient(circle at 40%% 30%%,#9dffa8,#2fc25a 60%%,#178a3a);border:2px solid #d8ffe0;'
                'box-shadow:0 4px 0 #0e6a2a;%sdisplay:flex;align-items:center;justify-content:center;font:700 20px Fredoka, sans-serif;'
                'color:#fff;text-shadow:0 2px 0 #0e6a2a">%d</div>' % (x - 18, y - 22, ring, k + 1))
# Horizont
body.append('<img src="/_blob/%s" alt="" aria-hidden="true" style="position:absolute;left:0;top:650px;width:390px;height:24px;opacity:.85">' % B['horizon'])
body.append('<div aria-hidden="true" style="position:absolute;left:-60px;right:-60px;top:668px;height:240px;border-radius:50% 50% 0 0 / 40px 40px 0 0;background:linear-gradient(180deg,#a65ae8 0%,#6a2fc0 12%,#3c1a8a 45%,#1e1050 100%);box-shadow:0 -6px 22px rgba(230,150,255,0.55), inset 0 3px 0 rgba(255,220,255,0.7)"></div>')
# Knöpfe
SPARK = ('<svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 1 14.5 9.5 23 12l-8.5 2.5L12 23l-2.5-8.5L1 12l8.5-2.5z" '
         'fill="#fff7d0" stroke="#c88a10" stroke-width="1"></path></svg>')
body.append('<a href="#premium" data-on="premium" style="position:absolute;left:40px;top:694px;width:310px;height:48px;border-radius:24px;text-decoration:none;'
            'color:#4a2000;background:linear-gradient(180deg,#ffe27a 0%,#ffc93a 60%,#f0a81f 100%);box-shadow:0 5px 0 #a86a00, inset 0 2px 0 rgba(255,255,255,0.6), 0 10px 20px rgba(0,0,0,0.4);'
            'display:flex;align-items:center;justify-content:center;gap:14px;font:700 21px Fredoka, sans-serif">' + SPARK + 'Premium freischalten' + SPARK + '</a>')
body.append('<a href="#alles" data-on="claim_all" style="position:absolute;left:24px;top:760px;width:216px;height:38px;border-radius:19px;text-decoration:none;'
            'color:#fff;background:linear-gradient(180deg,#6f9bff,#3a62e0);box-shadow:0 4px 0 #23408f, inset 0 2px 0 rgba(255,255,255,0.4);'
            'display:flex;align-items:center;justify-content:center;font:700 16px Fredoka, sans-serif;text-shadow:0 2px 0 #23408f">Alles beanspruchen</a>')
body.append('<a href="Main-v4.dc.html" style="position:absolute;left:252px;top:760px;width:114px;height:38px;border-radius:19px;text-decoration:none;'
            'color:#fff;background:linear-gradient(180deg,#8a7fc0,#5a5094);box-shadow:0 4px 0 #3a3270, inset 0 2px 0 rgba(255,255,255,0.3);'
            'display:flex;align-items:center;justify-content:center;font:700 16px Fredoka, sans-serif">Zurück</a>')
body.append('</div>')

TAIL = SRC[SRC.index('</x-dc>'):]
html = HEAD + '</helmet>\n' + '\n'.join(body) + '\n' + TAIL
open(os.path.join(P, 'Battle-Pass-Comic.dc.html'), 'w').write(html)
print('ok', len(html))
