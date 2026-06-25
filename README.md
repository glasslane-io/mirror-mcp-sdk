# Mirror MCP SDK

Official Python SDK for the Mirror AI MCP Server — access 46+ crypto intelligence skills via REST API.

## Installation

```bash
pip install mirror-mcp
```

## Quick Start

```python
from mirror_mcp import MirrorMCPClient

# Create client (reads MIRROR_API_KEY from env if not provided)
client = MirrorMCPClient(api_key="gl_mcp_...")

# List all 46+ skills
skills = client.list_skills()
for skill in skills:
    print(f"{skill.name}: {skill.title}")

# Get skills by category
defi_skills = client.get_skills_by_category("defi_analysis")

# Search for skills
results = client.search_skills("risk")

# Generate a prompt from a skill
prompt = client.generate_prompt(
    "analyze_defi_protocol_risk",
    protocol="Aave"
)
print(prompt)
```

## Authentication

Get your API key from [mirror.glasslane.io](https://mirror.glasslane.io):

```bash
export MIRROR_API_KEY="your-api-key"
```

## CLI Usage

```bash
# Check server health
mirror-mcp health

# List all skills
mirror-mcp list-skills

# Show skill details
mirror-mcp skill analyze_defi_protocol_risk

# Generate a prompt
mirror-mcp generate analyze_defi_protocol_risk --param protocol=Aave
```

## Documentation

Full documentation: https://mirror.glasslane.io/docs

## License

MIT License - Glass Lane Pty Ltd
