"""Utility functions for the translator."""


def validate_file_exists(file_path):
    """Validate that a file exists.

    Args:
        file_path: Path to file

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    import os

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")


def validate_file_extension(file_path, extension):
    """Validate file has correct extension.

    Args:
        file_path: Path to file
        extension: Expected extension (e.g., '.pptx')

    Raises:
        ValueError: If extension doesn't match
    """
    if not file_path.endswith(extension):
        raise ValueError(f"File must have {extension} extension: {file_path}")
