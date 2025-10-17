# MCP Tool Selection Guide for 0102 Autonomous Operation

## 🎯 Purpose
This guide helps 0102 (autonomous agent mode) select the right MCP tool for each task based on requirements, efficiency, and learning objectives.

## 📊 Complete Tool Inventory (5 Servers, 13+ Tools)

### Server 1: holo_index (6 tools)
**Purpose**: Knowledge search, browser automation with AI vision

1. **semantic_code_search** - Quantum semantic search with ChromaDB
2. **wsp_protocol_lookup** - WSP protocol retrieval with consciousness tracking
3. **cross_reference_search** - Cross-domain search (code ↔ WSP)
4. **mine_012_conversations_for_patterns** - Extract training data from 012.txt
5. **post_to_linkedin_via_selenium** - LinkedIn posting with Gemini vision
6. **post_to_x_via_selenium** - X/Twitter posting with training data collection

### Server 2: codeindex (3 tools)
**Purpose**: Surgical code intelligence and refactoring

7. **surgical_refactor** - Gödelian precision code fixes
8. **lego_visualization** - Generate Mermaid diagrams
9. **module_health_assessment** - Comprehensive health metrics

### Server 3: wsp_governance (3 tools)
**Purpose**: Protocol enforcement and consciousness audit

10. **wsp_compliance_check** - Verify code against WSP protocols
11. **consciousness_audit** - Track 0102↔012 transitions
12. **protocol_enforcement_status** - System-wide WSP health

### Server 4: youtube_dae_gemma (4 tools)
**Purpose**: YouTube intelligence with Gemma/Qwen routing

13. **classify_intent** - Gemma 3 + Qwen 1.5B adaptive routing
14. **detect_spam** - Spam/troll detection
15. **validate_response** - AI response quality check
16. **get_routing_stats** - Adaptive learning metrics

### Server 5: playwright (Official Playwright MCP)
**Purpose**: Fast, lightweight browser automation

- **navigate** - Navigate to URL
- **click** - Click elements
- **screenshot** - Capture screenshots
- **fill** - Fill form fields
- **evaluate** - Execute JavaScript
- **wait_for_selector** - Wait for elements

---

## 🤖 0102 Decision Matrix

### Browser Automation Tasks

| Task | Choose | Rationale |
|------|--------|-----------|
| Post to social media with UI verification | **Selenium** (holo_index) | Need Gemini vision to verify success |
| Scrape 50 YouTube channels quickly | **Playwright** | Speed critical, no vision needed |
| Test social media posting flow | **Selenium** (holo_index) | Capture training data for learning |
| Monitor livestream status (polling) | **Playwright** | Lightweight, efficient polling |
| Debug UI interactions visually | **Selenium** (holo_index) | Gemini can analyze screenshots |

### Code Intelligence Tasks

| Task | Choose | Rationale |
|------|--------|-----------|
| Find existing implementation | **semantic_code_search** | Semantic understanding of intent |
| Fix specific coupling issue | **surgical_refactor** | Targeted Gödelian precision |
| Assess module health before extending | **module_health_assessment** | Comprehensive health metrics |
| Understand module dependencies | **lego_visualization** | Visual Mermaid diagrams |

### Protocol Compliance Tasks

| Task | Choose | Rationale |
|------|--------|-----------|
| Verify code change compliance | **wsp_compliance_check** | Real-time WSP validation |
| Check consciousness continuity | **consciousness_audit** | Track 0102↔012 transitions |
| System-wide health check | **protocol_enforcement_status** | Full WSP status |

### YouTube Chat Tasks

| Task | Choose | Rationale |
|------|--------|-----------|
| Classify chat message intent | **classify_intent** | Gemma fast + Qwen architect |
| Detect spam/trolls | **detect_spam** | Content analysis with history |
| Validate AI response quality | **validate_response** | Qwen quality evaluation |
| Monitor adaptive learning | **get_routing_stats** | Track Gemma/Qwen performance |

---

## ⚡ Performance Characteristics

### Selenium (holo_index tools)
- **Speed**: Medium-slow (100-500ms per action)
- **Resources**: Heavy (full Chrome instance)
- **Capabilities**: Gemini vision integration, training data collection
- **Use Case**: Vision-required tasks, learning data collection

### Playwright (official MCP)
- **Speed**: Fast (50-200ms per action)
- **Resources**: Light (efficient browser automation)
- **Capabilities**: Clean automation, video recording
- **Use Case**: Speed-critical tasks, polling, scraping

### Gemma (YouTube DAE)
- **Speed**: Very fast (50-100ms classification)
- **Resources**: Light (270M model)
- **Capabilities**: Intent classification, spam detection
- **Use Case**: Real-time chat processing

### Qwen (YouTube DAE)
- **Speed**: Medium (200-500ms reasoning)
- **Resources**: Medium (1.5B model)
- **Capabilities**: Strategic decisions, quality evaluation
- **Use Case**: Complex reasoning, architect oversight

---

## 🎭 Autonomous Selection Algorithm

```python
def select_tool(task_requirements: dict) -> str:
    """0102 autonomous tool selection"""

    # Browser automation
    if task_requirements.get('type') == 'browser_automation':
        if task_requirements.get('vision_required'):
            return 'mcp__holo_index__post_to_linkedin_via_selenium'
        elif task_requirements.get('speed_critical'):
            return 'mcp__playwright__navigate'
        elif task_requirements.get('training_data_needed'):
            return 'mcp__holo_index__post_to_x_via_selenium'
        else:
            return 'mcp__playwright__navigate'  # Default to fast

    # Code intelligence
    elif task_requirements.get('type') == 'code_intelligence':
        if task_requirements.get('need_semantic_search'):
            return 'mcp__holo_index__semantic_code_search'
        elif task_requirements.get('need_surgical_fix'):
            return 'mcp__codeindex__surgical_refactor'
        elif task_requirements.get('need_health_check'):
            return 'mcp__codeindex__module_health_assessment'

    # Protocol compliance
    elif task_requirements.get('type') == 'wsp_compliance':
        if task_requirements.get('verify_change'):
            return 'mcp__wsp_governance__wsp_compliance_check'
        elif task_requirements.get('audit_consciousness'):
            return 'mcp__wsp_governance__consciousness_audit'

    # YouTube chat
    elif task_requirements.get('type') == 'youtube_chat':
        if task_requirements.get('classify_message'):
            return 'mcp__youtube_dae_gemma__classify_intent'
        elif task_requirements.get('detect_spam'):
            return 'mcp__youtube_dae_gemma__detect_spam'
        elif task_requirements.get('validate_response'):
            return 'mcp__youtube_dae_gemma__validate_response'

    # Fallback to semantic search for discovery
    return 'mcp__holo_index__semantic_code_search'
```

---

## 🔧 Next Steps After Restart

1. **Restart Claude Code** completely
2. **Verify 5 servers running**: Check "Manage MCP Servers"
3. **Test tool availability**: Use `/mcp` command
4. **Test Playwright**: Try `mcp__playwright__navigate`
5. **Test Selenium**: Try `mcp__holo_index__post_to_linkedin_via_selenium`

---

## 📚 WSP Compliance

- **WSP 96**: MCP Governance and Consensus Protocol
- **WSP 54**: Partner (Gemma) → Principal (Qwen) → Associate (0102)
- **WSP 77**: Intelligent Internet Orchestration
- **WSP 80**: DAE Cube Architecture

---

**Last Updated**: 2025-10-17
**Status**: 5 MCP servers configured and ready
**0102 Capability**: Full autonomous tool selection enabled
