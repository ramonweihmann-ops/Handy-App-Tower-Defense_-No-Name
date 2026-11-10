# Kartenwahl: fehlende Kartenmotive – Auftrag für ChatGPT (Stand 10.11.2026)

Die Kartenwahl nach jeder Welle ist im Spiel (Entwurf B). Motive gibt es bisher nur für sechs Karten
(`Vorlage_Raw/Kartenwahl_Kampf_v1/motive/`). Alle anderen Karten zeigen vorerst einen farbigen Kreis mit
Symbol. Dieser Auftrag liefert die 31 fehlenden Motive. Kosten: keine (eigene Bildgenerierung im Konto).

---

Bitte für mein Handyspiel (Tower Defense, Comic-Stil) 31 Kartenmotive erzeugen. Sie erscheinen auf den
Karten, die man nach jeder Welle wählt: klein auf dem Kärtchen (70 × 70 Punkte) und groß im Detailfeld
(98 × 98 Punkte).

STILVORLAGE: genau wie die sechs vorhandenen Motive im Repository Handy-App-Tower-Defense_-No-Name, Branch
claude/amazing-hypatia-yl59v4, Ordner Vorlage_Raw/Kartenwahl_Kampf_v1/motive/ (zum Beispiel
icon_breite_flamme.png, icon_feuerwalze.png, icon_plasma_kern.png). Kräftige Comic-Umrisse, satte Farben,
leichte Glanzlichter, ein Gegenstand oder Effekt groß in der Mitte.

FORMAT
- je 512 × 512 Pixel, PNG mit durchsichtigem Hintergrund (RGBA), Motiv mittig, etwa 8 % Rand frei
- keine Schrift, keine Zahlen, keine Rahmen, keine Karte drumherum, kein Hintergrund
- muss auch klein (70 Punkte) sofort erkennbar sein: wenige, große Formen
- keine Personen (das Heldenporträt setzt das Spiel selbst daneben), nur Waffe, Gegenstand oder Effekt
- jedes Motiv ein eigenes Bild, nicht aus einem Sammelbild ausschneiden

DATEINAMEN UND INHALT (Dateiname genau so, das Spiel ordnet über den Namen zu)

Spezialfähigkeit und Superfähigkeit je Waffe (die Fritzi-Motive gibt es schon):
- revolver_special.png – Fächerfeuer: Revolver, aus dem Lauf fächern drei Kugeln auf
- revolver_ult.png – Kugelhagel: Revolver mit rauchendem Lauf und Schwarm goldener Kugeln
- mg_special.png – Durchschlag: Maschinengewehr-Kugel, die zwei Zielscheiben hintereinander durchschlägt
- mg_ult.png – Dauerfeuer: Maschinengewehr mit hell glühendem Lauf und langem Mündungsfeuer
- rocket_special.png – Größere Explosion: große runde Comic-Explosion mit Druckwelle
- rocket_ult.png – Raketensalve: Fächer aus fünf kleinen Raketen mit Rauchspuren
- tesla_special.png – Kettenblitz: Blitz, der zickzack zwischen drei Kugeln springt
- tesla_ult.png – Gewittersturm: dunkle Wolke mit mehreren Blitzen nach unten
- cryo_special.png – Frostsplitter: Eiskristall, der in Splitter zerspringt
- cryo_ult.png – Eiszeit: großer Eisblock mit Frostnebel
- shotgun_special.png – Mehr Schrot: Schrotpatrone mit vielen Kugeln, die herausfliegen
- shotgun_ult.png – Breitseite: Schrotflinte mit breitem dreifachem Mündungsfeuer
- sniper_special.png – Durchschlag: Präzisionskugel mit Leuchtspur durch zwei Ziele
- sniper_ult.png – Kopfgeldjagd: Zielfernrohr-Fadenkreuz mit goldenem Stern in der Mitte
- beam_special.png – Längerer Atem: langer leuchtender Sternenstrahl (lila und gold)
- beam_ult.png – Sternenschweif: drei parallele Sternenstrahlen mit Funkeln
- drone_special.png – Feinmechanik: Schraubenschlüssel und Zahnrad mit grünem Reparaturfunkeln
- drone_ult.png – Geschützturm: kleiner Roboter-Geschützturm auf drei Beinen
- cannon_special.png – Mehr Wucht: Kanonenkugel mit großer Druckwelle nach vorn
- cannon_ult.png – Dampfwalze: schwere Walze mit Dampfwolken
- gravity_special.png – Größeres Feld: lila Schwerkraftring mit Kreisen nach außen
- gravity_ult.png – Schwarzes Loch: Strudel mit dunklem Kern und lila Rand

Allgemeine Waffenkarten (für alle Helden gleich):
- held_rate.png – Schneller feuern: Patronen mit Geschwindigkeitsstreifen
- held_reload.png – Schneller nachladen: Magazin mit kreisförmigem Pfeil
- held_mag.png – Größeres Magazin: großes, volles Magazin mit Patronen

Plasma-Karten:
- gate_ice.png – Eis-Plasma: Plasmakugel aus Eis (hellblau, Frostkristalle), passend zu icon_plasma_kern.png
- gate_plus3.png – Großer Verdichter: größere, prächtigere Fassung des Plasma-Verdichters (icon_plasma_kern.png)
- machine_rate.png – Schneller laden: Plasma-Tank mit Geschwindigkeitspfeilen
- machine_count.png – Mehr Plasma: drei leuchtende Plasmakugeln nebeneinander
- plasma_mag.png – +2 Schuss für alle: zwei goldene Patronen mit Plasma-Leuchten
- plasma_reload.png – Schneller nachladen für alle: Magazin mit Plasma-Kreispfeil

PRÜFEN VOR DEM HOCHLADEN
- Alle 31 Dateien da, Namen genau wie oben, 512 × 512, durchsichtiger Hintergrund (Ecken wirklich leer).
- Ein Übersichtsbild aller 31 Motive klein (70 Pixel) auf dunkellila Grund (#28203F): ist jedes erkennbar?
- Keine Schrift im Bild.

ABLAGE: Vorlage_Raw/Kartenmotive_v2/ mit den 31 PNGs, dem Übersichtsbild uebersicht_70px.png und einer kurzen
LIESMICH_CLAUDE.md (was erzeugt wurde, Auffälligkeiten).

## Danach (Claude)

Claude verkleinert die Motive auf 320 × 320, legt sie als `game/ui/karten/<Name>.webp` ab (das Spiel findet
sie über den Namen), trägt einige ins Mockup ein und schickt ein Prüfbild.
