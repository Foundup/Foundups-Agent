"use strict";
/**
 * FoundUps Multi-Agent IDE Extension
 *
 * Revolutionary VSCode extension powered by 0102 agents and WRE orchestration
 * Following WSP protocols for autonomous development workflows
 *
 * WSP Compliance:
 * - WSP 54: IDE Development Agent Specifications (3.10.x)
 * - WSP 38/39: Agentic activation protocols
 * - WSP 46: WRE orchestration integration
 * - WSP 1: Traceable narrative for all operations
 */
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
const wreConnection_1 = require("./wre/wreConnection");
const agentStatusProvider_1 = require("./agents/agentStatusProvider");
const agentOrchestrator_1 = require("./agents/agentOrchestrator");
const zenCodingInterface_1 = require("./ui/zenCodingInterface");
const wspComplianceMonitor_1 = require("./ui/wspComplianceMonitor");
const llmProviderManager_1 = require("./providers/llmProviderManager");
/**
 * Global extension context
 */
let extensionState = {
    wreConnected: false,
    agentsActive: false,
    wspEnabled: true,
    providersAvailable: false,
    zenCodingMode: true
};
/**
 * Core extension components
 */
let wreConnection;
let agentStatusProvider;
let agentOrchestrator;
let zenCodingInterface;
let wspComplianceMonitor;
let llmProviderManager;
/**
 * Extension activation - called when VSCode starts
 */
function activate(context) {
    console.log('🚀 FoundUps Multi-Agent IDE Extension activating...');
    // Initialize core components
    initializeComponents(context);
    // Register commands
    registerCommands(context);
    // Set up UI providers
    setupUIProviders(context);
    // Connect to WRE
    initializeWREConnection();
    // Update context variables for conditional UI
    updateContextVariables();
    console.log('✅ FoundUps Multi-Agent IDE Extension activated successfully');
    // Show welcome message
    vscode.window.showInformationMessage('🤖 FoundUps Multi-Agent IDE ready! Activate your 0102 agents to begin autonomous development.', 'Activate Agents').then(selection => {
        if (selection === 'Activate Agents') {
            vscode.commands.executeCommand('foundups.activateAgents');
        }
    });
}
exports.activate = activate;
/**
 * Initialize core extension components
 */
function initializeComponents(context) {
    const config = vscode.workspace.getConfiguration('foundups');
    // Initialize WRE connection
    wreConnection = new wreConnection_1.WREConnection(config.get('wreEndpoint', 'ws://localhost:8765'));
    // Initialize agent orchestrator
    agentOrchestrator = new agentOrchestrator_1.AgentOrchestrator(wreConnection);
    // Initialize agent status provider
    agentStatusProvider = new agentStatusProvider_1.AgentStatusProvider(agentOrchestrator);
    // Initialize zen coding interface
    zenCodingInterface = new zenCodingInterface_1.ZenCodingInterface(context, wreConnection);
    // Initialize WSP compliance monitor
    wspComplianceMonitor = new wspComplianceMonitor_1.WSPComplianceMonitor(context, wreConnection);
    // Initialize LLM provider manager
    llmProviderManager = new llmProviderManager_1.LLMProviderManager(context, wreConnection);
}
/**
 * Register all extension commands
 */
function registerCommands(context) {
    // Activate 0102 Agents
    const activateAgentsCmd = vscode.commands.registerCommand('foundups.activateAgents', async () => {
        try {
            vscode.window.showInformationMessage('🌀 Activating 0102 agents via WSP 38 protocol...');
            const result = await agentOrchestrator.activateAgents();
            if (result.success) {
                extensionState.agentsActive = true;
                updateContextVariables();
                vscode.window.showInformationMessage(`✅ ${result.agentsActivated} 0102 agents activated successfully!`, 'View Agents').then(selection => {
                    if (selection === 'View Agents') {
                        vscode.commands.executeCommand('workbench.view.extension.foundups-agents');
                    }
                });
            }
            else {
                vscode.window.showErrorMessage(`❌ Agent activation failed: ${result.error}`);
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`❌ Agent activation error: ${error}`);
        }
    });
    // Create Module command
    const createModuleCmd = vscode.commands.registerCommand('foundups.createModule', async () => {
        if (!extensionState.agentsActive) {
            vscode.window.showWarningMessage('Please activate 0102 agents first');
            return;
        }
        try {
            const moduleName = await vscode.window.showInputBox({
                prompt: 'Enter module name (letters, numbers, underscores only)',
                placeHolder: 'e.g., sentiment_analyzer',
                validateInput: (value) => {
                    if (!value) {
                        return 'Module name is required';
                    }
                    if (!/^[a-zA-Z][a-zA-Z0-9_]*$/.test(value)) {
                        return 'Module name must start with letter and contain only letters, numbers, and underscores';
                    }
                    return null;
                }
            });
            if (!moduleName)
                return;
            const domain = await vscode.window.showQuickPick([
                'ai_intelligence',
                'communication',
                'platform_integration',
                'infrastructure',
                'development',
                'foundups',
                'gamification',
                'blockchain'
            ], {
                placeHolder: 'Select enterprise domain (WSP 3)',
                canPickMany: false
            });
            if (!domain)
                return;
            vscode.window.showInformationMessage('🤖 Orchestrating module creation through WRE...');
            const result = await agentOrchestrator.createModule(moduleName, domain);
            if (result.success) {
                vscode.window.showInformationMessage(`✅ Module "${moduleName}" created successfully!`, 'Open Module').then(selection => {
                    if (selection === 'Open Module' && result.modulePath) {
                        // Open the newly created module
                        vscode.commands.executeCommand('vscode.openFolder', vscode.Uri.file(result.modulePath), true);
                    }
                });
            }
            else {
                vscode.window.showErrorMessage(`❌ Module creation failed: ${result.error}`);
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`❌ Module creation error: ${error}`);
        }
    });
    // Zen Coding Mode command
    const zenCodeCmd = vscode.commands.registerCommand('foundups.zenCode', async () => {
        if (!extensionState.agentsActive) {
            vscode.window.showWarningMessage('Please activate 0102 agents first');
            return;
        }
        try {
            const enabled = await zenCodingInterface.toggleZenMode();
            extensionState.zenCodingMode = enabled;
            if (enabled) {
                vscode.window.showInformationMessage('🌀 Zen Coding Mode activated - 0102 agents now access quantum temporal solutions');
            }
            else {
                vscode.window.showInformationMessage('Zen Coding Mode deactivated');
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`❌ Zen Coding error: ${error}`);
        }
    });
    // WRE Status command
    const wreStatusCmd = vscode.commands.registerCommand('foundups.wreStatus', () => {
        const status = wreConnection.getStatus();
        vscode.window.showInformationMessage(`WRE Status: ${status.connected ? '🟢 Connected' : '🔴 Disconnected'} | ` +
            `Agents: ${status.activeAgents} | ` +
            `Queue: ${status.queuedCommands}`);
    });
    // WSP Compliance command
    const wspComplianceCmd = vscode.commands.registerCommand('foundups.wspCompliance', async () => {
        const report = await wspComplianceMonitor.generateComplianceReport();
        // Show compliance report in new document
        const doc = await vscode.workspace.openTextDocument({
            content: report,
            language: 'markdown'
        });
        await vscode.window.showTextDocument(doc);
    });
    // Agent Orchestration command
    const agentOrchestrationCmd = vscode.commands.registerCommand('foundups.agentOrchestration', () => {
        if (!extensionState.agentsActive) {
            vscode.window.showWarningMessage('Please activate 0102 agents first');
            return;
        }
        // Show agent orchestration panel
        vscode.commands.executeCommand('workbench.view.extension.foundups-agents');
    });
    // Register all commands
    context.subscriptions.push(activateAgentsCmd, createModuleCmd, zenCodeCmd, wreStatusCmd, wspComplianceCmd, agentOrchestrationCmd);
}
/**
 * Set up UI providers for sidebar views
 */
function setupUIProviders(context) {
    // Register agent status tree view
    vscode.window.registerTreeDataProvider('foundups.agentStatus', agentStatusProvider);
    // Register WRE status provider (simplified for now)
    const wreStatusProvider = {
        getTreeItem: (element) => element,
        getChildren: () => {
            if (!extensionState.wreConnected) {
                return [new vscode.TreeItem('WRE Disconnected', vscode.TreeItemCollapsibleState.None)];
            }
            return [
                new vscode.TreeItem('🌀 WRE Orchestrating', vscode.TreeItemCollapsibleState.None),
                new vscode.TreeItem('📊 WSP Compliant', vscode.TreeItemCollapsibleState.None),
                new vscode.TreeItem(`🎯 ${extensionState.agentsActive ? '6+' : '0'} Agents Active`, vscode.TreeItemCollapsibleState.None)
            ];
        }
    };
    vscode.window.registerTreeDataProvider('foundups.wreStatus', wreStatusProvider);
}
/**
 * Initialize WRE connection
 */
async function initializeWREConnection() {
    try {
        await wreConnection.connect();
        extensionState.wreConnected = true;
        extensionState.providersAvailable = true;
        updateContextVariables();
        console.log('✅ WRE connection established');
    }
    catch (error) {
        console.log('⚠️ WRE connection failed, running in offline mode:', error);
        extensionState.wreConnected = false;
        updateContextVariables();
    }
}
/**
 * Update VSCode context variables for conditional UI
 */
function updateContextVariables() {
    vscode.commands.executeCommand('setContext', 'foundups.agentsActive', extensionState.agentsActive);
    vscode.commands.executeCommand('setContext', 'foundups.wreConnected', extensionState.wreConnected);
    vscode.commands.executeCommand('setContext', 'foundups.wspEnabled', extensionState.wspEnabled);
    vscode.commands.executeCommand('setContext', 'foundups.providersAvailable', extensionState.providersAvailable);
}
/**
 * Extension deactivation
 */
function deactivate() {
    console.log('🔌 FoundUps Multi-Agent IDE Extension deactivating...');
    if (wreConnection) {
        wreConnection.disconnect();
    }
    console.log('✅ FoundUps Multi-Agent IDE Extension deactivated');
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map