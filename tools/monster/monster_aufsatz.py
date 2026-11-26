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

def ridges(P, freq, seed, width, stretch=(1.0, 1.0, 1.0)):
    """feine, fließende Linien im Raum (Höhenlinien eines Rauschens): Adern, Hautfalten"""
    n = fbm3(P * np.asarray(stretch, np.float32), freq, seed, 3)
    return np.clip(1 - np.abs(n - 0.5) / width, 0, 1)

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
def giftkaulquappe(arm, body):
    """Giftsumpf, leicht: Giftkaulquappe – kleine, flinke Kaulquappe (Kommentar 25.11.: nicht wie ein Junges der
    Giftkröte, keine Füße): ovaler Kopfkörper, oben dunkeloliv mit violetten Flecken, heller Bauch, seitliche gelbe
    Augen mit Schlitzpupillen, kleines Maul mit Gifttropfen, ein paar leuchtende Warzen und ein breiter Flossenschwanz.
    Eigene Figur auf dem Skelett des Schleimlings (hüpft wie er)."""
    M = gift_mats()
    skin = look("KaulquappenHaut", (1.0, 1.0, 1.0), rough=0.25)
    green = look("Quappengruen", (0.3, 0.72, 0.22), rough=0.3)
    pale = look("Quappenbauch", (0.88, 0.95, 0.6), rough=0.3)
    prof = [(0.46, 0.0), (0.455, 0.08), (0.43, 0.16), (0.385, 0.23), (0.32, 0.28), (0.24, 0.3), (0.16, 0.295), (0.09, 0.27), (0.04, 0.21), (0.01, 0.12), (0.0, 0.0)]
    g = lathe("Kaulquappe", prof, segs=56)
    for v in g.data.vertices:
        v.co.y *= 1.22
        v.co.x *= 0.92
    H_, W_ = 1024, 1024
    uu, vv = lathe_uv_grid(H_, W_)
    grad = np.clip((vv - 0.38) / 0.14, 0, 1)
    col = np.asarray((0.88, 0.95, 0.6)) * (1 - grad[..., None]) + np.asarray((0.3, 0.72, 0.22)) * grad[..., None]
    # klare runde violette Punkte (versetztes Raster), oben dichter, mit sanftem Rand
    rows, cols = 7, 16
    ry = vv * rows; ri = np.floor(ry); fx = (uu * cols + 0.5 * (ri % 2)) % 1.0 - 0.5; fy = (ry - ri) - 0.5
    d = np.hypot(fx * 1.0, fy * 1.6)
    rad = 0.22 + 0.08 * np.sin(ri * 2.1 + np.floor(uu * cols + 0.5 * (ri % 2)) * 1.7)
    dot = np.clip((rad - d) / 0.04, 0, 1) * np.clip((vv - 0.5) / 0.08, 0, 1)
    col = col * (1 - dot[..., None]) + np.asarray((0.62, 0.22, 0.78)) * dot[..., None]
    col = col * (1.0 - 0.12 * (1 - vv))[..., None]
    arr = np.ones((H_, W_, 4), np.float32); arr[..., :3] = col
    lathe_texture(skin, arr)
    give(g, skin)
    bpy.context.view_layer.update()
    face = []
    for s_ in (-1, 1):
        p, n = surface(g, (s_ * 2.0, -0.24, 0.25), (-s_, 0, 0))
        c = p - n * 0.02
        face.append(give(sphere("Augapfel%d" % s_, tuple(c), 0.06), M["eye"]))
        sl = sphere("Schlitz%d" % s_, (0, 0, 0), 0.022, (0.45, 1.0, 1.4)); sl.location = c + n * 0.055
        sl.rotation_euler = n.to_track_quat('Y', 'Z').to_euler()
        face.append(give(sl, M["black"]))
        lid = sphere("Lid%d" % s_, (0, 0, 0), 0.066, (1.0, 1.0, 0.55), segs=(24, 12)); lid.location = c + Vector((0, 0, 0.026))
        lid.rotation_euler = (0, math.radians(-s_ * 12), 0)
        face.append(give(lid, green))
    hits = on_surface(g, (0, 0, 0.17), [(math.sin(a), -math.cos(a), -0.15 + 0.12 * (abs(a) / 0.8) ** 2) for a in [math.radians(t) for t in range(-40, 44, 8)]], lift=0.003)
    face.append(give(tube("Maul", [tuple(p) for p, n in hits], [0.008] + [0.013] * (len(hits) - 2) + [0.008], segs=8), M["mouth"]))
    p, n = hits[-1]
    face.append(give(sphere("Gifttropfen", tuple(p + Vector((0, -0.01, -0.05))), 0.016, (1, 1, 1.3)), M["toxic"]))
    rnd = random.Random(31)
    for i in range(7):
        a = rnd.uniform(-1.9, 1.9) + math.pi / 2
        el = rnd.uniform(0.6, 1.3)
        d = Vector((math.cos(a) * math.cos(el), math.sin(a) * math.cos(el), math.sin(el)))
        q, m = surface(g, Vector((0, 0, 0.2)) + d * 2.0, -d)
        if q is not None and q.z > 0.22:
            face.append(give(sphere("Warze%d" % i, tuple(q), rnd.uniform(0.012, 0.02), (1, 1, 0.7)), M["wart"]))
    attach(join_parts(face, "Kaulquappe_Kopf"), arm, "Top")
    q, m = surface(g, (0, 2.0, 0.17), (0, -1, 0))
    tail = [fin("Schwanz", q - m * 0.05, (0, 1.0, 0.25), 0.48, 0.13, green, curl=0.25),
            fin("Schwanzsaum", q - m * 0.04 + Vector((0, 0.02, 0.0)), (0, 1.0, 0.18), 0.5, 0.09, pale, curl=0.3)]
    attach(join_parts(tail, "Kaulquappe_Schwanz"), arm, "Body")
    skin_to(g, arm, lambda c: {"Top": smooth01((c.z - 0.02) / 0.13), "Body": 1 - smooth01((c.z - 0.02) / 0.13)})   # Maul bewegt sich mit dem Kopf
    dampen_scale(arm, ("Body", "Top"), 0.55)
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
    paint(T, mask, np.asarray((0.62, 0.6, 0.58), np.float32) * (0.92 + 0.16 * fbm3(P, 8.0, seed, 3)[..., None]), keep_shading=0.5)
    folds = ridges(P, freq * 0.35, seed + 1, 0.035, (1.0, 1.0, 2.8)) * np.clip((fbm3(P, 4.0, seed + 2, 2) - 0.35) / 0.15, 0, 1)
    paint(T, mask * folds * 0.75, (0.34, 0.32, 0.31), keep_shading=0.0)

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

def rhino_ears(body, arm, M, size):
    """Nashornohren seitlich oben am Kopf (flach, spitz, nach außen oben)"""
    parts = []
    for s_ in (-1, 1):
        p, n = surface(body, (s_ * 2.0, 0.03, bone_pt(arm, "mixamorig:Head", 1.0).z + size * 0.6), (-s_, 0, 0))
        if p is None:
            continue
        b0 = p - n * 0.02
        ear = horn("Ohr%d" % s_, tuple(b0), tuple(b0 + Vector((s_ * size * 0.5, 0.02, size * 0.45))), tuple(b0 + Vector((s_ * size * 0.75, 0.05, size * 0.95))), size * 0.33, n=8)
        for v in ear.data.vertices:                       # flach drücken (Ohrmuschel)
            v.co.y = b0.y + (v.co.y - b0.y) * 0.45
        parts.append(give(ear, M["hide_dark"]))
    attach(join_parts(parts, "Ohren"), arm, "mixamorig:Head")

@variante("sand_krabbler", "krabbler")
def hornling(arm, body):
    """Sternenwüste, leicht: Hornling – flinker Wüstenkobold mit grauer Faltenhaut, Nashornhorn vorn am Kopf,
    Sandsteinflecken, Lederrüstung mit Messing und kleinem Sandsteinpanzer auf der Schulter"""
    M = sand_mats()
    T = texels(body); R = regions(T, arm)
    hide_skin(T, R["skin"], 71)
    sand_cloth(T, R)
    commit(T)
    face_horn(body, arm, M, bone_pt(arm, "mixamorig:Head", 0.35).z, 0.24, 0.07)
    rhino_ears(body, arm, M, 0.14)
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
    face_horn(body, arm, M, bone_pt(arm, "mixamorig:Head", 0.3).z, 0.2, 0.058)
    rhino_ears(body, arm, M, 0.11)
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
    white = np.clip((0.2 - s) / 0.06, 0, 1) * np.clip((v - 0.75) / 0.08, 0, 1)
    paint(T, white, (0.99, 0.98, 0.95), keep_shading=0.35)          # Zähne sauber weiß (Kommentar 25.11.)
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
    attach(join_parts(hp, "Kaeferhoerner"), arm, "Head")          # unteres Horn entfernt (Kommentar 25.11.: mit den Zähnen verhakt)
    # neues Maul: Schnauzenplatte aus Nashornhaut über dem alten Gebiss, darauf ein grimmiger Mundstrich mit zwei kleinen
    # Hauern und seitlich zwei geschwungene Elfenbein-Zangen wie beim Nashornkäfer
    dark = look("Maulstrich", (0.12, 0.09, 0.08), rough=0.5)
    mz = Vector((0.0, -0.285, 0.085))
    muz = sphere("Schnauze", (0, 0, 0), 0.1, (1.3, 0.72, 0.62), segs=(32, 16)); muz.location = mz
    mp = [give(muz, M["hide"])]
    bpy.context.view_layer.update()
    line = []
    for k in range(9):
        u = -1 + 2 * k / 8
        q, m = surface(muz, (u * 0.085, -1.0, mz.z - 0.012 - 0.012 * (1 - u * u)), (0, 1, 0))
        if q is not None:
            line.append(q + m * 0.004)
    if len(line) > 3:
        mp.append(give(tube("Mundstrich", [tuple(q) for q in line], [0.006] + [0.009] * (len(line) - 2) + [0.006], segs=8), dark))
        for s_, q in ((-1, line[1]), (1, line[-2])):
            mp.append(give(tube("Hauer%d" % s_, [tuple(q + Vector((0, 0.004, -0.004))), tuple(q + Vector((s_ * 0.004, -0.008, 0.016))), tuple(q + Vector((s_ * 0.008, -0.01, 0.03)))],
                                [0.008, 0.005, 0.0], segs=8), M["ivory"]))
    for s_ in (-1, 1):
        b0 = mz + Vector((s_ * 0.1, -0.02, -0.02))
        mp.append(give(horn("Zange%d" % s_, tuple(b0), tuple(b0 + Vector((s_ * 0.05, -0.06, -0.01))), tuple(b0 + Vector((-s_ * 0.02, -0.11, 0.0))), 0.022, n=10), M["ivory"]))
    attach(join_parts(mp, "Neues_Maul"), arm, "Head")
    # Hörner auf dem Rückenpanzer (Kommentar 25.11.): Reihe in der Mitte, nach hinten geschwungen, kleinere seitlich
    back = []
    for k, (x, y, L, r0) in enumerate(((0.0, -0.06, 0.2, 0.045), (0.0, 0.07, 0.17, 0.04), (0.0, 0.19, 0.13, 0.035),
                                       (-0.13, 0.0, 0.11, 0.03), (0.13, 0.0, 0.11, 0.03), (-0.12, 0.14, 0.09, 0.026), (0.12, 0.14, 0.09, 0.026))):
        q, m = surface(body, (x, y, 2.0), (0, 0, -1))
        if q is None:
            continue
        b0 = q - m * 0.02
        out = Vector((x * 2.0, 0.0, 0.0))
        back.append(give(horn("Rueckenhorn%d" % k, tuple(b0), tuple(b0 + m * L * 0.55 + out * 0.15 + Vector((0, 0.03, 0))), tuple(b0 + m * L + out * 0.3 + Vector((0, L * 0.45, 0))), r0, n=10), M["ivory"]))
    attach(join_parts(back, "Rueckenhoerner"), arm, "Body")

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
def nebelirrlicht(arm, body):
    """Nebelfelder, leicht: Nebelirrlicht – kleine, schwebende Nebelflamme (Kommentar 25.11.: nicht wie ein Junges des
    Nebelgeists): runder Bauch, nach oben spitz zulaufend und nach hinten geweht, leuchtend lavendel bis weiß, zwei
    schräge cyan leuchtende Augen, ein freches Grinsen und drei kleine Nebelkugeln, die um den Fuß kreisen. Eigene Figur
    auf dem Skelett des Schleimlings."""
    M = nebel_mats()
    wisp = look("Irrlicht", (0.95, 0.94, 1.0), rough=0.4, emit=(0.6, 0.52, 0.95), strength=0.35)
    prof = [(0.78, 0.0), (0.7, 0.035), (0.6, 0.08), (0.5, 0.14), (0.4, 0.2), (0.31, 0.24), (0.22, 0.255), (0.14, 0.24), (0.07, 0.2), (0.025, 0.12), (0.0, 0.0)]
    g = lathe("Irrlicht", prof, segs=48)
    for v in g.data.vertices:
        if v.co.z > 0.32:
            t = (v.co.z - 0.32) / 0.46
            v.co.y += 0.22 * t * t
            v.co.x += 0.05 * math.sin(t * 3.0) * t
    H_, W_ = 512, 512
    vv = np.linspace(0, 1, H_)[:, None] * np.ones((1, W_))
    col = gradient((0.5, 0.4, 0.88), (0.93, 0.9, 1.0), (vv - 0.05) / 0.75)
    col = np.clip(col + ((fbm(H_, W_, 6, 81) - 0.5) * 0.22)[..., None], 0, 1)
    arr = np.ones((H_, W_, 4), np.float32); arr[..., :3] = col
    lathe_texture(wisp, arr)
    give(g, wisp)
    bpy.context.view_layer.update()
    skin_to(g, arm, lambda c: {"Top": smooth01((c.z - 0.12) / 0.3), "Body": 1 - smooth01((c.z - 0.12) / 0.3)})
    face = []
    p, n = surface(g, (0, -2.0, 0.26), (0, 1, 0))
    for s_ in (-1, 1):
        so = sphere("Augenhoehle%d" % s_, (0, 0, 0), 0.068, (1.2, 0.35, 0.85)); so.location = p + Vector((s_ * 0.085, 0.022, 0.045)); so.rotation_euler = (0, math.radians(s_ * -25), 0)
        face.append(give(so, M["dark"]))
        e = sphere("Auge%d" % s_, (0, 0, 0), 0.052, (1.2, 0.45, 0.8)); e.location = p + Vector((s_ * 0.085, 0.004, 0.045)); e.rotation_euler = (0, math.radians(s_ * -25), 0)
        face.append(give(e, M["eye"]))
        face.append(give(sphere("Pupille%d" % s_, tuple(p + Vector((s_ * 0.078, -0.018, 0.04))), 0.018), M["pupil"]))
    grin = [tuple(p + Vector((x, 0.006 + 0.05 * x * x, -0.05 + 2.4 * x * x))) for x in (-0.09, -0.045, 0.0, 0.045, 0.09)]
    face.append(give(tube("Grinsen", grin, [0.008, 0.014, 0.016, 0.014, 0.008], segs=8), M["dark"]))
    attach(join_parts(face, "Irrlicht_Gesicht"), arm, "Top")
    orbs = []
    for i, a in enumerate([i * 2 * math.pi / 3 + 0.5 for i in range(3)]):
        q, m = surface(g, (2.0 * math.cos(a), 2.0 * math.sin(a), 0.1 + 0.03 * i), (-math.cos(a), -math.sin(a), 0))
        if q is not None:
            orbs.append(give(sphere("Nebelkugel%d" % i, tuple(q + m * 0.012), 0.04), M["fog"]))
    attach(join_parts(orbs, "Irrlicht_Kugeln"), arm, "Body")
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
    parts = fog_ring("Nebelring", (c.x, c.y + 0.12, c.z - 0.42), 0.66, 0.016, 6, 0.045, M, tilt=10)
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
    ghost_paint(T, R["purple"] * R["head"], 0.3)
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
    k = ridges(P, freq * 0.45, seed + 1, 0.03) ** 1.5 * np.clip((fbm3(P, 4.0, seed + 2, 3) - 0.42) / 0.08, 0, 1)
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
    attach(join_parts(energy_ring("Energiering", (c.x, c.y + 0.12, c.z - 0.42), 0.68, 0.016, (10, 14, 0), M, 5, rnd), "Energiering"), arm, "Bone_001")
    for chain in (("Bone_009", "Bone_008", "Bone_006"), ("Bone_013", "Bone_012", "Bone_010")):
        tip = bone_pt(arm, chain[2], 1.0)
        attach(shard("HornKristall" + chain[0], tip - Vector((0, 0, 0.04)), Vector((0, 0.1, 1.0)), 0.12, 0.03, M["cr"]), arm, chain[2])

@variante("wurm_zombie", "zombie")
def leerenwandler(arm, body):
    """Herz des Wurmlochs, mittel: Leerenwandler – hagere Gestalt aus Sternenhimmel mit funkelnden Sternen,
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

# ---------------------------------------------------------------- Ozeanwelt (Welt 13 und 14): Stil der Tiefseekrake
# (Violett, Türkis, Orange wie Tiefseekrake, Blubberfisch und Krabbenpanzer)

def ocean_mats():
    return {
        "purple": look("Krakenviolett", (0.5, 0.22, 0.72), rough=0.45),
        "teal": look("Meerestuerkis", (0.15, 0.75, 0.8), rough=0.4),
        "orange": look("Flossenorange", (1.0, 0.45, 0.15), rough=0.45),
        "sucker": look("Saugnapf", (0.93, 0.85, 0.68), rough=0.5),
        "lure": look("Leuchtkoeder", (0.85, 1.0, 0.6), rough=0.2, emit=(0.6, 1.0, 0.5), strength=4.0),
    }

def fin(name, base, d, length, width, mat, curl=0.3):
    """flache Flosse: gebogene, flach gedrückte Spitze von base in Richtung d"""
    d = Vector(d).normalized()
    side = d.cross(Vector((0, 0, 1)))
    if side.length < 0.1:
        side = d.cross(Vector((1, 0, 0)))
    side.normalize()
    up = side.cross(d).normalized()
    o = horn(name, tuple(base), tuple(Vector(base) + d * length * 0.55 + up * length * curl * 0.4), tuple(Vector(base) + d * length + up * length * curl), width, n=10)
    for v in o.data.vertices:                      # flach: Dicke in Richtung side zusammendrücken
        rel = v.co - Vector(base)
        v.co = Vector(base) + rel - side * rel.dot(side) * 0.7
    return give(o, mat)

@variante("ozean_tentakler", "tentakler")
def rochenflieger(arm, body):
    """Ozeanwelt, mittel: Rochenflieger – fliegender Rochen: violetter Körper mit hellem Bauch, breite türkise
    Flügelflossen mit dunklen Flecken, orange Flossenkamm auf dem Kopf (wie die Tiefseekrake), orange Hörner und ein
    langer Rochenschwanz mit Endflosse"""
    M = ocean_mats()
    T = texels(body)
    px, P, N = T["px"], T["P"], T["N"]
    red = hue_mask(px, 0.02, 0.06, 0.35)
    teal = hue_mask(px, 0.49, 0.08, 0.3)
    hh, s, v = hsv(px)
    beige = np.clip((0.6 - s) / 0.1, 0, 1) * np.clip((v - 0.5) / 0.1, 0, 1) * hue_mask(px, 0.11, 0.07, 0.08)
    belly = np.clip(-N[..., 2] * 1.5, 0, 1)
    paint(T, red, gradient((0.5, 0.22, 0.72), (0.78, 0.6, 0.9), belly), keep_shading=0.45)
    edge, cid = worley3(P, 14.0, 151)
    spot = np.clip((0.35 - cid) / 0.1, 0, 1) * np.clip((edge - 0.008) / 0.01, 0, 1)
    paint(T, teal, gradient((0.12, 0.62, 0.72), (0.3, 0.85, 0.88), fbm3(P, 5.0, 153, 3)), keep_shading=0.35)
    paint(T, teal * spot, (0.08, 0.35, 0.5), keep_shading=0.2)
    paint(T, beige, (1.0, 0.5, 0.18), keep_shading=0.5)
    commit(T)
    parts = []
    for k, (x, y, L, tx) in enumerate(((0.0, 0.02, 0.24, 0.0), (-0.09, 0.08, 0.17, -0.5), (0.09, 0.08, 0.17, 0.5))):
        p, n = head_top(body, x, y)
        if p is not None:
            parts.append(fin("Kopfflosse%d" % k, p - n * 0.03, (tx, 0.45, 1.0), L, 0.07, M["orange"], curl=-0.25))
    q, m = back_pt(body, 0.0, 0.8)
    if q is not None:
        tail = tendril("Schwanz", tuple(q - m * 0.02), (0.0, 1.0, -0.25), 0.7, 0.035, 0.35, seed=7, n=14)
        parts.append(give(tail, M["purple"]))
        end = Vector(tail.data.vertices[-1].co)
        parts.append(fin("Schwanzflosse", end + Vector((0, -0.03, 0.0)), (0.0, 0.6, 0.5), 0.12, 0.05, M["orange"]))
    attach(join_parts(parts, "Rochenteile"), arm, "Bone_001")

@variante("ozean_brecher", "brecher")
def krakenschlaeger(arm, body):
    """Ozeanwelt, stark: Krakenschläger – massiger Tiefseeschläger mit violetter Krakenhaut und hellen Saugnapfpunkten,
    türkisem Taucheranzug, orangen Kopfflossen, einer leuchtenden Anglerfisch-Laterne auf der Stirn, kurzen
    Kinntentakeln und Flossen an den Unterarmen"""
    M = ocean_mats()
    T = texels(body); R = regions(T, arm)
    P = T["P"]
    paint(T, R["skin"], (0.5, 0.22, 0.72), keep_shading=0.5)
    edge, cid = worley3(P, 18.0, 161)
    dots = np.clip((0.012 - (edge * 0 + np.linalg.norm(P * 0, axis=-1))) , 0, 1)
    f1 = noise3(P, 40.0, 163)
    suck = np.clip((f1 - 0.82) / 0.05, 0, 1) * np.clip((fbm3(P, 4.0, 165, 2) - 0.45) / 0.1, 0, 1)
    paint(T, R["skin"] * suck, (0.93, 0.85, 0.68), keep_shading=0.3)
    paint(T, R["purple"] * (1 - R["head"]), (0.12, 0.58, 0.64), keep_shading=0.6)
    paint(T, R["purple"] * R["head"], (0.62, 0.32, 0.82), keep_shading=0.5)
    paint(T, R["grey"], (1.0, 0.5, 0.18), keep_shading=0.5)
    collar = np.maximum(R["white"] * (1 - R["head"]), R["collar"])
    paint(T, collar, (0.25, 0.85, 0.88), keep_shading=0.4)
    commit(T)
    parts = []
    for s_ in (-1, 1):
        p, n = surface(body, (s_ * 2.0, 0.02, bone_pt(arm, "mixamorig:Head", 0.75).z), (-s_, 0, 0))
        if p is not None:
            parts.append(fin("Kopfflosse%d" % s_, p - n * 0.03, (s_ * 1.0, 0.4, 0.6), 0.2, 0.08, M["orange"], curl=0.2))
    p, n = head_top(body, 0.0, 0.0)
    if p is not None:
        parts.append(fin("Kammflosse", p - n * 0.03, (0.0, 0.6, 1.0), 0.22, 0.08, M["orange"], curl=-0.2))
    q, m = front_pt(body, 0.0, bone_pt(arm, "mixamorig:Head", 0.85).z)
    if q is not None:
        st = [q - m * 0.01, q + Vector((0, -0.08, 0.12)), q + Vector((0, -0.2, 0.14)), q + Vector((0, -0.27, 0.06))]
        parts.append(give(tube("Laternenstiel", [tuple(c) for c in st], [0.016, 0.013, 0.011, 0.01], segs=8), M["purple"]))
        parts.append(give(sphere("Laterne", tuple(st[-1] + Vector((0, 0, -0.035))), 0.045), M["lure"]))
    jaw = front_pt(body, 0.0, bone_pt(arm, "mixamorig:Head", 0.1).z)
    if jaw[0] is not None:
        c0 = jaw[0] - jaw[1] * 0.02
        for k, (dx, L) in enumerate(((-0.08, 0.16), (-0.03, 0.2), (0.03, 0.2), (0.08, 0.16))):
            t_ = tendril("Kinntentakel%d" % k, tuple(c0 + Vector((dx, 0.01, 0.0))), (dx * 2.0, -0.35, -1.0), L, 0.025, 0.9, seed=40 + k)
            parts.append(give(t_, M["purple"]))
    attach(join_parts(parts, "Krakenkopf"), arm, "mixamorig:Head")
    for s_, side in ((1, "Left"), (-1, "Right")):
        f0 = bone_pt(arm, "mixamorig:%sForeArm" % side, 0.4)
        attach(fin("Armflosse" + side, f0 + Vector((s_ * 0.06, 0.04, 0.0)), (s_ * 0.7, 0.6, 0.4), 0.17, 0.06, M["teal"], curl=0.25), arm, "mixamorig:%sForeArm" % side)

# ---------------------------------------------------------------- Kristallplanet (Welt 15 und 16): Juwelen
# Geschliffene Edelsteine in Gold gefasst, Rosenquarz, Diamant (klar anders als Höhlenkristall und Sternenkristall)

def gem_mats():
    return {
        "gold": look("Gold", (1.0, 0.78, 0.32), rough=0.25, metal=0.9),
        "gold2": look("Altgold", (0.82, 0.58, 0.22), rough=0.35, metal=0.85),
        "rose": look("Rosenquarz", (1.0, 0.58, 0.76), rough=0.08, emit=(1.0, 0.45, 0.7), strength=0.35),
        "rose2": look("Rosenquarz2", (0.95, 0.4, 0.62), rough=0.08, emit=(0.9, 0.3, 0.55), strength=0.35),
        "diamond": look("Diamant", (0.92, 0.97, 1.0), rough=0.04, emit=(0.7, 0.85, 1.0), strength=0.5),
        "ruby": look("Rubin", (0.92, 0.1, 0.26), rough=0.06, emit=(0.85, 0.05, 0.2), strength=0.9),
        "sapphire": look("Saphir", (0.15, 0.35, 1.0), rough=0.06, emit=(0.1, 0.3, 1.0), strength=0.9),
        "emerald": look("Smaragd", (0.1, 0.85, 0.45), rough=0.06, emit=(0.05, 0.8, 0.4), strength=0.9),
        "pearl": look("Perle", (0.96, 0.93, 0.95), rough=0.25),
        "dark": look("Juwelendunkel", (0.12, 0.06, 0.12), rough=0.4),
    }

def gem(name, c, n, r, mat):
    """geschliffener Edelstein (Brillant): Tafel, Krone, Rundiste, Spitze; die Tafel zeigt in Richtung n"""
    bm = bmesh.new()
    k = 8
    table = [bm.verts.new((r * 0.55 * math.cos(a + math.pi / k), r * 0.55 * math.sin(a + math.pi / k), r * 0.35)) for a in [i * 2 * math.pi / k for i in range(k)]]
    girdle = [bm.verts.new((r * math.cos(a), r * math.sin(a), 0.0)) for a in [i * 2 * math.pi / k for i in range(k)]]
    tip = bm.verts.new((0, 0, -r * 0.85))
    bm.faces.new(table)
    for i in range(k):
        j = (i + 1) % k
        bm.faces.new([girdle[i], girdle[j], table[i]])
        bm.faces.new([table[i], girdle[j], table[j]])
        bm.faces.new([girdle[j], girdle[i], tip])
    o = finish(name, bm, smooth=False)
    o.matrix_world = Matrix.Translation(Vector(c)) @ Vector(n).normalized().to_track_quat('Z', 'Y').to_matrix().to_4x4()
    return give(o, mat)

def set_gem(name, p, n, r, mat, G, sink=0.4):
    """Edelstein in goldener Fassung, etwas in die Oberfläche eingelassen"""
    c = Vector(p) + Vector(n) * r * (0.35 - sink)
    parts = [gem(name, c, n, r, mat)]
    t = torus(name + "Fassung", (0, 0, 0), r * 1.02, r * 0.16, rot=(0, 0, 0), segs=24)
    t.matrix_world = Matrix.Translation(c) @ Vector(n).normalized().to_track_quat('Z', 'Y').to_matrix().to_4x4()
    parts.append(give(t, G["gold"]))
    return parts

def gold_paint(T, mask, seed, engrave=True, base=(1.0, 0.78, 0.32)):
    """Gold mit Gravur (feine dunkle Ranken)"""
    P = T["P"]
    paint(T, mask, np.asarray(base, np.float32) * (0.85 + 0.3 * fbm3(P, 6.0, seed, 2)[..., None]), keep_shading=0.6)
    if engrave:
        paint(T, mask * ridges(P, 9.0, seed + 1, 0.03) * 0.7, (0.55, 0.36, 0.12), keep_shading=0.0)

def facet_paint(T, mask, seed, cols, freq=14.0, lead=None, glow_k=0.4):
    """facettierter Edelstein: jede Zelle eine Farbe aus cols, helle Lichtpunkte; lead: Bleifassung (Farbe der Kanten)"""
    P = T["P"]
    edge, cid = worley3(P, freq, seed)
    out = np.zeros(cid.shape + (3,), np.float32)
    n = len(cols)
    for i, c in enumerate(cols):
        k = ((cid * n).astype(int) == i)[..., None]
        out = np.where(k, np.asarray(c, np.float32), out)
    out = out * (0.8 + 0.35 * fbm3(P, 30.0, seed + 2, 2)[..., None])
    paint(T, mask, out, keep_shading=0.3)
    glint = np.clip((noise3(P, 70.0, seed + 3) - 0.84) / 0.05, 0, 1)
    paint(T, mask * glint, (1.0, 1.0, 1.0), keep_shading=0.0)
    if lead is not None:
        paint(T, mask * np.clip(1 - edge / 0.004, 0, 1), lead, keep_shading=0.2)
    glow(T, mask * (glow_k * 0.5 + glint), (0.9, 0.8, 1.0))

def snail(name, length, height, G, body_m, shell_m, band_m, gem_mats, rnd, gems=6, spike=1.0, spike_m=None):
    """Juwelenschnecke: Schneckenfuß (flach, vorn mit Kopf und Fühleraugen) und ein eingerolltes Gehäuse aus
    Rosenquarz mit Goldband und eingesetzten Edelsteinen. Liefert (Fußteile, Gehäuseteile, Kopfteile)."""
    L = length; Hh = height
    path = [(0.0, L * 0.5, 0.04 * Hh), (0.0, L * 0.25, 0.09 * Hh), (0.0, 0.0, 0.12 * Hh), (0.0, -L * 0.25, 0.14 * Hh), (0.0, -L * 0.42, 0.22 * Hh), (0.0, -L * 0.5, 0.34 * Hh)]
    radii = [L * 0.03, L * 0.13, L * 0.17, L * 0.16, L * 0.13, L * 0.11]
    foot = tube(name + "Fuss", path, radii, segs=24)
    for v in foot.data.vertices:
        v.co.x *= 1.25
        v.co.z = max(v.co.z, 0.012 + 0.35 * v.co.x * v.co.x)   # leicht gewölbter Bauch statt flacher Fläche (flackerte)
    give(foot, body_m)
    head = give(sphere(name + "Kopf", path[-1], L * 0.115, (1.15, 1.0, 1.0)), body_m)
    # Gehäuse: logarithmische Spirale in der Seitenebene, Röhre wird nach innen dünner
    cy, cz = L * 0.08, Hh * 0.62
    pts, rr = [], []
    for i in range(40):
        t = i / 39
        a = t * 2.6 * math.pi
        R = Hh * 0.36 * math.exp(-0.42 * a)
        pts.append((0.0, cy + R * math.sin(a), cz - R * math.cos(a)))
        rr.append(Hh * 0.3 * math.exp(-0.42 * a) + 0.004)
    shell = give(tube(name + "Gehaeuse", pts, rr, segs=28), shell_m)
    for v in shell.data.vertices:
        v.co.x *= 1.1
    # Goldband als eigener schmaler Wulst auf dem Rücken der Röhre (Kommentar 25.11.: das übergestülpte Band flackerte)
    band_pts, band_r = [], []
    for (x, y, z), r_ in zip(pts, rr):
        out = Vector((0.0, y - cy, z - cz))
        out = out.normalized() if out.length > 1e-4 else Vector((0, 0, 1))
        band_pts.append(tuple(Vector((0.0, y, z)) + out * r_ * 0.97))
        band_r.append(max(0.004, r_ * 0.11))
    band = give(tube(name + "Goldband", band_pts[:-2], band_r[:-2], segs=10), band_m)
    shell_parts = [shell, band]
    for i in range(6, 30, 4):
        (x, y, z), r_ = pts[i], rr[i]
        c = Vector((0.0, y, z)); out = (c - Vector((0.0, cy, cz))).normalized()
        shell_parts.append(shard(name + "Kamm%d" % i, c + out * r_ * 0.8, out, r_ * 0.9 * spike, r_ * 0.22 * min(spike, 1.4),
                                 spike_m or (gem_mats[(i // 4) % len(gem_mats)] if i % 8 == 2 else shell_m)))
    for g_ in range(gems):
        i = int(4 + g_ * 30 / max(1, gems))
        (x, y, z), r_ = pts[i], rr[i]
        for s_ in (-1, 1):
            if g_ % 2 == (0 if s_ > 0 else 1):
                continue
            c = Vector((s_ * r_ * 1.05, y, z))
            shell_parts += set_gem(name + "Stein%d_%d" % (g_, s_), c, (s_, 0, 0.2), r_ * 0.45, gem_mats[g_ % len(gem_mats)], G)
    # Fühler mit Edelsteinaugen
    head_parts = []
    hp = Vector(path[-1])
    for s_ in (-1, 1):
        st = [hp + Vector((s_ * L * 0.05, 0, L * 0.06)), hp + Vector((s_ * L * 0.09, -L * 0.03, L * 0.2)), hp + Vector((s_ * L * 0.12, -L * 0.02, L * 0.32))]
        head_parts.append(give(tube(name + "Fuehler%d" % s_, [tuple(c) for c in st], [L * 0.025, L * 0.02, L * 0.017], segs=10), body_m))
        head_parts.append(gem(name + "Auge%d" % s_, st[-1] + Vector((0, -L * 0.01, L * 0.02)), (0, -1, 0.4), L * 0.05, gem_mats[0]))
    return [foot, head], shell_parts, head_parts

@variante("rosen_schleimling", "schleimling")
def glitzerling(arm, body):
    """Kristallplanet, leicht: Glitzerling – kleiner, schwebender Edelstein (Kommentar 25.11.: keine Schnecke, kleiner und
    leichter): ein geschliffener Rosenquarz mit Gesicht auf der Tafel, zwei kleine goldene Flügel und zwei winzige
    Diamanten, die um ihn kreisen. Eigene Figur auf dem Skelett des Schleimlings (hüpft und schwebt)."""
    G = gem_mats()
    eye_m = look("Glitzeraugen", (0.08, 0.03, 0.08), rough=0.2)
    shine = look("Glanzpunkt", (1, 1, 1), rough=0.2, emit=(1, 1, 1), strength=2.0)
    c = Vector((0.0, 0.0, 0.34))
    parts = [gem("Rosenstein", c, (0, -1, 0.12), 0.24, G["rose"])]
    fy = c.y - 0.24 * 0.35 - 0.004
    for s_ in (-1, 1):
        parts.append(give(sphere("Auge%d" % s_, (s_ * 0.05, fy, c.z + 0.035), 0.028, (0.85, 0.3, 1.15)), eye_m))
        parts.append(give(sphere("Glanz%d" % s_, (s_ * 0.05 + 0.01, fy - 0.008, c.z + 0.05), 0.009), shine))
        parts.append(give(tube("Braue%d" % s_, [(s_ * 0.085, fy - 0.004, c.z + 0.085), (s_ * 0.05, fy - 0.006, c.z + 0.078), (s_ * 0.02, fy - 0.005, c.z + 0.066)], [0.007, 0.008, 0.006], segs=6), eye_m))
    parts.append(give(tube("Mund", [(-0.03, fy - 0.004, c.z - 0.035), (0.0, fy - 0.006, c.z - 0.045), (0.03, fy - 0.004, c.z - 0.035)], [0.006, 0.007, 0.006], segs=6), eye_m))
    for s_ in (-1, 1):
        b0 = c + Vector((s_ * 0.17, 0.08, 0.04))
        parts += feather_fan("Fluegel%d_" % s_, b0, (s_ * 0.5, 0.8, 0.45), (0, 0, 1), 3, 0.1, 0.035, (G["gold"], G["gold2"]), spread=40)
    for i, a in enumerate((0.6, 3.6)):
        parts.append(gem("Begleiter%d" % i, c + Vector((0.27 * math.cos(a), 0.27 * math.sin(a), -0.1 + 0.08 * i)), (math.cos(a), math.sin(a), 0.5), 0.03, G["diamond"]))
    attach(join_parts(parts, "Glitzerling"), arm, "Top")
    dampen_scale(arm, ("Body", "Top"), 0.5)
    remove_body(body)

@variante("rosen_zombie", "zombie")
def rosenritter(arm, body):
    """Kristallplanet, mittel: Rosenritter – schlanker Ritter mit Haut aus Rosenquarz (schimmernd, mit hellen
    Lichtpunkten), goldener Rüstung mit Gravur, Perlenkragen, goldenen Schulterstücken mit Rubin, einem Rosenquarz-
    Diadem und leuchtend rosa Augen"""
    G = gem_mats()
    T = texels(body); R = regions(T, arm)
    facet_paint(T, R["skin"], 181, [(1.0, 0.6, 0.78), (0.95, 0.48, 0.68), (1.0, 0.72, 0.85)], freq=12.0, glow_k=0.3)
    gold_paint(T, R["purple"] * (1 - R["head"]), 183)
    paint(T, R["purple"] * R["head"], (1.0, 0.75, 0.86), keep_shading=0.4)
    paint(T, R["grey"], (0.96, 0.93, 0.95), keep_shading=0.4)
    eyes = R["white"] * R["head"]
    paint(T, eyes, (1.0, 0.75, 0.9), keep_shading=0.2)
    glow(T, eyes, (1.0, 0.35, 0.7))
    commit(T, strength=1.2)
    rnd = random.Random(185)
    for s_, side in ((1, "Left"), (-1, "Right")):
        a0 = bone_pt(arm, "mixamorig:%sArm" % side)
        p, n = surface(body, (a0.x, a0.y, a0.z + 0.12), (0, 0, -1))
        c = p if p is not None else a0
        dome = sphere("Schulterstueck" + side, (0, 0, 0), 0.085, (1.0, 1.1, 0.55)); dome.location = c + Vector((s_ * 0.015, 0, 0.01))
        parts = [give(dome, G["gold"])] + set_gem("SchulterRubin" + side, c + Vector((s_ * 0.015, 0, 0.055)), (s_ * 0.3, 0, 1), 0.03, G["ruby"], G)
        attach(join_parts(parts, "Schulter" + side), arm, "mixamorig:%sArm" % side)
    p, n = front_pt(body, 0.0, bone_pt(arm, "mixamorig:Head", 0.9).z)
    di = []
    if p is not None:
        di += set_gem("Stirnstein", p, n, 0.03, G["ruby"], G, sink=0.2)
    for k, (x, h) in enumerate(((0.0, 0.14), (-0.07, 0.1), (0.07, 0.1))):
        q, m = head_top(body, x, -0.02)
        if q is not None:
            di.append(shard("Diadem%d" % k, q - m * 0.02, (m + Vector((x * 3, -0.2, 0.6))).normalized(), h, 0.028, G["rose"] if k == 0 else G["rose2"]))
    attach(join_parts(di, "Diadem"), arm, "mixamorig:Head")
    nk = bone_pt(arm, "mixamorig:Neck", 0.1)
    pearls = [give(sphere("Perle%d" % i, (nk.x + 0.1 * math.cos(a), nk.y + 0.09 * math.sin(a), nk.z - 0.02), 0.022), G["pearl"])
              for i, a in enumerate([i * 2 * math.pi / 14 for i in range(14)])]
    attach(join_parts(pearls, "Perlenkragen"), arm, "mixamorig:Neck")

@variante("rosen_panzerkaefer", "panzerkaefer")
def juwelenkaefer(arm, body):
    """Kristallplanet, stark: Juwelenkäfer – schwerer Käfer mit goldenem, graviertem Panzer, in den große geschliffene
    Edelsteine gefasst sind (Rosenquarz, Diamant, Rubin), Körper aus Rosenquarz, Perlenfüße und ein Rosenquarzhorn"""
    G = gem_mats()
    T = texels(body)
    px, P, N = T["px"], T["P"], T["N"]
    teal = hue_mask(px, 0.49, 0.08, 0.3)
    red = np.maximum(hue_mask(px, 0.02, 0.06, 0.35), hue_mask(px, 0.97, 0.05, 0.3))
    hh, s, v = hsv(px)
    beige = np.clip((0.6 - s) / 0.1, 0, 1) * np.clip((v - 0.5) / 0.1, 0, 1) * hue_mask(px, 0.11, 0.07, 0.08)
    gold_paint(T, teal, 191)
    facet_paint(T, red, 193, [(1.0, 0.6, 0.78), (0.95, 0.48, 0.68), (1.0, 0.72, 0.85)], freq=16.0, glow_k=0.25)
    paint(T, beige, (0.96, 0.93, 0.95), keep_shading=0.5)
    commit(T, strength=1.0)
    parts = []
    mats = [G["rose"], G["diamond"], G["ruby"], G["rose2"], G["sapphire"], G["diamond"], G["emerald"]]
    for k, (x, y, r) in enumerate(((0.0, 0.05, 0.07), (-0.14, 0.1, 0.05), (0.14, 0.08, 0.05), (-0.08, -0.08, 0.04), (0.09, -0.09, 0.04), (0.0, 0.2, 0.045), (-0.2, -0.02, 0.035))):
        p, n = surface(body, (x, y, 2.0), (0, 0, -1))
        if p is not None and p.z > 0.15:
            parts += set_gem("Panzerstein%d" % k, p, n, r, mats[k % len(mats)], G, sink=0.35)
    attach(join_parts(parts, "Juwelenpanzer"), arm, "Body")
    h0 = bone_pt(arm, "Head", 0.4)
    q, m = surface(body, (0.0, -1.5, h0.z + 0.07), (0, 1, 0))
    if q is not None:
        attach(join_parts([shard("Horn", q - m * 0.03, (0, -0.6, 1.0), 0.2, 0.045, G["rose"]), shard("Horn2", q - m * 0.02 + Vector((0.04, 0, 0.02)), (0.4, -0.5, 1.0), 0.11, 0.03, G["rose2"])], "Horn"), arm, "Head")

@variante("glitzer_krabbler", "krabbler")
def glitzerwicht(arm, body):
    """Kristallplanet, leicht: Glitzerwicht – kleiner Kobold mit Haut aus geschliffenem Diamant (weiß-blau funkelnd),
    königsblauem Samtanzug mit Gold, bunten Edelsteinen am Kopf (Rubin, Saphir, Smaragd) und einem Diamantkrönchen"""
    G = gem_mats()
    T = texels(body); R = regions(T, arm)
    facet_paint(T, R["skin"], 201, [(0.9, 0.95, 1.0), (0.75, 0.85, 1.0), (0.97, 0.97, 1.0)], freq=14.0, glow_k=0.25)
    paint(T, R["purple"] * (1 - R["head"]), (0.16, 0.22, 0.62), keep_shading=0.6)
    facet_paint(T, R["purple"] * R["head"], 203, [(0.92, 0.1, 0.26), (0.15, 0.35, 1.0), (0.1, 0.85, 0.45)], freq=3.0, glow_k=0.9)
    gold_paint(T, R["grey"], 205, engrave=False)
    eyes = R["white"] * R["head"]
    paint(T, eyes, (0.85, 0.95, 1.0), keep_shading=0.2)
    glow(T, eyes, (0.5, 0.75, 1.0))
    commit(T, strength=1.2)
    cr = []
    for k, (x, h) in enumerate(((0.0, 0.15), (-0.09, 0.11), (0.09, 0.11), (-0.16, 0.08), (0.16, 0.08))):
        q, m = head_top(body, x, 0.0)
        if q is not None:
            cr.append(shard("Krone%d" % k, q - m * 0.02, (m + Vector((x * 2, 0, 0.5))).normalized(), h, 0.026, G["diamond"]))
    attach(join_parts(cr, "Diamantkrone"), arm, "mixamorig:Head")

@variante("glitzer_tentakler", "tentakler")
def facettenfalter(arm, body):
    """Kristallplanet, mittel: Facettenfalter – Flugwesen mit Flügeln wie Bleiglasfenster aus bunten Edelsteinen
    (Rubin, Saphir, Smaragd, Topas) in goldener Fassung, Körper aus geschliffenem Saphir, goldenen Hörnern und
    Diamanten an den Flügelspitzen"""
    G = gem_mats()
    T = texels(body)
    px, P = T["px"], T["P"]
    red = hue_mask(px, 0.02, 0.06, 0.35)
    teal = hue_mask(px, 0.49, 0.08, 0.3)
    hh, s, v = hsv(px)
    beige = np.clip((0.6 - s) / 0.1, 0, 1) * np.clip((v - 0.5) / 0.1, 0, 1) * hue_mask(px, 0.11, 0.07, 0.08)
    facet_paint(T, red, 211, [(0.2, 0.35, 0.95), (0.12, 0.25, 0.8), (0.3, 0.48, 1.0)], freq=12.0, glow_k=0.3)
    facet_paint(T, teal, 213, [(0.92, 0.12, 0.28), (0.15, 0.4, 1.0), (0.1, 0.85, 0.45), (1.0, 0.75, 0.15)], freq=10.0, lead=(0.95, 0.72, 0.28), glow_k=0.9)
    gold_paint(T, beige, 215, engrave=False)
    commit(T, strength=1.3)
    for side, chain in ((1, ("Bone_031", "Bone_030", "Bone_029")), (-1, ("Bone_026", "Bone_025", "Bone_024"))):
        tip = bone_pt(arm, chain[2], 1.0)
        attach(shard("Flügeldiamant%d" % side, tip + Vector((0, 0, -0.02)), Vector((side * 0.6, 0.0, 1.0)), 0.12, 0.035, G["diamond"]), arm, chain[2])
        mid = bone_pt(arm, chain[1], 0.9)
        attach(gem("Flügelstein%d" % side, mid + Vector((0, -0.03, 0.0)), (0, -1, 0.2), 0.04, G["ruby"]), arm, chain[1])
    q, m = front_pt(body, 0.0, 1.12)
    if q is not None:
        attach(join_parts(set_gem("Stirnstein", q, m, 0.035, G["emerald"], G, sink=0.2), "Stirnstein"), arm, "Bone_001")

@variante("glitzer_brecher", "brecher")
def goldbrecher(arm, body):
    """Kristallplanet, stark: Goldbrecher – massiger Schläger mit Haut aus graviertem Gold, königsblauer Rüstung,
    leuchtendem Diamantkragen, großem Rubin in der Brust, Edelsteingruppen auf den Schultern, Goldreifen mit Steinen
    an den Unterarmen und einem Diamantkamm"""
    G = gem_mats()
    T = texels(body); R = regions(T, arm)
    gold_paint(T, R["skin"], 221, base=(0.95, 0.74, 0.3))
    paint(T, R["purple"] * (1 - R["head"]), (0.16, 0.22, 0.62), keep_shading=0.6)
    gold_paint(T, R["purple"] * R["head"], 223, base=(0.85, 0.6, 0.24))
    paint(T, R["grey"], (0.96, 0.93, 0.95), keep_shading=0.4)
    collar = np.maximum(R["white"] * (1 - R["head"]), R["collar"])
    facet_paint(T, collar, 225, [(0.9, 0.95, 1.0), (0.75, 0.85, 1.0), (0.97, 0.97, 1.0)], freq=20.0, glow_k=0.8)
    eyes = R["white"] * R["head"]
    paint(T, eyes, (0.85, 0.95, 1.0), keep_shading=0.2)
    glow(T, eyes, (0.5, 0.75, 1.0))
    commit(T, strength=1.2)
    rnd = random.Random(227)
    sp = bone_pt(arm, "mixamorig:Spine1", 0.6)
    p, n = front_pt(body, 0.0, sp.z)
    if p is not None:
        attach(join_parts(set_gem("Brustrubin", p, n, 0.075, G["ruby"], G, sink=0.3), "Brustrubin"), arm, "mixamorig:Spine1")
    mats = (G["diamond"], G["ruby"], G["sapphire"], G["emerald"])
    for s_, side in ((1, "Left"), (-1, "Right")):
        a0 = bone_pt(arm, "mixamorig:%sArm" % side)
        parts = []
        for k, (dx, dy, h, r) in enumerate(((0.0, 0.0, 0.18, 0.05), (-s_ * 0.07, 0.06, 0.13, 0.04), (s_ * 0.05, -0.07, 0.12, 0.035))):
            p, n = surface(body, (a0.x + dx, a0.y + dy, a0.z + 0.15), (0, 0, -1))
            if p is not None:
                parts.append(shard("Schulterstein%s%d" % (side, k), p - n * 0.03, (n + Vector((s_ * 0.5, 0.1, 0))).normalized(), h, r, mats[k]))
        attach(join_parts(parts, "Schultersteine" + side), arm, "mixamorig:%sArm" % side)
        f0, f1 = bone_pt(arm, "mixamorig:%sForeArm" % side), bone_pt(arm, "mixamorig:%sForeArm" % side, 1.0)
        fm = f0.lerp(f1, 0.6)
        t = torus("Goldreif" + side, tuple(fm), 0.085, 0.022)
        t.rotation_euler = (f1 - f0).normalized().to_track_quat('Z', 'Y').to_euler()
        ring = [give(t, G["gold"])]
        ring.append(gem("Reifstein" + side, fm + Vector((s_ * 0.03, -0.07, 0.03)), (s_ * 0.3, -1, 0.3), 0.03, G["sapphire"]))
        attach(join_parts(ring, "Goldreif" + side), arm, "mixamorig:%sForeArm" % side)
    cr = []
    for k, (y, h) in enumerate(((-0.06, 0.16), (0.02, 0.2), (0.1, 0.15))):
        q, m = head_top(body, 0.0, y)
        if q is not None:
            cr.append(shard("Kamm%d" % k, q - m * 0.02, (m + Vector((0, y * 2, 0.3))).normalized(), h, 0.035, G["diamond"]))
    attach(join_parts(cr, "Diamantkamm"), arm, "mixamorig:Head")

# ---------------------------------------------------------------- Neue Bosse Kristallplanet (Welt 15 und 16)

def realistic_mouth(face, pm0, name, socket_m, throat_m, rnd, **kw):
    """Splitterzähne aus golem_face entfernen und ein realistisches Gebiss in die Maulöffnung setzen (Kommentar 25.11.:
    Maul wirkte grob und billig)"""
    keep = []
    for o in face:
        if o.name.startswith(("Oberzahn", "Unterzahn")):
            bpy.data.objects.remove(o, do_unlink=True)
        else:
            keep.append(o)
    if pm0 is not None:
        keep += jaw_set(name, pm0 + Vector((0, 0.035, 0.0)), 0.115, 0.05, socket_m, throat_m, rnd, **kw)
    return keep

def jaw_set(name, mc, a, b, socket_m, throat_m, rnd, enamel_col=(0.97, 0.95, 0.9), gum_col=(0.62, 0.16, 0.3), metal=0.0):
    """Realistisches Gebiss (Kommentar 25.11.: wirkte billig): dunkler Rachen, glühender Schlund, Zunge, Zahnfleisch
    oben und unten als Wulst, gebogene Zähne mit runder Wurzel und Spitze (vorn Schneidezähne, seitlich lange
    Fangzähne, hinten kleinere), alle der Bogenform des Mauls folgend"""
    mc = Vector(mc)
    gum = look(name + "Zahnfleisch", gum_col, rough=0.35, metal=metal * 0.5)
    tongue_m = look(name + "Zunge", (0.78, 0.25, 0.38), rough=0.3)
    enamel = look(name + "Zahnschmelz", enamel_col, rough=0.22 if metal == 0 else 0.3, metal=metal)
    out = []
    cav = sphere(name + "Rachen", (0, 0, 0), 1.0, (a, b * 0.45 / 0.55 * 0.82, b), segs=(32, 16)); cav.location = mc
    out.append(give(cav, socket_m))
    th = sphere(name + "Schlund", (0, 0, 0), 1.0, (a * 0.6, b * 0.3, b * 0.55)); th.location = mc + Vector((0, -b * 0.55, 0.0))
    out.append(give(th, throat_m))
    tg = sphere(name + "Zunge", (0, 0, 0), 1.0, (a * 0.55, b * 0.6, b * 0.28)); tg.location = mc + Vector((0, -b * 0.62, -b * 0.55))
    out.append(give(tg, tongue_m))
    def arch(u, top):
        y = mc.y - b * 0.95 * (1 - 0.55 * u * u)
        z = mc.z + (1 if top else -1) * b * (0.88 - 0.25 * u * u)
        return Vector((u * a * 0.92, y, z))
    for top in (True, False):
        pts = [arch(-1 + 2 * k / 14, top) for k in range(15)]
        out.append(give(tube(name + ("Oben" if top else "Unten") + "Fleisch", [tuple(p_) for p_ in pts], [b * 0.12] + [b * 0.2] * 13 + [b * 0.12], segs=10), gum))
        us = (-0.82, -0.58, -0.36, -0.12, 0.12, 0.36, 0.58, 0.82) if top else (-0.7, -0.45, -0.2, 0.05, 0.3, 0.55)
        for i, u in enumerate(us):
            base = arch(u, top)
            fang = (abs(abs(u) - 0.58) < 0.05) if top else (abs(abs(u) - 0.45) < 0.05)
            L = b * (1.05 if fang else (0.55 if abs(u) < 0.3 else 0.45)) * rnd.uniform(0.92, 1.05)
            r0 = b * (0.17 if fang else 0.13)
            d = Vector((0, 0, -1 if top else 1))
            fwd = Vector((0, -1, 0)) * L * 0.18
            pts = [base - d * r0 * 0.3, base + d * L * 0.35 + fwd * 0.4, base + d * L * 0.75 + fwd * 0.8, base + d * L + fwd]
            out.append(give(tube(name + "Zahn%s%d" % ("O" if top else "U", i), [tuple(p_) for p_ in pts], [r0, r0 * 0.9, r0 * 0.55, r0 * 0.08], segs=10), enamel))
    return out

@variante("juwelen_schnecke", "schleimmutter")
def juwelenschnecke(arm, body):
    """Rosenkristalle (Welt 15), Boss: Juwelenschnecke – riesige, bedrohliche Schnecke (Kommentar 25.11.: zu harmlos):
    dunkelrosa Fuß mit Rubinstacheln an den Seiten, eingerolltes Gehäuse aus Rosenquarz mit Goldwulst, eingesetzten
    Edelsteinen und einem Kamm aus großen Rubinstacheln, Fühler mit Rubinaugen, rot glühende, böse Augen am Kopf, ein
    breites Maul mit zwei Reihen Diamantzähnen und glühendem Schlund, goldene Krone. Eigene Figur auf dem Skelett der
    Schleimmutter."""
    G = gem_mats()
    skin = look("Schneckenhaut", (0.86, 0.38, 0.58), rough=0.3, emit=(0.6, 0.15, 0.35), strength=0.15)
    ruby_d = look("Rubinstachel", (0.7, 0.03, 0.14), rough=0.06, emit=(0.6, 0.02, 0.1), strength=0.9)
    glow_eye = look("Gluehauge", (1.0, 0.25, 0.2), rough=0.2, emit=(1.0, 0.12, 0.08), strength=5.0)
    socket = look("Augenhoehle", (0.12, 0.02, 0.06), rough=0.5)
    throat = look("Schlund", (0.6, 0.05, 0.12), rough=0.5, emit=(0.8, 0.08, 0.15), strength=1.6)
    rnd = random.Random(301)
    foot, shell, head = snail("Juwel", 1.25, 1.2, G, skin, G["rose"], G["gold"], [G["ruby"], G["diamond"], G["ruby"], G["diamond"]], rnd, gems=8, spike=1.9, spike_m=ruby_d)
    for o in foot:
        skin_to(o, arm, lambda c: {"Top": smooth01((c.z - 0.12) / 0.3), "Body": 1 - smooth01((c.z - 0.12) / 0.3)})
    hd = next(o for o in foot if o.name.endswith("Kopf"))
    hp = Vector((0.0, -0.625, 0.408))
    extra = []
    # Kopf vorn: böse Augen in dunklen Höhlen, breites Maul mit glühendem Schlund und zwei Zahnreihen
    p, n = surface(hd, (0.0, -2.0, hp.z + 0.04), (0, 1, 0))
    for s_ in (-1, 1):
        so = sphere("Augenhoehle%d" % s_, (0, 0, 0), 0.045, (1.3, 0.5, 0.75)); so.location = p + Vector((s_ * 0.07, 0.012, 0.035)); so.rotation_euler = (0, math.radians(-s_ * 22), 0)
        extra.append(give(so, socket))
        e = sphere("Gluehauge%d" % s_, (0, 0, 0), 0.032, (1.3, 0.5, 0.7)); e.location = p + Vector((s_ * 0.07, -0.006, 0.035)); e.rotation_euler = (0, math.radians(-s_ * 22), 0)
        extra.append(give(e, glow_eye))
        extra.append(give(tube("Braue%d" % s_, [tuple(p + Vector((s_ * 0.13, -0.0, 0.09))), tuple(p + Vector((s_ * 0.07, -0.02, 0.08))), tuple(p + Vector((s_ * 0.015, -0.02, 0.055)))],
                               [0.014, 0.018, 0.013]), ruby_d))
    mc = p + Vector((0.0, 0.005, -0.06))
    extra += jaw_set("Gebiss", mc, 0.12, 0.055, socket, throat, rnd)
    # Krone sitzt auf dem Kopf (Strahl von oben)
    for k in range(5):
        a = math.radians(-60 + 30 * k)
        q, m = surface(hd, (math.sin(a) * 0.08, hp.y - math.cos(a) * 0.05 + 0.03, 2.0), (0, 0, -1))
        if q is not None:
            extra.append(shard("Krone%d" % k, q - m * 0.015, (math.sin(a) * 0.4, -0.15, 1.0), 0.09 + 0.05 * (k == 2), 0.022, G["gold"]))
    # Rubinstacheln an den Seiten des Fußes
    spikes = []
    for s_ in (-1, 1):
        for k, y in enumerate((-0.3, -0.12, 0.06, 0.24)):
            q, m = surface(foot[0], (s_ * 2.0, y, 0.12), (-s_, 0, 0))
            if q is not None:
                spikes.append(shard("Fussstachel%d_%d" % (s_, k), q - m * 0.02, (m + Vector((0, 0.3, 0.6))).normalized(), 0.1 - 0.015 * k, 0.025, ruby_d))
    attach(join_parts(shell + head + extra, "Juwel_Oben"), arm, "Top")
    attach(join_parts(spikes, "Juwel_Stacheln"), arm, "Body")
    dampen_scale(arm, ("Body", "Top"), 0.35)
    remove_body(body)

def brooch(name, p, n, r, G, center_m, halo_m, n_halo=12):
    """Prunk-Brosche: großer Brillant in Krappenfassung, Goldring, Kranz aus kleinen Diamanten, äußerer Goldring und
    goldene Zierstrahlen mit Rubintropfen (Kommentar 25.11.: Brustteil wirkte billig und ohne Details)"""
    n = Vector(n).normalized()
    q = n.to_track_quat('Z', 'Y').to_matrix()
    ex, ey = q @ Vector((1, 0, 0)), q @ Vector((0, 1, 0))
    c = Vector(p) + n * r * 0.1
    parts = [gem(name, c, n, r, center_m)]
    bez = torus(name + "Fassung", (0, 0, 0), r * 1.04, r * 0.09, segs=40); bez.matrix_world = Matrix.Translation(c - n * r * 0.02) @ q.to_4x4()
    parts.append(give(bez, G["gold"]))
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8
        d = ex * math.cos(a) + ey * math.sin(a)
        parts.append(give(tube(name + "Krappe%d" % k, [tuple(c + d * r * 1.08 - n * r * 0.05), tuple(c + d * r * 1.0 + n * r * 0.22), tuple(c + d * r * 0.82 + n * r * 0.3)],
                               [r * 0.06, r * 0.05, r * 0.035], segs=6), G["gold"]))
    plate = torus(name + "Teller", (0, 0, 0), r * 1.35, r * 0.2, segs=48); plate.matrix_world = Matrix.Translation(c - n * r * 0.12) @ q.to_4x4()
    parts.append(give(plate, G["gold2"]))
    for k in range(n_halo):
        a = k * 2 * math.pi / n_halo
        d = ex * math.cos(a) + ey * math.sin(a)
        parts += set_gem(name + "Kranz%d" % k, c + d * r * 1.35 + n * r * 0.1, n, r * 0.14, halo_m, G, sink=0.1)
    outer = torus(name + "Aussenring", (0, 0, 0), r * 1.62, r * 0.06, segs=56); outer.matrix_world = Matrix.Translation(c - n * r * 0.1) @ q.to_4x4()
    parts.append(give(outer, G["gold"]))
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        d = ex * math.cos(a) + ey * math.sin(a)
        b0 = c + d * r * 1.62 - n * r * 0.1
        tip = b0 + d * r * 0.7 - n * r * 0.05
        parts.append(give(tube(name + "Strahl%d" % k, [tuple(b0), tuple(b0 + d * r * 0.35 + n * r * 0.08 + (ex * -math.sin(a) + ey * math.cos(a)) * r * 0.12), tuple(tip)],
                               [r * 0.06, r * 0.05, r * 0.03], segs=8), G["gold"]))
        parts.append(gem(name + "Tropfen%d" % k, tip + d * r * 0.08, n, r * 0.12, center_m))
    return parts

@variante("edelstein_golem_alt", "koloss")
def edelsteingolem(arm, body):
    """Glitzerschlucht (Welt 16), Boss: Edelsteingolem – riesiger Golem aus Goldblöcken (Kommentar 25.11.: Farben
    abgestimmt auf Gold, tiefrotes Rubin und Diamant): Gelenke aus dunkel glühendem Rubin, Gesicht mit leuchtenden
    Diamantaugen und sauber sitzenden Diamantzähnen, eine Diamantkrone mit goldenen Fassungen, die auf dem Kopf sitzt,
    eine Prunk-Brosche mit großem Rubin auf der Brust und Rubin-Diamant-Kristalle auf den Schultern. Eigene Figur."""
    G = gem_mats()
    ruby = look("Rubin", (0.72, 0.03, 0.12), rough=0.05, emit=(0.55, 0.0, 0.08), strength=0.8)
    joint = look("Rubingelenk", (0.6, 0.03, 0.1), rough=0.08, emit=(0.45, 0.0, 0.07), strength=1.0)
    g = golem_body(arm, body, G["gold"], G["gold2"], joint, flat=True, subdiv=1, fist_m=G["gold2"], nail_m=G["diamond"], legs=1.4)
    H = "mixamorig:Head"
    hc = g["head"] + Vector((0, -0.08, 0.24))
    skull = block_at("Kopf", hc, (0.25, 0.23, 0.22), G["gold"], 31, True, 1)
    jaw = block_at("Kiefer", hc + Vector((0, -0.07, -0.15)), (0.22, 0.17, 0.1), G["gold2"], 32, True, 1)
    socket = look("Augenhoehle", (0.18, 0.02, 0.05), rough=0.6, emit=(0.35, 0.0, 0.05), strength=0.6)
    eye = look("Diamantauge", (0.9, 0.97, 1.0), rough=0.1, emit=(0.75, 0.9, 1.0), strength=4.0)
    core = look("Diamantkern", (1.0, 1.0, 1.0), rough=0.1, emit=(0.95, 0.97, 1.0), strength=8.0)
    mouth_in = look("Maulinneres", (0.3, 0.02, 0.06), rough=0.6, emit=(0.6, 0.02, 0.08), strength=1.2)
    pm0, nm0 = surface(jaw, (0.0, -2.0, hc.z - 0.135), (0, 1, 0))
    face = golem_face(skull, jaw, hc, {"socket": socket, "eye": eye, "core": core, "mouth": mouth_in, "tooth": G["diamond"],
                                      "brow": G["gold2"], "crack": ruby, "throat": joint})
    face = realistic_mouth(face, pm0, "Golemgebiss", mouth_in, joint, random.Random(41), gum_col=(0.45, 0.05, 0.12))
    head = [skull, jaw] + face
    # Krone sitzt auf dem Schädel (Strahl von oben je Zacke) mit goldener Fassung am Fuß
    bpy.context.view_layer.update()
    for k in range(5):
        x = (k - 2) * 0.075
        q, m = surface(skull, (hc.x + x, hc.y - 0.06 + 0.02 * abs(k - 2), hc.z + 1.0), (0, 0, -1))
        if q is None:
            continue
        hgt = (0.24, 0.17, 0.12)[abs(k - 2)]
        d = (Vector((x * 1.6, 0.05, 1.0))).normalized()
        head.append(shard("Krone%d" % k, q - m * 0.03, d, hgt, 0.035, G["diamond"]))
        col = torus("Kronenfassung%d" % k, (0, 0, 0), 0.042, 0.012, segs=16); col.matrix_world = Matrix.Translation(q + m * 0.005) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        head.append(give(col, G["gold"]))
    q, m = surface(skull, (hc.x, hc.y - 1.0, hc.z + 0.13), (0, 1, 0))
    if q is not None:
        head += set_gem("Stirnrubin", q, m, 0.04, ruby, G, sink=0.3)
    attach(join_parts(head, "Golem_Kopf"), arm, H)
    # Brosche vor die Brust (zwischen den beiden Brustblöcken liegt eine Fuge): vorderste Stelle der Blöcke messen,
    # Brosche auf eine goldene Grundplatte davor setzen, Blick nach vorn
    chest_o = bpy.data.objects.get("Golem_Spine2")
    zc = g["chest"].z + 0.02
    ys = [surface(chest_o, (x, -2.0, zc), (0, 1, 0))[0] for x in (-0.14, -0.08, 0.08, 0.14)] if chest_o is not None else []
    ys = [q.y for q in ys if q is not None]
    yf = (min(ys) if ys else g["chest"].y - 0.32) - 0.015
    p, n = Vector((0.0, yf, zc)), Vector((0.0, -1.0, 0.08)).normalized()
    plate = lathe("Grundplatte", [(0.03, 0.0), (0.03, 0.2), (0.0, 0.215), (-0.03, 0.2), (-0.03, 0.0)], segs=48)
    plate.matrix_world = Matrix.Translation(p + n * 0.005) @ n.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    attach(join_parts([give(plate, G["gold2"])] + brooch("Brust", p + n * 0.04, n, 0.11, G, ruby, G["diamond"]), "Golem_Brosche"), arm, "mixamorig:Spine2")
    rnd = random.Random(311)
    for s_, side in ((1, "Left"), (-1, "Right")):
        a0 = bone_pt(arm, "mixamorig:%sArm" % side)
        c = a0 + Vector((s_ * 0.06, 0.0, 0.3))
        parts = cluster("Schulterkristall" + side, c, Vector((s_ * 0.5, 0.1, 1.0)).normalized(), 0.3, 0.06, (ruby, G["diamond"], ruby), rnd, count=4)
        attach(join_parts(parts, "Schulterkristall" + side), arm, "mixamorig:%sArm" % side)

# ---------------------------------------------------------------- Sturmriese (Welt 17 und 18): Wolken und Blitze

def storm_mats():
    return {
        "cloud": look("Wolke", (0.93, 0.95, 1.0), rough=0.85, emit=(0.6, 0.65, 0.8), strength=0.12),
        "cloud_dark": look("Gewitterwolke", (0.42, 0.47, 0.6), rough=0.85),
        "bolt": look("Blitz", (1.0, 0.95, 0.45), rough=0.3, emit=(1.0, 0.9, 0.3), strength=6.0),
        "eye": look("Blitzauge", (1.0, 0.97, 0.6), rough=0.2, emit=(1.0, 0.9, 0.35), strength=5.0),
        "dark": look("Sturmdunkel", (0.08, 0.09, 0.16), rough=0.5),
        "copper": look("Kupfer", (0.85, 0.5, 0.3), rough=0.3, metal=0.85),
        "rain": look("Regen", (0.55, 0.75, 1.0), rough=0.1, emit=(0.3, 0.5, 1.0), strength=0.5),
        "tooth": look("Sturmzahn", (0.97, 0.97, 1.0), rough=0.3),
        "throat": look("Gewitterschlund", (1.0, 0.75, 0.3), rough=0.4, emit=(1.0, 0.6, 0.15), strength=2.2),
    }

def cloud_parts(name, c, size, seed, M, n=12, flat=0.75, dark_below=True):
    """Wolke aus vielen weichen Kugeln: oben hell, unten dunkler (Gewitter)"""
    rnd = random.Random(seed)
    c = Vector(c)
    parts = []
    for i in range(n):
        a = rnd.uniform(0, 2 * math.pi); u = rnd.uniform(-0.25, 1.0)
        p = c + Vector((math.cos(a) * size * rnd.uniform(0.25, 0.95), math.sin(a) * size * rnd.uniform(0.2, 0.7), u * size * 0.45))
        r = size * rnd.uniform(0.32, 0.5) * (1.0 - 0.25 * max(0.0, u))
        mat = M["cloud_dark"] if (dark_below and p.z < c.z - size * 0.05) else M["cloud"]
        parts.append(give(sphere("%s%d" % (name, i), tuple(p), r, (1.0, 1.0, flat), segs=(18, 10)), mat))
    return parts

def bolt(name, p0, p1, r, M, n=5, jitter=0.25, seed=0):
    """Blitz: Zickzack von p0 nach p1, wird zur Spitze dünner"""
    rnd = random.Random(seed)
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    side = d.cross(Vector((0, 1, 0)))
    if side.length < 1e-3:
        side = d.cross(Vector((1, 0, 0)))
    side.normalize()
    pts = [p0]
    for i in range(1, n):
        t = i / n
        pts.append(p0 + d * t + side * d.length * jitter * (1 if i % 2 else -1) * rnd.uniform(0.6, 1.0))
    pts.append(p1)
    radii = [r * (1 - 0.8 * i / n) for i in range(n)] + [0.0]
    o = tube(name, [tuple(q) for q in pts], radii, segs=6)
    for pl in o.data.polygons:
        pl.use_smooth = False
    return give(o, M["bolt"])

def storm_skin(T, mask, seed, base=(0.32, 0.44, 0.68)):
    """Sturmhaut: blaugrau mit hellen Wolkenschlieren und gelb leuchtenden Blitzadern"""
    P = T["P"]
    paint(T, mask, gradient(base, (0.55, 0.65, 0.85), fbm3(P, 5.0, seed, 3) * 1.4 - 0.3), keep_shading=0.4)
    veins = ridges(P, 6.0, seed + 1, 0.025) ** 1.5 * np.clip((fbm3(P, 3.5, seed + 2, 2) - 0.45) / 0.08, 0, 1)
    paint(T, mask * veins, (1.0, 0.95, 0.5), keep_shading=0.0)
    glow(T, mask * veins, (1.0, 0.85, 0.25))

def storm_face(c, k, M, parts, fill=False):
    """Gewitter-Gesicht vorn auf einer Wolke: wütende, gelb leuchtende Augen, dicke dunkle Brauen, offenes Maul mit Zähnen"""
    c = Vector(c)
    for s_ in (-1, 1):
        so = sphere("Augenhoehle%d" % s_, (0, 0, 0), 0.07 * k, (1.2, 0.5, 0.8)); so.location = c + Vector((s_ * 0.12 * k, 0, 0.06 * k))
        so.rotation_euler = (0, math.radians(-s_ * 18), 0); parts.append(give(so, M["dark"]))
        e = sphere("Auge%d" % s_, (0, 0, 0), 0.05 * k, (1.2, 0.5, 0.75)); e.location = c + Vector((s_ * 0.12 * k, -0.02 * k, 0.06 * k))
        e.rotation_euler = (0, math.radians(-s_ * 18), 0); parts.append(give(e, M["eye"]))
        parts.append(give(tube("Braue%d" % s_, [tuple(c + Vector((s_ * 0.22 * k, -0.01 * k, 0.17 * k))), tuple(c + Vector((s_ * 0.12 * k, -0.04 * k, 0.15 * k))),
                                               tuple(c + Vector((s_ * 0.03 * k, -0.05 * k, 0.1 * k)))], [0.035 * k, 0.04 * k, 0.03 * k]), M["cloud_dark"]))
    m = sphere("Maul", (0, 0, 0), 0.1 * k, (1.3, 0.45, 0.6)); m.location = c + Vector((0, -0.01 * k, -0.12 * k))
    parts.append(give(m, M["dark"]))
    if not fill:
        for i, x in enumerate((-0.07, 0.0, 0.07)):
            parts.append(shard("Zahn%d" % i, c + Vector((x * k, -0.045 * k, -0.075 * k)), (0, -0.2, -1), 0.04 * k, 0.014 * k, M["tooth"]))
        return
    # gefülltes, realistisches Maul (Kommentare 25.11.: wirkte leer, dann zu grob): dunkler Rachen, glühender Schlund,
    # Zunge, Zahnfleisch und gebogene Zähne mit Fangzähnen; die alte Maulkugel wird durch den Rachen ersetzt
    parts.remove(m); bpy.data.objects.remove(m, do_unlink=True)
    mc = c + Vector((0, -0.01 * k, -0.12 * k))
    parts += jaw_set("Sturmgebiss", mc, 0.13 * k, 0.058 * k, M["dark"], M["throat"], random.Random(17), gum_col=(0.3, 0.33, 0.48))

@variante("sturm_wolke_alt", "schleimmutter")      # alte Kugelwolke; neu: tools/monster/sturmwolke.py
def sturmwolke(arm, body):
    """Wolkenwirbel (Welt 17), Boss: Sturmwolke – riesige, wütende Gewitterwolke: oben weiß, unten dunkel, gelb
    leuchtende Augen unter dicken Brauen, offenes Maul mit Zähnen, Blitze und Regentropfen darunter und Windwirbel an
    den Seiten. Schwebt. Eigene Figur auf dem Skelett der Schleimmutter."""
    M = storm_mats()
    low = cloud_parts("WolkeUnten", (0, 0.02, 0.42), 0.62, 321, M, n=14, flat=0.7)
    up = cloud_parts("WolkeOben", (0, 0.05, 0.72), 0.5, 322, M, n=12, flat=0.8, dark_below=False)
    face = []
    storm_face((0, -0.47, 0.6), 1.25, M, face, fill=True)
    attach(join_parts(up + face, "Sturm_Oben"), arm, "Top")
    below = []
    for k, (x, y, L) in enumerate(((-0.28, -0.1, 0.42), (0.05, -0.2, 0.5), (0.3, 0.05, 0.38), (-0.05, 0.25, 0.34))):
        below.append(bolt("Blitz%d" % k, (x, y, 0.18), (x + 0.08 * (1 if k % 2 else -1), y - 0.05, 0.18 - L), 0.035, M, n=5, jitter=0.22, seed=330 + k))
    rnd = random.Random(331)
    for i in range(10):
        x, y = rnd.uniform(-0.45, 0.45), rnd.uniform(-0.3, 0.35)
        below.append(give(sphere("Tropfen%d" % i, (x, y, rnd.uniform(-0.15, 0.15)), 0.022, (0.8, 0.8, 1.6)), M["rain"]))
    for s_ in (-1, 1):
        pts = []; radii = []
        for k in range(18):
            t = k / 17; a = t * 1.7 * 2 * math.pi
            pts.append((s_ * (0.75 + 0.06 * t), 0.05 + 0.14 * (1 - t) * math.cos(a), 0.5 + 0.14 * (1 - t) * math.sin(a)))
            radii.append(0.03 * (1 - t) + 0.006)
        radii[-1] = 0.0
        below.append(give(tube("Wind%d" % s_, pts, radii), M["cloud"]))
    attach(join_parts(low + below, "Sturm_Unten"), arm, "Body")
    dampen_scale(arm, ("Body", "Top"), 0.5)
    remove_body(body)

@variante("sturm_schleimling", "schleimling")
def gewittertropfen(arm, body):
    """Wolkenwirbel, leicht: Gewittertropfen – kleiner, glänzender Regentropfen (Kommentar 25.11.: keine kleine Wolke):
    tiefblau, oben spitz, gelb leuchtende, wütende Augen, kleines Maul, ein Blitz als Haarlocke an der Spitze und zwei
    Funken, die um ihn springen. Eigene Figur auf dem Skelett des Schleimlings (hüpft wie er)."""
    M = storm_mats()
    water = look("Regenwasser", (1, 1, 1), rough=0.06, emit=(0.15, 0.3, 0.7), strength=0.35)
    prof = [(0.7, 0.0), (0.64, 0.05), (0.55, 0.11), (0.45, 0.18), (0.35, 0.24), (0.25, 0.27), (0.16, 0.265), (0.08, 0.22), (0.025, 0.13), (0.0, 0.0)]
    g = lathe("Tropfen", prof, segs=48)
    H_, W_ = 512, 512
    vv = np.linspace(0, 1, H_)[:, None] * np.ones((1, W_))
    col = gradient((0.12, 0.3, 0.78), (0.45, 0.72, 1.0), (vv - 0.15) / 0.75)
    arr = np.ones((H_, W_, 4), np.float32); arr[..., :3] = np.clip(col, 0, 1)
    lathe_texture(water, arr)
    give(g, water)
    bpy.context.view_layer.update()
    skin_to(g, arm, lambda c: {"Top": smooth01((c.z - 0.1) / 0.3), "Body": 1 - smooth01((c.z - 0.1) / 0.3)})
    face = []
    p, n = surface(g, (0, -2.0, 0.24), (0, 1, 0))
    for s_ in (-1, 1):
        e = sphere("Auge%d" % s_, (0, 0, 0), 0.04, (1.2, 0.45, 0.8)); e.location = p + Vector((s_ * 0.07, 0.01, 0.035)); e.rotation_euler = (0, math.radians(-s_ * 18), 0)
        face.append(give(e, M["eye"]))
        face.append(give(sphere("Pupille%d" % s_, tuple(p + Vector((s_ * 0.065, -0.006, 0.03))), 0.013), M["dark"]))
        face.append(give(tube("Braue%d" % s_, [tuple(p + Vector((s_ * 0.12, 0.0, 0.09))), tuple(p + Vector((s_ * 0.07, -0.012, 0.085))), tuple(p + Vector((s_ * 0.02, -0.012, 0.065)))],
                              [0.011, 0.014, 0.01]), M["dark"]))
    face.append(give(tube("Maul", [tuple(p + Vector((-0.035, -0.004, -0.04))), tuple(p + Vector((0.0, -0.008, -0.05))), tuple(p + Vector((0.035, -0.004, -0.04)))], [0.008, 0.01, 0.008], segs=8), M["dark"]))
    face.append(bolt("Blitzlocke", (0.0, 0.0, 0.6), (0.06, 0.06, 0.84), 0.024, M, n=3, jitter=0.35, seed=345))
    for i, (a, z) in enumerate(((0.3, 0.32), (2.6, 0.2))):
        q, m = surface(g, (2.0 * math.cos(a), 2.0 * math.sin(a), z), (-math.cos(a), -math.sin(a), 0))
        if q is not None:
            face.append(bolt("Funke%d" % i, q - m * 0.015, q + m * 0.09 + Vector((0, 0, 0.05)), 0.013, M, n=3, jitter=0.35, seed=346 + i))
    attach(join_parts(face, "Tropfen_Gesicht"), arm, "Top")
    dampen_scale(arm, ("Body", "Top"), 0.55)
    remove_body(body)

@variante("sturm_tentakler", "tentakler")
def sturmfluegler(arm, body):
    """Wolkenwirbel, mittel: Sturmflügler – Flugwesen mit blaugrauer Sturmhaut und gelb leuchtenden Blitzadern,
    Flügeln aus Gewitterwolke mit Blitzen, Wolkenbäuschen an der Flügelkante, Blitzhörnern, gelb leuchtenden Augen und
    einem Blitz als Schwanz"""
    M = storm_mats()
    T = texels(body)
    px, P = T["px"], T["P"]
    red = hue_mask(px, 0.02, 0.06, 0.35)
    teal = hue_mask(px, 0.49, 0.08, 0.3)
    hh, s, v = hsv(px)
    beige = np.clip((0.6 - s) / 0.1, 0, 1) * np.clip((v - 0.5) / 0.1, 0, 1) * hue_mask(px, 0.11, 0.07, 0.08)
    white = np.clip((0.15 - s) / 0.06, 0, 1) * np.clip((v - 0.8) / 0.06, 0, 1)
    storm_skin(T, red, 351)
    paint(T, teal, gradient((0.3, 0.34, 0.46), (0.78, 0.82, 0.92), fbm3(P, 4.0, 353, 3) * 1.5 - 0.25), keep_shading=0.3)
    veins = ridges(P, 5.0, 354, 0.02) ** 2
    paint(T, teal * veins, (1.0, 0.95, 0.5), keep_shading=0.0)
    glow(T, teal * veins, (1.0, 0.85, 0.25))
    paint(T, beige, (1.0, 0.92, 0.45), keep_shading=0.3)
    glow(T, beige * 0.8, (1.0, 0.85, 0.25))
    paint(T, white, (1.0, 0.97, 0.6), keep_shading=0.2)
    glow(T, white, (1.0, 0.85, 0.3))
    commit(T, strength=2.0)
    for side, chain in ((1, ("Bone_031", "Bone_030", "Bone_029")), (-1, ("Bone_026", "Bone_025", "Bone_024"))):
        for k, (bone, t) in enumerate(((chain[1], 0.5), (chain[2], 0.35))):
            b0 = bone_pt(arm, bone, t)
            attach(join_parts(cloud_parts("Fluegelwolke%d_%d" % (side, k), b0 + Vector((0, 0.02, 0.04)), 0.12, 360 + k + side, M, n=5, flat=0.8, dark_below=False),
                              "Fluegelwolke%d_%d" % (side, k)), arm, bone)
    q, m = surface(body, (0.0, 0.15, -1.0), (0, 0, 1))
    if q is not None:
        attach(bolt("Schwanzblitz", q + Vector((0, 0, 0.03)), q + Vector((0.05, 0.35, -0.3)), 0.04, M, n=5, jitter=0.25, seed=365), arm, "Bone_001")

@variante("sturm_brecher", "brecher")
def donnerbrecher(arm, body):
    """Wolkenwirbel, stark: Donnerbrecher – massiger Schläger mit blaugrauer Sturmhaut und Blitzadern, dunkelblauer
    Rüstung mit Kupfer, Wolkenkragen, Gewitterwolken auf den Schultern, Blitzkamm auf dem Kopf, Blitzen an den
    Unterarmen und gelb leuchtenden Augen"""
    M = storm_mats()
    T = texels(body); R = regions(T, arm)
    storm_skin(T, R["skin"], 371)
    paint(T, R["purple"] * (1 - R["head"]), (0.1, 0.13, 0.28), keep_shading=0.6)
    paint(T, R["purple"] * R["head"], (0.25, 0.34, 0.55), keep_shading=0.5)
    paint(T, R["grey"], (0.85, 0.5, 0.3), keep_shading=0.5)
    collar = np.maximum(R["white"] * (1 - R["head"]), R["collar"])
    paint(T, collar, (0.93, 0.95, 1.0), keep_shading=0.4)
    eyes = R["white"] * R["head"]
    paint(T, eyes, (1.0, 0.97, 0.6), keep_shading=0.2)
    glow(T, eyes, (1.0, 0.85, 0.3))
    commit(T, strength=2.0)
    for s_, side in ((1, "Left"), (-1, "Right")):
        a0 = bone_pt(arm, "mixamorig:%sArm" % side)
        p, n = surface(body, (a0.x, a0.y, a0.z + 0.15), (0, 0, -1))
        c = (p if p is not None else a0) + Vector((s_ * 0.02, 0, 0.05))
        parts = cloud_parts("Schulterwolke" + side, c, 0.15, 380 + s_, M, n=7, flat=0.75)
        parts.append(bolt("Schulterblitz" + side, c + Vector((s_ * 0.05, 0, -0.05)), c + Vector((s_ * 0.12, -0.05, -0.3)), 0.022, M, n=4, seed=382 + s_))
        attach(join_parts(parts, "Schulterwolke" + side), arm, "mixamorig:%sArm" % side)
        f0, f1 = bone_pt(arm, "mixamorig:%sForeArm" % side, 0.2), bone_pt(arm, "mixamorig:%sForeArm" % side, 0.8)
        attach(bolt("Armblitz" + side, f0 + Vector((s_ * 0.08, 0.05, 0.05)), f1 + Vector((s_ * 0.1, 0.05, 0.08)), 0.02, M, n=5, jitter=0.15, seed=384 + s_), arm, "mixamorig:%sForeArm" % side)
    crest = []
    for k, (y, L) in enumerate(((-0.06, 0.17), (0.03, 0.22), (0.12, 0.16))):
        q, m = head_top(body, 0.0, y)
        if q is not None:
            crest.append(bolt("Kammblitz%d" % k, q - m * 0.02, q + Vector((0.0, y * 1.5 + 0.04, L)), 0.03, M, n=3, jitter=0.25, seed=390 + k))
    attach(join_parts(crest, "Blitzkamm"), arm, "mixamorig:Head")

# Blitzfront (Welt 18): gleiche Sturmwelt, aber elektrisch: Kupfer, Funken, Blitzableiter

def antenna(name, base, L, M, ball=0.04):
    b = Vector(base)
    pts = [b, b + Vector((0, 0.01, L * 0.5)), b + Vector((0, 0.02, L))]
    parts = [give(tube(name + "Stab", [tuple(p) for p in pts], [0.012, 0.01, 0.009], segs=8), M["copper"])]
    for k in range(3):
        parts.append(give(torus(name + "Ring%d" % k, tuple(b + Vector((0, 0.01, L * (0.3 + 0.2 * k)))), 0.022, 0.006, rot=(0, 0, 0), segs=16), M["copper"]))
    parts.append(give(sphere(name + "Kugel", tuple(pts[-1] + Vector((0, 0, ball * 0.8))), ball), M["bolt"]))
    return parts

def electric_body(T, R, seed):
    storm_skin(T, R["skin"], seed, base=(0.28, 0.48, 0.9))
    paint(T, R["purple"] * (1 - R["head"]), (0.08, 0.1, 0.24), keep_shading=0.6)
    spots = R["purple"] * R["head"]
    paint(T, spots, (1.0, 0.92, 0.4), keep_shading=0.3)
    glow(T, spots, (1.0, 0.85, 0.25))
    paint(T, R["grey"], (0.85, 0.5, 0.3), keep_shading=0.5)
    eyes = R["white"] * R["head"]
    paint(T, eyes, (1.0, 0.97, 0.6), keep_shading=0.2)
    glow(T, eyes, (1.0, 0.85, 0.3))

@variante("blitz_krabbler", "krabbler")
def funkenwicht(arm, body):
    """Blitzfront, leicht: Funkenwicht – flinker Kobold mit elektrisch blauer Haut und gelb leuchtenden Blitzadern,
    leuchtenden Funkenflecken am Kopf, gelb leuchtenden Augen und einer Kupferantenne mit Funkenkugel"""
    M = storm_mats()
    T = texels(body); R = regions(T, arm)
    electric_body(T, R, 401)
    commit(T, strength=2.0)
    q, m = head_top(body, 0.05, 0.0)
    if q is not None:
        attach(join_parts(antenna("Antenne", q - m * 0.02, 0.22, M, ball=0.045), "Antenne"), arm, "mixamorig:Head")
    sp = []
    for s_ in (-1, 1):
        a0 = bone_pt(arm, "mixamorig:%sArm" % s_ if False else "mixamorig:%sArm" % ("Left" if s_ > 0 else "Right"))
        sp.append(bolt("Schulterfunke%d" % s_, a0 + Vector((s_ * 0.02, 0, 0.08)), a0 + Vector((s_ * 0.1, 0.02, 0.2)), 0.016, M, n=3, jitter=0.3, seed=405 + s_))
    attach(join_parts(sp, "Funken"), arm, "mixamorig:Spine2")

@variante("blitz_zombie", "zombie")
def blitzlaeufer(arm, body):
    """Blitzfront, mittel: Blitzläufer – hagerer Läufer mit elektrisch blauer Haut und Blitzadern, Blitzhörnern auf dem
    Kopf, Wolkenkragen und einem Blitzableiter aus Kupfer auf dem Rücken, an dessen Spitze eine Funkenkugel leuchtet"""
    M = storm_mats()
    T = texels(body); R = regions(T, arm)
    electric_body(T, R, 411)
    commit(T, strength=2.0)
    horns = []
    for s_ in (-1, 1):
        q, m = head_top(body, s_ * 0.09, 0.0)
        if q is not None:
            horns.append(bolt("Blitzhorn%d" % s_, q - m * 0.02, q + Vector((s_ * 0.1, 0.03, 0.2)), 0.028, M, n=3, jitter=0.3, seed=415 + s_))
    attach(join_parts(horns, "Blitzhoerner"), arm, "mixamorig:Head")
    p, n = back_pt(body, 0.0, bone_pt(arm, "mixamorig:Spine2").z)
    if p is not None:
        attach(join_parts(antenna("Ableiter", p + Vector((0, 0.02, -0.05)), 0.55, M, ball=0.05), "Ableiter"), arm, "mixamorig:Spine2")
    nk = bone_pt(arm, "mixamorig:Neck", 0.0)
    attach(join_parts(cloud_parts("Wolkenkragen", nk + Vector((0, 0.02, -0.02)), 0.13, 419, M, n=8, flat=0.6, dark_below=False), "Wolkenkragen"), arm, "mixamorig:Spine2")

@variante("blitz_panzerkaefer", "panzerkaefer")
def donnerpanzer(arm, body):
    """Blitzfront, stark: Donnerpanzer – schwerer Käfer mit Panzer aus dunkler Gewitterwolke und gelb leuchtenden
    Blitznähten, einer Kupferspule mit Funkenkugel oben, Blitzableitern rundum, aus denen Blitze springen,
    Wolkenbäuschen am Rand und elektrisch blauem Körper"""
    M = storm_mats()
    T = texels(body)
    px, P, N = T["px"], T["P"], T["N"]
    teal = hue_mask(px, 0.49, 0.08, 0.3)
    red = np.maximum(hue_mask(px, 0.02, 0.06, 0.35), hue_mask(px, 0.97, 0.05, 0.3))
    hh, s, v = hsv(px)
    beige = np.clip((0.6 - s) / 0.1, 0, 1) * np.clip((v - 0.5) / 0.1, 0, 1) * hue_mask(px, 0.11, 0.07, 0.08)
    edge, cid = worley3(P, 8.0, 421)
    paint(T, teal, gradient((0.25, 0.28, 0.4), (0.62, 0.67, 0.8), np.clip(N[..., 2], 0, 1) * 0.8 + cid * 0.3), keep_shading=0.4)
    line = np.clip(1 - edge / 0.004, 0, 1)
    paint(T, teal * line, (1.0, 0.95, 0.5), keep_shading=0.0)
    glow(T, teal * line, (1.0, 0.85, 0.25))
    storm_skin(T, red, 423, base=(0.28, 0.48, 0.9))
    paint(T, beige, (0.85, 0.5, 0.3), keep_shading=0.5)
    commit(T, strength=2.0)
    parts = []
    p, n = surface(body, (0.0, 0.05, 2.0), (0, 0, -1))
    top = p if p is not None else Vector((0, 0.05, 0.4))
    coil = [give(tube("Spule", [tuple(top + Vector((0, 0, -0.02))), tuple(top + Vector((0, 0, 0.16)))], [0.045, 0.04], segs=14), M["copper"])]
    for k in range(5):
        coil.append(give(torus("Spulenring%d" % k, tuple(top + Vector((0, 0, 0.02 + 0.03 * k))), 0.05, 0.009, rot=(0, 0, 0), segs=20), M["copper"]))
    ball = top + Vector((0, 0, 0.21))
    coil.append(give(sphere("Funkenkugel", tuple(ball), 0.055), M["bolt"]))
    parts += coil
    rim = ring_hits(body, (0, 0.03, 0.2), 4, 0.35, phase=math.pi / 4)
    for k, (q, m, a) in enumerate(rim):
        tip = q + m * 0.02 + Vector((0, 0, 0.12))
        parts.append(give(tube("Ableiter%d" % k, [tuple(q - m * 0.01), tuple(tip)], [0.012, 0.009], segs=8), M["copper"]))
        parts.append(give(sphere("Ableiterkugel%d" % k, tuple(tip + Vector((0, 0, 0.015))), 0.022), M["bolt"]))
        parts.append(bolt("Funke%d" % k, ball, tip + Vector((0, 0, 0.02)), 0.012, M, n=4, jitter=0.15, seed=430 + k))
    cl = ring_hits(body, (0, 0.03, 0.18), 6, 0.1, phase=0.5, skip=lambda a: math.sin(a) < -0.6)
    for k, (q, m, a) in enumerate(cl):
        parts += cloud_parts("Randwolke%d" % k, q + m * 0.02, 0.07, 440 + k, M, n=4, flat=0.7, dark_below=False)
    attach(join_parts(parts, "Donnerpanzer_Aufbau"), arm, "Body")

@variante("donner_riese", "koloss")
def donnerriese(arm, body):
    """Blitzfront (Welt 18), Boss: Donnerriese – riesiger Sturmkrieger mit elektrisch blauer Haut und gelb leuchtenden
    Blitzadern, dunkelblauer Rüstung mit Kupfer, Wolkenmantel auf den Schultern, großen Blitzhörnern, einer Krone aus
    Gewitterwolken, zwei Blitzableitern auf dem Rücken und einer leuchtenden Sturmkugel in der Brust"""
    M = storm_mats()
    skin = look("Sturmhaut", (0.3, 0.48, 0.88), rough=0.5)
    T = texels(body); R = regions(T, arm)
    electric_body(T, R, 451)
    collar = np.maximum(R["white"] * (1 - R["head"]), R["collar"])
    paint(T, collar, (0.93, 0.95, 1.0), keep_shading=0.4)
    commit(T, strength=2.0)
    koloss_arms(arm, body, skin, M["dark"], M["copper"], cuff_style="stulpe", fingers=4)
    hc = bone_pt(arm, "mixamorig:Head", 0.45)
    head = []
    for s_ in (-1, 1):
        q, m = head_top(body, s_ * 0.17, 0.08)
        if q is not None:
            head.append(bolt("Blitzhorn%d" % s_, q - m * 0.03, q + Vector((s_ * 0.22, 0.06, 0.42)), 0.06, M, n=4, jitter=0.25, seed=455 + s_))
    q, m = head_top(body, 0.0, 0.1)
    if q is not None:
        for k in range(6):
            a = k * 2 * math.pi / 6 + 0.3
            c = q + Vector((math.cos(a) * 0.28, 0.05 + math.sin(a) * 0.22, 0.04))
            head += cloud_parts("Kronenwolke%d" % k, c, 0.09, 460 + k, M, n=4, flat=0.7)
    attach(join_parts(head, "Donner_Kopf"), arm, "mixamorig:Head")
    for s_, side in ((1, "Left"), (-1, "Right")):
        a0 = bone_pt(arm, "mixamorig:%sArm" % side)
        p, n = surface(body, (a0.x, a0.y, a0.z + 0.2), (0, 0, -1))
        c = (p if p is not None else a0) + Vector((s_ * 0.03, 0.02, 0.06))
        parts = cloud_parts("Wolkenmantel" + side, c, 0.27, 470 + s_, M, n=9, flat=0.7)
        parts.append(bolt("Mantelblitz" + side, c + Vector((s_ * 0.12, -0.05, -0.08)), c + Vector((s_ * 0.22, -0.12, -0.55)), 0.035, M, n=5, seed=472 + s_))
        attach(join_parts(parts, "Wolkenmantel" + side), arm, "mixamorig:%sArm" % side)
    sp = bone_pt(arm, "mixamorig:Spine2")
    back = []
    for s_ in (-1, 1):
        p, n = back_pt(body, s_ * 0.16, sp.z + 0.05)
        if p is not None:
            back += antenna("Ableiter%d" % s_, p + Vector((0, 0.02, -0.08)), 0.75, M, ball=0.07)
    q, m = front_pt(body, 0.0, bone_pt(arm, "mixamorig:Spine1", 0.6).z)
    if q is not None:
        back.append(give(sphere("Sturmkugel", tuple(q + m * 0.02), 0.085), M["bolt"]))
        t = torus("Sturmring", (0, 0, 0), 0.1, 0.018, segs=28); t.matrix_world = Matrix.Translation(q + m * 0.02) @ m.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        back.append(give(t, M["copper"]))
    attach(join_parts(back, "Donner_Ruecken"), arm, "mixamorig:Spine2")

# ---------------------------------------------------------------- Gemeinsame Bausteine für Planet 10 bis 15

def block_rot(name, c, semi, mat, rot, seed=3):
    """Block mit Drehung um seine eigene Mitte (block_at legt die Lage in die Punkte, eine Drehung danach würde ihn
    um den Weltursprung schwenken und versetzen)"""
    o = block_at(name, (0, 0, 0), semi, mat, seed, True, 0)
    o.location = Vector(c); o.rotation_euler = rot
    return o

def lathe_uv_grid(H_=1024, W_=1024):
    vv = np.linspace(0, 1, H_)[:, None] * np.ones((1, W_))
    uu = np.ones((H_, 1)) * np.linspace(0, 1, W_)[None, :]
    return uu, vv

def feather_tex(base, tip, rows=14, cols=18, seed=1, H_=1024, W_=1024):
    """Federkleid für Drehkörper: Reihen schuppiger Federn (Abwicklung: u rundum, v unten→oben)"""
    uu, vv = lathe_uv_grid(H_, W_)
    r = vv * rows
    row = np.floor(r); loc = r - row
    sc = 0.5 + 0.5 * np.abs(np.sin(math.pi * (uu * cols + row * 0.5)))
    edge = np.clip((loc - sc * 0.35) / 0.08, 0, 1)
    shade = 0.75 + 0.25 * edge
    col = np.asarray(base) * (1 - loc[..., None] * 0.35) + np.asarray(tip) * (loc[..., None] * 0.35)
    col = col * shade[..., None] * (0.92 + (fbm(H_, W_, 60, seed, 2) - 0.5)[..., None] * 0.15)
    arr = np.ones((H_, W_, 4), np.float32); arr[..., :3] = np.clip(col, 0, 1)
    return arr

def metal_tex(base, seed=1, panels=(8, 6), rust=0.3, stripes=None, H_=1024, W_=1024):
    """Blech für Drehkörper: Platten mit Fugen, Nieten an den Ecken, Rostflecken; stripes=(v0, v1): Warnstreifen-Band"""
    uu, vv = lathe_uv_grid(H_, W_)
    fu = (uu * panels[0]) % 1.0; fv = (vv * panels[1]) % 1.0
    seam = np.clip(1 - np.minimum(np.minimum(fu, 1 - fu), np.minimum(fv, 1 - fv)) / 0.012, 0, 1)
    riv = np.clip(1 - np.hypot(np.minimum(fu, 1 - fu) - 0.05, np.minimum(fv, 1 - fv) - 0.08) / 0.018, 0, 1)
    col = np.ones((H_, W_, 3)) * np.asarray(base) * (0.9 + 0.15 * fbm(H_, W_, 8, seed, 3))[..., None]
    rk = np.clip((fbm(H_, W_, 6, seed + 1, 4) - (1 - rust)) / 0.08, 0, 1)
    col = col * (1 - rk[..., None]) + np.asarray((0.55, 0.3, 0.14)) * rk[..., None]
    if stripes is not None:
        band = (vv > stripes[0]) & (vv < stripes[1])
        st = ((uu * 24 + vv * 6) % 1.0) < 0.5
        col = np.where((band & st)[..., None], np.asarray((0.95, 0.75, 0.1)), np.where(band[..., None], np.asarray((0.08, 0.08, 0.08)), col))
    col = col * (1 - seam[..., None] * 0.55)
    col = col * (1 - riv[..., None] * 0.2) + riv[..., None] * 0.25
    arr = np.ones((H_, W_, 4), np.float32); arr[..., :3] = np.clip(col, 0, 1)
    return arr

def metal_paint(T, mask, seed, base=(0.55, 0.57, 0.6), rust=0.35, freq=7.0):
    """Blech im Raum: Platten mit dunklen Fugen, Nietpunkte, Rostflecken"""
    P = T["P"]
    edge, cid = worley3(P, freq, seed)
    paint(T, mask, np.asarray(base, np.float32) * (0.85 + 0.25 * cid[..., None]), keep_shading=0.5)
    rk = np.clip((fbm3(P, 6.0, seed + 1, 4) - (1 - rust)) / 0.08, 0, 1)
    paint(T, mask * rk, (0.58, 0.3, 0.13), keep_shading=0.5)
    paint(T, mask * np.clip(1 - edge / 0.003, 0, 1), (0.16, 0.16, 0.18), keep_shading=0.0)
    riv = np.clip((noise3(P, 55.0, seed + 2) - 0.86) / 0.04, 0, 1) * np.clip((0.02 - edge) / 0.01, 0, 1)
    paint(T, mask * riv, (0.8, 0.8, 0.82), keep_shading=0.2)

def hazard_paint(T, mask, freq=9.0):
    P = T["P"]
    st = (((P[..., 0] + P[..., 2]) * freq) % 1.0) < 0.5
    paint(T, mask * st, (0.95, 0.75, 0.1), keep_shading=0.5)
    paint(T, mask * (~st), (0.1, 0.1, 0.1), keep_shading=0.5)

def robo_mats():
    return {
        "steel": look("Stahl", (0.6, 0.62, 0.66), rough=0.35, metal=0.8),
        "steel_dark": look("StahlDunkel", (0.28, 0.29, 0.32), rough=0.4, metal=0.7),
        "rust": look("Rost", (0.55, 0.3, 0.14), rough=0.75, metal=0.2),
        "led": look("LED", (1.0, 0.2, 0.12), rough=0.2, emit=(1.0, 0.12, 0.05), strength=6.0),
        "hazard": look("Warngelb", (0.95, 0.75, 0.1), rough=0.5),
        "rubber": look("Gummi", (0.07, 0.07, 0.08), rough=0.85),
        "smoke": look("Rauch", (0.45, 0.45, 0.48), rough=0.9),
    }

def exhaust(name, base, d, L, r, M, smoke=True):
    b = Vector(base); d = Vector(d).normalized()
    pts = [b, b + d * L * 0.5 + Vector((0, 0, L * 0.15)), b + d * L * 0.7 + Vector((0, 0, L * 0.5))]
    parts = [give(tube(name, [tuple(p) for p in pts], [r, r, r * 1.15], segs=12), M["steel_dark"])]
    parts.append(give(torus(name + "Rand", tuple(pts[-1]), r * 1.15, r * 0.25, rot=(0, 0, 0), segs=16), M["steel"]))
    if smoke:
        for k in range(3):
            parts.append(give(sphere(name + "Rauch%d" % k, tuple(pts[-1] + Vector((0.02 * k, 0.01 * k, r * 2 + k * r * 2.2))), r * (1.3 + 0.5 * k)), M["smoke"]))
    return parts

def gear(name, c, n, r, M, teeth=10):
    """Zahnrad: flache Scheibe mit Zähnen und Nabe, Achse in Richtung n"""
    parts = [give(lathe(name, [(r * 0.12, 0.0), (r * 0.12, r * 0.85), (-r * 0.12, r * 0.85), (-r * 0.12, 0.0)], segs=32), M["steel"])]
    for k in range(teeth):
        a = k * 2 * math.pi / teeth
        parts.append(give(block_at(name + "Zahn%d" % k, (math.cos(a) * r * 0.95, math.sin(a) * r * 0.95, 0), (r * 0.14, r * 0.14, r * 0.11), M["steel"], k, True, 0), M["steel"]))
    parts.append(give(sphere(name + "Nabe", (0, 0, 0), r * 0.25, (1, 1, 0.8)), M["steel_dark"]))
    o = join_parts(parts, name)
    o.matrix_world = Matrix.Translation(Vector(c)) @ Vector(n).normalized().to_track_quat('Z', 'Y').to_matrix().to_4x4()
    return o

def rotor(name, c, r, M, blades=3):
    parts = [give(sphere(name + "Nabe", tuple(c), r * 0.18), M["steel_dark"])]
    for k in range(blades):
        a = k * 2 * math.pi / blades
        tip = Vector(c) + Vector((math.cos(a) * r, math.sin(a) * r, 0.0))
        parts.append(block_rot(name + "Blatt%d" % k, (Vector(c) + tip) / 2, (r * 0.5, r * 0.09, r * 0.03), M["steel"], (0.25, 0, a), seed=k))
    return parts

def robo_body(T, R, seed, rust=0.4, suit=(0.36, 0.2, 0.12), hazard=False):
    metal_paint(T, R["skin"], seed, rust=rust)
    if hazard:
        hazard_paint(T, R["purple"] * (1 - R["head"]))
    else:
        paint(T, R["purple"] * (1 - R["head"]), suit, keep_shading=0.6)
    paint(T, R["purple"] * R["head"], (0.3, 0.31, 0.34), keep_shading=0.5)
    paint(T, R["grey"], (0.95, 0.75, 0.1), keep_shading=0.5)
    eyes = R["white"] * R["head"]
    paint(T, eyes, (1.0, 0.35, 0.25), keep_shading=0.2)
    glow(T, eyes, (1.0, 0.12, 0.05))

# ---------------------------------------------------------------- Schrottwelt (Welt 19 und 20): Rost, Stahl, Warnstreifen, rote LEDs

@variante("schrott_krabbler", "krabbler")
def schrottwicht(arm, body):
    """Schrotthalden, leicht: Schrottwicht – kleiner Kobold aus verbeultem, rostigem Blech mit Nieten, rot leuchtenden
    LED-Augen, Bolzen statt Flecken am Kopf, einem Auspuffrohr auf dem Rücken und einem Zahnrad an der Schulter"""
    M = robo_mats()
    T = texels(body); R = regions(T, arm)
    robo_body(T, R, 501, rust=0.5)
    commit(T, strength=2.0)
    p, n = back_pt(body, 0.0, bone_pt(arm, "mixamorig:Spine1").z)
    if p is not None:
        attach(join_parts(exhaust("Auspuff", p - n * 0.01, (0.0, 1.0, 0.2), 0.22, 0.025, M), "Auspuff"), arm, "mixamorig:Spine2")
    a0 = bone_pt(arm, "mixamorig:LeftArm")
    attach(gear("Zahnrad", a0 + Vector((0.04, 0.0, 0.05)), (1, 0, 0.3), 0.07, M), arm, "mixamorig:LeftArm")

@variante("schrott_zombie", "zombie")
def rostschlurfer(arm, body):
    """Schrotthalden, mittel: Rostschlurfer – hagerer Blechläufer mit viel Rost, aufgenieteten Flickblechen, rot
    leuchtenden Augen und zwei qualmenden Auspuffrohren auf dem Rücken"""
    M = robo_mats()
    T = texels(body); R = regions(T, arm)
    robo_body(T, R, 511, rust=0.6)
    commit(T, strength=2.0)
    hc = bone_pt(arm, "mixamorig:Head", 0.4)
    patch_on("BlechKopf", body, hc + Vector((-1.2, -0.3, 0.5)), (1.0, 0.25, -0.42), (0.1, 0.09), M["steel"], M["steel_dark"], arm, "mixamorig:Head", spin=0.4, rivets=True)
    sp = bone_pt(arm, "mixamorig:Spine1")
    patch_on("BlechBrust", body, (sp.x + 0.05, sp.y - 1.5, sp.z + 0.05), (0, 1, 0), (0.11, 0.1), M["rust"], M["steel_dark"], arm, "mixamorig:Spine1", spin=-0.3, rivets=True)
    parts = []
    for s_ in (-1, 1):
        p, n = back_pt(body, s_ * 0.07, bone_pt(arm, "mixamorig:Spine1", 0.8).z)
        if p is not None:
            parts += exhaust("Auspuff%d" % s_, p - n * 0.01, (s_ * 0.3, 1.0, 0.1), 0.3, 0.028, M)
    attach(join_parts(parts, "Auspuffe"), arm, "mixamorig:Spine2")

@variante("schrott_brecher", "brecher")
def schrottbrecher(arm, body):
    """Schrotthalden, stark: Schrottbrecher – massiger Schläger aus rostigem Stahl mit Warnstreifen-Rüstung, einem
    Reifen auf der Schulter, Blechschienen an den Unterarmen, rot leuchtenden Augen und Auspuffrohren"""
    M = robo_mats()
    T = texels(body); R = regions(T, arm)
    robo_body(T, R, 521, rust=0.45, hazard=True)
    collar = np.maximum(R["white"] * (1 - R["head"]), R["collar"])
    paint(T, collar, (0.1, 0.1, 0.11), keep_shading=0.5)
    commit(T, strength=2.0)
    a0 = bone_pt(arm, "mixamorig:LeftArm")
    tire = torus("Reifen", tuple(a0 + Vector((0.02, 0.0, 0.1))), 0.14, 0.055, rot=(0, 70, 0), segs=36)
    attach(give(tire, M["rubber"]), arm, "mixamorig:LeftArm")
    for s_, side in ((1, "Left"), (-1, "Right")):
        f0, f1 = bone_pt(arm, "mixamorig:%sForeArm" % side, 0.2), bone_pt(arm, "mixamorig:%sForeArm" % side, 0.85)
        attach(chunk_between("Schiene" + side, f0 + Vector((s_ * 0.05, 0.03, 0.02)), f1 + Vector((s_ * 0.05, 0.03, 0.02)), 0.065, M["steel"], 50 + s_, True, 1), arm, "mixamorig:%sForeArm" % side)
    parts = []
    for s_ in (-1, 1):
        p, n = back_pt(body, s_ * 0.14, bone_pt(arm, "mixamorig:Spine2").z)
        if p is not None:
            parts += exhaust("Auspuff%d" % s_, p - n * 0.01, (s_ * 0.2, 1.0, 0.2), 0.36, 0.035, M)
    attach(join_parts(parts, "Auspuffe"), arm, "mixamorig:Spine2")

@variante("schrott_koloss_alt", "koloss")          # alter Schrottkoloss; neu: tools/monster/schrottkoloss.py
def schrottkoloss(arm, body):
    """Schrotthalden (Welt 19), Boss: Schrottkoloss – riesiger Golem aus rostigen Stahlblöcken mit Warnstreifen,
    Gelenken aus glühenden Lampen, einem Kopf mit rot leuchtenden Augen und Stahlzähnen, einer Öltonne als Brust,
    Reifen auf der Schulter und qualmenden Schornsteinen auf dem Rücken"""
    M = robo_mats()
    lamp = look("Warnlampe", (1.0, 0.55, 0.1), rough=0.3, emit=(1.0, 0.45, 0.05), strength=3.0)
    g = golem_body(arm, body, M["steel"], M["rust"], lamp, flat=True, subdiv=1, fist_m=M["steel_dark"], nail_m=M["hazard"], legs=1.35)
    hc = g["head"] + Vector((0, -0.08, 0.24))
    skull = block_at("Kopf", hc, (0.25, 0.23, 0.22), M["steel"], 31, True, 1)
    jaw = block_at("Kiefer", hc + Vector((0, -0.07, -0.15)), (0.22, 0.17, 0.1), M["rust"], 32, True, 1)
    socket = look("Augenhoehle", (0.05, 0.05, 0.06), rough=0.6, emit=(0.4, 0.04, 0.02), strength=0.6)
    core = look("LEDkern", (1.0, 0.9, 0.8), rough=0.2, emit=(1.0, 0.8, 0.6), strength=8.0)
    mouth_in = look("Maulinneres", (0.12, 0.05, 0.04), rough=0.6, emit=(0.6, 0.1, 0.03), strength=0.8)
    pm0, nm0 = surface(jaw, (0.0, -2.0, hc.z - 0.135), (0, 1, 0))
    face = golem_face(skull, jaw, hc, {"socket": socket, "eye": M["led"], "core": core, "mouth": mouth_in, "tooth": M["steel"],
                                      "brow": M["steel_dark"], "crack": M["rust"], "throat": lamp})
    face = realistic_mouth(face, pm0, "Stahlgebiss", mouth_in, lamp, random.Random(43), enamel_col=(0.72, 0.74, 0.78), gum_col=(0.28, 0.29, 0.32), metal=0.8)
    head = [skull, jaw] + face
    head.append(gear("Kopfzahnrad", hc + Vector((0.2, 0.05, 0.16)), (1, 0.2, 0.5), 0.09, M))
    attach(join_parts(head, "Schrott_Kopf"), arm, "mixamorig:Head")
    ch = g["chest"] + Vector((0, -0.25, 0.0))
    barrel = [give(lathe("Oeltonne", [(0.17, 0.0), (0.17, 0.14), (0.1, 0.15), (-0.1, 0.15), (-0.17, 0.14), (-0.17, 0.0)], segs=28), M["hazard"])]
    barrel[0].rotation_euler = (math.radians(90), 0, 0); barrel[0].location = ch
    for k, z in enumerate((-0.09, 0.0, 0.09)):
        barrel.append(give(torus("Tonnenring%d" % k, tuple(ch + Vector((0, 0, z))), 0.155, 0.012, rot=(0, 0, 0), segs=28), M["rubber"]))
    attach(join_parts(barrel, "Oeltonne"), arm, "mixamorig:Spine2")
    a0 = bone_pt(arm, "mixamorig:LeftArm")
    attach(give(torus("Reifen", tuple(a0 + Vector((0.08, 0.0, 0.26))), 0.22, 0.08, rot=(0, 60, 0), segs=40), M["rubber"]), arm, "mixamorig:LeftArm")
    back = []
    for s_ in (-1, 1):
        b0 = g["chest"] + Vector((s_ * 0.2, 0.38, 0.1))
        back.append(give(tube("Schornstein%d" % s_, [tuple(b0), tuple(b0 + Vector((0, 0.05, 0.55)))], [0.07, 0.065], segs=16), M["steel_dark"]))
        for k in range(3):
            back.append(give(sphere("Qualm%d_%d" % (s_, k), tuple(b0 + Vector((0.03 * k * s_, 0.06 + 0.02 * k, 0.65 + 0.14 * k))), 0.08 + 0.04 * k), M["smoke"]))
    attach(join_parts(back, "Schornsteine"), arm, "mixamorig:Spine2")

def dome_robot(name, prof, M, base_col, eye_r, H_=1024):
    """Kuppel-Roboter (Drehkörper aus Blech mit Warnstreifen-Band) für Schleim-Skelette"""
    g = lathe(name, prof, segs=48)
    mat = look(name + "Blech", (1, 1, 1), rough=0.35, metal=0.6)
    lathe_texture(mat, metal_tex(base_col, seed=7, panels=(10, 5), rust=0.2, stripes=(0.12, 0.2)))
    give(g, mat)
    return g

@variante("robo_schleimling", "schleimling")
def federbot(arm, body):
    """Robo-Fabrik, leicht: Federbot – kleiner Hüpfroboter (Regel 25.11.: kein kleiner Boss): runder Blechkopf mit
    einem großen rot leuchtenden Auge und Visierblende, seitlichen Schraubenköpfen, auf einer Sprungfeder mit
    Warnstreifen-Fuß. Die Feder staucht beim Hüpfen. Eigene Figur auf dem Skelett des Schleimlings."""
    M = robo_mats()
    pts, radii = [], []
    for i in range(60):
        t = i / 59
        a = t * 5 * 2 * math.pi
        pts.append((0.09 * math.cos(a), 0.09 * math.sin(a), 0.05 + 0.28 * t))
        radii.append(0.016)
    spring = give(tube("Feder", pts, radii, segs=8), M["steel"])
    skin_to(spring, arm, lambda c: {"Top": smooth01((c.z - 0.05) / 0.28), "Body": 1 - smooth01((c.z - 0.05) / 0.28)})
    foot = give(lathe("Fuss", [(0.05, 0.0), (0.05, 0.16), (0.0, 0.17), (0.0, 0.0)], segs=32), M["hazard"])
    attach(join_parts([foot, give(torus("Fussring", (0, 0, 0.05), 0.16, 0.012, rot=(0, 0, 0), segs=32), M["rubber"])], "Federbot_Fuss"), arm, "Body")
    head = [give(sphere("Kopf", (0, 0, 0.47), 0.19, (1.0, 0.95, 0.85)), M["steel"]),
            give(torus("Kopfnaht", (0, 0, 0.47), 0.19, 0.008, rot=(0, 0, 0), segs=40), M["steel_dark"]),
            give(lathe("Hals", [(0.04, 0.0), (0.04, 0.06), (-0.04, 0.06), (-0.04, 0.0)], segs=20), M["steel_dark"])]
    head[-1].location = (0, 0, 0.33)
    eye_ring = torus("Augenring", (0, 0, 0), 0.085, 0.02, segs=32); eye_ring.matrix_world = Matrix.Translation((0, -0.165, 0.48)) @ Matrix.Rotation(math.radians(90), 4, 'X')
    head += [give(eye_ring, M["steel_dark"]), give(sphere("Auge", (0, -0.15, 0.48), 0.075, (1, 0.55, 1)), M["led"])]
    head.append(block_rot("Blende", (0, -0.15, 0.585), (0.13, 0.03, 0.02), M["steel_dark"], (math.radians(-20), 0, 0)))
    for s_ in (-1, 1):
        head.append(give(lathe("Schraube%d" % s_, [(0.02, 0.0), (0.02, 0.035), (-0.0, 0.035), (0.0, 0.0)], segs=6), M["steel_dark"]))
        head[-1].location = (s_ * 0.185, 0, 0.47); head[-1].rotation_euler = (0, math.radians(90 * s_), 0)
    attach(join_parts(head, "Federbot_Kopf"), arm, "Top")
    remove_body(body)

@variante("robo_tentakler", "tentakler")
def drohnenfluegler(arm, body):
    """Robo-Fabrik, mittel: Drohnenflügler – fliegende Drohne aus Stahlblech mit Nieten, Flügeln aus dunklem Blech,
    Rotoren auf den Flügeln, gelb-schwarzen Hörnern und rot leuchtenden Augen"""
    M = robo_mats()
    T = texels(body)
    px, P = T["px"], T["P"]
    red = hue_mask(px, 0.02, 0.06, 0.35)
    teal = hue_mask(px, 0.49, 0.08, 0.3)
    hh, s, v = hsv(px)
    beige = np.clip((0.6 - s) / 0.1, 0, 1) * np.clip((v - 0.5) / 0.1, 0, 1) * hue_mask(px, 0.11, 0.07, 0.08)
    white = np.clip((0.15 - s) / 0.06, 0, 1) * np.clip((v - 0.8) / 0.06, 0, 1)
    metal_paint(T, red, 531, rust=0.2)
    metal_paint(T, teal, 533, base=(0.3, 0.31, 0.35), rust=0.1, freq=10.0)
    hazard_paint(T, beige, freq=14.0)
    paint(T, white, (1.0, 0.35, 0.25), keep_shading=0.2)
    glow(T, white, (1.0, 0.12, 0.05))
    commit(T, strength=2.0)
    for side, chain in ((1, ("Bone_031", "Bone_030", "Bone_029")), (-1, ("Bone_026", "Bone_025", "Bone_024"))):
        b0 = bone_pt(arm, chain[2], 0.1)
        attach(join_parts(rotor("Rotor%d" % side, b0 + Vector((0, 0.02, 0.15)), 0.24, M) + [give(tube("Rotormast%d" % side, [tuple(b0), tuple(b0 + Vector((0, 0.02, 0.15)))], [0.02, 0.02], segs=8), M["steel_dark"])],
                          "Rotor%d" % side), arm, chain[2])
    q, m = back_pt(body, 0.0, 0.85)
    if q is not None:
        attach(join_parts(exhaust("Duese", q - m * 0.01, (0, 1, -0.3), 0.18, 0.03, M, smoke=False), "Duese"), arm, "Bone_001")

@variante("robo_panzerkaefer", "panzerkaefer")
def panzerroboter(arm, body):
    """Robo-Fabrik, stark: Panzerroboter – schwerer Käferpanzer aus Stahlplatten mit Nieten und Warnstreifen am Rand,
    einem kleinen Geschützturm oben, rot leuchtenden Augen und Auspuffrohren hinten"""
    M = robo_mats()
    T = texels(body)
    px, P, N = T["px"], T["P"], T["N"]
    teal = hue_mask(px, 0.49, 0.08, 0.3)
    red = np.maximum(hue_mask(px, 0.02, 0.06, 0.35), hue_mask(px, 0.97, 0.05, 0.3))
    hh, s, v = hsv(px)
    beige = np.clip((0.6 - s) / 0.1, 0, 1) * np.clip((v - 0.5) / 0.1, 0, 1) * hue_mask(px, 0.11, 0.07, 0.08)
    blue = hue_mask(px, 0.55, 0.08, 0.3) * np.clip((bone_pt(arm, "Head", 0.0).y - P[..., 1]) / 0.03, 0, 1)
    teal = np.maximum(teal, hue_mask(px, 0.55, 0.08, 0.3) * (1 - np.clip((bone_pt(arm, "Head", 0.0).y - P[..., 1]) / 0.03, 0, 1)))
    metal_paint(T, teal, 541, rust=0.25, freq=6.0)
    rim = teal * np.clip((0.12 - P[..., 2]) / 0.03, 0, 1)
    hazard_paint(T, rim, freq=12.0)
    metal_paint(T, red, 543, base=(0.3, 0.31, 0.35), rust=0.15)
    paint(T, beige, (0.95, 0.75, 0.1), keep_shading=0.5)
    paint(T, blue, (1.0, 0.3, 0.2), keep_shading=0.3)
    glow(T, blue, (1.0, 0.12, 0.05))
    commit(T, strength=2.0)
    p, n = surface(body, (0.0, 0.05, 2.0), (0, 0, -1))
    top = p if p is not None else Vector((0, 0.05, 0.4))
    tur = [give(sphere("Turm", tuple(top + Vector((0, 0, 0.01))), 0.09, (1, 1, 0.55)), M["steel"])]
    tur.append(give(tube("Rohr", [tuple(top + Vector((0, -0.05, 0.03))), tuple(top + Vector((0, -0.24, 0.06)))], [0.022, 0.02], segs=10), M["steel_dark"]))
    tur.append(give(torus("Muendung", tuple(top + Vector((0, -0.24, 0.06))), 0.022, 0.008, rot=(90, 0, 0), segs=12), M["steel"]))
    tur.append(give(sphere("Turmlampe", tuple(top + Vector((0.05, 0.02, 0.055))), 0.018), M["led"]))
    attach(join_parts(tur, "Geschuetzturm"), arm, "Body")
    parts = []
    for s_ in (-1, 1):
        q, m = surface(body, (s_ * 0.1, 1.5, 0.2), (0, -1, 0))
        if q is not None:
            parts += exhaust("Auspuff%d" % s_, q - m * 0.01, (s_ * 0.2, 1.0, 0.3), 0.18, 0.025, M)
    attach(join_parts(parts, "Auspuffe"), arm, "Body")

@variante("fabrik_mutter_alt", "schleimmutter")      # alte Kuppel-Fabrikmutter; neu: tools/monster/fabrikmutter.py
def fabrikmutter(arm, body):
    """Robo-Fabrik (Welt 20), Boss: Fabrikmutter – riesiger Kuppelroboter aus Blech mit Warnstreifen, Bildschirmgesicht
    mit rot leuchtenden LED-Augen, zwei Greifarmen, qualmenden Schornsteinen oben und Rädern unten. Eigene Figur auf dem
    Skelett der Schleimmutter."""
    M = robo_mats()
    prof = [(1.0, 0.0), (0.99, 0.12), (0.95, 0.24), (0.88, 0.34), (0.76, 0.42), (0.6, 0.47), (0.4, 0.5), (0.2, 0.5), (0.08, 0.48), (0.02, 0.42), (0.0, 0.3), (0.0, 0.0)]
    g = dome_robot("Fabrik", prof, M, (0.58, 0.6, 0.64), 0.1)
    skin_to(g, arm, lambda c: {"Top": smooth01((c.z - 0.2) / 0.4), "Body": 1 - smooth01((c.z - 0.2) / 0.4)})
    screen_m = look("Bildschirm", (0.03, 0.05, 0.06), rough=0.15, emit=(0.0, 0.08, 0.06), strength=0.5)
    parts = []
    p, n = surface(g, (0, -2.0, 0.62), (0, 1, 0))
    scr = block_at("Bildschirm", p + n * 0.0, (0.3, 0.05, 0.17), screen_m, 3, True, 0)
    parts.append(give(scr, screen_m))
    parts.append(give(block_at("Rahmen", p - n * 0.01, (0.33, 0.04, 0.2), M["steel_dark"], 4, True, 0), M["steel_dark"]))
    for s_ in (-1, 1):
        e = sphere("LEDAuge%d" % s_, (0, 0, 0), 0.06, (1.4, 0.4, 0.8)); e.location = p + Vector((s_ * 0.12, -0.05, 0.02)); e.rotation_euler = (0, math.radians(-s_ * 15), 0)
        parts.append(give(e, M["led"]))
        parts.append(block_rot("LEDBraue%d" % s_, p + Vector((s_ * 0.12, -0.05, 0.11)), (0.08, 0.01, 0.014), M["led"], (0, math.radians(s_ * 22), 0)))
    mouth = block_at("LEDMund", p + Vector((0, -0.05, -0.09)), (0.12, 0.01, 0.016), M["led"], 6, True, 0)
    parts.append(give(mouth, M["led"]))
    for s_ in (-1, 1):
        b0 = Vector((s_ * 0.22, 0.12, 0.95))
        parts.append(give(tube("Schornstein%d" % s_, [tuple(b0 - Vector((0, 0, 0.1))), tuple(b0 + Vector((0, 0, 0.25)))], [0.06, 0.055], segs=16), M["steel_dark"]))
        parts.append(give(torus("Schornsteinring%d" % s_, tuple(b0 + Vector((0, 0, 0.25))), 0.06, 0.012, rot=(0, 0, 0), segs=20), M["hazard"]))
        for k in range(3):
            parts.append(give(sphere("Qualm%d_%d" % (s_, k), tuple(b0 + Vector((0.02 * k * s_, 0.02 * k, 0.33 + 0.12 * k))), 0.06 + 0.035 * k), M["smoke"]))
    attach(join_parts(parts, "Fabrik_Oben"), arm, "Top")
    arms_ = []
    for s_ in (-1, 1):
        sh = Vector((s_ * 0.48, -0.05, 0.4)); el = Vector((s_ * 0.68, -0.25, 0.42)); wr = Vector((s_ * 0.6, -0.48, 0.32))
        arms_.append(give(sphere("Schultergelenk%d" % s_, tuple(sh), 0.08), M["hazard"]))
        arms_.append(give(tube("Oberarm%d" % s_, [tuple(sh), tuple(el)], [0.045, 0.04], segs=12), M["steel"]))
        arms_.append(give(sphere("Ellbogen%d" % s_, tuple(el), 0.055), M["steel_dark"]))
        arms_.append(give(tube("Unterarm%d" % s_, [tuple(el), tuple(wr)], [0.04, 0.035], segs=12), M["steel"]))
        for k in (-1, 1):
            arms_.append(give(horn("Greifer%d_%d" % (s_, k), tuple(wr), tuple(wr + Vector((k * 0.06, -0.08, 0.0))), tuple(wr + Vector((k * 0.02, -0.15, -0.02))), 0.025, n=8), M["steel_dark"]))
    for s_ in (-1, 1):
        for y in (-0.25, 0.25):
            arms_.append(give(torus("Rad%d_%d" % (s_, int(y * 10)), (s_ * 0.45, y, 0.08), 0.08, 0.035, rot=(0, 90, 0), segs=24), M["rubber"]))
    attach(join_parts(arms_, "Fabrik_Arme"), arm, "Body")
    dampen_scale(arm, ("Body", "Top"), 0.4)
    remove_body(body)

# ---------------------------------------------------------------- Wolkenstadt (Welt 21 und 22): Marmor, Himmelblau, Federn

def sky_mats():
    return {
        "marble": look("Marmor", (0.94, 0.94, 0.96), rough=0.25),
        "sky": look("Himmelblau", (0.45, 0.7, 0.98), rough=0.4),
        "gold": look("Himmelsgold", (1.0, 0.82, 0.4), rough=0.25, metal=0.9),
        "feather": look("Feder", (0.97, 0.97, 1.0), rough=0.7),
        "feather2": look("FederBlau", (0.62, 0.8, 1.0), rough=0.7),
        "eye": look("Himmelsauge", (1.0, 0.9, 0.5), rough=0.2, emit=(1.0, 0.8, 0.3), strength=2.5),
        "dark": look("Pupille", (0.05, 0.05, 0.08), rough=0.3),
        "beak": look("Schnabel", (1.0, 0.75, 0.25), rough=0.35),
    }

def marble_paint(T, mask, seed):
    P = T["P"]
    paint(T, mask, np.asarray((0.94, 0.94, 0.96), np.float32) * (0.93 + 0.1 * fbm3(P, 5.0, seed, 3)[..., None]), keep_shading=0.45)
    paint(T, mask * ridges(P, 4.0, seed + 1, 0.02) * 0.7, (0.62, 0.66, 0.78), keep_shading=0.0)

def feather_fan(name, base, d, side, n, L, w, mats, spread=70):
    """Fächer aus Federn (Flügel, Schwanz, Federbusch)"""
    d = Vector(d).normalized(); side = Vector(side).normalized()
    parts = []
    for k in range(n):
        t = k / max(1, n - 1)
        a = math.radians(-spread / 2 + spread * t)
        dd = (d * math.cos(a) + side * math.sin(a)).normalized()
        parts.append(fin("%s%d" % (name, k), Vector(base), dd, L * (0.75 + 0.25 * math.sin(math.pi * t)), w, mats[k % len(mats)], curl=0.15))
    return parts

def sky_body(T, R, seed, suit=(0.45, 0.7, 0.98)):
    marble_paint(T, R["skin"], seed)
    paint(T, R["purple"] * (1 - R["head"]), suit, keep_shading=0.6)
    paint(T, R["purple"] * R["head"], (0.75, 0.86, 1.0), keep_shading=0.5)
    paint(T, R["grey"], (1.0, 0.82, 0.4), keep_shading=0.5)
    eyes = R["white"] * R["head"]
    paint(T, eyes, (1.0, 0.92, 0.6), keep_shading=0.2)
    glow(T, eyes, (1.0, 0.8, 0.3))

def back_wings(body, arm, M, span, n=6, z=None, bone="mixamorig:Spine2"):
    sp = bone_pt(arm, bone)
    p, nn = back_pt(body, 0.0, z if z is not None else sp.z + 0.05)
    if p is None:
        return
    parts = []
    for s_ in (-1, 1):
        b0 = p + Vector((s_ * 0.05, 0.02, 0.0))
        parts += feather_fan("Fluegel%d_" % s_, b0, (s_ * 1.0, 0.5, 0.45), (0, 0, -1), n, span, span * 0.22, (M["feather"], M["feather2"]), spread=80)
    attach(join_parts(parts, "Fluegel"), arm, bone)

def plume(body, arm, M, L, n=5):
    p, nn = head_top(body, 0.0, 0.03)
    if p is None:
        return
    parts = feather_fan("Federbusch", p - nn * 0.02, (0, 0.5, 1.0), (1, 0, 0), n, L, L * 0.25, (M["feather2"], M["feather"]), spread=60)
    attach(join_parts(parts, "Federbusch"), arm, "mixamorig:Head")

@variante("himmel_krabbler", "krabbler")
def federwicht(arm, body):
    """Himmelsbrücken, leicht: Federwicht – kleiner Himmelskobold mit Haut aus weißem Marmor, himmelblauem Anzug mit
    Gold, golden leuchtenden Augen, kleinen Federflügeln und einem Federbusch"""
    M = sky_mats()
    T = texels(body); R = regions(T, arm)
    sky_body(T, R, 601)
    commit(T, strength=1.5)
    back_wings(body, arm, M, 0.22, n=5)
    plume(body, arm, M, 0.16)

@variante("himmel_tentakler", "tentakler")
def himmelsflatterer(arm, body):
    """Himmelsbrücken, mittel: Himmelsflatterer – Flugwesen mit weißem Federkleid, himmelblauen Federflügeln, goldenen
    Hörnern, golden leuchtenden Augen, Federkamm und Schwanzfedern"""
    M = sky_mats()
    T = texels(body)
    px, P = T["px"], T["P"]
    red = hue_mask(px, 0.02, 0.06, 0.35)
    teal = hue_mask(px, 0.49, 0.08, 0.3)
    hh, s, v = hsv(px)
    beige = np.clip((0.6 - s) / 0.1, 0, 1) * np.clip((v - 0.5) / 0.1, 0, 1) * hue_mask(px, 0.11, 0.07, 0.08)
    white = np.clip((0.15 - s) / 0.06, 0, 1) * np.clip((v - 0.8) / 0.06, 0, 1)
    paint(T, red, np.asarray((0.97, 0.97, 1.0), np.float32) * (0.9 + 0.12 * fbm3(P, 40.0, 611, 2)[..., None]), keep_shading=0.4)
    lines = ridges(P * np.asarray((1.0, 1.0, 0.3), np.float32), 14.0, 613, 0.05)
    paint(T, teal, gradient((0.45, 0.68, 0.98), (0.8, 0.9, 1.0), lines), keep_shading=0.35)
    paint(T, beige, (1.0, 0.82, 0.4), keep_shading=0.4)
    paint(T, white, (1.0, 0.92, 0.6), keep_shading=0.2)
    glow(T, white, (1.0, 0.8, 0.3))
    commit(T, strength=1.5)
    p, n = head_top(body, 0.0, 0.05)
    parts = []
    if p is not None:
        parts += feather_fan("Kamm", p - n * 0.02, (0, 0.5, 1.0), (1, 0, 0), 5, 0.2, 0.05, (M["feather2"], M["feather"]), spread=60)
    q, m = back_pt(body, 0.0, 0.8)
    if q is not None:
        parts += feather_fan("Schwanz", q - m * 0.02, (0, 1.0, -0.3), (1, 0, 0), 5, 0.3, 0.06, (M["feather"], M["feather2"]), spread=70)
    attach(join_parts(parts, "Federn"), arm, "Bone_001")

@variante("himmel_brecher", "brecher")
def wolkenwaechter(arm, body):
    """Himmelsbrücken, stark: Wolkenwächter – massiger Himmelsritter mit Marmorhaut, himmelblauer Rüstung mit Gold,
    goldenen Schulterplatten, Federflügeln auf dem Rücken, Federbusch und golden leuchtenden Augen"""
    M = sky_mats()
    T = texels(body); R = regions(T, arm)
    sky_body(T, R, 621)
    collar = np.maximum(R["white"] * (1 - R["head"]), R["collar"])
    paint(T, collar, (1.0, 0.82, 0.4), keep_shading=0.5)
    commit(T, strength=1.5)
    back_wings(body, arm, M, 0.5, n=7)
    plume(body, arm, M, 0.24, n=6)
    for s_, side in ((1, "Left"), (-1, "Right")):
        a0 = bone_pt(arm, "mixamorig:%sArm" % side)
        p, n = surface(body, (a0.x, a0.y, a0.z + 0.15), (0, 0, -1))
        c = (p if p is not None else a0) + Vector((s_ * 0.02, 0, 0.02))
        d = sphere("Schulterplatte" + side, (0, 0, 0), 0.13, (1.0, 1.1, 0.5)); d.location = c; d.rotation_euler = (0, math.radians(-s_ * 25), 0)
        attach(join_parts([give(d, M["gold"]), give(torus("Schulterrand" + side, tuple(c), 0.125, 0.015, rot=(0, -s_ * 25, 0), segs=32), M["sky"])], "Schulterplatte" + side), arm, "mixamorig:%sArm" % side)

def eagle_head(hc, R_, M, parts):
    """Adlerkopf: weißer Federkopf, goldener Hakenschnabel, golden leuchtende Augen mit Brauenwulst, Federkamm"""
    parts.append(give(sphere("Adlerkopf", tuple(hc), R_, (0.95, 1.05, 0.95), segs=(40, 24)), M["feather"]))
    tipb = hc + Vector((0, -R_ * 1.35, -R_ * 0.35))
    parts.append(give(horn("Schnabel", tuple(hc + Vector((0, -R_ * 0.75, -R_ * 0.05))), tuple(hc + Vector((0, -R_ * 1.3, 0.0))), tuple(tipb), R_ * 0.32, n=12), M["beak"]))
    for s_ in (-1, 1):
        c = hc + Vector((s_ * R_ * 0.45, -R_ * 0.78, R_ * 0.18))
        parts.append(give(sphere("Auge%d" % s_, tuple(c), R_ * 0.16), M["eye"]))
        parts.append(give(sphere("Pupille%d" % s_, tuple(c + Vector((0, -R_ * 0.12, 0))), R_ * 0.07), M["dark"]))
        parts.append(give(tube("Brauenwulst%d" % s_, [tuple(c + Vector((s_ * R_ * 0.25, R_ * 0.05, R_ * 0.18))), tuple(c + Vector((0, -R_ * 0.08, R_ * 0.14))),
                                                    tuple(c + Vector((-s_ * R_ * 0.2, -R_ * 0.1, R_ * 0.05)))], [R_ * 0.09, R_ * 0.1, R_ * 0.07]), M["feather2"]))
    parts += feather_fan("Kopffedern", hc + Vector((0, R_ * 0.3, R_ * 0.6)), (0, 0.8, 0.6), (1, 0, 0), 6, R_ * 1.5, R_ * 0.3, (M["feather"], M["feather2"]), spread=70)

@variante("greifen_waechter", "koloss")
def greifenwaechter(arm, body):
    """Himmelsbrücken (Welt 21), Boss: Greifenwächter – riesiger Himmelswächter mit Marmorhaut, himmelblau-goldener
    Rüstung, Adlerkopf mit goldenem Hakenschnabel und leuchtenden Augen, großen Federflügeln, Federstulpen und
    Krallenhänden. Eigene Figur auf dem Koloss-Skelett."""
    M = sky_mats()
    T = texels(body); R = regions(T, arm)
    sky_body(T, R, 631)
    collar = np.maximum(R["white"] * (1 - R["head"]), R["collar"])
    paint(T, collar, (1.0, 0.82, 0.4), keep_shading=0.5)
    commit(T, strength=1.5)
    koloss_arms(arm, body, M["marble"], M["beak"], M["feather"], cuff_style="fell", fingers=4, claws=True)
    c0, half = cut_head(body)
    R_ = max(half.x, half.z) * 0.98
    parts = []
    eagle_head(c0 + Vector((0, -0.02, 0.0)), R_, M, parts)
    attach(join_parts(parts, "Adlerkopf"), arm, "mixamorig:Head")
    back_wings(body, arm, M, 1.0, n=8)

@variante("turm_schleimling", "schleimling")
def glockling(arm, body):
    """Goldene Türme, leicht: Glockling – kleine, schwebende Himmelsglocke (Regel 25.11.: kein kleiner Boss): weißer
    Marmor mit himmelblauem Band und goldenem Rand, ein Gesicht mit golden leuchtenden Augen, ein goldener Klöppel unten,
    kleine Federflügel und eine goldene Aufhängeöse. Eigene Figur auf dem Skelett des Schleimlings."""
    M = sky_mats()
    bell = look("Glockenmarmor", (1, 1, 1), rough=0.3)
    prof = [(0.68, 0.0), (0.67, 0.07), (0.64, 0.13), (0.58, 0.18), (0.48, 0.21), (0.36, 0.23), (0.24, 0.26), (0.14, 0.31), (0.08, 0.36), (0.06, 0.37), (0.05, 0.34), (0.05, 0.0)]
    g = lathe("Glocke", prof, segs=48)
    H_, W_ = 512, 512
    vv = np.linspace(0, 1, H_)[:, None] * np.ones((1, W_))
    col = np.ones((H_, W_, 3)) * np.asarray((0.95, 0.95, 0.97))
    col = np.where(((vv > 0.18) & (vv < 0.28))[..., None], np.asarray((0.45, 0.7, 0.98)), col)
    col = np.where((vv < 0.12)[..., None], np.asarray((1.0, 0.82, 0.4)), col)
    col = col * (0.94 + 0.08 * fbm(H_, W_, 6, 3, 3))[..., None]
    arr = np.ones((H_, W_, 4), np.float32); arr[..., :3] = np.clip(col, 0, 1)
    lathe_texture(bell, arr)
    give(g, bell)
    bpy.context.view_layer.update()
    skin_to(g, arm, lambda c: {"Top": smooth01((c.z - 0.08) / 0.3), "Body": 1 - smooth01((c.z - 0.08) / 0.3)})
    face = []
    p, n = surface(g, (0, -2.0, 0.3), (0, 1, 0))
    for s_ in (-1, 1):
        face.append(give(sphere("Auge%d" % s_, tuple(p + Vector((s_ * 0.06, -0.005, 0.04))), 0.032, (1, 0.5, 1.2)), M["eye"]))
        face.append(give(sphere("Pupille%d" % s_, tuple(p + Vector((s_ * 0.056, -0.02, 0.035))), 0.013), M["dark"]))
        face.append(give(tube("Braue%d" % s_, [tuple(p + Vector((s_ * 0.1, 0.0, 0.09))), tuple(p + Vector((s_ * 0.06, -0.012, 0.085))), tuple(p + Vector((s_ * 0.02, -0.01, 0.07)))], [0.009, 0.011, 0.008]), M["sky"]))
    face.append(give(tube("Mund", [tuple(p + Vector((-0.03, -0.004, -0.02))), tuple(p + Vector((0.0, -0.008, -0.03))), tuple(p + Vector((0.03, -0.004, -0.02)))], [0.006, 0.008, 0.006], segs=6), M["dark"]))
    face.append(give(torus("Oese", (0, 0, 0.72), 0.05, 0.014, rot=(90, 0, 0), segs=24), M["gold"]))
    for s_ in (-1, 1):
        q, m = surface(g, (s_ * 2.0, 0.0, 0.42), (-s_, 0, 0))
        face += feather_fan("Fluegel%d_" % s_, q - m * 0.02, (s_ * 1.0, 0.3, 0.5), (0, 0, 1), 3, 0.15, 0.045, (M["feather"], M["feather2"]), spread=50)
    attach(join_parts(face, "Glockling_Oben"), arm, "Top")
    attach(join_parts([give(tube("Kloeppelstiel", [(0, 0, 0.12), (0, 0, 0.0)], [0.012, 0.012], segs=8), M["gold"]), give(sphere("Kloeppel", (0, 0, -0.01), 0.045), M["gold"])], "Kloeppel"), arm, "Body")
    dampen_scale(arm, ("Body", "Top"), 0.5)
    remove_body(body)

def owl_face(g, zc, k, M):
    """Eulengesicht: große goldene Augen in hellen Federscheiben, Schnabel, Brauen, Federohren"""
    p, n = surface(g, (0, -2.0, zc), (0, 1, 0))
    parts = []
    for s_ in (-1, 1):
        c = p + Vector((s_ * 0.11 * k, 0.02 * k, 0.03 * k))
        disc = sphere("Federscheibe%d" % s_, (0, 0, 0), 0.12 * k, (1.0, 0.35, 1.0)); disc.location = c + Vector((0, 0.01, 0))
        parts.append(give(disc, M["feather"]))
        parts.append(give(sphere("Auge%d" % s_, tuple(c + Vector((0, -0.035 * k, 0))), 0.07 * k, (1, 0.6, 1)), M["eye"]))
        parts.append(give(sphere("Pupille%d" % s_, tuple(c + Vector((0, -0.075 * k, 0))), 0.035 * k, (1, 0.5, 1)), M["dark"]))
        parts.append(give(tube("Braue%d" % s_, [tuple(c + Vector((s_ * 0.12 * k, -0.03 * k, 0.11 * k))), tuple(c + Vector((0, -0.07 * k, 0.1 * k))),
                                               tuple(c + Vector((-s_ * 0.09 * k, -0.08 * k, 0.05 * k)))], [0.022 * k, 0.026 * k, 0.018 * k]), M["feather2"]))
        q, m = surface(g, (s_ * 0.18 * k / 0.75, 0.0, 3.0), (0, 0, -1))
        if q is not None:
            parts.append(fin("Federohr%d" % s_, q - m * 0.02, (s_ * 0.5, 0.1, 1.0), 0.18 * k, 0.06 * k, M["feather2"], curl=-0.2))
    parts.append(give(horn("Schnabel", tuple(p + Vector((0, -0.02 * k, -0.04 * k))), tuple(p + Vector((0, -0.08 * k, -0.06 * k))), tuple(p + Vector((0, -0.07 * k, -0.13 * k))), 0.035 * k, n=8), M["beak"]))
    return parts

@variante("turm_zombie", "zombie")
def turmwaechter(arm, body):
    """Goldene Türme, mittel: Turmwächter – schlanker Himmelsritter mit Marmorhaut, himmelblauer Rüstung mit Gold,
    Helmbusch aus Federn, kleinen Federflügeln und golden leuchtenden Augen"""
    M = sky_mats()
    T = texels(body); R = regions(T, arm)
    sky_body(T, R, 651, suit=(0.95, 0.8, 0.42))
    commit(T, strength=1.5)
    plume(body, arm, M, 0.22, n=6)
    back_wings(body, arm, M, 0.3, n=5)

@variante("turm_panzerkaefer", "panzerkaefer")
def turmpanzer(arm, body):
    """Goldene Türme, stark: Turmpanzer – schwerer Käfer, dessen Panzer aus weißem Marmor mit Goldlinien ein kleines
    Türmchen mit goldenem Spitzdach und Fenstern trägt; himmelblauer Körper, Federn an den Seiten"""
    M = sky_mats()
    T = texels(body)
    px, P, N = T["px"], T["P"], T["N"]
    teal = hue_mask(px, 0.49, 0.08, 0.3)
    red = np.maximum(hue_mask(px, 0.02, 0.06, 0.35), hue_mask(px, 0.97, 0.05, 0.3))
    hh, s, v = hsv(px)
    beige = np.clip((0.6 - s) / 0.1, 0, 1) * np.clip((v - 0.5) / 0.1, 0, 1) * hue_mask(px, 0.11, 0.07, 0.08)
    marble_paint(T, teal, 661)
    edge, cid = worley3(P, 7.0, 663)
    paint(T, teal * np.clip(1 - edge / 0.003, 0, 1), (1.0, 0.82, 0.4), keep_shading=0.2)
    paint(T, red, (0.45, 0.7, 0.98), keep_shading=0.55)
    paint(T, beige, (1.0, 0.82, 0.4), keep_shading=0.5)
    commit(T, strength=1.0)
    p, n = surface(body, (0.0, 0.05, 2.0), (0, 0, -1))
    top = p if p is not None else Vector((0, 0.05, 0.4))
    win_m = look("Fenster", (0.3, 0.55, 1.0), rough=0.2, emit=(0.4, 0.65, 1.0), strength=1.5)
    tw = [give(lathe("Tuermchen", [(0.18, 0.0), (0.18, 0.07), (0.0, 0.075), (-0.03, 0.08), (-0.03, 0.0)], segs=24), M["marble"])]
    tw[0].location = top
    tw.append(give(horn("Spitzdach", tuple(top + Vector((0, 0, 0.17))), tuple(top + Vector((0, 0, 0.25))), tuple(top + Vector((0, 0, 0.34))), 0.1, n=6), M["gold"]))
    for k in range(4):
        a = k * math.pi / 2 + 0.3
        tw.append(block_rot("Fenster%d" % k, top + Vector((math.cos(a) * 0.073, math.sin(a) * 0.073, 0.1)), (0.012, 0.018, 0.03), win_m, (0, 0, a), seed=k))
    for s_ in (-1, 1):
        q, m = surface(body, (s_ * 2.0, 0.05, 0.18), (-s_, 0, 0))
        if q is not None:
            tw += feather_fan("Seitenfedern%d" % s_, q - m * 0.02, (s_ * 1.0, 0.4, 0.2), (0, 0, 1), 4, 0.14, 0.04, (M["feather"], M["feather2"]), spread=50)
    attach(join_parts(tw, "Turm"), arm, "Body")

@variante("wolken_eule", "schleimmutter")
def wolkeneule(arm, body):
    """Goldene Türme (Welt 22), Boss: Wolkeneule – riesige, runde Eule mit Federkleid in Weiß und Himmelblau, großen
    golden leuchtenden Augen, goldenem Schnabel, Federohren, ausgebreiteten Federflügeln, goldenen Krallen und einer
    Federkrone. Eigene Figur auf dem Skelett der Schleimmutter."""
    M = sky_mats()
    skin = look("Eulenfedern", (1, 1, 1), rough=0.7)
    prof = [(1.15, 0.0), (1.14, 0.14), (1.1, 0.28), (1.02, 0.4), (0.9, 0.5), (0.74, 0.56), (0.56, 0.58), (0.38, 0.56), (0.22, 0.5), (0.1, 0.4), (0.03, 0.26), (0.0, 0.0)]
    g = lathe("Wolkeneule", prof, segs=64)
    lathe_texture(skin, feather_tex((0.55, 0.75, 1.0), (0.98, 0.98, 1.0), rows=14, cols=18, seed=671))
    give(g, skin)
    bpy.context.view_layer.update()
    parts = owl_face(g, 0.78, 1.5, M)
    q, m = surface(g, (0, 0.0, 3.0), (0, 0, -1))
    parts += feather_fan("Krone", q - m * 0.03, (0, 0.3, 1.0), (1, 0, 0), 7, 0.3, 0.07, (M["gold"], M["feather2"]), spread=90)
    attach(join_parts(parts, "Eule_Kopf"), arm, "Top")
    wings = []
    for s_ in (-1, 1):
        p, n = surface(g, (s_ * 2.0, 0.05, 0.55), (-s_, 0, 0))
        wings += feather_fan("Fluegel%d_" % s_, p - n * 0.04, (s_ * 1.0, 0.2, -0.3), (0, 0, 1), 8, 0.55, 0.12, (M["feather2"], M["feather"]), spread=100)
        for k in range(3):
            a = math.radians(-25 + 25 * k)
            b0 = Vector((s_ * 0.18 + math.sin(a) * 0.05, -0.42, 0.04))
            wings.append(give(horn("Kralle%d_%d" % (s_, k), tuple(b0), tuple(b0 + Vector((math.sin(a) * 0.05, -0.06, -0.01))), tuple(b0 + Vector((math.sin(a) * 0.06, -0.1, -0.04))), 0.03, n=7), M["gold"]))
    attach(join_parts(wings, "Eule_Fluegel"), arm, "Body")
    skin_to(g, arm, lambda c: {"Top": smooth01((c.z - 0.25) / 0.5), "Body": 1 - smooth01((c.z - 0.25) / 0.5)})
    dampen_scale(arm, ("Body", "Top"), 0.4)
    remove_body(body)

# ---------------------------------------------------------------- Sporenwelt (Welt 23 und 24): Leuchtpilze, Myzel, Baumpilze

def spore_mats():
    return {
        "stalk": look("Pilzstiel", (0.93, 0.88, 0.76), rough=0.6),
        "cap": look("Pilzkappe", (0.95, 0.45, 0.15), rough=0.5, emit=(0.9, 0.35, 0.05), strength=0.4),
        "cap2": look("Pilzkappe2", (0.8, 0.3, 0.12), rough=0.5),
        "spot": look("Leuchtpunkt", (1.0, 0.95, 0.6), rough=0.4, emit=(1.0, 0.85, 0.4), strength=2.5),
        "teal": look("Sporenleuchten", (0.3, 1.0, 0.9), rough=0.3, emit=(0.2, 1.0, 0.85), strength=2.5),
        "bracket": look("Baumpilz", (0.75, 0.55, 0.3), rough=0.6),
        "bracket2": look("Baumpilz2", (0.3, 0.75, 0.7), rough=0.5, emit=(0.15, 0.6, 0.55), strength=0.8),
        "gill": look("Lamellen", (0.85, 0.7, 0.5), rough=0.7),
        "eye": look("Pilzauge", (0.4, 1.0, 0.9), rough=0.2, emit=(0.3, 1.0, 0.85), strength=3.0),
        "dark": look("Pilzdunkel", (0.12, 0.07, 0.05), rough=0.5),
    }

def glow_shroom(name, p, n, h, r, M, cap="cap", spots=True):
    n = Vector(n).normalized()
    parts = [give(tube(name + "Stiel", [tuple(p - n * 0.01), tuple(p + n * h * 0.5), tuple(p + n * h)], [r * 0.3, r * 0.26, r * 0.24]), M["stalk"])]
    c = sphere(name + "Hut", (0, 0, 0), r, (1, 1, 0.5)); c.location = p + n * h
    c.rotation_euler = n.to_track_quat('Z', 'Y').to_euler()
    parts.append(give(c, M[cap]))
    if spots:
        q = n.to_track_quat('Z', 'Y').to_matrix()
        for i in range(6):
            a = i * 2 * math.pi / 6 + 0.2
            d = q @ Vector((math.cos(a) * 0.6, math.sin(a) * 0.6, 0.42)).normalized()
            parts.append(give(sphere(name + "Punkt%d" % i, tuple(p + n * h + Vector((d.x * r, d.y * r, d.z * r * 0.55))), r * 0.13, (1, 1, 0.5)), M["spot"]))
    return parts

def bracket(name, p, n, r, mat):
    """Baumpilz: flacher, halbrunder Konsolenpilz, der waagerecht aus der Oberfläche wächst"""
    n = Vector(n); n.z = 0
    if n.length < 1e-3:
        n = Vector((1, 0, 0))
    n.normalize()
    o = sphere(name, (0, 0, 0), r, (1.0, 0.75, 0.22), segs=(20, 10))
    o.location = Vector(p) + n * r * 0.45
    o.rotation_euler = (0, 0, math.atan2(n.y, n.x) - math.pi / 2)
    return give(o, mat)

def spores(name, c, spread, n, r, M, seed):
    rnd = random.Random(seed)
    return [give(sphere("%s%d" % (name, i), tuple(Vector(c) + Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.3, 1))) * spread), r * rnd.uniform(0.6, 1.2)), M["teal"])
            for i in range(n)]

def mycel_paint(T, mask, seed, base=(0.42, 0.3, 0.2)):
    """Erdig-braune Haut, überzogen mit hellen Myzelfäden"""
    P = T["P"]
    paint(T, mask, np.asarray(base, np.float32) * (0.85 + 0.3 * fbm3(P, 6.0, seed, 3)[..., None]), keep_shading=0.5)
    th = np.maximum(ridges(P, 9.0, seed + 1, 0.02), ridges(P, 13.0, seed + 2, 0.015)) * np.clip((fbm3(P, 3.0, seed + 3, 2) - 0.4) / 0.1, 0, 1)
    paint(T, mask * th, (0.92, 0.9, 0.82), keep_shading=0.2)

def shroom_stalk_body(name, prof, M, H_=512):
    g = lathe(name, prof, segs=48)
    skin = look(name + "Haut", (1, 1, 1), rough=0.6)
    uu, vv = lathe_uv_grid(H_, H_)
    col = gradient((0.86, 0.78, 0.62), (0.96, 0.92, 0.82), vv) * (0.92 + 0.1 * fbm(H_, H_, 30, 3, 2))[..., None]
    arr = np.ones((H_, H_, 4), np.float32); arr[..., :3] = col
    lathe_texture(skin, arr)
    return give(g, skin)

def shroom_face(c, k, M, parts):
    c = Vector(c)
    for s_ in (-1, 1):
        parts.append(give(sphere("Auge%d" % s_, tuple(c + Vector((s_ * 0.09 * k, 0, 0.04 * k))), 0.045 * k, (1, 0.55, 1.2)), M["eye"]))
        parts.append(give(sphere("Pupille%d" % s_, tuple(c + Vector((s_ * 0.085 * k, -0.025 * k, 0.035 * k))), 0.018 * k), M["dark"]))
        parts.append(give(tube("Braue%d" % s_, [tuple(c + Vector((s_ * 0.15 * k, -0.0, 0.11 * k))), tuple(c + Vector((s_ * 0.09 * k, -0.02 * k, 0.1 * k))), tuple(c + Vector((s_ * 0.03 * k, -0.02 * k, 0.075 * k)))],
                               [0.016 * k, 0.02 * k, 0.014 * k]), M["cap2"]))
    m = sphere("Maul", (0, 0, 0), 0.06 * k, (1.3, 0.4, 0.6)); m.location = c + Vector((0, 0.0, -0.08 * k))
    parts.append(give(m, M["dark"]))

@variante("pilz_schleimling", "schleimling")
def bovistling(arm, body):
    """Pilzwald, leicht: Bovistling – kleine Pilzkugel wie ein Bovist (Regel 25.11.: kein kleiner Boss, keine
    Hutpilzform): heller, warziger Ball mit türkis leuchtenden Augen, einer Öffnung oben, aus der leuchtende Sporen
    puffen, und feinen Myzelwurzeln unten. Eigene Figur auf dem Skelett des Schleimlings (hüpft wie er)."""
    M = spore_mats()
    skin = look("Bovisthaut", (1, 1, 1), rough=0.7)
    prof = [(0.56, 0.0), (0.55, 0.09), (0.52, 0.18), (0.46, 0.25), (0.38, 0.3), (0.28, 0.32), (0.18, 0.31), (0.1, 0.27), (0.04, 0.2), (0.01, 0.1), (0.0, 0.0)]
    g = lathe("Bovist", prof, segs=48)
    H_, W_ = 512, 512
    uu, vv = lathe_uv_grid(H_, W_)
    dots = (np.sin(uu * 2 * math.pi * 18) * np.sin(vv * math.pi * 16) > 0.75).astype(np.float32)
    col = gradient((0.72, 0.6, 0.42), (0.95, 0.9, 0.78), vv * 1.3) * (1 - dots[..., None] * 0.18)
    col = col * (0.93 + 0.08 * fbm(H_, W_, 30, 7, 2))[..., None]
    arr = np.ones((H_, W_, 4), np.float32); arr[..., :3] = np.clip(col, 0, 1)
    lathe_texture(skin, arr)
    give(g, skin)
    bpy.context.view_layer.update()
    skin_to(g, arm, lambda c: {"Top": smooth01((c.z - 0.06) / 0.3), "Body": 1 - smooth01((c.z - 0.06) / 0.3)})
    face = []
    p, n = surface(g, (0, -2.0, 0.28), (0, 1, 0))
    for s_ in (-1, 1):
        face.append(give(sphere("Auge%d" % s_, tuple(p + Vector((s_ * 0.075, 0.005, 0.04))), 0.04, (1, 0.5, 1.2)), M["eye"]))
        face.append(give(sphere("Pupille%d" % s_, tuple(p + Vector((s_ * 0.07, -0.013, 0.035))), 0.015), M["dark"]))
    face.append(give(tube("Mund", [tuple(p + Vector((-0.04, -0.004, -0.03))), tuple(p + Vector((0.0, -0.008, -0.045))), tuple(p + Vector((0.04, -0.004, -0.03)))], [0.007, 0.009, 0.007], segs=6), M["dark"]))
    face.append(give(torus("Oeffnung", (0, 0, 0.555), 0.05, 0.016, rot=(0, 0, 0), segs=24), M["cap2"]))
    for k in range(4):
        face.append(give(sphere("Sporenwolke%d" % k, (0.02 * math.cos(k * 2), 0.02 * math.sin(k * 2), 0.62 + 0.07 * k), 0.035 + 0.012 * k), M["teal"]))
    attach(join_parts(face, "Bovist_Oben"), arm, "Top")
    roots = []
    for k in range(6):
        a = k * 2 * math.pi / 6 + 0.3
        roots.append(give(tendril("Wurzel%d" % k, (math.cos(a) * 0.18, math.sin(a) * 0.18, 0.03), (math.cos(a), math.sin(a), -0.6), 0.14, 0.012, 0.4, seed=k), M["stalk"]))
    attach(join_parts(roots, "Bovist_Wurzeln"), arm, "Body")
    dampen_scale(arm, ("Body", "Top"), 0.6)
    remove_body(body)

@variante("pilz_tentakler", "tentakler")
def sporenflatterer(arm, body):
    """Pilzwald, mittel: Sporenflatterer – Flugwesen mit moosbrauner Haut und Myzelfäden, Flügeln wie Pilzlamellen
    in Orange, kleinen Leuchtpilzen auf den Hornspitzen, türkis leuchtenden Augen und schwebenden Sporen"""
    M = spore_mats()
    T = texels(body)
    px, P = T["px"], T["P"]
    red = hue_mask(px, 0.02, 0.06, 0.35)
    teal = hue_mask(px, 0.49, 0.08, 0.3)
    hh, s, v = hsv(px)
    beige = np.clip((0.6 - s) / 0.1, 0, 1) * np.clip((v - 0.5) / 0.1, 0, 1) * hue_mask(px, 0.11, 0.07, 0.08)
    white = np.clip((0.15 - s) / 0.06, 0, 1) * np.clip((v - 0.8) / 0.06, 0, 1)
    mycel_paint(T, red, 711, base=(0.45, 0.33, 0.2))
    gl = ridges(P * np.asarray((1.0, 1.0, 0.25), np.float32), 18.0, 713, 0.12)
    paint(T, teal, gradient((0.75, 0.3, 0.1), (1.0, 0.62, 0.3), gl), keep_shading=0.35)
    glow(T, teal * gl * 0.3, (1.0, 0.45, 0.1))
    paint(T, beige, (0.93, 0.88, 0.76), keep_shading=0.5)
    paint(T, white, (0.5, 1.0, 0.92), keep_shading=0.2)
    glow(T, white, (0.3, 1.0, 0.85))
    commit(T, strength=1.5)
    for chain in (("Bone_009", "Bone_008", "Bone_006"), ("Bone_013", "Bone_012", "Bone_010")):
        tip = bone_pt(arm, chain[2], 1.0)
        attach(join_parts(glow_shroom("Hornpilz" + chain[0], tip - Vector((0, 0, 0.02)), (0, 0.1, 1), 0.04, 0.06, M, spots=False), "Hornpilz" + chain[0]), arm, chain[2])
    c = bone_pt(arm, "Bone_001", 0.5)
    attach(join_parts(spores("Spore", c + Vector((0, 0.1, 0.1)), 0.55, 10, 0.025, M, 715), "Sporen"), arm, "Bone_001")

@variante("pilz_panzerkaefer", "panzerkaefer")
def morchelpanzer(arm, body):
    """Pilzwald, stark: Morchelpanzer – schwerer Käfer, dessen Panzer wie eine Morchel aus Waben besteht, mit orange
    leuchtenden Pilzen, Myzelfäden auf der Haut und türkis leuchtenden Augen"""
    M = spore_mats()
    T = texels(body)
    px, P, N = T["px"], T["P"], T["N"]
    teal = hue_mask(px, 0.49, 0.08, 0.3)
    red = np.maximum(hue_mask(px, 0.02, 0.06, 0.35), hue_mask(px, 0.97, 0.05, 0.3))
    hh, s, v = hsv(px)
    beige = np.clip((0.6 - s) / 0.1, 0, 1) * np.clip((v - 0.5) / 0.1, 0, 1) * hue_mask(px, 0.11, 0.07, 0.08)
    head_ = np.clip((bone_pt(arm, "Head", 0.0).y - P[..., 1]) / 0.03, 0, 1)
    blue = hue_mask(px, 0.55, 0.08, 0.3) * head_
    teal = np.maximum(teal, hue_mask(px, 0.55, 0.08, 0.3) * (1 - head_))
    edge, cid = worley3(P, 16.0, 721)
    pit = np.clip((edge - 0.004) / 0.006, 0, 1)
    paint(T, teal, gradient((0.72, 0.58, 0.38), (0.3, 0.2, 0.12), pit), keep_shading=0.4)
    mycel_paint(T, red, 723)
    paint(T, beige, (0.93, 0.88, 0.76), keep_shading=0.5)
    paint(T, blue, (0.5, 1.0, 0.92), keep_shading=0.3)
    glow(T, blue, (0.3, 1.0, 0.85))
    commit(T, strength=1.5)
    parts = []
    for i, (x, y, h, r) in enumerate(((0.02, 0.06, 0.15, 0.09), (-0.15, 0.12, 0.1, 0.065), (0.15, 0.02, 0.09, 0.06), (0.05, -0.1, 0.07, 0.045), (-0.08, -0.06, 0.06, 0.04))):
        p, n = surface(body, (x, y, 2.0), (0, 0, -1))
        if p is not None:
            parts += glow_shroom("Pilz%d" % i, p, (n + Vector((x, 0.1, 0))).normalized(), h, r, M)
    parts += spores("Spore", (0, 0.05, 0.4), 0.3, 6, 0.02, M, 725)
    attach(join_parts(parts, "Morchelpilze"), arm, "Body")

@variante("pilz_koenigin", "schleimmutter")
def pilzkoenigin(arm, body):
    """Pilzwald (Welt 23), Boss: Pilzkönigin – riesiger Pilz mit dickem, hellem Stiel und wütendem Gesicht, breiter
    orange Kappe mit Leuchtpunkten und Lamellen, einer Krone aus kleinen Leuchtpilzen, Pilzen am Fuß und schwebenden
    Sporen. Eigene Figur auf dem Skelett der Schleimmutter."""
    M = spore_mats()
    g = shroom_stalk_body("Koenigin", [(0.7, 0.0), (0.7, 0.3), (0.55, 0.34), (0.35, 0.38), (0.15, 0.44), (0.04, 0.46), (0.0, 0.4), (0.0, 0.0)], M)
    skin_to(g, arm, lambda c: {"Top": smooth01((c.z - 0.15) / 0.4), "Body": 1 - smooth01((c.z - 0.15) / 0.4)})
    parts = []
    shroom_face((0, -0.37, 0.4), 1.8, M, parts)
    mw = next(o for o in parts if o.name == "Maul")
    parts.remove(mw); bpy.data.objects.remove(mw, do_unlink=True)
    parts += jaw_set("Pilzgebiss", Vector((0, -0.4, 0.265)), 0.12, 0.052, M["dark"], look("Pilzschlund", (1.0, 0.55, 0.2), rough=0.4, emit=(1.0, 0.45, 0.1), strength=1.4),
                     random.Random(23), gum_col=(0.55, 0.3, 0.2))
    cap = sphere("Kappe", (0, 0, 0.78), 0.72, (1, 1, 0.5)); parts.append(give(cap, M["cap"]))
    parts.append(give(lathe("Lamellen", [(0.68, 0.7), (0.72, 0.3), (0.725, 0.0)], segs=64), M["gill"]))
    for i in range(12):
        a = i * 2 * math.pi / 12 + 0.2
        el = 0.4 + 0.35 * (i % 3) / 2
        d = Vector((math.cos(a) * math.cos(el), math.sin(a) * math.cos(el), math.sin(el)))
        parts.append(give(sphere("Leuchtpunkt%d" % i, (d.x * 0.72, d.y * 0.72, 0.78 + d.z * 0.72 * 0.5), 0.07, (1, 1, 0.5)), M["spot"]))
    for k in range(5):
        a = math.radians(-60 + 30 * k)
        b0 = Vector((math.sin(a) * 0.2, -math.cos(a) * 0.12 + 0.04, 1.12))
        parts += glow_shroom("Kronenpilz%d" % k, b0, (math.sin(a) * 0.3, -0.1, 1.0), 0.08 + 0.04 * (k == 2), 0.06, M, cap="cap2")
    parts += spores("Spore", (0, 0, 1.3), 0.6, 12, 0.03, M, 731)
    attach(join_parts(parts, "Koenigin_Oben"), arm, "Top")
    foot = []
    for i in range(6):
        a = i * 2 * math.pi / 6 + 0.5
        p = Vector((math.cos(a) * 0.55, math.sin(a) * 0.5, 0.0))
        foot += glow_shroom("Fusspilz%d" % i, p, (math.cos(a) * 0.4, math.sin(a) * 0.4, 1.0), 0.09, 0.07, M, cap="cap" if i % 2 else "cap2")
    attach(join_parts(foot, "Koenigin_Fuss"), arm, "Body")
    dampen_scale(arm, ("Body", "Top"), 0.45)
    remove_body(body)

def spore_body(T, R, seed, suit=(0.22, 0.3, 0.14)):
    mycel_paint(T, R["skin"], seed)
    paint(T, R["purple"] * (1 - R["head"]), suit, keep_shading=0.6)
    spots = R["purple"] * R["head"]
    paint(T, spots, (0.4, 1.0, 0.9), keep_shading=0.3)
    glow(T, spots, (0.2, 1.0, 0.85))
    paint(T, R["grey"], (0.6, 0.45, 0.28), keep_shading=0.5)
    eyes = R["white"] * R["head"]
    paint(T, eyes, (0.5, 1.0, 0.92), keep_shading=0.2)
    glow(T, eyes, (0.3, 1.0, 0.85))

@variante("sporen_krabbler", "krabbler")
def sporenwicht(arm, body):
    """Sporennebel, leicht: Sporenwicht – kleiner Kobold mit erdbrauner Haut voller heller Myzelfäden, türkis
    leuchtenden Sporenflecken am Kopf, kleinen Leuchtpilzen auf dem Kopf und schwebenden Sporen"""
    M = spore_mats()
    T = texels(body); R = regions(T, arm)
    spore_body(T, R, 741)
    commit(T, strength=1.8)
    parts = []
    for k, (x, y, h, r) in enumerate(((0.0, 0.05, 0.1, 0.07), (-0.13, 0.0, 0.07, 0.05), (0.12, 0.08, 0.06, 0.045))):
        p, n = head_top(body, x, y)
        if p is not None:
            parts += glow_shroom("Kopfpilz%d" % k, p - n * 0.01, (n + Vector((x * 2, 0, 0.3))).normalized(), h, r, M, cap="bracket2", spots=False)
    parts += spores("Spore", bone_pt(arm, "mixamorig:Head", 1.0) + Vector((0, 0, 0.3)), 0.3, 6, 0.02, M, 743)
    attach(join_parts(parts, "Kopfpilze"), arm, "mixamorig:Head")

@variante("sporen_zombie", "zombie")
def myzelwandler(arm, body):
    """Sporennebel, mittel: Myzelwandler – hagere Gestalt, überwuchert von hellen Myzelfäden, mit türkis leuchtenden
    Baumpilzen an Schulter und Rücken, Leuchtpilzen auf dem Kopf und türkis leuchtenden Augen"""
    M = spore_mats()
    T = texels(body); R = regions(T, arm)
    spore_body(T, R, 751, suit=(0.3, 0.22, 0.14))
    commit(T, strength=1.8)
    parts = []
    for k, (x, y, h, r) in enumerate(((0.03, 0.05, 0.09, 0.06), (-0.08, 0.0, 0.06, 0.045))):
        p, n = head_top(body, x, y)
        if p is not None:
            parts += glow_shroom("Kopfpilz%d" % k, p - n * 0.01, (n + Vector((x * 2, 0, 0.3))).normalized(), h, r, M, cap="bracket2", spots=False)
    attach(join_parts(parts, "Kopfpilze"), arm, "mixamorig:Head")
    a0 = bone_pt(arm, "mixamorig:LeftArm", 0.3)
    br = [bracket("Schulterpilz%d" % k, *(lambda pn: (pn[0], pn[1]))(surface(body, a0 + Vector((1.0, dy, dz)), (-1, 0, 0))), r, M["bracket2"])
          for k, (dy, dz, r) in enumerate(((0.0, 0.0, 0.07), (0.04, -0.07, 0.055), (-0.03, 0.06, 0.045))) if surface(body, a0 + Vector((1.0, dy, dz)), (-1, 0, 0))[0] is not None]
    if br:
        attach(join_parts(br, "Schulterpilze"), arm, "mixamorig:LeftArm")
    back = []
    for k, (x, z, r) in enumerate(((-0.06, 1.0, 0.07), (0.07, 0.92, 0.06), (-0.03, 0.82, 0.05))):
        p, n = back_pt(body, x, z)
        if p is not None:
            back.append(bracket("Rueckenpilz%d" % k, p, n, r, M["bracket"] if k % 2 else M["bracket2"]))
    attach(join_parts(back, "Rueckenpilze"), arm, "mixamorig:Spine1")

@variante("sporen_brecher", "brecher")
def schwammbrecher(arm, body):
    """Sporennebel, stark: Schwammbrecher – massiger Schläger mit erdbrauner, von Myzel überzogener Haut, großen
    Baumpilzen in Orange und Türkis auf Schultern, Rücken und Unterarmen, Leuchtpilzen auf dem Kopf und Sporenwolke"""
    M = spore_mats()
    T = texels(body); R = regions(T, arm)
    spore_body(T, R, 761, suit=(0.25, 0.2, 0.12))
    collar = np.maximum(R["white"] * (1 - R["head"]), R["collar"])
    mycel_paint(T, collar, 763, base=(0.55, 0.45, 0.3))
    commit(T, strength=1.8)
    for s_, side in ((1, "Left"), (-1, "Right")):
        a0 = bone_pt(arm, "mixamorig:%sArm" % side, 0.2)
        br = []
        for k, (dy, dz, r) in enumerate(((0.0, 0.05, 0.11), (0.06, -0.06, 0.085), (-0.05, -0.1, 0.07))):
            p, n = surface(body, a0 + Vector((s_ * 1.0, dy, dz)), (-s_, 0, 0))
            if p is not None:
                br.append(bracket("Schulterpilz%s%d" % (side, k), p, n, r, M["bracket"] if (k + (s_ > 0)) % 2 else M["bracket2"]))
        f0 = bone_pt(arm, "mixamorig:%sForeArm" % side, 0.5)
        p, n = surface(body, f0 + Vector((s_ * 1.0, 0.0, 0.0)), (-s_, 0, 0))
        if br:
            attach(join_parts(br, "Schulterpilze" + side), arm, "mixamorig:%sArm" % side)
        if p is not None:
            attach(bracket("Armpilz" + side, p, n, 0.07, M["bracket2"]), arm, "mixamorig:%sForeArm" % side)
    back = []
    for k, (x, z, r) in enumerate(((-0.12, 1.15, 0.1), (0.12, 1.1, 0.09), (0.0, 0.98, 0.085), (-0.08, 0.86, 0.07))):
        p, n = back_pt(body, x, z)
        if p is not None:
            back.append(bracket("Rueckenpilz%d" % k, p, n, r, M["bracket"] if k % 2 else M["bracket2"]))
    back += spores("Spore", bone_pt(arm, "mixamorig:Spine2") + Vector((0, 0.3, 0.3)), 0.35, 8, 0.025, M, 765)
    attach(join_parts(back, "Rueckenpilze"), arm, "mixamorig:Spine2")
    parts = []
    for k, (x, y, h, r) in enumerate(((0.0, 0.0, 0.11, 0.075), (-0.1, 0.05, 0.08, 0.055), (0.1, 0.05, 0.07, 0.05))):
        p, n = head_top(body, x, y)
        if p is not None:
            parts += glow_shroom("Kopfpilz%d" % k, p - n * 0.01, (n + Vector((x * 2, 0, 0.3))).normalized(), h, r, M, cap="bracket2", spots=False)
    attach(join_parts(parts, "Kopfpilze"), arm, "mixamorig:Head")

@variante("pilz_riese_alt", "koloss")
def pilzriese(arm, body):
    """Sporennebel (Welt 24), Boss: Pilzriese – riesiger, von Myzel überwucherter Waldgeist mit erdbrauner Haut, großen
    Baumpilzen in Orange und Türkis auf Schultern und Rücken, einer Kappe aus Leuchtpilzen auf dem Kopf, türkis
    leuchtenden Augen, Rindenstulpen und einer Wolke aus leuchtenden Sporen"""
    M = spore_mats()
    bark = look("Rinde", (0.35, 0.25, 0.16), rough=0.85)
    T = texels(body); R = regions(T, arm)
    spore_body(T, R, 771, suit=(0.22, 0.17, 0.1))
    collar = np.maximum(R["white"] * (1 - R["head"]), R["collar"])
    mycel_paint(T, collar, 773, base=(0.55, 0.45, 0.3))
    commit(T, strength=1.8)
    koloss_arms(arm, body, bark, M["dark"], M["bracket"], cuff_style="fell", fingers=3)
    hc = bone_pt(arm, "mixamorig:Head", 0.6)
    parts = []
    for k, (x, y, h, r, cap) in enumerate(((0.0, 0.05, 0.22, 0.16, "cap"), (-0.2, 0.0, 0.14, 0.1, "bracket2"), (0.2, 0.02, 0.15, 0.11, "cap"), (-0.1, 0.18, 0.1, 0.08, "bracket2"), (0.12, 0.18, 0.11, 0.08, "cap2"))):
        p, n = head_top(body, x, y)
        if p is not None:
            parts += glow_shroom("Kopfpilz%d" % k, p - n * 0.02, (n + Vector((x * 2, y, 0.3))).normalized(), h, r, M, cap=cap, spots=(cap == "cap"))
    attach(join_parts(parts, "Pilzkappe"), arm, "mixamorig:Head")
    for s_, side in ((1, "Left"), (-1, "Right")):
        a0 = bone_pt(arm, "mixamorig:%sArm" % side, 0.15)
        br = []
        for k, (dy, dz, r) in enumerate(((0.0, 0.12, 0.2), (0.1, 0.0, 0.15), (-0.08, -0.08, 0.13), (0.0, -0.18, 0.11))):
            p, n = surface(body, a0 + Vector((s_ * 1.5, dy, dz)), (-s_, 0, 0))
            if p is not None:
                br.append(bracket("Schulterpilz%s%d" % (side, k), p, n, r, M["bracket"] if (k + (s_ > 0)) % 2 else M["bracket2"]))
        if br:
            attach(join_parts(br, "Schulterpilze" + side), arm, "mixamorig:%sArm" % side)
    back = []
    sp = bone_pt(arm, "mixamorig:Spine2")
    for k, (x, z, r) in enumerate(((-0.2, 0.1, 0.17), (0.2, 0.05, 0.16), (0.0, -0.1, 0.15), (-0.12, -0.3, 0.12), (0.14, -0.28, 0.12))):
        p, n = back_pt(body, x, sp.z + z)
        if p is not None:
            back.append(bracket("Rueckenpilz%d" % k, p, n, r, M["bracket"] if k % 2 else M["bracket2"]))
    back += spores("Spore", sp + Vector((0, 0.4, 0.4)), 0.7, 14, 0.04, M, 775)
    attach(join_parts(back, "Rueckenpilze"), arm, "mixamorig:Spine2")

# ---------------------------------------------------------------- Ablauf

if __name__ == "__main__":
    run(VAR, OUT)
