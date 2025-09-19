"""
Connector registry system for CoreAssist Voice Agent.

This module provides the base Connector class and the ConnectorRegistry
for managing and loading connectors dynamically.
"""

import json
import os
import importlib.util
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pathlib import Path


class Connector(ABC):
    """
    Base class for all connectors in the CoreAssist system.
    
    Each connector must implement the execute method and provide a manifest.json
    file in their directory containing tool definitions.
    """
    
    def __init__(self, connector_name: str):
        self.connector_name = connector_name
        self.manifest = self._load_manifest()
    
    def _load_manifest(self) -> Dict[str, Any]:
        """Load the manifest.json file for this connector."""
        connector_dir = Path(__file__).parent / "connectors" / self.connector_name
        manifest_path = connector_dir / "manifest.json"
        
        if not manifest_path.exists():
            raise FileNotFoundError(f"No manifest.json found for connector {self.connector_name}")
        
        with open(manifest_path, 'r') as f:
            return json.load(f)
    
    @abstractmethod
    async def execute(self, tool_name: str, parameters: Dict[str, Any], auth_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a tool with the given parameters.
        
        Args:
            tool_name: The name of the tool to execute (without namespace)
            parameters: Tool-specific parameters
            auth_data: Authentication data for the user (if needed)
            
        Returns:
            Dict containing the result of the tool execution
        """
        pass
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return the list of tools provided by this connector."""
        return self.manifest.get("tools", [])
    
    def get_namespaced_tools(self) -> List[Dict[str, Any]]:
        """Return tools with namespaced names (e.g., slack.send_message)."""
        tools = []
        for tool in self.get_tools():
            namespaced_tool = tool.copy()
            namespaced_tool["name"] = f"{self.connector_name}.{tool['name']}"
            tools.append(namespaced_tool)
        return tools


class ConnectorRegistry:
    """
    Registry for managing and loading connectors dynamically.
    
    This class automatically discovers connectors in the connectors directory
    and loads them for use by the FastAPI application.
    """
    
    def __init__(self):
        self.connectors: Dict[str, Connector] = {}
        self._load_connectors()
    
    def _load_connectors(self) -> None:
        """Automatically discover and load all connectors."""
        connectors_dir = Path(__file__).parent / "connectors"
        
        if not connectors_dir.exists():
            return
        
        for connector_path in connectors_dir.iterdir():
            if connector_path.is_dir() and not connector_path.name.startswith('_'):
                try:
                    self._load_connector(connector_path.name)
                except Exception as e:
                    print(f"Failed to load connector {connector_path.name}: {e}")
    
    def _load_connector(self, connector_name: str) -> None:
        """Load a specific connector by name."""
        connector_dir = Path(__file__).parent / "connectors" / connector_name
        connector_file = connector_dir / "connector.py"
        
        if not connector_file.exists():
            raise FileNotFoundError(f"No connector.py found for {connector_name}")
        
        # Load the module dynamically
        spec = importlib.util.spec_from_file_location(
            f"connectors.{connector_name}",
            connector_file
        )
        
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load connector module for {connector_name}")
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find the connector class (should be named after the connector)
        connector_class_name = "".join(word.capitalize() for word in connector_name.split('_')) + "Connector"
        
        if not hasattr(module, connector_class_name):
            raise AttributeError(f"No {connector_class_name} class found in {connector_name}")
        
        connector_class = getattr(module, connector_class_name)
        
        # Instantiate the connector
        connector_instance = connector_class(connector_name)
        self.connectors[connector_name] = connector_instance
        
        print(f"Loaded connector: {connector_name}")
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all tools from all connectors with both namespaced and original names."""
        all_tools = []
        
        for connector in self.connectors.values():
            # Add namespaced tools
            all_tools.extend(connector.get_namespaced_tools())
            # Also add original tools for backward compatibility
            all_tools.extend(connector.get_tools())
        
        return all_tools
    
    def get_connector_for_tool(self, tool_name: str) -> Optional[Connector]:
        """
        Get the connector that provides a specific tool.
        
        Supports both namespaced (e.g., 'slack.send_message') and 
        non-namespaced (e.g., 'send_message') tool names.
        """
        # Handle namespaced tools
        if '.' in tool_name:
            connector_name, actual_tool_name = tool_name.split('.', 1)
            if connector_name in self.connectors:
                connector = self.connectors[connector_name]
                # Verify the tool exists
                for tool in connector.get_tools():
                    if tool['name'] == actual_tool_name:
                        return connector
        else:
            # Handle non-namespaced tools - find the best match
            for connector in self.connectors.values():
                for tool in connector.get_tools():
                    if tool['name'] == tool_name:
                        return connector
        
        return None
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], auth_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a tool by name with the given parameters."""
        connector = self.get_connector_for_tool(tool_name)
        
        if not connector:
            raise ValueError(f"No connector found for tool: {tool_name}")
        
        # Extract the actual tool name (remove namespace if present)
        actual_tool_name = tool_name.split('.', 1)[-1] if '.' in tool_name else tool_name
        
        return await connector.execute(actual_tool_name, parameters, auth_data)
    
    def reload_connector(self, connector_name: str) -> None:
        """Reload a specific connector (useful for development)."""
        if connector_name in self.connectors:
            del self.connectors[connector_name]
        
        self._load_connector(connector_name)
    
    def list_connectors(self) -> List[str]:
        """Return a list of loaded connector names."""
        return list(self.connectors.keys())


# Global registry instance
registry = ConnectorRegistry()