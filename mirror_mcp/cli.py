"""
CLI for mirror-mcp client

Usage:
    mirror-mcp health                           # Check server health
    mirror-mcp list-skills                      # List all available skills
    mirror-mcp list-skills --category defi      # List DeFi skills
    mirror-mcp search risk                        # Search skills
    mirror-mcp skill analyze_defi_protocol_risk   # Show skill details
    mirror-mcp categories                         # List categories
    mirror-mcp permissions                      # Show key permissions
    
    mirror-mcp --api-key gl_mcp_... list-skills   # Use specific API key
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


def cmd_list_skills(args):
    """List available skills"""
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


def cmd_search(args):
    """Search for skills"""
    from mirror_mcp import MirrorMCPClient
    
    api_key = resolve_api_key(args)
    
    with MirrorMCPClient(api_key=api_key, base_url=args.base_url) as client:
        skills = client.search_skills(args.query)
        
        print(f"Search results for '{args.query}' ({len(skills)} matches):\n")
        
        for skill in skills:
            print(f"  {skill.name}")
            print(f"    Title: {skill.title}")
            print(f"    Category: {skill.category}")
            desc = skill.description
            if len(desc) > 80:
                desc = desc[:77] + "..."
            print(f"    {desc}")
            print()


def cmd_skill(args):
    """Show skill details"""
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


def cmd_categories(args):
    """List skill categories"""
    from mirror_mcp import MirrorMCPClient
    
    api_key = resolve_api_key(args)
    
    with MirrorMCPClient(api_key=api_key, base_url=args.base_url) as client:
        categories = client.get_categories()
        
        print(f"Skill categories ({len(categories)} total):\n")
        
        for key, cat in categories.items():
            print(f"  {cat.icon} {cat.name}")
            print(f"    Key: {key}")
            print(f"    {cat.description}")
            print()


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


def cmd_call(args):
    """Call a tool (placeholder - returns skill metadata)"""
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
            result = client.call_tool(args.tool_name, arguments)
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


def cmd_generate(args):
    """Generate a prompt from a skill"""
    from mirror_mcp import MirrorMCPClient
    
    api_key = resolve_api_key(args)
    
    # Parse parameters
    params = {}
    for param in args.param or []:
        if '=' in param:
            key, value = param.split('=', 1)
            params[key] = value
    
    with MirrorMCPClient(api_key=api_key, base_url=args.base_url) as client:
        try:
            prompt = client.generate_prompt(args.skill_name, **params)
            print(prompt)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="mirror-mcp",
        description="Mirror AI MCP Client — Connect to hosted crypto intelligence tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mirror-mcp health                              # Check server status
  mirror-mcp list-skills                         # List all skills
  mirror-mcp list-skills --category defi         # List DeFi skills
  mirror-mcp search "risk"                        # Search for risk-related skills
  mirror-mcp skill analyze_defi_protocol_risk    # Show skill details
  mirror-mcp generate analyze_defi_protocol_risk # Generate a prompt
  mirror-mcp permissions                          # Show your API key permissions
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
    
    # List skills command
    list_parser = subparsers.add_parser("list-skills", help="List available skills")
    list_parser.add_argument(
        "--category",
        help="Filter by category (e.g., defi_analysis, trading_workflows)"
    )
    list_parser.set_defaults(func=cmd_list_skills)
    
    # Backwards compatibility: list-tools
    list_tools_parser = subparsers.add_parser("list-tools", help="Alias for list-skills")
    list_tools_parser.add_argument(
        "--category",
        help="Filter by category"
    )
    list_tools_parser.set_defaults(func=cmd_list_skills)
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for skills")
    search_parser.add_argument("query", help="Search query")
    search_parser.set_defaults(func=cmd_search)
    
    # Skill details command
    skill_parser = subparsers.add_parser("skill", help="Show skill details")
    skill_parser.add_argument("skill_name", help="Name of the skill")
    skill_parser.set_defaults(func=cmd_skill)
    
    # Categories command
    cat_parser = subparsers.add_parser("categories", help="List skill categories")
    cat_parser.set_defaults(func=cmd_categories)
    
    # Permissions command
    perm_parser = subparsers.add_parser("permissions", help="Show API key permissions")
    perm_parser.set_defaults(func=cmd_permissions)
    
    # Call tool command
    call_parser = subparsers.add_parser("call", help="Call a tool (returns metadata)")
    call_parser.add_argument("tool_name", help="Name of the tool to call")
    call_parser.add_argument("arguments", nargs="?", help="JSON arguments for the tool")
    call_parser.set_defaults(func=cmd_call)
    
    # Generate prompt command
    gen_parser = subparsers.add_parser("generate", help="Generate a prompt from a skill")
    gen_parser.add_argument("skill_name", help="Name of the skill")
    gen_parser.add_argument("--param", action="append", help="Add parameter (key=value)")
    gen_parser.set_defaults(func=cmd_generate)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
