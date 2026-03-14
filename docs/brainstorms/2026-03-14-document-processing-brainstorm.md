---
date: 2026-03-14
topic: document-processing
---

# Document Processing Implementation

## What We're Building

A complete document processing pipeline that transforms uploaded files into searchable knowledge chunks. When users upload documents through the admin dashboard, the system will:

1. Parse the document content (text, PDF, Office files)
2. Split content into semantic chunks (respecting paragraph/sentence boundaries)
3. Generate embeddings using sentence-transformers (all-MiniLM-L6-v2)
4. Store chunks in FAISS vector index (per intent space)
5. Save metadata in SQLite for retrieval

This enables the query system to find relevant document chunks when users ask questions.

## Why This Approach

**Chosen: Approach B (Full Implementation)**

Selected because:
- Supports real-world document types users actually have
- Semantic chunking preserves context better than fixed-size
- Synchronous processing is simpler and sufficient for MVP
- Sticking with current stack (FAISS + SQLite) avoids migration complexity

**Rejected:**
- Approach A (MVP text-only): Would require users to manually convert documents
- Approach C (Async): YAGNI - can add later if volume demands it

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **Document types** | Text, PDF, Office (.docx, .xlsx, .pptx) - covers 90% of use cases |
| **Chunking strategy** | Semantic chunks using paragraph/sentence boundaries - better context preservation |
| **Processing mode** | Synchronous on upload - simpler implementation, sufficient for initial load |
| **Storage** | Keep current FAISS + SQLite stack - no migration needed, proven working |
| **Intent assignment** | Manual on upload - explicit and avoids classification complexity |
| **Embedding model** | all-MiniLM-L6-v2 - already configured, 384-dim, fast inference |

## Technical Approach

### Parsing Libraries
- **PDF**: PyPDF2 or pdfplumber (text extraction)
- **Office**: python-docx (Word), openpyxl (Excel), python-pptx (PowerPoint)
- **Text**: Native Python (no extra deps)

### Chunking Logic
```
1. Parse document to raw text
2. Split into paragraphs (\n\n)
3. If paragraph > max_chunk_size (e.g., 500 tokens):
   - Split into sentences
   - Group sentences into chunks of ~500 tokens
4. Generate embedding for each chunk
5. Store: chunk_id, intent_space, document_id, content, embedding_vector
```

### Database Schema Addition
```sql
-- New table for document chunks
CREATE TABLE document_chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT REFERENCES documents(id),
    intent_space TEXT,
    chunk_index INTEGER,
    content TEXT,
    embedding BLOB, -- or separate FAISS index
    created_at TIMESTAMP
);

-- Index for intent space queries
CREATE INDEX idx_chunks_intent ON document_chunks(intent_space);
```

### API Changes
- `POST /api/v1/documents/upload` - Add processing step after upload
- `GET /api/v1/documents/{id}/status` - Return processing status (pending/processing/completed/error)
- `GET /api/v1/documents/{id}/chunks` - (optional) View extracted chunks

### Dashboard Changes
- Upload form: Add intent space dropdown (required)
- Document list: Show processing status indicator
- Document detail: Show extracted chunks count

## Open Questions

1. **Max chunk size?** 500 tokens? 1000? Test with actual content.
2. **Handle OCR for scanned PDFs?** Defer - add pytesseract later if needed.
3. **Chunk overlap?** 10-20% overlap to preserve context across boundaries?
4. **Error handling?** What if parsing fails? Mark document as failed, allow retry?
5. **Duplicate detection?** Should we prevent uploading the same file twice?

## Dependencies to Add

```txt
# requirements.txt additions
PyPDF2>=3.0.0
python-docx>=0.8.11
openpyxl>=3.1.0
python-pptx>=0.6.21

# Optional (for scanned PDFs - future)
# pytesseract>=0.3.10
# pdf2image>=1.16.0
```

## Success Criteria

- [ ] Can upload .txt, .pdf, .docx files
- [ ] Documents are automatically processed after upload
- [ ] Processing status visible in dashboard
- [ ] Chunks retrievable via query API (next feature)
- [ ] Error handling for corrupted/unsupported files
- [ ] ~1000 tokens/sec processing speed (reasonable for MVP)

## Next Steps

→ `/ce:plan` for implementation details
