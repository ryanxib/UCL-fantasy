# Plan (UCL fantasy on FanTeam)

Scope (24 Nov 2026): daily contests first, then the league-phase season game.
One stage per build chat. A stage is done when its "done when" line is true and logged.

## Stage 0. Repo skeleton (24 Nov 2026: done)
README, NEXT, PLAN, LOG, METHOD, CHECKLIST. Props probe summary + script copied from `epl.dfs` (branch `ucl-probe`).
Done when: files pushed to main, copy logged.

## Stage 1. Fetching (Actions) (24 Nov 2026: done)
- Copy from `epl.dfs`: `fetch_props.py`, `fetch_pool.py`, `names.py` + `props` and `pool` workflows. Sport key `soccer_uefa_champs_league`.
- Public repo: check no script prints the key or a request URL (Action logs are public).
- Owner decision (24 Nov): raw bookmaker prices may be committed here (option A). Review at stage 4.
- `ODDS_API` secret set and checked (24 Nov).
Done when: `props` and `pool` have each run once on UCL with clean output, credits logged.

## Stage 2. Projection (spec updated 24 Nov 2026)
Goal: projected FanTeam points per pool player for one contest, saved before lock.
Copy from `epl.dfs` (log commit): `model/team_lines.py`, `model/score_matrix.py`, `model/daily_proj.py` (+ their tests).
Inputs: `data/clean/props/*_latest.csv`, `data/clean/props/team_latest.csv` (ignore `h2h_lay`), contest pool CSV + JSON,
`data/manual/overrides_<contest>.csv` (owner start overrides), `data/clean/uefa/player_match.csv` (fallback only).
Steps:
1. Team lines: margin-free 1X2, totals, BTTS (+ team totals where listed) -> score grid per game -> each team's expected
   goals, P(win/draw/loss), P(clean sheet), expected goals conceded.
2. Player goals: anytime scorer (mean of books, margin removed) -> P(scores) -> expected goals. Scale so the team's player
   goals = team expected goals minus own goals share.
3. Assists, SoT: props (mean of books). Scale assists to about 0.75-0.8 x team goals (check ratio in UEFA MD1-4 data).
   SoT points use SoT minus goals (a goal is not also a SoT).
4. Minutes: P(start) from Lineup column + props listing + overrides; P(60+), P(full match) by position from UEFA MD1-4
   starters. Clean sheet, goals conceded, impact (+0.3 win / -0.3 loss) weighted by expected share of minutes.
5. GK: saves = opponent expected SoT minus expected goals, x 0.5 (UEFA saves overcount; calibrate to FanTeam later).
6. Cards: props where listed, else position base rate from UEFA MD1-4. Ignore own goal / penalty events (tiny).
7. Games or players with no props (Porto-Feyenoord today): FALLBACK = team expected goals from the score grid, shared
   over players by their UEFA MD1-4 per-90 share of team goals / assists / SoT. Marked `fallback=1`. OWNER DECISION NEEDED.
8. Safety net: a non-starter is swapped for the dearest same-club same-position player at or below his price: value
   P(start) x own projection + (1 - P(start)) x replacement projection.
Outputs: `data/proj/<contest>_<stamp>.csv` (player, club, pos, price, P(start), each points part, total, fallback flag,
source), `data/proj/<contest>_warnings.md` (unlinked names, missing props, team sums off, overrides used). Frozen copy at lock.
Checks: per team, player goals sum = team expected goals; points by part rebuild the total; scoring unit test uses METHOD
table on 3 real MD2-4 rows (FanTeam points known); no pool player silently dropped.
Done when: one real matchday contest projected end to end before lock, warnings read, tests pass.
Later (flag, not v1): FanTeam/UEFA history blended where props exist, only if it lowers error on frozen projections.

## Stage 3. Lineups and freeze
- Copy `lineup_build.py`, `build_checks.py`, `pull_entries.py`. Rules (budget, max per club, captain, safety net) from each contest's JSON.
Done when: one matchday built and frozen before lock.

## Stage 4. Post-matchday review
- Copy review and ledgers from `nba.dfs`. Score frozen projections v actual points.
Done when: one matchday reviewed and logged.

## Stage 5. League-phase season game
Scoped later.

## Rule for new factors
Domestic-league history or any new factor starts as a flag. It changes projections only after it lowers the error on
projections saved before lock.
