import networkx as nx
import logging
import requests
import json
from jinja2 import Template
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

console = Console()

class WorkflowEngine:
    def __init__(self, data):
        self.nodes = data.get('nodes', [])
        self.dag = nx.DiGraph()
        self.results = {}

    def build_graph(self):
        for node in self.nodes:
            self.dag.add_node(node['id'], **node)
            for req in node.get('requires', []):
                self.dag.add_edge(req, node['id'])

    def visualize_workflow(self):
        """Visualizes the workflow structure similar to an n8n canvas."""
        console.print(Panel("[bold magenta]Termiflow Visualizer[/bold magenta]", expand=False))
        
        # Create a Tree to show dependencies
        workflow_tree = Tree("[bold green]Workflow Start[/bold green]")
        
        # We find 'root' nodes (nodes with no dependencies) to start the tree
        roots = [n for n, d in self.dag.in_degree() if d == 0]
        
        for root in roots:
            node_branch = workflow_tree.add(f"[cyan]{root}[/cyan] ({self.dag.nodes[root].get('type', 'shell')})")
            # Add children
            for child in self.dag.successors(root):
                node_branch.add(f"[yellow]➔ {child}[/yellow]")
        
        console.print(workflow_tree)
        console.print("\n")

    def run(self, verbose=False):
        try:
            self.visualize_workflow()
            order = list(nx.topological_sort(self.dag))
            
            # Create a status table for execution
            table = Table(title="Execution Status")
            table.add_column("Node ID", style="cyan")
            table.add_column("Type", style="magenta")
            table.add_column("Status", style="green")

            for node_id in order:
                node_data = self.dag.nodes[node_id]
                self._execute_node(node_id, node_data)
                table.add_row(node_id, node_data.get('type', 'shell'), "Success")
            
            console.print(table)
            self._export_results()
            
        except Exception as e:
            console.print(f"[bold red]Failure:[/bold red] {e}")

    def _execute_node(self, node_id, node_data):
        node_type = node_data.get('type', 'shell')
        template_str = node_data.get('url') if node_type == 'http' else node_data.get('command')
        
        # Variable Injection
        final_val = Template(template_str).render(results=self.results)

        if node_type == 'http':
            response = requests.request(node_data.get('method', 'GET'), final_val)
            self.results[node_id] = response.json() if 'application/json' in response.headers.get('Content-Type', '') else {"text": response.text}
        else:
            # shell simulation
            self.results[node_id] = {"status": "executed", "val": final_val}

    def _export_results(self):
        with open("workflow_output.json", "w") as f:
            json.dump(self.results, f, indent=4)