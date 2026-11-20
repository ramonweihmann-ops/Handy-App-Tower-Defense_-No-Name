# Talente – freigegebene Überarbeitung

Diese Fassung ersetzt die vier zu rundlichen Entwürfe aus `Vorlage_Raw/Talente_v2/` und ergänzt das ausdrücklich freigegebene neue Munitionslager. Für den Einbau ausschließlich die fünf Einzel-PNGs aus diesem Ordner verwenden.

| Datei | Zuordnung | Motiv und Farbvorlage |
| --- | --- | --- |
| tal_funkenherz.png | Fünkchen · Superfähigkeiten laden schneller | Facettierter vierzackiger rosa Stern #ff9ae0, kleiner goldener Funke #ffd34d |
| tal_werkzeugkiste.png | Pip · Booster laden schneller | Türkiser Maulschlüssel #8fe8e8, gerade Kanten und erkennbare Materialtiefe |
| tal_bollwerk.png | Rollo · mehr Schild | Orangefarbener Schild #ffc070, Rand #d8661a, dunkle Metallbänder und vier Nieten |
| tal_schwerefeld.png | Nova · Gegner laufen langsamer | Violetter gerichteter Wirbel #d0a8ff mit heller Mitte |
| tal_munitionslager.png | Bestehendes Talent Munitionslager | Offene grüne Munitionskiste, drei goldene Patronen mit kupferfarbenen Spitzen; vordere Kistenwand verdeckt die Patronen plausibel |

Die Hex-Werte sind Farbvorlagen; Schattierung, Konturen und Glanzlichter verwenden zusätzliche Farbtöne. Alle fünf Symbole enthalten das kleine Plus bereits. Keine Spielwerte ändern.

## Einbau in Godot

Die fünf Dateien jeweils der gleichnamigen Textur in `game/ui/upgrades_v2/` zuordnen. Falls der bestehende Ablauf WebP verwendet, mit erhaltenem Alphakanal und möglichst verlustfrei umwandeln. Keine weiteren Talent-Symbole ersetzen.

- Produktionsdateien: 256 × 256 Pixel, RGBA, echter transparenter Hintergrund.
- Vollständige quadratische Kachel auf etwa 44 × 44 Punkte skalieren, Seitenverhältnis erhalten, nicht am sichtbaren Motiv beschneiden.
- Mindestens 20 Pixel freier Rand sind geprüft. Die Motivbereiche stehen in `PRUEFUNG.json`.
- Keine zusätzliche Plus-Markierung, keinen grünen Farbfilter und keine zusätzliche Kontur darüberlegen.
- Vorhandene grüne Karten bleiben bestehen; Grün ist nur in den Vergleichsbildern enthalten.
- `uebersicht.png` zeigt die fünf neuen Fassungen und die sechs bisherigen Stilreferenzen bei 44 und 88 Pixeln. Das alte Munitionslager in der unteren Referenzreihe dient nur dem Vergleich.
- `auswahl.png` zeigt alle fünf Liefermotive größer. Übersichten nicht als Spieltextur verwenden.

## Prüfung und Herkunft

Maße, Farbmodus, vollständige Transparenz und Rand wurden für alle fünf Produktionsdateien geprüft. SHA-256-Prüfsummen dokumentieren die gelieferten Fassungen. Der abschließende Test in der tatsächlichen Talentseite in Godot steht aus.

Jedes Motiv wurde einzeln mit der eingebauten Bildgenerierung erstellt, nicht aus einer Übersicht ausgeschnitten. Anschließend erfolgten Größenexport und Zusammenstellung der Vorschauen. Keine zusätzlichen kostenpflichtigen Dienste. Die bereits freigegebenen Einzelbilder wurden beim Verpacken nicht neu generiert. Spieldateien wurden hier nicht verändert.
