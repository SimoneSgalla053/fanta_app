# Troubleshooting

## The app does not start

Activate the virtual environment and verify NiceGUI:

```bash
source .venv/bin/activate
python -c "import nicegui; print(nicegui.__version__)"
python -m py_compile fe.py backend.py populate_players.py config.py
```

Run commands from the project root because database paths are relative to the current directory.

## `no such table: team_simo`

The team database is missing or `MY_TEAM` does not match a table. Follow the initializer in [Getting Started](Getting-Started.md), then confirm `MY_TEAM` in `config.py`.

## Player update failed

The app keeps existing local data and prints the error. Check internet access, then try:

```bash
python populate_players.py
```

Fantacalcio may have changed its HTML or image URL format. Relevant constants and parsing logic are in `populate_players.py`.

## Portraits are missing

Confirm images exist:

```bash
find list/images -type f -name '*.png' | wc -l
```

Then run `python populate_players.py`. Missing individual portraits are nonfatal and use an initials fallback in the UI.

## Port already in use

Choose another port:

```bash
PORT=8099 python fe.py
```

## Assignment does not save

In the assignment dialog:

- Paid price must be greater than zero.
- A team must be selected.
- Select **Save assignment** after both fields are complete.

## Recover after resetting teams

Reset backups are stored in `db/teams_dataset/backups/`. Stop the app before restoring a backup:

```bash
cp db/teams_dataset/backups/teams_YYYYMMDD_HHMMSS.db db/teams_dataset/teams.db
```

Keep an additional copy of the current database before replacing it.

## CSV changes appear in Git

The role CSV files are tracked and are rewritten by successful updates. Review the quotation changes before committing. Generated databases and portrait caches are ignored.
