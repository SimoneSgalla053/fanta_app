from nicegui import ui

from calculate_value import (
    calculate_maximum_price_for_player,
    get_all_teams,
    get_players_for_team,
    get_remaining_players_for_role,
    get_team_and_price_for_player,
    insert_player_for_team,
)


def root():
    ui.sub_pages(
        {
            "/": index_page,
            "/teams": select_team_page,
            "/goalkeepers": goalkeepers_players_page,
            "/defenders": defenders_players_page,
            "/midfielders": midfielders_players_page,
            "/attackers": attackers_players_page,
            "/team/{team_name}": teams_page,
        }
    ).classes("w-full")


def index_page():
    ui.label("Fanta App Dashboard").classes("text-2xl font-bold mb-4")

    # 5 main navigation buttons
    with ui.column().classes("gap-3 max-w-xs"):
        ui.button("Goalkeepers", on_click=lambda: ui.navigate.to("/goalkeepers")).classes("w-full")
        ui.button("Defenders", on_click=lambda: ui.navigate.to("/defenders")).classes("w-full")
        ui.button("Midfielders", on_click=lambda: ui.navigate.to("/midfielders")).classes("w-full")
        ui.button("Attackers", on_click=lambda: ui.navigate.to("/attackers")).classes("w-full")
        ui.button("Teams", on_click=lambda: ui.navigate.to("/teams")).classes("w-full")


def select_team_page():
    ui.label("Select a Team").classes("text-2xl font-bold mb-4")
    teams = get_all_teams()

    with ui.column().classes("gap-2 max-w-xs"):
        for team in teams:
            ui.button(
                team.replace("team_", "").capitalize(),
                on_click=lambda t=team: ui.navigate.to(f"/team/{t}"),
            ).classes("w-full")

    ui.link("Back to home", "/").classes("mt-4 block")


def goalkeepers_players_page():
    players = get_remaining_players_for_role("goalkeepers")
    team_options = ["unassigned"] + get_all_teams()

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
            player_value, my_max_price = calculate_maximum_price_for_player(
                player.get("name"), "goalkeepers"
            )
            ui.label(player.get("name"))
            ui.label(player.get("role", "goalkeepers"))
            ui.label(str(player.get("rating", 0)))
            ui.label(str(player_value))
            ui.label(str(my_max_price))

            paid_input = ui.number(value=player.get("paid_value", 0), precision=0, min=0).classes(
                "w-24"
            )

            select = ui.select(
                options=team_options,
                value="unassigned",
                on_change=lambda e, p=player, inp=paid_input: insert_player_for_team(
                    e.value,
                    p.get("name"),
                    p.get("role", "goalkeepers"),
                    int(inp.value or 1),
                ),
            ).classes("w-40")

            paid_input.on_value_change(
                lambda e, p=player, inp=paid_input, sel=select: insert_player_for_team(
                    sel.value,
                    p.get("name"),
                    p.get("role", "goalkeepers"),
                    int(inp.value or 1),
                )
            )

    ui.link("Back to home", "/")


def defenders_players_page():
    players = get_remaining_players_for_role("defenders")
    team_options = ["unassigned"] + get_all_teams()

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
            player_value, my_max_price = calculate_maximum_price_for_player(
                player.get("name"), "defenders"
            )
            ui.label(player.get("name"))
            ui.label(player.get("role", "defenders"))
            ui.label(str(player.get("rating", 0)))
            ui.label(str(player_value))
            ui.label(str(my_max_price))

            team, price = get_team_and_price_for_player(player.get("name"), "defenders")

            paid_input = ui.number(value=price, precision=0, min=0).classes(
                "w-24"
            )

            select = ui.select(
                options=team_options,
                value=team,
                on_change=lambda e, p=player, inp=paid_input: insert_player_for_team(
                    e.value,
                    p.get("name"),
                    p.get("role", "defenders"),
                    int(inp.value or 1),
                ),
            ).classes("w-40")

            paid_input.on_value_change(
                lambda e, p=player, inp=paid_input, sel=select: insert_player_for_team(
                    sel.value,
                    p.get("name"),
                    p.get("role", "defenders"),
                    int(inp.value or 1),
                )
            )

    ui.link("Back to home", "/")


def midfielders_players_page():
    players = get_remaining_players_for_role("midfielders")
    team_options = ["unassigned"] + get_all_teams()

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
            player_value, my_max_price = calculate_maximum_price_for_player(
                player.get("name"), "midfielders"
            )
            ui.label(player.get("name"))
            ui.label(player.get("role", "midfielders"))
            ui.label(str(player.get("rating", 0)))
            ui.label(str(player_value))
            ui.label(str(my_max_price))

            paid_input = ui.number(value=player.get("paid_value", 0), precision=0, min=0).classes(
                "w-24"
            )

            select = ui.select(
                options=team_options,
                value="unassigned",
                on_change=lambda e, p=player, inp=paid_input: insert_player_for_team(
                    e.value,
                    p.get("name"),
                    p.get("role", "midfielders"),
                    int(inp.value or 1),
                ),
            ).classes("w-40")

            paid_input.on_value_change(
                lambda e, p=player, inp=paid_input, sel=select: insert_player_for_team(
                    sel.value,
                    p.get("name"),
                    p.get("role", "midfielders"),
                    int(inp.value or 1),
                )
            )

    ui.link("Back to home", "/")


def attackers_players_page():
    players = get_remaining_players_for_role("attackers")
    team_options = ["unassigned"] + get_all_teams()

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
            player_value, my_max_price = calculate_maximum_price_for_player(
                player.get("name"), "attackers"
            )
            ui.label(player.get("name"))
            ui.label(player.get("role", "attackers"))
            ui.label(str(player.get("rating", 0)))
            ui.label(str(player_value))
            ui.label(str(my_max_price))

            paid_input = ui.number(value=player.get("paid_value", 0), precision=0, min=0).classes(
                "w-24"
            )

            select = ui.select(
                options=team_options,
                value="unassigned",
                on_change=lambda e, p=player, inp=paid_input: insert_player_for_team(
                    e.value,
                    p.get("name"),
                    p.get("role", "attackers"),
                    int(inp.value or 1),
                ),
            ).classes("w-40")

            paid_input.on_value_change(
                lambda e, p=player, inp=paid_input, sel=select: insert_player_for_team(
                    sel.value,
                    p.get("name"),
                    p.get("role", "attackers"),
                    int(inp.value or 1),
                )
            )

    ui.link("Back to home", "/")


def teams_page(team_name: str):
    ui.label(f"Team: {team_name.replace('team_', '').capitalize()}").classes(
        "text-2xl font-bold mb-4"
    )

    # Get all players for this team
    players = get_players_for_team(team_name)

    if not players:
        ui.label("No players assigned to this team yet.").classes("text-gray-500 italic")
    else:
        # Group players by role
        roles_order = ["goalkeepers", "defenders", "midfielders", "attackers"]
        grouped_players = {role: [] for role in roles_order}

        for player in players:
            role_key = player.get("role", "").lower()
            # Normalize role string to match key
            if role_key in grouped_players:
                grouped_players[role_key].append(player)
            else:
                grouped_players.setdefault("other", []).append(player)

        # Columns configuration for NiceGUI ui.table
        columns = [
            {"name": "name", "label": "Name", "field": "name", "align": "left", "sortable": True},
            {"name": "role", "label": "Role", "field": "role", "align": "center"},
            {
                "name": "paid_value",
                "label": "Paid Value",
                "field": "paid_value",
                "align": "right",
                "sortable": True,
            },
        ]

        # Total team spending summary
        total_spent = sum(p.get("paid_value", 0) for p in players)
        ui.label(f"Total Players: {len(players)} | Total Spent: {total_spent} credits").classes(
            "text-lg font-semibold mb-4 text-blue-600"
        )

        # Render a table for each role section
        for role in roles_order:
            role_players = grouped_players[role]
            if role_players:
                role_spent = sum(p.get("paid_value", 0) for p in role_players)

                # Section Header
                ui.label(
                    f"{role.capitalize()} ({len(role_players)}) — Spent: {role_spent}"
                ).classes("text-lg font-bold mt-4 mb-1")

                # Table for this specific role
                ui.table(columns=columns, rows=role_players, row_key="name").props(
                    "flat bordered dense"
                ).classes("w-full mb-4")

    ui.link("Back to Teams", "/teams").classes("mt-4 inline-block text-blue-500")
    ui.link("Back to Home", "/").classes("ml-4 mt-4 inline-block text-gray-500")


ui.run(root)
