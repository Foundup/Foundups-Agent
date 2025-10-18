# WSP 84 Violation Archive

## Archive Date: 2025-09-18

These modules were archived because they violated WSP 84 Module Evolution Protocol by creating "enhanced_" versions instead of evolving existing modules in place.

## Archived Files:

### 1. `stream_resolver_enhanced.py` (26,718 bytes, Aug 24)
- **Original**: `stream_resolver.py` (52,701 bytes, Sept 18) - **SUPERIOR**
- **Issue**: Enhanced version became stale while original continued evolving
- **Current version has**: NO-QUOTA mode, intelligent quota testing, session caching
- **Enhanced version lacks**: Modern features, 26KB vs 52KB of functionality

### 2. `test_stream_resolver_enhanced.py`
- **Issue**: Test file for stale enhanced module
- **Current**: Main stream_resolver.py has proper test coverage

### 3. `enhanced_commands.py`
- **Original**: `commands.py` - **SUPERIOR**
- **Issue**: /help command already exists in main commands.py
- **Only unique feature**: /smacks command (timeout breakdown)
- **Note**: /smacks functionality could be added to main commands.py if needed

## WSP 84 Lesson Learned:

**❌ WRONG**: Create `enhanced_*`, `improved_*`, `intelligent_*` versions
**✅ RIGHT**: Edit existing files directly (trust git for safety)

The original files continued evolving and became superior to the "enhanced" versions, proving that module evolution in-place is the correct approach.

## References:
- WSP 84: Code Memory Verification Protocol
- Module Evolution Protocol (Section 2.6)
- Anti-Pattern: "enhanced_", "*_fixed", "*_improved", "*_v2" naming