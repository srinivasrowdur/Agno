# Docker Deployment for Agno Chat API

This guide explains how to deploy the production-ready Agno Chat API using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed on your system
- OpenAI API key

## Production Features

Our Docker setup includes the following production-ready features:

- **Multi-stage build** for smaller images
- **Non-root user** for improved security
- **Health checks** for container orchestration
- **Signal handling** for graceful shutdowns
- **Worker scaling** based on available CPU cores
- **Structured logging** for production environments
- **Environment-specific configuration**

## Deployment Steps

### 1. Set Environment Variables

Configure your application by creating a `.env` file based on `.env.example`:

```bash
# Required settings
OPENAI_API_KEY=your_openai_api_key_here

# Optional settings (with defaults shown)
MODEL_NAME=gpt-4
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-domain.com
```

### 2. Build and Run with Docker Compose

```bash
# Build and start the container
docker compose up --build -d
```

### 3. Verify Deployment

The API will be accessible at http://localhost:8000

Test the health check endpoint:

```bash
curl http://localhost:8000/
```

Or test the chat endpoint using the included test script:

```bash
python test_api.py
```

### 4. Managing the Container

To view logs:
```bash
docker compose logs -f
```

To stop the container:
```bash
docker compose down
```

## Docker Configuration Explanation

### Dockerfile

Our Dockerfile implements these best practices:

1. **Multi-stage build** - Uses a build stage to install dependencies, then copies only what's needed to the final image
2. **Security hardening** - Runs as non-root user (app:app)
3. **Minimal dependencies** - Installs only necessary system packages
4. **Cache optimization** - Organizes layers to maximize build cache usage
5. **Environment configuration** - Sets appropriate environment variables

### docker-compose.yml

The production configuration:
- Maps port 8000 from the container to the host
- Passes environment variables from host to container
- Configures health checks for container orchestration
- Sets appropriate restart policy for reliability
- Disables volume mounts in production for security

### entrypoint.sh

The entrypoint script provides:
- Proper signal handling for graceful shutdowns
- Environment validation to catch configuration errors early
- Dynamic worker configuration based on available resources
- Environment-specific server settings

### .dockerignore

Excludes unnecessary files from the Docker build context to keep the image size small and improve build times. 