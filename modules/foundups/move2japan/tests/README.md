# Move2Japan FoundUp — Tests (WSP 34)

## Test Strategy

### POC Phase Tests

- [ ] BC0 Intent Capture — trigger detection for `!move2japan`
- [ ] Urgency classification — 5-level categorization
- [ ] Passport status parsing — yes/no/expired/in_progress/unknown
- [ ] Routing logic — timeframe × passport matrix
- [ ] Soft funnel link generation — .info vs .foundups.com routing

### Prototype Phase Tests

- [ ] Stakeholder memory persistence — cross-session state
- [ ] Stage gating logic — prerequisite enforcement
- [ ] Roadmap progression — unlock conditions
- [ ] Dashboard API — stakeholder profile retrieval

## Running Tests

```bash
pytest modules/foundups/move2japan/tests/ -v
```

## Test Patterns

Follow existing FoundUp test patterns from `modules/foundups/gotjunk/` and `modules/foundups/simulator/`.
