"""
CLI for mirror-mcp client

Usage:
    # Server health
    mirror-mcp health
    
    # List tools (100+ executable tools)
    mirror-mcp tools
    mirror-mcp tools --category market
    
    # Execute tools
    mirror-mcp call get_symbol_price '{"symbol": "BTC"}'
    mirror-mcp call get_current_market_data
    
    # Legacy skill commands (still work)
    mirror-mcp list-skills
    mirror-mcp list-skills --category defi
    mirror-mcp skill analyze_defi_protocol_risk
    mirror-mcp permissions
    
    # With explicit API key
    mirror-mcp --api-key gl_mcp_... tools

Get your API key at: https://mirror.glasslane.io
"""

import os
import sys
import json
import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("mirror-mcp")


def resolve_api_key(args) -> str:
    """Get API key from args or environment"""
    api_key = args.api_key or os.getenv("MIRROR_API_KEY")
    if not api_key:
        print("Error: API key required.", file=sys.stderr)
        print("Set MIRROR_API_KEY environment variable or use --api-key", file=sys.stderr)
        print("Get your key at: https://mirror.glasslane.io", file=sys.stderr)
        sys.exit(1)
    return api_key


def cmd_health(args):
    """Check server health"""
    import httpx
    
    url = args.base_url or os.getenv("MIRROR_BASE_URL", "https://mcp.mirror.glasslane.io")
    
    try:
        response = httpx.get(f"{url}/health", timeout=10)
        data = response.json()
        
        print(f"Server: {url}")
        print(f"Status: {data.get('status', 'unknown')}")
        print(f"Database: {data.get('database', {}).get('status', 'unknown')}")
        print(f"Cache: {data.get('cache', {}).get('status', 'unknown')}")
        print(f"Chatbot: {data.get('chatbot', {}).get('status', 'unknown')}")
        print(f"Vector DB: {data.get('vector', {}).get('status', 'unknown')}")
        
        if data.get('status') == 'healthy':
            print("\n✓ Server is healthy")
            return 0
        else:
            print("\n⚠ Server is degraded")
            return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_tools(args):
    """List available executable tools"""
    from mirror_mcp import MirrorMCPClient
    
    api_key = resolve_api_key(args)
    
    with MirrorMCPClient(api_key=api_key, base_url=args.base_url) as client:
        tools = client.list_tools()
        
        if args.category:
            tools = [t for t in tools if t.get("category") == args.category]
            print(f"Tools in category '{args.category}' ({len(tools)} total):\n")
        else:
            print(f"Available tools ({len(tools)} total):\n")
        
        # Group by category
        from collections import defaultdict
        by_category = defaultdict(list)
        for tool in tools:
            by_category[tool.get("category", "other")].append(tool)
        
        for category in sorted(by_category.keys()):
            cat_tools = by_category[category]
            print(f"\n{category.upper()} ({len(cat_tools)} tools):")
            for tool in cat_tools:
                desc = tool.get("description", "")[:60]
                if len(tool.get("description", "")) > 60:
                    desc += "..."
                print(f"  • {tool['name']}")
                print(f"    {desc}")


def cmd_call(args):
    """Execute any tool via REST API"""
    from mirror_mcp import MirrorMCPClient
    
    api_key = resolve_api_key(args)
    
    # Parse arguments
    try:
        if args.arguments:
            arguments = json.loads(args.arguments)
        else:
            arguments = {}
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON arguments - {e}", file=sys.stderr)
        sys.exit(1)
    
    with MirrorMCPClient(api_key=api_key, base_url=args.base_url) as client:
        try:
            result = client.execute_tool(args.tool_name, arguments)
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


# Legacy commands for backwards compatibility
def cmd_list_skills(args):
    """List available skills (legacy)"""
    from mirror_mcp import MirrorMCPClient
    
    api_key = resolve_api_key(args)
    
    with MirrorMCPClient(api_key=api_key, base_url=args.base_url) as client:
        if args.category:
            skills = client.get_skills_by_category(args.category)
            print(f"Skills in category '{args.category}' ({len(skills)} total):\n")
        else:
            skills = client.list_skills()
            print(f"Available skills ({len(skills)} total):\n")
        
        for skill in skills:
            print(f"  {skill.name}")
            print(f"    Title: {skill.title}")
            desc = skill.description
            if len(desc) > 80:
                desc = desc[:77] + "..."
            print(f"    {desc}")
            if skill.tags:
                print(f"    Tags: {', '.join(skill.tags[:5])}")
            print()


def cmd_skill(args):
    """Show skill details (legacy)"""
    from mirror_mcp import MirrorMCPClient
    
    api_key = resolve_api_key(args)
    
    with MirrorMCPClient(api_key=api_key, base_url=args.base_url) as client:
        skill = client.get_skill(args.skill_name)
        
        if not skill:
            print(f"Error: Skill '{args.skill_name}' not found", file=sys.stderr)
            sys.exit(1)
        
        print(f"Skill: {skill.name}")
        print(f"Title: {skill.title}")
        print(f"Category: {skill.category}")
        print(f"\nDescription:")
        print(f"  {skill.description}")
        print(f"\nTags: {', '.join(skill.tags)}")


def cmd_permissions(args):
    """Show API key permissions"""
    from mirror_mcp import MirrorMCPClient
    
    api_key = resolve_api_key(args)
    
    with MirrorMCPClient(api_key=api_key, base_url=args.base_url) as client:
        perms = client.get_key_permissions()
        
        print(f"API Key: {perms.client_id}")
        print(f"Client Name: {perms.client_name}")
        print(f"Tier: {perms.tier}")
        print(f"\nData Domains:")
        for domain in perms.data_domains:
            print(f"  • {domain}")
        print(f"\nTable Access: {', '.join(perms.tables) if perms.tables else 'None'}")


def main():
    parser = argparse.ArgumentParser(
        prog="mirror-mcp",
        description="Mirror AI MCP Client — Connect to 100+ crypto intelligence tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # New tool-based workflow
  mirror-mcp tools                              # List all 100+ tools
  mirror-mcp tools --category market            # List market data tools
  mirror-mcp call get_symbol_price '{"symbol": "BTC"}'  # Execute tool
  mirror-mcp call get_current_market_data       # Get all market data
  
  # Server status
  mirror-mcp health
  mirror-mcp permissions
  
  # Legacy skill workflow (still supported)
  mirror-mcp list-skills                        # List skills/prompts
  mirror-mcp list-skills --category defi        # Filter by category
  mirror-mcp skill analyze_defi_protocol_risk  # Show skill details

Tool Categories:
  market        - Prices, volume, technical indicators
  defi          - Protocols, yield, liquidity pools
  security      - Token security, contract analysis
  compliance    - Regulations, documents, risk
  analytics     - Correlation, momentum, volatility
  blockchain    - Wallet analysis, transactions
  arbitrage     - Cross-DEX arbitrage opportunities
  nft           - NFT collections, ownership, whales
  alerts        - Price alerts, market signals
  research      - Token research, whitepapers
        """
    )
    parser.add_argument(
        "--api-key",
        help="Mirror AI API key (or set MIRROR_API_KEY env var)",
    )
    parser.add_argument(
        "--base-url",
        default="https://mcp.mirror.glasslane.io",
        help="MCP server base URL (default: https://mcp.mirror.glasslane.io)",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Health command
    health_parser = subparsers.add_parser("health", help="Check server health")
    health_parser.set_defaults(func=cmd_health)
    
    # Tools command (new)
    tools_parser = subparsers.add_parser("tools", help="List executable tools")
    tools_parser.add_argument(
        "--category",
        help="Filter by category (e.g., market, defi, analytics)"
    )
    tools_parser.set_defaults(func=cmd_tools)
    
    # Call tool command (new)
    call_parser = subparsers.add_parser("call", help="Execute a tool via REST API")
    call_parser.add_argument("tool_name", help="Name of the tool to execute")
    call_parser.add_argument("arguments", nargs="?", help="JSON arguments for the tool")
    call_parser.set_defaults(func=cmd_call)
    
    # Legacy list-skills (kept for compatibility)
    list_parser = subparsers.add_parser("list-skills", help="List skills/prompts (legacy)")
    list_parser.add_argument(
        "--category",
        help="Filter by category"
    )
    list_parser.set_defaults(func=cmd_list_skills)
    
    # Legacy skill command (kept for compatibility)
    skill_parser = subparsers.add_parser("skill", help="Show skill details (legacy)")
    skill_parser.add_argument("skill_name", help="Name of the skill")
    skill_parser.set_defaults(func=cmd_skill)
    
    # Permissions command
    perm_parser = subparsers.add_parser("permissions", help="Show API key permissions")
    perm_parser.set_defaults(func=cmd_permissions)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
