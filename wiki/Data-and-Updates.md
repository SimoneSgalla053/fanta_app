# Data and Updates

## Startup update

Importing `fe.py` calls `update_players()` before the UI is created. The updater:

1. Downloads the public Fantacalcio quotation page.
2. Parses the server-rendered player table.
3. Validates minimum player counts for all four roles.
4. Rewrites the semicolon-separated role CSV files.
5. Downloads missing official PNG portraits concurrently.
6. Rebuilds all four player tables in SQLite.
7. Removes roster entries whose `(name, role)` no longer exists.

A failed download or validation is reported in the terminal, and the app continues with existing local data.

## Sources

- Quotations: `https://www.fantacalcio.it/quotazioni-fantacalcio`
- Portraits: Fantacalcio's public content CDN, using season and player IDs parsed from the quotation page.

External page or markup changes can break parsing. See [Troubleshooting](Troubleshooting.md).

## Local files

```text
list/goalkeepers.csv
list/defenders.csv
list/midfielders.csv
list/attackers.csv
list/images/<season>/<player_id>.png
db/player_dataset/players.db
db/teams_dataset/teams.db
```

Portraits already present and non-empty are not downloaded again.

## Player database

Each role has a separate table with:

- `name`
- `team` (the real Serie A club)
- `rating` (normalized from `Qt.A`)
- `player_id`
- `image_path`

## Team database

Each fantasy team is a separate table named `team_<name>` with:

- `name`
- `role`
- `paid_value`

When current player data no longer contains an assigned `(name, role)`, that team row is deleted after a successful refresh.

## Manual update

Run the updater without starting the UI:

```bash
python populate_players.py
```

The terminal reports player counts, available portraits, and stale assignments removed.

## Backups

A full team reset creates a timestamped database backup in `db/teams_dataset/backups/`. Automatic player updates do not create a team backup before stale-player cleanup.
