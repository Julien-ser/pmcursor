"""Utility helper functions."""

import json
from typing import Any, Dict


def format_output(data: Dict[str, Any]) -> str:
    """Format dictionary output for display."""
    return json.dumps(data, indent=2)


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text with ellipsis if too long."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """Check if file has an allowed extension."""
    return any(filename.lower().endswith(ext) for ext in allowed_extensions)


ALLOWED_EXTENSIONS = [".txt", ".pdf", ".csv", ".json", ".md"]


def is_allowed_file(filename: str) -> bool:
    """Check if file type is allowed for upload."""
    return validate_file_extension(filename, ALLOWED_EXTENSIONS)
