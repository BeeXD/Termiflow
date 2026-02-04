// Termiflow Visual Workflow Editor - Vanilla JavaScript
(function() {
    'use strict';
    
    // State
    let nodes = [];
    let connections = [];
    let selectedNode = null;
    let draggingNode = null;
    let offset = { x: 0, y: 0 };
    let isPanning = false;
    let panStart = { x: 0, y: 0 };
    let viewOffset = { x: 0, y: 0 };
    let zoom = 1;
    let connectingFrom = null;
    
    let canvas, nodesGroup, connectionsGroup;
    
    // Load workflow from server
    async function loadWorkflow() {
        try {
            const response = await fetch('/api/workflow');
            const data = await response.json();
            
            nodes = [];
            connections = [];
            
            // Convert workflow nodes to visual format
            data.nodes.forEach((node, index) => {
                nodes.push({
                    id: node.id,
                    type: node.type,
                    x: 150 + (index * 250),
                    y: 150 + (index % 3) * 150,
                    data: node
                });
            });
            
            // Create connections from requires
            data.nodes.forEach(node => {
                if (node.requires) {
                    node.requires.forEach(req => {
                        connections.push({
                            from: req,
                            to: node.id
                        });
                    });
                }
            });
            
            render();
            showNotification('Workflow loaded successfully!', 'success');
        } catch (error) {
            showNotification('Error loading workflow: ' + error.message, 'error');
        }
    }
    
    // Save workflow to server
    async function saveWorkflow() {
        try {
            const workflowNodes = nodes.map(node => {
                const requires = connections
                    .filter(conn => conn.to === node.id)
                    .map(conn => conn.from);
                
                const result = {
                    id: node.data.id,
                    type: node.data.type
                };
                
                if (requires.length > 0) {
                    result.requires = requires;
                }
                
                if (node.data.type === 'http') {
                    result.method = node.data.method || 'GET';
                    result.url = node.data.url || '';
                } else if (node.data.type === 'shell') {
                    result.command = node.data.command || '';
                }
                
                return result;
            });
            
            const workflow = { nodes: workflowNodes };
            
            const response = await fetch('/api/workflow', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(workflow)
            });
            
            const result = await response.json();
            showNotification(result.message, result.status);
        } catch (error) {
            showNotification('Error saving workflow: ' + error.message, 'error');
        }
    }
    
    // Run workflow
    async function runWorkflow() {
        try {
            await saveWorkflow();
            
            const response = await fetch('/api/workflow/run', {
                method: 'POST'
            });
            
            const result = await response.json();
            showNotification(result.message, result.status);
        } catch (error) {
            showNotification('Error running workflow: ' + error.message, 'error');
        }
    }
    
    // Show results
    async function showResults() {
        try {
            const response = await fetch('/api/workflow/results');
            const results = await response.json();
            
            const modal = document.getElementById('modal');
            const modalBody = document.getElementById('modalBody');
            modalBody.textContent = JSON.stringify(results, null, 2);
            modal.style.display = 'block';
        } catch (error) {
            showNotification('Error fetching results: ' + error.message, 'error');
        }
    }
    
    // Render the workflow
    function render() {
        if (!nodesGroup || !connectionsGroup) {
            console.error('Canvas elements not initialized yet');
            return;
        }
        
        // Clear
        nodesGroup.innerHTML = '';
        connectionsGroup.innerHTML = '';
        
        // Draw connections
        connections.forEach(conn => {
            const fromNode = nodes.find(n => n.id === conn.from);
            const toNode = nodes.find(n => n.id === conn.to);
            
            if (fromNode && toNode) {
                drawConnection(fromNode, toNode);
            }
        });
        
        // Draw nodes
        nodes.forEach(node => {
            drawNode(node);
        });
    }
    
    // Draw a node
    function drawNode(node) {
        const icon = node.type === 'http' ? '🌐' : '💻';
        const isSelected = selectedNode && selectedNode.id === node.id;
        
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.setAttribute('class', 'node');
        g.setAttribute('data-id', node.id);
        g.setAttribute('transform', `translate(${node.x}, ${node.y})`);
        
        // Node background
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('width', '180');
        rect.setAttribute('height', '80');
        rect.setAttribute('rx', '8');
        rect.setAttribute('fill', '#0f4c75');
        rect.setAttribute('stroke', isSelected ? '#667eea' : '#1a5c8a');
        rect.setAttribute('stroke-width', '2');
        g.appendChild(rect);
        
        // Icon
        const iconText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        iconText.setAttribute('x', '15');
        iconText.setAttribute('y', '35');
        iconText.setAttribute('font-size', '24');
        iconText.textContent = icon;
        g.appendChild(iconText);
        
        // Title
        const title = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        title.setAttribute('x', '50');
        title.setAttribute('y', '35');
        title.setAttribute('fill', '#eee');
        title.setAttribute('font-weight', '600');
        title.setAttribute('font-size', '14');
        title.textContent = node.id;
        g.appendChild(title);
        
        // Type
        const type = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        type.setAttribute('x', '50');
        type.setAttribute('y', '50');
        type.setAttribute('fill', '#888');
        type.setAttribute('font-size', '10');
        type.textContent = node.type.toUpperCase();
        g.appendChild(type);
        
        // Input handle (top)
        const inputHandle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        inputHandle.setAttribute('cx', '90');
        inputHandle.setAttribute('cy', '0');
        inputHandle.setAttribute('r', '6');
        inputHandle.setAttribute('fill', '#667eea');
        inputHandle.setAttribute('stroke', '#16213e');
        inputHandle.setAttribute('stroke-width', '2');
        inputHandle.setAttribute('class', 'handle-input');
        g.appendChild(inputHandle);
        
        // Output handle (bottom)
        const outputHandle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        outputHandle.setAttribute('cx', '90');
        outputHandle.setAttribute('cy', '80');
        outputHandle.setAttribute('r', '6');
        outputHandle.setAttribute('fill', '#667eea');
        outputHandle.setAttribute('stroke', '#16213e');
        outputHandle.setAttribute('stroke-width', '2');
        outputHandle.setAttribute('class', 'handle-output');
        g.appendChild(outputHandle);
        
        // Event listeners
        rect.style.cursor = 'move';
        rect.addEventListener('mousedown', (e) => startDrag(e, node));
        rect.addEventListener('click', () => selectNode(node));
        
        outputHandle.style.cursor = 'crosshair';
        outputHandle.addEventListener('mousedown', (e) => {
            e.stopPropagation();
            startConnection(node);
        });
        
        inputHandle.style.cursor = 'crosshair';
        inputHandle.addEventListener('mouseup', (e) => {
            e.stopPropagation();
            endConnection(node);
        });
        
        nodesGroup.appendChild(g);
    }
    
    // Draw connection between nodes
    function drawConnection(fromNode, toNode) {
        const x1 = fromNode.x + 90;
        const y1 = fromNode.y + 80;
        const x2 = toNode.x + 90;
        const y2 = toNode.y;
        
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        const d = `M ${x1} ${y1} C ${x1} ${y1 + 50}, ${x2} ${y2 - 50}, ${x2} ${y2}`;
        path.setAttribute('d', d);
        path.setAttribute('stroke', '#667eea');
        path.setAttribute('stroke-width', '2');
        path.setAttribute('fill', 'none');
        path.setAttribute('marker-end', 'url(#arrowhead)');
        
        connectionsGroup.appendChild(path);
    }
    
    // Start dragging a node
    function startDrag(e, node) {
        draggingNode = node;
        const rect = canvas.getBoundingClientRect();
        offset.x = e.clientX - rect.left - node.x;
        offset.y = e.clientY - rect.top - node.y;
    }
    
    // Select a node
    function selectNode(node) {
        selectedNode = node;
        updatePropertiesPanel(node);
        render();
    }
    
    // Start creating a connection
    function startConnection(node) {
        connectingFrom = node;
    }
    
    // End creating a connection
    function endConnection(node) {
        if (connectingFrom && connectingFrom.id !== node.id) {
            // Check if connection already exists
            const exists = connections.some(c => 
                c.from === connectingFrom.id && c.to === node.id
            );
            
            if (!exists) {
                connections.push({
                    from: connectingFrom.id,
                    to: node.id
                });
                render();
                showNotification('Connection created! Remember to save.', 'success');
            }
        }
        connectingFrom = null;
    }
    
    // Add a new node
    function addNode(type, x, y) {
        const nodeId = `${type}_${Date.now()}`;
        const newNode = {
            id: nodeId,
            type: type,
            x: x,
            y: y,
            data: {
                id: nodeId,
                type: type
            }
        };
        
        if (type === 'http') {
            newNode.data.method = 'GET';
            newNode.data.url = '';
        } else if (type === 'shell') {
            newNode.data.command = '';
        }
        
        nodes.push(newNode);
        render();
        showNotification('Node added! Click to edit properties.', 'success');
    }
    
    // Delete a node
    function deleteNode(node) {
        nodes = nodes.filter(n => n.id !== node.id);
        connections = connections.filter(c => c.from !== node.id && c.to !== node.id);
        selectedNode = null;
        document.getElementById('propertiesContent').innerHTML = 
            '<p class="placeholder">Select a node to edit its properties</p>';
        render();
    }
    
    // Update properties panel
    function updatePropertiesPanel(node) {
        const panel = document.getElementById('propertiesContent');
        const nodeData = node.data;
        
        let html = `
            <div class="form-group">
                <label>Node ID</label>
                <input type="text" id="prop-id" value="${nodeData.id}" />
            </div>
            <div class="form-group">
                <label>Type</label>
                <input type="text" value="${nodeData.type}" disabled />
            </div>
        `;
        
        if (nodeData.type === 'http') {
            html += `
                <div class="form-group">
                    <label>Method</label>
                    <select id="prop-method">
                        <option value="GET" ${nodeData.method === 'GET' ? 'selected' : ''}>GET</option>
                        <option value="POST" ${nodeData.method === 'POST' ? 'selected' : ''}>POST</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>URL</label>
                    <textarea id="prop-url">${nodeData.url || ''}</textarea>
                </div>
            `;
        } else if (nodeData.type === 'shell') {
            html += `
                <div class="form-group">
                    <label>Command</label>
                    <textarea id="prop-command">${nodeData.command || ''}</textarea>
                </div>
            `;
        }
        
        html += `
            <button class="btn btn-primary" id="updateNodeBtn" style="width: 100%; margin-top: 1rem;">Update Node</button>
            <button class="delete-node-btn" id="deleteNodeBtn">Delete Node</button>
        `;
        
        panel.innerHTML = html;
        
        document.getElementById('updateNodeBtn').addEventListener('click', () => {
            const newId = document.getElementById('prop-id').value;
            nodeData.id = newId;
            node.id = newId;
            
            if (nodeData.type === 'http') {
                nodeData.method = document.getElementById('prop-method').value;
                nodeData.url = document.getElementById('prop-url').value;
            } else if (nodeData.type === 'shell') {
                nodeData.command = document.getElementById('prop-command').value;
            }
            
            render();
            showNotification('Node updated! Remember to save.', 'success');
        });
        
        document.getElementById('deleteNodeBtn').addEventListener('click', () => {
            if (confirm(`Delete node "${nodeData.id}"?`)) {
                deleteNode(node);
                showNotification('Node deleted! Remember to save.', 'success');
            }
        });
    }
    
    // Show notification
    function showNotification(message, type) {
        const color = type === 'success' ? '#48bb78' : type === 'error' ? '#e53e3e' : '#4299e1';
        
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${color};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    // Initialize
    document.addEventListener('DOMContentLoaded', () => {
        // Initialize canvas elements FIRST
        canvas = document.getElementById('canvas');
        nodesGroup = document.getElementById('nodes');
        connectionsGroup = document.getElementById('connections');
        
        // Toolbar buttons
        document.getElementById('loadBtn').addEventListener('click', loadWorkflow);
        document.getElementById('saveBtn').addEventListener('click', saveWorkflow);
        document.getElementById('runBtn').addEventListener('click', runWorkflow);
        document.getElementById('resultsBtn').addEventListener('click', showResults);
        
        // Modal
        const modal = document.getElementById('modal');
        const closeBtn = document.querySelector('.close');
        closeBtn.onclick = () => modal.style.display = 'none';
        window.onclick = (e) => {
            if (e.target === modal) modal.style.display = 'none';
        };
        
        // Mouse events for dragging
        document.addEventListener('mousemove', (e) => {
            if (draggingNode) {
                const rect = canvas.getBoundingClientRect();
                draggingNode.x = e.clientX - rect.left - offset.x;
                draggingNode.y = e.clientY - rect.top - offset.y;
                render();
            }
        });
        
        document.addEventListener('mouseup', () => {
            draggingNode = null;
        });
        
        // Palette drag and drop
        const paletteNodes = document.querySelectorAll('.palette-node');
        paletteNodes.forEach(paletteNode => {
            paletteNode.addEventListener('click', () => {
                const type = paletteNode.getAttribute('data-type');
                addNode(type, 100 + Math.random() * 200, 100 + Math.random() * 200);
            });
        });
        
        // Load workflow AFTER everything is initialized
        loadWorkflow();
    });
    
    // Add animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(400px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(400px); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
})();
