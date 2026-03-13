"""Tests for FileManager class."""

import os
import shutil
from pathlib import Path
import pytest

from src.storage.file_manager import FileManager


class TestFileManager:
    """Test suite for FileManager."""

    def test_init_creates_directories(self, temp_upload_dir, monkeypatch):
        """Test that FileManager creates necessary directories."""
        from src.config import settings

        # Update the actual global settings
        upload_path = os.path.join(temp_upload_dir, "uploads")
        data_path = os.path.join(temp_upload_dir, "data")
        monkeypatch.setattr(settings, "upload_dir", upload_path)
        monkeypatch.setattr(settings, "data_dir", data_path)

        fm = FileManager()
        assert os.path.exists(settings.upload_dir)
        assert os.path.exists(settings.data_dir)

    def test_save_upload(self, file_manager, temp_upload_dir, sample_project):
        """Test saving an uploaded file."""
        # Create a temp file to upload
        temp_file = os.path.join(temp_upload_dir, "source.txt")
        with open(temp_file, "w") as f:
            f.write("test content")

        saved_path = file_manager.save_upload(temp_file, "test.txt", sample_project.id)

        assert saved_path is not None
        assert os.path.exists(saved_path)
        assert "test.txt" in saved_path
        assert str(sample_project.id) in saved_path

        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)

    def test_get_file_path(self, file_manager, temp_upload_dir, sample_project):
        """Test getting file path."""
        # Save a file first
        temp_file = os.path.join(temp_upload_dir, "source.txt")
        with open(temp_file, "w") as f:
            f.write("test content")

        saved_path = file_manager.save_upload(temp_file, "test.txt", sample_project.id)
        file_path = file_manager.get_file_path(sample_project.id, "test.txt")

        assert file_path is not None
        assert file_path.exists()
        assert str(file_path) == saved_path

        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)

    def test_get_file_path_not_found(self, file_manager, sample_project):
        """Test getting non-existent file returns None."""
        file_path = file_manager.get_file_path(sample_project.id, "nonexistent.txt")
        assert file_path is None

    def test_delete_project_files(self, file_manager, temp_upload_dir, sample_project):
        """Test deleting project files."""
        # Save multiple files
        temp_file1 = os.path.join(temp_upload_dir, "file1.txt")
        temp_file2 = os.path.join(temp_upload_dir, "file2.txt")
        with open(temp_file1, "w") as f:
            f.write("content 1")
        with open(temp_file2, "w") as f:
            f.write("content 2")

        file_manager.save_upload(temp_file1, "file1.txt", sample_project.id)
        file_manager.save_upload(temp_file2, "file2.txt", sample_project.id)

        project_dir = file_manager.get_upload_dir(sample_project.id)
        assert project_dir.exists()

        file_manager.delete_project_files(sample_project.id)

        assert not project_dir.exists()

        # Clean up temp files
        for f in [temp_file1, temp_file2]:
            if os.path.exists(f):
                os.remove(f)

    def test_get_upload_dir(self, file_manager, sample_project):
        """Test getting upload directory."""
        upload_dir = file_manager.get_upload_dir(sample_project.id)
        assert upload_dir is not None
        assert str(sample_project.id) in str(upload_dir)

    def test_get_data_dir(self, file_manager):
        """Test getting data directory."""
        data_dir = file_manager.get_data_dir()
        assert data_dir is not None
        assert data_dir.exists()
