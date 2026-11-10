# Borkenkäfer: zweiter Versuch mit Draufsicht – Auftrag für ChatGPT (Stand 10.11.2026)

**Kosten: 1 Erzeugung, etwa 15 Meshy-Credits (bezahltes Konto). Vom Nutzer am 10.11.2026 freigegeben
(Variante a).** Die neue Bildvorlage entsteht mit der eingebauten Bildgenerierung, ohne Zusatzkosten.

Erster Versuch: acht statt sechs Beine (`Modelltests_v4/BORKENKAEFER_FEHLVERSUCH.md`). Beim Panzerkäfer hat genau
dieses Vorgehen beim zweiten Mal geklappt (`Modelltests_v2/LIESMICH_CLAUDE.md`): **eine eindeutige Draufsicht als
einzige Meshy-Eingabe.**

---

Der Borkenkäfer für mein Handyspiel hatte bei Meshy acht statt sechs Beine. Bitte einen zweiten Versuch so wie
beim Panzerkäfer, der damit beim zweiten Mal genau sechs Beine bekam. Alles liegt auf GitHub (Repository
`Handy-App-Tower-Defense_-No-Name`, Branch `claude/amazing-hypatia-yl59v4`).

**Kostenrahmen: genau eine Meshy-Erzeugung, etwa 15 Credits, vom Nutzer freigegeben.** Kein Rigging nötig. Wenn es
misslingt: melden, nicht neu erzeugen.

## Schritt 1: neue Bildvorlage (Draufsicht)

- Vorbild: der freigegebene Borkenkäfer `Vorlage_Raw/Gegner_51_150_v1/06_stark.png` (gleiche Farben, gleicher
  Rindenpanzer mit Moos, gleiches Gesicht) und als Muster für die Ansicht
  `Vorlage_Raw/Monster_Roh/Modelltests_v2/panzerkaefer_vorlage_oben.png`.
- **Ansicht von schräg oben** wie beim Panzerkäfer-Muster, so dass **alle sechs Beine einzeln zu sehen** sind:
  drei Beine auf jeder Seite, deutlich voneinander und vom Körper getrennt, gleichmäßig verteilt (vorn, Mitte,
  hinten), jedes mit eigenem Fuß. Kein viertes Beinpaar, keine Fühler, die wie Beine aussehen.
- Kopf mit Gesicht vorn gut sichtbar.
- Eine Figur, transparenter Hintergrund, 1024 × 1024 Pixel, etwa 10 % Rand, kein Schatten, keine Bodenplatte,
  kein Text.
- Datei: `borkenkaefer_vorlage_oben.png`. Vor dem Weitermachen die Beine auf dem Bild zählen: genau sechs.

## Schritt 2: eine Meshy-Erzeugung

- Meshy Bild-zu-3D T2.5, nur `borkenkaefer_vorlage_oben.png` als einziges Bild, kein Zusatztext
- Smart Topology, Ziel 10.000 Polygone, Texturen an, Posekorrektur aus, privat
- kein Rigging

## Vor dem Hochladen prüfen

- Modell von vorn, von der Seite, von oben und von unten rendern und die Beine zählen. **Nur hochladen, wenn es
  genau sechs sind.** Kleine Netzspitzen oder Fortsätze nur melden.

## Ablage

`Vorlage_Raw/Monster_Roh/Modelltests_v5/`:
- `borkenkaefer_vorlage_oben.png` (die tatsächliche Meshy-Eingabe)
- `borkenkaefer_statisch_roh.glb` (unverändert)
- `borkenkaefer_vorschau_vorn.png`, `_seite.png`, `_oben.png`, `_unten.png`
- `LIESMICH_CLAUDE.md`: verbrauchte Credits, Einstellungen, Dreiecke, gezählte Beine, Auffälligkeiten

## Danach (Claude)

Claude baut Skelett, Dreifuß-Gang und Biss wie beim Panzerkäfer (`tools/monsters/build_panzerkaefer.py`),
schickt ein Prüfbild und setzt den Borkenkäfer nach Freigabe als starken Gegner auf dem Dschungelmond ein.
