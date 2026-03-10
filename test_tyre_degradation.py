import sys
from pathlib import Path
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
"""
Note: I used claude to write those test statements, excluding analysis & business model 
"""
sys.path.insert(0, str(Path(__file__).parent))

from core.data_loader import load_session
from features.tyre_degradation import analyze_stint, analyze_all

console = Console()


def _color_r_squared(r2: float) -> str:
    """Color code R² values based on quality"""
    if r2 > 0.7:
        return f"[green]{r2:.3f}[/green]"
    elif r2 > 0.4:
        return f"[yellow]{r2:.3f}[/yellow]"
    else:
        return f"[red]{r2:.3f}[/red]"


def main():
    session_data = load_session(2024, "Monaco", "Q")
    console.print(f"[cyan]Loaded {len(session_data.laps)} laps[/cyan]\n")

    # Test single stint
    result = analyze_stint(session_data, "HAM", "SOFT", 1)
    if result:
        console.print(f"[green]✓ {result.key.driver} {result.key.compound} Stint {result.key.stint}[/green]")
        console.print(f"  Model Type: {result.model_type.upper()}")
        console.print(f"  Laps: {result.num_laps}")
        console.print(f"  Baseline: {result.baseline_time_ms:.0f}ms ({result.baseline_time_ms/1000/60:.2f}m)")
        console.print(f"  Degradation: {result.degradation_rate_ms_per_lap:.3f}ms/lap")
        console.print(f"  R² (Linear): {result.r_squared:.3f}")
        console.print(f"  R² (Quadratic): {result.r_squared_quadratic:.3f}")
        console.print(f"  R² (Exponential): {result.r_squared_exponential:.3f}\n")

    # Test all stints
    results = analyze_all(session_data)
    
    # Filter for meaningful stints (3+ laps, R² > 0.3)
    meaningful_results = {
        k: v for k, v in results.items() 
        if v.num_laps >= 3 and v.r_squared > 0.3
    }
    
    console.print(Panel(
        f"[yellow]Total stints: {len(results)} | Meaningful fits (3+ laps, R²>0.3): {len(meaningful_results)}[/yellow]",
        title="Analysis Summary",
        expand=False
    ))
    
    table = Table(title="All Tire Degradation Results (sorted by R²)")
    table.add_column("Driver", style="cyan")
    table.add_column("Compound", style="magenta")
    table.add_column("Stint", justify="right")
    table.add_column("Laps", justify="right")
    table.add_column("Model", style="blue")
    table.add_column("Baseline [ms]", justify="right")
    table.add_column("R²", justify="right")
    
    # Sort by R² descending
    for (driver, compound, stint), result in sorted(
        results.items(), 
        key=lambda x: x[1].r_squared, 
        reverse=True
    ):
        r2_color = _color_r_squared(result.r_squared)
        table.add_row(
            driver,
            compound,
            str(stint),
            str(result.num_laps),
            result.model_type,
            f"{result.baseline_time_ms:.0f}",
            r2_color,
        )
    
    console.print(table)
    
    if meaningful_results:
        console.print("\n[green]Meaningful fits found (R² > 0.3)[/green]")
        for (driver, compound, stint), result in sorted(
            meaningful_results.items(),
            key=lambda x: x[1].r_squared,
            reverse=True
        ):
            console.print(f"  {driver} {compound} Stint {stint}: R²={result.r_squared:.3f} ({result.model_type})")
    else:
        console.print("\n[yellow]No meaningful fits found in this session[/yellow]")
        console.print("   Tip: Qualifying sessions typically show poor tire degradation fits (R² < 0.3)")
        console.print("   Try analyzing race data instead (50+ consecutive laps)")


if __name__ == "__main__":
    main()
