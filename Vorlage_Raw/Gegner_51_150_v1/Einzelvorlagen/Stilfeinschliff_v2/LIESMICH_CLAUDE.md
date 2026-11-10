# Gezielter Stilfeinschliff – Version 2

Stand: 10.11.2026. Der Nutzer hat die Umsetzung der Stil-Empfehlung beauftragt und ausdrücklich ergänzt, dass der Schlundwächter nur geringfügig verändert werden soll.

## Drei gezielte Überarbeitungen

- **11_boss.png – Himmelswächter:** relativ größerer Kopf, kürzere und kräftigere Körperproportionen, weichere Hände, Stiefel und Panzerkanten. Weiß, Hellblau und Gold, Helm, Gesicht und zwei Flügel bleiben erkennbar erhalten. Der entschlossene Ausdruck bleibt; keine Babyfigur.
- **08_boss.png – Kristallgolem:** hauptsächlich weichere Übergänge an Händen, Gelenken, Stiefeln und Panzerkanten. Große Kristalle und die facettierte violett-türkise Rüstung bleiben erhalten. Keine zusätzlichen Splitter oder Texturdetails.
- **15_boss.png – Schlundwächter:** nur sehr dezente Abrundungen und weichere Übergänge. Silhouette, Proportionen, Helm, Schultern, Brustkern sowie Violett, Gold und Cyan bleiben weitgehend erhalten. Der markante Endboss-Charakter ist ausdrücklich gewünscht.

Die übrigen Monster wurden für diesen Feinschliff nicht neu erzeugt. Die bisherigen drei PNGs bleiben bytegleich im Unterordner `bisher/` erhalten. Die überarbeiteten PNGs stehen auch direkt im übergeordneten Ordner als aktuelle Vorlagen. Diese Version liegt zusätzlich als dokumentiertes Paket vor; `vergleich_vorher_nachher.png` zeigt links die bisherige und rechts die angepasste Fassung. Der Nutzer hat anschließend beauftragt, alles in dieser Fassung für Claude bereitzustellen. Die drei neuen Fassungen sind deshalb die aktuellen Bildvorlagen. Kein Spielcode oder bestehendes GLB wurde ersetzt.

## Technik und Anatomie

Alle drei Einzelbilder: **1024 × 1024 PNG, RGBA mit echter Transparenz**, Motiv mittig mit mindestens etwa zehn Prozent freiem Rand. Keine Bodenplatte, kein Schlagschatten, kein Text, keine frei schwebenden Effekte. Die Formatierung beschränkt sich auf proportionale Größenanpassung und transparenten Rand.

| Datei | Arme | Beine | Flügel | Fangarme |
|---|---:|---:|---:|---:|
| 11_boss.png | 2 | 2 | 2 | 0 |
| 08_boss.png | 2 | 2 | 0 | 0 |
| 15_boss.png | 2 | 2 | 0 | 0 |

Die Gliedmaßen wurden visuell gezählt. Hände, Füße und Flügel sind vollständig sichtbar. Die Frontansicht und offene A-Pose bleiben als Grundlage für die spätere Modellproduktion erhalten. Bei einem erzeugten 3D-Modell muss die Anatomie trotzdem erneut aus mehreren Richtungen geprüft werden.

`uebersicht.png` zeigt die neuen Varianten gemeinsam. `DATEIPRUEFUNG.json` enthält Abmessungen, Alpha-Motivgrenzen und Prüfsummen, `BILDANWEISUNGEN.json` die verwendeten Prompts und Referenzen. Es wurde ausschließlich die eingebaute Bildgenerierung verwendet, kein Meshy, kein Rigging und keine zusätzlichen kostenpflichtigen Dienste.

## Einbauhinweis

Beim Vergleich und späteren 3D-Test dieselbe Kamera, Beleuchtung und Materialrauheit für alte und neue Figuren verwenden. Sonst kann trotz passender Formen ein Stilbruch durch die Darstellung entstehen. Keine zusätzlichen realistischen Kratzer, Gravuren oder kleinen Panzerfacetten ergänzen. Die fehlenden Vorlagen `11_leicht.png` und `12_boss.png` werden durch dieses Paket nicht ergänzt; ihr Status im Hauptpaket bleibt offen.
