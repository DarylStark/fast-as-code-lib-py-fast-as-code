"""Custom resolvers."""

from pathlib import Path


class FileResolver:
    """Resolves "[file:my_file.txt]" to the contents of the file."""

    def __init__(self, root_path: Path, encoding: str = 'utf-8') -> None:
        """Set the root path."""
        self._root_path = root_path
        self._encoding = encoding

    def __call__(self, filename: str) -> str:
        """Load the file and return the contents."""
        file = self._root_path / filename
        return file.read_text(encoding=self._encoding)
