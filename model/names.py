"""Name and club matching across FanTeam (pool) and The Odds API. Accent-insensitive keys.
Copied from ryanxib/epl.dfs model/names.py (commit efa3cb9); FPL matcher removed (no FPL data for UCL)."""
import re, unicodedata

# Odds API full names <-> FanTeam club names. UCL list starts empty: extend when a run prints 'UNMATCHED CLUB'.
# Keys are compared after key(). EPL aliases from epl.dfs kept for the English clubs.
TEAM_ALIAS = {
    "man city": "manchester city", "man utd": "manchester united", "spurs": "tottenham hotspur",
    "tottenham": "tottenham hotspur", "newcastle": "newcastle united",
}


# Letters NFKD does not split into base + accent (Ø, ø, Æ, ß, Ł, Đ, ı ...). Without this, Bodø -> "bod".
FOLD = str.maketrans({"Ø": "O", "ø": "o", "Æ": "AE", "æ": "ae", "Œ": "OE", "œ": "oe", "ß": "ss", "Ł": "L", "ł": "l", "Đ": "D", "đ": "d", "ı": "i", "Þ": "Th", "þ": "th"})


def key(s) -> str:
    s = unicodedata.normalize("NFKD", str(s).translate(FOLD)).encode("ascii", "ignore").decode().lower()
    s = s.replace("&", " and ")
    return " ".join(re.sub(r"[^a-z' ]", " ", s.replace("-", " ")).replace("'", "").split())


def team_key(s) -> str:
    k = key(s)
    k = TEAM_ALIAS.get(k, k)
    return k.replace("afc ", "").replace(" fc", "").strip()


def player_keys(first, last):
    """Keys to try, most specific first: 'first last', 'last', initial + last."""
    f, l = key(first), key(last)
    ks = [f"{f} {l}".strip(), l]
    if f:
        ks.append(f"{f[0]} {l}")
    return [k for k in ks if k]
