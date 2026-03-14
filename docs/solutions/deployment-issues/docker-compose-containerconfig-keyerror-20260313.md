---
module: Docker Deployment
date: 2026-03-13
problem_type: deployment_issue
component: docker
category: deployment-issues
symptoms:
  - "KeyError: 'ContainerConfig' in docker-compose/service.py"
  - "ERROR: for kms_api_1 'ContainerConfig'"
  - "ERROR: for api 'ContainerConfig'"
  - "docker-compose up fails with ContainerConfig error"
root_cause: version_incompatibility
severity: high
tags: [docker, docker-compose, containerconfig, version-mismatch, ubuntu-24.04]
---

# Docker Compose ContainerConfig KeyError

## Problem Description

When running `docker-compose up -d` on Ubuntu 24.04 (or systems with Docker Engine v24+), the command fails with a `KeyError: 'ContainerConfig'` error.

## Exact Error Message

```
ERROR: for kms_api_1  'ContainerConfig'
ERROR: for api  'ContainerConfig'
Traceback (most recent call last):
  File "/usr/bin/docker-compose", line 33, in <module>
    sys.exit(load_entry_point('docker-compose==1.29.2', 'console_scripts', 'docker-compose')())
  ...
  File "/usr/lib/python3/dist-packages/compose/service.py", line 1579, in get_container_data_volumes
    container.image_config['ContainerConfig'].get('Volumes') or {}
KeyError: 'ContainerConfig'
```

## Environment

- **OS**: Ubuntu 24.04
- **Docker Engine**: v24.x or newer
- **Docker Compose**: v1.29.2 (python package)
- **Project**: IntelliKnow KMS

## Root Cause

Docker Compose v1 (the Python package `docker-compose`) is **incompatible** with Docker Engine v24+. The ContainerConfig field was changed/removed in newer Docker API versions, causing the KeyError.

Ubuntu 24.04 ships with:
- Docker Engine v24.x or newer
- Docker Compose v2.x as a plugin (uses `docker compose` syntax)

The old `docker-compose` (v1) command is deprecated.

## Solution

### Option 1: Use Docker Compose v2 (Recommended)

Replace `docker-compose` (hyphen) with `docker compose` (space):

```bash
# ❌ WRONG - Old v1 syntax
docker-compose up -d

# ✅ CORRECT - Modern v2 syntax
docker compose up -d
```

### Option 2: Full Command Examples

```bash
# Build and start services
docker compose up -d --build

# View logs
docker compose logs -f

# Stop services
docker compose down

# Restart specific service
docker compose restart api
```

### Option 3: Prune and Fresh Start

If containers were created with v1 and are now broken:

```bash
# Stop and remove old containers
docker-compose down 2>/dev/null || docker compose down

# Remove problematic containers
docker rm -f $(docker ps -aq --filter name=kms)

# Fresh start with v2
docker compose up -d --build
```

## Prevention

### For Development Teams

1. **Standardize on Docker Compose v2**:
   ```bash
   # Check version
   docker compose version  # Should show v2.x
   ```

2. **Update scripts and documentation**:
   - Replace all `docker-compose` with `docker compose`
   - Update CI/CD pipelines
   - Update README files

3. **Add to project setup**:
   ```bash
   # In setup scripts, verify v2 is available
   if ! docker compose version &> /dev/null; then
       echo "Error: Docker Compose v2 is required"
       exit 1
   fi
   ```

### For CI/CD

```yaml
# GitHub Actions example
- name: Start services
  run: |
    docker compose up -d --build
```

## Verification

After switching to v2, verify everything works:

```bash
# Check containers are running
docker ps

# Test API health
curl http://localhost:8000/api/v1/health/

# Check logs
docker compose logs -f api
```

## Related Issues

- Docker Compose v1 deprecation: https://docs.docker.com/compose/migrate/
- Ubuntu 24.04 Docker installation: See README.md Docker section

## References

- [Docker Compose Migration Guide](https://docs.docker.com/compose/migrate/)
- [Docker Engine API Changes](https://docs.docker.com/engine/api/)

---

**Documentation created**: 2026-03-13  
**Last updated**: 2026-03-13  
**Solution verified**: ✅ Yes - Confirmed working on Ubuntu 24.04
