# UEFA public API facts (tested 24 Nov 2026 from GitHub Actions; blocked from the chat workspace; no key, no login)
- Match list: `https://match.uefa.com/v5/matches?competitionId=1&seasonYear=2027&limit=100&offset=N&order=ASC` (234 matches incl.
  qualifying). League phase = `round.phase` TOURNAMENT, matchday = `matchday.name` (MD1..MD8), `status` FINISHED / UPCOMING.
- Lineups: `https://match.uefa.com/v5/matches/{id}/lineups` -> homeTeam/awayTeam: field (starters), bench; player id, name, fieldPosition.
- Player stats per match: `https://matchstats.uefa.com/v2/player-statistics/{id}` -> list per player: playerId, teamId, statistics
  [{name, value}]. League phase: ~380 stat names incl. minutes_played_official, goals, assists, attempts_on_target, saves,
  tackles, tackles_won, recovered_ball, clean_sheet, goals_conceded, cards, own goals. v1 is the same data, 5x bigger.
  Qualifiers carry only ~26 stats (no saves, tackles).
- Team stats per match: `https://matchstats.uefa.com/v1/team-statistics/{id}`.
- `compstats.uefa.com/v1/player-ranking` = season totals; ignores `matchId`. 404: compstats `/v1/player-stats`. 400: `/events`.
- `played_time` is NOT minutes (lower; likely ball-in-play). Use `minutes_played_official`.
Scripts: `scripts/probe_uefa.py` (uefa Action), `scripts/fetch_uefa_stats.py` (uefa_stats Action).
