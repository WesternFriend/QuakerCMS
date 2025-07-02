# Build stage
FROM python:3.12-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_CACHE_DIR=/tmp/uv-cache

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Runtime stage
FROM python:3.12-slim as runtime

# Create non-root user
RUN groupadd --gid 1000 wagtail \
    && useradd --uid 1000 --gid wagtail --shell /bin/bash --create-home wagtail

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Set work directory and change ownership
WORKDIR /app
RUN chown wagtail:wagtail /app

# Switch to non-root user
USER wagtail

# Copy virtual environment from builder stage
COPY --from=builder --chown=wagtail:wagtail /app/.venv /app/.venv

# Install Gunicorn for production server
RUN pip install gunicorn

# Copy project
COPY --chown=wagtail:wagtail . .

# Create entrypoint script with proper error handling and production server
RUN echo '#!/bin/bash\n\
    set -euo pipefail\n\
    \n\
    # Function to handle shutdown signals\n\
    shutdown() {\n\
    echo "Received shutdown signal, stopping Gunicorn gracefully..."\n\
    kill -TERM "$child" 2>/dev/null\n\
    wait "$child"\n\
    }\n\
    \n\
    # Trap signals and forward to shutdown function\n\
    trap shutdown SIGTERM SIGINT\n\
    \n\
    cd src\n\
    \n\
    # Start Gunicorn with proper configuration\n\
    exec gunicorn core.wsgi:application \\\n\
    --bind 0.0.0.0:8000 \\\n\
    --workers 3 \\\n\
    --worker-class sync \\\n\
    --worker-connections 1000 \\\n\
    --max-requests 1000 \\\n\
    --max-requests-jitter 100 \\\n\
    --timeout 30 \\\n\
    --keep-alive 2 \\\n\
    --access-logfile - \\\n\
    --error-logfile - \\\n\
    --log-level info &\n\
    \n\
    # Store the PID of the background process\n\
    child=$!\n\
    \n\
    # Wait for the background process\n\
    wait "$child"' > /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8000

# Run the application
CMD ["/app/entrypoint.sh"]
