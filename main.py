import typer
import json
import os
from engine import WorkflowEngine

app = typer.Typer(help="Termiflow: A Graph-Based Task Runner")

@app.command()
def run(
    file: str = typer.Argument(..., help="Path to the workflow JSON file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable detailed logging")
):
    """
    Step 4: CLI Interface to run workflows.
    """
    if not os.path.exists(file):
        typer.echo(f"Error: File {file} not found.", err=True)
        raise typer.Exit(code=1)

    with open(file, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            typer.echo("Error: Invalid JSON format.", err=True)
            raise typer.Exit(code=1)

    engine = WorkflowEngine(data)
    engine.build_graph()
    engine.run(verbose=verbose)

if __name__ == "__main__":
    app()