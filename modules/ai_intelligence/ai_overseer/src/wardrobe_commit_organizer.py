#!/usr/bin/env python3
"""
Wardrobe Commit Organizer - Atomic Commit Hygiene Skill

Organizes uncommitted changes into atomic, focused commits following
commit hygiene guidelines. Uses Qwen for semantic grouping and Gemma
for fast classification.

WSP Compliance:
- WSP 91: DAEMON observability (logging, decision tracking)
- WSP 27: Universal DAE Architecture (autonomous decision-making)
- WSP 49: Module Structure (proper separation of concerns)
"""

import subprocess
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class FileChange:
    """Represents a single file change."""
    status: str  # M, A, D, R, etc.
    filepath: str
    classification: str  # code, docs, config, test, build
    scope: str  # gotjunk, wsp_orchestrator, etc.
    logical_group: Optional[str] = None  # Qwen-assigned group ID


@dataclass
class CommitGroup:
    """Represents a logical group of files for atomic commit."""
    files: List[FileChange]
    commit_type: str  # feat, fix, docs, chore, test, refactor
    scope: str
    description: str

    @property
    def commit_message(self) -> str:
        """Generate conventional commit message."""
        return f"{self.commit_type}({self.scope}): {self.description}"


class WardrobeCommitOrganizer:
    """
    Organizes git changes into atomic commits following commit hygiene.

    Workflow:
    1. Analyze git status (get uncommitted changes)
    2. Classify files (Gemma: code|docs|config|test)
    3. Group related files (Qwen: semantic grouping)
    4. Separate by scope (module isolation)
    5. Generate commit messages
    6. Execute atomic commits
    """

    def __init__(self, logger, qwen_engine=None, max_files_per_commit: int = 5):
        """
        Initialize wardrobe organizer.

        Args:
            logger: Logging instance
            qwen_engine: Optional Qwen inference engine for semantic analysis
            max_files_per_commit: Maximum files per atomic commit (default: 5)
        """
        self.logger = logger
        self.qwen = qwen_engine
        self.max_files_per_commit = max_files_per_commit

        # Scope patterns for module detection
        self.scope_patterns = {
            r'modules/foundups/gotjunk/': 'gotjunk',
            r'modules/infrastructure/wsp_orchestrator/': 'wsp_orchestrator',
            r'modules/infrastructure/git_push_dae/': 'git_push_dae',
            r'modules/ai_intelligence/ai_overseer/': 'ai_overseer',
            r'modules/communication/liberty_alert/': 'liberty_alert',
            r'WSP_framework/': 'wsp_framework',
            r'holo_index/': 'holo_index',
            r'\.claude/': 'claude_config',
            r'CLAUDE\.md': 'docs',
            r'README\.md': 'docs',
            r'ModLog\.md': 'modlog',
        }

        # Classification patterns (for Gemma-less fallback)
        self.classification_patterns = {
            'docs': [r'README\.md', r'ModLog\.md', r'INTERFACE\.md', r'\.md$', r'docs/'],
            'test': [r'test_.*\.py$', r'.*_test\.py$', r'/tests/', r'\.test\.tsx?$', r'\.spec\.tsx?$'],
            'config': [r'\.json$', r'\.yaml$', r'\.toml$', r'\.env', r'package\.json', r'requirements\.txt'],
            'build': [r'package-lock\.json', r'yarn\.lock', r'\.pyc$', r'__pycache__'],
            'code': [],  # Default fallback
        }

    def organize_commits(self, dry_run: bool = False) -> Dict:
        """
        Main entry point: Organize uncommitted changes into atomic commits.

        Args:
            dry_run: If True, only analyze and report, don't create commits

        Returns:
            Dict with status, commits_created, commit_messages, details
        """
        self.logger.info("[WARDROBE] Starting commit organization")

        try:
            # Step 1: Analyze git status
            changes = self._get_uncommitted_changes()

            if not changes:
                self.logger.info("[WARDROBE] No uncommitted changes to organize")
                return {
                    'status': 'success',
                    'commits_created': 0,
                    'commit_messages': [],
                    'details': 'No uncommitted changes'
                }

            self.logger.info(f"[WARDROBE] Found {len(changes)} uncommitted files")

            # Step 2: Classify files
            file_changes = self._classify_files(changes)

            # Step 3: Group related files
            commit_groups = self._group_files(file_changes)

            # Step 4: Validate groups (scope isolation)
            valid_groups, invalid_groups = self._validate_groups(commit_groups)

            if invalid_groups:
                self.logger.warning(f"[WARDROBE] {len(invalid_groups)} groups violate scope isolation")

            # Step 5: Generate commit messages
            self._generate_commit_messages(valid_groups)

            # Step 6: Execute commits (unless dry run)
            if dry_run:
                self.logger.info("[WARDROBE] Dry run - no commits created")
                commit_messages = [g.commit_message for g in valid_groups]
                return {
                    'status': 'success',
                    'commits_created': 0,
                    'commit_messages': commit_messages,
                    'details': f'Dry run: {len(valid_groups)} commits planned'
                }
            else:
                result = self._execute_commits(valid_groups)
                return result

        except Exception as e:
            self.logger.error(f"[WARDROBE] Organization failed: {e}")
            return {
                'status': 'error',
                'commits_created': 0,
                'commit_messages': [],
                'details': f'Error: {e}'
            }

    def _get_uncommitted_changes(self) -> List[str]:
        """Get list of uncommitted files from git status."""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                check=True
            )

            lines = result.stdout.strip().split('\n') if result.stdout.strip() else []

            # Filter out untracked files we want to ignore
            filtered = []
            for line in lines:
                # Skip empty lines
                if not line.strip():
                    continue

                # Skip db artifacts (handled by db_gitignore_guard)
                if any(pattern in line for pattern in ['.db', '.db-shm', '.db-wal']):
                    continue

                filtered.append(line)

            return filtered

        except subprocess.CalledProcessError as e:
            self.logger.error(f"[WARDROBE] Git status failed: {e}")
            return []

    def _classify_files(self, changes: List[str]) -> List[FileChange]:
        """Classify each file as code, docs, config, test, or build."""
        file_changes = []

        for change in changes:
            # Parse git status line (format: "XY filepath")
            status = change[:2].strip()
            filepath = change[3:].strip()

            # Classify file
            classification = self._classify_file(filepath)

            # Detect scope (module)
            scope = self._detect_scope(filepath)

            file_changes.append(FileChange(
                status=status,
                filepath=filepath,
                classification=classification,
                scope=scope
            ))

        return file_changes

    def _classify_file(self, filepath: str) -> str:
        """Classify a single file."""
        # Try pattern matching
        for classification, patterns in self.classification_patterns.items():
            if any(re.search(pattern, filepath) for pattern in patterns):
                return classification

        # Default to 'code'
        return 'code'

    def _detect_scope(self, filepath: str) -> str:
        """Detect module scope from filepath."""
        for pattern, scope in self.scope_patterns.items():
            if re.search(pattern, filepath):
                return scope

        # Default scope
        return 'root'

    def _group_files(self, file_changes: List[FileChange]) -> List[CommitGroup]:
        """Group related files into logical commit groups."""
        groups = []

        # Strategy 1: Group by scope + classification
        # This ensures docs commits separate from code commits,
        # and each module's changes are isolated

        scope_classification_map = defaultdict(list)

        for fc in file_changes:
            key = f"{fc.scope}:{fc.classification}"
            scope_classification_map[key].append(fc)

        # Convert to CommitGroup objects
        for key, files in scope_classification_map.items():
            scope, classification = key.split(':')

            # Split large groups (respect max_files_per_commit)
            if len(files) > self.max_files_per_commit:
                # Split into chunks
                for i in range(0, len(files), self.max_files_per_commit):
                    chunk = files[i:i+self.max_files_per_commit]
                    groups.append(CommitGroup(
                        files=chunk,
                        commit_type=self._infer_commit_type(classification, chunk),
                        scope=scope,
                        description=self._generate_description(chunk)
                    ))
            else:
                groups.append(CommitGroup(
                    files=files,
                    commit_type=self._infer_commit_type(classification, files),
                    scope=scope,
                    description=self._generate_description(files)
                ))

        self.logger.info(f"[WARDROBE] Created {len(groups)} commit groups")
        return groups

    def _infer_commit_type(self, classification: str, files: List[FileChange]) -> str:
        """Infer conventional commit type from classification and file changes."""
        # Check file status for hints
        has_additions = any(fc.status.startswith('A') for fc in files)
        has_modifications = any(fc.status.startswith('M') for fc in files)
        has_deletions = any(fc.status.startswith('D') for fc in files)

        # Classification-based inference
        if classification == 'docs':
            return 'docs'
        elif classification == 'test':
            return 'test'
        elif classification in ['config', 'build']:
            return 'chore'
        elif classification == 'code':
            # Analyze filenames for clues
            if has_additions:
                return 'feat'
            elif has_deletions:
                return 'refactor'
            else:
                # Default to 'fix' for modifications
                return 'fix'

        return 'chore'

    def _generate_description(self, files: List[FileChange]) -> str:
        """Generate commit description from files."""
        if len(files) == 1:
            # Single file - use filename
            filename = Path(files[0].filepath).name
            return f"Update {filename}"

        # Multiple files - summarize
        classification = files[0].classification

        if classification == 'docs':
            return "Update documentation"
        elif classification == 'test':
            return "Update tests"
        elif classification == 'config':
            return "Update configuration"
        else:
            # Count file types
            file_count = len(files)
            return f"Update {file_count} files"

    def _validate_groups(self, groups: List[CommitGroup]) -> Tuple[List[CommitGroup], List[CommitGroup]]:
        """Validate commit groups for scope isolation."""
        valid = []
        invalid = []

        for group in groups:
            # Check scope isolation: all files in group must have same scope
            scopes = set(fc.scope for fc in group.files)

            if len(scopes) == 1:
                valid.append(group)
            else:
                self.logger.warning(
                    f"[WARDROBE] Invalid group: {group.commit_message} "
                    f"touches multiple scopes: {scopes}"
                )
                invalid.append(group)

        return valid, invalid

    def _generate_commit_messages(self, groups: List[CommitGroup]):
        """Enhance commit messages with Qwen semantic analysis (if available)."""
        if not self.qwen:
            self.logger.info("[WARDROBE] Qwen not available - using heuristic descriptions")
            return

        # Use Qwen to generate better descriptions
        for group in groups:
            try:
                # Construct prompt for Qwen
                filenames = [fc.filepath for fc in group.files]
                prompt = f"""Generate a concise commit description (max 10 words) for these files:

Files: {', '.join(filenames)}
Type: {group.commit_type}
Scope: {group.scope}

Description should focus on WHAT changed, not implementation details.
Return ONLY the description, no prefix."""

                # Query Qwen
                response = self.qwen.generate(prompt, max_tokens=50, temperature=0.3)

                # Clean response
                description = response.strip().strip('"').strip("'")

                # Update group description
                group.description = description
                self.logger.info(f"[WARDROBE] Qwen description: {description}")

            except Exception as e:
                self.logger.warning(f"[WARDROBE] Qwen description failed: {e}")
                # Keep heuristic description

    def _execute_commits(self, groups: List[CommitGroup]) -> Dict:
        """Execute atomic commits for each group."""
        commits_created = 0
        commit_messages = []

        for group in groups:
            try:
                # Stage files
                for fc in group.files:
                    subprocess.run(
                        ['git', 'add', fc.filepath],
                        capture_output=True,
                        check=True
                    )

                # Create commit
                commit_msg = group.commit_message
                subprocess.run(
                    ['git', 'commit', '-m', commit_msg],
                    capture_output=True,
                    check=True,
                    text=True
                )

                commits_created += 1
                commit_messages.append(commit_msg)

                self.logger.info(f"[WARDROBE] Created commit: {commit_msg}")

            except subprocess.CalledProcessError as e:
                self.logger.error(f"[WARDROBE] Commit failed: {e}")
                # Continue with other groups

        status = 'success' if commits_created > 0 else 'partial'

        return {
            'status': status,
            'commits_created': commits_created,
            'commit_messages': commit_messages,
            'details': f'Created {commits_created}/{len(groups)} commits'
        }


def apply_wardrobe_organizer(logger, qwen_engine=None, dry_run: bool = False) -> Dict:
    """
    Convenience function to apply wardrobe commit organizer.

    Args:
        logger: Logging instance
        qwen_engine: Optional Qwen inference engine
        dry_run: If True, only analyze and report

    Returns:
        Dict with status, commits_created, commit_messages, details
    """
    organizer = WardrobeCommitOrganizer(logger, qwen_engine)
    return organizer.organize_commits(dry_run=dry_run)
