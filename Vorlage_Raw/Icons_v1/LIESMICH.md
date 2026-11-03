# Symbole und Logos – Space-Comic v1

Stand: 03.11.2026. Für das Projekt „Station am Wurmloch“. Grundlage sind die beiden vom Nutzer übergebenen Symbolübersichten, der freigegebene Hauptbildschirm Comic v4 sowie die neuen Erfolgsmeldungen für Gold, Edelsteine und Energie.

## Inhalt

38 einzeln verwendbare Standbilder, vier Drehbögen, vier kleine GLB-Hilfsmodelle, eine beschriftete Übersicht sowie technische Prüfungen und Gestaltungsanweisungen. Die Benutzeroberfläche und die Spieldaten wurden nicht verändert.

| Gruppe | Dateien, jeweils mit Endung `.png` |
|---|---|
| Währungen und Werte | `icon_gold`, `icon_gems`, `icon_energy`, `icon_stars`, `icon_pass`, `icon_cards`, `icon_trophy`, `icon_league`, `icon_medal` |
| Bestehende Truhentypen | `chest_wood`, `chest_iron`, `chest_silver`, `chest_gold`, `chest_epic` |
| Zusätzliche Truhenvorschläge | `chest_platinum`, `chest_cosmic` |
| Booster | `booster_luftangriff`, `booster_medipack`, `booster_zeitlupe`, `booster_kuppel`, `booster_munition` |
| Kampf | `icon_core`, `icon_shield`, `icon_skull`, `icon_clock`, `icon_crown` |
| Aktionen | `act_daily`, `act_wheel`, `act_missions`, `act_shop`, `act_modes` |
| Reiter | `nav_shop`, `nav_heroes`, `nav_battle`, `nav_upgrades`, `nav_base` |
| Ergänzung aus der Übersicht | `act_settings`, `act_profile` |

`nav_shop` und `act_shop` sind identisch; ebenso `nav_heroes` und `icon_cards`. Beide Namen sind vorhanden, damit die im Spiel vorgesehenen Verwendungen direkt zugeordnet werden können. Der goldene `icon_trophy` und der blaue `act_modes` sind bewusst unterschiedliche Motive.

## Bildformat und Einbau

- Standbilder: 512 × 512 Pixel, PNG mit 8 Bit je RGBA-Kanal, also 32 Bit und echter Transparenz; eingebettetes sRGB-Profil.
- Sichtbares Motiv maximal 448 × 448 Pixel, mindestens 32 Pixel transparenter Rand. Truhen und stehende Gebäude-/Sockelsymbole haben ihre Standlinie bei y=470; der letzte belegte Pixel liegt bei y=469.
- Ohne eingebrannte Texte, Mengen, rote Hinweispunkte, umgebende Kacheln oder äußere Leuchteffekte. Kleine Lichtflächen auf dem Gegenstand gehören zum Material.
- Ein Symbol pro Datei. `UEBERSICHT.jpg` ist ausschließlich zur Sichtprüfung gedacht; sie enthält auch Vorschaudarstellungen bei 20 Pixeln auf hellem und dunklem Grund.
- In Godot die PNGs als Texturen einsetzen. Mengen, Beschriftungen, Kacheln, Ringe, Benachrichtigungspunkte, Pulsieren und Sammelbewegungen erzeugt das Spiel. Bei stark verkleinerter Darstellung lineare Filterung und bei Bedarf Mipmaps am tatsächlichen Bildschirm prüfen.
- Holztruhe „bereit“ verwendet dasselbe Motiv `chest_wood.png`; den Bereitschaftseffekt zeichnet das Spiel. Halboffene/offene Truhen sind laut Vorgabe ein späterer Schritt und hier nicht enthalten.

## Vier Drehungen

`spin_gold.png`, `spin_gems.png`, `spin_energy.png`, `spin_stars.png`: jeweils 1024 × 768 Pixel, vier Spalten und drei Reihen. Zwölf Zellen à 256 × 256, zeilenweise von links oben nach rechts unten, Bild 0 = Vorderseite, dann 30-Grad-Schritte. Für 1,2 Sekunden pro Umlauf mit 10 Bildern pro Sekunde abspielen. Nach Bild 11 folgt wieder Bild 0; das identische 360-Grad-Bild ist nicht doppelt enthalten. Größe, Mittelpunkt und Ausschnitt bleiben innerhalb einer Drehfolge unverändert.

Diese Bögen wurden aus tatsächlichen dicken Symbolkörpern gerendert, nicht durch seitliches Stauchen eines Standbildes. Gold, Blitz und Stern sind einfache konturierte Extrusionen; der Kristall hat gefaltete Vorder- und Rückflächen. Alle verwenden eine eingebettete Motivtextur. Es sind einfache Renderkörper, keine aufwendig modellierten Edelstein- oder Münzskulpturen. Das erhält den bereits freigegebenen Bildstil bei sehr geringem Aufwand. Lichtreflexe der Motivtextur sind eingebrannt.

Die optionalen Dateien unter `modelle/` sind dafür gedacht, dass Claude bei Bedarf selbst weitere Größen oder Drehansichten rendert. Im eigentlichen Spiel reichen die PNGs. Die GLBs haben Y oben, Vorderseite +Z, Ursprung in der Mitte, eine eingebettete 512-Textur, weniger als 2.000 Dreiecke und die Animation `Spin` mit einer vollen Y-Drehung in 1,2 Sekunden. Keine Laufzeit-3D-Symbole erforderlich.

Unter `quellen_3d/` liegen die vier Motivtexturen, vereinfachte Konturen und das Blender-Erzeugungsskript. Diese Quellen dienen zur Nachbearbeitung; Texturdateien dort sind keine zusätzlichen Spielsymbole. Die rohe Bildgenerierung und verworfene Vorversuche sind nicht Teil dieses Lieferpakets.

## Designentscheidungen

Die freigegebenen Währungsformen und die Motive des Hauptbildschirms wurden als Gestaltung beibehalten und für den Einzelgebrauch freigestellt beziehungsweise anhand der Vorlage sauber reproduziert. Das sind keine bloßen Ausschnitte aus dem vollständigen Hauptbildschirm. Für die anderen Symbole wurden entsprechende neue Einzelmotive mit der eingebauten Bildgenerierung erstellt. Es wurden keine kommerziellen Modellierungsdienste oder Adobe-Abos verwendet.

Platintruhe und Kosmostruhe sind zusätzliche Gestaltungsvorschläge. Dafür wurden keine neuen Preise, Inhalte oder Freischaltbedingungen festgelegt. Weitere Booster können später mit derselben Gestaltungsvorlage ergänzt werden. Neue Währungen wurden nicht erfunden.

Die Champion-Rundbilder behalten ihren freigegebenen Stil und sind in diesem Paket nicht erneut enthalten. Laut Vorgabe werden neue Porträts nur bei einem Stilwechsel benötigt; ein zusätzlicher Glanz kann einheitlich vom Spiel darübergelegt werden, ohne zwölf weitere Porträtvarianten zu pflegen.

## Quelle, Nutzung und Prüfung

Neu für dieses Projekt erstellte Motive: eingebaute Bildgenerierung mit den vom Nutzer bereitgestellten beziehungsweise bereits freigegebenen Projektvorlagen; örtlich erstellte Blender-Symbolkörper. Keine fremden Symbol- oder Modellpakete wurden eingebaut. Das Paket ist für die Verwendung im Spiel einschließlich einer kommerziellen Veröffentlichung bestimmt. Es wird keine fremde CC0-Lizenz oder rechtliche Exklusivität behauptet; die Erstellung ändert die geltenden Nutzungsbedingungen der verwendeten Dienste nicht.

`BILDANWEISUNGEN.json` dokumentiert die Gestaltung. `DATEIPRUEFUNG.json` enthält Maße, Transparenz, Motivgrenzen und SHA-256-Prüfsummen. `DREHUNG_3D_PRUEFUNG.json` beschreibt die Hilfsmodelle. Eine Prüfung im laufenden Godot-Spiel ist noch erforderlich; sie ist nicht durch die Dateiprüfung ersetzt.
