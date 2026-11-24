# Scoring check: UEFA stats scored with the rules table v FanTeam points

- MD2: clubs mapped 28/28; linked players with minutes 428; FanTeam non-zero players not linked 6; exact 21, off by exactly 0.3 (impact) 182, other 16
- MD3: clubs mapped 28/28; linked players with minutes 428; FanTeam non-zero players not linked 7; exact 43, off by exactly 0.3 (impact) 159, other 14
- MD4: clubs mapped 14/14; linked players with minutes 209; FanTeam non-zero players not linked 4; exact 6, off by exactly 0.3 (impact) 92, other 10

- ALL (excludes 522 GK/DEF/MID rows subbed on or off: clean sheet unknown): 543 player-matches; 503 (93%) match the table exactly or within the +-0.3 impact term; mean residual -0.00

## Biggest residuals (FanTeam minus model; impact +-0.3 not modelled)

md | player | club | pos | min | started | G | A | SoT | GC | sv | FanTeam | model | diff
---|---|---|---|---|---|---|---|---|---|---|---|---|---
2 | Ángel Ortiz | BET | DEF | 90 | 1 | 0 | 0 | 1 | 0 | 0 | 3.9 | 0.6 | +3.3
3 | Abde Ezzalzouli | BET | MID | 90 | 1 | 0 | 0 | 2 | 0 | 0 | 8.1 | 4.8 | +3.3
2 | Carlos Forbs | BRU | MID | 90 | 1 | 0 | 3 | 1 | 0 | 0 | 15.7 | 12.4 | +3.3
2 | Konrad Laimer | FCB | DEF | 90 | 1 | 0 | 1 | 0 | 0 | 0 | 6.0 | 3.0 | +3.0
2 | Ivan Perišić | PSV | MID | 90 | 1 | 0 | 0 | 1 | 0 | 0 | 1.1 | 3.4 | -2.3
2 | Ferran Torres | PSG | FOR | 14 | 0 | 0 | 0 | 1 | 0 | 0 | -0.6 | 1.4 | -2.0
4 | Zlatko Tripić | VIK | MID | 90 | 1 | 1 | 1 | 3 | 0 | 0 | 10.1 | 11.8 | -1.7
2 | Fábio Silva | BVB | FOR | 60 | 1 | 0 | 0 | 0 | 0 | 0 | -0.3 | 1.0 | -1.3
2 | Oğuz Aydın | FEN | MID | 90 | 1 | 0 | 0 | 2 | 0 | 0 | 1.7 | 2.8 | -1.1
3 | Georges Mikautadze | VIL | FOR | 60 | 1 | 1 | 0 | 1 | 0 | 0 | 5.0 | 6.0 | -1.0
3 | Achraf Hakimi | PSG | DEF | 90 | 1 | 0 | 1 | 1 | 0 | 0 | 5.5 | 4.6 | +0.9
2 | Alberto Brignoli | AEK | GOA | 90 | 1 | 0 | 0 | 0 | 3 | 2 | 1.2 | 2.0 | -0.8
2 | Ederson | FEN | GOA | 90 | 1 | 0 | 0 | 0 | 6 | 6 | 1.2 | 2.0 | -0.8
4 | Álvaro Vallés | BET | GOA | 90 | 1 | 0 | 0 | 0 | 2 | 5 | 2.7 | 3.5 | -0.8
4 | Maarten Vandevoordt | RBL | GOA | 90 | 1 | 0 | 0 | 0 | 3 | 4 | 2.2 | 3.0 | -0.8
4 | Stas Pokatilov | SABA | GOA | 90 | 1 | 0 | 0 | 0 | 4 | 4 | 6.2 | 7.0 | -0.8
4 | Nazar Domchak | SLA | GOA | 90 | 1 | 0 | 0 | 0 | 2 | 4 | 2.2 | 3.0 | -0.8
2 | Matvei Safonov | PSG | GOA | 90 | 1 | 0 | 0 | 0 | 2 | 8 | 4.3 | 5.0 | -0.7
3 | João Neves | PSG | MID | 90 | 1 | 0 | 1 | 0 | 0 | 0 | 6.7 | 6.0 | +0.7
3 | Allan Elias | MCI | MID | 90 | 1 | 0 | 0 | 0 | 0 | 0 | 3.7 | 3.0 | +0.7
3 | Nicolas Jackson | AVL | FOR | 70 | 1 | 0 | 0 | 2 | 0 | 0 | 3.5 | 2.8 | +0.7
4 | David Raya | ARS | GOA | 90 | 1 | 0 | 0 | 0 | 1 | 6 | 4.3 | 5.0 | -0.7
4 | Máximo Perrone | COM | MID | 90 | 1 | 0 | 1 | 0 | 0 | 0 | 6.7 | 6.0 | +0.7
4 | Mojmír Chytil | SLA | FOR | 45 | 0 | 0 | 0 | 0 | 0 | 0 | 1.7 | 1.0 | +0.7
2 | Zion Suzuki | AVL | GOA | 90 | 1 | 0 | 0 | 0 | 0 | 6 | 8.3 | 9.0 | -0.7
2 | Vitinha | PSG | MID | 90 | 1 | 1 | 0 | 2 | 0 | 0 | 9.1 | 8.4 | +0.7
3 | Kylian Mbappé | RMA | FOR | 88 | 1 | 1 | 1 | 1 | 0 | 0 | 9.7 | 9.0 | +0.7
2 | Arild Østbø | VIK | GOA | 90 | 1 | 0 | 0 | 0 | 3 | 6 | 3.5 | 4.0 | -0.5
3 | David Raya | ARS | GOA | 90 | 1 | 0 | 0 | 0 | 2 | 4 | 2.5 | 3.0 | -0.5
2 | Harry Kane | FCB | FOR | 90 | 1 | 2 | 0 | 5 | 0 | 0 | 11.8 | 12.2 | -0.4
2 | Alejandro Grimaldo | ATM | DEF | 90 | 1 | 0 | 0 | 1 | 0 | 0 | 6.9 | 6.6 | +0.3
2 | Jan Oblak | ATM | GOA | 90 | 1 | 0 | 0 | 0 | 0 | 4 | 8.3 | 8.0 | +0.3
2 | João Cancelo | BAR | DEF | 90 | 1 | 1 | 0 | 2 | 0 | 0 | 8.9 | 8.6 | +0.3
2 | Lamine Yamal | BAR | MID | 90 | 1 | 0 | 2 | 0 | 0 | 0 | 9.3 | 9.0 | +0.3
2 | Nicolò Tresoldi | BRU | FOR | 83 | 1 | 3 | 0 | 3 | 0 | 0 | 14.3 | 14.0 | +0.3
2 | Willi Orbán | RBL | DEF | 90 | 1 | 0 | 0 | 1 | 0 | 0 | 6.9 | 6.6 | +0.3
2 | Santiago Mouriño | VIL | DEF | 90 | 1 | 1 | 0 | 1 | 0 | 0 | 8.3 | 8.0 | +0.3
2 | Matty Cash | AVL | DEF | 90 | 1 | 0 | 0 | 1 | 0 | 0 | 6.9 | 6.6 | +0.3
2 | Nikita Haikin | BOD | GOA | 90 | 1 | 0 | 0 | 0 | 0 | 4 | 8.3 | 8.0 | +0.3
2 | Fredrik Sjøvold | BOD | DEF | 90 | 1 | 1 | 0 | 1 | 0 | 0 | 12.3 | 12.0 | +0.3

## Residual counts (rounded to 0.1)

-0.8: 6, -0.7: 3, -0.3: 220, -0.1: 3, +0.0: 70, +0.2: 3, +0.3: 213, +0.7: 7, +3.3: 3
