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
BUILDING_CARDS_PER_DAY = 10          # je Teamheld: frühere Quartiere je Held (nur noch für --alt)
HERO_CARDS = lambda h: 4 + 4 * h     # für Stufe h -> h+1
HERO_GOLD = lambda h: 60 * h
HERO_MAX = 30
TECH = [100, 200, 350, 550, 800, 1100, 1500, 2000, 2600, 3300]
AMMO = {"rate": (10, 80), "cap": (10, 60), "start": (10, 50), "lever": (5, 150), "count": (3, 500), "gate": (2, 1200)}
BOOSTER_COST = lambda lvl: 200 * lvl
BOOSTER_MAX = 5
DAILY_GOLD = 150 + 100               # Tagesbelohnung (7-Tage-Kalender: 1.050 Gold je Woche) + Gratis-Angebot im Shop
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

# --- Basislager (game/scripts/base_data.gd, save_game.gd base_*) -----------------------------
# Erzeuger: Menge pro Stunde von Stufe 1 bis 10; Ausbau Gold 150 × Stufe × (1 + 0,1 × Nummer),
# ab Stufe 6 dazu Sterne (Stufe − 5); kein Gebäude höher als die Kommandozentrale (01).
PROD = {"01": ("gold", 40, 400), "03": ("cards", 0.5, 5), "07": ("gold", 60, 600),
        "13": ("gems", 2 / 24, 10 / 24), "16": ("stars", 1 / 24, 1 / 8),
        "25": ("gold", 100, 1000), "26": ("cards", 1, 8)}
BOOST = {"18": ("gold", 0.03, 0.15), "22": ("cards", 0.05, 0.25)}
BUILD = {f"{i:02d}": (13 + 2 * (i - 13), 2600 + 400 * (i - 13)) for i in range(13, 31)}   # Level, Gold
HERO_UNLOCK = [0, 0, 1, 2, 2, 3, 4, 5, 7, 10, 13, 16]   # meta_data.gd HERO_UNLOCK, sortiert
HOURS_PER_DAY = 16                    # Erzeuger laufen so viele Stunden am Tag (Lager 8 Std., 2–3× abgeholt)

def bval(v1, v10, lvl):
    return v1 + (v10 - v1) * (lvl - 1) / 9

def bcost(bid, lvl):
    i = int(bid) - 1
    return int(round(150 * lvl * (1 + i * 0.1) / 10) * 10), max(0, lvl - 5)

def champions(done):
    return max(5, sum(1 for u in HERO_UNLOCK if done >= u))


def kills(L, atlas):
    for w in atlas["worlds"]:
        for l in w["levels"]:
            if l["level"] == L:
                return sum(g["count"] for g in l["groups"])
    return 250 + 3 * L


def simulate(n, atlas, gold_mult=1.0, verbose=True, base=True, base_share=1.0):
    gold = 300.0
    cards = 0.0                       # Karten je Teamheld
    hero = 1
    tech = 0
    ammo = {k: 0 for k in AMMO}
    booster = 1
    battles = 0.0
    rows = []
    blv = {}                          # Gebäude -> Stufe
    st = {"base_gold": 0.0, "battle_gold": 0.0, "base_cards": 0.0, "spent_base": 0, "stars_need": 0, "gems": 0.0, "stars": 0.0}
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
        if base:
            ch = champions(done)
            for i in range(1, 13):
                if i <= ch:
                    blv.setdefault(f"{i:02d}", 1)
            reserve = TEAM * HERO_GOLD(hero) if hero < HERO_MAX else 0
            budget = max(0.0, gold - reserve) * base_share
            spent = 0
            while True:
                nxt = next((b for b in sorted(BUILD) if b not in blv), None)
                if nxt and L >= BUILD[nxt][0] and f"{int(nxt) - 1:02d}" in blv and budget - spent >= BUILD[nxt][1]:
                    spent += BUILD[nxt][1]; blv[nxt] = 1; continue
                opts = [(bcost(b, l)[0], b) for b, l in blv.items() if l < 10 and (b == "01" or l < blv["01"])]
                if not opts:
                    break
                c, b = min(opts)
                if budget - spent < c:
                    break
                spent += c; st["stars_need"] += bcost(b, blv[b])[1]; blv[b] += 1
            gold -= spent; st["spent_base"] += spent
        rows.append((L, hero, target_hero(L), int(gold), int(cards), len(blv), (sum(blv.values()) / max(1, len(blv))), st["base_gold"], st["battle_gold"]))
        # Level spielen
        a = attempts(L)
        k = kills(L, atlas)
        gold_battle = (a - 1) * (k * 0.5 * GOLD_PER_KILL + GOLD_LOSS) + k * GOLD_PER_KILL + GOLD_WIN_PER_LEVEL * L + GOLD_WIN_BASE
        gb = 1.0 + (bval(*BOOST["18"][1:], blv["18"]) if base and "18" in blv else 0.0)
        cb = 1.0 + (bval(*BOOST["22"][1:], blv["22"]) if base and "22" in blv else 0.0)
        gold += gold_battle * gold_mult * gb
        st["battle_gold"] += gold_battle * gold_mult * gb
        share = IN_BATTLE / TEAM
        cards += share * (CARDS_WIN(L) + (a - 1) * CARDS_LOSS(L)) * cb
        battles += a
        days_before = (battles - a) / BATTLES_PER_DAY
        days_after = battles / BATTLES_PER_DAY
        gold += (days_after - days_before) * (DAILY_GOLD + WHEEL_GOLD + PASS_GOLD_PER_DAY)
        days = days_after - days_before
        if not base:
            cards += days * BUILDING_CARDS_PER_DAY
        else:
            ch = champions(L)
            for b, lvl in blv.items():
                if b in PROD:
                    item, v1, v10 = PROD[b]
                    amount = bval(v1, v10, lvl) * HOURS_PER_DAY * days
                    if item == "gold":
                        gold += amount; st["base_gold"] += amount
                    elif item == "cards":
                        cards += amount / ch; st["base_cards"] += amount / ch   # zufällig auf alle Helden
                    else:
                        st[item] += amount
    if verbose:
        print("Level | Heldenstufe | Ziel | Gold übrig | Karten übrig | Gebäude | Ø Stufe | Gold aus Basis | Gold aus Kämpfen")
        for L, h, t, g, c, nb, al, bg, kg in rows:
            if L % 5 == 0 or L in (1, 21):
                mark = "✓" if abs(h - t) <= 1 else ("↑" if h > t else "↓")
                print(f"{L:5} | {h:11} | {t:4} {mark} | {g:10} | {c:12} | {nb:7} | {al:7.1f} | {int(bg):14} | {int(kg):16}")
        print(f"Tage gespielt (bei {BATTLES_PER_DAY} Kämpfen/Tag): {battles / BATTLES_PER_DAY:.1f}")
        if base:
            print(f"Ins Basislager gesteckt: {st['spent_base']} Gold, dafür nötige Sterne: {st['stars_need']}, "
                  f"Karten aus der Basis je Held: {st['base_cards']:.0f}, Edelsteine {st['gems']:.0f}, Sterne {st['stars']:.0f}")
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", type=int, default=50)
    ap.add_argument("--atlas", default="")
    ap.add_argument("--gold-mult", type=float, default=1.0)
    ap.add_argument("--alt", action="store_true", help="früheres Spiel: Quartiere je Held statt Basislager")
    ap.add_argument("--battles", type=int, default=BATTLES_PER_DAY, help="Kämpfe pro Tag")
    a = ap.parse_args()
    BATTLES_PER_DAY = a.battles
    atlas = json.load(open(a.atlas)) if a.atlas else {"worlds": []}
    simulate(a.levels, atlas, a.gold_mult, base=not a.alt)
