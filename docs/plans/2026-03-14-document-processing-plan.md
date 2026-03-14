# Implementation Plan: Document Processing

**Source:** [Brainstorm Document](docs/brainstorms/2026-03-14-document-processing-brainstorm.md)  
**Date:** 2026-03-14  
**Estimated Effort:** 3-4 days

---

## Phase 1: Foundation (Day 1)

### 1.1 Add Dependencies
**Files to modify:**
- `requirements.txt`

**Add:**
```txt
PyPDF2>=3.0.0
python-docx>=0.8.11
openpyxl>=3.1.0
python-pptx>=0.6.21
```

### 1.2 Database Schema Update
**Files to modify:**
- `app/db/models.py` - Add DocumentChunk model
- `app/db/database.py` - Add chunk-related operations

**New Model:**
```python
class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    intent_space = Column(String, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(BLOB, nullable=True)  # JSON-serialized vector
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 1.3 Document Parser Module
**Files to create:**
- `app/core/document_parser.py`

**Responsibilities:**
- Detect file type by extension
- Parse content:
  - `.txt`, `.md` → Native Python
  - `.pdf` → PyPDF2/pdfplumber
  - `.docx` → python-docx
  - `.xlsx` → openpyxl
  - `.pptx` → python-pptx
- Return plain text content
- Handle errors gracefully

---

## Phase 2: Chunking & Embedding (Day 2)

### 2.1 Semantic Chunker
**Files to create:**
- `app/core/chunker.py`

**Algorithm:**
```python
def chunk_document(text: str, max_tokens: int = 500) -> List[str]:
    """Split text into semantic chunks."""
    # Split into paragraphs
    paragraphs = text.split('\n\n')
    
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for para in paragraphs:
        para_tokens = estimate_tokens(para)
        
        if para_tokens > max_tokens:
            # Split long paragraph into sentences
            sentences = sent_tokenize(para)
            for sent in sentences:
                sent_tokens = estimate_tokens(sent)
                if current_tokens + sent_tokens > max_tokens:
                    if current_chunk:
                        chunks.append(' '.join(current_chunk))
                    current_chunk = [sent]
                    current_tokens = sent_tokens
                else:
                    current_chunk.append(sent)
                    current_tokens += sent_tokens
        else:
            if current_tokens + para_tokens > max_tokens:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [para]
                current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks
```

### 2.2 Embedding Service
**Files to modify:**
- `app/core/knowledge_base.py`

**Add methods:**
```python
async def generate_embeddings(self, texts: List[str]) -> np.ndarray:
    """Generate embeddings for text chunks."""
    return self.embedding_model.encode(texts, show_progress_bar=False)

async def add_document_chunks(
    self, 
    document_id: str, 
    intent_space: str, 
    chunks: List[str]
) -> None:
    """Add chunks to FAISS index and database."""
    embeddings = await self.generate_embeddings(chunks)
    # Store in FAISS
    # Store in SQLite
```

---

## Phase 3: Processing Pipeline (Day 2-3)

### 3.1 Document Processor Service
**Files to create:**
- `app/core/document_processor.py`

**Workflow:**
```python
async def process_document(document_id: str, intent_space: str):
    # 1. Load document
    # 2. Parse content
    # 3. Generate chunks
    # 4. Generate embeddings
    # 5. Store chunks
    # 6. Update document status
```

### 3.2 Update Document Upload API
**Files to modify:**
- `app/api/v1/endpoints/documents.py`

**Changes:**
- After saving file, trigger processing
- Update Document model with processing status
- Add error handling

### 3.3 Add Status Tracking
**Files to modify:**
- `app/models/document.py` - Add status field (pending/processing/completed/error)
- `app/db/models.py` - Add processing_status, error_message columns

---

## Phase 4: Dashboard Updates (Day 3)

### 4.1 Upload Form Enhancement
**Files to modify:**
- `admin-dashboard/pages/2_Documents.py`

**Add:**
- Intent space dropdown (required)
- File type validation
- Processing status indicator

### 4.2 Document List Status
**Files to modify:**
- `admin-dashboard/pages/2_Documents.py`

**Add columns:**
- Processing Status (🟡 Pending / 🔵 Processing / 🟢 Completed / 🔴 Error)
- Chunks count
- Error message (if any)

### 4.3 Document Detail View
**Files to modify:**
- `admin-dashboard/pages/2_Documents.py`

**Add:**
- Show extracted chunks
- Preview first 3 chunks
- Retry processing button (for errors)

---

## Phase 5: Integration & Testing (Day 4)

### 5.1 Wire Everything Together
**Files to modify:**
- `app/main.py` - Ensure all modules initialized
- `app/core/__init__.py` - Export new modules

### 5.2 Add Tests
**Files to create:**
- `tests/test_document_parser.py`
- `tests/test_chunker.py`
- `tests/test_document_processing.py`

### 5.3 Error Handling
- Handle corrupted PDFs
- Handle password-protected documents
- Handle unsupported file types
- Retry logic for transient failures

---

## Files Summary

### New Files (7):
1. `app/core/document_parser.py` - Document parsing logic
2. `app/core/chunker.py` - Semantic chunking
3. `app/core/document_processor.py` - Processing orchestration
4. `tests/test_document_parser.py` - Parser tests
5. `tests/test_chunker.py` - Chunker tests
6. `tests/test_document_processing.py` - Integration tests
7. `docs/plans/2026-03-14-document-processing-plan.md` - This plan

### Modified Files (6):
1. `requirements.txt` - Add parsing dependencies
2. `app/db/models.py` - Add DocumentChunk model
3. `app/db/database.py` - Add chunk CRUD operations
4. `app/core/knowledge_base.py` - Add embedding generation
5. `app/api/v1/endpoints/documents.py` - Trigger processing
6. `admin-dashboard/pages/2_Documents.py` - UI updates

---

## Configuration

### Chunking Parameters
- **Max tokens per chunk:** 500
- **Overlap:** 0% (for MVP, add later if needed)
- **Tokenizer:** Approximate with word count / 0.75

### Processing
- **Mode:** Synchronous (process on upload)
- **Timeout:** 30 seconds per document
- **Retry:** 1 automatic retry on failure

---

## Success Criteria Checklist

- [ ] Can upload .txt, .pdf, .docx files
- [ ] Documents processed automatically after upload
- [ ] Processing status visible (pending/processing/completed/error)
- [ ] Chunks stored in FAISS with correct intent space
- [ ] Chunk metadata in SQLite
- [ ] Error handling for corrupted files
- [ ] Dashboard shows status and chunk count
- [ ] Unit tests passing (>80% coverage)
- [ ] Integration tests passing

---

## Open Decisions

1. **Chunk size:** Start with 500 tokens, adjust based on testing
2. **Overlap:** 0% for MVP, add 10-20% if retrieval quality poor
3. **PDF library:** Start with PyPDF2, upgrade to pdfplumber if extraction quality issues
4. **Error retry:** 1 automatic retry, then manual retry via dashboard

---

## Next Steps After Completion

1. Implement query responses (retrieve relevant chunks, generate LLM response)
2. Add direct chat interface
3. Performance optimization (async processing, caching)
4. Add chunk overlap for better context preservation

---

## Commands to Run

```bash
# After Phase 1
pip install -r requirements.txt

# After Phase 5
pytest tests/test_document_*.py -v

# Full test suite
pytest tests/ -v --tb=short
```
