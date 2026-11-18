# Rollo · Panzerkanone

Kurzer Blitz mit flachem Gasstoß, Runde Kanonenkugel, Offener kupferfarbener Staubring.

[Übersicht](UEBERSICHT.png) · [Eiswelt](ROLLO_EISWELT_VORSCHAU.gif) · [Raumdock](ROLLO_RAUMDOCK_VORSCHAU.gif) · [Ablaufdaten](ABLAUF_ROLLO.json)

| Effekt | Einzelbild | Raster | Bildrate |
| --- | ---: | ---: | ---: |
| [Mündung](rollo_muendung/) | 128 × 128 px | 4 × 2 | 24 fps |
| [Geschoss](rollo_geschoss/) | 256 × 256 px | 4 × 2 | 24 fps |
| [Einschlag](rollo_einschlag/) | 256 × 256 px | 4 × 3 | 24 fps |

Die Blätter verwenden gerades Alpha. Bilder zeilenweise von links nach rechts abspielen. Die drei Bildfolgen sind als einmalig exportiert. Während der Flugphase Bild 1–4 in voller Stärke wiederholen. Nach dem Flug mit Bild 5–8 ausblenden. Die Bildfolgen mit voller Deckkraft der Textur abspielen. Mündungsanker (32, 64), Geschoss von (20, 128) nach (236, 128), Einschlaganker (128, 128). Die Geschosskachel ist fest 1.6 m hoch. Die Einschlagkachel hat eine Größe von 0.98 m.

## Einbau in Godot

Das Geschoss mit der Vorderkante an der tatsächlichen Geschossposition ausrichten. Der Bogen in der Vorschau dient der Darstellung. Staubring beim Treffer am Ziel abspielen. Rückstoß und Doppelwumms kommen aus dem vorhandenen Spielablauf. Impuls an der vorgesehenen Stelle der Aktion `Shoot` auslösen und die Mündung an `Muzzle` binden. Schussrichtung im Spiel ausrichten. Die Montage nutzt das Spielmodell und die vorhandene Abschussbewegung in der Kamera von hinten oben bei 390 × 844 px. Der Test in Godot steht aus.
