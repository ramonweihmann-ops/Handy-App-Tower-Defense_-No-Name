#!/bin/bash
# Baut die Browser-Version des Piloten nach build/web/ – nur noch zum Testen am PC.
# Veröffentlicht wird ausschließlich die Android-App (scripts/build-android.sh nach docs/pilot/),
# darum schreibt dieses Skript nichts nach docs/.
# Ansehen: cd build/web && python3 -m http.server 8060, dann http://localhost:8060/ öffnen.
# Voraussetzung: Godot 4.7.2 mit Web-Exportvorlagen. Pfad zu Godot über GODOT, sonst „godot“.
set -euo pipefail
cd "$(dirname "$0")/.."
GODOT="${GODOT:-godot}"
rm -rf build/web
mkdir -p build/web
"$GODOT" --headless --path game --import >/dev/null 2>&1 || true
"$GODOT" --headless --path game --export-release "Web" "../build/web/index.html"
echo "Fertig: build/web/index.html"
