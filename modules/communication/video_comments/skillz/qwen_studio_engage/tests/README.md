# Qwen Studio Engage - Test Suite

Tests for the YouTube Studio autonomous comment engagement skill.

## Test Files

### Integration Tests
- **test_qwen_studio_engage.py** - Full autonomous flow (Qwen → Gemma → Vision)
- **test_youtube_studio_vision.py** - Vision automation validation test

### Vision AI Tests
- **test_gemini_simple.py** - Basic Gemini Vision button detection
- **test_gemini_vision_like.py** - Gemini Vision like/heart targeting
- **test_gemini_vision_visible.py** - Gemini Vision with visual feedback
- **test_gemini_coordinates.py** - Coordinate-based clicking
- **test_gemini_heart_stay_open.py** - Heart button with persistent window

### Selenium Tests
- **test_selenium_like.py** - DOM-based button detection
- **test_visible_heart_click.py** - Visual heart click test

### Experimental Tests
- **test_heart_not_like.py** - Distinguish heart from like button
- **test_heart_offset.py** - Offset-based heart targeting
- **test_map_buttons.py** - DOM structure mapping

### Utility Tests
- **test_save_screenshot.py** - Screenshot capture
- **test_simple_chrome.py** - Basic browser test
- **test_studio_simple.py** - Studio navigation test
- **test_browser_nav.py** - Browser session test

## Documentation
- **YOUTUBE_STUDIO_VISION_TEST.md** - Test documentation and findings

## Running Tests

```bash
# Run full autonomous test
python modules/communication/video_comments/skills/qwen_studio_engage/tests/test_qwen_studio_engage.py

# Run Gemini Vision test
python modules/communication/video_comments/skills/qwen_studio_engage/tests/test_gemini_simple.py
```

## Status

- ✅ Autonomous architecture working
- ✅ Gemini Vision (Tier 2) functional
- ⏸️ Awaiting UI-TARS (Tier 1) for precise targeting
