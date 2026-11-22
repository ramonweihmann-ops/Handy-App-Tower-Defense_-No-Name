# Weltraumschlacht – Konzept (Entwurf 22.11.2026)

Wunsch des Nutzers vom 22.11.2026: ein Konzept für Weltraumschlachten. Dies ist der erste Entwurf mit Vorschlägen.
Offene Fragen an den Nutzer sind mit **❓** markiert. Danach folgen Mockups, erst dann der Einbau.

Leitgedanke: Abwechslung zum Abenteuer, ohne dass man etwas Neues lernen muss. Die Steuerung bleibt gleich
(Plasma und Hebel, Champions, Energiekern, Kartenwahl nach jeder Welle). Neu ist, **wo** und **gegen wen** man
kämpft: im offenen All, auf dem Deck des eigenen Kreuzers, gegen fliegende Schwärme und ganze Schiffe.

---

## 1. Drei Ausrichtungen ❓

| | Was es ist | Aufwand | Server |
|---|---|---|---|
| **A) Flottenschlacht** (Empfehlung) | eigener Modus mit Kapiteln; man verteidigt seinen Kreuzer gegen Schwärme, Bomber und Mutterschiffe | mittel: neues Schlachtfeld, Flugbahnen, Schiffs-Gegner | nein |
| **B) Sternenkarte** | Galaxiekarte mit Sektoren, die man nacheinander erobert; jeder Sektor ist eine Schlacht | mittel bis groß: Karte, Fortschritt, Belohnungen | nein (mit Gilden ja) |
| **C) Gilden-Raid** | ein riesiges Mutterschiff mit gemeinsamem Leben, die ganze Gilde greift es über drei Tage an | klein, wenn A steht | ja |

**Vorschlag:** A als Grundmodus. C baut später darauf auf (gleiche Technik, gleiche Gegner) und gibt den Gilden aus
dem Truhenmodus ein gemeinsames Ziel (`docs/TRUHENMODUS.md`, Abschnitt 7). B kann A später als Karte einrahmen.

## 2. Flottenschlacht (A)

**Schlachtfeld:** Statt Brücke und Mauer liegt unten das Deck des eigenen Kreuzers, oben das offene All mit
Nebeln und Planeten. Der **Schiffsschild** ersetzt die Mauer (gleiche Anzeige „Schild …“). Champions stehen auf
dem Deck wie bisher.

**Was neu ist:**

| Gegner | Verhalten | Gegenmittel |
|---|---|---|
| **Jägerschwarm** | 5–8 kleine Jäger fliegen in Formation Kurven und Schleifen statt gerade nach unten | Flächenschaden (Fritzi, Brocken), Kettenblitz |
| **Bomber** | langsam, schwer gepanzert, wirft Bomben auf den Schild | Einzelschaden (Lynx, Kalle) |
| **Tarnschiff** | wird nur kurz sichtbar, wenn es feuert | Kritische Treffer, schnelle Schüsse |
| **Asteroid** | treibt durchs Bild, zerschießbar, gibt beim Zerplatzen Plasma | nebenbei mitnehmen |
| **Mutterschiff** (Boss) | drei Phasen: erst die **Schildgeneratoren** an den Flanken zerstören, dann die Geschütze, dann den Kern | gezieltes Feuer auf Schwachstellen |

- **Ausweichmanöver** (neue Superfähigkeit des Schiffs, Antippen alle ~45 s): Der Kreuzer rollt zur Seite,
  2 Sekunden lang treffen keine Bomben. ❓
- Die Gegner fliegen auf **Bahnen** (Kurven, Schleifen, Formationen), nicht nur geradeaus. Das ist der größte
  technische Unterschied zum Abenteuer.

**Aufbau:** Kapitel zu je 10 Missionen, jede Mission 5–7 Wellen, die 10. ist ein Mutterschiff.
- Freischaltung ab **Abenteuer-Level 30** ❓ (dann kennt man Kartenwahl, Meisterfähigkeit und Symbiosen).
- Kosten wie im Abenteuer: **5 Energie** je Mission ❓ (Alternative: eigene Treibstoff-Anzeige mit 5 Flügen am Tag).
- Schwierigkeit wächst mit dem Kapitel; das Balance-Labor stimmt sie ab wie das Abenteuer (gleiche Spielertypen).

**Belohnungen:** in den bestehenden Währungen, damit es nicht noch eine neue gibt:
- je Mission Gold und Booster-Teile; Sterne (1–3) nach verbleibendem Schild wie im Abenteuer
- je Kapitel eine **Flottentruhe** (Heldenkarten, Edelsteine)
- **Schiffs-Skins** (Aussehen von Deck und Schild) als besondere Belohnung, auch im Battle Pass verwendbar ❓

## 3. Gilden-Raid (C, später)

- Einmal pro Woche erscheint ein **Raid-Mutterschiff** mit riesigem gemeinsamem Leben.
- Jedes Gildenmitglied hat **3 Angriffe am Tag**, je 2 Minuten. Der Schaden zählt für die Gilde.
- Belohnung nach dem gemeinsamen Fortschritt (25 / 50 / 75 / 100 %) für alle, die mindestens einmal angegriffen
  haben, dazu ein kleiner Bonus nach dem eigenen Anteil.
- Braucht den Server (gemeinsames Leben, Gildenliste) → siehe `docs/WETTBEWERB.md`, Abschnitt 5.

## 4. Grafik und Aufwand

- **Schlachtfeld:** Deck des Kreuzers und Weltraum-Hintergrund. Raumschiffe und Decks sind harte Formen, die lassen
  sich gut **selbst in Blender bauen** (ohne ChatGPT und ohne Meshy-Kosten), im Stil der gemalten Brücken wie die
  Mauern.
- **Gegner:** Jäger, Bomber, Tarnschiff, Mutterschiff ebenfalls in Blender. Fliegende Schiffe brauchen keine
  Lauf-Animation, nur Flugbahnen und Neigung in den Kurven.
- **Technik:** Flugbahnen (Kurven, Formationen), Schwachstellen am Boss, Ausweichmanöver. Kampf, Champions,
  Karten und Effekte werden wiederverwendet.

## 5. Offene Fragen ❓

1. Welche Ausrichtung: A, B, C oder eine Mischung (Vorschlag: A jetzt, C später)?
2. Ab welchem Level freischalten (Vorschlag: Level 30)?
3. Energie wie im Abenteuer oder eigener Treibstoff?
4. Ausweichmanöver als Superfähigkeit des Schiffs: ja oder nein?
5. Schiffs-Skins als Belohnung und im Battle Pass?
6. Sollen die Champions in der Weltraumschlacht anders aussehen (z. B. Raumanzug-Skin) oder wie bisher?
7. Soll es eine eigene Rangliste geben (z. B. schnellste Kapitel) oder reichen Sterne und Truhen?
