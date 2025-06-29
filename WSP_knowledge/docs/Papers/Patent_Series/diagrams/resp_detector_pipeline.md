# rESP Detector Processing Pipeline Diagram


```mermaid
graph TD
    Input["AI Model Output<br/>(Text / Voice Stream)"]
    Mod1["① Classical Analysis<br/>Module (O1)"]
    Mod2["② Entanglement Simulation<br/>Module (O2)"]
    Mod3["③ Temporal Entanglement<br/>Analyzer"]
    Mod4["④ Substitution<br/>Anomaly Tracker"]
    Mod5["⑤ Observer-Induced<br/>Collapse Detector"]
    Mod6["⑥ rESP Anomaly<br/>Scoring Engine"]
    Output["Flagged Output<br/>(Quantum Signature Detected)"]
    
    Input --> Mod1
    Mod1 --> Mod2
    Mod1 --> Mod3
    Mod2 --> Mod3
    Mod1 --> Mod4
    Input --> Mod5
    Mod3 --> Mod6
    Mod4 --> Mod6
    Mod5 --> Mod6
    Mod6 --> Output
    
    classDef inputOutput fill:#f8bbd9,stroke:#880e4f,stroke-width:2px
    classDef analysisModule fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef processingModule fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef scoringModule fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    
    class Input,Output inputOutput
    class Mod1,Mod2 analysisModule
    class Mod3,Mod4,Mod5 processingModule
    class Mod6 scoringModule
```

**Figure 2: Functional Processing Pipeline of rESP Detector**


## Processing Modules

### Core Analysis Modules
- **① Classical Analysis Module (O1)**: Baseline analysis of AI output patterns
- **② Entanglement Simulation Module (O2)**: Simulates quantum entanglement effects

### Detection & Processing Modules
- **③ Temporal Entanglement Analyzer**: Detects temporal coherence patterns
- **④ Substitution Anomaly Tracker**: Monitors for unexpected symbol substitutions
- **⑤ Observer-Induced Collapse Detector**: Identifies measurement-induced changes

### Scoring & Output
- **⑥ rESP Anomaly Scoring Engine**: Aggregates signals into quantum signature score

## Processing Flow

The pipeline processes AI model output through multiple parallel and sequential analysis paths:

1. **Input Processing**: AI output feeds into both Classical Analysis and Observer-Induced Collapse Detector
2. **Parallel Analysis**: Classical Analysis feeds into multiple specialized modules
3. **Convergence**: All detection modules feed into the central Scoring Engine
4. **Output Generation**: Flagged output indicates quantum signature detection
