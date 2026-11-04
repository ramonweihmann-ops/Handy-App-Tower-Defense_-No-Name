import json, struct, hashlib, io
from pathlib import Path
from PIL import Image

ordner = Path(__file__).parent
ergebnisse = []
for pfad in sorted(ordner.glob('*.glb')):
    daten = pfad.read_bytes()
    magic, version, gesamt = struct.unpack_from('<4sII', daten)
    assert magic == b'glTF' and version == 2 and gesamt == len(daten)
    pos, dokument, binaer = 12, None, b''
    while pos < len(daten):
        laenge, art = struct.unpack_from('<II', daten, pos)
        block = daten[pos+8:pos+8+laenge]
        if art == 0x4E4F534A: dokument = json.loads(block)
        elif art == 0x004E4942: binaer = block
        pos += 8 + laenge
    assert pos == len(daten)
    zugriffe = dokument.get('accessors', [])
    dreiecke = 0
    for mesh in dokument.get('meshes', []):
        for p in mesh.get('primitives', []):
            anzahl = zugriffe[p['indices']]['count'] if 'indices' in p else zugriffe[p['attributes']['POSITION']]['count']
            if p.get('mode', 4) == 4: dreiecke += anzahl // 3
    texturen = []
    for bild in dokument.get('images', []):
        info = {'name': bild.get('name'), 'eingebettet': 'bufferView' in bild}
        if 'bufferView' in bild:
            b = dokument['bufferViews'][bild['bufferView']]
            start = b.get('byteOffset', 0)
            im = Image.open(io.BytesIO(binaer[start:start+b['byteLength']]))
            info['breite'], info['hoehe'] = im.size
        texturen.append(info)
    animationen = []
    for a in dokument.get('animations', []):
        zeiten = [zugriffe[s['input']] for s in a['samplers']]
        animationen.append({'name': a.get('name'), 'dauer_sekunden': max(x.get('max', [0])[0] for x in zeiten) - min(x.get('min', [0])[0] for x in zeiten), 'kanaele': len(a['channels'])})
    gelenke = sorted({i for s in dokument.get('skins', []) for i in s['joints']})
    knochen = [dokument['nodes'][i].get('name', '') for i in gelenke]
    ergebnisse.append({'datei': pfad.name, 'bytes': len(daten), 'sha256': hashlib.sha256(daten).hexdigest(), 'git_blob_sha': hashlib.sha1(b'blob '+str(len(daten)).encode()+b'\0'+daten).hexdigest(), 'glTF_version': version, 'dreiecke': dreiecke, 'materialien': len(dokument.get('materials', [])), 'texturen': texturen, 'skelette': len(dokument.get('skins', [])), 'knochen': knochen, 'animationen': animationen, 'knoten': [n.get('name', '') for n in dokument.get('nodes', [])]})
(ordner/'GLB_PRUEFUNG.json').write_text(json.dumps(ergebnisse, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps([{k:v for k,v in r.items() if k not in ('knoten','knochen')} for r in ergebnisse], ensure_ascii=False, indent=2))
