# Hauptbildschirm – eine Kugel mit horizontalem Saturnring

Stand 09.11.2026, Revision v8. `hauptbildschirm_aktuell_v5.png` ist die neue zusammengesetzte Fassung in 852 × 1846 Pixeln (PNG/RGB). Der Dateiname bleibt für den bestehenden Einbau erhalten.

Die vorherige Planetengrafik und sämtliche alten Ringbögen wurden im betroffenen Bereich durch eine mit der eingebauten Bildgenerierung erzeugte planetenfreie Hintergrundplatte ersetzt. Darauf liegt genau eine einzelne, separat erzeugte und einheitlich skalierte Planetenkugel. Es gibt keinen zweiten Planeten dahinter. Der Ring liegt horizontal um dieselbe Kugel; sein hinterer Teil ist verdeckt, sein vorderer Bogen davor sichtbar. Die rechte Bildschirmkante schneidet das Objekt wie bisher teilweise ab. Der Ring muss nicht vollständig im Bild sichtbar sein.

Zusätzlich enthalten: `ringplanet_einzeln.png` als transparentes Einzelobjekt und `hauptbildschirm_ohne_ringplanet.png` als Hintergrund mit unveränderter UI. Nicht das Einzelobjekt noch einmal auf das bereits zusammengesetzte Endbild legen, sonst würde der Planet doppelt erscheinen. Für den einfachen Einbau nur `hauptbildschirm_aktuell_v5.png` verwenden.

Die UI-Silhouetten und Schrift liegen zuletzt als geschützte Originalpixel über dem Planeten. Kopfleiste, Titelbox, Boss, Pfad, linke Angebote, Spielen-Knopf und Reiterleiste bleiben erhalten. Die Differenzprüfung bestätigt null geänderte Pixel außerhalb der örtlichen Bearbeitungsmaske und null geänderte Pixel in der UI-Schutzmaske. Innerhalb des Planeten-/Ringbereichs einschließlich des ursprünglichen Ringglanzes wurde die Grafik neu aufgebaut. Keine Spielcodeänderung, keine anderen Pakete geändert.

`vergleich_ring.png` zeigt die ursprüngliche Vorlage und diese Fassung. `PRUEFUNG.json` enthält die Position und den einheitlichen Skalierungsfaktor des Einzelobjekts. Beide neuen Bildelemente wurden mit der eingebauten Bildgenerierung erzeugt. Technische Ebenenzusammensetzung und Pixelprüfung erfolgten lokal. Keine zusätzlichen kostenpflichtigen Dienste.
