#!/bin/bash
# Baut die Android-App (APK) des Piloten und legt sie mit einer Download-Seite nach docs/pilot/.
# Die Seite wird über GitHub Pages ausgeliefert; am Handy Link öffnen, APK laden, installieren.
#
# Voraussetzungen: Godot 4.7.2 mit Android-Exportvorlagen, Java, apksigner.
#   GODOT=/pfad/zu/godot  (sonst „godot“)
# Signiert wird mit dem Pilot-Testschlüssel android/pilot-test.keystore (nur für Testversionen!).
set -euo pipefail
cd "$(dirname "$0")/.."
GODOT="${GODOT:-godot}"

# Versionsnummer muss bei jedem Build steigen, sonst installiert Android kein Update
CODE=$(( ($(date -u +%s) - 1767225600) / 60 ))
STAMP="$(date -u +%Y%m%d-%H%M)"
sed -i "s/^version\/code=.*/version\/code=$CODE/" game/export_presets.cfg

export GODOT_ANDROID_KEYSTORE_RELEASE_PATH="$PWD/android/pilot-test.keystore"
export GODOT_ANDROID_KEYSTORE_RELEASE_USER="pilot"
export GODOT_ANDROID_KEYSTORE_RELEASE_PASSWORD="android"

rm -rf build/android
mkdir -p build/android docs/pilot
"$GODOT" --headless --path game --import >/dev/null 2>&1 || true
"$GODOT" --headless --path game --export-release "Android" ../build/android/station-pilot.apk

APK="station-pilot-$STAMP.apk"
rm -rf docs/pilot/*
cp build/android/station-pilot.apk "docs/pilot/$APK"
SIZE=$(du -m "docs/pilot/$APK" | cut -f1)
cat > docs/pilot/index.html <<HTML
<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Cache-Control" content="no-cache">
<title>Station am Wurmloch – Pilot</title>
<style>
  body { background:#0d1022; color:#eef; font-family:system-ui,sans-serif; margin:0; padding:32px 20px; text-align:center; }
  h1 { color:#ffd24a; font-size:1.6em; }
  a.btn { display:inline-block; margin:24px 0; padding:18px 28px; background:#ffd24a; color:#222; border-radius:14px; font-weight:bold; text-decoration:none; font-size:1.2em; }
  p, li { color:#b8c4e0; line-height:1.5; text-align:left; max-width:520px; margin:8px auto; }
</style>
</head>
<body>
<h1>Station am Wurmloch</h1>
<p style="text-align:center">Pilot · Android · Stand $STAMP UTC · etwa $SIZE MB</p>
<a class="btn" href="$APK">App herunterladen</a>
<ol>
  <li>Auf „App herunterladen“ tippen und die Datei öffnen.</li>
  <li>Beim ersten Mal fragt Android, ob der Browser Apps installieren darf: erlauben.</li>
  <li>Neue Versionen einfach drüber installieren, der Spielstand bleibt.</li>
</ol>
</body>
</html>
HTML
touch docs/.nojekyll
echo "Fertig: docs/pilot/$APK (Version $CODE)"
