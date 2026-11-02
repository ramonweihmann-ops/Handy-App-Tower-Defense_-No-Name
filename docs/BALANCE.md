# Balance-Bericht

Stand 02.11.2026 · nach Plasma-Erzeuger, Energiekern und höchstens 3 Helden neu abgestimmt.

Werte: Sprung ab Level 21 ×10, danach +1 % Gegnerleben je Level (vorher ×4,7 und +2,5 %), Bosse
selbst ×0,8. Boss-Level bekommen je Welt einen eigenen Faktor auf das Leben aller Gegner
(`GameData.BOSS_TUNE`: 25 ×0,7 · 30 ×0,85 · 40 ×1,05 · 45 ×0,95 · 50 ×0,6), weil dort meist
mitten im Level verloren wird, nicht am Boss.

Siegquote beim ersten Versuch je Spielerprofil (✓ im Ziel, ↑ zu leicht, ↓ zu schwer), 6 Läufe je
Level und Profil – ein Lauf mehr oder weniger sind 17 %. Zielkurve und Profile: `docs/KONZEPT.md`
(Abschnitt 9), `game/tests/balance_profiles.gd`.

## Normale Level (Lauf mit den endgültigen Werten für normale Level)

| Level | durchschnitt | zahlend | Ø Schild übrig (Sieg) | Ø Warten auf Munition |
|---|---|---|---|---|
| 21 | 100% ↑ | 100% ✓ | 89% | 0% |
| 22 | 67% ✓ | 100% ✓ | 79% | 0% |
| 28 | 50% ↓ | 100% ✓ | 86% | 0% |
| 33 | 83% ↑ | 100% ✓ | 90% | 0% |
| 43 | 67% ✓ | 100% ✓ | 96% | 0% |

## Boss-Level (Lauf mit Boss-Faktoren; Level 40 danach von ×1,15 auf ×1,05 gesenkt)

| Level | durchschnitt | zahlend | Ø Schild übrig (Sieg) | Ø Warten auf Munition |
|---|---|---|---|---|
| 25 (Boss) | 33% ↓ | 83% ✓ | 83% | 0% |
| 30 (Boss) | 50% ✓ | 33% ↓ | 75% | 0% |
| 35 (Boss) | 50% ✓ | 83% ✓ | 86% | 0% |
| 40 (Boss) | 33% ↓ | 67% ↓ | 92% | 0% |
| 45 (Boss) | 33% ↓ | 67% ↓ | 98% | 0% |
| 50 (Boss) | 33% ↓ | 83% ✓ | 100% | 0% |

## Verlauf der Abstimmung

| Variante | Sprung / Wachstum / Boss | Abweichungen |
|---|---|---|
| alt (vor Plasma) | ×4,7 / +2,5 % / ×1,22 | 13 (fast alles zu leicht, Level 50 zu schwer) |
| A | ×5,6 / +2 % / ×1,3 | 13 |
| B | ×6,2 / +1,5 % / ×1,3 | 13 |
| C | ×8 / +1 % / ×1,0 | 12 |
| D | ×10 / +1 % / ×0,8 | 12 (normale Level gut, Bosse je Welt sehr verschieden) |
| E/F | D + Faktor je Boss-Level | normale Level 3–4, Boss-Level knapp unter dem Ziel |

Erkenntnis: Normale Level reagieren kaum auf mehr Gegnerleben, bis der Sprung sehr groß ist (die
Helden haben viel Reserve, der Schild bleibt fast voll). Boss-Level reagieren dagegen stark und je
Welt verschieden.
