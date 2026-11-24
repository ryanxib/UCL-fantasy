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

## Stage 2. Projection
- Copy `team_lines.py`, `score_matrix.py`, `daily_proj.py`. Score grid fitted to 1X2, totals, BTTS, team totals.
- Player goals and assists scaled so each team's sum equals its expected goals.
- Saves = opponent expected shots on target minus expected goals.
- Start chance: props listing + pool Lineup column + owner overrides.
- METHOD.md scoring confirmed against a UCL contest rules JSON.
Done when: one real matchday projected end to end, warnings read, tests pass.

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
