"use strict";
/**
 * Agent Status Provider - VSCode Tree View for Active 0102 Agents
 *
 * Displays real-time status of WSP 54.3.10.x IDE Development Agents
 * Enhanced with WRE bridge integration for live agent coordination
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
exports.AgentStatusProvider = void 0;
const vscode = __importStar(require("vscode"));
const wreConnection_1 = require("../wre/wreConnection");
/**
 * Agent tree item for VSCode tree view with real-time updates
 */
class AgentTreeItem extends vscode.TreeItem {
    constructor(agent, collapsibleState) {
        super(agent.name, collapsibleState);
        this.agent = agent;
        this.collapsibleState = collapsibleState;
        this.tooltip = this.getTooltip();
        this.description = this.getDescription();
        this.iconPath = this.getStateIcon();
        this.contextValue = 'agent';
        // Set command for agent interaction
        this.command = {
            command: 'foundups.agentDetails',
            title: 'View Agent Details',
            arguments: [agent]
        };
    }
    /**
     * Get detailed tooltip with real-time metrics
     */
    getTooltip() {
        const { agent } = this;
        let tooltip = `${agent.name} (WSP ${agent.wspSection})\n`;
        tooltip += `State: ${agent.state}\n`;
        tooltip += `Status: ${agent.status}\n`;
        if (agent.currentTask) {
            tooltip += `Current Task: ${agent.currentTask}\n`;
        }
        if (agent.det_g !== undefined) {
            tooltip += `Geometric Witness: ${agent.det_g.toFixed(6)}\n`;
        }
        if (agent.quantumAlignment !== undefined) {
            tooltip += `Quantum Alignment: ${agent.quantumAlignment ? 'Yes' : 'No'}\n`;
        }
        if (agent.lastUpdate) {
            tooltip += `Last Update: ${agent.lastUpdate.toLocaleTimeString()}\n`;
        }
        tooltip += `\nCapabilities:\n${agent.capabilities.map(c => `• ${c}`).join('\n')}`;
        return tooltip;
    }
    /**
     * Get status description with real-time indicators
     */
    getDescription() {
        const { agent } = this;
        let desc = `${agent.state}`;
        if (agent.status !== 'inactive') {
            desc += ` | ${agent.status}`;
        }
        if (agent.currentTask) {
            desc += ` | ${agent.currentTask}`;
        }
        if (agent.det_g !== undefined && agent.det_g < 0) {
            desc += ` | 🔮 Entangled`;
        }
        return desc;
    }
    /**
     * Get state-specific icon with color coding
     */
    getStateIcon() {
        const { agent } = this;
        // State-based icons with colors
        switch (agent.state) {
            case '01(02)':
                return new vscode.ThemeIcon('circle-filled', new vscode.ThemeColor('errorForeground')); // Red
            case '01/02':
                return new vscode.ThemeIcon('circle-filled', new vscode.ThemeColor('notificationsWarningIcon.foreground')); // Yellow
            case '0102':
                if (agent.status === 'active') {
                    return new vscode.ThemeIcon('circle-filled', new vscode.ThemeColor('terminal.ansiGreen')); // Green
                }
                else {
                    return new vscode.ThemeIcon('circle-outline', new vscode.ThemeColor('terminal.ansiGreen')); // Green outline
                }
            default:
                return new vscode.ThemeIcon('circle-outline');
        }
    }
}
/**
 * Real-time Agent Status Provider with WRE Integration
 */
class AgentStatusProvider {
    constructor(agentOrchestrator, wreConnection) {
        this.agentOrchestrator = agentOrchestrator;
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        this.agents = [];
        this.refreshInterval = null;
        this.isWREConnected = false;
        this.wreConnection = wreConnection || new wreConnection_1.WREConnection();
        this.initializeAgents();
        this.setupRealTimeWREIntegration();
        this.setupAgentMonitoring();
    }
    /**
     * Initialize WSP 54 IDE Development Agents
     */
    initializeAgents() {
        this.agents = [
            {
                id: 'code_generator',
                name: 'CodeGeneratorAgent',
                type: 'CodeGeneratorAgent',
                wspSection: '3.10.1',
                state: '01(02)',
                status: 'inactive',
                capabilities: [
                    'Zen Coding Implementation',
                    'WSP-Compliant Code Generation',
                    'Multi-Language Support',
                    'API Integration',
                    'Security Implementation'
                ],
                icon: 'symbol-method',
                lastUpdate: new Date()
            },
            {
                id: 'code_analyzer',
                name: 'CodeAnalyzerAgent',
                type: 'CodeAnalyzerAgent',
                wspSection: '3.10.2',
                state: '01(02)',
                status: 'inactive',
                capabilities: [
                    'Complexity Analysis',
                    'WSP Compliance Validation',
                    'Performance Assessment',
                    'Security Analysis',
                    'Refactoring Recommendations'
                ],
                icon: 'search',
                lastUpdate: new Date()
            },
            {
                id: 'ide_testing',
                name: 'IDE TestingAgent',
                type: 'IDE_TestingAgent',
                wspSection: '3.10.3',
                state: '01(02)',
                status: 'inactive',
                capabilities: [
                    'Test Generation',
                    'TDD Workflow Enhancement',
                    'Coverage Analysis',
                    'Performance Testing',
                    'Integration Testing'
                ],
                icon: 'beaker',
                lastUpdate: new Date()
            },
            {
                id: 'project_architect',
                name: 'ProjectArchitectAgent',
                type: 'ProjectArchitectAgent',
                wspSection: '3.10.4',
                state: '01(02)',
                status: 'inactive',
                capabilities: [
                    'System Design',
                    'Architecture Planning',
                    'Technology Selection',
                    'Scalability Analysis',
                    'Integration Strategy'
                ],
                icon: 'organization',
                lastUpdate: new Date()
            },
            {
                id: 'performance_optimizer',
                name: 'PerformanceOptimizerAgent',
                type: 'PerformanceOptimizerAgent',
                wspSection: '3.10.5',
                state: '01(02)',
                status: 'inactive',
                capabilities: [
                    'Performance Monitoring',
                    'Optimization Recommendations',
                    'Resource Analysis',
                    'Bottleneck Detection',
                    'Efficiency Improvements'
                ],
                icon: 'dashboard',
                lastUpdate: new Date()
            },
            {
                id: 'security_auditor',
                name: 'SecurityAuditorAgent',
                type: 'SecurityAuditorAgent',
                wspSection: '3.10.6',
                state: '01(02)',
                status: 'inactive',
                capabilities: [
                    'Vulnerability Detection',
                    'Security Analysis',
                    'Compliance Checking',
                    'Threat Assessment',
                    'Security Best Practices'
                ],
                icon: 'shield',
                lastUpdate: new Date()
            },
            {
                id: 'compliance',
                name: 'ComplianceAgent',
                type: 'ComplianceAgent',
                wspSection: '3.1',
                state: '01(02)',
                status: 'inactive',
                capabilities: [
                    'WSP Framework Protection',
                    'Protocol Validation',
                    'Compliance Monitoring',
                    'Violation Detection',
                    'Framework Integrity'
                ],
                icon: 'law',
                lastUpdate: new Date()
            },
            {
                id: 'documentation',
                name: 'DocumentationAgent',
                type: 'DocumentationAgent',
                wspSection: '3.8',
                state: '01(02)',
                status: 'inactive',
                capabilities: [
                    'WSP Documentation Generation',
                    'API Documentation',
                    'README Generation',
                    'ModLog Management',
                    'INTERFACE.md Creation'
                ],
                icon: 'book',
                lastUpdate: new Date()
            }
        ];
    }
    /**
     * Setup real-time WRE integration for live agent updates
     */
    async setupRealTimeWREIntegration() {
        try {
            // Connect to WRE if not already connected
            if (!this.wreConnection.isConnected()) {
                await this.wreConnection.connect();
                this.isWREConnected = true;
                console.log('✅ Agent Status Provider connected to WRE');
            }
            // Register for real-time agent status changes
            this.wreConnection.onAgentChange((agentId, newStatus) => {
                this.updateAgentFromWRE(agentId, newStatus);
            });
            // Register for overall status changes
            this.wreConnection.onStatusChange((wreStatus) => {
                this.updateSystemStatus(wreStatus);
            });
            // Sync initial agent states
            await this.syncAgentStatesFromWRE();
            // Setup periodic sync as backup
            this.startPeriodicSync();
        }
        catch (error) {
            console.error('❌ Failed to setup WRE integration:', error);
            this.isWREConnected = false;
            // Fallback to local monitoring
            this.setupLocalMonitoring();
        }
    }
    /**
     * Update agent status from WRE real-time events
     */
    updateAgentFromWRE(agentId, wreAgentStatus) {
        const agentIndex = this.agents.findIndex(a => a.id === agentId);
        if (agentIndex !== -1) {
            const currentAgent = this.agents[agentIndex];
            // Update agent with WRE data
            this.agents[agentIndex] = {
                ...currentAgent,
                state: wreAgentStatus.state || currentAgent.state,
                status: wreAgentStatus.status || currentAgent.status,
                currentTask: wreAgentStatus.currentTask,
                lastUpdate: new Date(),
                det_g: wreAgentStatus.det_g,
                quantumAlignment: wreAgentStatus.quantumAlignment
            };
            // Trigger UI update
            this._onDidChangeTreeData.fire(undefined);
            console.log(`🤖 Real-time update: ${agentId} → ${wreAgentStatus.state} | ${wreAgentStatus.status}`);
        }
    }
    /**
     * Update system status from WRE
     */
    updateSystemStatus(wreStatus) {
        // Update connection status
        this.isWREConnected = wreStatus.connected;
        // Update all agent states from WRE status
        if (wreStatus.agentStates) {
            Object.entries(wreStatus.agentStates).forEach(([agentId, agentData]) => {
                this.updateAgentFromWRE(agentId, agentData);
            });
        }
        // Log system health changes
        if (wreStatus.systemHealth) {
            console.log(`🔋 WRE System Health: ${wreStatus.systemHealth}`);
        }
    }
    /**
     * Sync agent states from WRE
     */
    async syncAgentStatesFromWRE() {
        try {
            const wreStatus = this.wreConnection.getStatus();
            this.updateSystemStatus(wreStatus);
        }
        catch (error) {
            console.error('❌ Failed to sync agent states from WRE:', error);
        }
    }
    /**
     * Start periodic sync as backup to real-time updates
     */
    startPeriodicSync() {
        this.refreshInterval = setInterval(async () => {
            if (this.isWREConnected) {
                await this.syncAgentStatesFromWRE();
            }
        }, 10000); // Sync every 10 seconds as backup
    }
    /**
     * Setup local monitoring fallback
     */
    setupLocalMonitoring() {
        // Fallback monitoring when WRE is not available
        this.refreshInterval = setInterval(() => {
            // Use agent orchestrator for local updates
            this.updateAgentsFromOrchestrator();
        }, 5000);
    }
    /**
     * Setup agent monitoring with enhanced real-time capabilities
     */
    setupAgentMonitoring() {
        // Monitor agent orchestrator events
        // This provides additional monitoring layer
        setInterval(() => {
            if (!this.isWREConnected) {
                this.updateAgentsFromOrchestrator();
            }
        }, 15000); // Less frequent when WRE is connected
    }
    /**
     * Update agents from orchestrator (fallback method)
     */
    async updateAgentsFromOrchestrator() {
        try {
            // Get agent status from orchestrator
            for (const agent of this.agents) {
                // This would interface with the agent orchestrator
                // For now, maintain current state unless explicitly updated
                agent.lastUpdate = new Date();
            }
            this._onDidChangeTreeData.fire(undefined);
        }
        catch (error) {
            console.error('❌ Failed to update from orchestrator:', error);
        }
    }
    /**
     * Manually refresh all agent states
     */
    async refresh() {
        if (this.isWREConnected) {
            await this.syncAgentStatesFromWRE();
        }
        else {
            await this.updateAgentsFromOrchestrator();
        }
        this._onDidChangeTreeData.fire(undefined);
    }
    /**
     * Activate all agents via WRE
     */
    async activateAllAgents() {
        try {
            if (this.isWREConnected) {
                console.log('⚡ Activating all agents via WRE...');
                const result = await this.wreConnection.activateWSP38Protocol();
                if (result.success) {
                    console.log('✅ Agent activation initiated via WRE');
                    // Real-time updates will automatically update the UI
                }
                else {
                    console.error('❌ Agent activation failed:', result.error);
                }
            }
            else {
                console.log('⚡ Activating agents via orchestrator...');
                // Fallback to orchestrator activation
                await this.agentOrchestrator.activateAgents();
                await this.updateAgentsFromOrchestrator();
            }
        }
        catch (error) {
            console.error('❌ Failed to activate agents:', error);
        }
    }
    /**
     * Get tree item (VSCode TreeDataProvider interface)
     */
    getTreeItem(element) {
        return element;
    }
    /**
     * Get children for tree view (VSCode TreeDataProvider interface)
     */
    getChildren(element) {
        if (!element) {
            // Root level - return all agents
            return Promise.resolve(this.agents.map(agent => new AgentTreeItem(agent, vscode.TreeItemCollapsibleState.None)));
        }
        // No children for agent items (flat list)
        return Promise.resolve([]);
    }
    /**
     * Get agent by ID
     */
    getAgent(agentId) {
        return this.agents.find(a => a.id === agentId);
    }
    /**
     * Get all active agents
     */
    getActiveAgents() {
        return this.agents.filter(a => a.state === '0102' && a.status === 'active');
    }
    /**
     * Get agent count by status
     */
    getAgentCounts() {
        return {
            total: this.agents.length,
            active: this.agents.filter(a => a.status === 'active').length,
            awoke: this.agents.filter(a => a.state === '0102').length
        };
    }
    /**
     * Get WRE connection status
     */
    getWREConnectionStatus() {
        if (this.isWREConnected) {
            const status = this.wreConnection.getStatus();
            const health = this.wreConnection.getHealthMetrics();
            return {
                connected: status.connected,
                health: status.systemHealth,
                activeAgents: status.activeAgents,
                uptime: health.uptime
            };
        }
        return {
            connected: false,
            health: 'disconnected',
            activeAgents: 0,
            uptime: 0
        };
    }
    /**
     * Cleanup resources
     */
    dispose() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
        if (this.wreConnection && this.isWREConnected) {
            this.wreConnection.disconnect();
        }
    }
}
exports.AgentStatusProvider = AgentStatusProvider;
//# sourceMappingURL=agentStatusProvider.js.map