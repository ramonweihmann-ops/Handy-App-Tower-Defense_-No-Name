#!/bin/bash
# Baut die Browser-Version des Piloten nach docs/pilot/ (wird über GitHub Pages ausgeliefert).
# Jede Version bekommt eigene Dateinamen (spiel-<Zeitstempel>.*), damit Handys keine alten
# Dateien aus dem Zwischenspeicher mit neuen mischen. docs/pilot/index.html leitet weiter.
# Voraussetzung: Godot 4.7.2 mit Web-Exportvorlagen. Pfad zu Godot über GODOT, sonst „godot“.
set -euo pipefail
cd "$(dirname "$0")/.."
GODOT="${GODOT:-godot}"
STAMP="$(date -u +%Y%m%d-%H%M%S)"
NAME="spiel-$STAMP"
rm -rf build/web
mkdir -p build/web docs/pilot
"$GODOT" --headless --path game --import >/dev/null 2>&1 || true
"$GODOT" --headless --path game --export-release "Web" "../build/web/$NAME.html"
rm -rf docs/pilot/*
cp build/web/* docs/pilot/
cat > docs/pilot/index.html <<HTML
<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Cache-Control" content="no-cache">
<title>Station am Wurmloch (Pilot)</title>
<script>location.replace("$NAME.html");</script>
</head>
<body style="background:#0d1022;color:#fff;font-family:sans-serif;text-align:center;padding-top:40vh">
<a href="$NAME.html" style="color:#ffd24a">Pilot starten</a>
</body>
</html>
HTML
touch docs/.nojekyll
echo "Fertig: docs/pilot/$NAME.html"
