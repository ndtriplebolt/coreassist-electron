"""
CoreAssist Voice Agent FastAPI Backend.

This is the main FastAPI application that provides:
- /tools/manifest: Dynamic tools manifest from all connectors
- /tools/call: Unified tool execution endpoint
- /health: Health check endpoint

All POST endpoints require X-Auth header with SHARED_SECRET.
"""

import os
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from registry import registry
from auth.store import auth_store


app = FastAPI(
    title="CoreAssist Voice Agent API",
    description="Dynamic tools manifest and unified tool router for voice agent with pluggable connectors",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response validation
class ToolCallRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to execute (supports namespaced names like 'slack.send_message')")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool-specific parameters")
    user_id: Optional[str] = Field(None, description="User ID for authentication context (optional)")


class ToolCallResponse(BaseModel):
    success: bool
    result: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    connectors_loaded: int
    total_tools: int
    auth_stats: Dict[str, int]


class ManifestResponse(BaseModel):
    tools: List[Dict[str, Any]]
    connectors: List[str]
    supports_namespaced_calls: bool = True


# Authentication dependency
async def verify_auth(x_auth: str = Header(None)):
    """
    Verify the X-Auth header contains the correct shared secret.
    Only applies to POST endpoints for security.
    """
    if not x_auth:
        raise HTTPException(
            status_code=401,
            detail="Missing X-Auth header"
        )
    
    if not auth_store.verify_shared_secret(x_auth):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication"
        )
    
    return True


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify the service is running and connectors are loaded.
    """
    try:
        # Clean up expired sessions
        auth_store.cleanup_expired_sessions()
        
        return HealthResponse(
            status="healthy",
            connectors_loaded=len(registry.list_connectors()),
            total_tools=len(registry.get_all_tools()),
            auth_stats=auth_store.get_stats()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )


@app.get("/tools/manifest", response_model=ManifestResponse)
async def get_tools_manifest():
    """
    Get the dynamic tools manifest from all loaded connectors.
    
    Returns all available tools with both namespaced (e.g., 'slack.send_message') 
    and original names for maximum compatibility.
    """
    try:
        all_tools = registry.get_all_tools()
        connectors = registry.list_connectors()
        
        return ManifestResponse(
            tools=all_tools,
            connectors=connectors,
            supports_namespaced_calls=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate manifest: {str(e)}"
        )


@app.post("/tools/call", response_model=ToolCallResponse, dependencies=[Depends(verify_auth)])
async def call_tool(request: ToolCallRequest):
    """
    Execute a tool call through the unified router.
    
    Supports both namespaced (e.g., 'slack.send_message') and generic tool names.
    For generic names, the router selects the best matching connector.
    
    Requires X-Auth header with SHARED_SECRET.
    """
    try:
        # Get user auth data if user_id is provided
        auth_data = None
        if request.user_id:
            user_data = auth_store.get_user(request.user_id)
            if user_data:
                # Get connector name from tool name
                connector_name = request.tool_name.split('.')[0] if '.' in request.tool_name else None
                if connector_name:
                    auth_data = auth_store.get_connector_credentials(request.user_id, connector_name)
        
        # Execute the tool
        result = await registry.execute_tool(
            tool_name=request.tool_name,
            parameters=request.parameters,
            auth_data=auth_data
        )
        
        return ToolCallResponse(
            success=True,
            result=result
        )
        
    except ValueError as e:
        return ToolCallResponse(
            success=False,
            error=f"Tool not found: {str(e)}"
        )
    except Exception as e:
        return ToolCallResponse(
            success=False,
            error=f"Tool execution failed: {str(e)}"
        )


@app.get("/connectors")
async def list_connectors():
    """List all loaded connectors and their status."""
    connectors_info = []
    
    for connector_name in registry.list_connectors():
        connector = registry.connectors[connector_name]
        tools = connector.get_tools()
        
        connectors_info.append({
            "name": connector_name,
            "tools_count": len(tools),
            "tools": [tool["name"] for tool in tools],
            "manifest": connector.manifest.get("info", {})
        })
    
    return {
        "connectors": connectors_info,
        "total_connectors": len(connectors_info)
    }


@app.post("/connectors/{connector_name}/reload", dependencies=[Depends(verify_auth)])
async def reload_connector(connector_name: str):
    """
    Reload a specific connector (useful for development).
    
    Requires X-Auth header with SHARED_SECRET.
    """
    try:
        registry.reload_connector(connector_name)
        return {"message": f"Connector {connector_name} reloaded successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reload connector {connector_name}: {str(e)}"
        )


# Development endpoints (remove in production)
@app.get("/dev/auth/stats")
async def get_auth_stats():
    """Development endpoint to view auth store statistics."""
    return auth_store.get_stats()


if __name__ == "__main__":
    # Check required environment variables
    required_env_vars = ["SHARED_SECRET"]
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set the following environment variables:")
        print("- SHARED_SECRET: Secret key for API authentication")
        print("- OPENAI_API_KEY: OpenAI API key (optional, for OpenAI-based connectors)")
        exit(1)
    
    print("Starting CoreAssist Voice Agent API...")
    print(f"Loaded connectors: {', '.join(registry.list_connectors())}")
    print(f"Total tools available: {len(registry.get_all_tools())}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )