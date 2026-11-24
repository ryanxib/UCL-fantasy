"""Copied from ryanxib/epl.dfs model/score_matrix.py (commit efa3cb9), unchanged except this line.
Scoreline probabilities per game from ALL bookmaker team prices we have (22 Nov): h2h, every totals line, plus (when pulled with
`props extra=yes`) both-teams-to-score, team totals, alternate totals, draw no bet. NOT used: double chance (overlapping outcomes,
the fetcher's normalisation is wrong for it), alternate spreads (first pull mis-normalised), quarter / whole lines, totals above 4.5
(thin and noisy: one book's Over 6.5 was priced as a coin flip).

Method: start from the independent-Poisson scoreline grid (lam_h, lam_a from model/team_lines.py), then move it the least possible
(maximum entropy, i.e. minimum KL distance) until it reproduces every price. Soft fit (small ridge) because bookmakers disagree a little.
This keeps what Poisson gets wrong visible and fixed: 0-0 and 1-1 draws, both-score, and each team's goal ladder.
Out: data/clean/score_matrix.json  {game: {home, away, lam_h, lam_a, grid 9x9, used: [markets], max_err, worst}}
     data/clean/score_matrix_fit.md  one line per game: constraints used, biggest misses.
Use: from score_matrix import load; M = load()[(home_name, away_name)]['grid']  (rows = home goals, columns = away goals).
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.optimize import minimize
from scipy.stats import poisson

N = 9
I, J = np.meshgrid(np.arange(N), np.arange(N), indexing="ij"); T = I + J
R = Path(__file__).resolve().parents[1]


def over_mask(S, line):
    """Win fraction of an OVER bet on a quantity S (total or team goals) at a half or quarter line; pushes ignored."""
    f = line % 1
    if abs(f - .5) < 1e-9: return (S > line).astype(float)
    if abs(f - .25) < 1e-9: return .5 * (S > line - .25) + .5 * (S > line + .25)      # x.25 = halves at x.0 and x.5
    if abs(f - .75) < 1e-9: return .5 * (S > line - .25) + .5 * (S > line + .25)      # x.75 = halves at x.5 and (x+1).0
    return (S > line).astype(float)


def constraints(g, home, away):
    """List of (label, weight mask over the grid, target, n_books). Fewer books = looser fit."""
    C = []
    # a line is usable only if BOTH sides were quoted (a lone Over is normalised to 1.0 by the fetcher): keep Over rows that have an Under partner
    pair = {(r.market, getattr(r, "who", ""), r.line) for r in g.itertuples() if r.outcome == "Under"}
    g = g[~g.market.isin(["double_chance", "alternate_spreads"])]
    g = g[[not (r.market in ("totals", "alternate_totals", "team_totals", "alternate_team_totals") and r.line == r.line and (abs(r.line % 1 - .5) > 1e-9 or r.line > 4.5)) for r in g.itertuples()]]
    g = g[[(r.outcome != "Over") or (r.market not in ("totals", "alternate_totals", "team_totals", "alternate_team_totals")) or ((r.market, getattr(r, "who", ""), r.line) in pair) for r in g.itertuples()]]
    for r in g.itertuples():
        m, o, ln, p, who = r.market, r.outcome, r.line, r.p_novig, getattr(r, "who", ""); nbk = getattr(r, "n_books", 5)
        if m == "h2h":
            if o == home: C.append(("h2h home", (I > J) * 1.0, p, nbk))
            elif o == away: C.append(("h2h away", (I < J) * 1.0, p, nbk))
            elif o == "Draw": C.append(("h2h draw", (I == J) * 1.0, p, nbk))
        elif m in ("totals", "alternate_totals") and o == "Over" and ln == ln:
            C.append((f"total over {ln}", over_mask(T, ln), p, nbk))
        elif m == "btts" and o == "Yes":
            C.append(("btts yes", ((I > 0) & (J > 0)) * 1.0, p, nbk))
        elif m in ("team_totals", "alternate_team_totals") and o == "Over" and ln == ln:
            if who == home: C.append((f"{home} over {ln}", over_mask(I, ln), p, nbk))
            elif who == away: C.append((f"{away} over {ln}", over_mask(J, ln), p, nbk))
        elif m == "alternate_spreads" and ln == ln and abs(ln % 1 - .5) < 1e-9:
            if who == home: C.append((f"{home} {ln:+g}", ((I + ln) > J) * 1.0, p, nbk))
            elif who == away: C.append((f"{away} {ln:+g}", ((J + ln) > I) * 1.0, p, nbk))
        elif m == "draw_no_bet":
            if o == home: C.append(("dnb home", (1 - p) * (I > J) - p * (I < J), 0.0, nbk))
            elif o == away: C.append(("dnb away", (1 - p) * (I < J) - p * (I > J), 0.0, nbk))
        elif m == "double_chance":
            if o.replace(" or ", "/") .startswith(home) and "Draw" in o: C.append(("dc home/draw", (I >= J) * 1.0, p, nbk))
            elif "Draw" in o and away in o: C.append(("dc away/draw", (I <= J) * 1.0, p, nbk))
            elif home in o and away in o: C.append(("dc home/away", (I != J) * 1.0, p, nbk))
    return C


def fit_game(lh, la, C, ridge=2e-3):
    prior = np.outer(poisson.pmf(np.arange(N), lh), poisson.pmf(np.arange(N), la)); prior /= prior.sum()
    if not C: return prior, 0.0, ""
    nb = [x[3] for x in C]; F = np.array([c[1].ravel() for c in C]); c = np.array([c[2] for c in C]); lp = np.log(prior.ravel() + 1e-300)
    rg = ridge * (5.0 / np.clip(np.array(nb, float), 1, 5))     # fewer books = looser fit
    def dual(th):
        z = lp + F.T @ th; mx = z.max(); w = np.exp(z - mx); Z = w.sum(); p = w / Z
        return mx + np.log(Z) - th @ c + .5 * (rg * th) @ th, F @ p - c + rg * th
    res = minimize(dual, np.zeros(len(C)), jac=True, method="L-BFGS-B")
    z = lp + F.T @ res.x; p = np.exp(z - z.max()); p /= p.sum()
    err = F @ p - c; k = int(np.argmax(np.abs(err)))
    return p.reshape(N, N), float(np.abs(err).max()), f"{C[k][0]} off by {err[k]:+.3f}"


def build(root=R):
    t = pd.read_csv(root / "data/clean/props/team_latest.csv"); t["who"] = ""
    xf = root / "data/clean/props/team_extra_latest.csv"
    if xf.exists(): t = pd.concat([t, pd.read_csv(xf)], ignore_index=True)
    tl = pd.read_csv(root / "data/clean/team_lines.csv"); out, md = {}, []
    for (game, home, away), g in t.groupby(["game", "home", "away"]):
        row = tl[tl.game == game]
        if row.empty: continue
        lh, la = float(row.lam_h.iloc[0]), float(row.lam_a.iloc[0]); C = constraints(g, home, away)
        grid, mx, worst = fit_game(lh, la, C)
        out[game] = dict(home=home, away=away, lam_h=lh, lam_a=la, grid=grid.round(6).tolist(), used=sorted(set(c[0].split(" ")[0] for c in C)), n_constraints=len(C), max_err=round(mx, 4), worst=worst,
                         markets=sorted(g.market.unique()))
        md.append(f"- {game}: {len(C)} prices ({', '.join(sorted(g.market.unique()))}); biggest miss {mx:.3f} ({worst}); mean goals {float((grid.sum(1) * np.arange(N)).sum()):.2f} v {float((grid.sum(0) * np.arange(N)).sum()):.2f} (Poisson fit {lh:.2f} v {la:.2f})")
    (root / "data/clean/score_matrix.json").write_text(json.dumps(out))
    (root / "data/clean/score_matrix_fit.md").write_text("# Score matrix fit (maximum entropy from Poisson prior)\n" + "\n".join(md) + "\n")
    return out


def load(root=R):
    f = root / "data/clean/score_matrix.json"
    d = json.load(open(f)) if f.exists() else {}
    return {k: dict(v, grid=np.array(v["grid"])) for k, v in d.items()}


if __name__ == "__main__":
    o = build(); print(Path(R / "data/clean/score_matrix_fit.md").read_text())
