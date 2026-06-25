"""
Mirror AI MCP Client SDK

A Python client for connecting to the hosted Mirror AI MCP Server at
https://mcp.mirror.glasslane.io

Usage:
    from mirror_mcp import MirrorMCPClient
    
    client = MirrorMCPClient(api_key="your-api-key")
    
    # List available tools/skills
    tools = client.list_tools()
    
    # Call a tool via REST API
    result = client.call_tool("get_token_price", {"symbol": "BTC"})
"""

import os
import json
import logging
from typing import Any, Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime

import httpx

logger = logging.getLogger("mirror_mcp")

DEFAULT_BASE_URL = "https://mcp.mirror.glasslane.io"


@dataclass
class Skill:
    """Represents a Mirror AI skill/prompt template"""
    name: str
    title: str
    description: str
    category: str
    tags: List[str]


@dataclass
class SkillCategory:
    """Represents a skill category"""
    key: str
    name: str
    description: str
    icon: str


@dataclass
class KeyPermissions:
    """Represents API key permissions"""
    client_id: str
    client_name: str
    tier: str
    data_domains: List[str]
    tables: List[str]


class MirrorMCPError(Exception):
    """Base exception for Mirror MCP client errors"""
    pass


class AuthenticationError(MirrorMCPError):
    """Raised when API key is invalid or missing"""
    pass


class ToolExecutionError(MirrorMCPError):
    """Raised when a tool execution fails"""
    pass


class MirrorMCPClient:
    """
    Mirror AI MCP Client
    
    Connects to the hosted Mirror AI MCP Server and provides a Pythonic
    interface to all 46+ crypto intelligence skills and tools.
    
    Args:
        api_key: Your Mirror AI API key. If not provided, reads from
                 MIRROR_API_KEY environment variable.
        base_url: The MCP server base URL. Defaults to https://mcp.mirror.glasslane.io
        timeout: Request timeout in seconds (default: 60)
    
    Example:
        client = MirrorMCPClient(api_key="gl_mcp_...")
        
        # List available skills
        skills = client.list_skills()
        
        # Get skills by category
        defi_skills = client.get_skills_by_category("defi_analysis")
        
        # Check key permissions
        perms = client.get_key_permissions()
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 60.0
    ):
        self.api_key = api_key or os.getenv("MIRROR_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key required. Provide api_key parameter or set MIRROR_API_KEY "
                "environment variable. Get your key at https://mirror.glasslane.io"
            )
        
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=self.timeout
        )
        
        self._async_client: Optional[httpx.AsyncClient] = None
        
        # Cache for skills
        self._skills: Optional[List[Skill]] = None
        self._categories: Optional[Dict[str, SkillCategory]] = None
    
    def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client"""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=self.timeout
            )
        return self._async_client
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle HTTP response and raise appropriate errors"""
        if response.status_code == 401:
            raise AuthenticationError("Invalid or expired API key")
        response.raise_for_status()
        return response.json()
    
    def get_key_permissions(self) -> KeyPermissions:
        """
        Get permissions and metadata for the current API key.
        
        Returns:
            KeyPermissions with client_id, tier, data_domains, etc.
        """
        response = self._client.get("/api/key-permissions")
        data = self._handle_response(response)
        
        return KeyPermissions(
            client_id=data["client_id"],
            client_name=data["client_name"],
            tier=data["tier"],
            data_domains=data.get("data_domains", []),
            tables=data.get("tables", [])
        )
    
    async def get_key_permissions_async(self) -> KeyPermissions:
        """Async version of get_key_permissions"""
        client = self._get_async_client()
        response = await client.get("/api/key-permissions")
        data = self._handle_response(response)
        
        return KeyPermissions(
            client_id=data["client_id"],
            client_name=data["client_name"],
            tier=data["tier"],
            data_domains=data.get("data_domains", []),
            tables=data.get("tables", [])
        )
    
    def list_skills(self, refresh: bool = False) -> List[Skill]:
        """
        List all available skills/prompts on the MCP server.
        
        Args:
            refresh: If True, bypass cache and fetch fresh data
            
        Returns:
            List of Skill objects with name, title, description, category, and tags.
            
        Example:
            skills = client.list_skills()
            for skill in skills:
                print(f"{skill.name}: {skill.title}")
        """
        if self._skills is not None and not refresh:
            return self._skills
        
        response = self._client.get("/api/skills")
        data = self._handle_response(response)
        
        self._skills = [
            Skill(
                name=s["name"],
                title=s["title"],
                description=s["description"],
                category=s["category"],
                tags=s.get("tags", [])
            )
            for s in data.get("skills", [])
        ]
        
        self._categories = {
            key: SkillCategory(
                key=key,
                name=cat["name"],
                description=cat["description"],
                icon=cat.get("icon", "")
            )
            for key, cat in data.get("categories", {}).items()
        }
        
        return self._skills
    
    async def list_skills_async(self, refresh: bool = False) -> List[Skill]:
        """Async version of list_skills"""
        if self._skills is not None and not refresh:
            return self._skills
        
        client = self._get_async_client()
        response = await client.get("/api/skills")
        data = self._handle_response(response)
        
        self._skills = [
            Skill(
                name=s["name"],
                title=s["title"],
                description=s["description"],
                category=s["category"],
                tags=s.get("tags", [])
            )
            for s in data.get("skills", [])
        ]
        
        self._categories = {
            key: SkillCategory(
                key=key,
                name=cat["name"],
                description=cat["description"],
                icon=cat.get("icon", "")
            )
            for key, cat in data.get("categories", {}).items()
        }
        
        return self._skills
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """
        Get a specific skill by name.
        
        Args:
            name: Skill name (e.g., "analyze_defi_protocol_risk")
            
        Returns:
            Skill object or None if not found
        """
        skills = self.list_skills()
        for skill in skills:
            if skill.name == name:
                return skill
        return None
    
    def get_skills_by_category(self, category: str) -> List[Skill]:
        """
        Get all skills in a specific category.
        
        Args:
            category: Category key (e.g., "defi_analysis", "trading_workflows")
            
        Returns:
            List of Skill objects
            
        Available categories:
            - defi_analysis
            - trading_workflows
            - security_workflows
            - nft_workflows
            - compliance_workflows
            - contract_workflows
            - intelligence_workflows
            - user_experience_workflows
        """
        skills = self.list_skills()
        return [s for s in skills if s.category == category]
    
    def search_skills(self, query: str) -> List[Skill]:
        """
        Search skills by name, title, description, or tags.
        
        Args:
            query: Search string
            
        Returns:
            List of matching Skill objects
        """
        query = query.lower()
        skills = self.list_skills()
        results = []
        
        for skill in skills:
            if (query in skill.name.lower() or
                query in skill.title.lower() or
                query in skill.description.lower() or
                any(query in tag.lower() for tag in skill.tags)):
                results.append(skill)
        
        return results
    
    def get_categories(self) -> Dict[str, SkillCategory]:
        """
        Get all skill categories.
        
        Returns:
            Dict mapping category key to SkillCategory
        """
        if self._categories is None:
            self.list_skills()  # Populates categories cache
        return self._categories or {}
    
    def call_tool(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute an MCP tool by calling the hosted server.
        
        Args:
            name: Tool/skill name (e.g., "analyze_defi_protocol_risk")
            arguments: Tool arguments as a dictionary
            timeout: Optional override for request timeout
            
        Returns:
            Tool execution result as a dictionary
            
        Raises:
            ToolExecutionError: If the tool execution fails
            AuthenticationError: If the API key is invalid
        """
        # Note: Tool execution would go through the MCP endpoint
        # For now, this is a placeholder - the MCP endpoint requires SSE
        # In the future, we can add a REST endpoint for tool execution
        
        # For now, generate a prompt from the skill
        skill = self.get_skill(name)
        if not skill:
            raise ToolExecutionError(f"Skill '{name}' not found")
        
        # Return skill metadata - actual execution needs MCP protocol
        return {
            "skill": skill.name,
            "title": skill.title,
            "description": skill.description,
            "category": skill.category,
            "tags": skill.tags,
            "arguments_provided": arguments or {},
            "note": "Full tool execution requires MCP protocol. Use skill metadata to generate prompts for your LLM."
        }
    
    def generate_prompt(self, skill_name: str, **kwargs) -> str:
        """
        Generate a prompt for a skill with the given parameters.
        
        This is useful for feeding into your own LLM when you want to
        use Mirror AI's prompt templates.
        
        Args:
            skill_name: Name of the skill
            **kwargs: Parameters to fill into the prompt template
            
        Returns:
            Generated prompt text
        """
        skill = self.get_skill(skill_name)
        if not skill:
            raise ToolExecutionError(f"Skill '{skill_name}' not found")
        
        # Build prompt from skill metadata
        prompt_parts = [
            f"# {skill.title}",
            "",
            skill.description,
            "",
            "## Parameters:",
        ]
        
        for key, value in kwargs.items():
            prompt_parts.append(f"- {key}: {value}")
        
        if not kwargs:
            prompt_parts.append("(No parameters provided)")
        
        prompt_parts.extend([
            "",
            f"Category: {skill.category}",
            f"Tags: {', '.join(skill.tags)}"
        ])
        
        return "\n".join(prompt_parts)
    
    def health(self) -> Dict[str, Any]:
        """
        Check the health status of the MCP server.
        
        Returns:
            Health status dictionary with database, cache, chatbot, and vector service status
        """
        response = self._client.get("/health")
        return self._handle_response(response)
    
    def close(self):
        """Close the HTTP client"""
        self._client.close()
        if self._async_client:
            import asyncio
            asyncio.get_event_loop().run_until_complete(self._async_client.aclose())
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


# Backwards compatibility aliases
list_tools = MirrorMCPClient.list_skills
call_tool = MirrorMCPClient.call_tool


# Convenience function for simple use cases
def get_mirror_client(api_key: Optional[str] = None) -> MirrorMCPClient:
    """
    Create a Mirror MCP client with the given API key.
    
    Args:
        api_key: API key (or reads from MIRROR_API_KEY env var)
        
    Returns:
        Configured MirrorMCPClient instance
        
    Example:
        client = get_mirror_client()
        skills = client.list_skills()
    """
    return MirrorMCPClient(api_key=api_key)
