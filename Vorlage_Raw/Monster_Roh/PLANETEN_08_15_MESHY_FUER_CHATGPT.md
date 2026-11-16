# Planeten 08–15: 3D-Modelle der 32 Gegner – Auftrag für ChatGPT (Stand 16.11.2026)

**Reihenfolge:** Auftrag 5 von 5 (Übersicht in `Vorlage_Raw/AUFTRAEGE_REIHENFOLGE.md`).

**Kosten: je Gegner eine Erzeugung zu etwa 15 Meshy-Credits, je Planet etwa 60 Credits, alle acht Planeten
zusammen etwa 480 Credits (bezahltes Konto).** Wie bei Dschungel und Ozean: **Planet für Planet**, jeder Planet
braucht eine eigene Freigabe des Nutzers. Den Text unten erst abschicken, wenn in der Tabelle „Freigabe“
ein Datum steht, und nur für diese Planeten.

| Nr. | Planet | Level | Gegner (leicht · mittel · stark · Boss) | Freigabe |
|---|---|---|---|---|
| 08 | Kristallplanet | 71–80 | Kristallwichtel · Glitzerfledermaus · Quarzkäfer · Kristallgolem | offen |
| 09 | Sturmriese | 81–90 | Funkenball · Donnervogel · Blitzpanzer · Sturmwolke | offen |
| 10 | Schrottwelt | 91–100 | Schraubenkrabbler · Propellerdrohne · Stahlbrecher · Schrottkoloss | offen |
| 11 | Wolkenstadt | 101–110 | Wolkenflausch · Federflügler · Goldwächter · Himmelswächter | offen |
| 12 | Sporenwelt | 111–120 | Pilzhüpfer · Sporenschwirrer · Pilzpanzer · Riesenpilzmutter | offen |
| 13 | Geistermond | 121–130 | Geisterlein · Laternenflatterer · Steinritter · Mondgeist | offen |
| 14 | Tempelplanet | 131–140 | Skarabäus-Krabbler · Maskenflieger · Steinwächter · Tempelkoloss | offen |
| 15 | Schwarzes Loch | 141–150 | Schattenkugel · Leerenflügler · Sternenpanzer · Schlundwächter | offen |

Bis dahin laufen dort eingefärbte Gegner der ersten Welten. Bisherige Ergebnisse: Dschungel (`Modelltests_v4`),
Ozean (`Modelltests_v6`). Bei Sechsbeinern hat Meshy zweimal acht Beine erzeugt (Borkenkäfer, Krabbenpanzer).

---

## Text für ChatGPT (je freigegebenem Planet einmal, `NN` = Planetnummer)

Bitte aus den vier freigegebenen Bildvorlagen von Planet NN bei Meshy je ein 3D-Modell erzeugen, für mein
Handyspiel (Tower Defense, Comic-Stil). Die Vorlagen liegen auf GitHub (Repository Handy-App-Tower-Defense_-No-Name,
Branch claude/amazing-hypatia-yl59v4) unter Vorlage_Raw/Gegner_51_150_v1/Einzelvorlagen/NN_leicht.png,
NN_mittel.png, NN_stark.png, NN_boss.png.
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

ABLAGE in Vorlage_Raw/Monster_Roh/Modelltests_NN/ (NN = Planetnummer) mit je Gegner:
- <id>_vorlage.png (die tatsächliche Meshy-Eingabe)
- <id>_statisch_roh.glb (unverändert)
- bei humanoidem Rigging zusätzlich <id>_rig_roh.glb mit den mitgelieferten Bewegungen
- <id>_vorschau_vorn.png, <id>_vorschau_seite.png, <id>_vorschau_oben.png, <id>_vorschau_unten.png
- eine kurze LIESMICH_CLAUDE.md: verbrauchte Credits, Einstellungen, Dreiecke, gezählte Arme/Beine/Flügel,
  Auffälligkeiten; bei einem Fehlversuch einen kurzen Bericht statt des Modells
Als <id> den Namen klein ohne Umlaute nehmen (z. B. kristallwichtel, glitzerfledermaus, quarzkaefer, kristallgolem).

## Danach (Claude)

Claude baut Skelette und Bewegungen, schickt dem Nutzer ein Prüfbild auf der Brücke des Planeten und schaltet die
Gegner erst nach Freigabe ein (wie bei Dschungel und Ozean).
