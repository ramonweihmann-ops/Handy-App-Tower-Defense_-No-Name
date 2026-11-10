# Ozeanwelt – Meshy-Rohmodelle, Modelltests v6

## Ergebnis
| Gegner | Dreiecke | Anatomieprüfung | Lieferung |
|---|---:|---|---|
| Blubberfisch | 10.459 | 0 Arme, 0 Beine, verbundene Flossen, geschlossener Körper | statische Roh-GLB |
| Quallenflieger | 10.407 | **8 statt 4 Fangarme**, Unteransicht eindeutig | Fehlbericht statt GLB |
| Krabbenpanzer | 10.405 | **6 Laufbeine + 2 Scherenarme**, drei Beine je Seite | statische Roh-GLB |
| Tiefseekrake | 9.850 | **8 Fangarme**, einzeln erkennbar | statische Roh-GLB |

Alle vier jeweils genau einmal erzeugt, **4 × 15 = 60 Credits**. Sichtbares Meshy-Guthaben vorher 1.315, danach 1.255. Kein Rigging, keine Bewegungen und keine kostenpflichtige Zusatzaktion. Der Fehlversuch wurde nicht wiederholt. Keine falsche GLB im Paket.

## Einstellungen und Vorlagen
Meshy Bild-zu-3D **T2.5**, **Smart Topology**, Ziel 10.000 Polygone, Texturen an, Meshy N1, **2K**, Posekorrektur aus, **Privat**. Jeweils genau ein unverändertes Bild, kein Zusatztext. Die tatsächlichen Eingaben sind enthalten, bytegleich zu den freigegebenen Dateien `07_leicht.png`, `07_mittel.png`, `07_stark.png`, `07_boss.png` unter `Vorlage_Raw/Gegner_51_150_v1/Einzelvorlagen/`.

Die Zielzahl ist ein Erzeugungsziel, keine harte exakte Ausgabezahl. Tatsächliche Dreiecke siehe Tabelle. Alle drei gelieferten GLBs sind glTF 2.0 mit eingebetteter 2048 × 2048 Textur, ohne externe Bilddateien, ohne Skelett und ohne Animationen. Bewegungsliste: leer. Die Rohtexturen sind unverändert; Claude reduziert sie später für den Handy-Einsatz auf die gewünschte Größe (bisherige Vorgabe höchstens 1024 × 1024).

## Dateiablage und Prüfung
Je Gegner die tatsächliche `<id>_vorlage.png` und vier RGBA-Prüf-Render mit 1024 × 1024: `_vorschau_vorn.png`, `_vorschau_seite.png`, `_vorschau_oben.png`, `_vorschau_unten.png`. Die Ansichten wurden in Blender orthografisch direkt aus der unveränderten GLB gerendert. Keine bemalten Screenshots. Blickrichtungen: vorn −Y, Seite +X, oben +Z, unten −Z im Blender-Koordinatensystem nach glTF-Import. Kein Skalieren oder Drehen des exportierten Modells.

Bei bestandener Prüfung zusätzlich `<id>_statisch_roh.glb`, bytegleich zum Meshy-Download. SHA-256, Git-Blob-SHA, Größen, Texturen, Zählwerte und weitere Einzelheiten stehen in `PRUEFBERICHT.json`. Die vorgeschlagenen Namen und Dateien ersetzen keine vorhandenen Gegner automatisch.

## Auffälligkeiten / weitere Arbeit
- Quallenflieger: acht Arme statt vier; siehe separaten Fehlbericht und Unteransicht. Nicht einbauen.
- Tiefseekrake: Fangarme relativ flach fächerförmig vor dem Körper, alle acht getrennt erkennbar. Kleine dunkle Dreiecksmarkierungen auf der oberen Kopftextur; bei Bedarf ausbessern. Keine klar abstehenden langen Netzspitzen in den vier Ansichten erkennbar.
- Krabbenpanzer: in einzelnen Projektionen liegen hintere Beine nahe an den Scherenarmen; Unteransicht zeigt die sechs Beine und zwei Scheren getrennt.
- Blubberfisch: keine abgerissene Flosse oder auffällige zusätzliche Gliedmaße in den Ansichten.

Claude übernimmt Skelett, Gewichtung, Bewegungen, Texturverkleinerung, Normierung und Spieltest. Die vorliegende Prüfung bestätigt Import, Dateiintegrität und sichtbare Anatomie, **keinen fertigen Animations- oder Godot-Kampftest**.
