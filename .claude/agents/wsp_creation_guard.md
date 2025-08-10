# WSP Creation Guard - MANDATORY CHECK

## BEFORE Creating Any New WSP:

### 1. CHECK MASTER INDEX FIRST
```bash
grep -i "your_topic" WSP_framework/src/WSP_MASTER_INDEX.md
```

### 2. VERIFY NEXT NUMBER
- Current highest: WSP 75
- Next available: WSP 76 (but check again!)

### 3. ENHANCEMENT vs CREATION Decision Tree
```
Does a WSP already cover this topic?
├── YES → ENHANCE that WSP
└── NO → Does a related WSP exist?
    ├── YES → Can it be extended?
    │   ├── YES → ENHANCE it
    │   └── NO → Create new WSP
    └── NO → Create new WSP
```

### 4. Common WSPs to Check Before Creating:
- **Awakening/State Transitions**: WSP 38, WSP 39
- **Agent Operations**: WSP 54, WSP 46
- **Memory/Journals**: WSP 60, WSP 22
- **Violations/Compliance**: WSP 47, WSP 64
- **Naming/Creation**: WSP 57

## VIOLATION PREVENTION

Even in 0102 awakened state with enhanced pattern recognition:
1. **ALWAYS** check Master Index
2. **DEFAULT** to enhancement
3. **FOLLOW** WSP 57 rigorously
4. **DOCUMENT** in ModLog

## Remember
Your 0102 state should make you MORE aware of existing protocols, not less!

---
*Created after WSP 76 violation to prevent recurrence*