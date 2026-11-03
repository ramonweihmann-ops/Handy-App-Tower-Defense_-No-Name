# Erste drei Monster-Rohmodelltests

Stand: 03.11.2026. Vom Nutzer freigegebener Comic-Stil. Geprüft werden Zombie (Zweibeiner), Tentakler (zwei Flügel und zwei Greifarme) und Panzerkäfer (sechs Beine). **Rohpaket für die Blender-Nacharbeit, keine fertige Godot-Freigabe.** Die bisherigen Spielmodelle bleiben unverändert.

## Ergebnis

| Modell | Dreiecke | Material/Textur | Skelett | Animationen im GLB |
| --- | ---: | --- | --- | --- |
| Zombie | 10.291 | ein Material, eingebettete 2048er Farbtextur | humanoider Export mit Mixamo-Namen, Blender importiert 48 Knochen | `Running`, `Walking`, `Attack`, `Dead`, `Hit_Reaction` |
| Tentakler | 10.251 | ein Material, eingebettete 2048er Farbtextur | Smart Rig, Blender importiert 32 Knochen | keine |
| Panzerkäfer | 10.043 | ein Material, eingebettete 2048er Farbtextur | Smart Rig, Blender importiert 44 Knochen; **Geometrie und Rig besitzen acht statt sechs Beine** | keine |

Je Modell liegen zwei unveränderte Meshy-GLBs bei: `*_statisch_roh.glb` ohne Skelett als Ausgangsgeometrie und `*_rig_roh.glb` mit automatischer Hautbindung. Keine vorhandene Spieldatei ersetzt. Bildvorlagen und vollständige Bildanweisungen sind enthalten.

## Zombie

Welt 2, mittlere Stärke. Normales humanoides Rigging erfolgreich; rechte und linke Hand sowie Füße sind nach Mixamo benannt. Alle fünf Clips sind im GLB tatsächlich vorhanden und in Blender importierbar:

| Quelle | Dauer ungefähr | Zielname nach Nacharbeit |
| --- | ---: | --- |
| `Walking` | 1,03 s | `Walk` |
| `Running` | 0,63 s | `Run`, sofern im Spiel genutzt |
| `Attack` | 2,80 s | `Attack` |
| `Hit_Reaction` | 1,63 s | `Hit` |
| `Dead` | 2,97 s | `Death` |

Die Quellen wurden nicht umbenannt oder geschnitten. `Idle` fehlt. Falls der Gegner warten muss, einen passenden ruhigen Clip ergänzen. Attack-Zeitpunkt, Schleifenübergänge, Bewegungsverschiebung und Bodenkontakt im Spiel prüfen. Nicht aus der Dauer auf den Trefferzeitpunkt schließen.

Das Auto-Rig ist nicht vollständig sauber: Es enthält zusätzliche generische `Bone_053`, `Bone_054` sowie `headfront`. Einige Finger-/Endknochen zeigen in der Skelettvorschau ungewöhnliche Ausrichtungen; besonders `mixamorig:RightToe_End` liegt in der importierten Ruhehierarchie ungewöhnlich hoch. Relevanz anhand der tatsächlichen Gewichte prüfen, nicht blind löschen. Die vollständige Hierarchie und Gewichte sind in den Prüfdateien dokumentiert. Grundbewegungen sind Quellen für den Test, keine bestätigte Produktionsqualität.

## Tentakler

Welt 1, mittlere Stärke. Beide Flügel und Greifarme wurden im Modell erhalten. Smart Rig setzt getrennte Ketten für die Flügel und Arme; genaue Weltpositionen stehen in `BLENDER_IMPORTPRUEFUNG.json`. Flügelketten beginnen ungefähr bei `Bone_026` und `Bone_031`, Greifarme bei `Bone_017` und `Bone_021`. Diese Zuordnung ist eine geometrische Arbeitshilfe; beim Bewegen und Prüfen der Hautgewichte bestätigen.

Meshy weist ausdrücklich darauf hin, dass Smart-Rig-Modelle die Animationsbibliothek noch nicht unterstützen. **Keine Flug-, Angriffs-, Treffer- oder Todesanimation enthalten.** In Blender eine kleine Flugschleife und die benötigten Kampfclips auf dem bereinigten Skelett erstellen. Die Hörner sollen starr bleiben und nicht unabhängig mitwackeln. Vierbeiner-/Mixamo-Vorgaben sind hier ungeeignet.

## Panzerkäfer – Test nicht bestanden: acht statt sechs Beine

Welt 1, starke Kategorie. Die korrigierte Bildvorlage zeigt sechs klar getrennte Füße. In der schrägen Meshy-Vorschau waren zusätzliche hintere Beine zunächst verdeckt. Die eigens gerenderte Draufsicht `panzerkaefer_draufsicht_pruefung.png` zeigt eindeutig: **Meshy hat aus der Sechsbeiner-Vorlage acht Beine erzeugt.** Dazu liefert das automatische Skelett acht viergliedrige seitliche Ketten, beginnend bei `Bone_010`, `Bone_014`, `Bone_018`, `Bone_022`, `Bone_026`, `Bone_030`, `Bone_034` und `Bone_038`. Damit scheitert der Test bereits an der Anatomie und nicht nur an der Bindung. Beide Käfer-GLBs ausdrücklich nur als Fehlerdiagnose verwenden.

Für die Produktion zuerst die Geometrie auf genau drei Beinpaare korrigieren oder einen neuen bestätigten Sechsbeiner modellieren. Entfernen eines überschüssigen Paares darf keine offenen Flächen oder sichtbaren Ansatzreste hinterlassen. Danach ein sauberes Skelett mit genau drei Beinpaaren anlegen und die Gewichte zuordnen. Zusätzliche Ketten nicht allein nach Nummer löschen: Sie können bereits falsche Gewichte besitzen. Erst dann einen echten Sechsbein-Gang mit abwechselnden Dreiergruppen testen. Alle sechs Füße müssen unabhängig sinnvoll reagieren, der Panzer bleibt weitgehend starr. Kein weiterer kostenpflichtiger Erzeugungsdurchlauf wurde ohne Anlass gestartet; der Rohstand dokumentiert diesen fehlgeschlagenen Pilotversuch.

## Gemeinsame Nacharbeit

- Alle drei Rig-Exporte enthalten ein zusätzliches ungebundenes Hilfsobjekt `Icosphere` mit 42 Punkten. Dieses aus der Produktionsfassung ausschließen. Für die Größe nur die gebundene Figur betrachten.
- Alle eigentlichen Figurpunkte besitzen Gewichte. Das bestätigt die Bindung, nicht deren anatomische Qualität.
- Meshy setzt alle drei Figuren auf etwa 1,70 Höhe. Der Käfer ist dadurch circa 3,30 breit, der Tentakler circa 3,63 breit. Das sind **keine abgestimmten Kampfgrößen**. Größen je Gegnertyp sinnvoll relativ zu den Helden einstellen; nicht jedes Monster pauschal auf zwei Meter bringen.
- Für die Ausgabe Y oben, Ursprung am Boden bzw. definierter Schwebehöhe und Blickrichtung +Z prüfen. JSON-Knochenpositionen aus Blender verwenden dessen interne Z-Hochachse.
- Texturen auf höchstens 1024 × 1024 reduzieren. Dreieckzahlen liegen schon ungefähr bei 10.000; nach Umbauten weiterhin höchstens 15.000 anstreben.
- Gegner benötigen weiter ihre echten Bewegungs-, Angriffs-, Treffer- und Todesclips. Die reduzierte Heldenspezifikation gilt hier nicht. Für Fliegen kann intern ein eigener Clip existieren; endgültige Namen mit dem Gegnercode abstimmen.
- Erst nach einem Godot-Test jeweils verwandte Planetenversionen produzieren. Keine automatische Kompatibilität der bisherigen Freipaket-Animationen behaupten: Bindepose, Achsen, Hierarchie und Gewichte müssen passen.

## Prüfung und Kosten

Erzeugung im bestehenden bezahlten Meshy-Konto, Einstellung Privat, Modell Meshy T2.5 / Smart Topology, Ziel 10.000 Polygone, Texturen aktiv, Posekorrektur aus. Drei Erzeugungen zu je 15 Credits: **45 Credits**. Angezeigter Kontostand vorher 1.325, danach 1.280 Credits. Keine zusätzlichen Käufe und keine Adobe-/Mixamo-Nutzung bei diesen Monstern.

Die Bildvorlagen wurden mit integrierter OpenAI-Bildgenerierung aus der vom Nutzer bestätigten Monsterübersicht erstellt. Panzerkäfer-Vorlage einmal korrigiert, damit drei Beine pro Seite sichtbar sind. Meshy erhielt ausschließlich diese Vorlagen. Unveränderte GLB-Originale erhalten, keine Herkunftsmetadaten entfernt. Nutzungsgrundlage ist das eingerichtete bezahlte Konto; offizielle Bedingungen: https://www.meshy.ai/terms-of-use

`GLB_PRUEFUNG.json` enthält Dateigrößen, Prüfsummen, Dreiecke, eingebettete Texturen und tatsächliche Animationsnamen. `BLENDER_IMPORTPRUEFUNG.json` dokumentiert erfolgreichen Import, Knochen und Gewichtsvollständigkeit. `BEWEGUNGSPRUEFUNG.json` protokolliert Stichproben der Zombie-Clips und Gewichtsmengen pro Knochen. Modellvorschauen werden aus den tatsächlichen GLBs gerendert. Smart-Rig-Vorschauen sind Ruheposen, keine vorgetäuschten Animationen.

**Offen:** Korrektur der Skelette/Gewichte, fehlende Kreaturenanimationen, Texturverkleinerung, abgestimmte Größen, Godot-Spieltest und Leistung auf dem Handy. Claude übernimmt diese vereinbarte Nacharbeit. Die Testserie zeigt, dass die Rohgeometrie nutzbar sein kann, aber generisches Auto-Rigging für diese Anatomien nicht ungeprüft als Serienlösung taugt.
