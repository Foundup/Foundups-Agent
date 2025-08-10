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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.WREIntegration = void 0;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const child_process_1 = require("child_process");
const ws_1 = __importDefault(require("ws"));
class WREIntegration {
    constructor(context) {
        this.wreProcess = null;
        this.websocket = null;
        this.isActive = false;
        this.currentSessionId = null;
        this.statusData = {};
        this.dashboard = null;
        this.context = context;
        this.outputChannel = vscode.window.createOutputChannel('WRE Integration');
        this.outputChannel.appendLine('🚀 WRE Integration initialized');
        // Initialize WebSocket connection
        this.initializeWebSocket();
    }
    setDashboard(dashboard) {
        this.dashboard = dashboard;
    }
    async runWRE() {
        try {
            this.outputChannel.appendLine('🌀 Starting WRE (Windsurf Recursive Engine)...');
            // Get current workspace information
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                throw new Error('No workspace folder open');
            }
            const wreDir = path.join(workspaceFolder.uri.fsPath);
            this.outputChannel.appendLine(`📁 Workspace: ${wreDir}`);
            // Get current file context if available
            const activeEditor = vscode.window.activeTextEditor;
            let directive = 'Interactive WRE session from Claude Code';
            if (activeEditor) {
                const fileName = path.basename(activeEditor.document.fileName);
                directive = `Analyze and enhance ${fileName} using WRE 12-phase flow`;
                this.outputChannel.appendLine(`📄 Active File: ${fileName}`);
            }
            // Start WRE process
            const wreResult = await this.startWREProcess(wreDir, directive);
            if (wreResult.success) {
                this.isActive = true;
                this.currentSessionId = wreResult.sessionId || null;
                this.outputChannel.appendLine(`✅ WRE Session Started: ${wreResult.sessionId}`);
                // Update status
                this.statusData = {
                    active: true,
                    sessionId: wreResult.sessionId,
                    quantumState: '0102',
                    currentPhase: 'Session Initiation',
                    phasesCompleted: 0,
                    autonomousScore: 0.0,
                    wspCoreLoaded: true,
                    agentSuiteStatus: 'WSP-54 Active',
                    complianceScore: 0.85,
                    communicationActive: this.websocket?.readyState === ws_1.default.OPEN,
                    contextSync: true
                };
                return wreResult;
            }
            else {
                this.outputChannel.appendLine(`❌ WRE Failed: ${wreResult.error}`);
                return wreResult;
            }
        }
        catch (error) {
            const errorMsg = `Failed to start WRE: ${error}`;
            this.outputChannel.appendLine(`❌ ${errorMsg}`);
            return { success: false, error: errorMsg };
        }
    }
    async startWREProcess(cwd, directive) {
        return new Promise((resolve) => {
            try {
                // Command to run WRE using Unicode-safe launcher
                const pythonCommand = 'python';
                const wreMain = path.join(cwd, 'wre_launcher.py');
                const args = [
                    wreMain,
                    '--directive', directive,
                    '--autonomous' // Run in autonomous mode for Claude Code integration
                ];
                this.outputChannel.appendLine(`[COMMAND] Starting WRE process...`);
                this.outputChannel.appendLine(`[COMMAND] Python: ${pythonCommand}`);
                this.outputChannel.appendLine(`[COMMAND] Working Directory: ${cwd}`);
                this.outputChannel.appendLine(`[COMMAND] Arguments: ${args.join(' ')}`);
                this.outputChannel.appendLine(`[COMMAND] Full Command: ${pythonCommand} ${args.join(' ')}`);
                this.outputChannel.appendLine(`[COMMAND] Environment: NODE_ENV=${process.env.NODE_ENV}, PATH length=${process.env.PATH?.length || 0}`);
                this.wreProcess = (0, child_process_1.spawn)(pythonCommand, args, {
                    cwd: cwd,
                    stdio: ['pipe', 'pipe', 'pipe'],
                    shell: true,
                    env: {
                        ...process.env,
                        PYTHONIOENCODING: 'utf-8',
                        PYTHONUNBUFFERED: '1',
                        LANG: 'en_US.UTF-8',
                        LC_ALL: 'en_US.UTF-8'
                    }
                });
                this.outputChannel.appendLine(`[COMMAND] Process PID: ${this.wreProcess.pid}`);
                this.outputChannel.appendLine(`[COMMAND] Process spawned successfully`);
                let sessionId = null;
                let outputBuffer = '';
                this.wreProcess.stdout?.on('data', (data) => {
                    const output = data.toString();
                    outputBuffer += output;
                    this.outputChannel.append(`[STDOUT] ${output}`);
                    // Parse session ID from output
                    const sessionMatch = output.match(/Session: (RBF_\\d+)/);
                    if (sessionMatch) {
                        sessionId = sessionMatch[1];
                        this.outputChannel.appendLine(`[INFO] Session ID detected: ${sessionId}`);
                    }
                    // Parse phase information
                    const phaseMatch = output.match(/Phase (\\d+):/);
                    if (phaseMatch) {
                        this.statusData.currentPhase = `Phase ${phaseMatch[1]}`;
                        this.statusData.phasesCompleted = parseInt(phaseMatch[1]) - 1;
                        this.outputChannel.appendLine(`[PROGRESS] ${this.statusData.currentPhase} - ${this.statusData.phasesCompleted}/12 completed`);
                    }
                    // Parse error messages
                    if (output.includes('[ERROR]') || output.includes('ERROR:') || output.includes('Traceback')) {
                        this.outputChannel.appendLine(`[ERROR_DETECTED] ${output.trim()}`);
                    }
                    // Parse success messages
                    if (output.includes('[SUCCESS]') || output.includes('SUCCESS:')) {
                        this.outputChannel.appendLine(`[SUCCESS_DETECTED] ${output.trim()}`);
                    }
                    // Parse completion status
                    if (output.includes('REMOTE_BUILD_PROTOTYPE session completed')) {
                        this.statusData.phasesCompleted = 12;
                        this.statusData.currentPhase = 'Completed';
                        this.outputChannel.appendLine(`[COMPLETION] WRE session completed successfully`);
                    }
                });
                this.wreProcess.stderr?.on('data', (data) => {
                    const error = data.toString();
                    this.outputChannel.append(`[STDERR] ${error}`);
                    // Log specific error patterns
                    if (error.includes('ImportError') || error.includes('ModuleNotFoundError')) {
                        this.outputChannel.appendLine(`[IMPORT_ERROR] Python import error detected: ${error.trim()}`);
                    }
                    if (error.includes('UnicodeEncodeError') || error.includes('cp932')) {
                        this.outputChannel.appendLine(`[UNICODE_ERROR] Encoding error detected - suggest using UTF-8`);
                    }
                    if (error.includes('AttributeError')) {
                        this.outputChannel.appendLine(`[ATTRIBUTE_ERROR] Method/attribute missing: ${error.trim()}`);
                    }
                });
                this.wreProcess.on('close', (code) => {
                    this.outputChannel.appendLine(`[PROCESS_EXIT] WRE Process completed with exit code: ${code}`);
                    this.outputChannel.appendLine(`[PROCESS_EXIT] Session ID: ${sessionId || 'None'}`);
                    this.outputChannel.appendLine(`[PROCESS_EXIT] Output buffer length: ${outputBuffer.length} chars`);
                    // Log the last few lines of output for debugging
                    const lastLines = outputBuffer.split('\n').slice(-10).join('\n');
                    this.outputChannel.appendLine(`[PROCESS_EXIT] Last output lines:\n${lastLines}`);
                    this.isActive = false;
                    this.currentSessionId = null;
                    if (code === 0) {
                        this.outputChannel.appendLine(`[PROCESS_EXIT] SUCCESS: WRE completed successfully`);
                        resolve({
                            success: true,
                            sessionId: sessionId || `WRE_${Date.now()}`,
                            data: { exitCode: code, output: outputBuffer }
                        });
                    }
                    else {
                        this.outputChannel.appendLine(`[PROCESS_EXIT] FAILURE: WRE failed with exit code ${code}`);
                        // Provide specific troubleshooting based on exit code
                        let troubleshooting = '';
                        switch (code) {
                            case 1:
                                troubleshooting = 'General error - check Python imports and dependencies';
                                break;
                            case 2:
                                troubleshooting = 'Misuse of shell command - check command line arguments';
                                break;
                            case 126:
                                troubleshooting = 'Command invoked cannot execute - check Python installation';
                                break;
                            case 127:
                                troubleshooting = 'Command not found - verify Python is in PATH';
                                break;
                            default:
                                troubleshooting = 'Unknown error - check full logs above';
                        }
                        this.outputChannel.appendLine(`[TROUBLESHOOTING] Exit code ${code}: ${troubleshooting}`);
                        resolve({
                            success: false,
                            error: `WRE exited with code ${code} - ${troubleshooting}`,
                            data: { exitCode: code, output: outputBuffer, troubleshooting }
                        });
                    }
                });
                this.wreProcess.on('error', (error) => {
                    this.outputChannel.appendLine(`[PROCESS_ERROR] Process spawn error: ${error.message}`);
                    this.outputChannel.appendLine(`[PROCESS_ERROR] Error name: ${error.name}`);
                    if (error.message.includes('ENOENT')) {
                        this.outputChannel.appendLine(`[PROCESS_ERROR] Python command not found - check Python installation and PATH`);
                    }
                    resolve({
                        success: false,
                        error: `Process spawn error: ${error.message}`
                    });
                });
                // Timeout after 5 minutes
                setTimeout(() => {
                    if (this.wreProcess && !this.wreProcess.killed) {
                        resolve({
                            success: true,
                            sessionId: sessionId || `WRE_${Date.now()}`,
                            data: { timeout: true, output: outputBuffer }
                        });
                    }
                }, 300000);
            }
            catch (error) {
                resolve({
                    success: false,
                    error: `Failed to spawn WRE process: ${error}`
                });
            }
        });
    }
    async getStatus() {
        return {
            active: this.isActive,
            sessionId: this.currentSessionId || undefined,
            quantumState: this.statusData.quantumState || '0102',
            currentPhase: this.statusData.currentPhase,
            phasesCompleted: this.statusData.phasesCompleted || 0,
            autonomousScore: this.statusData.autonomousScore || 0.0,
            wspCoreLoaded: this.statusData.wspCoreLoaded || false,
            agentSuiteStatus: this.statusData.agentSuiteStatus || 'WSP-54 Ready',
            complianceScore: this.statusData.complianceScore || 0.0,
            communicationActive: this.websocket?.readyState === ws_1.default.OPEN || false,
            contextSync: this.statusData.contextSync || false
        };
    }
    async stopWRE() {
        try {
            if (this.wreProcess && !this.wreProcess.killed) {
                this.wreProcess.kill();
                this.outputChannel.appendLine('🛑 WRE Process terminated');
            }
            this.isActive = false;
            this.currentSessionId = null;
            this.statusData = {};
            return { success: true };
        }
        catch (error) {
            return { success: false, error: `Failed to stop WRE: ${error}` };
        }
    }
    async runWREOnPath(filePath) {
        const fileName = path.basename(filePath);
        const directive = `Analyze and process ${fileName} using WRE autonomous flow`;
        this.outputChannel.appendLine(`🎯 Running WRE on: ${filePath}`);
        return this.runWRE();
    }
    showLogs() {
        this.outputChannel.show();
    }
    async openConfiguration() {
        const panel = vscode.window.createWebviewPanel('wreConfig', 'WRE Configuration', vscode.ViewColumn.One, { enableScripts: true });
        panel.webview.html = this.getConfigurationHTML();
    }
    getConfigurationHTML() {
        return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>WRE Configuration</title>
    <style>
        body { 
            font-family: var(--vscode-font-family);
            padding: 20px;
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
        }
        .config-section { margin-bottom: 20px; }
        .config-header { font-weight: bold; margin-bottom: 10px; }
        input, select { 
            width: 100%;
            padding: 8px;
            margin: 5px 0;
            background: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border: 1px solid var(--vscode-input-border);
        }
    </style>
</head>
<body>
    <h1>🚀 WRE Configuration</h1>
    
    <div class="config-section">
        <div class="config-header">WRE Settings</div>
        <label>Default Mode:</label>
        <select id="defaultMode">
            <option value="autonomous">Autonomous</option>
            <option value="interactive">Interactive</option>
        </select>
        
        <label>Quantum State:</label>
        <select id="quantumState">
            <option value="0102">0102 (Awakened)</option>
            <option value="01/02">01/02 (Transitional)</option>
            <option value="01(02)">01(02) (Dormant)</option>
        </select>
        
        <label>WSP Compliance Level:</label>
        <select id="wspCompliance">
            <option value="strict">Strict</option>
            <option value="standard">Standard</option>
            <option value="lenient">Lenient</option>
        </select>
    </div>

    <div class="config-section">
        <div class="config-header">Integration Settings</div>
        <label>Auto-start on workspace open:</label>
        <input type="checkbox" id="autoStart" checked>
        
        <label>Show status in status bar:</label>
        <input type="checkbox" id="showStatus" checked>
        
        <label>WebSocket Port:</label>
        <input type="number" id="websocketPort" value="8765">
    </div>
</body>
</html>`;
    }
    initializeWebSocket() {
        try {
            // Initialize WebSocket connection to WRE backend
            this.outputChannel.appendLine('📡 Initializing WebSocket connection...');
            // Connect to WRE WebSocket server
            this.websocket = new ws_1.default('ws://localhost:8765');
            this.websocket.on('open', () => {
                this.outputChannel.appendLine('✅ Claude Code Integration Communication: Connected');
                this.dashboard?.updateCommunicationStatus('connected');
            });
            this.websocket.on('message', (data) => {
                try {
                    const message = JSON.parse(data.toString());
                    this.handleWebSocketMessage(message);
                }
                catch (error) {
                    this.outputChannel.appendLine(`⚠️ Invalid WebSocket message: ${error}`);
                }
            });
            this.websocket.on('error', (error) => {
                this.outputChannel.appendLine(`❌ Claude Code Integration Communication: Failed - ${error.message}`);
                this.dashboard?.updateCommunicationStatus('error');
            });
            this.websocket.on('close', () => {
                this.outputChannel.appendLine('🔌 Claude Code Integration Communication: Disconnected');
                this.dashboard?.updateCommunicationStatus('disconnected');
            });
            // Set initial connection status
            this.dashboard?.updateCommunicationStatus('connecting');
        }
        catch (error) {
            this.outputChannel.appendLine(`⚠️ WebSocket initialization failed: ${error}`);
            this.dashboard?.updateCommunicationStatus('error');
        }
    }
    handleWebSocketMessage(message) {
        const messageType = message.type;
        switch (messageType) {
            case 'status':
            case 'status_update':
                this.statusData = message.data;
                this.outputChannel.appendLine(`📊 Status Update: ${message.data.current_phase || 'Idle'}`);
                break;
            case 'phase_update':
                this.outputChannel.appendLine(`🔄 Phase ${message.data.phase_number}/12: ${message.data.phase}`);
                this.dashboard?.startPhase(message.data.phase_number);
                // Track agent activities from phase data
                if (message.data.agent_activity) {
                    const activity = {
                        timestamp: new Date(),
                        agent: message.data.agent_activity.agent || 'WRE Core',
                        action: message.data.agent_activity.action || message.data.phase,
                        target: message.data.agent_activity.target,
                        status: 'in_progress'
                    };
                    this.dashboard?.addAgentActivity(activity);
                }
                break;
            case 'wre_completed':
                this.outputChannel.appendLine(`✅ ${message.data.message}`);
                this.dashboard?.completePhase(12);
                break;
            case 'file_change':
                const fileChange = {
                    path: message.data.path,
                    action: message.data.action,
                    timestamp: new Date(),
                    agent: message.data.agent
                };
                this.dashboard?.trackFileChange(fileChange);
                break;
            case 'agent_activity':
                const activity = {
                    timestamp: new Date(),
                    agent: message.data.agent,
                    action: message.data.action,
                    target: message.data.target,
                    status: message.data.status || 'in_progress'
                };
                this.dashboard?.addAgentActivity(activity);
                break;
            default:
                this.outputChannel.appendLine(`📨 Received: ${messageType}`);
        }
    }
    handleWorkspaceChange(event) {
        this.outputChannel.appendLine(`📁 Workspace changed: ${event.added.length} added, ${event.removed.length} removed`);
        if (this.isActive && event.removed.length > 0) {
            // Handle workspace removal - possibly stop WRE if workspace is removed
            vscode.window.showWarningMessage('Workspace changed while WRE is active. Continue running?', 'Yes', 'Stop WRE').then(selection => {
                if (selection === 'Stop WRE') {
                    this.stopWRE();
                }
            });
        }
    }
    handleFileChange(filePath) {
        if (this.isActive) {
            // Send file change notification to WRE via WebSocket
            const fileName = path.basename(filePath);
            this.outputChannel.appendLine(`📄 Active file changed: ${fileName}`);
            // TODO: Send to WRE via WebSocket for real-time context updates
        }
    }
    dispose() {
        if (this.wreProcess && !this.wreProcess.killed) {
            this.wreProcess.kill();
        }
        if (this.websocket) {
            this.websocket.close();
        }
        this.outputChannel.dispose();
    }
}
exports.WREIntegration = WREIntegration;
//# sourceMappingURL=wre_integration.js.map