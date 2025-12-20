# Cursor IDE GPT Codex Restoration Guide

## Problem Statement
Cursor IDE update moved agent chat from right side to left side, causing GPT Codex to be removed/hidden since it was previously located on the left side where the agent chat now resides.

## Research Findings

### 1. Cursor IDE Panel System
Cursor uses VS Code's panel system with configurable locations:
- **Left Sidebar**: Explorer, Search, Source Control, Extensions, etc.
- **Right Sidebar**: Custom panels, extensions
- **Bottom Panel**: Terminal, Problems, Output, Debug Console
- **Editor Area**: Main code editing space

### 2. GPT Codex Location
GPT Codex typically appears as:
- A panel/extension in the left sidebar
- An inline code completion feature
- A separate view/panel that can be docked

### 3. Cursor Settings Location
Cursor settings are stored in:
- **Windows**: `%APPDATA%\Cursor\User\settings.json`
- **macOS**: `~/Library/Application Support/Cursor/User/settings.json`
- **Linux**: `~/.config/Cursor/User/settings.json`

## Solution Steps

### Step 1: Check Cursor Settings
1. Open Cursor IDE
2. Press `Ctrl+,` (Windows/Linux) or `Cmd+,` (macOS) to open Settings
3. Search for "Codex" or "GPT"
4. Check if Codex is disabled in settings

### Step 2: Check Extensions
1. Press `Ctrl+Shift+X` (Windows/Linux) or `Cmd+Shift+X` (macOS) to open Extensions
2. Search for "Codex" or "GPT"
3. Verify if Codex extension is:
   - Installed but disabled
   - Not installed
   - Hidden from view

### Step 3: Restore Panel Visibility
If Codex is a panel/view:

1. **Via Command Palette**:
   - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
   - Type "View: Show Codex" or "View: Toggle Codex"
   - Execute the command

2. **Via View Menu**:
   - Go to `View` → `Open View...`
   - Search for "Codex"
   - Select it to restore

### Step 4: Configure Panel Location
If Codex panel exists but is in wrong location:

1. **Move Panel**:
   - Right-click on Codex panel header
   - Select "Move Panel Right" or "Move Panel Left"
   - Or drag the panel to desired location

2. **Via Settings JSON**:
   ```json
   {
     "workbench.panel.defaultLocation": "right",
     "workbench.sideBar.location": "left"
   }
   ```

### Step 5: Check Cursor-Specific Settings
Cursor may have custom settings for AI features:

1. Open Settings (`Ctrl+,` or `Cmd+,`)
2. Search for:
   - `cursor.codex`
   - `cursor.gpt`
   - `cursor.ai`
   - `cursor.panel`
3. Check for any disabled/hidden settings

### Step 6: Reset Cursor Layout
If Codex still not visible:

1. **Reset Workbench Layout**:
   - Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
   - Type "View: Reset View Locations"
   - Execute to restore default layout

2. **Reset Window Layout**:
   - Command Palette
   - Type "View: Reset Window Layout"
   - Execute to restore all panels

### Step 7: Check Cursor Version & Updates
1. Go to `Help` → `About` to check Cursor version
2. Check if Codex was removed in recent update:
   - Visit Cursor changelog: https://cursor.com/changelog
   - Check if Codex was deprecated/replaced
   - Look for migration instructions

### Step 8: Alternative: Use Command Palette
If Codex functionality exists but panel is hidden:

1. Press `Ctrl+Shift+P` / `Cmd+Shift+P`
2. Type "Codex" to see available Codex commands
3. Use commands directly instead of panel

## Advanced Troubleshooting

### Check Cursor Configuration Files
1. Navigate to Cursor settings directory:
   ```powershell
   # Windows PowerShell
   cd $env:APPDATA\Cursor\User
   ```

2. Check `settings.json` for Codex-related settings:
   ```json
   {
     "cursor.codex.enabled": true,
     "cursor.codex.panelLocation": "left",
     "workbench.view.alwaysShowHeaderActions": true
   }
   ```

### Check Workspace Settings
1. Check `.vscode/settings.json` in workspace root
2. Look for Codex-related overrides
3. Remove any conflicting settings

### Reinstall Codex Extension (if applicable)
1. Extensions view (`Ctrl+Shift+X` / `Cmd+Shift+X`)
2. Search "Codex"
3. If found but disabled, click "Enable"
4. If not found, search marketplace for "GPT Codex" or "Cursor Codex"

## Cursor-Specific AI Features

### Understanding Cursor's AI Architecture
Cursor has multiple AI features:
- **Agent Chat**: Main AI assistant (now on left side)
- **Codex**: Code completion/suggestions (may be integrated into Agent Chat)
- **Composer**: Multi-file editing AI
- **Inline Suggestions**: Code completion as you type

### Possible Integration
Codex functionality may have been:
- **Integrated into Agent Chat**: Check if Codex features are now in Agent Chat panel
- **Replaced by Composer**: New multi-file editing replaces Codex
- **Moved to Inline Suggestions**: Codex now appears as inline completions

## Recommended Actions

### Immediate Steps:
1. ✅ Check Settings → Search "Codex" → Enable if found
2. ✅ Check Extensions → Search "Codex" → Enable if disabled
3. ✅ Command Palette → "View: Show Codex" → Execute
4. ✅ Check View menu → Open View → Search "Codex"

### If Not Found:
1. ✅ Check Cursor changelog for Codex deprecation
2. ✅ Verify Codex features are in Agent Chat
3. ✅ Check if inline suggestions replaced Codex
4. ✅ Contact Cursor support if feature was removed

## WSP Compliance Notes

**WSP 50 (Pre-Action Verification)**: Verified Cursor settings locations and panel system before providing solutions.

**WSP 83 (Documentation)**: This document serves as technical reference for IDE configuration issues.

**WSP 80 (DAE Architecture)**: Cursor IDE integration is part of the IDE FoundUps module cube-level architecture.

---

## Next Steps
1. Execute Step 1-4 above to restore Codex
2. If unsuccessful, check Cursor changelog for deprecation notice
3. Verify if Codex functionality moved to Agent Chat
4. Document findings in this file for future reference









