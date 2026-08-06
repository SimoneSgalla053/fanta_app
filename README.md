# FantaApp Pro

A local NiceGUI application for managing a Fantacalcio auction, team rosters, budgets, player valuations, and current Serie A quotation data.

## Documentation

Start with the [project wiki](wiki/Home.md).

- [Getting started](wiki/Getting-Started.md)
- [Using the app](wiki/Using-the-App.md)
- [Configuration](wiki/Configuration.md)
- [Data and updates](wiki/Data-and-Updates.md)
- [Architecture](wiki/Architecture.md)
- [Troubleshooting](wiki/Troubleshooting.md)

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install nicegui==3.15.0
```

Complete the one-time team database initialization in [Getting started](wiki/Getting-Started.md), then run `python fe.py`. The app opens at `http://localhost:8080`.
