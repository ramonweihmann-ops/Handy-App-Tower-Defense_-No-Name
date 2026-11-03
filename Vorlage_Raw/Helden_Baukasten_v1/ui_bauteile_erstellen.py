from pathlib import Path
import json,shutil,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
UI=ROOT/'ui';UI.mkdir(exist_ok=True)
(ROOT/'figuren').mkdir(exist_ok=True)
(ROOT/'hintergrund').mkdir(exist_ok=True)
(ROOT/'symbole').mkdir(exist_ok=True)

def svg(name,w,h,body,defs=''):
    text=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs>{defs}</defs>{body}</svg>'
    ET.fromstring(text)
    (UI/(name+'.svg')).write_text(text,encoding='utf-8')

def gradient(name,top,bottom):
    return f'<linearGradient id="{name}" x1="0" y1="0" x2="0" y2="1"><stop stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient>'

def panel(name,top,bottom,w=512,h=512,frame=True):
    d=gradient('f',top,bottom)+gradient('g','#fff1a1','#e99116')
    b=f'<rect x="8" y="8" width="{w-16}" height="{h-16}" rx="52" fill="#211448" stroke="#7962ad" stroke-width="12"/>'
    b+=f'<rect x="18" y="18" width="{w-36}" height="{h-36}" rx="44" fill="url(#f)" stroke="url(#g)" stroke-width="10"/>' if frame else f'<rect x="8" y="8" width="{w-16}" height="{h-16}" rx="44" fill="url(#f)"/>'
    b+=f'<path d="M55 33 H{w-65}" fill="none" stroke="#fff8db" stroke-opacity=".65" stroke-width="6" stroke-linecap="round"/>'
    svg(name,w,h,b,d)

for color,a,b in [('violett','#9b4aff','#42218e'),('gold','#ffe57b','#f4a51b'),('cyan','#74d7ff','#368ee5'),('rosa','#ff9bc8','#df4a91')]:panel('portrait_hintergrund_'+color,a,b)

svg('portrait_rahmen_gold',512,512,'<rect x="11" y="11" width="490" height="490" rx="52" fill="none" stroke="#34205d" stroke-width="20"/><rect x="13" y="13" width="486" height="486" rx="49" fill="none" stroke="url(#g)" stroke-width="12"/><path d="M62 22 H450" fill="none" stroke="#fff5c5" stroke-width="4" stroke-linecap="round"/>',gradient('g','#fff5a8','#ec9b20'))
svg('portrait_maske',512,512,'<rect x="27" y="27" width="458" height="458" rx="38" fill="#fff"/>')
panel('kartenkoerper','#6041bb','#24154f',512,900)

for name,a,b in [('banner_gruen','#69ed79','#14983e'),('banner_rot','#ff806a','#d92249')]:
    defs=gradient('f',a,b)+gradient('g','#fff6b8','#efab25')
    body='<rect x="23" y="12" width="978" height="136" rx="63" fill="#302052" stroke="url(#g)" stroke-width="12"/><rect x="30" y="20" width="964" height="120" rx="57" fill="url(#f)"/><path d="M83 26 H941" stroke="#fff9d0" stroke-width="5" stroke-linecap="round"/>'
    for x in [4,960]:
        body+=f'<rect x="{x}" y="58" width="60" height="44" rx="20" fill="#7b689f" stroke="#d0b3cd" stroke-width="5"/><rect x="{x+10}" y="69" width="40" height="22" rx="10" fill="#20e1ed" stroke="#b4ffff" stroke-width="4"/>'
    svg(name,1024,160,body,defs)

svg('zaehler_dunkel',192,96,'<rect x="4" y="4" width="184" height="88" rx="44" fill="#162b42" fill-opacity=".65"/>')
panel('stufe_plakette','#fff0a1','#ffc62d',256,96)
panel('zeit_plakette','#49347f','#24164c',320,96)
for name,a,b in [('knopf_gruen_normal','#b1ff65','#3dce25'),('knopf_gruen_hover','#d0ff9b','#64e63f'),('knopf_gruen_gedrueckt','#54d432','#2ca51b'),('knopf_gesperrt','#4d347b','#23143f')]:
    defs=gradient('f',a,b)
    body=f'<rect x="7" y="9" width="498" height="112" rx="38" fill="{b}" stroke="#674a9c" stroke-width="6"/><rect x="10" y="7" width="492" height="101" rx="36" fill="url(#f)"/><path d="M57 16 H455" stroke="#fff" stroke-opacity=".38" stroke-width="6" stroke-linecap="round"/>'
    svg(name,512,128,body,defs)

svg('fortschritt_schiene',512,80,'<rect x="5" y="5" width="502" height="70" rx="35" fill="#160e34" stroke="#9972c2" stroke-width="6"/>')
for name,a,b in [('gruen','#c4ff8e','#44de30'),('gold','#fff29c','#ffd044'),('cyan','#94eaff','#29b8fc')]:
    svg('fortschritt_'+name,512,80,'<rect x="5" y="5" width="502" height="70" rx="35" fill="url(#f)"/><path d="M37 14 H475" stroke="#fff" stroke-opacity=".4" stroke-width="5" stroke-linecap="round"/>',gradient('f',a,b))

svg('nav_hintergrund',1024,200,'<path d="M0 200 V60 Q0 6 65 6 H959 Q1024 6 1024 60 V200Z" fill="url(#f)" stroke="#6844a6" stroke-width="7"/>',gradient('f','#33266d','#21184c'))
svg('nav_aktiv',192,160,'<rect x="4" y="4" width="184" height="152" rx="35" fill="url(#f)" stroke="#ffdb6b" stroke-width="4"/>',gradient('f','#594076','#30234d'))
svg('kampf_knopf',192,192,'<rect x="4" y="8" width="184" height="180" rx="42" fill="#e9a21e"/><rect x="4" y="4" width="184" height="174" rx="42" fill="url(#f)" stroke="#ffedac" stroke-width="4"/><path d="M35 13 H157" stroke="#fff5c8" stroke-width="5" stroke-linecap="round"/>',gradient('f','#ffe688','#ffc628'))
svg('hinweispunkt',64,64,'<circle cx="32" cy="32" r="27" fill="#ff3c4e" stroke="#fff8ed" stroke-width="7"/><path d="M19 17 Q31 9 44 18" fill="none" stroke="#ffb5bb" stroke-width="5" stroke-linecap="round"/>')
svg('plus',64,64,'<path d="M32 10 V54 M10 32 H54" fill="none" stroke="#b9acdd" stroke-width="13" stroke-linecap="round"/><path d="M32 8 V52 M10 30 H54" fill="none" stroke="#fff" stroke-width="11" stroke-linecap="round"/>')
svg('haekchen',64,64,'<circle cx="32" cy="32" r="30" fill="#fffdf1"/><path d="M18 32 L28 42 L47 22" stroke="#2fba46" stroke-width="9" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')

icons=ROOT.parent/'icons_v1'
if not icons.exists():icons=ROOT.parent/'Icons_v1'
for name in ['nav_shop','nav_heroes','nav_battle','nav_upgrades','nav_base','icon_clock']:
    source=icons/(name+'.png')
    if source.exists():shutil.copy2(source,ROOT/'symbole'/(name+'.png'))
reference=ROOT.parent/'reiter_comic_v1'/'helden_entwurf_v1.png'
if reference.exists():shutil.copy2(reference,ROOT/'helden_design_freigegeben.png')

data={
 'entwurfsflaeche':{'breite':934,'hoehe':1684},
 'aufbau':'Hintergrund, danach skalierbare UI-Flächen, freigestellte Figuren, Text und Fortschritt, zuletzt Navigation. Keine Ausschnitte aus dem freigegebenen Gesamtbild verwenden.',
 'texte_als_ui':True,'schrift':'Vorhandene lizenzierte Spielschrift verwenden; keine Schriftdatei beigelegt.',
 'figuren_format':{'pixel':[512,512],'farbraum':'sRGB','alpha':True,'freier_rand_minimum':32},
 'neunfeld_raster_empfehlung':{'portrait_hintergrund':[48,48,48,48],'kartenkoerper':[48,48,48,48],'portrait_rahmen_gold':[48,48,48,48],'knopf':[42,42,42,42]},
 'freigeschaltet':{'zaehler':'4/7','banner':[88,67,758,120],'portrait_zeile_y':220,'portrait_groesse':[210,230],
  'karten':[{'id':'lynx','name':'LYNX','figur':'figuren/lynx.png','hintergrund':'violett','stufe':3,'karten':40,'karten_ziel':40,'status':'bereit','hinweis':True},
   {'id':'dusty_jo','name':'DUSTY JO','figur':'figuren/dusty_jo.png','hintergrund':'gold','stufe':6,'karten':15,'karten_ziel':25},
   {'id':'iska','name':'ISKA','figur':'figuren/iska.png','hintergrund':'cyan','stufe':5,'karten':7,'karten_ziel':20},
   {'id':'margot','name':'MARGOT','figur':'figuren/margot.png','hintergrund':'rosa','stufe':4,'karten':18,'karten_ziel':20}]},
 'gesperrt':{'zaehler':'3','banner':[42,621,850,104],'karten_zeile_y':760,'karten_groesse':[286,530],
  'karten':[{'id':'volta','name':'VOLTA','figur':'figuren/volta.png','hintergrund':'cyan','karten':2,'karten_ziel':10,'zeit':'5 Std.','plus':True,'aktion':'KAUFEN'},
   {'id':'brocken','name':'BROCKEN','figur':'figuren/brocken.png','hintergrund':'cyan','karten':0,'karten_ziel':10,'bedingung':'Starterpaket · 3 Tage','sperre_saettigung':0,'aktion':'ANSEHEN'},
   {'id':'schleimmutter','name':'SCHLEIMMUTTER','figur':'figuren/schleimmutter_gesperrt.png','hintergrund':'rosa','karten':0,'karten_ziel':10,'bedingung':'Boss Welt 1 besiegen','zusatz':'Level 5 nötig','plus':True,'aktion':'GESPERRT','deaktiviert':True}]},
 'navigation':{'aktiv':'heroes','unterer_rand':0,'symbole':['nav_shop','nav_heroes','nav_battle','nav_upgrades','nav_base']},
 'hinweis':'Koordinaten sind Referenzwerte des Entwurfs, keine fest vorgeschriebene Handyauflösung. Auf kleineren Displays mit Containern/Skalierung anpassen; Labels und Touchflächen lesbar halten.'}
(ROOT/'LAYOUT_UND_BEISPIELDATEN.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('Wiederverwendbare SVG-Bauteile, Symbole und Layoutdaten erstellt.')
