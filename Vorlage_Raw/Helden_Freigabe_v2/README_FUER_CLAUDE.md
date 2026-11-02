# Freigegebenes Heldendesign und 3D-Produktionsvorgabe

## Lieferstatus

Der Nutzer hat die beiliegende vereinfachte 3D-Designübersicht gestalterisch freigegeben. Die PNG ist eine gerenderte Bildvorlage, keine Modelldatei. Dieses Paket enthält noch KEINE GLB-Dateien, keine Skelette und keine geprüften Animationen. Für den Kampf müssen die acht Figuren anhand dieser Vorlage tatsächlich modelliert, texturiert, mit Skeletten versehen und animiert werden. Die stärker detaillierte frühere Designübersicht ist nicht die aktuelle Freigabe.

## Verbindlicher Stil

Erwachsene menschliche Figuren mit sympathischem, leicht stilisiertem Gesicht und gut lesbaren Silhouetten. Große ruhige Stoff- und Lederflächen, wenige Gurte und Taschen, zurückhaltende Space-Module und cyanfarbene Akzente. Keine überladenen Rüstungen, keine fotorealistische Mikrotextur und keine kleinkindhaften Proportionen. Charaktertypen, Frisuren, Farben und klassische mechanische Waffen aus der freigegebenen Übersicht erhalten. Die Waffen nicht in Laser- oder Plasmawaffen umgestalten.

Oben von links: Dusty Jo, Iska, Brocken, Volta. Unten von links: Kalle, Käpt'n Margot, Lynx, Fritzi. Die Vorlage zeigt Präsentationsposen; diese sind keine verbindlichen Animations- oder Bindeposen.

## Anforderungen an echte Kampfmodelle

- GLB, glTF 2.0, mit eingebetteten Texturen; keine externen Texturabhängigkeiten.
- Y zeigt nach oben. Ein Held ist ungefähr 2 Einheiten groß; vorgeschlagener gemeinsamer Ursprung am Boden zwischen den Füßen. Abweichende Körpergrößen und Blickrichtung vor Integration einheitlich mit dem Spiel abstimmen.
- Jede Figur benötigt ein funktionierendes Skelett mit korrekt zugeordneten Hautgewichten. Die Waffen müssen bei Lauf-, Dreh- und Schussbewegungen passend mitgeführt werden.
- Heldenanimationen exakt: `Idle`, `Run`, `Shoot`, `Hit`, `Death`.
- Gegneranimationen exakt: `Walk`, `Attack`, `Hit`, `Death`.
- Höchstens 15.000 Dreiecke pro kompletter Figur einschließlich dargestellter Waffe und Zubehör; möglichst im Bereich 10.000–15.000 oder darunter, sofern die Gestaltung erhalten bleibt.
- Jede eingebettete Textur höchstens 1024 × 1024 Pixel. Klare Materialien, begrenzte Materialwechsel und saubere, zur Beleuchtung des Spiels passende Oberflächen.
- Nutzung im Spiel einschließlich kommerzieller Veröffentlichung muss für Modell, Texturen und Animationen nachweisbar erlaubt sein. Diese Anforderung ist noch KEIN Lizenznachweis. Bei Fremdmaterialien Herkunft, Lizenz, notwendige Namensnennung und etwaige Einschränkungen pro Datei dokumentieren. Bei eigenen oder generierten Modellen ebenfalls Produktionsquelle und geltende Nutzungsbedingungen dokumentieren.

## Abnahme pro GLB

1. Import in Godot ohne fehlende Texturen, Fehler oder externe Dateien.
2. Tatsächliche Modellhöhe und Y-Ausrichtung prüfen.
3. Dreiecke und Texturabmessungen am exportierten GLB prüfen.
4. Vorhandensein von Skelett, Hautgewichten und sämtlichen exakt benannten Animationen prüfen; bloße leere Animationsspuren reichen nicht.
5. Alle Bewegungen im Spiel abspielen: Laufen und Drehen ohne auseinanderfallende Körperteile, stabiler Waffengriff, plausibler Schuss und Rückstoß, Trefferreaktion, Tod ohne unerwünschtes Rückspringen. Laufanimationen für die vorhandene Bewegungslogik abstimmen, damit es keine doppelte Verschiebung gibt.
6. Lesbarkeit aus tatsächlicher Spielkamera und Leistung auf dem Zielhandy mit mehreren gleichzeitig sichtbaren Helden und Gegnern testen.
7. Kommerzielle Nutzungsrechte anhand der mitgelieferten Belege prüfen.

## Bilder bleiben Bilder

Schlachtfeldhintergründe, Brücken und Böden, gemalte Basisgebäude, Symbole, Truhen, Rahmen und Kartenmotive dürfen weiterhin als PNGs eingebunden werden. Diese Unterscheidung betrifft das Ausgabeformat; für Kampfhelden und Kampfgegner sind Bilder kein Ersatz für GLB-Modelle.

Für Gegner sind in diesem Paket lediglich die technischen Anforderungen enthalten. Ein konkretes neues Gegnerdesign wurde hier noch nicht vorgelegt oder freigegeben.

