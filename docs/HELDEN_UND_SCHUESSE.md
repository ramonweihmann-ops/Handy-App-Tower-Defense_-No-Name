# Champions im Kampf und Schussanimationen – Konzept (16.11.2026)

Rückmeldung des Nutzers beim Spielen: Viele Champions sehen von hinten noch „komisch“ aus, und nur die
Schussanimation von Dusty Jo gefällt. Die übrigen wirken wie Striche, Brockens Raketen sind durchsichtig.

## 1. Champions von hinten

### Befund

| Champion | Modell im Kampf heute | Zustand |
|---|---|---|
| Dusty Jo | eigenes Comic-Modell (Meshy, `models/heroes_v2/dusty_jo.glb`) | gut, passt zum Bild |
| Iska, Brocken, Volta, Kalle, Käpt'n Margot, Lynx, Fritzi | Standardfiguren aus einem kostenlosen Paket (Quaternius, `models/heroes/`), nur eingefärbt | passen nicht zum Comic-Bild |
| Fünkchen, Pip, Rollo, Nova | **gar kein Modell**, das Spiel baut eine einfache Klötzchenform | sehen am schlechtesten aus |

Ursache: Dusty Jo war der Pilot. Die übrigen elf Champions wurden nie als Comic-Modell gebaut. Das Spiel lädt alles
richtig, es gibt nur noch keine passenden Modelle.

### Weg (wie bei Dusty Jo)

1. **Vorlagen (ChatGPT, kostenlos):** je Champion drei Ansichten im Comic-Stil der Heldenbilder
   (`game/ui/heroes2d/`): von vorn, links und **hinten**, A-Pose, leere Hände. Die Waffe baut Claude getrennt, damit
   sie beim Bewegen fest in der Hand sitzt.
2. **Modell (Meshy, kostet):** Bild zu 3D aus den drei Ansichten, wie bei Dusty Jo (Meshy 7.1, Multi-View,
   angezeigt **30 Credits je Champion**). Elf Champions zusammen etwa **330 Credits**. Freigabe gruppenweise.
3. **Skelett, Waffe und Bewegungen (Claude, kostenlos):** wie bei Dusty Jo mit `tools/heroes/build_dusty_jo.py`:
   Idle, Shoot, Victory, Waffe mit Mündungspunkt. Fünkchen (Drache), Pip (Roboter) und Rollo (Panzer) bekommen
   eigene einfache Bewegungen (Flügelschlag, Schweben, Kettenrollen).
4. **Prüfbild** im Kampf von hinten, dann Freigabe je Champion.

Vorgeschlagene Reihenfolge: zuerst die vier ohne Modell (Fünkchen, Pip, Rollo, Nova), dann die Start-Champions
(Iska, Brocken, Kalle, Fritzi), dann Volta, Käpt'n Margot, Lynx.

## 2. Schussanimationen

### Befund

- Alle Champions außer Dusty Jo schießen mit **flachen Bildfolgen** von ChatGPT (`game/fx/<name>_geschoss.webp`). Im
  schrägen Kamerablick wirken sie wie Striche. Brockens Rakete ist zusätzlich halb durchsichtig gezeichnet
  (Deckkraft 0,9 im Bild und im Spiel).
- Dusty Jo wirkt gut, weil der Schuss **räumlich** gebaut ist: Mündungsfeuer am echten Mündungspunkt der Waffe, eine
  leuchtende Kugel mit Leuchtspur in 3D, kurzer Rückstoß in der Bewegung.

### Weg: echte 3D-Geschosse und Partikel statt flacher Bilder

Grundsatz: **Was fliegt, ist ein kleines 3D-Objekt** (Kugel, Rakete, Eissplitter, Kanonenkugel). **Was leuchtet, raucht
oder brennt, sind Partikel** in Godot. Die Bildfolgen von ChatGPT bleiben nur für Einschläge und Explosionen, wo sie
gut aussehen. Die kleinen Geschosse baut Claude selbst in Blender (kostenlos). Meshy lohnt sich dafür nicht: Die
Formen sind einfach, und Meshy liefert zu viele Dreiecke.

| Champion | Geschoss | Mündung | Spur | Einschlag |
|---|---|---|---|---|
| Dusty Jo | bleibt wie jetzt (Vorbild) | | | |
| Iska | kurze, helle Leuchtspur-Kugeln in schneller Folge (wie Dusty, schmaler) | Mündungsfeuer im Wechsel, Hülsen fliegen seitlich | kurze Leuchtspur | Funken |
| Brocken | **massive 3D-Rakete** (rot-grau, deckend), dreht sich leicht | Rückstoß-Rauch nach hinten | Feuerstrahl am Heck und Rauchfahne | große Explosion (Bildfolge, freigegeben) |
| Volta | **Blitz als gezackter Leuchtstrahl**, flackert, springt von Gegner zu Gegner | Funkenring am Gerät | Nachglühen | Funkenregen |
| Kalle | **Eissplitter** (3D-Kristall) | Frostwolke | Schneeflocken-Partikel | Eisbruch, Splitter fliegen |
| Käpt'n Margot | 5–7 kleine glühende Schrotkugeln im Fächer | großes Mündungsfeuer mit Rauchwolke | kurze Spuren | kleine Funken |
| Lynx | sehr schnelle, dicke Leuchtspur; kurz vorher ein dünner Ziellaser | heller Blitz | lange Spur | heller Treffer mit Ring |
| Fritzi | **echte Flammen als Partikel** im Kegel (kein Bild) | Zündflamme | | Glut am Gegner |
| Fünkchen | Sternenatem: Band aus kleinen leuchtenden Sternen | Funkeln am Maul | Sternenstaub | Sternregen |
| Pip | grüne Energiebolzen | kleiner Lichtring | | grünes Reparaturfunkeln an der Mauer |
| Rollo | **3D-Kanonenkugel** im Bogen | dicke Rauchwolke | Rauchspur | Staubring und Rückstoß |
| Nova | violette Schwerkraftkugel mit wirbelnden Teilchen | Wirbel | | Sog nach innen |

Andere KI-Werkzeuge: Video-KIs (Runway, Pika und ähnliche) erzeugen Filme, keine Effekte, die sich im Spiel frei
drehen und wiederholen lassen. Für Spieleffekte gibt es Programme wie EmberGen, sie kosten Lizenzgebühren und
liefern am Ende wieder Bildfolgen. Darum ist der Weg oben besser: Er kostet nichts und sieht aus jedem Blickwinkel
räumlich aus.

### Ablauf

1. Claude baut zuerst **Brocken** (Rakete), **Volta** (Blitz) und **Fritzi** (Flammen) neu, weil sie am meisten stören.
2. Ein **Effekt-Labor** im Spiel spielt alle Schüsse nebeneinander ab; der Nutzer bekommt ein kurzes Video (GIF) je
   Champion zur Ansicht.
3. Freigabe je Champion, dann die übrigen.
4. Einstellung „Effekte: bisher / neu“ bleibt, bis alle freigegeben sind.

## Stand 17.11.2026: alle zwölf Champions mit neuem Modell

Alle Champions nutzen die neuen Comic-Modelle (`game/models/heroes_v2/`, Bauskripte in `tools/heroes/`), seit
0.10.13 ohne Schalter für alle sichtbar. Die Waffen der sieben Menschen sind Platzhalter aus Grundformen, bis die
Meshy-Waffen aus Auftrag W2 da sind (Vorlagen: `Vorlage_Raw/Waffen_Roh/`).

**Regel des Nutzers (17.11.2026):** Solange er der einzige Tester ist, wird alles Neue sofort für alle sichtbar
eingebaut, ohne Entwicklermodus oder Prüfschalter. Die Testkarte steht immer unter Spielmodi.

## Stand 18.11.2026: gemalte Schusseffekte von ChatGPT (v2)

Seit 0.10.23 (Volta) und 0.10.24 (Dusty Jo, Iska, Lynx) kommen Mündungsblitz, Geschoss und Einschlag dieser
Champions als Bildfolgen von ChatGPT (`Vorlage_Raw/Schusseffekte_<held>_v2/`). Übernahme mit
`tools/effekte/import_schuss_v2.py game/fx <held> …`; das Werkzeug dreht die Bilder (Schussrichtung im Bild nach
rechts → im Spiel nach oben) und trägt die **im Spiel abgestimmten Größen** ein (Tabelle TUNING im Werkzeug).
ChatGPTs eigene Größen passen zu seiner Vorschau, nicht zu unserer Kamera.

| Darstellung (JSON) | Wirkung im Spiel | Champion |
|---|---|---|
| `leuchtspur` | Streifen fliegt mit der Kugel, Spitze vorn, wiederholt nur die hellen Bilder (`schleife_bilder`) | Dusty Jo |
| `bolzen` | wie Leuchtspur, kürzer (Wunsch 18.11.: Iskas Bolzen nicht zu lang gezogen) | Iska |
| `durchschuss` | Linie von der Mündung bis zum Ziel, endet auf dem Bildschirm genau dort (`FxSprite.span`) | Lynx |
| Blitzbogen | ein Bogen je Sprung der Kette (battle.gd) | Volta |

- Fliegende Geschosse werden nicht in die Tiefe verkürzt, sonst sind sie bei der flachen Kamera nur Punkte.
- **Voll deckend (Entscheidung 18.11.2026):** Gemalte Schusseffekte (`v2` oder `deckend` in der JSON) werden nicht
  mehr auf 80 % gedämpft. Das sieht kräftiger aus; die Explosionen bleiben dafür bewusst klein. Alle übrigen
  Effekte (Explosionen, Fähigkeiten, Strahlen) behalten die Dämpfung (`FxSprite.ALPHA`).
- Abnahme: Aufnahme im Spiel mit fester Bildrate (`--fixed-fps 20`, sonst ruckelt der Film bei langsamem Rechner)
  und `--shot-show=<ordner>`, je Champion Eiswelt (Level 12) und Raumdock (Level 3), dem Nutzer nebeneinander zeigen.
- Offen: S3 (Kalle, Margot, Pip) und S4 (Fünkchen, Rollo, Nova). Brocken und Fritzi behalten ihre 3D-Effekte.
