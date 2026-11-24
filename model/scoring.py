"""FanTeam football scoring, CONFIRMED for UCL 24 Nov 2026 (rules page screenshots + data check: METHOD.md,
data/manual/fanteam_rules_2026-11-24.md, data/ref/scoring_check.md). One place for the table: used by daily_proj and tests."""
POS = ("GK", "DEF", "MID", "FWD")
APPEARANCE = 1
MIN60 = 1                      # extra, 60 FULL minutes
GOAL = {"GK": 8, "DEF": 6, "MID": 5, "FWD": 4}
ASSIST = 3
CLEAN_SHEET = {"GK": 4, "DEF": 4, "MID": 1, "FWD": 0}          # needs 60+ min on pitch
CONCEDED_PER_2 = {"GK": -1, "DEF": -1, "MID": 0, "FWD": 0}     # -1 per 2 goals conceded while on pitch
SOT = {"GK": 1.0, "DEF": 0.6, "MID": 0.4, "FWD": 0.4}           # a goal is NOT also a shot on target
SAVE = 0.5
PEN_SAVE = 5
FULL_MATCH = {"GK": 0, "DEF": 0, "MID": 1, "FWD": 1}           # started and not subbed off
YELLOW, RED = -1, -3                                            # a red replaces a yellow
OWN_GOAL = CAUSED_PEN = CAUSED_FK_GOAL = PEN_MISS = -2
IMPACT_WIN, IMPACT_LOSS = 0.3, -0.3                              # team won / lost while he was on the pitch
FT_POS = {"goalkeeper": "GK", "defender": "DEF", "midfielder": "MID", "forward": "FWD"}
UEFA_POS = {"GOALKEEPER": "GK", "DEFENDER": "DEF", "MIDFIELDER": "MID", "FORWARD": "FWD"}


def points(pos, minutes, started, goals=0, assists=0, sot_incl_goals=0, conceded=0, saves=0, pen_saves=0,
           yellow=0, red=0, own_goals=0, caused_pen=0, result=0, subbed_off=None):
    """Points for one player-match from counts. result: +1 team won / -1 lost while he was on. subbed_off None = infer."""
    if minutes <= 0: return 0.0
    full = started and (not subbed_off if subbed_off is not None else minutes >= 90)
    p = APPEARANCE + (MIN60 if minutes >= 60 else 0) + GOAL[pos] * goals + ASSIST * assists
    p += SOT[pos] * max(0, sot_incl_goals - goals)
    p += (CLEAN_SHEET[pos] if minutes >= 60 and conceded == 0 else 0) + CONCEDED_PER_2[pos] * (conceded // 2)
    if pos == "GK": p += SAVE * saves + PEN_SAVE * pen_saves
    p += FULL_MATCH[pos] * (1 if full else 0)
    p += (RED * red) if red else (YELLOW * yellow)
    p += OWN_GOAL * own_goals + CAUSED_PEN * caused_pen
    p += IMPACT_WIN if result > 0 else (IMPACT_LOSS if result < 0 else 0)
    return round(p, 2)
