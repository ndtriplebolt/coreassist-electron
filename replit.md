# Overview

CoreAssist Voice Agent Backend is a FastAPI-based system that provides a dynamic tools manifest and unified tool router for voice agent applications. The system features a pluggable connector architecture that allows third-party integrations to be loaded dynamically from the `connectors/` directory. It supports both namespaced tool routing (e.g., `slack.send_message`) and generic tool calls, with shared secret authentication for API security.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Framework
- **FastAPI Backend**: RESTful API with automatic OpenAPI documentation and request/response validation using Pydantic models
- **Connector Registry System**: Abstract base class `Connector` with dynamic loading mechanism that discovers connectors from the filesystem
- **Manifest-Driven Configuration**: Each connector includes a `manifest.json` file defining available tools, parameters, and authentication requirements

## Authentication Architecture
- **Shared Secret Model**: All POST endpoints require `X-Auth` header validation against `SHARED_SECRET` environment variable
- **In-Memory Auth Store**: Current implementation uses in-memory storage for users, sessions, and connector credentials with clear migration path to database
- **OAuth2 Integration Points**: Prepared infrastructure for OAuth2 flows with Google and Slack APIs (currently stubbed with TODO implementations)

## Tool Execution System
- **Unified Router**: Single `/tools/call` endpoint handles all tool executions regardless of connector
- **Namespaced Resolution**: Supports both `connector.tool_name` and generic `tool_name` routing patterns
- **Parameter Validation**: Pydantic models ensure type safety and automatic validation for tool parameters

## Connector Architecture
- **Plugin System**: Connectors are discovered and loaded automatically from `connectors/` directory structure
- **Standardized Interface**: All connectors implement the abstract `Connector` class with consistent `execute()` method signature
- **Manifest Schema**: JSON manifests define tool metadata, parameters, authentication requirements, and OAuth scopes

# External Dependencies

## Core Dependencies
- **FastAPI**: Web framework providing async support and automatic API documentation
- **Uvicorn**: ASGI server for running the FastAPI application
- **Pydantic**: Data validation and serialization using Python type annotations
- **OpenAI SDK**: Integration for OpenAI-based connectors and AI capabilities

## Third-Party Service Integrations
- **Google Calendar API**: OAuth2-based integration for calendar event management
- **Google Tasks API**: OAuth2-based integration for task list and task management
- **Slack API**: OAuth2-based integration for messaging and channel management

## Development Infrastructure
- **CORS Middleware**: Configured for cross-origin requests to support frontend integration
- **Environment Configuration**: Uses `python-dotenv` for environment variable management
- **Dynamic Module Loading**: Uses `importlib.util` for runtime connector discovery and loading

## Authentication Services
- **OAuth2 Providers**: Google Cloud Platform and Slack for service-specific authentication
- **Token Management**: Infrastructure prepared for access token storage and refresh (currently in development)

Note: OAuth2 flows are currently stubbed with TODO implementations, indicating planned but not yet complete integration with external authentication providers.