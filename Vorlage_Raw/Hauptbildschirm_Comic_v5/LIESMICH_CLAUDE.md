# Freigegebener Hauptbildschirm – funktionale Übergabe für Claude

Stand 09.11.2026. Die zuletzt gezeigte Ein-Kugel-Fassung ist vom Nutzer mit „viel besser“ bestätigt. Das freigegebene Bild und der Planet werden hier nicht neu gestaltet.

## Empfohlener Einbau: genau eine Hintergrunddatei ersetzen

1. `godot_einbau/main_bg.webp` nach `game/ui_mock/home/main_bg.webp` kopieren.
2. Godot die geänderte WebP-Textur neu importieren lassen. Die vorhandene `.import`-Zuordnung und das bestehende Layout beibehalten, keinen fremden `.godot`-Cache kopieren.
3. Kein weiteres Planetenobjekt darüberlegen. Der neue Hintergrund enthält bereits genau eine Kugel samt horizontalem Ring und den bereinigten Bereich des alten Planeten.

Die Datei ist passend zum aktuellen Repository-Hintergrund **1170 × 2532 Pixel, RGB, verlustfreies WebP**. `main_bg.png` hat exakt dieselben Pixel und dient als PNG-Alternative. Die vorliegenden Bilddaten wurden nicht aus dem Gesamtentwurf blind übernommen: Nur die freigegebene Austauschregion wurde in die aktuelle Spieldatei übertragen. Außerhalb dieser Region bleiben die dekodierten bisherigen Bildpixel identisch.

## Was im bestehenden Spiel weiterarbeitet

Der aktuelle `game/ui_mock/home/layout.json` verwendet 390 × 844 logische Punkte, Exportmaßstab 3 und `states.main.bg = main_bg.webp`. `MockView` lädt dieses Bild unter `_live_layer`, `_text_layer` und `_btn_layer`. Rechts liegen echte Antippflächen; Werte, Hinweispunkte und Levelauswahl kommen weiter aus den bisherigen Daten und Skripten. `HomeScreen` zeichnet den Levelpfad samt Helden, Knoten und Sternen darüber.

Für den empfohlenen Einbau **keine** Button-Rechtecke, Texte, IDs, Ereignisse, Live-Bilder, Weltenauswahl, Kopfleiste oder Navigation verändern. Auch die bisher aus dem Hintergrund übernommenen statischen Symbole bleiben erhalten. Insbesondere `Tägliche Belohnung`, `Glücksrad`, `Missionen`, `Shop`, `Spielmodi`, Weltwechsel, Spielen und die fünf Reiter behalten ihre bestehenden Funktionen.

`hauptbildschirm_aktuell_v5.png` mit 852 × 1846 Pixeln ist die bestätigte **Gestaltungsreferenz**, kein Ersatz für die funktionale UI und kein Ersatz für die maßgenaue WebP-Datei im obigen Einbauweg.

## Alternative: Bildüberlagerung auf dem bisherigen Hintergrund

Nur wenn ein Dateiaustausch nicht gewünscht ist: `godot_einbau/ringkorrektur_overlay_1170x2532.png` als transparentes `TextureRect` im selben lokalen Bereich wie `_bg` direkt über `_bg`, aber unter den Live-, Text- und Button-Ebenen einsetzen. `mouse_filter = Control.MOUSE_FILTER_IGNORE`, `expand_mode = TextureRect.EXPAND_IGNORE_SIZE`, `stretch_mode = TextureRect.STRETCH_SCALE`. Position und Größe müssen bei jeder Größenänderung exakt denen von `_bg` entsprechen. Die rechte Kante am bestehenden Bildschirmrahmen beschneiden.

Dieses Overlay ist ein vollständiger lokaler **Pixelersatz**, nicht bloß ein zweiter Planet: Seine deckenden Hintergrundteile entfernen die alte Kugel und die alten Ringreste. Bestehende UI-Pixel sind an den geschützten Stellen ausgespart. Die Überlagerung des Overlays auf den alten Hintergrund rekonstruiert die mitgelieferte neue Hintergrunddatei pixelgleich.

Nur einen Einbauweg wählen. Die Überlagerung nicht zusätzlich auf den bereits korrigierten Hintergrund legen. `ringkorrektur_overlay_852x1846.png` ist dieselbe Änderung im Entwurfsraster und gehört ausschließlich zu diesem Raster.

## Skalierung und Einzelobjekt

Die vorhandene `MockView._layout()`-Berechnung bleibt maßgeblich: `s = min(Breite/390, Höhe/844)`, Versatz mittig für den verbleibenden Rand. Nicht unabhängig auf die volle Fensterbreite skalieren; das verschiebt den Planeten gegenüber den Schaltflächen auf anderen Seitenverhältnissen.

`ringplanet_einzeln.png` ist eine zusätzliche transparente Quelle für einen späteren komplett getrennten Ebenenaufbau. Sie ist kein direkter Hintergrundersatz. Im 852 × 1846-Entwurf lag das gleichmäßig skalierte Original bei (398,335), Maßstab 0,4903078677309008, gerundete Rastergröße 753 × 502. Dafür muss der alte Planet zuvor entfernt und die vorhandene UI anschließend wieder darübergezeichnet werden. Die bestehende `hauptbildschirm_ohne_ringplanet.png` enthält bereits statische UI-Anteile und ist ebenfalls kein allgemein UI-freier Weltraumhintergrund.

## Prüfung und Abnahme im Spiel

Technisch geprüft: Dateimaße und Transparenz, exakte Rekonstruktion aus Overlay und bisheriger Spieldatei, identische PNG-/WebP-Pixel und unveränderte Pixel außerhalb der Austauschregion. Einzelheiten stehen in `EINBAU.json` und `DATEIPRUEFUNG.json`.

Nach dem Einbau durch Claude: Hauptbildschirm bei 390 × 844 und mindestens einem abweichenden Seitenverhältnis prüfen, jeden rechten Aktionsknopf sowie Spielen und die Reiter anklicken, Weltwechsel und aktuelle Werte prüfen. Der Planet darf weder Antippflächen abfangen noch ein zweites Mal erscheinen. Der Status des separaten Godot-Dateitests steht in `DATEIPRUEFUNG.json`; ein vollständiger Durchlauf des Spielprojekts wird hier nicht behauptet.

Keine neuen Bildgenerierungen, keine zusätzlichen Dienste, keine Änderung am Spielcode in diesem Auftrag. Die Lieferung liegt ausschließlich unter `Vorlage_Raw/` zur Übernahme durch Claude.
