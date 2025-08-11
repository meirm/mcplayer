# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) architecture project focused on creating a unified interface layer between backend services and multiple client types (web frontends and AI agents). The architecture eliminates the need for maintaining separate APIs for human and AI interfaces.

## Key Architecture Concepts

### MCP Server Layer
- Tools: Executable functions for create, update, delete operations
- Resources: Data access points for queries, lists, and aggregations  
- Prompts: AI interaction templates
- Implementation typically in Python with FastMCP or Node.js with MCP SDKs

### MCP-HTTP Bridge Layer
- Translates MCP protocol to HTTP for web clients
- Generates REST-like endpoints from MCP definitions
- Provides WebSocket support for progress notifications
- Handles authentication, sessions, and CORS

### Client Integration Patterns
- Web clients use React/Vue hooks that consume the HTTP bridge
- Mobile apps use SDKs wrapping HTTP bridge calls
- AI agents connect directly via MCP or through the bridge

## Development Patterns

### MCP Tool Implementation
Tools are async functions decorated with `@mcp.tool()` that:
- Accept Pydantic models for input validation
- Use Context for progress reporting and logging
- Return structured data for clients
- Support batch operations with progress callbacks

### Resource Implementation
Resources are decorated with `@mcp.resource("protocol://path")` and:
- Provide data access with filtering and pagination
- Return structured responses with metadata
- Support query parameters for flexible data retrieval

### HTTP Bridge Patterns
- Auto-generates REST endpoints from MCP tools: `/api/tools/{tool_name}`
- Maps resources to GET endpoints: `/api/resources/{resource_path}`
- WebSocket endpoints for progress tracking: `/ws/tools/{tool_name}`
- Discovery endpoint for capability inspection: `/api/discovery`

### Frontend Integration (React/TypeScript)
- Use `useMCP()` hook for tool execution and resource reading
- Support both HTTP and WebSocket connections for progress tracking
- Handle async operations with proper error boundaries
- Maintain type safety from backend to frontend

## Implementation Phases

1. **Proof of Concept**: Basic MCP server with minimal HTTP bridge and React demo
2. **Production Features**: Authentication, error handling, monitoring, performance optimization
3. **Advanced Capabilities**: Real-time subscriptions, batch operations, transaction support

## Security Considerations

- Authentication handled at bridge layer with context injection
- Rate limiting with different limits for UI vs AI clients
- Input validation via Pydantic models at MCP server level
- Permission checks within tool implementations using context