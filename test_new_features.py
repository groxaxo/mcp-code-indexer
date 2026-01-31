#!/usr/bin/env python3
"""
Test the new features: callgraph, references, git snapshots.
"""

import os
import sys
from pathlib import Path

# Set environment variable before importing config
os.environ["MCP_ALLOWED_ROOTS"] = str(Path.cwd())

from mcp_code_indexer.config import load_config
from mcp_code_indexer.indexer import index_repo, workspace_id_for
from mcp_code_indexer.search import SearchEngine
from mcp_code_indexer.db import connect


def main():
    repo_root = Path.cwd()
    cfg = load_config()
    db_path = (cfg.data_dir / "metadata.db").resolve()
    print(f"Data dir: {cfg.data_dir}")
    print(f"DB path: {db_path}")

    # Index the repo (incremental)
    print("Indexing repo...")
    result = index_repo(
        cfg,
        repo_root,
        db_path,
        job_cb=lambda prog, p, t, msg: print(f"  {p}/{t} {msg}"),
    )
    print(f"Indexing result: {result}")

    wid = workspace_id_for(repo_root)
    conn = connect(db_path)

    # Get git ref (HEAD)
    from mcp_code_indexer.indexer import get_git_ref

    git_ref = get_git_ref(repo_root)
    print(f"Git ref: {git_ref}")

    # List snapshots
    rows = conn.execute(
        "SELECT git_ref, indexed_at FROM snapshots WHERE workspace_id=? ORDER BY indexed_at DESC LIMIT 5",
        (wid,),
    ).fetchall()
    print(f"Snapshots: {rows}")

    # Search engine
    engine = SearchEngine(cfg, db_path)

    # Test symbol references for a known Python symbol (e.g., "Analyzer")
    print("\nTesting symbol_references for 'Analyzer'...")
    refs = engine.py_symbol_references(repo_root, "Analyzer", git_ref=git_ref, limit=5)
    for r in refs:
        print(f"  {r['file_path']}:{r['line']}:{r['col']} {r['context']}")

    # Find a symbol id for callgraph (maybe "Analyzer")
    # Need to query py_symbols table
    cur = conn.execute(
        "SELECT symbol_id, qualname FROM py_symbols WHERE workspace_id=? AND git_ref=? AND symbol_name=? LIMIT 1",
        (wid, git_ref, "Analyzer"),
    )
    row = cur.fetchone()
    if row:
        symbol_id = row[0]
        print(f"\nFound symbol_id for Analyzer: {symbol_id}")
        # Callgraph out direction depth 1
        print("Testing callgraph (out) for Analyzer...")
        cg = engine.py_callgraph(
            repo_root, symbol_id, depth=1, direction="out", git_ref=git_ref
        )
        print(f"  Nodes: {len(cg['nodes'])}")
        print(f"  Edges: {len(cg['edges'])}")
        for edge in cg["edges"][:5]:
            print(f"    {edge['from']} -> {edge['to']}")
    else:
        print("\nAnalyzer symbol not found, trying another...")
        # Find any python symbol
        cur = conn.execute(
            "SELECT symbol_id, symbol_name, qualname FROM py_symbols WHERE workspace_id=? AND git_ref=? LIMIT 1",
            (wid, git_ref),
        )
        row = cur.fetchone()
        if row:
            symbol_id = row[0]
            print(f"Testing callgraph for {row[1]} ({row[2]})")
            cg = engine.py_callgraph(
                repo_root, symbol_id, depth=1, direction="out", git_ref=git_ref
            )
            print(f"  Nodes: {len(cg['nodes'])} edges: {len(cg['edges'])}")

    # Test git_list_snapshots via SQL
    print("\nSnapshot list:")
    rows = conn.execute(
        "SELECT git_ref, indexed_at FROM snapshots WHERE workspace_id=? ORDER BY indexed_at DESC",
        (wid,),
    ).fetchall()
    for r in rows:
        print(f"  {r[0]} - {r[1]}")

    # Test search with git_ref filter
    print("\nTesting codebase_search with git_ref filter...")
    # Use a simple query
    hits = engine.hybrid_search(
        repo_root, "def index_repo", top_k=3, filters={"git_ref": git_ref}
    )
    for h in hits:
        print(
            f"  {h['file_path']}:{h['start_line']}-{h['end_line']} score={h['score']:.3f}"
        )

    print("\nAll tests completed.")


if __name__ == "__main__":
    main()
