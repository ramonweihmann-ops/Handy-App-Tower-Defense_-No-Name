# Kartenmotive für Symbiosen und Meisterfähigkeit – Auftrag für ChatGPT (Stand 16.11.2026)

**Reihenfolge:** Auftrag 3 von 4 (Übersicht in `Vorlage_Raw/AUFTRAEGE_REIHENFOLGE.md`).
**Kosten: keine** (eingebaute Bildgenerierung im Konto).

**Erst abschicken, wenn der Nutzer die Mockups „Karten-Meister“ und „Karten-Symbiose“ freigegeben hat** und die
Liste der Symbiosen feststeht (`docs/KARTENSYSTEM.md`). Ändert sich dort etwas, diese Liste vorher anpassen.

---

Bitte für mein Handyspiel (Tower Defense, Comic-Stil) acht neue Kartenmotive erzeugen. Sie erscheinen auf den
Karten, die man nach jeder Welle wählt: klein auf dem Kärtchen (70 × 70 Punkte) und groß im Detailfeld
(104 × 104 Punkte).

STILVORLAGE: genau wie die 31 vorhandenen Motive im Repository Handy-App-Tower-Defense_-No-Name, Branch
claude/amazing-hypatia-yl59v4, Ordner Vorlage_Raw/Kartenmotive_v2/ (zum Beispiel tesla_special.png,
rocket_special.png, cryo_special.png; Fritzis Flammenmotiv liegt im Spiel unter game/ui/karten/flamer_special.webp). Kräftige Comic-Umrisse, satte Farben, leichte Glanzlichter, ein Gegenstand
oder Effekt groß in der Mitte.

NEU: SYMBIOSEN. Zwei Champions verbinden ihre Spezialfähigkeiten zu einer neuen Wirkung. Jedes Symbiose-Motiv
verschmilzt deshalb die beiden vorhandenen Motive zu **einem** neuen Effekt, gut erkennbar als Mischung aus beiden.
Ein feiner mintgrüner Schimmer (#7cf2c2) um den Effekt kennzeichnet alle Symbiosen als Familie.

FORMAT
- je 512 × 512 Pixel, PNG mit durchsichtigem Hintergrund (RGBA), Motiv mittig, etwa 8 % Rand frei
- keine Schrift, keine Zahlen, keine Rahmen, keine Karte drumherum, kein Hintergrund
- muss auch klein (70 Punkte) sofort erkennbar sein: wenige, große Formen
- keine Personen (die Porträts setzt das Spiel selbst daneben), nur Waffe, Gegenstand oder Effekt
- jedes Motiv ein eigenes Bild, nicht aus einem Sammelbild ausschneiden

DATEINAMEN UND INHALT (Dateiname genau so, das Spiel ordnet über den Namen zu)

Symbiosen (Mischung aus den beiden genannten vorhandenen Motiven):
- sym_kettenexplosion.png – Explosiver Kettenblitz (tesla_special + rocket_special): Zickzack-Blitz springt
  zwischen drei Kugeln, an jeder Kugel eine runde Comic-Explosion
- sym_frostblitz.png – Frostblitz (tesla_special + cryo_special): hellblauer Blitz aus Eis, an den Spitzen
  Eiskristalle und Frostsplitter
- sym_brandschrot.png – Brandschrot (shotgun_special + flamer_special): Schrotpatrone, aus der brennende
  Feuerkugeln fliegen
- sym_schwerkraftbombe.png – Schwerkraftbombe (rocket_special + gravity_special): Rakete, deren Einschlag einen
  violetten Wirbel bildet, der Splitter nach innen zieht
- sym_durchschlagsalve.png – Durchschlag-Salve (mg_special + sniper_special): Kugel mit Leuchtspur durchschlägt
  drei Zielscheiben hintereinander, daneben eine Reihe MG-Kugeln
- sym_reparaturwucht.png – Reparaturwucht (drone_special + cannon_special): schwere Kanonenkugel mit grünem
  Reparaturfunkeln, Schraubenschlüssel und Zahnrad im Schweif
- sym_sternenfeuer.png – Sternenfeuer (beam_special + flamer_special): leuchtender Sternenstrahl (lila und gold),
  der in Flammen übergeht

Meisterfähigkeit (erscheint klein neben jeder Waffenfähigkeit, die Stufe 3 erreicht hat):
- meister_abzeichen.png – goldenes Abzeichen: Stern in einem Lorbeerkranz mit kleiner Krone, glänzend,
  sehr einfach und klar (wird auch mit 20 Punkten Breite gezeigt)

ZUSÄTZLICH
- uebersicht_70px.png: alle acht Motive verkleinert auf 70 Punkte nebeneinander, zur Kontrolle der Lesbarkeit

BITTE LIEFERN in Vorlage_Raw/Kartenmotive_v3/ auf GitHub (Branch claude/amazing-hypatia-yl59v4):
1. die acht PNG-Dateien
2. uebersicht_70px.png
3. LIESMICH_CLAUDE.md: je Datei Motiv und Größe
4. BILDANWEISUNG.txt: die verwendeten Bildprompts

Nur die eingebaute Bildgenerierung im bestehenden Konto verwenden, keine weiteren kostenpflichtigen Dienste.
