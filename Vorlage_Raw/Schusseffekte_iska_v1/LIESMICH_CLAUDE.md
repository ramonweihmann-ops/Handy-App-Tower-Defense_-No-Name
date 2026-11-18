# Iska · Energieblaster

Ein kurzer türkiser Mündungsimpuls, ein kompakter Energiebolzen und ein sparsamer türkiser Treffer. Die Vorschau zeigt drei aufeinanderfolgende Bolzen.

[Übersicht](UEBERSICHT.png) · [Eiswelt animiert](ISKA_EISWELT_VORSCHAU.gif) · [Raumdock animiert](ISKA_RAUMDOCK_VORSCHAU.gif) · [Ablaufdaten](ABLAUF_ISKA.json)

## Formate

| Effekt | Einzelbild | Raster | Bildrate |
| --- | ---: | ---: | ---: |
| [Mündung](iska_muendung/) | 128 × 128 px | 4 × 2 | 24 fps |
| [Geschoss](iska_geschoss/) | 256 × 256 px | 4 × 2 | 24 fps |
| [Einschlag](iska_einschlag/) | 256 × 256 px | 4 × 3 | 24 fps |

Jedes Raster verwendet gerades Alpha. Die Reihenfolge ist links nach rechts, danach die nächste Zeile. Im Spiel einmalig abspielen. Die GIFs dienen der Vorschau. Der Mündungsanker liegt bei (32, 64), der Einschlaganker bei (128, 128). Das Geschoss zeigt im Quellbild nach rechts. Die normierten Koordinaten für Start (20, 128) und Spitze beziehungsweise Ziel (236, 128) stehen in der JSON. Die feste Höhe der vollständigen Geschosskachel ist 1.55 m, die Einschlaggröße 0.8 m.

## Einbau in Godot

Den Bolzen als kurzen Spritestreifen an der aktuellen Geschossposition darstellen. `ziel_anker` markiert die Spitze. Bei Dauerfeuer die einzelnen Treffer lokal abspielen, damit sich zwischen den Gegnern keine durchgehende Leuchtfläche bildet. In der Vorschau liegen zwischen Abschuss und Einschlag vier Bilder bei 24 fps.

Bei einer entlang der gesamten Bahn aufgespannten Spur ist die Quadbreite der Punktabstand mal 256 / 216. Die Höhe kommt separat aus feste_hoehe_m. Für Mündung und Treffer eignen sich einzelne kameraseitige Sprites. Schussrichtung, Shoot und Muzzle werden im Spiel von Claude verbunden. Die tatsächlichen Ziele und Trefferzeiten kommen aus dem bestehenden Kampfsystem.

Die drei Motive wurden mit der eingebauten Bildgenerierung erstellt und technisch zu Bildfolgen normalisiert. Die Kampfvorschauen verwenden die exakten WebP-Brücken und das Champion-GLB mit der vorhandenen Aktion Shoot von hinten oben bei 390 × 844 px. Die Sichtprüfung erfolgte an den Montagen. Der Einbau und Test in Godot stehen aus.
