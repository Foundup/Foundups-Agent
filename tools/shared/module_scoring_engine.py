"""
WSP 37 Dynamic Module Scoring Engine
====================================

This module implements the WSP 37 Roadmap Scoring System with dynamic priority
calculation based on roadmap progression (POC → Prototype → MVP).

The engine automatically adjusts module priorities based on:
- Roadmap progression status
- Dependency relationships  
- 012 priority changes
- System health and completion status

Scoring Dimensions (WSP 15 MPS System):
- Complexity (1-5): Implementation difficulty
- Importance (1-5): Essential nature for core functions
- Deferability (1-5): Urgency (lower = more deferrable)
- Impact (1-5): Value delivered to users/system

Priority Classification:
- P0 (16-20): Critical - Work begins immediately
- P1 (13-15): High - Important for near-term roadmap
- P2 (10-12): Medium - Valuable but not urgent
- P3 (7-9): Low - Can be deferred
- P4 (4-6): Backlog - Reconsidered in future planning
"""

import yaml
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ModuleScore:
    """Represents a module's scoring data"""
    name: str
    path: str
    domain: str
    status: str
    roadmap_stage: str
    complexity: int
    importance: int
    deferability: int
    impact: int
    rider_influence: int
    mps_score: int
    llme_current: str
    llme_target: str
    owner: str
    last_updated: str
    summary: str
    priority_class: str

class WSP37ScoringEngine:
    """WSP 37 Dynamic Module Scoring Engine"""
    
    def __init__(self, scoring_file: str = "modules_to_score.yaml"):
        self.scoring_file = scoring_file
        self.modules: Dict[str, ModuleScore] = {}
        self.load_modules()
    
    def load_modules(self) -> None:
        """Load modules from YAML scoring file"""
        try:
            if not os.path.exists(self.scoring_file):
                logger.warning(f"Scoring file {self.scoring_file} not found")
                return
            
            with open(self.scoring_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data or 'modules' not in data:
                logger.warning("No modules found in scoring file")
                return
            
            for module_data in data['modules']:
                if 'scores' not in module_data:
                    logger.warning(f"Module {module_data.get('name', 'unknown')} missing scores")
                    continue
                
                scores = module_data['scores']
                mps_score = sum([
                    scores.get('complexity', 0),
                    scores.get('importance', 0),
                    scores.get('deferability', 0),
                    scores.get('impact', 0),
                    scores.get('rider_influence', 0)
                ])
                
                priority_class = self._calculate_priority_class(mps_score)
                
                module_score = ModuleScore(
                    name=module_data['name'],
                    path=module_data['path'],
                    domain=module_data.get('domain', 'unknown'),
                    status=module_data['status'],
                    roadmap_stage=module_data['roadmap_stage'],
                    complexity=scores.get('complexity', 0),
                    importance=scores.get('importance', 0),
                    deferability=scores.get('deferability', 0),
                    impact=scores.get('impact', 0),
                    rider_influence=scores.get('rider_influence', 0),
                    mps_score=mps_score,
                    llme_current=module_data.get('llme_current', '000'),
                    llme_target=module_data.get('llme_target', '111'),
                    owner=module_data.get('owner', '0102'),
                    last_updated=module_data.get('last_updated', datetime.now().strftime('%Y-%m-%d')),
                    summary=module_data.get('summary', ''),
                    priority_class=priority_class
                )
                
                self.modules[module_data['name']] = module_score
                
            logger.info(f"Loaded {len(self.modules)} modules from scoring file")
            
        except Exception as e:
            logger.error(f"Error loading modules: {e}")
    
    def _calculate_priority_class(self, mps_score: int) -> str:
        """Calculate priority class based on MPS score (now includes rider influence)"""
        if mps_score >= 20:
            return "P0"
        elif mps_score >= 15:
            return "P1"
        elif mps_score >= 10:
            return "P2"
        elif mps_score >= 7:
            return "P3"
        else:
            return "P4"
    
    def get_priority_modules(self, priority_class: str = "P0") -> List[ModuleScore]:
        """Get modules by priority class, sorted by MPS score (highest first)"""
        priority_modules = [
            module for module in self.modules.values()
            if module.priority_class == priority_class
        ]
        return sorted(priority_modules, key=lambda x: x.mps_score, reverse=True)
    
    def get_all_modules_sorted(self) -> List[ModuleScore]:
        """Get all modules sorted by priority (P0 first, then P1, etc.)"""
        priority_order = ["P0", "P1", "P2", "P3", "P4"]
        sorted_modules = []
        
        for priority in priority_order:
            modules = self.get_priority_modules(priority)
            sorted_modules.extend(modules)
        
        return sorted_modules
    
    def get_module_by_name(self, name: str) -> Optional[ModuleScore]:
        """Get a specific module by name"""
        return self.modules.get(name)
    
    def get_modules_by_domain(self, domain: str) -> List[ModuleScore]:
        """Get all modules in a specific domain"""
        return [
            module for module in self.modules.values()
            if module.domain == domain
        ]
    
    def get_modules_by_status(self, status: str) -> List[ModuleScore]:
        """Get all modules with a specific status"""
        return [
            module for module in self.modules.values()
            if module.status == status
        ]
    
    def get_modules_by_roadmap_stage(self, stage: str) -> List[ModuleScore]:
        """Get all modules at a specific roadmap stage"""
        return [
            module for module in self.modules.values()
            if module.roadmap_stage == stage
        ]
    
    def update_module_status(self, name: str, new_status: str, new_llme: str) -> bool:
        """Update a module's status and LLME level"""
        if name not in self.modules:
            logger.warning(f"Module {name} not found")
            return False
        
        module = self.modules[name]
        module.status = new_status
        module.llme_current = new_llme
        module.last_updated = datetime.now().strftime('%Y-%m-%d')
        
        # Recalculate priority if status changed significantly
        if new_status != module.roadmap_stage:
            self._recalculate_module_priority(module)
        
        logger.info(f"Updated module {name}: status={new_status}, llme={new_llme}")
        return True
    
    def _recalculate_module_priority(self, module: ModuleScore) -> None:
        """Recalculate module priority based on current status"""
        # Adjust scores based on roadmap progression
        if module.status == "MVP":
            # MVP modules get reduced urgency
            module.deferability = max(1, module.deferability - 1)
        elif module.status == "POC":
            # POC modules get increased urgency if they're blocking
            if module.importance >= 4:
                module.deferability = min(5, module.deferability + 1)
        
        # Recalculate MPS score
        module.mps_score = sum([
            module.complexity,
            module.importance,
            module.deferability,
            module.impact
        ])
        
        # Update priority class
        module.priority_class = self._calculate_priority_class(module.mps_score)
    
    def add_dependency_boost(self, module_name: str, dependent_modules: List[str]) -> None:
        """Boost a module's importance if it's blocking other modules"""
        if module_name not in self.modules:
            logger.warning(f"Module {module_name} not found for dependency boost")
            return
        
        module = self.modules[module_name]
        dependent_count = len(dependent_modules)
        
        # Boost importance based on number of dependent modules
        if dependent_count >= 3:
            module.importance = min(5, module.importance + 1)
        elif dependent_count >= 1:
            # Small boost for any dependencies
            if module.importance < 4:
                module.importance += 1
        
        # Recalculate scores
        self._recalculate_module_priority(module)
        logger.info(f"Applied dependency boost to {module_name}: {dependent_count} dependents")
    
    def get_roadmap_summary(self) -> Dict[str, Dict]:
        """Get a summary of modules by roadmap stage"""
        summary = {
            "POC": {"count": 0, "modules": []},
            "PROTOTYPE": {"count": 0, "modules": []},
            "MVP": {"count": 0, "modules": []},
            "PLANNED": {"count": 0, "modules": []}
        }
        
        for module in self.modules.values():
            stage = module.roadmap_stage
            if stage in summary:
                summary[stage]["count"] += 1
                summary[stage]["modules"].append({
                    "name": module.name,
                    "priority": module.priority_class,
                    "mps_score": module.mps_score
                })
        
        return summary
    
    def get_priority_summary(self) -> Dict[str, Dict]:
        """Get a summary of modules by priority class"""
        summary = {}
        
        for priority in ["P0", "P1", "P2", "P3", "P4"]:
            modules = self.get_priority_modules(priority)
            summary[priority] = {
                "count": len(modules),
                "modules": [
                    {
                        "name": module.name,
                        "domain": module.domain,
                        "status": module.status,
                        "mps_score": module.mps_score
                    }
                    for module in modules
                ]
            }
        
        return summary
    
    def export_prioritized_list(self) -> List[Dict]:
        """Export modules as a prioritized list for WRE integration"""
        sorted_modules = self.get_all_modules_sorted()
        
        prioritized_list = []
        for i, module in enumerate(sorted_modules, 1):
            prioritized_list.append({
                "rank": i,
                "name": module.name,
                "path": module.path,
                "priority": module.priority_class,
                "mps_score": module.mps_score,
                "status": module.status,
                "domain": module.domain,
                "summary": module.summary
            })
        
        return prioritized_list

def main():
    """Test the scoring engine"""
    engine = WSP37ScoringEngine()
    
    print("=== WSP 37 Module Scoring Engine ===")
    print(f"Loaded {len(engine.modules)} modules")
    
    # Show priority summary
    priority_summary = engine.get_priority_summary()
    print("\n=== Priority Summary ===")
    for priority, data in priority_summary.items():
        print(f"{priority}: {data['count']} modules")
        for module in data['modules']:
            print(f"  - {module['name']} ({module['domain']}) - {module['status']} - Score: {module['mps_score']}")
    
    # Show roadmap summary
    roadmap_summary = engine.get_roadmap_summary()
    print("\n=== Roadmap Summary ===")
    for stage, data in roadmap_summary.items():
        print(f"{stage}: {data['count']} modules")
    
    # Show top priority modules
    p0_modules = engine.get_priority_modules("P0")
    print(f"\n=== P0 Critical Modules ({len(p0_modules)}) ===")
    for module in p0_modules:
        print(f"{module.name}: {module.mps_score} - {module.summary}")

if __name__ == "__main__":
    main() 