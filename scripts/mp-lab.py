#!/usr/bin/env python3
"""Multiplayer-Labor: spielt Multiplayer-Kämpfe automatisch (echtes Spiel, Spielerprofile) und misst,
wie sich ein typischer Spieler schlägt. Daraus entstehen die Werte der Computergegner (MpMatch) und
die Prüfung, ob die Wertung fair ausgeht (game/tests/mp_fairness.gd).

Aufruf (im Hauptordner):
  GODOT=/pfad/zu/godot python3 scripts/mp-lab.py [--levels 5,15,25] [--seeds 6]
      [--profiles anfaenger,durchschnitt,zahlend] [--parallel 4] [--out game/tests/mp_runs.json]

Je Lauf: besiegte Gegner alle 10 Sekunden, Boss besiegt, Zeit bis zum Fallen der Station.
Ausgabe: Übersicht je Level und Profil und vorgeschlagene Werte für die Computergegner.
"""
import argparse, concurrent.futures, json, math, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WAVES, MATCH = 7, 300.0
WAVE_T = MATCH / WAVES
# Stärke der Profile gegenüber einem typischen Spieler (balance_profiles.gd: zahlend ≈ +30 % Kampfkraft)
SKILL = {"anfaenger": 0.8, "durchschnitt": 1.0, "zahlend": 1.3}


def run(godot, level, profile, seed):
    game = os.environ.get("GAME_DIR", os.path.join(ROOT, "game"))
    cmd = [godot, "--headless", "--fixed-fps", "60", "--path", game, "--", "--autotest", "--mp",
           f"--level={level}", f"--seed={seed}", "--pull", f"--profile={profile}"]
    cmd += os.environ.get("LAB_ARGS", "").split()
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=900).stdout
    except subprocess.TimeoutExpired:
        return None
    for line in out.splitlines():
        if line.startswith("MPTEST"):
            v = dict(re.findall(r"(\w+)=(\S+)", line))
            return {"level": level, "profile": profile, "seed": seed, "kills": int(v["kills"]),
                    "bosses": int(v["bosses"]), "secs": float(v["secs"]), "out": v["out"] == "true",
                    "curve": [int(x) for x in v["curve"].split(",") if x], "place": int(v["place"])}
    return None


def wave_stats(runs):
    """Besiegte Gegner je Sekunde und Ausscheiden je Sekunde, je Welle."""
    rate, hazard = [], []
    for w in range(WAVES):
        t0, t1 = w * WAVE_T, (w + 1) * WAVE_T
        k = s = 0.0
        alive = deaths = 0.0
        for r in runs:
            c = [0] + r["curve"]
            end = min(r["secs"], t1)
            if end <= t0:
                continue
            def at(t):
                i = min(int(t / 10), len(c) - 1)
                j = min(i + 1, len(c) - 1)
                f = t / 10 - int(t / 10)
                return c[i] + (c[j] - c[i]) * f
            k += at(end) - at(t0)
            s += end - t0
            alive += end - t0
            if r["out"] and t0 <= r["secs"] < t1:
                deaths += 1
        rate.append(k / s if s else 0.0)
        hazard.append(deaths / alive if alive else 0.0)
    return rate, hazard


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", default="5,15,25,35,45")
    ap.add_argument("--seeds", type=int, default=6)
    ap.add_argument("--profiles", default="durchschnitt,zahlend")
    ap.add_argument("--parallel", type=int, default=4)
    ap.add_argument("--out", default=os.path.join(ROOT, "game", "tests", "mp_runs.json"))
    a = ap.parse_args()
    godot = os.environ.get("GODOT", "godot")
    levels = [int(x) for x in a.levels.split(",")]
    jobs = [(l, p, s) for l in levels for p in a.profiles.split(",") for s in range(1, a.seeds + 1)]
    runs = []
    with concurrent.futures.ThreadPoolExecutor(a.parallel) as ex:
        for r in ex.map(lambda j: run(godot, *j), jobs):
            if r:
                runs.append(r)
                print("  L%-2d %-12s Samen %d: %3d besiegt, Boss %d, %s" % (r["level"], r["profile"], r["seed"], r["kills"], r["bosses"],
                      "fällt bei %d s" % r["secs"] if r["out"] else "hält durch"), flush=True)
    json.dump(runs, open(a.out, "w"), indent=0)
    print("\nLevel Profil        hält durch  Boss  besiegt  Zeit")
    for l in levels:
        for p in a.profiles.split(","):
            rs = [r for r in runs if r["level"] == l and r["profile"] == p]
            if not rs:
                continue
            print("%5d %-12s %9.0f %% %4.0f %% %7.0f %5.0f s" % (l, p, 100 * sum(not r["out"] for r in rs) / len(rs),
                  100 * sum(r["bosses"] > 0 for r in rs) / len(rs), sum(r["kills"] for r in rs) / len(rs), sum(r["secs"] for r in rs) / len(rs)))
    base = [r for r in runs if r["profile"] == "durchschnitt"]
    if base:
        rate, hz = wave_stats(base)
        boss = sum(r["bosses"] > 0 for r in base) / len(base)
        print("\nComputergegner (typischer Spieler = durchschnitt):")
        print("  RATE   =", [round(x, 3) for x in rate])
        print("  HAZARD =", [round(x, 5) for x in hz])
        print("  BOSS_CHANCE =", round(boss, 2))
        strong = [r for r in runs if r["profile"] == "zahlend"]
        if strong:
            r2, h2 = wave_stats(strong)
            b2 = sum(r["bosses"] > 0 for r in strong) / len(strong)
            ln = math.log(SKILL["zahlend"])
            rp = math.log(max(1e-6, sum(r2) / max(1e-6, sum(rate)))) / ln
            hp = -math.log(max(1e-6, (sum(h2) + 1e-4) / (sum(hz) + 1e-4))) / ln
            bp = math.log(max(1e-6, b2 / max(0.01, boss))) / ln
            print("  RATE_POW = %.2f  HAZARD_POW = %.2f  BOSS_POW = %.2f" % (rp, hp, bp))


if __name__ == "__main__":
    main()
