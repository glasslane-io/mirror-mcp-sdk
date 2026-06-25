"""
mirror-mcp — Mirror AI MCP Client SDK

A Python client for connecting to the hosted Mirror AI MCP Server at
https://mcp.mirror.glasslane.io

Quick start:
    from mirror_mcp import MirrorMCPClient
    
    # Create client (reads MIRROR_API_KEY from env if not provided)
    client = MirrorMCPClient(api_key="gl_mcp_...")
    
    # List all 100+ executable tools
    tools = client.list_tools()
    
    # Execute a tool via REST API
    result = client.execute_tool("get_symbol_price", {"symbol": "BTC"})
    price = result["result"][0]["price"]
    
    # List tools by category
    market_tools = client.get_tools_by_category("market")
    
    # Search for tools
    tools = [t for t in tools if "price" in t["name"]]

CLI Usage:
    export MIRROR_API_KEY="gl_mcp_..."
    mirror-mcp health
    mirror-mcp tools                    # List all tools
    mirror-mcp tools --category market  # List market tools
    mirror-mcp call get_symbol_price '{"symbol": "BTC"}'
    mirror-mcp permissions

Get your API key at: https://mirror.glasslane.io
"""

__version__ = "4.2.0"
__author__ = "Glass Lane Pty Ltd"
__email__ = "info@glasslane.io"

from .client import (
    MirrorMCPClient,
    MirrorMCPError,
    AuthenticationError,
    ToolExecutionError,
    Skill,
    SkillCategory,
    KeyPermissions,
    get_mirror_client,
)

__all__ = [
    "MirrorMCPClient",
    "MirrorMCPError",
    "AuthenticationError",
    "ToolExecutionError",
    "Skill",
    "SkillCategory",
    "KeyPermissions",
    "get_mirror_client",
]
