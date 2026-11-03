from pathlib import Path
import json,shutil,xml.etree.ElementTree as ET

R=Path(__file__).resolve().parent
U=R/'ui';U.mkdir(exist_ok=True)
(R/'hintergrund').mkdir(exist_ok=True)
(R/'symbole').mkdir(exist_ok=True)
def grad(a,b):return f'<linearGradient id="f" x1="0" y1="0" x2="0" y2="1"><stop stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>'
def save(name,w,h,body,defs=''):
    data=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs>{defs}</defs>{body}</svg>'
    ET.fromstring(data);(U/(name+'.svg')).write_text(data,encoding='utf-8')
def pill(name,a,b,stroke='#7658ac',w=512,h=128):
    body=f'<rect x="5" y="9" width="{w-10}" height="{h-14}" rx="{h*.43}" fill="{b}"/><rect x="5" y="5" width="{w-10}" height="{h-17}" rx="{h*.43}" fill="url(#f)" stroke="{stroke}" stroke-width="4"/><path d="M{h*.4} 13 H{w-h*.4}" fill="none" stroke="#fff" stroke-opacity=".24" stroke-width="4" stroke-linecap="round"/>'
    save(name,w,h,body,grad(a,b))
for name,a,b in [('bereich_angriff','#ff849e','#d14d75'),('bereich_schutz','#55c7fa','#1677cc'),('bereich_technik','#bb78ed','#7144b6'),('umschalter_aktiv','#c585ff','#8f3ee4')]:pill(name,a,b)
pill('kopf_leiste','#a56cf0','#4c2694',w=1024,h=160)
pill('umschalter_grund','#5e3a90','#2b1c50',w=1024,h=128)
save('detail_box',1024,340,'<rect x="8" y="8" width="1008" height="324" rx="54" fill="url(#f)" stroke="#ae78e7" stroke-width="6"/>',grad('#4c2d81','#281947'))
for name,a,b,edge in [('modul_normal','#875ad4','#493079','#8d71bd'),('modul_ausgewaehlt','#9461eb','#52358d','#ffdc6b'),('modul_gesperrt','#6e5c99','#44355f','#8677a5')]:
    body='<ellipse cx="128" cy="183" rx="119" ry="32" fill="#7145a6"/><ellipse cx="128" cy="174" rx="119" ry="27" fill="#ad82df"/>'
    body+=f'<rect x="18" y="11" width="220" height="172" rx="61" fill="url(#f)" stroke="{edge}" stroke-width="5"/><path d="M54 25 Q128 9 202 25" fill="none" stroke="#e4d1ff" stroke-opacity=".35" stroke-width="5" stroke-linecap="round"/>'
    save(name,256,224,body,grad(a,b))
shield='<path d="M256 51 Q352 103 430 114 V247 Q428 353 256 459 Q84 353 82 247 V114 Q160 103 256 51Z" fill="url(#f)" stroke="#48528c" stroke-width="15" stroke-linejoin="round"/><path d="M113 136 Q182 123 256 83" fill="none" stroke="#c9f3ff" stroke-width="15" stroke-linecap="round"/>'
save('symbol_schild',512,512,shield,grad('#91d8ff','#3c7ee0'))
smallshield='<path d="M256 171 L325 198 V261 Q325 314 256 351 Q187 314 187 261 V198Z" fill="url(#f)" stroke="#b6d7ff" stroke-width="9" stroke-linejoin="round"/>'
arrows='<path d="M107 217 C117 100 260 67 366 143 L405 177 M405 112 V177 H340 M405 295 C395 412 252 445 146 369 L107 335 M107 400 V335 H172" fill="none" stroke="#c7daff" stroke-width="25" stroke-linecap="round" stroke-linejoin="round"/>'
save('symbol_regeneration',512,512,smallshield+arrows,grad('#8dcdff','#3e79c8'))
save('symbol_schloss',512,512,'<circle cx="256" cy="256" r="215" fill="url(#f)" stroke="#e8efff" stroke-width="24"/><path d="M204 244 V197 Q204 137 256 137 Q308 137 308 197 V244" fill="none" stroke="#fff" stroke-width="28" stroke-linecap="round"/><rect x="174" y="225" width="164" height="148" rx="24" fill="#fff"/><circle cx="256" cy="281" r="20" fill="#497cdb"/><path d="M256 289 V321" stroke="#497cdb" stroke-width="20" stroke-linecap="round"/>',grad('#8cc8ff','#426dd0'))
save('marke_gold',128,128,'<circle cx="64" cy="64" r="59" fill="url(#f)" stroke="#ffde76" stroke-width="4"/>',grad('#ffe58b','#f6b638'))
save('verbinder_gerade',256,64,'<path d="M7 32 H249" fill="none" stroke="#7566a0" stroke-width="19" stroke-linecap="round"/><path d="M7 30 H249" fill="none" stroke="#a3d8f6" stroke-width="13" stroke-linecap="round"/>')
save('verbinder_gebogen',256,256,'<path d="M20 20 C20 165 91 236 236 236" fill="none" stroke="#7566a0" stroke-width="19" stroke-linecap="round"/><path d="M20 20 C20 165 91 236 236 236" fill="none" stroke="#a3d8f6" stroke-width="13" stroke-linecap="round"/>')
hero=R.parent/'helden_baukasten_v1'/'ui'
if not hero.exists():hero=R.parent/'Helden_Baukasten_v1'/'ui'
for name in ['knopf_gruen_normal','knopf_gruen_hover','knopf_gruen_gedrueckt','knopf_gesperrt','haekchen','nav_hintergrund','nav_aktiv','kampf_knopf']:
    if (hero/(name+'.svg')).exists():shutil.copy2(hero/(name+'.svg'),U/(name+'.svg'))
icons=R.parent/'icons_v1'
if not icons.exists():icons=R.parent/'Icons_v1'
for name in ['nav_shop','nav_heroes','nav_battle','nav_upgrades','nav_base','icon_energy','icon_gold','icon_gems','act_profile','act_settings']:
    if (icons/(name+'.png')).exists():shutil.copy2(icons/(name+'.png'),R/'symbole'/(name+'.png'))

graph={'status':'Gestaltung am 03.11.2026 freigegeben; Strukturbeispiel zur Umsetzung, keine neue Spielbalance','referenzdatei':'tech_werft_freigegeben.png','referenzflaeche':[978,1608],
 'aktive_seite':'Upgrades','aktiver_unterreiter':'TECH-WERFT','aktiver_bereich':'schutz',
 'bereiche':[{'id':'angriff','text':'ANGRIFF'},{'id':'schutz','text':'SCHUTZ'},{'id':'technik','text':'TECHNIK'}],
 'prinzip':'Forschungsbereiche und die beiden Schutz-Aeste sind parallel ausbaubar; keine exklusive Wahl, die andere Bereiche dauerhaft sperrt.',
 'aeste':[{'id':'schildstaerke','text':'Schildstärke'},{'id':'regeneration','text':'Regeneration'}],
 'knoten':[{'id':'schild_1','symbol':'ui_png/symbol_schild.png','zeichen':'I','position_relativ':[.50,.515],'zustand':'erforscht'},
  {'id':'schild_2','symbol':'ui_png/symbol_schild.png','zeichen':'II','position_relativ':[.27,.405],'zustand':'ausgewaehlt','voraussetzungen':['schild_1'],'marke':'3'},
  {'id':'schild_3','symbol':'ui_png/symbol_schild.png','zeichen':'III','position_relativ':[.27,.295],'zustand':'gesperrt','voraussetzungen':['schild_2']},
  {'id':'regeneration_1','symbol':'ui_png/symbol_regeneration.png','position_relativ':[.73,.405],'zustand':'verfuegbar','voraussetzungen':['schild_1']},
  {'id':'regeneration_2','symbol':'ui_png/symbol_regeneration.png','position_relativ':[.73,.295],'zustand':'gesperrt','voraussetzungen':['regeneration_1']}],
 'verbindungen':[['schild_1','schild_2'],['schild_2','schild_3'],['schild_1','regeneration_1'],['regeneration_1','regeneration_2']],
 'detailbox':{'auswahl':'schild_2','titel':'Schild II','beschreibung':'Mehr Schildstärke','zusatz':'Andere Forschungswege bleiben verfügbar','aktion':'AUSBAUEN'},
 'beispielressourcen':{'profilstufe':12,'energie':[25,30],'gold':4573,'edelsteine':350},
 'nicht_festgelegt':['Preise und Kosten','Konkrete Zahlenwerte der Wirkungen','Anzahl weiterer Ausbaustufen','Vollständige Bäume von Angriff und Technik'],
 'renderhinweise':{'texte_dynamisch':True,'zeichen_auf_schild_als_label':True,'kein_aeusserer_schein':True,'randstaerke':'Eine dünne Kontur, keine mehrfachen Goldränder','knopf':'Weiche Grün-Kapsel mit dunklem grünen Text','navigation_am_unteren_rand':True}}
(R/'FORSCHUNGSWEGE_UND_LAYOUT.json').write_text(json.dumps(graph,ensure_ascii=False,indent=2),encoding='utf-8')
print('Textfreie Tech-Werft-Bauteile und Forschungsstruktur erstellt.')
