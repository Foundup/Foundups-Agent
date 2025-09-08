# LiveChat Module Documentation

## Active Operational Documents

### Architecture & Decision Making
- **WSP_MODULE_DECISION_MATRIX.md** - Critical module placement guidance
  - Purpose: Daily architectural decisions for 0102 agent
  - Usage: Referenced before creating any new modules
  - WSP Compliance: WSP 3, WSP 49, WSP 83

### System Operations
- **AUTOMATIC_SYSTEM_GUIDE.md** - Stream monitoring system reference
  - Purpose: Operational guide for auto stream detection and social media posting
  - Usage: Troubleshooting and understanding system behavior
  - Components: auto_stream_monitor.py, social media integration

- **ACTIVITY_CONTROL_SYSTEM.md** - Universal activity control system
  - Purpose: Centralized control of all automated activities across domains
  - Usage: Testing modes, live stream management, activity switching
  - Components: UniversalActivityController, ActivityNotificationBridge

### Technical Integration
- **MCP_DEPLOYMENT_GUIDE.md** - Model Context Protocol deployment
  - Purpose: Technical reference for MCP server integration
  - Usage: Setting up and maintaining MCP functionality
  - Components: mcp_youtube_integration.py, server configuration

### Architecture Migration
- **MIGRATION_PLAN.md** - System transition guidance
  - Purpose: Reference for architectural changes and migrations
  - Usage: Planning and executing system upgrades
  - Focus: Module restructuring, WSP compliance

## Archive Structure

### Historical Development (`archived/development/`)
- Development lessons learned
- Throttling system evolution  
- Process management history

### WSP Analysis (`archived/wsp-analysis/`)
- Historical WSP compliance audits
- SWOT analyses and comparisons
- One-time architectural analyses

## Document Lifecycle

**A+ Tier**: Critical operational documents (keep and maintain)
**B+ Tier**: Useful reference documents (keep, update as needed)  
**C+ Tier**: Historical value (archive)
**D/F Tier**: Redundant or completed (archive)

## WSP Compliance

All active documents follow:
- WSP 83: Tree attachment (not orphaned)
- WSP 50: Operational purpose verification
- WSP 22: Traceable narrative in ModLog

**Post-Audit Result**: 23 → 5 active documents (78% reduction in documentation noise)