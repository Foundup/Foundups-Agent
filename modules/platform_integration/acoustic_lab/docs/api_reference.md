# Acoustic Lab API Reference

## Overview

The Acoustic Lab provides RESTful API endpoints for educational acoustic triangulation and audio signature analysis. All endpoints follow WSP 84 (Response Formatting Protocol) standards.

## Base URL

```
Production: https://acoustic-lab.edu
Development: http://localhost:8000
```

## Authentication

- **IP Geofencing**: Restricted to Utah state for educational demonstrations
- **No User Authentication**: Public educational access
- **Rate Limiting**: 2 uploads per minute, 10 general requests per second

## Endpoints

### GET /

Educational web interface with drag-and-drop audio upload functionality.

**Response**: HTML page with educational interface
**Content-Type**: `text/html`
**Rate Limit**: 10 req/sec

```html
<!-- Educational Interface -->
<body style="background: black; color: white;">
  <h1>Acoustic Lab - Educational Platform</h1>
  <p>This tool teaches acoustic triangulation and audio fingerprinting.</p>
  <div id="upload-zone">Drag WAV files here</div>
  <div id="results"></div>
</body>
```

### POST /upload

Processes uploaded audio file or X video URL for triangulation and signature analysis.

**Content-Type**: `multipart/form-data`
**Rate Limit**: 2 req/min
**File Size Limit**: 16MB
**Accepted Formats**: WAV files or X video URLs

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `audio` | file | For file upload | WAV audio file with synthetic tones |
| `x_url` | string | For X processing | X/Twitter video post URL |
| `metadata` | JSON string | Yes | GPS coordinates, timestamp, and source info |

#### GPS Data Format

```json
{
  "sensors": [
    {
      "latitude": 40.7608,
      "longitude": -111.8910,
      "timestamp": 1640995200.0,
      "sensor_id": "sensor_1"
    },
    {
      "latitude": 40.7610,
      "longitude": -111.8908,
      "timestamp": 1640995200.1,
      "sensor_id": "sensor_2"
    }
  ]
}
```

#### Response Format

**Success Response (200)**

```json
{
  "success": true,
  "results": {
    "location": {
      "latitude": 40.7609,
      "longitude": -111.8909,
      "confidence": 0.85,
      "error_radius_meters": 15.2
    },
    "sound_type": "Tone A",
    "confidence": 0.92,
    "processing_time_ms": 2340,
    "proof_of_existence": {
      "hash": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
      "ethereum_tx": "simulated_0x1234567890abcdef"
    }
  },
  "educational_notes": {
    "triangulation_method": "Geometric triangulation using time-of-arrival differences",
    "sound_speed_used": "343 m/s (air)",
    "mfcc_features": "13 mel-frequency cepstral coefficients",
    "confidence_threshold": "80% for tone matching"
  }
}
```

**Error Responses**

**400 Bad Request**
```json
{
  "success": false,
  "error": {
    "type": "INVALID_AUDIO",
    "message": "No sharp sound peak detected (>1kHz required for synthetic tones)",
    "details": "Uploaded audio does not contain detectable synthetic tone"
  }
}
```

**403 Forbidden**
```json
{
  "success": false,
  "error": {
    "type": "GEO_RESTRICTED",
    "message": "Access restricted to educational demonstration areas",
    "details": "IP geofencing active - Utah state required for Phase 1"
  }
}
```

**429 Too Many Requests**
```json
{
  "success": false,
  "error": {
    "type": "RATE_LIMITED",
    "message": "Upload rate limit exceeded",
    "details": "Maximum 2 uploads per minute allowed",
    "retry_after": 45
  }
}
```

**500 Internal Server Error**
```json
{
  "success": false,
  "error": {
    "type": "PROCESSING_ERROR",
    "message": "Audio processing failed",
    "details": "Technical details for debugging"
  }
}
```

### GET /health

Service health monitoring endpoint for load balancers and monitoring systems.

**Response**: Plain text health status
**Content-Type**: `text/plain`
**Rate Limit**: Unlimited (for monitoring)

#### Success Response (200)
```
OK - Acoustic Lab operational
Timestamp: 2025-01-15T10:30:00Z
Version: Phase 1.0.0
Uptime: 7 days, 4 hours
```

#### Service Unavailable (503)
```
SERVICE UNAVAILABLE - Database connection failed
Timestamp: 2025-01-15T10:30:00Z
```

## Data Structures

### Location Result

```typescript
interface LocationResult {
  latitude: number;        // WGS84 latitude (-90 to 90)
  longitude: number;       // WGS84 longitude (-180 to 180)
  confidence: number;      // 0.0 to 1.0 confidence score
  error_radius_meters: number; // Estimated accuracy radius
}
```

### Sound Analysis

```typescript
interface SoundAnalysis {
  sound_type: string;      // "Tone A", "Tone B", or "Tone C"
  confidence: number;      // 0.0 to 1.0 matching confidence
  mfcc_features: number[]; // 13 MFCC coefficients
  peak_frequency: number;  // Dominant frequency in Hz
}
```

### Proof of Existence

```typescript
interface ProofOfExistence {
  hash: string;           // SHA-256 hash of analysis results
  ethereum_tx: string;    // Simulated transaction hash
  timestamp: number;      // Unix timestamp
}
```

## Processing Pipeline

### Audio Validation
1. **Format Check**: WAV file validation
2. **Peak Detection**: >1kHz sharp sound required
3. **Duration Check**: Minimum 0.2 seconds
4. **Sample Rate**: 44.1kHz recommended

### Feature Extraction
1. **Windowing**: 0.2-second analysis window
2. **MFCC Computation**: 13 mel-frequency coefficients
3. **Fingerprint Matching**: Library comparison
4. **Confidence Scoring**: Similarity threshold (80%)

### Triangulation
1. **Time-of-Arrival**: Sensor timestamp differences
2. **Geometric Calculation**: Trilateration algorithm
3. **Error Estimation**: Statistical confidence bounds
4. **Location Validation**: Geographic bounds checking

### Blockchain Proof
1. **Result Serialization**: JSON canonical format
2. **SHA-256 Hashing**: Cryptographic proof generation
3. **Testnet Logging**: Simulated Ethereum transaction
4. **Hash Storage**: Educational proof-of-existence

## Error Handling

### Client Errors (4xx)
- **400**: Invalid audio format or missing GPS data
- **403**: Geographic access restriction
- **413**: File size exceeds 16MB limit
- **415**: Unsupported file format (non-WAV)
- **429**: Rate limit exceeded

### Server Errors (5xx)
- **500**: Audio processing failure
- **502**: Upstream service unavailable
- **503**: Service temporarily unavailable
- **504**: Processing timeout (>60 seconds)

## Security Considerations

### Input Validation
- File type verification (WAV only)
- Size limits (16MB maximum)
- Content scanning (synthetic audio only)
- GPS coordinate bounds checking

### Rate Limiting
- Per-IP address limiting
- Burst allowance for educational use
- Exponential backoff for violations
- Administrative override capability

### Geographic Restrictions
- IP-based geofencing to Utah
- Free IP geolocation service
- Educational demonstration focus
- Privacy-preserving implementation

## Performance Characteristics

### Processing Times
- **Audio Analysis**: 1-3 seconds
- **Triangulation**: <100ms
- **Fingerprint Matching**: <500ms
- **Blockchain Proof**: <50ms

### Resource Usage
- **Memory**: <256MB per request
- **CPU**: <1 second processing time
- **Storage**: In-memory only (no persistence)
- **Network**: <10KB response size

## Educational Integration

### Learning Outcomes
- Understand acoustic triangulation mathematics
- Apply signal processing to real-world problems
- Learn blockchain proof-of-existence concepts
- Practice scientific method in audio analysis

### Assessment Integration
- Automated grading of triangulation accuracy
- Confidence score evaluation
- Processing time optimization
- Error analysis and interpretation

---

**Acoustic Lab API Reference - Complete Technical Documentation**
**WSP 84 Compliant Response Formatting**
**Educational Platform for Acoustic Research**
