# Fritzi · Gemalter Flammenstoß

Die Lieferung ersetzt die klobigen Feuerkugeln durch zusammenhängende Feuerzungen und einen offenen Bodenkranz. Erzeugt mit der eingebauten Bildgenerierung; keine kostenpflichtigen Zusatzdienste. Die Spielwerte bleiben unverändert.

[Übersicht](UEBERSICHT.png) · [Eiswelt](FRITZI_EISWELT_VORSCHAU.gif) · [Raumdock](FRITZI_RAUMDOCK_VORSCHAU.gif) · [Ablauf](ABLAUF_FRITZI.json)

| Teil | Kachel | Raster | Bilder | Anker in Pixeln |
| --- | --- | --- | --- | --- |
| fritzi_muendung | 128 × 128 | 4 × 2 | 8 | (32, 64) |
| fritzi_geschoss | 256 × 256 | 4 × 2 | 8 | Start (20, 128), Ziel (236, 128) |
| fritzi_einschlag | 256 × 256 | 4 × 3 | 12 | Mitte (128, 128) |

Je Ordner liegen das PNG-Bildblatt, die JSON-Beschreibung und eine animierte GIF-Vorschau. Alle Bildfolgen laufen mit 24 Bildern/s, zeilenweise von links nach rechts. PNGs verwenden RGBA mit geradem Alpha. Die Vorschau-GIFs wiederholen sich nur zum Anschauen; `loop: false` gilt für die Effekte im Spiel. Keine zusätzliche Abschwächung der Deckkraft. Die Transparenz der Ausblendbilder bleibt erhalten.

## Einbau

- Den Impuls an die vorhandene Aktion `Shoot` koppeln. Die Mündung am Knoten `Muzzle` verankern und nach rechts gezeichnete Texturen in Zielrichtung drehen.
- `darstellung: bogen` wie bei Kalle auswerten. Die Strecke zwischen den beiden Ankern exakt von der Düse bis zum Trefferpunkt spannen. Die Zielkante darf nicht hinter dem Ziel weiterlaufen. Die feste Kachelhöhe von 2,0 m ist eine grafische Startempfehlung, kein neuer Spielwert.
- Die ersten vier Strahlbilder sind der volle Stoß; bei längeren Stößen nur diese wiederholen. Bilder 5–8 blenden aus. Normalerweise alle acht Bilder einmal abspielen. Kein fliegendes Projektil aus dem Strahl machen.
- Den Einschlag bodennah um den vorhandenen Trefferkreis legen. Die leere Mitte freihalten und keine deckende Fläche darunter setzen. Die Kachel enthält bereits eine flache perspektivische Ellipse. Bei kameraorientierten Sprites diese nicht ein zweites Mal flach drücken. Falls stattdessen eine Bodenprojektion verwendet wird, die Perspektivkorrektur passend vornehmen.
- `groesse_m: 3.0` beim Einschlag dient lediglich als Vorschauwert. Die tatsächliche Größe aus Fritzis bestehendem Flächenradius ableiten, einschließlich der vorhandenen Superfähigkeit. Dabei den transparenten Kachelrand berücksichtigen. Keine Änderung an Radius, Schaden, Brenndauer oder Schussrate.

## Prüfung und Vorschau

Die Kampfvorschauen sind Montagen mit Fritzis vorhandenem Spielmodell und dessen `Shoot`-Bewegung aus der Kamera von hinten oben. Mündungspositionen stammen aus `Muzzle`. Beide Schauplätze werden bei 390 × 844 Pixeln mit zwei Gegnern im Trefferkreis und voller Texturdeckkraft gezeigt. Der Flammenkranz wird auch über die Gegner gezeichnet, damit eine mögliche Verdeckung sichtbar ist. Diese Vorschauen sind keine Aufnahme aus Godot; den abschließenden Test mit der tatsächlichen Trefferkreis-Skalierung bitte im Spiel durchführen.

Die Motive wurden mit eingebauter Bildgenerierung erstellt und technisch in das vorhandene Rasterformat gepackt. Die verwendeten Bildanweisungen liegen in `BILDANWEISUNGEN.txt`.
