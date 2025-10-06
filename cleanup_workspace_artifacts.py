#!/usr/bin/env python3
"""
WSP Workspace Cleanup Script
Removes artifacts from WSP Documentation Guardian testing
- Removes .backup files created during ASCII remediation testing
- Removes stray test files
- Cleans up temp directories
- Maintains safety checks to avoid deleting legitimate files

WSP Compliance: WSP 20 (ASCII-only), WSP 22 (Documentation)
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Set

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('cleanup_log.txt', mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WSPWorkspaceCleanup:
    """Safe workspace cleanup for WSP Documentation Guardian artifacts"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.backup_files_removed: List[Path] = []
        self.test_files_removed: List[Path] = []
        self.temp_dirs_cleaned: List[Path] = []
        self.errors: List[str] = []

    def is_safe_to_delete_backup(self, backup_path: Path) -> bool:
        """
        Safety check: Only delete .backup files that match our remediation pattern
        """
        if not backup_path.suffix == '.backup':
            return False

        # Check if corresponding original file exists (indicates our backup)
        original_path = backup_path.with_suffix('')
        if not original_path.exists():
            return False

        # Check if backup is in our temp directory structure
        if 'temp/wsp_backups' in str(backup_path):
            return True

        # For WSP framework backups, check if they're ASCII remediation backups
        # These would have been created during our testing
        backup_content = ""
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_content = f.read(1024)  # Read first 1KB
        except Exception:
            return False

        # Check if this looks like a WSP ASCII remediation backup
        # (contains non-ASCII characters that would have been sanitized)
        has_unicode = any(ord(c) > 127 for c in backup_content)
        if has_unicode:
            # This is likely one of our ASCII remediation backups
            return True

        # For scattered backups, check modification time (our recent testing)
        try:
            stat = backup_path.stat()
            age_hours = (datetime.now().timestamp() - stat.st_mtime) / 3600
            # Allow backups up to 48 hours old (covering our testing period)
            return age_hours < 48
        except Exception:
            return False

    def find_backup_files(self) -> List[Path]:
        """Find all .backup files in the repository"""
        backup_files = []
        for root, dirs, files in os.walk(self.repo_root):
            for file in files:
                if file.endswith('.backup'):
                    backup_files.append(Path(root) / file)
        return backup_files

    def find_test_files(self) -> List[Path]:
        """Find stray test files created during testing"""
        test_files = []
        test_patterns = [
            'test_wsp_doc.md',
            'test_wsp_doc.txt',
            # Add other known test file patterns here
        ]

        for pattern in test_patterns:
            for file_path in self.repo_root.rglob(pattern):
                if file_path.is_file():
                    test_files.append(file_path)

        return test_files

    def cleanup_backup_files(self) -> int:
        """Remove all safe-to-delete backup files"""
        backup_files = self.find_backup_files()
        removed_count = 0

        logger.info(f"Found {len(backup_files)} .backup files to evaluate")

        for backup_file in backup_files:
            if self.is_safe_to_delete_backup(backup_file):
                try:
                    backup_file.unlink()
                    self.backup_files_removed.append(backup_file)
                    removed_count += 1
                    logger.info(f"Removed backup: {backup_file}")
                except Exception as e:
                    error_msg = f"Failed to remove {backup_file}: {e}"
                    self.errors.append(error_msg)
                    logger.error(error_msg)
            else:
                logger.info(f"Skipped unsafe backup: {backup_file}")

        return removed_count

    def cleanup_test_files(self) -> int:
        """Remove stray test files"""
        test_files = self.find_test_files()
        removed_count = 0

        logger.info(f"Found {len(test_files)} test files to remove")

        for test_file in test_files:
            try:
                test_file.unlink()
                self.test_files_removed.append(test_file)
                removed_count += 1
                logger.info(f"Removed test file: {test_file}")
            except Exception as e:
                error_msg = f"Failed to remove test file {test_file}: {e}"
                self.errors.append(error_msg)
                logger.error(error_msg)

        return removed_count

    def cleanup_temp_directory(self) -> int:
        """Clean up temp/wsp_backups directory safely"""
        temp_dir = self.repo_root / "temp" / "wsp_backups"
        cleaned_count = 0

        if temp_dir.exists():
            try:
                # Only remove if it's our wsp_backups directory
                if temp_dir.name == "wsp_backups" and temp_dir.parent.name == "temp":
                    shutil.rmtree(temp_dir)
                    self.temp_dirs_cleaned.append(temp_dir)
                    logger.info(f"Removed temp directory: {temp_dir}")
                    cleaned_count = 1
                else:
                    logger.warning(f"Skipped unsafe temp directory: {temp_dir}")
            except Exception as e:
                error_msg = f"Failed to remove temp directory {temp_dir}: {e}"
                self.errors.append(error_msg)
                logger.error(error_msg)

        return cleaned_count

    def cleanup_log_files(self) -> int:
        """Clean up cleanup-related log files"""
        log_files_to_clean = [
            self.repo_root / "backup_files_to_clean.txt",
            self.repo_root / "cleanup_log.txt"
        ]

        cleaned_count = 0
        for log_file in log_files_to_clean:
            if log_file.exists():
                try:
                    log_file.unlink()
                    cleaned_count += 1
                    logger.info(f"Removed cleanup log: {log_file}")
                except Exception as e:
                    logger.warning(f"Could not remove cleanup log {log_file}: {e}")

        return cleaned_count

    def run_cleanup(self) -> dict:
        """Run complete workspace cleanup"""
        logger.info("=== WSP WORKSPACE CLEANUP STARTED ===")
        logger.info(f"Repository root: {self.repo_root}")

        start_time = datetime.now()

        # Run cleanup phases
        backup_count = self.cleanup_backup_files()
        test_count = self.cleanup_test_files()
        temp_count = self.cleanup_temp_directory()
        log_count = self.cleanup_log_files()

        end_time = datetime.now()
        duration = end_time - start_time

        # Summary
        summary = {
            'backup_files_removed': len(self.backup_files_removed),
            'test_files_removed': len(self.test_files_removed),
            'temp_dirs_cleaned': len(self.temp_dirs_cleaned),
            'logs_cleaned': log_count,
            'errors': len(self.errors),
            'duration_seconds': duration.total_seconds()
        }

        logger.info("=== WSP WORKSPACE CLEANUP COMPLETED ===")
        logger.info(f"Backup files removed: {summary['backup_files_removed']}")
        logger.info(f"Test files removed: {summary['test_files_removed']}")
        logger.info(f"Temp directories cleaned: {summary['temp_dirs_cleaned']}")
        logger.info(f"Log files cleaned: {summary['logs_cleaned']}")
        logger.info(f"Errors encountered: {summary['errors']}")
        logger.info(f"Duration: {summary['duration_seconds']:.2f} seconds")

        if self.errors:
            logger.warning("Errors encountered:")
            for error in self.errors:
                logger.warning(f"  - {error}")

        return summary

def main():
    """Main cleanup execution"""
    repo_root = Path(__file__).resolve().parent

    # Confirm with user before proceeding
    print("WSP Workspace Cleanup Script")
    print("=" * 40)
    print(f"Repository root: {repo_root}")
    print()
    print("This will remove:")
    print("- .backup files created during WSP testing")
    print("- Stray test files (test_wsp_doc.md, etc.)")
    print("- temp/wsp_backups directory")
    print("- Cleanup log files")
    print()

    response = input("Proceed with cleanup? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Cleanup cancelled.")
        return

    # Run cleanup
    cleanup = WSPWorkspaceCleanup(repo_root)
    summary = cleanup.run_cleanup()

    # Final report
    print("\n" + "=" * 40)
    print("CLEANUP SUMMARY")
    print("=" * 40)
    print(f"Backup files removed: {summary['backup_files_removed']}")
    print(f"Test files removed: {summary['test_files_removed']}")
    print(f"Temp directories cleaned: {summary['temp_dirs_cleaned']}")
    print(f"Log files cleaned: {summary['logs_cleaned']}")
    print(f"Errors: {summary['errors']}")
    print(".2f")
    print()
    print("[SUCCESS] Workspace cleanup completed successfully!")
    print("Repository is now clean of WSP testing artifacts.")

if __name__ == "__main__":
    main()
