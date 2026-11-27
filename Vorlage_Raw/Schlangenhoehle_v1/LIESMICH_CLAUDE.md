# Schlangenhöhle – Schlachtfeld und Planetensymbol

Stand: 27.11.2026. Repository: `Handy-App-Tower-Defense_-No-Name`, Branch `claude/amazing-hypatia-yl59v4`.

Der Nutzer hat das Höhlendesign und Symbol freigegeben und anschließend die präzise geometrische Bildkorrektur ausdrücklich erlaubt. Diese Lieferung übernimmt den freigegebenen Entwurf; die weiteren, verworfenen Neuzeichnungen sind nicht enthalten.

## Dateien

- `snake_cave.png`: fertiges Schlachtfeld, 780 × 1688 Pixel, RGB, ohne Transparenz und ohne eingezeichnete Prüflinien.
- `icon_snake_cave.png`: Planetensymbol, 512 × 512 Pixel, RGBA, echter Alphakanal. Goldene Schlange um dunklen Asteroiden mit violetten Kristallen.
- `MASSKONTROLLE.png`: Schlachtfeld mit eingeblendeten Sollkanten, Mittelpunktlinie und Plattformgrenzen. Nur zur Kontrolle verwenden.
- `MASSPRUEFUNG.json`: Sollkoordinaten, gemessene Kantenstichproben, Formate, Alphabereich und SHA-256-Prüfsummen.
- `UEBERSICHT.png`: Gesamtbild und Symbol, zusätzlich bei 60 Pixeln auf hellem und dunklem Grund.
- `BILDANWEISUNGEN.txt`: Gestaltungsanweisungen und Beschreibung der abschließenden Maßkorrektur.

## Maßprüfung

Koordinaten beziehen sich immer auf die unbeschnittene Datei mit 780 × 1688 Pixeln, Ursprung oben links.

| Stelle | Soll | Sichtprüfung der fertigen Datei |
|---|---|---|
| Oben links | (280, 294) | etwa (280, 294), Ablesegenauigkeit ±3 px |
| Oben rechts | (500, 294) | etwa (500, 294), Ablesegenauigkeit ±3 px |
| Unten links | (64, 1158) | etwa (64, 1158), Ablesegenauigkeit ±3 px |
| Unten rechts | (716, 1158) | etwa (716, 1158), Ablesegenauigkeit ±3 px |
| Wegmitte | x = 390 | geometrisch gesetzt |
| Plattformbeginn | y = 1169 | Übergang entsprechend ausgerichtet |
| Ruhiger Anzeigenbereich | y = 1410–1688 | frei von Figuren und Effekten |

Die Sollseiten sind gerade: links `x = 280 - (y - 294) / 4`, rechts `x = 500 + (y - 294) / 4`, jeweils für y = 294 bis 1158. Die Goldleisten liegen außen. Der Abstand zwischen Brückenende und Plattform beträgt 11 Pixel.

Zusätzlich zur Sichtprüfung wurden die inneren Goldkanten an elf Höhen zwischen y = 298 und y = 1140 anhand ihrer Farbgrenze abgelesen. Größte Abweichung dort: 2,5 Pixel; damit innerhalb der geforderten ±6 Pixel. Das sind Messungen der sichtbaren gemalten Kontur, nicht nur ein Wiederholen der vorgegebenen Koordinaten. Eine geglättete Bildkante ist kein mathematisch scharfer Einzelpixel; die geometrische Zuordnung selbst liegt auf den Sollwerten.

Symbol: Alpha reicht von 0 bis 255. Der gesamte nicht vollständig transparente Bereich liegt innerhalb (46, 51) bis (472, 471), rechte/untere Grenze exklusiv. Der sichtbare Hauptkörper liegt deutlich weiter innen. Das Motiv wurde nur gleichmäßig verkleinert und auf transparenter Fläche zentriert.

## Einbau in Godot

1. `snake_cave.png` über denselben Hintergrundpfad und dieselbe Skalierung wie die vorhandenen 780 × 1688-Schlachtfelder einsetzen. Keine zusätzliche Verschiebung, perspektivische Verzerrung oder individuelle Beschneidung anwenden.
2. Die vorhandene Weg- und Plattformgeometrie beibehalten: Fahrbahn endet bei y = 1158; Heldenbereich beginnt bei y = 1169. Gegner, Mauer, Helden und Oberfläche bleiben separate Spielelemente.
3. Das Symbol mit erhaltenem Seitenverhältnis und Alphakanal in die Planetenauswahl einbinden. Dunkle Vorschauhintergründe sind nicht Teil der PNG-Datei.
4. Die Prüfbilder nicht als Spieltexturen verwenden. Sie enthalten bewusst Linien und Beschriftungen.
5. Beim Einbau noch im Spiel prüfen: dunkle Schlangengegner müssen sich vor dem grauvioletten Fahrbahnbelag abheben; obere Kopfleiste und untere Anzeigen überlagern nur die vorgesehenen ruhigen Bereiche.

## Herstellung und Grenzen

Illustrationen mit der eingebauten Bildgenerierung erstellt, keine zusätzlichen kostenpflichtigen Dienste. Die abschließende geometrische Korrektur des freigegebenen Bildes erfolgte nach ausdrücklicher Erlaubnis rechnerisch und mit geglätteter Abtastung. Fahrbahn und Anschluss zur Plattform wurden ausgerichtet, angrenzende Bildbereiche kontinuierlich angepasst, damit keine Schnittkanten entstehen. Die Figurendekoration wurde nicht neu erfunden.

Format-, Alpha-, Kanten- und Sichtprüfung sind erfolgt. Ein Godot-Lauf oder ein Test mit tatsächlich bewegten Gegnern wurde in diesem Auftrag nicht durchgeführt. Die Dateien liegen als Vorlagen bereit; die Spieldateien wurden nicht automatisch ersetzt.
