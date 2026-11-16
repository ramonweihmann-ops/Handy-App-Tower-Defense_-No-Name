# Brücken der Planeten 06–15 überarbeiten – Auftrag für ChatGPT (Stand 16.11.2026)

**Reihenfolge:** Auftrag 2 von 5 (Übersicht in `Vorlage_Raw/AUFTRAEGE_REIHENFOLGE.md`).
**Kosten: keine.** Nur die eingebaute Bildbearbeitung im bestehenden Konto.

Befund (Planeten-Übersicht vom 16.11.2026): Die Planeten 01–05 haben eigene, aufwendige Brücken (Metall mit
Leuchtlinien, Eisplatten, Sandsteinfliesen, Lavagestein mit Glutfugen, Nebelmetall mit violetten Lichtern).
Bei den Planeten 06–15 ist die Brücke überall dieselbe schlichte Plankenbrücke, nur anders eingefärbt. Schon die
Originale sahen so aus, beim Einbau ist nichts verloren gegangen. Die Kulissen sind gut und bleiben.

Bild anhängen: `Vorlage_Raw/Bruecken_Referenz/bruecken_vergleich.png` (oben die fünf guten Brücken, unten die
zehn schlichten).

---

Ich entwickle ein Handy-Tower-Defense-Spiel (hochkant, Comic-Stil im Weltraum). Jeder Planet ist ein gemaltes
Schlachtfeld mit einer Brücke, über die die Gegner nach unten laufen. Bild `bruecken_vergleich.png` zeigt oben
die Brücken der ersten fünf Planeten: Jede hat ihr eigenes Material, eigene Geländer und Lichter, man erkennt
den Planeten schon an der Brücke. Unten die zehn neueren Planeten: Dort ist die Brücke überall dieselbe schlichte
Plankenbrücke. **Bitte bei diesen zehn Planeten nur die Brücke neu gestalten**, in derselben Qualität und
Detailfülle wie oben.

## So bitte arbeiten

Für jeden Planeten das vorhandene Bild **bearbeiten**, nicht neu erzeugen. Die Bilder liegen auf GitHub
(Repository Handy-App-Tower-Defense_-No-Name, Branch claude/amazing-hypatia-yl59v4) in
`Vorlage_Raw/Planeten_51_150_v1/Geprueft_2026_11_09/` (für die Ozeanwelt `ocean_world_korrigiert.png`).

- **Neu gestalten:** Fahrbahn der Brücke (Material, Plattenmuster, dezente Mittelmarkierung), Geländer und
  Brückenränder (Form, Verzierung, Lichter).
- **Unverändert lassen:** Kulisse, Himmel, Planeten links und rechts, die Plattform unten (ab y = 1169) und das
  Bildformat.
- **Lage, Form und Perspektive der Brücke genau beibehalten:** Fahrbahn oben von (280,294) bis (500,294), unten
  von (64,1158) bis (716,1158), Mitte x = 390, gerade, Brückenende bei y = 1158. Geländer und Verzierungen dürfen
  außen ein wenig überragen, die Fahrbahn selbst nicht.

## Lesbarkeit im Spiel

- Die **Fahrbahn bleibt mitteldunkel und eher entsättigt**, damit die bunten Gegner klar davor stehen. Leuchtende
  Akzente gehören an die Ränder und Geländer, auf der Fahrbahn höchstens eine dezente Mittelmarkierung.
- Keine feinen, sich wiederholenden Muster (Gitter, Streifen, Rauschen) auf der Fahrbahn: Das Bild wird im Spiel
  verkleinert und würde flimmern. Große Platten mit klaren Fugen wie bei Planet 01–05 sind richtig.
- Keine Figuren, keine Gegner, keine Schrift, keine Logos, keine Mauer.

## Die zehn Brücken

| Nr. | Datei | Planet | Neue Brücke |
|---|---|---|---|
| 06 | `jungle_moon.png` | Dschungelmond | dunkles Bronze-Metall mit großen Platten, Geländer aus Bronze mit Ranken, Moos und kleinen leuchtenden Blüten, smaragdgrüne Lampen in den Pfosten |
| 07 | `ocean_world_korrigiert.png` | Ozeanwelt | weiß-blaues Metall wie ein Schiffsdeck, runde Bullaugen-Lampen in Türkis an den Rändern, Geländer mit Rettungsringen und Tauen, unten Stelzen ins Wasser |
| 08 | `crystal_planet.png` | Kristallplanet | Platten aus mattem dunklem Kristallglas mit hellen Facettenkanten, an den Rändern Reihen kleiner rosa Kristalle, die von innen leuchten |
| 09 | `storm_giant.png` | Sturmriese | schweres graues Stahlgerüst mit Querstreben, Blitzableiter-Masten an den Geländern mit kleinen Funken, gelb-schwarze Warnstreifen nur am Rand, gelbe Warnlichter |
| 10 | `scrap_world.png` | Schrottwelt | vernietete Stahlplatten mit Rostflecken und Kupfer-Flicken, Geländer aus Rohren und Zahnrädern, orange Lampen in Käfigen |
| 11 | `cloud_city.png` | Wolkenstadt | weißer Marmor mit Goldeinlagen am Rand, Fahrbahn schiefergrau, Balustrade mit kleinen Säulen und goldenen Kugeln, himmelblaue Lichter |
| 12 | `spore_world.png` | Sporenwelt | dunkles Holz auf Metallträgern, kleine leuchtende Pilze in Orange und Türkis an den Rändern, Geländer aus gebogenen Pilzstielen |
| 13 | `ghost_moon.png` | Geistermond | alte dunkle Steinplatten mit Metallbeschlägen, Geländer aus Steinpfeilern mit kleinen Laternen in kaltem Türkis, leichter Bodennebel nur außen |
| 14 | `temple_planet.png` | Tempelplanet | sandfarbene Steinplatten mit goldenen Einlagen an den Fugen, Geländer aus kleinen Tempelsäulen mit goldenen Feuerschalen, warme goldene Lichter (keine Schriftzeichen) |
| 15 | `black_hole.png` | Schwarzes Loch | schwarzes Metall mit weißen und violetten Lichtkanten, schwere gepanzerte Seitenwände wie eine letzte Verteidigungslinie, Energiefeld-Pfosten in Violett |

Jede Brücke muss sich auf einen Blick von den anderen 14 unterscheiden.

## Technik und Prüfung

- PNG, genau 780 × 1688 Pixel, RGB ohne Transparenz, Dateiname wie in der Tabelle (Ozean: `ocean_world.png`).
- Danach selbst prüfen: die vier Fahrbahnecken ablesen, Abweichung höchstens etwa ±6 Pixel.
- `uebersicht.png`: oben die zehn Brücken vorher, darunter nachher, verkleinert nebeneinander.

## Ablauf und Lieferung

1. **Erst zwei Planeten zur Abstimmung:** `crystal_planet.png` und `cloud_city.png`. Ich prüfe sie im Spiel und
   gebe Rückmeldung.
2. Danach die übrigen acht im selben Stil.

Bitte liefern in den Ordner **`Vorlage_Raw/Bruecken_06_15_v1/`** auf GitHub
(Repository `Handy-App-Tower-Defense_-No-Name`, Branch **`claude/amazing-hypatia-yl59v4`**):
1. die Schlachtfelder (Namen wie in der Tabelle)
2. `uebersicht.png`
3. `LIESMICH_CLAUDE.md`: je Datei Planet und Ergebnis der Maßprüfung (vier Ecken)
4. `BILDANWEISUNGEN.json`: die verwendeten Bildprompts je Datei

Nur die eingebaute Bildbearbeitung im bestehenden Konto verwenden, keine weiteren kostenpflichtigen Dienste.
