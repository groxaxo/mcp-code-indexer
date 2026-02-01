import pytest
from pathlib import Path

from mcp_code_indexer.chunkers import (
    Chunk,
    guess_language,
    chunk_python,
    chunk_fallback,
)


class TestChunkers:
    """Test code chunking functionality."""

    def test_chunk_dataclass(self):
        """Test Chunk dataclass creation and properties."""
        chunk = Chunk(
            file_path="src/main.py",
            language="python",
            chunk_type="function",
            symbol_name="hello_world",
            start_line=10,
            end_line=20,
            text="def hello_world():\n    print('Hello')",
        )

        assert chunk.file_path == "src/main.py"
        assert chunk.language == "python"
        assert chunk.chunk_type == "function"
        assert chunk.symbol_name == "hello_world"
        assert chunk.start_line == 10
        assert chunk.end_line == 20
        assert "def hello_world" in chunk.text

    def test_guess_language_python(self):
        """Test language guessing for Python files."""
        assert guess_language(Path("test.py")) == "python"
        assert guess_language(Path("module.py")) == "python"
        assert guess_language(Path("src/main.py")) == "python"

    def test_guess_language_javascript(self):
        """Test language guessing for JavaScript files."""
        assert guess_language(Path("script.js")) == "javascript"
        assert guess_language(Path("app.jsx")) == "javascript"

    def test_guess_language_typescript(self):
        """Test language guessing for TypeScript files."""
        assert guess_language(Path("types.ts")) == "typescript"
        assert guess_language(Path("component.tsx")) == "typescript"

    def test_guess_language_other(self):
        """Test language guessing for other file types."""
        assert guess_language(Path("README.md")) == "markdown"
        assert guess_language(Path("config.json")) == "json"
        assert guess_language(Path("docker-compose.yml")) == "yaml"
        assert guess_language(Path("script.sh")) == "bash"
        assert guess_language(Path("query.sql")) == "sql"
        assert guess_language(Path("Cargo.toml")) == "toml"

    def test_guess_language_unknown(self):
        """Test language guessing for unknown file extensions."""
        assert guess_language(Path("file.unknown")) == "text"
        assert guess_language(Path("no_extension")) == "text"

    def test_guess_language_case_insensitive(self):
        """Test that language guessing is case-insensitive."""
        assert guess_language(Path("test.PY")) == "python"
        assert guess_language(Path("TEST.JS")) == "javascript"
        assert guess_language(Path("File.TSX")) == "typescript"

    def test_chunk_python_simple_function(self, sample_python_code):
        """Test chunking a simple Python function."""
        chunks, symbols = chunk_python(
            "test.py", sample_python_code, max_chunk_chars=8000
        )

        # Should have at least module chunk and function chunk
        assert len(chunks) >= 2

        # Check for function chunk
        function_chunks = [c for c in chunks if c.chunk_type == "function"]
        assert len(function_chunks) >= 1

        func_chunk = function_chunks[0]
        assert func_chunk.symbol_name == "hello_world"
        assert func_chunk.language == "python"
        assert "def hello_world" in func_chunk.text
        assert "print" in func_chunk.text

        # Check symbols
        assert len(symbols) >= 2  # function and class
        symbol_names = [s[0] for s in symbols]
        assert "hello_world" in symbol_names
        assert "TestClass" in symbol_names

    def test_chunk_python_class(self, sample_python_code):
        """Test chunking a Python class."""
        chunks, symbols = chunk_python(
            "test.py", sample_python_code, max_chunk_chars=8000
        )

        # Find class chunk
        class_chunks = [c for c in chunks if c.chunk_type == "class"]
        assert len(class_chunks) >= 1

        class_chunk = class_chunks[0]
        assert class_chunk.symbol_name == "TestClass"
        assert class_chunk.language == "python"
        assert "class TestClass" in class_chunk.text
        assert "__init__" in class_chunk.text or "def greet" in class_chunk.text

    def test_chunk_python_module_chunk(self, sample_python_code):
        """Test that module-level chunk is created."""
        chunks, symbols = chunk_python(
            "test.py", sample_python_code, max_chunk_chars=8000
        )

        # Should have module chunk (first 80 lines)
        module_chunks = [c for c in chunks if c.chunk_type == "module"]
        assert len(module_chunks) >= 1

        module_chunk = module_chunks[0]
        assert module_chunk.symbol_name is None
        assert module_chunk.language == "python"
        assert module_chunk.start_line == 1
        assert module_chunk.end_line <= 80

    def test_chunk_python_syntax_error(self):
        """Test chunking Python code with syntax error (should fallback)."""
        invalid_python = "def invalid_function(\n    missing_paren"

        chunks, symbols = chunk_python("bad.py", invalid_python, max_chunk_chars=8000)

        # Should use fallback chunking
        assert len(chunks) > 0
        # Fallback creates window chunks
        assert any(c.chunk_type == "window" for c in chunks)

    def test_chunk_python_large_function(self):
        """Test chunking a large Python function (should split into windows)."""
        # Create a large function
        lines = ["def large_function():"] + [
            f"    print('Line {i}')" for i in range(1000)
        ]
        large_code = "\n".join(lines)

        chunks, symbols = chunk_python("large.py", large_code, max_chunk_chars=1000)

        # Should have window chunks for the large function
        window_chunks = [c for c in chunks if c.chunk_type == "window"]
        assert len(window_chunks) > 1  # Should be split into multiple windows

        # All chunks should be within size limit
        for chunk in window_chunks:
            assert len(chunk.text) <= 1000

    def test_chunk_fallback_basic(self):
        """Test fallback chunking for non-Python files."""
        text = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        chunks = chunk_fallback("test.txt", text, "text", max_lines=2, overlap_lines=1)

        # With max_lines=2 and overlap_lines=1, we should get overlapping chunks
        assert len(chunks) >= 2

        for chunk in chunks:
            assert chunk.chunk_type == "window"
            assert chunk.language == "text"
            assert chunk.symbol_name is None
            assert chunk.end_line - chunk.start_line + 1 <= 2

    def test_chunk_fallback_overlap(self):
        """Test that fallback chunking creates overlapping chunks."""
        # Create text with 10 lines
        lines = [f"Line {i + 1}" for i in range(10)]
        text = "\n".join(lines)

        chunks = chunk_fallback("test.txt", text, "text", max_lines=3, overlap_lines=1)

        # Check that chunks overlap
        chunk_ranges = [(c.start_line, c.end_line) for c in chunks]

        # Each chunk should have 3 lines (except possibly last)
        for start, end in chunk_ranges:
            assert end - start + 1 <= 3

        # Check overlap between consecutive chunks
        for i in range(len(chunk_ranges) - 1):
            _, end1 = chunk_ranges[i]
            start2, _ = chunk_ranges[i + 1]
            # Should overlap by at least 1 line
            assert start2 <= end1

    def test_chunk_fallback_empty(self):
        """Test fallback chunking with empty text."""
        chunks = chunk_fallback("empty.txt", "", "text", max_lines=10, overlap_lines=2)

        # Should return empty list for empty text
        assert len(chunks) == 0

    def test_chunk_fallback_single_line(self):
        """Test fallback chunking with single line."""
        text = "Single line of text"
        chunks = chunk_fallback(
            "single.txt", text, "text", max_lines=10, overlap_lines=2
        )

        assert len(chunks) == 1
        chunk = chunks[0]
        assert chunk.start_line == 1
        assert chunk.end_line == 1
        assert chunk.text == text

    def test_chunk_fallback_whitespace(self):
        """Test fallback chunking with whitespace-only text."""
        text = "   \n\n\t\n   "
        chunks = chunk_fallback(
            "whitespace.txt", text, "text", max_lines=10, overlap_lines=2
        )

        # Should return empty list for whitespace-only text
        assert len(chunks) == 0
