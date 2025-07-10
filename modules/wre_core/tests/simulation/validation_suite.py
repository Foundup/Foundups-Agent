"""
WRE Simulation Validation Suite

Validation functions for WRE simulation test results.
Relocated from tests/wre_simulation/ per WSP 3 compliance requirements.

WSP Compliance:
- WSP 3: Enterprise Domain Architecture (proper test location)
- WSP 5: Test Coverage Protocol (validation testing)
- WSP 22: Traceable Narrative (documented relocation)
"""

from pathlib import Path
from typing import Dict, List, Any
import json
import yaml


def validate_simulation_output(sandbox_path: Path, goal_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate the output of a WRE simulation against expected results.
    
    Args:
        sandbox_path: Path to the sandbox directory
        goal_data: The goal configuration data
        
    Returns:
        Dictionary with validation results
    """
    validation_result = {
        'success': True,
        'errors': [],
        'warnings': [],
        'validated_items': []
    }
    
    try:
        # Check if goal was processed
        if 'expected_outputs' in goal_data:
            for expected_output in goal_data['expected_outputs']:
                if not _validate_expected_output(sandbox_path, expected_output, validation_result):
                    validation_result['success'] = False
        
        # Check for WSP compliance in generated files
        if not _validate_wsp_compliance(sandbox_path, validation_result):
            validation_result['success'] = False
            
        # Check for proper module structure
        if not _validate_module_structure(sandbox_path, validation_result):
            validation_result['success'] = False
            
    except Exception as e:
        validation_result['success'] = False
        validation_result['errors'].append(f"Validation error: {str(e)}")
    
    return validation_result


def _validate_expected_output(sandbox_path: Path, expected_output: Dict[str, Any], 
                             validation_result: Dict[str, Any]) -> bool:
    """Validate a specific expected output."""
    output_path = sandbox_path / expected_output.get('path', '')
    
    if not output_path.exists():
        validation_result['errors'].append(f"Expected output not found: {output_path}")
        return False
    
    # Validate file content if specified
    if 'content_contains' in expected_output:
        try:
            content = output_path.read_text(encoding='utf-8')
            for required_text in expected_output['content_contains']:
                if required_text not in content:
                    validation_result['errors'].append(
                        f"Required text '{required_text}' not found in {output_path}"
                    )
                    return False
        except Exception as e:
            validation_result['errors'].append(f"Error reading {output_path}: {e}")
            return False
    
    validation_result['validated_items'].append(f"✅ {output_path}")
    return True


def _validate_wsp_compliance(sandbox_path: Path, validation_result: Dict[str, Any]) -> bool:
    """Validate WSP compliance in generated files."""
    success = True
    
    # Check for required documentation files
    required_docs = ['README.md', 'ROADMAP.md', 'ModLog.md']
    
    # Find all module directories
    modules_dir = sandbox_path / 'modules'
    if modules_dir.exists():
        for domain_dir in modules_dir.iterdir():
            if domain_dir.is_dir():
                for module_dir in domain_dir.iterdir():
                    if module_dir.is_dir():
                        for doc_file in required_docs:
                            doc_path = module_dir / doc_file
                            if doc_path.exists():
                                validation_result['validated_items'].append(f"✅ {doc_path}")
                            else:
                                validation_result['warnings'].append(f"Missing documentation: {doc_path}")
    
    return success


def _validate_module_structure(sandbox_path: Path, validation_result: Dict[str, Any]) -> bool:
    """Validate proper module structure."""
    success = True
    
    # Check for proper module structure
    modules_dir = sandbox_path / 'modules'
    if not modules_dir.exists():
        validation_result['errors'].append("Missing modules directory")
        return False
    
    # Validate enterprise domain structure
    expected_domains = ['ai_intelligence', 'communication', 'platform_integration', 
                       'infrastructure', 'gamification', 'blockchain', 'foundups']
    
    for domain in expected_domains:
        domain_path = modules_dir / domain
        if domain_path.exists():
            validation_result['validated_items'].append(f"✅ Domain: {domain}")
        else:
            validation_result['warnings'].append(f"Missing domain: {domain}")
    
    return success


def validate_agent_output(agent_name: str, output_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate output from a specific WRE agent.
    
    Args:
        agent_name: Name of the agent
        output_data: The output data from the agent
        
    Returns:
        Dictionary with validation results
    """
    validation_result = {
        'success': True,
        'errors': [],
        'warnings': [],
        'validated_items': []
    }
    
    # Agent-specific validation
    if agent_name == 'ComplianceAgent':
        if 'findings' not in output_data:
            validation_result['errors'].append("ComplianceAgent missing 'findings' field")
            validation_result['success'] = False
        else:
            validation_result['validated_items'].append("✅ ComplianceAgent findings present")
    
    elif agent_name == 'LoremasterAgent':
        required_fields = ['status', 'protocols_found', 'findings']
        for field in required_fields:
            if field not in output_data:
                validation_result['errors'].append(f"LoremasterAgent missing '{field}' field")
                validation_result['success'] = False
            else:
                validation_result['validated_items'].append(f"✅ LoremasterAgent {field} present")
    
    elif agent_name == 'ModuleScaffoldingAgent':
        if 'created_files' not in output_data:
            validation_result['warnings'].append("ModuleScaffoldingAgent missing 'created_files' field")
        else:
            validation_result['validated_items'].append("✅ ModuleScaffoldingAgent created_files present")
    
    return validation_result


def generate_validation_report(validation_results: List[Dict[str, Any]]) -> str:
    """
    Generate a comprehensive validation report.
    
    Args:
        validation_results: List of validation result dictionaries
        
    Returns:
        Formatted validation report string
    """
    report = []
    report.append("# WRE Simulation Validation Report")
    report.append("=" * 50)
    report.append("")
    
    total_tests = len(validation_results)
    passed_tests = sum(1 for result in validation_results if result['success'])
    failed_tests = total_tests - passed_tests
    
    report.append(f"## Summary")
    report.append(f"- Total Tests: {total_tests}")
    report.append(f"- Passed: {passed_tests}")
    report.append(f"- Failed: {failed_tests}")
    report.append(f"- Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    report.append("")
    
    for i, result in enumerate(validation_results, 1):
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        report.append(f"## Test {i}: {status}")
        
        if result['validated_items']:
            report.append("### Validated Items:")
            for item in result['validated_items']:
                report.append(f"- {item}")
        
        if result['warnings']:
            report.append("### Warnings:")
            for warning in result['warnings']:
                report.append(f"- ⚠️ {warning}")
        
        if result['errors']:
            report.append("### Errors:")
            for error in result['errors']:
                report.append(f"- ❌ {error}")
        
        report.append("")
    
    return "\n".join(report) 