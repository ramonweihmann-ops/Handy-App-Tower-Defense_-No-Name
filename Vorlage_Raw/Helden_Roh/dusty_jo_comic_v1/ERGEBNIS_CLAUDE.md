# Dusty Jo – Ergebnis des ersten Tests (Claude, 03.11.2026)

**Fertig und im Spiel:** `game/models/heroes_v2/dusty_jo.glb`, gebaut mit
`tools/heroes/build_dusty_jo.py` aus `dusty_jo_smart_rig_roh.glb` (Blender 5.2 als Python-Baustein, ohne Handarbeit).

| Prüfung | Ergebnis |
|---|---|
| Dreiecke | 10.377 inkl. Revolver |
| Texturen | 3 × 1024 × 1024, eingebettet |
| Höhe / Achsen | 2,0 Einheiten, Füße auf 0, Y oben, Blick +Z (glTF) |
| Hilfsobjekt `Icosphere` | entfernt |
| Waffe | `mixamorig:RightHand` → `WeaponSocket` → `Weapon` (starr) → `Muzzle` (−Z entlang des Laufs) |
| Animationen | `Idle` (2 s, Schleife), `Shoot` (0,4 s: Anschlag → Rückstoß → Anschlag), `Victory` (1,6 s, Schleife) |
| Godot | lädt ohne Fehler; Schüsse kommen aus `Muzzle`; Heldenseite zeigt `Victory`, Kampf `Shoot` |

**Seiten:** Nicht geraten, sondern aus der Textur bestimmt: Das türkise Abzeichen (anatomisch linker
Oberarm) sitzt auf +X, das Gesicht auf −Y (Blender). Daraus: rechte Hand = `Bone_023`.

**Knochennamen** (GLB → in Godot, dort wird `:` zu `_`):

| Smart-Rig | GLB | Godot |
|---|---|---|
| Bone_000 | mixamorig:Hips | mixamorig_Hips |
| Bone_016 | mixamorig:Head | mixamorig_Head |
| Bone_023 / 018 | mixamorig:RightHand / LeftHand | mixamorig_RightHand / _LeftHand |
| Bone_012 / 008 | mixamorig:RightFoot / LeftFoot | mixamorig_RightFoot / _LeftFoot |
| Bone_025 / 024 | mixamorig:RightArm / RightForeArm | … |
| Bone_020 / 019 | mixamorig:LeftArm / LeftForeArm | … |
| Bone_005 | mixamorig:Spine2 | … |
| Bone_026 / 021 | mixamorig:RightShoulder / LeftShoulder | … |

Die übrigen Knochen behalten `Bone_###`.

**Animationen** sind im Skript aus Armrichtungen berechnet (keine Bibliothek nötig). Das Smart Rig
genügt also, solange Meshy es so liefert. Für weitere Helden: Rohmodell mit Smart Rig wie hier, plus
die drei Ansichten. Das Skript wird je Held angepasst (Waffe, Posen); die Seitenbestimmung über die
Textur braucht ein eindeutiges Merkmal auf einer Seite, sonst kurz angeben, welche Seite rechts ist.

**Griff (korrigiert 03.11.2026, freigegeben):** Die rechte Hand wird über die Fingerknochen des Smart Rigs
zur Faust gekrümmt (Finger `Bone_035`/`034`/`033`, Daumen `Bone_038`/`037`/`036`). Der Anker
`WeaponSocket` wird in der Zielpose aus der Faust berechnet: Griff in der Faust, Lauf nach vorn, Griff nach
unten. Er hängt starr an der Hand, so sitzt der Revolver in jeder Pose in der Faust. Für weitere Helden
gilt dasselbe; die Fingerknochen heißen je Modell anders und werden im Skript eingetragen.

**Grenzen:** Die Siegerpose ist bewusst einfach. Prüfbild aus Godot: `claude_godot_posen.png` (alle Posen, Nahaufnahmen der Hand, Faust ohne Waffe).
