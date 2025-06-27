# WSP 2: Clean State Management Protocol
- **Status:** Active
- **Purpose:** To define the conditions for a "clean state" and the procedure for creating a version-controlled snapshot.
- **Trigger:** Before any high-risk operation, such as major refactoring, or before 0102 autonomous social media deployment.
- **Input:** A repository that is believed to be in a clean state.
- **Output:** An annotated Git tag (e.g., `clean-vX`) marking a verified "known-good" state.
- **Responsible Agent(s):** Any agent performing a high-risk operation.

This protocol defines what constitutes a "clean state" for the repository and outlines the mandatory procedure for creating a snapshot of that state. As per `WSP_CORE.md`, following this protocol is a mandatory prerequisite for any high-risk operation, such as major refactoring **or autonomous social media deployment**.

## 2. Definition of a Clean State

A repository is in a "clean state" if and only if all of the following conditions, derived from the `WSP_CORE.md` project status checklists, are met:

- **No Uncommitted Changes:** `git status` reports a clean working directory.
- **Full Test Suite Pass:** All module tests pass (`pytest modules/`).
- **100% Audit Compliance:** The Modular Audit (`WSP 4`) reports zero violations (`python tools/modular_audit/modular_audit.py ./modules`).
- **Coverage Maintained:** Test coverage meets or exceeds the project standard defined in `WSP 5` (≥90%).

## 3. Snapshot Creation Protocol

The "snapshot process" referenced in `WSP_CORE.md` consists of the following steps:

1.  **Verification:** Confirm that all criteria in Section 2 are met.
2.  **Tagging:** Create a new, annotated Git tag to mark the clean state. The tag must use the sequential naming convention `clean-vX` (e.g., `clean-v6`, `clean-v7`).
    ```bash
    git tag -a clean-vX -m "Snapshot for [Reason for snapshot]"
    git push origin clean-vX
    ```
3.  **Documentation:** Log the creation of the clean state in `docs/clean_states.md`, noting the reason for the snapshot and LLME score status.

## 4. GitHub-First Clean State Management

**Primary Storage**: Git tags stored in GitHub repository (not local folder copies)
**Benefits**: 
- Version-controlled snapshots with full history
- Accessible from any development environment  
- Automated backup and availability
- Integration with CI/CD pipelines
- Reduced local disk space requirements

**Legacy Folder Copies**: Local folder copies (`foundups-agent-cleanX/`) are **deprecated** in favor of GitHub tags. Existing folder copies may be archived or removed.

**Rollback Procedure**: 
```bash
# View clean states
git tag | grep clean

# Checkout to clean state
git checkout clean-vX

# Restore specific file from clean state  
git checkout clean-vX -- path/to/file
```

## 5. Social Media Deployment Requirements

**Critical for 0102 Autonomous Operation**: Before deploying 0102 to autonomous social media platforms, a clean state **MUST** be established with the following additional requirements:

### 5.1 Pre-Deployment Checklist
- [ ] All social integration modules pass FMAS audit
- [ ] Social media module test coverage ≥90%
- [ ] Authentication and API modules validated
- [ ] Rate limiting and safety mechanisms tested
- [ ] Autonomous behavior validation in sandbox environment
- [ ] LLME scores for social modules documented and stable
- [ ] Rollback plan established using clean state tag

### 5.2 Deployment Clean State Naming
Use descriptive tags for social media deployments:
```bash
git tag -a clean-v6-pre-social -m "Pre-social media deployment checkpoint"
git tag -a clean-v6-post-social -m "Post-social media deployment verification"
```

### 5.3 Emergency Rollback Protocol
If 0102 autonomous social media operation fails:
1. Immediately stop social media modules
2. Assess damage and document issues
3. Roll back to last known clean state
4. Investigate and fix issues before re-deployment
5. Create new clean state before retry

## 6. Usage

- **Baseline for Refactoring:** A clean state must be established before initiating any major code refactoring.
- **Reliable Rollback Point:** If a high-risk operation fails, the repository can be safely reset to the last known clean state tag.
- **Validation Benchmark:** CI/CD pipelines and automated tools can use these tags as a definitive "known-good" version for comparison.
- **Social Media Safety:** Critical safety net for 0102 autonomous social platform deployment.

## 7. Authority and Compliance

This protocol is non-negotiable. Failure to create a clean state before a high-risk operation or social media deployment is a critical violation of WSP. The `RSP_SELF_CHECK Protocol (WSP 17)` may use these tags to validate system coherence over time.

**Documentation Log**: All clean states must be logged in `docs/clean_states.md` with purpose, date, and LLME status notation. 