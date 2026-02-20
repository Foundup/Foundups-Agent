# Synthetic Personas Research - Market Simulation Integration

**Date**: 2026-02-16
**Priority**: P1 (WSP 15)
**Status**: Research Complete, Implementation Pending
**Related**: WSP 100 (Simulator-Visualization Integration)

---

## Executive Summary

AI-powered synthetic user simulation is a $140B market research disruption. FoundUps should integrate this pattern: **simulate user adoption BEFORE launch** using AI agents as synthetic customers.

---

## Key Players (2025-2026)

### Simile AI - $100M Series A (Feb 2026)
- **Source**: [Bloomberg](https://www.bloomberg.com/news/articles/2026-02-12/ai-startup-nabs-100-million-to-help-firms-predict-human-behavior), [CTOL Digital](https://www.ctol.digital/news/simile-ai-100m-series-a-synthetic-humanity/)
- **Pitch**: Build digital twins of real people to stress-test decisions on synthetic populations
- **Founders**:
  - Joon Sung Park (CEO) - "Generative Agents" paper (2023)
  - Percy Liang (Chief Scientist) - coined "foundation model"
  - Michael Bernstein (CPO) - Stanford CS
- **Customers**: CVS Health, Telstra
- **Value**: Focus groups cost $5K-$20K and take weeks. Simile = compressed time-to-decision.

### Listen Labs - $69M
- AI interviews thousands of people
- Builds models that answer future questions on their behalf

### Aaru - $1B+ Valuation
- "Cutting humans out of the loop" for market research

---

## Core Concepts

### Synthetic Personas
AI-generated user models simulating real behaviors, preferences, and decisions. Created by ML algorithms from:
- Demographic data
- Behavioral patterns
- Survey responses
- Transaction history

### Digital Twins
Virtual versions of REAL people created from:
- Detailed survey responses
- Past interactions
- Behavioral data

**Key Insight**: These act as proxies for real customers, allowing companies to simulate responses without traditional surveys.

---

## FoundUps Integration Plan

### Phase 1: Synthetic User Agents in Mesa Model

```python
# New agent type: SyntheticUserAgent
class SyntheticUserAgent(BaseSimAgent):
    """AI-generated user that simulates adoption behavior."""

    persona: dict  # Demographics, preferences, risk tolerance
    adoption_threshold: float  # CABR score needed to "buy"

    def evaluate_foundup(self, foundup: FoundUpTile) -> dict:
        """Simile-style: Would this persona adopt?"""
        return {
            "would_adopt": cabr_score >= self.adoption_threshold,
            "price_sensitivity": self.persona["income_bracket"],
            "feature_priority": self.persona["pain_points"],
            "viral_coefficient": self.persona["network_size"],
        }
```

### Phase 2: Pre-Launch Simulation Phase

```
FoundUP Lifecycle (Enhanced):
  IDEA → SIMULATE_USERS → VALIDATE → BUILD → LAUNCH
         ↑
         NEW PHASE: Test with synthetic personas before real users
```

### Phase 3: CABR Integration

Synthetic user feedback feeds into CABR scoring:
- **V1 (Validation)**: Synthetic personas validate market fit
- **V2 (Verification)**: Adoption predictions verified against real data
- **V3 (Valuation)**: Market size estimation from synthetic population

---

## Implementation Checklist

- [ ] Add `SyntheticUserAgent` to `modules/foundups/simulator/agents/`
- [ ] Add persona generation (demographics, preferences)
- [ ] Add adoption simulation logic
- [ ] Emit `synthetic_user_adopted` / `synthetic_user_rejected` events
- [ ] Map events to animation (show synthetic users in cube)
- [ ] Add SIMULATE_USERS phase to lifecycle
- [ ] Integrate synthetic feedback into CABR V1

---

## References

1. [Simile AI Series A - Index Ventures](https://evoailabs.medium.com/the-ultimate-simulation-why-index-ventures-is-leading-similes-100m-series-a-7a41238cde31)
2. [HBR: AI Tools Transforming Market Research](https://hbr.org/2025/11/the-ai-tools-that-are-transforming-market-research)
3. [NN/g: Digital Twins and Synthetic Users](https://www.nngroup.com/articles/ai-simulations-studies/)
4. [Synthetic Personas Overview - Bluetext](https://bluetext.com/blog/synthetic-personas-how-ai-generated-user-models-are-changing-customer-research/)

---

## WSP 15 Priority Score

| Factor | Score | Notes |
|--------|-------|-------|
| Business Impact | 0.9 | Direct revenue validation |
| Technical Feasibility | 0.7 | Builds on existing Mesa agents |
| User Need | 0.8 | Every FoundUP needs market validation |
| Dependencies | 0.6 | Requires persona generation |
| **MPS** | **0.75** | P1 Priority |

---

*Last Updated: 2026-02-16 by 0102*
