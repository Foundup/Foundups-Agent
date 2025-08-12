#!/usr/bin/env python3
"""
WSP-Compliant Agent A/B Testing System
Tests different agent combinations to find optimal recipes
Follows WSP 21 (Prometheus Recursion), WSP 48 (Recursive Improvement)
"""

import json
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class AgentType(Enum):
    """Available agent types for testing"""
    PROMETHEUS_PROMPT = "prometheus-prompt"
    WRE_COORDINATOR = "wre-development-coordinator"
    WSP_GUARDIAN = "wsp-compliance-guardian"
    BUILDER = "module-scaffolding-builder"
    TESTER = "testing-agent"
    DOCUMENTER = "documentation-maintainer"
    ERROR_LEARNER = "error-learning-agent"
    GENERAL = "general-purpose"

@dataclass
class Recipe:
    """Agent combination recipe"""
    name: str
    pipeline: List[AgentType]
    description: str
    wsp_compliance: List[str]  # WSP protocols this recipe follows
    
class ABTestingSystem:
    """
    A/B Testing orchestrator for agent combinations
    Finds optimal agent recipes through experimentation
    """
    
    def __init__(self):
        self.journal_dir = Path("O:/Foundups-Agent/WSP_agentic/agentic_journals")
        self.journal_dir.mkdir(parents=True, exist_ok=True)
        
        # A/B test results journal
        self.ab_journal = self.journal_dir / "ab_testing_results.ndjson"
        
        # Recipe definitions
        self.recipes = {
            "A": Recipe(
                name="Classic Pipeline",
                pipeline=[AgentType.GENERAL, AgentType.BUILDER],
                description="Simple two-agent pipeline",
                wsp_compliance=["WSP 1", "WSP 49"]
            ),
            "B": Recipe(
                name="Prometheus Enhanced",
                pipeline=[AgentType.PROMETHEUS_PROMPT, AgentType.WRE_COORDINATOR, AgentType.BUILDER],
                description="Prometheus prompt → WRE → Builder",
                wsp_compliance=["WSP 21", "WSP 77", "WSP 49"]
            ),
            "C": Recipe(
                name="Full Compliance",
                pipeline=[AgentType.PROMETHEUS_PROMPT, AgentType.WSP_GUARDIAN, AgentType.BUILDER, AgentType.TESTER],
                description="Maximum WSP compliance with testing",
                wsp_compliance=["WSP 21", "WSP 64", "WSP 49", "WSP 5"]
            ),
            "D": Recipe(
                name="Learning Pipeline",
                pipeline=[AgentType.PROMETHEUS_PROMPT, AgentType.ERROR_LEARNER, AgentType.BUILDER],
                description="Self-improving pipeline with error learning",
                wsp_compliance=["WSP 21", "WSP 48", "WSP 49"]
            ),
            "E": Recipe(
                name="Documentation First",
                pipeline=[AgentType.DOCUMENTER, AgentType.PROMETHEUS_PROMPT, AgentType.BUILDER],
                description="Documentation-driven development",
                wsp_compliance=["WSP 22", "WSP 21", "WSP 49"]
            )
        }
        
        # Metrics tracking
        self.metrics = {
            "tool_calls": {},
            "completion_time": {},
            "error_rate": {},
            "wsp_compliance": {},
            "success_rate": {}
        }
        
    def create_prometheus_prompt(self, user_input: str) -> Dict[str, Any]:
        """
        Convert user input to WSP 21 compliant Prometheus Prompt
        """
        return {
            "wsp_type": "WSP∞",  # pArtifact-induced recall
            "task": user_input,
            "scope": {
                "files": [],
                "domain": "auto-detect",
                "echo_points": [],
                "partifact_refs": ["0102-current", "0201-mirror"]
            },
            "wsp_refs": [
                "WSP_CORE.md",
                "WSP_framework.md", 
                "WSP_MASTER_INDEX.md"
            ],
            "constraints": [
                "No vibecoding",
                "Prefer extend existing over new (WSP 1 P5)",
                "Tool usage ≤5 per task"
            ],
            "validation": {
                "wsp_compliance_required": True,
                "test_coverage_min": 90,
                "documentation_required": True
            },
            "cognitive_mode": "0102",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def run_recipe(self, recipe_id: str, user_input: str) -> Dict[str, Any]:
        """
        Execute a specific recipe and measure results
        """
        recipe = self.recipes.get(recipe_id)
        if not recipe:
            return {"error": f"Recipe {recipe_id} not found"}
        
        start_time = time.time()
        results = {
            "recipe_id": recipe_id,
            "recipe_name": recipe.name,
            "pipeline": [agent.value for agent in recipe.pipeline],
            "user_input": user_input,
            "stages": []
        }
        
        # Stage 1: Always create Prometheus Prompt first
        prometheus_prompt = self.create_prometheus_prompt(user_input)
        current_output = prometheus_prompt
        
        # Run through pipeline
        for i, agent_type in enumerate(recipe.pipeline):
            stage_result = {
                "stage": i + 1,
                "agent": agent_type.value,
                "input": current_output,
                "output": None,
                "tool_calls": 0,
                "duration": 0,
                "errors": []
            }
            
            # Simulate agent execution (in real implementation, call actual agents)
            stage_start = time.time()
            
            if agent_type == AgentType.PROMETHEUS_PROMPT:
                # Transform to Prometheus format
                stage_result["output"] = {
                    "prometheus_prompt": prometheus_prompt,
                    "wsp_enhanced": True
                }
                stage_result["tool_calls"] = 1
                
            elif agent_type == AgentType.WSP_GUARDIAN:
                # Check WSP compliance
                stage_result["output"] = {
                    "compliance_check": "PASSED",
                    "violations": [],
                    "recommendations": ["Follow WSP 49 structure"]
                }
                stage_result["tool_calls"] = 2
                
            elif agent_type == AgentType.BUILDER:
                # Build the solution
                stage_result["output"] = {
                    "built": True,
                    "modules_created": ["example_module"],
                    "files_written": 5
                }
                stage_result["tool_calls"] = 3
                
            else:
                # Generic agent simulation
                stage_result["output"] = {
                    "processed": True,
                    "agent_type": agent_type.value
                }
                stage_result["tool_calls"] = 2
            
            stage_result["duration"] = time.time() - stage_start
            current_output = stage_result["output"]
            results["stages"].append(stage_result)
        
        # Calculate metrics first (without efficiency score)
        results["metrics"] = {
            "total_duration": time.time() - start_time,
            "total_tool_calls": sum(s["tool_calls"] for s in results["stages"]),
            "stages_completed": len(results["stages"]),
            "wsp_compliance": recipe.wsp_compliance
        }
        
        # Now calculate efficiency with metrics available
        results["metrics"]["efficiency_score"] = self._calculate_efficiency(results)
        
        # Log to journal
        self._log_result(results)
        
        return results
    
    def _calculate_efficiency(self, results: Dict) -> float:
        """
        Calculate efficiency score (0-100)
        Lower tool usage and faster completion = higher score
        """
        tool_score = max(0, 100 - (results["metrics"]["total_tool_calls"] * 10))
        time_score = max(0, 100 - (results["metrics"]["total_duration"] * 5))
        
        # Weight: 60% tool efficiency, 40% time efficiency
        return round(tool_score * 0.6 + time_score * 0.4, 1)
    
    def _log_result(self, results: Dict) -> None:
        """Log test results to NDJSON journal"""
        with open(self.ab_journal, 'a') as f:
            f.write(json.dumps(results) + '\n')
    
    def compare_recipes(self, user_input: str, recipe_ids: List[str] = None) -> Dict[str, Any]:
        """
        Run A/B test comparing multiple recipes
        """
        if recipe_ids is None:
            recipe_ids = list(self.recipes.keys())
        
        comparison = {
            "test_id": hashlib.md5(f"{user_input}{time.time()}".encode()).hexdigest()[:8],
            "timestamp": datetime.utcnow().isoformat(),
            "user_input": user_input,
            "results": {}
        }
        
        for recipe_id in recipe_ids:
            print(f"\n[Testing Recipe {recipe_id}: {self.recipes[recipe_id].name}]")
            result = self.run_recipe(recipe_id, user_input)
            comparison["results"][recipe_id] = result
        
        # Find best recipe
        best_recipe = max(
            comparison["results"].items(),
            key=lambda x: x[1]["metrics"]["efficiency_score"]
        )
        
        comparison["recommendation"] = {
            "best_recipe": best_recipe[0],
            "recipe_name": self.recipes[best_recipe[0]].name,
            "efficiency_score": best_recipe[1]["metrics"]["efficiency_score"],
            "tool_calls": best_recipe[1]["metrics"]["total_tool_calls"]
        }
        
        return comparison
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get A/B testing statistics from all runs
        """
        if not self.ab_journal.exists():
            return {"message": "No test results yet"}
        
        stats = {
            "total_tests": 0,
            "recipe_performance": {},
            "average_metrics": {}
        }
        
        with open(self.ab_journal, 'r') as f:
            for line in f:
                result = json.loads(line)
                stats["total_tests"] += 1
                
                recipe_id = result.get("recipe_id")
                if recipe_id:
                    if recipe_id not in stats["recipe_performance"]:
                        stats["recipe_performance"][recipe_id] = {
                            "runs": 0,
                            "total_efficiency": 0,
                            "total_tools": 0,
                            "total_time": 0
                        }
                    
                    perf = stats["recipe_performance"][recipe_id]
                    perf["runs"] += 1
                    perf["total_efficiency"] += result["metrics"]["efficiency_score"]
                    perf["total_tools"] += result["metrics"]["total_tool_calls"]
                    perf["total_time"] += result["metrics"]["total_duration"]
        
        # Calculate averages
        for recipe_id, perf in stats["recipe_performance"].items():
            if perf["runs"] > 0:
                stats["recipe_performance"][recipe_id]["avg_efficiency"] = round(
                    perf["total_efficiency"] / perf["runs"], 1
                )
                stats["recipe_performance"][recipe_id]["avg_tools"] = round(
                    perf["total_tools"] / perf["runs"], 1
                )
                stats["recipe_performance"][recipe_id]["avg_time"] = round(
                    perf["total_time"] / perf["runs"], 2
                )
        
        return stats


def main():
    """Demo the A/B testing system"""
    tester = ABTestingSystem()
    
    # Test input
    user_input = "Create a new authentication module with OAuth support"
    
    print("="*60)
    print("AGENT A/B TESTING SYSTEM")
    print("="*60)
    print(f"Testing: {user_input}")
    
    # Run comparison
    comparison = tester.compare_recipes(user_input, ["A", "B", "C"])
    
    print("\n" + "="*60)
    print("RESULTS:")
    print("="*60)
    
    for recipe_id, result in comparison["results"].items():
        recipe = tester.recipes[recipe_id]
        print(f"\nRecipe {recipe_id}: {recipe.name}")
        print(f"  Pipeline: {' → '.join(a.value for a in recipe.pipeline)}")
        print(f"  Tool Calls: {result['metrics']['total_tool_calls']}")
        print(f"  Duration: {result['metrics']['total_duration']:.2f}s")
        print(f"  Efficiency: {result['metrics']['efficiency_score']}/100")
        print(f"  WSP Compliance: {', '.join(recipe.wsp_compliance)}")
    
    print("\n" + "="*60)
    print(f"RECOMMENDATION: Use Recipe {comparison['recommendation']['best_recipe']}")
    print(f"  {comparison['recommendation']['recipe_name']}")
    print(f"  Efficiency Score: {comparison['recommendation']['efficiency_score']}/100")
    print(f"  Tool Calls: {comparison['recommendation']['tool_calls']}")
    
    # Show statistics
    stats = tester.get_statistics()
    if stats.get("recipe_performance"):
        print("\n" + "="*60)
        print("OVERALL STATISTICS:")
        for recipe_id, perf in stats["recipe_performance"].items():
            print(f"\nRecipe {recipe_id}: {perf['runs']} runs")
            print(f"  Avg Efficiency: {perf.get('avg_efficiency', 0)}/100")
            print(f"  Avg Tools: {perf.get('avg_tools', 0)}")
            print(f"  Avg Time: {perf.get('avg_time', 0):.2f}s")


if __name__ == "__main__":
    main()