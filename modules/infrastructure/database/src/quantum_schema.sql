-- WSP 78 Quantum Schema Extensions for AgentDB
-- Phase 1: Non-Breaking Additions for Quantum Support
-- Enables Grover's Algorithm (O(√N) search) and Quantum Attention
-- Date: 2025-09-27
-- Token Budget: ~5K tokens (Phase 1)

-- ============================================================================
-- QUANTUM STATE TABLES
-- ============================================================================

-- Quantum states for patterns (supports superposition)
CREATE TABLE IF NOT EXISTS quantum_states (
    state_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern TEXT,                  -- Pattern being represented
    state_vector BLOB,             -- Packed binary amplitudes (complex numbers)
    coherence_score REAL,          -- Decoherence measure (0-1)
    dimension INTEGER,             -- Size of Hilbert space
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_measured DATETIME,
    measurement_result TEXT        -- Collapsed state after measurement
);

-- Index for pattern lookups
CREATE INDEX IF NOT EXISTS idx_quantum_pattern ON quantum_states(pattern);

-- ============================================================================
-- GROVER'S ALGORITHM ORACLE TABLES
-- ============================================================================

-- Oracle marking for Grover's search
CREATE TABLE IF NOT EXISTS quantum_oracles (
    oracle_id INTEGER PRIMARY KEY,
    pattern_type TEXT,             -- 'vibecode', 'duplicate', 'wsp_violation'
    pattern_hash INTEGER,          -- Hash for O(1) lookup
    phase_inversion REAL DEFAULT -1.0,  -- Marked states get phase flip
    marked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    confidence REAL DEFAULT 1.0    -- Confidence in marking (0-1)
);

-- Critical index for oracle performance (enables O(1) marking checks)
CREATE INDEX IF NOT EXISTS idx_oracle_hash ON quantum_oracles(pattern_hash)
    WHERE phase_inversion = -1.0;

-- ============================================================================
-- QUANTUM AMPLITUDE STORAGE
-- ============================================================================

-- Individual amplitude storage for debugging/visualization
CREATE TABLE IF NOT EXISTS quantum_amplitudes (
    amplitude_id INTEGER PRIMARY KEY,
    state_id INTEGER,              -- Foreign key to quantum_states
    basis_state TEXT,              -- |0>, |1>, |00>, |01>, etc.
    real_part REAL,               -- Real component
    imaginary_part REAL,          -- Imaginary component
    magnitude REAL GENERATED ALWAYS AS (sqrt(real_part*real_part + imaginary_part*imaginary_part)),
    phase REAL,                    -- Phase angle in radians
    FOREIGN KEY (state_id) REFERENCES quantum_states(state_id)
);

-- Index for state lookups
CREATE INDEX IF NOT EXISTS idx_amplitude_state ON quantum_amplitudes(state_id);

-- ============================================================================
-- QUANTUM ATTENTION MECHANISM
-- ============================================================================

-- Quantum attention weights for pattern matching
CREATE TABLE IF NOT EXISTS quantum_attention (
    attention_id INTEGER PRIMARY KEY,
    query_pattern TEXT,            -- Query being attended to
    key_pattern TEXT,              -- Key being matched against
    attention_weight BLOB,         -- Complex amplitude weight
    entanglement_score REAL,       -- Quantum entanglement measure (0-1)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for query-key lookups
CREATE INDEX IF NOT EXISTS idx_quantum_attention_qk ON quantum_attention(query_pattern, key_pattern);

-- ============================================================================
-- QUANTUM MEASUREMENT HISTORY
-- ============================================================================

-- Track measurements for decoherence analysis
CREATE TABLE IF NOT EXISTS quantum_measurements (
    measurement_id INTEGER PRIMARY KEY,
    state_id INTEGER,
    measured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    basis TEXT,                    -- Measurement basis (computational, Hadamard, etc.)
    outcome TEXT,                  -- Measurement result
    probability REAL,              -- Probability of this outcome
    decoherence_factor REAL,       -- How much coherence was lost
    FOREIGN KEY (state_id) REFERENCES quantum_states(state_id)
);

-- ============================================================================
-- QUANTUM ENTANGLEMENT MAPPING
-- ============================================================================

-- Track entangled states for quantum correlation
CREATE TABLE IF NOT EXISTS quantum_entanglement (
    entanglement_id INTEGER PRIMARY KEY,
    state_id_1 INTEGER,
    state_id_2 INTEGER,
    entanglement_type TEXT,        -- 'Bell', 'GHZ', 'W', 'custom'
    correlation_strength REAL,     -- Strength of entanglement (0-1)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id_1) REFERENCES quantum_states(state_id),
    FOREIGN KEY (state_id_2) REFERENCES quantum_states(state_id)
);

-- ============================================================================
-- BACKWARD COMPATIBLE EXTENSIONS TO EXISTING TABLES
-- ============================================================================

-- Add quantum fields to breadcrumbs (NULL by default - won't break existing code)
ALTER TABLE agents_breadcrumbs ADD COLUMN quantum_state_id INTEGER;
ALTER TABLE agents_breadcrumbs ADD COLUMN amplitude_vector BLOB;
ALTER TABLE agents_breadcrumbs ADD COLUMN coherence_score REAL;

-- Add quantum fields to patterns (NULL by default)
ALTER TABLE agents_memory ADD COLUMN quantum_encoded BLOB;
ALTER TABLE agents_memory ADD COLUMN superposition_count INTEGER;

-- Add quantum fields to contracts (NULL by default)
ALTER TABLE agents_contracts ADD COLUMN quantum_priority BLOB;
ALTER TABLE agents_contracts ADD COLUMN entangled_contracts TEXT;

-- ============================================================================
-- VIEWS FOR QUANTUM ANALYSIS
-- ============================================================================

-- View for active quantum states with high coherence
CREATE VIEW IF NOT EXISTS active_quantum_states AS
SELECT
    qs.*,
    COUNT(qm.measurement_id) as measurement_count,
    AVG(qm.decoherence_factor) as avg_decoherence
FROM quantum_states qs
LEFT JOIN quantum_measurements qm ON qs.state_id = qm.state_id
WHERE qs.coherence_score > 0.7
GROUP BY qs.state_id;

-- View for marked oracle patterns
CREATE VIEW IF NOT EXISTS marked_patterns AS
SELECT
    qo.*,
    qs.state_vector,
    qs.coherence_score
FROM quantum_oracles qo
LEFT JOIN quantum_states qs ON qo.pattern_type = qs.pattern
WHERE qo.phase_inversion = -1.0
ORDER BY qo.confidence DESC;

-- View for entangled state pairs
CREATE VIEW IF NOT EXISTS entangled_pairs AS
SELECT
    qe.*,
    qs1.pattern as pattern_1,
    qs2.pattern as pattern_2,
    qs1.coherence_score as coherence_1,
    qs2.coherence_score as coherence_2
FROM quantum_entanglement qe
JOIN quantum_states qs1 ON qe.state_id_1 = qs1.state_id
JOIN quantum_states qs2 ON qe.state_id_2 = qs2.state_id
WHERE qe.correlation_strength > 0.5;

-- ============================================================================
-- PERFORMANCE INDEXES
-- ============================================================================

-- Partial index for high-coherence states (most queries)
CREATE INDEX IF NOT EXISTS idx_high_coherence ON quantum_states(coherence_score)
    WHERE coherence_score > 0.5;

-- Partial index for recent measurements
CREATE INDEX IF NOT EXISTS idx_recent_measurements ON quantum_measurements(measured_at)
    WHERE measured_at > datetime('now', '-7 days');

-- Composite index for quantum attention lookups
CREATE INDEX IF NOT EXISTS idx_attention_composite ON quantum_attention(
    query_pattern, key_pattern, entanglement_score
);

-- ============================================================================
-- TRIGGERS FOR COHERENCE MANAGEMENT
-- ============================================================================

-- Automatically update coherence on measurement
CREATE TRIGGER IF NOT EXISTS update_coherence_on_measurement
AFTER INSERT ON quantum_measurements
BEGIN
    UPDATE quantum_states
    SET coherence_score = coherence_score * (1 - NEW.decoherence_factor),
        last_measured = NEW.measured_at
    WHERE state_id = NEW.state_id;
END;

-- ============================================================================
-- METADATA
-- ============================================================================

-- Track schema version for migrations
CREATE TABLE IF NOT EXISTS quantum_schema_metadata (
    version TEXT PRIMARY KEY,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Record this schema application
INSERT OR IGNORE INTO quantum_schema_metadata (version, description)
VALUES ('1.0.0', 'Initial quantum schema - Phase 1 non-breaking additions');

-- ============================================================================
-- NOTES FOR IMPLEMENTATION
-- ============================================================================
-- 1. BLOB fields store packed binary complex numbers using struct.pack('dd', real, imag)
-- 2. Pattern hashes use Python's hash() function for O(1) oracle lookups
-- 3. Coherence scores decay with measurements (decoherence simulation)
-- 4. All new columns are nullable - existing code won't break
-- 5. Indexes optimized for quantum search operations
-- 6. Views provide convenient access to quantum data
-- 7. Triggers automate coherence management