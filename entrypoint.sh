#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# The first argument to this script is the command to run (e.g., "web", "worker", "beat")
COMMAND=$1

echo "Running entrypoint with command: $COMMAND"

if [ "$COMMAND" = "web" ]; then
    # For the web service, first run database migrations
    echo "Running database migrations..."
    alembic upgrade head
    
    # Then start the web server
    echo "Starting Uvicorn web server..."
    exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}

elif [ "$COMMAND" = "worker" ]; then
    echo "Starting Celery worker..."
    exec celery -A src.tasks.worker.celery_app worker -l info

elif [ "$COMMAND" = "beat" ]; then
    echo "Starting Celery beat scheduler..."
    exec celery -A src.tasks.worker.celery_app beat -l info

else
    echo "Unknown command: $COMMAND"
    exit 1
fi