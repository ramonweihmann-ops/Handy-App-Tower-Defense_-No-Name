# Station am Wurmloch · App-Symbol v1

Drei Varianten zur Auswahl, auf Basis von `game/ui/start/ladebildschirm_comic.webp` und den vorhandenen Champion-Porträts. Noch keine Variante als endgültiges Spielsymbol eingesetzt.

[Große Auswahl](AUSWAHL.png) · [Alle Größen und Masken](UEBERSICHT.png)

| Variante | Inhalt | Einschätzung |
| --- | --- | --- |
| A | Dusty Jo als große Kopf-und-Schultern-Büste vor dem Wurmloch | Empfehlung für die stärkste Lesbarkeit bei 48 Pixeln. Hut, Gesicht und rotes Halstuch sind klar erkennbar. |
| B | Pinkes Monster aus dem Ladebildschirm, Dusty kleiner vorn | Markantes Monster als Hauptmotiv. Dusty ist bei 48 Pixeln klein, Hut und Gesicht bleiben unterscheidbar. |
| C | Dusty vorn, Iska links und Brocken rechts dahinter | Die Gruppe ist erkennbar; einzelne Gesichtszüge sind bei 48 Pixeln weniger deutlich als bei A. |

## Dateien je Variante

- `A_1024.png`, entsprechend B/C: 1024 × 1024, RGB, vollständig deckend, bis an die Kanten gestaltet. Keine eingebauten abgerundeten Ecken, kein Text.
- `A_192.png`, entsprechend B/C: direkt aus der jeweiligen 1024er Fassung verkleinert, RGB.
- `A_vordergrund_432.png`, entsprechend B/C: 432 × 432, RGBA, ausschließlich Figuren. Tatsächlicher transparenter Hintergrund, einschließlich der Zwischenräume.
- `A_hintergrund_432.png`, entsprechend B/C: 432 × 432, RGB, ausschließlich Wurmloch und Weltraum. Alle drei verwenden denselben Hintergrund, damit die Auswahl vergleichbar bleibt.

## Einbau nach Auswahl

Die 1024er Fassung als vollständiges quadratisches Symbol verwenden. Für ein adaptives Symbol Vordergrund und Hintergrund derselben Variante getrennt übernehmen, zentriert und ohne zusätzliche Beschneidung der 432er Ebenen. Die wichtigsten Inhalte liegen innerhalb des geforderten mittleren Kreises mit 288 Pixeln Durchmesser um (216,216). Tatsächlich liegen sämtliche sichtbaren Vordergrundpixel innerhalb dieses Kreises; siehe `PRUEFUNG.json`.

Die normale 1024er Komposition entspricht dem zentralen 288er Sichtbereich der adaptiven Ebenen. Sie wurde aus den hochauflösenden Motiven zusammengesetzt, nicht aus der kleinen 432er Datei hochskaliert. Bei einer Vorschau durch bloßes Überlagern der kompletten 432er Ebenen wirken die Figuren entsprechend kleiner: dort ist der zusätzliche äußere Spielraum noch sichtbar. Nicht mit einer Vergrößerung des Vordergrunds ausgleichen.

Die konkreten Android-Exportzuweisungen bitte beim Einbau im Projekt setzen und auf einem Gerät prüfen. Bestehendes `game/icon.svg` und Exportkonfiguration wurden nicht ersetzt. Keine vorgefertigten Masken in Produktionsdateien einrechnen; die Masken sind nur in der Prüfübersicht enthalten.

## Sichtprüfung

Die Übersicht enthält alle drei Varianten und das aus `game/icon.svg` rasterisierte bisherige Symbol. Jeweils 48, 72 und 96 Pixel, Kreis und abgerundetes Quadrat, auf hellem und dunklem Verlaufshintergrund in stilisierten Handy-Startbildschirmen. Bei 100 Prozent Bildansicht sind die angegebenen Pixelgrößen unverändert; verkleinerte Chat-Vorschauen zeigen sie kleiner. Es handelt sich um Layoutsimulationen, nicht um echte Android-Bildschirmaufnahmen.

Alle drei Motive bleiben unter den beiden Masken erkennbar, ohne Verlust von Gesichtern oder Kopfbedeckungen. Variante A ist bei kleinster Darstellung am ruhigsten. Keine Schrift in den eigentlichen Symbolen; Beschriftungen stehen nur in Übersichten und Dokumentation.

Die Figuren und das Wurmloch stammen aus der eingebauten Bildgenerierung. Technische Ebenenmontage, Größenexport, Rasterisierung des vorhandenen SVG und Prüfübersichten wurden anschließend erstellt. Sehr schwaches Alpha-Rauschen an transparenten Rändern wurde beim Export entfernt. Keine zusätzlichen kostenpflichtigen Dienste. Die verwendeten Bildanweisungen stehen in `BILDANWEISUNGEN.txt`.
