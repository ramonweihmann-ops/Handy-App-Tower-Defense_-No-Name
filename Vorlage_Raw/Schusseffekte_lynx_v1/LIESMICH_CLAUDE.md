# Lynx · Scharfschützengewehr

Eine weiß-grüne Mündung mit kleinem hellem Rauchring, eine lange gerade Spur und ein konzentrierter Treffer. Ein längerer Funke zeigt im Spriteraster nach rechts.

[Übersicht](UEBERSICHT.png) · [Eiswelt animiert](LYNX_EISWELT_VORSCHAU.gif) · [Raumdock animiert](LYNX_RAUMDOCK_VORSCHAU.gif) · [Ablaufdaten](ABLAUF_LYNX.json)

## Formate

| Effekt | Einzelbild | Raster | Bildrate |
| --- | ---: | ---: | ---: |
| [Mündung](lynx_muendung/) | 128 × 128 px | 4 × 2 | 24 fps |
| [Geschoss](lynx_geschoss/) | 256 × 256 px | 4 × 2 | 24 fps |
| [Einschlag](lynx_einschlag/) | 256 × 256 px | 4 × 3 | 24 fps |

Jedes Raster verwendet gerades Alpha. Die Reihenfolge ist links nach rechts, danach die nächste Zeile. Im Spiel einmalig abspielen. Die GIFs dienen der Vorschau. Der Mündungsanker liegt bei (32, 64), der Einschlaganker bei (128, 128). Das Geschoss zeigt im Quellbild nach rechts. Die normierten Koordinaten für Start (20, 128) und Spitze beziehungsweise Ziel (236, 128) stehen in der JSON. Die feste Höhe der vollständigen Geschosskachel ist 1.25 m, die Einschlaggröße 1 m.

## Einbau in Godot

Die Spur nach dem Treffer entlang der sichtbaren Schusslinie aufspannen und schnell ausblenden. Den Einschlag entsprechend mitdrehen, damit der längere Funke hinter dem Trefferpunkt liegt. In der Vorschau beginnen Spur und Treffer gleichzeitig.

Bei einer entlang der gesamten Bahn aufgespannten Spur ist die Quadbreite der Punktabstand mal 256 / 216. Die Höhe kommt separat aus feste_hoehe_m. Für Mündung und Treffer eignen sich einzelne kameraseitige Sprites. Schussrichtung, Shoot und Muzzle werden im Spiel von Claude verbunden. Die tatsächlichen Ziele und Trefferzeiten kommen aus dem bestehenden Kampfsystem.

Die drei Motive wurden mit der eingebauten Bildgenerierung erstellt und technisch zu Bildfolgen normalisiert. Die Kampfvorschauen verwenden die exakten WebP-Brücken und das Champion-GLB mit der vorhandenen Aktion Shoot von hinten oben bei 390 × 844 px. Die Sichtprüfung erfolgte an den Montagen. Der Einbau und Test in Godot stehen aus.
