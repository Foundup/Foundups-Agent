#!/usr/bin/env python3
import sqlite3

def inspect_chromadb():
    print('[DB INSPECTION] Checking ChromaDB SQLite database structure')
    print('=' * 60)

    try:
        conn = sqlite3.connect(r'E:/HoloIndex/vectors/chroma.sqlite3')
        cursor = conn.cursor()

        # Check what tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f'Found {len(tables)} tables:')
        for table in tables:
            print(f'  - {table[0]}')

        # Check collections table
        try:
            cursor.execute('SELECT COUNT(*) FROM collections')
            collection_count = cursor.fetchone()[0]
            print(f'Collections table has {collection_count} entries')

            if collection_count > 0:
                cursor.execute('SELECT id, name FROM collections LIMIT 5')
                collections = cursor.fetchall()
                print('Sample collections:')
                for coll in collections:
                    print(f'  {coll[0]}: {coll[1]}')
        except Exception as e:
            print(f'Error reading collections: {e}')

        # Check embeddings table
        try:
            cursor.execute('SELECT COUNT(*) FROM embeddings')
            embedding_count = cursor.fetchone()[0]
            print(f'Embeddings table has {embedding_count} entries')
        except Exception as e:
            print(f'Error reading embeddings: {e}')

        # Check FTS table specifically
        try:
            cursor.execute("SELECT COUNT(*) FROM embedding_fulltext_search")
            fts_count = cursor.fetchone()[0]
            print(f'FTS table has {fts_count} entries')
        except Exception as e:
            print(f'Error reading FTS table: {e}')

        conn.close()

    except Exception as e:
        print(f'Failed to inspect database: {e}')

if __name__ == "__main__":
    inspect_chromadb()
