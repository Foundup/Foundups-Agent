"use strict";
/**
 * WSP Compliance Monitor - Real-Time Protocol Compliance Tracking
 *
 * Monitors WSP protocol compliance across all IDE operations
 * Following WSP protocols for compliance validation and reporting
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
exports.WSPComplianceMonitor = void 0;
const vscode = __importStar(require("vscode"));
/**
 * WSP Compliance Monitor for Real-Time Protocol Tracking
 */
class WSPComplianceMonitor {
    constructor(context, wreConnection) {
        this.violations = new Map();
        this.protocolStatuses = new Map();
        this.monitoringActive = false;
        this.context = context;
        this.wreConnection = wreConnection;
        // Create status bar item
        this.complianceStatusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
        this.complianceStatusBar.command = 'foundups.showComplianceReport';
        // Create tree provider
        this.complianceTreeProvider = new WSPComplianceTreeProvider(this);
        this.initializeWSPProtocols();
    }
    /**
     * Initialize WSP protocol monitoring
     */
    initializeWSPProtocols() {
        const wspProtocols = [
            { id: 'WSP_1', name: 'Framework Coherence Protocol' },
            { id: 'WSP_3', name: 'Enterprise Domain Organization' },
            { id: 'WSP_5', name: 'Testing Coverage Protocol' },
            { id: 'WSP_11', name: 'Interface Definition Protocol' },
            { id: 'WSP_22', name: 'ModLog and Roadmap Protocol' },
            { id: 'WSP_38', name: 'Agentic Activation Protocol' },
            { id: 'WSP_39', name: 'Agentic Ignition Protocol' },
            { id: 'WSP_46', name: 'WRE Integration Protocol' },
            { id: 'WSP_49', name: 'Module Directory Structure' },
            { id: 'WSP_54', name: 'WRE Agent Duties Specification' }
        ];
        wspProtocols.forEach(protocol => {
            this.protocolStatuses.set(protocol.id, {
                protocolId: protocol.id,
                protocolName: protocol.name,
                status: 'unknown',
                lastCheck: new Date(),
                details: 'Monitoring not started',
                violationCount: 0,
                autoFixAvailable: false
            });
        });
    }
    /**
     * Start WSP compliance monitoring
     */
    async startMonitoring() {
        if (this.monitoringActive) {
            return;
        }
        try {
            this.monitoringActive = true;
            // Show status bar
            this.complianceStatusBar.show();
            this.updateStatusBar();
            // Register tree view
            vscode.window.createTreeView('foundups.complianceView', {
                treeDataProvider: this.complianceTreeProvider,
                showCollapseAll: true
            });
            // Subscribe to WRE compliance events
            await this.wreConnection.subscribeToEvent('wsp_compliance_update', (data) => {
                this.handleComplianceUpdate(data);
            });
            // Start periodic compliance checks
            this.startPeriodicChecks();
            vscode.window.showInformationMessage('🔍 WSP Compliance monitoring started');
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to start WSP monitoring: ${error}`);
        }
    }
    /**
     * Stop WSP compliance monitoring
     */
    stopMonitoring() {
        this.monitoringActive = false;
        this.complianceStatusBar.hide();
        vscode.window.showInformationMessage('WSP Compliance monitoring stopped');
    }
    /**
     * Start periodic compliance checks
     */
    startPeriodicChecks() {
        setInterval(async () => {
            if (this.monitoringActive) {
                await this.performComplianceCheck();
            }
        }, 30000); // Check every 30 seconds
    }
    /**
     * Perform comprehensive WSP compliance check
     */
    async performComplianceCheck() {
        try {
            const result = await this.wreConnection.sendCommand({
                command: 'check_wsp_compliance',
                protocols: Array.from(this.protocolStatuses.keys()),
                workspace_path: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath
            });
            if (result.success && result.results) {
                this.processComplianceResults(result.results);
            }
        }
        catch (error) {
            console.error('WSP compliance check failed:', error);
        }
    }
    /**
     * Process compliance check results
     */
    processComplianceResults(results) {
        // Update protocol statuses
        if (results.protocols) {
            Object.entries(results.protocols).forEach(([protocolId, data]) => {
                const status = this.protocolStatuses.get(protocolId);
                if (status) {
                    status.status = data.status;
                    status.lastCheck = new Date();
                    status.details = data.details;
                    status.violationCount = data.violations?.length || 0;
                    status.autoFixAvailable = data.auto_fix_available || false;
                }
            });
        }
        // Update violations
        if (results.violations) {
            this.violations.clear();
            results.violations.forEach((violation) => {
                this.violations.set(violation.id, {
                    id: violation.id,
                    protocolId: violation.protocol_id,
                    severity: violation.severity,
                    description: violation.description,
                    file: violation.file,
                    line: violation.line,
                    autoFixable: violation.auto_fixable,
                    timestamp: new Date(violation.timestamp)
                });
            });
        }
        // Update UI
        this.updateStatusBar();
        this.complianceTreeProvider.refresh();
    }
    /**
     * Handle real-time compliance updates from WRE
     */
    handleComplianceUpdate(data) {
        if (data.protocol_id) {
            const status = this.protocolStatuses.get(data.protocol_id);
            if (status) {
                status.status = data.status;
                status.lastCheck = new Date();
                status.details = data.details;
                this.updateStatusBar();
                this.complianceTreeProvider.refresh();
            }
        }
        // Handle new violations
        if (data.violation) {
            this.violations.set(data.violation.id, data.violation);
            // Show violation notification
            if (data.violation.severity === 'critical' || data.violation.severity === 'high') {
                vscode.window.showWarningMessage(`WSP Violation: ${data.violation.description}`, 'View Details', 'Auto Fix').then(action => {
                    if (action === 'View Details') {
                        this.showComplianceReport();
                    }
                    else if (action === 'Auto Fix' && data.violation.auto_fixable) {
                        this.autoFixViolation(data.violation.id);
                    }
                });
            }
        }
    }
    /**
     * Update status bar with compliance summary
     */
    updateStatusBar() {
        const totalProtocols = this.protocolStatuses.size;
        const compliantCount = Array.from(this.protocolStatuses.values())
            .filter(status => status.status === 'compliant').length;
        const violationCount = this.violations.size;
        let icon = '✅';
        let text = `WSP: ${compliantCount}/${totalProtocols}`;
        if (violationCount > 0) {
            const criticalViolations = Array.from(this.violations.values())
                .filter(v => v.severity === 'critical').length;
            if (criticalViolations > 0) {
                icon = '🚨';
                text += ` (${criticalViolations} critical)`;
            }
            else {
                icon = '⚠️';
                text += ` (${violationCount} issues)`;
            }
        }
        this.complianceStatusBar.text = `${icon} ${text}`;
        this.complianceStatusBar.tooltip = `WSP Compliance: ${compliantCount}/${totalProtocols} protocols compliant, ${violationCount} violations`;
    }
    /**
     * Show comprehensive compliance report
     */
    async showComplianceReport() {
        const panel = vscode.window.createWebviewPanel('foundups.complianceReport', '📊 WSP Compliance Report', vscode.ViewColumn.One, { enableScripts: true });
        panel.webview.html = this.generateComplianceReportHTML();
    }
    /**
     * Auto-fix WSP violation
     */
    async autoFixViolation(violationId) {
        const violation = this.violations.get(violationId);
        if (!violation || !violation.autoFixable) {
            vscode.window.showErrorMessage('Auto-fix not available for this violation');
            return;
        }
        try {
            const result = await this.wreConnection.sendCommand({
                command: 'auto_fix_wsp_violation',
                violation_id: violationId
            });
            if (result.success) {
                vscode.window.showInformationMessage(`✅ Auto-fixed WSP violation: ${violation.description}`);
                this.violations.delete(violationId);
                this.updateStatusBar();
                this.complianceTreeProvider.refresh();
            }
            else {
                vscode.window.showErrorMessage(`Failed to auto-fix violation: ${result.error}`);
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`Auto-fix failed: ${error}`);
        }
    }
    /**
     * Generate compliance report HTML
     */
    generateComplianceReportHTML() {
        const protocols = Array.from(this.protocolStatuses.values());
        const violations = Array.from(this.violations.values());
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; }
                    .header { color: #0078d4; border-bottom: 2px solid #0078d4; padding-bottom: 10px; margin-bottom: 20px; }
                    .protocol { margin: 10px 0; padding: 10px; border-radius: 5px; }
                    .compliant { background-color: #d4edda; border-left: 4px solid #28a745; }
                    .warning { background-color: #fff3cd; border-left: 4px solid #ffc107; }
                    .violation { background-color: #f8d7da; border-left: 4px solid #dc3545; }
                    .unknown { background-color: #f8f9fa; border-left: 4px solid #6c757d; }
                    .violation-item { margin: 5px 0; padding: 8px; background: #f8f9fa; border-radius: 3px; }
                    .severity-critical { border-left: 3px solid #dc3545; }
                    .severity-high { border-left: 3px solid #fd7e14; }
                    .severity-medium { border-left: 3px solid #ffc107; }
                    .severity-low { border-left: 3px solid #20c997; }
                </style>
            </head>
            <body>
                <h1 class="header">📊 WSP Compliance Report</h1>
                
                <h2>Protocol Compliance Status</h2>
                ${protocols.map(protocol => `
                    <div class="protocol ${protocol.status}">
                        <strong>${protocol.protocolId}: ${protocol.protocolName}</strong><br>
                        Status: ${protocol.status}<br>
                        Last Check: ${protocol.lastCheck.toLocaleString()}<br>
                        ${protocol.details}
                        ${protocol.violationCount > 0 ? `<br>Violations: ${protocol.violationCount}` : ''}
                    </div>
                `).join('')}
                
                ${violations.length > 0 ? `
                    <h2>Active Violations (${violations.length})</h2>
                    ${violations.map(violation => `
                        <div class="violation-item severity-${violation.severity}">
                            <strong>${violation.protocolId}</strong> - ${violation.severity.toUpperCase()}<br>
                            ${violation.description}<br>
                            <small>File: ${violation.file}${violation.line ? `:${violation.line}` : ''}</small><br>
                            <small>Time: ${violation.timestamp.toLocaleString()}</small>
                            ${violation.autoFixable ? '<br><small>✅ Auto-fix available</small>' : ''}
                        </div>
                    `).join('')}
                ` : '<h2>✅ No Active Violations</h2>'}
            </body>
            </html>
        `;
    }
    /**
     * Generate comprehensive compliance report
     */
    async generateComplianceReport() {
        await this.performComplianceCheck();
        const protocols = Array.from(this.protocolStatuses.values());
        const violations = Array.from(this.violations.values());
        let report = '# WSP Compliance Report\n\n';
        report += `Generated: ${new Date().toLocaleString()}\n\n`;
        report += `## Summary\n`;
        report += `- Total Protocols: ${protocols.length}\n`;
        report += `- Compliant: ${protocols.filter(p => p.status === 'compliant').length}\n`;
        report += `- Violations: ${violations.length}\n\n`;
        report += `## Protocol Status\n`;
        protocols.forEach(protocol => {
            const status = protocol.status === 'compliant' ? '✅' :
                protocol.status === 'warning' ? '⚠️' : '❌';
            report += `${status} **${protocol.protocolId}**: ${protocol.protocolName} - ${protocol.status}\n`;
        });
        if (violations.length > 0) {
            report += `\n## Active Violations\n`;
            violations.forEach(violation => {
                const severity = violation.severity === 'critical' ? '🚨' :
                    violation.severity === 'high' ? '⚠️' : 'ℹ️';
                report += `${severity} **${violation.protocolId}**: ${violation.description}\n`;
            });
        }
        return report;
    }
    /**
     * Get protocol statuses for tree view
     */
    getProtocolStatuses() {
        return Array.from(this.protocolStatuses.values());
    }
    /**
     * Get violations for tree view
     */
    getViolations() {
        return Array.from(this.violations.values());
    }
    /**
     * Dispose of compliance monitor
     */
    dispose() {
        this.complianceStatusBar.dispose();
        this.monitoringActive = false;
    }
}
exports.WSPComplianceMonitor = WSPComplianceMonitor;
/**
 * Tree data provider for WSP compliance view
 */
class WSPComplianceTreeProvider {
    constructor(complianceMonitor) {
        this.complianceMonitor = complianceMonitor;
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
    }
    refresh() {
        this._onDidChangeTreeData.fire();
    }
    getTreeItem(element) {
        return element;
    }
    getChildren(element) {
        if (!element) {
            // Root level - return protocol categories
            return [
                new ComplianceTreeItem('Protocols', vscode.TreeItemCollapsibleState.Expanded, 'category'),
                new ComplianceTreeItem('Violations', vscode.TreeItemCollapsibleState.Expanded, 'category')
            ];
        }
        if (element.label === 'Protocols') {
            return this.complianceMonitor.getProtocolStatuses().map(protocol => new ComplianceTreeItem(`${protocol.protocolId}: ${protocol.status}`, vscode.TreeItemCollapsibleState.None, 'protocol', protocol));
        }
        if (element.label === 'Violations') {
            const violations = this.complianceMonitor.getViolations();
            return violations.map(violation => new ComplianceTreeItem(`${violation.protocolId}: ${violation.description}`, vscode.TreeItemCollapsibleState.None, 'violation', violation));
        }
        return [];
    }
}
/**
 * Tree item for compliance view
 */
class ComplianceTreeItem extends vscode.TreeItem {
    constructor(label, collapsibleState, itemType, data) {
        super(label, collapsibleState);
        this.label = label;
        this.collapsibleState = collapsibleState;
        this.itemType = itemType;
        this.data = data;
        this.tooltip = this.getTooltip();
        this.iconPath = this.getIcon();
        this.contextValue = itemType;
    }
    getTooltip() {
        if (this.itemType === 'protocol' && this.data) {
            return `${this.data.protocolName}\nStatus: ${this.data.status}\nLast Check: ${this.data.lastCheck.toLocaleString()}`;
        }
        if (this.itemType === 'violation' && this.data) {
            return `${this.data.description}\nSeverity: ${this.data.severity}\nFile: ${this.data.file}`;
        }
        return this.label;
    }
    getIcon() {
        if (this.itemType === 'protocol' && this.data) {
            switch (this.data.status) {
                case 'compliant': return new vscode.ThemeIcon('check', new vscode.ThemeColor('terminal.ansiGreen'));
                case 'warning': return new vscode.ThemeIcon('warning', new vscode.ThemeColor('notificationsWarningIcon.foreground'));
                case 'violation': return new vscode.ThemeIcon('error', new vscode.ThemeColor('errorForeground'));
                default: return new vscode.ThemeIcon('question');
            }
        }
        if (this.itemType === 'violation') {
            return new vscode.ThemeIcon('bug', new vscode.ThemeColor('errorForeground'));
        }
        return new vscode.ThemeIcon('folder');
    }
}
//# sourceMappingURL=wspComplianceMonitor.js.map