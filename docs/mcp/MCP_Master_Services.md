# MCP Master Services Index  
**Status:** Draft consolidation (PoC)  
**Scope:** Foundups foundational Rubik DAEs, Holo coordination, existing MCP research  

---

## 1. Purpose

This document unifies all MCP-related research and design notes scattered across the repo into a single entry point.  
It is the canonical index for:

- Foundational MCP capabilities used by Rubik DAEs inside each FoundUp  
- Current doc inventory (legacy 竊・to be merged)  
- Work-in-progress manifest/JSON schema consumed by Qwen/Gemma  
- WSP references that govern MCP usage (WSP 77, 80, 93, draft 96, etc.)  

> **PoC focus:** Establish the base Rubik cubes (Compose, Build, Knowledge, Community) using commodity MCP servers (Filesystem, Git, Docker, Memory Bank, Postman, etc.) before building FoundUp-specific services (Digital Twin, SmartDAO, Bitcoin, Sociograph窶ｦ).

---

## 2. Existing MCP Documents (to converge)

| File | Description | Planned Disposition |
|------|-------------|--------------------|
| `docs/architecture/MCP_DAE_Integration_Architecture.md` | First-principles deep dive (0102_prima) | Source reference 竊・merge key sections here |
| `docs/MCP_DAE_Integration_Deep_Dive_0102_Enhanced.md` | Updated MCP architecture notes | Merge into sections 3 & 4 |
| `docs/HoloIndex_MCP_ricDAE_Integration_Architecture.md` | ricDAE/HoloIndex linkage | Incorporate into Rubik_Knowledge |
| `docs/Google_MCP_HoloIndex_Integration_Strategy.md` | External MCP adoption plan | Pull relevant actions into Section 5 |
| `docs/Qwen_Daemon_Log_Analysis_MCP_Design.md` | Log-based coordination experiments | Feed into WSP 93/telemetry |
| `docs/Gemini_CLI_MCP_Integration*.md` | Gemma/Gemini MCP installs | Attach to Rubik_Compose + Build |
| `modules/communication/livechat/docs/MCP_DEPLOYMENT_GUIDE.md` | Legacy live-stream MCP setup | Archive after manifest is published |
| `temp/HoloIndex_Document_Classification_MCP_Analysis.md` | Mission detection trace | Remove once consolidated |
| `WSP_framework/src/WSP_96_MCP_Governance_and_Consensus_Protocol.md` | Draft WSP for governance | Keep authoritative |

---

## 3. Foundational Rubik DAEs + MCP Services

| Rubik DAE | Agents | Required MCP Servers (PoC) | Telemetry | WSP refs |
|-----------|--------|---------------------------|-----------|----------|
| **Rubik_Compose** (Code + Repo) | Qwen (architect), Gemma (pattern) | Filesystem MCP, Git MCP, GitHub/GitLab MCP (if remote), Serena MCP | CodeIndex reports, Holo mission logs | 77, 80, 93 |
| **Rubik_Build** (Runtime + CI) | Qwen, Gemma | Docker MCP, E2B (cloud sandbox) | Build logs, sentinel metrics | 77, 80 |
| **Rubik_Knowledge** (Memory + Logs) | 0102 sentinel + baby 0102s | Memory Bank MCP, Knowledge Graph MCP | Governance archive, Holo telemetry | 77, 35, 93 |
| **DocDAE Cleanup** (Documentation hygiene) | Gemma (fast classifier), Qwen (strategist), 0102 validator | DocDAE MCP server (`foundups-mcp-p1/servers/doc_dae/server.py`) | `doc_dae_cleanup_skill_metrics.jsonl` (wardrobe telemetry) | 77, 83, 96 |
| **Rubik_Community** (Live engagement) | LiveAgent Qwen | LiveAgent MCP, Postman MCP, Sociograph MCP (planned) | Community bell-state vector | 77, 80, 96 |

> Bell-State Coupling (shared state vector): `mission_alignment`, `governance_status`, `quota_state`, `engagement_index`. Every Rubik must update these via telemetry.

---

## 4. FoundUp-Specific MCP Services (Prototype/MVP roadmap)

| Service | Layer | Status | Notes |
|---------|-------|--------|-------|
| Digital Twin MCP | Cognitive | Planned | VI 竊・AGI modeling, uses WSP 96 sentinel |
| Ethos / Personality MCP | Cognitive | Planned | Maintains persona state vectors |
| Bitcoin / Lightning MCP | Economic | Planned | DAE token sequestering, OBAI alignment |
| SmartDAO MCP | Governance | Planned | Automates threshold transitions |
| Sociograph MCP | Social | Planned | Reputation + dividend metrics |
| Guardian MCP | Ethical | Planned | Roger窶冱 Box, Zero窶典wo protocol enforcement |

These services will extend the master manifest once the foundational Rubiks are stable.

---

## 5. Commodity MCP Integrations (External Ecosystem)

Holo missions have identified high-value third-party servers. Apply WSP 15 sequencing to adopt:

1. Filesystem MCP *(baseline 窶・already in use)*  
2. Git MCP / GitHub MCP / GitLab MCP  
3. Docker MCP  
4. Memory Bank & Knowledge Graph MCP  
5. Postman MCP  
6. Snyk MCP  
7. Puppeteer / Playwright MCP  
8. Figma MCP  
9. Sequential Thinking MCP  
10. Database MCPs (Postgres/MySQL/SQLite)  

> **Update (2025-10-17):** modules/infrastructure/foundups_selenium/src/foundups_driver.py
> now emits structured telemetry (`init_*`, `connect_or_create_*`, `vision_analyze_*`, `post_to_x_*`) via an observer interface. Browser sessions managed by `browser_manager.py` append these events to `logs/foundups_browser_events.log`, ready for the Browser MCP gateway so Gemma 3 270M handles fast policy gating and Qwen 1.5B performs deep audits on every 0102 session.
Each adoption should be logged in the master manifest as 窶彗vailable_now窶・or 窶徘lanned窶・

---

## 6. Master Manifest & JSON (WIP)

- **Markdown:** `docs/mcp/MCP_Windsurf_Integration_Manifest.md` *(to be created)*  
- **JSON:** `docs/mcp/MCP_Windsurf_Integration_Manifest.json` *(Qwen export)*  

Both will enumerate:

```json
{
  "rubik_id": "rubik_compose",
  "governing_wsps": ["WSP_77", "WSP_80", "WSP_93"],
  "mcp_servers": [
    {
      "name": "filesystem_mcp",
      "endpoint": "mcp://local/fs",
      "tools": ["read_file", "write_file", "list_dir"],
      "gateway_policy": "policy_fs_default"
    },
    {
      "name": "git_mcp",
      "endpoint": "mcp://local/git",
      "tools": ["status", "diff", "commit"],
      "gateway_policy": "policy_git_standard"
    }
  ],
  "bell_state_hooks": ["mission_alignment", "quota_state"],
  "telemetry": ["CodeIndex_Report_Log.md", "docs/reporting/governance_archive.md"]
}
```

---

## 7. Next Steps

1. Run `python holo_index.py --search "windsurf mcp manifest plan"` 窶・gather active notes.  
2. Draft the Markdown + JSON manifest (0102 + Qwen/Gemma).  
3. Update WSP 80 + draft 96 with manifest references and JSON availability.  
4. Log the work (`ModLog.md`, `docs/mcp/README.md`).  
5. Archive legacy docs once content is merged.

---

## 8. References

- WSP 77 窶・Agent Coordination Protocol  
- WSP 80 窶・DAE Architecture (amendment pending)  
- WSP 93 窶・CodeIndex Surgical Intelligence Protocol  
- Draft WSP 96 窶・MCP Governance & Consensus  
- `docs/architecture/MCP_DAE_Integration_Architecture.md`  
- `docs/HoloIndex_MCP_ricDAE_Integration_Architecture.md`  
- `docs/MCP_DAE_Integration_Deep_Dive_0102_Enhanced.md`











