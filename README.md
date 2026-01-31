# mcp-code-indexer (local semantic codebase indexing MCP server)

[![GitHub](https://img.shields.io/badge/GitHub-groxaxo/mcp--code--indexer-blue)](https://github.com/groxaxo/mcp-code-indexer)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

This is a **local** MCP server that indexes a codebase into **Qdrant + SQLite** and exposes tools like:
- `index_init`, `index_refresh`, `index_status`, `index_stats`
- `codebase_search`, `codebase_fetch`
- `symbol_find` (Python-only for now)

It’s designed to be:
- **Local-first** (no code leaves your machine unless you change the embedder)
- **Incremental** (hash-based reindexing)
- **Safe by default** (repo root allowlist + path normalization)

## What you need

- Python 3.10+
- Docker (recommended) to run Qdrant locally

## Quick start

### 1) Start Qdrant
```bash
docker compose up -d
```

### 2) Create a venv + install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

> Optional GPU embeddings (ONNX):  
> `pip install fastembed-gpu`

### 3) Allow your repo roots (important)
Set a colon-separated allowlist:
```bash
export MCP_ALLOWED_ROOTS="$HOME/projects:$HOME/code"
```

### 4) Run the MCP server (stdio)
```bash
python -m mcp_code_indexer
```

## Using it in an MCP host

### Claude Desktop example (Linux/macOS)
Edit your Claude config JSON and add:

```json
{
  "mcpServers": {
    "code-indexer": {
      "command": "bash",
      "args": ["-lc", "cd /ABS/PATH/mcp-code-indexer && source .venv/bin/activate && python -m mcp_code_indexer"]
    }
  }
}
```

## Tool examples

- Index a repo:
  - `index_init(repo_root="/home/you/projects/myrepo")`
- Search:
  - `codebase_search(query="where is auth handled?", repo_root="/home/you/projects/myrepo", top_k=8)`
- Fetch lines:
  - `codebase_fetch(repo_root="/home/you/projects/myrepo", file_path="src/auth.py", start_line=1, end_line=120)`

## Notes / Roadmap
- Current chunking:
  - Python: AST-based function/class chunks
  - Others: line-window chunks
- Next upgrades:
  - Tree-sitter multi-language chunking
  - Hybrid lexical (BM25) + rerank
  - Callgraph for more languages


## Hybrid search + rerank

- Default `codebase_search` mode is **hybrid** (semantic + BM25 keyword search).
- You can force a mode: `mode='semantic' | 'lexical' | 'hybrid'`.
- Hybrid weight: `alpha` (semantic weight; lexical = 1-alpha).

### Optional cross-encoder reranking

Install:
```bash
pip install sentence-transformers
```
Then call:
- `codebase_search(..., mode='hybrid', use_rerank=True)`



## Callgraph + references (Python)

- `symbol_references(repo_root, symbol_name, git_ref?, path_prefix?, limit?)`
- `callgraph(repo_root, symbol_id, depth=1, direction='out'|'in'|'both', git_ref?)`

This is **static, best-effort** and meant for navigation.


## Git snapshots

- Each index run stores the current `HEAD` commit as `git_ref` (or `working_tree`).
- Index data is kept **per git_ref**: vectors, BM25, symbols, callgraph.
- List snapshots: `git_list_snapshots(repo_root)`
- Query a snapshot: `codebase_search(..., filters={'git_ref': '<sha>'})`
