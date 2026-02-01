import pytest
from pathlib import Path
from unittest.mock import Mock

from mcp_code_indexer.security import (
    normalize_repo_root,
    normalize_rel_file,
    PathAccessError,
)


class TestSecurity:
    """Test security and path normalization functions."""

    def test_normalize_repo_root_valid(self, temp_dir):
        """Test normalizing a repo root within allowed paths."""
        allowed_roots = [temp_dir]
        repo_root = temp_dir / "subdir"
        repo_root.mkdir()

        result = normalize_repo_root(str(repo_root), allowed_roots)
        assert result == repo_root.resolve()

    def test_normalize_repo_root_nested(self, temp_dir):
        """Test normalizing a nested repo root within allowed paths."""
        allowed_roots = [temp_dir]
        repo_root = temp_dir / "deeply" / "nested" / "directory"
        repo_root.mkdir(parents=True)

        result = normalize_repo_root(str(repo_root), allowed_roots)
        assert result == repo_root.resolve()

    def test_normalize_repo_root_not_exist(self, temp_dir):
        """Test normalizing a non-existent repo root."""
        allowed_roots = [temp_dir]
        non_existent = temp_dir / "does_not_exist"

        with pytest.raises(PathAccessError, match="repo_root does not exist"):
            normalize_repo_root(str(non_existent), allowed_roots)

    def test_normalize_repo_root_not_directory(self, temp_dir):
        """Test normalizing a repo root that is not a directory."""
        allowed_roots = [temp_dir]
        file_path = temp_dir / "file.txt"
        file_path.write_text("test")

        with pytest.raises(
            PathAccessError, match="repo_root does not exist or is not a directory"
        ):
            normalize_repo_root(str(file_path), allowed_roots)

    def test_normalize_repo_root_not_allowed(self, temp_dir):
        """Test normalizing a repo root outside allowed paths."""
        allowed_roots = [Path("/allowed/path")]
        repo_root = temp_dir  # Different from allowed path

        with pytest.raises(
            PathAccessError, match="repo_root is not within MCP_ALLOWED_ROOTS"
        ):
            normalize_repo_root(str(repo_root), allowed_roots)

    def test_normalize_repo_root_multiple_allowed(self, temp_dir):
        """Test normalizing with multiple allowed roots."""
        allowed_root1 = temp_dir / "allowed1"
        allowed_root2 = temp_dir / "allowed2"
        allowed_root1.mkdir()
        allowed_root2.mkdir()

        allowed_roots = [allowed_root1, allowed_root2]
        repo_root = allowed_root2 / "subdir"
        repo_root.mkdir()

        result = normalize_repo_root(str(repo_root), allowed_roots)
        assert result == repo_root.resolve()

    def test_normalize_rel_file_valid(self, temp_dir):
        """Test normalizing a relative file path."""
        repo_root = temp_dir
        file_path = "src/main.py"

        result = normalize_rel_file(repo_root, file_path)
        expected = (repo_root / file_path).resolve()
        assert result == expected

    def test_normalize_rel_file_with_subdirectories(self, temp_dir):
        """Test normalizing a relative file path with subdirectories."""
        repo_root = temp_dir
        file_path = "deeply/nested/directory/file.py"

        result = normalize_rel_file(repo_root, file_path)
        expected = (repo_root / file_path).resolve()
        assert result == expected

    def test_normalize_rel_file_absolute_path(self, temp_dir):
        """Test normalizing an absolute file path (should fail)."""
        repo_root = temp_dir
        file_path = "/absolute/path/file.py"

        with pytest.raises(PathAccessError, match="file_path must be relative"):
            normalize_rel_file(repo_root, file_path)

    def test_normalize_rel_file_traversal_attempt(self, temp_dir):
        """Test normalizing a file path with traversal (should fail)."""
        repo_root = temp_dir
        file_path = "../outside/file.py"

        with pytest.raises(PathAccessError, match="file_path escapes repo_root"):
            normalize_rel_file(repo_root, file_path)

    def test_normalize_rel_file_double_dots(self, temp_dir):
        """Test normalizing a file path with multiple dots (should fail)."""
        repo_root = temp_dir
        file_path = "subdir/../../outside/file.py"

        with pytest.raises(PathAccessError, match="file_path escapes repo_root"):
            normalize_rel_file(repo_root, file_path)

    def test_normalize_rel_file_dot_slash(self, temp_dir):
        """Test normalizing a file path starting with ./."""
        repo_root = temp_dir
        file_path = "./src/main.py"

        result = normalize_rel_file(repo_root, file_path)
        expected = (repo_root / "src/main.py").resolve()
        assert result == expected

    def test_path_resolution_symlink_protection(self, temp_dir):
        """Test that path resolution protects against symlink traversal."""
        repo_root = temp_dir
        subdir = repo_root / "subdir"
        subdir.mkdir()

        # Create a symlink that points outside repo_root
        symlink = subdir / "link"
        symlink.symlink_to("/tmp")

        # Try to access through symlink
        file_path = "subdir/link/../.."

        with pytest.raises(PathAccessError, match="file_path escapes repo_root"):
            normalize_rel_file(repo_root, file_path)

    def test_normalize_repo_root_expand_user(self, temp_dir, monkeypatch):
        """Test that tilde expansion works in repo root paths."""
        # Mock home directory
        mock_home = temp_dir / "home" / "user"
        mock_home.mkdir(parents=True)
        monkeypatch.setenv("HOME", str(mock_home))

        allowed_roots = [mock_home]
        repo_root = "~/projects/myproject"

        result = normalize_repo_root(repo_root, allowed_roots)
        expected = (mock_home / "projects/myproject").resolve()
        assert result == expected
