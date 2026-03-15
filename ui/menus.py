from simple_term_menu import TerminalMenu
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.table import Table
from rich.text import Text
from rich.align import Align
from datetime import timedelta
from typing import Optional

from core.data_loader import load_session
from core.analysis import (
    compare_laps,
    find_best_lap_per_driver,
    find_fastest_sector,
    analyze_tyre_degradation
)

# claude helped me with the rich/simple_term_menu funciotns, since its repeditive to read the whole doc 
console = Console()


def main_menu() -> str:
    options = [
        "Analyze Current Session",
        "Load Different Session",
        "Exit"
    ]
    
    menu = TerminalMenu(
        options,
        title="┃ F1 PERFORMANCE ANALYSIS ┃",
        menu_cursor="▶ ",
        menu_cursor_style=("fg_red", "bold"),
        menu_highlight_style=("fg_red", "bold"),
    )
    
    idx = menu.show()
    
    if idx == 0:
        return "analyze"
    elif idx == 1:
        return "load_session"
    else:
        return "exit"


def analysis_menu() -> str:
    options = [
        "Compare Two Drivers",
        "Analyze Sectors",
        "Tire Degradation Analysis",
        "Speed Trap Analysis",
        "Back to Main Menu"
    ]
    
    menu = TerminalMenu(
        options,
        title="┃ SELECT ANALYSIS ┃",
        menu_cursor="▶ ",
        menu_cursor_style=("fg_cyan", "bold"),
        menu_highlight_style=("fg_cyan", "bold"),
    )
    
    idx = menu.show()
    
    if idx == 0:
        return "compare"
    elif idx == 1:
        return "sectors"
    elif idx == 2:
        return "degradation"
    elif idx == 3:
        return "speed_trap"
    else:
        return "back"


def select_driver_from_session(session_data, title: str = "Select Driver") -> Optional[str]:
    drivers = sorted(session_data.drivers)
    
    menu = TerminalMenu(
        drivers,
        title=f"┃ {title} ┃",
        menu_cursor="▶ ",
        menu_cursor_style=("fg_green", "bold"),
        menu_highlight_style=("fg_green", "bold"),
    )
    
    idx = menu.show()
    return drivers[idx] if idx is not None else None


def select_two_drivers(session_data) -> tuple:
    console.print("\n[bold cyan]Select first driver:[/bold cyan]")
    driver1 = select_driver_from_session(session_data, "DRIVER 1")
    
    if driver1 is None:
        return None, None
    
    console.print(f"\n[bold cyan]Select second driver:[/bold cyan]")
    driver2 = select_driver_from_session(session_data, "DRIVER 2")
    
    return driver1, driver2


def display_comparison_result(comparison, lap1, lap2):
    delta_seconds = comparison.lap_time_delta.total_seconds()
    
    if delta_seconds > 0:
        delta_color = "red"
        winner = comparison.driver1
    else:
        delta_color = "green"
        winner = comparison.driver2
    
    lap_table = Table(title="Lap Times", show_header=True, header_style="bold cyan")
    lap_table.add_column("Driver", style="cyan", width=10)
    lap_table.add_column("Time", style="green", width=12)
    lap_table.add_row(lap1.driver, lap1.formatted_lap_time())
    lap_table.add_row(lap2.driver, lap2.formatted_lap_time())
    
    sector_table = Table(title="Sector Breakdown", show_header=True, header_style="bold cyan")
    sector_table.add_column("Sector", style="cyan", width=8)
    sector_table.add_column(lap1.driver, style="green", width=12)
    sector_table.add_column(lap2.driver, style="green", width=12)
    sector_table.add_column("Delta", style="yellow", width=12)
    
    for sector in [1, 2, 3]:
        s1_time = lap1.formatted_sector(sector)
        s2_time = lap2.formatted_sector(sector)
        delta = comparison.sector_deltas.get(sector, None)
        
        if delta:
            delta_str = f"+{delta.total_seconds():.3f}s" if delta.total_seconds() > 0 else f"{delta.total_seconds():.3f}s"
        else:
            delta_str = "—"
        
        sector_table.add_row(f"S{sector}", s1_time, s2_time, delta_str)
    
    summary = f"""
[bold cyan]{comparison.driver1}[/bold cyan] vs [bold cyan]{comparison.driver2}[/bold cyan]

[bold]Lap Time Delta:[/bold] [{delta_color}]{abs(delta_seconds):.3f}s[/{delta_color}]
[bold]Winner:[/bold] [green]{winner}[/green]
[bold]Biggest Gap:[/bold] Sector {comparison.best_sector}
    """
    
    left_panel = Panel(summary, title="[bold]Summary[/bold]", border_style="cyan")
    right_content = Columns([lap_table, sector_table], equal=False, expand=False)
    
    console.print(Columns([left_panel, right_content], equal=False))
    
    # Key insights
    console.print("\n[bold yellow]Key Insights:[/bold yellow]")
    for area in comparison.improvement_areas:
        console.print(f"  • {area}")


def display_sector_analysis(session_data):
    """Display fastest sector times for all drivers"""
    sector_options = ["Sector 1", "Sector 2", "Sector 3"]
    
    menu = TerminalMenu(
        sector_options,
        title="┃ SELECT SECTOR ┃",
        menu_cursor="▶ ",
        menu_cursor_style=("fg_yellow", "bold"),
        menu_highlight_style=("fg_yellow", "bold"),
    )
    
    idx = menu.show()
    if idx is None:
        return
    
    sector = idx + 1
    fastest = find_fastest_sector(session_data, sector)
    
    sorted_drivers = sorted(fastest.items(), key=lambda x: x[1])
    
    table = Table(title=f"Fastest Sector {sector} Times", show_header=True, header_style="bold cyan")
    table.add_column("Pos", width=4, justify="right", style="dim")
    table.add_column("Driver", width=10, style="cyan")
    table.add_column("Time", width=15, justify="right", style="green")
    table.add_column("Gap to Best", width=15, justify="right", style="yellow")
    
    best_time = sorted_drivers[0][1] if sorted_drivers else None
    
    for i, (driver, sector_time) in enumerate(sorted_drivers[:10], start=1):
        gap = sector_time - best_time if best_time else None
        gap_str = f"+{gap.total_seconds():.3f}s" if gap and gap.total_seconds() > 0 else "—"
        
        time_str = f"{sector_time}"
        table.add_row(str(i), driver, time_str, gap_str)
    
    console.print(Panel(table, title=f"[bold]Sector {sector} Analysis[/bold]", border_style="cyan"))


def display_tire_degradation(session_data):
    driver = select_driver_from_session(session_data, "SELECT DRIVER")
    
    if not driver:
        return
    
    # Optional: Filter by compound
    compounds = set([lap.tyre_compound for lap in session_data.laps if lap.driver == driver])
    
    if len(compounds) > 1:
        console.print(f"\n[dim]Found {len(compounds)} tire compounds: {', '.join(compounds)}[/dim]")
        compound_choice = console.input("[yellow]Analyze all compounds or specific? (all/specific):[/yellow] ").strip().lower()
        compound = None if compound_choice == "all" else list(compounds)[0]
    else:
        compound = None
    
    degradation = analyze_tyre_degradation(driver, session_data, compound)
    
    if not degradation:
        console.print("[red]No data found[/red]")
        return
    
    table = Table(title=f"{driver} - Tire Degradation", show_header=True, header_style="bold cyan")
    table.add_column("Lap", width=6, justify="right", style="dim")
    table.add_column("Time (s)", width=12, justify="right", style="green")
    table.add_column("Δ vs Lap 1", width=12, justify="right", style="yellow")
    
    lap_nums = sorted(degradation.keys())
    first_time = degradation[lap_nums[0]] if lap_nums else 0
    
    for lap_num in lap_nums[:15]:  
        time = degradation[lap_num]
        delta = time - first_time
        delta_str = f"+{delta:.3f}s" if delta > 0 else f"{delta:.3f}s"
        
        table.add_row(str(int(lap_num)), f"{time:.3f}", delta_str)
    
    console.print(Panel(table, title="[bold]Degradation Analysis[/bold]", border_style="cyan"))
    
    console.print("\n[dim]Note: Raw lap times include multiple factors (temp, traffic, etc.)[/dim]")
    console.print("[dim]For pure tire degradation analysis, use fuel-corrected times.[/dim]")


def load_session_menu() -> tuple:
    console.print("\n[bold cyan]Load F1 Session[/bold cyan]\n")
    
    year = console.input("[yellow]Enter year (e.g., 2024):[/yellow] ").strip()
    event = console.input("[yellow]Enter event (e.g., Monaco):[/yellow] ").strip()
    
    session_types = ["Q (Qualifying)", "R (Race)", "FP1", "FP2", "FP3"]
    menu = TerminalMenu(
        session_types,
        title="┃ SESSION TYPE ┃",
        menu_cursor="▶ ",
        menu_cursor_style=("fg_green", "bold"),
        menu_highlight_style=("fg_green", "bold"),
    )
    
    idx = menu.show()
    if idx is None:
        return None, None, None
    
    session_type = session_types[idx].split()[0]
    
    return int(year), event, session_type


def run_analysis_workflow(session_data):
    while True:
        feature = analysis_menu()
        
        if feature == "back":
            break
        elif feature == "compare":
            driver1, driver2 = select_two_drivers(session_data)
            if driver1 and driver2:
                best_laps = find_best_lap_per_driver(session_data)
                lap1 = best_laps[driver1]
                lap2 = best_laps[driver2]
                
                comparison = compare_laps(lap1, lap2)
                if comparison:
                    display_comparison_result(comparison, lap1, lap2)
                else:
                    console.print("[red]Could not compare laps[/red]")
            
            console.input("\n[dim]Press Enter to continue...[/dim]")
        
        elif feature == "sectors":
            display_sector_analysis(session_data)
            console.input("\n[dim]Press Enter to continue...[/dim]")
        
        elif feature == "degradation":
            display_tire_degradation(session_data)
            console.input("\n[dim]Press Enter to continue...[/dim]")
        
        elif feature == "speed_trap":
            console.print("[yellow]Speed Trap Analysis - Coming soon![/yellow]")
            console.input("[dim]Press Enter to continue...[/dim]")
