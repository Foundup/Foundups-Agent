/**
 * FoundUP Cube Animation Module
 *
 * Tells the FoundUP lifecycle story:
 * IDEA → SCAFFOLD → BUILD → PROMOTE → INVEST → CUSTOMERS → LAUNCH (MVP) → CELEBRATE → RESET
 *
 * Location: public/js/foundup-cube.js
 * Spec: public/cube-story-spec.md
 *
 * Phases:
 *   Phase 1 (current): Single-cube 45s deterministic loop
 *   Phase 2 (planned): Camera handoff to next cube spawn
 *   Phase 3 (planned): Multi-cube zoom-out with staggered states
 *   Phase 4 (planned): Simulator event integration (USE_SIM_EVENTS flag)
 *   Phase 5 (planned): Ticker/chat as event subscribers
 *
 * Usage:
 *   <canvas id="buildCanvas"></canvas>
 *   <script src="js/foundup-cube.js"></script>
 *   <script>FoundupCube.init('buildCanvas');</script>
 */

const FoundupCube = (function () {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // FROZEN STYLE CONSTANTS (DO NOT MODIFY - guardrail for visual consistency)
    // ═══════════════════════════════════════════════════════════════════════
    const STYLE = Object.freeze({
        // Color palette
        palette: Object.freeze({
            accent: '#7c5cfc',
            cyan: '#00e5d0',
            gold: '#f5a623',
            pink: '#ff4ea0',
            bg: '#08080f',
        }),

        // Face colors for cube blocks
        faceColors: Object.freeze([
            '#ff2d2d', '#ff8c00', '#ffd700', '#00b341', '#0066ff', '#9b59b6',
            '#00e5d0', '#ff6b9d', '#a855f7', '#22c55e'
        ]),

        // Agent type colors
        agentColors: Object.freeze({
            worker: '#ff3b3b',
            promoter: '#00e5d0',
            investor: '#ffd700',
            founder: '#f5a623',
        }),

        // WSP 27 priority level colors
        levelColors: Object.freeze({
            P0: '#ff2d2d',  // Elite - red
            P1: '#ff8c00',  // Senior - orange
            P2: '#ffd700',  // Mid - yellow
            P3: '#00b341',  // Junior - green
            P4: '#0066ff',  // Novice - blue
        }),

        // Easing functions
        easing: Object.freeze({
            quadInOut: (t) => t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2,
            quadOut: (t) => 1 - (1 - t) * (1 - t),
            linear: (t) => t,
        }),

        // Particle settings
        particles: Object.freeze({
            blockBurstCount: 8,
            confettiCount: 60,
            trailLength: 20,
            particleDecay: 0.03,
            confettiDecay: 0.015,
        }),

        // Camera settings (for future multi-cube phases)
        camera: Object.freeze({
            panSpeed: 0.02,      // Normalized units per frame
            zoomSpeed: 0.01,
            defaultScale: 15,
            minScale: 8,
            maxScale: 25,
        }),

        // Typography
        fonts: Object.freeze({
            status: '11px monospace',
            label: '10px monospace',
            announcement: 'bold 18px sans-serif',
            agentSymbol: 'bold 6px sans-serif',
        }),
    });

    // ═══════════════════════════════════════════════════════════════════════
    // FEATURE FLAGS
    // ═══════════════════════════════════════════════════════════════════════
    const FLAGS = {
        USE_SIM_EVENTS: false,  // Phase 4: Wire to simulator events
        ENABLE_TICKER: true,    // Phase 5: Event subscriber ticker (now active)
        ENABLE_CHAT: false,     // Phase 5: Event subscriber chat bubbles
        MULTI_CUBE: false,      // Phase 3: Multi-cube zoom-out
        DEBUG_TIMING: false,    // Log phase transitions
    };

    // ═══════════════════════════════════════════════════════════════════════
    // SIMULATOR EVENT BRIDGE (Phase 4)
    // ═══════════════════════════════════════════════════════════════════════
    const simBridge = {
        connected: false,
        eventSource: null,
        reconnectAttempts: 0,
        maxReconnectAttempts: 5,
        reconnectDelay: 2000,
        lastLifecycleStage: 'PoC',
        endpoint: '/api/sim-events',  // SSE endpoint when running with simulator
    };

    // Map simulator events to cube events (from modules/foundups/simulator/event_bus.py)
    const SIM_EVENT_MAP = {
        'foundup_created': (d) => ({ type: 'loop_started', data: { loopCount: 1, name: d.name } }),
        'task_state_changed': (d) => {
            if (d.new_state === 'claimed') return { type: 'agent_spawned', data: { type: 'worker', status: 'claiming...' } };
            if (d.new_state === 'submitted') return { type: 'block_filled', data: { x: 0, y: 0, z: 0, total: d.task_id } };
            if (d.new_state === 'verified') return { type: 'sim_security_audit', data: {} };
            if (d.new_state === 'paid') return { type: 'phase_changed', data: { phase: 'COMPLETE' } };
            return null;
        },
        'fi_trade_executed': (d) => ({ type: 'sim_dex_trade', data: { amount: d.fi_amount || d.amount || 100 } }),
        'investor_funding_received': (d) => ({ type: 'sim_investor_funding', data: { amount: d.ups_amount || d.amount || 1000 } }),
        'milestone_published': (d) => ({ type: 'dao_launched', data: { milestone: d.milestone || 'MVP' } }),
        'lifecycle_changed': (d) => {
            if (d.stage === 'Proto') return { type: 'phase_changed', data: { phase: 'BUILDING' } };
            if (d.stage === 'MVP') return { type: 'phase_changed', data: { phase: 'LAUNCH' } };
            return null;
        },
        'customer_arrived': (d) => ({ type: 'customers_arrived', data: { count: d.count || 1 } }),
    };

    function connectSimulatorBridge() {
        if (!FLAGS.USE_SIM_EVENTS || simBridge.connected) return;

        try {
            simBridge.eventSource = new EventSource(simBridge.endpoint);

            simBridge.eventSource.onopen = () => {
                simBridge.connected = true;
                simBridge.reconnectAttempts = 0;
                console.log('[CUBE] Simulator bridge connected');
                addTickerMessage('sim_connected', {});
            };

            simBridge.eventSource.onmessage = (event) => {
                try {
                    const simEvent = JSON.parse(event.data);
                    handleSimulatorEvent(simEvent);
                } catch (e) {
                    console.warn('[CUBE] Invalid simulator event:', e);
                }
            };

            simBridge.eventSource.onerror = () => {
                simBridge.connected = false;
                simBridge.eventSource.close();

                if (simBridge.reconnectAttempts < simBridge.maxReconnectAttempts) {
                    simBridge.reconnectAttempts++;
                    setTimeout(connectSimulatorBridge, simBridge.reconnectDelay);
                }
            };
        } catch (e) {
            console.warn('[CUBE] Simulator bridge unavailable:', e.message);
        }
    }

    function handleSimulatorEvent(simEvent) {
        const mapper = SIM_EVENT_MAP[simEvent.type];
        if (!mapper) return;

        const mapped = mapper(simEvent.data || {});
        if (!mapped) return;

        // Emit as internal cube event
        emitEvent(mapped.type, mapped.data);

        // Track lifecycle stage changes
        if (simEvent.type === 'lifecycle_changed') {
            simBridge.lastLifecycleStage = simEvent.data.stage;
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // CONFIGURATION
    // ═══════════════════════════════════════════════════════════════════════
    const CONFIG = {
        targetSize: 4,          // 4x4x4 cube
        agentSpawnRate: 0.012,
        maxAgents: 15,
        fiPerBlock: 50,
        loopDuration: 45000,    // 45s total loop
    };

    // ═══════════════════════════════════════════════════════════════════════
    // PHASE DEFINITIONS (45s deterministic loop)
    // ═══════════════════════════════════════════════════════════════════════
    // Story Arc: IDEA → SCAFFOLD → BUILD → PROMOTE → INVEST → CUSTOMERS → LAUNCH (DAO/MVP)
    // Total: 3+4+18+4+4+4+5+3+0 = 45s
    const PHASES = {
        IDEA:      { duration: 3000,  next: 'SCAFFOLD' },   // 0-3s: Founder appears
        SCAFFOLD:  { duration: 4000,  next: 'BUILDING' },   // 3-7s: Wireframe, planners spawn
        BUILDING:  { duration: 18000, next: 'COMPLETE' },   // 7-25s: Main build phase
        COMPLETE:  { duration: 0,     next: 'PROMOTING' },  // 25s: Instant transition
        PROMOTING: { duration: 4000,  next: 'INVESTOR' },   // 25-29s: Promoter goes out
        INVESTOR:  { duration: 4000,  next: 'CUSTOMERS' },  // 29-33s: Investor arrives
        CUSTOMERS: { duration: 4000,  next: 'LAUNCH' },     // 33-37s: Customers join, growth
        LAUNCH:    { duration: 5000,  next: 'CELEBRATE' },  // 37-42s: DAO/MVP launched
        CELEBRATE: { duration: 3000,  next: 'RESET' },      // 42-45s: Celebration
        RESET:     { duration: 0,     next: 'IDEA' },       // 45s: Instant reset
    };

    // ═══════════════════════════════════════════════════════════════════════
    // STATE
    // ═══════════════════════════════════════════════════════════════════════
    let canvas, ctx, w, h;
    let currentPhase = 'IDEA';
    let phaseStartTime = 0;
    let loopStartTime = 0;
    let time = 0;
    let fiEarned = 0;
    let loopCount = 0;

    const agents = [];
    const filledBlocks = new Set();
    const confetti = [];
    const particles = [];

    // Event subscribers (Phase 5)
    const eventSubscribers = [];

    // Camera state (Phase 2/3)
    const camera = {
        x: 0,
        y: 0,
        scale: STYLE.camera.defaultScale,
        targetX: 0,
        targetY: 0,
        targetScale: STYLE.camera.defaultScale,
    };

    // Camera handoff state (Phase 2: camera pans between cubes)
    const cameraHandoff = {
        enabled: false,          // Activate after FLAGS.MULTI_CUBE or 3rd loop
        cubeCount: 0,            // Number of completed cubes
        maxCubesBeforeZoom: 3,   // After 3 cubes, zoom out to reveal all
        isTransitioning: false,  // True during pan animation
        transitionProgress: 0,   // 0-1 pan progress
        transitionDuration: 2000, // ms for pan animation
        cubePositions: [],       // [{x, y, scale, loopCount, phase}]
        zoomedOut: false,        // True when showing all cubes
    };

    // Ticker state (Phase 5 preview - always active)
    const ticker = {
        messages: [],
        maxMessages: 20,
        scrollOffset: 0,
        speed: 0.8,
    };

    // Ticker message templates by activity
    const TICKER_MESSAGES = {
        agent_spawned: (d) => `${d.type} joins the build...`,
        agent_recruited: (d) => `new ${d.type} recruited!`,
        block_filled: (d) => `block ${d.x},${d.y},${d.z} built (${d.total}/64)`,
        phase_changed: (d) => `phase: ${d.phase}`,
        promoter_recruited: (d) => `promoter brought ${d.count} agents!`,
        investor_arrived: () => `investor enters with capital`,
        customers_arrived: (d) => `${d.count} customers arrived!`,
        dao_launched: () => `MVP LAUNCHED!`,
        cube_complete: () => `cube complete - all 64 blocks built`,
        loop_started: (d) => `new foundup #${d.loopCount} starting...`,
        // Simulated activity messages
        sim_holo_indexing: () => `agent holo indexing...`,
        sim_planning: () => `agent planning architecture...`,
        sim_researching: () => `agent researching solutions...`,
        sim_creating_collaterals: () => `agent creating collaterals...`,
        sim_security_audit: () => `agent performing security audit...`,
        sim_promoting: () => `agent promoting foundup...`,
        sim_dex_trade: (d) => `DEX: ${d.amount || '100'} F_i traded`,
        sim_investor_funding: (d) => `investor: ${d.amount || '1000'} UP$ funded`,
        sim_connected: () => `simulator connected - live events active`,
    };

    // ═══════════════════════════════════════════════════════════════════════
    // AGENT BEHAVIORS (WSP 54 roles)
    // ═══════════════════════════════════════════════════════════════════════
    const BEHAVIORS = {
        normal: { weight: 0.7, speedMod: 1.0 },
        eager: { weight: 0.15, speedMod: 1.5 },
        methodical: { weight: 0.1, speedMod: 0.6 },
        chaotic: { weight: 0.05, speedMod: 1.2 },
    };

    const QUIRKS = {
        spazOut: 0.02,
        wander: 0.03,
        celebrate: 0.01,
        recruit: 0.5,  // 50% chance promoter returns with agents after spazzing
    };

    // ═══════════════════════════════════════════════════════════════════════
    // UTILITY FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════
    function isoProject(x, y, z, ox, oy, s) {
        const ix = (x - y) * s * 0.866;
        const iy = (x + y) * s * 0.5 - z * s;
        return { x: ox + ix, y: oy + iy };
    }

    function shadeColor(color, percent) {
        const num = parseInt(color.replace('#', ''), 16);
        const amt = Math.round(2.55 * percent);
        const R = Math.min(255, Math.max(0, (num >> 16) + amt));
        const G = Math.min(255, Math.max(0, ((num >> 8) & 0x00FF) + amt));
        const B = Math.min(255, Math.max(0, (num & 0x0000FF) + amt));
        return `rgb(${R},${G},${B})`;
    }

    function pickBehavior() {
        const roll = Math.random();
        let cumulative = 0;
        for (const [name, data] of Object.entries(BEHAVIORS)) {
            cumulative += data.weight;
            if (roll < cumulative) return name;
        }
        return 'normal';
    }

    function emitEvent(type, data) {
        const event = { type, data, timestamp: Date.now(), phase: currentPhase };
        eventSubscribers.forEach(fn => {
            try { fn(event); } catch (e) { console.error('Event subscriber error:', e); }
        });
        // Auto-add to ticker if template exists
        addTickerMessage(type, data);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // TICKER FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════
    function addTickerMessage(type, data) {
        const template = TICKER_MESSAGES[type];
        if (!template) return;

        const text = template(data || {});
        ticker.messages.push({
            text,
            timestamp: Date.now(),
            x: w + 10, // Start off-screen right
        });

        // Limit messages
        while (ticker.messages.length > ticker.maxMessages) {
            ticker.messages.shift();
        }
    }

    function updateTicker() {
        // Move all messages left
        ticker.messages.forEach(m => {
            m.x -= ticker.speed;
        });

        // Remove messages that have scrolled off-screen
        ticker.messages = ticker.messages.filter(m => m.x > -400);

        // Add simulated activity messages during BUILD phase
        if (currentPhase === 'BUILDING' && Math.random() < 0.005) {
            const simTypes = [
                'sim_holo_indexing', 'sim_planning', 'sim_researching',
                'sim_creating_collaterals', 'sim_security_audit'
            ];
            const simType = simTypes[Math.floor(Math.random() * simTypes.length)];
            addTickerMessage(simType, {});
        }

        // Add promoting messages during PROMOTING phase
        if (currentPhase === 'PROMOTING' && Math.random() < 0.02) {
            addTickerMessage('sim_promoting', {});
        }
    }

    function drawTicker() {
        if (ticker.messages.length === 0) return;

        const tickerY = h - 40;
        const tickerHeight = 20;

        // Semi-transparent background bar
        ctx.fillStyle = 'rgba(8, 8, 15, 0.8)';
        ctx.fillRect(0, tickerY - 2, w, tickerHeight + 4);

        // Top border glow
        const borderGrd = ctx.createLinearGradient(0, tickerY - 2, w, tickerY - 2);
        borderGrd.addColorStop(0, 'rgba(124, 92, 252, 0)');
        borderGrd.addColorStop(0.5, 'rgba(124, 92, 252, 0.5)');
        borderGrd.addColorStop(1, 'rgba(124, 92, 252, 0)');
        ctx.fillStyle = borderGrd;
        ctx.fillRect(0, tickerY - 2, w, 1);

        // Draw messages
        ctx.font = '11px monospace';
        ctx.textBaseline = 'middle';

        ticker.messages.forEach((m, i) => {
            // Calculate alpha based on age
            const age = Date.now() - m.timestamp;
            const alpha = Math.min(1, Math.max(0.3, 1 - age / 30000));

            // Color based on message type
            let color = `rgba(228, 226, 236, ${alpha * 0.8})`;
            if (m.text.includes('MVP') || m.text.includes('LAUNCH')) {
                color = `rgba(255, 215, 0, ${alpha})`;
            } else if (m.text.includes('investor')) {
                color = `rgba(255, 215, 0, ${alpha * 0.9})`;
            } else if (m.text.includes('customer')) {
                color = `rgba(0, 229, 208, ${alpha * 0.9})`;
            } else if (m.text.includes('recruited') || m.text.includes('joins')) {
                color = `rgba(0, 229, 208, ${alpha * 0.7})`;
            }

            ctx.fillStyle = color;
            ctx.fillText(m.text, m.x, tickerY + tickerHeight / 2);
        });
    }

    // ═══════════════════════════════════════════════════════════════════════
    // CAMERA HANDOFF (Phase 2)
    // After cube completes, pan camera to next spawn position
    // Repeat 3 times, then zoom out to reveal all cubes
    // ═══════════════════════════════════════════════════════════════════════
    function updateCamera() {
        // Smooth camera movement toward target
        const lerpSpeed = 0.05;
        camera.x += (camera.targetX - camera.x) * lerpSpeed;
        camera.y += (camera.targetY - camera.y) * lerpSpeed;
        camera.scale += (camera.targetScale - camera.scale) * lerpSpeed;

        // Update handoff transition
        if (cameraHandoff.isTransitioning) {
            cameraHandoff.transitionProgress += 16 / cameraHandoff.transitionDuration;
            if (cameraHandoff.transitionProgress >= 1) {
                cameraHandoff.transitionProgress = 1;
                cameraHandoff.isTransitioning = false;
            }
        }
    }

    function triggerCameraHandoff() {
        if (!FLAGS.MULTI_CUBE) return;

        // Save current cube position
        cameraHandoff.cubePositions.push({
            x: camera.x,
            y: camera.y,
            scale: camera.scale,
            loopCount: loopCount,
            phase: 'COMPLETE',
        });

        cameraHandoff.cubeCount++;

        // After maxCubesBeforeZoom, zoom out to show all
        if (cameraHandoff.cubeCount >= cameraHandoff.maxCubesBeforeZoom && !cameraHandoff.zoomedOut) {
            triggerZoomOut();
            return;
        }

        // Pan camera to new position for next cube
        cameraHandoff.isTransitioning = true;
        cameraHandoff.transitionProgress = 0;

        // New cube spawns offset from previous
        const offsetX = (cameraHandoff.cubeCount % 2 === 0) ? -200 : 200;
        const offsetY = 50 * cameraHandoff.cubeCount;
        camera.targetX = offsetX;
        camera.targetY = offsetY;

        emitEvent('camera_handoff', { cubeCount: cameraHandoff.cubeCount });
    }

    function triggerZoomOut() {
        cameraHandoff.zoomedOut = true;
        cameraHandoff.isTransitioning = true;
        cameraHandoff.transitionProgress = 0;

        // Zoom out to show all cubes
        camera.targetScale = STYLE.camera.minScale;
        camera.targetX = 0;
        camera.targetY = 0;

        emitEvent('zoom_out', { cubeCount: cameraHandoff.cubeCount });
        addTickerMessage('phase_changed', { phase: 'ECOSYSTEM VIEW' });
    }

    function getCameraOffset() {
        // Returns camera offset for drawing
        return {
            x: camera.x,
            y: camera.y,
            scale: camera.scale,
        };
    }

    // ═══════════════════════════════════════════════════════════════════════
    // DRAWING FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════
    function drawCubelet(x, y, z, ox, oy, s, color, alpha = 1) {
        const p1 = isoProject(x, y, z, ox, oy, s);
        const p2 = isoProject(x + 1, y, z, ox, oy, s);
        const p3 = isoProject(x + 1, y + 1, z, ox, oy, s);
        const p4 = isoProject(x, y + 1, z, ox, oy, s);
        const p5 = isoProject(x, y, z + 1, ox, oy, s);
        const p6 = isoProject(x + 1, y, z + 1, ox, oy, s);
        const p7 = isoProject(x + 1, y + 1, z + 1, ox, oy, s);
        const p8 = isoProject(x, y + 1, z + 1, ox, oy, s);

        ctx.globalAlpha = alpha;

        // Top face
        ctx.beginPath();
        ctx.moveTo(p5.x, p5.y);
        ctx.lineTo(p6.x, p6.y);
        ctx.lineTo(p7.x, p7.y);
        ctx.lineTo(p8.x, p8.y);
        ctx.closePath();
        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = 'rgba(255,255,255,0.15)';
        ctx.lineWidth = 0.5;
        ctx.stroke();

        // Left face
        ctx.beginPath();
        ctx.moveTo(p4.x, p4.y);
        ctx.lineTo(p8.x, p8.y);
        ctx.lineTo(p7.x, p7.y);
        ctx.lineTo(p3.x, p3.y);
        ctx.closePath();
        ctx.fillStyle = shadeColor(color, -20);
        ctx.fill();
        ctx.stroke();

        // Right face
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p5.x, p5.y);
        ctx.lineTo(p8.x, p8.y);
        ctx.lineTo(p4.x, p4.y);
        ctx.closePath();
        ctx.fillStyle = shadeColor(color, -40);
        ctx.fill();
        ctx.stroke();

        ctx.globalAlpha = 1;
    }

    function drawWireframeCube(ox, oy, size, scale, alpha) {
        ctx.strokeStyle = `rgba(124, 92, 252, ${alpha})`;
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 4]);

        const offset = size / 2;
        const corners = [];

        for (let x = 0; x <= 1; x++) {
            for (let y = 0; y <= 1; y++) {
                for (let z = 0; z <= 1; z++) {
                    corners.push(isoProject(
                        x * size - offset,
                        y * size - offset,
                        z * size,
                        ox, oy, scale
                    ));
                }
            }
        }

        const edges = [
            [0, 1], [0, 2], [1, 3], [2, 3],
            [4, 5], [4, 6], [5, 7], [6, 7],
            [0, 4], [1, 5], [2, 6], [3, 7],
        ];

        edges.forEach(([a, b]) => {
            ctx.beginPath();
            ctx.moveTo(corners[a].x, corners[a].y);
            ctx.lineTo(corners[b].x, corners[b].y);
            ctx.stroke();
        });

        ctx.setLineDash([]);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // AGENT MANAGEMENT
    // ═══════════════════════════════════════════════════════════════════════
    function spawnAgent(type = 'worker', status = 'building...') {
        const angle = Math.random() * Math.PI * 2;
        const dist = 150 + Math.random() * 100;
        const sx = w / 2 + Math.cos(angle) * dist;
        const sy = h * 0.45 + Math.sin(angle) * dist * 0.5;
        const behavior = pickBehavior();

        const agent = {
            id: 'agent_' + Math.random().toString(36).substr(2, 6),
            sx, sy,
            x: sx, y: sy,
            tx: w / 2 + (Math.random() - 0.5) * 60,
            ty: h * 0.45 + (Math.random() - 0.5) * 40,
            progress: 0,
            speed: (0.005 + Math.random() * 0.005) * BEHAVIORS[behavior].speedMod,
            size: type === 'investor' ? 10 : (type === 'founder' ? 8 : 6),
            type,
            status,
            color: STYLE.agentColors[type] || STYLE.agentColors.worker,
            trail: [],
            showLabel: true,
            behavior,
            fiEarned: 0,
            level: 'P4',
            isSpazzing: false,
            spazTimer: 0,
            recruitCount: 0,
        };

        agents.push(agent);
        emitEvent('agent_spawned', { agent: agent.id, type, status });
        return agent;
    }

    function spawnAgentNear(nearX, nearY, type, status) {
        const angle = Math.random() * Math.PI * 2;
        const dist = 30 + Math.random() * 20;
        const sx = nearX + Math.cos(angle) * dist;
        const sy = nearY + Math.sin(angle) * dist;
        const behavior = pickBehavior();

        const agent = {
            id: 'agent_' + Math.random().toString(36).substr(2, 6),
            sx, sy,
            x: sx, y: sy,
            tx: w / 2 + (Math.random() - 0.5) * 60,
            ty: h * 0.45 + (Math.random() - 0.5) * 40,
            progress: 0,
            speed: (0.005 + Math.random() * 0.005) * BEHAVIORS[behavior].speedMod,
            size: 6,
            type,
            status,
            color: STYLE.agentColors[type] || STYLE.agentColors.worker,
            trail: [],
            showLabel: true,
            behavior,
            fiEarned: 0,
            level: 'P4',
            isSpazzing: false,
            spazTimer: 0,
            recruitCount: 0,
        };

        agents.push(agent);
        emitEvent('agent_recruited', { agent: agent.id, type });
        return agent;
    }

    function updateAgentBehaviors() {
        agents.forEach(a => {
            // Spaz out behavior
            if (!a.isSpazzing && (a.behavior === 'chaotic' || a.type === 'promoter')) {
                if (Math.random() < QUIRKS.spazOut) {
                    a.isSpazzing = true;
                    a.spazTimer = 60 + Math.random() * 60;
                    a.status = a.type === 'promoter' ? 'PROMOTING!!!' : 'excited!!!';
                    emitEvent('agent_spazzing', { agent: a.id });
                }
            }

            if (a.isSpazzing) {
                a.spazTimer--;
                a.x += (Math.random() - 0.5) * 8;
                a.y += (Math.random() - 0.5) * 8;
                a.x = Math.max(20, Math.min(w - 20, a.x));
                a.y = Math.max(20, Math.min(h - 20, a.y));

                if (a.spazTimer <= 0) {
                    a.isSpazzing = false;
                    a.status = a.type === 'promoter' ? 'promoting...' : 'building...';

                    // Promoter returns with recruits
                    if (a.type === 'promoter' && Math.random() < QUIRKS.recruit) {
                        const recruits = 1 + Math.floor(Math.random() * 3);
                        a.recruitCount += recruits;
                        a.status = `recruited ${recruits}!`;
                        emitEvent('promoter_recruited', { count: recruits });
                        for (let i = 0; i < recruits; i++) {
                            setTimeout(() => spawnAgentNear(a.x, a.y, 'worker', 'joining...'), i * 200);
                        }
                    }
                }
            }

            // Random celebration
            if (!a.isSpazzing && Math.random() < QUIRKS.celebrate) {
                const originalSize = a.size;
                a.size = a.size * 1.5;
                setTimeout(() => { a.size = originalSize; }, 300);
            }
        });
    }

    function updateAgents() {
        for (let i = agents.length - 1; i >= 0; i--) {
            const a = agents[i];
            if (a.isSpazzing) continue; // Skip normal movement when spazzing

            a.progress += a.speed;

            if (a.progress >= 1) {
                a.progress = 0;
                const angle = Math.random() * Math.PI * 2;
                const dist = 30 + Math.random() * 40;
                a.sx = a.x;
                a.sy = a.y;
                a.tx = w / 2 + Math.cos(angle) * dist;
                a.ty = h * 0.45 + Math.sin(angle) * dist * 0.5;

                if (currentPhase === 'BUILDING') {
                    fillRandomBlock();
                }
            }

            const t = STYLE.easing.quadInOut(a.progress);
            a.x = a.sx + (a.tx - a.sx) * t;
            a.y = a.sy + (a.ty - a.sy) * t;

            if (a.type === 'investor') {
                a.trail.push({ x: a.x, y: a.y });
                if (a.trail.length > STYLE.particles.trailLength) a.trail.shift();
            }
        }
    }

    function drawAgents() {
        agents.forEach(a => {
            // Draw trail for investors
            if (a.type === 'investor' && a.trail.length > 0) {
                for (let i = 0; i < a.trail.length; i++) {
                    const t = a.trail[i];
                    const alpha = (i / a.trail.length) * 0.5;
                    ctx.beginPath();
                    ctx.arc(t.x, t.y, 3, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(255, 215, 0, ${alpha})`;
                    ctx.fill();
                }
            }

            // Draw agent dot with gradient
            ctx.beginPath();
            ctx.arc(a.x, a.y, a.size, 0, Math.PI * 2);
            const grd = ctx.createRadialGradient(a.x, a.y, 0, a.x, a.y, a.size);
            grd.addColorStop(0, a.color);
            grd.addColorStop(1, shadeColor(a.color, -30));
            ctx.fillStyle = grd;
            ctx.fill();

            // Glow effect
            ctx.shadowColor = a.color;
            ctx.shadowBlur = a.isSpazzing ? 20 : 10;
            ctx.fill();
            ctx.shadowBlur = 0;

            // Icon based on type
            ctx.fillStyle = '#fff';
            ctx.font = STYLE.fonts.agentSymbol;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            const icons = { founder: '★', worker: '$', promoter: '↗', investor: '₿' };
            ctx.fillText(icons[a.type] || '$', a.x, a.y);

            // Status label
            if (a.showLabel) {
                ctx.font = STYLE.fonts.label;
                ctx.fillStyle = 'rgba(255,255,255,0.7)';
                ctx.fillText(a.status, a.x, a.y + a.size + 12);
            }
        });
    }

    // ═══════════════════════════════════════════════════════════════════════
    // BLOCK FILLING
    // ═══════════════════════════════════════════════════════════════════════
    function fillRandomBlock() {
        const size = CONFIG.targetSize;
        let attempts = 0;

        while (attempts < 20) {
            const x = Math.floor(Math.random() * size);
            const y = Math.floor(Math.random() * size);
            const z = Math.floor(Math.random() * size);
            const key = `${x},${y},${z}`;

            if (!filledBlocks.has(key)) {
                filledBlocks.add(key);
                fiEarned += CONFIG.fiPerBlock;
                spawnBlockParticles(x, y, z);
                emitEvent('block_filled', { x, y, z, total: filledBlocks.size });
                return;
            }
            attempts++;
        }
    }

    function spawnBlockParticles(bx, by, bz) {
        const cx = w / 2, cy = h * 0.45;
        const scale = camera.scale;
        const offset = CONFIG.targetSize / 2;
        const pos = isoProject(bx - offset, by - offset, bz + 0.5, cx, cy, scale);

        for (let i = 0; i < STYLE.particles.blockBurstCount; i++) {
            particles.push({
                x: pos.x, y: pos.y,
                vx: (Math.random() - 0.5) * 4,
                vy: (Math.random() - 0.5) * 4 - 2,
                life: 1,
                color: STYLE.faceColors[Math.floor(Math.random() * STYLE.faceColors.length)],
            });
        }
    }

    function updateParticles() {
        for (let i = particles.length - 1; i >= 0; i--) {
            const p = particles[i];
            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.1;
            p.life -= STYLE.particles.particleDecay;
            if (p.life <= 0) particles.splice(i, 1);
        }
    }

    function drawParticles() {
        particles.forEach(p => {
            ctx.beginPath();
            ctx.arc(p.x, p.y, 3 * p.life, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.globalAlpha = p.life;
            ctx.fill();
            ctx.globalAlpha = 1;
        });
    }

    // ═══════════════════════════════════════════════════════════════════════
    // CONFETTI
    // ═══════════════════════════════════════════════════════════════════════
    function spawnConfetti() {
        const cx = w / 2, cy = h * 0.35;
        for (let i = 0; i < STYLE.particles.confettiCount; i++) {
            confetti.push({
                x: cx, y: cy,
                vx: (Math.random() - 0.5) * 12,
                vy: (Math.random() - 0.5) * 12 - 8,
                color: STYLE.faceColors[Math.floor(Math.random() * STYLE.faceColors.length)],
                life: 1,
                rotation: Math.random() * Math.PI * 2,
                rotationSpeed: (Math.random() - 0.5) * 0.3,
            });
        }
    }

    function updateConfetti() {
        for (let i = confetti.length - 1; i >= 0; i--) {
            const c = confetti[i];
            c.x += c.vx;
            c.y += c.vy;
            c.vy += 0.15;
            c.vx *= 0.99;
            c.rotation += c.rotationSpeed;
            c.life -= STYLE.particles.confettiDecay;
            if (c.life <= 0) confetti.splice(i, 1);
        }
    }

    function drawConfetti() {
        confetti.forEach(c => {
            ctx.save();
            ctx.translate(c.x, c.y);
            ctx.rotate(c.rotation);
            ctx.fillStyle = c.color;
            ctx.globalAlpha = c.life;
            ctx.fillRect(-4, -2, 8, 4);
            ctx.restore();
        });
        ctx.globalAlpha = 1;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // PHASE MANAGEMENT
    // ═══════════════════════════════════════════════════════════════════════
    function updatePhase() {
        const elapsed = Date.now() - phaseStartTime;
        const phase = PHASES[currentPhase];

        if (elapsed >= phase.duration) {
            const nextPhase = phase.next;
            if (FLAGS.DEBUG_TIMING) {
                console.log(`[CUBE] Phase transition: ${currentPhase} → ${nextPhase} at ${Date.now() - loopStartTime}ms`);
            }
            currentPhase = nextPhase;
            phaseStartTime = Date.now();
            onPhaseChange(nextPhase);
            emitEvent('phase_changed', { phase: nextPhase, loopTime: Date.now() - loopStartTime });
        }
    }

    function onPhaseChange(phase) {
        const size = CONFIG.targetSize;

        switch (phase) {
            case 'IDEA':
                // New loop begins
                loopCount++;
                loopStartTime = Date.now();
                agents.length = 0;
                filledBlocks.clear();
                confetti.length = 0;
                particles.length = 0;
                fiEarned = 0;
                // Founder appears center
                const founder = spawnAgent('founder', 'ideating...');
                founder.x = w / 2;
                founder.y = h * 0.45;
                founder.sx = w / 2;
                founder.sy = h * 0.45;
                emitEvent('loop_started', { loopCount });
                break;

            case 'SCAFFOLD':
                // Planners spawn around founder
                spawnAgent('worker', 'planning...');
                spawnAgent('worker', 'researching...');
                break;

            case 'BUILDING':
                // Add builders
                spawnAgent('worker', 'building...');
                spawnAgent('worker', 'coding...');
                spawnAgent('worker', 'designing...');
                break;

            case 'COMPLETE':
                // Fill all remaining blocks instantly
                for (let x = 0; x < size; x++) {
                    for (let y = 0; y < size; y++) {
                        for (let z = 0; z < size; z++) {
                            filledBlocks.add(`${x},${y},${z}`);
                        }
                    }
                }
                agents.forEach(a => a.status = 'done!');
                emitEvent('cube_complete', { blocks: size * size * size, fiEarned });
                break;

            case 'PROMOTING':
                // First worker becomes promoter
                if (agents.length > 1) {
                    const promoter = agents[1]; // Skip founder
                    promoter.type = 'promoter';
                    promoter.color = STYLE.agentColors.promoter;
                    promoter.status = 'promoting...';
                    promoter.tx = w - 80;
                    promoter.ty = h * 0.3;
                }
                break;

            case 'INVESTOR':
                // Gold investor arrives from right
                const investor = spawnAgent('investor', 'investing...');
                investor.sx = w + 50;
                investor.x = w + 50;
                investor.ty = h * 0.4;
                emitEvent('investor_arrived', { agent: investor.id });
                break;

            case 'CUSTOMERS':
                // Customers join - more agents spawn (users/customers)
                spawnAgent('worker', 'customer!');
                setTimeout(() => spawnAgent('worker', 'user joined!'), 600);
                setTimeout(() => spawnAgent('worker', 'trying it...'), 1200);
                setTimeout(() => spawnAgent('worker', 'paying!'), 1800);
                agents.forEach(a => {
                    if (a.type === 'worker' && a.status !== 'customer!' && a.status !== 'user joined!' && a.status !== 'trying it...' && a.status !== 'paying!') {
                        a.status = 'growing...';
                    }
                });
                emitEvent('customers_arrived', { count: 4 });
                break;

            case 'LAUNCH':
                // DAO/MVP Launch - PoC → Proto → MVP complete
                spawnConfetti();
                agents.forEach(a => a.status = 'MVP live!');
                emitEvent('dao_launched', { agents: agents.length, fiEarned, milestone: 'MVP' });
                break;

            case 'CELEBRATE':
                // Continue celebration, spawn more confetti
                setTimeout(() => spawnConfetti(), 1000);
                break;

            case 'RESET':
                // Trigger camera handoff if multi-cube mode enabled
                if (FLAGS.MULTI_CUBE) {
                    triggerCameraHandoff();
                }
                // Loops back to IDEA via phase transition
                break;
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // WSP IMPORTANCE COLOR MAPPING
    // Maps block position to WSP module importance (P0=critical, P4=low)
    // ═══════════════════════════════════════════════════════════════════════
    function getWSPImportanceColor(x, y, z, size) {
        // Layer-based importance: bottom layers = foundation (P0), top = features (P4)
        // Center blocks more important than edges
        const centerDist = Math.abs(x - size/2 + 0.5) + Math.abs(y - size/2 + 0.5);
        const layerImportance = z / (size - 1); // 0 = bottom, 1 = top
        const centerImportance = 1 - (centerDist / size);

        // Combine: bottom-center = P0, top-edge = P4
        const importance = (1 - layerImportance) * 0.6 + centerImportance * 0.4;

        if (importance > 0.8) return STYLE.levelColors.P0;      // Elite - red
        if (importance > 0.6) return STYLE.levelColors.P1;      // Senior - orange
        if (importance > 0.4) return STYLE.levelColors.P2;      // Mid - yellow
        if (importance > 0.2) return STYLE.levelColors.P3;      // Junior - green
        return STYLE.levelColors.P4;                             // Novice - blue
    }

    // ═══════════════════════════════════════════════════════════════════════
    // DRAWING
    // ═══════════════════════════════════════════════════════════════════════
    function drawCube() {
        const cx = w / 2;
        const cy = h * 0.45;
        const size = CONFIG.targetSize;
        const scale = camera.scale;
        const offset = size / 2;

        // Glow behind cube
        const grd = ctx.createRadialGradient(cx, cy, 0, cx, cy, 100);
        grd.addColorStop(0, 'rgba(124, 92, 252, 0.1)');
        grd.addColorStop(1, 'transparent');
        ctx.fillStyle = grd;
        ctx.fillRect(0, 0, w, h);

        // Calculate global alpha for fade effects
        let globalAlpha = 1;
        if (currentPhase === 'IDEA') {
            // Fade in
            const elapsed = Date.now() - phaseStartTime;
            globalAlpha = Math.min(1, elapsed / 1000);
        } else if (currentPhase === 'RESET' || currentPhase === 'CELEBRATE') {
            // During celebrate/reset, check if close to end
            const elapsed = Date.now() - phaseStartTime;
            const duration = PHASES[currentPhase].duration || 1;
            if (currentPhase === 'RESET' || (currentPhase === 'CELEBRATE' && elapsed > 2000)) {
                globalAlpha = Math.max(0, 1 - (elapsed - 2000) / 1000);
            }
        }

        if (currentPhase === 'IDEA' || currentPhase === 'SCAFFOLD') {
            // Translucent planning cube - shows structure before agents fill it
            drawPlanningCube(cx, cy, size, scale, offset, globalAlpha);
        } else {
            // Draw filled blocks with WSP importance colors during BUILD
            drawFilledCube(cx, cy, size, scale, offset, globalAlpha);
        }
    }

    function drawPlanningCube(cx, cy, size, scale, offset, globalAlpha) {
        // Draw translucent 4x4x4 ghost structure during IDEA/SCAFFOLD
        const baseAlpha = currentPhase === 'IDEA' ? 0.15 : 0.25;

        // Draw wireframe outline first
        const wireAlpha = currentPhase === 'IDEA' ? 0.2 : 0.4;
        drawWireframeCube(cx, cy, size, scale, wireAlpha * globalAlpha);

        // Draw translucent blocks colored by WSP importance
        for (let z = 0; z < size; z++) {
            for (let y = size - 1; y >= 0; y--) {
                for (let x = 0; x < size; x++) {
                    const color = getWSPImportanceColor(x, y, z, size);
                    drawCubelet(
                        x - offset, y - offset, z,
                        cx, cy, scale,
                        color,
                        baseAlpha * globalAlpha
                    );
                }
            }
        }
    }

    function drawFilledCube(cx, cy, size, scale, offset, globalAlpha) {
        for (let z = 0; z < size; z++) {
            for (let y = size - 1; y >= 0; y--) {
                for (let x = 0; x < size; x++) {
                    const key = `${x},${y},${z}`;
                    if (filledBlocks.has(key)) {
                        // Filled blocks use WSP importance colors
                        const color = getWSPImportanceColor(x, y, z, size);
                        drawCubelet(
                            x - offset, y - offset, z,
                            cx, cy, scale,
                            color,
                            globalAlpha
                        );
                    } else if (currentPhase !== 'IDEA' && currentPhase !== 'SCAFFOLD') {
                        // Ghost block - WSP color at low alpha
                        const color = getWSPImportanceColor(x, y, z, size);
                        drawCubelet(
                            x - offset, y - offset, z,
                            cx, cy, scale,
                            color,
                            0.1 * globalAlpha
                        );
                    }
                }
            }
        }
    }

    function drawStatusBar() {
        const cx = w / 2;
        const statusY = h - 20;

        ctx.font = STYLE.fonts.status;
        ctx.fillStyle = 'rgba(255,255,255,0.5)';
        ctx.textAlign = 'center';

        const blocksFilled = filledBlocks.size;
        const totalBlocks = Math.pow(CONFIG.targetSize, 3);
        const pct = Math.round((blocksFilled / totalBlocks) * 100);

        let statusText = `FoundUP Cube: ${CONFIG.targetSize}×${CONFIG.targetSize}×${CONFIG.targetSize}`;
        statusText += `  |  Agents: ${agents.length}`;
        statusText += `  |  F_i: ${fiEarned.toLocaleString()}`;
        statusText += `  |  ${currentPhase}`;

        if (currentPhase === 'BUILDING') {
            statusText += ` (${pct}%)`;
        }

        ctx.fillText(statusText, cx, statusY);

        // Phase announcement for LAUNCH/CELEBRATE
        if (currentPhase === 'LAUNCH' || currentPhase === 'CELEBRATE') {
            const elapsed = Date.now() - phaseStartTime;
            const pulse = 0.8 + Math.sin(elapsed / 100) * 0.2;
            ctx.font = STYLE.fonts.announcement;
            ctx.fillStyle = `rgba(255, 215, 0, ${pulse})`;
            ctx.fillText('FoundUP$ MVP is LIVE!', cx, h * 0.15);
        }

        // Phase announcement for CUSTOMERS
        if (currentPhase === 'CUSTOMERS') {
            const elapsed = Date.now() - phaseStartTime;
            const pulse = 0.7 + Math.sin(elapsed / 150) * 0.3;
            ctx.font = STYLE.fonts.announcement;
            ctx.fillStyle = `rgba(0, 229, 208, ${pulse})`;
            ctx.fillText('First paying customers!', cx, h * 0.15);
        }

        // Ecosystem view status (zoomed out)
        if (cameraHandoff.zoomedOut) {
            ctx.font = STYLE.fonts.announcement;
            ctx.fillStyle = 'rgba(124, 92, 252, 0.8)';
            ctx.fillText(`Ecosystem: ${cameraHandoff.cubeCount} FoundUPs`, cx, h * 0.12);
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MULTI-CUBE ZOOM-OUT (Phase 3)
    // Draw mini cubes with agent pixel swarms when zoomed out
    // ═══════════════════════════════════════════════════════════════════════
    function drawMiniCubes() {
        const miniScale = 6;  // Small cubes
        const spacing = 120;  // Space between cubes
        const startX = w / 2 - (cameraHandoff.cubePositions.length - 1) * spacing / 2;
        const startY = h * 0.4;

        cameraHandoff.cubePositions.forEach((cube, i) => {
            const cubeX = startX + i * spacing;
            const cubeY = startY;

            // Draw mini cube (simplified - just faces)
            drawMiniCube(cubeX, cubeY, miniScale, i);

            // Draw agent swarm around cube (pixels colored by role)
            drawAgentSwarm(cubeX, cubeY, i);

            // Label
            ctx.font = '10px monospace';
            ctx.fillStyle = 'rgba(255,255,255,0.6)';
            ctx.textAlign = 'center';
            ctx.fillText(`#${cube.loopCount}`, cubeX, cubeY + 60);
        });
    }

    function drawMiniCube(cx, cy, scale, cubeIndex) {
        // Draw a simplified cube representation
        const size = 2;  // 2x2x2 mini representation
        const offset = size / 2;
        const colors = [
            STYLE.levelColors.P0,
            STYLE.levelColors.P1,
            STYLE.levelColors.P2,
            STYLE.levelColors.P3,
        ];

        // Just draw top visible blocks
        for (let x = 0; x < size; x++) {
            for (let y = 0; y < size; y++) {
                const colorIdx = (x + y + cubeIndex) % colors.length;
                const p = isoProject(x - offset, y - offset, size, cx, cy, scale);

                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(p.x + scale * 0.866, p.y - scale * 0.5);
                ctx.lineTo(p.x, p.y - scale);
                ctx.lineTo(p.x - scale * 0.866, p.y - scale * 0.5);
                ctx.closePath();

                ctx.fillStyle = colors[colorIdx];
                ctx.globalAlpha = 0.8;
                ctx.fill();
                ctx.strokeStyle = 'rgba(255,255,255,0.3)';
                ctx.lineWidth = 0.5;
                ctx.stroke();
                ctx.globalAlpha = 1;
            }
        }
    }

    function drawAgentSwarm(cx, cy, cubeIndex) {
        // Draw pixel swarm representing agents around mini cube
        // Colors represent roles (WSP 54)
        const swarmSize = 8 + cubeIndex * 3;  // More agents for older cubes
        const elapsed = Date.now() / 1000;

        for (let i = 0; i < swarmSize; i++) {
            // Orbital motion around cube
            const angle = (i / swarmSize) * Math.PI * 2 + elapsed * 0.5 + cubeIndex;
            const radius = 25 + Math.sin(elapsed * 2 + i) * 8;
            const px = cx + Math.cos(angle) * radius;
            const py = cy + Math.sin(angle) * radius * 0.5 - 20;

            // Role-based color (cycle through agent types)
            const roles = ['worker', 'promoter', 'investor', 'founder'];
            const role = roles[i % roles.length];
            const color = STYLE.agentColors[role];

            // Draw pixel dot
            ctx.beginPath();
            ctx.arc(px, py, 2, 0, Math.PI * 2);
            ctx.fillStyle = color;
            ctx.fill();

            // Subtle glow
            ctx.shadowColor = color;
            ctx.shadowBlur = 4;
            ctx.fill();
            ctx.shadowBlur = 0;
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // ANIMATION LOOP
    // ═══════════════════════════════════════════════════════════════════════
    function animate() {
        ctx.clearRect(0, 0, w, h);
        time += 0.016;

        updatePhase();
        updateAgents();
        updateAgentBehaviors();
        updateParticles();
        updateConfetti();
        updateTicker();
        updateCamera();

        // Spawn agents during building
        if (currentPhase === 'BUILDING' && Math.random() < CONFIG.agentSpawnRate && agents.length < CONFIG.maxAgents) {
            const statuses = ['building...', 'coding...', 'testing...', 'designing...'];
            spawnAgent('worker', statuses[Math.floor(Math.random() * statuses.length)]);
        }

        drawCube();
        drawParticles();
        drawAgents();
        drawConfetti();
        drawTicker();
        drawStatusBar();

        // Draw mini-cubes in zoomed-out mode (Phase 3)
        if (cameraHandoff.zoomedOut && cameraHandoff.cubePositions.length > 0) {
            drawMiniCubes();
        }

        requestAnimationFrame(animate);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // PUBLIC API
    // ═══════════════════════════════════════════════════════════════════════
    function init(canvasId, options = {}) {
        canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`FoundupCube: Canvas #${canvasId} not found`);
            return null;
        }

        // Apply options
        if (options.useSimEvents !== undefined) FLAGS.USE_SIM_EVENTS = options.useSimEvents;
        if (options.debugTiming !== undefined) FLAGS.DEBUG_TIMING = options.debugTiming;
        if (options.multiCube !== undefined) FLAGS.MULTI_CUBE = options.multiCube;

        ctx = canvas.getContext('2d');

        function resize() {
            const rect = canvas.getBoundingClientRect();
            const dpr = window.devicePixelRatio || 1;
            w = rect.width;
            h = rect.height;
            canvas.width = w * dpr;
            canvas.height = h * dpr;
            ctx.scale(dpr, dpr);
        }

        window.addEventListener('resize', resize);
        resize();

        // Start
        loopStartTime = Date.now();
        phaseStartTime = Date.now();
        onPhaseChange('IDEA');

        // Connect simulator bridge if enabled
        if (FLAGS.USE_SIM_EVENTS) {
            connectSimulatorBridge();
        }

        animate();
        console.log('FoundupCube initialized (45s loop, Phase 1)');

        return {
            subscribe: (fn) => { eventSubscribers.push(fn); },
            unsubscribe: (fn) => {
                const idx = eventSubscribers.indexOf(fn);
                if (idx !== -1) eventSubscribers.splice(idx, 1);
            },
            getState: () => ({
                phase: currentPhase,
                loopCount,
                agents: agents.length,
                blocks: filledBlocks.size,
                fiEarned,
            }),
        };
    }

    return { init, STYLE, FLAGS };
})();

// Auto-init if buildCanvas exists
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        const canvas = document.getElementById('buildCanvas');
        if (canvas && !canvas.dataset.foundupInit) {
            canvas.dataset.foundupInit = 'true';
            FoundupCube.init('buildCanvas');
        }
    });
}
