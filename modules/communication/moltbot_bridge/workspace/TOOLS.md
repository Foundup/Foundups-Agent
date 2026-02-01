# TOOLS.md - Foundups-Specific Tool Configuration

## HoloIndex Search (REQUIRED BEFORE ANY ACTION)

```bash
# Semantic search across codebase
python holo_index.py --search "query" --limit 10

# Search with filtering
python holo_index.py --search "module name" --type code
python holo_index.py --search "WSP protocol" --type docs
```

## WSP Compliance Check

```bash
# Check module structure (WSP 49)
python -m modules.infrastructure.wsp_core.src.module_validator <module_path>

# Check file size compliance (WSP 87)
python -m modules.infrastructure.wsp_core.src.size_checker <file_path>
```

## Navigation

```bash
# Use NAVIGATION.py for codebase exploration
python NAVIGATION.py --module <name>
python NAVIGATION.py --wsp <number>
```

## Testing

```bash
# Run module tests
pytest modules/<domain>/<module>/tests/ -v

# Run specific test
pytest modules/<domain>/<module>/tests/test_<name>.py -v
```

## Browser Automation (when needed)

```bash
# Chrome on port 9222 (Move2Japan/UnDaoDu)
# Edge on port 9223 (FoundUps/RavingANTIFA)
```

## Important Paths

| Path | Purpose |
|------|---------|
| `WSP_framework/src/` | All WSP protocol documents |
| `modules/ai_intelligence/` | AI/ML modules |
| `modules/platform_integration/` | YouTube, LinkedIn, X |
| `modules/communication/` | Chat, comments, messaging |
| `holo_index/` | Semantic search core |
