"""
WSP Validator - Protocol Compliance Validation

WSP Compliance:
- WSP 54 (Agent Duties): Protocol validation and compliance checking
- WSP 22 (ModLog): Change tracking and validation history
- WSP 11 (Interface): Public API documentation and standards

Validates WSP protocol compliance through Cursor agents.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Represents a WSP protocol validation result"""
    protocol: str
    is_compliant: bool
    violations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class WSPValidator:
    """
    Validates WSP protocol compliance through Cursor agents.
    
    This class ensures that all development activities follow WSP protocols
    and maintains compliance standards across the autonomous development system.
    """
    
    def __init__(self):
        """Initialize the WSP validator."""
        self.validation_history: List[Dict[str, Any]] = []
        self.protocol_definitions = self._initialize_protocol_definitions()
        
        logger.info("WSPValidator initialized")
    
    def _initialize_protocol_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Initialize WSP protocol definitions and validation rules."""
        return {
            "WSP_11": {
                "name": "Interface Documentation Standards",
                "requirements": [
                    "Public API definition",
                    "Parameter specifications",
                    "Return value documentation",
                    "Error handling",
                    "Usage examples"
                ],
                "validation_rules": [
                    "INTERFACE.md file exists",
                    "All public methods documented",
                    "Parameter types specified",
                    "Return values documented",
                    "Error scenarios covered"
                ]
            },
            "WSP_22": {
                "name": "ModLog and Roadmap Protocol",
                "requirements": [
                    "Chronological change log",
                    "WSP protocol references",
                    "Impact analysis",
                    "Enhancement tracking"
                ],
                "validation_rules": [
                    "ModLog.md file exists",
                    "ROADMAP.md file exists",
                    "Changes dated and documented",
                    "WSP references included",
                    "Impact analysis provided"
                ]
            },
            "WSP_54": {
                "name": "Agent Duties Specification",
                "requirements": [
                    "Agent role definitions",
                    "Duty specifications",
                    "Coordination protocols",
                    "Performance metrics"
                ],
                "validation_rules": [
                    "Agent roles clearly defined",
                    "Duties specified per agent",
                    "Coordination mechanisms documented",
                    "Performance tracking implemented"
                ]
            },
            "WSP_47": {
                "name": "Module Violation Tracking",
                "requirements": [
                    "Violation logging",
                    "Issue categorization",
                    "Resolution tracking",
                    "Prevention measures"
                ],
                "validation_rules": [
                    "Violation tracking system exists",
                    "Issues categorized properly",
                    "Resolution status tracked",
                    "Prevention measures documented"
                ]
            },
            "WSP_3": {
                "name": "Enterprise Domain Architecture",
                "requirements": [
                    "Functional distribution",
                    "Domain separation",
                    "Cross-domain dependencies",
                    "Scalability considerations"
                ],
                "validation_rules": [
                    "Modules distributed by function",
                    "No platform consolidation",
                    "Cross-domain dependencies documented",
                    "Scalable architecture maintained"
                ]
            }
        }
    
    async def validate_protocols(
        self, 
        protocols: List[str], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validates WSP protocols for a given context.
        
        Args:
            protocols: List of WSP protocols to validate
            context: Context information for validation
            
        Returns:
            Dict[str, Any]: Validation results and compliance status
        """
        try:
            validation_results = []
            
            for protocol in protocols:
                if protocol in self.protocol_definitions:
                    result = await self._validate_single_protocol(protocol, context)
                    validation_results.append(result)
                else:
                    logger.warning(f"Unknown protocol: {protocol}")
            
            # Aggregate results
            aggregated_results = self._aggregate_validation_results(validation_results)
            
            # Update validation history
            self._update_validation_history(protocols, context, aggregated_results)
            
            logger.info(f"Protocol validation completed for {len(protocols)} protocols")
            return aggregated_results
            
        except Exception as e:
            logger.error(f"Protocol validation failed: {e}")
            raise
    
    async def validate_module_compliance(
        self, 
        module_path: str, 
        protocols: List[str]
    ) -> Dict[str, Any]:
        """
        Validates WSP compliance for a specific module.
        
        Args:
            module_path: Path to the module for validation
            protocols: WSP protocols to validate
            
        Returns:
            Dict[str, Any]: Module compliance report
        """
        try:
            # Create module context
            module_context = {
                "module_path": module_path,
                "validation_type": "module_compliance",
                "timestamp": datetime.now()
            }
            
            # Validate protocols
            protocol_results = await self.validate_protocols(protocols, module_context)
            
            # Perform module-specific validations
            module_validations = await self._validate_module_structure(module_path, protocols)
            
            # Combine results
            compliance_results = {
                "status": protocol_results["status"],
                "violations": protocol_results["violations"] + module_validations["violations"],
                "recommendations": protocol_results["recommendations"] + module_validations["recommendations"],
                "module_specific": module_validations
            }
            
            logger.info(f"Module compliance validation completed for {module_path}")
            return compliance_results
            
        except Exception as e:
            logger.error(f"Module compliance validation failed: {e}")
            raise
    
    async def _validate_single_protocol(self, protocol: str, context: Dict[str, Any]) -> ValidationResult:
        """
        Validates a single WSP protocol.
        
        Args:
            protocol: Protocol to validate
            context: Validation context
            
        Returns:
            ValidationResult: Validation result for the protocol
        """
        protocol_def = self.protocol_definitions[protocol]
        violations = []
        recommendations = []
        
        # Simulate protocol validation (replace with actual validation logic)
        validation_rules = protocol_def["validation_rules"]
        
        for rule in validation_rules:
            # Simulate rule validation
            is_valid = await self._simulate_rule_validation(rule, context)
            
            if not is_valid:
                violations.append(f"Rule violation: {rule}")
                recommendations.append(f"Address: {rule}")
        
        # Calculate confidence based on validation results
        confidence = self._calculate_validation_confidence(violations, len(validation_rules))
        
        return ValidationResult(
            protocol=protocol,
            is_compliant=len(violations) == 0,
            violations=violations,
            recommendations=recommendations,
            confidence=confidence
        )
    
    async def _simulate_rule_validation(self, rule: str, context: Dict[str, Any]) -> bool:
        """
        Simulates rule validation for development purposes.
        
        Args:
            rule: Validation rule to check
            context: Validation context
            
        Returns:
            bool: True if rule passes validation, False otherwise
        """
        # Simulate validation delay
        import asyncio
        await asyncio.sleep(0.01)
        
        # Simulate validation results based on rule content
        if "exists" in rule.lower():
            return True  # Assume files exist for simulation
        elif "documented" in rule.lower():
            return True  # Assume documentation is present
        elif "specified" in rule.lower():
            return True  # Assume specifications are complete
        else:
            return True  # Default to passing for simulation
    
    def _calculate_validation_confidence(self, violations: List[str], total_rules: int) -> float:
        """
        Calculates confidence score for validation results.
        
        Args:
            violations: List of validation violations
            total_rules: Total number of validation rules
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        if total_rules == 0:
            return 0.0
        
        passed_rules = total_rules - len(violations)
        confidence = passed_rules / total_rules
        
        # Adjust confidence based on violation severity
        if violations:
            confidence *= 0.8  # Reduce confidence for any violations
        
        return max(confidence, 0.0)
    
    def _aggregate_validation_results(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """
        Aggregates validation results from multiple protocols.
        
        Args:
            results: List of validation results
            
        Returns:
            Dict[str, Any]: Aggregated validation data
        """
        aggregated = {
            "status": {},
            "violations": [],
            "recommendations": [],
            "overall_compliance": True,
            "confidence_avg": 0.0
        }
        
        total_confidence = 0.0
        
        for result in results:
            aggregated["status"][result.protocol] = result.is_compliant
            aggregated["violations"].extend(result.violations)
            aggregated["recommendations"].extend(result.recommendations)
            total_confidence += result.confidence
            
            if not result.is_compliant:
                aggregated["overall_compliance"] = False
        
        # Calculate average confidence
        if results:
            aggregated["confidence_avg"] = total_confidence / len(results)
        
        return aggregated
    
    async def _validate_module_structure(self, module_path: str, protocols: List[str]) -> Dict[str, Any]:
        """
        Validates module structure and organization.
        
        Args:
            module_path: Path to the module
            protocols: WSP protocols being validated
            
        Returns:
            Dict[str, Any]: Module structure validation results
        """
        violations = []
        recommendations = []
        
        # Simulate module structure validation
        required_files = ["README.md", "ModLog.md", "ROADMAP.md", "INTERFACE.md"]
        
        for file in required_files:
            # Simulate file existence check
            file_exists = await self._simulate_file_check(f"{module_path}/{file}")
            
            if not file_exists:
                violations.append(f"Missing required file: {file}")
                recommendations.append(f"Create {file} following WSP standards")
        
        return {
            "violations": violations,
            "recommendations": recommendations
        }
    
    async def _simulate_file_check(self, file_path: str) -> bool:
        """
        Simulates file existence check.
        
        Args:
            file_path: Path to check
            
        Returns:
            bool: True if file exists, False otherwise
        """
        # Simulate file check delay
        import asyncio
        await asyncio.sleep(0.01)
        
        # For simulation, assume files exist
        return True
    
    def _update_validation_history(
        self, 
        protocols: List[str], 
        context: Dict[str, Any], 
        results: Dict[str, Any]
    ):
        """Updates validation history."""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "protocols": protocols,
            "context": context,
            "results": results
        }
        
        self.validation_history.append(history_entry)
        
        # Keep only last 100 entries
        if len(self.validation_history) > 100:
            self.validation_history = self.validation_history[-100:]
    
    def get_validation_history(self) -> List[Dict[str, Any]]:
        """Returns validation history."""
        return self.validation_history.copy()
    
    def get_protocol_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Returns protocol definitions."""
        return self.protocol_definitions.copy() 