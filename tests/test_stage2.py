"""Stage 2 offline checks. Run: python tests/test_stage2.py (needs committed data: props, pool 1170340, UEFA MD1-4)."""
import importlib.util, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "model"))


def load(name, rel):
    s = importlib.util.spec_from_file_location(name, ROOT / rel); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


def test_scoring_real_rows():
    """Scoring table rebuilds real FanTeam points (rows from data/ref/scoring_check.md, MD2-4)."""
    S = load("scoring", "model/scoring.py")
    # rule arithmetic: FWD 90 min, 2 goals, 5 SoT incl. goals, win = 1+1+8+3x0.4+1+0.3
    assert S.points("FWD", 90, True, goals=2, sot_incl_goals=5, result=1) == 12.5
    # Carlos Forbs MD2: MID 90, 3 assists, 1 SoT; FanTeam 15.7 = model 12.4 + one extra fantasy assist (+3) + win 0.3
    assert S.points("MID", 90, True, assists=4, sot_incl_goals=1, conceded=1, result=1) == 15.7
    assert S.points("DEF", 90, True, conceded=0) == 6.0
    assert S.points("GK", 90, True, conceded=2, saves=4, result=-1) == 1 + 1 - 1 + 2 - 0.3
    assert S.points("MID", 59, True) == 1.0 and S.points("MID", 0, False) == 0.0


def test_projection_contest():
    dp = load("daily_proj", "model/daily_proj.py")
    D = dp.main("1170340")
    pool = pd.read_csv(sorted((ROOT / "data/raw/fanteam").glob("pool_1170340_*.csv"))[-1], encoding="utf-8-sig")
    assert len(D) == len(pool), "a pool player was dropped"
    pr = D[D.xp.notna()]
    parts = [c for c in D if c.startswith("pts_")]
    assert (pr[parts].fillna(0).sum(axis=1) - pr.xp_start).abs().max() < 0.01, "parts do not rebuild xp_start"
    UT = dp.uefa_tables(pd.read_csv(ROOT / "data/clean/uefa/player_match.csv", dtype={"player_id": str}))
    w = pr.p_start + pr.p_sub * (UT["sub_mins"] / pr.mins)
    chk = pr.assign(w=w).groupby("club").apply(lambda g: (g.w * g.lam_goal).sum() - g.team_xg.iloc[0] * (1 - UT["og_share"]))
    assert chk.abs().max() < 0.01, "team goal sums != team xG"
    assert set(pr[pr.fallback == 1].club) == {"FCP", "FEY"}, "fallback should cover exactly the game with no props"
    assert (pr.xp > -1).all() and (pr.xp < 15).all()
    assert not pr.player.str.match(r"^(\w+) \1$").any(), "doubled names"


if __name__ == "__main__":
    test_scoring_real_rows(); print("scoring ok")
    test_projection_contest(); print("projection ok")
