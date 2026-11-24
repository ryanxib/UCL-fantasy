# UCL-fantasy

Champions League 2026-27 fantasy on FanTeam: daily contests first, then the league-phase season game.
Same method as the owner's EPL, NBA and EuroLeague repos. **This repo is the only memory.**

Start of every chat: read `NEXT.md`, then `PLAN.md`, then the last entries of `LOG.md`. Then follow `CHECKLIST.md`.

**This repo is public.** Never write keys, tokens, account details or personal names to any file, log line or
Action output. Ask the owner before committing raw bookmaker data.

## Files
| File | What it is |
|---|---|
| `NEXT.md` | Current state, next step, open items. Read first |
| `PLAN.md` | Build stages |
| `LOG.md` | Dated log, newest first |
| `METHOD.md` | Contest rules (confirmed or TBC), model rules, bookmaker facts |
| `CHECKLIST.md` | Steps for each kind of chat |

## Data and code
| Path | What it is |
|---|---|
| `data/ref/ucl_props_probe.md` | Odds API probe, 24 Nov 2026: which UCL markets and books exist (summary only, no prices) |
| `data/ref/ucl_props_probe_raw.json` | The probe's raw API replies (raw prices; committing approved by the owner) |
| `scripts/probe_ucl_props.py` | The one-off script that wrote them (no Action here) |
| `scripts/fetch_props.py` | The Odds API -> `data/raw/props/ucl_<stamp>.json.gz` + `data/clean/props/<market>_latest.csv` / `_history.csv`, `team_*`, `team_extra_*` |
| `scripts/fetch_pool.py` | FanTeam pool + contest rules by tournament id -> `data/raw/fanteam/`, registry `data/ref/contests.csv`. Standings scrubbed of user identity |
| `scripts/check_odds_key.py` | Free check that the `ODDS_API` secret works -> `data/ref/odds_key_check.md` |
| `model/names.py` | Accent-insensitive name and club keys (Bodø -> bodo) |
| `tests/test_stage1.py` | Offline checks: parsing on the probe data, scrub, name keys, no key printed |

## Actions (fetching runs here; the Claude workspace cannot reach FanTeam or bookmakers, nor call the Actions API)
| Workflow | How to run | Output |
|---|---|---|
| `props` | Actions -> Run workflow, or commit arguments to `requests/props.txt` (e.g. `--hours 30`) | `data/clean/props/`, `data/raw/props/last_run.txt` (credits left) |
| `pool` | Actions -> Run workflow, or commit tournament ids to `requests/pool.txt` | `data/raw/fanteam/`, `pool_last_run.txt`, `data/ref/contests.csv` |
| `key_check` | Runs on change to its script, or by hand | `data/ref/odds_key_check.md` |
Secret: `ODDS_API` (shared with the NBA and EPL repos: same monthly credits).

Code is copied from sister repos, never imported. Each copy is logged with source repo, file and commit.
