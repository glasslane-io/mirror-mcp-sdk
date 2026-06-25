"""
mirror-mcp — Mirror AI MCP Client SDK

A Python client for connecting to the hosted Mirror AI MCP Server at
https://mcp.mirror.glasslane.io

Quick start:
    from mirror_mcp import MirrorMCPClient
    
    # Create client (reads MIRROR_API_KEY from env if not provided)
    client = MirrorMCPClient(api_key="gl_mcp_...")
    
    # List all 46+ skills
    skills = client.list_skills()
    
    # Get skills by category
    defi_skills = client.get_skills_by_category("defi_analysis")
    
    # Search for skills
    results = client.search_skills("risk")
    
    # Show skill details
    skill = client.get_skill("analyze_defi_protocol_risk")
    
    # Generate a prompt
    prompt = client.generate_prompt("analyze_defi_protocol_risk", protocol="Aave")

CLI Usage:
    export MIRROR_API_KEY="gl_mcp_..."
    mirror-mcp health
    mirror-mcp list-skills
    mirror-mcp skill analyze_defi_protocol_risk
    mirror-mcp permissions

Get your API key at: https://mirror.glasslane.io
"""

__version__ = "4.1.4"
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
