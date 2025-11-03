# Acoustic Lab - Architecture Design & Implementation

## System Architecture Overview

The Acoustic Lab implements a microservices-inspired architecture within a single Flask application, designed for educational acoustic triangulation and audio signature analysis. The system follows WSP 49 (Module Structure Protocol) with clear separation of concerns and modular component design.

## Core Architectural Principles

### 1. Educational-First Design
- **Synthetic Data Focus**: All processing designed around synthetic audio datasets
- **Transparency**: Clear visibility into algorithmic processes and decision-making
- **Safety Boundaries**: Strict constraints preventing real-world data processing
- **Learning Objectives**: Architecture designed to teach acoustic principles

### 2. Memory-First Processing
- **Zero Persistence**: No disk storage of audio data or results
- **In-Memory Operations**: All processing occurs in RAM with immediate cleanup
- **Resource Efficiency**: Minimal memory footprint with streaming processing
- **Security by Design**: No persistent data reduces attack surface

### 3. Modular Component Architecture
```
Acoustic Lab
+-- Input Processing Layer
[U+2502]   +-- File Upload Handler
[U+2502]   +-- X Video Processor
+-- Analysis Engine
[U+2502]   +-- Audio Processor
[U+2502]   +-- Fingerprint Library
[U+2502]   +-- Triangulation Engine
+-- Security Layer
[U+2502]   +-- IP Geofencing
[U+2502]   +-- Rate Limiting
[U+2502]   +-- Input Validation
+-- Output Layer
    +-- Results Formatter
    +-- Ethereum Logger
```

## Component Design Details

### Input Processing Layer

#### File Upload Handler
**Purpose**: Handle direct WAV file uploads with validation
**Design Decisions**:
- **Format Restriction**: WAV only to ensure Librosa compatibility
- **Size Limits**: 16MB maximum to prevent abuse
- **Memory Streaming**: Direct BytesIO processing without temp files
- **Validation Chain**: Format -> Size -> Content -> Processing

#### X Video Processor
**Purpose**: Extract and process audio from X (Twitter) video URLs
**Design Decisions**:
- **URL Validation**: Strict x.com/twitter.com domain checking
- **Memory Downloads**: yt-dlp with in-memory processing
- **Audio Extraction**: ffmpeg subprocess with time limits (3s)
- **Fallback Handling**: Graceful degradation for processing failures

### Analysis Engine

#### Audio Processor (`acoustic_processor.py`)
**Core Algorithm Flow**:
```
Input Audio -> Peak Detection -> Window Extraction -> MFCC -> Fingerprint Matching -> Triangulation
```

**Key Design Decisions**:
- **Peak Detection**: >1kHz threshold identifies synthetic tone events
- **Window Size**: 0.2-second windows capture complete tone signatures
- **MFCC Configuration**: 13 coefficients, 44.1kHz sampling for consistency
- **Confidence Threshold**: 80% minimum match for educational demonstration

#### Audio Library (`audio_library.py`)
**Fingerprint Database Design**:
```python
SYNTHETIC_TONES = {
    'Tone A': {'frequency': 1000, 'pattern': 'sine_wave'},
    'Tone B': {'frequency': 1500, 'pattern': 'square_wave'},
    'Tone C': {'frequency': 2000, 'pattern': 'sawtooth_wave'}
}
```

**Design Decisions**:
- **Pre-computed Fingerprints**: MFCC vectors calculated at startup
- **Similarity Matching**: Cosine distance for pattern comparison
- **Educational Labels**: Clear tone identification for learning
- **Extensibility**: Easy addition of new synthetic signatures

#### Triangulation Engine (`triangulation_engine.py`)
**Geometric Algorithm**:
```
Time-of-Arrival Triangulation:
1. Calculate time differences between sensor detections
2. Convert time delays to distance differences (speed of sound)
3. Solve geometric intersection of sensor circles
4. Apply error estimation and confidence scoring
```

**Design Decisions**:
- **Speed of Sound**: 343 m/s (air at 20°C) for accuracy
- **Geometric Method**: Circle intersection for 3+ sensor scenarios
- **Error Propagation**: Statistical confidence bounds
- **Educational Output**: Step-by-step calculation visibility

### Security Layer

#### IP Geofencing Implementation
**Geographic Restriction Logic**:
```python
def check_ip_geofencing(client_ip: str) -> None:
    # Free IP geolocation service
    location = get_location(client_ip)

    # Utah state restriction for educational access
    if location.region != 'UT':
        raise IPGeofencingError(f"Access restricted to Utah state")
```

**Design Decisions**:
- **Service Choice**: ip-api.com for free, reliable geolocation
- **Graceful Degradation**: Allow access if service unavailable
- **Educational Focus**: Utah restriction for demonstration purposes
- **Privacy Conscious**: No IP storage or tracking

#### Rate Limiting Architecture
**Multi-Layer Protection**:
- **Global Limits**: 10 req/sec general, 2 req/min uploads
- **IP-Based Tracking**: Per-client rate enforcement
- **Burst Allowance**: Short-term spikes with smoothing
- **Educational Throttling**: Prevent resource exhaustion

### Output Layer

#### Results Formatting
**Educational Response Structure**:
```json
{
  "location": [lat, lng],
  "sound_type": "Tone A",
  "confidence": 0.92,
  "triangulation_data": {
    "sensors_used": 3,
    "error_estimate": 5.2
  },
  "source": "x_video|direct_upload",
  "ethereum_hash": "sha256_proof"
}
```

**Design Decisions**:
- **Structured Output**: Clear separation of result components
- **Educational Labels**: Human-readable field names
- **Source Tracking**: Input method identification
- **Proof Integration**: Cryptographic verification included

#### Ethereum Logger (`ethereum_logger.py`)
**Blockchain Proof-of-Existence**:
```python
class EthereumLogger:
    def log_acoustic_analysis(self, results: dict) -> str:
        # Generate SHA-256 hash of analysis results
        hash_value = sha256(json.dumps(results, sort_keys=True))

        # Simulate Ethereum testnet transaction
        tx_hash = simulate_ethereum_transaction(hash_value)

        return tx_hash
```

**Design Decisions**:
- **Educational Demonstration**: Simulated transactions for learning
- **Cryptographic Integrity**: SHA-256 proof generation
- **Testnet Focus**: No mainnet transactions or real costs
- **Non-Blocking**: Logging failures don't affect analysis

## Implementation Patterns

### Error Handling Strategy
**Comprehensive Exception Hierarchy**:
```
AcousticLabError (Base)
+-- AudioValidationError (Invalid audio format/content)
+-- GPSValidationError (Missing/invalid coordinates)
+-- IPGeofencingError (Geographic access restriction)
+-- XProcessingError (Video download/extraction failure)
+-- TriangulationError (Geometric calculation failure)
```

**Design Decisions**:
- **Specific Exceptions**: Clear error categorization
- **Educational Messages**: Helpful error descriptions
- **Graceful Degradation**: Partial failures handled gracefully
- **Logging Integration**: All errors logged for analysis

### Memory Management
**Zero-Copy Processing**:
```python
def process_audio(audio_bytes: bytes) -> dict:
    # Direct BytesIO processing
    with io.BytesIO(audio_bytes) as audio_buffer:
        # Process without copying
        results = analyze_buffer(audio_buffer)

    # Immediate cleanup
    del audio_bytes
    return results
```

**Design Decisions**:
- **Memory Efficiency**: Direct buffer processing
- **No Persistence**: All data cleaned up immediately
- **Resource Limits**: Explicit memory constraints
- **GC Optimization**: Manual cleanup where beneficial

### Performance Optimization
**Streaming Processing Pipeline**:
```
Input -> Validation -> Feature Extraction -> Matching -> Triangulation -> Output
     v         v             v            v           v          v
   <100ms    <200ms       <500ms       <100ms     <50ms     <10ms
```

**Design Decisions**:
- **Bottleneck Identification**: Feature extraction is the main cost
- **Optimization Focus**: MFCC computation efficiency
- **Memory Constraints**: Processing limits prevent resource exhaustion
- **Timeout Protection**: Maximum processing time limits

## Data Flow Architecture

### File Upload Flow
```
User Upload -> IP Check -> File Validation -> Audio Processing -> Results -> Ethereum Log -> Response
      v          v            v              v            v          v          v
   Browser    Geofence    Format/Size    MFCC/Matching  JSON     SHA-256    Client
```

### X Video Flow
```
X URL -> IP Check -> URL Validation -> yt-dlp Download -> ffmpeg Extract -> Audio Processing -> Results
    v        v            v                v                v              v            v
 Browser   Geofence     Domain Check     Memory Buffer    WAV Bytes     Analysis     JSON
```

## Security Architecture

### Defense in Depth
**Multiple Security Layers**:
1. **Network Level**: IP geofencing and rate limiting
2. **Input Level**: Format validation and size restrictions
3. **Processing Level**: Memory-only operations, no persistence
4. **Output Level**: Safe JSON responses, no sensitive data leakage

### Threat Mitigation
- **DoS Prevention**: Rate limiting and resource limits
- **Data Exfiltration**: No persistent storage
- **Code Injection**: Input validation and safe processing
- **Resource Exhaustion**: Memory and time limits

## Scalability Considerations

### Vertical Scaling
- **CPU Intensive**: Audio processing benefits from faster cores
- **Memory Efficient**: Low memory footprint allows more concurrent users
- **I/O Light**: Network and disk I/O minimal
- **Container Ready**: Docker-compatible for easy deployment

### Horizontal Scaling
- **Stateless Design**: No session state to manage
- **Load Balancer Ready**: nginx upstream configuration ready
- **Database Optional**: Phase 1 operates without persistence
- **Service Discovery**: Ready for microservices evolution

## Testing Architecture

### Unit Test Coverage
**Component Isolation**:
- **Audio Library**: Fingerprint matching accuracy
- **Triangulation Engine**: Geometric calculation correctness
- **IP Geofencing**: Geographic restriction logic
- **X Processing**: Video download and extraction

### Integration Testing
**End-to-End Flows**:
- **File Upload Pipeline**: Complete processing chain
- **X Video Pipeline**: URL to results workflow
- **Error Scenarios**: Failure mode handling
- **Performance Benchmarks**: Timing and resource usage

### Educational Validation
**Learning Objectives Testing**:
- **Triangulation Accuracy**: Geometric calculation validation
- **Fingerprint Recognition**: Tone identification reliability
- **Processing Transparency**: Clear result presentation
- **Safety Boundaries**: Restriction enforcement

## Deployment Architecture

### Production Stack
```
Client Browser -> Nginx (SSL/TLS) -> Gunicorn -> Flask App -> Analysis Pipeline -> Response
       v             v              v          v              v            v
     HTTPS        Reverse Proxy   WSGI Server  Routes    Processing   JSON/Errors
```

### Infrastructure Requirements
- **Compute**: 1 vCPU, 2GB RAM (Phase 1 conservative)
- **Storage**: 10GB for application and logs
- **Network**: Standard bandwidth for educational traffic
- **Security**: SSL certificates and firewall configuration

### Monitoring Integration
**Observability Stack**:
- **Application Metrics**: Health endpoints and processing stats
- **System Monitoring**: CPU, memory, and disk usage
- **Error Tracking**: Exception logging and alerting
- **Performance Profiling**: Response time and throughput tracking

## Future Evolution Path

### Phase 2 Enhancements
- **Client-Side Processing**: WebAssembly audio analysis
- **Real-Time Visualization**: Canvas-based triangulation display
- **Enhanced UI/UX**: Progressive Web App features
- **Offline Capability**: Service worker caching

### Phase 3 Production Features
- **Multi-User Platform**: User accounts and session management
- **Database Integration**: Result persistence and analytics
- **Advanced Analytics**: Performance metrics and usage patterns
- **API Expansion**: Third-party integration capabilities

### Architectural Scaling
- **Microservices Evolution**: Component separation for scale
- **Container Orchestration**: Kubernetes for multi-region deployment
- **CDN Integration**: Global content delivery optimization
- **Advanced Security**: WAF and intrusion detection

## Implementation Quality Assurance

### Code Quality Standards
- **Type Hints**: Full Python typing for maintainability
- **Documentation**: Comprehensive docstrings and comments
- **Error Handling**: Robust exception management
- **Testing Coverage**: >90% test coverage target

### Performance Benchmarks
**Target Metrics**:
- **Response Time**: <5 seconds for typical audio files
- **Memory Usage**: <256MB per concurrent analysis
- **CPU Efficiency**: Minimal background processing
- **Error Rate**: <1% for valid inputs

### Security Validation
**Regular Assessments**:
- **Dependency Scanning**: Automated vulnerability detection
- **Input Fuzzing**: Boundary condition testing
- **Access Pattern Analysis**: Usage monitoring for anomalies
- **Code Review**: Security-focused implementation review

---

**Acoustic Lab Architecture Design & Implementation**
**Educational Platform with Production-Grade Architecture**
**WSP 49 Compliant - Scalable and Maintainable Design**

