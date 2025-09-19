# CoreAssist Voice Agent Backend

A FastAPI backend with pluggable connectors for voice agent tool routing and third-party integrations. This system provides a dynamic tools manifest and unified tool router that supports both namespaced and generic tool calls.

## Features

- **Dynamic Tool Registry**: Automatically discovers and loads connectors from the `connectors/` directory
- **Namespaced Tool Routing**: Supports both `slack.send_message` and generic `send_message` calls
- **Shared Secret Authentication**: All POST endpoints require `X-Auth` header with `SHARED_SECRET`
- **RESTful API**: Clean endpoints for tool manifest, execution, and health checks
- **Example Connectors**: Google Tasks, Google Calendar, and Slack connectors included

## Environment Variables

### Required
- `SHARED_SECRET`: Secret key for API authentication (e.g., `core-assist-dev-secret-2024`)

### Optional
- `OPENAI_API_KEY`: OpenAI API key for OpenAI-based connectors

### Connector-Specific (TODO: Implement OAuth flows)
- Google OAuth credentials:
  - `GOOGLE_CLIENT_ID`
  - `GOOGLE_CLIENT_SECRET`
- Slack OAuth credentials:
  - `SLACK_CLIENT_ID`
  - `SLACK_CLIENT_SECRET`

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export SHARED_SECRET="your-secret-key"
   export OPENAI_API_KEY="your-openai-key"  # optional
   ```

3. **Run the server**:
   ```bash
   cd backend
   python main.py
   ```

4. **Server will start on http://0.0.0.0:5000**

## API Endpoints

### GET /health
Health check endpoint with connector status.

**Example Response**:
```json
{
  "status": "healthy",
  "connectors_loaded": 3,
  "total_tools": 15,
  "auth_stats": {
    "total_users": 0,
    "active_sessions": 0,
    "total_connector_credentials": 0
  }
}
```

### GET /tools/manifest
Get dynamic tools manifest from all loaded connectors.

**Example Response**:
```json
{
  "tools": [
    {
      "name": "slack.send_message",
      "description": "Send a message to a Slack channel or user",
      "parameters": {
        "type": "object",
        "properties": {
          "channel": {"type": "string"},
          "text": {"type": "string"}
        },
        "required": ["channel", "text"]
      }
    }
  ],
  "connectors": ["google_tasks", "google_calendar", "slack"],
  "supports_namespaced_calls": true
}
```

### POST /tools/call
Execute a tool through the unified router.

**Headers**:
- `X-Auth: your-shared-secret`
- `Content-Type: application/json`

**Example Request**:
```json
{
  "tool_name": "slack.send_message",
  "parameters": {
    "channel": "#general",
    "text": "Hello from CoreAssist!"
  },
  "user_id": "user123"
}
```

**Example Response**:
```json
{
  "success": true,
  "result": {
    "message": {
      "ts": "1234567890.123",
      "channel": "#general",
      "text": "Hello from CoreAssist!"
    },
    "ok": true
  }
}
```

## Example curl Commands

### 1. Check Health
```bash
curl http://localhost:5000/health
```

### 2. Get Tools Manifest
```bash
curl http://localhost:5000/tools/manifest
```

### 3. Send Slack Message
```bash
curl -X POST http://localhost:5000/tools/call \\
  -H "X-Auth: core-assist-dev-secret-2024" \\
  -H "Content-Type: application/json" \\
  -d '{
    "tool_name": "slack.send_message",
    "parameters": {
      "channel": "#general",
      "text": "Hello from curl!"
    }
  }'
```

### 4. Create Google Calendar Event
```bash
curl -X POST http://localhost:5000/tools/call \\
  -H "X-Auth: core-assist-dev-secret-2024" \\
  -H "Content-Type: application/json" \\
  -d '{
    "tool_name": "google_calendar.create_event",
    "parameters": {
      "title": "Team Meeting",
      "start_time": "2024-01-15T10:00:00-08:00",
      "end_time": "2024-01-15T11:00:00-08:00",
      "description": "Weekly team sync"
    }
  }'
```

### 5. Create Google Task
```bash
curl -X POST http://localhost:5000/tools/call \\
  -H "X-Auth: core-assist-dev-secret-2024" \\
  -H "Content-Type: application/json" \\
  -d '{
    "tool_name": "google_tasks.create_task",
    "parameters": {
      "tasklist_id": "sample_list_1",
      "title": "Review API documentation",
      "notes": "Focus on authentication flows"
    }
  }'
```

## How to Add a Connector

Adding a new connector is simple:

1. **Create connector directory**:
   ```bash
   mkdir backend/connectors/your_service
   ```

2. **Create manifest.json**:
   ```json
   {
     "info": {
       "name": "Your Service",
       "description": "Description of your service connector",
       "version": "1.0.0",
       "auth_required": true
     },
     "tools": [
       {
         "name": "your_tool",
         "description": "What your tool does",
         "parameters": {
           "type": "object",
           "properties": {
             "param1": {"type": "string"}
           },
           "required": ["param1"]
         }
       }
     ]
   }
   ```

3. **Create connector.py**:
   ```python
   from registry import Connector
   from typing import Dict, Any, Optional

   class YourServiceConnector(Connector):
       async def execute(self, tool_name: str, parameters: Dict[str, Any], auth_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
           if tool_name == "your_tool":
               return await self._your_tool_implementation(parameters, auth_data)
           return {"error": f"Unknown tool: {tool_name}"}
       
       async def _your_tool_implementation(self, parameters: Dict[str, Any], auth_data: Dict[str, Any]) -> Dict[str, Any]:
           # Your implementation here
           return {"result": "success"}
   ```

4. **Restart the server** - The connector will be automatically loaded!

## Sample JSON Payloads

### Slack Tools
```json
// slack.send_message
{
  "tool_name": "slack.send_message",
  "parameters": {
    "channel": "#general",
    "text": "Hello team!",
    "thread_ts": "1234567890.123"
  }
}

// slack.list_channels
{
  "tool_name": "slack.list_channels",
  "parameters": {
    "exclude_archived": true
  }
}
```

### Google Calendar Tools
```json
// google_calendar.create_event
{
  "tool_name": "google_calendar.create_event",
  "parameters": {
    "title": "Project Review",
    "start_time": "2024-01-15T14:00:00-08:00",
    "end_time": "2024-01-15T15:00:00-08:00",
    "attendees": ["alice@company.com", "bob@company.com"]
  }
}

// google_calendar.list_events
{
  "tool_name": "google_calendar.list_events",
  "parameters": {
    "calendar_id": "primary",
    "max_results": 5
  }
}
```

### Google Tasks Tools
```json
// google_tasks.create_task
{
  "tool_name": "google_tasks.create_task",
  "parameters": {
    "tasklist_id": "sample_list_1",
    "title": "Complete project documentation",
    "notes": "Include API examples and setup guide",
    "due_date": "2024-01-20"
  }
}

// google_tasks.list_tasks
{
  "tool_name": "google_tasks.list_tasks",
  "parameters": {
    "tasklist_id": "sample_list_1"
  }
}
```

## Architecture

### Core Components

- **`main.py`**: FastAPI application with endpoints and middleware
- **`registry.py`**: Connector base class and dynamic loading system
- **`auth/store.py`**: In-memory authentication store with database TODOs

### Connector Structure

Each connector consists of:
- **`manifest.json`**: Tool definitions and metadata
- **`connector.py`**: Implementation class inheriting from `Connector`

### Tool Routing

The system supports both:
- **Namespaced calls**: `slack.send_message` (explicit connector)
- **Generic calls**: `send_message` (router finds best match)

## Development Notes

### Current Status
- ✅ Core FastAPI backend with dynamic registry
- ✅ Three example connectors with stub implementations
- ✅ Shared secret authentication
- ✅ Comprehensive API documentation

### TODO Items
- 🔄 Implement OAuth2 flows for Google and Slack
- 🔄 Replace in-memory auth store with database
- 🔄 Add comprehensive error handling and logging
- 🔄 Implement connector health checks
- 🔄 Add rate limiting and request validation

### Security Notes
- All POST endpoints require `X-Auth` header with `SHARED_SECRET`
- Auth store contains TODOs for proper password hashing and encryption
- OAuth credentials should be properly secured in production

## License

This project is part of the CoreAssist Voice Agent system.