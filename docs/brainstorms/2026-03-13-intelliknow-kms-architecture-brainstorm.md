---
date: 2026-03-13
topic: intelliknow-kms-architecture
status: draft
---

# IntelliKnow KMS - Architecture Brainstorm

## Development Environment (China)

Given the project is developed in China, configure the following for faster downloads:

### Package Managers
```bash
# pip - Tsinghua mirror
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# npm - TaoBao mirror
npm config set registry https://registry.npmmirror.com

# Docker - Alibaba mirror (in daemon.json)
{
  "registry-mirrors": ["https://docker.mirrors.ustc.edu.cn"]
}
```

### Model Downloads
- **Ollama**: Models will be pulled through configured proxy if needed
- **Hugging Face**: Use mirror endpoint or pre-download models
  ```bash
  export HF_ENDPOINT=https://hf-mirror.com
  ```

## Project Constraints

**Timeline**: 7 calendar days (1 week) from kickoff  
**Team**: Solo developer (no external collaboration)  
**Scope**: MVP-focused - prioritize core functions; no over-engineering  
**AI Usage**: Leverage AI for document parsing, query classification, and response generation

## What We're Building

**IntelliKnow KMS** is a Gen AI-powered Knowledge Management System that enables enterprises to:

1. **Ingest documents** (PDF, DOCX) and automatically build a searchable knowledge base using AI-powered parsing and embeddings
2. **Query via multiple frontends** (Telegram, Microsoft Teams) with natural language questions
3. **Classify intents** into predefined spaces (HR, Legal, Finance) with option to add custom spaces (e.g., Operations, IT) for context-aware responses
4. **Monitor and analyze** usage through an admin dashboard with analytics on document access, query patterns, and classification accuracy

The system addresses the core enterprise pain point of fragmented information by creating a unified, AI-accessible knowledge layer that employees can query from their preferred communication tools.

## Why This Approach

### Architecture Decisions

We evaluated three approaches for the backend architecture:

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **Monolithic FastAPI** (Chosen) | Simple deployment, faster development, easier debugging | Less scalable for massive scale | ✅ Best for 7-day MVP |
| Microservices | Better scalability, independent deployment | Adds complexity, network overhead | ❌ Overkill for MVP |
| Hybrid (API + Workers) | Good balance of simplicity and performance | More moving parts | ❌ Unnecessary for initial scope |

**Rationale**: Given the 7-day timeline and solo development constraint, a monolithic FastAPI application provides the fastest path to a working MVP while maintaining code organization and testability.

### Frontend Approach

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **Streamlit** (Chosen) | Rapid prototyping, minimal code, built-in widgets | Limited customization | ✅ Fastest for admin tools |
| Jinja2 Templates | No build process, server-side rendering | Less interactive | ❌ Slower to build rich UIs |
| React + FastAPI | Best UX, full customization | Build complexity, separate deployment | ❌ Overkill for MVP |

**Rationale**: Streamlit enables rapid dashboard development with minimal code, perfect for internal admin tools where functionality matters more than pixel-perfect design.

### AI/LLM Strategy

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **Local Models (Ollama)** (Chosen) | No API costs, works offline, data privacy | Requires setup, slower on CPU | ✅ Best for enterprise data |
| OpenAI API | Most reliable, fast, well-documented | Usage costs, data leaves premises | ❌ Cost and privacy concerns |
| Hybrid | Maximum flexibility | Configuration complexity | ❌ Unnecessary for MVP |

**Rationale**: Using local models via Ollama ensures enterprise data never leaves the premises, eliminates ongoing API costs, and works offline. Models like Llama 3 or Mistral are sufficient for intent classification and response generation.

### Vector Database

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **FAISS + SQLite** (Chosen) | Fast, lightweight, proven | Manual persistence needed | ✅ Perfect for MVP scale |
| ChromaDB | Built-in persistence, easier setup | Less performant at scale | ❌ FAISS is more flexible |
| PostgreSQL + pgvector | Full SQL capabilities | More complex setup | ❌ Overkill for initial scope |

**Rationale**: FAISS provides excellent performance for vector similarity search, while SQLite handles metadata and relational data. This combination is battle-tested and lightweight.

### Bot Integration Priority

**Chosen**: Telegram + Microsoft Teams

**Rationale**: 
- Telegram has the easiest bot API with webhook support
- Microsoft Teams is the enterprise standard
- Both have excellent Python SDKs
- 2 platforms meets the requirement while staying within timeline

## Key Decisions

### 1. **Document Processing Pipeline**
```
Upload → Parse → Chunk → Embed → Store → Index by Intent Space
```

- **PDF/DOCX Parsing**: Use `python-docx` for DOCX and `PyPDF2`/`pdfplumber` for PDFs
- **Chunking Strategy**: 1000 tokens with 200 token overlap for semantic coherence
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions, fast, confirmed choice)
- **Local LLM**: Qwen3.5-9B (optimized for Chinese/English, efficient on consumer hardware)
- **Storage**: Separate FAISS indexes per intent space (HR, Legal, Finance) for better retrieval accuracy
- **China Development Note**: Configure package managers (pip, npm) and model downloads to use Chinese mirrors (Tsinghua, Alibaba) to speed up downloads

### 2. **Intent Classification Strategy**

**Hybrid Approach**:
- **Rule-based** (80% of queries): Keyword matching for common patterns ("HR policy", "legal contract", "expense report")
- **LLM fallback** (20% of queries): Use local model for edge cases and ambiguous queries
- **Confidence threshold**: 70% minimum for direct classification, fall back to "General" space below threshold

### 3. **Multi-Frontend Architecture**

**Central Orchestrator Pattern**:
```
User Query → Bot Adapter → QueryOrchestrator → Intent Classifier → Knowledge Base → Response
```

- **Single business logic layer** (`QueryOrchestrator`) handles all queries
- **Separate adapters** for Telegram and Teams (translate platform-specific formats)
- **Webhooks** for production (not polling) - better performance and resource usage

### 4. **FastAPI Project Structure**

```
intelliknow-kms/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── api/v1/              # API endpoints
│   ├── bots/                # Telegram & Teams adapters
│   ├── core/                # Business logic
│   │   ├── knowledge_base.py
│   │   ├── intent_classifier.py
│   │   └── document_processor.py
│   ├── models/              # Pydantic models
│   └── db/                  # SQLite & FAISS management
├── admin-dashboard/         # Streamlit app
│   ├── app.py              # Main dashboard
│   └── pages/              # Document mgmt, Analytics, Settings
└── tests/
```

### 5. **Streamlit Dashboard Pages**

1. **Dashboard** (Home): Metrics, recent activity, system status
2. **Documents**: Upload, view, delete documents; search and filter
3. **Intent Spaces**: Create/edit/delete intent spaces; view classification logs
4. **Integrations**: Configure Telegram/Teams bots; test connections
5. **Analytics**: Query history, most accessed documents, classification accuracy

## Open Questions

### Technical Questions

1. **Document Update Strategy**
   - When a document is updated, should we:
     - A) Delete all chunks and re-index (simpler)
     - B) Track chunk versions and update only changed chunks (complex but efficient)
   - Decision needed: Start with A for MVP, consider B if update frequency is high

2. **Response Caching**
   - Should we cache LLM responses for identical queries?
   - Trade-off: Faster responses vs. potentially stale information
   - Decision needed: Implement with TTL (e.g., 1 hour) for common queries

3. **Authentication & Authorization**
   - Should the admin dashboard have user authentication?
   - If yes: Simple API key or full JWT-based auth?
   - Decision needed: API key for MVP, JWT if multi-user requirement emerges

### Resolved Questions

- ✅ **Embedding Model**: `all-MiniLM-L6-v2` (chosen for speed, 384 dimensions)
- ✅ **Local LLM**: Qwen3.5-9B (chosen for Chinese/English optimization)
- ✅ **Development Environment**: China mirror configuration documented

### Product Questions

5. **Intent Space Management**
   - Should users be able to create custom intent spaces beyond HR/Legal/Finance?
   - If yes: How to handle documents that span multiple spaces?
   - Decision needed: Allow custom spaces with multi-label support

6. **Response Formatting**
   - Should responses include citations (source document references)?
   - Format: Simple text, Markdown, or structured JSON?
   - Decision needed: Include citations in Markdown format

7. **Analytics Depth**
   - What metrics are most important?
     - Query volume, response time, classification accuracy
     - Document popularity, user satisfaction
   - Decision needed: Focus on query volume, response time, and classification accuracy for MVP

## Tech Stack Summary

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Backend** | FastAPI (Python) | Modern, fast, async support, great docs |
| **Admin UI** | Streamlit | Rapid prototyping, minimal code |
| **Vector DB** | FAISS | High performance, battle-tested |
| **Relational DB** | SQLite | Zero-config, portable, sufficient for MVP |
| **LLM** | Qwen3.5-9B via Ollama | Optimized for Chinese/English, efficient on consumer hardware |
| **Embeddings** | all-MiniLM-L6-v2 | 384 dims, fast, sufficient quality for MVP |
| **Document Parsing** | python-docx, PyPDF2 | Standard libraries, well-maintained |
| **Bot Integration** | python-telegram-bot, botbuilder | Official SDKs, well-documented |
| **Deployment** | Docker + docker-compose | Portable, reproducible |

## Success Criteria

The system is considered successful when:

1. ✅ Documents can be uploaded (PDF, DOCX) and automatically indexed
2. ✅ Queries via Telegram and Teams receive accurate, context-aware responses
3. ✅ Intent classification achieves ≥70% accuracy on test queries
4. ✅ Admin dashboard shows real-time analytics (query volume, classification accuracy)
5. ✅ Average response time < 3 seconds for typical queries
6. ✅ System can be deployed locally with `docker-compose up`

## Next Steps

→ Run `/ce:plan` to create the implementation plan
→ Review this document for any final adjustments
→ Begin implementation following the plan

## References

- **FAISS Documentation**: https://faiss.ai/
- **python-telegram-bot**: https://github.com/python-telegram-bot/python-telegram-bot (28.9k stars)
- **Microsoft Bot Framework**: https://github.com/microsoft/BotBuilder-Samples
- **LangChain Patterns**: https://github.com/langchain-ai/langchain
- **FastAPI Best Practices**: https://fastapi.tiangolo.com/tutorial/bigger-applications/
