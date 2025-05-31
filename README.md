# FoundUps Agent - YouTube Livestream Co-Host

![FoundUps Logo Placeholder](docs/logo.png) <!-- Add a logo later -->

FoundUps Agent is an open-source, modular AI-powered co-host designed to join YouTube livestreams, engage with the chat, track interactions, and counter misinformation using the **Windsurf Standard Procedures (WSP)** framework.

**Core Mission:** To provide real-time, intelligent engagement in live chats, fostering logical discussion, reinforcing truth, and analyzing social dynamics, ultimately aiming to counter PSYOP-style manipulation.

**Status:** Prototype Phase - **WSP Compliant Architecture** (Core chat listening and logging functional)

## 🏗️ Windsurf Standard Procedures (WSP) Framework

This project is built using the **Windsurf Standard Procedures (WSP)** - a comprehensive development framework that ensures:

- **🧱 Modular "Code LEGO" Architecture**: Standardized module interfaces for seamless composition
- **🎯 Enterprise Domain Organization**: Logical grouping of functionality into enterprise domains
- **🧪 Test-Driven Quality Gates**: Automated compliance and coverage validation  
- **📊 LLME Semantic Rating**: AI-ready semantic assessment of module importance and state
- **🔄 Clean State Management**: Reliable rollback and baseline comparison capabilities
- **⚙️ Automated Compliance**: FMAS (FoundUps Modular Audit System) ensures structural integrity

For detailed WSP documentation, see [`docs/FoundUps_WSP_Framework.md`](docs/FoundUps_WSP_Framework.md).

## Unique Approach: Emoji Sentiment Mapper (ESM)
This agent utilizes the **Emoji Sentiment Mapper (ESM)**, a novel symbolic interpretive layer designed to understand user interaction beyond surface text. ESM maps user statements (sentiment, rhetoric, aggression) to numerical triads corresponding to defined psycho-emotional states on the UN-DAO-DU symbolic axis. This allows the agent to decode user disposition in real-time and select calibrated responses (e.g., roast, truth drop, soft echo) aimed at fostering logical discussion, countering misinformation, and potentially guiding users toward more constructive dialogue, effectively acting as a system for "targeted memetic surgery". *(See `docs/esm_abstract.md` for details)*.

## Features (Current & Planned)

*   **Real-time Chat Monitoring:** Connects to any public YouTube livestream chat.
*   **OAuth Authentication:** Securely logs in as a dedicated Google Account with automatic token rotation.
*   **Persistent Memory:** Logs all chat messages per user in the `memory/` directory (JSONL format).
*   **WSP-Compliant Modular Design:** Easily extensible with new features following enterprise domain patterns.
*   **Multi-Agent System:** Coordinated AI agents for different aspects of chat moderation and engagement.
*   **Docker Support:** Containerized for easy deployment and consistent environments.
*   **(In Progress) AI Integration:** LLM/DeepSeq for intelligent responses, user profiling, fallacy detection.
*   **(Planned) Blockchain Integration:** UndaoDude token rewards via smart contracts for engagement.
*   **(Planned) Gamification:** Trigger mini-games (logic puzzles, etc.) via chat commands.
*   **(Planned) Streamer Dashboard:** Configuration and analytics for bot owners (MVP).

## 🏢 Enterprise Domain Architecture (WSP 3)

The project follows the **WSP 3 Enterprise Domain Architecture**, organizing modules into logical business domains:

```
foundups-agent/
├── 📋 docs/                     # WSP Framework documentation & guides
│   ├── FoundUps_WSP_Framework.md # Complete WSP specification
│   └── clean_states.md          # Clean state history (WSP 2)
├── 🧩 modules/                  # Enterprise Domain Structure (WSP 3)
│   ├── ai_intelligence/         # 🧠 AI & LLM Core Capabilities
│   │   ├── banter_engine/       #   💬 Intelligent conversation generation
│   │   └── multi_agent_system/  #   🤖 Coordinated AI agent management
│   ├── communication/           # 💬 User Interaction & Chat Processing
│   │   └── livechat/            #   📺 YouTube livestream chat integration
│   │       ├── livechat/        #     🔌 Core chat listener module (WSP 1)
│   │       ├── live_chat_processor/ # 🔄 Message processing pipeline
│   │       └── live_chat_poller/    # ⏰ Chat polling mechanisms
│   ├── platform_integration/    # 🌐 External Systems & APIs
│   │   ├── stream_resolver/     #   🔍 Stream identification & metadata
│   │   └── youtube_auth/        #   🔐 YouTube API authentication
│   └── infrastructure/          # ⚙️ Core Systems & Operations
│       ├── agent_management/    #   👥 Multi-agent coordination
│       ├── oauth_management/    #   🔑 OAuth token lifecycle management
│       ├── token_manager/       #   💾 Token storage & rotation
│       └── blockchain_integration/ # ⛓️ Blockchain service integration
├── 🛠️ tools/                   # Development & Maintenance Tools
│   ├── modular_audit/          #   📊 FMAS - Module compliance validation
│   └── testing/                #   🧪 Testing utilities & helpers
├── 🗃️ memory/                  # Persistent chat logs and user data
├── 🔐 credentials/             # OAuth tokens and API keys (gitignored)
├── 📊 reports/                 # Test coverage and audit reports
├── 🔧 utils/                   # Utility functions and logging
├── 🐳 Dockerfile              # Container configuration
├── 📋 main.py                 # Application entry point
├── 📝 ModLog.md               # Module change log (WSP 11)
└── 📦 requirements.txt        # Python dependencies
```

### WSP Module Structure

Each module follows **WSP 1** standardized structure:

```
modules/<domain>/<feature_group>/<module_name>/
├── src/                 # Implementation code
│   ├── __init__.py     # Module exports
│   └── <module>.py     # Main implementation
├── tests/              # Test suite (WSP 6, WSP 14)
│   ├── README.md       # Test documentation (mandatory)
│   └── test_*.py       # Test implementations
├── INTERFACE.md        # API documentation (WSP 12)
├── requirements.txt    # Module dependencies (WSP 13)
└── __init__.py        # Public API definition
```

## 🚀 Getting Started

### Prerequisites

*   **Python 3.8+**
*   **Git**
*   **Docker** (optional, but recommended)
*   **Google Account** (create a dedicated one for the agent)
*   **Google Cloud Project** with YouTube Data API v3 enabled

### Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Foundup/Foundups-Agent.git
    cd Foundups-Agent
    ```

2.  **Set up Google Cloud Credentials:**
    *   Go to the [Google Cloud Console](https://console.cloud.google.com/)
    *   Create a new project or select an existing one
    *   Enable the "YouTube Data API v3"
    *   Go to "Credentials" → Create "OAuth client ID"
        *   Application type: "Desktop app"
        *   Name: e.g., "FoundUps Agent Desktop"
    *   Download the JSON credentials file
    *   **IMPORTANT:** Place it in `foundups-agent/credentials/` directory

3.  **Configure Environment Variables:**
    ```bash
    cp .env.example .env
    # Edit .env file with your credentials and configuration
    ```

4.  **Install Dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

5.  **Validate WSP Compliance** (Optional but recommended):
    ```bash
    # Run FMAS audit to ensure system integrity
    python tools/modular_audit/modular_audit.py ./modules
    
    # Run test suite
    pytest modules/ -v
    ```

### Running the Agent

#### Quick Start (Python)

```bash
# First run (OAuth setup)
python main.py
# Follow browser prompts for authentication

# Subsequent runs
python main.py
```

#### Docker Deployment

```bash
# Build the image
docker build -t foundups-agent .

# Run with mounted volumes
docker run --rm -it \
  -v "$(pwd)/credentials:/app/credentials" \
  -v "$(pwd)/memory:/app/memory" \
  --env-file .env \
  foundups-agent
```

## 🔧 Development Workflow

### WSP Commands & Tools

```bash
# System compliance audit
python tools/modular_audit/modular_audit.py ./modules

# Test coverage verification (WSP 6)
pytest modules/ --cov=modules --cov-report=html

# Create Clean State snapshot (WSP 2)
git tag -a clean-v5 -m "Description"

# Module prioritization scoring (WSP 5)
python prioritize_module.py --report top10
```

### Contributing Guidelines

1. **Follow WSP Standards**: All contributions must comply with WSP framework
2. **Enterprise Domain Placement**: New features go in appropriate enterprise domains
3. **Test Coverage**: Maintain ≥90% test coverage per WSP 6
4. **Interface Definition**: Define clear module interfaces per WSP 12
5. **Conventional Commits**: Use emoji prefixes from WSP 10 (ESM Protocol)

Example commit: `✨ feat(livechat): add circuit breaker for quota management`

## 📊 System Status & Metrics

- **WSP Compliance**: ✅ Fully compliant
- **Test Coverage**: 📈 Target: ≥90% per module
- **Module Count**: 🧩 8+ domains, 10+ modules
- **Architecture Maturity**: 🏗️ Prototype → MVP transition

## 🤝 Contributing

We welcome contributions! Please:

1. Read the [WSP Framework documentation](docs/FoundUps_WSP_Framework.md)
2. Follow the enterprise domain structure
3. Ensure WSP compliance before submitting PRs
4. See our [Contributing Guide](docs/CONTRIBUTING.md) for details

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

* **Google YouTube Data API**
* **The Windsurf Protocol Community**
* **All contributors and supporters**
* **WSP Framework Development Team**

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/Foundup/Foundups-Agent/issues)
- **Documentation**: [`docs/FoundUps_WSP_Framework.md`](docs/FoundUps_WSP_Framework.md)
- **Community**: Join our community discussions

---

**⚡ Quick Links:**
- 📖 [WSP Framework Docs](docs/FoundUps_WSP_Framework.md)
- 🏗️ [Enterprise Architecture Guide](docs/FoundUps_WSP_Framework.md#wsp-3-enterprise-domain-architecture--hierarchical-module-organization)
- 🧪 [Testing Standards](docs/FoundUps_WSP_Framework.md#wsp-6-test-audit--coverage-verification)
- 🔧 [Development Commands](docs/FoundUps_WSP_Framework.md#quick-reference-tables)
