import os
from pathlib import Path

from nicegui import app, ui

from backend import (
    calculate_maximum_price_for_player,
    calculate_remaining_credits_for_players,
    calculate_remaining_players,
    get_all_players_for_role,
    get_all_teams,
    get_players_for_team,
    get_team_and_price_for_player,
    insert_player_for_team,
    reset_all_teams,
)
from config import (
    MAX_CREDIT_AMOUNT,
    MAX_CREDIT_PER_ROLE,
    MY_TEAM,
    NUMBER_OF_PLAYERS_PER_ROLE,
)
from populate_players import update_players

try:
    player_counts = update_players()
    print(
        "Player data updated: "
        + ", ".join(f"{role}={count}" for role, count in player_counts.items())
    )
except Exception as error:
    print(f"Player data update failed; using the existing local database: {error}")

PLAYER_IMAGES_DIR = Path(__file__).resolve().parent / "list/images"
PLAYER_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
app.add_static_files("/player-images", PLAYER_IMAGES_DIR)

ROLE_META = {
    "goalkeepers": {
        "label": "Goalkeepers",
        "icon": "shield",
        "route": "/goalkeepers",
        "q_color": "amber",
        "text": "text-amber-500",
        "gradient": "from-amber-400 to-orange-500",
    },
    "defenders": {
        "label": "Defenders",
        "icon": "security",
        "route": "/defenders",
        "q_color": "blue",
        "text": "text-blue-500",
        "gradient": "from-blue-400 to-indigo-500",
    },
    "midfielders": {
        "label": "Midfielders",
        "icon": "tune",
        "route": "/midfielders",
        "q_color": "teal",
        "text": "text-emerald-500",
        "gradient": "from-emerald-400 to-teal-500",
    },
    "attackers": {
        "label": "Attackers",
        "icon": "bolt",
        "route": "/attackers",
        "q_color": "pink",
        "text": "text-rose-500",
        "gradient": "from-rose-400 to-pink-600",
    },
}

NAV_LINKS = [
    ("Dashboard", "/", "dashboard"),
    ("Teams", "/teams", "groups"),
    ("Goalkeepers", "/goalkeepers", "shield"),
    ("Defenders", "/defenders", "security"),
    ("Midfielders", "/midfielders", "tune"),
    ("Attackers", "/attackers", "bolt"),
]


def my_team_summary() -> tuple[dict, dict]:
    """Credits spent and players bought per role for my team."""
    spent = {role: 0 for role in ROLE_META}
    count = {role: 0 for role in ROLE_META}
    for player in get_players_for_team(MY_TEAM):
        role = (player.get("role") or "").lower()
        if role in spent:
            spent[role] += player.get("paid_value") or 0
            count[role] += 1
    return spent, count


def stat_card(title: str, value: str, icon: str, accent: str):
    with ui.card().classes(
        "p-5 border border-slate-200 shadow-sm rounded-2xl hover:shadow-lg transition-shadow"
    ):
        with ui.row().classes("items-center justify-between w-full no-wrap"):
            with ui.column().classes("gap-1"):
                ui.label(title).classes("text-xs text-slate-500 font-bold uppercase tracking-wider")
                ui.label(value).classes(f"text-2xl font-black {accent}")
            ui.icon(icon, size="md").classes(f"{accent} opacity-30")


def layout_wrapper(content_fn, *args, **kwargs):
    """Wraps pages in a consistent, modern navigation layout."""
    with ui.column().classes(
        "w-full min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 "
        "text-slate-800 gap-0"
    ):
        # Sticky glassy header
        with ui.row().classes(
            "w-full sticky top-0 z-50 bg-slate-900/95 backdrop-blur text-white "
            "px-6 py-3 items-center justify-between shadow-lg no-wrap"
        ):
            with ui.row().classes("items-center gap-2 cursor-pointer no-wrap").on(
                "click", lambda: ui.navigate.to("/")
            ):
                ui.icon("sports_soccer", size="md").classes("text-emerald-400")
                ui.label("FantaApp Pro").classes(
                    "text-xl font-black tracking-wide "
                    "bg-gradient-to-r from-emerald-400 to-teal-300 bg-clip-text text-transparent"
                )

            with ui.row().classes("gap-1 items-center no-wrap"):
                for label, route, icon in NAV_LINKS:
                    ui.button(label, icon=icon, on_click=lambda r=route: ui.navigate.to(r)).props(
                        "flat dense no-caps color=white"
                    ).classes("px-3 rounded-full hover:bg-white/10 transition")

        # Main Page Container
        with ui.column().classes("w-full max-w-7xl mx-auto p-6 md:p-8 flex-1"):
            content_fn(*args, **kwargs)


def index_page():
    with ui.column().classes("w-full items-center text-center mb-8 gap-2"):
        ui.label("Fantacalcio Auction Hub").classes(
            "text-4xl md:text-5xl font-black pb-1 "
            "bg-gradient-to-r from-slate-900 via-emerald-600 to-teal-500 "
            "bg-clip-text text-transparent"
        )
        ui.label("Manage player budgets, max prices, and team assignments in real time.").classes(
            "text-slate-500"
        )

    remaining_credits = round(calculate_remaining_credits_for_players())
    remaining_players = calculate_remaining_players()
    spent, count = my_team_summary()
    my_spent = sum(spent.values())

    with ui.grid(columns="1 sm:3").classes("w-full gap-4 mb-8"):
        stat_card("Market Credits Left", f"{remaining_credits} cr", "savings", "text-emerald-600")
        stat_card("Open Roster Slots", str(remaining_players), "event_seat", "text-blue-600")
        stat_card(
            "My Total Spend",
            f"{my_spent} / {MAX_CREDIT_AMOUNT} cr",
            "account_balance_wallet",
            "text-rose-600",
        )

    with ui.card().classes("w-full p-6 mb-8 border border-slate-200 shadow-sm rounded-2xl"):
        ui.label("My Budget by Role").classes(
            "text-sm font-bold uppercase tracking-wider text-slate-500 mb-4"
        )
        with ui.grid(columns="1 md:2").classes("w-full gap-x-10 gap-y-5"):
            for role, meta in ROLE_META.items():
                with (
                    ui.column()
                    .classes("w-full gap-1 cursor-pointer")
                    .on("click", lambda r=meta["route"]: ui.navigate.to(r))
                ):
                    with ui.row().classes("w-full justify-between items-center no-wrap"):
                        with ui.row().classes("items-center gap-2 no-wrap"):
                            ui.icon(meta["icon"]).classes(meta["text"])
                            ui.label(meta["label"]).classes("font-semibold text-slate-800")
                        ui.label(
                            f"{spent[role]} / {MAX_CREDIT_PER_ROLE[role]} cr · "
                            f"{count[role]}/{NUMBER_OF_PLAYERS_PER_ROLE[role]}"
                        ).classes("text-xs text-slate-500 font-medium")
                    ui.linear_progress(
                        value=min(spent[role] / MAX_CREDIT_PER_ROLE[role], 1.0),
                        show_value=False,
                        color=meta["q_color"],
                    ).props("rounded size=8px")

    ui.label("Explore the Market").classes("text-lg font-bold text-slate-800 mb-3")
    with ui.grid(columns="1 sm:2 lg:5").classes("w-full gap-4"):
        cards = [
            (meta["label"], meta["icon"], meta["route"], meta["gradient"])
            for meta in ROLE_META.values()
        ]
        cards.append(("Teams Overview", "groups", "/teams", "from-purple-400 to-fuchsia-600"))

        for name, icon, route, gradient in cards:
            with (
                ui.card()
                .classes(
                    "p-6 flex flex-col items-center justify-center text-center cursor-pointer "
                    "rounded-2xl hover:-translate-y-1 hover:shadow-xl transition-all duration-200 "
                    "border border-slate-100"
                )
                .on("click", lambda r=route: ui.navigate.to(r))
            ):
                with ui.element("div").classes(
                    f"w-12 h-12 rounded-full bg-gradient-to-br {gradient} text-white mb-3 "
                    "shadow-md flex items-center justify-center"
                ):
                    ui.icon(icon, size="sm")
                ui.label(name).classes("font-bold text-slate-800")


def select_team_page():
    def confirm_reset():
        if reset_confirmation.value != "RESET":
            return
        removed = reset_all_teams()
        reset_dialog.close()
        ui.notify(
            f"All teams reset. {removed} player assignments removed.",
            type="positive",
            position="top-right",
        )
        team_directory.refresh()

    def open_reset_dialog():
        reset_confirmation.value = ""
        reset_dialog.open()

    with ui.dialog() as reset_dialog, ui.card().classes("w-full max-w-md p-6 rounded-2xl").props(
        "persistent"
    ):
        with ui.row().classes("items-center gap-3 no-wrap"):
            ui.icon("warning", size="md").classes("text-red-500")
            ui.label("Reset all teams?").classes("text-xl font-bold text-slate-900")
        ui.label(
            "Every player assignment and paid price will be permanently removed from all teams."
        ).classes("text-slate-600")
        reset_confirmation = (
            ui.input("Type RESET to confirm")
            .props("outlined autofocus autocomplete=off")
            .classes("w-full mt-2")
        )
        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Cancel", on_click=reset_dialog.close).props("flat no-caps color=slate")
            ui.button("Erase all rosters", icon="delete_forever", on_click=confirm_reset).props(
                "unelevated no-caps color=negative"
            ).bind_enabled_from(reset_confirmation, "value", lambda value: value == "RESET")

    with ui.row().classes("w-full items-center justify-between mb-6"):
        with ui.column().classes("gap-1"):
            ui.label("Teams Directory").classes("text-3xl font-extrabold text-slate-900")
            ui.label("Select a team to inspect roster allocations and total spend.").classes(
                "text-slate-500"
            )
        ui.button("Reset all teams", icon="delete_sweep", on_click=open_reset_dialog).props(
            "outline no-caps color=negative"
        ).classes("rounded-lg")

    @ui.refreshable
    def team_directory():
        total_slots = sum(NUMBER_OF_PLAYERS_PER_ROLE.values())

        with ui.grid(columns="1 sm:2 md:3 lg:4").classes("w-full gap-4"):
            for team in get_all_teams():
                t_name = team.replace("team_", "").capitalize()
                roster = get_players_for_team(team)
                spent_total = sum(p.get("paid_value", 0) for p in roster)
                with (
                    ui.card()
                    .classes(
                        "p-5 cursor-pointer rounded-2xl hover:border-emerald-500 hover:shadow-lg "
                        "border border-slate-200 transition-all shadow-sm"
                    )
                    .on("click", lambda t=team: ui.navigate.to(f"/team/{t}"))
                ):
                    with ui.row().classes("items-center justify-between w-full mb-3 no-wrap"):
                        with ui.row().classes("items-center gap-3 no-wrap"):
                            ui.avatar(t_name[0], color="slate-800", text_color="white").classes(
                                "font-bold"
                            )
                            ui.label(t_name).classes("font-bold text-slate-800 text-lg")
                        ui.icon("chevron_right", color="gray-400")
                    with ui.row().classes(
                        "w-full justify-between text-xs text-slate-500 font-medium mb-1 no-wrap"
                    ):
                        ui.label(f"{len(roster)}/{total_slots} players")
                        ui.label(f"{spent_total}/{MAX_CREDIT_AMOUNT} cr")
                    ui.linear_progress(
                        value=min(spent_total / MAX_CREDIT_AMOUNT, 1.0),
                        show_value=False,
                        color="teal",
                    ).props("rounded size=6px")

    team_directory()


def render_role_page(role: str):
    meta = ROLE_META[role]

    with ui.row().classes("items-center gap-3 mb-1 no-wrap"):
        with ui.element("div").classes(
            f"p-2.5 rounded-xl bg-gradient-to-br {meta['gradient']} text-white shadow-md "
            "flex items-center justify-center"
        ):
            ui.icon(meta["icon"], size="sm")
        ui.label(f"{meta['label']} Market").classes("text-3xl font-extrabold text-slate-900")
    ui.label("Review calculated max values and assign won players to target teams.").classes(
        "text-slate-500 mb-4"
    )

    players = get_all_players_for_role(role)
    teams = get_all_teams()
    team_options = {team: team.replace("team_", "").capitalize() for team in teams}
    state = {"search": "", "hide_assigned": False}
    assignment_state = {"player_name": ""}

    @ui.refreshable
    def budget_bar():
        spent, count = my_team_summary()
        cap = MAX_CREDIT_PER_ROLE[role]
        with ui.card().classes("w-full p-4 mb-4 border border-slate-200 shadow-sm rounded-2xl"):
            with ui.row().classes("w-full justify-between items-center mb-1 no-wrap"):
                ui.label("My budget for this role").classes(
                    "text-xs font-bold uppercase tracking-wider text-slate-500"
                )
                ui.label(
                    f"{spent[role]} / {cap} cr · "
                    f"{count[role]}/{NUMBER_OF_PLAYERS_PER_ROLE[role]} players"
                ).classes("text-sm font-bold text-slate-700")
            ui.linear_progress(
                value=min(spent[role] / cap, 1.0), show_value=False, color=meta["q_color"]
            ).props("rounded size=10px")

    def handle_assignment(team_val: str, player_name: str, paid_val: int):
        insert_player_for_team(team_val, player_name, role, paid_val)
        if team_val == "unassigned":
            ui.notify(f"{player_name} released to the market", type="info", position="top-right")
        else:
            ui.notify(
                f"{player_name} → {team_val.replace('team_', '').capitalize()} "
                f"for {paid_val} cr",
                type="positive",
                position="top-right",
            )
        budget_bar.refresh()
        market.refresh()

    def save_assignment():
        player_name = assignment_state["player_name"]
        if not assignment_team.value:
            ui.notify("Select a team before assigning the player.", type="warning")
            return
        if assignment_price.value is None or assignment_price.value < 0:
            ui.notify("Enter a valid paid price.", type="warning")
            return
        assignment_dialog.close()
        handle_assignment(
            assignment_team.value,
            player_name,
            int(assignment_price.value),
        )

    def release_player():
        player_name = assignment_state["player_name"]
        assignment_dialog.close()
        handle_assignment("unassigned", player_name, 0)

    with ui.dialog() as assignment_dialog, ui.card().classes("w-full max-w-md p-6 rounded-2xl"):
        with ui.row().classes("items-center gap-3 mb-2 no-wrap"):
            ui.icon("person_add", size="sm").classes("text-emerald-600")
            assignment_title = ui.label("Assign player").classes("text-xl font-bold text-slate-900")
        ui.label("Enter the paid price, then select the destination team.").classes(
            "text-sm text-slate-500 mb-3"
        )
        assignment_price = (
            ui.number("Paid price", value=0, precision=0, min=0)
            .props("outlined autofocus")
            .classes("w-full")
        )
        assignment_team = (
            ui.select(options=team_options, label="Team").props("outlined").classes("w-full")
        )
        with ui.row().classes("w-full justify-between items-center mt-3"):
            release_button = ui.button(
                "Release player", icon="person_remove", on_click=release_player
            ).props("flat no-caps color=negative")
            with ui.row().classes("gap-2"):
                ui.button("Cancel", on_click=assignment_dialog.close).props(
                    "flat no-caps color=slate"
                )
                ui.button("Save assignment", icon="check", on_click=save_assignment).props(
                    "unelevated no-caps color=positive"
                )

    def open_assignment_dialog(player_name: str, current_team: str, current_price: int):
        assignment_state["player_name"] = player_name
        assigned = current_team != "unassigned"
        assignment_title.set_text(
            f"{'Edit assignment for' if assigned else 'Assign'} {player_name}"
        )
        assignment_price.value = current_price if assigned else 0
        assignment_team.value = current_team if assigned else None
        release_button.set_visibility(assigned)
        assignment_dialog.open()

    @ui.refreshable
    def market():
        term = state["search"].strip().lower()
        visible = [
            p
            for p in players
            if not term
            or term in p.get("name", "").lower()
            or term in (p.get("team") or "").lower()
        ]

        with ui.card().classes(
            "w-full p-0 overflow-hidden border border-slate-200 shadow-sm rounded-2xl"
        ):
            with ui.grid(columns=6).classes(
                "w-full bg-slate-100 p-4 gap-2 font-bold text-slate-600 text-xs uppercase "
                "tracking-wider border-b border-slate-200"
            ):
                ui.label("Player")
                ui.label("Club")
                ui.label("Rating")
                ui.label("Valuation")
                ui.label("My Max Price")
                ui.label("Action")

            shown = 0
            with ui.column().classes("w-full divide-y divide-slate-100 gap-0"):
                for player in visible:
                    p_name = player.get("name")
                    p_club = player.get("team", "")
                    p_rating = player.get("rating", 0)
                    p_image = player.get("image_path")

                    current_team, current_price = get_team_and_price_for_player(p_name, role)
                    assigned = current_team != "unassigned"
                    if state["hide_assigned"] and assigned:
                        continue
                    shown += 1

                    player_value, my_max_price = calculate_maximum_price_for_player(p_name, role)

                    row_classes = "w-full p-4 gap-2 items-center transition hover:bg-slate-50"
                    if assigned:
                        row_classes += " bg-slate-50/50 opacity-70"

                    with ui.grid(columns=6).classes(row_classes):
                        with ui.row().classes("items-center gap-3 no-wrap"):
                            if p_image:
                                ui.image(f"/player-images/{p_image}").props("fit=cover").classes(
                                    "w-12 h-12 rounded-full bg-slate-100 shadow-sm shrink-0"
                                )
                            else:
                                ui.avatar(
                                    (p_name or "?")[0],
                                    color="slate-200",
                                    text_color="slate-600",
                                    size="lg",
                                ).classes("font-bold shrink-0")
                            with ui.column().classes("gap-0.5"):
                                ui.label(p_name).classes("font-semibold text-slate-800")
                                if assigned:
                                    ui.badge(
                                        current_team.replace("team_", "").capitalize(),
                                        color="emerald-100",
                                        text_color="emerald-700",
                                    ).classes("w-fit font-bold")
                        ui.label(p_club).classes("text-slate-500 text-sm")
                        rating_color = (
                            "bg-emerald-100 text-emerald-700"
                            if p_rating >= 80
                            else (
                                "bg-amber-100 text-amber-700"
                                if p_rating >= 55
                                else "bg-slate-100 text-slate-600"
                            )
                        )
                        ui.label(str(p_rating)).classes(
                            f"w-10 text-center py-0.5 rounded-full text-sm font-bold {rating_color}"
                        )
                        ui.label(f"{player_value} cr").classes("text-slate-500")
                        ui.label(f"{my_max_price} cr").classes("font-extrabold text-emerald-600")
                        ui.button(
                            "Edit" if assigned else "Assign",
                            icon="edit" if assigned else "person_add",
                            on_click=lambda p=p_name, t=current_team, price=current_price: (
                                open_assignment_dialog(p, t, price)
                            ),
                        ).props(
                            f"{'flat' if assigned else 'unelevated'} dense no-caps "
                            f"color={'slate' if assigned else 'positive'}"
                        ).classes(
                            "rounded-lg"
                        )

                if shown == 0:
                    with ui.column().classes("w-full p-12 items-center gap-2"):
                        ui.icon("search_off", size="lg").classes("text-slate-300")
                        ui.label("No players match your filters.").classes("text-slate-500")

    budget_bar()

    with ui.row().classes("w-full items-center gap-4 mb-4 no-wrap"):
        ui.input(placeholder="Search player or club...").props(
            "dense outlined clearable debounce=300"
        ).classes("w-72 bg-white rounded-lg").on_value_change(
            lambda e: (state.update(search=e.value or ""), market.refresh())
        )
        ui.switch(
            "Hide assigned",
            on_change=lambda e: (state.update(hide_assigned=bool(e.value)), market.refresh()),
        ).props(f"color={meta['q_color']}")

    market()


def teams_page(team_name: str):
    clean_name = team_name.replace("team_", "").capitalize()

    with ui.row().classes("items-center gap-4 w-full mb-6 no-wrap"):
        ui.avatar(clean_name[0], color="slate-900", text_color="white", size="lg").classes(
            "font-bold shadow-md"
        )
        with ui.column().classes("gap-0"):
            ui.label(f"Team {clean_name}").classes("text-3xl font-extrabold text-slate-900")
            ui.label("Roster breakdown and expenditure").classes("text-slate-500 text-sm")

    players = get_players_for_team(team_name)

    if not players:
        with ui.card().classes(
            "w-full p-12 text-center border border-dashed border-slate-300 shadow-none rounded-2xl"
        ):
            ui.icon("group_off", size="xl").classes("text-slate-300 mb-2")
            ui.label("No players assigned to this team yet.").classes("text-slate-500 text-base")
            ui.button(
                "Browse Market",
                on_click=lambda: ui.navigate.to("/goalkeepers"),
            ).props("flat color=primary")
        return

    grouped_players = {role: [] for role in ROLE_META}
    for player in players:
        role_key = (player.get("role") or "").lower()
        key = role_key if role_key in ROLE_META else "other"
        grouped_players.setdefault(key, []).append(player)

    total_spent = sum(p.get("paid_value", 0) for p in players)
    total_slots = sum(NUMBER_OF_PLAYERS_PER_ROLE.values())

    role_colors = {
        "goalkeepers": "#f59e0b",
        "defenders": "#3b82f6",
        "midfielders": "#10b981",
        "attackers": "#f43f5e",
    }
    pie_data = [
        {
            "name": ROLE_META[r]["label"] if r in ROLE_META else r.capitalize(),
            "value": sum(p.get("paid_value", 0) for p in group),
            "itemStyle": {"color": role_colors.get(r, "#94a3b8")},
        }
        for r, group in grouped_players.items()
        if group
    ]

    with ui.grid(columns="1 md:3").classes("w-full gap-4 mb-6"):
        with ui.card().classes("p-5 border border-slate-200 shadow-sm rounded-2xl"):
            ui.label("Total Squad Size").classes("text-xs text-slate-500 font-bold uppercase")
            ui.label(f"{len(players)} / {total_slots} Players").classes(
                "text-2xl font-black text-slate-800"
            )
            ui.linear_progress(
                value=min(len(players) / total_slots, 1.0), show_value=False, color="blue"
            ).props("rounded size=8px").classes("mt-3")
        with ui.card().classes("p-5 border border-slate-200 shadow-sm rounded-2xl"):
            ui.label("Total Budget Spent").classes("text-xs text-slate-500 font-bold uppercase")
            ui.label(f"{total_spent} / {MAX_CREDIT_AMOUNT} cr").classes(
                "text-2xl font-black text-emerald-600"
            )
            ui.linear_progress(
                value=min(total_spent / MAX_CREDIT_AMOUNT, 1.0), show_value=False, color="teal"
            ).props("rounded size=8px").classes("mt-3")
        with ui.card().classes("p-3 border border-slate-200 shadow-sm rounded-2xl"):
            ui.label("Spend by Role").classes("text-xs text-slate-500 font-bold uppercase")
            ui.echart(
                {
                    "tooltip": {"trigger": "item", "formatter": "{b}: {c} cr ({d}%)"},
                    "series": [
                        {
                            "type": "pie",
                            "radius": ["55%", "85%"],
                            "itemStyle": {
                                "borderRadius": 6,
                                "borderColor": "#fff",
                                "borderWidth": 2,
                            },
                            "label": {"show": False},
                            "data": pie_data,
                        }
                    ],
                }
            ).classes("w-full h-32")

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

    for role, role_players in grouped_players.items():
        if not role_players:
            continue
        role_spent = sum(p.get("paid_value", 0) for p in role_players)
        meta = ROLE_META.get(role)
        with (
            ui.expansion(
                f"{meta['label'] if meta else role.capitalize()} ({len(role_players)})",
                icon=meta["icon"] if meta else "help",
                caption=f"Subtotal: {role_spent} cr",
                value=True,
            )
            .classes(
                "w-full mb-4 bg-white border border-slate-200 rounded-2xl shadow-sm "
                "overflow-hidden"
            )
            .props("header-class=font-bold")
        ):
            ui.table(columns=columns, rows=role_players, row_key="name").props(
                "flat dense"
            ).classes("w-full")


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


ui.run(root, port=int(os.getenv("PORT", "8080")), reload=False)
