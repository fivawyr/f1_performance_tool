import fastf1 as f1_dataset
import pandas as pd
from ui.ui_functions import show_banner, select_team
from ui.menus import main_menu, run_analysis_workflow, load_session_menu
from core.data_loader import load_session

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress_bar import ProgressBar

console = Console()

team = select_team()
show_banner(team)

console.print("[bold cyan]Loading default session (2024 Monaco Qualifying)...[/bold cyan]\n")
session_data = load_session(2024, "Monaco", "Q")

while True:
    choice = main_menu()
    
    if choice == "analyze":
        console.clear()
        run_analysis_workflow(session_data)
        console.clear()
    
    elif choice == "load_session":
        console.clear()
        year, event, session_type = load_session_menu()
        if year and event and session_type:
            try:
                session_data = load_session(year, event, session_type)
                console.print(f"\n[green]Session loaded: {year} {event} {session_type}[/green]")
            except Exception as e:
                console.print(f"[red]Error loading session: {e}[/red]")
        console.input("[dim]Press Enter to continue...[/dim]")
        console.clear()
    
    elif choice == "exit":
        console.print("[yellow]Goodbye! [/yellow]")
        break

