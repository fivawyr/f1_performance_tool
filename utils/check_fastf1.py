# small python script - helper function for checking fastf1 data. We can clarify the output by 
# taking a small prove of the dataset 

import fastf1
from rich.console import Console
from rich.table import Table
from rich import inspect
from rich.pretty import pprint
import os 

console = Console()

os.makedirs("cache", exist_ok=True) 
fastf1.Cache.enable_cache("cache/") 

with console.status("[cyan]Loading session...", spinner="dots"):
    session = fastf1.get_session(2018, "Monaco", "Q")
    session.load()

console.print("[green]Session loaded![/green]\n")

console.print("[bold #1C69D4]── Event Info ──[/bold #1C69D4]")
pprint(dict(session.event))

console.print("\n[bold #1C69D4]── Drivers ──[/bold #1C69D4]")
pprint(session.drivers)

console.print("\n[bold #1C69D4]── Raw Laps (first 10) ──[/bold #1C69D4]")
pprint(session.laps.head(10).to_dict(orient="records"))

console.print("\n[bold #1C69D4]── Fastest Lap per Driver ──[/bold #1C69D4]")
fastest = session.laps.groupby("Driver")["LapTime"].min().sort_values().reset_index()

table = Table(header_style="bold #1C69D4", border_style="dim")
table.add_column("Pos", width=4, justify="right")
table.add_column("Driver", width=8)
table.add_column("Fastest Lap", width=15, justify="right", style="green")

for i, (_, row) in enumerate(fastest.iterrows(), start=1):
    table.add_row(str(i), row["Driver"], str(row["LapTime"]))

console.print(table)

console.print("\n[bold #1C69D4]── Available Columns in session.laps ──[/bold #1C69D4]")
pprint(list(session.laps.columns))
