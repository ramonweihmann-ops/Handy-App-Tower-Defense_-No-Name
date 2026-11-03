# Basislager: 30 Gebäude (Vorschlag zur Prüfung)

Stand 02.11.2026. Vorlage: `Vorlage_Raw/Raumbasis_30` (Gestaltung freigegeben). Werte sind ein erster
Vorschlag; vor dem Einbau rechne ich sie mit `scripts/economy-sim.py` und dem Balance-Labor nach.

## Grundregeln

- **Gebäude 01–12 gehören zu den Champions** (12 Champions, Stand 03.11.2026): 01–05 hat jeder von
  Anfang an, 06–12 kommen mit dem 6. bis 12. freigeschalteten Champion dazu.
- **Gebäude 13–30 baut man:** Jedes wird ab einem bestimmten Abenteuer-Level baubar und kostet
  dann Gold, etwa alle zwei Level ein neues (Level 13 bis 47). Die Tabelle unten nennt für 09–12 noch
  Level und Gold aus dem ersten Entwurf; die gelten jetzt nicht mehr, sie kommen mit dem 9.–12. Champion.
- **Ausbau:** Jedes Gebäude hat Stufe 1–10. Ausbauen kostet Gold, ab Stufe 6 zusätzlich Sterne.
- **Zwei Arten:** *Erzeuger* sammeln mit der Zeit etwas, das man abholt (Lager läuft voll und stoppt).
  *Verstärker* wirken dauerhaft im Kampf (kleine Prozentwerte, wachsen mit der Stufe).
- Die Basis wächst nach oben: Neue Reihen erscheinen über den alten, nichts wird verschoben.
  Gesperrte Plätze zeigen eine Baustelle mit Schloss und dem Level, ab dem gebaut werden kann.

## Die 30 Gebäude

| Nr. | Gebäude | frei ab | Art | Wirkung (Stufe 1 → Stufe 10) |
|---|---|---|---|---|
| 01 | Kommandozentrale | Start | Erzeuger | Gold 40 → 400 pro Stunde; Stufe der Zentrale begrenzt alle anderen Stufen |
| 02 | Sanitätsstation | Start | Verstärker | Schild heilt nach jeder Welle 2 % → 6 % |
| 03 | Werkstatt | Start | Erzeuger | Heldenkarten 0,5 → 5 pro Stunde (wie die heutigen Quartiere) |
| 04 | Hologrammakademie | Start | Verstärker | Erfahrung im Kampf +3 % → +15 % |
| 05 | Reaktorturm | Start | Erzeuger | Energie: 1 Punkt alle 3 Std. → alle 1 Std. |
| 06 | Kommunikationsstation | 6. Champion | Verstärker | Pass-Punkte je Sieg +2 → +10 |
| 07 | Gewächshaus | 7. Champion | Erzeuger | Gold 60 → 600 pro Stunde |
| 08 | Roboterlabor | 8. Champion | Verstärker | Plasma lädt +2 % → +10 % schneller |
| 09 | Sternwarte | Level 5 · 1.000 Gold | Verstärker | Krit-Chance +1 % → +5 % |
| 10 | Schiffswerft | Level 7 · 1.400 Gold | Verstärker | Booster laden 3 % → 15 % schneller |
| 11 | Schildgenerator | Level 9 · 1.800 Gold | Verstärker | Schild +2 % → +10 % |
| 12 | Trainingshalle | Level 11 · 2.200 Gold | Verstärker | Schaden aller Helden +1 % → +6 % |
| 13 | Kristallforschung | Level 13 · 2.600 Gold | Erzeuger | Edelsteine 2 → 10 pro Tag |
| 14 | Panzerwerkstatt | Level 15 · 3.000 Gold | Verstärker | Schaden gegen starke Gegner und Bosse +2 % → +10 % |
| 15 | Drohnenhangar | Level 17 · 3.400 Gold | Verstärker | Start-Plasma +2 → +10 |
| 16 | Alchemielabor | Level 19 · 3.800 Gold | Erzeuger | Talent-Sterne: 1 alle 24 Std. → alle 8 Std. |
| 17 | Energiespeicher | Level 21 · 4.200 Gold | Verstärker | Energie-Maximum +2 → +10 |
| 18 | Navigationszentrale | Level 23 · 4.600 Gold | Verstärker | Gold aus Kämpfen +3 % → +15 % |
| 19 | Eisforschung | Level 25 · 5.000 Gold | Verstärker | Frost (Kalle) verlangsamt 5 % → 25 % stärker |
| 20 | Feuerforschung | Level 27 · 5.400 Gold | Verstärker | Brand (Fritzi) 5 % → 25 % stärker |
| 21 | Waffenwerkstatt | Level 29 · 5.800 Gold | Verstärker | Schaden aller Helden +1 % → +6 % |
| 22 | Bibliotheksarchiv | Level 31 · 6.200 Gold | Verstärker | Heldenkarten aus Kämpfen +5 % → +25 % |
| 23 | Biolabor | Level 33 · 6.600 Gold | Verstärker | Medipack-Booster heilt 5 % → 25 % mehr |
| 24 | Teleportstation | Level 35 · 7.000 Gold | Verstärker | Plasma-Speicher +3 → +15 |
| 25 | Versorgungsdepot | Level 37 · 7.400 Gold | Erzeuger | Gold 100 → 1.000 pro Stunde |
| 26 | Veredelungsanlage | Level 39 · 7.800 Gold | Erzeuger | Heldenkarten 1 → 8 pro Stunde |
| 27 | Kommandantenresidenz | Level 41 · 8.200 Gold | Verstärker | Lager aller Erzeuger +10 % → +50 % |
| 28 | Satellitenkontrolle | Level 43 · 8.600 Gold | Verstärker | Luftschlag-Booster 5 % → 25 % stärker |
| 29 | Reparaturdock | Level 45 · 9.000 Gold | Verstärker | Schild-Reparatur (Karte) 5 % → 25 % stärker |
| 30 | Heldenmonument | Level 47 · 9.400 Gold | Verstärker | Schaden aller Helden +2 % → +10 % |

Kampfstärke aus allen Verstärkern zusammen bei voller Stufe: Schaden etwa +22 %, Schild +10 %,
Krit +5 %. Das ist so viel wie 2–3 Heldenstufen und muss in die Schwierigkeitskurve eingerechnet
werden (die Spielerprofile im Balance-Labor bekommen das Basislager dazu).

## Fragen zur Entscheidung

1. Sollen die heutigen 8 Quartiere (je Held Heldenkarten) wegfallen und durch Werkstatt (03) und
   Veredelungsanlage (26) ersetzt werden? Vorschlag: ja, Karten kommen dann für zufällige oder den
   gerade gewählten Helden.
2. „Überfall“ und „Rache“ (Angriffe auf andere Basen) bleiben später, sie brauchen einen Server.

## Grafik

Gebäude einzeln freigestellt (Variante B), Boden aus einer zweiten Vorlage mit denselben, aber leeren
Bauplätzen (bei ChatGPT angefragt). Gesperrte Plätze: Baustelle mit Schloss. Antippen öffnet das
Gebäudefenster (Name, Stufe, Wirkung jetzt → nächste Stufe, Lager mit „Abholen“, „Ausbauen“ mit Kosten).
