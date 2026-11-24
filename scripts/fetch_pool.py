"""Fetch a FanTeam player pool by tournament id (runs in the `pool` Action; FanTeam is blocked from the Claude workspace).
Copied from ryanxib/epl.dfs scripts/fetch_pool.py (commit efa3cb9). UCL change: the contest JSON is SCRUBBED before saving
(public repo): the base endpoint returns the top-20 standings with user names and ids. Rank, score and payout are kept.

python scripts/fetch_pool.py <tournament_id> [<tournament_id> ...]
Endpoint (known pattern): https://fanteam-game.api.scoutgg.net/tournaments/{id}/players?bearer[white_label]=fanteam&format=csv
Out: data/raw/fanteam/pool_<id>_<UTC date>.csv (as served, never edited), contest_<id>.json (rules + prize info as served),
data/ref/contests.csv (one row per contest id: the registry) and data/raw/fanteam/pool_last_run.txt (via the Action).
If the endpoint refuses (auth, 403), the owner sends the pool file instead; daily_proj reads either.
Expected columns (seen on NBA pools): Tournament, PlayerID, Name, FName, Club, Lineup, Position, Price. Football values TBC.
"""
import csv, json, sys, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = "https://fanteam-game.api.scoutgg.net/tournaments/{}/players?bearer[white_label]=fanteam&format=csv"
META = "https://fanteam-game.api.scoutgg.net/tournaments/{}?bearer[white_label]=fanteam"
REG_COLS = ["id", "name", "game_type", "starts", "buy_in", "cost", "currency", "budget", "max_per_club", "captains", "safety_net",
            "entries_per_user", "guaranteed", "entrants", "round", "matches", "teams", "n_players", "pool_file", "pulled_utc"]


KEEP = {"rank", "score", "payout"}   # standings rows: everything else (user, ids, uuid, entry name) is dropped


def scrub(d):
    """Public repo: standings rows (fantasyTeams and similar lists) keep only rank, score, payout. A whitelist, so new
    identity fields FanTeam adds later are dropped too. Tournament, match and club data stay."""
    if isinstance(d, dict):
        out = {}
        for k, v in d.items():
            if k in ("fantasyTeams", "standings", "entries") and isinstance(v, list):
                out[k] = [{kk: vv for kk, vv in e.items() if kk in KEEP} if isinstance(e, dict) else e for e in v]
            else:
                out[k] = scrub(v)
        return out
    if isinstance(d, list):
        return [scrub(x) for x in d]
    return d


def get_meta(t, out):
    """Rules + prize info for one contest: raw JSON kept as served, flat row for the registry. Never stops the pool pull."""
    try:
        req = urllib.request.Request(META.format(t), headers={"User-Agent": "ucl-fantasy"})
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.loads(r.read())
    except Exception as e:
        print(f"{t}: meta FAILED {e} (pool still saved; rules from the screen)"); return {}
    (out / f"contest_{t}.json").write_text(json.dumps(scrub(d), indent=1, ensure_ascii=False))
    x = d.get("tournament") or {}; de = x.get("details") or {}
    return dict(id=t, name=x.get("name"), game_type=x.get("gameType"), starts=x.get("registrationTime"), buy_in=x.get("buyIn"),
                cost=x.get("cost"), currency=x.get("currency"), budget=de.get("budget"), max_per_club=x.get("maxPlayersPerTeam"),
                captains=de.get("captains"), safety_net=de.get("safetyNet"), entries_per_user=x.get("maxFantasyTeamsPerUser"),
                guaranteed=x.get("guaranteedPrizePoolAmount"), entrants=d.get("total"), round=d.get("round"),
                matches=len(d.get("realMatches") or []), teams=",".join(sorted(y.get("abbr", "") for y in (d.get("realTeams") or []))))


def register(row):
    """Upsert one row per contest id in data/ref/contests.csv (the registry of every contest pulled)."""
    f = ROOT / "data/ref/contests.csv"; f.parent.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(f))) if f.exists() else []
    rows = [r for r in rows if r["id"] != str(row["id"])] + [{k: row.get(k, "") for k in REG_COLS}]
    rows.sort(key=lambda r: int(r["id"]))
    with open(f, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=REG_COLS); w.writeheader(); w.writerows(rows)


def main(ids):
    out = ROOT / "data/raw/fanteam"; out.mkdir(parents=True, exist_ok=True)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d"); bad = 0
    for t in ids:
        try:
            req = urllib.request.Request(URL.format(t), headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read().decode("utf8")
        except urllib.error.HTTPError as e:
            print(f"{t}: HTTP {e.code} {e.reason} {e.read().decode('utf8', 'ignore')[:200]}"); bad += 1; continue
        except Exception as e:
            print(f"{t}: FAILED {e}"); bad += 1; continue
        lines = body.strip().splitlines()
        if len(lines) < 2 or "Price" not in lines[0]:
            print(f"{t}: unexpected reply (first line: {lines[0][:200] if lines else 'empty'})"); bad += 1; continue
        p = out / f"pool_{t}_{day}.csv"; p.write_text(body)
        print(f"{t}: {len(lines) - 1} players -> {p.relative_to(ROOT)}; columns: {lines[0]}")
        m = get_meta(t, out)
        register({**m, "id": t, "n_players": len(lines) - 1, "pool_file": str(p.relative_to(ROOT)),
                  "pulled_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")})
        if m:
            print(f"{t}: {m.get('name')} | buy-in {m.get('buy_in')} {m.get('currency')} | budget {m.get('budget')} | max/club {m.get('max_per_club')}"
                  f" | captains {m.get('captains')} | safety net {m.get('safety_net')} | entries/user {m.get('entries_per_user')}"
                  f" | entrants {m.get('entrants')} | matches {m.get('matches')} ({m.get('teams')}) | starts {m.get('starts')}")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: fetch_pool.py <tournament_id> ...")
    sys.exit(main(sys.argv[1:]))
