# Implementation Plan: Performance Optimization

**Source:** [Brainstorm Document](docs/brainstorms/2026-03-14-performance-optimization-brainstorm.md)  
**Date:** 2026-03-14  
**Estimated Effort:** 2-3 days

---

## Phase 1: Model Pre-downloading (Day 1)

### 1.1 Embedding Model Pre-download
**File to modify:**
- `app/core/embedding.py`

**Changes:**
```python
class EmbeddingGenerator:
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self._model = None
        self._ensure_model_downloaded()
    
    def _ensure_model_downloaded(self):
        """Download model on initialization to avoid first-query timeout"""
        try:
            print(f"Downloading embedding model: {self.model_name}")
            start_time = time.time()
            _ = self.model  # This triggers download
            elapsed = time.time() - start_time
            print(f"Embedding model ready in {elapsed:.1f}s")
        except Exception as e:
            print(f"Warning: Could not download embedding model: {e}")
```

### 1.2 LLM Model Pre-download
**File to create:**
- `app/core/startup.py`

**Implementation:**
```python
import httpx
import asyncio
from app.config import settings

async def download_llm_model(max_retries: int = 3):
    """Pull LLM model on startup"""
    url = f"{settings.OLLAMA_BASE_URL}/api/pull"
    model = settings.LLM_MODEL
    
    for attempt in range(max_retries):
        try:
            print(f"Pulling LLM model: {model} (attempt {attempt + 1})")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={"name": model, "stream": False},
                    timeout=300.0
                )
                
                if response.status_code == 200:
                    print(f"LLM model '{model}' ready")
                    return True
                else:
                    print(f"Failed to pull model: {response.status_code}")
                    
        except Exception as e:
            print(f"Error pulling model: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(5)
    
    print(f"Warning: Could not pull LLM model after {max_retries} attempts")
    return False
```

### 1.3 Integrate into App Startup
**File to modify:**
- `app/main.py`

**Add to startup event:**
```python
@app.on_event("startup")
async def startup_event():
    # Initialize database
    await init_db()
    
    # Download models in background
    asyncio.create_task(download_llm_model())
    
    print("IntelliKnow KMS started successfully")
```

---

## Phase 2: HTTP Connection Pooling (Day 1)

### 2.1 Response Generator with Connection Pool
**File to modify:**
- `app/core/response_generator.py`

**Changes:**
```python
import httpx
from typing import Optional

class ResponseGenerator:
    def __init__(self):
        self.ollama_url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        self.model = settings.LLM_MODEL
        # Create persistent client with connection pooling
        self.client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with connection pooling"""
        if self.client is None or self.client.is_closed:
            self.client = httpx.AsyncClient(
                limits=httpx.Limits(
                    max_connections=20,
                    max_keepalive_connections=10
                ),
                timeout=httpx.Timeout(60.0, connect=10.0)
            )
        return self.client
    
    async def generate(self, query: str, context_chunks: List[Tuple[dict, float]], 
                       intent_space: str) -> str:
        # ... existing code ...
        client = await self._get_client()
        response = await client.post(self.ollama_url, json={...})
        # ...
    
    async def close(self):
        """Close HTTP client"""
        if self.client and not self.client.is_closed:
            await self.client.aclose()
```

### 2.2 Intent Classifier with Connection Pool
**File to modify:**
- `app/core/intent_classifier.py`

**Similar changes** - use shared client

### 2.3 Lifecycle Management
**File to modify:**
- `app/main.py`

**Add shutdown event:**
```python
@app.on_event("shutdown")
async def shutdown_event():
    await response_generator.close()
    # Close other clients
```

---

## Phase 3: Caching Layer (Day 1-2)

### 3.1 Embedding Cache
**File to modify:**
- `app/core/embedding.py`

**Implementation:**
```python
import hashlib
import time
from typing import Dict, Tuple

class EmbeddingCache:
    """LRU cache for embeddings"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[str, Tuple[np.ndarray, float]] = {}
        self.access_order: list = []
    
    def _get_key(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()
    
    def get(self, text: str) -> Optional[np.ndarray]:
        key = self._get_key(text)
        if key in self.cache:
            embedding, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                # Update access order
                self.access_order.remove(key)
                self.access_order.append(key)
                return embedding
            else:
                del self.cache[key]
                self.access_order.remove(key)
        return None
    
    def set(self, text: str, embedding: np.ndarray):
        key = self._get_key(text)
        
        # Evict oldest if at capacity
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
        
        self.cache[key] = (embedding, time.time())
        if key not in self.access_order:
            self.access_order.append(key)


class EmbeddingGenerator:
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self._model = None
        self.cache = EmbeddingCache(max_size=1000)
        self._ensure_model_downloaded()
    
    def generate_single(self, text: str) -> np.ndarray:
        # Check cache first
        cached = self.cache.get(text)
        if cached is not None:
            return cached
        
        # Generate and cache
        embedding = self._compute_embedding(text)
        self.cache.set(text, embedding)
        return embedding
```

### 3.2 Query Result Cache
**File to create:**
- `app/core/cache.py`

**Implementation:**
```python
import time
from typing import Optional, Dict, Any

class QueryCache:
    """Cache for query results"""
    
    def __init__(self, ttl: int = 300):  # 5 minutes
        self.ttl = ttl
        self.cache: Dict[str, Tuple[Any, float]] = {}
    
    def _get_key(self, query: str, intent_space: str) -> str:
        return f"{intent_space}:{hash(query) % 1000000}"
    
    def get(self, query: str, intent_space: str) -> Optional[Any]:
        key = self._get_key(query, intent_space)
        if key in self.cache:
            result, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return result
            del self.cache[key]
        return None
    
    def set(self, query: str, intent_space: str, result: Any):
        key = self._get_key(query, intent_space)
        self.cache[key] = (result, time.time())
    
    def clear(self):
        self.cache.clear()


# Global cache instance
query_cache = QueryCache()
```

### 3.3 Integrate Query Cache
**File to modify:**
- `app/core/query_orchestrator.py`

**Changes:**
```python
from app.core.cache import query_cache

class QueryOrchestrator:
    async def process(self, request: QueryRequest) -> QueryResponse:
        start_time = time.time()
        
        # Check cache first
        cached = query_cache.get(request.query, "General")
        if cached:
            return QueryResponse(
                query=request.query,
                response=cached["response"],
                intent_classified=cached["intent"],
                confidence_score=cached["confidence"],
                citations=cached["citations"],
                response_time_ms=(time.time() - start_time) * 1000
            )
        
        # Process normally...
        response = await self._process_uncached(request)
        
        # Cache result
        query_cache.set(request.query, response.intent_classified, {
            "response": response.response,
            "intent": response.intent_classified,
            "confidence": response.confidence_score,
            "citations": response.citations
        })
        
        return response
```

---

## Phase 4: Async Document Processing (Day 2)

### 4.1 Celery Configuration
**File to create:**
- `app/worker.py`

**Implementation:**
```python
from celery import Celery
import asyncio
from app.config import settings
from app.core.document_processor import document_processor

celery_app = Celery(
    "intellikow_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.worker"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max
    worker_prefetch_multiplier=1,
)

@celery_app.task(bind=True, max_retries=3)
def process_document_task(self, document_id: str, file_path: str, intent_space: str):
    """Process document in background"""
    try:
        result = asyncio.run(
            document_processor.process(document_id, file_path, intent_space)
        )
        return result
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

### 4.2 Update API to Use Celery
**File to modify:**
- `app/api/v1/endpoints/documents.py`

**Changes:**
```python
from app.worker import process_document_task

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(...):
    # ... existing code ...
    
    # Queue for processing instead of asyncio.create_task
    process_document_task.delay(doc_id, file_path, intent_space)
    
    return DocumentUploadResponse(
        document_id=doc_id,
        filename=file.filename,
        status="queued",  # Changed from "pending"
        message="Document uploaded and queued for processing."
    )
```

### 4.3 Task Status Endpoint
**File to modify:**
- `app/api/v1/endpoints/documents.py`

**Add:**
```python
from celery.result import AsyncResult

@router.get("/{document_id}/task-status")
async def get_task_status(document_id: str):
    """Get document processing task status"""
    # Query Celery for task status
    # Return: queued, processing, completed, error
    pass
```

---

## Phase 5: FAISS Index Optimization (Day 2)

### 5.1 Dynamic Index Selection
**File to modify:**
- `app/db/faiss_manager.py`

**Changes:**
```python
def _create_index(self, n_vectors: int = 0) -> faiss.Index:
    """Create appropriate index based on dataset size"""
    if n_vectors < 1000:
        # Small dataset: exact search
        return faiss.IndexFlatL2(self.dimension)
    elif n_vectors < 10000:
        # Medium dataset: IVF with few clusters
        nlist = max(4, int(n_vectors / 100))
        quantizer = faiss.IndexFlatL2(self.dimension)
        index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
        return index
    else:
        # Large dataset: IVF with many clusters
        nlist = min(100, int(n_vectors / 100))
        quantizer = faiss.IndexFlatL2(self.dimension)
        index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
        return index

def add_chunks(self, intent_space: str, embeddings: np.ndarray, 
               chunks_metadata: List[dict]) -> bool:
    # ...
    # Rebuild index if size changed significantly
    n_vectors = len(self.metadata[intent_space]) + len(chunks_metadata)
    if self.indexes[intent_space].ntotal == 0:
        self.indexes[intent_space] = self._create_index(n_vectors)
    # ...
```

---

## Docker Compose Updates

### 6.1 Add Redis Service
**File to modify:**
- `docker-compose.yml`

**Add:**
```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
  command: redis-server --appendonly yes

worker:
  build: .
  command: celery -A app.worker worker --loglevel=info
  volumes:
    - ./data:/app/data
  environment:
    - REDIS_URL=redis://redis:6379/0
  depends_on:
    - redis
    - api

volumes:
  # ... existing volumes ...
  redis_data:
```

---

## Files Summary

### New Files (3):
1. `app/core/startup.py` - Model downloading
2. `app/core/cache.py` - Caching utilities
3. `app/worker.py` - Celery worker configuration

### Modified Files (7):
1. `app/core/embedding.py` - Add caching, pre-download
2. `app/core/response_generator.py` - Connection pooling
3. `app/core/intent_classifier.py` - Connection pooling
4. `app/core/query_orchestrator.py` - Query caching
5. `app/db/faiss_manager.py` - Index optimization
6. `app/api/v1/endpoints/documents.py` - Async processing
7. `app/main.py` - Startup/shutdown events
8. `docker-compose.yml` - Add Redis and worker services

---

## Configuration Updates

**`.env` additions:**
```bash
REDIS_URL=redis://localhost:6379/0
EMBEDDING_CACHE_SIZE=1000
QUERY_CACHE_TTL=300
```

**`app/config.py` additions:**
```python
REDIS_URL: str = "redis://localhost:6379/0"
EMBEDDING_CACHE_SIZE: int = 1000
QUERY_CACHE_TTL: int = 300  # seconds
```

---

## Success Criteria Checklist

- [ ] Embedding model downloaded on startup (< 2 min)
- [ ] LLM model pulled on startup (or gracefully skipped)
- [ ] HTTP clients use connection pooling
- [ ] Embedding cache working (check hit rate)
- [ ] Query cache working (5 min TTL)
- [ ] Document processing async (returns immediately)
- [ ] Celery worker processes documents
- [ ] FAISS uses IVF index for >1k docs
- [ ] Query response < 2 seconds (cached)
- [ ] Query response < 5 seconds (uncached)
- [ ] No timeouts on first query

---

## Testing

**Test 1: Cold Start**
```bash
# Fresh startup
docker compose up -d
# Check logs for model downloads
docker compose logs -f api
# First query should not timeout
curl -X POST http://localhost:8000/api/v1/queries/ask \
  -d '{"query": "test"}'
```

**Test 2: Cache Hit**
```bash
# Same query twice
time curl ...  # First: ~5s
time curl ...  # Second: ~0.1s (cached)
```

**Test 3: Async Upload**
```bash
# Upload should return immediately
time curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@large.pdf"
# Should return in < 1s, status: "queued"
```

---

## Commands

```bash
# Start with new services
docker compose up -d --build

# Monitor worker
docker compose logs -f worker

# Check Redis
docker exec kms-redis-1 redis-cli info

# Purge Celery queue
docker exec kms-api-1 celery -A app.worker purge
```
