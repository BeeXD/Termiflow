import typer
import json
import os
from engine import WorkflowEngine
from rich.console import Console
from rich.panel import Panel
from rich.pretty import pprint

# Initialize Console and Typer
console = Console()
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

# --- ADD THIS NEW FUNCTION BELOW ---

@app.command()
def inspect(node_id: str):
    """
    Inspect the output of a specific node from the last run stored in workflow_output.json.
    """
    output_file = "workflow_output.json"
    
    if not os.path.exists(output_file):
        console.print("[bold red]Error:[/bold red] No output file found. Run 'python main.py run <file>' first.")
        return

    with open(output_file, "r") as f:
        results = json.load(f)

    if node_id in results:
        console.print(Panel(f" [bold cyan]Data for Node: {node_id}[/bold cyan]", expand=False))
        pprint(results[node_id])
    else:
        # Suggest available nodes if the user types a wrong ID
        available_nodes = ", ".join(results.keys())
        console.print(f"[bold yellow]Node '{node_id}' not found.[/bold yellow]")
        console.print(f"Available nodes from last run: [green]{available_nodes}[/green]")

if __name__ == "__main__":
    app()