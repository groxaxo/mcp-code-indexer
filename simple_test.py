#!/usr/bin/env python3
"""Simple tests for mcp-code-indexer without pytest dependencies."""

import sys
import os
import tempfile
import hashlib
from pathlib import Path
from unittest.mock import Mock, patch

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_config():
    """Test configuration module."""
    print("Testing config module...")

    from mcp_code_indexer.config import Config, load_config

    # Test Config creation
    config = Config(
        allowed_roots=[Path("/test/path")],
        data_dir=Path("/tmp/data"),
        qdrant_host="localhost",
        qdrant_port=6333,
        qdrant_collection="test_collection",
        max_chunk_chars=8000,
        max_fallback_lines=220,
        fallback_overlap_lines=40,
    )

    assert config.allowed_roots == [Path("/test/path")]
    assert config.qdrant_host == "localhost"
    print("✓ Config creation test passed")

    # Test load_config with environment variables
    with patch.dict(
        os.environ,
        {
            "MCP_ALLOWED_ROOTS": "/custom/path",
            "QDRANT_HOST": "custom-host",
            "QDRANT_PORT": "9999",
        },
        clear=True,
    ):
        config = load_config()

        assert len(config.allowed_roots) == 1
        assert config.qdrant_host == "custom-host"
        assert config.qdrant_port == 9999
        print("✓ Config loading with env vars test passed")

    print("All config tests passed!\n")


def test_hashing():
    """Test hashing module."""
    print("Testing hashing module...")

    from mcp_code_indexer.hashing import sha256_bytes, sha256_text, sha256_file

    # Test sha256_bytes
    test_data = b"Hello, World!"
    expected = hashlib.sha256(test_data).hexdigest()
    result = sha256_bytes(test_data)
    assert result == expected
    print("✓ sha256_bytes test passed")

    # Test sha256_text
    test_text = "Hello, World!"
    expected = hashlib.sha256(test_text.encode("utf-8")).hexdigest()
    result = sha256_text(test_text)
    assert result == expected
    print("✓ sha256_text test passed")

    # Test sha256_file
    with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
        f.write(b"Test file content")
        temp_file = f.name

    try:
        expected = hashlib.sha256(b"Test file content").hexdigest()
        result = sha256_file(Path(temp_file))
        assert result == expected
        print("✓ sha256_file test passed")
    finally:
        os.unlink(temp_file)

    print("All hashing tests passed!\n")


def test_security():
    """Test security module."""
    print("Testing security module...")

    from mcp_code_indexer.security import (
        normalize_repo_root,
        normalize_rel_file,
        PathAccessError,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create test directory structure
        allowed_dir = tmpdir_path / "allowed"
        allowed_dir.mkdir()

        repo_dir = allowed_dir / "repo"
        repo_dir.mkdir()

        # Test normalize_repo_root valid
        result = normalize_repo_root(str(repo_dir), [allowed_dir])
        assert result == repo_dir.resolve()
        print("✓ normalize_repo_root valid test passed")

        # Test normalize_repo_root not allowed
        other_dir = tmpdir_path / "other"
        other_dir.mkdir()

        try:
            normalize_repo_root(str(other_dir), [allowed_dir])
            assert False, "Should have raised PathAccessError"
        except PathAccessError:
            print("✓ normalize_repo_root not allowed test passed")

        # Test normalize_rel_file valid
        file_path = "src/main.py"
        result = normalize_rel_file(repo_dir, file_path)
        expected = (repo_dir / file_path).resolve()
        assert result == expected
        print("✓ normalize_rel_file valid test passed")

        # Test normalize_rel_file absolute path
        try:
            normalize_rel_file(repo_dir, "/absolute/path")
            assert False, "Should have raised PathAccessError"
        except PathAccessError as e:
            assert "must be relative" in str(e)
            print("✓ normalize_rel_file absolute path test passed")

        # Test normalize_rel_file traversal
        try:
            normalize_rel_file(repo_dir, "../outside")
            assert False, "Should have raised PathAccessError"
        except PathAccessError as e:
            assert "escapes repo_root" in str(e)
            print("✓ normalize_rel_file traversal test passed")

    print("All security tests passed!\n")


def test_chunkers():
    """Test chunkers module."""
    print("Testing chunkers module...")

    from mcp_code_indexer.chunkers import (
        Chunk,
        guess_language,
        chunk_python,
        chunk_fallback,
    )

    # Test Chunk dataclass
    chunk = Chunk(
        file_path="test.py",
        language="python",
        chunk_type="function",
        symbol_name="test_func",
        start_line=1,
        end_line=10,
        text="def test_func(): pass",
    )

    assert chunk.file_path == "test.py"
    assert chunk.symbol_name == "test_func"
    print("✓ Chunk dataclass test passed")

    # Test guess_language
    assert guess_language(Path("test.py")) == "python"
    assert guess_language(Path("script.js")) == "javascript"
    assert guess_language(Path("README.md")) == "markdown"
    print("✓ guess_language test passed")

    # Test chunk_python with simple code
    python_code = """
def hello():
    print("Hello")

class Test:
    def method(self):
        return "test"
"""

    chunks, symbols = chunk_python("test.py", python_code, max_chunk_chars=8000)

    assert len(chunks) > 0
    assert len(symbols) >= 2  # function and class
    print("✓ chunk_python test passed")

    # Test chunk_fallback
    text = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
    chunks = chunk_fallback("test.txt", text, "text", max_lines=2, overlap_lines=1)

    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.chunk_type == "window"
    print("✓ chunk_fallback test passed")

    print("All chunkers tests passed!\n")


def test_db():
    """Test database module."""
    print("Testing database module...")

    from mcp_code_indexer.db import connect, fetch_all, fetch_one, execute, SCHEMA

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    try:
        # Test connect creates schema
        conn = connect(db_path)
        assert conn is not None

        # Check that tables were created
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        table_names = [t[0] for t in tables]
        assert "workspaces" in table_names
        assert "snapshots" in table_names
        print("✓ Database schema creation test passed")

        # Test fetch_all
        cursor.execute("CREATE TABLE test_table (id INTEGER, name TEXT)")
        cursor.execute("INSERT INTO test_table VALUES (1, 'test1'), (2, 'test2')")
        conn.commit()

        results = fetch_all(conn, "SELECT * FROM test_table ORDER BY id", ())
        assert len(results) == 2
        assert results[0]["id"] == 1
        assert results[0]["name"] == "test1"
        assert results[1]["id"] == 2
        assert results[1]["name"] == "test2"
        print("✓ fetch_all test passed")

        # Test fetch_one
        result = fetch_one(conn, "SELECT name FROM test_table WHERE id = ?", (1,))
        assert result["name"] == "test1"
        print("✓ fetch_one test passed")

        # Test execute
        execute(conn, "INSERT INTO test_table VALUES (3, 'test3')", ())

        result = fetch_one(conn, "SELECT COUNT(*) FROM test_table", ())
        assert result["COUNT(*)"] == 3
        print("✓ execute test passed")

        conn.close()

    finally:
        os.unlink(db_path)

    print("All database tests passed!\n")


def main():
    """Run all tests."""
    print("Running mcp-code-indexer tests...")
    print("=" * 60)

    tests = [test_config, test_hashing, test_security, test_chunkers, test_db]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} failed: {e}")
            import traceback

            traceback.print_exc()
            failed += 1
        print("-" * 60)

    print("=" * 60)
    print(f"Test Summary:")
    print(f"  Total tests: {len(tests)}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
