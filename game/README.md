# Pilot: Station am Wurmloch (Godot 4.7)

Erster spielbarer Pilot: 5 Level im Motiv „Schleim-Welt“, 4 Helden, Kugelbahn als
Munitions-Maschine, Kartenauswahl im Run. Grafik aus einfachen Formen (Platzhalter).

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

## Balance (Stand 30.10.2026, automatischer Test, 10 Läufe je Level, ohne Hebel)

| Level | gewonnen | Karten pro Level |
|---|---|---|
| 1–3 | 10/10 | 3–6 |
| 4 | 6/10 | 7–8 |
| 5 (Boss) | 2/10 | 7–9 |

Mit Hebel wird es deutlich leichter. Der Test wählt Karten nach einfachen Regeln.

## Tempo und Leistung

- Grundtempo 60 % (`BASE_SPEED` in `main.gd`), Knopf x1/x2. x3 soll erst viel später kommen (etwa ab Level 100).
- Ausgelegt aufs Handy: keine Schatten, keine Kantenglättung, kein Glow, Treffer-Funken nur bei kritischen Treffern, höchstens 55 Kugeln gleichzeitig.
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
