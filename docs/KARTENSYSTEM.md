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

## Offen

- Ergebnis Balance-Labor (Siegquoten bisher / neu / neu ohne „ab Welle 5“) und daraus nötige Anpassungen
- Mockup der neuen Karten (Meisterfähigkeit, Symbiose, belegte Plätze), danach Einbau ins Spiel und ins Tutorial
  (dort wählt man bisher nach Welle 1 einen Helden)
