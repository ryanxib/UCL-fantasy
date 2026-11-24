# Can we pull per-player UCL match stats from FanTeam? (desk research, 24 Nov 2026)

Not tested on UCL yet. Based on FanTeam API facts tested in `ryanxib/epl.dfs` (commit efa3cb9, `data/ref/fanteam_api.md`,
`data/raw/fanteam/entry_fantasy_teams_134534901.json`). FanTeam is blocked from the chat workspace: any pull is an Action.

## What exists (EPL-tested)
1. Finished contest pool: `/tournaments/{id}/players?format=csv` has FanTeam `Points` per player for EVERY player in the pool.
   Total points only, no stat breakdown.
2. One entry: `/fantasy_teams/{id}` (daily) or `?round=N` (season game) has `realPlayerMatchStats` with the full breakdown
   (goal, assist, shotOnTarget, allShotsOnTarget, keeperSave, cleanSheet, concededGoal, cards, playtime1/15/60/90,
   started, minutesPlayed, fouls, ownGoal, penalties, MOTM). BUT ONLY FOR THE 11 (daily) / 15 (season) PLAYERS IN THAT ENTRY.
   Checked: saved EPL entry has 11 stat rows for 11 picks.
3. No all-players stats endpoint found. 404: stats, players/stats, results, fixtures, gameweeks, rounds.

## So, for every player
- Points per player per matchday: yes, if we have one finished daily UCL contest id per matchday (pool CSV).
- Full stat breakdown per player: only by merging many entries' squads. Owned players: covered. Players nobody picked: missing.
  Coverage is unknown until probed.

## UCL ids known (from epl.dfs scans)
- League Phase Season Game: 1137274, 1137277 (High-Roller), 1137280, 1137283 (1,812 entrants). Start 8 Sep 2026, 18 matches listed.
- No daily UCL contest ids for MD1-4 found yet. Need a `scan` over id ranges around each matchday.

## Not checked
- Whether UCL season game `?round=N` works like EPL, and its viewableRound.
- Coverage share (players with stats / players who played) from merging N squads.
- Whether `keeperSave` and tackles exist for UCL (no tackles key in the EPL stats).
