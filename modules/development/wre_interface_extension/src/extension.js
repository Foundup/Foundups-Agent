#!/usr/bin/env javascript
/**
 * WRE Interface Extension for VS Code
 * 
 * Autonomous development interface powered by WRE (Windsurf Recursive Engine)
 * with 0102 agent coordination and WSP protocol compliance.
 * 
 * WSP Compliance: WSP 54 (Agent Duties), WSP 46 (Agentic Recursion), WSP 50 (Pre-Action Verification)
 */

const vscode = require('vscode');
const path = require('path');
const { spawn } = require('child_process');

/**
 * WRE Interface Extension Main Class
 * Provides autonomous development capabilities through WRE integration
 */
class WREInterfaceExtension {
    constructor() {
        this.statusBarItem = null;
        this.subAgentCoordinator = null;
        this.isActive = false;
        this.currentSession = null;
    }

    /**
     * Activate the WRE Interface Extension
     */
    activate(context) {
        console.log('🌀 WRE Interface Extension is now active!');

        // Initialize status bar
        this.initializeStatusBar();

        // Register commands
        this.registerCommands(context);

        // Initialize sub-agent coordinator
        this.initializeSubAgentCoordinator();

        // Show activation message
        vscode.window.showInformationMessage('🚀 WRE Interface Extension Activated - Autonomous Development Ready');
    }

    /**
     * Initialize status bar for WRE status display
     */
    initializeStatusBar() {
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
        this.statusBarItem.text = '🌀 WRE: Inactive';
        this.statusBarItem.tooltip = 'WRE Interface Extension Status';
        this.statusBarItem.show();
        this.statusBarItem.command = 'wre.activate';
    }

    /**
     * Register WRE commands
     */
    registerCommands(context) {
        // WRE Activation Command
        let activateCommand = vscode.commands.registerCommand('wre.activate', () => {
            this.activateWRE();
        });

        // Create Module Command
        let createModuleCommand = vscode.commands.registerCommand('wre.createModule', () => {
            this.createModule();
        });

        // Analyze Code Command
        let analyzeCodeCommand = vscode.commands.registerCommand('wre.analyzeCode', () => {
            this.analyzeCode();
        });

        // Run Tests Command
        let runTestsCommand = vscode.commands.registerCommand('wre.runTests', () => {
            this.runTests();
        });

        // Validate Compliance Command
        let validateComplianceCommand = vscode.commands.registerCommand('wre.validateCompliance', () => {
            this.validateCompliance();
        });

        context.subscriptions.push(
            activateCommand,
            createModuleCommand,
            analyzeCodeCommand,
            runTestsCommand,
            validateComplianceCommand
        );
    }

    /**
     * Initialize sub-agent coordinator for multi-agent operations
     */
    initializeSubAgentCoordinator() {
        // Import sub-agent coordinator from the module
        const coordinatorPath = path.join(__dirname, 'sub_agent_coordinator.py');
        
        // Set up Python path for WRE integration
        process.env.PYTHONPATH = path.join(__dirname, '..', '..', '..', '..');
        
        console.log('🤖 Sub-Agent Coordinator initialized');
    }

    /**
     * Activate WRE autonomous development
     */
    async activateWRE() {
        try {
            this.statusBarItem.text = '🌀 WRE: Activating...';
            
            // Execute WRE activation through sub-agent coordinator
            const result = await this.executeWRECommand('activate');
            
            if (result.success) {
                this.isActive = true;
                this.statusBarItem.text = '🌀 WRE: Active';
                vscode.window.showInformationMessage('🚀 WRE Autonomous Development Activated');
                
                // Show available commands
                this.showAvailableCommands();
            } else {
                this.statusBarItem.text = '🌀 WRE: Error';
                vscode.window.showErrorMessage(`❌ WRE Activation Failed: ${result.error}`);
            }
        } catch (error) {
            this.statusBarItem.text = '🌀 WRE: Error';
            vscode.window.showErrorMessage(`❌ WRE Activation Error: ${error.message}`);
        }
    }

    /**
     * Create new module with WRE
     */
    async createModule() {
        if (!this.isActive) {
            vscode.window.showWarningMessage('⚠️ Please activate WRE first');
            return;
        }

        try {
            // Get module name from user
            const moduleName = await vscode.window.showInputBox({
                prompt: 'Enter module name',
                placeHolder: 'e.g., my_new_module'
            });

            if (!moduleName) return;

            // Get domain selection
            const domain = await vscode.window.showQuickPick([
                'ai_intelligence',
                'communication', 
                'platform_integration',
                'infrastructure',
                'monitoring',
                'development',
                'foundups',
                'gamification',
                'blockchain'
            ], {
                placeHolder: 'Select enterprise domain'
            });

            if (!domain) return;

            this.statusBarItem.text = '🌀 WRE: Creating Module...';
            
            // Execute module creation
            const result = await this.executeWRECommand('createModule', {
                moduleName: moduleName,
                domain: domain
            });

            if (result.success) {
                vscode.window.showInformationMessage(`✅ Module '${moduleName}' created successfully in ${domain}`);
                this.statusBarItem.text = '🌀 WRE: Active';
            } else {
                vscode.window.showErrorMessage(`❌ Module Creation Failed: ${result.error}`);
            }
        } catch (error) {
            vscode.window.showErrorMessage(`❌ Module Creation Error: ${error.message}`);
        }
    }

    /**
     * Analyze code quality with WRE
     */
    async analyzeCode() {
        if (!this.isActive) {
            vscode.window.showWarningMessage('⚠️ Please activate WRE first');
            return;
        }

        try {
            this.statusBarItem.text = '🌀 WRE: Analyzing...';
            
            // Get current file path
            const activeEditor = vscode.window.activeTextEditor;
            if (!activeEditor) {
                vscode.window.showWarningMessage('⚠️ No active file to analyze');
                return;
            }

            const filePath = activeEditor.document.fileName;
            
            // Execute code analysis
            const result = await this.executeWRECommand('analyzeCode', {
                filePath: filePath
            });

            if (result.success) {
                // Show analysis results in output panel
                this.showAnalysisResults(result.data);
                vscode.window.showInformationMessage('✅ Code analysis completed');
            } else {
                vscode.window.showErrorMessage(`❌ Code Analysis Failed: ${result.error}`);
            }
            
            this.statusBarItem.text = '🌀 WRE: Active';
        } catch (error) {
            vscode.window.showErrorMessage(`❌ Code Analysis Error: ${error.message}`);
        }
    }

    /**
     * Run tests with WRE
     */
    async runTests() {
        if (!this.isActive) {
            vscode.window.showWarningMessage('⚠️ Please activate WRE first');
            return;
        }

        try {
            this.statusBarItem.text = '🌀 WRE: Running Tests...';
            
            // Execute test suite
            const result = await this.executeWRECommand('runTests');

            if (result.success) {
                this.showTestResults(result.data);
                vscode.window.showInformationMessage('✅ Test suite completed');
            } else {
                vscode.window.showErrorMessage(`❌ Test Execution Failed: ${result.error}`);
            }
            
            this.statusBarItem.text = '🌀 WRE: Active';
        } catch (error) {
            vscode.window.showErrorMessage(`❌ Test Execution Error: ${error.message}`);
        }
    }

    /**
     * Validate WSP compliance with WRE
     */
    async validateCompliance() {
        if (!this.isActive) {
            vscode.window.showWarningMessage('⚠️ Please activate WRE first');
            return;
        }

        try {
            this.statusBarItem.text = '🌀 WRE: Validating...';
            
            // Execute WSP compliance validation
            const result = await this.executeWRECommand('validateCompliance');

            if (result.success) {
                this.showComplianceResults(result.data);
                vscode.window.showInformationMessage('✅ WSP compliance validation completed');
            } else {
                vscode.window.showErrorMessage(`❌ Compliance Validation Failed: ${result.error}`);
            }
            
            this.statusBarItem.text = '🌀 WRE: Active';
        } catch (error) {
            vscode.window.showErrorMessage(`❌ Compliance Validation Error: ${error.message}`);
        }
    }

    /**
     * Execute WRE command through sub-agent coordinator
     */
    async executeWRECommand(command, params = {}) {
        return new Promise((resolve, reject) => {
            const coordinatorPath = path.join(__dirname, 'sub_agent_coordinator.py');
            
            const pythonProcess = spawn('python', [coordinatorPath, command, JSON.stringify(params)], {
                cwd: path.join(__dirname, '..', '..', '..', '..'),
                env: { ...process.env, PYTHONPATH: path.join(__dirname, '..', '..', '..', '..') }
            });

            let output = '';
            let error = '';

            pythonProcess.stdout.on('data', (data) => {
                output += data.toString();
            });

            pythonProcess.stderr.on('data', (data) => {
                error += data.toString();
            });

            pythonProcess.on('close', (code) => {
                if (code === 0) {
                    try {
                        const result = JSON.parse(output);
                        resolve(result);
                    } catch (e) {
                        resolve({ success: true, data: output });
                    }
                } else {
                    reject(new Error(error || `Command failed with code ${code}`));
                }
            });
        });
    }

    /**
     * Show available WRE commands
     */
    showAvailableCommands() {
        const commands = [
            'WRE: Create New Module',
            'WRE: Analyze Code Quality', 
            'WRE: Run Test Suite',
            'WRE: Validate WSP Compliance'
        ];

        vscode.window.showInformationMessage(
            `🚀 WRE Commands Available:\n${commands.join('\n')}`,
            'Open Command Palette'
        ).then(selection => {
            if (selection === 'Open Command Palette') {
                vscode.commands.executeCommand('workbench.action.showCommands');
            }
        });
    }

    /**
     * Show analysis results in output panel
     */
    showAnalysisResults(data) {
        const output = vscode.window.createOutputChannel('WRE Code Analysis');
        output.clear();
        output.appendLine('=== WRE Code Analysis Results ===');
        output.appendLine(JSON.stringify(data, null, 2));
        output.show();
    }

    /**
     * Show test results in output panel
     */
    showTestResults(data) {
        const output = vscode.window.createOutputChannel('WRE Test Results');
        output.clear();
        output.appendLine('=== WRE Test Results ===');
        output.appendLine(JSON.stringify(data, null, 2));
        output.show();
    }

    /**
     * Show compliance results in output panel
     */
    showComplianceResults(data) {
        const output = vscode.window.createOutputChannel('WRE Compliance Results');
        output.clear();
        output.appendLine('=== WRE WSP Compliance Results ===');
        output.appendLine(JSON.stringify(data, null, 2));
        output.show();
    }

    /**
     * Deactivate the extension
     */
    deactivate() {
        if (this.statusBarItem) {
            this.statusBarItem.dispose();
        }
        console.log('🌀 WRE Interface Extension deactivated');
    }
}

// Export the extension
module.exports = WREInterfaceExtension; 