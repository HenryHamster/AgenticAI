# Green Agent Dockerfile for AgentBeats
# Uses earthshaker (agentbeats run_ctrl) for agent lifecycle management
FROM python:3.13-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY coolify/green_agent/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the backend application
COPY backend/ .

# Copy run.sh from green_agent folder
COPY coolify/green_agent/run.sh /app/run.sh
RUN chmod +x /app/run.sh

# Create logs directory
RUN mkdir -p /var/log/agents

# Default port for the controller (can be overridden)
ENV CONTROLLER_PORT=8080
EXPOSE 8080

# Health check via controller status endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${CONTROLLER_PORT}/status || exit 1

# Start the AgentBeats controller
CMD ["agentbeats", "run_ctrl"]
