# Truhenmodus – Konzept (Entwurf 22.11.2026)

Wunsch des Nutzers vom 22.11.2026: ein Truhenmodus mit den Stufen **leicht, mittel, schwer**. „Schwer“ sollen beim
ersten Versuch nur Spieler schaffen, die bezahlen; wer nur Werbung schaut, darf dort gern einmal scheitern. Offen
sind noch Mechanik, Belohnung, Rangliste, Gilden und mehr. Dies ist der erste Entwurf mit Vorschlägen.
Offene Fragen an den Nutzer sind mit **❓** markiert.

---

## 1. Mechanik: Beutezug (Vorschlag)

Ein eigener Kampf um Beute, damit sich der Modus anders anfühlt als das Abenteuer:

- Neben den normalen Angreifern kommen **Beuteträger**: kleine Gegner mit goldenen Säcken. Sie greifen die Mauer
  nicht an, sondern laufen quer über das Feld und **fliehen** nach einigen Sekunden zurück durchs Portal.
- Jeder erwischte Beuteträger füllt die **Truhenanzeige** (Bronze → Silber → Gold → Schatz).
- **Sieg:** Die Mauer hält alle Wellen (5 bei leicht, 6 bei mittel, 7 bei schwer). Die Truhe richtet sich danach,
  wie viele Beuteträger man erwischt hat.
- **Niederlage:** Man behält die **Hälfte** der bis dahin gesammelten Beute ❓. So lohnt auch ein gescheiterter
  Versuch ein wenig, und niemand geht ganz leer aus.
- Bei **schwer** bewacht in der letzten Welle ein **Schatzwächter** (Boss) die größte Beute.

Champions, Kartenwahl, Booster und Energiekern funktionieren wie im Abenteuer.

## 2. Stufen

| Stufe | Freischaltung | Gegner | Wellen | Beste Truhe |
|---|---|---|---|---|
| **Leicht** | ab Abenteuer-Level 15 ❓ | wie das eigene höchste Level −10 % | 5 | Silbertruhe |
| **Mittel** | nach erstem Sieg auf leicht | wie das höchste Level +10 % | 6 | Goldtruhe |
| **Schwer** | nach erstem Sieg auf mittel | wie das höchste Level +35 %, Schatzwächter | 7 | Schatztruhe |

Die Gegner wachsen mit dem eigenen Fortschritt mit, damit der Modus immer passt.

## 3. „Schwer“ und Bezahlen – offen und fair

**Ziel:** Wer bezahlt, schafft „schwer“ in der Regel beim ersten Versuch; wer nicht bezahlt, scheitert meist
einmal und schafft es nach ein paar Versuchen oder Aufwertungen.

**Wichtig:** Das Spiel darf **nicht heimlich** nach Zahlstatus entscheiden, wer gewinnt (z. B. versteckt stärkere
Gegner für Nichtzahler). Das wäre Täuschung: Google Play und Apple verbieten das, in der EU kann es als irreführende
Geschäftspraxis gelten, besonders bei jüngeren Spielern, und es kostet Bewertungen, wenn es auffällt. Alle spielen
nach denselben, sichtbaren Regeln.

**So erreichen wir das Ziel offen:**

- „Schwer“ wird im Balance-Labor so abgestimmt, dass der erste Versuch **ohne Käufe** selten klappt:

  | Spielertyp | Sieg beim 1. Versuch | nach 3 Versuchen |
  |---|---|---|
  | zahlend (mit Truhen-Pass) | 80–90 % | fast immer |
  | durchschnitt ohne Käufe | 20–30 % | 60–70 % |
  | anfaenger | unter 10 % | 30–40 % |

- **Truhen-Pass** (Monatsabo, Preis ❓, z. B. 4,99 €), sichtbar im Truhenmodus beworben:
  - **Schatzschild:** +30 % Schild in allen Truhenkämpfen
  - +1 Schlüssel am Tag
  - doppelte Beute bei Bronze und Silber
- **Wiederbelebung** einmal je Kampf für Edelsteine (Mauer wieder voll), nicht per Werbung ❓
- Booster wirken wie immer.
- Die **Wahrscheinlichkeiten** der Truheninhalte stehen im Spiel (Pflicht bei Zufallsinhalt).

## 4. Versuche (Schlüssel)

- **2 Schlüssel am Tag** gratis ❓
- **+1 Schlüssel per Werbung**, höchstens 2-mal am Tag (wie beim Knopf „Belohnung verdoppeln“)
- weitere Schlüssel für Edelsteine (z. B. 30)
- Truhen-Pass: +1 Schlüssel am Tag
- Ein Versuch kostet einen Schlüssel, egal welche Stufe.

## 5. Belohnungen

| Truhe | Inhalt (Vorschlag ❓) |
|---|---|
| Bronze | Gold, 2–4 Booster-Teile |
| Silber | mehr Gold, 4–8 Booster-Teile, Heldenkarten |
| Gold | Gold, 10–20 Booster-Teile, Heldenkarten, 10–20 Edelsteine |
| **Schatz** (nur schwer) | viel Gold, 20–40 Booster-Teile, Karten eines **Wunsch-Champions**, 30–60 Edelsteine, selten ein Champion-Skin |

- **Erstsieg-Bonus** je Stufe einmal pro Woche: Truhe eine Größe höher ❓
- Die Mengen wachsen mit dem höchsten Level (wie bei der Heldentruhe).

## 6. Rangliste

- **Schatzjäger der Woche:** Punkte = erwischte Beuteträger × Stufenfaktor (leicht 1, mittel 2, schwer 4).
- In **Gruppen zu 50** mit ähnlicher Kampfkraft wie beim Überleben, damit auch Neulinge vorne landen können.
- Belohnung am Wochenende nach Platz in der Gruppe (Platz 1–3 Schatztruhe, Top 10 Goldtruhe, alle Silbertruhe).
- Braucht den Server (`docs/WETTBEWERB.md`, Abschnitt 5) ❓; ohne Server zuerst mit Computer-Ranglisten wie im Pilot.

## 7. Gilden (neu, für alle Modi)

Gilden gibt es im Spiel noch nicht. Vorschlag, damit sie im Truhenmodus und später im Gilden-Raid
(`docs/WELTRAUMSCHLACHT.md`) ein gemeinsames Ziel haben:

- **Gründen** ab Level 20 für 500 Gold ❓; höchstens **30 Mitglieder**; beitreten frei oder auf Anfrage
  (Einstellung der Gilde).
- **Gildenname und Wappen:** Name wird wie der Kontoname auf dem Server geprüft (für Kinder ab 6 geeignet,
  Sperrliste); Wappen aus festen Formen und Farben, keine eigenen Bilder.
- **Kein Chat** (Entscheidung 16.11.2026). Vorschlag stattdessen: feste **Kurzmeldungen** („Gut gemacht!“,
  „Wer macht mit?“, „Danke!“) ❓
- **Gildenziel der Woche:** Alle Truhenpunkte der Mitglieder zählen zusammen. Stufen schalten eine **Gildentruhe**
  frei, die jedes Mitglied bekommt, das mindestens 10 Punkte beigetragen hat.
- **Gilden-Rangliste:** Summe der Wochenpunkte.
- **Später:** Gilden-Raid gegen das Mutterschiff (Weltraumschlacht C).
- Rollen: Anführer, Stellvertreter, Mitglied; Anführer kann Mitglieder entfernen. Wer 14 Tage nicht spielt,
  verliert den Anführerposten an den aktivsten Stellvertreter.

**Server und Kosten:** Gilden, Gildenziele und Ranglisten brauchen den Server (geplant auf dem Mini-PC, nur
Stromkosten; `docs/WETTBEWERB.md`, Abschnitt 5). Gildennamen und Mitgliedschaften sind personenbezogene Daten →
Datenschutzerklärung ergänzen.

## 8. Offene Fragen ❓

1. Mechanik „Beutezug“ (Beuteträger fliehen, Truhe nach erwischter Beute) passt, oder lieber eine andere Idee
   (z. B. Truhe beschützen, die von Gegnern angegriffen wird)?
2. Bei Niederlage die Hälfte der Beute behalten: ja oder nein?
3. Freischaltung ab Level 15?
4. Truhen-Pass als Monatsabo: ja, und zu welchem Preis? Oder lieber einzelne Käufe (Schlüsselpakete,
   Schatzschild für 24 Stunden)?
5. Wiederbelebung nur für Edelsteine oder auch einmal am Tag per Werbung?
6. Wie viele Gratis-Schlüssel am Tag (Vorschlag 2) und wie viele per Werbung (Vorschlag 2)?
7. Inhalte der Truhen und Erstsieg-Bonus so in Ordnung?
8. Rangliste „Schatzjäger der Woche“: ja oder nein?
9. Gilden: Gründungsstufe, Kosten, Größe, Kurzmeldungen statt Chat?
10. Soll der Modus ein eigenes Schlachtfeld bekommen (z. B. Schatzkammer-Planet) oder auf den Planeten des
    Abenteuers spielen?
