# Neue Gegner für Level 51–150 – Auftrag für ChatGPT (Stand 09.11.2026)

Hinweis für uns: Dieser Auftrag umfasst **nur Schritt 1, die Bildvorlagen** (eingebaute Bildgenerierung, keine
Zusatzkosten). Aus den Vorlagen werden später bei Meshy 3D-Modelle; das kostet etwa 15 Meshy-Credits je Gegner
und wird erst nach eigener Freigabe beauftragt (siehe unten).

Bilder anhängen:
- `Vorlage_Raw/Gegner_51_150_Referenz/gegner_bisher.png` (unsere acht Gegner, Stil-Vorbild)
- `Vorlage_Raw/Gegner_51_150_Referenz/planeten_uebersicht.png` (alle 15 Planeten)
- `Vorlage_Raw/Planeten_Referenz/kampf_im_spiel.png` (so klein laufen die Gegner im Spiel über die Brücke)

---

Ich entwickle ein Handy-Tower-Defense-Spiel (hochkant, Comic-Stil im Weltraum). Gegner laufen über eine Brücke
auf unsere Station zu. Bisher gibt es acht Gegner (Bild `gegner_bisher.png`). Für Level 51–150 gibt es zehn neue
Planeten (Bild `planeten_uebersicht.png`, Nummer 06 bis 15). **Für jeden neuen Planeten brauche ich vier eigene
Gegner**, passend zum Planeten: leicht, mittel, stark und einen Boss. Zusammen 40 Gegner.

## Stil (wie `gegner_bisher.png`)

- Freundliche, leicht freche Comic-Gegner mit großen Augen und klarer Mimik, weiche glänzende 3D-Comic-Optik,
  kräftige Farben. Kein Blut, keine Wunden, nichts Gruseliges (für Kinder ab 6 geeignet).
- Einfacher Detailgrad wie bei den bisherigen Gegnern, große klare Formen.
- **Im Spiel sind die Gegner nur 30–60 Punkte groß.** Jeder braucht deshalb einen eindeutigen Umriss und eine
  Hauptfarbe, die sich von der Fahrbahn seines Planeten (mitteldunkles Grau oder Braun) klar abhebt.
- Die vier Gegner eines Planeten gehören sichtbar zusammen (gemeinsames Thema und Farben), sind aber in Größe und
  Form deutlich verschieden: leicht = klein und flink, mittel = mittelgroß, stark = breit und gepanzert,
  Boss = sehr groß und eindrucksvoll.
- Nichts von anderen Spielen, Filmen oder bekannten Figuren nachmachen.

## Die zehn Planeten mit Vorschlägen

Die Vorschläge sind Anregungen; eigene bessere Ideen im selben Thema sind willkommen.

| Nr. | Planet | leicht | mittel | stark | Boss |
|---|---|---|---|---|---|
| 06 | Dschungelmond | Rankling (hüpfendes Pflanzenknäuel) | Blütenschnapper (fliegende Blüte, Blätter als Flügel) | Borkenkäfer (Panzer aus Baumrinde) | Urwaldriese (wandelnder Baum) |
| 07 | Ozeanwelt | Blubberfisch (hüpfender Kugelfisch) | Quallenflieger (schwebende Qualle mit kurzen, dicken Armen) | Krabbenpanzer | Tiefseekrake (große Krake mit kurzen, dicken Armen) |
| 08 | Kristallplanet | Kristallwichtel | Glitzerfledermaus | Quarzkäfer | Kristallgolem |
| 09 | Sturmriese | Funkenball | Donnervogel | Blitzpanzer | Sturmwolke mit Gesicht und dicken Wolkenarmen |
| 10 | Schrottwelt | Schraubenkrabbler (Mini-Roboter) | Propellerdrohne | Stahlbrecher (Roboter) | Schrottkoloss (großer Roboter) |
| 11 | Wolkenstadt | Wolkenflausch | Federflügler | Goldwächter (in Rüstung) | Himmelswächter |
| 12 | Sporenwelt | Pilzhüpfer | Sporenschwirrer | Pilzpanzer | Riesenpilzmutter |
| 13 | Geistermond | Geisterlein (freundlich) | Laternenflatterer | Steinritter | Mondgeist |
| 14 | Tempelplanet | Skarabäus-Krabbler | Maskenflieger | Steinwächter | Tempelkoloss |
| 15 | Schwarzes Loch | Schattenkugel | Leerenflügler | Sternenpanzer | Schlundwächter (Endboss des Spiels) |

## Damit daraus gute 3D-Modelle werden (wichtig)

Jede Einzelvorlage wird später als **einziges Bild** in einen 3D-Generator gegeben. Sie muss den Körper deshalb
eindeutig zeigen:
- Eine einzelne freigestellte Figur, transparenter Hintergrund, 1024 × 1024 Pixel, etwa 10 % Rand.
- Frontal, gerade von vorn, keine Bodenplatte, kein Schatten, kein Text, keine zweite Ansicht.
- **Zweibeiner:** A-Pose, Arme etwa 40 Grad abgespreizt, Ellbogen gestreckt, Beine gerade und hüftbreit, klare
  Lücken zwischen Armen und Körper und zwischen den Beinen. Genau zwei Arme und zwei Beine, einfache Hände mit
  abgesetztem Daumen. Keine Waffe in der Hand, keine losen Teile.
- **Vierbeiner, Krabbeltiere, Flieger, Klumpen:** leichte Dreiviertel-Ansicht von vorn ist erlaubt, wenn die Form
  so besser erkennbar ist. Anzahl der Beine, Flügel und Arme klar zählbar.
- Keine dünnen Fäden, Ranken, Haare oder Tropfen, die frei in der Luft hängen; keine durchsichtigen Teile.
  Fangarme, Ranken und Wolkenarme kurz und dick.

## Liefern

Ordner `Vorlage_Raw/Gegner_51_150_v1/` auf GitHub (Repository `Handy-App-Tower-Defense_-No-Name`, Branch
`claude/amazing-hypatia-yl59v4`):
1. je Planet eine Übersicht `planet_06_uebersicht.png` … `planet_15_uebersicht.png`: die vier Gegner
   nebeneinander auf dunkelviolettem Grund (#2a1f63), mit Namen und Stärke darunter (wie `gegner_bisher.png`)
2. je Gegner eine Einzelvorlage `<planet>_<stärke>.png`, zum Beispiel `06_leicht.png`, `06_boss.png`
   (Stärke: leicht, mittel, stark, boss)
3. `alle_gegner.png`: alle 40 klein in einer Übersicht, zur Kontrolle
4. `LIESMICH_CLAUDE.md`: je Gegner Name, Planet, Stärke, Körperbau (Zweibeiner, Vierbeiner, Flieger, Klumpen …)
5. `BILDANWEISUNGEN.json`: die verwendeten Bildprompts

**Ablauf:** Bitte zuerst nur Planet 06 (Dschungelmond) liefern und auf Rückmeldung warten. Danach die übrigen neun.

Nur die eingebaute Bildgenerierung im bestehenden Konto verwenden, keine weiteren kostenpflichtigen Dienste.
Nichts bei Meshy oder anderen Diensten erzeugen.

---

## Schritt 2 (später, nur nach Freigabe der Kosten)

Aus den freigegebenen Vorlagen entstehen 3D-Modelle bei Meshy (wie bei den bisherigen acht Gegnern, siehe
`Vorlage_Raw/Monster_Roh/NAECHSTE_MONSTER_FUER_CHATGPT.md`). Kosten etwa 15 Meshy-Credits je Gegner:
alle 40 Gegner etwa 600 Credits, nur die 10 Bosse etwa 150 Credits. Bis dahin nutzt das Spiel weiter die
eingefärbten bisherigen Gegner.
