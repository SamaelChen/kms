# Brainstorm: Fix Dashboard API Connection Error in Docker

**Date:** 2026-03-14
**Status:** Open

## What We're Building

Fix the API connection error that occurs when the Streamlit dashboard runs inside a Docker container but tries to connect to `localhost:8000` instead of the actual API container.

**Error Message:**
```
API connection error: HTTPConnectionPool(host='localhost', port=8000): Max retries exceeded with url: /api/v1/analytics/stats (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x77bdc5129a50>: Failed to establish a new connection: [Errno 111] Connection refused'))
```

## Why This Happens

1. The dashboard files hardcode `API_URL = "http://localhost:8000"`
2. When running in Docker, each container has its own `localhost`
3. The dashboard container's `localhost:8000` points to itself, not the API container
4. In Docker Compose, the API service is accessible via `http://api:8000` (service name)

## Proposed Approaches

### Approach 1: Environment Variable (Recommended)

**Description:** Make `API_URL` configurable via environment variable with a sensible default.

**Implementation:**
- Change hardcoded `API_URL` to read from environment variable
- Default to `http://localhost:8000` for local development
- Set `API_URL=http://api:8000` in docker-compose.yml for Docker deployment

**Files to modify:**
- `admin-dashboard/app.py`
- `admin-dashboard/pages/2_Documents.py`
- `admin-dashboard/pages/3_Intent_Spaces.py`
- `admin-dashboard/pages/4_Integrations.py`
- `admin-dashboard/pages/5_Analytics.py`
- `admin-dashboard/pages/6_Chat.py`
- `docker-compose.yml`

**Pros:**
- Simple and standard practice
- Works for both local development and Docker
- Easy to understand and maintain
- No additional dependencies

**Cons:**
- Need to update multiple dashboard files
- Environment variable must be set correctly

**Code Example:**
```python
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")
```

### Approach 2: Centralized Config Module

**Description:** Create a shared config module that all dashboard pages import.

**Implementation:**
- Create `admin-dashboard/config.py` with API_URL
- All pages import from this config
- Still use environment variable override

**Pros:**
- Single source of truth
- Easier to maintain
- Can add other config values

**Cons:**
- More refactoring needed
- Still need to update imports in all pages

### Approach 3: Docker Network Aliases

**Description:** Configure Docker networking to make API available at `localhost:8000` within dashboard container.

**Implementation:**
- Add `network_mode: host` (not recommended, breaks container isolation)
- Or use `extra_hosts` to map `localhost` to API container (hacky)

**Pros:**
- No code changes needed

**Cons:**
- Breaks Docker best practices
- Not portable
- Can cause port conflicts
- Makes testing harder

### Approach 4: Auto-Detection Logic

**Description:** Detect if running inside Docker and automatically switch URL.

**Implementation:**
- Check for Docker-specific environment variables
- Try `api:8000` first, fallback to `localhost:8000`

**Pros:**
- Automatic, no manual config

**Cons:**
- Magic behavior that might confuse users
- Fragile (depends on Docker internals)
- Harder to debug when it fails

## Recommendation

**Go with Approach 1 (Environment Variable)** because:
1. It's the industry standard for containerized applications
2. Simple to implement and understand
3. Works reliably in both environments
4. Easy to document and communicate

## Key Decisions

1. **Use `API_URL` environment variable** with default fallback
2. **Set `API_URL=http://api:8000`** in docker-compose.yml dashboard service
3. **Update all 6 dashboard files** to use the environment variable
4. **Document** the configuration requirement for developers

## Open Questions

- Should we validate the API_URL format?
- Should we show a helpful error message if connection fails, suggesting to check API_URL?
- Should we create a shared config module as a future improvement?

## Implementation Steps

1. Update `docker-compose.yml` to add `API_URL=http://api:8000` to dashboard service
2. Update each dashboard file to read from environment variable
3. Test locally (should work with default)
4. Test in Docker (should work with env var)
5. Update documentation if needed

## Acceptance Criteria

- [ ] Dashboard connects to API successfully when running in Docker
- [ ] Dashboard still works when running locally (without Docker)
- [ ] Error message is helpful if API_URL is misconfigured
- [ ] All dashboard pages use the same configuration method
