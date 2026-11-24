"""Copied from ryanxib/epl.dfs model/team_lines.py (commit efa3cb9), unchanged except this line.
Bookmaker team markets -> expected goals per team per game (Poisson inversion).

Input: data/clean/props/team_latest.csv (fetch_props.py: no-vig h2h home/draw/away and totals over/under per line).
Model: home and away goals are independent Poisson with means lam_h, lam_a (a standard, simple football model;
it slightly under-prices draws). Solve lam_h, lam_a so the model's home-win, draw, away-win and over/under chances
are as close as possible to the market's (least squares).
Out: one row per game: lam_h, lam_a, p_cs_h (= home keeps a clean sheet = P(away scores 0) = exp(-lam_a)), p_cs_a, fit error.
"""
import numpy as np, pandas as pd
from scipy.optimize import minimize
from scipy.stats import poisson

G = np.arange(11)


def probs(lh, la):
    m = np.outer(poisson.pmf(G, lh), poisson.pmf(G, la))
    tot = np.add.outer(G, G)
    return dict(home=np.tril(m, -1).sum(), draw=np.trace(m), away=np.triu(m, 1).sum()), m, tot


def fit(p_home, p_draw, p_away, totals):
    """totals: list of (line, p_over). Returns lam_h, lam_a, rmse."""
    def loss(x):
        lh, la = np.exp(x); r, m, tot = probs(lh, la); e = [r["home"] - p_home, r["draw"] - p_draw, r["away"] - p_away]
        for line, po in totals:
            e.append(m[tot > line].sum() - po)
        return float(np.sum(np.square(e)))
    best = min((minimize(loss, x0, method="Nelder-Mead", options=dict(xatol=1e-6, fatol=1e-10)) for x0 in
                ([0.3, 0.1], [0.5, 0.5], [0.1, 0.3])), key=lambda r: r.fun)
    lh, la = np.exp(best.x)
    return lh, la, float(np.sqrt(best.fun / (3 + len(totals))))


def from_team_csv(t: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (game, home, away, start), g in t.groupby(["game", "home", "away", "start"]):
        h2h = g[g.market == "h2h"].set_index("outcome").p_novig
        if not {home, away, "Draw"} <= set(h2h.index):
            continue
        tot = g[(g.market == "totals") & (g.outcome == "Over")]
        totals = list(zip(tot.line, tot.p_novig))
        lh, la, err = fit(h2h[home], h2h["Draw"], h2h[away], totals)
        rows.append(dict(game=game, home=home, away=away, start=start, lam_h=lh, lam_a=la,
                         p_cs_h=np.exp(-la), p_cs_a=np.exp(-lh), p_h=h2h[home], p_d=h2h['Draw'], p_a=h2h[away],
                         fit_rmse=err, n_totals=len(totals)))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    import sys
    from pathlib import Path
    R = Path(__file__).resolve().parents[1]
    d = from_team_csv(pd.read_csv(R / "data/clean/props/team_latest.csv"))
    d.round(3).to_csv(R / "data/clean/team_lines.csv", index=False)
    print(d.round(2).to_string(index=False))
