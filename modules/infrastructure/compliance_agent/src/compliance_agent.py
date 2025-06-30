from pathlib import Path
import os

class ComplianceAgent:
    def __init__(self):
        """Initializes the Compliance Agent."""
        print("ComplianceAgent initialized.")
        self.errors = []

    def _check_directory_structure(self, module_path: Path):
        """Duty 1: Verify 'src' and 'tests' subdirectories exist."""
        if not (module_path / "src").is_dir():
            self.errors.append(f"Missing 'src' directory in {module_path}")
        if not (module_path / "tests").is_dir():
            self.errors.append(f"Missing 'tests' directory in {module_path}")

    def _check_mandatory_files(self, module_path: Path):
        """Duty 2: Ensure mandatory files exist."""
        required_files = ["README.md", "__init__.py"]
        for f in required_files:
            if not (module_path / f).is_file():
                self.errors.append(f"Missing mandatory file: {f} in {module_path}")
        
        # WSP-54 implies tests/README.md is also mandatory via ModuleScaffoldingAgent spec
        if not (module_path / "tests" / "README.md").is_file():
            self.errors.append(f"Missing mandatory file: tests/README.md in {module_path}")


    def _check_test_file_correspondence(self, module_path: Path):
        """Duty 3: For every .py file in src, verify a corresponding test_*.py exists."""
        src_path = module_path / "src"
        tests_path = module_path / "tests"

        if not src_path.is_dir() or not tests_path.is_dir():
            return # Avoid errors if directories are missing, handled by other checks

        for src_file in src_path.glob('**/*.py'):
            # Ignore __init__.py files for this check
            if src_file.name == '__init__.py':
                continue
            
            relative_path = src_file.relative_to(src_path)
            test_file_name = f"test_{relative_path.name}"
            expected_test_path = tests_path / relative_path.with_name(test_file_name)

            if not expected_test_path.exists():
                self.errors.append(f"Missing test file for '{src_file.name}'. Expected at '{expected_test_path}'")

    def run_check(self, module_path_str: str) -> dict:
        """
        Runs a full WSP compliance check on a given module directory.
        
        Args:
            module_path_str: The string path to the module to be checked.

        Returns:
            A dictionary containing the compliance status and a list of errors.
        """
        print(f"ComplianceAgent: Running compliance check on '{module_path_str}'...")
        self.errors = []
        module_path = Path(module_path_str)

        if not module_path.is_dir():
            return {
                "compliant": False,
                "errors": [f"Module path does not exist or is not a directory: {module_path_str}"]
            }

        self._check_directory_structure(module_path)
        self._check_mandatory_files(module_path)
        self._check_test_file_correspondence(module_path)

        # Duty 4 is noted as future/dependent on other WSPs, so it's not implemented yet.

        is_compliant = len(self.errors) == 0

        if is_compliant:
            print(f"ComplianceAgent: '{module_path_str}' is compliant.")
        else:
            print(f"ComplianceAgent: '{module_path_str}' is NOT compliant. Found {len(self.errors)} errors.")
            for error in self.errors:
                print(f"  - {error}")

        return {
            "compliant": is_compliant,
            "errors": self.errors
        }