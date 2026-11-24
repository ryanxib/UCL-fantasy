# Log (newest first)

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
