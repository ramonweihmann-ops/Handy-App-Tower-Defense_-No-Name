# Wettbewerb: Mehrspieler, Ligen, Ranglisten, Überleben – Gesamtkonzept (Entwurf 16.11.2026)

Grundlage für die Anpassungen des Nutzers. Danach folgen Mockups, erst dann der Einbau.
Bestehender Pilot (Computergegner, Wertung, Pokale, Saison): `docs/MULTIPLAYER.md`.

Leitgedanke des Nutzers: „Wer ist der Beste?“ begeistert die Spieler am meisten, hier wird das Geld ausgegeben.
Darum muss es ansprechend und fair sein, vor allem die Gegnersuche.

Offene Fragen an den Nutzer sind mit **❓** markiert.

---

## 1. Gegnersuche (Matchmaking)

Ziel: vier Kommandanten mit ähnlicher Stärke, kurze Wartezeit, keine unfairen Paarungen.

**Zwei Werte je Spieler:**
- **Pokale** (sichtbar): bestimmen die Liga, steigen und fallen nach jedem Kampf.
- **Kampfkraft** (verdeckt): Stand der Station und der Champions (Heldenstufen, Upgrades, Booster). So trifft ein
  Spieler mit starken Champions nicht auf Neulinge, nur weil er wenige Pokale hat.

**Suche in Stufen** (Werte zum Abstimmen):

| Wartezeit | Pokale höchstens entfernt | Kampfkraft höchstens entfernt |
|---|---|---|
| 0–5 s | ±100 | ±10 % |
| 5–12 s | ±250 | ±15 % |
| 12–20 s | ±500 | ±20 % |
| ab 20 s | freie Plätze füllen Computergegner mit passender Stärke (wie im Pilot) | |

- Höchstens etwa 20–25 Sekunden Wartezeit. Die Suche zeigt die gefundenen Kommandanten nacheinander (wie jetzt).
- Nicht zweimal hintereinander dieselben Gegner.
- In Legende und den oberen Galaxie-Stufen wird länger gewartet (bis 40 s), weil dort echte Gegner wichtiger sind.
- **❓ Computergegner kennzeichnen?** Ehrlicher ist ein kleines Zeichen (z. B. „KI“) am Namen. Ohne Kennzeichnung
  wirkt es voller, kann aber bei Entdeckung Vertrauen kosten. Empfehlung: kennzeichnen, sobald es genug echte
  Spieler gibt; im Pilot wie jetzt.

**Fairness im Kampf:** Alle vier spielen dieselben Wellen mit demselben Startwert (gleiche Gegner zur gleichen
Zeit). Gegnerleben richtet sich nach der Kampfkraft der Gruppe, nicht nach der des Einzelnen.

## 2. Ligen und Stufen (bestätigt 16.11.2026)

| Liga | Stufen (III · II · I) ab Pokalen | Farbe |
|---|---|---|
| Bronze | 0 · 130 · 260 | Kupfer |
| Silber | 400 · 600 · 800 | Silber |
| Gold | 1.000 · 1.270 · 1.540 | Gold |
| Kristall | 1.800 · 2.130 · 2.460 | Violett |
| Sternen | 2.800 · 3.200 · 3.600 | Himmelblau |
| Galaxie | 4.000 · 4.500 · 5.000 | Pink |
| **Legende** | ab 5.500, keine Stufen, dafür Platz in der Weltrangliste | Gold-Regenbogen |

- **❓ Namen:** Der Nutzer schrieb „Bronze, Silber, Gold, Diamant …“. Bisher heißt die vierte Liga **Kristall**
  (passend zum Weltraum, die Bilder sind so beauftragt). Umbenennen in Diamant? Dann den Bildauftrag anpassen.
- Pokale je Platz wie im Pilot (`MpData.TROPHIES`), in Legende +25 / +5 / −10 / −25.
- **Aufstieg** in eine neue Stufe oder Liga wird gefeiert (Abzeichen fliegt ein). **Abstieg** nur innerhalb einer
  Liga; aus einer Liga fällt man erst, wenn man 50 Pokale unter ihre Grenze rutscht (Schutz gegen Hin und Her).
- **Saison:** 2 Wochen wie bisher. Zum Saisonende werden Pokale über 1.000 um ein Viertel des Überschusses gesenkt
  (aus 3.000 werden 2.500). So bleibt Bewegung in den Ligen, ohne dass jemand ganz unten anfängt.
- **Saisonbelohnung** nach der höchsten erreichten Liga: Truhe in der Farbe der Liga (Bronze klein … Legende groß).
  Dazu für Legende: Platz 1 / Top 10 / Top 100 je ein Spielerrahmen für die nächste Saison.

## 3. Ranglisten

| Liste | Wer steht drin | Sortiert nach |
|---|---|---|
| **Liga-Gruppe** | 30 Kommandanten der eigenen Stufe (wie jetzt) | Pokale |
| **Weltrangliste** | die besten 100 in Legende | Pokale |
| **Freunde** (später) | eigene Freunde | Pokale |
| **Überleben – Woche** | alle, gruppiert in Gruppen zu 50 mit ähnlicher Kampfkraft | längste Zeit dieser Woche |
| **Überleben – Bestzeit** | die besten 100 weltweit | längste Zeit aller Zeiten |

- Eigener Platz immer unten fest sichtbar (wie im Mockup „Rangliste“).
- **Spielerrahmen:** je Liga ein Rahmen um das Spielerbild, dazu Platz 1 / Top 10 / Top 100. Sie zeigen den Erfolg
  in allen Listen und im Kampf.
- **Namen:** Das Spiel ist für Kinder ab 6. Deshalb keine frei eintippbaren Namen, sondern **zusammengesetzte
  Namen aus Wortlisten** (z. B. „Flinker Komet 27“). Kein Chat, nur feste Emotes. ❓ Einverstanden?

## 4. Überleben (endloses Level)

**Ablauf:** Ein eigenes Schlachtfeld (Vorschlag: der fertige, bisher ungenutzte **Ringplanet**). Die Gegner kommen
ohne Ende. Man spielt, bis die Station fällt. Gewertet wird die **Zeit**.

**Schwierigkeit in Stufen alle 3 Minuten:**

| Zeit | Stufe | Was sich ändert |
|---|---|---|
| 0–3 min | 1 | Gegner des eigenen Fortschritts, ruhiger Einstieg |
| 3 min | 2 | Gegnerleben +30 %, mehr Gegner gleichzeitig |
| 6 min | 3 | +30 %, erster Boss |
| 9 min | 4 | +30 %, schnellere Gegner (+10 %) |
| 12 min | 5 | +30 %, zwei Bosse |
| 15 min | 6 | +30 %, Gegner aller Welten gemischt |
| ab 18 min | 7, 8 … | je Stufe +30 %, Boss alle 3 min |

Kurz vor jeder Stufe eine Ansage („In 10 Sekunden: Stufe 4!“). Zeitmedaillen bei 3, 6, 9, 12, 15 und 20 Minuten.

**Wege, sich zu verbessern** (damit man immer weiterkommen kann und die Rangliste spannend bleibt):
1. **Im Lauf:** Kartenwahl nach jeder Minute (wie nach jeder Welle), Champions kommen dazu (ab der 3. Minute,
   passend zu „Held ab Welle 5“), Meisterfähigkeiten und Symbiosen zählen hier besonders.
2. **Überlebenspunkte (neu, nur für diesen Modus):** Jede überlebte Minute, jeder Boss und jede Medaille bringt
   Punkte. Sie werden in der **Überlebens-Werkstatt** ausgegeben und wirken **nur im Modus Überleben**:

   | Verbesserung | Stufen | Wirkung je Stufe |
   |---|---|---|
   | Verstärktes Schild | 10 | Schild +8 % |
   | Plasma-Vorrat | 10 | Start-Plasma +10 |
   | Schnellere Karten | 5 | erste Kartenwahl 10 s früher |
   | Zweiter Atem | 3 | einmal pro Lauf: Schild füllt sich zu 25 / 40 / 60 % wieder auf |
   | Startkarte | 3 | 1 / 2 / 3 Karten schon zu Beginn |
   | Bossjäger | 5 | +6 % Schaden gegen Bosse |

   Preise steigen je Stufe. ❓ Name: „Überlebenspunkte“ oder etwas Bildhaftes (z. B. „Sternsplitter“)?
3. **Allgemein:** Heldenstufen und Upgrades aus dem Abenteuer zählen mit.

**Fairness der Rangliste:** Die Wochenliste vergleicht nur Spieler mit ähnlicher Kampfkraft (Gruppen zu 50). So
haben auch Neulinge eine Chance auf Platz 1 ihrer Gruppe. Belohnung am Wochenende nach Platz in der Gruppe.

**Kosten:** 1 Energie wie ein Abenteuer-Level (❓ oder 3 Versuche am Tag frei?).

**❓ Geld:** Überlebenspunkte kaufbar? Empfehlung: nein, damit die Rangliste glaubwürdig bleibt; kaufbar nur
„Zweiter Atem“-Ladungen oder ein Pass mit mehr Punkten je Minute (+25 %).

## 5. Server und Kosten

**Was der Server tut** (schlank, das Spiel rechnet jeder auf seinem Handy):
- Gegnersuche (Warteschlange), Startwert für den Kampf verteilen
- während des Kampfes: Punkte der vier Kommandanten etwa einmal pro Sekunde weiterreichen (Live-Rangliste links oben)
- Ergebnis prüfen (Plausibilität: Punkte pro Sekunde, Zeit, Kampfkraft) und Pokale buchen
- Ranglisten, Ligen, Saisonwechsel, Überlebens-Bestzeiten speichern
- Spielerkonto (anonym über die Geräte-Kennung, später Google Play Spiele / Apple Game Center)

**Datenmenge:** etwa 100 Byte je Spieler und Sekunde im Kampf. 1.000 Spieler gleichzeitig ≈ 100 kB/s. Das schafft
ein kleiner Rechner gut.

**Varianten:**

| Variante | Laufende Kosten | Vorteile | Nachteile |
|---|---|---|---|
| **Mini-PC des Nutzers** zu Hause, erreichbar über Cloudflare Tunnel (kostenlos, kein offener Port am Router) | nur Strom, etwa 2–5 € im Monat | keine Mietkosten, volle Kontrolle | hängt am Heimanschluss (Upload, Stromausfall, Zwangstrennung), Datensicherung selbst, Ausfall = kein Mehrspieler |
| Kleiner gemieteter Server (z. B. in Deutschland) | etwa 5–10 € im Monat | Rechenzentrum, feste Adresse, Sicherungen | kleine Monatskosten |
| Cloudflare (Workers und Durable Objects, wie beim Love Diary) | ab etwa 5 $ im Monat | wächst automatisch mit | Kosten steigen mit den Spielern, Architektur anders |

**Empfehlung:** Pilot und erste Monate auf dem **Mini-PC** über Cloudflare Tunnel. Daten jede Nacht verschlüsselt
sichern. Wenn es mehr als einige hundert Spieler gleichzeitig werden oder Ausfälle stören, auf einen gemieteten
Server umziehen (der Server-Code bleibt gleich, Docker).

**Mini-PC des Nutzers: ACEMAGIC F5A** (Produktseite acemagic.de/products/f5a-270-minipc; laut Testberichten
AMD Ryzen AI 9 mit 12 Kernen / 24 Threads, zwei 2,5-Gbit-LAN-Anschlüsse, PCIe-4.0-SSD). Für unseren Server ist das
weit mehr als genug: Rechenleistung und Speicher reichen für Zehntausende Spieler gleichzeitig. Der Engpass ist
nicht der Rechner, sondern der **Upload des Heimanschlusses** und seine Verfügbarkeit. Stromverbrauch im Leerlauf
etwa 10–15 W, also rund 3–4 € im Monat.
- Betrieb: Linux (z. B. Ubuntu Server) oder Windows mit Docker; Server-Programm und Datenbank als Container.
- Erreichbarkeit über Cloudflare Tunnel (kostenlos, kein offener Port, feste Adresse trotz wechselnder IP).
- Sicherung: Datenbank nachts verschlüsselt auf einen externen Speicher kopieren.
- ❓ Upload-Geschwindigkeit des Anschlusses? Für 1.000 Spieler gleichzeitig reichen etwa 2 Mbit/s.
- ❓ Läuft auf dem Mini-PC schon etwas anderes (z. B. das Webportal)? Dann bekommt das Spiel einen eigenen Container.

**Rechtliches (vor dem Start mit echten Spielern):** Spielernamen und Ergebnisse sind personenbezogene Daten →
Datenschutzerklärung ergänzen, Löschung auf Wunsch. Für Kinder: keine freien Texte, kein Chat (siehe oben).

## 6. Reihenfolge

1. Nutzer passt dieses Konzept an (❓-Punkte).
2. Mockups: Gegnersuche, Liga-Aufstieg, Ranglisten (Gruppe, Welt, Überleben), Überleben (Kampf mit Stufenanzeige,
   Werkstatt, Ergebnis mit Medaille). Bilder kommen aus Auftrag 1 von ChatGPT.
3. Einbau ohne Server: Ligen mit Stufen, Legende, Rahmen, Überleben mit Werkstatt und Computer-Ranglisten.
4. Server auf dem Mini-PC: Konto, Gegnersuche, Live-Punkte, Ranglisten. Test mit wenigen echten Spielern.
