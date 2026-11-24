"""Per-player per-match stats for UCL 2026-27 league-phase matchdays from UEFA public APIs (endpoints found by probe_uefa.py, 24 Nov 2026).
  match list : match.uefa.com/v5/matches?competitionId=1&seasonYear=2027
  lineups    : match.uefa.com/v5/matches/{id}/lineups          (names, positions, starters, bench)
  stats      : matchstats.uefa.com/v2/player-statistics/{id}    (~380 stat names per player; we keep the fantasy ones)
Usage: python scripts/fetch_uefa_stats.py 1,2,3,4
Output: data/clean/uefa/player_match.csv (one row per player per match), data/clean/uefa/pull_report.md
Kept per player: name, club, position, started, and the stats in KEEP. No ages, birth dates or other personal details."""
import csv, json, sys, time, urllib.request
from pathlib import Path

H = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
KEEP = ["minutes_played_official", "played_time", "goals", "assists", "attempts", "attempts_on_target", "attempts_blocked",
        "saves", "saves_on_penalty", "goals_conceded", "clean_sheet", "tackles", "tackles_won", "recovered_ball",
        "clearance_completed", "blocked", "fouls_committed", "fouls_suffered", "offsides", "yellow_cards", "red_cards",
        "own_goal_conceded", "penalty_conceded"]
OUT = Path("data/clean/uefa"); OUT.mkdir(parents=True, exist_ok=True)


def get(url, tries=4):
    for i in range(tries):
        try:
            b = urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=90).read(); time.sleep(0.5)
            return json.loads(b)
        except Exception as e:
            err = e; time.sleep(3 * (i + 1))
    raise err


def main():
    mds = ["MD%s" % x for x in sys.argv[1].split(",")]
    ms, off = [], 0
    while off < 1000:
        page = get("https://match.uefa.com/v5/matches?competitionId=1&seasonYear=2027&limit=100&offset=%d&order=ASC" % off)
        if not page: break
        ms += page; off += 100
    todo = [m for m in ms if (m.get("round") or {}).get("phase") == "TOURNAMENT" and (m.get("matchday") or {}).get("name") in mds
            and m.get("status") == "FINISHED"]
    rep = ["# UEFA player stats pull " + time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "",
           "- %d matches in list; %d finished league-phase matches in %s" % (len(ms), len(todo), ",".join(mds))]
    rows = []
    for m in todo:
        mid = m["id"]; md = m["matchday"]["name"]
        names = {}
        for side in ("homeTeam", "awayTeam"):
            names[m[side]["id"]] = m[side].get("internationalName")
        try:
            lu = get("https://match.uefa.com/v5/matches/%s/lineups" % mid)
            st = get("https://matchstats.uefa.com/v2/player-statistics/%s" % mid)
        except Exception as e:
            rep.append("- %s %s: FAILED %s" % (md, mid, str(e)[:80])); continue
        info = {}
        for side in ("homeTeam", "awayTeam"):
            t = lu.get(side) or {}
            tid = (t.get("team") or {}).get("id")
            for grp, started in (("field", 1), ("bench", 0)):
                for p in t.get(grp) or []:
                    pl = p.get("player") or {}
                    info[str(pl.get("id"))] = dict(name=pl.get("internationalName"), position=pl.get("fieldPosition"),
                                                   team_id=tid, started=started)
        n_stats = 0
        for p in st:
            pid = str(p.get("playerId")); s = {x["name"]: x.get("value") for x in p.get("statistics") or []}
            i = info.get(pid, {})
            r = dict(md=md, match_id=mid, kickoff=(m.get("kickOffTime") or {}).get("dateTime"), player_id=pid,
                     name=i.get("name"), team_id=p.get("teamId"), club=names.get(str(p.get("teamId"))),
                     opponent=[v for k, v in names.items() if k != str(p.get("teamId"))][0] if len(names) == 2 else "",
                     position=i.get("position"), started=i.get("started", ""), in_lineup=int(bool(i)))
            r.update({k: s.get(k, "") for k in KEEP}); rows.append(r); n_stats += 1
        missing = len(set(info) - {str(p.get("playerId")) for p in st})
        rep.append("- %s %s v %s (%s): %d stat rows, %d in lineup without stats" % (md, names.get(m["homeTeam"]["id"]),
                   names.get(m["awayTeam"]["id"]), mid, n_stats, missing))
    with open(OUT / "player_match.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    played = [r for r in rows if str(r["minutes_played_official"]) not in ("", "0")]
    no_name = sum(1 for r in rows if not r["name"])
    rep += ["", "- total rows %d; with minutes > 0: %d; rows without a lineup name: %d" % (len(rows), len(played), no_name)]
    for md in mds:
        sub = [r for r in played if r["md"] == md]
        rep.append("- %s: %d matches, %d players with minutes, %d with saves value, %d with tackles value" % (
            md, len({r["match_id"] for r in sub}), len(sub), sum(1 for r in sub if r["saves"] != ""), sum(1 for r in sub if r["tackles"] != "")))
    open(OUT / "pull_report.md", "w").write("\n".join(rep) + "\n")
    print("\n".join(rep))


if __name__ == "__main__":
    main()
