# HoloIndex Qwen Advisor Test Plan (FMAS Draft)

- **Status:** Draft (Pre-Implementation)
- **Protocols:** WSP 22, WSP 35, WSP 17, WSP 18, WSP 87

## Functional Coverage
| ID | Area | Description | Planned Tests |
|----|------|-------------|---------------|
| F1 | Advisor Prompt | Qwen prompt composition uses retrieved code + WSP context | tests/holo_index/test_qwen_advisor_prompt.py |
| F2 | Advisor Output | Compliance reminders include WSP 18 TODOs | tests/holo_index/test_qwen_advisor_output.py |
| F3 | Retrieval Gap Detection | Advisor flags missing NAVIGATION assets | tests/holo_index/test_qwen_advisor_gap.py |
| F4 | CLI Flags | --llm-advisor toggles behaviour safely | tests/holo_index/test_cli_flags.py |
| F5 | Telemetry | Usage log written to E:/HoloIndex/indexes/holo_usage.json | tests/holo_index/test_advisor_telemetry.py |
| F6 | Reward Signals | Advisor rating/ack events award points and log telemetry | tests/holo_index/test_reward_events.py |

## Modular Tests
| ID | Component | Verification |
|----|-----------|-------------|
| M1 | Cache Layer | Replays cached response on identical query hash |
| M2 | Model Loader | Handles missing Qwen model gracefully |
| M3 | Prompt Templates | Template references WSP IDs correctly |
| M4 | Reward Engine | Points + rating/ack payload recorded in telemetry |

## Acceptance
| ID | Scenario | Criteria |
|----|----------|----------|
| A1 | Advisor Enabled | Search returns compliance checklist with zero exceptions |
| A2 | Advisor Disabled | Search falls back to pure retrieval |
| A3 | Idle Automation | Advisor output reminds to run idle tasks once integrated |

### Notes
- Populate test files once advisor implementation is ready.
- Advisor output now includes an auto-link to this plan when test cues are detected.
- Reward telemetry captures advisor ratings and acknowledgement events for future analysis.
- Update this plan and TESTModLog entries with actual testcase names and results (WSP 22).
