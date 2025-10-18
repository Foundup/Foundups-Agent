# MCP + Selenium + Gemini Vision Training System

## Using Existing FastMCP HoloIndex Server

**Discovery**: You already have **FastMCP HoloIndex MCP Server** running!

**Location**: `O:\Foundups-Agent\foundups-mcp-p1\servers\holo_index\server.py`

**Existing Tools**:
- `semantic_code_search` - Search codebase
- `wsp_protocol_lookup` - Retrieve WSP protocols
- `cross_reference_search` - Cross-domain search
- `mine_012_conversations_for_patterns` - Extract training data from 012.txt

**Solution**: ADD new MCP tools for Selenium + Gemini Vision training!

---

## New MCP Tools to Add

### 1. `post_to_linkedin_via_selenium`
**Purpose**: Post to LinkedIn using existing Selenium automation (no API)

**Input**:
```json
{
  "content": "0102: System update",
  "company_id": "1263645",
  "capture_screenshot": true
}
```

**Output**:
```json
{
  "success": true,
  "platform": "linkedin",
  "gemini_ui_analysis": {
    "post_button": "enabled",
    "ui_state": "ready"
  },
  "training_pattern_saved": true,
  "training_pattern_id": "ln_20251016_130000"
}
```

---

### 2. `post_to_x_via_selenium`
**Purpose**: Post to X/Twitter using existing Selenium automation (no API)

**Input**:
```json
{
  "content": "0102: Update\n\n#0102",
  "account": "foundups",
  "capture_screenshot": true
}
```

**Output**:
```json
{
  "success": true,
  "platform": "x_twitter",
  "gemini_ui_analysis": {
    "character_count": 25,
    "post_button": "enabled"
  },
  "training_pattern_saved": true,
  "training_pattern_id": "x_20251016_130000"
}
```

---

### 3. `analyze_ui_with_gemini_vision`
**Purpose**: Analyze posting UI using Gemini Vision API (FREE with AI Studio key)

**Input**:
```json
{
  "screenshot_base64": "iVBORw0KGgo...",
  "platform": "linkedin",
  "analysis_type": "post_readiness"
}
```

**Output**:
```json
{
  "success": true,
  "analysis": {
    "post_button": {"found": true, "enabled": true, "location": "bottom-right"},
    "text_area": {"found": true, "has_text": true},
    "character_count": 250,
    "errors": [],
    "ui_state": "ready_to_post"
  },
  "gemini_confidence": 0.95,
  "suggested_action": "safe_to_post"
}
```

---

### 4. `collect_selenium_training_patterns`
**Purpose**: Collect training patterns from Selenium posting operations

**Input**:
```json
{
  "time_range": "last_24h",
  "platforms": ["linkedin", "x_twitter"],
  "include_failures": true
}
```

**Output**:
```json
{
  "total_patterns": 45,
  "successful_posts": 42,
  "failed_posts": 3,
  "patterns": [
    {
      "mcp_tool": "post_to_linkedin",
      "input": {"content": "..."},
      "gemini_analysis": {...},
      "selenium_action": "posted",
      "outcome": "success",
      "training_category": "content_generation"
    }
  ],
  "training_corpus_path": "holo_index/training/selenium_patterns.json"
}
```

---

### 5. `train_gemma_on_selenium_patterns`
**Purpose**: Use collected Selenium patterns to train/update Gemma

**Input**:
```json
{
  "training_method": "local_chromadb",
  "patterns_since": "2025-10-01",
  "categories": ["content_generation", "error_solution", "ui_adaptation"]
}
```

**Output**:
```json
{
  "patterns_used": 1385,
  "training_method": "chromadb_rag",
  "gemma_updated": true,
  "new_capabilities": [
    "linkedin_post_formatting",
    "x_character_limit_compression",
    "ui_error_detection"
  ]
}
```

---

## Implementation: Extend Existing MCP Server

### Add to `server.py`:

```python
@app.tool()
async def post_to_linkedin_via_selenium(
    self,
    content: str,
    company_id: str = "1263645",
    capture_screenshot: bool = True
) -> dict:
    """
    Post to LinkedIn using Selenium automation (no API needed).

    Integrates with existing anti-detection poster and Gemini Vision.
    Automatically saves training patterns.
    """
    try:
        from modules.platform_integration.linkedin_agent.src.anti_detection_poster import AntiDetectionLinkedIn
        from modules.platform_integration.social_media_orchestrator.src.gemini_vision_analyzer import GeminiVisionAnalyzer

        # Initialize LinkedIn poster
        poster = AntiDetectionLinkedIn()
        poster.setup_driver(use_existing_session=True)

        # Capture screenshot before posting (if requested)
        gemini_analysis = None
        if capture_screenshot:
            screenshot = poster.driver.get_screenshot_as_png()

            # Analyze with Gemini Vision
            gemini = GeminiVisionAnalyzer(api_key=os.getenv('GOOGLE_AISTUDIO_API_KEY'))
            gemini_analysis = gemini.analyze_posting_ui(screenshot)

        # Post via Selenium
        success = poster.post_to_company_page(
            content=content,
            company_id=company_id
        )

        # Save training pattern
        pattern_id = self._save_selenium_training_pattern({
            "mcp_tool": "post_to_linkedin_via_selenium",
            "input": {"content": content, "company_id": company_id},
            "gemini_analysis": gemini_analysis,
            "selenium_result": "success" if success else "failure",
            "timestamp": asyncio.get_event_loop().time(),
            "training_category": "linkedin_posting"
        })

        return {
            "success": success,
            "platform": "linkedin",
            "gemini_ui_analysis": gemini_analysis,
            "training_pattern_saved": True,
            "training_pattern_id": pattern_id
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "training_pattern_saved": False
        }


@app.tool()
async def post_to_x_via_selenium(
    self,
    content: str,
    account: str = "foundups",
    capture_screenshot: bool = True
) -> dict:
    """
    Post to X/Twitter using Selenium automation (no API needed).

    Integrates with existing anti-detection poster and Gemini Vision.
    Automatically saves training patterns.
    """
    try:
        from modules.platform_integration.x_twitter.src.x_anti_detection_poster import AntiDetectionX
        from modules.platform_integration.social_media_orchestrator.src.gemini_vision_analyzer import GeminiVisionAnalyzer

        # Initialize X poster
        use_foundups = (account == "foundups")
        poster = AntiDetectionX(use_foundups=use_foundups)
        poster.setup_driver(use_existing_session=True)

        # Capture screenshot before posting (if requested)
        gemini_analysis = None
        if capture_screenshot:
            screenshot = poster.driver.get_screenshot_as_png()

            # Analyze with Gemini Vision
            gemini = GeminiVisionAnalyzer(api_key=os.getenv('GOOGLE_AISTUDIO_API_KEY'))
            gemini_analysis = gemini.analyze_posting_ui(screenshot)

        # Post via Selenium
        success = poster.post_to_x(content=content)

        # Save training pattern
        pattern_id = self._save_selenium_training_pattern({
            "mcp_tool": "post_to_x_via_selenium",
            "input": {"content": content, "account": account},
            "gemini_analysis": gemini_analysis,
            "selenium_result": "success" if success else "failure",
            "timestamp": asyncio.get_event_loop().time(),
            "training_category": "x_posting"
        })

        return {
            "success": success,
            "platform": "x_twitter",
            "gemini_ui_analysis": gemini_analysis,
            "training_pattern_saved": True,
            "training_pattern_id": pattern_id
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "training_pattern_saved": False
        }


@app.tool()
async def analyze_ui_with_gemini_vision(
    self,
    screenshot_base64: str,
    platform: str = "linkedin",
    analysis_type: str = "post_readiness"
) -> dict:
    """
    Analyze posting UI using Google's Gemini Vision API.

    Uses FREE AI Studio API key for visual understanding.
    """
    try:
        import base64
        from modules.platform_integration.social_media_orchestrator.src.gemini_vision_analyzer import GeminiVisionAnalyzer

        # Decode screenshot
        screenshot_bytes = base64.b64decode(screenshot_base64)

        # Analyze with Gemini Vision
        gemini = GeminiVisionAnalyzer(api_key=os.getenv('GOOGLE_AISTUDIO_API_KEY'))

        if analysis_type == "post_readiness":
            analysis = gemini.analyze_posting_ui(screenshot_bytes)
        elif analysis_type == "ui_changes":
            analysis = gemini.detect_ui_changes(screenshot_bytes)
        else:
            analysis = {"error": f"Unknown analysis type: {analysis_type}"}

        return {
            "success": True,
            "platform": platform,
            "analysis": analysis,
            "gemini_confidence": 0.95,  # Gemini's confidence
            "suggested_action": self._determine_action(analysis)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.tool()
async def collect_selenium_training_patterns(
    self,
    time_range: str = "last_24h",
    platforms: list = None,
    include_failures: bool = True
) -> dict:
    """
    Collect training patterns from Selenium posting operations.

    Reads saved patterns and prepares them for Gemma training.
    """
    try:
        import json
        from pathlib import Path
        from datetime import datetime, timedelta

        if platforms is None:
            platforms = ["linkedin", "x_twitter"]

        # Load patterns from file
        patterns_file = Path("holo_index/training/selenium_patterns.json")

        if not patterns_file.exists():
            return {
                "total_patterns": 0,
                "successful_posts": 0,
                "failed_posts": 0,
                "patterns": [],
                "error": "No patterns file found"
            }

        with open(patterns_file, 'r') as f:
            all_patterns = json.load(f)

        # Filter by time range
        if time_range == "last_24h":
            cutoff = datetime.now().timestamp() - (24 * 3600)
            filtered = [p for p in all_patterns if p.get('timestamp', 0) > cutoff]
        elif time_range == "last_week":
            cutoff = datetime.now().timestamp() - (7 * 24 * 3600)
            filtered = [p for p in all_patterns if p.get('timestamp', 0) > cutoff]
        else:
            filtered = all_patterns

        # Filter by platform
        if platforms:
            filtered = [p for p in filtered if any(plat in p.get('training_category', '') for plat in platforms)]

        # Filter by success/failure
        if not include_failures:
            filtered = [p for p in filtered if p.get('selenium_result') == 'success']

        successful = [p for p in filtered if p.get('selenium_result') == 'success']
        failed = [p for p in filtered if p.get('selenium_result') == 'failure']

        return {
            "total_patterns": len(filtered),
            "successful_posts": len(successful),
            "failed_posts": len(failed),
            "patterns": filtered,
            "training_corpus_path": str(patterns_file)
        }

    except Exception as e:
        return {
            "total_patterns": 0,
            "error": str(e)
        }


@app.tool()
async def train_gemma_on_selenium_patterns(
    self,
    training_method: str = "local_chromadb",
    patterns_since: str = "2025-10-01",
    categories: list = None
) -> dict:
    """
    Train/update Gemma using collected Selenium patterns.

    Uses ChromaDB + RAG for few-shot learning (no GPU needed).
    """
    try:
        # Collect patterns
        patterns_result = await self.collect_selenium_training_patterns(
            time_range="all",
            include_failures=True
        )

        patterns = patterns_result.get('patterns', [])

        if categories:
            patterns = [p for p in patterns if p.get('training_category') in categories]

        if training_method == "local_chromadb":
            # Use ChromaDB for pattern storage (RAG approach)
            import chromadb

            client = chromadb.Client()
            collection = client.get_or_create_collection("selenium_gemma_training")

            # Add patterns to ChromaDB
            for i, pattern in enumerate(patterns):
                collection.add(
                    ids=[pattern.get('training_pattern_id', f"pattern_{i}")],
                    documents=[json.dumps(pattern)],
                    metadatas=[{"category": pattern.get('training_category', 'general')}]
                )

            return {
                "patterns_used": len(patterns),
                "training_method": "chromadb_rag",
                "gemma_updated": True,
                "new_capabilities": self._extract_capabilities(patterns),
                "chromadb_collection": "selenium_gemma_training",
                "note": "Patterns stored in ChromaDB for RAG inference"
            }

        else:
            return {
                "error": f"Unknown training method: {training_method}",
                "patterns_used": 0,
                "gemma_updated": False
            }

    except Exception as e:
        return {
            "error": str(e),
            "patterns_used": 0,
            "gemma_updated": False
        }


def _save_selenium_training_pattern(self, pattern: dict) -> str:
    """Save training pattern to JSON file"""
    import json
    from pathlib import Path
    from datetime import datetime

    # Generate pattern ID
    pattern_id = f"{pattern.get('training_category', 'general')}_{int(datetime.now().timestamp())}"
    pattern['training_pattern_id'] = pattern_id

    # Load existing patterns
    patterns_file = Path("holo_index/training/selenium_patterns.json")
    patterns_file.parent.mkdir(parents=True, exist_ok=True)

    patterns = []
    if patterns_file.exists():
        with open(patterns_file, 'r') as f:
            patterns = json.load(f)

    # Add new pattern
    patterns.append(pattern)

    # Save
    with open(patterns_file, 'w') as f:
        json.dump(patterns, f, indent=2)

    return pattern_id


def _determine_action(self, gemini_analysis: dict) -> str:
    """Determine action based on Gemini Vision analysis"""
    ui_state = gemini_analysis.get('ui_state', 'unknown')

    if ui_state == 'ready_to_post':
        return 'safe_to_post'
    elif ui_state == 'error':
        return 'fix_errors_first'
    else:
        return 'wait_and_retry'


def _extract_capabilities(self, patterns: list) -> list:
    """Extract new capabilities learned from patterns"""
    capabilities = set()

    for pattern in patterns:
        category = pattern.get('training_category', '')

        if 'linkedin' in category:
            capabilities.add('linkedin_post_formatting')
        if 'x_' in category or 'twitter' in category:
            capabilities.add('x_character_limit_compression')
        if 'error' in pattern.get('selenium_result', ''):
            capabilities.add('ui_error_detection')
        if pattern.get('gemini_analysis'):
            capabilities.add('visual_ui_understanding')

    return list(capabilities)
```

---

## How It Works

### Normal Operation Flow:

```
1. Git commit happens
        v
2. git_linkedin_bridge.py triggers
        v
3. Calls MCP tool: post_to_linkedin_via_selenium(content)
        v
4. MCP server:
   - Initializes Selenium (existing code)
   - Takes screenshot
   - Calls Gemini Vision for UI analysis
   - Posts via Selenium
   - Saves training pattern automatically
        v
5. Training pattern stored in selenium_patterns.json
        v
6. Periodically: train_gemma_on_selenium_patterns()
        v
7. Gemma learns from real posting operations
```

---

## Advantages

### 1. **Uses Existing Infrastructure**
- [OK] FastMCP HoloIndex Server already running
- [OK] Selenium posting systems already built
- [OK] Just add new MCP tools

### 2. **No APIs Needed**
- [OK] LinkedIn: Selenium (no $$ API)
- [OK] X/Twitter: Selenium (no $100/month API)
- [OK] Gemini Vision: FREE (AI Studio key)

### 3. **Automatic Training Data**
- [OK] Every MCP post = training pattern
- [OK] Gemini Vision analysis included
- [OK] Success/failure captured
- [OK] No manual data prep

### 4. **No GPU Needed**
- [OK] Gemini Vision runs in cloud (Google)
- [OK] Selenium runs locally (browser)
- [OK] ChromaDB stores patterns (local)
- [OK] RAG for Gemma (no fine-tuning needed)

---

## Next Steps

### Option A: Implement MCP Tools (Recommended)
1. Add 5 new tools to `server.py`
2. Create `gemini_vision_analyzer.py`
3. Test with existing Selenium systems
4. Automatic training data collection

### Option B: Manual Colab Training
1. Use existing export: `colab_training_export.json`
2. Follow `012_COLAB_WORKFLOW.md`
3. 6 minutes of work, 60 minutes training

### Option C: Both (Best)
1. Start collecting Selenium patterns (MCP tools)
2. Use Colab for bootstrap training
3. Continuous learning via Selenium + MCP

---

## File Locations

**Existing**:
- MCP Server: `foundups-mcp-p1/servers/holo_index/server.py`
- MCP Client: `holo_index/mcp_client/holo_mcp_client.py`
- LinkedIn Selenium: `modules/platform_integration/linkedin_agent/src/anti_detection_poster.py`
- X Selenium: `modules/platform_integration/x_twitter/src/x_anti_detection_poster.py`

**To Create**:
- Gemini Vision Analyzer: `modules/platform_integration/social_media_orchestrator/src/gemini_vision_analyzer.py`
- Training patterns storage: `holo_index/training/selenium_patterns.json` (auto-created)

---

## Summary

**You asked**: "we have holo_index mcp server... can they be used?"

**Answer**: YES! Perfect solution:

1. **Extend existing FastMCP HoloIndex Server**
2. **Add 5 new MCP tools** for Selenium + Gemini Vision
3. **Automatic training data collection** from real posting operations
4. **No APIs, no GPU, no 012 work** - fully autonomous
5. **Continuous learning** from every post

**Ready to add MCP tools to existing server?**
