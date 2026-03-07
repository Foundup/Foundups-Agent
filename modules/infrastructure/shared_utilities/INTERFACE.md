# shared_utilities Interface Specification

**WSP 11 Compliance:** In Progress
**Last Updated:** 2025-09-25
**Version:** 0.1.0

## [OVERVIEW] Module Overview

**Domain:** infrastructure
**Purpose:** [Brief description of module functionality]

## [API] Public API

### Primary Classes

#### SharedUtilities
```python
class SharedUtilities:
    """Main class for [module functionality]"""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize SharedUtilities

        Args:
            config: Optional configuration dictionary
        """

    def process(self, [parameters]) -> [ReturnType]:
        """[Method description]

        Args:
            [parameters]: [Parameter description]

        Returns:
            [ReturnType]: [Return value description]

        Raises:
            [ExceptionType]: [When exception is raised]
        """
```

### Utility Functions

#### utility_shared_utilities
```python
def utility_shared_utilities([parameters]) -> [ReturnType]:
    """[Function description]

    Args:
        [parameters]: [Parameter description]

    Returns:
        [ReturnType]: [Return value description]
    """
```

### YouTube Channel Registry
```python
from modules.infrastructure.shared_utilities.youtube_channel_registry import (
    get_channels,
    get_channel_ids,
    get_channel_keys,
    get_rotation_order,
    add_channel,
)

# Load registry
channels = get_channels()
channel_ids = get_channel_ids(role="live_check")
rotation_keys = get_rotation_order(role="comments")

# Add new channel
ok, msg = add_channel({
    "key": "newchannel",
    "id": "UCxxxxxxxxxxxx",
    "name": "NewChannel",
    "handle": "@NewChannel",
})
```

### LinkedIn Account Registry
```python
from modules.infrastructure.shared_utilities.linkedin_account_registry import (
    get_accounts,
    get_company_id,
    get_article_url,
    get_admin_url,
    get_company_page_url,
    get_default_company,
    list_all_accounts,
    ACCOUNT_ALIASES,
)

# Get all accounts from LINKEDIN_ACCOUNTS_JSON env var
accounts = get_accounts()  # {"foundups": "1263645", "undaodu": "68706058", ...}

# Get company ID with fuzzy matching/aliases
company_id = get_company_id("foundups")  # "1263645"
company_id = get_company_id("monk")      # "68706058" (alias for undaodu)
company_id = get_company_id("m2j")       # "104834798" (alias for move2japan)

# Get URLs for company pages
article_url = get_article_url("foundups")  # Direct article editor URL
admin_url = get_admin_url("undaodu")       # Company admin posts URL
page_url = get_company_page_url("move2japan")  # Public company page

# Get default company (from LINKEDIN_DEFAULT_COMPANY env var)
default_id = get_default_company()  # Falls back to "1263645" (foundups)

# List all accounts with URLs (for debugging)
all_info = list_all_accounts()
```

#### Environment Configuration
```bash
# .env or .env.example
LINKEDIN_DEFAULT_COMPANY=foundups
LINKEDIN_ACCOUNTS_JSON={"foundups":"1263645","undaodu":"68706058","move2japan":"104834798",...}
```

#### Available Aliases
| Alias | Maps To | Company ID |
|-------|---------|------------|
| monk, 012, michael, mjt | undaodu | 68706058 |
| m2j, japan | move2japan | 104834798 |
| fu, foundups® | foundups | 1263645 |
| aw, wall | autonomouswall | 35532191 |
| See ACCOUNT_ALIASES dict for full list |||

#### LinkedInCompany Constants
```python
from modules.infrastructure.shared_utilities.linkedin_account_registry import LinkedInCompany

# Use constants instead of string literals for type safety
company_id = get_company_id(LinkedInCompany.FOUNDUPS)
company_id = get_company_id(LinkedInCompany.UNDAODU)
company_id = get_company_id(LinkedInCompany.MOVE2JAPAN)
```

### CTO Note: Forking This Codebase

> **For teams forking FoundUps-Agent to build their own pAVS ecosystem:**

**What's Externalized (Easy)**:
- Company **IDs** are loaded from `LINKEDIN_ACCOUNTS_JSON` env var
- Default company from `LINKEDIN_DEFAULT_COMPANY` env var
- No code changes needed for ID-only customization

**What's Hardcoded (Requires Changes)**:
- Company **names** (e.g., "foundups", "undaodu") appear in ~72 places across 13 files
- These are used in: enum definitions, config mappings, string comparisons, default values

**To Fork**:
1. Update `LinkedInCompany` class in `linkedin_account_registry.py` with your company names
2. Run the bulk migration skill to find/replace across codebase:
   ```bash
   python -m modules.infrastructure.wre_core.skillz.qwen_bulk_import_migration.executor \
     --preset linkedin_registry --dry-run
   ```
3. Create custom replacement_map in migration spec for your company names
4. Update `ACCOUNT_ALIASES` dict for your team's preferred shortcuts

**Files Most Affected**:
- `linkedin_agent/` - 2 files (posting, engagement)
- `social_media_orchestrator/` - 6 files (channel config, routing)
- `browser_actions/` - 1 file (LinkedIn actions)
- `ai_overseer/skillz/` - 1 file (company poster skill)

**Design Decision (2026-03-07)**: Company names were kept as readable strings rather than UUIDs for developer ergonomics. The `LinkedInCompany` constants provide type-safety while maintaining readability.

## [CONFIG] Configuration

### Required Configuration
```python
# Example configuration
config = {
    "setting1": "value1",
    "setting2": 42
}
```

### Optional Configuration
```python
# Optional settings with defaults
optional_config = {
    "timeout": 30,  # Default: 30 seconds
    "retries": 3    # Default: 3 attempts
}
```

## [USAGE] Usage Examples

### Basic Usage
```python
from modules.infrastructure.shared_utilities import SharedUtilities

# Initialize
instance = SharedUtilities(config)

# Use main functionality
result = instance.process([example_parameters])
print(f"Result: {result}")
```

### Advanced Usage
```python
# With custom configuration
custom_config = {
    "special_setting": "custom_value"
}
advanced_instance = SharedUtilities(custom_config)

# Use utility function
processed = utility_shared_utilities([input_data])
```

## [DEPENDENCIES] Dependencies

### Internal Dependencies
- modules.[domain].[dependency_module] - [Reason for dependency]

### External Dependencies
- [package_name]>=x.y.z - [Purpose of dependency]

## [TESTING] Testing

### Running Tests
```bash
cd modules/infrastructure/shared_utilities
python -m pytest tests/
```

### Test Coverage
- **Current:** 0% (implementation needed)
- **Target:** >=90%

## [PERFORMANCE] Performance Characteristics

### Expected Performance
- **Latency:** [expected latency]
- **Throughput:** [expected throughput]
- **Resource Usage:** [memory/CPU expectations]

## [ERRORS] Error Handling

### Common Errors
- **[ErrorType1]:** [Description and resolution]
- **[ErrorType2]:** [Description and resolution]

### Exception Hierarchy
```python
class [ModuleName]Error(Exception):
    """Base exception for [module_name]"""
    pass

class [SpecificError]([ModuleName]Error):
    """Specific error type"""
    pass
```

## [HISTORY] Version History

### 0.1.0 (2025-09-25)
- Initial interface specification
- Basic API structure defined
- Placeholder implementation created

## [NOTES] Development Notes

### Current Status
- [x] WSP 49 structure compliance
- [x] Interface specification defined
- [ ] Functional implementation (TODO)
- [ ] Comprehensive testing (TODO)

### Future Enhancements
- [Enhancement 1]
- [Enhancement 2]
- [Integration with other modules]

---

**WSP 11 Interface Compliance:** Structure Complete, Implementation Pending
