# Ecosystem Animation Tests

## Test Strategy

This is a visual animation module. Testing is primarily manual/visual.

## Manual Test Checklist

### Layer 1: Core
- [ ] Canvas renders without errors
- [ ] Glowing orb visible at center
- [ ] Orb has gradient effect

### Layer 2: Timeline
- [ ] Slider moves from Y0 to Y10
- [ ] Year display updates
- [ ] Orb size changes with year

### Layer 3: Particles
- [ ] Particles visible around core
- [ ] Particle count increases with year
- [ ] Particles orbit smoothly

### Layer 4: Flow
- [ ] Flow particles spawn from edges
- [ ] Particles move toward core
- [ ] Absorption effect on contact

### Layer 5: Milestones
- [ ] GENESIS burst at Y0
- [ ] SELF_SUSTAINING burst (scenario-dependent)
- [ ] 10X_RATIO burst
- [ ] 100X_RATIO burst
- [ ] 1M_FOUNDUPS burst

### Layer 6: Scenarios
- [ ] Conservative button selects scenario
- [ ] Baseline button selects scenario
- [ ] OpenClaw button selects scenario
- [ ] Visual differs between scenarios
- [ ] Auto-play animates Y0→Y10

## Run Local Test

```bash
cd public
python -m http.server 5000
# Open: http://localhost:5000/ecosystem.html
```

## Browser Compatibility

- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge
