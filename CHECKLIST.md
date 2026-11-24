# Checklists (one job per chat)

Start of every chat: read NEXT.md, PLAN.md, last LOG.md entries. If the repo cannot be reached, stop and say so.
Every file is public: no keys, tokens, account details or personal names. Ask before committing raw bookmaker data.

## Matchday (before lock)
1. [ ] Tournament id(s) from the owner (contest Overview screenshot). Write ids to `requests/pool.txt`, push -> `pool` Action. Read `data/raw/fanteam/pool_last_run.txt`; check rules (budget, max per club, captain, safety net) v the screen
2. [ ] Props on the day: write e.g. `--hours 30` to `requests/props.txt` (change the line, or the push will not trigger), push -> `props` Action. Read `data/raw/props/last_run.txt`; log credits left
3. [ ] Projection, calls, lineups, freeze: not built yet (PLAN stages 2-3)

## Post-matchday
1. [ ] Owner's screens (scores, ranks, cash line, prizes) -> file straight away (no personal names)
2. [ ] Score frozen projection v actual -> `review/`
3. [ ] Judge decisions, not luck
4. [ ] LOG.md, NEXT.md, commit and push

## Build
1. [ ] One stage (or part) of PLAN.md. 2. [ ] Tests. 3. [ ] Log each code copy (source repo, file, commit). 4. [ ] LOG.md, NEXT.md, commit and push

## Research
One question, answered with data, logged.
