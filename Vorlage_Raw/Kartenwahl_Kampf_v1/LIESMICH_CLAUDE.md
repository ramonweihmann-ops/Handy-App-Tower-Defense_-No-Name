# Kartenwahl im Kampf – freigegebene Fassung

Die drei Optionen stehen untereinander. Die Kategorien WAFFE, SUPER und CHAMPION sind farbige, gut sichtbare Plaketten. Texte bleiben schlank. Die gewählte Karte erhält einen Goldrand und einen grünen Haken. Der zusätzliche Text „Ausgewählt“ entfällt. Fritzi hat die orange Mütze. Porträts etwas größer als im Vorgänger, ohne die Karte zu dominieren.

## Dateien und Aufbau
- `kartenwahl_entwurf_freigegeben.png`: unveränderte freigegebene Gestaltungsvorlage; kein Hintergrund für die komplette Spieloberfläche.
- `motive/`: sechs einzelne transparente RGBA-PNGs, je 512 × 512. Waffenmotiv, Feuerwalze, Fritzi-Porträt, vorhandener Dusty Jo, Plasmatank und Energiekern. Neu ausgegebene Motive sind eigenständige Bausteine im Vorlagenstil; keine fehleranfälligen Rechteckausschnitte aus dem Bildschirm.
- `ui/`: skalierbare SVG-Bausteine ohne eingebrannte Texte: Fenster, normale/gewählte Karte, normale/gedrückte/inaktive Knöpfe, Kategorien, Stufenfeld, Neu-im-Team-Feld, Haken und Porträtrahmen sowie drei Kategoriesymbole. SVG wird von Godot importiert; für frei gestreckte Flächen NinePatchRect oder StyleBoxFlat mit den Radien/Farben verwenden.
- `TEXTE_UND_BEISPIELE.json`: getrennte Texte für Helden- und Plasma-Varianten. Beispielwerte unverändert aus den vorliegenden Ansichten.
- `LAYOUT.json`: Maße in Punkten, Farben, Schriftgrößen und Zustände. Die Maße sind eine Einbauempfehlung für 390 × 844, keine Änderung an der Kampfkamera.

## Einbau
CanvasLayer → Abdunklung (ColorRect) → zentriertes Panel → Überschrift → VBoxContainer mit drei auswählbaren Karten → Bestätigung. Pro Karte: Button/Control mit Hintergrund, Motiv-TextureRect (KEEP_ASPECT_CENTERED), optionalem Porträt, Trennlinie, Kategorie, Titel, Stufe und Details. Texte als Labels, niemals aus dem Entwurf ausschneiden. Der Hinweistext „Ausgewählt“ wird nicht angelegt.

Abdunklung etwa #100D22 mit 55–65 % Deckkraft; vorhandenes Kampf-HUD und Hintergrund weiterverwenden. Das Bild enthält nur beispielhafte HUD-Werte. Keine Werte daraus übernehmen. Motive sind stillstehende UI-Symbole und keine Kampfanimationen oder 3D-Waffen.

Fenster und Karten auf die verfügbare Breite anpassen, gleiche Höhen und Abstände für alle Optionen. Referenzlayout siehe JSON. Titel maximal zwei Zeilen, Beschreibung mindestens 12 Punkte, Kategorie immer sichtbar. Bei langen Übersetzungen die Texthöhe anpassen statt stark zu verkleinern; auf 390 × 844 prüfen. Keine glänzenden Zusatzrahmen, keinen weiteren Effekttext hinzufügen.

Fredoka für Überschriften und Nunito für Details, vorhandene lizenzierte Projekt-Schriften verwenden. Dateien enthalten keine fremden Fontdateien. SVGs enthalten keine Schrift. UI-Auswahl höchstens 100–150 ms weich einblenden; keine starke Pulsanimation.

## Fachliche Prüfung
„+1 Spezialfähigkeit“ ist auf der ursprünglichen Waffenkarte enthalten und bleibt unverändert. Bitte fachlich mit der tatsächlichen Fähigkeit abgleichen. „×2“ beim Plasma-Verdichter wurde nicht als doppelter Schaden interpretiert. Keine Preise, Stufen, Wirkungen oder Freischaltungen ergänzt. Die Spielauswahl und die Bestätigung laufen weiterhin über die bestehenden Daten und Regeln.

Die Plasma-Optionen nutzen denselben Kartenbaukasten; ihre Werte werden als separate Labels gesetzt. Das Plasmakernmotiv ist eine vorhandene Stilreferenz, der Text definiert die Option. Weitere Helden erhalten ihre jeweils vorhandenen Porträts und Waffensymbole über Datenzuordnung; Fritzi-/Dusty-Motive nicht für andere Helden fest verdrahten.

## Quellen
Eigene projektbezogene Bildgenerierung im bestehenden Konto und bereits vorhandene Projektgrafiken, siehe QUELLEN.json und BILDANWEISUNGEN.json. Keine externen Asset-Pakete und keine kostenpflichtigen Zusatzdienste eingesetzt. Keine Exklusivitäts- oder Schutzrechtsgarantie abgeleitet.
