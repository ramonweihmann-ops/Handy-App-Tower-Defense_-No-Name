# Talente – freigegebene ruhige Gestaltung v1

Vom Nutzer am 03.11.2026 freigegeben. Die Gesamtansicht `talente_freigegeben.png` (978 × 1608) ist die optische Referenz. Das vertraute 4 × 4-Gitter, die Ziehbox, die Texte und die untere Navigation bleiben erhalten. Weiche bunte Comicflächen, dünne Ränder, dezenter Weltraum; keine zusätzlichen blinkenden Rahmen.

## Direkt nutzbare Einzelteile

- `ui_png/`: 18 transparente PNG-Bauteile für Talentkarten, Kopfbereiche, Ziehbox, Titel, goldene/grüne/violette Knöpfe, Umschalter und Navigation.
- `ui/`: dieselben 18 Bauteile als editierbare SVGs, ohne eingebrannte Texte.
- `symbole/`: zwölf vorhandene separate Symbole für Schnelllader/Energiekern, Sanitätskoffer, Währungen, Profil, Einstellungen und Navigation. Unverändert aus dem freigegebenen Paket Icons_v1.
- `hintergrund/weltraum_gemeinsam.png`: UI-freier Weltraumhintergrund, gemeinsam mit der Tech-Werft verwendbar.
- `LAYOUT_UND_ZUSTAENDE.json`: ungefähre Referenzpositionen, Kartenzustände und Beschriftungen.
- `BAUTEILE_UEBERSICHT.jpg`: Prüfübersicht, nicht als Spielfläche einsetzen.
- `DATEIPRUEFUNG.json`: tatsächliche Dateimaße, Transparenz und Prüfsummen.

Die Gesamtansicht muss nicht zerschnitten werden. Der Bildentwurf besitzt keine ursprünglichen separaten Ebenen: Die UI-Flächen wurden als wiederverwendbare Vektoren passend nachgebaut, nicht pixelidentisch aus Ebenen exportiert. Der gemeinsame, separat erzeugte Hintergrund übernimmt die ruhige Farbfamilie; seine Planetendetails entsprechen nicht exakt der Talente-Gesamtansicht. Für Material, Proportionen und Feinabstände bleibt die Freigabe maßgeblich. Die vorhandene lizenzierte Spielschrift verwenden; keine Schriftdatei ist beigefügt.

## Zusammenbau

1. Hintergrund über die Bildschirmfläche legen. Sichere Bildschirmränder berücksichtigen.
2. Vier Spalten und vier Zeilen anlegen. Zwei grüne bekannte Karten, vierzehn violette unbekannte Karten. Überschriften, Stufen, Fragezeichen und Pluszeichen als dynamische Labels darüberlegen. Icons mittig platzieren. Den dunkleren Kopfbereich innerhalb der grünen Karte maskieren, damit die unteren Rundungen nicht überstehen.
3. Die Ziehbox mit eigenem Titel und drei Schaltflächen aufbauen. Gold: `ÖFFNEN` mit Videozeichen und `3/3`; Grün: `ÖFFNEN` mit Talent-Stern und `1`; Violett: `5 STERNE AUF EINMAL ZIEHEN`. Das einfache Video-Dreieck zeichnet die Oberfläche selbst. Mengen und Verfügbarkeit aus der vorhandenen Spiellogik übernehmen.
4. Den Umschalter TECH-WERFT / TALENTE darüber setzen; TALENTE ist aktiv. Unten Upgrades hervorheben, Navigation bis zum unteren sicheren Bildschirmrand führen.

Die Anzeige von zwei freigeschalteten Talenten sowie alle Mengen sind Beispielzustände. Es werden keine neuen Preise, Ziehchancen oder Spielfunktionen eingeführt. Unbekannte Felder sind nicht automatisch kaufbar. Die Spielkonfiguration entscheidet, ob Schaltflächen aktiv oder gesperrt sind. Grün enthält Normal-, Hervorhebungs- und Drückzustand; Gold und Violett Normal- und Drückzustand. Gesperrte Knöpfe liegen separat bei.

Flächen mit erhaltenen Rundungen skalieren; Symbole proportional skalieren. Keine Texte oder Zahlen in die Grafiken einbacken. Die Anordnung bei kleinen Displays darf responsiv angepasst werden, ohne die Felder zu überlagern.

## Herkunft und Prüfung

Eigenständig für dieses Projekt erstellte Gestaltung und Vektorflächen; vorhandene freigegebene Projektsymbole wiederverwendet. Keine zusätzlichen Fremdassets oder Schriften beigelegt. Dieses Paket erteilt keine weitergehende Zusage über ausschließliche Urheberrechte an generierten Bildern.

PNG-Dateien, Transparenz, Maße, SVG-XML und die 16 Feldzuordnungen wurden geprüft. Ein Laufzeittest in Godot steht noch aus. Die Generatoren sind optional; die PNG-Dateien sind bereits nutzbar. Die Bildanweisungsdatei dokumentiert die gemeinsamen Entwurfsquellen von Tech-Werft und Talente, nicht zusätzliche Freigaben anderer Konzepte.
