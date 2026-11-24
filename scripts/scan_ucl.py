"""Find past FanTeam UCL daily contests and pull FanTeam points per player per matchday (no login, public endpoints).
Scan logic adapted from ryanxib/epl.dfs scripts/scan_tournaments.py (commit efa3cb9).

Usage: python scripts/scan_ucl.py START END STEP FINE GWS
  START..END step STEP : coarse scan of tournament ids (base endpoint, ~33 KB each, one call per 0.7 s)
  FINE                 : around each UCL hit, scan +-FINE ids one by one (0 = off)
  GWS                  : matchdays to pull points for, comma list (e.g. 1,2,3,4)
UCL = gameType football and matchCollection.seasonIds contains 2026 (seen on contest 1170340, UCL MD5).
Output (no user names or ids written; public repo):
  data/ref/scan/ucl_scan_<START>_<END>_<STEP>.csv   every football contest found (+ date map rows)
  data/clean/points/ucl_points_md<N>.csv            FanTeam points per player, one row per player per matchday
  data/clean/points/ucl_points_report.md            what was found, coverage per matchday, gaps
"""
import csv, json, sys, time, urllib.error, urllib.request
from pathlib import Path

B = "https://fanteam-game.api.scoutgg.net/tournaments/"
Q = "bearer[white_label]=fanteam"
UCL_SEASON = 2026
DELAY = 0.7


def get(path, raw=False):
    url = B + path + ("&" if "?" in path else "?") + Q
    for attempt in range(6):
        try:
            time.sleep(DELAY)
            r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "ucl-fantasy"}), timeout=60).read()
            return r if raw else json.loads(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(15 * (attempt + 1)); continue
            if e.code in (401, 403, 404):
                return None
            time.sleep(3)
        except Exception:
            time.sleep(3)
    return None


def meta(tid):
    d = get(str(tid))
    if not d or "tournament" not in d:
        return None
    t = d["tournament"]; mc = d.get("matchCollection") or {}
    ms = d.get("realMatches") or []
    return dict(id=tid, name=t.get("name"), game_type=t.get("gameType"), created=t.get("createdAt"),
                starts=t.get("registrationTime"), buy_in=t.get("buyIn"), entrants=d.get("total"),
                seasons=";".join(str(x) for x in (mc.get("seasonIds") or [])),
                gws=";".join(str(x) for x in (mc.get("gameweeks") or [])), matches=len(ms),
                match_ids=";".join(str(m.get("id")) for m in ms),
                kickoffs=";".join(sorted({str(m.get("startTime") or m.get("startAt") or "")[:16] for m in ms})),
                status=";".join(sorted({str(m.get("status")) for m in ms})),
                teams=",".join(sorted(x.get("abbr", "") for x in (d.get("realTeams") or []))))


def is_ucl(r):
    return r and r["game_type"] == "football" and str(UCL_SEASON) in r["seasons"].split(";")


def main():
    a, b, step, fine = (int(x) for x in sys.argv[1:5])
    gws = [int(x) for x in sys.argv[5].split(",")] if len(sys.argv) > 5 else [1, 2, 3, 4]
    seen, rows, log = set(), [], []
    for i in range(a, b + 1, step):
        seen.add(i); r = meta(i)
        if r: rows.append(r)
    hits = [r["id"] for r in rows if is_ucl(r)]
    log.append("- coarse: %d ids, %d found, %d UCL" % (len(range(a, b + 1, step)), len(rows), len(hits)))
    if fine:
        for h in hits:
            for i in range(h - fine, h + fine + 1):
                if i in seen: continue
                seen.add(i); r = meta(i)
                if r and r["game_type"] == "football": rows.append(r)
        log.append("- fine: +-%d around each hit; %d ids tried in total" % (fine, len(seen)))
    out = Path("data/ref/scan"); out.mkdir(parents=True, exist_ok=True)
    cols = list(rows[0]) if rows else ["id"]
    keep = [r for r in rows if r["game_type"] == "football"] + [  # date map: one non-football row per coarse step
        r for r in rows if r["game_type"] != "football" and (r["id"] - a) % step == 0]
    with open(out / ("ucl_scan_%d_%d_%d.csv" % (a, b, step)), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(sorted(keep, key=lambda r: r["id"]))
    ucl = sorted([r for r in rows if is_ucl(r)], key=lambda r: r["id"])
    log.append("- UCL contests found: %d" % len(ucl))
    # per matchday: greedy set of contests that covers the most matches, then pull each pool
    pts = Path("data/clean/points"); pts.mkdir(parents=True, exist_ok=True)
    for gw in gws:
        cands = [r for r in ucl if r["gws"] == str(gw) and "pending" not in r["status"]]  # EPL finished status = "confirmed"
        allm = set(m for r in cands for m in r["match_ids"].split(";") if m)
        chosen, cov = [], set()
        while True:
            best = max(cands, key=lambda r: len(set(r["match_ids"].split(";")) - cov), default=None)
            if not best or not (set(best["match_ids"].split(";")) - cov): break
            chosen.append(best); cov |= set(best["match_ids"].split(";"))
        out_rows = {}
        for r in chosen:
            raw = get(str(r["id"]) + "/players?format=csv", raw=True)
            if not raw:
                log.append("- MD%d: pool %d FAILED" % (gw, r["id"])); continue
            for p in csv.DictReader(raw.decode("utf-8-sig").splitlines()):
                pid = p.get("PlayerID")
                if pid in out_rows: continue
                out_rows[pid] = dict(md=gw, contest=r["id"], player_id=pid, name=p.get("Name"), fname=p.get("FName"),
                                     club=p.get("Club"), position=p.get("Position"), price=p.get("Price"),
                                     lineup=p.get("Lineup"), status=p.get("Status"), points=p.get("Points"),
                                     owned=p.get("Owned"), captained=p.get("Captained"))
        if out_rows:
            with open(pts / ("ucl_points_md%d.csv" % gw), "w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(next(iter(out_rows.values())))); w.writeheader(); w.writerows(out_rows.values())
        played = sum(1 for x in out_rows.values() if x["points"] not in ("", None, "0", "0.0"))
        log.append("- MD%d: %d finished UCL contests, %d matches seen, chosen %s cover %d; %d players, %d with non-zero points"
                   % (gw, len(cands), len(allm), [r["id"] for r in chosen], len(cov), len(out_rows), played))
    with open(pts / "ucl_points_report.md", "w") as fh:
        fh.write("# UCL FanTeam points pull " + time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()) + "\n\n" + "\n".join(log) + "\n\n")
        fh.write("## UCL contests found\n\nid | name | created | kickoffs | gws | matches | entrants\n---|---|---|---|---|---|---\n")
        for r in ucl:
            fh.write("%s | %s | %s | %s | %s | %s | %s\n" % (r["id"], r["name"], r["created"], r["kickoffs"], r["gws"], r["matches"], r["entrants"]))
    print("\n".join(log))


if __name__ == "__main__":
    main()
