# Getting Started

## Requirements

- Python 3.12 or later
- Internet access during startup for quotation and portrait updates
- NiceGUI 3.15.0 (the currently verified version)

## Install

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install nicegui==3.15.0
```

## Initialize teams

The SQLite databases are local and excluded from Git. Before the first launch, create the team tables:

```bash
python - <<'PY'
import sqlite3
from pathlib import Path

teams = [
    "giaco",
    "schiaro",
    "nico",
    "jack",
    "ivo",
    "giacca",
    "sebastian",
    "simo",
]
path = Path("db/teams_dataset/teams.db")
path.parent.mkdir(parents=True, exist_ok=True)
with sqlite3.connect(path) as database:
    for team in teams:
        database.execute(f"""
            CREATE TABLE IF NOT EXISTS team_{team} (
                name TEXT PRIMARY KEY,
                role TEXT NOT NULL,
                paid_value INTEGER DEFAULT 0
            )
        """)
PY
```

Change the names in `teams` before running the command if your league uses different teams. Table names must use the `team_` prefix.

## Run

```bash
python fe.py
```

Open `http://localhost:8080`. To use another port:

```bash
PORT=8099 python fe.py
```

At startup the app downloads current Fantacalcio quotations, updates the CSV files, downloads missing portraits, rebuilds the player database, and removes obsolete roster assignments. If downloading fails, startup continues with the existing local data.

## Stop

Press `Ctrl+C` in the terminal running the app.
