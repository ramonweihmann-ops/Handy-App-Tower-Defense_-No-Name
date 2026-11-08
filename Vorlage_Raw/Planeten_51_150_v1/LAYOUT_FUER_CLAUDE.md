# Planeten 51–150: freigegebene Gestaltungslieferung, Stand 08.11.2026

Acht weitere Schlachtfelder und dreizehn neue Symbole ergänzen die freigegebenen Dateien. Insgesamt stehen zehn neue Welten und fünfzehn Planetensymbole bereit. Alle Schlachtfelder sind PNG/RGB mit genau 780 × 1688 Pixeln. Die Symbole sind PNG/RGBA mit 512 × 512 Pixeln, echtem transparentem Hintergrund und etwa 8 % Außenrand. Farbraum sRGB.

## Übergabe nach visueller Freigabe

Der Nutzer hat die zusammengestellte Gestaltung für Claude freigegeben. `storm_giant.png` enthält jetzt die bestätigte Ringkorrektur: zwei klar getrennte Ringebenen, gemeinsame senkrechte Nabe, konzentrische Ringkonturen und radiale Tragarme mit stimmigen Anschlüssen. Die vier Fahrbahnecken wurden für diese neue Bildfassung erneut abgelesen; Werte aus der vorherigen Fassung nicht ungeprüft übernehmen. Die PNG-Abmessungen bleiben 780 × 1688 Pixel. Für neue Karten weiterhin gegebenenfalls entzerren und im Spiel prüfen; die visuelle Freigabe ersetzt keinen Godot-Test.

`uebersicht.png` zeigt jetzt alle 15 Welten mit Symbolen. Für die zehn neuen Welten gibt es zusätzlich `neue_10_welten_detail_v2.png`; `alle_15_symbole_v2.png` zeigt nur die Symbole. `PRUEFLISTE.md` ordnet die Nummern 01–15 den Bildern zu. Die fünf bisherigen Weltkarten erscheinen ausschließlich als Vergleich in der Übersicht und werden nicht ersetzt. Claudes `ocean_world_korrigiert.png` bleibt unverändert und ist weiterhin die aktive Ozean-Fassung.

## Bereits freigegebene Dateien

`jungle_moon.png`, `icon_jungle_moon.png` und `icon_ocean_world.png` bleiben unverändert. Für die Ozeanwelt **`ocean_world_korrigiert.png`** verwenden: Claude hat diese Datei bereits entzerrt und im Spiel eingebaut. Sie wurde weder verändert noch neu generiert. Das alte `ocean_world.png` bleibt aus Gründen der Nachvollziehbarkeit erhalten und soll die korrigierte Fassung nicht ersetzen. Die Gesamtübersicht zeigt die korrigierte Fassung.

## Gemessene Geometrie für Claude

Reihenfolge in dieser Tabelle und im Array: **oben links / oben rechts / unten links / unten rechts**. Koordinaten beziehen sich auf die gelieferten PNGs. Die Messung folgt der inneren Fahrbahnkante vor den seitlichen Lichtleisten. Abgelesen am Pixelraster, ungefähr ±4 Pixel Messunsicherheit. Der letzte Wert ist der größte euklidische Abstand eines gemessenen Eckpunkts vom Sollpunkt, nicht nur eine einzelne x- oder y-Abweichung.

| Datei | Welt | Level | Gemessene Ecken in Pixeln (OL / OR / UL / UR) | Größter Abstand zum Soll |
|---|---|---|---|---|
| jungle_moon.png | Dschungelmond | 51–60 | [280, 294] / [500, 294] / [66, 1164] / [715, 1164] | 6.3 px |
| ocean_world_korrigiert.png | Ozeanwelt | 61–70 | [278, 293] / [501, 293] / [64, 1158] / [715, 1158] | 2.2 px |
| crystal_planet.png | Kristallplanet | 71–80 | [280, 279] / [500, 279] / [66, 1164] / [715, 1164] | 15.0 px |
| storm_giant.png | Sturmriese | 81–90 | [251, 297] / [529, 297] / [36, 1133] / [743, 1133] | 37.5 px |
| scrap_world.png | Schrottwelt | 91–100 | [249, 296] / [528, 296] / [38, 1131] / [743, 1131] | 38.2 px |
| cloud_city.png | Wolkenstadt | 101–110 | [276, 264] / [502, 264] / [77, 1163] / [698, 1163] | 30.3 px |
| spore_world.png | Sporenwelt | 111–120 | [279, 286] / [501, 286] / [61, 1164] / [719, 1164] | 8.1 px |
| ghost_moon.png | Geistermond | 121–130 | [267, 285] / [528, 285] / [43, 1164] / [739, 1164] | 29.4 px |
| temple_planet.png | Tempelplanet | 131–140 | [279, 287] / [501, 287] / [54, 1162] / [725, 1162] | 10.8 px |
| black_hole.png | Schwarzes Loch | 141–150 | [250, 278] / [527, 278] / [59, 1127] / [720, 1127] | 34.0 px |

Die einzelnen Werte stehen unter `fahrbahn_ecken_px` und `fahrbahn_ecken_array` in `PRUEFBERICHT.json`. Die Sollpunkte sind getrennt hinterlegt: OL `(280,294)`, OR `(500,294)`, UL `(64,1158)`, UR `(716,1158)`. Mitte `x = 390`, Mauer ungefähr `y = 1134`, Plattform ab `y = 1169`, ruhiger Anzeigenbereich ab `y = 1410`. Unter `pruefung/` zeigen die acht neuen Prüfbilder die Sollkontur in Magenta und die gemessene Kontur in Türkis. Prüfbilder niemals als Hintergrund einsetzen.

Die Brücken sind visuell gerade und werden gleichmäßig breiter. Die acht neuen Karten sind zur Implementierung geliefert; Claude kann kleine Abweichungen anhand der vier Ecken entzerren. Die Maßwerte sind keine Behauptung pixelgenauer Deckung mit der Schablone. Neue Karten wurden von ChatGPT nicht in Godot getestet. Nach dem Entzerren die Kanten, die Mauerhöhe und den Übergang zur Plattform im Spiel prüfen. Die beiden bereits eingebauten Welten sind laut Nutzer freigegeben.

## Symbole

Dateien: `icon_space_dock.png`, `icon_ice_world.png`, `icon_desert_outpost.png`, `icon_lava_asteroid.png`, `icon_nebula_portal.png`, `icon_jungle_moon.png`, `icon_ocean_world.png`, `icon_crystal_planet.png`, `icon_storm_giant.png`, `icon_scrap_world.png`, `icon_cloud_city.png`, `icon_spore_world.png`, `icon_ghost_moon.png`, `icon_temple_planet.png`, `icon_black_hole.png`.

Die fünf bisherigen Schlachtfelder werden nicht ersetzt; ergänzt werden nur ihre Symbole. Symbole proportional skalieren, ungefähr 60 logische Punkte breit einsetzen; keinen violetten Hintergrund aus der Übersicht mit übernehmen. Die zwei freigegebenen Symbole bleiben unverändert.

## Herstellung und Kontrolle

Nur eingebaute Bildgenerierung im bestehenden Konto verwendet. Keine weiteren kostenpflichtigen Dienste. Jede Karte und jedes Symbol wurde einzeln erstellt. Die neuen Karten sind Bearbeitungen von `space_dock.png` mit dem freigegebenen Dschungelmond als Geometrie-/Stilreferenz. Wolkenstadt und Schwarzes Loch erhielten zusätzlich eine Breitenkorrektur über die Bildgenerierung. Technische Formatierung: einheitliche Skalierung und Beschnitt, keine perspektivische Entzerrung. Alle tatsächlichen Bildanweisungen und Formatierungswerte stehen in `BILDANWEISUNGEN.json`.

`uebersicht.png` zeigt alle fünfzehn Welten mit zugehörigen Symbolen; die zusätzliche Detailübersicht zeigt die zehn neuen Welten. Alle Dateimaße, PNG-Modi, Transparenz und Symbolränder wurden technisch geprüft. Der Spielcode bleibt unverändert. Bei den Bilddateien wird ausschließlich die bestätigte neue Ringfassung unter `storm_giant.png` übernommen; alle anderen bereits vorhandenen Karten und Symbole bleiben unverändert.
