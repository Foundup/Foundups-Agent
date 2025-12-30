# Human Interaction Module - Public API

Complete interface documentation for the Human Interaction Module.

## Public API

### Primary Function

```python
from modules.infrastructure.human_interaction import get_interaction_controller

def get_interaction_controller(driver, platform: str = "youtube_chat") -> InteractionController
```

**Args:**
- `driver`: Selenium WebDriver instance
- `platform`: Platform name (e.g., "youtube_chat", "linkedin", "twitter")

**Returns:** InteractionController instance

**Example:**
```python
interaction = get_interaction_controller(driver, platform="youtube_chat")
```

---

## InteractionController Class

### Methods

#### `async hover_action(action_name: str) -> bool`

Hover at action coordinates with Bezier curve movement (no click).

**Args:**
- `action_name`: Action name from platform profile (e.g., "party_toggle")

**Returns:** `True` if successful, `False` otherwise

**Example:**
```python
await interaction.hover_action("party_toggle")  # Opens reactions popup
```

---

#### `async click_action(action_name: str) -> bool`

Click action with full anti-detection sophistication.

**Automatically includes:**
- Thinking pause (30% chance)
- Bezier curve mouse movement
- Coordinate variance (±8px)
- Probabilistic errors (8-13% miss rate)
- Fatigue modeling (slower over time)

**Args:**
- `action_name`: Action name from platform profile (e.g., "reaction_celebrate")

**Returns:** `True` if successful, `False` if error/mistake

**Example:**
```python
success = await interaction.click_action("reaction_celebrate")
if success:
    print("Clicked celebrate reaction!")
else:
    print("Missed the button (human error)")
```

---

#### `async spam_action(action_name: str, count: int = 30) -> Dict[str, int]`

Spam action multiple times with full sophistication.

**Automatically handles:**
- Popup re-opening (every 3 clicks for YouTube reactions)
- Errors and fatigue
- Progress logging

**Args:**
- `action_name`: Action to spam (e.g., "reaction_heart")
- `count`: Number of times to perform action (default: 30)

**Returns:** Dictionary with metrics:
```python
{
    "success": 28,    # Successful clicks
    "errors": 2,      # Mistakes made
    "thinking_pauses": 9  # Times paused to think
}
```

**Example:**
```python
results = await interaction.spam_action("reaction_heart", count=30)
print(f"Sent {results['success']}/30 hearts ({results['errors']} mistakes)")
```

---

#### `get_stats() -> Dict[str, Any]`

Get current interaction statistics.

**Returns:** Dictionary with stats:
```python
{
    "platform": "youtube_chat",
    "sophistication": {
        "action_count": 25,
        "current_error_rate": 0.10,
        "fatigue_multiplier": 1.2,
        "is_fatigued": True
    },
    "human_behavior_available": True,
    "in_iframe": True
}
```

**Example:**
```python
stats = interaction.get_stats()
print(f"Performed {stats['sophistication']['action_count']} actions")
print(f"Fatigue: {stats['sophistication']['fatigue_multiplier']:.2f}x slower")
```

---

#### `reset_sophistication()`

Reset sophistication engine (clears fatigue, resets error rate).

**Use when:** Long break between action bursts (e.g., after 5+ minutes idle)

**Example:**
```python
# After long pause
await asyncio.sleep(300)  # 5 minutes
interaction.reset_sophistication()  # Reset fatigue
```

---

## Platform Profiles API

### Loading Profiles

```python
from modules.infrastructure.human_interaction import load_platform_profile

profile = load_platform_profile("youtube_chat")
```

### PlatformProfile Class

#### `get_action(action_name: str) -> Optional[Dict[str, Any]]`

Get action configuration.

**Returns:**
```python
{
    "coordinates": {"x": 359, "y": 759},
    "variance": {"x": 8, "y": 8},
    "action": "hover",
    "description": "Heart button - hover to open popup",
    "timing": {
        "before_hover": {"min": 0.15, "max": 0.35},
        "after_hover": {"min": 0.15, "max": 0.30}
    }
}
```

#### `get_coordinates(action_name: str) -> Optional[Tuple[int, int]]`

Get base coordinates for action.

**Returns:** `(x, y)` tuple

#### `requires_iframe() -> bool`

Check if platform requires iframe switching.

#### `get_iframe_selector() -> Optional[str]`

Get iframe selector if required.

---

## Sophistication Engine API

### SophisticationEngine Class

#### `__init__(base_error_rate=0.08, fatigue_threshold=20, thinking_probability=0.30)`

**Args:**
- `base_error_rate`: Base probability of mistakes (default: 8%)
- `fatigue_threshold`: Actions before fatigue (default: 20)
- `thinking_probability`: Chance of thinking pause (default: 30%)

#### `should_make_mistake() -> bool`

Determine if current action should be a mistake.

**Error rate increases with fatigue:**
- Actions 0-20: 8% error rate
- Actions 21-50: 8% → 13% (linear increase)
- Actions 50+: 13% max error rate

#### `get_fatigue_multiplier() -> float`

Get delay multiplier based on fatigue.

**Returns:** 1.0 to 1.8

**Fatigue curve:**
- Actions 0-20: 1.0x (normal)
- Actions 21-50: 1.0x → 1.8x (slowdown)
- Actions 50+: 1.8x (max fatigue)

#### `should_pause_to_think() -> bool`

Determine if should pause before action.

**Returns:** `True` 30% of the time

#### `get_thinking_duration() -> float`

Get random thinking pause duration.

**Returns:** 0.5 to 2.0 seconds

---

## Available Platforms

### youtube_chat

**Actions:**
- `party_toggle` - Hover to open reactions popup
- `reaction_100` - 💯 reaction
- `reaction_wide_eyes` - 😲 reaction
- `reaction_celebrate` - 🎉 reaction
- `reaction_smiley` - 😊 reaction
- `reaction_heart` - ❤️ reaction

**Iframe:** Required (`iframe#chatframe`)

### Future Platforms

- `youtube_studio` - YouTube Studio comments
- `linkedin` - LinkedIn commenting/posting
- `twitter` - X/Twitter posting/liking

---

## Error Handling

### Common Errors

**Platform not found:**
```python
try:
    interaction = get_interaction_controller(driver, "invalid_platform")
except FileNotFoundError as e:
    print(f"Platform not found: {e}")
    # Available: youtube_chat, linkedin, twitter
```

**Action not found:**
```python
try:
    await interaction.click_action("nonexistent_action")
except ValueError as e:
    print(f"Action not found: {e}")
```

**Iframe switch failed:**
```python
success = await interaction.click_action("reaction_heart")
if not success:
    print("Failed - iframe not accessible")
```

---

## Integration Examples

### YouTube !party Command

```python
# In party_reactor.py
from modules.infrastructure.human_interaction import get_interaction_controller

async def party_mode(self, total_clicks: int = 30):
    interaction = get_interaction_controller(self.driver, "youtube_chat")

    # Spam reactions with full sophistication
    results = await interaction.spam_action("reaction_celebrate", count=total_clicks)

    return results  # {"success": 28, "errors": 2, "thinking_pauses": 9}
```

### LinkedIn Commenting (Future)

```python
interaction = get_interaction_controller(driver, "linkedin")

# Type comment
await interaction.type_text("Great post!", field="comment_box")

# Submit
await interaction.click_action("submit_comment")
```

### X/Twitter Posting (Future)

```python
interaction = get_interaction_controller(driver, "twitter")

# Type tweet
await interaction.type_text("Hello world!", field="compose_tweet")

# Send
await interaction.click_action("send_tweet")
```

---

## Performance

### Typical Action Times

**Without anti-detection (instant):**
- Mouse teleportation: 0ms
- Click: 0ms
- Total: 0ms (DETECTABLE)

**With anti-detection (human-like):**
- Bezier curve movement: 200-500ms
- Thinking pause (30% chance): 500-2000ms
- Click + delays: 100-300ms
- Total: 300-2800ms (UNDETECTABLE)

### Spam Performance

**30 reactions:**
- Before: 4.5 seconds (5.7 reactions/sec) ← IMPOSSIBLE for humans
- After: 15-45 seconds (0.7-2.0 reactions/sec) ← Human-like

---

## Version History

**v0.1.0** (2025-12-16)
- Initial release
- YouTube Live Chat support
- Bezier curves, coordinate variance
- Probabilistic errors, fatigue modeling
- Thinking pauses

---

**See also:**
- README.md - Overview and quick start
- ModLog.md - Change history
- platforms/*.json - Platform configurations
