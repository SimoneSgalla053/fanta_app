import csv
import sqlite3


def populate_db(csv_file_path, db_path="db/player_dataset/players.db", table_name="defenders"):
    # Connect to SQLite database (creates file if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"""
            DROP TABLE IF EXISTS {table_name}
        """)

    # Create table dynamically
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            name TEXT PRIMARY KEY NOT NULL,
            team TEXT NOT NULL,
            rating INTEGER NOT NULL
        )
    """)

    players_to_insert = []

    # Open and parse the CSV file
    with open(csv_file_path, mode="r", encoding="latin-1") as file:
        # Skip header lines if necessary, then read using CSV reader with semicolon delimiter
        reader = csv.reader(file, delimiter=";")

        header = None
        for row in reader:
            # Skip empty lines or title lines
            if not row or len(row) < 7:
                continue

            # Identify header row to dynamically locate column indices
            if "Nome" in row and "Squadra" in row and "Qt.A" in row:
                header = row
                name_idx = header.index("Nome")
                team_idx = header.index("Squadra")
                rating_idx = header.index("Qt.A")
                continue

            # Extract target values when header is set
            if header:
                try:
                    name = row[name_idx].strip()
                    team = row[team_idx].strip()
                    rating = int(row[rating_idx].strip())

                    players_to_insert.append((name, team, rating))
                except (ValueError, IndexError):
                    # Skip malformed data rows
                    continue

    # Bulk insert into SQLite table
    cursor.executemany(
        f"""
        INSERT INTO {table_name} (name, team, rating) 
        VALUES (?, ?, ?)
    """,
        players_to_insert,
    )

    conn.commit()
    conn.close()
    print(f"Successfully inserted {len(players_to_insert)} players into '{table_name}' table.")


# Usage Example:
populate_db('list/goalkeepers.csv', table_name='goalkeepers')
populate_db('list/defenders.csv', table_name='defenders')
populate_db('list/midfielders.csv', table_name='midfielders')
populate_db('list/attackers.csv', table_name='attackers')
