from rich.console import Console
from rich.table import Table

def print_table(list, title):
    table = Table(title=title)
    keys = list[0].keys()
    for key in keys:
        table.add_column(key, justify="center", style="cyan")
    for each in list:
        table.add_row(*each.values())
    console = Console()
    console.print(table)