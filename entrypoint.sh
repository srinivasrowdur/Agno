#!/bin/bash
set -e

# Function to handle shutdown signal
function handle_sigterm() {
    echo "Received SIGTERM, shutting down gracefully..."
    kill -TERM "$child_pid"
    wait "$child_pid"
    echo "Server stopped, exiting."
    exit 0
}

# Register the signal handler
trap 'handle_sigterm' TERM INT

echo "Starting Agno Chat API server..."

# Check for required environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "ERROR: OPENAI_API_KEY environment variable is required"
    exit 1
fi

# Set number of workers based on available CPUs if not specified
if [ -z "$WORKERS" ]; then
    WORKERS=$(nproc --all)
    # Use at least 1 worker, at most 4
    WORKERS=$((WORKERS > 4 ? 4 : WORKERS))
    WORKERS=$((WORKERS < 1 ? 1 : WORKERS))
fi

# Set log level based on environment if not specified
if [ -z "$LOG_LEVEL" ]; then
    if [ "$ENVIRONMENT" = "production" ]; then
        LOG_LEVEL="INFO"
    else
        LOG_LEVEL="DEBUG"
    fi
fi

# Print configuration
echo "Configuration:"
echo "- Environment: ${ENVIRONMENT:-development}"
echo "- Workers: $WORKERS"
echo "- Log Level: $LOG_LEVEL"

# Start server with proper settings
if [ "$ENVIRONMENT" = "production" ]; then
    # Use Gunicorn with Uvicorn workers in production
    gunicorn app.main:app \
        --bind 0.0.0.0:8000 \
        --workers $WORKERS \
        --worker-class uvicorn.workers.UvicornWorker \
        --log-level $LOG_LEVEL &
else
    # Use Uvicorn in development for hot reloading
    uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --log-level $LOG_LEVEL \
        --reload &
fi

# Store the PID of the server process
child_pid=$!

# Wait for the server process to finish
wait "$child_pid" 