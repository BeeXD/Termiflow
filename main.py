import json
from nodes import execute_http_request, execute_terminal_log
import networkx as nx
import typer
import logging
from jinja2 import Template
import json

# Initialize Typer and Logging
app = typer.Typer()
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def run_workflow(file_path):
    with open(file_path, 'r') as f:
        workflow = json.load(f)

    print(f"--- Starting Workflow: {workflow['name']} ---")
    
    last_output = None

    for node in workflow['nodes']:
        if node['type'] == "httpRequest":
            last_output = execute_http_request(node['params'])
        
        elif node['type'] == "terminalLog":
            last_output = execute_terminal_log(node['params'], last_output)

    print("--- Workflow Finished Successfully ---")

if __name__ == "__main__":
    run_workflow('workflow.json')