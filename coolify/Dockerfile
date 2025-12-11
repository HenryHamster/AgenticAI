# Multi-Agent Dockerfile for Coolify
# Runs 1 Green Agent + 2 Purple Agents behind nginx reverse proxy
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies including nginx and supervisor
RUN apt-get update && apt-get install -y \
    gcc \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the backend application
COPY backend/ .

# Copy nginx and supervisor configurations from coolify folder
COPY coolify/docker/nginx.conf /etc/nginx/nginx.conf
COPY coolify/docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create logs directory
RUN mkdir -p /var/log/agents /var/log/nginx

# Expose port 80 (nginx will handle routing)
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start supervisor (which manages nginx and all agents)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
