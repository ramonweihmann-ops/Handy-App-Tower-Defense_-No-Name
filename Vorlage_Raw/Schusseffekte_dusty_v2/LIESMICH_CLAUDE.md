# Dusty Jo · Revolver

Ein kurzer goldener Mündungsblitz ohne Rauch, eine goldene Kugel mit kurzer Funkenspur und ein kleiner Einschlag mit nach außen laufenden Funken. Die Anschlussdaten entsprechen Version 1.

[Übersicht](UEBERSICHT.png) · [Eiswelt animiert](DUSTY_EISWELT_VORSCHAU.gif) · [Raumdock animiert](DUSTY_RAUMDOCK_VORSCHAU.gif) · [Ablaufdaten](ABLAUF_DUSTY.json)

## Formate

| Effekt | Einzelbild | Raster | Bildrate |
| --- | ---: | ---: | ---: |
| [Mündung](dusty_muendung/) | 128 × 128 px | 4 × 2 | 24 fps |
| [Geschoss](dusty_geschoss/) | 256 × 256 px | 4 × 2 | 24 fps |
| [Einschlag](dusty_einschlag/) | 256 × 256 px | 4 × 3 | 24 fps |

Jedes Raster verwendet gerades Alpha. Die Reihenfolge ist links nach rechts, danach die nächste Zeile. Im Spiel einmalig abspielen. Die GIFs dienen der Vorschau. Der Mündungsanker liegt bei (32, 64), der Einschlaganker bei (128, 128). Das Geschoss zeigt im Quellbild nach rechts. Die normierten Koordinaten für Start (20, 128) und Spitze beziehungsweise Ziel (236, 128) stehen in der JSON. Die feste Höhe der vollständigen Geschosskachel ist 1.3 m, die Einschlaggröße 0.9 m.

## Einbau in Godot

Für die schnelle Kugel das Sprite an der jüngsten Teilstrecke der sichtbaren Flugbahn mitführen. Die helle Spitze bei `ziel_anker` liegt vorn. In der Vorschau liegt zwischen Abschuss und Einschlag ein Abstand von zwei Bildern bei 24 fps.

Bei einer entlang der gesamten Bahn aufgespannten Spur ist die Quadbreite der Punktabstand mal 256 / 216. Die Höhe kommt separat aus feste_hoehe_m. Für Mündung und Treffer eignen sich einzelne kameraseitige Sprites. Schussrichtung, Shoot und Muzzle werden im Spiel von Claude verbunden. Die tatsächlichen Ziele und Trefferzeiten kommen aus dem bestehenden Kampfsystem.

Die drei Motive wurden mit der eingebauten Bildgenerierung erstellt und technisch zu Bildfolgen normalisiert. Die Kampfvorschauen verwenden die exakten WebP-Brücken und das Champion-GLB mit der vorhandenen Aktion Shoot von hinten oben bei 390 × 844 px. Die Sichtprüfung erfolgte an den Montagen. Der Einbau und Test in Godot stehen aus.
