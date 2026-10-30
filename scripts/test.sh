#!/bin/bash
# Automatische Tests ohne Fenster: Kugelbahn-Durchfluss und je ein Lauf pro Level.
set -uo pipefail
cd "$(dirname "$0")/.."
GODOT="${GODOT:-godot}"
"$GODOT" --headless --path game --import >/dev/null 2>&1 || true
fail=0
echo "== Kugelbahn (60 s) =="
"$GODOT" --headless --fixed-fps 60 --path game --script res://tests/ball_flow.gd 2>&1 | grep -E "t=60|raus|ERROR"
echo "== Menü-Rundgang =="
out=$("$GODOT" --headless --fixed-fps 60 --path game -- --smoke 2>&1)
echo "$out" | grep -E "SMOKE"
if echo "$out" | grep -qE "SCRIPT ERROR|ERROR:"; then echo "$out" | grep -E "ERROR" | head -5; fail=1; fi
echo "== Level 1 bis 5 (Seed 1, mit Hebel) =="
for lvl in 1 2 3 4 5; do
  out=$("$GODOT" --headless --fixed-fps 60 --path game -- --autotest --level=$lvl --seed=1 --pull 2>&1)
  echo "$out" | grep -E "AUTOTEST" | sed 's/ cards=.*//'
  if echo "$out" | grep -qE "SCRIPT ERROR|ERROR:"; then echo "$out" | grep -E "ERROR" | head -5; fail=1; fi
done
exit $fail
