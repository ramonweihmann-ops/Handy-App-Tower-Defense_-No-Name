# Übergabe nach Freigabe am 08.11.2026

Die Gestaltung der gesamten Übersicht ist vom Nutzer freigegeben. Bitte die neuen Karten und Symbole übernehmen und im Spiel prüfen.

1. **Sturmriese:** `storm_giant.png` ist jetzt die bestätigte neue Fassung mit räumlich korrigierten Ringstationen. Die bisherigen Eckpunkte dieser Karte sind durch die aktuellen Werte in `PRUEFBERICHT.json` ersetzt. Vor einer Entzerrung die neue Bilddatei verwenden. Das zugehörige Prüfbild steht unter `pruefung/storm_giant_ecken.png`.
2. **Ozeanwelt:** Weiterhin `ocean_world_korrigiert.png` benutzen. Die von Claude bereits korrigierte und eingebaute Datei bleibt unverändert. Nicht erneut generieren und nicht durch das historische `ocean_world.png` ersetzen.
3. **Geometrie:** Für jede der zehn neuen Welten sind vier gemessene innere Fahrbahnecken in Pixeln vorhanden: oben links, oben rechts, unten links, unten rechts. Sollpunkte sind separat hinterlegt. Gemessene Werte sind Näherungen mit Messunsicherheit. Falls nötig entzerren, dann Gegnerweg, Mauerhöhe und Heldenplattform im Spiel prüfen. Die visuelle Freigabe ist kein Nachweis eines Godot-Tests durch ChatGPT.
4. **Symbole:** Alle fünfzehn `icon_*.png` liegen einzeln mit 512 × 512 Pixeln und transparentem Hintergrund bereit. Die zwei früher freigegebenen Symbole wurden nicht ersetzt.
5. **Kontrolle:** `uebersicht.png` zeigt alle fünfzehn Welten, `neue_10_welten_detail_v2.png` die zehn neuen Welten größer, `alle_15_symbole_v2.png` die Symbole und `PRUEFLISTE.md` die Reihenfolge 01–15. Die ursprünglichen fünf Schlachtfelder werden durch diese Lieferung nicht geändert.

Einzelbilder verwenden, nicht aus den Übersichten ausschneiden. Details und Herstellung: `LAYOUT_FUER_CLAUDE.md`, `BILDANWEISUNGEN.json`, `PRUEFBERICHT.json`. Kein Spielcode geändert.
