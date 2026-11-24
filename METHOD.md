# Method (the one rulebook)

## How Claude talks to the owner
- Blunt advisor. No flattery. Challenge assumptions. Judge decisions, not luck.
- Plain English, short sentences, short structured answers. Explain any stats term in a few words.
- Lead with the answer. Say what is checked, what is assumed, what is missing. Never invent a number that should come from data.

## Contest rules (FanTeam UCL 2026-27)
**All TBC.** Working assumption: same scoring as FanTeam EPL (copied below from `epl.dfs` METHOD.md, where it is
confirmed for EPL). Confirm against the first UCL contest's rules JSON before trusting it here.
Per contest, always read from the rules JSON: budget, max per club, captain multiplier, safety net.

### Seen in contest JSON (CONFIRMED for that contest)
| Contest | Matches | Budget | Max/club | Captain | Safety net | Subs timing | CS stack penalty | Entries/user | Prize ratio | Rule version |
|---|---|---|---|---|---|---|---|---|---|---|
| 1170340 Tuesday Main Event GW5 (24 Nov, 20:00 UTC games only) | 7 | 121 | 3 | 2.0x | team | start of match | on (1) | 15 | 17 | 13 |
Rule version 13 is the same number as the EPL contests (`epl.dfs` data/ref/fanteam_api.md). That points to the same
scoring, but the JSON does not list points per event: scoring stays TBC until the Rules tab is checked.
Pool CSV for UCL: Tournament, PlayerID, Name, FName, Club (3-letter code), Lineup (expected / possible / unexpected /
injured / suspended), Position (goalkeeper / defender / midfielder / forward), Price. Club codes for GW5: AEK ARS BET BVB
COM FCP FEY LEN MCI NAP PSV RBL RMA SLV.

### Scoring (EPL, confirmed there; TBC for UCL)
| Event | GK | DEF | MID | FWD |
|---|---|---|---|---|
| Appearance | 1 | 1 | 1 | 1 |
| 60+ minutes (extra) | +1 | +1 | +1 | +1 |
| Goal | 8 | 6 | 5 | 4 |
| Assist | 3 | 3 | 3 | 3 |
| Clean sheet (while on the pitch; subbed off after 60 keeps it) | 4 | 4 | 1 | 0 |
| Goals conceded while on pitch | -1 per 2 | -1 per 2 | 0 | 0 |
| Shot on target | 1.0 (not modelled) | 0.6 | 0.4 | 0.4 |
| Save | 0.5 each | - | - | - |
| Full-match bonus | - | - | +1 | +1 |
Win while on pitch +0.3, loss -0.3. Yellow -1, red -3 (a red replaces a yellow). No FPL-style bonus points.
Open (from EPL): does the full-match bonus need start and finish, or just being on at full time?
TBC (2021 article, not FanTeam): no shot-on-target points when that shot is a goal or gives an assist. Check against data.
The FanTeam API has no scoring table (probe 24 Nov, `data/ref/fanteam_rules_probe.md`): confirm scoring from raw stats v points.

## Model rules (v1)
- Bookmaker prices first. Remove margin; mean of books.
- Goals: anytime scorer. Shots, SoT, assists, tackles, cards: player props.
- Clean sheet, goals conceded, win: score grid fitted to team markets.
- Team totals anchor players: a team's player goals and assists add up to its expected goals.
- Saves: opponent expected SoT minus expected goals (saves props too thin).
- Start chance is the weakest input. Recheck once XIs are out.
- No domestic-league history in v1. New factors start as flags (see PLAN.md).

## Bookmaker facts (The Odds API, probe 24 Nov 2026: `data/ref/ucl_props_probe.md`)
- Sport key `soccer_uefa_champs_league`. Player props up about a day before kick-off.
- Anytime scorer: 5-6 books (betrivers, betway, draftkings, fanduel, onexbet, mybookieag). No Pinnacle or Betfair on player props.
- Shots / SoT: betrivers, fanduel, onexbet (+ betway, draftkings alternates). Assists: fanduel Over 0.5 + betrivers/betway alternates.
- Tackles: draftkings only. Saves: 3-4 GKs only. Cards: betway, draftkings.
- Team markets deep: h2h ~48 books, totals ~24, BTTS ~16 (Pinnacle present). Team totals thin: fanduel (+ mybookieag).
- Yes/Over-only markets: 1/price includes the margin.
- Match names on an accent-insensitive key (e.g. Bodø/Glimt, ŠK Slovan Bratislava).
- The key is shared with the NBA and EPL repos. Log credits left after each run.
- Cost of `fetch_props.py` (estimate from markets x regions, to be checked against real runs): about 21 credits per game + 4 per run.
  A 9-game night about 190. Billing counts only markets that return data.
- Not yet checked: coverage for the smallest clubs, real cost of a full 18-game pull.

## Data policy (public repo)
- Raw bookmaker prices: committed (owner decision A, 24 Nov 2026). Review at stage 4.
- FanTeam standings: only rank, score, payout are saved. No user names, ids or entry names.
- No keys, tokens, account details or personal names in any file or Action log.
