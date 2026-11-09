# Dschungelmond: 3D-Modelle der vier neuen Gegner – Auftrag für ChatGPT (Stand 09.11.2026)

**Kosten: 4 Erzeugungen zu je etwa 15 Meshy-Credits, zusammen etwa 60 Credits (bezahltes Konto).
Vom Nutzer am 09.11.2026 freigegeben (etwa 60 Credits).** Wenn Rigging oder Bewegungen bei Meshy extra kosten,
das vorher sagen und nicht ungefragt buchen.

Vorlagen (vom Nutzer freigegeben): `Vorlage_Raw/Gegner_51_150_v1/06_leicht.png`, `06_mittel.png`, `06_stark.png`,
`06_boss.png`. Vorgehen wie bei den bisherigen acht Gegnern (`Vorlage_Raw/Monster_Roh/NAECHSTE_MONSTER_FUER_CHATGPT.md`).

---

Bitte aus diesen vier freigegebenen Bildvorlagen bei Meshy je ein 3D-Modell erzeugen, für mein Handyspiel
(Tower Defense, Comic-Stil). Die Vorlagen liegen auf GitHub (Repository `Handy-App-Tower-Defense_-No-Name`, Branch
`claude/amazing-hypatia-yl59v4`) unter `Vorlage_Raw/Gegner_51_150_v1/`.

**Kostenrahmen: höchstens 4 Erzeugungen, etwa 60 Meshy-Credits, vom Nutzer freigegeben.** Wenn Rigging oder
Bewegungen extra kosten, vorher melden und nicht ungefragt buchen. Je Gegner nur ein Versuch; wenn er misslingt,
melden statt sofort neu erzeugen.

## Die vier Gegner

| ID | Vorlage | Name · Stärke | Körperbau | Meshy-Rigging |
|---|---|---|---|---|
| `rankling` | `06_leicht.png` | Rankling · leicht | Blätterklumpen ohne Arme und Beine | **nicht nötig** |
| `bluetenschnapper` | `06_mittel.png` | Blütenschnapper · mittel | fliegende Blüte, zwei Blattflügel, keine Arme, keine Beine | **nicht nötig** |
| `borkenkaefer` | `06_stark.png` | Borkenkäfer · stark | Käfer mit Rindenpanzer, genau **sechs** Beine (drei je Seite) | **nicht nötig** |
| `urwaldriese` | `06_boss.png` | Urwaldriese · Boss | Zweibeiner (wandelnder Baum), zwei Arme, zwei Beine | humanoides Rigging mit `Walking` und `Attack` |

Für Rankling, Blütenschnapper und Borkenkäfer baut Claude Skelett und Bewegungen selbst; dafür reicht das
statische Modell.

## Erzeugung

- Meshy Bild-zu-3D (T2.5 wie bisher), genau die Vorlage als einziges Bild, kein Zusatztext
- Smart Topology, Ziel 10.000 Polygone, Texturen an, Posekorrektur aus, privat
- Claude verkleinert danach selbst auf das Handy-Maß (leicht ≤ 3.000, mittel ≤ 5.000, stark ≤ 7.000,
  Boss ≤ 12.000 Dreiecke, Textur 1024)

## Vor dem Hochladen prüfen

- Jedes Modell von vorn, von der Seite und von oben rendern und die Gliedmaßen zählen.
- **Borkenkäfer:** genau sechs Beine. Beim früheren Panzerkäfer hat Meshy acht Beine erzeugt; die Draufsicht ist
  hier die wichtigste Kontrolle.
- **Blütenschnapper:** genau zwei Flügel, keine zusätzlichen Arme oder Beine.
- **Urwaldriese:** zwei Arme, zwei Beine, Hände nicht mit dem Körper verschmolzen; nach dem Rigging prüfen, ob
  Laufen und Angriff die Arme sauber bewegen.
- Nur hochladen, wenn es zur Vorlage passt. Kleine Netzspitzen oder Fortsätze nur melden, Claude entfernt sie.

## Ablage

`Vorlage_Raw/Monster_Roh/Modelltests_v4/` mit je Gegner:

- `<id>_vorlage.png` (die tatsächliche Meshy-Eingabe)
- `<id>_statisch_roh.glb` (unverändert)
- beim Urwaldriesen zusätzlich `urwaldriese_rig_roh.glb` mit den mitgelieferten Bewegungen
- `<id>_vorschau_vorn.png`, `<id>_vorschau_seite.png`, `<id>_vorschau_oben.png`
- eine kurze `LIESMICH_CLAUDE.md`: verbrauchte Credits, Einstellungen, Dreiecke, Bewegungsnamen, gezählte
  Gliedmaßen, Auffälligkeiten

## Danach (Claude)

Claude baut je Gegner Skelett und Bewegungen nach, setzt die Gegner im Spiel für Level 51–60 ein und schickt dem
Nutzer ein **Prüfbild** (Laufen, Angriff, Größe neben den Helden auf der Brücke des Dschungelmonds). Kein Gegner wird
ohne Freigabe aktiv; bis dahin bleiben die eingefärbten bisherigen Gegner im Spiel.
