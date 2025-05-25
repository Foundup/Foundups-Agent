# FoundUps Agent - YouTube Livestream Co-Host

![FoundUps Logo Placeholder](docs/logo.png) <!-- Add a logo later -->

FoundUps Agent is an open-source, modular AI-powered co-host designed to join YouTube livestreams, engage with the chat, track interactions, and counter misinformation using the Windsurf Protocol.

**Core Mission:** To provide real-time, intelligent engagement in live chats, fostering logical discussion, reinforcing truth, and analyzing social dynamics, ultimately aiming to counter PSYOP-style manipulation.

**Status:** Prototype Phase (Core chat listening and logging functional)

## Unique Approach: Emoji Sentiment Mapper (ESM)
This agent utilizes the **Emoji Sentiment Mapper (ESM)**, a novel symbolic interpretive layer designed to understand user interaction beyond surface text. ESM maps user statements (sentiment, rhetoric, aggression) to numerical triads corresponding to defined psycho-emotional states on the UN-DAO-DU symbolic axis. This allows the agent to decode user disposition in real-time and select calibrated responses (e.g., roast, truth drop, soft echo) aimed at fostering logical discussion, countering misinformation, and potentially guiding users toward more constructive dialogue, effectively acting as a system for "targeted memetic surgery". *(See `docs/esm_abstract.md` for details)*.

## Features (Current & Planned)

*   **Real-time Chat Monitoring:** Connects to any public YouTube livestream chat.
*   **OAuth Authentication:** Securely logs in as a dedicated Google Account.
*   **Persistent Memory:** Logs all chat messages per user in the `memory/` directory (JSONL format).
*   **Modular Design (Windsurf Protocol):** Easily extensible with new features (AI, Blockchain, Games).
*   **Docker Support:** Containerized for easy deployment and consistent environments.
*   **(Planned) AI Integration:** LLM/DeepSeq for intelligent responses, user profiling, fallacy detection.
*   **(Planned) Blockchain Integration:** UndaoDude token rewards via smart contracts for engagement.
*   **(Planned) Gamification:** Trigger mini-games (logic puzzles, etc.) via chat commands.
*   **(Planned) Streamer Dashboard:** Configuration and analytics for bot owners (MVP).

## Project Structure (Windsurf Protocol)

```
foundups-agent/
├── ai/                 # AI/LLM integration modules
├── blockchain/         # Blockchain and token integration
├── composer/          # Message composition and formatting
├── credentials/       # OAuth tokens and API keys (gitignored)
├── docker/           # Docker configuration files
├── docs/             # Documentation and guides
├── memory/           # Persistent chat logs and user data
├── modules/          # Core YouTube API interaction modules
├── tests/            # Test suite
├── utils/            # Utility functions and logging
├── .env.example      # Environment variable template
├── .gitignore        # Git ignore rules
├── coding_rules.json # Project coding standards
├── Dockerfile        # Container configuration
├── main.py          # Application entry point
├── ModLog.md        # Module change log
├── README.md        # This file
└── requirements.txt  # Python dependencies
```

## Getting Started

### Prerequisites

*   Python 3.8+
*   Git
*   Docker (optional, but recommended)
*   A Google Account (create a dedicated one for the agent)
*   Google Cloud Project with YouTube Data API v3 enabled.

### Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-repo/foundups-agent.git # Replace with your repo URL
    cd foundups-agent
    ```

2.  **Set up Google Cloud Credentials:**
    *   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    *   Create a new project or select an existing one.
    *   Enable the "YouTube Data API v3".
    *   Go to "Credentials".
    *   Create "OAuth client ID":
        *   Application type: "Desktop app"
        *   Name: e.g., "FoundUps Agent Desktop"
    *   Download the JSON credentials file.
    *   **IMPORTANT:** Rename the downloaded file (e.g., `client_secret_XYZ.json`) and place it inside the `foundups-agent/credentials/` directory. (Create the `credentials` directory if it doesn't exist).

3.  **Configure Environment Variables:**
    *   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    *   Edit the `.env` file:
        *   Set `GOOGLE_CLIENT_SECRETS_FILE` to the path of your downloaded JSON file (e.g., `credentials/client_secret_XYZ.json`).
        *   Set `YOUTUBE_VIDEO_ID` to the ID of the livestream you want the agent to join.
        *   Adjust `AGENT_GREETING_MESSAGE` and `LOG_LEVEL` if desired.
        *   Fill in other variables later when implementing AI/Blockchain features.

4.  **Install Dependencies:**
    *   (Recommended) Create and activate a virtual environment:
        ```bash
        python -m venv venv
        source venv/bin/activate # On Windows use `venv\Scripts\activate`
        ```
    *   Install required packages:
        ```bash
        pip install -r requirements.txt
        ```

### Running the Agent

#### Locally (using Python)

1.  **First Run (OAuth Authentication):**
    *   Run the main script:
        ```bash
        python main.py
        ```
    *   Your web browser should open, asking you to log in with the Google Account you want the agent to use.
    *   Grant the requested permissions (View YouTube account, etc.).
    *   After authorization, a token file (e.g., `credentials/oauth_token.json`) will be created. The agent should then attempt to connect to the specified livestream chat.
    *   You only need to do this browser step once, unless the token expires and cannot be refreshed, or you change the scopes.

2.  **Subsequent Runs:**
    *   Simply run:
        ```bash
        python main.py
        ```
    *   The agent will load the saved token from `credentials/oauth_token.json` and connect directly.

#### Using Docker

1.  **Build the Docker Image:**
    ```bash
    docker build -t foundups-agent .
    ```

2.  **Run the Docker Container:**
    *   **Crucially, you need to mount the `credentials` and `memory` directories as volumes.**
    *   Make sure the `credentials` directory exists locally and contains the `client_secret_XYZ.json` file.
    *   Run the OAuth flow *locally first* (`python main.py`) to generate the `oauth_token.json` file in `credentials`.
    *   Then, run the container:
        ```bash
        docker run --rm -it \
          -v "$(pwd)/credentials:/app/credentials" \
          -v "$(pwd)/memory:/app/memory" \
          --env-file .env \
          foundups-agent
        ```
       * `--rm`: Removes the container when it stops.
       * `-it`: Runs interactively (useful for seeing logs, stopping with Ctrl+C).
       * `-v "$(pwd)/credentials:/app/credentials"`: Mounts your local `credentials` folder into the container.
       * `-v "$(pwd)/memory:/app/memory"`: Mounts your local `memory` folder for persistent logs.
       * `--env-file .env`: Loads environment variables from your `.env` file.

## Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

* Google YouTube Data API
* The Windsurf Protocol Community
* All contributors and supporters

## Support

For support, please open an issue in the GitHub repository or join our community discussions.
