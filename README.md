# Mirror MCP SDK

Official Python SDK for the Mirror AI MCP Server — access 100+ crypto intelligence tools via REST API.

## What's New in v4.1.8

✨ **Universal Tool Execution** — Execute any of 100+ MCP tools directly via REST API:

```python
# Get Bitcoin price
result = client.execute_tool("get_symbol_price", {"symbol": "BTC"})
print(result["result"][0]["price"])

# List all available tools
tools = client.list_tools()
for tool in tools:
    print(f"{tool['name']}: {tool['description']}")
```

## Installation

```bash
pip install mirror-mcp
```

## Quick Start

```python
from mirror_mcp import MirrorMCPClient

# Create client (reads MIRROR_API_KEY from env if not provided)
client = MirrorMCPClient(api_key="gl_mcp_...")

# List all 100+ executable tools
tools = client.list_tools()
for tool in tools:
    print(f"{tool['name']}: {tool['description']}")

# Execute any tool
result = client.execute_tool("get_symbol_price", {"symbol": "BTC"})
print(result["result"][0]["price"])

# Get market data
result = client.execute_tool("get_current_market_data", {"limit": 10})
for coin in result["result"]:
    print(f"{coin['symbol']}: ${coin['price']}")

# DeFi tools
result = client.execute_tool("query_defi_protocols", {"protocol": "Aave"})

# Security analysis
result = client.execute_tool("analyze_token_security", {"symbol": "ETH"})

# Compliance
result = client.execute_tool("compliance_search_documents", {"query": "MiCA"})
```

## Authentication

Get your API key from [mirror.glasslane.io](https://mirror.glasslane.io):

```bash
export MIRROR_API_KEY="your-api-key"
```

## Available Tool Categories

- **market** — Prices, volume, technical indicators, top movers
- **defi** — Protocols, yield farming, liquidity pools
- **security** — Token security, contract analysis
- **compliance** — Regulations, documents, risk assessment
- **analytics** — Price correlation, momentum, volatility
- **blockchain** — Wallet analysis, transaction patterns
- **arbitrage** — Cross-DEX arbitrage opportunities
- **nft** — NFT collections, ownership, whale tracking
- **alerts** — Price alerts, market signals
- **research** — Token research, whitepaper analysis

## CLI Usage

```bash
# Check server health
mirror-mcp health

# List all 100+ tools
mirror-mcp tools

# List tools by category
mirror-mcp tools --category market

# Execute any tool
mirror-mcp call get_symbol_price '{"symbol": "BTC"}'
mirror-mcp call get_current_market_data

# Show API key permissions
mirror-mcp permissions

# Legacy: list skills/prompts (still supported)
mirror-mcp list-skills
mirror-mcp list-skills --category defi
```

## Async Support

```python
import asyncio
from mirror_mcp import MirrorMCPClient

async def get_prices():
    async with MirrorMCPClient(api_key="...") as client:
        # List tools
        tools = await client.list_tools_async()
        
        # Execute multiple tools concurrently
        results = await asyncio.gather(
            client.execute_tool_async("get_symbol_price", {"symbol": "BTC"}),
            client.execute_tool_async("get_symbol_price", {"symbol": "ETH"}),
            client.execute_tool_async("get_symbol_price", {"symbol": "SOL"}),
        )
        return results

asyncio.run(get_prices())
```

## Error Handling

```python
from mirror_mcp import MirrorMCPClient, AuthenticationError, ToolExecutionError

try:
    client = MirrorMCPClient(api_key="your-key")
    result = client.execute_tool("get_symbol_price", {"symbol": "BTC"})
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except ToolExecutionError as e:
    print(f"Tool execution failed: {e}")
```

## Documentation

- **Mirror AI Platform**: https://mirror.glasslane.io
- **GitHub**: https://github.com/glasslane-io/mirror-mcp-sdk

## License

MIT License — Copyright © 2025 Glass Lane Pty Ltd
