# UEFA API probe 2026-11-24 12:52 UTC

- match list: 234 matches, 162 finished; statuses ['FINISHED', 'UPCOMING']
- probe match: 2049556 ('Club Brugge', 'Aston Villa', '2026-09-08T16:45:00Z')

endpoint | status | bytes | items
---|---|---|---
match | 200 | 34397 | dict: awayTeam,competition,competitionPhase,condition,fullTimeAt,group,homeTeam,id,kickOffTime,lineupStatus
lineups | 200 | 86336 | dict: awayTeam,homeTeam,lineupStatus,matchId
events | 400 | 0 | 
matchstats_v1_players | 200 | 5285052 | list 44
matchstats_v2_players | 200 | 1100656 | list 44
matchstats_v1_teams | 200 | 351238 | list 2
compstats_player_stats_match | 404 | 0 | 
compstats_ranking_match | 200 | 273689 | list 50
compstats_ranking_season | 200 | 273689 | list 50

## Shapes

### match
https://match.uefa.com/v5/matches/2049556
```
{
 "awayTeam": {
  "associationId": "str",
  "associationLogoUrl": "str",
  "bigLogoUrl": "str",
  "confederationType": "str",
  "countryCode": "str",
  "id": "str",
  "idProvider": "str",
  "internationalName": "str",
  "isPlaceHolder": "bool",
  "logoUrl": "str",
  "mediumLogoUrl": "str",
  "organizationId": "str",
  "teamCode": "str",
  "teamTypeDetail": "str",
  "translations": {
   "countryName": {
    "EN": "...",
    "FR": "...",
    "DE": "...",
    "ES": "...",
    "PT": "...",
    "IT": "...",
    "RU": "...",
    "ZH": "...",
    "AR": "..."
   },
   "displayName": {
    "EN": "...",
    "FR": "...",
    "DE": "...",
    "ES": "...",
    "PT": "...",
    "IT": "...",
    "RU": "...",
    "ZH": "...",
    "AR": "..."
   },
   "displayOfficialName": {
    "EN": "...",
    "FR": "...",
    "DE": "...",
    "ES": "...",
    "PT": "...",
    "IT": "...",
    "RU": "...",
    "ZH": "...",
    "AR": "..."
   },
   "displayTeamCode": {
    "EN": "...",
    "FR": "...",
    "DE": "...",
    "ES": "...",
    "PT": "...",
    "IT": "...",
    "RU": "...",
    "ZH": "...",
    "AR": "..."
   },
   "shortName": {
    "EN": "...",
    "FR": "...",
    "DE": "...",
    "ES": "...",
    "PT": "...",
    "IT": "...",
    "RU": "...",
    "ZH": "...",
    "AR": "..."
   }
  },
  "typeIsNational": "bool",
  "typeTeam": "str"
 },
 "competition": {
  "age": "str",
  "code": "str",
  "id": "str",
  "images": {
   "FULL_LOGO": "str"
  },
  "metaData": {
   "name": "str"
  },
  "region": "str",
  "sex": "str",
  "sportsType": "str",
  "teamCategory": "str",
  "translations": {
   "name": {
    "EN": "...",
    "FR": "...",
    "DE": "...",
    "ES": "...",
    "PT": "...",
    "IT": "...",
    "RU": "...",
    "ZH": "...",
    "AR": "..."
   },
   "prequalifyingName": {
    "EN": "...",
    "FR": "...",
    "DE": "...",
    "ES": "...",
    "PT": "...",
    "IT": "...",
    "RU": "...",
    "ZH": "...",
    "AR": "..."
   },
   "qualifyingName": {
    "EN": "...",
    "FR": "...",
    "DE": "...",
    "ES": "...",
    "PT": "...",
    "IT": "...",
    "RU": "...",
    "ZH": "...",
    "AR": "..."
   },
   "shortName": {},
   "tournamentName": {
    "EN": "...",
    "FR": "...",
    "DE": "...",
    "ES": "...",
    "PT": "...",
    "IT": "...",
    "RU": "...",
    "ZH": "...",
    "AR": "..."
   }
  },
  "type": "str"
 },
 "competitionPhase": "str",
 "condition": {
  "humidity": "int",
  "pitchCondition": "str",
  "temperature": "int",
  "translations": {
   "pitchConditionName": {
    "EN": "...",
    "FR": "...",
    "DE": "...",
    "ES": "...",
    "PT": "...",
    "IT": "...",
    "RU": "...",
    "ZH": "...",
    "AR": "..."
   },
   "weatherConditionName": {
    "EN": "...",
    "FR": "...",
    "DE": "...",
    "ES": "...",
    "PT": "...",
    "IT": "...",
    "RU": "...",
    "ZH": "...",
    "AR": "..."
   }
  },
  "weatherCondition": "str",
  "windSpeed": "int"
 },
 "fullTimeAt": "str",
 "group": {
  "competitionId": "str",
  "id": "str",
  "meta
```

### lineups
https://match.uefa.com/v5/matches/2049556/lineups
```
{
 "awayTeam": {
  "bench": [
   10,
   {
    "isLateUpdate": "...",
    "jerseyNumber": "...",
    "player": "...",
    "type": "..."
   }
  ],
  "coaches": [
   1,
   {
    "imageUrl": "...",
    "person": "...",
    "role": "...",
    "translations": "..."
   }
  ],
  "field": [
   11,
   {
    "fieldCoordinate": "...",
    "fspFieldCoordinate": "...",
    "isLateUpdate": "...",
    "jerseyNumber": "...",
    "player": "...",
    "type": "..."
   }
  ],
  "kitImageUrl": "str",
  "shirtColor": "str",
  "team": {
   "associationId": "str",
   "associationLogoUrl": "str",
   "bigLogoUrl": "str",
   "confederationType": "str",
   "countryCode": "str",
   "id": "str",
   "idProvider": "str",
   "internationalName": "str",
   "isPlaceHolder": "bool",
   "logoUrl": "str",
   "mediumLogoUrl": "str",
   "organizationId": "str",
   "teamCode": "str",
   "teamTypeDetail": "str",
   "translations": {
    "countryName": "...",
    "displayName": "...",
    "displayOfficialName": "...",
    "displayTeamCode": "...",
    "shortName": "..."
   },
   "typeIsNational": "bool",
   "typeTeam": "str"
  }
 },
 "homeTeam": {
  "bench": [
   12,
   {
    "isLateUpdate": "...",
    "jerseyNumber": "...",
    "player": "...",
    "type": "..."
   }
  ],
  "coaches": [
   1,
   {
    "imageUrl": "...",
    "person": "...",
    "role": "...",
    "translations": "..."
   }
  ],
  "field": [
   11,
   {
    "fieldCoordinate": "...",
    "fspFieldCoordinate": "...",
    "isLateUpdate": "...",
    "jerseyNumber": "...",
    "player": "...",
    "type": "..."
   }
  ],
  "kitImageUrl": "str",
  "shirtColor": "str",
  "team": {
   "associationId": "str",
   "associationLogoUrl": "str",
   "bigLogoUrl": "str",
   "confederationType": "str",
   "countryCode": "str",
   "id": "str",
   "idProvider": "str",
   "internationalName": "str",
   "isPlaceHolder": "bool",
   "logoUrl": "str",
   "mediumLogoUrl": "str",
   "organizationId": "str",
   "teamCode": "str",
   "teamTypeDetail": "str",
   "translations": {
    "countryName": "...",
    "displayName": "...",
    "displayOfficialName": "...",
    "displayTeamCode": "...",
    "shortName": "..."
   },
   "typeIsNational": "bool",
   "typeTeam": "str"
  }
 },
 "lineupStatus": "str",
 "matchId": "str"
}
```

### matchstats_v1_players
https://matchstats.uefa.com/v1/player-statistics/2049556
```
[
 44,
 {
  "idProvider": "str",
  "playerId": "str",
  "statistics": [
   4,
   {
    "name": "...",
    "translations": "...",
    "value": "..."
   }
  ],
  "teamId": "str"
 }
]
```

### matchstats_v2_players
https://matchstats.uefa.com/v2/player-statistics/2049556
```
[
 44,
 {
  "idProvider": "str",
  "playerId": "str",
  "statistics": [
   4,
   {
    "name": "...",
    "value": "..."
   }
  ],
  "teamId": "str"
 }
]
```

### matchstats_v1_teams
https://matchstats.uefa.com/v1/team-statistics/2049556
```
[
 2,
 {
  "idProvider": "str",
  "statistics": [
   429,
   {
    "name": "...",
    "translations": "...",
    "value": "..."
   }
  ],
  "teamId": "str"
 }
]
```

### compstats_ranking_match
https://compstats.uefa.com/v1/player-ranking
```
[
 50,
 {
  "idProvider": "str",
  "player": {
   "age": "str",
   "birthDate": "str",
   "clubId": "str",
   "clubJerseyNumber": "str",
   "clubShirtName": "str",
   "countryCode": "str",
   "detailedFieldPosition": "str",
   "fieldPosition": "str",
   "gender": "str",
   "height": "int",
   "id": "str",
   "imageUrl": "str",
   "internationalName": "str",
   "nationalFieldPosition": "str",
   "nationalJerseyNumber": "str",
   "nationalShirtName": "str",
   "nationalTeamId": "str",
   "translations": {
    "countryName": "...",
    "fieldPosition": "...",
    "firstName": "...",
    "lastName": "...",
    "name": "...",
    "nationalFieldPosition": "...",
    "shortName": "..."
   },
   "weight": "int"
  },
  "playerId": "str",
  "statistics": [
   8,
   {
    "name": "...",
    "translations": "...",
    "unit": "...",
    "value": "..."
   }
  ],
  "team": {
   "associationId": "str",
   "associationLogoUrl": "str",
   "bigLogoUrl": "str",
   "confederationType": "str",
   "countryCode": "str",
   "id": "str",
   "idProvider": "str",
   "internationalName": "str",
   "isPlaceHolder": "bool",
   "logoUrl": "str",
   "mediumLogoUrl": "str",
   "organizationId": "str",
   "teamCode": "str",
   "teamTypeDetail": "str",
   "translations": {
    "countryName": "...",
    "displayName": "...",
    "displayOfficialName": "...",
    "displayTeamCode": "...",
    "shortName": "..."
   },
   "typeIsNational": "bool",
   "typeTeam": "str"
  },
  "teamId": "str"
 }
]
```

### compstats_ranking_season
https://compstats.uefa.com/v1/player-ranking
```
[
 50,
 {
  "idProvider": "str",
  "player": {
   "age": "str",
   "birthDate": "str",
   "clubId": "str",
   "clubJerseyNumber": "str",
   "clubShirtName": "str",
   "countryCode": "str",
   "detailedFieldPosition": "str",
   "fieldPosition": "str",
   "gender": "str",
   "height": "int",
   "id": "str",
   "imageUrl": "str",
   "internationalName": "str",
   "nationalFieldPosition": "str",
   "nationalJerseyNumber": "str",
   "nationalShirtName": "str",
   "nationalTeamId": "str",
   "translations": {
    "countryName": "...",
    "fieldPosition": "...",
    "firstName": "...",
    "lastName": "...",
    "name": "...",
    "nationalFieldPosition": "...",
    "shortName": "..."
   },
   "weight": "int"
  },
  "playerId": "str",
  "statistics": [
   8,
   {
    "name": "...",
    "translations": "...",
    "unit": "...",
    "value": "..."
   }
  ],
  "team": {
   "associationId": "str",
   "associationLogoUrl": "str",
   "bigLogoUrl": "str",
   "confederationType": "str",
   "countryCode": "str",
   "id": "str",
   "idProvider": "str",
   "internationalName": "str",
   "isPlaceHolder": "bool",
   "logoUrl": "str",
   "mediumLogoUrl": "str",
   "organizationId": "str",
   "teamCode": "str",
   "teamTypeDetail": "str",
   "translations": {
    "countryName": "...",
    "displayName": "...",
    "displayOfficialName": "...",
    "displayTeamCode": "...",
    "shortName": "..."
   },
   "typeIsNational": "bool",
   "typeTeam": "str"
  },
  "teamId": "str"
 }
]
```
