# Ranglisten, Ligen und Überleben: Auftrag für ChatGPT (Stand 16.11.2026)

**Reihenfolge:** Auftrag 1 von 5 (Übersicht in `Vorlage_Raw/AUFTRAEGE_REIHENFOLGE.md`).
**Kosten: keine.** Nur die eingebaute Bildgenerierung im bestehenden Konto, keine weiteren Dienste.

## Für uns: Ligen-Vorschlag (vor dem Abschicken vom Nutzer bestätigen)

Die sechs Ligen im Spiel bleiben, mit gleichen Farben und gleichen Pokalgrenzen (`game/scripts/mp_data.gd`). Neu sind
drei Stufen je Liga und eine siebte Liga ganz oben. So gibt es öfter einen kleinen Aufstieg, und die besten Spieler
haben eine eigene Bühne.

| Liga | Stufen | ab Pokalen | Farbe | Motiv des Abzeichens |
|---|---|---|---|---|
| Bronze | III · II · I | 0 / 130 / 260 | Kupfer-Orange | einfaches Schild mit einem Stern |
| Silber | III · II · I | 400 / 600 / 800 | Silber | Schild mit Flügelansatz |
| Gold | III · II · I | 1.000 / 1.270 / 1.540 | Gold | Schild mit zwei Flügeln und Krone |
| Kristall | III · II · I | 1.800 / 2.130 / 2.460 | Violett | Kristallschild mit Kristallzacken |
| Sternen | III · II · I | 2.800 / 3.200 / 3.600 | Himmelblau | Schild mit Sternenkranz |
| Galaxie | III · II · I | 4.000 / 4.500 / 5.000 | Pink-Magenta | Schild mit Spiralgalaxie und großen Flügeln |
| **Legende** (neu) | keine, dafür Platz in der Weltrangliste | 5.500 | Gold-Regenbogen | Krone über einem Planeten mit Ring, prächtigste Form |

- Die Stufe (III, II, I) zeichnet das Spiel selbst als kleine Sterne unter dem Abzeichen. Deshalb braucht jede Liga
  nur **ein** Abzeichen.
- **Überleben** bekommt eine eigene Rangliste nach Durchhaltezeit. Alle 3 Minuten wird es schwerer. Für jede
  geschaffte Zeitstufe gibt es eine Medaille: 3, 6, 9, 12, 15 und 20 Minuten. Die Farben folgen den Ligen.

---

## Text für ChatGPT

Bilder anhängen (alle in `Vorlage_Raw/Ranglisten_Referenz/`):
- `rangliste_entwurf.png`: unser Ranglisten-Bildschirm (Siegertreppchen, Liste, Aufstiegszone)
- `symbole_vorhanden.png`: unsere bisherigen Symbole, an deren Stil sich alles richten soll
- `spielerbilder_vorhanden.png`: unsere zwölf Champions als runde Spielerbilder

---

Ich entwickle ein Handy-Tower-Defense-Spiel (hochkant, Comic-Stil im Weltraum, Godot). Spieler treten im
Mehrspieler gegeneinander an und steigen in Ligen auf. Dazu kommt ein Modus „Überleben“ mit eigener Rangliste:
Wer hält am längsten durch? Der Ranglisten-Bildschirm ist gestaltet (Bild `rangliste_entwurf.png`). Es fehlen die
Grafiken für Ligen, Pokale, Spielerrahmen und Überleben. Bitte genau diese Bilder erstellen, nichts weiter.

**Stil (wie `symbole_vorhanden.png`):** weiche, glänzende Comic-Schattierung, kräftige Farben, Licht von links oben,
kein Fotorealismus, keine dicke schwarze Kontur. Freundlich und für Kinder ab 6 geeignet, aber edel genug, dass
man stolz darauf ist. **Keine Schrift, keine Zahlen, keine Buchstaben** auf den Bildern (das Spiel schreibt selbst),
keine Logos, nichts von anderen Spielen nachmachen.

**Wichtig für alle Abzeichen:** Die sieben Liga-Abzeichen sind eine Familie. Gleiche Grundform (ein Wappenschild),
gleiche Größe im Bild, gleiche Blickrichtung (frontal). Von Liga zu Liga werden sie **sichtbar prächtiger**: mehr
Flügel, mehr Glanz, größere Krone. Man muss die Rangfolge auf einen Blick erkennen, auch ganz klein (im Spiel
40–120 Punkte breit).

### A. Liga-Abzeichen (7 Bilder)

| Datei | Liga | Farbe | Motiv |
|---|---|---|---|
| `liga_bronze.png` | Bronze | Kupfer-Orange (#e8964a / #a8561a) | einfaches, rundliches Schild mit einem Stern in der Mitte |
| `liga_silber.png` | Silber | Silber (#e6eaee / #8d949c) | Schild mit Stern, links und rechts kleine Flügelansätze |
| `liga_gold.png` | Gold | Gold (#ffe27a / #c8901a) | Schild mit Stern, zwei Flügel, kleine Krone oben |
| `liga_kristall.png` | Kristall | Violett (#b48cff / #5a3fd8) | Schild aus Kristall mit Kristallzacken als Flügeln und Krone, leichtes Funkeln |
| `liga_sternen.png` | Sternen | Himmelblau (#8fe8ff / #2a8ad8) | Schild mit Kranz aus kleinen Sternen, große Flügel, Krone |
| `liga_galaxie.png` | Galaxie | Pink-Magenta (#ff9fe0 / #c2508f) | Schild mit Spiralgalaxie in der Mitte, große prächtige Flügel, Krone mit Edelstein |
| `liga_legende.png` | Legende | Gold mit Regenbogenschimmer | das prächtigste: Krone über einem Planeten mit Ring, goldene Flügel, Strahlenkranz |

### B. Pokale und Saison (5 Bilder)

| Datei | Motiv | Wo im Spiel |
|---|---|---|
| `pokal_symbol.png` | einzelner goldener Pokal, schlicht, gut lesbar auch bei 20 Punkten | Pokalzahl oben in der Leiste und in der Liste |
| `saisonpokal_1.png` | großer goldener Siegerpokal mit Stern, leuchtend | Saisonende, Platz 1 |
| `saisonpokal_2.png` | derselbe Pokal in Silber | Saisonende, Platz 2 |
| `saisonpokal_3.png` | derselbe Pokal in Bronze | Saisonende, Platz 3 |
| `saison_truhe.png` | Truhe in Violett-Gold mit Pokal-Prägung auf dem Deckel, leicht geöffnet, Licht strahlt heraus | Belohnung zum Saisonwechsel |

### C. Rahmen für Spielerbilder (10 Bilder)

Runde Rahmen, die um unsere runden Spielerbilder gelegt werden (`spielerbilder_vorhanden.png`). **Die Mitte ist
komplett durchsichtig** (ein Kreis mit etwa 62 % des Bilddurchmessers), damit das Spielerbild darunter zu sehen ist.

| Datei | Motiv |
|---|---|
| `rahmen_bronze.png` … `rahmen_galaxie.png` (6 Dateien) | Ring in der Farbe der Liga, mit dem Schmuck des Liga-Abzeichens (Stern, Flügel, Krone) |
| `rahmen_legende.png` | Ring wie das Legende-Abzeichen, mit Strahlenkranz |
| `rahmen_platz1.png` | goldener Ring mit großer Krone oben und Lorbeerkranz, für den Besten der Weltrangliste |
| `rahmen_top10.png` | silber-goldener Ring mit kleiner Krone, für die Top 10 |
| `rahmen_top100.png` | Ring mit Sternen, für die Top 100 |

### D. Überleben (8 Bilder)

| Datei | Motiv | Größe |
|---|---|---|
| `ueberleben_titel.png` | Titelbild des Modus: unsere Station auf der Brücke, von allen Seiten kommen Gegnerscharen, darüber eine große Stoppuhr, die rot glüht. Spannend, nicht gruselig. **Nicht durchsichtig**, ohne Schrift. | 780 × 420 |
| `ueberleben_symbol.png` | Stoppuhr mit Unendlich-Zeichen auf dem Zifferblatt, für die Kachel im Menü | 512 × 512 |
| `medaille_3min.png` | runde Medaille mit Stoppuhr-Motiv, Bronze | 512 × 512 |
| `medaille_6min.png` | dieselbe in Silber | 512 × 512 |
| `medaille_9min.png` | dieselbe in Gold | 512 × 512 |
| `medaille_12min.png` | dieselbe in Kristall-Violett | 512 × 512 |
| `medaille_15min.png` | dieselbe in Sternen-Blau | 512 × 512 |
| `medaille_20min.png` | dieselbe in Galaxie-Pink mit Flammenkranz, die prächtigste | 512 × 512 |

Die Medaillen sind wie die Liga-Abzeichen eine Familie: gleiche Form, von Stufe zu Stufe prächtiger.

### E. Gegnersuche (1 Bild)

| Datei | Motiv | Größe |
|---|---|---|
| `gegnersuche_hintergrund.png` | Hintergrund für die Gegnersuche: dunkler Weltraum (dunkelviolett #1a1240 bis #2a1f63), in der Mitte ein großer Radarkreis mit leuchtenden Ringen und einem Lichtstrahl, ein paar Sterne. Ruhig, damit Schrift und Spielerbilder darüber gut lesbar sind. **Nicht durchsichtig**, ohne Schrift. | 780 × 1688 |

## Technik

- Alle Bilder außer Titelbild und Hintergrund: einzeln als PNG mit **transparentem Hintergrund**, **512 × 512 Pixel**,
  Motiv mittig mit etwa 8 % Rand.
- Gut lesbar auch ganz klein.
- Zusätzlich `uebersicht.png`: alle Bilder geordnet nach A–E auf dunkelviolettem Grund (#2a1f63), zur Kontrolle.

## Bitte liefern

Ordner `Vorlage_Raw/Ranglisten_v1/` auf GitHub, Repository `Handy-App-Tower-Defense_-No-Name`,
Branch `claude/amazing-hypatia-yl59v4`:
1. die 31 Bilddateien (Namen wie oben)
2. `uebersicht.png`
3. `LIESMICH_CLAUDE.md`: Tabelle je Datei mit Motiv, Größe und Verwendung (aus diesem Auftrag übernehmen)
4. `BILDANWEISUNG.txt`: die verwendeten Bildprompts

Nur die eingebaute Bildgenerierung im bestehenden Konto verwenden, keine weiteren kostenpflichtigen Dienste.
