# Pilot: Station am Wurmloch (Godot 4.7)

Erster spielbarer Pilot: 5 Level im Motiv „Schleim-Welt“, 4 Helden, Kugelbahn als
Munitions-Maschine, Kartenauswahl im Run. Grafik aus einfachen Formen (Platzhalter).

## Spielen

- Im Browser (Handy): über GitHub Pages, `docs/pilot/index.html`
- Am PC: Projektordner `game/` in Godot 4.7 öffnen und starten

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
GODOT=/pfad/zu/godot scripts/build-web.sh   # Browser-Version nach docs/pilot/
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
