# Dusty Jo – erster vollständiger GLB für den Godot-Test

Stand: 02.11.2026. Dies ist der Pilot für die Spielintegration, noch keine Freigabe für die Serienproduktion aller Helden.

## Direkt verwenden

`dusty_jo.glb` enthält Körper, Skelett, starren Revolver, eingebettete Textur und alle sechs Animationen. Die GLB-Datei allein reicht als Modellressource. Für die Vorschau das beiliegende `project.godot` mit Godot 4.5.1 oder neuer öffnen und starten. Die sechs Tasten schalten die Animationen um; der Drehschalter erlaubt die Rundumprüfung. Die eigentliche Spielintegration bleibt bei Claude.

## Geprüfte Daten

- glTF 2.0 / GLB, etwa 2 MB.
- 7.819 Dreiecke einschließlich Revolver; zwei Materialien.
- Ein eingebetteter Farbatlas mit 1024 × 1024 Pixeln; Waffenfarben als Vertexfarben.
- Ein Skelett mit 72 Gelenken. Dieses Skelett nach dem Pilotentest als Vorlage für die übrigen Helden wiederverwenden.
- Y oben, Körper in Ruhepose 2,0 Einheiten hoch, Boden bei Y = 0, Blickrichtung +Z.
- Keine mitexportierten Kameras oder Lichter.
- `GLB_PRUEFBERICHT.json`: direkte Prüfung der Exportdatei.
- `GODOT_PRUEFBERICHT.json`: tatsächlicher Import und Animationstest in Godot 4.5.1.

## Waffenbefestigung

In der GLB-Datei exakt:

`mixamorig:RightHand` → `WeaponSocket` → `Weapon` → `Muzzle`

`WeaponSocket` ist in der Blender-Quelle per Bone Parent mit der anatomisch rechten Hand verbunden. `Weapon` ist ein eigenes starres Mesh, ohne Skin. `Muzzle` sitzt an der Laufspitze. Schussrichtung: `-muzzle.global_basis.z.normalized()`. Im Anschlag zeigt sie nach +Z; das wurde im Godot-Test numerisch geprüft.

**Wichtige Godot-Eigenheit:** `Skeleton3D` erlaubt keinen Doppelpunkt in Knochennamen. Godot 4.5.1 importiert daher `mixamorig:RightHand` als `mixamorig_RightHand`. Das betrifft entsprechend auch Hips, Head, LeftHand, RightFoot und LeftFoot. Die GLB- und Blender-Namen erfüllen unverändert die vorgegebenen Mixamo-Namen. Im Spiel die importierten Namen mit Unterstrich verwenden oder mit `name.replace(":", "_")` auflösen. Nicht versuchen, einen Doppelpunkt in Godots Skelett zurückzubenennen.

Der importierte Pfad relativ zur Modellwurzel ist:

`SmartRigArmature/Skeleton3D/mixamorig_RightHand/WeaponSocket/Weapon/Muzzle`

Der Knoten `mixamorig_RightHand` unter `Skeleton3D` ist Godots automatisch erzeugtes `BoneAttachment3D`, dessen `bone_name` ebenfalls `mixamorig_RightHand` lautet. `WeaponSocket`, `Weapon` und `Muzzle` behalten ihre exakten Namen.

Referenz: https://github.com/godotengine/godot/blob/4.5/scene/3d/skeleton_3d.cpp (Prüfung in `Skeleton3D::add_bone`).

## Animationen und Ablauf

| Name | Dauer | Schleife | Verhalten |
|---|---:|---|---|
| `Idle` | 2,4167 s | ja | Anschlag mit dezenter Atmung |
| `Run` | 0,625 s | ja | Laufen auf der Stelle, Revolver bleibt befestigt |
| `Shoot` | 0,4167 s | nein | Anschlag → Rückstoß → gleicher Anschlag |
| `Hit` | 0,7917 s | ja | Trefferreaktion mit Rückkehr zum Anfang |
| `Death` | 3,5 s | nein | Zusammenbrechen, liegende Endpose mit Haltephase |
| `Victory` | 3,0 s | ja | Jubeln für das Heldenmenü |

Alle sechs Clips enthalten echte Skelettspuren. Horizontale Wurzelbewegung wurde entfernt; die Figur wird im Spiel bewegt. Bei den Schleifen stimmen erste und letzte Pose überein. `Shoot` beginnt und endet im selben Anschlag. Nach `Shoot` nach `Idle` zurückblenden; nach `Death` nicht auf `Idle` wechseln.

**Schleifen im Godot-Projekt explizit setzen:** glTF definiert selbst keine verbindlichen Schleifenkennzeichen. Das beiliegende `dusty_jo_test.gd` setzt `Animation.LOOP_LINEAR` für `Idle`, `Run`, `Hit`, `Victory` und `Animation.LOOP_NONE` für `Shoot`, `Death`. Diese Einstellung in die Spielintegration übernehmen oder die entsprechenden erweiterten Godot-Importoptionen setzen.

## Bearbeitbare Quelle und Lizenz

`Quellen/dusty_jo_bearbeitbar.blend` enthält das Modell, die Waffenbefestigung und alle sechs bearbeitbaren Aktionen. Der Unterordner ist mit `.gdignore` versehen, damit Godot ihn nicht zusätzlich als Blender-Szene importiert. Die Vorschauen wurden aus dem bearbeiteten Modell gerendert; `godot_vorschau.png` stammt aus dem tatsächlich gestarteten Godot-Testprojekt.

Lizenz und Herkunft siehe `LIZENZ_UND_HERKUNFT.md`. Es wurden keine Adobe-Abos, Bezahlfunktionen oder Mixamo-Animationsdownloads benötigt.

## Noch im eigentlichen Spiel prüfen

Lesbarkeit aus der Kampfkamera, Handgriff bei schnellen Übergängen, Mündungsfeuer/Projektile entlang -Z, Fußkontakt, Tod am tatsächlichen Spielboden und Leistung mit vielen Figuren. Der isolierte Godot-Test ersetzt diesen Spieltest nicht. Erst danach die weiteren Helden produzieren.
