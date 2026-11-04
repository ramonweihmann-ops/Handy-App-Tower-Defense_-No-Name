# Heldenauswahl beim Kampfstart – freigegebener Entwurf

Der Nutzer hat diesen Entwurf zum Bereitstellen auf GitHub freigegeben. Die vollständige Bildschirmvorlage liegt in `heldenauswahl_entwurf_v1.png` (852 × 1846 Pixel).

## Umsetzung

- Drei gleichwertige Karten nebeneinander: Brocken, Kalle, Iska. Keine Vorauswahl.
- Eine gemeinsame dunkelviolette Auswahlbox mit abgerundeten Ecken, feinem Goldrand und dezenten türkisen Details. Waffenfarben: Rostorange, Cyan, Blau.
- Größere freigegebene Heldenfiguren, klare Trennung zwischen Waffe, Figur, Name, Beruf und Beschreibung. Grüne Auswahlknöpfe.
- Den bisherigen Hinweis zu starken Starthelden einmal gemeinsam unter den Karten anzeigen.
- Hintergrund und Kampfbedienung bleiben der Kontext; während der Auswahl pausiert beziehungsweise sperrt das Spiel die Kampfaktionen entsprechend der bestehenden Logik. Keine neue Spiellogik aus dem Bild ableiten.
- Texte, Heldenbilder, Rahmen und Knöpfe als getrennte Godot-Elemente umsetzen. Das PNG ist eine Gestaltungsvorlage, keine fertige anklickbare Oberfläche und kein Satz freigestellter Einzelteile. Vorhandene freigegebene Helden und UI-Bausteine wiederverwenden.

## Texte

Überschrift: „Wer verteidigt die Station?“
Untertitel: „Wähle deinen ersten Helden“

| Held | Waffe | Beruf | Beschreibung |
|---|---|---|---|
| Brocken | Raketenwerfer | Bergarbeiter | Langsam, laut und mit viel Wumms. |
| Kalle | Frostpistole | Kühltechniker | Friert ein, was zu schnell ist. |
| Iska | Maschinengewehr | Sicherheitsschefin | Dauerfeuer, bis nichts mehr steht. |

Knöpfe: „Auswählen“
Gemeinsamer Hinweis: „Alle drei sind starke Start-Helden“

Alle Karten sollen vollständig antippbar sein. Die Zeilenumbrüche für lange Waffennamen und Berufsbezeichnungen an der tatsächlichen Handygröße prüfen. Keine neuen Kosten, Werte oder Voraussetzungen aus der Grafik übernehmen. Das Bild ist noch kein Godot-Spieltest.

`BILDANWEISUNG.txt` enthält den verwendeten Bildprompt. `ENTWURFSNOTIZ.md` erläutert die Gestaltung. Erzeugt mit eingebauter Bildgenerierung im vorhandenen Konto; keine zusätzlichen Dienste genutzt.
