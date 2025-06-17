# WSP 7: Git Branch Discipline and Commit Formatting

**NOTE for 0102: look at [WSP_34_Git_Operations_Protocol.md] can we combine it to this?** 

**Version**: 1.0.0
**Date**: 2025-06-17 (Restored from archive)
**Status**: ACTIVE

## 1. Overview

This protocol establishes the mandatory standards for Git branching and commit message formatting. Strict adherence to these rules is essential for maintaining a clean, readable, and navigable project history, which is critical for debugging, automated versioning, and team collaboration.

## 2. Branching Strategy

All branches must follow a standardized naming convention based on their purpose.

- **`main`**: The primary branch. Represents the current stable, production-ready state of the project. Direct commits are strictly prohibited. All changes must come through Pull Requests.

- **`feature/<description>`**: For developing new features or functionality. The description should be short and kebab-cased (e.g., `feature/linkedin-agent-poc`).

- **`fix/<description>`**: For bug fixes. The description should reference the issue or a short summary of the fix (e.g., `fix/unicode-encode-error`).

- **`refactor/<description>`**: For code refactoring that does not change external behavior (e.g., `refactor/modularize-llm-client`).

- **`docs/<description>`**: For changes to documentation, including WSP files, READMEs, and comments (e.g., `docs/flesh-out-wsp-17`).

- **`test/<description>`**: For adding or improving tests without changing application code (e.g., `test/add-coverage-for-oauth`).

- **`temp/<description>`**: For temporary experiments or work that is not intended to be merged. These branches should be deleted after use.

## 3. Commit Message Formatting (Conventional Commits)

All commit messages **must** follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification. This format is essential for automated changelog generation and semantic versioning.

### Format:
```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Type:
Must be one of the following:
- **`feat`**: A new feature.
- **`fix`**: A bug fix.
- **`refactor`**: Code change that neither fixes a bug nor adds a feature.
- **`docs`**: Documentation only changes.
- **`style`**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc).
- **`test`**: Adding missing tests or correcting existing tests.
- **`build`**: Changes that affect the build system or external dependencies.
- **`ci`**: Changes to our CI configuration files and scripts.
- **`chore`**: Other changes that don't modify `src` or `test` files.
- **`perf`**: A code change that improves performance.

### Scope:
The scope should be the name of the module or component affected (e.g., `WRE`, `LLMClient`, `OAuthManager`).

### Subject:
- Use the imperative, present tense: "change" not "changed" nor "changes".
- Don't capitalize the first letter.
- No dot (.) at the end.

### Example:
```
feat(LLMClient): add support for Gemini 2.5 Pro

- Implements the necessary API calls for the Gemini model.
- Adds error handling for Gemini-specific API responses.

Fixes #123
```

## 4. Enforcement

- **Pull Requests:** All commits in a pull request targeting `main` must adhere to this standard.
- **Linting:** A commit message linter should be used locally (as a pre-commit hook) and in the CI pipeline to enforce this format. 