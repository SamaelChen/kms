# Code Review Report - IntelliKnow KMS

**Date**: 2026-03-14
**Scope**: Core modules, API endpoints, database layer
**Status**: ✅ Review Complete - Issues Found

---

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| 🔴 Critical | 1 | Cache inconsistency bug |
| 🟡 Medium | 3 | Error handling improvements needed |
| 🟢 Low | 2 | Code quality improvements |

---

## 🔴 Critical Issues

### 1. Cache Key Bug in Query Orchestrator
**File**: `app/core/query_orchestrator.py` (Line 22)
**Issue**: Cache key does not include `intent_space`, causing incorrect cache hits

```python
# Current (BUGGY):
cached = query_cache.get(request.query, "General")  # Always uses "General"

# Should use actual intent_space from classification
```

**Impact**: Queries with different intent spaces may return cached results from wrong space
**Fix**: Move cache check after intent classification

---

## 🟡 Medium Issues

### 2. Async Task Error Handling
**File**: `app/api/v1/endpoints/documents.py` (Lines 44-47)
**Issue**: `asyncio.create_task` without error handling

```python
# Current:
asyncio.create_task(
    document_processor.process(doc_id, file_path, intent_space)
)
```

**Problem**: Exceptions in background task are silently lost
**Fix**: Add error handling callback or use proper task management

### 3. Generic Exception Handling
**File**: `app/api/v1/endpoints/documents.py` (Line 57)
**File**: `app/api/v1/endpoints/queries.py` (Line 17)
**Issue**: Catching generic `Exception` masks bugs

```python
# Current:
except Exception as e:
    raise HTTPException(500, f"Upload failed: {str(e)}")
```

**Fix**: Catch specific exceptions, log unexpected ones

### 4. Test Synchronization Issue
**File**: `tests/test_intent_classifier.py`
**Issue**: Tests call async methods synchronously

```python
# Current (WRONG):
intent, confidence = intent_classifier._rule_based_classify(query.lower())

# Should be:
# asyncio.run() or pytest-asyncio
```

---

## 🟢 Low Priority

### 5. Missing Input Validation
**File**: `app/api/v1/endpoints/documents.py` (Line 19)
**Issue**: No validation on intent_space parameter

### 6. Resource Management
**File**: `app/core/embedding.py`
**Issue**: Model loaded on every container start, no lazy loading

---

## Recommendations

1. **Fix cache bug immediately** - Move cache check after intent classification
2. **Add structured logging** - Replace print statements with proper logging
3. **Implement circuit breaker** - For Ollama connection failures
4. **Add request timeouts** - All external calls should have timeouts
5. **Add metrics collection** - Track cache hit rates, response times
6. **Improve test coverage** - Add integration tests for full pipeline

---

## Files Modified

See PR with fixes for:
- `app/core/query_orchestrator.py`
- `app/api/v1/endpoints/documents.py`
- `app/api/v1/endpoints/queries.py`
- `tests/test_intent_classifier.py`
