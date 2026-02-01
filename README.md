# 🔍 mcp-code-indexer

### **Your AI Coding Assistant's Semantic Memory for Codebases**

[![PyPI Version](https://img.shields.io/pypi/v/mcp-code-indexer)](https://pypi.org/project/mcp-code-indexer/)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/groxaxo/mcp-code-indexer)](https://github.com/groxaxo/mcp-code-indexer)
[![Downloads](https://img.shields.io/pypi/dm/mcp-code-indexer)](https://pypi.org/project/mcp-code-indexer/)

**Transform your AI coding assistant into a codebase expert** with local-first semantic indexing. mcp-code-indexer is an MCP server that gives Claude, Cursor, and Windsurf deep understanding of your entire codebase through hybrid search, callgraph analysis, and git-aware indexing.

> ⚡ **Zero cloud dependencies** • 🔒 **Code never leaves your machine** • 🧠 **Semantic + keyword hybrid search**

## 🚀 Why mcp-code-indexer?

Tired of AI assistants guessing about your codebase? mcp-code-indexer gives them **perfect memory**:

| Without mcp-code-indexer | With mcp-code-indexer |
|--------------------------|----------------------|
| ❌ "Where's the auth middleware?" | ✅ **"Found auth middleware in `src/auth.py:42-78`"** |
| ❌ "What calls this function?" | ✅ **"`process_user()` is called by 3 functions across 2 files"** |
| ❌ "What changed in commit abc123?" | ✅ **"Commit abc123 added user validation in `models/user.py`"** |
| ❌ Manual file navigation | ✅ **Semantic search across entire codebase** |

## ✨ Core Features

### 🔍 **Hybrid Semantic Search**
- **Vector embeddings** + **BM25 keyword matching** = Best of both worlds
- **Cross-encoder reranking** for precision results (optional)
- **Multi-modal queries**: "Find authentication middleware" or "search for database connection code"

### 🧠 **Deep Code Understanding**
- **Python AST analysis** - Function/class boundaries with semantic chunking
- **Callgraph visualization** - See function relationships (depth configurable)
- **Symbol references** - Find all usages of classes, functions, variables
- **Git-aware indexing** - Query specific commits or working tree changes

### ⚡ **Performance & Security**
- **Incremental indexing** - Only reindex changed files (hash-based)
- **Local-first architecture** - Your code never leaves your machine
- **Security allowlist** - Whitelist specific repository roots only
- **Fast embeddings** - ONNX-based with optional GPU acceleration

## 🚀 Get Started in 60 Seconds

### 1️⃣ **Start Qdrant (Vector Database)**
```bash
docker compose up -d
```
> Qdrant runs locally in Docker - no cloud services required

### 2️⃣ **Install mcp-code-indexer**
```bash
# Install from PyPI (recommended)
pip install mcp-code-indexer

# Or install latest from GitHub
pip install git+https://github.com/groxaxo/mcp-code-indexer.git

# Optional: GPU acceleration for embeddings
pip install fastembed-gpu
```

### 3️⃣ **Configure Your Codebases**
```bash
# Allow specific directories (colon-separated)
export MCP_ALLOWED_ROOTS="$HOME/projects:$HOME/work:$HOME/code"

# Or allow current directory only
export MCP_ALLOWED_ROOTS="$(pwd)"
```

### 4️⃣ **Launch & Connect**
```bash
# Start the MCP server
python -m mcp_code_indexer
```

Now connect to your favorite AI coding assistant:

## 🤖 **AI Assistant Integration**

### **Claude Desktop** (Linux/macOS)
Edit `~/.config/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "code-indexer": {
      "command": "python",
      "args": ["-m", "mcp_code_indexer"],
      "env": {
        "MCP_ALLOWED_ROOTS": "/absolute/path/to/your/code"
      }
    }
  }
}
```

### **Cursor IDE**
Add to your MCP settings:
```json
{
  "mcpServers": {
    "code-indexer": {
      "command": "python",
      "args": ["-m", "mcp_code_indexer"],
      "env": {
        "MCP_ALLOWED_ROOTS": "/Users/you/projects"
      }
    }
  }
}
```

### **Windsurf / Continue**
Configure in your IDE's MCP settings with similar JSON structure.

> **💡 Pro Tip**: Restart your AI assistant after configuration changes!

## 🎯 **See It in Action**

### **Index Your Codebase**
```python
# Initialize indexing for a repository
index_init(repo_root="/home/you/projects/awesome-app")

# Incremental refresh (only changed files)
index_refresh(repo_root="/home/you/projects/awesome-app")
```

### **🔍 Semantic Code Search**
```python
# Hybrid search: "Find authentication middleware"
results = codebase_search(
    query="authentication middleware",
    repo_root="/home/you/projects/awesome-app",
    top_k=10,
    mode="hybrid"  # semantic + keyword
)

# Returns: [{file: "src/auth.py", lines: "42-78", content: "...", score: 0.92}]
```

### **🧭 Navigate Code Relationships**
```python
# Find all usages of a class
symbol_find(
    repo_root="/home/you/projects/awesome-app",
    name="UserModel",
    language="python"
)

# Visualize function call relationships
callgraph(
    repo_root="/home/you/projects/awesome-app",
    symbol_id="process_user_abc123",
    depth=3,
    direction="both"  # incoming & outgoing calls
)

# Get symbol references across codebase
symbol_references(
    repo_root="/home/you/projects/awesome-app",
    symbol_name="Database",
    limit=20
)
```

### **📸 Git-Aware Queries**
```python
# Search specific git commit
codebase_search(
    query="user validation",
    repo_root="/home/you/projects/awesome-app",
    git_commit="abc123def"
)

# List all indexed snapshots
git_list_snapshots(repo_root="/home/you/projects/awesome-app")
```

### **📄 Fetch Code Snippets**
```python
# Get specific file sections
codebase_fetch(
    repo_root="/home/you/projects/awesome-app",
    file_path="src/auth.py",
    start_line=10,
    end_line=50
)
```


## ⚙️ **Advanced Configuration**

### **Search Modes & Reranking**
```python
# Choose your search strategy
codebase_search(..., mode="hybrid")      # Default: semantic + keyword
codebase_search(..., mode="semantic")    # Pure vector similarity
codebase_search(..., mode="lexical")     # Pure keyword (BM25)

# Advanced: Cross-encoder reranking for precision
pip install sentence-transformers
codebase_search(..., use_rerank=True)    # Re-rank results for accuracy
```

### **Python AST Analysis**
- **Smart chunking**: Functions/classes as semantic units (not arbitrary lines)
- **Symbol resolution**: Track imports, class inheritance, function calls
- **Reference tracking**: Find where symbols are used across files

### **Git Integration**
- **Commit-aware indexing**: Each `index_init` stores current git commit
- **Multi-version querying**: Search code as it existed at any commit
- **Working tree support**: Index uncommitted changes separately

### **Performance Tuning**
```bash
# Environment variables for optimization
export MCP_EMBEDDER="fastembed"          # Default embedding model
export MCP_CHUNK_SIZE=1000               # Characters per chunk
export MCP_OVERLAP=200                   # Chunk overlap for context
```

## 🏗️ **Architecture**

### **Local-First Design**
```
┌─────────────────┐    ┌─────────────────────┐    ┌─────────────┐
│   AI Assistant  │◄──►│  mcp-code-indexer   │◄──►│   Qdrant    │
│  (Claude/Cursor)│    │    MCP Server       │    │ (Vector DB) │
└─────────────────┘    └─────────────────────┘    └─────────────┘
        │                          │
        │ MCP Protocol             │ Local Network
        ▼                          ▼
┌─────────────────┐        ┌─────────────┐
│  Your Codebase  │        │   SQLite    │
│   (Local Files) │        │ (Metadata)  │
└─────────────────┘        └─────────────┘
```

### **Key Design Principles**
1. **🔒 Privacy First**: Code never leaves your machine
2. **⚡ Performance**: Incremental indexing, fast embeddings
3. **🧠 Intelligence**: AST analysis + semantic search
4. **📈 Scalable**: Handles large codebases efficiently

## 🚧 **Roadmap & Future**

### **Coming Soon** 🚀
- [ ] **Multi-language support** (JavaScript/TypeScript, Go, Rust via tree-sitter)
- [ ] **Enhanced callgraphs** for complex codebases
- [ ] **Web UI dashboard** for visualization and management
- [ ] **Batch indexing** for large monorepos
- [ ] **Plugin system** for custom embedders and analyzers
- [ ] **Real-time indexing** with file watchers

### **Community Ideas** 💡
Have a feature request? [Open an issue](https://github.com/groxaxo/mcp-code-indexer/issues) or join the discussion!

## 🤝 **Contributing**

We love contributions! Here's how you can help:

1. **Report bugs** 🐛 - [Open an issue](https://github.com/groxaxo/mcp-code-indexer/issues)
2. **Suggest features** 💡 - Share your ideas
3. **Submit PRs** 🔧 - Fix bugs or add features
4. **Improve docs** 📚 - Help others get started
5. **Share feedback** 🗣️ - Tell us what works and what doesn't

### **Development & Testing**

#### **Setup Testing Environment**
```bash
# Method 1: Using conda (recommended)
./setup_test_env.sh

# Method 2: Manual setup
conda create -n mcp-test python=3.10 -y
conda activate mcp-test
pip install -e .
pip install pytest pytest-asyncio pytest-cov pytest-mock
```

#### **Running Tests**
```bash
# Run all tests
python -m pytest tests/ -v

# Run unit tests only
python -m pytest tests/unit/ -v

# Run integration tests only
python -m pytest tests/integration/ -v

# Run with coverage report
python -m pytest tests/ --cov=mcp_code_indexer --cov-report=html

# Run simple test runner (no pytest dependencies)
python simple_test.py
```

#### **Development Setup**
```bash
# Clone the repository
git clone https://github.com/groxaxo/mcp-code-indexer.git
cd mcp-code-indexer

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
ruff format .
```

## 📄 **License**

MIT License - see [LICENSE](LICENSE) for details.

---

## ⭐ **Support the Project**

If mcp-code-indexer makes your AI coding assistant smarter:
- **Star the repo** ⭐ on [GitHub](https://github.com/groxaxo/mcp-code-indexer)
- **Share with colleagues** who use AI coding tools
- **Contribute** to make it better for everyone

**Happy coding with your AI assistant!** 🚀
