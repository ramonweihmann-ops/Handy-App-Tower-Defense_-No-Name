# Vier weitere Champion-Porträts für den Auflevel-Bildschirm

Diese Lieferung ergänzt [Version 1](../Champion_Portraets_v1/). Die [Übersicht mit Namen](UEBERSICHT_CHAMPIONS.png) zeigt alle zwölf Champions. Die Einzeldateien und die [Platzierungsdaten](PORTRAET_LAYOUT.json) dieses Ordners decken Fünkchen, Pip, Rollo und Nova ab.

| ID | Motiv |
| --- | --- |
| `fuenkchen` | Aufgerichteter Drache mit gespreizten Flügeln, Stern-Medaillon und kleinem Sternenatem |
| `pip` | Winkender Roboter mit fest gehaltenem Schraubenschlüssel und schwebenden Schrauben |
| `rollo` | Blick über die Front mit angehobenem Rohr und kleinen Staubwölkchen an den Ketten |
| `nova` | Exo-Pilotin mit erhobener Raketenfaust und dezent glimmenden Handgelenkdüsen |

## Einbau

- [Ohne Hintergrund](ohne_hintergrund/) für das Fenster mit separat gezeichneter Fläche. Die Figuren und ihre kleinen Effekte liegen im PNG mit echtem Alphakanal.
- [Mit Hintergrund](mit_hintergrund/) für ein direkt einsetzbares Bild auf `#221935`. Beide Varianten verwenden pro Champion dieselbe Größe von 1122 × 1402 Pixeln und denselben Bildausschnitt.
- Die Textur anhand der Champion-ID laden. `motivbereich_px` gibt das sichtbare Rechteck als `[x, y, breite, höhe]` an. Die Werte gelten für die Positionierung des Motivs, auch wenn die Hintergrundfassung als vollständiges Bild geladen wird.
- Seitenverhältnis beibehalten und das Motiv horizontal zentrieren. `maximale_motivhoehe_relativ_zur_anzeigehoehe` begrenzt die Höhe relativ zur Bildfläche. Rollo bleibt etwas niedriger, damit seine breite Silhouette dem Maßstab der Reihe entspricht. Die Anzeigehöhe und Standlinie sind Vorschlagswerte für den Einbau.

Die vier Einzelbilder enthalten keine Namen. Godot kann den Namen aus dem vorhandenen UI anzeigen. Die Prüfung im echten Auflevel-Fenster steht noch aus.
