# Method (the one rulebook)

## How Claude talks to the owner
- Blunt advisor. No flattery. Challenge assumptions. Judge decisions, not luck.
- Plain English, short sentences, short structured answers. Explain any stats term in a few words.
- Lead with the answer. Say what is checked, what is assumed, what is missing. Never invent a number that should come from data.

## Contest rules (FanTeam UCL 2026-27)
Scoring CONFIRMED 24 Nov 2026 (see below).
Per contest, always read from the rules JSON: budget, max per club, captain multiplier, safety net.

### Seen in contest JSON (CONFIRMED for that contest)
| Contest | Matches | Budget | Max/club | Captain | Safety net | Subs timing | CS stack penalty | Entries/user | Prize ratio | Rule version |
|---|---|---|---|---|---|---|---|---|---|---|
| 1170340 Tuesday Main Event GW5 (24 Nov, 20:00 UTC games only) | 7 | 121 | 3 | 2.0x | team | start of match | on (1) | 15 | 17 | 13 |
Rule version 13 is the same number as the EPL contests (`epl.dfs` data/ref/fanteam_api.md). That points to the same
scoring, but the JSON does not list points per event: scoring stays TBC until the Rules tab is checked.
Pool CSV for UCL: Tournament, PlayerID, Name, FName, Club (3-letter code), Lineup (expected / possible / unexpected /
injured / suspended), Position (goalkeeper / defender / midfielder / forward), Price. Club codes for GW5: AEK ARS BET BVB
COM FCP FEY LEN MCI NAP PSV RBL RMA SLV.

### Scoring (CONFIRMED for UCL, 24 Nov 2026: rules page + data check)
Source: FanTeam football rules page, owner screenshots `data/manual/fanteam_rules_2026-11-24.md`. Same table as EPL.
Data check `scripts/check_scoring.py` -> `data/ref/scoring_check.md`: UEFA stats scored with this table v FanTeam points,
MD2-4, 543 player-matches with full information: 93% match exactly or within the +-0.3 impact term; mean residual 0.00.
| Event | GK | DEF | MID | FWD |
|---|---|---|---|---|
| Appearance | 1 | 1 | 1 | 1 |
| 60+ full minutes (extra) | +1 | +1 | +1 | +1 |
| Goal | 8 | 6 | 5 | 4 |
| Assist (fantasy assist) | 3 | 3 | 3 | 3 |
| Clean sheet (60+ min on pitch) | 4 | 4 | 1 | 0 |
| Goals conceded while on pitch | -1 per 2 | -1 per 2 | 0 | 0 |
| Shot on target (a goal is NOT also a shot on target) | 1.0 | 0.6 | 0.4 | 0.4 |
| Save | 0.5 | - | - | - |
| Penalty save | 5 | - | - | - |
| Played full match (started, not subbed off) | - | - | +1 | +1 |
All: yellow -1, red -3, own goal -2, caused a penalty -2, caused a scoring free kick -2, penalty miss -2.
Impact: +0.3 if the team won the time the player was on the pitch, -0.3 if it lost. Captain 2x (contest JSON).
Fantasy assist is wider than the official assist: winning a penalty or free kick that is scored, rebounds off the post,
forcing an own goal. Seen in data: +3.0/+3.3 residuals = one extra fantasy assist.
Data notes (24 Nov): UEFA `minutes_played_official` = 60 can be under 60 full minutes (no 60+ point; 2 cases). UEFA GK
`saves` often run 1-2 above FanTeam's save count: do not use UEFA saves as FanTeam saves without a correction.
UEFA per-player `goals_conceded` is 0 for outfield players: use team score + time on pitch instead.

## Model rules (v1)
Code: `model/daily_proj.py CONTEST [--freeze]` (stage 2, 24 Nov). Scoring in `model/scoring.py`. Output `data/proj/`.
INFERRED (not from data yet; calibrate in stage 4): Lineup -> P(start) confirmed 1.0, expected 0.85, possible 0.45,
unexpected 0.05, injured / suspended 0; sub-on chance = UEFA bench rate (0.42), halved for 'unexpected'.
Measured from UEFA MD1-4: assists per goal 0.84, SoT per goal 2.80 (GK saves), own-goal share 0.031, yellows per team-game 1.76.
Approximations: clean sheet = P(team CS) ^ (share of match played) x P(60+); impact = full-time result x share played.
- Bookmaker prices first. Remove margin; mean of books.
- Goals: anytime scorer. Shots, SoT, assists, tackles, cards: player props.
- Clean sheet, goals conceded, win: score grid fitted to team markets.
- Team totals anchor players: a team's player goals and assists add up to its expected goals.
- Saves: opponent expected SoT minus expected goals (saves props too thin).
- Start chance is the weakest input. Recheck once XIs are out.
- No domestic-league history in v1. New factors start as flags (see PLAN.md).

## Bookmaker facts (The Odds API, probe 24 Nov 2026: `data/ref/ucl_props_probe.md`)
- Sport key `soccer_uefa_champs_league`. Player props up about a day before kick-off.
- Anytime scorer: 5-6 books (betrivers, betway, draftkings, fanduel, onexbet, mybookieag). No Pinnacle or Betfair on player props.
- Shots / SoT: betrivers, fanduel, onexbet (+ betway, draftkings alternates). Assists: fanduel Over 0.5 + betrivers/betway alternates.
- Tackles: draftkings only. Saves: 3-4 GKs only. Cards: betway, draftkings.
- Team markets deep: h2h ~48 books, totals ~24, BTTS ~16 (Pinnacle present). Team totals thin: fanduel (+ mybookieag).
- Yes/Over-only markets: 1/price includes the margin.
- Match names on an accent-insensitive key (e.g. Bodø/Glimt, ŠK Slovan Bratislava).
- The key is shared with the NBA and EPL repos. Log credits left after each run.
- Cost of `fetch_props.py` (estimate from markets x regions, to be checked against real runs): about 21 credits per game + 4 per run.
  A 9-game night about 190. Billing counts only markets that return data.
- Not yet checked: coverage for the smallest clubs, real cost of a full 18-game pull.

## Data policy (public repo)
- Raw bookmaker prices: committed (owner decision A, 24 Nov 2026). Review at stage 4.
- FanTeam standings: only rank, score, payout are saved. No user names, ids or entry names.
- No keys, tokens, account details or personal names in any file or Action log.
