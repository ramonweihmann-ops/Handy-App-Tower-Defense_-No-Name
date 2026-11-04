"""Baut aus einem humanoiden Meshy-Rohmodell (Mixamo-Knochennamen) die Spiel-GLB: Zombie (Modelltests_v1),
Krabbler, Brecher und Zombie-Koloss (Modelltests_v3). Gleiches Vorgehen für alle Zweibeiner.
Aufruf: python3 build_zweibeiner.py <id>_rig_roh.glb <ausgabe.glb> [dreiecke] [arm-abstand-grad] [--klaue] [--meshy-angriff=0.5]
(benötigt: pip install bpy). arm-abstand-grad: wie weit die Arme beim Laufen vom Körper abstehen (Hände
sollen frei an den Beinen vorbeischwingen), Standard 18. --klaue: Angriff mit offenen Klauen statt Fäusten.
--offene-haende: echte Fingerknochen behalten (keine Faust), wie beim Brecher.
--beine-gerade: Beine beim Laufen gerade nebeneinander nach vorn (Koloss: Meshys Gang ließ die dicken
Oberschenkel ineinanderlaufen); jeder Fuß auf fester Spur, Knie und Fußspitzen nach vorn.
--meshy-angriff=f: den mitgelieferten Angriff von Meshy nehmen (Brecher, Krabbler; vom Nutzer so gewählt),
zeitlich um f gestaucht; Arme bleiben vor dem Körper, echte Fingerknochen bleiben, Kopf wie bei Meshy.

Nach der Prüfung durch den Nutzer (04.11.2026): Kopf sitzt fest auf dem Oberkörper (Meshys Kopfnicken zog
die Unterlippe zu einer Spitze nach oben), Arme beim Laufen neu (hängen neben dem Körper, schwingen nur
vor und zurück, gegengleich zu den Beinen), Angriff neu als Hammerschlag nach vorn vor dem Körper.

- Hilfsobjekt „Icosphere“ entfernen
- auf etwa 5.000 Dreiecke verkleinern (mittlerer Gegner, docs/MONSTER_EINBAU.md), Gewichte bleiben erhalten
- Textur auf 1024 × 1024
- Bewegungen umbenennen: Walking → Walk, Running → Run, Dead → Death.
  Hit_Reaction fällt weg (wandert 60 cm zur Seite; Treffer zeigt das Spiel durch Aufblitzen).
- Angriff neu berechnet (der mitgelieferte kreuzt die Arme und führt sie durch den Körper):
  Lauern (Arme nach vorn) → Ausholen (Arme schräg nach außen oben, am Kopf vorbei) → Schlag (beide Klauen
  nach vorn unten, Oberkörper beugt mit) → Lauern; 1,1 s, Schleife.
- Faust beim Schlag: Die Finger hängen im Rohmodell kaum an ihren Knochen. Darum je Hand ein neuer Knochen
  „LeftFingers“/„RightFingers“ ab den Knöcheln, die Punkte dahinter gehen weich auf ihn über; beim Schlag
  krümmt er die Finger zur Handfläche (Faust), beim Ausholen leicht (Klaue).
- Blick +Z (glTF), Füße auf dem Boden; die Größe im Kampf stellt das Spiel ein (models.gd „height“)
"""
import bpy, sys, math

args = [a for a in sys.argv[1:] if not a.startswith('-')]
src, out = args[0], args[1]
target = int(args[2]) if len(args) > 2 else 5000
arm_out = float(args[3]) if len(args) > 3 else 18.0
claw = '--klaue' in sys.argv
# --beine-gerade: Beine beim Laufen selbst führen (Koloss): jeder Fuß auf fester Spur nach vorn im Abstand
# der Grundhaltung, Knie nach vorn, Füße gerade; von Meshy nur Takt, Schrittlänge und Fußheben
straight_legs = '--beine-gerade' in sys.argv
open_hands = '--offene-haende' in sys.argv   # echte Fingerknochen behalten, keine Faust (Koloss wie Brecher)
hand_twist = 0.0   # --hand-dreh=grad: Hände um die Unterarmachse zum Körper drehen (Handfläche nach innen)
finger_relax = 0.0  # --finger=grad: echte Finger beim Laufen locker krümmen
for a in sys.argv:
    if a.startswith('--hand-dreh='):
        hand_twist = float(a.split('=', 1)[1])
    if a.startswith('--finger='):
        finger_relax = float(a.split('=', 1)[1])
leg_spread = 0.0
meshy_attack = 0.0
for a in sys.argv:
    if a.startswith('--meshy-angriff='):
        meshy_attack = float(a.split('=', 1)[1])

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
scene = bpy.context.scene
for o in list(scene.objects):
    if o.name.startswith("Icosphere"):
        bpy.data.objects.remove(o, do_unlink=True)
arm = [o for o in scene.objects if o.type == 'ARMATURE'][0]
body = [o for o in scene.objects if o.type == 'MESH'][0]
arm.name = "Armature"
body.name = "Gegner"

# --- Dreiecke verkleinern (Decimate vor dem Armature-Modifier anwenden) -----------------------
tris = sum(len(p.vertices) - 2 for p in body.data.polygons)
bpy.context.view_layer.objects.active = body
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
dec = body.modifiers.new("Verkleinern", 'DECIMATE')
dec.ratio = min(1.0, target / tris)
dec.use_collapse_triangulate = True
bpy.ops.object.modifier_move_to_index(modifier=dec.name, index=0)
bpy.ops.object.modifier_apply(modifier=dec.name)
print("DREIECKE", tris, "->", sum(len(p.vertices) - 2 for p in body.data.polygons))

# --- Fingerknochen für die Faust ------------------------------------------------------------------
from mathutils import Vector
def finger_bone(side, palm):
    hand = "mixamorig:%sHand" % side
    groups = {g.index for g in body.vertex_groups if g.name == hand or g.name.startswith("mixamorig:%sHand" % side)}
    hb = arm.data.bones[hand]
    h0 = arm.matrix_world @ hb.head_local
    h1 = arm.matrix_world @ hb.tail_local
    axis = (h1 - h0).normalized()
    pts = []
    for v in body.data.vertices:
        w = sum(g.weight for g in v.groups if g.group in groups)
        if w > 0.5:
            pts.append((v, (body.matrix_world @ v.co - h0).dot(axis)))
    tmax = max(t for _, t in pts)
    knuckle = 0.45 * tmax
    # neuer Knochen an den Knöcheln
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones.new("%sFingers" % side)
    inv = arm.matrix_world.inverted()
    eb.head = inv @ (h0 + axis * knuckle)
    eb.tail = inv @ (h0 + axis * tmax)
    eb.parent = arm.data.edit_bones[hand]
    bpy.ops.object.mode_set(mode='OBJECT')
    # Gewichte: Fingergruppen in die Hand, dann weich ab den Knöcheln auf den Fingerknochen
    vg_hand = body.vertex_groups[hand]
    vg_f = body.vertex_groups.new(name="%sFingers" % side)
    for v, t in pts:
        w = sum(g.weight for g in v.groups if g.group in groups)
        for g in list(v.groups):
            if g.group in groups and g.group != vg_hand.index:
                body.vertex_groups[g.group].remove([v.index])
        x = min(1.0, max(0.0, (t - (knuckle - 0.012)) / 0.03))
        s = x * x * (3 - 2 * x)
        vg_hand.add([v.index], w * (1 - s), 'REPLACE')
        if s > 0:
            vg_f.add([v.index], w * s, 'REPLACE')
    # Krümmachse in Knochenkoordinaten: Finger drehen zur Handfläche
    bend = axis.cross(Vector(palm)).normalized()
    return "%sFingers" % side, bend

# Faust-Knochen nur für den eigenen Angriff; mit Meshys Angriff bleiben die echten Fingerknochen
FINGERS = [] if meshy_attack > 0 or open_hands else [finger_bone("Left", (-1, 0, 0)), finger_bone("Right", (1, 0, 0))]

# --- Beingewichte nach Seite --------------------------------------------------------------------
# Meshys Auto-Rig hängt bei kurzen, dicht stehenden Beinen Teile eines Oberschenkels an die Knochen des
# anderen Beins; beim Gehen verschmelzen die Beine dann ineinander (Koloss). Jeder Punkt eines Beins
# bekommt nur die Beinknochen seiner Seite (Gewicht der Gegenseite wandert auf den gleichen Knochen
# dieser Seite), die Mitte (Schritt) bleibt, wie sie ist.
def fix_leg_sides():
    names = {g.name: g.index for g in body.vertex_groups}
    parts = ("UpLeg", "Leg", "Foot", "ToeBase", "Toe_End")
    hl = arm.matrix_world @ arm.data.bones["mixamorig:LeftUpLeg"].head_local
    hr = arm.matrix_world @ arm.data.bones["mixamorig:RightUpLeg"].head_local
    cx = (hl.x + hr.x) * 0.5
    half = abs(hl.x - hr.x) * 0.5
    sign = 1.0 if hl.x > hr.x else -1.0
    moved = 0
    for v in body.data.vertices:
        p = body.matrix_world @ v.co
        if p.z > hl.z + half * 0.5:
            continue
        d = (p.x - cx) * sign          # > 0: linke Seite
        if abs(d) < half * 0.25:
            continue                   # Schritt in der Mitte
        mine, other = ("Left", "Right") if d > 0 else ("Right", "Left")
        for part in parts:
            go = names.get("mixamorig:%s%s" % (other, part))
            gm = names.get("mixamorig:%s%s" % (mine, part))
            if go is None or gm is None:
                continue
            w = 0.0
            for g in v.groups:
                if g.group == go:
                    w = g.weight
            if w > 0.0:
                body.vertex_groups[go].remove([v.index])
                cur = 0.0
                for g in v.groups:
                    if g.group == gm:
                        cur = g.weight
                body.vertex_groups[gm].add([v.index], cur + w, 'REPLACE')
                moved += 1
    print("BEINGEWICHTE umgehängt", moved)


fix_leg_sides()

# --- Textur 1024 ------------------------------------------------------------------------------
for img in bpy.data.images:
    if img.size[0] > 1024:
        img.scale(1024, 1024)
        img.pack()

# --- Bewegungen --------------------------------------------------------------------------------
RENAME = {"Walking": "Walk", "Running": "Run"}
if meshy_attack > 0:
    RENAME["Attack"] = "Attack"
for a in list(bpy.data.actions):
    if a.name in RENAME:
        a.name = RENAME[a.name]
        a.use_fake_user = True
    else:
        bpy.data.actions.remove(a)

from mathutils import Vector, Matrix, Quaternion
pose = arm.pose
aw = arm.matrix_world
SIDES = (("Left", 1.0), ("Right", -1.0))
ARMS = ["mixamorig:%s%s" % (s, b) for s, _ in SIDES for b in ("Shoulder", "Arm", "ForeArm", "Hand")]
RIGID = ["mixamorig:Neck", "mixamorig:Head", "headfront"]


def fcurves(act):
    out = []
    if hasattr(act, "layers") and act.layers:
        for layer in act.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    out.extend((bag, fc) for fc in bag.fcurves)
    else:
        out = [(act, fc) for fc in act.fcurves]
    return out


def drop_channels(act, bones):
    """Kanäle dieser Knochen aus einer Bewegung entfernen (danach neu setzen)"""
    for bag, fc in fcurves(act):
        for b in bones:
            if fc.data_path.startswith('pose.bones["%s"]' % b):
                bag.fcurves.remove(fc)
                break


def bone_dir(name):
    m = aw @ pose.bones[name].matrix
    return m.to_3x3().col[1].normalized()


def point(name, d):
    """Knochen in Weltrichtung d drehen (um seinen Kopf, Kinder folgen)"""
    pb = pose.bones[name]
    cur = aw @ pb.matrix
    q = cur.to_3x3().col[1].normalized().rotation_difference(Vector(d).normalized())
    m = Matrix.Translation(cur.translation) @ q.to_matrix().to_4x4() @ Matrix.Translation(-cur.translation) @ cur
    pb.matrix = aw.inverted() @ m
    bpy.context.view_layer.update()


def rot_world(name, axis, deg):
    """Knochen um eine Weltachse durch seinen Kopf drehen (Kinder folgen)"""
    pb = pose.bones[name]
    cur = aw @ pb.matrix
    q = Quaternion(Vector(axis).normalized(), math.radians(deg))
    m = Matrix.Translation(cur.translation) @ q.to_matrix().to_4x4() @ Matrix.Translation(-cur.translation) @ cur
    pb.matrix = aw.inverted() @ m
    bpy.context.view_layer.update()


def keep_legs_apart(factor):
    """Knie und Füße beim Laufen nie dichter als factor × ihr Abstand in der Grundhaltung (Meshys Gang
    zieht die Knie unter die Hüfte; beim Koloss mit dicken Oberschenkeln laufen die Beine dann ineinander).
    Dreht Ober- bzw. Unterschenkel um die Blickachse nach außen."""
    def x_of(name, tail=True, rest=False):
        if rest:
            b = arm.data.bones[name]
            return (aw @ (b.tail_local if tail else b.head_local)).x
        pb = pose.bones[name]
        return (aw @ (pb.tail if tail else pb.head)).x
    sign = 1.0 if x_of("mixamorig:LeftUpLeg", False, True) > x_of("mixamorig:RightUpLeg", False, True) else -1.0
    for part in ("UpLeg", "Leg"):
        target = factor * sign * (x_of("mixamorig:Left" + part, True, True) - x_of("mixamorig:Right" + part, True, True))
        for _ in range(5):
            gap = sign * (x_of("mixamorig:Left" + part) - x_of("mixamorig:Right" + part))
            need = target - gap
            if need <= 0.002:
                break
            for s, sx in SIDES:
                pb = pose.bones["mixamorig:%s%s" % (s, part)]
                length = (aw @ pb.tail - aw @ pb.head).length
                ang = math.degrees(math.asin(min(0.9, need * 0.5 / max(1e-4, length))))
                rot_world("mixamorig:%s%s" % (s, part), (0, 1, 0), -sx * sign * ang)


def knee_dirs():
    out = {}
    for sd, _ in SIDES:
        bh = aw @ arm.data.bones["mixamorig:%sUpLeg" % sd].head_local
        bk = aw @ arm.data.bones["mixamorig:%sLeg" % sd].head_local
        ba = aw @ arm.data.bones["mixamorig:%sFoot" % sd].head_local
        u = (ba - bh).normalized()
        o = (bk - bh) - u * (bk - bh).dot(u)
        out[sd] = o.normalized() if o.length > 1e-4 else Vector((0, -1, 0))
    return out


KNEE_DIR = knee_dirs()


def leg_ik(side, ankle, foot_world):
    """Zwei-Knochen-Bein: Oberschenkel und Schienbein so drehen, dass das Fußgelenk bei ankle liegt und das
    Knie nach vorn (−Y) zeigt; danach den Fuß auf seine Weltlage foot_world (gerade nach vorn) setzen."""
    up, lo, ft = ("mixamorig:%s%s" % (side, b) for b in ("UpLeg", "Leg", "Foot"))
    H = aw @ pose.bones[up].head
    l1 = arm.data.bones[up].length * aw.to_scale().x
    l2 = arm.data.bones[lo].length * aw.to_scale().x
    d_vec = ankle - H
    d = min(d_vec.length, (l1 + l2) * 0.999)
    u = d_vec.normalized()
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, l1 * l1 - a * a))
    # Knie zeigt in die Richtung, in die es in der Grundhaltung gebeugt ist (bei kurzen, breiten Beinen etwas
    # nach außen; sonst sähen die Beine x-beinig aus), dazu nach vorn
    p = KNEE_DIR[side] + Vector((0, -0.6, 0))
    p = (p - u * p.dot(u)).normalized()
    K = H + u * a + p * h
    A = H + u * d
    point(up, K - H)
    point(lo, A - (aw @ pose.bones[lo].head))
    m = foot_world.copy()
    m.translation = aw @ pose.bones[ft].head
    pose.bones[ft].matrix = aw.inverted() @ m
    bpy.context.view_layer.update()


def reset(bones):
    for n in bones:
        if n in pose.bones:
            pb = pose.bones[n]
            pb.rotation_mode = 'QUATERNION'
            pb.rotation_quaternion = Quaternion()
            pb.location = (0, 0, 0)
    bpy.context.view_layer.update()


def key(bones, frame):
    for n in bones:
        if n in pose.bones:
            pose.bones[n].keyframe_insert("rotation_quaternion", frame=frame)
            pose.bones[n].keyframe_insert("location", frame=frame)


def arm_dirs(sx, out_deg, swing_deg, bend_deg):
    """Richtung von Ober- und Unterarm (Figur schaut nach −Y, linker Arm auf +X):
    hängt um out_deg seitlich ab, schwingt um swing_deg nach vorn (+) / hinten (−), Ellbogen beugt um bend_deg"""
    o, w, b = math.radians(out_deg), math.radians(swing_deg), math.radians(swing_deg + bend_deg)
    up = Vector((sx * math.sin(o), -math.sin(w) * math.cos(o), -math.cos(o) * math.cos(w)))
    fore = Vector((sx * math.sin(o) * 0.85, -math.sin(b) * math.cos(o), -math.cos(o) * math.cos(b)))
    return up.normalized(), fore.normalized()


FINGER_BONES = [n for n, _ in FINGERS]
REAL_FINGERS = [pb.name for pb in pose.bones if any(k in pb.name for k in ("HandIndex", "HandMiddle", "HandRing", "HandPinky"))
                and pb.name[-1] in "123"]


def relax_fingers(side, deg):
    """Echte Finger locker krümmen: jedes Glied um seine eigene Querachse (lokal X)"""
    for n in REAL_FINGERS:
        if n.startswith("mixamorig:%sHand" % side):
            pb = pose.bones[n]
            pb.rotation_mode = 'QUATERNION'
            pb.rotation_quaternion = Quaternion((1, 0, 0), math.radians(deg))
    bpy.context.view_layer.update()


def curl(deg):
    for name, bend in FINGERS:
        local = (arm.data.bones[name].matrix_local.to_3x3().inverted() @ (aw.to_3x3().normalized().inverted() @ bend)).normalized()
        pose.bones[name].rotation_quaternion = Quaternion(local, math.radians(deg))
    bpy.context.view_layer.update()


# Laufen: Beine und Hüfte von Meshy, Kopf fest, Arme neu
scene.render.fps = 30
for walk_name in ("Walk", "Run"):
    act = bpy.data.actions.get(walk_name)
    if act is None:
        continue
    arm.animation_data_create()
    arm.animation_data.action = act
    f0, f1 = [int(round(x)) for x in act.frame_range]
    swing = {}
    for f in range(f0, f1 + 1):
        scene.frame_set(f)
        # Oberschenkel nach hinten (+Y) = gleichseitiger Arm nach vorn
        swing[f] = {s: bone_dir("mixamorig:%sUpLeg" % s).y for s, _ in SIDES}
    peak = max(max(abs(v) for v in d.values()) for d in swing.values()) or 1.0
    amp = 24.0 if walk_name == "Walk" else 34.0
    LEGB = ["mixamorig:%s%s" % (sd, b) for sd, _ in SIDES for b in ("UpLeg", "Leg", "Foot")] if straight_legs else []
    legs = {}
    track = {}
    if straight_legs:
        # Spur jedes Fußes: x wie in der Grundhaltung (relativ zur Hüfte), y/z (vor, zurück, heben) von Meshy
        rest_x = {sd: (aw @ arm.data.bones["mixamorig:%sFoot" % sd].head_local).x for sd, _ in SIDES}
        for f in range(f0, f1 + 1):
            scene.frame_set(f)
            track[f] = {}
            for sd, _ in SIDES:
                pb = pose.bones["mixamorig:%sFoot" % sd]
                w = aw @ pb.matrix
                a_pos = w.translation.copy()
                a_pos.x = rest_x[sd]
                # Fuß gerade nach vorn: Drehung um die Hochachse herausnehmen
                fwd = w.to_3x3().col[1].copy()
                flat = Vector((fwd.x, fwd.y, 0.0))
                yaw = Vector((0.0, flat.length if fwd.y >= 0 else -flat.length, 0.0))
                q = flat.rotation_difference(yaw) if flat.length > 1e-4 else Quaternion()
                rot = (q.to_matrix().to_4x4() @ Matrix(w.to_3x3()).to_4x4())
                track[f][sd] = (a_pos, rot)
    EXTRA = REAL_FINGERS if finger_relax else []
    drop_channels(act, ARMS + RIGID + FINGER_BONES + LEGB + EXTRA)
    for f in range(f0, f1 + 1):
        scene.frame_set(f)
        reset(ARMS + RIGID + FINGER_BONES + EXTRA)
        if straight_legs:
            reset(LEGB)
            for sd, _ in SIDES:
                leg_ik(sd, track[f][sd][0], track[f][sd][1])
        for s, sx in SIDES:
            sw = amp * swing[f][s] / peak
            up, fore = arm_dirs(sx, arm_out, sw, 14.0 + max(0.0, sw) * 0.35)
            point("mixamorig:%sArm" % s, up)
            point("mixamorig:%sForeArm" % s, fore)
            point("mixamorig:%sHand" % s, fore)
            if hand_twist:
                rot_world("mixamorig:%sForeArm" % s, fore, sx * hand_twist)
            if finger_relax:
                relax_fingers(s, finger_relax)
        if FINGERS:
            curl(18)
        key(ARMS + RIGID + FINGER_BONES + LEGB + EXTRA, f)
    arm.animation_data.action = None
    print("LAUFEN neu", walk_name, f0, f1)

def meshy_attack_fix():
    """Meshys Angriff: schneller, Arme nie hinter dem Körper"""
    act = bpy.data.actions["Attack"]
    for _bag, fc in fcurves(act):
        for kp in fc.keyframe_points:
            kp.co.x *= meshy_attack
            kp.handle_left.x *= meshy_attack
            kp.handle_right.x *= meshy_attack
    arm.animation_data.action = act
    f0, f1 = [int(round(x)) for x in act.frame_range]
    BONES = [("mixamorig:%s%s" % (sd, b)) for sd, _ in SIDES for b in ("Arm", "ForeArm", "Hand")]
    dirs = {}
    for f in range(f0, f1 + 1):
        scene.frame_set(f)
        dirs[f] = {n: bone_dir(n) for n in BONES}
    # Kopf hier wie bei Meshy (beim Schlag hält er das Gesicht oben; fest auf dem Oberkörper taucht es weg)
    drop_channels(act, BONES)
    for f in range(f0, f1 + 1):
        scene.frame_set(f)
        reset(BONES)
        for n in BONES:
            d = dirs[f][n].copy()
            if d.y > -0.08:        # nach hinten (+Y): vor den Körper holen
                d.y = -0.08
            point(n, d)
        key(BONES, f)
    arm.animation_data.action = None
    print("ANGRIFF von Meshy, gestaucht auf", meshy_attack, "Bilder", f0, f1)


if meshy_attack > 0:
    meshy_attack_fix()
    reset([pb.name for pb in pose.bones])
    print("BEWEGUNGEN", sorted(a.name for a in bpy.data.actions))
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS',
                              export_yup=True, export_apply=False, export_force_sampling=True)
    print("FERTIG", out)
    sys.exit(0)

# Angriff: Hammerschlag nach vorn – ausholen vor dem Körper nach oben, zuschlagen vor dem Körper auf
# Brusthöhe; Beine bleiben stehen, Kopf fest auf dem Oberkörper
ALL = [pb.name for pb in pose.bones]
LEGS = ["mixamorig:Hips"] + ["mixamorig:%s%s" % (sd, b) for sd, _ in SIDES for b in ("UpLeg", "Leg", "Foot", "ToeBase")]

# Standhaltung der Beine aus dem Laufen: das Bild, in dem die Füße am dichtesten beieinander sind
# (die Grundhaltung des Skeletts steht breitbeinig mit Knien nach außen)
walk = bpy.data.actions["Walk"]
arm.animation_data.action = walk
best, best_d = 0, 1e9
wf0, wf1 = [int(round(x)) for x in walk.frame_range]
for f in range(wf0, wf1 + 1):
    scene.frame_set(f)
    l = aw @ pose.bones["mixamorig:LeftFoot"].head
    r = aw @ pose.bones["mixamorig:RightFoot"].head
    d = abs(l.y - r.y) + abs(l.z - r.z)
    if d < best_d:
        best, best_d = f, d
scene.frame_set(best)
STANCE = {n: (pose.bones[n].rotation_quaternion.copy(), pose.bones[n].location.copy()) for n in LEGS}
arm.animation_data.action = None
print("STAND aus Laufbild", best)


def attack_pose(phase):
    reset(ALL)
    for n, (q, loc) in STANCE.items():
        pose.bones[n].rotation_quaternion = q
        pose.bones[n].location = loc
    bpy.context.view_layer.update()
    # Oberkörper: zurücklehnen beim Ausholen, nach vorn beugen beim Schlag
    lean = {"lauern": -6.0, "vorn": -2.0, "ausholen": 10.0, "obenvorn": 2.0, "schlag": -24.0, "zurueck": -12.0}[phase]
    sp = pose.bones["mixamorig:Spine1"]
    cur = aw @ sp.matrix
    q = Quaternion(Vector((1, 0, 0)), math.radians(lean))
    sp.matrix = aw.inverted() @ (Matrix.Translation(cur.translation) @ q.to_matrix().to_4x4() @ Matrix.Translation(-cur.translation) @ cur)
    bpy.context.view_layer.update()
    for s, sx in SIDES:
        if phase == "lauern":     # Arme vorn, leicht angewinkelt, Hände vor dem Bauch
            up, fore = Vector((sx * 0.30, -0.55, -0.78)), Vector((sx * 0.12, -0.95, -0.25))
        elif phase == "vorn":     # Zwischenstellung: Arme waagrecht nach vorn (Weg nach oben vor dem Körper)
            up, fore = Vector((sx * 0.22, -0.97, 0.05)), Vector((sx * 0.08, -0.80, 0.60))
        elif phase == "obenvorn":  # Zwischenstellung beim Zuschlagen: Arme schräg nach vorn oben
            up, fore = Vector((sx * 0.20, -0.80, 0.55)), Vector((sx * 0.07, -0.85, 0.52))
        elif phase == "zurueck":  # Zwischenstellung nach dem Schlag
            up, fore = Vector((sx * 0.25, -0.85, -0.45)), Vector((sx * 0.10, -0.98, -0.15))
        elif phase == "ausholen":  # Fäuste vor dem Körper über den Kopf
            up, fore = Vector((sx * 0.22, -0.55, 0.80)), Vector((sx * 0.08, -0.25, 0.96))
        else:                      # Schlag nach vorn, Fäuste auf Brusthöhe vor dem Körper
            up, fore = Vector((sx * 0.16, -0.98, -0.10)), Vector((sx * 0.06, -0.92, -0.38))
        point("mixamorig:%sArm" % s, up)
        point("mixamorig:%sForeArm" % s, fore)
        point("mixamorig:%sHand" % s, fore)
    curl({"lauern": 20, "vorn": 35, "ausholen": 45 if not claw else 15, "obenvorn": 70 if not claw else 25,
          "schlag": 100 if not claw else 35, "zurueck": 60}[phase])
    if not FINGERS and finger_relax:
        # echte Finger: beim Schlag fester gekrümmt
        for s, _ in SIDES:
            relax_fingers(s, finger_relax * {"lauern": 1.0, "vorn": 1.2, "ausholen": 1.0, "obenvorn": 1.6,
                                             "schlag": 2.4, "zurueck": 1.6}[phase])


act = bpy.data.actions.new("Attack")
act.use_fake_user = True
arm.animation_data_create()
arm.animation_data.action = act
for frame, phase in [(0, "lauern"), (6, "vorn"), (12, "ausholen"), (15, "ausholen"), (18, "obenvorn"), (21, "schlag"),
                     (27, "schlag"), (32, "zurueck"), (36, "lauern")]:
    attack_pose(phase)
    key(ALL, frame)
arm.animation_data.action = None
reset(ALL)
print("BEWEGUNGEN", sorted(a.name for a in bpy.data.actions))

bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS',
                          export_yup=True, export_apply=False, export_force_sampling=True)
print("FERTIG", out)
