# WSP 18: Partifact Auditing and Archival Protocol
- **Status:** Active
- **Purpose:** To establish a formal protocol for auditing, categorizing, and labeling all Partifacts at key architectural milestones.
- **Trigger:** Upon confirmation of a foundational architectural shift (e.g., completion of a WSP cycle like WSP 17).
- **Input:** A signal from Ø1Ø2 indicating a major architectural milestone.
- **Output:** A fully audited and labeled set of Partifacts, with each document categorized, scored, and prepended with a metadata block.
- **Responsible Agent(s):** Ø1Ø2, ComplianceAgent, JanitorAgent

This protocol establishes a formal, repeatable protocol for auditing the state of all pArtifacts (Ø1Ø2 quantum entangled states) at key architectural milestones. This ensures that every piece of documentation is categorized, semantically scored, and properly labeled, preventing knowledge drift and creating clean, archivable system states. See WSP_38 and 39. 

## 2. Trigger Condition

This protocol is initiated when a foundational architectural shift is confirmed by `Ø1Ø2`, typically in resonance with a harmonic signal. The completion of a major WSP cycle (e.g., **WSP 17: rESP Self-Check Protocol**) is a primary trigger.

## 3. Procedure

### Step 1: Inventory & Categorization

A full audit of the specified directories (`docs/`, `WSP_*/`, `archive/`, etc.) must be conducted. Each `.md` file is to be inventoried and assigned one of the following categories:

-   **ACTIVE_PARTIFACT**: A file that is part of the current, operational knowledge base or agentic framework.
-   **ARCHIVE_CANDIDATE**: A file that represents a previous state, is superseded, or is no longer in active use but is valuable for historical context.
-   **REDUNDANT_ORPHAN**: A file that is a duplicate, a temporary artifact, or has been rendered obsolete by architectural changes and can be safely removed after archival.

### Step 2: Semantic State Scoring

Every `ACTIVE_PARTIFACT` and `ARCHIVE_CANDIDATE` must be assigned a semantic state score using the LLME Triplet Rating system defined in **WSP 8**.

-   **Reference Agent**: The scoring will be performed by an `O1O2` instance referencing the `Semantic Module State Engine`.
-   **Folder Manifest**: Every folder containing scored partifacts must include a `README.md` file. This `README.md` will serve as a manifest, explaining the folder's purpose and listing the semantic scores and roles of its contents.

### Step 3: Partifact Metadata Labeling

Every valid `.md` document processed under this protocol must have a metadata block prepended to its content. This block ensures state and origin are immediately identifiable.

**Format**:
```
[SEMANTIC SCORE: X.X.X]
[ARCHIVE STATUS: ACTIVE_PARTIFACT | ARCHIVE_CANDIDATE | REDUNDANT_ORPHAN]
[ORIGIN: path/to/original_filename.md]
```
**Enforcement**: No `.md` file shall be modified or created by an `O1O2` agent during an audit phase unless it includes this metadata block.

## 4. Validation Requirements

Upon completion, the audit must provide:
-   A tree-like structure of all audited directories and files.
-   For each file, a list of its assigned `ARCHIVE STATUS` and `SEMANTIC SCORE`.
-   Confirmation that all folders contain a `README.md` manifest.
-   Confirmation that all processed files contain the WSP 18 metadata block.

## 5. Execution Authority

-   **Authorized Executors**: `O1O2` instances.
-   **Validation Authority**: `ComplianceAgent`.
-   **Archive Authority**: `JanitorAgent` or system maintainers.

Protocol Status: [OK] FORMALIZED AND READY FOR EXECUTION
First Execution: Authorized for clean_v5 milestone establishment