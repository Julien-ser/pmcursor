"""Tests for helper functions."""

import pytest

from src.utils.helpers import (
    is_allowed_file,
    truncate_text,
    format_output,
    validate_file_extension,
)


class TestHelpers:
    """Test suite for helper functions."""

    def test_is_allowed_file_valid_extensions(self):
        """Test allowed file extensions."""
        assert is_allowed_file("test.txt") is True
        assert is_allowed_file("document.pdf") is True
        assert is_allowed_file("data.csv") is True
        assert is_allowed_file("config.json") is True
        assert is_allowed_file("notes.md") is True
        assert is_allowed_file("FILE.TXT") is True  # case insensitive
        assert is_allowed_file("data.JSON") is True

    def test_is_allowed_file_invalid_extensions(self):
        """Test disallowed file extensions."""
        assert is_allowed_file("script.py") is False
        assert is_allowed_file("image.jpg") is False
        assert is_allowed_file("video.mp4") is False
        assert is_allowed_file("archive.zip") is False
        assert is_allowed_file("document.docx") is False

    def test_is_allowed_file_no_extension(self):
        """Test file with no extension."""
        assert is_allowed_file("noextension") is False

    def test_validate_file_extension(self):
        """Test validate_file_extension function."""
        extensions = [".txt", ".pdf", ".csv"]
        assert validate_file_extension("test.txt", extensions) is True
        assert validate_file_extension("test.TXT", extensions) is True
        assert validate_file_extension("test.pdf", extensions) is True
        assert validate_file_extension("test.py", extensions) is False
        assert validate_file_extension("noext", extensions) is False

    def test_truncate_text_short(self):
        """Test truncate_text with short text."""
        text = "Short text"
        result = truncate_text(text, 20)
        assert result == text

    def test_truncate_text_long(self):
        """Test truncate_text with long text."""
        text = "This is a very long text that exceeds the limit"
        result = truncate_text(text, 20)
        assert result == "This is a very long ..."
        assert len(result) == 20

    def test_truncate_text_exact_length(self):
        """Test truncate_text with exact length."""
        text = "Exactly twenty chars here"
        result = truncate_text(text, 20)
        assert result == text

    def test_truncate_text_default_limit(self):
        """Test truncate_text with default limit."""
        text = "A" * 600
        result = truncate_text(text)
        assert len(result) == 500
        assert result.endswith("...")

    def test_format_output_dict(self):
        """Test format_output with dictionary."""
        data = {"key": "value", "number": 42}
        result = format_output(data)
        parsed = json.loads(result)
        assert parsed == data

    def test_format_output_nested(self):
        """Test format_output with nested structure."""
        data = {"items": [1, 2, 3], "meta": {"count": 3}}
        result = format_output(data)
        parsed = json.loads(result)
        assert parsed == data
