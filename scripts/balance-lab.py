#!/usr/bin/env python3
"""Balance-Labor: spielt Level mit Spielerprofilen automatisch durch und prüft die Zielkurve.

Aufruf (im Hauptordner):
  GODOT=/pfad/zu/godot python3 scripts/balance-lab.py [--levels 1-10] [--seeds 12]
      [--profiles anfaenger,durchschnitt,zahlend] [--parallel 4] [--out docs/BALANCE.md]

Jeder Lauf ist ein automatischer Test (--autotest) mit Hebel und Boostern; das Profil stellt den
typischen Spielstand vor dem Level nach (game/tests/balance_profiles.gd). Ergebnis: Bericht mit
Siegquote je Level und Profil, Abgleich mit der Zielkurve (docs/KONZEPT.md, Abschnitt 9) und
Siegquote je Starthelden.
"""
import argparse, collections, concurrent.futures, os, re, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOSS_EVERY = 5

# Zielkurve: (von, bis) Siegquote beim ersten Versuch; None = keine Vorgabe.
def target(level, profile):
    boss = level % BOSS_EVERY == 0
    if level <= 20:
        return {"anfaenger": (0.70, 1.0), "durchschnitt": (0.85, 1.0), "zahlend": (0.95, 1.0)}[profile]
    if boss:
        return {"anfaenger": None, "durchschnitt": (0.35, 0.55), "zahlend": (0.70, 1.0)}[profile]
    return {"anfaenger": None, "durchschnitt": (0.55, 0.75), "zahlend": (0.85, 1.0)}[profile]


def run(godot, level, profile, seed):
    cmd = [godot, "--headless", "--fixed-fps", "60", "--path", os.path.join(ROOT, "game"), "--",
           "--autotest", f"--level={level}", f"--seed={seed}", "--pull", f"--profile={profile}"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=900).stdout
    except subprocess.TimeoutExpired:
        return None
    for line in out.splitlines():
        if line.startswith("AUTOTEST"):
            v = dict(re.findall(r"(\w+)=(\S+)", line))
            fence = v["fence"].split("/")
            start = re.search(r"start:(\w+)", v.get("cards", ""))
            return {"level": level, "profile": profile, "seed": seed, "win": v["result"] == "win",
                    "time": float(v["time"]), "wait": float(v["wait"]), "fill": float(v["fill"]),
                    "shield": float(fence[0]) / max(1.0, float(fence[1])),
                    "start": start.group(1) if start else "?"}
    return None


def parse_levels(s):
    out = []
    for part in s.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", default="1-10")
    ap.add_argument("--seeds", type=int, default=12)
    ap.add_argument("--profiles", default="anfaenger,durchschnitt,zahlend")
    ap.add_argument("--parallel", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "BALANCE.md"))
    a = ap.parse_args()
    godot = os.environ.get("GODOT", "godot")
    levels, profiles = parse_levels(a.levels), a.profiles.split(",")
    jobs = [(l, p, s) for l in levels for p in profiles for s in range(1, a.seeds + 1)]
    t0 = time.time()
    results = []
    with concurrent.futures.ThreadPoolExecutor(a.parallel) as ex:
        for i, r in enumerate(ex.map(lambda j: run(godot, *j), jobs), 1):
            if r:
                results.append(r)
            if i % 20 == 0:
                print(f"{i}/{len(jobs)} Läufe …", flush=True)
    by = collections.defaultdict(list)
    for r in results:
        by[(r["level"], r["profile"])].append(r)
    lines = ["# Balance-Bericht", "",
             f"Stand {time.strftime('%d.%m.%Y %H:%M')} · {len(results)} Läufe · {a.seeds} je Level und Profil · "
             f"Dauer {int(time.time() - t0) // 60} min", "",
             "Siegquote beim ersten Versuch je Spielerprofil (✓ im Ziel, ↑ zu leicht, ↓ zu schwer, · ohne Vorgabe). "
             "Zielkurve und Profile: `docs/KONZEPT.md` (Abschnitt 9), `game/tests/balance_profiles.gd`.", "",
             "| Level | " + " | ".join(profiles) + " | Ø Schild übrig (Sieg) | Ø Warten auf Munition |",
             "|---|" + "---|" * len(profiles) + "---|---|"]
    misses = 0
    for l in levels:
        cells, shields, waits = [], [], []
        for p in profiles:
            rs = by[(l, p)]
            if not rs:
                cells.append("–")
                continue
            q = sum(r["win"] for r in rs) / len(rs)
            t = target(l, p)
            mark = "·" if t is None else ("✓" if t[0] <= q <= t[1] else ("↑" if q > t[1] else "↓"))
            misses += mark in "↑↓"
            cells.append(f"{q:.0%} {mark}")
            shields += [r["shield"] for r in rs if r["win"]]
            waits += [r["wait"] for r in rs]
        boss = " (Boss)" if l % BOSS_EVERY == 0 else ""
        sh = f"{sum(shields) / len(shields):.0%}" if shields else "–"
        wt = f"{sum(waits) / len(waits):.0%}" if waits else "–"
        lines.append(f"| {l}{boss} | " + " | ".join(cells) + f" | {sh} | {wt} |")
    lines += ["", f"**Abweichungen von der Zielkurve: {misses}**", "",
              "## Starthelden", "",
              "Siegquote, wenn der Lauf mit diesem Helden begann (alle Level und Profile). Große Abstände "
              "heißen: ein Held ist zu stark oder zu schwach.", "",
              "| Held | Läufe | Siegquote | Ø Schild übrig | Ø Dauer |", "|---|---|---|---|---|"]
    heroes = collections.defaultdict(list)
    for r in results:
        heroes[r["start"]].append(r)
    def score(rs):
        return (sum(r["win"] for r in rs) / len(rs), sum(r["shield"] for r in rs) / len(rs))
    for h, rs in sorted(heroes.items(), key=lambda kv: tuple(-x for x in score(kv[1]))):
        q, sh = score(rs)
        t = sum(r["time"] for r in rs) / len(rs)
        lines.append(f"| {h} | {len(rs)} | {q:.0%} | {sh:.0%} | {t:.0f} s |")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())
