from pathlib import Path
import json, shutil

R=Path(__file__).resolve().parent
U=R/'ui'; U.mkdir(parents=True,exist_ok=True)
for d in ['symbole','hintergrund']: (R/d).mkdir(exist_ok=True)
def panel(name,w,h,top,bottom,edge,radius=40):
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs><linearGradient id="f" x2="0" y2="1"><stop stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient></defs><rect x="4" y="9" width="{w-8}" height="{h-13}" rx="{radius}" fill="{bottom}"/><rect x="4" y="4" width="{w-8}" height="{h-17}" rx="{radius}" fill="url(#f)" stroke="{edge}" stroke-width="4"/><path d="M{radius} 12 H{w-radius}" stroke="#fff" stroke-opacity=".22" stroke-width="3" stroke-linecap="round"/></svg>'
    (U/(name+'.svg')).write_text(svg,encoding='utf-8')
panel('talent_unbekannt',256,256,'#7950dd','#4830a4','#9470df',32)
panel('talent_freigeschaltet',256,256,'#73dd64','#35a844','#8ce781',32)
panel('talent_kopfbereich',256,64,'#358f43','#257337','#64b769',24)
panel('ziehbox',1024,340,'#342154','#21183f','#8659b9',48)
panel('ziehbox_titel',640,96,'#60477a','#35234e','#816298',38)
panel('knopf_gold_normal',512,144,'#ffe37a','#ffbd31','#ffe99c',44)
panel('knopf_gold_gedrueckt',512,144,'#ffc44c','#e79a22','#fbd278',44)
panel('knopf_violett_normal',1024,128,'#c878fa','#8635d3','#d59aff',42)
panel('knopf_violett_gedrueckt',1024,128,'#a352e2','#6924aa','#b97fe9',42)
tech=R.parent/'tech_werft_freigabe_v1'
for name in ['umschalter_aktiv','umschalter_grund','knopf_gruen_normal','knopf_gruen_hover','knopf_gruen_gedrueckt','knopf_gesperrt','nav_hintergrund','nav_aktiv','kampf_knopf']:
    shutil.copy2(tech/'ui'/(name+'.svg'),U/(name+'.svg'))
icons=R.parent/'icons_v1'
for name in ['nav_shop','nav_heroes','nav_battle','nav_upgrades','nav_base','icon_stars','icon_gold','icon_gems','icon_core','booster_medipack','act_profile','act_settings']:
    shutil.copy2(icons/(name+'.png'),R/'symbole'/(name+'.png'))
shutil.copy2(tech/'hintergrund'/'tech_werft_hintergrund.png',R/'hintergrund'/'weltraum_gemeinsam.png')
shutil.copy2(tech/'raster.cjs',R/'raster.cjs')
shutil.copy2(R.parent/'upgrade_forschungswerft_v1'/'talente_ruhig.png',R/'talente_freigegeben.png')
slots=[]
for row in range(4):
    for col in range(4):
        n=row*4+col
        slots.append({'id':f'talent_{n+1:02}','zeile':row,'spalte':col,'rechteck':[76+210*col,150+213*row,198,204], 'zustand':'freigeschaltet' if n<2 else 'unbekannt','titel':['Schnelllader','Sanitätskoffer'][n] if n<2 else None,'stufe':1 if n<2 else None,'symbol':['symbole/icon_core.png','symbole/booster_medipack.png'][n] if n<2 else None})
layout={'status':'Vom Nutzer am 03.11.2026 freigegebene Gestaltung','referenzflaeche':[978,1608],'referenzdatei':'talente_freigegeben.png','aktive_seite':'Upgrades','aktiver_unterreiter':'TALENTE','gitter':{'spalten':4,'zeilen':4,'felder':slots},'ziehbox':{'rechteck':[89,1024,800,274],'titel':'Neues Talent erhalten','aktionen':[{'text':'ÖFFNEN','art':'video','anzeige':'3/3','rechteck':[120,1074,361,105]},{'text':'ÖFFNEN','art':'talent_stern','anzeige':'1','rechteck':[499,1074,360,105]},{'text':'5 STERNE AUF EINMAL ZIEHEN','art':'fuenffach','rechteck':[120,1189,739,90]}]},'unterreiter':{'rechteck':[149,1325,679,87],'links':'TECH-WERFT','rechts':'TALENTE'},'navigation':{'oben':1450,'unterkante':1608,'aktiv':'Upgrades'},'kopf_beispiel':{'profilstufe':12,'talent_sterne':3,'gold':4573,'edelsteine':350},'texte_dynamisch':True,'fragezeichen_als_label':True,'layout_hinweis':'Pixelpositionen sind ungefähre Referenzwerte; responsiv mit sicheren Bildschirmrändern umsetzen. Beispielwerte sind keine neue Spielbalance.'}
(R/'LAYOUT_UND_ZUSTAENDE.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),encoding='utf-8')
prompts=json.loads((R.parent/'upgrade_forschungswerft_v1'/'BILDANWEISUNGEN_RUHIG.json').read_text(encoding='utf-8'))
(R/'BILDANWEISUNGEN_QUELLE.json').write_text(json.dumps(prompts,ensure_ascii=False,indent=2),encoding='utf-8')
print('Talente-Bauteile und Layout erstellt.')
