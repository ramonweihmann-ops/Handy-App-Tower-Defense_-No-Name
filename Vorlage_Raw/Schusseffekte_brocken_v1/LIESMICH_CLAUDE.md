# Brocken · Gemalte Rakete

Gerundetes rotes Gehäuse mit dunklen Metallringen, schmalem türkisem Energieeinsatz, kurzer Heckflamme und kompaktem Rauch. Die Freigabe von `game/fx/brocken_explosion.webp` gilt weiterhin. Beide Vorschauen nutzen die unveränderte Explosion und das Spielmodell von Brocken mit `Shoot` und `Muzzle`.

[Übersicht](UEBERSICHT.png) · [Eiswelt](BROCKEN_EISWELT_VORSCHAU.gif) · [Raumdock](BROCKEN_RAUMDOCK_VORSCHAU.gif) · [Ablaufdaten](ABLAUF_BROCKEN.json)

| Effekt | Einzelbild | Raster | Wiedergabe |
| --- | ---: | ---: | --- |
| [Mündung](brocken_muendung/) | 128 × 128 px | 4 × 2 | Einmal am Werferende |
| [Geschoss](brocken_geschoss/) | 256 × 256 px | 4 × 2 | Bilder 1–4 im Flug wiederholen, Bilder 5–8 zum Ausblenden |

Beide Blätter verwenden 24 Bilder/s, gerades Alpha und die Reihenfolge links nach rechts, dann nächste Zeile. Im Spiel volle Deckkraft verwenden. Die Mündung bei (32, 64) verankern und nach vorne zum Ziel richten. Beim Geschoss liegen der Anfang bei (20, 128) und die Spitze bei (236, 128). Der projizierte Raketenkörper nimmt 155 der 256 Kachelpixel ein. Den Körper auf etwa 1,2–1,5 m einpassen. Aus 1,35 m sichtbarer Körperlänge ergibt sich für die gesamte Bildkachel eine effektive Kantenlänge von rund 2,23 m. Den Skalierungsfaktor von `FxSprite` einrechnen. Das Seitenverhältnis der quadratischen Kachel beibehalten.

## Einbau in Godot

`darstellung: rakete` in `projectile.gd` vor dem bisherigen 3D-Raketenzweig als gemaltes, nicht gestrecktes Sprite behandeln. Die Sprite-Spitze an der Geschossposition verankern, `schleife_bilder: 4` auswerten und den Ablauf ab Bild 5 beim Ausblenden abspielen. Ausschließlich die neue Mündung vorwärts ausrichten. Dazu in `hero.gd` für diese Fassung den bisherigen 3D-Rückstoß und die Richtungsumkehr beim Mündungsbild umgehen. Drehung weiter aus der vorhandenen flachen Flugbahn über `set_dir` ableiten. `battle.explode` löst beim Treffer weiterhin die vorhandene Explosion aus. Die Lieferung enthält Grafikdateien und Vorschauen. Der Einbau in Godot steht aus.
