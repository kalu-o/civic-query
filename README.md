# CivicQuery: AI-Powered Civic Information Assistant

> 🏆 **Submitted to the G7 GovAI Challenge**

**CivicQuery** is a sovereign, voice-first AI assistant designed to bridge the digital divide in public administration. It leverages **Verifiable Retrieval-Augmented Generation (RAG)**, local LLMs (via Ollama), and Web API speech interfaces to provide accurate, legally cited answers to citizen queries.

Unlike standard cloud chatbots, **CivicQuery** runs entirely on-premise. It is architected for **GDPR compliance** and **Data Sovereignty**, ensuring that sensitive citizen data never leaves the municipal infrastructure.

<img width="212" height="392" alt="1" src="https://github.com/user-attachments/assets/9fe1e571-8de1-482e-8e0f-93d8edb16123" />


## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Features

-   **🎙️ Voice-First Interface:** accessible Speech-to-Speech interaction for the elderly and visually impaired.
-   **🔒 Data Sovereignty:** Runs 100% offline/on-premise using **Ollama** (Llama 3 / Mistral). No data is sent to OpenAI or cloud providers.
-   **⚖️ Verifiable RAG:** "Citation-First" architecture. The AI refuses to hallucinate and links every answer to specific government documents (PDF/HTML).
-   **⚡ Real-Time Streaming:** Built on **WebSockets** for low-latency voice interaction.
-   **🐳 Containerized:** Fully Dockerized stack for easy deployment across any G7 municipal IT environment.

## Architecture

1.  **Client/Frontend**:
    -   Built with **HTML5 & Vanilla JavaScript**.
    -   Uses the **Web Speech API** for browser-based ASR (Speech Recognition) and TTS (Synthesis).
    -   Communicates with the backend via **WebSockets** for real-time token streaming.

2.  **Server/Backend**:
    -   **API Framework:** FastAPI (Python).
    -   **Orchestration:** LangChain.
    -   **Vector Store:** ChromaDB (Local).

3.  **Inference Engine**:
    -   **Ollama**: Runs as a sidecar container to host local LLMs (Llama 3, Mistral, Phi-3).

## Prerequisites

-   **Docker Desktop** (or Docker Engine on Linux)
-   **Poetry** (for local Python dependency management)
-   *(Optional)* **NVIDIA GPU** for lower latency inference.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/kalu-o/civic-query.git
cd civic-query
```

### 2. Set Up the Environment

Install Poetry if you haven't already:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Install dependencies:

```bash
poetry install
```

## Configuration

CivicQuery is designed to run without external proprietary API keys. Configuration is handled via environment variables (or a `.env` file).

**Key Variables:**

```ini
# RAG Settings
CHUNK_SIZE=1500
CHUNK_OVERLAP=200
RETURN_SOURCE_DOCUMENTS=True  # Critical for Citation Feature

# Model Settings
LLM_TYPE=llama3              # Options: llama3, mistral, phi3
EMBEDDING_LLM_TYPE=all-MiniLM-L6-v2
OLLAMA_BASE_URL=http://ollama:11434
```

## Deployment (Docker)

The recommended way to run CivicQuery is via Docker Compose, which spins up both the App and the Ollama inference engine.

### 1. Build and Run

```bash
docker compose -f docker-compose-ollama.build.yml up -d --build
```

### 2. Download the Model (First Run Only)

Since the system is offline capable, you must pull the model into the container once:

```bash
docker exec -it ollama ollama run llama3
# Wait for the ">>>" prompt, then press Ctrl+D to exit.
```

### 3. Access the Application

Open your browser and navigate to:
`http://localhost:8001`

*Note: The FastAPI documentation (Swagger UI) is available at `http://localhost:8001/docs`.*

## Development

### Running Locally (Without Docker)

If you are developing the Python backend and have Ollama running separately:

```bash
# Ensure Ollama is running locally on port 11434
poetry run civic_query_service --port 8001
```

### Frontend Development

The frontend logic is located in `static/index.html`. You can edit this file directly. Hard refreshes in the browser will reflect changes immediately.

## Contributing

Contributions are welcome, especially for adding support for additional G7 languages (French, Italian, Japanese). Please fork the repository and create a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
