#!/usr/bin/env python3
"""
Test WRE Git Skill - SkillExecutor functionality

Location: holo_index/wre_integration/tests/test_wre_skill.py
"""

import sys
import os
import logging
from pathlib import Path

# Add repo root to path (3 levels up from tests/)
repo_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(repo_root))

from holo_index.wre_integration.skill_executor import SkillExecutor

# Setup logging to see output
logging.basicConfig(level=logging.INFO)


def test_git_skill():
    print("Testing WRE Git Skill...")
    executor = SkillExecutor(repo_root=repo_root)
    
    # Manually trigger the skill
    triggers = [{
        "type": "manual_test",
        "skill": "qwen_gitpush",
        "payload": {"reason": "testing"}
    }]
    
    executor.execute_wre_skills(triggers)


if __name__ == "__main__":
    test_git_skill()

