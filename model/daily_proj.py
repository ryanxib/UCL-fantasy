"""UCL daily projection for one FanTeam contest.  python model/daily_proj.py CONTEST_ID [--freeze] [--force]
Structure and helpers adapted from ryanxib/epl.dfs model/daily_proj.py (commit efa3cb9): e_floor, lam_from_ladder,
odds_match, safety net, freeze. EPL's FPL-history parts replaced by UEFA MD1-4 data (data/clean/uefa/player_match.csv).

xPts = P(start) x points-if-start + P(sub on) x points-if-sub, then the safety net (non-starter -> replacement).
Sources (PLAN.md stage 2):
  team       score grid from bookmaker team markets (team_lines.py -> score_matrix.py): team xG, P(win/draw/loss),
             P(clean sheet), goals conceded.
  goals      anytime scorer props (mean of books) -> lam = -ln(1-p); FALLBACK (no props): UEFA MD1-4 goals per 90,
             shrunk to the position rate. Then ANCHOR: each team's expected player goals = team xG x (1 - own-goal share).
  assists    assist Over 0.5 props (fanduel + alternates, mean) else UEFA per 90; anchored to team xG x assists-per-goal.
  SoT        props ladder (Poisson mean of the Over lines) else UEFA per 90 x team-xG factor. Points on SoT minus goals.
  minutes    P(start) from the pool Lineup column (map below, INFERRED) + owner overrides. P(60+), P(full match), minutes
             given a start: player's UEFA MD1-4 starts, shrunk to the position average. Sub-on chance: UEFA bench rate.
  GK saves   (opponent expected SoT - opponent xG) x 0.5; SoT per goal from UEFA MD1-4.
  cards      card props x k (k = UEFA yellows per team-game / mean props sum per team) else UEFA position rate.
  impact     +0.3 x P(win) - 0.3 x P(loss), x share of the match played (approximation of 'while on the pitch').
Not modelled (small): own goals, caused penalties / free kicks, penalty misses and saves, GK goals.
Out: data/proj/<contest>_<stamp>.csv, data/proj/<contest>_latest.csv, data/proj/<contest>_warnings.md.
--freeze: copy to data/proj/<contest>_frozen.csv; refused after the contest start time unless --force.
"""
import argparse, glob, json, shutil, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import poisson

R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R / "model"))
from names import key, player_keys, team_key  # noqa: E402
import team_lines as TL, score_matrix as SM, scoring as S  # noqa: E402

# Pool Lineup column -> P(start). INFERRED (FanTeam does not publish this); calibrate in stage 4 reviews.
LINEUP_P = {"confirmed": 1.0, "expected": 0.85, "possible": 0.45, "unexpected": 0.05, "bench": 0.0,
            "injured": 0.0, "suspended": 0.0, "doubtful": 0.3}
SHRINK_MIN = 270          # pseudo-minutes at the position rate (3 full games)
SHRINK_STARTS = 2         # pseudo-starts at the position average for minutes
OG_SHARE = 0.03           # share of goals that are own goals (UEFA MD1-4 measured at run time when possible)


def e_floor(lam, per):
    """E[floor(X / per)] for X ~ Poisson(lam)."""
    k = np.arange(0, 40)
    return float((poisson.pmf(k, lam) * (k // per)).sum())


def lam_from_ladder(g):
    """Poisson mean from Over lines: solve each line, average."""
    out = []
    for line, p in zip(g.line, g.p_mean):
        if not 0.001 < p < 0.999 or pd.isna(line):
            continue
        lo, hi = 1e-4, 15.0
        for _ in range(60):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if 1 - poisson.cdf(np.floor(line), mid) < p else (lo, mid)
        out.append((lo + hi) / 2)
    return float(np.mean(out)) if out else np.nan


def odds_match(df, game, first, last):
    """Rows of one props market for this player: same game, name match on tokens (from epl.dfs)."""
    if df is None or df.empty:
        return None
    g = df[df.game == game]
    if g.empty:
        return g
    f, l = key(first), key(last)
    tok = g.key.str.split()
    if f and l:
        full = g[(tok.str[0] == f.split()[0]) & (tok.str[-1] == l.split()[-1])]
        if len(full): return full
    exact = g[g.key.isin(player_keys(first, last) + ([f] if f and f == l else []))]
    if len(exact): return exact
    if l:
        lo = g[tok.str[-1] == l.split()[-1]]
        if lo.key.nunique() == 1: return lo
        lo = g[g.key.str.contains(r"\b" + l + r"\b", regex=True)]
        if lo.key.nunique() == 1: return lo
    return g.iloc[0:0]


def club_to_odds(ft_teams, odds_teams):
    """FanTeam realTeams name -> Odds API team name: equal key, or all FanTeam tokens inside the odds name (unique)."""
    out = {}
    for abbr, name in ft_teams.items():
        k = team_key(name); tk = set(k.split())
        hit = [o for o in odds_teams if team_key(o) == k] or [o for o in odds_teams if tk <= set(team_key(o).split())]
        if len(hit) == 1: out[abbr] = hit[0]
    return out


def uefa_tables(U):
    """Per-player UEFA MD1-4 rates and position defaults."""
    U = U[U.name.fillna("") != ""].copy()
    for c in ("minutes_played_official", "goals", "assists", "attempts_on_target", "yellow_cards", "red_cards", "started"):
        U[c] = pd.to_numeric(U[c], errors="coerce").fillna(0)
    U["pos"] = U.position.map(S.UEFA_POS)
    pl = U[U.minutes_played_official > 0]
    tot = pl.groupby("pos")[["minutes_played_official", "goals", "assists", "attempts_on_target", "yellow_cards", "red_cards"]].sum()
    rate = {c: (tot[c] / tot.minutes_played_official * 90).to_dict() for c in ("goals", "assists", "attempts_on_target", "yellow_cards", "red_cards")}
    st = pl[pl.started == 1]
    posmin = st.groupby("pos").agg(mins=("minutes_played_official", "mean"),
                                   p60=("minutes_played_official", lambda x: (x >= 61).mean()),     # 60 official can be < 60 full minutes
                                   p_full=("minutes_played_official", lambda x: (x >= 90).mean())).to_dict("index")
    bench = U[(U.started == 0) & (U.in_lineup.astype(str) == "1")]
    p_sub = float((bench.minutes_played_official > 0).mean()) if len(bench) else 0.3
    sub_mins = float(bench[bench.minutes_played_official > 0].minutes_played_official.mean()) if len(bench) else 20.0
    per = {}
    for pid, g in U.groupby("player_id"):
        pos = g.pos.mode().iloc[0] if g.pos.notna().any() else None
        if pos is None: continue
        m = g.minutes_played_official.sum(); s_ = g[g.started == 1]
        d = dict(pos=pos, minutes=m, n_md=len(g), starts=len(s_), apps=int((g.minutes_played_official > 0).sum()))
        for c in ("goals", "assists", "attempts_on_target", "yellow_cards", "red_cards"):
            d[c + "_90"] = (g[c].sum() + rate[c][pos] * SHRINK_MIN / 90) / ((m + SHRINK_MIN) / 90)
        pm = posmin[pos]
        d["mins"] = (s_.minutes_played_official.sum() + pm["mins"] * SHRINK_STARTS) / (len(s_) + SHRINK_STARTS)
        d["p60"] = ((s_.minutes_played_official >= 61).sum() + pm["p60"] * SHRINK_STARTS) / (len(s_) + SHRINK_STARTS)
        d["p_full"] = ((s_.minutes_played_official >= 90).sum() + pm["p_full"] * SHRINK_STARTS) / (len(s_) + SHRINK_STARTS)
        per[str(pid)] = d
    goals = U.goals.sum(); ogs = pd.to_numeric(U.own_goal_conceded, errors="coerce").fillna(0).sum()
    games = U.match_id.nunique()
    return dict(per=per, rate=rate, posmin=posmin, p_sub=p_sub, sub_mins=sub_mins,
                ast_per_goal=float(U.assists.sum() / max(goals, 1)), sot_per_goal=float(U.attempts_on_target.sum() / max(goals, 1)),
                og_share=float(ogs / max(goals + ogs, 1)), yellow_per_team_game=float(U.yellow_cards.sum() / max(2 * games, 1)),
                n_games=int(games), gpg=float((goals + ogs) / max(2 * games, 1)))   # goals per team-game


def link_uefa(pool, U, link_file):
    """FanTeam PlayerID -> UEFA player_id: saved link (MD2-4 check) first, then surname within the mapped club."""
    out = {}
    if link_file.exists():
        L = pd.read_csv(link_file, dtype=str)
        out.update(dict(zip(L.fanteam_id, L.uefa_id)))
    U = U[U.name.fillna("") != ""]
    uk = {c: {key(n).split()[-1] for n in g.name if key(n)} for c, g in U.groupby("club")}
    votes = {}
    for r in pool.itertuples():
        for c, ks in uk.items():
            if key(r.last).split() and key(r.last).split()[-1] in ks: votes[(r.club, c)] = votes.get((r.club, c), 0) + 1
    cmap = {}
    for (fc, uc), v in sorted(votes.items(), key=lambda x: -x[1]):
        if fc not in cmap and uc not in cmap.values() and v >= 3: cmap[fc] = uc
    names = U.drop_duplicates("player_id")[["player_id", "name", "club"]]
    for r in pool.itertuples():
        if str(r.pid) in out: continue
        c = names[names.club == cmap.get(r.club)]
        if c.empty: continue
        sk, fk = key(r.last), key(r.first)
        hit = c[[bool(sk) and (sk in key(n) or key(n) == key(f"{r.first} {r.last}")) for n in c.name]]
        if len(hit) > 1: hit = hit[[bool(fk) and fk[:3] in key(n) for n in hit.name]]
        if len(hit) == 1: out[str(r.pid)] = str(hit.player_id.iloc[0])
    return out, cmap


def main(contest, freeze=False, force=False):
    log = []
    pf = sorted(glob.glob(str(R / f"data/raw/fanteam/pool_{contest}_*.csv")))
    if not pf: sys.exit(f"no pool file for {contest}: run the pool Action (requests/pool.txt)")
    pool = pd.read_csv(pf[-1], encoding="utf-8-sig", dtype={"PlayerID": str})
    pool = pool.rename(columns={"PlayerID": "pid", "FName": "first", "Name": "last", "Club": "club", "Position": "pos_raw", "Price": "price", "Lineup": "lineup"})
    pool["first"] = pool["first"].fillna(""); pool["last"] = pool["last"].fillna("")
    pool["player"] = [l if key(f) == key(l) else f"{f} {l}".strip() for f, l in zip(pool["first"], pool["last"])]   # 'Isco Isco' -> 'Isco'
    pool["pos"] = pool.pos_raw.map(S.FT_POS)
    cj = json.load(open(R / f"data/raw/fanteam/contest_{contest}.json"))
    ft_teams = {t["abbr"]: t["name"] for t in cj["realTeams"]}
    start = min(m["startTime"] for m in cj["realMatches"])
    log.append(f"contest {contest}: pool {Path(pf[-1]).name}, {len(pool)} players, {len(cj['realMatches'])} games, first kick-off {start}")

    # ---- team markets -> score grids
    P = R / "data/clean/props"
    team = pd.read_csv(P / "team_latest.csv"); team = team[team.market != "h2h_lay"]
    lines = TL.from_team_csv(team); lines.round(4).to_csv(R / "data/clean/team_lines.csv", index=False)
    SM.build(); grids = SM.load()
    fetched = str(team.fetched_utc.iloc[0]) if len(team) else "?"
    log.append(f"team markets fetched {fetched}: {len(lines)} games fitted")
    c2o = club_to_odds(ft_teams, sorted(set(lines.home) | set(lines.away)))
    miss = sorted(set(ft_teams) - set(c2o))
    if miss: log.append(f"UNMATCHED CLUB (no team markets; players NOT projected): {miss} -> add to names.TEAM_ALIAS")
    T = {}
    for gname, g in grids.items():
        G = g["grid"]; N = G.shape[0]; i = np.arange(N)
        hx, ax = float((G.sum(1) * i).sum()), float((G.sum(0) * i).sum())
        pw = float(np.tril(G, -1).sum()); pd_ = float(np.trace(G)); pl = float(np.triu(G, 1).sum())
        T[g["home"]] = dict(game=gname, opp=g["away"], xg=hx, xga=ax, p_cs=float(G[:, 0].sum()), p_win=pw, p_loss=pl, ga_dist=G.sum(0))
        T[g["away"]] = dict(game=gname, opp=g["home"], xg=ax, xga=hx, p_cs=float(G[0, :].sum()), p_win=pl, p_loss=pw, ga_dist=G.sum(1))

    # ---- UEFA MD1-4
    U = pd.read_csv(R / "data/clean/uefa/player_match.csv", dtype={"player_id": str})
    UT = uefa_tables(U)
    link, cmap = link_uefa(pool, U, R / "data/clean/points/link_uefa_fanteam.csv")
    log.append(f"UEFA MD1-4: {UT['n_games']} games; assists per goal {UT['ast_per_goal']:.2f}, SoT per goal {UT['sot_per_goal']:.2f}, "
               f"own-goal share {UT['og_share']:.3f}, yellows per team-game {UT['yellow_per_team_game']:.2f}, bench sub-on rate {UT['p_sub']:.2f}")
    log.append(f"UEFA link: {sum(1 for p in pool.pid if p in link)} of {len(pool)} pool players linked")

    # ---- props
    def rd(m):
        f = P / f"{m}_latest.csv"
        return pd.read_csv(f) if f.exists() else None
    ats, ast, asta, sot, card = (rd(m) for m in ("player_goal_scorer_anytime", "player_assists", "player_assists_alternate",
                                                 "player_shots_on_target", "player_to_receive_card"))
    astall = pd.concat([x for x in (ast, asta) if x is not None], ignore_index=True)
    astall = astall[astall.line == 0.5] if len(astall) else astall
    props_fetched = str(ats.fetched_utc.iloc[0]) if ats is not None and len(ats) else "none"
    log.append(f"player props fetched {props_fetched}")

    # ---- overrides
    ov = {}
    of = R / f"data/manual/overrides_{contest}.csv"
    if of.exists():
        for r in pd.read_csv(of).itertuples():
            ov[key(r.player)] = float(r.p_start)
        log.append(f"overrides: {len(ov)} from {of.name}")

    rows = []
    for r in pool.itertuples():
        d = dict(pid=r.pid, player=r.player, club=r.club, pos=r.pos, price=r.price, lineup=r.lineup, flags=[])
        t = T.get(c2o.get(r.club))
        if r.pos is None or t is None:
            d["flags"].append("no game / position"); rows.append(d); continue
        u = UT["per"].get(link.get(r.pid, ""), None)
        pm = UT["posmin"][r.pos]
        ps = LINEUP_P.get(str(r.lineup), 0.3)
        if str(r.lineup) not in LINEUP_P: d["flags"].append(f"lineup '{r.lineup}' unknown")
        if key(r.player) in ov: ps = ov[key(r.player)]; d["flags"].append("override")
        out_ = str(r.lineup) in ("injured", "suspended") and key(r.player) not in ov
        psub = 0.0 if out_ else (1 - ps) * UT["p_sub"] * (0.5 if str(r.lineup) == "unexpected" else 1.0)
        mins = u["mins"] if u else pm["mins"]; p60 = u["p60"] if u else pm["p60"]; pfull = u["p_full"] if u else pm["p_full"]
        mf = mins / 90
        d.update(opp=t["opp"], team_xg=t["xg"], opp_xg=t["xga"], p_start=ps, p_sub=psub, mins=mins, p60=p60, p_full=pfull,
                 uefa_linked=int(u is not None), uefa_apps=u["apps"] if u else 0)
        # goals (per start, before the team anchor)
        pr = odds_match(ats, t["game"], r.first, r.last)
        if pr is not None and len(pr):
            p = float(pr.p_mean.mean()); d["p_anytime"] = p; d["ats_books"] = int(pr.n_books.max())
            d["lam_goal_raw"], d["src_goal"] = -np.log(1 - min(p, 0.95)), "props"
        else:
            rate = u["goals_90"] if u else UT["rate"]["goals"][r.pos]
            d["lam_goal_raw"], d["src_goal"] = rate * mf * t["xg"] / UT["gpg"], ("uefa" if u else "pos_avg")   # scaled to team xG below
        pa = odds_match(astall, t["game"], r.first, r.last) if len(astall) else None
        if pa is not None and len(pa):
            d["lam_ast_raw"], d["src_ast"] = -np.log(1 - min(float(pa.p_mean.mean()), 0.95)), "props"
        else:
            rate = u["assists_90"] if u else UT["rate"]["assists"][r.pos]
            d["lam_ast_raw"], d["src_ast"] = rate * mf * t["xg"] / UT["gpg"], ("uefa" if u else "pos_avg")
        so = odds_match(sot, t["game"], r.first, r.last)
        ls = lam_from_ladder(so) if so is not None and len(so) else np.nan
        if not np.isnan(ls):
            d["lam_sot"], d["src_sot"] = ls, "props"
        else:
            rate = u["attempts_on_target_90"] if u else UT["rate"]["attempts_on_target"][r.pos]
            d["lam_sot"], d["src_sot"] = rate * mf * t["xg"] / UT["gpg"], ("uefa" if u else "pos_avg")
        pc = odds_match(card, t["game"], r.first, r.last)
        d["p_card_raw"] = float(pc.p_mean.mean()) if pc is not None and len(pc) else np.nan
        d["yellow_90"] = u["yellow_cards_90"] if u else UT["rate"]["yellow_cards"][r.pos]
        d["red_90"] = u["red_cards_90"] if u else UT["rate"]["red_cards"][r.pos]
        if d["src_goal"] != "props" and r.pos != "GK": d["flags"].append("fallback goals")
        d["_t"] = t
        rows.append(d)
    D = pd.DataFrame(rows)
    ok = D.get("_t").notna() if "_t" in D else pd.Series(False, index=D.index)

    # ---- team anchors: expected player goals / assists given P(start), P(sub) = team xG targets
    D["fallback"] = 0
    for club, g in D[ok].groupby("club"):
        t = g["_t"].iloc[0]
        w = g.p_start + g.p_sub * (UT["sub_mins"] / g.mins)        # expected share of a 'start' worth of minutes
        tg = t["xg"] * (1 - UT["og_share"]); ta = t["xg"] * UT["ast_per_goal"]
        sg = float((w * g.lam_goal_raw).sum()); sa = float((w * g.lam_ast_raw).sum())
        kg = tg / sg if sg > 0 else 1.0; ka = ta / sa if sa > 0 else 1.0
        D.loc[g.index, "k_goal"], D.loc[g.index, "k_ast"] = kg, ka
        D.loc[g.index, "lam_goal"] = g.lam_goal_raw * kg; D.loc[g.index, "lam_ast"] = g.lam_ast_raw * ka
        if (g.src_goal == "props").sum() == 0: D.loc[g.index, "fallback"] = 1
        if not 0.6 <= kg <= 1.4: log.append(f"WARNING {club}: goal anchor factor {kg:.2f} (props v team xG disagree)")
    # cards calibration k: UEFA yellows per team-game / mean props sum per team (starters weighted)
    cs = D[ok & D.p_card_raw.notna()].groupby("club").apply(lambda g: (g.p_start * g.p_card_raw).sum())
    k_card = UT["yellow_per_team_game"] / float(cs.mean()) if len(cs) and cs.mean() > 0 else np.nan
    log.append(f"card props calibration k = {k_card:.2f} (UEFA yellows per team-game / props sum per team)" if not np.isnan(k_card) else "card props: none")

    # ---- points per player
    out = []
    for i, d in D.iterrows():
        if not ok[i]:
            out.append(d); continue
        t = d["_t"]; pos = d.pos; mf = d.mins / 90
        ev = {}
        ev["appearance"] = S.APPEARANCE + S.MIN60 * d.p60
        ev["goal"] = d.lam_goal * S.GOAL[pos]
        ev["assist"] = d.lam_ast * S.ASSIST
        ev["sot"] = max(d.lam_sot - d.lam_goal, 0) * S.SOT[pos] if pos != "GK" else 0.0
        # clean sheet: needs 60+; P(no goal against in his minutes) ~ P(team CS) ** mf (Poisson in time)
        p_cs_on = t["p_cs"] ** min(mf, 1.0)
        ev["clean_sheet"] = d.p60 * p_cs_on * S.CLEAN_SHEET[pos]
        ev["conceded"] = e_floor(t["xga"] * min(mf, 1.0), 2) * S.CONCEDED_PER_2[pos]
        if pos == "GK":
            ev["saves"] = max(t["xga"] * UT["sot_per_goal"] - t["xga"], 0) * min(mf, 1.0) * S.SAVE
        ev["full_match"] = d.p_full * S.FULL_MATCH[pos]
        py = d.p_card_raw * k_card if not np.isnan(d.p_card_raw) and not np.isnan(k_card) else d.yellow_90 * mf
        ev["cards"] = min(py, 0.9) * S.YELLOW + d.red_90 * mf * (S.RED - S.YELLOW)
        ev["impact"] = min(mf, 1.0) * (t["p_win"] * S.IMPACT_WIN + t["p_loss"] * S.IMPACT_LOSS)
        xs = float(sum(ev.values()))
        sm = UT["sub_mins"] / 90
        sub = S.APPEARANCE + d.lam_goal / max(mf, 0.1) * sm * S.GOAL[pos] + d.lam_ast / max(mf, 0.1) * sm * S.ASSIST + \
            sm * (t["p_win"] * S.IMPACT_WIN + t["p_loss"] * S.IMPACT_LOSS)
        for k_, v in ev.items(): d["pts_" + k_] = v
        d["xp_start"], d["xp_sub"] = xs, sub
        d["xp_own"] = d.p_start * xs + d.p_sub * sub
        out.append(d)
    D = pd.DataFrame(out).drop(columns=["_t"])
    # ---- safety net: a non-starter is replaced by the dearest same-club same-position player at or below his price
    rep = []
    for i, r in D.iterrows():
        if pd.isna(r.get("xp_start")): rep.append(np.nan); continue
        c = D[(D.club == r.club) & (D.pos == r.pos) & (D.price <= r.price) & (D.index != i) & D.xp_start.notna() & (D.p_start >= 0.3)]
        rep.append(float(c.loc[c.price.idxmax()].p_start * c.loc[c.price.idxmax()].xp_start) if len(c) else 0.0)
    D["xp_rep"] = rep
    # starts: own points; no start: replacement (if any) else his sub chance (a non-starter who comes on IS replaced)
    D["xp"] = np.where(D.xp_start.notna(), D.p_start * D.xp_start + (1 - D.p_start) * np.where(D.xp_rep > 0, D.xp_rep, D.p_sub / (1 - D.p_start).clip(lower=1e-9) * D.xp_sub), np.nan)
    D["value"] = D.xp / D.price
    sn = D.xp_rep.notna() & (D.p_start < 0.3) & (D.xp_rep > 0)
    D.loc[sn, "flags"] = D.loc[sn, "flags"].map(lambda x: (x if isinstance(x, list) else []) + ["value via safety net"])
    D["flags"] = D["flags"].map(lambda x: "; ".join(x) if isinstance(x, list) else x)
    D = D.sort_values("xp", ascending=False)

    # ---- checks and warnings
    pr_ = D[D.xp.notna()]
    log.append(f"{len(D)} pool players, {len(pr_)} projected; goals from props {int((pr_.src_goal == 'props').sum())}, "
               f"UEFA {int((pr_.src_goal == 'uefa').sum())}, position average {int((pr_.src_goal == 'pos_avg').sum())}")
    fb = sorted(pr_[pr_.fallback == 1].club.unique())
    if fb: log.append(f"FALLBACK clubs (no player props at all; goals shared by UEFA MD1-4 rates): {fb}")
    starters_noprops = pr_[(pr_.p_start >= 0.8) & (pr_.src_goal != "props") & (pr_.fallback == 0) & (pr_.pos != "GK")]
    if len(starters_noprops):
        log.append(f"expected starters with no anytime price in a priced game ({len(starters_noprops)}): " +
                   ", ".join(f"{a} ({b})" for a, b in zip(starters_noprops.player, starters_noprops.club)))
    team_chk = pr_.assign(w=pr_.p_start + pr_.p_sub * (UT["sub_mins"] / pr_.mins)).groupby("club").apply(
        lambda g: pd.Series(dict(goals=(g.w * g.lam_goal).sum(), team_xg=g.team_xg.iloc[0] * (1 - UT["og_share"]), k_goal=g.k_goal.iloc[0], k_ast=g.k_ast.iloc[0])))
    bad = team_chk[(team_chk.goals - team_chk.team_xg).abs() > 0.01]
    log.append("team sums: player goals = team xG for all clubs" if bad.empty else f"TEAM SUM CHECK FAILED: {bad.index.tolist()}")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%MZ")
    O = R / "data/proj"; O.mkdir(parents=True, exist_ok=True)
    cols = ["pid", "player", "club", "pos", "price", "lineup", "opp", "p_start", "p_sub", "mins", "p60", "p_full", "team_xg", "opp_xg",
            "p_anytime", "src_goal", "lam_goal", "src_ast", "lam_ast", "src_sot", "lam_sot", "pts_appearance", "pts_goal", "pts_assist",
            "pts_sot", "pts_clean_sheet", "pts_conceded", "pts_saves", "pts_full_match", "pts_cards", "pts_impact", "xp_start", "xp_sub",
            "xp_own", "xp_rep", "xp", "value", "fallback", "uefa_linked", "uefa_apps", "k_goal", "k_ast", "flags"]
    D = D[[c for c in cols if c in D]].rename(columns={"flags": "notes"})   # 'flags' clashes with DataFrame.flags
    D.round(4).to_csv(O / f"{contest}_{stamp}.csv", index=False); D.round(4).to_csv(O / f"{contest}_latest.csv", index=False)
    top = D[D.xp.notna()].head(30)[["player", "club", "pos", "price", "p_start", "src_goal", "lam_goal", "xp", "notes"]].round(2)
    txt = "# Projection warnings, contest %s, %s\n\n" % (contest, stamp) + "\n".join("- " + x for x in log) + \
          "\n\n## Team anchors\n\n" + team_chk.round(2).to_string() + "\n\n## Top 30\n\n" + top.to_string(index=False) + "\n"
    (O / f"{contest}_warnings.md").write_text(txt); print(txt)
    if freeze:
        if datetime.now(timezone.utc) > datetime.fromisoformat(start.replace("Z", "+00:00")) and not force:
            sys.exit("after lock: not frozen (use --force only to rebuild a lost file, and log it)")
        shutil.copy(O / f"{contest}_latest.csv", O / f"{contest}_frozen.csv")
        (O / f"{contest}_frozen_at.txt").write_text(stamp + "\n"); print("FROZEN ->", f"{contest}_frozen.csv")
    return D


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("contest"); ap.add_argument("--freeze", action="store_true")
    ap.add_argument("--force", action="store_true"); a = ap.parse_args()
    main(a.contest, a.freeze, a.force)
