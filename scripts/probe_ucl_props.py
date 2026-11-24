"""One-off: what does The Odds API offer for the Champions League? Writes data/ref/ucl_props_probe.md (+ raw json).
Needs env ODDS_API_KEY. Cost: ~1 credit per region for each markets call, markets x regions for each odds call."""
import json, os, sys, urllib.parse, urllib.request, urllib.error
from collections import defaultdict
from pathlib import Path
B = "https://api.the-odds-api.com/v4"
OUT = Path("data/ref"); OUT.mkdir(parents=True, exist_ok=True)
KEY = os.environ["ODDS_API_KEY"]
log = []
def get(path, **p):
    p["apiKey"] = KEY
    try:
        with urllib.request.urlopen(f"{B}/{path}?{urllib.parse.urlencode(p)}", timeout=60) as r:
            return json.load(r), r.headers.get("x-requests-remaining")
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode("utf8", "ignore")[:300]}, None
def w(s=""): log.append(s); print(s)

sports, _ = get("sports", all="true")
ucl = [s for s in sports if "champ" in (s["key"] + s["title"]).lower() and "soccer" in s["key"]]
w("# UCL Odds API probe"); w(f"Sport keys matching: {[(s['key'], s['title'], s['active']) for s in ucl]}")
sk = next((s["key"] for s in ucl if s["key"] == "soccer_uefa_champs_league"), ucl[0]["key"] if ucl else None)
if not sk: sys.exit("no UCL sport key")
ev, rem = get(f"sports/{sk}/events")
w(f"Events listed: {len(ev)} (credits left {rem})")
for e in ev[:20]: w(f"- {e['commence_time']} {e['away_team']} @ {e['home_team']} id={e['id']}")
ev = sorted(ev, key=lambda e: e["commence_time"])
raw = {"events": ev, "markets": {}, "odds": {}}
for e in ev[:2]:
    m, rem = get(f"sports/{sk}/events/{e['id']}/markets", regions="uk,eu,us")
    raw["markets"][e["id"]] = m
    names = defaultdict(list)
    for bk in m.get("bookmakers", []) if isinstance(m, dict) else []:
        for mk in bk["markets"]: names[mk["key"]].append(bk["key"])
    w(f"\n## Markets for {e['away_team']} @ {e['home_team']} ({e['commence_time']}) credits left {rem}")
    for k, v in sorted(names.items()): w(f"- {k}: {len(v)} books: {', '.join(sorted(v))}")
    pm = sorted(k for k in names if k.startswith("player_"))
    if not pm: w("NO player markets listed yet"); continue
    o, rem = get(f"sports/{sk}/events/{e['id']}/odds", regions="uk,eu,us", markets=",".join(pm), oddsFormat="decimal")
    raw["odds"][e["id"]] = o
    w(f"\n### Player market depth (credits left {rem})")
    if "error" in o: w(f"error {o}"); continue
    for mk in pm:
        players, books, lines = set(), set(), set()
        for bk in o.get("bookmakers", []):
            for x in bk["markets"]:
                if x["key"] != mk: continue
                books.add(bk["key"])
                for oc in x["outcomes"]:
                    players.add(oc.get("description") or oc["name"]); lines.add((oc["name"], oc.get("point")))
        w(f"- {mk}: {len(players)} players, books={sorted(books)}, outcome types={sorted({str(l[0]) for l in lines})}, lines={sorted({l[1] for l in lines if l[1] is not None})[:8]}")
(OUT / "ucl_props_probe.md").write_text("\n".join(log))
(OUT / "ucl_props_probe_raw.json").write_text(json.dumps(raw))
