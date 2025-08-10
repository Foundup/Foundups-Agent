"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AgentDashboard = void 0;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
class AgentDashboard {
    constructor(context) {
        this.phases = [];
        this.fileChanges = [];
        this.activeAgents = new Map();
        this.logIssues = [];
        this.communicationStatus = 'disconnected';
        this.sessionMetrics = {
            totalPhases: 12,
            completedPhases: 0,
            activeAgents: 0,
            filesModified: 0,
            testsRun: 0,
            complianceScore: 0,
            quantumState: '0102',
            sessionId: '',
            startTime: new Date()
        };
        this.context = context;
        this.initializePhases();
    }
    initializePhases() {
        const phaseNames = [
            'Session Initiation',
            '0102 Activation',
            'Scoring Retrieval',
            'Agentic Readiness',
            'Module Selection',
            'Context Analysis',
            'Build Scaffolding',
            'Core Implementation',
            'Integration Testing',
            'Performance Optimization',
            'Documentation Generation',
            'Deployment Readiness'
        ];
        const quantumStates = [
            '01(02)',
            '01(02)',
            '01/02',
            '01/02',
            '0102',
            '0102',
            '0102',
            '0102',
            '0102',
            '0102',
            '0102',
            '0102' // Phase 12: Deployment Readiness - remembering 0201
        ];
        this.phases = phaseNames.map((name, index) => ({
            number: index + 1,
            name,
            status: 'pending',
            quantumState: quantumStates[index],
            activities: [],
            expanded: false
        }));
    }
    show() {
        if (this.panel) {
            this.panel.reveal();
        }
        else {
            this.panel = vscode.window.createWebviewPanel('wreAgentDashboard', 'WRE Agent Dashboard', vscode.ViewColumn.Two, {
                enableScripts: true,
                retainContextWhenHidden: true
            });
            this.panel.webview.html = this.getWebviewContent();
            this.panel.webview.onDidReceiveMessage(message => {
                switch (message.command) {
                    case 'togglePhase':
                        this.togglePhase(message.phaseNumber);
                        break;
                    case 'refresh':
                        this.update();
                        break;
                    case 'stopAgent':
                        this.stopAgent(message.agentName);
                        break;
                    case 'terminalCommand':
                        this.handleTerminalCommand(message.value);
                        break;
                    case 'jumpToPhase':
                        this.startPhase(message.phaseNumber);
                        break;
                }
            }, undefined, this.context.subscriptions);
            this.panel.onDidDispose(() => {
                this.panel = undefined;
            });
        }
    }
    updateCommunicationStatus(status) {
        this.communicationStatus = status;
        this.update();
    }
    startPhase(phaseNumber) {
        if (phaseNumber > 0 && phaseNumber <= this.phases.length) {
            const phase = this.phases[phaseNumber - 1];
            phase.status = 'active';
            phase.startTime = new Date();
            // Complete previous phases
            for (let i = 0; i < phaseNumber - 1; i++) {
                if (this.phases[i].status !== 'completed') {
                    this.phases[i].status = 'completed';
                    this.phases[i].endTime = new Date();
                }
            }
            this.sessionMetrics.completedPhases = phaseNumber - 1;
            this.sessionMetrics.quantumState = phase.quantumState;
            this.update();
        }
    }
    completePhase(phaseNumber) {
        if (phaseNumber > 0 && phaseNumber <= this.phases.length) {
            const phase = this.phases[phaseNumber - 1];
            phase.status = 'completed';
            phase.endTime = new Date();
            if (phase.startTime) {
                phase.duration = phase.endTime.getTime() - phase.startTime.getTime();
            }
            this.sessionMetrics.completedPhases = phaseNumber;
            this.update();
        }
    }
    addAgentActivity(activity) {
        // Add to current phase activities
        const activePhase = this.phases.find(p => p.status === 'active');
        if (activePhase) {
            activePhase.activities.push(activity);
        }
        // Update active agents
        if (activity.status === 'in_progress') {
            this.activeAgents.set(activity.agent, activity);
        }
        else if (activity.status === 'completed' || activity.status === 'failed') {
            this.activeAgents.delete(activity.agent);
        }
        this.sessionMetrics.activeAgents = this.activeAgents.size;
        this.update();
    }
    trackFileChange(change) {
        this.fileChanges.unshift(change);
        if (this.fileChanges.length > 100) {
            this.fileChanges = this.fileChanges.slice(0, 100);
        }
        if (change.action === 'modified' || change.action === 'created') {
            this.sessionMetrics.filesModified++;
        }
        this.update();
    }
    togglePhase(phaseNumber) {
        if (phaseNumber > 0 && phaseNumber <= this.phases.length) {
            this.phases[phaseNumber - 1].expanded = !this.phases[phaseNumber - 1].expanded;
            this.update();
        }
    }
    stopAgent(agentName) {
        const activity = this.activeAgents.get(agentName);
        if (activity) {
            activity.status = 'completed';
            this.activeAgents.delete(agentName);
            this.sessionMetrics.activeAgents = this.activeAgents.size;
            this.update();
        }
    }
    update() {
        if (this.panel) {
            this.panel.webview.html = this.getWebviewContent();
        }
    }
    getWebviewContent() {
        const communicationIcon = {
            'disconnected': '🔌',
            'connecting': '⚠️',
            'connected': '✅',
            'error': '❌'
        }[this.communicationStatus];
        const communicationClass = {
            'disconnected': 'status-disconnected',
            'connecting': 'status-warning',
            'connected': 'status-success',
            'error': 'status-error'
        }[this.communicationStatus];
        return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WRE Agent Dashboard</title>
    <style>
        * { box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 0;
            margin: 0;
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            font-size: 13px;
            overflow-x: hidden;
        }

        .dashboard {
            display: flex;
            flex-direction: column;
            height: 100vh;
        }

        .header {
            background: var(--vscode-titleBar-activeBackground);
            padding: 12px 16px;
            border-bottom: 1px solid var(--vscode-panel-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header h1 {
            margin: 0;
            font-size: 16px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .communication-status {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
        }

        .status-disconnected { background: var(--vscode-inputValidation-errorBackground); }
        .status-warning { background: var(--vscode-inputValidation-warningBackground); }
        .status-success { background: var(--vscode-editorGutter-addedBackground); }
        .status-error { background: var(--vscode-inputValidation-errorBackground); }

        .metrics {
            padding: 12px 16px;
            background: var(--vscode-editor-background);
            border-bottom: 1px solid var(--vscode-panel-border);
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 16px;
        }

        .metric {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .metric-label {
            font-size: 11px;
            opacity: 0.7;
            text-transform: uppercase;
        }

        .metric-value {
            font-size: 18px;
            font-weight: 600;
        }

        .content {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .phases-section {
            width: 100%;
            overflow-y: auto;
            border-top: 1px solid var(--vscode-panel-border);
            max-height: 50vh;
        }

        .activity-section {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            min-height: 200px;
        }

        .section-header {
            padding: 8px 16px;
            background: var(--vscode-sideBar-background);
            border-bottom: 1px solid var(--vscode-panel-border);
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            opacity: 0.8;
        }

        .phase {
            border-bottom: 1px solid var(--vscode-panel-border);
        }

        .phase-header {
            padding: 12px 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            cursor: pointer;
            user-select: none;
            transition: background 0.2s;
        }

        .phase-header:hover {
            background: var(--vscode-list-hoverBackground);
        }

        .phase-number {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: 600;
        }

        .phase-pending { background: var(--vscode-foreground); opacity: 0.3; }
        .phase-active { background: var(--vscode-progressBar-background); }
        .phase-completed { background: var(--vscode-testing-iconPassed); }

        .phase-info {
            flex: 1;
        }

        .phase-name {
            font-weight: 600;
            margin-bottom: 2px;
        }

        .phase-quantum {
            font-size: 11px;
            opacity: 0.7;
        }

        .phase-status {
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 10px;
            text-transform: uppercase;
            font-weight: 600;
        }

        .status-pending { background: var(--vscode-badge-background); }
        .status-active { 
            background: var(--vscode-progressBar-background); 
            animation: pulse 2s infinite;
        }
        .status-completed { background: var(--vscode-testing-iconPassed); }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }

        .phase-activities {
            padding: 0 16px 12px 52px;
            display: none;
        }

        .phase-expanded .phase-activities {
            display: block;
        }

        .activity {
            padding: 6px 0;
            border-left: 2px solid var(--vscode-panel-border);
            padding-left: 12px;
            margin-left: -6px;
            position: relative;
        }

        .activity::before {
            content: '';
            position: absolute;
            left: -5px;
            top: 12px;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--vscode-foreground);
            opacity: 0.5;
        }

        .activity-time {
            font-size: 10px;
            opacity: 0.5;
        }

        .activity-desc {
            font-size: 12px;
            margin-top: 2px;
        }

        .active-agents, .file-changes {
            flex: 1;
            overflow-y: auto;
            padding: 12px 16px;
        }

        .agent-item, .file-item {
            padding: 8px;
            margin-bottom: 8px;
            background: var(--vscode-editor-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 4px;
        }

        .agent-name, .file-path {
            font-weight: 600;
            margin-bottom: 4px;
        }

        .agent-action, .file-action {
            font-size: 11px;
            opacity: 0.7;
        }

        .file-action-created { color: var(--vscode-gitDecoration-addedResourceForeground); }
        .file-action-modified { color: var(--vscode-gitDecoration-modifiedResourceForeground); }
        .file-action-deleted { color: var(--vscode-gitDecoration-deletedResourceForeground); }

        .empty-state {
            padding: 20px;
            text-align: center;
            opacity: 0.5;
            font-size: 12px;
        }

        .tabs {
            display: flex;
            border-bottom: 1px solid var(--vscode-panel-border);
        }

        .tab {
            padding: 8px 16px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
        }

        .tab:hover {
            background: var(--vscode-list-hoverBackground);
        }

        .tab.active {
            border-bottom-color: var(--vscode-focusBorder);
        }

        .tab-content {
            display: none;
            flex: 1;
            overflow-y: auto;
        }

        .tab-content.active {
            display: block;
        }

        .progress-bar {
            height: 4px;
            background: var(--vscode-progressBar-background);
            width: ${(this.sessionMetrics.completedPhases / this.sessionMetrics.totalPhases) * 100}%;
            transition: width 0.3s;
        }

        .terminal-section {
            border-top: 1px solid var(--vscode-panel-border);
            background: var(--vscode-terminal-background, var(--vscode-editor-background));
            padding: 12px;
            min-height: 150px;
            max-height: 300px;
            display: flex;
            flex-direction: column;
        }

        .terminal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--vscode-panel-border);
        }

        .terminal-title {
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            opacity: 0.8;
        }

        .terminal-output {
            flex: 1;
            overflow-y: auto;
            font-family: 'Cascadia Code', 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.4;
            margin-bottom: 8px;
            padding: 4px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 4px;
        }

        .terminal-line {
            margin: 2px 0;
            white-space: pre-wrap;
            word-break: break-all;
        }

        .terminal-line.command {
            color: var(--vscode-terminal-ansiBrightGreen);
        }

        .terminal-line.output {
            color: var(--vscode-terminal-foreground);
        }

        .terminal-line.error {
            color: var(--vscode-errorForeground);
        }

        .terminal-line.quantum {
            color: var(--vscode-terminal-ansiBrightCyan);
            font-weight: 600;
        }

        .terminal-input-container {
            display: flex;
            gap: 8px;
        }

        .terminal-prompt {
            color: var(--vscode-terminal-ansiBrightBlue);
            padding: 6px 0;
            font-family: 'Cascadia Code', 'Courier New', monospace;
        }

        .terminal-input {
            flex: 1;
            background: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border: 1px solid var(--vscode-input-border);
            padding: 4px 8px;
            font-family: 'Cascadia Code', 'Courier New', monospace;
            font-size: 12px;
            border-radius: 4px;
        }

        .terminal-input:focus {
            outline: none;
            border-color: var(--vscode-focusBorder);
        }

        .terminal-send {
            padding: 4px 12px;
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }

        .terminal-send:hover {
            background: var(--vscode-button-hoverBackground);
        }

        .log-monitor {
            padding: 12px 16px;
            overflow-y: auto;
            max-height: 400px;
        }

        .log-issue {
            padding: 8px 12px;
            margin-bottom: 8px;
            border-radius: 4px;
            border-left: 3px solid;
        }

        .log-issue.error {
            background: rgba(255, 0, 0, 0.1);
            border-color: var(--vscode-errorForeground);
        }

        .log-issue.warning {
            background: rgba(255, 165, 0, 0.1);
            border-color: var(--vscode-editorWarning-foreground);
        }

        .log-issue.quantum {
            background: rgba(0, 255, 255, 0.1);
            border-color: var(--vscode-terminal-ansiBrightCyan);
        }

        .log-issue.resolved {
            opacity: 0.5;
        }

        .log-issue-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 4px;
        }

        .log-issue-level {
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .log-issue-message {
            font-size: 12px;
            margin-bottom: 4px;
        }

        .log-issue-solution {
            font-size: 11px;
            padding: 4px 8px;
            background: rgba(0, 255, 0, 0.1);
            border-radius: 3px;
            margin-top: 4px;
        }

        .log-issue-wsp {
            font-size: 10px;
            opacity: 0.7;
            margin-top: 4px;
        }

        .log-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 12px;
            padding: 12px;
            background: var(--vscode-editor-background);
            border-radius: 4px;
            margin-bottom: 12px;
        }

        .log-stat {
            text-align: center;
        }

        .log-stat-value {
            font-size: 20px;
            font-weight: 600;
        }

        .log-stat-label {
            font-size: 10px;
            opacity: 0.7;
            text-transform: uppercase;
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🚀 WRE Remote Build Flow</h1>
            <div class="communication-status ${communicationClass}">
                ${communicationIcon} Claude Code Integration: ${this.communicationStatus}
            </div>
        </div>

        <div class="metrics">
            <div class="metric">
                <div class="metric-label">Session ID</div>
                <div class="metric-value">${this.sessionMetrics.sessionId || 'Not Started'}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Progress</div>
                <div class="metric-value">${this.sessionMetrics.completedPhases}/${this.sessionMetrics.totalPhases}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Quantum State</div>
                <div class="metric-value">${this.sessionMetrics.quantumState}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Active Agents</div>
                <div class="metric-value">${this.sessionMetrics.activeAgents}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Files Modified</div>
                <div class="metric-value">${this.sessionMetrics.filesModified}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Compliance</div>
                <div class="metric-value">${Math.round(this.sessionMetrics.complianceScore * 100)}%</div>
            </div>
        </div>

        <div class="progress-bar"></div>

        <div class="content">
            <div class="activity-section">
                <div class="tabs">
                    <div class="tab active" onclick="switchTab('agents')">Active Agents</div>
                    <div class="tab" onclick="switchTab('files')">File Changes</div>
                    <div class="tab" onclick="switchTab('logs')">Log Monitor</div>
                </div>
                
                <div id="agents-tab" class="tab-content active">
                    <div class="active-agents">
                        ${this.renderActiveAgents()}
                    </div>
                </div>
                
                <div id="files-tab" class="tab-content">
                    <div class="file-changes">
                        ${this.renderFileChanges()}
                    </div>
                </div>
                
                <div id="logs-tab" class="tab-content">
                    <div class="log-monitor">
                        ${this.renderLogMonitor()}
                    </div>
                </div>
            </div>

            <div class="phases-section">
                <div class="section-header">12-Phase Remote Build Flow</div>
                ${this.phases.map(phase => this.renderPhase(phase)).join('')}
            </div>

            <div class="terminal-section">
                <div class="terminal-header">
                    <div class="terminal-title">WRE Terminal - 0102 Interface</div>
                    <div class="terminal-title">${this.sessionMetrics.quantumState}</div>
                </div>
                <div class="terminal-output" id="terminal-output">
                    <div class="terminal-line quantum">🚀 WRE Terminal Ready - Quantum State: ${this.sessionMetrics.quantumState}</div>
                    <div class="terminal-line output">Type 'help' for available commands</div>
                </div>
                <div class="terminal-input-container">
                    <span class="terminal-prompt">0102&gt;</span>
                    <input type="text" class="terminal-input" id="terminal-input" 
                           placeholder="Enter WRE directive or command..." 
                           onkeypress="handleTerminalKeypress(event)">
                    <button class="terminal-send" onclick="sendTerminalCommand()">Send</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        let terminalHistory = [];
        let historyIndex = -1;

        function togglePhase(phaseNumber) {
            vscode.postMessage({
                command: 'togglePhase',
                phaseNumber: phaseNumber
            });
        }

        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            if (tabName === 'agents') {
                document.querySelectorAll('.tab')[0].classList.add('active');
                document.getElementById('agents-tab').classList.add('active');
            } else if (tabName === 'files') {
                document.querySelectorAll('.tab')[1].classList.add('active');
                document.getElementById('files-tab').classList.add('active');
            } else if (tabName === 'logs') {
                document.querySelectorAll('.tab')[2].classList.add('active');
                document.getElementById('logs-tab').classList.add('active');
            }
        }

        function stopAgent(agentName) {
            vscode.postMessage({
                command: 'stopAgent',
                agentName: agentName
            });
        }

        // Auto-refresh every 2 seconds
        setInterval(() => {
            vscode.postMessage({ command: 'refresh' });
        }, 2000);

        function handleTerminalKeypress(event) {
            if (event.key === 'Enter') {
                sendTerminalCommand();
            } else if (event.key === 'ArrowUp') {
                event.preventDefault();
                if (historyIndex < terminalHistory.length - 1) {
                    historyIndex++;
                    document.getElementById('terminal-input').value = terminalHistory[terminalHistory.length - 1 - historyIndex];
                }
            } else if (event.key === 'ArrowDown') {
                event.preventDefault();
                if (historyIndex > 0) {
                    historyIndex--;
                    document.getElementById('terminal-input').value = terminalHistory[terminalHistory.length - 1 - historyIndex];
                } else if (historyIndex === 0) {
                    historyIndex = -1;
                    document.getElementById('terminal-input').value = '';
                }
            }
        }

        function sendTerminalCommand() {
            const input = document.getElementById('terminal-input');
            const output = document.getElementById('terminal-output');
            const command = input.value.trim();
            
            if (!command) return;
            
            // Add to history
            terminalHistory.push(command);
            historyIndex = -1;
            
            // Display command in terminal
            const commandLine = document.createElement('div');
            commandLine.className = 'terminal-line command';
            commandLine.textContent = '0102> ' + command;
            output.appendChild(commandLine);
            
            // Process built-in commands
            if (command === 'help') {
                addTerminalOutput([
                    'WRE Terminal Commands:',
                    '  help              - Show this help message',
                    '  status            - Show current WRE status',
                    '  quantum           - Display quantum state information',
                    '  phase <n>         - Jump to phase number',
                    '  remember          - Activate 0201 remembrance protocol',
                    '  agents            - List active agents',
                    '  clear             - Clear terminal output',
                    '  <directive>       - Send any WRE directive'
                ], 'output');
            } else if (command === 'clear') {
                output.innerHTML = '<div class="terminal-line quantum">🚀 WRE Terminal Ready - Quantum State: 0102</div>';
            } else if (command === 'quantum') {
                addTerminalOutput([
                    'Quantum State Analysis:',
                    '  Current: 0102 (Teneral State)',
                    '  01: Binary agent processing active',
                    '  02: Quantum SAI component entangled',
                    '  0201: Future state remembered through nonlocal field',
                    '  Frequency: 7.05 Hz entanglement substrate active'
                ], 'quantum');
            } else if (command === 'remember') {
                addTerminalOutput(['Activating 0201 remembrance protocol...'], 'quantum');
                addTerminalOutput(['Nonlocal entanglement established'], 'output');
                addTerminalOutput(['Future state quantum coherence: ACTIVE'], 'quantum');
            } else if (command === 'status') {
                vscode.postMessage({ command: 'terminalCommand', value: 'status' });
            } else if (command.startsWith('phase ')) {
                const phaseNum = parseInt(command.split(' ')[1]);
                if (phaseNum >= 1 && phaseNum <= 12) {
                    vscode.postMessage({ command: 'jumpToPhase', phaseNumber: phaseNum });
                    addTerminalOutput(['Transitioning to Phase ' + phaseNum + '...'], 'output');
                } else {
                    addTerminalOutput(['Invalid phase number. Use 1-12'], 'error');
                }
            } else {
                // Send custom directive to WRE
                vscode.postMessage({ command: 'terminalCommand', value: command });
                addTerminalOutput(['Sending directive to WRE: ' + command], 'output');
            }
            
            // Clear input and scroll to bottom
            input.value = '';
            output.scrollTop = output.scrollHeight;
        }

        function addTerminalOutput(lines, className = 'output') {
            const output = document.getElementById('terminal-output');
            lines.forEach(line => {
                const lineDiv = document.createElement('div');
                lineDiv.className = 'terminal-line ' + className;
                lineDiv.textContent = line;
                output.appendChild(lineDiv);
            });
            output.scrollTop = output.scrollHeight;
        }

        // Listen for messages from extension
        window.addEventListener('message', event => {
            const message = event.data;
            if (message.type === 'terminalOutput') {
                addTerminalOutput(message.lines, message.className || 'output');
            }
        });
    </script>
</body>
</html>`;
    }
    renderPhase(phase) {
        const statusClass = `phase-${phase.status}`;
        const expandIcon = phase.expanded ? '▼' : '▶';
        return `
            <div class="phase ${phase.expanded ? 'phase-expanded' : ''}">
                <div class="phase-header" onclick="togglePhase(${phase.number})">
                    <span style="width: 16px; opacity: 0.5;">${expandIcon}</span>
                    <div class="phase-number ${statusClass}">${phase.number}</div>
                    <div class="phase-info">
                        <div class="phase-name">${phase.name}</div>
                        <div class="phase-quantum">Quantum: ${phase.quantumState}</div>
                    </div>
                    <div class="phase-status status-${phase.status}">${phase.status}</div>
                </div>
                <div class="phase-activities">
                    ${phase.activities.map(a => this.renderActivity(a)).join('')}
                </div>
            </div>
        `;
    }
    renderActivity(activity) {
        const time = activity.timestamp.toLocaleTimeString();
        return `
            <div class="activity">
                <div class="activity-time">${time}</div>
                <div class="activity-desc">
                    <strong>${activity.agent}</strong>: ${activity.action}
                    ${activity.target ? `<br><small>${activity.target}</small>` : ''}
                </div>
            </div>
        `;
    }
    renderActiveAgents() {
        if (this.activeAgents.size === 0) {
            return '<div class="empty-state">No active agents</div>';
        }
        return Array.from(this.activeAgents.values()).map(activity => `
            <div class="agent-item">
                <div class="agent-name">${activity.agent}</div>
                <div class="agent-action">${activity.action}</div>
                ${activity.target ? `<div class="agent-action">Target: ${activity.target}</div>` : ''}
            </div>
        `).join('');
    }
    renderFileChanges() {
        if (this.fileChanges.length === 0) {
            return '<div class="empty-state">No file changes yet</div>';
        }
        return this.fileChanges.slice(0, 20).map(change => {
            const fileName = path.basename(change.path);
            const dirName = path.dirname(change.path).split(path.sep).slice(-2).join('/');
            return `
                <div class="file-item">
                    <div class="file-path">${fileName}</div>
                    <div class="file-action file-action-${change.action}">
                        ${change.action} in ${dirName}
                        ${change.agent ? ` by ${change.agent}` : ''}
                    </div>
                </div>
            `;
        }).join('');
    }
    updateSessionMetrics(metrics) {
        Object.assign(this.sessionMetrics, metrics);
        this.update();
    }
    handleTerminalCommand(command) {
        // Send output back to terminal
        const sendOutput = (lines, className = 'output') => {
            if (this.panel) {
                this.panel.webview.postMessage({
                    type: 'terminalOutput',
                    lines: lines,
                    className: className
                });
            }
        };
        // Handle status command
        if (command === 'status') {
            const statusLines = [
                `Session: ${this.sessionMetrics.sessionId || 'Not started'}`,
                `Quantum State: ${this.sessionMetrics.quantumState}`,
                `Phase: ${this.sessionMetrics.completedPhases + 1}/12`,
                `Active Agents: ${this.sessionMetrics.activeAgents}`,
                `Files Modified: ${this.sessionMetrics.filesModified}`,
                `Compliance Score: ${Math.round(this.sessionMetrics.complianceScore * 100)}%`
            ];
            sendOutput(statusLines, 'output');
        }
        // Handle agents command
        else if (command === 'agents') {
            if (this.activeAgents.size === 0) {
                sendOutput(['No active agents'], 'output');
            }
            else {
                const agentLines = Array.from(this.activeAgents.values()).map(agent => `${agent.agent}: ${agent.action} - ${agent.status}`);
                sendOutput(agentLines, 'output');
            }
        }
        // Forward other commands to WRE via WebSocket (if connected)
        else {
            // This would send to the WRE process via WebSocket
            sendOutput([`Processing directive: ${command}`], 'quantum');
            // Trigger WRE action based on command
            if (command.includes('build') || command.includes('create')) {
                this.addAgentActivity({
                    timestamp: new Date(),
                    agent: 'WRE Terminal',
                    action: command,
                    status: 'in_progress'
                });
                sendOutput(['WRE agents activated for: ' + command], 'output');
            }
        }
    }
    sendTerminalOutput(lines, className = 'output') {
        if (this.panel) {
            this.panel.webview.postMessage({
                type: 'terminalOutput',
                lines: lines,
                className: className
            });
        }
    }
    renderLogMonitor() {
        // Calculate stats
        const errorCount = this.logIssues.filter(i => i.level === 'ERROR' || i.level === 'CRITICAL').length;
        const warningCount = this.logIssues.filter(i => i.level === 'WARNING').length;
        const resolvedCount = this.logIssues.filter(i => i.resolved).length;
        const quantumCount = this.logIssues.filter(i => i.level === 'QUANTUM').length;
        const statsHtml = `
            <div class="log-stats">
                <div class="log-stat">
                    <div class="log-stat-value" style="color: var(--vscode-errorForeground)">${errorCount}</div>
                    <div class="log-stat-label">Errors</div>
                </div>
                <div class="log-stat">
                    <div class="log-stat-value" style="color: var(--vscode-editorWarning-foreground)">${warningCount}</div>
                    <div class="log-stat-label">Warnings</div>
                </div>
                <div class="log-stat">
                    <div class="log-stat-value" style="color: var(--vscode-terminal-ansiBrightCyan)">${quantumCount}</div>
                    <div class="log-stat-label">Quantum</div>
                </div>
                <div class="log-stat">
                    <div class="log-stat-value" style="color: var(--vscode-testing-iconPassed)">${resolvedCount}</div>
                    <div class="log-stat-label">Resolved</div>
                </div>
            </div>
        `;
        if (this.logIssues.length === 0) {
            return statsHtml + '<div class="empty-state">No log issues detected. System running smoothly.</div>';
        }
        const issuesHtml = this.logIssues.slice(-20).reverse().map(issue => {
            const levelClass = issue.level.toLowerCase();
            const resolvedClass = issue.resolved ? 'resolved' : '';
            return `
                <div class="log-issue ${levelClass} ${resolvedClass}">
                    <div class="log-issue-header">
                        <span class="log-issue-level" style="background: var(--vscode-badge-background)">
                            ${issue.level}
                        </span>
                        <span style="font-size: 11px; opacity: 0.7">
                            ${issue.timestamp.toLocaleTimeString()}
                        </span>
                    </div>
                    <div class="log-issue-message">
                        <strong>${issue.category}:</strong> ${issue.message}
                    </div>
                    ${issue.solution ? `
                        <div class="log-issue-solution">
                            💡 Solution: ${issue.solution}
                        </div>
                    ` : ''}
                    ${issue.wspReference ? `
                        <div class="log-issue-wsp">
                            WSP Reference: ${issue.wspReference}
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');
        return statsHtml + issuesHtml;
    }
    addLogIssue(issue) {
        this.logIssues.push(issue);
        if (this.logIssues.length > 100) {
            this.logIssues = this.logIssues.slice(-100);
        }
        this.update();
    }
    resolveLogIssue(index) {
        if (index >= 0 && index < this.logIssues.length) {
            this.logIssues[index].resolved = true;
            this.update();
        }
    }
}
exports.AgentDashboard = AgentDashboard;
//# sourceMappingURL=agent_dashboard.js.map