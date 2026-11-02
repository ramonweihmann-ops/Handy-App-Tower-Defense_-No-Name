# Raumbasis mit 30 Gebäuden – freigegebene Gestaltung

Die gemeinsame PNG-Datei zeigt alle 30 vom Nutzer gestalterisch bestätigten Gebäude. Originalauflösung: 724 × 2172 Pixel. Keine künstliche Hochskalierung. Die Gebäude stehen in zehn Reihen mit je drei Plätzen. Die Reihenfolge wächst von unten nach oben und innerhalb einer Reihe von links nach rechts.

## Verwendung

`GEBAEUDE_INDEX.json` enthält für jedes Gebäude eine eindeutige ID, einen deutschen Namen, ein rechteckiges Auswahlgebiet und einen ungefähren Fußpunkt. Der Ursprung liegt oben links; Rechtecke verwenden x, y, Breite, Höhe. Die Auswahlgebiete sind Orientierungshilfen für das Ausschneiden, keine präzisen Gebäudekonturen oder Trefferflächen.

Die PNG ist eine zusammenhängende Illustrationsvorlage mit undurchsichtigem Boden, Wegen und Nummernschildern. Sie enthält noch keine transparent freigestellten Sprites. Für frei platzierbare Gebäude muss Claude die Konturen entlang Dach, Antennen und Gebäudesockel freistellen und den umgebenden Boden sowie die Kontrollnummern entfernen. Ein rechteckiger AtlasTexture-Ausschnitt allein liefert weiterhin Hintergrund mit. Antennen oder ausladende Gebäudeteile können über die Auswahlgebiete hinausreichen; die Originalansicht beim Freistellen mitprüfen. Die niedrige native Einzelgebäudeauflösung bei großen Darstellungen berücksichtigen.

Die Gebäude-IDs im JSON sind maßgeblich. Im Bild ist das Schild von Gebäude 26 trotz Korrekturversuch als „6“ dargestellt. Das Gebäude zwischen 25 und 27 ist eindeutig Gebäude 26. Die Kontrollnummern gehören nicht in die fertigen Spielgrafiken.

## Erweiterbare Basis

Ein Gebäude pro freigeschaltetem Champion. Gebäude 01–05 bilden den Startbestand; danach kommt pro Champion das Gebäude mit der nächsten ID hinzu. Die Positionsdaten geben eine mögliche stabile Anordnung vor; die Kamera scrollt bei zunehmendem Ausbau nach oben. Bestehende Gebäude nicht mit jeder Stufe verkleinern oder versetzen. Der Ausbau bis 40 lässt sich später durch zusätzliche Reihen oberhalb von 28–30 fortsetzen.

Diese Lieferung enthält die gemeinsame Vorlage und den Ausschneideplan. Sie enthält noch keine fertigen Hintergrundvarianten für die einzelnen Championanzahlen, keine transparente Freistellung und keine Änderung der Spielszene. Der Nutzer wollte zunächst die Gebäude prüfen und diese nun für Claude zum Ausschneiden bereitgestellt haben.

