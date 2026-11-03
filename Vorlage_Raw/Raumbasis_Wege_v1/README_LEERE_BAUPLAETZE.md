# Raumbasis mit Wegen und leeren Bauplätzen

Stand: 03.11.2026. Ergänzung zu `Raumbasis_Wege_v1`, ohne bestehende Gebäude oder Dateien zu ersetzen.

## Hintergrund

`raumbasis_leere_bauplaetze.png`: 724 × 2172 Pixel, RGB-PNG, vollständig deckend. Drei Spalten mit zehn Reihen, insgesamt 30 leere Bauplätze. Gebäude und Kontrollnummern sind entfernt. Wege, unterer Brückeneingang, Außenfelsen sowie Weltraumkulisse bleiben in der bestehenden Anordnung erhalten.

Die Karte wurde aus `raumbasis_mit_wegen_vorschau.png` mit der integrierten Bildbearbeitung erstellt. Die Platzanordnung und der Bildausschnitt wurden visuell verglichen; es handelt sich um eine bearbeitete Illustration, keine pixelidentische Ebenenrekonstruktion. Vorhandene Gebäudeanker weiterverwenden und die Eingangskanten beim Einbau visuell fein ausrichten.

## Einbau

- Diese PNG als unterste statische Hintergrundebene verwenden.
- Freigestellte Gebäude separat darüber platzieren. Gesperrte Gebäude ausblenden; darunter bleibt der leere Bauplatz sichtbar.
- Keine rechteckigen Gebäudeausschnitte mit altem Boden oder Nummernschild darüberlegen. Gebäude benötigen echte transparente Konturen.
- Die PNG enthält das gesamte sichtbare Wegenetz bis Platz 30. Gebäude können unabhängig davon eingeblendet werden. Wenn zusätzlich einzelne zukünftige Wege verschwinden sollen, werden dafür separate Weggrafiken oder Masken benötigt; die Wege dieser PNG sind fest eingemalt.

## Korrigierte Freischaltung

Die folgende Regel ersetzt die frühere Gleichsetzung aller 30 Gebäude mit der Championzahl:

1. Gebäude 01–12: je Champion freischalten.
2. Gebäude 13–30: über die im Spiel festgelegten Level- und Goldanforderungen; hier werden keine neuen Preise oder Level erfunden.
3. Gebäude ab 13 ausschließlich in Reihenfolge bauen: 14 erst nach 13, 15 erst nach 14 usw. Der Zugang zu diesem Ausbau setzt die vorausgehende Basis bis 12 voraus.

Die bisherigen Werte `unlock_at` im Wegenetz als **Ausbauindex**, nicht generell als Championzahl interpretieren. Bei einer lückenlosen Folge tatsächlich gebauter Gebäude 01 bis N gilt die vorhandene Erreichbarkeitsprüfung für diesen Index weiterhin. Level- und Goldbedingungen werden davon unabhängig im Spiel geprüft.

## Prüfung

PNG erfolgreich geöffnet und dekodiert; Größe 724 × 2172 geprüft. Sichtprüfung: 30 leere Flächen, drei Spalten, zehn Reihen, keine Gebäude, keine Ziffern oder Schilder. Eingang und durchgehende Hauptwege vorhanden. SHA-256 und Dateigröße stehen in `DATEIPRUEFUNG_LEERE_BAUPLAETZE.json`.
