.PHONY: help build up down logs clean install dev

# Default target
help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies for all services"
	@echo "  make build     - Build all podman containers"
	@echo "  make up        - Start all services with podman-compose"
	@echo "  make down      - Stop all services"
	@echo "  make logs      - Show logs from all services"
	@echo "  make clean     - Clean up containers and volumes"
	@echo "  make dev       - Run services in development mode (without containers)"
	@echo "  make test      - Run tests for all services"

# Install dependencies
install:
	@echo "Installing backend dependencies..."
	cd apps/backend && pip install -r requirements.txt
	@echo "Installing MCP server dependencies..."
	cd apps/mcp-server && pip install -r requirements.txt
	@echo "Installing MCP proxy dependencies..."
	cd apps/mcp-proxy && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd apps/frontend && npm install

# Build containers
build:
	podman-compose build

# Start services
up:
	podman-compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "MCP Bridge API: http://localhost:8000"
	@echo "Backend API: http://localhost:8001"
	@echo "API Discovery: http://localhost:8000/api/discovery"

# Stop services
down:
	podman-compose down

# Show logs
logs:
	podman-compose logs -f

# Show logs for specific service
logs-backend:
	podman-compose logs -f backend

logs-mcp:
	podman-compose logs -f mcp-server

logs-bridge:
	podman-compose logs -f mcp-bridge

logs-frontend:
	podman-compose logs -f frontend

# Clean up
clean:
	podman-compose down -v
	podman system prune -f

# Development mode (run without containers)
dev:
	@echo "Starting services in development mode..."
	@echo "Start each service in a separate terminal:"
	@echo "1. Backend API: cd apps/backend && python main.py"
	@echo "2. MCP Server: cd apps/mcp-server && python server.py"
	@echo "3. MCP Bridge: cd apps/mcp-proxy && python mcp_bridge.py"
	@echo "4. Frontend: cd apps/frontend && npm start"

# Run tests
test:
	@echo "Running tests..."
	cd apps/backend && python -m pytest tests/ || true
	cd apps/mcp-server && python -m pytest tests/ || true
	cd apps/mcp-proxy && python -m pytest tests/ || true
	cd apps/frontend && npm test || true

# Individual service commands
backend:
	cd apps/backend && python main.py

mcp-server:
	cd apps/mcp-server && python server.py

mcp-bridge:
	cd apps/mcp-proxy && python mcp_bridge.py

frontend:
	cd apps/frontend && npm start

# Podman-specific commands
pod-create:
	podman pod create --name mcp-pod -p 3000:3000 -p 8000:8000

pod-start:
	podman pod start mcp-pod

pod-stop:
	podman pod stop mcp-pod

pod-rm:
	podman pod rm mcp-pod