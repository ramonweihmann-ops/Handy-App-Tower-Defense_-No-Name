from pathlib import Path
from html import escape
import base64

R=Path(__file__).resolve().parent
items=[]
def asset(name,x,y,w,h,contain=False,extra=''):
    p=R/name
    mime='image/svg+xml' if p.suffix=='.svg' else 'image/png'
    src='data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode()
    items.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="{src}" preserveAspectRatio="'+('xMidYMid meet' if contain else 'none')+f'" {extra}/>')
def text(s,x,y,size=30,color='#fff',anchor='middle'):
    for k,line in enumerate(s.split('\n')):
        items.append(f'<text x="{x}" y="{y+k*size*1.15}" text-anchor="{anchor}" font-family="Arial, sans-serif" font-weight="bold" font-size="{size}" fill="{color}">{escape(line)}</text>')
def bar(x,y,w,h,v,m,color,label=''):
    asset('ui/fortschritt_schiene.svg',x,y,w,h)
    if v:
        width=max(0,min(w,w*v/m));items.append(f'<svg x="{x}" y="{y}" width="{width}" height="{h}" viewBox="0 0 {width} {h}" overflow="hidden">')
        asset('ui/fortschritt_'+color+'.svg',0,0,w,h);items.append('</svg>')
    if label:text(label,x+w/2,y+h*.70,23)
def button(label,x,y,w,h,disabled=False):
    asset('ui/'+('knopf_gesperrt' if disabled else 'knopf_gruen_normal')+'.svg',x,y,w,h)
    text(label,x+w/2,y+h*.61,30,'#e9d7ff' if disabled else '#183b08')

asset('hintergrund/helden_hintergrund.png',0,0,934,1684)
asset('ui/banner_gruen.svg',82,60,770,124);text('FREIGESCHALTET',407,139,43)
asset('ui/zaehler_dunkel.svg',684,89,124,61);text('4/7',746,132,35)
top=[('lynx','LYNX','violett',3,40,40,'gruen'),('dusty_jo','DUSTY JO','gold',6,15,25,'gold'),('iska','ISKA','cyan',5,7,20,'cyan'),('margot','MARGOT','rosa',4,18,20,'gold')]
for i,(name,label,color,level,val,total,progress) in enumerate(top):
    x=18+i*230
    asset('ui/portrait_hintergrund_'+color+'.svg',x,216,210,230)
    asset('figuren/'+name+'.png',x+2,224,206,210,True)
    asset('ui/portrait_rahmen_gold.svg',x,216,210,230)
    asset('ui/stufe_plakette.svg',x+27,408,156,49);text('Stufe '+str(level),x+105,441,27,'#4a2705')
    text(label,x+105,494,31);bar(x+6,516,198,29,val,total,progress)
    text(f'{val}/{total}'+(' · bereit' if i==0 else ' Karten'),x+105,578,24,'#a4f37b' if i==0 else '#fff')
    if i==0:asset('ui/hinweispunkt.svg',x+158,216,49,49)
asset('ui/banner_rot.svg',34,624,866,111);text('NOCH NICHT FREIGESCHALTET',424,697,33)
asset('ui/zaehler_dunkel.svg',775,647,82,62);text('3',816,691,35)
low=[('volta','VOLTA','cyan','',2,10,'KAUFEN'),('brocken','BROCKEN','cyan','Starterpaket · 3\nTage',0,10,'ANSEHEN'),('schleimmutter_gesperrt','SCHLEIMMUTTER','rosa','Boss Welt 1\nbesiegen',0,10,'GESPERRT')]
for i,(name,label,color,condition,val,total,action) in enumerate(low):
    x=17+i*305
    asset('ui/kartenkoerper.svg',x,759,290,534)
    asset('ui/portrait_hintergrund_'+color+'.svg',x+12,771,266,250)
    asset('figuren/'+name+'.png',x+21,779,248,236,True,'filter="url(#grau)"' if i==1 else '')
    asset('ui/portrait_rahmen_gold.svg',x+12,771,266,250)
    text(label,x+145,1069,24 if i==2 else 32,'#ffe67a')
    if condition:text(condition,x+145,1112,25,'#ffe67a')
    bar(x+23,1130 if i==0 else 1164,244,39,val,total,'cyan',f'{val}/{total}'+(' · Level 5 nötig' if i==2 else ' Karten'))
    button(action,x+15,1211,260,73,i==2)
    if i==0:
        asset('ui/zeit_plakette.svg',x+21,782,150,45);asset('symbole/icon_clock.png',x+24,790,30,30,True);text('5 Std.',x+109,814,23,'#ffe67a')
    if i!=1:asset('ui/plus.svg',x+229,785,35,35)
asset('ui/nav_hintergrund.svg',0,1520,934,164);asset('ui/nav_aktiv.svg',196,1530,172,145)
for i,(name,label) in enumerate(zip(['nav_shop','nav_heroes','nav_battle','nav_upgrades','nav_base'],['Shop','Helden','Kampf','Upgrades','Basis'])):
    x=14+i*185
    if i==2:
        asset('ui/kampf_knopf.svg',x+8,1484,157,157);asset('symbole/'+name+'.png',x+21,1499,129,129,True)
    else:asset('symbole/'+name+'.png',x+29,1531,118,101,True)
    text(label,x+86,1668,27,'#ffe67a' if i in [1,2] else '#fff')
out='<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="934" height="1684" viewBox="0 0 934 1684"><defs><filter id="grau"><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncR type="linear" slope=".73"/><feFuncG type="linear" slope=".73"/><feFuncB type="linear" slope=".73"/></feComponentTransfer></filter></defs>'+''.join(items)+'</svg>'
target=R/'vorschau_zusammengesetzt.svg';target.write_text(out,encoding='utf-8')
print('Vorschau aus den tatsächlichen Einzeldateien aufgebaut.')
