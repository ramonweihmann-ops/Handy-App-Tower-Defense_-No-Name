# Neue Planeten für Level 51–150: Auftrag für ChatGPT (Stand 06.11.2026)

Zum Kopieren in ChatGPT. Dazu als Bilder anhängen:
- `Vorlage_Raw/Karten_v3/space_dock.png`: **Bild 1**, die Geometrie-Vorlage, die für jeden Planeten bearbeitet wird
- `Vorlage_Raw/Planeten_Referenz/planeten_bisher.png`: die fünf bisherigen Planeten (Stil und Qualität)
- `Vorlage_Raw/Planeten_Referenz/schablone_bruecke.png`: Maße der Brücke und Bereiche (nur zur Orientierung)
- `Vorlage_Raw/Planeten_Referenz/kampf_im_spiel.png`: so sieht ein Planet im Spiel aus, mit Gegnern, Mauer, Held und Anzeigen darüber

---

Ich entwickle ein Handy-Tower-Defense-Spiel (hochkant, Comic-Stil im Weltraum, Godot). Jeder Planet ist ein
gemaltes Schlachtfeld: eine Brücke führt von oben in die Bildmitte nach unten zu einer Verteidigungsplattform.
Die Gegner laufen über die Brücke nach unten, die Helden stehen unten auf der Plattform. Gegner, Helden, Mauer
und alle Anzeigen legt das Spiel selbst darüber. Es gibt schon fünf Planeten (Bild `planeten_bisher.png`).
Für Level 51–150 brauche ich **zehn neue Planeten**, je einen für 10 Level.

## So bitte arbeiten

Für jeden Planeten **Bild 1 (`space_dock.png`) bearbeiten**, nicht frei neu erzeugen: Kulisse, Himmel,
Planeten, Brückenmaterial und Bodenmaterial neu gestalten, aber **Lage, Form, Perspektive und Kamera der
Brücke und der Plattform genau beibehalten**. Nur so passen Gegnerweg und Mauer im Spiel ohne Nacharbeit.

## Feste Maße (alle Planeten gleich)

Koordinaten im Bild 780 × 1688 Pixel, Ursprung oben links (siehe `schablone_bruecke.png`):

- **Fahrbahn der Brücke:** obere Kante von (280,294) bis (500,294), untere Kante von (64,1158) bis
  (716,1158), Mitte x = 390. Gerade, kein Knick, keine Kurve, nicht länger oder kürzer. Geländer, Lichter,
  Frost, Ranken usw. dürfen die Kante außen ein wenig überragen, die Fahrbahn selbst nicht.
- **Brückenende** genau bei y = 1158. Oben kein Tor, kein Tunnel, nichts, das die Fahrbahn verdeckt.
- **Plattform** ab y = 1169 bis zum unteren Rand: flach und ruhig wie bei den bisherigen Planeten
  (dünne bündige Fugen, wenige kleine Nieten, feine Materialstruktur, dezente Randlichter im Planeten-Farbton).
  Keine Fahrbahnfortsetzung, keine dicken Rahmen, keine hellen Lichtleisten.
- **y 1169–1410:** Standplatz der Helden, frei und flach.
- **y 1410–1688:** hier liegen Anzeigen und Fähigkeits-Knöpfe, darum besonders ruhig und eher dunkel.
- **y 0–110:** hier liegt im Spiel die Kopfleiste. Dort keine wichtigen Details (kein Planetenmittelpunkt,
  keine Hauptfigur der Kulisse).

## Damit es im Spiel gut lesbar ist

- Die **Fahrbahn ist mitteldunkel und eher entsättigt**, damit die bunten Gegner (grün, violett, rot, blau)
  klar davor stehen. Keine grellen Flächen und keine starken Lichtlinien mitten auf der Fahrbahn; eine dezente
  Mittelmarkierung ist erlaubt. Leuchtende Akzente gehören an die Ränder und Geländer.
- Keine feinen, sich wiederholenden Muster (Gitter, Streifen, Rauschen) auf Fahrbahn und Plattform: Das Bild
  wird im Spiel verkleinert und würde sonst flimmern.
- Die Kulisse links und rechts darf lebendig sein (Planeten, Monde, Ringe, Stationen, Felsen), soll aber nicht
  heller sein als die Brücke.
- Jeder Planet muss sich auf einen Blick von den anderen 14 unterscheiden (Farbe, Material, Kulisse).
- Stil wie die bisherigen fünf: hochwertiger, stilisierter Comic- und 3D-Spielgrafikstil, kräftige Farben,
  Licht von oben, kein Fotorealismus.
- Keine Figuren, keine Gegner, keine Schrift, keine Logos, keine Knöpfe, keine Mauer. Nichts von anderen
  Spielen nachmachen.

## Die zehn Planeten

| Nr. | Datei | Level | Planet | Kulisse | Brücke und Plattform |
|---|---|---|---|---|---|
| 06 | `jungle_moon.png` | 51–60 | Dschungelmond | dichter Urwald auf schwebenden Felsinseln, Riesenpflanzen, leuchtende Blüten, grüner Gasriese am Himmel | dunkles Bronze-Metall, Ranken und Moos nur an den Geländern, smaragdgrüne Randlichter |
| 07 | `ocean_world.png` | 61–70 | Ozeanwelt | endloses türkisfarbenes Meer, Wasserfälle von schwebenden Inseln, Korallentürme, zwei Monde | Brücke auf Stelzen über dem Wasser, weißes und blaues Metall, Gischt nur außen, türkise Lichter |
| 08 | `crystal_planet.png` | 71–80 | Kristallplanet | rosa und magentafarbene Riesenkristalle, funkelnder Sternenhimmel | Fahrbahn aus mattem dunklem Kristallglas, Ränder mit kleinen Kristallen, rosa Randlichter |
| 09 | `storm_giant.png` | 81–90 | Sturmriese | Gasriese mit gelben und blauen Wolkenbändern, Blitze in den Wolken, Wirbelsturm im Hintergrund | stabiles graues Stahlgerüst, Blitzableiter an den Geländern, gelbe Warnlichter |
| 10 | `scrap_world.png` | 91–100 | Schrottwelt | Roboterfabrik und Schrottberge, große Zahnräder, Schornsteine mit Dampf, Kupfertöne | rostiges Kupfer und vernietete Stahlplatten, orange Lampen |
| 11 | `cloud_city.png` | 101–110 | Wolkenstadt | heller Taghimmel über Wolken, schwebende weiße Türme mit goldenen Kuppeln (die einzige helle Welt) | weißer Marmor mit Gold, himmelblaue Lichter; Fahrbahn trotzdem mitteldunkel (Schiefergrau) |
| 12 | `spore_world.png` | 111–120 | Sporenwelt | Wald aus riesigen leuchtenden Pilzen in Orange und Türkis, schwebende Sporen | dunkles Holz und Metall, Pilze klein an den Rändern, orange und türkise Lichter |
| 13 | `ghost_moon.png` | 121–130 | Geistermond | nächtliche Ruinen im Nebel, blasser Mond, gespenstisches grünlich-blaues Licht (freundlich, nicht gruselig) | alter dunkler Stein mit Metallbeschlägen, kalte türkise Lichter |
| 14 | `temple_planet.png` | 131–140 | Tempelplanet | uralte Alien-Tempel und Säulen in einer Felsenschlucht, goldene Verzierungen (keine Schrift, keine echten Schriftzeichen) | sandfarbener Stein mit goldenen Einlagen, warme goldene Lichter |
| 15 | `black_hole.png` | 141–150 | Schwarzes Loch (Finale) | riesiges Schwarzes Loch mit leuchtender Scheibe, verzerrtes Sternenlicht, Trümmer von Raumschiffen | schwarzes Metall mit weißen und violetten Lichtkanten, wirkt wie die letzte Verteidigungslinie |

## Zusätzlich: Planetensymbole (klein)

Für jeden der zehn neuen **und** der fünf bisherigen Planeten ein rundes Planetensymbol, wie ein kleiner
Planet im Weltraum (Kugel mit dem Charakter der Welt, ggf. Ring oder Mond), ohne Hintergrund. Das Spiel zeigt
es bei der Meldung „Neuer Planet entdeckt“ und bei der Planetenwahl.

- `icon_<datei>.png`, zum Beispiel `icon_jungle_moon.png`, und für die bisherigen `icon_space_dock.png`,
  `icon_ice_world.png`, `icon_desert_outpost.png`, `icon_lava_asteroid.png`, `icon_nebula_portal.png`
- 512 × 512 Pixel, **transparenter Hintergrund**, Motiv mittig mit etwa 8 % Rand, gut erkennbar auch bei
  60 Punkten Breite

## Technik

- Schlachtfelder: **PNG, genau 780 × 1688 Pixel, RGB ohne Transparenz**, ein fertig zusammengesetztes Bild
  (keine Ebenen nötig). Falls die Bildgenerierung ein anderes Format liefert: ohne Verzerren skalieren und so
  zuschneiden, dass die Brücke wieder genau auf den Maßen oben liegt.
- Danach selbst prüfen: Linien der Schablone auf das Ergebnis legen; die Fahrbahnkanten müssen auf etwa
  ±6 Pixel passen.
- `uebersicht.png`: alle zehn Schlachtfelder verkleinert nebeneinander, darunter die 15 Symbole, zur Kontrolle.

## Ablauf und Lieferung

1. **Erst zwei Planeten zur Abstimmung:** `jungle_moon.png` und `ocean_world.png` mit Symbol. Ich prüfe sie im
   Spiel und gebe Rückmeldung.
2. Danach die übrigen acht Planeten und alle Symbole im selben Stil.

Bitte liefern in den Ordner **`Vorlage_Raw/Planeten_51_150_v1/`** auf GitHub
(Repository `Handy-App-Tower-Defense_-No-Name`, Branch **`claude/amazing-hypatia-yl59v4`**):
1. die Schlachtfelder (Namen wie in der Tabelle)
2. die Symbole `icon_*.png`
3. `uebersicht.png`
4. `LAYOUT_FUER_CLAUDE.md`: je Datei Planet, Level, Größe; Ergebnis der Maßprüfung je Bild
5. `BILDANWEISUNGEN.json`: die verwendeten Bildprompts je Datei
6. `PRUEFBERICHT.json`: je Datei Breite, Höhe, ob die Brückenmaße eingehalten sind

Nur die eingebaute Bildgenerierung im bestehenden Konto verwenden, keine weiteren kostenpflichtigen Dienste.
