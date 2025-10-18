# Migration Tools

WSP-compliant tools for migrating the FoundUps Agent codebase to Enterprise Domain structure.

## Tools

### fix_imports.py

**Purpose:** Migrates flat module imports to WSP 3 Enterprise Domain hierarchical structure.

**WSP Compliance:**
- [OK] Located in proper `tools/` directory per WSP 3
- [OK] Uses Enterprise Domain import mappings
- [OK] Includes violation scanning and reporting
- [OK] Follows WSP documentation standards

**Usage:**
```bash
# From project root
python tools/migration/fix_imports.py
```

**Features:**
- Scans for WSP 3 violations (flat imports)
- Automatically fixes Enterprise Domain import paths
- Reports on changes made
- Provides FMAS compliance verification instructions

**Enterprise Domain Mappings:**
- `modules.banter_engine.*` -> `modules.ai_intelligence.banter_engine.*`
- `modules.livechat.*` -> `modules.communication.livechat.*`
- `modules.youtube_auth.*` -> `modules.platform_integration.youtube_auth.*`
- `modules.token_manager.*` -> `modules.infrastructure.token_manager.*`
- And more...

## Related WSPs

- **WSP 3:** Enterprise Domain Architecture (compliance target)
- **WSP 1:** Module Refactoring (structure requirements)
- **WSP 4:** FMAS Usage (verification tool) 