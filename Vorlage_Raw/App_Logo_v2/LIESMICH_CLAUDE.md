# Station am Wurmloch · Freigegebenes App-Symbol B, v2

Der Nutzer hat Variante B mit weicher räumlicher Einbettung freigegeben. Diese Lieferung ersetzt B aus `App_Logo_v1`. Monster und Dusty kommen sichtbar aus dem Wurmloch; der vordere Portalbogen verdeckt die unteren Körperkonturen. A und C sind nicht ausgewählt.

[Freigegebene Grafik](B_1024.png) · [Größen- und Maskenvergleich](UEBERSICHT.png)

## Produktionsdateien

| Datei | Größe | Verwendung |
| --- | --- | --- |
| B_1024.png | 1024 × 1024, RGB | Unveränderte freigegebene Gesamtgrafik, quadratisch und deckend |
| B_192.png | 192 × 192, RGB | Direkt verkleinerte Gesamtgrafik |
| B_vordergrund_432.png | 432 × 432, RGBA | Beide Figuren einschließlich des vorderen Portalbogens, echte Transparenz |
| B_hintergrund_432.png | 432 × 432, RGB | Wurmloch mit zusätzlichem äußeren Beschnittraum, ohne Figuren |

## Einbau

Für ein normales vollständiges Symbol `B_1024.png` verwenden. Nicht erneut freistellen und keine abgerundeten Ecken in die Datei einbauen. Für Androids adaptive Darstellung Vordergrund und Hintergrund getrennt, zentriert und ohne zusätzlichen Zuschnitt der 432er Ebenen einsetzen. Der vordere Portalbogen gehört bewusst zur Vordergrundebene: Wird er entfernt, entsteht erneut der unerwünschte ausgeschnittene Eindruck.

Der zentrale Sicherheitskreis hat gemäß Auftrag 288 Pixel Durchmesser um (216,216). Gesichter, Kopfbedeckung und charakteristische Kopfhöcker liegen darin. Dekorative Ausläufe des Portallichts dürfen außerhalb liegen und von der Gerätemaske beschnitten werden. Keine zusätzliche Vergrößerung des Vordergrunds und keine automatische Entfernung seines transparenten Randes.

Die adaptive Zusammensetzung wurde aus der freigegebenen Grafik mit eingebauter Bildbearbeitung abgeleitet. Sie ist keine pixelgleiche Zerlegung: leichte Unterschiede bei Hintergrundlicht und Freistellung sind vorhanden. `B_ADAPTIV_VORSCHAU.png` und `UEBERSICHT.png` zeigen die tatsächliche Zusammensetzung neben der unveränderten Freigabe. Die freigegebene 1024er Gesamtgrafik bleibt die gestalterische Referenz.

Godot-Projekt-/Android-Exportzuweisungen beim Einbau passend setzen. In diesem Auftrag wurden weder `game/icon.svg` noch Exportkonfiguration oder Spielcode geändert. Danach auf einem echten Android-Startbildschirm prüfen, insbesondere Gerätemasken und Bewegung der Ebenen.

## Prüfung

Alle vier Produktionsdateien auf Maße und Farbmodus geprüft. Die 1024er Datei ist bytegleich zur freigegebenen Fassung. Übersicht mit 48, 72 und 96 Pixeln, jeweils rund und abgerundet-quadratisch, auf hellem und dunklem Hintergrund, samt altem Symbol. Gesichter und Kopfbedeckungen bleiben unter beiden Masken sichtbar. Vorschauen sind technische Simulationen, keine echten Geräteaufnahmen. Pixelgrößen gelten bei 100 Prozent Bildansicht.

Erzeugt und bearbeitet mit der eingebauten Bildgenerierung. Größenexport, Ebenenmontage und Vorschauen anschließend technisch zusammengestellt. Keine weiteren kostenpflichtigen Dienste.
