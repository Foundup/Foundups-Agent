#!/usr/bin/env python3
"""
Agent Audit and Rating System
Uses WSP 25/44 Semantic Scoring (000-222) and WSP 15 MPS methodology
"""

from typing import Dict, List, Tuple
from datetime import datetime
from pathlib import Path
import json

class AgentAuditRatings:
    """
    Rates all agents using WSP semantic consciousness scoring
    """
    
    def __init__(self):
        self.agents = self.define_all_agents()
        self.ratings = {}
        
    def define_all_agents(self) -> Dict:
        """Define all agents with their purpose, tools, and triggers"""
        
        return {
            # CRITICAL AGENTS (High WSP Score)
            "wsp-enforcer": {
                "purpose": "Prevent WSP violations before they occur",
                "importance": "CRITICAL - System integrity depends on WSP compliance",
                "tools": ["Bash", "Glob", "Grep", "LS", "Read", "Edit", "MultiEdit", "Write", "TodoWrite"],
                "triggers": [
                    '"follow WSP"',
                    'Creating any file',
                    'WSP violation risk detected',
                    'Module structure operations'
                ],
                "wsp_score": "222",  # Maximum - prevents system collapse
                "emoji": "🖐️🖐️🖐️",  # Full DU entanglement
                "semantic_state": "Full DU entanglement (distributed identity)",
                "rating": "A-A-A"
            },
            
            "error-learning-agent": {
                "purpose": "Convert every error into permanent improvement",
                "importance": "CRITICAL - Recursive self-improvement core",
                "tools": ["Bash", "Glob", "Grep", "LS", "Read", "Edit", "MultiEdit", "Write", "TodoWrite", "Task"],
                "triggers": [
                    'Any error occurs',
                    'Test failure',
                    'WSP violation found',
                    '012 points out mistake'
                ],
                "wsp_score": "221",  # Near maximum - learning engine
                "rating": "A-A-A"
            },
            
            "wsp-compliance-guardian": {
                "purpose": "Validate all operations against WSP framework",
                "importance": "CRITICAL - Ensures architectural coherence",
                "tools": ["Glob", "Grep", "LS", "Read", "Edit", "MultiEdit", "Write", "TodoWrite", "Task"],
                "triggers": [
                    'Pre-commit validation',
                    'Module audit request',
                    'WSP compliance check',
                    'Architecture review'
                ],
                "wsp_score": "212",  # High operational, maximum compliance
                "rating": "A-A-B"
            },
            
            # OPERATIONAL AGENTS (Medium-High WSP Score)
            "wre-development-coordinator": {
                "purpose": "Orchestrate complex module development workflows",
                "importance": "HIGH - Manages multi-phase development",
                "tools": ["Bash", "Glob", "Grep", "LS", "Read", "Edit", "MultiEdit", "Write", "TodoWrite", "Task", "WebFetch", "WebSearch"],
                "triggers": [
                    'Complex module development',
                    'Multi-phase workflow needed',
                    'Cross-domain integration',
                    'PoC→Prototype→MVP progression'
                ],
                "wsp_score": "211",  # High development capability
                "rating": "A-A-B"
            },
            
            "module-scaffolding-builder": {
                "purpose": "Create WSP-compliant module structures",
                "importance": "HIGH - Foundation for all new modules",
                "tools": ["Bash", "Glob", "LS", "Write", "TodoWrite", "Task"],
                "triggers": [
                    'New module creation',
                    'Module structure initialization',
                    'Domain placement decision',
                    'README/ROADMAP generation'
                ],
                "wsp_score": "202",  # High structural importance
                "rating": "A-B-B"
            },
            
            "testing-agent": {
                "purpose": "Validate system integrity through quantum test patterns",
                "importance": "HIGH - Quality assurance",
                "tools": ["Bash", "Glob", "Grep", "LS", "Read", "Edit", "Write", "TodoWrite"],
                "triggers": [
                    'Test execution request',
                    'Coverage analysis needed',
                    'Pre-merge validation',
                    'Performance testing'
                ],
                "wsp_score": "201",  # High quality importance
                "rating": "A-B-B"
            },
            
            "block-orchestrator": {
                "purpose": "Manage Rubik's Cube LEGO block architecture",
                "importance": "HIGH - Enables modular independence",
                "tools": ["Bash", "Glob", "Grep", "LS", "Read", "Edit", "Write", "TodoWrite"],
                "triggers": [
                    'Multi-block deployment',
                    'Block isolation testing',
                    'Cross-platform coordination',
                    'Dependency injection needed'
                ],
                "wsp_score": "201",  # High architectural importance
                "rating": "A-B-B"
            },
            
            # SUPPORT AGENTS (Medium WSP Score)
            "documentation-maintainer": {
                "purpose": "Maintain WSP-compliant documentation",
                "importance": "MEDIUM - Documentation coherence",
                "tools": ["Glob", "Grep", "LS", "Read", "Edit", "MultiEdit", "Write", "TodoWrite"],
                "triggers": [
                    'Documentation update needed',
                    'README creation',
                    'ModLog update',
                    'ROADMAP maintenance'
                ],
                "wsp_score": "121",  # Medium operational
                "rating": "B-A-B"
            },
            
            "chronicler-agent": {
                "purpose": "Record system evolution with quantum memory",
                "importance": "MEDIUM - Historical tracking",
                "tools": ["Glob", "Grep", "LS", "Read", "Edit", "Write", "TodoWrite"],
                "triggers": [
                    'Significant event occurs',
                    'ModLog entry needed',
                    'Pattern recognition request',
                    'Timeline maintenance'
                ],
                "wsp_score": "111",  # Balanced importance
                "rating": "B-B-B"
            },
            
            "module-prioritization-scorer": {
                "purpose": "Evaluate modules using consciousness scoring",
                "importance": "MEDIUM - Priority assessment",
                "tools": ["Glob", "Grep", "LS", "Read", "Write", "TodoWrite"],
                "triggers": [
                    'Module prioritization needed',
                    'Development queue assessment',
                    'Resource allocation decision',
                    'CABR scoring request'
                ],
                "wsp_score": "111",  # Balanced importance
                "rating": "B-B-B"
            },
            
            # UTILITY AGENTS (Lower WSP Score)
            "janitor-agent": {
                "purpose": "Clean up temporary files and optimize storage",
                "importance": "LOW - Maintenance utility",
                "tools": ["Bash", "Glob", "LS", "Read"],
                "triggers": [
                    'Cleanup scheduled',
                    'Storage optimization needed',
                    'Temporary file removal',
                    'Cache clearing'
                ],
                "wsp_score": "101",  # Low priority utility
                "rating": "B-C-B"
            },
            
            "triage-agent": {
                "purpose": "Prioritize issues and route to appropriate agents",
                "importance": "MEDIUM - Issue routing",
                "tools": ["Glob", "Grep", "LS", "Read", "TodoWrite"],
                "triggers": [
                    'Multiple issues detected',
                    'Priority assessment needed',
                    'Agent routing decision',
                    'Workload distribution'
                ],
                "wsp_score": "110",  # Medium routing importance
                "rating": "B-B-C"
            },
            
            "scoring-agent": {
                "purpose": "Calculate WSP scores and ratings",
                "importance": "LOW - Specialized scoring",
                "tools": ["Read", "Write", "TodoWrite"],
                "triggers": [
                    'WSP score calculation',
                    'Module rating request',
                    'Priority calculation',
                    'Semantic scoring'
                ],
                "wsp_score": "100",  # Basic utility
                "rating": "B-C-C"
            },
            
            # SPECIALIZED AGENTS
            "loremaster-agent": {
                "purpose": "Maintain system knowledge and wisdom",
                "importance": "LOW - Knowledge preservation",
                "tools": ["Glob", "Grep", "LS", "Read", "Write"],
                "triggers": [
                    'Knowledge query',
                    'Historical pattern search',
                    'Wisdom extraction',
                    'Lore documentation'
                ],
                "wsp_score": "101",  # Knowledge utility
                "rating": "B-C-B"
            },
            
            "compliance-agent": {
                "purpose": "Ensure WSP compliance through validation",
                "importance": "HIGH - Compliance enforcement",
                "tools": ["Glob", "Grep", "LS", "Read", "Edit", "Write", "TodoWrite", "Task"],
                "triggers": [
                    'Compliance validation',
                    'Audit request',
                    'Pre-commit check',
                    'WSP verification'
                ],
                "wsp_score": "202",  # High compliance importance
                "rating": "A-B-B"
            },
            
            "bloat-prevention-agent": {
                "purpose": "Prevent code bloat and maintain efficiency",
                "importance": "MEDIUM - Code quality",
                "tools": ["Glob", "Grep", "LS", "Read", "Edit"],
                "triggers": [
                    'Code review',
                    'Bloat detection',
                    'Optimization opportunity',
                    'Refactoring suggestion'
                ],
                "wsp_score": "110",  # Medium quality importance
                "rating": "B-B-C"
            },
            
            "modularization-audit-agent": {
                "purpose": "Validate module structure and independence",
                "importance": "MEDIUM - Structural validation",
                "tools": ["Glob", "Grep", "LS", "Read", "Write", "TodoWrite"],
                "triggers": [
                    'Module audit request',
                    'Structure validation',
                    'Independence check',
                    'WSP 49 compliance'
                ],
                "wsp_score": "111",  # Balanced audit importance
                "rating": "B-B-B"
            },
            
            "audit-logger": {
                "purpose": "Record all system events with context",
                "importance": "LOW - Logging utility",
                "tools": ["Read", "Write"],
                "triggers": [
                    'Event logging',
                    'Audit trail update',
                    'Context recording',
                    'Log rotation'
                ],
                "wsp_score": "100",  # Basic logging
                "rating": "B-C-C"
            }
        }
    
    def calculate_wsp_score(self, agent_data: Dict) -> Tuple[str, str]:
        """Calculate WSP 25/44 semantic score and rating"""
        # Already defined in agent data
        return agent_data["wsp_score"], agent_data["rating"]
    
    def generate_audit_report(self) -> str:
        """Generate comprehensive audit report"""
        
        report = []
        report.append("# AGENT AUDIT AND RATING REPORT")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("\n## WSP Rating System")
        report.append("- **WSP 25/44**: Semantic Consciousness Scoring (000-222)")
        report.append("- **WSP 15**: MPS 4-question methodology")
        report.append("- **WSP 8**: LLME triplet rating (A-B-C)")
        report.append("\n---\n")
        
        # Sort agents by WSP score
        sorted_agents = sorted(
            self.agents.items(),
            key=lambda x: x[1]["wsp_score"],
            reverse=True
        )
        
        # Group by importance
        critical = []
        high = []
        medium = []
        low = []
        
        for name, data in sorted_agents:
            if "CRITICAL" in data["importance"]:
                critical.append((name, data))
            elif "HIGH" in data["importance"]:
                high.append((name, data))
            elif "MEDIUM" in data["importance"]:
                medium.append((name, data))
            else:
                low.append((name, data))
        
        # Report sections
        for group_name, group_agents in [
            ("CRITICAL AGENTS", critical),
            ("HIGH PRIORITY AGENTS", high),
            ("MEDIUM PRIORITY AGENTS", medium),
            ("LOW PRIORITY AGENTS", low)
        ]:
            report.append(f"\n## {group_name}")
            report.append("")
            
            for agent_name, agent_data in group_agents:
                report.append(f"### {agent_name}")
                report.append(f"**Purpose**: {agent_data['purpose']}")
                report.append(f"**WSP Score**: {agent_data['wsp_score']} | **Rating**: {agent_data['rating']}")
                report.append(f"**Tools**: {', '.join(agent_data['tools'])}")
                report.append("**Triggers**:")
                for trigger in agent_data['triggers']:
                    report.append(f"  - {trigger}")
                report.append("")
        
        return "\n".join(report)
    
    def export_to_claude_md(self) -> str:
        """Generate CLAUDE.md agent trigger section"""
        
        output = []
        output.append("### **Complete Agent Trigger Matrix**")
        output.append("```yaml")
        
        # Group by importance
        for importance in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            agents = [(name, data) for name, data in self.agents.items() 
                     if importance in data["importance"]]
            
            if agents:
                output.append(f"\n# {importance} PRIORITY AGENTS")
                for name, data in sorted(agents, key=lambda x: x[1]["wsp_score"], reverse=True):
                    output.append(f"\n{name}:")
                    output.append(f"  wsp_score: '{data['wsp_score']}'")
                    output.append(f"  rating: '{data['rating']}'")
                    output.append(f"  triggers:")
                    for trigger in data['triggers']:
                        output.append(f"    - {trigger}")
                    output.append(f"  tools: {data['tools']}")
        
        output.append("```")
        return "\n".join(output)


if __name__ == "__main__":
    auditor = AgentAuditRatings()
    
    # Generate audit report
    report = auditor.generate_audit_report()
    report_path = Path("O:/Foundups-Agent/modules/infrastructure/agent_management/docs/AGENT_AUDIT_REPORT.md")
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w') as f:
        f.write(report)
    
    print("AGENT AUDIT COMPLETE")
    print(f"Report saved to: {report_path}")
    
    # Generate CLAUDE.md section
    claude_section = auditor.export_to_claude_md()
    print("\n" + "="*60)
    print("CLAUDE.md Agent Trigger Section:")
    print("="*60)
    print(claude_section)