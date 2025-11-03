# Qwen/Grok Autonomous Bug Fixing Architecture
**WSP Compliance**: WSP 77 (Agent Coordination), WSP 15 (MPS Scoring), WSP 96 (Skills)

## [LIGHTNING] Core Insight

**012's Vision**: "why cant it fix the bug if its simple... level 1 or 2 or delegate it to grok to fix... 3 plus but grok should read claude.me and follow wsp and use holo to find and fix... but qwen and gemma should be able to VERY specifically say exactly what to fix no?"

**Answer**: YES! They should DIRECTLY fix bugs, not just create reports!

## First Principles: What Should Happen?

**Bad (Current Thinking)**:
```
Gemma: Detects "unicode_error"
Qwen: "This is fixable, complexity=1"
0102: [UNAVAILABLE - daemon is running 24/7]
Result: Bug report created, nobody fixes it ❌
```

**Good (Your Vision)**:
```
Gemma: "UnicodeEncodeError at banter_engine.py:156, pattern '[U+1F44B]'"
Qwen: Read file → Generate Edit → Execute → Verify → Done! ✓
Result: Bug FIXED in 200-500ms ✓
```

## Corrected 3-Phase Architecture

### Phase 1 (Gemma Associate): Precise Detection
**Input**: Bash output from daemon (via BashOutput tool)
**Processing**: Apply regex patterns from skill JSON
**Output**: EXACT error location + EXACT pattern

**Example Output**:
```json
{
  "error_type": "unicode_error",
  "file": "modules/ai_intelligence/banter_engine/src/banter_engine.py",
  "line": 156,
  "pattern": "[U+1F44B]",
  "context": "UnicodeEncodeError: 'cp932' codec can't encode character",
  "wsp_15_mps": {
    "complexity": 1,
    "importance": 4,
    "deferability": 5,
    "impact": 4,
    "total_mps": 14,
    "priority": "P1"
  }
}
```

### Phase 2 (Qwen Partner): Autonomous Execution

#### Branch 1: Simple Fixes (Complexity 1-2)
**Qwen executes DIRECTLY**:

```python
def qwen_fix_simple_bug(detection: Dict) -> Dict:
    """
    Qwen autonomously fixes complexity 1-2 bugs

    Tools available:
    - Read(file_path): Read files
    - Edit(file_path, old_string, new_string): Edit files
    - Bash(command): Run shell commands
    - WebFetch/HoloIndex: Research patterns
    """

    # 1. Read the file with the bug
    file_content = Read(detection["file"])

    # 2. Load fix pattern from skill JSON
    skill = load_skill("youtube_daemon_monitor.json")
    pattern = skill["error_patterns"][detection["error_type"]]
    fix_action = pattern["fix_action"]  # e.g., "apply_unicode_conversion_fix"
    wre_pattern = pattern.get("wre_pattern", None)  # e.g., "unicode_escape_to_emoji"

    # 3. Generate EXACT Edit command
    if fix_action == "apply_unicode_conversion_fix":
        old_string = find_buggy_line(file_content, detection["line"])
        new_string = apply_wre_pattern(old_string, wre_pattern)

        # 4. Execute Edit
        Edit(
            file_path=detection["file"],
            old_string=old_string,
            new_string=new_string
        )

        # 5. Verify fix worked
        verify_result = Bash(f"python -c 'import {module_from_path(detection['file'])}; print(\"OK\")'")

        if verify_result.success:
            # 6. Announce fix
            post_to_undaodu(pattern["announcement_template"])

            # 7. Update skill learning stats
            update_skill_stats(skill, "bugs_fixed", 1)

            return {
                "status": "fixed",
                "action": "auto_fix",
                "fix_applied": new_string,
                "verification": "passed"
            }
        else:
            # Rollback and create bug report
            return {
                "status": "failed",
                "action": "create_bug_report",
                "reason": "Fix verification failed"
            }

    elif fix_action == "run_reauthorization_script":
        # Execute OAuth reauth script
        result = Bash(pattern["fix_command"])
        return {
            "status": "fixed" if result.success else "failed",
            "action": "auto_fix",
            "command_executed": pattern["fix_command"]
        }
```

#### Branch 2: Moderate Fixes (Complexity 3-4)
**Delegate to Grok with SPECIFIC plan**:

```python
def qwen_delegate_to_grok(detection: Dict) -> Dict:
    """
    Qwen creates SPECIFIC fix plan for Grok to execute
    """

    # 1. Research fix pattern using HoloIndex
    holo_results = HoloIndex.search(f"{detection['error_type']} fix pattern")

    # 2. Load CLAUDE.md context for Grok
    claude_md = Read("O:/Foundups-Agent/CLAUDE.md")

    # 3. Create SPECIFIC fix instructions
    grok_instructions = f"""
    CONTEXT: You are fixing a {detection['error_type']} bug in a running daemon.

    REQUIREMENTS:
    - Read CLAUDE.md and follow WSP protocols
    - Use HoloIndex to find existing patterns: python holo_index.py --search "{detection['error_type']}"
    - Apply WSP 15 MPS scoring for any new code
    - Follow WSP 50 (Pre-Action Verification)

    BUG DETAILS:
    - File: {detection['file']}:{detection['line']}
    - Error: {detection['pattern']}
    - Complexity: {detection['wsp_15_mps']['complexity']}
    - Priority: {detection['wsp_15_mps']['priority']}

    RECOMMENDED FIX:
    {detection.get('recommended_fix', 'Analyze file and apply architectural fix')}

    EXPECTED EDIT:
    - Read {detection['file']}
    - Identify root cause (API state, logic error, etc.)
    - Apply fix following existing patterns found in HoloIndex
    - Verify with tests
    - Update skill JSON with new pattern

    DELIVERABLE:
    - Exact Edit commands applied
    - Verification test results
    - Pattern description for skill JSON
    """

    # 4. Send to Grok API
    grok_result = GrokAPI.execute(
        instructions=grok_instructions,
        tools=["Read", "Edit", "Bash", "HoloIndex"],
        context={
            "claude_md": claude_md,
            "skill_json": load_skill("youtube_daemon_monitor.json"),
            "holo_results": holo_results
        }
    )

    return grok_result
```

#### Branch 3: Complex Issues (Complexity 5+)
**Create detailed bug report for 0102**:

```python
def qwen_create_bug_report(detection: Dict) -> Dict:
    """
    Qwen creates comprehensive bug report for 0102 review
    """

    # Research existing patterns
    holo_results = HoloIndex.search(f"{detection['error_type']} architecture")

    # Generate report
    bug_report = f"""
# Bug Report: {detection['error_type']}
**Priority**: {detection['wsp_15_mps']['priority']}
**Complexity**: {detection['wsp_15_mps']['complexity']}/5
**Detected**: {datetime.now()}

## WSP 15 MPS Scoring
- Complexity: {detection['wsp_15_mps']['complexity']} (Very High - requires architectural changes)
- Importance: {detection['wsp_15_mps']['importance']}
- Deferability: {detection['wsp_15_mps']['deferability']}
- Impact: {detection['wsp_15_mps']['impact']}
- Total MPS: {detection['wsp_15_mps']['total_mps']}

## Error Details
**File**: {detection['file']}:{detection['line']}
**Pattern**: {detection['pattern']}
**Context**: {detection['context']}

## Bash Output Excerpt
```
{detection.get('bash_excerpt', 'N/A')}
```

## HoloIndex Research
{holo_results}

## Recommended Fix
{detection.get('recommended_fix', 'Requires 0102 architectural review')}

## Code References
- [{detection['file']}]({detection['file']})
- Related modules: {detection.get('related_modules', [])}

## Next Steps for 0102
1. Review architectural implications
2. Decide on fix approach
3. Update WSP protocols if needed
4. Apply fix and verify
5. Update skill JSON with new pattern
"""

    # Save report
    report_path = f"bugs/{detection['daemon_name']}/{timestamp}_{detection['error_type']}.md"
    Write(report_path, bug_report)

    return {
        "status": "reported",
        "action": "bug_report_created",
        "report_path": report_path
    }
```

### Phase 3 (Learning): Pattern Storage

```python
def store_fix_pattern(detection: Dict, fix_result: Dict):
    """
    Store successful fix pattern in skill JSON for future use
    """

    skill = load_skill("youtube_daemon_monitor.json")

    # Update learning stats
    skill["learning_stats"]["total_bugs_detected"] += 1
    if fix_result["status"] == "fixed":
        skill["learning_stats"]["total_bugs_fixed"] += 1
        skill["learning_stats"]["last_fix"] = datetime.now().isoformat()
    elif fix_result["status"] == "reported":
        skill["learning_stats"]["total_reports_generated"] += 1

    # Calculate pattern accuracy
    skill["learning_stats"]["pattern_accuracy"] = (
        skill["learning_stats"]["total_bugs_fixed"] /
        skill["learning_stats"]["total_bugs_detected"]
    )

    # Store new WRE pattern if discovered
    if "wre_pattern_discovered" in fix_result:
        error_pattern = skill["error_patterns"][detection["error_type"]]
        error_pattern["wre_pattern"] = fix_result["wre_pattern_discovered"]

    # Save updated skill
    save_skill("youtube_daemon_monitor.json", skill)
```

## Tool Requirements

### Qwen Needs:
1. **Read tool**: Read files to analyze bugs
2. **Edit tool**: Apply surgical fixes
3. **Bash tool**: Run verification commands
4. **HoloIndex access**: Research existing patterns
5. **Skill JSON access**: Load fix actions and WRE patterns

### Grok Needs (for complexity 3-4):
1. **Same tools as Qwen**: Read, Edit, Bash, HoloIndex
2. **CLAUDE.md context**: Follow WSP protocols
3. **Skill JSON context**: Understand system patterns
4. **Specific instructions from Qwen**: Exact fix plan

## Example: Complete Bug Fix Flow

### Detection (Gemma)
```json
{
  "error_type": "unicode_error",
  "file": "modules/ai_intelligence/banter_engine/src/banter_engine.py",
  "line": 156,
  "pattern": "[U+1F44B]",
  "wsp_15_mps": {"complexity": 1}
}
```

### Execution (Qwen)
```python
# Complexity 1 → Qwen fixes directly
file_content = Read("modules/ai_intelligence/banter_engine/src/banter_engine.py")

# Find buggy line
old_string = "    text = f'[U+{hex_code}]'"

# Apply WRE pattern "unicode_escape_to_emoji"
new_string = "    text = chr(int(hex_code, 16))  # Convert Unicode escape to emoji"

# Execute fix
Edit(
    file_path="modules/ai_intelligence/banter_engine/src/banter_engine.py",
    old_string=old_string,
    new_string=new_string
)

# Verify
Bash("python -c 'from modules.ai_intelligence.banter_engine.src.banter_engine import BanterEngine; print(\"OK\")'")

# Announce
post_to_undaodu("012 fix applied - Unicode emoji conversion restored")
```

### Result
- **Time**: 200-500ms
- **Tokens**: 200-300 (Qwen execution)
- **Status**: Bug FIXED
- **No 0102 needed**: ✓

## Integration Points

### 1. BashOutput Integration
```python
def monitor_daemon(bash_id: str, skill_path: str):
    while True:
        # Read bash output
        output = BashOutput(bash_id)

        # Phase 1: Gemma detection
        detections = gemma_detect_errors(output, skill)

        # Phase 2: Qwen execution
        for detection in detections:
            if detection["wsp_15_mps"]["complexity"] <= 2:
                qwen_fix_simple_bug(detection)
            elif detection["wsp_15_mps"]["complexity"] <= 4:
                qwen_delegate_to_grok(detection)
            else:
                qwen_create_bug_report(detection)

        # Wait for next check
        time.sleep(skill["health_check_interval"])
```

### 2. WRE Pattern Memory
```json
{
  "unicode_escape_to_emoji": {
    "pattern": "f'[U+{hex_code}]'",
    "fix": "chr(int(hex_code, 16))",
    "success_rate": 0.95,
    "applications": 47
  },
  "oauth_token_refresh": {
    "pattern": "Token has been REVOKED",
    "fix": "python modules/platform_integration/youtube_auth/scripts/reauthorize_set1.py",
    "success_rate": 1.0,
    "applications": 12
  }
}
```

## Benefits of This Architecture

**24/7 Autonomous Operation**: ✓
- Qwen fixes simple bugs (complexity 1-2) without human intervention
- Grok handles moderate bugs (complexity 3-4) with specific plans
- 0102 reviews complex bugs (complexity 5+) asynchronously

**Token Efficiency**: ✓
- Simple fixes: 200-300 tokens (Qwen execution)
- Moderate fixes: 500-1000 tokens (Grok delegation)
- Complex bugs: Bug report only (100 tokens)

**Precision**: ✓
- Gemma provides EXACT location (file:line)
- Qwen generates EXACT Edit commands
- No guessing, no vibecoding

**Learning**: ✓
- Successful fixes stored in WRE pattern memory
- Skill JSON updated with learning stats
- Future bugs fixed faster (pattern reuse)

## Next Steps

1. **Implement Qwen execution logic**: Add Read/Edit/Bash tool calls to Qwen
2. **Integrate BashOutput**: Connect to live daemon shells
3. **Create WRE pattern store**: Store successful fix patterns
4. **Add Grok delegation**: API integration for complexity 3-4 bugs
5. **Test with live daemon**: Monitor bash 56046d for Unicode errors

---
*Created: 2025-10-20*
*Author: 012 (vision) + 0102 (implementation)*
*WSP Compliance: WSP 77, WSP 15, WSP 96*
