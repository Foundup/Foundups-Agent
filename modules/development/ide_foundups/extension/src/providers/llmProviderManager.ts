/**
 * LLM Provider Manager - Universal LLM Provider Interface for VSCode
 * 
 * TypeScript interface to the Python LLM provider system
 * Supports dynamic provider discovery and intelligent routing
 */

import * as vscode from 'vscode';
import { WREConnection } from '../wre/wreConnection';

/**
 * LLM provider configuration
 */
interface LLMProvider {
    id: string;
    name: string;
    type: 'reasoning' | 'code_generation' | 'quick_response' | 'local' | 'multimodal';
    status: 'available' | 'unavailable' | 'rate_limited' | 'error';
    capabilities: string[];
    costPerToken: number;
    maxTokens: number;
    latency: number;
    qualityScore: number;
    lastUsed?: Date;
}

/**
 * LLM request configuration
 */
interface LLMRequest {
    task: 'code_generation' | 'code_analysis' | 'documentation' | 'reasoning' | 'chat' | 'quick_response';
    prompt: string;
    context?: string;
    language?: string;
    maxTokens?: number;
    temperature?: number;
    preferredProviders?: string[];
    requireFastResponse?: boolean;
    costLimit?: number;
}

/**
 * LLM response
 */
interface LLMResponse {
    success: boolean;
    content: string;
    provider: string;
    tokensUsed: number;
    cost: number;
    latency: number;
    qualityMetrics?: {
        relevance: number;
        accuracy: number;
        completeness: number;
    };
    error?: string;
}

/**
 * Provider health metrics
 */
interface ProviderHealthMetrics {
    providerId: string;
    availability: number;
    averageLatency: number;
    successRate: number;
    costEfficiency: number;
    lastHealthCheck: Date;
    recentErrors: string[];
}

/**
 * Universal LLM Provider Manager for VSCode Extension
 */
export class LLMProviderManager {
    private wreConnection: WREConnection;
    private context: vscode.ExtensionContext;
    private availableProviders: Map<string, LLMProvider> = new Map();
    private providerHealth: Map<string, ProviderHealthMetrics> = new Map();
    private requestHistory: LLMRequest[] = [];
    private statusBarItem: vscode.StatusBarItem;
    private defaultProvider: string = 'auto';

    constructor(context: vscode.ExtensionContext, wreConnection: WREConnection) {
        this.context = context;
        this.wreConnection = wreConnection;
        
        // Create status bar item
        this.statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            200
        );
        this.statusBarItem.command = 'foundups.showProviderStatus';
        
        this.initializeProviders();
    }

    /**
     * Initialize LLM providers
     */
    private async initializeProviders(): Promise<void> {
        try {
            // Get available providers from WRE
            const result = await this.wreConnection.sendCommand({
                command: 'get_available_providers',
                include_health_metrics: true
            });

            if (result.success && result.results) {
                this.processProviderList(result.results.providers);
                this.updateProviderHealth(result.results.health_metrics);
            }

            // Subscribe to provider status updates
            await this.wreConnection.subscribeToEvent('provider_status_change', (data) => {
                this.handleProviderStatusChange(data);
            });

            // Start health monitoring
            this.startHealthMonitoring();
            
            // Update status bar
            this.updateStatusBar();

        } catch (error) {
            console.error('Failed to initialize LLM providers:', error);
            vscode.window.showErrorMessage(`LLM Provider initialization failed: ${error}`);
        }
    }

    /**
     * Process provider list from WRE
     */
    private processProviderList(providers: any[]): void {
        this.availableProviders.clear();
        
        providers.forEach(provider => {
            this.availableProviders.set(provider.id, {
                id: provider.id,
                name: provider.name,
                type: provider.type,
                status: provider.status,
                capabilities: provider.capabilities || [],
                costPerToken: provider.cost_per_token || 0,
                maxTokens: provider.max_tokens || 4096,
                latency: provider.latency || 0,
                qualityScore: provider.quality_score || 0.5
            });
        });
    }

    /**
     * Update provider health metrics
     */
    private updateProviderHealth(healthMetrics: any[]): void {
        healthMetrics.forEach(metrics => {
            this.providerHealth.set(metrics.provider_id, {
                providerId: metrics.provider_id,
                availability: metrics.availability,
                averageLatency: metrics.average_latency,
                successRate: metrics.success_rate,
                costEfficiency: metrics.cost_efficiency,
                lastHealthCheck: new Date(metrics.last_health_check),
                recentErrors: metrics.recent_errors || []
            });
        });
    }

    /**
     * Handle provider status changes
     */
    private handleProviderStatusChange(data: any): void {
        const provider = this.availableProviders.get(data.provider_id);
        if (provider) {
            provider.status = data.status;
            provider.latency = data.latency || provider.latency;
            
            this.updateStatusBar();
            
            // Show notification for critical status changes
            if (data.status === 'error' || data.status === 'unavailable') {
                vscode.window.showWarningMessage(
                    `LLM Provider ${provider.name} is now ${data.status}`
                );
            }
        }
    }

    /**
     * Start health monitoring
     */
    private startHealthMonitoring(): void {
        setInterval(async () => {
            try {
                const result = await this.wreConnection.sendCommand({
                    command: 'get_provider_health',
                    provider_ids: Array.from(this.availableProviders.keys())
                });

                if (result.success && result.results) {
                    this.updateProviderHealth(result.results.health_metrics);
                    this.updateStatusBar();
                }
            } catch (error) {
                console.error('Provider health check failed:', error);
            }
        }, 60000); // Check every minute
    }

    /**
     * Make LLM request with intelligent provider selection
     */
    public async makeRequest(request: LLMRequest): Promise<LLMResponse> {
        try {
            // Select optimal provider
            const selectedProvider = this.selectOptimalProvider(request);
            
            // Send request through WRE
            const result = await this.wreConnection.sendCommand({
                command: 'llm_request',
                provider_id: selectedProvider,
                task: request.task,
                prompt: request.prompt,
                context: request.context,
                language: request.language,
                max_tokens: request.maxTokens,
                temperature: request.temperature,
                require_fast_response: request.requireFastResponse,
                cost_limit: request.costLimit
            });

            if (result.success) {
                const response: LLMResponse = {
                    success: true,
                    content: result.results.content,
                    provider: result.results.provider,
                    tokensUsed: result.results.tokens_used,
                    cost: result.results.cost,
                    latency: result.results.latency,
                    qualityMetrics: result.results.quality_metrics
                };

                // Update request history
                this.requestHistory.push(request);
                if (this.requestHistory.length > 100) {
                    this.requestHistory.shift();
                }

                return response;
            } else {
                throw new Error(result.error || 'LLM request failed');
            }

        } catch (error) {
            return {
                success: false,
                content: '',
                provider: 'none',
                tokensUsed: 0,
                cost: 0,
                latency: 0,
                error: error instanceof Error ? error.message : String(error)
            };
        }
    }

    /**
     * Select optimal provider for request
     */
    private selectOptimalProvider(request: LLMRequest): string {
        // If user specified preferred providers, try those first
        if (request.preferredProviders && request.preferredProviders.length > 0) {
            for (const providerId of request.preferredProviders) {
                const provider = this.availableProviders.get(providerId);
                if (provider && provider.status === 'available') {
                    return providerId;
                }
            }
        }

        // Auto-select based on task type and constraints
        const availableProviders = Array.from(this.availableProviders.values())
            .filter(p => p.status === 'available');

        if (availableProviders.length === 0) {
            throw new Error('No LLM providers available');
        }

        // Task-specific provider selection
        let candidates = availableProviders;

        switch (request.task) {
            case 'code_generation':
                candidates = candidates.filter(p => 
                    p.type === 'code_generation' || p.capabilities.includes('code_generation')
                );
                break;
            case 'reasoning':
                candidates = candidates.filter(p => 
                    p.type === 'reasoning' || p.capabilities.includes('reasoning')
                );
                break;
            case 'chat':
            case 'quick_response':
                candidates = candidates.filter(p => 
                    p.type === 'quick_response' || p.latency < 2000
                );
                break;
        }

        // Fallback to all available providers if no task-specific ones found
        if (candidates.length === 0) {
            candidates = availableProviders;
        }

        // Apply constraints
        if (request.requireFastResponse) {
            candidates = candidates.filter(p => p.latency < 1500);
        }

        if (request.costLimit && request.costLimit > 0) {
            candidates = candidates.filter(p => p.costPerToken <= request.costLimit!);
        }

        // Score providers and select best
        let bestProvider = candidates[0];
        let bestScore = 0;

        candidates.forEach(provider => {
            const health = this.providerHealth.get(provider.id);
            const score = this.calculateProviderScore(provider, health, request);
            
            if (score > bestScore) {
                bestScore = score;
                bestProvider = provider;
            }
        });

        return bestProvider.id;
    }

    /**
     * Calculate provider score for selection
     */
    private calculateProviderScore(
        provider: LLMProvider, 
        health: ProviderHealthMetrics | undefined,
        request: LLMRequest
    ): number {
        let score = provider.qualityScore * 0.4; // Base quality weight

        // Health metrics
        if (health) {
            score += health.availability * 0.2;
            score += health.successRate * 0.2;
            score += (1 - health.averageLatency / 5000) * 0.1; // Normalize latency
            score += health.costEfficiency * 0.1;
        }

        // Task-specific bonuses
        if (request.task === 'code_generation' && provider.capabilities.includes('code_generation')) {
            score += 0.2;
        }
        if (request.requireFastResponse && provider.latency < 1000) {
            score += 0.15;
        }

        return Math.max(0, Math.min(1, score));
    }

    /**
     * Get provider status summary
     */
    public getProviderStatus(): {
        available: number;
        total: number;
        defaultProvider: string;
        quickestProvider: string;
        cheapestProvider: string;
    } {
        const providers = Array.from(this.availableProviders.values());
        const available = providers.filter(p => p.status === 'available');
        
        let quickestProvider = 'none';
        let cheapestProvider = 'none';
        let minLatency = Infinity;
        let minCost = Infinity;

        available.forEach(provider => {
            if (provider.latency < minLatency) {
                minLatency = provider.latency;
                quickestProvider = provider.name;
            }
            if (provider.costPerToken < minCost) {
                minCost = provider.costPerToken;
                cheapestProvider = provider.name;
            }
        });

        return {
            available: available.length,
            total: providers.length,
            defaultProvider: this.defaultProvider,
            quickestProvider,
            cheapestProvider
        };
    }

    /**
     * Update status bar with provider information
     */
    private updateStatusBar(): void {
        const status = this.getProviderStatus();
        
        let icon = '🧠';
        if (status.available === 0) {
            icon = '❌';
        } else if (status.available < status.total) {
            icon = '⚠️';
        }

        this.statusBarItem.text = `${icon} LLM: ${status.available}/${status.total}`;
        this.statusBarItem.tooltip = `LLM Providers: ${status.available}/${status.total} available\nDefault: ${status.defaultProvider}\nQuickest: ${status.quickestProvider}\nCheapest: ${status.cheapestProvider}`;
        this.statusBarItem.show();
    }

    /**
     * Show provider status panel
     */
    public async showProviderStatus(): Promise<void> {
        const panel = vscode.window.createWebviewPanel(
            'foundups.providerStatus',
            '🧠 LLM Provider Status',
            vscode.ViewColumn.One,
            { enableScripts: true }
        );

        panel.webview.html = this.generateProviderStatusHTML();
    }

    /**
     * Generate provider status HTML
     */
    private generateProviderStatusHTML(): string {
        const providers = Array.from(this.availableProviders.values());
        
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; }
                    .header { color: #0078d4; border-bottom: 2px solid #0078d4; padding-bottom: 10px; margin-bottom: 20px; }
                    .provider { margin: 15px 0; padding: 15px; border-radius: 8px; border: 1px solid #ddd; }
                    .available { background-color: #d4edda; border-color: #28a745; }
                    .unavailable { background-color: #f8d7da; border-color: #dc3545; }
                    .rate-limited { background-color: #fff3cd; border-color: #ffc107; }
                    .provider-name { font-size: 1.2em; font-weight: bold; margin-bottom: 8px; }
                    .provider-details { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
                    .metric { padding: 5px; background: rgba(0,0,0,0.05); border-radius: 3px; }
                    .capabilities { margin-top: 10px; }
                    .capability-tag { display: inline-block; background: #0078d4; color: white; padding: 2px 8px; margin: 2px; border-radius: 12px; font-size: 0.8em; }
                </style>
            </head>
            <body>
                <h1 class="header">🧠 LLM Provider Status</h1>
                
                ${providers.map(provider => {
                    const health = this.providerHealth.get(provider.id);
                    return `
                        <div class="provider ${provider.status}">
                            <div class="provider-name">${provider.name} (${provider.id})</div>
                            <div class="provider-details">
                                <div class="metric">Status: ${provider.status}</div>
                                <div class="metric">Type: ${provider.type}</div>
                                <div class="metric">Latency: ${provider.latency}ms</div>
                                <div class="metric">Cost/Token: $${provider.costPerToken.toFixed(6)}</div>
                                <div class="metric">Max Tokens: ${provider.maxTokens}</div>
                                <div class="metric">Quality Score: ${(provider.qualityScore * 100).toFixed(1)}%</div>
                                ${health ? `
                                    <div class="metric">Availability: ${(health.availability * 100).toFixed(1)}%</div>
                                    <div class="metric">Success Rate: ${(health.successRate * 100).toFixed(1)}%</div>
                                ` : ''}
                            </div>
                            <div class="capabilities">
                                ${provider.capabilities.map(cap => 
                                    `<span class="capability-tag">${cap}</span>`
                                ).join('')}
                            </div>
                        </div>
                    `;
                }).join('')}
            </body>
            </html>
        `;
    }

    /**
     * Set default provider
     */
    public setDefaultProvider(providerId: string): void {
        if (providerId === 'auto' || this.availableProviders.has(providerId)) {
            this.defaultProvider = providerId;
            vscode.window.showInformationMessage(`Default LLM provider set to: ${providerId}`);
            this.updateStatusBar();
        } else {
            vscode.window.showErrorMessage(`Provider ${providerId} not found`);
        }
    }

    /**
     * Get available provider IDs
     */
    public getAvailableProviderIds(): string[] {
        return Array.from(this.availableProviders.keys())
            .filter(id => this.availableProviders.get(id)?.status === 'available');
    }

    /**
     * Dispose of provider manager
     */
    public dispose(): void {
        this.statusBarItem.dispose();
    }
} 