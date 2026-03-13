import os
import shutil
from pathlib import Path
from typing import Optional
from src.config import settings


class FileManager:
    """Handles file uploads and storage operations."""

    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.data_dir = Path(settings.data_dir)
        self._ensure_directories()

    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        self.upload_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)

    def save_upload(self, file_path: str, filename: str, project_id: int) -> str:
        """Save an uploaded file to the project's upload directory."""
        project_upload_dir = self.upload_dir / str(project_id)
        project_upload_dir.mkdir(exist_ok=True)

        destination = project_upload_dir / filename
        shutil.copy2(file_path, destination)

        return str(destination)

    def get_file_path(self, project_id: int, filename: str) -> Optional[Path]:
        """Get the path to a stored file."""
        file_path = self.upload_dir / str(project_id) / filename
        return file_path if file_path.exists() else None

    def delete_project_files(self, project_id: int):
        """Delete all files associated with a project."""
        project_upload_dir = self.upload_dir / str(project_id)
        if project_upload_dir.exists():
            shutil.rmtree(project_upload_dir)

    def get_upload_dir(self, project_id: int) -> Path:
        """Get the upload directory for a project."""
        return self.upload_dir / str(project_id)

    def get_data_dir(self) -> Path:
        """Get the main data directory."""
        return self.data_dir


file_manager = FileManager()
