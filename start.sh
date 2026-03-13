#!/bin/bash
# PMCursor Production Startup Script

set -e  # Exit on error

echo "========================================"
echo "PMCursor Production Startup"
echo "========================================"

# Check for required environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "ERROR: OPENAI_API_KEY is not set"
    echo "Please set it in .env file or environment"
    exit 1
fi

# Create necessary directories if they don't exist
mkdir -p uploads data logs

# Set defaults if not provided
export APP_HOST=${APP_HOST:-0.0.0.0}
export APP_PORT=${APP_PORT:-8000}
export DEBUG=${DEBUG:-False}
export DATABASE_URL=${DATABASE_URL:-sqlite:///./pmcursor.db}
export MAX_UPLOAD_SIZE_MB=${MAX_UPLOAD_SIZE_MB:-100}

# Determine number of workers (CPU cores * 2 + 1 is a good rule of thumb)
WORKERS=${WORKERS:-4}

echo "Configuration:"
echo "  Host: $APP_HOST"
echo "  Port: $APP_PORT"
echo "  Workers: $WORKERS"
echo "  Debug: $DEBUG"
echo "  Database: $DATABASE_URL"
echo ""

echo "Starting PMCursor with gunicorn..."
echo "Health check: http://$APP_HOST:$APP_PORT/health"
echo ""

exec gunicorn src.api.server:app \
    --workers $WORKERS \
    --bind "$APP_HOST:$APP_PORT" \
    --access-logfile "-" \
    --error-logfile "-" \
    --log-level "${LOG_LEVEL:-info}" \
    --timeout 120 \
    --keep-alive 5
