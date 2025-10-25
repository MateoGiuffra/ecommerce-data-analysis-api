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
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn

# Copy the application source code
COPY ./src ./src
COPY ./alembic ./alembic
COPY alembic.ini .

# Command to run the application
# The web server will bind to 0.0.0.0 to be accessible from outside the container.
# Render provides the PORT environment variable.
CMD uvicorn src.main:app --host 0.0.0.0 --port $PORT