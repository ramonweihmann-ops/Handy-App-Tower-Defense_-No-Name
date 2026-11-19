# Prompts für ChatGPT (Stand 16.11.2026)

Nacheinander abschicken: den nächsten erst, wenn der vorige geliefert ist und Claude ihn geprüft hat.
Jeden Prompt komplett zwischen den Linien kopieren. Quelle und Hintergrund: `AUFTRAEGE_REIHENFOLGE.md`.

## Prompt 1: Ranglisten, Ligen, Spielerrahmen, Überleben, Gegnersuche

**Kosten:** keine Kosten · **Abschicken:** sofort

~~~~text
Die Referenzbilder liegen auf GitHub (Repository Handy-App-Tower-Defense_-No-Name, Branch claude/amazing-hypatia-yl59v4) in Vorlage_Raw/Ranglisten_Referenz/: rangliste_entwurf.png, symbole_vorhanden.png, spielerbilder_vorhanden.png. Bitte von dort laden.

Ich entwickle ein Handy-Tower-Defense-Spiel (hochkant, Comic-Stil im Weltraum, Godot). Spieler treten im
Mehrspieler gegeneinander an und steigen in Ligen auf. Dazu kommt ein Modus „Überleben“ mit eigener Rangliste:
Wer hält am längsten durch? Der Ranglisten-Bildschirm ist gestaltet (Bild `rangliste_entwurf.png`). Es fehlen die
Grafiken für Ligen, Pokale, Spielerrahmen und Überleben. Bitte genau diese Bilder erstellen, nichts weiter.

**Stil (wie `symbole_vorhanden.png`):** weiche, glänzende Comic-Schattierung, kräftige Farben, Licht von links oben,
kein Fotorealismus, keine dicke schwarze Kontur. Freundlich und für Kinder ab 6 geeignet, aber edel genug, dass
man stolz darauf ist. **Keine Schrift, keine Zahlen, keine Buchstaben** auf den Bildern (das Spiel schreibt selbst),
keine Logos, nichts von anderen Spielen nachmachen.

**Wichtig für alle Abzeichen:** Die sieben Liga-Abzeichen sind eine Familie. Gleiche Grundform (ein Wappenschild),
gleiche Größe im Bild, gleiche Blickrichtung (frontal). Von Liga zu Liga werden sie **sichtbar prächtiger**: mehr
Flügel, mehr Glanz, größere Krone. Man muss die Rangfolge auf einen Blick erkennen, auch ganz klein (im Spiel
40–120 Punkte breit).

### A. Liga-Abzeichen (7 Bilder)

| Datei | Liga | Farbe | Motiv |
|---|---|---|---|
| `liga_bronze.png` | Bronze | Kupfer-Orange (#e8964a / #a8561a) | einfaches, rundliches Schild mit einem Stern in der Mitte |
| `liga_silber.png` | Silber | Silber (#e6eaee / #8d949c) | Schild mit Stern, links und rechts kleine Flügelansätze |
| `liga_gold.png` | Gold | Gold (#ffe27a / #c8901a) | Schild mit Stern, zwei Flügel, kleine Krone oben |
| `liga_diamant.png` | Diamant | Eisblau (#8fe8ff / #2a8ad8) | Schild mit großem geschliffenem Diamanten in der Mitte, Flügel, Krone, Funkeln |
| `liga_kristall.png` | Kristall | Violett (#b48cff / #5a3fd8) | Schild aus Kristall mit großen Kristallzacken als Flügeln, Krone mit Edelstein, starkes Funkeln (prächtiger als Diamant) |
| `liga_galaxie.png` | Galaxie | Pink-Magenta (#ff9fe0 / #c2508f) | Schild mit Spiralgalaxie in der Mitte, große prächtige Flügel, Krone mit Edelstein |
| `liga_legende.png` | Legende | Gold mit Regenbogenschimmer | das prächtigste: Krone über einem Planeten mit Ring, goldene Flügel, Strahlenkranz |

### B. Pokale und Saison (5 Bilder)

| Datei | Motiv | Wo im Spiel |
|---|---|---|
| `pokal_symbol.png` | einzelner goldener Pokal, schlicht, gut lesbar auch bei 20 Punkten | Pokalzahl oben in der Leiste und in der Liste |
| `saisonpokal_1.png` | großer goldener Siegerpokal mit Stern, leuchtend | Saisonende, Platz 1 |
| `saisonpokal_2.png` | derselbe Pokal in Silber | Saisonende, Platz 2 |
| `saisonpokal_3.png` | derselbe Pokal in Bronze | Saisonende, Platz 3 |
| `saison_truhe.png` | Truhe in Violett-Gold mit Pokal-Prägung auf dem Deckel, leicht geöffnet, Licht strahlt heraus | Belohnung zum Saisonwechsel |

### C. Rahmen für Spielerbilder (10 Bilder)

Runde Rahmen, die um unsere runden Spielerbilder gelegt werden (`spielerbilder_vorhanden.png`). **Die Mitte ist
komplett durchsichtig** (ein Kreis mit etwa 62 % des Bilddurchmessers), damit das Spielerbild darunter zu sehen ist.

| Datei | Motiv |
|---|---|
| `rahmen_bronze.png`, `rahmen_silber.png`, `rahmen_gold.png`, `rahmen_diamant.png`, `rahmen_kristall.png`, `rahmen_galaxie.png` (6 Dateien) | Ring in der Farbe der Liga, mit dem Schmuck des Liga-Abzeichens (Stern, Flügel, Krone) |
| `rahmen_legende.png` | Ring wie das Legende-Abzeichen, mit Strahlenkranz |
| `rahmen_platz1.png` | goldener Ring mit großer Krone oben und Lorbeerkranz, für den Besten der Weltrangliste |
| `rahmen_top10.png` | silber-goldener Ring mit kleiner Krone, für die Top 10 |
| `rahmen_top100.png` | Ring mit Sternen, für die Top 100 |

### D. Überleben (8 Bilder)

| Datei | Motiv | Größe |
|---|---|---|
| `ueberleben_titel.png` | Titelbild des Modus: unsere Station auf der Brücke, von allen Seiten kommen Gegnerscharen, darüber eine große Stoppuhr, die rot glüht. Spannend, nicht gruselig. **Nicht durchsichtig**, ohne Schrift. | 780 × 420 |
| `ueberleben_symbol.png` | Stoppuhr mit Unendlich-Zeichen auf dem Zifferblatt, für die Kachel im Menü | 512 × 512 |
| `medaille_3min.png` | runde Medaille mit Stoppuhr-Motiv, Bronze | 512 × 512 |
| `medaille_6min.png` | dieselbe in Silber | 512 × 512 |
| `medaille_9min.png` | dieselbe in Gold | 512 × 512 |
| `medaille_12min.png` | dieselbe in Diamant-Eisblau | 512 × 512 |
| `medaille_15min.png` | dieselbe in Kristall-Violett | 512 × 512 |
| `medaille_20min.png` | dieselbe in Galaxie-Pink mit Flammenkranz, die prächtigste | 512 × 512 |

Die Medaillen sind wie die Liga-Abzeichen eine Familie: gleiche Form, von Stufe zu Stufe prächtiger.

### E. Gegnersuche (1 Bild)

| Datei | Motiv | Größe |
|---|---|---|
| `gegnersuche_hintergrund.png` | Hintergrund für die Gegnersuche: dunkler Weltraum (dunkelviolett #1a1240 bis #2a1f63), in der Mitte ein großer Radarkreis mit leuchtenden Ringen und einem Lichtstrahl, ein paar Sterne. Ruhig, damit Schrift und Spielerbilder darüber gut lesbar sind. **Nicht durchsichtig**, ohne Schrift. | 780 × 1688 |

## Technik

- Alle Bilder außer Titelbild und Hintergrund: einzeln als PNG mit **transparentem Hintergrund**, **512 × 512 Pixel**,
  Motiv mittig mit etwa 8 % Rand.
- Gut lesbar auch ganz klein.
- Zusätzlich `uebersicht.png`: alle Bilder geordnet nach A–E auf dunkelviolettem Grund (#2a1f63), zur Kontrolle.

## Bitte liefern

Ordner `Vorlage_Raw/Ranglisten_v1/` auf GitHub, Repository `Handy-App-Tower-Defense_-No-Name`,
Branch `claude/amazing-hypatia-yl59v4`:
1. die 31 Bilddateien (Namen wie oben)
2. `uebersicht.png`
3. `LIESMICH_CLAUDE.md`: Tabelle je Datei mit Motiv, Größe und Verwendung (aus diesem Auftrag übernehmen)
4. `BILDANWEISUNG.txt`: die verwendeten Bildprompts

Nur die eingebaute Bildgenerierung im bestehenden Konto verwenden, keine weiteren kostenpflichtigen Dienste.
~~~~

## Prompt 1b: Nachtrag zu Prompt 1 (Liganamen geändert)

**Abschicken:** sofort hinterher, weil ChatGPT schon an Prompt 1 arbeitet

~~~~text
Nachtrag zum Auftrag „Ranglisten, Ligen …“ – bitte vor dem Abschluss noch berücksichtigen:

Die Ligen heißen jetzt (von unten nach oben): Bronze, Silber, Gold, Diamant, Kristall, Galaxie, Legende.
Die Sternen-Liga entfällt. Dadurch ändern sich vier Bilder:

1. liga_sternen.png entfällt. Neu: liga_diamant.png (4. Liga) – Eisblau (#8fe8ff / #2a8ad8), Schild mit großem
   geschliffenem Diamanten in der Mitte, Flügel, Krone, Funkeln.
2. liga_kristall.png ist jetzt die 5. Liga, also eine Stufe über Diamant: Violett (#b48cff / #5a3fd8), Schild aus
   Kristall mit großen Kristallzacken als Flügeln, Krone mit Edelstein, starkes Funkeln. Muss sichtbar prächtiger
   sein als Diamant und etwas schlichter als Galaxie.
3. rahmen_sternen.png entfällt. Neu: rahmen_diamant.png (eisblau, mit Diamant-Schmuck). rahmen_kristall.png im Stil
   des neuen Kristall-Abzeichens.
4. Medaillen: medaille_12min.png in Diamant-Eisblau, medaille_15min.png in Kristall-Violett.

Die Rangfolge muss auf einen Blick erkennbar bleiben: Bronze < Silber < Gold < Diamant < Kristall < Galaxie < Legende.
Alles andere bleibt wie im Auftrag. Die Übersicht und LIESMICH_CLAUDE.md bitte entsprechend anpassen.
Der aktualisierte Auftrag liegt auf GitHub unter Vorlage_Raw/RANGLISTEN_FUER_CHATGPT.md.
~~~~

## Prompt 1c: Arenen neu (Bahn unten auf dem Arenaboden)

**Kosten:** keine · **Abschicken:** nach Prompt 1 (Wunsch vom 16.11.2026)

~~~~text
Die Bilder liegen auf GitHub (Repository Handy-App-Tower-Defense_-No-Name, Branch claude/amazing-hypatia-yl59v4):
Vorlage_Raw/Arena_Karten_v1/universums_arena.png, Vorlage_Raw/Arena_Karten_v1/multiplayer_arena.png und die
Maßschablone Vorlage_Raw/Planeten_Referenz/schablone_bruecke.png. Bitte von dort laden.

Ich entwickle ein Handy-Tower-Defense-Spiel (hochkant, Comic-Stil im Weltraum). Für zwei Spielmodi gibt es je eine
Arena als Schlachtfeld (Bilder universums_arena.png und multiplayer_arena.png). Die Gegner laufen auf einer Bahn von
oben nach unten zu unserer Verteidigungsplattform. Problem: In beiden Bildern sieht die Bahn aus wie eine Brücke, die
nach oben zur obersten Tribüne ansteigt. Das wirkt falsch. **Bitte beide Arenen so neu zeichnen:**

- Die Bahn liegt **flach unten auf dem Arenaboden**, wie eine Kampfbahn in einem Stadion. Kein Brückengeländer, das
  in die Höhe führt; seitlich nur eine niedrige Bande oder Leuchtkante.
- **Ringsum steigen die Tribünen an** (links, rechts und hinten), voll mit kleinen, angedeuteten Zuschauern, Lichtern
  und Fahnen. Man sieht alle Ränge, die von oben auf die Bahn herabschauen.
- **Am oberen Ende der Bahn** ist ein großer, leuchtender **Tunnel unter der hinteren Tribüne**. Aus ihm kommen die
  Gegner. Der Tunnel sitzt hinter dem Bahnende und verdeckt die Bahn nicht.
- Über dem Tunnel an der hinteren Tribüne eine große Anzeigetafel (ohne Schrift, ohne Zahlen, nur leuchtende Fläche;
  das Spiel schreibt selbst darauf).
- Unten bleibt unsere Verteidigungsplattform wie bisher (ab y = 1169, flach und ruhig).

**Feste Maße (wie bei allen Schlachtfeldern, Bild 780 × 1688 Pixel):** Fahrbahn oben von (280,294) bis (500,294),
unten von (64,1158) bis (716,1158), Mitte x = 390, gerade, Ende genau bei y = 1158. Die Perspektive bleibt so,
nur sieht die Fläche jetzt wie Boden aus statt wie eine Brücke. y 0–110 ohne wichtige Details (Kopfleiste im Spiel).
Fahrbahn mitteldunkel und ruhig, keine feinen Muster, damit die bunten Gegner gut zu sehen sind.

**Die zwei Arenen:**

| Datei | Modus | Stimmung |
|---|---|---|
| `ueberleben_arena.png` | Überleben (endlos) | violett-gold wie die bisherige Universums-Arena, dazu warmes Orange-Rot am Tunnel, als käme von dort ohne Ende Nachschub; dramatisch, aber freundlich |
| `multiplayer_arena.png` | Mehrspieler | blau-violett mit Fahnen in vier Farben (blau, rot, grün, gelb) für die vier Kommandanten |

Stil wie die bisherigen Bilder: hochwertiger, stilisierter Comic- und 3D-Spielgrafikstil, kräftige Farben, kein
Fotorealismus. Keine Figuren auf der Bahn, keine Gegner, keine Schrift, keine Logos.

**Technik:** PNG, genau 780 × 1688 Pixel, RGB. Danach die vier Fahrbahnecken ablesen (höchstens etwa ±6 Pixel).

**Bitte liefern** in `Vorlage_Raw/Arena_Karten_v2/`: die zwei Bilder, `uebersicht.png` (alt und neu nebeneinander),
`LIESMICH_CLAUDE.md` mit der Maßprüfung, `BILDANWEISUNGEN.json` mit den Prompts.

Nur die eingebaute Bildgenerierung im bestehenden Konto verwenden, keine weiteren kostenpflichtigen Dienste.
~~~~

## Prompt 2: Brücken der Planeten 06–15 neu gestalten

**Kosten:** keine Kosten · **Abschicken:** sofort

~~~~text
Das Vergleichsbild liegt auf GitHub (Repository Handy-App-Tower-Defense_-No-Name, Branch claude/amazing-hypatia-yl59v4) unter Vorlage_Raw/Bruecken_Referenz/bruecken_vergleich.png. Bitte von dort laden.

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
~~~~

## Prompt 3: Quallenflieger: Modell mit acht Armen nachreichen

**Kosten:** keine Kosten · **Abschicken:** sofort (freigegeben am 11.11.2026)

~~~~text
Bitte das Meshy-Modell des Quallenfliegers aus dem Ozean-Auftrag (Modelltests_v6), das wegen acht statt vier
Fangarmen als Fehlversuch gemeldet wurde, trotzdem auf GitHub bereitstellen. Repository
Handy-App-Tower-Defense_-No-Name, Branch claude/amazing-hypatia-yl59v4.

WICHTIG
- Keinen neuen Meshy-Versuch starten, keine Credits ausgeben, nichts nachbearbeiten.
- Genau die damals heruntergeladene Datei, bytegleich (die „fehlerhafte lokale GLB“ aus dem Fehlbericht).
- Falls die Datei nicht mehr vorhanden ist: nur das melden. Nicht neu erzeugen.

ABLAGE in Vorlage_Raw/Monster_Roh/Modelltests_v6/:
- quallenflieger_statisch_roh_8arme.glb (unverändert)
- im vorhandenen quallenflieger_FEHLVERSUCH.md einen Absatz ergänzen: Datei nachgereicht, Größe, SHA-256,
  Dreiecke, keine weiteren Credits
~~~~

## Prompt 4: Kartenmotive für sieben Symbiosen und das Meister-Abzeichen

**Kosten:** keine Kosten · **Abschicken:** erst wenn du die Mockups „Karten-Meister“ und „Karten-Symbiose“ freigegeben hast

~~~~text
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
~~~~

## Prompt 4b: Fähigkeiten der Champions und fehlende Kartenlogos (23 Motive)

**Kosten:** keine · **Abschicken:** jederzeit (Fähigkeiten bestätigt am 16.11.2026)

~~~~text
Bitte für mein Handyspiel (Tower Defense, Comic-Stil) 23 Motive erzeugen: Fähigkeiten der Champions und vier
fehlende Kartenlogos.

STILVORLAGE: genau wie die 31 vorhandenen Kartenmotive im Repository Handy-App-Tower-Defense_-No-Name, Branch
claude/amazing-hypatia-yl59v4, Ordner Vorlage_Raw/Kartenmotive_v2/ (zum Beispiel tesla_special.png,
cryo_special.png, revolver_ult.png). Kräftige Comic-Umrisse, satte Farben, leichte Glanzlichter, ein Gegenstand oder
Effekt groß in der Mitte. Bitte von dort laden.

FORMAT
- je 512 × 512 Pixel, PNG mit durchsichtigem Hintergrund (RGBA), Motiv mittig, etwa 8 % Rand frei
- keine Schrift, keine Zahlen, keine Rahmen, keine Karte drumherum, kein Hintergrund
- muss auch klein (56 Punkte) sofort erkennbar sein: wenige, große Formen
- keine Personen, nur Waffe, Gegenstand oder Effekt
- jedes Motiv ein eigenes Bild, nicht aus einem Sammelbild ausschneiden
- jedes Motiv muss sich klar von den vorhandenen Motiven desselben Champions unterscheiden

DATEINAMEN UND INHALT (Dateiname genau so)

A. Fähigkeiten der acht Champions (je Champion zwei; einige gibt es schon, diese hier fehlen):
- talent_dusty_schnellzieher.png – Schnellzieher: Revolver, der aus dem Holster gezogen wird, mit Bewegungsstreifen
  und kleiner Stoppuhr (Tempo am Wellenanfang)
- talent_iska_leuchtspur.png – Leuchtspur: Kugel mit grellem Leuchtschweif, die am Ende in einer kleinen Explosion endet
- talent_iska_doppelmagazin.png – Doppelmagazin: zwei zusammengeklebte Magazine, das obere glüht (stärkere Schüsse)
- talent_brocken_splitterregen.png – Splitterregen: Raketeneinschlag, aus dem viele kleine Splitter fächerförmig fliegen
- talent_brocken_schwerer_treffer.png – Schwerer Treffer: dicke Rakete mit großem Rückstoß-Pfeil und Druckwelle
- talent_kalle_frostmantel.png – Frostmantel: Schneeflocke in einem Ring aus kaltem Nebel, wirkt bremsend
- talent_fritzi_brandspur.png – Brandspur: Feuerspur auf dem Boden, Flammen in einer Linie
- talent_fritzi_hitzewelle.png – Hitzewelle: breite, gewellte Flammenwand, die nach vorn rollt
- talent_volta_ueberspannung.png – Überspannung: Akku mit Blitz, der über den Rand knistert (Extra-Schaden gegen Bosse:
  kleiner Boss-Stern daneben)
- talent_margot_enterhaken.png – Enterhaken: Enterhaken an einem Seil, das sich spannt
- talent_lynx_zielfernrohr.png – Zielfernrohr: Zielfernrohr mit funkelndem Linsen-Glanz und kleinem Stern

B. Fähigkeiten der übrigen vier Champions (je zwei, neu):
- talent_fuenkchen_sternenstaub.png – Sternenstaub: Wolke aus funkelndem lila-goldenem Staub (getroffene Gegner nehmen mehr Schaden)
- talent_fuenkchen_kometenschweif.png – Kometenschweif: kleiner Komet mit breitem Schweif, der drei Spuren zieht
- talent_pip_notreparatur.png – Notreparatur: Schraubenschlüssel mit rotem Warnlicht und grünem Plus
- talent_pip_ersatzteile.png – Ersatzteile: Häufchen aus Zahnrädern, Schrauben und einem Schildstück
- talent_rollo_panzerplatte.png – Panzerplatte: dicke, vernietete Stahlplatte mit Sternprägung
- talent_rollo_doppelwumms.png – Doppelwumms: zwei Kanonenkugeln hintereinander mit doppelter Druckwelle
- talent_nova_miniloch.png – Mini-Loch: kleiner violetter Wirbel, der Funken nach innen zieht
- talent_nova_zeitdehnung.png – Zeitdehnung: verbogene Sanduhr in einem violetten Schwerkraftring

C. Fehlende Kartenlogos (bisher alte Symbole):
- held_damage.png – Mehr Schaden: Kugel mit kräftigem Aufprallstern und Pfeil nach oben
- held_crit.png – Kritische Treffer: Zielscheibe, deren Mitte mit einem goldenen Blitzstern getroffen ist
- gate_fire.png – Feuer-Plasma: Plasmakugel (wie gate_ice.png, aber orange-rot) mit Flammen
- plasma_core.png – Energiekern: leuchtender türkiser Energiekern in einer goldenen Fassung (passend zu plasma_mag.png und gate_ice.png)

ZUSÄTZLICH
- uebersicht_56px.png: alle Motive verkleinert auf 56 Punkte, nach Champion gruppiert, zur Kontrolle der Lesbarkeit

BITTE LIEFERN in Vorlage_Raw/Kartenmotive_v4/ auf GitHub (Branch claude/amazing-hypatia-yl59v4):
1. die PNG-Dateien
2. uebersicht_56px.png
3. LIESMICH_CLAUDE.md: je Datei Motiv und Champion
4. BILDANWEISUNG.txt: die verwendeten Bildprompts

Nur die eingebaute Bildgenerierung im bestehenden Konto verwenden, keine weiteren kostenpflichtigen Dienste.
~~~~

## Prompt 5: 3D-Gegner Planet 08 (Kristallplanet), danach 09–15 genauso

**Kosten:** etwa 60 Meshy-Credits je Planet · **Abschicken:** erst nach deiner Freigabe für Planet 08 (noch nicht erteilt). Für Planet 09–15 bekommst du den Prompt jeweils fertig von mir, sobald du den Planeten freigibst

~~~~text
Bitte aus den vier freigegebenen Bildvorlagen von Planet 08 bei Meshy je ein 3D-Modell erzeugen, für mein
Handyspiel (Tower Defense, Comic-Stil). Die Vorlagen liegen auf GitHub (Repository Handy-App-Tower-Defense_-No-Name,
Branch claude/amazing-hypatia-yl59v4) unter Vorlage_Raw/Gegner_51_150_v1/Einzelvorlagen/08_leicht.png,
08_mittel.png, 08_stark.png, 08_boss.png.
Ausnahme: Für 11_leicht.png und 12_boss.png die Dateien aus Einzelvorlagen/Ersatz_aus_Uebersicht/ nehmen.

KOSTENRAHMEN: höchstens 4 Erzeugungen, etwa 60 Meshy-Credits, vom Nutzer für diesen Planeten freigegeben. Wenn
Rigging oder Bewegungen extra kosten, vorher melden und nicht ungefragt buchen. Je Gegner nur ein Versuch; wenn er
misslingt, melden statt neu erzeugen.

KÖRPERBAU UND RIGGING (aus Einzelvorlagen/LIESMICH_CLAUDE.md, genau so zählen)

| Vorlage | Name | Körperbau | Meshy-Rigging |
|---|---|---|---|
| 08_leicht | Kristallwichtel | Zweibeiner, 2 Arme, 2 Beine | humanoid mit `Walking` und `Attack` |
| 08_mittel | Glitzerfledermaus | Flieger, 2 Flügel, 2 kleine Beine | keins |
| 08_stark | Quarzkäfer | Krabbeltier, genau 6 Beine | keins |
| 08_boss | Kristallgolem | Zweibeiner, 2 Arme, 2 Beine | humanoid mit `Walking` und `Attack` |
| 09_leicht | Funkenball | kompakter Schwebekörper, keine Gliedmaßen | keins |
| 09_mittel | Donnervogel | Flieger, 2 Flügel, 2 Beine | keins |
| 09_stark | Blitzpanzer | Krabbeltier, genau 6 Beine | keins |
| 09_boss | Sturmwolke | Schwebekörper mit 2 Armen, keine Beine | keins |
| 10_leicht | Schraubenkrabbler | Krabbeltier, genau 6 Beine | keins |
| 10_mittel | Propellerdrohne | kompakter Schwebekörper mit 2 festen Rotorscheiben | keins |
| 10_stark | Stahlbrecher | Zweibeiner, 2 Arme, 2 Beine | humanoid mit `Walking` und `Attack` |
| 10_boss | Schrottkoloss | Zweibeiner, 2 Arme, 2 Beine | humanoid mit `Walking` und `Attack` |
| 11_leicht | Wolkenflausch | Wolkenkörper ohne Gliedmaßen | keins |
| 11_mittel | Federflügler | Flieger, 2 Flügel, 2 Beine | keins |
| 11_stark | Goldwächter | Zweibeiner, 2 Arme, 2 Beine | humanoid mit `Walking` und `Attack` |
| 11_boss | Himmelswächter | Zweibeiner mit 2 Flügeln, 2 Arme, 2 Beine | humanoid mit `Walking` und `Attack` (Flügel bleiben steif) |
| 12_leicht | Pilzhüpfer | Pilzkörper auf 2 Beinen, keine Arme | keins |
| 12_mittel | Sporenschwirrer | Flieger, 2 Flügel | keins |
| 12_stark | Pilzpanzer | Krabbeltier, genau 6 Beine | keins |
| 12_boss | Riesenpilzmutter | Zweibeiner, 2 Arme, 2 Beine (Arme in der Vorlage gebeugt) | humanoid versuchen; wenn es scheitert, nur das statische Modell |
| 13_leicht | Geisterlein | kompakter Schwebekörper, keine Gliedmaßen | keins |
| 13_mittel | Laternenflatterer | Flieger, 2 Flügel | keins |
| 13_stark | Steinritter | Zweibeiner, 2 Arme, 2 Beine | humanoid mit `Walking` und `Attack` |
| 13_boss | Mondgeist | Schwebekörper mit 2 Armen, keine Beine | keins |
| 14_leicht | Skarabäus-Krabbler | Krabbeltier, genau 6 Beine | keins |
| 14_mittel | Maskenflieger | Flieger, 2 Flügel | keins |
| 14_stark | Steinwächter | Zweibeiner, 2 Arme, 2 Beine | humanoid mit `Walking` und `Attack` |
| 14_boss | Tempelkoloss | Zweibeiner, 2 Arme, 2 Beine | humanoid mit `Walking` und `Attack` |
| 15_leicht | Schattenkugel | kompakter Schwebekörper, keine Gliedmaßen | keins |
| 15_mittel | Leerenflügler | Flieger, 2 Flügel | keins |
| 15_stark | Sternenpanzer | Krabbeltier, genau 6 Beine | keins |
| 15_boss | Schlundwächter | Zweibeiner, 2 Arme, 2 Beine | humanoid mit `Walking` und `Attack` |

Wo „keins“ steht, baut Claude Skelett und Bewegungen selbst; das statische Modell reicht.
Planet 15: Auren, Ringe und Blitze sind NICHT Teil des Modells. Leuchtende Fugen dürfen in der Textur sein.

ERZEUGUNG
- Meshy Bild-zu-3D (T2.5 wie bei Dschungel und Ozean), genau die Vorlage als einziges Bild, kein Zusatztext
- Smart Topology, Ziel 10.000 Polygone, Texturen an, Posekorrektur aus, privat

VOR DEM HOCHLADEN PRÜFEN
- Jedes Modell von vorn, von der Seite, von oben und von unten rendern und zählen.
- Krabbeltiere: genau sechs Beine. Meshy hat schon zweimal acht erzeugt. Draufsicht und Unteransicht sind die
  wichtigste Kontrolle. Acht Beine sind kein Grund für einen neuen Versuch: hochladen und melden, Claude zieht
  überzählige Beine in den Körper zurück (wie beim Krabbenpanzer).
- Zweibeiner: Hände nicht mit dem Körper verschmolzen, Beine getrennt. Nach dem Rigging prüfen, ob die Bewegungen
  sauber laufen (keine abreißenden Teile).
- Flieger: genau zwei Flügel, nicht abgerissen.
- Kleine Netzspitzen oder Fortsätze nur melden, Claude entfernt sie.

ABLAGE in Vorlage_Raw/Monster_Roh/Modelltests_08/ (08 = Planetnummer) mit je Gegner:
- <id>_vorlage.png (die tatsächliche Meshy-Eingabe)
- <id>_statisch_roh.glb (unverändert)
- bei humanoidem Rigging zusätzlich <id>_rig_roh.glb mit den mitgelieferten Bewegungen
- <id>_vorschau_vorn.png, <id>_vorschau_seite.png, <id>_vorschau_oben.png, <id>_vorschau_unten.png
- eine kurze LIESMICH_CLAUDE.md: verbrauchte Credits, Einstellungen, Dreiecke, gezählte Arme/Beine/Flügel,
  Auffälligkeiten; bei einem Fehlversuch einen kurzen Bericht statt des Modells
Als <id> den Namen klein ohne Umlaute nehmen (z. B. kristallwichtel, glitzerfledermaus, quarzkaefer, kristallgolem).
~~~~

## Prompt H1: Vorlagen für elf Champions (drei Ansichten)

**Kosten:** keine · **Abschicken:** jederzeit

~~~~text
Bitte für mein Handyspiel (Tower Defense, Comic-Stil) Bildvorlagen für 3D-Modelle von elf Champions erstellen.
Vorbild ist unser fertiger Champion Dusty Jo: Repository Handy-App-Tower-Defense_-No-Name, Branch
claude/amazing-hypatia-yl59v4, Ordner Vorlage_Raw/Helden_Roh/dusty_jo_comic_v1/ (dusty_jo_vorn.png,
dusty_jo_links.png, dusty_jo_hinten.png). Genau so bitte für jeden der elf Champions.

Aussehen: genau wie die Heldenbilder im Spiel, Ordner game/ui/heroes2d/ (iska.png, brocken.png, volta.png,
kalle.png, margot.png, lynx.png, fritzi.png, fuenkchen.png, pip.png, rollo.png, nova.png). Gleiche Figur, gleiche
Farben, gleiche Frisur und Kleidung, gleicher kindgerechter Comic-Stil mit großem Kopf. Bitte von dort laden.

JE CHAMPION DREI BILDER
- <id>_vorn.png: von vorn
- <id>_links.png: von der linken Seite
- <id>_hinten.png: von hinten (besonders wichtig, so sieht man die Figur im Spiel am häufigsten)

FÜR ALLE MENSCHEN (Iska, Brocken, Volta, Kalle, Margot, Lynx, Fritzi, Nova)
- A-Pose: Arme etwa 40 Grad vom Körper abgespreizt, Ellbogen gestreckt, Beine gerade und hüftbreit
- klare Lücken zwischen Armen und Körper und zwischen den Beinen
- **leere Hände, keine Waffe, kein Gerät in der Hand** (die Waffe wird getrennt gebaut). Hut, Mütze, Gurte und
  Taschen bleiben, aber fest am Körper.
- Haare eng am Kopf, Pferdeschwänze nicht frei abstehend

SONDERFORMEN
- fuenkchen (lila Drache): steht auf vier Beinen, Flügel halb ausgebreitet und klar vom Körper getrennt, Schwanz
  gerade nach hinten, Maul geschlossen
- pip (Roboter): A-Pose wie oben, Hände leer (ohne Schraubenschlüssel), Antenne gerade
- rollo (Panzer): wie im Bild, Kanone nach vorn, Ketten gut sichtbar; keine Pose nötig

FORMAT
- je 1254 × 1254 Pixel, PNG mit durchsichtigem Hintergrund, eine Figur, etwa 10 % Rand
- orthografisch, keine Bodenplatte, kein Schatten, keine Schrift
- alle drei Ansichten einer Figur in gleicher Größe und Höhe, damit sie zusammenpassen

BITTE LIEFERN je Champion in Vorlage_Raw/Helden_Roh/<id>_comic_v1/ (id: iska, brocken, volta, kalle, margot, lynx,
fritzi, fuenkchen, pip, rollo, nova): die drei Bilder und eine kurze LIESMICH_CLAUDE.md. Dazu
Vorlage_Raw/Helden_Roh/UEBERSICHT_VORLAGEN.png mit allen 33 Bildern.

Nur die eingebaute Bildgenerierung im bestehenden Konto verwenden, keine weiteren kostenpflichtigen Dienste.
~~~~

## Prompt H2: Meshy-Modelle Fünkchen, Pip, Rollo, Nova

**Kosten:** etwa 120 Meshy-Credits, freigegeben am 16.11.2026 · **Abschicken:** nachdem H1 geliefert ist

~~~~text
Bitte aus den neuen Vorlagen bei Meshy 3D-Modelle für vier Champions erzeugen, genau wie damals bei Dusty Jo
(Vorlage_Raw/Helden_Roh/dusty_jo_comic_v1/LIESMICH_CLAUDE.md). Repository Handy-App-Tower-Defense_-No-Name, Branch
claude/amazing-hypatia-yl59v4.

KOSTENRAHMEN: vom Nutzer freigegeben, höchstens 4 Erzeugungen zu je etwa 30 Credits (zusammen etwa 120 Credits).
Je Champion ein Versuch; wenn er misslingt, melden statt neu erzeugen. Wenn Rigging oder Bewegungen extra kosten,
vorher melden und nicht ungefragt buchen.

DIE VIER CHAMPIONS (Vorlagen in Vorlage_Raw/Helden_Roh/<id>_comic_v1/)
- fuenkchen: lila Drache auf vier Beinen mit zwei Flügeln · kein Rigging (Claude baut Skelett und Flügelschlag)
- pip: Roboter, A-Pose · humanoides Auto-Rigging versuchen; scheitert es, das Intelligente Rig (Beta) wie bei Dusty Jo
- rollo: Panzer mit Ketten und Kanone · kein Rigging
- nova: Mensch, A-Pose · humanoides Auto-Rigging versuchen; scheitert es, das Intelligente Rig (Beta) wie bei Dusty Jo

ERZEUGUNG
- Meshy 7.1 Bild zu 3D mit Multi-View aus den drei Ansichten (vorn, links, hinten), Standardauflösung,
  Texturen 2K, privat
- danach die kostenlose 10K-Reduktion speichern (Voraussetzung für das Rigging)

VOR DEM HOCHLADEN PRÜFEN
- jedes Modell von vorn, von der Seite, von oben und **von hinten** rendern
- Gliedmaßen zählen: Fünkchen vier Beine und zwei Flügel, Pip und Nova zwei Arme und zwei Beine, Rollo zwei Ketten
- Rückseite muss zur Vorlage passen (keine verschmolzenen oder fehlenden Teile)

ABLAGE in Vorlage_Raw/Helden_Roh/<id>_comic_v1/ je Champion:
- <id>_original_statisch.glb (unverändert), <id>_reduziert_statisch.glb (10K)
- bei Rigging zusätzlich <id>_rig_roh.glb
- <id>_vorschau_vorn.png, _seite.png, _oben.png, _hinten.png
- Ergänzung in LIESMICH_CLAUDE.md: verbrauchte Credits, Einstellungen, Dreiecke, gezählte Gliedmaßen, Rigging-Ergebnis
~~~~

## Prompt H3: Meshy-Modelle Iska, Brocken, Volta, Kalle, Margot, Lynx, Fritzi

**Kosten:** etwa 210 Meshy-Credits, freigegeben am 16.11.2026 · **Abschicken:** nachdem H2 geliefert ist

~~~~text
Bitte aus den Vorlagen bei Meshy 3D-Modelle für die sieben übrigen Champions erzeugen, genau wie bei Dusty Jo
(Vorlage_Raw/Helden_Roh/dusty_jo_comic_v1/LIESMICH_CLAUDE.md) und H2. Repository Handy-App-Tower-Defense_-No-Name,
Branch claude/amazing-hypatia-yl59v4.

KOSTENRAHMEN: vom Nutzer freigegeben, höchstens 7 Erzeugungen zu je etwa 30 Credits (zusammen etwa 210 Credits).
Je Champion ein Versuch; wenn er misslingt, melden statt neu erzeugen. Wenn Rigging oder Bewegungen extra kosten,
vorher melden und nicht ungefragt buchen. Adobe/Mixamo nicht verwenden.

DIE SIEBEN CHAMPIONS (Vorlagen in Vorlage_Raw/Helden_Roh/<id>_comic_v1/, alle Menschen in A-Pose, leere Hände)
- iska: dunkelblaue Jacke mit türkisen Streifen, langer brauner Pferdeschwanz (hinten gut sichtbar)
- brocken: gelbe Mütze, weißes Shirt, braune Latzhose mit Gurten, große Handschuhe, kräftige Statur
- volta: weißer Laborkittel, blonder Haarknoten, türkise Kopfhörer, türkise Hose
- kalle: dunkle Haare, Hosenträger, olivgrüne Hose, Armband
- margot: Piratenhut (Dreispitz) mit rotem Band, blauer Mantel mit Goldrand, blonde Haare
- lynx: rote Haare mit Pferdeschwanz, grüner Schal, olivgrüner Anzug mit Gurten
- fritzi: orange Mütze, braune Weste mit Werkzeuggurt, blaue Hose
Für alle: humanoides Auto-Rigging versuchen; scheitert es, das Intelligente Rig (Beta) wie bei Dusty Jo.
Waffen und gehaltene Geräte NICHT mit erzeugen, die baut Claude als eigene Modelle.

ERZEUGUNG
- Meshy 7.1 Bild zu 3D mit Multi-View aus den drei Ansichten (vorn, links, hinten), Standardauflösung,
  Texturen 2K, privat
- danach die kostenlose 10K-Reduktion speichern (Voraussetzung für das Rigging)

VOR DEM HOCHLADEN PRÜFEN
- jedes Modell von vorn, von der Seite, von oben und **von hinten** rendern
- Gliedmaßen zählen: zwei Arme, zwei Beine, Kopf; Hände frei und nicht mit dem Körper verschmolzen
- Rückseite muss zur Vorlage passen: Pferdeschwänze (Iska, Lynx), Haarknoten (Volta), Hut und Mantel (Margot),
  Latzhose-Gurte (Brocken), Weste (Fritzi) nicht verschmolzen oder fehlend
- Hüte und Mützen sitzen fest auf dem Kopf, keine Löcher oder schwebenden Teile

ABLAGE in Vorlage_Raw/Helden_Roh/<id>_comic_v1/ je Champion:
- <id>_original_statisch.glb (unverändert), <id>_reduziert_statisch.glb (10K)
- <id>_rig_roh.glb (Ergebnis des Riggings)
- <id>_vorschau_vorn.png, _seite.png, _oben.png, _hinten.png
- Ergänzung in LIESMICH_CLAUDE.md: verbrauchte Credits, Einstellungen, Dreiecke, gezählte Gliedmaßen, Rigging-Ergebnis
Dazu Vorlage_Raw/Helden_Roh/UEBERSICHT_MODELLE_H3.png mit den Hinten-Vorschauen aller sieben nebeneinander.
~~~~

## Prompt W1: Vorlagen für acht Champion-Waffen (drei Ansichten)

**Kosten:** keine Kosten · **Abschicken:** sofort · danach W2 (Meshy, etwa 240 Credits, eigene Freigabe)

~~~~text
Bitte für mein Handyspiel (Tower Defense, Comic-Stil, Godot) Vorlagen für acht Waffen der Champions erstellen.
Aus den Vorlagen entstehen danach bei Meshy 3D-Modelle, die die Figuren in der rechten Hand halten.
Repository Handy-App-Tower-Defense_-No-Name, Branch claude/amazing-hypatia-yl59v4.

REFERENZEN (bitte laden)
- Heldenbilder mit der jeweiligen Waffe: game/ui/heroes2d/<id>.png
- Stil und Farben der Figuren: Vorlage_Raw/Helden_Roh/UEBERSICHT_VORLAGEN.png
Die Waffe soll genau so aussehen wie im Heldenbild, nur sauber und vollständig.

DIE ACHT WAFFEN
- dusty: klassischer Western-Revolver, Metalllauf, Holzgriff, Trommel
- iska: kompaktes Sturmgewehr, dunkles Metall, türkiser Handschutz, gebogenes Magazin
- brocken: großer roter Raketenwerfer zum Schultern, dunkle Ringe vorn und hinten, Griff und Vordergriff unten
- volta: Blitzpistole, weißes Gehäuse, türkise Spule mit Metallringen, leuchtende Spitze
- kalle: Eisblaster, hellblaues Gehäuse, weiße Mündung, kleiner Kältetank oben
- margot: doppelläufige Piratenflinte, Holzschaft, Messingband
- lynx: Scharfschützengewehr, olivgrün und dunkel, langes Zielfernrohr mit türkiser Linse, Holzschaft
- fritzi: Flammenwerfer, braunes Gehäuse, Metalldüse mit orangem Ring, roter Brennstofftank unter dem Lauf

ANSICHTEN je Waffe (für Meshy Multi-View)
- <id>_waffe_seite.png: genau von der Seite, Lauf zeigt nach RECHTS, Griff unten gut sichtbar
- <id>_waffe_oben.png: genau von oben, Lauf zeigt nach RECHTS
- <id>_waffe_vorn.png: genau von vorn in die Mündung
- alle drei Ansichten in gleichem Maßstab, orthografisch, keine Perspektive

FORMAT
- je 1254 × 1254 Pixel, PNG mit durchsichtigem Hintergrund, eine Waffe, etwa 10 % Rand
- keine Hände, keine Figur, kein Halter, keine Bodenplatte, kein Schatten, keine Schrift, keine Logos
- Comic-Stil wie die Figuren: klare Formen, kräftige Farben, weiche Schattierung, leicht übertriebene Proportionen
  (dickere Läufe, größere Griffe), damit die Waffe im Spiel auch klein gut erkennbar ist
- Griff deutlich ausgeformt, so dass eine einfache Comic-Hand ihn umfassen kann

BITTE LIEFERN in Vorlage_Raw/Waffen_Roh/<id>_waffe_v1/: die drei Bilder und eine kurze LIESMICH_CLAUDE.md
(Waffe, Länge im Verhältnis zur Figur aus dem Heldenbild, wo genau Griff und Mündung liegen).
Dazu Vorlage_Raw/Waffen_Roh/UEBERSICHT_WAFFEN.png mit allen 24 Bildern.

Nur die eingebaute Bildgenerierung im bestehenden Konto verwenden, keine weiteren kostenpflichtigen Dienste.
~~~~

## Prompt W2: Meshy-Modelle der acht Champion-Waffen

**Kosten:** etwa 240 Meshy-Credits (8 × 30), **erst nach Freigabe durch den Nutzer** · **Abschicken:** nach W1

~~~~text
Bitte aus den freigegebenen Waffenvorlagen bei Meshy 3D-Modelle erzeugen, genau wie bei den Champions (H2/H3).
Repository Handy-App-Tower-Defense_-No-Name, Branch claude/amazing-hypatia-yl59v4.

KOSTENRAHMEN: vom Nutzer freigegeben, höchstens 8 Erzeugungen zu je etwa 30 Credits (zusammen etwa 240 Credits).
Je Waffe ein Versuch; wenn er misslingt, melden statt neu erzeugen. Kein Rigging, keine Bewegungen.

DIE ACHT WAFFEN (Vorlagen in Vorlage_Raw/Waffen_Roh/<id>_waffe_v1/, je seite, oben, vorn)
dusty, iska, brocken, volta, kalle, margot, lynx, fritzi

ERZEUGUNG
- Meshy 7.1 Bild zu 3D mit Multi-View aus den drei Ansichten, Standardauflösung, Texturen 2K, privat
- danach die kostenlose Reduktion auf etwa 3.000 Dreiecke (Waffen sind im Spiel klein); falls nur 10K möglich ist,
  die 10K-Fassung speichern

VOR DEM HOCHLADEN PRÜFEN
- jede Waffe von der Seite, von oben, von vorn und schräg hinten rendern
- Lauf, Griff, Abzugsbügel, Zielfernrohr und Tanks vollständig, nichts verschmolzen oder abgebrochen
- besonders Lynx (dünner Lauf, Zielfernrohr) und Brocken (drei getrennte Mündungen)
- Mündung zeigt in die gleiche Richtung wie in der Seitenansicht (nach rechts)

ABLAGE in Vorlage_Raw/Waffen_Roh/<id>_waffe_v1/ je Waffe:
- <id>_waffe_original.glb (unverändert), <id>_waffe_reduziert.glb
- <id>_waffe_vorschau_seite.png, _oben.png, _vorn.png, _schraeg.png
- Ergänzung in LIESMICH_CLAUDE.md: verbrauchte Credits, Einstellungen, Dreiecke, Prüfergebnis
Dazu Vorlage_Raw/Waffen_Roh/UEBERSICHT_MODELLE_WAFFEN.png mit den Seitenansichten aller acht Modelle.
~~~~

## Prompt H4: Heldenposen mit Waffe in der Hand (Vergleich zu Claudes Fassung)

**Kosten:** keine Meshy-Credits (nur Blender und, falls nötig, kostenloses Neu-Riggen) · **Abschicken:** 17.11.2026

~~~~text
Bitte für mein Handyspiel die acht menschlichen Champions so posieren, dass sie ihre Waffe sauber in der rechten Hand
halten. Repository Handy-App-Tower-Defense_-No-Name, Branch claude/amazing-hypatia-yl59v4. Claude hat eine eigene
Fassung gebaut; wir vergleichen danach beide.

EINGABEN
- Figuren mit Skelett: Vorlage_Raw/Helden_Roh/<id>_comic_v1/<id>_rig_roh.glb
  (Dusty: Vorlage_Raw/Helden_Roh/dusty_jo_comic_v1/dusty_jo_smart_rig_roh.glb)
- Waffen: Vorlage_Raw/Waffen_Roh/<id>_waffe_v1/<id>_waffe_reduziert.glb, Griff/Mündung/Länge in der LIESMICH_CLAUDE.md
- Heldenbilder (Vorbild für die Pose): game/ui/heroes2d/<id>.png
- Claudes Bauskript zum Nachlesen: tools/heroes/build_hero_v2.py
- ids: dusty, iska, brocken, volta, kalle, margot, lynx, fritzi

JE CHAMPION ZWEI POSEN (Blender, als Aktionen am Skelett)
1. „Pose“: Heldenpose für das Menü, wie auf dem Heldenbild. Die Figur steht still (leichtes Atmen erlaubt).
   Sie wird von vorn schräg gezeigt (etwa 15° gedreht).
2. „Shoot“: Anschlag nach vorn für den Kampf, beginnt in der Zielhaltung, kurzer Rückstoß und zurück (0,4 s).
   Die Figur wird im Kampf NUR von hinten oben gesehen: die Waffe muss rechts neben dem Körper sichtbar sein,
   nicht vom großen Kopf verdeckt.
Optional „Idle“ (Waffe gesenkt) und „Victory“ (Waffe erhoben).

WICHTIG FÜR DIE HÄNDE
- Die rechte Hand umschließt den Griff wie eine Faust. Nichts geht durch die Waffe: keine Hand im Griff, kein Arm
  durch Schaft oder Lauf, keine Waffe im Kopf oder Gesicht.
- Bei zweihändigen Waffen (Iska, Brocken, Margot, Lynx, Fritzi) liegt die linke Hand am Vorderschaft oder stützt ihn.
- Finger krümmen, wo das Skelett Fingerknochen hat (Kalle, Lynx). Iska, Volta, Margot, Fritzi haben nur einen
  Handknochen: dort bitte in Meshy kostenlos neu riggen mit der humanoiden Vorlage MIT Fingern (wie bei Pip und
  Nova, Leistenmarkierung von Hand setzen), dann Finger um den Griff krümmen.
- Keine verdrehten Unterarme (kein „Bonbonpapier“-Verdrehen); Drehung zwischen Unterarm und Hand verteilen.
- Volta hält links ein Tablet (dunkler Rahmen, türkiser Bildschirm), Brocken trägt den Werfer auf der Schulter.

TECHNIK (damit es ins Spiel passt)
- Figur 2,0 Einheiten hoch, Füße auf dem Boden, Blick nach -Y in Blender (glTF mit +Y oben exportieren)
- Knochennamen wie Mixamo: mixamorig:Hips, mixamorig:RightHand, mixamorig:LeftHand, mixamorig:Head usw.
- Waffe als eigenes, starres Objekt: rechter Handknochen → Leerobjekt „WeaponSocket“ → „Weapon“ → Leerobjekt
  „Muzzle“ an der Mündung (lokale -Z zeigt in Schussrichtung)
- Texturen höchstens 1024 × 1024, je Figur unter 15.000 Dreiecke
- Export: GLB mit allen Aktionen (export_animation_mode ACTIONS)

LIEFERN in Vorlage_Raw/Helden_Posen_v1/<id>/:
- <id>.glb
- vorschau_pose.png (schräg vorn), vorschau_seite.png, vorschau_kampf.png (von hinten oben wie im Spiel),
  vorschau_hand.png (Nahaufnahme rechte Hand mit Waffe)
- LIESMICH_CLAUDE.md: was geändert wurde, Neu-Rigging ja/nein, Dreiecke
Dazu Vorlage_Raw/Helden_Posen_v1/UEBERSICHT.png mit allen vorschau_pose.png und vorschau_hand.png.
~~~~

## Prompt P2: Champion-Porträts für Fünkchen, Pip, Rollo und Nova

**Kosten:** keine (eingebaute Bildgenerierung) · **Abschicken:** 17.11.2026

~~~~text
Bitte für mein Handyspiel „Station am Wurmloch“ vier weitere Champion-Porträts für den Auflevel-Bildschirm malen,
genau im Stil und Format der acht Porträts, die du schon geliefert hast. Repository Handy-App-Tower-Defense_-No-Name,
Branch claude/amazing-hypatia-yl59v4.

VORBILD (bitte laden)
- Deine acht Porträts: Vorlage_Raw/Champion_Portraets_v1/ (UEBERSICHT_CHAMPIONS.png, ohne_hintergrund/, mit_hintergrund/)
- Deine Bildanweisungen dazu: Vorlage_Raw/Champion_Portraets_v1/BILDANWEISUNGEN.txt (gleiche Grundanweisung verwenden)
- Aussehen der vier Figuren: game/ui/heroes2d/<id>.png und die Vorlagen Vorlage_Raw/Helden_Roh/<id>_comic_v1/<id>_vorn.png

DIE VIER MOTIVE (Vorschläge, gern dramatischer ausarbeiten)
- fuenkchen · Fünkchen, kleiner lila Weltraumdrache mit türkisen Flügeln und goldenem Stern-Medaillon. Steht stolz
  auf den Hinterbeinen, Flügel weit gespreizt, haucht einen kleinen funkelnden Sternenatem (lila-goldene Funken)
  zur Seite. Freches, freundliches Grinsen.
- pip · Pip, kleiner Cyberbot mit Bildschirmgesicht (türkise Augen), oranger Brustplatte und Antenne. Hält in einem
  Greifer einen großen Schraubenschlüssel, mit dem anderen winkt er; ein paar Schrauben schweben verspielt um ihn.
- rollo · Rollo, Mini-Panzer mit orangen Ketten, blauem Turm mit Bildschirmaugen und Stern auf der Front. Leicht
  schräg von vorn, Turm keck zur Seite gedreht, Rohr nach oben gerichtet, kleine Staubwölkchen an den Ketten,
  als würde er gerade anfahren.
- nova · Nova, Exo-Pilotin mit lockigem Haar, lila-weißem Anzug und türkisem Stirnband. Kraftvolle Pose mit einer
  erhobenen Raketenfaust, deren Handgelenk-Düsen leise glühen, die andere Faust geballt vor dem Körper.

GLEICH WIE BEI DEN ACHT
- 1122 × 1402 Pixel, je Motiv zwei Fassungen: ohne Hintergrund (echter Alphakanal) und mit ruhigem Dunkelviolett #221935
- ganze Figur, frontal oder leicht gedreht, Gesicht und Augen sichtbar, etwa 10 % Rand
- kein Text, keine Logos, keine Benutzeroberfläche, kein Schuss, kein Blut, nur eine Figur
- Hände bzw. Greifer fassen sichtbar und plastisch zu, nichts geht durcheinander

BITTE LIEFERN in Vorlage_Raw/Champion_Portraets_v2/:
- ohne_hintergrund/<id>.png und mit_hintergrund/<id>.png (ids: fuenkchen, pip, rollo, nova)
- PORTRAET_LAYOUT.json mit denselben Feldern wie in v1 (datei, name, bildgroesse_px, motivbereich_px,
  maximale_motivhoehe_relativ_zur_anzeigehoehe, abstand_zur_standlinie_relativ_zur_anzeigehoehe, datei_mit_hintergrund)
- UEBERSICHT_CHAMPIONS.png mit allen zwölf Porträts (die acht aus v1 und die vier neuen) und Namen
- LIESMICH_CLAUDE.md und BILDANWEISUNGEN.txt

Nur die eingebaute Bildgenerierung im bestehenden Konto verwenden, keine weiteren kostenpflichtigen Dienste.
~~~~

## Prompt S1b: Voltas Blitz überarbeiten (nach dem Spieltest)

**Kosten:** keine · **Abschicken:** 17.11.2026

~~~~text
Danke für Voltas Schusseffekt (Vorlage_Raw/Schusseffekte_Volta_v1/). Das Format passt genau, Claude hat ihn eingebaut und
im Spiel getestet. Repository Handy-App-Tower-Defense_-No-Name, Branch claude/amazing-hypatia-yl59v4.

BEFUND IM SPIEL (Bild: Vorlage_Raw/Schusseffekte_Volta_Referenz/spieltest_v1.png, links Eisbrücke, rechts Raumdock)
- Blitzbogen: viel zu dünn und blass. Selbst mit 2,1 m statt 0,7 m Höhe ist er auf der hellen Eisbrücke kaum zu
  sehen, auf dem Raumdock nur als feiner Strich. Die Kamera schaut von hinten oben, der Bogen ist im Bild nur
  1–2 Pixel breit.
- Einschlag: zu groß und zu weiß, er deckt den Gegner fast ganz zu.
- Mündungsblitz: passt so.

BITTE ÜBERARBEITEN (gleiches Format, gleiche Dateinamen, neuer Ordner Vorlage_Raw/Schusseffekte_Volta_v2/)
1. volta_blitzbogen (256 × 256 je Bild, 4 × 2, 24 fps, Start links bei x 20, Ziel rechts bei x 236, Mitte y 128)
   - weißer Kern mindestens 6–8 px dick, durchgehend, ohne Lücken
   - kräftiger Leuchtsaum in Türkis bis Blauviolett, etwa 30–40 px nach oben und unten auslaufend
   - Zacken etwas ruhiger (Ausschlag höchstens ±35 px), damit der Bogen dick wirkt und nicht zittert
   - 2–3 kurze Seitenäste mit Funken, aber keine dunklen oder grauen Ränder (die wirken auf hellem Boden wie
     ein Schatten)
   - erste Bilder hell aufblitzend, letzte 2–3 Bilder ausklingend
   - in der JSON: feste_hoehe_m 2.0
2. volta_einschlag (256 × 256 je Bild, 4 × 3, 24 fps)
   - kleiner: groesse_m 1.0 statt 1.48
   - Mitte nur kurz hell (2–3 Bilder), danach durchsichtig, damit der Gegner sichtbar bleibt
   - Funken und kleine Blitzbögen nach außen, Glühen in Türkis statt Weiß
3. volta_muendung: unverändert übernehmen

PRÜFEN VOR DER LIEFERUNG
- die Kampfvorschau auf zwei Brücken zeigen: der hellen Eiswelt (game/fields/ice_world.webp) und dem Raumdock
  (game/fields/space_dock.webp), Kamera von hinten oben wie im Spiel, Bogen über 6–8 m Entfernung
- der Bogen muss auf beiden Brücken auf den ersten Blick zu sehen sein, auch verkleinert auf Handygröße

LIEFERN in Vorlage_Raw/Schusseffekte_Volta_v2/: die drei Ordner mit Sheet-PNG, JSON und Vorschau-GIF, ABLAUF_VOLTA.json,
LIESMICH_CLAUDE.md, UEBERSICHT.png und VOLTA_KAMPF_VORSCHAU_EIS.gif sowie VOLTA_KAMPF_VORSCHAU_RAUMDOCK.gif.

Nur die eingebaute Bildgenerierung und Bildbearbeitung im bestehenden Konto verwenden, keine kostenpflichtigen Dienste.
~~~~

## Prompt S2: Schusseffekte Dusty, Iska, Lynx (gleiches Format wie Volta v2)

**Kosten:** keine · **Abschicken:** 17.11.2026 (abgeschickt, im Spiel seit 0.10.24) · danach S3 Kalle, Margot, Pip und S4 Fünkchen, Rollo, Nova

~~~~text
Voltas Blitz v2 ist im Spiel und freigegeben, danke! Bitte jetzt im gleichen Format und mit den gleichen Prüfvorgaben
die Schusseffekte für drei weitere Champions bauen. Repository Handy-App-Tower-Defense_-No-Name,
Branch claude/amazing-hypatia-yl59v4. Vorbild für Format, JSON und Lieferung: Vorlage_Raw/Schusseffekte_Volta_v2/.

DIE DREI CHAMPIONS (Waffen: Vorlage_Raw/Waffen_Roh/<id>_waffe_v1/, Modelle mit Aktion „Shoot“ und Knoten „Muzzle“:
game/models/heroes_v2/<id>.glb, für Dusty dusty_jo.glb)
- dusty · Revolver: kurzer, warmer Mündungsblitz in Gelb-Orange mit kleiner Rauchwolke, schnelle Kugel als heller
  gelber Leuchtstrich, Einschlag als kleiner Funkenstern
- iska · Energieblaster: türkiser Mündungsblitz, kurze türkise Energiebolzen (schnelles Dauerfeuer, darf nicht
  überladen wirken), kleiner türkiser Einschlag
- lynx · Scharfschützengewehr: kräftiger, kurzer Mündungsblitz mit Rauchring, langer dünner Leuchtstrich in Weiß-Grün
  quer über die Bahn, deutlicher Einschlag mit kleinem Durchschuss-Funken nach hinten

JE CHAMPION DREI TEILE (Namen <id>_muendung, <id>_geschoss, <id>_einschlag)
- Mündung: 128 × 128 je Bild, 4 × 2, Schussrichtung nach RECHTS, Anker am Waffenende
- Geschoss: 256 × 256 je Bild, 4 × 2, als Leuchtstrich von links (Start bei x 20) nach rechts (Ziel bei x 236),
  Mitte y 128; heller Kern mindestens 6 px, Leuchtsaum 25–35 px; JSON mit feste_hoehe_m
- Einschlag: 256 × 256 je Bild, 4 × 3, durchsichtige Mitte, damit der Gegner sichtbar bleibt, groesse_m etwa 0,8–1,0
- 24 fps, einmal abspielen, gerades Alpha, keine dunklen oder grauen Ränder

PRÜFEN VOR DER LIEFERUNG
- Kampfvorschau je Champion auf der hellen Eisbrücke (game/fields/ice_world.webp) und dem Raumdock
  (game/fields/space_dock.webp), Kamera von hinten oben wie im Spiel
- alles muss auch verkleinert auf Handygröße auf den ersten Blick zu sehen sein

LIEFERN in Vorlage_Raw/Schusseffekte_<id>_v1/ je Champion: drei Ordner mit Sheet-PNG, JSON und Vorschau-GIF,
ABLAUF_<ID>.json, LIESMICH_CLAUDE.md, UEBERSICHT.png, Vorschau-GIFs für Eiswelt und Raumdock.

Nur die eingebaute Bildgenerierung und Bildbearbeitung im bestehenden Konto verwenden, keine kostenpflichtigen Dienste.
~~~~

## Prompt S3: Schusseffekte Kalle, Margot, Pip (gleiches Format wie S2)

**Kosten:** keine · **Abschicken:** 18.11.2026 (abgeschickt, im Spiel seit 0.10.25) · danach S4 Fünkchen, Rollo, Nova

~~~~text
Dusty Jo, Iska und Lynx sind im Spiel und freigegeben, danke! Bitte jetzt im gleichen Format die Schusseffekte für
die nächsten drei Champions bauen. Repository Handy-App-Tower-Defense_-No-Name, Branch claude/amazing-hypatia-yl59v4.
Vorbild für Ordner, Dateinamen, JSON und Lieferung: Vorlage_Raw/Schusseffekte_dusty_v2/ (gleiche Struktur).

WAS WIR BEIM EINBAU VON S2 GELERNT HABEN (bitte beachten)
- Im Spiel werden die Schusseffekte VOLL DECKEND gezeichnet (keine Abschwächung). Darum keine großen, weichen
  Dunst- oder Rauchflächen; Rauch nur klein und kompakt. Beim Einschlag bleibt die Mitte frei, damit man den Gegner sieht.
- Fliegende Geschosse: Bild 1–4 sind die volle Flugphase (das Spiel wiederholt sie, solange das Geschoss fliegt),
  Bild 5–8 blenden aus. Bild 1–4 also gleich hell, nur leicht flackernd.
- Die Streifen nicht zu lang ziehen (Iskas Bolzen waren uns zu lang): der helle Kopf des Geschosses etwa 40 % der
  Kachelbreite, die Spur dahinter kurz und schnell auslaufend.
- Größen in Metern stimmen wir im Spiel selbst ab; wichtig ist, dass alles auch verkleinert auf Handygröße auf den
  ersten Blick zu sehen ist (heller Kern mindestens 8 px bei 256 px Kachelhöhe).

DIE DREI CHAMPIONS (Waffen: Vorlage_Raw/Waffen_Roh/<id>_waffe_v1/ beziehungsweise Pips Modell, Modelle mit Aktion
„Shoot“ und Knoten „Muzzle“: game/models/heroes_v2/<id>.glb)
- kalle · Eisblaster (hellblaues Gehäuse, weiße Mündung, kleiner Kältetank): Frost-STRAHL, der vom Blaster bis zum
  Gegner reicht und mit einer Fähigkeit auf Nachbarn überspringt (wie Voltas Blitzbogen, Vorbild
  Vorlage_Raw/Schusseffekte_Volta_v2/). Eisblau-weißer Strahl mit hellem Kern und kleinen Eiskristallen entlang des
  Strahls. Mündung: kurze kalte Frostwolke mit Glitzern. Einschlag: Eisbruch, kleine Splitter fliegen nach außen.
- margot · doppelläufige Piratenflinte (Holzschaft, Messingband): großer, kurzer Mündungsblitz in Orange-Gelb mit
  kleiner, kompakter Pulverrauchwolke. Geschoss: ein Bündel aus drei kleinen glühenden Schrotkugeln mit kurzen
  Spuren (das Spiel schießt mehrere solcher Bündel gleichzeitig im Fächer). Einschlag: kleine Funken.
- pip · kleiner Cyberbot (orange Brustplatte, türkise Augen, schießt aus dem Arm): ein einzelner grüner
  Energiebolzen (nicht zwei wie bei Iska), rund und freundlich, kein Laser. Mündung: kleiner grüner Lichtring.
  Einschlag: grünes Funkeln. Pips Reparaturfunkeln an der Mauer (pip_reparatur) bleibt wie es ist.

JE CHAMPION DREI TEILE (Namen <id>_muendung, <id>_geschoss, <id>_einschlag)
- Mündung: 128 × 128 je Bild, 4 × 2, Schussrichtung nach RECHTS, Anker am Waffenende (links Mitte)
- Geschoss: 256 × 256 je Bild, 4 × 2, Schussrichtung nach RECHTS, Start bei x 20, Spitze/Ziel bei x 236, Mitte y 128;
  JSON mit feste_hoehe_m, ziel_anker und darstellung: kalle „bogen“ (über die ganze Strecke gespannt, wie Voltas
  Blitzbogen), margot „leuchtspur“, pip „bolzen“
- Einschlag: 256 × 256 je Bild, 4 × 3, freie Mitte, positive x-Richtung folgt der Schussrichtung
- 24 fps, einmal abspielen, gerades Alpha, keine dunklen oder grauen Ränder

PRÜFEN VOR DER LIEFERUNG
- Kampfvorschau je Champion auf der hellen Eisbrücke (game/fields/ice_world.webp) und dem Raumdock
  (game/fields/space_dock.webp), Kamera von hinten oben wie im Spiel, Effekte voll deckend
- verkleinert auf Handygröße (390 × 844) muss jeder Schuss sofort zu sehen sein

LIEFERN in Vorlage_Raw/Schusseffekte_<id>_v1/ je Champion: drei Ordner mit Sheet-PNG, JSON und Vorschau-GIF,
ABLAUF_<ID>.json, LIESMICH_CLAUDE.md, UEBERSICHT.png, Vorschau-GIFs für Eiswelt und Raumdock.

Nur die eingebaute Bildgenerierung und Bildbearbeitung im bestehenden Konto verwenden, keine kostenpflichtigen Dienste.
~~~~

## Prompt S4: Schusseffekte Fünkchen, Rollo, Nova (gleiches Format wie S3)

**Kosten:** keine · **Abschicken:** 18.11.2026 (abgeschickt, im Spiel seit 0.10.25 mit Fünkchen v3 und Rollo v2) · danach sind alle Champions außer Brocken und Fritzi
(eigene 3D-Effekte) mit gemalten Schusseffekten ausgestattet

~~~~text
Kalle, Margot und Pip sind im Spiel, danke! Bitte jetzt im gleichen Format wie S3 die Schusseffekte für die letzten
drei Champions bauen. Repository Handy-App-Tower-Defense_-No-Name, Branch claude/amazing-hypatia-yl59v4.
Vorbild für Ordner, Dateinamen, JSON und Lieferung: Vorlage_Raw/Schusseffekte_kalle_v1/ (gleiche Struktur).

Es gelten dieselben Regeln wie bei S3: im Spiel voll deckend (keine großen weichen Dunst- oder Rauchflächen),
fliegende Geschosse Bild 1–4 volle Flugphase und Bild 5–8 ausblenden, Streifen nicht zu lang, alles verkleinert auf
Handygröße auf den ersten Blick sichtbar, beim Einschlag bleibt die Mitte frei.

DIE DREI CHAMPIONS (Modelle mit Aktion „Shoot“ und Knoten „Muzzle“: game/models/heroes_v2/<id>.glb, Porträts:
game/ui/portraits/<id>.webp)
- fuenkchen · kleiner Drache, Sternenatem: ein Band aus kleinen leuchtenden Sternen und warmem Licht, das vom Maul
  quer über die ganze Bahn reicht und alle Gegner in der Reihe durchdringt (darstellung „strahl“, über die ganze
  Strecke gespannt wie Kalles Froststrahl). Mündung: Funkeln am Maul. Einschlag: kleiner Sternregen.
- rollo · kleiner Panzer mit Kanone: schwere, dunkle Kanonenkugel mit kurzer, kompakter Rauchspur (darstellung
  „leuchtspur“, Kugel vorn). Mündung: dicke, aber kompakte Rauchwolke mit kurzem Feuerblitz. Einschlag: Staubring und
  ein paar Brocken, der Gegner wird zurückgestoßen.
- nova · Schwerkraft-Heldin: violette Schwerkraftkugel mit wirbelnden Teilchen (darstellung „bolzen“). Mündung:
  kleiner violetter Wirbel. Einschlag: Sog nach innen, ein violetter Wirbel, der die Gegner zusammenzieht; dieser
  Einschlag darf größer sein (er zeigt das Schwerkraftfeld, etwa 2–3 m), Mitte trotzdem frei.

JE CHAMPION DREI TEILE (Namen <id>_muendung, <id>_geschoss, <id>_einschlag)
- Mündung: 128 × 128 je Bild, 4 × 2, Schussrichtung nach RECHTS, Anker am Waffenende beziehungsweise Maul (links Mitte)
- Geschoss: 256 × 256 je Bild, 4 × 2, Schussrichtung nach RECHTS, Start bei x 20, Spitze/Ziel bei x 236, Mitte y 128;
  JSON mit feste_hoehe_m, ziel_anker und darstellung (siehe oben)
- Einschlag: 256 × 256 je Bild, 4 × 3, freie Mitte, positive x-Richtung folgt der Schussrichtung
- 24 fps, einmal abspielen, gerades Alpha, keine dunklen oder grauen Ränder

PRÜFEN VOR DER LIEFERUNG
- Kampfvorschau je Champion auf der hellen Eisbrücke (game/fields/ice_world.webp) und dem Raumdock
  (game/fields/space_dock.webp), Kamera von hinten oben wie im Spiel, Effekte voll deckend
- verkleinert auf Handygröße (390 × 844) muss jeder Schuss sofort zu sehen sein

LIEFERN in Vorlage_Raw/Schusseffekte_<id>_v1/ je Champion: drei Ordner mit Sheet-PNG, JSON und Vorschau-GIF,
ABLAUF_<ID>.json, LIESMICH_CLAUDE.md, UEBERSICHT.png, Vorschau-GIFs für Eiswelt und Raumdock.

Nur die eingebaute Bildgenerierung und Bildbearbeitung im bestehenden Konto verwenden, keine kostenpflichtigen Dienste.
~~~~

## Prompt R1: Alternative Rakete für Brocken (gemalt, gleiches Format wie S2–S4)

**Kosten:** keine · **Abschicken:** 18.11.2026 · Wunsch des Nutzers: eine Rakete, die zu den Designs der anderen
Waffen passt und nicht so kantig aussieht. Claudes 3D-Rakete (verkleinert) bleibt bis zum Vergleich im Spiel.

~~~~text
Alle Schusseffekte sind im Spiel, danke! Ein Champion fehlt noch: Brocken. Seine Rakete ist bisher ein einfaches
3D-Modell aus Grundformen und wirkt zu kantig. Bitte eine gemalte Rakete im gleichen Format wie die anderen
Schusseffekte bauen, damit sie zu den übrigen Champions passt. Repository Handy-App-Tower-Defense_-No-Name, Branch
claude/amazing-hypatia-yl59v4. Vorbild für Ordner, Dateinamen, JSON und Lieferung: Vorlage_Raw/Schusseffekte_rollo_v2/
(gleiche Struktur).

BROCKEN UND SEINE WAFFE
- brocken: gelbe Mütze, weißes Shirt, braune Latzhose mit Gurten, große Handschuhe, kräftige Statur; Modell mit Aktion
  „Shoot“ und Knoten „Muzzle“: game/models/heroes_v2/brocken.glb, Porträt: game/ui/portraits/brocken.webp
- Waffe: großer roter Schulter-Raketenwerfer mit dunklen Metallringen und drei Mündungen
  (Vorlage_Raw/Waffen_Roh/brocken_waffe_v1/, Ansichten seite/oben/vorn)

DIE RAKETE (bitte zwei Teile, die Explosion bleibt die vorhandene, freigegebene)
- brocken_muendung: kurzer Abschussblitz mit kleiner, kompakter Rauchwolke am Werfer, Schussrichtung nach RECHTS,
  128 × 128 je Bild, 4 × 2, Anker am Werferende (links Mitte)
- brocken_geschoss: eine runde, freundliche Comic-Rakete passend zum Werfer: rotes Gehäuse mit dunklen Ringen, runde
  Spitze, weiche, abgerundete Flossen (nichts Eckiges, kein Raumschiff), kleine helle Flamme am Heck und eine kurze,
  kompakte Rauchspur dahinter. Spitze nach RECHTS. 256 × 256 je Bild, 4 × 2, Start bei x 20, Spitze bei x 236, Mitte
  y 128; JSON mit feste_hoehe_m, ziel_anker und darstellung „rakete“. Bild 1–4 Flugphase (wird wiederholt, Flamme
  und Rauch flackern leicht), Bild 5–8 ausblenden.
- Größe: im Spiel etwa 1,2–1,5 m lang, kleiner als die Gegner. Die Rakete fliegt in einer flachen Bahn (kurz steigen,
  fast gerade, zum Ziel hin absenken); das Spiel dreht sie entlang der Flugbahn.
- 24 fps, gerades Alpha, keine dunklen oder grauen Ränder; im Spiel voll deckend, darum keine großen weichen
  Rauchflächen.

PRÜFEN VOR DER LIEFERUNG
- Kampfvorschau auf der hellen Eisbrücke (game/fields/ice_world.webp) und dem Raumdock (game/fields/space_dock.webp),
  Kamera von hinten oben wie im Spiel, mit der vorhandenen Explosion (game/fx/brocken_explosion.webp) beim Treffer
- verkleinert auf Handygröße (390 × 844) muss die Rakete sofort als Rakete zu erkennen sein

LIEFERN in Vorlage_Raw/Schusseffekte_brocken_v1/: zwei Ordner (brocken_muendung, brocken_geschoss) mit Sheet-PNG, JSON
und Vorschau-GIF, ABLAUF_BROCKEN.json, LIESMICH_CLAUDE.md, UEBERSICHT.png, Vorschau-GIFs für Eiswelt und Raumdock.

Nur die eingebaute Bildgenerierung und Bildbearbeitung im bestehenden Konto verwenden, keine kostenpflichtigen Dienste.
~~~~

## Prompt S5: Fritzis Flammenstrahl (gemalt, gleiches Format wie S2–S4)

**Kosten:** keine · **Abschicken:** 18.11.2026 · Wunsch des Nutzers: Fritzis bisherige Flammen (Partikel-Kugeln)
wirken klobig und verdecken die Gegner; ein gemalter Flammenstrahl soll zu den anderen Champions passen.

~~~~text
Noch ein Champion, dann haben alle gemalte Schusseffekte: Fritzi. Ihre Flammen sind bisher eine dichte Wolke aus
runden orangen Kugeln, die klobig wirkt und die Gegner fast ganz verdeckt. Bitte einen gemalten Flammenstrahl im
gleichen Format wie die anderen Schusseffekte bauen. Repository Handy-App-Tower-Defense_-No-Name, Branch
claude/amazing-hypatia-yl59v4. Vorbild für Ordner, Dateinamen, JSON und Lieferung: Vorlage_Raw/Schusseffekte_kalle_v1/
(gleiche Struktur, Kalles Froststrahl ist ebenfalls ein gespannter Strahl).

FRITZI UND IHRE WAFFE
- fritzi: orange Mütze, braune Weste mit Werkzeuggurt, blaue Hose; Modell mit Aktion „Shoot“ und Knoten „Muzzle“:
  game/models/heroes_v2/fritzi.glb, Porträt: game/ui/portraits/fritzi.webp
- Waffe: Flammenwerfer mit braunem Gehäuse, Metalldüse mit orangem Ring und rotem Brennstofftank unter dem Lauf
  (Vorlage_Raw/Waffen_Roh/fritzi_waffe_v1/, Ansichten seite/oben/vorn)

SO WIRKT FRITZI IM SPIEL
- Jeder Schuss ist ein kurzer Flammenstoß von der Düse zum Ziel. Er trifft alle Gegner in einem Kreis um das Ziel
  (etwa 1,5–3 m, mit der Superfähigkeit gut doppelt so groß) und setzt sie in Brand. Fritzi schießt schnell
  hintereinander, darum darf ein einzelner Stoß nicht überladen wirken.

JE TEIL (Namen fritzi_muendung, fritzi_geschoss, fritzi_einschlag)
- fritzi_muendung: kleine Zündflamme mit kurzem Aufflackern an der Düse, Schussrichtung nach RECHTS,
  128 × 128 je Bild, 4 × 2, Anker an der Düse (links Mitte)
- fritzi_geschoss: echter Flammenstrahl aus Feuerzungen in Gelb, Orange und etwas Rot, an der Düse schmal und hell,
  zum Ziel hin breiter und lebendig züngelnd; KEINE runden Kugeln, keine Rauchwolke. Schussrichtung nach RECHTS,
  256 × 256 je Bild, 4 × 2, Start bei x 20, Ziel bei x 236, Mitte y 128; JSON mit feste_hoehe_m, ziel_anker und
  darstellung „bogen“ (das Spiel spannt den Strahl von der Düse bis zum Ziel). Bild 1–4 voller Stoß (gleich hell, nur
  züngelnd), Bild 5–8 ausblenden.
- fritzi_einschlag: das Feuer breitet sich am Boden um das Ziel aus, ein flacher Flammenkranz mit Feuerzungen, die
  außen hochschlagen; die MITTE bleibt frei, damit man die Gegner darin sieht. Das Spiel skaliert ihn auf den
  Trefferkreis. 256 × 256 je Bild, 4 × 3, Anker in der Mitte, positive x-Richtung folgt der Schussrichtung.
- 24 fps, einmal abspielen, gerades Alpha, keine dunklen oder grauen Ränder

WAS WIR BEI DEN ANDEREN GELERNT HABEN (bitte beachten)
- Im Spiel werden die Schusseffekte voll deckend gezeichnet. Darum keine großen, weichen Dunst- oder Rauchflächen.
- Gegner dürfen nie ganz verdeckt sein: Strahl endet am Ziel, Flammen beim Einschlag liegen außen herum.
- Alles muss auch verkleinert auf Handygröße auf den ersten Blick zu sehen sein (heller Kern mindestens 8 px bei
  256 px Kachelhöhe).

PRÜFEN VOR DER LIEFERUNG
- Kampfvorschau auf der hellen Eisbrücke (game/fields/ice_world.webp) und dem Raumdock (game/fields/space_dock.webp),
  Kamera von hinten oben wie im Spiel, mit zwei Gegnern im Trefferkreis
- verkleinert auf Handygröße (390 × 844) müssen Strahl und Einschlag sofort zu sehen sein und die Gegner sichtbar bleiben

LIEFERN in Vorlage_Raw/Schusseffekte_fritzi_v1/: drei Ordner mit Sheet-PNG, JSON und Vorschau-GIF, ABLAUF_FRITZI.json,
LIESMICH_CLAUDE.md, UEBERSICHT.png, Vorschau-GIFs für Eiswelt und Raumdock.

Nur die eingebaute Bildgenerierung und Bildbearbeitung im bestehenden Konto verwenden, keine kostenpflichtigen Dienste.
~~~~

## Prompt L1: Neues App-Logo auf Basis des Ladebildschirms

**Kosten:** keine · **Abschicken:** 19.11.2026 · Wunsch des Nutzers: das bisherige Logo (`game/icon.svg`, einfacher
Kreis mit Punkten) passt nicht; das neue soll die Grafik des Spiels zeigen, Vorbild ist der neue Ladebildschirm.

~~~~text
Ich brauche ein neues App-Logo (App-Symbol für den Startbildschirm des Handys) für unser Spiel „Station am Wurmloch“.
Das bisherige Logo ist nur ein abstrakter Kreis mit drei Punkten und zeigt nichts von unserer Grafik. Grundlage ist
der neue Ladebildschirm. Repository Handy-App-Tower-Defense_-No-Name, Branch claude/amazing-hypatia-yl59v4.

VORLAGEN
- Ladebildschirm: game/ui/start/ladebildschirm_comic.webp (violettes Wurmloch, pinkes Monster, die Champions vorn,
  Schriftzug „Station am Wurmloch“) – Stil, Farben und Licht bitte genau so
- Champions: game/ui/portraits/<id>.webp (dusty, iska, brocken, volta, kalle, margot, lynx, fritzi, fuenkchen, pip,
  rollo, nova), Dusty Jo (Cowboyhut, rotes Halstuch) ist das Gesicht des Spiels
- bisheriges Logo zum Vergleich: game/icon.svg

WAS DAS LOGO ZEIGEN SOLL
- Eine klare, einfache Szene aus dem Ladebildschirm, die auch winzig auf dem Handy (48 px) sofort lesbar ist:
  großes, leuchtendes violettes Wurmloch als Hintergrund, davor ein Champion groß und freundlich im Comic-Stil
- Bitte DREI Varianten zur Auswahl:
  A) Dusty Jo (Kopf und Schultern, Hut, Halstuch) vor dem Wurmloch
  B) das pinke Monster, das aus dem Wurmloch herausschaut, Dusty Jo vorn klein angeschnitten
  C) drei Champions (Dusty Jo, Brocken, Iska) als Gruppe vor dem Wurmloch
- KEIN Text und keine Buchstaben im Logo (auf dem Handy unlesbar); keine dünnen Linien, keine kleinen Details am Rand
- kräftige Kontraste, damit es auf hellem und dunklem Hintergrundbild auffällt

FORMATE JE VARIANTE (Android, Godot-Export)
- <variante>_1024.png: 1024 × 1024, quadratisch, randlos bis an die Kanten gemalt, OHNE abgerundete Ecken (das Handy
  schneidet selbst rund oder eckig zu), keine Transparenz
- <variante>_vordergrund_432.png: 432 × 432 mit Transparenz, nur das Motiv (Champion/Monster), alles Wichtige
  innerhalb des mittleren Kreises mit 288 px Durchmesser (Android schneidet den Rand je nach Handy ab)
- <variante>_hintergrund_432.png: 432 × 432 ohne Transparenz, nur das Wurmloch mit Sternenhimmel
- <variante>_192.png: 192 × 192, aus dem 1024er verkleinert

PRÜFEN VOR DER LIEFERUNG
- Vorschau jeder Variante auf einem Handy-Startbildschirm in 48, 72 und 96 px, mit runder und mit eckig-abgerundeter
  Maske, je einmal auf hellem und dunklem Hintergrundbild, daneben das bisherige Logo zum Vergleich
- die Variante muss auch in 48 px als „Comic-Held vor violettem Wurmloch“ erkennbar sein

LIEFERN in Vorlage_Raw/App_Logo_v1/: je Variante die vier Dateien (A_, B_, C_), UEBERSICHT.png mit allen Vorschauen,
LIESMICH_CLAUDE.md mit kurzer Beschreibung je Variante.

Nur die eingebaute Bildgenerierung und Bildbearbeitung im bestehenden Konto verwenden, keine kostenpflichtigen Dienste.
~~~~

## Prompt T1: Talent-Symbole für Fünkchen, Pip, Rollo und Nova (gemalt, wie die acht vorhandenen)

**Kosten:** keine Kosten · **Abschicken:** jederzeit; bis zur Lieferung zeigt das Spiel vorläufige Symbole (tools/talent_symbole.js)

~~~~text
Bitte für mein Handyspiel (Tower Defense, Comic-Stil) vier neue Talent-Symbole malen. Sie erscheinen auf der Seite
„Talente“ in grünen Karten (Symbol etwa 44 × 44 Punkte) neben acht vorhandenen Symbolen.

STILVORLAGE: genau wie die vorhandenen Talent-Symbole im Repository Handy-App-Tower-Defense_-No-Name, Branch
claude/amazing-hypatia-yl59v4, Ordner game/ui/upgrades_v2/ (tal_feuerkraft.webp, tal_glueckspilz.webp,
tal_kopfgeld.webp, tal_lernfreude.webp, tal_munitionslager.webp, tal_scharfschuetze.webp; Herkunft
Vorlage_Raw/Talente_v1/). Glänzende Comic-Gegenstände mit kräftigem dunklem Umriss, Glanzlicht oben links, rechts
oben ein kleines helles „+“ wie bei den vorhandenen Symbolen.

DIE VIER TALENTE (Form und Farbe bitte so, damit sie zu den Sechsecken auf „Held aufleveln“ passen)
- tal_funkenherz.png – Funkenherz (Fünkchen): Superfähigkeiten laden schneller. Großer rosa Funkelstern mit vier
  Spitzen, daneben ein kleiner goldener Funke. Rosa #ff9ae0, Gold #ffd34d.
- tal_werkzeugkiste.png – Werkzeugkiste (Pip): Booster laden schneller. Türkiser Schraubenschlüssel, schräg von
  links unten nach rechts oben. Türkis #8fe8e8.
- tal_bollwerk.png – Bollwerk (Rollo): mehr Schild. Orangefarbener Wappenschild mit dunklerem Kreuz aus Metallbändern
  und kleinen Nieten. Orange #ffc070, Rand #d8661a.
- tal_schwerefeld.png – Schwerefeld (Nova): Gegner laufen langsamer. Violette Spirale (Schwerkraftwirbel) mit leichtem
  Leuchten in der Mitte. Violett #d0a8ff.

FORMAT
- je 256 × 256 Pixel, PNG mit durchsichtigem Hintergrund (RGBA), Motiv mittig, etwa 8 % Rand frei
- keine Schrift, keine Zahlen, keine Karte, kein Hintergrund
- muss auch klein (44 Punkte) sofort erkennbar sein: wenige, große Formen
- jedes Symbol ein eigenes Bild, nicht aus einem Sammelbild ausschneiden

ZUSÄTZLICH
- uebersicht.png: die vier neuen Symbole neben den sechs vorhandenen tal_*-Symbolen, auf Grün (#3c8c3c), je 44 und 88 px

BITTE LIEFERN in Vorlage_Raw/Talente_v2/ auf GitHub (Branch claude/amazing-hypatia-yl59v4):
1. die vier PNG-Dateien
2. uebersicht.png
3. LIESMICH_CLAUDE.md: je Datei Motiv und Farben
4. BILDANWEISUNG.txt: die verwendeten Bildprompts

Nur die eingebaute Bildgenerierung im bestehenden Konto verwenden, keine weiteren kostenpflichtigen Dienste.
~~~~
