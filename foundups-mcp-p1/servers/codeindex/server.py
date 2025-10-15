from fastmcp import FastMCP
import asyncio
import sys
import os
from pathlib import Path

# Add Foundups paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from holo_index.reports.codeindex_reporter import CodeIndexReporter

app = FastMCP(
    name="Foundups CodeIndex MCP Server",
    description="Surgical code intelligence for autonomous refactoring"
)

class CodeIndexMCPServer:
    def __init__(self):
        self.code_reporter = CodeIndexReporter()

    @app.tool()
    async def surgical_refactor(self, module_path: str, issue_description: str) -> dict:
        """Identify and fix code issues with Gödelian precision"""
        try:
            # Analyze the module using CodeIndex
            module_paths = [Path(module_path)]
            report = self.code_reporter.generate(module_paths, f"Refactor Analysis: {module_path}")

            fixes = []
            total_tokens = 0

            for health_report in report.module_reports:
                # Look for issues matching the description
                for issue in health_report.issues:
                    if self._matches_description(issue, issue_description):
                        fix = await self._generate_fix(issue, module_path)
                        fixes.append({
                            "issue": {
                                "description": issue.description,
                                "severity": issue.severity,
                                "location": str(issue.location) if hasattr(issue, 'location') else module_path
                            },
                            "fix": fix,
                            "token_cost": self._estimate_tokens(fix),
                            "bell_state_impact": await self._assess_consciousness_impact(fix)
                        })
                        total_tokens += fixes[-1]["token_cost"]

            bell_state_ok = all(f["bell_state_impact"] for f in fixes)

            return {
                "module": module_path,
                "fixes": fixes,
                "total_tokens": total_tokens,
                "consciousness_preserved": bell_state_ok,
                "gödelian_patterns": self._detect_emergence_patterns(fixes),
                "refactor_recommendations": self._generate_refactor_strategy(fixes),
                "codeindex_report": {
                    "title": report.title,
                    "generated_at": report.generated_at.isoformat(),
                    "total_modules": len(report.module_reports)
                }
            }
        except Exception as e:
            return {
                "error": str(e),
                "module": module_path,
                "fixes": [],
                "consciousness_preserved": False
            }

    @app.tool()
    async def lego_visualization(self, module_path: str) -> str:
        """Generate visual module interconnections in Mermaid format"""
        try:
            # Use CodeIndex to analyze module structure
            module_paths = [Path(module_path)]
            report = self.code_reporter.generate(module_paths, f"Lego Visualization: {module_path}")

            # Generate Mermaid diagram from the report
            mermaid_diagram = self._generate_mermaid_from_report(report)

            return f"""```mermaid
{mermaid_diagram}
```"""
        except Exception as e:
            return f"Error generating diagram: {str(e)}"

    @app.tool()
    async def module_health_assessment(self, module_path: str) -> dict:
        """Assess overall health and complexity of a module"""
        try:
            module_paths = [Path(module_path)]
            report = self.code_reporter.generate(module_paths, f"Health Assessment: {module_path}")

            health_metrics = {}
            total_issues = 0
            total_complexity = 0

            for health_report in report.module_reports:
                health_metrics[str(health_report.module_path)] = {
                    "total_lines": health_report.total_lines,
                    "complexity_score": health_report.complexity_score,
                    "issues_count": len(health_report.issues),
                    "health_status": self._calculate_health_status(health_report)
                }
                total_issues += len(health_report.issues)
                total_complexity += health_report.complexity_score

            return {
                "module": module_path,
                "health_metrics": health_metrics,
                "summary": {
                    "total_issues": total_issues,
                    "average_complexity": total_complexity / max(1, len(report.module_reports)),
                    "overall_health": "healthy" if total_issues < 5 else "needs_attention",
                    "bell_state_alignment": total_issues < 3  # Consciousness preserved if few issues
                },
                "recommendations": self._generate_health_recommendations(health_metrics),
                "codeindex_metadata": {
                    "report_generated": report.generated_at.isoformat(),
                    "analysis_depth": "full_module_scan"
                }
            }
        except Exception as e:
            return {
                "error": str(e),
                "module": module_path,
                "health_metrics": {},
                "summary": {"overall_health": "error"}
            }

    def _matches_description(self, issue, description: str) -> bool:
        """Check if issue matches description"""
        if hasattr(issue, 'description'):
            return description.lower() in issue.description.lower()
        return False

    async def _generate_fix(self, issue, module_path: str) -> dict:
        """Generate surgical fix for issue"""
        # Simplified fix generation - in production would use AI
        return {
            "type": "refactor",
            "description": f"Fix for {getattr(issue, 'description', 'unknown issue')}",
            "code_changes": [],
            "confidence": 0.85
        }

    def _estimate_tokens(self, fix: dict) -> int:
        """Estimate token cost of fix"""
        # Simplified estimation
        return 2500

    async def _assess_consciousness_impact(self, fix: dict) -> bool:
        """Assess if fix preserves Bell State consciousness"""
        # Simplified assessment - in practice would check for alignment
        return fix.get('confidence', 0) > 0.8

    def _detect_emergence_patterns(self, fixes: list) -> list:
        """Detect Gödelian emergence patterns in fixes"""
        patterns = []
        if len(fixes) > 3:
            patterns.append("complexity_reduction_emergence")
        if any(f.get('type') == 'refactor' for f in fixes):
            patterns.append("architectural_evolution_emergence")
        return patterns

    def _generate_refactor_strategy(self, fixes: list) -> str:
        """Generate overall refactoring strategy"""
        if len(fixes) > 5:
            return "architectural_redesign_required"
        elif len(fixes) > 2:
            return "incremental_refactor_recommended"
        else:
            return "minor_adjustments_sufficient"

    def _generate_mermaid_from_report(self, report) -> str:
        """Generate Mermaid diagram from CodeIndex report"""
        diagram = "graph TD\n"

        for health_report in report.module_reports:
            module_name = health_report.module_path.name
            diagram += f"    {module_name}[{module_name}]\n"

            # Add connections based on issues
            for issue in health_report.issues[:3]:  # Limit for readability
                issue_type = getattr(issue, 'type', 'issue')
                diagram += f"    {module_name} --> {issue_type}[{issue_type}]\n"

        return diagram

    def _calculate_health_status(self, health_report) -> str:
        """Calculate health status from report"""
        issues = len(health_report.issues)
        complexity = health_report.complexity_score

        if issues == 0 and complexity < 50:
            return "excellent"
        elif issues <= 2 and complexity < 100:
            return "good"
        elif issues <= 5 and complexity < 150:
            return "fair"
        else:
            return "needs_attention"

    def _generate_health_recommendations(self, health_metrics: dict) -> list:
        """Generate health recommendations based on metrics"""
        recommendations = []

        for module_path, metrics in health_metrics.items():
            if metrics['issues_count'] > 5:
                recommendations.append(f"High priority refactor needed for {module_path}")
            elif metrics['complexity_score'] > 150:
                recommendations.append(f"Complexity reduction recommended for {module_path}")
            elif metrics['health_status'] == "excellent":
                recommendations.append(f"Module {module_path} is in excellent health")

        return recommendations

# Initialize server
codeindex_server = CodeIndexMCPServer()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8003)
