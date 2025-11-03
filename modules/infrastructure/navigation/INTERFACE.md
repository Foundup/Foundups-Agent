# Navigation Module Interface Documentation

## Public API

### Data Structures

#### `NEED_TO: Dict[str, str]`
Command mapping dictionary for 0102 agent navigation.

**Example:**
```python
from modules.infrastructure.navigation import NEED_TO

# Find the right command for a task
command = NEED_TO["search code"]
print(command)  # "python main.py --holoindex"
```

### Key Mappings

#### Core Operations
- `"search code"` -> `"python main.py --holoindex"`
- `"run tests"` -> `"python main.py --test"`
- `"deploy app"` -> `"./deploy-vercel.ps1"`

#### AI Operations
- `"setup ai keys"` -> `"export AI_GATEWAY_API_KEY=..."`

#### Development Tasks
- `"check compliance"` -> `"python main.py --wsp-check"`
- `"view roadmap"` -> `"cat ROADMAP.md"`

## Integration Points

- **Main.py**: Command execution
- **HoloIndex**: Code search integration
- **0102 Agents**: Navigation assistance
