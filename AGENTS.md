---
title: cherry-mcp Agent Guidelines
author: Theo
version: 1.0
---

# cherry-mcp Agent Guidelines

This file provides guidelines for AI coding agents working on the cherry-mcp project.

## 1. Project Overview

- **Project**: cherry-mcp (MCP Server for Cherry Studio Knowledge Base)
- **Language**: Python 3.10+
- **Framework**: MCP SDK, httpx, numpy
- **Entry Point**: `main.py`

## 2. Commands

### Setup
```bash
# Create virtual environment
python -m venv venv

# Install dependencies
venv/Scripts/pip.exe install -r requirements.txt
```

### Run
```bash
# Run MCP server (stdio mode)
venv/Scripts/python.exe main.py

# Or with UTF-8 encoding for Chinese output
$env:PYTHONIOENCODING="utf-8"; .\venv\Scripts\python.exe main.py
```

### Test
```bash
# Run all tests
venv/Scripts/pytest.exe

# Run single test file
venv/Scripts/pytest.exe tests/test_knowledge.py

# Run single test
venv/Scripts/pytest.exe tests/test_knowledge.py::test_function_name

# Run with verbose output
venv/Scripts/pytest.exe -v

# Run async tests
venv/Scripts/pytest.exe -v asyncio_mode=auto
```

### Lint & Format (Optional)
```bash
# Type check with mypy
venv/Scripts/mypy.exe .

# Format with black
venv/Scripts/black.exe .

# Lint with ruff
venv/Scripts/ruff.exe check .
```

## 3. Code Style

### Imports
- Standard library first, then third-party, then local
- Use absolute imports from package root
```python
# Good
import asyncio
import httpx
from cherrymcp.knowledge import EmbeddingClient

# Avoid
from .config import get_kb_config
```

### Formatting
- Line length: 100 characters max
- Use 4 spaces for indentation (no tabs)
- Use Black formatting automatically

### Type Hints (Required)
- Always use type hints for function parameters and return types
- Use built-in types (str, int, list, dict) not typing module when possible
```python
# Good
def process_data(query: str, top_k: int = 5) -> list[dict]:
    ...

# Avoid
def process_data(query, top_k=5):
    ...
```

### Naming Conventions
| Type | Convention | Example |
|------|------------|---------|
| Files | snake_case | `embedding.py` |
| Classes | PascalCase | `EmbeddingClient` |
| Functions | snake_case | `list_knowledge_bases()` |
| Constants | UPPER_SNAKE | `DEFAULT_TIMEOUT` |
| Variables | snake_case | `config_path` |

### Docstrings
- Use Google-style docstrings
- Explain "why" not "what"
- Include Args, Returns, Raises sections for functions
```python
def embed_text(text: str) -> np.ndarray | None:
    """Convert text to embedding vector.
    
    Args:
        text: Input text to embed.
        
    Returns:
        Embedding vector as numpy array, or None on failure.
    """
```

### Error Handling
- Never use silent error handling (empty except)
- Always log or return meaningful error messages
- Use specific exception types when possible
```python
# Good
try:
    result = await client.request()
except httpx.HTTPError as e:
    logger.error(f"HTTP error: {e}")
    return None

# Bad
try:
    result = await client.request()
except:
    pass
```

## 4. Project Structure

```
cherrymcp/
├── main.py                 # Entry point (MCP stdio server)
├── requirements.txt        # Dependencies
├── config.json            # Doc reference only (not used in code)
├── .env                   # Runtime config (API keys, paths)
├── .env.example          # Environment template
│
├── cherrymcp/            # Main package
│   ├── __init__.py
│   │
│   ├── knowledge/        # Knowledge base module
│   │   ├── config.py    # Reads .env, provides get_kb_config()
│   │   ├── embedding.py # Embedding API client
│   │   ├── knowledge_base.py
│   │   └── vector_search.py
│   │
│   └── tools/           # MCP tools
│       ├── knowledge_tools.py
│       └── __init__.py
│
└── tests/               # Test directory
    └── test_*.py
```

## 5. Configuration

### Runtime Behavior
- Code reads configuration from `.env` via `cherrymcp/knowledge/config.py`
- `config.json` is documentation only, not used in code execution
- Environment variables: `CHERRYSTUDIO_KB_PATH`, `EMBEDDING_URL`, `EMBEDDING_API_KEY`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSION`

### OpenCode MCP Configuration
```json
{
  "cherry-mcp": {
    "search": {
      "default_top_k": 20,
      "default_threshold": 0.5,
      "max_fetch": 1000
    }
  }
}
```
Search parameters passed via MCP call, embedding config via `environment` field.

## 6. MCP Tools

### Tool Pattern
```python
Tool(
    name="tool_name",
    description="What it does",
    description_for_model="When to use it",
    inputSchema={
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "..."}
        },
        "required": ["param"]
    }
)
```

### Response Format
```python
from mcp.types import TextContent

# Success
return [TextContent(type="text", text="result...")]

# Error
return [TextContent(type="text", text="Error: ...")]
```

## 7. Testing Guidelines

- Test files: `tests/test_*.py`
- Use `pytest` and `pytest-asyncio`
- Mock external dependencies (HTTP calls, file I/O)
- Test async functions with `@pytest.mark.asyncio`

## 8. Important Notes

- **API Keys**: Never commit to git; use `.gitignore`
- **Embedding Config**: Must match Cherry Studio knowledge base settings (url, model, dimension)
- **Vector Dimension**: Must match knowledge base vector dimension or search returns nothing
- **Encoding**: Use `PYTHONIOENCODING=utf-8` for Chinese output
