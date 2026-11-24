# Next

## State (24 Nov 2026)
- Stages 0 and 1 done. `props` ran on tonight's 9 games (18482 credits left). `pool` ran on contest 1170340
  (Tuesday Main Event GW5, 7 games at 20:00 UTC, budget 121, max 3 per club, captain 2x, safety net team).
- No projection, lineup or review code yet.

## Next step
Stage 2 (projection), a new build chat. Or a research chat first: pull UCL 2026-27 player match stats (MD1-5) from
FanTeam (past contest ids via a scan; raw stats via `/fantasy_teams/{id}`), check against FanTeam points.

## Open items
1. Scoring CONFIRMED 24 Nov (rules screenshots + UEFA stats v FanTeam points, 93% match; METHOD.md). A goal is not also a
   shot on target. Open: GK save count (UEFA runs 1-2 above FanTeam).
2. Meaning of the screen icons "P", captain-style, shield on contest 1170340: TBC (likely captain + safety net).
3. Coverage gaps: Porto @ Feyenoord still had no player props at 11:20 UTC (see `data/ref/props_coverage.md`) and is IN
   contest 1170340. Re-run `coverage` closer to kick-off (1 credit per game).
   Stage 2 needs a fallback for games without props. Decide in stage 2.
4. `team_latest.csv` includes `h2h_lay` rows: ignore in stage 2.
5. `epl.dfs` has the name-key bug fixed here (Ø, ß, Ł dropped). Fix there in an EPL chat.
6. Raw prices policy (option A): review at stage 4.
7. Past FanTeam points: `data/clean/points/ucl_points_md{2,3,4}.csv`. Coverage MD1 0/18, MD2 14/18, MD3 14/18, MD4 7/18 games
   (dailies skip 18:45 CET games; no dailies found for MD1 or MD4 Tue). Flag only until it lowers projection error.
8. UEFA stats MD1-4 DONE: `data/clean/uefa/player_match.csv` (all 72 games; minutes, goals, assists, SoT, saves, tackles, CS,
   cards). After each matchday: commit `requests/uefa_stats.txt` with the new matchday list to refresh.
   Linked to FanTeam ids for MD2-4 (`data/clean/points/link_uefa_fanteam.csv`). Next: points from stats for all players
   (needs goal times for subs: UEFA events/lineups) in stage 2.
