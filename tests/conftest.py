import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock
import sys

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_python_code():
    """Sample Python code for testing."""
    return '''
def hello_world():
    """A simple hello world function."""
    print("Hello, World!")
    return "Hello"

class TestClass:
    """A test class for demonstration."""
    
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello, {self.name}"
'''


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    from mcp_code_indexer.config import Config

    return Config(
        allowed_roots=[Path("/allowed/path")],
        data_dir=Path("/tmp/test_data"),
        qdrant_host="localhost",
        qdrant_port=6333,
        qdrant_collection="test_collection",
        max_chunk_chars=8000,
        max_fallback_lines=220,
        fallback_overlap_lines=40,
    )


@pytest.fixture
def mock_db_connection():
    """Create a mock database connection."""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn


@pytest.fixture
def mock_qdrant_client():
    """Create a mock Qdrant client."""
    mock_client = Mock()
    mock_client.upsert = AsyncMock()
    mock_client.search = AsyncMock()
    mock_client.delete = AsyncMock()
    return mock_client
