"""Probe public web sources for UCL 2026-27 per-player match stats. Reachability only: status, size, top-level keys.
Writes data/ref/web_sources_probe.md. URLs are guesses unless marked; a 404 means a wrong guess, not proof of no data."""
import json, time, urllib.request
URLS = [
    ("UEFA match API (matches list)", "https://match.uefa.com/v5/matches?competitionId=1&seasonYear=2027&limit=20&offset=0&order=ASC"),
    ("UEFA comp stats (player ranking)", "https://compstats.uefa.com/v1/player-ranking?competitionId=1&seasonYear=2027&limit=20&offset=0&stats=goals"),
    ("UEFA site player stats page", "https://www.uefa.com/uefachampionsleague/clubs/players/250092517--julian-ryerson/statistics/"),
    ("UCL Fantasy (gaming.uefa.com) players feed", "https://gaming.uefa.com/en/uclfantasy/services/feeds/players/players_80_en_1.json"),
    ("Sofascore API (UCL seasons)", "https://api.sofascore.com/api/v1/unique-tournament/7/seasons"),
    ("FotMob API (UCL league)", "https://www.fotmob.com/api/leagues?id=42"),
    ("FBref UCL stats page", "https://fbref.com/en/comps/8/Champions-League-Stats"),
    ("Understat (no UCL; control)", "https://understat.com/"),
]
out = ["# Web sources probe " + time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "", "source | status | bytes | head", "---|---|---|---"]
for name, url in URLS:
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json,text/html"}), timeout=30)
        b = r.read(); st = r.status
        try:
            j = json.loads(b); head = "json keys: " + (",".join(list(j)[:12]) if isinstance(j, dict) else "list[%d]" % len(j))
        except Exception:
            head = "html/text"
    except Exception as e:
        st, b, head = getattr(e, "code", "ERR"), b"", str(e)[:80]
    out.append("%s | %s | %d | %s" % (name, st, len(b), head.replace("|", "/")))
    time.sleep(1)
open("data/ref/web_sources_probe.md", "w").write("\n".join(out) + "\n")
print("\n".join(out))
