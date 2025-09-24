# Module Health Interface

## Public API

### Size Auditing

```python
class SizeAuditor:
    """Audits file sizes against WSP 87 thresholds"""

    def __init__(self, thresholds: Optional[Dict[str, int]] = None):
        """
        Initialize with optional custom thresholds

        Args:
            thresholds: Dict with 'optimal', 'warning', 'critical' keys
        """

    def audit_file(self, file_path: Path) -> SizeAuditResult:
        """
        Audit single file size

        Returns:
            SizeAuditResult with size and severity
        """

    def audit_module(self, module_path: Path) -> List[SizeAuditResult]:
        """
        Audit all files in module

        Returns:
            List of audit results for files exceeding thresholds
        """

    def audit_codebase(self, root_path: Path) -> ModuleHealthReport:
        """
        Comprehensive codebase audit

        Returns:
            Full health report with statistics
        """

    def suggest_refactoring(self, file_path: Path) -> RefactoringSuggestions:
        """
        Generate refactoring suggestions for large file

        Returns:
            Suggestions for splitting/organizing file
        """
```

### Structure Auditing

```python
class StructureAuditor:
    """Validates module structure per WSP 49"""

    def __init__(self, requirements: Optional[List[str]] = None):
        """
        Initialize with optional custom requirements

        Args:
            requirements: List of required files/directories
        """

    def validate_module(self, module_path: Path) -> StructureValidationResult:
        """
        Validate single module structure

        Returns:
            Validation result with compliance status
        """

    def validate_domain(self, domain_path: Path) -> List[StructureValidationResult]:
        """
        Validate all modules in domain

        Returns:
            List of validation results
        """

    def generate_scaffold(self, module_path: Path) -> ScaffoldResult:
        """
        Generate missing structure elements

        Returns:
            Result with created elements
        """

    def check_compliance(self, path: Path) -> ComplianceReport:
        """
        Full WSP 49 compliance check

        Returns:
            Detailed compliance report
        """
```

### Data Structures

```python
@dataclass
class SizeAuditResult:
    """Result of file size audit"""
    file_path: Path
    line_count: int
    severity: str  # 'optimal', 'acceptable', 'warning', 'critical'
    message: str
    suggested_action: Optional[str]
```

```python
@dataclass
class StructureValidationResult:
    """Result of structure validation"""
    module_path: Path
    required_elements: List[str]
    present_elements: List[str]
    missing_elements: List[str]
    compliance_level: str  # 'full', 'partial', 'violation'
    wsp_compliant: bool
```

```python
@dataclass
class ModuleHealthReport:
    """Comprehensive health report"""
    total_files: int
    files_by_severity: Dict[str, int]
    largest_files: List[Tuple[Path, int]]
    refactoring_candidates: List[Path]
    size_distribution: Dict[str, float]
    overall_health: str  # 'excellent', 'good', 'fair', 'poor'
```

```python
@dataclass
class RefactoringSuggestions:
    """Suggestions for file refactoring"""
    file_path: Path
    current_size: int
    suggested_splits: List[SplitSuggestion]
    extractable_classes: List[str]
    extractable_functions: List[str]
    complexity_hotspots: List[CodeSection]
```

```python
@dataclass
class HealthNotice:
    """Health warning for integration"""
    wsp_protocol: str
    check_type: str  # 'size', 'structure', 'documentation'
    severity: str    # 'info', 'warning', 'critical'
    message: str
    fix_command: Optional[str]
```

## Usage Examples

### Basic Size Audit

```python
from holo_index.module_health import SizeAuditor

auditor = SizeAuditor()

# Audit single file
result = auditor.audit_file("modules/example/src/large_file.py")
if result.severity == 'warning':
    print(f"Warning: {result.file_path} has {result.line_count} lines")
    print(f"Action: {result.suggested_action}")

# Audit entire module
issues = auditor.audit_module("modules/example")
for issue in issues:
    if issue.severity in ['warning', 'critical']:
        print(f"{issue.severity.upper()}: {issue.message}")
```

### Structure Validation

```python
from holo_index.module_health import StructureAuditor

auditor = StructureAuditor()

# Validate module
result = auditor.validate_module("modules/example")
if not result.wsp_compliant:
    print(f"WSP 49 Violation: Missing {result.missing_elements}")

# Generate missing structure
if result.missing_elements:
    scaffold = auditor.generate_scaffold("modules/example")
    print(f"Created: {scaffold.created_elements}")
```

### Health Integration

```python
from holo_index.module_health import generate_health_notices

# Generate notices for HoloIndex
notices = generate_health_notices("modules/")

# Format for display
for notice in notices:
    print(f"[{notice.wsp_protocol}] [{notice.severity.upper()}] {notice.message}")
    if notice.fix_command:
        print(f"    FIX: {notice.fix_command}")
```

### Refactoring Suggestions

```python
from holo_index.module_health import SizeAuditor

auditor = SizeAuditor()

# Get refactoring suggestions
suggestions = auditor.suggest_refactoring("modules/large_module.py")

print(f"File: {suggestions.file_path} ({suggestions.current_size} lines)")
print("\nSuggested Splits:")
for split in suggestions.suggested_splits:
    print(f"  - {split.name}: Lines {split.start_line}-{split.end_line}")

print("\nExtractable Classes:")
for cls in suggestions.extractable_classes:
    print(f"  - {cls}")
```

### Comprehensive Health Check

```python
from holo_index.module_health import run_health_check

# Full health check
report = run_health_check("modules/")

print(f"Overall Health: {report.overall_health}")
print(f"Total Files: {report.total_files}")
print("\nSize Distribution:")
for category, percentage in report.size_distribution.items():
    print(f"  {category}: {percentage:.1%}")

print("\nRefactoring Candidates:")
for candidate in report.refactoring_candidates[:5]:
    print(f"  - {candidate}")
```

## Integration with HoloIndex

### Automatic Health Checking

Health checks run automatically during searches:

```python
# In HoloIndex search results
{
    'code': [...],
    'wsps': [...],
    'health_notices': [
        {
            'wsp_protocol': 'WSP 87',
            'severity': 'warning',
            'message': 'file.py approaching size limit (879 lines)',
            'fix_command': 'Consider refactoring file.py'
        }
    ]
}
```

### CLI Integration

```bash
# Run standalone health check
python holo_index.py --health-check modules/

# Include health in search
python holo_index.py --search "query" --include-health
```

## Configuration

### Custom Thresholds

```python
auditor = SizeAuditor(thresholds={
    'optimal': 400,
    'warning': 700,
    'critical': 900
})
```

### Custom Requirements

```python
auditor = StructureAuditor(requirements=[
    'README.md',
    'INTERFACE.md',
    'ModLog.md',
    'src/',
    'tests/',
    'docs/',
    'requirements.txt'
])
```

## Error Handling

Methods may raise:
- `FileNotFoundError`: Path doesn't exist
- `PermissionError`: Can't read file/directory
- `ValueError`: Invalid thresholds or requirements

## WSP Compliance

- **WSP 87**: Code Navigation Protocol (size limits)
- **WSP 49**: Module Directory Structure
- **WSP 11**: Complete interface documentation
- **WSP 22**: Documentation requirements