#!/usr/bin/env python3
import sys
from pathlib import Path
from typing import Dict, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from core.data_loader import load_session
from core.models import SessionData
from features.tyre_degradation import analyse_all, TireDegradationResult
import json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

console = Console()

def print_analysis_summary(
    results: Dict[Tuple[str, str, int], TireDegradationResult],
    session_data: SessionData) -> None:
    
    console.print()
    console.print(Panel(
        f"[bold cyan]{session_data.year} {session_data.event} {session_data.session_type}[/bold cyan]",
        expand=False))
    
    console.print(f"\n[bold]Analysis Results:[/bold]")
    console.print(f"Total stints analyzed: {len(results)}")
    console.print(f"Total laps in session: {len(session_data.laps)}")
    console.print(f"Unique drivers: {len(session_data.drivers)}")
    
    r_squared_values = [r.r_squared for r in results.values()]
    if r_squared_values:
        avg_r2 = sum(r_squared_values) / len(r_squared_values)
        max_r2 = max(r_squared_values)
        min_r2 = min(r_squared_values)
        
        console.print(f"\n[bold]R² Statistics:[/bold]")
        console.print(f"Average R²: {avg_r2:.3f}")
        console.print(f"Max R²: {max_r2:.3f}")
        console.print(f"Min R²: {min_r2:.3f}")
        
        high_quality = sum(1 for r in r_squared_values if r > 0.6)
        medium_quality = sum(1 for r in r_squared_values if 0.3 <= r <= 0.6)
        low_quality = sum(1 for r in r_squared_values if r < 0.3)
        
        console.print(f"\n[bold]Quality Distribution:[/bold]") # percentage representation of the amount of model use
        console.print(f"[green]High quality (R² > 0.6)[/green]: {high_quality} ({100*high_quality/len(results):.1f}%)")
        console.print(f"[yellow]Medium quality (0.3 ≤ R² ≤ 0.6)[/yellow]: {medium_quality} ({100*medium_quality/len(results):.1f}%)")
        console.print(f"[red]Low quality (R² < 0.3)[/red]: {low_quality} ({100*low_quality/len(results):.1f}%)")
    
    model_counts = {}
    for result in results.values():
        model = result.model_type
        model_counts[model] = model_counts.get(model, 0) + 1
    
    console.print(f"\n[bold]Model Distribution:[/bold]")
    for model, count in sorted(model_counts.items()):
        console.print(f"  {model.capitalize()}: {count} ({100*count/len(results):.1f}%)")
    
    compound_counts = {}
    for key in results.keys():
        compound = key[1]
        compound_counts[compound] = compound_counts.get(compound, 0) + 1
    
    console.print(f"\n[bold]Tire Compound Distribution:[/bold]")
    for compound, count in sorted(compound_counts.items()):
        console.print(f"  {compound}: {count} stints")


def print_detailed_results(results: Dict[Tuple[str, str, int], TireDegradationResult]) -> None:    
    sorted_results = sorted(
        results.items(),
        key=lambda x: x[1].r_squared,
        reverse=True
    )
    
    # Create table
    table = Table(
        title="Detailed Tire Degradation Analysis Results",
        show_header=True,
        header_style="bold cyan"
    )
    
    table.add_column("Driver", style="cyan", width=8)
    table.add_column("Compound", style="magenta", width=10)
    table.add_column("Stint", justify="right", width=5)
    table.add_column("Laps", justify="right", width=5)
    table.add_column("Baseline (ms)", justify="right", width=15)
    table.add_column("Degrad. (ms/lap)", justify="right", width=15)
    table.add_column("R²", justify="right", width=10)
    table.add_column("Model", style="green", width=10)
    
    for (driver, compound, stint), result in sorted_results:
        # Color code R² values
        if result.r_squared > 0.6:
            r2_style = "green"
        elif result.r_squared > 0.3:
            r2_style = "yellow"
        else:
            r2_style = "red"
        
        table.add_row(
            driver,
            compound,
            str(stint),
            str(result.num_laps),
            f"{result.baseline_time_ms:.0f}",
            f"{result.degradation_rate_ms_per_lap:.2f}",
            f"[{r2_style}]{result.r_squared:.3f}[/{r2_style}]",
            result.model_type
        )
    
    console.print(table)


def save_results_to_file(
    results: Dict[Tuple[str, str, int], TireDegradationResult],
    session_data: SessionData,
    output_dir: str = "analysis_results") -> str:
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    race_label = f"{session_data.year}_{session_data.event}_{session_data.session_type}"
    
    json_file = output_path / f"race_analysis_{race_label}_{timestamp}.json"
    json_data = {
        "session": {
            "year": session_data.year,
            "event": session_data.event,
            "session_type": session_data.session_type,
        },
        "timestamp": timestamp,
        "summary": {
            "total_stints": len(results),
            "total_laps": len(session_data.laps),
            "unique_drivers": len(session_data.drivers),
            "avg_r_squared": sum(r.r_squared for r in results.values()) / len(results) if results else 0,
        },
        "results": [
            {
                "driver": key[0],
                "compound": key[1],
                "stint": key[2],
                **result.to_dict()
            }
            for key, result in results.items()
        ]
    }
    
    with open(json_file, "w") as f:
        json.dump(json_data, f, indent=2)
    
    console.print(f"\n[green]✓[/green] Results saved to: {json_file}")
    
    # Save to markdown for easy reading
    md_file = output_path / f"race_analysis_{race_label}_{timestamp}.md"
    with open(md_file, "w") as f:
        f.write(f"# Race Analysis: {race_label}\n\n")
        f.write(f"**Date**: {timestamp}\n\n")
        
        f.write("## Summary\n\n")
        r_squared_values = [r.r_squared for r in results.values()]
        f.write(f"- **Total stints analyzed**: {len(results)}\n")
        f.write(f"- **Total laps**: {len(session_data.laps)}\n")
        f.write(f"- **Average R²**: {sum(r_squared_values) / len(r_squared_values):.3f}\n")
        f.write(f"- **Unique drivers**: {len(session_data.drivers)}\n\n")
        
        high_quality = sum(1 for r in r_squared_values if r > 0.6)
        medium_quality = sum(1 for r in r_squared_values if 0.3 <= r <= 0.6)
        low_quality = sum(1 for r in r_squared_values if r < 0.3)
        
        f.write("## Quality Distribution\n\n")
        f.write(f"- **High quality (R² > 0.6)**: {high_quality} ({100*high_quality/len(results):.1f}%)\n")
        f.write(f"- **Medium quality (0.3 ≤ R² ≤ 0.6)**: {medium_quality} ({100*medium_quality/len(results):.1f}%)\n")
        f.write(f"- **Low quality (R² < 0.3)**: {low_quality} ({100*low_quality/len(results):.1f}%)\n\n")
        
        f.write("## Detailed Results\n\n")
        f.write("| Driver | Compound | Stint | Laps | Baseline (ms) | Degrad. (ms/lap) | R² | Model |\n")
        f.write("|--------|----------|-------|------|---------------|------------------|----|-------|\n")
        
        sorted_results = sorted(results.items(), key=lambda x: x[1].r_squared, reverse=True)
        for (driver, compound, stint), result in sorted_results:
            f.write(f"| {driver} | {compound} | {stint} | {result.num_laps} | {result.baseline_time_ms:.0f} | {result.degradation_rate_ms_per_lap:.2f} | {result.r_squared:.3f} | {result.model_type} |\n")
    
    console.print(f"[green]✓[/green] Markdown report saved to: {md_file}")
    
    return str(json_file)


def main():
    
    console.print("\n" + "="*70)
    console.print("[bold cyan]PHASE 2: RACE DATA ANALYSIS[/bold cyan]")
    console.print("="*70)

    console.print("\n[bold]Step 1: Loading 2022 British Grand Prix Race Data[/bold]")
    session = load_session(2022, "British", "R")
    
    # Run analysis
    console.print("\n[bold]Step 2: Analyzing All Stints[/bold]")
    with console.status("[cyan]Analyzing tire degradation...", spinner="dots"):
        results = analyse_all(session)
    
    console.print("\n[bold]Step 3: Results Summary[/bold]")
    print_analysis_summary(results, session)
    
    console.print("\n[bold]Step 4: Detailed Results[/bold]")
    print_detailed_results(results)
    
    console.print("\n[bold]Step 5: Saving Results[/bold]")
    save_results_to_file(results, session)
    
    console.print("\n" + "="*70)
    console.print("[bold cyan]ASSESSMENT[/bold cyan]")
    console.print("="*70)
    
    r_squared_values = [r.r_squared for r in results.values()]
    avg_r2 = sum(r_squared_values) / len(r_squared_values)
    
    if avg_r2 > 0.6:
        console.print(f"\n[green]SUCCESS![/green] Average R² = {avg_r2:.3f}")
        console.print("Race data shows strong degradation patterns!")
        console.print("Proceed to Phase 3: Data Preprocessing")
    elif avg_r2 > 0.3:
        console.print(f"\n[yellow]PARTIAL SUCCESS[/yellow] Average R² = {avg_r2:.3f}")
        console.print("Race data shows moderate patterns.")
        console.print("Phase 3 preprocessing should improve results significantly.")
    else:
        console.print(f"\n[red]LIMITED SUCCESS[/red] Average R² = {avg_r2:.3f}")
        console.print("Even race data shows weak patterns.")
        console.print("May need fuel correction or temperature adjustment in Phase 3.")
    
    console.print("\n" + "="*70)

if __name__ == "__main__":
    main()
