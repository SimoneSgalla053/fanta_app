from config import (
    STANDARD_ROLE_MULTIPLIERS,
    TOTAL_CREDITS_AMOUNT,
    NUMBER_OF_PLAYERS_PER_ROLE,
    MAX_CREDIT_PER_ROLE,
)
import sqlite3

teams_db = sqlite3.connect("db/teams_dataset/teams.db")
players_db = sqlite3.connect("db/player_dataset/players.db")


def calculate_remaining_credits_for_players() -> float:
    """
    Calculate the remaining credits for players based on the total credits and player numbers.

    Returns:
        float: The remaining credits for players.
    """
    remaining_credits = TOTAL_CREDITS_AMOUNT
    teams = get_all_teams()
    for table in teams:
        if teams_db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] > 25:
            remaining_credits -= 500
        else:
            remaining_credits -= (
                teams_db.execute(f"SELECT SUM(paid_value) FROM {table}").fetchone()[0] or 0
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


def calculate_maximum_price_for_player(name: str, role: str) -> tuple[float, float]:
    """
    Calculate the maximum price for a player based on the mean rating for the remaining players.

    Returns:
        float: The maximum price for a player.
        float: The player's rating.
    """
    role_multiplier = STANDARD_ROLE_MULTIPLIERS.get(role)
    player_rating = players_db.execute(
        f"SELECT rating FROM {role} WHERE name = ?", (name,)
    ).fetchone()
    player_value = (
        player_rating[0] * (calculate_mean_for_remaining_players() / 60) * role_multiplier
    )

    my_remaining_credits_for_role = MAX_CREDIT_PER_ROLE[role] - (
        teams_db.execute(
            "SELECT SUM(paid_value) FROM team_simo WHERE role = ?", (role,)
        ).fetchone()[0]
        or 0
    )

    my_remaining_players_for_role = (
        NUMBER_OF_PLAYERS_PER_ROLE[role]
        - teams_db.execute("SELECT COUNT(*) FROM team_simo WHERE role = ?", (role,)).fetchone()[0]
    )

    my_max_price = (
        player_rating[0]
        * (calculate_mean_for_remaining_players() / 60)
        * (
            my_remaining_credits_for_role
            / my_remaining_players_for_role
            / calculate_mean_for_remaining_players()
        )
    )

    return round(player_value), round(my_max_price)


def insert_player_for_team(team: str, name: str, role: str, paid_value: float) -> None:
    """
    Insert a player into the team database.

    Args:
        name (str): The name of the player.
        role (str): The role of the player.
        paid_value (float): The paid value for the player.
    """
    teams_db.execute(
        f"INSERT INTO teams.{team} (name, role, paid_value) VALUES (?, ?, ?)",
        (name, role, paid_value),
    )
    players_db.execute(f"DELETE FROM {role} WHERE name = ?", (name,))
    teams_db.commit()


def get_players_for_team(team: str) -> list[dict]:
    """
    Get the players for a team from the database.

    Args:
        team (str): The name of the team.

    Returns:
        list[tuple[str, str, float]]: A list of players with their name, role, and paid value.
    """
    team = teams_db.execute(f"SELECT name, role, paid_value FROM {team}").fetchall()
    team_dict = [
        {"name": name, "role": role, "paid_value": paid_value} for name, role, paid_value in team
    ]
    return team_dict


def get_remaining_players_for_role(role: str) -> list[dict]:
    """
    Get the remaining players for a specific role from the database.

    Args:
        role (str): The role to check.
    Returns:
        list[dict[str, str, int]]: A list of remaining players for the specified role.
    """
    players = players_db.execute(f"SELECT name, team, rating FROM {role}").fetchall()
    players_dict = [
        {"name": name, "team": team, "rating": rating} for name, team, rating in players
    ]
    return players_dict


def get_all_teams() -> list[str]:
    """
    Get all the teams from the database.

    Returns:
        list[str]: A list of team names.
    """
    teams = teams_db.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    return [team[0] for team in teams if team[0] != "sqlite_sequence"]
