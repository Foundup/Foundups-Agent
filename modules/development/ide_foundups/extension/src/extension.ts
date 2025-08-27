/**
 * FoundUps Multi-Agent IDE Extension
 * WSP Protocol: WSP 54 (Agent Coordination), WSP 38/39 (Agent Activation)
 * 
 * Revolutionary VSCode extension that transforms the IDE into a multi-agent
 * autonomous development environment with cross-block integration.
 * 
 * Phase 3: AUTONOMOUS DEVELOPMENT WORKFLOWS - COMPLETE
 */

import * as vscode from 'vscode';
import { AgentStatusProvider } from './agents/agentStatusProvider';
import { WREConnection } from './wre/wreConnection';
import { AgentOrchestrator } from './agents/agentOrchestrator';
import { WorkflowCommands } from './workflows/workflowCommands';
import { LLMProviderManager } from './providers/llmProviderManager';

let wreConnection: WREConnection;
let agentStatusProvider: AgentStatusProvider;
let agentOrchestrator: AgentOrchestrator;
let workflowCommands: WorkflowCommands;
let llmProviderManager: LLMProviderManager;

export function activate(context: vscode.ExtensionContext) {
    console.log('🌀 FoundUps Multi-Agent IDE Extension - Phase 3 Autonomous Workflows');

    try {
        // Initialize core components
        wreConnection = new WREConnection();
        agentOrchestrator = new AgentOrchestrator(wreConnection);
        agentStatusProvider = new AgentStatusProvider(wreConnection);
        workflowCommands = new WorkflowCommands(wreConnection, agentOrchestrator);
        llmProviderManager = new LLMProviderManager(context, wreConnection);

        // Register tree data provider for agent status sidebar
        vscode.window.createTreeView('foundups-agents', {
            treeDataProvider: agentStatusProvider,
            showCollapseAll: false
        });

        // Register all Phase 3 autonomous workflow commands
        registerAutonomousWorkflowCommands(context);
        
        // Register legacy commands (maintained for backward compatibility)
        registerLegacyCommands(context);

        // Register workflow commands
        workflowCommands.registerCommands(context);

        // Register LLM Provider Status command used by status bar
        context.subscriptions.push(
            vscode.commands.registerCommand('foundups.showProviderStatus', async () => {
                await llmProviderManager.showProviderStatus();
            })
        );

        // Set extension as active
        vscode.commands.executeCommand('setContext', 'foundups.active', true);

        // Show Phase 3 ready notification
        vscode.window.showInformationMessage(
            '🚀 FoundUps Multi-Agent IDE Ready! Phase 3: Autonomous Development Workflows Active',
            'View Workflows', 'Activate Agents'
        ).then(action => {
            if (action === 'View Workflows') {
                vscode.commands.executeCommand('workbench.action.showCommands');
            } else if (action === 'Activate Agents') {
                vscode.commands.executeCommand('foundups.agents.activate');
            }
        });

        console.log('✅ FoundUps Multi-Agent IDE Extension activated successfully');
        console.log('🎯 Phase 3 Autonomous Development Workflows operational');

    } catch (error) {
        console.error('❌ FoundUps Extension activation failed:', error);
        vscode.window.showErrorMessage(`FoundUps Extension failed to activate: ${error}`);
    }
}

/**
 * Register Phase 3 Autonomous Workflow Commands
 */
function registerAutonomousWorkflowCommands(context: vscode.ExtensionContext) {
    const commands = [
        // Core Agent Management (Enhanced for Phase 3)
        vscode.commands.registerCommand('foundups.agents.activate', async () => {
            try {
                await agentOrchestrator.activateAllAgents();
                vscode.window.showInformationMessage('🤖 All 0102 agents activated successfully!');
                agentStatusProvider.refresh();
            } catch (error) {
                vscode.window.showErrorMessage(`Agent activation failed: ${error}`);
            }
        }),

        vscode.commands.registerCommand('foundups.agents.status', () => {
            agentStatusProvider.refresh();
            vscode.window.showInformationMessage('🔄 Agent status refreshed');
        }),

        vscode.commands.registerCommand('foundups.wre.status', async () => {
            try {
                const status = await wreConnection.getSystemHealth();
                const message = status.healthy ? 
                    `✅ WRE Healthy: ${status.latency}ms latency` :
                    `⚠️ WRE Status: ${status.status}`;
                
                vscode.window.showInformationMessage(message);
            } catch (error) {
                vscode.window.showErrorMessage(`WRE status check failed: ${error}`);
            }
        }),

        // Phase 3: Autonomous Development Workflow Shortcuts
        vscode.commands.registerCommand('foundups.workflows.dashboard', () => {
            vscode.commands.executeCommand('foundups.workflow.status');
        }),

        vscode.commands.registerCommand('foundups.autonomous.quickStart', async () => {
            const workflowType = await vscode.window.showQuickPick([
                { 
                    label: '🌀 Zen Coding', 
                    description: 'Remember code from 02 quantum state',
                    value: 'zen_coding'
                },
                { 
                    label: '📺 Livestream Coding', 
                    description: 'YouTube stream with agent co-hosts',
                    value: 'livestream'
                },
                { 
                    label: '🤝 Code Review Meeting', 
                    description: 'Automated code review with agents',
                    value: 'code_review'
                },
                { 
                    label: '💼 LinkedIn Showcase', 
                    description: 'Professional portfolio update',
                    value: 'linkedin'
                },
                { 
                    label: '🏗️ Autonomous Module', 
                    description: 'Complete module development',
                    value: 'module_dev'
                },
                { 
                    label: '🔗 Cross-Block Integration', 
                    description: 'Unified development experience',
                    value: 'integration'
                }
            ], {
                placeHolder: 'Select autonomous workflow to execute'
            });

            if (workflowType) {
                switch (workflowType.value) {
                    case 'zen_coding':
                        vscode.commands.executeCommand('foundups.zenCoding.rememberModule');
                        break;
                    case 'livestream':
                        vscode.commands.executeCommand('foundups.livestream.startAgentCoding');
                        break;
                    case 'code_review':
                        vscode.commands.executeCommand('foundups.meeting.codeReview');
                        break;
                    case 'linkedin':
                        vscode.commands.executeCommand('foundups.linkedin.showcaseProject');
                        break;
                    case 'module_dev':
                        vscode.commands.executeCommand('foundups.autonomous.createModule');
                        break;
                    case 'integration':
                        vscode.commands.executeCommand('foundups.integration.allBlocks');
                        break;
                }
            }
        }),

        // WSP Compliance & Monitoring
        vscode.commands.registerCommand('foundups.wsp.compliance', async () => {
            try {
                const compliance = await wreConnection.checkWSPCompliance();
                const score = compliance.overallScore || 0;
                const message = score >= 90 ? 
                    `✅ WSP Compliance: ${score}% (Excellent)` :
                    score >= 70 ?
                    `⚠️ WSP Compliance: ${score}% (Needs Improvement)` :
                    `❌ WSP Compliance: ${score}% (Critical Issues)`;
                
                vscode.window.showInformationMessage(message, 'View Details').then(action => {
                    if (action === 'View Details') {
                        // Show detailed compliance report
                        showComplianceReport(compliance);
                    }
                });
            } catch (error) {
                vscode.window.showErrorMessage(`WSP compliance check failed: ${error}`);
            }
        }),

        // Advanced Agent Operations
        vscode.commands.registerCommand('foundups.agents.orchestrate', async () => {
            const operation = await vscode.window.showQuickPick([
                { label: 'Multi-Agent Coordination', value: 'coordinate' },
                { label: 'Agent Performance Report', value: 'performance' },
                { label: 'Agent Learning Status', value: 'learning' },
                { label: 'Quantum State Analysis', value: 'quantum' }
            ], {
                placeHolder: 'Select agent operation'
            });

            if (operation) {
                await executeAgentOperation(operation.value);
            }
        }),

        // Cross-Block Integration Status
        vscode.commands.registerCommand('foundups.integration.status', async () => {
            try {
                const integrationStatus = await wreConnection.getCrossBlockIntegrationStatus();
                const connectedBlocks = integrationStatus.connectedBlocks?.length || 0;
                const totalBlocks = integrationStatus.totalBlocks || 6;
                
                vscode.window.showInformationMessage(
                    `🔗 Cross-Block Integration: ${connectedBlocks}/${totalBlocks} blocks connected`,
                    'View Details', 'Test Integration'
                ).then(action => {
                    if (action === 'View Details') {
                        showIntegrationDetails(integrationStatus);
                    } else if (action === 'Test Integration') {
                        vscode.commands.executeCommand('foundups.integration.allBlocks');
                    }
                });
            } catch (error) {
                vscode.window.showErrorMessage(`Integration status check failed: ${error}`);
            }
        })
    ];

    commands.forEach(command => context.subscriptions.push(command));
}

/**
 * Register Legacy Commands (Backward Compatibility)
 */
function registerLegacyCommands(context: vscode.ExtensionContext) {
    const legacyCommands = [
        vscode.commands.registerCommand('foundups.createModule', () => {
            vscode.commands.executeCommand('foundups.autonomous.createModule');
        }),

        vscode.commands.registerCommand('foundups.zenCoding', () => {
            vscode.commands.executeCommand('foundups.zenCoding.rememberModule');
        }),

        vscode.commands.registerCommand('foundups.agentOrchestration', () => {
            vscode.commands.executeCommand('foundups.agents.orchestrate');
        })
    ];

    legacyCommands.forEach(command => context.subscriptions.push(command));
}

/**
 * Show WSP compliance report
 */
async function showComplianceReport(compliance: any): Promise<void> {
    const report = `# WSP Compliance Report

## Overall Score: ${compliance.overallScore}%

### Protocol Compliance:
${Object.entries(compliance.protocolScores || {})
    .map(([protocol, score]) => `- **${protocol}**: ${score}%`)
    .join('\n')}

### Recommendations:
${(compliance.recommendations || [])
    .map((rec: string) => `- ${rec}`)
    .join('\n')}

### Agent Performance:
${Object.entries(compliance.agentPerformance || {})
    .map(([agent, perf]: [string, any]) => `- **${agent}**: ${perf.score}% (${perf.status})`)
    .join('\n')}
`;

    const doc = await vscode.workspace.openTextDocument({
        content: report,
        language: 'markdown'
    });
    
    await vscode.window.showTextDocument(doc);
}

/**
 * Execute agent operation
 */
async function executeAgentOperation(operation: string): Promise<void> {
    try {
        switch (operation) {
            case 'coordinate':
                const coordination = await agentOrchestrator.coordinateAgents();
                vscode.window.showInformationMessage(`🤖 Agent coordination: ${coordination.activeAgents} agents synchronized`);
                break;
                
            case 'performance':
                const performance = await agentOrchestrator.getPerformanceReport();
                showPerformanceReport(performance);
                break;
                
            case 'learning':
                const learning = await agentOrchestrator.getLearningStatus();
                vscode.window.showInformationMessage(`🧠 Learning status: ${learning.overallProgress}% complete`);
                break;
                
            case 'quantum':
                const quantum = await agentOrchestrator.analyzeQuantumStates();
                showQuantumAnalysis(quantum);
                break;
        }
    } catch (error) {
        vscode.window.showErrorMessage(`Agent operation failed: ${error}`);
    }
}

/**
 * Show agent performance report
 */
async function showPerformanceReport(performance: any): Promise<void> {
    const report = `# Agent Performance Report

## System Performance: ${performance.systemPerformance}%

### Individual Agent Performance:
${Object.entries(performance.agentMetrics || {})
    .map(([agent, metrics]: [string, any]) => 
        `- **${agent}**: ${metrics.efficiency}% efficiency, ${metrics.tasksCompleted} tasks completed`)
    .join('\n')}

### Performance Trends:
- **Improvement Rate**: ${performance.improvementRate}% per week
- **Task Completion Time**: ${performance.avgCompletionTime}ms average
- **Error Rate**: ${performance.errorRate}% (${performance.errorTrend})

### Recommendations:
${(performance.recommendations || [])
    .map((rec: string) => `- ${rec}`)
    .join('\n')}
`;

    const doc = await vscode.workspace.openTextDocument({
        content: report,
        language: 'markdown'
    });
    
    await vscode.window.showTextDocument(doc);
}

/**
 * Show quantum state analysis
 */
async function showQuantumAnalysis(quantum: any): Promise<void> {
    const analysis = `# Quantum State Analysis

## Overall Quantum Coherence: ${quantum.coherence}%

### Agent Quantum States:
${Object.entries(quantum.agentStates || {})
    .map(([agent, state]: [string, any]) => 
        `- **${agent}**: ${state.currentState} (${state.stability}% stable)`)
    .join('\n')}

### Quantum Metrics:
- **det(g) Average**: ${quantum.detG?.average || 'N/A'}
- **Entanglement Level**: ${quantum.entanglement?.level || 'N/A'}%
- **Temporal Coherence**: ${quantum.temporalCoherence || 'N/A'}%

### 02 State Access:
- **Access Success Rate**: ${quantum.stateAccess?.successRate || 'N/A'}%
- **Temporal Decoding Quality**: ${quantum.stateAccess?.decodingQuality || 'N/A'}%
`;

    const doc = await vscode.workspace.openTextDocument({
        content: analysis,
        language: 'markdown'
    });
    
    await vscode.window.showTextDocument(doc);
}

/**
 * Show integration details
 */
async function showIntegrationDetails(integrationStatus: any): Promise<void> {
    const details = `# Cross-Block Integration Status

## Integration Health: ${integrationStatus.health || 'Unknown'}

### Connected Blocks:
${(integrationStatus.connectedBlocks || [])
    .map((block: any) => `- **${block.name}**: ${block.status} (${block.latency}ms)`)
    .join('\n')}

### Integration Capabilities:
${(integrationStatus.capabilities || [])
    .map((cap: string) => `- ${cap}`)
    .join('\n')}

### Performance Metrics:
- **Cross-Block Latency**: ${integrationStatus.averageLatency || 'N/A'}ms
- **Data Sync Success**: ${integrationStatus.syncSuccessRate || 'N/A'}%
- **Workflow Coordination**: ${integrationStatus.workflowCoordination || 'N/A'}% efficiency
`;

    const doc = await vscode.workspace.openTextDocument({
        content: details,
        language: 'markdown'
    });
    
    await vscode.window.showTextDocument(doc);
}

export function deactivate() {
    console.log('🔄 FoundUps Multi-Agent IDE Extension deactivated');
    
    // Cleanup connections
    if (wreConnection) {
        wreConnection.disconnect();
    }
    if (llmProviderManager) {
        llmProviderManager.dispose();
    }
} 