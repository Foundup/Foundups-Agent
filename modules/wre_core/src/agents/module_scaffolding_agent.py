import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ModuleScaffoldingAgent:
    """
    An agent responsible for creating the standard directory and file structure for new modules.
    """
    def __init__(self, module_path, module_name):
        """
        Initializes the agent with the target path and name for the new module.

        Args:
            module_path (str): The full path from the project root where the module will be created (e.g., 'modules/new_feature').
            module_name (str): The descriptive name of the module (e.g., 'NewFeature').
        """
        self.root_path = Path(module_path)
        self.module_name = module_name
        self.agent_file_name = f"{self.module_name.lower().replace(' ', '_')}_agent.py"

    def execute(self):
        """
        Executes the scaffolding process.
        """
        logging.info(f"Executing scaffolding for module: '{self.module_name}' at {self.root_path}")
        try:
            self._create_directories()
            self._create_files()
            logging.info(f"✅ Successfully scaffolded module '{self.module_name}'.")
            return True
        except Exception as e:
            logging.error(f"❌ Failed to scaffold module '{self.module_name}'. Reason: {e}")
            return False

    def _create_directories(self):
        """Creates the necessary directories for the module."""
        src_path = self.root_path / "src"
        src_path.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created directory: {src_path}")

    def _create_files(self):
        """Creates the standard placeholder files for the module."""
        files_to_create = {
            self.root_path / "__init__.py": "",
            self.root_path / "README.md": f"# {self.module_name}\\n\\nThis module is responsible for...",
            self.root_path / "src" / self.agent_file_name: self._get_agent_template(),
            self.root_path / "src" / "__init__.py": "",
        }

        for file_path, content in files_to_create.items():
            if not file_path.exists():
                file_path.write_text(content, encoding='utf-8')
                logging.info(f"Created file: {file_path}")

    def _get_agent_template(self):
        """Returns the template for the main agent file."""
        class_name = "".join(word.capitalize() for word in self.module_name.split(' ')) + "Agent"
        return f"""class {class_name}:
    def __init__(self):
        print("Initializing {class_name}...")

    def run(self):
        print("{class_name} is running.")
"""

if __name__ == '__main__':
    # Example usage for standalone testing
    print("Running ModuleScaffoldingAgent standalone test...")
    test_module_name = "Example Test"
    test_module_path = f"modules/testing/{test_module_name.lower().replace(' ', '_')}"
    
    scaffolder = ModuleScaffoldingAgent(module_path=test_module_path, module_name=test_module_name)
    scaffolder.execute()
    print("\\nTo clean up, manually delete the 'modules/testing' directory.") 