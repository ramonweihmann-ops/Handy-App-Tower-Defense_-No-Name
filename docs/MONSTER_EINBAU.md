# Comic-Monster ins Spiel bringen (Plan, Stand 03.11.2026)

Grundlage: `Vorlage_Raw/Monster_Roh/Modelltests_v1` (Zombie, Tentakler, Panzerkäfer aus Meshy, Prüfung von
ChatGPT in `LIESMICH_CLAUDE.md`). Gleicher Weg wie bei Dusty Jo: Rohmodell → Blender-Nacharbeit per Skript
(`tools/monsters/build_<id>.py`, Blender als Python-Baustein, kostenlos) → GLB in `game/models/enemies_v2/` →
Godot-Test → **Prüfbild für die Freigabe** → erst dann im Spiel aktiv.

## Was das Spiel von einem Gegner braucht

| Punkt | heute im Code | Vorgabe für die Comic-Monster |
|---|---|---|
| Bewegungen | `walk` (Schleife) und `attack` (Schleife an der Mauer), `models.gd` | `Walk` oder `Fly` (auf der Stelle, Schleife), `Attack` (0,6–1,2 s, Schleife). `Hit` und `Death` vorerst nicht nötig: Treffer blinken, besiegte Gegner zerplatzen mit Effekt |
| Größe | `height` je Gegner (Schleimling 0,95 … Koloss 3,0) | Modell auf 1 Einheit normieren, das Spiel skaliert je Gegnertyp |
| Ausrichtung | Blick zu den Helden | Blick +Z (glTF), Ursprung zwischen den Füßen, Flieger mit fester Schwebehöhe (`lift`) |
| Leistung | bis über 20 Gegner gleichzeitig auf älteren Handys | **leicht ≤ 3.000, mittel ≤ 5.000, stark ≤ 7.000, Boss ≤ 12.000 Dreiecke** (Rohmodelle haben ~10.000 → verkleinern) |
| Textur | – | eine Textur, höchstens 1024 × 1024 (heute 2048) |

## Ablauf

**Schritt 1 – Zombie (Welt 2, mittel):** bereit für den Einbau.
- Hilfsobjekt `Icosphere` und die überzähligen Knochen ohne Gewicht entfernen (`Bone_053`, `Bone_054`,
  `headfront` nur nach Gewichtsprüfung), Textur 1024, auf ≤ 5.000 Dreiecke verkleinern.
- Clips umbenennen: `Walking` → `Walk`, `Attack` bleibt (auf eine Schlagschleife kürzen), `Hit_Reaction` →
  `Hit`, `Dead` → `Death` (für später). Vorwärtsbewegung aus den Clips nehmen (Gegner laufen per Code).
- In Godot: Lauf- und Angriffsschleife, Fußkontakt, Größe neben den Helden, Leistung mit 25 Zombies.
- **Prüfbild für dich** (Laufen, Angriff, Seite, im Kampf auf der Brücke), dann aktiv.

**Schritt 2 – Tentakler (Welt 1, mittel):** Modell gut, aber ohne Bewegungen.
- Bewegungen per Skript selbst erzeugen (wie bei Dusty Jo): `Fly` (Flügelschlag über die Ketten ab
  `Bone_026`/`Bone_031`, leichtes Auf und Ab), `Attack` (Greifarme ab `Bone_017`/`Bone_021` schnellen nach
  vorn). Hörner bleiben starr. Auf ≤ 5.000 Dreiecke.
- **Prüfbild für dich**, dann aktiv.

**Schritt 3 – Panzerkäfer (Welt 1, stark):** Test nicht bestanden, Meshy hat acht statt sechs Beine erzeugt.
- Empfehlung: **eine neue Erzeugung** mit der korrigierten Sechsbeiner-Vorlage und ausdrücklich „genau sechs
  Beine“, dazu die Draufsicht als Kontrolle. Kosten: etwa 15 Meshy-Credits (bezahltes Konto, braucht deine
  Freigabe). Ein Beinpaar in Blender zu entfernen geht, hinterlässt aber leicht Löcher und schiefe Gewichte.
- Danach rigge ich die sechs Beine selbst und erzeuge einen Dreifuß-Gang (`Walk`) und einen Biss (`Attack`).

**Stand:** Zombie, Tentakler und Panzerkäfer sind freigegeben und aktiv (Version 0.7.4). Auftrag für die
übrigen fünf: `Vorlage_Raw/Monster_Roh/NAECHSTE_MONSTER_FUER_CHATGPT.md` (etwa 75 Meshy-Credits, freigegeben am 03.11.2026).

**Schritt 4 – restliche Gegner**, wenn die drei laufen: Schleimling, Schleimmutter (Boss), Krabbler, Brecher,
Zombie-Koloss (Boss). Je Gegner: Bildvorlage (ChatGPT) → Meshy → mein Skript → Prüfbild → Einbau.
Planetenversionen (Welt 3–10) erst danach; bis dahin färbt das Spiel die Gegner je Welt ein wie heute.

Umstellung im Code: Eintrag je Gegner in `game/scripts/battle/models.gd` (`ENEMIES`) auf das neue Modell mit
Kennzeichen `v2`; die alten Modelle bleiben als Rückfall, solange ein neues fehlt. Kampfwerte (Leben, Tempo,
Schaden) ändern sich nicht; nur Aussehen und Bewegung.

## Mockups, die dazukommen

1. **Gegner-Übersicht (neu):** alle Monster je Welt und Stärke (leicht, mittel, stark, Boss) mit den neuen
   Comic-Bildern, Name, Stärke und in welchen Welten sie auftreten. Vorlage für Prüfung und für den
   Gegner-Atlas.
2. **Schlachtfelder:** die Boards „Schlachtfeld · …“ zeigen statt der alten Figuren die neuen Monster
   (Bilder aus Godot gerendert), damit Größe und Wirkung auf der Brücke geprüft werden können.
3. **Abenteuer-Pfad:** Boss-Marker je Welt mit dem Comic-Boss der Welt (heute für alle Welten derselbe).
4. **Kampf · Boss-Warnung:** kurzer Hinweis „Boss kommt“ mit Bild des Bosses (heute nur Text).

## Reihenfolge der Freigaben

Zombie-Prüfbild → Tentakler-Prüfbild → Entscheidung Panzerkäfer (neue Erzeugung ja/nein) → Gegner-Übersicht
als Mockup → Rest. Kein Modell geht ohne dein OK ins Spiel.
