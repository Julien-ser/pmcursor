import os
from pathlib import Path
from typing import List, Optional
import PyPDF2
import pandas as pd
import json


class DataProcessor:
    """Processes uploaded files into analyzable text content."""

    def __init__(self, file_manager):
        self.file_manager = file_manager

    def extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text content from various file types."""
        file_type = file_type.lower()

        if file_type in ["txt", "md"]:
            return self._extract_from_text(file_path)
        elif file_type == "pdf":
            return self._extract_from_pdf(file_path)
        elif file_type in ["csv"]:
            return self._extract_from_csv(file_path)
        elif file_type in ["json"]:
            return self._extract_from_json(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def _extract_from_text(self, file_path: str) -> str:
        """Extract text from a plain text file."""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file."""
        text = []
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text())
        return "\n".join(text)

    def _extract_from_csv(self, file_path: str) -> str:
        """Extract and format data from CSV."""
        df = pd.read_csv(file_path)
        # Convert to a readable text format
        return f"CSV Data Summary:\nColumns: {', '.join(df.columns)}\n\nRows: {len(df)}\n\nSample Data:\n{df.head(10).to_string()}"

    def _extract_from_json(self, file_path: str) -> str:
        """Extract and format data from JSON."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, indent=2)

    def process_project_files(self, project_id: int) -> str:
        """Process all files for a project and return combined text."""
        upload_dir = self.file_manager.get_upload_dir(project_id)
        if not upload_dir.exists():
            return ""

        combined_text = []
        for file_path in upload_dir.iterdir():
            if file_path.is_file():
                try:
                    file_type = file_path.suffix.lstrip(".")
                    text = self.extract_text(str(file_path), file_type)
                    combined_text.append(f"=== {file_path.name} ===\n{text}\n")
                except Exception as e:
                    combined_text.append(
                        f"=== {file_path.name} (ERROR: {str(e)}) ===\n"
                    )

        return "\n".join(combined_text)
