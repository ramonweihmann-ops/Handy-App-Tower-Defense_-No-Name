# Multiplayer „4 Kommandanten“

Stand: Pilot (November 2026). Im Pilot sind die drei anderen Kommandanten **Computergegner**, die wie
echte Spieler auftreten (Name, Held, Pokale). Das kostet nichts und braucht keinen Server. Zum Release
sollen echte Spieler gegeneinander antreten, mit Emotes, ohne Chat (braucht einen Server, verursacht
laufende Kosten; vorher abstimmen).

## Ablauf

1. Hauptbildschirm → Kachel **Modi** → **Spielmodi** → Multiplayer **SPIELEN** (5 Energie).
2. **Gegnersuche**: drei Kommandanten werden nacheinander gefunden („VS“), dann der erste Held.
3. **Kampf** (5:00 Minuten, festes Tempo für alle, kein Tempo-Knopf): Links oben die Live-Rangliste
   der vier Kommandanten mit besiegten Gegnern, rechts die Restzeit und der Hinweis auf den Boss.
   Wer fällt, wird in der Liste grau mit „RAUS · Zeit“. Pause ist möglich; „Aufgeben“ zählt wie
   das Fallen der Station.
4. **Ergebnis**: Platz 1–4 mit besiegten Gegnern, Zeit, Punkten und Pokalen, darunter die Belohnung.
5. **Rangliste**: Liga mit 30 Kommandanten, Siegertreppchen, Aufstiegszone, eigener Platz unten.

## Wellen

| Wert | | Code |
|---|---|---|
| Dauer | 300 s, 7 Wellen à ≈43 s (Karte nach jeder Welle) | `MpData.MATCH_TIME`, `WAVES` |
| Nachschub | Gegner kommen, sobald Platz auf der Bahn ist: 8 gleichzeitig in Welle 1, +2 je Welle. Wer schneller besiegt, bekommt schneller neue Gegner und kann Punkte sammeln. | `ALIVE_BASE`, `ALIVE_PER_WAVE`, `SPAWN_GAP` |
| Gegnerleben | Grundleben der Station × Abstimmung je Levelbereich × 1,22 je Welle (kurz und heftig) | `HP_WAVE`, `HP_TUNE` |
| Boss | schon in Welle 5, angepasst an die Station: schaffbar mit guter Aufstellung und etwas Kartenglück, aber nicht immer | `BOSS_WAVE`, `BOSS_HP`, `BOSS_TUNE` |
| Station | richtet sich nach dem Fortschritt im Abenteuer (höchstes freies Level) | `station_level()` |

## Wertung

- **10 Punkte je besiegtem Gegner** (Boss **100**) und **2 Punkte je Sekunde**, die die Station hält.
  Wer bis zum Schluss durchhält, bekommt die volle Zeit.
- Rangfolge nach Punkten, bei Gleichstand längere Zeit, dann mehr besiegte Gegner.
- **Feste Regel:** Wer früher fällt **und** weniger Gegner besiegt hat, steht immer hinter dem anderen,
  auch wenn ihn ein Boss nach Punkten nach vorn gebracht hätte. Damit ist sicher: **Wer zuerst fällt
  und am wenigsten besiegt hat, wird Letzter.** Wer früher fällt, aber mehr besiegt hat, kann trotzdem
  gewinnen (Punkte farmen lohnt sich), und wer die Mauer länger hält, sammelt Zeitpunkte.
- Geprüft in `game/tests/mp_fairness.gd` an 50.000 zufälligen Kämpfen (läuft in `scripts/test.sh`).

## Liga, Pokale, Belohnung

| Liga | ab Pokalen | Pokale Platz 1 / 2 / 3 / 4 |
|---|---|---|
| Bronze | 0 | +30 / +15 / +5 / −5 |
| Silber | 400 | +30 / +12 / 0 / −10 |
| Gold | 1.000 | +30 / +10 / −5 / −15 |
| Kristall, Sternen, Galaxie | 1.800 / 2.800 / 4.000 | +30 / +8 / −10 / −20 |

Nie unter 0 Pokale. Belohnung je Platz: Gold = Siegesgold eines Levels × 1,0 / 0,75 / 0,55 / 0,4,
Heldenkarten für die Helden im Kampf = Karten eines Siegs × 1,5 / 1,25 / 1,0 / 0,8 (mehr Erfahrung als
im Abenteuer), Pass-Punkte 30 / 20 / 15 / 10.

**Saison:** zwei Wochen. Wer gespielt hat, bekommt zum Saisonwechsel eine Truhe: golden bis Platz 5
(40 Edelsteine, 1.500 Gold, 12 Heldenkarten), sonst silbern (15 Edelsteine, 600 Gold, 5 Heldenkarten).

## Computergegner (Pilot)

Die Gegner sind aus echten Kämpfen des Spiels gemessen (`scripts/mp-lab.py` spielt Multiplayer-Kämpfe
mit den Spielerprofilen aus `game/tests/balance_profiles.gd`): besiegte Gegner je Sekunde und
Ausscheiden je Sekunde für jede Welle, Boss-Quote. Jeder Gegner bekommt eine Stärke um 1,0 (typischer
Spieler auf demselben Stand), die mit der Liga steigt (Bronze 0,96 … Galaxie 1,16) und um ±0,1 streut;
dazu schwankt jede Welle (Kartenglück). Stärke wirkt auf Tempo (Stärke^RATE_POW), Ausscheiden
(Stärke^−HAZARD_POW) und Boss (Stärke^BOSS_POW). Alles hängt nur vom Startwert ab (nachprüfbar).

**Fairness-Prüfung** (`tests/mp_fairness.gd`): Jeder gemessene echte Lauf tritt 300-mal gegen neu
gewürfelte Computergegner an. Ziel: Ein typischer Spieler landet im Mittel auf Platz 2,2–2,8; ein
stärkerer schneidet besser, ein schwächerer schlechter ab.

## Messwerte

Siehe Abschnitt „Abstimmung“ unten (wird mit `scripts/mp-lab.py` erneuert).
