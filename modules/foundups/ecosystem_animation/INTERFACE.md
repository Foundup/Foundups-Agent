# Ecosystem Animation Interface

**Version**: 1.0.0
**Module**: `ecosystem_animation`

## JavaScript API

### EcosystemGrowth

Main animation module (IIFE pattern, like foundup-cube.js).

#### Methods

```javascript
// Initialize animation on canvas element
EcosystemGrowth.init(canvasId: string): Promise<void>

// Set current year (0-10, supports decimals)
EcosystemGrowth.setYear(year: number): void

// Set growth scenario
EcosystemGrowth.setScenario(name: 'conservative' | 'baseline' | 'openclaw'): void

// Toggle auto-play animation
EcosystemGrowth.toggleAutoPlay(): void
```

## Data Schema

### ten_year_projection.json

```typescript
interface ProjectionData {
  generated_at: string;
  btc_price_assumption: number;
  genesis_staker_config: {
    count: number;
    avg_stake_btc: number;
    du_pool_pct: number;
  };
  scenarios: {
    [key: string]: Scenario;
  };
}

interface Scenario {
  scenario: string;
  description: string;
  bootstrap_btc: number;
  genesis_stakers: number;
  genesis_stake_total_btc: number;
  years: YearData[];
}

interface YearData {
  year: number;
  foundups: number;
  daily_volume_usd: number;
  daily_revenue_usd: number;
  monthly_revenue_btc: number;
  annual_revenue_btc: number;
  cumulative_btc_reserve: number;
  operational_cost_btc: number;
  net_revenue_btc: number;
  is_self_sustaining: boolean;
  genesis_staker_ratio: number;
  f_i_price_multiple: number;
  milestones: string[];
}
```

## Visual Constants

```javascript
const STYLE = {
  core: {
    baseRadius: 25,      // Y0 size
    maxRadius: 120,      // Y10 size
    healthColors: {
      struggling: '#ff4444',
      growing: '#ffa500',
      thriving: '#22c55e',
    },
  },
  particles: {
    minCount: 15,        // Y0
    maxCount: 400,       // Y10
  },
  milestones: {
    GENESIS: { color: '#7c5cfc', burstCount: 30 },
    SELF_SUSTAINING: { color: '#22c55e', burstCount: 50 },
    '10X_RATIO': { color: '#ffd700', burstCount: 40 },
    '100X_RATIO': { color: '#ff8c00', burstCount: 60 },
    '1M_FOUNDUPS': { color: '#ff4ea0', burstCount: 80 },
  },
};
```

## HTML Structure

```html
<div class="canvas-container">
  <canvas id="ecosystemCanvas"></canvas>
</div>

<div class="controls">
  <input type="range" id="timelineSlider" min="0" max="10" step="0.1">
  <button class="scenario-btn" data-scenario="baseline">Baseline</button>
  <button id="autoPlayBtn">Play</button>
</div>
```

## Events (DOM)

| Event | Element | Description |
|-------|---------|-------------|
| `input` | `#timelineSlider` | Year changed |
| `click` | `.scenario-btn` | Scenario selected |
| `click` | `#autoPlayBtn` | Toggle auto-play |

## Browser Support

- Modern browsers with Canvas 2D support
- Requires ES6+ (const, arrow functions)
- No external dependencies
