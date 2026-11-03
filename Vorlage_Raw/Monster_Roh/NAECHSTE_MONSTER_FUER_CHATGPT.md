# Die fünf restlichen Monster: Auftrag für ChatGPT (Stand 03.11.2026)

Zombie, Tentakler und Panzerkäfer laufen im Spiel (freigegeben). Es fehlen noch die fünf übrigen Gegner der
Welten 1 und 2. Ab Welt 3 färbt das Spiel dieselben Figuren je Welt ein; dafür braucht es keine eigenen Modelle.

**Kosten: 5 Erzeugungen zu je etwa 15 Meshy-Credits, zusammen etwa 75 Credits (bezahltes Konto).
Vom Nutzer am 03.11.2026 freigegeben (75 Credits).** Wenn Rigging oder Bewegungen bei Meshy extra
kosten, das vorher sagen und nicht ungefragt buchen.

## Die fünf Monster

Vorlage ist jeweils die vom Nutzer bestätigte Comic-Monsterübersicht (dieselbe wie bei Zombie, Tentakler und
Panzerkäfer). Gleicher Stil, gleicher einfacher Detailgrad, freundliche Comic-Gegner, kein Blut, keine Wunden.

| Monster | Welt · Stärke | Körperbau | Meshy-Rigging | Was ich (Claude) danach mache |
|---|---|---|---|---|
| Schleimling | 1 · leicht | Schleimklumpen ohne Arme und Beine | **nicht nötig** | eigenes kleines Skelett, Hüpfen (`Walk`) und Zuschnappen (`Attack`) |
| Schleimmutter | 1 · Boss | großer Schleimklumpen, wie Schleimling, aber deutlich anders als er (Größe, Form, Merkmale aus der Übersicht) | **nicht nötig** | wie Schleimling, schwerfälliger |
| Krabbler | 2 · leicht | kleiner Zweibeiner | humanoides Rigging mit `Walking`/`Running` und `Attack` wie beim Zombie | Bewegungen säubern, kürzen, einbauen |
| Brecher | 2 · stark | kräftiger, breiter Zweibeiner | humanoides Rigging mit `Walking` und `Attack` | wie Krabbler |
| Zombie-Koloss | 2 · Boss | sehr großer Zweibeiner, lange Arme | humanoides Rigging mit `Walking` und `Attack` | wie Krabbler; wenn das Rigging an den langen Armen scheitert, rigge ich selbst |

## Bildvorlagen (je Monster eine)

- Eine einzelne freigestellte Figur, transparenter Hintergrund, quadratisch etwa 1024 × 1024, zehn Prozent Rand.
- Frontal, orthografisch, keine Bodenplatte, kein Schatten, kein Text, keine zweite Ansicht.
- **Zweibeiner:** A-Pose, Arme etwa 40 Grad abgespreizt, Ellbogen gestreckt, Beine gerade und hüftbreit,
  klare Lücken zwischen Armen und Körper und zwischen den Beinen. Genau zwei Arme, zwei Beine, einfache Hände
  mit abgesetztem Daumen. Keine Waffe in der Hand (die Waffe des Brechers, falls er eine hat, bitte weglassen
  oder fest am Körper; lose Teile verformen sich beim Rigging falsch).
- **Schleime:** leichte Dreiviertel-Ansicht von vorn ist in Ordnung, wenn die Form so besser erkennbar ist;
  Augen und Mund klar abgesetzt, keine dünnen Fäden oder Tropfen, die frei in der Luft hängen.
- Erfahrung aus dem Panzerkäfer: Meshy T2.5 nimmt nur **ein** Bild und keinen Zusatztext. Deshalb muss die eine
  Vorlage die Anatomie eindeutig zeigen (Anzahl der Gliedmaßen, Lücken).

## Erzeugung

- Meshy T2.5, Smart Topology, Ziel 10.000 Polygone, Texturen an, Posekorrektur aus, privat
  (wie bei den ersten drei Monstern). Ich verkleinere danach selbst auf das Handy-Maß
  (leicht ≤ 3.000, stark ≤ 7.000, Boss ≤ 12.000 Dreiecke, Textur 1024).
- **Vor dem Hochladen prüfen:** Modell von vorn, von der Seite und von oben rendern und die Gliedmaßen zählen.
  Nur hochladen, wenn es zur Vorlage passt. Kleine Netzspitzen oder Fortsätze nur melden, ich entferne sie.
- Je Monster nur ein Versuch. Wenn er misslingt: melden statt sofort neu erzeugen.

## Ablage

`Vorlage_Raw/Monster_Roh/Modelltests_v3/` mit je Monster:

- `<id>_vorlage.png` (die tatsächliche Meshy-Eingabe)
- `<id>_statisch_roh.glb` (unverändert)
- bei den Zweibeinern zusätzlich `<id>_rig_roh.glb` mit den mitgelieferten Bewegungen
- `<id>_vorschau_vorn.png`, `<id>_vorschau_seite.png`, `<id>_vorschau_oben.png`
- eine kurze `LIESMICH_CLAUDE.md`: Credits, Einstellungen, Dreiecke, Bewegungsnamen, Auffälligkeiten

IDs: `schleimling`, `schleimmutter`, `krabbler`, `brecher`, `koloss`.

## Danach

Ich baue je Monster Skelett und Bewegungen nach (Skripte in `tools/monsters/`), teste im Spiel und schicke dem
Nutzer ein **Prüfbild** (Laufen, Angriff, Größe neben den Helden auf der Brücke). Kein Monster wird ohne seine
Freigabe aktiv; bis dahin bleiben die alten Figuren im Spiel.
