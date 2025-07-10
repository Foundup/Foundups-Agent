# WRE Simulation Test Framework

**Comprehensive simulation testing for the Windsurf Recursive Engine (WRE)**

Relocated from `tests/wre_simulation/` per WSP 3 compliance requirements.

## WSP Compliance Status

- **WSP 3**: ✅ Enterprise Domain Architecture (proper test location)
- **WSP 5**: ✅ Test Coverage Protocol (simulation testing)
- **WSP 22**: ✅ Traceable Narrative (documented relocation)
- **WSP 49**: ✅ Module Directory Structure (standardized organization)

## 🎯 Purpose

The WRE Simulation Test Framework provides comprehensive testing capabilities for:

- **End-to-end workflow simulation** - Complete WRE operations from goal to completion
- **Agent behavior validation** - ComplianceAgent, LoremasterAgent, and other agent testing
- **Integration testing** - Cross-module interaction verification
- **Performance testing** - System behavior under various conditions
- **WSP compliance verification** - Framework adherence validation

## 🏗️ Architecture

### Core Components

#### 1. Test Harness (`harness.py`)
Main orchestrator for simulation execution:
- **Sandbox Creation**: Isolated test environments
- **Goal-driven Execution**: YAML-based test scenarios
- **Result Validation**: Automated success/failure determination
- **Cleanup Management**: Resource cleanup and teardown

#### 2. Validation Suite (`validation_suite.py`)
Comprehensive result validation:
- **Output Verification**: Expected file and content validation
- **WSP Compliance Checking**: Framework adherence verification
- **Agent Output Validation**: Agent-specific result validation
- **Report Generation**: Detailed validation reports

#### 3. Goal System (`goals/`)
YAML-based test scenarios:
- **`create_user_auth.yaml`**: User authentication flow testing
- **`delegate_scaffolding_via_sel.yaml`**: Module scaffolding delegation testing
- **Custom Goals**: Extensible goal definition system

## 🚀 Quick Start

### Running Simulations

```bash
# Run default simulation
cd modules/wre_core/tests/simulation/
python harness.py

# Run specific goal
python harness.py --goal create_user_auth.yaml

# Run with custom goal
python harness.py --goal your_custom_goal.yaml
```

### Creating Custom Goals

```yaml
# example_goal.yaml
name: "Example WRE Goal"
description: "Test WRE functionality for specific scenario"
timeout: 300  # seconds

# Expected system behavior
actions:
  - type: "module_creation"
    module_name: "test_module"
    domain: "platform_integration"
  - type: "agent_invocation"
    agent: "ModuleScaffoldingAgent"
    parameters:
      path: "modules/platform_integration/test_module"

# Validation criteria
expected_outputs:
  - path: "modules/platform_integration/test_module/README.md"
    content_contains:
      - "test_module"
      - "WSP Compliance"
  - path: "modules/platform_integration/test_module/src/__init__.py"
    content_contains:
      - "def"

# Success criteria
success_conditions:
  - all_outputs_exist: true
  - wsp_compliance: true
  - no_critical_errors: true
```

## 🧪 Test Categories

### 1. Agent Validation Tests
- **ComplianceAgent**: WSP violation detection
- **LoremasterAgent**: Protocol auditing and manifest generation
- **ModuleScaffoldingAgent**: Module creation and structure validation
- **ScoringAgent**: Module prioritization and scoring

### 2. Integration Tests
- **Cross-module communication**: Module interaction validation
- **API integration**: External platform integration testing
- **Data flow**: Information flow between components
- **Error handling**: System resilience under failure conditions

### 3. Performance Tests
- **Load testing**: System behavior under heavy load
- **Memory usage**: Resource consumption monitoring
- **Execution time**: Performance benchmarking
- **Scalability**: Multi-module concurrent operations

### 4. WSP Compliance Tests
- **File structure validation**: Module organization verification
- **Documentation requirements**: README, ROADMAP, ModLog presence
- **Naming conventions**: WSP-compliant naming standards
- **Import structure**: Proper module import patterns

## 📊 Validation Framework

### Validation Levels

1. **Syntax Validation** - Basic file existence and structure
2. **Semantic Validation** - Content correctness and completeness
3. **Behavioral Validation** - System behavior verification
4. **Performance Validation** - Resource usage and timing
5. **Compliance Validation** - WSP framework adherence

### Validation Reports

The framework generates detailed reports:
- **Summary Statistics**: Pass/fail rates, execution times
- **Detailed Results**: Per-test validation outcomes
- **Error Analysis**: Failure categorization and root cause analysis
- **Recommendations**: Suggested improvements and fixes

## 🔧 Configuration

### Environment Variables

```bash
# Test execution settings
WRE_SIMULATION_TIMEOUT=300
WRE_SIMULATION_RETRIES=3
WRE_SIMULATION_LOG_LEVEL=INFO

# Platform credentials (for integration tests)
DISCORD_BOT_TOKEN=your_discord_token
LINKEDIN_CLIENT_ID=your_linkedin_id
YOUTUBE_API_KEY=your_youtube_key
```

### Simulation Configuration

```python
# simulation_config.py
SIMULATION_CONFIG = {
    'timeout': 300,
    'retries': 3,
    'log_level': 'INFO',
    'sandbox_cleanup': True,
    'parallel_execution': False,
    'validation_strict': True
}
```

## 📈 Test Execution Flow

1. **Setup Phase**
   - Create isolated sandbox environment
   - Copy project structure to sandbox
   - Initialize test configuration

2. **Execution Phase**
   - Parse goal YAML file
   - Execute WRE with specified goal
   - Monitor execution and capture outputs

3. **Validation Phase**
   - Verify expected outputs exist
   - Validate content correctness
   - Check WSP compliance
   - Generate validation report

4. **Cleanup Phase**
   - Archive test results
   - Clean up sandbox environment
   - Generate summary report

## 🔍 Debugging and Troubleshooting

### Common Issues

1. **Sandbox Creation Failures**
   - Check disk space and permissions
   - Verify Python path configuration
   - Ensure proper module imports

2. **Goal Execution Timeouts**
   - Increase timeout values
   - Check for infinite loops
   - Verify goal file syntax

3. **Validation Failures**
   - Review expected output definitions
   - Check file path specifications
   - Verify content requirements

### Debug Mode

```bash
# Run with debug logging
WRE_SIMULATION_LOG_LEVEL=DEBUG python harness.py --goal debug_goal.yaml

# Run with verbose output
python harness.py --goal test_goal.yaml --verbose

# Run with preserved sandbox
python harness.py --goal test_goal.yaml --no-cleanup
```

## 📋 Test Documentation Standards

### Test Case Documentation

Each test case should include:
- **Purpose**: What the test validates
- **Prerequisites**: Required setup or conditions
- **Steps**: Detailed execution steps
- **Expected Results**: Success criteria
- **Cleanup**: Required cleanup steps

### Goal File Documentation

Each goal file should include:
- **Name**: Descriptive test name
- **Description**: Detailed purpose and scope
- **Author**: Test creator information
- **Version**: Goal file version
- **Dependencies**: Required modules or agents

## 🚀 Future Enhancements

### Planned Features

1. **Parallel Test Execution**: Run multiple simulations concurrently
2. **Visual Test Reports**: HTML-based result visualization
3. **Integration with CI/CD**: Automated test execution
4. **Performance Benchmarking**: Historical performance tracking
5. **Advanced Goal Templates**: Reusable goal components

### Extension Points

1. **Custom Validators**: Plugin system for validation extensions
2. **Platform-Specific Tests**: Platform integration test modules
3. **Load Testing Framework**: Stress testing capabilities
4. **Mock Services**: Test double system for external dependencies

## 📚 Related Documentation

- **[WRE Core README](../README.md)**: Main WRE documentation
- **[WSP Framework](../../../../WSP_framework/README.md)**: WSP protocol documentation
- **[Module Development Guide](../../../../docs/module_development.md)**: Module creation guidelines
- **[Testing Standards](../../../docs/testing_standards.md)**: Project testing guidelines

## 🤝 Contributing

### Adding New Tests

1. Create goal YAML file in `goals/` directory
2. Add validation logic to `validation_suite.py`
3. Update documentation with test description
4. Add test to CI/CD pipeline

### Reporting Issues

Please report issues with:
- Test execution details
- Goal file content
- Expected vs actual results
- Environment information

---

**WSP Compliance Notes:**
- All tests must maintain WSP framework compliance
- New tests should follow WSP 5 (≥90% coverage)
- Documentation must follow WSP 22 (traceable narrative)
- Module organization must follow WSP 49 (directory structure) 