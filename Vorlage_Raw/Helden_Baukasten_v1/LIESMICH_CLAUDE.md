# Heldenbildschirm – wiederverwendbarer Baukasten v1

Der Heldenbildschirm wurde am 03.11.2026 gestalterisch freigegeben. Dieses Paket liefert seine Bausteine einzeln. **Der freigegebene Gesamtentwurf muss nicht zerschnitten werden.**

## Direkt verwendbare Dateien

| Ordner / Datei | Verwendung |
|---|---|
| `hintergrund/helden_hintergrund.png` | Leerer vollständiger Weltraumhintergrund ohne Figuren, Beschriftungen, Karten oder Navigation |
| `figuren/*.png` | Sieben einzelne transparente 512er-Freistellungen: Lynx, Dusty Jo, Iska, Margot, Volta, Brocken und die gesperrte Schleimmutter |
| `ui/*.svg` | 26 editierbare textfreie UI-Bauteile: vier Kartenfarben, Goldrahmen, Portraitmaske, Kartenkörper, grüne/rote Bereichsbanner, Zählerfläche, Stufen-/Zeitplaketten, Schaltflächen, Fortschritt, Navigation, Plus, Hinweis und Haken |
| `ui_png/*.png` | Dieselben 26 Bauteile gerastert, falls PNG-Texturen für den Einbau praktischer sind |
| `symbole/*.png` | Fünf bereits freigegebene Navigationssymbole und die Uhr, unverändert aus Icons_v1 übernommen |
| `LAYOUT_UND_BEISPIELDATEN.json` | Ebenenfolge, Beispielzustände, Referenzkoordinaten und Zuordnung der Dateien |
| `helden_design_freigegeben.png` | Maßgeblicher freigegebener Gestaltungsentwurf, nur zum Vergleichen |
| `helden_modular_vorschau.png` | Tatsächlich aus diesen Einzeldateien aufgebaute Zusammenbauprüfung |

Alle Figuren-PNGs haben echte Transparenz, sRGB und mindestens 32 Pixel freien Rand. Die Karten, Namen, Stufen, Kartenmengen, Zeitwerte und Knopftexte sind **nicht in die Einzelmotive eingebrannt**. Die Maße der übrigen PNGs und die Prüfsummen stehen in `DATEIPRUEFUNG.json`.

## Empfohlener Aufbau

1. Hintergrund als eigener bildschirmfüllender Hintergrund.
2. Bereichsbanner als textfreie Fläche, darüber je ein Label für Überschrift und Anzahl.
3. Pro Karte: farbiger Kartenhintergrund, Figur als eigener TextureRect, Goldrahmen darüber. Bei Bedarf die beigefügte Portraitmaske zum runden Begrenzen benutzen. Figur passend innerhalb des Rahmens skalieren, statt aus einem Gesamtbild neue Ausschnitte zu speichern.
4. Stufenplakette, Name, Fortschritt und Meldungen als eigene Elemente. Text immer aus den tatsächlichen Spieldaten erzeugen. Für das Beispiel sind dieselben sieben Einträge und Werte wie in der Freigabe hinterlegt.
5. Normale, hervorgehobene, gedrückte und gesperrte Schaltflächen sind getrennt enthalten. Labels darüberlegen und die vorhandenen Spielaktionen anschließen.
6. Navigation am unteren Bildschirmrand verankern. `nav_aktiv` nur hinter Helden, der gemeinsame goldgelbe Kampfknopf bleibt in der Mitte.

Für skalierbare Rahmen, Kartenkörper und Knöpfe eignen sich beispielsweise NinePatchRect beziehungsweise StyleBoxTexture. In der Layoutdatei sind Randvorschläge angegeben; die Rundungen beim Strecken erhalten. Die SVGs verwenden einfache Formen und Verläufe ohne externe Bilder oder Schriftabhängigkeiten. Die gerasterten PNGs vermeiden unterschiedliche SVG-Renderer als Ursache für Abweichungen.

Brocken wird als farbige Grundfigur geliefert. Für den noch gesperrten Zustand dieselbe Figur im Spiel entsättigen und etwas abdunkeln; die Zusammenbauprüfung zeigt das. Die Schleimmutter ist dagegen bereits als graue Sperrfigur geliefert. In diesem Paket sind keine neuen Kampfmodelle, Skelette oder Animationen enthalten.

## Originalgestaltung und Nachbau

Der Bildentwurf besitzt keine ursprünglichen getrennten Ebenen. Deshalb wurden die sieben Figuren anhand der freigegebenen Gestaltung einzeln neu freigestellt und die UI-Flächen als bearbeitbare Vektorbauteile nachgebaut. Die Zusammenbauprüfung ist **kein pixelidentischer Ebenenexport** des generierten Bildes. Der freigegebene Gesamtentwurf bleibt für Typografie, Materialanmutung und Feinabstände die optische Referenz.

Die Zusammenbauprüfung nutzt eine Systemschrift. Beim Einbau die bereits lizenzierte Spielschrift verwenden; Schriftdateien werden nicht neu verteilt. Leichte Glanzeffekte, Interaktionen, Schaltzustände und das konkrete responsive Layout setzt das Spiel um. Das Paket ändert keine Freischaltregeln, Preise oder Kartenstände im Spiel.

## Vorschau und Quellen

`vorschau.html` setzt die Einzelbilder als reine Gestaltungsansicht zusammen; die Schaltflächen lösen keine Käufe aus. Die Python- und Node-Hilfsskripte sind optionale Quellen zur erneuten Bauteilerzeugung und Vorschau. Für den eigentlichen Einbau sind sie nicht nötig. Die SVG-Rasterung benötigt bei einer erneuten Ausführung das Paket `sharp`; die bereits gerasterten PNGs sind ohne diese Abhängigkeit verwendbar.

Figuren und Hintergrund: eingebaute Bildgenerierung mit den bereits freigegebenen Projektvorlagen. UI-Flächen: neu erstellte editierbare Vektorgrafiken. Navigationssymbole: vorhandenes Projektpaket Icons_v1. Keine weiteren Meshy-Credits oder Adobe-Dienste verwendet. Keine fremden Symbol- oder Schriftpakete hinzugefügt; rechtliche Exklusivität wird nicht behauptet.

Die Dateien wurden auf Lesbarkeit, Transparenz und Vollständigkeit geprüft und aus den Einzelbauteilen zusammengesetzt. Ein Test in der laufenden Godot-App steht noch aus. Die neu entworfene Tech-Werft und Talente sind getrennte Designarbeiten und werden hier nicht als bereits eingebaut oder spielmechanisch freigegeben ausgegeben.
