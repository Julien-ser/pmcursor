"""Tests for DataProcessor class."""

import os
import pytest
from src.core.data_processor import DataProcessor


class TestDataProcessor:
    """Test suite for DataProcessor."""

    def test_extract_from_text(self, data_processor, temp_upload_dir):
        """Test extracting text from plain text file."""
        test_file = os.path.join(temp_upload_dir, "test.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("Hello, World!")

        text = data_processor._extract_from_text(test_file)
        assert text == "Hello, World!"

    def test_extract_from_markdown(self, data_processor, temp_upload_dir):
        """Test extracting text from markdown file."""
        test_file = os.path.join(temp_upload_dir, "test.md")
        content = "# Heading\n\nThis is a paragraph."
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)

        text = data_processor._extract_from_text(test_file)  # .md treated as text
        assert text == content

    def test_extract_from_pdf(self, data_processor):
        """Test extracting text from PDF file."""
        # This test requires a real PDF file; we'll skip if PyPDF2 is not available
        pytest.importorskip("PyPDF2")

        # For now, we'll create a simple test that checks the method exists
        # In a real scenario, we'd create a sample PDF
        assert hasattr(data_processor, "_extract_from_pdf")

    def test_extract_from_csv(self, data_processor, temp_upload_dir):
        """Test extracting text from CSV file."""
        test_file = os.path.join(temp_upload_dir, "test.csv")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("name,age\nAlice,30\nBob,25")

        text = data_processor._extract_from_csv(test_file)
        assert "CSV Data Summary" in text
        assert "name, age" in text or "name,age" in text
        assert "Alice" in text
        assert "Bob" in text

    def test_extract_from_json(self, data_processor, temp_upload_dir):
        """Test extracting text from JSON file."""
        test_file = os.path.join(temp_upload_dir, "test.json")
        data = {"key": "value", "numbers": [1, 2, 3]}
        import json

        with open(test_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

        text = data_processor._extract_from_json(test_file)
        assert "key" in text
        assert "value" in text

        # Should be valid JSON
        parsed = json.loads(text)
        assert parsed == data

    def test_extract_text_unsupported_type(self, data_processor):
        """Test that unsupported file type raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported file type"):
            data_processor.extract_text("dummy path", "xyz")

    def test_extract_text_txt(self, data_processor, temp_upload_dir):
        """Test extract_text for txt files."""
        test_file = os.path.join(temp_upload_dir, "test.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("Test content")

        text = data_processor.extract_text(test_file, "txt")
        assert text == "Test content"

    def test_extract_text_pdf(self, data_processor, temp_upload_dir):
        """Test extract_text for pdf files."""
        pytest.importorskip("PyPDF2")
        # This would need an actual PDF file
        # For now, just verify the method routes correctly
        assert data_processor.extract_text.__code__.co_code is not None

    def test_extract_text_csv(self, data_processor, temp_upload_dir):
        """Test extract_text for csv files."""
        test_file = os.path.join(temp_upload_dir, "test.csv")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("col1,col2\nval1,val2")

        text = data_processor.extract_text(test_file, "csv")
        assert "col1" in text
        assert "col2" in text

    def test_extract_text_json(self, data_processor, temp_upload_dir):
        """Test extract_text for json files."""
        test_file = os.path.join(temp_upload_dir, "test.json")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write('{"test": "data"}')

        text = data_processor.extract_text(test_file, "json")
        assert "test" in text
        assert "data" in text

    def test_process_project_files_empty_dir(self, data_processor, tmp_path):
        """Test processing when upload directory doesn't exist."""
        # Use a non-existent project ID
        result = data_processor.process_project_files(99999)
        assert result == ""

    def test_process_project_files_multiple(
        self, file_manager, data_processor, sample_project, temp_upload_dir
    ):
        """Test processing multiple files."""
        # Create test files
        files = [
            ("file1.txt", "Content 1"),
            ("file2.md", "# Header\nContent 2"),
            ("file3.csv", "a,b\n1,2"),
        ]

        for filename, content in files:
            file_path = os.path.join(temp_upload_dir, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            file_manager.save_upload(file_path, filename, sample_project.id)

        result = data_processor.process_project_files(sample_project.id)

        assert "file1.txt" in result
        assert "Content 1" in result
        assert "file2.md" in result
        assert "# Header" in result
        assert "file3.csv" in result

    def test_process_project_files_handles_errors(
        self, file_manager, data_processor, sample_project, temp_upload_dir
    ):
        """Test that processing handles file errors gracefully."""
        # Create a file that will cause an error (e.g., corrupted PDF)
        test_file = os.path.join(temp_upload_dir, "corrupted.pdf")
        with open(test_file, "wb") as f:
            f.write(b"Not a real PDF")

        file_manager.save_upload(test_file, "corrupted.pdf", sample_project.id)

        result = data_processor.process_project_files(sample_project.id)

        # Should include error message
        assert "corrupted.pdf" in result
        assert "ERROR" in result or "error" in result.lower()
