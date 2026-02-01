import pytest
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch
import tempfile

from mcp_code_indexer.server import mcp, _stats_for_workspace


class TestServerIntegration:
    """Integration tests for the MCP server."""

    @pytest.fixture
    def mock_components(self):
        """Mock the server components."""
        with (
            patch("mcp_code_indexer.server.job_mgr") as mock_job_mgr,
            patch("mcp_code_indexer.server.search_engine") as mock_search_engine,
            patch("mcp_code_indexer.server.db_path") as mock_db_path,
        ):
            mock_job_mgr.index_repo = AsyncMock()
            mock_job_mgr.index_paths = AsyncMock()
            mock_search_engine.search = AsyncMock()
            mock_search_engine.find_symbol = AsyncMock()
            mock_search_engine.get_symbol_references = AsyncMock()
            mock_search_engine.get_callgraph = AsyncMock()
            mock_search_engine.list_snapshots = AsyncMock()
            mock_search_engine.fetch_file = AsyncMock()

            mock_db_path.__str__ = Mock(return_value="/tmp/test.db")

            yield {
                "job_mgr": mock_job_mgr,
                "search_engine": mock_search_engine,
                "db_path": mock_db_path,
            }

    @pytest.mark.asyncio
    async def test_index_init_tool(self, mock_components, temp_dir):
        """Test the index_init tool."""
        mock_job_mgr = mock_components["job_mgr"]
        mock_job_mgr.index_repo.return_value = {
            "status": "success",
            "workspace_id": "test123",
        }

        # Mock the security functions
        with patch("mcp_code_indexer.server.normalize_repo_root") as mock_normalize:
            mock_normalize.return_value = Path(temp_dir)

            # Call the tool
            result = await mcp._tools["index_init"].callback(repo_root=str(temp_dir))

            assert result["status"] == "success"
            assert "workspace_id" in result
            mock_job_mgr.index_repo.assert_called_once()

    @pytest.mark.asyncio
    async def test_index_refresh_tool(self, mock_components, temp_dir):
        """Test the index_refresh tool."""
        mock_job_mgr = mock_components["job_mgr"]
        mock_job_mgr.index_paths.return_value = {"status": "success", "updated": 5}

        with patch("mcp_code_indexer.server.normalize_repo_root") as mock_normalize:
            mock_normalize.return_value = Path(temp_dir)

            result = await mcp._tools["index_refresh"].callback(
                repo_root=str(temp_dir), rel_paths=["src/main.py", "tests/test.py"]
            )

            assert result["status"] == "success"
            assert "updated" in result
            mock_job_mgr.index_paths.assert_called_once()

    @pytest.mark.asyncio
    async def test_codebase_search_tool(self, mock_components, temp_dir):
        """Test the codebase_search tool."""
        mock_search_engine = mock_components["search_engine"]
        mock_search_engine.search.return_value = {
            "results": [
                {
                    "file_path": "src/main.py",
                    "start_line": 10,
                    "end_line": 20,
                    "text": "def hello_world():",
                    "score": 0.95,
                }
            ]
        }

        with patch("mcp_code_indexer.server.normalize_repo_root") as mock_normalize:
            mock_normalize.return_value = Path(temp_dir)

            result = await mcp._tools["codebase_search"].callback(
                query="hello world function",
                repo_root=str(temp_dir),
                top_k=10,
                mode="hybrid",
            )

            assert "results" in result
            assert len(result["results"]) == 1
            assert result["results"][0]["file_path"] == "src/main.py"
            mock_search_engine.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_symbol_find_tool(self, mock_components, temp_dir):
        """Test the symbol_find tool."""
        mock_search_engine = mock_components["search_engine"]
        mock_search_engine.find_symbol.return_value = {
            "symbols": [
                {
                    "symbol_id": "abc123",
                    "symbol_name": "User",
                    "symbol_kind": "class",
                    "file_path": "models/user.py",
                    "start_line": 5,
                    "end_line": 50,
                }
            ]
        }

        with patch("mcp_code_indexer.server.normalize_repo_root") as mock_normalize:
            mock_normalize.return_value = Path(temp_dir)

            result = await mcp._tools["symbol_find"].callback(
                repo_root=str(temp_dir), name="User", language="python"
            )

            assert "symbols" in result
            assert len(result["symbols"]) == 1
            assert result["symbols"][0]["symbol_name"] == "User"
            mock_search_engine.find_symbol.assert_called_once()

    @pytest.mark.asyncio
    async def test_symbol_references_tool(self, mock_components, temp_dir):
        """Test the symbol_references tool."""
        mock_search_engine = mock_components["search_engine"]
        mock_search_engine.get_symbol_references.return_value = {
            "references": [
                {
                    "file_path": "src/auth.py",
                    "start_line": 42,
                    "end_line": 42,
                    "text": "user = User()",
                }
            ]
        }

        with patch("mcp_code_indexer.server.normalize_repo_root") as mock_normalize:
            mock_normalize.return_value = Path(temp_dir)

            result = await mcp._tools["symbol_references"].callback(
                repo_root=str(temp_dir), symbol_name="User", limit=20
            )

            assert "references" in result
            assert len(result["references"]) == 1
            assert "User()" in result["references"][0]["text"]
            mock_search_engine.get_symbol_references.assert_called_once()

    @pytest.mark.asyncio
    async def test_callgraph_tool(self, mock_components, temp_dir):
        """Test the callgraph tool."""
        mock_search_engine = mock_components["search_engine"]
        mock_search_engine.get_callgraph.return_value = {
            "nodes": [{"id": "func1", "name": "process_user", "type": "function"}],
            "edges": [{"source": "func1", "target": "func2", "type": "calls"}],
        }

        with patch("mcp_code_indexer.server.normalize_repo_root") as mock_normalize:
            mock_normalize.return_value = Path(temp_dir)

            result = await mcp._tools["callgraph"].callback(
                repo_root=str(temp_dir), symbol_id="abc123", depth=2, direction="out"
            )

            assert "nodes" in result
            assert "edges" in result
            mock_search_engine.get_callgraph.assert_called_once()

    @pytest.mark.asyncio
    async def test_git_list_snapshots_tool(self, mock_components, temp_dir):
        """Test the git_list_snapshots tool."""
        mock_search_engine = mock_components["search_engine"]
        mock_search_engine.list_snapshots.return_value = {
            "snapshots": [
                {"git_ref": "abc123", "indexed_at": "2024-01-01T00:00:00Z"},
                {"git_ref": "working_tree", "indexed_at": "2024-01-02T00:00:00Z"},
            ]
        }

        with patch("mcp_code_indexer.server.normalize_repo_root") as mock_normalize:
            mock_normalize.return_value = Path(temp_dir)

            result = await mcp._tools["git_list_snapshots"].callback(
                repo_root=str(temp_dir)
            )

            assert "snapshots" in result
            assert len(result["snapshots"]) == 2
            mock_search_engine.list_snapshots.assert_called_once()

    @pytest.mark.asyncio
    async def test_codebase_fetch_tool(self, mock_components, temp_dir):
        """Test the codebase_fetch tool."""
        mock_search_engine = mock_components["search_engine"]
        mock_search_engine.fetch_file.return_value = {
            "file_path": "src/main.py",
            "content": "def main():\n    print('Hello')",
            "start_line": 1,
            "end_line": 2,
        }

        with (
            patch("mcp_code_indexer.server.normalize_repo_root") as mock_normalize,
            patch("mcp_code_indexer.server.normalize_rel_file") as mock_normalize_file,
        ):
            mock_normalize.return_value = Path(temp_dir)
            mock_normalize_file.return_value = Path(temp_dir) / "src/main.py"

            result = await mcp._tools["codebase_fetch"].callback(
                repo_root=str(temp_dir),
                file_path="src/main.py",
                start_line=1,
                end_line=10,
            )

            assert "file_path" in result
            assert "content" in result
            assert "def main()" in result["content"]
            mock_search_engine.fetch_file.assert_called_once()

    def test_stats_for_workspace(self, mock_components):
        """Test the _stats_for_workspace helper function."""
        mock_db_path = mock_components["db_path"]

        with (
            patch("mcp_code_indexer.server.connect") as mock_connect,
            patch("mcp_code_indexer.server.fetch_one") as mock_fetch_one,
        ):
            mock_conn = Mock()
            mock_connect.return_value = mock_conn

            # Mock the fetch_one calls
            mock_fetch_one.side_effect = [
                {"n": 100},  # files count
                {"n": 50},  # symbols count
                {"n": 30},  # python symbols count
                {"n": 200},  # references count
            ]

            stats = _stats_for_workspace("test_workspace", "abc123")

            assert stats["files"] == 100
            assert stats["symbols"] == 50
            assert stats["python_symbols"] == 30
            assert stats["references"] == 200

            # Should have made 4 fetch_one calls
            assert mock_fetch_one.call_count == 4

    def test_stats_for_workspace_no_git_ref(self, mock_components):
        """Test _stats_for_workspace without git_ref."""
        mock_db_path = mock_components["db_path"]

        with (
            patch("mcp_code_indexer.server.connect") as mock_connect,
            patch("mcp_code_indexer.server.fetch_one") as mock_fetch_one,
        ):
            mock_conn = Mock()
            mock_connect.return_value = mock_conn

            # Mock the fetch_one calls (without git_ref)
            mock_fetch_one.side_effect = [
                {"n": 80},  # files count
                {"n": 40},  # symbols count
                {"n": 25},  # python symbols count
                {"n": 150},  # references count
            ]

            stats = _stats_for_workspace("test_workspace", None)

            assert stats["files"] == 80
            assert stats["symbols"] == 40
            assert stats["python_symbols"] == 25
            assert stats["references"] == 150

            # Should have made 4 fetch_one calls with different queries
            assert mock_fetch_one.call_count == 4

    def test_tools_registered(self):
        """Test that all expected tools are registered."""
        expected_tools = [
            "index_init",
            "index_refresh",
            "codebase_search",
            "symbol_find",
            "symbol_references",
            "callgraph",
            "git_list_snapshots",
            "codebase_fetch",
        ]

        for tool_name in expected_tools:
            assert tool_name in mcp._tools
            assert hasattr(mcp._tools[tool_name], "callback")
            assert callable(mcp._tools[tool_name].callback)
