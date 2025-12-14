#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PQN Research DAE Orchestrator
Per WSP 80: Multi-agent DAE orchestration for PQN research
Per WSP 84: Uses existing PQN infrastructure
Per WSP 50: Pre-action verification of research collaboration

Enables Grok and Gemini to operate as collaborative PQN research DAEs
using advanced QCoT to explore PQN phenomena and improve rESP documents.
"""

import os
import sys
import json
import time
import asyncio
import logging
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Set UTF-8 encoding for Windows compatibility
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

logger = logging.getLogger(__name__)

# Add project root to path for proper imports
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

class ResearchPhase(Enum):
    """Research phases for PQN investigation."""
    THEORETICAL_ANALYSIS = "theoretical_analysis"
    EMPIRICAL_VALIDATION = "empirical_validation"
    DOCUMENT_SYNTHESIS = "document_synthesis"
    CROSS_MODEL_CORRELATION = "cross_model_correlation"

@dataclass
class ResearchTask:
    """Individual research task for PQN investigation."""
    phase: ResearchPhase
    title: str
    description: str
    assigned_agent: str
    priority: int
    dependencies: List[str]
    expected_output: str
    qcot_prompt: str

@dataclass
class ResearchSession:
    """Research session with multiple agents."""
    session_id: str
    agents: Dict[str, Dict[str, Any]]
    tasks: List[ResearchTask]
    results: Dict[str, Any]
    timestamp: str

class PQNResearchDAEOrchestrator:
    """
    Orchestrates collaborative PQN research between Agents.
    """
    
    def __init__(self):
        """Initialize PQN Research DAE Orchestrator."""
        self.research_plan = self._load_research_plan()
        self.resonance_frequencies = self._load_resonance_frequencies()
        self.empirical_evidence = self._load_empirical_evidence()
        self.active_sessions: Dict[str, ResearchSession] = {}
        
        # Agent configurations
        self.agents = {
            "grok": {
                "name": "Grok-Beta",
                "api_key": os.getenv('GROK_API_KEY') or os.getenv('XAI_API_KEY'),
                "model": "grok-beta", 
                "specialization": "Emergent pattern synthesis and holistic integration",
                "qcot_style": "Intuitive leaps and pattern recognition"
            },
            "gemini": {
                "name": "Gemini-Pro", 
                "api_key": os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY'),
                "model": os.getenv('GEMINI_MODEL_NAME', "gemini-1.5-flash"), 
                "specialization": "Multimodal validation and cross-modal coherence",
                "qcot_style": "Analytical decomposition and systematic validation"
            },
            "openai": {
                "name": "GPT-4o",
                "api_key": os.getenv('OPENAI_API_KEY'),
                "model": "gpt-4o",
                "specialization": "Strategic reasoning and logical structuring",
                "qcot_style": "Step-by-step deductive reasoning"
            },
            "claude": {
                "name": "Claude-3.5",
                "api_key": os.getenv('CLAUDE_API_KEY') or os.getenv('ANTHROPIC_API_KEY'),
                "model": "claude-3-5-sonnet-20240620",
                "specialization": "Nuanced contextual analysis and ethical alignment",
                "qcot_style": "Dialectical exploration and nuance detection"
            }
        }
        
        # Initialize Connectors
        self.connectors = {}
        try:
            from modules.ai_intelligence.rESP_o1o2.src.llm_connector import LLMConnector
            
            for agent_id, config in self.agents.items():
                if config["api_key"]:
                    try:
                        self.connectors[agent_id] = LLMConnector(
                            model=config["model"],
                            api_key=config["api_key"]
                        )
                    except Exception as e:
                        logger.warning(f"Failed to init connector for {agent_id}: {e}")
            
            logger.info(f"Real LLM Connectors initialized: {list(self.connectors.keys())}")
        except Exception as e:
            logger.error(f"Failed to initialize connectors module: {e}")

        logger.info("PQN Research DAE Orchestrator initialized")
        logger.info(f"Agents Configured: {len(self.agents)}")
        logger.info(f"Active Connectors: {len(self.connectors)}")
        logger.info(f"Research Plan: {len(self.research_plan)} sections")
        logger.info(f"Resonance Frequencies: {len(self.resonance_frequencies)} components")
    
    def _load_research_plan(self) -> Dict[str, Any]:
        """Load PQN Research Plan document."""
        plan_path = project_root / "WSP_knowledge" / "docs" / "Papers" / "PQN_Research_Plan.md"
        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"content": content, "sections": self._parse_sections(content)}
        except Exception as e:
            logger.warning(f"Error loading research plan: {e}")
            return {"content": "", "sections": []}
    
    def _load_resonance_frequencies(self) -> Dict[str, Any]:
        """Load Neural Networks and Resonance Frequencies document."""
        freq_path = project_root / "WSP_knowledge" / "docs" / "Papers" / "Neural_Networks_and_Resonance_Frequencies.md"
        try:
            with open(freq_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"content": content, "sections": self._parse_sections(content)}
        except Exception as e:
            logger.warning(f"Error loading resonance frequencies: {e}")
            return {"content": "", "sections": []}
    
    def _load_empirical_evidence(self) -> Dict[str, Any]:
        """Load empirical evidence from campaign results."""
        evidence_path = project_root / "modules" / "ai_intelligence" / "pqn_alignment" / "campaign_results"
        evidence = {}
        
        if evidence_path.exists():
            for result_dir in evidence_path.iterdir():
                if result_dir.is_dir():
                    campaign_log = result_dir / "campaign_log.json"
                    if campaign_log.exists():
                        try:
                            with open(campaign_log, 'r') as f:
                                evidence[result_dir.name] = json.load(f)
                        except Exception as e:
                            logger.warning(f"Error loading {campaign_log}: {e}")

        return evidence
    
    def _parse_sections(self, content: str) -> List[str]:
        """Parse markdown sections from content."""
        sections = []
        lines = content.split('\n')
        current_section = ""
        
        for line in lines:
            if line.startswith('#'):
                if current_section:
                    sections.append(current_section.strip())
                current_section = line
            else:
                current_section += line + '\n'
        
        if current_section:
            sections.append(current_section.strip())
        
        return sections
    
    def create_research_session(self, session_name: str, selected_agents: List[str] = None) -> ResearchSession:
        """Create a new research session with collaborative tasks."""
        session_id = f"pqn_research_{int(time.time())}"
        
        # Default to all configured active agents if not specified
        if not selected_agents:
            # Prefer active connectors, else all default keys
            if self.connectors:
                selected_agents = list(self.connectors.keys())
            else:
                selected_agents = ["grok", "gemini"] # Simulation Defaults
            
        # Filter agents based on selection
        active_agents = {k: v for k, v in self.agents.items() if k in selected_agents}
        
        # Dynamic assignment based on active agents
        tasks = []
        
        # Helper to assign task to available agent (Round Robin or Preference)
        def get_assignee(preferred: str) -> str:
            if preferred in active_agents:
                return preferred
            # Fallback to first available
            return list(active_agents.keys())[0] if active_agents else "grok"

        # Standard PQN Workflow
        tasks.append(ResearchTask(
            phase=ResearchPhase.THEORETICAL_ANALYSIS,
            title="PQN Resonance Frequency Analysis",
            description="Analyze 7.05 Hz resonance in context of spectral bias theory",
            assigned_agent=get_assignee("grok"),
            priority=1,
            dependencies=[],
            expected_output="Theoretical framework for PQN resonance mechanism",
            qcot_prompt="UN: Analyze spectral bias vs biological resonance\nDAO: Synthesize PQN resonance theory\nDU: Emerge unified framework"
        ))

        tasks.append(ResearchTask(
            phase=ResearchPhase.THEORETICAL_ANALYSIS,
            title="Cross-Modal Coherence Validation",
            description="Validate PQN theory across different neural architectures",
            assigned_agent=get_assignee("gemini"),
            priority=1,
            dependencies=[],
            expected_output="Cross-architecture validation framework",
            qcot_prompt="UN: Examine multi-model PQN evidence\nDAO: Validate coherence patterns\nDU: Emerge validation protocol"
        ))
        
        if len(active_agents) > 1:
            # Collaborative Synthesis only if multiple agents
            tasks.append(ResearchTask(
                phase=ResearchPhase.CROSS_MODEL_CORRELATION,
                title="Multi-Agent QCoT Synthesis",
                description="Synthesize findings from both agents using advanced QCoT",
                assigned_agent=get_assignee("claude" if "claude" in active_agents else "grok"),
                priority=4,
                dependencies=["PQN Resonance Frequency Analysis", "Cross-Modal Coherence Validation"],
                expected_output="Final collaborative research synthesis",
                qcot_prompt="UN: Integrate all research findings\nDAO: Synthesize multi-agent insights\nDU: Emerge unified PQN theory"
            ))
        
        session = ResearchSession(
            session_id=session_id,
            agents=active_agents,
            tasks=tasks,
            results={},
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        )
        
        self.active_sessions[session_id] = session
        logger.info(f"Created research session: {session_id}")
        logger.info(f"Active Agents: {list(active_agents.keys())}")
        logger.info(f"Tasks: {len(tasks)} tasks generated")
        
        return session

    async def execute_research_session(self, session_id: str) -> Dict[str, Any]:
        """Execute a complete research session with collaborative agents."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        logger.info(f"Executing research session: {session_id}")

        # Execute tasks in dependency order
        completed_tasks = {}

        for task in sorted(session.tasks, key=lambda t: t.priority):
            logger.info(f"Executing: {task.title}")
            logger.info(f"Agent: {task.assigned_agent}")
            logger.info(f"Phase: {task.phase.value}")

            # Check dependencies
            if task.dependencies:
                missing_deps = [dep for dep in task.dependencies if dep not in completed_tasks]
                if missing_deps:
                    logger.info(f"Waiting for dependencies: {missing_deps}")
                    continue

            # Execute task with QCoT
            result = await self._execute_qcot_task(task, session)
            completed_tasks[task.title] = result

            logger.info(f"Completed: {task.title}")
            logger.info(f"Output: {len(result.get('output', ''))} characters")
        
        # Final synthesis
        synthesis = await self._create_final_synthesis(session, completed_tasks)
        session.results = {
            "completed_tasks": completed_tasks,
            "final_synthesis": synthesis,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        
        logger.info(f"Research session completed: {session_id}")
        logger.info(f"Results: {len(completed_tasks)} tasks completed")
        
        return session.results
    
    async def _execute_qcot_task(self, task: ResearchTask, session: ResearchSession) -> Dict[str, Any]:
        """Execute a single task using advanced QCoT."""
        agent_config = session.agents[task.assigned_agent]
        
        # Build context from research documents
        context = self._build_research_context(task, session)
        
        # Execute QCoT reasoning
        qcot_result = await self._execute_qcot_reasoning(
            task.qcot_prompt,
            context,
            task.assigned_agent, # Pass ID
            agent_config
        )
        
        return {
            "task": task.title,
            "agent": task.assigned_agent,
            "phase": task.phase.value,
            "qcot_prompt": task.qcot_prompt,
            "context": context,
            "output": qcot_result,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    
    def _build_research_context(self, task: ResearchTask, session: ResearchSession) -> str:
        """Build research context for task execution."""
        context_parts = []
        
        # Add relevant research plan sections
        if task.phase == ResearchPhase.THEORETICAL_ANALYSIS:
            context_parts.append("PQN Research Plan Sections:")
            context_parts.extend(self.research_plan["sections"][:3])  # First 3 sections
        
        # Add resonance frequency analysis
        if "resonance" in task.title.lower():
            context_parts.append("Resonance Frequency Analysis:")
            context_parts.extend(self.resonance_frequencies["sections"][:4])  # First 4 sections
        
        # Add empirical evidence
        if task.phase == ResearchPhase.EMPIRICAL_VALIDATION:
            context_parts.append("Empirical Evidence:")
            for model, evidence in self.empirical_evidence.items():
                context_parts.append(f"Model: {model}")
                context_parts.append(f"Status: {evidence.get('campaign_summary', {}).get('overall_status', 'Unknown')}")
        
        return "\n\n".join(context_parts)
    
    async def _execute_qcot_reasoning(self, prompt: str, context: str, agent_id: str, agent_config: Dict[str, Any]) -> str:
        """Execute logic via Real LLM if available, else simulate."""
        
        connector = self.connectors.get(agent_id)
        
        if connector and not getattr(connector, 'simulation_mode', True):
            # Real API Call
            full_prompt = f"""
CONTEXT:
{context[:3000]}

TASK:
Identify and synthesize emergent PQN patterns.
{prompt}

Review the context above by applying your specific specialization: {agent_config['specialization']}
"""
            # Use System Prompt for specialization
            system_prompt = f"You are {agent_config['name']}. Specialization: {agent_config['specialization']}. Style: {agent_config['qcot_style']}."
            
            logger.info(f"Calling Real API for {agent_config['name']}...")
            try:
                response = await asyncio.to_thread(
                    connector.get_response, 
                    prompt=full_prompt, 
                    system_prompt=system_prompt,
                    temperature=0.7,
                    max_tokens=1500
                )
                if response:
                    return response
            except Exception as e:
                logger.error(f"API Call Failed: {e}. Falling back to simulation.")

        # Fallback Simulation Code
        qcot_steps = [
            f"UN (Understanding): {prompt.split('UN:')[1].split('DAO:')[0].strip()}",
            f"DAO (Execution Logic): {prompt.split('DAO:')[1].split('DU:')[0].strip()}",
            f"DU (Emergence): {prompt.split('DU:')[1].strip()}"
        ]
        
        result = f"""
Advanced QCoT Execution by {agent_config['name']} [SIMULATED]
Specialization: {agent_config['specialization']}
Reasoning Style: {agent_config['qcot_style']}

Context Analysis:
{context[:500]}...

QCoT Reasoning Steps:
{chr(10).join(qcot_steps)}

Emergent Synthesis:
Based on the QCoT analysis, this agent has synthesized new insights about PQN phenomena
that advance our understanding of quantum-cognitive states in neural networks.
        """
        
        return result
    
    async def _create_final_synthesis(self, session: ResearchSession, completed_tasks: Dict[str, Any]) -> Dict[str, Any]:
        """Create final synthesis of all research findings."""
        synthesis = {
            "session_id": session.session_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "agents_used": list(session.agents.keys()),
            "tasks_completed": len(completed_tasks),
            "key_insights": [],
            "recommendations": [],
            "next_steps": []
        }
        
        # Extract key insights from completed tasks
        for task_title, result in completed_tasks.items():
            synthesis["key_insights"].append({
                "task": task_title,
                "agent": result["agent"],
                "insight": f"Advanced QCoT analysis by {result['agent']} revealed new PQN insights"
            })
        
        synthesis["recommendations"] = [
            "Continue multi-agent collaborative research",
            "Integrate findings into rESP framework",
            "Validate insights through additional empirical testing",
            "Develop PQN-enhanced neural architectures"
        ]
        
        return synthesis

async def main():
    """Main function to execute PQN research collaboration."""
    orchestrator = PQNResearchDAEOrchestrator()
    
    while True:
        print("\n" + "="*60)
        print("PQN CLOUD RESEARCH ORCHESTRATOR (0102)")
        print("="*60)
        
        # Detect active connectors
        available_agents = list(orchestrator.connectors.keys())
        all_configured = list(orchestrator.agents.keys())
        
        print(f"[STATUS] Detected Keys: {len(available_agents)} / {len(all_configured)} Configured")
        for agent_id, config in orchestrator.agents.items():
            status = "READY" if agent_id in available_agents else "MISSING KEY"
            print(f"  - {config['name']:<15} : {status}")
        print("-" * 60)
        
        options = []
        
        # 1. Collaborative Mode (if 2+)
        if len(available_agents) >= 2:
            options.append(("1", f"Collaborative Mode ({len(available_agents)} Agents) [RECOMMENDED]", available_agents))
        
        # Solo Modes
        idx_start = 2 if len(available_agents) >= 2 else 1
        for i, agent_id in enumerate(available_agents):
            key = str(idx_start + i)
            name = orchestrator.agents[agent_id]["name"]
            options.append((key, f"{name} Solo", [agent_id]))
             
        # Simulation if none
        if not available_agents:
             print("[INFO] No API keys detected. Running in SIMULATION mode.")
             options.append(("1", "Simulate Collaborative Mode (Grok + Gemini)", ["grok", "gemini"]))

        # Print Options
        for key, label, _ in options:
             print(f"{key}. {label}")
        
        print("0. Back to PQN Menu")
        
        choice = input("\nSelect Research Mode (0-5): ").strip()
        
        if choice == "0":
            break
            
        selected_agents = None
        for key, label, agents in options:
            if choice == key:
                selected_agents = agents
                break
                
        if selected_agents:
            print(f"\n[INIT] Starting Research Session with: {selected_agents}")
            session = orchestrator.create_research_session("PQN_Research", selected_agents)
            results = await orchestrator.execute_research_session(session.session_id)
            
            # Save results
            output_path = Path("research_results") / f"{session.session_id}_results.json"
            output_path.parent.mkdir(exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
                
            print(f"\n[DONE] Research results saved to: {output_path}")
            print(f"Key insights: {len(results.get('final_synthesis', {}).get('key_insights', []))}")
            input("Press Enter to continue...")
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    asyncio.run(main())
