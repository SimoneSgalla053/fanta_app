from config import (
    STANDARD_ROLE_MULTIPLIERS,
    TOTAL_CREDITS_AMOUNT,
    NUMBER_OF_PLAYERS_PER_ROLE,
    MAX_CREDIT_PER_ROLE,
)
from dbm import sqlite3

teams_db = sqlite3.connect("teams.db")
players_db = sqlite3.connect("players.db")


def calculate_remaining_credits_for_players() -> float:
    """
    Calculate the remaining credits for players based on the total credits and player numbers.

    Returns:
        float: The remaining credits for players.
    """
    remaining_credits = TOTAL_CREDITS_AMOUNT
    for table in teams_db.execute("SELECT name FROM sqlite_master WHERE type='table';"):
        if teams_db.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0] > 25:
            remaining_credits -= 500
        else:
            remaining_credits -= (
                teams_db.execute(f"SELECT SUM(paid_value) FROM {table[0]}").fetchone()[0] or 0
            )
    return remaining_credits


def calculate_remaining_players() -> int:
    """
    Calculate the remaining players based on the total credits and player numbers.

    Returns:
        int: The remaining players.
    """
    remaining_players = sum(NUMBER_OF_PLAYERS_PER_ROLE.values()) * 10
    for table in teams_db.execute("SELECT name FROM sqlite_master WHERE type='table';"):
        remaining_players -= teams_db.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
    return remaining_players


def calculate_mean_for_remaining_players() -> float:
    """
    Calculate the mean rating for the remaining players based on the total credits and player numbers.

    Returns:
        float: The mean rating for the remaining players.
    """
    mean_for_player = calculate_remaining_credits_for_players() / calculate_remaining_players()
    return mean_for_player


def calculate_maximum_price_for_player(name: str, role: str) -> float, float:
    """
    Calculate the maximum price for a player based on the mean rating for the remaining players.

    Returns:
        float: The maximum price for a player.
        float: The player's rating.
    """
    role_multiplier = STANDARD_ROLE_MULTIPLIERS.get(role)
    player_rating = players_db.execute(
        "SELECT rating, role FROM players WHERE name = ?", (name,)
    ).fetchone()
    player_value = player_rating[0] * (calculate_mean_for_remaining_players()/6) * role_multiplier

    my_remaining_credits_for_role = MAX_CREDIT_PER_ROLE[role] - teams_db.execute(
        "SELECT SUM(paid_value) FROM teams.team_simone WHERE role = ?", (role,)
    ).fetchone()[0] or 0

    my_remaining_players_for_role = NUMBER_OF_PLAYERS_PER_ROLE[role] - teams_db.execute(
        "SELECT COUNT(*) FROM teams.team_simone WHERE role = ?", (role,)
    ).fetchone()[0]

    my_max_price = player_rating[0] * (calculate_mean_for_remaining_players()/6) * (my_remaining_credits_for_role/my_remaining_players_for_role)

    return player_value, my_max_price
