"""Stabile Wegabschnitte für die unveränderten 30 Gebäudeplätze."""
import json
from pathlib import Path
from collections import deque

p=Path(__file__).resolve().parent
index=json.loads((p/'GEBAEUDE_INDEX_ORIGINAL.json').read_text(encoding='utf-8-sig'))
nodes={}; edges=[]
def node(name,x,y,kind='junction'):
    nodes[name]={'id':name,'x':x,'y':y,'kind':kind};return name
def edge(a,b,unlock,kind='lane',via=None):
    pts=[[nodes[a]['x'],nodes[a]['y']]]+(via or [])+[[nodes[b]['x'],nodes[b]['y']]]
    edges.append({'id':f'weg_{len(edges)+1:03d}','from':a,'to':b,'unlock_at':unlock,'kind':kind,'points':pts})
node('eingang',363,2130,'entry')
for row in range(1,11):
    group=index['gebaeude'][(row-1)*3:row*3]
    front=group[0]['fusspunkt_ca_px']['y']+26
    for side,x in [('L',246),('M',363),('R',480)]:node(f'r{row}_{side}',x,front)
    first=(row-1)*3+1
    if row==1:edge('eingang','r1_M',1,'entry')
    else:
        # Linker Ast wächst mit dem ersten Haus der nächsten Reihe.
        old=nodes[f'r{row-1}_L']['y']
        edge(f'r{row-1}_L',f'r{row}_L',first,'lane',[[236,(old+front)/2]])
        # Rechter Ast schließt später den Rundweg der vollständigen Reihe.
        old=nodes[f'r{row-1}_R']['y']
        edge(f'r{row-1}_R',f'r{row}_R',first+2,'lane',[[490,(old+front)/2]])
    edge(f'r{row}_L',f'r{row}_M',first if row==1 else first+1,'cross')
    edge(f'r{row}_M',f'r{row}_R',first+2,'cross')
    for i,g in enumerate(group):
        ident=g['id'];x=g['fusspunkt_ca_px']['x'];y=g['fusspunkt_ca_px']['y']
        node(f'haus_{ident}',x,y,'building')
        if i==1:edge(f'r{row}_M',f'haus_{ident}',int(ident),'access')
        else:
            side='L' if i==0 else 'R'
            edge(f'r{row}_{side}',f'haus_{ident}',int(ident),'access',[[x,front]])
doc={
    'status':'Logischer Verbindungsplan; sichtbare Einmündungen an den Sprites fein ausrichten.',
    'coordinate_system':{'origin':'oben links','width':index['breite'],'height':index['hoehe'],'unit':'Pixel der bisherigen Originalvorlage'},
    'reference_image':'raumbasis_30_gebaeude_pruefansicht.png',
    'preview_image':'raumbasis_mit_wegen_vorschau.png',
    'entry':'eingang',
    'unlock_rule':'Gebäude mit ID <= Championzahl; Wege mit unlock_at <= Championzahl. Bestehende Plätze bleiben unverändert.',
    'start_count':5,'max_count':30,
    'buildings':[{'id':g['id'],'name':g['name'],'unlock_at':int(g['id']),'row':g['reihe_von_unten'],'column':g['spalte_von_links'],'foot':g['fusspunkt_ca_px'],'source_rect':g['auswahl_px'],'access_node':f"haus_{g['id']}"} for g in index['gebaeude']],
    'nodes':list(nodes.values()),'segments':edges,
    'areas':[{'id':i+1,'building_ids':[f'{n:02d}' for n in range(i*6+1,i*6+7)]} for i in range(5)],
    'style':{'main_width':26,'access_width':16,'edge_color':'#c9a252','surface_color':'#726c92','light_color':'#75dce8','use':'Farbrichtwerte für Wege unter den Gebäudesprites; kein neues Gebäudedesign.'},
    'camera':{'overview':'Aktive Gebäudeflächen und Eingang mit Rand vollständig einpassen.','normal':'Auf Lagerbreite einpassen; leichtes Schieben nach oben.','focus':'Gewähltes Gebäude samt Ausrüstung einpassen.','gesture':'Ziehen und Zwei-Finger-Zoom; Zoom am Fingerpunkt halten.','position_rule':'Nur Kamera ändern, nicht alle Gebäude bei neuem Champion verschieben oder verkleinern.'}
}
(p/'WEGENETZ.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
checks=[]
for count in range(1,31):
    graph={n:set() for n in nodes}
    active=[e for e in edges if e['unlock_at']<=count]
    for e in active:graph[e['from']].add(e['to']);graph[e['to']].add(e['from'])
    seen={'eingang'};q=deque(seen)
    while q:
        for next_id in graph[q.popleft()]-seen:seen.add(next_id);q.append(next_id)
    required={f'haus_{i:02d}' for i in range(1,count+1)}
    assert required<=seen,(count,required-seen)
    assert not any(f'haus_{i:02d}' in seen for i in range(count+1,31))
    for e in active:assert e['from'] in seen and e['to'] in seen,(count,e)
    checks.append({'gebaeude':count,'aktive_wegabschnitte':len(active),'alle_aktiven_gebaeude_erreichbar':True,'keine_isolierten_wegabschnitte':True})
for g,original in zip(doc['buildings'],index['gebaeude']):assert g['foot']==original['fusspunkt_ca_px'] and g['source_rect']==original['auswahl_px']
(p/'WEGENETZ_PRUEFBERICHT.json').write_text(json.dumps({'status':'Alle 30 Ausbaustufen geprüft','punkte':len(nodes),'wegabschnitte':len(edges),'positionen_der_30_gebaeude':'unverändert aus dem bestehenden Index','pruefung':checks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{len(nodes)} Punkte, {len(edges)} Wegabschnitte; alle 30 Ausbaustufen verbunden.')
