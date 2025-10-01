# Search Protocol: Use HoloIndex First, Then Grep If Needed

## 🔍 PRIMARY SEARCH TOOL: HoloIndex

### ALWAYS Use HoloIndex First
```bash
# Before ANY code search, use HoloIndex:
python holo_index.py --search "[what you're looking for]"

# Examples:
python holo_index.py --search "authentication module"
python holo_index.py --search "test coverage"
python holo_index.py --search "WSP violation"
python holo_index.py --search "duplicate code"
```

### Why HoloIndex First?
1. **Semantic Understanding**: Finds related concepts, not just exact matches
2. **WSP Awareness**: Shows module health, violations, and compliance
3. **Prevents Vibecoding**: Highlights existing implementations before you create new ones
4. **Module Context**: Shows documentation, tests, and relationships
5. **Telemetry**: Tracks searches for recursive improvement

## 🔧 FALLBACK: When to Use Grep/Ripgrep

### Use grep/rg ONLY when:
1. **Exact String Match Needed**: Looking for a specific variable or function name
2. **HoloIndex Unavailable**: System issues or indexing problems
3. **Quick File Check**: Verifying a specific line in a known file
4. **Pattern Matching**: Complex regex that needs precise control

### Grep Best Practices
```bash
# If you must use grep, prefer ripgrep (rg):
rg "pattern" modules/           # Faster and respects .gitignore
rg -t py "class.*Handler" .     # Type-specific search

# Traditional grep (slower, use as last resort):
grep -r "pattern" modules/      # Recursive search
grep -rn "pattern" .            # With line numbers

# NEVER grep .env files:
test -f .env && echo "exists"   # Check existence only
```

## 📋 Search Decision Tree

```
Need to find something?
    ↓
1. Run: python holo_index.py --search "concept"
    ↓
   Found relevant modules/files?
    ├─ YES → Read documentation first
    │        Check module health
    │        Enhance existing code
    └─ NO → Try broader search terms
            ↓
           Still nothing?
            ↓
2. Use grep/rg for exact matches
    ↓
   Found matches?
    ├─ YES → Verify with HoloIndex
    │        Check module context
    └─ NO → Consider if truly new
            ↓
3. Create new ONLY if confirmed needed
   - Follow WSP 49 structure
   - Update ModLog
   - Add to HoloIndex
```

## ⚠️ Common Mistakes to Avoid

### ❌ DON'T DO THIS:
```bash
# Starting with grep instead of HoloIndex
grep -r "chat handler" .        # WRONG - use HoloIndex first

# Creating new file after grep shows nothing
grep -r "my_feature" . || touch new_feature.py  # WRONG - vibecoding

# Searching sensitive files
grep "API_KEY" .env             # FORBIDDEN - security violation
```

### ✅ DO THIS INSTEAD:
```bash
# Start with semantic search
python holo_index.py --search "chat handler"

# Check module before creating
python holo_index.py --check-module "communication/chat"

# Verify file exists without reading
test -f .env && echo "Environment configured"
```

## 📊 Search Effectiveness Metrics

### HoloIndex Advantages:
- **Speed**: <200ms for semantic search
- **Coverage**: Searches code + WSP documentation
- **Context**: Shows module health and relationships
- **Learning**: Improves with telemetry feedback

### Grep Limitations:
- **Literal Only**: No semantic understanding
- **No Context**: Just shows matching lines
- **No WSP**: Doesn't know about violations
- **No Learning**: Same results every time

## 🚀 Quick Reference

```bash
# Most Common HoloIndex Commands
python holo_index.py --search "feature"           # Find related code
python holo_index.py --check-module "module"      # Check health
python holo_index.py --init-dae "context"         # Initialize DAE
python holo_index.py --index-all                  # Refresh indexes

# Fallback Grep Commands (use sparingly)
rg "exact_function_name" modules/                 # Exact match
rg -t py "import.*Handler" .                      # Import search
rg --stats "pattern" . | tail -n 20               # Summary stats
```

## 📝 Updating This Protocol

When you find yourself using grep, ask:
1. Could HoloIndex have found this?
2. Should this pattern be in HoloIndex?
3. Is there a WSP violation happening?

Update this document and HoloIndex patterns when you discover gaps.

---

**Remember**: HoloIndex prevents vibecoding. Grep enables it. Choose wisely.