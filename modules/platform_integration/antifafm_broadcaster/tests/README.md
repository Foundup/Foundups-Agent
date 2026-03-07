# antifaFM Broadcaster Tests

Test suite for YouTube Live streaming automation.

## Test Files

| File | Purpose | Type |
|------|---------|------|
| `test_go_live_steps.py` | Step-by-step Go Live automation debugging | Manual/Interactive |

## Prerequisites

1. **Chrome with Debug Port**: Chrome must be running with `--remote-debugging-port=9222`
   ```powershell
   chrome.exe --remote-debugging-port=9222
   ```

2. **Logged into YouTube**: Chrome must be logged into the antifaFM YouTube account

3. **Selenium**: `pip install selenium`

## Running Tests

### Interactive Go Live Test
```powershell
python modules/platform_integration/antifafm_broadcaster/tests/test_go_live_steps.py
```

This test will:
1. Check Chrome debug port is open
2. Connect via Selenium
3. Navigate to YouTube Studio
4. Print all visible buttons (debugging)
5. Click Create button
6. Print menu items (debugging)
7. Click Go Live
8. Check stream status
9. Take screenshots at each step (saved to `logs/`)

## Test Output

Screenshots are saved to `logs/` folder:
- `screenshot_before_create_*.png`
- `screenshot_after_create_*.png`
- `screenshot_after_go_live_*.png`
- `screenshot_final_*.png`

## Expected Flow

```
YouTube Studio Dashboard
    ↓
Click CREATE button (top right)
    ↓
Dropdown appears with options
    ↓
Click "Go live" in dropdown
    ↓
Stream page loads ("Connect your encoder")
    ↓
FFmpeg connects via RTMP
    ↓
"You're live" appears
```

## Troubleshooting

### Chrome not found on port 9222
- Start Chrome with: `chrome.exe --remote-debugging-port=9222`
- Or use the dependency launcher: main.py → option 13

### Create button not found
- Check screenshots to see actual page state
- YouTube Studio UI may have changed
- May need to update selectors in `youtube_go_live.py`

### Go Live not in dropdown
- Create was clicked but dropdown didn't appear
- Try increasing wait time after Create click
- Check screenshot_after_create_*.png

## WSP Compliance

- WSP 5: Test coverage for automation
- WSP 6: Test documentation
- WSP 27: DAE Architecture testing
