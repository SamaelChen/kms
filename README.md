# IntelliKnow KMS

**Gen AI-powered Knowledge Management System**

A production-ready knowledge management system that enables enterprises to ingest documents (PDF, DOCX), classify queries by intent (HR, Legal, Finance), and respond via multi-frontend integrations (Telegram, Microsoft Teams).

## Features

- **Document Ingestion**: Upload and automatically index PDF and DOCX files
- **Intent Classification**: AI-powered classification into HR, Legal, Finance, or General categories
- **Semantic Search**: FAISS-based vector search for relevant document retrieval
- **Multi-Frontend Support**: Telegram and Microsoft Teams bot integrations
- **Admin Dashboard**: Streamlit-based interface for management and analytics
- **Local LLM**: Uses Ollama with Qwen3.5-9B for data privacy

## Architecture

```
┌─────────────┐  ┌─────────────┐
│   Telegram  │  │    Teams    │
└──────┬──────┘  └──────┬──────┘
       │                │
       └────────┬───────┘
                │
       ┌────────▼────────┐
       │   FastAPI       │
       │   (Backend)     │
       └────────┬────────┘
                │
       ┌────────▼────────┐
       │  Query          │
       │  Orchestrator   │
       └────────┬────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
┌───▼───┐  ┌────▼────┐ ┌───▼────┐
│Intent │  │Knowledge│ │Response│
│Classify│  │  Base   │ │Generate│
└───────┘  └────┬────┘ └────────┘
                │
       ┌────────▼────────┐
       │  FAISS + SQLite │
       └─────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose (optional)
- Ollama (for local LLM)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd intelliknow-kms
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start Ollama and pull the model:
```bash
ollama serve
ollama pull qwen3.5:9b
```

5. Run the application:
```bash
# Start API
uvicorn app.main:app --reload

# Start Dashboard (in another terminal)
streamlit run admin-dashboard/app.py
```

### Docker Deployment

#### Option 1: Docker Compose (Recommended - v2.x)

```bash
# Build and start all services
docker compose up -d --build

# Or without rebuilding (if images exist)
docker compose up -d
```

#### Option 2: Docker Compose (Legacy - v1.x)

```bash
# Build and start all services
docker-compose up -d --build

# Or without rebuilding
docker-compose up -d
```

#### Verify Services

```bash
# Check running containers
docker ps

# View logs
docker compose logs -f

# Test API health
curl http://localhost:8000/api/v1/health/
```

#### Access Points

| Service | URL | Notes |
|---------|-----|-------|
| API | http://localhost:8000 | FastAPI backend |
| Dashboard | http://localhost:8501 | Streamlit admin |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Ollama | http://localhost:11435 | LLM service (port 11435 to avoid conflicts) |

#### First-Time Setup

**Important**: The first query will timeout as sentence-transformers downloads the embedding model (~400MB). This is expected behavior.

```bash
# Pre-download embedding model (optional, prevents first-query timeout)
docker exec kms-api-1 python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Pull LLM model for queries
docker exec kms-ollama-1 ollama pull qwen3.5:9b
# Or for testing, use a smaller model:
docker exec kms-ollama-1 ollama pull qwen:0.5b
```

#### Stopping Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes (WARNING: deletes data)
docker compose down -v
```

## Usage

### Upload Documents

Via API:
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F "intent_space=HR"
```

Via Dashboard:
Navigate to http://localhost:8501 and use the Documents page.

### Query Knowledge Base

Via API:
```bash
curl -X POST "http://localhost:8000/api/v1/queries/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the leave policy?"}'
```

### Bot Integration

Configure bot tokens in `.env`:
```
TELEGRAM_BOT_TOKEN=your_token
TEAMS_APP_ID=your_app_id
TEAMS_APP_PASSWORD=your_password
```

## Development

### Project Structure

```
intelliknow-kms/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── bots/            # Bot integrations
│   ├── core/            # Business logic
│   ├── db/              # Database layer
│   └── models/          # Pydantic models
├── admin-dashboard/     # Streamlit app
├── data/               # Data storage
├── tests/              # Test suite
└── docs/               # Documentation
```

### Running Tests

```bash
pytest
```

## Tech Stack

- **Backend**: FastAPI (Python)
- **Admin UI**: Streamlit
- **Vector DB**: FAISS
- **Relational DB**: SQLite
- **LLM**: Ollama (Qwen3.5-9B)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)

## License

MIT License