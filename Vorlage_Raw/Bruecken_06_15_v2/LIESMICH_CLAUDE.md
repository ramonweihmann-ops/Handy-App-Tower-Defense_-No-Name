# Drei überarbeitete Brücken für die Welten 06–08

[Vorher-nachher-Übersicht](uebersicht.png) · jeweils gleicher Bildausschnitt und Maßstab.

- [06 · Dschungelmond](jungle_moon.png) – Aufrechte Bronzepfosten mit gewundenen Lianen, Moospolstern, kleinen leuchtenden Blüten und smaragdgrünen Laternen.
- [07 · Ozeanwelt](ocean_world.png) – Schiffsreling mit Tauen, Rettungsringen und warmen Bullaugen-Lampen. Die seitlichen Stützpfeiler reichen sichtbar bis ins Wasser.
- [08 · Kristallplanet](crystal_planet.png) – Große dunkle Kristallglasplatten mit hellen Facettenkanten. Beidseits der Fahrbahn stehen von innen rosa leuchtende Kristallspitzen.

## Maßprüfung

Alle drei Dateien sind RGB-PNGs mit **780 × 1688 px**. Die Montage verwendet je Welt die in Version 1 dokumentierten Eckpunkte der inneren Fahrbahnkante. Der Koordinatenursprung liegt links oben. Die Tabelle gibt die exakten Zielkoordinaten der Montage an. Bei der Sichtprüfung können Schatten, Fugen oder vorspringende Sockel die sichtbare Kante lokal um wenige Pixel verschieben.

| Welt | Oben links | Oben rechts | Unten links | Unten rechts | Änderung der Montagepunkte gegenüber Version 1 |
| --- | --- | --- | --- | --- | --- |
| 06 · Dschungelmond | (282, 294) | (499, 294) | (65, 1159) | (716, 1159) | 0 px |
| 07 · Ozeanwelt | (280, 294) | (500, 294) | (64, 1158) | (716, 1158) | 0 px |
| 08 · Kristallplanet | (280, 294) | (500, 294) | (63, 1158) | (717, 1158) | 0 px |

Der Pixelvergleich mit Version 1 bestätigt die identische Verteidigungsplattform ab Zeile 1169 und den identischen Bereich unmittelbar über der Fahrbahnmitte. Die neue Grafik sitzt lokal auf der Brücke und den direkt anschließenden Übergängen zur Kulisse, etwa an den Laternen, Kristallspitzen und Pfeilern im Wasser.

## Einbau in Godot

Die drei Dateien sind für den Austausch der gleichnamigen Texturen aus `Vorlage_Raw/Bruecken_06_15_v1/` vorgesehen. Die bisherigen Koordinaten für Gegnerpfad, Spawn und Verteidigungsplattform weiterverwenden. Die Maß- und Sichtprüfung erfolgte an den PNGs. Nach dem Austausch im Spiel kurz Spawnkante und Plattformübergang prüfen.
