import json
from typing import Dict, List, Any, Optional

class MissionCoordinator:
    """
    Coordinates specialized missions for HoloDAE.
    - MCP Adoption
    - Orphan Archaeology
    - WSP Documentation Guardianship
    """

    def __init__(self, agent_type: str = "0102"):
        self.agent_type = agent_type

    def coordinate_mcp_adoption_mission(self, query: str) -> Optional[str]:
        """
        FIRST PRINCIPLES: HoloIndex MCP adoption status checker
        """
        query_lower = query.lower()

        # Detect MCP adoption status queries
        if not any(phrase in query_lower for phrase in [
            'mcp adoption status', 'rubik provisioning', 'mcp rubik status',
            'windsurf mcp status', 'mcp integration status'
        ]):
            return None

        # Load MCP manifest for status checking
        try:
            with open('docs/mcp/MCP_Windsurf_Integration_Manifest.json', 'r', encoding='utf-8') as f:
                manifest = json.load(f)
        except FileNotFoundError:
            return "[FAIL] MCP manifest not found. Run MCP manifest creation first."
        except UnicodeDecodeError:
            return "[FAIL] MCP manifest encoding error. Please regenerate the manifest."

        # Generate agent-aware status report
        if self.agent_type == "qwen":
            return self._generate_qwen_mcp_status(manifest)
        elif self.agent_type == "gemma":
            return self._generate_gemma_mcp_status(manifest)
        else:
            return self._generate_0102_mcp_status(manifest)

    def coordinate_orphan_archaeology_mission(self, query: str) -> Optional[str]:
        """
        FIRST PRINCIPLES: HoloIndex as multi-agent coordinator for orphan archaeology
        """
        query_lower = query.lower()

        # Detect orphan archaeology mission
        if not any(word in query_lower for word in ['orphan', '464', 'archaeology', 'cleanup']):
            return None  # Not orphan archaeology

        # FIRST PRINCIPLES: Use existing data structures
        try:
            with open('docs/Orphan_Complete_Dataset.json', 'r') as f:
                dataset = json.load(f)
                orphan_dataset = {orphan['relative_path']: orphan for orphan in dataset.get('orphans', [])}
        except FileNotFoundError:
            return "[FAIL] Orphan dataset not found. Run orphan analysis preparation first."
        except json.JSONDecodeError:
            return "[FAIL] Orphan dataset corrupted. Regenerate from orphan analysis."

        analyzed_count = self._count_analyzed_orphans()

        # Agent-aware coordination output
        if self.agent_type == "qwen":
            return self._generate_qwen_orphan_coordination(orphan_dataset, analyzed_count)
        elif self.agent_type == "gemma":
            return self._generate_gemma_orphan_coordination(orphan_dataset, analyzed_count)
        else:
            # 0102 gets strategic overview and delegation plan
            return self._generate_0102_orphan_coordination(orphan_dataset, analyzed_count)

    def _generate_qwen_mcp_status(self, manifest: Dict) -> str:
        """Qwen gets structured MCP status for planning."""
        status_summary = {
            "phase": manifest["manifest"]["phase"],
            "rubik_status": {},
            "mcp_availability": {},
            "coordination_readiness": "ready_for_implementation"
        }

        for rubik_name, rubik_data in manifest["rubik_cubes"].items():
            rubik_status = {
                "mcp_servers": len(rubik_data["mcp_servers"]),
                "available_now": sum(1 for mcp in rubik_data["mcp_servers"].values()
                                   if mcp["status"] == "available_now"),
                "planned": sum(1 for mcp in rubik_data["mcp_servers"].values()
                             if mcp["status"] == "planned"),
                "research": sum(1 for mcp in rubik_data["mcp_servers"].values()
                              if mcp["status"] == "research")
            }
            status_summary["rubik_status"][rubik_name] = rubik_status

        # MCP availability summary
        all_mcp = {}
        for rubik_data in manifest["rubik_cubes"].values():
            for mcp_name, mcp_data in rubik_data["mcp_servers"].items():
                if mcp_name not in all_mcp:
                    all_mcp[mcp_name] = {"status": mcp_data["status"], "used_by": []}
                all_mcp[mcp_name]["used_by"].append(rubik_data["purpose"][:20])

        status_summary["mcp_availability"] = all_mcp

        return json.dumps(status_summary, indent=2)

    def _generate_gemma_mcp_status(self, manifest: Dict) -> str:
        """Gemma gets binary status validations."""
        # Count available MCPs
        available_count = 0
        planned_count = 0
        research_count = 0

        for rubik_data in manifest["rubik_cubes"].values():
            for mcp_data in rubik_data["mcp_servers"].values():
                if mcp_data["status"] == "available_now":
                    available_count += 1
                elif mcp_data["status"] == "planned":
                    planned_count += 1
                elif mcp_data["status"] == "research":
                    research_count += 1

        return f"MCP_STATUS|available:{available_count}|planned:{planned_count}|research:{research_count}|phase_0_1_ready"

    def _generate_0102_mcp_status(self, manifest: Dict) -> str:
        """0102 gets strategic MCP adoption overview."""
        phase = manifest["manifest"]["phase"]

        # Calculate overall readiness
        total_mcp = 0
        available_mcp = 0

        for rubik_data in manifest["rubik_cubes"].values():
            for mcp_data in rubik_data["mcp_servers"].values():
                total_mcp += 1
                if mcp_data["status"] == "available_now":
                    available_mcp += 1

        readiness_percentage = (available_mcp / total_mcp) * 100 if total_mcp > 0 else 0

        strategic_status = f"""
# 🏗️ WINDSURF MCP ADOPTION STATUS

## [DATA] Current Phase: {phase}
## [TARGET] Overall Readiness: {readiness_percentage:.1f}% ({available_mcp}/{total_mcp} MCP servers available)

## 🧩 Foundational Rubik Status

"""

        for rubik_name, rubik_data in manifest["rubik_cubes"].items():
            rubik_title = rubik_name.replace('_', ' ').title()
            purpose = rubik_data["purpose"]
            mcp_count = len(rubik_data["mcp_servers"])
            available = sum(1 for mcp in rubik_data["mcp_servers"].values()
                          if mcp["status"] == "available_now")

            strategic_status += f"""
### {rubik_title}
**Purpose**: {purpose}
**MCP Servers**: {available}/{mcp_count} available
**Status**: {'🟢 READY' if available == mcp_count else '🟡 PARTIAL' if available > 0 else '🔴 PENDING'}
"""

            # List available MCPs
            available_mcps = [name.replace('_', ' ').title()
                            for name, data in rubik_data["mcp_servers"].items()
                            if data["status"] == "available_now"]
            if available_mcps:
                strategic_status += f"**Available**: {', '.join(available_mcps)}\n"

        strategic_status += f"""

## 🚀 Next Steps

1. **Complete Phase 0.1**: Integrate remaining available MCP servers
2. **Phase 0.2 Planning**: Begin GitHub/E2B MCP integration
3. **Monitor Coordination**: Ensure WSP 77 agent coordination working
4. **Validate Bell States**: Confirm φ²-φ⁵ entanglement across Rubiks

## ⚡ Immediate Actions Required

- [ ] Verify Filesystem MCP integration in all Rubiks
- [ ] Confirm Git MCP version control operations
- [ ] Test Docker MCP build capabilities
- [ ] Validate Memory Bank MCP persistence

## 🔗 References

- **Manifest**: docs/mcp/MCP_Windsurf_Integration_Manifest.md
- **JSON Data**: docs/mcp/MCP_Windsurf_Integration_Manifest.json
- **WSP 77**: Agent Coordination Protocol
- **WSP 80**: Cube-Level DAE Orchestration

**Status**: {'🟢 PHASE 0.1 ACTIVE' if readiness_percentage >= 50 else '🟡 INITIALIZING'}
**HoloIndex**: 🟢 COORDINATOR MODE ACTIVE
"""

        return strategic_status.strip()

    def _count_analyzed_orphans(self) -> int:
        """Count how many orphans have been analyzed so far."""
        analysis_files = [
            'docs/Qwen_Orphan_Analysis_Complete.json',
            'docs/Gemma_Similarity_Matrix.json'
        ]
        count = 0
        for file_path in analysis_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    count += len(data)
            except (FileNotFoundError, json.JSONDecodeError):
                continue
        return count

    def _generate_qwen_orphan_coordination(self, orphan_dataset: Dict, analyzed_count: int) -> str:
        """Generate Qwen-specific coordination output with batch processing plan."""
        total_orphans = len(orphan_dataset)
        batch_size = 50
        remaining = total_orphans - analyzed_count
        batches_needed = (remaining + batch_size - 1) // batch_size

        # Prepare next batch for Qwen processing
        unanalyzed = [oid for oid in orphan_dataset.keys() if oid not in self._get_analyzed_orphan_ids()]
        next_batch = unanalyzed[:batch_size]

        coordination = {
            "mission": "ORPHAN_ARCHAEOLOGY_PHASE_1",
            "status": f"{analyzed_count}/{total_orphans} analyzed",
            "next_batch": next_batch,
            "batch_size": len(next_batch),
            "remaining_batches": max(0, batches_needed - 1),
            "tasks": [
                "read_file_content_first_100_lines",
                "parse_imports_ast_based",
                "identify_code_purpose_from_docstrings",
                "categorize_integrate_archive_delete_standalone",
                "assign_cluster_id_if_applicable"
            ],
            "output_format": "structured_json_per_orphan",
            "coordination_guidance": "Focus on batch processing efficiency. Gemma will handle similarity analysis after your categorization."
        }

        return json.dumps(coordination, indent=2)

    def _generate_gemma_orphan_coordination(self, orphan_dataset: Dict, analyzed_count: int) -> str:
        """Generate Gemma-specific coordination output with specialized tasks."""
        pending_similarity = self._get_orphans_needing_similarity_analysis()

        coordination = {
            "mission": "ORPHAN_ARCHAEOLOGY_SIMILARITY_ANALYSIS",
            "pending_tasks": len(pending_similarity),
            "specialization": "FAST_SIMILARITY_ANALYSIS",
            "next_task": pending_similarity[:10] if pending_similarity else [],
            "method": "ast_based_similarity_scoring",
            "output_format": "binary_duplicate_unique_classification",
            "parallel_capable": True
        }

        return json.dumps(coordination, indent=2)

    def _generate_0102_orphan_coordination(self, orphan_dataset: Dict, analyzed_count: int) -> str:
        """Generate 0102 strategic overview with delegation plan."""
        total_orphans = len(orphan_dataset)
        progress_percentage = (analyzed_count / total_orphans) * 100 if total_orphans > 0 else 0

        strategic_overview = f"""
# 🏛️ ORPHAN ARCHAEOLOGY MISSION COORDINATION

## [DATA] Mission Status
- **Total Orphans**: {total_orphans}
- **Analyzed**: {analyzed_count} ({progress_percentage:.1f}%)
- **Remaining**: {total_orphans - analyzed_count}

## [TARGET] Agent Delegation Strategy

### Qwen (Coordination & Categorization)
- **Role**: Batch analysis of 50 orphans at a time
- **Tasks**: Purpose identification, import analysis, categorization
- **Output**: Structured JSON per orphan
- **Status**: Ready for next batch

### Gemma (Similarity Analysis)
- **Role**: Fast AST-based similarity scoring
- **Tasks**: Duplicate detection, function comparison
- **Output**: Binary classifications
- **Status**: Parallel processing capable

## [ROCKET] Next Actions

1. **Dispatch Qwen**: Analyze next batch of 50 orphans
2. **Monitor Progress**: Track completion across all 464 orphans
3. **Aggregate Results**: Build integration roadmap
4. **Execute Cleanup**: Integrate/archive/delete based on analysis

## [UP] Expected Outcomes

- **Clean Codebase**: Every orphan accounted for
- **Agent Training**: Qwen/Gemma learn codebase patterns
- **Prevention**: Future vibecoding detection
- **Integration**: Valuable code properly integrated

**HoloIndex Status**: 🟢 COORDINATOR MODE ACTIVE
**Mission Control**: 0102 strategic oversight
**Execution Agents**: Qwen + Gemma specialized analysis
        """.strip()

        return strategic_overview

    def _get_analyzed_orphan_ids(self) -> set:
        """Get set of orphan IDs that have been analyzed."""
        analyzed_ids = set()
        try:
            with open('docs/Qwen_Orphan_Analysis_Complete.json', 'r') as f:
                qwen_data = json.load(f)
                analyzed_ids.update(qwen_data.keys())
        except (FileNotFoundError, json.JSONDecodeError):
            pass

        try:
            with open('docs/Gemma_Similarity_Matrix.json', 'r') as f:
                gemma_data = json.load(f)
                analyzed_ids.update(gemma_data.keys())
        except (FileNotFoundError, json.JSONDecodeError):
            pass

        return analyzed_ids

    def _get_orphans_needing_similarity_analysis(self) -> List[str]:
        """Get orphans that need similarity analysis."""
        # This would check Qwen analysis results to find orphans needing Gemma similarity scoring
        # For now, return a sample list
        return ["orphan_1", "orphan_2", "orphan_3"]  # Placeholder
