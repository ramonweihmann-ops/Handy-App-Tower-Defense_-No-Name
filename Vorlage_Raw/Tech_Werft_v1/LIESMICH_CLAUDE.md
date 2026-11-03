# Tech-Werft – freigegebene ruhige Gestaltung v1

Vom Nutzer am 03.11.2026 freigegeben: `tech_werft_freigegeben.png`, 978 × 1608 Pixel. Maßgeblich ist die ruhigere Schutz-Ansicht mit zwei seitlichen Ästen, drei Bereichsreitern oben und der großen Detailbox unten. Dünne Konturen, weiche Kapselknöpfe und dezente Farben verwenden; starke Leuchtränder und schwere Grundplattformen vermeiden.

## Dateien und Wiederverwendung

- `tech_werft_freigegeben.png`: freigegebene Gesamtansicht zum Vergleichen.
- `hintergrund/tech_werft_hintergrund.png`: separat nutzbarer leerer Weltraumhintergrund, ohne Texte, Module, Verbindungslinien oder Navigation.
- `ui/*.svg` und `ui_png/*.png`: 24 textfreie Bauteile als editierbare Vektoren und gerasterte PNGs. Enthalten sind Bereichsknöpfe, Titel- und Detailflächen, Modulzustände, Schild, Regeneration, Schloss, Verbindungen, Statusmarke, Schaltflächen und Navigation.
- `symbole/*.png`: zehn unverändert wiederverwendete Symbole aus Icons_v1 für Ressourcen, Profil, Einstellungen und Navigation.
- `FORSCHUNGSWEGE_UND_LAYOUT.json`: Zuordnung der Knoten, Verbindungen, Statusbeispiele, Bereichswähler und Detailbox.
- `BAUTEILE_UEBERSICHT.jpg`: reine Prüfübersicht; die Einzeldateien für den Einbau benutzen.

Die Zahlen I, II und III auf dem Schild sowie alle Überschriften, Kosten, Werte und Schaltflächentexte im Spiel als eigene Labels setzen. Die gelbe Marke 3 ist ebenfalls eine leere Fläche plus dynamischer Text. Claude muss die Gesamtansicht nicht zerschneiden.

Der generierte Gesamtentwurf hat keine ursprünglichen getrennten Ebenen. Der leere Hintergrund wurde deshalb mit der eingebauten Bildgenerierung abgeleitet; die UI-Bauteile wurden als einfache wiederverwendbare Vektoren in derselben Farbfamilie nachgebaut. Das ist kein pixelidentischer Ebenenexport. Für die genaue Materialanmutung und Feinabstände bleibt die freigegebene Gesamtansicht die optische Referenz. Die bereits verwendete lizenzierte Spielschrift benutzen; keine neue Schriftdatei wird verteilt.

## Verhalten und Forschungswege

Oben bleiben die drei Bereichswähler **Angriff, Schutz, Technik**. Die Gestaltung des Schutz-Arms ist freigegeben; für die vollständigen Bäume der anderen beiden Bereiche sind noch keine neuen Inhalte festgelegt.

Im Schutzbereich ist Schild I der gemeinsame Ausgangspunkt. Von ihm aus führen zwei unabhängig ausbaubare Äste zu Schild II / Schild III und zu Regeneration / weiterer Regeneration. Der eine Ast soll den anderen nicht dauerhaft sperren. Die JSON-Datei beschreibt dieses Strukturbeispiel, keine fertige neue Laufzeitkonfiguration oder Spielbalance.

Status im gezeigten Beispiel: Schild I erforscht mit Haken, Schild II ausgewählt mit kleiner Marke 3, Schild III gesperrt, erste Regeneration verfügbar und weitere Regeneration gesperrt. Die jeweils gewählte Verbesserung zeigt ihre Angaben in der Detailbox. Die Zeile „Andere Forschungswege bleiben verfügbar“ und der weiche grüne AUSBAUEN-Knopf gehören zur ausgewählten Gestaltung.

Konkrete Kosten, Zahlenwerte und zusätzliche Stufen liefert die vorhandene beziehungsweise später abgestimmte Spielkonfiguration. In diesem Paket wurden dafür keine Werte erfunden. Die früher gezeigte Querverbindung „Deckungsfeuer“ ist nicht Bestandteil dieser Freigabe. Der Talente-Entwurf ist eine getrennte Gestaltung und wird hier nicht zusätzlich als freigegeben veröffentlicht.

## Umsetzung und Prüfung

Hintergrund zuerst, Verbindungen dahinter, dann Modulflächen, Symbole und Statuszeichen. Texte und Trefferflächen darüber legen. Verbindungen können mit den mitgelieferten Vorlagen oder direkt über passende Kurven gezeichnet werden. Alle Leitungen sichtbar an ihren Knoten anschließen. Rahmen und Knöpfe beim Skalieren mit erhaltenen Ecken verwenden; die Referenzgröße ist keine fest vorgeschriebene Handyauflösung.

Die normalen, hervorgehobenen, gedrückten und gesperrten Knöpfe sind getrennt vorhanden. Bei verfügbaren Modulen reicht eine kleine Kontur; nur der ausgewählte Knoten bekommt einen dünnen warmgelben Rand. Kein zusätzliches Pulsieren oder äußeres Blinken für sämtliche Elemente hinzufügen. Die Navigation am unteren Bildrand verankern und Upgrades aktiv markieren.

Die Dateien wurden auf Öffnen, Maße, Transparenz und Prüfsummen kontrolliert; die Forschungsstruktur wurde auf vollständige Knotenverweise und Zyklen geprüft. Ein Test im laufenden Godot-Spiel steht noch aus. Die optionalen Python-/Node-Skripte dienen nur zur erneuten Bauteilerzeugung; bereits nutzbare PNGs liegen bei.
