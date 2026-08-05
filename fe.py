from nicegui import ui

from backend import (
    calculate_maximum_price_for_player,
    get_all_players_for_role,
    get_all_teams,
    get_players_for_team,
    get_team_and_price_for_player,
    insert_player_for_team,
)


def layout_wrapper(content_fn, *args, **kwargs):
    """Wraps pages in a consistent, modern navigation layout."""
    with ui.column().classes("w-full min-h-screen bg-slate-50 text-slate-800"):
        # Header Navbar
        with ui.row().classes(
            "w-full bg-slate-900 text-white px-8 py-4 items-center justify-between shadow-md"
        ):
            # FIXED: Attached .on('click', ...) instead of passing on_click to ui.row()
            with ui.row().classes("items-center gap-2 cursor-pointer").on(
                "click", lambda: ui.navigate.to("/")
            ):
                ui.icon("sports_soccer", size="md").classes("text-emerald-400")
                ui.label("FantaApp Pro").classes("text-xl font-bold tracking-wide")

            with ui.row().classes("gap-6 font-medium text-slate-300"):
                ui.link("Dashboard", "/").classes("hover:text-emerald-400 transition")
                ui.link("Teams", "/teams").classes("hover:text-emerald-400 transition")
                ui.link("Goalkeepers", "/goalkeepers").classes("hover:text-emerald-400 transition")
                ui.link("Defenders", "/defenders").classes("hover:text-emerald-400 transition")
                ui.link("Midfielders", "/midfielders").classes("hover:text-emerald-400 transition")
                ui.link("Attackers", "/attackers").classes("hover:text-emerald-400 transition")

        # Main Page Container
        with ui.column().classes("w-full max-w-7xl mx-auto p-6 md:p-8 flex-1"):
            content_fn(*args, **kwargs)


def index_page():
    ui.label("Fantacalcio Auction Hub").classes("text-3xl font-extrabold text-slate-900 mb-2")
    ui.label("Manage player budgets, max prices, and team assignments in real time.").classes(
        "text-slate-500 mb-8"
    )

    with ui.grid(columns="1 sm:2 md:3 lg:5").classes("w-full gap-4"):
        roles = [
            ("Goalkeepers", "shield", "/goalkeepers", "bg-amber-500"),
            ("Defenders", "security", "/defenders", "bg-blue-500"),
            ("Midfielders", "tune", "/midfielders", "bg-emerald-500"),
            ("Attackers", "bolt", "/attackers", "bg-rose-500"),
            ("Teams Overview", "groups", "/teams", "bg-purple-500"),
        ]

        for name, icon, route, color_cls in roles:
            with (
                ui.card()
                .classes(
                    "p-6 flex flex-col items-center justify-center text-center cursor-pointer "
                    "hover:-translate-y-1 hover:shadow-xl transition-all duration-200 border border-slate-100"
                )
                .on("click", lambda r=route: ui.navigate.to(r))
            ):
                with ui.avatar(color=None).classes(f"{color_cls} text-white mb-3 shadow-md"):
                    ui.icon(icon)
                ui.label(name).classes("font-bold text-slate-800 text-lg")


def select_team_page():
    ui.label("Teams Directory").classes("text-3xl font-extrabold text-slate-900 mb-2")
    ui.label("Select a team to inspect roster allocations and total spend.").classes(
        "text-slate-500 mb-6"
    )

    teams = get_all_teams()

    with ui.grid(columns="1 sm:2 md:3 lg:4").classes("w-full gap-4"):
        for team in teams:
            t_name = team.replace("team_", "").capitalize()
            with (
                ui.card()
                .classes(
                    "p-5 flex flex-row items-center justify-between cursor-pointer "
                    "hover:border-emerald-500 border border-slate-200 transition-all shadow-sm"
                )
                .on("click", lambda t=team: ui.navigate.to(f"/team/{t}"))
            ):
                with ui.row().classes("items-center gap-3"):
                    ui.avatar(t_name[0], color="slate-800", text_color="white").classes("font-bold")
                    ui.label(t_name).classes("font-bold text-slate-800 text-lg")
                ui.icon("chevron_right", color="gray-400")


def render_role_page(role: str):
    ui.label(f"{role.capitalize()} Market").classes("text-3xl font-extrabold text-slate-900 mb-2")
    ui.label("Review calculated max values and assign won players to target teams.").classes(
        "text-slate-500 mb-6"
    )

    players = get_all_players_for_role(role)
    team_options = ["unassigned"] + get_all_teams()
    max_price_labels = {}

    def refresh_all_max_prices():
        for player_name, label in max_price_labels.items():
            _, new_max_price = calculate_maximum_price_for_player(player_name, role)
            label.set_text(f"{new_max_price} cr")

    def handle_assignment(team_val: str, player_name: str, player_role: str, paid_val: int):
        insert_player_for_team(team_val, player_name, player_role, paid_val)
        refresh_all_max_prices()

    with ui.card().classes("w-full p-0 overflow-hidden border border-slate-200 shadow-sm"):
        with ui.grid(columns=7).classes(
            "w-full bg-slate-100 p-4 gap-2 font-bold text-slate-600 text-xs uppercase tracking-wider border-b border-slate-200"
        ):
            ui.label("Name")
            ui.label("Role")
            ui.label("Rating")
            ui.label("Valuation")
            ui.label("My Max Price")
            ui.label("Paid Price")
            ui.label("Assign Team")

        with ui.column().classes("w-full divide-y divide-slate-100"):
            for player in players:
                p_name = player.get("name")
                p_role = player.get("role", role)
                p_rating = str(player.get("rating", 0))

                player_value, my_max_price = calculate_maximum_price_for_player(p_name, role)
                current_team, current_price = get_team_and_price_for_player(p_name, role)

                with ui.grid(columns=7).classes(
                    "w-full p-4 gap-2 items-center hover:bg-slate-50 transition"
                ):
                    ui.label(p_name).classes("font-semibold text-slate-800")
                    ui.badge(
                        p_role.upper(),
                        color="slate-200",
                        text_color="slate-700",
                    ).classes("w-fit font-bold")
                    ui.label(p_rating).classes("text-slate-600 font-medium")
                    ui.label(f"{player_value} cr").classes("text-slate-500")

                    max_price_label = ui.label(f"{my_max_price} cr").classes(
                        "font-extrabold text-emerald-600"
                    )
                    max_price_labels[p_name] = max_price_label

                    paid_input = (
                        ui.number(value=current_price or 0, precision=0, min=0)
                        .props("dense outlined debounce=500")
                        .classes("w-24 bg-white")
                    )

                    select = (
                        ui.select(
                            options=team_options,
                            value=current_team or "unassigned",
                        )
                        .props("dense outlined")
                        .classes("w-40 bg-white")
                    )

                    select.on_value_change(
                        lambda e, p=p_name, r=p_role, inp=paid_input: handle_assignment(
                            e.value, p, r, int(inp.value or 0)
                        )
                    )
                    paid_input.on_value_change(
                        lambda e, p=p_name, r=p_role, sel=select: handle_assignment(
                            sel.value, p, r, int(e.value or 0)
                        )
                    )


def teams_page(team_name: str):
    clean_name = team_name.replace("team_", "").capitalize()

    with ui.row().classes("items-center justify-between w-full mb-6"):
        with ui.row().classes("items-center gap-4"):
            ui.avatar(clean_name[0], color="slate-900", text_color="white", size="lg").classes(
                "font-bold"
            )
            with ui.column().classes("gap-0"):
                ui.label(f"Team {clean_name}").classes("text-3xl font-extrabold text-slate-900")
                ui.label("Roster breakdown and expenditure").classes("text-slate-500 text-sm")

    players = get_players_for_team(team_name)

    if not players:
        with ui.card().classes(
            "w-full p-12 text-center border border-dashed border-slate-300 shadow-none"
        ):
            ui.icon("group_off", size="xl").classes("text-slate-300 mb-2")
            ui.label("No players assigned to this team yet.").classes("text-slate-500 text-base")
            ui.button(
                "Browse Market",
                on_click=lambda: ui.navigate.to("/goalkeepers"),
            ).props("flat color=primary")
    else:
        roles_order = ["goalkeepers", "defenders", "midfielders", "attackers"]
        grouped_players = {role: [] for role in roles_order}

        for player in players:
            role_key = player.get("role", "").lower()
            if role_key in grouped_players:
                grouped_players[role_key].append(player)
            else:
                grouped_players.setdefault("other", []).append(player)

        total_spent = sum(p.get("paid_value", 0) for p in players)

        with ui.row().classes("w-full gap-4 mb-6"):
            with ui.card().classes("p-4 flex-1 border border-slate-200 shadow-sm"):
                ui.label("Total Squad Size").classes("text-xs text-slate-500 font-bold uppercase")
                ui.label(f"{len(players)} Players").classes("text-2xl font-black text-slate-800")
            with ui.card().classes("p-4 flex-1 border border-slate-200 shadow-sm"):
                ui.label("Total Budget Spent").classes("text-xs text-slate-500 font-bold uppercase")
                ui.label(f"{total_spent} Credits").classes("text-2xl font-black text-emerald-600")

        columns = [
            {
                "name": "name",
                "label": "Name",
                "field": "name",
                "align": "left",
                "sortable": True,
            },
            {"name": "role", "label": "Role", "field": "role", "align": "center"},
            {
                "name": "paid_value",
                "label": "Paid Value (cr)",
                "field": "paid_value",
                "align": "right",
                "sortable": True,
            },
        ]

        for role in roles_order:
            role_players = grouped_players[role]
            if role_players:
                role_spent = sum(p.get("paid_value", 0) for p in role_players)
                with ui.column().classes("w-full mb-6 gap-2"):
                    with ui.row().classes("justify-between items-center w-full px-1"):
                        ui.label(f"{role.capitalize()} ({len(role_players)})").classes(
                            "text-lg font-bold text-slate-800"
                        )
                        ui.badge(
                            f"Subtotal: {role_spent} cr",
                            color="slate-800",
                            text_color="white",
                        )

                    ui.table(columns=columns, rows=role_players, row_key="name").props(
                        "flat bordered dense"
                    ).classes("w-full bg-white border border-slate-200 rounded-lg shadow-sm")


# Routing Callbacks
def index():
    layout_wrapper(index_page)


def select_team():
    layout_wrapper(select_team_page)


def gk_page():
    layout_wrapper(render_role_page, "goalkeepers")


def def_page():
    layout_wrapper(render_role_page, "defenders")


def mid_page():
    layout_wrapper(render_role_page, "midfielders")


def att_page():
    layout_wrapper(render_role_page, "attackers")


def team_detail(team_name: str):
    layout_wrapper(teams_page, team_name)


def root():
    ui.sub_pages(
        {
            "/": index,
            "/teams": select_team,
            "/goalkeepers": gk_page,
            "/defenders": def_page,
            "/midfielders": mid_page,
            "/attackers": att_page,
            "/team/{team_name}": team_detail,
        }
    ).classes("w-full")


ui.run(root)
