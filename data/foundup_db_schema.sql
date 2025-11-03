-- FoundUp Local Telemetry Database Schema
-- Purpose: Replace 219 scattered JSONL files with unified SQLite storage
-- Architecture: Local persistence layer for WSP 77 autonomous loop
-- Federation: LibertyAlert publisher reads from this DB and shares to mesh
--
-- WSP Compliance:
-- - WSP 77: Enables Gemma/Qwen/0102 coordination with fast local queries
-- - WSP 91: Observability via indexed queries
-- - Thread-safe: SQLite WAL mode handles concurrent writes

-- Enable WAL mode for concurrent reads/writes
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA foreign_keys=ON;

-- =============================================================================
-- CHAT MESSAGES (replaces 215 JSONL files)
-- =============================================================================
CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    stream_id TEXT NOT NULL,
    sent_at TEXT NOT NULL,          -- ISO8601 timestamp
    message TEXT,
    message_type TEXT DEFAULT 'chat',  -- chat, superchat, membership, etc.
    metadata_json TEXT,              -- Flexible storage for additional data
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_chat_user ON chat_messages(user_id);
CREATE INDEX idx_chat_stream ON chat_messages(stream_id);
CREATE INDEX idx_chat_sent ON chat_messages(sent_at);
CREATE INDEX idx_chat_type ON chat_messages(message_type);

-- =============================================================================
-- PERMISSION EVENTS (replaces permission_events.jsonl)
-- =============================================================================
CREATE TABLE IF NOT EXISTS permission_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    event_type TEXT NOT NULL,        -- PERMISSION_GRANTED, PERMISSION_REVOKED, etc.
    permission_level TEXT,           -- read_only, metrics_write, edit_access_tests, edit_access_src
    granted_at TEXT NOT NULL,
    granted_by TEXT,                 -- 0102, system_automatic, etc.
    confidence REAL,                 -- Confidence score at time of grant
    justification TEXT,
    approval_signature TEXT,         -- SHA256 signature for WSP 50 audit
    metadata_json TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_perm_agent ON permission_events(agent_id);
CREATE INDEX idx_perm_timestamp ON permission_events(granted_at);
CREATE INDEX idx_perm_type ON permission_events(event_type);

-- =============================================================================
-- CONFIDENCE EVENTS (replaces confidence_events.jsonl)
-- =============================================================================
CREATE TABLE IF NOT EXISTS confidence_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    confidence_before REAL,
    confidence_after REAL,
    event_type TEXT NOT NULL,        -- HUMAN_APPROVAL, TESTS_PASSED, ROLLBACK, etc.
    success BOOLEAN,
    validation TEXT,
    recorded_at TEXT NOT NULL,
    metadata_json TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_conf_agent ON confidence_events(agent_id);
CREATE INDEX idx_conf_timestamp ON confidence_events(recorded_at);
CREATE INDEX idx_conf_type ON confidence_events(event_type);

-- =============================================================================
-- DAEMON HEALTH (replaces youtube_dae_heartbeat.jsonl)
-- =============================================================================
CREATE TABLE IF NOT EXISTS daemon_health (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    daemon_name TEXT NOT NULL,
    heartbeat_at TEXT NOT NULL,
    status TEXT NOT NULL,            -- running, stopped, error, degraded
    video_id TEXT,                   -- Current video being processed (if applicable)
    errors_detected INTEGER DEFAULT 0,
    uptime_seconds INTEGER,
    metrics_json TEXT,               -- Flexible metrics storage
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_health_daemon ON daemon_health(daemon_name);
CREATE INDEX idx_health_timestamp ON daemon_health(heartbeat_at);
CREATE INDEX idx_health_status ON daemon_health(status);

-- =============================================================================
-- ERROR EVENTS (replaces system-wide error logging)
-- =============================================================================
CREATE TABLE IF NOT EXISTS error_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_module TEXT NOT NULL,
    raised_at TEXT NOT NULL,
    severity TEXT NOT NULL,          -- CRITICAL, ERROR, WARNING
    error_type TEXT,                 -- ValueError, RuntimeError, etc.
    message TEXT,
    stack_trace TEXT,
    payload_json TEXT,               -- Additional context
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_error_module ON error_events(source_module);
CREATE INDEX idx_error_severity ON error_events(severity);
CREATE INDEX idx_error_timestamp ON error_events(raised_at);
CREATE INDEX idx_error_type ON error_events(error_type);

-- =============================================================================
-- LIBERTYALERT MESH EVENTS (change feed for cross-FoundUp sharing)
-- =============================================================================
CREATE TABLE IF NOT EXISTS mesh_outbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,        -- permission_granted, chat_message, daemon_health, etc.
    source_table TEXT NOT NULL,      -- Which table this event came from
    source_id INTEGER NOT NULL,      -- ID in source table
    payload_json TEXT NOT NULL,      -- Full event data for mesh publishing
    published_at TEXT,               -- When successfully published to mesh (NULL = pending)
    retry_count INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_mesh_pending ON mesh_outbox(published_at) WHERE published_at IS NULL;
CREATE INDEX idx_mesh_type ON mesh_outbox(event_type);

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- Cross-agent analytics: permissions + confidence together
CREATE VIEW IF NOT EXISTS agent_status AS
SELECT
    p.agent_id,
    p.permission_level,
    p.granted_at,
    c.confidence_after as current_confidence,
    c.recorded_at as confidence_updated_at
FROM permission_events p
LEFT JOIN confidence_events c ON p.agent_id = c.agent_id
WHERE p.id = (SELECT MAX(id) FROM permission_events p2 WHERE p2.agent_id = p.agent_id)
  AND c.id = (SELECT MAX(id) FROM confidence_events c2 WHERE c2.agent_id = c.agent_id);

-- Recent daemon health summary
CREATE VIEW IF NOT EXISTS daemon_summary AS
SELECT
    daemon_name,
    status,
    heartbeat_at,
    uptime_seconds,
    errors_detected
FROM daemon_health
WHERE id IN (
    SELECT MAX(id) FROM daemon_health GROUP BY daemon_name
);

-- Error frequency by module
CREATE VIEW IF NOT EXISTS error_summary AS
SELECT
    source_module,
    severity,
    COUNT(*) as error_count,
    MAX(raised_at) as last_error
FROM error_events
WHERE raised_at > datetime('now', '-24 hours')
GROUP BY source_module, severity
ORDER BY error_count DESC;

-- =============================================================================
-- MIGRATION METADATA
-- =============================================================================
CREATE TABLE IF NOT EXISTS migration_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT NOT NULL,            -- chat_history, permissions, etc.
    jsonl_files_migrated INTEGER,
    records_migrated INTEGER,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    status TEXT DEFAULT 'in_progress',  -- in_progress, completed, failed
    error_message TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- =============================================================================
-- INITIAL SCHEMA VERSION
-- =============================================================================
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT DEFAULT (datetime('now')),
    description TEXT
);

INSERT INTO schema_version (version, description) VALUES
(1, 'Initial schema - replaces 219 JSONL files with unified SQLite storage');
