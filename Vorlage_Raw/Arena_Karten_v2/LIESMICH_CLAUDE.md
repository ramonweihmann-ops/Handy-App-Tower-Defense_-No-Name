# Arena-Schlachtfelder für „Station am Wurmloch“

Beide Hintergründe sind deckende RGB-PNGs mit **780 × 1688 Pixeln**. Die Laufbahn liegt bündig im Stadionboden. Die schmalen Leuchtkanten markieren die Laufbahn, der Tunnel sitzt hinter der oberen Bahnkante. Die Anzeigetafel darüber ist leer und wird vom Spiel beschriftet.

| Datei | Modus und Gestaltung |
|---|---|
| `ueberleben_arena.png` | Endloses Überleben. Violett-goldene Arena mit orange-rotem Tunnel. |
| `multiplayer_arena.png` | Mehrspieler. Blau-violette Arena mit je einer blauen, roten, grünen und gelben Fahne. |
| `uebersicht.png` | Je Arena die alte und die neue Fassung nebeneinander. |
| `BILDANWEISUNGEN.json` | Verwendete Prompts und GitHub-Referenzpfade. |

## Maßprüfung

Die Koordinaten beziehen sich auf die fertigen Bilder ab der linken oberen Ecke. Gemessen wurde am Übergang der Tunnelsohle zur Laufbahn, an den bündigen seitlichen Lichtkanten und an der unteren Bodenfuge. Die Leuchtkanten haben einige Pixel Breite. An der violetten Vorderkante wurden die seitlichen Kanten bis zum Schnitt mit der hellen Querlinie verlängert.

| Bild | Oben links | Oben rechts | Unten links | Unten rechts |
|---|---:|---:|---:|---:|
| Soll | (280, 294) | (500, 294) | (64, 1158) | (716, 1158) |
| Überleben | (280, 294) | (499, 294) | ca. (65, 1158) | ca. (715, 1158) |
| Mehrspieler | (280, 294) | (499, 294) | (64, 1158) | (716, 1158) |

Die generierten Rohbilder wurden auf die Maßschablone registriert. Dabei wurde der Tunnel an den Bahnstart gesetzt und der Übergang zur Verteidigungsplattform auf das vorgegebene Raster ausgerichtet. Die gemessenen Eckpositionen liegen innerhalb der Toleranz von etwa ±6 Pixeln. Das Spiel kann den vorhandenen Gegnerpfad auf **x = 390** und die Verteidigungsplattform ab **y = 1169** verwenden. Die ersten 110 Pixel bilden den ruhigen Bereich für die Kopfleiste.

## Einbau

Die zwei fertigen PNGs sind die Hintergrundgrafiken. Gegner, Zaun, Helden, Bildschirmtexte und HUD setzt das Spiel darüber. Den Sollwert **y = 1158** für das Bahnende verwenden. Die Pixelprüfung bezieht sich auf die exportierten PNGs.

