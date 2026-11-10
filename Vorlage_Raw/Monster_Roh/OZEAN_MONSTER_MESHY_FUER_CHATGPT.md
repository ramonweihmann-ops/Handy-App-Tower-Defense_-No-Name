# Ozeanwelt: 3D-Modelle der vier Gegner – Auftrag für ChatGPT (Stand 10.11.2026)

**Kosten: 4 Erzeugungen zu je etwa 15 Meshy-Credits, zusammen etwa 60 Credits (bezahltes Konto).
Vom Nutzer am 10.11.2026 freigegeben (Variante a: Planet für Planet, zuerst die Ozeanwelt).**
Rigging und mitgelieferte Bewegungen haben beim Dschungelmond nichts extra gekostet; falls doch, vorher fragen.

Vorlagen: `Vorlage_Raw/Gegner_51_150_v1/Einzelvorlagen/07_leicht.png`, `07_mittel.png`, `07_stark.png`,
`07_boss.png`. Vorgehen wie beim Dschungelmond (`DSCHUNGEL_MONSTER_MESHY_FUER_CHATGPT.md`, Ergebnis `Modelltests_v4`).

---

Bitte aus diesen vier freigegebenen Bildvorlagen bei Meshy je ein 3D-Modell erzeugen, für mein Handyspiel
(Tower Defense, Comic-Stil). Die Vorlagen liegen auf GitHub (Repository Handy-App-Tower-Defense_-No-Name, Branch
claude/amazing-hypatia-yl59v4) unter Vorlage_Raw/Gegner_51_150_v1/Einzelvorlagen/.

KOSTENRAHMEN: höchstens 4 Erzeugungen, etwa 60 Meshy-Credits, vom Nutzer freigegeben. Wenn Rigging oder
Bewegungen extra kosten, vorher melden und nicht ungefragt buchen. Je Gegner nur ein Versuch; wenn er misslingt,
melden statt neu erzeugen.

DIE VIER GEGNER
- blubberfisch (07_leicht.png): Blubberfisch · leicht · runder Fischkörper mit Flossen, keine Arme, keine Beine · kein Rigging
- quallenflieger (07_mittel.png): Quallenflieger · mittel · schwebende Qualle mit genau VIER kurzen, dicken Fangarmen · kein Rigging
- krabbenpanzer (07_stark.png): Krabbenpanzer · stark · Krabbe mit genau SECHS Laufbeinen (drei je Seite) plus ZWEI Scherenarmen · kein Rigging
- tiefseekrake (07_boss.png): Tiefseekrake · Boss · Krake mit genau ACHT Fangarmen · kein Rigging
Alle vier ohne Rigging: Skelett und Bewegungen baut Claude selbst. Das statische Modell reicht.

ERZEUGUNG
- Meshy Bild-zu-3D (T2.5 wie beim Dschungelmond), genau die Vorlage als einziges Bild, kein Zusatztext
- Smart Topology, Ziel 10.000 Polygone, Texturen an, Posekorrektur aus, privat

VOR DEM HOCHLADEN PRÜFEN
- Jedes Modell von vorn, von der Seite, von oben und von unten rendern und zählen.
- Krabbenpanzer: genau sechs Laufbeine plus zwei Scheren. Beim Borkenkäfer und beim ersten Panzerkäfer hat Meshy
  acht Beine erzeugt; Draufsicht und Unteransicht sind hier die wichtigste Kontrolle.
- Quallenflieger: genau vier Fangarme. Tiefseekrake: genau acht Fangarme, nicht miteinander verschmolzen.
- Blubberfisch: geschlossener Körper, Flossen nicht abgerissen.
- Nur hochladen, wenn es zur Vorlage passt. Kleine Netzspitzen oder Fortsätze nur melden, Claude entfernt sie.

ABLAGE in Vorlage_Raw/Monster_Roh/Modelltests_v6/ mit je Gegner:
- <id>_vorlage.png (die tatsächliche Meshy-Eingabe)
- <id>_statisch_roh.glb (unverändert)
- <id>_vorschau_vorn.png, <id>_vorschau_seite.png, <id>_vorschau_oben.png, <id>_vorschau_unten.png
- eine kurze LIESMICH_CLAUDE.md: verbrauchte Credits, Einstellungen, Dreiecke, gezählte Beine/Fangarme/Scheren,
  Auffälligkeiten; bei einem Fehlversuch wie beim Borkenkäfer einen kurzen Fehlversuchsbericht statt des Modells

## Danach (Claude)

Claude baut Skelett und Bewegungen (Fisch hüpft bzw. schwimmt, Qualle schwebt und pulsiert, Krabbe läuft seitlich
mit Scherenangriff, Krake schwebt mit wogenden Fangarmen), schickt dem Nutzer ein Prüfbild auf der Brücke der
Ozeanwelt und schaltet die Gegner erst nach Freigabe für Level 61–70 ein.
