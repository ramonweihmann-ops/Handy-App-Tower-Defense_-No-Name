# Fritzi · Lokaler Flammenkontakt v4

Der Einschlag sitzt jetzt direkt an der dem Strahl zugewandten Körperseite. Kurze unregelmäßige Feuerzungen lenken seitlich ab und verglühen. Kein Bodenkranz und keine freistehenden Flammensymbole.

Diese freigegebene vollständige Lieferung ersetzt `Schusseffekte_fritzi_v1`. Die Zwischenfassungen v2 und v3 werden nicht benötigt. Mündung und Strahl sind identisch zur bisherigen Lieferung; nur Einschlag und Zielpositionierung wurden überarbeitet. Der Strahlendpunkt der Vorschau liegt jetzt tatsächlich am ersten Gegner statt zwischen den beiden Gegnern.

[Übersicht](UEBERSICHT.png) · [Eiswelt](FRITZI_EISWELT_VORSCHAU.gif) · [Raumdock](FRITZI_RAUMDOCK_VORSCHAU.gif) · [Ablaufdaten](ABLAUF_FRITZI.json)

## Einbau

Alle drei Effektordner gemeinsam übernehmen. Mündung an `Muzzle` binden und mit der vorhandenen Aktion `Shoot` auslösen. Mündungsblatt 4 × 2 mit 128er Kacheln, Anker (32,64). Strahlblatt 4 × 2 mit 256er Kacheln. Den Strahl mit `darstellung: bogen` von (20,128) bis (236,128) zwischen Düse und Körperkontakt aufspannen. Seine Höhe und Grafik beibehalten. Bilder 1–4 zeigen den vollen Stoß, Bilder 5–8 das Ausblenden.

Den Kontaktanker des Einschlags (128,128) an den zugewandten Körperrand setzen und positive X in Schussrichtung drehen. An getroffenen Gegnern mitführen. Weitere Gegner im vorhandenen Trefferkreis erhalten einen kleineren lokalen Kontakt; kein zusätzlicher Strahl nötig. Der Trefferkreis selbst wird nicht als Flammenfläche gezeichnet. Radius, Schaden und Brenndauer bleiben Spielwerte.

Die Bildfolge hat zwölf Bilder, 4 × 3 Raster, 256 × 256 je Kachel, 24 Bilder/s, gerades Alpha. Größenwert 1,8 m als Startvorschlag für die gesamte transparente Kachel, nicht die sichtbare Flammenfläche. Einmal abspielen. Der Einbau in Godot und die Anpassung der Kontaktpunkte an die jeweiligen Gegnerformen stehen aus.

Die Vorschau zeigt eine Montage mit Fritzis vorhandener Shoot-Bewegung auf beiden Brücken und zwei Gegnern. Effekte werden mit voller Texturdeckkraft gezeigt. Erzeugt mit eingebauter Bildgenerierung.

Die freigegebene Vorschau verwendet für den Einschlag eine vollständige Kachel von 58 × 58 Bildschirmpixeln am ersten und 48 × 48 Pixeln am zweiten Gegner bei 390 × 844 Pixeln. Das sichtbare Motiv belegt nur einen Teil der Kachel. Diese dezente Größe beim Einbau als visuelle Referenz nehmen; der Meterwert ist nur ein Startvorschlag. Nicht auf die Motivgrenzen zuschneiden oder auf den ganzen Trefferkreis vergrößern. Kontaktpunkt aus Gegnerform und eingehender Richtung bestimmen, nicht mit einem festen Versatz für alle Gegner. Gesicht und Körpermitte frei halten.

Die PNG-Bildblätter sind die Produktionsdateien, die GIFs nur Vorschauen. Reihenfolge links nach rechts, dann nächste Zeile. Keine additive Mischung und keine zusätzliche Abschwächung. Die Transparenz der Ausblendbilder bleibt wirksam. Die letzten zwei Einschlagbilder sind leer.
