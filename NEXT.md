# Next

## State (24 Nov 2026)
- Stages 0 and 1 done. `props` ran on tonight's 9 games (18482 credits left). `pool` ran on contest 1170340
  (Tuesday Main Event GW5, 7 games at 20:00 UTC, budget 121, max 3 per club, captain 2x, safety net team).
- No projection, lineup or review code yet.

## Next step
Stage 2 (projection), a new build chat. Or a research chat first: pull UCL 2026-27 player match stats (MD1-5) from
FanTeam (past contest ids via a scan; raw stats via `/fantasy_teams/{id}`), check against FanTeam points.

## Open items
1. Scoring TBC for UCL: contest JSON has rule version 13 (same as EPL) but no points table. Need a Rules tab screenshot.
2. Meaning of the screen icons "P", captain-style, shield on contest 1170340: TBC (likely captain + safety net).
3. Coverage gaps: Porto @ Feyenoord had no player props on 24 Nov and is IN contest 1170340; Slovan game thin.
   Stage 2 needs a fallback for games without props. Decide in stage 2.
4. `team_latest.csv` includes `h2h_lay` rows: ignore in stage 2.
5. `epl.dfs` has the name-key bug fixed here (Ø, ß, Ł dropped). Fix there in an EPL chat.
6. Raw prices policy (option A): review at stage 4.
