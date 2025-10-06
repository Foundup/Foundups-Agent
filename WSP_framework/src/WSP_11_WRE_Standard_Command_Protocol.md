# WSP 11: WRE Standard Command Protocol
- **Status:** Active
- **Purpose:** To define the high-level, standardized command set for interacting with the Windsurf Recursive Engine (WRE) and standardized interactive interface patterns for modules.
- **Trigger:** When a user or agent issues a command to the WRE or interacts with module interfaces.
- **Input:** A standardized command (e.g., `go`, `fix`, `save`) or interactive interface input.
- **Output:** The execution of the corresponding WRE core functionality or module operation.
- **Responsible Agent(s):** WRE Orchestrator, Module Interfaces

This protocol defines the Standard Command Set for the Windsurf Recursive Engine (WRE) and Interactive Interface Standards for modules. These commands and interfaces provide a high-level, standardized interface for users and other agents to interact with the WRE's core functionalities and individual modules.

## 1. Interactive Interface Standards (WSP 11.1)

### 1.1 Numbered Command Interface Pattern
All modules that provide standalone interactive interfaces MUST implement a numbered command system for enhanced usability and consistency.

**Standard Pattern:**
```
[U+1F3AF] [Module Name] Interactive Mode
Available commands:
  1. status     - Show current status
  2. [command]  - [Description]
  3. [command]  - [Description]
  4. [command]  - [Description]
  5. [command]  - [Description]
  6. quit       - Exit

Enter command number (1-N) or command name:
Press Ctrl+C or type 'N' or 'quit' to exit
```

### 1.2 Interface Requirements

#### **Dual Input Support**
- **MUST** accept both numbered input (1, 2, 3...) and text commands (status, auth, quit)
- **MUST** provide clear error messages for invalid inputs
- **SHOULD** offer command suggestions for typos

#### **Standard Commands**
- **Position 1**: Always `status` - Show current operational status
- **Last Position**: Always `quit` - Exit interactive mode
- **Middle Positions**: Module-specific functionality commands

#### **Output Standards**
- **MUST** use consistent emoji prefixes for each module type
- **MUST** provide clear, actionable output for each command
- **SHOULD** include helpful context and next steps

### 1.3 Module-Specific Implementations

#### **[U+1F3AC] YouTube Proxy** (`youtube_proxy`)
```
[U+1F3AC] YouTube Proxy Interactive Mode
Available commands:
  1. status     - Show current status
  2. stream     - Show stream info
  3. components - List active components
  4. connect    - Connect to stream
  5. quit       - Exit
```

#### **[U+1F4BC] LinkedIn Agent** (`linkedin_agent`)
```
[U+1F4BC] LinkedIn Agent Interactive Mode
Available commands:
  1. status     - Show current status
  2. auth       - Test authentication
  3. profile    - Show profile info
  4. posts      - Show pending posts
  5. generate   - Generate test content
  6. quit       - Exit
```

#### **[U+1F426] X/Twitter DAE** (`x_twitter`)
```
[U+1F426] X/Twitter DAE Interactive Mode
Available commands:
  1. status     - Show DAE status
  2. auth       - Test authentication
  3. identity   - Show DAE identity
  4. post       - Generate test post
  5. engage     - Test engagement
  6. quit       - Exit
```

### 1.4 Implementation Method
Modules MUST implement:
- `run_standalone()` method for independent execution
- `_interactive_mode()` method for command interface
- Integration with Block Orchestrator system
- Graceful mock component fallbacks

## 2. Command Philosophy

The WRE command set should be:
-   **Concise**: Commands should be short and easy to remember.
-   **Consistent**: The syntax and behavior of commands should be predictable.
-   **Extensible**: The framework should allow for the easy addition of new commands as the WRE's capabilities grow.
-   **User-Friendly**: Interactive interfaces should provide numbered shortcuts and clear guidance.

## 3. Standard Command Set (Proposed)

### Core Commands
-   `k` - (To be defined. Likely related to knowledge or state checks.)
-   `go` - (To be defined. Likely related to initiating a goal or task.)
-   `init` - (To be defined. Likely related to initializing a new module or project.)
-   `fix` - (To be defined. Likely related to initiating an automated error correction workflow.)
-   `save` - (Defined in **WSP 10: State Save Protocol**.)

### Additional Commands
*(Additional command definitions will be added here as they are proposed and ratified.)* 

---

## 4. Related Protocols

### WSP 72: Block Independence Interactive Protocol
This protocol extends the interactive interface standards defined in WSP 11.1 to include:
- **Cube Management**: Interactive assessment and testing of entire Rubik's Cube collections
- **0102 pArtifact Operations**: Autonomous verification and management of block independence
- **Documentation Linking**: Direct access to module documentation through interactive interfaces
- **Test Suite Integration**: Comprehensive testing and compliance verification

**See**: [WSP 72: Block Independence Interactive Protocol](WSP_72_Block_Independence_Interactive_Protocol.md) for complete implementation details. 