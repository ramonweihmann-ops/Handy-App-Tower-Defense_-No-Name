# Champion-Porträts für den Auflevel-Bildschirm

## Dateien

- [Ohne Hintergrund](ohne_hintergrund/) · acht PNGs mit echtem Alphakanal für das Auflevel-Fenster. Der Fensterhintergrund kann frei gestaltet werden.
- [Mit Hintergrund](mit_hintergrund/) · dieselben acht Motive auf ruhigem Dunkelviolett `#221935`. Die Fassung ist als direkt einsetzbares Einzelbild gedacht.
- [Übersicht mit Namen](UEBERSICHT_CHAMPIONS.png) und [Maße und Ausrichtung je Motiv](PORTRAET_LAYOUT.json).

Beide Fassungen haben pro Champion dieselben Bildmaße und denselben Bildausschnitt. In den Einzelbildern steht kein Text. Die Dateinamen entsprechen den Champion-IDs.

## Einpassen in Godot

1. Im Auflevel-Fenster die Textur anhand der Champion-ID laden. Die JSON enthält unter `datei` den Pfad zur transparenten Fassung und unter `datei_mit_hintergrund` den Pfad zur Variante mit dunkelvioletter Fläche.
2. Das Bild proportional in den verfügbaren Bereich einpassen. Für die transparente Fassung kann `motivbereich_px` als `[x, y, breite, höhe]` zur Platzierung oder als Region einer `AtlasTexture` dienen. Bei der Hintergrundfassung umfasst die Textur die gesamte Bildfläche. Hut, Haare, Lauf und Stiefel sollen vollständig im Fenster bleiben.
3. Das sichtbare Motiv horizontal zentrieren und unten auf der Standlinie platzieren. `maximale_motivhoehe_relativ_zur_anzeigehoehe` und `abstand_zur_standlinie_relativ_zur_anzeigehoehe` sind Vorschlagswerte relativ zur Höhe des Bildbereichs. Fritzi sitzt durch den Sprung leicht höher, Lynx bleibt kniend niedriger.
4. Den Namen bei Bedarf als UI-Text unter dem Bild setzen. Das Portrait ist eine statische Illustration.

Die PNGs wurden auf Dateizuordnung, Bildgröße und Hintergrund geprüft. Die Ansicht im fertigen Godot-Fenster steht zur Prüfung aus.
