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
exports.deactivate = exports.activate = void 0;
const vscode = __importStar(require("vscode"));
const wre_integration_1 = require("./wre_integration");
const agent_dashboard_1 = require("./agent_dashboard");
function activate(context) {
    console.log('Claude WRE Integration is now active!');
    // Initialize WRE Integration
    const wreIntegration = new wre_integration_1.WREIntegration(context);
    // Initialize Agent Dashboard
    const agentDashboard = new agent_dashboard_1.AgentDashboard(context);
    wreIntegration.setDashboard(agentDashboard);
    // Status bar item
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(rocket) WRE Ready";
    statusBarItem.tooltip = "Click to run WRE (Windsurf Recursive Engine)";
    statusBarItem.command = 'claude-wre.runWRE';
    statusBarItem.show();
    // Register commands
    const commands = [
        // Show Agent Dashboard command
        vscode.commands.registerCommand('claude-wre.showDashboard', () => {
            agentDashboard.show();
        }),
        // Main "Run WRE" command
        vscode.commands.registerCommand('claude-wre.runWRE', async () => {
            // Show dashboard when starting WRE
            agentDashboard.show();
            try {
                statusBarItem.text = "$(loading~spin) WRE Starting...";
                const result = await wreIntegration.runWRE();
                if (result.success) {
                    statusBarItem.text = "$(check) WRE Active";
                    vscode.window.showInformationMessage(`WRE Session Started: ${result.sessionId}`, 'View Logs', 'WRE Status').then(selection => {
                        if (selection === 'View Logs') {
                            wreIntegration.showLogs();
                        }
                        else if (selection === 'WRE Status') {
                            vscode.commands.executeCommand('claude-wre.statusWRE');
                        }
                    });
                }
                else {
                    statusBarItem.text = "$(error) WRE Error";
                    vscode.window.showErrorMessage(`WRE Failed to Start: ${result.error}`, 'View Logs', 'Retry').then(selection => {
                        if (selection === 'View Logs') {
                            wreIntegration.showLogs();
                        }
                        else if (selection === 'Retry') {
                            vscode.commands.executeCommand('claude-wre.runWRE');
                        }
                    });
                }
            }
            catch (error) {
                statusBarItem.text = "$(error) WRE Error";
                vscode.window.showErrorMessage(`WRE Error: ${error}`);
            }
        }),
        // WRE Status command
        vscode.commands.registerCommand('claude-wre.statusWRE', async () => {
            const status = await wreIntegration.getStatus();
            const panel = vscode.window.createWebviewPanel('wreStatus', 'WRE Status', vscode.ViewColumn.One, { enableScripts: true });
            panel.webview.html = generateStatusHTML(status);
        }),
        // Stop WRE command  
        vscode.commands.registerCommand('claude-wre.stopWRE', async () => {
            statusBarItem.text = "$(loading~spin) Stopping WRE...";
            const result = await wreIntegration.stopWRE();
            if (result.success) {
                statusBarItem.text = "$(rocket) WRE Ready";
                vscode.window.showInformationMessage('WRE Session Stopped');
            }
            else {
                statusBarItem.text = "$(error) WRE Error";
                vscode.window.showErrorMessage(`Failed to stop WRE: ${result.error}`);
            }
        }),
        // Configure WRE command
        vscode.commands.registerCommand('claude-wre.configWRE', async () => {
            await wreIntegration.openConfiguration();
        })
    ];
    // Register context menu for "Run WRE on File/Folder"
    const contextMenuCommand = vscode.commands.registerCommand('claude-wre.runWREOnContext', async (uri) => {
        if (uri) {
            await wreIntegration.runWREOnPath(uri.fsPath);
        }
    });
    // Add all disposables to context
    context.subscriptions.push(statusBarItem, ...commands, contextMenuCommand, wreIntegration);
    // Set up workspace change listeners
    vscode.workspace.onDidChangeWorkspaceFolders((e) => {
        wreIntegration.handleWorkspaceChange(e);
    });
    vscode.window.onDidChangeActiveTextEditor((editor) => {
        if (editor) {
            wreIntegration.handleFileChange(editor.document.uri.fsPath);
        }
    });
    console.log('Claude WRE Integration activated successfully');
}
exports.activate = activate;
function deactivate() {
    console.log('Claude WRE Integration deactivated');
}
exports.deactivate = deactivate;
function generateStatusHTML(status) {
    return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WRE Status</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 20px;
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
        }
        .status-section {
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 8px;
            background: var(--vscode-editor-inactiveSelectionBackground);
        }
        .status-header {
            font-weight: bold;
            font-size: 18px;
            margin-bottom: 10px;
            color: var(--vscode-textLink-foreground);
        }
        .status-item {
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
            padding: 5px 0;
            border-bottom: 1px solid var(--vscode-panel-border);
        }
        .status-value {
            font-weight: bold;
        }
        .success { color: var(--vscode-terminal-ansiGreen); }
        .error { color: var(--vscode-terminal-ansiRed); }
        .warning { color: var(--vscode-terminal-ansiYellow); }
        .info { color: var(--vscode-terminal-ansiBlue); }
    </style>
</head>
<body>
    <h1>🚀 WRE (Windsurf Recursive Engine) Status</h1>
    
    <div class="status-section">
        <div class="status-header">System Status</div>
        <div class="status-item">
            <span>WRE State:</span>
            <span class="status-value ${status.active ? 'success' : 'error'}">
                ${status.active ? '✅ ACTIVE' : '❌ INACTIVE'}
            </span>
        </div>
        <div class="status-item">
            <span>Session ID:</span>
            <span class="status-value info">${status.sessionId || 'None'}</span>
        </div>
        <div class="status-item">
            <span>Quantum State:</span>
            <span class="status-value success">${status.quantumState || '0102'}</span>
        </div>
    </div>

    <div class="status-section">
        <div class="status-header">12-Phase REMOTE_BUILD_PROTOTYPE Flow</div>
        <div class="status-item">
            <span>Current Phase:</span>
            <span class="status-value info">${status.currentPhase || 'Not Running'}</span>
        </div>
        <div class="status-item">
            <span>Phases Completed:</span>
            <span class="status-value success">${status.phasesCompleted || 0}/12</span>
        </div>
        <div class="status-item">
            <span>Autonomous Score:</span>
            <span class="status-value info">${status.autonomousScore || 0.0}</span>
        </div>
    </div>

    <div class="status-section">
        <div class="status-header">WSP Integration</div>
        <div class="status-item">
            <span>WSP_CORE Loaded:</span>
            <span class="status-value ${status.wspCoreLoaded ? 'success' : 'warning'}">
                ${status.wspCoreLoaded ? '✅ YES' : '⚠️ NO'}
            </span>
        </div>
        <div class="status-item">
            <span>Agent Suite Status:</span>
            <span class="status-value success">${status.agentSuiteStatus || 'WSP-54 Ready'}</span>
        </div>
        <div class="status-item">
            <span>Compliance Score:</span>
            <span class="status-value info">${status.complianceScore || 0.0}</span>
        </div>
    </div>

    <div class="status-section">
        <div class="status-header">Claude Code Integration</div>
        <div class="status-item">
            <span>Communication:</span>
            <span class="status-value ${status.communicationActive ? 'success' : 'warning'}">
                ${status.communicationActive ? '✅ WebSocket Active' : '⚠️ Establishing...'}
            </span>
        </div>
        <div class="status-item">
            <span>Context Sync:</span>
            <span class="status-value info">${status.contextSync ? '✅ Synchronized' : '⚠️ Pending'}</span>
        </div>
    </div>
</body>
</html>`;
}
//# sourceMappingURL=extension.js.map