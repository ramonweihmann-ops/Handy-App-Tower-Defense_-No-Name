#!/usr/bin/env python3
"""Wirtschafts-Simulation: Kann ein Spieler ohne Käufe so schnell aufwerten, wie die
Schwierigkeitskurve annimmt (Balance-Profil „Durchschnitt“)?

Spielt Level 1–N nacheinander durch (mit durchschnittlich mehreren Versuchen ab Level 21),
sammelt Gold, Karten und Tagesbelohnungen und gibt das Gold gierig aus: erst Tech-Baum und
Munition nach Plan, dann Heldenstufen für das Hauptteam. Vergleicht die erreichte Heldenstufe
mit dem Ziel aus game/tests/balance_profiles.gd (1 + (Level-1)/2,5).

Die Werte unten spiegeln game/scripts/meta_data.gd und main.gd (_grant_rewards). Wird dort
etwas geändert, hier mitziehen.   Aufruf: python3 scripts/economy-sim.py [--levels 50]
"""
import argparse, json, math, os

# --- Spielwerte (aus dem Spiel übernommen) ---------------------------------------
GOLD_PER_KILL = 2
GOLD_WIN_PER_LEVEL = 80
GOLD_WIN_BASE = 800
GOLD_LOSS = 400
CARDS_WIN = lambda L: int(5 + 0.55 * L)   # je Held im Kampf
CARDS_LOSS = lambda L: int(5 + 0.55 * L) // 2
BUILDING_CARDS_PER_DAY = 10          # je Teamheld: Basislager, 2x täglich geleert (Stufe 1–2)
HERO_CARDS = lambda h: 4 + 4 * h     # für Stufe h -> h+1
HERO_GOLD = lambda h: 60 * h
HERO_MAX = 30
TECH = [100, 200, 350, 550, 800, 1100, 1500, 2000, 2600, 3300]
AMMO = {"rate": (10, 80), "cap": (10, 60), "start": (10, 50), "lever": (5, 150), "count": (3, 500), "gate": (2, 1200)}
BOOSTER_COST = lambda lvl: 200 * lvl
BOOSTER_MAX = 5
DAILY_GOLD = 150 + 100               # tägliche Belohnung + Gratis-Angebot im Shop
WHEEL_GOLD = 120                     # grober Mittelwert pro Dreh (1x täglich)
PASS_GOLD_PER_DAY = 90               # grob: Missionen -> Pass-Stufen, davon Gold-Anteil

# --- Annahmen zum Spielverhalten ----------------------------------------------------
TEAM = 5                             # Hauptteam, das aufgewertet wird
IN_BATTLE = 4                        # Helden im Kampf
BATTLES_PER_DAY = 10
def attempts(L):                      # Versuche bis zum Sieg (ohne Käufe)
    if L <= 20:
        return 1.1
    return 2.2 if L % 5 == 0 else 1.6

def target_hero(L):                   # Balance-Profil „Durchschnitt“
    return min(HERO_MAX, 1 + int((L - 1) / 2.5))

def ammo_plan(done):                  # Munitions-Stufen laut Profil „Durchschnitt“
    return {"rate": done // 3, "cap": done // 3, "start": done // 4, "lever": done // 5, "count": done // 8, "gate": done // 10}

def kills(L, atlas):
    for w in atlas["worlds"]:
        for l in w["levels"]:
            if l["level"] == L:
                return sum(g["count"] for g in l["groups"])
    return 250 + 3 * L


def simulate(n, atlas, gold_mult=1.0, verbose=True):
    gold = 300.0
    cards = 0.0                       # Karten je Teamheld
    hero = 1
    tech = 0
    ammo = {k: 0 for k in AMMO}
    booster = 1
    battles = 0.0
    rows = []
    for L in range(1, n + 1):
        done = L - 1
        # vor dem Level: Gold ausgeben (Plan-Upgrades zuerst, dann Helden)
        while tech < min(10, int(done * 0.8)) and gold >= TECH[tech]:
            gold -= TECH[tech]; tech += 1
        plan = ammo_plan(done)
        for k, (mx, cost) in AMMO.items():
            while ammo[k] < min(mx, plan[k]) and gold >= cost * (ammo[k] + 1):
                gold -= cost * (ammo[k] + 1); ammo[k] += 1
        while booster < min(BOOSTER_MAX, 1 + done // 5) and gold >= 2 * BOOSTER_COST(booster):
            gold -= 2 * BOOSTER_COST(booster); booster += 1
        while hero < HERO_MAX and cards >= HERO_CARDS(hero) and gold >= TEAM * HERO_GOLD(hero):
            cards -= HERO_CARDS(hero); gold -= TEAM * HERO_GOLD(hero); hero += 1
        rows.append((L, hero, target_hero(L), int(gold), int(cards)))
        # Level spielen
        a = attempts(L)
        k = kills(L, atlas)
        gold_battle = (a - 1) * (k * 0.5 * GOLD_PER_KILL + GOLD_LOSS) + k * GOLD_PER_KILL + GOLD_WIN_PER_LEVEL * L + GOLD_WIN_BASE
        gold += gold_battle * gold_mult
        share = IN_BATTLE / TEAM
        cards += share * (CARDS_WIN(L) + (a - 1) * CARDS_LOSS(L))
        battles += a
        days_before = (battles - a) / BATTLES_PER_DAY
        days_after = battles / BATTLES_PER_DAY
        gold += (days_after - days_before) * (DAILY_GOLD + WHEEL_GOLD + PASS_GOLD_PER_DAY)
        cards += (days_after - days_before) * BUILDING_CARDS_PER_DAY
    if verbose:
        print("Level | Heldenstufe erreicht | Ziel | Gold übrig | Karten übrig (je Held)")
        for L, h, t, g, c in rows:
            if L % 5 == 0 or L in (1, 21):
                mark = "✓" if abs(h - t) <= 1 else ("↑" if h > t else "↓")
                print(f"{L:5} | {h:20} | {t:4} {mark} | {g:10} | {c:8}")
        print(f"Tage gespielt (bei {BATTLES_PER_DAY} Kämpfen/Tag): {battles / BATTLES_PER_DAY:.1f}")
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", type=int, default=50)
    ap.add_argument("--atlas", default="")
    ap.add_argument("--gold-mult", type=float, default=1.0)
    a = ap.parse_args()
    atlas = json.load(open(a.atlas)) if a.atlas else {"worlds": []}
    simulate(a.levels, atlas, a.gold_mult)
