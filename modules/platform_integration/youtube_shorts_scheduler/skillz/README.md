# YouTube Shorts Scheduler Skills

This directory contains AI skills for the youtube_shorts_scheduler module following WSP 95 (WRE Skills Wardrobe Protocol).

## Available Skills

| Skill | Intent Type | Agent | Status |
|-------|-------------|-------|--------|
| `ffcpln_title_enhance` | GENERATION | Qwen + Gemma | prototype |

## Architecture

```
skills/
├── ffcpln_title_enhance/     # FFCPLN clickbait title generation
│   ├── SKILL.md              # Instructions (WSP 95)
│   ├── executor.py           # Python implementation
│   └── tests/                # Unit tests
└── README.md                 # This file
```

## WSP 95 Compliance

Skills follow the micro chain-of-thought paradigm:
1. Qwen executes multi-step reasoning
2. Gemma validates each step
3. Pattern fidelity ≥ 90% required for production

## Usage

```python
from modules.platform_integration.youtube_shorts_scheduler.skills.ffcpln_title_enhance import FFCPLNTitleEnhanceSkill

skill = FFCPLNTitleEnhanceSkill()
result = skill.execute(context)
```
