# Fünf weitere Comic-Monster – Rohmodelle v3

Stand: 04.11.2026. Auftrag aus `NAECHSTE_MONSTER_FUER_CHATGPT.md`. Keine Spieldatei ersetzt, keine Freigabe für den aktiven Kampf vorweggenommen. Weltvarianten ab Welt 3 weiterhin über die vorhandenen Grundmodelle gestalten.

## Inhalt und tatsächliche Ergebnisse

| ID | Kategorie | Dreiecke statisch / Rig | Skelett / tatsächliche Bewegungsnamen | Sichtprüfung |
| --- | --- | ---: | --- | --- |
| schleimling | Welt 1, leicht | 10.447 / entfällt | kein Rig, keine Clips | geschlossener Schleimkörper; keine Arme und Beine |
| schleimmutter | Welt 1, Boss | 10.215 / entfällt | kein Rig, keine Clips | breiter Körper, rosa Gesicht, drei gelbe Kronenkugeln; keine Arme und Beine |
| krabbler | Welt 2, leicht | 10.116 / 10.116 | humanoid; `Running`, `Walking`, `Attack` | zwei Arme, zwei Beine; freie Abstände |
| brecher | Welt 2, stark | 10.274 / 10.274 | humanoid; `Running`, `Walking`, `Attack` | zwei Arme, zwei Beine; breite Schultern und Handschuhe |
| koloss | Welt 2, Boss | 10.501 / 10.501 | humanoid; `Running`, `Walking`, `Attack` | zwei lange Arme, zwei kurze Beine, große grüne Hände |

Je Monster liegen die tatsächliche Meshy-Eingabe als `<id>_vorlage.png`, das unveränderte texturierte `<id>_statisch_roh.glb` und drei aus diesem GLB gerenderte Ansichten `vorn`, `seite`, `oben` vor. Für die drei Zweibeiner zusätzlich unveränderte `<id>_rig_roh.glb` mit allen hinzugefügten Clips. Die zusätzliche Laufbewegung beim Brecher und Koloss wird von Meshy automatisch mitgeliefert und darf bei Bedarf ungenutzt bleiben.

Alle acht GLBs enthalten jeweils eine eingebettete 2048 × 2048-Farbtextur und ein Material. Texturen wurden bewusst nicht verkleinert, Geometrie nicht bereinigt, Clips nicht umbenannt und Metadaten nicht entfernt. Das sind unveränderte Rohquellen für die vereinbarte Nacharbeit.

## Einstellungen und Kosten

Je Monster genau ein Versuch: Meshy T2.5, Smart Topology, Ziel 10.000 Polygone, Textur an (Meshy N1 / 2K), Posekorrektur aus, privat. Das Ziel ist ein Näherungswert; tatsächliche Dreieckzahlen stehen oben. Keine Mehransicht und kein Zusatztext an Meshy übergeben.

**5 × 15 = 75 Credits verbraucht.** Humanoides Rigging und hinzugefügter Vorgabeclip Angriff: **0 zusätzliche Credits**, keine kostenpflichtige Bewegungserzeugung, kein neuer Kauf. Ausgangsstand 1.265; nach Schleimling 1.250; am Folgetag 50 Credits tägliche Gutschrift, dadurch 1.300. Danach Schleimmutter 1.285, Krabbler 1.270, Brecher 1.255, Koloss 1.240. Rigging und Clip-Auswahl haben den Endstand nicht verändert.

Kostenquelle geprüft am 04.11.2026: [offizielle Webapp-Kostenübersicht](https://docs.meshy.ai/en/webapp/pricing) (Rigging und fertige Animationsclips jeweils 0 Credits). Keine API-Riggingpreise zugrunde gelegt. Der erste Rigging-Start wurde bei ungeklärtem Preis automatisch blockiert; erst nach Prüfung der offiziellen Kostenübersicht ausgeführt.

## Vorlagen und Herkunft

Neue Einzelvorlagen mit der eingebauten Bildgenerierung aus der vom Nutzer bestätigten Übersicht `monster_comic_v1/monster_10_welten_uebersicht.png` abgeleitet. Eine Figur pro Bild, transparente 1024 × 1024-PNGs, auf höchstens 818 Pixel Motivbreite/-höhe skaliert und mittig gesetzt, etwa zehn Prozent Rand. Schleime ohne Gliedmaßen; Zweibeiner mit offenen einfachen Händen und A-Pose ohne Waffen. Keine Bodenplatten, Texte oder zusätzlichen Ansichten.

Nutzungsgrundlage: bestehendes bezahltes Meshy-Konto, Einstellung privat. [Meshy-Bedingungen](https://www.meshy.ai/terms-of-use). Keine Zusage über ausschließliche Rechte an generierten Formen; keine Fremdmodell-Dateien beigemischt.

## Auffälligkeiten und Nacharbeit

- **Schleimling:** Anatomie entspricht der Vorlage. Kleine unregelmäßige Augenränder und gebackene Glanzstellen sind sichtbar. Ruhig glätten bzw. beim späteren Texturaufbereiten prüfen. Hüpfen und Zuschnappen samt kleinem Skelett erstellt Claude.
- **Schleimmutter:** Kleine dunkle dreieckige Stelle an der seitlichen Flanke (Seitenansicht), außerdem fleckige Pupille links im Bild. Als Netz-/Texturartefakte prüfen und bereinigen; kein zusätzliches Körperteil. Keine frei hängenden Fäden oder Tropfen.
- **Krabbler:** Hände bewusst vereinfacht. Kopf deutlich größer als Rumpf; Kopfgewichtung und Schulterübergänge im Bewegungstest kontrollieren. A-Pose und beide Beine blieben erhalten.
- **Brecher:** Breite starre Schulterpanzer und dicker Halskragen. Bei Angriff mögliche Überschneidungen von Kragen, Händen und Kopf kontrollieren. Große einfache Handschuhe statt einzelner feiner Finger.
- **Koloss:** Sehr breite Hände und kurze Beine wie Vorlage. Unterarme/Hände und Kragen beim Angriff auf Selbstüberschneidungen prüfen. Oben am Rücken ein kleiner kantiger violetter Panzerfortsatz, keine zusätzliche Gliedmaße. Bei Bedarf glätten. Kein zweiter Riggingversuch ausgeführt.

Die Rig-Assistenten wurden auf humanoid gestellt, Ausrichtung beibehalten und Kinn-/Hüftmarken an die Comic-Proportionen angepasst. Beim Krabbler zusätzlich Schulter-/Kniemarkierungen korrigiert. Meshy normiert die Rig-Fassung ungefähr auf 1,70 Höhe; das ist ausdrücklich **keine endgültige Kampfgröße**. Boss, Brecher und Krabbler im Spiel unterschiedlich groß skalieren.

`Walking` dauert ungefähr 1,03 s, `Running` 0,63 s und `Attack` 2,80 s. Timing, Schleifen, Root-Bewegung und Trefferzeitpunkt danach säubern. `Hit`, `Death` und ein eigener `Idle` sind nicht enthalten; Claude ergänzt die benötigten Gegnerclips. Endgültige Namen insbesondere `Walking` → `Walk` nach vorhandener Spielkonfiguration setzen.

## Prüfungen

Alle fünf statischen Modelle in Blender importiert und aus drei orthografischen Richtungen gerendert, anschließend visuell auf Körperbau und Gliedmaßen geprüft. Alle drei Rigs in Blender importiert; je Clip fünf Zeitpunkte auf endliche Koordinaten geprüft. Das bestätigt Importierbarkeit, nicht automatisch saubere Hautgewichte oder fertige Animationen.

`GLB_PRUEFUNG.json`: Dateiprüfsummen, Dreiecke, Texturen, Knochen und tatsächliche Clips. `RIG_IMPORT_UND_BEWEGUNGSPRUEFUNG.json`: Import und Bewegungsstichproben. Einzelne `*_IMPORTPRUEFUNG.json`: statische Geometriegrenzen. `DATEIPRUEFUNG.json`: Bildmaße und Prüfsummen. `MODELLUEBERSICHT.jpg`: Prüfübersicht aus den tatsächlichen GLBs, jedes Modell unabhängig auf seine Zelle eingepasst; kein Größenvergleich.

Claude übernimmt Handyziele (leicht ≤ 3.000, stark ≤ 7.000, Boss ≤ 12.000 Dreiecke), Texturen 1024 × 1024, bereinigte Skelette/Gewichte, fehlende Clips, abgestimmte Größen und Godot-Spieltest. Vor Nutzerfreigabe die bisherigen Spielfiguren aktiv lassen.
