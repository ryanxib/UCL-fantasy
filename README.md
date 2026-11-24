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
| `scripts/probe_ucl_props.py` | The one-off script that wrote it (reads the key from env `ODDS_API_KEY`; no Action here yet) |

Code is copied from sister repos, never imported. Each copy is logged with source repo, file and commit.
