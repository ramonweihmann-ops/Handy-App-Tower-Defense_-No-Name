# Schusseffekt für Voltas Blitzpistole

[Animierte Kampfvorschau](VOLTA_KAMPF_VORSCHAU.gif) · [Abschuss in Nahaufnahme](VOLTA_ABSCHUSS_DETAIL.gif) · [Übersicht der drei Einzelteile](UEBERSICHT.png)

Dieser Vorschlag zeigt einen schlanken Kettenblitz mit hellem Kern, kühlem blau-violettem Rand und kurzen Funken am Kontaktpunkt. Die Kampfvorschau montiert die Raumdock-Brücke, zwei Schleimlinge und die gerenderte Aktion `Shoot` aus Voltas vorhandenem GLB. Der Oberkörper gibt beim Abschuss kurz nach, der Waffenarm hebt sich leicht und kehrt in die Zielhaltung zurück. Der Blitz startet pro Bild am projizierten Knoten `Muzzle`.

## Abschuss synchronisieren

Die Dateipfade, Aktion und Vorschauwerte sind auch in [ABLAUF_VOLTA.json](ABLAUF_VOLTA.json) hinterlegt. Der Modellpfad ist relativ zu diesem Ordner.

Die vorhandene Volta-Animation enthält `Shoot` mit 0,40 s Laufzeit. Den Clip ab Beginn der visuellen Schussaktion einmal abspielen und gleichzeitig den Mündungsblitz starten. Den Weltpunkt für Mündung und ersten Blitz während des sichtbaren Bogens am animierten `Muzzle` abfragen. Der Rückstoß erreicht seinen Höchstwert nach etwa 67 ms und klingt dann ab. Zielauswahl und Schadenszeitpunkte liefert das vorhandene Kampfsystem. [Volta-GLB mit der Aktion Shoot](https://github.com/ramonweihmann-ops/Handy-App-Tower-Defense_-No-Name/blob/11cd6b5aa1fe945f48aa746ea9d5fbf15e5c09ed/Vorlage_Raw/Helden_Posen_v1/volta/volta.glb)

| Effekt | Einsatz | Einzelbild | Raster | Dauer bei 24 fps |
| --- | --- | ---: | ---: | ---: |
| [Mündungsblitz](volta_muendung/) | Am Knoten `Muzzle` starten. Ausrichtung zum ersten Ziel. | 128 × 128 px | 4 × 2 | 0,33 s |
| [Blitzbogen](volta_blitzbogen/) | Einen Bogen pro Verbindung zwischen Mündung und Ziel beziehungsweise zwischen zwei Zielen zeichnen. | 256 × 256 px | 4 × 2 | 0,33 s |
| [Einschlag](volta_einschlag/) | Auf dem Trefferpunkt des Gegners zentrieren. | 256 × 256 px | 4 × 3 | 0,50 s |

## Einbau in Godot

- Aus dem PNG-Raster je Effekt `SpriteFrames` mit `AtlasTexture`-Regionen anlegen. Die Bilder laufen zeilenweise von links nach rechts. Die PNGs haben gerades Alpha, und die Farbe im weichen Lichtrand ist bereits gemalt. Die JSON nennt Größe, Anker und 24 Bilder pro Sekunde. Im Spiel wird einmalig abgespielt. Die GIFs dienen der Vorschau.
- Mündung und Einschlag als zur Kamera gewandte Sprites verwenden. Der Anker stammt aus der JSON und ist auf die Größe eines Einzelbilds normiert, mit Ursprung links oben. Bei zentriertem Sprite lautet der Versatz in Texturpixeln `(Vector2(0.5, 0.5) - anker) * einzelbildgroesse`. Für den Mündungsblitz zeigt die Textur von ihrem Anker nach rechts.
- Für den Blitzbogen ein kameraseitig ausgerichtetes Quad zwischen den sichtbaren Endpunkten aufspannen. Im Einzelbild liegt der Start bei `(20, 128)`, das Ziel bei `(236, 128)`. Bei 256 px Einzelbildbreite ist die Quadbreite daher `punktabstand * 256.0 / 216.0`. Quadmitte ist der Mittelpunkt der Verbindung. Die Höhe separat skalieren, damit ein langer Blitz schlank bleibt. Der Vorschlag für die Höhe der gesamten Texturkachel steht als `feste_hoehe_m` in der JSON. Alternativ im vorhandenen 2D-Effekt-Layer beide Punkte in Bildschirmkoordinaten projizieren und dieselbe Rechnung anwenden.
- Die laufende Kampfberechnung liefert die tatsächlichen Ziele. Bei einer Kette das Blitzbogen-Sprite pro Verbindung erneut starten. In der Vorschau folgt der zweite Bogen mit zwei Bildern Abstand, rund 83 ms. Für den ersten Bogen gilt Alpha 1,0, für den zweiten 0,68. Der zweite Einschlag läuft mit Alpha 0,72 bei etwa 82 % der Größe des ersten. So bleiben Folgetreffer gegenüber dem ersten Blitz erkennbar gedämpft. Die Werte sind visuelle Vorgaben für den Entwurf.

Erster Anschlussversuch im Spiel noch offen. In der Spielkamera besonders die Lesbarkeit der dünnen Linien auf der hellen Brückenbeleuchtung prüfen.
