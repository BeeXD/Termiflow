
# Termiflow

Termiflow is a lightweight, graph-based CLI workflow orchestrator designed to automate complex tasks with a focus on visual clarity and dependency management. Inspired by enterprise tools like n8n, Termiflow brings a visual "canvas" experience directly to your terminal.


## Key Features

- **Dependency Mapping (DAGs**): Unlike linear task runners, Termiflow uses a Directed Acyclic Graph (DAG) via NetworkX. This ensures that tasks only execute once their specific requirements are met (e.g., Node C waits for both Node A and Node B).

- **Rich Visuals**: Leveraging the Rich library, Termiflow provides a beautiful, color-coded visualization of your workflow tree and a real-time execution status table.

- **Variable Injection**: Support for dynamic data flow using Jinja2 templates. You can inject outputs from a previous HTTP request directly into a subsequent Shell command using {{ results.node_id.key }}.

- **Protocol Diversity**: Native support for both local Shell commands and external HTTP requests (GET/POST).

- **State Persistence**: Every run automatically exports its full execution state to workflow_output.json, allowing for post-execution analysis and debugging.

## Project Structure
```
termiflow/
├── main.py              # CLI Entry point 
├── engine.py            # Core Logic (NetworkX & Jinja2)
├── workflow.json        # Sample workflow configuration
├── workflow_output.json # Generated state after execution
└── requirements.txt     # Project dependencies
```
## Installation

Clone the branch

```bash
git clone -b visualise https://github.com/BeeXD/Termiflow.git
cd sem-proj
```
Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage
**Run a Workflow** 
```bash
python main.py run workflow.json
```

Inspect Node Data
```bash
python main.py inspect [Node_id]
```
## Example Workflow `workflow.json`

```json
{
  "nodes": [
    {
      "id": "Get_Weather",
      "type": "http",
      "method": "GET",
      "url": "https://api.open-meteo.com/v1/forecast?latitude=12.97&longitude=77.59&current_weather=true"
    },
    {
      "id": "Log_Weather",
      "requires": ["Get_Weather"],
      "type": "shell",
      "command": "echo 'The temp in Bengaluru is {{ results.Get_Weather.current_weather.temperature }}°C'"
    }
  ]
}
```


## Screenshots

![App Screenshot](https://i.ibb.co/BVb4Wjbc/Screenshot-2025-12-31-113506.png)

![Workflow output](https://i.ibb.co/1GT7bb2h/Screenshot-2025-12-31-113752.png)


## Built With

- [NetworkX](https://networkx.org/) - For graph-based dependency sorting.

- [Typer](https://typer.tiangolo.com/) - For a robust CLI experience.

- [Rich](https://github.com/Textualize/rich) - For terminal-based visualizations.

- [Jinja2](https://jinja.palletsprojects.com/) - For dynamic variable injection.

- [Requests](https://requests.readthedocs.io/) - For HTTP task execution.

