# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [4.1.4] - 2026-06-25

### Changed
- Complete rewrite: Now uses REST API endpoints instead of MCP SSE transport
- Simplified dependencies: Removed MCP SDK dependency, now only requires `httpx`
- Updated to match hosted server API at `https://mcp.mirror.glasslane.io`

### Added
- `list_skills()` - List all 46+ available skills
- `get_skills_by_category()` - Filter skills by category
- `search_skills()` - Search skills by name/title/description/tags
- `generate_prompt()` - Generate prompts from skill templates
- `get_key_permissions()` - Check API key permissions
- New CLI commands: `search`, `skill`, `categories`, `permissions`, `generate`

### Removed
- MCP SSE transport (server requires Bearer auth via REST)
- Async context manager pattern (still supports async methods)
- `call_tool()` execution (returns metadata only until REST endpoint available)

## [4.1.3] - 2026-06-25

### Changed
- Republished as client SDK (not server)
- Updated documentation

## [4.1.2] - 2026-06-25

### Changed
- Documentation URL fix

## [4.1.0] - 2026-06-25

### Initial Release
- Client SDK for Mirror AI MCP Server
- Support for 46+ crypto intelligence tools
- Synchronous and asynchronous APIs
