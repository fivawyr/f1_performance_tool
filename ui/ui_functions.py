from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich import box

console = Console()

TEAMS = {
    "Red Bull Racing": {
        "color": "#3671C6",
        "accent": "#CC1E4A",
        "chassis": "RB20",
        "engine": "Honda RBPT",
        "base": "Milton Keynes",
        "drivers": "VER · PER",
        "art": (
            "[bold #3671C6]██████╗ ███████╗██████╗     ██████╗ ██╗   ██╗██╗     ██╗[/]\n"
            "[bold #3671C6]██╔══██╗██╔════╝██╔══██╗    ██╔══██╗██║   ██║██║     ██║[/]\n"
            "[bold #3671C6]██████╔╝█████╗  ██║  ██║    ██████╔╝██║   ██║██║     ██║[/]\n"
            "[bold #3671C6]██╔══██╗██╔══╝  ██║  ██║    ██╔══██╗██║   ██║██║     ██║[/]\n"
            "[bold #3671C6]██║  ██║███████╗██████╔╝    ██████╔╝╚██████╔╝███████╗███████╗[/]\n"
            "[bold #3671C6]╚═╝  ╚═╝╚══════╝╚═════╝     ╚═════╝  ╚═════╝ ╚══════╝╚══════╝[/]"
        ),
    },
    "Scuderia Ferrari": {
        "color": "#E8002D",
        "accent": "#FFFF00",
        "chassis": "SF-24",
        "engine": "Ferrari",
        "base": "Maranello",
        "drivers": "LEC · SAI",
        "art": (
            "[bold #E8002D]███████╗███████╗██████╗ ██████╗  █████╗ ██████╗ ██╗[/]\n"
            "[bold #E8002D]██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗██║[/]\n"
            "[bold #E8002D]█████╗  █████╗  ██████╔╝██████╔╝███████║██████╔╝██║[/]\n"
            "[bold #E8002D]██╔══╝  ██╔══╝  ██╔══██╗██╔══██╗██╔══██║██╔══██╗██║[/]\n"
            "[bold #E8002D]██║     ███████╗██║  ██║██║  ██║██║  ██║██║  ██║██║[/]\n"
            "[bold #E8002D]╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝[/]"
        ),
    },
    "Mercedes-AMG": {
        "color": "#27F4D2",
        "accent": "#000000",
        "chassis": "W15",
        "engine": "Mercedes",
        "base": "Brackley",
        "drivers": "HAM · RUS",
        "art": (
            "[bold #27F4D2]███╗   ███╗███████╗██████╗  ██████╗███████╗██████╗ ███████╗[/]\n"
            "[bold #27F4D2]████╗ ████║██╔════╝██╔══██╗██╔════╝██╔════╝██╔══██╗██╔════╝[/]\n"
            "[bold #27F4D2]██╔████╔██║█████╗  ██████╔╝██║     █████╗  ██║  ██║█████╗  [/]\n"
            "[bold #27F4D2]██║╚██╔╝██║██╔══╝  ██╔══██╗██║     ██╔══╝  ██║  ██║██╔══╝  [/]\n"
            "[bold #27F4D2]██║ ╚═╝ ██║███████╗██║  ██║╚██████╗███████╗██████╔╝███████╗[/]\n"
            "[bold #27F4D2]╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚══════╝╚═════╝ ╚══════╝[/]"
        ),
    },
    "McLaren": {
        "color": "#FF8000",
        "accent": "#000000",
        "chassis": "MCL38",
        "engine": "Mercedes",
        "base": "Woking",
        "drivers": "NOR · PIA",
        "art": (
            "[bold #FF8000]███╗   ███╗ ██████╗██╗      █████╗ ██████╗ ███████╗███╗   ██╗[/]\n"
            "[bold #FF8000]████╗ ████║██╔════╝██║     ██╔══██╗██╔══██╗██╔════╝████╗  ██║[/]\n"
            "[bold #FF8000]██╔████╔██║██║     ██║     ███████║██████╔╝█████╗  ██╔██╗ ██║[/]\n"
            "[bold #FF8000]██║╚██╔╝██║██║     ██║     ██╔══██║██╔══██╗██╔══╝  ██║╚██╗██║[/]\n"
            "[bold #FF8000]██║ ╚═╝ ██║╚██████╗███████╗██║  ██║██║  ██║███████╗██║ ╚████║[/]\n"
            "[bold #FF8000]╚═╝     ╚═╝ ╚═════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝[/]"
        ),
    },
    "Aston Martin": {
        "color": "#229971",
        "accent": "#CEDC00",
        "chassis": "AMR24",
        "engine": "Mercedes",
        "base": "Silverstone",
        "drivers": "ALO · STR",
        "art": (
            "[bold #229971] █████╗ ███████╗████████╗ ██████╗ ███╗   ██╗[/]\n"
            "[bold #229971]██╔══██╗██╔════╝╚══██╔══╝██╔═══██╗████╗  ██║[/]\n"
            "[bold #229971]███████║███████╗   ██║   ██║   ██║██╔██╗ ██║[/]\n"
            "[bold #229971]██╔══██║╚════██║   ██║   ██║   ██║██║╚██╗██║[/]\n"
            "[bold #229971]██║  ██║███████║   ██║   ╚██████╔╝██║ ╚████║[/]\n"
            "[bold #229971]╚═╝  ╚═╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═══╝[/]"
        ),
    },
    "Kick Sauber": {
        "color": "#52E252",
        "accent": "#E8002D",
        "chassis": "C44",
        "engine": "Ferrari",
        "base": "Hinwil",
        "drivers": "BOT · ZHO",
        "art": (
            "[bold #52E252] ██████╗ █████╗ ██╗   ██╗██████╗ ███████╗██████╗ [/]\n"
            "[bold #52E252]██╔════╝██╔══██╗██║   ██║██╔══██╗██╔════╝██╔══██╗[/]\n"
            "[bold #52E252]╚█████╗ ███████║██║   ██║██████╔╝█████╗  ██████╔╝[/]\n"
            "[bold #52E252] ╚═══██╗██╔══██║██║   ██║██╔══██╗██╔══╝  ██╔══██╗[/]\n"
            "[bold #52E252]██████╔╝██║  ██║╚██████╔╝██████╔╝███████╗██║  ██║[/]\n"
            "[bold #52E252]╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝[/]"
        ),
    },
    "Williams": {
        "color": "#64C4FF",
        "accent": "#041E42",
        "chassis": "FW46",
        "engine": "Mercedes",
        "base": "Grove",
        "drivers": "ALB · SAR",
        "art": (
            "[bold #64C4FF]██╗    ██╗██╗██╗     ██╗     ██╗ █████╗ ███╗   ███╗███████╗[/]\n"
            "[bold #64C4FF]██║    ██║██║██║     ██║     ██║██╔══██╗████╗ ████║██╔════╝[/]\n"
            "[bold #64C4FF]██║ █╗ ██║██║██║     ██║     ██║███████║██╔████╔██║███████╗[/]\n"
            "[bold #64C4FF]██║███╗██║██║██║     ██║     ██║██╔══██║██║╚██╔╝██║╚════██║[/]\n"
            "[bold #64C4FF]╚███╔███╔╝██║███████╗███████╗██║██║  ██║██║ ╚═╝ ██║███████║[/]\n"
            "[bold #64C4FF] ╚══╝╚══╝ ╚═╝╚══════╝╚══════╝╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝[/]"
        ),
    },
}


def show_banner(team_name: str):
    team = TEAMS[team_name]
    c = team["color"]

    speed = f"[{c}]▰▰▰▰▰▰▰▰▰▰▰▰▰[/] [white]▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰[/] [{c}]▰▰▰▰▰▰▰▰▰▰▰▰▰[/]"
    subtitle = "[bold white]  F1 Data Analysis Tool  ·  Powered by FastF1  [/bold white]"
    meta = f"[dim]  Chassis: {team['chassis']}  ·  Engine: {team['engine']}  ·  Base: {team['base']}  ·  Drivers: {team['drivers']}[/dim]"
    content = f"{team['art']}\n\n{subtitle}\n{speed}\n{meta}"
    console.print(Panel(
        content,
        border_style=c,
        padding=(0, 2),
        box=box.HEAVY,
    ))
    console.print(Rule(style=c))
    console.print()


def select_team() -> str:
    from simple_term_menu import TerminalMenu # lazy import, since simple_term tend to need some time to load

    console.print("[bold white]Select your team:[/bold white]\n")

    team_names = list(TEAMS.keys())
    menu = TerminalMenu(
        team_names,
        title="  F1 Team Selector",
        menu_cursor="▶ ",
        menu_cursor_style=("fg_red", "bold"),
        menu_highlight_style=("fg_red", "bold"),
    )
    idx = menu.show()

    if idx is None:
        console.print("[red]No team selected. Exiting.[/red]")
        raise SystemExit(0)

    return team_names[idx] # type: ignore 
 