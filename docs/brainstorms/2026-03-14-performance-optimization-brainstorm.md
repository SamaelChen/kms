---
date: 2026-03-14
topic: performance-optimization
---

# Performance Optimization

## What We're Building

Comprehensive performance improvements across the entire system to eliminate timeouts, reduce latency, and improve throughput.

**Optimizations:**
1. **Model Pre-downloading** - Download embedding model and LLM on startup
2. **HTTP Connection Pooling** - Reuse connections to Ollama
3. **Caching Layer** - Cache embeddings and query results
4. **Async Document Processing** - Background workers for uploads
5. **FAISS Index Optimization** - Tune index parameters

## Why This Approach

**Chosen: Multi-layer optimization**

Each optimization targets a different bottleneck:
- Model downloads → Eliminate cold-start timeouts
- Connection pooling → Reduce HTTP overhead
- Caching → Avoid redundant computation
- Async processing → Better UX for uploads
- FAISS tuning → Faster search

**Order of implementation:**
1. Model pre-downloading (biggest impact, easiest)
2. Connection pooling (medium impact, easy)
3. Caching (high impact, medium effort)
4. Async processing (medium impact, higher effort)
5. FAISS tuning (low-medium impact, easy)

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **Embedding model** | Download on startup in `__init__.py` or first API call |
| **LLM model** | Pull via Ollama API on startup with retry logic |
| **HTTP pooling** | Use `httpx.AsyncClient` with connection limits |
| **Caching** | In-memory LRU cache for embeddings; Redis optional for production |
| **Async processing** | Celery with Redis broker; SQLite backend for MVP |
| **FAISS tuning** | Keep IndexFlatL2 for <100k docs; add IVF/HNSW for scale |

## Technical Approach

### 1. Model Pre-downloading

**Embedding Model:**
```python
# app/core/embedding.py
class EmbeddingGenerator:
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self._model = None
        self._download_on_init()
    
    def _download_on_init(self):
        """Pre-download model files"""
        from sentence_transformers import SentenceTransformer
        SentenceTransformer(self.model_name)
```

**LLM Model:**
```python
# app/core/startup.py
async def download_llm_model():
    """Pull LLM model on startup"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.OLLAMA_BASE_URL}/api/pull",
            json={"name": settings.LLM_MODEL},
            timeout=300
        )
```

### 2. HTTP Connection Pooling

**Response Generator:**
```python
# Use shared client
class ResponseGenerator:
    def __init__(self):
        self.client = httpx.AsyncClient(
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            timeout=httpx.Timeout(30.0)
        )
    
    async def close(self):
        await self.client.aclose()
```

### 3. Caching Layer

**Embedding Cache:**
```python
# app/core/embedding.py
from functools import lru_cache
import hashlib

class EmbeddingGenerator:
    def __init__(self):
        self.cache = {}  # Simple dict; use Redis for production
        self.cache_size = 1000
    
    def _get_cache_key(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()
    
    def generate_single(self, text: str) -> np.ndarray:
        key = self._get_cache_key(text)
        if key in self.cache:
            return self.cache[key]
        
        embedding = self._compute_embedding(text)
        if len(self.cache) < self.cache_size:
            self.cache[key] = embedding
        return embedding
```

**Query Result Cache:**
```python
# Cache recent queries for 5 minutes
class QueryCache:
    def __init__(self, ttl=300):
        self.cache = {}
        self.ttl = ttl
    
    def get(self, query: str, intent_space: str):
        key = f"{intent_space}:{query}"
        if key in self.cache:
            result, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return result
        return None
```

### 4. Async Document Processing

**Celery Setup:**
```python
# app/worker.py
from celery import Celery

celery_app = Celery(
    "document_processor",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task
def process_document_task(document_id: str, file_path: str, intent_space: str):
    # Run async
    asyncio.run(document_processor.process(document_id, file_path, intent_space))
```

**API Change:**
```python
# Instead of asyncio.create_task
celery_app.send_task(
    "process_document_task",
    args=[doc_id, file_path, intent_space]
)
```

### 5. FAISS Index Optimization

**Current:** IndexFlatL2 (exact search)
**Optimized:** IndexIVFFlat for >10k docs

```python
# app/db/faiss_manager.py
def _create_index(self, n_vectors: int = 0) -> faiss.Index:
    if n_vectors < 10000:
        # Exact search for small datasets
        return faiss.IndexFlatL2(self.dimension)
    else:
        # Approximate search for large datasets
        nlist = min(int(n_vectors / 100), 100)  # Number of clusters
        quantizer = faiss.IndexFlatL2(self.dimension)
        return faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
```

## Open Questions

1. **Cache invalidation:** When to clear embedding cache? Document updates?
2. **Redis dependency:** Add Redis container or keep in-memory for MVP?
3. **Celery vs RQ:** Celery is robust but complex; RQ simpler but fewer features?
4. **Model download timeout:** 5 minutes sufficient for embedding model?
5. **Cache size:** 1000 embeddings ~ 1.5MB; reasonable for single instance?

## Dependencies to Add

```txt
# Optional - for production caching
redis==5.0.1

# For async processing
celery==5.3.4
# OR
rq==1.15.1
```

## Success Criteria

- [ ] Embedding model pre-downloaded on startup
- [ ] LLM model pulled on startup
- [ ] HTTP connections pooled (measure with logging)
- [ ] Query response time < 2 seconds (currently ~5-30s)
- [ ] Document upload returns immediately (async processing)
- [ ] FAISS search < 100ms for 10k docs
- [ ] Cache hit rate > 30% for repeated queries
- [ ] No first-query timeouts

## Implementation Order

1. **Phase 1:** Model pre-downloading (biggest user impact)
2. **Phase 2:** HTTP connection pooling (easy win)
3. **Phase 3:** Embedding caching (reduces compute)
4. **Phase 4:** Async document processing (better UX)
5. **Phase 5:** Query caching and FAISS tuning (incremental gains)

## Next Steps

→ `/ce:plan` for implementation details
