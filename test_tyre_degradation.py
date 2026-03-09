import sys
from pathlib import Path
from rich.table import Table
from rich.console import Console

sys.path.insert(0, str(Path(__file__).parent))

from core.data_loader import load_session
from features.tyre_degradation import analyze_stint, analyze_all

console = Console()


def main():
    session_data = load_session(2024, "Monaco", "Q")
    console.print(f"[cyan]Loaded {len(session_data.laps)} laps[/cyan]\n")

    # Test single stint
    result = analyze_stint(session_data, "HAM", "SOFT", 1)
    if result:
        console.print(f"[green]✓ {result.key.driver} {result.key.compound}[/green]")
        console.print(f"  Baseline: {result.baseline_time_ms:.0f}ms")
        console.print(f"  Degradation: {result.degradation_rate_ms_per_lap:.3f}ms/lap")
        console.print(f"  R²: {result.r_squared:.3f}\n")

    # Test all stints
    results = analyze_all(session_data)
    
    table = Table(title="Tire Degradation Analysis")
    table.add_column("Driver", style="cyan")
    table.add_column("Compound", style="magenta")
    table.add_column("Laps", justify="right")
    table.add_column("Baseline [ms]", justify="right")
    table.add_column("Degrad [ms/lap]", justify="right", style="yellow")
    table.add_column("R²", justify="right")
    
    for (driver, compound, stint), result in sorted(results.items()):
        table.add_row(
            driver,
            compound,
            str(result.num_laps),
            f"{result.baseline_time_ms:.0f}",
            f"{result.degradation_rate_ms_per_lap:.3f}",
            f"{result.r_squared:.3f}",
        )
    
    console.print(table)


if __name__ == "__main__":
    main()
