# Log (newest first)

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
