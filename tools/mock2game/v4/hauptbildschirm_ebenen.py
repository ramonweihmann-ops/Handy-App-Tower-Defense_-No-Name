# Hauptbildschirm Comic v4 (Vorlage_Raw/Hauptbildschirm_Comic_v4): entfernt die veränderlichen Teile
# (Zahlen, Texte, rote Punkte, Level-Plattformen, Held) aus dem Gesamtbild und stellt grüne und goldene
# Plattform sowie Schloss frei. Ausgabe nach /tmp/x/hb4/out/ (Pfade unten anpassen).
import cv2, numpy as np
src='/home/user/Handy-App-Tower-Defense_-No-Name/Vorlage_Raw/Hauptbildschirm_Comic_v4/hauptbildschirm_symbole_v4.png'
O='/tmp/x/hb4/out/'
im=cv2.imread(src)
H,W=im.shape[:2]
def textmask(img, rect, thr=45, dil=3):
    x0,y0,x1,y1=rect
    c=img[y0:y1,x0:x1].astype(np.int16)
    # Hintergrundfarbe der Fläche: Median am Rand des Rechtecks
    border=np.concatenate([c[0],c[-1],c[:,0],c[:,-1]])
    med=np.median(border,axis=0)
    d=np.abs(c-med).sum(axis=2)
    mk=(d>thr).astype(np.uint8)*255
    mk=cv2.dilate(mk,np.ones((dil,dil),np.uint8))
    full=np.zeros((H,W),np.uint8); full[y0:y1,x0:x1]=mk
    return full
# 1) Texte auf Bedienflächen (nur die Schriftpixel)
texts=[(182,58,272,96),(390,58,474,96),(596,58,662,96),(86,90,116,118),
       (538,158,652,196),(676,168,796,200),
       (365,292,492,322),(330,330,528,428),
       (52,561,130,591),(52,727,130,757),(46,892,136,922),(52,1052,130,1082),
       (352,1495,515,1535)]
m=np.zeros((H,W),np.uint8)
for r in texts: m|=textmask(im,r)
m_text=m.copy()
# 2) rote Hinweise, Schloss, Knoten, Sterne, Held, Namensschild: ganze Flächen
def rect(x0,y0,x1,y1): cv2.rectangle(m,(x0,y0),(x1,y1),255,-1)
for r in [(783,434,822,474),(783,562,822,602),(783,692,822,732),(783,952,822,992),(276,1698,310,1734),(616,1698,650,1734)]: rect(*r)
rect(520,530,556,576)
m_text=m.copy()
m=np.zeros((H,W),np.uint8)
cv2.ellipse(m,(323,778),(84,86),0,0,360,255,-1); rect(240,790,408,866)   # Knoten 4 mit Schein
for cx,cy in [(565,950),(372,1100),(240,1252)]:
    cv2.ellipse(m,(cx,cy-8),(58,46),0,0,360,255,-1); rect(cx-66,cy-8,cx+66,cy+62)  # Plattform
    rect(cx-46,cy+64,cx+46,cy+100)  # Sterne
rect(400,668,484,856)    # Held
rect(198,852,482,914)    # Namensschild
m_big=m.copy()
cv2.imwrite(O+'mask.png',m|m_text)
bg=cv2.inpaint(im,m_text,5,cv2.INPAINT_TELEA)
# große Flächen: weicher Verlauf aus der Umgebung (normierte Faltung) statt Schlieren, dazu Sterne
big=cv2.dilate(m_big,np.ones((9,9),np.uint8))
keep=(big==0).astype(np.float32)
f=bg.astype(np.float32)*keep[...,None]
num=cv2.GaussianBlur(f,(0,0),28); den=cv2.GaussianBlur(keep,(0,0),28)[...,None]
smooth=num/np.maximum(den,1e-3)
# feine Körnung aus einem ungestörten Himmelsausschnitt
rng=np.random.default_rng(7)
fill=smooth.copy()
ys,xs=np.where(big>0)
for _ in range(int(len(ys)/2600)):
    i=rng.integers(len(ys)); y,x=ys[i],xs[i]; r=rng.choice([1,1,1,2]); a=rng.uniform(0.5,1.0)
    cv2.circle(fill,(int(x),int(y)),int(r),(255*a,240*a,245*a),-1,lineType=cv2.LINE_AA)
w=cv2.GaussianBlur((big>0).astype(np.float32),(0,0),6)[...,None]
bg=(bg.astype(np.float32)*(1-w)+fill*w).clip(0,255).astype(np.uint8)
cv2.imwrite(O+'bg_v4.png',bg)
# 3) Plattformen als freigestellte Bilder (Form aus Ellipsen)
def cut(cx,cy,parts,box,digit_box,digit_dark):
    x0,y0,x1,y1=box
    a=np.zeros((H,W),np.uint8)
    for (ex,ey,rx,ry) in parts: cv2.ellipse(a,(cx+ex,cy+ey),(rx,ry),0,0,360,255,-1)
    a=cv2.GaussianBlur(a,(0,0),1.2)
    c=im.copy()
    # Ziffer entfernen (die zeichnet das Spiel)
    dx0,dy0,dx1,dy1=digit_box
    reg=c[dy0:dy1,dx0:dx1].astype(np.int16)
    lum=reg.mean(axis=2)
    dm=((lum<150) if digit_dark else (lum>190)).astype(np.uint8)*255
    dm=cv2.dilate(dm,np.ones((9,9),np.uint8))
    full=np.zeros((H,W),np.uint8); full[dy0:dy1,dx0:dx1]=dm
    c=cv2.inpaint(c,full,12,cv2.INPAINT_TELEA)
    c=cv2.inpaint(c,full,12,cv2.INPAINT_NS)
    rgba=cv2.cvtColor(c,cv2.COLOR_BGR2BGRA); rgba[...,3]=a
    return rgba[y0:y1,x0:x1]
g=cut(240,1252,[(0,-4,54,40),(0,40,66,30),(0,18,66,24)],(168,1195,312,1328),(212,1222,268,1278),False)
cv2.imwrite(O+'platform_green.png',g)
o=cut(323,778,[(0,-6,70,68),(0,52,80,30),(0,30,80,26)],(240,700,406,870),(282,735,364,815),True)
cv2.imwrite(O+'platform_gold.png',o)
# 4) Schloss (hell auf dunkel)
lk=im[530:576,520:556].copy(); lum=lk.mean(axis=2)
al=np.clip((lum-70)*2.2,0,255).astype(np.uint8)
lr=cv2.cvtColor(lk,cv2.COLOR_BGR2BGRA); lr[...,3]=al; cv2.imwrite(O+'lock.png',lr)
