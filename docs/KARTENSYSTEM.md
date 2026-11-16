# Kartensystem im Kampf – neuer Vorschlag (Stand 16.11.2026, im Balance-Labor)

Nach jeder geschafften Welle wählt man eine Karte. Vorschlag des Nutzers vom 14.11.2026, Entscheidungen vom
16.11.2026. Im Spiel nur mit dem Labor-Schalter `--karten-neu` aktiv (`game/scripts/battle/card_rules.gd`),
einzelne Teile mit `--karten-neu=held5,plaetze,meister,symbiose`.

## Regeln

1. **Neue Champions erst ab Welle 5** (`held5`): Die Karten nach Welle 1–4 sind nur Verbesserungen. Ab der Karte
   nach Welle 5 kann ein neuer Champion kommen (höchstens drei im Kampf wie bisher).
2. **Höchstens 3 Waffenfähigkeiten je Champion** (`plaetze`): Schaden, Feuerrate, Nachladen, Magazin, Kritisch und
   Spezialfähigkeit belegen je einen Platz, sobald sie Stufe 1 haben. Sind drei belegt, kommen für diesen Champion
   nur noch Karten dieser drei. Die Superfähigkeit zum Antippen (SUPER-Karte) zählt extra.
3. **Meisterfähigkeit auf Stufe 3** (`meister`): Waffenfähigkeiten haben höchstens Stufe 3. Mit der dritten Stufe
   werden sie zur Meisterfähigkeit und bekommen einen Zusatz:

| Fähigkeit | Meisterfähigkeit | Zusatz |
|---|---|---|
| Mehr Schaden | Wuchttreffer | jeder 4. Schuss macht dreifachen Schaden |
| Schneller feuern | Doppelschuss | jeder 3. Schuss trifft zusätzlich einen zweiten Gegner |
| Schneller nachladen | Blitzladen | 30 % Chance, sofort fertig nachgeladen zu haben |
| Größeres Magazin | Sparmagazin | 25 % Chance, dass ein Schuss keine Munition verbraucht |
| Kritische Treffer | Volltreffer | kritische Treffer dreifach statt doppelt |
| Spezialfähigkeit | Meister-… | wirkt wie zwei Stufen mehr (Kettenblitz springt 5- statt 3-mal weiter, Fächerfeuer 4 Kugeln mehr …) |

4. **Symbiosen** (`symbiose`): Sind zwei passende Champions im Team und haben beide ihre Spezialfähigkeit
   (mindestens Stufe 1), kann eine Symbiose-Karte kommen (einmalig, Kategorie SYMBIOSE):

| Symbiose | Champions | Wirkung |
|---|---|---|
| Explosiver Kettenblitz | Volta + Brocken | jeder vom Kettenblitz getroffene Gegner explodiert |
| Frostblitz | Volta + Kalle | der Kettenblitz macht langsamer (Frost) |
| Brandschrot | Käpt'n Margot + Fritzi | Schrot setzt Gegner in Brand |
| Schwerkraftbombe | Brocken + Nova | Raketen ziehen die Gegner am Einschlag zusammen |
| Durchschlag-Salve | Iska + Lynx | beider Kugeln durchschlagen einen Gegner mehr |
| Reparaturwucht | Pip + Rollo | jeder Wuchtschuss flickt das Schild ein wenig |
| Sternenfeuer | Fünkchen + Fritzi | der Sternenatem setzt Gegner in Brand |

Dusty Jo hat noch keine Symbiose.

## Ergebnis Balance-Labor (16.11.2026)

Level 3–50, je Level und Profil 5 Läufe, Siegquote beim ersten Versuch (durchschnitt / zahlend):

| Level | bisher | neu komplett | neu ohne „ab Welle 5“ |
|---|---|---|---|
| 3–15 | 100 / 100 | 100 / 100 | 100 / 100 |
| 20 | 100 / 100 | 100 / 100 (anfaenger 80) | 100 / 100 |
| 25 | 100 / 100 | 60 / 80 | 100 / 100 |
| 30 | 100 / 80 | 40 / 40 | 100 / 80 |
| 40 | 80 / 80 | 40 / 80 | 80 / 100 |
| 50 | 100 / 100 | 60 / 60 | 100 / 100 |

- **„Held ab Welle 5“ macht ab Level 25 deutlich schwerer**: Mit einem Champion allein bricht das Schild oft in
  Welle 6 ein, kurz nachdem der zweite dazukam. Zahlende Spieler fallen bei Level 30 und 50 unter die Zielkurve.
- **Plätze, Meisterfähigkeit und Symbiosen ändern die Siegquote kaum** (fast gleich wie bisher). Meisterfähigkeiten
  kommen vor (z. B. Dusty Jo mit Meister-Spezialfähigkeit), Symbiosen in den Probeläufen nie: Dafür müssen genau
  das passende Paar im Team sein und beide ihre Spezialfähigkeit haben.

### Ausgleich (Entscheidung 16.11.2026: Gegner leichter, solange man allein kämpft; Symbiose reicht mit einer Spezialfähigkeit)

| Fassung | L20 | L25 | L30 | L40 | L50 |
|---|---|---|---|---|---|
| Wellen 1–5 allein −20 % | 100 / 100 | 80 / 100 | 20 / 100 | 80 / 60 | 60 / 60 |
| Wellen 1–5 allein −30 % | 100 / 100 | 80 / 100 | 0 / 60 | 80 / 100 | 60 / 100 |
| **bis Welle 8: allein −45 %, zu zweit −20 %** (eingestellt) | 100 / 100 | 100 / 100 | 40 / 80 | 60 / 100 | 80 / 80 |

(Siegquote durchschnitt / zahlend, je 5 Läufe.) Verloren wurde vorher in Welle 4–6: allein, oder direkt nachdem der
zweite Champion nach Welle 5 dazukam. Mit dem eingestellten Ausgleich liegt das neue System etwa auf dem Stand des
bisherigen. Level 30 bleibt für Durchschnittsspieler schwer, aber das ist auch bisher so (Zielkurve ab Level 21:
Bosse 35–55 %, `scripts/balance-lab.py`). Der Wunsch „bis Level 30 entspannt“ betrifft deshalb die Grundkurve
(Sprung ab Level 21, `docs/KONZEPT.md` 9.1), nicht nur das Kartensystem.

## Offen

- Grundkurve: „bis Level 30 entspannt“ (Vorschlag an den Nutzer)
- Mockup der neuen Karten (Meisterfähigkeit, Symbiose, belegte Plätze), danach Einbau ins Spiel und ins Tutorial
  (dort wählt man bisher nach Welle 1 einen Helden)
