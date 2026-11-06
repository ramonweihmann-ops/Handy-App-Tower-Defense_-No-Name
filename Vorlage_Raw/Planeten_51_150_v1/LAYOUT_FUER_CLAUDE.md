# Neue Planeten – erste Abstimmungsrunde

Diese Lieferung enthält zunächst die zwei beauftragten Testwelten mit ihren Symbolen. Die acht weiteren Welten und die Symbole der bisherigen fünf Welten folgen nach der Abstimmung. Keine Änderungen am Spielcode.

**Wichtiger Prüfstatus:** Dschungelmond: geprüfte Kanten ungefähr innerhalb der gewünschten ±6 Pixel, am unteren Abschluss im Grenzbereich. Ozeanwelt: Gestaltungsentwurf, Maßprüfung NICHT bestanden; Abweichungen von etwa 20–35 Pixeln. Die Ozeanwelt vor produktivem Einbau geometrisch korrigieren. Nicht als fertig maßhaltige Karte behandeln. Beide Bilder sind noch nicht in Godot getestet.

| Datei | Welt | Level | Format |
|---|---|---|---|
| jungle_moon.png | 06 – Dschungelmond | 51–60 | 780 × 1688, PNG, RGB |
| ocean_world.png | 07 – Ozeanwelt | 61–70 | 780 × 1688, PNG, RGB |
| icon_jungle_moon.png | Planetensymbol Dschungelmond | 51–60 | 512 × 512, PNG, RGBA, transparenter Hintergrund |
| icon_ocean_world.png | Planetensymbol Ozeanwelt | 61–70 | 512 × 512, PNG, RGBA, transparenter Hintergrund |

## Verbindliche Zielgeometrie

Ursprung links oben, Bezug 780 × 1688 Pixel. Fahrbahntrapez: oben `(280,294)` bis `(500,294)`, unten `(64,1158)` bis `(716,1158)`. Mitte `x = 390`. Gerade Seitenkanten: `x_links = 280 − (y − 294)/4`, `x_rechts = 500 + (y − 294)/4`.

Mauer im Spiel ungefähr bei `y = 1134`; sie gehört nicht zum Hintergrund. Brückenende bei `y = 1158`. Heldenfläche `y = 1169–1410`, Anzeige-/Fähigkeitsfläche `y = 1410–1688`, Kopfleiste `y = 0–110`. Die eigentliche Spielfläche bleibt frei von Figuren, Mauer und Bedienelementen.

## Erzeugung und Prüfung

Die Bilder wurden mit der eingebauten Bildgenerierung als Bearbeitung von `space_dock.png` erstellt. Die übrigen Referenzen dienten als Stil-, Geometrie- und Einbauvorlage. Eine Geometriekorrektur verwendet zusätzlich ein Prüfbild mit überlagerten Ziellinien. Die finalen Bilder enthalten keine Hilfslinien. Technische Formatierung: ausschließlich einheitliche Skalierung und Beschnitt, keine perspektivische Verformung.

Die Ergebnisse der Maßprüfung und verbleibende Abweichungen stehen je Bild in `PRUEFBERICHT.json`. Eine Sichtprüfung am Schablonenbild ersetzt keinen Test mit Godots tatsächlicher Kamera und Skalierung. Die Prüfabbildungen unter `pruefung/` dienen nur zur Kontrolle; sie sind keine Spielhintergründe.

Die Symbole haben mindestens ungefähr 8 % transparenten Außenrand. Beim Einbau das Seitenverhältnis erhalten. `uebersicht.png` enthält ausschließlich eine verkleinerte Kontrollansicht; daraus keine Spielflächen ausschneiden.

## Noch ausstehend nach Freigabe

Kristallplanet (71–80), Sturmriese (81–90), Schrottwelt (91–100), Wolkenstadt (101–110), Sporenwelt (111–120), Geistermond (121–130), Tempelplanet (131–140), Schwarzes Loch (141–150). Insgesamt sind danach zehn Schlachtfelder und fünfzehn Planetensymbole vorgesehen. Die bisherigen fünf Karten werden durch diese Lieferung nicht ersetzt.
