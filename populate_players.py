import csv
import math
import os
import re
import sqlite3
import tempfile
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

MIN_OUT = 10.0
MAX_OUT = 100.0
MAX_QT = 35.0  # Top Fantacalcio Qt.A ceiling
K_EXP = 0.72  # Curve shape factor

QUOTATIONS_URL = "https://www.fantacalcio.it/quotazioni-fantacalcio"
PLAYER_IMAGE_URL = "https://content.fantacalcio.it/web/campioncini/{season}/card/{player_id}.png"
CSV_HEADER = [
    "Id",
    "R",
    "RM",
    "Nome",
    "Squadra",
    "Qt.A",
    "Qt.I",
    "Diff.",
    "Qt.A M",
    "Qt.I M",
    "Diff.M",
    "FVM",
    "FVM M",
]
ROLE_FILES = {
    "P": ("goalkeepers", "goalkeepers.csv"),
    "D": ("defenders", "defenders.csv"),
    "C": ("midfielders", "midfielders.csv"),
    "A": ("attackers", "attackers.csv"),
}
MINIMUM_ROLE_COUNTS = {"P": 20, "D": 50, "C": 50, "A": 50}


def normalize_rating(qt_a: int) -> int:
    """Normalize Qt.A to a score between 10 and 100."""
    if qt_a <= 1:
        return int(MIN_OUT)

    value = min(float(qt_a), MAX_QT)
    log_ratio = math.log(value) / math.log(MAX_QT)
    normalized = MIN_OUT + (MAX_OUT - MIN_OUT) * (log_ratio**K_EXP)
    return round(normalized)


class QuotationsParser(HTMLParser):
    """Parse the server-rendered Fantacalcio quotation table."""

    def __init__(self) -> None:
        super().__init__()
        self.players: list[dict[str, str]] = []
        self._player: dict[str, str] | None = None
        self._field: str | None = None
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())

        if tag == "tr" and "player-row" in classes:
            self._player = {
                "R": (attributes.get("data-filter-role-classic") or "").upper(),
                "RM": attributes.get("data-filter-role-mantra") or "",
            }
            return
        if self._player is None:
            return

        if tag == "a" and "player-link" in classes:
            href = attributes.get("href") or ""
            match = re.search(r"/squadre/([^/]+)/[^/]+/(\d+)$", href)
            if match:
                self._player["Squadra"] = match.group(1).replace("-", " ").title()
                self._player["Id"] = match.group(2)
        elif tag in {"th", "td"}:
            field_by_class = {
                "player-name": "Nome",
                "player-team": "Squadra breve",
                "player-classic-initial-price": "Qt.I",
                "player-classic-current-price": "Qt.A",
                "player-classic-fvm": "FVM",
                "player-mantra-initial-price": "Qt.I M",
                "player-mantra-current-price": "Qt.A M",
                "player-mantra-fvm": "FVM M",
            }
            self._field = next(
                (field_by_class[name] for name in classes if name in field_by_class), None
            )
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self._player is not None and self._field:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._player is None:
            return
        if tag in {"th", "td"} and self._field:
            value = " ".join("".join(self._parts).split())
            if value and (self._field != "Squadra breve" or "Squadra" not in self._player):
                self._player[self._field] = value
            self._field = None
            self._parts = []
        elif tag == "tr":
            if all(key in self._player for key in ("Id", "R", "Nome", "Squadra", "Qt.A")):
                self.players.append(self._player)
            self._player = None


def download_latest_players(timeout: float = 20.0) -> tuple[dict[str, list[list[str]]], str]:
    request = Request(
        QUOTATIONS_URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; FantaApp/1.0)"},
    )
    with urlopen(request, timeout=timeout) as response:
        html = response.read().decode("utf-8")

    season_match = re.search(r"/api/v1/Excel/prices/(\d+)/1", html)
    if not season_match:
        raise ValueError("Could not determine the current Fantacalcio season")
    season_id = season_match.group(1)

    parser = QuotationsParser()
    parser.feed(html)

    rows_by_role = {role: [] for role in ROLE_FILES}
    for player in parser.players:
        role = player["R"]
        if role not in rows_by_role:
            continue
        try:
            current = int(player["Qt.A"])
            initial = int(player["Qt.I"])
            mantra_current = int(player["Qt.A M"])
            mantra_initial = int(player["Qt.I M"])
        except (KeyError, ValueError):
            continue
        rows_by_role[role].append(
            [
                player["Id"],
                role,
                player.get("RM", ""),
                player["Nome"],
                player["Squadra"],
                str(current),
                str(initial),
                str(current - initial),
                str(mantra_current),
                str(mantra_initial),
                str(mantra_current - mantra_initial),
                player.get("FVM", "0"),
                player.get("FVM M", "0"),
            ]
        )

    for role, minimum in MINIMUM_ROLE_COUNTS.items():
        if len(rows_by_role[role]) < minimum:
            raise ValueError(
                f"Downloaded data failed validation for role {role}: "
                f"found {len(rows_by_role[role])}, expected at least {minimum}"
            )
    return rows_by_role, season_id


def _download_player_images(
    rows_by_role: dict[str, list[list[str]]], image_dir: Path, season_id: str
) -> int:
    season_dir = image_dir / season_id
    season_dir.mkdir(parents=True, exist_ok=True)
    player_ids = [row[0] for rows in rows_by_role.values() for row in rows]

    def download_image(player_id: str) -> bool:
        destination = season_dir / f"{player_id}.png"
        if destination.exists() and destination.stat().st_size > 0:
            return True

        request = Request(
            PLAYER_IMAGE_URL.format(season=season_id, player_id=player_id),
            headers={"User-Agent": "Mozilla/5.0 (compatible; FantaApp/1.0)"},
        )
        temporary: Path | None = None
        try:
            with urlopen(request, timeout=15.0) as response:
                if response.headers.get_content_type() != "image/png":
                    return False
                image = response.read()
            if not image.startswith(b"\x89PNG\r\n\x1a\n"):
                return False
            with tempfile.NamedTemporaryFile(
                mode="wb", dir=season_dir, prefix=f".{player_id}.", delete=False
            ) as file:
                file.write(image)
                temporary = Path(file.name)
            os.replace(temporary, destination)
            return True
        except (OSError, ValueError):
            return False
        finally:
            if temporary:
                temporary.unlink(missing_ok=True)

    with ThreadPoolExecutor(max_workers=12) as executor:
        return sum(executor.map(download_image, player_ids))


def _write_csv_files(rows_by_role: dict[str, list[list[str]]], list_dir: Path) -> None:
    list_dir.mkdir(parents=True, exist_ok=True)
    temporary_files: list[tuple[Path, Path]] = []
    try:
        for role, (_, filename) in ROLE_FILES.items():
            destination = list_dir / filename
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="",
                dir=list_dir,
                prefix=f".{filename}.",
                delete=False,
            ) as file:
                writer = csv.writer(file, delimiter=";", lineterminator="\n")
                writer.writerow(["Quotazioni Fantacalcio - aggiornamento automatico"] + [""] * 12)
                writer.writerow(CSV_HEADER)
                writer.writerows(rows_by_role[role])
                temporary_files.append((Path(file.name), destination))

        for temporary, destination in temporary_files:
            os.replace(temporary, destination)
    finally:
        for temporary, _ in temporary_files:
            temporary.unlink(missing_ok=True)


def _rebuild_database(
    rows_by_role: dict[str, list[list[str]]], db_path: Path, image_dir: Path, season_id: str
) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        for role, (table_name, _) in ROLE_FILES.items():
            connection.execute(f"DROP TABLE IF EXISTS {table_name}")
            connection.execute(f"""
                CREATE TABLE {table_name} (
                    name TEXT PRIMARY KEY NOT NULL,
                    team TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    player_id TEXT NOT NULL,
                    image_path TEXT
                )
                """)
            players = [
                (
                    row[3],
                    row[4],
                    normalize_rating(int(row[5])),
                    row[0],
                    (
                        f"{season_id}/{row[0]}.png"
                        if (image_dir / season_id / f"{row[0]}.png").exists()
                        else None
                    ),
                )
                for row in rows_by_role[role]
            ]
            connection.executemany(
                f"""INSERT OR IGNORE INTO {table_name}
                    (name, team, rating, player_id, image_path) VALUES (?, ?, ?, ?, ?)""",
                players,
            )


def update_players(base_dir: str | Path | None = None) -> dict[str, int]:
    """Download current players and portraits, then rebuild local data."""
    project_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent
    rows_by_role, season_id = download_latest_players()
    image_dir = project_dir / "list/images"
    _write_csv_files(rows_by_role, project_dir / "list")
    image_count = _download_player_images(rows_by_role, image_dir, season_id)
    _rebuild_database(
        rows_by_role,
        project_dir / "db/player_dataset/players.db",
        image_dir,
        season_id,
    )
    print(f"Player portraits available: {image_count}")
    return {ROLE_FILES[role][0]: len(rows) for role, rows in rows_by_role.items()}


if __name__ == "__main__":
    counts = update_players()
    print(
        "Player database updated: " + ", ".join(f"{role}={count}" for role, count in counts.items())
    )
