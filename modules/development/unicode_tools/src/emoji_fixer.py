#!/usr/bin/env python3
"""
Fix emoji characters in MCP manager for better compatibility
"""

# Read the file
with open('modules/infrastructure/mcp_manager/src/mcp_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define emoji replacements
replacements = {
    '[OK]': '[OK]',
    '[FAIL]': '[FAIL]',
    '[ROCKET]': '[START]',
    '[STOP]': '[STOP]',
    '[REFRESH]': '[RESTART]',
    '[U+1F3E5]': '[HEALTH]',
    '[U+1F9EA]': '[TEST]',
    '[BOT]': '[AI]',
    '[CLIPBOARD]': '[LOGS]',
    '[DATA]': '[METRICS]',
    '[AI]': '[MEMORY]',
    '[LINK]': '[DEPS]',
    '[U+2699]️': '[CONFIG]',
    '[TARGET]': '[TARGET]',
    '[GAME]': '[GAME]',
    '[FACTORY]': '[FACTORY]',
    '[TOOL]': '[TOOLS]',
    '[U+26A0]️': '[WARN]',
    '[U+1F5C2]️': '[FILE]',
    '[CELEBRATE]': '[SUCCESS]',
    '[IDEA]': '[TIP]',
    '[MUSIC]': '[WORKFLOW]',
}

# Apply replacements
for emoji, text in replacements.items():
    content = content.replace(emoji, text)

# Write back
with open('modules/infrastructure/mcp_manager/src/mcp_manager.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('All emojis replaced with text equivalents')
