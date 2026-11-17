# Volta · Kettenblitz nach dem Spieltest

[Eiswelt animiert](VOLTA_EISWELT_VORSCHAU.gif) · [Raumdock animiert](VOLTA_RAUMDOCK_VORSCHAU.gif) · [Beide Brücken nebeneinander](UEBERSICHT.png)

## Änderungen für den nächsten Test

| Effekt | Fassung 2 |
| --- | --- |
| Blitzbogen | Rund 7 px weißer Kern und ein weicher, etwa 35 px breiter Leuchtsaum in der 256er-Kachel. Kräftiger Türkis-Violett-Kontrast. Feste Höhe der gesamten Texturkachel im Spiel 2,0 m. |
| Einschlag | 1,0 m Kachelbreite. Die Mitte bleibt transparent und kurze Funken laufen vom Ziel nach außen. |
| Mündungsblitz | Geprüfte Dateien aus Version 1 übernommen. |

## Dateien und Ausrichtung

- Jeder Effekt liegt als RGBA-Raster-PNG und JSON mit Ankern, Größe und 24 fps vor. Die Bilder werden zeilenweise von links nach rechts gelesen und einmalig abgespielt. Mündung und Bogen zeigen im Quellbild nach rechts. Der Einschlag ist auf dem Trefferpunkt zentriert.
- Start und Ziel des Blitzbogens liegen in der 256er-Kachel bei `(20, 128)` und `(236, 128)`. Bei einem aufgespannten Quad gilt `breite = punktabstand * 256.0 / 216.0`, mit Quadmitte zwischen den Endpunkten. Die Höhe aus `feste_hoehe_m` getrennt anwenden. Beim vorherigen Test gesetzte zusätzliche Vergrößerungen auf den neuen Sollwert abstimmen.
- Schussrichtung, Animation `Shoot` und Knoten `Muzzle` werden im Spiel von Claude verbunden. [ABLAUF_VOLTA.json](ABLAUF_VOLTA.json) enthält die Vorschauwerte und verweist auf das vorhandene Modell.
- Die Vorschauen verwenden die helle Eiswelt und zum Vergleich das Raumdock bei gleichem Bildmaßstab von 390 × 844. Der zweite Bogen erscheint nach 83 ms bei 68 % Alpha. Das ist nur die Staffelung der Darstellung. Zielauswahl und Schadenszeitpunkte kommen weiterhin aus dem Kampfsystem.

Die Vorschauen wurden als Montage geprüft. Der erneute Godot-Test auf der Eisbrücke steht aus.
