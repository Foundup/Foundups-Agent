#!/usr/bin/env python3
"""
Debug CodeIndex integration
"""

import sys
sys.path.insert(0, '.')

from holo_index.qwen_advisor.advisor import QwenAdvisor, AdvisorContext

print('=== DEBUGGING CODEINDEX INTEGRATION ===')

context = AdvisorContext(
    query='stream_resolver',
    code_hits=[{'file_path': 'modules/platform_integration/stream_resolver/src/no_quota_stream_checker.py'}],
    wsp_hits=[]
)

advisor = QwenAdvisor()

# Test the guidance synthesis directly
guidance = advisor._synthesize_guidance(
    llm_analysis={'summary': 'test'},
    wsp_analysis={'risk_level': 'low'},
    rules_guidance={'compliant': True},
    troubleshooting_guidance='',
    integration_gaps=None,
    context=context,
    enable_dae_cube_mapping=False,
    enable_function_indexing=True
)

print(f'Guidance length: {len(guidance)}')
print(f'Contains SURGERY: {"[SURGERY]" in guidance}')
print(f'Contains LEGO: {"[LEGO]" in guidance}')
print(f'Contains CIRCULATION: {"[CIRCULATION]" in guidance}')
print(f'Contains CHOICE: {"[CHOICE]" in guidance}')
print(f'Contains ASSUMPTIONS: {"[ASSUMPTIONS]" in guidance}')

# Print first 800 chars to see what's in the guidance
print(f'\nGuidance preview:\n{guidance[:800]}')
