# Kampfeffekte – Vorschlag v1

50 getrennte Effektpakete für „Station am Wurmloch“, Stand 04.11.2026. Enthalten sind alle zwölf Helden, drei Iska-Mündungsvarianten, Pips Reparatur, drei Farben für besiegte Gegner, Boss-Auflösung, Zauntreffer, kritischer Treffer, Medipack und die vier Luftangriff-Bausteine.

Dies ist die Bildfolgen-Fassung zum Vergleich mit Claudes Partikeln. Sie wurde auf Dateiformat und visuell auf den exportierten Bildern geprüft, **noch nicht im Godot-Kampf**. Spielgeschwindigkeit, Überlagerungen und endgültige Weltgrößen bitte auf Claudes Prüfseite vergleichen. Es werden keine Spieldateien ersetzt und keine Schadenswerte vorgegeben.

## Dateien und Abspielung

- Je Ordner: `<name>_sheet.png`, `<name>.json`, `<name>_vorschau.gif`.
- PNG: RGBA, sRGB, gerades/nicht vormultipliziertes Alpha. Alle Pakete verwenden `mischung: alpha`; keine separate additive Fassung.
- Bildfolgen: 16 Phasen, 4 Spalten × 4 Reihen, links nach rechts und dann nächste Zeile. 24 Bilder/s. Kleine Effekte 128 × 128 je Phase, sonst 256 × 256. Größtes animiertes Blatt 1024 × 1024.
- Ausnahme gemäß Auftrag: Raumjäger als statisches 512 × 512-Sprite, zusätzlich `luftangriff_raumjaeger.png`; JSON hat eine Phase. Seine Bewegung und die Triebwerksanimation sind getrennt.
- GIFs zeigen dieselben Phasen vor dunkelviolettem Prüfgrund, weil GIF weiche Transparenz nicht sauber unterstützt. Dieser Grund ist **nicht** im PNG. GIF-Zeiten liegen formatbedingt bei 40/50 ms; maßgeblich sind die 24 Bilder/s im JSON. Die GIFs wiederholen auch einmalige Effekte zur Sichtprüfung.
- Anker sind normiert: X nach rechts, Y nach unten. Mündungsursprung unten bei `[0.5, 0.75]`, andere Motive in der Mitte. Keine eigene Kollisions- oder Schadensgröße aus dem Motiv ableiten.
- Eine gemeinsame Skalierung pro Bildfolge bewahrt das Wachsen und Abklingen; die Motivposition wurde pro Phase am dokumentierten Anker registriert. Freie Zellränder sind geprüft.
- Originalrichtung der gerichteten Motive: nach oben. Im Spiel vom jeweiligen `Muzzle` zum Ziel ausrichten. Brockens Rauchstoß am Werferheck entgegengesetzt ausrichten. Billboard bleibt zur Kamera gerichtet.
- `groesse_m` beschreibt die vorgeschlagene volle Quadratbreite einschließlich transparenter Ränder. Richtwerte: Brücke etwa 9 m, Held etwa 1,5 m. Keine verbindliche Abstimmung auf die Spielkamera.
- Strahlen von Volta, Kalle und Fünkchen sind entlang ihrer Längsachse zwischen Start und Ziel dehnbar. Geschosse bewegt das Spiel. Dusty Jos letzten Schuss mit mehreren Instanzen auffächern; Iskas drei Varianten abwechseln.
- Schleifen sind gezeichnete Phasenfolgen. Übergang und Flackertempo im Spiel prüfen; eine mathematisch identische Anschlussphase ist nicht garantiert.
- Zuerst ohne Mipmaps und ohne additive Mischung prüfen. Bei geglätteter Filterung dürfen keine Nachbarzellen eingelesen werden. Das Spiel muss Effekte nach der letzten Phase ausblenden, wenn `loop` falsch ist.

## Luftangriff und Übersicht

Zwei oder drei Instanzen des Jägers fliegen von unten nach oben. Triebwerksfolge getrennt am Heck platzieren, Bomben getrennt auslösen und anschließend die Explosionsreihe abspielen. Alternativ einzelne `brocken_explosion`-Instanzen zeitversetzt setzen. Flugtempo, Bombenabwurf und Schadenszeitpunkt bestimmt der Spielcode.

`UEBERSICHT.png` zeigt alle 50 Motive in beschrifteten Brücken-Ausschnitten mit einem einheitlichen angenäherten Maßstab aus `groesse_m` (Brückenbreite rund 9 m). `EFFEKTKATALOG.png` zeigt dieselben Motive vergrößert und unabhängig skaliert zur Detailkontrolle; dieser Katalog ist kein Größenvergleich. `KAMPFSZENE_VORSCHAU.png` zeigt die priorisierten Effekte als gemeinsame Montage auf derselben Brücke. Alle drei sind **Gestaltungsmontagen, keine Bildschirmfotos eines Godot-Spieltests**. Ein echtes Kampf-Bildschirmfoto lag für diesen Export nicht vor.

## Erzeugung und Auffälligkeiten

Erzeugt mit der eingebauten Bildgenerierung im vorhandenen Konto, auf Grundlage der freigegebenen Comic-Stilvorlagen. Technische Verarbeitung: Raster zerlegen, mit gemeinsamem Maßstab verkleinern, am Anker registrieren, transparente PNGs sowie GIFs und JSON exportieren. Unerwünschte Metallplatten und Hintergrundschleier wurden durch Bildbearbeitung entfernt. Keine Meshy-Erzeugung, keine Meshy-Credits und keine zusätzlichen kostenpflichtigen Dienste.

Die Bausteine sind bewusst als gut erkennbare Comic-Vorschläge gehalten. Einzelne Flackerphasen und Konturen variieren durch die Bildgenerierung. Kleine Düsenansätze sind beim Triebwerksglühen mitgezeichnet. Die Bombe wirkt wie eine kleine Raumkapsel. Dies bitte bei der Freigabe neben der Partikelfassung beurteilen. `BILDANWEISUNGEN.json` enthält die verwendeten Bildanweisungen und Korrekturen; `DATEIPRUEFUNG.json` und `ABSCHLUSSPRUEFUNG.json` dokumentieren die technische Kontrolle.

## Herkunft und Nutzung

Neu generierte Grafiken für dieses Projekt, keine übernommenen Fremd-Spielgrafiken oder Bibliotheks-Effekte. Die Verwendung im Spiel ist im Rahmen der geltenden Bedingungen des verwendeten OpenAI-Kontos vorgesehen; es wird keine gesonderte Fremdasset-Lizenz benötigt. Eine rechtliche Exklusivität oder urheberrechtliche Schutzfähigkeit KI-generierter Einzelmotive wird nicht zugesichert. Die Brückengrafik in den Montagen stammt aus dem vorhandenen Projektbestand.

## Enthaltene Pakete

| Kennung | Einzelbild px | Phasen | Schleife | Breite m |
|---|---:|---:|---|---:|
| `brocken_explosion` | 256 | 16 | nein | 2.5 |
| `luftangriff_raumjaeger` | 512 | 1 | nein | 1.8 |
| `luftangriff_triebwerk` | 128 | 16 | ja | 0.8 |
| `luftangriff_bombe` | 128 | 16 | ja | 0.35 |
| `luftangriff_explosionsreihe` | 256 | 16 | nein | 8 |
| `gegner_besiegt_gruen` | 256 | 16 | nein | 1.15 |
| `gegner_besiegt_lila` | 256 | 16 | nein | 1.15 |
| `gegner_besiegt_rosa` | 256 | 16 | nein | 1.15 |
| `boss_besiegt` | 256 | 16 | nein | 3.3 |
| `energiezaun_treffer` | 256 | 16 | nein | 1.15 |
| `kritischer_treffer` | 128 | 16 | nein | 0.65 |
| `medipack_heilung` | 256 | 16 | nein | 2 |
| `dusty_jo_muendung` | 128 | 16 | nein | 0.55 |
| `dusty_jo_geschoss` | 256 | 16 | ja | 0.8 |
| `dusty_jo_einschlag` | 128 | 16 | nein | 0.65 |
| `iska_muendung` | 128 | 16 | nein | 0.5 |
| `iska_geschoss` | 256 | 16 | ja | 0.8 |
| `iska_einschlag` | 128 | 16 | nein | 0.65 |
| `brocken_muendung` | 128 | 16 | nein | 0.8 |
| `brocken_geschoss` | 256 | 16 | ja | 1.1 |
| `volta_muendung` | 128 | 16 | nein | 0.55 |
| `volta_geschoss` | 256 | 16 | ja | 2 |
| `volta_einschlag` | 256 | 16 | nein | 1.2 |
| `kalle_muendung` | 128 | 16 | nein | 0.6 |
| `kalle_geschoss` | 256 | 16 | ja | 1.8 |
| `kalle_einschlag` | 256 | 16 | nein | 1.4 |
| `margot_muendung` | 128 | 16 | nein | 0.75 |
| `margot_geschoss` | 256 | 16 | ja | 1.6 |
| `margot_einschlag` | 128 | 16 | nein | 1.1 |
| `lynx_muendung` | 128 | 16 | nein | 0.55 |
| `lynx_geschoss` | 256 | 16 | ja | 2.5 |
| `lynx_einschlag` | 128 | 16 | nein | 0.9 |
| `fritzi_muendung` | 128 | 16 | nein | 0.75 |
| `fritzi_geschoss` | 256 | 16 | ja | 2.2 |
| `fritzi_einschlag` | 256 | 16 | ja | 1.1 |
| `fuenkchen_muendung` | 128 | 16 | nein | 0.55 |
| `fuenkchen_geschoss` | 256 | 16 | ja | 2.8 |
| `fuenkchen_einschlag` | 128 | 16 | nein | 1 |
| `pip_muendung` | 128 | 16 | nein | 0.35 |
| `pip_geschoss` | 256 | 16 | ja | 0.45 |
| `pip_einschlag` | 128 | 16 | nein | 0.65 |
| `rollo_muendung` | 128 | 16 | nein | 0.9 |
| `rollo_geschoss` | 256 | 16 | ja | 0.65 |
| `rollo_einschlag` | 256 | 16 | nein | 1.7 |
| `nova_muendung` | 128 | 16 | nein | 0.65 |
| `nova_geschoss` | 256 | 16 | ja | 0.9 |
| `nova_einschlag` | 256 | 16 | nein | 2 |
| `iska_muendung_variante_2` | 128 | 16 | nein | 0.5 |
| `iska_muendung_variante_3` | 128 | 16 | nein | 0.5 |
| `pip_reparatur` | 256 | 16 | nein | 1.3 |
