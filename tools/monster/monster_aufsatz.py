# Monster je Welt (Wunsch 25.11.2026): Jede Welt bekommt eigene leichte, mittlere und starke Monster im Stil ihres
# Bosses statt eingefärbter Kopien der Monster aus Welt 1 und 2. Gebaut wie die Bosse (tools/bosse/boss_aufsatz.py):
# vorhandenes Grundmodell mit Skelett und Animationen (Schleimling, Tentakler, Panzerkäfer, Krabbler, Zombie, Brecher),
# eigene Teile an den Knochen, Haut im Raum neu bemalt (ohne Nähte in der zerstückelten Abwicklung), als GLB mit allen
# Animationen. Werte (Leben, Tempo, Panzer) bleiben die des Grundmonsters; nur das Aussehen ist neu.
# Aufruf: blender -b -P tools/monster/monster_aufsatz.py -- <variante> <ziel.glb>
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bosse"))
from boss_aufsatz import *          # Bausteine (tube, crystal, look, surface, attach, …), variante, run

# ---------------------------------------------------------------- Haut im Raum bemalen

def texels(body):
    """Für jedes Texel der Körpertextur die Lage auf dem Körper (Ruhehaltung, Welt) und die Flächenrichtung.
    Muster (Risse, Flecken, Reif, Schnee oben) werden damit im Raum berechnet und laufen über die vielen kleinen
    Stücke der Abwicklung hinweg, ohne Nähte. Liefert ein Wörterbuch mit px (alte Farben), P, N, cov (Texel gehört
    zum Körper), out (neue Farben, anfangs = alt), em (Leuchten, anfangs schwarz)."""
    m, tex, img, px = body_texture(body)
    h, w = px.shape[:2]
    me = body.data
    me.calc_loop_triangles()
    uvl = me.uv_layers.active.data
    mw = body.matrix_world; m3 = mw.to_3x3()
    co = np.array([tuple(mw @ v.co) for v in me.vertices], np.float32)
    vn = np.array([tuple((m3 @ v.normal).normalized()) for v in me.vertices], np.float32)
    P = np.zeros((h, w, 3), np.float32); N = np.zeros((h, w, 3), np.float32); cov = np.zeros((h, w), bool)
    for tri in me.loop_triangles:
        U = np.array([(uvl[k].uv.x * w, uvl[k].uv.y * h) for k in tri.loops])
        x0, y0 = np.floor(U.min(0)).astype(int) - 1; x1, y1 = np.ceil(U.max(0)).astype(int) + 1
        x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, w - 1), min(y1, h - 1)
        if x1 < x0 or y1 < y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        Q = np.stack([gx.ravel(), gy.ravel()], 1)
        v0 = U[1] - U[0]; v1 = U[2] - U[0]; d00 = v0 @ v0; d01 = v0 @ v1; d11 = v1 @ v1
        den = d00 * d11 - d01 * d01
        if abs(den) < 1e-12:
            continue
        v2 = Q - U[0]; d20 = v2 @ v0; d21 = v2 @ v1
        b1 = (d11 * d20 - d01 * d21) / den; b2 = (d00 * d21 - d01 * d20) / den; b0 = 1 - b1 - b2
        eps = -1.0 / max(1.0, math.sqrt(max(d00, d11)))
        ins = (b0 >= eps) & (b1 >= eps) & (b2 >= eps)
        if not ins.any():
            continue
        bb = np.clip(np.stack([b0[ins], b1[ins], b2[ins]], 1), 0, None); bb /= bb.sum(1, keepdims=True)
        V = list(tri.vertices)
        ix = (Q[ins] - 0.5).astype(int)
        P[ix[:, 1], ix[:, 0]] = bb @ co[V]
        N[ix[:, 1], ix[:, 0]] = bb @ vn[V]
        cov[ix[:, 1], ix[:, 0]] = True
    N /= np.maximum(np.linalg.norm(N, axis=-1, keepdims=True), 1e-6)
    em = np.zeros((h, w, 4), np.float32); em[..., 3] = 1
    return {"px": px, "P": P, "N": N, "cov": cov, "out": px.copy(), "em": em, "tex": tex, "body": body}

def commit(T, strength=1.5, pad=True):
    """neue Farben (und Leuchten, falls gesetzt) ins Modell übernehmen, Ränder der Stücke auffüllen"""
    body = T["body"]
    T["tex"].image = new_image(body.name + "_Farbe", np.clip(T["out"], 0, 1))
    if T["em"][..., :3].max() > 0.01:
        set_emission(body, T["em"].copy(), strength)
    if pad:
        pad_texture(body, grow=10, shrink=1)

def hsv(px):
    r, g, b = px[..., 0], px[..., 1], px[..., 2]
    mx = np.maximum(np.maximum(r, g), b); mn = np.minimum(np.minimum(r, g), b); d = mx - mn
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0)
    hh = np.zeros_like(mx)
    dd = np.maximum(d, 1e-6)
    hh = np.where(mx == r, ((g - b) / dd) % 6, hh)
    hh = np.where(mx == g, (b - r) / dd + 2, hh)
    hh = np.where(mx == b, (r - g) / dd + 4, hh)
    return hh / 6.0, s, mx

def hue_mask(px, center, width=0.07, smin=0.25, vmin=0.12):
    """Stellen eines Farbtons (0 rot, 0.33 grün, 0.5 türkis, 0.75 violett), weich begrenzt"""
    hh, s, v = hsv(px)
    dh = np.abs(((hh - center) + 0.5) % 1.0 - 0.5)
    return np.clip((width - dh) / (width * 0.4), 0, 1) * np.clip((s - smin) / 0.1, 0, 1) * np.clip((v - vmin) / 0.08, 0, 1)

def lum(px):
    return 0.3 * px[..., 0] + 0.6 * px[..., 1] + 0.1 * px[..., 2]

def _hash(ix, iy, iz, seed):
    h = (ix.astype(np.uint32) * np.uint32(73856093)) ^ (iy.astype(np.uint32) * np.uint32(19349663)) ^ \
        (iz.astype(np.uint32) * np.uint32(83492791)) ^ np.uint32((seed * 2654435761) & 0xffffffff)
    h ^= h >> np.uint32(13); h *= np.uint32(1274126177); h ^= h >> np.uint32(16)
    return (h & np.uint32(0xffffff)).astype(np.float32) / float(0xffffff)

def noise3(P, freq, seed=0):
    """glattes Rauschen im Raum (0..1), P: (…, 3)"""
    Q = P * freq
    i = np.floor(Q).astype(np.int64); f = Q - i
    u = f * f * (3 - 2 * f)
    acc = np.zeros(P.shape[:-1], np.float32)
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                wgt = (u[..., 0] if dx else 1 - u[..., 0]) * (u[..., 1] if dy else 1 - u[..., 1]) * (u[..., 2] if dz else 1 - u[..., 2])
                acc += wgt * _hash(i[..., 0] + dx, i[..., 1] + dy, i[..., 2] + dz, seed)
    return acc

def fbm3(P, freq, seed=0, octaves=4):
    out = np.zeros(P.shape[:-1], np.float32); amp = 1.0; tot = 0.0
    for o in range(octaves):
        out += noise3(P, freq * 2 ** o, seed + o * 17) * amp; tot += amp; amp *= 0.5
    return out / tot

def worley3(P, freq, seed=0):
    """Zellen im Raum: Abstand zur nächsten Zellgrenze (Welt-Einheiten) und eine Zufallszahl je Zelle (0..1)"""
    Q = P * freq
    i = np.floor(Q).astype(np.int64)
    f1 = np.full(P.shape[:-1], 9.0, np.float32); f2 = f1.copy(); cid = np.zeros(P.shape[:-1], np.float32)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                cx, cy, cz = i[..., 0] + dx, i[..., 1] + dy, i[..., 2] + dz
                fp = np.stack([cx + _hash(cx, cy, cz, seed), cy + _hash(cx, cy, cz, seed + 1), cz + _hash(cx, cy, cz, seed + 2)], -1)
                d = np.linalg.norm(Q - fp, axis=-1)
                closer = d < f1
                f2 = np.where(closer, f1, np.minimum(f2, d))
                cid = np.where(closer, _hash(cx, cy, cz, seed + 3), cid)
                f1 = np.where(closer, d, f1)
    return (f2 - f1) * 0.5 / freq, cid

def paint(T, mask, color, keep_shading=0.5):
    """Maske (0..1 je Texel) in eine Farbe umfärben; keep_shading: wie viel der alten Helligkeit erhalten bleibt"""
    px = T["px"]
    l = lum(px)[..., None]
    c = np.asarray(color, np.float32)
    if c.ndim == 1:
        c = c[None, None, :]
    new = np.clip(c * ((1 - keep_shading) + keep_shading * (0.55 + l * 0.9)), 0, 1)
    k = np.clip(mask, 0, 1)[..., None]
    T["out"][..., :3] = T["out"][..., :3] * (1 - k) + new * k

def glow(T, mask, color):
    k = np.clip(mask, 0, 1)[..., None]
    T["em"][..., :3] = np.maximum(T["em"][..., :3], k * np.asarray(color, np.float32))

def gradient(a, b, t):
    t = np.clip(t, 0, 1)[..., None]
    return np.asarray(a, np.float32) * (1 - t) + np.asarray(b, np.float32) * t

# ---------------------------------------------------------------- kleine Bausteine

def bone_pt(arm, bone, t=0.0):
    b = arm.data.bones[bone]
    return arm.matrix_world @ b.head_local.lerp(b.tail_local, t)

def curl_horn(name, base, s, size, mat, turns=1.5, up=1.0):
    """eingerolltes Horn (wie beim Frost-Yeti): von base nach außen, oben und zurück eingerollt; s = Seite ±1"""
    pts = []; radii = []
    for i in range(14):
        t = i / 13
        a = t * turns * math.pi
        Rh = size * (1 - 0.45 * t)
        pts.append(tuple(Vector(base) + Vector((s * size * 0.55 * t, math.sin(a) * Rh, ((1 - math.cos(a)) * Rh * 0.85) * up))))
        radii.append(size * 0.42 * (1 - t) + size * 0.05)
    radii[-1] = 0.0
    return give(tube(name, pts, radii), mat)

def icicle(name, top, length, r, mat, bend=(0, 0, 0)):
    """Eiszapfen von top nach unten, leicht unregelmäßig"""
    t = Vector(top); bd = Vector(bend)
    pts = [t + Vector((0, 0, 0.01)), t + Vector((0, 0, -length * 0.35)) + bd * 0.3, t + Vector((0, 0, -length * 0.7)) + bd * 0.7, t + Vector((0, 0, -length)) + bd]
    return give(tube(name, [tuple(p) for p in pts], [r, r * 0.72, r * 0.38, 0.0], segs=7), mat)

def ring_hits(body, center, n, z, spread=1.0, phase=0.0, skip=None):
    """Punkte (Punkt, Normale) rund um center in Höhe z, von außen gesucht; skip(Winkel) lässt Stellen aus"""
    out = []
    for i in range(n):
        a = phase + i * 2 * math.pi / n
        if skip is not None and skip(a):
            continue
        d = Vector((math.cos(a) * spread, math.sin(a) * spread, z)).normalized()
        p, nn = surface(body, Vector(center) + d * 2.0, -d)
        if p is not None:
            out.append((p, nn, a))
    return out

def fluff(name, pts, mat, arm, bone, r=0.05, length=0.08, seed=3):
    """weiche Fellbüschel: kurze, runde Strähnen, die nach außen und unten fallen (nicht spitz wie Stacheln)"""
    rnd = random.Random(seed)
    parts = []
    for i, (p, n) in enumerate(pts):
        side = n.cross(Vector((0, 0, 1)))
        if side.length < 0.1:
            side = n.cross(Vector((0, 1, 0)))
        side.normalize()
        L = length * rnd.uniform(0.8, 1.2); rr = r * rnd.uniform(0.85, 1.15)
        d = (n * 0.8 + Vector((0, 0, -0.6)) + side * rnd.uniform(-0.3, 0.3)).normalized()
        pts_ = [p - n * 0.025, p + d * L * 0.35, p + d * L * 0.7 + Vector((0, 0, -0.2 * L)), p + d * L + Vector((0, 0, -0.45 * L))]
        parts.append(give(tube("%s%d" % (name, i), [tuple(q) for q in pts_], [rr, rr * 0.95, rr * 0.7, rr * 0.25], segs=10), mat))
    return attach(join_parts(parts, name), arm, bone)

def clumps(name, pts, mat, arm, bone, r=0.05, seed=3, squash=0.6):
    """Fellklumpen: flache, weiche Wülste, die auf der Oberfläche aufliegen (wirkt wie dichtes Fell, nicht wie Zacken)"""
    rnd = random.Random(seed)
    parts = []
    for i, (p, n) in enumerate(pts):
        rr = r * rnd.uniform(0.8, 1.2)
        o = sphere("%s%d" % (name, i), (0, 0, 0), rr, (1.0, 1.0, squash), segs=(16, 10))
        o.location = p + n * rr * 0.12 + Vector((0, 0, -rr * 0.15))
        o.rotation_euler = n.to_track_quat('Z', 'Y').to_euler()
        parts.append(give(o, mat))
    return attach(join_parts(parts, name), arm, bone)

def lathe_texture(mat, arr):
    nt = mat.node_tree
    ti = nt.nodes.new("ShaderNodeTexImage"); ti.image = new_image(mat.name + "_Farbe", arr)
    nt.links.new(ti.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])

def streaks(h, w, cells_u, cells_v, seed):
    """Fellsträhnen: Rauschen, in v-Richtung gestreckt (Abwicklung eines Drehkörpers: u rundum, v von oben nach unten)"""
    from PIL import Image as _Img
    small = fbm(max(8, cells_v * 4), w, cells_u, seed, octaves=3).astype(np.float32)
    return np.array(_Img.fromarray(small, mode="F").resize((w, h), _Img.BILINEAR))

# ---------------------------------------------------------------- Frostmond (Welt 3): Stil des Frost-Yetis

def frost_mats():
    return {
        "fur": look("Fell", (0.9, 0.94, 1.0), rough=0.9),
        "fur2": look("FellSchatten", (0.74, 0.82, 0.94), rough=0.9),
        "face": look("YetiGesicht", (0.56, 0.64, 0.78), rough=0.6),
        "dark": look("YetiDunkel", (0.12, 0.14, 0.22), rough=0.5),
        "eye": look("EisAuge", (0.7, 0.95, 1.0), rough=0.2, emit=(0.45, 0.85, 1.0), strength=3.0),
        "fang": look("Fangzahn", (0.97, 0.97, 0.94), rough=0.3),
        "horn": look("Eishorn", (0.62, 0.72, 0.86), rough=0.25),
        "ice": look("Eis", (0.8, 0.94, 1.0), rough=0.08, emit=(0.55, 0.85, 1.0), strength=0.45),
        "ice_deep": look("EisTief", (0.42, 0.7, 0.98), rough=0.1, emit=(0.35, 0.7, 1.0), strength=0.7),
        "claw": look("Kralle", (0.16, 0.17, 0.25), rough=0.35),
    }

def yeti_face(g, zc, k, M, angry=1.0):
    """Yeti-Gesicht vorn auf einem Körper g (wie beim Frost-Yeti, verkleinert um k): blaugraue Maske, eisblau leuchtende
    Augen in dunklen Höhlen, Fellbrauen schräg nach innen, Nase, Maul mit zwei Fangzähnen. Liefert die Teile."""
    p, n = surface(g, (0, -2.0, zc), (0, 1, 0))
    F = lambda x, dy, z: tuple(Vector((p.x + x * k, p.y + dy * k, p.z + z * k)))
    parts = []
    mask_ = sphere("Gesicht", (0, 0, 0), 0.2 * k, (1.2, 0.3, 0.95)); mask_.location = F(0, 0.045, -0.01)
    parts.append(give(mask_, M["face"]))
    muzzle = sphere("Schnauze", (0, 0, 0), 0.095 * k, (1.35, 0.62, 0.72)); muzzle.location = F(0, -0.035, -0.075)
    parts.append(give(muzzle, M["face"]))
    parts.append(give(sphere("Nase", F(0, -0.085, -0.045), 0.024 * k, (1.3, 0.8, 0.8)), M["dark"]))
    mouth = sphere("Maul", (0, 0, 0), 0.05 * k, (1.5, 0.4, 0.45)); mouth.location = F(0, -0.07, -0.115)
    parts.append(give(mouth, M["dark"]))
    for s in (-1, 1):
        parts.append(give(tube("Fang%d" % s, [F(s * 0.04, -0.085, -0.135), F(s * 0.042, -0.097, -0.105), F(s * 0.045, -0.095, -0.08)],
                               [0.015 * k, 0.01 * k, 0.0]), M["fang"]))
        so = sphere("Augenhoehle%d" % s, (0, 0, 0), 0.05 * k, (1.15, 0.6, 0.8)); so.location = F(s * 0.075, -0.02, 0.045)
        so.rotation_euler = (0, math.radians(-s * 15 * angry), 0)
        parts.append(give(so, M["dark"]))
        e = sphere("Auge%d" % s, (0, 0, 0), 0.037 * k, (1.15, 0.6, 0.85)); e.location = F(s * 0.075, -0.042, 0.045)
        e.rotation_euler = (0, math.radians(-s * 15 * angry), 0)
        parts.append(give(e, M["eye"]))
        parts.append(give(sphere("Pupille%d" % s, F(s * 0.07, -0.068, 0.04), 0.014 * k), M["dark"]))
        parts.append(give(tube("Braue%d" % s, [F(s * 0.135, -0.0, 0.1), F(s * 0.075, -0.05, 0.095 - 0.01 * angry), F(s * 0.02, -0.055, 0.075 - 0.012 * angry)],
                               [0.026 * k, 0.03 * k, 0.02 * k]), M["fur"]))
    return parts

@variante("frost_schleimling", "schleimling")
def frost_knaeuel(arm, body):
    """Frostmond, leicht: Frostknäuel – kleiner, runder Schneeball aus weißem Fell mit Yeti-Gesicht (eisblau leuchtende
    Augen, Fangzähne), eingerollten Eishörnchen, Eiskristallen auf dem Rücken und einem Fellkranz unten. Eigene Figur
    auf dem Skelett des Schleimlings (hüpft wie er)."""
    M = frost_mats()
    skin = look("KnaeuelFell", (1.0, 1.0, 1.0), rough=0.9)
    prof = [(0.8, 0.0), (0.79, 0.09), (0.76, 0.18), (0.7, 0.27), (0.62, 0.34), (0.52, 0.39), (0.41, 0.415), (0.3, 0.41), (0.2, 0.39),
            (0.12, 0.35), (0.06, 0.29), (0.02, 0.2), (0.003, 0.1), (0.0, 0.0)]
    g = lathe("Knaeuel", prof, segs=64)
    # Fell: weiß mit feinen Strähnen, unten bläulich schattiert, oben heller (Bildzeile 0 = unten = v 0)
    H_, W_ = 1024, 1024
    vv = np.linspace(0, 1, H_)[:, None] * np.ones((1, W_))
    st = streaks(H_, W_, 90, 6, 31)
    col = gradient((0.66, 0.76, 0.9), (0.95, 0.97, 1.0), (vv - 0.12) / 0.5)
    col = np.clip(col * (0.9 + (st[..., None] - 0.5) * 0.35), 0, 1)
    arr = np.ones((H_, W_, 4), np.float32); arr[..., :3] = col
    lathe_texture(skin, arr)
    give(g, skin)
    bpy.context.view_layer.update()
    parts = yeti_face(g, 0.47, 1.15, M)
    # eingerollte Eishörnchen seitlich oben
    for s in (-1, 1):
        p, n = surface(g, (s * 2.0, -0.02, 0.66), (-s, 0, 0))
        parts.append(curl_horn("Horn%d" % s, p - n * 0.03, s, 0.12, M["horn"], turns=1.4))
    # Fellschopf oben, Eiskristalle auf dem Rücken
    top = on_surface(g, (0, 0, 0.4), [(-0.25, -0.15, 1), (0.0, -0.05, 1), (0.22, -0.12, 1), (0.08, 0.18, 1), (-0.15, 0.15, 1)])
    for k, (x, y, z, h, r) in enumerate(((0.0, 0.35, 0.55, 0.2, 0.05), (-0.16, 0.3, 0.45, 0.14, 0.04), (0.17, 0.3, 0.46, 0.15, 0.04), (0.05, 0.38, 0.32, 0.1, 0.03))):
        parts.append(shard_on("RueckenEis%d" % k, g, (x, y, z), (x * 1.2, 1.0, 0.75), h, r, M["ice_deep"] if k % 2 == 0 else M["ice"], depth=0.03))
    attach(join_parts(parts, "Knaeuel_Kopf"), arm, "Top")
    clumps("Schopf", top, M["fur"], arm, "Top", r=0.07, seed=5)
    # Fellkranz unten rundum und ein paar Büschel an den Seiten
    rim = [(p, n) for p, n, a in ring_hits(g, (0, 0, 0.12), 22, -0.15, phase=0.2)]
    clumps("Fellkranz", rim, M["fur2"], arm, "Body", r=0.075, seed=7, squash=0.55)
    side = [(p, n) for p, n, a in ring_hits(g, (0, 0, 0.36), 10, 0.35, phase=1.0, skip=lambda a: math.sin(a) < -0.45)]
    clumps("FellSeite", side, M["fur"], arm, "Top", r=0.06, seed=9, squash=0.5)
    skin_to(g, arm, lambda c: {"Top": smooth01((c.z - 0.14) / 0.36), "Body": 1 - smooth01((c.z - 0.14) / 0.36)})
    dampen_scale(arm, ("Body", "Top"), 0.55)
    remove_body(body)

@variante("frost_tentakler", "tentakler")
def eisschwinge(arm, body):
    """Frostmond, mittel: Eisschwinge – Flugwesen mit weißem Fell, Flügeln aus durchscheinendem Eis mit hellen
    Sprüngen und Eiskristallen an der Flügelkante, Eishörnern, Eiskristallkamm auf dem Kopf, eisblau leuchtenden
    Augen und Eiszapfen unter dem Bauch. Eigene Figur auf dem Skelett des Tentaklers."""
    M = frost_mats()
    T = texels(body)
    px, P, N = T["px"], T["P"], T["N"]
    red = hue_mask(px, 0.02, 0.06, 0.35)
    teal = hue_mask(px, 0.49, 0.08, 0.3)
    hh, s, v = hsv(px)
    beige = np.clip((0.6 - s) / 0.1, 0, 1) * np.clip((v - 0.5) / 0.1, 0, 1) * hue_mask(px, 0.11, 0.07, 0.08)
    white = np.clip((0.15 - s) / 0.06, 0, 1) * np.clip((v - 0.8) / 0.06, 0, 1)
    # Fell: weiß, Unterseite bläulich, feine Strähnen
    fine = fbm3(P, 60.0, 3, 2)
    under = np.clip(-N[..., 2] * 1.4, 0, 1)
    paint(T, red, gradient((0.92, 0.95, 1.0), (0.62, 0.72, 0.88), under) * (0.88 + (fine[..., None] - 0.5) * 0.3), keep_shading=0.35)
    # Flügelhaut: Eis mit hellen Sprüngen, die leicht leuchten
    edge, cid = worley3(P, 9.0, 11)
    crack = np.clip(1 - edge / 0.006, 0, 1)
    ice = gradient((0.42, 0.68, 0.95), (0.72, 0.9, 1.0), cid)
    paint(T, teal, ice, keep_shading=0.3)
    paint(T, teal * crack, (0.95, 0.99, 1.0), keep_shading=0.0)
    glow(T, teal * (0.18 + crack * 0.6), (0.4, 0.75, 1.0))
    paint(T, beige, (0.62, 0.74, 0.9), keep_shading=0.6)
    glow(T, white, (0.35, 0.7, 1.0))          # Augenweiß leuchtet eisblau
    commit(T, strength=1.2)
    # Eiskristalle an der Flügel-Oberkante, nach oben außen
    for side, chain in ((1, ("Bone_031", "Bone_030", "Bone_029")), (-1, ("Bone_026", "Bone_025", "Bone_024"))):
        for k, (bone, t, h) in enumerate(((chain[1], 0.35, 0.15), (chain[1], 0.85, 0.2), (chain[2], 0.3, 0.17), (chain[2], 0.7, 0.12))):
            b0 = bone_pt(arm, bone, t)
            p, n = surface(body, b0 + Vector((0, 0, 1.0)), (0, 0, -1))
            base = (p - n * 0.02) if p is not None else b0
            d = Vector((side * 0.45, 0.15, 1.0))
            attach(shard("FluegelEis%d_%d" % (side, k), base, d, h, 0.035, M["ice"] if k % 2 else M["ice_deep"]), arm, bone)
        # Eiszapfen an der Flügel-Unterkante (Spitzen)
        tip = bone_pt(arm, chain[2], 1.0)
        for k, (dx, L) in enumerate(((0.0, 0.14), (-side * 0.12, 0.1))):
            attach(icicle("FluegelZapfen%d_%d" % (side, k), tip + Vector((dx, 0, -0.04)), L, 0.025, M["ice"]), arm, chain[2])
    # Kopf: Kamm aus Eiskristallen zwischen den Hörnern
    head = bone_pt(arm, "Bone_001", 0.5)
    for k, (x, y, h, r) in enumerate(((0.0, 0.0, 0.24, 0.05), (-0.09, 0.05, 0.17, 0.04), (0.09, 0.05, 0.17, 0.04), (0.0, 0.13, 0.15, 0.04))):
        attach(shard_on("KopfEis%d" % k, body, (x, y, 1.3), (x * 2.0, 0.25 + y, 1.0), h, r, M["ice_deep"] if k == 0 else M["ice"], depth=0.03), arm, "Bone_001")
    # Eiszapfen unter dem Bauch
    for k, (x, y, L) in enumerate(((0.0, -0.05, 0.16), (-0.12, 0.0, 0.11), (0.12, 0.0, 0.12), (-0.05, 0.12, 0.09), (0.07, 0.12, 0.1))):
        p, n = surface(body, (x, y, -1.0), (0, 0, 1))
        if p is not None:
            attach(icicle("BauchZapfen%d" % k, p + Vector((0, 0, 0.02)), L, 0.03, M["ice"] if k % 2 else M["ice_deep"]), arm, "Bone_001")
    # Fellbüschel an den Wangen und am Rücken
    cheeks = on_surface(body, (0, -0.1, 1.0), [(s_ * 1.0, -0.3, z) for s_ in (-1, 1) for z in (-0.2, 0.1)])
    fur_tufts("FellWange", cheeks, M["fur"], arm, "Bone_001", r=0.05, length=0.12, seed=13)
    back = on_surface(body, (0, 0.0, 1.0), [(x, 1.0, z) for x, z in ((-0.3, 0.2), (0.3, 0.2), (0.0, 0.4), (0.0, -0.1))])
    fur_tufts("FellRuecken", back, M["fur2"], arm, "Bone_001", r=0.055, length=0.13, seed=17)

@variante("frost_panzerkaefer", "panzerkaefer")
def gletscherpanzer(arm, body):
    """Frostmond, stark: Gletscherpanzer – schwerer Panzerläufer mit verschneitem Gletscherpanzer: oben Schnee, an
    den Seiten blaues Eis mit Sprüngen, aufragende Eisschollen auf dem Rücken, Eiszapfen rund um den Panzerrand,
    zwei große geschwungene Stoßzähne, Fell an den Beinen, blaugraue Haut. Eigene Figur auf dem Skelett des Panzerkäfers."""
    M = frost_mats()
    tusk = look("Stosszahn", (0.93, 0.95, 0.98), rough=0.3)
    T = texels(body)
    px, P, N = T["px"], T["P"], T["N"]
    teal = hue_mask(px, 0.49, 0.08, 0.3)
    red = np.maximum(hue_mask(px, 0.02, 0.06, 0.35), hue_mask(px, 0.97, 0.05, 0.3))
    hh, s, v = hsv(px)
    beige = np.clip((0.6 - s) / 0.1, 0, 1) * np.clip((v - 0.5) / 0.1, 0, 1) * hue_mask(px, 0.11, 0.07, 0.08)
    # Panzer: oben Schnee (wo die Fläche nach oben zeigt), Seiten Gletschereis mit Schollen und Sprüngen
    edge, cid = worley3(P, 7.0, 21)
    snow_k = np.clip((N[..., 2] - 0.45 + (fbm3(P, 14.0, 4, 3) - 0.5) * 0.5) / 0.15, 0, 1)
    ice = gradient((0.3, 0.55, 0.88), (0.58, 0.8, 0.98), cid * 0.8 + (P[..., 2] - 0.1) * 0.8)
    snow = np.clip(np.asarray((0.93, 0.96, 1.0), np.float32) * (0.92 + (fbm3(P, 40.0, 5, 2)[..., None] - 0.5) * 0.15), 0, 1)
    col = ice * (1 - snow_k[..., None]) + snow * snow_k[..., None]
    paint(T, teal, col, keep_shading=0.35)
    crack = np.clip(1 - edge / 0.005, 0, 1) * (1 - snow_k)
    paint(T, teal * crack, (0.16, 0.3, 0.55), keep_shading=0.0)
    glow(T, teal * (1 - snow_k) * 0.12, (0.4, 0.75, 1.0))
    # Haut blaugrau, helle Teile (Bauch, Füße) eisblass
    paint(T, red, (0.42, 0.5, 0.64), keep_shading=0.6)
    paint(T, beige, (0.78, 0.86, 0.95), keep_shading=0.5)
    commit(T, strength=1.0)
    # Eiszapfen rund um den Panzerrand (vorn beim Kopf frei)
    rim = ring_hits(body, (0, 0.03, 0.2), 18, 0.02, phase=0.1, skip=lambda a: math.sin(a) < -0.7)
    for k, (p, n, a) in enumerate(rim):
        L = 0.07 + 0.05 * ((k * 7) % 3) / 2
        attach(icicle("RandZapfen%d" % k, p + n * 0.005 + Vector((0, 0, -0.005)), L, 0.022, M["ice"] if k % 2 else M["ice_deep"]), arm, "Body")
    # Eisschollen auf dem Rücken: flache, schräg aufgestellte Platten wie Packeis (nicht hoch wie beim Kristallkäfer)
    for k, (x, y, w_, h_, tilt, yaw) in enumerate(((0.0, 0.06, 0.13, 0.1, 25, 0), (-0.14, 0.12, 0.1, 0.08, 35, -30), (0.15, 0.1, 0.11, 0.08, 30, 35),
                                                   (-0.05, -0.08, 0.09, 0.07, -30, -10), (0.09, 0.22, 0.09, 0.07, 45, 15), (0.2, -0.06, 0.08, 0.06, -25, 50),
                                                   (-0.2, -0.03, 0.08, 0.06, -25, -50))):
        p, n = surface(body, (x, y, 1.0), (0, 0, -1))
        if p is None:
            continue
        o = block_at("Eisscholle%d" % k, (0, 0, 0), (w_, 0.022, h_), M["ice_deep"] if k % 2 == 0 else M["ice"], seed=40 + k, flat=True, subdiv=1)
        o.matrix_world = Matrix.Translation(p + n * (h_ * 0.35)) @ Matrix.Rotation(math.radians(yaw), 4, 'Z') @ Matrix.Rotation(math.radians(tilt), 4, 'X')
        attach(o, arm, "Body")
    for k, (x, y, h, r) in enumerate(((0.05, 0.0, 0.13, 0.04), (-0.08, 0.18, 0.1, 0.035))):
        attach(shard_on("Eisspitze%d" % k, body, (x, y, 0.3), (x * 2, 0.3, 1.0), h, r, M["ice"], depth=0.03), arm, "Body")
    # Stoßzähne: aus den Mundwinkeln nach vorn, unten und wieder hoch geschwungen
    h0 = bone_pt(arm, "Head", 0.6)
    for s_ in (-1, 1):
        q, m = surface(body, (s_ * 0.1, -1.5, h0.z - 0.03), (0, 1, 0))
        root = (q - m * 0.02) if q is not None else h0
        attach(give(horn("Stosszahn%d" % s_, tuple(root), tuple(root + Vector((s_ * 0.09, -0.12, -0.1))), tuple(root + Vector((s_ * 0.03, -0.24, 0.08))), 0.035, n=12), tusk), arm, "Head")
    # Fell an den Oberbeinen
    for b in [b.name for b in arm.data.bones if b.name.endswith("_Up")]:
        c = bone_pt(arm, b, 0.6)
        sx = 1 if c.x > 0 else -1
        pts = on_surface(body, c, [(sx * 1.0, 0.0, 0.6), (sx * 0.8, 0.5, 0.4), (sx * 0.8, -0.5, 0.4)])
        fur_tufts("Beinfell" + b, pts, M["fur"], arm, b, r=0.03, length=0.07, seed=sum(map(ord, b)) % 97)

# ---------------------------------------------------------------- Zweibeiner (Krabbler, Zombie, Brecher)

def regions(T, arm):
    """Bereiche der Zweibeiner-Textur: Haut (grün), Violett (Anzug, am Kopf Flecken), Grau (Gürtel, Schnallen),
    Weiß (Augen, Kragen), Dunkel (Pupillen), Gelb (Zähne), Kopf (über dem Hals)"""
    px, P = T["px"], T["P"]
    hh, s, v = hsv(px)
    neck = bone_pt(arm, "mixamorig:Neck", 0.6).z
    return {
        "skin": hue_mask(px, 0.25, 0.09, 0.3),
        "purple": hue_mask(px, 0.76, 0.09, 0.25),
        "grey": np.clip((0.2 - s) / 0.06, 0, 1) * np.clip((v - 0.35) / 0.1, 0, 1) * np.clip((0.84 - v) / 0.06, 0, 1),
        "white": np.clip((0.16 - s) / 0.06, 0, 1) * np.clip((v - 0.84) / 0.05, 0, 1),
        "dark": np.clip((0.2 - v) / 0.06, 0, 1),
        "yellow": hue_mask(px, 0.13, 0.05, 0.4),
        "head": np.clip((P[..., 2] - neck) / 0.03, 0, 1),
        "collar": np.clip((0.3 - s) / 0.08, 0, 1) * np.clip((v - 0.5) / 0.08, 0, 1) * np.clip((neck - P[..., 2]) / 0.02, 0, 1)
                  * np.clip((P[..., 2] - (bone_pt(arm, "mixamorig:Neck").z - 0.14)) / 0.02, 0, 1),
    }

def cracked(T, mask, freq, width, base, line_col, glow_col, seed=1, var=0.4, sparse=0.0, calm=None):
    """Platten mit leuchtenden Fugen (Basalt mit Magma, Kristall mit Adern): jede Zelle etwas anders hell.
    sparse > 0: Fugen nur stellenweise (Adern); calm: Maske, wo die Fugen schwächer sind (Gesicht)"""
    P = T["P"]
    edge, cid = worley3(P, freq, seed)
    if sparse > 0:
        edge = np.where(fbm3(P, 5.0, seed + 9, 3) > sparse, edge, 1.0)
    if calm is not None:
        edge = edge + calm * 0.05
    col = np.asarray(base, np.float32) * ((1 - var / 2) + var * cid)[..., None] * (0.9 + (fbm3(P, 30.0, seed + 5, 2)[..., None] - 0.5) * 0.25)
    paint(T, mask, col, keep_shading=0.35)
    line = np.clip(1 - edge / width, 0, 1) ** 1.3
    halo = np.clip(1 - edge / (width * 3.5), 0, 1) ** 2
    paint(T, mask * line, line_col, keep_shading=0.0)
    glow(T, mask * np.maximum(line, halo * 0.35), glow_col)
    return edge, cid

def head_top(body, x=0.0, y=0.0):
    return surface(body, (x, y, 3.0), (0, 0, -1))

def back_pt(body, x, z, y0=1.5):
    return surface(body, (x, y0, z), (0, -1, 0))

def front_pt(body, x, z):
    return surface(body, (x, -1.5, z), (0, 1, 0))

def spikes_on_back(body, arm, bone, rows, mats, glow_from=None, r0=0.05):
    """Stacheln/Splitter am Rücken: rows = [(x, z, Länge, Neigung x), …]; mats = (Grund, Spitze) oder ein Material"""
    parts = []
    for k, (x, z, L, tx) in enumerate(rows):
        p, n = back_pt(body, x, z)
        if p is None:
            continue
        b0 = p - n * 0.02
        o = horn("Stachel%d" % k, tuple(b0), tuple(b0 + Vector((tx * 0.3 * L, 0.45 * L, 0.45 * L))), tuple(b0 + Vector((tx * 0.6 * L, 0.75 * L, 0.95 * L))),
                 r0 * (L / 0.2) ** 0.5, n=9, glow_from=glow_from)
        parts.append(give(o, *mats) if isinstance(mats, tuple) else give(o, mats))
    if parts:
        attach(join_parts(parts, "Ruecken_" + bone.split(":")[-1]), arm, bone)

def head_horns(body, arm, mats, size, spread=0.12, up=0.9, out=0.6, glow_from=None, y=0.0, drop=0.04):
    """zwei Hörner oben seitlich am Kopf"""
    parts = []
    for s_ in (-1, 1):
        p, n = head_top(body, s_ * spread, y)
        if p is None:
            continue
        b0 = p - n * 0.02 + Vector((0, 0, -drop))
        o = horn("Kopfhorn%d" % s_, tuple(b0), tuple(b0 + Vector((s_ * out * size * 0.6, 0.05 * size, up * size * 0.5))),
                 tuple(b0 + Vector((s_ * out * size, 0.15 * size, up * size))), size * 0.28, n=10, glow_from=glow_from)
        parts.append(give(o, *mats) if isinstance(mats, tuple) else give(o, mats))
    attach(join_parts(parts, "Kopfhoerner"), arm, "mixamorig:Head")

def shoulder_blocks(body, arm, mat, size, seed=0, glow_m=None, rise=0.06):
    """kantige Schulterblöcke (Basalt, Kristall) auf beiden Schultern"""
    for s_, side in ((1, "Left"), (-1, "Right")):
        a0 = bone_pt(arm, "mixamorig:%sArm" % side)
        p, n = surface(body, (a0.x + s_ * 0.03, a0.y, a0.z + 0.12), (0, 0, -1))
        c = (p if p is not None else a0) + Vector((s_ * 0.02, 0, rise * 0.5))
        parts = [block_at("Schulterblock" + side, c, (size, size * 0.95, size * 0.7), mat, seed + (s_ > 0), True, 1)]
        if glow_m is not None:
            parts.append(give(sphere("SchulterGlut" + side, tuple(c + Vector((0, 0, -size * 0.45))), size * 0.55, (1.1, 1.0, 0.5)), glow_m))
        attach(join_parts(parts, "Schulter" + side), arm, "mixamorig:%sArm" % side)

def lava_mats():
    return {
        "basalt": look("Basalt", (0.24, 0.2, 0.19), rough=0.75),
        "basalt2": look("Basalt2", (0.33, 0.27, 0.24), rough=0.8),
        "glut": look("Glut", (1.0, 0.42, 0.08), rough=0.5, emit=(1.0, 0.38, 0.05), strength=3.5),
        "glut_hell": look("GlutHell", (1.0, 0.75, 0.25), rough=0.4, emit=(1.0, 0.65, 0.15), strength=5.0),
        "iron": look("Eisen", (0.26, 0.24, 0.26), rough=0.45, metal=0.6),
    }

def face_zone(T, arm, half_w=0.2):
    """Gesicht: vorn am Kopf (dort bleiben Muster ruhig, damit Augen und Maul lesbar sind)"""
    P = T["P"]
    hc = bone_pt(arm, "mixamorig:Head", 0.4)
    return np.clip((hc.y - 0.06 - P[..., 1]) / 0.05, 0, 1) * np.clip((half_w - np.abs(P[..., 0])) / 0.05, 0, 1) * np.clip((P[..., 2] - bone_pt(arm, "mixamorig:Neck", 0.5).z) / 0.03, 0, 1)

def lava_skin(T, R, freq, width, seed, arm=None):
    """Lava-Haut: Basaltplatten mit glühenden Fugen; Anzug wird dunkle Schlacke mit Glutrand; Eisen statt Grau;
    Augen glühen orange (wie beim Magma-Golem)"""
    calm = face_zone(T, arm) if arm is not None else None
    cracked(T, R["skin"], freq, width, (0.24, 0.2, 0.19), (1.0, 0.5, 0.12), (1.0, 0.42, 0.06), seed=seed, calm=calm)
    suit = R["purple"] * (1 - R["head"])
    edge, cid = worley3(T["P"], freq * 0.7, seed + 50)
    paint(T, suit, gradient((0.13, 0.09, 0.08), (0.24, 0.13, 0.09), cid), keep_shading=0.6)
    glow(T, suit * np.clip(1 - edge / (width * 0.6), 0, 1) * 0.5, (1.0, 0.35, 0.05))
    paint(T, R["grey"], (0.3, 0.28, 0.3), keep_shading=0.6)
    eyes = R["white"] * R["head"]
    paint(T, eyes, (1.0, 0.78, 0.35), keep_shading=0.2)
    glow(T, eyes, (1.0, 0.55, 0.1))

# ---------------------------------------------------------------- Lava-Kolonie (Welt 4): Stil des Magma-Golems

@variante("lava_krabbler", "krabbler")
def glutwicht(arm, body):
    """Lava-Kolonie, leicht: Glutwicht – kleiner, flinker Kobold aus Basalt mit glühenden Fugen, glühenden
    Magmaflecken am Kopf, orange glühenden Augen, zwei Hörnchen mit Glutspitze und Basaltzacken am Rücken"""
    L = lava_mats()
    T = texels(body); R = regions(T, arm)
    lava_skin(T, R, 7.0, 0.006, 3, arm)
    spots = R["purple"] * R["head"]
    paint(T, spots, (0.95, 0.32, 0.06), keep_shading=0.35)
    glow(T, spots, (0.95, 0.28, 0.04))
    commit(T, strength=2.4)
    head_horns(body, arm, (L["basalt"], L["glut"]), 0.2, spread=0.17, up=1.0, out=0.45, glow_from=6, y=0.0, drop=0.06)
    spikes_on_back(body, arm, "mixamorig:Spine1", [(0.0, 0.82, 0.12, 0), (-0.08, 0.72, 0.09, -0.6), (0.08, 0.72, 0.09, 0.6)], (L["basalt"], L["glut"]), glow_from=6, r0=0.035)

@variante("lava_zombie", "zombie")
def schlackenwandler(arm, body):
    """Lava-Kolonie, mittel: Schlackenwandler – hagere Gestalt aus Basalt mit glühenden Fugen, Schlackenkleidung mit
    Glutrand, Basaltblöcken mit Glut auf den Schultern, glühenden Augen, Hörnern und Basaltstacheln am Rücken"""
    L = lava_mats()
    T = texels(body); R = regions(T, arm)
    lava_skin(T, R, 9.0, 0.006, 7, arm)
    spots = R["purple"] * R["head"]
    paint(T, spots, (0.2, 0.12, 0.1), keep_shading=0.4)
    commit(T, strength=2.2)
    head_horns(body, arm, (L["basalt"], L["glut"]), 0.17, spread=0.1, up=1.0, out=0.55, glow_from=6, y=0.02, drop=0.05)
    shoulder_blocks(body, arm, L["basalt2"], 0.085, seed=12, glow_m=L["glut"])
    spikes_on_back(body, arm, "mixamorig:Spine2", [(0.0, 1.08, 0.18, 0), (-0.1, 1.0, 0.14, -0.5), (0.1, 1.0, 0.14, 0.5), (0.0, 0.9, 0.12, 0)],
                   (L["basalt"], L["glut"]), glow_from=6, r0=0.04)

@variante("lava_brecher", "brecher")
def magmabrecher(arm, body):
    """Lava-Kolonie, stark: Magmabrecher – massiger Schläger: Basalthaut mit breiten Glutfugen, glühender
    Magmakragen, glühender Magmakern in der Brust, schwere Basaltschultern, Basaltschienen an den Unterarmen,
    Hörner und Rückenstacheln mit Glutspitzen"""
    L = lava_mats()
    T = texels(body); R = regions(T, arm)
    lava_skin(T, R, 7.0, 0.008, 11, arm)
    spots = R["purple"] * R["head"]
    paint(T, spots, (0.2, 0.12, 0.1), keep_shading=0.4)
    collar = np.maximum(R["white"] * (1 - R["head"]), R["collar"])
    paint(T, collar, (1.0, 0.6, 0.2), keep_shading=0.3)
    glow(T, collar, (1.0, 0.45, 0.08))
    commit(T, strength=2.6)
    head_horns(body, arm, (L["basalt"], L["glut"]), 0.22, spread=0.12, up=0.8, out=0.8, glow_from=6, y=0.02, drop=0.07)
    shoulder_blocks(body, arm, L["basalt"], 0.13, seed=21, glow_m=L["glut"], rise=0.08)
    # Magmakern in der Brust mit Schollen darum
    sp = bone_pt(arm, "mixamorig:Spine1", 0.6)
    p, n = front_pt(body, 0.0, sp.z)
    core = p + n * 0.01
    parts = [give(sphere("Brustkern", tuple(core), 0.075, (1.1, 0.6, 1.0)), L["glut_hell"])]
    for i, (dx, dz, sz) in enumerate(((-0.075, 0.06, 0.05), (0.08, 0.05, 0.045), (-0.07, -0.07, 0.048), (0.07, -0.07, 0.05), (0.0, 0.1, 0.04))):
        parts.append(block_at("Scholle%d" % i, core + Vector((dx, 0.0, dz)), (sz, sz * 0.6, sz), L["basalt2"], 40 + i, True, 1))
    attach(join_parts(parts, "Brustkern"), arm, "mixamorig:Spine1")
    # Basaltschienen an den Unterarmen
    for s_, side in ((1, "Left"), (-1, "Right")):
        f0, f1 = bone_pt(arm, "mixamorig:%sForeArm" % side, 0.2), bone_pt(arm, "mixamorig:%sForeArm" % side, 0.85)
        parts = [chunk_between("Schiene" + side, f0 + Vector((s_ * 0.05, 0.03, 0.02)), f1 + Vector((s_ * 0.05, 0.03, 0.02)), 0.06, L["basalt2"], 50 + s_, True, 1)]
        for k, t in enumerate((0.3, 0.7)):
            c = f0.lerp(f1, t) + Vector((s_ * 0.09, 0.05, 0.05))
            parts.append(give(horn("ArmZacke%s%d" % (side, k), tuple(c), tuple(c + Vector((s_ * 0.04, 0.03, 0.05))), tuple(c + Vector((s_ * 0.06, 0.06, 0.1))), 0.03, n=8, glow_from=5), L["basalt"], L["glut"]))
        attach(join_parts(parts, "Unterarm" + side), arm, "mixamorig:%sForeArm" % side)
    spikes_on_back(body, arm, "mixamorig:Spine2", [(0.0, 1.22, 0.24, 0), (-0.16, 1.14, 0.19, -0.5), (0.16, 1.14, 0.19, 0.5), (-0.08, 0.98, 0.15, -0.3), (0.08, 0.98, 0.15, 0.3)],
                   (L["basalt"], L["glut"]), glow_from=6, r0=0.05)

# ---------------------------------------------------------------- Giftsumpf (Welt 5): Stil der Giftkröte

def gift_mats():
    return {
        "leg": look("Kroetenbein", (0.42, 0.55, 0.2), rough=0.6),
        "belly": look("Bauch", (0.78, 0.82, 0.45), rough=0.6),
        "wart": look("Giftwarze", (0.55, 1.0, 0.25), rough=0.25, emit=(0.45, 1.0, 0.15), strength=1.6),
        "eye": look("Kroetenauge", (1.0, 0.8, 0.15), rough=0.15, emit=(0.9, 0.6, 0.05), strength=0.8),
        "black": look("Pupille", (0.04, 0.03, 0.03), rough=0.3),
        "mouth": look("Maulspalt", (0.18, 0.05, 0.12), rough=0.5),
        "toxic": look("Gifttropfen", (0.6, 1.0, 0.3), rough=0.1, emit=(0.5, 1.0, 0.2), strength=1.8),
        "stalk": look("Stiel", (0.9, 0.86, 0.75), rough=0.6),
        "cap": look("Pilzhut", (0.7, 0.25, 0.85), rough=0.45, emit=(0.6, 0.15, 0.8), strength=0.5),
        "dot": look("Pilzpunkt", (0.97, 0.95, 0.9), rough=0.5),
    }

def toad_skin(T, mask, seed, freq=6.0, belly_mask=None):
    """Krötenhaut wie bei der Giftkröte: oliv, violette Flecken mit dunklem Rand (im Raum, ohne Nähte), heller Bauch"""
    P = T["P"]
    n = fbm3(P, freq, seed, 3)
    k = np.clip((n - 0.58) * 45, 0, 1)
    ring = np.clip(1 - np.abs(n - 0.575) * 70, 0, 1)
    col = np.asarray((0.38, 0.52, 0.16), np.float32) * (0.9 + (fbm3(P, 40.0, seed + 3, 2)[..., None] - 0.5) * 0.25)
    paint(T, mask, col, keep_shading=0.4)
    paint(T, mask * k, (0.5, 0.17, 0.6), keep_shading=0.3)
    paint(T, mask * ring * 0.55, (0.16, 0.08, 0.18), keep_shading=0.0)
    if belly_mask is not None:
        paint(T, mask * belly_mask, (0.8, 0.83, 0.48), keep_shading=0.4)

def mushroom(name, p, n, h, r, M, dots=True):
    parts = [give(tube(name + "Stiel", [tuple(p - n * 0.01), tuple(p + n * h * 0.5), tuple(p + n * h)], [r * 0.3, r * 0.26, r * 0.24]), M["stalk"])]
    cap_ = sphere(name + "Hut", (0, 0, 0), r, (1, 1, 0.55)); cap_.location = p + n * h
    cap_.rotation_euler = n.to_track_quat('Z', 'Y').to_euler()
    parts.append(give(cap_, M["cap"]))
    if dots:
        q = n.to_track_quat('Z', 'Y').to_matrix()
        for i in range(5):
            a = i * 2 * math.pi / 5 + 0.4
            d = q @ Vector((math.cos(a) * 0.62, math.sin(a) * 0.62, 0.42)).normalized()
            parts.append(give(sphere(name + "Punkt%d" % i, tuple(p + n * h + Vector((d.x * r, d.y * r, d.z * r * 0.6))), r * 0.14, (1, 1, 0.5)), M["dot"]))
    return parts

def warts_on(body, center, dirs, M, rmin=0.012, rmax=0.026, seed=1):
    rnd = random.Random(seed)
    out = []
    for i, (p, n) in enumerate(on_surface(body, center, dirs, lift=0.0)):
        out.append(give(sphere("Warze%d" % i, tuple(p), rnd.uniform(rmin, rmax), (1, 1, 0.7)), M["wart"]))
    return out

def toad_eyes(c_left, c_right, r, M, parts):
    for s_, c in ((-1, c_left), (1, c_right)):
        parts.append(give(sphere("Augenwulst%d" % s_, tuple(c), r * 1.3, (1, 0.95, 0.9)), M["leg"]))
        parts.append(give(sphere("Augapfel%d" % s_, tuple(c + Vector((0, -r * 0.6, r * 0.4))), r), M["eye"]))
        parts.append(give(sphere("Schlitz%d" % s_, tuple(c + Vector((0, -r * 1.52, r * 0.45))), r * 0.4, (1.5, 0.35, 0.45)), M["black"]))
        parts.append(give(tube("Lid%d" % s_, [tuple(c + Vector((-r * 1.05, -r * 0.65, r * 0.8))), tuple(c + Vector((0, -r, r * 1.13))), tuple(c + Vector((r * 1.05, -r * 0.65, r * 0.8)))],
                              [r * 0.33, r * 0.4, r * 0.33]), M["leg"]))

@variante("gift_schleimling", "schleimling")
def kroetling(arm, body):
    """Giftsumpf, leicht: Krötling – kleine, runde Kröte (wie ein Junges der Giftkröte): oliv mit violetten Flecken,
    große gelbe Augen mit Schlitzpupillen, breites Maul mit Gifttropfen, leuchtende Giftwarzen, ein Giftpilz auf
    dem Kopf, kleine Vorderfüße. Eigene Figur auf dem Skelett des Schleimlings (hüpft wie er)."""
    M = gift_mats()
    skin = look("KroetlingHaut", (1.0, 1.0, 1.0), rough=0.55)
    prof = [(0.62, 0.0), (0.61, 0.1), (0.585, 0.2), (0.54, 0.29), (0.47, 0.36), (0.39, 0.41), (0.3, 0.43), (0.21, 0.43), (0.13, 0.41),
            (0.07, 0.37), (0.03, 0.3), (0.006, 0.18), (0.0, 0.0)]
    g = lathe("Kroetling", prof, segs=64)
    for v in g.data.vertices:
        if v.co.y < 0:
            v.co.z *= 1.0 - 0.08 * min(1.0, -v.co.y / 0.4) * max(0.0, (v.co.z - 0.25) / 0.35)
    H_, W_ = 1024, 1024
    vv = np.linspace(0, 1, H_)[:, None] * np.ones((1, W_))
    spots = fbm(H_, W_, 15, 95)
    grad = np.clip((vv - 0.38) / 0.16, 0, 1)
    col = np.asarray((0.84, 0.86, 0.5)) * (1 - grad[..., None]) + np.asarray((0.38, 0.52, 0.16)) * grad[..., None]
    k = (np.clip((spots - 0.58) * 45, 0, 1) * grad)[..., None]
    ring = (np.clip(1 - np.abs(spots - 0.575) * 70, 0, 1) * grad)[..., None]
    col = np.clip(col + ((fbm(H_, W_, 40, 96, 2) - 0.5) * 0.12)[..., None], 0, 1)
    col = col * (1 - k) + np.asarray((0.5, 0.17, 0.6)) * k
    col = col * (1 - ring * 0.55) + np.asarray((0.16, 0.08, 0.18)) * (ring * 0.55)
    arr = np.ones((H_, W_, 4), np.float32); arr[..., :3] = col
    lathe_texture(skin, arr)
    give(g, skin)
    bpy.context.view_layer.update()
    face = []
    cl = []
    for s_ in (-1, 1):
        p, n = surface(g, (s_ * 0.16, -2.0, 0.5), (0, 1, 0))
        cl.append(p + Vector((0, 0.035, 0.045)))
    toad_eyes(cl[0], cl[1], 0.07, M, face)
    hits = on_surface(g, (0, 0, 0.3), [(math.sin(a), -math.cos(a), 0.1 * (abs(a) / 1.05) ** 2 - 0.05) for a in [math.radians(t) for t in range(-58, 62, 8)]], lift=0.004)
    face.append(give(tube("Maul", [tuple(p) for p, n in hits], [0.01] + [0.018] * (len(hits) - 2) + [0.01], segs=8), M["mouth"]))
    face.append(give(tube("Lippe", [tuple(p + n * 0.01 + Vector((0, 0, 0.018))) for p, n in hits[1:-1]], [0.013] * (len(hits) - 2), segs=8), M["leg"]))
    p, n = hits[-1]
    face.append(give(tube("Giftfaden", [tuple(p), tuple(p + Vector((0, -0.01, -0.05))), tuple(p + Vector((0, -0.012, -0.08)))], [0.013, 0.008, 0.01]), M["toxic"]))
    face.append(give(sphere("Gifttropfen", tuple(p + Vector((0, -0.012, -0.093))), 0.017, (1, 1, 1.2)), M["toxic"]))
    rnd = random.Random(29)
    for i in range(18):
        a = rnd.uniform(-2.4, 2.4) + math.pi / 2
        el = rnd.uniform(0.3, 1.2)
        d = Vector((math.cos(a) * math.cos(el), math.sin(a) * math.cos(el), math.sin(el)))
        p, n = surface(g, Vector((0, 0, 0.25)) + d * 2.0, -d)
        if p is None or p.z < 0.2:
            continue
        face.append(give(sphere("Warze%d" % i, tuple(p), rnd.uniform(0.015, 0.03), (1, 1, 0.7)), M["wart"]))
    p, n = surface(g, (0.06, 0.12, 2.0), (0, 0, -1))
    face += mushroom("Pilz", p, (n + Vector((0.2, 0.25, 0))).normalized(), 0.09, 0.06, M)
    attach(join_parts(face, "Kroetling_Kopf"), arm, "Top")
    feet = []
    for s_ in (-1, 1):
        w0 = Vector((s_ * 0.24, -0.33, 0.035))
        feet.append(give(sphere("Fuss%d" % s_, tuple(w0), 0.055, (1.1, 1.2, 0.55)), M["leg"]))
        for k in range(3):
            a = math.radians(-35 + 35 * k)
            d = Vector((s_ * math.sin(a + 0.3) * 0.6, -math.cos(a + 0.3), 0))
            feet.append(give(sphere("Zeh%d_%d" % (s_, k), tuple(w0 + d * 0.06 + Vector((0, 0, -0.01))), 0.022, (1, 1, 0.8)), M["belly"]))
    attach(join_parts(feet, "Kroetling_Fuesse"), arm, "Body")
    skin_to(g, arm, lambda c: {"Top": smooth01((c.z - 0.12) / 0.3), "Body": 1 - smooth01((c.z - 0.12) / 0.3)})
    dampen_scale(arm, ("Body", "Top"), 0.45)
    remove_body(body)

@variante("gift_zombie", "zombie")
def moorschlurfer(arm, body):
    """Giftsumpf, mittel: Moorschlurfer – hagerer Sumpfgänger mit Krötenkopf (große gelbe Augen mit Schlitzpupillen,
    breites Maul mit Gifttropfen), olivgrüner Haut mit violetten Flecken, moosig-dunklen Lumpen, leuchtenden
    Giftwarzen und Giftpilzen auf der Schulter"""
    M = gift_mats()
    skin_m = look("MoorHaut", (0.4, 0.54, 0.17), rough=0.6)
    T = texels(body); R = regions(T, arm)
    toad_skin(T, R["skin"], 31, freq=7.0)
    rags = R["purple"] * (1 - R["head"])
    P = T["P"]
    paint(T, rags, gradient((0.16, 0.2, 0.1), (0.3, 0.27, 0.14), fbm3(P, 9.0, 33, 3)), keep_shading=0.6)
    paint(T, R["grey"], (0.45, 0.4, 0.3), keep_shading=0.6)
    commit(T, strength=1.0)
    # Krötenkopf statt des alten Kopfes
    c0, half = cut_head(body)
    H = "mixamorig:Head"
    hc = c0 + Vector((0, -0.03, -0.04))
    R_ = max(half.x, half.z) * 0.95
    head = sphere("Kroetenkopf", tuple(hc), R_, (1.18, 1.0, 0.78), segs=(48, 28))
    give(head, skin_m)
    parts = [head]
    fy = hc.y - R_ * 0.95
    toad_eyes(Vector((hc.x - R_ * 0.48, hc.y - R_ * 0.55, hc.z + R_ * 0.52)), Vector((hc.x + R_ * 0.48, hc.y - R_ * 0.55, hc.z + R_ * 0.52)), R_ * 0.3, M, parts)
    bpy.context.view_layer.update()
    hits = on_surface(head, hc, [(math.sin(a), -math.cos(a), -0.25 + 0.12 * (abs(a) / 1.1) ** 2) for a in [math.radians(t) for t in range(-62, 66, 8)]], lift=0.003)
    parts.append(give(tube("Maul", [tuple(p) for p, n in hits], [0.008] + [0.016] * (len(hits) - 2) + [0.008], segs=8), M["mouth"]))
    parts.append(give(tube("Lippe", [tuple(p + n * 0.008 + Vector((0, 0, 0.016))) for p, n in hits[1:-1]], [0.011] * (len(hits) - 2), segs=8), M["leg"]))
    p, n = hits[0]
    parts.append(give(tube("Giftfaden", [tuple(p), tuple(p + Vector((0, -0.01, -0.05))), tuple(p + Vector((0, -0.012, -0.08)))], [0.012, 0.008, 0.009]), M["toxic"]))
    parts.append(give(sphere("Gifttropfen", tuple(p + Vector((0, -0.012, -0.092))), 0.016, (1, 1, 1.2)), M["toxic"]))
    parts += warts_on(head, hc, [(x, y, z) for x, y, z in ((-0.4, 0.5, 0.8), (0.3, 0.6, 0.7), (0.0, 0.8, 0.6), (-0.7, 0.3, 0.3), (0.7, 0.3, 0.35), (0.2, 0.2, 1.0), (-0.2, 0.9, 0.2))], M, 0.012, 0.022, seed=3)
    attach(join_parts(parts, "Kroetenkopf"), arm, H)
    # Giftpilze auf der linken Schulter, Warzen an Schultern und Armen
    sh = bone_pt(arm, "mixamorig:LeftArm")
    sp = []
    for i, (dx, dy, h, r) in enumerate(((0.0, 0.02, 0.1, 0.055), (0.07, 0.07, 0.07, 0.04), (-0.05, 0.06, 0.06, 0.032))):
        p, n = surface(body, (sh.x + 0.03 + dx, sh.y + dy, sh.z + 0.12), (0, 0, -1))
        if p is not None:
            sp += mushroom("Pilz%d" % i, p, n, h, r, M)
    attach(join_parts(sp, "SchulterPilze"), arm, "mixamorig:LeftShoulder")
    for s_, side in ((1, "Left"), (-1, "Right")):
        a = bone_pt(arm, "mixamorig:%sArm" % side, 0.5)
        w = warts_on(body, a, [(s_, 0.2, 0.5), (s_, -0.3, 0.3), (s_ * 0.6, 0.8, 0.2), (s_, 0.0, -0.2)], M, 0.01, 0.018, seed=7 + s_)
        if w:
            attach(join_parts(w, "ArmWarzen" + side), arm, "mixamorig:%sArm" % side)
    sp2 = bone_pt(arm, "mixamorig:Spine1")
    w = warts_on(body, sp2, [(x, 1.0, z) for x, z in ((-0.3, 0.4), (0.25, 0.5), (0.0, 0.1), (-0.15, -0.3), (0.3, -0.1))], M, 0.012, 0.022, seed=19)
    attach(join_parts(w, "RueckenWarzen"), arm, "mixamorig:Spine1")

@variante("gift_panzerkaefer", "panzerkaefer")
def pilzpanzer(arm, body):
    """Giftsumpf, stark: Pilzpanzer – schwerer Panzerläufer, auf dessen moosigem Krötenpanzer große violett
    leuchtende Giftpilze wachsen, mit leuchtenden Giftwarzen, olivgrüner Haut, gelben Augen und Gifttropfen am Maul"""
    M = gift_mats()
    T = texels(body)
    px, P, N = T["px"], T["P"], T["N"]
    teal = hue_mask(px, 0.49, 0.08, 0.3)
    red = np.maximum(hue_mask(px, 0.02, 0.06, 0.35), hue_mask(px, 0.97, 0.05, 0.3))
    hh, s, v = hsv(px)
    beige = np.clip((0.6 - s) / 0.1, 0, 1) * np.clip((v - 0.5) / 0.1, 0, 1) * hue_mask(px, 0.11, 0.07, 0.08)
    # Panzer: moosig dunkeloliv mit violetten Flecken, Moos oben heller
    toad_skin(T, teal, 41, freq=5.0)
    moss = np.clip((N[..., 2] - 0.5) / 0.3, 0, 1) * np.clip((fbm3(P, 12.0, 43, 3) - 0.45) / 0.1, 0, 1)
    paint(T, teal * moss, (0.3, 0.45, 0.12), keep_shading=0.5)
    paint(T, red, (0.36, 0.44, 0.17), keep_shading=0.6)
    paint(T, beige, (0.8, 0.83, 0.48), keep_shading=0.5)
    # Augen (türkis/blau im Grundmodell, nur am Kopf) werden gelb
    hb = bone_pt(arm, "Head", 0.0)
    head = np.clip((hb.y - P[..., 1]) / 0.03, 0, 1)
    blue = hue_mask(px, 0.55, 0.08, 0.3) * head
    paint(T, blue, (1.0, 0.8, 0.15), keep_shading=0.4)
    commit(T, strength=0.8)
    # große Giftpilze auf dem Panzer
    shell = []
    for i, (x, y, h, r, tx) in enumerate(((0.02, 0.08, 0.16, 0.1, 0.0), (-0.15, 0.12, 0.11, 0.07, -0.4), (0.16, 0.02, 0.1, 0.065, 0.4),
                                          (0.06, -0.1, 0.07, 0.045, 0.2), (-0.09, -0.06, 0.06, 0.04, -0.3))):
        p, n = surface(body, (x, y, 2.0), (0, 0, -1))
        if p is None:
            continue
        shell += mushroom("Pilz%d" % i, p, (n + Vector((tx, 0.1, 0.0))).normalized(), h, r, M)
    rnd = random.Random(47)
    for i in range(16):
        a = rnd.uniform(0, 2 * math.pi); el = rnd.uniform(0.2, 1.1)
        d = Vector((math.cos(a) * math.cos(el), math.sin(a) * math.cos(el), math.sin(el)))
        p, n = surface(body, Vector((0, 0.03, 0.18)) + d * 2.0, -d)
        if p is None or p.z < 0.18:
            continue
        shell.append(give(sphere("Warze%d" % i, tuple(p), rnd.uniform(0.014, 0.026), (1, 1, 0.7)), M["wart"]))
    attach(join_parts(shell, "Pilzpanzer"), arm, "Body")
    # Gifttropfen an den Mundwinkeln
    h0 = bone_pt(arm, "Head", 0.6)
    drip = []
    for s_ in (-1, 1):
        q, m = surface(body, (s_ * 0.07, -1.5, h0.z - 0.04), (0, 1, 0))
        if q is None:
            continue
        drip.append(give(tube("Giftfaden%d" % s_, [tuple(q), tuple(q + Vector((0, -0.01, -0.04))), tuple(q + Vector((0, -0.012, -0.07)))], [0.012, 0.008, 0.009]), M["toxic"]))
        drip.append(give(sphere("Gifttropfen%d" % s_, tuple(q + Vector((0, -0.012, -0.082))), 0.015, (1, 1, 1.2)), M["toxic"]))
    attach(join_parts(drip, "Gifttropfen"), arm, "Head")

# ---------------------------------------------------------------- Kristallhöhlen (Welt 6): Stil des Kristallkäfers

def crystal_mats():
    return {
        "cr": look("Kristall", (1.0, 0.6, 0.95), rough=0.1, emit=(0.95, 0.4, 0.9), strength=0.9),
        "cr2": look("Kristall2", (0.75, 0.5, 1.0), rough=0.1, emit=(0.6, 0.35, 1.0), strength=1.1),
        "cr3": look("Kristall3", (0.55, 0.95, 1.0), rough=0.1, emit=(0.35, 0.9, 1.0), strength=1.3),
        "slate": look("Schiefer", (0.3, 0.27, 0.38), rough=0.55),
    }

def crystal_skin(T, mask, freq, width, seed):
    """dunkler Schiefer mit pink leuchtenden Kristalladern (wie der Panzer des Kristallkäfers)"""
    cracked(T, mask, freq, width, (0.3, 0.24, 0.4), (1.0, 0.55, 0.95), (1.0, 0.4, 0.92), seed=seed, var=0.35, sparse=0.47)

def cluster(name, p, n, h, r, mats, rnd, count=3, spread=25):
    """Kristallgruppe: ein großer Kristall und kleinere schräg daneben, Füße stecken in der Oberfläche"""
    out = []
    for j in range(count):
        d = (n + Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * (0.0 if j == 0 else spread / 60)).normalized()
        off = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * r * (0 if j == 0 else 0.8)
        out.append(shard("%s_%d" % (name, j), p - n * r * 0.5 + off, d, h * (1.0 if j == 0 else rnd.uniform(0.45, 0.7)), r * (1.0 if j == 0 else 0.65), mats[j % len(mats)]))
    return out

@variante("kristall_krabbler", "krabbler")
def splitterwicht(arm, body):
    """Kristallhöhlen, leicht: Splitterwicht – kleiner Höhlenkobold aus dunklem Schiefer mit pink leuchtenden
    Kristalladern, einem Kamm aus Kristallen auf dem Kopf, pink leuchtenden Augen und Kristallsplittern an den Schultern"""
    C = crystal_mats()
    T = texels(body); R = regions(T, arm)
    crystal_skin(T, R["skin"], 11.0, 0.005, 5)
    paint(T, R["purple"] * (1 - R["head"]), (0.3, 0.15, 0.46), keep_shading=0.6)
    spots = R["purple"] * R["head"]
    paint(T, spots, (0.85, 0.45, 1.0), keep_shading=0.3)
    glow(T, spots, (0.7, 0.3, 1.0))
    paint(T, R["grey"], (0.5, 0.55, 0.7), keep_shading=0.6)
    eyes = R["white"] * R["head"]
    paint(T, eyes, (1.0, 0.75, 0.97), keep_shading=0.2)
    glow(T, eyes, (1.0, 0.35, 0.9))
    commit(T, strength=1.8)
    rnd = random.Random(11)
    parts = []
    for k, (x, y, h, r) in enumerate(((0.0, 0.02, 0.24, 0.05), (0.0, 0.16, 0.18, 0.045), (-0.12, 0.06, 0.15, 0.04), (0.12, 0.06, 0.15, 0.04), (0.0, -0.12, 0.13, 0.035))):
        p, n = head_top(body, x, y)
        if p is not None:
            parts += cluster("Kopfkristall%d" % k, p, (n + Vector((x * 2, y * 1.5, 0.4))).normalized(), h, r, (C["cr"], C["cr2"], C["cr3"])[k % 3:] + (C["cr"],), rnd, count=2)
    attach(join_parts(parts, "Kopfkristalle"), arm, "mixamorig:Head")
    for s_, side in ((1, "Left"), (-1, "Right")):
        a0 = bone_pt(arm, "mixamorig:%sArm" % side)
        p, n = surface(body, (a0.x, a0.y, a0.z + 0.1), (0, 0, -1))
        if p is not None:
            attach(join_parts(cluster("Schulterkristall" + side, p, (n + Vector((s_ * 0.6, 0.2, 0))).normalized(), 0.13, 0.035, (C["cr2"], C["cr"]), rnd, count=3),
                              "Schulterkristall" + side), arm, "mixamorig:%sArm" % side)

@variante("kristall_tentakler", "tentakler")
def glimmerfluegler(arm, body):
    """Kristallhöhlen, mittel: Glimmerflügler – Flugwesen aus dunklem Schiefer mit pink leuchtenden Adern, Flügeln
    aus facettiertem Kristall (pink, violett, cyan, mit leuchtenden Kanten), Kristallhörnern, Kristallsplittern an
    der Flügelkante und einem Kristall auf der Stirn"""
    C = crystal_mats()
    T = texels(body)
    px, P = T["px"], T["P"]
    red = hue_mask(px, 0.02, 0.06, 0.35)
    teal = hue_mask(px, 0.49, 0.08, 0.3)
    hh, s, v = hsv(px)
    beige = np.clip((0.6 - s) / 0.1, 0, 1) * np.clip((v - 0.5) / 0.1, 0, 1) * hue_mask(px, 0.11, 0.07, 0.08)
    white = np.clip((0.15 - s) / 0.06, 0, 1) * np.clip((v - 0.8) / 0.06, 0, 1)
    crystal_skin(T, red, 10.0, 0.005, 9)
    edge, cid = worley3(P, 12.0, 13)
    facet = np.where((cid < 0.4)[..., None], np.asarray((0.95, 0.45, 0.9), np.float32),
                     np.where((cid < 0.75)[..., None], np.asarray((0.6, 0.4, 1.0), np.float32), np.asarray((0.45, 0.9, 1.0), np.float32)))
    paint(T, teal, facet * (0.75 + 0.25 * cid[..., None]), keep_shading=0.25)
    line = np.clip(1 - edge / 0.005, 0, 1)
    paint(T, teal * line, (1.0, 0.92, 1.0), keep_shading=0.0)
    glow(T, teal * (0.35 + line * 0.6), (0.85, 0.45, 1.0))
    paint(T, beige, (0.95, 0.55, 0.95), keep_shading=0.4)
    glow(T, beige * 0.6, (0.9, 0.35, 0.9))
    paint(T, white, (1.0, 0.75, 0.97), keep_shading=0.2)
    glow(T, white, (1.0, 0.35, 0.9))
    commit(T, strength=1.3)
    rnd = random.Random(17)
    for side, chain in ((1, ("Bone_031", "Bone_030", "Bone_029")), (-1, ("Bone_026", "Bone_025", "Bone_024"))):
        for k, (bone, t, h) in enumerate(((chain[1], 0.3, 0.13), (chain[1], 0.8, 0.18), (chain[2], 0.35, 0.15), (chain[2], 0.75, 0.11))):
            b0 = bone_pt(arm, bone, t)
            p, n = surface(body, b0 + Vector((0, 0, 1.0)), (0, 0, -1))
            base = (p - n * 0.02) if p is not None else b0
            attach(shard("FluegelKristall%d_%d" % (side, k), base, Vector((side * 0.5, 0.1, 1.0)), h, 0.032, (C["cr"], C["cr2"], C["cr3"])[k % 3]), arm, bone)
        tip = bone_pt(arm, chain[2], 1.0)
        attach(shard("FluegelSpitze%d" % side, tip, Vector((side * 0.6, 0.0, -1.0)), 0.13, 0.03, C["cr3"]), arm, chain[2])
    # Kristalle an den Hornspitzen und auf der Stirn
    for chain in (("Bone_009", "Bone_008", "Bone_006"), ("Bone_013", "Bone_012", "Bone_010")):
        tip = bone_pt(arm, chain[2], 1.0)
        attach(shard("HornKristall" + chain[0], tip - Vector((0, 0, 0.04)), Vector((0, 0.1, 1.0)), 0.11, 0.03, C["cr"]), arm, chain[2])
    p, n = front_pt(body, 0.0, 1.12)
    if p is not None:
        attach(join_parts(cluster("Stirnkristall", p, (n + Vector((0, 0, 0.9))).normalized(), 0.12, 0.032, (C["cr3"], C["cr"]), rnd, count=2), "Stirnkristall"), arm, "Bone_001")

@variante("kristall_brecher", "brecher")
def drusenbrecher(arm, body):
    """Kristallhöhlen, stark: Drusenbrecher – massiger Höhlenriese aus dunklem Schiefer mit pink leuchtenden Adern,
    Kristalldrusen auf Schultern und Rücken, Kristallsplittern an den Unterarmen, einem Kristallhorn auf der Stirn,
    leuchtendem Kristallkragen und pink leuchtenden Augen"""
    C = crystal_mats()
    T = texels(body); R = regions(T, arm)
    crystal_skin(T, R["skin"], 8.0, 0.006, 15)
    paint(T, R["purple"] * (1 - R["head"]), (0.3, 0.15, 0.46), keep_shading=0.6)
    paint(T, R["purple"] * R["head"], (0.24, 0.2, 0.32), keep_shading=0.5)
    paint(T, R["grey"], (0.5, 0.55, 0.7), keep_shading=0.6)
    collar = np.maximum(R["white"] * (1 - R["head"]), R["collar"])
    paint(T, collar, (0.6, 0.95, 1.0), keep_shading=0.3)
    glow(T, collar, (0.35, 0.85, 1.0))
    eyes = R["white"] * R["head"]
    paint(T, eyes, (1.0, 0.75, 0.97), keep_shading=0.2)
    glow(T, eyes, (1.0, 0.35, 0.9))
    commit(T, strength=1.8)
    rnd = random.Random(23)
    mats = (C["cr"], C["cr2"], C["cr3"])
    for s_, side in ((1, "Left"), (-1, "Right")):
        a0 = bone_pt(arm, "mixamorig:%sArm" % side)
        parts = []
        for k, (dx, dy, h, r) in enumerate(((0.0, 0.0, 0.2, 0.05), (-s_ * 0.08, 0.06, 0.15, 0.04), (s_ * 0.05, -0.07, 0.13, 0.035))):
            p, n = surface(body, (a0.x + dx, a0.y + dy, a0.z + 0.15), (0, 0, -1))
            if p is not None:
                parts += cluster("Druse%s%d" % (side, k), p, (n + Vector((s_ * 0.5, 0.1, 0))).normalized(), h, r, mats[k % 3:] + mats[:k % 3], rnd, count=3)
        attach(join_parts(parts, "Druse" + side), arm, "mixamorig:%sArm" % side)
        f0, f1 = bone_pt(arm, "mixamorig:%sForeArm" % side, 0.2), bone_pt(arm, "mixamorig:%sForeArm" % side, 0.85)
        fp = []
        for k, t in enumerate((0.25, 0.55, 0.85)):
            c = f0.lerp(f1, t)
            p, n = surface(body, c + Vector((s_ * 0.5, 0.5, 0.3)), (-s_ * 0.5, -0.5, -0.3))
            if p is not None:
                fp.append(shard("ArmSplitter%s%d" % (side, k), p - n * 0.02, (n + Vector((0, 0.3, 0.3))).normalized(), 0.11 + 0.03 * (k == 1), 0.03, mats[k % 3]))
        attach(join_parts(fp, "ArmKristall" + side), arm, "mixamorig:%sForeArm" % side)
    back = []
    for k, (x, z, h, r) in enumerate(((0.0, 1.2, 0.26, 0.06), (-0.17, 1.12, 0.2, 0.05), (0.17, 1.12, 0.2, 0.05), (-0.08, 0.98, 0.15, 0.04), (0.09, 0.97, 0.15, 0.04))):
        p, n = back_pt(body, x, z)
        if p is not None:
            back += cluster("Rueckendruse%d" % k, p, (n + Vector((x * 2, 0, 0.7))).normalized(), h, r, mats[k % 3:] + mats[:k % 3], rnd, count=3)
    attach(join_parts(back, "Rueckendrusen"), arm, "mixamorig:Spine2")
    p, n = front_pt(body, 0.0, 1.62)
    if p is not None:
        attach(join_parts(cluster("Stirnhorn", p, (n + Vector((0, 0, 1.3))).normalized(), 0.2, 0.045, (C["cr"], C["cr2"]), rnd, count=2), "Stirnhorn"), arm, "mixamorig:Head")

# ---------------------------------------------------------------- Sternenwüste (Welt 7): Stil des Nashorn-Kriegers

def sand_mats():
    return {
        "hide": look("Nashornhaut", (0.6, 0.58, 0.56), rough=0.75),
        "hide_dark": look("NashornhautDunkel", (0.45, 0.43, 0.42), rough=0.8),
        "ivory": look("Horn", (0.93, 0.86, 0.7), rough=0.35),
        "stone": look("Sandstein", (0.86, 0.68, 0.42), rough=0.85),
        "stone2": look("Sandstein2", (0.75, 0.56, 0.33), rough=0.85),
        "brass": look("Messing", (0.9, 0.66, 0.3), rough=0.3, metal=0.9),
        "cloth": look("Wuestentuch", (0.82, 0.7, 0.5), rough=0.9),
    }

def hide_skin(T, mask, seed, freq=22.0):
    """graue Nashornhaut mit Falten (feine dunkle Linien im Raum)"""
    P = T["P"]
    edge, cid = worley3(P, freq, seed)
    paint(T, mask, np.asarray((0.62, 0.6, 0.58), np.float32) * (0.9 + 0.2 * cid[..., None]), keep_shading=0.5)
    paint(T, mask * np.clip(1 - edge / 0.0025, 0, 1) * 0.8, (0.3, 0.28, 0.27), keep_shading=0.0)

def sand_cloth(T, R):
    """Anzug wird Lederrüstung, Grau wird Messing, Kopfflecken Sandstein"""
    paint(T, R["purple"] * (1 - R["head"]), (0.55, 0.36, 0.2), keep_shading=0.6)
    paint(T, R["grey"], (0.85, 0.62, 0.3), keep_shading=0.5)
    paint(T, R["purple"] * R["head"], (0.86, 0.68, 0.42), keep_shading=0.5)

def stone_dome(name, c, r, s_, M, arm, bone, rivets=8):
    """Schulterpanzer aus Sandstein mit Messingband und Nieten (wie beim Nashorn-Krieger)"""
    c = Vector(c)
    parts = []
    dome = sphere(name, (0, 0, 0), r, (1.0, 1.08, 0.5)); dome.location = c; dome.rotation_euler = (0, math.radians(-s_ * 22), 0)
    parts.append(give(dome, M["stone"]))
    t = torus(name + "Band", tuple(c - Vector((0, 0, r * 0.05))), r * 0.94, r * 0.085, rot=(0, -s_ * 22, 0)); t.scale = (1.0, 1.08, 1.0)
    parts.append(give(t, M["brass"]))
    for a in range(rivets):
        ang = a * 2 * math.pi / rivets
        parts.append(give(sphere(name + "Niete%d" % a, tuple(c + Vector((r * 0.9 * math.cos(ang), r * 0.94 * math.sin(ang), r * 0.17))), r * 0.09), M["brass"]))
    attach(join_parts(parts, name), arm, bone)

def face_horn(body, arm, M, z, length, r0, bone="mixamorig:Head", small=True):
    """Nashornhorn vorn am Kopf (großes Horn, darüber ein kleines)"""
    p, n = front_pt(body, 0.0, z)
    parts = [give(horn("Nasenhorn", tuple(p - n * 0.03), tuple(p + Vector((0, -length * 0.5, length * 0.25))), tuple(p + Vector((0, -length * 0.35, length))), r0, n=12), M["ivory"])]
    if small:
        q, m = front_pt(body, 0.0, z + length * 0.55)
        if q is not None:
            parts.append(give(horn("Stirnhorn", tuple(q - m * 0.02), tuple(q + Vector((0, -length * 0.25, length * 0.15))), tuple(q + Vector((0, -length * 0.18, length * 0.45))), r0 * 0.55, n=9), M["ivory"]))
    attach(join_parts(parts, "Hoerner"), arm, bone)

@variante("sand_krabbler", "krabbler")
def hornling(arm, body):
    """Sternenwüste, leicht: Hornling – flinker Wüstenkobold mit grauer Faltenhaut, Nashornhorn vorn am Kopf,
    Sandsteinflecken, Lederrüstung mit Messing und kleinem Sandsteinpanzer auf der Schulter"""
    M = sand_mats()
    T = texels(body); R = regions(T, arm)
    hide_skin(T, R["skin"], 71)
    sand_cloth(T, R)
    commit(T)
    face_horn(body, arm, M, bone_pt(arm, "mixamorig:Head", 0.35).z, 0.17, 0.05)
    a0 = bone_pt(arm, "mixamorig:LeftArm")
    p, n = surface(body, (a0.x, a0.y, a0.z + 0.1), (0, 0, -1))
    stone_dome("Panzer", (p if p is not None else a0) + Vector((0.02, 0, 0.01)), 0.08, 1, M, arm, "mixamorig:LeftArm", rivets=6)

@variante("sand_zombie", "zombie")
def duenenwaechter(arm, body):
    """Sternenwüste, mittel: Dünenwächter – hagerer Wüstenkrieger mit grauer Faltenhaut, Nashornhorn, Wüstentuch um
    den Hals, Lederrüstung, Sandstein-Schulterpanzern mit Messingband und Armschienen aus Messing"""
    M = sand_mats()
    T = texels(body); R = regions(T, arm)
    hide_skin(T, R["skin"], 73)
    sand_cloth(T, R)
    commit(T)
    face_horn(body, arm, M, bone_pt(arm, "mixamorig:Head", 0.3).z, 0.15, 0.045)
    for s_, side in ((1, "Left"), (-1, "Right")):
        a0 = bone_pt(arm, "mixamorig:%sArm" % side)
        p, n = surface(body, (a0.x, a0.y, a0.z + 0.12), (0, 0, -1))
        stone_dome("Panzer" + side, (p if p is not None else a0) + Vector((s_ * 0.02, 0, 0.01)), 0.095, s_, M, arm, "mixamorig:%sArm" % side)
        fm = bone_pt(arm, "mixamorig:%sForeArm" % side, 0.55)
        f0, f1 = bone_pt(arm, "mixamorig:%sForeArm" % side), bone_pt(arm, "mixamorig:%sForeArm" % side, 1.0)
        d = (f1 - f0).normalized()
        t = torus("Schiene" + side, tuple(fm), 0.05, 0.014)
        t.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
        attach(give(t, M["brass"]), arm, "mixamorig:%sForeArm" % side)
    nk = bone_pt(arm, "mixamorig:Neck", 0.2)
    scarf = torus("Tuch", tuple(nk + Vector((0, 0.0, 0.0))), 0.1, 0.035); scarf.scale = (1.05, 1.0, 1.0)
    attach(give(scarf, M["cloth"]), arm, "mixamorig:Neck")
    attach(give(tube("Tuchende", [tuple(nk + Vector((0.04, 0.1, 0.0))), tuple(nk + Vector((0.07, 0.16, -0.08))), tuple(nk + Vector((0.08, 0.2, -0.18)))],
                     [0.03, 0.028, 0.012]), M["cloth"]), arm, "mixamorig:Spine2")

@variante("sand_panzerkaefer", "panzerkaefer")
def nashornkaefer(arm, body):
    """Sternenwüste, stark: Nashornkäfer – schwerer Käfer mit Panzer aus Sandsteinplatten, Messingband mit Nieten um
    den Panzerrand, großem Nashornhorn auf dem Kopf, grauer Faltenhaut und elfenbeinfarbenen Füßen"""
    M = sand_mats()
    T = texels(body)
    px, P, N = T["px"], T["P"], T["N"]
    teal = hue_mask(px, 0.49, 0.08, 0.3)
    red = np.maximum(hue_mask(px, 0.02, 0.06, 0.35), hue_mask(px, 0.97, 0.05, 0.3))
    hh, s, v = hsv(px)
    beige = np.clip((0.6 - s) / 0.1, 0, 1) * np.clip((v - 0.5) / 0.1, 0, 1) * hue_mask(px, 0.11, 0.07, 0.08)
    edge, cid = worley3(P, 9.0, 81)
    paint(T, teal, gradient((0.72, 0.53, 0.31), (0.9, 0.72, 0.46), cid), keep_shading=0.4)
    paint(T, teal * np.clip(1 - edge / 0.004, 0, 1), (0.45, 0.32, 0.18), keep_shading=0.0)
    hide_skin(T, red, 83)
    paint(T, beige, (0.93, 0.86, 0.7), keep_shading=0.5)
    commit(T)
    # Messingband mit Nieten um den Panzerrand
    rim = ring_hits(body, (0, 0.03, 0.17), 40, 0.0, phase=0.0, skip=lambda a: math.sin(a) < -0.75)
    pts = [p + n * 0.008 for p, n, a in rim]
    if len(pts) > 4:
        parts = [give(tube("Messingband", [tuple(q) for q in pts], [0.016] * len(pts), segs=8), M["brass"])]
        for k in range(0, len(rim), 3):
            p, n, a = rim[k]
            parts.append(give(sphere("Niete%d" % k, tuple(p + n * 0.02), 0.014), M["brass"]))
        attach(join_parts(parts, "Panzerrand"), arm, "Body")
    # großes Nashornhorn auf dem Kopf, kleines davor
    h0 = bone_pt(arm, "Head", 0.4)
    p, n = surface(body, (0.0, h0.y, 2.0), (0, 0, -1))
    if p is None or p.z < 0.15:
        p, n = surface(body, (0.0, -1.5, h0.z + 0.06), (0, 1, 0))
    hp = [give(horn("Kaeferhorn", tuple(p - n * 0.02), tuple(p + Vector((0, -0.1, 0.12))), tuple(p + Vector((0, -0.06, 0.3))), 0.055, n=12), M["ivory"])]
    q, m = surface(body, (0.0, -1.5, h0.z - 0.0), (0, 1, 0))
    if q is not None:
        hp.append(give(horn("Nasenhorn", tuple(q - m * 0.02), tuple(q + Vector((0, -0.07, 0.03))), tuple(q + Vector((0, -0.1, 0.1))), 0.03, n=9), M["ivory"]))
    attach(join_parts(hp, "Kaeferhoerner"), arm, "Head")

# ---------------------------------------------------------------- Nebelfelder (Welt 8): Stil des Nebelgeists

def nebel_mats():
    return {
        "ghost": look("Geist", (0.93, 0.92, 1.0), rough=0.45, emit=(0.72, 0.68, 1.0), strength=0.45),
        "shade": look("GeistSchatten", (0.7, 0.66, 0.92), rough=0.5, emit=(0.55, 0.5, 0.9), strength=0.3),
        "dark": look("Maul", (0.08, 0.04, 0.16), rough=0.6, emit=(0.35, 0.1, 0.6), strength=0.6),
        "eye": look("Auge", (0.75, 0.95, 1.0), rough=0.2, emit=(0.55, 0.9, 1.0), strength=4.0),
        "pupil": look("Pupille", (0.1, 0.02, 0.2), rough=0.3),
        "fog": look("Nebel", (0.88, 0.92, 1.0), rough=0.3, emit=(0.7, 0.8, 1.0), strength=0.9),
    }

def fog_curl(name, base, size, mat, turns=2.3):
    pts = []; radii = []
    for k in range(16):
        t = k / 15
        a = t * turns * 2 * math.pi
        pts.append(tuple(Vector(base) + Vector((size * 0.45 * (1 - t) * math.cos(a), size * 0.45 * (1 - t) * math.sin(a), t * size))))
        radii.append(size * 0.25 * (1 - t) + 0.004)
    radii[-1] = 0.0
    return give(tube(name, pts, radii), mat)

def fog_ring(name, c, R, r, n_orbs, orb, M, tilt=-14):
    parts = [give(torus(name, tuple(c), R, r, rot=(tilt, 0, 0)), M["fog"])]
    t_ = math.radians(tilt)
    for i in range(n_orbs):
        a = i * 2 * math.pi / n_orbs + 0.4
        parts.append(give(sphere(name + "Kugel%d" % i, (c[0] + R * math.cos(a), c[1] + R * math.sin(a) * math.cos(t_), c[2] + R * math.sin(a) * math.sin(t_)),
                                 orb * (1.0 + 0.3 * (i % 2))), M["fog"]))
    return parts

def ghost_paint(T, mask, glow_k=0.25):
    """Geisterhaut: oben weiß, unten lavendel, mit hellen Nebelschlieren, leicht leuchtend"""
    P = T["P"]
    z = P[..., 2]
    zmin, zmax = float(z[T["cov"]].min()), float(z[T["cov"]].max())
    col = gradient((0.62, 0.52, 0.92), (0.97, 0.96, 1.0), (z - zmin) / max(0.01, zmax - zmin) * 1.4 - 0.1)
    col = np.clip(col + ((fbm3(P, 5.0, 77, 3) - 0.5) * 0.25)[..., None] * np.asarray((0.6, 0.6, 0.8), np.float32), 0, 1)
    paint(T, mask, col, keep_shading=0.3)
    glow(T, mask * glow_k, (0.72, 0.68, 1.0))

@variante("nebel_schleimling", "schleimling")
def nebelwisch(arm, body):
    """Nebelfelder, leicht: Nebelwisch – kleines Gespenst wie ein Junges des Nebelgeists: gewellter Saum, leuchtende
    Augen, kleines Maul, Stummelärmchen, Nebellocke oben und ein kleiner Nebelring. Eigene Figur auf dem Skelett des
    Schleimlings (hüpft wie er)."""
    M = nebel_mats()
    prof = [(0.74, 0.0), (0.72, 0.08), (0.69, 0.14), (0.64, 0.2), (0.57, 0.25), (0.47, 0.285), (0.36, 0.295), (0.26, 0.3),
            (0.19, 0.31), (0.13, 0.325), (0.08, 0.345)]
    hem = lambda a: (-0.08 * (0.5 + 0.5 * math.cos(6 * a + 0.3)) ** 1.5, 0.02 * math.cos(6 * a + 0.3))
    g = lathe("Wisch", prof, segs=56, hem=hem)
    inner = lathe("WischBoden", [(0.06, 0.34), (0.11, 0.24), (0.15, 0.0)], segs=56)
    H_, W_ = 512, 512
    v = np.linspace(0, 1, H_)[:, None] * np.ones((1, W_))
    wisp = fbm(H_, W_, 6, 79)
    grad = np.clip((v - 0.25) / 0.6, 0, 1)
    col = np.asarray((0.62, 0.52, 0.92)) * (1 - grad[..., None]) + np.asarray((0.97, 0.96, 1.0)) * grad[..., None]
    col = np.clip(col + ((wisp - 0.5) * 0.25)[..., None] * np.asarray((0.6, 0.6, 0.8)), 0, 1)
    arr = np.ones((H_, W_, 4), np.float32); arr[..., :3] = col
    lathe_texture(M["ghost"], arr)
    for o in (g, inner):
        give(o, M["ghost"])
        skin_to(o, arm, lambda c: {"Top": smooth01((c.z - 0.2) / 0.35), "Body": 1 - smooth01((c.z - 0.2) / 0.35)})
    parts = []
    for s in (-1, 1):
        sock = sphere("Augenhoehle%d" % s, (0, 0, 0), 0.065, (1.0, 0.35, 1.25)); sock.location = (s * 0.1, -0.268, 0.5)
        sock.rotation_euler = (0, math.radians(s * 22), 0); parts.append(give(sock, M["dark"]))
        e = sphere("Auge%d" % s, (0, 0, 0), 0.046, (1.0, 0.5, 1.2)); e.location = (s * 0.1, -0.288, 0.5)
        e.rotation_euler = (0, math.radians(s * 22), 0); parts.append(give(e, M["eye"]))
        parts.append(give(sphere("Pupille%d" % s, (s * 0.092, -0.312, 0.485), 0.017), M["pupil"]))
        parts.append(give(tube("Braue%d" % s, [(s * 0.17, -0.25, 0.6), (s * 0.1, -0.28, 0.58), (s * 0.04, -0.29, 0.545)], [0.016, 0.02, 0.014]), M["shade"]))
    mouth = sphere("Maul", (0, 0, 0), 0.065, (1.2, 0.35, 0.8)); mouth.location = (0, -0.29, 0.35)
    parts.append(give(mouth, M["dark"]))
    parts.append(fog_curl("Locke", (0, 0, 0.7), 0.2, M["ghost"]))
    parts += fog_ring("Nebelring", (0.0, 0.03, 0.72), 0.28, 0.012, 4, 0.032, M)
    attach(join_parts(parts, "Wisch_Kopf"), arm, "Top")
    arms_ = []
    for s in (-1, 1):
        arms_.append(give(tube("Arm%d" % s, [(s * 0.25, -0.02, 0.3), (s * 0.34, -0.08, 0.34), (s * 0.39, -0.15, 0.42)], [0.05, 0.045, 0.04]), M["ghost"]))
        arms_.append(give(sphere("Hand%d" % s, (s * 0.4, -0.17, 0.45), 0.05, (1, 1, 1.1)), M["ghost"]))
    attach(join_parts(arms_, "Wisch_Arme"), arm, "Body")
    dampen_scale(arm, ("Body", "Top"), 0.6)
    remove_body(body)

@variante("nebel_tentakler", "tentakler")
def geisterflatterer(arm, body):
    """Nebelfelder, mittel: Geisterflatterer – Flugwesen aus Nebel: weiß bis lavendel, Flügel aus hellem Nebelschleier
    mit Schlieren, cyan leuchtende Augen, Nebellocke auf dem Kopf, Nebelring mit Kugeln um den Körper und ein
    Geisterschweif statt Beinen"""
    M = nebel_mats()
    T = texels(body)
    px, P = T["px"], T["P"]
    red = hue_mask(px, 0.02, 0.06, 0.35)
    teal = hue_mask(px, 0.49, 0.08, 0.3)
    hh, s, v = hsv(px)
    beige = np.clip((0.6 - s) / 0.1, 0, 1) * np.clip((v - 0.5) / 0.1, 0, 1) * hue_mask(px, 0.11, 0.07, 0.08)
    white = np.clip((0.15 - s) / 0.06, 0, 1) * np.clip((v - 0.8) / 0.06, 0, 1)
    ghost_paint(T, red)
    streak = fbm3(P * np.asarray((1.0, 1.0, 3.0), np.float32), 6.0, 85, 3)
    paint(T, teal, gradient((0.6, 0.55, 0.92), (0.92, 0.94, 1.0), streak * 1.3 - 0.15), keep_shading=0.25)
    glow(T, teal * 0.45, (0.65, 0.65, 1.0))
    paint(T, beige, (0.7, 0.66, 0.92), keep_shading=0.5)
    paint(T, white, (0.75, 0.95, 1.0), keep_shading=0.2)
    glow(T, white, (0.45, 0.85, 1.0))
    commit(T, strength=1.0)
    c = bone_pt(arm, "Bone_001", 0.5)
    parts = fog_ring("Nebelring", (c.x, c.y + 0.05, c.z - 0.05), 0.5, 0.014, 6, 0.035, M, tilt=-8)
    p, n = head_top(body, 0.0, 0.05)
    if p is not None:
        parts.append(fog_curl("Locke", p - n * 0.02, 0.24, M["ghost"]))
    q, m = surface(body, (0.0, 0.1, -1.0), (0, 0, 1))
    if q is not None:
        parts.append(give(tendril("Schweif", tuple(q + Vector((0, 0, 0.04))), (0.0, 0.45, -1.0), 0.45, 0.09, 1.2, seed=3), M["ghost"]))
    attach(join_parts(parts, "Geist_Teile"), arm, "Bone_001")

@variante("nebel_brecher", "brecher")
def nebelhuene(arm, body):
    """Nebelfelder, stark: Nebelhüne – großer Spukriese mit bleicher, schwach leuchtender Geisterhaut, dunkelviolettem
    Gewand mit gewelltem Saum, cyan leuchtenden Augen, Nebellocke, Nebelring mit Kugeln über dem Kopf und
    Nebelkugeln auf den Schultern"""
    M = nebel_mats()
    robe = look("Gewand", (0.3, 0.22, 0.48), rough=0.7, emit=(0.25, 0.15, 0.45), strength=0.25)
    T = texels(body); R = regions(T, arm)
    ghost_paint(T, R["skin"], 0.3)
    paint(T, R["purple"] * (1 - R["head"]), (0.3, 0.22, 0.48), keep_shading=0.6)
    paint(T, R["purple"] * R["head"], (0.72, 0.68, 0.95), keep_shading=0.5)
    paint(T, R["grey"], (0.72, 0.68, 0.92), keep_shading=0.5)
    collar = np.maximum(R["white"] * (1 - R["head"]), R["collar"])
    paint(T, collar, (0.9, 0.93, 1.0), keep_shading=0.3)
    glow(T, collar * 0.8, (0.7, 0.8, 1.0))
    eyes = R["white"] * R["head"]
    paint(T, eyes, (0.75, 0.95, 1.0), keep_shading=0.2)
    glow(T, eyes, (0.45, 0.85, 1.0))
    commit(T, strength=1.4)
    # Gewand mit gewelltem Saum um die Hüften
    hp = bone_pt(arm, "mixamorig:Hips")
    hem = lambda a: (-0.07 * (0.5 + 0.5 * math.cos(9 * a)) ** 1.5, 0.015 * math.cos(9 * a))
    sk = lathe("Gewandsaum", [(0.12, 0.27), (0.02, 0.29), (-0.1, 0.31), (-0.2, 0.33)], segs=54, hem=hem)
    for v in sk.data.vertices:
        v.co.y *= 0.85
    sk.location = (hp.x, hp.y + 0.01, hp.z)
    attach(give(sk, robe), arm, "mixamorig:Hips")
    p, n = head_top(body, 0.0, 0.0)
    parts = []
    if p is not None:
        parts.append(fog_curl("Locke", p - n * 0.02, 0.22, M["ghost"]))
        parts += fog_ring("Nebelring", (p.x, p.y + 0.03, p.z + 0.06), 0.3, 0.013, 6, 0.032, M)
    attach(join_parts(parts, "Nebelkopf"), arm, "mixamorig:Head")
    for s_, side in ((1, "Left"), (-1, "Right")):
        a0 = bone_pt(arm, "mixamorig:%sArm" % side)
        p, n = surface(body, (a0.x, a0.y, a0.z + 0.15), (0, 0, -1))
        c = (p if p is not None else a0)
        orbs = [give(sphere("Schulterkugel%s%d" % (side, k), tuple(c + Vector((s_ * dx, dy, 0.04 + dz))), r), M["fog"])
                for k, (dx, dy, dz, r) in enumerate(((0.0, 0.0, 0.03, 0.05), (0.07, 0.06, 0.0, 0.035), (0.05, -0.07, 0.0, 0.03)))]
        attach(join_parts(orbs, "Schulterkugeln" + side), arm, "mixamorig:%sArm" % side)

# ---------------------------------------------------------------- Schattenreich (Welt 9): Stil des Schattenwesens

def shadow_mats():
    return {
        "black": look("Schatten", (0.07, 0.06, 0.1), rough=0.18, metal=0.1),
        "black2": look("Schatten2", (0.12, 0.09, 0.18), rough=0.2, metal=0.1),
        "glow": look("Schattenglut", (0.8, 0.4, 1.0), rough=0.3, emit=(0.72, 0.3, 1.0), strength=3.5),
        "eye": look("Schattenauge", (0.95, 0.85, 1.0), rough=0.2, emit=(0.85, 0.65, 1.0), strength=5.0),
        "thorn": look("Dorn", (0.55, 0.25, 0.85), rough=0.15, emit=(0.5, 0.2, 0.85), strength=1.4),
    }

def shadow_skin(T, mask, seed, freq=12.0):
    """glänzend schwarzer Schatten mit violett glimmenden Adern (stellenweise)"""
    P = T["P"]
    sheen = fbm3(P, 6.0, seed, 3)[..., None]
    paint(T, mask, np.asarray((0.05, 0.04, 0.08), np.float32) + sheen * np.asarray((0.07, 0.03, 0.12), np.float32), keep_shading=0.25)
    edge, cid = worley3(P, freq, seed + 1)
    k = np.clip(1 - edge / 0.004, 0, 1) ** 1.5 * (fbm3(P, 5.0, seed + 2, 3) > 0.45)
    paint(T, mask * k, (0.75, 0.45, 1.0), keep_shading=0.0)
    glow(T, mask * k, (0.7, 0.3, 1.0))

def shadow_body(T, R, freq=12.0, seed=101, collar_glow=False):
    shadow_skin(T, R["skin"], seed, freq)
    paint(T, R["purple"] * (1 - R["head"]), (0.12, 0.09, 0.18), keep_shading=0.6)
    spots = R["purple"] * R["head"]
    paint(T, spots, (0.08, 0.06, 0.12), keep_shading=0.4)
    paint(T, R["grey"], (0.2, 0.14, 0.3), keep_shading=0.5)
    if collar_glow:
        collar = np.maximum(R["white"] * (1 - R["head"]), R["collar"])
        paint(T, collar, (0.8, 0.45, 1.0), keep_shading=0.3)
        glow(T, collar, (0.7, 0.3, 1.0))
    eyes = R["white"] * R["head"]
    paint(T, eyes, (0.95, 0.85, 1.0), keep_shading=0.2)
    glow(T, eyes, (0.85, 0.6, 1.0))

def third_eye(body, arm, M, z, r):
    p, n = front_pt(body, 0.0, z)
    if p is None:
        return
    e = sphere("Stirnauge", (0, 0, 0), r, (1.0, 0.45, 1.3)); e.location = p + n * (r * 0.15)
    attach(give(e, M["eye"]), arm, "mixamorig:Head")

def head_tendrils(body, arm, M, n_, L, r0, spread=0.12):
    parts = []
    for i in range(n_):
        x = (i - (n_ - 1) / 2) * spread
        p, n = head_top(body, x, 0.04)
        if p is None:
            continue
        parts.append(give(tendril("Kopfranke%d" % i, tuple(p - n * 0.02), (x * 4.0, 1.0, 0.9), L * (1.0 if i == n_ // 2 else 0.85), r0, 1.1, seed=i), M["black2"]))
    if parts:
        attach(join_parts(parts, "Kopfranken"), arm, "mixamorig:Head")

def shoulder_thorns(body, arm, M, scale, n_=3):
    for s_, side in ((1, "Left"), (-1, "Right")):
        a0 = bone_pt(arm, "mixamorig:%sArm" % side)
        p, n = surface(body, (a0.x, a0.y, a0.z + 0.15), (0, 0, -1))
        c = p if p is not None else a0
        sh = []
        for k, (dx, dy, h_, r, tx, ty) in enumerate(((0.0, 0.0, 0.28, 0.065, 0, 30), (0.1, 0.08, 0.2, 0.05, -15, 55), (-0.03, -0.08, 0.18, 0.045, 25, 18))[:n_]):
            sh.append(give(crystal("Schulterdorn%s%d" % (side, k), tuple(c + Vector((s_ * dx * scale, dy * scale, -0.02))), h_ * scale, r * scale, (tx, s_ * ty, 0)), M["thorn"]))
        attach(join_parts(sh, "Schulterdornen" + side), arm, "mixamorig:%sArm" % side)

def back_tendrils(body, arm, M, rows, r0):
    back = []
    for i, (x, z, dx, dz, L) in enumerate(rows):
        p, n = back_pt(body, x, z)
        if p is not None:
            back.append(give(tendril("Rueckenranke%d" % i, tuple(p - n * 0.02), (dx, 1.0, dz), L, r0, 0.9, seed=10 + i), M["black2"]))
    if back:
        attach(join_parts(back, "Rueckenranken"), arm, "mixamorig:Spine2")

@variante("schatten_krabbler", "krabbler")
def schattenwicht(arm, body):
    """Schattenreich, leicht: Schattenwicht – kleiner Kobold aus glänzend schwarzem Schatten mit violett glimmenden
    Adern, drittem leuchtenden Auge auf der Stirn, Schattenranken auf dem Kopf und kleinen Dornen auf den Schultern"""
    M = shadow_mats()
    T = texels(body); R = regions(T, arm)
    shadow_body(T, R, 13.0, 103)
    commit(T, strength=2.0)
    third_eye(body, arm, M, bone_pt(arm, "mixamorig:Head", 1.0).z + 0.18, 0.04)
    head_tendrils(body, arm, M, 3, 0.3, 0.04, spread=0.13)
    shoulder_thorns(body, arm, M, 0.45, n_=2)

@variante("schatten_zombie", "zombie")
def schattenschleicher(arm, body):
    """Schattenreich, mittel: Schattenschleicher – hagere Gestalt aus glänzend schwarzem Schatten mit violetten Adern,
    drittem Auge, Ranken aus Kopf und Rücken und violetten Kristalldornen auf den Schultern"""
    M = shadow_mats()
    T = texels(body); R = regions(T, arm)
    shadow_body(T, R, 11.0, 107)
    commit(T, strength=2.0)
    third_eye(body, arm, M, bone_pt(arm, "mixamorig:Head", 1.0).z + 0.13, 0.032)
    head_tendrils(body, arm, M, 2, 0.26, 0.035, spread=0.12)
    shoulder_thorns(body, arm, M, 0.6)
    back_tendrils(body, arm, M, ((-0.08, 1.05, -0.9, 0.5, 0.42), (0.08, 1.05, 0.9, 0.5, 0.42), (0.0, 0.9, 0.0, -0.2, 0.36)), 0.04)

@variante("schatten_brecher", "brecher")
def dornenbrecher(arm, body):
    """Schattenreich, stark: Dornenbrecher – massiger Schläger aus glänzend schwarzem Schatten mit violetten Adern,
    violett glühendem Kragen, großen Kristalldornen auf Schultern und Rücken, Schattenranken aus dem Rücken und an den
    Unterarmen und einem dritten Auge"""
    M = shadow_mats()
    T = texels(body); R = regions(T, arm)
    shadow_body(T, R, 9.0, 109, collar_glow=True)
    commit(T, strength=2.2)
    third_eye(body, arm, M, bone_pt(arm, "mixamorig:Head", 0.75).z + 0.05, 0.035)
    shoulder_thorns(body, arm, M, 0.85)
    back = []
    for k, (x, z, h_, r, tx, ty) in enumerate(((0.0, 1.22, 0.3, 0.07, -35, 0), (-0.15, 1.1, 0.22, 0.055, -40, -20), (0.15, 1.1, 0.22, 0.055, -40, 20), (0.0, 0.98, 0.2, 0.05, -50, 0))):
        p, n = back_pt(body, x, z)
        if p is not None:
            back.append(give(crystal("Rueckendorn%d" % k, tuple(p - n * 0.03), h_, r, (tx, ty, 0)), M["thorn"]))
    attach(join_parts(back, "Rueckendornen"), arm, "mixamorig:Spine2")
    back_tendrils(body, arm, M, ((-0.2, 1.15, -0.9, 0.5, 0.55), (0.2, 1.15, 0.9, 0.5, 0.55), (-0.15, 0.95, -0.8, -0.1, 0.45), (0.15, 0.95, 0.8, -0.1, 0.45)), 0.055)
    for s_, side in ((1, "Left"), (-1, "Right")):
        f0 = bone_pt(arm, "mixamorig:%sForeArm" % side, 0.35)
        o = tendril("Armranke" + side, tuple(f0 + Vector((s_ * 0.06, 0.04, 0.0))), (s_ * 1.0, 0.6, 0.3), 0.3, 0.035, 1.0, seed=30 + s_)
        attach(give(o, M["black2"]), arm, "mixamorig:%sForeArm" % side)

# ---------------------------------------------------------------- Herz des Wurmlochs (Welt 10): Stil des Kristallriesen,
# aber aus Sternenstaub statt Höhlenkristall (damit es klar anders aussieht als die Kristallhöhlen)

def wurm_mats():
    return {
        "cr": look("Riesenkristall", (0.5, 0.26, 0.9), rough=0.1, emit=(0.42, 0.18, 0.85), strength=0.6),
        "cr2": look("Riesenkristall2", (0.85, 0.3, 0.75), rough=0.1, emit=(0.75, 0.2, 0.65), strength=0.5),
        "energy": look("Wurmlochenergie", (0.5, 0.95, 1.0), rough=0.2, emit=(0.3, 0.85, 1.0), strength=3.0),
        "void": look("Leere", (0.06, 0.05, 0.16), rough=0.3, emit=(0.2, 0.1, 0.45), strength=0.3),
    }

def star_skin(T, mask, seed, star_freq=90.0):
    """Sternenhaut: tiefes Indigo mit Nebelschleiern (Magenta, Cyan) und funkelnden Sternen, leicht leuchtend"""
    P = T["P"]
    neb = fbm3(P, 4.0, seed, 4)
    neb2 = fbm3(P, 3.0, seed + 7, 3)
    col = np.asarray((0.06, 0.05, 0.17), np.float32)[None, None, :] + np.clip(neb - 0.45, 0, 1)[..., None] * np.asarray((0.75, 0.2, 0.8), np.float32) \
        + np.clip(neb2 - 0.55, 0, 1)[..., None] * np.asarray((0.1, 0.7, 0.9), np.float32)
    star = np.clip((noise3(P, star_freq, seed + 3) - 0.86) / 0.05, 0, 1) * np.clip((noise3(P, star_freq * 0.37, seed + 5) - 0.4) / 0.2, 0, 1)
    paint(T, mask, col, keep_shading=0.25)
    paint(T, mask * star, (1.0, 0.97, 1.0), keep_shading=0.0)
    glow(T, mask * np.maximum(star, np.clip(neb - 0.5, 0, 1) * 0.6), (0.8, 0.6, 1.0))

def energy_ring(name, c, R, r, tilt, M, n_shards=0, rnd=None):
    parts = [give(torus(name, tuple(c), R, r, rot=tilt, segs=48), M["energy"])]
    for i in range(n_shards):
        a = i * 2 * math.pi / n_shards + 0.5
        tm = Matrix.Rotation(math.radians(tilt[0]), 3, 'X') @ Matrix.Rotation(math.radians(tilt[1]), 3, 'Y')
        pos = Vector(c) + tm @ Vector((R * math.cos(a), R * math.sin(a), 0))
        parts.append(shard(name + "Splitter%d" % i, pos - Vector((0, 0, 0.03)), Vector((rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), 1)), 0.08, 0.025, M["cr"] if i % 2 else M["cr2"]))
    return parts

@variante("wurm_tentakler", "tentakler")
def sternenflatterer(arm, body):
    """Herz des Wurmlochs, mittel: Sternenflatterer – Flugwesen aus Sternenstaub: Körper wie der Nachthimmel mit
    funkelnden Sternen, Flügel aus leuchtendem Nebel (Magenta bis Cyan), violette Kristallhörner, cyan leuchtende
    Augen und ein Energiering aus dem Wurmloch, der um den Körper kreist"""
    M = wurm_mats()
    T = texels(body)
    px, P = T["px"], T["P"]
    red = hue_mask(px, 0.02, 0.06, 0.35)
    teal = hue_mask(px, 0.49, 0.08, 0.3)
    hh, s, v = hsv(px)
    beige = np.clip((0.6 - s) / 0.1, 0, 1) * np.clip((v - 0.5) / 0.1, 0, 1) * hue_mask(px, 0.11, 0.07, 0.08)
    white = np.clip((0.15 - s) / 0.06, 0, 1) * np.clip((v - 0.8) / 0.06, 0, 1)
    star_skin(T, red, 121)
    wing = fbm3(P, 3.5, 123, 3)
    paint(T, teal, gradient((0.85, 0.25, 0.8), (0.2, 0.8, 1.0), wing * 1.6 - 0.3), keep_shading=0.25)
    star = np.clip((noise3(P, 80.0, 125) - 0.85) / 0.05, 0, 1)
    paint(T, teal * star, (1.0, 1.0, 1.0), keep_shading=0.0)
    glow(T, teal * (0.5 + star), (0.7, 0.5, 1.0))
    paint(T, beige, (0.6, 0.35, 1.0), keep_shading=0.4)
    glow(T, beige * 0.7, (0.5, 0.25, 1.0))
    paint(T, white, (0.7, 0.98, 1.0), keep_shading=0.2)
    glow(T, white, (0.3, 0.85, 1.0))
    commit(T, strength=1.5)
    rnd = random.Random(127)
    c = bone_pt(arm, "Bone_001", 0.5)
    attach(join_parts(energy_ring("Energiering", (c.x, c.y + 0.08, c.z - 0.02), 0.52, 0.014, (-12, 18, 0), M, 5, rnd), "Energiering"), arm, "Bone_001")
    for chain in (("Bone_009", "Bone_008", "Bone_006"), ("Bone_013", "Bone_012", "Bone_010")):
        tip = bone_pt(arm, chain[2], 1.0)
        attach(shard("HornKristall" + chain[0], tip - Vector((0, 0, 0.04)), Vector((0, 0.1, 1.0)), 0.12, 0.03, M["cr"]), arm, chain[2])

@variante("wurm_zombie", "zombie")
def leerenwandler(arm, body):
    """Herz des Wurmlochs, mittel-stark: Leerenwandler – hagere Gestalt aus Sternenhimmel mit funkelnden Sternen,
    Rüstung aus violetten Kristallplatten mit leuchtenden Kanten, cyan leuchtendem Kern in der Brust, einem
    Energiering über dem Kopf mit kreisenden Kristallsplittern und Kristallen auf den Schultern"""
    M = wurm_mats()
    T = texels(body); R = regions(T, arm)
    star_skin(T, R["skin"], 131)
    plate = R["purple"] * (1 - R["head"])
    edge, cid = worley3(T["P"], 10.0, 133)
    paint(T, plate, gradient((0.32, 0.16, 0.6), (0.7, 0.28, 0.75), cid), keep_shading=0.4)
    line = np.clip(1 - edge / 0.004, 0, 1)
    paint(T, plate * line, (0.6, 0.95, 1.0), keep_shading=0.0)
    glow(T, plate * line, (0.3, 0.85, 1.0))
    paint(T, R["purple"] * R["head"], (0.55, 0.3, 0.95), keep_shading=0.4)
    glow(T, R["purple"] * R["head"] * 0.6, (0.5, 0.25, 1.0))
    paint(T, R["grey"], (0.45, 0.9, 1.0), keep_shading=0.4)
    glow(T, R["grey"] * 0.5, (0.3, 0.85, 1.0))
    eyes = R["white"] * R["head"]
    paint(T, eyes, (0.7, 0.98, 1.0), keep_shading=0.2)
    glow(T, eyes, (0.3, 0.85, 1.0))
    commit(T, strength=1.6)
    rnd = random.Random(137)
    p, n = head_top(body, 0.0, 0.0)
    if p is not None:
        attach(join_parts(energy_ring("Heiligenschein", (p.x, p.y + 0.02, p.z + 0.08), 0.17, 0.012, (-15, 0, 0), M, 3, rnd), "Kopfring"), arm, "mixamorig:Head")
    sp = bone_pt(arm, "mixamorig:Spine1", 0.7)
    q, m = front_pt(body, 0.0, sp.z)
    if q is not None:
        core = [give(sphere("Kern", tuple(q + m * 0.005), 0.04, (1.0, 0.6, 1.0)), M["energy"])]
        for k in range(4):
            a = k * math.pi / 2 + 0.4
            core.append(shard("Kernsplitter%d" % k, q + Vector((math.cos(a) * 0.045, -0.01, math.sin(a) * 0.045)), Vector((math.cos(a), -0.6, math.sin(a))), 0.06, 0.018, M["cr"]))
        attach(join_parts(core, "Brustkern"), arm, "mixamorig:Spine1")
    for s_, side in ((1, "Left"), (-1, "Right")):
        a0 = bone_pt(arm, "mixamorig:%sArm" % side)
        p, n = surface(body, (a0.x, a0.y, a0.z + 0.12), (0, 0, -1))
        if p is not None:
            attach(join_parts(cluster("Schulterkristall" + side, p, (n + Vector((s_ * 0.6, 0.2, 0))).normalized(), 0.14, 0.035, (M["cr"], M["cr2"]), rnd, count=3),
                              "Schulterkristall" + side), arm, "mixamorig:%sArm" % side)

@variante("wurm_panzerkaefer", "panzerkaefer")
def sternenpanzer(arm, body):
    """Herz des Wurmlochs, stark: Sternenpanzer – schwerer Käfer mit Panzer aus violetten Kristallfacetten, auf dem
    ein leuchtender Wurmloch-Strudel kreist, Kristallspitzen rund um den Panzer, Körper aus Sternenhimmel, einem
    Kristallhorn und einem Energiering um den Panzer"""
    M = wurm_mats()
    T = texels(body)
    px, P, N = T["px"], T["P"], T["N"]
    teal = hue_mask(px, 0.49, 0.08, 0.3)
    red = np.maximum(hue_mask(px, 0.02, 0.06, 0.35), hue_mask(px, 0.97, 0.05, 0.3))
    hh, s, v = hsv(px)
    beige = np.clip((0.6 - s) / 0.1, 0, 1) * np.clip((v - 0.5) / 0.1, 0, 1) * hue_mask(px, 0.11, 0.07, 0.08)
    edge, cid = worley3(P, 9.0, 141)
    paint(T, teal, gradient((0.3, 0.15, 0.62), (0.75, 0.3, 0.8), cid), keep_shading=0.35)
    # Strudel oben auf dem Panzer: Spiralarme um die höchste Stelle
    top = P[..., :2] - np.asarray((0.0, 0.03), np.float32)
    r = np.linalg.norm(top, axis=-1); th = np.arctan2(top[..., 1], top[..., 0])
    spiral = 0.5 + 0.5 * np.cos(3 * th + r * 38.0)
    swirl = np.clip((spiral - 0.55) / 0.3, 0, 1) * np.clip((0.3 - r) / 0.12, 0, 1) * np.clip((N[..., 2] - 0.3) / 0.3, 0, 1)
    eye_ = np.clip((0.05 - r) / 0.03, 0, 1) * np.clip((N[..., 2] - 0.5) / 0.3, 0, 1)
    paint(T, teal * swirl, gradient((0.3, 0.9, 1.0), (1.0, 0.5, 0.95), r / 0.3), keep_shading=0.0)
    paint(T, teal * eye_, (0.02, 0.0, 0.05), keep_shading=0.0)
    glow(T, teal * swirl, (0.4, 0.8, 1.0))
    line = np.clip(1 - edge / 0.004, 0, 1) * (1 - swirl)
    paint(T, teal * line, (0.85, 0.6, 1.0), keep_shading=0.0)
    glow(T, teal * line * 0.6, (0.7, 0.35, 1.0))
    star_skin(T, red, 143)
    paint(T, beige, (0.85, 0.4, 0.85), keep_shading=0.5)
    glow(T, beige * 0.4, (0.75, 0.2, 0.65))
    commit(T, strength=1.6)
    rnd = random.Random(147)
    rim = ring_hits(body, (0, 0.03, 0.22), 12, 0.25, phase=0.2, skip=lambda a: math.sin(a) < -0.6)
    sp = []
    for k, (p, n, a) in enumerate(rim):
        sp.append(shard("Randkristall%d" % k, p - n * 0.02, (n + Vector((0, 0, 0.5))).normalized(), 0.1 + 0.04 * (k % 2), 0.028, M["cr"] if k % 2 else M["cr2"]))
    attach(join_parts(sp, "Randkristalle"), arm, "Body")
    attach(join_parts(energy_ring("Energiering", (0.0, 0.03, 0.2), 0.42, 0.012, (8, 0, 0), M, 0, rnd), "Energiering"), arm, "Body")
    h0 = bone_pt(arm, "Head", 0.4)
    q, m = surface(body, (0.0, -1.5, h0.z + 0.04), (0, 1, 0))
    if q is not None:
        attach(join_parts(cluster("Stirnkristall", q, (m + Vector((0, -0.2, 1.2))).normalized(), 0.16, 0.035, (M["cr"], M["cr2"]), rnd, count=2), "Stirnkristall"), arm, "Head")

# ---------------------------------------------------------------- Ablauf

if __name__ == "__main__":
    run(VAR, OUT)
