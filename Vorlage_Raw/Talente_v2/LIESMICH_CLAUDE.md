# Vier neue Talent-Symbole

Vier einzeln mit der eingebauten Bildgenerierung gezeichnete Motive, keine Ausschnitte aus einem Sammelbild. Stilreferenzen aus `game/ui/upgrades_v2/`. Die sechs Referenzen sind in `uebersicht.png` bei 44 und 88 Pixeln auf Grün `#3c8c3c` daneben gestellt. `auswahl.png` zeigt die vier neuen Motive größer.

| Datei | Talent / Champion | Motiv | Farbvorlage |
| --- | --- | --- | --- |
| tal_funkenherz.png | Funkenherz / Fünkchen | Rosa vierzackiger Funkelstern und kleiner goldener Funke | Rosa #ff9ae0, Gold #ffd34d |
| tal_werkzeugkiste.png | Werkzeugkiste / Pip | Türkiser Schraubenschlüssel von links unten nach rechts oben | Türkis #8fe8e8 |
| tal_bollwerk.png | Bollwerk / Rollo | Orangefarbener Wappenschild, dunkle Metallbänder als Kreuz, vier Nieten | Orange #ffc070, Rand #d8661a |
| tal_schwerefeld.png | Schwerefeld / Nova | Breite violette Spirale mit heller Mitte | Violett #d0a8ff |

Die Hex-Werte sind die Vorgaben für die gemalten Farbfamilien. Glanzlichter, Schatten und Umrisse verwenden weitere abgestufte Töne. Alle vier Symbole haben rechts oben ein kleines helles Plus.

## Einbau

Je 256 × 256 Pixel, RGBA mit echtem transparentem Hintergrund. Motiv einschließlich Plus zentriert; mindestens 22 Pixel Abstand zu den Kachelrändern. Die vollständige Kachel auf etwa 44 × 44 Punkte anzeigen, Seitenverhältnis beibehalten. Nicht nach sichtbarem Motiv beschneiden. Keine zusätzliche Karte oder Plus-Markierung darüber zeichnen. Farben nicht mit einem grünen Farbfilter multiplizieren.

Die im Spiel bereits vorhandenen gleichnamigen WebP-Dateien wurden nicht geändert. Nach Auswahl diese PNGs in den vorhandenen Importablauf übernehmen und die passenden vier Spieltexturen ersetzen. Alle übrigen Talente unverändert lassen.

## Prüfung

Maße, RGBA und freier Rand sind geprüft; die Motivbereiche stehen in `PRUEFUNG.json`. Bei 44 Pixeln bleiben Stern, Schraubenschlüssel, Schild und Wirbel erkennbar. Die Übersicht enthält echte 44-/88-Pixel-Darstellungen bei 100 Prozent Bildansicht; die Chatansicht kann die gesamte Übersicht verkleinern. Keine Schrift in den Produktionsbildern, nur das geforderte Plus. Der abschließende Einbautest in Godot steht aus.

Verwendet wurde ausschließlich die eingebaute Bildgenerierung. Anschließend Größenexport, Entfernung sehr schwachen Alpha-Rauschens und technische Zusammenstellung der Vorschau. Keine zusätzlichen kostenpflichtigen Dienste.
