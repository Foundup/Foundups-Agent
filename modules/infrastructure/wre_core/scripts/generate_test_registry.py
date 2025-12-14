import os
import json
import ast
from pathlib import Path
from typing import Dict, List, Any

# Configuration
REPO_ROOT = Path(__file__).resolve().parents[4] # Adjust based on depth
REGISTRY_PATH = REPO_ROOT / "WSP_knowledge" / "WSP_Test_Registry.json"
EXCLUDE_DIRS = {".git", ".vscode", ".idea", "__pycache__", "node_modules", "env", "venv", ".venv", "site-packages", ".gemini", ".claude"}

def scan_for_tests(root_dir: Path) -> List[Dict[str, Any]]:
    """Scan directory for test files and extract metadata."""
    tests = []
    
    for root, dirs, files in os.walk(root_dir):
        # Filter excludes
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                full_path = Path(root) / file
                rel_path = full_path.relative_to(root_dir)
                
                metadata = extract_test_metadata(full_path)
                if metadata:
                    tests.append({
                        "id": file.replace(".py", ""),
                        "path": str(rel_path).replace("\\", "/"),
                        "description": metadata.get("docstring", "No description provided"),
                        "capabilities": metadata.get("capabilities", []),
                        "execution_type": metadata.get("execution_type", "unknown")
                    })
    return tests

def extract_test_metadata(file_path: Path) -> Dict[str, Any]:
    """Parse python file to extract docstrings and potential capabilities."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
            
        docstring = ast.get_docstring(tree)
        
        # Simple heuristics for capabilities
        capabilities = []
        execution_type = "unit"
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "selenium" in content or "webdriver" in content:
                capabilities.append("browser_automation")
                execution_type = "integration"
            if "GeminiVision" in content or "vision_analyzer" in content:
                capabilities.append("computer_vision")
                capabilities.append("vision_bridge")
                execution_type = "e2e_vision"
            if "tkinter" in content or "messagebox" in content:
                capabilities.append("interactive_feedback")
                capabilities.append("012_protocol")
                
        return {
            "docstring": docstring.strip() if docstring else None,
            "capabilities": capabilities,
            "execution_type": execution_type
        }
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None

def main():
    log_path = REPO_ROOT / "registry_debug.log"
    
    try:
        with open(log_path, "w", encoding="utf-8") as log:
            def log_msg(msg):
                print(msg)
                log.write(msg + "\n")
            
            log_msg(f"Scanning for tests in: {REPO_ROOT}")
            
            try:
                tests = scan_for_tests(REPO_ROOT)
                log_msg(f"Found {len(tests)} tests.")
            except Exception as e:
                log_msg(f"Scan failed: {e}")
                raise

            registry = {
                "version": "1.0",
                "last_updated": "2025-12-06",
                "schema": "WSP_98_Test_Registry",
                "total_tests": len(tests),
                "tests": tests
            }
            
            # Ensure directory exists
            REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
            
            with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
                json.dump(registry, f, indent=2)
                
            log_msg(f"Registry generated at: {REGISTRY_PATH}")

    except Exception as e:
        print(f"FATAL ERROR: {e}")

if __name__ == "__main__":
    main()
