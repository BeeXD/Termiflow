import networkx as nx
import logging
import requests
import json
from jinja2 import Template

# Standard logging configuration for error handling
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class WorkflowEngine:
    def __init__(self, data):
        self.nodes = data.get('nodes', [])
        self.dag = nx.DiGraph()
        self.results = {}  # Acts as the "memory" for Variable Injection

    def build_graph(self):
        """Builds a Directed Acyclic Graph (DAG) for dependency mapping."""
        for node in self.nodes:
            self.dag.add_node(node['id'], **node)
            for req in node.get('requires', []):
                self.dag.add_edge(req, node['id'])

    def run(self, verbose=False):
        """Executes the graph using topological sort for correct ordering."""
        if not verbose:
            logging.getLogger().setLevel(logging.WARNING)
        
        try:
            order = list(nx.topological_sort(self.dag))
            for node_id in order:
                node_data = self.dag.nodes[node_id]
                self._execute_node(node_id, node_data)
            
            # Post-Execution Hook: Export final results
            self._export_results()
            logging.info("✅ Workflow completed and results exported.")
            
        except nx.NetworkXUnfeasible:
            logging.error("❌ Error: Circular dependency detected in workflow!")
        except Exception as e:
            logging.error(f"❌ Critical Failure at node {node_id}: {e}")

    def _execute_node(self, node_id, node_data):
        """Checks the node type and routes to the correct handler."""
        node_type = node_data.get('type', 'shell') 
        
        if node_type == 'http':
            self._handle_http_node(node_id, node_data)
        else:
            self._handle_shell_node(node_id, node_data)

    def _handle_http_node(self, node_id, node_data):
        """Performs dynamic HTTP requests based on user input."""
        url_template = Template(node_data.get('url', ''))
        url = url_template.render(results=self.results)
        method = node_data.get('method', 'GET').upper()
        
        logging.info(f"🌐 [HTTP {method}] Executing {node_id}...")
        
        response = requests.request(method, url)
        response.raise_for_status() # Basic error handling for bad HTTP codes
        
        try:
            self.results[node_id] = response.json()
        except:
            self.results[node_id] = {"text": response.text}

    def _handle_shell_node(self, node_id, node_data):
        """Handles standard terminal commands with variable injection."""
        command_template = Template(node_data.get('command', ''))
        final_command = command_template.render(results=self.results)
        
        print(f"💻 [Shell] {node_id}: {final_command}")
        # In a production environment, use subprocess.run(final_command, shell=True)
        self.results[node_id] = {"status": "success", "command_ran": final_command}

    def _export_results(self):
        """Saves the final state of all nodes to a file."""
        with open("workflow_output.json", "w") as f:
            json.dump(self.results, f, indent=4)