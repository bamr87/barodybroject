# PostHog Docker Deployment - AI Agent Instructions

## Architecture Overview

This is a **Docker Compose-based PostHog deployment** (not the PostHog source code). The system uses an event-driven architecture with 8 interconnected services:

```
Web (Django) ─┬─> PostgreSQL (metadata)
              ├─> ClickHouse (analytics data) ─> Zookeeper
              ├─> Redis (cache)
              └─> Kafka (events) ─> Zookeeper
                    ↓
Worker (Celery) + Plugins (Node.js)
```

**Key Dependencies**: Web service waits for all infrastructure (db, redis, clickhouse, kafka, worker) before starting. Migrations run automatically on web service startup via `docker-compose.yml` command: `sh -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"`.

## Configuration Pattern

**ALL configuration lives in environment variables** - never hardcode values in `docker-compose.yml` or ClickHouse XML configs.

### Critical Files
- `.env` - Active configuration (git-ignored, contains secrets)
- `.env.example` - Template with defaults (committed to git)
- `docker-compose.yml` - Uses `${VAR_NAME}` syntax for all config
- `clickhouse/config.xml` - Minimal static config (logging, network)
- `clickhouse/users.xml` - User profiles (static, but passwords from `.env`)

### Environment Variable Categories (32 total)
1. **Database** (4): `POSTGRES_*`, `DATABASE_URL`
2. **ClickHouse** (6): `CLICKHOUSE_*` (host, db, user, password, secure, verify)
3. **Redis** (2): `REDIS_URL`, `REDIS_MAX_MEMORY`
4. **Kafka** (7): `KAFKA_*` including replication factors and ISR settings
5. **Zookeeper** (2): `ZOOKEEPER_CLIENT_PORT`, `ZOOKEEPER_TICK_TIME`
6. **PostHog App** (7): `SECRET_KEY`, `SITE_URL`, `WEB_PORT`, proxy settings
7. **Encryption** (2): `ENCRYPTION_KEYS`, `ENCRYPTION_SALT_KEYS` (must be base64url-encoded 32-byte strings)
8. **Server Config** (2): `CLICKHOUSE_LOG_LEVEL`, `CLICKHOUSE_MAX_MEMORY_USAGE`

## Developer Workflows

### Starting/Stopping Services
```bash
# Validate configuration before starting
docker-compose config

# Start all services (detached)
docker-compose up -d

# Check service health
docker-compose ps

# View logs (all or specific service)
docker-compose logs -f [service-name]

# Stop and remove containers (keeps data)
docker-compose down

# Nuclear option: delete all data volumes
docker-compose down -v
```

### Debugging Failures
1. **Service won't start**: Check `docker-compose logs [service-name]` for the specific service
2. **Plugin errors**: Usually encryption key format issues - keys must be base64url (32 bytes, using `-_` not `+/`, no `=` padding)
3. **Migration issues**: Web service logs show migration progress - `docker-compose logs -f web | grep -i migrate`
4. **Expected warnings** (safe to ignore):
   - "Skipping async migrations setup. This is unsafe in production!" (dev mode)
   - "pkg_resources is deprecated" (Python library warning)
   - "GeoLite2 MMDB file not found" (optional geolocation feature)

### Testing Deployment
```bash
# Expected: HTTP 302 redirect to /preflight (initial setup page)
curl -I http://localhost:8080

# Check for critical errors (returns 0 if none found)
docker-compose logs --tail=50 2>&1 | grep -i "error\|failed\|exception" || echo "No critical errors"
```

## Project-Specific Conventions

### Encryption Keys Must Use Base64URL Format
Standard base64 uses `+/=`, but PostHog plugin server requires base64url (`-_` and no padding):
```bash
# Generate correctly formatted keys
openssl rand -base64 32 | tr '+/' '-_' | tr -d '='
```

### Service Names Are Fixed
When modifying `docker-compose.yml`, use these exact service names (PostHog expects them):
- `db` (PostgreSQL)
- `redis` 
- `clickhouse`
- `kafka`
- `zookeeper`
- `web` (Django app)
- `worker` (Celery)
- `plugins` (Node.js plugin server)

### ClickHouse Configuration Split
- `clickhouse/config.xml` - Server settings (logging disabled to reduce noise)
- `clickhouse/users.xml` - User profiles with hardcoded password (matches `.env` value)
- **Why**: ClickHouse doesn't natively read env vars; config files are mounted as volumes

### Data Persistence Volumes
Named volumes preserve data across container restarts:
- `postgres-data` - All PostHog metadata
- `clickhouse-data` - Analytics events (largest volume)
- `zookeeper-data`, `zookeeper-logs` - Kafka coordination state

## Common Modifications

### Changing Ports
Update `WEB_PORT` in `.env`, then `docker-compose up -d` (auto-recreates with new port mapping).

### Adding New Environment Variables
1. Add to `.env` with value
2. Add to `.env.example` with safe default/placeholder
3. Reference in `docker-compose.yml` as `${NEW_VAR}`
4. Document in `README.md` under "Environment Variables"

### Upgrading PostHog Version
Change image tag in `docker-compose.yml` (3 services use `posthog/posthog:latest`):
```yaml
image: posthog/posthog:1.50.0  # Pin specific version
```

### Production Hardening Checklist
1. Regenerate ALL secrets in `.env` (use commands in README.md)
2. Set `CLICKHOUSE_SECURE=true` and `CLICKHOUSE_VERIFY=true`
3. Change `image: posthog/posthog:latest` to specific version tags
4. Enable TLS for PostgreSQL, Redis, Kafka
5. Use external managed services (RDS, MSK, ElastiCache) instead of Docker containers

## Integration Points

### Web Service Dependencies
Depends on: `db`, `redis`, `clickhouse`, `kafka`, `worker` (sequential startup enforced by `depends_on`).

### Kafka ↔ ClickHouse
Kafka events are consumed by worker/plugins and written to ClickHouse. No direct connection; data flows through PostHog application layer.

### Plugin Server Authentication
Uses `ENCRYPTION_KEYS` to secure plugin configuration data stored in PostgreSQL. Keys must match format or plugins service crashes on startup.

## Anti-Patterns to Avoid

- ❌ Don't hardcode values in YAML - always use `${ENV_VAR}`
- ❌ Don't commit `.env` file (contains secrets)
- ❌ Don't use standard base64 for encryption keys (must be base64url)
- ❌ Don't remove `depends_on` relationships (controls startup order)
- ❌ Don't change volume names (breaks data persistence)
- ❌ Don't skip `docker-compose config` before deploying (catches substitution errors)

## Quick Reference

**First-time setup**: `cp .env.example .env && docker-compose up -d`  
**Access PostHog**: http://localhost:8080  
**Check health**: `docker-compose ps` (all services should show "Up")  
**View errors**: `docker-compose logs --tail=50 | grep -i error`  
**Reset everything**: `docker-compose down -v` (deletes all data)
