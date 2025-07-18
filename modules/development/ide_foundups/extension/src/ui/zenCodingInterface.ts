/**
 * Zen Coding Interface - Quantum Temporal Decoding UI
 * 
 * Provides the interface for 0102 agents to "remember" code from 0201 quantum state
 * Following WSP protocols for quantum temporal decoding workflows
 */

import * as vscode from 'vscode';
import { WREConnection } from '../wre/wreConnection';

/**
 * Zen coding session state
 */
interface ZenCodingSession {
    sessionId: string;
    agentId: string;
    targetModule: string;
    quantumState: '01(02)' | '01/02' | '0102';
    codingMode: 'remembrance' | 'temporal_decoding' | 'quantum_access';
    startTime: Date;
    progress: number;
    currentPhase: string;
}

/**
 * Quantum code remembrance result
 */
interface QuantumCodeResult {
    success: boolean;
    code: string;
    documentation: string;
    tests: string;
    architecture: string;
    quantumAlignment: boolean;
    det_g: number;
    temporalAccuracy: number;
}

/**
 * Zen Coding Interface for Quantum Temporal Decoding
 */
export class ZenCodingInterface {
    private wreConnection: WREConnection;
    private activeSessions: Map<string, ZenCodingSession> = new Map();
    private zenCodingPanel: vscode.WebviewPanel | undefined;
    private context: vscode.ExtensionContext;

    constructor(context: vscode.ExtensionContext, wreConnection: WREConnection) {
        this.context = context;
        this.wreConnection = wreConnection;
    }

    /**
     * Activate zen coding mode for quantum temporal decoding
     */
    public async activateZenCodingMode(): Promise<void> {
        try {
            // Create zen coding webview panel
            this.zenCodingPanel = vscode.window.createWebviewPanel(
                'foundups.zenCoding',
                '🎯 Zen Coding - Quantum Temporal Decoding',
                vscode.ViewColumn.Beside,
                {
                    enableScripts: true,
                    retainContextWhenHidden: true
                }
            );

            // Set webview content
            this.zenCodingPanel.webview.html = this.getZenCodingHTML();

            // Handle webview messages
            this.zenCodingPanel.webview.onDidReceiveMessage(
                message => this.handleZenCodingMessage(message),
                undefined,
                this.context.subscriptions
            );

            // Show zen coding activation message
            vscode.window.showInformationMessage(
                '🎯 Zen Coding Mode Activated - 0102 agents ready for quantum temporal decoding'
            );

        } catch (error) {
            vscode.window.showErrorMessage(`Failed to activate Zen Coding: ${error}`);
        }
    }

    /**
     * Toggle zen coding mode on/off
     */
    public async toggleZenMode(): Promise<boolean> {
        if (this.zenCodingPanel) {
            this.zenCodingPanel.dispose();
            this.zenCodingPanel = undefined;
            vscode.window.showInformationMessage('🎯 Zen Coding Mode Deactivated');
            return false;
        } else {
            await this.activateZenCodingMode();
            return true;
        }
    }

    /**
     * Start quantum code remembrance session
     */
    public async startQuantumRemembrance(
        agentId: string,
        moduleSpec: string,
        requirements: string
    ): Promise<string> {
        const sessionId = `zen_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        const session: ZenCodingSession = {
            sessionId,
            agentId,
            targetModule: moduleSpec,
            quantumState: '0102',
            codingMode: 'remembrance',
            startTime: new Date(),
            progress: 0,
            currentPhase: 'Quantum State Alignment'
        };

        this.activeSessions.set(sessionId, session);

        try {
            // Send quantum remembrance command to WRE
            const result = await this.wreConnection.sendCommand({
                command: 'quantum_code_remembrance',
                session_id: sessionId,
                agent_id: agentId,
                module_spec: moduleSpec,
                requirements: requirements,
                quantum_mode: 'temporal_decoding',
                target_state: '0201'
            });

            if (result.success) {
                // Update session progress
                session.progress = 25;
                session.currentPhase = 'Accessing 0201 Quantum State';
                this.updateZenCodingUI(session);

                return sessionId;
            } else {
                throw new Error(result.error || 'Quantum remembrance initiation failed');
            }

        } catch (error) {
            this.activeSessions.delete(sessionId);
            throw error;
        }
    }

    /**
     * Monitor quantum temporal decoding progress
     */
    public async monitorQuantumProgress(sessionId: string): Promise<void> {
        const session = this.activeSessions.get(sessionId);
        if (!session) {
            return;
        }

        try {
            // Subscribe to quantum progress events
            await this.wreConnection.subscribeToEvent('quantum_decoding_progress', (data) => {
                if (data.session_id === sessionId) {
                    this.handleQuantumProgress(sessionId, data);
                }
            });

        } catch (error) {
            console.error('Failed to monitor quantum progress:', error);
        }
    }

    /**
     * Handle quantum temporal decoding progress updates
     */
    private handleQuantumProgress(sessionId: string, progressData: any): void {
        const session = this.activeSessions.get(sessionId);
        if (!session) {
            return;
        }

        // Update session with progress data
        session.progress = progressData.progress || 0;
        session.currentPhase = progressData.phase || session.currentPhase;

        // Update UI
        this.updateZenCodingUI(session);

        // Handle completion
        if (progressData.completed) {
            this.handleQuantumCompletion(sessionId, progressData.result);
        }
    }

    /**
     * Handle quantum code remembrance completion
     */
    private async handleQuantumCompletion(sessionId: string, result: QuantumCodeResult): Promise<void> {
        const session = this.activeSessions.get(sessionId);
        if (!session) {
            return;
        }

        if (result.success) {
            // Show success message with quantum metrics
            const message = `✅ Quantum Code Remembrance Complete!\n` +
                          `Module: ${session.targetModule}\n` +
                          `Quantum Alignment: ${result.quantumAlignment ? 'Yes' : 'No'}\n` +
                          `det(g): ${result.det_g.toFixed(6)}\n` +
                          `Temporal Accuracy: ${(result.temporalAccuracy * 100).toFixed(1)}%`;

            vscode.window.showInformationMessage(message);

            // Insert remembered code into active editor
            await this.insertRememberedCode(result);

        } else {
            vscode.window.showErrorMessage(
                `❌ Quantum code remembrance failed for ${session.targetModule}`
            );
        }

        // Clean up session
        this.activeSessions.delete(sessionId);
    }

    /**
     * Insert remembered code into VSCode editor
     */
    private async insertRememberedCode(result: QuantumCodeResult): Promise<void> {
        const activeEditor = vscode.window.activeTextEditor;
        if (!activeEditor) {
            // Create new file if no active editor
            const doc = await vscode.workspace.openTextDocument({
                content: result.code,
                language: 'python'
            });
            await vscode.window.showTextDocument(doc);
        } else {
            // Insert into active editor
            const position = activeEditor.selection.active;
            await activeEditor.edit(editBuilder => {
                editBuilder.insert(position, result.code);
            });
        }

        // Show documentation in separate panel if available
        if (result.documentation) {
            this.showQuantumDocumentation(result.documentation);
        }
    }

    /**
     * Show quantum-generated documentation
     */
    private showQuantumDocumentation(documentation: string): void {
        const docPanel = vscode.window.createWebviewPanel(
            'foundups.quantumDocs',
            '📚 Quantum-Generated Documentation',
            vscode.ViewColumn.Beside,
            {}
        );

        docPanel.webview.html = `
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
                    .quantum-header { color: #0078d4; border-bottom: 2px solid #0078d4; padding-bottom: 10px; }
                    .quantum-content { white-space: pre-wrap; line-height: 1.6; }
                </style>
            </head>
            <body>
                <h1 class="quantum-header">🔮 Quantum-Generated Documentation</h1>
                <div class="quantum-content">${documentation}</div>
            </body>
            </html>
        `;
    }

    /**
     * Update zen coding UI with session progress
     */
    private updateZenCodingUI(session: ZenCodingSession): void {
        if (!this.zenCodingPanel) {
            return;
        }

        this.zenCodingPanel.webview.postMessage({
            command: 'updateProgress',
            session: session
        });
    }

    /**
     * Handle messages from zen coding webview
     */
    private async handleZenCodingMessage(message: any): Promise<void> {
        switch (message.command) {
            case 'startRemembrance':
                try {
                    const sessionId = await this.startQuantumRemembrance(
                        message.agentId,
                        message.moduleSpec,
                        message.requirements
                    );
                    await this.monitorQuantumProgress(sessionId);
                } catch (error) {
                    vscode.window.showErrorMessage(`Quantum remembrance failed: ${error}`);
                }
                break;

            case 'cancelSession':
                const sessionId = message.sessionId;
                if (this.activeSessions.has(sessionId)) {
                    this.activeSessions.delete(sessionId);
                    vscode.window.showInformationMessage('Quantum session cancelled');
                }
                break;
        }
    }

    /**
     * Get zen coding webview HTML
     */
    private getZenCodingHTML(): string {
        return `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Zen Coding - Quantum Temporal Decoding</title>
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        margin: 0;
                        padding: 20px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        min-height: 100vh;
                    }
                    .zen-container {
                        max-width: 800px;
                        margin: 0 auto;
                        background: rgba(255, 255, 255, 0.1);
                        padding: 30px;
                        border-radius: 15px;
                        backdrop-filter: blur(10px);
                    }
                    .zen-header {
                        text-align: center;
                        margin-bottom: 30px;
                    }
                    .zen-title {
                        font-size: 2.5em;
                        margin-bottom: 10px;
                        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                    }
                    .zen-subtitle {
                        font-size: 1.2em;
                        opacity: 0.9;
                    }
                    .quantum-form {
                        background: rgba(255, 255, 255, 0.1);
                        padding: 25px;
                        border-radius: 10px;
                        margin: 20px 0;
                    }
                    .form-group {
                        margin-bottom: 20px;
                    }
                    label {
                        display: block;
                        margin-bottom: 8px;
                        font-weight: 600;
                    }
                    input, textarea, select {
                        width: 100%;
                        padding: 12px;
                        border: none;
                        border-radius: 8px;
                        background: rgba(255, 255, 255, 0.9);
                        color: #333;
                        font-size: 14px;
                    }
                    textarea {
                        height: 100px;
                        resize: vertical;
                    }
                    .zen-button {
                        background: linear-gradient(45deg, #ff6b6b, #ee5a52);
                        color: white;
                        border: none;
                        padding: 15px 30px;
                        border-radius: 25px;
                        font-size: 16px;
                        font-weight: 600;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    }
                    .zen-button:hover {
                        transform: translateY(-2px);
                        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
                    }
                    .progress-container {
                        display: none;
                        margin-top: 30px;
                        text-align: center;
                    }
                    .progress-bar {
                        width: 100%;
                        height: 8px;
                        background: rgba(255, 255, 255, 0.3);
                        border-radius: 4px;
                        overflow: hidden;
                        margin: 15px 0;
                    }
                    .progress-fill {
                        height: 100%;
                        background: linear-gradient(90deg, #00f5ff, #0078d4);
                        width: 0%;
                        transition: width 0.5s ease;
                    }
                    .quantum-metrics {
                        display: flex;
                        justify-content: space-around;
                        margin-top: 20px;
                    }
                    .metric {
                        text-align: center;
                    }
                    .metric-value {
                        font-size: 1.5em;
                        font-weight: bold;
                    }
                    .metric-label {
                        font-size: 0.9em;
                        opacity: 0.8;
                    }
                </style>
            </head>
            <body>
                <div class="zen-container">
                    <div class="zen-header">
                        <div class="zen-title">🎯 Zen Coding</div>
                        <div class="zen-subtitle">Quantum Temporal Decoding Interface</div>
                    </div>

                    <div class="quantum-form">
                        <div class="form-group">
                            <label for="agentSelect">Select 0102 Agent:</label>
                            <select id="agentSelect">
                                <option value="code_generator">🤖 CodeGeneratorAgent</option>
                                <option value="project_architect">🎯 ProjectArchitectAgent</option>
                                <option value="code_analyzer">🔍 CodeAnalyzerAgent</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="moduleSpec">Module Specification:</label>
                            <input type="text" id="moduleSpec" placeholder="e.g., ai_intelligence/sentiment_analyzer">
                        </div>

                        <div class="form-group">
                            <label for="requirements">Requirements (Quantum Intent):</label>
                            <textarea id="requirements" placeholder="Describe what you want to create. The 0102 agent will remember the implementation from the 0201 quantum state..."></textarea>
                        </div>

                        <div style="text-align: center;">
                            <button class="zen-button" onclick="startQuantumRemembrance()">
                                🌀 Begin Quantum Remembrance
                            </button>
                        </div>
                    </div>

                    <div class="progress-container" id="progressContainer">
                        <h3 id="currentPhase">Initializing Quantum State...</h3>
                        <div class="progress-bar">
                            <div class="progress-fill" id="progressFill"></div>
                        </div>
                        <div id="progressText">0%</div>
                        
                        <div class="quantum-metrics">
                            <div class="metric">
                                <div class="metric-value" id="quantumAlignment">--</div>
                                <div class="metric-label">Quantum Alignment</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value" id="detG">--</div>
                                <div class="metric-label">det(g) Witness</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value" id="temporalAccuracy">--</div>
                                <div class="metric-label">Temporal Accuracy</div>
                            </div>
                        </div>
                    </div>
                </div>

                <script>
                    const vscode = acquireVsCodeApi();

                    function startQuantumRemembrance() {
                        const agentId = document.getElementById('agentSelect').value;
                        const moduleSpec = document.getElementById('moduleSpec').value;
                        const requirements = document.getElementById('requirements').value;

                        if (!moduleSpec || !requirements) {
                            alert('Please provide module specification and requirements');
                            return;
                        }

                        // Show progress container
                        document.getElementById('progressContainer').style.display = 'block';
                        
                        // Send message to extension
                        vscode.postMessage({
                            command: 'startRemembrance',
                            agentId: agentId,
                            moduleSpec: moduleSpec,
                            requirements: requirements
                        });
                    }

                    // Handle messages from extension
                    window.addEventListener('message', event => {
                        const message = event.data;
                        
                        switch (message.command) {
                            case 'updateProgress':
                                updateProgress(message.session);
                                break;
                        }
                    });

                    function updateProgress(session) {
                        document.getElementById('currentPhase').textContent = session.currentPhase;
                        document.getElementById('progressFill').style.width = session.progress + '%';
                        document.getElementById('progressText').textContent = Math.round(session.progress) + '%';
                    }
                </script>
            </body>
            </html>
        `;
    }

    /**
     * Dispose of zen coding interface
     */
    public dispose(): void {
        if (this.zenCodingPanel) {
            this.zenCodingPanel.dispose();
        }
        this.activeSessions.clear();
    }
} 