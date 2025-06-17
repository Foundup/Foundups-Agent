# WSP 7: Test-Validated Commit Protocol
- **Status:** Active
- **Purpose:** To ensure no code is committed to a protected branch without first passing automated quality checks.
- **Trigger:** Automatically, on `git commit`.
- **Input:** Staged code changes.
- **Output:** A successful commit if the audit passes, or an aborted commit with an error report if it fails.
- **Responsible Agent(s):** ComplianceAgent

This protocol ensures that no code is committed to a protected branch without first passing a rigorous, automated quality check. It also mandates clear documentation for all tests to ensure their purpose and patterns are understood.

## 2. Enforcement via Pre-Commit Hook

-   **Mechanism**: A mandatory Git pre-commit hook is the primary enforcement point for this protocol.
-   **Action**: Before a commit is finalized, this hook automatically triggers a **Comprehensive Test Audit (WSP 6)** on all staged modules.
-   **Outcome**: If the audit fails for any reason (structural non-compliance, test failures, or insufficient coverage), the commit is automatically aborted. The developer receives the failure report from the audit and must remediate all issues before attempting to commit again.

## 3. Test File Documentation

-   **Requirement**: Every `tests/` directory **must** contain a `README.md` file.
-   **Content**: This file is not optional; it must clearly document the testing strategy for the module, explain the purpose of each test file, and describe any common patterns, mocks, or fixtures used. This is critical for maintainability and onboarding.
-   **Verification**: The existence of this file is validated by the **FMAS Validation Protocol (WSP 4)**.

## 4. Manual Override

-   A manual override of the pre-commit hook (e.g., using `git commit --no-verify`) is strictly forbidden in the standard development workflow and should be technically prevented by repository rules where possible.
-   Any exceptions require explicit, logged approval from a lead developer and will be flagged for review by the `ComplianceAgent`. 