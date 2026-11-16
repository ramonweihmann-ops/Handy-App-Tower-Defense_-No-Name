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
