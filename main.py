import typer
import json
import os
from engine import WorkflowEngine

app = typer.Typer(help="Termiflow: Advanced Graph-Based Task Runner")

@app.command()
def run(
    file: str = typer.Argument(..., help="The workflow.json file to execute"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed logs")
):
    """Run a Termiflow project file with dependency mapping."""
    if not os.path.exists(file):
        typer.echo(f"Error: {file} not found.", err=True)
        raise typer.Exit(code=1)

    with open(file, 'r') as f:
        data = json.load(f)

    engine = WorkflowEngine(data)
    engine.build_graph()
    engine.run(verbose=verbose)

if __name__ == "__main__":
    app()