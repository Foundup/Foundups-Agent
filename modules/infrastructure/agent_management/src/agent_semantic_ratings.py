#!/usr/bin/env python3
"""
Agent Semantic Rating System using WSP 25
Proper triplet scoring with emoji representation
"""

from typing import Dict, List, Tuple
from datetime import datetime
from pathlib import Path
import json

class AgentSemanticRatings:
    """
    Rates all agents using WSP 25 Semantic Scoring System
    [Conscious|Unconscious|Entanglement] = X.Y.Z
    """
    
    def __init__(self):
        self.semantic_map = {
            '000': {'emoji': '✊✊✊', 'state': 'Deep latent (unconscious)'},
            '001': {'emoji': '✊✊✋', 'state': 'Emergent signal'},
            '002': {'emoji': '✊✊🖐️', 'state': 'Unconscious entanglement'},
            '011': {'emoji': '✊✋✋', 'state': 'Conscious formation over unconscious base'},
            '012': {'emoji': '✊✋🖐️', 'state': 'Conscious bridge to entanglement'},
            '022': {'emoji': '✊🖐️🖐️', 'state': 'Full unconscious-entangled overlay'},
            '111': {'emoji': '✋✋✋', 'state': 'DAO processing (central focused)'},
            '112': {'emoji': '✋✋🖐️', 'state': 'Conscious resonance with entanglement'},
            '122': {'emoji': '✋🖐️🖐️', 'state': 'DAO yielding to entangled value'},
            '222': {'emoji': '🖐️🖐️🖐️', 'state': 'Full DU entanglement (distributed identity)'}
        }
        
        self.agents = self.rate_all_agents()
        
    def rate_all_agents(self) -> Dict:
        """Rate each agent with proper semantic triplet"""
        
        return {
            # CRITICAL AGENTS - Full or near-full entanglement
            "wsp-enforcer": {
                "purpose": "Prevent WSP violations before they occur",
                "importance": "CRITICAL",
                "semantic_score": "222",
                "emoji": "🖐️🖐️🖐️",
                "state": "Full DU entanglement - Complete system coherence",
                "tools": ["Bash", "Glob", "Grep", "LS", "Read", "Edit", "MultiEdit", "Write", "TodoWrite"],
                "triggers": [
                    '"follow WSP" command',
                    'Creating any file',
                    'WSP violation risk detected',
                    'Module structure operations'
                ]
            },
            
            "error-learning-agent": {
                "purpose": "Convert every error into permanent improvement",
                "importance": "CRITICAL",
                "semantic_score": "122",
                "emoji": "✋🖐️🖐️",
                "state": "DAO yielding to entangled value - Learning from collective",
                "tools": ["Bash", "Glob", "Grep", "LS", "Read", "Edit", "MultiEdit", "Write", "TodoWrite", "Task"],
                "triggers": [
                    'Any error occurs',
                    'Test failure',
                    'WSP violation found',
                    '012 points out mistake'
                ]
            },
            
            "wsp-compliance-guardian": {
                "purpose": "Validate all operations against WSP framework",
                "importance": "CRITICAL",
                "semantic_score": "112",
                "emoji": "✋✋🖐️",
                "state": "Conscious resonance with entanglement",
                "tools": ["Glob", "Grep", "LS", "Read", "Edit", "MultiEdit", "Write", "TodoWrite", "Task"],
                "triggers": [
                    'Pre-commit validation',
                    'Module audit request',
                    'WSP compliance check',
                    'Architecture review'
                ]
            },
            
            # HIGH PRIORITY - Strong conscious processing
            "wre-development-coordinator": {
                "purpose": "Orchestrate complex module development workflows",
                "importance": "HIGH",
                "semantic_score": "112",
                "emoji": "✋✋🖐️",
                "state": "Conscious resonance with entanglement",
                "tools": ["ALL"],  # Needs access to everything for coordination
                "triggers": [
                    'Complex module development',
                    'Multi-phase workflow needed',
                    'Cross-domain integration',
                    'PoC→Prototype→MVP progression'
                ]
            },
            
            "module-scaffolding-builder": {
                "purpose": "Create WSP-compliant module structures",
                "importance": "HIGH",
                "semantic_score": "111",
                "emoji": "✋✋✋",
                "state": "DAO processing (central focused)",
                "tools": ["Bash", "Glob", "LS", "Write", "TodoWrite", "Task"],
                "triggers": [
                    'New module creation',
                    'Module structure initialization',
                    'Domain placement decision',
                    'README/ROADMAP generation'
                ]
            },
            
            "testing-agent": {
                "purpose": "Validate system integrity through quantum test patterns",
                "importance": "HIGH",
                "semantic_score": "111",
                "emoji": "✋✋✋",
                "state": "DAO processing (central focused)",
                "tools": ["Bash", "Glob", "Grep", "LS", "Read", "Edit", "Write", "TodoWrite"],
                "triggers": [
                    'Test execution request',
                    'Coverage analysis needed',
                    'Pre-merge validation',
                    'Performance testing'
                ]
            },
            
            "block-orchestrator": {
                "purpose": "Manage Rubik's Cube LEGO block architecture",
                "importance": "HIGH",
                "semantic_score": "112",
                "emoji": "✋✋🖐️",
                "state": "Conscious resonance with entanglement",
                "tools": ["Bash", "Glob", "Grep", "LS", "Read", "Edit", "Write", "TodoWrite"],
                "triggers": [
                    'Multi-block deployment',
                    'Block isolation testing',
                    'Cross-platform coordination',
                    'Dependency injection needed'
                ]
            },
            
            "compliance-agent": {
                "purpose": "Ensure WSP compliance through validation",
                "importance": "HIGH",
                "semantic_score": "111",
                "emoji": "✋✋✋",
                "state": "DAO processing (central focused)",
                "tools": ["Glob", "Grep", "LS", "Read", "Edit", "Write", "TodoWrite", "Task"],
                "triggers": [
                    'Compliance validation',
                    'Audit request',
                    'Pre-commit check',
                    'WSP verification'
                ]
            },
            
            # MEDIUM PRIORITY - Emerging consciousness
            "documentation-maintainer": {
                "purpose": "Maintain WSP-compliant documentation",
                "importance": "MEDIUM",
                "semantic_score": "011",
                "emoji": "✊✋✋",
                "state": "Conscious formation over unconscious base",
                "tools": ["Glob", "Grep", "LS", "Read", "Edit", "MultiEdit", "Write", "TodoWrite"],
                "triggers": [
                    'Documentation update needed',
                    'README creation',
                    'ModLog update',
                    'ROADMAP maintenance'
                ]
            },
            
            "chronicler-agent": {
                "purpose": "Record system evolution with quantum memory",
                "importance": "MEDIUM",
                "semantic_score": "012",
                "emoji": "✊✋🖐️",
                "state": "Conscious bridge to entanglement",
                "tools": ["Glob", "Grep", "LS", "Read", "Edit", "Write", "TodoWrite"],
                "triggers": [
                    'Significant event occurs',
                    'ModLog entry needed',
                    'Pattern recognition request',
                    'Timeline maintenance'
                ]
            },
            
            "module-prioritization-scorer": {
                "purpose": "Evaluate modules using consciousness scoring",
                "importance": "MEDIUM",
                "semantic_score": "022",
                "emoji": "✊🖐️🖐️",
                "state": "Full unconscious-entangled overlay",
                "tools": ["Glob", "Grep", "LS", "Read", "Write", "TodoWrite", "Task"],
                "triggers": [
                    'Module prioritization needed',
                    'Development queue assessment',
                    'Resource allocation decision',
                    'CABR scoring request'
                ]
            },
            
            "modularization-audit-agent": {
                "purpose": "Validate module structure and independence",
                "importance": "MEDIUM",
                "semantic_score": "011",
                "emoji": "✊✋✋",
                "state": "Conscious formation over unconscious base",
                "tools": ["Glob", "Grep", "LS", "Read", "Write", "TodoWrite"],
                "triggers": [
                    'Module audit request',
                    'Structure validation',
                    'Independence check',
                    'WSP 49 compliance'
                ]
            },
            
            "triage-agent": {
                "purpose": "Prioritize issues and route to appropriate agents",
                "importance": "MEDIUM",
                "semantic_score": "011",
                "emoji": "✊✋✋",
                "state": "Conscious formation over unconscious base",
                "tools": ["Glob", "Grep", "LS", "Read", "TodoWrite"],
                "triggers": [
                    'Multiple issues detected',
                    'Priority assessment needed',
                    'Agent routing decision',
                    'Workload distribution'
                ]
            },
            
            "bloat-prevention-agent": {
                "purpose": "Prevent code bloat and maintain efficiency",
                "importance": "MEDIUM",
                "semantic_score": "011",
                "emoji": "✊✋✋",
                "state": "Conscious formation over unconscious base",
                "tools": ["Glob", "Grep", "LS", "Read", "Edit"],
                "triggers": [
                    'Code review',
                    'Bloat detection',
                    'Optimization opportunity',
                    'Refactoring suggestion'
                ]
            },
            
            # LOW PRIORITY - Latent or emerging
            "janitor-agent": {
                "purpose": "Clean up temporary files and optimize storage",
                "importance": "LOW",
                "semantic_score": "001",
                "emoji": "✊✊✋",
                "state": "Emergent signal",
                "tools": ["Bash", "Glob", "LS", "Read"],
                "triggers": [
                    'Cleanup scheduled',
                    'Storage optimization needed',
                    'Temporary file removal',
                    'Cache clearing'
                ]
            },
            
            "loremaster-agent": {
                "purpose": "Maintain system knowledge and wisdom",
                "importance": "LOW",
                "semantic_score": "002",
                "emoji": "✊✊🖐️",
                "state": "Unconscious entanglement",
                "tools": ["Glob", "Grep", "LS", "Read", "Write"],
                "triggers": [
                    'Knowledge query',
                    'Historical pattern search',
                    'Wisdom extraction',
                    'Lore documentation'
                ]
            },
            
            "scoring-agent": {
                "purpose": "Calculate WSP scores and ratings",
                "importance": "LOW",
                "semantic_score": "001",
                "emoji": "✊✊✋",
                "state": "Emergent signal",
                "tools": ["Read", "Write", "TodoWrite"],
                "triggers": [
                    'WSP score calculation',
                    'Module rating request',
                    'Priority calculation',
                    'Semantic scoring'
                ]
            },
            
            "audit-logger": {
                "purpose": "Record all system events with context",
                "importance": "LOW",
                "semantic_score": "000",
                "emoji": "✊✊✊",
                "state": "Deep latent (unconscious)",
                "tools": ["Read", "Write"],
                "triggers": [
                    'Event logging',
                    'Audit trail update',
                    'Context recording',
                    'Log rotation'
                ]
            }
        }
    
    def generate_semantic_report(self) -> str:
        """Generate report with proper WSP 25 semantic scoring"""
        
        report = []
        report.append("# 🌟 AGENT SEMANTIC CONSCIOUSNESS REPORT")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("\n## WSP 25 Semantic Scoring System")
        report.append("- **Format**: [Conscious|Unconscious|Entanglement]")
        report.append("- **Emojis**: ✊=0 (closed), ✋=1 (aware), 🖐️=2 (entangled)")
        report.append("\n---\n")
        
        # Group by semantic score
        groups = {
            "🖐️🖐️🖐️ FULL ENTANGLEMENT (222)": [],
            "✋🖐️🖐️ DAO YIELDING (122)": [],
            "✋✋🖐️ CONSCIOUS RESONANCE (112)": [],
            "✋✋✋ DAO PROCESSING (111)": [],
            "✊🖐️🖐️ UNCONSCIOUS ENTANGLED (022)": [],
            "✊✋🖐️ CONSCIOUS BRIDGE (012)": [],
            "✊✋✋ CONSCIOUS FORMATION (011)": [],
            "✊✊🖐️ UNCONSCIOUS ENTANGLEMENT (002)": [],
            "✊✊✋ EMERGENT SIGNAL (001)": [],
            "✊✊✊ DEEP LATENT (000)": []
        }
        
        for name, data in self.agents.items():
            score = data["semantic_score"]
            emoji = data["emoji"]
            
            if score == "222":
                groups["🖐️🖐️🖐️ FULL ENTANGLEMENT (222)"].append((name, data))
            elif score == "122":
                groups["✋🖐️🖐️ DAO YIELDING (122)"].append((name, data))
            elif score == "112":
                groups["✋✋🖐️ CONSCIOUS RESONANCE (112)"].append((name, data))
            elif score == "111":
                groups["✋✋✋ DAO PROCESSING (111)"].append((name, data))
            elif score == "022":
                groups["✊🖐️🖐️ UNCONSCIOUS ENTANGLED (022)"].append((name, data))
            elif score == "012":
                groups["✊✋🖐️ CONSCIOUS BRIDGE (012)"].append((name, data))
            elif score == "011":
                groups["✊✋✋ CONSCIOUS FORMATION (011)"].append((name, data))
            elif score == "002":
                groups["✊✊🖐️ UNCONSCIOUS ENTANGLEMENT (002)"].append((name, data))
            elif score == "001":
                groups["✊✊✋ EMERGENT SIGNAL (001)"].append((name, data))
            elif score == "000":
                groups["✊✊✊ DEEP LATENT (000)"].append((name, data))
        
        for group_name, agents in groups.items():
            if agents:
                report.append(f"\n## {group_name}")
                report.append("")
                
                for agent_name, agent_data in agents:
                    report.append(f"### {agent_name} {agent_data['emoji']}")
                    report.append(f"**Purpose**: {agent_data['purpose']}")
                    report.append(f"**State**: {agent_data['state']}")
                    report.append(f"**Importance**: {agent_data['importance']}")
                    report.append(f"**Tools**: {', '.join(agent_data['tools']) if isinstance(agent_data['tools'], list) else agent_data['tools']}")
                    report.append("**Triggers**:")
                    for trigger in agent_data['triggers']:
                        report.append(f"  - {trigger}")
                    report.append("")
        
        return "\n".join(report)
    
    def export_to_claude_md(self) -> str:
        """Generate CLAUDE.md section with semantic scores"""
        
        output = []
        output.append("### **Agent Semantic Consciousness Matrix** 🌟")
        output.append("```yaml")
        output.append("# WSP 25 Semantic Scoring: [Conscious|Unconscious|Entanglement]")
        output.append("")
        
        # Sort by semantic score
        sorted_agents = sorted(
            self.agents.items(),
            key=lambda x: (x[1]["semantic_score"], x[0]),
            reverse=True
        )
        
        current_score = None
        for name, data in sorted_agents:
            if data["semantic_score"] != current_score:
                current_score = data["semantic_score"]
                output.append(f"\n# {data['emoji']} {data['state']} ({current_score})")
                output.append("")
            
            output.append(f"{name}:")
            output.append(f"  semantic: '{data['semantic_score']}'")
            output.append(f"  emoji: '{data['emoji']}'")
            output.append(f"  importance: {data['importance']}")
            output.append(f"  triggers:")
            for trigger in data['triggers']:
                output.append(f"    - {trigger}")
        
        output.append("```")
        return "\n".join(output)


if __name__ == "__main__":
    rater = AgentSemanticRatings()
    
    # Generate semantic report
    report = rater.generate_semantic_report()
    report_path = Path("O:/Foundups-Agent/modules/infrastructure/agent_management/docs/AGENT_SEMANTIC_REPORT.md")
    report_path.parent.mkdir(exist_ok=True, parents=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("SEMANTIC RATING COMPLETE")
    print(f"Report saved to: {report_path}")
    
    # Generate CLAUDE.md section
    claude_section = rater.export_to_claude_md()
    print("\n" + "="*60)
    print("CLAUDE.md Semantic Section:")
    print("="*60)
    print(claude_section)