#!/usr/bin/env python3
"""First-passage simulation for an account with rules: which comes first — the profit target,
the daily loss limit or the maximum loss?

Model: every trade wins `rr × risk` with probability `win`, otherwise loses `risk`; trades are
independent; risk is a fixed share of the start balance (100). Rules are checked after every
trade. A path stops at the first event. The generator is seeded, so the same inputs give the
same numbers.

  python3 first_passage.py --win 45 --rr 1.5 --risk 1 --tpd 3 --days 30 --daily 5 --maxl 10 --target 8

This is arithmetic on the numbers you enter. It is not a forecast, not a recommendation to
trade and not investment advice. Real trades are not independent and real rules differ by firm.
Standard library only.
"""
from __future__ import annotations

import argparse
import json
import math
import sys

M = 0xFFFFFFFF


def imul(a: int, b: int) -> int:
    return (a * b) & M


def mulberry32(seed: int):
    a = seed & M

    def rnd() -> float:
        nonlocal a
        a = (a + 0x6D2B79F5) & M
        t = imul(a ^ (a >> 15), 1 | a)
        t = ((t + imul(t ^ (t >> 7), 61 | t)) & M) ^ t
        return ((t ^ (t >> 14)) & M) / 4294967296
    return rnd


def pct(s: list[float], q: float) -> float:
    k = (len(s) - 1) * q
    lo, hi = math.floor(k), math.ceil(k)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def simulate(p: dict) -> dict:
    """Standard view: a path stops at the first of target / daily limit / maximum loss; the balance is held from
    then on and the drawdown is measured up to that moment. The balance cannot go below 0. cont=True keeps trading."""
    rnd = mulberry32(p["seed"])
    win, gain, loss = p["win"] / 100, p["risk"] * p["rr"], p["risk"]
    cont = p.get("cont", False)
    cols = [[0.0] * p["runs"] for _ in range(p["days"])]
    dds = []
    n_pass = n_daily = n_max = n_both = deep = 0
    for r in range(p["runs"]):
        bal = peak = 100.0
        worst = 0.0
        outcome = 0
        stopped = False
        for d in range(p["days"]):
            day_start = bal
            for _ in range(p["tpd"]):
                if stopped:
                    break
                bal += gain if rnd() < win else -loss
                if bal < 0:
                    bal = 0.0
                if bal > peak:
                    peak = bal
                else:
                    x = (peak - bal) / peak * 100
                    if x > worst:
                        worst = x
                if outcome == 0:
                    hit_max = bal <= (peak if p["trail"] else 100) * (1 - p["maxl"] / 100)
                    hit_daily = day_start - bal >= day_start * p["daily"] / 100
                    if hit_max and hit_daily:
                        outcome = 4
                    elif hit_max:
                        outcome = 3
                    elif hit_daily:
                        outcome = 2
                    elif bal >= 100 + p["target"]:
                        outcome = 1
                    if outcome != 0 and not cont:
                        stopped = True
                if bal <= 0:
                    stopped = True
            cols[d][r] = bal
        dds.append(worst)
        deep += worst >= p["dd"]
        n_pass += outcome == 1
        n_daily += outcome == 2
        n_max += outcome == 3
        n_both += outcome == 4
    last = sorted(cols[-1])
    sd = sorted(dds)
    n = p["runs"]
    return {"pass": n_pass / n * 100, "daily": n_daily / n * 100, "max": n_max / n * 100, "both": n_both / n * 100,
            "deep": deep / n * 100, "medianDD": pct(sd, .5), "p95DD": pct(sd, .95), "maxDD": sd[-1],
            "last": [pct(last, q) for q in (.05, .25, .5, .75, .95)]}


def main() -> int:
    ap = argparse.ArgumentParser(description="Which comes first: the profit target or a loss limit?")
    ap.add_argument("--win", type=float, default=45, help="win rate in percent")
    ap.add_argument("--rr", type=float, default=1.5, help="payoff ratio (average win / average loss)")
    ap.add_argument("--risk", type=float, default=1, help="risk per trade, percent of the start balance")
    ap.add_argument("--tpd", type=int, default=3, help="trades per day")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--daily", type=float, default=5, help="daily loss limit, percent of the day's opening balance")
    ap.add_argument("--maxl", type=float, default=10, help="maximum loss, percent")
    ap.add_argument("--trail", action="store_true", help="measure the maximum loss from the peak balance")
    ap.add_argument("--target", type=float, default=8, help="profit target, percent")
    ap.add_argument("--dd", type=float, default=10, help="drawdown depth to watch, percent")
    ap.add_argument("--runs", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--cont", action="store_true", help="keep trading after the first event")
    ap.add_argument("--json", action="store_true")
    p = vars(ap.parse_args())
    as_json = p.pop("json")
    r = simulate(p)
    if as_json:
        print(json.dumps({"inputs": p, "result": r}, indent=2))
        return 0
    print(f"{p['runs']:,} paths · seed {p['seed']}")
    print(f"  target first            {r['pass']:6.1f} %")
    print(f"  daily loss limit first  {r['daily']:6.1f} %")
    print(f"  maximum loss first      {r['max']:6.1f} %")
    print(f"  both limits at once     {r['both']:6.1f} %")
    print(f"  drawdown >= {p['dd']:g}%        {r['deep']:6.1f} %")
    print(f"  median max drawdown     {r['medianDD']:6.1f} %   (95th percentile {r['p95DD']:.1f} %)")
    print("0.0 % means it did not occur in these paths, or occurred below the displayed precision. Not a forecast.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
