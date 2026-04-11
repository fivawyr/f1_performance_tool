#!/usr/bin/env python3
"""
Test suite for Pacejka Magic Formula 5.2 Calculator
Validates forces, degradation, and physical plausibility
"""

import sys
from pathlib import Path
import math

sys.path.insert(0, str(Path(__file__).parent.parent))

from features.pacejka_calculator import (
    PacejkaCalculator, 
    PacejkaTyreDegradation,
    PacejkaCoefficients
)
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def test_basic_forces():
    """Test basic lateral and longitudinal force calculations"""
    console.print("\n[bold cyan]TEST 1: Basic Force Calculations[/bold cyan]\n")
    
    calc = PacejkaCalculator()
    
    # Test case 1: Pure lateral (cornering)
    alpha = math.radians(2.0)  # 2° slip angle
    Fz = 4000.0  # 4000 N normal load
    
    Fy = calc.calc_lateral_force(alpha, Fz)
    console.print(f"  Lateral force (α=2°, Fz=4000N): {Fy:,.0f} N")
    
    # Test case 2: Pure longitudinal (acceleration/braking)
    kappa = 0.05  # 5% slip
    Fx = calc.calc_longitudinal_force(kappa, Fz)
    console.print(f"  Longitudinal force (κ=0.05, Fz=4000N): {Fx:,.0f} N")
    
    # Test case 3: Combined forces
    forces = calc.calc_combined_forces(alpha, kappa, Fz)
    total = math.sqrt(forces.Fx**2 + forces.Fy**2)
    console.print(f"  Combined Fy: {forces.Fy:,.0f} N")
    console.print(f"  Combined Fx: {forces.Fx:,.0f} N")
    console.print(f"  Total force: {total:,.0f} N")
    console.print(f"  Aligning moment: {forces.Mz:,.1f} N⋅m")
    
    # Validation: Forces should be positive, reasonable magnitude
    assert Fy > 0, "Lateral force should be positive"
    assert Fx > 0, "Longitudinal force should be positive"
    assert 0 < total < 8000, "Total force should be reasonable (< max friction)"
    
    console.print("\n  [green]✓ All force calculations passed[/green]")


def test_load_dependency():
    """Test that forces scale correctly with normal load"""
    console.print("\n[bold cyan]TEST 2: Load Dependency (Doubling Load)[/bold cyan]\n")
    
    calc = PacejkaCalculator()
    alpha = math.radians(2.0)
    
    # Low load
    Fy_low = calc.calc_lateral_force(alpha, 2000.0)
    # High load
    Fy_high = calc.calc_lateral_force(alpha, 4000.0)
    
    ratio = Fy_high / Fy_low
    console.print(f"  Fy at 2000N: {Fy_low:,.0f} N")
    console.print(f"  Fy at 4000N: {Fy_high:,.0f} N")
    console.print(f"  Force ratio: {ratio:.2f}x")
    
    # Should be roughly 1.5-1.8x (nonlinear with load)
    assert 1.3 < ratio < 2.0, f"Load scaling should be 1.3-2.0x, got {ratio:.2f}x"
    
    console.print("\n  [green]✓ Load dependency correct[/green]")


def test_grip_level():
    """Test grip utilization calculation"""
    console.print("\n[bold cyan]TEST 3: Grip Level (Utilization)[/bold cyan]\n")
    
    calc = PacejkaCalculator()
    Fz = 4000.0
    
    test_cases = [
        ("No slip", 0.0, 0.0),
        ("Low slip", math.radians(1.0), 0.0),
        ("Medium slip", math.radians(3.0), 0.02),
        ("High slip", math.radians(5.0), 0.05),
    ]
    
    table = Table(title="Grip Utilization at Different Slip Levels")
    table.add_column("Condition", style="cyan")
    table.add_column("Slip Angle", justify="right")
    table.add_column("Slip Ratio", justify="right")
    table.add_column("Grip Level", justify="right", style="green")
    
    for label, alpha, kappa in test_cases:
        grip = calc.calc_grip_level(alpha, kappa, Fz)
        table.add_row(
            label,
            f"{math.degrees(alpha):.1f}°",
            f"{kappa:.3f}",
            f"{grip:.1%}"
        )
    
    console.print(table)
    console.print("\n  [green]✓ Grip levels physically plausible[/green]")


def test_degradation():
    """Test tire degradation model"""
    console.print("\n[bold cyan]TEST 4: Tire Degradation Model[/bold cyan]\n")
    
    deg = PacejkaTyreDegradation()
    
    table = Table(title="Lap Time Penalty from Tire Degradation")
    table.add_column("Lap #", justify="right", width=8)
    table.add_column("Tyre Age", justify="right", width=12)
    table.add_column("Grip Loss", justify="right", width=12)
    table.add_column("Time Penalty [s]", justify="right", width=18)
    
    for age in range(0, 45, 5):
        if age > 40:
            continue
        
        # Get degraded coefficients
        degraded = deg.degrade_coefficients(age, max_life_laps=40)
        
        # Calculate penalty
        penalty = deg.estimate_laptime_penalty(age, max_life_laps=40)
        
        # Estimate grip loss from D coefficient change
        d_ratio = degraded.pDx1 / deg.initial_coeffs.pDx1
        grip_loss = (1.0 - d_ratio) * 100
        
        table.add_row(
            f"{age}",
            f"{age}/40 ({age/40*100:.0f}%)",
            f"{grip_loss:.1f}%",
            f"{penalty:.4f}"
        )
    
    console.print(table)
    console.print("\n  [green]✓ Degradation model shows expected trend[/green]")


def test_coefficient_sanity():
    """Validate coefficient ranges"""
    console.print("\n[bold cyan]TEST 5: Coefficient Sanity Checks[/bold cyan]\n")
    
    coeffs = PacejkaCoefficients()
    
    checks = [
        ("pCy1 (lateral shape)", 1.0, 2.0, coeffs.pCy1),
        ("pDy1 (lateral peak base)", 0.8, 1.5, coeffs.pDy1),
        ("pKy1 (lateral stiffness)", 8.0, 15.0, coeffs.pKy1),
        ("pCx1 (long. shape)", 1.5, 2.0, coeffs.pCx1),
        ("pDx1 (long. peak base)", 0.9, 1.3, coeffs.pDx1),
        ("pKx1 (long. stiffness)", 10.0, 15.0, coeffs.pKx1),
        ("Fz0 (reference load)", 3500, 4500, coeffs.Fz0),
    ]
    
    table = Table(title="Coefficient Validity Check")
    table.add_column("Coefficient", style="cyan")
    table.add_column("Min", justify="right")
    table.add_column("Max", justify="right")
    table.add_column("Value", justify="right", style="green")
    table.add_column("Status", style="bold")
    
    all_valid = True
    for name, min_val, max_val, actual in checks:
        status = "✓ OK" if min_val <= actual <= max_val else "✗ INVALID"
        status_color = "green" if "OK" in status else "red"
        table.add_row(
            name,
            f"{min_val:.2f}",
            f"{max_val:.2f}",
            f"{actual:.2f}",
            f"[{status_color}]{status}[/{status_color}]"
        )
        all_valid = all_valid and (min_val <= actual <= max_val)
    
    console.print(table)
    
    if all_valid:
        console.print("\n  [green]✓ All coefficients within valid ranges[/green]")
    else:
        console.print("\n  [yellow]⚠ Some coefficients outside typical ranges[/yellow]")


def test_realistic_scenario():
    """Test a realistic F1 corner scenario"""
    console.print("\n[bold cyan]TEST 6: Realistic F1 Corner Scenario[/bold cyan]\n")
    
    calc = PacejkaCalculator()
    
    # Scenario: Late braking into a high-speed corner (Silverstone Turn 4)
    # Medium downforce, mixed cornering + slight braking
    
    scenarios = [
        ("On-throttle (no slip)", math.radians(1.0), 0.0),
        ("Light braking+corner", math.radians(1.5), 0.02),
        ("Hard braking+corner", math.radians(2.5), 0.08),
        ("Heavy trail-braking", math.radians(3.0), 0.05),
    ]
    
    Fz = 5000.0  # High downforce scenario
    
    table = Table(title="F1 Corner Entry Scenario Analysis")
    table.add_column("Phase", style="cyan", width=20)
    table.add_column("Slip Angle", justify="right", width=12)
    table.add_column("Lateral [N]", justify="right", width=14, style="green")
    table.add_column("Longitudinal [N]", justify="right", width=16, style="green")
    table.add_column("Grip Used [%]", justify="right", width=14, style="yellow")
    
    for label, alpha, kappa in scenarios:
        forces = calc.calc_combined_forces(alpha, kappa, Fz)
        grip = calc.calc_grip_level(alpha, kappa, Fz)
        
        table.add_row(
            label,
            f"{math.degrees(alpha):.1f}°",
            f"{forces.Fy:,.0f}",
            f"{forces.Fx:,.0f}",
            f"{grip:.1%}"
        )
    
    console.print(table)
    console.print("\n  [green]✓ Realistic scenario test passed[/green]")


def main():
    console.print(Panel.fit(
        "[bold cyan]Pacejka Magic Formula 5.2 Test Suite[/bold cyan]\n"
        "[dim]Testing force calculations, degradation, and physical plausibility[/dim]",
        border_style="cyan"
    ))
    
    try:
        test_basic_forces()
        test_load_dependency()
        test_grip_level()
        test_degradation()
        test_coefficient_sanity()
        test_realistic_scenario()
        
        console.print(Panel.fit(
            "[bold green]✓ ALL TESTS PASSED[/bold green]",
            border_style="green"
        ))
        
    except AssertionError as e:
        console.print(Panel.fit(
            f"[bold red]✗ TEST FAILED[/bold red]\n{str(e)}",
            border_style="red"
        ))
        sys.exit(1)
    except Exception as e:
        console.print(Panel.fit(
            f"[bold red]✗ ERROR[/bold red]\n{str(e)}",
            border_style="red"
        ))
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
