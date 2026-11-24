"""Where does FanTeam publish the scoring (rule version 13)? Tries likely endpoints; then scans tournament ids for
FINISHED UCL contests (needed to check the scoring against real points). Writes data/ref/fanteam_rules_probe.md and
data/ref/scan/ucl_scan.csv. Saves no raw bodies: only status, size and keys that mention points/scoring (public repo).
Guesses only: a 404 means the guess was wrong. Run: python scripts/probe_rules.py <tournament_id> <scan_from> <scan_to> <step>"""
import csv, json, sys, time, urllib.error, urllib.request
from pathlib import Path

B = "https://fanteam-game.api.scoutgg.net"; Q = "bearer[white_label]=fanteam"
tid, a, b, step = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
HDR = {"User-Agent": "Mozilla/5.0"}
UCL = {"RMA", "PSV", "ARS", "BVB", "MCI", "NAP", "FCP", "FEY", "BAR", "PSG", "BAY", "LIV", "INT", "ATM", "JUV", "GAL"}


def fetch(url):
    time.sleep(0.7)
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=40)
        return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:
        return type(e).__name__, b""


def keys_like(x, path="", hits=None):
    hits = [] if hits is None else hits
    if isinstance(x, dict):
        for k, v in x.items():
            p = f"{path}.{k}"
            if any(s in k.lower() for s in ("point", "scor", "rule", "multiplier", "bonus")) and not isinstance(v, (dict, list)):
                hits.append(f"{p} = {str(v)[:60]}")
            keys_like(v, p, hits)
    elif isinstance(x, list) and x:
        keys_like(x[0], path + "[0]", hits)
    return hits


out = ["# FanTeam scoring-rules probe", f"Tournament {tid} (rule version 13)", "", "## Endpoints"]
cands = [f"/tournaments/{tid}/players?format=json&{Q}", f"/rule_versions/13?{Q}", f"/rules/13?{Q}", f"/rule-versions/13?{Q}",
         f"/scoring_rules?{Q}", f"/scoring?{Q}", f"/games/98781?{Q}", f"/match_collections/98781?{Q}",
         f"/tournaments/{tid}/scoring?{Q}", f"/tournaments/{tid}/rule_version?{Q}", f"/white_labels/fanteam?{Q}", f"/config?{Q}",
         f"/sports/football/rules?{Q}", f"/game_rules/football?{Q}"]
for c in cands:
    st, body = fetch(B + c)
    line = f"- `{c.split('?')[0]}` {st}, {len(body)} bytes"
    if st == 200 and body:
        try:
            hits = keys_like(json.loads(body))
            hits = [h for h in hits if "user" not in h.lower() and "name" not in h.lower()][:25]
            line += "\n" + "\n".join(f"  - {h}" for h in hits) if hits else " (no scoring-like keys)"
        except Exception:
            line += " (not JSON)"
    out.append(line)

out += ["", f"## Scan {a}-{b} step {step}: football contests with UCL clubs (finished ones can check the scoring)"]
rows = []
for i in range(a, b + 1, step):
    st, body = fetch(f"{B}/tournaments/{i}?{Q}")
    if st != 200:
        continue
    try:
        d = json.loads(body); t = d["tournament"]
    except Exception:
        continue
    teams = sorted(x.get("abbr", "") for x in (d.get("realTeams") or []))
    if t.get("gameType") != "football":
        continue
    rows.append(dict(id=i, name=t.get("name"), starts=t.get("registrationTime"), status=t.get("status"), round=d.get("round"),
                     rule_version=t.get("ruleVersion"), matches=len(d.get("realMatches") or []), ucl=len(UCL & set(teams)),
                     teams=",".join(teams)))
Path("data/ref/scan").mkdir(parents=True, exist_ok=True)
with open("data/ref/scan/ucl_scan.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["id", "name", "starts", "status", "round", "rule_version", "matches", "ucl", "teams"])
    w.writeheader(); w.writerows(rows)
u = [r for r in rows if r["ucl"] >= 2]
out.append(f"{len(range(a, b + 1, step))} ids tried, {len(rows)} football contests, {len(u)} with 2+ UCL clubs:")
out += [f"- {r['id']} {r['name']} | {r['starts']} | {r['status']} | round {r['round']} | rv {r['rule_version']} | {r['matches']} matches" for r in u]
Path("data/ref/fanteam_rules_probe.md").write_text("\n".join(out) + "\n")
print("\n".join(out))
