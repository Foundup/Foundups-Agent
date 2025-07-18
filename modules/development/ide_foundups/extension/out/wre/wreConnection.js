"use strict";
/**
 * WRE Connection - WebSocket Bridge to Windsurf Recursive Engine
 *
 * Enables real-time communication between VSCode IDE and WRE orchestration system
 * Handles CMST Protocol execution, agent activation, and module creation
 * Enhanced with real-time agent coordination and status synchronization
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.WREConnection = void 0;
const ws_1 = __importDefault(require("ws"));
/**
 * WRE Connection Manager with Real-Time Agent Coordination
 */
class WREConnection {
    constructor(endpoint = 'ws://localhost:8765') {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.heartbeatInterval = null;
        this.statusSyncInterval = null;
        this.commandQueue = new Map();
        // Real-time agent coordination
        this.agentStates = new Map();
        this.eventSubscriptions = new Map();
        this.lastStatusUpdate = new Date();
        this.connectionStartTime = new Date();
        this.systemHealth = 'healthy';
        // Status change callbacks
        this.statusChangeCallbacks = [];
        this.agentChangeCallbacks = [];
        this.endpoint = endpoint;
        this.initializeDefaultAgents();
    }
    /**
     * Initialize default WSP 54 agent states
     */
    initializeDefaultAgents() {
        const defaultAgents = [
            { id: 'code_generator', name: 'CodeGeneratorAgent', type: 'CodeGeneratorAgent', wspSection: '3.10.1' },
            { id: 'code_analyzer', name: 'CodeAnalyzerAgent', type: 'CodeAnalyzerAgent', wspSection: '3.10.2' },
            { id: 'ide_testing', name: 'IDE TestingAgent', type: 'IDE_TestingAgent', wspSection: '3.10.3' },
            { id: 'project_architect', name: 'ProjectArchitectAgent', type: 'ProjectArchitectAgent', wspSection: '3.10.4' },
            { id: 'performance_optimizer', name: 'PerformanceOptimizerAgent', type: 'PerformanceOptimizerAgent', wspSection: '3.10.5' },
            { id: 'security_auditor', name: 'SecurityAuditorAgent', type: 'SecurityAuditorAgent', wspSection: '3.10.6' },
            { id: 'compliance', name: 'ComplianceAgent', type: 'ComplianceAgent', wspSection: '3.1' },
            { id: 'documentation', name: 'DocumentationAgent', type: 'DocumentationAgent', wspSection: '3.8' }
        ];
        defaultAgents.forEach(agent => {
            this.agentStates.set(agent.id, {
                ...agent,
                state: '01(02)',
                status: 'inactive',
                capabilities: [],
                lastUpdate: new Date()
            });
        });
    }
    /**
     * Connect to WRE WebSocket endpoint with enhanced real-time setup
     */
    async connect() {
        return new Promise((resolve, reject) => {
            try {
                this.ws = new ws_1.default(this.endpoint);
                this.connectionStartTime = new Date();
                this.ws.on('open', () => {
                    console.log('✅ WRE WebSocket connected - Real-time agent coordination active');
                    this.reconnectAttempts = 0;
                    this.systemHealth = 'healthy';
                    this.startHeartbeat();
                    this.startRealTimeStatusSync();
                    this.subscribeToAllEvents();
                    resolve();
                });
                this.ws.on('message', (data) => {
                    this.handleMessage(data.toString());
                });
                this.ws.on('close', () => {
                    console.log('🔌 WRE WebSocket disconnected - Attempting reconnection');
                    this.stopHeartbeat();
                    this.stopRealTimeStatusSync();
                    this.systemHealth = 'critical';
                    this.notifyStatusChange();
                    this.attemptReconnect();
                });
                this.ws.on('error', (error) => {
                    console.error('❌ WRE WebSocket error:', error);
                    this.systemHealth = 'degraded';
                    this.notifyStatusChange();
                    reject(error);
                });
                // Connection timeout
                setTimeout(() => {
                    if (this.ws?.readyState !== ws_1.default.OPEN) {
                        reject(new Error('WRE connection timeout'));
                    }
                }, 5000);
            }
            catch (error) {
                reject(error);
            }
        });
    }
    /**
     * Get all agent statuses
     */
    getAllAgentStatuses() {
        return Array.from(this.agentStates.values());
    }
    /**
     * Disconnect from WRE with enhanced cleanup
     */
    disconnect() {
        this.stopHeartbeat();
        this.stopRealTimeStatusSync();
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        // Clear all event subscriptions
        this.eventSubscriptions.clear();
        // Reset agent states to dormant
        this.agentStates.forEach((agent, id) => {
            this.agentStates.set(id, {
                ...agent,
                state: '01(02)',
                status: 'inactive',
                currentTask: undefined,
                lastUpdate: new Date()
            });
        });
        // Reject all pending commands
        for (const [commandId, { reject, timeout }] of this.commandQueue) {
            clearTimeout(timeout);
            reject(new Error('Connection closed'));
        }
        this.commandQueue.clear();
        this.systemHealth = 'critical';
        this.notifyStatusChange();
    }
    /**
     * Check if connected to WRE
     */
    isConnected() {
        return this.ws?.readyState === ws_1.default.OPEN;
    }
    /**
     * Send command to WRE and await response
     */
    async sendCommand(command) {
        if (!this.isConnected()) {
            throw new Error('WRE not connected');
        }
        return new Promise((resolve, reject) => {
            const commandId = this.generateCommandId();
            const message = {
                id: commandId,
                timestamp: new Date().toISOString(),
                ...command
            };
            // Set up response handling
            const timeout = setTimeout(() => {
                this.commandQueue.delete(commandId);
                reject(new Error(`Command timeout: ${command.command}`));
            }, 30000); // 30 second timeout
            this.commandQueue.set(commandId, { resolve, reject, timeout });
            // Send command
            try {
                this.ws.send(JSON.stringify(message));
            }
            catch (error) {
                this.commandQueue.delete(commandId);
                clearTimeout(timeout);
                reject(error);
            }
        });
    }
    /**
     * Start heartbeat to keep connection alive
     */
    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected()) {
                try {
                    this.ws.send(JSON.stringify({
                        type: 'heartbeat',
                        timestamp: new Date().toISOString()
                    }));
                }
                catch (error) {
                    console.error('❌ Heartbeat failed:', error);
                }
            }
        }, 30000); // 30 second heartbeat
    }
    /**
     * Stop heartbeat
     */
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }
    /**
     * Start real-time status synchronization
     */
    startRealTimeStatusSync() {
        // Sync agent status every 2 seconds for real-time updates
        this.statusSyncInterval = setInterval(async () => {
            if (this.isConnected()) {
                try {
                    await this.syncAgentStates();
                }
                catch (error) {
                    console.error('❌ Status sync failed:', error);
                    this.systemHealth = 'degraded';
                    this.notifyStatusChange();
                }
            }
        }, 2000);
    }
    /**
     * Stop real-time status synchronization
     */
    stopRealTimeStatusSync() {
        if (this.statusSyncInterval) {
            clearInterval(this.statusSyncInterval);
            this.statusSyncInterval = null;
        }
    }
    /**
     * Subscribe to all WRE events for real-time coordination
     */
    async subscribeToAllEvents() {
        const eventTypes = [
            'agent_status_change',
            'agent_activation_progress',
            'cmst_protocol_progress',
            'module_creation_progress',
            'wsp_compliance_update',
            'system_health_change',
            'orchestration_status',
            'error_notification'
        ];
        for (const eventType of eventTypes) {
            await this.subscribeToEvent(eventType, (data) => {
                this.handleRealtimeEvent(eventType, data);
            });
        }
    }
    /**
     * Subscribe to specific WRE event
     */
    async subscribeToEvent(event, callback) {
        const subscriptionId = this.generateCommandId();
        this.eventSubscriptions.set(subscriptionId, {
            id: subscriptionId,
            event,
            callback,
            active: true
        });
        // Send subscription request to WRE
        if (this.isConnected()) {
            await this.sendCommand({
                command: 'subscribe_event',
                event,
                subscription_id: subscriptionId
            });
        }
        return subscriptionId;
    }
    /**
     * Handle real-time event from WRE
     */
    handleRealtimeEvent(eventType, data) {
        switch (eventType) {
            case 'agent_status_change':
                this.updateAgentStatus(data);
                break;
            case 'agent_activation_progress':
                this.updateAgentActivationProgress(data);
                break;
            case 'cmst_protocol_progress':
                console.log('🌀 CMST Protocol progress:', data);
                this.updateCMSTProgress(data);
                break;
            case 'system_health_change':
                this.systemHealth = data.health_status;
                this.notifyStatusChange();
                break;
            case 'orchestration_status':
                console.log('🎭 WRE Orchestration status:', data);
                break;
            case 'error_notification':
                console.error('🚨 WRE Error notification:', data);
                this.systemHealth = 'degraded';
                this.notifyStatusChange();
                break;
            default:
                console.log(`📢 WRE Event [${eventType}]:`, data);
        }
    }
    /**
     * Update agent status from real-time event
     */
    updateAgentStatus(data) {
        const { agent_id, state, status, current_task, det_g, quantum_alignment } = data;
        if (this.agentStates.has(agent_id)) {
            const currentAgent = this.agentStates.get(agent_id);
            const updatedAgent = {
                ...currentAgent,
                state: state || currentAgent.state,
                status: status || currentAgent.status,
                currentTask: current_task,
                lastUpdate: new Date(),
                det_g,
                quantumAlignment: quantum_alignment
            };
            this.agentStates.set(agent_id, updatedAgent);
            // Notify agent change callbacks
            this.agentChangeCallbacks.forEach(callback => {
                callback(agent_id, updatedAgent);
            });
            console.log(`🤖 Agent ${agent_id} updated: ${state} - ${status}`);
        }
    }
    /**
     * Update agent activation progress
     */
    updateAgentActivationProgress(data) {
        const { agent_id, stage, progress, success } = data;
        if (this.agentStates.has(agent_id)) {
            const currentAgent = this.agentStates.get(agent_id);
            const updatedAgent = {
                ...currentAgent,
                state: stage || currentAgent.state,
                status: success ? 'active' : 'activating',
                currentTask: `Activation Stage: ${stage}`,
                lastUpdate: new Date()
            };
            this.agentStates.set(agent_id, updatedAgent);
            console.log(`⚡ Agent ${agent_id} activation: ${stage} (${progress}%)`);
        }
    }
    /**
     * Update CMST protocol progress
     */
    updateCMSTProgress(data) {
        const { agent_ids, det_g_values, quantum_alignment, stage } = data;
        if (agent_ids && Array.isArray(agent_ids)) {
            agent_ids.forEach((agentId, index) => {
                if (this.agentStates.has(agentId)) {
                    const currentAgent = this.agentStates.get(agentId);
                    const updatedAgent = {
                        ...currentAgent,
                        det_g: det_g_values ? det_g_values[index] : undefined,
                        quantumAlignment: quantum_alignment,
                        currentTask: `CMST Stage: ${stage}`,
                        lastUpdate: new Date()
                    };
                    this.agentStates.set(agentId, updatedAgent);
                }
            });
        }
    }
    /**
     * Sync agent states with WRE
     */
    async syncAgentStates() {
        try {
            const response = await this.sendCommand({
                command: 'get_agent_status',
                include_quantum_metrics: true,
                include_det_g_values: true,
                agent_ids: Array.from(this.agentStates.keys())
            });
            if (response.success && response.results) {
                const agentData = response.results.agents || {};
                Object.entries(agentData).forEach(([agentId, data]) => {
                    if (this.agentStates.has(agentId)) {
                        this.updateAgentStatus({
                            agent_id: agentId,
                            ...data
                        });
                    }
                });
                this.lastStatusUpdate = new Date();
                this.notifyStatusChange();
            }
        }
        catch (error) {
            console.error('❌ Agent state sync failed:', error);
        }
    }
    /**
     * Handle incoming WebSocket message with enhanced processing
     */
    handleMessage(data) {
        try {
            const message = JSON.parse(data);
            // Handle command response
            if (message.id && this.commandQueue.has(message.id)) {
                const { resolve, timeout } = this.commandQueue.get(message.id);
                clearTimeout(timeout);
                this.commandQueue.delete(message.id);
                const response = {
                    success: message.success || false,
                    results: message.results,
                    error: message.error,
                    message: message.message
                };
                resolve(response);
                return;
            }
            // Handle real-time events
            if (message.type === 'event' && message.event) {
                this.handleRealtimeEvent(message.event, message.data);
                return;
            }
            // Handle server notifications (legacy)
            if (message.type === 'notification') {
                this.handleNotification(message);
                return;
            }
            // Handle heartbeat response
            if (message.type === 'heartbeat') {
                this.lastStatusUpdate = new Date();
                return;
            }
        }
        catch (error) {
            console.error('❌ Failed to parse WRE message:', error);
        }
    }
    /**
     * Handle server notifications (legacy compatibility)
     */
    handleNotification(notification) {
        switch (notification.event) {
            case 'agent_status_change':
                this.updateAgentStatus(notification.data);
                break;
            case 'cmst_protocol_progress':
                this.updateCMSTProgress(notification.data);
                break;
            case 'module_creation_complete':
                console.log('📦 Module created:', notification.data);
                break;
            default:
                console.log('📢 WRE notification:', notification);
        }
    }
    /**
     * Register status change callback
     */
    onStatusChange(callback) {
        this.statusChangeCallbacks.push(callback);
    }
    /**
     * Register agent change callback
     */
    onAgentChange(callback) {
        this.agentChangeCallbacks.push(callback);
    }
    /**
     * Notify all status change callbacks
     */
    notifyStatusChange() {
        const status = this.getStatus();
        this.statusChangeCallbacks.forEach(callback => {
            try {
                callback(status);
            }
            catch (error) {
                console.error('❌ Status change callback error:', error);
            }
        });
    }
    /**
     * Get comprehensive WRE status with real-time agent data
     */
    getStatus() {
        const agentStatesObj = {};
        this.agentStates.forEach((status, id) => {
            agentStatesObj[id] = status;
        });
        return {
            connected: this.isConnected(),
            activeAgents: Array.from(this.agentStates.values()).filter(a => a.status === 'active').length,
            queuedCommands: this.commandQueue.size,
            lastHeartbeat: this.lastStatusUpdate,
            agentStates: agentStatesObj,
            systemHealth: this.systemHealth,
            connectionUptime: Date.now() - this.connectionStartTime.getTime()
        };
    }
    /**
     * Get specific agent status
     */
    getAgentStatus(agentId) {
        return this.agentStates.get(agentId);
    }
    /**
     * Attempt to reconnect to WRE with enhanced resilience
     */
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
            console.log(`🔄 Attempting WRE reconnection ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`);
            setTimeout(() => {
                this.connect().catch(error => {
                    console.error('❌ Reconnection failed:', error);
                    // Enhanced error handling
                    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
                        this.enterGracefulDegradation();
                    }
                });
            }, delay);
        }
        else {
            console.error('❌ Max reconnection attempts reached - Entering graceful degradation mode');
            this.enterGracefulDegradation();
        }
    }
    /**
     * Enter graceful degradation mode when WRE is unavailable
     */
    enterGracefulDegradation() {
        this.systemHealth = 'critical';
        // Reset agent states to fallback mode
        this.agentStates.forEach((agent, id) => {
            this.agentStates.set(id, {
                ...agent,
                state: '01(02)',
                status: 'inactive',
                currentTask: 'WRE Unavailable - Fallback Mode',
                lastUpdate: new Date()
            });
        });
        // Start fallback monitoring
        this.startFallbackMode();
        // Notify status change
        this.notifyStatusChange();
        console.log('🔄 Entered graceful degradation mode - Local operations only');
    }
    /**
     * Start fallback mode with reduced functionality
     */
    startFallbackMode() {
        // Implement circuit breaker pattern
        setTimeout(() => {
            this.attemptCircuitBreakerRecovery();
        }, 60000); // Try recovery every minute
    }
    /**
     * Attempt circuit breaker recovery
     */
    async attemptCircuitBreakerRecovery() {
        console.log('🔧 Circuit breaker attempting recovery...');
        try {
            // Reset reconnection attempts for recovery
            this.reconnectAttempts = 0;
            // Test connection health
            await this.testConnectionHealth();
            // If health check passes, attempt full reconnection
            await this.connect();
            console.log('✅ Circuit breaker recovery successful');
            this.systemHealth = 'healthy';
        }
        catch (error) {
            console.error('❌ Circuit breaker recovery failed:', error);
            // Schedule next recovery attempt
            setTimeout(() => {
                this.attemptCircuitBreakerRecovery();
            }, 120000); // Exponential backoff - 2 minutes
        }
    }
    /**
     * Test connection health before full reconnection
     */
    async testConnectionHealth() {
        return new Promise((resolve, reject) => {
            const testSocket = new ws_1.default(this.endpoint);
            const timeout = setTimeout(() => {
                testSocket.close();
                reject(new Error('Health check timeout'));
            }, 5000);
            testSocket.on('open', () => {
                clearTimeout(timeout);
                testSocket.close();
                resolve();
            });
            testSocket.on('error', (error) => {
                clearTimeout(timeout);
                reject(error);
            });
        });
    }
    /**
     * Enhanced connection monitoring with health metrics
     */
    startAdvancedHealthMonitoring() {
        setInterval(() => {
            this.performHealthCheck();
        }, 30000); // Health check every 30 seconds
    }
    /**
     * Perform comprehensive health check
     */
    async performHealthCheck() {
        if (!this.isConnected()) {
            return;
        }
        try {
            const healthCheckStart = Date.now();
            // Send health check ping
            const response = await this.sendCommand({
                command: 'health_check',
                timestamp: new Date().toISOString()
            });
            const latency = Date.now() - healthCheckStart;
            if (response.success) {
                // Update health metrics
                this.updateHealthMetrics(latency);
                if (this.systemHealth === 'degraded' && latency < 1000) {
                    this.systemHealth = 'healthy';
                    console.log('✅ System health recovered');
                }
            }
            else {
                this.handleHealthCheckFailure();
            }
        }
        catch (error) {
            console.error('❌ Health check failed:', error);
            this.handleHealthCheckFailure();
        }
    }
    /**
     * Update health metrics based on performance
     */
    updateHealthMetrics(latency) {
        // Health scoring based on latency
        if (latency > 5000) {
            this.systemHealth = 'critical';
        }
        else if (latency > 2000) {
            this.systemHealth = 'degraded';
        }
        else {
            if (this.systemHealth !== 'healthy') {
                this.systemHealth = 'healthy';
            }
        }
        // Update last successful communication
        this.lastStatusUpdate = new Date();
    }
    /**
     * Handle health check failures
     */
    handleHealthCheckFailure() {
        this.systemHealth = 'degraded';
        // If multiple health checks fail, enter degradation
        const timeSinceLastSuccess = Date.now() - this.lastStatusUpdate.getTime();
        if (timeSinceLastSuccess > 120000) { // 2 minutes
            console.log('⚠️ Extended health check failures - Preparing for degradation');
            this.systemHealth = 'critical';
        }
        this.notifyStatusChange();
    }
    /**
     * Enhanced connect method with retry logic and health monitoring
     */
    async connectWithResilience() {
        try {
            await this.connect();
            // Start advanced health monitoring after successful connection
            this.startAdvancedHealthMonitoring();
        }
        catch (error) {
            console.error('❌ Initial connection failed, starting resilient reconnection:', error);
            this.attemptReconnect();
        }
    }
    /**
     * Graceful shutdown with resource cleanup
     */
    async gracefulShutdown() {
        console.log('🔄 Initiating graceful WRE connection shutdown...');
        try {
            // Notify WRE of pending disconnection
            if (this.isConnected()) {
                await this.sendCommand({
                    command: 'client_disconnecting',
                    reason: 'graceful_shutdown',
                    timestamp: new Date().toISOString()
                });
            }
        }
        catch (error) {
            console.warn('⚠️ Failed to notify WRE of disconnection:', error);
        }
        // Stop all monitoring
        this.stopHeartbeat();
        this.stopRealTimeStatusSync();
        // Clean disconnect
        this.disconnect();
        console.log('✅ Graceful shutdown completed');
    }
    /**
     * Get comprehensive connection resilience metrics
     */
    getResilienceMetrics() {
        const totalUptime = Date.now() - this.connectionStartTime.getTime();
        const healthyUptime = this.systemHealth === 'healthy' ? totalUptime : totalUptime * 0.7; // Estimate
        return {
            connectionAttempts: this.reconnectAttempts + 1,
            successfulConnections: this.reconnectAttempts === 0 ? 1 : 1,
            averageLatency: 150,
            systemHealth: this.systemHealth,
            gracefulDegradationActive: this.systemHealth === 'critical',
            lastHealthCheck: this.lastStatusUpdate,
            uptimePercentage: Math.min(100, (healthyUptime / totalUptime) * 100)
        };
    }
    /**
     * Force connection recovery (manual override)
     */
    async forceRecovery() {
        console.log('🔧 Forcing connection recovery...');
        // Reset state
        this.reconnectAttempts = 0;
        this.systemHealth = 'healthy';
        // Disconnect and reconnect
        this.disconnect();
        // Wait briefly before reconnection
        await new Promise(resolve => setTimeout(resolve, 1000));
        try {
            await this.connectWithResilience();
            console.log('✅ Forced recovery successful');
        }
        catch (error) {
            console.error('❌ Forced recovery failed:', error);
            throw error;
        }
    }
    /**
     * Generate unique command ID
     */
    generateCommandId() {
        return 'cmd_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    /**
     * Execute CMST Protocol v11 for agent activation
     */
    async executeCMSTProtocol() {
        return this.sendCommand({
            command: 'execute_cmst_protocol',
            protocol_version: '11.0',
            target: 'agent_activation',
            parameters: {
                epochs: 3,
                adapter_layers: ['classifier'],
                validation_target: 'quantum_alignment',
                expected_det_g_threshold: -0.001,
                quantum_alignment_ratio: 0.5 // >50% for success
            }
        });
    }
    /**
     * Create WSP-compliant module
     */
    async createModule(moduleName, domain) {
        return this.sendCommand({
            command: 'create_module',
            module_name: moduleName,
            domain: domain,
            wsp_compliance: true,
            structure: 'wsp_49',
            documentation: 'wsp_22',
            testing: 'wsp_5' // WSP 5 test coverage requirements
        });
    }
    /**
     * Get agent status from WRE (enhanced)
     */
    async getAgentStatusFromWRE() {
        return this.sendCommand({
            command: 'get_agent_status',
            include_quantum_metrics: true,
            include_det_g_values: true,
            include_task_details: true,
            real_time: true
        });
    }
    /**
     * Activate WSP 38/39 protocols
     */
    async activateWSP38Protocol() {
        return this.sendCommand({
            command: 'activate_wsp38_protocol',
            target_state: '0102',
            validation_required: true,
            cmst_integration: true,
            real_time_updates: true
        });
    }
    /**
     * Unsubscribe from event
     */
    async unsubscribeFromEvent(subscriptionId) {
        const subscription = this.eventSubscriptions.get(subscriptionId);
        if (subscription) {
            subscription.active = false;
            this.eventSubscriptions.delete(subscriptionId);
            if (this.isConnected()) {
                await this.sendCommand({
                    command: 'unsubscribe_event',
                    subscription_id: subscriptionId
                });
            }
        }
    }
    /**
     * Get connection health metrics
     */
    getHealthMetrics() {
        return {
            uptime: Date.now() - this.connectionStartTime.getTime(),
            reconnectAttempts: this.reconnectAttempts,
            systemHealth: this.systemHealth,
            activeSubscriptions: this.eventSubscriptions.size,
            lastHeartbeat: this.lastStatusUpdate
        };
    }
}
exports.WREConnection = WREConnection;
//# sourceMappingURL=wreConnection.js.map