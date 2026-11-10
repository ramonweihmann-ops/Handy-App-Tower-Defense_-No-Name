# Dschungelmond – geprüfte 3D-Rohmodelle v4

Stand: 10.11.2026. Auftrag `Vorlage_Raw/Monster_Roh/DSCHUNGEL_MONSTER_MESHY_FUER_CHATGPT.md`. Vier genehmigte Erzeugungen ausgeführt, je ein Versuch. Drei Figuren bestanden die Anatomieprüfung; der Borkenkäfer hat acht statt sechs Beine und ist ausdrücklich nicht geliefert.

| ID | Ergebnis | Dreiecke | Skelett / Bewegungen | Gezählter Körperbau |
|---|---|---:|---|---|
| rankling | statisches Rohmodell geliefert | 9.492 | kein Skelett, keine Clips | keine Arme und Beine |
| bluetenschnapper | statisches Rohmodell geliefert | 10.381 | kein Skelett, keine Clips | zwei Blattflügel, keine Arme und Beine |
| borkenkaefer | Fehlversuch, Modell ausgeschlossen | 9.980 | kein Rigging | acht statt sechs Beine |
| urwaldriese | statisches Modell plus Rig geliefert | 10.290 / 10.290 | 58 Knochen; `Running`, `Walking`, `Attack` | zwei Arme, zwei Beine, freie Hände |

## Inhalt und Prüfungen

Für die drei gelieferten Figuren jeweils tatsächliche Meshy-Eingabe, unveränderte texturierte GLB und orthografische Ansichten von vorn, Seite und oben. Vorlagen sind 1024 × 1024 Pixel mit Alpha und anhand ihrer Git-Blob-Prüfsummen identisch mit den freigegebenen GitHub-Vorlagen. Kein neues Bild für diesen Auftrag erzeugt.

Alle vier gelieferten GLBs sind glTF 2.0 mit einer eingebetteten 2048 × 2048-Farbtextur und einem Material. Rohdateien nicht bereinigt, verkleinert oder neu exportiert. Die Texturen bleiben absichtlich in Originalauflösung; Claude übernimmt 1024-Pixel-Texturen und mobile Geometrieziele. `GLB_PRUEFUNG.json` nennt Dateiprüfsummen, tatsächliche Dreiecke, Texturen und Clips. Blender-Import und alle drei Ansichten wurden geprüft.

`Walking` dauert ungefähr 1,033 s, `Running` 0,633 s, `Attack` 2,800 s. Gehen und Laufen werden beim humanoiden Rigging automatisch mitgeliefert; Angriff stammt aus der kostenlosen Vorgabebibliothek. Export: GLB, Skelettvorlage Mixamo, riggierter Charakter an, alle hinzugefügten Animationen, einzelne Datei. Tatsächliche Knotennamen stehen in der GLB-Prüfung; vor Spielintegration mit vorhandener Gegnerkonfiguration abgleichen. Keine Namen oder Clips nachträglich umbenannt.

Das Boss-Rig wurde in Blender importiert. Alle drei Clips an je fünf Zeitpunkten auf endliche Koordinaten geprüft; keine ungewichteten Netzpunkte festgestellt. Je vier Zeitpunkte aus `Walking` und `Attack` sind in `urwaldriese_bewegungspruefung.png` gerendert. Arme und Hände bewegen sich mit, ohne abzureißen. Bei hochgeführter Hand sind Überschneidungen mit der breiten Baumkrone beziehungsweise Schulterblättern möglich. Kurze Beine ergeben enge Fuß-/Beinkreuzungen: im Godot-Spieltest prüfen und gegebenenfalls Gewichte/Clip säubern. Keine fertige Animationsfreigabe oder Godot-Abnahme behauptet.

## Einstellungen und Kosten

Meshy Bild zu 3D, T2.5, Smart Topology, Ziel 10.000 Polygone (Näherungswert), Texturen an, Meshy N1 / 2K, Posekorrektur aus, privat. Genau ein Bild pro Erzeugung, kein Zusatztext. **4 × 15 = 60 Credits**, einschließlich des misslungenen Borkenkäfers. **Rigging und Vorgabeclips: 0 zusätzliche Credits.** Keine weiteren Versuche oder Käufe.

Kontoverlauf: Ausgang 1.290 → 1.275 → 1.260 → 1.245 → 1.230. Am 10.11. kam eine automatische Tagesgutschrift von 100 hinzu; Endstand nach Rigging und Angriff 1.330. Deshalb nicht bloß Anfangs- und Endstand voneinander abziehen. Details in `BEFUNDE_UND_KOSTEN.json` und Abschlussbild.

Kostenreferenz, geprüft am 09./10.11.2026: [Meshy Webapp – Credits](https://docs.meshy.ai/en/webapp/pricing). Dort sind Rigging und fertige Bewegungsclips mit 0 Credits aufgeführt; Text-zu-Bewegung ist ein anderer, kostenpflichtiger Ablauf und wurde nicht verwendet. Bestehendes bezahltes Konto, Ausgabe privat. [Meshy-Nutzungsbedingungen](https://www.meshy.ai/terms-of-use). Keine zusätzliche Zusage exklusiver Rechte an KI-Ausgaben.

## Hinweise für Claude

- Rankling: geschlossener Blätterkörper. Kleine unruhige Kanten und gebackene Glanzstellen später glätten bzw. materialseitig prüfen. Eigenes kleines Skelett und Hüpfen wie vereinbart selbst aufbauen.
- Blütenschnapper: genau zwei breite Blattflügel, keine zusätzlichen Gliedmaßen. Ansatz der Flügel beim späteren eigenen Rig sauber gewichten; Gesicht und Blütenkranz nicht mitflattern lassen.
- Urwaldriese: kleine dunkle Punkte/Vertiefungen an Fingern und vereinfachte Hände sind lokale Netz-/Texturartefakte. Bei Bedarf bereinigen. Breite Krone und Blatt-Schulterkappen auf Durchdringung prüfen. Die Rig-Fassung wurde von Meshy auf ungefähr 1,70 m normiert; dies ist keine festgelegte Bossgröße im Spiel.
- Borkenkäfer: Fehlversuchsbericht lesen; keine achtbeinige Datei importieren. Kein Ersatzmodell unter gleichem Namen vortäuschen.

Handyziele laut Auftrag: leicht ≤ 3.000, mittel ≤ 5.000, stark ≤ 7.000, Boss ≤ 12.000 Dreiecke; Texturen 1024. Fehlende Gegnerclips ergänzt Claude. `Walking` gegebenenfalls auf den im Spiel erwarteten Namen `Walk` zuordnen; Root-Bewegung, Schleifen, Angriffsereignis und Größen auf der Dschungelbrücke testen. Erst ein Prüfbild an den Nutzer liefern und dessen Freigabe abwarten, bis dahin bisherige Gegner aktiv lassen. Keine Spieldateien wurden für diese Lieferung ersetzt.
