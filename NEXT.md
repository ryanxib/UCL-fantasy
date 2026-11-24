# Next

## State (24 Nov 2026)
- Stage 0 done. Stage 1 built: `props` ran clean on tonight's 9 games (178 credits; 18482 left). `pool` built and tested
  offline, not yet run: needs a FanTeam tournament id.
- No projection, lineup or review code yet.

## Next step
1. Finish stage 1: owner sends a UCL contest id (Overview screenshot) -> write it to `requests/pool.txt`, push, read
   `data/raw/fanteam/pool_last_run.txt`. Then confirm UCL scoring in METHOD.md from the contest JSON (still TBC).
2. Then stage 2 (projection), a new build chat.

## Open items
1. Scoring is TBC for UCL until a UCL contest rules JSON is checked.
2. Coverage gaps: Porto @ Feyenoord had no player props on 24 Nov; Slovan game thin. Stage 2 needs a fallback for
   games without props (team expected goals shared over players needs a source for shares). Decide in stage 2.
3. `team_latest.csv` includes `h2h_lay` rows: ignore in stage 2.
4. `epl.dfs` has the same name-key bug fixed here (Ø, ß, Ł dropped: "Ødegaard" -> "degaard"). Fix there in an EPL chat.
5. Raw prices policy (option A): review at stage 4.
