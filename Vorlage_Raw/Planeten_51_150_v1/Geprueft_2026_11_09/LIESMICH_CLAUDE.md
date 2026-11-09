# Planeten – geprüfte technische Lieferung vom 09.11.2026

Die Gestaltung wurde vom Nutzer freigegeben; die anschließende technische Entzerrung wurde ausdrücklich beauftragt. Alle 15 Spielbilder liegen als PNG/RGB in 780 × 1688 Pixeln vor. Die bestätigten Ausgangsbilder bleiben unter `originale/` erhalten.

**Einbau:** Bilder aus diesem Ordner verwenden, nicht die unentzerrten Originale und nicht die bisherigen Dateien aus dem übergeordneten Verzeichnis. Spielcode, vorhandene Dateien im Unterordner `korrigiert/` und die bisher aktiven Karten wurden nicht verändert. Claude soll die Übernahme im Spiel testen.

**Ozeanwelt:** `ocean_world_korrigiert.png` ist bytegleich mit Claudes bereits eingebauter korrigierter Fassung. Nicht durch `ocean_world.png` ersetzen.

**Messprüfung:** Sollpunkte OL (280,294), OR (500,294), UL (64,1158), UR (716,1158), Mitte x390. Neu abgelesene Ecken, ungefähr ±6 Pixel Messunsicherheit, stehen in `PRUEFBERICHT.json`. Größte abgelesene Eckabweichung: 11.7 Pixel. Alle Karten liegen einschließlich Messunsicherheit unter der später erlaubten Toleranz von 40 Pixeln. Das ursprüngliche Feinziel von ±6 Pixeln wird nicht für alle Karten als exakt erreicht ausgegeben.

**Bereiche:** Schutzmauer ungefähr y1134; Heldenbereich y1169–1410, Anzeigen y1410–1688 frei und flach. Materialfugen bleiben Teil der Grafik. Die Plattformkante liegt je nach Material wenige Pixel neben der Sollhöhe; konkrete Ablesungen stehen im Prüfbericht. Keine Figuren, Mauer oder UI eingebrannt.

**Wichtige technische Anpassungen:** Breitere Entwürfe wurden proportional auf das Zielformat skaliert und seitlich beschnitten. Dadurch sind Stationen am Bildrand teilweise stärker angeschnitten als im Designoriginal; keine Ovalstreckung durch einfaches Stauchen. Für Schrottwelt, Sporenwelt, Tempelplanet und Schwarzes Loch wurden wegen abgeschnittener Ränder die vollständigen vorhandenen Brücken und Unterkulissen derselben Welt maßlich angepasst; die neu bestätigten mittigen Portale im oberen Himmel bleiben erhalten. Die Originale zeigen die vollständige Designfreigabe und sind zusätzlich für spätere Bearbeitungen enthalten.

**Vorhandene Symbole:** Alle 15 Planetensymbole sind unverändert kopiert, PNG/RGBA 512 × 512 mit echtem Alpha.

## Dateien und Messung

| Nr. | Welt | Spielbild | Gemessene Ecken OL / OR / UL / UR | Größte Abweichung |
|---|---|---|---|---|
| 01 | Raumdock | [space_dock.png](space_dock.png) | [280, 294] / [500, 294] / [64, 1158] / [716, 1158] | 0.0 px |
| 02 | Eiswelt | [ice_world.png](ice_world.png) | [281, 294] / [499, 294] / [66, 1158] / [714, 1158] | 2.0 px |
| 03 | Wüstenaußenposten | [desert_outpost.png](desert_outpost.png) | [280, 294] / [500, 294] / [65, 1158] / [715, 1158] | 1.0 px |
| 04 | Lava-Asteroid | [lava_asteroid.png](lava_asteroid.png) | [280, 294] / [500, 294] / [66, 1158] / [714, 1158] | 2.0 px |
| 05 | Nebelportal | [nebula_portal.png](nebula_portal.png) | [281, 294] / [499, 294] / [68, 1158] / [712, 1158] | 4.0 px |
| 06 | Dschungelmond | [jungle_moon.png](jungle_moon.png) | [280, 294] / [500, 294] / [64, 1158] / [716, 1158] | 0.0 px |
| 07 | Ozeanwelt | [ocean_world_korrigiert.png](ocean_world_korrigiert.png) | [278, 293] / [501, 293] / [64, 1158] / [715, 1158] | 2.2 px |
| 08 | Kristallplanet | [crystal_planet.png](crystal_planet.png) | [280, 294] / [500, 294] / [65, 1158] / [715, 1158] | 1.0 px |
| 09 | Sturmriese | [storm_giant.png](storm_giant.png) | [280, 294] / [500, 294] / [59, 1156] / [721, 1156] | 5.4 px |
| 10 | Schrottwelt | [scrap_world.png](scrap_world.png) | [279, 300] / [501, 300] / [55, 1164] / [725, 1164] | 10.8 px |
| 11 | Wolkenstadt | [cloud_city.png](cloud_city.png) | [282, 294] / [498, 294] / [61, 1158] / [719, 1158] | 3.0 px |
| 12 | Sporenwelt | [spore_world.png](spore_world.png) | [280, 294] / [500, 294] / [68, 1158] / [712, 1158] | 4.0 px |
| 13 | Geistermond | [ghost_moon.png](ghost_moon.png) | [280, 294] / [500, 294] / [63, 1158] / [717, 1158] | 1.0 px |
| 14 | Tempelplanet | [temple_planet.png](temple_planet.png) | [280, 294] / [500, 294] / [69, 1158] / [711, 1158] | 5.0 px |
| 15 | Schwarzes Loch | [black_hole.png](black_hole.png) | [280, 294] / [500, 294] / [54, 1164] / [726, 1164] | 11.7 px |

`uebersicht.png` und `reihe_01.png` bis `reihe_03.png` zeigen ausschließlich diese technischen Fassungen. `pruefung/*_vergleich.png` zeigt Sollkontur in Rosa und die erneut abgelesene Kontur in Türkis; die Prüfminiaturen sind zur Ansicht halb so groß, sämtliche JSON-Koordinaten beziehen sich auf 780 × 1688.

**Laufzeittest noch offen:** Claude sollte jede Karte mit der vorhandenen Godot-Kamera, Mauer, Gegnerbahn und Heldenpositionen testen. Die Sicht- und Maßprüfung hier ersetzt diesen Test nicht. Keine Programmierung vorgenommen.

Herstellung: eingebaute Bildgenerierung für die freigegebenen Designs, anschließend ausdrücklich erlaubte lokale technische Bildverarbeitung. Keine neuen kostenpflichtigen Dienste.
