#!/bin/bash
# Baut die Browser-Version des Piloten nach docs/pilot/ (wird über GitHub Pages ausgeliefert).
# Voraussetzung: Godot 4.7.2 mit Web-Exportvorlagen. Pfad zu Godot über GODOT, sonst „godot“.
set -euo pipefail
cd "$(dirname "$0")/.."
GODOT="${GODOT:-godot}"
mkdir -p build/web docs/pilot
"$GODOT" --headless --path game --import >/dev/null 2>&1 || true
"$GODOT" --headless --path game --export-release "Web" ../build/web/index.html
rm -rf docs/pilot/*
cp build/web/* docs/pilot/
touch docs/.nojekyll
echo "Fertig: docs/pilot/index.html"
