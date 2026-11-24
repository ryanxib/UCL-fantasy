# Log (newest first)

## 2026-11-24 Stage 2 spec written into PLAN.md
- Inputs, 8 steps, outputs, checks, done-when. Open owner decision: fallback for games with no player props (step 7).

## 2026-11-24 Scoring confirmed for UCL
- Owner sent 8 screenshots of the FanTeam football rules page. Transcribed: `data/manual/fanteam_rules_2026-11-24.md`.
- Same table as EPL. New vs METHOD: own goal -2, caused penalty -2, scoring free kick -2, penalty miss -2, penalty save 5,
  60+ means 60 FULL minutes, full match = started and not subbed off, a goal is not also a shot on target. METHOD.md updated.
- Data check (`scripts/check_scoring.py` -> `data/ref/scoring_check.md`): UEFA MD2-4 stats scored with the table v FanTeam
  points. 1,065 linked player-matches (club codes 70/70 mapped, 17 non-zero FanTeam players not linked). Of 543 with full
  information (on for the whole match, or forwards): 93% exact or off by the 0.3 impact term; mean residual 0.00.
  Rest explained: extra fantasy assists (+3), UEFA GK saves 1-2 above FanTeam's, 60 official minutes < 60 full minutes,
  penalty misses / caused penalties not in our stat set.
- First run used UEFA per-player goals_conceded: it is 0 for outfield players. Fixed: opponent final score for full-match rows.
- New: `data/clean/points/link_uefa_fanteam.csv` (UEFA id <-> FanTeam id, MD2-4). Starting point for stage 2 linking.

## 2026-11-24 UEFA per-player per-match stats, MD1-4 (research)
- Probe (`uefa` Action, `scripts/probe_uefa.py`): found the per-match player stats endpoint. Facts in `data/ref/uefa_api.md`.
- Pull (`uefa_stats` Action, `scripts/fetch_uefa_stats.py`): `data/clean/uefa/player_match.csv`, report `pull_report.md`.
  All 72 league-phase games of MD1-4, 3,196 rows, 2,259 with minutes (561-569 per matchday). 0 failures.
- Checks: per-match goals + own goals = final score in 72 of 72. 147 goalkeeper appearances, 522 saves (max 9).
  Tackles avg 0.93 per player-match. 2 rows with no name (no minutes; one is a card with no team, likely staff): ignore.
- Kept player name, club, position, starter flag and 23 stats. No ages or birth dates (public repo).
- Removed probe samples that were cut off at 400 KB (invalid JSON). Kept match list, lineups samples.
- NOT done: link UEFA player ids to FanTeam player ids (names + club; stage 2). Not converted to FanTeam points:
  scoring still TBC for UCL. Flag only until it lowers projection error.

## 2026-11-24 History run 2 results (step 10, ids 1135500-1158800)
- 2,665 ids tried, 193 UCL contests. Still NO daily contest for MD1 and none for MD4 Tuesday. MD4 file unchanged (Wed, 7 games).
- Likely FanTeam ran no dailies on those days. Not proven: a cluster smaller than 10 ids could be missed.
- Final FanTeam daily coverage: MD1 0/18 games, MD2 14/18, MD3 14/18, MD4 7/18. The 18:45 CET games are never covered.
- Gaps need another source. UEFA match + comp stats APIs answer from Actions (both 200): next research chat.

## 2026-11-24 History run 1 results (Action 45380700535, 34 min)
- Scan 1137000-1170000 step 40, fine +-40: 157 UCL contests (seasonId 2026). Report: `data/clean/points/ucl_points_report_run1.md`.
- Points files: MD2 678 players / 14 of 18 games (1143672 Tue, 1143711 Wed); MD3 687 / 14 of 18 (1148080, 1148891);
  MD4 348 / 7 of 18 (1158791, Wed only). MD1: no daily contest found.
- Every daily contest found covers only the 20:00 CET games: the 4 early (18:45 CET) games per matchday have no FanTeam
  daily points. MD5 contest 1170340 is the same. Fix is not a scan: needs another source (season game or UEFA).
- Web sources probe (from the Action): UEFA match API (match.uefa.com) 200, UEFA comp stats API (compstats.uefa.com) 200.
  Sofascore 403, FBref 403, FotMob 404 (wrong guess), uefa.com pages and UCL Fantasy feed timed out.
- Run 2 started: ids 1135500-1158800 step 10, fine 10, MD1 and MD4 only.

## 2026-11-24 Coverage refresh + scoring-rules probe
- New `scripts/coverage.py` + `coverage` Action (`requests/coverage.txt`): books per market per game, no prices, 1 credit
  per game. Output `data/ref/props_coverage.md` (+ history CSV, shows change v previous run from the next run on).
- Run 11:20 UTC, next 48 h (18 games): 18 credits, 18464 left.
  - Porto @ Feyenoord: still NO player props (0 books, 2 h after the 09:35 pull and ~9 h before kick-off). Team markets fine.
  - Tonight's other 8 games unchanged v 09:35: anytime scorer 5-7 books, shots/SoT 3, assists 1 (+2 alternates), tackles 1, cards 2.
  - Wednesday's 9 games already have full player props (anytime 5-6 books). Liverpool @ Brugge SoT 2 books; Fenerbahce @ Shakhtar no saves.
- New `scripts/probe_rules.py` + `probe_rules` Action: FanTeam has NO scoring table in its API. Tried 14 endpoints.
  `/rule_versions/13`, `/rules/13`, `/scoring*`, `/match_collections/*` are 404. `/games/98781` and `/players?format=json`
  give only `ruleVersion = 13`. `/white_labels/fanteam` points to a help-centre article ("fantasy-football-soccer-rules"),
  not data. `playerChoices` in `/players?format=json` carries `totalPoints` and `lastPoints` per player (useful for the history work).
- So the scoring can be confirmed only by data: raw stats v points on a finished UCL contest (history work), or the Rules tab.
- Web search found no FanTeam rules page. A 2021 article (Fantasy Football Scout) says shot-on-target points are NOT given
  when the shot is a goal or gives an assist. Not in METHOD's EPL table: added as TBC.
- Both Actions now have their own concurrency group: in a shared group GitHub cancels a waiting job when a newer one queues
  (the first coverage/probe runs were held behind the long `history` run).

## 2026-11-24 Research: past FanTeam points per matchday (in progress)
- Owner: per-matchday FanTeam points (not season totals) as a guide where odds are thin. Also look for web stats sources.
- MD dates (UEFA): MD1 8-10 Sep, MD2 13/14 Oct, MD3 20/21 Oct, MD4 3/4 Nov, MD5 24/25 Nov (not finished).
- UCL contests on FanTeam: gameType football, matchCollection.seasonIds = [2026] (contest 1170340). EPL season id is 2004.
- New: `scripts/scan_ucl.py` (scan adapted from `ryanxib/epl.dfs` scripts/scan_tournaments.py, commit efa3cb9),
  `scripts/probe_web_sources.py`, `history` Action (runs on a push to `requests/history.txt`). Writes only contest
  meta and player points: no user names or ids. Offline test on contest 1170340 files: passes.
- Points are a new factor: flag only, until it lowers the error on saved projections.

## 2026-11-24 Research: per-player match stats from FanTeam
- Question: can we pull every UCL player match stat for MD1-5 from FanTeam? Answer in `data/ref/fanteam_stats_access.md`.
- Short answer: points per player yes (finished contest pool CSV); full stat breakdown only for players inside pulled entries.
- MD5 is not finished: tonight's 9 games are its first half. Only MD1-4 can be pulled now.
- Desk research only (FanTeam blocked from this workspace). Nothing fetched. No code changed.

## 2026-11-24 Stage 1 done: first pool run
- Owner sent contest 1170340 (Tuesday Main Event GW5). Overview screen saved: `data/manual/contest_1170340_screen.md`.
- `pool` Action via `requests/pool.txt`: clean. 345 players, contest JSON saved, row in `data/ref/contests.csv`.
- Rules from JSON (confirmed for this contest): budget 121, max 3 per club, captain 2x, safety net "team", subs at start
  of match, clean-sheet stack penalty on, 15 entries per user, 172 entrants at pull time, rule version 13. Written to METHOD.md.
- The contest covers only the 7 games at 20:00 UTC (not the 17:45 games). It includes Porto @ Feyenoord, which had no player props.
- Privacy check of the saved JSON: standings rows hold only rank, score, payout. No user names or ids elsewhere.
- Lineup column today: 154 expected, 41 possible, 111 unexpected, 38 injured, 1 suspended.

## 2026-11-24 Stage 1: fetching built
- Owner decision: raw bookmaker prices may be committed (option A). Review at stage 4.
- Copied from `ryanxib/epl.dfs` commit `efa3cb9cdb1f31e21031b5c1a0e278d77de50dca`, adapted:
  - `scripts/fetch_props.py`: sport key UCL; calls per UCL book coverage (anytime us,uk,eu; shots/SoT/assists us,eu;
    assists alt + tackles alt + cards us,uk); extra team markets (btts, team totals, alt team totals, us,uk) on by default;
    h2h + totals uk,eu (adds Pinnacle); default window 30 h; raw file `ucl_<stamp>.json.gz`.
  - `scripts/fetch_pool.py`: contest JSON standings scrubbed to rank, score, payout (whitelist; public repo).
  - `model/names.py`: FPL matcher and EPL alias list removed.
  - `.github/workflows/props.yml`, `pool.yml`: also run on a push that changes `requests/props.txt` / `requests/pool.txt`
    (this workspace cannot call the Actions API). Arguments checked by a pattern before reaching the shell. `team_lines` step dropped (stage 2).
- BUG FIXED (also present in `epl.dfs`, not fixed there): `key()` turned "Ødegaard" into "degaard" and "Bodø" into "bod",
  because NFKD does not split Ø, ß, Ł etc. Added a fold table in `names.py` and `fetch_props.py`.
- Added `tests/test_stage1.py` (offline): all 4 pass.
- First `props` run, 24 Nov 09:35 UTC, `--hours 30` (tonight's 9 games): clean, no key in the log.
  - Cost 178 credits (18660 -> 18482): 21 per game with props, 6 for a game without, 4 for team markets. Estimate held.
  - Porto @ Feyenoord: NO player props at all (0 books), team markets fine. Real Betis @ Slovan Bratislava: only 21 players
    priced (thin). Other games 36-49 players, 5-7 books on anytime scorer.
  - Team markets: h2h and totals for all 9 games, 39-40 books on h2h. `team_latest.csv` also holds `h2h_lay` (exchange lay
    prices) rows: stage 2 must ignore them.
  - Team totals: 1-2 books per game (4-8 prices). Alternate team totals deeper (57-69 prices).

## 2026-11-24 Raw probe copied; key check Action
- Owner approved committing raw bookmaker data for the probe. Copied `data/ref/ucl_props_probe_raw.json` from
  `ryanxib/epl.dfs`, branch `ucl-probe`, commit `fc6e3788d43f8bb0280fb0a725ae325f2dbf55f5` (unchanged, 420 KB). Checked: no key in it.
- Key check ran OK 09:30 UTC: credits left 18660 (unchanged, so the check is free).
- Added `scripts/check_odds_key.py` + `key_check` Action: confirms the `ODDS_API` secret works using the free /sports
  endpoint (0 credits). Writes `data/ref/odds_key_check.md`. Prints no key or URL. Workspace cannot read repo secrets directly.

## 2026-11-24 Stage 0: repo skeleton
- Repo set: `ryanxib/UCL-fantasy` (public, owner's choice). Replaces the planned `ucl.dfs`, which was never created.
- Added README, PLAN, METHOD, CHECKLIST, NEXT, LOG.
- Copied from `ryanxib/epl.dfs`, branch `ucl-probe`, commit `fc6e3788d43f8bb0280fb0a725ae325f2dbf55f5` (24 Nov 2026 04:40 UTC):
  - `data/ref/ucl_props_probe.md` -> `data/ref/ucl_props_probe.md` (unchanged)
  - `scripts/probe_ucl_props.py` -> `scripts/probe_ucl_props.py` (unchanged; reads key from env, prints no key)
- NOT copied (waiting for owner): `data/ref/ucl_props_probe_raw.json` (420 KB, raw bookmaker prices) and the
  `ucl_probe.yml` workflow (it would commit raw prices; not needed once stage 1 lands).
- Credits left on the shared Odds API key at end of the probe: 18660 (24 Nov 04:40 UTC).
- METHOD.md scoring copied from `epl.dfs` METHOD.md and marked TBC for UCL.
