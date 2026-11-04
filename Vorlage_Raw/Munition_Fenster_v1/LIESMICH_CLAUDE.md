# Munition – sechs unabhängige Upgrade-Module

Die Munition gehört zum Reiter **Upgrades**. Das Fenster öffnet sich über dieser Seite; es ist kein Kampf-Fenster. Profil-/Währungsleiste und untere Navigation bleiben sichtbar. Die Upgrade-Seite hinter dem Fenster wird abgedunkelt.

Alle sechs Verbesserungen können **parallel und unabhängig** gekauft werden. Die Anordnung ist nur eine Sortierung. Keine Verbindungslinien, Pfeilketten, vorherigen Stufen anderer Module oder neuen Freischaltbedingungen. Pro Kauf steigt ausschließlich das gewählte Modul um eine Stufe. Die Verbesserungen gelten dauerhaft in jedem Kampf.

## Dateien

- `munition_entwurf_v1.png`: vollständige Bildschirmvorlage, 852 × 1846 Pixel.
- Sechs einzelne RGBA-Symbole, jeweils 256 × 256 Pixel, transparenter Hintergrund und freier Rand. Keine Rahmen oder Knöpfe in diese Dateien einbauen.
- `LAYOUT_UND_WERTE.json`: genaue Texte, Preisformeln, Beispielwerte und Zielpositionen für die Nachbildung als Godot-Oberfläche.
- `BILDANWEISUNG.txt`: verwendete Bildanweisung für den Bildschirm und die sechs Symbole.
- `DATEIPRUEFUNG.json`: tatsächliche Bildgrößen und Transparenzprüfung.

Der Bildschirm ist eine Gestaltungsvorlage. Texte, Preise, Segmente, Symbole und Knöpfe separat in Godot bauen. Keine Bildschirm-Ausschnitte als fertige anklickbare Karten verwenden.

## Inhalt und Werte

Überschrift: **Munition**

Untertitel: **Gilt in jedem Kampf.**

Gold des Spielers im Entwurf: **662**.

| Verbesserung | Wortgetreue Beschreibung | Stufen | Preis je nächster Stufe |
|---|---|---:|---|
| Plasma-Takt | Plasma kommt 6 % schneller nach (je Stufe) | 10 | 80 Gold × (Stufe + 1) |
| Plasma-Tank | +8 Plasma Platz (je Stufe) | 10 | 60 Gold × (Stufe + 1) |
| Startvorrat | +5 Plasma zu Beginn (je Stufe) | 10 | 50 Gold × (Stufe + 1) |
| Energiekern | Energiekern 1,5 s schneller bereit und +2 Plasma (je Stufe) | 5 | 150 Gold × (Stufe + 1) |
| Zweiter Erzeuger | +1 Plasma pro Ladung (je Stufe) | 3 | 500 Gold × (Stufe + 1) |
| Start-Tore | Stufe 1: +3-Tor, Stufe 2: zweites ×2-Tor von Anfang an | 2 | 1.200 Gold × (Stufe + 1) |

`Stufe` in der Formel ist die bereits erreichte Stufe, beginnend bei 0. Bei maximaler Stufe keinen weiteren Kaufpreis berechnen oder anzeigen. Keine neuen Werte hinzufügen. Texte und Symbole müssen voneinander getrennt bleiben, damit die Spielstände dynamisch eingesetzt werden können.

## Drei Zustände im Entwurf

| Modul | Gezeigt | Nächster Preis | Zustand |
|---|---|---:|---|
| Plasma-Takt | 6/10 | 560 Gold | kaufbar |
| Plasma-Tank | 4/10 | 300 Gold | kaufbar |
| Startvorrat | **10/10** | kein Kaufknopf | MAX |
| Energiekern | 3/5 | 600 Gold | kaufbar |
| Zweiter Erzeuger | 0/3 | 500 Gold | kaufbar |
| Start-Tore | 0/2 | 1.200 Gold | zu teuer |

**Bewusste Demoabweichung:** Der ursprüngliche Beispielstand des Startvorrats war 4/10 mit einem nächsten Preis von 250 Gold. Nur für die ausdrücklich gewünschte MAX-Darstellung wird dieses Modul im Bild auf 10/10 gesetzt. Das verändert keine Spieldaten. Die anderen fünf Beispielstände bleiben wie vorgegeben.

- **Kaufbar:** grüner Knopf, Goldmünze und Preis, dunkle Schrift. Bei Antippen einmal den vom Spiel berechneten Preis prüfen und genau eine Stufe kaufen.
- **Zu teuer:** ausgegrauter Knopf, Goldmünze, Preis rot. Der Kauf ist deaktiviert; das Modul bleibt sichtbar. Nicht als gesperrt oder als abhängig von anderen Modulen darstellen.
- **MAX:** goldenes Abzeichen mit `MAX` anstelle des Kaufknopfs, alle Segmente gefüllt, kein weiterer Preis.

Die Anzahl der Segmente entspricht immer der maximalen Stufenzahl: 10, 10, 10, 5, 3, 2. Die gefüllten Segmente entsprechen der erreichten Stufe. Die Zahlenanzeige bleibt zusätzlich bestehen, damit sich Stände eindeutig ablesen lassen.

## Aufbau und Abstände

Alle folgenden Maße sind **logische Punkte auf 390 × 844**, keine Pixel des hochauflösenden Bildes. Bei anderer Bildschirmgröße über Container skalieren; Schrift und Trefferflächen nicht blind proportional verkleinern.

- Kopfleiste: Zielbereich y = 0–66. Vorhandene Profil-, Energie-, Gold-, Edelstein- und Einstellungsfelder wiederverwenden. Gold 662; keine neuen Währungen.
- Navigation: Zielbereich y = 774–844; Reiter Shop, Helden, Kampf, Upgrades, Basis. Upgrades aktiv.
- Fenster: x = 10, y = 76, Breite = 370, Höhe = 684. Rundung etwa 22; Goldkontur etwa 1,5.
- Fensterkopf: Titel ca. 28 Punkte Fredoka fett; Untertitel 12 Punkte Nunito. Roter Schließenknopf oben rechts, weißes X, sichtbarer Knopf ca. 36 und Trefferfläche mindestens 44 × 44.
- Module als Raster **2 Spalten × 3 Reihen**. Linke Spalte x = 22, rechte x = 199; Breite jeweils 169. Zeilen beginnen bei y = 145, 345, 545; Höhe jeweils 192. 8 Punkte horizontaler und vertikaler Zwischenraum. Außenabstand mindestens 12.
- Reihenfolge zeilenweise: Plasma-Takt / Plasma-Tank; Startvorrat / Energiekern; Zweiter Erzeuger / Start-Tore. Diese Reihenfolge begründet **keine** Kaufabhängigkeit.
- Innenabstand je Modul etwa 8. Titel 16 Punkte Fredoka fett, für lange Namen nötigenfalls zweizeilig; Stufen 11–12 Punkte Nunito fett.
- Symbole etwa 42–48 Punkte groß, nicht über Namen oder Text legen. Beschreibungen 12 Punkte Nunito mit ca. 14 Punkten Zeilenhöhe. Im schmalen Modul sind bei Energiekern und Start-Tore bis zu drei Zeilen zulässig, damit keine Wörter fehlen und die Schrift lesbar bleibt.
- Segmentleiste ca. 6–7 Punkte hoch, Abstände 2–3. Die Breite pro Segment passt sich der jeweiligen Segmentzahl an.
- Preisknöpfe ca. 120–145 × 32 sichtbar, Trefferfläche mindestens 44 Punkte hoch. Roter Preis nur im Zustand zu teuer. Münze ohne zusätzliche Preiswährung.
- Kein Scrollen. Auf 390 × 844 prüfen, ob alle sechs Module zwischen den bestehenden Leisten vollständig sichtbar sind. Das rasterartige Layout soll sich klar von einem linearen Tech-Baum unterscheiden.

Die Pixelvorlage dient der optischen Orientierung. Für die Godot-Umsetzung sind die Textwerte, Segmentanzahlen und Zustände in diesem Dokument und der JSON-Datei maßgeblich. Fredoka und Nunito als echte Schriften einsetzen; die Bildgenerierung ist keine Fontdatei.

## Farbwerte für die Umsetzung

| Verwendung | Hex |
|---|---|
| Fenster dunkelviolett | `#231747` |
| Oberes weiches Fensterlicht | `#44306F` |
| Modulfläche | `#302354` |
| Modulrand, dezent | `#6C5298` |
| Goldkontur und Überschrift | `#FFD56A` |
| Helle Titel | `#FFF4D8` |
| Beschreibung und Nebenangaben | `#DDD6F3` |
| Plasma / gefüllte Segmente | `#52E7FF` |
| Leere Segmente | `#514266` |
| Kaufknopf oben / unten | `#A0F568` / `#4BC62D` |
| Kaufknopf-Schrift | `#14320E` |
| Deaktivierter Knopf | `#514D68` |
| Zu teurer Preis | `#FF8A8A` |
| MAX-Abzeichen oben / unten | `#FFE58A` / `#D99B31` |
| MAX-Schrift | `#613A0A` |
| Schließen oben / unten | `#EF626E` / `#B82545` |
| Abdunklung der Upgrade-Seite | `#0B071C` mit ca. 60 % Deckkraft |

Die Hintergrundabdunklung unterhalb der bestehenden Leisten und hinter dem Fenster einsetzen. Das Fenster empfängt die Eingaben. Ein Hintergrundklick löst keinen Kauf aus. Vorhandenes Schließverhalten beibehalten.

## Symbole und Herkunft

| Datei | Motiv |
|---|---|
| icon_plasma_takt.png | Uhr/Pfeile mit Plasmatropfen |
| icon_plasma_tank.png | Plasma-Tank |
| icon_startvorrat.png | Kiste mit Plasma |
| icon_energiekern.png | Leuchtende Energie-Kugel |
| icon_zweiter_erzeuger.png | Zwei Generatorrohre |
| icon_start_tore.png | Zwei Tore mit +3 und ×2 |

Erzeugt ausschließlich mit eingebauter Bildgenerierung im bestehenden Konto. Keine weiteren kostenpflichtigen Dienste, kein Meshy. Technische Größenanpassung und PNG-Verpackung nach der Generierung. Kein Fotorealismus. Symbole neu für dieses Projekt generiert; Verwendung im Rahmen der geltenden Kontobedingungen, keine Zusicherung rechtlicher Exklusivität einzelner KI-generierter Motive.

Noch kein Godot-Spieltest. Nach dem Einbau die Lesbarkeit bei 390 × 844, Textumbrüche, unabhängige Käufe, die drei Zustände und den sofortigen Preiswechsel nach einem Kauf prüfen.
