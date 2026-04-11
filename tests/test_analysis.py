"""
Test script for core/analysis.py
"""

from core.data_loader import load_session
from core.analysis import (
    compare_laps, 
    find_best_lap_per_driver,
    find_fastest_sector,
    analyze_tyre_degradation
)
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

console.print("[bold cyan]Loading session...[/bold cyan]")
session_data = load_session(2018, "Monaco", "Q")

console.print(f"\n[bold cyan]Session loaded with {len(session_data.laps)} valid laps[/bold cyan]")
console.print(f"[dim]Available drivers: {', '.join(session_data.drivers)}[/dim]\n")

console.print("[bold yellow]TEST 1: Compare Two Drivers[/bold yellow]\n")

best_laps = find_best_lap_per_driver(session_data)

console.print(f"[dim]Found best laps for {len(best_laps)} drivers[/dim]")
drivers_list = list(best_laps.keys())[:5]
console.print(f"[dim]Example drivers: {', '.join(drivers_list)}[/dim]\n")

drivers_to_compare = list(best_laps.keys())[:2]

if len(drivers_to_compare) >= 2:
    driver1 = drivers_to_compare[0]
    driver2 = drivers_to_compare[1]
    
    lap1 = best_laps[driver1]
    lap2 = best_laps[driver2]
    
    console.print(f"Comparing [cyan]{driver1}[/cyan] (time: {lap1.lap_time}) vs [cyan]{driver2}[/cyan] (time: {lap2.lap_time})\n")
    
    comparison = compare_laps(lap1, lap2)
    
    if comparison:
        console.print(f"  Lap time delta: [green]{comparison.lap_time_delta}[/green]")
        console.print(f"  Sector deltas: {comparison.sector_deltas}")
        console.print(f"  Biggest gap in: Sector {comparison.best_sector}")
        console.print(f"  Areas for improvement: {', '.join(comparison.improvement_areas)}")
    else:
        console.print("[red]Could not compare laps[/red]")
else:
    console.print("[red]Not enough drivers to compare[/red]")

console.print(f"\n[bold yellow]TEST 2: Fastest Sector 1 Times[/bold yellow]")
console.print("[dim](Top 5 drivers)[/dim]\n")

fastest_s1 = find_fastest_sector(session_data, 1)

sorted_s1 = sorted(fastest_s1.items(), key=lambda x: x[1])[:5]
table = Table(header_style="bold cyan", border_style="dim")
table.add_column("Pos", width=4, justify="right")
table.add_column("Driver", width=10)
table.add_column("Sector 1 Time", width=15, justify="right", style="green")

for i, (driver, time) in enumerate(sorted_s1, start=1):
    table.add_row(str(i), driver, f"{time}")

console.print(table)

console.print(f"\n[bold yellow]TEST 3: Tire Degradation Analysis[/bold yellow]")

first_driver = list(best_laps.keys())[0] if best_laps else None

if first_driver:
    console.print(f"[dim]({first_driver}'s lap times over stints)[/dim]\n")
    
    degradation = analyze_tyre_degradation(first_driver, session_data)
    
    if degradation:
        console.print("Lap Number -> Lap Time (seconds):")
        for lap_num in sorted(degradation.keys())[:10]:
            console.print(f"  Lap {int(lap_num):2d}: {degradation[lap_num]:7.3f}s")
        
        console.print("\n[dim]Note: Lap times vary due to multiple factors:[/dim]")
        console.print("[dim]  - Tire degradation[/dim]")
        console.print("[dim]  - Driver aggressiveness[/dim]")
        console.print("[dim]  - Track temperature[/dim]")
        console.print("[dim]  - Traffic/Position[/dim]")
        console.print("[dim]For accurate tire analysis, use fuel-corrected times! -> features/tyre_degradation[/dim]")
    else:
        console.print("[red]No data found for this driver[/red]")
else:
    console.print("[red]No data available[/red]")

console.print("\n[bold green]All tests completed![/bold green]")
