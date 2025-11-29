#!/usr/bin/env python3
import os
import shutil
import time
from pathlib import Path

def recreate_chromadb():
    print('[DATABASE RECOVERY] ChromaDB corruption requires full recreation')
    print('=' * 65)

    vectors_dir = Path('E:/HoloIndex/vectors')
    db_file = vectors_dir / 'chroma.sqlite3'

    # Create backup of corrupted database
    timestamp = int(time.time())
    backup_name = f'chroma.sqlite3.corrupted_{timestamp}.bak'
    backup_path = vectors_dir / backup_name

    print(f'[BACKUP] Creating backup of corrupted database as {backup_name}')
    if db_file.exists():
        shutil.copy2(db_file, backup_path)
    else:
        print('[WARNING] No corrupted database file found')

    # Remove corrupted database if it exists
    if db_file.exists():
        print('[REMOVE] Removing corrupted database file')
        db_file.unlink()

    # Create fresh ChromaDB database
    print('[CREATE] Creating fresh ChromaDB database')
    import chromadb
    client = chromadb.PersistentClient(path=str(vectors_dir))

    # Verify it works
    collections = client.list_collections()
    print(f'[VERIFY] Fresh database initialized with {len(collections)} collections')

    print('')
    print('[SUCCESS] ChromaDB database recreated successfully!')
    print('Corrupted database backed up for analysis')
    print('Fresh database created and verified')
    print('Ready for HoloIndex operations')

if __name__ == "__main__":
    recreate_chromadb()
