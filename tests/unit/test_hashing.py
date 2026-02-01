import pytest
from pathlib import Path
import hashlib

from mcp_code_indexer.hashing import sha256_bytes, sha256_text, sha256_file


class TestHashing:
    """Test hashing functions."""

    def test_sha256_bytes(self):
        """Test SHA256 hash of bytes."""
        test_data = b"Hello, World!"
        expected = hashlib.sha256(test_data).hexdigest()

        result = sha256_bytes(test_data)
        assert result == expected
        assert len(result) == 64  # SHA256 produces 64 hex chars

    def test_sha256_bytes_empty(self):
        """Test SHA256 hash of empty bytes."""
        test_data = b""
        expected = hashlib.sha256(test_data).hexdigest()

        result = sha256_bytes(test_data)
        assert result == expected

    def test_sha256_text(self):
        """Test SHA256 hash of text string."""
        test_text = "Hello, World!"
        expected = hashlib.sha256(test_text.encode("utf-8")).hexdigest()

        result = sha256_text(test_text)
        assert result == expected

    def test_sha256_text_unicode(self):
        """Test SHA256 hash of Unicode text."""
        test_text = "Hello, 世界! 🚀"
        result = sha256_text(test_text)

        # Should not raise encoding errors
        assert len(result) == 64

    def test_sha256_text_empty(self):
        """Test SHA256 hash of empty text."""
        test_text = ""
        expected = hashlib.sha256(test_text.encode("utf-8")).hexdigest()

        result = sha256_text(test_text)
        assert result == expected

    def test_sha256_file(self, temp_dir):
        """Test SHA256 hash of a file."""
        file_path = temp_dir / "test.txt"
        content = b"Test file content for hashing"
        file_path.write_bytes(content)

        expected = hashlib.sha256(content).hexdigest()
        result = sha256_file(file_path)

        assert result == expected

    def test_sha256_file_large(self, temp_dir):
        """Test SHA256 hash of a large file with chunking."""
        file_path = temp_dir / "large.txt"

        # Create a file larger than 1MB to test chunking
        content = b"X" * (2 * 1024 * 1024)  # 2MB
        file_path.write_bytes(content)

        expected = hashlib.sha256(content).hexdigest()
        result = sha256_file(file_path, chunk_size=1024 * 1024)  # 1MB chunks

        assert result == expected

    def test_sha256_file_empty(self, temp_dir):
        """Test SHA256 hash of an empty file."""
        file_path = temp_dir / "empty.txt"
        file_path.write_bytes(b"")

        expected = hashlib.sha256(b"").hexdigest()
        result = sha256_file(file_path)

        assert result == expected

    def test_sha256_file_not_exists(self, temp_dir):
        """Test SHA256 hash of non-existent file (should raise error)."""
        file_path = temp_dir / "not_exists.txt"

        with pytest.raises(FileNotFoundError):
            sha256_file(file_path)

    def test_sha256_file_small_chunk_size(self, temp_dir):
        """Test SHA256 hash with very small chunk size."""
        file_path = temp_dir / "test.txt"
        content = b"Test content"
        file_path.write_bytes(content)

        expected = hashlib.sha256(content).hexdigest()
        result = sha256_file(file_path, chunk_size=1)  # 1 byte chunks

        assert result == expected

    def test_sha256_consistency(self):
        """Test that hashing is consistent across different methods."""
        test_text = "Consistent hashing test"

        # All three methods should produce the same hash for the same content
        bytes_hash = sha256_bytes(test_text.encode("utf-8"))
        text_hash = sha256_text(test_text)

        assert bytes_hash == text_hash

    def test_sha256_file_vs_bytes(self, temp_dir):
        """Test that file hashing matches bytes hashing."""
        content = b"File content for comparison"
        file_path = temp_dir / "compare.txt"
        file_path.write_bytes(content)

        file_hash = sha256_file(file_path)
        bytes_hash = sha256_bytes(content)

        assert file_hash == bytes_hash
