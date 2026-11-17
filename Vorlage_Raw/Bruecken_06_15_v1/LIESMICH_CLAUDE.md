# Brücken 06–15 · Zwei Muster zur Spielprüfung

Diese erste Lieferung enthält den Kristallplaneten und die Wolkenstadt. Die übrigen acht Brücken folgen nach der Rückmeldung aus dem Spiel.

- Kristallplanet (`crystal_planet.png`) · Dunkles Kristallglas mit großflächigen Facetten und kleinen rosa Kristallen an den seitlichen Schienen.
- Wolkenstadt (`cloud_city.png`) · Blaugraue Schieferplatten mit versetzten Fugen, weiße Marmorbalustraden, goldene Kugeln und himmelblaue Einbauleuchten.
- [Vorher und nachher](uebersicht.png) · Die Ausschnitte zeigen die Brücken in derselben Skalierung.

## Maßprüfung

Beide Schlachtfelder sind PNGs mit 780 × 1688 Pixeln in RGB. Die Koordinaten beziehen sich auf die inneren Fahrbahnkanten, Ursprung links oben. Abgelesen im vergrößerten Ausgabebild. Die sichtbare Übergangskante kann durch Schattierung um wenige Pixel variieren.

| Datei | Oben links | Oben rechts | Unten links | Unten rechts | Größte sichtbare Abweichung vom Soll |
| --- | --- | --- | --- | --- | --- |
| `crystal_planet.png` | (280, 294) | (500, 294) | (64, 1158) | (716, 1158) | etwa 2 px |
| `cloud_city.png` | (280, 294) | (500, 294) | (64, 1158) | (716, 1158) | etwa 2 px |

Die Brücken stammen aus der eingebauten Bildbearbeitung mit den vorhandenen Schlachtfeldern als direkte Vorlage. Die neuen Brückenbereiche wurden auf das vorhandene Trapez eingepasst. Außerhalb dieser Bereiche stammen die Pixel aus den Originaldateien. An den Außenseiten der Geländer liegt ein schmaler Übergang zur Kulisse. Die komplette Plattform ab y = 1169 und die obere Kulisse bis y = 261 sind in beiden Dateien pixelgleich mit der Vorlage. Das Spiel ist der nächste Prüfschritt.
