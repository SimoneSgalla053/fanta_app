# FantaApp Pro Wiki

FantaApp Pro is a local auction dashboard built with Python, NiceGUI, and SQLite. It tracks player assignments and prices for every team while calculating live market values and a maximum suggested price for the configured personal team.

![FantaApp Pro dashboard showing auction credits, roster slots, spending, and role budgets](imgs/dashboard.png)

## Main features

- Dashboard with remaining credits, roster slots, and personal budget progress.
- Separate markets for goalkeepers, defenders, midfielders, and attackers.
- Search and assigned-player filtering.
- Official player portraits cached locally and served by the app.
- Explicit assignment dialog that saves team and paid price together.
- Team roster, spending totals, role subtotals, and charts.
- Automatic Fantacalcio quotation updates at startup.
- Automatic removal of obsolete players from team rosters.
- Guarded full-team reset with a timestamped SQLite backup.

## Wiki pages

- [Getting Started](Getting-Started.md)
- [Using the App](Using-the-App.md)
- [Configuration](Configuration.md)
- [Data and Updates](Data-and-Updates.md)
- [Architecture](Architecture.md)
- [Troubleshooting](Troubleshooting.md)

## Important data note

The `db/` directory is ignored by Git. Team assignments, paid prices, generated player tables, image caches, and reset backups remain local to the machine running the app.

## Publishing to GitHub Wiki

These pages use GitHub Wiki-compatible filenames, including `_Sidebar.md`. They are versioned in this repository under `wiki/`. To display them in a repository's GitHub **Wiki** tab, enable Wikis in the repository settings and copy the contents of `wiki/` into the separate `<repository>.wiki.git` repository.
