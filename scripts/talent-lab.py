#!/usr/bin/env python3
"""Talent-Labor: misst, wie viel einzelne Talente im Kampf bringen (Balance-Labor mit --talente).

Aufruf (im Hauptordner):
  GODOT=/pfad/zu/godot python3 scripts/talent-lab.py [--levels 36-40] [--seeds 3] [--profile durchschnitt]
      [--varianten neu:0,neu:5,funkenherz:5,werkzeugkiste:5,bollwerk:5,schwerefeld:5] [--parallel 4]

Jede Variante spielt dieselben Level und Seeds; „neu:0“ ist der Vergleich ohne die vier Talente von Fünkchen, Pip,
Rollo und Nova. Einzelne Varianten setzen nur ihr Talent, die anderen drei bleiben auf 0. Ausgabe: Siegquote,
übriges Schild und Kampfzeit je Variante.
"""
import argparse, concurrent.futures, importlib.util, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("lab", os.path.join(ROOT, "scripts", "balance-lab.py"))
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)
NEW = ["funkenherz", "werkzeugkiste", "bollwerk", "schwerefeld"]


def variant_args(v):
    if v.startswith("neu:"):
        return "neu:" + v[4:]
    tid, lvl = v.split(":")
    return ",".join("%s:%s" % (t, lvl if t == tid else "0") for t in NEW)


def one(godot, level, profile, seed, v):
    os.environ["LAB_ARGS"] = "--talente=" + variant_args(v)
    return v, lab.run(godot, level, profile, seed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", default="36-40")
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--profile", default="durchschnitt")
    ap.add_argument("--varianten", default="neu:0,neu:5," + ",".join(t + ":5" for t in NEW))
    ap.add_argument("--parallel", type=int, default=os.cpu_count() or 4)
    a = ap.parse_args()
    godot = os.environ.get("GODOT", "godot")
    variants = a.varianten.split(",")
    jobs = [(l, s, v) for v in variants for l in lab.parse_levels(a.levels) for s in range(1, a.seeds + 1)]
    res = {v: [] for v in variants}
    # Prozesse statt Threads: LAB_ARGS ist je Lauf verschieden
    with concurrent.futures.ProcessPoolExecutor(a.parallel) as ex:
        futs = [ex.submit(one, godot, l, a.profile, s, v) for l, s, v in jobs]
        for f in concurrent.futures.as_completed(futs):
            v, r = f.result()
            if r:
                res[v].append(r)
            print("fertig %d/%d" % (sum(len(x) for x in res.values()), len(jobs)), file=sys.stderr, flush=True)
    print("| Variante | Kämpfe | Siege | übriges Schild | Kampfzeit |")
    print("|---|---|---|---|---|")
    for v in variants:
        rs = res[v]
        if not rs:
            print("| %s | 0 | – | – | – |" % v)
            continue
        win = sum(r["win"] for r in rs) / len(rs)
        sh = sum(r["shield"] for r in rs) / len(rs)
        tm = sum(r["time"] for r in rs) / len(rs)
        print("| %s | %d | %d %% | %d %% | %d s |" % (v, len(rs), round(win * 100), round(sh * 100), round(tm)))


if __name__ == "__main__":
    main()
