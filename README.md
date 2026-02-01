# mcp-code-indexer (v0.4.0)

[![GitHub](https://img.shields.io/badge/GitHub-groxaxo/mcp--code--indexer-blue)](https://github.com/groxaxo/mcp-code-indexer)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![PyPI](https://img.shields.io/badge/pypi-v0.4.0-blue)](https://pypi.org/project/mcp-code-indexer/)

**Local semantic codebase indexing MCP server** with Qdrant + SQLite backend.

## ✨ Features

- **🔍 Semantic + BM25 hybrid search** - Combines vector embeddings with keyword matching
- **🧠 Python AST analysis** - Function/class chunking with callgraph and symbol references
- **📸 Git snapshot support** - Index and query different git commits
- **⚡ Incremental indexing** - Hash-based reindexing (only changed files)
- **🔒 Local-first** - No code leaves your machine (unless you change the embedder)
- **🛡️ Security-first** - Repo root allowlist + path normalization

## 🚀 Quick Start

### 1) Start Qdrant
```bash
docker compose up -d
```

### 2) Install from PyPI or GitHub
```bash
# From PyPI
pip install mcp-code-indexer

# Or from GitHub (latest)
pip install git+https://github.com/groxaxo/mcp-code-indexer.git

# Optional: GPU embeddings (ONNX)
pip install fastembed-gpu
```

### 3) Configure allowed repositories
```bash
export MCP_ALLOWED_ROOTS="$HOME/projects:$HOME/code"
```

### 4) Run the MCP server
```bash
python -m mcp_code_indexer
```

## 📋 MCP Host Integration

### Claude Desktop (Linux/macOS)
Edit your Claude config JSON (`~/.config/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "code-indexer": {
      "command": "python",
      "args": ["-m", "mcp_code_indexer"]
    }
  }
}
```

### Cursor / Windsurf
Add to your MCP configuration:

```json
{
  "mcpServers": {
    "code-indexer": {
      "command": "python",
      "args": ["-m", "mcp_code_indexer"],
      "env": {
        "MCP_ALLOWED_ROOTS": "/path/to/your/projects"
      }
    }
  }
}
```

## 🎯 Tool Examples

### Indexing
```python
index_init(repo_root="/home/you/projects/myrepo")
index_refresh(repo_root="/home/you/projects/myrepo", rel_paths=["src/main.py"])
```

### Search & Navigation
```python
# Hybrid search (semantic + keyword)
codebase_search(
    query="authentication middleware",
    repo_root="/home/you/projects/myrepo",
    top_k=10,
    mode="hybrid"
)

# Find Python symbols
symbol_find(
    repo_root="/home/you/projects/myrepo",
    name="User",
    language="python"
)

# Get symbol references
symbol_references(
    repo_root="/home/you/projects/myrepo",
    symbol_name="Database",
    limit=20
)

# Explore callgraph
callgraph(
    repo_root="/home/you/projects/myrepo",
    symbol_id="abc123...",
    depth=2,
    direction="out"
)

# List git snapshots
git_list_snapshots(repo_root="/home/you/projects/myrepo")
```

### File Access
```python
codebase_fetch(
    repo_root="/home/you/projects/myrepo",
    file_path="src/auth.py",
    start_line=10,
    end_line=50
)
```


## 🔧 Advanced Features

### Hybrid Search & Reranking
- **Default mode**: `hybrid` (semantic + BM25 keyword search)
- **Available modes**: `semantic` | `lexical` | `hybrid`
- **Hybrid weight**: `alpha` parameter (semantic weight; lexical = 1-alpha)

**Optional cross-encoder reranking**:
```bash
pip install sentence-transformers
```
```python
codebase_search(..., mode='hybrid', use_rerank=True)
```

### Python AST Analysis
- **Function/class chunking**: AST-based semantic boundaries
- **Symbol references**: Find usages of Python symbols across codebase
- **Callgraph analysis**: Static function call relationships (depth configurable)

### Git Snapshot Support
- **Per-commit indexing**: Each index run stores current `HEAD` commit
- **Snapshot querying**: Search specific git commits
- **Working tree support**: Index uncommitted changes as `working_tree`

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────┐    ┌─────────────┐
│   MCP Client    │◄──►│  MCP Server │◄──►│   Qdrant    │
│  (Claude, etc.) │    │ (Python)    │    │ (Vector DB) │
└─────────────────┘    └─────────────┘    └─────────────┘
                              │
                              ▼
                       ┌─────────────┐
                       │   SQLite    │
                       │ (Metadata)  │
                       └─────────────┘
```

## 📈 Roadmap
- [ ] Tree-sitter multi-language support
- [ ] Enhanced callgraph for more languages
- [ ] Web UI for visualization
- [ ] Batch indexing improvements
- [ ] Plugin system for custom embedders

## 🤝 Contributing
Contributions welcome! Please open issues or PRs on [GitHub](https://github.com/groxaxo/mcp-code-indexer).

## 📄 License
MIT License - see [LICENSE](LICENSE) file for details.
