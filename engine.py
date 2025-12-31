import networkx as nx
import logging
from jinja2 import Template

# Setup logging for Error Handling
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class WorkflowEngine:
    def __init__(self, data):
        self.nodes = data.get('nodes', [])
        self.dag = nx.DiGraph()
        self.results = {}  # Store results for variable injection

    def build_graph(self):
        """Step 1: Dependency Mapping using NetworkX"""
        for node in self.nodes:
            # Add node and store its metadata
            self.dag.add_node(node['id'], **node)
            # Add edges for dependencies
            for req in node.get('requires', []):
                self.dag.add_edge(req, node['id'])

    def run(self, verbose=False):
        """Step 2: Error Handling and Execution"""
        if not verbose:
            logging.getLogger().setLevel(logging.WARNING)

        try:
            # Get execution order (Topological Sort)
            order = list(nx.topological_sort(self.dag))
            
            for node_id in order:
                node_data = self.dag.nodes[node_id]
                self._execute_node(node_id, node_data)
                
            logging.info("✅ Workflow completed successfully.")
            
        except nx.NetworkXUnfeasible:
            logging.error("❌ Circular dependency detected! Check your JSON.")
        except Exception as e:
            logging.error(f"❌ Workflow failed at node {node_id}: {e}")

    def _execute_node(self, node_id, node_data):
        """Step 3: Variable Injection & Command Simulation"""
        command_raw = node_data.get('command', '')
        
        # Inject variables using Jinja2
        template = Template(command_raw)
        final_command = template.render(results=self.results)
        
        print(f"[Running {node_id}]: {final_command}")
        
        # Simulate an output for the next node to use
        # In a real app, you'd use subprocess.run(final_command)
        self.results[node_id] = {"output": f"Data_from_{node_id}"}