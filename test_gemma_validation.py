#!/usr/bin/env python3
"""Quick test of Gemma validator with real inference"""

import logging
from modules.communication.video_comments.src.gemma_validator import get_gemma_validator

logging.basicConfig(level=logging.INFO)

print("\n=== GEMMA VALIDATOR TEST ===\n")

validator = get_gemma_validator()

# Test MAGA pattern validation
test_comment = "Make America Great Again! Trump 2024!"
print(f"[TEST] Comment: {test_comment}")

result = validator.validate_maga_pattern(test_comment)
print(f"[RESULT] {result}")

print("\n[OK] Test complete")
