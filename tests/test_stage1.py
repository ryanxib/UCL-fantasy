"""Stage 1 offline checks (no API calls, no credits). Run: python tests/test_stage1.py"""
import importlib.util, json, os, re, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, rel):
    s = importlib.util.spec_from_file_location(name, ROOT / rel); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


def test_keys():
    n = load("names", "model/names.py"); fp = load("fp", "scripts/fetch_props.py")
    assert n.team_key("Bodø/Glimt") == "bodo glimt"
    assert n.key("Ødegaard") == fp.key("Ødegaard") == "odegaard"
    assert n.key("Łukasz Fabiański") == "lukasz fabianski"
    assert n.team_key("ŠK Slovan Bratislava") == "sk slovan bratislava"


def test_props_parse_probe():
    """The probe's raw odds parse; every anytime-scorer row has a probability in (0, 1)."""
    fp = load("fp", "scripts/fetch_props.py")
    raw = json.load(open(ROOT / "data/ref/ucl_props_probe_raw.json"))
    rows = [r for o in raw["odds"].values() for r in fp.player_rows(o)]
    ats = [r for r in rows if r["market"] == "player_goal_scorer_anytime"]
    assert len(ats) > 100 and all(0 < r["p"] < 1 for r in ats)
    with tempfile.TemporaryDirectory() as d:
        fp.OUT = Path(d); fp.clean(rows, "TEST")
        assert (Path(d) / "player_goal_scorer_anytime_latest.csv").exists()


def test_pool_scrub():
    p = load("pool", "scripts/fetch_pool.py")
    d = {"tournament": {"name": "UCL Special", "userId": None},
         "fantasyTeams": [{"rank": 1, "score": 80.1, "payout": 100, "userId": 7, "name": "someone",
                           "user": {"name": "someone"}, "extra": {"uuid": "7|abc"}}]}
    s = p.scrub(d)
    assert s["fantasyTeams"] == [{"rank": 1, "score": 80.1, "payout": 100}]
    assert s["tournament"]["name"] == "UCL Special"


def test_no_key_printed():
    """No script prints the key or builds a printed URL with it."""
    for f in (ROOT / "scripts").glob("*.py"):
        t = f.read_text()
        for line in t.splitlines():
            if "print(" in line:   # a print may name the secret, never interpolate it
                assert not re.search(r"\{[^}]*(KEY|apiKey|environ)", line), f"{f.name}: {line.strip()}"


if __name__ == "__main__":
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v(); print("ok", k)
