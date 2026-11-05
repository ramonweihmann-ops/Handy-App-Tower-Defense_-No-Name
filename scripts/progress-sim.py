#!/usr/bin/env python3
"""Fortschritts-Simulation über Tage (Balancing Level 21–50, Monetarisierung).

Spielt Tag für Tag: Kämpfe am nächsten offenen Level (Sieg oder Niederlage nach einer
Siegchance), tägliche Quellen (Tägliche Belohnung, Glücksrad, Shop-Gratis, Gratis-Truhe,
Tagesangebot, Battle Pass, Basislager), Aufwerten nach Plan (Tech, Munition, Booster, Basis,
Helden). Drei Spielertypen: ohne Käufe, einmal 5 € (bei Level 21) und monatlich zahlend
(Prime, Battle Pass, ein Edelsteinpaket im Monat).

Siegchance: Das Balance-Labor stimmt die Gegner auf das Profil „Durchschnitt“ ab (Heldenstufe
1 + (Level − 1) / 2,5). Wer genau so stark ist, gewinnt normale Level beim ersten Versuch zu
etwa 65 %, Bosse zu 45 %; jede Heldenstufe mehr oder weniger ist +7 % Schaden. Zahlend (+4 Stufen)
liegt im Labor bei rund 90 % – daraus die Steigung der Kurve.

Werte spiegeln game/scripts/meta_data.gd, base_data.gd und main.gd. VARIANTEN unten probiert
Änderungen aus, ohne das Spiel anzufassen.
Aufruf: python3 scripts/progress-sim.py [--variante ist] [--seeds 40] [--alle]
"""
import argparse, math, random, statistics

# --- Spielwerte (Stand 0.9.2) ----------------------------------------------------------
BASE = dict(
    cards_needed=lambda h: 4 + 4 * h,          # Karten für Heldenstufe h -> h+1
    gold_needed=lambda h: 60 * h,              # Gold je Held
    win_gold=lambda L: 800 + 80 * L,
    loss_gold=400,
    kill_gold=lambda L: 2 * (250 + 3 * L),     # 2 Gold je Gegner, grob Gegnerzahl je Level
    win_cards=lambda L: int(5 + 0.55 * L),     # je Held im Kampf, Niederlage: die Hälfte
    chest_cards=lambda L: 10 + int(1.5 * L),   # Heldentruhe (100 Edelsteine)
    free_chest=lambda L: 10 + int(L / 2),      # Gratis-Truhe 1× am Tag (bis zu)
    shop_gold_free=700,                        # Gold-Shop: 200 + 500 gratis am Tag
    daily_offer_cards=5,                       # Tagesangebot gratis (ein Held)
    base_mult=1.0,                             # Basislager-Ertrag
    hero_max=30,
    farm_below=0.30,
    chest_team=False,                          # Heldentruhe nur für Helden der Aufstellung
    videos=0,                                  # Werbevideos am Tag: Siegbelohnung verdoppeln (nur ohne Werbefrei)
    hq_cap=None,                               # Heldenstufe höchstens hq_cap(Stufe der Kommandozentrale)
    slope_neg=None,                            # Steigung der Siegchance, wenn man hinter dem Plan liegt                           # unter dieser Siegchance lieber sammeln
    phase2_curve=None,                         # Zusatzkosten ab Heldenstufe 10 (Variante)
)
TEAM = 5          # Helden, die man aufwertet (Hauptteam)
IN_BATTLE = 3     # Helden im Kampf
TECH = [100, 200, 350, 550, 800, 1100, 1500, 2000, 2600, 3300]
AMMO = {"rate": (10, 80), "cap": (10, 60), "start": (10, 50), "lever": (5, 150), "count": (3, 500), "gate": (2, 1200)}
HERO_UNLOCK = [0, 0, 1, 2, 2, 3, 4, 5, 7, 10, 13, 16]
# Tägliche Quellen ohne Kämpfe (Mittel je Tag)
DAILY = dict(gold=150 + 106, gems=10 + 3, cards=3.6 + 0.4, stars=0.13)   # Tagesbelohnung + Glücksrad
PASS_PER_DAY = 1.6     # Pass-Stufen je Tag (Missionen + Siege), Mittel aus pass_reward
# Basislager: Erzeuger (Menge je Stunde Stufe 1 -> 10), Bauplatz-Level und -Gold
PROD = {"01": ("gold", 40, 400), "03": ("cards", 0.5, 5), "07": ("gold", 60, 600),
        "13": ("gems", 2 / 24, 10 / 24), "16": ("stars", 1 / 24, 1 / 8), "25": ("gold", 100, 1000), "26": ("cards", 1, 8)}
BUILD = {f"{i:02d}": (13 + 2 * (i - 13), 2600 + 400 * (i - 13)) for i in range(13, 31)}
HOURS = 16    # Erzeuger laufen so viele Stunden am Tag voll (Lager 8 Std., 2× abgeholt)

C_NORMAL = math.log(0.65 / 0.35)
C_BOSS = math.log(0.45 / 0.55)
SLOPE = (math.log(0.9 / 0.1) - C_NORMAL) / 4.0      # je Heldenstufe Vorsprung


def target_hero(L):
    return min(30, 1 + int((L - 1) / 2.5))


def p_win(L, delta, slope_neg=None):
    c = C_BOSS if L % 5 == 0 and L > 20 else C_NORMAL
    if L <= 20:
        c += 0.8                                   # Einstieg: gut schaffbar
    x = c + (slope_neg if (slope_neg and delta < 0) else SLOPE) * delta
    return min(0.98, max(0.02, 1 / (1 + math.exp(-x))))


def bval(v1, v10, lvl):
    return v1 + (v10 - v1) * (lvl - 1) / 9


def bcost(bid, lvl):
    return int(round(150 * lvl * (1 + (int(bid) - 1) * 0.1) / 10) * 10), max(0, lvl - 5)


PROFILES = {
    # Kämpfe/Tag, Startkauf (Edelsteine bei Level 21), Edelsteine/Monat, Prime, Pass-Premium
    "ohne Käufe": dict(battles=10, gems_at21=0, gems_month=0, prime=False, premium=False),
    "einmal 5 €": dict(battles=10, gems_at21=1100, gems_month=0, prime=False, premium=False),
    "monatlich": dict(battles=10, gems_at21=0, gems_month=2400, prime=True, premium=True),
}


def simulate(V, prof, seed, levels=50, days_max=400):
    rnd = random.Random(seed)
    s = dict(gold=300.0, gems=100.0, stars=1.0, cards=0.0, hero=1, tech=0, booster=1, L=1)
    ammo = {k: 0 for k in AMMO}
    blv = {}
    log = {}           # Level -> [Versuche, Tag des Siegs, Vorsprung je Versuch …]
    farms = {}         # Welt -> Kämpfe zum Sammeln (geschaffte Level noch einmal)
    stuck = {}         # Welt -> Tage ohne neues Level
    bought21 = False
    cards_need = V["cards_needed"]
    gold_need = V["gold_needed"]
    extra = V["phase2_curve"] or (lambda h: (0, 0))

    def champions():
        return max(5, sum(1 for u in HERO_UNLOCK if s["L"] - 1 >= u))

    def to_team(n):     # zufällige Karten: nur der Anteil, der beim Hauptteam landet
        return n * min(1.0, TEAM / champions())

    def spend():
        done = s["L"] - 1
        while s["tech"] < min(10, int(done * 0.8)) and s["gold"] >= TECH[s["tech"]]:
            s["gold"] -= TECH[s["tech"]]; s["tech"] += 1
        plan = {"rate": done // 3, "cap": done // 3, "start": done // 4, "lever": done // 5, "count": done // 8, "gate": done // 10}
        for k, (mx, cost) in AMMO.items():
            while ammo[k] < min(mx, plan[k]) and s["gold"] >= cost * (ammo[k] + 1):
                s["gold"] -= cost * (ammo[k] + 1); ammo[k] += 1
        while s["booster"] < min(5, 1 + done // 5) and s["gold"] >= 2 * 200 * s["booster"]:
            s["gold"] -= 2 * 200 * s["booster"]; s["booster"] += 1
        # Edelsteine: Heldentruhen (100 Edelsteine)
        while s["gems"] >= 100:
            s["gems"] -= 100
            n = V["chest_cards"](s["L"])
            s["cards"] += n if V["chest_team"] else to_team(n)
        while s["hero"] < V["hero_max"]:
            h = s["hero"]
            if V["hq_cap"] and h >= V["hq_cap"](blv.get("01", 1)):
                break
            ec, eg = extra(h)
            nc, ng = TEAM * (cards_need(h) + ec), TEAM * (gold_need(h) + eg)
            if s["cards"] >= nc and s["gold"] >= ng:
                s["cards"] -= nc; s["gold"] -= ng; s["hero"] += 1
            else:
                break
        # Basislager mit dem Gold, das für die nächste Heldenstufe nicht gebraucht wird
        ch = champions()
        for i in range(1, 13):
            if i <= ch:
                blv.setdefault(f"{i:02d}", 1)
        h = s["hero"]
        reserve = TEAM * (gold_need(h) + extra(h)[1]) if h < V["hero_max"] else 0
        budget = max(0.0, s["gold"] - reserve)
        while True:
            nxt = next((b for b in sorted(BUILD) if b not in blv), None)
            if nxt and s["L"] >= BUILD[nxt][0] and f"{int(nxt) - 1:02d}" in blv and budget >= BUILD[nxt][1]:
                budget -= BUILD[nxt][1]; s["gold"] -= BUILD[nxt][1]; blv[nxt] = 1; continue
            opts = [(bcost(b, l), b) for b, l in blv.items() if l < 10 and (b == "01" or l < blv["01"])]
            if V["hq_cap"] and s["hero"] >= V["hq_cap"](blv["01"]) and blv["01"] < 10:
                opts = [(bcost("01", blv["01"]), "01")]
            if not opts:
                break
            (c, st), b = min(opts)
            if budget < c or s["stars"] < st:
                break
            budget -= c; s["gold"] -= c; s["stars"] -= st; blv[b] += 1

    day = 0
    while s["L"] <= levels and day < days_max:
        day += 1
        L = s["L"]
        # tägliche Quellen
        s["gold"] += DAILY["gold"] + V["shop_gold_free"]
        s["gems"] += DAILY["gems"]
        s["stars"] += DAILY["stars"]
        s["cards"] += to_team(DAILY["cards"] + 0.75 * V["free_chest"](L)) + V["daily_offer_cards"] * min(1.0, TEAM / champions())
        pl = PASS_PER_DAY * (2 if prof["premium"] else 1)
        lvlf = 1 + L // 10
        s["gold"] += pl / 3 * 150 * lvlf; s["gems"] += pl / 3 * 10 * lvlf; s["cards"] += to_team(pl / 6 * 4 * lvlf); s["stars"] += pl / 6 * lvlf
        if prof["gems_month"] and L >= 21:
            s["gems"] += prof["gems_month"] / 30      # Monatspaket, über den Monat verteilt ausgegeben
        if prof["gems_at21"] and L >= 21 and not bought21:
            s["gems"] += prof["gems_at21"]; bought21 = True
        for b, lvl in blv.items():
            if b in PROD:
                item, v1, v10 = PROD[b]
                a = bval(v1, v10, lvl) * HOURS * V["base_mult"]
                if item == "cards":
                    s["cards"] += to_team(a)
                else:
                    s[item] += a
        # Kämpfe: das nächste offene Level; ist es gerade aussichtslos, ein geschafftes
        # Level noch einmal fahren (Karten und Gold sammeln)
        won_today = False
        videos = V["videos"]   # mit Werbefrei/Prime ohne Video, sonst per Video
        for _ in range(prof["battles"]):
            if s["L"] > levels:
                break
            spend()
            L = s["L"]
            bonus = (0.7 if prof["prime"] else 0.0)
            delta = s["hero"] - target_hero(L) + bonus
            p = p_win(L, delta, V["slope_neg"])
            if p < V["farm_below"] and L > 21:
                F = L - 1 if (L - 1) % 5 else L - 2         # Wiederholen: lieber ein normales Level
                pf = p_win(F, s["hero"] - target_hero(F) + bonus, V["slope_neg"])
                fw = rnd.random() < pf
                s["gold"] += V["kill_gold"](F) * (1.0 if fw else 0.5) + (V["win_gold"](F) if fw else V["loss_gold"])
                s["cards"] += IN_BATTLE * V["win_cards"](F) * (1 if fw else 0.5)
                s["stars"] += 1 if fw else 0
                farms[(L - 1) // 10] = farms.get((L - 1) // 10, 0) + 1
                continue
            won = rnd.random() < p
            log.setdefault(L, [0, 0])[0] += 1
            dbl = 2 if (won and videos > 0) else 1
            if dbl == 2:
                videos -= 1
            s["gold"] += V["kill_gold"](L) * (1.0 if won else 0.5) + (V["win_gold"](L) * dbl if won else V["loss_gold"])
            c = V["win_cards"](L) * (dbl if won else 0.5)
            s["cards"] += IN_BATTLE * c        # alle drei Helden im Kampf gehören zum Hauptteam
            log[L].append(s["hero"] - target_hero(L))
            if won:
                s["stars"] += 3
                log[L][1] = day
                s["L"] += 1
                won_today = True
        if not won_today and s["L"] > 21:
            stuck[(s["L"] - 1) // 10] = stuck.get((s["L"] - 1) // 10, 0) + 1
    s["farms"] = farms; s["stuck"] = stuck
    return log, day, s


def summarize(V, prof, seeds):
    days = {k: [] for k in (21, 30, 40, 50)}
    att = {}
    finish = []
    farm, stk = {}, {}
    for sd in range(seeds):
        log, day, s = simulate(V, prof, sd)
        for k in days:
            if k in log and log[k][1]:
                days[k].append(log[k][1])
        for L, rec in log.items():
            a = rec[0]
            att.setdefault(L, []).append(a)
        finish.append(s["hero"])
        for w, n in s["farms"].items():
            farm.setdefault(w, []).append(n)
        for w, n in s["stuck"].items():
            stk.setdefault(w, []).append(n)
    med = lambda xs: statistics.median(xs) if xs else float("nan")
    world = {}
    for w0 in (21, 31, 41):
        n = [statistics.mean(att[L]) for L in range(w0, w0 + 10) if L in att and L % 5]
        b = [statistics.mean(att[L]) for L in range(w0, w0 + 10) if L in att and L % 5 == 0]
        w = (w0 - 1) // 10
        world[w0] = (statistics.mean(n) if n else 0, statistics.mean(b) if b else 0,
                     max(max(att[L]) for L in range(w0, w0 + 10) if L in att),
                     sum(farm.get(w, [])) / seeds, sum(stk.get(w, [])) / seeds)
    return {k: med(v) for k, v in days.items()}, world


VARIANTEN = {
    "ist": {},
}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--variante", default="ist")
    ap.add_argument("--seeds", type=int, default=40)
    ap.add_argument("--alle", action="store_true")
    a = ap.parse_args()
    names = list(VARIANTEN) if a.alle else [a.variante]
    for name in names:
        V = dict(BASE); V.update(VARIANTEN[name])
        print(f"== Variante {name}")
        print("Spielertyp     | Tag L21 | L30 | L40 | L50 | je Welt 21–30 · 31–40 · 41–50: Versuche normal/Boss, Sammelkämpfe, Tage ohne neues Level")
        for pn, prof in PROFILES.items():
            d, w = summarize(V, prof, a.seeds)
            ws = " · ".join(f"{w[k][0]:.1f}/{w[k][1]:.1f} S{w[k][3]:.0f} T{w[k][4]:.1f}" for k in (21, 31, 41))
            print(f"{pn:14} | {d[21]:7.0f} | {d[30]:3.0f} | {d[40]:3.0f} | {d[50]:3.0f} | {ws}")
