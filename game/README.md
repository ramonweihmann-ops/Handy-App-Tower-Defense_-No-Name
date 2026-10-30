# Pilot: Station am Wurmloch (Godot 4.7)

Spielbarer Pilot: 5 Level im Motiv „Schleim-Welt“, 8 Helden, Kugelbahn als
Munitions-Maschine, Kartenauswahl im Run, Hauptmenü mit Shop, Sammlung (Aufstellung bis 10
Helden), Upgrades (Tech-Baum, Munition, Talente), Basislager und Battle Pass, Spielstand und
Selbst-Update für die Testphase. Grafik aus einfachen Formen (Platzhalter).

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
| `scripts/ui/` | Anzeige im Kampf, Theme, Bausteine |
| `shaders/` | Deck, Energiezaun, Wurmloch, Sternenhimmel |
| `tests/` | Tests ohne Fenster für die Kugelbahn |

## Befehle (im Hauptordner)

```bash
GODOT=/pfad/zu/godot scripts/test.sh        # Kugelbahn-Test und Level 1–5 automatisch
GODOT=/pfad/zu/godot scripts/build-android.sh   # Android-App (APK) mit Download-Seite nach docs/pilot/
GODOT=/pfad/zu/godot scripts/build-web.sh       # Browser-Version (nur noch für Tests am PC)
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

- Grundtempo 60 % (`BASE_SPEED` in `main.gd`), Knopf x1/x2. x3 soll erst viel später kommen (etwa ab Level 100).
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
