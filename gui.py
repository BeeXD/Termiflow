"""
Termiflow GUI - A web-based interface for visual workflow creation.
Similar to n8n, this provides a node-based canvas for building workflows.
"""
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
from engine import WorkflowEngine
import threading

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

WORKFLOW_FILE = 'workflow.json'

@app.route('/')
def index():
    """Serve the main GUI page."""
    return render_template('index.html')

@app.route('/api/workflow', methods=['GET'])
def get_workflow():
    """Get the current workflow configuration."""
    if os.path.exists(WORKFLOW_FILE):
        with open(WORKFLOW_FILE, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    return jsonify({"nodes": []})

@app.route('/api/workflow', methods=['POST'])
def save_workflow():
    """Save the workflow configuration."""
    data = request.json
    with open(WORKFLOW_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    return jsonify({"status": "success", "message": "Workflow saved successfully"})

@app.route('/api/workflow/run', methods=['POST'])
def run_workflow():
    """Execute the current workflow."""
    try:
        if not os.path.exists(WORKFLOW_FILE):
            return jsonify({"status": "error", "message": "No workflow file found"}), 404
        
        with open(WORKFLOW_FILE, 'r') as f:
            data = json.load(f)
        
        # Run workflow in background to avoid blocking
        def execute():
            engine = WorkflowEngine(data)
            engine.build_graph()
            engine.run(verbose=False)
        
        thread = threading.Thread(target=execute)
        thread.start()
        
        return jsonify({"status": "success", "message": "Workflow execution started"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/workflow/results', methods=['GET'])
def get_results():
    """Get the results from the last workflow execution."""
    output_file = 'workflow_output.json'
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            results = json.load(f)
        return jsonify(results)
    return jsonify({})

@app.route('/api/nodes/types', methods=['GET'])
def get_node_types():
    """Get available node types."""
    return jsonify({
        "types": [
            {
                "id": "http",
                "name": "HTTP Request",
                "description": "Make HTTP GET/POST requests",
                "fields": ["method", "url"]
            },
            {
                "id": "shell",
                "name": "Shell Command",
                "description": "Execute shell commands",
                "fields": ["command"]
            }
        ]
    })

def main():
    """Start the GUI server."""
    import os
    print("🚀 Starting Termiflow GUI Server...")
    print("📊 Open http://localhost:5000 in your browser")
    
    # Use environment variable for host, default to localhost for security
    host = os.environ.get('TERMIFLOW_HOST', '127.0.0.1')
    port = int(os.environ.get('TERMIFLOW_PORT', '5000'))
    
    app.run(debug=False, host=host, port=port, use_reloader=False)

if __name__ == '__main__':
    main()
