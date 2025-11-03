#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io

"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

Conversation Log Cleanup Utility

Cleanup script for conversation logs - removes duplicates and organizes with new naming convention.
Supports backup creation, duplicate detection, and structured file organization.

Author: FoundUps Agent Utilities Team
Version: 1.0.0
Date: 2025-01-29
WSP Compliance: WSP 13 (Test Creation & Management), WSP 22 (Traceable Narrative)

Dependencies:
- None (uses only standard library)

Usage:
    python tools/cleanup_conversation_logs.py
    
Features:
- Automatic duplicate detection using content hashing
- Safe backup creation before cleanup
- Support for multiple conversation log formats
- Structured file organization with size and timestamp info
"""

import os
import glob
import shutil
from datetime import datetime
import json

def cleanup_conversation_logs():
    """Clean up duplicate conversation logs and organize with new naming convention."""
    
    print("[U+1F9F9] Starting conversation log cleanup...")
    
    # Define directories
    memory_dir = "memory"
    conversations_dir = os.path.join(memory_dir, "conversations")
    backup_dir = os.path.join(memory_dir, "backup_old_logs")
    
    if not os.path.exists(conversations_dir):
        print("[FAIL] No conversations directory found")
        return
    
    # Create backup directory
    os.makedirs(backup_dir, exist_ok=True)
    
    # Get all conversation files
    conversation_files = glob.glob(os.path.join(conversations_dir, "*.txt"))
    
    print(f"[U+1F4C1] Found {len(conversation_files)} conversation files")
    
    # Categorize files
    stream_files = []
    daily_files = []
    old_format_files = []
    
    for file_path in conversation_files:
        filename = os.path.basename(file_path)
        
        if filename.startswith("stream_"):
            # Old format: stream_YYYY-MM-DD_VideoID.txt
            old_format_files.append(file_path)
        elif filename.startswith("daily_summary_"):
            # Daily summary files
            daily_files.append(file_path)
        elif "_" in filename and len(filename.split("_")) >= 3:
            # New format: YYYY-MM-DD_StreamTitle_VideoID.txt
            stream_files.append(file_path)
        else:
            # Unknown format
            old_format_files.append(file_path)
    
    print(f"[DATA] File categorization:")
    print(f"  - Stream files (new format): {len(stream_files)}")
    print(f"  - Daily summary files: {len(daily_files)}")
    print(f"  - Old format files: {len(old_format_files)}")
    
    # Move old format files to backup
    if old_format_files:
        print(f"[BOX] Moving {len(old_format_files)} old format files to backup...")
        for file_path in old_format_files:
            filename = os.path.basename(file_path)
            backup_path = os.path.join(backup_dir, filename)
            shutil.move(file_path, backup_path)
            print(f"  Moved: {filename}")
    
    # Check for duplicate content in remaining files
    print("[SEARCH] Checking for duplicate content...")
    
    file_hashes = {}
    duplicates = []
    
    for file_path in stream_files + daily_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Create a simple hash of the content
            content_hash = hash(content)
            
            if content_hash in file_hashes:
                duplicates.append((file_path, file_hashes[content_hash]))
            else:
                file_hashes[content_hash] = file_path
                
        except Exception as e:
            print(f"[U+26A0]️ Error reading {file_path}: {e}")
    
    # Handle duplicates
    if duplicates:
        print(f"[U+1F5D1]️ Found {len(duplicates)} duplicate files:")
        for duplicate_path, original_path in duplicates:
            duplicate_name = os.path.basename(duplicate_path)
            original_name = os.path.basename(original_path)
            
            print(f"  Duplicate: {duplicate_name}")
            print(f"  Original:  {original_name}")
            
            # Move duplicate to backup
            backup_path = os.path.join(backup_dir, f"duplicate_{duplicate_name}")
            shutil.move(duplicate_path, backup_path)
            print(f"  -> Moved duplicate to backup")
    else:
        print("[OK] No duplicates found")
    
    # Show final summary
    remaining_files = glob.glob(os.path.join(conversations_dir, "*.txt"))
    print(f"\n[CLIPBOARD] Cleanup Summary:")
    print(f"  - Files remaining: {len(remaining_files)}")
    print(f"  - Files backed up: {len(old_format_files) + len(duplicates)}")
    print(f"  - Backup location: {backup_dir}")
    
    # Show current file structure
    if remaining_files:
        print(f"\n[U+1F4C1] Current conversation files:")
        for file_path in sorted(remaining_files):
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            print(f"  - {filename} ({file_size} bytes)")

def show_conversation_structure():
    """Show the current conversation log structure."""
    
    print("\n[DATA] Current Conversation Log Structure:")
    print("=" * 50)
    
    conversations_dir = os.path.join("memory", "conversations")
    
    if not os.path.exists(conversations_dir):
        print("[FAIL] No conversations directory found")
        return
    
    files = glob.glob(os.path.join(conversations_dir, "*.txt"))
    
    if not files:
        print("[U+1F4ED] No conversation files found")
        return
    
    # Group by type
    stream_files = [f for f in files if not os.path.basename(f).startswith("daily_summary_")]
    daily_files = [f for f in files if os.path.basename(f).startswith("daily_summary_")]
    
    print(f"[U+1F4FA] Stream-specific logs ({len(stream_files)}):")
    for file_path in sorted(stream_files):
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        print(f"  - {filename}")
        print(f"    Size: {file_size} bytes | Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n[U+1F4C5] Daily summary logs ({len(daily_files)}):")
    for file_path in sorted(daily_files):
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        print(f"  - {filename}")
        print(f"    Size: {file_size} bytes | Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    print("[ROCKET] FoundUps Agent - Conversation Log Cleanup")
    print("=" * 50)
    
    # Show current structure
    show_conversation_structure()
    
    # Ask for confirmation
    print("\n" + "=" * 50)
    response = input("[U+1F914] Do you want to proceed with cleanup? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        cleanup_conversation_logs()
        print("\n" + "=" * 50)
        show_conversation_structure()
        print("\n[OK] Cleanup completed!")
    else:
        print("[FAIL] Cleanup cancelled") 