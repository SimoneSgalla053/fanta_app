from nicegui import ui

from calculate_value import (
    calculate_maximum_price_for_player,
    get_all_teams,
    get_players_for_team,
    get_remaining_players_for_role,
    insert_player_for_team,
)


def root():
    ui.sub_pages(
        {
            "/goalkeepers": goalkeepers_players_page,
            "/defenders": defenders_players_page,
            "/midfielders": midfielders_players_page,
            "/attackers": attackers_players_page,
            "/team/{team_name}": teams_page,
        }
    ).classes("w-full")


def goalkeepers_players_page():
    players = get_remaining_players_for_role("goalkeepers")
    team_options = ["unassigned"] + get_all_teams()

    # Updated to 5 columns to match the 5 header items
    with ui.grid(columns=7).classes("w-full items-center p-4 gap-2"):
        # Header
        ui.label("Name").classes("font-bold")
        ui.label("Role").classes("font-bold")
        ui.label("Rating").classes("font-bold")
        ui.label("Player Value").classes("font-bold")
        ui.label("My Max Price").classes("font-bold")
        ui.label("Paid Value").classes("font-bold")
        ui.label("Assign Team").classes("font-bold")

        # Rows
        for player in players:
            player_value, my_max_price = calculate_maximum_price_for_player(player.get("name"), "goalkeepers")
            ui.label(player.get("name"))
            ui.label(player.get("role", "Goalkeeper"))
            ui.label(str(player.get("rating", 0)))
            ui.label(str(player_value))
            ui.label(str(my_max_price))

            # 1. Create a numeric input for paid_value
            paid_input = ui.number(
                value=player.get("paid_value", 0), precision=0, min=0  # Enforces integer step
            ).classes("w-24")

            # 2. Pass paid_input.value dynamically to your callback
            select = ui.select(
                options=team_options,
                value="unassigned",
                on_change=lambda e, p=player, inp=paid_input: insert_player_for_team(
                    e.value,
                    p.get("name"),
                    p.get("role", "Goalkeeper"),
                    int(inp.value or 1),  # Read current value from input
                ),
            ).classes("w-40")

            paid_input.on_value_change(lambda e, p=player, inp=paid_input, sel=select: insert_player_for_team(
                    sel.value,
                    p.get("name"),
                    p.get("role", "Goalkeeper"),
                    int(inp.value or 1),  # Read current value from input
                ),)  # Update select when input changes

    ui.link("Back to home", "/")


def defenders_players_page():
    players = get_remaining_players_for_role("defenders")
    team_options = ["unassigned"] + get_all_teams()

    # Updated to 5 columns to match the 5 header items
    with ui.grid(columns=7).classes("w-full items-center p-4 gap-2"):
        # Header
        ui.label("Name").classes("font-bold")
        ui.label("Role").classes("font-bold")
        ui.label("Rating").classes("font-bold")
        ui.label("Player Value").classes("font-bold")
        ui.label("My Max Price").classes("font-bold")
        ui.label("Paid Value").classes("font-bold")
        ui.label("Assign Team").classes("font-bold")

        # Rows
        for player in players:
            player_value, my_max_price = calculate_maximum_price_for_player(player.get("name"), "defenders")
            ui.label(player.get("name"))
            ui.label(player.get("role", "defender"))
            ui.label(str(player.get("rating", 0)))
            ui.label(str(player_value))
            ui.label(str(my_max_price))

            # 1. Create a numeric input for paid_value
            paid_input = ui.number(
                value=player.get("paid_value", 0), precision=0, min=0  # Enforces integer step
            ).classes("w-24")

            # 2. Pass paid_input.value dynamically to your callback
            select = ui.select(
                options=team_options,
                value="unassigned",
                on_change=lambda e, p=player, inp=paid_input: insert_player_for_team(
                    e.value,
                    p.get("name"),
                    p.get("role", "Defender"),
                    int(inp.value or 1),  # Read current value from input
                ),
            ).classes("w-40")

            paid_input.on_value_change(lambda e, p=player, inp=paid_input, sel=select: insert_player_for_team(
                    sel.value,
                    p.get("name"),
                    p.get("role", "Defender"),
                    int(inp.value or 1),  # Read current value from input
                ),)  # Update select when input changes

    ui.link("Back to home", "/")


def midfielders_players_page():
    players = get_remaining_players_for_role("midfielders")
    team_options = ["unassigned"] + get_all_teams()

    # Updated to 5 columns to match the 5 header items
    with ui.grid(columns=7).classes("w-full items-center p-4 gap-2"):
        # Header
        ui.label("Name").classes("font-bold")
        ui.label("Role").classes("font-bold")
        ui.label("Rating").classes("font-bold")
        ui.label("Player Value").classes("font-bold")
        ui.label("My Max Price").classes("font-bold")
        ui.label("Paid Value").classes("font-bold")
        ui.label("Assign Team").classes("font-bold")

        # Rows
        for player in players:
            player_value, my_max_price = calculate_maximum_price_for_player(player.get("name"), "midfielders")
            ui.label(player.get("name"))
            ui.label(player.get("role", "Midfielder"))
            ui.label(str(player.get("rating", 0)))
            ui.label(str(player_value))
            ui.label(str(my_max_price))

            # 1. Create a numeric input for paid_value
            paid_input = ui.number(
                value=player.get("paid_value", 0), precision=0, min=0  # Enforces integer step
            ).classes("w-24")

            # 2. Pass paid_input.value dynamically to your callback
            select = ui.select(
                options=team_options,
                value="unassigned",
                on_change=lambda e, p=player, inp=paid_input: insert_player_for_team(
                    e.value,
                    p.get("name"),
                    p.get("role", "Midfielder"),
                    int(inp.value or 1),  # Read current value from input
                ),
            ).classes("w-40")

            paid_input.on_value_change(lambda e, p=player, inp=paid_input, sel=select: insert_player_for_team(
                    sel.value,
                    p.get("name"),
                    p.get("role", "Midfielder"),
                    int(inp.value or 1),  # Read current value from input
                ),)  # Update select when input changes

    ui.link("Back to home", "/")


def attackers_players_page():
    players = get_remaining_players_for_role("attackers")
    team_options = ["unassigned"] + get_all_teams()

    # Updated to 5 columns to match the 5 header items
    with ui.grid(columns=7).classes("w-full items-center p-4 gap-2"):
        # Header
        ui.label("Name").classes("font-bold")
        ui.label("Role").classes("font-bold")
        ui.label("Rating").classes("font-bold")
        ui.label("Player Value").classes("font-bold")
        ui.label("My Max Price").classes("font-bold")
        ui.label("Paid Value").classes("font-bold")
        ui.label("Assign Team").classes("font-bold")

        # Rows
        for player in players:
            player_value, my_max_price = calculate_maximum_price_for_player(player.get("name"), "attackers")
            ui.label(player.get("name"))
            ui.label(player.get("role", "Attacker"))
            ui.label(str(player.get("rating", 0)))
            ui.label(str(player_value))
            ui.label(str(my_max_price))

            # 1. Create a numeric input for paid_value
            paid_input = ui.number(
                value=player.get("paid_value", 0), precision=0, min=0  # Enforces integer step
            ).classes("w-24")

            # 2. Pass paid_input.value dynamically to your callback
            select = ui.select(
                options=team_options,
                value="unassigned",
                on_change=lambda e, p=player, inp=paid_input: insert_player_for_team(
                    e.value,
                    p.get("name"),
                    p.get("role", "Attacker"),
                    int(inp.value or 1),  # Read current value from input
                ),
            ).classes("w-40")

            paid_input.on_value_change(lambda e, p=player, inp=paid_input, sel=select: insert_player_for_team(
                    sel.value,
                    p.get("name"),
                    p.get("role", "Attacker"),
                    int(inp.value or 1),  # Read current value from input
                ),)  # Update select when input changes

    ui.link("Back to home", "/")


def teams_page(team_name: str):
    ui.label(get_players_for_team(team_name))
    ui.link("Back to home", "/")


ui.run(root)
