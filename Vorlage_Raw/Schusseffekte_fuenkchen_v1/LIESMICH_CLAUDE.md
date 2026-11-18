# Fünkchen · Sternenatem

Kurzer Atemstoß, Lavendelfarbenes Sternenband, Kleine Sternfunken.

[Übersicht](UEBERSICHT.png) · [Eiswelt](FUENKCHEN_EISWELT_VORSCHAU.gif) · [Raumdock](FUENKCHEN_RAUMDOCK_VORSCHAU.gif) · [Ablaufdaten](ABLAUF_FUENKCHEN.json)

| Effekt | Einzelbild | Raster | Bildrate |
| --- | ---: | ---: | ---: |
| [Mündung](fuenkchen_muendung/) | 128 × 128 px | 4 × 2 | 24 fps |
| [Geschoss](fuenkchen_geschoss/) | 256 × 256 px | 4 × 2 | 24 fps |
| [Einschlag](fuenkchen_einschlag/) | 256 × 256 px | 4 × 3 | 24 fps |

Die Blätter verwenden gerades Alpha. Bilder zeilenweise von links nach rechts abspielen. Die drei Bildfolgen sind als einmalig exportiert. Während der Flugphase Bild 1–4 in voller Stärke wiederholen. Nach dem Flug mit Bild 5–8 ausblenden. Die Bildfolgen mit voller Deckkraft der Textur abspielen. Mündungsanker (32, 64), Geschoss von (20, 128) nach (236, 128), Einschlaganker (128, 128). Die Geschosskachel ist fest 1.7 m hoch. Die Einschlagkachel hat eine Größe von 0.87 m.

## Einbau in Godot

Den Sternenatem wie den vorhandenen Strahl entlang der Schusslinie spannen. Die Zielmarke sitzt am Ende der sichtbaren Linie. Sternfunken an den vom Spiel gemeldeten Treffern abspielen. Impuls an der vorgesehenen Stelle der Aktion `Shoot` auslösen und die Mündung an `Muzzle` binden. Schussrichtung im Spiel ausrichten. Die Montage nutzt das Spielmodell und die vorhandene Abschussbewegung in der Kamera von hinten oben bei 390 × 844 px. Der Test in Godot steht aus.
