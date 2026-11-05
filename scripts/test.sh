#!/bin/bash
# Automatische Tests ohne Fenster: Menü-Rundgang, Superfähigkeiten, Multiplayer und je ein Lauf pro Level.
set -uo pipefail
cd "$(dirname "$0")/.."
GODOT="${GODOT:-godot}"
"$GODOT" --headless --path game --import >/dev/null 2>&1 || true
fail=0
echo "== Menü-Rundgang =="
out=$("$GODOT" --headless --fixed-fps 60 --path game -- --smoke 2>&1)
echo "$out" | grep -E "SMOKE"
if grep -qE "SCRIPT ERROR|ERROR:|SMOKE FEHLER" <<< "$out"; then echo "$out" | grep -E "ERROR|FEHLER" | head -5; fail=1; fi
echo "== Tutorial: ganzer Durchlauf =="
out=$("$GODOT" --headless --fixed-fps 60 --path game -- --tutflow 2>&1)
echo "$out" | grep -E "TUTFLOW fertig"
if grep -qE "SCRIPT ERROR|ERROR:|FEHLER" <<< "$out" || ! grep -q "TUTFLOW fertig" <<< "$out"; then echo "$out" | grep -E "ERROR|FEHLER" | head -5; fail=1; fi
echo "== Superfähigkeiten =="
out=$("$GODOT" --headless --fixed-fps 60 --path game -- --autotest --level=4 --seed=1 --ultcheck 2>&1)
echo "$out" | grep -E "ULTCHECK fertig"
if grep -qE "SCRIPT ERROR|ERROR:|ausgelöst: false" <<< "$out"; then echo "$out" | grep -E "ERROR|false" | head -5; fail=1; fi
echo "== Multiplayer: Wertung und Computergegner =="
out=$("$GODOT" --headless --path game --script tests/mp_fairness.gd 2>&1)
echo "$out" | grep -E "MPCHECK"
if grep -qE "SCRIPT ERROR|ERROR:|MPCHECK FEHLER" <<< "$out"; then echo "$out" | grep -E "ERROR|FEHLER" | head -5; fail=1; fi
echo "== Multiplayer-Kampf (Station 5, Seed 1) =="
out=$("$GODOT" --headless --fixed-fps 60 --path game -- --autotest --mp --level=5 --seed=1 --pull 2>&1)
echo "$out" | grep -E "MPTEST" | sed 's/ curve=.*//'
if grep -qE "SCRIPT ERROR|ERROR:" <<< "$out" || ! grep -q "MPTEST" <<< "$out"; then echo "$out" | grep -E "ERROR" | head -5; fail=1; fi
echo "== Level 1 bis 5 (Seed 1, mit Hebel) =="
for lvl in 1 2 3 4 5; do
  out=$("$GODOT" --headless --fixed-fps 60 --path game -- --autotest --level=$lvl --seed=1 --pull 2>&1)
  echo "$out" | grep -E "AUTOTEST" | sed 's/ cards=.*//'
  if grep -qE "SCRIPT ERROR|ERROR:" <<< "$out"; then echo "$out" | grep -E "ERROR" | head -5; fail=1; fi
done
exit $fail
