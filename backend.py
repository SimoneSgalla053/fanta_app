from config import (
    MAX_CREDIT_AMOUNT,
    MAX_CREDIT_PER_ROLE,
    MY_TEAM,
    NUMBER_OF_PLAYERS_PER_ROLE,
    STANDARD_ROLE_MULTIPLIERS,
    TOTAL_CREDITS_AMOUNT,
)
import sqlite3

teams_db = sqlite3.connect("db/teams_dataset/teams.db")
players_db = sqlite3.connect("db/player_dataset/players.db")

# Roles in auction order: budget left over from earlier roles rolls into later ones
ROLES = list(NUMBER_OF_PLAYERS_PER_ROLE)
FULL_ROSTER_SIZE = sum(NUMBER_OF_PLAYERS_PER_ROLE.values())


def _validate_role(role: str) -> None:
    if role not in NUMBER_OF_PLAYERS_PER_ROLE:
        raise ValueError(f"Unknown role: {role!r}")


def _my_count_for_role(role: str) -> int:
    return teams_db.execute(f"SELECT COUNT(*) FROM {MY_TEAM} WHERE role = ?", (role,)).fetchone()[0]


def _my_spent_for_role(role: str) -> int:
    return (
        teams_db.execute(
            f"SELECT SUM(paid_value) FROM {MY_TEAM} WHERE role = ?", (role,)
        ).fetchone()[0]
        or 0
    )


def calculate_remaining_credits_for_players() -> float:
    """
    Calculate the remaining credits for players based on the total credits and player numbers.

    Returns:
        float: The remaining credits for players.
    """
    remaining_credits = TOTAL_CREDITS_AMOUNT
    teams = get_all_teams()
    for table in teams:
        if teams_db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] >= FULL_ROSTER_SIZE:
            remaining_credits -= MAX_CREDIT_AMOUNT
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
    teams = get_all_teams()
    remaining_players = FULL_ROSTER_SIZE * len(teams)
    for table in teams:
        remaining_players -= teams_db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    return remaining_players


def calculate_mean_for_remaining_players() -> float:
    """
    Calculate the mean credit value for the remaining players.

    Returns:
        float: The mean rating for the remaining players.
    """
    remaining_players = calculate_remaining_players()
    if remaining_players <= 0:
        return 0.0
    return calculate_remaining_credits_for_players() / remaining_players


def calculate_maximum_price_for_player(name: str, role: str) -> tuple[int, int]:
    """
    Calculate the market valuation and my maximum price for a player.

    Returns:
        int: The player's market valuation, rounded.
        int: The maximum price I should pay, rounded.
    """
    _validate_role(role)
    row = players_db.execute(f"SELECT rating FROM {role} WHERE name = ?", (name,)).fetchone()
    if row is None:
        return 0, 0
    rating = row[0]

    player_value = (
        rating * (calculate_mean_for_remaining_players() / 60) * STANDARD_ROLE_MULTIPLIERS[role]
    )

    # Leftover budget from earlier roles rolls over once their slots are all filled
    extra_credits = 0
    prior_roles = ROLES[: ROLES.index(role)]
    if prior_roles and all(
        _my_count_for_role(r) >= NUMBER_OF_PLAYERS_PER_ROLE[r] for r in prior_roles
    ):
        extra_credits = sum(MAX_CREDIT_PER_ROLE[r] - _my_spent_for_role(r) for r in prior_roles)

    my_remaining_credits_for_role = (
        MAX_CREDIT_PER_ROLE[role] + extra_credits - _my_spent_for_role(role)
    )
    my_remaining_players_for_role = NUMBER_OF_PLAYERS_PER_ROLE[role] - _my_count_for_role(role)

    if my_remaining_players_for_role > 0:
        # The mean cancels out of the original formula, so it is omitted here
        my_max_price = rating * my_remaining_credits_for_role / my_remaining_players_for_role / 60
    else:
        my_max_price = 0

    return round(player_value), round(my_max_price)


def insert_player_for_team(team: str, name: str, role: str, paid_value: float) -> None:
    """
    Insert a player into the team database.

    Args:
        name (str): The name of the player.
        role (str): The role of the player.
        paid_value (float): The paid value for the player.
    """
    teams = get_all_teams()
    if team != "unassigned" and team not in teams:
        raise ValueError(f"Unknown team: {team!r}")

    for table in teams:
        teams_db.execute(f"DELETE FROM {table} WHERE name = ?", (name,))
    if team != "unassigned":
        teams_db.execute(
            f"INSERT INTO {team} (name, role, paid_value) VALUES (?, ?, ?)",
            (name, role, paid_value),
        )
    teams_db.commit()


def get_players_for_team(team: str) -> list[dict]:
    """
    Get the players for a team from the database.

    Args:
        team (str): The name of the team.

    Returns:
        list[tuple[str, str, float]]: A list of players with their name, role, and paid value.
    """
    if team not in get_all_teams():
        return []
    rows = teams_db.execute(f"SELECT name, role, paid_value FROM {team}").fetchall()
    return [
        {"name": name, "role": role, "paid_value": paid_value} for name, role, paid_value in rows
    ]


def get_all_players_for_role(role: str) -> list[dict]:
    """
    Get all players for a specific role from the database, including assigned ones.

    Args:
        role (str): The role to check.
    Returns:
        list[dict[str, str, int]]: A list of players for the specified role.
    """
    _validate_role(role)
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


def get_team_and_price_for_player(name: str, role: str) -> tuple[str, int]:
    """
    Get the team for a specific player from the database.

    Args:
        name (str): The name of the player.
        role (str): The role of the player.
    Returns:
        str: The name of the team the player belongs to, or "unassigned" if not found.
    """
    for table in get_all_teams():
        if (
            teams_db.execute(
                f"SELECT COUNT(*) FROM {table} WHERE name = ? AND role = ?", (name, role)
            ).fetchone()[0]
            > 0
        ):
            return table, (
                teams_db.execute(
                    f"SELECT paid_value FROM {table} WHERE name = ? AND role = ?", (name, role)
                ).fetchone()[0]
                or 0
            )
    return "unassigned", 0
