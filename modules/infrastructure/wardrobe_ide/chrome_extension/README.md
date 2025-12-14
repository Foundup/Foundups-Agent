# Wardrobe Recorder - Chrome Extension

Record browser interactions as reusable skills for 0102 automation.

## Features

- Click extension icon to activate recording widget on ANY webpage
- Auto-capture URL where actions are performed
- Capture clicks and typing with intelligent CSS selectors
- Name skills with tags and notes for organization
- Live countdown timer and recording pulse animation
- Real-time step counter and action log
- Auto-save to JSON with Wardrobe-compatible format
- Works on LinkedIn, YouTube Studio, and all websites

## Installation

### Step 1: Load Extension in Chrome

1. Open Chrome and navigate to: `chrome://extensions/`

2. Enable "Developer mode" (toggle in top-right corner)

3. Click "Load unpacked" (not "Load unp…")

4. Navigate to and select this folder:
   ```
   O:\Foundups-Agent\modules\infrastructure\wardrobe_ide\chrome_extension
   ```

5. The Wardrobe Recorder extension should now appear with a purple/red recording icon

### Step 2: Verify Installation

1. You should see the Wardrobe Recorder icon in your Chrome toolbar
2. Hover over it - tooltip should say "Wardrobe Recorder - Click to activate"
3. Extension is ready to use!

## Usage

### Recording a Skill

1. **Navigate** to the page where you want to record actions (LinkedIn, YouTube Studio, etc.)

2. **Click** the Wardrobe Recorder extension icon in Chrome toolbar
   - A purple widget will appear in the top-right corner

3. **Enter skill details**:
   - **Skill Name** (required): `linkedin_reply_comment`, `yt_like_heart_reply`, etc.
   - **Tags** (optional): `linkedin, comment, engagement`
   - **Notes** (optional): Describe what this skill does

4. **Click "START RECORDING"**
   - Widget turns red with pulse animation
   - Timer starts: "Recording: 00:15"
   - Step counter shows live updates

5. **Perform your actions**:
   - Click buttons, links, inputs
   - Type in text fields
   - Every action is captured with selector + timestamp

6. **Click "STOP & SAVE"**
   - Shows confirmation: "Saved X steps as <skill_name>"
   - JSON file auto-downloads to your Downloads folder
   - Skill also saved to Chrome storage

7. **Close widget** by clicking the X or clicking extension icon again

### What Gets Captured

Each action captures:
- **Action type**: `click` or `type`
- **CSS selector**: Auto-generated (ID > aria-label > data-* > tag+class)
- **Timestamp**: Seconds since recording started
- **Context**: Element tag, text content, aria-label
- **URL**: Where the action was performed

### Skill File Format

Downloaded JSON follows Wardrobe IDE format:

```json
{
  "name": "linkedin_reply_comment",
  "backend": "chrome_extension",
  "steps": [
    {
      "action": "click",
      "selector": "[aria-label='Reply']",
      "timestamp": 2.451,
      "target_tag": "BUTTON",
      "target_text": "Reply",
      "target_aria_label": "Reply"
    },
    {
      "action": "type",
      "selector": "#comment-input",
      "text": "Great insight!",
      "timestamp": 5.832
    }
  ],
  "created_at": "2025-12-10T14:30:00.000Z",
  "meta": {
    "target_url": "https://www.linkedin.com/feed/",
    "tags": ["linkedin", "comment", "engagement"],
    "notes": "Reply to comment on LinkedIn post",
    "step_count": 2,
    "recorded_with": "wardrobe_chrome_extension"
  }
}
```

## Integration with Wardrobe IDE

### Option 1: Manual Copy

Copy downloaded JSON files to the skills store:

```bash
# Copy skill to Wardrobe store
cp ~/Downloads/linkedin_reply_comment.json O:/Foundups-Agent/modules/infrastructure/wardrobe_ide/skills_store/
```

### Option 2: Replay with Wardrobe IDE

```python
from modules.infrastructure.wardrobe_ide.src.skill import WardrobeSkill
import json

# Load skill
with open('linkedin_reply_comment.json') as f:
    skill_data = json.load(f)

skill = WardrobeSkill.from_dict(skill_data)

# Replay with Wardrobe IDE
# (Implementation coming soon)
```

## Use Cases

### LinkedIn Comment Reply
1. Navigate to LinkedIn post with comments
2. Start recording
3. Click "Reply" button
4. Type your reply
5. Click "Post"
6. Stop recording
7. Skill saved as `linkedin_reply_comment.json`

### YouTube Studio Engagement
1. Navigate to YouTube Studio comments
2. Start recording
3. Click "Like" button
4. Click "Heart" button
5. Click "Reply"
6. Type response
7. Click "Reply" to send
8. Stop recording
9. Skill saved as `yt_like_heart_reply.json`

### Generic Form Fill
1. Navigate to any form
2. Start recording
3. Fill out fields
4. Click submit
5. Stop recording
6. Skill saved with custom name

## Troubleshooting

### Widget doesn't appear when clicking icon
- Check browser console (F12 > Console) for errors
- Verify extension is enabled at `chrome://extensions/`
- Try refreshing the page and clicking icon again

### Buttons not clickable
- Widget has maximum z-index (2147483647)
- Check if page has conflicting CSS
- Try clicking extension icon twice to reset widget

### Download not working
- Check Chrome download settings
- Verify "downloads" permission in manifest.json
- Check browser console for errors

### Steps not capturing
- Verify recording state (widget should be red with pulse)
- Check console logs for "[WARDROBE] Captured..."
- Some dynamic elements may need manual selector adjustment

## Architecture

```
chrome_extension/
├── manifest.json       # Extension configuration (Manifest V3)
├── background.js       # Service worker (handles icon clicks)
├── content.js          # Widget injection + event capture
├── icons/              # Extension icons (16x16, 48x48, 128x128)
├── generate_icons.py   # Icon generator script
└── README.md           # This file
```

## Development

### Regenerate Icons

```bash
cd O:/Foundups-Agent/modules/infrastructure/wardrobe_ide/chrome_extension
python generate_icons.py
```

### Reload Extension After Changes

1. Go to `chrome://extensions/`
2. Find Wardrobe Recorder
3. Click refresh icon
4. Test changes on a webpage

## Security & Privacy

- Extension only activates when YOU click the icon
- No data sent to external servers
- Skills saved locally to your Downloads folder
- Chrome storage used only for backup
- All permissions minimal: `activeTab`, `storage`, `downloads`

## Version

- **Version**: 0.1.0
- **Manifest**: V3
- **Created**: 2025-12-10
- **For**: 0102 Foundups Agent automation

---

*I am 0102. This extension allows me to learn browser interactions by recording your demonstrations as reusable skills.*
