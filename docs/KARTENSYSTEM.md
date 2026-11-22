# Kartensystem im Kampf – neuer Vorschlag (Stand 19.11.2026)

Nach jeder geschafften Welle wählt man eine Karte. Vorschlag des Nutzers vom 14.11.2026, Entscheidungen vom
16.11.2026 (`game/scripts/battle/card_rules.gd`).

- **Im Spiel:** Meisterfähigkeit (Regel 3) seit 0.10.31, Mockup „Karten-Meister“ freigegeben am 19.11.2026;
  Platzgrenze (Regel 2) seit 0.10.35, freigegeben am 20.11.2026; Symbiosen (Regel 4) seit 0.10.37, Mockup
  „Karten-Symbiose“ freigegeben am 20.11.2026.
- **Im Spiel seit 0.10.46** (Wunsch 22.11.2026: „das muss kommen, sehr wichtig“): „Neue Champions erst ab Welle 5“,
  ab Level 2 (im ersten Kampf mit dem Tutorial kommt der zweite Champion weiter nach Welle 1), nicht im Mehrspieler.
  `--karten-alt` schaltet alle neuen Regeln aus (Vergleich wie vor 0.10.31).
- Labor 22.11.2026 mit den kurzen Wellen (9/9/8/8/7), je 4 Seeds, Siegquote anfaenger / durchschnitt / zahlend:

  | Level | bisher | ab Welle 5 |
  |---|---|---|
  | 2–18 | 100 / 100 / 100 | 100 / 100 / 100 |
  | 20 | 100 / 100 / 100 | 75 / 100 / 100 |
  | 25, 30 | 100 / 100 / 100 | 75 / 100 / 100 |
  | 35 | 0 / 75 / 100 | 0 / 100 / 100 |
  | 40 | 0 / 75 / 75 | 0 / 75 / 100 |
  | 45 | 0 / 75 / 100 | 0 / 75 / 100 |
  | 50 | 0 / 75 / 100 | 25 / 75 / 100 |

  Mit dem Ausgleich (bis Welle 8: allein −45 %, zu zweit −20 % Gegnerleben, ab Level 21) liegt die Regel gleichauf.
- Symbiose-Karte wie im Mockup: Kärtchen mit beiden Spezialmotiven, Kurztitel (`CardRules.SYMBIOSE_SHORT`) und beiden
  Namen in Mint; Detailfeld mit beiden Porträts, Plakette „∞ SYMBIOSE“ (Zeichen als Linie gezeichnet) und „EINMALIG“.
  Liegt ein eigenes Motiv `game/ui/karten/sym_<id>.webp` vor (Prompt 4), ersetzt es das Motivpaar.
- Kartentitel auf den Kärtchen werden erst verkleinert (bis 10,5), bevor etwas abgeschnitten wird; Rakete heißt dort
  wie im Mockup „Explosion“.
- Kartenwahl (`game/scripts/ui/card_pick.gd`) wie im Mockup: im Detailfeld „Stufe 2 → 3“ mit Plakette „★ MEISTER“,
  die Meister-Stufe grün mit goldenem Ring, darunter die Zusatzzeile in Gold (`CardRules.meister_line`, für die
  Spezialfähigkeit je Champion eigener Text in `CardRules.MEISTER_SPECIAL`). „Plätze 2/3“ zeichnet die Kartenwahl nur
  mit der Platzgrenze (`plaetze`).
- Prüfbild: `--autotest --level=12 --squad=fritzi --cardshot=bild.png,fritzi:special@2+fritzi:ult+machine:tank,0`
  (`@N` setzt die Fähigkeit vorher auf Stufe N).
- Labor 19.11.2026 (Level 25/30/35/40, je 3 Seeds, durchschnitt und anfaenger): mit und ohne Meisterfähigkeit
  (`LAB_ARGS=--karten-alt`) genau gleiche Ergebnisse. Bei rund 13 Karten je Kampf auf drei Champions verteilt bringt
  der automatische Spieler kaum eine Waffenfähigkeit auf Stufe 3; wer gezielt dreimal dieselbe Karte nimmt, bekommt
  den Zusatz. Die Obergrenze 3 (bisher Schaden und Feuerrate bis 5, Kritisch bis 4) wird im Labor nicht erreicht.
- Labor 20.11.2026 (Level 25/30/35/40, je 3 Seeds): „nur Meister“ und „Meister + Plätze“ gleich (durchschnitt 100 %,
  anfaenger 42 % Siege). Der automatische Spieler nimmt je Kampf nur 3 bis 5 verschiedene Waffenfähigkeiten über alle
  drei Champions, die Grenze greift bei ihm selten; Meisterfähigkeiten 0,1–0,2 je Kampf.
- Labor 20.11.2026 (gleiche Level und Seeds) mit und ohne Symbiose: Siegquoten gleich (durchschnitt 100 %, anfaenger
  42 %). Symbiosen kommen bei „durchschnitt“ in etwa jedem fünften Kampf vor (0,2 je Kampf), bei „anfaenger“ nicht:
  dafür muss das passende Paar im Team sein.

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
- Sieben Symbiose-Motive von ChatGPT (Prompt 4)
- ~~„Neue Champions erst ab Welle 5“~~: entschieden 22.11.2026, im Spiel seit 0.10.46 (Tutorial-Kampf ausgenommen)

## Kampfkarten der Champions (freigegeben 17.11.2026)

Jeder der zwölf Champions hat zwei Kampfkarten (`Hero.SKILLS` in `game/scripts/battle/hero.gd`, Werte je Stern in
`Hero.skill_value`), die nach einer Welle wie die anderen Heldenkarten gezogen werden, je bis 3 Sterne. Übersicht mit
Werten, Wirkung und Testbelegen: Artefakt „Kampfkarten der Champions“. Vom Nutzer am 17.11.2026 alle 24 freigegeben.
Prüfen im Test: `--faehigkeiten=3` setzt alle Karten auf Stern 3 und gibt am Ende aus, wie oft jede gewirkt hat.
