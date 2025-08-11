FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy MCP server files
COPY ../mcp-server/mcp_server_stdio.py ./mcp-server/
COPY ../mcp-server/requirements.txt ./mcp-server/

# Install MCP server dependencies
RUN pip install --no-cache-dir -r mcp-server/requirements.txt

# Copy MCPO wrapper files
COPY setup_mcpo.py .
COPY config/ ./config/

# Create non-root user
RUN useradd -m -u 1000 mcpo && chown -R mcpo:mcpo /app
USER mcpo

# Expose MCPO port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Default command
CMD ["python", "setup_mcpo.py", "--port", "8002", "--mode", "config"]