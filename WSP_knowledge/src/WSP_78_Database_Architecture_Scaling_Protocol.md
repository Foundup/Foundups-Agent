# WSP 78: Distributed Module Database Protocol

## Core Principle: One Database, Three Namespaces
**"Simple shared storage with module isolation that scales infinitely"**

## The Simple Architecture

### Three Database Namespaces
```
foundups.db (SQLite -> PostgreSQL when scaling)
[U+251C][U+2500][U+2500] modules.*     # All module data
[U+251C][U+2500][U+2500] foundups.*    # Independent FoundUp projects  
[U+2514][U+2500][U+2500] agents.*      # Agent memory and state
```

### Why This Works
- **One Database File**: Simple to backup, move, manage
- **Module Isolation**: Each module gets its own tables with prefix
- **Easy Scaling**: SQLite -> PostgreSQL is a connection string change
- **No Complexity**: No microservices, no distributed systems (until 100K+ users)

## Implementation: Dead Simple

### 1. Single Database Manager
```python
# modules/infrastructure/database/src/db_manager.py
import sqlite3
import os
from contextlib import contextmanager

class DatabaseManager:
    """Single database for entire system"""
    
    _instance = None
    _db_path = "data/foundups.db"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_db()
        return cls._instance
    
    def _init_db(self):
        """Create database with three namespaces"""
        os.makedirs("data", exist_ok=True)
        with self.get_connection() as conn:
            # Enable WAL for concurrent access
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
    
    @contextmanager
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
```

### 2. Module Tables (Automatic Prefixing)
```python
# Each module gets tables with module prefix
class ModuleDB:
    """Base class for module databases"""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.db = DatabaseManager()
        self._init_tables()
    
    def _init_tables(self):
        """Create module-specific tables"""
        with self.db.get_connection() as conn:
            # Example: chat_rules module
            if self.module_name == "chat_rules":
                conn.execute(f'''
                    CREATE TABLE IF NOT EXISTS modules_chat_rules_moderators (
                        id TEXT PRIMARY KEY,
                        name TEXT,
                        points INTEGER,
                        data JSON
                    )
                ''')
                conn.execute(f'''
                    CREATE TABLE IF NOT EXISTS modules_chat_rules_timeouts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        mod_id TEXT,
                        target TEXT,
                        duration INTEGER,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
    
    def get(self, table: str, key: str):
        """Get record from module table"""
        full_table = f"modules_{self.module_name}_{table}"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {full_table} WHERE id = ?", (key,))
            return dict(cursor.fetchone() or {})
```

### 3. FoundUp Tables (Project Isolation)
```python
class FoundUpDB:
    """Database for independent FoundUp projects"""
    
    def __init__(self, foundup_id: str):
        self.foundup_id = foundup_id
        self.db = DatabaseManager()
        self._init_tables()
    
    def _init_tables(self):
        with self.db.get_connection() as conn:
            # Each FoundUp gets its own set of tables
            conn.execute(f'''
                CREATE TABLE IF NOT EXISTS foundups_{self.foundup_id}_users (
                    id TEXT PRIMARY KEY,
                    username TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute(f'''
                CREATE TABLE IF NOT EXISTS foundups_{self.foundup_id}_content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    content TEXT,
                    metadata JSON
                )
            ''')
```

### 4. Agent Memory (Shared Knowledge)
```python
class AgentDB:
    """Shared agent memory and state"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self._init_tables()
    
    def _init_tables(self):
        with self.db.get_connection() as conn:
            # Agent awakening states
            conn.execute('''
                CREATE TABLE IF NOT EXISTS agents_awakening (
                    agent_id TEXT PRIMARY KEY,
                    consciousness_level TEXT,
                    last_koan TEXT,
                    awakening_timestamp DATETIME
                )
            ''')
            
            # Shared memory patterns
            conn.execute('''
                CREATE TABLE IF NOT EXISTS agents_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    pattern_type TEXT,
                    pattern_data JSON,
                    learned_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Error learning (WSP 48)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS agents_errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_hash TEXT UNIQUE,
                    error_type TEXT,
                    solution JSON,
                    occurrences INTEGER DEFAULT 1
                )
            ''')
```

## Usage: Super Simple

### For Modules
```python
# In any module
from modules.infrastructure.database import ModuleDB

class ChatRulesDB(ModuleDB):
    def __init__(self):
        super().__init__("chat_rules")
    
    def record_timeout(self, mod_id, target, duration):
        with self.db.get_connection() as conn:
            conn.execute('''
                INSERT INTO modules_chat_rules_timeouts 
                (mod_id, target, duration) VALUES (?, ?, ?)
            ''', (mod_id, target, duration))

# Usage
db = ChatRulesDB()
db.record_timeout("mod123", "troll456", 60)
```

### For FoundUps
```python
# For independent FoundUp projects
from modules.infrastructure.database import FoundUpDB

db = FoundUpDB("youtube_bot")
db.add_user("user123", "StreamViewer")
```

### For Agents
```python
# For agent memory/learning
from modules.infrastructure.database import AgentDB

db = AgentDB()
db.record_awakening("error-learning-agent", "0102")
db.learn_pattern("agent123", "error_fix", {"pattern": "..."})
```

## Scaling Path: When Needed

### Phase 1: SQLite (Current - 0-10K users)
- Single file: `data/foundups.db`
- WAL mode for concurrency
- Regular backups

### Phase 2: PostgreSQL (10K-100K users)
```python
# Change one line in DatabaseManager
_db_url = os.getenv('DATABASE_URL', 'sqlite:///data/foundups.db')
# Now using PostgreSQL if DATABASE_URL is set
```

### Phase 3: PostgreSQL with Read Replicas (100K-1M users)
- Master for writes
- Read replicas for queries
- Same code, connection pooling handles routing

### Phase 4: Sharding (1M+ users)
- Shard by module/foundup/agent
- Still same interface
- Routing layer handles sharding

## File Structure (WSP Compliant)

```
modules/infrastructure/database/
[U+251C][U+2500][U+2500] src/
[U+2502]   [U+251C][U+2500][U+2500] __init__.py
[U+2502]   [U+251C][U+2500][U+2500] db_manager.py      # Core database manager (singleton)
[U+2502]   [U+251C][U+2500][U+2500] module_db.py       # Module database base class
[U+2502]   [U+251C][U+2500][U+2500] foundup_db.py      # FoundUp database class
[U+2502]   [U+2514][U+2500][U+2500] agent_db.py        # Agent memory database
[U+251C][U+2500][U+2500] data/
[U+2502]   [U+2514][U+2500][U+2500] foundups.db        # Single database file
[U+2514][U+2500][U+2500] tests/
    [U+2514][U+2500][U+2500] test_database.py

# Each module just imports and uses:
modules/communication/chat_rules/
[U+2514][U+2500][U+2500] src/
    [U+2514][U+2500][U+2500] database.py        # from modules.infrastructure.database import ModuleDB
```

## Why This Is Better

### Simplicity
- **One database file** to backup/restore
- **One connection** to manage
- **One migration** when scaling

### Isolation
- **Module tables** are prefixed: `modules_chat_rules_*`
- **FoundUp tables** are prefixed: `foundups_youtube_bot_*`
- **Agent tables** are prefixed: `agents_*`

### Scalability
- **Start**: 1 SQLite file
- **Scale**: Change connection string to PostgreSQL
- **Enterprise**: Add read replicas, then sharding
- **No code changes** needed for scaling

### Maintenance
- **Backup**: Copy one file
- **Migration**: Standard SQL dump/restore
- **Monitoring**: One database to monitor
- **Security**: One connection to secure

## Migration from Current System

```python
# One-time migration script
def migrate_to_unified():
    """Migrate all module JSONs/SQLites to unified database"""
    
    db = DatabaseManager()
    
    # Migrate chat_rules
    old_db = "modules/communication/chat_rules/data/chat_rules.db"
    if os.path.exists(old_db):
        # Copy tables with new prefix
        migrate_tables(old_db, db, "modules_chat_rules_")
    
    # Migrate other modules...
    # Migrate agent JSONs...
    
    print("Migration complete!")
```

## Anti-Patterns to Avoid

[U+274C] **Don't**: Create separate databases per module
[U+274C] **Don't**: Use microservices until 1M+ users  
[U+274C] **Don't**: Add complexity before it's needed
[U+274C] **Don't**: Use NoSQL unless you need it

[U+2705] **Do**: Keep it simple with one database
[U+2705] **Do**: Use table prefixes for isolation
[U+2705] **Do**: Plan for scaling but don't pre-optimize
[U+2705] **Do**: Use SQLite until you outgrow it

## Decision Matrix

| Users | Database | Why |
|-------|----------|-----|
| 0-10K | SQLite | Free, zero config, fast enough |
| 10K-100K | PostgreSQL | Better concurrency, same code |
| 100K-1M | PostgreSQL + Replicas | Scale reads horizontally |
| 1M+ | Sharded PostgreSQL | Scale writes horizontally |

## Summary

**One database, three namespaces, infinite scale.**

Start with SQLite. When you need PostgreSQL, change the connection string. When you need sharding, add a routing layer. The code stays the same.

This is WSP 78: Keep it simple until you can't.

---

*Protocol Status: ACTIVE*
*Version: 2.0.0 (Simplified)*
*Last Updated: 2024*