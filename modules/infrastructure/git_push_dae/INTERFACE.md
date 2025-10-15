# GitPushDAE Interface Documentation

## Public API

### GitPushDAE Class

```python
class GitPushDAE:
    """WSP 91 compliant DAEMON for autonomous git push decisions."""

    def __init__(self, domain: str, check_interval: int = 300):
        """
        Initialize GitPushDAE daemon.

        Args:
            domain: Monitoring domain (e.g., 'foundups_development')
            check_interval: Seconds between monitoring cycles (default: 300)
        """

    def start(self) -> None:
        """Start the autonomous monitoring daemon with WSP 91 logging."""

    def stop(self) -> None:
        """Stop the daemon with full lifecycle logging."""

    def health_check(self) -> HealthStatus:
        """WSP 91 compliant health check."""

    def make_push_decision(self, context: PushContext) -> PushDecision:
        """Make autonomous push decision with full observability."""

    def monitoring_cycle(self) -> None:
        """Main monitoring logic - checks for push-worthy changes."""
```

### Data Structures

```python
@dataclass
class PushContext:
    """Context for autonomous push decision."""
    uncommitted_changes: List[str]
    quality_score: float
    time_since_last_push: int
    social_value_score: float
    repository_health: str

@dataclass
class PushDecision:
    """Autonomous push decision result."""
    should_push: bool
    confidence: float
    reasoning: str
    expected_impact: str
    cost_estimate: float
    alternatives_considered: List[Dict]

@dataclass
class HealthStatus:
    """WSP 91 health status."""
    daemon_name: str
    status: str  # 'healthy', 'degraded', 'critical', 'failed'
    vital_signs: Dict
    anomalies: List[str]
    recommendations: List[str]
```

## Agentic Parameters

### Push Decision Criteria (Autonomous)

1. **Code Quality Threshold**: `quality_score >= 0.5`
   - Development quality is iterative - not perfect upfront
   - Encourages frequent progress sharing over perfection

2. **Change Significance**: `len(uncommitted_changes) >= 3`
   - Minimum 3 changed files to warrant push

3. **Time Windows**: Respect deep sleep hours only
   - No pushes between 02:00-06:00 local time
   - Evening coding (22:00-02:00) is prime development time

4. **Frequency Control**: `time_since_last_push >= 1800` (30 minutes)
   - Prevent spam pushes

5. **Social Value**: `social_value_score >= 0.6`
   - Content valuable for LinkedIn/X audience

6. **Repository Health**: Accept "dirty" state during development
   - BLOCKED: "conflicts" (must resolve)
   - ACCEPTABLE: "dirty" (active development)
   - ACCEPTABLE: "clean" (no uncommitted changes)

7. **Cost Efficiency**: Push value vs analysis cost

### Error Handling

- **Retry Logic**: Failed pushes retried with exponential backoff
- **Circuit Breaker**: Stop posting if social media APIs fail repeatedly
- **Fallback Mode**: Continue monitoring even if social posting fails

## Parameter Specifications

### Constructor Parameters

- **domain**: `str` - Monitoring domain identifier
- **check_interval**: `int` - Monitoring cycle interval in seconds (default: 300)

### Return Value Documentation

- **PushDecision.should_push**: `bool` - Whether to execute git push
- **PushDecision.confidence**: `float` 0.0-1.0 - Decision confidence level
- **PushDecision.cost_estimate**: `float` - Estimated token cost in USD

### Error Handling

- **GitPushDAEError**: Base exception for daemon errors
- **QualityAssessmentError**: Quality check failures
- **SocialMediaError**: Posting failures (non-blocking)

## Examples

### Basic Usage
```python
from modules.infrastructure.git_push_dae.src.git_push_dae import GitPushDAE

# Launch autonomous daemon
dae = GitPushDAE(domain="foundups_development")
dae.start()

# Daemon runs indefinitely with full WSP 91 observability
```

### Custom Configuration
```python
# Custom monitoring interval
dae = GitPushDAE(
    domain="foundups_development",
    check_interval=600  # 10-minute checks
)
```
