# Schreibt das Mockup „Main-v4.dc.html“ (1 · Abenteuer-Pfad, Comic v4) aus den Ebenen: Positionen aus dem
# Entwurf (852 × 1846) auf 390 × 844 umgerechnet, Knöpfe mit denselben Zielen wie im bisherigen Pfad.
K=390/852
def P(v): return round(v*K,1)
D='/tmp/claude-0/-home-user/5d5708a7-8615-55c4-a499-565014920cdf/scratchpad/artifact-files/0b65aff5-f8dc-494a-b7d6-efdc5c5b6414'
tpl=open(D+'/project/Basislager-Bauplatz.dc.html').read()
head=tpl[:tpl.index('<div style="width: 390px')].replace('<title>Sternwarte</title>','<title>Abenteuer-Pfad</title>')
tail=tpl[tpl.index('</x-dc>'):]
BG='/_blob/baef930e75d8afcfd4c46f8994ec0c7e'; GREEN='/_blob/8cf953a56d499752f60a4d6dbf657c05'; GOLD='/_blob/68fdebed74480985593e3287b3c1e4e1'
LOCK='/_blob/99cb721099e94f3ce0a20deb93b66b40'; HERO='/_blob/9f460bc7bfd2c147ed0a87fe1b39f28e'
o=[]
A=o.append
def hit(tag,attrs,x,y,w,h,inner=''):
    A(f'<{tag} {attrs} style="position: absolute; left: {x}px; top: {y}px; width: {w}px; height: {h}px; padding: 0; border: none; background: transparent; text-decoration: none; display: block">{inner}</{tag}>')
def badge(x,y,s=12):
    return f'<span style="position: absolute; left: {x}px; top: {y}px; width: {s}px; height: {s}px; border-radius: 4px; background: #ff3b30; border: 2px solid #fff4f0; box-sizing: border-box; box-shadow: 0 2px 4px rgba(0,0,0,0.4)"></span>'
def text(x,y,t,font,color,anchor='left',extra=''):
    tr={'left':'translateY(-50%)','center':'translate(-50%,-50%)'}[anchor]
    A(f'<div style="position: absolute; left: {x}px; top: {y}px; transform: {tr}; font: {font}; color: {color}; white-space: nowrap{extra}">{t}</div>')
A(f'<div style="width: 390px; height: 844px; position: relative; overflow: hidden; font-family: Nunito, \'Trebuchet MS\', sans-serif; color: #fff7ea; background: #1b1745">')
A(f'<img src="{BG}" alt="" aria-hidden="true" style="position: absolute; left: 0; top: 0; width: 390px; height: 845px">')
# Kopfleiste
hit('button','aria-label="Profil"',P(20),P(27),P(98),P(98))
text(P(100),P(103),'12','800 11px Nunito, sans-serif','#3a2400','center')
text(P(190),P(76),'25/30','800 12px Nunito, sans-serif','#fff7ea')
text(P(398),P(76),'4.573','800 12px Nunito, sans-serif','#fff7ea')
text(P(603),P(76),'350','800 12px Nunito, sans-serif','#fff7ea')
for lab,cx in [('Energie kaufen',296),('Gold kaufen',500),('Edelsteine kaufen',704)]:
    hit('button',f'aria-label="{lab}"',P(cx-24),P(52),P(48),P(48))
hit('button','aria-label="Einstellungen"',P(756),P(44),P(64),P(64))
# Battle Pass
hit('a','href="#pass" aria-label="Battle Pass"',P(25),P(145),P(803),P(83))
text(P(545),P(176),'Stufe 2','700 14px Fredoka, sans-serif','#3a2000')
text(P(735),P(184),'Abholen!','800 11px Nunito, sans-serif','#fff','center')
# Welt
hit('button','aria-label="Vorherige Welt"',P(210),P(330),P(54),P(56))
hit('button','aria-label="Nächste Welt"',P(590),P(330),P(54),P(56))
text(P(428),P(306),'WELT 1','700 11px Nunito, sans-serif','#e8e2ff','center','; letter-spacing: 0.12em')
A(f'<div style="position: absolute; left: {P(428)-45}px; top: {P(372)}px; width: 90px; transform: translateY(-50%); text-align: center; font: 700 19px/1.05 Fredoka, sans-serif; color: #fff">Schleim-Welt</div>')
# Angebote links
for (href,lab,y,timer,ty) in [('Angebot-Lynx.dc.html','Champion-Angebot Lynx',445,'22 Std.',575),('Angebot-Volta.dc.html','Champion-Angebot Volta',610,'5 Std.',742),
                              ('Starterpaket.dc.html','Starterpaket',775,'3 Tage',907),('Kartenpaket.dc.html','Kartentruhe',940,'Heute',1067)]:
    hit('a',f'href="{href}" aria-label="{lab}"',P(30),P(y),P(117),P(112))
    text(P(90),P(ty),timer,'800 10px Nunito, sans-serif','#fff7ea','center')
# Aktionen rechts
for (tag,attrs,y,b) in [('button','aria-label="Tägliche Belohnung"',430,True),('button','aria-label="Glücksrad"',560,True),('a','href="Missionen.dc.html" aria-label="Missionen"',690,True),
                        ('a','href="#shop" aria-label="Shop"',820,False),('a','href="Spielmodi.dc.html" aria-label="Spielmodi"',945,True)]:
    hit(tag,attrs,P(705),P(y),P(125),P(128),badge(P(785-705),P(438-430)) if b else '')
# Boss-Schloss
A(f'<div aria-label="gesperrt" style="position: absolute; left: {P(520)}px; top: {P(530)}px; width: {P(36)}px; height: {P(46)}px"><img src="{LOCK}" alt="" style="width: 100%; height: 100%"></div>')
# Level-Knoten: drei geschaffte, dann der ausgewählte
gw,gh=144*K,133*K; gcx,gcy=72*K,53*K
for n,(cx,cy),sy,st in [(1,(240,1248),1335,3),(2,(372,1096),1180,2),(3,(565,946),1032,3)]:
    x,y=P(cx),P(cy); h=round(2*(P(sy)-9-y),1); w=50
    A(f'<div data-live="node_done" style="position: absolute; left: {x-w/2}px; top: {y-h/2}px; width: {w}px; height: {h}px"><img src="{GREEN}" alt="" style="position: absolute; left: {round(w/2-gcx,1)}px; top: {round(h/2-gcy,1)}px; width: {round(gw,1)}px; height: {round(gh,1)}px"><span style="position: absolute; left: 0; right: 0; top: {round(h/2-11,1)}px; text-align: center; font: 700 20px/22px Fredoka, sans-serif; color: #fff7ea">{n}</span></div>')
    stars=''.join(f'<span style="color: {"#ffd34d" if i<st else "#8a86b0"}">★</span>' for i in range(3))
    A(f'<div aria-label="{st} Sterne" style="position: absolute; left: {x-22}px; top: {P(sy)-9}px; width: 44px; height: 18px; text-align: center; font: 12px/18px sans-serif; letter-spacing: 1px; text-shadow: 0 1px 0 #6a4a00">{stars}</div>')
x,y=P(323),P(772)
A(f'<div data-live="cur_glow" style="position: absolute; left: {x-55}px; top: {y-55}px; width: 110px; height: 110px; border-radius: 50%; background: radial-gradient(circle, rgba(255,214,90,0.55) 0%, rgba(255,214,90,0.18) 45%, rgba(255,214,90,0) 70%)"></div>')
ow,oh=166*K,170*K; ocx,ocy=83*K,72*K
A(f'<div data-live="node_cur" style="position: absolute; left: {x-32}px; top: {y-32}px; width: 64px; height: 64px"><img src="{GOLD}" alt="" style="position: absolute; left: {round(32-ocx,1)}px; top: {round(32-ocy,1)}px; width: {round(ow,1)}px; height: {round(oh,1)}px"><span style="position: absolute; left: 0; right: 0; top: 17px; text-align: center; font: 700 28px/30px Fredoka, sans-serif; color: #5a2800">4</span></div>')
A(f'<img src="{HERO}" alt="Dusty Jo" data-live="map_hero" style="position: absolute; left: 180px; top: 323px; height: 66px; filter: drop-shadow(0 6px 6px rgba(0,0,0,0.35)); z-index: 5">')
A(f'<div data-live="lvl_tag" style="position: absolute; left: {P(340)-62}px; top: {P(883)-11.5}px; width: 124px; height: 23px; box-sizing: border-box; border-radius: 12px; background: rgba(20,12,48,0.78); border: 1px solid rgba(169,140,255,0.35); text-align: center; font: 800 12px/21px Nunito, sans-serif">Panzer im Schleim</div>')
# Spielen
A(f'<a href="#kampf" style="position: absolute; left: {P(150)}px; top: {P(1428)}px; width: {P(550)}px; height: {P(125)}px; text-decoration: none; display: block"><span style="position: absolute; left: 0; right: 0; top: {P(1515-1428)-7}px; text-align: center; font: 800 10px/14px Nunito, sans-serif; color: #3d1d00; opacity: 0.85" aria-label="Level 4 · 5 Energie">Level 4 · 5 <svg width="10" height="10" viewBox="0 0 24 24" aria-hidden="true"><path d="M13 2 4 14h7l-1 8 9-12h-7z" fill="#3d1d00"></path></svg></span></a>')
# Reiterleiste
for (href,x0,x1,bx) in [('#shop',30,160,0),('#helden',190,320,292),('#upgrades',530,665,632),('#basis',700,830,0)]:
    hit('a',f'href="{href}"',P(x0),P(1700),P(x1-x0),P(146),badge(P(bx-x0)-6,P(1702-1700)) if bx else '')
hit('a','href="#kampf" aria-label="Kampf"',P(355),P(1665),P(140),P(135))
A('</div>')
open(D+'/project/Main-v4.dc.html','w').write(head+'\n'.join(o)+'\n'+tail)
