"""Pull UCL bookmaker prices (The Odds API) for games starting in the next N hours.
Copied from ryanxib/epl.dfs scripts/fetch_props.py (commit efa3cb9) and adapted for UCL (see LOG.md 2026-11-24).

Needs env ODDS_API_KEY (repo secret ODDS_API). The key is SHARED with nba.dfs and epl.dfs: same monthly credits.
Cost = markets returned x regions, per game call. The events list is free. Per game (UCL books, probe 24 Nov 2026):
  anytime scorer, regions us,uk,eu                                    = 3 credits
  shots, shots on target, assists, regions us,eu                      = 6
  assists alternate, tackles alternate, to receive card, regions us,uk = 6
  extra team markets (btts, team totals, alt team totals), us,uk      = 6  (default on; --no-extra to skip)
  h2h + totals for ALL games in one call, uk,eu (incl. Pinnacle)       = 4 per run
  -> about 21 credits per game; a 9-game night about 190, all 18 games about 380.
UCL facts (probe): no Pinnacle or Betfair on player props. Assists main market = fanduel Over 0.5 only.
Tackles = draftkings only. Team totals = fanduel (+ mybookie) only. Saves props too thin: not pulled.
Yes-only / Over-only: probability = 1/price, which INCLUDES the book's margin (flag incl_margin).

PUBLIC REPO: never print the key or a request URL. Errors print the HTTP code and the API's message only.

Raw (never edited): data/raw/props/ucl_<UTC stamp>.json.gz   (owner approved committing raw prices, 24 Nov 2026)
Clean, one file per market in data/clean/props/:
  <market>_latest.csv / <market>_history.csv   one row per game, player, line: p_mean, p_median, p_pinnacle, p_exchange, n_books, books
  team_latest.csv / team_history.csv           no-vig 1X2 and over/under per game
  team_extra_latest.csv / _history.csv         btts, team totals, alternate team totals
Run: python scripts/fetch_props.py [--hours 30] [--no-team] [--no-extra] [--from-raw FILE]
"""
import argparse, gzip, json, os, sys, unicodedata, re
from datetime import datetime, timedelta, timezone
from pathlib import Path
import urllib.error, urllib.parse, urllib.request
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://api.the-odds-api.com/v4/sports/soccer_uefa_champs_league"
OUT = ROOT / "data/clean/props"
CALLS = [  # (markets, regions) per game
    (["player_goal_scorer_anytime"], "us,uk,eu"),
    (["player_shots", "player_shots_on_target", "player_assists"], "us,eu"),
    (["player_assists_alternate", "player_tackles_alternate", "player_to_receive_card"], "us,uk"),
]


# Letters NFKD does not split into base + accent (Ø, ø, Æ, ß, Ł, Đ, ı ...). Without this, Bodø -> "bod".
FOLD = str.maketrans({"Ø": "O", "ø": "o", "Æ": "AE", "æ": "ae", "Œ": "OE", "œ": "oe", "ß": "ss", "Ł": "L", "ł": "l", "Đ": "D", "đ": "d", "ı": "i", "Þ": "Th", "þ": "th"})


def key(name: str) -> str:
    """Accent-insensitive match key: 'Ødegaard' -> 'odegaard'."""
    s = unicodedata.normalize("NFKD", str(name).translate(FOLD)).encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z ]", "", s.replace("-", " ")).split())


def get(path, **p):
    p["apiKey"] = os.environ["ODDS_API_KEY"]
    try:
        with urllib.request.urlopen(f"{BASE}/{path}?{urllib.parse.urlencode(p)}", timeout=60) as r:
            return json.load(r), r.headers.get("x-requests-remaining"), r.headers.get("x-requests-last")
    except urllib.error.HTTPError as e:  # show the API's reason, never the key
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode('utf8', 'ignore')[:200]}") from None


def player_rows(data):
    out, game = [], f"{data['away_team']} @ {data['home_team']}"
    for bk in data.get("bookmakers", []):
        for m in bk.get("markets", []):
            by = {}
            for o in m.get("outcomes", []):
                if bk["key"].startswith("betfair_ex") and o["price"] <= 1.05:
                    continue   # exchange placeholder: no money on it (seen 24 Oct: 1.01 = '99% to score')
                by.setdefault((o.get("description"), o.get("point")), {})[o["name"]] = o["price"]
            for (pl, pt), px in by.items():
                if "Over" in px and "Under" in px:
                    po, pu = 1 / px["Over"], 1 / px["Under"]; p, vig = po / (po + pu), False
                elif "Over" in px:
                    p, vig = 1 / px["Over"], True
                elif "Yes" in px:
                    p, vig = 1 / px["Yes"], "No" not in px
                    if "No" in px:
                        p = p / (p + 1 / px["No"])
                else:
                    continue
                out.append(dict(game=game, home=data["home_team"], away=data["away_team"],
                                start=data["commence_time"], player=pl, key=key(pl), market=m["key"],
                                line=pt, book=bk["key"], p=p, incl_margin=vig))
    return out


def team_rows(games):
    out = []
    for g in games:
        for bk in g.get("bookmakers", []):
            for m in bk.get("markets", []):
                px = {(o["name"], o.get("point")): o["price"] for o in m["outcomes"]}
                inv = {k: 1 / v for k, v in px.items()}; s = sum(inv.values())
                for (nm, pt), v in inv.items():
                    out.append(dict(game=f"{g['away_team']} @ {g['home_team']}", home=g["home_team"],
                                    away=g["away_team"], start=g["commence_time"], market=m["key"],
                                    outcome=nm, line=pt, book=bk["key"], p_novig=v / s))
    if not out:
        return pd.DataFrame()
    d = pd.DataFrame(out)
    return (d.groupby(["game", "home", "away", "start", "market", "outcome", "line"], dropna=False)
            .agg(p_novig=("p_novig", "mean"), n_books=("book", "nunique")).reset_index())


EXTRA = ["btts", "team_totals", "alternate_team_totals"]
EXTRA_REGIONS = "us,uk"   # team totals sit with US books on UCL (probe)


def extra_rows(d, market):
    """Team-level extra markets for one event (22 Nov): btts (Yes/No), team_totals / alternate_team_totals (Over/Under per team and line),
    alternate_totals (Over/Under per line), alternate_spreads (handicap per team), draw_no_bet, double_chance. No-vig within each book, then
    the mean over books. Rows: game, market, who (team or ''), outcome, line, p_novig, n_books."""
    out, game = [], f"{d['away_team']} @ {d['home_team']}"
    for bk in d.get("bookmakers", []):
        for m in bk.get("markets", []):
            if m["key"] != market:
                continue
            groups = {}
            for o in m.get("outcomes", []):
                who = o.get("description") if market.endswith("team_totals") else ""
                line = o.get("point")
                if market == "alternate_spreads":    # the pair is (team +x, other team -x): group by |x| so each pair is normalised
                    groups.setdefault(line if o["name"] == d["home_team"] else (-line if line is not None else None), []).append((o["name"], line, o["price"]))   # pair = (home h, away -h)
                else:
                    groups.setdefault((who, line), []).append((o["name"], who, o["price"]))
            for k, g in groups.items():
                s = sum(1 / x[2] for x in g)
                for nm, extra, pr in g:
                    if market == "alternate_spreads":
                        out.append(dict(game=game, home=d["home_team"], away=d["away_team"], start=d["commence_time"], market=market, who=nm, outcome="Cover",
                                        line=extra, book=bk["key"], p_novig=(1 / pr) / s))
                    else:
                        out.append(dict(game=game, home=d["home_team"], away=d["away_team"], start=d["commence_time"], market=market,
                                        who=k[0] if isinstance(k, tuple) else "", outcome=nm, line=k[1] if isinstance(k, tuple) else k, book=bk["key"], p_novig=(1 / pr) / s))
    return out


def write(df, name, stamp):
    OUT.mkdir(parents=True, exist_ok=True)
    df = df.copy(); df["fetched_utc"] = stamp
    df.round(4).to_csv(OUT / f"{name}_latest.csv", index=False)
    h = OUT / f"{name}_history.csv"
    df.round(4).to_csv(h, mode="a", header=not h.exists(), index=False)


def clean(rows, stamp):
    if not rows:
        print("no player lines (props post about a day before kick-off)"); return
    d = pd.DataFrame(rows)
    for mk, g in d.groupby("market"):
        pin = g[g.book == "pinnacle"].groupby(["game", "key", "line"], dropna=False).p.mean().rename("p_pinnacle")
        exc = g[g.book == "betfair_ex_uk"].groupby(["game", "key", "line"], dropna=False).p.mean().rename("p_exchange")
        a = (g.groupby(["game", "home", "away", "start", "player", "key", "market", "line"], dropna=False)
             .agg(p_mean=("p", "mean"), p_median=("p", "median"), n_books=("book", "nunique"),
                  books=("book", lambda x: ";".join(sorted(set(x)))), incl_margin=("incl_margin", "all"))
             .reset_index().join(pin, on=["game", "key", "line"]).join(exc, on=["game", "key", "line"]))
        write(a, mk, stamp)
        print(f"  {mk}: {len(a)} rows, {a.player.nunique()} players -> data/clean/props/{mk}_latest.csv")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=int, default=30)
    ap.add_argument("--no-team", action="store_true", help="skip h2h/totals (saves 2 credits)")
    ap.add_argument("--no-extra", action="store_true", help="skip btts / team totals (saves about 6 credits per game)")
    ap.add_argument("--from-raw", help="rebuild clean files from a saved raw file: no API call, no credits")
    a = ap.parse_args()
    if a.from_raw:
        raw = json.load(gzip.open(a.from_raw, "rt"))
        stamp = Path(a.from_raw).name.split(".")[0].replace("ucl_", "")
        clean([r for d in raw["games"] for r in player_rows(d)], stamp)
        if raw.get("team"):
            write(team_rows(raw["team"]), "team", stamp)
        return 0
    if not os.environ.get("ODDS_API_KEY"):
        print("ODDS_API_KEY not set (add repo secret ODDS_API)"); return 1
    now = datetime.now(timezone.utc); stamp = now.strftime("%Y%m%dT%H%MZ")
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    win = dict(commenceTimeFrom=now.strftime(fmt), commenceTimeTo=(now + timedelta(hours=a.hours)).strftime(fmt))
    print(f"run {now:%Y-%m-%d %H:%M}Z")
    try:
        events, rem, _ = get("events", dateFormat="iso", **win)
    except Exception as e:
        print(f"events call failed: {e}"); return 1
    print(f"{len(events)} games in the next {a.hours}h; credits left {rem}")
    raw, rows, xrows = {"games": [], "team": [], "extra": []}, [], []
    for ev in events:
        print(f"{ev['away_team']} @ {ev['home_team']}  {ev['commence_time']}")
        merged = None
        for mk, reg in CALLS:
            try:
                d, rem, last = get(f"events/{ev['id']}/odds", regions=reg, markets=",".join(mk),
                                   oddsFormat="decimal", dateFormat="iso")
            except Exception as e:
                print(f"  {','.join(mk)}: FAILED {e}"); continue
            n = len(player_rows(d)); rows += player_rows(d)
            print(f"  {','.join(mk)} ({reg}): {len(d.get('bookmakers', []))} books, {n} prices "
                  f"(used {last}, left {rem})")
            if merged is None:
                merged = d
            else:
                merged["bookmakers"] = merged.get("bookmakers", []) + d.get("bookmakers", [])
        if not a.no_extra:
            try:
                d, rem, last = get(f"events/{ev['id']}/odds", regions=EXTRA_REGIONS, markets=",".join(EXTRA), oddsFormat="decimal", dateFormat="iso")
                raw["extra"].append(d)
                for mk in EXTRA:
                    r = extra_rows(d, mk); xrows += r
                    print(f"  extra {mk}: {len(r)} prices")
                print(f"  extra ({EXTRA_REGIONS}): {len(d.get('bookmakers', []))} books (used {last}, left {rem})")
            except Exception as e:
                print(f"  extra: FAILED {e}")
        if merged:
            raw["games"].append(merged)
    if not a.no_team and events:
        try:
            t, rem, last = get("odds", regions="uk,eu", markets="h2h,totals", oddsFormat="decimal",
                               dateFormat="iso", **win)
            raw["team"] = t; tr = team_rows(t)
            if len(tr):
                write(tr, "team", stamp)
            print(f"team markets: {len(t)} games (used {last}, left {rem})")
        except Exception as e:
            print(f"team markets FAILED {e}")
    if xrows:
        x = pd.DataFrame(xrows)
        x = (x.groupby(["game", "home", "away", "start", "market", "who", "outcome", "line"], dropna=False)
             .agg(p_novig=("p_novig", "mean"), n_books=("book", "nunique")).reset_index())
        write(x, "team_extra", stamp); print(f"team_extra: {len(x)} rows, markets {sorted(x.market.unique())}")
    (ROOT / "data/raw/props").mkdir(parents=True, exist_ok=True)
    with gzip.open(ROOT / f"data/raw/props/ucl_{stamp}.json.gz", "wt") as f:
        json.dump(raw, f)
    clean(rows, stamp)
    print(f"CREDITS LEFT {rem}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
