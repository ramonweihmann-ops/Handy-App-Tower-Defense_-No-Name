# Tutorial: Auftrag für ChatGPT (Stand 04.11.2026)

Zum Kopieren in ChatGPT. Dazu als Bilder anhängen: Screenshots von Abenteuer-Pfad, Kampf (mit Heldenauswahl),
Belohnung nach dem Sieg, Helden, Held aufleveln, Upgrades (Tech-Werft), Basislager. Am einfachsten aus dem Mockup
„Menü-Entwürfe Wurmloch“ oder vom Handy.

---

Ich entwickle ein Handy-Tower-Defense-Spiel (hochkant, Comic-Stil im Weltraum, Godot). Ich brauche ein
**Tutorial für neue Spieler**: einen Ablaufplan und die Gestaltung der Tutorial-Elemente. Bitte zuerst den Plan
und die Gestaltung, noch keine Programmierung.

**Das Spiel kurz:** Helden stehen unten am Energiezaun einer Raumstation und schießen auf Monster, die über eine
Brücke kommen. Munition ist **Plasma** (füllt sich nach, Anzeige unten). Der **Energiekern** in der Mitte unten lädt
sich auf; Antippen („TIPPEN!“) schießt Kugeln durch eine Bahn, die Plasma bringen. Zu Beginn eines Kampfes wählt
man den **ersten Helden** aus drei Karten; nach jeder Welle wählt man eine **Karte** (neuer Held oder Verbesserung).
Es gibt zwei **Booster**-Knöpfe (Luftangriff, Medipack). Nach dem Sieg gibt es Gold, Heldenkarten und Pass-Punkte.

Menü unten mit fünf Reitern: **Shop**, **Helden** (Helden mit Karten und Gold aufleveln), **Kampf**
(Abenteuer-Pfad mit Leveln und großem Spielen-Knopf), **Upgrades** (Tech-Werft: Module mit Gold ausbauen; Talente
mit Sternen; Fenster Munition für dauerhafte Plasma-Stufen), **Basis** (Basislager: Gebäude bauen und ausbauen, sie
erzeugen mit der Zeit Gold, Karten, Energie; Lager einsammeln). Dazu Tägliche Belohnung, Glücksrad, Missionen,
Battle Pass und Spielmodi (Multiplayer).

**Meine Idee (bitte prüfen und verbessern):** Kein langes Tutorial am Anfang, sondern ein **geführter Einstieg
über die ersten 3–5 Kämpfe**. Der Spieler spielt sofort, und nach jedem Kampf wird er zu genau einem neuen Bereich
geführt und **muss diesen Schritt einmal selbst ausführen**, bevor es weitergeht. Das Spiel gibt dafür so viel Gold
und so viele Karten, dass der Schritt sicher klappt. Grob:
1. Start: Hinweis auf „Spielen“ (Level 1).
2. Kampf 1: wenige kurze Hinweise im Kampf (Held wählen, Plasma, Energiekern antippen, Karte nach der Welle,
   einmal Luftangriff).
3. Nach Kampf 1: zum Reiter Helden → einen Helden aufleveln.
4. Kampf 2, danach: Upgrades → ein Modul der Tech-Werft ausbauen (Munition kurz zeigen).
5. Kampf 3, danach: Basis → ein Gebäude bauen oder ausbauen, Lager einsammeln.
6. Danach frei, höchstens noch einmal kurz auf Tägliche Belohnung, Missionen und Spielmodi hinweisen
   (ohne Zwang), sobald sie zum ersten Mal wichtig werden.

**Was ich von dir brauche:**

A) **Ablaufplan** als Tabelle: Schritt, wann (Auslöser), welcher Bildschirm, welches Element hervorgehoben wird,
   genauer Hinweistext, ob der Schritt Pflicht ist (alles andere gesperrt) oder freiwillig, wann er als erledigt gilt
   und was das Spiel dafür schenkt (z. B. Karten, Gold). Kurze Texte, Du-Form, freundlich und klar, höchstens zwei
   Zeilen je Hinweis, ohne Fachbegriffe.

B) **Antworten auf meine offenen Fragen**, mit Empfehlung:
   - Pflicht oder überspringbar? (Ich tendiere zu Pflicht für Helden, Upgrades, Basis.)
   - Pausiert der Kampf bei Hinweisen, oder laufen sie nebenher?
   - Was passiert, wenn man einen Kampf verliert, die App mitten im Schritt schließt oder schon genug weiß?
   - Wie viele Hinweise verträgt der erste Kampf, ohne zu nerven?
   - Kurze Begründung, wie andere erfolgreiche Handyspiele das lösen (allgemein, keine fremden Grafiken kopieren).

C) **Gestaltung der Tutorial-Elemente** im Stil des Spiels (Comic, kräftige Farben, dunkelviolette Fenster mit
   Goldrand, Schrift Fredoka für Überschriften und Nunito für Text):
   - Abdunklung mit „Lichtkegel“ (Spotlight) auf das Element, das angetippt werden soll
   - Zeigerhand oder Pfeil, der sanft pulsiert
   - Hinweisblase mit Text, gern mit einer **Erzählerfigur** (Vorschlag: der Roboter-Held Pip als Stationshelfer,
     oder eine eigene Stations-KI; bitte mach einen Vorschlag)
   - kleiner Fortschritt („Schritt 2 von 5“) und ein Abschluss-Moment mit Belohnung

**Bitte liefern (Ordner `Vorlage_Raw/Tutorial_v1/` auf GitHub, Branch `claude/amazing-hypatia-yl59v4`):**
1. `TUTORIAL_ABLAUF.md`: Plan (A) und Antworten (B).
2. `TUTORIAL_ABLAUF.json`: dieselben Schritte maschinenlesbar (id, auslöser, bildschirm, ziel_element, text, pflicht,
   erledigt_wenn, geschenk).
3. Vier bis sechs Bildschirmentwürfe hochkant (je 852 × 1846 Pixel), z. B. `tutorial_01_spielen.png`,
   `tutorial_02_kampf_energiekern.png`, `tutorial_03_held_aufleveln.png`, `tutorial_04_tech_werft.png`,
   `tutorial_05_basis.png`, `tutorial_06_abschluss.png`.
4. Einzelteile als PNG mit **transparentem Hintergrund**: Zeigerhand (256 × 256), Erzählerfigur in 2–3 Posen
   (je 512 × 512), Rahmen der Hinweisblase (z. B. 512 × 256, mit Rand zum Strecken).
5. `LIESMICH_CLAUDE.md`: Aufbau, Farben (Hex-Werte), Größen auf 390 × 844 Punkten, Animationen (Pulsieren,
   Einblenden), Hinweise für den Einbau. Die Bilder sind Vorlagen; Texte, Lichtkegel und Knöpfe baut Claude
   als einzelne Teile.
6. Kurz `BILDANWEISUNG.txt` (verwendete Bildprompts).

Keine neuen Spielwerte, Preise oder Funktionen erfinden; was das Tutorial schenkt, bitte nur als Vorschlag
kennzeichnen. Nur die eingebaute Bildgenerierung im bestehenden Konto verwenden, keine weiteren kostenpflichtigen
Dienste.
