# Drei freigegebene Trefferanimationen

Diese Bildfolgen wurden vom Nutzer im direkten Vergleich mit Champions und zwei Gegnern auf Eisbrücke und Raumdock freigegeben. Die gelieferten Sprite-Blätter sind gegenüber dieser Vorschau unverändert. Nur die Trefferanimationen ersetzen; vorhandene Mündungen, Geschosse, Waffen und Abschussbewegungen behalten.

## Dateien und Zuordnung

| Champion | Bildfolge | Zieldatei im Spiel | Gestaltung |
| --- | --- | --- | --- |
| Brocken | `brocken/brocken_einschlag_sheet.png` | `game/fx/brocken_explosion.webp` und `.json` | Kurzer Zündblitz, aufbrechende orange Feuerzungen, rascher Zerfall |
| Rollo | `rollo/rollo_einschlag_sheet.png` | `game/fx/rollo_einschlag.webp` und `.json` | Kompakter gold-kupferner Aufprall mit nach außen fliegenden Splittern |
| Nova | `nova/nova_einschlag_sheet.png` | `game/fx/nova_einschlag.webp` und `.json` | Violette Energie zieht sich zusammen und bricht als kurzer Impuls auf |

Die jeweilige JSON liegt neben dem Blatt. Produktionsformat: 1024 × 768 Pixel, RGBA mit geradem Alpha, 4 Spalten × 3 Reihen, zwölf Kacheln à 256 × 256, zeilenweise links nach rechts, 24 fps, einmalig, Gesamtdauer 0,5 Sekunden. Anker jeweils `[0.5, 0.5]`. Beim WebP-Export Alpha erhalten, möglichst verlustfrei. Keine schwarzen Hintergründe einrechnen.

## Wichtige Einbaueinstellungen

1. **Volle Texturdeckkraft:** `deckend: true`. Die alte Brocken-JSON hatte diese Angabe nicht und wurde von `FxSprite` zusätzlich auf 80 Prozent abgeschwächt. Keine zusätzliche additive Überblendung oder Weißfläche ergänzen.
2. **Zeitablauf der Freigabe bewahren:** `speed: 1.0`, `tempo: 1.0`, `loop: false`. Im bisher geprüften Code nutzt `battle.gd::explode()` für Brocken `speed: 1.15`; `Projectile.play_impact()` verwendet für ungerichtete Effekte pauschal `speed: 1.5`; Nova hatte `tempo: 0.7`. Diese Aufrufwerte für die neuen Treffer anpassen, damit die vorgesehenen 24 fps wirksam sind. Kein globaler Wechsel für andere Effekte.
3. **Ausblenden:** Die Bildfolgen enthalten bereits Zerfall und Ausblenden. Für diese drei Aufrufe `fade: 0.0` verwenden, um die späten Bilder nicht durch das zusätzliche Standard-Ausblenden von `FxSprite` vorzeitig zu entfernen. Letztes Bild wird nach Ablauf entfernt.
4. **Ausrichtung:** Die neue Vorschau zeigt die Einschläge ungedreht zur Kamera, daher `gerichtet: false`. Keine Geschossrichtung als `dir` übernehmen. Bestehende gerichtete Bögen nicht zusätzlich laufen lassen. Die Freigabe betrifft keine auf den Boden projizierte Fläche.
5. **Größe abstimmen:** `groesse_m` ist ein Startwert, kein im Spiel bestätigtes Maß. Die freigegebenen vollständigen Effektkacheln waren in der 390 × 844 Vorschau 110 Pixel (Brocken), 88 Pixel (Rollo), 98 Pixel (Nova) groß. `FxSprite.SCALE = 1.2` und explizite `width`-Werte berücksichtigen: `explode()` setzt derzeit `max(2.5, radius * 1.45)`, Nova `max(1.6, radius * 2.0)` und überschreibt damit die JSON-Größe. Nicht blind nur die JSON ändern. Visuelle Größe vom Schadensradius unterscheiden und bei großen Radien begrenzen, falls sonst Gegner verdeckt werden.
6. **Einmaliger Treffer:** Am tatsächlichen Auftreffpunkt auslösen, nicht bei jedem Bild der Aktion `Shoot`. Die Vorschauflugzeit ist keine neue Spielregel. Nova erhält einen einmaligen Trefferimpuls; Dauer, Sog, Verlangsamung und Schaden des Schwerkraftfelds unverändert lassen.
7. **Gemeinsame Explosion:** `battle.explode()` wird auch von explosiven Zusatztreffern verwendet, etwa Iskas Leuchtspur. Diese erben beim Austausch die neue Brocken-Grafik. Bei ihnen kompakte visuelle Größe prüfen; keine zweite zusätzliche Explosion erzeugen. Spielbalance bleibt unverändert.

## Vergleich und Prüfung

- [Alle drei auf der Eisbrücke](VERGLEICH_ice_world.gif)
- [Alle drei auf dem Raumdock](VERGLEICH_space_dock.gif)
- Je Champion: `ice_world.gif` und `space_dock.gif` mit vollständigem 390 × 844 Bild.
- `PRUEFBILD_*.png`: Standbilder einer geöffneten Trefferphase.
- `PRUEFUNG.json`: Dateimaße, Alpha-Prüfung und Prüfsummen der freigegebenen Sprite-Blätter.

Die Vorschauen sind Montagen mit den vorhandenen Spielmodellen und Abschussbewegungen, Spielgeschossen, zwei Gegnern und Originalbrücken. Sie sind kein aufgezeichneter Godot-Test. Der kurze Auftakt darf den zentralen Gegner für wenige Bilder überlagern; danach wird die Mitte frei. Auf beiden Brücken und bei gleichzeitigem Dauerfeuer mehrerer Champions im Spiel prüfen: Treffer klar sichtbar, Gegner nach der Spitzenphase erkennbar, keine quadratischen Kachelränder, keine alten Effekte zusätzlich.

Jede Bildfolge wurde einzeln mit der eingebauten Bildgenerierung erstellt; anschließend erfolgten technischer Kachelexport und Vorschau-Montage. Keine zusätzlichen kostenpflichtigen Dienste. Dieses Paket ändert keine Spieldateien selbst.
