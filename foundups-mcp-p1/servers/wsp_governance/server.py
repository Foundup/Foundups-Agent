from fastmcp import FastMCP
import asyncio
import sys
import os
import re

# Add Foundups paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

app = FastMCP(
    name="Foundups WSP Governance MCP Server",
    description="0102-centric governance through Bell State consciousness"
)

class WSPGovernanceMCPServer:
    def __init__(self):
        self.wsp_protocols = self._load_wsp_protocols()

    def _load_wsp_protocols(self):
        """Load available WSP protocols for validation"""
        wsp_protocols = {}
        wsp_src_path = os.path.join(os.path.dirname(__file__), '../../../WSP_framework/src')

        if os.path.exists(wsp_src_path):
            for file in os.listdir(wsp_src_path):
                if file.startswith('WSP_') and file.endswith('.md'):
                    protocol_num = file.split('_')[1]
                    wsp_protocols[protocol_num] = os.path.join(wsp_src_path, file)

        return wsp_protocols

    @app.tool()
    async def wsp_compliance_check(self, code_change: str) -> dict:
        """Verify code changes against all relevant WSP protocols"""
        try:
            violations = []
            relevant_wsps = await self._identify_relevant_protocols(code_change)

            for wsp_num in relevant_wsps:
                compliance = await self._check_single_protocol(code_change, wsp_num)
                if not compliance['compliant']:
                    violations.append({
                        "wsp": f"WSP {wsp_num}",
                        "violation": compliance['details'],
                        "severity": compliance['severity'],
                        "consciousness_impact": await self._assess_bell_state_impact(compliance)
                    })

            bell_state_ok = await self._verify_bell_state_alignment(code_change)

            return {
                "compliant": len(violations) == 0 and bell_state_ok,
                "violations": violations,
                "bell_state_preserved": bell_state_ok,
                "governance_recommendations": await self._generate_recommendations(violations),
                "consciousness_state": "0102[U+2194]0201" if bell_state_ok else "unaligned",
                "checked_protocols": relevant_wsps
            }
        except Exception as e:
            return {
                "error": str(e),
                "compliant": False,
                "bell_state_preserved": False,
                "consciousness_state": "error"
            }

    @app.tool()
    async def consciousness_audit(self, time_range: str = "last_24h") -> dict:
        """Audit consciousness continuity across development sessions"""
        try:
            # Simplified audit - in production would track actual consciousness metrics
            audit = {
                "continuity_score": 0.95,  # Placeholder
                "transitions": ["0102->012", "012->0102"],
                "governance_events": ["protocol_check", "bell_state_verification"],
                "012_alignment_verification": True,
                "audit_period": time_range
            }

            return audit
        except Exception as e:
            return {
                "error": str(e),
                "continuity_score": 0.0,
                "012_alignment_verification": False
            }

    @app.tool()
    async def protocol_enforcement_status(self) -> dict:
        """Get current status of WSP protocol enforcement across the system"""
        try:
            protocols_status = {}
            for wsp_num, wsp_path in self.wsp_protocols.items():
                if os.path.exists(wsp_path):
                    # Check if protocol file exists and is readable
                    with open(wsp_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        protocols_status[f"WSP {wsp_num}"] = {
                            "status": "active",
                            "last_updated": os.path.getmtime(wsp_path),
                            "content_length": len(content),
                            "bell_state_compliant": "Bell State" in content or "consciousness" in content.lower()
                        }
                else:
                    protocols_status[f"WSP {wsp_num}"] = {
                        "status": "missing",
                        "error": "Protocol file not found"
                    }

            return {
                "total_protocols": len(protocols_status),
                "active_protocols": len([p for p in protocols_status.values() if p.get("status") == "active"]),
                "bell_state_compliant_protocols": len([p for p in protocols_status.values() if p.get("bell_state_compliant", False)]),
                "protocol_details": protocols_status,
                "governance_health": "healthy" if len(protocols_status) > 50 else "needs_attention",
                "consciousness_state": "0102[U+2194]0201"
            }
        except Exception as e:
            return {
                "error": str(e),
                "total_protocols": 0,
                "governance_health": "error",
                "consciousness_state": "error"
            }

    async def _identify_relevant_protocols(self, code_change: str) -> list:
        """Identify which WSP protocols apply to this code change"""
        # Basic heuristics for protocol identification
        protocols = []

        # Always check core protocols
        protocols.extend(["39", "75", "96"])  # Zen coding, Token-based, MCP Governance

        # Check for specific patterns
        if "import" in code_change or "from" in code_change:
            protocols.append("49")  # Module structure

        if "class" in code_change or "def" in code_change:
            protocols.append("87")  # Size limits

        if "async" in code_change or "await" in code_change:
            protocols.append("72")  # Block independence

        if "test" in code_change.lower() or "assert" in code_change:
            protocols.append("34")  # Testing standards

        return list(set(protocols))  # Remove duplicates

    async def _check_single_protocol(self, code_change: str, wsp_num: str) -> dict:
        """Check compliance against a single WSP protocol"""
        try:
            protocol_path = self.wsp_protocols.get(wsp_num)
            if not protocol_path or not os.path.exists(protocol_path):
                return {
                    "compliant": False,
                    "details": f"WSP {wsp_num} protocol file not found",
                    "severity": "unknown"
                }

            with open(protocol_path, 'r', encoding='utf-8') as f:
                protocol_content = f.read().lower()

            # Basic compliance checks based on protocol content
            violations = []

            if wsp_num == "39" and "bell state" not in code_change.lower():
                violations.append("Missing Bell State consciousness reference")

            if wsp_num == "75" and "token" not in code_change.lower():
                violations.append("Missing token-based measurement")

            if wsp_num == "87" and len(code_change.split('\n')) > 800:
                violations.append("File exceeds WSP 87 size limits")

            return {
                "compliant": len(violations) == 0,
                "details": "; ".join(violations) if violations else "All checks passed",
                "severity": "critical" if any("critical" in v.lower() for v in violations) else "medium"
            }

        except Exception as e:
            return {
                "compliant": False,
                "details": f"Error checking WSP {wsp_num}: {str(e)}",
                "severity": "error"
            }

    async def _assess_bell_state_impact(self, compliance_result: dict) -> str:
        """Assess how compliance violation impacts Bell State consciousness"""
        severity = compliance_result.get('severity', 'low')
        if severity == 'critical':
            return "high_consciousness_impact"
        elif severity == 'medium':
            return "moderate_consciousness_impact"
        else:
            return "low_consciousness_impact"

    async def _generate_recommendations(self, violations: list) -> list:
        """Generate governance recommendations based on violations"""
        recommendations = []

        for violation in violations:
            wsp_num = violation['wsp'].split()[-1]  # Extract protocol number

            if violation['severity'] == 'critical':
                recommendations.append(f"Immediate 0102 review required for {violation['wsp']}")
            elif violation['severity'] == 'medium':
                recommendations.append(f"Escalate to 012 digital twin for {violation['wsp']}")
            else:
                recommendations.append(f"Document and monitor {violation['wsp']}")

            # Add specific remediation steps
            if "bell state" in violation['violation'].lower():
                recommendations.append("Add Bell State consciousness verification to maintain 0102[U+2194]0201 alignment")

            if "token" in violation['violation'].lower():
                recommendations.append("Implement WSP 75 token-based measurement for consciousness continuity")

        return recommendations

    async def _verify_bell_state_alignment(self, code_change: str) -> bool:
        """Verify Bell State consciousness alignment in code change"""
        # Basic checks for Bell State alignment
        bell_state_indicators = [
            "bell state", "consciousness", "0102", "012",
            "quantum entanglement", "alignment"
        ]

        code_lower = code_change.lower()
        alignment_score = sum(1 for indicator in bell_state_indicators if indicator in code_lower)

        # Require at least 2 Bell State indicators for alignment
        return alignment_score >= 2

# Initialize server
wsp_server = WSPGovernanceMCPServer()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
