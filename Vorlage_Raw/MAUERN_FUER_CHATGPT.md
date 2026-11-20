# Mauern je Planet – Auftrag für ChatGPT (Stand 20.11.2026)

**Nicht mehr nötig (20.11.2026):** Die Mauern hat Claude in Blender gebaut, im Stil der gemalten Brücken
(`tools/mauern/`, im Spiel seit 0.10.40). Der Auftrag bleibt nur zum Nachlesen.

**Kosten: keine.** Nur die eingebaute Bildgenerierung im bestehenden Konto.

Befund: Im Kampf liegt auf allen 15 Planeten und in beiden Arenen dieselbe schlichte graue Leiste mit Pfosten als
Mauer (Bildschirmfotos `Vorlage_Raw/Mauer_Referenz/mauer_heute.png`). Sie wirkt billig und passt zu keinem Planeten.
Wunsch des Nutzers (20.11.2026): für jedes Level eine passende Mauer. Das Schlachtfeld wechselt alle 10 Level mit
dem Planeten, also bekommt jeder Planet seine eigene Mauer.

Ablauf: Teil 1 (Planeten 01–05) zuerst; Claude setzt die Mauern ins Kampf-Mockup und zeigt sie dem Nutzer. Erst
nach Freigabe Teil 2 (06–10) und Teil 3 (11–15 und die zwei Arenen) im selben Stil.

Einbau (Claude): Die Mauer bleibt eine eigene Ebene zwischen Gegnern und Champions (wie die heutige Leiste in
`battle_hud.gd`, `_update_rail`): Gegner an der Mauer stehen dahinter, die Champions davor. Der Schildbalken
„Schild …“ wird weiter vom Spiel darübergezeichnet.

---

## Teil 1: Planeten 01–05

~~~~text
Ich entwickle ein Handy-Tower-Defense-Spiel (hochkant, gemalter Comic-Stil im Weltraum). Jeder Planet ist ein
gemaltes Schlachtfeld mit einer Brücke, über die die Gegner nach unten laufen. Am unteren Ende der Brücke steht die
Mauer, die meine Champions verteidigen. Heute ist das auf allen Planeten dieselbe schlichte graue Leiste mit
Pfosten – sie wirkt billig. Bitte für jeden Planeten eine eigene, hochwertige Mauer malen, die zu Brücke und
Kulisse dieses Planeten passt.

UNTERLAGEN auf GitHub (Repository Handy-App-Tower-Defense_-No-Name, Branch claude/amazing-hypatia-yl59v4):
- Vorlage_Raw/Mauer_Referenz/mauer_heute.png – alle 15 Planeten mit der heutigen Mauer (Bildschirmfotos)
- Vorlage_Raw/Mauer_Referenz/mauer_lage.png – ganzes Kampfbild, rot: heutige Mauer, gelb: Platz für die neue
- Vorlage_Raw/Mauer_Referenz/mauer_schablone.png – die Schablone 780 × 260 mit den Maßlinien (siehe FORMAT)
- die Schlachtfelder selbst (780 × 1688): game/fields/space_dock.webp, ice_world.webp, desert_outpost.webp,
  lava_asteroid.webp, nebula_portal.webp

DIE FÜNF MAUERN (Material und Lichter aus Brücke und Geländer des jeweiligen Planeten übernehmen)
- mauer_01_space_dock.png – Raumstation: Barrikade aus blauweißen Stahl-Panzerplatten mit Nieten, cyanfarbene
  Leuchtstreifen, Pfosten mit kleinen Schildsendern. Lichtfarbe #5ab8ff.
- mauer_02_ice_world.png – Eiswelt: Mauer aus Eisblöcken und bereiftem Metall, ein paar Eiszapfen, hellblaue
  Kristallpfosten. Lichtfarbe #8fd8ff.
- mauer_03_desert_outpost.png – Wüstenaußenposten: Sandsteinblöcke mit Messingbändern und Nieten,
  bernsteinfarbene Lampen, an den Enden ein paar Sandsäcke. Lichtfarbe #ffc45a.
- mauer_04_lava_asteroid.png – Lava-Asteroid: Basalt und Obsidian mit glühenden Lavafugen, schwere Eisenplatten.
  Lichtfarbe #ff7a3d.
- mauer_05_nebula_portal.png – Nebelportal: dunkles Violettmetall mit leuchtenden Kristalleinsätzen und violetten
  Lichtern. Lichtfarbe #c08cff.

FORMAT (bitte genau einhalten, sonst passt die Mauer nicht auf die Brücke)
- je 780 × 260 Pixel, PNG mit durchsichtigem Hintergrund (RGBA). Geht das nicht sauber, dann auf einfarbigem
  Magenta #ff00ff ohne Verlauf und ohne Schatten auf dem Magenta.
- Das Bild ist der Ausschnitt y 940 bis 1200 des Schlachtfelds (siehe mauer_schablone.png):
  - Fuß der Mauer bei y = 228, gerade waagerecht über die ganze Breite (0 bis 780)
  - Oberkante des Mauerkörpers etwa bei y = 160 (Mauerkörper etwa 60–75 Pixel hoch)
  - nur schmale Aufbauten (Pfosten, Türmchen, Zinnen, Lampen, höchstens 6–8 Stück) dürfen bis y = 110 reichen,
    damit man die Gegner dahinter noch sieht
  - unter y = 228 höchstens ein weicher Schatten (bis 12 Pixel), sonst durchsichtig
  - über den Aufbauten alles durchsichtig
- Blick wie im Spiel: von vorn und leicht von oben, die Oberseite der Mauer ist ein wenig zu sehen.
- Gleicher Malstil wie die Schlachtfelder: kräftige Formen, klare Kanten, Glanzlichter, Comic, nicht fotorealistisch.
- Mitteldunkel mit Leuchtakzenten in der Lichtfarbe: Die bunten Champions davor und die Gegner dahinter müssen klar
  hervorstechen. Die Mauer soll stabil und wertig wirken, nicht überladen.
- Keine Schrift, keine Zahlen, keine Figuren, keine Gegner.
- jede Mauer ein eigenes Bild, nicht aus einem Sammelbild ausschneiden

ZUSÄTZLICH
- vorschau_01.png … vorschau_05.png: die Mauer auf das ganze Schlachtfeld gelegt (780 × 1688, an y = 940)
- uebersicht.png: alle fünf Vorschauen nebeneinander, verkleinert

BITTE LIEFERN in Vorlage_Raw/Mauern_v1/ auf GitHub (Branch claude/amazing-hypatia-yl59v4):
1. die fünf Mauern (PNG)
2. die fünf Vorschauen und uebersicht.png
3. LIESMICH_CLAUDE.md: je Datei Motiv, Material und Farben, und ob der Hintergrund durchsichtig oder Magenta ist
4. BILDANWEISUNG.txt: die verwendeten Bildprompts

Nur die eingebaute Bildgenerierung im bestehenden Konto verwenden, keine weiteren kostenpflichtigen Dienste.
~~~~

## Teil 2: Planeten 06–10 (erst nach Freigabe von Teil 1)

~~~~text
Danke für die Mauern 01–05, sie sind freigegeben. Bitte im selben Stil und genau im selben FORMAT wie in Teil 1
die Mauern für die Planeten 06–10 malen. Schlachtfelder: game/fields/jungle_moon.webp, ocean_world.webp,
crystal_planet.webp, storm_giant.webp, scrap_world.webp (Branch claude/amazing-hypatia-yl59v4). Stilvorlage sind die
gelieferten Mauern in Vorlage_Raw/Mauern_v1/.

- mauer_06_jungle_moon.png – Dschungelmond: Palisade aus dicken Stämmen und Steinen, Ranken, Moos, grüne Laternen.
  Lichtfarbe #5fe07a.
- mauer_07_ocean_world.png – Ozeanwelt: türkises Schott-Metall mit Korallen und Muscheln, Bullaugen-Lampen.
  Lichtfarbe #45d8e8.
- mauer_08_crystal_planet.png – Kristallplanet: rosa Kristallzinnen auf dunklem Fels. Lichtfarbe #ff7ad0.
- mauer_09_storm_giant.png – Sturmriese: gelb-schwarzes Warnmetall, Blitzableiter mit kleinen Funken.
  Lichtfarbe #ffd84a.
- mauer_10_scrap_world.png – Schrottwelt: zusammengeschweißte rostige Platten, Schrauben, alte Reifen,
  orangefarbene Lampen. Lichtfarbe #ff9a4a.

Dazu vorschau_06.png … vorschau_10.png und uebersicht_06_10.png. Liefern in Vorlage_Raw/Mauern_v1/, LIESMICH_CLAUDE.md
und BILDANWEISUNG.txt ergänzen. Nur die eingebaute Bildgenerierung im bestehenden Konto verwenden.
~~~~

## Teil 3: Planeten 11–15 und die zwei Arenen (erst nach Freigabe von Teil 2)

~~~~text
Danke, die Mauern 06–10 sind freigegeben. Bitte im selben Stil und genau im selben FORMAT wie in Teil 1 die
Mauern für die Planeten 11–15 und die zwei Arenen malen. Schlachtfelder: game/fields/cloud_city.webp,
spore_world.webp, ghost_moon.webp, temple_planet.webp, black_hole.webp, universums_arena.webp,
multiplayer_arena.webp (Branch claude/amazing-hypatia-yl59v4). Stilvorlage: Vorlage_Raw/Mauern_v1/.

- mauer_11_cloud_city.png – Wolkenstadt: weißer Marmor mit goldenen Kanten, hellblaue Lichter. Lichtfarbe #7ac8ff.
- mauer_12_spore_world.png – Sporenwelt: Pilzhüte, Wurzeln, leuchtende Sporenlampen. Lichtfarben #ffa040 und #1a8a7a.
- mauer_13_ghost_moon.png – Geistermond: alte Ruinensteine mit Efeu, grüne Geisterlaternen. Lichtfarbe #5fe0c0.
- mauer_14_temple_planet.png – Tempelplanet: goldene Tempelsteine mit Ornamenten (keine Schrift, keine Zeichen,
  die man lesen könnte). Lichtfarbe #ffd060.
- mauer_15_black_hole.png – Schwarzes Loch: die stärkste Festung, dunkles Obsidianmetall mit violetter Energie.
  Lichtfarbe #b98cff.
- mauer_16_universums_arena.png – Universums-Arena: Arena-Bande passend zur Tribüne, violette Lichter.
- mauer_17_multiplayer_arena.png – Multiplayer-Arena: Arena-Bande passend zur Tribüne, blaue Lichter.

Dazu vorschau_11.png … vorschau_17.png und uebersicht_11_17.png. Liefern in Vorlage_Raw/Mauern_v1/,
LIESMICH_CLAUDE.md und BILDANWEISUNG.txt ergänzen. Nur die eingebaute Bildgenerierung im bestehenden Konto verwenden.
~~~~
