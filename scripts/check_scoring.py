"""Check the FanTeam scoring table (METHOD.md, from the rules page 24 Nov 2026) against real FanTeam points.
Scores UEFA per-match stats (data/clean/uefa/player_match.csv) with the table and compares with FanTeam pool points
(data/clean/points/ucl_points_md*.csv). Writes data/ref/scoring_check.md and data/clean/points/link_uefa_fanteam.csv.
Linking: club codes mapped by most surname matches; players by accent-folded surname (+ first name if needed) within club.
Not computable from UEFA stats: impact (+-0.3 needs goal times), caused a scoring free kick, penalty miss, fantasy assists
that are not official assists (won penalties, deflections). So residual = FanTeam - model is judged with that in mind."""
import csv, collections, statistics, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from model.names import key

GOAL = {"GOALKEEPER": 8, "DEFENDER": 6, "MIDFIELDER": 5, "FORWARD": 4}
SOT = {"GOALKEEPER": 1.0, "DEFENDER": 0.6, "MIDFIELDER": 0.4, "FORWARD": 0.4}
CS = {"GOALKEEPER": 4, "DEFENDER": 4, "MIDFIELDER": 1, "FORWARD": 0}
POS = {"goalkeeper": "GOALKEEPER", "defender": "DEFENDER", "midfielder": "MIDFIELDER", "forward": "FORWARD"}


def n(x):
    try: return float(x)
    except (TypeError, ValueError): return 0.0


def model_points(u, pos, gc_full):
    """gc_full: opponent's final goals. UEFA per-player goals_conceded is 0 for outfield players (checked 24 Nov), so goals
    conceded on the pitch is only known for players on for the whole match. Others: GC/CS from UEFA value (GK) or None."""
    m = n(u["minutes_played_official"])
    if m <= 0: return None, {}
    gc = gc_full if (u["started"] == "1" and m >= 90) else (n(u["goals_conceded"]) if pos == "GOALKEEPER" else None)
    p = {"app": 1, "60": 1 if m >= 60 else 0, "goal": GOAL[pos] * n(u["goals"]), "assist": 3 * n(u["assists"]),
         "sot": SOT[pos] * max(0.0, n(u["attempts_on_target"]) - n(u["goals"])),   # a goal is not a shot on target
         "cs": CS[pos] if (m >= 60 and gc == 0) else 0,
         "gc": -((gc or 0) // 2) if pos in ("GOALKEEPER", "DEFENDER") else 0,
         "save": 0.5 * n(u["saves"]) if pos == "GOALKEEPER" else 0, "pen_save": 5 * n(u["saves_on_penalty"]) if pos == "GOALKEEPER" else 0,
         "full": 1 if pos in ("MIDFIELDER", "FORWARD") and u["started"] == "1" and m >= 90 else 0,
         "yc": -1 * n(u["yellow_cards"]) if not n(u["red_cards"]) else 0, "rc": -3 * n(u["red_cards"]),
         "og": -2 * n(u["own_goal_conceded"]), "pen_conc": -2 * n(u["penalty_conceded"])}
    p["partial"] = gc is None and CS[pos] > 0      # CS / GC unknown for this row
    return round(sum(v for k, v in p.items() if k != "partial"), 2), p


def main():
    U = list(csv.DictReader(open("data/clean/uefa/player_match.csv")))
    M = {r["id"]: r for r in csv.DictReader(open("data/ref/uefa_matches.csv"))}
    def opp_goals(r):
        m = M[r["match_id"]]
        return n(m["away_goals"]) if r["club"] == m["home"] else n(m["home_goals"])
    out, links = ["# Scoring check: UEFA stats scored with the rules table v FanTeam points", ""], []
    allres = []
    for md in (2, 3, 4):
        F = list(csv.DictReader(open("data/clean/points/ucl_points_md%d.csv" % md)))
        u = [r for r in U if r["md"] == "MD%d" % md and r["name"]]
        # club map: FanTeam code -> UEFA club, by surname overlap
        ukeys = collections.defaultdict(set)
        for r in u: ukeys[r["club"]].add(key(r["name"].split()[-1]))
        votes = collections.Counter()
        for f in F:
            for c, ks in ukeys.items():
                if key(f["name"].split()[-1]) in ks: votes[(f["club"], c)] += 1
        cmap = {}
        for (fc, uc), v in votes.most_common():
            if fc not in cmap and uc not in cmap.values() and v >= 3: cmap[fc] = uc
        # player link inside club
        by_club = collections.defaultdict(list)
        for r in u: by_club[r["club"]].append(r)
        res, unl, played = [], 0, 0
        for f in F:
            if f["status"] != "finished" and n(f["points"]) == 0: continue
            cands = by_club.get(cmap.get(f["club"]), [])
            sk = key(f["name"]); fk = key(f["fname"])
            hit = [r for r in cands if sk and (sk in key(r["name"]) or key(r["name"]) in sk + fk or key(r["name"]) == key(f["fname"] + f["name"]))]
            if len(hit) > 1: hit = [r for r in hit if fk and fk[:3] in key(r["name"])] or hit[:0]
            if len(hit) != 1:
                if n(f["points"]) != 0: unl += 1
                continue
            r = hit[0]; pos = POS[f["position"]]
            mp, parts = model_points(r, pos, opp_goals(r))
            links.append(dict(md=md, fanteam_id=f["player_id"], uefa_id=r["player_id"], fanteam_name=f["name"], uefa_name=r["name"], club=f["club"]))
            if mp is None:
                if n(f["points"]) != 0: res.append((md, f, r, 0.0, n(f["points"]), pos, {}))
                continue
            played += 1
            res.append((md, f, r, mp, n(f["points"]), pos, parts))
        allres += res
        d = [ft - mp for (_, _, _, mp, ft, _, pt) in res if not pt.get("partial")]
        exact = sum(1 for x in d if abs(x) < 0.05); imp = sum(1 for x in d if abs(abs(x) - 0.3) < 0.05)
        out.append("- MD%d: clubs mapped %d/%d; linked players with minutes %d; FanTeam non-zero players not linked %d; "
                   "exact %d, off by exactly 0.3 (impact) %d, other %d" % (md, len(cmap), len({f['club'] for f in F}), played, unl, exact, imp, len(d) - exact - imp))
    full = [x for x in allres if not x[6].get("partial")]
    d = [ft - mp for (_, _, _, mp, ft, _, _) in full]
    ok = sum(1 for x in d if abs(x) < 0.05 or abs(abs(x) - 0.3) < 0.05)
    out += ["", "- ALL (excludes %d GK/DEF/MID rows subbed on or off: clean sheet unknown): %d player-matches; %d (%.0f%%) match the table exactly or within the +-0.3 impact term; mean residual %.2f" % (
        len(allres) - len(full), len(d), ok, 100 * ok / max(1, len(d)), statistics.mean(d) if d else 0), "",
        "## Biggest residuals (FanTeam minus model; impact +-0.3 not modelled)", "",
        "md | player | club | pos | min | started | G | A | SoT | GC | sv | FanTeam | model | diff", "---|---|---|---|---|---|---|---|---|---|---|---|---|---"]
    for md, f, r, mp, ft, pos, _ in sorted(full, key=lambda x: -abs(x[4] - x[3]))[:40]:
        out.append("%d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %.1f | %.1f | %+.1f" % (md, r["name"], f["club"], pos[:3], r["minutes_played_official"],
                   r["started"], r["goals"], r["assists"], r["attempts_on_target"], r["goals_conceded"], r["saves"], ft, mp, ft - mp))
    # residual pattern by size
    buckets = collections.Counter(round(x, 1) for x in d)
    out += ["", "## Residual counts (rounded to 0.1)", "", ", ".join("%+.1f: %d" % (k, v) for k, v in sorted(buckets.items()) if v >= 3)]
    Path("data/ref/scoring_check.md").write_text("\n".join(out) + "\n")
    with open("data/clean/points/link_uefa_fanteam.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(links[0])); w.writeheader(); w.writerows(links)
    print("\n".join(out[:8]))


if __name__ == "__main__":
    main()
