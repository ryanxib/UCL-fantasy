"""Checks the ODDS_API secret without spending credits. The /sports endpoint is free.
Writes data/ref/odds_key_check.md. Never prints the key or the request URL (repo and logs are public)."""
import os, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path
out = Path("data/ref/odds_key_check.md"); out.parent.mkdir(parents=True, exist_ok=True)
key = os.environ.get("ODDS_API_KEY", "")
now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
if not key:
    msg = "MISSING: secret ODDS_API is not set on this repo"
else:
    try:
        with urllib.request.urlopen(f"https://api.the-odds-api.com/v4/sports?apiKey={key}", timeout=30) as r:
            msg = f"OK: key works. Credits left {r.headers.get('x-requests-remaining')}, used {r.headers.get('x-requests-used')}"
    except urllib.error.HTTPError as e:
        msg = f"KEY SET BUT REJECTED: HTTP {e.code}"
    except Exception as e:
        msg = f"ERROR: {type(e).__name__}"
out.write_text(f"# Odds API key check\n{now}: {msg}\n")
print(msg)
