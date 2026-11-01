# Mockups → Spiel (mock2game)

Baut die Menü-Bildschirme 1:1 nach den Design-Mockups („Menü-Entwürfe Wurmloch“) ins Spiel.

1. Mockups herunterladen (Dateien `project/*.dc.html` und die Bilder `<id>.webp`) in einen Ordner,
   z. B. `MOCKUP_DIR=/pfad/zu/mockups`.
2. Export: `MOCKUP_DIR=… node export.js cfg/home.json` → `out/home/` (Hintergrund, Knöpfe, Texte als PNG/JSON).
   `dcrt.js` bildet die Mockup-Laufzeit nach (`{{ }}`, `sc-if`, `sc-for`, Knöpfe), die Schriften kommen aus `game/fonts`.
3. Ins Spiel: `python3 to_game.py out/home home` → `game/ui_mock/home/` (WebP, Import-Einstellungen, `layout.json`).

Im Spiel setzt `scripts/ui/mock/mock_view.gd` den Bildschirm wieder zusammen: Hintergrundbild, Knöpfe
als Bilder, alle Texte als echte Texte (Schrift, Größe, Farbe, Schatten aus dem Mockup). Was sich
ändert (Level-Knoten, Werte), steht in der Konfiguration unter `live` und zeichnet das Spiel selbst.
Rote Hinweis-Punkte werden immer herausgenommen und vom Spiel nur gezeigt, wenn etwas wartet.

Konfiguration (`cfg/*.json`): `board` (Mockup-Datei), `out`, `states` (Zustände mit `set` = setState),
`overlays` (Popups: nur die neuen Elemente gegenüber dem Grundzustand), `live` (`sel` = CSS-Auswahl,
`id`, `img` = Bild mit aufnehmen), `eval` (JavaScript je Zustand/Popup, läuft nach `set`) und `script`
(Hilfs-Skript neben der Konfiguration, läuft vor jedem `eval`). Beispiele: `cfg/shop.json` baut die
Reiter Truhen/Aufladen/Event aus den Bausteinen des Mockups, `cfg/wheel.json` passt die Felder des
Glücksrads an die echten Gewinne an und nimmt Rad, Nabe und Zeiger als eigene Bilder auf.
`to_game.py` legt gleiche Bilder (z. B. denselben Hintergrund in mehreren Zuständen) nur einmal ab.

Benötigt Node mit Playwright (Chromium) und Python mit Pillow.
