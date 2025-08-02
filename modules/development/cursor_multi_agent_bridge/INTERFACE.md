# Cursor Multi-Agent Bridge Interface Documentation

## **Public API Definition**

### **CursorWSPBridge Class**
Main interface for coordinating Cursor's multi-agent feature with WSP/WRE system.

#### **Constructor**
```python
CursorWSPBridge(config: Optional[Dict[str, Any]] = None)
```
- **config**: Optional configuration dictionary for bridge settings
- **Returns**: Initialized bridge instance

#### **Core Methods**

##### **activate_wsp_agents()**
Activates WSP 54 agents in Cursor workspace.
- **Parameters**: None
- **Returns**: Dict[str, bool] - Activation status for each agent
- **Error Handling**: Raises AgentActivationError if agents cannot be activated

##### **coordinate_development(task: str, wsp_protocols: List[str], cursor_agents: List[str])**
Coordinates autonomous development through Cursor agents.
- **Parameters**:
  - **task**: str - Development task description
  - **wsp_protocols**: List[str] - Required WSP protocols
  - **cursor_agents**: List[str] - Cursor agent types to coordinate
- **Returns**: Dict[str, Any] - Coordination results and agent responses
- **Error Handling**: Raises CoordinationError if agent coordination fails

##### **validate_wsp_compliance(module_path: str, protocols: List[str])**
Validates WSP compliance through Cursor agents.
- **Parameters**:
  - **module_path**: str - Path to module for validation
  - **protocols**: List[str] - WSP protocols to validate
- **Returns**: Dict[str, Any] - Compliance report with violations and recommendations
- **Error Handling**: Raises ValidationError if validation process fails

##### **get_agent_status()**
Returns current status of all Cursor-WSP agents.
- **Parameters**: None
- **Returns**: Dict[str, Dict[str, Any]] - Status information for each agent
- **Error Handling**: None

##### **update_agent_config(agent_type: str, config: Dict[str, Any])**
Updates configuration for specific agent type.
- **Parameters**:
  - **agent_type**: str - Type of agent to configure
  - **config**: Dict[str, Any] - New configuration settings
- **Returns**: bool - Success status
- **Error Handling**: Raises ConfigError if configuration is invalid

## **Parameter Specifications**

### **Agent Types**
- **compliance**: WSP protocol enforcement agent
- **documentation**: ModLog and README maintenance agent
- **testing**: Test coverage and validation agent
- **architecture**: Module structure compliance agent
- **code_review**: Code quality assessment agent
- **orchestrator**: Multi-agent coordination agent

### **WSP Protocols**
- **WSP_11**: Interface documentation standards
- **WSP_22**: ModLog and Roadmap protocol
- **WSP_54**: Agent duties specification
- **WSP_47**: Module violation tracking
- **WSP_3**: Enterprise domain architecture

## **Return Value Documentation**

### **Coordination Response**
```python
{
    "success": bool,
    "agent_responses": Dict[str, str],
    "wsp_compliance": Dict[str, bool],
    "execution_time": float,
    "errors": List[str],
    "recommendations": List[str]
}
```

### **Compliance Report**
```python
{
    "module_path": str,
    "protocols_checked": List[str],
    "compliance_status": Dict[str, bool],
    "violations": List[Dict[str, Any]],
    "recommendations": List[str],
    "score": float
}
```

## **Error Handling**

### **AgentActivationError**
Raised when WSP agents cannot be activated in Cursor workspace.
- **Error Code**: ACT001
- **Recovery**: Retry activation or check Cursor agent availability

### **CoordinationError**
Raised when agent coordination fails during development tasks.
- **Error Code**: COORD001
- **Recovery**: Check agent status and retry coordination

### **ValidationError**
Raised when WSP compliance validation fails.
- **Error Code**: VAL001
- **Recovery**: Review module structure and protocol requirements

### **ConfigError**
Raised when agent configuration is invalid.
- **Error Code**: CONFIG001
- **Recovery**: Validate configuration parameters

## **Examples**

### **Basic Agent Activation**
```python
bridge = CursorWSPBridge()
status = bridge.activate_wsp_agents()
print(f"Agents activated: {status}")
```

### **Development Coordination**
```python
result = await bridge.coordinate_development(
    task="Create new module with WSP compliance",
    wsp_protocols=["WSP_11", "WSP_22", "WSP_54"],
    cursor_agents=["compliance", "documentation", "testing"]
)
```

### **Compliance Validation**
```python
report = await bridge.validate_wsp_compliance(
    module_path="modules/new_module",
    protocols=["WSP_11", "WSP_22"]
)
if report["score"] < 0.8:
    print("Compliance issues detected")
``` 