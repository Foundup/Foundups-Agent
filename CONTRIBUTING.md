# Contributing to FoundUps Agent

Thank you for your interest in contributing to FoundUps! This document provides guidelines and information for contributors.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and collaborative environment. We are building the infrastructure for autonomous ventures - collaboration over competition.

## How to Contribute

### Reporting Issues

1. Check existing issues to avoid duplicates
2. Use the issue templates when available
3. Provide clear reproduction steps
4. Include relevant logs and environment details

### Pull Requests

1. Fork the repository
2. Create a feature branch from `main`
3. Follow the WSP (Windsurf Protocol) conventions
4. Write tests for new functionality
5. Update documentation as needed
6. Submit a PR with a clear description

### Branch Naming

```
feature/short-description
fix/issue-number-description
docs/documentation-update
refactor/module-name
```

## Development Setup

### Prerequisites

- Python 3.12+
- Git
- Windows/Linux/macOS

### Installation

```bash
# Clone the repository
git clone https://github.com/FOUNDUPS/Foundups-Agent.git
cd Foundups-Agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running Tests

```bash
# Run all tests
python -m pytest modules/ -q

# Run specific module tests
python -m pytest modules/foundups/simulator/tests/ -v
```

## WSP Compliance

All contributions should follow the Windsurf Protocol (WSP) framework:

- **WSP 3**: Module domain organization
- **WSP 5**: Test coverage requirements
- **WSP 22**: ModLog documentation
- **WSP 49**: Module structure standards
- **WSP 50**: Pre-action verification
- **WSP 72**: Block independence

See [WSP_MASTER_INDEX.md](WSP_framework/WSP_MASTER_INDEX.md) for the complete protocol catalog.

## Module Structure

New modules should follow this structure:

```
modules/[domain]/[module_name]/
  README.md          # Module overview
  INTERFACE.md       # Public API documentation
  ROADMAP.md         # Development roadmap
  ModLog.md          # Change history
  src/               # Source code
  tests/             # Test files
    README.md
    TestModLog.md
  requirements.txt   # Module dependencies
```

## Commit Messages

Follow conventional commits:

```
feat(module): add new feature
fix(module): fix bug description
docs(module): update documentation
refactor(module): code restructuring
test(module): add or update tests
chore(module): maintenance tasks
```

## Questions?

- Open a GitHub issue for technical questions
- Join our community discussions

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License for code, with patent considerations as described in the [LICENSE](LICENSE) file.

---

*FoundUps - Building the orchestration infrastructure for an intelligent internet*
