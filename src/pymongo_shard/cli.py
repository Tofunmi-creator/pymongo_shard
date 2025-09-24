"""Console script for pymongo_shard."""

import typer
from rich.console import Console

from pymongo_shard import utils

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for pymongo_shard."""
    console.print("Replace this message by putting your code into "
               "pymongo_shard.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()
