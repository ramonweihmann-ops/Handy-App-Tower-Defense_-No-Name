# Pilot: Station am Wurmloch (Godot 4.7)

Spielbarer Pilot: 10 Level in zwei Welten (Schleim-Welt, Zombie-Kolonie), 8 Helden, Kugelbahn als
Munitions-Maschine, Kartenauswahl im Run, Booster im Kampf, Hauptmenü mit Shop, Sammlung
(Aufstellung bis 10 Helden, Booster), Upgrades (Tech-Baum, Munition, Talente), Basislager und
Battle Pass, Töne und Musik, Spielstand und Selbst-Update für die Testphase. Helden und Gegner
sind fertige, animierte 3D-Modelle (CC0 von Quaternius, Quellen in `models/QUELLEN.md`).

## Spielen

- **Android:** https://ramonweihmann-ops.github.io/Handy-App-Tower-Defense_-No-Name/pilot/ öffnen, App herunterladen, installieren. Neue Versionen werden drüber installiert.
- **iOS:** gleiches Projekt, wird später auf einem Mac gebaut (Xcode, Apple-Entwicklerkonto).
- **Am PC:** Projektordner `game/` in Godot 4.7 öffnen und starten.

## Aufbau

| Datei | Inhalt |
|---|---|
| `scripts/main.gd` | Spielablauf: Menü, Heldenwahl, Karten, Pause, Ergebnis, automatischer Test |
| `scripts/game_data.gd` | Helden, Gegner, Wellen, Erfahrung (alle Balance-Werte) |
| `scripts/battle/` | 3D-Schlachtfeld, Helden, Gegner, Geschosse, Effekte |
| `scripts/machine/` | Kugelbahn (2D-Physik) und Energiekugeln |
| `scripts/ammo_store.gd` | gemeinsamer Munitionsspeicher |
| `scripts/meta_data.gd`, `scripts/save_game.gd` | Menü-Werte (Energie, Booster, Upgrades, Pass) und Spielstand |
| `scripts/sfx.gd` | Töne und Musik (Autoload „Sfx“) |
| `scripts/ui/` | Menü, Anzeige im Kampf, Theme (weiche „Candy“-Flächen), Levelbild, Porträts |
| `shaders/` | Deck, Energiezaun, Wurmloch, Sternenhimmel, Menü- und Levelbild-Hintergrund |
| `models/` | 3D-Modelle (glTF) für Helden, Gegner und Waffen, Zuordnung in `scripts/battle/models.gd` |
| `audio/` | Töne und Musik, selbst erzeugt mit `scripts/make_sounds.py` (keine fremden Rechte) |
| `tests/` | Tests ohne Fenster: Kugelbahn und Menü-Rundgang |

## Befehle (im Hauptordner)

```bash
GODOT=/pfad/zu/godot scripts/test.sh        # Kugelbahn-Test und Level 1–5 automatisch
GODOT=/pfad/zu/godot scripts/build-android.sh   # Android-App (APK) mit Download-Seite nach docs/pilot/
GODOT=/pfad/zu/godot scripts/build-web.sh       # Browser-Version nach build/web/ (nur für Tests am PC)
python3 scripts/make_sounds.py                  # Töne und Musik neu erzeugen
```

Einzelner automatischer Lauf mit Ausgabe der Werte:

```bash
godot --headless --fixed-fps 60 --path game -- --autotest --level=4 --seed=3 --pull
```

## Balance (Stand 0.2.1, automatischer Test, 8 Läufe je Level, ohne Hebel, ohne Aufwertungen)

| Level | gewonnen | Munitionsspeicher im Mittel | Helden warten auf Munition |
|---|---|---|---|
| 1 | 8/8 | 67 % | 0 % |
| 2 | 8/8 | 56 % | 3 % |
| 3 | 7/8 | 39 % | 18 % |
| 4 | 4/8 | 40 % | 16 % |
| 5 (Boss) | 2/8 | 36 % | 19 % |

Munition soll knapp, aber kein Dauer-Engpass sein; dauerhafte Munitions-Upgrades, Heldenstufen
und der Hebel gleichen das aus. Messen mit `--autotest` (Ausgabe `fill`, `full`, `wait`).

## Selbst-Update (Testphase)

`scripts/build-android.sh` schreibt `game/build_info.json` (eigene Version) und
`docs/pilot/version.json` (neueste Version, APK-Name, Hinweistext). Die App prüft beim Start und
im Menü, zeigt „Jetzt aktualisieren“, lädt die APK in ihren Speicher und öffnet die
Android-Installation; beim nächsten Start wird die Datei gelöscht. Hinweistext über `NOTES=…`,
Versionsname über `VNAME=…`. Später ersetzt Google Play diesen Weg.

## Tempo und Leistung

- Tempo je Stufe in `TEMPO_SCALE` (`main.gd`): x1 = 68 %, x2 = 120 %, x3 = 180 % der Rechengeschwindigkeit. x3 gibt es nur in der Testphase; später erst etwa ab Level 100.
- Grafik „Hoch“ (Leuchten, Schatten) oder „Sparsam“, umschaltbar in den Einstellungen. Treffer-Funken nur bei kritischen Treffern, höchstens 55 Kugeln gleichzeitig, Formen und Materialien von Geschossen werden wiederverwendet.
- Die Kugelbahn läuft in einer eigenen Ansicht in voller Größe und wird auf 78 % verkleinert angezeigt; darunter bleibt Abstand zur Gestenleiste des Handys.
- Im breiten Fenster bleibt das Spiel eine Hochformat-Spalte in der Mitte.

## Android-Build

- Paketname des Piloten: `com.homipoint.wurmloch.pilot` (die endgültige Play-Store-App bekommt einen eigenen Namen)
- nur 64-Bit (`arm64-v8a`), etwa 27 MB
- signiert mit dem **Pilot-Testschlüssel** `android/pilot-test.keystore` (Passwort `android`). Er liegt absichtlich im Repo, damit jede Sitzung Updates bauen kann, die sich über die alte App installieren lassen. **Nur für Testversionen.** Für Google Play kommt ein eigener, geheimer Upload-Schlüssel, der nie ins Repo gehört.
- Versionsnummer zählt bei jedem Build automatisch hoch.
- Benötigt: Godot-Android-Exportvorlagen, Java, `apksigner` und `zipalign` (Ubuntu-Pakete).

## Ladebildschirm

Beim Start zeigt die App einen Ladebildschirm. Währenddessen wird jeder Held, jeder Gegner und
jeder Effekt einmal unsichtbar dargestellt, damit das Handy die Grafik vorbereitet und es beim
ersten Schuss nicht ruckelt (`_warm_up` in `main.gd`).

## Töne und Musik

Alle Klänge sind mit `scripts/make_sounds.py` aus Sinus, Rauschen und Hüllkurven erzeugt, also
frei von fremden Rechten. `Sfx.play("name")` spielt einen Ton; gleiche Töne kurz hintereinander
werden gedrosselt (Werte in `GAP`), damit Salven bei x2/x3 nicht zu Rauschen werden. Jeder Knopf
klickt automatisch. Töne und Musik lassen sich in den Einstellungen getrennt abschalten. In den
automatischen Tests und hinter dem Ladebildschirm ist alles stumm.

## Booster

Bis zu zwei Booster pro Kampf (Sammlung → Booster): Luftangriff, Medipack, Zeitlupe, Kuppel,
Munitionskiste. Sie werden mit Gold aufgewertet (mehr Wirkung, kürzere Abklingzeit) und im Kampf
über die runden Knöpfe am linken Rand ausgelöst.

## 3D-Modelle

`scripts/battle/models.gd` legt fest, welcher Held und welcher Gegner welches Modell bekommt
(Datei, Höhe, Animationen). Helden stehen in einer Zielhaltung (Schuss-Animation angehalten) und
halten ein Waffenmodell, wo es eins gibt; Tesla, Eiskanone und Flammenwerfer behalten ihre
eigene Form. Gegner laufen mit ihrer Lauf-Animation und wechseln am Zaun in den Angriff; Treffer
und Frost färben sie über eine Überlagerung, die nur eingeschaltet ist, solange sie wirkt. Fehlt
eine Modelldatei, baut die Figur ihre einfache Form wie früher.

Bilder zum Ansehen am PC (braucht ein Fenster, z. B. `xvfb-run`):

```bash
godot --path game res://tests/render_models.tscn -- --out=/tmp/helden.png --mode=front    # oder enemies, times
godot --path game -- --autotest --level=7 --shot=/tmp/kampf.png                          # Kampfbild nach 8 s
```
