"""Probe UEFA public APIs for UCL 2026-27 per-player per-match stats. Runs in the `uefa` Action (UEFA is blocked here).
1. Match list (match.uefa.com, tested 200 on 24 Nov) -> data/ref/uefa_matches.csv (id, matchday, kickoff, teams, score, status)
2. For one finished match, try candidate endpoints (most are GUESSES) -> data/ref/uefa_probe.md (status, size, structure)
   and a raw sample of each one that answers -> data/ref/uefa_samples/<name>.json
No keys, no personal data. Usage: python scripts/probe_uefa.py [MATCH_ID]"""
import csv, json, sys, time, urllib.request
from pathlib import Path

H = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
REF = Path("data/ref"); SAMP = REF / "uefa_samples"; SAMP.mkdir(parents=True, exist_ok=True)
rep = ["# UEFA API probe " + time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), ""]


def get(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=45)
        b = r.read(); time.sleep(0.5)
        return r.status, b
    except Exception as e:
        return getattr(e, "code", "ERR " + str(e)[:60]), b""


def shape(x, depth=0):
    if depth > 3: return "..."
    if isinstance(x, dict): return {k: shape(v, depth + 1) for k, v in list(x.items())[:40]}
    if isinstance(x, list): return [len(x), shape(x[0], depth + 1)] if x else [0]
    return type(x).__name__


def g(d, *ks):
    for k in ks:
        d = d.get(k) if isinstance(d, dict) else None
    return d


# 1. match list
rows, off = [], 0
while off < 1000:
    st, b = get("https://match.uefa.com/v5/matches?competitionId=1&seasonYear=2027&limit=100&offset=%d&order=ASC" % off)
    if st != 200: rep.append("- match list offset %d: %s" % (off, st)); break
    page = json.loads(b)
    if not page: break
    if off == 0:
        (SAMP / "match_list_first.json").write_text(json.dumps(page[0], indent=1))
    for m in page:
        rows.append(dict(id=m.get("id"), matchday=g(m, "matchday", "name") or g(m, "round", "metaData", "name"),
                         phase=g(m, "round", "phase") or m.get("phase"), kickoff=g(m, "kickOffTime", "dateTime"),
                         home=g(m, "homeTeam", "internationalName"), away=g(m, "awayTeam", "internationalName"),
                         home_goals=g(m, "score", "total", "home"), away_goals=g(m, "score", "total", "away"),
                         status=m.get("status")))
    off += 100
if rows:
    with open(REF / "uefa_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
fin = [r for r in rows if str(r["status"]).upper() in ("FINISHED", "PLAYED")]
rep.append("- match list: %d matches, %d finished; statuses %s" % (len(rows), len(fin), sorted({str(r["status"]) for r in rows})))
mid = sys.argv[1] if len(sys.argv) > 1 else (fin[0]["id"] if fin else None)
rep.append("- probe match: %s %s" % (mid, next(((r["home"], r["away"], r["kickoff"]) for r in rows if str(r["id"]) == str(mid)), "")))

# 2. candidate per-match endpoints (guesses unless noted)
S = "competitionId=1&seasonYear=2027"
STATS = "minutes_played_official,goals,assists,attempts_on_target,tackles_won,saves,yellow_cards,red_cards"
C = [
    ("match", "https://match.uefa.com/v5/matches/%s" % mid),
    ("lineups", "https://match.uefa.com/v5/matches/%s/lineups" % mid),
    ("events", "https://match.uefa.com/v5/matches/%s/events?limit=300&offset=0" % mid),
    ("matchstats_v1_players", "https://matchstats.uefa.com/v1/player-statistics/%s" % mid),
    ("matchstats_v2_players", "https://matchstats.uefa.com/v2/player-statistics/%s" % mid),
    ("matchstats_v1_teams", "https://matchstats.uefa.com/v1/team-statistics/%s" % mid),
    ("compstats_player_stats_match", "https://compstats.uefa.com/v1/player-stats?%s&matchId=%s" % (S, mid)),
    ("compstats_ranking_match", "https://compstats.uefa.com/v1/player-ranking?%s&matchId=%s&limit=50&offset=0&optionalFields=PLAYER,TEAM&stats=%s" % (S, mid, STATS)),
    ("compstats_ranking_season", "https://compstats.uefa.com/v1/player-ranking?%s&limit=50&offset=0&optionalFields=PLAYER,TEAM&stats=%s" % (S, STATS)),
]
rep += ["", "endpoint | status | bytes | items", "---|---|---|---"]
shapes = []
for name, url in C:
    st, b = get(url)
    items = ""
    if st == 200 and b:
        try:
            j = json.loads(b)
            items = ("list %d" % len(j)) if isinstance(j, list) else ("dict: " + ",".join(list(j)[:10]))
            (SAMP / (name + ".json")).write_text(json.dumps(j, indent=1)[:400000])
            shapes.append("### " + name + "\n" + url.split("?")[0] + "\n```\n" + json.dumps(shape(j), indent=1)[:3000] + "\n```")
        except Exception:
            items = "not json"
    rep.append("%s | %s | %d | %s" % (name, st, len(b), items.replace("|", "/")))
open(REF / "uefa_probe.md", "w").write("\n".join(rep) + "\n\n## Shapes\n\n" + "\n\n".join(shapes) + "\n")
print("\n".join(rep))
