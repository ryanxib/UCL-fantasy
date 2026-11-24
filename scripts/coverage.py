"""Cheap Odds API coverage check: which books list which UCL markets, per game. No prices.
Cost: events list free + 1 credit per game (the /markets endpoint; probe 24 Nov: 1 credit per call).
Writes data/ref/props_coverage.md (latest + change v previous run) and appends data/ref/props_coverage_history.csv.
Copied pattern from scripts/probe_ucl_props.py. Needs env ODDS_API_KEY. Never prints the key or a URL.
Run: python scripts/coverage.py [--hours 48]"""
import argparse, csv, json, os, sys, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

B = "https://api.the-odds-api.com/v4/sports/soccer_uefa_champs_league"
WATCH = ["player_goal_scorer_anytime", "player_shots", "player_shots_on_target", "player_assists", "player_assists_alternate",
         "player_tackles_alternate", "player_to_receive_card", "player_goalie_saves_alternate", "team_totals", "btts", "h2h", "totals"]
SHORT = {"player_goal_scorer_anytime": "ATS", "player_shots": "shots", "player_shots_on_target": "SoT", "player_assists": "ast",
         "player_assists_alternate": "ast_alt", "player_tackles_alternate": "tkl", "player_to_receive_card": "card",
         "player_goalie_saves_alternate": "saves", "team_totals": "TT", "btts": "btts", "h2h": "1X2", "totals": "tot"}
REF = Path("data/ref"); HIST = REF / "props_coverage_history.csv"


def get(path, **p):
    p["apiKey"] = os.environ["ODDS_API_KEY"]
    try:
        with urllib.request.urlopen(f"{B}/{path}?{urllib.parse.urlencode(p)}", timeout=60) as r:
            return json.load(r), r.headers.get("x-requests-remaining")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode('utf8', 'ignore')[:200]}") from None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--hours", type=int, default=48); a = ap.parse_args()
    if not os.environ.get("ODDS_API_KEY"):
        print("ODDS_API_KEY not set"); return 1
    now = datetime.now(timezone.utc); stamp = now.strftime("%Y-%m-%d %H:%MZ"); fmt = "%Y-%m-%dT%H:%M:%SZ"
    ev, rem = get("events", commenceTimeFrom=now.strftime(fmt), commenceTimeTo=(now + timedelta(hours=a.hours)).strftime(fmt))
    ev = sorted(ev, key=lambda e: e["commence_time"])
    prev = {}
    if HIST.exists():
        rows = list(csv.DictReader(open(HIST)))
        if rows:
            last = max(r["run"] for r in rows)
            prev = {(r["game"], r["market"]): int(r["n_books"]) for r in rows if r["run"] == last}
    new = []
    for e in ev:
        game = f"{e['away_team']} @ {e['home_team']}"
        try:
            m, rem = get(f"events/{e['id']}/markets", regions="us,uk,eu")
        except Exception as x:
            print(f"{game}: FAILED {x}"); continue
        books = {}
        for bk in m.get("bookmakers", []):
            for mk in bk["markets"]:
                books.setdefault(mk["key"], set()).add(bk["key"])
        for mk in WATCH:
            new.append(dict(run=stamp, game=game, start=e["commence_time"], market=mk, n_books=len(books.get(mk, ())),
                            books=";".join(sorted(books.get(mk, ())))))
    REF.mkdir(parents=True, exist_ok=True)
    with open(HIST, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(new[0]) if new else ["run"]); (not HIST.stat().st_size) and w.writeheader(); w.writerows(new)
    out = [f"# UCL props coverage (books listing each market), run {stamp}, credits left {rem}",
           "Change v the previous run in brackets. 0 = market not listed (yet). Player props post about a day before kick-off.", "",
           "| Kick-off UTC | Game | " + " | ".join(SHORT[m] for m in WATCH) + " |", "|---|---|" + "---|" * len(WATCH)]
    for (game, start) in dict.fromkeys((r["game"], r["start"]) for r in new):
        cells = []
        for mk in WATCH:
            n = next(r["n_books"] for r in new if r["game"] == game and r["market"] == mk)
            p = prev.get((game, mk))
            cells.append(f"{n}" + (f" ({n - p:+d})" if p is not None and n != p else ""))
        out.append(f"| {start[5:16].replace('T', ' ')} | {game} | " + " | ".join(cells) + " |")
    (REF / "props_coverage.md").write_text("\n".join(out) + "\n")
    print("\n".join(out)); print(f"CREDITS LEFT {rem}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
