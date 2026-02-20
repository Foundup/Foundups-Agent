/**
 * Ecosystem Growth Animation
 *
 * 10-Year Visual Litepaper for pAVS
 * Shows ecosystem growth WITHOUT numbers - visual speaks for itself
 *
 * Visual Language:
 *   - Central orb size = BTC Reserve (larger = more)
 *   - Particle density = FoundUp count (more particles = more activity)
 *   - Color gradient = Health (green = thriving, yellow = growing)
 *   - Flow streams = Revenue (particles flowing into core)
 *   - Burst effects = Milestones (fireworks at key events)
 *
 * Layers (Occam's approach):
 *   Layer 1: Static Core (glowing orb)
 *   Layer 2: Timeline Slider (drives state)
 *   Layer 3: Particle System (FoundUps)
 *   Layer 4: Revenue Flows (fee particles)
 *   Layer 5: Milestone Bursts (celebration effects)
 *   Layer 6: Polish (scenarios, auto-play)
 */

const EcosystemGrowth = (function () {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // FROZEN STYLE CONSTANTS (Visual consistency)
    // ═══════════════════════════════════════════════════════════════════════
    const STYLE = Object.freeze({
        bg: '#08080f',

        // Core (BTC Reserve)
        core: {
            baseRadius: 25,        // Y0 radius
            maxRadius: 120,        // Y10 radius
            baseGlow: '#7c5cfc',
            healthColors: {
                struggling: '#ff4444',
                growing: '#ffa500',
                thriving: '#22c55e',
            },
        },

        // Particles (FoundUps)
        particles: {
            minCount: 15,          // Y0
            maxCount: 400,         // Y10
            baseSpeed: 0.3,
            colors: ['#ff2d2d', '#ff8c00', '#ffd700', '#00b341', '#0066ff', '#9b59b6'],
        },

        // Flow (Revenue)
        flow: {
            streamCount: 6,        // Number of inflow streams
            particleSpeed: 1.5,
            spawnRate: 0.03,       // Per frame probability
            color: '#00e5d0',
        },

        // Milestones
        milestones: {
            GENESIS: { color: '#7c5cfc', burstCount: 30 },
            SELF_SUSTAINING: { color: '#22c55e', burstCount: 50 },
            '10X_RATIO': { color: '#ffd700', burstCount: 40 },
            '100X_RATIO': { color: '#ff8c00', burstCount: 60 },
            '1M_FOUNDUPS': { color: '#ff4ea0', burstCount: 80 },
        },
    });

    // ═══════════════════════════════════════════════════════════════════════
    // STATE
    // ═══════════════════════════════════════════════════════════════════════
    let canvas, ctx, w, h;
    let animationFrameId = null;
    let projectionData = null;
    let currentScenario = 'baseline_conservative';
    let currentYear = 0;
    let isAutoPlaying = false;
    let autoPlaySpeed = 0.02;  // Years per frame (~5 seconds per year at 60fps)

    // Visual state
    const core = {
        x: 0,
        y: 0,
        radius: STYLE.core.baseRadius,
        targetRadius: STYLE.core.baseRadius,
        health: 0.5,         // 0 = red, 0.5 = yellow, 1 = green
        pulsePhase: 0,
    };

    const particles = [];    // FoundUp particles
    const flowParticles = []; // Revenue flow particles
    const burstParticles = []; // Milestone burst particles
    const triggeredMilestones = new Set();  // Track which milestones triggered

    // ═══════════════════════════════════════════════════════════════════════
    // INITIALIZATION
    // ═══════════════════════════════════════════════════════════════════════
    async function init(canvasId) {
        canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error('[Ecosystem] Canvas not found:', canvasId);
            return;
        }

        ctx = canvas.getContext('2d');

        // Load projection data
        try {
            const response = await fetch('data/ten_year_projection.json');
            projectionData = await response.json();
            console.log('[Ecosystem] Loaded projection data:', Object.keys(projectionData.scenarios).length, 'scenarios');
        } catch (e) {
            console.error('[Ecosystem] Failed to load projection data:', e);
            // Use fallback data
            projectionData = createFallbackData();
        }

        // Setup resize
        resize();
        window.addEventListener('resize', resize);

        // Setup controls
        setupControls();

        // Start render loop
        render();

        console.log('[Ecosystem] Initialized');
    }

    function resize() {
        const container = canvas.parentElement;
        const dpr = window.devicePixelRatio || 1;
        w = container.clientWidth;
        h = container.clientHeight;
        canvas.width = w * dpr;
        canvas.height = h * dpr;
        canvas.style.width = w + 'px';
        canvas.style.height = h + 'px';
        ctx.scale(dpr, dpr);

        // Center core
        core.x = w / 2;
        core.y = h / 2;
    }

    function createFallbackData() {
        // Minimal fallback if JSON fails to load
        return {
            scenarios: {
                'baseline_conservative': {
                    years: Array.from({ length: 11 }, (_, i) => ({
                        year: i,
                        foundups: 100 + i * i * 200,
                        cumulative_btc_reserve: 50 + i * i * 100,
                        is_self_sustaining: i >= 1,
                        milestones: i === 0 ? ['GENESIS'] : [],
                    })),
                },
            },
        };
    }

    // ═══════════════════════════════════════════════════════════════════════
    // CONTROLS
    // ═══════════════════════════════════════════════════════════════════════
    function setupControls() {
        // Timeline slider
        const slider = document.getElementById('timelineSlider');
        const yearDisplay = document.getElementById('yearDisplay');
        if (slider) {
            slider.addEventListener('input', (e) => {
                setYear(parseFloat(e.target.value));
                yearDisplay.textContent = Math.floor(currentYear);
            });
        }

        // Scenario buttons
        const scenarioButtons = document.querySelectorAll('.scenario-btn');
        scenarioButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                scenarioButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                setScenario(btn.dataset.scenario);
            });
        });

        // Auto-play button
        const autoPlayBtn = document.getElementById('autoPlayBtn');
        if (autoPlayBtn) {
            autoPlayBtn.addEventListener('click', toggleAutoPlay);
        }
    }

    function toggleAutoPlay() {
        isAutoPlaying = !isAutoPlaying;
        const btn = document.getElementById('autoPlayBtn');
        if (btn) {
            btn.textContent = isAutoPlaying ? 'Pause' : 'Play';
        }
        if (isAutoPlaying && currentYear >= 10) {
            // Reset to start
            setYear(0);
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // DATA ACCESS
    // ═══════════════════════════════════════════════════════════════════════
    function setScenario(name) {
        // Map friendly names to data keys
        const keyMap = {
            'conservative': 'conservative_conservative',
            'baseline': 'baseline_conservative',
            'openclaw': 'openclaw_comfortable',
        };
        currentScenario = keyMap[name] || name;

        // Reset milestones
        triggeredMilestones.clear();

        // Re-apply current year to update visuals
        setYear(currentYear);
    }

    function setYear(year) {
        currentYear = Math.max(0, Math.min(10, year));

        // Update slider display
        const slider = document.getElementById('timelineSlider');
        const yearDisplay = document.getElementById('yearDisplay');
        if (slider) slider.value = currentYear;
        if (yearDisplay) yearDisplay.textContent = Math.floor(currentYear);

        // Get interpolated data
        const data = getYearData(currentYear);
        if (!data) return;

        // Update core size based on BTC reserve (normalized)
        const maxReserve = getMaxReserve();
        const reserveRatio = Math.min(1, data.cumulative_btc_reserve / maxReserve);
        core.targetRadius = STYLE.core.baseRadius + reserveRatio * (STYLE.core.maxRadius - STYLE.core.baseRadius);

        // Update health based on sustainability
        core.health = data.is_self_sustaining ? 0.8 + Math.random() * 0.2 : 0.3 + Math.random() * 0.2;

        // Update particle count based on FoundUps
        updateParticleCount(data.foundups);

        // Check milestones
        checkMilestones(data);
    }

    function getYearData(year) {
        if (!projectionData) return null;

        const scenario = projectionData.scenarios[currentScenario];
        if (!scenario) return null;

        const floorYear = Math.floor(year);
        const ceilYear = Math.ceil(year);
        const t = year - floorYear;

        const floorData = scenario.years[floorYear];
        const ceilData = scenario.years[Math.min(ceilYear, 10)];

        if (!floorData) return null;
        if (floorYear === ceilYear || !ceilData) return floorData;

        // Interpolate
        return {
            year: year,
            foundups: lerp(floorData.foundups, ceilData.foundups, t),
            cumulative_btc_reserve: lerp(floorData.cumulative_btc_reserve, ceilData.cumulative_btc_reserve, t),
            is_self_sustaining: t < 0.5 ? floorData.is_self_sustaining : ceilData.is_self_sustaining,
            milestones: floorData.milestones,
            daily_revenue_usd: lerp(floorData.daily_revenue_usd || 0, ceilData.daily_revenue_usd || 0, t),
        };
    }

    function getMaxReserve() {
        if (!projectionData) return 1000;
        const scenario = projectionData.scenarios[currentScenario];
        if (!scenario) return 1000;
        return scenario.years[10]?.cumulative_btc_reserve || 1000;
    }

    function lerp(a, b, t) {
        return a + (b - a) * t;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // LAYER 3: PARTICLE SYSTEM (FoundUps)
    // ═══════════════════════════════════════════════════════════════════════
    function updateParticleCount(foundups) {
        // Map foundups to particle count (logarithmic scale)
        const maxFoundups = getMaxFoundups();
        const ratio = Math.log(1 + foundups) / Math.log(1 + maxFoundups);
        const targetCount = Math.floor(STYLE.particles.minCount + ratio * (STYLE.particles.maxCount - STYLE.particles.minCount));

        // Add or remove particles to match target
        while (particles.length < targetCount) {
            particles.push(createParticle());
        }
        while (particles.length > targetCount) {
            particles.pop();
        }
    }

    function getMaxFoundups() {
        if (!projectionData) return 1000000;
        const scenario = projectionData.scenarios[currentScenario];
        if (!scenario) return 1000000;
        return scenario.years[10]?.foundups || 1000000;
    }

    function createParticle() {
        const angle = Math.random() * Math.PI * 2;
        const distance = 60 + Math.random() * 150;  // Orbit distance from core
        return {
            angle: angle,
            distance: distance,
            speed: (0.3 + Math.random() * 0.7) * STYLE.particles.baseSpeed,
            size: 1.5 + Math.random() * 2,
            color: STYLE.particles.colors[Math.floor(Math.random() * STYLE.particles.colors.length)],
            offsetX: (Math.random() - 0.5) * 20,
            offsetY: (Math.random() - 0.5) * 20,
        };
    }

    function updateParticles() {
        particles.forEach(p => {
            // Orbital motion
            p.angle += p.speed * 0.02;

            // Slight wobble
            p.offsetX += (Math.random() - 0.5) * 0.5;
            p.offsetY += (Math.random() - 0.5) * 0.5;
            p.offsetX *= 0.98;
            p.offsetY *= 0.98;
        });
    }

    function drawParticles() {
        particles.forEach(p => {
            const x = core.x + Math.cos(p.angle) * (core.radius + p.distance) + p.offsetX;
            const y = core.y + Math.sin(p.angle) * (core.radius + p.distance) * 0.6 + p.offsetY; // Flatten for 3D effect

            ctx.beginPath();
            ctx.arc(x, y, p.size, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.globalAlpha = 0.7;
            ctx.fill();

            // Glow
            ctx.shadowColor = p.color;
            ctx.shadowBlur = 4;
            ctx.fill();
            ctx.shadowBlur = 0;
        });
        ctx.globalAlpha = 1;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // LAYER 4: REVENUE FLOW
    // ═══════════════════════════════════════════════════════════════════════
    function updateFlowParticles() {
        const data = getYearData(currentYear);
        if (!data) return;

        // Spawn rate scales with revenue
        const revenueRatio = Math.min(1, (data.daily_revenue_usd || 0) / 1000000000);
        const spawnChance = STYLE.flow.spawnRate * (0.2 + revenueRatio * 0.8);

        // Spawn new flow particles
        if (Math.random() < spawnChance) {
            const streamAngle = Math.floor(Math.random() * STYLE.flow.streamCount) * (Math.PI * 2 / STYLE.flow.streamCount);
            const edge = Math.max(w, h) * 0.6;
            flowParticles.push({
                x: core.x + Math.cos(streamAngle) * edge,
                y: core.y + Math.sin(streamAngle) * edge,
                targetX: core.x,
                targetY: core.y,
                speed: STYLE.flow.particleSpeed * (0.8 + Math.random() * 0.4),
                size: 2 + Math.random() * 2,
                life: 1,
            });
        }

        // Update existing flow particles
        for (let i = flowParticles.length - 1; i >= 0; i--) {
            const p = flowParticles[i];

            // Move toward core
            const dx = p.targetX - p.x;
            const dy = p.targetY - p.y;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist < core.radius) {
                // Absorbed by core - pulse effect
                core.pulsePhase = Math.PI;
                flowParticles.splice(i, 1);
            } else {
                p.x += (dx / dist) * p.speed;
                p.y += (dy / dist) * p.speed;
            }
        }
    }

    function drawFlowParticles() {
        flowParticles.forEach(p => {
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fillStyle = STYLE.flow.color;
            ctx.globalAlpha = 0.8;
            ctx.fill();

            // Trail
            const dx = core.x - p.x;
            const dy = core.y - p.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            const trailX = p.x - (dx / dist) * 10;
            const trailY = p.y - (dy / dist) * 10;

            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(trailX, trailY);
            ctx.strokeStyle = STYLE.flow.color;
            ctx.globalAlpha = 0.3;
            ctx.lineWidth = p.size * 0.5;
            ctx.stroke();
        });
        ctx.globalAlpha = 1;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // LAYER 5: MILESTONES
    // ═══════════════════════════════════════════════════════════════════════
    function checkMilestones(data) {
        if (!data.milestones) return;

        data.milestones.forEach(milestone => {
            if (!triggeredMilestones.has(milestone) && STYLE.milestones[milestone]) {
                triggerMilestone(milestone);
                triggeredMilestones.add(milestone);
            }
        });
    }

    function triggerMilestone(type) {
        const config = STYLE.milestones[type];
        if (!config) return;

        // Create burst particles
        for (let i = 0; i < config.burstCount; i++) {
            const angle = (i / config.burstCount) * Math.PI * 2;
            const speed = 3 + Math.random() * 4;
            burstParticles.push({
                x: core.x,
                y: core.y,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed,
                size: 3 + Math.random() * 3,
                color: config.color,
                life: 1,
            });
        }
    }

    function updateBurstParticles() {
        for (let i = burstParticles.length - 1; i >= 0; i--) {
            const p = burstParticles[i];
            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.05;  // Gravity
            p.life -= 0.015;

            if (p.life <= 0) {
                burstParticles.splice(i, 1);
            }
        }
    }

    function drawBurstParticles() {
        burstParticles.forEach(p => {
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size * p.life, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.globalAlpha = p.life;
            ctx.fill();

            ctx.shadowColor = p.color;
            ctx.shadowBlur = 8;
            ctx.fill();
            ctx.shadowBlur = 0;
        });
        ctx.globalAlpha = 1;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // LAYER 1: CORE (BTC Reserve)
    // ═══════════════════════════════════════════════════════════════════════
    function drawCore() {
        // Smooth radius transition
        core.radius += (core.targetRadius - core.radius) * 0.05;

        // Pulse effect
        core.pulsePhase *= 0.95;
        const pulse = 1 + Math.sin(core.pulsePhase) * 0.05;
        const displayRadius = core.radius * pulse;

        // Health color
        let coreColor;
        if (core.health < 0.4) {
            coreColor = STYLE.core.healthColors.struggling;
        } else if (core.health < 0.7) {
            coreColor = STYLE.core.healthColors.growing;
        } else {
            coreColor = STYLE.core.healthColors.thriving;
        }

        // Outer glow
        const gradient = ctx.createRadialGradient(
            core.x, core.y, displayRadius * 0.3,
            core.x, core.y, displayRadius * 1.5
        );
        gradient.addColorStop(0, coreColor);
        gradient.addColorStop(0.5, STYLE.core.baseGlow + '80');
        gradient.addColorStop(1, 'transparent');

        ctx.beginPath();
        ctx.arc(core.x, core.y, displayRadius * 1.5, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();

        // Inner core
        ctx.beginPath();
        ctx.arc(core.x, core.y, displayRadius, 0, Math.PI * 2);

        const innerGradient = ctx.createRadialGradient(
            core.x - displayRadius * 0.2, core.y - displayRadius * 0.2, 0,
            core.x, core.y, displayRadius
        );
        innerGradient.addColorStop(0, '#ffffff');
        innerGradient.addColorStop(0.2, coreColor);
        innerGradient.addColorStop(1, shadeColor(coreColor, -30));

        ctx.fillStyle = innerGradient;
        ctx.fill();

        // Highlight
        ctx.beginPath();
        ctx.arc(core.x - displayRadius * 0.25, core.y - displayRadius * 0.25, displayRadius * 0.2, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
        ctx.fill();
    }

    function shadeColor(color, percent) {
        const num = parseInt(color.replace('#', ''), 16);
        const amt = Math.round(2.55 * percent);
        const R = Math.max(0, Math.min(255, (num >> 16) + amt));
        const G = Math.max(0, Math.min(255, ((num >> 8) & 0x00ff) + amt));
        const B = Math.max(0, Math.min(255, (num & 0x0000ff) + amt));
        return '#' + (0x1000000 + R * 0x10000 + G * 0x100 + B).toString(16).slice(1);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // RENDER LOOP
    // ═══════════════════════════════════════════════════════════════════════
    function render() {
        // Clear
        ctx.fillStyle = STYLE.bg;
        ctx.fillRect(0, 0, w, h);

        // Auto-play
        if (isAutoPlaying) {
            currentYear += autoPlaySpeed;
            if (currentYear >= 10) {
                currentYear = 10;
                isAutoPlaying = false;
                const btn = document.getElementById('autoPlayBtn');
                if (btn) btn.textContent = 'Play';
            }
            setYear(currentYear);
        }

        // Update
        updateParticles();
        updateFlowParticles();
        updateBurstParticles();

        // Draw (back to front)
        drawParticles();
        drawFlowParticles();
        drawCore();
        drawBurstParticles();

        // Continue loop
        animationFrameId = requestAnimationFrame(render);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // PUBLIC API
    // ═══════════════════════════════════════════════════════════════════════
    return {
        init,
        setYear,
        setScenario,
        toggleAutoPlay,
    };
})();
