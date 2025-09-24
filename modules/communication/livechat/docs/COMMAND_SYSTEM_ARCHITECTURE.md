# Command System Architecture - Better Organization Proposal

## Current Issues
1. Commands scattered across multiple files
2. No centralized registry
3. Typo handlers mixed with main logic
4. Throttling logic duplicated
5. Hard to discover all commands

## Proposed Architecture

### 1. Centralized Command Registry
```python
# command_registry.py
COMMAND_REGISTRY = {
    '/score': {
        'handler': 'command_handler.handle_score',
        'aliases': ['/stats'],
        'cost': 0,
        'throttle_weight': 1.0,
        'role': 'everyone',
        'help': 'Show XP, level, rank, frags'
    },
    '/pqn': {
        'handler': 'pqn_handler.handle_research',
        'aliases': ['/pnq', '/pqm'],  # Typos auto-handled
        'cost': 100,  # Grok tokens
        'throttle_weight': 2.0,
        'role': 'everyone',
        'help': 'Quantum consciousness research'
    }
    # ... all 37 patterns
}
```

### 2. Single Command Router
```python
# command_router.py
class CommandRouter:
    def __init__(self):
        self.registry = load_command_registry()
        self.throttle_manager = IntelligentThrottleManager()

    def route_command(self, text, user, role):
        # 1. Find command (handles aliases/typos automatically)
        cmd = self.find_command(text)
        if not cmd:
            return None

        # 2. Check role permissions
        if not self.check_role(cmd, role):
            return f"Command requires {cmd.required_role} role"

        # 3. Apply throttling
        if not self.throttle_manager.should_allow(cmd, user):
            return None  # Silently throttled

        # 4. Track API cost
        self.track_cost(cmd.cost)

        # 5. Execute handler
        return cmd.handler(text, user, role)
```

### 3. Unified Throttling
```python
# unified_throttle.py
class UnifiedThrottleManager:
    COST_TIERS = {
        'free': {'weight': 0.5, 'cooldown': 1},    # Local commands
        'low': {'weight': 1.0, 'cooldown': 5},     # Basic API
        'medium': {'weight': 1.5, 'cooldown': 10}, # Factcheck
        'high': {'weight': 2.0, 'cooldown': 30},   # PQN/Grok
        'critical': {'weight': 3.0, 'cooldown': 60} # Consciousness
    }

    def calculate_throttle(self, command, user):
        # Single place for ALL throttle logic
        base_cooldown = self.COST_TIERS[command.tier]['cooldown']
        user_multiplier = self.get_user_multiplier(user)
        quota_multiplier = self.get_quota_multiplier()
        return base_cooldown * user_multiplier * quota_multiplier
```

### 4. Auto-Discovery System
```python
# command_discovery.py
class CommandDiscoverySystem:
    def scan_codebase(self):
        """Scan for all command patterns"""
        patterns = []
        # Find all .startswith('/') patterns
        # Find all regex patterns for special commands
        # Find all emoji patterns
        return patterns

    def feed_to_holoindex(self, patterns):
        """Auto-feed discoveries to HoloIndex"""
        for pattern in patterns:
            self.discovery_feeder.record(pattern)

    def generate_docs(self):
        """Auto-generate COMMAND_REFERENCE.md"""
        # From registry, create complete documentation
```

### 5. Command Analytics
```python
# command_analytics.py
class CommandAnalytics:
    def track(self, command, user, success, cost):
        """Track every command for optimization"""
        self.db.insert({
            'command': command,
            'user': user,
            'success': success,
            'api_cost': cost,
            'timestamp': now(),
            'quota_remaining': self.get_quota()
        })

    def optimize_throttling(self):
        """Learn from usage patterns"""
        # Adjust throttle weights based on success/failure
        # Predict quota exhaustion
        # Suggest command deprecation/promotion
```

## Benefits of This Architecture

1. **Single Source of Truth**: All commands in one registry
2. **Easy Discovery**: One file to see all commands
3. **Auto-Documentation**: Generate docs from registry
4. **Unified Throttling**: One place for all throttle logic
5. **Better Testing**: Test commands in isolation
6. **Easy Extension**: Add new commands to registry
7. **Analytics Built-in**: Track usage and costs
8. **Typo Tolerance**: Automatic alias handling
9. **Role Management**: Centralized permissions
10. **Cost Tracking**: Know exactly what costs tokens

## Migration Plan

### Phase 1: Build Registry (1 day)
- Create command_registry.py with all 37 patterns
- Map to existing handlers

### Phase 2: Create Router (1 day)
- Build CommandRouter class
- Route to existing handlers
- Add to message_processor.py

### Phase 3: Unify Throttling (2 days)
- Merge all throttle logic
- Create tier system
- Test extensively

### Phase 4: Add Analytics (1 day)
- Track all commands
- Build optimization logic

### Phase 5: Auto-Discovery (1 day)
- Scan for new patterns
- Feed to HoloIndex
- Generate documentation

## Cost Analysis

### Current Costs (per hour typical usage)
- Polling: 720 calls × 5 units = 3,600 units
- Commands: ~50 calls × 0-200 units = 0-10,000 units
- Grok API: ~10 calls × 100 tokens = 1,000 tokens

### With Better Organization
- Smart polling: 360 calls × 5 units = 1,800 units (50% reduction)
- Command caching: ~30 calls × 0-200 units = 0-6,000 units
- Grok optimization: ~5 calls × 100 tokens = 500 tokens

**Potential Savings: 40-50% reduction in API costs**

## Conclusion

The current system works but is hard to maintain and extend. This architecture would:
- Make all commands easily discoverable
- Reduce API costs through better throttling
- Enable self-improvement through analytics
- Simplify adding new commands
- Provide better user experience

The effort (6 days) would pay for itself quickly through:
- Reduced debugging time
- Faster feature additions
- Lower API costs
- Better user satisfaction