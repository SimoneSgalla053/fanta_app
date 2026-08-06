# Configuration

Auction settings are defined in `config.py`.

## League and budget

```python
PLAYERS_NUMBER = 8
MAX_CREDIT_AMOUNT = 500
TOTAL_CREDITS_AMOUNT = MAX_CREDIT_AMOUNT * PLAYERS_NUMBER
MY_TEAM = "team_simo"
```

- `PLAYERS_NUMBER`: number of fantasy teams used to derive total auction credits.
- `MAX_CREDIT_AMOUNT`: starting credits per team.
- `TOTAL_CREDITS_AMOUNT`: total credits available across the league.
- `MY_TEAM`: team used for personal maximum-price calculations and dashboard progress.

`MY_TEAM` must match an existing SQLite table name.

## Roster slots

```python
NUMBER_OF_PLAYERS_PER_ROLE = {
    "goalkeepers": 3,
    "defenders": 8,
    "midfielders": 8,
    "attackers": 6,
}
```

These values determine full roster size, open slots, and personal role progress.

## Role budgets

```python
MAX_CREDIT_PER_ROLE = {
    "goalkeepers": 50,
    "defenders": 100,
    "midfielders": 100,
    "attackers": 250,
}
```

Unused budget rolls into later roles only after every slot in all earlier roles is filled. Role order follows the dictionary order above.

## Multipliers

`STANDARD_ROLE_MULTIPLIERS` controls the market valuation weighting per role. It is derived from role budget, role slots, and a divisor of 20.

Restart the app after changing configuration.
