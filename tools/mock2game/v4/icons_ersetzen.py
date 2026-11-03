# Ersetzt in allen Mockups die alten Vektor-Symbole (Währungen, Truhen, Booster, Aktionen, Reiter) durch die
# Space-Comic-Symbole aus Vorlage_Raw/Icons_v1 (Artefakt-Bilder /_blob/…). Zuordnung über eine Signatur je Grafik
# (groups.json aus der Sammlung aller Grafiken). Glanzstreifen bleiben als Maske über dem neuen Symbol erhalten,
# große Münzen/Edelsteine/Energie drehen sich mit den Drehbögen. Fähigkeiten und Talente bleiben unverändert.
import re, json, hashlib
L='/tmp/claude-0/-home-user/5d5708a7-8615-55c4-a499-565014920cdf/scratchpad/live/project/'
D='/tmp/claude-0/-home-user/5d5708a7-8615-55c4-a499-565014920cdf/scratchpad/artifact-files/0b65aff5-f8dc-494a-b7d6-efdc5c5b6414/project/'
B={'act_daily':'9e86330a195fbdf1b93cfd4562dd7ff7','act_missions':'5c8b050b14ce3418d6abced052dba601','act_modes':'298380e5476850c0d6f7f42c055fdd03','act_profile':'c6520c126eaef250cf8c96aab08afb3d','act_settings':'611fa89140db6251fef2183951a9139e','act_shop':'cd213f387fd9f639e37f5a86a87a5bbb','act_wheel':'74a0e94aae4202b96f0e80f93ea0e63e','booster_medipack':'dd7054fb54670662847dcdc16282bd60','chest_epic':'baf9f06fcb0d2b33946819dd274625e6','chest_gold':'a6fd4a688244d03f9e607db4156c6d44','chest_iron':'7d011ff3bfb5540e1e2cbb5775ad012c','chest_silver':'62e8b74c034853695d34f01afab124af','chest_wood':'311b501b97554ebc2fbb4f6814abe2c2','icon_cards':'4226ce88963d52c78a7e6a3bfd259f4f','icon_clock':'6fc4e6a92dba79eb70d4cc012895d7bc','icon_core':'ef79e5170922359419113508f4fa4451','icon_crown':'094a347fd531660704d9738ec3903f60','icon_energy':'7d5fe1a2dacc479ab01f992e73ba4c53','icon_gems':'0e654f50e6bce23818b52fe089316e93','icon_gold':'09671ef380ce59e8e86d5efbf00d4b88','icon_league':'fc8fc4a0a119e5898b4714c15d3e2b13','icon_medal':'4376e9694a4123018e7152e1eba995c6','icon_pass':'9f5a9d64c6a8b4375597a046c3d34116','icon_shield':'d126e524fab4074848f955bc0eaa5612','icon_skull':'942789a575c4e4cf8809d871c30d2af3','icon_stars':'f6b25886830b76047864fad5438cf901','icon_trophy':'be7e2af70f4504a25a50b3fc151f8a7b','nav_base':'ddf3200a8de9ae897c5ce73c2b84f6bc','nav_battle':'fb9c6ac51a4e714e85dd643f94f2b256','nav_heroes':'bba9c40260a4ba0dcb7396b68ea8746c','nav_shop':'384538de9e78872298ca6773ce57a8e6','nav_upgrades':'260b46a3b52192d6858b1ee0dc229989'}
SPIN={'icon_gold':'f3fab2ef042b1dcb5e5fc6ff5e850b4b','icon_energy':'e3742f5e5b9e2c7134e02b3ffb3e327d','icon_gems':'4538a4a51c906601544b17164fb41b7d','icon_stars':'8d28003cfa4377e372cd0a53d07e6b0b'}
M={}
def put(name,idx):
    for i in idx: M[i]=name
put('icon_gold',[7,121,138,145,162,184,190,229,241,244,255])
put('icon_gems',[20,22,25,122,139,185,191,193,216,228,232,239,243,250])
put('icon_energy',[120,137,161,231,242])
put('icon_stars',[30,151,195,253])
put('icon_pass',[155,247,254])
put('icon_cards',[66,124,147])
put('nav_heroes',[98])
put('icon_trophy',[189])
put('act_modes',[210])
put('icon_league',[187])
put('icon_medal',[217])
put('chest_wood',[194,212,213,223,233,235,248])
put('chest_iron',[214]); put('chest_silver',[224]); put('chest_epic',[215,236,238])
put('icon_core',[251]); put('booster_medipack',[117,252])
put('icon_clock',[18,103,153,183])
put('icon_skull',[152]); put('icon_shield',[154]); put('icon_crown',[188,219])
put('act_daily',[205,206]); put('act_wheel',[207]); put('act_missions',[208,249]); put('act_shop',[209])
put('nav_shop',[97]); put('nav_battle',[99]); put('nav_upgrades',[100]); put('nav_base',[101])
put('act_settings',[123]); put('act_profile',[200])
G=json.load(open('/tmp/x/rep/groups.json'))
KEY={G[i]['k']:n for i,n in M.items()}
svg_re=re.compile(r'<svg\b[^>]*>.*?</svg>',re.S)
def norm(s):
    s=re.sub(r'\bid="[^"]*"','',s); s=re.sub(r'url\(#[^)]*\)','url(#)',s); s=re.sub(r'clip-path="[^"]*"','',s)
    s=re.sub(r'<svg\b[^>]*>','<svg>',s,count=1); return s
CSS='''
.ic-shine{position:absolute;inset:0;pointer-events:none;background:linear-gradient(110deg,rgba(255,255,255,0) 38%,rgba(255,255,255,0.75) 50%,rgba(255,255,255,0) 62%);background-size:300% 100%;animation:icshine 2.6s linear infinite}
@keyframes icshine{0%{background-position:130% 0}55%,100%{background-position:-60% 0}}
@keyframes icspin{''' + ''.join(f'{k*100/12:.3f}%{{background-position:{(k%4)*100/3:.3f}% {(k//4)*50}%}}' for k in range(12)) + '''100%{background-position:0% 0%}}
.ic-spin{animation:icspin 1.2s step-end -0.85s infinite;background-size:400% 300%;background-repeat:no-repeat}
'''
def attr(tag,name):
    m=re.search(r'\b%s="([^"]*)"'%name,tag); return m.group(1) if m else None
def build(svg,name):
    tag=re.match(r'<svg\b[^>]*>',svg).group(0)
    w=attr(tag,'width') or '24'; h=attr(tag,'height') or w
    st=attr(tag,'style') or ''
    st=re.sub(r'overflow\s*:\s*visible;?','',st)
    st=re.sub(r'filter\s*:\s*drop-shadow\(0 0 [^;]*\)\s*;?','',st)
    lab=attr(tag,'aria-label')
    hid=' aria-hidden="true"' if not lab else f' role="img" aria-label="{lab}"'
    u='/_blob/'+B[name]
    spin = name in SPIN and (('attributeName="rx"' in svg) or ('type="scale"' in svg)) and float(w) >= 40
    was_anim = name in SPIN and (('attributeName="rx"' in svg) or ('type="scale"' in svg))
    shine = (not spin) and (was_anim or re.search(r'<rect[^>]*>\s*<animate attributeName="x"',svg) is not None)
    base=f'display:inline-block;flex:none;width:{w}px;height:{h}px;vertical-align:middle;{st}'
    if spin:
        return f'<span{hid} class="ic-spin" style="{base};background-image:url(/_blob/{SPIN[name]})"></span>'
    if shine:
        mask=f'-webkit-mask:url({u}) center/contain no-repeat;mask:url({u}) center/contain no-repeat'
        pos='' if 'position' in st else 'position:relative;'
        return f'<span{hid} style="{pos}{base}"><img src="{u}" alt="" style="width:100%;height:100%;display:block"><span class="ic-shine" style="{mask}"></span></span>'
    return f'<img src="{u}" alt=""{hid} style="{base};object-fit:contain">'
c=json.load(open(L+'canvas.json'))
boards=[b for b in c['boards'] if not b.startswith('Icons-')]
stats={}
changed=[]
for b in boards:
    h=open(L+b).read(); n=[0]
    def rep(m):
        s=m.group(0); k=hashlib.md5(norm(s).encode()).hexdigest()[:10]
        if k in KEY:
            n[0]+=1; stats[KEY[k]]=stats.get(KEY[k],0)+1; return build(s,KEY[k])
        return s
    h2=svg_re.sub(rep,h)
    if n[0]:
        if '.ic-shine' not in h2:
            h2=h2.replace('</style>',CSS+'</style>',1) if '</style>' in h2 else h2.replace('</helmet>','<style>'+CSS+'</style></helmet>',1)
        open(D+b,'w').write(h2); changed.append((b,n[0]))
print(changed); print(stats)
json.dump([b for b,_ in changed],open('/tmp/x/rep/changed.json','w'))
