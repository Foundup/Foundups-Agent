import sys
from pathlib import Path

# Add project root to Python path (4 levels up from this test file)
test_file = Path(__file__).resolve()
project_root = test_file.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Test ComplianceAgent directly
print("Importing ComplianceAgent...")
from modules.infrastructure.compliance_agent.src.compliance_agent import ComplianceAgent

print("Creating ComplianceAgent...")
agent = ComplianceAgent(project_root)

print("Checking methods...")
methods = [method for method in dir(agent) if not method.startswith('_')]
print("Available methods:", methods)

if 'verify_readiness' in methods:
    print("SUCCESS: verify_readiness found!")
else:
    print("ERROR: verify_readiness not found!")
    
print("Testing verify_readiness...")
try:
    result = agent.verify_readiness()
    print(f"Result type: {type(result)}")
    print(f"Readiness: {result.readiness_status}")
except Exception as e:
    print(f"Error calling verify_readiness: {e}")