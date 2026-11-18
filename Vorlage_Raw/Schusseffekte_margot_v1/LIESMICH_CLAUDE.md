# Margot · Piratenflinte

Doppelblitz mit kleinem Rauchstoß, Bündel aus drei Schrotkugeln, Kurze Funken.

[Übersicht](UEBERSICHT.png) · [Eiswelt](MARGOT_EISWELT_VORSCHAU.gif) · [Raumdock](MARGOT_RAUMDOCK_VORSCHAU.gif) · [Ablaufdaten](ABLAUF_MARGOT.json)

| Effekt | Einzelbild | Raster | Bildrate |
| --- | ---: | ---: | ---: |
| [Mündung](margot_muendung/) | 128 × 128 px | 4 × 2 | 24 fps |
| [Geschoss](margot_geschoss/) | 256 × 256 px | 4 × 2 | 24 fps |
| [Einschlag](margot_einschlag/) | 256 × 256 px | 4 × 3 | 24 fps |

Die Blätter verwenden gerades Alpha. Bilder zeilenweise von links nach rechts abspielen. Die drei Bildfolgen sind als einmalig exportiert. Während der Flugphase Bild 1–4 in voller Stärke wiederholen. Nach dem Flug mit Bild 5–8 ausblenden. Die Bildfolgen mit voller Deckkraft der Textur abspielen. Mündungsanker (32, 64), Geschoss von (20, 128) nach (236, 128), Einschlaganker (128, 128). Die Geschosskachel ist fest 1.45 m hoch. Die Einschlagkachel hat eine Größe von 0.8 m.

## Einbau in Godot

Die drei Schrotkugeln bilden ein Bündel pro Sprite. Dieselbe Bildfolge für jedes vom Spiel erzeugte Bündel im Fächer wiederverwenden. Impuls an der vorgesehenen Stelle der Aktion `Shoot` auslösen und die Mündung an `Muzzle` binden. Schussrichtung im Spiel ausrichten. Die Montage nutzt das Spielmodell und die vorhandene Abschussbewegung in der Kamera von hinten oben bei 390 × 844 px. Der Test in Godot steht aus.
