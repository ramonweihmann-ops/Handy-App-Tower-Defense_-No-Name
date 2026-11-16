# Arenen neu: Bahn unten auf dem Arenaboden – Auftrag für ChatGPT (Stand 16.11.2026)

**Kosten: keine** (eingebaute Bildgenerierung). Wunsch des Nutzers vom 16.11.2026: Bei der Universums-Arena
(künftig Überleben) und der Multiplayer-Arena steigt die Bahn wie eine Brücke zur obersten Tribüne an. Richtig ist:
Die Bahn läuft **unten auf dem Arenaboden**, alle Tribünen ringsum schauen auf sie herab, und die Gegner kommen aus
einem **Tunnel unter der Tribüne** am oberen Ende der Bahn.

Vorhandene Bilder: `Vorlage_Raw/Arena_Karten_v1/universums_arena.png` und `multiplayer_arena.png`.
Maße wie bei allen Schlachtfeldern: `Vorlage_Raw/Planeten_Referenz/schablone_bruecke.png`.

---

## Text für ChatGPT

Die Bilder liegen auf GitHub (Repository Handy-App-Tower-Defense_-No-Name, Branch claude/amazing-hypatia-yl59v4):
Vorlage_Raw/Arena_Karten_v1/universums_arena.png, Vorlage_Raw/Arena_Karten_v1/multiplayer_arena.png und die
Maßschablone Vorlage_Raw/Planeten_Referenz/schablone_bruecke.png. Bitte von dort laden.

Ich entwickle ein Handy-Tower-Defense-Spiel (hochkant, Comic-Stil im Weltraum). Für zwei Spielmodi gibt es je eine
Arena als Schlachtfeld (Bilder universums_arena.png und multiplayer_arena.png). Die Gegner laufen auf einer Bahn von
oben nach unten zu unserer Verteidigungsplattform. Problem: In beiden Bildern sieht die Bahn aus wie eine Brücke, die
nach oben zur obersten Tribüne ansteigt. Das wirkt falsch. **Bitte beide Arenen so neu zeichnen:**

- Die Bahn liegt **flach unten auf dem Arenaboden**, wie eine Kampfbahn in einem Stadion. Kein Brückengeländer, das
  in die Höhe führt; seitlich nur eine niedrige Bande oder Leuchtkante.
- **Ringsum steigen die Tribünen an** (links, rechts und hinten), voll mit kleinen, angedeuteten Zuschauern, Lichtern
  und Fahnen. Man sieht alle Ränge, die von oben auf die Bahn herabschauen.
- **Am oberen Ende der Bahn** ist ein großer, leuchtender **Tunnel unter der hinteren Tribüne**. Aus ihm kommen die
  Gegner. Der Tunnel sitzt hinter dem Bahnende und verdeckt die Bahn nicht.
- Über dem Tunnel an der hinteren Tribüne eine große Anzeigetafel (ohne Schrift, ohne Zahlen, nur leuchtende Fläche;
  das Spiel schreibt selbst darauf).
- Unten bleibt unsere Verteidigungsplattform wie bisher (ab y = 1169, flach und ruhig).

**Feste Maße (wie bei allen Schlachtfeldern, Bild 780 × 1688 Pixel):** Fahrbahn oben von (280,294) bis (500,294),
unten von (64,1158) bis (716,1158), Mitte x = 390, gerade, Ende genau bei y = 1158. Die Perspektive bleibt so,
nur sieht die Fläche jetzt wie Boden aus statt wie eine Brücke. y 0–110 ohne wichtige Details (Kopfleiste im Spiel).
Fahrbahn mitteldunkel und ruhig, keine feinen Muster, damit die bunten Gegner gut zu sehen sind.

**Die zwei Arenen:**

| Datei | Modus | Stimmung |
|---|---|---|
| `ueberleben_arena.png` | Überleben (endlos) | violett-gold wie die bisherige Universums-Arena, dazu warmes Orange-Rot am Tunnel, als käme von dort ohne Ende Nachschub; dramatisch, aber freundlich |
| `multiplayer_arena.png` | Mehrspieler | blau-violett mit Fahnen in vier Farben (blau, rot, grün, gelb) für die vier Kommandanten |

Stil wie die bisherigen Bilder: hochwertiger, stilisierter Comic- und 3D-Spielgrafikstil, kräftige Farben, kein
Fotorealismus. Keine Figuren auf der Bahn, keine Gegner, keine Schrift, keine Logos.

**Technik:** PNG, genau 780 × 1688 Pixel, RGB. Danach die vier Fahrbahnecken ablesen (höchstens etwa ±6 Pixel).

**Bitte liefern** in `Vorlage_Raw/Arena_Karten_v2/`: die zwei Bilder, `uebersicht.png` (alt und neu nebeneinander),
`LIESMICH_CLAUDE.md` mit der Maßprüfung, `BILDANWEISUNGEN.json` mit den Prompts.

Nur die eingebaute Bildgenerierung im bestehenden Konto verwenden, keine weiteren kostenpflichtigen Dienste.
