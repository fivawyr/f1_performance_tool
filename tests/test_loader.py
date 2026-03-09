from core.data_loader import load_session
from rich.console import Console
from rich.table import Table

console = Console()

session_data = load_session(2018, "Monaco", "Q")

console.print(f"\n[bold cyan]Session Info:[/bold cyan]")
console.print(f"  Year: {session_data.year}")
console.print(f"  Event: {session_data.event}")
console.print(f"  Session Type: {session_data.session_type}")
console.print(f"  Total Drivers: {len(session_data.drivers)}")
console.print(f"  Total Valid Laps: {len(session_data.laps)}\n")

console.print("[bold cyan]First 5 Laps:[/bold cyan]")
table = Table(header_style="bold cyan", border_style="dim")
table.add_column("Driver", width=10)
table.add_column("Lap #", width=6, justify="right")
table.add_column("Lap Time", width=12, justify="right", style="green")
table.add_column("Sector1", width=12, justify="right")
table.add_column("Compound", width=10)
table.add_column("Personal Best?", width=12)

for lap in session_data.laps[:5]:
    table.add_row(
        lap.driver,
        str(int(lap.lap_number)),
        str(lap.lap_time) if lap.lap_time else "—",
        str(lap.sector1) if lap.sector1 else "—",
        lap.tyre_compound,
        "yes" if lap.is_personal_best else "no"
    )

console.print(table)

