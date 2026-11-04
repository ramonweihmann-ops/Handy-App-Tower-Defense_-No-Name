# Fenster „Munition“: Auftrag für ChatGPT (Stand 04.11.2026)

Zum Kopieren in ChatGPT. Dazu als Bild anhängen: `Vorlage_Raw/Munition_Fenster_alt.png` (so sieht es jetzt im
Spiel aus) und zum Stil zwei freigegebene Entwürfe, z. B. `Vorlage_Raw/Heldenauswahl_Start_v1/heldenauswahl_entwurf_v1.png`
und einen Screenshot des Gebäudefensters im Basislager.

---

Ich entwickle ein Handy-Tower-Defense-Spiel (hochkant, Comic-Stil im Weltraum, Godot). Bitte gestalte mir das
Fenster **„Munition“** neu. Es ist eines der letzten Fenster im alten Stil.

**Wo es sitzt:** Reiter „Upgrades“ → Knopf „Munition“. Es öffnet sich als Fenster über der Upgrade-Seite. Oben
bleibt die Kopfleiste (Profil, Energie, Gold, Edelsteine, Einstellungen), unten die Reiterleiste (Shop, Helden,
Kampf, Upgrades, Basis). Dazwischen liegt das Fenster, dahinter die Upgrade-Seite abgedunkelt.

**Was es macht:** Dauerhafte Verbesserungen für Plasma (die Munition aller Helden) und den Energiekern. Sie gelten
in jedem Kampf und werden mit Gold gekauft, eine Stufe pro Kauf. Heute ist es eine schlichte Liste mit Titel,
„Stufe x/y“, Beschreibung, dünnem Fortschrittsbalken und grünem Preisknopf (Bild angehängt). Das wirkt langweilig.

**Die sechs Verbesserungen (Texte und Werte bitte genau so übernehmen, keine neuen Werte erfinden):**

| Name | Beschreibung | Stufen | Preis der nächsten Stufe |
|---|---|---|---|
| Plasma-Takt | Plasma kommt 6 % schneller nach (je Stufe) | 10 | 80 Gold × (Stufe + 1) |
| Plasma-Tank | +8 Plasma Platz (je Stufe) | 10 | 60 Gold × (Stufe + 1) |
| Startvorrat | +5 Plasma zu Beginn (je Stufe) | 10 | 50 Gold × (Stufe + 1) |
| Energiekern | Energiekern 1,5 s schneller bereit und +2 Plasma (je Stufe) | 5 | 150 Gold × (Stufe + 1) |
| Zweiter Erzeuger | +1 Plasma pro Ladung (je Stufe) | 3 | 500 Gold × (Stufe + 1) |
| Start-Tore | Stufe 1: +3-Tor, Stufe 2: zweites ×2-Tor von Anfang an | 2 | 1.200 Gold × (Stufe + 1) |

Beispielstand für den Entwurf: Plasma-Takt 6/10 (560 Gold), Plasma-Tank 4/10 (300), Startvorrat 4/10 (250),
Energiekern 3/5 (600), Zweiter Erzeuger 0/3 (500), Start-Tore 0/2 (1.200, gerade zu teuer). Gold des Spielers: 662.

**Gestaltung:**
- Stil wie die freigegebenen Fenster: dunkelviolettes Fenster mit abgerundeten Ecken und feinem Goldrand,
  goldene Überschrift „Munition“ in Fredoka (rund, fett), Fließtext in Nunito. Roter Schließen-Knopf mit weißem X
  oben rechts. Kräftige Farben, weiche Comic-Schattierung, kein Fotorealismus.
- Untertitel klein: „Gilt in jedem Kampf.“
- Jede Verbesserung bekommt ein **eigenes Symbol** im Comic-Stil der Spiel-Icons (Plasma ist hellblau/cyan
  leuchtend): z. B. Uhr/Pfeile mit Plasmatropfen (Takt), Tank (Tank), Kiste mit Plasma (Startvorrat), leuchtende
  Energiekugel (Energiekern), zweites Rohr/Generator (Erzeuger), Tor mit „+3“/„×2“ (Start-Tore).
- Die Stufen deutlich zeigen, gern als Segmente oder Punkte statt dünnem Balken (10, 5, 3 oder 2 Segmente).
- Drei Zustände sichtbar machen: kaufbar (grüner Knopf mit Goldmünze und Preis), zu teuer (Knopf ausgegraut,
  Preis rot), voll ausgebaut („MAX“, goldenes Abzeichen statt Knopf). Bitte im Entwurf alle drei zeigen
  (z. B. eine Zeile auf MAX setzen).
- Alles muss auf einen Handy-Bildschirm passen (390 × 844 Punkte), ohne Scrollen. Texte nicht zu klein:
  Namen etwa 16 pt, Beschreibungen mindestens 11–12 pt. Lange Beschreibungen dürfen zweizeilig sein.
- Keine Werbung, keine Preise in Echtgeld, keine neuen Spielfunktionen.

**Bitte liefern (Ordner `Vorlage_Raw/Munition_Fenster_v1/` auf GitHub, Branch `claude/amazing-hypatia-yl59v4`):**
1. `munition_entwurf_v1.png`: der ganze Bildschirm als Gestaltungsvorlage (852 × 1846 Pixel, hochkant).
2. Die sechs Symbole einzeln als PNG mit **transparentem Hintergrund**, je 256 × 256 Pixel, Motiv mittig mit etwas
   Rand: `icon_plasma_takt.png`, `icon_plasma_tank.png`, `icon_startvorrat.png`, `icon_energiekern.png`,
   `icon_zweiter_erzeuger.png`, `icon_start_tore.png`.
3. `LIESMICH_CLAUDE.md`: Aufbau des Fensters, alle Texte, die drei Zustände, Farben (Hex-Werte), Abstände und
   Hinweise für den Einbau. Das Bild ist eine Vorlage: Texte, Knöpfe und Symbole baut Claude als einzelne Teile.
4. Kurz `BILDANWEISUNG.txt` (verwendeter Bildprompt).

Nur die eingebaute Bildgenerierung im bestehenden Konto verwenden, keine weiteren kostenpflichtigen Dienste.
