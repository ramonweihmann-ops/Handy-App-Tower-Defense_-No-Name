#!/usr/bin/env bash
# Mauern der Schlachtfelder in Blender bauen und fürs Spiel ablegen (game/ui/mauern/<feld>.webp).
# Aufruf (im Hauptordner): tools/mauern/bauen.sh [feld …]    braucht blender (4.x) und python3 mit Pillow und numpy
# Ablauf je Feld (Stand 22.11.2026, alle Mauern freigegeben):
# 1. Blender rendert die Mauer aus der Spielkamera (wall.py). Stil „form“ = Form der Lava-Mauer (form_kit.py) mit Farben
#    und Bauteilen aus planet_<feld>_form.py und Zusatzteilen aus planet_<feld>_extra.py; die Lava-Mauer selbst im Stil
#    „detail“ (planet_lava_asteroid_detail.py). 600 Durchgänge, etwa 3–5 Minuten je Mauer.
# 2. angleichen.py zieht Farbton und Kontrast leicht (0.25) zur Brücke, 3. inv_filmic.py gleicht das Filmic-Tonemapping
# der Kampfszene aus, 4. Zuschnitt 780 × 260 als WebP. Danach im Spiel: godot --headless --path game --import
set -euo pipefail
cd "$(dirname "$0")/../.."
TMP=$(mktemp -d)
FELDER=${*:-"space_dock ice_world desert_outpost lava_asteroid nebula_portal jungle_moon ocean_world crystal_planet storm_giant scrap_world cloud_city spore_world ghost_moon temple_planet black_hole universums_arena multiplayer_arena"}
for F in $FELDER; do
  STIL=form
  [ "$F" = lava_asteroid ] && STIL=detail
  WALLSTYLE=$STIL blender -b -P tools/mauern/wall.py -- "$F" "$TMP/$F.png" 600 > "$TMP/$F.log" 2>&1 || { tail -20 "$TMP/$F.log"; exit 1; }
  python3 tools/mauern/angleichen.py "$TMP/$F.png" "game/fields/$F.webp" "$TMP/${F}_a.png" 0.25
  python3 tools/mauern/inv_filmic.py "$TMP/${F}_a.png" "$TMP/${F}_i.png" > /dev/null
  python3 -c "from PIL import Image; Image.open('$TMP/${F}_i.png').crop((0, 0, 780, 260)).save('game/ui/mauern/$F.webp', quality=90, alpha_quality=100, method=6)"
  echo "Mauer $F fertig"
done
rm -rf "$TMP"
