# WSP 9: Project Configuration Standard
- **Status:** Draft
- **Purpose:** To define a project-specific configuration file (`.foundups_project_rules`) for customizing WSP procedures and settings.
- **Trigger:** When the WRE Orchestrator starts an operation within a FoundUp project.
- **Input:** The `.foundups_project_rules` file from a project's root directory.
- **Output:** A set of project-specific rules that override global WSP defaults for the current operation.
- **Responsible Agent(s):** WRE Orchestrator

This protocol defines the standard for a project-specific configuration file, `.foundups_project_rules`. This file allows for the customization of certain WSP procedures, LLME configurations, and other project-level settings to tailor the WRE's behavior for a specific FoundUp.

**Note:** This protocol is in a draft state. The full template and documentation will be populated in future iterations.

## 2. File Location and Naming

-   **Filename**: `.foundups_project_rules`
-   **Location**: At the root of a specific FoundUp project, likely within `modules/foundups/<project_name>/`.

## 3. Configuration Schema (Proposed)

The configuration file will use the YAML format.

```yaml
# .foundups_project_rules template
project:
  name: "[Project Name]"
  version: "[Version]"
  
rules:
  # [Project-specific rules to be defined]
  # Example:
  #   - require_manual_approval_for_deploys: true
  
llme:
  # [LLME-specific configurations to be defined]
  # Example:
  #   - custom_llme_thresholds:
  #       emergent: 2.5
  
wsp:
  # [WSP procedure customizations to be defined]
  # Example:
  #   - override_wsp_6_coverage_target: 85
```

## 4. Usage Guidelines

*(This section will be defined in a future version.)*

The `WRE Orchestrator` will be responsible for locating and parsing this file at the start of any operation within a FoundUp project. If the file exists, its rules will override the global WSP defaults for that specific operation. 