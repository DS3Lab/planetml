import sys
import typer
from art import text2art
from typing import Optional
from rich.pretty import pprint
sys.path.append(".")
from cli.pkg.planetd import PlanetML

__version__ = "0.0.1"
app = typer.Typer()
planetml = PlanetML()

def version_callback(value: bool):
    if value:
        toma_computer_art = text2art("TOGETHER COMPUTER")
        print(toma_computer_art)
        typer.echo(f"Version: {__version__}")

        raise typer.Exit()

@app.command()
def main(
        version: Optional[bool] = typer.Option(
            None, "--version", 
            callback=version_callback,
            help="Display version information"
        ),

    ):
    print(f"Hello")

@app.command()
def stats():
    pprint(planetml.get_site_status())

if __name__ == "__main__":
    app()

