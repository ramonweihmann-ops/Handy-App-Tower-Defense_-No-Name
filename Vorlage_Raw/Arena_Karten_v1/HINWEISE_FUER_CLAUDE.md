# Arena-Schlachtfelder – erste Designfassung

Stand: 03.11.2026. Zwei neue Arena-Hintergründe als PNG; bisherige Karten bleiben erhalten. Noch keine Spielszene, keine Spiellogik und keine Navigation geändert.

## Gestaltung

- `universums_arena.png`: kosmisches Stadion für den Universums-/Ausdauermodus. Violettblau, Gold, große Tribünenringe und ein kosmisches Tor am entfernten Laufbahnende.
- `multiplayer_arena.png`: interstellare Wettkampfarena mit cremefarbenen Bögen, Cyan links und Korallorange/Magenta rechts. Die Farben kennzeichnen Stadionbereiche, keine zwei Spielfelder. Nur eine eigene Heldenseite und eine einzige Gegnerlaufbahn.

Die Laufbahn bleibt als konstruktive Brücke erhalten, ist aber in Stadionarchitektur eingebettet. Keine Helden, Gegner oder fertigen HUD-Anzeigen in die Bilder eingemalt. Der untere flache Boden ist für die eigene Heldengruppe, Nachladen und Fähigkeiten reserviert.

## Tatsächliche Bildgröße und Layout

Beide Dateien sind **977 × 1610 Pixel** groß, vollständig deckende PNGs. Das Bildwerkzeug hat die angeforderte Größe 780 × 1688 nicht eingehalten. Keine nachträgliche Verzerrung oder künstliche Hochskalierung vorgenommen. Die Bilder sind deshalb **keine pixelgleichen Ersatzdateien** für `godot_karten_v3`.

Die folgenden Punkte wurden visuell aus den ausgegebenen Bildern abgelesen; sie sind Näherungen für den Einbau und müssen mit Figuren im Spiel geprüft werden. Ursprung oben links:

| Bereich | Universums-Arena | Multiplayer-Arena |
| --- | --- | --- |
| Mittellinie | x ≈ 488 | x ≈ 488 |
| Ferne Laufbahnkante | y ≈ 280, x ≈ 396–573 | y ≈ 270, x ≈ 401–576 |
| Übergang zur eigenen Plattform | y ≈ 1148 | y ≈ 1108 |
| Gemeinsam sicherer gerader Gegnerpfad als Vorschlag | (488, 320) → (488, 1070) | (488, 320) → (488, 1070) |
| Freier Bereich für eigene Helden | ungefähr y = 1170–1350 | ungefähr y = 1170–1350 |
| Ressourcen und Nachladen | ungefähr y = 1350–1495 | ungefähr y = 1350–1495 |
| Fähigkeiten | ungefähr y = 1495–1610 | ungefähr y = 1495–1610 |

Im jeweiligen Arenamodus Hintergrund, Figuren und Weltkoordinaten zusammen auf einer gemeinsamen logischen Fläche anordnen. Seitenverhältnis erhalten; keine automatische Vollbild-Zuschneidung, die Tribünen oder Boden abschneidet. Für ein schmales Handyfenster die Ansichtsstrategie ausdrücklich prüfen, bevor diese Dateien eingesetzt werden. Die vorhandenen HUD-Elemente bleiben separat und erhalten ausreichende Antippflächen. Die alten 780er Pixelkoordinaten nicht unverändert auf diese Bilder übertragen. Keine Kollisionsfläche aus den dekorativen Geländern ableiten.

## Moduslogik bleibt getrennt

Universumsmodus: Nutzer beschreibt ein Überleben so lange wie möglich. Ob die Zeit hochzählt oder ein Countdown läuft, ist noch nicht abschließend festgelegt; beides wird als dynamische Anzeige im Spiel umgesetzt. Kein Zeitwert ist im Hintergrund eingebrannt.

Multiplayer: keine zweite Heldengruppe im Hintergrund, keine zusätzliche untere Plattform. Art der Gegnerzuweisung, Wertung, Ranglisten und Netzwerklogik werden mit dieser Grafik nicht festgelegt.

## Danach vorgemerkt: Monster-Modelltests

Der Nutzer hat die Reihenfolge festgehalten: **erst diese beiden Arenen, danach Zombie, Tentakler und Panzerkäfer als erste Modelltests.** Damit werden Zweibeiner, Flügel und sechs Beine geprüft, bevor weitere Planetenversionen entstehen. Die freigegebene Monsterübersicht liegt lokal unter `ausgabe/monster_comic_v1/`.

1. Zombie: humanoide Hierarchie, Lauf-/Angriffsbewegungen und Verformungen testen.
2. Tentakler: zwei Flügel und zwei Greifarme, Körperbewegung und Flugzyklus testen.
3. Panzerkäfer: sechs kurze Beine, saubere Bodenbewegung und Panzer prüfen.

Das ist ein vorgemerkter nächster Arbeitsschritt. In diesem Paket wurden keine neuen Monster-GLBs erzeugt. Bestehende Animationen sind nicht automatisch auf neue Körper übertragbar.

## Prüfung und Herkunft

Die integrierte Bildgenerierung verwendete `ausgabe/godot_karten_v3/nebula_portal.png` als Geometrie-/Stilvorlage. Vollständige deutsche Bildanweisungen liegen bei. Beide PNGs wurden geöffnet und auf Bildgröße, Vollständigkeit, eine durchgehende Hauptlaufbahn, eine eigene Plattform und fehlende feste HUD-Texte geprüft. Dateigrößen und SHA-256 stehen in `DATEIPRUEFUNG.json`. Noch kein Godot-Spieltest.
