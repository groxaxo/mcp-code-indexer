import os
from pathlib import Path
from unittest.mock import patch
import pytest

from mcp_code_indexer.config import Config, load_config


class TestConfig:
    """Test configuration loading and validation."""

    def test_config_creation(self):
        """Test Config dataclass creation."""
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
        assert config.data_dir == Path("/tmp/data")
        assert config.qdrant_host == "localhost"
        assert config.qdrant_port == 6333
        assert config.qdrant_collection == "test_collection"
        assert config.max_chunk_chars == 8000
        assert config.max_fallback_lines == 220
        assert config.fallback_overlap_lines == 40

    def test_load_config_defaults(self):
        """Test loading config with default environment variables."""
        with patch.dict(os.environ, {}, clear=True):
            config = load_config()

            # Should default to current working directory
            assert config.allowed_roots == [Path.cwd().resolve()]
            assert config.qdrant_host == "127.0.0.1"
            assert config.qdrant_port == 6333
            assert config.qdrant_collection == "code_chunks"
            assert config.max_chunk_chars == 8000
            assert config.max_fallback_lines == 220
            assert config.fallback_overlap_lines == 40

    def test_load_config_custom_env(self):
        """Test loading config with custom environment variables."""
        test_path = "/custom/path:/another/path"
        with patch.dict(
            os.environ,
            {
                "MCP_ALLOWED_ROOTS": test_path,
                "MCP_CODE_INDEX_DATA_DIR": "/custom/data",
                "QDRANT_HOST": "custom-host",
                "QDRANT_PORT": "9999",
                "QDRANT_COLLECTION": "custom_collection",
                "MCP_MAX_CHUNK_CHARS": "5000",
                "MCP_MAX_FALLBACK_LINES": "100",
                "MCP_FALLBACK_OVERLAP_LINES": "20",
            },
            clear=True,
        ):
            config = load_config()

            assert len(config.allowed_roots) == 2
            assert (
                config.allowed_roots[0] == Path("/custom/path").expanduser().resolve()
            )
            assert (
                config.allowed_roots[1] == Path("/another/path").expanduser().resolve()
            )
            assert config.data_dir == Path("/custom/data").expanduser().resolve()
            assert config.qdrant_host == "custom-host"
            assert config.qdrant_port == 9999
            assert config.qdrant_collection == "custom_collection"
            assert config.max_chunk_chars == 5000
            assert config.max_fallback_lines == 100
            assert config.fallback_overlap_lines == 20

    def test_load_config_empty_allowed_roots(self):
        """Test loading config with empty allowed roots string."""
        with patch.dict(os.environ, {"MCP_ALLOWED_ROOTS": ""}, clear=True):
            config = load_config()

            # Should default to current working directory
            assert config.allowed_roots == [Path.cwd().resolve()]

    def test_load_config_with_tilde_expansion(self):
        """Test that tilde expansion works in paths."""
        with patch.dict(
            os.environ,
            {
                "MCP_ALLOWED_ROOTS": "~/test/path",
                "MCP_CODE_INDEX_DATA_DIR": "~/test/data",
            },
            clear=True,
        ):
            config = load_config()

            # Paths should be expanded
            assert str(config.allowed_roots[0]).startswith("/")
            assert "~" not in str(config.allowed_roots[0])
            assert str(config.data_dir).startswith("/")
            assert "~" not in str(config.data_dir)

    def test_config_immutable(self):
        """Test that Config is immutable (frozen dataclass)."""
        config = Config(
            allowed_roots=[Path("/test")],
            data_dir=Path("/tmp"),
            qdrant_host="localhost",
            qdrant_port=6333,
            qdrant_collection="test",
            max_chunk_chars=8000,
            max_fallback_lines=220,
            fallback_overlap_lines=40,
        )

        # Should not be able to modify attributes
        with pytest.raises(Exception):
            config.qdrant_host = "new-host"
