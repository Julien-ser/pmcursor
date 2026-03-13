# Production Dockerfile for PMCursor
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash pmcursor && \
    chown -R pmcursor:pmcursor /app

# Switch to non-root user
USER pmcursor

# Copy requirements first for better caching
COPY --chown=pmcursor:pmcursor requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=pmcursor:pmcursor . .

# Create necessary directories with proper permissions
RUN mkdir -p uploads data logs && \
    chmod -R 755 uploads data logs

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose the port the app runs on
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run the application with gunicorn in production
CMD ["gunicorn", "src.api.server:app", "--workers", "4", "--bind", "0.0.0.0:8000", "--access-logfile", "-"]
