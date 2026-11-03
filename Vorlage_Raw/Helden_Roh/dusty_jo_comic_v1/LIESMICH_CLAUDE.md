# Dusty Jo – erster Rohmodell-Pilot im Comic-Stil

Stand: 03.11.2026. Neues Modell aus den freigegebenen, vereinfachten Comic-Entwürfen. Die bisherige detaillierte Version bleibt unverändert erhalten.

**Status: Rohmodell mit alternativem Skelett vorhanden; noch keine Animationen, keine Waffe und keine Freigabe für den direkten Spieleinsatz.** Der nächste Schritt ist ein Skelett-/Verformungstest durch Claude. Weitere Helden werden nach diesem Pilotvergleich erzeugt.

## Dateien und gemessener Zustand

| Datei | Inhalt |
| --- | --- |
| `dusty_jo_original_statisch.glb` | Unveränderter Meshy-Export, 412.566 Dreiecke, ein Material, drei eingebettete 2048er Texturen, ohne Skelett. Nur als Detailreserve verwenden. |
| `dusty_jo_reduziert_statisch.glb` | Unveränderter Meshy-Export der kostenlosen 10K-Vorbereitung, tatsächlich 10.269 Dreiecke, ein Material, drei eingebettete 2048er Texturen, ohne Skelett. Saubere Ausgangsdatei für ein neues gemeinsames Heldenskelett. |
| `dusty_jo_smart_rig_roh.glb` | Unveränderter Meshy-Smart-Rig-Export. Eine Hautbindung mit 38 Gelenkknoten, Blender importiert eine Armatur mit 39 Knochen. Namen `Bone_000` bis `Bone_038`, KEINE Mixamo-Namen. Keine Animationen. |
| `dusty_jo_vorn.png`, `dusty_jo_links.png`, `dusty_jo_hinten.png` | Drei transparente Einzelvorlagen, je 1254 × 1254 Pixel, leere Hände und A-Pose. |
| `GLB_PRUEFUNG.json` | Tatsächliche Dateigrößen, Prüfsummen, Dreiecke, Texturen, Gelenke und Animationen aller drei GLBs. |
| `BLENDER_IMPORTPRUEFUNG.json` | Erfolgreicher Import der Smart-Rig-Datei in Blender 4.5.3, Knochenhierarchie und Positionen. |
| `meshy_smart_rig_nachweis.jpg` | Browseransicht des erstellten Skeletts einschließlich Hinweis auf fehlende Bibliotheksunterstützung. |

Alle Modell-Dateien sind glTF 2.0 als GLB. Keine Texturen müssen nachgeladen werden. Es wurden keine Modellmetadaten entfernt.

## Was in Meshy geklappt hat und was nicht

Erzeugung aus Front, linker Seite und Rücken mit Meshy 7.1, Standardauflösung, Texturen 2K, Multi-View aktiv und Einstellung Privat im bezahlten Konto. Angezeigter Erzeugungspreis: 30 Credits. Die kostenlose Reduktion war Voraussetzung für das Rigging und wurde als getrennte Fassung gespeichert. Die Benutzeroberfläche zeigte während der Sitzung zusätzliche Belohnungsgutschriften; daraus lässt sich kein verlässlicher Nettopreis ableiten.

Das normale humanoide Auto-Rigging scheiterte zweimal mit der Meldung „Der Rigging-Vorgang am Modell ist fehlgeschlagen“. Der erste Versuch nutzte eine korrigierte Beckenmarkierung, der zweite die vorgeschlagenen Markierungen. Keine Serie weiterer kostenpflichtiger Modellversuche gestartet.

Das alternative **Intelligente Rig (Beta)** wurde erfolgreich exportiert. Meshy zeigt dazu ausdrücklich: **Smart-Rig-Modelle unterstützen die Animationsbibliothek noch nicht.** Deshalb fehlen Idle, Shoot und Victory tatsächlich; es gibt keine umbenannten Platzhalter. Adobe/Mixamo wurde bei diesem neuen Comic-Piloten nicht verwendet, es entstanden dort keine zusätzlichen Kosten.

## Konkrete Nacharbeit für Claude

1. Mit `dusty_jo_reduziert_statisch.glb` als verlässlicher Ausgangsdatei arbeiten. Die Smart-Rig-Datei als optionale Gewichtungs-/Knochenvorlage testen, nicht als fertiges gemeinsames Mixamo-Skelett behandeln. Ein bloßes Umbenennen garantiert keine kompatible Hierarchie oder Bewegungen.
2. Im Smart-Rig-Import ist `output_unwrapped` an `SmartRigArmature` gebunden; alle 11.126 importierten Figurpunkte besitzen Gewichte. Zusätzlich existiert ein ungebundenes Hilfsobjekt `Icosphere` mit 42 Punkten. Dieses Hilfsobjekt aus der Produktionsfassung ausschließen. Die Gesamtgrenzen inklusive Hilfsobjekt sind keine brauchbare Figurengröße.
3. Tatsächlich gemessene Höhe der gebundenen Figur: **etwa 1,70 Blender-Einheiten**. Trotz angeforderter Größenänderung hat der Export diese Höhe behalten. Figur und Skelett gemeinsam auf etwa 2 Einheiten bringen, Transformationen korrekt behandeln; Ursprung zwischen den Füßen, Ausgabe Y oben, Blickrichtung +Z prüfen. Die beigefügte Messdatei verwendet Blenders interne Z-Hochachse.
4. Für alle menschlichen Helden ein gemeinsames Skelett sicherstellen. Mindestens diese exakten Namen liefern: `mixamorig:Hips`, `mixamorig:Head`, `mixamorig:RightHand`, `mixamorig:LeftHand`, `mixamorig:RightFoot`, `mixamorig:LeftFoot`. Keine `.001`-Endungen. Seitliche Zuordnung anhand der Vorder-/Rückansicht kontrollieren, nicht aus `Bone_###` raten.
5. Erst die Verformungen an Hals, Schulter, Ellbogen, Hand, Hüfte und Knien testen. Die sehr einfachen Hände besitzen keine einzeln modellierten fünf Finger; keine Fingeranimation voraussetzen. Revolvergriff mit der rechten Hand im Spielmaßstab prüfen.
6. Separaten klassischen Revolver ergänzen, nicht mit dem Körper verschmelzen: rechter Handknochen → `WeaponSocket` → `Weapon` → `Muzzle`. Waffe starr, nicht hautgebunden. `Muzzle` an der Laufspitze, lokale −Z-Achse in Schussrichtung.
7. Texturen von 2048 auf höchstens 1024 reduzieren. Maximal 15.000 Dreiecke einschließlich Waffe, höchstens zwei Materialien anstreben. Die Ausgangsfigur hat bereits 10.269 Dreiecke.
8. Benötigte Endanimationen: **`Idle`, `Shoot`, `Victory`**. `Special` nur, falls Dusty Jos Superfähigkeit eine eigene sichtbare Körperaktion braucht. Der Nutzer hat `Run`, `Hit`, `Death` für Helden ausdrücklich als unnötig beschrieben. Keine zusätzlichen Bewegungen nur wegen älterer Sechserlisten erstellen.
9. `Idle` ruhig und ortsfest; `Shoot` kurzer Anschlag/Rückstoß/Zurückkehren, etwa 0,3–0,5 Sekunden; `Victory` für das Heldenmenü. Keine fertigen Animationen in diesem Paket behaupten. Vorhandene ältere, detaillierte Pilotanimationen können allenfalls als Quellen für eine echte Übertragung dienen, nicht direkt als passende neue Clips.
10. Finale GLB in Godot mit Vorder- und Kampf-Rückansicht testen: Handhaltung, Schussachse, Bodenkontakt, Größenverhältnis und Verformungen. Godot kann beim Import Doppelpunkte in Knochennamen ersetzen; die ursprünglichen GLB-Namen und die Godot-Zuordnung getrennt dokumentieren.

## Gestaltung beibehalten

Großer freundlicher Kopf, einfache schwarze Augen, kleiner Schnurrbart, brauner Cowboyhut mit türkisfarbener Frontplakette, rotes Halstuch, braune Jacke, beigefarbenes Hemd, dunkelblaue Hose und breite braune Stiefel. Türkisabzeichen am anatomisch linken Oberarm. Keine zusätzliche feine Rüstung, keine realistische Hautstruktur. Die Comic-Proportionen sollen erhalten bleiben.

## Herkunft und Nutzungsbedingungen

Die drei Vorlagen wurden für dieses Projekt mit OpenAI-Bildgenerierung erstellt; Meshy erhielt ausschließlich diese neuen Einzelansichten. Rohmodell-Erzeugung am 03.11.2026 im eingerichteten bezahlten Meshy-Konto mit privater Ausgabe. Laut Meshy dürfen zahlende Nutzer ihre Ausgaben kommerziell einsetzen, soweit Rechte an Eingaben gewahrt sind. Die unveränderten Originale bleiben dokumentiert; keine eigenständige Weiterverteilung einer Meshy-Animationsbibliothek.

Offizielle Angaben, in dieser Sitzung eingesehen:
- https://help.meshy.ai/en/articles/9992001-can-i-use-meshy-assets-commercially-license-copyright-explained
- https://www.meshy.ai/terms-of-use

## Prüfgrenzen

GLB-Struktur, Textur-Einbettung, Prüfsummen, Skelett und Blender-Import geprüft. **Nicht geprüft:** animierte Verformungen, Waffenbefestigung, kanonische Mixamo-Hierarchie, Godot-Laufzeit und Handy-Leistung. Diese Punkte sind offen und gehören zum vereinbarten ersten Claude-Test. Nach dessen Ergebnis den Ablauf für weitere Helden festlegen.
