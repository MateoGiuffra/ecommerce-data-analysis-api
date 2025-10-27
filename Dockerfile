# --- 1. Build Stage: Install dependencies ---
# Use an official Python image as a parent image
FROM python:3.12-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry'

# Set the working directory in the container
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy only the files needed for dependency installation
COPY pyproject.toml poetry.lock ./

# Install dependencies, excluding development ones
RUN poetry install --no-root --without dev

# --- 2. Final Stage: Create the production image ---
FROM python:3.12-slim as final

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copy the installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
# Copy executables installed by poetry
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/
COPY --from=builder /usr/local/bin/celery /usr/local/bin/
COPY --from=builder /usr/local/bin/alembic /usr/local/bin/

# Copy the application source code
COPY ./src ./src
COPY ./alembic ./alembic
COPY ./scripts ./scripts
COPY alembic.ini .
COPY entrypoint.sh .

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint for the container
# This allows us to specify the command (web, worker, beat) in Render's start command
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["web"]