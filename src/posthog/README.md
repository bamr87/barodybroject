# PostHog Docker Deployment

This is a Docker Compose setup for running PostHog locally with environment variable configuration.

## Overview

PostHog is an open-source product analytics platform. This setup includes:
- PostgreSQL (database)
- Redis (caching)
- ClickHouse (analytics database)
- Kafka (event streaming)
- Zookeeper (Kafka coordination)
- PostHog Web Server
- PostHog Worker (background jobs)
- PostHog Plugins Server

## Environment Configuration

All configuration has been abstracted into environment variables for easier management and deployment across different environments.

### Files

- `.env` - Contains all environment variables (DO NOT commit to version control)
- `.env.example` - Template file with default values (safe to commit)
- `docker-compose.yml` - Docker Compose configuration using environment variables
- `.gitignore` - Ensures `.env` and data directories are not committed

### Environment Variables

The following categories of variables are configured:

#### Database
- `POSTGRES_USER` - PostgreSQL username
- `POSTGRES_DB` - PostgreSQL database name
- `POSTGRES_PASSWORD` - PostgreSQL password
- `DATABASE_URL` - Full PostgreSQL connection string

#### ClickHouse
- `CLICKHOUSE_HOST` - ClickHouse server hostname
- `CLICKHOUSE_DATABASE` - ClickHouse database name
- `CLICKHOUSE_USER` - ClickHouse username
- `CLICKHOUSE_PASSWORD` - ClickHouse password
- `CLICKHOUSE_SECURE` - Use TLS connection (true/false)
- `CLICKHOUSE_VERIFY` - Verify TLS certificates (true/false)

#### Redis
- `REDIS_URL` - Redis connection URL
- `REDIS_MAX_MEMORY` - Maximum memory allocation for Redis

#### Kafka & Zookeeper
- `KAFKA_BROKER_ID` - Kafka broker ID
- `KAFKA_ZOOKEEPER_CONNECT` - Zookeeper connection string
- `KAFKA_ADVERTISED_LISTENERS` - Kafka advertised listeners
- `KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR` - Replication factor
- `KAFKA_TRANSACTION_STATE_LOG_MIN_ISR` - Min in-sync replicas
- `KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR` - Replication factor
- `KAFKA_HOSTS` - Kafka hosts for PostHog
- `ZOOKEEPER_CLIENT_PORT` - Zookeeper client port
- `ZOOKEEPER_TICK_TIME` - Zookeeper tick time

#### PostHog Application
- `SECRET_KEY` - Django secret key
- `SITE_URL` - Public URL for PostHog
- `WEB_PORT` - Port to expose web interface (default: 8080)
- `IS_BEHIND_PROXY` - Whether behind a proxy
- `DISABLE_SECURE_SSL_REDIRECT` - Disable SSL redirect
- `TRUST_ALL_PROXIES` - Trust all proxy headers

#### Plugin Server
- `ENCRYPTION_KEYS` - Encryption keys for plugins
- `ENCRYPTION_SALT_KEYS` - Salt keys for encryption

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB of available RAM

### Setup

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Customize the `.env` file:**
   Edit `.env` and update values as needed:
   - Change passwords for production use
   - Update `SECRET_KEY` (generate a new one)
   - Update `SITE_URL` if not using localhost
   - Update `WEB_PORT` if port 8080 is in use

3. **Generate secure keys:**
   ```bash
   # Generate SECRET_KEY
   openssl rand -hex 32
   
   # Generate ENCRYPTION_KEYS
   openssl rand -base64 32
   ```

### Running PostHog

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Check status:**
   ```bash
   docker-compose ps
   ```

3. **View logs:**
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f web
   ```

4. **Access PostHog:**
   Open your browser to: `http://localhost:8080` (or your configured `SITE_URL`)

### Stopping PostHog

```bash
# Stop services but keep data
docker-compose stop

# Stop and remove containers (keeps data volumes)
docker-compose down

# Stop, remove containers AND delete all data
docker-compose down -v
```

## Validation

After starting the services, you can verify the deployment:

```bash
# Check HTTP response
curl -I http://localhost:8080

# Expected: HTTP 302 redirect to /preflight
```

## Configuration Validation

Before deploying, validate your configuration:

```bash
docker-compose config
```

This will show the resolved configuration with all environment variables substituted.

## Troubleshooting

### Services not starting

Check logs for specific service:
```bash
docker-compose logs [service-name]
```

Service names: `db`, `redis`, `clickhouse`, `kafka`, `zookeeper`, `worker`, `web`, `plugins`

### Connection issues

1. Ensure all services are running:
   ```bash
   docker-compose ps
   ```

2. Check network connectivity:
   ```bash
   docker network ls
   docker network inspect posthog_default
   ```

### Database migration issues

View web service logs to see migration progress:
```bash
docker-compose logs -f web | grep -i migrate
```

### Port conflicts

If port 8080 is in use, update `WEB_PORT` in `.env`:
```bash
WEB_PORT=8081
```

Then restart:
```bash
docker-compose up -d
```

## Data Persistence

Data is persisted in Docker volumes:
- `posthog_postgres-data` - PostgreSQL data
- `posthog_clickhouse-data` - ClickHouse data
- `posthog_zookeeper-data` - Zookeeper data
- `posthog_zookeeper-logs` - Zookeeper logs

To backup data:
```bash
docker run --rm -v posthog_postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz -C /data .
```

## Security Notes

⚠️ **Important for Production:**

1. Change all default passwords in `.env`
2. Generate new `SECRET_KEY` and `ENCRYPTION_KEYS`
3. Never commit `.env` file to version control
4. Use proper SSL/TLS certificates
5. Set `CLICKHOUSE_SECURE=true` and `CLICKHOUSE_VERIFY=true` for production
6. Review and harden ClickHouse configuration
7. Use a proper reverse proxy (nginx, Caddy, Traefik)

## Development vs Production

This setup is optimized for development. For production:

1. Use managed databases (RDS, Cloud SQL, etc.)
2. Use managed Kafka (MSK, Confluent Cloud, etc.)
3. Enable SSL/TLS for all connections
4. Use proper secret management (AWS Secrets Manager, HashiCorp Vault, etc.)
5. Set up monitoring and alerting
6. Configure proper backups
7. Review PostHog's official production deployment guides

## Resources

- [PostHog Documentation](https://posthog.com/docs)
- [PostHog GitHub](https://github.com/PostHog/posthog)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## License

This configuration follows PostHog's MIT license.
