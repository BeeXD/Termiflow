import typer
import json
from engine import WorkflowEngine

app = typer.Typer()

@app.command()
def start(file: str):
    with open(file, 'r') as f:
        data = json.load(f)
    
    engine = WorkflowEngine(data)
    engine.build_graph()
    engine.run()

if __name__ == "__main__":
    app()